"""Tests for ``delegated_answers``: a delegated answer cites a written rule or says none.

Records are written in this file against a temporary checkout, so a quoted rule
is checked against text the test controls (ADR 0309 rulings 1 and 2).
"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import artifact_lock_test_support  # noqa: F401 -- the graders below reach artifact_lock
import delegated_answers as d
import differential_scan
import filled_vitals_census
from prose_bind import NAMING, bind


RULE_TEXT = (
    "**Not withheld.** A BMI of 26.5 from a filled height and weight produces\n"
    "`E66.3` and `Z68.26`, and the note carries both.\n"
)
SETTLED = (
    "## QUESTION: Code weight where no weight assessment was documented?\n"
    'RULE: skills/clinical-note/SKILL.md: "A BMI of 26.5 from a filled height and weight produces `E66.3` and `Z68.26`, and the note carries both."\n'
    "ANSWER: the codes stay, as the rule says.\n"
)
NONE = (
    "## QUESTION: Which of two equivalent follow-up intervals?\n"
    "RULE: none found\n"
    "ANSWER: two weeks, named at the go-ahead.\n"
)


class Checkout:
    def __enter__(self) -> tuple[Path, Path]:
        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name)
        skill = root / "skills" / "clinical-note"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(RULE_TEXT, encoding="utf-8")
        run = root / "run"
        run.mkdir()
        return root, run

    def __exit__(self, *exc: object) -> None:
        self.directory.cleanup()


def gate(record: str | None, submission: str | None = "a-test-submission") -> tuple[bool, str]:
    with Checkout() as (root, run):
        if record is not None:
            (run / d.RECORD).write_text(record, encoding="utf-8")
        return d.completion_gate(run, submission, root=root)


class TheBoundaryIsDeclaredOnce(unittest.TestCase):
    def test_the_docstring_points_at_the_object_without_copying_rows(self):
        doc = d.__doc__ or ""
        self.assertEqual(1, doc.count("delegated_answers.DECLARED_LIMITS"))
        self.assertEqual((), bind(d.DECLARED_LIMITS, doc, mode=NAMING))


class TheGate(unittest.TestCase):
    def test_it_waits_for_the_terminal_submission(self):
        failed, report = gate(SETTLED, submission=None)
        self.assertFalse(failed)
        self.assertIn("not graded", report.casefold())

    def test_an_absent_record_is_reported_and_never_graded(self):
        failed, report = gate(None)
        self.assertFalse(failed)
        self.assertIn("none recorded", report)

    def test_a_quoted_rule_and_a_none_found_answer_are_clean_and_counted(self):
        failed, report = gate(SETTLED + "\n" + NONE)
        self.assertFalse(failed, report)
        self.assertIn("2 recorded, 1 settled by a quoted written rule, 1 with no governing rule", report)

    def test_a_rule_the_cited_file_does_not_contain_is_a_finding(self):
        failed, report = gate(SETTLED.replace("carries both", "carries neither"))
        self.assertTrue(failed)
        self.assertIn("does not contain", report)

    def test_a_fragment_the_file_contains_is_not_a_governing_sentence(self):
        fragment = SETTLED.replace(
            '"A BMI of 26.5 from a filled height and weight produces `E66.3` and `Z68.26`, and the note carries both."',
            '"withheld"',
        )
        failed, report = gate(fragment)
        self.assertTrue(failed)
        self.assertIn("not a governing sentence", report)

    def test_a_rule_outside_the_written_rules_is_a_finding(self):
        failed, report = gate(SETTLED.replace("skills/clinical-note/SKILL.md", "scratch/notes.md"))
        self.assertTrue(failed)
        self.assertIn("outside", report)

    def test_a_missing_answer_or_a_bare_rule_is_a_finding(self):
        for record, why in (
            (NONE.replace("ANSWER: two weeks, named at the go-ahead.\n", ""), "ANSWER"),
            (NONE.replace("RULE: none found", "RULE: the skill says so"), "neither"),
        ):
            with self.subTest(why=why):
                failed, report = gate(record)
                self.assertTrue(failed)
                self.assertIn(why, report)

    def test_a_record_with_no_question_is_a_finding(self):
        failed, report = gate("delegated answers follow\n")
        self.assertTrue(failed)
        self.assertIn("no QUESTION record", report)

    def test_the_report_never_carries_the_question_or_the_answer(self):
        _, report = gate(SETTLED.replace("carries both", "carries neither") + NONE)
        self.assertNotIn("weight assessment", report)
        self.assertNotIn("two weeks", report)


class BothNoteGradersRunIt(unittest.TestCase):
    """Driven through each command, so a dropped call fails rather than a dropped string."""

    def test_each_completion_grader_reports_the_row_at_a_submission(self):
        for module in (filled_vitals_census, differential_scan):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as directory:
                run = Path(directory)
                (run / "note-1.md").write_text(
                    "# Note 1, 45-year-old male\n\nVS: Ht 70 in, Wt 160 lb\n", encoding="utf-8"
                )
                (run / d.RECORD).write_text("RULE: none found\n", encoding="utf-8")
                stdout, stderr = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    status = module.main([str(run), "--submission", "a-test-submission"])
                output = stdout.getvalue() + stderr.getvalue()
                self.assertEqual(1, status)
                self.assertIn(f"{d.EXPECTED_ROW}: finding - {d.RECORD} holds no QUESTION record", output)


if __name__ == "__main__":
    unittest.main()
