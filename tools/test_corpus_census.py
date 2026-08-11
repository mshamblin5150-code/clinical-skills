"""Tests for the corpus census extractors.

These run against the committed, PHI-free fixtures in ``fixtures/day-a/shorthand/``
and against inline strings. They never touch ``scratch/``. Their job is to catch
the silent failure mode the census exists to prevent: an extractor that stops
matching and reports a confident wrong number.
"""

import unittest
from pathlib import Path

import corpus_census as cc

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "fixtures" / "day-a" / "shorthand"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class SplitNotes(unittest.TestCase):
    def test_splits_on_the_note_delimiter(self):
        text = "Date: 5-06-20\nNote 1\nfirst\n\nnote 2\nsecond\n"
        self.assertEqual(len(cc.split_notes(text)), 2)

    def test_drops_the_preamble_before_the_first_note(self):
        text = "Date: 5-06-20\nNote 1\nfirst\n"
        self.assertNotIn("Date:", cc.split_notes(text)[0])

    def test_delimiter_is_case_insensitive(self):
        # fixtures/day-a/shorthand/case-03.md really does open "NOte 3".
        text = "Note 1\na\n\nnote 2\nb\n\nNOte 3\nc\n"
        self.assertEqual(len(cc.split_notes(text)), 3)

    def test_tolerates_a_hash_before_the_number(self):
        self.assertEqual(len(cc.split_notes("Note #1\na\n\nNote #2\nb\n")), 2)

    def test_every_committed_fixture_is_one_note(self):
        for path in sorted(FIXTURES.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertEqual(len(cc.split_notes(path.read_text(encoding="utf-8"))), 1)

    def test_concatenated_fixtures_split_back_into_ten(self):
        day = "\n\n".join(
            p.read_text(encoding="utf-8") for p in sorted(FIXTURES.glob("case-*.md"))
        )
        self.assertEqual(len(cc.split_notes(day)), 10)


class BloodPressure(unittest.TestCase):
    def test_reads_a_lowercase_reading(self):
        self.assertEqual(cc.bp_readings("bp 134/77 hr 79"), [(134, 77)])

    def test_reads_an_uppercase_reading(self):
        self.assertEqual(cc.bp_readings("BP 139/85 hr 91"), [(139, 85)])

    def test_reads_an_unprefixed_reading(self):
        self.assertEqual(cc.bp_readings("126/83 hr 84 t 97.1"), [(126, 83)])

    def test_ignores_a_date_of_birth(self):
        self.assertEqual(cc.bp_readings("dob 03/04/1990"), [])

    def test_ignores_a_pain_score(self):
        self.assertEqual(cc.bp_readings("c/o 8/10 pain, 10/10 at worst"), [])

    def test_ignores_heart_sounds(self):
        self.assertEqual(cc.bp_readings("s1,s2, 2/2. positive bowel"), [])

    def test_ignores_a_drug_fraction(self):
        self.assertEqual(cc.bp_readings("zithromax 200/5ml 3/4 t x 3 days"), [])

    def test_has_bp_follows_the_readings(self):
        self.assertTrue(cc.has_bp("bp 117/74"))
        self.assertFalse(cc.has_bp("hx: htn, djd"))

    def test_normal_is_below_130_over_80(self):
        self.assertTrue(cc.is_normal_bp((117, 74)))
        self.assertFalse(cc.is_normal_bp((134, 77)))  # systolic out
        self.assertFalse(cc.is_normal_bp((126, 83)))  # diastolic out
        self.assertFalse(cc.is_normal_bp((130, 80)))  # boundary is exclusive

    def test_fixture_readings(self):
        self.assertEqual(cc.bp_readings(fixture("case-01.md")), [(134, 77)])
        self.assertEqual(cc.bp_readings(fixture("case-03.md")), [(139, 85)])


class BodyMeasurements(unittest.TestCase):
    def test_height_in_feet_and_inches(self):
        self.assertTrue(cc.has_height("ht 5'4\" wt 212 lbs"))

    def test_height_in_bare_inches(self):
        self.assertTrue(cc.has_height("spo2 95 ht 62.5 wt 141"))

    def test_height_without_the_token(self):
        self.assertTrue(cc.has_height("rr 20 spo2 96 36in 33lb"))

    def test_height_spelled_out_in_inches(self):
        self.assertTrue(cc.has_height("spo2 99% ht 63 inches wt 160"))

    def test_height_survives_a_mistyped_token(self):
        # case-08 really does read "hr 65 inches"; the fixture README names that
        # typo as a defect the set exists to find, so "ht" cannot be relied on.
        self.assertTrue(cc.has_height(fixture("case-08.md")))
        self.assertTrue(cc.has_height(fixture("case-05.md")))
        self.assertTrue(cc.has_height(fixture("case-10.md")))

    def test_a_measurement_in_prose_is_not_a_height(self):
        self.assertFalse(cc.has_height("wt 165 in the office today"))

    def test_ht_inside_a_word_is_not_a_height(self):
        self.assertFalse(cc.has_height("hx: htn, hypothyroid, right knee pain"))

    def test_weight_with_the_token(self):
        self.assertTrue(cc.has_weight("ht 5'10 wt 285"))

    def test_weight_by_unit_alone(self):
        self.assertTrue(cc.has_weight("36in 33lb"))

    def test_no_weight(self):
        self.assertFalse(cc.has_weight("hx: htn, djd, l knee surgery"))

    def test_fixtures_carry_both(self):
        for name in ("case-01.md", "case-03.md"):
            with self.subTest(case=name):
                self.assertTrue(cc.has_height(fixture(name)))
                self.assertTrue(cc.has_weight(fixture(name)))


class OtherVitals(unittest.TestCase):
    def test_pulse_temp_rr_spo2(self):
        self.assertTrue(cc.has_other_vitals("hr 130 t 97.3 rr 32 spo2 99%"))

    def test_absent(self):
        self.assertFalse(cc.has_other_vitals("cc: right foot pain x 3-4 months"))

    def test_any_vital_is_the_union(self):
        self.assertTrue(cc.has_any_vital("hr 130 t 97.3 rr 32 spo2 99% wt 15"))
        self.assertTrue(cc.has_any_vital("bp 170/78"))
        self.assertFalse(cc.has_any_vital("cc: cough x 2 days\nallergy nkda"))


class Age(unittest.TestCase):
    def test_years_spelled_out(self):
        self.assertTrue(cc.has_stated_age("48 year old F"))

    def test_yo_abbreviation(self):
        self.assertTrue(cc.has_stated_age("60 yo F"))
        self.assertTrue(cc.has_stated_age("44 y/o female"))

    def test_years_of_age(self):
        self.assertTrue(cc.has_stated_age("[PT] is 54 years of age"))

    def test_bare_age_and_sex_on_its_own_line(self):
        self.assertTrue(cc.has_stated_age("[PT]\n51 f\ncc: dysuria"))
        self.assertTrue(cc.has_stated_age("[PT]\n48f\ncc: dysuria"))
        self.assertTrue(cc.has_stated_age("61F\n"))

    def test_pediatric_months(self):
        self.assertTrue(cc.has_stated_age("[PT]\n8 months old\nhr 130"))
        self.assertTrue(cc.has_stated_age("[PT]\n13 month male\nBp 164"))

    def test_a_temperature_is_not_an_age(self):
        # "t 98 F" would read as a 98-year-old under an unanchored digit+sex rule.
        self.assertFalse(cc.has_stated_age("bp 120/86 hr 97 t 98 F rr 20"))

    def test_a_dose_is_not_an_age(self):
        self.assertFalse(cc.has_stated_age("plan toradol 10 mg IM"))
        self.assertFalse(cc.has_stated_age("plan augmentin 875 for 10 days"))

    def test_gestational_age_is_not_patient_age(self):
        self.assertFalse(cc.has_stated_age("[PT]\n8 weeks g1p0a0\nbp 131/84"))

    def test_fixtures(self):
        self.assertTrue(cc.has_stated_age(fixture("case-01.md")))
        self.assertTrue(cc.has_stated_age(fixture("case-03.md")))


class DateOfBirth(unittest.TestCase):
    """Every date here is synthetic. The shapes are real; the values are not."""

    def test_token_with_slashes(self):
        self.assertTrue(cc.has_dob("dob 03/04/1990"))

    def test_token_with_dashes_and_two_digit_year(self):
        self.assertTrue(cc.has_dob("dob 7-8-91"))
        self.assertTrue(cc.has_dob("DOB 10-11-01"))

    def test_bare_date_alone_on_a_line(self):
        self.assertTrue(cc.has_dob("[PT]\nHR 132 t 97.3\n3/04/2020\nVaccs utd"))

    def test_an_lmp_is_not_a_birth_date(self):
        self.assertFalse(cc.has_dob("ht 5'6\" wt 110 8/10 pain. lmp 5-06-2020"))

    def test_a_visit_date_header_is_not_a_birth_date(self):
        self.assertFalse(cc.has_dob("Date: 5-06-20\ncc: cough"))


class Survey(unittest.TestCase):
    def setUp(self):
        self.notes = [
            p.read_text(encoding="utf-8") for p in sorted(FIXTURES.glob("case-*.md"))
        ]

    def test_counts_the_fixture_set(self):
        c = cc.survey(self.notes)
        self.assertEqual(c.notes, 10)
        self.assertEqual(c.with_bp + c.without_bp, 10)
        self.assertEqual(c.with_either_age_or_dob + c.with_neither, 10)

    def test_report_emits_no_note_text(self):
        """Standing rule 1: the census output must be safe to paste anywhere."""
        report = cc.format_report(cc.survey(self.notes), source="fixtures", date="2026-08-11")
        for leak in ("cc:", "hx:", "exam:", "[PT]", "plan "):
            with self.subTest(leak=leak):
                self.assertNotIn(leak, report)


if __name__ == "__main__":
    unittest.main()
