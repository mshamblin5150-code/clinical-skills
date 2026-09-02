"""Contract tests for ticket #821's course-assignment workflow."""

from __future__ import annotations

import unittest
from pathlib import Path

import deck_scan


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "course-assignment" / "SKILL.md"
AGENTS = ROOT / "AGENTS.md"
README = ROOT / "README.md"
CASE_STUDY = ROOT / "skills" / "practicum-case-study" / "SKILL.md"
DISCUSSION_POST = ROOT / "skills" / "discussion-post" / "SKILL.md"


class TheCourseAssignmentWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")

    def test_the_skill_is_indexed_and_accepts_only_a_deck(self):
        self.assertIn("| course-assignment |", AGENTS.read_text(encoding="utf-8"))
        self.assertIn("course-assignment", README.read_text(encoding="utf-8"))
        self.assertIn("ARTIFACT: deck", self.skill)
        self.assertIn("deck is the only accepted value", self.skill)
        self.assertNotIn("ARTIFACT: paper", self.skill)

    def test_the_signed_bar_names_every_required_field(self):
        for field in deck_scan.REQUIRED_BAR_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field + ":", self.skill)
        self.assertIn("show `bar.md` to the clinician", self.skill)
        self.assertIn("explicit confirmation", self.skill)

    def test_research_refutation_and_adversarial_reads_have_distinct_subjects(self):
        self.assertIn("Research produces claim records", self.skill)
        self.assertIn("Refutation attacks each record that exists", self.skill)
        self.assertIn("adversarial pass attacks the rendered artifact for records that do not exist", self.skill)
        self.assertIn("keyed to slide number", self.skill)

    def test_the_population_split_and_every_grader_row_are_written_out(self):
        self.assertIn("slide face alone", self.skill)
        self.assertIn("slide face and speaker notes", self.skill)
        for row in deck_scan.ROWS:
            with self.subTest(row=row):
                self.assertIn(f"`{row}`", self.skill)

    def test_the_commands_and_render_retention_are_explicit(self):
        for command in ("research_ledger.py", "deck_scan.py", "deck_render.py", "render_scan.py"):
            self.assertIn(command, self.skill)
        self.assertIn("one page-faithful PDF", self.skill)
        self.assertIn("one 120-dpi PNG per slide", self.skill)
        self.assertIn("only the last pass", self.skill)
        self.assertIn("clinician-supplied PDF", self.skill)
        self.assertIn("explicit go-ahead", self.skill)

    def test_declared_limits_are_pointed_to_without_a_second_copy(self):
        self.assertIn("deck_scan.DECLARED_LIMITS", self.skill)
        for limit in deck_scan.DECLARED_LIMITS:
            with self.subTest(limit=limit.key):
                self.assertIn(f"`{limit.key}`", self.skill)
                self.assertNotIn(limit.limit, self.skill)


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
