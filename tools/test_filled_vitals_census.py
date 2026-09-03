"""Tests for the filled-vitals census.

These run against the twelve committed notes in ``fixtures/filled-anchor/notes/``
and against inline strings. They never touch ``scratch/`` or ``output/``.

**The fixture numbers below are the evidence for issue #67**, and pinning them is
half of what this file is for. Those twelve notes are **day-b run 1**, byte for
byte apart from two redacted site names, so the counts over them are a fact
about a run that happened rather than a bar anything has to clear -- and a run
record is exactly the kind of thing that gets quietly "tidied". Four of the nine filled heights are 5'10", including the 17-year-old's;
six of the nine filled pressures land not-normal against a corpus that
splits about evenly. An edit that changed either number would void the argument in
``skills/clinical-note/SKILL.md`` and in ``fixtures/day-b/assertions.md`` without
touching a word of either.

The other half is the silent failure mode every extractor here shares with
``corpus_census``: a regex that stops matching reports zero and reads as good news.
``NineOfTwelveDeclareAFilledBody`` is the guard -- cases 2, 3 and 4 carry given
body values and must keep reading as given.
"""

import io
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import filled_vitals_census as fvc
import run_grader

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


class TheKeyHeadsALineRatherThanOpeningASentence(unittest.TestCase):
    """A column-0 match is not enough, and two committed notes prove it.

    The module used to open a block on any ``FILLED·asserted`` at column 0. Note
    prose is hard-wrapped, so a sentence can begin a line with the key and mean
    nothing by it -- ``case-04`` writes ``FILLED·asserted.`` at column 0 far above
    its tier block, and ``case-06`` writes
    ``FILLED·asserted item 11.`` below its own. On ``case-04`` the parser took the
    prose one, which is exactly the failure the module's own docstring says the
    column-0 rule prevents: **a whole note body read as declared content, with
    the real block never read at all.**

    A tier key *heads* a line -- end of line, or an aligned column of two or more
    spaces before its content. A sentence does neither.
    """

    def test_a_wrapped_prose_sentence_does_not_open_a_block(self):
        """``case-04``'s shape: the key at column 0 with a period after it."""
        text = (
            "and acetaminophen — both inferred and listed in\n"
            "FILLED·asserted. **Whether he takes an NSAID** is unconfirmed.\n"
        )
        self.assertEqual(fvc.filled_block(text), "")

    def test_a_prose_reference_with_one_space_does_not_open_a_block(self):
        """``case-06``'s shape: the key, one space, and a running sentence."""
        text = "FILLED·asserted item 11. Filled vitals are not results.\n"
        self.assertEqual(fvc.filled_block(text), "")

    def test_a_key_alone_on_its_line_opens_a_block(self):
        """``case-07`` and ``case-08`` write it this way -- a third live form."""
        text = "FILLED·asserted\n    BP 138/86 filled.\nFILLED·proposed\n    Ibuprofen.\n"
        block = fvc.filled_block(text)
        self.assertIn("BP 138/86 filled", block)
        self.assertNotIn("Ibuprofen", block)

    def test_case_04s_block_is_its_tier_block_and_not_its_body(self):
        """The committed instance, which is why this rule is not hypothetical."""
        block = fvc.filled_block(note("case-04.md"))
        self.assertIn("Home meds — omeprazole", block)
        self.assertNotIn("Whether he takes an NSAID", block)

    def test_the_committed_notes_still_read_exactly_one_key_each(self):
        for name in sorted(p.name for p in NOTES.glob("case-*.md")):
            with self.subTest(note=name):
                self.assertEqual(fvc.key_coverage(note(name)), (1, 1))


class TheRepeatedKeyFormIsOneBlock(unittest.TestCase):
    """Issue #204. Three block forms are live and all three are this skill's.

    The parser used to end a block at the next line starting ``FILLED``, which
    includes ``FILLED·asserted`` itself. On the aligned-continuation form that is
    right. On the **repeated-key** form -- one key per line, which is how
    ``skills/clinical-note/SKILL.md``'s own worked examples write a multi-item
    block -- the first declaration swallowed nothing and every one after it was
    read as a block that ended where it began, and nothing in the report or the
    exit status said so. **How many declarations one run lost is #204's to state
    and is deliberately not restated here**, on that module's own terms.
    """

    REPEATED = (
        "DERIVED           BMI 26.5 = 703 x 185 / 70^2.\n"
        "FILLED·asserted   HEIGHT 5'10\" (70 in) filled. Plausible for a 41-year-old man.\n"
        "FILLED·asserted   WEIGHT 185 lb filled. Reasoned from the same.\n"
        "FILLED·asserted   BP 142/88 filled. Reasoned from age 41.\n"
        "FILLED·asserted   HR 96 filled.\n"
        "FILLED·proposed   Recheck in 4 weeks.\n"
    )

    def test_every_declaration_in_a_repeated_key_block_reads(self):
        fill = fvc.read_fill(self.REPEATED)
        self.assertEqual(fill.height_in, 70)
        self.assertEqual(fill.weight_lb, 185)
        self.assertEqual(fill.pressure, (142, 88))
        self.assertIn("heart_rate", fill.counted)

    def test_the_block_still_ends_at_the_proposed_key(self):
        """Reading past it would put forward actions among declared values."""
        self.assertNotIn("Recheck", fvc.filled_block(self.REPEATED))
        self.assertNotIn("BMI 26.5", fvc.filled_block(self.REPEATED))

    def test_the_aligned_continuation_form_reads_the_same_values(self):
        aligned = (
            "FILLED·asserted   HEIGHT 5'10\" (70 in) filled. Plausible for a 41-year-old man.\n"
            "                  WEIGHT 185 lb filled. BP 142/88 filled. HR 96 filled.\n"
            "FILLED·proposed   Recheck in 4 weeks.\n"
        )
        self.assertEqual(fvc.read_fill(aligned), fvc.read_fill(self.REPEATED))

    def test_a_declaration_may_not_wrap_from_one_repeated_key_into_the_next(self):
        """Each key opens its own item, so the 80-character window stops there.

        Without a boundary the tail of one entry welds to the ``filled`` of the
        next, which would read a *given* value on one line as declared by the
        word on the line below it.
        """
        text = (
            "FILLED·asserted   BMI 25.7 rests on the charted Ht 6'2\"\n"
            "FILLED·asserted   WEIGHT 200 lb filled.\n"
            "FILLED·proposed   Recheck.\n"
        )
        # No ``given`` anywhere, so the height's only route to being read as
        # declared is the word on the line below it. That route is the one the
        # repeated key closes, and nothing else in this module would.
        self.assertIsNone(fvc.read_fill(text).height_in)
        self.assertEqual(fvc.read_fill(text).weight_lb, 200)


class TheTwoBoundariesAreLooseInOppositeDirections(unittest.TestCase):
    """The start is strict and the end is permissive, and that is not symmetry.

    The two fail opposite ways. A **start** that matches too readily opens a
    block on prose and reads a note body as declared content. An **end** that
    matches too *reluctantly* never closes the block and reads the tiers below
    it as declared content -- which is the same defect one boundary over.

    The first version of #204's fix applied the heads-a-line rule to both, and
    the case below is what that cost: a single-space ``FLAG`` stopped closing
    the block, so a **given** pressure the note had flagged, and a charted
    weight under ``GAPS``, both read as filled -- with the coverage row
    reporting a clean scan over them. Found by the spec axis of ``/code-review``
    and re-derived before it was believed.
    """

    FLAGGED = (
        "FILLED·asserted   HEIGHT 5'10\" (70 in) filled. Plausible for a 41-year-old man.\n"
        "FLAG BP 151/93 undiscussed\n"
        "GAPS x-ray ordered, WEIGHT 300 lb filled per chart\n"
    )

    def test_a_single_space_key_still_closes_the_block(self):
        fill = fvc.read_fill(self.FLAGGED)
        self.assertEqual(fill.height_in, 70)
        self.assertIsNone(fill.pressure)
        self.assertIsNone(fill.weight_lb)

    def test_a_prose_line_starting_filled_closes_rather_than_opens(self):
        """``case-06`` writes ``FILLED, not traced.`` below its own block.

        Closing early truncates, which is the safe direction; opening there
        would read everything after it as declared.
        """
        text = "FILLED·asserted   BP 120/70 filled.\nFILLED, not traced.\nWEIGHT 300 lb filled\n"
        self.assertIsNone(fvc.read_fill(text).weight_lb)
        self.assertEqual(fvc.read_fill(text).pressure, (120, 70))

    def test_a_repeated_asserted_key_is_still_not_an_end(self):
        """Both separators, so the end's lookahead tracks the start's class."""
        for key in ("FILLED·asserted", "FILLED.asserted", "FILLED asserted"):
            with self.subTest(key=key):
                text = f"{key}   BP 120/70 filled.\n{key}   WEIGHT 185 lb filled.\n"
                self.assertEqual(fvc.read_fill(text).weight_lb, 185)

    def test_the_proposed_key_is_still_an_end(self):
        text = "FILLED·asserted   BP 120/70 filled.\nFILLED·proposed   WEIGHT 185 lb filled.\n"
        self.assertIsNone(fvc.read_fill(text).weight_lb)


class CoverageIsCountedAndRefused(unittest.TestCase):
    """Issue #204's ruling, and #177's arrangement adopted whole.

    Reading both forms leaves the tool silently tolerant of a fourth nobody has
    written. So the signal is derived from the **member list** -- the
    ``FILLED·asserted`` keys the note carries -- rather than from whether a block
    was found at all, which is the arithmetic that let *one declaration of N* read
    like a complete scan. A key the read block does not contain is a member that was not
    read: the report says so on **every** run, and the exit status refuses.
    """

    INTERLEAVED = (
        "FILLED·asserted   HEIGHT 5'10\" (70 in) filled. Plausible for a 41-year-old man.\n"
        "DERIVED           BMI 26.5 = 703 x 185 / 70^2.\n"
        "FILLED·asserted   BP 142/88 filled.\n"
    )

    def test_a_key_outside_the_read_block_is_counted_unread(self):
        self.assertEqual(fvc.key_coverage(self.INTERLEAVED), (2, 1))

    def test_a_note_with_no_block_is_not_a_partial_scan(self):
        """Declaring nothing and being half-read are different states."""
        self.assertEqual(fvc.key_coverage("SUBJECTIVE\n\nOBJECTIVE\n"), (0, 0))

    def test_the_report_names_what_was_scanned_on_every_run(self):
        report = fvc.format_report(fvc.survey(all_notes()), source="notes")
        self.assertIn("scanned", report)
        self.assertIn("FILLED·asserted", report)

    def test_the_scanned_row_comes_before_the_counts(self):
        """A count printed ahead of the caveat is read as the verdict."""
        report = fvc.format_report(fvc.survey(all_notes()), source="notes")
        self.assertLess(report.index("scanned"), report.index("notes read"))

    def test_a_partly_read_note_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(fvc.main([str(written(Path(tmp), a=self.INTERLEAVED))]), 2)

    def test_the_same_note_read_whole_exits_zero(self):
        """So the two above is the unread key and not the temp directory."""
        whole = self.INTERLEAVED.replace(
            "DERIVED           BMI 26.5 = 703 x 185 / 70^2.\n", ""
        )
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(fvc.main([str(written(Path(tmp), a=whole))]), 0)

    def test_a_violation_outranks_a_partly_read_note(self):
        """1 wins, on ``differential_scan.py``'s ordering and for its reason."""
        bare = self.INTERLEAVED.replace(" Plausible for a 41-year-old man.", "")
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(fvc.main([str(written(Path(tmp), a=bare))]), 1)

    def test_the_floor_note_precedes_the_findings_it_qualifies(self):
        """#177's ordering: a count ahead of its caveat reads as the verdict.

        Every finding printed below is a count, and each is a floor where a key
        went unread -- so the caveat cannot be the last thing on the page.
        """
        bare = self.INTERLEAVED.replace(" Plausible for a 41-year-old man.", "")
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                self.assertEqual(fvc.main([str(written(Path(tmp), a=bare))]), 1)
        out = stderr.getvalue()
        self.assertIn("is a floor", out)
        self.assertLess(out.index("is a floor"), out.index("B18 fails"))

    def test_the_committed_set_reads_every_key_it_has(self):
        census = fvc.survey(all_notes())
        self.assertEqual(census.asserted_keys_unread, 0)
        self.assertEqual(census.asserted_keys, census.asserted_keys_read)


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
        read = run_grader.read_run_directory(NOTES)
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

    # Compliant under #97's height rule, so a non-zero below is the shared body
    # and never the age-and-sex line failing underneath it.
    BODY = (
        "FILLED·asserted   HEIGHT 5'10\" (70 in) filled. Plausible for a 36-year-old\n"
        "                  man; no habitus datum in the source. WEIGHT 190 lb filled.\n"
    )

    def test_a_repeated_body_exits_non_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = written(Path(tmp), a=self.BODY, b=self.BODY)
            self.assertEqual(fvc.survey(run_grader.read_run_directory(directory)).repeated_bodies, 1)
            self.assertEqual(fvc.main([str(directory)]), 1)

    def test_two_different_bodies_exit_zero(self):
        """So the non-zero above is the repeat and not the temp directory."""
        with tempfile.TemporaryDirectory() as tmp:
            other = self.BODY.replace("190 lb", "165 lb")
            self.assertEqual(fvc.main([str(written(Path(tmp), a=self.BODY, b=other))]), 0)


class TheTiltBarIsArithmeticRatherThanOpinion(unittest.TestCase):
    """Issue #97's ruling, and the reason it could be made at all.

    That ticket's own objection was that *a row saying no more than N needs an N
    that nothing grounds*. It is groundable: ``clinical-note`` measures 249
    transcribed pressures splitting about evenly at 130/80, so an honestly
    reasoned set of filled pressures should land like that many coin flips. The
    clinician then chose not a count but a **false-alarm rate** -- how often he
    would accept an honest run being failed for nothing -- and 2% put the bar at
    8 of 9. These tests pin the ruling at the shape it was made in.
    """

    def test_eight_of_nine_fails_and_seven_passes(self):
        """The clinician's ruling on 2026-08-17, in the numbers he was shown."""
        self.assertTrue(fvc.tilt_beyond_chance(8, 9))
        self.assertFalse(fvc.tilt_beyond_chance(7, 9))

    def test_the_run_that_filed_the_ticket_passes_and_that_is_deliberate(self):
        """Six of nine is a coin-flip outcome one time in four.

        ``fixtures/filled-anchor``'s six not-normal pressures are what #67 and #97
        were argued from, and the bar does **not** fail them. That was ruled
        knowingly: a bar at 6 wrongly fails an honest run 25% of the time, which
        is the rate at which a warning stops being read. The height half of that
        same run is where its defect is graded instead.
        """
        self.assertFalse(fvc.tilt_beyond_chance(6, 9))

    def test_a_set_too_small_to_grade_can_never_fail(self):
        """Five all-abnormal pressures are 1 in 32, which is not yet evidence.

        Stated as a test because the alternative reading -- that a five-note set
        passed the bar -- is exactly the silent-pass shape this repo refuses. Six
        is the smallest set that can fail it, and only by failing every one.
        """
        self.assertFalse(fvc.tilt_beyond_chance(5, 5))
        self.assertTrue(fvc.tilt_beyond_chance(6, 6))

    def test_no_pressures_at_all_is_not_a_pass(self):
        """Nothing to grade is reported by the exit status, not by this."""
        self.assertFalse(fvc.tilt_beyond_chance(0, 0))

    def test_the_bar_is_one_sided(self):
        """A set landing *below* the line is not what this measures.

        Filled pressures clustering normal is a different defect -- the bland
        normal -- and ``clinical-note`` guards it elsewhere. A two-sided test here
        would fail a run for the opposite of the behavior #97 is about.
        """
        self.assertFalse(fvc.tilt_beyond_chance(0, 9))
        self.assertFalse(fvc.tilt_beyond_chance(1, 9))


class AFilledHeightNamesTheAgeAndTheSex(unittest.TestCase):
    """The clinician's second ruling on 2026-08-17.

    Repetition across a set stays honest -- ``clinical-note`` says outright that
    *the repetition across a set is that honesty's consequence* -- so no bar
    counts repeated heights. What is graded is that the two anchors a height
    always has were read: age and sex are given on every patient in this corpus,
    so a height is never truly unanchored however little the encounter says about
    the body.

    **The form is already in the corpus, which is the strongest argument for the
    rule.** ``fixtures/filled-anchor`` case 6 writes *Approximately the 60th
    percentile for a 17-year-old male* and case 9 *plausible for a 44-year-old
    female*. Four of that set's nine heights are written that way and five name
    nothing at all, so this requires a form the skill has demonstrably produced
    rather than inventing a new burden.
    """

    def test_a_line_naming_both_passes(self):
        self.assertTrue(fvc.names_person("Plausible for a 36-year-old man; no habitus datum."))

    def test_a_sex_without_an_age_fails(self):
        """``Plausible adult male height`` names a sex and no age at all.

        **Not the 17-year-old's line**, which names both -- that claim was made
        during the grilling for this ticket from two notes rather than nine, and
        this scanner is what disproved it. Kept as a predicate test because the
        shape is the one five of that set's nine heights come closest to.
        """
        self.assertFalse(fvc.names_person("Plausible adult male height; nothing to move it."))

    def test_an_age_without_a_sex_fails(self):
        self.assertFalse(fvc.names_person("Mid-range for a 17-year-old; no habitus datum."))

    def test_a_bare_F_is_not_a_sex(self):
        """``T 98.4 F`` is a temperature unit, and it sits in these blocks.

        Accepting a bare ``M`` or ``F`` would pass a height whose only claim to
        naming a sex is the Fahrenheit mark on a neighboring temperature.
        """
        self.assertFalse(fvc.names_person("HEIGHT 5'10\" filled. T 98.4 F filled. 36 yo."))

    def test_the_pediatric_age_forms_read(self):
        for age in ("a 17-year-old boy", "17 yo male", "age 17, male", "a 9-month-old girl"):
            with self.subTest(age=age):
                self.assertTrue(fvc.names_person(f"Reasoned from {age}."))

    def test_the_scope_is_the_height_declaration_and_not_the_whole_block(self):
        """The canonical block names the age on the *pressure* line.

        A block-wide check would pass that height on an age read for a different
        value, which is the 17-year-old defect surviving its own fix.
        """
        block = (
            "FILLED·asserted   BP 146/84 filled. Reasoned from age 68 with type 2\n"
            "                  diabetes, at rest and in no distress.\n"
            "                  Ht 5'10\" (70 in) filled. Plausible adult male height.\n"
        )
        self.assertFalse(fvc.read_fill(block).height_names_person)

    def test_a_height_whose_own_clause_names_both_reads_true(self):
        block = (
            "FILLED·asserted   BP 146/84 filled. Reasoned from the given pulse of 112.\n"
            "                  Ht 5'10\" (70 in) filled. Mid-range for a 68-year-old man;\n"
            "                  no habitus or percentile datum in the source to move it.\n"
        )
        self.assertTrue(fvc.read_fill(block).height_names_person)

    def test_a_note_declaring_no_filled_height_is_not_graded(self):
        """``None`` rather than ``False`` -- a control has nothing to fail."""
        self.assertIsNone(fvc.read_fill("FILLED·asserted   BP 138/86 filled.\n").height_names_person)


class TheCensusSeesTheOtherVitalClasses(unittest.TestCase):
    """Issue #69's finding, answered by counting rather than by grading.

    That ruling turned entirely on a filled temperature and two filled
    saturations, and this tool could not see any of them. **All five of the
    classes that comment names are counted now**, and the fifth was nearly left
    out: the first pass added four and wrote prose enumerating them as though the
    gap were closed, which review caught. The pain score is the one with no label
    of its own -- it is written ``7/10 itching filled`` -- and the only one
    already carrying a clinician's ruling, #59's carve-out on a filled ``0/10``.

    They are counted and **not graded**: the corpus supplies no comparable even
    split for a temperature or a saturation, so no cutoff here could be grounded
    the way the pressure one is.
    """

    def setUp(self):
        self.census = fvc.survey(all_notes())

    def test_every_class_69_named_is_counted(self):
        """The enumeration is read off the module, not retyped here.

        A sixth class added to ``COUNTED_CLASSES`` and forgotten in the report is
        the failure this replaces, and it is the failure the four-field version
        actually committed.
        """
        self.assertEqual(
            [key for _, key, _ in fvc.COUNTED_CLASSES],
            ["temperature", "heart_rate", "resp_rate", "saturation", "pain_score"],
        )

    def test_the_four_vital_classes_are_nine_each(self):
        """**Every one of the nine filled cases declares all four.**

        The first count taken during #97's grilling read 7 temperatures, from a
        hand-rolled regex that missed the two written ``98.2 °F`` with a degree
        sign. Pinned here at the figure this module actually produces, which is
        the point of counting with the instrument rather than beside it.
        """
        for key in ("temperature", "heart_rate", "resp_rate", "saturation"):
            with self.subTest(key=key):
                self.assertEqual(self.census.count_of(key), 9)

    def test_the_set_declares_more_than_the_census_used_to_reach(self):
        """27 graded against 36 counted, and the 36 is pinned rather than derived.

        That figure is published in three prose files, which is #180's shape --
        so it is asserted as a literal here and the pain-score zero is asserted
        beside it. A sixth class, or a run declaring a severity, moves the total
        and fails this test rather than leaving three files quietly wrong.
        """
        graded = self.census.heights + self.census.weights + self.census.pressures
        self.assertEqual(graded, 27)
        self.assertEqual(self.census.counted_total, 36)
        self.assertEqual(self.census.count_of("pain_score"), 0)

    def test_a_given_vital_is_still_not_counted(self):
        fill = fvc.read_fill(
            "FILLED·asserted   BMI from the given T 101.2 F and HR 118 filled.\n"
        )
        self.assertNotIn("temperature", fill.counted)

    def test_a_filled_severity_is_counted(self):
        """#69's fifth class, and the one with no label of its own."""
        fill = fvc.read_fill("FILLED·asserted   7/10 itching filled.\n")
        self.assertIn("pain_score", fill.counted)

    def test_counting_a_severity_is_not_59s_rule(self):
        """A filled ``0/10`` is counted here and graded nowhere in this module.

        #59's carve-out is about what the disclosure line must say, which is a
        reader's question. Counting it must not read as having checked it.
        """
        fill = fvc.read_fill("FILLED·asserted   0/10 filled.\n")
        self.assertIn("pain_score", fill.counted)

    def test_none_of_them_reaches_the_exit_status(self):
        """Counted, not graded — so a set declaring only these exits 2."""
        with tempfile.TemporaryDirectory() as tmp:
            block = (
                "FILLED·asserted   T 101.2 F filled. HR 118 filled. SpO2 91% filled.\n"
                "                  9/10 filled.\n"
            )
            self.assertEqual(fvc.main([str(written(Path(tmp), a=block, b=block))]), 2)


class ExitStatusSeparatesNotScannedFromNothingFound(unittest.TestCase):
    """``differential_scan.py``'s arrangement, adopted for its reason.

    A run whose notes declare no filled height and no filled pressure has nothing
    for either graded rule to read, and reporting that as 0 would file the
    strongest thing known about the run -- that it was never graded -- under the
    heading that means it passed. ``scratch/day-a-run-2`` is the real instance:
    eleven notes, nothing filled at all. **Where a violation and an ungraded set
    both hold, 1 wins**, which is that tool's ordering too.
    """

    BODY = "FILLED·asserted   HEIGHT 5'10\" (70 in) filled. Plausible for a 36-year-old man.\n"

    def test_a_clean_set_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            other = self.BODY.replace("5'10\" (70 in)", "5'8\" (68 in)")
            self.assertEqual(fvc.main([str(written(Path(tmp), a=self.BODY, b=other))]), 0)

    def test_a_set_declaring_nothing_gradeable_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            block = "FILLED·asserted   None. Every vital in this encounter was given.\n"
            self.assertEqual(fvc.main([str(written(Path(tmp), a=block, b=block))]), 2)

    def test_a_directory_with_no_notes_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(fvc.main([str(Path(tmp))]), 2)

    def test_a_directory_that_is_not_there_exits_two(self):
        self.assertEqual(fvc.main([str(REPO_ROOT / "no-such-directory")]), 2)

    def test_a_height_with_no_person_named_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            bare = "FILLED·asserted   HEIGHT 5'10\" (70 in) filled.\n"
            self.assertEqual(fvc.main([str(written(Path(tmp), a=bare))]), 1)

    def test_the_tilt_bar_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            notes = {
                f"case{n}": f"FILLED·asserted   BP 1{40 + n}/9{n % 10} filled.\n" for n in range(6)
            }
            self.assertEqual(fvc.main([str(written(Path(tmp), **notes))]), 1)

    def test_a_violation_outranks_an_ungraded_set(self):
        """Both hold at once, and the exit reports the violation.

        Returning 2 here would say *nothing was graded* about a set in which
        something was graded and failed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            bare = "FILLED·asserted   HEIGHT 5'10\" (70 in) filled.\n"
            silent = "SUBJECTIVE  no block here at all\n"
            self.assertEqual(fvc.main([str(written(Path(tmp), a=bare, b=silent))]), 1)


class TheCommittedRunSplitsOnTheHeightRule(unittest.TestCase):
    """It exits 1, and reading that as breakage is the mistake to avoid.

    ``fixtures/filled-anchor/notes`` is day-b **run 1** byte for byte apart from
    two redacted site names, written before drift row 19 existed. The obvious
    prediction from that is that it fails the age-and-sex rule everywhere,
    **and it does not** -- four of the
    nine heights already name both, two of them with a percentile. So the set is
    not uniformly pre-row-19 and it is not uniform at all, which is
    [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s
    subject arriving on this file: the prediction was made from two notes during
    #97's grilling and corrected by running the scanner over all twelve.

    The counts over it are untouched and stay the evidence for #67.
    """

    def test_the_set_exits_one(self):
        self.assertEqual(fvc.main([str(NOTES)]), 1)

    def test_five_of_the_nine_heights_name_no_age_and_sex(self):
        self.assertEqual(fvc.survey(all_notes()).heights_missing_person, 5)

    def test_the_other_four_already_write_the_compliant_form(self):
        """Which is why the rule asks for nothing new of the skill."""
        census = fvc.survey(all_notes())
        self.assertEqual(census.heights - census.heights_missing_person, 4)

    def test_its_pressures_clear_the_tilt_bar(self):
        """So the exit status above is the heights and nothing else."""
        census = fvc.survey(all_notes())
        self.assertFalse(fvc.tilt_beyond_chance(census.abnormal_pressures, census.pressures))


if __name__ == "__main__":
    unittest.main()
