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
AGENTS = ROOT / "AGENTS.md"
README = ROOT / "README.md"
CASE_STUDY = ROOT / "skills" / "practicum-case-study" / "SKILL.md"
DISCUSSION_POST = ROOT / "skills" / "discussion-post" / "SKILL.md"


class TheCourseAssignmentWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.docx_branch = DOCX_BRANCH.read_text(encoding="utf-8")

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
        self.assertIn("Research produces claim records", self.skill)
        self.assertIn("refutation leg attacks the reference", self.skill)
        self.assertIn("attacks the rendered artifact for records that do not exist", self.skill)
        self.assertIn("keyed to slide number", self.skill)
        self.assertIn("value or sense differs from the claim heading", self.skill)
        self.assertIn("qualifier appears on the same slide face as its claim", self.skill)
        self.assertIn("speaker notes do not satisfy the qualifier", self.skill)
        self.assertIn("heading no longer matches the slide text it sources", self.skill)

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

    def test_the_live_submission_type_selects_one_carrier_before_the_gate(self):
        self.assertIn("SUBMISSION-TYPE: file-upload | canvas-composer", self.skill)
        self.assertIn("Branch on the signed `SUBMISSION-TYPE`", self.skill)
        self.assertIn("For `file-upload`, the carrier is the finished `.pptx`", self.skill)
        self.assertIn("For `canvas-composer`, write the exact deck-accompanying text", self.skill)
        self.assertIn("submission-readback.html", self.skill)
        self.assertIn("This is the existing submission gate", self.skill)
        self.assertIn("do not switch routes or retry the load", self.skill)

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
