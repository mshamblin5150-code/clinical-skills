"""Tests for tools/threshold_sheet.py.

**Synthetic sheets built in this file, and the committed one is never graded here.**
That is `test_icd10.py`'s reasoning: a test reading the sheet its own gates passed
would pass for two reasons, one of them being that the sheet and the grader are wrong
together. `reference/thresholds/hypertension.md` is graded by running the command,
which is one line a reader can run and check.

Two classes matter more than the rest. ``RangeGate`` pins each of the ten false
positives the first version produced on that real sheet -- every one of them was a
number in a unit the row was not about. ``ConflictRule`` pins the clinician's ruling
that two populations disagreeing is not a conflict, which is the one rule here that
came from outside the corpus.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import threshold_sheet as gate  # noqa: E402

def header(mode: str = "exact") -> str:
    """The sheet preamble, with the source's declared mode parameterized.

    Parameterized because gate_coverage now cross-checks the sheet's declared mode
    against the recommendation record's, so a fixture hard-coding `exact` cannot be
    used to test the `bound` path -- it would fail on the disagreement rather than on
    the thing under test. That mismatch is itself a finding now, and it has its own
    test below.
    """
    return HEADER.replace("| 2025 | 2025 | https://example.invalid | exact |",
                          f"| 2025 | 2025 | https://example.invalid | {mode} |")


HEADER = f"""# Test sheet

{gate.SCHEMA_MARKER}

## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| src | AHA/ACC | Society/doc | 2025 | 2025 | https://example.invalid | exact |

## Scope

citations resolved against C:/nowhere on 2026-08-16

## Populations

| key | verbatim |
| --- | --- |
| adults | adults |
| adults-ckd | adults with chronic kidney disease |
"""


def sheet(rows: str, conflicts: str = "", coverage: str = "", mode: str = "exact") -> gate.Sheet:
    text = (
        header(mode)
        + "\n## Thresholds\n\n"
        + "| quantity | population | value | snippet | source | page | rec | class |\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + rows
        + "\n## Conflicts\n\n"
        + conflicts
        + "\n## Coverage\n\n"
        + coverage
    )
    return gate.parse(text, Path("test-sheet.md"))


def row(quantity="bp-goal", population="adults", value="<130 mm Hg",
        snippet="an SBP goal of <130 mm Hg", page="p41", rec="p41/goal/1", klass="1") -> str:
    return f"| {quantity} | {population} | {value} | \"{snippet}\" | src | {page} | {rec} | {klass} |\n"


class Parsing(unittest.TestCase):
    def test_a_sheet_without_the_marker_is_not_graded_rather_than_clean(self):
        """The #153 shape at the file level. A sheet the parser cannot read must not
        report zero violations."""
        parsed = gate.parse("# Not a sheet\n\nsome prose\n", Path("x.md"))
        self.assertFalse(parsed.ok)
        self.assertIn("marker", parsed.why_not)

    def test_a_sheet_with_the_marker_but_no_rows_is_not_graded_either(self):
        parsed = gate.parse(HEADER, Path("x.md"))
        self.assertFalse(parsed.ok)
        self.assertIn("no row", parsed.why_not)

    def test_a_pipe_row_outside_the_thresholds_section_is_not_a_threshold(self):
        """The load-bearing parser choice, and `block_scan.py`'s rule adopted whole.

        A sheet's own prose discusses its rules, and the README beside it is full of
        example rows. A parser matching a row shape anywhere would read the
        explanation of a threshold as a threshold.
        """
        parsed = sheet(row())
        self.assertEqual(len(parsed.rows), 1)
        self.assertEqual(len(parsed.sources), 1)
        self.assertEqual(len(parsed.populations), 2)


class SchemaGate(unittest.TestCase):
    def test_an_undeclared_population_key_fails(self):
        """The key is the whole conflict mechanism, so an undeclared one is not a
        typo -- it is a row that can never be compared with any other."""
        failures = gate.gate_schema(sheet(row(population="adults-pregnancy")))
        self.assertTrue(any("not declared" in message for message in failures))

    def test_an_undeclared_source_key_fails(self):
        parsed = sheet(row())
        parsed.rows = [parsed.rows[0].__class__(**{**parsed.rows[0].__dict__, "source": "ghost"})]
        self.assertTrue(any("'## Sources'" in message for message in gate.gate_schema(parsed)))

    def test_a_symbol_font_pound_sign_in_a_value_fails(self):
        """73 of these are in the corpus, all of them a less-or-equal sign that lost
        its encoding. A sheet holds the fact and must not hold the mis-encoding."""
        failures = gate.gate_schema(sheet(row(value="\u00a3120 mm Hg")))
        self.assertTrue(any("Symbol-font" in message for message in failures))

    def test_a_unicode_comparison_sign_in_a_value_fails(self):
        failures = gate.gate_schema(sheet(row(value="\u2265130 mm Hg")))
        self.assertTrue(any("ASCII" in message for message in failures))

    def test_a_verbatim_snippet_may_keep_the_unicode_sign_the_value_may_not(self):
        """The asymmetry is deliberate and it is the point of having two columns.

        A snippet is a citation anchor and must match the page exactly, typography
        included. A value is what a clinician reads back, and it is normalized.
        """
        failures = gate.gate_schema(
            sheet(row(value=">=130 mm Hg", snippet="average SBP is \u2265130 mm Hg"))
        )
        self.assertEqual(failures, [])


class ConflictRule(unittest.TestCase):
    def test_same_quantity_and_population_with_different_values_needs_a_conflict_block(self):
        rows = row(value="<130 mm Hg") + row(value="<120 mm Hg", rec="p50/goal/1")
        failures = gate.gate_schema(sheet(rows))
        self.assertTrue(any("CONFLICT" in message for message in failures))

    def test_a_conflict_block_satisfies_it(self):
        rows = row(value="<130 mm Hg") + row(value="<120 mm Hg", rec="p50/goal/1")
        parsed = sheet(rows, conflicts="**CONFLICT: bp-goal** - the two societies differ because ...\n")
        self.assertEqual(gate.gate_schema(parsed), [])

    def test_different_populations_are_not_a_conflict(self):
        """The clinician's ruling, made mechanical.

        KDIGO targets SBP <120 in CKD and AHA/ACC targets <130/80 in general adults.
        Those are two rows about two patients, and calling them a contradiction would
        be the sheet inventing one. This is the reason the population key exists at
        all -- without it this case is indistinguishable from the one above.
        """
        rows = (
            row(quantity="bp-goal", population="adults", value="<130 mm Hg")
            + row(quantity="bp-goal", population="adults-ckd", value="<120 mm Hg", rec="p50/goal/1")
        )
        self.assertEqual(gate.gate_schema(sheet(rows)), [])

    def test_the_same_value_stated_twice_is_not_a_conflict(self):
        """A guideline restates its own targets in several sections, so a sheet
        legitimately carries the same number from several recommendations."""
        rows = row(rec="p41/goal/1") + row(rec="p48/goal/1")
        self.assertEqual(gate.gate_schema(sheet(rows)), [])


class CitationTier1(unittest.TestCase):
    def test_a_value_whose_number_is_absent_from_its_snippet_fails(self):
        failures = gate.gate_citation_tier1(
            sheet(row(value="<140 mm Hg", snippet="an SBP goal of <130 mm Hg"))
        )
        self.assertEqual(len(failures), 1)
        self.assertIn("140", failures[0])

    def test_a_value_with_no_number_is_not_checked(self):
        """`monthly` and `once daily` are real rows in the first sheet. A gate that
        demanded a digit would refuse a correct row."""
        self.assertEqual(
            gate.gate_citation_tier1(sheet(row(value="monthly", snippet="at monthly intervals"))),
            [],
        )

    def test_it_runs_with_no_pdfs_anywhere(self):
        """The whole reason tier 1 exists. Decision 2: there must be no machine on
        which citation checking drops to zero."""
        failures, skipped, rendered = gate.gate_citation_tier2(
            sheet(row()), Path("C:/nowhere-at-all")
        )
        self.assertEqual(failures, [])
        self.assertIsNotNone(skipped)
        self.assertEqual(rendered, 0)
        self.assertEqual(gate.gate_citation_tier1(sheet(row())), [])


class CoverageGate(unittest.TestCase):
    RECS = {
        "doc_id": "Society/doc",
        "mode": "exact",
        "recommendations": [
            {"rec_id": "p41/goal/1"},
            {"rec_id": "p41/goal/2"},
            {"rec_id": "p41/goal/3"},
        ],
    }

    def test_an_uncited_unscoped_recommendation_refuses_on_an_exact_source(self):
        parsed = sheet(row(rec="p41/goal/1"), coverage="- `p41/goal/2` - no number stated\n")
        refusals, warnings, _ = gate.gate_coverage(parsed, self.RECS)
        self.assertEqual(len(refusals), 1)
        self.assertIn("p41/goal/3", refusals[0])
        self.assertEqual(warnings, [])

    def test_the_same_omission_only_warns_on_a_bound_source(self):
        """Gate 2's two behaviors, and the mode is read off the recommendation record
        rather than decided here. A marker count over-reports, so enforcing it would
        refuse a correct sheet for recommendations that do not exist."""
        parsed = sheet(
            row(rec="p41/goal/1"),
            coverage="- `p41/goal/2` - no number stated\n",
            mode="bound",
        )
        refusals, warnings, _ = gate.gate_coverage(parsed, {**self.RECS, "mode": "bound"})
        self.assertEqual(refusals, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("over-reports", warnings[0])

    def test_a_sheet_declaring_a_mode_its_record_disagrees_with_is_refused(self):
        """Found in review: the `mode` column was decorative.

        `gate_coverage` read the mode off the recommendation record and never off the
        sheet, so a sheet could declare `exact` over a `bound` record and pass — while
        README.md tells a reader that column is what decides refuse-versus-warn.
        Neither value is trusted over the other, because only the disagreement is
        knowable; what produced it is not.
        """
        parsed = sheet(row(rec="p41/goal/1"), mode="exact")
        refusals, _, _ = gate.gate_coverage(parsed, {**self.RECS, "mode": "bound"})
        self.assertTrue(any("declares mode" in message for message in refusals))

    def test_a_row_carrying_the_wrong_class_for_its_recommendation_is_refused(self):
        """The one check here that catches a row pinned to the WRONG recommendation.

        Every other gate passes such a row: its number is real, its snippet is on the
        page it names, and its rec_id exists. Only the class disagrees.
        """
        recs = {**self.RECS, "recommendations": [{"rec_id": "p41/goal/1", "cor": "2a"}]}
        refusals, _, _ = gate.gate_coverage(sheet(row(rec="p41/goal/1", klass="1")), recs)
        self.assertTrue(any("does not match" in message for message in refusals))

    def test_a_bound_source_carries_no_class_so_the_class_check_stays_quiet(self):
        """Running text does not put the class in a cell, so `cor` is None on every
        marker hit and there is nothing to compare. The check declines rather than
        inventing a disagreement."""
        recs = {
            "doc_id": "Society/doc",
            "mode": "bound",
            "recommendations": [{"rec_id": "p41/goal/1", "cor": None}],
        }
        refusals, _, _ = gate.gate_coverage(sheet(row(rec="p41/goal/1"), mode="bound"), recs)
        self.assertEqual(refusals, [])

    def test_it_fires_on_one_unread_item_not_only_on_total_absence(self):
        """#153's lesson, from this ticket's own comment: fire on ANY unread item.

        A gate that only fires when nothing was covered reads green over partial
        coverage, which is the case that actually ships -- there it was 2 of 83.
        """
        covered = "".join(f"- `p41/goal/{n}` - no number\n" for n in (2, 3))
        parsed = sheet(row(rec="p41/goal/1"), coverage=covered)
        refusals, _, _ = gate.gate_coverage(parsed, self.RECS)
        self.assertEqual(refusals, [])

        parsed = sheet(row(rec="p41/goal/1"), coverage="- `p41/goal/2` - no number\n")
        refusals, _, _ = gate.gate_coverage(parsed, self.RECS)
        self.assertEqual(len(refusals), 1)

    def test_no_recommendation_record_is_reported_as_ungraded_never_as_clean(self):
        refusals, warnings, ungraded = gate.gate_coverage(sheet(row()), None)
        self.assertEqual((refusals, warnings), ([], []))
        self.assertEqual(ungraded, 1)


class RangeGate(unittest.TestCase):
    """Each of these was a false failure on the first real sheet.

    The first version matched a bound by substring against the row's QUANTITY name and
    then graded every number in the value against it. Ten rows failed and all ten were
    correct. The bound is keyed on the unit now, and each shape below is one of those
    ten.
    """

    def test_catches_the_failure_it_exists_for(self):
        failures, _ = gate.gate_range(sheet(row(value="<1300 mm Hg", snippet="1300")))
        self.assertEqual(len(failures), 1)
        self.assertIn("1300", failures[0])

    def test_a_bmi_unit_suffix_is_not_a_bmi(self):
        """`>=27 kg/m2` -- the 2 in m2 was being graded as a body mass index."""
        failures, _ = gate.gate_range(sheet(row(quantity="bmi-threshold", value=">=27 kg/m2")))
        self.assertEqual(failures, [])

    def test_a_duration_in_a_row_whose_quantity_name_contains_bp_is_not_a_pressure(self):
        """`acute-ich-bp-control-duration` = `>=7 days`. The name contains `bp`; the
        number is a count of days."""
        failures, _ = gate.gate_range(
            sheet(row(quantity="acute-ich-bp-control-duration", value=">=7 days"))
        )
        self.assertEqual(failures, [])

    def test_a_percentage_beside_a_time_window_is_not_a_pressure(self):
        """`15% in 24 h` failed twice: once on the 15 and once on the 24."""
        failures, _ = gate.gate_range(
            sheet(row(quantity="acute-stroke-bp-reduction-target", value="15% in 24 h"))
        )
        self.assertEqual(failures, [])

    def test_a_pressure_and_a_time_window_in_one_value_grade_separately(self):
        """`<160/110 mm Hg within 30 to 60 min` -- both pressures graded, both
        minutes left alone, in a single value."""
        failures, ungraded = gate.gate_range(
            sheet(row(value="<160/110 mm Hg within 30 to 60 min"))
        )
        self.assertEqual(failures, [])
        self.assertEqual(ungraded, 2)

    def test_a_paired_systolic_and_diastolic_bound_grades_both_numbers(self):
        failures, _ = gate.gate_range(sheet(row(value="140-159/90-109 mm Hg")))
        self.assertEqual(failures, [])
        failures, _ = gate.gate_range(sheet(row(value="140-159/900-109 mm Hg")))
        self.assertEqual(len(failures), 1)

    def test_a_number_in_no_recognized_unit_is_counted_rather_than_passed(self):
        """The ungraded count is returned and printed. A gate that grades 4 of 200
        numbers and reports clean is the shape #153 caught reading green."""
        _, ungraded = gate.gate_range(sheet(row(value="once daily after 3 doses")))
        self.assertEqual(ungraded, 1)


class QuietSuppressesTheReportAndNeverAFinding(unittest.TestCase):
    """The pre-commit hook runs `--quiet`, so this is the contract that decides
    whether the gate can be made silent.

    **It was broken once, between writing the flag and wiring the hook.** Every FAIL
    line went through the quiet shim, which does not take ``file=``, so a failing
    sheet raised a TypeError instead of naming what was wrong. That is worse than
    either outcome it sits between: the commit was refused, and by a traceback rather
    than by a finding. Anything written to stderr is a finding and goes to ``print``.
    """

    @staticmethod
    def run_grade(quiet: bool, sheet_text: str) -> tuple[int, str, str]:
        import io
        import contextlib
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(sheet_text, encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = gate.grade(path, None, Path("C:/nowhere-at-all"), quiet=quiet)
            return status, out.getvalue(), err.getvalue()

    BROKEN = (
        HEADER
        + "\n## Thresholds\n\n"
        + "| quantity | population | value | snippet | source | page | rec | class |\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + row(value="<1300 mm Hg", snippet="an SBP goal of <1300 mm Hg")
    )

    def test_quiet_hides_the_report_on_a_clean_sheet(self):
        text = (
            HEADER
            + "\n## Thresholds\n\n"
            + "| quantity | population | value | snippet | source | page | rec | class |\n"
            + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            + row()
        )
        _, loud, _ = self.run_grade(False, text)
        _, quiet, _ = self.run_grade(True, text)
        self.assertIn("SCHEMA", loud)
        self.assertNotIn("SCHEMA", quiet)

    def test_quiet_still_prints_every_finding(self):
        status, _, err = self.run_grade(True, self.BROKEN)
        self.assertEqual(status, 1)
        self.assertIn("FAIL", err)
        self.assertIn("1300", err)

    def test_quiet_still_prints_the_tier_two_banner(self):
        """The banner is the one thing decision 2 turns on: a skipped tier 2 must not
        be readable as a pass, and the hook runs quiet."""
        _, out, _ = self.run_grade(True, self.BROKEN)
        self.assertIn("CITATION TIER 2 DID NOT RUN", out)


class TheExitStatusSaysWhichKindOfNotGraded(unittest.TestCase):
    """Found in review, and it is this ticket's own lesson failing on its own gate.

    ``grade`` tested ``recs_path is None`` to decide whether to report that omission
    went unchecked. A ``--recs`` pointing at a file that does not exist is not None,
    so COVERAGE silently did not run, nothing printed, and the sheet exited **0**.
    That is exactly *"a test that goes green because its input vanished"*, and the
    pre-commit hook was one typo away from it.
    """

    CLEAN = (
        header()
        + "\n## Thresholds\n\n"
        + "| quantity | population | value | snippet | source | page | rec | class |\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + row()
    )

    def grade_with(self, recs_path: Path | None) -> int:
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(self.CLEAN, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return gate.grade(path, recs_path, Path("C:/nowhere-at-all"), quiet=True)

    def test_a_recs_path_that_does_not_exist_is_2_and_not_0(self):
        self.assertEqual(self.grade_with(Path("C:/nowhere-at-all/recs.json")), 2)

    def test_no_recs_at_all_is_also_2(self):
        self.assertEqual(self.grade_with(None), 2)

    def test_a_missing_recs_file_says_so_by_name(self):
        """The two 2s are not the same event and the message has to distinguish them:
        one is a run that never meant to check omission, the other is a typo."""
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(self.CLEAN, encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                gate.grade(path, Path("C:/nowhere/recs.json"), Path("C:/nowhere"), quiet=True)
            self.assertIn("no such file", err.getvalue())


class TheReportBodySaysCoverageDidNotRun(unittest.TestCase):
    """The sibling of the class above, and it survived that fix because every test
    there passes ``quiet=True`` and so never reads the report.

    The exit status was right and the stderr notice was right; the **report body**
    still printed ``COVERAGE  0 refusing, 0 warning``, which is what a clean coverage
    pass prints. Redirect stdout to keep the report -- which is the only reason to
    print one -- and the notice is on the stream you dropped, leaving an artifact
    that reads as a full pass over a gate that never ran.

    That is this ticket's comment 3 exactly, *"a count printed beside a green verdict
    is read as a footnote to a pass"*, one turn sharper: a **zero** printed beside a
    gate that did not run. ``CITATION tier 2`` already prints ``SKIPPED`` in the body
    for the same situation, so the fix is to make COVERAGE symmetric with the gate
    standing next to it rather than to invent a convention.
    """

    def report_for(self, recs_path: Path | None) -> str:
        import contextlib
        import io
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sheet.md"
            path.write_text(TheExitStatusSaysWhichKindOfNotGraded.CLEAN, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                gate.grade(path, recs_path, Path("C:/nowhere-at-all"), quiet=False)
            return out.getvalue()

    def coverage_line(self, report: str) -> str:
        lines = [line for line in report.splitlines() if "COVERAGE" in line]
        self.assertEqual(len(lines), 1, f"expected one COVERAGE line, got {lines}")
        return lines[0]

    def test_a_missing_recs_file_does_not_print_a_zero_count(self):
        line = self.coverage_line(self.report_for(Path("C:/nowhere/recs.json")))
        self.assertIn("NOT RUN", line)
        self.assertNotIn("0 refusing", line)

    def test_no_recs_at_all_does_not_print_a_zero_count_either(self):
        line = self.coverage_line(self.report_for(None))
        self.assertIn("NOT RUN", line)
        self.assertNotIn("0 refusing", line)

    def test_a_graded_sheet_still_prints_its_counts(self):
        """The fix must not swallow the ordinary line: a run that did check omission
        and found nothing has to keep saying so, or this trades one silence for
        another."""
        import contextlib
        import io
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            recs = Path(directory) / "recs.json"
            recs.write_text(
                json.dumps(
                    {
                        "doc_id": "d",
                        "source": "d.pdf",
                        "mode": "exact",
                        "totals": {"recommendations": 1, "tables": 1},
                        "recommendations": [
                            {"rec_id": "p1/topic/1", "page": 1, "cor": "1", "text": "t"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            path = Path(directory) / "sheet.md"
            path.write_text(TheExitStatusSaysWhichKindOfNotGraded.CLEAN, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                gate.grade(path, recs, Path("C:/nowhere-at-all"), quiet=False)
            line = self.coverage_line(out.getvalue())
            self.assertIn("refusing", line)
            self.assertNotIn("NOT RUN", line)


class TheRenderedPageEscapeHatch(unittest.TestCase):
    """#83: *"a per-row annotation meaning read off the rendered page, extraction
    garbles this table. Declaring it is a deliberate act that leaves a trace."*"""

    def test_a_declared_row_is_skipped_by_tier_two_and_counted(self):
        marked = row(snippet=f"{gate.RENDERED_MARKER} an SBP goal of <130 mm Hg")
        failures, skipped, rendered = gate.gate_citation_tier2(
            sheet(marked), Path(__file__).parent
        )
        self.assertIsNone(skipped)
        self.assertEqual(rendered, 1)
        self.assertEqual(failures, [])

    def test_an_undeclared_row_is_not_skipped(self):
        _, _, rendered = gate.gate_citation_tier2(sheet(row()), Path(__file__).parent)
        self.assertEqual(rendered, 0)

    def test_the_marker_must_start_the_snippet_not_merely_appear_in_it(self):
        """`phi-scan: synthetic`'s own-line rule, adopted for the reason it was added
        there: a bare substring test let two files exempt themselves just by
        explaining the pragma."""
        mentioned = row(snippet=f"a row may declare {gate.RENDERED_MARKER} to opt out, <130")
        _, _, rendered = gate.gate_citation_tier2(sheet(mentioned), Path(__file__).parent)
        self.assertEqual(rendered, 0)

    def test_tier_one_still_grades_a_declared_row(self):
        """The hatch buys out of tier 2 only. A value whose number is absent from its
        own snippet is still a refusal, because that check needs no page at all."""
        marked = row(value="<140 mm Hg", snippet=f"{gate.RENDERED_MARKER} a goal of <130 mm Hg")
        self.assertEqual(len(gate.gate_citation_tier1(sheet(marked))), 1)


class TheGraderMatchesTheFormatItDocuments(unittest.TestCase):
    """`test_spelling_scan.py`'s reasoning: a checker that has drifted from the file a
    reader opens is worse than none, because it reads as agreement."""

    def test_the_readme_names_every_section_the_parser_reads(self):
        readme = (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")
        for section in ("## Sources", "## Scope", "## Populations", "## Thresholds",
                        "## Conflicts", "## Coverage"):
            self.assertIn(f"### `{section}`", readme, f"{section} is not documented")

    def test_the_readme_states_the_schema_marker_the_parser_requires(self):
        readme = (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(gate.SCHEMA_MARKER, readme)

    def test_the_readme_still_names_the_two_citation_tiers(self):
        readme = (gate.SHEET_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("tier", readme.lower())
        self.assertIn("everywhere", readme)


if __name__ == "__main__":
    unittest.main()
