"""Contract tests for ticket #416's initial-post workflow."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POST = ROOT / "skills" / "discussion-post" / "SKILL.md"
REPLY = ROOT / "skills" / "discussion-reply" / "SKILL.md"
CASE_STUDY = ROOT / "skills" / "practicum-case-study" / "SKILL.md"
AGENTS = ROOT / "AGENTS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TheInitialPostHasOneRoutingSurface(unittest.TestCase):
    def test_the_skill_and_index_exist_and_route_worked_cases_away(self):
        post = read(POST)
        rows = [line for line in read(AGENTS).splitlines() if line.startswith("| discussion-post ")]

        self.assertEqual(1, len(rows))
        self.assertIn("initial post", rows[0])
        self.assertIn("practicum-case-study", post)
        self.assertRegex(post, r"(?i)worked clinical case.*not the skill")

    def test_practicum_frontmatter_no_longer_claims_generic_board_posts(self):
        description = read(CASE_STUDY).split("---", 2)[1]
        self.assertNotIn("discussion board", description)

    def test_practicum_scopes_every_run_artifact_to_the_derived_directory(self):
        case_study = read(CASE_STUDY)

        self.assertIn("scratch/runs/<course>-<module>-case-study/", case_study)
        self.assertIn("<run-directory>/claims.md", case_study)
        self.assertIn("<run-directory>/checks.md", case_study)
        self.assertNotIn("scratch/claims.md", case_study)
        self.assertNotIn("scratch/checks.md", case_study)
        self.assertIn("<run-directory>/evidence.txt", case_study)
        self.assertIn("<run-directory>/proposed-<date>.md", case_study)
        self.assertGreater(case_study.count("<claims-ledger>"), 6)
        self.assertGreater(case_study.count("<checks-ledger>"), 3)
        self.assertRegex(case_study, r"(?is)every signed bar element.*finished draft")

    def test_worked_case_routing_precedes_patient_bearing_board_reads(self):
        post = read(POST)
        route = re.search(
            r"If the prompt asks for a\s+worked clinical case, stop",
            post,
        )
        classmate_read = post.index("every classmate initial post")

        self.assertIsNotNone(route)
        self.assertLess(route.start(), classmate_read)
        case_study = read(CASE_STUDY)
        self.assertIn("case-study run directory", case_study)
        self.assertIn("board-<date>.md", case_study)
        self.assertIn("bar.md", case_study)
        self.assertIn("does not see the classmate posts", case_study)
        self.assertRegex(case_study, r"(?is)after the draft exists.*differentiation\.md")

    def test_setup_names_the_initial_post_as_a_voice_model_consumer(self):
        setup = read(ROOT / "skills" / "setup-clinical-skills" / "SKILL.md")

        self.assertIn("[discussion-post](../discussion-post/SKILL.md)", setup)


class OneBoardOwnsOneRun(unittest.TestCase):
    def test_both_discussion_skills_use_the_board_key_and_versioned_snapshot(self):
        for path in (POST, REPLY):
            with self.subTest(skill=path.parent.name):
                text = read(path)
                self.assertIn("scratch/runs/<course>-<module>-discussion/", text)
                self.assertIn("board-<date>.md", text)
                self.assertNotIn("<course>-<module>-<date>", text)


class TheWorkflowCarriesEveryRatifiedGate(unittest.TestCase):
    def test_the_skill_names_the_signed_bar_and_all_three_graders(self):
        post = read(POST)

        for needle in (
            "bar.md",
            "sign",
            "research_ledger.py",
            "reference_scan.py",
            "discussion_post_scan.py",
            "output/discussions/<course>-<module>-discussion-<date>.md",
            "docx_write.py",
            "explicit go-ahead",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, post)

    def test_step_seven_renders_one_bold_heading_document_and_grades_it(self):
        post = read(POST)
        self.assertRegex(post, r"docx_write\.py[^\n]+--bold-headings")
        self.assertRegex(post, r"discussion_post_scan\.py[^\n]+--docx")
        self.assertNotRegex(post, r"(?i)manually demote|heading demotion")
        self.assertNotRegex(post, r"carries the hanging indent.*heading structure")

    def test_the_post_claim_set_is_derived_from_citations_and_body_numbers(self):
        post = read(POST)

        self.assertRegex(post, r"(?is)every in-text citation.*every (?:Arabic )?numeral")
        self.assertIn("citation year", post)
        self.assertIn("page locator", post)
        self.assertRegex(post, r"statute section\s+number")

    def test_dead_claim_dispositions_are_explicit(self):
        post = read(POST)

        self.assertRegex(post, r"(?is)refuted.*sentence is cut")
        self.assertRegex(post, r"(?is)unsourced.*own.*reasoning")
        self.assertRegex(post, r"(?is)paywalled.*counted")

    def test_the_drafter_is_blind_to_classmate_posts_until_differentiation(self):
        post = read(POST)

        self.assertIn("does not see the classmate posts", post)
        self.assertIn("differentiation", post)


class TheCanvasPasteMeasurement(unittest.TestCase):
    RECORD = ROOT / "skills" / "discussion-post" / "reference" / "canvas-paste-calibration.json"

    def test_scope_is_carried_in_schema_fields_and_the_observation_is_recorded(self):
        record = json.loads(read(self.RECORD))
        for field in ("measured_on", "institution", "course", "theme", "instrument"):
            with self.subTest(field=field):
                self.assertTrue(record[field])
        self.assertEqual(record["measured_on"], "2026-08-22")
        self.assertEqual(record["sanitizer"]["keeps"], "tags only")
        self.assertTrue(record["rendered_type_scale"])
        self.assertNotIn("editor", record["observed_in"])


class VerifiedSourcesComposeAcrossTheBoard(unittest.TestCase):
    def test_reply_reuse_requires_a_new_claim_record_but_not_new_page_resolution(self):
        reply = read(REPLY)

        self.assertRegex(reply, r"inherits `REFERENCE`,\s*`RESOLVED` and `PAGE-YEAR`")
        self.assertIn("new `RESTATEMENT` and a new `REFUTATION`", reply)
        self.assertRegex(reply, r"(?is)respent-source.*reply.*reply")


if __name__ == "__main__":
    unittest.main()
