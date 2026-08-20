"""Tests for the CDC pediatric BMI-for-age calculator.

The percentile expectations come from columns in CDC's committed 2022 extended
BMI-for-age table.  They are an answer key independent of the calculator: the
tests never recreate either CDC formula to obtain an expected value.
"""

from __future__ import annotations

import unittest

import cdc_percentile as cdc


class CdcPublishedPercentilesAreTheAnswerKey(unittest.TestCase):
    def test_lms_percentiles_through_the_95th_match_cdc_columns(self):
        for bmi, expected in ((14.7193, 5.0), (18.1195, 85.0), (19.2789, 95.0)):
            with self.subTest(percentile=expected):
                result = cdc.calculate("male", 24, bmi)
                self.assertAlmostEqual(result.percentile, expected, delta=0.06)

    def test_extended_percentiles_above_the_95th_match_cdc_columns(self):
        for bmi, expected in ((20.4536, 98.0), (21.0676, 99.0), (22.5258, 99.9)):
            with self.subTest(percentile=expected):
                result = cdc.calculate("male", 24, bmi)
                self.assertAlmostEqual(result.percentile, expected, delta=0.06)


class EveryPediatricBandHasOneAnswer(unittest.TestCase):
    def test_the_six_z68_bands_use_cdc_cutpoints(self):
        cases = (
            (14.0, "Z68.51", None),
            (16.0, "Z68.52", None),
            (18.5, "Z68.53", "E66.3"),
            (20.0, "Z68.54", "E66.811"),
            (23.5, "Z68.55", "E66.812"),
            (27.1, "Z68.56", "E66.813"),
        )
        for bmi, z68, e66 in cases:
            with self.subTest(bmi=bmi):
                result = cdc.calculate("male", 24, bmi)
                self.assertEqual(result.z68_code, z68)
                self.assertEqual(result.e66_code, e66)

    def test_each_exact_cutpoint_enters_the_higher_band(self):
        row = cdc.load_chart()[(1, 24.5)]
        cases = (
            (row.p5, "Z68.52"),
            (row.p85, "Z68.53"),
            (row.p95, "Z68.54"),
            (row.p120_of_p95, "Z68.55"),
            (1.4 * row.p95, "Z68.56"),
        )
        for bmi, expected in cases:
            with self.subTest(code=expected):
                self.assertEqual(cdc.calculate("male", 24, bmi).z68_code, expected)

    def test_a_whole_year_age_uses_the_midpoint_month_and_discloses_it(self):
        result = cdc.calculate_for_years("female", 16, 21.6)
        self.assertEqual(result.completed_months, 198)
        self.assertTrue(result.age_month_was_filled)


class InputsFailClosed(unittest.TestCase):
    def test_age_below_the_pediatric_chart_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "24 through 239"):
            cdc.calculate("female", 23, 18.0)

    def test_age_at_the_adult_boundary_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "24 through 239"):
            cdc.calculate("male", 240, 25.0)

    def test_nonpositive_bmi_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            cdc.calculate("male", 120, 0)

    def test_unknown_sex_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "male or female"):
            cdc.calculate("unknown", 120, 20)


if __name__ == "__main__":
    unittest.main()
