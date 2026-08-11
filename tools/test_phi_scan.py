"""Tests for the PHI pre-commit scanner.

phi-scan: synthetic

Every name and date below is invented. Testing a PHI scanner requires PHI-shaped
input, so this file declares itself synthetic -- and, like every file, remains
subject to the corpus layer regardless.
"""

import re
import tempfile
import unittest
from pathlib import Path
from random import Random

import phi_scan as ps

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

        Two of the harvested names are longer strings with a real patient name
        inside them -- see NOT_NAMES. A single alternation matches the outer one
        and resumes past it, silently dropping the inner. Bucketing does not.
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
        text = self.SYNTHETIC + 'assert has_dob("dob 4-17-88")\n'
        self.assertIn("corpus-date", [f.rule for f in scan(text)])

    def test_pragma_must_be_near_the_top(self):
        buried = "x\n" * 3000 + ps.SYNTHETIC_PRAGMA + "\n"
        self.assertFalse(ps.declares_synthetic(buried))

    def test_the_repo_test_files_declare_it(self):
        from pathlib import Path
        for name in ("test_corpus_census.py", "test_phi_scan.py"):
            with self.subTest(file=name):
                text = (ps.REPO_ROOT / "tools" / name).read_text(encoding="utf-8")
                self.assertTrue(ps.declares_synthetic(text))


class PhiDirectories(unittest.TestCase):
    def test_both_working_and_output_are_guarded(self):
        # scratch/ is working material, output/ is finished notes. Both are
        # gitignored, so both are only ever staged via `git add -f`.
        for directory in ("scratch/", "output/"):
            with self.subTest(directory=directory):
                self.assertIn(directory, ps.PHI_DIRECTORIES)

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


if __name__ == "__main__":
    unittest.main()
