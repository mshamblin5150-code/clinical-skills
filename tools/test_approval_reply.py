"""Whole clinician messages bind approvals to their source revision. #1474."""

from contextlib import ExitStack, redirect_stdout, redirect_stderr
from datetime import datetime
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
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "scratch" / "runs" / "synthetic-approval"
        self.run.mkdir(parents=True)
        self.source = self.run / "post.md"
        self.source.write_text("Synthetic approved content.\n", encoding="utf-8")
        os.utime(self.source, (100, 100))
        self.sessions = self.root / "sessions"
        self.sessions.mkdir()
        self.transcript = self.sessions / "main.jsonl"
        stack = self.enterContext(ExitStack())
        stack.enter_context(mock.patch.object(aar_scan, "transcript_roots", return_value=(self.sessions,)))
        stack.enter_context(mock.patch.object(aar_scan, "is_live_run", return_value=True))
        stack.enter_context(mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=self.root / "scratch"))
        stack.enter_context(mock.patch.object(approvals, "_pre_post_grade", return_value=(0, "pregrade clean")))
        self.write(human())

    def write(self, *rows, path=None):
        # Real discovery must find the run in a main transcript's tool input.
        reference = {"type": "assistant", "message": {"content": [{
            "type": "tool_use", "id": "read-run", "name": "Read",
            "input": {"path": str(self.run / "post.md")},
        }]}}
        (path or self.transcript).write_text(
            "\n".join(json.dumps(row) for row in (reference, *rows)) + "\n",
            encoding="utf-8",
        )

    def approve(self, reply=REPLY, skill="discussion-post"):
        return approvals.approve(
            self.run, skill=skill, submission="synthetic-post", sources=(self.source,),
            grader_args=(str(self.run),), content_approved=True, clinician_reply=reply,
        )

    def record(self):
        return json.loads((self.run / approvals.RECORD).read_text(encoding="utf-8"))

    def posted(self, skill="discussion-post"):
        approvals.record_agent_posting(self.run, skill=skill, submission="synthetic-post")
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

    def test_unreadable_approval_is_rechecked_as_found_absent_or_incomplete(self):
        self.transcript.write_text("{unreadable\n", encoding="utf-8")
        self.approve()
        self.assertEqual("not verified", self.record()["items"][0]["reply_verification"])
        self.posted()
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
        self.approve()
        self.posted()
        payload = self.record()
        item = payload["items"][0]
        self.assertEqual("not verified", item["reply_verification"])
        for name in ("reply_verification", "clinician_reply", "approvals"):
            item.pop(name)
        (self.run / approvals.RECORD).write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual((False, "the approval record: clean"), approvals.completion_gate(self.run, "discussion-post", "synthetic-post"))

    def test_pending_gate_one_cannot_reuse_its_only_reply_at_gate_two(self):
        self.transcript.unlink()
        self.approve()
        self.write(human())
        with self.assertRaises(approvals.ApprovalRecordError):
            self.approve()
        self.write(human(), human(timestamp=NEXT))
        self.approve()
        self.posted()
        self.assertFalse(approvals.completion_gate(self.run, "discussion-post", "synthetic-post")[0])

    def test_two_unreadable_gates_need_two_messages_at_completion(self):
        self.transcript.unlink()
        self.approve()
        self.approve()
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
        self.approve(skill="clinical-note")
        self.posted(skill="clinical-note")
        stack = self.enterContext(ExitStack())
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
