"""Cover ``checks_ledger``'s parser and rows against synthetic checks files.

Every checks file here is written in this file and a temp directory, the way
``test_research_ledger`` writes its ledgers rather than pointing at a real one.
**There is no committed checks file and there will not be one**: it lives under
``scratch/`` because a reader's findings describe a draft written about a
patient, which is ``test_differential_scan``'s position exactly.

``TheSkillSaysWhatThisChecks`` is the one class that reads a committed file, and
it is here for ``test_spelling_scan``'s reason: a scanner that has drifted from
the file a reader opens is worse than no scanner, because it reads as agreement.
**It runs the scanner over the skill's own worked example** rather than only
matching strings -- a documented record shape the grader would refuse teaches the
next run to write a checks file that fails, and every substring test here would
still be green.

**The expected heading set is derived from the skill's own table rather than
retyped**, which is the one place this class is stronger than its sibling's. The
module holds the vocabulary because a run directory is not a checkout and the
tool cannot read ``SKILL.md`` at run time; the test reads the table and asserts
the two agree, on ``test_spelling_scan``'s arrangement with the conventions
table.
"""

from __future__ import annotations

import io
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import checks_ledger as checks

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"

# A record that passes every row, so a test can change one field and know the
# finding it gets back belongs to that field.
CLEAN_RECORD = """\
## CHECK: differential ordering
VERDICT: clean
"""

DEFECT_RECORD = """\
## CHECK: MDM completeness
VERDICT: defect
FINDINGS: The second MDM entry summarizes diverticulitis and names no
    discriminator from this case, and it carries no citation.
"""


def whole_file(*records: str, complete: bool = True) -> str:
    """A checks file. ``complete`` fills in every heading the table names."""
    written = list(records)
    if complete:
        named = {checks.normalize(checks.read_records(r)[0].check) for r in records}
        written += [
            f"## CHECK: {name}\nVERDICT: clean\n"
            for name in checks.EXPECTED_CHECKS
            if checks.normalize(name) not in named
        ]
    return "\n".join(written)


def kinds(text: str) -> list[str]:
    """The finding kinds one checks file produces, in report order."""
    return [f.kind for f in checks.survey(checks.read_records(text)).findings]


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        status = checks.main(argv)
    return status, out.getvalue(), err.getvalue()


def in_a_file(text: str, name: str = "case-study-checks.md"):
    """Write ``text`` to a throwaway directory and hand back the path."""
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / name
    path.write_text(text, encoding="utf-8")
    return directory, path


class TheParserReadsARecordAndItsWrappedFields(unittest.TestCase):
    def test_a_record_opens_on_a_check_heading(self):
        records = checks.read_records(CLEAN_RECORD)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].check, "differential ordering")

    def test_a_field_value_wraps_the_way_a_finding_wraps(self):
        record = checks.read_records(DEFECT_RECORD)[0]
        self.assertIn("no citation", record.value("FINDINGS"))
        self.assertIn("discriminator", record.value("FINDINGS"))

    def test_the_heading_level_is_free(self):
        record = checks.read_records(CLEAN_RECORD.replace("## ", "#### "))[0]
        self.assertEqual(record.check, "differential ordering")

    def test_two_records_do_not_bleed_into_each_other(self):
        records = checks.read_records(CLEAN_RECORD + DEFECT_RECORD)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].value("FINDINGS"), "")

    def test_a_line_before_the_first_heading_belongs_to_no_record(self):
        records = checks.read_records("Post-draft checks.\n\n" + CLEAN_RECORD)
        self.assertEqual(len(records), 1)

    def test_the_complete_file_fails_nothing(self):
        self.assertEqual(kinds(whole_file(CLEAN_RECORD, DEFECT_RECORD)), [])


class EveryCheckTheTableNamesIsPresent(unittest.TestCase):
    """The row that has no counterpart in ``research_ledger``.

    That grader has no expected count and says so; this one does, because
    ``skills/practicum-case-study/SKILL.md`` step 9 fixes the set. A reader that
    was never spawned leaves a hole nothing else in the file shows.
    """

    def test_a_missing_heading_is_a_finding(self):
        text = "\n".join(
            f"## CHECK: {name}\nVERDICT: clean\n" for name in checks.EXPECTED_CHECKS[:-1]
        )
        self.assertEqual(kinds(text), [checks.MISSING_CHECK])

    def test_the_finding_names_which_check_is_missing(self):
        text = "\n".join(
            f"## CHECK: {name}\nVERDICT: clean\n" for name in checks.EXPECTED_CHECKS[1:]
        )
        found = checks.survey(checks.read_records(text)).findings
        self.assertEqual([f.check for f in found], [checks.EXPECTED_CHECKS[0]])

    def test_the_two_reference_rows_are_not_one_check(self):
        """The first table row's name is a prefix of the second's, so a substring
        match would read either one as satisfying both."""
        text = whole_file()
        short, long = checks.EXPECTED_CHECKS[0], checks.EXPECTED_CHECKS[1]
        self.assertTrue(long.startswith(short))
        without_long = text.replace(f"## CHECK: {long}\n", "## CHECK: dropped\n")
        self.assertIn(checks.MISSING_CHECK, kinds(without_long))

    def test_case_and_separating_punctuation_do_not_have_to_match(self):
        text = whole_file().replace("the faculty's own to-do list", "The Faculty's Own To Do List")
        self.assertEqual(kinds(text), [])

    def test_dropping_the_apostrophe_is_a_different_word_and_reports_as_missing(self):
        """The limit of the normalizer, pinned rather than described. ``faculty s``
        and ``facultys`` are not the same token, so this heading does not match --
        and what that costs is a **reported** miss, never a silent pass, which is
        why the sibling's ``normalize`` is taken whole rather than widened here."""
        text = whole_file().replace("the faculty's own to-do list", "the facultys own to-do list")
        self.assertEqual(kinds(text), [checks.MISSING_CHECK])

    def test_a_heading_outside_the_table_is_counted_and_not_graded(self):
        """A run adding a check of its own has not failed anything. A misspelled
        one is already caught from the other direction, by the row above."""
        text = whole_file() + "\n## CHECK: the voice model\nVERDICT: clean\n"
        self.assertEqual(kinds(text), [])
        self.assertEqual(checks.survey(checks.read_records(text)).outside_the_table, 1)

    def test_a_misspelled_heading_is_caught_as_the_missing_one(self):
        text = whole_file().replace("MDM completeness", "MDM completness")
        self.assertEqual(kinds(text), [checks.MISSING_CHECK])


class TwoRecordsForOneCheckIsAWriteThatLandedTwice(unittest.TestCase):
    """#206's lost-write shape showing through: two verdicts for one check, and
    nothing in the file says which was meant."""

    def test_a_repeated_heading_is_a_finding(self):
        text = whole_file() + "\n## CHECK: differential ordering\nVERDICT: defect\nFINDINGS: x\n"
        self.assertEqual(kinds(text), [checks.DUPLICATE_CHECK])

    def test_it_is_reported_once_per_repeat_and_not_once_per_record(self):
        text = whole_file() + "\n## CHECK: MDM completeness\nVERDICT: clean\n"
        found = list(checks.survey(checks.read_records(text)).findings)
        self.assertEqual(len(found), 1)

    def test_every_finding_of_a_triple_names_the_same_total(self):
        """An earlier draft decremented as it went, so the second finding of a
        triple read ``2 records`` -- a count that was false about the file, in the
        one output a reader is told to trust."""
        one = "## CHECK: MDM completeness\nVERDICT: clean\n"
        found = checks.survey(checks.read_records(whole_file() + "\n" + one + "\n" + one)).findings
        self.assertEqual([f.detail for f in found], ["3 records", "3 records"])

    def test_a_repeat_outside_the_table_is_still_two_verdicts(self):
        extra = "## CHECK: the voice model\nVERDICT: clean\n"
        text = whole_file() + "\n" + extra + "\n" + extra
        self.assertEqual(kinds(text), [checks.DUPLICATE_CHECK])


class AHeadingWithNoVerdictIsACheckThatDidNotRun(unittest.TestCase):
    """``SKILL.md`` names this failure itself and then leaves it to the reader who
    has just been told the draft is finished. This is that sentence made runnable."""

    def test_a_bare_heading_fails(self):
        text = whole_file().replace(
            "## CHECK: MDM completeness\nVERDICT: clean\n", "## CHECK: MDM completeness\n"
        )
        self.assertEqual(kinds(text), [checks.MISSING_VERDICT])

    def test_a_verdict_present_but_empty_is_the_same_defect(self):
        text = whole_file().replace(
            "## CHECK: MDM completeness\nVERDICT: clean\n",
            "## CHECK: MDM completeness\nVERDICT:\n",
        )
        self.assertEqual(kinds(text), [checks.MISSING_VERDICT])

    def test_a_heading_with_findings_and_no_verdict_still_fails(self):
        """The reader wrote something; the field that gates every row below it is
        still absent."""
        text = whole_file().replace(
            "## CHECK: MDM completeness\nVERDICT: clean\n",
            "## CHECK: MDM completeness\nFINDINGS: the third entry names no discriminator\n",
        )
        self.assertEqual(kinds(text), [checks.MISSING_VERDICT])

    def test_a_short_file_is_only_visible_because_the_headings_were_written_first(self):
        """Both halves of the ordering rule, in one test. Headings first and a
        lost verdict is a bare heading; headings last and the record is simply
        absent -- which the row above catches, and its sibling grader cannot."""
        headings_first = whole_file().replace(
            "## CHECK: the Rx blocks\nVERDICT: clean\n", "## CHECK: the Rx blocks\n"
        )
        self.assertEqual(kinds(headings_first), [checks.MISSING_VERDICT])
        never_written = whole_file().replace("## CHECK: the Rx blocks\nVERDICT: clean\n", "")
        self.assertEqual(kinds(never_written), [checks.MISSING_CHECK])


class AVerdictIsOneOfTwoWords(unittest.TestCase):
    """``research_ledger``'s ``STATUS`` argument, arriving at the second fan-out:
    the field selects which rows run, so a third word is a record graded on
    nothing at all."""

    def a_verdict(self, value: str) -> list[str]:
        return kinds(
            whole_file().replace(
                "## CHECK: MDM completeness\nVERDICT: clean\n",
                f"## CHECK: MDM completeness\nVERDICT: {value}\n",
            )
        )

    def test_both_declared_words_pass(self):
        self.assertEqual(self.a_verdict("clean"), [])
        self.assertEqual(
            kinds(
                whole_file().replace(
                    "## CHECK: MDM completeness\nVERDICT: clean\n",
                    "## CHECK: MDM completeness\nVERDICT: defect\nFINDINGS: entry 3 names none\n",
                )
            ),
            [],
        )

    def test_a_prefix_of_a_declared_word_is_not_that_word(self):
        """``startswith`` alone is what the sibling matches on, and it is not safe
        for these two words. Every one of these reported nothing, or reported the
        wrong thing, before the boundary went in."""
        self.assertEqual(self.a_verdict("cleanish"), [checks.UNKNOWN_VERDICT])
        self.assertEqual(self.a_verdict("cleanly not run"), [checks.UNKNOWN_VERDICT])
        self.assertEqual(self.a_verdict("defect-free"), [checks.UNKNOWN_VERDICT])
        self.assertEqual(self.a_verdict("defective reasoning throughout"), [checks.UNKNOWN_VERDICT])

    def test_the_boundary_is_not_a_space_only(self):
        """A hyphen, a colon or a comma after the keyword is an ordinary form and
        none of them is a letter."""
        self.assertEqual(self.a_verdict("clean: every entry carries a citation"), [])
        self.assertEqual(self.a_verdict("clean, checked twice"), [])

    def test_a_third_word_is_a_finding(self):
        self.assertEqual(self.a_verdict("mostly fine"), [checks.UNKNOWN_VERDICT])

    def test_a_third_word_does_not_also_report_the_rows_it_skipped(self):
        """One finding, not two. The record is unreadable, not badly written."""
        self.assertEqual(self.a_verdict("probably a defect"), [checks.UNKNOWN_VERDICT])

    def test_case_is_free(self):
        self.assertEqual(self.a_verdict("Clean"), [])

    def test_a_reason_after_the_word_is_allowed_on_either(self):
        self.assertEqual(self.a_verdict("clean - every entry carries a citation"), [])


class ADefectSaysWhatAndWhere(unittest.TestCase):
    """``specificity_scan``'s substance test: anybody can write ``defect``, and
    nobody writes the entry's position and the rule it fails without having read
    it."""

    def a_defect(self, findings: str | None) -> list[str]:
        block = "## CHECK: MDM completeness\nVERDICT: defect\n"
        if findings is not None:
            block += f"FINDINGS: {findings}\n"
        return kinds(whole_file().replace("## CHECK: MDM completeness\nVERDICT: clean\n", block))

    def test_a_defect_with_no_findings_is_a_finding(self):
        self.assertEqual(self.a_defect(None), [checks.DEFECT_WITHOUT_FINDINGS])

    def test_an_empty_findings_field_is_the_same_defect(self):
        self.assertEqual(self.a_defect(""), [checks.DEFECT_WITHOUT_FINDINGS])

    def test_a_findings_field_with_substance_passes(self):
        self.assertEqual(self.a_defect("entry 2 names no discriminator"), [])

    def test_a_reason_on_the_verdict_line_is_not_the_findings_field(self):
        """**#240 asks for `FINDINGS` with substance and an earlier draft here read
        it looser**, accepting a reason typed after the keyword. It says the same
        thing somewhere the record shape does not put it, so a reader looking for
        the finding has nowhere fixed to look."""
        text = whole_file().replace(
            "## CHECK: MDM completeness\nVERDICT: clean\n",
            "## CHECK: MDM completeness\nVERDICT: defect - entry 2 names no discriminator\n",
        )
        self.assertEqual(kinds(text), [checks.DEFECT_WITHOUT_FINDINGS])

    def test_a_clean_check_is_not_asked_for_findings(self):
        """**Named in #240 and deliberately not a row.** A check that ran and
        found nothing is indistinguishable from one that reported nothing, and no
        string test can tell them apart."""
        self.assertEqual(kinds(whole_file()), [])


class TheReportCarriesNoFindingTextWithoutShow(unittest.TestCase):
    def setUp(self):
        self.scan = checks.survey(checks.read_records(whole_file(CLEAN_RECORD, DEFECT_RECORD)))

    def test_the_default_report_prints_no_finding_text(self):
        text = whole_file(CLEAN_RECORD, DEFECT_RECORD).replace("VERDICT: defect", "VERDICT: awful")
        scan = checks.survey(checks.read_records(text))
        report = checks.format_report(scan, source="case-study-checks.md")
        self.assertNotIn("awful", report)
        self.assertNotIn("diverticulitis", report)

    def test_show_prints_it(self):
        text = whole_file(CLEAN_RECORD, DEFECT_RECORD).replace("VERDICT: defect", "VERDICT: awful")
        scan = checks.survey(checks.read_records(text))
        report = checks.format_report(scan, source="case-study-checks.md", show=True)
        self.assertIn("PHI", report)
        self.assertIn("awful", report)

    def test_every_row_is_named_in_the_report_with_its_ticket(self):
        report = checks.format_report(self.scan, source="case-study-checks.md")
        for kind in checks.KINDS:
            with self.subTest(row=kind):
                self.assertIn(kind, report)
                self.assertIn(f"{checks.ROW_TICKET[kind]} - {kind}", report)

    def test_the_report_names_the_file_and_never_a_path(self):
        report = checks.format_report(self.scan, source="case-study-checks.md")
        self.assertIn("case-study-checks.md", report)

    def test_the_default_report_names_a_missing_check(self):
        """The one thing it prints beside a count, and the string comes from
        ``EXPECTED_CHECKS`` rather than from the file."""
        text = "\n".join(
            f"## CHECK: {name}\nVERDICT: clean\n" for name in checks.EXPECTED_CHECKS[:-1]
        )
        scan = checks.survey(checks.read_records(text))
        report = checks.format_report(scan, source="case-study-checks.md")
        self.assertIn(checks.EXPECTED_CHECKS[-1], report)

    def test_a_heading_outside_the_table_is_never_named_without_show(self):
        """The narrowness is the whole of the exception above: an off-table
        heading is the run's own text, so it is counted and not printed."""
        text = whole_file() + "\n## CHECK: the patient's own words\nVERDICT: clean\n"
        scan = checks.survey(checks.read_records(text))
        self.assertEqual(scan.outside_the_table, 1)
        self.assertNotIn("the patient", checks.format_report(scan, source="case-study-checks.md"))

    def test_a_duplicate_heading_is_counted_and_not_named_without_show(self):
        """A duplicate's name is read off the file, so it takes the file's rule
        and not the missing-check exception."""
        extra = "## CHECK: the patient's own words\nVERDICT: clean\n"
        scan = checks.survey(checks.read_records(whole_file() + "\n" + extra + "\n" + extra))
        report = checks.format_report(scan, source="case-study-checks.md")
        self.assertIn(f"{checks.DUPLICATE_CHECK:<{checks.KIND_COLUMN}} 1", report)
        self.assertNotIn("the patient", report)


class TheCommandExitsOnWhatItFound(unittest.TestCase):
    """0 clean, 1 for a violation, 2 for every way of not having scanned. A file
    whose headings this cannot read would otherwise report zero findings and look
    like a checked draft."""

    def test_a_complete_file_exits_zero(self):
        directory, path = in_a_file(whole_file(CLEAN_RECORD, DEFECT_RECORD))
        with directory:
            self.assertEqual(run([str(path)])[0], 0)

    def test_a_failing_record_exits_one(self):
        directory, path = in_a_file(whole_file().replace("VERDICT: clean\n", "\n", 1))
        with directory:
            self.assertEqual(run([str(path)])[0], 1)

    def test_no_arguments_exits_two(self):
        status, _out, err = run([])
        self.assertEqual(status, 2)
        self.assertIn("usage", err)

    def test_a_missing_file_exits_two_rather_than_one(self):
        directory, path = in_a_file("")
        with directory:
            status, _out, err = run([str(path.parent / "absent.md")])
        self.assertEqual(status, 2)
        self.assertIn("absent.md", err)

    def test_a_file_with_no_check_headings_exits_two(self):
        directory, path = in_a_file("The draft looks fine to me.\n")
        with directory:
            status, _out, err = run([str(path)])
        self.assertEqual(status, 2)
        self.assertIn("no check records", err)

    def test_the_exit_one_message_names_no_finding_text(self):
        directory, path = in_a_file(
            whole_file(CLEAN_RECORD, DEFECT_RECORD).replace(
                "FINDINGS: The second MDM entry summarizes diverticulitis and names no\n"
                "    discriminator from this case, and it carries no citation.\n",
                "",
            )
        )
        with directory:
            status, _out, err = run([str(path)])
        self.assertEqual(status, 1)
        self.assertNotIn("diverticulitis", err)
        self.assertIn("--show", err)

    def test_the_error_messages_name_the_file_and_never_the_path(self):
        """A checks file sits under ``scratch/``, so the path is a directory
        naming a patient's run."""
        directory, path = in_a_file("nothing here\n", name="case-study-checks.md")
        with directory:
            _status, _out, err = run([str(path)])
        self.assertNotIn(str(path.parent), err)


class TheSkillSaysWhatThisChecks(unittest.TestCase):
    """``test_spelling_scan``'s rule: a scanner that has drifted from the file a
    reader opens is worse than none, because it reads as agreement."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")

    def table_checks(self) -> list[str]:
        """The first column of the check table in
        ``skills/practicum-case-study/SKILL.md`` step 9, which is the expected set."""
        body = self.skill.split("### 9. Check", 1)[1]
        rows = re.search(r"^\| Check \|.*?(?=\n\n)", body, re.S | re.M).group(0).splitlines()
        return [line.split("|")[1].strip() for line in rows[2:]]

    def test_the_expected_set_is_the_tables_own_column(self):
        """**The vocabulary is derived here and held in the module**, because a
        run directory is not a checkout and the tool cannot read ``SKILL.md`` at
        run time. This is the assertion that keeps the two the same."""
        self.assertEqual(list(checks.EXPECTED_CHECKS), self.table_checks())

    def test_the_skill_names_the_command(self):
        self.assertIn("python tools/checks_ledger.py scratch/case-study-checks.md", self.skill)

    def test_the_skill_shows_every_field_the_parser_reads(self):
        example = self._worked_example()
        self.assertIn("CHECK:", example)
        self.assertIn("VERDICT:", example)
        self.assertIn("FINDINGS:", example)

    # One phrase per row, keyed on the module's own tuple, so a row added without
    # a sentence in the skill fails here rather than becoming a rule only the
    # scanner knows -- which is what ``AGENTS.md`` classes this tool by.
    ROW_PHRASES = {
        checks.MISSING_CHECK: "a heading the table names that is not in the file",
        checks.DUPLICATE_CHECK: "two records under one check",
        checks.MISSING_VERDICT: "a heading with no `VERDICT`",
        checks.UNKNOWN_VERDICT: "a `VERDICT` that is neither word",
        checks.DEFECT_WITHOUT_FINDINGS: "a `defect` with no `FINDINGS` under it",
    }

    def test_the_skill_writes_out_every_row_the_grader_applies(self):
        for kind in checks.KINDS:
            with self.subTest(row=kind):
                self.assertIn(kind, self.ROW_PHRASES, "row is not written into the skill")
                self.assertIn(self.ROW_PHRASES[kind], self.skill)

    def test_the_skill_declares_both_verdicts(self):
        for name in checks.VERDICTS:
            with self.subTest(verdict=name):
                self.assertIn(f"`{name}`", self.skill)

    def test_the_skill_says_a_clean_scan_is_not_a_checked_draft(self):
        self.assertIn("A clean scan is not a checked draft", self.skill)

    def test_the_skill_sends_the_checks_file_to_a_gitignored_directory(self):
        self.assertIn("scratch/case-study-checks.md", self.skill)
        self.assertNotIn("output/case-study-checks.md", self.skill)

    def test_the_skill_keeps_one_writer_on_the_checks_file(self):
        self.assertIn("They return their record; they do not write it", self.skill)
        self.assertIn("Write the check headings down before spawning anything", self.skill)

    def test_the_worked_example_in_the_skill_passes_the_scanner(self):
        """**The one that catches drift a substring cannot see.** A documented
        record shape the grader would refuse teaches the next run to write a
        checks file that fails, and every string test above would still be green."""
        example = self._worked_example()
        records = checks.read_records(example)
        self.assertEqual(len(records), 1, "the skill should carry one worked check record")
        self.assertEqual(checks.record_findings(records[0]), [])

    def _worked_example(self) -> str:
        """The fenced block holding the record shape."""
        blocks = re.findall(r"```\n(## CHECK:.*?)```", self.skill, re.S)
        self.assertEqual(len(blocks), 1, "the skill should carry one worked check record")
        return blocks[0]


if __name__ == "__main__":
    unittest.main()
