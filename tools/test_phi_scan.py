"""Tests for the PHI pre-commit scanner.

phi-scan: synthetic

Every name and date below is invented. Testing a PHI scanner requires PHI-shaped
input, so this file declares itself synthetic -- and, like every file, remains
subject to the corpus layer regardless.
"""

import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date as CalendarDate, timedelta
from pathlib import Path
from random import Random

import name_index as ni
import phi_scan as ps
from repo_root import output_root, scratch_root

NAMES = {"Jordan Vance", "Priya Raman"}
DATES = {"4-17-88", "11/02/2011"}


def scan(text, path="some/file.md", names=None, dates=None):
    index = ps.build_index(NAMES if names is None else names,
                           DATES if dates is None else dates)
    return ps.scan_text(text, path, index)


class CorpusLayer(unittest.TestCase):
    def test_catches_a_corpus_name(self):
        found = scan("seen by Jordan Vance today")
        self.assertEqual([f.rule for f in found], ["corpus-name"])

    def test_is_case_insensitive(self):
        self.assertTrue(scan("jordan vance"))

    def test_matches_on_a_word_boundary_only(self):
        self.assertFalse(scan("Priya Ramanujan was a mathematician"))

    def test_catches_a_corpus_date(self):
        # Both layers fire here, and that is correct: the value is a real corpus
        # date and it is also date-shaped.
        self.assertIn("corpus-date", [f.rule for f in scan("dos 4-17-88")])

    def test_catches_an_alternate_numeric_rendering_of_a_corpus_date(self):
        found = scan("dos 04/17/1988", dates={"4-17-88"})
        self.assertIn("corpus-date", [f.rule for f in found])

    def test_a_two_digit_year_matches_either_plausible_century(self):
        pairs = (
            ({"4-17-68"}, "April 17, 1968"),
            ({"4-17-1968"}, "04/17/68"),
        )
        for dates, rendered in pairs:
            with self.subTest(dates=dates, rendered=rendered):
                found = scan(f"dos {rendered}", dates=dates)
                self.assertIn("corpus-date", [f.rule for f in found])

    def test_catches_a_written_rendering_of_a_corpus_date(self):
        found = scan("seen April 17, 1988", dates={"4-17-88"})
        self.assertIn("corpus-date", [f.rule for f in found])

    def test_catches_standard_English_written_date_variants(self):
        for rendered in ("Apr 17, 1988", "Apr. 17, 1988", "17 April 1988", "17 Apr 88"):
            with self.subTest(rendered=rendered):
                found = scan(f"seen {rendered}", dates={"4-17-88"})
                self.assertIn("corpus-date", [f.rule for f in found])

    def test_catches_an_iso_rendering_of_a_corpus_date(self):
        found = scan("seen 1988-04-17", dates={"4-17-88"})
        self.assertIn("corpus-date", [f.rule for f in found])

    def test_reports_the_rendering_that_appeared_in_the_scanned_text(self):
        found = scan("seen April 17, 1988", dates={"4-17-88"})
        corpus_findings = [f for f in found if f.rule == "corpus-date"]
        self.assertEqual([f.match for f in corpus_findings], ["April 17, 1988"])

    def test_does_not_normalize_an_unrelated_date_into_a_corpus_finding(self):
        for rendered in ("04/18/1988", "April 18, 1988", "1988-04-18"):
            with self.subTest(rendered=rendered):
                rules = [f.rule for f in scan(f"seen {rendered}", dates={"4-17-88"})]
                self.assertNotIn("corpus-date", rules)

    def test_an_invalid_date_shaped_corpus_literal_keeps_exact_protection(self):
        rules = [f.rule for f in scan("seen 2-30-99", dates={"2-30-99"})]
        self.assertIn("corpus-date", rules)

    def test_reports_the_line_number(self):
        found = scan("clean\nclean\nJordan Vance\n")
        self.assertEqual(found[0].line, 3)

    def test_clean_text_passes(self):
        self.assertEqual(scan("bp 134/77 hr 79, no identifiers here"), [])


class CorpusIndexing(unittest.TestCase):
    """The prefilter that makes the corpus layer affordable (#18).

    `build_index` buckets each name under a word it requires, and a line is only
    tested against the buckets its own tokens land in. That is a **filter, not a
    matcher**: every candidate it lets through is still tested with the same
    ``\\bname\\b`` pattern, so the only way it can be wrong is by skipping a pair
    that would have matched. These tests are all aimed at that one failure.
    """

    HOSTILE = {
        "Jordan Vance",         # plain two-part name
        "Doctor Jordan Vance",  # contains another name outright
        "Ellery Fane",          # shares its bucket word with the next one
        "Ellery Voss",
        "Mary-Ann O'Dell",      # punctuation inside the name
        "Patient Zervas",       # bucket word is common English
        "Smithers Fane",
    }

    def naive(self, text, names):
        """What the scan did before the index existed. The reference answer."""
        return {
            (number, name)
            for number, line in enumerate(text.splitlines(), start=1)
            for name in names
            if re.search(r"\b" + re.escape(name) + r"\b", line, re.I)
        }

    def indexed(self, text, names):
        index = ps.build_index(names, set())
        return {(f.line, f.match) for f in ps.scan_text(text, "f.md", index)}

    def assert_agrees(self, text):
        self.assertEqual(self.indexed(text, self.HOSTILE),
                         self.naive(text, self.HOSTILE))

    def test_agrees_with_a_naive_scan_over_hostile_lines(self):
        for line in (
            "seen by Jordan Vance today",
            "seen by Doctor Jordan Vance today",   # two names, one nested
            "JORDAN VANCE and jordan vance",
            "Ellery Fane referred to Ellery Voss",
            "handed off to Mary-Ann O'Dell at 0700",
            "the patient denies chest pain",       # bucket word, no name
            "doctor ellery patient vance jordan",  # every bucket word, no name
            "Jordan Vancely is not a hit",
            "",
            "no identifiers here",
        ):
            with self.subTest(line=line):
                self.assert_agrees(line)

    def test_agrees_line_by_line_across_a_whole_document(self):
        self.assert_agrees("\n".join([
            "clean line",
            "seen by Doctor Jordan Vance",
            "",
            "Ellery Voss, Ellery Fane, Mary-Ann O'Dell",
        ]))

    def test_a_nested_name_is_still_reported_separately(self):
        """The alternation fix would have lost this one, so it is asserted.

        A single alternation matches the outer name and resumes past it,
        silently dropping the inner. Bucketing does not.

        `prune_covered` now keeps such pairs out of the harvest, so this is no
        longer reachable from `corpus_identifiers`. It is still asserted:
        `build_index` is a matcher any caller may hand a set to, and the pruning
        leans on it behaving this way -- a nested name that survives pruning is
        one the corpus carries twice and must still be reported twice.
        """
        found = self.indexed("seen by Doctor Jordan Vance", self.HOSTILE)
        self.assertEqual(found, {(1, "Doctor Jordan Vance"), (1, "Jordan Vance")})

    def test_names_sharing_a_bucket_word_are_both_found(self):
        found = self.indexed("Ellery Fane paged Ellery Voss", self.HOSTILE)
        self.assertEqual(found, {(1, "Ellery Fane"), (1, "Ellery Voss")})

    def test_the_bucket_word_alone_is_not_a_finding(self):
        self.assertEqual(self.indexed("Zervas was the patient", self.HOSTILE), set())

    def test_folding_a_long_s_agrees(self):
        """``re.I`` matches ``s`` against U+017F LATIN SMALL LETTER LONG S, and
        ``'ſ'.lower()`` is itself while ``.casefold()`` is ``'s'``. Tokens
        are therefore casefolded -- but see the next test for why casefolding is
        not on its own enough.
        """
        line = "ſmithers Fane"
        self.assertTrue(self.naive(line, self.HOSTILE))  # the old scan caught it
        self.assert_agrees(line)

    def test_a_line_outside_ascii_is_tested_against_every_name(self):
        """Why casefolding is not enough, and the ASCII guard exists.

        ``str.casefold`` is **not** the equivalence ``re.I`` uses, and the Latin
        i family is where they part. ``re.I`` matches ``i`` against U+0130 and
        U+0131; ``'İ'.casefold()`` is ``i`` + U+0307 COMBINING DOT ABOVE,
        which is not a word character, so the line tokenizes to ``i`` + ``smail``
        and the bucket ``ismail`` is never reached. ``'ı'.casefold()`` is
        itself. Either way the name was skipped before its pattern ran -- a
        silent miss on the staged path as well as the audit.

        The guard is coarse on purpose: over pure ASCII, casefold and ``re.I``
        agree exactly, so anything else falls back to testing every name.
        """
        for label, line in (
            ("U+0130 dotted capital I", "İsmail Kaya"),
            ("U+0131 dotless small i", "ısmail Kaya"),
        ):
            with self.subTest(label=label):
                names = {"Ismail Kaya"}
                self.assertTrue(self.naive(line, names))  # the old scan caught it
                self.assertEqual(self.indexed(line, names), self.naive(line, names))

    def test_a_name_outside_ascii_is_tested_against_every_line(self):
        """The same hole from the other side: the exotic character is in the
        name and the line is plain, so the name's own bucket word is one no
        ASCII line can produce."""
        names = {"İsmail Kaya"}
        line = "seen by ismail kaya"
        self.assertTrue(self.naive(line, names))
        self.assertEqual(self.indexed(line, names), self.naive(line, names))

    def test_punctuation_outside_ascii_does_not_force_the_fallback(self):
        """The guard is on non-ASCII *word* characters, not on non-ASCII.

        This repo's Markdown carries em dashes and curly quotes on nearly every
        prose line. Falling back to every-name-per-line for those gives the
        right answer and loses most of the speedup -- `--all` measured 0.2s with
        this distinction and 2.0s without it.
        """
        index = ps.build_index(self.HOSTILE, set())
        line = "the note — filed “properly” — by Ellery Fane"
        self.assertLess(len(index.candidates(line)), len(index.everything))
        self.assertEqual(self.indexed(line, self.HOSTILE),
                         self.naive(line, self.HOSTILE))

    def test_a_letter_outside_ascii_does_force_the_fallback(self):
        index = ps.build_index(self.HOSTILE, set())
        self.assertEqual(list(index.candidates("İsmail")),
                         list(index.everything))

    def test_agrees_with_a_naive_scan_on_generated_input(self):
        """The hand-written cases above are the ones somebody thought of.

        This is the one that found the U+0130 hole. The alphabet is small and
        deliberately nasty -- the Latin i family, a long s, a Kelvin sign, an em
        dash, and the punctuation that splits word runs -- so short random names
        and lines collide often. Seeded, so a failure is reproducible.
        """
        alphabet = "aiIsSİıſK -'—"
        random = Random(20260811)
        for trial in range(400):
            names = {
                "".join(random.choices(alphabet, k=random.randint(1, 6)))
                for _ in range(4)
            }
            line = "".join(random.choices(alphabet, k=random.randint(0, 24)))
            with self.subTest(trial=trial):
                self.assertEqual(self.indexed(line, names), self.naive(line, names))

    def test_a_name_with_no_word_characters_is_always_tested(self):
        """No word run means no bucket, so such a name goes in the always-run
        list rather than being filed under nothing and never tested again."""
        names = {"-- --"}
        index = ps.build_index(names, set())
        self.assertEqual([name for name, _ in index.unbucketed], ["-- --"])
        self.assertEqual(index.buckets, {})
        # Whatever `\b` makes of a name edged with punctuation, the indexed scan
        # has to reach the same answer as the naive one.
        text = "signed-- --here"
        self.assertEqual(self.indexed(text, names), self.naive(text, names))

    def test_the_required_token_is_the_longest_word_in_the_name(self):
        # Longest, because it is the most selective: the rarer the word, the
        # fewer lines drag the name into a pattern match.
        self.assertEqual(ps._required_token("Jordan Vance"), "jordan")
        self.assertEqual(ps._required_token("Mary-Ann O'Dell"), "mary")
        self.assertIsNone(ps._required_token("-- --"))

    def test_findings_come_out_ordered_by_name(self):
        """The scanner prints these, and set iteration order is not stable
        across processes. These two names bucket in the opposite order to the
        order they are reported in, so the test fails if the buckets leak out.
        """
        names = {"Zeta Alpha", "Beta Gamma"}   # bucket words: alpha, gamma
        found = [f.match for f in ps.scan_text(
            "Zeta Alpha met Beta Gamma", "f.md", ps.build_index(names, set()))]
        self.assertEqual(found, ["Beta Gamma", "Zeta Alpha"])


class ShapeLayer(unittest.TestCase):
    def test_dob_with_a_date(self):
        rules = [f.rule for f in scan("dob 03/04/1990", names=set(), dates=set())]
        self.assertIn("dob-with-date", rules)

    def test_a_dob_field_name_in_a_table_is_not_a_hit(self):
        # skills/batch-shift/SKILL.md documents a `dob` field in a table; that
        # must not trip the scanner or the rule gets switched off.
        rules = [f.rule for f in scan("| `dob` | 15 |", names=set(), dates=set())]
        self.assertNotIn("dob-with-date", rules)

    def test_ssn_and_phone(self):
        for text, rule in (("123-45-6789", "ssn"), ("(304) 555-0142", "phone")):
            with self.subTest(rule=rule):
                found = scan(text, names=set(), dates=set())
                self.assertIn(rule, [f.rule for f in found])

    def test_mrn_with_digits(self):
        found = scan("MRN 4471902", names=set(), dates=set())
        self.assertIn("mrn-with-digits", [f.rule for f in found])

    def test_iso_dates_are_not_flagged(self):
        # The skill files are full of "measured 2026-08-11". Flagging those would
        # make the scanner unusable.
        found = scan("measured 2026-08-11 across 559 encounters",
                     names=set(), dates=set())
        self.assertEqual(found, [])

    def test_a_us_short_date_is_flagged(self):
        found = scan("seen 2-30-99", names=set(), dates=set())
        self.assertIn("us-short-date", [f.rule for f in found])


class SyntheticPragma(unittest.TestCase):
    SYNTHETIC = f'"""header\n\n{ps.SYNTHETIC_PRAGMA}\n"""\n'

    def test_pragma_suppresses_shape_rules(self):
        text = self.SYNTHETIC + 'assert has_dob("dob 03/04/1990")\n'
        self.assertEqual(scan(text, names=set(), dates=set()), [])

    def test_pragma_does_not_suppress_the_corpus_layer(self):
        """The whole point: a file may call its dates invented, never its names."""
        text = self.SYNTHETIC + 'assert has_name("Jordan Vance")\n'
        self.assertEqual([f.rule for f in scan(text)], ["corpus-name"])

    def test_pragma_does_not_suppress_a_real_corpus_date(self):
        text = self.SYNTHETIC + 'assert has_dob("dob 04/17/1988")\n'
        self.assertIn("corpus-date", [f.rule for f in scan(text)])

    def test_pragma_must_be_near_the_top(self):
        buried = "x\n" * 3000 + ps.SYNTHETIC_PRAGMA + "\n"
        self.assertFalse(ps.declares_synthetic(buried))

    def test_prose_about_the_pragma_does_not_exempt_a_file(self):
        """Explaining the rule is not invoking it.

        A substring test let any file that documented the pragma near its top
        exempt itself by accident, and two files did.
        """
        prose = (
            "# The scanner\n\n"
            f"A file needing PHI-shaped literals declares `{ps.SYNTHETIC_PRAGMA}` "
            "near its top. That exempts the shape rules only.\n"
        )
        self.assertFalse(ps.declares_synthetic(prose))
        found = scan(prose + "dob 03/04/1990\n", names=set(), dates=set())
        self.assertIn("dob-with-date", [f.rule for f in found])

    def test_the_repo_test_files_declare_it(self):
        for name in ("test_corpus_census.py", "test_phi_scan.py"):
            with self.subTest(file=name):
                text = (ps.REPO_ROOT / "tools" / name).read_text(encoding="utf-8")
                self.assertTrue(ps.declares_synthetic(text))

    def test_the_repo_test_files_declare_it_as_stored_on_disk(self):
        """As ``scan_all`` sees them, which is not what ``read_text`` returns.

        The working tree here is CRLF and ``read_text_if_text`` decodes bytes
        without newline translation, so the pragma line ends ``\\r\\n``. The test
        above cannot catch a rule that rejects that, because ``read_text``
        translates the ``\\r`` away first.
        """
        for name in ("test_corpus_census.py", "test_phi_scan.py"):
            with self.subTest(file=name):
                text = self.on_disk(ps.REPO_ROOT / "tools" / name)
                self.assertTrue(ps.declares_synthetic(text))

    def test_the_files_that_only_document_the_pragma_are_not_exempt(self):
        """Four files discuss the rule near their top. None of them invokes it.

        Three exempted themselves by accident until 2026-08-11 -- phi_scan.py via
        its own ``SYNTHETIC_PRAGMA`` assignment, README.md via its PHI section,
        test_icd10.py via a docstring paragraph -- while CLAUDE.md, which says the
        same thing further down, did not. What that hid was those files' own
        illustration of the date rule, not any real PHI.

        test_icd10.py is why this test lists files rather than testing a synthetic
        string: its docstring states it "deliberately does not claim" the pragma,
        and under the old rule saying so was how it claimed one.
        """
        for name in ("tools/phi_scan.py", "tools/test_icd10.py",
                     "README.md", "CLAUDE.md"):
            with self.subTest(file=name):
                text = self.on_disk(ps.REPO_ROOT / name)
                self.assertFalse(ps.declares_synthetic(text))

    def on_disk(self, path):
        """The file as ``scan_all`` reads it, failing loudly if it reads as binary."""
        text = ps.read_text_if_text(path)
        self.assertIsNotNone(text, f"{path} read as binary")
        return text

    def test_comment_punctuation_around_the_pragma_is_allowed(self):
        """A declaration has to survive being written in a comment.

        Nothing in the repo uses these forms today -- both real declarations sit
        in a bare docstring line -- so this pins the intent rather than a caller:
        the rule excludes prose, not comment syntax.
        """
        for line in (f"# {ps.SYNTHETIC_PRAGMA}",
                     f"// {ps.SYNTHETIC_PRAGMA}",
                     f" * {ps.SYNTHETIC_PRAGMA}",
                     f"    {ps.SYNTHETIC_PRAGMA}  "):
            with self.subTest(line=line):
                self.assertTrue(ps.declares_synthetic(f"header\n{line}\nbody\n"))

    def test_the_pragma_must_end_its_line(self):
        """Trailing prose is prose, wherever the line started."""
        self.assertFalse(
            ps.declares_synthetic(f"# {ps.SYNTHETIC_PRAGMA} is how you opt out\n")
        )

    def test_the_search_window_cannot_fake_a_line_end(self):
        """A prose line the window cut through is not a declaration.

        The cut has to land exactly where the pragma stops, on a line that starts
        with it -- so this is an accident, not an attack. But it was a way for a
        file to exempt itself by explaining the rule, which is the one thing the
        line anchor exists to prevent.
        """
        pragma_line_start = "x" * (ps.PRAGMA_SEARCH_CHARS - len(ps.SYNTHETIC_PRAGMA) - 1)
        cut_mid_sentence = (
            pragma_line_start + "\n" + ps.SYNTHETIC_PRAGMA + " is how you opt out\n"
        )
        self.assertFalse(ps.declares_synthetic(cut_mid_sentence))
        found = scan(cut_mid_sentence + "dob 03/04/1990\n", names=set(), dates=set())
        self.assertIn("dob-with-date", [f.rule for f in found])

    def test_an_unterminated_final_pragma_line_still_declares(self):
        """Dropping a cut line must not cost a file with no trailing newline."""
        self.assertTrue(ps.declares_synthetic(f'"""header\n\n{ps.SYNTHETIC_PRAGMA}'))


class PhiDirectories(unittest.TestCase):
    def test_both_working_and_output_are_guarded(self):
        # scratch/ is working material, output/ is finished notes. Both are
        # gitignored, so both are only ever staged via `git add -f`.
        for directory in ("scratch/", "output/"):
            with self.subTest(directory=directory):
                self.assertIn(directory, ps.PHI_DIRECTORIES)

    def test_shared_root_names_are_bound_to_the_path_layer(self):
        """A renamed output root must not escape both gitignore and the PHI guard."""
        self.assertIn(scratch_root().name + "/", ps.PHI_DIRECTORIES)
        self.assertIn(output_root().name + "/", ps.PHI_DIRECTORIES)

    def test_gitignore_lists_every_guarded_directory(self):
        """A guarded directory that is not gitignored is a trap, not a guard."""
        ignored = (ps.REPO_ROOT / ".gitignore").read_text(encoding="utf-8").split()
        for directory in ps.PHI_DIRECTORIES:
            with self.subTest(directory=directory):
                self.assertIn(directory, ignored)


class Redaction(unittest.TestCase):
    def test_findings_are_redacted_by_default(self):
        finding = scan("Jordan Vance")[0]
        rendered = finding.render(show=False)
        self.assertNotIn("Jordan Vance", rendered)
        self.assertIn("J***********", rendered)

    def test_show_reveals(self):
        self.assertIn("Jordan Vance", scan("Jordan Vance")[0].render(show=True))


class CoveredNamePruning(unittest.TestCase):
    """Dropping harvested names that cannot refuse a line on their own (#12).

    Mostly this is case-variant deduplication -- 465 of the 468 names dropped on
    2026-08-11 were another spelling of a name that is kept, and the corpus
    layer has always matched with ``re.I``. The remaining 3 are the longer
    phrases with a real name inside that #12 named as the reason the harvested
    class could not be reasoned about. Both fall out of one rule, so both are
    tested here.

    **This prunes the harvest, not the matcher.** ``build_index`` still reports
    nested names separately and `CorpusIndexing` still holds it to that; a name
    the harvest keeps is matched exactly as before. The only claim here is that
    the pruned set refuses exactly the lines the unpruned set refuses.
    """

    def refused_lines(self, text, names):
        index = ps.build_index(names, set())
        return {f.line for f in ps.scan_text(text, "f.md", index)}

    def assert_refuses_the_same_lines(self, text, names):
        self.assertEqual(self.refused_lines(text, ps.prune_covered(names)),
                         self.refused_lines(text, names))

    def test_a_phrase_containing_a_kept_name_is_dropped(self):
        self.assertEqual(ps.prune_covered({"Jordan Vance", "allergy Jordan Vance"}),
                         {"Jordan Vance"})

    def test_a_phrase_containing_no_kept_name_survives(self):
        """The residual #12 is really about: clinical vocabulary has no patient
        name in it, so nothing covers it and pruning leaves it alone."""
        self.assertEqual(ps.prune_covered({"Jordan Vance", "allergy nkda"}),
                         {"Jordan Vance", "allergy nkda"})

    def test_coverage_needs_a_word_boundary(self):
        """``\\bJordan Vance\\b`` does not match inside "Jordan Vancely", so the
        longer string really can refuse a line the shorter one cannot."""
        names = {"Jordan Vance", "Jordan Vancely"}
        self.assertEqual(ps.prune_covered(names), names)
        self.assert_refuses_the_same_lines("a Jordan Vancely line", names)

    def test_coverage_is_case_insensitive_like_the_match(self):
        self.assertEqual(ps.prune_covered({"Jordan Vance", "seen by JORDAN VANCE"}),
                         {"Jordan Vance"})

    def test_case_variants_leave_exactly_one_survivor(self):
        """Two spellings of one name cover each other. Dropping both would empty
        the layer, so the tie is broken and one is kept."""
        self.assertEqual(len(ps.prune_covered({"Jordan Vance", "jordan vance"})), 1)

    def test_a_chain_of_coverage_collapses_to_the_shortest(self):
        """B covers A and C covers B. Dropping B must not strand C -- the name
        inside B is inside C too, so the shortest speaks for all three."""
        self.assertEqual(
            ps.prune_covered({"Vance", "Jordan Vance", "seen by Jordan Vance"}),
            {"Vance"})

    def test_no_survivor_contains_another_survivor(self):
        """The property, stated as narrowly as it actually holds.

        #12's objection to exempting a class of harvested phrases was that some
        of them had a real patient name inside -- it counted two, and pruning
        drops 3. But what this asserts is only that no survivor contains another
        *surviving* name, which is weaker than "no survivor hides a name": see
        `KeptNames.test_a_short_name_is_removed_before_it_can_cover_anything`.
        """
        survivors = ps.prune_covered({
            "Jordan Vance", "Doctor Jordan Vance", "Priya Raman", "allergy nkda",
            "Ellery Fane", "Ellery Fane referred", "sore throat", "Mary-Ann O'Dell",
        })
        for outer in survivors:
            for inner in survivors:
                if outer != inner:
                    with self.subTest(outer=outer, inner=inner):
                        self.assertIsNone(
                            re.search(r"\b" + re.escape(inner) + r"\b", outer, re.I))

    def test_refuses_the_same_lines_over_hostile_input(self):
        names = CorpusIndexing.HOSTILE | {"allergy nkda", "seen by Ellery Fane"}
        for line in (
            "seen by Doctor Jordan Vance today",
            "seen by Ellery Fane",
            "allergy nkda",
            "Jordan Vancely is not a hit",
            "handed off to Mary-Ann O'Dell at 0700",
            "no identifiers here",
            "",
        ):
            with self.subTest(line=line):
                self.assert_refuses_the_same_lines(line, names)

    def test_refuses_the_same_lines_on_generated_input(self):
        """The hand-written cases are the ones somebody thought of.

        A tiny, collision-prone alphabet makes coverage between generated names
        common, which is the condition the argument has to hold under, and the
        apostrophe and space put word boundaries at the edges of a name as well
        as inside it. Seeded, so a failure is reproducible.
        """
        alphabet = "ab -'"
        random = Random(20260811)
        for trial in range(400):
            names = {
                "".join(random.choices(alphabet, k=random.randint(1, 7)))
                for _ in range(5)
            }
            line = "".join(random.choices(alphabet, k=random.randint(0, 20)))
            with self.subTest(trial=trial):
                self.assert_refuses_the_same_lines(line, names)


class ReviewHint(unittest.TestCase):
    """The pointer to `harvest_review`, printed on a corpus-name refusal (#12)."""

    NAME_HIT = [ps.Finding("f.md", 1, "corpus-name", "Jordan Vance")]
    SHAPE_HIT = [ps.Finding("f.md", 1, "us-short-date", "4-17-88")]
    WAITING = {"reaction latex", "vaccs utd"}

    def test_it_names_the_count_and_the_command(self):
        hint = ps.review_hint(self.NAME_HIT, self.WAITING)
        self.assertIn("2", hint)
        self.assertIn("tools/harvest_review.py", hint)

    def test_a_shape_only_refusal_does_not_drag_it_along(self):
        """The count is only worth reading when a *name* matched."""
        self.assertEqual(ps.review_hint(self.SHAPE_HIT, self.WAITING), "")

    def test_nothing_left_to_review_says_nothing(self):
        self.assertEqual(ps.review_hint(self.NAME_HIT, set()), "")

    def test_it_reports_how_many_and_never_which(self):
        """The hook's output has to stay safe to paste into a ticket. Apart from
        the count, the line is fixed text -- no harvested string reaches it."""
        one = ps.review_hint(self.NAME_HIT, {"reaction latex"})
        two = ps.review_hint(self.NAME_HIT, self.WAITING)
        self.assertEqual(one.replace("1 harvested", "N harvested"),
                         two.replace("2 harvested", "N harvested"))
        for string in self.WAITING:
            self.assertNotIn(string, two)


class KeptNames(unittest.TestCase):
    """The harvest's filter and its pruning, in the order `corpus_identifiers`
    runs them. Extracted so the wiring is reachable from a test: every case in
    `CoveredNamePruning` calls `prune_covered` directly, so dropping the call
    from the harvest left all of them green.
    """

    def test_it_both_filters_and_prunes(self):
        kept = ps.kept_names({"Jordan Vance", "jordan vance", "allergy nkda",
                              "Short", "seen by Jordan Vance"})
        self.assertEqual(kept, {"Jordan Vance"})

    def test_a_short_name_is_removed_before_it_can_cover_anything(self):
        """The limit of the "no survivor hides a name" claim, pinned down.

        The length floor runs first, so a real surname of five characters or
        fewer is gone before pruning and covers nothing -- and the phrase
        carrying it survives with the name still inside. No such survivor exists
        in the corpus today, which makes that luck rather than a guarantee.
        """
        kept = ps.kept_names({"Voss", "allergy Voss"})
        self.assertEqual(kept, {"allergy Voss"})
        self.assertTrue(re.search(r"\bVoss\b", kept.pop()))

    def test_an_allowlisted_entry_also_covers_nothing(self):
        """The same ordering via NOT_NAMES -- but this one is not a hole.

        An allowlisted entry is by definition not an identifier, so a phrase
        that outlives it is not hiding anything. Asserted to keep the two cases
        apart: only the length floor can strand a real name.
        """
        self.assertEqual(ps.kept_names({"nkda", "reaction nkda"}), {"reaction nkda"})


class NameHarvesting(unittest.TestCase):
    def test_accepts_a_two_part_name(self):
        self.assertTrue(ps._looks_like_a_name("Jordan Vance"))

    def test_rejects_a_single_word(self):
        self.assertFalse(ps._looks_like_a_name("Jordan"))

    def test_rejects_a_clinical_phrase_by_allowlist(self):
        self.assertIn("sore throat", ps.NOT_NAMES)

    def test_the_labeled_nkda_forms_are_exempt_too(self):
        """Exercises the filter, not just the membership.

        `corpus_identifiers` drops a harvested candidate with
        ``len(n) > 5 and n.lower() not in NOT_NAMES``. Asserting the entry is in
        the set proves nothing on its own -- this reproduces the expression, so
        the test fails if the filter is ever changed to compare something else.
        """
        harvested = {"Allergy NKDA", "allergies nkda", "Jordan Vance"}
        kept = {n for n in harvested if len(n) > 5 and n.lower() not in ps.NOT_NAMES}
        self.assertEqual(kept, {"Jordan Vance"})

    def test_a_labeled_form_would_otherwise_be_harvested(self):
        """The reason the entries are needed: the phrase does look like a name."""
        self.assertTrue(ps._looks_like_a_name("Allergy NKDA"))
        # Punctuation is what saved day-a -- "allergies: nkda" cannot be harvested.
        self.assertFalse(ps._looks_like_a_name("allergies: nkda"))

    def test_the_allowlist_is_lowercase(self):
        """corpus_identifiers filters on n.lower(), so a capital here never fires."""
        for phrase in ps.NOT_NAMES:
            with self.subTest(phrase=phrase):
                self.assertEqual(phrase, phrase.lower())

    def test_rejects_a_line_with_digits(self):
        self.assertFalse(ps._looks_like_a_name("bp 134/77 hr 79"))


class BinaryFiles(unittest.TestCase):
    """This repo tracks a 13 MB SQLite code set, and the scanner reads every
    tracked file. Decoded as text and regexed, a binary produces findings that
    are neither true nor false -- just bytes that happened to match. A scanner
    whose output cannot be trusted is worse than one that says nothing.
    """

    def test_a_null_byte_marks_a_file_binary(self):
        self.assertTrue(ps.looks_binary(b"SQLite format 3\x00\x04\x00\x01"))

    def test_plain_text_is_not_binary(self):
        self.assertFalse(ps.looks_binary(b"seen by Jordan Vance today\n"))

    def test_accented_text_is_not_binary(self):
        # Nothing in this repo needs them, but a scanner that called UTF-8 text
        # binary would skip a real file and say nothing about it.
        self.assertFalse(ps.looks_binary("clinician's note - café".encode("utf-8")))

    def test_reading_a_binary_file_yields_nothing_to_scan(self):
        path = Path(tempfile.mkdtemp()) / "code.sqlite"
        # A real SQLite header, then a corpus name in the bytes. Even a genuine
        # hit inside a binary is unactionable: there is no line to fix.
        path.write_bytes(b"SQLite format 3\x00" + b"Jordan Vance" + b"\x00\x01\x02")
        self.assertIsNone(ps.read_text_if_text(path))

    def test_reading_a_text_file_yields_its_content(self):
        path = Path(tempfile.mkdtemp()) / "note.md"
        path.write_text("seen by Jordan Vance today\n", encoding="utf-8")
        self.assertIn("Jordan Vance", ps.read_text_if_text(path))


class StagedDiffParsing(unittest.TestCase):
    """The staged path is already safe from binaries, and this pins down why."""

    def test_a_binary_diff_contributes_no_lines(self):
        # git emits no `+++ b/` header and no + lines for a binary file, so the
        # path never enters the additions map and `git show :path` is never
        # called on 13 MB of it. That is load-bearing and invisible, so it is
        # asserted here rather than trusted.
        diff = (
            "diff --git a/reference/icd10cm-2026.sqlite b/reference/icd10cm-2026.sqlite\n"
            "new file mode 100644\n"
            "index 0000000..1234567\n"
            "Binary files /dev/null and b/reference/icd10cm-2026.sqlite differ\n"
        )
        self.assertEqual(ps.parse_diff(diff), {})

    def test_a_text_diff_contributes_its_added_lines(self):
        diff = (
            "diff --git a/notes.md b/notes.md\n"
            "--- a/notes.md\n"
            "+++ b/notes.md\n"
            "@@ -0,0 +12 @@\n"
            "+seen by Jordan Vance today\n"
        )
        self.assertEqual(
            ps.parse_diff(diff), {"notes.md": [(12, "seen by Jordan Vance today")]}
        )

    def test_line_numbers_advance_within_a_hunk(self):
        diff = (
            "+++ b/notes.md\n"
            "@@ -0,0 +5,2 @@\n"
            "+first\n"
            "+second\n"
        )
        self.assertEqual(ps.parse_diff(diff), {"notes.md": [(5, "first"), (6, "second")]})


class LayerReport(unittest.TestCase):
    """#86 decision 2: a run has to say which layers it actually ran.

    The ticket's trap is that *a green check on a PHI scan that cannot see the
    corpus is worse than no check, because it reads as coverage*. In CI that is
    permanent -- ``scratch/`` is gitignored PHI and must never reach a runner --
    so the CI job prints this report beside its checkmark.

    **Derived, never typed.** The obvious implementation is a banner written
    into the workflow YAML, which is a claim about the scanner that the scanner
    does not make and nothing re-derives. #143 is what that becomes. So the
    report is computed from the scanner's own inputs, and the workflow only
    prints it.
    """

    def report(self, names=frozenset(), dates=frozenset(), scan_all=True):
        return "\n".join(ps.layer_report(set(names), set(dates), scan_all))

    def test_every_layer_is_named_whether_or_not_it_ran(self):
        """A layer omitted because it did not run is the omission that reads as
        coverage. All three are named in every configuration."""
        for scan_all in (True, False):
            with self.subTest(scan_all=scan_all):
                text = self.report(NAMES, DATES, scan_all).lower()
                for layer in ("path", "corpus", "shape"):
                    self.assertIn(layer, text)

    def test_a_dead_corpus_layer_says_not_run(self):
        line = self.corpus_line(self.report())
        self.assertIn("NOT RUN", line)

    def test_a_live_corpus_layer_says_active(self):
        line = self.corpus_line(self.report(NAMES, DATES, scan_all=False))
        self.assertIn("ACTIVE", line)

    def test_all_mode_reports_the_path_layer_as_not_run(self):
        """``--all`` walks tracked files, and every guarded directory is
        gitignored -- so there is no staged path for that layer to test. It is
        inapplicable rather than clean, which is the distinction this whole
        report exists to draw."""
        self.assertIn("NOT RUN", self.path_line(self.report(NAMES, DATES, scan_all=True)))
        self.assertIn("ACTIVE", self.path_line(self.report(NAMES, DATES, scan_all=False)))

    def test_the_shape_layer_is_always_active(self):
        """It needs nothing but the file, so it is the one layer a runner has."""
        for scan_all in (True, False):
            with self.subTest(scan_all=scan_all):
                self.assertIn("ACTIVE", self.shape_line(self.report(scan_all=scan_all)))

    def test_a_live_corpus_reports_counts_and_never_an_identifier(self):
        """`corpus_census.py`'s rule, and the reason this output is safe to paste
        into a ticket at all: counts only, never the matched string."""
        text = self.report(NAMES, DATES, scan_all=False)
        self.assertIn("2", self.corpus_line(text))
        for identifier in NAMES | DATES:
            with self.subTest(identifier=identifier):
                self.assertNotIn(identifier, text)

    def test_a_live_corpus_names_the_date_renderings_it_checks(self):
        line = self.corpus_line(self.report(NAMES, DATES, scan_all=False))
        for family in ("US numeric", "written English", "ISO"):
            with self.subTest(family=family):
                self.assertIn(family, line)

    def test_a_report_with_a_dead_layer_warns_that_clean_is_not_coverage(self):
        """The checkmark is the thing being defended against, so the warning has
        to be in the report rather than left to whoever reads it."""
        text = self.report()
        self.assertIn("NOT", text)
        self.assertRegex(text, r"(?i)clean")

    def test_a_report_with_every_layer_live_carries_no_warning(self):
        text = self.report(NAMES, DATES, scan_all=False)
        self.assertNotRegex(text, r"(?i)a clean result")

    def test_one_missing_source_reads_as_partial_and_never_as_active(self):
        """Three states, and a two-valued verdict has to lie about one of them.
        A half-present corpus reported ACTIVE is what let #93's fix reintroduce
        #93 -- see `missing_corpus_sources`."""
        line = self.corpus_line(
            "\n".join(ps.layer_report(set(NAMES), set(), False, ["day-file-text"]))
        )
        self.assertIn("PARTIAL", line)
        self.assertNotIn("ACTIVE", line)

    def test_both_missing_still_reads_as_not_run(self):
        line = self.corpus_line(
            "\n".join(ps.layer_report(set(), set(), False,
                                      ["name-index.json", "day-file-text"]))
        )
        self.assertIn("NOT RUN", line)

    def test_a_partial_layer_still_warns_that_clean_is_not_coverage(self):
        """Half a layer is not a layer, so the banner has to fire on it too."""
        text = "\n".join(ps.layer_report(set(NAMES), set(), False, ["day-file-text"]))
        self.assertRegex(text, r"(?i)a clean result")

    def test_a_partial_report_names_no_identifier(self):
        """The counts-only rule holds on every path, including the new one --
        this text reaches a CI step summary, which is a place people paste from."""
        text = "\n".join(ps.layer_report(set(NAMES), set(DATES), False, ["day-file-text"]))
        for identifier in NAMES | DATES:
            with self.subTest(identifier=identifier):
                self.assertNotIn(identifier, text)

    def _line(self, text, word):
        """The layer's own row, not the warning beneath it -- which names the
        dead layers and so contains their words too."""
        label = f"{word} layer "
        matches = [ln for ln in text.splitlines() if ln.strip().lower().startswith(label)]
        self.assertEqual(len(matches), 1, f"expected one {word!r} row in:\n{text}")
        return matches[0]

    def corpus_line(self, text):
        return self._line(text, "corpus")

    def path_line(self, text):
        return self._line(text, "path")

    def shape_line(self, text):
        return self._line(text, "shape")


class TheCorpusLayerStatesItsDenominator(unittest.TestCase):
    """A name count is not a coverage claim and read as one until #141.

    The index is harvested from the corpus and need not cover it, so an index
    three encounters short printed exactly what a complete one printed --
    ``ACTIVE`` and a number, on a page a reader trusts. The vocabulary could not
    express the difference either: ``missing_corpus_sources`` tests a source's
    presence on disk, so a file that is there and short is ``ACTIVE``.

    **Declared, never enforced**, ruled 2026-08-19. These assert the line and
    the absence of a status change together, because either alone is the wrong
    ruling.
    """

    def report(self, covered, encounters, missing=()):
        found = ni.Coverage(
            files=1, unique_files=1, encounters=encounters, covered=covered,
            entries=covered, orphans=0, unrecognized=0,
            proposed=encounters - covered, proposed_named=0,
            proposed_extra_strings=0,
        )
        return "\n".join(ps.layer_report(set(NAMES), set(DATES), False, list(missing), found))

    def test_a_complete_index_states_both_numbers(self):
        self.assertIn("names from 3 of 3 encounters", self.report(3, 3))

    def test_a_short_index_states_both_numbers(self):
        self.assertIn("names from 1 of 3 encounters", self.report(1, 3))

    def test_a_short_index_names_the_shortfall_and_its_remedy(self):
        text = self.report(1, 3)
        self.assertIn("2 encounter(s) have no name-index entry", text)
        self.assertIn("tools/name_index.py --write", text)

    def test_a_complete_index_says_nothing_further(self):
        self.assertNotIn("no name-index entry", self.report(3, 3))

    def test_a_shortfall_does_not_claim_the_layer_did_not_run(self):
        """The layer ran. What is short is the list it ran against, so this is
        its own line and never a fourth entry in the dead-layer warning."""
        self.assertNotIn('NOT "no PHI"', self.report(1, 3))

    def test_an_absent_source_beats_a_shortfall(self):
        """A missing ``name-index.json`` has no coverage to state, and PATIENT
        NAMES ARE NOT CHECKED is the stronger thing to say about that run."""
        text = self.report(1, 3, ["name-index.json"])
        self.assertIn("PATIENT NAMES ARE NOT CHECKED", text)
        self.assertNotIn("no name-index entry", text)

    def test_no_coverage_leaves_the_line_as_it_was(self):
        """``day-file-text/`` absent: there is no denominator to have."""
        text = "\n".join(ps.layer_report(set(NAMES), set(DATES), False))
        self.assertIn("ACTIVE", text)
        self.assertNotIn("names from", text)

    def test_it_reports_counts_and_never_an_identifier(self):
        text = self.report(1, 3)
        for identifier in NAMES | DATES:
            with self.subTest(identifier=identifier):
                self.assertNotIn(identifier, text)


class TheWalkedPopulation(unittest.TestCase):
    """#258: a clean result covers the set that was walked, and now says so.

    #254 ruled that every ``git ls-files`` walk states what a clean result
    covers, and `scan_all`'s statement landed in its docstring the way the four
    test walks' did. It is the one walk with **user-visible output**, so the
    honest form -- *no tracked file carries PHI* -- was written down and **not
    on the page the reader is looking at**. CI is where that lands: the job runs
    ``--all`` with nothing staged and prints `layer_report` beside its
    checkmark, and that report's subject was *which layers ran* rather than
    *what was scanned*.

    **The fact was already on the page, attached to the wrong layer.** The
    ``--all`` path-layer row read ``--all walks tracked files; nothing can be
    staged from a gitignored directory`` -- the honest form, spent explaining
    why the path layer is inapplicable rather than what the two live layers
    covered.

    Ruled 2026-08-19, all four of the ticket's open questions: the qualifier
    goes **into** `layer_report`, whose subject widens from *which layers ran*
    to *what was scanned*; it prints on **every** ``--all`` run, on
    `phi_scan`'s own *neither door buys silence* precedent; ``spelling_scan``
    gets the same treatment, being the walk with the recorded instance; and the
    staged mode states its population too, so an absent row never reads as a
    stronger claim.
    """

    def report(self, all_mode):
        return "\n".join(ps.layer_report(set(NAMES), set(DATES), all_mode))

    def scanned_row(self, text):
        rows = [ln for ln in text.splitlines() if ln.strip().startswith("scanned")]
        self.assertEqual(len(rows), 1, f"expected one scanned row in:\n{text}")
        return rows[0]

    def test_both_modes_name_the_set_they_walked(self):
        """Open question 4. The staged mode's population is unsurprising, which
        is not a reason to leave it silent: a reader who has learned to read
        ``--all``'s row would read its absence as a stronger claim."""
        for all_mode in (True, False):
            with self.subTest(all_mode=all_mode):
                self.assertTrue(self.scanned_row(self.report(all_mode)).strip())

    def test_the_all_mode_row_names_tracked_files_and_what_that_excludes(self):
        """Both limbs, on #254's reasoning: *tracked* alone is what the walk's
        name already said, and *untracked* alone never says what a pass means."""
        row = self.scanned_row(self.report(True))
        self.assertRegex(row, r"(?<!un)tracked files")
        self.assertRegex(row, r"(?i)untracked")

    def test_the_staged_row_names_what_a_commit_does_not_reach(self):
        row = self.scanned_row(self.report(False))
        self.assertIn("staged", row)
        self.assertRegex(row, r"(?i)not scanned")

    def test_the_walked_set_is_stated_once_and_on_its_own_row(self):
        """The ticket's own finding, made a rule: one fact, one row. Leaving the
        clause on the path-layer row as well would restate it in the place that
        made it unreadable -- and two copies of one claim, each editable without
        failing anything, is #220."""
        text = self.report(True)
        carriers = [ln for ln in text.splitlines() if "tracked" in ln.lower()]
        self.assertEqual(len(carriers), 1, f"expected one row about the walk in:\n{text}")
        self.assertEqual(carriers[0], self.scanned_row(text))

    def test_the_population_is_stated_before_the_layers(self):
        """A reader meets the scope before the verdicts, which is the order the
        claim has to be read in: every ACTIVE below is about this set."""
        for all_mode in (True, False):
            with self.subTest(all_mode=all_mode):
                lines = self.report(all_mode).splitlines()
                first_layer = next(
                    i for i, ln in enumerate(lines) if ln.strip().startswith("path layer")
                )
                self.assertLess(lines.index(self.scanned_row(self.report(all_mode))),
                                first_layer)

    def test_the_header_names_what_was_scanned_rather_than_the_layers(self):
        """Open question 1's cost, taken deliberately rather than absorbed. A
        header still reading ``layers`` over a row that is not a layer is the
        drift this repo refuses everywhere else."""
        for all_mode in (True, False):
            with self.subTest(all_mode=all_mode):
                header = self.report(all_mode).splitlines()[0]
                self.assertNotIn("layers", header)
                self.assertIn("coverage", header)

    def test_the_new_row_names_no_identifier(self):
        """Counts-only holds on the widened report too. This text reaches a CI
        step summary, which is a place people paste from."""
        text = self.report(True) + "\n" + self.report(False)
        for identifier in NAMES | DATES:
            with self.subTest(identifier=identifier):
                self.assertNotIn(identifier, text)


class TheShortfallReachesTheCommitter(unittest.TestCase):
    """The venue is the whole ruling, and the first version reached none of it.

    #141 comment 4: *"on every commit from every worktree, which is where most
    commits here are made."* The hook runs this scanner **bare**, so the only
    callers of ``layer_report`` are ``--layers`` -- which a person has to type --
    and the dead-corpus branch. A shortfall living only in that report printed on
    no commit at all, while this repo's prose said it printed on every one. That
    is #220's lesson: a prose claim no code change fails against.

    So these drive ``main`` on the ordinary path rather than ``layer_report``,
    which is the distinction the defect turned on.
    """

    def run_main(self, coverage, marker=None):
        """``main`` with the corpus present, the scan clean, and coverage stubbed."""
        real = (ps.corpus_identifiers, ps.missing_corpus_sources,
                ps.corpus_coverage, ps.scan_staged, ps.REPO_ROOT)
        ps.corpus_identifiers = lambda: (set(NAMES), set(DATES))
        ps.missing_corpus_sources = lambda: []
        ps.corpus_coverage = lambda: coverage
        ps.scan_staged = lambda index: []
        with tempfile.TemporaryDirectory() as temporary:
            ps.REPO_ROOT = Path(temporary)
            if marker is not None:
                target = ps.REPO_ROOT / ps.TRACKER_HARVEST_MARKER
                target.parent.mkdir(parents=True)
                target.write_text(json.dumps(marker), encoding="utf-8")
            try:
                out, err = io.StringIO(), io.StringIO()
                with redirect_stdout(out), redirect_stderr(err):
                    code = ps.main([])
                return code, out.getvalue(), err.getvalue()
            finally:
                (ps.corpus_identifiers, ps.missing_corpus_sources,
                 ps.corpus_coverage, ps.scan_staged, ps.REPO_ROOT) = real

    def coverage(self, covered, encounters):
        return ni.Coverage(
            files=1, unique_files=1, encounters=encounters, covered=covered,
            entries=covered, orphans=0, unrecognized=0,
            proposed=encounters - covered, proposed_named=0,
            proposed_extra_strings=0,
        )

    def test_a_short_index_is_named_on_an_ordinary_commit(self):
        code, out, err = self.run_main(self.coverage(548, 551))
        self.assertIn("3 encounter(s) have no name-index entry", err)
        self.assertIn("tools/name_index.py --write", err)

    def test_a_covered_index_adds_nothing(self):
        """This scanner cannot afford noise -- ``review_hint``'s argument.

        **Not "prints nothing": #258 landed between the writing and the merge**,
        and a staged run now always states the population it walked. What this
        asserts is that a covered index adds no *second* line to it.
        """
        code, out, err = self.run_main(self.coverage(551, 551))
        self.assertEqual(out, "")
        self.assertNotIn("name-index entry", err)
        self.assertEqual(len(err.strip().splitlines()), 2, err)
        self.assertIn(ps.TRACKER_HARVEST_NOTICE, err)

    def test_the_shortfall_does_not_refuse_the_commit(self):
        """Declared, never enforced. Ruled 2026-08-19."""
        self.assertEqual(self.run_main(self.coverage(548, 551))[0], 0)

    def test_it_says_how_many_and_never_which(self):
        """The hook's output has to stay safe to paste -- #12's rule."""
        err = self.run_main(self.coverage(548, 551))[2]
        for identifier in NAMES | DATES:
            with self.subTest(identifier=identifier):
                self.assertNotIn(identifier, err)

    def test_no_coverage_adds_nothing(self):
        """``day-file-text/`` absent: there is no denominator to have, so there
        is nothing to say about one -- beside #258's population row, which is
        about a different question and always prints."""
        err = self.run_main(None)[2]
        self.assertNotIn("name-index entry", err)
        self.assertIn("never run", err.lower())

    def test_an_absent_marker_reads_as_never_run_on_an_ordinary_commit(self):
        err = self.run_main(self.coverage(551, 551))[2]
        self.assertIn(ps.TRACKER_HARVEST_NOTICE, err)
        self.assertIn("never run", err.lower())

    def test_a_marker_states_its_exact_age(self):
        ran_on = CalendarDate.today() - timedelta(days=37)
        marker = {
            "version": 1,
            "ran_on": ran_on.isoformat(),
            "finding_counts": {},
        }

        err = self.run_main(self.coverage(551, 551), marker)[2]

        self.assertIn(ps.TRACKER_HARVEST_NOTICE, err)
        self.assertIn("37 day(s)", err)

    def test_age_is_stated_without_any_threshold_verdict(self):
        for age in (0, 400):
            with self.subTest(age=age):
                marker = {
                    "version": 1,
                    "ran_on": (
                        CalendarDate.today() - timedelta(days=age)
                    ).isoformat(),
                    "finding_counts": {},
                }
                err = self.run_main(self.coverage(551, 551), marker)[2]
                self.assertIn(f"{age} day(s)", err)
                self.assertNotRegex(
                    err.lower(), r"stale|overdue|threshold|too old"
                )

    def test_claude_points_at_the_command_that_supplies_the_notice(self):
        prose = (
            Path(__file__).resolve().parent.parent / "CLAUDE.md"
        ).read_text(encoding="utf-8")
        self.assertIn("python tools/tracker_scan.py --harvest", prose)
        self.assertIn(
            ps.TRACKER_HARVEST_NOTICE,
            self.run_main(self.coverage(551, 551))[2],
        )

class AnAllRunStatesItsCoverage(unittest.TestCase):
    """#258 open question 2: on **every** ``--all`` run, not only a degraded one.

    A clean ``--all`` printed nothing at all, so the population statement
    reached a reader only through ``--layers`` or a dead corpus. `phi_scan`'s
    own precedent cuts the other way -- ``PATIENT NAMES ARE NOT CHECKED`` prints
    whether or not a door was taken, because *neither door buys silence* -- and
    printing it conditionally would teach a reader that the silence means
    something.

    **Staged runs are untouched**, which is the same ruling read the other way:
    the staged row exists in the report, and the report still prints there only
    when a layer is degraded. The hook runs on every commit and this scanner
    cannot afford noise -- `review_hint` carries that argument already.
    """

    def setUp(self):
        self._saved = {
            name: getattr(ps, name)
            for name in ("corpus_identifiers", "_git", "scan_staged", "scan_all",
                         "missing_corpus_sources", "corpus_coverage")
        }
        self.addCleanup(self.restore)
        ps.scan_staged = lambda index: []
        ps.scan_all = lambda index: []
        ps.missing_corpus_sources = lambda: []
        ps.corpus_identifiers = lambda: (set(NAMES), set(DATES))
        # **The fifth stub, added when #141 merged.** Without it the one-line
        # assertion below reads the real `scratch/`: a short name index adds a
        # shortfall row, so this class would pass or fail on the state of
        # somebody's working directory rather than on its own subject.
        ps.corpus_coverage = lambda: None
        ps._git = lambda *args: ""

    def restore(self):
        for name, value in self._saved.items():
            setattr(ps, name, value)

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = ps.main(list(argv))
        return status, out.getvalue(), err.getvalue()

    def test_a_clean_all_run_still_states_what_it_walked(self):
        status, _, err = self.run_main(["--all"])
        self.assertEqual(status, 0)
        self.assertRegex(err, r"(?i)untracked")

    def test_the_statement_goes_to_stderr(self):
        """stdout is ``--layers``' channel and the CI job pipes it into the step
        summary; a scanning run writing there would corrupt that report."""
        _, out, _ = self.run_main(["--all"])
        self.assertEqual(out, "")

    def test_it_is_printed_once_when_the_corpus_is_also_dead(self):
        """Both reasons to print are live at once in CI, which is the only
        configuration that will ever happen there. Two copies of the report is
        the failure this test exists to catch."""
        ps.missing_corpus_sources = lambda: ["name-index.json", "day-file-text"]
        ps.corpus_identifiers = lambda: (set(), set())
        _, _, err = self.run_main(["--all", ps.ALLOW_NO_CORPUS_FLAG])
        self.assertEqual(err.count("phi-scan coverage"), 1)

    def test_a_clean_staged_run_states_its_population_and_nothing_else(self):
        """Open question 4, and the clause it was ruled on -- *so an absent
        banner never reads as a stronger claim*.

        **The first version of this change asserted silence here**, which
        satisfies *state it in both modes* on the letter by putting the row in
        the staged rendering and never printing it: the ordinary commit said
        nothing, and the row was reachable only through ``--layers`` or a
        degraded corpus. That leaves ``--all``'s row the only one and therefore
        the special case, which is exactly what the question was asked to
        remove. Caught by the spec axis of ``/code-review``.

        **One row and not the report**, which is where the noise argument
        survives: the other four lines answer a question nobody asked on an
        ordinary commit, and the full report still prints the moment a layer is
        degraded.
        """
        status, _, err = self.run_main([])
        self.assertEqual(status, 0)
        self.assertEqual(len(err.strip().splitlines()), 2, err)
        self.assertIn(ps.scanned_population(False), err)
        self.assertIn(ps.TRACKER_HARVEST_NOTICE, err)
        self.assertNotIn("layer", err)


class LayersCommandLine(unittest.TestCase):
    """``--layers`` reports and does not scan.

    Kept apart from a scanning run deliberately: the CI job prints the report as
    its own step, on the page the checkmark is attached to rather than in a log
    nobody opens.

    **The reason it was built is spent and the mode is not**, which is worth
    saying so nobody deletes it as redundant. It existed because a clean scan
    printed nothing at all, so the coverage had nowhere else to appear; since
    #258 an ``--all`` scan prints the same report to **stderr**. The step
    summary needs it on **stdout**, and a scanning run's stderr is where a
    refusal goes -- so the two channels stay separate and the mode stays.
    """

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = ps.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_layers_prints_the_report_and_exits_zero(self):
        status, out, _ = self.run_main(["--layers"])
        self.assertEqual(status, 0)
        for layer in ("path", "corpus", "shape"):
            self.assertIn(layer, out.lower())

    def test_the_report_goes_to_stdout(self):
        """So the CI job can pipe it into the step summary beside the checkmark,
        rather than leaving it in a log nobody opens."""
        _, out, err = self.run_main(["--layers"])
        self.assertTrue(out.strip())
        self.assertNotIn("path layer", err)

    def test_layers_names_the_mode_it_is_reporting_on(self):
        """``--layers`` alone answers for a staged run; with ``--all`` it answers
        for the whole tree, and the path layer differs between them.

        **The header is asserted by name, and the first version was not.** It
        only checked that the two outputs differ, which the path-layer line
        satisfies on its own -- so it stayed green while the header said
        ``(--all)`` for both. That was a live bug: renaming the parameter off
        ``scan_all`` left this one reference resolving to the module-level
        *function* of that name, which is always truthy. A test that passes
        because some other line moved is `test_icd10.py`'s two-reasons
        objection, and this is what it looks like from the inside.
        """
        _, staged, _ = self.run_main(["--layers"])
        _, everything, _ = self.run_main(["--layers", "--all"])
        self.assertNotEqual(staged, everything)
        self.assertIn("(staged)", staged.splitlines()[0])
        self.assertNotIn("--all", staged.splitlines()[0])
        self.assertIn("(--all)", everything.splitlines()[0])


class DidNotScan(unittest.TestCase):
    """Issue #93: a dead corpus layer refuses instead of warning.

    **The whole ticket is an exit status, not a message.** The old code printed
    ``no corpus under scratch/ -- the corpus layer is inactive`` and returned 0,
    which reads exactly like the ordinary preamble of a passing hook -- the
    ticket's own words. Two exit-0s meant two different things and nothing in the
    status told them apart.

    Every test here injects the corpus state rather than reading the real tree,
    because whether the machine running the suite happens to hold patient
    material is precisely the variable under test. A test that read the real
    ``scratch/`` would assert something different on the maintainer's machine
    than on a runner, which is the defect wearing a lab coat.
    """

    NAME_SOURCE = "name-index.json"
    DATE_SOURCE = "day-file-text"

    def setUp(self):
        self._saved = {
            name: getattr(ps, name)
            for name in ("corpus_identifiers", "_git", "scan_staged", "scan_all",
                         "missing_corpus_sources")
        }
        self.addCleanup(self.restore)
        # Nothing staged and nothing tracked, so a run's status is about the
        # corpus and never about a finding -- except where a test says otherwise.
        ps.scan_staged = lambda index: []
        ps.scan_all = lambda index: []
        self.set_config("")

    def restore(self):
        for name, value in self._saved.items():
            setattr(ps, name, value)

    def set_config(self, value):
        """Stand in for ``git config --bool --get``. Unset returns "" and exit 1,
        which this module already tolerates -- `_git` never checks a status."""
        ps._git = lambda *args: value

    def corpus(self, live, missing=None):
        """``missing`` overrides which halves are on disk, so the three states --
        both present, one present, neither -- are all reachable from a test."""
        if missing is None:
            missing = [] if live else [self.NAME_SOURCE, self.DATE_SOURCE]
        ps.missing_corpus_sources = lambda: list(missing)
        names = set(NAMES) if self.NAME_SOURCE not in missing else set()
        dates = set(DATES) if self.DATE_SOURCE not in missing else set()
        ps.corpus_identifiers = lambda: (names, dates)

    def run_main(self, argv=(), live=False, config="", missing=None):
        self.corpus(live, missing)
        self.set_config(config)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = ps.main(list(argv))
        return status, out.getvalue(), err.getvalue()

    def test_half_a_corpus_does_not_read_as_a_scan(self):
        """**This bug was introduced by #93's own fix and caught in review.**

        The first version inferred deadness from ``not names and not dates``, so
        a tree holding one source and not the other took the live path: no
        report, no refusal, exit 0. The ticket's own comment had said so in
        advance -- *option 2 cannot be gated on whether ``scratch/`` exists ...
        whatever refuses has to test for the corpus itself*.
        """
        for absent in (self.NAME_SOURCE, self.DATE_SOURCE):
            with self.subTest(absent=absent):
                status, _, err = self.run_main(missing=[absent])
                self.assertEqual(status, ps.NOT_SCANNED)
                self.assertIn(absent, err)

    def test_the_dangerous_half_is_named_for_what_it_costs(self):
        """With ``day-file-text/`` present and ``name-index.json`` gone the scan
        ran on dates alone -- which is checking no patient name at all, and the
        shape layer cannot stand in: #93's own *shape rules catch an SSN or a
        ``dob`` token; they do not catch a patient's name*."""
        _, _, err = self.run_main(missing=[self.NAME_SOURCE])
        self.assertIn("PATIENT NAMES ARE NOT CHECKED", err)

    def test_a_missing_date_half_does_not_claim_names_are_unchecked(self):
        """The report has to be true in both directions. Saying patient names
        are unchecked when they were is the mirror error, and it teaches a
        reader to discount the line that matters."""
        _, _, err = self.run_main(missing=[self.DATE_SOURCE])
        self.assertNotIn("PATIENT NAMES ARE NOT CHECKED", err)
        self.assertIn("date literals are not checked", err)

    def test_a_dead_corpus_refuses(self):
        """The commit stops. `tools/hooks/pre-commit` needs no edit to honor
        this -- it already ORs any non-zero into its own status."""
        status, _, _ = self.run_main()
        self.assertEqual(status, ps.NOT_SCANNED)

    def test_two_is_not_one(self):
        """A finding and a dead corpus are different claims about a tree, and a
        reader acts differently on each. `guidelines_search.py`'s arrangement."""
        self.assertNotEqual(ps.NOT_SCANNED, 1)
        self.assertNotEqual(ps.NOT_SCANNED, 0)

    def test_a_live_corpus_with_no_findings_is_still_zero(self):
        """The ordinary passing commit stays zero while declaring harvest age.

        The staged population and the harvest age are the two commit-path
        declarations. What it must not do is print the whole layer report on
        every commit, which is the noise `review_hint` already argues against.
        """
        status, _, err = self.run_main(live=True)
        self.assertEqual(status, 0)
        self.assertEqual(len(err.strip().splitlines()), 2, err)
        self.assertIn(ps.TRACKER_HARVEST_NOTICE, err)

    def test_the_flag_downgrades_the_status(self):
        status, _, _ = self.run_main([ps.ALLOW_NO_CORPUS_FLAG])
        self.assertEqual(status, 0)

    def test_the_config_downgrades_the_status(self):
        status, _, _ = self.run_main(config="true\n")
        self.assertEqual(status, 0)

    def test_an_unset_config_refuses(self):
        """Unset must be false. A default that allowed would put every machine
        that has never heard of this setting into the configuration #93 is about."""
        for value in ("", "false\n", "\n"):
            with self.subTest(value=value):
                status, _, _ = self.run_main(config=value)
                self.assertEqual(status, ps.NOT_SCANNED)

    def test_being_allowed_does_not_buy_silence(self):
        """The ruling that makes the escape safe: the flag is about the exit
        status, not about the message. `console_codec`'s errors="replace" shape --
        a stream that cannot move still has to print a legible line."""
        _, _, allowed = self.run_main([ps.ALLOW_NO_CORPUS_FLAG])
        _, _, refused = self.run_main()
        for text in (allowed, refused):
            self.assertIn("PATIENT NAMES ARE NOT CHECKED", text)
            self.assertIn("corpus layer", text)

    def test_the_refusal_names_both_doors(self):
        """A hook that stops a commit without saying how to proceed is a hook
        people learn to --no-verify around."""
        _, _, err = self.run_main()
        self.assertIn(ps.ALLOW_NO_CORPUS_CONFIG, err)
        self.assertIn(ps.ALLOW_NO_CORPUS_FLAG, err)
        self.assertIn("git config", err)

    def test_the_refusal_names_the_path_it_looked_in(self):
        """So a wrong resolution reads as a wrong resolution rather than as a
        missing corpus -- which is #93 itself, and would otherwise recur silently."""
        _, _, err = self.run_main()
        self.assertIn(str(ps.SCRATCH), err)

    def test_a_finding_outranks_a_dead_corpus(self):
        """`differential_scan.py`'s ruling, for its reason: returning NOT_SCANNED
        here would file the strongest thing known about the tree under the
        weakest heading."""
        ps.scan_staged = lambda index: [
            ps.Finding(path="notes.md", line=3, rule="shape-dob", match="4-17-88")
        ]
        status, _, err = self.run_main()
        self.assertEqual(status, 1)
        self.assertIn("refusing the commit", err)

    def test_a_refusal_on_a_dead_corpus_still_states_its_coverage(self):
        """So the finding reads as a floor rather than as the whole -- the same
        reason `differential_scan` names its unwelded count on an exit 1."""
        ps.scan_staged = lambda index: [
            ps.Finding(path="notes.md", line=3, rule="shape-dob", match="4-17-88")
        ]
        _, _, err = self.run_main()
        self.assertIn("PATIENT NAMES ARE NOT CHECKED", err)

    def test_layers_reports_and_never_refuses(self):
        """It scans nothing, so it has nothing to have failed to scan. The mode
        exists to be printed beside a checkmark, and a non-zero there would make
        the report itself the failure."""
        for argv in ([""], ["--all"]):
            with self.subTest(argv=argv):
                status, out, _ = self.run_main(["--layers", *argv])
                self.assertEqual(status, 0)
                self.assertIn("corpus layer", out)

    def test_the_degradation_goes_to_stderr(self):
        """stdout is `--layers`' channel, and the CI job pipes it into the step
        summary. A degradation notice landing there would corrupt that report."""
        _, out, err = self.run_main()
        self.assertEqual(out, "")
        self.assertTrue(err.strip())


class CorpusResolution(unittest.TestCase):
    """Where the scanner looks for the corpus, versus where it looks for files.

    These are two different trees in a worktree and #93 is what happens when one
    constant serves both.
    """

    def test_the_corpus_is_resolved_through_the_owning_checkout(self):
        from repo_root import scratch_root
        self.assertEqual(ps.SCRATCH, scratch_root())

    def test_the_scanned_tree_is_still_this_one(self):
        """`scan_all` walks from REPO_ROOT and `_git` runs there. Moving those to
        the main checkout would make a worktree scan somebody else's files, which
        is a worse bug than the one being fixed."""
        self.assertEqual(ps.REPO_ROOT, Path(ps.__file__).resolve().parent.parent)

    def test_every_corpus_path_hangs_off_the_resolved_root(self):
        """The three that must move together. A ledger left behind in the
        worktree would rule on names harvested from a corpus it cannot see."""
        self.assertEqual(ps.REVIEWED_LEDGER.parent, ps.SCRATCH)


if __name__ == "__main__":
    unittest.main()
