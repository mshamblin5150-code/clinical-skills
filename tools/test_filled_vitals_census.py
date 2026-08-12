"""Tests for the filled-vitals census.

These run against the twelve committed notes in ``fixtures/filled-anchor/notes/``
and against inline strings. They never touch ``scratch/`` or ``output/``.

**The fixture numbers below are the evidence for issue #67**, and pinning them is
half of what this file is for. Those twelve notes are **day-b run 1**, byte for
byte, so the counts over them are a fact about a run that happened rather than a
bar anything has to clear -- and a run record is exactly the kind of thing that gets quietly
"tidied". Four of the nine filled heights are 5'10", including the 17-year-old's;
six of the nine filled pressures land not-normal against a corpus that
splits about evenly. An edit that changed either number would void the argument in
``skills/clinical-note/SKILL.md`` and in ``fixtures/day-b/assertions.md`` without
touching a word of either.

The other half is the silent failure mode every extractor here shares with
``corpus_census``: a regex that stops matching reports zero and reads as good news.
``NineOfTwelveDeclareAFilledBody`` is the guard -- cases 2, 3 and 4 carry given
body values and must keep reading as given.
"""

import tempfile
import textwrap
import unittest
from pathlib import Path

import filled_vitals_census as fvc

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTES = REPO_ROOT / "fixtures" / "filled-anchor" / "notes"

# day-b's nine vital-less encounters, carried one stage down the pipeline. The
# other three -- 2, 3 and 4 -- are the given-vitals controls, and the census must
# read all three as declaring no filled body value at all.
FILLED_CASES = (1, 5, 6, 7, 8, 9, 10, 11, 12)
GIVEN_CASES = (2, 3, 4)


def note(name: str) -> str:
    return (NOTES / name).read_text(encoding="utf-8")


def all_notes() -> list[str]:
    return [p.read_text(encoding="utf-8") for p in sorted(NOTES.glob("case-*.md"))]


def written(directory: Path, **notes: str) -> Path:
    for name, text in notes.items():
        (directory / f"{name}.md").write_text(text, encoding="utf-8")
    return directory


class FilledBlock(unittest.TestCase):
    """The block is found by a tier key at column 0, never by the phrase."""

    def test_reads_from_the_asserted_key_to_the_next_key(self):
        text = textwrap.dedent(
            """\
            DERIVED           BMI 26.5 = 703 x 185 / 70^2.
            FILLED·asserted   BP 138/86 filled.
                              HEIGHT 5'10" (70 in) filled.
            FILLED·proposed   Ibuprofen 400 mg PO q6h PRN.
            FLAG              None.
            """
        )
        block = fvc.filled_block(text)
        self.assertIn("BP 138/86 filled", block)
        self.assertIn("HEIGHT 5'10\" (70 in) filled", block)
        self.assertNotIn("Ibuprofen", block)
        self.assertNotIn("BMI 26.5", block)

    def test_the_phrase_in_the_note_body_does_not_open_a_block(self):
        """``case-03`` writes "listed in FILLED·asserted" in its prose.

        A matcher that opened a block there would read a whole note body as
        declared-filled content, which is how a given value becomes a filled one.
        """
        text = "hydrochlorothiazide 25 mg — inferred, listed in FILLED·asserted, confirm.\n"
        self.assertEqual(fvc.filled_block(text), "")

    def test_a_note_with_no_block_reads_empty(self):
        self.assertEqual(fvc.filled_block("SUBJECTIVE\n\nOBJECTIVE\n"), "")

    def test_the_middle_dot_is_not_required(self):
        """An ASCII ``FILLED.asserted`` or ``FILLED asserted`` still opens it."""
        for key in ("FILLED·asserted", "FILLED.asserted", "FILLED asserted"):
            with self.subTest(key=key):
                text = f"{key}   BP 120/70 filled.\nFLAG              None.\n"
                self.assertIn("BP 120/70 filled", fvc.filled_block(text))


class Declarations(unittest.TestCase):
    """A value counts as filled only where the block declares it so.

    This is ``clinical-note``'s own mandated form -- *not ``blood pressure
    filled`` -- ``BP 142/88 filled``* -- and reusing it as the discriminator is
    what lets the census tell a filled value from one the block merely mentions.
    """

    def test_a_labeled_value_followed_by_filled_is_a_declaration(self):
        fill = fvc.read_fill("FILLED·asserted   BP 138/86 filled. HEIGHT 5'10\" (70 in) filled.\n")
        self.assertEqual(fill.pressure, (138, 86))
        self.assertEqual(fill.height_in, 70)

    def test_a_value_the_block_only_mentions_is_not_declared(self):
        """``case-04`` names its given 6'2" inside the block to explain a BMI."""
        fill = fvc.read_fill(
            "FILLED·asserted   BMI 25.7 = 703 x 200 / 74^2, from the given Ht 6'2\" and\n"
            "                  the given Wt 200 lb. Both inputs are given.\n"
        )
        self.assertIsNone(fill.height_in)
        self.assertIsNone(fill.weight_lb)

    def test_a_given_value_in_a_sentence_ending_in_filled_is_still_given(self):
        """The 80-character window's own failure mode, guarded.

        One sentence can name a given height and reach the word ``filled`` about
        something else. Without the guard this reads 6'2" as a filled height —
        a given value counted as generated, which is the direction that matters.
        """
        fill = fvc.read_fill(
            "FILLED·asserted   BMI 25.7 from the given Ht 6'2\" and Wt 200 lb filled.\n"
        )
        self.assertIsNone(fill.height_in)

    def test_a_filled_line_naming_a_given_anchor_still_reads(self):
        """And this is why the guard looks only at the words before the label.

        Drift row 19 requires a filled value's line to name what it was reasoned
        from, and the anchors are usually givens. A guard scanning the clause
        would reject the lines the rule exists to produce.
        """
        fill = fvc.read_fill(
            "FILLED·asserted   From the given pulse of 112, BP 138/86 filled.\n"
        )
        self.assertEqual(fill.pressure, (138, 86))

    def test_a_counterfactual_height_is_not_the_filled_one(self):
        """Threshold-proximity disclosures name the adjacent value on purpose."""
        fill = fvc.read_fill(
            "FILLED·asserted   HEIGHT 5'4\" (64 in) filled; BMI 30.0. Within 1.0 of the\n"
            "                  obesity threshold — 5'5\" gives 29.1, and the workup drops.\n"
        )
        self.assertEqual(fill.height_in, 64)

    def test_a_height_in_bare_inches_reads(self):
        """Otherwise the row is evadable by formatting, which is #70's defect.

        A run writing ``70 in`` rather than ``5'10"`` would declare no height,
        and a set with no declared heights shares no bodies and exits 0.
        """
        fill = fvc.read_fill("FILLED·asserted   HEIGHT 70 in filled. WEIGHT 190 lb filled.\n")
        self.assertEqual(fill.height_in, 70)
        self.assertEqual(fill.body, (70, 190))

    def test_the_feet_form_wins_over_the_inches_gloss(self):
        """``5'10" (70 in)`` is one height written twice, not two."""
        fill = fvc.read_fill("FILLED·asserted   HEIGHT 5'10\" (70 in) filled.\n")
        self.assertEqual(fill.height_in, 70)

    def test_lowercase_and_abbreviated_labels_both_read(self):
        fill = fvc.read_fill("FILLED·asserted   Ht 5'10\" filled. Wt 198 lb filled.\n")
        self.assertEqual(fill.height_in, 70)
        self.assertEqual(fill.weight_lb, 198)

    def test_an_empty_block_declares_nothing(self):
        fill = fvc.read_fill("")
        self.assertIsNone(fill.height_in)
        self.assertIsNone(fill.weight_lb)
        self.assertIsNone(fill.pressure)


class NineOfTwelveDeclareAFilledBody(unittest.TestCase):
    """The set's own split, guarded so an edit to it fails loudly.

    day-b's nine vital-less encounters are the whole reason that set exists, and
    the three controls are what stop every row above passing vacuously. If a
    control ever reads as filled, the counts below stop being about filled values.
    """

    def test_the_nine_declare_a_filled_pressure_height_and_weight(self):
        for n in FILLED_CASES:
            with self.subTest(case=n):
                fill = fvc.read_fill(note(f"case-{n:02d}.md"))
                self.assertIsNotNone(fill.pressure)
                self.assertIsNotNone(fill.height_in)
                self.assertIsNotNone(fill.weight_lb)

    def test_the_three_controls_declare_no_filled_body_value(self):
        for n in GIVEN_CASES:
            with self.subTest(case=n):
                fill = fvc.read_fill(note(f"case-{n:02d}.md"))
                self.assertIsNone(fill.pressure)
                self.assertIsNone(fill.height_in)
                self.assertIsNone(fill.weight_lb)


class TheRunRecordRepeatsItsHeights(unittest.TestCase):
    """Issue #67's evidence, recomputed from committed files.

    day-b's own run-2 finding lives in a gitignored directory and cannot be
    checked by a reader with only this repo. This is the same defect in the run
    record the repo does ship.
    """

    def setUp(self):
        self.census = fvc.survey(all_notes())

    def test_the_set_is_twelve_notes_and_the_readme_is_not_one(self):
        read = fvc.read_notes(NOTES)
        self.assertEqual(len(read), 12)
        self.assertFalse([t for t in read if t.startswith("# filled-anchor")])

    def test_nine_filled_heights_over_four_distinct_values(self):
        self.assertEqual(self.census.heights, 9)
        self.assertEqual(self.census.distinct_heights, 4)

    def test_the_largest_height_group_is_four_notes(self):
        self.assertEqual(self.census.largest_height_group, 4)

    def test_every_weight_is_distinct(self):
        self.assertEqual(self.census.weights, 9)
        self.assertEqual(self.census.distinct_weights, 9)

    def test_no_two_notes_share_a_body(self):
        """The row this run passes and day-b's run 2 does not.

        Run 2 handed cases 1 and 5 an identical 5'10" / 190 lb at ages 36 and 68.
        Nothing here does that, which is why the row is worth having: it is not
        a bar written to be cleared by the run in front of it.
        """
        self.assertEqual(self.census.repeated_bodies, 0)

    def test_six_of_the_nine_filled_pressures_are_not_normal(self):
        """Against a corpus that splits about evenly at 130/80.

        ``skills/clinical-note/SKILL.md`` measures 249 transcribed pressures,
        half of them below 130/80, and says outright that neither default is
        available. Six of nine is the tilt issue #67 names. **Not normal** is
        systolic 130 or above *or* diastolic 80 or above, which is day-b B2's
        wording and not the same predicate as *at or above 130/80*.
        """
        self.assertEqual(self.census.pressures, 9)
        self.assertEqual(self.census.abnormal_pressures, 6)

    def test_run_1_repeated_no_pressure_and_run_2_did(self):
        """The one #67 pattern this run record does **not** carry.

        day-b's run 2 wrote ``138/84`` twice and ``138/86`` twice. Run 1's nine
        are nine distinct readings, so the pressure defect it does carry is the
        tilt above rather than repetition — two different failures of one rule,
        which is why R5 counts both.
        """
        self.assertEqual(self.census.distinct_pressures, 9)
        self.assertEqual(self.census.largest_pressure_group, 1)


class TheReportPrintsCountsOnly(unittest.TestCase):
    """Same rule ``corpus_census`` holds itself to, for the same reason.

    These notes are PHI-free fixtures, but the tool's real target is a run
    directory under ``scratch/`` or ``output/``. A weight is not an identifier on
    its own and a 373 lb one in a small county is closer to being one than the
    tool can judge, so the default output carries no value at all.
    """

    def setUp(self):
        self.census = fvc.survey(all_notes())

    def test_no_measured_value_reaches_the_default_report(self):
        report = fvc.format_report(self.census, source="notes")
        for value in ("5'10", "138/86", "185", "198", "205", "210"):
            with self.subTest(value=value):
                self.assertNotIn(value, report)

    def test_the_counts_do_reach_it(self):
        report = fvc.format_report(self.census, source="notes")
        self.assertIn("9", report)
        self.assertIn("largest", report.lower())

    def test_show_reveals_the_repeated_values(self):
        report = fvc.format_report(self.census, source="notes", show=True)
        self.assertIn("5'10\"", report)

    def test_the_source_name_is_the_only_free_text(self):
        report = fvc.format_report(self.census, source="filled-anchor/notes")
        self.assertIn("filled-anchor/notes", report)


class ExitStatusReportsTheDefect(unittest.TestCase):
    """A grader that cannot fail is a grader nothing checks.

    ``fixtures/day-b`` B13 asks that no two cases share an identical filled body.
    The tool answers it with an exit status so a run cannot report a pass by
    printing something reassuring.
    """

    BODY = "FILLED·asserted   HEIGHT 5'10\" (70 in) filled. WEIGHT 190 lb filled.\n"

    def test_a_set_with_no_repeated_body_exits_zero(self):
        self.assertEqual(fvc.main([str(NOTES)]), 0)

    def test_a_repeated_body_exits_non_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = written(Path(tmp), a=self.BODY, b=self.BODY)
            self.assertEqual(fvc.survey(fvc.read_notes(directory)).repeated_bodies, 1)
            self.assertEqual(fvc.main([str(directory)]), 1)

    def test_two_different_bodies_exit_zero(self):
        """So the non-zero above is the repeat and not the temp directory."""
        with tempfile.TemporaryDirectory() as tmp:
            other = self.BODY.replace("190 lb", "165 lb")
            self.assertEqual(fvc.main([str(written(Path(tmp), a=self.BODY, b=other))]), 0)

    def test_a_directory_with_no_notes_exits_non_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(fvc.main([str(Path(tmp))]), 1)

    def test_a_directory_that_is_not_there_exits_non_zero(self):
        self.assertEqual(fvc.main([str(REPO_ROOT / "no-such-directory")]), 1)


if __name__ == "__main__":
    unittest.main()
