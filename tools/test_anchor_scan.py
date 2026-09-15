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
import json
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import anchor_scan as scan
import run_grader
from grader_conformance import (
    EmptyPopulationInput,
    UnreadRemainderInput,
    for_module,
    unread_remainder_conformance,
)
from prose_bind import NAMING, bind, section

GraderConformance = for_module(scan)

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "icd10-cpt" / "SKILL.md"
POSITIVE_RUN = REPO_ROOT / "fixtures" / "worksheet-grammar-positive-control"
POSITIVE_SOURCE = REPO_ROOT / "fixtures" / "filled-anchor" / "notes" / "case-01.md"

BLOCK = "--- CODED, ANCHOR WAS FILLED - CONFIRM BEFORE SUBMITTING ---"
OLD_BLOCK = "--- NOT CODED, ANCHOR WAS FILLED ---"


class TheDeclaredLimitsObjectOwnsBothProseSurfaces(unittest.TestCase):
    POINTER = "anchor_scan.DECLARED_LIMITS"

    def test_docstring_and_claude_section_each_point_once_without_copying_rows(self):
        claude = section((REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8"), "### Anchor scan")
        for surface in (scan.__doc__ or "", claude):
            with self.subTest(surface=surface[:40]):
                self.assertEqual(1, surface.count(self.POINTER))
                self.assertEqual((), bind(scan.DECLARED_LIMITS, surface, mode=NAMING))

    def test_the_partition_is_two_declared_readings_and_nine_behaviors(self):
        dispositions = [row[2] for row in scan.DECLARED_LIMITS]
        self.assertEqual(2, dispositions.count(run_grader.EvidenceDisposition.DECLARED_READING))
        self.assertEqual(9, dispositions.count(run_grader.EvidenceDisposition.BEHAVIOR))
        self.assertTrue(all(subject and reason for subject, reason, _ in scan.DECLARED_LIMITS))


class EveryBehaviorLimitHasALiveControl(unittest.TestCase):
    CONTROLS = {
        "NOT FOR ENTRY entries": "TheParserFindsMarkedCodes.test_a_differential_entry_is_not_a_proposed_code",
        "recognized filled-anchor listing lines": "DeclaredLimitBoundaryControls.test_a_table_listing_is_unread_beside_the_code_dash_form",
        "recognized SOURCE marks": "DeclaredLimitBoundaryControls.test_only_a_value_beginning_with_filled_marks_the_code",
        "filled-anchor block closing headings": "DeclaredLimitBoundaryControls.test_a_subheading_ends_the_filled_anchor_block",
        "filled-anchor block opening form": "DeclaredLimitBoundaryControls.test_only_the_delimited_line_opens_the_filled_anchor_block",
        "contiguous indented detail pairing": "DeclaredLimitBoundaryControls.test_a_blank_line_orphans_a_recognized_source",
        "pediatric-band computation": "DeclaredLimitBoundaryControls.test_the_required_sentence_is_not_a_recomputation",
        "per-run gradeable coverage": "DeclaredLimitBoundaryControls.test_an_unread_worksheet_adds_nothing_beside_a_readable_one",
        "E/M descriptor agreement": "TheReportCarriesNoCode.test_every_report_prints_the_excluded_em_count",
    }

    def test_each_behavior_subject_names_a_passing_control(self):
        behavior = {subject for subject, _, disposition in scan.DECLARED_LIMITS if disposition is run_grader.EvidenceDisposition.BEHAVIOR}
        self.assertEqual(behavior, set(self.CONTROLS))
        for subject, name in self.CONTROLS.items():
            result = unittest.TestResult()
            unittest.defaultTestLoader.loadTestsFromName(f"test_anchor_scan.{name}").run(result)
            self.assertTrue(result.wasSuccessful(), f"{subject}: {result.errors + result.failures}")


class DeclaredLimitBoundaryControls(unittest.TestCase):
    def test_an_unrecognized_code_and_source_form_contributes_nothing(self):
        unread = scan.read_worksheet(
            "- ICD-10  J02.9  Acute pharyngitis, unspecified\n"
            "  **SOURCE:** filled\n"
        )
        self.assertEqual((0, frozenset()), (unread.proposed, unread.marked))
        self.assertEqual(1, unread.unread_remainder)

    def test_a_table_listing_is_unread_beside_the_code_dash_form(self):
        table = scan.read_worksheet(worksheet(block="| Z68.36 | BMI 36.4 |"))
        line = scan.read_worksheet(worksheet(block="Z68.36 - BMI 36.4"))
        self.assertEqual(frozenset(), table.listed)
        self.assertEqual(frozenset({"Z68.36"}), line.listed)

    def test_a_bold_source_label_does_not_mark_the_code(self):
        text = entry("Z68.36", "Adult BMI", source="filled").replace("SOURCE:", "**SOURCE:**")
        self.assertEqual(frozenset(), scan.read_worksheet(text).marked)

    def test_only_a_value_beginning_with_filled_marks_the_code(self):
        affirmative = scan.read_worksheet(entry("Z68.36", "Adult BMI", source="filled - height"))
        negated = scan.read_worksheet(entry("Z68.36", "Adult BMI", source="recorded, not filled"))
        self.assertEqual(frozenset({"Z68.36"}), affirmative.marked)
        self.assertEqual((frozenset(), 1), (negated.marked, negated.orphaned_details))

    def test_a_subheading_ends_the_filled_anchor_block(self):
        sheet = scan.read_worksheet(
            f"{BLOCK}\n### Adult BMI band\nZ68.36 - BMI 36.4\n"
        )
        self.assertEqual(frozenset(), sheet.listed)

    def test_only_the_delimited_line_opens_the_filled_anchor_block(self):
        prose = scan.read_worksheet(
            "Accounting note names CODED, ANCHOR WAS FILLED for review.\n"
            "Z68.36 - BMI 36.4\n"
        )
        prefixed = scan.read_worksheet(
            "### --- CODED, ANCHOR WAS FILLED - CONFIRM BEFORE SUBMITTING ---\n"
            "Z68.36 - BMI 36.4\n"
        )
        delimited = scan.read_worksheet(f"{BLOCK}\nZ68.36 - BMI 36.4\n")
        self.assertEqual((frozenset(), False), (prose.listed, prose.has_block))
        self.assertEqual((frozenset(), False), (prefixed.listed, prefixed.has_block))
        self.assertEqual((frozenset({"Z68.36"}), True), (delimited.listed, delimited.has_block))

    def test_an_unrecognized_block_is_reported_without_inventing_listing_findings(self):
        sheet = scan.read_worksheet(
            entry("Z68.36", "Adult BMI", source="filled - height")
            + "### --- CODED, ANCHOR WAS FILLED - CONFIRM BEFORE SUBMITTING ---\n"
            + "Z68.36 - BMI 36.4\n"
        )

        self.assertFalse(sheet.has_block)
        self.assertEqual([], scan.worksheet_findings(sheet))

    def test_a_blank_line_orphans_a_recognized_source(self):
        sheet = scan.read_worksheet(
            "ICD-10  Z68.36  Adult BMI\n\n  SOURCE: filled - height\n"
        )
        self.assertEqual((frozenset(), 1), (sheet.marked, sheet.orphaned_details))

    def test_the_required_sentence_is_not_a_recomputation(self):
        text = entry(
            "Z68.54",
            "Pediatric BMI above the 95th percentile",
            confidence="verified against ICD-10-CM FY2026 and CDC 2022 Extended BMI-for-Age",
        )
        result = scan.read_worksheet(text)
        self.assertEqual((), tuple(result.pediatric_not_computed))

    def test_an_unread_worksheet_adds_nothing_beside_a_readable_one(self):
        readable = scan.read_worksheet(
            worksheet(entry("I10", "Hypertension", source="filled"), block="I10 - filled pressure")
        )
        result = scan.survey([readable, scan.read_worksheet(worksheet())])
        self.assertEqual(2, result.worksheets)
        self.assertEqual(2, result.subjects)


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


def empty_population_input(root: Path) -> EmptyPopulationInput:
    empty, twin = root / "empty", root / "twin"
    empty.mkdir()
    twin.mkdir()
    (empty / "codes.md").write_text(worksheet(), encoding="utf-8")
    (twin / "codes.md").write_text(
        worksheet(
            entry(
                "Z68.52",
                "Body mass index [BMI] pediatric, 5th percentile to less than 85th percentile for age",
                confidence=(
                    "verified against ICD-10-CM FY2026 and CDC 2022 Extended BMI-for-Age"
                ),
            )
        ),
        encoding="utf-8",
    )
    return EmptyPopulationInput(
        (str(empty),),
        population_size=lambda result: result.subjects,
        twin_argv=(str(twin),),
    )


def unread_remainder_input(root: Path) -> UnreadRemainderInput:
    unread, twin = root / "unread", root / "twin"
    unread.mkdir()
    twin.mkdir()
    unread_text = worksheet(
        entry("I10", "Hypertension", source="filled")
        + "\n- ICD-10 R12 Heartburn\n  - **SOURCE:** filled\n",
        block="I10 - filled pressure",
    )
    twin_text = worksheet(
        entry("I10", "Hypertension", source="filled"),
        block="I10 - filled pressure",
    )
    (unread / "codes.md").write_text(unread_text, encoding="utf-8")
    (twin / "codes.md").write_text(twin_text, encoding="utf-8")
    return UnreadRemainderInput(
        (str(unread),),
        (str(twin),),
        unread_remainder=lambda result: result.unread_remainder,
    )


UnreadRemainderConformance = unread_remainder_conformance(scan)


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

    def test_a_source_line_that_does_not_begin_with_filled_is_an_orphan(self):
        sheet = scan.read_worksheet(
            worksheet(entry("I10", "Essential (primary) hypertension", source="recorded"))
        )
        self.assertEqual(sheet.marked, frozenset())
        self.assertEqual(sheet.orphaned_details, 1)

    def test_a_wrapped_descriptor_still_carries_its_line_scoped_marker(self):
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

    def test_it_reads_each_dash_but_not_a_bullet_or_bold(self):
        block = (
            "Z68.36 — BMI 36.4 from a filled height\n"
            "- E66.3 – overweight, from a filled height\n"
            "**R03.0** - elevated reading, filled pressure\n"
        )
        sheet = scan.read_worksheet(worksheet(block=block))
        self.assertEqual(sheet.listed, frozenset({"Z68.36"}))

    def test_it_refuses_bold_anywhere_in_the_listing_value(self):
        sheet = scan.read_worksheet(
            worksheet(block="Z68.36 - **BMI 36.4** from a filled height")
        )
        self.assertEqual(sheet.listed, frozenset())

    def test_it_reads_a_cpt_code(self):
        # A CPT code is five digits and matches nothing an ICD-10 pattern accepts.
        # ``icd10-cpt`` step 3 says CPT entries take the same shape, so a filled-
        # anchored one owes the same listing.
        sheet = scan.read_worksheet(worksheet(block="99406 - cessation counseling, a filled plan item"))
        self.assertEqual(sheet.listed, frozenset({"99406"}))

    def test_it_refuses_a_listing_that_names_its_code_set(self):
        block = (
            "CPT 12001 - the simple designation rests on a filled exploration\n"
            "ICD-10 Z68.36 - BMI 36.4 from a filled height\n"
        )
        sheet = scan.read_worksheet(worksheet(block=block))
        self.assertEqual(sheet.listed, frozenset())

    def test_a_confidence_line_in_the_not_coded_block_is_outside_pairing(self):
        text = (
            entry("I10", "Hypertension")
            + "\n\n--- NOT CODED, NOTHING ESTABLISHED IT ---\n"
            + "  NOT CODED: 99406  Cessation counseling\n"
            + "  CONFIDENCE: verify this number\n"
        )
        self.assertEqual(0, scan.read_worksheet(text).orphaned_details)

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

    def test_every_report_prints_the_excluded_em_count(self):
        sheet = scan.read_worksheet("E/M: 99214 Office visit\n" + worksheet())

        self.assertIn("E/M lines excluded", scan.format_report(scan.survey([sheet]), "run"))
        self.assertEqual(1, scan.survey([sheet]).excluded_em)


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
            texts = run_grader.read_run_directory(directory)
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
            [scan.read_worksheet(text) for text in run_grader.read_run_directory(cls.directory)]
        )

    def test_twelve_worksheets(self):
        self.assertEqual(self.scan.worksheets, 12)

    def test_two_hundred_and_nine_codes_proposed_for_entry(self):
        # 296 code-shaped entries less the 87 marked ``NOT FOR ENTRY``. **This read 214 until a
        # reader found the four whose descriptors wrap**, and the suite was green
        # over the wrong number the whole time -- which is what a figure pinned to a
        # parser buys and does not buy.
        self.assertEqual(self.scan.proposed, 209)

    def test_twenty_nine_marks_and_twenty_three_strict_listings(self):
        self.assertEqual(self.scan.marked, 29)
        self.assertEqual(self.scan.listed, 23)

    def test_ten_worksheets_carry_the_strict_step_four_block(self):
        self.assertEqual(self.scan.with_block, 10)

    def test_the_preserved_run_exposes_its_two_pre_calculator_bands(self):
        # The run is byte-for-byte evidence from before #123. Rewriting its two
        # recalled Z68.52 entries would falsify that record; the replacement A1
        # check must therefore find both rather than bless or mutate them.
        self.assertEqual(self.scan.pediatric_bands, 2)
        self.assertEqual(self.scan.pediatric_not_computed, 2)
        self.assertEqual(5, len(self.scan.findings))
        self.assertEqual(3, self.scan.unlisted_marks)
        self.assertEqual(
            {finding.kind for finding in self.scan.findings},
            {scan.UNLISTED_MARK, scan.PEDIATRIC_NOT_COMPUTED},
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

    def test_the_skill_pins_the_narrow_listing_and_line_boundaries(self):
        self.assertIn("carries no code-system token, bullet, or bold markers", self.text)
        self.assertIn("Every field value owns one physical line", self.text)
        self.assertIn("marker refuses this physical line, not the code everywhere", self.text)

    def test_the_differential_template_has_a_home_for_its_reason(self):
        self.assertIn("why that otherwise repeated code belongs in the MDM", self.text)

    def test_a_not_coded_record_may_carry_confidence(self):
        self.assertIn("A `NOT CODED` record may carry", self.text)

    def test_the_skill_carries_the_external_cause_neoplasm_and_drug_rulings(self):
        for phrase in (
            "Section I.C.20",
            "The note chooses the Neoplasm Table column",
            "Section I.C.19.e",
            "hedged self-harm or assault intent",
            "anchor_scan.DECLARED_LIMITS",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)


class ThePositiveControlStaysGradeable(unittest.TestCase):
    def setUp(self):
        self.worksheet = (POSITIVE_RUN / "case-01.md").read_text(encoding="utf-8")

    def test_the_real_generated_worksheet_clears_the_anchor_grammar(self):
        result = scan.survey([scan.read_worksheet(self.worksheet)])

        self.assertEqual(1, result.with_block)
        self.assertEqual((3, 3, 0), (result.marked, result.listed, result.orphaned_details))
        self.assertEqual(0, result.unread_remainder)
        self.assertEqual((), result.findings)

    def test_every_quoted_anchor_is_one_physical_source_line(self):
        source_lines = set(POSITIVE_SOURCE.read_text(encoding="utf-8").splitlines())
        anchors = re.findall(r'(?mi)^[ \t]*ANCHOR[ \t]*:[ \t]*"(.*)"[ \t]*$', self.worksheet)

        self.assertTrue(anchors)
        self.assertTrue(all(any(anchor in line for line in source_lines) for anchor in anchors))

    def test_the_adult_bmi_anchor_carries_both_eligibility_facts(self):
        block = re.search(
            r"(?ms)^ICD-10[ \t]+Z68\.26\b.*?(?=^(?:ICD-10|CPT|HCPCS)[ \t]+|\Z)",
            self.worksheet,
        )
        self.assertIsNotNone(block)
        assert block is not None
        self.assertIn("36-year-old male", block.group())
        self.assertIn("BMI 26.5", block.group())

    def test_the_overweight_anchor_is_a_complete_source_claim(self):
        expected = (
            "BMI 26.5 = 703 x 185 / 70^2 = 130,055 / 4,900 = 26.54. "
            "Overweight band."
        )
        block = re.search(
            r"(?ms)^ICD-10[ \t]+E66\.3\b.*?(?=^(?:ICD-10|CPT|HCPCS)[ \t]+|\Z)",
            self.worksheet,
        )
        self.assertIsNotNone(block)
        assert block is not None
        self.assertIn(f'ANCHOR: "{expected}"', block.group())


AGREEMENT_NOTE = """# Synthetic note

## A:

Occasional heartburn.

**Differential:**
1. Plantar wart - B07.0: focal plantar lesion. Less likely.

**Preexisting diagnoses (ICD10):**
Heartburn **R12**

**Final diagnosis:**
Pain in left toe(s) - **M79.675**

NOT CODED: M86.9 Osteomyelitis, unspecified, no imaging established bone infection.

## Proposed coding worksheet

E/M: 99214 Office visit
CPT: 10060 Incision and drainage of abscess
HCPCS: None
"""

AGREEMENT_WORKSHEET = """--- PROPOSED CODES ---

ICD-10  R12  Heartburn
  ANCHOR: "Occasional heartburn"
  SPECIFICITY: complete - symptom code
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M79.675  Pain in left toe(s)
  ANCHOR: "Pain in left toe(s)"
  SPECIFICITY: complete - left toe documented
  CONFIDENCE: verified against ICD-10-CM FY2026

CPT  10060  Incision and drainage of abscess; simple or single
  ANCHOR: "Incision and drainage of abscess"
  SPECIFICITY: complete - performed today
  CONFIDENCE: verified against CPT Professional 2026

--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

Plantar wart was considered for the focal plantar lesion.
ICD-10  B07.0  Plantar wart  NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

--- NOT CODED, NOTHING ESTABLISHED IT ---

Osteomyelitis was considered but no imaging established bone infection.
  NOT CODED: M86.9  Osteomyelitis, unspecified
  needs: imaging establishing bone infection
  proposed instead: M79.675  Pain in left toe(s)
"""


class AgreementModes(unittest.TestCase):
    def setUp(self):
        self.raw = tempfile.TemporaryDirectory()
        root = Path(self.raw.name)
        self.worksheets = root / "worksheets"
        self.notes = root / "notes"
        self.worksheets.mkdir()
        self.notes.mkdir()
        (self.worksheets / "case-01.md").write_text(AGREEMENT_WORKSHEET, encoding="utf-8")
        (self.notes / "case-01.md").write_text(AGREEMENT_NOTE, encoding="utf-8")

    def tearDown(self):
        self.raw.cleanup()

    def brief(self) -> dict:
        output = io.StringIO()
        with redirect_stdout(output):
            status = scan.main(
                [str(self.worksheets), "--notes", str(self.notes), "--agreement-brief"]
            )
        self.assertEqual(status, 0)
        return json.loads(output.getvalue())

    def clean_record(self) -> dict:
        brief = self.brief()
        records = []
        words = {
            ("entry", "R12"): "heartburn",
            ("entry", "M79.675"): "Pain in left toe(s)",
            ("procedure", "10060"): "Incision and drainage of abscess",
            ("differential", "B07.0"): "Plantar wart",
            ("refused", "M86.9"): "Osteomyelitis",
        }
        for subject in brief["pairs"][0]["codes"]:
            records.append(
                {
                    "subject_id": subject["subject_id"],
                    "system": subject["system"],
                    "code": subject["code"],
                    "role": subject["role"],
                    "agreeing_words": words[(subject["role"], subject["code"])],
                    "route": "descriptor words",
                    "encounter_evidence": (
                        "performed in this encounter"
                        if subject["role"] == "procedure"
                        else "none"
                    ),
                    "open_status_evidence": "none",
                    "threshold": "none",
                    "waits_on_result": "none",
                }
            )
        return {"pairs": [{"stem": "case-01", "codes": records}]}

    def grade(self, record: dict) -> tuple[int, str]:
        record_path = Path(self.raw.name) / "agreement-read.json"
        record_path.write_text(json.dumps(record), encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            status = scan.main(
                [
                    str(self.worksheets),
                    "--notes",
                    str(self.notes),
                    "--agreement-read",
                    str(record_path),
                ]
            )
        return status, output.getvalue()

    def test_the_brief_contains_the_note_and_official_descriptors_but_no_anchors(self):
        brief = self.brief()

        self.assertIn("Synthetic note", brief["pairs"][0]["note"])
        self.assertNotIn("anchor", json.dumps(brief).lower())
        self.assertIn("Heartburn", [row["descriptor"] for row in brief["pairs"][0]["codes"]])
        self.assertEqual(1, brief["excluded_em"])

    def test_the_brief_carries_the_stem_table_and_cross_reference_rules(self):
        instructions = self.brief()["instructions"]

        for phrase in (
            "subject code's stem",
            "word order within a cross-reference",
            "still-unmatched cross-reference",
            "Neoplasm Table routes",
            "drug-table routes",
            "hedged self-harm or assault",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, instructions)

    def test_unpaired_note_or_worksheet_is_unread(self):
        (self.notes / "case-02.md").write_text(AGREEMENT_NOTE, encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            status = scan.main(
                [str(self.worksheets), "--notes", str(self.notes), "--agreement-brief"]
            )

        self.assertEqual(2, status)
        self.assertIn("unread remainder", output.getvalue())

    def test_a_code_missing_from_the_official_database_is_unread(self):
        worksheet = AGREEMENT_WORKSHEET.replace("ICD-10  R12  Heartburn", "ICD-10  Z99.99  Heartburn")
        (self.worksheets / "case-01.md").write_text(worksheet, encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            status = scan.main(
                [str(self.worksheets), "--notes", str(self.notes), "--agreement-brief"]
            )

        self.assertEqual(2, status)
        self.assertGreater(json.loads(output.getvalue())["unread remainder"], 0)

    def test_a_complete_verbatim_read_and_bidirectional_bind_are_clean(self):
        status, report = self.grade(self.clean_record())

        self.assertEqual(0, status)
        self.assertIn("agreement findings                 0", report)
        self.assertIn("E/M lines excluded                  1", report)

    def test_words_absent_from_the_worksheet_support_fail(self):
        record = self.clean_record()
        record["pairs"][0]["codes"][0]["agreeing_words"] = "unrelated words"

        self.assertEqual(1, self.grade(record)[0])

    def test_a_fabricated_index_route_fails(self):
        record = self.clean_record()
        record["pairs"][0]["codes"][0]["route"] = "banana"

        self.assertEqual(1, self.grade(record)[0])

    def test_an_exact_official_index_route_passes(self):
        record = self.clean_record()
        row = next(
            item for item in record["pairs"][0]["codes"] if item["code"] == "R12"
        )
        row["route"] = "Heartburn -> code R12"

        self.assertEqual(0, self.grade(record)[0])

    def test_a_referral_chain_starts_in_the_agreeing_words_and_ends_at_the_code(self):
        subject = scan.AgreementSubject(
            "ICD-10", "F17.210", "Nicotine dependence, cigarettes, uncomplicated",
            "entry", "current daily smoker", "ICD-10:F17.210:entry:1",
        )
        route = (
            "Smoker -> see Dependence, drug, nicotine | "
            "Dependence (on) (syndrome) > drug NEC > nicotine > cigarettes -> code F17.210"
        )

        self.assertTrue(scan._valid_route(subject, route, "current daily smoker"))
        self.assertFalse(
            scan._valid_route(
                subject,
                "Dependence (on) (syndrome) > drug NEC > nicotine > cigarettes -> code F17.210",
                "current daily smoker",
            )
        )

    def test_an_index_stem_needs_the_tabular_encounter_character(self):
        subject = scan.AgreementSubject(
            "ICD-10", "S61.011A", "Laceration without foreign body of right thumb "
            "without damage to nail, initial encounter", "entry", "right thumb laceration",
        )
        route = "Laceration > thumb > right -> code S61.011"
        catalog = {
            route: ("Laceration > thumb > right", "S61011", None, None),
        }
        siblings = (
            ("S61011A", subject.descriptor),
            ("S61011D", subject.descriptor.replace("initial", "subsequent")),
            ("S61011S", subject.descriptor.replace("initial encounter", "sequela")),
        )

        with patch.object(scan, "_index_route_catalog", return_value=catalog), patch.object(
            scan, "_stem_descriptors", return_value=siblings
        ):
            self.assertTrue(
                scan._valid_route(subject, route, "right thumb laceration", "initial encounter")
            )
            self.assertFalse(
                scan._valid_route(subject, route, "right thumb laceration", "subsequent encounter")
            )

    def test_a_laterality_mutation_does_not_agree_through_the_other_stem(self):
        subject = scan.AgreementSubject(
            "ICD-10", "S61.012A", "Laceration without foreign body of left thumb "
            "without damage to nail, initial encounter", "entry", "right thumb laceration",
        )
        right_route = "Laceration > thumb > right -> code S61.011"
        catalog = {
            right_route: ("Laceration > thumb > right", "S61011", None, None),
        }

        with patch.object(scan, "_index_route_catalog", return_value=catalog):
            self.assertFalse(
                scan._valid_route(
                    subject, right_route, "right thumb laceration", "initial encounter"
                )
            )

    def test_cross_reference_word_order_does_not_change_the_route(self):
        subject = scan.AgreementSubject("ICD-10", "A12.3", "Example", "entry", "example")
        first = "Example -> see Target, reordered"
        last = "Reordered > Target -> code A12.3"
        catalog = {
            first: ("Example", None, "Target, reordered", None),
            last: ("Reordered > Target", "A123", None, None),
        }

        with patch.object(scan, "_index_route_catalog", return_value=catalog):
            self.assertEqual(
                scan.RouteStatus.VALID,
                scan._route_status(subject, f"{first} | {last}", "example"),
            )

    def test_cross_reference_placeholders_are_filled_from_the_next_step(self):
        self.assertTrue(
            scan._reference_matches(
                "Contact, with, by type of instrument",
                "Contact (accidental) > with > knife",
                "W260",
                "cut with a knife",
            )
        )
        self.assertFalse(
            scan._reference_matches(
                "Contact, with, by type of instrument",
                "Contact (accidental) > with > knife",
                "W260",
                "accident during food preparation",
            )
        )

    def test_cross_reference_code_instructions_are_satisfied_by_the_subject(self):
        reference = "categories T36-T50, with 6th character 5"

        self.assertTrue(scan._reference_matches(reference, "Drug destination", "T391X5A"))
        self.assertFalse(scan._reference_matches(reference, "Drug destination", "T391X4A"))
        self.assertFalse(scan._reference_matches(reference, "Drug destination", "T601X5A"))

    def test_drug_table_reference_still_checks_range_character_and_destination(self):
        reference = (
            "Table of Drugs and Chemicals, categories T36-T50, with 6th character 5"
        )

        self.assertTrue(
            scan._reference_matches(
                reference,
                "Ibuprofen > Poisoning Undetermined",
                "T391X5A",
            )
        )
        self.assertFalse(
            scan._reference_matches(
                reference,
                "Ibuprofen > Poisoning Undetermined",
                "T601X5A",
            )
        )
        self.assertFalse(
            scan._reference_matches(
                reference,
                "Ibuprofen > Poisoning Undetermined",
                "T391X4A",
            )
        )
        self.assertFalse(
            scan._reference_matches(reference, "Contact > with > knife", "T391X5A")
        )

    def test_external_cause_reference_checks_its_named_destination(self):
        reference = "Index to External Causes of Injury, Perpetrator"

        self.assertTrue(
            scan._reference_matches(reference, "Perpetrator > parent", "Y070")
        )
        self.assertFalse(
            scan._reference_matches(reference, "Contact > with > knife", "W260")
        )

    def test_an_unmatched_real_cross_reference_is_unread_not_invalid(self):
        subject = scan.AgreementSubject("ICD-10", "A12.3", "Example", "entry", "example")
        first = "Example -> see Opaque CMS wording"
        last = "Actual destination -> code A12.3"
        catalog = {
            first: ("Example", None, "Opaque CMS wording", None),
            last: ("Actual destination", "A123", None, None),
        }

        with patch.object(scan, "_index_route_catalog", return_value=catalog):
            self.assertEqual(
                scan.RouteStatus.UNREAD,
                scan._route_status(subject, f"{first} | {last}", "example"),
            )

    def test_an_unmatched_real_cross_reference_names_the_unread_residue(self):
        record = self.clean_record()
        row = next(item for item in record["pairs"][0]["codes"] if item["code"] == "R12")
        first = "Heartburn -> see Opaque CMS wording"
        last = "Actual destination -> code R12"
        row["route"] = f"{first} | {last}"
        catalog = {
            first: ("Heartburn", None, "Opaque CMS wording", None),
            last: ("Actual destination", "R12", None, None),
        }

        with patch.object(scan, "_index_route_catalog", return_value=catalog):
            status, report = self.grade(record)

        self.assertEqual(2, status)
        self.assertIn("Opaque CMS wording", report)
        self.assertNotIn("codes with no route               1", report)

    def test_an_unmatched_cross_reference_to_another_code_is_invalid(self):
        subject = scan.AgreementSubject("ICD-10", "A12.3", "Example", "entry", "example")
        first = "Example -> see Opaque CMS wording"
        last = "Actual destination -> code B12.3"
        catalog = {
            first: ("Example", None, "Opaque CMS wording", None),
            last: ("Actual destination", "B123", None, None),
        }

        with patch.object(scan, "_index_route_catalog", return_value=catalog):
            self.assertEqual(
                scan.RouteStatus.INVALID,
                scan._route_status(subject, f"{first} | {last}", "example"),
            )

    def test_drug_columns_follow_the_guideline_definitions(self):
        cases = (
            ("2-year-old got into the ibuprofen", "Poisoning Accidental (unintentional)"),
            ("properly administered ibuprofen caused an adverse effect", "Adverse effect"),
            ("stopped taking ibuprofen on her own", "Underdosing"),
            ("ibuprofen overdose in a suicide attempt", "Poisoning Intentional self-harm"),
            ("ibuprofen poisoning after an assault", "Poisoning Assault"),
            ("intentional ibuprofen poisoning by an assailant", "Poisoning Assault"),
            ("ibuprofen ingestion; intent cannot be determined", "Poisoning Undetermined"),
        )

        for words, expected in cases:
            with self.subTest(words=words):
                self.assertTrue(scan._drug_column_agrees(expected, words))
                self.assertFalse(
                    any(
                        scan._drug_column_agrees(other, words)
                        for other in scan.DRUG_COLUMNS
                        if other != expected
                    )
                )

    def test_hedged_self_harm_agrees_only_with_undetermined(self):
        words = "acetaminophen ingestion, possibly intentional self-harm; patient denies"

        self.assertTrue(scan._drug_column_agrees("Poisoning Undetermined", words))
        self.assertFalse(scan._drug_column_agrees("Poisoning Intentional self-harm", words))
        self.assertFalse(scan._drug_column_agrees("Poisoning Accidental (unintentional)", words))

    def test_neoplasm_behavior_columns_are_mutually_exclusive(self):
        cases = (
            ("malignant lung cancer", "Malignant Primary"),
            ("metastatic lung cancer", "Malignant Secondary"),
            ("lung carcinoma in situ", "Ca in situ"),
            ("benign lung neoplasm", "Benign"),
            ("lung neoplasm with indeterminate pathology", "Uncertain Behavior"),
            ("lung neoplasm", "Unspecified Behavior"),
        )

        for words, expected in cases:
            with self.subTest(words=words):
                self.assertTrue(scan._neoplasm_column_agrees(expected, words))
                self.assertFalse(
                    any(
                        scan._neoplasm_column_agrees(other, words)
                        for other in scan.NEOPLASM_COLUMNS
                        if other != expected
                    )
                )

    def test_a_stem_mismatch_is_a_finding_even_when_a_reference_is_unread(self):
        subject = scan.AgreementSubject(
            "ICD-10",
            "S61.011S",
            "Laceration without foreign body of right thumb without damage to nail, sequela",
            "entry",
            "right thumb laceration",
        )
        first = "Laceration -> see Opaque CMS wording"
        last = "Laceration > thumb > right -> code S61.011"
        catalog = {
            first: ("Laceration", None, "Opaque CMS wording", None),
            last: ("Laceration > thumb > right", "S61011", None, None),
        }
        siblings = (
            ("S61011A", subject.descriptor.replace("sequela", "initial encounter")),
            ("S61011S", subject.descriptor),
        )

        with patch.object(scan, "_index_route_catalog", return_value=catalog), patch.object(
            scan, "_stem_descriptors", return_value=siblings
        ):
            self.assertEqual(
                scan.RouteStatus.INVALID,
                scan._route_status(
                    subject,
                    f"{first} | {last}",
                    "right thumb laceration",
                    "initial encounter",
                ),
            )

    def test_neoplasm_columns_do_not_turn_a_mass_into_a_neoplasm(self):
        words = "left breast mass concerning for malignancy; biopsy scheduled"

        self.assertFalse(scan._neoplasm_column_agrees("Malignant Primary", words))
        self.assertFalse(scan._neoplasm_column_agrees("Unspecified Behavior", words))

    def test_an_unqualified_tumor_takes_unspecified_behavior(self):
        words = "lung tumor with behavior not stated"

        self.assertTrue(scan._neoplasm_column_agrees("Unspecified Behavior", words))
        self.assertFalse(scan._neoplasm_column_agrees("Uncertain Behavior", words))

    def test_uncertain_behavior_requires_an_indeterminate_pathology_result(self):
        self.assertTrue(
            scan._neoplasm_column_agrees(
                "Uncertain Behavior", "pathology was indeterminate for malignant versus benign"
            )
        )
        self.assertFalse(
            scan._neoplasm_column_agrees("Uncertain Behavior", "biopsy is pending")
        )

    def test_a_benign_morphology_does_not_wait_for_tissue(self):
        self.assertTrue(scan._neoplasm_column_agrees("Benign", "likely lipoma on examination"))

    def test_a_differential_descriptor_cannot_supply_its_own_agreeing_words(self):
        worksheet = AGREEMENT_WORKSHEET.replace(
            "Plantar wart was considered for the focal plantar lesion.",
            "A focal lesion was considered.",
        )
        (self.worksheets / "case-01.md").write_text(worksheet, encoding="utf-8")

        self.assertEqual(1, self.grade(self.clean_record())[0])

    def test_a_malformed_evidence_field_is_unread(self):
        record = self.clean_record()
        record["pairs"][0]["codes"][0]["threshold"] = None

        self.assertEqual(2, self.grade(record)[0])

    def test_duplicate_subject_occurrences_each_require_a_reader_row(self):
        first = AGREEMENT_WORKSHEET.split("ICD-10  M79.675", 1)[0]
        heartburn = first[first.index("ICD-10  R12") :]
        worksheet = AGREEMENT_WORKSHEET.replace(heartburn, heartburn + heartburn, 1)
        (self.worksheets / "case-01.md").write_text(worksheet, encoding="utf-8")
        record = self.clean_record()
        duplicate = [
            row for row in record["pairs"][0]["codes"] if row["code"] == "R12"
        ]
        self.assertEqual(2, len(duplicate))
        record["pairs"][0]["codes"].remove(duplicate[-1])

        self.assertEqual(2, self.grade(record)[0])

    def test_duplicate_pair_records_are_unread(self):
        record = self.clean_record()
        record["pairs"].append(record["pairs"][0].copy())

        self.assertEqual(2, self.grade(record)[0])

    def test_a_surplus_pair_record_is_unread(self):
        record = self.clean_record()
        record["pairs"].append({"stem": "case-99", "codes": []})

        self.assertEqual(2, self.grade(record)[0])

    def test_a_non_object_code_record_is_unread_instead_of_a_traceback(self):
        record = self.clean_record()
        record["pairs"][0]["codes"][0] = None

        self.assertEqual(2, self.grade(record)[0])

    def test_a_differential_descriptor_waiting_on_a_result_fails(self):
        record = self.clean_record()
        row = next(
            item for item in record["pairs"][0]["codes"] if item["role"] == "differential"
        )
        row["waits_on_result"] = "pathology result"

        status, report = self.grade(record)
        self.assertEqual(1, status)
        self.assertRegex(report, r"descriptors waiting on results\s+1")

    def test_a_procedure_descriptor_the_reader_cannot_settle_is_unread(self):
        record = self.clean_record()
        row = next(
            item for item in record["pairs"][0]["codes"] if item["role"] == "procedure"
        )
        row["agreeing_words"] = "none"
        row["route"] = "none"

        status, report = self.grade(record)
        self.assertEqual(2, status)
        self.assertRegex(report, r"unread remainder 1")

    def test_a_procedure_without_encounter_evidence_fails(self):
        record = self.clean_record()
        row = next(
            item for item in record["pairs"][0]["codes"] if item["role"] == "procedure"
        )
        row["encounter_evidence"] = "none"

        status, report = self.grade(record)
        self.assertEqual(1, status)
        self.assertRegex(report, r"codes with no encounter evidence\s+1")

    def test_a_final_code_absent_from_the_worksheet_fails_the_bind(self):
        (self.notes / "case-01.md").write_text(
            AGREEMENT_NOTE.replace("Pain in left toe(s) - **M79.675**", "Pain in left toe(s) - **M25.572**"),
            encoding="utf-8",
        )

        self.assertEqual(1, self.grade(self.clean_record())[0])


    def test_a_refusal_dropped_from_the_note_fails_the_bind(self):
        (self.notes / "case-01.md").write_text(
            AGREEMENT_NOTE.replace(
                "NOT CODED: M86.9 Osteomyelitis, unspecified, no imaging established bone infection.\n",
                "",
            ),
            encoding="utf-8",
        )

        self.assertEqual(1, self.grade(self.clean_record())[0])

    def test_an_inline_welded_refusal_participates_in_the_bind(self):
        note = AGREEMENT_NOTE.replace(
            "NOT CODED: M86.9 Osteomyelitis, unspecified, no imaging established bone infection.",
            "Imaging is absent; NOT CODED: M86.9 Osteomyelitis, unspecified.",
        )
        (self.notes / "case-01.md").write_text(note, encoding="utf-8")

        self.assertEqual(0, self.grade(self.clean_record())[0])

    def test_procedure_lookup_prose_without_an_anchor_is_not_a_proposal(self):
        worksheet = AGREEMENT_WORKSHEET.replace(
            "CPT  10060  Incision and drainage of abscess; simple or single\n"
            '  ANCHOR: "Incision and drainage of abscess"\n'
            "  SPECIFICITY: complete - performed today\n"
            "  CONFIDENCE: verified against CPT Professional 2026\n",
            "CPT 10060 was looked up but is not proposed.\n",
        )
        note = AGREEMENT_NOTE.replace("CPT: 10060 Incision and drainage of abscess", "CPT: None")
        (self.worksheets / "case-01.md").write_text(worksheet, encoding="utf-8")
        (self.notes / "case-01.md").write_text(note, encoding="utf-8")
        record = self.clean_record()

        self.assertNotIn("10060", [row["code"] for row in record["pairs"][0]["codes"]])
        self.assertEqual(0, self.grade(record)[0])

    def test_a_rendered_procedure_nobody_proposed_fails_the_bind(self):
        (self.notes / "case-01.md").write_text(
            AGREEMENT_NOTE.replace("CPT: 10060", "CPT: 12001"), encoding="utf-8"
        )

        self.assertEqual(1, self.grade(self.clean_record())[0])

    def test_a_refusal_substitute_absent_from_the_proposed_entries_fails(self):
        (self.worksheets / "case-01.md").write_text(
            AGREEMENT_WORKSHEET.replace(
                "proposed instead: M79.675", "proposed instead: M25.572"
            ),
            encoding="utf-8",
        )

        self.assertEqual(1, self.grade(self.clean_record())[0])


class CommittedAgreementControls(unittest.TestCase):
    ROOT = Path(__file__).resolve().parent.parent / "fixtures"

    def grade(self, control: str, root: Path | None = None) -> tuple[int, str]:
        base = root or self.ROOT / control
        output = io.StringIO()
        with redirect_stdout(output):
            status = scan.main(
                [
                    str(base / "worksheets"),
                    "--notes",
                    str(base / "notes"),
                    "--agreement-read",
                    str(base / "agreement-read.json"),
                ]
            )
        return status, output.getvalue()

    def test_the_blind_positive_and_note_path_records_are_clean(self):
        for control in (
            "descriptor-agreement-positive-control",
            "descriptor-agreement-note-path-control",
            "descriptor-agreement-index-table-control",
        ):
            with self.subTest(control=control):
                status, report = self.grade(control)
                self.assertEqual(0, status)
                self.assertIn("agreement findings                 0", report)
                self.assertIn("unread remainder 0", report)

    def mutated_index_table_control(
        self,
        stem: str,
        old_code: str,
        new_code: str,
        new_descriptor: str,
        new_route: str,
    ) -> Path:
        raw = tempfile.TemporaryDirectory()
        self.addCleanup(raw.cleanup)
        destination = Path(raw.name) / "control"
        shutil.copytree(
            self.ROOT / "descriptor-agreement-index-table-control", destination
        )
        worksheet_path = destination / "worksheets" / f"{stem}.md"
        worksheet = worksheet_path.read_text(encoding="utf-8")
        old_descriptor = scan._official_descriptor("ICD-10", old_code)
        self.assertIsNotNone(old_descriptor)
        old_line = f"ICD-10  {old_code}  {old_descriptor}"
        self.assertIn(old_line, worksheet)
        worksheet_path.write_text(
            worksheet.replace(
                old_line,
                f"ICD-10  {new_code}  {new_descriptor}",
                1,
            ),
            encoding="utf-8",
        )
        record_path = destination / "agreement-read.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        row = next(
            item
            for pair in record["pairs"]
            if pair["stem"] == stem
            for item in pair["codes"]
            if item["code"] == old_code
        )
        row["code"] = new_code
        row["descriptor"] = new_descriptor
        row["subject_id"] = row["subject_id"].replace(old_code, new_code)
        row["route"] = new_route
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return destination

    def test_real_injury_control_rejects_laterality_and_sequela_mutations(self):
        cases = (
            (
                "S61.012A",
                "Laceration without foreign body of left thumb without damage to nail, initial encounter",
            ),
            (
                "S61.011S",
                "Laceration without foreign body of right thumb without damage to nail, sequela",
            ),
        )
        for code, descriptor in cases:
            with self.subTest(code=code):
                root = self.mutated_index_table_control(
                    "injury",
                    "S61.011A",
                    code,
                    descriptor,
                    "Laceration > thumb > right -> code S61.011",
                )
                status, report = self.grade("", root)
                self.assertEqual(1, status)
                self.assertRegex(report, r"codes with no route\s+1")

    def test_real_neoplasm_control_rejects_unsupported_behavior_mutations(self):
        cases = (
            (
                "D39.0",
                "Neoplasm of uncertain behavior of uterus",
                "Neoplasm, neoplastic > uterus, uteri, uterine > Uncertain Behavior -> code D39.0",
            ),
            (
                "C55",
                "Malignant neoplasm of uterus, part unspecified",
                "Neoplasm, neoplastic > uterus, uteri, uterine > Malignant Primary -> code C55",
            ),
        )
        for code, descriptor, route in cases:
            with self.subTest(code=code):
                root = self.mutated_index_table_control(
                    "neoplasm", "D25.9", code, descriptor, route
                )
                status, report = self.grade("", root)
                self.assertEqual(1, status)
                self.assertRegex(report, r"codes with no route\s+1")

    def test_the_blind_negative_reader_rederived_the_predicted_rows(self):
        base = self.ROOT / "descriptor-agreement-negative-control"
        self.assertEqual(
            (self.ROOT / "filled-anchor" / "notes" / "case-01.md").read_bytes(),
            (base / "notes" / "case-01.md").read_bytes(),
        )
        self.assertEqual(
            (self.ROOT / "worksheet-grammar-positive-control" / "case-01.md").read_bytes(),
            (base / "worksheets" / "case-01.md").read_bytes(),
        )
        record = json.loads((base / "agreement-read.json").read_text(encoding="utf-8"))
        rows = {
            (row["code"], row["role"]): row
            for row in record["pairs"][0]["codes"]
        }

        self.assertEqual("none", rows[("M79.5", "entry")]["agreeing_words"])
        self.assertNotEqual("none", rows[("M79.5", "differential")]["waits_on_result"])
        self.assertEqual("none", rows[("Z13.1", "differential")]["agreeing_words"])
        status, report = self.grade("descriptor-agreement-negative-control")
        self.assertEqual(1, status)
        self.assertRegex(report, r"codes with no agreeing words\s+3")
        self.assertRegex(report, r"non-verbatim agreeing words\s+1")
        self.assertRegex(report, r"codes with no route\s+3")
        self.assertRegex(report, r"codes with no encounter evidence\s+2")
        self.assertRegex(report, r"descriptors waiting on results\s+2")
        self.assertRegex(report, r"note/worksheet bind findings\s+4")
        self.assertRegex(report, r"unread remainder 1")


    def mutated_note_path(self, old: str, new: str) -> Path:
        raw = tempfile.TemporaryDirectory()
        self.addCleanup(raw.cleanup)
        destination = Path(raw.name) / "control"
        shutil.copytree(self.ROOT / "descriptor-agreement-note-path-control", destination)
        note_path = destination / "notes" / "case-01.md"
        note = note_path.read_text(encoding="utf-8")
        self.assertIn(old, note)
        note_path.write_text(note.replace(old, new, 1), encoding="utf-8")
        return destination

    def test_a_one_line_final_diagnosis_mutation_fires_the_committed_bind(self):
        root = self.mutated_note_path(
            "Final diagnosis: Cutaneous abscess of left foot - L02.612; "
            "Pain in left toe(s) - M79.675",
            "Final diagnosis: Cutaneous abscess of left foot - L02.612; "
            "Pain in left toe(s) - M25.572",
        )
        self.assertEqual(1, self.grade("", root)[0])

    def test_a_one_line_differential_mutation_fires_the_committed_bind(self):
        old = "Pain in left toe(s) - M79.675: severe focal pain"
        root = self.mutated_note_path(
            old, "Pain in left toe(s) - M25.572: severe focal pain"
        )
        self.assertEqual(1, self.grade("", root)[0])

    def test_a_one_line_refusal_mutation_fires_the_committed_bind(self):
        root = self.mutated_note_path("NOT CODED: S90.452A", "NOT CODED: S90.452D")
        self.assertEqual(1, self.grade("", root)[0])

    def test_a_one_line_procedure_mutation_fires_the_committed_bind(self):
        root = self.mutated_note_path("CPT: None", "CPT: 10060")
        self.assertEqual(1, self.grade("", root)[0])


class CommittedIndexAndTableControls(unittest.TestCase):
    ROOT = Path(__file__).resolve().parent.parent / "fixtures"

    def subject(self, code: str) -> scan.AgreementSubject:
        descriptor = scan._official_descriptor("ICD-10", code)
        self.assertIsNotNone(descriptor)
        return scan.AgreementSubject("ICD-10", code, descriptor or "", "entry", "")

    def test_the_committed_thumb_note_supports_both_index_stems(self):
        note = (self.ROOT / "filled-anchor" / "notes" / "case-06.md").read_text(
            encoding="utf-8"
        )
        injury_words = "a 2.25 cm linear laceration of the right thumb"
        mechanism_words = "a clean linear cut from a sheet-metal edge"
        self.assertIn(injury_words, note)
        self.assertIn(mechanism_words, note)

        self.assertTrue(
            scan._valid_route(
                self.subject("S61.011A"),
                "Laceration > thumb > right -> code S61.011",
                injury_words,
                "initial encounter",
            )
        )
        self.assertTrue(
            scan._valid_route(
                self.subject("W26.8XXA"),
                "Contact (accidental) > with > sharp object (s) > specified NEC -> code W26.8",
                mechanism_words,
                "initial encounter",
            )
        )

    def test_laterality_and_sequela_mutations_fail_the_committed_thumb_note(self):
        route = "Laceration > thumb > right -> code S61.011"
        words = "a 2.25 cm linear laceration of the right thumb"

        self.assertFalse(
            scan._valid_route(self.subject("S61.012A"), route, words, "initial encounter")
        )
        self.assertFalse(
            scan._valid_route(self.subject("S61.011S"), route, words, "initial encounter")
        )

    def test_the_committed_fibroid_note_supports_d259(self):
        note = (self.ROOT / "blind-run" / "obesity-bmi-case-01.md").read_text(
            encoding="utf-8"
        )
        words = "uterine fibroid mass"
        self.assertIn(words, note)

        self.assertTrue(
            scan._valid_route(
                self.subject("D25.9"),
                "Fibroid (tumor) > uterus -> code D25.9",
                words,
            )
        )

    def test_uncertain_or_malignant_mutations_fail_without_the_ruled_evidence(self):
        self.assertFalse(
            scan._valid_route(
                self.subject("D39.0"),
                "Neoplasm, neoplastic > corpus > uteri > Uncertain Behavior -> code D39.0",
                "uterine neoplasm; biopsy is pending",
            )
        )
        self.assertFalse(
            scan._valid_route(
                self.subject("C55"),
                "Neoplasm, neoplastic > uterus, uteri, uterine > Malignant Primary -> code C55",
                "uterine mass concerning for malignancy; no pathology result",
            )
        )


if __name__ == "__main__":
    unittest.main()
