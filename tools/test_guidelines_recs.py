"""Tests for tools/guidelines_recs.py.

**Synthetic tables built in this file, and no PDF is ever opened.** ``*.pdf`` is
globally gitignored and the corpus is copyrighted documents outside the repo, so
a test that read one could not run on a fresh clone. Every function under test above
``extract`` takes a list of cells, which is what makes that possible -- the same line
``test_guidelines_extract.py`` draws around ``rebuild_text`` taking a dictionary.

The two shapes pinned hardest are the ones the whole mode distinction rests on: a
table that qualifies, and a table that looks like one and must not.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import hashlib
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import artifact_lock_test_support  # noqa: E402, F401
import guidelines_recs as recs  # noqa: E402
from prose_bind import ProseBind  # noqa: E402


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
    def test_every_marker_declares_a_valid_anchor_and_the_old_shape_is_a_type_error(self):
        self.assertEqual(
            {marker.anchor for marker in recs.TEXT_MARKERS},
            recs.MARKER_ANCHORS,
        )
        with self.assertRaises(TypeError):
            recs.Marker("old-shape", re.compile("marker"))
        with self.assertRaisesRegex(ValueError, "sideways"):
            recs.Marker("bad-value", re.compile("marker"), "sideways")

    def test_an_invalid_anchor_is_refused_again_when_the_reader_dispatches(self):
        malformed = recs.Marker("malformed", re.compile("marker"), recs.ANCHOR_LEADING)
        object.__setattr__(malformed, "anchor", "sideways")
        with mock.patch.object(recs, "TEXT_MARKERS", (malformed,)):
            with self.assertRaisesRegex(ValueError, "sideways"):
                recs.read_marker_recommendations(1, "marker text", "doc")

    def test_the_two_measured_windows_are_pinned(self):
        self.assertEqual(recs.FORWARD_LABEL_WINDOW, 160)
        self.assertEqual(recs.BACKWARD_LABEL_WINDOW, 920)

    def test_a_leading_marker_reads_forward_and_backs_off_the_cut_token(self):
        text = "Recommendation 3.1.1 " + "whole " * 30 + "unfinishedtoken"
        found = recs.read_marker_recommendations(8, text, "KDIGO/x")

        self.assertTrue(found[0].text.startswith("Recommendation 3.1.1"))
        self.assertFalse(found[0].text.endswith("unfinished"))
        self.assertLessEqual(len(found[0].text), recs.FORWARD_LABEL_WINDOW)

    def test_a_trailing_marker_reads_from_its_nearest_sentence_boundary(self):
        text = (
            "Previous recommendation should not leak. "
            "We suggest the treatment for this population "
            "(conditional recommendation, low certainty of evidence)."
        )
        found = recs.read_marker_recommendations(9, text, "IDSA/x")

        self.assertEqual(len(found), 1)
        self.assertTrue(found[0].text.startswith("We suggest the treatment"))
        self.assertNotIn("Previous recommendation", found[0].text)

    def test_backward_boundaries_ignore_abbreviations_and_decimal_units(self):
        text = (
            "We suggest culture for e.g. Streptococcus infection after 1.5 mg dosing "
            "rather than a Liberal Vs. Conservative split "
            "(conditional recommendation, low certainty of evidence)."
        )
        found = recs.read_marker_recommendations(9, text, "IDSA/x")

        self.assertTrue(found[0].text.startswith("We suggest culture"))

    def test_a_backward_read_with_no_sentence_boundary_takes_the_cap_on_a_whole_word(self):
        prefix = "intro " * 220
        marker = "(weak recommendation, low-quality evidence)"
        found = recs.read_marker_recommendations(9, prefix + marker, "IDSA/x")

        self.assertLessEqual(len(found[0].text), recs.BACKWARD_LABEL_WINDOW)
        self.assertTrue(found[0].text.endswith(marker))
        self.assertFalse(found[0].text.startswith("ntro"))

    def test_sub_references_are_part_of_the_leading_marker_anchor(self):
        found = recs.read_marker_recommendations(
            12, "Recommendation 11.8a was revised for clarity.", "ADA/x"
        )

        self.assertEqual(found[0].rec_id, "p12/recommendation/11.8a")

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
        """Ten documents in the corpus elide the words and write only the two grades.

        It is a separate marker because nothing else on the page says which convention
        is in use, and folding it into the spelled-out pattern would make a document
        that uses one look like a document that uses both.

        **This docstring read *three* for one merge**, from a count taken over the
        extracted text rather than over the PDFs and over a hand-picked ten files. None
        of the ten is reached by any other marker in this module, so the limb carries
        ten of the twenty-nine documents #173 moved and not three.
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

| Topic | Population | Grade | Interval | Year | Superseded by | Threshold sheet | File | Page |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Skin Cancer | fair-skinned young adults | B | not stated | 2018 |  |  | `skin.pdf` | 1 |
| Skin Cancer | adults older than 24 | C | not stated | 2018 |  |  | `skin.pdf` | 1 |
| Thyroid Dysfunction | nonpregnant adults | I | not stated | 2015 |  |  | `thyroid.pdf` | 2 |

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


def _rawline(text: str, *, gap_after: dict[int, float] | None = None) -> dict:
    """A minimal rawdict line; selected gaps model positioned word boundaries."""

    gaps = gap_after or {}
    chars: list[dict] = []
    cursor = 0.0
    for index, glyph in enumerate(text):
        chars.append(
            {
                "c": glyph,
                "origin": (cursor, 10.0),
                "bbox": (cursor, 0.0, cursor + 5.0, 10.0),
            }
        )
        cursor += 5.0 + gaps.get(index, 0.0)
    return {
        "blocks": [
            {"type": 0, "lines": [{"spans": [{"size": 10.0, "chars": chars}]}]}
        ]
    }


class _StubPage:
    def __init__(self, text, tables=(), raw=None, *, fail_raw=False):
        self._text = text
        self._tables = tables
        self._raw = raw if raw is not None else _rawline(text)
        self._fail_raw = fail_raw

    def get_text(self, kind="text"):
        if kind == "rawdict" and self._fail_raw:
            raise AssertionError("rawdict reader ran")
        return self._raw if kind == "rawdict" else self._text

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
        page = _StubPage(
            "Recommendation 3.1.1 We suggest screening.",
            tables=[COR_TABLE],
            fail_raw=True,
        )
        with stub_reader([page]):
            records, mode, source = recs.extract(Path("kdigo.pdf"), "KDIGO/x")
        self.assertEqual((mode, source), (recs.MODE_EXACT, recs.SOURCE_RULED_TABLE))
        self.assertEqual(len(records), 1)

    def test_the_marker_limb_recovers_a_welded_number_and_text(self):
        welded = "Recommendation3.3Yearly influenza vaccination is recommended."
        raw = _rawline(welded, gap_after={13: 4.0, 16: 4.0})
        page = _StubPage(welded, raw=raw)
        with stub_reader([page]):
            repaired, mode, source = recs.extract(Path("idsa.pdf"), "IDSA/x")
            raw_records, _, _ = recs.extract(
                Path("idsa.pdf"),
                "IDSA/x",
                marker_reader=lambda candidate: candidate.get_text("text"),
            )
        self.assertEqual((mode, source), (recs.MODE_BOUND, recs.SOURCE_TEXT_MARKER))
        self.assertEqual(raw_records, [])
        self.assertEqual(len(repaired), 1)
        self.assertIn("Recommendation 3.3 Yearly", repaired[0].text)

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


class DeclaredLimitsAndCensus(ProseBind, unittest.TestCase):
    def test_real_committed_ada_changelog_prefixes_are_recognized(self):
        fixture = (
            recs.REPO_ROOT
            / "fixtures"
            / "guidelines-recs-labels"
            / "ada-changelog-prefixes.txt"
        )
        labels = fixture.read_text(encoding="utf-8").splitlines()
        records = [
            recs.read_marker_recommendations(12, label, "ADA/x")[0]
            for label in labels
        ]

        self.assertEqual(recs.changelog_shape_census(records), len(labels))

    def test_a_mutated_real_prefix_outside_the_shape_matches_nothing(self):
        fixture = (
            recs.REPO_ROOT
            / "fixtures"
            / "guidelines-recs-labels"
            / "ada-changelog-prefixes.txt"
        )
        real = fixture.read_text(encoding="utf-8").splitlines()[0]
        mutated = real.replace(" was ", " now ", 1)
        records = recs.read_marker_recommendations(12, mutated, "ADA/x")

        self.assertEqual(recs.changelog_shape_census(records), 0)

    def test_the_changelog_census_is_a_shape_floor_not_a_verb_list(self):
        records = recs.read_marker_recommendations(
            12,
            "Recommendation 11.8a was revised. "
            "Recommendation 11.8b was written. "
            "Recommendation 11.8c now includes another item.",
            "ADA/x",
        )

        self.assertEqual(recs.changelog_shape_census(records), 2)

    def test_the_changelog_limit_is_appended_to_the_shared_registry(self):
        self.assertIn(
            "changelog-shape-floor",
            {row.key for row in recs.DECLARED_LIMITS},
        )

    def test_a_sweep_record_and_its_per_document_summary_carry_the_floor(self):
        record = recs.Recommendation(
            rec_id="p12/recommendation/11.8a",
            doc_id="society/doc",
            page=12,
            table="recommendation",
            number=1,
            cor=None,
            loe=None,
            text="Recommendation 11.8a was revised.",
            mode=recs.MODE_BOUND,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            destination = root / "records"
            source.mkdir()
            destination.mkdir()
            (source / "doc.pdf").write_bytes(b"synthetic")
            out = io.StringIO()
            with mock.patch.object(
                recs,
                "extract",
                return_value=([record], recs.MODE_BOUND, recs.SOURCE_TEXT_MARKER),
            ), contextlib.redirect_stdout(out):
                recs.build_sweep(
                    source,
                    destination,
                    {"commit": "a" * 40, "dirty": False},
                )
            payload = json.loads((destination / "doc.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["totals"]["changelog_shape_floor"], 1)
        self.assertIn("doc  changelog floor 1", out.getvalue())

    def test_the_glossary_describes_both_windows_and_the_boundary_stop(self):
        context = (recs.REPO_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        definition = context.split("**Recommendation label**:", 1)[1].split(
            "_Avoid_:", 1
        )[0]

        self.assertIn(str(recs.FORWARD_LABEL_WINDOW), definition)
        self.assertIn(str(recs.BACKWARD_LABEL_WINDOW), definition)
        self.assertIn("sentence boundary", definition)

    def test_the_registry_rows_are_named_three_field_records(self):
        self.assertEqual(len(recs.DECLARED_LIMITS), len(recs.NOT_REACHED))
        keys = [row.key for row in recs.DECLARED_LIMITS]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(
            {row.evidence for row in recs.DECLARED_LIMITS},
            set(recs.EvidenceDisposition),
        )
        self.assertEqual(
            recs.NOT_REACHED,
            tuple(row.limit for row in recs.DECLARED_LIMITS),
        )

    def test_the_registry_is_the_derived_population_not_a_floor(self):
        self.assertNotIn(
            "registry-population-floor",
            {row.key for row in recs.DECLARED_LIMITS},
        )
        source = (recs.REPO_ROOT / "tools" / "guidelines_recs.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("until it lands", source.lower())

    def test_record_resolution_limits_are_part_of_the_shared_registry(self):
        keys = {row.key for row in recs.DECLARED_LIMITS}
        self.assertTrue(
            {
                "record-source-unreadable",
                "literal-read-site-floor",
                "record-prefix-does-not-bind-source-key",
                "record-prefix-does-not-prove-producer",
                "recs-root-clutter-unreported",
            }.issubset(keys)
        )

    def test_ruled_table_identifier_collisions_are_declared(self):
        keys = {row.key for row in recs.DECLARED_LIMITS}
        self.assertIn("ruled-table-rec-id-collision", keys)

        shared = "x" * 48
        tables = [
            [
                [f"Recommendations for {shared} first"],
                ["COR", "LOE", "Recommendation"],
                ["1", "A", "1. First recommendation."],
            ],
            [
                [f"Recommendations for {shared} second"],
                ["COR", "LOE", "Recommendation"],
                ["1", "A", "1. Second recommendation."],
            ],
        ]

        rows = recs.read_table_recommendations(7, tables, "society/doc")

        self.assertEqual(rows[0].rec_id, rows[1].rec_id)

    def test_record_ownership_limits_are_part_of_the_shared_registry(self):
        keys = {row.key for row in recs.DECLARED_LIMITS}
        self.assertTrue(
            {
                "literal-read-site-floor",
                "source-pdf-left-corpus",
                "source-pdf-verification-skipped",
                "ownership-does-not-prove-content",
            }.issubset(keys)
        )

    def test_the_curated_table_read_once_limit_is_behavioral(self):
        row = next(
            row
            for row in recs.DECLARED_LIMITS
            if row.key == "curated-table-read-once"
        )
        self.assertEqual(
            row.limit,
            "A run does not establish that its curated rows match the committed "
            "curated table as it stands when the recommendation record is written.",
        )
        self.assertEqual(row.evidence, recs.EvidenceDisposition.BEHAVIOR)

    def test_prose_points_at_the_registry_without_copying_any_row(self):
        claude = (recs.REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        surfaces = {
            "the module docstring": recs.__doc__,
            "CLAUDE.md": claude,
        }
        for where, prose in surfaces.items():
            with self.subTest(where=where):
                self.assertProseIn("guidelines_recs.DECLARED_LIMITS", prose, where)
                for row in recs.DECLARED_LIMITS:
                    self.assertProseNotIn(row.key, prose, f"{where}: {row.key}")
                    self.assertProseNotIn(row.limit, prose, f"{where}: {row.key}")

    def test_the_prose_bind_detects_a_planted_key_and_sentence(self):
        for row in recs.DECLARED_LIMITS:
            with self.subTest(key=row.key):
                planted = f"See the object. {row.key}. {row.limit}"
                with self.assertRaises(AssertionError):
                    self.assertProseNotIn(row.key, planted)
                with self.assertRaises(AssertionError):
                    self.assertProseNotIn(row.limit, planted)

    @staticmethod
    def _literal_record_reads(source: str) -> list[int]:
        tree = ast.parse(source)
        parents: dict[ast.AST, ast.AST] = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node

        def scope(node: ast.AST) -> ast.AST:
            current = node
            while current in parents:
                current = parents[current]
                if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return current
            return tree

        literal_paths: dict[ast.AST, set[str]] = {}
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            if value is None or not any(
                isinstance(part, ast.Constant)
                and isinstance(part.value, str)
                and "recs-" in part.value
                for part in ast.walk(value)
            ):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            literal_paths.setdefault(scope(node), set()).update(
                target.id for target in targets if isinstance(target, ast.Name)
            )
        findings: list[int] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            inline_literal = any(
                isinstance(part, ast.Constant)
                and isinstance(part.value, str)
                and "recs-" in part.value
                for part in ast.walk(node)
            )
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in {"read_text", "read_bytes", "open"}
                and (
                    inline_literal
                    or (
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id in literal_paths.get(scope(node), set())
                    )
                )
            ) or (
                isinstance(node.func, ast.Name)
                and node.func.id == "open"
                and inline_literal
            ):
                findings.append(node.lineno)
        return findings

    def test_no_other_tool_directly_opens_a_literal_recommendation_record(self):
        """A one-assignment walk: paths assembled by deeper indirection are unseen."""
        positive = "path = root / f'recs-{key}.json'\nvalue = path.read_text()\n"
        self.assertEqual(self._literal_record_reads(positive), [2])
        self.assertEqual(
            self._literal_record_reads(
                "value = (root / f'recs-{key}.json').read_text()\n"
            ),
            [1],
        )
        self.assertEqual(
            self._literal_record_reads("value = open(root / f'recs-{key}.json')\n"),
            [1],
        )
        findings = {}
        for path in (recs.REPO_ROOT / "tools").glob("*.py"):
            if path.name == "guidelines_recs.py" or path.name.startswith("test_"):
                continue
            lines = self._literal_record_reads(path.read_text(encoding="utf-8"))
            if lines:
                findings[path.name] = lines
        self.assertEqual(findings, {})


class RecommendationRecordOwnership(unittest.TestCase):
    def trusted_record(self, pdf: Path, counted_from: str) -> dict:
        producer = recs.artifact_provenance.current_producer()
        producer["inputs"] = recs.artifact_provenance.producer_file_identity(
            recs.RECORD_TRUST_FLOOR[counted_from]
        )
        return {
            "doc_id": "Society/guideline",
            "source": str(pdf),
            "source_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "counted_from": counted_from,
            "mode": recs.MODE_EXACT,
            "producer": producer,
            "recommendations": [],
        }

    def test_each_counting_limb_has_its_ruled_input_floor(self):
        self.assertEqual(
            recs.RECORD_TRUST_FLOOR,
            {
                recs.SOURCE_RULED_TABLE: ("tools/guidelines_recs.py",),
                recs.SOURCE_CURATED_TABLE: (
                    "tools/guidelines_recs.py",
                    "reference/guidelines-uspstf.md",
                ),
                recs.SOURCE_TEXT_MARKER: (
                    "tools/guidelines_recs.py",
                    "tools/guidelines_extract.py",
                ),
                recs.SOURCE_NOTHING_FOUND: (
                    "tools/guidelines_recs.py",
                    "tools/guidelines_extract.py",
                    "reference/guidelines-uspstf.md",
                ),
            },
        )

    def test_the_writer_stamps_its_inputs_and_source_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "idsa.pdf"
            pdf.write_bytes(b"source bytes")
            target = root / "recs-idsa.json"
            with stub_reader([_StubPage("Give fluids (strong, moderate).")] ):
                status = recs.main([str(pdf), "--json", str(target)])
            payload = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(status, 0)
        self.assertEqual(
            payload["source_sha256"], hashlib.sha256(b"source bytes").hexdigest()
        )
        self.assertIsInstance(payload["producer"]["commit"], str)
        self.assertIsInstance(payload["producer"]["dirty"], bool)
        self.assertEqual(
            {row["path"] for row in payload["producer"]["inputs"]},
            set(recs.RECORD_TRUST_FLOOR[recs.SOURCE_TEXT_MARKER]),
        )

    def test_an_absent_or_unrecognized_counted_from_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "guideline.pdf"
            pdf.write_bytes(b"source")
            for counted_from in (None, "remembered-default"):
                with self.subTest(counted_from=counted_from):
                    payload = self.trusted_record(pdf, recs.SOURCE_RULED_TABLE)
                    if counted_from is None:
                        payload.pop("counted_from")
                    else:
                        payload["counted_from"] = counted_from
                    path = root / f"recs-{counted_from or 'absent'}.json"
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    with self.assertRaises(recs.UntrustedRecommendationRecord):
                        recs.load_recommendation_record(path)

    def test_a_changed_source_pdf_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "guideline.pdf"
            pdf.write_bytes(b"source")
            path = root / "recs-guideline.json"
            path.write_text(
                json.dumps(self.trusted_record(pdf, recs.SOURCE_RULED_TABLE)),
                encoding="utf-8",
            )
            pdf.write_bytes(b"different source")
            with self.assertRaisesRegex(
                recs.UntrustedRecommendationRecord, "source PDF sha256"
            ):
                recs.load_recommendation_record(path)

    def test_an_unreachable_source_pdf_is_bannered_but_the_record_can_be_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "guideline.pdf"
            pdf.write_bytes(b"source")
            payload = self.trusted_record(pdf, recs.SOURCE_RULED_TABLE)
            pdf.unlink()
            path = root / "recs-guideline.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                loaded = recs.load_recommendation_record(path)

        self.assertEqual(loaded["doc_id"], "Society/guideline")
        self.assertIn("SOURCE PDF NOT VERIFIED", stderr.getvalue())
        self.assertIn(str(pdf), stderr.getvalue())

    def test_the_untrusted_peek_returns_only_the_source_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recs-guideline.json"
            path.write_text(
                json.dumps(
                    {
                        "source": "C:/corpus/Society/guideline.pdf",
                        "recommendations": [{"text": "must not escape the peek"}],
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                recs.peek_recommendation_source(path), "guideline.pdf"
            )

    def test_source_filename_matching_owns_case_suffix_and_whitespace_normalization(self):
        self.assertTrue(
            recs.source_filename_matches_document(
                "GUIDELINE.PDF", "  Society/guideline  "
            )
        )
        self.assertFalse(
            recs.source_filename_matches_document("other.pdf", "Society/guideline")
        )

    def test_a_nontext_record_source_matches_no_document(self):
        record = {"source": {"path": "other.pdf"}}
        self.assertEqual(
            recs.record_built_from_another_document(record, "expected.pdf"), ""
        )

    def test_the_length_floor_counts_a_weld_and_its_known_false_positive(self):
        records = [
            recs.Recommendation(
                rec_id="p1/x/1",
                doc_id="x",
                page=1,
                table="x",
                number=1,
                cor=None,
                loe=None,
                text=(
                    "Recommendation3.3Yearlyinfluenzavaccination and "
                    "esophagogastroduodenoscopy are both reported."
                ),
                mode=recs.MODE_BOUND,
            )
        ]
        self.assertEqual(recs.glued_run_census(records), 2)

    def test_a_short_weld_is_outside_the_census(self):
        records = [
            recs.Recommendation(
                rec_id="p1/x/1",
                doc_id="x",
                page=1,
                table="x",
                number=1,
                cor=None,
                loe=None,
                text="shortweld stays below the declared floor",
                mode=recs.MODE_BOUND,
            )
        ]
        self.assertEqual(recs.glued_run_census(records), 0)

    def test_json_and_every_successful_summary_carry_the_census(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "idsa.pdf"
            pdf.write_bytes(b"stub")
            target = root / "recs-idsa.json"
            out = io.StringIO()
            with stub_reader([_StubPage("Give fluids (strong, moderate).")]):
                with contextlib.redirect_stdout(out):
                    status = recs.main([str(pdf), "--json", str(target)])
            payload = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(status, 0)
        self.assertIn("glued runs", out.getvalue())
        self.assertIn("changelog floor", out.getvalue())
        self.assertIn("spacing-dependent", out.getvalue())
        self.assertIn("#446", out.getvalue())
        self.assertIn("reports only", out.getvalue())
        self.assertEqual(payload["totals"]["glued_runs"], 0)
        self.assertEqual(payload["totals"]["changelog_shape_floor"], 0)

    def test_the_comparison_command_reports_the_repaired_difference(self):
        welded = "Recommendation3.3Yearly influenza vaccination is recommended."
        raw = _rawline(welded, gap_after={13: 4.0, 16: 4.0})
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "idsa.pdf"
            pdf.write_bytes(b"stub")
            out = io.StringIO()
            with stub_reader([_StubPage(welded, raw=raw)]):
                with contextlib.redirect_stdout(out):
                    status = recs.main([str(pdf), "--compare-readers"])
        self.assertEqual(status, 0)
        self.assertIn("reader changed   yes", out.getvalue())
        self.assertIn("raw records      0", out.getvalue())
        self.assertIn("repaired records 1", out.getvalue())

    def test_reader_comparison_preserves_repeated_marker_references(self):
        def marker(text: str) -> recs.Recommendation:
            return recs.Recommendation(
                rec_id="p1/recommendation/3.3",
                doc_id="idsa",
                page=1,
                table="recommendation",
                number=1,
                cor=None,
                loe=None,
                text=text,
                mode=recs.MODE_BOUND,
            )

        repaired = [marker("repaired first quotation"), marker("same last quotation")]
        raw = [marker("raw first quotation"), marker("same last quotation")]
        with mock.patch.object(
            recs,
            "extract",
            side_effect=[
                (repaired, recs.MODE_BOUND, recs.SOURCE_TEXT_MARKER),
                (raw, recs.MODE_BOUND, recs.SOURCE_TEXT_MARKER),
            ],
        ):
            raw_count, repaired_count, changed = recs.compare_marker_readers(
                Path("idsa.pdf"), "idsa"
            )
        self.assertEqual((raw_count, repaired_count, changed), (2, 2, 1))

    def test_reader_comparison_counts_an_inserted_duplicate_once(self):
        def marker(text: str) -> recs.Recommendation:
            return recs.Recommendation(
                rec_id="p1/recommendation/3.3",
                doc_id="idsa",
                page=1,
                table="recommendation",
                number=1,
                cor=None,
                loe=None,
                text=text,
                mode=recs.MODE_BOUND,
            )

        raw = [marker("first quotation"), marker("last quotation")]
        for repaired in (
            [marker("inserted quotation"), *raw],
            [raw[0], marker("inserted quotation"), raw[1]],
        ):
            with self.subTest(repaired=[record.text for record in repaired]):
                with mock.patch.object(
                    recs,
                    "extract",
                    side_effect=[
                        (repaired, recs.MODE_BOUND, recs.SOURCE_TEXT_MARKER),
                        (raw, recs.MODE_BOUND, recs.SOURCE_TEXT_MARKER),
                    ],
                ):
                    counts = recs.compare_marker_readers(Path("idsa.pdf"), "idsa")
                self.assertEqual(counts, (2, 3, 1))

    def test_the_corpus_comparison_command_derives_the_changed_document_count(self):
        welded = "Recommendation3.3Yearly influenza vaccination is recommended."
        raw = _rawline(welded, gap_after={13: 4.0, 16: 4.0})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.pdf").write_bytes(b"stub")
            nested = root / "Society"
            nested.mkdir()
            (nested / "two.pdf").write_bytes(b"stub")
            out = io.StringIO()
            with stub_reader([_StubPage(welded, raw=raw)]):
                with contextlib.redirect_stdout(out):
                    status = recs.main([str(root), "--compare-readers"])
        self.assertEqual(status, 0)
        self.assertIn("documents         2", out.getvalue())
        self.assertIn("changed documents 2", out.getvalue())
        self.assertIn("changed records   2", out.getvalue())


class TheCommittedTableIsWhatTheCommandReads(unittest.TestCase):
    """`curated_rows_for` with nothing stubbed, because every test above stubs it.

    Without this the whole limb could be wired to a file that does not exist and the
    synthetic tests would still be green -- which is the shape this repo keeps
    catching, a check that could not have worked reading as a settled result.
    """

    def test_it_reads_the_committed_table_and_finds_rows_for_a_file_named_in_it(self):
        recs.reset_curated_cache()
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
        recs.reset_curated_cache()
        parsed = recs.parse_curated_table(recs.CURATED_TABLE.read_text(encoding="utf-8"))
        filename = sorted(parsed)[0]
        self.assertEqual(recs.curated_rows_for(filename.upper()), parsed[filename])

    def test_a_later_record_stamp_does_not_establish_which_table_bytes_supplied_the_rows(self):
        first_table = CURATED
        second_table = CURATED.replace(
            "The USPSTF recommends counseling young adults with fair skin.",
            "The USPSTF recommends using sunscreen in young adults.",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            table_path = root / "reference" / "guidelines-uspstf.md"
            module_path = root / "tools" / "guidelines_recs.py"
            pdf = root / "skin.pdf"
            table_path.parent.mkdir()
            module_path.parent.mkdir()
            table_path.write_text(first_table, encoding="utf-8")
            module_path.write_text("# identity fixture\n", encoding="utf-8")
            pdf.write_bytes(b"source bytes")

            original_identity = recs.artifact_provenance.producer_file_identity
            with (
                mock.patch.object(recs, "CURATED_TABLE", table_path),
                mock.patch.object(
                    recs.artifact_provenance,
                    "producer_file_identity",
                    side_effect=lambda paths: original_identity(paths, repo_root=root),
                ),
            ):
                recs.reset_curated_cache()
                cached_rows = recs.curated_rows_for("skin.pdf")
                table_path.write_text(second_table, encoding="utf-8")
                payload, _ = recs._record_payload(
                    pdf,
                    "USPSTF/skin",
                    recs.curated_records(cached_rows, "USPSTF/skin"),
                    recs.MODE_EXACT,
                    recs.SOURCE_CURATED_TABLE,
                    {"commit": "fixture", "dirty": False},
                )

        stamped_inputs = {
            row["path"]: row["sha256"] for row in payload["producer"]["inputs"]
        }
        self.assertEqual(
            payload["recommendations"][0]["text"],
            "The USPSTF recommends counseling young adults with fair skin.",
        )
        self.assertEqual(
            stamped_inputs["reference/guidelines-uspstf.md"],
            hashlib.sha256(second_table.encode("utf-8")).hexdigest(),
        )

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
