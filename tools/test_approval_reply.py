"""Whole clinician messages bind approvals to their source revision. #1474."""

from contextlib import ExitStack, redirect_stdout, redirect_stderr
from datetime import datetime, timedelta
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import artifact_lock_test_support
import aar_scan
import approval_record as approvals
import differential_scan
import run_grader
from project_context_test_support import write_none_context


REPLY = "Approved, provided the documented condition is kept."
LATER = "2100-10-09T12:00:00Z"
NEXT = "2100-10-09T12:01:00Z"


def human(text=REPLY, timestamp=LATER, **flags):
    return {"type": "user", "timestamp": timestamp,
            "message": {"content": text}, **flags}


def codex(text=REPLY, timestamp=LATER, **flags):
    return {"type": "response_item", "timestamp": timestamp,
            "payload": {"type": "message", "role": "user",
                        "content": [{"type": "input_text", "text": text}]}, **flags}


class WholeReplyApproval(unittest.TestCase):
    def setUp(self):
        from approval_record_test_support import isolate_manifest_binding
        isolate_manifest_binding(self)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "scratch" / "runs" / "synthetic-approval"
        self.run.mkdir(parents=True)
        write_none_context(self.run)
        self.source = self.run / "post.md"
        self.source.write_text("Synthetic approved content.\n", encoding="utf-8")
        os.utime(self.source, (100, 100))
        self.sessions = self.root / "sessions"
        self.sessions.mkdir()
        self.transcript = self.sessions / "main.jsonl"
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(mock.patch.object(aar_scan, "transcript_roots", return_value=(self.sessions,)))
        stack.enter_context(mock.patch.object(aar_scan, "is_live_run", return_value=True))
        stack.enter_context(mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=self.root / "scratch"))
        stack.enter_context(mock.patch.object(approvals, "_pre_post_grade", return_value=(0, "pregrade clean")))
        # ADR 0318 tests isolate whole-reply binding; ADR 0330 is exercised in test_reader_remarks.
        stack.enter_context(mock.patch.object(approvals.reader_remarks, "verify", return_value=[]))
        self.write(human())

    def write(self, *rows, path=None, shown=True):
        # Real discovery must find the run in a main transcript's tool input.
        reference = {"type": "assistant", "message": {"content": [{
            "type": "tool_use", "id": "read-run", "name": "Read",
            "input": {"path": str(self.run / "post.md")},
        }]}}
        shown_at = datetime.fromtimestamp(max(101, self.source.stat().st_mtime + 1), tz=datetime.fromisoformat(LATER.replace("Z", "+00:00")).tzinfo).isoformat()
        presentation = ({"type": "assistant", "timestamp": shown_at,
                         "message": {"content": self.source.read_text(encoding="utf-8")}},) if shown else ()
        # Route disclosure is a separate prerequisite from the body presentation
        # these tests deliberately omit or corrupt. Reapprovals need a new line.
        with_routes = []
        for row in rows:
            if row.get("type") == "user" or row.get("payload", {}).get("role") == "user":
                route_at = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")) - timedelta(microseconds=1)
                with_routes.append({"type": "assistant", "timestamp": route_at.isoformat(),
                    "message": {"content": "Canvas load route (synthetic-post): Raw HTML — cost: confirm raw textarea and return to formatted view."}})
            with_routes.append(row)
        (path or self.transcript).write_text(
            "\n".join(json.dumps(row) for row in (reference, *presentation, *with_routes)) + "\n",
            encoding="utf-8",
        )

    def approve(self, reply=REPLY, skill="discussion-post", kind="content"):
        return approvals.approve(
            self.run, skill=skill, submission="synthetic-post", sources=(self.source,),
            grader_args=(str(self.run),), content_approved=True, clinician_reply=reply, approval_kind=kind,
        )

    def record(self):
        return json.loads((self.run / approvals.RECORD).read_text(encoding="utf-8"))

    def posted(self, skill="discussion-post", clinician=False):
        recorder = approvals.record_clinician_posting if clinician else approvals.record_agent_posting
        recorder(self.run, skill=skill, submission="synthetic-post")
        (self.run / "reread.md").write_text(
            "## REREAD: synthetic-post\nPOST-URL: https://example.test/posts/1\n"
            "POSTED: 2026-10-09 12:00\nREAD: 2026-10-09\n"
            f"SUBMISSION-SHA256: {sha256(self.source.read_bytes()).hexdigest()}\n"
            "VERDICT: matches - full stored body checked\n", encoding="utf-8",
        )

    def test_whole_reply_is_private_and_spacing_does_not_change_the_match(self):
        for row in (human(" Approved,\n provided the documented condition is kept. "), codex()):
            with self.subTest(row_type=row["type"]):
                (self.run / approvals.RECORD).unlink(missing_ok=True)
                self.write(row)
                self.approve()
                item = self.record()["items"][0]
                self.assertEqual(REPLY, item["clinician_reply"])
                self.assertEqual("verified", item["reply_verification"])

    def test_absent_stale_substring_and_blank_replies_refuse_without_writing(self):
        cases = (
            (human("No go-ahead."), REPLY),
            (human(timestamp="1970-01-01T00:00:01Z"), REPLY),
            (human(REPLY + " Fix the date first."), REPLY),
            (human(), " \n "),
        )
        for row, reply in cases:
            with self.subTest(row=row, reply=reply):
                self.write(row)
                with self.assertRaises(approvals.ApprovalRecordError) as error:
                    self.approve(reply)
                self.assertNotIn(REPLY, str(error.exception))
                self.assertFalse((self.run / approvals.RECORD).exists())

    def test_newest_source_time_is_the_boundary_and_equal_time_is_not_later(self):
        timestamp = datetime.fromisoformat(LATER.replace("Z", "+00:00")).timestamp()
        os.utime(self.source, (timestamp, timestamp))
        with self.assertRaises(approvals.ApprovalRecordError):
            self.approve()

    def test_machine_and_other_context_entries_never_supply_the_reply(self):
        tool = {"type": "user", "timestamp": LATER, "message": {"content": [{
            "type": "tool_result", "tool_use_id": "read-run", "content": REPLY,
        }]}}
        cases = {
            "tool result": tool,
            "Codex tool result": {"type": "response_item", "timestamp": LATER,
                                  "payload": {"type": "function_call_output", "output": REPLY}},
            "hook context": human(REPLY, isMeta=True),
            "scheduled trigger": codex(f"<scheduled-trigger>{REPLY}</scheduled-trigger>"),
            "relayed session": codex(f"<codex_delegation>{REPLY}</codex_delegation>"),
            "sidechain": human(REPLY, isSidechain=True),
            "reminder only": human(f"<system-reminder>{REPLY}</system-reminder>"),
        }
        for label, row in cases.items():
            with self.subTest(kind=label):
                self.write(row)
                with self.assertRaises(approvals.ApprovalRecordError):
                    self.approve()
                self.assertFalse((self.run / approvals.RECORD).exists())

    def test_subagent_transcripts_are_excluded_by_actual_discovery(self):
        self.write(human("No approval in the main sitting."))
        subagents = self.sessions / "subagents"
        subagents.mkdir()
        self.write(human(), path=subagents / "claude-agent.jsonl")
        self.write({"type": "session_meta", "payload": {"source": {"subagent": {"name": "reader"}}}},
                   codex(), path=self.sessions / "codex-agent.jsonl")
        with self.assertRaises(approvals.ApprovalRecordError):
            self.approve()
        self.assertFalse((self.run / approvals.RECORD).exists())

    def test_harness_reminder_plus_human_reply_keeps_the_human_remainder(self):
        for row in (human, codex):
            with self.subTest(adapter=row.__name__):
                (self.run / approvals.RECORD).unlink(missing_ok=True)
                self.write(row(f"<system-reminder>Harness instructions.</system-reminder>\n{REPLY}"))
                self.approve()
                self.assertEqual("verified", self.record()["items"][0]["reply_verification"])

    def test_reapproval_requires_a_later_message_and_preserves_both_whole_replies(self):
        self.approve()
        before = (self.run / approvals.RECORD).read_bytes()
        with self.assertRaises(approvals.ApprovalRecordError):
            self.approve()
        self.assertEqual(before, (self.run / approvals.RECORD).read_bytes())
        self.write(human(), human(timestamp=NEXT))
        self.approve()
        item = self.record()["items"][0]
        self.assertEqual(2, len(item["approvals"]))
        self.assertEqual([REPLY, REPLY], [row["clinician_reply"] for row in item["approvals"]])
        self.assertLess(item["approvals"][0]["reply_matched_at"], item["approvals"][1]["reply_matched_at"])

    def test_changed_source_does_not_move_the_old_approval_boundary(self):
        self.approve()
        later_reply = "Approve the revised synthetic content."
        self.source.write_text("Revised synthetic content.\n", encoding="utf-8")
        os.utime(self.source, (datetime.fromisoformat(LATER.replace("Z", "+00:00")).timestamp() + 1,) * 2)
        self.write(human(), human(later_reply, NEXT))
        self.approve(later_reply)
        self.assertEqual([REPLY, later_reply], [row["clinician_reply"] for row in self.record()["items"][0]["approvals"]])

    def test_summarized_ask_refuses_all_three_skills_without_quoting_blocks(self):
        self.source.write_text("# Synthetic heading\n\nFull synthetic paragraph.\n\n## References\n\nSynthetic reference.\n", encoding="utf-8")
        os.utime(self.source, (100, 100))
        for skill in approvals.SHOWN_TEXT_SKILLS:
            with self.subTest(skill=skill):
                self.write({"type": "assistant", "timestamp": "2100-10-09T11:59:59Z",
                            "message": {"content": "Summary only."}}, human(), shown=False)
                with self.assertRaisesRegex(approvals.ApprovalRecordError, "4 missing blocks") as error:
                    self.approve(skill=skill)
                self.assertNotIn("Full synthetic", str(error.exception))
                self.assertFalse((self.run / approvals.RECORD).exists())

    def test_verbatim_codex_ask_and_unchanged_gate_two_pass(self):
        self.write({"type": "response_item", "timestamp": "2100-10-09T11:59:59Z",
                    "payload": {"type": "message", "role": "assistant", "content": [
                        {"type": "output_text", "text": "Synthetic   approved\ncontent."}]}}, human(), shown=False)
        self.approve()
        self.assertEqual("verified", self.record()["items"][0]["shown_text_verification"])
        self.write(human(), human(timestamp=NEXT), shown=False)
        self.approve()
        self.assertEqual("exempt", self.record()["items"][0]["shown_text_verification"])

    def test_bare_reask_after_revision_refuses(self):
        self.approve()
        self.source.write_text("Revised synthetic content.\n", encoding="utf-8")
        os.utime(self.source, (datetime.fromisoformat(LATER.replace("Z", "+00:00")).timestamp() + 1,) * 2)
        self.write(human(), human(timestamp=NEXT), shown=False)
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "1 missing blocks"):
            self.approve()
        self.assertEqual(1, self.record()["approval_revision"])

    def test_unreadable_shown_text_is_incomplete_without_completion_recheck(self):
        self.transcript.write_text("{unreadable\n", encoding="utf-8")
        # Isolate the established shown-text fallback from the independent,
        # fail-closed route disclosure gate covered by test_canvas_load_route.
        with mock.patch.object(approvals.canvas_load_route, "require_shown"):
            result = self.approve()
        self.assertIn("shown-text transcript unreadable", result.pregrade_report)
        self.assertEqual("incomplete", self.record()["items"][0]["pregrade_status"])

    def test_committed_post_requires_its_full_reference_list(self):
        controls = Path(__file__).resolve().parents[1] / "fixtures" / "coursework-style"
        for skill in approvals.SHOWN_TEXT_SKILLS:
            with self.subTest(skill=skill):
                text = (controls / f"{skill}.md").read_text(encoding="utf-8")
                self.source.write_text(text, encoding="utf-8")
                os.utime(self.source, (100, 100))
                self.write(human())
                self.approve(skill=skill)
                (self.run / approvals.RECORD).unlink()
                self.write({"type": "assistant", "timestamp": "2100-10-09T11:59:59Z",
                            "message": {"content": text.rsplit("\n", 2)[0]}}, human(), shown=False)
                with self.assertRaisesRegex(approvals.ApprovalRecordError, "1 missing blocks"):
                    self.approve(skill=skill)

    def test_shown_text_must_be_main_assistant_text_inside_the_window(self):
        text = self.source.read_text(encoding="utf-8")
        cases = (
            {"type": "assistant", "timestamp": "1970-01-01T00:00:01Z", "message": {"content": text}},
            {"type": "assistant", "timestamp": NEXT, "message": {"content": text}},
            {"type": "assistant", "timestamp": "2100-10-09T11:59:59Z", "isSidechain": True, "message": {"content": text}},
            {"type": "user", "timestamp": "2100-10-09T11:59:59Z", "message": {"content": text}},
            {"type": "response_item", "timestamp": "2100-10-09T11:59:59Z", "payload": {"type": "function_call_output", "output": text}},
        )
        for row in cases:
            with self.subTest(row=row):
                self.write(row, human(), shown=False)
                with self.assertRaisesRegex(approvals.ApprovalRecordError, "1 missing blocks"):
                    self.approve()

    def test_unreadable_approval_is_rechecked_as_found_absent_or_incomplete(self):
        self.transcript.write_text("{unreadable\n", encoding="utf-8")
        # This control owns legacy reply rechecking, not route verification.
        with mock.patch.object(approvals.canvas_load_route, "require_shown"):
            self.approve()
        self.assertEqual("not verified", self.record()["items"][0]["reply_verification"])
        self.posted(clinician=True)
        result = approvals.completion_gate(self.run, "discussion-post", "synthetic-post")
        self.assertFalse(tuple(result)[0])
        self.assertTrue(result.coverage)
        self.write(human("No approval."))
        failed, report = approvals.completion_gate(self.run, "discussion-post", "synthetic-post")
        self.assertTrue(failed)
        self.assertNotIn(REPLY, report)
        self.write(human())
        failed, report = approvals.completion_gate(self.run, "discussion-post", "synthetic-post")
        self.assertFalse(failed)
        self.assertIn("clean", report)

    def test_no_transcript_records_incomplete_and_legacy_items_keep_the_old_grade(self):
        self.transcript.unlink()
        # Seed a legacy incomplete approval without claiming a route was shown.
        with mock.patch.object(approvals.canvas_load_route, "require_shown"):
            self.approve()
        self.posted()
        payload = self.record()
        item = payload["items"][0]
        self.assertEqual("not verified", item["reply_verification"])
        for name in ("reply_verification", "clinician_reply", "approvals", "approval_kind", "recorded_at"):
            item.pop(name)
        (self.run / approvals.RECORD).write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual((False, "the approval record: clean"), approvals.completion_gate(self.run, "discussion-post", "synthetic-post"))

    def test_pending_gate_one_cannot_reuse_its_only_reply_at_gate_two(self):
        self.transcript.unlink()
        # Seed the old pending-reply state; route failure has its own controls.
        with mock.patch.object(approvals.canvas_load_route, "require_shown"):
            self.approve()
        self.write(human())
        with self.assertRaises(approvals.ApprovalRecordError):
            self.approve()
        self.write(human(), human(timestamp=NEXT))
        self.approve(kind="posting")
        self.posted()
        self.assertFalse(approvals.completion_gate(self.run, "discussion-post", "synthetic-post")[0])

    def test_two_unreadable_gates_need_two_messages_at_completion(self):
        self.transcript.unlink()
        # Seed the old pending-reply state; route failure has its own controls.
        with mock.patch.object(approvals.canvas_load_route, "require_shown"):
            self.approve()
        self.approve(kind="posting")
        self.posted()
        self.write(human())
        self.assertTrue(approvals.completion_gate(self.run, "discussion-post", "synthetic-post")[0])
        self.write(human(), human(timestamp=NEXT))
        self.assertFalse(approvals.completion_gate(self.run, "discussion-post", "synthetic-post")[0])

    def test_pregrade_report_and_error_redact_the_whole_reply(self):
        for status in (0, 1, 2):
            with self.subTest(status=status):
                (self.run / approvals.RECORD).unlink(missing_ok=True)
                with mock.patch.object(approvals, "_pre_post_grade", return_value=(status, "grader: " + REPLY)):
                    if status == 1:
                        with self.assertRaises(approvals.ApprovalRecordError) as error:
                            self.approve()
                        text = str(error.exception)
                    else:
                        text = self.approve().pregrade_report
                    self.assertNotIn(REPLY, text)

    def test_terminal_grader_declares_unreadable_reply_and_findings_win(self):
        self.source.write_text(
            "S:\nSubjective.\nO:\nObjective.\nA:\nDifferential:\n"
            "1. Acute bronchitis - J20.9: favored.\nP:\nNon-pharmacologic:\n"
            "Pharmacologic:\nHealth Promotion/Patient Education:\nReferral/Follow-up:\nCoding worksheet\n",
            encoding="utf-8",
        )
        self.transcript.unlink()
        approvals.prepare(self.run, skill="clinical-note", submission="synthetic-post",
                          sources=(self.source,), grader_args=(str(self.run),))
        self.approve(skill="clinical-note")
        self.posted(skill="clinical-note")
        stack = ExitStack()
        self.addCleanup(stack.close)
        for module in (differential_scan.aar_scan, differential_scan.medatrax_posting, differential_scan.artifact_repairs):
            stack.enter_context(mock.patch.object(module, "completion_gate", return_value=(False, "other row clean")))
        out, error = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(error):
            status = differential_scan.main([str(self.run), "--note", str(self.source), "--submission", "synthetic-post"])
        self.assertEqual(2, status, error.getvalue())
        self.assertIn(approvals.REPLY_UNREADABLE, out.getvalue())
        self.assertNotIn(REPLY, out.getvalue() + error.getvalue())
        with mock.patch.object(differential_scan.artifact_repairs, "completion_gate", return_value=(True, "repair finding")):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(1, differential_scan.main([str(self.run), "--note", str(self.source), "--submission", "synthetic-post"]))


if __name__ == "__main__":
    unittest.main()
