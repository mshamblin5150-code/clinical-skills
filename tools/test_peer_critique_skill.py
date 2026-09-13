"""Contract tests binding the peer-critique skill to its grader and indexes."""

from __future__ import annotations

import json
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
CANVAS_EDITOR = ROOT / "skills" / "_shared" / "reference" / "canvas-editor.md"
CANVAS_CALIBRATION = (
    ROOT / "skills" / "_shared" / "reference" / "canvas-editor-calibration.json"
)
CLAUDE = ROOT / "CLAUDE.md"
CONTEXT = ROOT / "CONTEXT.md"


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


class ThePeerCritiqueUsesTheRuledSurface(ProseBind, unittest.TestCase):
    def test_the_reply_and_critique_are_separate_artifacts_on_separate_surfaces(self):
        skill = read(SKILL)
        self.assertProseIn("The Reply goes on the board", skill)
        self.assertProseIn("The Peer critique goes in the peer-review comment", skill)
        self.assertProseIn("the critique is not also posted to the board", skill)
        self.assertProseIn("The Reply to the same classmate is a separate artifact, not a substitute", skill)

    def test_the_run_retains_plain_text_and_stored_comment_readback(self):
        skill = read(SKILL)
        self.assertIn("critique.txt", skill)
        self.assertIn("critique-stored-comment-readback.txt", skill)
        self.assertNotIn("critique.html", skill)
        self.assertNotIn("critique-<surface>-readback.html", skill)

    def test_the_comment_receives_literal_plain_text_not_composer_html(self):
        skill = read(SKILL)
        self.assertProseIn("plain text built from critique.md", skill)
        self.assertProseIn("every character literal", skill)
        self.assertProseIn("plain text names the transport", skill)
        self.assertProseIn("retain the bold heading markers", skill)
        self.assertProseIn("The peer-review comment is not a Composer", skill)

    def test_the_posted_reading_uses_stored_text_and_accepts_the_legacy_display(self):
        skill = read(SKILL)
        self.assertProseIn("compares Canvas's stored comment text", skill)
        self.assertProseIn("at minimum the ampersand count", skill)
        self.assertProseIn("expected display behavior", skill)
        self.assertProseIn("it is not filed", skill)
        self.assertProseIn("POST-URL names the reviewed submission's page", skill)
        self.assertIn("LEGACY-DISPLAY:", skill)

    def test_a_course_without_a_peer_review_still_asks_the_clinician(self):
        self.assertProseIn("Where a course assigns no peer review", read(SKILL))


class TheAmpersandBoundaryMatchesTheRuling(ProseBind, unittest.TestCase):
    def test_the_scanner_names_the_stored_text_as_gradable(self):
        subjects = {subject: reason for subject, reason in peer_critique_scan.NOT_REACHED}
        reason = subjects["the legacy peer-review page's display of a stored ampersand"]
        self.assertIn("stored comment text", reason)
        self.assertIn("accepted", reason)

    def test_the_maintainer_guide_narrows_the_display_defect_to_one_page(self):
        guide = read(CLAUDE)
        self.assertProseIn("stored comment text is compared with the source", guide)
        self.assertProseIn("The 2026-09-12 Bluefield observation found", guide)

    def test_posted_reading_includes_the_peer_review_comment_surface(self):
        glossary = read(CONTEXT)
        self.assertProseIn("a Peer-review comment", glossary)
        self.assertProseIn("the reviewed submission's page the locator", glossary)

    def test_the_canvas_sheet_names_the_peer_review_comment_as_a_non_composer(self):
        sheet = read(CANVAS_EDITOR)
        self.assertProseIn("classifies the peer-review comment as a non-Composer surface", sheet)
        self.assertProseIn("2026-09-12 Bluefield observation", sheet)

    def test_the_calibration_retains_the_four_instrument_observation(self):
        records = json.loads(read(CANVAS_CALIBRATION))
        record = next(
            row for row in records if row.get("surface") == "peer-review comment"
        )
        self.assertEqual("2026-09-12", record["measured_on"])
        instruments = record["ampersand_observation"]
        self.assertEqual(3, instruments["stored_comment_text"]["real_ampersands"])
        self.assertEqual(3, instruments["formatted_html"]["single_escaped_ampersands"])
        self.assertEqual(3, instruments["legacy_page_server_html"]["double_escaped_ampersands"])
        self.assertEqual(3, instruments["legacy_page_rendered_text"]["visible_entities"])


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
