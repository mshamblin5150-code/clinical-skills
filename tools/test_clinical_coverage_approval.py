"""Clinical pre-ask coverage, shared transcript snapshot and selector floor. #1845."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import aar_scan
import approval_record as approvals
import reader_remarks
from test_approval_record import NOTE


class ClinicalCoverageApproval(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run = Path(self.temporary.name)
        self.note = self.run / "note-1.md"
        self.note.write_text(NOTE, encoding="utf-8")
        os.utime(self.note, (1, 1))
        self.transcript = self.run / "session.jsonl"
        self.grade = "paired grade\nunread remainder 1\nrow 13: NOT RUN\n"
        self.grader = mock.patch.object(approvals, "_pre_post_grade", return_value=(2, self.grade)).start()
        self.addCleanup(mock.patch.stopall)
        self.discovery = mock.patch.object(aar_scan, "discover_transcripts", return_value=
            aar_scan.TranscriptDiscovery((self.transcript,), 1, 0, 0, 1)).start()
        self.skill = "clinical-note"

    def arguments(self):
        return dict(skill=self.skill, submission="synthetic-note", sources=(self.note,),
                    grader_args=(str(self.run),))

    def prepare(self):
        return approvals.prepare(self.run, **self.arguments())

    def approve(self):
        return approvals.approve(self.run, **self.arguments(), content_approved=True,
                                  clinician_reply="Approved.")

    def show(self, coverage, *, shown_at=None, reply_at=None, codex=False):
        import uptodate_block
        stamp = time.time() + 10
        shown_at = stamp if shown_at is None else shown_at
        reply_at = stamp + 1 if reply_at is None else reply_at
        def row(role, text, at):
            result = {"timestamp": datetime.fromtimestamp(at, timezone.utc).isoformat()}
            if codex:
                result.update(type="response_item", payload={"type": "message", "role": role,
                    "content": [{"type": "output_text" if role == "assistant" else "input_text", "text": text}]})
            else:
                result.update(type=role, message={"content": text})
            return result
        self.transcript.write_text("\n".join(json.dumps(r) for r in (
            row("assistant", uptodate_block.render(self.run, (self.note,)) + "\n" + coverage, shown_at),
            row("user", "Approved.", reply_at))) + "\n", encoding="utf-8")

    def item(self):
        return json.loads((self.run / approvals.RECORD).read_text(encoding="utf-8"))["items"][0]

    def test_both_clinical_skills_show_coverage_without_coursework_context_or_remarks(self):
        for skill in sorted(approvals.CLINICAL_SKILLS):
            for codex in (False, True):
                with self.subTest(skill=skill, codex=codex):
                    self.skill = skill
                    (self.run / approvals.RECORD).unlink(missing_ok=True)
                    with mock.patch.object(approvals.project_context, "go_ahead", side_effect=AssertionError("coursework only")):
                        prepared = self.prepare()
                        self.assertEqual((), prepared.remarks)
                        self.show("\n".join(prepared.coverage), codex=codex)
                        self.discovery.reset_mock()
                        self.approve()
                    self.discovery.assert_called_once_with(self.run.resolve())
                    self.assertEqual("incomplete", self.item()["pregrade_status"])
                    self.assertEqual("verified", self.item()["coverage_verification"])
                    self.assertEqual([], self.item()["reader_remarks"])
                    self.assertFalse(self.item()["project_context_check"])

    def test_readable_transcript_missing_or_changing_a_line_refuses(self):
        prepared = self.prepare()
        for coverage in ("", "unread remainder 1", "unread remainder 10\nrow 13: NOT RUN"):
            with self.subTest(coverage=coverage):
                self.show(coverage)
                with self.assertRaisesRegex(approvals.ApprovalRecordError, "coverage lines were not shown"):
                    self.approve()
                self.assertFalse((self.run / approvals.RECORD).exists())
        self.show("\n".join(prepared.coverage))
        self.approve()

    def test_missing_prepare_refuses_even_when_transcript_is_unreadable(self):
        for unread in (False, True):
            with self.subTest(unread=unread):
                self.show("\n".join(reader_remarks.coverage_lines(self.grade)))
                if unread:
                    self.transcript.unlink()
                with self.assertRaisesRegex(approvals.ApprovalRecordError, "pre-ask grade receipt"):
                    self.approve()

    def test_grade_change_refuses_even_when_coverage_lines_stay_the_same(self):
        prepared = self.prepare()
        self.show("\n".join(prepared.coverage))
        self.grader.return_value = (2, self.grade + "an additional checked row\n")
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "prepared grade or source changed"):
            self.approve()

    def test_grade_after_reply_or_lines_outside_prepare_reply_window_refuse(self):
        prepared = self.prepare()
        self.show("\n".join(prepared.coverage), shown_at=2, reply_at=3)
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "before the approval reply"):
            self.approve()
        self.show("\n".join(prepared.coverage), shown_at=2)
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "coverage lines were not shown"):
            self.approve()
        stamp = time.time() + 20
        self.show("\n".join(prepared.coverage), shown_at=stamp + 1, reply_at=stamp)
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "coverage lines were not shown"):
            self.approve()

    def test_source_change_requires_a_fresh_prepare(self):
        prepared = self.prepare()
        self.note.write_text(NOTE.replace("Subjective.", "Changed subjective."), encoding="utf-8")
        self.show("\n".join(prepared.coverage))
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "source changed"):
            self.approve()

    def test_unreadable_transcript_records_reason_and_never_a_clean_approval(self):
        self.grader.return_value = (0, "paired grade clean")
        self.prepare()
        self.approve()
        item = self.item()
        self.assertEqual("incomplete", item["pregrade_status"])
        self.assertEqual("unreadable", item["coverage_verification"])
        self.assertIn("transcript unreadable", item["coverage_reason"])
        self.assertIn(item["coverage_reason"], item["pregrade_report"])
        self.discovery.assert_called_once()

    def test_unreadable_transcript_does_not_waive_changed_grade(self):
        self.prepare()
        self.grader.return_value = (0, "changed grade")
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "prepared grade or source changed"):
            self.approve()

    def test_clean_shown_grade_can_record_clean(self):
        self.grader.return_value = (0, "paired grade clean\nunread remainder 0")
        prepared = self.prepare()
        self.show("\n".join(prepared.coverage))
        self.approve()
        self.assertEqual("clean", self.item()["pregrade_status"])

    def test_prepared_finding_and_submission_mode_refuse(self):
        self.grader.return_value = (1, "finding")
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "finding"):
            self.prepare()
        args = self.arguments()
        args["grader_args"] = (str(self.run), "--submission", "synthetic-note")
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "must not receive --submission"):
            approvals.prepare(self.run, **args)


class CoverageVocabulary(unittest.TestCase):
    def test_all_ruled_wordings_are_selected_with_spelling_and_case_variants(self):
        # Literal nonzero grader lines keep the undated fallback independent of
        # the shipped Rh(D) year, as ADR 0428 ruling 3 permits.
        lines = (
            "visit times: not checked - shift values missing",
            "Rh(D) citations: year not compared - the sheet states none: 1",
            "label contradictions: 1 counted, never-graded",
            "other contradictions: never graded",
            "row 13 floor was not run in one note",
            "row 13: NOT RUN",
            "the image answer: not verified - transcript unreadable",
            "unread remainder 0", "posting: NOT GRADED", "rows: not-graded",
            "body: not scanned", "incomplete coverage",
        )
        self.assertEqual(lines, reader_remarks.coverage_lines("\n".join((*lines, *lines))))

    def test_correct_set_asides_and_uptodate_block_are_outside_the_selector(self):
        lines = ("run records set aside: 2", "UPTODATE CONFLICTS: none",
                 "UPTODATE FAILED PULLS: none", "UPTODATE MISMATCHED SEARCHES: none",
                 reader_remarks.report((reader_remarks.Remark("reader", "not checked"),)))
        self.assertEqual((), reader_remarks.coverage_lines("\n".join(lines)))


if __name__ == "__main__":
    unittest.main()
