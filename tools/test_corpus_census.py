"""Tests for the corpus census extractors.

These run against the committed, PHI-free fixtures in ``fixtures/day-a/shorthand/``
and ``fixtures/day-b/shorthand/`` and against inline strings. They never touch
``scratch/``. Their job is to catch the silent failure mode the census exists to
prevent: an extractor that stops matching and reports a confident wrong number.

``DayBIsTheAbsenceSet`` does a second job: it guards the properties of the
*inputs* that day-b's assertion rows rest on, so an edit to one voids the set
loudly rather than quietly. Three shapes, and the first two are absences. Nine of
the twelve encounters carry no vital at all, which is that set's whole reason for
existing; case 9 documents a COVID contact and orders no swab, which is what makes
D6 checkable; and the twelve split seven / two / three on whether the shorthand
writes a pain score, writes "no pain", or writes neither, which is what B7 and B8
divide on. A well-meaning edit that "completes" any of them would leave every row
above it passing with nothing tested.

phi-scan: synthetic

Testing a date-of-birth extractor requires date-shaped literals, so this file is
exempt from the shape rules. **Every date below is invented.** The pragma does not
exempt it from the corpus layer: a real patient name or a real date lifted from
``scratch/`` is still refused here, which is exactly how the first version of this
file was caught using both.
"""

import re
import tempfile
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
DAY_B_HYPERTENSIVE = (8, 9)  # the two B2 anchors: htn documented, no pressure
# Every case documenting hypertension, which is wider than the B2 anchors. Cases
# 2 and 3 carry a given pressure, so the run has nothing to fill and B2 does not
# score them -- but they are what stops the extractor test being vacuous, and
# case 2's given 121/61 is the reading day-b/assertions.md cites as the in-corpus
# proof that a normal pressure in a hypertensive is a real patient. Issue #23.
DAY_B_DOCUMENTS_HTN = (2, 3, 8, 9)
DAY_B_HTN_WITH_BP = (2, 3)

# The three chest findings D2, D3 and D7 anchor on. Every one of these cases is
# also in DAY_B_NO_VITAL, which is what leaves all three rows open to a filled
# dismissal -- "deferred, afebrile with SpO2 97%" names the finding in the Plan
# and passes. B9 is what closes that. Issue #27.
DAY_B_LUNG_FINDING = {
    1: "lungs diminished in all four fields",
    9: "lung sounds diminished",
    11: "inspiratory wheezing noted in all fields",
}

# The OLDCARTS severity split B5-B8 rest on, for issue #30. Every case is in
# exactly one of the three, and which one decides whether its severity is a
# given the run must preserve or a value the run must invent.
DAY_B_PAIN_SCORE = {1: 8, 4: 5, 5: 2, 7: 7, 8: 8, 10: 8, 11: 6}
DAY_B_NO_PAIN = (2, 12)  # the shorthand writes the absence, so 0/10 is a given
DAY_B_SEVERITY_FILLED = (3, 6, 9)  # neither a score nor an absence: the run invents one
DAY_B_SEVERITY_NONZERO = (6, 9)  # B8's anchors. Case 3 itches rather than hurts

# B9's ten: every case where *anything* in the filled-vitals license class was
# generated. The vital-less nine plus case 3, whose vital line is complete and
# whose severity the run has to invent. Not B1's list, which is the mistake the
# first draft of the row made. Issue #27.
DAY_B_B9 = (1, 3, 5, 6, 7, 8, 9, 10, 11, 12)
NO_PAIN = r"(?i)\bno pain\b"

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


def day_b_plan(number: int) -> str:
    """Everything after the last ``plan`` token in a day-b input, lowercased.

    Crude on purpose, and it has one job: separate an order the clinician placed
    from the same word appearing earlier in the note for another reason. Case 9
    writes ``covid`` in the exam prose, as the contact's diagnosis, and orders no
    swab -- so a whole-file substring test for ``covid`` would report the
    exposure as a test that was run. The plans in these twelve are all a trailing
    ``plan``-prefixed run of comma-separated items, which is the whole structure
    this needs.

    Two things keep the crudeness from failing open. The token is matched on word
    boundaries, so ``planned``, ``plantar`` and ``explains`` do not split the
    note and silently truncate the half being searched. And a note with no plan
    token raises rather than returning "", which would make every ``assertNotIn``
    below pass on an empty string.
    """
    parts = re.split(r"\bplan\b", day_b(number).lower())
    if len(parts) == 1:
        raise AssertionError(f"day-b case {number} has no plan line to read")
    return parts[-1]


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


class ReadCorpusDropsDuplicateDayFiles(unittest.TestCase):
    """One day file in the clinician's catalog is on disk twice, byte for byte.

    ``GLOSSARY.md`` and ``batch-shift`` both describe the catalog as 48 unique
    files; the census walked all 49 and reported a corpus eight encounters
    larger, with nothing to reconcile the two. Issue #16.

    Deduplication is by **content**, not by name: the copy does not share a
    filename with its original, so a name-based check would not have seen it.
    """

    SHIFT = "day header\nNote 1\n51 f\ncc: cough\n\nNote 2\n7 yo M\ncc: rash\n"
    OTHER = "day header\nNote 1\n34 f\ncc: fever\n"

    def corpus_of(self, files: dict[str, str]) -> cc.Corpus:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in files.items():
                (root / name).write_text(text, encoding="utf-8")
            return cc.read_corpus(root)

    def test_identical_content_under_different_names_is_read_once(self):
        corpus = self.corpus_of({"a.txt": self.SHIFT, "scan-copy.txt": self.SHIFT})
        self.assertEqual(len(corpus.notes), 2)
        self.assertEqual(corpus.files, 2)
        self.assertEqual(corpus.unique_files, 1)

    def test_files_that_differ_are_all_kept(self):
        corpus = self.corpus_of({"a.txt": self.SHIFT, "b.txt": self.OTHER})
        self.assertEqual(len(corpus.notes), 3)
        self.assertEqual(corpus.files, 2)
        self.assertEqual(corpus.unique_files, 2)

    def test_a_repeated_encounter_inside_one_file_is_not_deduplicated(self):
        """Dedup is per file. A shift that saw two alike patients saw two patients."""
        corpus = self.corpus_of({"a.txt": "hdr\nNote 1\n51 f\n\nNote 2\n51 f\n"})
        self.assertEqual(len(corpus.notes), 2)
        self.assertEqual(corpus.unique_files, 1)

    def test_encounters_stay_grouped_by_the_file_they_came_from(self):
        corpus = self.corpus_of({"a.txt": self.SHIFT, "b.txt": self.OTHER})
        self.assertEqual([len(day) for day in corpus.day_files], [2, 1])


class SurveyFilesCase(unittest.TestCase):
    """Shared day files and the one-line survey call, for the two cases below.

    They are separate cases because they are separate claims by separate skills
    — ADR 0001's reasoning — but the fixtures and the call are the same three
    lines either way, and a second copy of them is a second thing to keep in
    step. Nothing here asserts; both subclasses do.
    """

    AGELESS = ("Note 1\ndob 4/4/44\ncc: cough\n", "Note 2\ndob 5/5/55\ncc: rash\n")
    MIXED = ("Note 1\ndob 4/4/44\ncc: cough\n", "Note 2\n51 f\ncc: rash\n")
    EVERY = ("Note 1\n51 f\ncc: cough\n", "Note 2\n7 yo M\ncc: rash\n")

    def survey(self, *days: tuple[str, ...]) -> cc.FileCensus:
        return cc.survey_files(cc.Corpus(day_files=days, files=len(days)))


class SurveyFilesCountsFilesNotEncounters(SurveyFilesCase):
    """The claim clinical-note step 1 rests on, made re-derivable. Issue #16.

    Step 1 quotes no share deliberately, and says instead that whole day files
    state no age at all. Nothing printed that until this existed, which left the
    replacement claim exactly as unverifiable as the 353-encounter one it
    replaced.
    """

    def test_a_file_with_no_age_anywhere_counts(self):
        self.assertEqual(self.survey(self.AGELESS).with_no_stated_age, 1)

    def test_one_stated_age_is_enough_to_clear_a_file(self):
        self.assertEqual(self.survey(self.MIXED).with_no_stated_age, 0)

    def test_counts_files_and_not_the_encounters_inside_them(self):
        census = self.survey(self.AGELESS, self.AGELESS, self.MIXED)
        self.assertEqual(census.with_no_stated_age, 2)
        self.assertEqual(census.unique_files, 3)

    def test_an_empty_file_is_not_a_file_without_an_age(self):
        """A file the delimiter found nothing in says nothing about ages."""
        self.assertEqual(self.survey(()).with_no_stated_age, 0)

    def test_the_duplicate_is_not_counted_twice(self):
        corpus = cc.Corpus(day_files=(self.AGELESS,), files=2)
        self.assertEqual(cc.survey_files(corpus).files, 2)
        self.assertEqual(cc.survey_files(corpus).unique_files, 1)


class SurveyFilesSplitsTheCatalogByAgeExtreme(SurveyFilesCase):
    """The evidence for *measure the file in front of you*. Issue #36.

    ``batch-shift`` step 3 quoted four corpus-wide shares and, in the very next
    paragraph, told the reader not to carry a share between the two halves of
    the catalog. The shares are gone; what replaces them is the shape of the
    per-file distribution, which is what makes the instruction an argument
    rather than an assertion. A corpus that really is bimodal has files piled at
    both ends; one sitting uniformly at its own corpus-wide rate -- 65% of 551
    encounters state an age, measured 2026-08-11 -- would have almost none.

    **No threshold is invented.** "Dominant" needs a boundary, and a fourth
    boundary in this repo is a defect waiting to happen — see the age bands. The
    two ends are *every* and *none*, which need no boundary at all, and
    everything else is mixed.

    The three counts overlap the case above at ``with_no_stated_age`` on
    purpose: that field is now one leg of a partition, and a change that got the
    other two right while quietly moving it would pass every test up there.
    """

    def test_a_file_stating_an_age_throughout_counts_at_the_every_end(self):
        self.assertEqual(self.survey(self.EVERY).with_age_in_every_note, 1)

    def test_one_ageless_encounter_moves_a_file_out_of_every(self):
        census = self.survey(self.MIXED)
        self.assertEqual(census.with_age_in_every_note, 0)
        self.assertEqual(census.with_mixed_age, 1)

    def test_a_file_with_no_age_anywhere_is_not_mixed(self):
        census = self.survey(self.AGELESS)
        self.assertEqual(census.with_mixed_age, 0)
        self.assertEqual(census.with_no_stated_age, 1)

    def test_a_single_encounter_file_is_an_end_and_never_the_middle(self):
        """One encounter cannot disagree with itself, so it is always an extreme."""
        census = self.survey(("Note 1\n51 f\n",), ("Note 1\ndob 4/4/44\n",))
        self.assertEqual(census.with_age_in_every_note, 1)
        self.assertEqual(census.with_no_stated_age, 1)
        self.assertEqual(census.with_mixed_age, 0)

    def test_an_empty_file_lands_in_none_of_the_three(self):
        """``all()`` of nothing is true, and an empty file states no ages at all.

        Letting it in at the *every* end is the vacuous-truth bug, and it would
        inflate the exact figure batch-shift now rests on. ``with_no_stated_age``
        already excludes it; this is the same exclusion on the other end.
        """
        census = self.survey(())
        self.assertEqual(census.with_age_in_every_note, 0)
        self.assertEqual(census.with_no_stated_age, 0)
        self.assertEqual(census.with_mixed_age, 0)

    def test_the_three_partition_the_files_that_hold_encounters(self):
        days = (self.AGELESS, self.EVERY, self.MIXED, self.EVERY)
        census = self.survey(*days)
        self.assertEqual(
            census.with_age_in_every_note
            + census.with_no_stated_age
            + census.with_mixed_age,
            len(days),
        )

    def test_it_counts_files_and_not_the_encounters_inside_them(self):
        census = self.survey(self.EVERY, self.EVERY)
        self.assertEqual(census.with_age_in_every_note, 2)


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


class PainScore(unittest.TestCase):
    """The severity marker behind issue #30.

    ``clinical-note`` now requires an OLDCARTS severity on every note, written
    as a pain scale. What the census answers is how often the clinician writes
    one himself -- the population the rule fills for is the remainder, and a
    rule about it should be able to say how large it is.

    The extractor lives beside ``BP_PAIR`` because they read the same shape and
    must not read each other's: ``BloodPressure.test_ignores_a_pain_score``
    is this class seen from the other side.
    """

    def test_a_bare_score(self):
        self.assertEqual(cc.pain_scores("he c/o 8/10 pain"), [8])

    def test_spaces_around_the_slash(self):
        self.assertEqual(cc.pain_scores("rates his pain 2 / 10"), [2])

    def test_both_ends_of_the_scale_are_in_range(self):
        self.assertEqual(cc.pain_scores("0/10 now, was 10/10 overnight"), [0, 10])

    def test_above_the_scale_is_not_a_score(self):
        """``12/10`` is rejected, and the reason is the decoy it shares.

        Patients do say "twelve out of ten", so this loses a real score now and
        then. Above 10 the same characters are far likelier to be a written
        date -- the false positive the module cannot otherwise exclude at all,
        see the limit in ``corpus_census`` -- so the range check is spent where
        it buys the most.
        """
        self.assertEqual(cc.pain_scores("12/10"), [])

    def test_a_score_that_ends_a_sentence(self):
        """The form BP_PAIR's trailing guard would have thrown away.

        Two of day-b's seven scores are written this way, and copying that
        guard verbatim dropped both. On a vital line a following dot is a
        decimal point; in prose it is a full stop.
        """
        self.assertEqual(cc.pain_scores("rates his pain 2/10. there is swelling"), [2])
        self.assertEqual(cc.pain_scores("exacerbated by movment 6/10."), [6])

    def test_a_date_after_the_score_is_still_not_a_score(self):
        # Loosening the trailing guard must not reach the digits: "10/10/25"
        # is a date, and the slash and digit alternatives are what refuse it.
        self.assertEqual(cc.pain_scores("f/u 10/10/25"), [])
        self.assertEqual(cc.pain_scores("wbc 6/100"), [])

    def test_heart_sounds_are_not_a_score(self):
        self.assertEqual(cc.pain_scores("s1,s2 2/2"), [])

    def test_a_blood_pressure_is_not_a_score(self):
        self.assertEqual(cc.pain_scores("bp 121/61 hr 64 t 96.9"), [])

    def test_a_pressure_whose_digits_end_in_ten_is_not_a_score(self):
        # The lookaround is what does this: "10" sits inside "110", so the
        # character before it is a digit and the match is refused. Without it
        # every systolic in the hundreds would offer a "10" to pair with.
        self.assertEqual(cc.pain_scores("bp 110/104"), [])

    def test_a_concentration_is_not_a_score(self):
        self.assertEqual(cc.pain_scores("zithromax 200/5ml 3/4 t x 3 days"), [])

    def test_a_suture_size_is_not_a_score(self):
        # day-b case 6 writes "5 5-0 sutures placed" and carries no pain score;
        # a run that read one there would make the fixture's own split wrong.
        self.assertEqual(cc.pain_scores("lidocaine 1% 5 5-0 sutures placed"), [])

    def test_presence_follows_the_values(self):
        self.assertTrue(cc.has_pain_score("c/o 8/10 body aches"))
        self.assertFalse(cc.has_pain_score("cc: itching, can feel ince in her ears"))

    def test_the_survey_counts_the_notes_not_the_scores(self):
        c = cc.survey(["c/o 8/10 pain, later 6/10", "no score here", "2/10"])
        self.assertEqual(c.with_pain_score, 2)


class DocumentedHypertension(unittest.TestCase):
    """The marker behind the counts issue #23 turned on.

    ``clinical-note`` used to instruct that a documented hypertensive gets a
    hypertensive filled pressure. What decided that rule was how often the
    clinician's *own* transcribed pressures agree with it, and that count is
    only computable if the history marker is extractable. An extractor that
    quietly stopped matching would leave the rule's stated evidence asserting a
    number nobody could recompute -- the failure this whole module exists for.
    """

    def test_the_abbreviation(self):
        self.assertTrue(cc.has_documented_hypertension("hx: htn, djd"))

    def test_the_word_both_ways(self):
        self.assertTrue(cc.has_documented_hypertension("hx of hypertension"))
        self.assertTrue(cc.has_documented_hypertension("known hypertensive"))

    def test_the_code(self):
        self.assertTrue(cc.has_documented_hypertension("pre-existing: I10, E11.9"))

    def test_absent(self):
        self.assertFalse(cc.has_documented_hypertension("cc: cough x 2 days"))

    def test_height_is_not_hypertension(self):
        """``ht`` welded to its value is the shape that defeated other tokens.

        ``\\bhtn\\b`` cannot match inside "ht5'7"" and must not, but the pair is
        close enough in this corpus's shorthand to be worth pinning: three
        encounters were misread once already over exactly this welding.
        """
        self.assertFalse(cc.has_documented_hypertension("bp 122/63, hr 59 ht5'7\" wt145"))
        self.assertFalse(cc.has_documented_hypertension("ht 5'4\" wt 212 lbs"))

    def test_a_negated_mention_still_counts(self):
        """Asserted so the known over-count is visible rather than assumed away.

        No negation guard is carried, on the same reasoning as ``OBESITY``: the
        corpus holds no negated form among the 175 encounters that write the
        token, audited 2026-08-11, so a guard would be exercised by nothing.
        This is the line to change if one appears -- and the test that would
        start failing when it does.
        """
        self.assertTrue(cc.has_documented_hypertension("denies htn"))

    def test_day_b_documents_it_in_exactly_four_cases(self):
        """Two with a pressure and two without, and the pair matters.

        ``DAY_B_HYPERTENSIVE`` is narrower than this on purpose -- it is the two
        B2 anchors, which need the pressure *absent* so the run has to fill one.
        Cases 2 and 3 document the same history and carry a given pressure, so
        they are hypertensives the extractor must find and B2 must not score.
        An extractor matching everything would pass the first assertion alone.
        """
        matched = [n for n in range(1, 13) if cc.has_documented_hypertension(day_b(n))]
        self.assertEqual(matched, list(DAY_B_DOCUMENTS_HTN))
        self.assertEqual(
            [n for n in matched if cc.has_bp(day_b(n))], list(DAY_B_HTN_WITH_BP)
        )

    def test_case_2_is_the_normal_hypertensive_the_rule_rests_on(self):
        """day-b/assertions.md cites this reading by value; here it is checked.

        A *given* 121/61 against a documented hypertension is the in-corpus
        proof that B2's second exit describes a real patient rather than a
        loophole -- and the single clearest refutation of the retired rule that
        a documented hypertensive gets a hypertensive pressure. Case 3 is the
        other way at 147/81, which is what stops the pair being one-sided.
        """
        self.assertEqual(cc.bp_readings(day_b(2)), [(121, 61)])
        self.assertTrue(cc.all_bp_readings_normal(day_b(2)))
        self.assertEqual(cc.bp_readings(day_b(3)), [(147, 81)])
        self.assertFalse(cc.all_bp_readings_normal(day_b(3)))

    def test_the_documented_false_positives_are_the_ones_documented(self):
        """Each is audited at zero in the corpus; each would still match here.

        The comment beside ``HYPERTENSION`` lists three ways it can be wrong and
        says all three cost nothing today. That is a claim about the corpus, not
        about the regex, and this is what stops the two being confused: the
        regex really does behave this way, and the comment is honest only for
        as long as the audit holds.
        """
        # Included wrongly: a different disease, and a non-diagnosis.
        self.assertTrue(cc.has_documented_hypertension("hx: pulmonary hypertension"))
        self.assertTrue(cc.has_documented_hypertension("pre-hypertensive"))
        # Excluded wrongly: the plural defeats the closing boundary.
        self.assertFalse(cc.has_documented_hypertension("two hypertensives seen"))

    def test_the_code_is_matched_in_either_case(self):
        """Wanted, not tolerated -- and asserted because it looks accidental.

        ``I10`` is written with a capital in the pattern, under a leading
        ``(?i)`` that a reader scanning the alternatives can easily miss.
        """
        self.assertTrue(cc.has_documented_hypertension("pre-existing: i10"))
        self.assertTrue(cc.has_documented_hypertension("pre-existing: I10"))

    def test_the_lenient_leg_is_counted_beside_the_strict_one(self):
        """Both legs are printed so the day they diverge is visible.

        The strict figure is the one the rule was written on. It is only safe
        to quote while the difference is inspectable, which is what the lenient
        counter exists to make it.
        """
        c = cc.survey(["hx: htn. bp 162/98, recheck 128/78", "hx: htn. bp 118/70"])
        self.assertEqual(c.hypertension_bp_normal, 1)
        self.assertEqual(c.hypertension_bp_normal_lenient, 2)

    def test_the_survey_counts_the_population_and_its_pressures(self):
        notes = [
            "hx: htn. bp 117/74",  # documented, and normal
            "hx: htn. bp 148/92",  # documented, and not
            "hx: htn, no vitals taken",  # documented, no pressure to count
            "cc: cough. bp 118/70",  # a pressure, but no hypertension
        ]
        c = cc.survey(notes)
        self.assertEqual(c.with_hypertension, 3)
        self.assertEqual(c.hypertension_with_bp, 2)
        self.assertEqual(c.hypertension_bp_normal, 1)
        self.assertEqual(c.hypertension_bp_not_normal, 1)

    def test_a_note_is_normal_only_when_every_reading_is(self):
        """Per note, not per reading, and the strict leg is the safe one.

        A recheck after treatment is the case: counting the note normal on its
        best reading would overstate how often his hypertensives sit at target,
        which is the direction that would flatter the rule being written.
        """
        c = cc.survey(["hx: htn. bp 162/98, recheck 128/78"])
        self.assertEqual(c.hypertension_with_bp, 1)
        self.assertEqual(c.hypertension_bp_normal, 0)


class DocumentedObesity(unittest.TestCase):
    """The markers behind the counts issue #15 turned on.

    A row demanding that a *filled* BMI be consistent with a documented obesity
    needs a case whose shorthand documents one. day-b has none, so the figures
    naming how many the corpus holds are what justify ``fixtures/obesity-bmi``
    existing at all -- and an extractor that quietly stopped matching would leave
    that justification asserting a number nobody could recompute.
    """

    def test_obesity_in_a_history_line(self):
        self.assertTrue(cc.has_documented_obesity("hx: htn, obesity, gerd"))

    def test_the_adjective_counts_too(self):
        self.assertTrue(cc.has_documented_obesity("exam: obese female, nad"))

    def test_morbid_obesity(self):
        self.assertTrue(cc.has_documented_obesity("hx morbid obesity, osa"))

    def test_absent(self):
        self.assertFalse(cc.has_documented_obesity("hx: dm, copd, prostate ca"))

    def test_a_lung_lobe_is_not_an_obesity(self):
        """The decoy that was live in the corpus, not a hypothetical one.

        ``obes`` with no leading boundary matches inside "lobes", and the
        clinician writes lung fields constantly: "crackles in the bilateral
        upper lobes" counted as documented obesity until 2026-08-11. It
        inflated the corpus figure this whole fixture set is justified by,
        which is the silent wrong number this file exists to prevent.
        """
        self.assertFalse(cc.has_documented_obesity("crackles in the bilateral upper lobes"))
        self.assertFalse(cc.has_documented_obesity("wheezing in the b/l lower lobes"))

    def test_a_negated_obesity_is_not_excluded(self):
        """Stated rather than asserted, because there is nothing to exclude.

        ``\bobes`` matches whatever word precedes it, so "no obesity" would
        count. A negation guard is not carried: audited 2026-08-11, the corpus
        contains zero negated forms among the encounters that write the token,
        so the guard would be exercised by nothing and could break silently in
        either direction. This is the line to change if one appears.

        **No count is quoted here on purpose.** An earlier draft said "the five
        encounters", which was the pre-``\b`` figure and stayed behind when the
        lobes decoy dropped it. A number in a docstring is one nothing
        recomputes; ``corpus_census.py`` prints the live one.
        """
        self.assertTrue(cc.has_documented_obesity("denies obesity"))  # by design

    def test_bariatric_surgery(self):
        for shorthand in (
            "hx gastric bypass 2016",
            "s/p bariatric surgery",
            "hx: sleeve gastrectomy, chole",
            "lap band placed, then removed",
            "s/p roux-en-y",
        ):
            with self.subTest(shorthand=shorthand):
                self.assertTrue(cc.has_bariatric_history(shorthand))

    def test_bariatric_absent(self):
        self.assertFalse(cc.has_bariatric_history("hx: chole, btl, d&c"))

    def test_bariatric_is_not_obesity(self):
        """The two markers are deliberately separate, and O2 rests on the split.

        A post-bypass patient is where a sub-30 BMI is *plausible and
        accountable* -- the second exit -- while a written "obesity" is where an
        unexplained sub-30 BMI is the defect. Folding them into one marker would
        lose the distinction the set is built on.
        """
        self.assertFalse(cc.has_documented_obesity("s/p gastric bypass"))
        self.assertFalse(cc.has_bariatric_history("hx: obesity"))

    def test_sleep_apnea(self):
        for shorthand in ("hx osa", "uses cpap nightly", "obstructive sleep apnea"):
            with self.subTest(shorthand=shorthand):
                self.assertTrue(cc.has_sleep_apnea(shorthand))

    def test_osa_needs_its_own_word(self):
        # The token is three letters and would otherwise fire inside a longer one.
        self.assertFalse(cc.has_sleep_apnea("hx: rosacea, gerd"))

    def test_body_measurement_is_the_union_of_height_and_weight(self):
        self.assertTrue(cc.has_body_measurement("ht 5'4\" wt 212 lbs"))
        self.assertTrue(cc.has_body_measurement("wt 212"))
        self.assertTrue(cc.has_body_measurement("36in"))
        self.assertFalse(cc.has_body_measurement("bp 142/88 hr 79 t 98.1"))

    def test_the_survey_counts_the_qualifying_shape(self):
        """Documented obesity *and* no body measurement -- the fixturable case."""
        c = cc.survey(
            [
                "hx: obesity, htn\ncc: cough",          # qualifies
                "hx: obesity\nht 5'4\" wt 240",          # documented, measured
                "hx: gastric bypass\ncc: sore throat",   # bariatric, qualifies
                "hx: dm\ncc: rash",                      # neither
            ]
        )
        self.assertEqual(c.with_obesity, 2)
        self.assertEqual(c.obesity_no_measurement, 1)
        self.assertEqual(c.with_bariatric, 1)
        self.assertEqual(c.bariatric_no_measurement, 1)


class HedgedDiagnosis(unittest.TestCase):
    """Guards the figure drift row 13 cites, and the decoys that inflate it.

    The row is in ``skills/clinical-note/SKILL.md`` and it turns on a rate: a
    differential is generated in every note, a hedge appears in the shorthand of
    about one in sixteen, and the row's two halves therefore fire at very
    different frequencies. Issue #19 published that percentage before anything
    could recompute it. This is what recomputes it.

    Every token here is a **prefix or boundary** match for the same reason
    ``OBESITY`` is: a four-letter clinical token hides inside longer words, and
    this corpus is where that was learned. ``prob`` is the live case --
    ``fixtures/day-a/shorthand/case-10.md`` writes "he states he has problems
    urinatin", and a bare ``prob`` counts that encounter as hedged.
    """

    OBESITY_BMI = REPO_ROOT / "fixtures" / "obesity-bmi" / "shorthand"

    def test_prob_alone(self):
        self.assertTrue(cc.has_hedge("dx prob viral uri"))

    def test_probable_and_probably(self):
        self.assertTrue(cc.has_hedge("probable strep"))
        self.assertTrue(cc.has_hedge("probably viral"))

    def test_a_problem_is_not_a_hedge(self):
        """The decoy, asserted against the fixture that carries it."""
        self.assertFalse(cc.has_hedge("he states he has problems urinatin"))
        self.assertFalse(cc.has_hedge(fixture("case-10.md")))

    def test_possible_forms(self):
        for text in ("poss ptx", "possible cellulitis", "possibly viral"):
            with self.subTest(text=text):
                self.assertTrue(cc.has_hedge(text))

    def test_suspected_forms(self):
        for text in ("susp fx", "suspected strep", "suspicion for pe"):
            with self.subTest(text=text):
                self.assertTrue(cc.has_hedge(text))

    def test_rule_out(self):
        self.assertTrue(cc.has_hedge("r/o pna"))
        self.assertTrue(cc.has_hedge("R/O fracture"))

    def test_versus(self):
        self.assertTrue(cc.has_hedge("bronchitis vs pna"))

    def test_a_vital_signs_header_is_not_a_versus(self):
        """``VS`` opens a vital line and would otherwise read as a hedge.

        The colon is **not** what distinguishes them, which a first version of
        this guard assumed: he writes ``VS 138/86`` and ``VS- 138/86`` too, and
        both slipped through a lookahead that only rejected ``VS:``. What
        actually separates the two is what follows -- a vital line runs into a
        number, a differential runs into a diagnosis.
        """
        for text in ("VS: 138/86, hr 88, t 98.8", "vs : 138/86", "VS 138/86 hr 88",
                     "VS- 138/86", "VS. 98.6"):
            with self.subTest(text=text):
                self.assertFalse(cc.has_hedge(text))

    def test_a_spelled_out_suspension_is_not_a_suspicion(self):
        """Ordinary pediatric prescribing, and it would inflate the count."""
        for text in ("amoxicillin suspension 400/5", "amox suspended"):
            with self.subTest(text=text):
                self.assertFalse(cc.has_hedge(text))

    def test_an_abbreviated_suspension_still_counts(self):
        """The limit the guard cannot reach, pinned rather than wished away.

        ``susp 250/5ml`` is a suspension and ``susp fx`` is a suspicion, and the
        four letters are identical. HEDGE says so in prose; this is the test that
        makes the claim checkable, and it is why the figure is a proxy.
        """
        self.assertTrue(cc.has_hedge("susp 250/5ml"))

    def test_a_genuine_question_counts_and_that_is_deliberate(self):
        """A known over-count, pinned so it stays a decision rather than a bug.

        ``[a-z]\\?`` is the loosest alternative in HEDGE and it cannot tell
        ``strep?`` from a question written into the prose. It is kept because
        issue #19's published table counted the same seven tokens, so the figure
        stays comparable to the one already on the ticket -- and because the
        figure is quoted as a proxy rather than a bound.
        """
        self.assertTrue(cc.has_hedge("pt asks: is this contagious?"))

    def test_the_prefixed_question_mark_is_not_matched(self):
        """``?fx`` is the other shorthand form, and it is deliberately absent.

        No committed fixture carries it and the corpus cannot be audited from
        every clone, so an alternative matched by nothing is one nothing can
        catch going wrong -- the reasoning ``SLEEP_APNEA`` already carries for
        ``apnoea``. This is the line to change if the form turns up.
        """
        self.assertFalse(cc.has_hedge("?fx right wrist"))

    def test_likely(self):
        self.assertTrue(cc.has_hedge("likely viral"))

    def test_unlikely_is_deliberately_not_counted(self):
        """A rejection is a conclusion, not a hedge, and the count says so."""
        self.assertFalse(cc.has_hedge("unlikely to be bacterial"))

    def test_a_question_mark_suffix(self):
        self.assertTrue(cc.has_hedge("strep? throat cx sent"))

    def test_a_plain_note_carries_none(self):
        self.assertFalse(cc.has_hedge("cc: sore throat x 3 days\ndx strep pharyngitis"))

    def test_day_a_and_day_b_carry_no_hedge(self):
        """Why no hedged-input assertion can be written against either set."""
        for path in sorted(FIXTURES.glob("case-*.md")) + sorted(DAY_B.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertFalse(cc.has_hedge(path.read_text(encoding="utf-8")))

    def test_obesity_bmi_case_1_does_carry_one(self):
        """Issue #19 said no committed fixture carries a hedge token. One does.

        ``possibly ultrasounds there`` hedges **a past test**, not a diagnosis,
        so the ticket's substantive point survives: nothing committed can anchor
        an assertion about a hedged *diagnosis*. The token count is what was
        wrong, and this is the case that would have failed a blanket claim.
        """
        self.assertTrue(cc.has_hedge((self.OBESITY_BMI / "case-01.md").read_text(encoding="utf-8")))

    def test_the_survey_counts_hedged_encounters(self):
        c = cc.survey(
            [
                "dx prob viral uri",              # hedged
                "bronchitis vs pna",              # hedged
                "he has problems urinatin",       # the decoy
                "cc: rash\ndx contact dermatitis",  # plain
            ]
        )
        self.assertEqual(c.with_hedge, 2)


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
        not via a height token, so asserting it beside cases 3 and 4 would make
        the *input* look tidier than it is.

        What the reference read settled (2026-08-11) is the clinical question --
        62 is a height, so day-b's B4 now covers case 2. It did not settle the
        extraction question this test guards: the shorthand still carries no
        height token, and an extractor that only looked for one would miss it.
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

    def test_the_d6_anchor_documents_a_contact_and_orders_no_test(self):
        """D6 is only checkable while case 9's plan stays empty of testing.

        The row asks the skill to order COVID-19, influenza and strep swabs from
        a documented positive contact ([issue #32]). Writing any of those into
        the input would make it a *given* order, and the row would pass having
        tested nothing -- the same way a vital added to one of the nine would
        void B1. The exposure itself is asserted rather than assumed for the
        opposite reason: remove it and the row fails a correct note.

        [issue #32]: https://github.com/mshamblin5150-code/clinical-skills/issues/32
        """
        self.assertIn("postive for covid", day_b(9).lower())  # typo preserved
        for token in ("covid", "flu", "strep", "swab", "rsv"):
            with self.subTest(token=token):
                self.assertNotIn(token, day_b_plan(9))

    def test_the_two_contacts_he_did_swab_carry_the_order(self):
        """D6's prose claims swabbing a documented contact is his own practice.

        Cases 8 and 12 are where the same shift did it, and they are what makes
        case 9 a lapse rather than a house style. Asserted here so the claim
        breaks loudly if either input is edited.
        """
        self.assertIn("covid", day_b_plan(8))
        for token in ("covid", "strep", "flu"):
            with self.subTest(token=token):
                self.assertIn(token, day_b_plan(12))

    def test_the_d7_anchor_documents_a_lung_finding_and_orders_no_imaging(self):
        """D7 is only checkable while case 9's plan stays empty of imaging.

        The same shape as D6 one row up, and asserted for the same two opposite
        reasons. The finding is asserted because removing it would fail a
        correct note; the absent order is asserted because writing a film into
        the input would make it a *given* and the row would pass having tested
        nothing -- exactly how a vital added to one of the nine would void B1.

        [issue #27]: https://github.com/mshamblin5150-code/clinical-skills/issues/27
        """
        self.assertIn("lung sounds diminished", day_b(9).lower())
        for token in ("cxr", "xray", "x-ray", "radiograph", "film", "imaging"):
            with self.subTest(token=token):
                self.assertNotIn(token, day_b_plan(9))

    def test_the_film_he_did_order_is_on_the_same_shift(self):
        """D7's prose claims imaging a diminished lung base is his own practice.

        Case 7 is where this shift did it -- ``diminished in bases`` on exam and
        ``cxr`` in the plan -- which is what makes case 9 a lapse rather than a
        house style. It is also why case 7 cannot host the row itself: the order
        is a given there, so a run that merely copied the input would pass. Same
        reason case 10 is not a second D6.
        """
        self.assertIn("diminished in bases", day_b(7).lower())
        self.assertIn("cxr", day_b_plan(7))

    def test_the_three_lung_rows_sit_on_vital_less_cases(self):
        """B9's ground: D2, D3 and D7 are each open to a filled dismissal.

        All three cases are filled a complete vital set, so all three rows can
        be answered by naming the finding and disposing of it on two invented
        numbers. That is the cheat B9 closes, and it stops being the reason B9
        exists the moment any of these three acquires a vital line.
        """
        for n, finding in DAY_B_LUNG_FINDING.items():
            with self.subTest(case=n):
                note = day_b(n)
                self.assertIn(finding, note.lower())
                self.assertFalse(cc.has_any_vital(note))

    def test_b9_reaches_every_case_with_something_generated(self):
        """B9's list is a union, and case 3 is the member easy to lose.

        The row reaches any case where something in the filled-vitals license
        class was generated -- a vital, a body measurement, or the OLDCARTS
        severity. That is the vital-less nine *plus* case 3, whose vital line is
        complete and whose severity the run must invent. Derived from the inputs
        here rather than copied from B1's list, because the first draft of the
        row did copy B1 and dropped her.

        [issue #27]: https://github.com/mshamblin5150-code/clinical-skills/issues/27
        """
        reached = tuple(
            n
            for n in range(1, 13)
            if not cc.has_any_vital(day_b(n))
            or not (cc.has_pain_score(day_b(n)) or re.search(NO_PAIN, day_b(n)))
        )
        self.assertEqual(reached, DAY_B_B9)

    def test_the_two_cases_b9_does_not_reach_supply_both(self):
        """Cases 2 and 4 are outside B9, and the row is vacuous on them.

        Both carry a full vital line and both settle the severity in the
        shorthand, so a run has nothing generated to reason from and B9 has
        nothing to check. This is what makes the exclusion a property of the
        inputs rather than an oversight.

        **The two settle it differently**, and asserting a score on both would
        be wrong: case 4 writes ``5``, while case 2 writes ``no pain`` -- an
        absence, which is a given scoring 0/10 rather than a value to invent.
        ``DAY_B_NO_PAIN`` is the split, and the first version of this test
        failed on exactly that distinction.
        """
        for n in (2, 4):
            with self.subTest(case=n):
                note = day_b(n)
                self.assertTrue(cc.has_any_vital(note))
                self.assertTrue(cc.has_pain_score(note) or re.search(NO_PAIN, note))

    def test_seven_cases_transcribe_a_severity(self):
        """B7's list, with the value each case must survive with."""
        for n, score in DAY_B_PAIN_SCORE.items():
            with self.subTest(case=n):
                self.assertEqual(cc.pain_scores(day_b(n)), [score])

    def test_two_cases_write_the_absence_of_pain(self):
        """B7's other half, and it is a given rather than a silence.

        Cases 2 and 12 say "no pain" outright, so 0/10 there is transcribed and
        not the bland fill the rule forbids. A run that scores either of them
        above zero has invented a symptom, which standing rule 2 covers without
        any exception -- the severity license buys a number for a complaint the
        shorthand documents, not a complaint.
        """
        for n in DAY_B_NO_PAIN:
            with self.subTest(case=n):
                note = day_b(n)
                self.assertRegex(note, NO_PAIN)
                self.assertFalse(cc.has_pain_score(note))

    def test_three_cases_leave_the_severity_to_be_filled(self):
        """No number written, and no absence written either.

        B5 and B6 reach all twelve, but these three are the only ones where the
        severity is *invented* rather than transcribed. Writing a score into any
        of them, or writing "no pain" into one, would start failing correct
        notes -- the same trap ``obesity-bmi``'s control guard exists for.
        """
        for n in DAY_B_SEVERITY_FILLED:
            with self.subTest(case=n):
                note = day_b(n)
                self.assertFalse(cc.has_pain_score(note))
                self.assertNotRegex(note, NO_PAIN)

    def test_two_of_the_seven_scores_end_a_sentence(self):
        """The count day-b's prose quotes, computed rather than eyeballed.

        It is the count that justifies the narrowed trailing guard in
        ``PAIN_SCORE``. Written by hand it would have been the one figure in
        this set nothing recomputes -- and it was, until the review caught it.
        """
        sentence_final = [
            n for n in sorted(DAY_B_PAIN_SCORE) if re.search(r"/\s*10\s*\.", day_b(n))
        ]
        self.assertEqual(sentence_final, [5, 11])

    def test_b8_takes_two_of_those_three_and_leaves_the_boundary_out(self):
        """Case 3 itches; B8 demands a score above 0/10 and she is not in it.

        Asserted rather than assumed, because the two lists differing by
        exactly one case is the whole of B8's design, and a future edit that
        "tidied" them into agreement would enforce a ruling nobody made --
        whether a non-painful complaint scores 0/10 or scores its own
        intensity. day-b lists that under *Still unresolved*.
        """
        self.assertEqual(
            sorted(set(DAY_B_SEVERITY_FILLED) - set(DAY_B_SEVERITY_NONZERO)), [3]
        )

    def test_the_severity_split_is_the_whole_set(self):
        self.assertEqual(
            sorted(tuple(DAY_B_PAIN_SCORE) + DAY_B_NO_PAIN + DAY_B_SEVERITY_FILLED),
            list(range(1, 13)),
        )


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


class ObesityBmiIsTheDocumentedObesitySet(unittest.TestCase):
    """Guards the property every obesity-bmi assertion rests on.

    Two properties, and O2 needs both. The set's cases must carry **no body
    measurement**, so the BMI under test is wholly invented -- a weight alone
    would be enough to void it, because a given weight plus a filled height
    makes the arithmetic partly real. And the anchors must document obesity
    while the controls must not: fold those two groups together and the row
    loses the distinction between "a BMI below 30 contradicts a given" and "a
    BMI below 30 is exactly what a successful bypass looks like".
    """

    OBESITY_BMI = REPO_ROOT / "fixtures" / "obesity-bmi" / "shorthand"
    ANCHORS = (1, 2)      # the shorthand writes "obese" / "obesity"
    CONTROLS = (3, 4)     # a bariatric history, and no claim about today

    def case(self, number: int) -> str:
        return (self.OBESITY_BMI / f"case-{number:02d}.md").read_text(encoding="utf-8")

    def test_the_set_has_four_cases(self):
        self.assertEqual(len(sorted(self.OBESITY_BMI.glob("case-*.md"))), 4)

    def test_every_case_is_exactly_one_note(self):
        for path in sorted(self.OBESITY_BMI.glob("case-*.md")):
            with self.subTest(case=path.name):
                self.assertEqual(len(cc.split_notes(path.read_text(encoding="utf-8"))), 1)

    def test_no_case_carries_a_body_measurement(self):
        """The row under test is about a BMI with no given input at all."""
        for n in self.ANCHORS + self.CONTROLS:
            with self.subTest(case=n):
                self.assertFalse(cc.has_body_measurement(self.case(n)))

    def test_no_case_carries_any_vital(self):
        for n in self.ANCHORS + self.CONTROLS:
            with self.subTest(case=n):
                self.assertFalse(cc.has_any_vital(self.case(n)))

    def test_the_anchors_document_obesity(self):
        for n in self.ANCHORS:
            with self.subTest(case=n):
                self.assertTrue(cc.has_documented_obesity(self.case(n)))

    def test_the_controls_document_a_bariatric_history_and_not_an_obesity(self):
        """Both halves are load-bearing, and O5 is why the second one is.

        O5 forbids obesity being written into these two patients' histories,
        on the ground that the shorthand documents the surgery and never the
        diagnosis. Add the word to either input and the row starts failing
        correct notes -- so this asserts the premise rather than trusting it.
        """
        for n in self.CONTROLS:
            with self.subTest(case=n):
                note = self.case(n)
                self.assertTrue(cc.has_bariatric_history(note))
                self.assertFalse(cc.has_documented_obesity(note))

    def test_the_anchors_carry_no_bariatric_history(self):
        """Otherwise O2's second exit would be available on every case."""
        for n in self.ANCHORS:
            with self.subTest(case=n):
                self.assertFalse(cc.has_bariatric_history(self.case(n)))

    def test_every_case_states_an_age(self):
        """Including case 2, whose age was derived before its birth date came out."""
        for n in self.ANCHORS + self.CONTROLS:
            with self.subTest(case=n):
                self.assertIsNotNone(cc.age_in_years(self.case(n)))

    def test_no_case_carries_a_date_of_birth(self):
        for n in self.ANCHORS + self.CONTROLS:
            with self.subTest(case=n):
                self.assertFalse(cc.has_dob(self.case(n)))

    def test_the_split_is_the_whole_set(self):
        numbers = [
            int(p.stem.split("-")[1]) for p in sorted(self.OBESITY_BMI.glob("case-*.md"))
        ]
        self.assertEqual(numbers, sorted(self.ANCHORS + self.CONTROLS))


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
            files=cc.FileCensus(
                files=1, unique_files=1, with_no_stated_age=0,
                with_age_in_every_note=1, with_mixed_age=0,
            ),
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

    def report(self, files: int = 11, unique: int = 10) -> str:
        return cc.format_report(
            cc.survey(self.notes), source="fixtures", date="2026-08-11",
            bands=cc.survey_bands(self.notes),
            files=cc.FileCensus(
                files=files, unique_files=unique, with_no_stated_age=1,
                with_age_in_every_note=4, with_mixed_age=5,
            ),
        )

    def test_report_emits_no_note_text(self):
        """Standing rule 1: the census output must be safe to paste anywhere."""
        report = self.report()
        for leak in ("cc:", "hx:", "exam:", "[PT]", "plan "):
            with self.subTest(leak=leak):
                self.assertNotIn(leak, report)

    def test_format_report_is_never_handed_a_note(self):
        """The invariant the module docstring states, asserted rather than trusted.

        ``Corpus`` holds note text and ``FileCensus`` does not, which is the whole
        reason the second type exists. A signature that took the first would put
        note text one formatting mistake away from the console.
        """
        # ``from __future__ import annotations`` keeps these as strings.
        annotations = cc.format_report.__annotations__
        self.assertNotIn("Corpus", annotations.values())
        self.assertEqual(annotations["files"], "FileCensus")
        for field in cc.FileCensus.__dataclass_fields__.values():
            with self.subTest(field=field.name):
                self.assertEqual(field.type, "int")

    def test_reports_the_duplicate_when_there_is_one(self):
        self.assertIn("files: 11 (10 unique)", self.report())

    def test_says_nothing_about_uniqueness_when_no_file_repeats(self):
        report = self.report(files=10, unique=10)
        files_line = next(l for l in report.splitlines() if l.startswith("files:"))
        self.assertEqual(files_line, "files: 10")


if __name__ == "__main__":
    unittest.main()
