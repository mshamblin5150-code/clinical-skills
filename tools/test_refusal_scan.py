"""Behavior tests for ``refusal_scan`` at its command-line seam."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import refusal_scan as scan
from grader_conformance import for_module

GraderConformance = for_module(scan)


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL = REPO_ROOT / "skills" / "icd10-cpt" / "SKILL.md"
ASSERTIONS = REPO_ROOT / "fixtures" / "filled-anchor" / "assertions.md"
RUN_README = REPO_ROOT / "fixtures" / "filled-anchor" / "run-2" / "README.md"
EXPECTED_VECTOR = "6, 1, 1, 3, 3, 1, 9, 8, 3, 8, 2, 7"


def worksheet(*blocks: str) -> str:
    proposed = """--- PROPOSED CODES ---
ICD-10  M79.604  Pain in right leg
  ANCHOR: "right leg pain"
  SPECIFICITY: complete - site and laterality stated
  CONFIDENCE: verified against ICD-10-CM FY2026
"""
    differential = """--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---
ICD-10  M86.9  Osteomyelitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
"""
    refusal = "\n\n".join(blocks)
    return f"""{proposed}
{differential}
--- NOT CODED, NOTHING ESTABLISHED IT ---
{refusal}

--- E/M LEVEL ---
not requested
"""


def refusal(
    code: str = "M86.9",
    descriptor: str = "Osteomyelitis, unspecified",
    needs: str | None = "a resulted film or bone biopsy",
    substitute: str | None = "M79.604  Pain in right leg",
) -> str:
    lines = [
        "Contiguous osteomyelitis, suspected from a chronic wound",
        f"  NOT CODED: {code}  {descriptor}",
    ]
    if needs is not None:
        lines.append(f"  needs: {needs}")
    if substitute is not None:
        lines.append(f"  proposed instead: {substitute}")
    return "\n".join(lines)


class TheParserReadsOnlyTheStepFourBlock(unittest.TestCase):
    def test_a_complete_refusal_is_clean(self):
        sheet = scan.read_worksheet(worksheet(refusal()))
        self.assertEqual(len(sheet.refusals), 1)
        self.assertEqual(scan.worksheet_findings(sheet), [])

    def test_a_differential_not_coded_mark_is_not_a_refusal(self):
        text = worksheet(refusal()).replace(
            "ICD-10  M86.9  Osteomyelitis, unspecified   NOT FOR ENTRY",
            "ICD-10  M86.9  Osteomyelitis, unspecified   NOT FOR ENTRY\n"
            "  NOT CODED: J15.7  Pneumonia due to Mycoplasma pneumoniae",
        )
        self.assertEqual(len(scan.read_worksheet(text).refusals), 1)

    def test_the_block_ends_at_the_next_heading(self):
        text = worksheet(refusal()) + "\nNOT CODED: J15.7  Pneumonia due to Mycoplasma pneumoniae\n"
        self.assertEqual(len(scan.read_worksheet(text).refusals), 1)

    def test_a_mark_with_wrapped_fields_stays_one_refusal(self):
        text = worksheet(
            "Contiguous osteomyelitis, suspected from a chronic wound\n"
            "  NOT CODED: M86.9  Osteomyelitis, unspecified\n"
            "  needs: a film that resulted, or a bone\n"
            "    biopsy\n"
            "  proposed instead: M79.604  Pain in right\n"
            "    leg"
        )
        sheet = scan.read_worksheet(text)
        self.assertEqual(len(sheet.refusals), 1)
        self.assertEqual(scan.worksheet_findings(sheet), [])


class EveryRefusalCarriesTheThreeMechanicalParts(unittest.TestCase):
    def test_a_worksheet_missing_the_block_fails(self):
        sheet = scan.read_worksheet("--- PROPOSED CODES ---\nICD-10  I10  Essential hypertension\n")
        self.assertEqual(
            [finding.kind for finding in scan.worksheet_findings(sheet)],
            [scan.MISSING_BLOCK],
        )

    def test_a_missing_needs_line_fails(self):
        sheet = scan.read_worksheet(worksheet(refusal(needs=None)))
        self.assertEqual(
            [finding.kind for finding in scan.worksheet_findings(sheet)],
            [scan.MISSING_NEEDS],
        )

    def test_a_mark_without_a_descriptor_is_malformed(self):
        text = worksheet(refusal()).replace(
            "NOT CODED: M86.9  Osteomyelitis, unspecified",
            "NOT CODED: M86.9",
        )
        sheet = scan.read_worksheet(text)
        self.assertEqual(
            [finding.kind for finding in scan.worksheet_findings(sheet)],
            [scan.MALFORMED_MARK],
        )

    def test_a_missing_substitute_fails(self):
        sheet = scan.read_worksheet(worksheet(refusal(substitute=None)))
        self.assertEqual(
            [finding.kind for finding in scan.worksheet_findings(sheet)],
            [scan.MISSING_SUBSTITUTE],
        )

    def test_a_refused_code_proposed_for_entry_fails(self):
        sheet = scan.read_worksheet(worksheet(refusal(code="M79.604", descriptor="Pain in right leg")))
        self.assertEqual(
            [finding.kind for finding in scan.worksheet_findings(sheet)],
            [scan.PROPOSED_AND_REFUSED],
        )

    def test_the_same_code_in_the_differential_is_allowed(self):
        sheet = scan.read_worksheet(worksheet(refusal()))
        self.assertIn("M86.9", sheet.differential)
        self.assertEqual(scan.worksheet_findings(sheet), [])


class TheCommandReportsWhetherItScanned(unittest.TestCase):
    def run_over(self, files: dict[str, str], *args: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw) / "run"
            directory.mkdir()
            for name, text in files.items():
                (directory / name).write_text(text, encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                status = scan.main([str(directory), *args])
            return status, output.getvalue()

    def test_a_clean_run_exits_zero(self):
        self.assertEqual(self.run_over({"case-01.md": worksheet(refusal())})[0], 0)

    def test_a_violation_exits_one(self):
        self.assertEqual(
            self.run_over({"case-01.md": worksheet(refusal(needs=None))})[0],
            1,
        )

    def test_no_refusals_is_unscanned(self):
        self.assertEqual(self.run_over({"case-01.md": worksheet()})[0], 2)

    def test_a_missing_directory_is_unscanned(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "absent"
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(scan.main([str(path)]), 2)
            self.assertNotIn(str(path), output.getvalue())
            self.assertIn("absent", output.getvalue())

    def test_a_mistyped_flag_is_refused_before_the_directory_is_read(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw) / "run"
            directory.mkdir()
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                status = scan.main([str(directory), "--shwo"])

        self.assertEqual(2, status)
        self.assertIn("unrecognized option --shwo", stderr.getvalue())

    def test_default_output_names_no_code(self):
        status, report = self.run_over({"case-01.md": worksheet(refusal())})
        self.assertEqual(status, 0)
        self.assertNotIn("M86.9", report)
        self.assertIn("refusal records", report)
        self.assertIn("records per worksheet             1", report)

    def test_show_names_the_code(self):
        _, report = self.run_over(
            {"case-01.md": worksheet(refusal(needs=None))}, "--show"
        )
        self.assertIn("M86.9", report)

    def test_a_readme_is_not_a_worksheet(self):
        status, report = self.run_over(
            {
                "case-01.md": worksheet(refusal()),
                "README.md": worksheet(refusal(code="J15.7")),
            }
        )
        self.assertEqual(status, 0)
        self.assertIn("worksheets                       1", report)


class TheCommittedRunPinsTheWalkedRow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = REPO_ROOT / "fixtures" / "filled-anchor" / "run-2"
        cls.scan = scan.survey(
            [scan.read_worksheet(text) for text in scan.read_worksheets(directory)]
        )

    def test_all_twelve_worksheets_carry_the_block(self):
        self.assertEqual(self.scan.worksheets, 12)
        self.assertEqual(self.scan.with_block, 12)

    def test_the_per_case_refusal_counts_are_pinned(self):
        self.assertEqual(self.scan.per_worksheet, (6, 1, 1, 3, 3, 1, 9, 8, 3, 8, 2, 7))
        self.assertEqual(self.scan.refusals, 52)

    def test_the_walked_row_is_clean(self):
        self.assertEqual(self.scan.findings, ())

    def test_both_prose_surfaces_carry_the_pinned_vector(self):
        for path in (ASSERTIONS, RUN_README):
            with self.subTest(path=path):
                self.assertIn(EXPECTED_VECTOR, path.read_text(encoding="utf-8"))


class TheSkillStillStatesTheRow(unittest.TestCase):
    def test_step_four_requires_all_three_fields(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("NOT CODED: <code and official descriptor>", text)
        self.assertIn("needs: <the result that would establish it>", text)
        self.assertIn("proposed instead: <the code the encounter does document>", text)


if __name__ == "__main__":
    unittest.main()
