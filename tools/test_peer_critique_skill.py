"""Contract tests binding the peer-critique skill to its grader and indexes."""

from __future__ import annotations

import unittest
from pathlib import Path

import aar_scan
import peer_critique_scan
from prose_bind import NAMING, ProseBind, bind


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "peer-critique" / "SKILL.md"
RUBRIC = ROOT / "skills" / "_shared" / "reference" / "rubric.md"
AGENTS = ROOT / "AGENTS.md"
README = ROOT / "README.md"
REPLY = ROOT / "skills" / "discussion-reply" / "SKILL.md"
CASE_STUDY = ROOT / "skills" / "practicum-case-study" / "SKILL.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TheSkillIsIndexed(unittest.TestCase):
    def test_the_skill_is_in_both_indexes(self):
        self.assertIn("| peer-critique |", read(AGENTS))
        self.assertIn("`peer-critique`", read(README))

    def test_the_skill_declares_enough_numbered_steps(self):
        headings = [line for line in read(SKILL).splitlines() if line.startswith("## ")]
        numbered = [line for line in headings if line[3:4].isdigit()]
        self.assertGreaterEqual(len(numbered), 3)


class EveryGraderRowIsWrittenOut(ProseBind, unittest.TestCase):
    """A consumer with no Python walks the same checks the command runs."""

    def test_every_row_key_appears_backticked(self):
        skill = read(SKILL)
        for row in peer_critique_scan.ROWS:
            with self.subTest(row=row):
                self.assertIn(f"`{row}`", skill)

    def test_the_skill_points_at_the_limit_inventory_without_copying_it(self):
        skill = read(SKILL)
        self.assertIn("peer_critique_scan.NOT_REACHED", skill)
        self.assertEqual((), bind(peer_critique_scan.NOT_REACHED, skill, mode=NAMING))


class TheNumericBarsAreBoundToTheGrader(ProseBind, unittest.TestCase):
    def test_the_word_floor_is_the_scanner_constant(self):
        self.assertProseIn(
            f"a floor of {peer_critique_scan.WORD_FLOOR_COUNT}", read(SKILL)
        )

    def test_the_reported_ceiling_is_the_scanner_constant(self):
        self.assertProseIn(
            f"The {peer_critique_scan.WORD_CEILING_COUNT}-word expectation", read(SKILL)
        )

    def test_the_reference_floor_is_the_scanner_constant(self):
        self.assertIn(
            f"at least {peer_critique_scan.REFERENCE_FLOOR_COUNT} references", read(SKILL)
        )


class TheEightHeadingsAgreeWithTheSheet(unittest.TestCase):
    """The grader, the skill and the distilled spec name one set of headings."""

    def test_the_rubric_sheet_names_every_required_heading(self):
        rubric = read(RUBRIC)
        for heading in peer_critique_scan.REQUIRED_HEADINGS:
            with self.subTest(heading=heading):
                self.assertIn(heading, rubric)

    def test_the_sheet_points_at_the_skill_that_owns_the_deliverable(self):
        self.assertIn("../../peer-critique/SKILL.md", read(RUBRIC))


class TheClinicalRulingsSurviveInProse(ProseBind, unittest.TestCase):
    """The two rulings that cost the most to learn are load-bearing here."""

    def test_only_what_the_case_supplied_is_in_scope(self):
        self.assertProseIn("Only what the case supplied is in scope.", read(SKILL))

    def test_an_argued_off_entry_is_a_decision_and_an_absent_one_is_the_failure(self):
        skill = read(SKILL)
        self.assertProseIn("An entry named and then argued away by the tests is correct practice", skill)
        self.assertProseIn("An entry never made is the failure.", skill)

    def test_the_classmates_own_source_is_read_rather_than_replaced(self):
        self.assertProseIn("read the guideline they cited", read(SKILL))


class ThePostingGateIsStated(ProseBind, unittest.TestCase):
    def test_posting_needs_an_explicit_go_ahead(self):
        self.assertProseIn("Only an explicit go-ahead authorizes posting.", read(SKILL))

    def test_the_lms_is_not_edited_after_posting(self):
        self.assertProseIn(
            "Nothing on the LMS is edited after it is posted.", read(SKILL)
        )

    def test_the_ampersand_defect_is_named_with_its_ticket(self):
        self.assertIn("issues/991", read(SKILL))


class TheSiblingsRouteToThisSkill(ProseBind, unittest.TestCase):
    """Both skills that exclude the deliverable now name the one that owns it."""

    def test_the_case_study_points_here(self):
        self.assertIn("peer-critique", read(CASE_STUDY))

    def test_the_reply_skill_points_here(self):
        self.assertIn("peer-critique", read(REPLY))


class TheAfterActionReviewIsWired(unittest.TestCase):
    def test_the_skill_is_scoped_for_the_review(self):
        self.assertIn("peer-critique", aar_scan.SCOPED_SKILLS)

    def test_the_skill_invokes_the_review_and_names_its_clean_row(self):
        skill = read(SKILL)
        self.assertIn("`/AAR`", skill)
        self.assertIn(f"{aar_scan.EXPECTED_ROW}: clean", skill)

    def test_the_grader_declares_the_expected_completion_check(self):
        self.assertEqual(
            (aar_scan.EXPECTED_ROW,), peer_critique_scan.EXPECTED_COMPLETION_CHECKS
        )


if __name__ == "__main__":
    unittest.main()
