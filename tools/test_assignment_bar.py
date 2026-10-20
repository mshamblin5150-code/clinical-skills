"""Public-interface tests for course-assignment artifact discrimination."""

from __future__ import annotations

import artifact_lock_test_support
import unittest
import json
import os
from contextlib import redirect_stdout, redirect_stderr
import io
from pathlib import Path
import tempfile
from unittest import mock

import assignment_bar
import course_assignment_scan
import deck_scan
import run_grader
import approval_record
import assignment_submission
import completion_checks
from project_context_test_support import write_none_context


DOCX_BAR = """\
ASSIGNMENT: https://example.invalid/assignment
SIGNED: 2026-09-13
ARTIFACT: docx
SUBMISSION-TYPE: file-upload
WORD-MIN: 900
WORD-MAX: 1200
REFERENCE-MIN: 3
SOURCE-CLASSES: peer-reviewed | government
RECENCY-WINDOW-YEARS: 5
"""

DECK_BAR = """\
ASSIGNMENT: https://example.invalid/assignment
SIGNED: 2026-09-13
ARTIFACT: deck
SLIDE-MAX: 10
SLIDE-LIMIT-SCOPE: all
SUBMISSION-TYPE: file-upload
AUDIENCE-PURPOSE: Explain the assignment.
TALK-STYLE: Academic presentation.
BULLETS-PER-SLIDE: 6
WORDS-PER-BULLET: 6
FONT-POINTS: 24
FONT-DIRECTION: floor
SOURCE-CLASSES: peer-reviewed | government
RECENCY-WINDOW-YEARS: 5
"""


class ArtifactDiscrimination(unittest.TestCase):
    def test_a_valid_docx_bar_selects_the_docx_adapter(self):
        envelope = assignment_bar.parse(DOCX_BAR)

        self.assertEqual("docx", envelope.artifact)
        self.assertEqual("assignment_docx_scan", assignment_bar.adapter_name(envelope))

    def test_an_ambiguous_artifact_field_fails_loudly(self):
        ambiguous = DOCX_BAR.replace(
            "ARTIFACT: docx", "ARTIFACT: deck\nARTIFACT: docx"
        )

        with self.assertRaisesRegex(
            run_grader.SourceError, "duplicate ARTIFACT"
        ):
            assignment_bar.parse(ambiguous)

    def test_the_dispatcher_passes_the_parsed_envelope_to_the_docx_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
            adapter = mock.Mock()
            adapter.main.return_value = 17

            with mock.patch.object(
                course_assignment_scan, "_import_adapter", return_value=adapter
            ) as imported:
                status = course_assignment_scan.main([str(run), "--artifact", "paper.docx"])

        imported.assert_called_once_with("assignment_docx_scan")
        envelope = adapter.main.call_args.kwargs["envelope"]
        self.assertEqual("docx", envelope.artifact)
        self.assertEqual(17, status)

    def test_dispatcher_preserves_adapter_option_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
            adapter = mock.Mock()
            adapter.main.return_value = 2
            with mock.patch.object(
                course_assignment_scan, "_import_adapter", return_value=adapter
            ):
                status = course_assignment_scan.main(
                    [str(run), "--artifact", "paper.docx", "--submission", "--show"]
                )

        self.assertEqual(2, status)

    def test_bar_only_validation_does_not_require_a_finished_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(0, status)

    def test_docx_bar_can_leave_the_word_maximum_unbounded(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            unbounded = DOCX_BAR.replace("WORD-MAX: 1200", "WORD-MAX: none")
            (run / "bar.md").write_text(unbounded, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(0, status)

    def test_numeric_word_maximum_is_recorded_without_blocking_the_bar(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            recorded = DOCX_BAR.replace("WORD-MAX: 1200", "WORD-MAX: 1")
            (run / "bar.md").write_text(recorded, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(0, status)

    def test_bar_only_validation_rejects_an_incomplete_docx_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            incomplete = DOCX_BAR.replace("WORD-MIN: 900\n", "")
            (run / "bar.md").write_text(incomplete, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(2, status)

    def test_bar_only_validation_rejects_a_nonpositive_recency_window(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            invalid = DOCX_BAR.replace("RECENCY-WINDOW-YEARS: 5", "RECENCY-WINDOW-YEARS: 0")
            (run / "bar.md").write_text(invalid, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(2, status)

    def test_bar_only_validation_rejects_an_unknown_source_class(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            invalid = DOCX_BAR.replace(
                "peer-reviewed | government", "peer-reviewed | invented source"
            )
            (run / "bar.md").write_text(invalid, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(2, status)

    def test_the_legacy_deck_adapter_accepts_a_preparsed_envelope(self):
        status = deck_scan.main([], envelope=assignment_bar.parse(DECK_BAR))

        self.assertEqual(2, status)


class BarSignatures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        self.bar = self.run / "bar.md"
        self.messages = []
        self.transcripts = mock.patch.object(approval_record, "_main_transcripts",
            side_effect=lambda run: ([self.messages], False))
        self.transcripts.start()
        self.addCleanup(self.transcripts.stop)

    def draft(self, text):
        self.bar.write_text(text.replace("SIGNED: 2026-09-13\n", ""), encoding="utf-8")
        os.utime(self.bar, (100, 100))

    def sign(self, reply="I confirm this bar.", timestamp="2100-10-09T12:00:00Z"):
        self.messages.append({"type": "user", "timestamp": timestamp,
                              "message": {"content": reply}})
        return assignment_bar.sign(self.run, reply)

    def scan(self, *args):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            status = course_assignment_scan.main([str(self.run), *args])
        self.report = output.getvalue()
        return status

    def test_signed_bytes_and_both_versions_are_retained_for_each_branch(self):
        for text in (DOCX_BAR, DECK_BAR):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as directory:
                self.run = Path(directory)
                self.bar = self.run / "bar.md"
                self.messages = []
                self.draft(text)
                self.sign()
                first = self.bar.read_bytes()
                self.assertEqual(0, self.scan("--bar-only"))
                with mock.patch.object(course_assignment_scan, "_import_adapter") as imported:
                    imported.return_value.main.return_value = 0
                    self.assertEqual(0, self.scan("--artifact", "paper.docx", "--submission", "paper"))
                self.bar.write_bytes(first + b"Changed requirement.\n")
                self.assertEqual(2, self.scan("--bar-only"))
                self.assertEqual(2, self.scan("--artifact", "missing.docx"))
                self.assertEqual(2, self.scan("--artifact", "missing.docx", "--submission", "paper"))
                self.assertIn("does not match its latest signature", self.report)
                self.sign("I confirm the amended bar.", "2100-10-09T12:01:00Z")
                self.assertEqual(0, self.scan("--bar-only"))
                record = json.loads((self.run / assignment_bar.RECORD).read_text())
                self.assertEqual(2, len(record["signatures"]))
                self.assertEqual(first, (self.run / record["signatures"][0]["copy"]).read_bytes())
                self.assertEqual(self.bar.read_bytes(), (self.run / record["signatures"][1]["copy"]).read_bytes())
                self.assertEqual("I confirm the amended bar.", record["signatures"][1]["clinician_reply"])

    def test_missing_signature_refuses_a_current_bar_but_legacy_is_not_graded(self):
        self.bar.write_text(DOCX_BAR.replace("2026-09-13", "2100-01-01"))
        self.assertEqual(2, self.scan("--bar-only"))
        self.bar.write_text(DOCX_BAR)
        failed, report = assignment_bar.completion_gate(self.run)
        self.assertFalse(failed)
        self.assertIn("not graded", report)
        self.assertIn("assignment_bar:completion_gate", completion_checks.registry())
        self.bar.write_text(DOCX_BAR.replace("2026-09-13", "2026-10-12"))
        self.assertIn("not graded", assignment_bar.completion_gate(self.run)[1])

    def test_own_work_request_can_precede_the_requested_bar_edit(self):
        self.draft(DOCX_BAR)
        self.sign()
        request = "Please use my own unpublished work."
        self.messages.append({"type": "user", "timestamp": "2100-10-09T12:01:00Z",
                              "message": {"content": request}})
        self.bar.write_text(self.bar.read_text().replace("government", "government | clinician's own work"))
        os.utime(self.bar, (4126852920, 4126852920))  # later than the request
        assignment_bar.sign(self.run, request)
        self.assertFalse(assignment_bar.completion_gate(self.run)[0])

    def test_failed_signature_write_can_be_retried_without_losing_the_draft(self):
        self.draft(DOCX_BAR)
        original = self.bar.read_bytes()
        import bar_signatures
        replace = bar_signatures.os.replace
        def fail_record(source, destination):
            if Path(destination).name == assignment_bar.RECORD:
                raise OSError("record write failed")
            return replace(source, destination)
        with mock.patch.object(bar_signatures.os, "replace", side_effect=fail_record):
            with self.assertRaisesRegex(assignment_bar.UnreadableRecord, "could not be opened"):
                self.sign()
        self.assertEqual(original, self.bar.read_bytes())
        self.assertEqual([], list((self.run / "signed-bars").iterdir()))
        self.sign("I confirm the retry.", "2100-10-09T12:01:00Z")
        self.assertFalse(assignment_bar.completion_gate(self.run)[0])

    def test_malformed_copy_and_reply_fields_refuse_without_crashing(self):
        self.draft(DOCX_BAR)
        self.sign()
        path = self.run / assignment_bar.RECORD
        original = json.loads(path.read_text())
        for field, value in (("copy", None), ("copy", []), ("clinician_reply", None), ("reply_verification", [])):
            with self.subTest(field=field, value=value):
                payload = json.loads(json.dumps(original))
                payload["signatures"][-1][field] = value
                path.write_text(json.dumps(payload))
                with self.assertRaises(assignment_bar.UnreadableRecord):
                    assignment_bar.completion_gate(self.run)

    def test_absent_substring_blank_stale_and_reused_reply_refuse(self):
        self.draft(DOCX_BAR)
        self.messages.append({"type": "user", "timestamp": "2100-01-01T00:00:00Z",
                              "message": {"content": "I confirm, with conditions."}})
        self.messages.append({"type": "user", "timestamp": "1970-01-01T00:00:01Z",
                              "message": {"content": "Stale reply."}})
        for reply in ("I confirm", "", "Something else", "Stale reply."):
            with self.subTest(reply=reply), self.assertRaises(run_grader.SourceError):
                assignment_bar.sign(self.run, reply)
        self.sign()
        with self.assertRaises(run_grader.SourceError):
            assignment_bar.sign(self.run, "I confirm this bar.")
        self.assertEqual(1, len(json.loads((self.run / assignment_bar.RECORD).read_text())["signatures"]))

    def test_spacing_is_ignored_and_unreadable_is_recorded_not_verified(self):
        self.draft(DOCX_BAR)
        self.messages.append({"type": "user", "timestamp": "2100-01-01T00:00:00Z",
                              "message": {"content": "Yes,\n sign it."}})
        assignment_bar.sign(self.run, "Yes, sign it.")
        with mock.patch.object(approval_record, "_main_transcripts", return_value=([], True)):
            assignment_bar.sign(self.run, "New reply from unreadable transcript.")
        latest = json.loads((self.run / assignment_bar.RECORD).read_text())["signatures"][-1]
        self.assertEqual("not verified", latest["reply_verification"])
        self.assertIn("not verified", assignment_bar.completion_gate(self.run)[1])

    def test_changed_bar_refuses_both_submission_gates_and_click_authorization(self):
        self.draft(DOCX_BAR)
        self.sign()
        artifact = self.run / "paper.docx"
        artifact.write_bytes(b"synthetic artifact")
        write_none_context(self.run)
        with mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "clean")), \
             mock.patch.object(assignment_submission.reader_remarks, "verify", return_value=[]):
            staged = assignment_submission.stage(self.run, artifact, artifact_approved=True,
                                                  clinician_reply="I confirm this bar.")
            self.bar.write_bytes(self.bar.read_bytes() + b"Changed.\n")
            with self.assertRaisesRegex(assignment_submission.GateError, "show the changed lines"):
                assignment_submission.stage(self.run, artifact, artifact_approved=True,
                                             clinician_reply="I confirm this bar.")
            with self.assertRaisesRegex(assignment_submission.GateError, "show the changed lines"):
                assignment_submission.confirm(staged, uploaded_carriers=(artifact,), clinician_reply="Submit the synthetic assignment.")
            self.assertFalse(assignment_submission.upload_is_allowed(staged, artifact))
            self.assertFalse(assignment_submission.submit_is_authorized(staged))


if __name__ == "__main__":
    unittest.main()
