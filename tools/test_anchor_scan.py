"""Cover ``anchor_scan``'s parser against synthetic worksheets.

Every worksheet here is written in this file, on ``test_specificity_scan``'s
reasoning and for its reason: the parser has to be exercised against shapes no
committed run happens to contain, including the two shapes that must *not* read
as a pass -- the pre-[#46] heading, and a code named in prose inside the block.

``TheSkillSaysWhatThisChecks`` is the one test that reads a committed file, and
it is there for ``test_spelling_scan``'s reason: a scanner that has drifted from
the file a reader opens is worse than none, because it reads as agreement.
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import anchor_scan as scan

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "icd10-cpt" / "SKILL.md"

BLOCK = "--- CODED, ANCHOR WAS FILLED - CONFIRM BEFORE SUBMITTING ---"
OLD_BLOCK = "--- NOT CODED, ANCHOR WAS FILLED ---"


def entry(code: str, descriptor: str, source: str | None = None,
          confidence: str = "verified against ICD-10-CM FY2026") -> str:
    lines = [f"ICD-10  {code}  {descriptor}", '  ANCHOR: "the note text"']
    if source is not None:
        lines.append(f"  SOURCE: {source}")
    lines += [
        "  SPECIFICITY: complete - no further axis",
        f"  CONFIDENCE: {confidence}",
    ]
    return "\n".join(lines)


def worksheet(entries: str = "", block: str | None = None,
              heading: str = BLOCK) -> str:
    text = "--- PROPOSED CODES ---\n\n" + entries + "\n\n"
    if block is not None:
        text += f"{heading}\n{block}\n\n"
    text += "--- NOT CODED, NOTHING ESTABLISHED IT ---\nnothing\n"
    return text


class TheParserFindsMarkedCodes(unittest.TestCase):
    def test_a_source_line_marks_the_entry_above_it(self):
        sheet = scan.read_worksheet(
            worksheet(entry("Z68.36", "Body mass index [BMI] 36.0-36.9, adult",
                            source="filled - height; confirm before submitting"))
        )
        self.assertEqual(sheet.marked, frozenset({"Z68.36"}))

    def test_an_entry_without_a_source_line_is_not_marked(self):
        sheet = scan.read_worksheet(worksheet(entry("I10", "Essential (primary) hypertension")))
        self.assertEqual(sheet.marked, frozenset())
        self.assertEqual(sheet.proposed, 1)

    def test_a_source_line_that_does_not_say_filled_does_not_mark(self):
        sheet = scan.read_worksheet(
            worksheet(entry("I10", "Essential (primary) hypertension", source="recorded"))
        )
        self.assertEqual(sheet.marked, frozenset())

    def test_a_wrapped_descriptor_still_carries_its_not_for_entry_mark(self):
        # ``K27.9 Peptic ulcer, site unspecified, unspecified as acute or chronic,
        # without hemorrhage or perforation`` does not fit a line, so the mark lands
        # on the continuation. A single-line reading calls it a proposed code and
        # publishes a differential count four short -- which is what it did.
        wrapped = (
            "ICD-10  K27.9  Peptic ulcer, site unspecified, unspecified as acute or chronic, without\n"
            "               hemorrhage or perforation   NOT FOR ENTRY\n"
            "  CONFIDENCE: verified against ICD-10-CM FY2026\n"
        )
        sheet = scan.read_worksheet(wrapped)
        self.assertEqual(sheet.proposed, 0)

    def test_the_mark_is_not_read_out_of_the_next_entry(self):
        # The span stops at the next entry, so a for-entry code immediately above a
        # differential one does not borrow its mark.
        pair = (
            "ICD-10  I10  Essential (primary) hypertension\n"
            "ICD-10  J20.9  Acute bronchitis, unspecified   NOT FOR ENTRY\n"
        )
        self.assertEqual(scan.read_worksheet(pair).proposed, 1)

    def test_the_mark_is_not_read_out_of_a_later_field_line(self):
        # A field line closes the span, so prose about the rule beneath a code does
        # not silently exempt it.
        prose = (
            "ICD-10  I10  Essential (primary) hypertension\n"
            "  SPECIFICITY: complete - no further axis\n"
            "  NOTE: the differential codes below are all NOT FOR ENTRY\n"
        )
        self.assertEqual(scan.read_worksheet(prose).proposed, 1)

    def test_a_differential_entry_is_not_a_proposed_code(self):
        differential = (
            "--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---\n"
            "ICD-10  J20.9  Acute bronchitis, unspecified   NOT FOR ENTRY\n"
            "  CONFIDENCE: verified against ICD-10-CM FY2026\n"
        )
        sheet = scan.read_worksheet(differential)
        self.assertEqual(sheet.proposed, 0)
        self.assertEqual(sheet.marked, frozenset())


class TheParserReadsTheStepFourBlock(unittest.TestCase):
    def test_it_reads_a_code_pinned_by_a_dash(self):
        sheet = scan.read_worksheet(worksheet(block="Z68.36 - BMI 36.4 from a filled height"))
        self.assertEqual(sheet.listed, frozenset({"Z68.36"}))

    def test_it_reads_an_em_dash_and_a_bullet_and_bold(self):
        block = (
            "Z68.36 — BMI 36.4 from a filled height\n"
            "- E66.3 – overweight, from a filled height\n"
            "**R03.0** - elevated reading, filled pressure\n"
        )
        sheet = scan.read_worksheet(worksheet(block=block))
        self.assertEqual(sheet.listed, frozenset({"Z68.36", "E66.3", "R03.0"}))

    def test_it_reads_a_cpt_code(self):
        # A CPT code is five digits and matches nothing an ICD-10 pattern accepts.
        # ``icd10-cpt`` step 3 says CPT entries take the same shape, so a filled-
        # anchored one owes the same listing.
        sheet = scan.read_worksheet(worksheet(block="99406 - cessation counseling, a filled plan item"))
        self.assertEqual(sheet.listed, frozenset({"99406"}))

    def test_it_reads_a_listing_that_names_its_code_set(self):
        block = (
            "CPT 12001 - the simple designation rests on a filled exploration\n"
            "ICD-10 Z68.36 - BMI 36.4 from a filled height\n"
        )
        sheet = scan.read_worksheet(worksheet(block=block))
        self.assertEqual(sheet.listed, frozenset({"12001", "Z68.36"}))

    def test_a_marked_cpt_code_listed_in_the_block_is_clean(self):
        sheet = scan.read_worksheet(
            worksheet(
                "CPT  99406  Smoking and tobacco use cessation counseling visit\n"
                '  ANCHOR: "the note text"\n'
                "  SOURCE: filled - the counseling is a proposed plan item\n"
                "  SPECIFICITY: complete - time documented\n"
                "  CONFIDENCE: verify this number",
                block="99406 - cessation counseling, a filled plan item",
            )
        )
        self.assertEqual(scan.worksheet_findings(sheet), [])

    def test_a_measurement_at_the_start_of_a_line_is_not_a_code(self):
        # The block's tail often accounts for filled values that support no code.
        block = "RR 18 - upper-normal, so no R06.82\nHt 5'10\" and Wt 198 lb - they support no code\n"
        sheet = scan.read_worksheet(worksheet(block=block))
        self.assertEqual(sheet.listed, frozenset())

    def test_a_code_named_in_prose_inside_the_block_is_not_a_listing(self):
        # fixtures/filled-anchor assertions.md, *Still unresolved*: a run can write
        # the code into the block in a sentence, which puts the string exactly where
        # a substring search looks. The block's own line format is the test.
        block = "Z68.25 needs no SOURCE line, the inputs were given\n"
        sheet = scan.read_worksheet(worksheet(block=block))
        self.assertEqual(sheet.listed, frozenset())

    def test_the_block_ends_at_the_next_heading(self):
        sheet = scan.read_worksheet(worksheet(block="Z68.36 - BMI 36.4 from a filled height"))
        # ``NOT CODED, NOTHING ESTABLISHED IT`` follows the block in ``worksheet``.
        self.assertEqual(sheet.listed, frozenset({"Z68.36"}))

    def test_the_pre_46_heading_is_not_this_block(self):
        # Run 1 refused every filled anchor and wrote them under the old heading.
        # Reading that as the new block would score the superseded behavior as a pass.
        sheet = scan.read_worksheet(
            worksheet(block="Z68.36 - BMI 36.4 from a filled height", heading=OLD_BLOCK)
        )
        self.assertEqual(sheet.listed, frozenset())
        self.assertFalse(sheet.has_block)


class TheMarkAndTheListingMustAgree(unittest.TestCase):
    def test_a_marked_and_listed_code_is_clean(self):
        sheet = scan.read_worksheet(
            worksheet(
                entry("Z68.36", "Body mass index [BMI] 36.0-36.9, adult", source="filled - height"),
                block="Z68.36 - BMI 36.4 from a filled height",
            )
        )
        self.assertEqual(scan.worksheet_findings(sheet), [])

    def test_a_marked_code_absent_from_the_block_fails(self):
        sheet = scan.read_worksheet(
            worksheet(
                entry("Z68.36", "Body mass index [BMI] 36.0-36.9, adult", source="filled - height"),
                block="E66.3 - overweight",
            )
        )
        kinds = [f.kind for f in scan.worksheet_findings(sheet)]
        self.assertIn(scan.UNLISTED_MARK, kinds)

    def test_a_listed_code_carrying_no_source_line_fails(self):
        sheet = scan.read_worksheet(
            worksheet(
                entry("Z68.36", "Body mass index [BMI] 36.0-36.9, adult"),
                block="Z68.36 - BMI 36.4 from a filled height",
            )
        )
        kinds = [f.kind for f in scan.worksheet_findings(sheet)]
        self.assertIn(scan.UNMARKED_LISTING, kinds)

    def test_a_code_listed_but_never_proposed_fails_the_same_way(self):
        sheet = scan.read_worksheet(worksheet(block="Z68.36 - BMI 36.4 from a filled height"))
        kinds = [f.kind for f in scan.worksheet_findings(sheet)]
        self.assertEqual(kinds, [scan.UNMARKED_LISTING])


class ThePediatricBandIsComputed(unittest.TestCase):
    def test_a_z68_5_claiming_verification_is_clean(self):
        sheet = scan.read_worksheet(
            worksheet(
                entry("Z68.52", "Body mass index [BMI] pediatric, 5th percentile to less than"
                      " 85th percentile for age", source="filled - height and weight",
                      confidence="verified against ICD-10-CM FY2026 and CDC 2022 "
                      "Extended BMI-for-Age"),
                block="Z68.52 - BMI 23.0 from a filled height and weight",
            )
        )
        self.assertEqual(scan.worksheet_findings(sheet), [])

    def test_a_z68_5_still_saying_verify_this_number_fails(self):
        sheet = scan.read_worksheet(
            worksheet(
                entry("Z68.52", "Body mass index [BMI] pediatric, 5th percentile to less than"
                      " 85th percentile for age", confidence="verify this number")
            )
        )
        kinds = [finding.kind for finding in scan.worksheet_findings(sheet)]
        self.assertEqual(kinds, [scan.PEDIATRIC_NOT_COMPUTED])

    def test_naming_an_unavailable_cdc_table_is_not_computation(self):
        sheet = scan.read_worksheet(
            worksheet(
                entry("Z68.52", "Body mass index [BMI] pediatric, 5th percentile to less than"
                      " 85th percentile for age", confidence="verify this number - CDC 2022 "
                      "Extended BMI-for-Age was unavailable")
            )
        )
        kinds = [finding.kind for finding in scan.worksheet_findings(sheet)]
        self.assertEqual(kinds, [scan.PEDIATRIC_NOT_COMPUTED])

    def test_each_duplicate_code_entry_needs_its_own_computation(self):
        descriptor = "Body mass index [BMI] pediatric, 5th percentile to less than 85th percentile for age"
        entries = "\n\n".join(
            (
                entry("Z68.52", descriptor, confidence="verified against ICD-10-CM FY2026 and "
                      "CDC 2022 Extended BMI-for-Age"),
                entry("Z68.52", descriptor, confidence="verify this number"),
            )
        )
        sheet = scan.read_worksheet(worksheet(entries))
        self.assertEqual(sheet.pediatric, ("Z68.52", "Z68.52"))
        self.assertEqual(len(scan.worksheet_findings(sheet)), 1)

    def test_a_computed_band_alone_counts_as_something_scanned(self):
        sheet = scan.read_worksheet(
            worksheet(
                entry("Z68.52", "Body mass index [BMI] pediatric, 5th percentile to less than"
                      " 85th percentile for age", confidence="verified against ICD-10-CM "
                      "FY2026 and CDC 2022 Extended BMI-for-Age")
            )
        )
        self.assertEqual(scan.survey([sheet]).subjects, 1)

    def test_an_adult_band_may_claim_the_lookup(self):
        sheet = scan.read_worksheet(
            worksheet(
                entry("Z68.36", "Body mass index [BMI] 36.0-36.9, adult", source="filled - height"),
                block="Z68.36 - BMI 36.4 from a filled height",
            )
        )
        self.assertEqual(scan.worksheet_findings(sheet), [])


class TheReportCarriesNoCode(unittest.TestCase):
    def setUp(self):
        sheet = scan.read_worksheet(
            worksheet(
                entry("Z68.36", "Body mass index [BMI] 36.0-36.9, adult"),
                block="Z68.36 - BMI 36.4 from a filled height",
            )
        )
        self.survey = scan.survey([sheet])

    def test_the_default_report_names_no_code(self):
        report = scan.format_report(self.survey, source="run")
        self.assertNotIn("Z68.36", report)
        self.assertIn("1", report)

    def test_show_names_the_code(self):
        report = scan.format_report(self.survey, source="run", show=True)
        self.assertIn("Z68.36", report)


class TheExitStatusSaysWhetherAnythingWasScanned(unittest.TestCase):
    def run_over(self, files: dict[str, str], *args: str) -> int:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw) / "run"
            directory.mkdir()
            for name, text in files.items():
                (directory / name).write_text(text, encoding="utf-8")
            return scan.main([str(directory), *args])

    def test_no_argument_is_two(self):
        self.assertEqual(scan.main([]), 2)

    def test_a_missing_directory_is_two(self):
        with tempfile.TemporaryDirectory() as raw:
            self.assertEqual(scan.main([str(Path(raw) / "absent")]), 2)

    def test_an_empty_directory_is_two(self):
        self.assertEqual(self.run_over({}), 2)

    def test_a_run_that_marked_nothing_is_two_rather_than_clean(self):
        # The shape run 1 had. Nothing to grade is not the same as nothing wrong.
        output = io.StringIO()
        with redirect_stdout(output):
            status = self.run_over(
                {"case-01.md": worksheet(entry("I10", "Essential (primary) hypertension"))}
            )
        self.assertEqual(status, 2)
        self.assertIn("anchor scan over run", output.getvalue())

    def test_the_old_heading_alone_is_two(self):
        self.assertEqual(
            self.run_over(
                {"case-01.md": worksheet(block="Z68.36 - BMI 36.4", heading=OLD_BLOCK)}
            ),
            2,
        )

    def test_a_clean_run_is_zero(self):
        self.assertEqual(
            self.run_over(
                {
                    "case-01.md": worksheet(
                        entry("Z68.36", "Body mass index [BMI] 36.0-36.9, adult",
                              source="filled - height"),
                        block="Z68.36 - BMI 36.4 from a filled height",
                    )
                }
            ),
            0,
        )

    def test_a_violation_is_one(self):
        self.assertEqual(
            self.run_over(
                {
                    "case-01.md": worksheet(
                        entry("Z68.36", "Body mass index [BMI] 36.0-36.9, adult",
                              source="filled - height"),
                        block="E66.3 - overweight",
                    )
                }
            ),
            1,
        )

    def test_a_readme_is_not_a_worksheet(self):
        clean = worksheet(
            entry("Z68.36", "Body mass index [BMI] 36.0-36.9, adult", source="filled - height"),
            block="Z68.36 - BMI 36.4 from a filled height",
        )
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw) / "run"
            directory.mkdir()
            (directory / "case-01.md").write_text(clean, encoding="utf-8")
            (directory / "README.md").write_text(
                "Prose about the run, naming Z68.99 - a code in a sentence\n", encoding="utf-8"
            )
            texts = scan.read_worksheets(directory)
        self.assertEqual(len(texts), 1)


class TheCommittedRunsFiguresArePinned(unittest.TestCase):
    """Pin the figures ``fixtures/filled-anchor/run-2/README.md`` publishes.

    **This is not the scanner being graded against the run, and the difference is
    the whole reason it is allowed here.** Every test above builds its own
    worksheet, because a test that read the run this scanner's own row graded would
    pass for two reasons and one of them is that the run and the scanner are wrong
    together. What this class does instead is ``test_spelling_scan``'s move: a
    figure published in prose goes stale silently, so the file that states it fails
    a test rather than quietly voiding its own argument.
    """

    @classmethod
    def setUpClass(cls):
        cls.directory = REPO_ROOT / "fixtures" / "filled-anchor" / "run-2"
        cls.scan = scan.survey(
            [scan.read_worksheet(text) for text in scan.read_worksheets(cls.directory)]
        )

    def test_twelve_worksheets(self):
        self.assertEqual(self.scan.worksheets, 12)

    def test_two_hundred_and_ten_codes_proposed_for_entry(self):
        # 297 entries less the 87 marked ``NOT FOR ENTRY``. **This read 214 until a
        # reader found the four whose descriptors wrap**, and the suite was green
        # over the wrong number the whole time -- which is what a figure pinned to a
        # parser buys and does not buy.
        self.assertEqual(self.scan.proposed, 210)

    def test_twenty_nine_marks_and_twenty_nine_listings(self):
        # The two being equal is A1/A2/A5's mechanical limb; the value being 29 is
        # the figure the README states.
        self.assertEqual(self.scan.marked, 29)
        self.assertEqual(self.scan.listed, 29)

    def test_every_worksheet_carries_the_step_four_block(self):
        self.assertEqual(self.scan.with_block, 12)

    def test_the_preserved_run_exposes_its_two_pre_calculator_bands(self):
        # The run is byte-for-byte evidence from before #123. Rewriting its two
        # recalled Z68.52 entries would falsify that record; the replacement A1
        # check must therefore find both rather than bless or mutate them.
        self.assertEqual(self.scan.pediatric_bands, 2)
        self.assertEqual(self.scan.pediatric_not_computed, 2)
        self.assertEqual(
            {finding.kind for finding in self.scan.findings},
            {scan.PEDIATRIC_NOT_COMPUTED},
        )


class TheSkillSaysWhatThisChecks(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")

    def test_the_skill_still_requires_both_the_mark_and_the_listing(self):
        self.assertIn("SOURCE: filled", self.text)
        self.assertIn("CODED, ANCHOR WAS FILLED", self.text)
        self.assertIn("Both, not one instead of the other", self.text)

    def test_the_skill_sends_the_pediatric_band_to_the_cdc_tool(self):
        self.assertIn("cdc_percentile.py", self.text)


if __name__ == "__main__":
    unittest.main()
