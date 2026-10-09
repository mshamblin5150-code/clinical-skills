"""Tests for ``bmi_codes``: the codes a note's own height and weight owe.

phi-scan: synthetic

Every note here is written in this file. The committed run records are read only
to pin the two findings they carry, which were measured before the row was
believed (ADR 0309 ruling 2).
"""

from __future__ import annotations

import unittest
from pathlib import Path

import bmi_codes as b
from prose_bind import NAMING, bind


REPO_ROOT = Path(__file__).resolve().parent.parent


def note(vitals: str, codes: str = "", opener: str = "45-year-old male", tier: str = "") -> str:
    return (
        f"# Note 1, {opener}\n\nS:\nCC: cough\n\nO:\nVS: BP 128/78, HR 80, {vitals}\n\n"
        f"A:\nDifferential:\n1. Acute bronchitis - J20.9\n{codes}\n\n"
        f"A {opener.split(',')[0]} with a cough.\n{tier}"
    )


class TheBoundaryIsDeclaredOnce(unittest.TestCase):
    def test_the_docstring_points_at_the_object_without_copying_rows(self):
        doc = b.__doc__ or ""
        self.assertEqual(1, doc.count("bmi_codes.DECLARED_LIMITS"))
        self.assertEqual((), bind(b.DECLARED_LIMITS, doc, mode=NAMING))


class AdultBands(unittest.TestCase):
    def test_the_band_edges(self):
        cases = {19.9: "Z68.1", 20.0: "Z68.20", 26.5: "Z68.26", 39.9: "Z68.39",
                 40.0: "Z68.41", 44.9: "Z68.41", 45.0: "Z68.42", 59.9: "Z68.43",
                 69.9: "Z68.44", 70.0: "Z68.45"}
        for bmi, code in cases.items():
            with self.subTest(bmi=bmi):
                self.assertEqual(code, b.adult_band(bmi))

    def test_the_bmi_is_rounded_to_the_precision_a_note_writes(self):
        self.assertEqual(24.0, b.bmi_of(62, 131))
        self.assertEqual(26.5, b.bmi_of(70, 185))


class WhatANoteOwes(unittest.TestCase):
    def test_an_overweight_adult_carrying_both_codes_owes_nothing(self):
        reading = b.read_note(note(
            "Ht 5'10\" (70 in), Wt 185 lb ∴ BMI 26.5",
            "2. Overweight - E66.3 with Body mass index 26.0-26.9, adult - Z68.26",
        ))
        self.assertEqual((26.5, "Z68.26", "E66.3", ()), (reading.bmi, reading.z68, reading.e66, reading.missing))

    def test_the_issue_1461_shape_fails_both_codes(self):
        """A delegated answer removed the codes and the tier block said so."""
        reading = b.read_note(note(
            "Ht 5'10\", Wt 185 lb ∴ BMI 26.5",
            tier="GAPS              No weight diagnosis was coded.\n",
        ))
        self.assertEqual(("Z68.26", "E66.3"), reading.missing)

    def test_any_obesity_code_satisfies_the_family_and_overweight_does_not(self):
        vitals = "Ht 5'6\", Wt 200 lb ∴ BMI 32.3"
        for e66, missing in (("E66.9", ()), ("E66.811", ()), ("E66.01", ()), ("E66.3", ("an obesity E66 code",))):
            with self.subTest(e66=e66):
                reading = b.read_note(note(vitals, f"2. Obesity - {e66} with BMI - Z68.32"))
                self.assertEqual(missing, reading.missing)

    def test_a_normal_bmi_is_read_and_never_graded(self):
        reading = b.read_note(note("Ht 5'9\", Wt 160 lb ∴ BMI 23.6"))
        self.assertEqual((23.6, False, ()), (reading.bmi, reading.graded, reading.missing))

    def test_a_welded_refusal_is_not_a_written_code(self):
        reading = b.read_note(note(
            "Ht 70 in, Wt 185 lb",
            "NOT CODED: Z68.26 Body mass index 26.0-26.9, adult, filled values; NOT CODED: E66.3 Overweight, filled.",
        ))
        self.assertEqual(("Z68.26", "E66.3"), reading.missing)

    def test_a_tier_block_mention_is_not_a_written_code(self):
        reading = b.read_note(note(
            "Ht 70 in, Wt 185 lb",
            tier="FILLED·asserted   Wt 185 lb filled.\n                  Would add E66.3 with Z68.26.\n",
        ))
        self.assertEqual(("Z68.26", "E66.3"), reading.missing)

    def test_metric_values_are_converted(self):
        reading = b.read_note(note("Ht 178 cm, Wt 95 kg", "E66.3 and Z68.29"))
        self.assertEqual((30.0, "Z68.30"), (reading.bmi, reading.z68))


class PediatricBands(unittest.TestCase):
    def test_a_child_reads_through_the_cdc_table(self):
        reading = b.read_note(note("Ht 36 in, Wt 33 lb ∴ BMI 17.9", opener="3-year-old boy"))
        self.assertEqual(("Z68.53", "E66.3"), (reading.z68, reading.e66))

    def test_an_unstated_sex_is_graded_where_both_charts_agree(self):
        reading = b.read_note(note("Ht 36 in, Wt 33 lb", opener="3-year-old"))
        self.assertEqual(("Z68.53", "E66.3"), reading.missing)

    def test_a_healthy_weight_band_owes_nothing(self):
        reading = b.read_note(note("Ht 44 in, Wt 44 lb", opener="7-year-old girl"))
        self.assertFalse(reading.graded)
        self.assertTrue(reading.read)

    def test_under_two_is_never_graded(self):
        reading = b.read_note(note("Ht 28.5 in, Wt 21 lb", opener="11-month-old female"))
        self.assertEqual((18.2, False), (reading.bmi, reading.graded))


class TheAge(unittest.TestCase):
    def test_the_most_stated_age_wins_over_a_relative_stated_once(self):
        region = "mother is a 62-year-old. A 36-year-old male. The 36-year-old reports"
        self.assertEqual((36.0, None), b.age_years(region))

    def test_durations_and_coding_ranges_are_not_ages(self):
        self.assertIsNone(b.age_years("illness is 1 to 2 days old; aged 2 to 19; ages 15-65"))

    def test_the_medatrax_age_field_is_an_age(self):
        self.assertEqual((34.0, None), b.age_years("Age + unit:            34 Years"))


class UnreadIsNotClean(unittest.TestCase):
    def test_a_bmi_whose_inputs_cannot_be_read_is_unread(self):
        reading = b.read_note(note("Ht five ten, Wt about 185 ∴ BMI 26.5"))
        self.assertTrue(reading.unread)

    def test_a_graded_range_bmi_with_no_age_is_unread(self):
        text = "VS: Ht 70 in, Wt 185 lb ∴ BMI 26.5\nOverweight.\n"
        self.assertTrue(b.read_note(text).unread)

    def test_a_normal_bmi_with_no_age_owes_nothing_at_any_age(self):
        text = "VS: Ht 69 in, Wt 160 lb ∴ BMI 23.6\n"
        self.assertFalse(b.read_note(text).unread)

    def test_a_note_without_body_measurements_is_outside_the_population(self):
        reading = b.read_note(note("T 98.6 F, RR 16"))
        self.assertEqual((False, False), (reading.candidate, reading.read))


class TheCommittedRecordsCarryTwoMeasuredFindings(unittest.TestCase):
    """Both predate the rule they now fail, and neither record is edited for it."""

    def read(self, relative: str) -> b.Reading:
        return b.read_note((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_filled_anchor_case_05_predates_the_not_withheld_ruling(self):
        self.assertEqual(("Z68.28", "E66.3"), self.read("fixtures/filled-anchor/notes/case-05.md").missing)

    def test_hedged_dx_case_03_predates_the_committed_calculator(self):
        self.assertEqual(("Z68.53", "E66.3"), self.read("fixtures/slot-form-run/hedged-dx-case-03.md").missing)

    def test_a_compliant_obese_record_reads_clean(self):
        reading = self.read("fixtures/slot-form-run/day-a-case-06.md")
        self.assertEqual(("Z68.41", ()), (reading.z68, reading.missing))


if __name__ == "__main__":
    unittest.main()
