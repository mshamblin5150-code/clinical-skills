"""Contract tests for ticket #416's initial-post workflow."""

from __future__ import annotations

import json
import io
import re
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from xml.etree import ElementTree

import discussion_post_scan
import discussion_reply_scan
import discussion_artifact
import docx_write
import reference_scan
from prose_bind import ProseBind
from test_discussion_post_scan import BODY as POST_BODY, Run as PostRun
from test_discussion_reply_scan import BODY as REPLY_BODY, Run as ReplyRun


ROOT = Path(__file__).resolve().parent.parent
POST = ROOT / "skills" / "discussion-post" / "SKILL.md"
REPLY = ROOT / "skills" / "discussion-reply" / "SKILL.md"
CASE_STUDY = ROOT / "skills" / "practicum-case-study" / "SKILL.md"
AGENTS = ROOT / "AGENTS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TheInitialPostHasOneRoutingSurface(ProseBind, unittest.TestCase):
    def test_the_skill_and_index_exist_and_route_worked_cases_away(self):
        post = read(POST)
        rows = [line for line in read(AGENTS).splitlines() if line.startswith("| discussion-post ")]

        self.assertEqual(1, len(rows))
        self.assertIn("initial post", rows[0])
        self.assertIn("practicum-case-study", post)
        self.assertRegex(post, r"(?i)worked clinical case.*not the skill")

    def test_practicum_frontmatter_no_longer_claims_generic_board_posts(self):
        description = read(CASE_STUDY).split("---", 2)[1]
        self.assertProseNotIn("discussion board", description)

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

    def test_reply_walks_the_complete_limit_inventory_not_retired_partial_names(self):
        reply = read(REPLY)

        self.assertIn("discussion_reply_scan.NOT_REACHED", reply)
        self.assertNotIn("discussion_reply_scan.UNMARKED_INVOKED_SOURCE_LIMIT", reply)

    def test_step_seven_renders_one_bold_heading_document_and_grades_it(self):
        post = read(POST)
        self.assertRegex(post, r"docx_write\.py[^\n]+--bold-headings")
        self.assertRegex(post, r"discussion_post_scan\.py[^\n]+--docx")
        self.assertIn("rendered-comments", post)
        self.assertNotRegex(post, r"(?i)manually demote|heading demotion")
        self.assertNotRegex(post, r"carries the hanging indent.*heading structure")

    def test_the_post_workflow_relies_on_rendering_while_the_reply_still_omits_comments(self):
        post = read(POST)
        reply = read(REPLY)

        self.assertIn("`docx_write.py` drops own-line HTML comments", post)
        retired_instruction = "omit every " + "`INVOKED` comment"
        self.assertNotIn(retired_instruction, post)
        self.assertIn("omitting the `INVOKED` comments", reply)
        self.assertIn("pastes from Markdown", post)

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


class EachDiscussionSkillStatesTheInvokedSourceForm(ProseBind, unittest.TestCase):
    def test_both_skills_state_the_shared_marker_form(self):
        for path in (POST, REPLY):
            with self.subTest(skill=path.parent.name):
                self.assertProseIn(discussion_artifact.INVOKED_FORM, read(path))

    def test_the_marker_rule_keys_on_presence_not_conscious_intent(self):
        reply = read(REPLY)

        self.assertNotIn("consciously", reply)
        self.assertRegex(reply, r"(?i)mark every (?:retained )?invoked source")

    def test_reply_approval_names_the_invoked_source_table_and_two_questions(self):
        reply = read(REPLY)

        self.assertProseIn("the invoked source, its domain, and the property it spends", reply)
        self.assertProseIn("whether the substance is right", reply)
        self.assertProseIn("whether each invoked source sounds like the clinician", reply)
        self.assertProseIn("one approval with two named questions", reply)

    def test_neither_skill_teaches_magnitude_or_a_domain_taxonomy(self):
        for path in (POST, REPLY):
            text = read(path)
            with self.subTest(skill=path.parent.name):
                self.assertProseIn("do not enlarge the noun or increase the rate", text)
                self.assertProseIn("do not create a list of permitted domains", text)
                self.assertProseIn("state the property as a predicate-bearing clause", text)

    def test_current_skill_prose_uses_the_domain_term(self):
        for path in (POST, REPLY):
            with self.subTest(skill=path.parent.name):
                self.assertNotRegex(read(path), r"(?i)\bfigure(?:s)?\b")


class EachSkillStatesTheLabelItsPipelineAccepts(unittest.TestCase):
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

    def stated_label(self, path: Path, phrase: str) -> str:
        match = re.search(phrase + r" `(?P<label>[^`]+)`", read(path))
        self.assertIsNotNone(match, f"{path} does not state its pipeline label")
        return match.group("label")

    def test_the_reply_label_runs_clean_through_the_reply_command(self):
        label = self.stated_label(REPLY, r"End with the bold Markdown label")
        with tempfile.TemporaryDirectory() as temp:
            run = ReplyRun(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                REPLY_BODY.replace("**References**", label),
                encoding="utf-8",
            )
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                status = discussion_reply_scan.main([temp])

        self.assertEqual(0, status)

    def test_the_post_label_runs_clean_through_every_post_command_and_renders_bold(self):
        label = self.stated_label(POST, r"End with the Markdown heading")
        with tempfile.TemporaryDirectory() as temp:
            run = PostRun(Path(temp))
            run.draft.write_text(
                POST_BODY.replace(
                    "# Access Is More Than Availability",
                    "# Access Is More Than Availability\n\n"
                    "<!-- INVOKED: gravity | attracts mass -->",
                ).replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.\n\n"
                    "<!-- INVOKED: gravity | attracts mass -->",
                ).replace("## References", label),
                encoding="utf-8",
            )
            document = run.root / "post.docx"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                post_status = discussion_post_scan.main(
                    [str(run.root), "--draft", str(run.draft)]
                )
                reference_status = reference_scan.main(
                    [str(run.draft), "--as-of", "2026-08-22"]
                )
                render_status = docx_write.main(
                    [str(run.draft), str(document), "--bold-headings"]
                )
                rendered_post_status = discussion_post_scan.main(
                    [
                        str(run.root),
                        "--draft",
                        str(run.draft),
                        "--docx",
                        str(document),
                    ]
                )
            with zipfile.ZipFile(document) as archive:
                xml = ElementTree.fromstring(archive.read("word/document.xml"))

        self.assertEqual((0, 0, 0, 0), (
            post_status,
            reference_status,
            render_status,
            rendered_post_status,
        ))
        rendered_text = "".join(text.text or "" for text in xml.iter(self.W + "t"))
        self.assertNotIn("INVOKED", rendered_text)
        paragraph = next(
            node
            for node in xml.iter(self.W + "p")
            if "".join(text.text or "" for text in node.iter(self.W + "t")) == "References"
        )
        self.assertIsNone(paragraph.find("./" + self.W + "pPr/" + self.W + "pStyle"))
        runs = paragraph.findall("./" + self.W + "r")
        self.assertTrue(runs)
        self.assertTrue(
            all(run.find("./" + self.W + "rPr/" + self.W + "b") is not None for run in runs)
        )


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

        self.assertRegex(
            reply,
            r"inherits `REFERENCE`,\s*`RESOLVED`, `PAGE-YEAR`, and `STATED-EXPIRY`",
        )
        self.assertIn("new `RESTATEMENT`, `REFUTATION`, and `SECOND-ROUTE`", reply)
        self.assertIn("`SECOND-ROUTE` belongs to the new refutation and is never inherited", reply)
        self.assertRegex(reply, r"(?is)respent-source.*reply.*reply")


if __name__ == "__main__":
    unittest.main()
