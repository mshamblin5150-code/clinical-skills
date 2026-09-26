"""Contract tests for ticket #821's course-assignment workflow."""

from __future__ import annotations

import unittest
from pathlib import Path

import deck_scan
import assignment_docx_scan
from prose_bind import NAMING, bind


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "course-assignment" / "SKILL.md"
DOCX_BRANCH = ROOT / "skills" / "course-assignment" / "references" / "docx.md"
RUN_STATUS = ROOT / "skills" / "course-assignment" / "references" / "run-status.md"
AGENTS = ROOT / "AGENTS.md"
README = ROOT / "README.md"
CASE_STUDY = ROOT / "skills" / "practicum-case-study" / "SKILL.md"
DISCUSSION_POST = ROOT / "skills" / "discussion-post" / "SKILL.md"


class TheCourseAssignmentWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.docx_branch = DOCX_BRANCH.read_text(encoding="utf-8")
        cls.run_status = RUN_STATUS.read_text(encoding="utf-8")

    def test_the_skill_is_indexed_and_dispatches_only_signed_deck_or_docx_artifacts(self):
        self.assertIn("| course-assignment |", AGENTS.read_text(encoding="utf-8"))
        self.assertIn("course-assignment", README.read_text(encoding="utf-8"))
        self.assertIn("ARTIFACT: deck", self.skill)
        self.assertIn("ARTIFACT: docx", self.skill)
        self.assertIn("references/docx.md", self.skill)
        self.assertNotIn("ARTIFACT: paper", self.skill)

    def test_the_signed_bar_names_every_required_field(self):
        for field in deck_scan.REQUIRED_BAR_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field + ":", self.skill)
        self.assertIn("show `bar.md` to the clinician", self.skill)
        self.assertIn("explicit confirmation", self.skill)

    def test_research_refutation_and_adversarial_reads_have_distinct_subjects(self):
        skill = " ".join(self.skill.split())
        self.assertIn("Research produces claim records", self.skill)
        self.assertIn("refutation leg attacks the reference", self.skill)
        self.assertIn("attacks the rendered artifact for records that do not exist", skill)
        self.assertIn("keyed to slide number", skill)
        self.assertIn("value or sense differs from the claim heading", skill)
        self.assertIn("qualifier appears on the same slide face as its claim", skill)
        self.assertIn("speaker notes do not satisfy the qualifier", skill)
        self.assertIn("heading no longer matches the slide text it sources", skill)

    def test_the_population_split_and_every_grader_row_are_written_out(self):
        self.assertIn("slide face alone", self.skill)
        self.assertIn("slide face and speaker notes", self.skill)
        for row in deck_scan.ROWS:
            with self.subTest(row=row):
                self.assertIn(f"`{row}`", self.skill)
        self.assertIn("appears in no believed claim-record heading", self.skill)

    def test_the_commands_and_render_retention_are_explicit(self):
        for command in (
            "research_ledger.py",
            "deck_scan.py",
            "deck_render.py",
            "render_scan.py",
            "post_html.py",
        ):
            self.assertIn(command, self.skill)
        self.assertIn("one page-faithful PDF", self.skill)
        self.assertIn("one 120-dpi PNG per slide", self.skill)
        self.assertIn("only the last pass", self.skill)
        self.assertIn("clinician-supplied PDF", self.skill)
        self.assertIn("explicit go-ahead", self.skill)

    def test_adversarial_read_follows_the_retained_render_and_names_its_inputs(self):
        production = self.skill.split("## 3. Produce the deck", 1)[1].split("## 4.", 1)[0]
        inspection = " ".join(self.skill.split("## 5. Render and inspect every slide", 1)[1].split("## 6.", 1)[0].split())
        self.assertNotIn("The adversarial investor reader", production)
        ordered = (
            "python tools/deck_render.py",
            "python tools/render_scan.py",
            "This vision-capable **Second reader**",
            "The adversarial investor reader",
            "this fresh **Second reader**",
            "Rerun `deck_scan.py --pptx <deck>`",
        )
        positions = [inspection.index(item) for item in ordered]
        self.assertEqual(positions, sorted(positions))
        for phrase in (
            "highest retained",
            "final speaker-note text",
            "file_digest.sha256",
            "CLAIMS: <SHA-256 of claims.md when the reader was briefed>",
            "PASS: <positive retained pass number>",
            "SLIDES: <read PNG count> of <deck slide count> read",
            "UNSEEN: none | <what was not read>",
            "VERDICT: clean - <reason> | defect - <reason>",
            "`claims.md`-only repair",
        ):
            self.assertIn(phrase, inspection)

    def test_the_final_deck_gets_a_fingerprinted_presentation_intent_read(self):
        inspection = " ".join(
            self.skill.split("## 5. Render and inspect every slide", 1)[1]
            .split("## 6.", 1)[0]
            .split()
        )
        for phrase in (
            "SLIDE-LIMIT-SCOPE: all | content",
            "AUDIENCE-PURPOSE: <the assignment's audience-facing purpose>",
            "TALK-STYLE: <the clinician-confirmed presentation style>",
            "## PRESENTATION-INTENT: <course>-<module>-course-assignment-<date>.pptx",
            "DRAFT: <SHA-256 of the output .pptx>",
            "CONTENT-SLIDES: <comma-separated slide numbers> | none",
            "REFERENCE-SLIDES: <comma-separated slide numbers> | none",
            "INTERNAL-COMMENTARY: none | found - <slide and commentary>",
            "SPOKEN-ARC: follows - <reason> | departs - <reason>",
            "intent.md",
            "partition every deck slide exactly once",
        ):
            self.assertIn(phrase, self.skill)
        self.assertLess(
            inspection.index("This vision-capable **Second reader**"),
            inspection.index("## PRESENTATION-INTENT:"),
        )
        self.assertLess(
            inspection.index("## PRESENTATION-INTENT:"),
            inspection.index("The adversarial investor reader"),
        )

    def test_the_live_submission_type_selects_one_carrier_before_the_gate(self):
        self.assertIn("SUBMISSION-TYPE: file-upload | canvas-composer", self.skill)
        self.assertIn("Branch on the signed `SUBMISSION-TYPE`", self.skill)
        self.assertIn("For `file-upload`, the carrier is the finished `.pptx`", self.skill)
        self.assertIn("For `canvas-composer`, write the exact deck-accompanying text", self.skill)
        self.assertIn("submission-readback.html", self.skill)
        self.assertIn("This is the existing submission gate", self.skill)
        self.assertIn("do not switch routes or retry the load", self.skill)

    def test_submission_approval_binds_the_filename_population(self):
        for surface in (self.skill, self.docx_branch):
            with self.subTest(surface=surface[:30]):
                self.assertIn("ATTACHMENT-COUNT:", surface)
                self.assertIn("FILENAME:", surface)
                self.assertIn("SUBMITTED-FILE:", surface)
                self.assertIn("assignment_submission.upload_is_allowed", surface)
        self.assertIn("excluded by default", " ".join(self.skill.split()))

    def test_both_branches_carry_the_clinician_upload_and_run_status_contract(self):
        for surface in (self.skill, self.docx_branch):
            with self.subTest(surface=surface[:30]):
                self.assertIn("assignment_submission.record_clinician_upload", surface)
                self.assertIn("run-status.md", surface)
                self.assertIn("Run status:", surface)
                self.assertIn("run directory", surface)
        for line in (
            "Run status: awaiting upload",
            "Run status: awaiting posted reading",
            "Run status: awaiting AAR",
            "Run status: stopped - <reason>",
            "Run status: complete",
        ):
            self.assertIn(line, self.run_status)

    def test_approval_requires_the_run_directory_pre_upload_grade(self):
        for surface in (self.skill, self.docx_branch):
            with self.subTest(surface=surface[:30]):
                self.assertIn("pre-upload grade", surface)
                self.assertIn("before approval", surface)

    def test_completion_binds_and_links_the_canonical_finished_artifact(self):
        normalized = " ".join(self.skill.split())
        self.assertIn("`repo_root.output_root()`", self.skill)
        self.assertIn("canonical copy", normalized)
        self.assertIn("raw-byte SHA-256", normalized)
        self.assertIn("Markdown link", normalized)
        self.assertIn("never the worktree copy", normalized)

    def test_declared_limits_are_pointed_to_without_a_second_copy(self):
        self.assertEqual(1, self.skill.count("deck_scan.DECLARED_LIMITS"))
        for limit in deck_scan.DECLARED_LIMITS:
            with self.subTest(limit=limit.key):
                self.assertNotIn(f"`{limit.key}`", self.skill)
        limits = tuple(limit.limit for limit in deck_scan.DECLARED_LIMITS)
        self.assertEqual((), bind(limits, self.skill, mode=NAMING))

    def test_the_docx_branch_writes_out_its_bar_grader_render_and_two_gates(self):
        for field in assignment_docx_scan.REQUIRED_BAR_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field + ":", self.docx_branch)
        for row in assignment_docx_scan.ROWS:
            with self.subTest(row=row):
                self.assertIn(f"`{row}`", self.docx_branch)
        for limit in assignment_docx_scan.DECLARED_LIMITS:
            with self.subTest(limit=limit.key):
                self.assertIn(f"`{limit.key}`", self.docx_branch)
        self.assertEqual(
            (),
            bind(
                tuple(limit.limit for limit in assignment_docx_scan.DECLARED_LIMITS),
                self.docx_branch,
                mode=NAMING,
            ),
        )
        for command in (
            "assignment_docx.py",
            "assignment_docx_scan.py",
            "assignment_docx_render.py",
            "render_scan.py",
            "course_assignment_scan.py",
        ):
            self.assertIn(command, self.docx_branch)
        self.assertIn("Gate 1", self.docx_branch)
        self.assertIn("Gate 2", self.docx_branch)
        self.assertIn("assignment_submission.stage", self.docx_branch)
        self.assertIn("assignment_submission.submit_is_authorized", self.docx_branch)
        self.assertIn("Submit Assignment", self.docx_branch)
        self.assertIn("assignment-docx.sha256", self.docx_branch)
        self.assertIn("the after-action review: clean", self.docx_branch)


class ExistingLedgerConsumersSignTheirPolicy(unittest.TestCase):
    def test_the_clinical_case_study_signs_the_original_policy(self):
        text = CASE_STUDY.read_text(encoding="utf-8")
        self.assertIn(
            "SOURCE-CLASSES: society guideline | peer-reviewed | government | tertiary reference",
            text,
        )
        self.assertIn("RECENCY-WINDOW-YEARS: 5", text)

    def test_the_initial_post_signs_the_original_policy(self):
        text = DISCUSSION_POST.read_text(encoding="utf-8")
        self.assertIn(
            "SOURCE-CLASSES: society guideline | peer-reviewed | government | tertiary reference",
            text,
        )
        self.assertIn("RECENCY-WINDOW-YEARS: 5", text)


if __name__ == "__main__":
    unittest.main()
