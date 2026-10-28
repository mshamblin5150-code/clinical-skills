"""APA mechanics defects and twins through each prose grader's public command.

Synthetic coursework only; no patient, course board, or private source is copied.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

import assignment_docx
from element_coverage_test_support import finalize_current_docx_fixture
import assignment_docx_scan
import case_study_scan
import coursework_mechanics as mechanics
import discussion_post_scan
import discussion_reply_scan
import peer_critique_scan
import test_assignment_docx_scan as word_fixture
import test_discussion_post_scan as post_fixture
import test_discussion_reply_scan as reply_fixture
import test_peer_critique_scan as critique_fixture
from prose_bind import NAMING, bind


GRADERS = ("word", "post", "reply", "critique", "case")
# spelling-scan: mentions 1
REFERENCE = "US Preventive Services Task Force. (2026). *A cancelled CKD review*. Example Press."


class PublicMechanics(unittest.TestCase):
    def test_the_shared_instructions_name_the_limit_owner_without_copying_it(self):
        prose = (Path(__file__).resolve().parents[1] / "skills/_shared/reference/apa7.md").read_text(encoding="utf-8")
        self.assertIn("coursework_mechanics.DECLARED_LIMITS", prose)
        self.assertEqual((), bind(mechanics.DECLARED_LIMITS, prose, mode=NAMING))

    def command(self, root: Path, kind: str, body: str, *, language="en", handling=None, reference=REFERENCE):
        if kind == "word":
            case = word_fixture.empty_population_input(root)
            if language is None:
                bar = Path(case.argv[0]) / "bar.md"
                bar.write_text(bar.read_text(encoding="utf-8").replace("PAPER-LANGUAGE: en\n", ""), encoding="utf-8")
            path = Path(case.argv[2])
            spec = replace(assignment_docx.fixture_spec(),
                           title_page=replace(assignment_docx.fixture_spec().title_page, title="Purpose"),
                           sections=(assignment_docx.Section("Purpose", (body,)),),
                           references=(reference,))
            assignment_docx.build(spec, path, force=True)
            finalize_current_docx_fixture(Path(case.argv[0]), path)
            with ZipFile(path) as archive:
                document = ElementTree.fromstring(archive.read("word/document.xml"))
            text = mechanics.word_surface(document)
            module, argv = assignment_docx_scan, list(case.argv)
            record_root = Path(case.argv[0])
        elif kind == "post":
            run = post_fixture.Run(root)
            path = run.draft
            text = "# Purpose\n\n" + body + "\n\n# References\n\n" + reference
            path.write_text(text, encoding="utf-8")
            run.write_heading_read()
            module, argv = discussion_post_scan, [str(root), "--draft", str(path)]
        elif kind == "reply":
            run = reply_fixture.Run(root, posted=False)
            path = root / "response-maren.md"
            text = "# Purpose\n\n" + body + "\n\n# References\n\n" + reference
            path.write_text(text, encoding="utf-8")
            run.write_heading_read()
            module, argv = discussion_reply_scan, [str(root)]
        elif kind == "critique":
            critique_fixture.build_run(root=root, posted=False)
            path = root / "critique.md"
            text = "# Purpose\n\n" + body + "\n\n# References\n\n" + reference
            path.write_text(text, encoding="utf-8")
            (root / "critique.txt").unlink(missing_ok=True)
            module, argv = peer_critique_scan, [str(root)]
        else:
            path = root / "case.md"
            text = "## Plan\n\n" + body + "\n\n## References\n\n" + reference
            path.write_text(text, encoding="utf-8")
            module, argv = case_study_scan, [str(path)]
        if language is not None:
            argv.extend(("--paper-language", language))
        else:
            argv.extend(("--profile", str(root / "missing-profile.md")))
        if handling is not None:
            # IDs come from the public report; digest is derived from the exact
            # surface independently of the production digest helper.
            record = {"artifacts": [{"artifact": path.name,
                                      "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                                      "hits": handling}]}
            ((record_root if kind == "word" else root) / mechanics.RECORD_NAME).write_text(json.dumps(record), encoding="utf-8")
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = module.main([*argv, "--show"])
        return status, stdout.getvalue() + stderr.getvalue()

    def assert_row(self, report: str, row: str, expected: int):
        self.assertRegex(report, rf"(?m)^{re.escape(row)}: {expected}$", report)

    def test_each_defect_and_correct_twin_crosses_every_public_command(self):
        # spelling-scan: mentions 2
        cases = (
            ("undefined-abbreviation", "CKD affects care.", "Chronic kidney disease (CKD) affects care."),
            ("spelling-variant", "US care meets U.S. practice.", "U.S. care meets U.S. practice."),
            ("spelling-variant", "The healthcare setting changed.", "The health care setting changed."),
            ("spelling-variant", "Healthcare services changed.", "Health care services changed."),
            ("spelling-variant", "# Healthcare services", "# Health care services"),
            ("closed-prefix", "The pre-operative visit changed.", "The preoperative visit changed."),
            ("uncertain-prefix", "The post-acute visit changed.", "The postacute visit changed."),
            ("small-count", "There were 3 patients.", "There were three patients."),
            ("uncertain-digit", "The patient received 2 tablets.", "The patient received two tablets."),
            ("large-number-word", "The ninety-day plan changed.", "The 90-day plan changed."),
            ("numeral-opening", "2026 brought a change.", "The year 2026 brought a change."),
            ("british-body-form", "The visit was cancelled.", "The visit was canceled."),
            ("british-body-form", "The colours differed.", "The colors differed."),
        )
        for grader in GRADERS:
            for row, defect, twin in cases:
                with self.subTest(grader=grader, row=row, body=defect), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    status, report = self.command(root, grader, defect)
                    self.assertEqual(1, status, report)
                    self.assert_row(report, row, 1)
                with self.subTest(grader=grader, twin=twin), tempfile.TemporaryDirectory() as temp:
                    _, report = self.command(Path(temp), grader, twin)
                    self.assert_row(report, row, 0)

    def test_exclusions_and_house_abbreviations_cross_every_command(self):
        # spelling-scan: mentions 1
        body = (
            'HEENT was documented. An anti-inflammatory was selected. '
            'Symptoms co-occur. A meta-analysis was read. '
            'The US Preventive Services Task Force advised U.S. services. '
            'The cited title A cancelled CKD review remains as printed. '
            'The quotation “CKD involved 3 patients and post-acute care” remains as printed.'
        )
        for grader in GRADERS:
            with self.subTest(grader=grader), tempfile.TemporaryDirectory() as temp:
                _, report = self.command(Path(temp), grader, body)
                for row in ("undefined-abbreviation", "spelling-variant", "uncertain-prefix",
                            "small-count", "uncertain-digit", "british-body-form"):
                    self.assert_row(report, row, 0)

    def test_journal_article_titles_are_excluded_before_the_italic_journal_name(self):
        # spelling-scan: mentions 1
        title = "A cancelled CKD review of 3 patients with post-acute ninety-day care"
        reference = f"Author, A. (2026). {title}. *Example Journal*, 2, 10–20."
        for grader in GRADERS:
            with self.subTest(grader=grader), tempfile.TemporaryDirectory() as temp:
                _, report = self.command(Path(temp), grader, f"The article {title} was read.", reference=reference)
                for row in ("undefined-abbreviation", "small-count", "uncertain-prefix",
                            "large-number-word", "british-body-form"):
                    self.assert_row(report, row, 0)

    def test_each_uncertain_hit_requires_its_own_current_handling_record(self):
        for grader in GRADERS:
            for body, row, decision in (
                ("The post-acute visit changed.", "uncertain-prefix",
                 {"action": "retained", "entry": "https://www.merriam-webster.com/dictionary/post-acute"}),
                ("The patient received 2 tablets.", "uncertain-digit",
                 {"action": "retained", "exception": "measurement"}),
            ):
                with self.subTest(grader=grader, row=row), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    _, report = self.command(root, grader, body)
                    ids = re.findall(rf"HIT ({row}:\d+:\d+:[0-9a-f]{{64}})", report)
                    self.assertEqual(1, len(ids), report)
                    # Fresh setup paths avoid reusing fixture-owned directories.
                    with tempfile.TemporaryDirectory() as second:
                        _, handled = self.command(Path(second), grader, body, handling={ids[0]: decision})
                        self.assert_row(handled, row, 0)
                    with tempfile.TemporaryDirectory() as third:
                        _, invalid = self.command(Path(third), grader, body, handling={ids[0]: {"action": "retained", "exception": "plausible"}})
                        self.assertIn("mechanics retained hit requires", invalid)

    def test_partial_handling_leaves_the_other_hit_blocking(self):
        body = "The patient received 2 tablets and 4 capsules."
        for grader in GRADERS:
            with self.subTest(grader=grader), tempfile.TemporaryDirectory() as temp:
                _, report = self.command(Path(temp), grader, body)
                ids = re.findall(r"HIT (uncertain-digit:\d+:\d+:[0-9a-f]{64})", report)
                self.assertEqual(2, len(ids), report)
                with tempfile.TemporaryDirectory() as second:
                    status, report = self.command(Path(second), grader, body,
                        handling={ids[0]: {"action": "retained", "exception": "measurement"}})
                    self.assertEqual(1, status, report)
                    self.assert_row(report, "uncertain-digit", 1)

    def test_changed_shape_is_accepted_without_claiming_its_truth(self):
        for grader in GRADERS:
            with self.subTest(grader=grader), tempfile.TemporaryDirectory() as temp:
                _, report = self.command(Path(temp), grader, "The post-acute visit changed.")
                key = re.search(r"HIT (uncertain-prefix:\d+:\d+:[0-9a-f]{64})", report)[1]
                with tempfile.TemporaryDirectory() as second:
                    _, report = self.command(Path(second), grader, "The post-acute visit changed.",
                                             handling={key: {"action": "changed"}})
                    self.assert_row(report, "uncertain-prefix", 0)

    def test_structural_exceptions_dates_decimals_and_number_words_at_openings(self):
        body = (
            "Ten visits occurred. The pre-APA and pre-1960 designs differ. "
            "The re-form example uses a self-report and non-achievement-oriented scale. "
            "The anti-intellectual label remains. There were 2 mg over 3 days at 4%. "
            "The value was 2.5 on October 3, 2026 in Table 4. They asked us about US care."
        )
        for grader in GRADERS:
            with self.subTest(grader=grader), tempfile.TemporaryDirectory() as temp:
                _, report = self.command(Path(temp), grader, body)
                for row in ("spelling-variant", "closed-prefix", "uncertain-prefix",
                            "uncertain-digit", "large-number-word", "numeral-opening"):
                    self.assert_row(report, row, 0)

    def test_apa_citation_locators_are_not_sentence_openings(self):
        # APA 7 requires page, paragraph, and circa locators; their periods end no sentence.
        body = (
            'The guideline says "query the provider" (Example Agency, 2026, p. 1, p. 12). '
            'The brief agrees (Example Agency, 2026, pp. 2–3, 7; Example Agency, 2026, para. 4). '
            'The emperor wrote it (Marcus Aurelius, ca. 180/2023, 5.20; Book 5, Section 20).'
        )
        for grader in GRADERS:
            with self.subTest(grader=grader), tempfile.TemporaryDirectory() as temp:
                _, report = self.command(Path(temp), grader, body)
                for row in ("uncertain-digit", "numeral-opening"):
                    self.assert_row(report, row, 0)
            with self.subTest(grader=grader, twin="opening"), tempfile.TemporaryDirectory() as temp:
                _, report = self.command(Path(temp), grader, "The visit ended. 2026 brought a change.")
                self.assert_row(report, "numeral-opening", 1)
            # The declared limit: an abbreviation outside the locator list still reads as a boundary.
            with self.subTest(grader=grader, control="unlisted abbreviation"), tempfile.TemporaryDirectory() as temp:
                _, report = self.command(Path(temp), grader, "The record cites vol. 12 of the series.")
                self.assert_row(report, "numeral-opening", 1)
            # Only the locator's own page numbers are exempt; a count written after it still needs handling.
            for control in ("I saw p. 4, 5 nurses waited.", "The study ran ca. 1990, 5 nurses joined.",
                            "She read the book 5 times."):
                with self.subTest(grader=grader, control=control), tempfile.TemporaryDirectory() as temp:
                    _, report = self.command(Path(temp), grader, control)
                    self.assert_row(report, "uncertain-digit", 1)

    def test_record_shape_and_surface_digest_fail_closed(self):
        import run_grader
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, report = self.command(root, "case", "The post-acute visit changed.")
            key = re.search(r"HIT (uncertain-prefix:\d+:\d+:[0-9a-f]{64})", report)[1]
            path = root / mechanics.RECORD_NAME
            path.write_text(json.dumps({"artifacts": [{"artifact": "case.md",
                "sha256": "0" * 64, "hits": {key: {"action": "changed"}}}]}), encoding="utf-8")
            parsed = run_grader.Parsed(str(root), values={"--paper-language": "en"})
            original = run_grader.Grade(scan=None, source=str(root))
            grade = mechanics.apply_grade(original, root, (("case.md", (root / "case.md").read_text(encoding="utf-8")),), parsed)
            self.assertTrue(grade.findings_failed)
            self.assertIn("mechanics-record: 1", "\n".join(grade.reports))
            path.write_text("not JSON", encoding="utf-8")
            grade = mechanics.apply_grade(original, root, (("case.md", "Plain prose."),), parsed)
            self.assertTrue(grade.findings_failed)
            self.assertIn("mechanics-record: 1", "\n".join(grade.reports))

    def test_other_languages_and_unread_language_report_every_row_not_graded(self):
        for grader in GRADERS:
            for language in ("Spanish", None):
                with self.subTest(grader=grader, language=language), tempfile.TemporaryDirectory() as temp:
                    status, report = self.command(Path(temp), grader, "Texto suficiente.", language=language)
                    self.assertIn(status, (1, 2))  # Existing unrelated findings still win.
                    for row in mechanics.ROWS:
                        self.assertIn(f"{row}: not graded - language", report)

    def test_language_coverage_takes_exit_two_and_existing_findings_still_win(self):
        # Public command with its preexisting grade isolated: the new coverage
        # result must itself select exit 2, rather than relying on another gap.
        from unittest import mock
        import run_grader
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for failed, expected in ((False, 2), (True, 1)):
                original = case_study_scan.survey
                def isolated(source, parsed):
                    grade = run_grader.Grade(scan=original(source.markdown, source.skill_text),
                                             source=source.name, findings_failed=failed)
                    return mechanics.apply_grade(grade, root, (("case.md", source.markdown),), parsed)
                with mock.patch.object(case_study_scan, "GRADER", replace(case_study_scan.GRADER, grade=isolated)):
                    status, _ = self.command(root, "case", "Texto suficiente.", language="Spanish")
                    self.assertEqual(expected, status)


if __name__ == "__main__":
    unittest.main()
