"""Synthetic public signing and changed-bar controls for ADR 0397."""
# phi-scan: synthetic
import artifact_lock_test_support
import artifact_lock
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest import mock

import approval_record
import bar_signatures
import checks_ledger
import research_ledger
import completion_checks
import run_record_reader
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta


class SharedBarSigning(unittest.TestCase):
    def test_public_peer_signature_finding_and_machine_coverage_keep_voice_grading(self):
        import test_voice_read as voice_tests
        mechanics_scope = voice_tests.mechanics_test_support.begin()
        self.addCleanup(voice_tests.mechanics_test_support.end, mechanics_scope)
        case = voice_tests.PublicCompletionCommand()
        case.setUp()
        self.addCleanup(case.doCleanups)
        self.assertEqual(0, case.command()[0])
        bar = case.run / "bar.md"
        original = bar.read_bytes()
        bar.write_bytes(original + b"Changed requirement.\n")
        status, report = case.command()
        self.assertEqual(1, status, report)
        self.assertIn("does not match its latest signature", report)
        self.assertNotIn("coverage failure names no exit-2 limb", report)
        bar.write_bytes(original)
        history = case.run / bar_signatures.RECORD
        history.write_bytes(b"{")
        self.assertEqual(2, case.command()[0])
        (case.records / voice_tests.voice_read.READER_RECORD_NAME).unlink()
        status, report = case.command()
        self.assertEqual(1, status, report)
        self.assertIn("reader record is missing or invalid", report)
        self.assertIn("unread tool-written records 1", report)

    def test_native_success_keeps_another_creators_reused_temporary_name(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            self.sign(run, "peer-critique", "SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\n")
            reply = "I confirm this second synthetic bar."
            messages = [{"type": "user", "timestamp": "2101-01-01T00:00:00Z", "message": {"content": reply}}]
            replace = bar_signatures.os.replace
            reused = []
            def publish_then_reuse(source, destination):
                replace(source, destination)
                if Path(destination) == run / "bar.md":
                    Path(source).write_bytes(b"other creator evidence")
                    reused.append(Path(source))
            with mock.patch.object(bar_signatures.os, "replace", side_effect=publish_then_reuse), mock.patch.object(
                approval_record, "_main_transcripts", return_value=([messages], False)
            ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(0, bar_signatures.main([str(run), "--skill", "peer-critique", "--reply", reply]))
            self.assertEqual(1, len(reused))
            self.assertEqual(b"other creator evidence", reused[0].read_bytes())
            history = json.loads((run / bar_signatures.RECORD).read_text())["signatures"]
            self.assertEqual(2, len(history))
            self.assertEqual(reply, history[-1]["clinician_reply"])
            self.assertEqual((run / "bar.md").read_bytes(), (run / history[-1]["copy"]).read_bytes())
            self.assertFalse(bar_signatures.completion_gate(run, skill="peer-critique")[0])

    def test_shared_signer_native_refusals_preserve_each_new_skill_history(self):
        for skill in bar_signatures.SKILLS[1:]:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                run = Path(directory)
                text = "SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\n"
                if skill == "discussion-post":
                    text += "TOPIC: Synthetic\nSYLLABUS: Synthetic\nWORD-FLOOR: 100\nWORD-CEILING: none\nREFERENCE-MINIMUM: 1\n"
                if skill == "practicum-case-study":
                    text += "SUBMISSION-TYPE: file-upload\nRequired: synthetic assessment.\n"
                self.sign(run, skill, text)
                history = run / bar_signatures.RECORD
                before = history.read_bytes(), (run / "bar.md").read_bytes(), (run / "signed-bars/bar-1.md").read_bytes()
                reply = "I confirm the second synthetic bar."
                messages = [{"type": "user", "timestamp": "2101-01-01T00:00:00Z", "message": {"content": reply}}]
                def command():
                    output = io.StringIO()
                    with mock.patch.object(approval_record, "_main_transcripts", return_value=([messages], False)), redirect_stdout(output), redirect_stderr(output):
                        status = bar_signatures.main([str(run), "--skill", skill, "--reply", reply])
                    return status, output.getvalue()
                with artifact_lock.hold(history, "synthetic owner"):
                    status, report = command()
                self.assertEqual(2, status, report)
                self.assertIn("held by another task:", report)
                replace = run_record_reader.os.replace
                def interrupted(source, destination):
                    if Path(destination) == history:
                        raise OSError("PRIVATE-PLANTED")
                    return replace(source, destination)
                with mock.patch.object(run_record_reader.os, "replace", side_effect=interrupted):
                    status, report = command()
                self.assertEqual(2, status, report)
                self.assertIn("unreadable — could not be opened", report)
                self.assertNotIn("PRIVATE-PLANTED", report)
                self.assertEqual(before, (history.read_bytes(), (run / "bar.md").read_bytes(), (run / "signed-bars/bar-1.md").read_bytes()))
                self.assertFalse((run / "signed-bars/bar-2.md").exists())
                competing = run / "bar.md.collision.building"
                competing.write_bytes(b"competing evidence")
                with mock.patch.object(bar_signatures.uuid, "uuid4", return_value=mock.Mock(hex="collision")):
                    status, report = command()
                self.assertEqual(2, status, report)
                self.assertEqual(b"competing evidence", competing.read_bytes())
                self.assertEqual(before[:2], (history.read_bytes(), (run / "bar.md").read_bytes()))
                self.assertFalse((run / "signed-bars/bar-2.md").exists())

    def test_concurrent_shared_signs_allocate_distinct_retained_revisions(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "bar.md").write_text("SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\n", encoding="utf-8")
            verification = approval_record.ReplyVerification("not verified", "synthetic unread transcript")
            with mock.patch.object(approval_record, "verify_clinician_reply", return_value=verification), ThreadPoolExecutor(max_workers=2) as pool:
                entries = list(pool.map(lambda reply: bar_signatures.sign(run, reply, skill="discussion-reply"), ("first whole reply", "second whole reply")))
            history = json.loads((run / bar_signatures.RECORD).read_text())["signatures"]
            self.assertEqual({entry["copy"] for entry in entries}, {"signed-bars/bar-1.md", "signed-bars/bar-2.md"})
            self.assertEqual({entry["clinician_reply"] for entry in history}, {"first whole reply", "second whole reply"})
            self.assertFalse(bar_signatures.completion_gate(run, skill="discussion-reply")[0])

    def test_retained_signature_boundary_names_the_shared_owner(self):
        instructions = (Path(__file__).resolve().parents[1] / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("retained bar signatures to `bar_signatures.DECLARED_LIMITS`", instructions)
        self.assertNotIn("assignment_bar.DECLARED_LIMITS", instructions)
        self.assertTrue(any("Unreadable retained signature bookkeeping" in line for line in bar_signatures.DECLARED_LIMITS))

    def test_damaged_signature_history_preserves_independent_ledger_findings(self):
        import test_research_ledger as ledger_tests
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            text = "SOURCE-CLASSES: society guideline | peer-reviewed | government | tertiary reference\nRECENCY-WINDOW-YEARS: 5\n"
            self.sign(run, "discussion-reply", text)
            record = run / bar_signatures.RECORD
            record.write_bytes(b'{')
            claims = run / "claims.md"
            for body, expected in ((ledger_tests.ledger_text(ledger_tests.CLEAN), 2), ("DATE: 2026-09-02\n\n## CLAIM: Synthetic statement.\nSTATUS: invented\n", 1)):
                claims.write_text(body, encoding="utf-8")
                output = io.StringIO()
                with redirect_stdout(output), redirect_stderr(output):
                    status = research_ledger.main([str(claims)])
                self.assertEqual(expected, status, output.getvalue())
                self.assertIn("unread tool-written records 1", output.getvalue())
                self.assertIn("not graded", output.getvalue())
            self.assertEqual(b'{', record.read_bytes())

    def test_historical_completion_starts_at_the_exact_approval_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "bar.md").write_text("SIGNED: 2000-01-01\nSOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\n", encoding="utf-8")
            cutoff = completion_checks.registry()["bar_signatures:completion_gate"][0]
            for moment, expected in ((cutoff - timedelta(microseconds=1), False), (cutoff, True)):
                token = completion_checks.MOMENTS.set({"approval": moment})
                try:
                    self.assertEqual(expected, bar_signatures.completion_gate(run, skill="peer-critique")[0])
                finally:
                    completion_checks.MOMENTS.reset(token)

    def sign(self, run, skill, text, reply="2", moment="2100-01-01T00:00:00Z"):
        (run / "bar.md").write_text(text, encoding="utf-8")
        os.utime(run / "bar.md", (100, 100))
        messages = [{"type": "user", "timestamp": moment, "message": {"content": reply}}]
        with mock.patch.object(approval_record, "_main_transcripts", return_value=([messages], False)):
            return bar_signatures.sign(run, reply, skill=skill)

    def test_ledger_refuses_an_edit_and_a_reused_post_signature_is_checked_without_resigning(self):
        from test_research_ledger import CLEAN, ledger_text
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            text = "SOURCE-CLASSES: society guideline | peer-reviewed | government | tertiary reference\nRECENCY-WINDOW-YEARS: 5\nTOPIC: Synthetic\nSYLLABUS: Synthetic\nWORD-FLOOR: 100\nWORD-CEILING: none\nREFERENCE-MINIMUM: 1\n"
            self.sign(run, "discussion-post", text)
            history = (run / bar_signatures.RECORD).read_bytes()
            self.assertFalse(bar_signatures.completion_gate(run, skill="discussion-reply")[0])
            self.assertEqual(history, (run / bar_signatures.RECORD).read_bytes())
            claims = run / "claims.md"
            claims.write_text(ledger_text(CLEAN), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                clean = research_ledger.main([str(claims)])
                (run / "bar.md").write_bytes((run / "bar.md").read_bytes() + b"Changed requirement.\n")
                changed = research_ledger.main([str(claims)])
            self.assertEqual((0, 1), (clean, changed), output.getvalue())
            self.assertIn("does not match its latest signature", output.getvalue())

    def test_bar_walk_must_be_repeated_after_resigning(self):
        from test_checks_ledger import PreReviewWalksThroughCommand
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            text = "SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\nSUBMISSION-TYPE: file-upload\nRequired: synthetic assessment.\n"
            first = self.sign(run, "practicum-case-study", text)
            records = PreReviewWalksThroughCommand().records()
            records["routing-walk.json"] = {"entries": [], "none": "No synthetic routing subjects"}
            records["bar-walk.json"]["bar_sha256"] = first["sha256"]
            for name, value in records.items():
                (run / name).write_text(json.dumps(value), encoding="utf-8")
            checks = run / "checks.md"
            checks.write_text("FIRST-DRAFT: 2099-01-01T00:00:00Z\n", encoding="utf-8")
            def grade():
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    return checks_ledger.main([str(checks), "--walks-only"])
            self.assertEqual(0, grade())
            latest = self.sign(run, "practicum-case-study", text + "Required: synthetic follow-up.\n", "3", "2100-01-01T00:01:00Z")
            self.assertEqual(1, grade())
            records["bar-walk.json"]["bar_sha256"] = latest["sha256"]
            (run / "bar-walk.json").write_text(json.dumps(records["bar-walk.json"]), encoding="utf-8")
            self.assertEqual(0, grade())
            (run / bar_signatures.RECORD).write_bytes(b'{')
            self.assertEqual(2, grade())  # Signature-dependent comparison is not graded.
            records["bar-walk.json"]["entries"] = [{"element": "Synthetic requirement", "outcome": "invented"}]
            (run / "bar-walk.json").write_text(json.dumps(records["bar-walk.json"]), encoding="utf-8")
            self.assertEqual(1, grade())  # Independent walk content still refuses.

    def test_each_new_skill_signs_and_refuses_changed_bytes(self):
        for skill in ("discussion-post", "discussion-reply", "peer-critique", "practicum-case-study"):
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as directory:
                run = Path(directory)
                text = "SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\n"
                if skill == "discussion-post":
                    text += "TOPIC: Synthetic\nSYLLABUS: Synthetic\nWORD-FLOOR: 100\nWORD-CEILING: none\nREFERENCE-MINIMUM: 1\n"
                if skill == "practicum-case-study":
                    text += "SUBMISSION-TYPE: file-upload\nRequired: explain the supplied synthetic case.\n"
                (run / "bar.md").write_text(text, encoding="utf-8")
                os.utime(run / "bar.md", (100, 100))
                messages = [{"type": "user", "timestamp": "2100-01-01T00:00:00Z", "message": {"content": "2"}}]
                with mock.patch.object(approval_record, "_main_transcripts", return_value=([messages], False)), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(0, bar_signatures.main([str(run), "--skill", skill, "--reply", "2"]))
                self.assertFalse(bar_signatures.completion_gate(run, skill=skill)[0])
                retained = json.loads((run / "bar-signatures.json").read_text())["signatures"][-1]
                self.assertEqual("2", retained["clinician_reply"])
                (run / "bar.md").write_text((run / "bar.md").read_text() + "Changed requirement.\n")
                self.assertTrue(bar_signatures.completion_gate(run, skill=skill)[0])


if __name__ == "__main__":
    unittest.main()
