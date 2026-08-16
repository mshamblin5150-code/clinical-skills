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

import sys
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
