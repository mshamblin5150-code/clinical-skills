"""Tests for the PHI pre-commit scanner.

phi-scan: synthetic

Every name and date below is invented. Testing a PHI scanner requires PHI-shaped
input, so this file declares itself synthetic -- and, like every file, remains
subject to the corpus layer regardless.
"""

import unittest

import phi_scan as ps

NAMES = {"Jordan Vance", "Priya Raman"}
DATES = {"4-17-88", "11/02/2011"}


def scan(text, path="some/file.md", names=None, dates=None):
    return ps.scan_text(text, path, NAMES if names is None else names,
                        DATES if dates is None else dates)


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

    def test_rejects_a_line_with_digits(self):
        self.assertFalse(ps._looks_like_a_name("bp 134/77 hr 79"))


if __name__ == "__main__":
    unittest.main()
