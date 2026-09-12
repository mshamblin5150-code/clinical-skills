"""Contract tests for the submission-keyed after-action review. #814."""

from __future__ import annotations

import io
import importlib
import ast
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import artifact_lock_test_support  # noqa: F401

import aar_scan
import checks_ledger
import differential_scan
import discussion_post_scan
import discussion_reply_scan
import filled_vitals_census
import grader_conformance
import specificity_scan


GraderConformance = grader_conformance.for_module(aar_scan)


def empty_population_input(root: Path) -> grader_conformance.EmptyPopulationInput:
    run = root / "run"
    run.mkdir()
    return grader_conformance.EmptyPopulationInput(
        (str(run), "--submission", "synthetic-submission"),
        population_size=lambda result: result.population,
    )


class DeclaredLimitsAreBound(unittest.TestCase):
    def test_the_test_suite_names_the_declared_limits_object(self):
        self.assertTrue(aar_scan.DECLARED_LIMITS)
        self.assertEqual(
            tuple(reason for _subject, reason in aar_scan.DECLARED_LIMITS),
            aar_scan.NOT_REACHED,
        )


def row(kind: str, uuid: str, message: object, **extra: object) -> dict[str, object]:
    return {
        "type": kind,
        "uuid": uuid,
        "sessionId": "session-1",
        "message": message,
        **extra,
    }


def write_transcript(path: Path, run: Path | None = None) -> None:
    command = "echo ready" if run is None else f'python tools/discussion_post_scan.py "{run}"'
    rows = [
        row(
            "user",
            "u1",
            {"content": "That is the wrong section; use the nurse practitioner section."},
            attributionSkill="discussion-post",
        ),
        row(
            "assistant",
            "a1",
            {
                "content": [
                    {"type": "text", "text": "You are right. I corrected the citation."},
                    {
                        "type": "tool_use",
                        "id": "tool-1",
                        "name": "Bash",
                        "input": {"command": command},
                    },
                ]
            },
            attributionSkill="discussion-post",
        ),
        row(
            "user",
            "u2",
            {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool-1",
                        "content": "patient-bearing output that must be dropped",
                        "is_error": False,
                    }
                ]
            },
            attributionSkill="discussion-post",
        ),
    ]
    path.write_text("\n".join(json.dumps(item) for item in rows) + "\n", encoding="utf-8")


def codex_row(payload: object, **extra: object) -> dict[str, object]:
    return {"type": "response_item", "payload": payload, **extra}


def write_codex_transcript(path: Path, run: Path | None = None) -> None:
    command = "echo ready" if run is None else f'python tools/discussion_post_scan.py "{run}"'
    rows = [
        codex_row(
            {
                "type": "message",
                "id": "u1",
                "role": "user",
                "content": [{"type": "input_text", "text": "That is the wrong section."}],
            }
        ),
        codex_row(
            {
                "type": "message",
                "id": "a1",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "I corrected the citation."}],
            }
        ),
        codex_row(
            {
                "type": "custom_tool_call",
                "id": "call-item-1",
                "call_id": "call-1",
                "name": "exec",
                "input": json.dumps({"cmd": command}),
                "status": "completed",
            }
        ),
        codex_row(
            {
                "type": "custom_tool_call_output",
                "id": "output-1",
                "call_id": "call-1",
                "output": [{"type": "input_text", "text": "patient-bearing output"}],
            }
        ),
        codex_row(
            {
                "type": "agent_message",
                "id": "agent-1",
                "author": "/root/checker",
                "recipient": "/root",
                "content": [{"type": "input_text", "text": "The checker found one mismatch."}],
            }
        ),
        codex_row(
            {
                "type": "message",
                "id": "developer-1",
                "role": "developer",
                "content": [{"type": "input_text", "text": "private developer instruction"}],
            }
        ),
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {"type": "UserMessage", "id": "u1", "content": [{"type": "text", "text": "That is the wrong section."}]},
            },
        },
    ]
    path.write_text("\n".join(json.dumps(item) for item in rows) + "\n", encoding="utf-8")


class GithubPublicationEvidence(unittest.TestCase):
    def test_a_successful_codex_command_execution_proves_the_gh_call(self):
        with tempfile.TemporaryDirectory() as temp:
            transcript = Path(temp) / "codex.jsonl"
            event = {
                "type": "event_msg",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "CommandExecution",
                        "command": ["pwsh", "-Command", "gh issue create --title follow-up"],
                        "status": "completed",
                        "exit_code": 0,
                    },
                },
            }
            transcript.write_text(json.dumps(event) + "\n", encoding="utf-8")

            self.assertTrue(aar_scan._successful_gh_call((transcript,)))


def invoke_main(arguments: list[str], stdin: str | None = None) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    original_stdin = aar_scan.sys.stdin
    if stdin is not None:
        aar_scan.sys.stdin = io.StringIO(stdin)
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = aar_scan.main(arguments)
    finally:
        aar_scan.sys.stdin = original_stdin
    return status, stdout.getvalue(), stderr.getvalue()


class CommandModes(unittest.TestCase):
    """The three command modes whose routing #840 migrated."""

    def test_the_graded_mode_prints_the_report_and_returns_its_finding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()

            status, stdout, stderr = invoke_main(
                [str(run), "--submission", "post-1"]
            )

        self.assertEqual(status, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(
            stdout,
            "after-action review over run\n\n"
            "  review records                  0\n"
            "  candidate population            0\n"
            "  correction records              0\n"
            "  sustain records                 0\n"
            "  unread candidates               0\n"
            "  orphaned sittings               0\n"
            "  findings                        1\n\n"
            "  declared limits:\n"
            "    semantic classification\n"
            "    tool-result-only correction\n"
            "    uncorrected error\n"
            "    orchestrator veto\n"
            "    subagent silence\n"
            "    transcript flush\n"
            "    run-key discovery\n"
            "    subagent launch-result drift\n",
        )

    def test_the_extract_mode_writes_and_reports_its_private_packet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            run.mkdir()
            transcript = root / "session-1.jsonl"
            write_transcript(transcript)
            memory = root / "memory" / "MEMORY.md"
            memory.parent.mkdir()
            memory.write_text("# Index\n", encoding="utf-8")

            status, stdout, stderr = invoke_main(
                [
                    str(run),
                    "--submission", "post-1",
                    "--transcript", str(transcript),
                    "--memory-index", str(memory),
                    "--extract",
                ]
            )

            self.assertTrue(aar_scan.extract_path(run, "post-1").is_file())
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(
            stdout,
            "after-action review extract over run\n"
            "  candidate population            4\n"
            "  private extract written         post-1.extract.md\n",
        )

    def test_the_session_end_mode_keeps_its_silent_exit_two(self) -> None:
        self.assertEqual(invoke_main(["--session-end"], stdin="{}"), (2, "", ""))

    def test_a_refused_review_open_is_a_finding_without_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "alias-parent").mkdir()
            # Drive an unresolved spelling on every platform. Windows CI's
            # short temporary-directory alias exposed this same mismatch.
            run = root / "alias-parent" / ".." / "run"
            (run / "aar").mkdir(parents=True)
            review = aar_scan.review_path(run, "post-1")
            review.write_text("# AFTER-ACTION REVIEW\n", encoding="utf-8")
            original = Path.read_text

            def refusing(path: Path, *args: object, **kwargs: object) -> str:
                if path.resolve() == review.resolve():
                    raise PermissionError(13, "denied", str(review))
                return original(path, *args, **kwargs)

            with mock.patch.object(Path, "read_text", refusing):
                status, stdout, stderr = invoke_main(
                    [str(run), "--submission", "post-1", "--show"]
                )

        self.assertEqual((status, stderr), (1, ""))
        self.assertIn("unscannable-review: cannot read review", stdout)

    def test_the_runner_refuses_unknown_flags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            status, _stdout, stderr = invoke_main(
                [str(run), "--submission", "post-1", "--unknown"]
            )
        self.assertEqual(status, 2)
        self.assertEqual(stderr, "unrecognized option --unknown\n")

    def test_the_runner_accepts_a_flag_first_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            status, stdout, stderr = invoke_main(
                ["--show", str(run), "--submission", "post-1"]
            )
        self.assertEqual((status, stderr), (1, ""))
        self.assertIn("after-action review over run", stdout)

    def test_the_runner_refuses_show_as_a_submission_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            status, stdout, stderr = invoke_main(
                [str(run), "--submission", "--show"]
            )
        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "--submission needs a key\n")


class ReductionByEntryShape(unittest.TestCase):
    def test_claude_user_rows_are_labeled_by_harness_envelope_and_flags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            rows = [
                row("user", "typed", {"content": "Please keep the assessment concise."}),
                row(
                    "user",
                    "notification",
                    {"content": "[SYSTEM NOTIFICATION — NOT USER INPUT]\n<task-notification>done</task-notification>"},
                ),
                row(
                    "user",
                    "skill",
                    {"content": "Base directory for this skill: C:\\skills\\aar\nInstructions"},
                    isMeta=True,
                ),
                row("user", "meta", {"content": "Harness resumed the task."}, isMeta=True),
                row(
                    "user",
                    "compact",
                    {"content": "Summary of the earlier context."},
                    isCompactSummary=True,
                ),
            ]
            transcript.write_text(
                "\n".join(json.dumps(item) for item in rows) + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [candidate.kind for candidate in candidates],
            [
                "clinician",
                "task-notification",
                "skill-prompt",
                "harness-meta",
                "compaction-summary",
            ],
        )
    def test_subagent_launch_acknowledgment_is_not_labeled_as_a_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            rows = [
                row(
                    "assistant",
                    "a1",
                    {
                        "content": [
                            {"type": "tool_use", "id": "agent-call", "name": "Agent", "input": {}}
                        ]
                    },
                ),
                row(
                    "user",
                    "launch",
                    {
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "agent-call",
                                "content": "Async agent launched successfully.\nagentId: agent-7",
                            }
                        ]
                    },
                ),
            ]
            transcript.write_text(
                "\n".join(json.dumps(item) for item in rows) + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [candidate.kind for candidate in candidates],
            ["tool-call", "subagent-launch", "tool-status"],
        )

    def test_attachment_task_notification_is_a_first_class_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            transcript.write_text(
                json.dumps(
                    {
                        "type": "attachment",
                        "uuid": "attachment-row",
                        "attachment": {
                            "type": "queued_command",
                            "commandMode": "task-notification",
                            "prompt": (
                                "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
                                "<task-notification><task-id>reader-9</task-id>"
                                "<result>Finished.</result></task-notification>"
                            ),
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [(candidate.identifier, candidate.kind) for candidate in candidates],
            [("reader-9", "task-notification")],
        )

    def test_assistant_and_queue_notification_envelopes_are_first_class_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            banner = (
                "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
                "<task-notification><task-id>reader-10</task-id>"
                "<result>Finished.</result></task-notification>"
            )
            transcript.write_text(
                "\n".join(
                    json.dumps(item)
                    for item in (
                        row(
                            "assistant",
                            "assistant-row",
                            {"content": [{"type": "text", "text": banner}]},
                        ),
                        {
                            "type": "queue-operation",
                            "uuid": "queue-row",
                            "operation": "enqueue",
                            "content": banner.replace("reader-10", "reader-11"),
                        },
                        {
                            "type": "queue-operation",
                            "uuid": "unknown-queue-row",
                            "operation": "enqueue",
                            "content": "<future-harness-event>Queued.</future-harness-event>",
                        },
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [(candidate.identifier, candidate.kind) for candidate in candidates],
            [
                ("reader-10", "task-notification"),
                ("reader-11", "task-notification"),
                ("unknown-queue-row", "harness-meta"),
            ],
        )

    def test_keeps_conversation_and_status_but_drops_ordinary_result_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            write_transcript(transcript)

            candidates = aar_scan.reduce_transcript(transcript)
            joined = "\n".join(row.text for row in candidates)

            self.assertIn("wrong section", joined)
            self.assertIn("I corrected", joined)
            self.assertIn("Bash", joined)
            self.assertIn("completed", joined)
            self.assertNotIn("patient-bearing", joined)

    def test_keeps_a_short_human_correction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "short.jsonl"
            transcript.write_text(
                json.dumps(row("user", "u1", {"content": "agree"})) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(aar_scan.reduce_transcript(transcript)[0].text, "agree")

    def test_codex_keeps_conversation_tools_and_agent_results_without_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "rollout.jsonl"
            write_codex_transcript(transcript)

            candidates = aar_scan.reduce_transcript(transcript)
            joined = "\n".join(candidate.text for candidate in candidates)

            self.assertEqual(
                [candidate.kind for candidate in candidates],
                ["clinician", "assistant", "tool-call", "tool-status", "subagent-result"],
            )
            self.assertEqual(joined.count("That is the wrong section."), 1)
            self.assertIn("exec: completed", joined)
            self.assertIn("The checker found one mismatch.", joined)
            self.assertNotIn("patient-bearing output", joined)
            self.assertNotIn("private developer instruction", joined)

    def test_codex_labels_harness_envelopes_compaction_and_delegation_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "rollout.jsonl"
            rows = [
                codex_row(
                    {
                        "type": "message",
                        "id": "context-1",
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "<environment_context>private context</environment_context>"}
                        ],
                    }
                ),
                {
                    "type": "compacted",
                    "payload": {
                        "message": "Summary of the earlier context.",
                        "replacement_history": [],
                    },
                },
                {
                    "type": "inter_agent_communication_metadata",
                    "payload": {"trigger_turn": True},
                },
            ]
            transcript.write_text(
                "\n".join(json.dumps(item) for item in rows) + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [candidate.kind for candidate in candidates],
            ["environment-context", "compaction-summary", "inter-agent-metadata"],
        )
        self.assertEqual(candidates[1].text, "Summary of the earlier context.")

    def test_codex_function_call_keeps_its_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "rollout.jsonl"
            transcript.write_text(
                json.dumps(
                    codex_row(
                        {
                            "type": "function_call",
                            "id": "call-item-1",
                            "call_id": "call-1",
                            "namespace": "mcp__cua_repl",
                            "name": "js",
                            "arguments": "{}",
                        }
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            candidate = aar_scan.reduce_transcript(transcript)[0]

            self.assertEqual(candidate.text, "mcp__cua_repl.js")

    def test_codex_tool_input_discovers_the_run_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory) / "scratch"
            run = scratch / "runs" / "case-study"
            run.mkdir(parents=True)
            transcript = Path(directory) / "rollout.jsonl"
            write_codex_transcript(transcript, run)
            with mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=scratch):
                found = aar_scan.discover_run_directories(aar_scan.read_transcript(transcript))

            self.assertEqual(found, (run.resolve(),))


class EntryKindsAreBound(unittest.TestCase):
    def test_every_candidate_kind_is_literal_or_passes_the_declared_kind_guard(self) -> None:
        tree = ast.parse(Path(aar_scan.__file__).read_text(encoding="utf-8"))
        checked = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "Candidate" or len(node.args) < 3:
                continue
            checked += 1
            kind = node.args[2]
            if isinstance(kind, ast.Constant) and isinstance(kind.value, str):
                self.assertIn(kind.value, aar_scan.ENTRY_KINDS)
                continue
            self.assertIsInstance(kind, ast.Call)
            self.assertIsInstance(kind.func, ast.Name)
            self.assertEqual(kind.func.id, "_declared_entry_kind")
        self.assertGreater(checked, 0)

    def test_the_envelope_table_and_envelope_kind_vocabulary_match_both_ways(self) -> None:
        self.assertEqual(
            set(aar_scan.ENVELOPE_KINDS.values()),
            set(aar_scan.ENVELOPE_ENTRY_KINDS),
        )
        self.assertLessEqual(
            set(aar_scan.ENVELOPE_ENTRY_KINDS),
            set(aar_scan.ENTRY_KINDS),
        )
        self.assertEqual(
            {
                aar_scan._envelope_kind(f"prefix <{tag}>body</{tag}>")
                for tag in aar_scan.ENVELOPE_KINDS
            },
            set(aar_scan.ENVELOPE_ENTRY_KINDS),
        )

    def test_the_measured_codex_row_type_vocabulary_is_declared(self) -> None:
        self.assertEqual(
            aar_scan.CODEX_ROW_TYPES,
            {
                "compacted",
                "event_msg",
                "inter_agent_communication_metadata",
                "response_item",
                "session_meta",
                "token_usage_record",
                "turn_context",
                "world_state",
            },
        )


class SubmissionRecord(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run = self.root / "course-module-discussion"
        self.run.mkdir()
        self.transcript = self.root / "session-1.jsonl"
        write_transcript(self.transcript)
        self.memory = self.root / "memory" / "MEMORY.md"
        self.memory.parent.mkdir()
        self.memory.write_text("# Index\n", encoding="utf-8")
        self.submission = "post-2026-09-02"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def extract(self) -> tuple[dict[str, str], set[str]]:
        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        return aar_scan._extract_metadata(aar_scan.extract_path(self.run, self.submission))

    def test_version_two_extract_frames_a_body_that_quotes_an_entry_heading(self) -> None:
        self.transcript.write_text(
            json.dumps(
                row(
                    "user",
                    "u-collision",
                    {"content": "Classifier discussion:\n## ENTRY: not-an-entry\nStill one body."},
                )
            )
            + "\n",
            encoding="utf-8",
        )

        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        path = aar_scan.extract_path(self.run, self.submission)
        text = path.read_text(encoding="utf-8")
        fields, identifiers = aar_scan._extract_metadata(path)

        self.assertEqual(fields["FORMAT"], "2")
        self.assertEqual(
            fields["ENTRY-KINDS"],
            " | ".join(
                f"{kind} = {description}"
                for kind, description in aar_scan.ENTRY_KIND_DESCRIPTIONS.items()
            ),
        )
        self.assertIn("TEXT-LINES: 3", text)
        self.assertEqual(identifiers, {"u-collision"})

    def test_extract_header_reports_matcher_remainders_and_launch_accounting(self) -> None:
        rows = [
            row(
                "assistant",
                "a1",
                {"content": [{"type": "tool_use", "id": "agent-call", "name": "Agent", "input": {}}]},
                version="2.1.266",
            ),
            row(
                "user",
                "launch",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "agent-call",
                            "content": "Async agent launched successfully.\nagentId: reader-7",
                        }
                    ]
                },
                version="2.1.266",
            ),
            {
                "type": "attachment",
                "uuid": "notification",
                "attachment": {
                    "type": "queued_command",
                    "commandMode": "task-notification",
                    "prompt": (
                        "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
                        "<task-notification><task-id>reader-7</task-id>"
                        "<result>Finished.</result></task-notification>"
                    ),
                },
                "version": "2.1.266",
            },
            row("user", "new-wrapper", {"content": "<future-wrapper>Injected.</future-wrapper>"}),
            row(
                "assistant",
                "assistant-wrapper",
                {
                    "content": [
                        {"type": "text", "text": "<future-assistant>Injected.</future-assistant>"}
                    ]
                },
            ),
            {"type": "future_row", "payload": {}},
            {"type": "response_item", "payload": {"type": "future_item"}},
        ]
        self.transcript.write_text(
            "\n".join(json.dumps(item) for item in rows) + "\n",
            encoding="utf-8",
        )

        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        fields, _identifiers = aar_scan._extract_metadata(
            aar_scan.extract_path(self.run, self.submission)
        )

        self.assertEqual(fields["HARNESS-VERSIONS"], "2.1.266")
        self.assertEqual(fields["UNDECLARED-ENVELOPES"], "2")
        self.assertEqual(fields["UNDECLARED-CODEX-ROW-TYPES"], "1")
        self.assertEqual(fields["UNDECLARED-CODEX-PAYLOAD-TYPES"], "1")
        self.assertEqual(fields["SUBAGENT-LAUNCHES"], "1")
        self.assertEqual(fields["SUBAGENT-JOINED-RESULTS"], "1")
        self.assertEqual(fields["SUBAGENT-UNJOINED"], "0")
        self.assertEqual(fields["NOTIFICATIONS-WITHOUT-JOIN-KEY"], "0")

    def test_an_unknown_extract_format_is_not_scanned(self) -> None:
        self.write_clean()
        path = aar_scan.extract_path(self.run, self.submission)
        path.write_text(
            path.read_text(encoding="utf-8").replace("FORMAT: 2", "FORMAT: 99", 1),
            encoding="utf-8",
        )

        status, stdout, stderr = invoke_main(
            [str(self.run), "--submission", self.submission]
        )

        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertIn("unknown extract format 99", stderr)

    def test_a_malformed_known_extract_is_an_extract_finding(self) -> None:
        self.write_clean()
        path = aar_scan.extract_path(self.run, self.submission)
        path.write_text(
            path.read_text(encoding="utf-8").replace("TEXT-LINES: 1", "TEXT-LINES: many", 1),
            encoding="utf-8",
        )

        scan = aar_scan.survey(self.run, self.submission)

        self.assertEqual([finding.kind for finding in scan.findings], ["unscannable-extract"])

    def test_a_prior_review_result_is_relabelled_by_recorded_identity(self) -> None:
        self.transcript.write_text(
            "\n".join(
                json.dumps(item)
                for item in [
                    row("user", "watermark", {"content": "First sitting."}),
                    row(
                        "user",
                        "notification-row",
                        {
                            "content": (
                                "<task-notification><task-id>reader-1</task-id>"
                                "<result>Earlier verdicts.</result></task-notification>"
                            )
                        },
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "first.md").write_text(
            "\n".join(
                [
                    "# AFTER-ACTION REVIEW",
                    "SUBMISSION: first",
                    f"TRANSCRIPTS: {self.transcript.stem}",
                    "WATERMARK: watermark",
                    "CLASSIFIER-ENTRY: reader-1",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        population, _transcripts = aar_scan.collect_population(self.run, self.transcript)

        self.assertEqual([(item.identifier, item.kind) for item in population], [("reader-1", "prior-review")])

    def test_prior_records_select_the_furthest_watermark_not_the_last_filename(self) -> None:
        self.transcript.write_text(
            "\n".join(
                json.dumps(row("user", identifier, {"content": identifier}))
                for identifier in ("first", "second", "third")
            )
            + "\n",
            encoding="utf-8",
        )
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "review.md").write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\nWATERMARK: second\nCLASSIFIER-ENTRY: current-reader\n",
            encoding="utf-8",
        )
        (aar / "review.pass1.md").write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\nWATERMARK: first\n",
            encoding="utf-8",
        )

        population, _transcripts = aar_scan.collect_population(self.run, self.transcript)

        self.assertEqual([candidate.identifier for candidate in population], ["third"])
        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        fields, _identifiers = aar_scan._extract_metadata(
            aar_scan.extract_path(self.run, self.submission)
        )
        self.assertEqual(fields["UNMARKED-PRIOR-REVIEWS"], "0")

    def test_a_legacy_notification_uuid_remains_a_valid_watermark_alias(self) -> None:
        self.transcript.write_text(
            "\n".join(
                json.dumps(item)
                for item in [
                    row(
                        "user",
                        "legacy-notification-uuid",
                        {
                            "content": (
                                "<task-notification><task-id>reader-legacy</task-id>"
                                "<result>Finished.</result></task-notification>"
                            )
                        },
                    ),
                    row("user", "after", {"content": "Continue."}),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "legacy.md").write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\nWATERMARK: legacy-notification-uuid\n",
            encoding="utf-8",
        )

        population, _transcripts = aar_scan.collect_population(self.run, self.transcript)

        self.assertEqual([candidate.identifier for candidate in population], ["after"])

    def test_a_prior_watermark_without_classifier_identity_is_reported(self) -> None:
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "legacy.md").write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\nWATERMARK: u1\n",
            encoding="utf-8",
        )

        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        fields, _identifiers = aar_scan._extract_metadata(
            aar_scan.extract_path(self.run, self.submission)
        )

        self.assertEqual(fields["UNMARKED-PRIOR-REVIEWS"], "1")
        self.write_clean()
        scan = aar_scan.survey(self.run, self.submission)
        self.assertIn("unmarked-prior-review", [finding.kind for finding in scan.findings])

    def write_clean(self) -> None:
        fields, _identifiers = self.extract()
        record = "\n".join(
            [
                "# AFTER-ACTION REVIEW",
                f"SUBMISSION: {self.submission}",
                f"TRANSCRIPTS: {fields['TRANSCRIPTS']}",
                f"POPULATION: {fields['POPULATION']}",
                "UNREAD: 0",
                f"WATERMARK: {fields['WATERMARK']}",
                f"MEMORY-INDEX: {self.memory}",
                "CLASSIFIER: fresh adversarial reader",
                "CLASSIFIER-ENTRY: reader-1",
                "DISAGREEMENTS: none recorded",
                "CORRECTIONS: none",
                "SUSTAINS: none",
                "",
            ]
        )
        aar_scan.review_path(self.run, self.submission).write_text(record, encoding="utf-8")

    def test_missing_record_is_the_expected_row(self) -> None:
        scan = aar_scan.survey(self.run, self.submission)

        self.assertEqual([row.kind for row in scan.findings], ["missing-review"])
        self.assertIsNotNone(aar_scan.completion_finding(self.run, [self.submission]))

    def test_a_complete_zero_correction_review_passes(self) -> None:
        self.write_clean()

        scan = aar_scan.survey(self.run, self.submission)

        self.assertEqual(scan.findings, ())
        self.assertEqual(scan.unread, 0)
        self.assertIsNone(aar_scan.completion_finding(self.run, [self.submission]))

    def test_a_post_cutoff_review_requires_the_classifier_entry_identity(self) -> None:
        self.write_clean()
        review = aar_scan.review_path(self.run, self.submission)
        review.write_text(
            review.read_text(encoding="utf-8").replace("CLASSIFIER-ENTRY: reader-1\n", ""),
            encoding="utf-8",
        )

        scan = aar_scan.survey(self.run, self.submission)

        self.assertIn("missing-classifier-entry", [finding.kind for finding in scan.findings])

    def test_a_clean_graded_command_drains_orphan_pointers_after_reporting(self) -> None:
        self.write_clean()
        pointer = self.run / "aar" / "orphaned-earlier.json"
        pointer.write_text(
            json.dumps(
                {
                    "transcript_path": str(self.transcript),
                    "run_key": self.run.name,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        stdout = io.StringIO()
        stderr = io.StringIO()
        original_unlink = Path.unlink

        def unlink_after_report(path: Path, *args: object, **kwargs: object) -> None:
            self.assertIn(
                "after-action review over course-module-discussion", stdout.getvalue()
            )
            original_unlink(path, *args, **kwargs)

        with (
            mock.patch.object(Path, "unlink", unlink_after_report),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = aar_scan.main([str(self.run), "--submission", self.submission])

        self.assertEqual((status, stderr.getvalue()), (0, ""))
        self.assertFalse(pointer.exists())

    def test_a_correction_cannot_be_dispositioned_nowhere(self) -> None:
        fields, identifiers = self.extract()
        event = sorted(identifiers)[0]
        record = "\n".join(
            [
                "# AFTER-ACTION REVIEW",
                f"SUBMISSION: {self.submission}",
                f"TRANSCRIPTS: {fields['TRANSCRIPTS']}",
                f"POPULATION: {fields['POPULATION']}",
                "UNREAD: 0",
                f"WATERMARK: {fields['WATERMARK']}",
                f"MEMORY-INDEX: {self.memory}",
                "CLASSIFIER: fresh adversarial reader",
                "CLASSIFIER-ENTRY: reader-1",
                "DISAGREEMENTS: none recorded",
                "SUSTAINS: none",
                f"## CORRECTION: {event}",
                "CORRECTOR: clinician",
                "IN-ERROR: orchestrator",
                "SUMMARY: cited the wrong regulation section",
                "CLASSIFIER: tracker ticket",
                "ORCHESTRATOR: agree - the citation was wrong",
                "DISPOSITION: nothing durable",
                "TARGET: none",
                "LANDING: none",
                "",
            ]
        )
        aar_scan.review_path(self.run, self.submission).write_text(record, encoding="utf-8")

        kinds = {row.kind for row in aar_scan.survey(self.run, self.submission).findings}

        self.assertIn("unknown-disposition", kinds)


class EveryScopedCompletionGraderExpectsTheReview(unittest.TestCase):
    def test_every_scoped_skill_maps_to_a_grader_that_expects_the_fixed_row(self) -> None:
        self.assertEqual(set(aar_scan.COMPLETION_GRADERS), set(aar_scan.SCOPED_SKILLS))
        for skill, module_name in aar_scan.COMPLETION_GRADERS.items():
            with self.subTest(skill=skill, grader=module_name):
                module = importlib.import_module(module_name)
                self.assertEqual(module.EXPECTED_COMPLETION_CHECKS, (aar_scan.EXPECTED_ROW,))
                text = (
                    Path(__file__).resolve().parent.parent / "skills" / skill / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn(module_name, text)
                self.assertIn("--submission", text)

    def test_an_unpaired_scoped_skill_is_named(self) -> None:
        with self.assertRaisesRegex(ValueError, "unpaired-skill"):
            aar_scan.validate_completion_graders(
                {"unpaired-skill"}, aar_scan.COMPLETION_GRADERS
            )

    def test_each_scoped_skill_invokes_aar_and_its_completion_row(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for name in aar_scan.SCOPED_SKILLS:
            with self.subTest(skill=name):
                text = (root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("`/AAR`", text)
                self.assertIn("the after-action review: clean", text)

    def test_session_end_is_registered_as_the_orphan_pointer_only(self) -> None:
        root = Path(__file__).resolve().parent.parent
        settings = json.loads((root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        registered = settings["hooks"]["SessionEnd"]
        aar_handlers = [
            handler
            for registration in registered
            for handler in registration["hooks"]
            if "aar_scan.py" in handler["command"]
        ]

        self.assertEqual(len(aar_handlers), 1)
        self.assertIn("--session-end", aar_handlers[0]["command"])


class OrphanedSitting(unittest.TestCase):
    def test_session_end_writes_exactly_the_two_field_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "scratch" / "runs" / "course-module-discussion"
            run.mkdir(parents=True)
            transcript = root / "session-1.jsonl"
            write_transcript(transcript, run)
            original = aar_scan.repo_root.scratch_root
            aar_scan.repo_root.scratch_root = lambda: root / "scratch"
            try:
                status = aar_scan.session_end(
                    {
                        "hook_event_name": "SessionEnd",
                        "session_id": "session-1",
                        "transcript_path": str(transcript),
                        "reason": "other",
                    }
                )
            finally:
                aar_scan.repo_root.scratch_root = original

            self.assertEqual(status, 0)
            pointers = aar_scan.orphan_paths(run)
            self.assertEqual(len(pointers), 1)
            payload = json.loads(pointers[0].read_text(encoding="utf-8"))
            self.assertEqual(set(payload), {"transcript_path", "run_key"})
            self.assertEqual(payload["run_key"], run.name)

    def test_subagent_session_gets_no_pointer(self) -> None:
        self.assertEqual(
            aar_scan.session_end(
                {
                    "hook_event_name": "SessionEnd",
                    "agent_id": "agent-1",
                    "session_id": "session-1",
                    "transcript_path": "missing.jsonl",
                }
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
