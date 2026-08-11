"""Tests for the ICD-10-CM builder and the lookup that reads its database.

These run against the committed excerpts in ``tools/testdata/`` — seventeen lines
of the CMS order file and three ``diag`` subtrees of the tabular XML — and never
against ``reference/icd10cm-2026.sqlite``. A test that read the shipped database
would pass for two different reasons, one of them being that the builder and the
test are wrong in the same way.

The excerpts are public-domain CMS content. They carry no patient data, so this
file needs no ``phi-scan: synthetic`` pragma and deliberately does not claim one.

``NotesReachTheCodeThatNeedsThem`` is the load-bearing class. Issue #10 turns on
one note — E66's *"code to identify body mass index (BMI), if known"* — being
readable from ``E66811``, the code an obesity diagnosis actually gets. The note
lives on the three-character parent, so a lookup that does not walk ancestors
finds nothing and the rule built on it silently never fires.
"""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import icd10_build as build
import icd10_lookup as lookup

TESTDATA = Path(__file__).resolve().parent / "testdata"
ORDER = (TESTDATA / "icd10cm_order_excerpt.txt").read_text(encoding="utf-8")
TABULAR = (TESTDATA / "icd10cm_tabular_excerpt.xml").read_text(encoding="utf-8")

# The excerpt holds these seventeen and nothing else. Stated here so a change to
# the file has to be made in both places on purpose.
EXCERPT_CODES = 17


class OrderFile(unittest.TestCase):
    def test_parses_the_code_and_its_descriptor(self):
        row = build.parse_order_line(
            "00001 A00     0 Cholera                                    "
            "                  Cholera"
        )
        self.assertEqual(row.code, "A00")
        self.assertEqual(row.long, "Cholera")

    def test_reads_the_billable_flag(self):
        rows = {row.code: row for row in build.parse_order_file(ORDER)}
        # A00 is a header; A000 is the billable child under it.
        self.assertFalse(rows["A00"].billable)
        self.assertTrue(rows["A000"].billable)

    def test_keeps_the_long_descriptor_where_the_short_one_is_abbreviated(self):
        rows = {row.code: row for row in build.parse_order_file(ORDER)}
        # The whole point of the descriptor discipline is that the clinician can
        # read the code's meaning. "w/o diagnosis of htn" does not do that job.
        self.assertEqual(
            rows["R030"].long,
            "Elevated blood-pressure reading, without diagnosis of hypertension",
        )
        self.assertEqual(
            rows["R030"].short, "Elevated blood-pressure reading, w/o diagnosis of htn"
        )

    def test_drops_the_short_descriptor_when_it_says_nothing_new(self):
        rows = {row.code: row for row in build.parse_order_file(ORDER)}
        self.assertIsNone(rows["Z6836"].short)

    def test_reads_every_line_of_the_excerpt(self):
        self.assertEqual(len(build.parse_order_file(ORDER)), EXCERPT_CODES)

    def test_ignores_a_blank_trailing_line(self):
        self.assertEqual(build.parse_order_file(ORDER + "\n\n"), build.parse_order_file(ORDER))


class TabularNotes(unittest.TestCase):
    def setUp(self):
        self.notes = build.parse_tabular(TABULAR)

    def by_code(self, code):
        return [n for n in self.notes if n.code == code]

    def test_extracts_the_bmi_instruction_issue_10_rests_on(self):
        texts = [n.text for n in self.by_code("E66") if n.kind == "useAdditionalCode"]
        self.assertEqual(len(texts), 1)
        # "if known" is CMS's own language, and the filled-anchor rule cites it
        # rather than asserting a house rule. If this phrase ever leaves the
        # release, the rule in icd10-cpt loses its authority and must be reworded.
        self.assertIn("if known", texts[0])

    def test_splits_a_multi_note_block_into_one_row_each(self):
        # E66's excludes2 carries four separate exclusions; collapsing them into
        # one string would make a code-by-code check unreadable.
        self.assertEqual(len(self.by_code("E66")), 6)
        self.assertEqual(
            len([n for n in self.by_code("E66") if n.kind == "excludes2"]), 4
        )

    def test_extracts_the_z68_age_boundary(self):
        texts = " ".join(n.text for n in self.by_code("Z68"))
        self.assertIn("20 years of age or older", texts)
        self.assertIn("2-19 years of age", texts)

    def test_stores_codes_without_their_dots(self):
        codes = {n.code for n in self.notes}
        self.assertFalse([c for c in codes if "." in c])

    def test_carries_no_note_kind_the_lookup_does_not_know(self):
        self.assertFalse({n.kind for n in self.notes} - set(build.NOTE_KINDS))

    def test_drops_an_entry_that_carries_no_text(self):
        # R11.16 ships an empty <note/> in the real release. An empty string in
        # the note table would read as an instruction that says nothing.
        empty = '<ICD10CM.tabular><diag><name>R11.16</name><codeAlso><note/></codeAlso></diag></ICD10CM.tabular>'
        self.assertEqual(build.parse_tabular(empty), [])

    def test_keeps_a_note_whose_text_is_split_by_inline_markup(self):
        # Notes carry nested elements. Reading .text alone truncates at the
        # first child, which looks like a shorter valid note, not a failure.
        markup = (
            "<ICD10CM.tabular><diag><name>E66</name><excludes1>"
            "<note>code <i>first</i> the cause</note>"
            "</excludes1></diag></ICD10CM.tabular>"
        )
        self.assertEqual(build.parse_tabular(markup)[0].text, "code first the cause")


class ReleaseProvenance(unittest.TestCase):
    """A committed code set that cannot name its own revision cannot be audited."""

    def test_reads_the_version_out_of_the_tabular(self):
        self.assertEqual(
            build.parse_version(TABULAR), "excerpt of FY2026 April 1 2026 release"
        )

    def test_says_so_rather_than_guessing_when_the_version_is_absent(self):
        self.assertIsNone(build.parse_version("<ICD10CM.tabular></ICD10CM.tabular>"))

    def test_names_the_revision_and_not_only_the_fiscal_year(self):
        # The bare tabular <version> is "2026", which is true of both the October
        # 2025 and the April 2026 revisions. Coding changed between them, so the
        # zip the build actually read has to appear in the string.
        release = build.release_string(
            "2026", Path("april-1-2026-code-descriptions-in-tabular-order.zip")
        )
        self.assertIn("2026", release)
        self.assertIn("april-1-2026", release)


def build_excerpt_database(release: str = "test release") -> Path:
    """A throwaway database built from the excerpts, for one test class."""
    path = Path(tempfile.mkdtemp()) / "excerpt.sqlite"
    build.write_database(
        path, build.parse_order_file(ORDER), build.parse_tabular(TABULAR), release
    )
    return path


class ExcerptDatabase(unittest.TestCase):
    """Base for the classes that need a built database rather than a parser."""

    @classmethod
    def setUpClass(cls):
        cls.path = build_excerpt_database()

    def setUp(self):
        self.db = lookup.open_database(self.path)

    def tearDown(self):
        self.db.close()


class BuildsADatabase(unittest.TestCase):
    def setUp(self):
        self.path = build_excerpt_database()
        self.db = sqlite3.connect(self.path)

    def tearDown(self):
        self.db.close()

    def test_holds_every_code(self):
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM code").fetchone()[0], EXCERPT_CODES
        )

    def test_records_which_release_it_was_built_from(self):
        # A committed data artifact that cannot say which fiscal year it is
        # cannot be audited against the one the clinician is being graded on.
        release = self.db.execute(
            "SELECT value FROM meta WHERE key = 'release'"
        ).fetchone()
        self.assertEqual(release[0], "test release")

    def test_rebuilding_over_an_existing_file_does_not_double_the_rows(self):
        build.write_database(
            self.path, build.parse_order_file(ORDER), build.parse_tabular(TABULAR), "second"
        )
        again = sqlite3.connect(self.path)
        self.assertEqual(again.execute("SELECT count(*) FROM code").fetchone()[0], EXCERPT_CODES)
        again.close()


class Lookup(ExcerptDatabase):
    def test_finds_a_code_written_the_way_a_clinician_writes_it(self):
        # Every code in this repo's notes is written with a dot; the CMS files
        # store none. The lookup absorbs that rather than making callers care.
        self.assertEqual(lookup.describe(self.db, "Z68.36").code, "Z6836")

    def test_tolerates_case_and_surrounding_whitespace(self):
        self.assertEqual(lookup.describe(self.db, "  z68.36 ").code, "Z6836")

    def test_returns_nothing_for_a_code_that_does_not_exist(self):
        # A fluent, plausible, wrong code number is the failure this database
        # exists to catch, so the miss has to be unambiguous.
        self.assertIsNone(lookup.describe(self.db, "Z68.99"))

    def test_reports_a_header_code_as_not_billable(self):
        # Z682 is "BMI 20-29, adult" — a real code that cannot be submitted.
        # Proposing it reads as correct until the claim is rejected.
        self.assertFalse(lookup.describe(self.db, "Z68.2").billable)
        self.assertTrue(lookup.describe(self.db, "Z68.20").billable)


class NotesReachTheCodeThatNeedsThem(ExcerptDatabase):
    """Issue #10's rule is only as good as the note it cites being findable."""

    def test_the_bmi_instruction_is_reachable_from_the_obesity_code(self):
        # E66.811 "Obesity, class 1" is the code an obesity diagnosis gets. The
        # BMI instruction sits on E66, three characters up.
        kinds = {n.kind: n.text for n in lookup.notes_for(self.db, "E66.811")}
        self.assertIn("useAdditionalCode", kinds)
        self.assertIn("if known", kinds["useAdditionalCode"])

    def test_a_note_names_the_ancestor_it_came_from(self):
        # A note inherited from E66 must not read as though it were written
        # against E66.811, or the clinician cannot check it in the tabular.
        note = next(
            n for n in lookup.notes_for(self.db, "E66.811") if n.kind == "useAdditionalCode"
        )
        self.assertEqual(note.code, "E66")

    def test_does_not_borrow_notes_from_a_code_that_merely_starts_the_same(self):
        # Z68 is an ancestor of Z6836. R03 is not an ancestor of anything here,
        # and E66's notes must not reach R030 by string proximity.
        codes = {n.code for n in lookup.notes_for(self.db, "R03.0")}
        self.assertNotIn("E66", codes)

    def test_a_code_with_no_notes_anywhere_up_its_tree_returns_empty(self):
        self.assertEqual(lookup.notes_for(self.db, "A00.0"), [])


if __name__ == "__main__":
    unittest.main()
