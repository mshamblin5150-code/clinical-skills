"""Cover ``name_index``'s window parser, its merge and its coverage arithmetic.

Every day file here is written in this file and a temp directory, on
``test_differential_scan``'s arrangement and for its reason: **the real corpus is
gitignored PHI and there will never be a fixture of it.** Nothing here reads
``scratch/``, and no count taken against the real corpus is asserted anywhere --
those live in the module's own docstring, beside the command that reprints them.

phi-scan: synthetic

The names below are invented. They are shaped like the corpus's -- two words,
letters only -- because the shape is what the parser reads.

**One class reads a committed file** -- ``skills/batch-shift/SKILL.md`` -- on
``test_spelling_scan``'s reasoning: `batch-shift` step 3 is this parser's written
spec, and a spec that has drifted from the tool is worse than none, because it
reads as agreement.

**And one class pins the direction of the merge.** The index's ``name`` field is
hand-curated and is not derivable from the corpus, so a rebuild is a destroying
operation and a merge is not. ``TheMergeOnlyAdds`` is that property; if it ever
fails, the fix is the merge and never the assertion.
"""

from __future__ import annotations

import ast
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import corpus_census as cc
import name_index as ni
import phi_scan as ps

REPO_ROOT = Path(__file__).resolve().parent.parent
BATCH_SHIFT = REPO_ROOT / "skills" / "batch-shift" / "SKILL.md"
MODULE = Path(ni.__file__)

# A string that appears in no legitimate counts-only report, driven through the
# corpus's aperture onto the output. ``test_tracker_bodies``'s marker, for its
# reason -- and shaped like a name, so the parser really does pick it up.
MARKER = "Zzmarker Qqmarker"


def day_file(*encounters: str) -> str:
    """A day file: a header belonging to no encounter, then the encounters."""
    return "day header, not an encounter\n\n" + "\n\n".join(encounters) + "\n"


def encounter(number: int, *lines: str, label: str = "Note") -> str:
    return f"{label} {number}\n" + "\n".join(lines)


def entry(stem: str, note: int, name, *window: str) -> dict:
    return {
        "file": f"{stem}.txt",
        "note": note,
        "raw": window[0] if window else "",
        "win": list(window),
        "name": name,
    }


class Tree:
    """A throwaway corpus directory and index file, on ``test_skills_mirror``'s
    arrangement -- built here, never read from or repaired against the real one."""

    def __init__(self, case: unittest.TestCase):
        holder = tempfile.TemporaryDirectory()
        case.addCleanup(holder.cleanup)
        self.root = Path(holder.name)
        self.corpus = self.root / "day-file-text"
        self.corpus.mkdir()
        self.index = self.root / "name-index.json"

    def write(self, stem: str, text: str) -> Path:
        path = self.corpus / f"{stem}.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def put_index(self, entries) -> None:
        self.index.write_text(json.dumps(entries), encoding="utf-8")

    def entries(self) -> list:
        return json.loads(self.index.read_text(encoding="utf-8"))

    def run(self, *args: str) -> tuple:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = ni.main([str(self.corpus), "--index", str(self.index), *args])
        return code, out.getvalue(), err.getvalue()


class TheDelimiterIsTheDeclaredNumber(unittest.TestCase):
    """``Note N`` opens an encounter, and ``N`` is what the file says it is.

    `batch-shift` step 3: the numbering skips and repeats in this catalog, and
    the instruction is to report that rather than renumber it tidy. Keying an
    entry on its position instead would silently re-file every encounter after a
    skip, and the index's own note numbers are not contiguous in nine files.
    """

    def setUp(self):
        self.tree = Tree(self)

    def test_case_insensitive(self):
        self.tree.write("d", day_file(
            encounter(1, "Alice Trent", "40 yo F"),
            encounter(2, "Bela Cortez", "8 yo M", label="NOte"),
        ))
        self.assertEqual([e.note for e in ni.encounters(self.tree.corpus)], [1, 2])

    def test_a_skipped_number_is_kept_as_written(self):
        self.tree.write("d", day_file(
            encounter(8, "Alice Trent", "40 yo F"),
            encounter(10, "Bela Cortez", "8 yo M"),
        ))
        self.assertEqual([e.note for e in ni.encounters(self.tree.corpus)], [8, 10])

    def test_a_repeated_number_is_two_encounters(self):
        self.tree.write("d", day_file(
            encounter(2, "Alice Trent", "40 yo F"),
            encounter(2, "Bela Cortez", "8 yo M"),
        ))
        found = ni.encounters(self.tree.corpus)
        self.assertEqual(len(found), 2)
        self.assertEqual({e.note for e in found}, {2})

    def test_the_day_header_is_not_an_encounter(self):
        self.tree.write("d", day_file(encounter(1, "Alice Trent", "40 yo F")))
        self.assertEqual(len(ni.encounters(self.tree.corpus)), 1)


class TheWindowIsWhatFindsTheName(unittest.TestCase):
    """The shapes that defeated the index, from #141's own reading.

    Each of the three unindexed encounters put something other than the name on
    the line after ``Note N`` -- one a stray punctuation character and a blank
    line, two a parenthetical annotation. `batch-shift` step 3 names the remedy:
    read a window and take the first line shaped like a name.
    """

    def setUp(self):
        self.tree = Tree(self)

    def name_of(self, *lines: str):
        self.tree.write("d", day_file(encounter(1, *lines)))
        return ni.encounters(self.tree.corpus)[0].name

    def test_a_stray_punctuation_line_and_a_blank_are_skipped(self):
        self.assertEqual(self.name_of("*", "", "Alice Trent", "40 yo F"), "Alice Trent")

    def test_a_parenthetical_annotation_is_skipped(self):
        self.assertEqual(
            self.name_of("(saw this patient last week)", "Bela Cortez", "8 yo M"),
            "Bela Cortez",
        )

    def test_a_vitals_line_is_skipped(self):
        self.assertEqual(
            self.name_of("124/65 HR 115 SpO2 99% T 99.6", "Cleo Marsden", "8 yo F"),
            "Cleo Marsden",
        )

    def test_the_window_is_anchored_at_the_name(self):
        """``raw == win[0]`` holds for every entry the index already carries."""
        self.tree.write("d", day_file(
            encounter(1, "*", "", "Alice Trent", "40 yo F", "cc: cough", "hx: none"),
        ))
        found = ni.encounters(self.tree.corpus)[0]
        self.assertEqual(found.window[0], "Alice Trent")
        self.assertEqual(found.window[0], found.raw)

    def test_the_window_stops_at_the_next_encounter(self):
        self.tree.write("d", day_file(
            encounter(1, "Alice Trent"),
            encounter(2, "Bela Cortez", "8 yo M"),
        ))
        self.assertNotIn("Bela Cortez", ni.encounters(self.tree.corpus)[0].window)

    def test_a_name_below_the_lookahead_is_not_found(self):
        """The bound is stated rather than unlimited, and this is where it bites.

        A wider search is not free: two words of clinical vocabulary have a
        name's exact shape, so every extra line searched is another chance to
        file ``sore throat`` as a patient. The residue is reported for a human.
        """
        buried = [f"filler line {n} here" for n in range(ni.LOOKAHEAD + 1)]
        self.assertIsNone(self.name_of(*buried, "Alice Trent"))

    def test_an_encounter_with_no_name_still_becomes_an_entry(self):
        """Coverage and naming are two claims, and only the first is mechanical."""
        self.tree.write("d", day_file(encounter(1, "40 yo F", "cc: cough")))
        found = ni.encounters(self.tree.corpus)[0]
        self.assertIsNone(found.name)
        self.assertEqual(found.window[0], "40 yo F")


class TheNameShapeIsTheHarvestsOwn(unittest.TestCase):
    """One predicate, imported rather than restated.

    A generator holding its own answer could write a ``name`` the harvest will
    not scan for, or pass over a line the harvest would have taken -- which is
    ``reference_scan``'s reason for importing ``REFERENCE_HEADING`` from the
    renderer instead of keeping a copy of it.
    """

    def test_phi_scan_uses_this_object(self):
        self.assertIs(ps._looks_like_a_name, ni.looks_like_a_name)


class ByteIdenticalDayFilesAreOneShift(unittest.TestCase):
    """The catalog holds one day file twice, byte for byte, under two names.

    ``corpus_census.read_corpus`` drops the copy, so the denominator counts that
    shift once. An entry filed under the dropped twin's name still covers the
    kept file -- without the alias the whole shift reads as unindexed, which is
    eight encounters of false shortfall against the real corpus.
    """

    def setUp(self):
        self.tree = Tree(self)
        text = day_file(encounter(1, "Alice Trent", "40 yo F"))
        self.tree.write("a-copy", text)
        self.tree.write("b-original", text)

    def test_the_copy_is_not_counted_twice(self):
        self.assertEqual(len(ni.encounters(self.tree.corpus)), 1)

    def test_an_entry_under_either_name_covers_the_shift(self):
        for stem in ("a-copy", "b-original"):
            with self.subTest(stem=stem):
                self.tree.put_index([entry(stem, 1, "Alice Trent", "Alice Trent")])
                found = ni.coverage(self.tree.entries(), self.tree.corpus)
                self.assertEqual(found.uncovered, 0)


class TheMergeOnlyAdds(unittest.TestCase):
    """Every existing entry survives a merge unchanged, in order, as a prefix.

    **This is the property the whole design rests on.** Most of the index's
    ``name`` fields match the line they were harvested from and a minority do
    not, so the field carries a human's correction that nothing here can
    re-derive. A rebuild would overwrite it; a merge cannot. The proportions are
    in the module docstring, where the command that reprints them is.
    """

    def setUp(self):
        self.tree = Tree(self)
        self.tree.write("d", day_file(
            encounter(1, "Alice Trent", "40 yo F"),
            encounter(2, "*", "", "Bela Cortez", "8 yo M"),
        ))
        # A curated entry: the `name` differs from the line it was harvested
        # from, which is the shape a rebuild would destroy.
        self.original = [entry("d", 1, "Alice Trent", "alice trent", "40 yo F")]
        self.tree.put_index(self.original)

    def merged(self):
        return ni.merge(self.original, ni.encounters(self.tree.corpus))

    def test_the_original_entries_are_a_prefix_of_the_merge(self):
        self.assertEqual(self.merged()[:len(self.original)], self.original)

    def test_the_curated_name_is_not_overwritten(self):
        self.assertEqual(self.merged()[0]["name"], "Alice Trent")

    def test_only_the_uncovered_encounter_is_added(self):
        merged = self.merged()
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[1]["note"], 2)

    def test_no_harvested_name_is_lost(self):
        """The firewall's own reading of the merge, which is the one that counts."""
        merged = self.merged()
        before = ps.kept_names(ps.harvested_names(self.original))
        after = ps.kept_names(ps.harvested_names(merged))
        self.assertEqual(before - after, set())
        self.assertTrue(after - before)

    def test_a_second_merge_adds_nothing(self):
        once = self.merged()
        self.assertEqual(ni.merge(once, ni.encounters(self.tree.corpus)), once)


class CoverageIsAgainstTheCensusDenominator(unittest.TestCase):
    def setUp(self):
        self.tree = Tree(self)
        self.tree.write("d", day_file(
            encounter(1, "Alice Trent", "40 yo F"),
            encounter(2, "Bela Cortez", "8 yo M"),
            encounter(3, "Cleo Marsden", "31 yo F"),
        ))

    def test_a_complete_index_is_zero_uncovered(self):
        self.tree.put_index([
            entry("d", n, name, name)
            for n, name in ((1, "Alice Trent"), (2, "Bela Cortez"), (3, "Cleo Marsden"))
        ])
        found = ni.coverage(self.tree.entries(), self.tree.corpus)
        self.assertEqual((found.encounters, found.covered, found.uncovered), (3, 3, 0))

    def test_a_short_index_names_the_shortfall(self):
        self.tree.put_index([entry("d", 1, "Alice Trent", "Alice Trent")])
        found = ni.coverage(self.tree.entries(), self.tree.corpus)
        self.assertEqual((found.encounters, found.covered, found.uncovered), (3, 1, 2))

    def test_an_absent_index_is_wholly_uncovered(self):
        found = ni.coverage([], self.tree.corpus)
        self.assertEqual(found.uncovered, 3)

    def test_an_entry_for_an_encounter_that_is_gone_is_counted_and_never_dropped(self):
        """An orphan entry is a claim about a shift the corpus no longer holds.

        Counted rather than deleted: a name harvested from one is still a
        patient's, and the corpus layer is right to keep scanning for it.
        """
        self.tree.put_index([entry("gone", 4, "Dara Vance", "Dara Vance")])
        found = ni.coverage(self.tree.entries(), self.tree.corpus)
        self.assertEqual(found.orphans, 1)
        self.assertEqual(found.uncovered, 3)


class TheExitStatusSaysWhichKindOfNothing(unittest.TestCase):
    """0 covered, 1 short, 2 every way of not having scanned.

    ``guidelines_search``'s convention, already in five siblings here. The limb
    that matters is 2: a run pointed at a directory holding no ``Note N`` line
    at all would otherwise report zero uncovered encounters and read as a clean
    index.
    """

    def setUp(self):
        self.tree = Tree(self)

    def test_covered_is_zero(self):
        self.tree.write("d", day_file(encounter(1, "Alice Trent", "40 yo F")))
        self.tree.put_index([entry("d", 1, "Alice Trent", "Alice Trent")])
        self.assertEqual(self.tree.run()[0], 0)

    def test_short_is_one(self):
        self.tree.write("d", day_file(encounter(1, "Alice Trent", "40 yo F")))
        self.tree.put_index([])
        self.assertEqual(self.tree.run()[0], 1)

    def test_no_corpus_directory_is_two(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = ni.main([str(self.tree.root / "nope"), "--index", str(self.tree.index)])
        self.assertEqual(code, ni.NOT_SCANNED)

    def test_no_encounter_in_any_file_is_two(self):
        self.tree.write("d", "a header, and nothing that opens an encounter\n")
        self.tree.put_index([])
        self.assertEqual(self.tree.run()[0], ni.NOT_SCANNED)

    def test_an_absent_index_is_a_cold_start_and_not_two(self):
        """Nothing on disk is a legitimate first run; a broken file is not."""
        self.tree.write("d", day_file(encounter(1, "Alice Trent", "40 yo F")))
        self.assertEqual(self.tree.run()[0], 1)

    def test_a_malformed_index_is_two_and_never_an_empty_one(self):
        """The limb that protects the curation.

        ``phi_scan.harvest_entries`` falls back to ``[]`` for a file that is
        absent *and* for one that will not parse -- correct there, because a
        scanner with no names is a scanner that finds none. Here the same
        fallback would read a damaged index as a cold start and write a
        from-scratch one over it, destroying every hand-corrected name in it.
        """
        self.tree.write("d", day_file(encounter(1, "Alice Trent", "40 yo F")))
        self.tree.index.write_text("{ this is not json", encoding="utf-8")
        self.assertEqual(self.tree.run("--write")[0], ni.NOT_SCANNED)
        self.assertEqual(self.tree.index.read_text(encoding="utf-8"), "{ this is not json")

    def test_an_index_that_is_not_a_list_is_two(self):
        self.tree.write("d", day_file(encounter(1, "Alice Trent", "40 yo F")))
        self.tree.put_index({"entries": []})
        self.assertEqual(self.tree.run("--write")[0], ni.NOT_SCANNED)


class WritingIsAskedForAndReported(unittest.TestCase):
    def setUp(self):
        self.tree = Tree(self)
        self.tree.write("d", day_file(
            encounter(1, "Alice Trent", "40 yo F"),
            encounter(2, "Bela Cortez", "8 yo M"),
        ))
        self.tree.put_index([entry("d", 1, "Alice Trent", "Alice Trent")])

    def test_the_default_writes_nothing(self):
        before = self.tree.index.read_text(encoding="utf-8")
        self.assertEqual(self.tree.run()[0], 1)
        self.assertEqual(self.tree.index.read_text(encoding="utf-8"), before)

    def test_write_closes_the_gap_and_goes_green(self):
        self.assertEqual(self.tree.run("--write")[0], 0)
        self.assertEqual(len(self.tree.entries()), 2)
        self.assertEqual(self.tree.run()[0], 0)


class TheDenominatorIsTheCensusDenominator(unittest.TestCase):
    """This module and ``corpus_census`` must count the same encounters.

    **The coverage figure is a fraction whose halves come from two modules**, and
    the whole claim is worthless if they disagree about what an encounter is.
    They have separate delimiters -- the census reads a whole day file with a
    multiline pattern, this matches line by line -- so agreement is a property to
    assert rather than one to assume. Against the real corpus on 2026-08-19 they
    agree exactly; here they are driven over the shapes that could part them.
    """

    def setUp(self):
        self.tree = Tree(self)

    def assert_agree(self, *files: str):
        for n, text in enumerate(files):
            self.tree.write(f"d{n}", text)
        census = cc.read_corpus(self.tree.corpus)
        self.assertEqual(len(ni.encounters(self.tree.corpus)), len(census.notes))

    def test_the_ordinary_shape(self):
        self.assert_agree(day_file(
            encounter(1, "Alice Trent", "40 yo F"),
            encounter(2, "Bela Cortez", "8 yo M"),
        ))

    def test_a_mixed_case_delimiter(self):
        self.assert_agree(day_file(
            encounter(1, "Alice Trent"), encounter(2, "Bela Cortez", label="NOte"),
        ))

    def test_a_hash_before_the_number(self):
        self.assert_agree(day_file(
            encounter(1, "Alice Trent", label="Note #"),
            encounter(2, "Bela Cortez", label="note#"),
        ))

    def test_an_indented_delimiter(self):
        self.assert_agree("day header\n\n  Note 1\nAlice Trent\n\n\tNote 2\nBela Cortez\n")

    def test_the_byte_identical_copy_is_dropped_by_both(self):
        text = day_file(encounter(1, "Alice Trent"), encounter(2, "Bela Cortez"))
        self.assert_agree(text, text)

    def test_a_file_holding_no_encounter_adds_none_to_either(self):
        self.assert_agree("a header and nothing else\n")


class TheTargetIsUnderScratchOrOutsideEveryCheckout(unittest.TestCase):
    """The one thing here that can stop a write.

    The index is a list of patient names. Under ``scratch/`` it is gitignored and
    ``phi_scan``'s path layer refuses a commit from it even under ``git add -f``;
    anywhere else inside a checkout it is one ``git add -A`` from being tracked
    with nothing under it.
    """

    def setUp(self):
        self.tree = Tree(self)
        self.tree.write("d", day_file(encounter(1, "Alice Trent", "40 yo F")))

    def test_outside_every_checkout_is_allowed(self):
        self.assertIsNone(ni.refuse_target(self.tree.root / "name-index.json"))

    def test_inside_a_checkout_is_refused(self):
        (self.tree.root / ".git").mkdir()
        self.assertIsNotNone(ni.refuse_target(self.tree.root / "sub" / "name-index.json"))

    def test_under_scratch_inside_a_checkout_is_allowed(self):
        (self.tree.root / ".git").mkdir()
        self.assertIsNone(ni.refuse_target(self.tree.root / "scratch" / "name-index.json"))

    def test_a_refused_target_is_two_and_writes_nothing(self):
        (self.tree.root / ".git").mkdir()
        target = self.tree.root / "name-index.json"
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = ni.main([str(self.tree.corpus), "--index", str(target), "--write"])
        self.assertEqual(code, ni.NOT_SCANNED)
        self.assertFalse(target.exists())


class TheReportIsCountsOnly(unittest.TestCase):
    """The corpus is the patient record itself, so nothing it holds may reach a
    report a reader pastes. ``--show`` output is PHI: read it, do not paste it."""

    def setUp(self):
        self.tree = Tree(self)
        self.tree.write("d", day_file(
            encounter(1, MARKER, "40 yo F", "cc: " + MARKER),
            encounter(2, "40 yo M", "cc: cough"),
        ))
        self.tree.put_index([])

    def test_nothing_from_the_corpus_reaches_the_default_report(self):
        code, out, err = self.tree.run()
        self.assertEqual(code, 1)
        self.assertNotIn("Zzmarker", out + err)
        self.assertNotIn("Qqmarker", out + err)

    def test_show_reveals_it(self):
        self.assertIn(MARKER, self.tree.run("--show")[1])

    def test_the_corpus_directory_name_is_the_only_path_printed(self):
        self.assertIn(self.tree.corpus.name, self.tree.run()[1])


class TheParserAgreesWithItsWrittenSpec(unittest.TestCase):
    """`batch-shift` step 3 is this parser's spec and names it, both directions."""

    def setUp(self):
        self.text = BATCH_SHIFT.read_text(encoding="utf-8")

    def test_the_step_names_the_generator(self):
        self.assertIn("tools/name_index.py", self.text)

    def test_the_step_no_longer_says_no_generator_is_committed(self):
        self.assertNotIn("no generator for the index is committed", self.text)

    def test_the_window_rule_is_still_written_there(self):
        self.assertIn("The name is not reliably the line after `Note N`", self.text)


class TheCommandLineTakesTheConsoleCodec(unittest.TestCase):
    """``test_console_codec`` asserts a floor over the directory; this asserts it
    of this module by name, so a rename cannot leave the floor satisfied by a
    sibling."""

    def test_use_utf8_is_called_from_main(self):
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        called = {
            node.func.id
            for guard in tree.body if isinstance(guard, ast.If)
            for node in ast.walk(guard)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertIn("use_utf8", called)


if __name__ == "__main__":
    unittest.main()
