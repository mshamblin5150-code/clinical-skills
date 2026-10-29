"""Public-contract tests for the approved-run Stop hook. #1398."""

from __future__ import annotations

import artifact_lock_test_support
import contextlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import run_status_stop_hook as hook


@contextlib.contextmanager
def working_directory(path: Path):
    """Temporarily enter ``path`` on interpreters before ``contextlib.chdir``."""

    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def command_record(run: Path) -> dict[str, object]:
    return {
        "type": "event_msg",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "CommandExecution",
                "command": ["python", "tool.py", str(run)],
                "parsed_cmd": [{"type": "read", "path": str(run / "bar.md")}],
                "status": "completed",
            },
        },
    }


def claude_assistant_record(message: str) -> dict[str, object]:
    return {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": message}],
        },
    }


class RunStatusContract(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.run = self.root / "scratch" / "runs" / "nur-5042-module-5-course-assignment"
        self.run.mkdir(parents=True)
        self.artifact = self.root / "assignment.pptx"
        self.artifact.write_bytes(b"approved deck")
        (self.run / "submission-gates.json").write_text(
            json.dumps(
                {
                    "artifact": self.artifact.name,
                    "artifact_path": str(self.artifact),
                    "gate1_approved": True,
                    "approval_revision": 1,
                    "upload_route": "awaiting-upload",
                    "sha256": "a" * 64,
                    "attachment_count": 1,
                    "approved_carriers": [{"filename": self.artifact.name, "sha256": "a" * 64}],
                    "uploaded_files": [],
                }
            ),
            encoding="utf-8",
        )
        self.transcript = self.root / "session.jsonl"
        self.transcript.write_text(json.dumps(command_record(self.run)) + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def grade(self, message: str) -> dict[str, object]:
        return hook.handle(
            {
                "last_assistant_message": message,
                "transcript_path": str(self.transcript),
                "stop_hook_active": False,
            }
        )

    def test_missing_status_line_is_retracted(self) -> None:
        result = self.grade("The deck is ready for your upload.")

        self.assertEqual("block", result["decision"])
        self.assertIn("Run status:", result["reason"])

    def command_grade(self, raw: bytes) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(Path(hook.__file__).resolve())],
            input=raw,
            capture_output=True,
            env={**os.environ, "PYTHONUTF8": "0", "PYTHONIOENCODING": "cp1252"},
            timeout=10,
            check=False,
        )

    def test_command_decodes_raw_utf8_even_with_cp1252_stdin(self) -> None:
        # #1520: the shared command-path codec must preserve the required em dash.
        # Removing stdin from use_utf8's defaults makes the allowed case block.
        for separator, allowed in ((" — ", True), (" - ", False)):
            with self.subTest(separator=separator):
                line = f"Run status: {self.run.name}{separator}awaiting posting"
                payload = {
                    "transcript_path": str(self.transcript),
                    "last_assistant_message": f"Ready.\n\n{line}",
                    "stop_hook_active": False,
                }
                result = self.command_grade(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(b"", result.stderr)
                if allowed:
                    self.assertEqual(b"", result.stdout)
                else:
                    response = json.loads(result.stdout.decode("utf-8"))
                    self.assertEqual("block", response["decision"])
                    self.assertIn("malformed", response["reason"])
                    self.assertIn(line, response["reason"])

    def test_invalid_command_input_allows_with_an_ungraded_warning(self) -> None:
        for raw in (b"\xff", b"{", b"[]"):
            with self.subTest(raw=raw):
                result = self.command_grade(raw)
                self.assertEqual(0, result.returncode, result.stderr)
                response = json.loads(result.stdout.decode("utf-8"))
                self.assertTrue(response["continue"])
                self.assertIn("did not grade the turn", response["systemMessage"])
                self.assertNotIn("decision", response)
                self.assertEqual(b"", result.stderr)

    def test_malformed_line_identifies_the_failed_grammar_element(self) -> None:
        for line, element in (
            (f"Run status:{self.run.name} — awaiting posting", "prefix"),
            (f"Run status: {self.run.name} - awaiting posting", "separator"),
            ("Run status: invalid key — awaiting posting", "run key"),
            (f"Run status: {self.run.name} — ready", "status must be"),
            (f"Run status: {self.run.name} — stopped -", "reason after the hyphen"),
        ):
            with self.subTest(line=line):
                response = self.grade(line)
                self.assertEqual("block", response["decision"])
                self.assertIn(line, response["reason"])
                self.assertIn(element, response["reason"])

    def test_every_refusal_names_expected_keys_and_the_touch_rule(self) -> None:
        other = self.root / "scratch" / "runs" / "second-approved-run"
        other.mkdir(parents=True)
        (other / "submission-gates.json").write_bytes(
            (self.run / "submission-gates.json").read_bytes()
        )
        self.transcript.write_text(
            "\n".join(json.dumps(command_record(run)) for run in (self.run, other)),
            encoding="utf-8",
        )
        line = f"Run status: {self.run.name} — awaiting posting"
        other_line = f"Run status: {other.name} — awaiting posting"
        stopped = f"Run status: {self.run.name} — stopped -"
        malformed = f"Run status: {self.run.name} - awaiting posting"
        messages = (
            "Missing lines.",
            f"{line}\nRun status: wrong-key — awaiting posting",
            f"{line}\n{line}",
            f"{malformed}\n{other_line}",
            f"{stopped}\n{other_line}",
            f"{line}\nInterruption.\n{other_line}",
            f"{line}\n{other_line}\nTrailing prose.",
            f"Run status: {self.run.name} — complete\n{other_line}",
        )
        with mock.patch.object(hook, "completion_is_clean", return_value=False):
            for message in messages:
                with self.subTest(message=message):
                    response = self.grade(message)
                    self.assertEqual("block", response["decision"])
                    for run in (self.run, other):
                        self.assertIn(run.name, response["reason"])
                    self.assertIn("tool-call input names its directory", response["reason"])
        self.assertIn(malformed, self.grade(f"{malformed}\n{other_line}")["reason"])
        self.assertIn(stopped, self.grade(f"{stopped}\n{other_line}")["reason"])
        mixed = self.grade(f"{stopped}\n{malformed}")["reason"]
        self.assertIn(f"{stopped!r}: Run status: stopped needs", mixed)
        self.assertIn(f"{malformed!r}: The separator must", mixed)
        self.assertEqual({}, self.grade(
            f"Run status: {self.run.name} — stopped - waiting for correction\n{other_line}"
        ))
        response = self.grade(f"{line}\n{other_line}")
        self.assertEqual("block", response["decision"])
        self.assertIn("stays stopped", response["reason"])
        self.assertIn(other.name, response["reason"])
        self.assertIn("tool-call input names its directory", response["reason"])

    def write_session(self, *records: dict[str, object]) -> None:
        self.transcript.write_text(
            "\n".join(json.dumps(record) for record in records), encoding="utf-8"
        )

    def start_record(self) -> dict[str, object]:
        return {"type": "session_meta", "timestamp": "2026-01-01T00:00:00Z"}

    def make_run_old(self) -> None:
        for path in self.run.rglob("*"):
            if path.is_file():
                os.utime(path, (1, 1))

    def test_native_denied_subdirectory_requires_a_status_line(self):
        from tree_walk_test_support import denied_listing
        self.make_run_old()
        denied = self.run / "secret-identifier"
        denied.mkdir()
        self.write_session(self.start_record(), command_record(self.run))
        with denied_listing(denied):
            response = self.grade("Finished.")
        self.assertEqual("block", response["decision"])
        self.assertNotIn(denied.name, response["reason"])

    def check_links_do_not_touch_run(self, *, native):
        from tree_walk_test_support import junctions
        self.make_run_old()
        target = self.root / "linked-target"
        target.mkdir()
        (target / "changed.txt").touch()
        if native:
            junctions(self.run, target)
        else:
            try:
                (self.run / "link").symlink_to(target, target_is_directory=True)
            except OSError as failure:
                self.skipTest(str(failure))
        self.write_session(self.start_record(), command_record(self.run))
        self.assertEqual({}, self.grade("Read only."))

    def test_native_junctions_do_not_touch_run(self):
        self.check_links_do_not_touch_run(native=True)

    def test_symbolic_link_does_not_touch_run(self):
        self.check_links_do_not_touch_run(native=False)

    def test_unreadable_subdirectory_requires_a_status_line(self):
        self.make_run_old()
        denied = self.run / "private-folder"
        denied.mkdir()
        self.write_session(self.start_record(), command_record(self.run))
        scandir = os.scandir
        def read(path):
            if Path(path) == denied:
                raise PermissionError("private-folder")
            return scandir(path)
        with mock.patch("tree_walk.os.scandir", side_effect=read):
            response = self.grade("Finished.")
            self.assertEqual("block", response["decision"])
            self.assertEqual({}, self.grade(f"Run status: {self.run.name} \u2014 stopped - restore access"))
        self.assertNotIn(denied.name, response["reason"])

    def test_failed_file_stat_requires_a_status_line(self):
        self.make_run_old()
        self.write_session(self.start_record(), command_record(self.run))
        source = self.run / "working.md"
        source.touch()
        os.utime(source, (1, 1))
        self.assertEqual({}, self.grade("Finished."))
        original = Path.stat
        def read(path, *args, **kwargs):
            if path == source:
                raise PermissionError("private-file")
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, "stat", read):
            self.assertEqual("block", self.grade("Finished.")["decision"])
        def vanished(path, *args, **kwargs):
            if path == source:
                raise FileNotFoundError("vanished")
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, "stat", vanished):
            self.assertEqual("block", self.grade("Finished.")["decision"])

    def test_read_only_read_binds_nothing(self) -> None:
        self.make_run_old()
        record = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Read", "input": {"file_path": str(self.run / "submission-gates.json")}}
        ]}}
        self.write_session(self.start_record(), record)
        self.assertEqual({}, self.grade("Read for reference."))

    def test_output_prose_and_user_mentions_bind_nothing_even_after_a_write(self) -> None:
        for record in (
            {"type": "response_item", "payload": {"type": "function_call_output", "output": str(self.run)}},
            {"type": "user", "message": {"role": "user", "content": str(self.run)}},
            claude_assistant_record(str(self.run)),
            {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": str(self.run)}]}},
        ):
            with self.subTest(record=record):
                self.write_session(self.start_record(), record)
                self.assertEqual({}, self.grade("No work in this run."))

    def test_folder_listing_output_binds_nothing(self) -> None:
        record = command_record(self.run)
        record["payload"]["item"]["command"] = ["ls", str(self.run.parent)]
        record["payload"]["item"]["aggregated_output"] = str(self.run)
        self.write_session(self.start_record(), record)
        self.assertEqual({}, self.grade("Listed folders."))

    def test_command_named_run_with_nested_changed_file_binds(self) -> None:
        self.make_run_old()
        nested = self.run / "drafts"
        nested.mkdir()
        (nested / "reply.md").write_text("draft", encoding="utf-8")
        self.write_session(self.start_record(), command_record(self.run))
        self.assertEqual("block", self.grade("Drafted.")["decision"])

    def test_relative_script_path_does_not_absorb_the_run_path(self) -> None:
        relative = "scratch/runs/relative-run"
        run = self.root / relative
        run.mkdir(parents=True)
        (run / "reply.md").write_text("draft", encoding="utf-8")
        for executable in ("python", "C:/Python/python.exe", "/usr/bin/python"):
            for script in ("post_html.py", "course_assignment_scan.py"):
                for prefix in ("", "./"):
                    record = {"type": "response_item", "payload": {"type": "function_call", "arguments": json.dumps({"cmd": f"{executable} tools/{script} {prefix}{relative}"})}}
                    with self.subTest(executable=executable, script=script, prefix=prefix), working_directory(self.root):
                        self.assertEqual((run.resolve(),), hook.touched_runs((self.start_record(), record)))

    def test_space_in_structured_and_quoted_absolute_run_paths(self) -> None:
        run = self.root / "parent with spaces" / "scratch" / "runs" / "space-run"
        run.mkdir(parents=True)
        (run / "reply.md").write_text("draft", encoding="utf-8")
        for inputs in ({"file_path": str(run / "reply.md")}, {"cmd": f'python tool.py "{run}"'}):
            record = {"type": "response_item", "payload": {"type": "function_call", "arguments": json.dumps(inputs)}}
            with self.subTest(inputs=inputs):
                self.assertEqual((run.resolve(),), hook.touched_runs((self.start_record(), record)))

    def brief_record(self, prompt: str) -> dict[str, object]:
        return {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Agent", "input": {"prompt": prompt}}
        ]}}

    def test_a_brief_naming_a_checkout_and_a_run_binds_only_the_run(self) -> None:
        # #2042: the whole sentence was read as one path, which Windows refuses
        # as an invalid name, and every reply became unsatisfiable.
        checkout = self.root / "worktrees" / "w1"
        line = f"Run status: {self.run.name} — awaiting posting"
        for ending in (".", ""):
            prompt = f"Repo checkout: {checkout}. Run directory: {self.run}{ending}"
            with self.subTest(ending=ending):
                self.write_session(self.start_record(), self.brief_record(prompt))
                self.assertEqual((self.run.resolve(),), hook.touched_runs(hook._records(self.transcript)))
                self.assertEqual({}, self.grade(f"Briefed.\n\n{line}"))

    def test_trailing_punctuation_ends_the_run_name(self) -> None:
        for mention in (f"(see {self.run}),", f"Run directory: {self.run}:", f"{self.run};", f"[{self.run}]!"):
            with self.subTest(mention=mention):
                self.write_session(self.start_record(), self.brief_record(mention))
                self.assertEqual((self.run.resolve(),), hook.touched_runs(hook._records(self.transcript)))

    def test_a_name_outside_the_status_key_rule_is_not_recognized(self) -> None:
        # The key-grammar prefix exists too, so the name must not be misread as it.
        odd = self.run.parent / "odd+run"
        for folder in (odd, self.run.parent / "odd"):
            folder.mkdir()
            (folder / "reply.md").write_text("draft", encoding="utf-8")
        self.write_session(self.start_record(), self.brief_record(f"Run directory: {odd}"))
        self.assertEqual((), hook.touched_runs(hook._records(self.transcript)))

    def test_only_hook_state_changed_binds_nothing(self) -> None:
        self.make_run_old()
        (self.run / hook.STATE_RECORD).write_text("{}", encoding="utf-8")
        self.write_session(self.start_record(), command_record(self.run))
        self.assertEqual({}, self.grade("Only the hook wrote."))

    def test_codex_and_claude_tool_inputs_bind_changed_runs(self) -> None:
        records = (
            {"type": "response_item", "payload": {"type": "function_call", "arguments": json.dumps({"cmd": f'python tool.py "{self.run}"'})}},
            {"type": "response_item", "payload": {"type": "custom_tool_call", "input": f'edit "{self.run / "reply.md"}"'}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "input": {"file_path": str(self.run / "reply.md")}}]}},
        )
        for record in records:
            with self.subTest(record=record):
                self.write_session(self.start_record(), record)
                self.assertEqual((self.run.resolve(),), hook.touched_runs(hook._records(self.transcript)))

    def test_unreadable_start_falls_back_to_mentions(self) -> None:
        self.make_run_old()
        for timestamp in (None, "not a date", "2026-01-01T00:00:00"):
            with self.subTest(timestamp=timestamp):
                self.write_session({"timestamp": timestamp, "output": str(self.run)})
                self.assertEqual("block", self.grade("Mention fallback.")["decision"])

    def test_failing_retry_warns_in_both_payload_shapes_and_preserves_state(self) -> None:
        before = b'{"status":"stopped","approval_revision":"[]"}'
        state = self.run / hook.STATE_RECORD
        state.write_bytes(before)
        line = f"Run status: {self.run.name} — complete"
        for client in ("codex", "claude"):
            with self.subTest(client=client), mock.patch.object(hook, "completion_is_clean", return_value=False):
                self.write_session(command_record(self.run), claude_assistant_record(line))
                payload = {"transcript_path": str(self.transcript), "stop_hook_active": True}
                if client == "codex":
                    payload["last_assistant_message"] = line
                result = hook.handle(payload)
                self.assertEqual({"systemMessage"}, set(result))
                self.assertIn(line, result["systemMessage"])
                self.assertIn("terminal grade", result["systemMessage"])
                self.assertEqual(before, state.read_bytes())

    def test_retry_warns_for_each_failing_complete_and_writes_no_state(self) -> None:
        other = self.run.parent / "second-run"
        other.mkdir()
        (other / "submission-gates.json").write_bytes((self.run / "submission-gates.json").read_bytes())
        self.write_session(command_record(self.run), command_record(other))
        lines = [f"Run status: {run.name} — complete" for run in (self.run, other)]
        with mock.patch.object(hook, "completion_is_clean", return_value=False):
            response = hook.handle({"transcript_path": str(self.transcript), "stop_hook_active": True, "last_assistant_message": "\n".join(lines)})
        self.assertEqual({"systemMessage"}, set(response))
        for run, line in zip((self.run, other), lines):
            self.assertIn(f"{line!r}: complete requires", response["systemMessage"])
            self.assertFalse((run / hook.STATE_RECORD).exists())

    def test_passing_retry_is_recorded(self) -> None:
        for status in ("stopped - needs correction", "complete"):
            with self.subTest(status=status), mock.patch.object(hook, "completion_is_clean", return_value=True):
                response = hook.handle({"transcript_path": str(self.transcript), "stop_hook_active": True, "last_assistant_message": f"Run status: {self.run.name} — {status}"})
                self.assertEqual({}, response)
                state = json.loads((self.run / hook.STATE_RECORD).read_text(encoding="utf-8"))
                self.assertEqual(status.split(" - ")[0], state["status"])

    def test_retry_grammar_and_missing_lines_warn_without_blocking(self) -> None:
        for line in ("Missing.", f"Run status: {self.run.name} - complete", f"Run status: {self.run.name} — stopped -"):
            with self.subTest(line=line):
                response = hook.handle({"transcript_path": str(self.transcript), "stop_hook_active": True, "last_assistant_message": line})
                self.assertEqual({"systemMessage"}, set(response))
                self.assertFalse((self.run / hook.STATE_RECORD).exists())

    def test_retry_warning_is_emitted_as_utf8_json_for_both_clients(self) -> None:
        line = f"Run status: {self.run.name} - complete"
        self.write_session(command_record(self.run), claude_assistant_record(line))
        for client in ("codex", "claude"):
            with self.subTest(client=client):
                payload = {"transcript_path": str(self.transcript), "stop_hook_active": True}
                if client == "codex":
                    payload["last_assistant_message"] = line
                result = self.command_grade(json.dumps(payload).encode("utf-8"))
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(b"", result.stderr)
                response = json.loads(result.stdout.decode("utf-8"))
                self.assertEqual({"systemMessage"}, set(response))
                self.assertIn(line, response["systemMessage"])
                self.assertIn("separator", response["systemMessage"])
                self.assertFalse((self.run / hook.STATE_RECORD).exists())

    def test_retry_collects_completion_failure_beside_malformed_or_missing_lines(self) -> None:
        other = self.run.parent / "second-run"
        other.mkdir()
        (other / "submission-gates.json").write_bytes((self.run / "submission-gates.json").read_bytes())
        self.write_session(command_record(self.run), command_record(other))
        complete = f"Run status: {other.name} — complete"
        for first in (f"Run status: {self.run.name} - complete\n", ""):
            with self.subTest(first=first), mock.patch.object(hook, "completion_is_clean", return_value=False) as grade:
                response = hook.handle({"transcript_path": str(self.transcript), "stop_hook_active": True, "last_assistant_message": first + complete})
                self.assertEqual({"systemMessage"}, set(response))
                self.assertIn(f"{complete!r}: complete requires", response["systemMessage"])
                grade.assert_called_once()
                self.assertFalse((other / hook.STATE_RECORD).exists())

    def test_awaiting_posting_is_accepted_after_approval(self) -> None:
        self.assertEqual(
            {},
            self.grade(
                f"The deck is ready.\n\nRun status: {self.run.name} — awaiting posting"
            ),
        )

    def test_claude_reads_the_last_assistant_message_from_its_transcript(self) -> None:
        message = f"The deck is ready.\n\nRun status: {self.run.name} — awaiting posting"
        self.transcript.write_text(
            json.dumps(command_record(self.run))
            + "\n"
            + json.dumps(claude_assistant_record(message))
            + "\n",
            encoding="utf-8",
        )

        self.assertEqual(
            {},
            hook.handle(
                {
                    "transcript_path": str(self.transcript),
                    "stop_hook_active": False,
                }
            ),
        )

    def test_tool_input_after_final_text_is_not_part_of_the_reply(self) -> None:
        message = f"Ready.\n\nRun status: {self.run.name} — awaiting posting"
        record = claude_assistant_record(message)
        record["message"]["content"].append(
            {"type": "tool_use", "id": "synthetic-read", "name": "Read",
             "input": {"file_path": str(self.run / "bar.md")}}
        )
        self.transcript.write_text(
            "\n".join(json.dumps(row) for row in (command_record(self.run), record)) + "\n",
            encoding="utf-8",
        )

        self.assertEqual({}, hook.handle({"transcript_path": str(self.transcript)}))

    def test_tool_input_cannot_supply_a_missing_or_wrong_reply_status(self) -> None:
        correct = f"Run status: {self.run.name} — awaiting posting"
        for reply in ("Ready.", "Run status: another-run — awaiting posting"):
            with self.subTest(reply=reply):
                record = claude_assistant_record(reply)
                record["message"]["content"].append(
                    {"type": "tool_use", "name": "Write", "input": {"content": correct}}
                )
                self.transcript.write_text(
                    "\n".join(json.dumps(row) for row in (command_record(self.run), record)) + "\n",
                    encoding="utf-8",
                )
                result = hook.handle({"transcript_path": str(self.transcript)})
                self.assertEqual("block", result["decision"])

    def test_tool_only_message_does_not_replace_the_final_reply(self) -> None:
        message = f"Ready.\n\nRun status: {self.run.name} — awaiting posting"
        tool_only = {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Read", "input": {"file_path": str(self.run / "bar.md")}}
        ]}}
        self.transcript.write_text(
            "\n".join(json.dumps(row) for row in (
                command_record(self.run), claude_assistant_record(message), tool_only,
            )) + "\n", encoding="utf-8",
        )

        result = self.command_grade(json.dumps({"transcript_path": str(self.transcript)}).encode("utf-8"))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(b"", result.stdout)

    def test_final_visible_text_wins_over_earlier_reply_and_text_metadata(self) -> None:
        correct = f"Run status: {self.run.name} — awaiting posting"
        content = [{"type": "output_text", "text": correct, "annotations": [{"type": "synthetic-metadata"}]}]
        for final in (
            {"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": content}},
            {"type": "event_msg", "payload": {"item": {"type": "AgentMessage", "content": content}}},
            {"type": "assistant", "message": {"role": "assistant", "content": correct}},
        ):
            with self.subTest(final=final):
                self.transcript.write_text(
                    "\n".join(json.dumps(row) for row in (
                        command_record(self.run), claude_assistant_record("Working."), final,
                    )) + "\n", encoding="utf-8",
                )
                self.assertEqual({}, hook.handle({"transcript_path": str(self.transcript)}))

        self.transcript.write_text(
            "\n".join(json.dumps(row) for row in (
                command_record(self.run), claude_assistant_record(correct), claude_assistant_record("No status here."),
            )) + "\n", encoding="utf-8",
        )
        self.assertEqual("block", hook.handle({"transcript_path": str(self.transcript)})["decision"])

    def test_repeated_tool_mentions_and_command_punctuation_need_one_status(self) -> None:
        line = f"Run status: {self.run.name} — awaiting posting"
        records = [command_record(self.run), command_record(self.run)]
        for command in (f"python tool.py {self.run};", f'python tool.py "{self.run}"'):
            records.append({"type": "response_item", "payload": {
                "type": "function_call", "arguments": json.dumps({"cmd": command}),
            }})
        records.append(claude_assistant_record(line))
        self.transcript.write_text(
            "\n".join(json.dumps(row) for row in records) + "\n", encoding="utf-8",
        )

        self.assertEqual({}, hook.handle({"transcript_path": str(self.transcript)}))

    def test_string_content_parts_still_require_a_keyed_status(self) -> None:
        for parts, allowed in (
            (["Ready.", f"Run status: {self.run.name} — awaiting posting"], True),
            (["Ready.", "No status here."], False),
        ):
            with self.subTest(parts=parts):
                record = {"type": "assistant", "message": {"role": "assistant", "content": parts}}
                self.transcript.write_text(
                    "\n".join(json.dumps(row) for row in (command_record(self.run), record)) + "\n",
                    encoding="utf-8",
                )
                result = hook.handle({"transcript_path": str(self.transcript)})
                if allowed:
                    self.assertEqual({}, result)
                else:
                    self.assertEqual("block", result.get("decision"))

    def test_early_complete_is_retracted(self) -> None:
        with mock.patch.object(hook, "completion_is_clean", return_value=False):
            result = self.grade(
                f"Submitted.\n\nRun status: {self.run.name} — complete"
            )

        self.assertEqual("block", result["decision"])
        self.assertIn("terminal grade", result["reason"])

    def test_clean_completion_closes_the_run_for_later_replies(self) -> None:
        with mock.patch.object(hook, "completion_is_clean", return_value=True):
            self.assertEqual(
                {}, self.grade(f"Done.\n\nRun status: {self.run.name} — complete")
            )

        self.assertEqual({}, self.grade("A later reply about another subject."))

    def test_reasonless_stopped_is_retracted(self) -> None:
        result = self.grade(
            f"I stopped here.\n\nRun status: {self.run.name} — stopped -"
        )

        self.assertEqual("block", result["decision"])
        self.assertIn("reason", result["reason"])

    def test_a_stopped_run_stays_stopped_until_another_approval(self) -> None:
        self.assertEqual(
            {},
            self.grade(
                f"The posted file differs.\n\nRun status: {self.run.name} — stopped - posted file differs"
            ),
        )

        result = self.grade(
            f"I am checking it.\n\nRun status: {self.run.name} — awaiting posted reading"
        )
        self.assertEqual("block", result["decision"])
        self.assertIn("stays stopped", result["reason"])

        record = json.loads((self.run / "submission-gates.json").read_text(encoding="utf-8"))
        record["approval_revision"] = 2
        (self.run / "submission-gates.json").write_text(json.dumps(record), encoding="utf-8")
        self.assertEqual(
            {},
            self.grade(
                f"The revision is approved.\n\nRun status: {self.run.name} — awaiting posting"
            ),
        )

    def test_the_claude_stop_registration_uses_the_same_hook(self) -> None:
        settings = json.loads(
            (Path(__file__).resolve().parents[1] / ".claude" / "settings.json").read_text(
                encoding="utf-8"
            )
        )
        commands = [
            handler["command"]
            for registration in settings["hooks"]["Stop"]
            for handler in registration["hooks"]
        ]

        self.assertTrue(any("run_status_stop_hook.py" in command for command in commands))

    def test_a_new_skill_row_is_discoverable_from_the_approval_record(self) -> None:
        other = self.root / "scratch" / "runs" / "course-module-other-submission"
        other.mkdir(parents=True)
        record = other / "approval.json"
        item = {
            "skill": "other-submission",
            "submission": "one",
            "sha256": "0" * 64,
            "sources": [str(self.artifact)],
            "grader_args": [str(other)],
            "posting_route": "awaiting-posting",
            "approval_revision": 1,
            "pregrade_status": "clean",
        }
        record.write_text(
            json.dumps({"version": 1, "approval_revision": 1, "items": [item]}),
            encoding="utf-8",
        )
        spec = hook.RunKind(
            skill="other-submission",
            approval_record=record.name,
            completion_command="other_scan.py",
        )

        with mock.patch.object(hook, "RUN_KIND_BY_SKILL", {spec.skill: spec}):
            self.assertEqual(
                ((spec, item),),
                hook.approvals(other.resolve()),
            )

    def test_a_malformed_posting_item_opens_no_run(self) -> None:
        run = self.root / "scratch" / "runs" / "malformed-discussion"
        run.mkdir(parents=True)
        (run / "posting-approvals.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "approval_revision": 1,
                    "items": [
                        {
                            "skill": "discussion-post",
                            "submission": "post",
                            "grader_args": [str(run)],
                            "approval_revision": 1,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.transcript.write_text(
            json.dumps(command_record(run)) + "\n", encoding="utf-8"
        )

        self.assertEqual("block", self.grade("The record is incomplete.").get("decision"))
        self.assertEqual({}, self.grade(f"Run status: {run.name} — stopped - approval record unreadable"))

    def test_each_posting_skill_opens_from_its_record_and_retracts_early_complete(self) -> None:
        for skill in (
            "discussion-post",
            "discussion-reply",
            "peer-critique",
            "practicum-case-study",
            "clinical-note",
            "batch-shift",
        ):
            with self.subTest(skill=skill):
                run = self.root / "scratch" / "runs" / f"key-{skill}"
                run.mkdir(parents=True)
                artifact = run / "approved.md"
                artifact.write_text("approved\n", encoding="utf-8")
                (run / "posting-approvals.json").write_text(
                    json.dumps(
                        {
                            "version": 1,
                            "approval_revision": 1,
                            "items": [
                                {
                                    "skill": skill,
                                    "submission": "submission-key",
                                    "sha256": "0" * 64,
                                    "sources": [str(artifact)],
                                    "grader_args": [str(run)],
                                    "posting_route": "awaiting-posting",
                                    "approval_revision": 1,
                                    "pregrade_status": "clean",
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                self.transcript.write_text(
                    json.dumps(command_record(run)) + "\n", encoding="utf-8"
                )
                with mock.patch.object(hook, "completion_is_clean", return_value=False):
                    result = self.grade(
                        f"Done.\n\nRun status: {run.name} — complete"
                    )
                self.assertEqual("block", result["decision"])
                self.assertIn("terminal grade", result["reason"])

    def test_two_touched_approved_runs_each_need_their_own_keyed_line(self) -> None:
        other = self.root / "scratch" / "runs" / "nur-5042-module-6-course-assignment"
        other.mkdir(parents=True)
        other_artifact = self.root / "assignment-2.pptx"
        other_artifact.write_bytes(b"approved deck two")
        (other / "submission-gates.json").write_text(
            json.dumps(
                {
                    "artifact": other_artifact.name,
                    "artifact_path": str(other_artifact),
                    "gate1_approved": True,
                    "sha256": "a" * 64,
                    "attachment_count": 1,
                    "approved_carriers": [{"filename": other_artifact.name, "sha256": "a" * 64}],
                    "uploaded_files": [],
                    "approval_revision": 1,
                    "upload_route": "awaiting-upload",
                }
            ),
            encoding="utf-8",
        )
        self.transcript.write_text(
            json.dumps(command_record(self.run))
            + "\n"
            + json.dumps(command_record(other))
            + "\n",
            encoding="utf-8",
        )

        result = self.grade(
            f"Both are ready.\n\nRun status: {other.name} — awaiting posting"
        )
        self.assertEqual("block", result["decision"])

        self.assertEqual(
            {},
            self.grade(
                "Both are ready.\n\n"
                f"Run status: {self.run.name} — awaiting posting\n"
                f"Run status: {other.name} — awaiting posting"
            ),
        )

    def test_distinct_runs_with_the_same_key_refuse_before_completion_grading(self) -> None:
        other = self.root / "other-checkout" / "scratch" / "runs" / self.run.name
        other.mkdir(parents=True)
        other_artifact = other / "other-assignment.pptx"
        other_artifact.write_bytes(b"another synthetic approved deck")
        approval = json.loads((self.run / "submission-gates.json").read_text(encoding="utf-8"))
        approval.update(artifact=other_artifact.name, artifact_path=str(other_artifact))
        (other / "submission-gates.json").write_text(json.dumps(approval), encoding="utf-8")
        self.write_session(command_record(self.run), command_record(other))
        complete = f"Run status: {self.run.name} — complete"
        waiting = f"Run status: {self.run.name} — awaiting posting"
        for message, retry in ((complete, False), (complete + "\n" + complete, False),
                               (waiting, False), (complete, True)):
            with self.subTest(message=message, retry=retry):
                with mock.patch.object(hook, "completion_is_clean", return_value=False) as grade:
                    result = hook.handle({"transcript_path": str(self.transcript),
                                          "last_assistant_message": message,
                                          "stop_hook_active": retry})
                self.assertEqual({"systemMessage"} if retry else {"decision", "reason"}, set(result))
                if not retry:
                    self.assertEqual("block", result["decision"])
                reason = result["systemMessage"] if retry else result["reason"]
                self.assertIn("share a run key", reason)
                self.assertNotIn(str(self.root), reason)
                grade.assert_not_called()
                self.assertFalse((self.run / hook.STATE_RECORD).exists())
                self.assertFalse((other / hook.STATE_RECORD).exists())

    def test_two_reply_run_stays_open_while_one_approved_reply_is_unposted(self) -> None:
        run = self.root / "scratch" / "runs" / "nur-5042-module-7-discussion"
        run.mkdir(parents=True)
        (run / "posting-approvals.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "approval_revision": 2,
                    "items": [
                        {
                            "skill": "discussion-reply",
                            "submission": f"response-{number}.md",
                            "sha256": "0" * 64,
                            "sources": [str(run / f"response-{number}.md")],
                            "grader_args": [str(run)],
                            "posting_route": "awaiting-posting",
                            "approval_revision": number,
                            "pregrade_status": "clean",
                        }
                        for number in (1, 2)
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.transcript.write_text(
            json.dumps(command_record(run)) + "\n", encoding="utf-8"
        )

        with mock.patch.object(
            hook, "completion_is_clean", side_effect=(True, False)
        ):
            result = self.grade(f"Done.\n\nRun status: {run.name} — complete")

        self.assertEqual("block", result["decision"])
        self.assertIn("every approved item", result["reason"])

    def test_a_code_lookup_with_no_approval_record_opens_nothing(self) -> None:
        lookup = self.root / "scratch" / "runs" / "code-lookup"
        lookup.mkdir(parents=True)
        self.transcript.write_text(
            json.dumps(command_record(lookup)) + "\n", encoding="utf-8"
        )

        self.assertEqual({}, self.grade("The requested code was located."))


if __name__ == "__main__":
    unittest.main()
