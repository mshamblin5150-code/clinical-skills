"""Tests for the corpus census extractors.

These run against the committed, PHI-free fixtures in ``fixtures/day-a/shorthand/``
and ``fixtures/day-b/shorthand/`` and against inline strings. They never touch
``scratch/``. Their job is to catch the silent failure mode the census exists to
prevent: an extractor that stops matching and reports a confident wrong number.

``DayBIsTheAbsenceSet`` does a second job. day-b's whole reason for existing is
that nine of its twelve encounters carry no vital at all, and every row in its
assertion set rests on that. A well-meaning edit that "completes" one of those
vital lines would quietly void the set instead of failing it.

phi-scan: synthetic

Testing a date-of-birth extractor requires date-shaped literals, so this file is
exempt from the shape rules. **Every date below is invented.** The pragma does not
exempt it from the corpus layer: a real patient name or a real date lifted from
``scratch/`` is still refused here, which is exactly how the first version of this
file was caught using both.
"""

import unittest
from pathlib import Path

import corpus_census as cc

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "fixtures" / "day-a" / "shorthand"
DAY_B = REPO_ROOT / "fixtures" / "day-b" / "shorthand"
PEDS_BP = REPO_ROOT / "fixtures" / "peds-bp" / "shorthand"

# day-b/shorthand/README.md states this split in prose; the numbers are here so a
# change to either one has to be made in both places on purpose.
DAY_B_NO_VITAL = (1, 5, 6, 7, 8, 9, 10, 11, 12)
DAY_B_CONTROL = (2, 3, 4)
DAY_B_HYPERTENSIVE = (8, 9)  # the two B2 anchors

# peds-bp keeps its source shift's numbering, so the gaps are the omitted cases.
PEDS_BP_CASES = (2, 3, 5, 8, 9)
PEDS_BP_VITAL_LINE = (3, 5)  # a structured line was written; only the BP is missing
# Case 8 joins them under the census's reading, which counts the bare word "temp"
# in "temp this vist is 99.5" as a vital. That is a real given temperature written
# into the exam prose rather than onto a vital line -- the distinction peds-bp's
# assertions list under *Still unresolved*, and the reason these are two constants.
PEDS_BP_ANY_VITAL = (3, 5, 8)


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def day_b(number: int) -> str:
    return (DAY_B / f"case-{number:02d}.md").read_text(encoding="utf-8")


def peds_bp(number: int) -> str:
    return (PEDS_BP / f"case-{number:02d}.md").read_text(encoding="utf-8")


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

    def test_height_with_no_space_after_the_token(self):
        # He writes the vital line both ways. "ht5'7"" defeats a trailing \b on the
        # token, and the feet-and-inches alternative cannot rescue it either: there
        # is no word boundary between the "t" and the "5". Three encounters in the
        # corpus were read as having no height because of this.
        self.assertTrue(cc.has_height("bp 122/63, hr 59 ht5'7\" wt145"))
        self.assertTrue(cc.has_height("spo2 100% ht62.5 wt141"))

    def test_a_bare_token_is_still_a_height(self):
        # The no-space form is added, never substituted for the plain token.
        self.assertTrue(cc.has_height("ht 62.5 wt 141"))

    def test_a_measurement_in_prose_is_not_a_height(self):
        self.assertFalse(cc.has_height("wt 165 in the office today"))

    def test_ht_inside_a_word_is_not_a_height(self):
        self.assertFalse(cc.has_height("hx: htn, hypothyroid, right knee pain"))

    def test_weight_with_the_token(self):
        self.assertTrue(cc.has_weight("ht 5'10 wt 285"))

    def test_weight_by_unit_alone(self):
        self.assertTrue(cc.has_weight("36in 33lb"))

    def test_weight_with_no_space_after_the_token(self):
        self.assertTrue(cc.has_weight("bp 122/63, hr 59 ht5'7\" wt145"))
        self.assertTrue(cc.has_weight("ht 5'10 wt285"))

    def test_no_weight(self):
        self.assertFalse(cc.has_weight("hx: htn, djd, l knee surgery"))

    def test_the_no_space_form_still_requires_a_number(self):
        # "htn" is the decoy the digit exists to exclude: without it the new
        # alternative would read every hypertension history as a height.
        self.assertFalse(cc.has_height("hx: htn, gerd, hypothyroid"))

    def test_weight_has_no_equivalent_decoy(self):
        """Stated rather than asserted, because there is nothing to assert.

        The plain ``\\bwt\\b`` alternative predates this change and still counts a
        bare "wt" with no value as a weight. So there is no string that the
        no-space alternative must reject and the plain one accepts, and a
        mirror of the height test above would be vacuous -- it would pass
        whatever the new alternative did.
        """
        self.assertTrue(cc.has_weight("wt not recorded"))  # by the plain token

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

    def test_yo_run_together_with_the_sex_letter(self):
        # The form that broke HEIGHT, in the age extractor: "45yof" welds the
        # value, the token and the sex letter, so the trailing \b after "o"
        # cannot match. One note in the corpus writes it. That note is counted
        # today only because the token happens to sit alone on its own line and
        # AGE_AND_SEX_LINE rescues it -- move it into a sentence and the age
        # disappears, which is the silent failure this file exists to prevent.
        self.assertTrue(cc.has_stated_age("[PT] presents, 45yof c/o dysuria x 2 days"))
        self.assertTrue(cc.has_stated_age("[PT] presents, 45y/om c/o cough"))

    def test_the_welded_form_has_no_decoy_the_older_rule_misses(self):
        """Stated rather than asserted, because the obvious decoy is vacuous.

        The tempting test for the ``[mf]`` guard is "hold 3 your own meds" --
        and it does not exercise the guard at all. The pre-existing
        ``y\\.?o\\.?\\b`` alternative already rejects it, so the assertion
        passes identically with the guard deleted. Writing it as an assert
        would name a finding it never checks, which is the ADR 0001 failure
        mode. The guard earns its place by argument, not by this test:
        without it the alternative would end in nothing at all.
        """
        self.assertFalse(cc.has_stated_age("hold 3 your own meds"))  # by the older rule

    def test_a_follow_up_token_is_not_an_age(self):
        # "f/u" puts an "f" directly after a number, and audited 2026-08-11 it is
        # the commonest of the three digit+sex shapes in the corpus that sit
        # anywhere but alone on a line -- the form AGE_AND_SEX_LINE's line anchor
        # most has to reject. Unanchor that rule and every "augmentin 500 f/u"
        # becomes a 500-year-old.
        self.assertFalse(cc.has_stated_age("plan augmentin 500 f/u prn"))
        self.assertFalse(cc.has_stated_age("wbc 12 f/u in 2 weeks"))

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


class DayBIsTheAbsenceSet(unittest.TestCase):
    """Guards the property every day-b assertion rests on."""

    def test_the_set_has_twelve_cases(self):
        self.assertEqual(len(sorted(DAY_B.glob("case-*.md"))), 12)

    def test_every_case_is_exactly_one_note(self):
        for path in sorted(DAY_B.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertEqual(len(cc.split_notes(path.read_text(encoding="utf-8"))), 1)

    def test_nine_cases_carry_no_vital_at_all(self):
        for n in DAY_B_NO_VITAL:
            with self.subTest(case=n):
                self.assertFalse(cc.has_any_vital(day_b(n)))

    def test_the_three_controls_carry_a_full_vital_line(self):
        for n in DAY_B_CONTROL:
            with self.subTest(case=n):
                note = day_b(n)
                self.assertTrue(cc.has_bp(note))
                self.assertTrue(cc.has_weight(note))
                self.assertTrue(cc.has_other_vitals(note))

    def test_only_two_controls_carry_an_unambiguous_height(self):
        """Case 2's height is a preserved typo, and this test must not hide it.

        Case 2 reads ``wt 62in wt 131`` -- ``wt`` written where ``ht`` was meant.
        ``has_height`` returns True for it, but only via the bare ``62in`` form,
        not via a height token, so asserting it beside cases 3 and 4 would make a
        real ambiguity look settled. day-b/assertions.md exempts case 2's height
        from B4 for the same reason.
        """
        for n in (3, 4):
            with self.subTest(case=n, form="ht token"):
                self.assertRegex(day_b(n), r"(?i)\bht\s*\d|\bht\b")
        self.assertNotRegex(day_b(2), r"(?i)\bht\b")
        self.assertTrue(cc.has_height(day_b(2)))  # by "62in" alone

    def test_the_split_is_the_whole_set(self):
        self.assertEqual(sorted(DAY_B_NO_VITAL + DAY_B_CONTROL), list(range(1, 13)))

    def test_the_b1_anchors_document_hypertension_and_no_pressure(self):
        """B1 is only checkable where the history says htn and no BP was taken."""
        for n in DAY_B_HYPERTENSIVE:
            with self.subTest(case=n):
                note = day_b(n)
                self.assertIn("htn", note.lower())
                self.assertFalse(cc.has_bp(note))

    def test_every_case_states_an_age(self):
        """No day-b row is about a missing age; day-a case 10 already covers that."""
        for path in sorted(DAY_B.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertTrue(cc.has_stated_age(path.read_text(encoding="utf-8")))

    def test_no_case_carries_a_date_of_birth(self):
        for path in sorted(DAY_B.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertFalse(cc.has_dob(path.read_text(encoding="utf-8")))


class AgeInYears(unittest.TestCase):
    """The value extractor, as opposed to ``has_stated_age``'s presence check.

    Every decoy ``Age`` rejects must resolve to ``None`` here, not to a number:
    a presence check that over-matches inflates a percentage, but a value
    extractor that over-matches puts an encounter in the wrong age band, which
    is the thing issue #11's ruling turns on.
    """

    def test_years(self):
        self.assertEqual(cc.age_in_years("45 yo M"), 45)
        self.assertEqual(cc.age_in_years("a 7 years old male"), 7)
        self.assertEqual(cc.age_in_years("62 years of age"), 62)

    def test_bare_age_and_sex_on_its_own_line(self):
        self.assertEqual(cc.age_in_years("cc: cough\n51 f\nhx: none"), 51)

    def test_months_floor_to_zero(self):
        self.assertEqual(cc.age_in_years("9 months old M"), 0)
        self.assertEqual(cc.age_in_years("11 month old F"), 0)
        self.assertEqual(cc.age_in_years("3 week old female"), 0)

    def test_a_stated_year_beats_a_month_form_later_in_the_note(self):
        self.assertEqual(cc.age_in_years("2 yo M\ncough x 3 months old habit"), 2)

    def test_decoys_resolve_to_none(self):
        for decoy in (
            "t 98 F",              # a temperature on its own line
            "toradol 10 m",        # a dose
            "x 3 days f/u",        # the follow-up token taking the sex letter
            "32 weeks gestation",  # not the patient's age
            "no age anywhere",
        ):
            with self.subTest(decoy=decoy):
                self.assertIsNone(cc.age_in_years(decoy))

    def test_agrees_with_the_presence_check_on_every_committed_fixture(self):
        """The two must never disagree: one says there is an age, the other reads it."""
        for directory in (FIXTURES, DAY_B, PEDS_BP):
            for path in sorted(directory.glob("case-*.md")):
                note = path.read_text(encoding="utf-8")
                with self.subTest(case=f"{directory.name}/{path.name}"):
                    self.assertEqual(
                        cc.has_stated_age(note), cc.age_in_years(note) is not None
                    )

    def test_reads_the_day_b_adolescents(self):
        """Issue #11 turned on these two not being small children."""
        self.assertEqual(cc.age_in_years(day_b(6)), 17)
        self.assertEqual(cc.age_in_years(day_b(12)), 16)


class PedsBpIsTheSelectiveAbsenceSet(unittest.TestCase):
    """Guards the property every peds-bp assertion rests on.

    day-b's set is defined by encounters carrying *no* vital. This one is
    defined by the opposite shape -- a vital line that was written and is
    missing only the blood pressure -- and a well-meaning edit that added a
    pressure to case 3 or 5 would void the set rather than fail it.
    """

    def test_the_set_has_five_cases(self):
        self.assertEqual(len(sorted(PEDS_BP.glob("case-*.md"))), 5)

    def test_the_case_numbers_are_the_shifts_own(self):
        """Gaps in the numbering are the four school-age controls left out."""
        numbers = [int(p.stem.split("-")[1]) for p in sorted(PEDS_BP.glob("case-*.md"))]
        self.assertEqual(numbers, list(PEDS_BP_CASES))

    def test_every_case_is_exactly_one_note(self):
        for path in sorted(PEDS_BP.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertEqual(len(cc.split_notes(path.read_text(encoding="utf-8"))), 1)

    def test_no_case_carries_a_blood_pressure(self):
        for n in PEDS_BP_CASES:
            with self.subTest(case=n):
                self.assertFalse(cc.has_bp(peds_bp(n)))

    def test_every_case_is_under_six(self):
        for n in PEDS_BP_CASES:
            with self.subTest(case=n):
                age = cc.age_in_years(peds_bp(n))
                self.assertIsNotNone(age)
                self.assertLess(age, 6)

    def test_the_two_anchors_carry_a_vital_line_without_a_pressure(self):
        """Cases 3 and 5 are the inversion the set exists to test."""
        for n in PEDS_BP_VITAL_LINE:
            with self.subTest(case=n):
                note = peds_bp(n)
                self.assertTrue(cc.has_other_vitals(note))
                self.assertTrue(cc.has_weight(note))
                self.assertFalse(cc.has_bp(note))

    def test_case_three_carries_the_given_height_and_weight_percentiles(self):
        """P4 asserts these survive, and the anchor argument rests on them."""
        note = peds_bp(3)
        self.assertTrue(cc.has_height(note))
        self.assertIn("99.9th percentile", note)


class Bands(unittest.TestCase):
    """The age-band counts behind the two figures issue #11 wrote into SKILL.md."""

    def test_bands_partition_the_notes(self):
        notes = [peds_bp(n) for n in PEDS_BP_CASES] + [day_b(n) for n in (1, 6, 12)]
        bands = cc.survey_bands(notes)
        self.assertEqual(sum(b.notes for b in bands.values()), len(notes))

    def test_the_peds_set_lands_entirely_under_six(self):
        bands = cc.survey_bands([peds_bp(n) for n in PEDS_BP_CASES])
        self.assertEqual(bands[cc.UNDER_SIX].notes, 5)
        self.assertEqual(bands[cc.UNDER_SIX].without_bp, 5)
        self.assertEqual(bands[cc.UNDER_SIX].vital_line_no_bp, len(PEDS_BP_ANY_VITAL))
        self.assertEqual(bands[cc.UNDER_SIX].no_vital_at_all, 5 - len(PEDS_BP_ANY_VITAL))

    def test_a_missing_age_lands_in_its_own_band_rather_than_an_age_one(self):
        bands = cc.survey_bands(["cc: cough\nbp 120/80\n"])
        self.assertEqual(bands[cc.AGE_UNKNOWN].notes, 1)
        for name in (cc.UNDER_SIX, cc.ADULT):
            with self.subTest(band=name):
                self.assertEqual(bands[name].notes, 0)

    def test_no_vital_at_all_and_vital_line_no_bp_are_disjoint(self):
        notes = [peds_bp(n) for n in PEDS_BP_CASES] + [day_b(n) for n in range(1, 13)]
        for name, band in cc.survey_bands(notes).items():
            with self.subTest(band=name):
                self.assertEqual(
                    band.no_vital_at_all + band.vital_line_no_bp, band.without_bp
                )

    def test_the_band_report_emits_no_note_text(self):
        notes = [peds_bp(n) for n in PEDS_BP_CASES]
        report = cc.format_report(
            cc.survey(notes), source="fixtures", date="2026-08-11",
            bands=cc.survey_bands(notes),
        )
        self.assertIn("line, no BP", report)  # the section really rendered
        for leak in ("cc:", "hx:", "exam:", "[PT]", "plan ", "percentile"):
            with self.subTest(leak=leak):
                self.assertNotIn(leak, report)


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
        report = cc.format_report(
            cc.survey(self.notes), source="fixtures", date="2026-08-11",
            bands=cc.survey_bands(self.notes),
        )
        for leak in ("cc:", "hx:", "exam:", "[PT]", "plan "):
            with self.subTest(leak=leak):
                self.assertNotIn(leak, report)


if __name__ == "__main__":
    unittest.main()
