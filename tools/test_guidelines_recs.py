"""Tests for tools/guidelines_recs.py.

**Synthetic tables built in this file, and no PDF is ever opened.** ``*.pdf`` is
globally gitignored and the corpus is 179 copyrighted documents outside the repo, so
a test that read one could not run on a fresh clone. Every function under test above
``extract`` takes a list of cells, which is what makes that possible -- the same line
``test_guidelines_extract.py`` draws around ``rebuild_text`` taking a dictionary.

The two shapes pinned hardest are the ones the whole mode distinction rests on: a
table that qualifies, and a table that looks like one and must not.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import guidelines_recs as recs  # noqa: E402


def table(title: str, *rows: tuple[str, str, str]) -> list[list[str]]:
    """A ruled recommendation table in the shape PyMuPDF's find_tables emits.

    Row 0 is the merged caption -- one populated cell and empty siblings, which is
    what a merged cell extracts as. Row 1 is the COR/LOE header. The rest are
    recommendations.
    """
    return [[title, "", ""], ["COR", "LOE", "Recommendations"], *[list(row) for row in rows]]


class TableTitle(unittest.TestCase):
    def test_reads_the_caption_out_of_a_merged_first_row(self):
        self.assertEqual(recs.table_title(["Recommendations for OSA", "", ""]), "OSA")

    def test_stops_at_the_first_rendered_line(self):
        """AHA/ACC sets a sentence under the caption INSIDE the same merged cell.

        Flattening the whole cell put that sentence into the title and therefore into
        every rec_id derived from it -- a citation a reader has to type by hand. Found
        on the real document, fixed by cutting at the newline.
        """
        cell = "Recommendations for OSA\nReferenced studies that support the recommendations"
        self.assertEqual(recs.table_title([cell, "", ""]), "OSA")

    def test_a_data_table_has_no_title(self):
        """This is what keeps a table of numbers from being read as recommendations.

        A guideline is full of tables whose cells are numbers; only the ones captioned
        `Recommendations for` are recommendation tables.
        """
        self.assertIsNone(recs.table_title(["Table 5. Antihypertensive Doses", "", ""]))


class HeaderRow(unittest.TestCase):
    def test_recognizes_the_cor_loe_header(self):
        self.assertTrue(recs.is_header_row(["COR", "LOE", "Recommendations"]))

    def test_is_case_insensitive_but_position_sensitive(self):
        self.assertTrue(recs.is_header_row(["cor", "loe", "Recommendations"]))
        self.assertFalse(recs.is_header_row(["LOE", "COR", "Recommendations"]))

    def test_a_legend_explaining_the_classes_is_not_a_header(self):
        self.assertFalse(recs.is_header_row(["Class of Recommendation", "Level of Evidence"]))


class ReadingATable(unittest.TestCase):
    def test_reads_every_numbered_row(self):
        found = recs.read_table_recommendations(
            32,
            [table(
                "Recommendations for BP Treatment Threshold",
                ("1", "A", "1. In all adults with hypertension, initiation of medication"),
                ("1", "A", "2. In all adults with hypertension, a second agent"),
                ("2a", "B-R", "3. In adults with CVD, initiation is reasonable"),
            )],
            "AHA ACC/example",
        )
        self.assertEqual(len(found), 3)
        self.assertEqual([r.cor for r in found], ["1", "1", "2a"])
        self.assertEqual([r.loe for r in found], ["A", "A", "B-R"])
        self.assertEqual(found[0].mode, recs.MODE_EXACT)

    def test_rec_id_welds_page_table_and_number(self):
        """The identifier a sheet cites and the omission gate matches on.

        Built from position rather than from a running counter, so re-running the
        extractor on an unchanged PDF produces the same identifiers and a sheet does
        not silently come unpinned from the recommendations it scoped out.
        """
        found = recs.read_table_recommendations(
            32,
            [table("Recommendations for BP Treatment Threshold", ("1", "A", "3. Something"))],
            "AHA ACC/example",
        )
        self.assertEqual(found[0].rec_id, "p32/bp-treatment-threshold/3")

    def test_both_the_title_and_the_header_are_required(self):
        """Either alone is a real thing in these documents and neither is a
        recommendation table.

        The caption alone matches a continuation table's repeated heading; the header
        alone appears in the front-matter legend. Requiring both is what makes the
        `exact` mode claim defensible.
        """
        title_only = [["Recommendations for OSA", "", ""], ["Topic", "Detail", "Notes"], ["a", "b", "1. x"]]
        header_only = [["Table 5. Doses", "", ""], ["COR", "LOE", "Recommendations"], ["1", "A", "1. x"]]
        self.assertEqual(recs.read_table_recommendations(1, [title_only], "d"), [])
        self.assertEqual(recs.read_table_recommendations(1, [header_only], "d"), [])

    def test_an_unnumbered_row_is_not_a_recommendation(self):
        """A footnote or a continuation line inside the table body carries no number,
        and counting it would inflate the very figure gate 2 is allowed to refuse on."""
        found = recs.read_table_recommendations(
            5,
            [table(
                "Recommendations for OSA",
                ("1", "A", "1. A real recommendation"),
                ("", "", "*Doses shown are the maximum studied."),
            )],
            "d",
        )
        self.assertEqual(len(found), 1)

    def test_a_class_cell_that_will_not_parse_leaves_cor_none_rather_than_guessing(self):
        found = recs.read_table_recommendations(
            5, [table("Recommendations for OSA", ("see text", "A", "1. Something"))], "d"
        )
        self.assertEqual(len(found), 1)
        self.assertIsNone(found[0].cor)


class MarkerReading(unittest.TestCase):
    def test_finds_kdigo_style_markers(self):
        found = recs.read_marker_recommendations(
            8, "Recommendation 3.1.1 We suggest ... Practice Point 3.1.2 ...", "KDIGO/x"
        )
        self.assertEqual(len(found), 2)
        self.assertTrue(all(record.mode == recs.MODE_BOUND for record in found))

    def test_a_marker_hit_carries_no_class(self):
        """Running text does not put the class in a cell, so there is nothing to read.

        This is half of why a marker count cannot be enforced: the count is soft AND
        the classification is absent, so a row citing one has nothing to check against.
        """
        found = recs.read_marker_recommendations(8, "Recommendation 3.1.1 We suggest", "K")
        self.assertIsNone(found[0].cor)
        self.assertIsNone(found[0].loe)

    def test_a_cross_reference_is_counted_too_which_is_why_it_over_reports(self):
        """The over-report, demonstrated rather than asserted in prose.

        One real recommendation and two mentions of it come back as three. That is
        the whole reason `bound` may only warn, and pinning it here stops anyone
        "fixing" the count into something gate 2 would then be allowed to refuse on.
        """
        text = (
            "Recommendation 3.1.1 We suggest lowering blood pressure. "
            "See Recommendation 3.1.1 above. As stated in Recommendation 3.1.1, ..."
        )
        found = recs.read_marker_recommendations(8, text, "K")
        self.assertEqual(len(found), 3)


class IdsaProseMarkers(unittest.TestCase):
    """#173 limb 2. IDSA writes strength and certainty in prose, so the count is a bound.

    Two renderings are in the corpus and they are separate markers rather than one
    alternation, because they are two different things a reader sees on the page and a
    merged pattern would report a document as using a house style it does not.
    """

    def test_finds_the_spelled_out_form(self):
        found = recs.read_marker_recommendations(
            9, "Vancomycin is preferred (strong recommendation, moderate-quality evidence).", "IDSA/x"
        )
        self.assertEqual([record.table for record in found], ["grade-spelled-out"])
        self.assertEqual(found[0].mode, recs.MODE_BOUND)

    def test_finds_the_certainty_spelling_too(self):
        """The newer IDSA files write "certainty of evidence" where the older ones write
        "quality evidence". Both are the same house style and both are in the corpus."""
        found = recs.read_marker_recommendations(
            9, "(conditional recommendation, very low certainty of evidence)", "IDSA/x"
        )
        self.assertEqual(len(found), 1)

    def test_a_line_break_inside_the_parenthetical_does_not_defeat_it(self):
        """Taken off a real page. The renderer wraps inside the parenthesis, so a
        pattern that could not cross a newline would find nothing on the documents this
        limb exists for."""
        found = recs.read_marker_recommendations(
            9, "sleep study for patients (weak recommendation, low-\nquality evidence).24", "IDSA/x"
        )
        self.assertEqual(len(found), 1)

    def test_finds_the_terse_form(self):
        """Three documents in the corpus elide the words and write only the two grades.

        It is a separate marker because nothing else on the page says which convention
        is in use, and folding it into the spelled-out pattern would make a document
        that uses one look like a document that uses both.
        """
        found = recs.read_marker_recommendations(
            4, "Obtain blood cultures (strong, moderate). Give fluids (weak, very low).", "IDSA/y"
        )
        self.assertEqual([record.table for record in found], ["grade-terse", "grade-terse"])

    def test_the_terse_form_takes_only_the_four_certainty_words(self):
        """The whole safety of the terse pattern is that both halves are closed
        vocabularies. Opening the second half would match any parenthetical that starts
        with the word `strong`, which is an ordinary English adjective."""
        found = recs.read_marker_recommendations(4, "(strong, unclear) (strong, GRADE)", "IDSA/y")
        self.assertEqual(found, [])

    def test_a_marker_hit_carries_no_class(self):
        """The strength IS in the parenthetical, and it is still not read out.

        Gate 2 compares a sheet row's class against `cor`, and that comparison is the
        one thing catching a row pinned to the wrong recommendation. Filling `cor` from
        an over-reporting marker would make that check fire on pairings the marker
        invented, so it is left None deliberately rather than by oversight.
        """
        found = recs.read_marker_recommendations(9, "(strong recommendation, high-quality evidence)", "I")
        self.assertIsNone(found[0].cor)
        self.assertIsNone(found[0].loe)

    def test_another_society_quoting_a_graded_recommendation_is_counted_too(self):
        """The over-report, demonstrated on the case that is actually in the corpus.

        One USPSTF document quotes the American College of Physicians' recommendation in
        GRADE terms and one GOLD document states its own that way. Both are real marker
        hits in running text and both are counted, which is why this mode may only warn.
        """
        found = recs.read_marker_recommendations(
            2, "the ACP recommended a sleep study (weak recommendation, low-quality evidence)", "USPSTF/z"
        )
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].mode, recs.MODE_BOUND)


CURATED = """# USPSTF recommendation statements

## Grades

| Grade | Meaning | Rows |
| --- | --- | --- |
| A | Recommended | 1 |

## Recommendations

| Topic | Population | Grade | Interval | Year | Superseded by | File | Page |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Skin Cancer | fair-skinned young adults | B | not stated | 2018 |  | `skin.pdf` | 1 |
| Skin Cancer | adults older than 24 | C | not stated | 2018 |  | `skin.pdf` | 1 |
| Thyroid Dysfunction | nonpregnant adults | I | not stated | 2015 |  | `thyroid.pdf` | 2 |

## Statements

| Grade | Statement | File | Page |
| --- | --- | --- | --- |
| B | The USPSTF recommends counseling young adults with fair skin. | `skin.pdf` | 1 |
| C | The USPSTF recommends selectively offering counseling to adults older than 24. | `skin.pdf` | 1 |
| I | Evidence is insufficient to assess screening for thyroid dysfunction. | `thyroid.pdf` | 2 |
"""

SKIN_PAGE = (
    "The USPSTF recommends counseling young adults with fair skin. "
    "The USPSTF recommends selectively offering counseling to adults older than 24."
)


class ParsingTheCuratedTable(unittest.TestCase):
    """#173 limb 1. `reference/guidelines-uspstf.md` is the source, and it is a ruled
    table: one recommendation per row, the grade in a cell.

    Its two halves are written from one sorted list in one loop each by
    `uspstf_table.render_markdown`, so they are aligned by construction -- and this
    parser checks that rather than assuming it, because the alignment is the only thing
    joining a statement to the row it belongs to and nothing in the file declares it.
    """

    def test_groups_rows_by_the_file_they_came_from(self):
        rows = recs.parse_curated_table(CURATED)
        self.assertEqual(sorted(rows), ["skin.pdf", "thyroid.pdf"])
        self.assertEqual(len(rows["skin.pdf"]), 2)

    def test_pairs_each_row_with_its_statement(self):
        rows = recs.parse_curated_table(CURATED)
        self.assertEqual(rows["thyroid.pdf"][0].grade, "I")
        self.assertIn("thyroid dysfunction", rows["thyroid.pdf"][0].statement)
        self.assertEqual(rows["thyroid.pdf"][0].page, 2)

    def test_the_summary_table_of_grades_is_not_read_as_recommendations(self):
        """A three-column table whose first cell is a grade letter sits above the real
        one. A parser keyed on cell shape rather than on the heading a table sits under
        would read it as a recommendation belonging to no file at all."""
        rows = recs.parse_curated_table(CURATED)
        self.assertNotIn("", rows)
        self.assertEqual(sum(len(value) for value in rows.values()), 3)

    def test_two_halves_that_disagree_are_not_scanned(self):
        """The failure this exists for: someone edits one table and not the other.

        A positional join across two tables is silent when it goes wrong -- every
        statement shifts by one and every record still looks well formed -- so a
        disagreement is a refusal rather than a best effort.
        """
        broken = CURATED.replace("| I | Evidence is insufficient", "| A | Evidence is insufficient")
        with self.assertRaises(recs.DidNotScan):
            recs.parse_curated_table(broken)

    def test_an_empty_statement_is_not_scanned(self):
        """The one needle that is in every haystack.

        `curated_recommendations` asks whether the statement is on the page it cites,
        and an empty string is in every page -- so a blank statement cell would verify
        vacuously and hand gate 2 a recommendation to refuse a sheet over whose text
        nobody has.
        """
        broken = CURATED.replace(
            "Evidence is insufficient to assess screening for thyroid dysfunction.", ""
        )
        with self.assertRaises(recs.DidNotScan):
            recs.parse_curated_table(broken)

    def test_a_page_cell_that_is_not_a_number_is_not_scanned(self):
        """Every other malformation here raises; this one used to raise ValueError out
        of `int`, which reaches the caller as a traceback rather than as an exit 2."""
        broken = CURATED.replace("| `thyroid.pdf` | 2 |", "| `thyroid.pdf` | front |")
        with self.assertRaises(recs.DidNotScan):
            recs.parse_curated_table(broken)

    def test_halves_of_different_lengths_are_not_scanned(self):
        broken = CURATED.replace(
            "| I | Evidence is insufficient to assess screening for thyroid dysfunction. "
            "| `thyroid.pdf` | 2 |\n",
            "",
        )
        with self.assertRaises(recs.DidNotScan):
            recs.parse_curated_table(broken)


class CuratedRecommendations(unittest.TestCase):
    """Records built from the curated rows, each checked against the page it cites."""

    def rows(self, filename="skin.pdf"):
        return recs.parse_curated_table(CURATED)[filename]

    def test_one_record_per_row_in_exact_mode(self):
        found = recs.curated_recommendations(self.rows(), "USPSTF/skin", [SKIN_PAGE])
        self.assertEqual(len(found), 2)
        self.assertTrue(all(record.mode == recs.MODE_EXACT for record in found))

    def test_the_grade_is_the_class_and_there_is_no_separate_level_of_evidence(self):
        """USPSTF folds certainty into the letter, so `loe` is None rather than
        invented. Gate 2 lowercases both sides of its class comparison, so the grade is
        stored the way the table writes it and still reads as a grade under `--show`."""
        found = recs.curated_recommendations(self.rows(), "USPSTF/skin", [SKIN_PAGE])
        self.assertEqual([record.cor for record in found], ["B", "C"])
        self.assertTrue(all(record.loe is None for record in found))

    def test_rec_id_welds_page_topic_and_ordinal(self):
        found = recs.curated_recommendations(self.rows(), "USPSTF/skin", [SKIN_PAGE])
        self.assertEqual([record.rec_id for record in found], ["p1/skin-cancer/1", "p1/skin-cancer/2"])

    def test_a_row_that_is_not_on_the_page_it_cites_is_not_scanned(self):
        """This is what earns the `exact` label, and it is the answer to the objection
        that a committed intermediate can go stale.

        The AHA/ACC records are read out of the document as it is opened; these are read
        out of a file built from a corpus that may since have moved. So every row is
        checked against the page it names, and a document whose rows do not check is
        reported as not scanned rather than counted short.
        """
        with self.assertRaises(recs.DidNotScan):
            recs.curated_recommendations(self.rows(), "USPSTF/skin", ["an unrelated page"])

    def test_a_ligature_on_the_page_still_verifies(self):
        """Two of the corpus's rows failed this check on a typographic ligature alone --
        the page sets `deficiency` with U+FB01 and the table spells it out. Folding
        under NFKC is what makes the check about the words rather than about the type."""
        rows = recs.parse_curated_table(
            CURATED.replace("thyroid dysfunction", "thyroid deficiency")
        )["thyroid.pdf"]
        page = "Evidence is insufficient to assess screening for thyroid deﬁciency."
        found = recs.curated_recommendations(rows, "USPSTF/thyroid", ["", page])
        self.assertEqual(len(found), 1)

    def test_a_page_number_past_the_end_of_the_document_is_not_scanned(self):
        with self.assertRaises(recs.DidNotScan):
            recs.curated_recommendations(self.rows("thyroid.pdf"), "USPSTF/thyroid", ["one page only"])


class TheCommittedCuratedTable(unittest.TestCase):
    """The one thing in this file that reads the tree, on `test_reference_scan.py`'s
    reasoning: a committed artifact this parser would refuse is a coverage hole every
    synthetic test above would still be green over.

    **No count is asserted here.** The row and document totals are a property of a
    corpus refresh, they are already pinned against the artifact in
    `test_guideline_sheets.py`, and a second copy is #143.
    """

    def setUp(self):
        path = Path(__file__).resolve().parent.parent / "reference" / "guidelines-uspstf.md"
        self.rows = recs.parse_curated_table(path.read_text(encoding="utf-8"))

    def test_it_parses_and_its_two_halves_agree(self):
        self.assertTrue(self.rows)

    def test_every_grouped_file_has_rows_and_every_row_has_a_statement(self):
        for filename, rows in self.rows.items():
            self.assertTrue(filename.endswith(".pdf"), filename)
            self.assertTrue(rows, filename)
            for row in rows:
                self.assertTrue(row.statement.strip(), filename)
                self.assertGreaterEqual(row.page, 1)

    def test_the_grades_are_the_five_uspstf_letters(self):
        grades = {row.grade for rows in self.rows.values() for row in rows}
        self.assertEqual(grades, set("ABCDI"))

    def test_no_two_rows_of_one_file_collide_on_a_rec_id(self):
        """A duplicated identifier would let one sheet row account for two
        recommendations and satisfy the omission gate for both."""
        for filename, rows in self.rows.items():
            identifiers = [record.rec_id for record in recs.curated_records(rows, filename)]
            self.assertEqual(len(identifiers), len(set(identifiers)), filename)

    def test_no_two_topics_of_one_file_share_a_truncated_slug(self):
        """The assertion above cannot fail and this one can, which is why both are here.

        `slug` caps at 48 characters and most of these topics are longer than that, so
        two distinct topics in one document could truncate identically -- and the
        ordinal counter would then merge them into one apparent group while still
        handing out unique identifiers. Nothing would look wrong; a reader following a
        `rec_id` would land on the wrong topic. It does not happen on the table as
        committed, and a corpus refresh is exactly when it could start.
        """
        for filename, rows in self.rows.items():
            groups: dict[tuple[int, str], set[str]] = {}
            for row in rows:
                groups.setdefault((row.page, recs.slug(row.topic)), set()).add(row.topic)
            for key, topics in groups.items():
                self.assertEqual(len(topics), 1, f"{filename} {key}: {sorted(topics)}")


class _StubTable:
    def __init__(self, rows):
        self._rows = rows

    def extract(self):
        return self._rows


class _StubTables:
    def __init__(self, tables):
        self.tables = [_StubTable(rows) for rows in tables]


class _StubPage:
    def __init__(self, text, tables=()):
        self._text = text
        self._tables = tables

    def get_text(self, _kind="text"):
        return self._text

    def find_tables(self):
        return _StubTables(self._tables)


class _StubDocument:
    def __init__(self, pages):
        self._pages = pages
        self.closed = False

    def __iter__(self):
        return iter(self._pages)

    def close(self):
        self.closed = True


class _StubReader:
    """Stands in for ``pymupdf`` in ``sys.modules`` while a test runs.

    **Still no PDF is opened**, which is this file's whole arrangement -- ``*.pdf`` is
    globally gitignored and the corpus is outside the repo. The stub goes in rather than
    the real library because the real one would need a file to read; installing it under
    the name ``extract`` imports means the test runs identically on a machine that has
    PyMuPDF and on one that does not.
    """

    def __init__(self, pages):
        self._pages = pages

    def open(self, _path):
        return _StubDocument(self._pages)


@contextlib.contextmanager
def stub_reader(pages):
    previous = sys.modules.get("pymupdf")
    sys.modules["pymupdf"] = _StubReader(pages)
    try:
        yield
    finally:
        if previous is None:
            del sys.modules["pymupdf"]
        else:
            sys.modules["pymupdf"] = previous


COR_TABLE = [
    ["Recommendations for OSA", "", ""],
    ["COR", "LOE", "Recommendations"],
    ["1", "A", "1. Screen for obstructive sleep apnea."],
]


class Precedence(unittest.TestCase):
    """Which of the three readings answers a document, which is #173's live risk.

    The curated table has to win over the markers, and the case is real rather than
    imagined: one USPSTF document quotes another society's recommendation in GRADE
    terms, so reading the markers first would answer a curated 90-document society
    with a bound of 1 and call it scanned.
    """

    def setUp(self):
        # The committed table is replaced with the synthetic one for the length of the
        # test. `curated_rows_for` caches, so this is the seam -- the alternative is
        # passing the rows into `extract`, which would test the injected value rather
        # than the precedence.
        self.saved = recs._CURATED_CACHE
        recs._CURATED_CACHE = recs.parse_curated_table(CURATED)

    def tearDown(self):
        recs._CURATED_CACHE = self.saved

    def test_the_curated_table_beats_a_marker_on_the_same_page(self):
        page = _StubPage(SKIN_PAGE + " (weak recommendation, low-quality evidence)")
        with stub_reader([page]):
            records, mode, source = recs.extract(Path("skin.pdf"), "USPSTF/skin")
        self.assertEqual((mode, source), (recs.MODE_EXACT, recs.SOURCE_CURATED_TABLE))
        self.assertEqual(len(records), 2)
        self.assertNotIn("grade-spelled-out", {record.table for record in records})

    def test_a_ruled_table_beats_a_marker(self):
        page = _StubPage("Recommendation 3.1.1 We suggest screening.", tables=[COR_TABLE])
        with stub_reader([page]):
            records, mode, source = recs.extract(Path("kdigo.pdf"), "KDIGO/x")
        self.assertEqual((mode, source), (recs.MODE_EXACT, recs.SOURCE_RULED_TABLE))
        self.assertEqual(len(records), 1)

    def test_a_marker_answers_a_document_with_no_table_of_either_kind(self):
        page = _StubPage("Give fluids (strong, moderate).")
        with stub_reader([page]):
            records, mode, source = recs.extract(Path("idsa.pdf"), "IDSA/x")
        self.assertEqual((mode, source), (recs.MODE_BOUND, recs.SOURCE_TEXT_MARKER))
        self.assertEqual(len(records), 1)

    def test_a_document_with_none_of_the_three_is_counted_at_nothing(self):
        with stub_reader([_StubPage("An ordinary paragraph of guideline prose.")]):
            records, mode, _ = recs.extract(Path("gina.pdf"), "GINA/x")
        self.assertEqual(records, [])
        self.assertEqual(mode, recs.MODE_BOUND)

    def test_a_stale_curated_row_stops_the_document_being_counted(self):
        with stub_reader([_StubPage("a page this table's rows are not on")]):
            with self.assertRaises(recs.DidNotScan):
                recs.extract(Path("skin.pdf"), "USPSTF/skin")

    def test_the_command_reports_a_stale_curated_table_as_not_scanned(self):
        """Exit 2, and never the `no recommendation found` line below it.

        The two say different things -- one is a document with nothing in it and the
        other is a table that has come unpinned from the corpus -- and a reader who
        acted on the first would go looking in the PDF for a defect that is in the
        committed file.
        """
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "skin.pdf"
            pdf.write_bytes(b"not really a pdf, the reader is stubbed")
            out, err = io.StringIO(), io.StringIO()
            with stub_reader([_StubPage("a page this table's rows are not on")]):
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    status = recs.main([str(pdf)])
        self.assertEqual(status, 2)
        self.assertIn("did not scan", err.getvalue())
        self.assertNotIn("no recommendation found", err.getvalue())

    def test_the_command_names_where_an_exact_count_came_from(self):
        """`exact` arrives two ways since #173, and the report has to say which.

        A curated count is read out of a committed file rather than out of the PDF's
        own layout, and a reader deciding whether to trust a refusal needs that on the
        same screen as the word.
        """
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "skin.pdf"
            pdf.write_bytes(b"not really a pdf, the reader is stubbed")
            out, err = io.StringIO(), io.StringIO()
            with stub_reader([_StubPage(SKIN_PAGE)]):
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    status = recs.main([str(pdf)])
        self.assertEqual(status, 0)
        self.assertIn(recs.SOURCE_CURATED_TABLE, out.getvalue())
        self.assertIn(recs.CURATED_TABLE.name, out.getvalue())


class TheCommittedTableIsWhatTheCommandReads(unittest.TestCase):
    """`curated_rows_for` with nothing stubbed, because every test above stubs it.

    Without this the whole limb could be wired to a file that does not exist and the
    synthetic tests would still be green -- which is the shape this repo keeps
    catching, a check that could not have worked reading as a settled result.
    """

    def test_it_reads_the_committed_table_and_finds_rows_for_a_file_named_in_it(self):
        recs._CURATED_CACHE = None
        parsed = recs.parse_curated_table(recs.CURATED_TABLE.read_text(encoding="utf-8"))
        filename = sorted(parsed)[0]
        self.assertEqual(recs.curated_rows_for(filename), parsed[filename])

    def test_a_document_the_table_does_not_name_gets_no_curated_rows(self):
        self.assertEqual(recs.curated_rows_for("a-file-no-society-published.pdf"), [])

    def test_the_filename_is_matched_regardless_of_case(self):
        """`Path.name` returns what the caller typed, not what the filesystem holds.

        On Windows a path pasted with different case opens the same document and
        reaches `curated_rows_for` spelled differently, and an exact-match miss is
        silent: the document falls through to the markers and comes back `bound`
        where it should have come back `exact`.
        """
        recs._CURATED_CACHE = None
        parsed = recs.parse_curated_table(recs.CURATED_TABLE.read_text(encoding="utf-8"))
        filename = sorted(parsed)[0]
        self.assertEqual(recs.curated_rows_for(filename.upper()), parsed[filename])

    def test_two_files_differing_only_in_case_are_not_scanned(self):
        """Unreachable against the committed table, which is the reason to test it here.

        The case-insensitive lookup is only unambiguous while no two rows collide, and
        picking one of two would attach a document to the wrong recommendations
        silently. The committed table has no such pair -- the test below asserts that
        -- so a corpus refresh is the only way this arrives, and it arrives as a
        refusal rather than as a guess.
        """
        saved = recs._CURATED_CACHE
        recs._CURATED_CACHE = {"Skin.pdf": [], "skin.pdf": []}
        try:
            with self.assertRaises(recs.DidNotScan):
                recs.curated_rows_for("SKIN.pdf")
        finally:
            recs._CURATED_CACHE = saved

    def test_the_committed_table_names_no_two_files_differing_only_in_case(self):
        """Which is what makes the lookup above unambiguous rather than a guess."""
        parsed = recs.parse_curated_table(recs.CURATED_TABLE.read_text(encoding="utf-8"))
        lowered = [name.lower() for name in parsed]
        self.assertEqual(len(lowered), len(set(lowered)))


class Slug(unittest.TestCase):
    def test_is_lowercase_hyphenated_and_bounded(self):
        long_title = (
            "BP Treatment Threshold and the Use of CVD Risk Estimation to Guide Drug "
            "Treatment of Hypertension"
        )
        result = recs.slug(long_title)
        self.assertLessEqual(len(result), 48)
        self.assertRegex(result, r"^[a-z0-9-]+$")
        self.assertFalse(result.endswith("-"))


if __name__ == "__main__":
    unittest.main()
