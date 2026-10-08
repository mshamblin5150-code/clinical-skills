"""Public-contract tests for durable approval records. #1421."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import approval_record


NOTE = (
    "S:\nSubjective.\nO:\nObjective.\nA:\nAssessment.\nP:\n"
    "Non-pharmacologic:\nPharmacologic:\nHealth Promotion/Patient Education:\n"
    "Referral/Follow-up:\nCoding worksheet\n"
)


class ApprovalRecordContract(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run = self.root / "scratch" / "runs" / "nur-5042-module-5-discussion"
        self.run.mkdir(parents=True)
        self.artifact = self.root / "post.md"
        self.artifact.write_text("approved post\n", encoding="utf-8")
        self.preflight = mock.patch.object(
            approval_record, "_preflight_grader", return_value=None
        )
        self.preflight.start()
        self.addCleanup(self.preflight.stop)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_invalid_grader_invocation_cannot_be_accepted_as_incomplete(self) -> None:
        self.preflight.stop()
        with self.assertRaisesRegex(
            approval_record.ApprovalRecordError, "invocation is invalid"
        ):
            approval_record._preflight_grader("discussion-post", ())
        self.preflight.start()

    def test_content_go_ahead_records_the_skill_submission_and_source_population(self) -> None:
        completed = subprocess.CompletedProcess([], 0, "pre-post grade: clean\n", "")
        with mock.patch.object(approval_record.subprocess, "run", return_value=completed):
            approved = approval_record.approve(
                self.run,
                skill="discussion-post",
                submission="nur-5042-module-5-discussion-2026-09-26",
                sources=(self.artifact,),
                grader_args=(str(self.run), "--draft", str(self.artifact)),
                content_approved=True,
            )

        record = json.loads(
            (self.run / approval_record.RECORD).read_text(encoding="utf-8")
        )
        self.assertEqual("discussion-post", approved.skill)
        self.assertEqual(approved.sha256, record["items"][0]["sha256"])
        self.assertEqual(
            "nur-5042-module-5-discussion-2026-09-26",
            record["items"][0]["submission"],
        )
        self.assertEqual([str(self.artifact.resolve())], record["items"][0]["sources"])

    def test_a_pre_post_finding_refuses_without_writing_an_approval(self) -> None:
        completed = subprocess.CompletedProcess([], 1, "", "word-floor: 1\n")
        with mock.patch.object(approval_record.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(approval_record.ApprovalRecordError, "finding"):
                approval_record.approve(
                    self.run,
                    skill="discussion-post",
                    submission="post-key",
                    sources=(self.artifact,),
                    grader_args=(str(self.run), "--draft", str(self.artifact)),
                    content_approved=True,
                )

        self.assertFalse((self.run / approval_record.RECORD).exists())

    def test_a_recorded_clinician_posting_grades_clean_through_its_posted_reading(self) -> None:
        completed = subprocess.CompletedProcess([], 0, "pre-post grade: clean\n", "")
        with mock.patch.object(approval_record.subprocess, "run", return_value=completed):
            approval = approval_record.approve(
                self.run,
                skill="discussion-post",
                submission="post-key",
                sources=(self.artifact,),
                grader_args=(str(self.run), "--draft", str(self.artifact)),
                content_approved=True,
            )
        approval_record.record_clinician_posting(
            self.run, skill="discussion-post", submission="post-key"
        )
        (self.run / "reread.md").write_text(
            "## REREAD: post-key\n"
            "POST-URL: https://example.test/posts/1\n"
            "POSTED: 2026-09-26 10:00\n"
            "READ: 2026-09-26\n"
            f"SUBMISSION-SHA256: {approval.sha256}\n"
            "VERDICT: matches - stored body matches the approved source\n",
            encoding="utf-8",
        )

        failed, report = approval_record.completion_gate(
            self.run, "discussion-post", "post-key"
        )

        self.assertFalse(failed, report)
        self.assertIn("clean", report)

    def test_incomplete_pre_post_coverage_is_recorded_and_does_not_block(self) -> None:
        self.artifact.write_text(NOTE, encoding="utf-8")
        completed = subprocess.CompletedProcess([], 2, "unread remainder 1\n", "")
        with mock.patch.object(approval_record.subprocess, "run", return_value=completed):
            approved = approval_record.approve(
                self.run,
                skill="clinical-note",
                submission="encounter-key-2026-09-26",
                sources=(self.artifact,),
                grader_args=(str(self.run),),
                content_approved=True,
            )

        record = json.loads(
            (self.run / approval_record.RECORD).read_text(encoding="utf-8")
        )
        self.assertIn("unread remainder", approved.pregrade_report)
        self.assertEqual("incomplete", record["items"][0]["pregrade_status"])

    def test_note_approval_checks_every_source_before_recording(self) -> None:
        for skill in ("batch-shift", "clinical-note"):
            with self.subTest(skill=skill):
                record = self.run / approval_record.RECORD
                record.unlink(missing_ok=True)
                self.artifact.write_text(NOTE, encoding="utf-8")
                other = self.root / "other.md"
                other.write_text(NOTE.replace("Assessment.", "Confirm medication before entry."), encoding="utf-8")
                with mock.patch.object(approval_record, "_pre_post_grade", return_value=(0, "clean")):
                    with self.assertRaises(approval_record.ApprovalRecordError) as refused:
                        approval_record.approve(
                            self.run, skill=skill, submission="note-key",
                            sources=(self.artifact, other), grader_args=(str(self.run),),
                            content_approved=True,
                        )
                    self.assertIn(str(other.resolve()), str(refused.exception))
                    self.assertIn("before entry", str(refused.exception))
                    self.assertFalse(record.exists())
                    other.write_text(NOTE, encoding="utf-8")
                    approval_record.approve(
                        self.run, skill=skill, submission="note-key",
                        sources=(self.artifact, other), grader_args=(str(self.run),),
                        content_approved=True,
                    )
                self.assertTrue(record.exists())
                self.assertFalse((self.root / "entry-copies").exists())

    def test_coursework_approval_does_not_check_note_grammar(self) -> None:
        self.artifact.write_text("Confirm medication before entry.\n", encoding="utf-8")
        with mock.patch.object(approval_record, "_pre_post_grade", return_value=(0, "clean")):
            approval_record.approve(
                self.run, skill="discussion-post", submission="post-key",
                sources=(self.artifact,), grader_args=(str(self.run),),
                content_approved=True,
            )
        self.assertTrue((self.run / approval_record.RECORD).exists())

    def test_approval_and_posted_reading_fingerprint_mismatch_is_a_finding(self) -> None:
        completed = subprocess.CompletedProcess([], 0, "clean\n", "")
        with mock.patch.object(approval_record.subprocess, "run", return_value=completed):
            approval_record.approve(
                self.run,
                skill="peer-critique",
                submission="critique.md",
                sources=(self.artifact,),
                grader_args=(str(self.run),),
                content_approved=True,
            )
        approval_record.record_agent_posting(
            self.run, skill="peer-critique", submission="critique.md"
        )
        (self.run / "reread.md").write_text(
            "## REREAD: critique.md\n"
            "POST-URL: https://example.test/review/1\n"
            "POSTED: 2026-09-26 10:00\n"
            "READ: 2026-09-26\n"
            f"SUBMISSION-SHA256: {'f' * 64}\n"
            "VERDICT: matches - stored comment matches\n",
            encoding="utf-8",
        )

        failed, report = approval_record.completion_gate(
            self.run, "peer-critique", "critique.md"
        )

        self.assertTrue(failed)
        self.assertIn("SUBMISSION-SHA256 is missing, malformed, or stale", report)

    def test_clinician_posting_without_approval_is_refused(self) -> None:
        with self.assertRaisesRegex(approval_record.ApprovalRecordError, "approval"):
            approval_record.record_clinician_posting(
                self.run, skill="batch-shift", submission="shift-2026-09-26"
            )


if __name__ == "__main__":
    unittest.main()
