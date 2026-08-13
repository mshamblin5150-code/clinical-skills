"""Tests for the guideline catalog's parsers, classifiers and checker.

These run against the committed fixtures in ``tools/testdata/`` and never against
``C:/codeing/guidelines-src`` or ``reference/guidelines-catalog.md``. Same
reasoning as ``test_icd10.py``: a test that read the real corpus would pass for
two different reasons, one of them being that the extractor and the test are
wrong in the same way. Nothing here opens a PDF, so ``pypdf``/``fitz`` are not
needed to run the suite.

The page fixtures are ``%%PAGE%%``-delimited plain text standing in for what the
extractor hands back per page. They carry no patient data of any kind — they are
public-domain USPSTF and CDC material plus the functional running heads of a
journal PDF — so this file needs no ``phi-scan: synthetic`` pragma and
deliberately does not claim one.

``AccessLinesAreNotPublicationDates`` is the load-bearing class. Every AHA/ACC
file in the corpus, and most IDSA ones, carry ``Downloaded from ... 2026`` on
every page. That line is the most-repeated year in the document, so a year rule
that does not exclude it reports the day the corpus was collected as the
publication year of a 2018 guideline — and ``year`` is the only staleness signal
this catalog has.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import guidelines_catalog as gc

TESTDATA = Path(__file__).resolve().parent / "testdata"


def pages(name: str) -> list[str]:
    """Read a page fixture as the list of page texts the extractor would hand back.

    Anything before the first ``%%PAGE%%`` is preamble, not a page — which is
    what lets ``guidelines_capture_pages.txt`` carry its ``phi-scan: synthetic``
    declaration and the note explaining why it needs a date-shaped literal.
    """
    text = (TESTDATA / name).read_text(encoding="utf-8")
    return [p for p in text.split("%%PAGE%%")[1:] if p.strip()]


USPSTF_PAGES = pages("guidelines_uspstf_pages.txt")
JOURNAL_PAGES = pages("guidelines_journal_pages.txt")
CAPTURE_PAGES = pages("guidelines_capture_pages.txt")
CATALOG = (TESTDATA / "guidelines_catalog_sample.md").read_text(encoding="utf-8")

# Pinned so a fixture that grows or loses a page fails here rather than turning
# some other assertion green for the wrong reason. The capture fixture earned
# this: its preamble once spelled out the page delimiter and split into a third
# page that was pure prose, and the only symptom was one classify test flipping.
assert (len(USPSTF_PAGES), len(JOURNAL_PAGES), len(CAPTURE_PAGES)) == (3, 4, 2)


def row(**overrides) -> gc.Row:
    base = dict(
        society="USPSTF",
        filename="copd-screening.pdf",
        title="Screening for Chronic Obstructive Pulmonary Disease",
        topic="COPD screening",
        population="adult",
        year="2022",
        page_count="6",
        cls="recommendation-statement",
    )
    base.update(overrides)
    return gc.Row(**base)


def doc(**overrides) -> gc.Document:
    base = dict(
        society="USPSTF",
        filename="copd-screening.pdf",
        page_count=6,
        cls="recommendation-statement",
        title_guess="Screening for Chronic Obstructive Pulmonary Disease",
        year_guess="2022",
    )
    base.update(overrides)
    return gc.Document(**base)


class TableRows(unittest.TestCase):
    def test_splits_on_pipes_and_trims(self):
        self.assertEqual(gc.split_table_row("| a | b | c |"), ["a", "b", "c"])

    def test_an_escaped_pipe_stays_inside_its_cell(self):
        # The ACIP captures really are titled "... | Vaccines & Immunizations |
        # CDC", so a title with pipes in it is a corpus fact, not a hypothetical.
        cells = gc.split_table_row(r"| ACIP | f.pdf | Adults \| Vaccines \| CDC | t |")
        self.assertEqual(cells[2], "Adults | Vaccines | CDC")
        self.assertEqual(len(cells), 4)

    def test_cells_are_assigned_by_column_name_not_position(self):
        built = gc.row_from_cells(
            ["USPSTF", "f.pdf", "T", "topic", "adult", "2022", "6", "recommendation-statement"]
        )
        self.assertEqual(built.cls, "recommendation-statement")
        self.assertEqual(built.cells["class"], "recommendation-statement")

    def test_the_wrong_number_of_cells_raises_rather_than_shifting_columns(self):
        with self.assertRaises(ValueError):
            gc.row_from_cells(["USPSTF", "f.pdf", "T"])

    def test_separator_row_is_recognized(self):
        self.assertTrue(gc.is_separator_row(["---", ":---", "---:"]))
        self.assertFalse(gc.is_separator_row(["---", "USPSTF"]))


class ParsingTheCatalog(unittest.TestCase):
    def setUp(self):
        self.rows, self.unsettled, self.problems = gc.parse_catalog(CATALOG)

    def test_the_legend_table_above_the_catalog_is_not_read_as_rows(self):
        self.assertEqual(self.problems, [])
        self.assertEqual(len(self.rows), 3)
        self.assertEqual({r.society for r in self.rows}, {"ACIP", "KDIGO", "USPSTF"})

    def test_the_table_ends_at_the_first_line_that_is_not_one(self):
        self.assertNotIn("Prose after the table", [r.society for r in self.rows])

    def test_cells_land_in_the_right_columns(self):
        acip = next(r for r in self.rows if r.society == "ACIP")
        self.assertEqual(acip.title, "Recommended Vaccinations for Adults | Vaccines & Immunizations | CDC")
        self.assertEqual(acip.page_count, "7")
        self.assertEqual(acip.cls, "web-capture")

    def test_the_closing_comment_indexes_by_filename_and_column(self):
        self.assertEqual(self.unsettled["schedule-adults.pdf"], {"year"})
        self.assertEqual(self.unsettled["KDIGO-2024-CKD-Guideline.pdf"], {"population"})

    def test_a_row_with_the_wrong_cell_count_is_reported_not_dropped_silently(self):
        broken = CATALOG.replace(
            "| USPSTF | copd-screening.pdf |", "| USPSTF | copd-screening.pdf | extra |"
        )
        rows, _, problems = gc.parse_catalog(broken)
        self.assertEqual(len(rows), 2)
        self.assertTrue(any("9 cells, expected 8" in p for p in problems))

    def test_a_file_with_no_catalog_table_says_so(self):
        _, _, problems = gc.parse_catalog("# Nothing here\n\nJust prose.\n")
        self.assertTrue(any("no table headed" in p for p in problems))

    def test_a_closing_comment_naming_a_column_that_cannot_be_unsettled_is_refused(self):
        text = CATALOG + "\n- `copd-screening.pdf` — `page_count` — nope\n"
        _, _, problems = gc.parse_catalog(text)
        self.assertTrue(any("page_count" in p for p in problems))


class DocumentClass(unittest.TestCase):
    def test_a_uspstf_title_page_is_a_recommendation_statement(self):
        self.assertEqual(gc.classify(USPSTF_PAGES), "recommendation-statement")

    def test_whitespace_is_squashed_before_the_markers_are_looked_for(self):
        # Several USPSTF files extract as "USPreventiveServicesTaskForce
        # RecommendationStatement" with the spaces gone.
        run_together = ["USPreventiveServicesTaskForceRecommendationStatement"]
        self.assertEqual(gc.classify(run_together), "recommendation-statement")

    def test_a_summary_of_recommendation_statements_heading_is_not_one(self):
        # Four KDIGO guidelines and the CDC opioid guideline carry this line in
        # their table of contents. Matching the phrase alone classed all five
        # wrongly.
        self.assertEqual(gc.classify(JOURNAL_PAGES), "guideline")

    def test_a_browser_print_is_a_web_capture(self):
        self.assertEqual(gc.classify(CAPTURE_PAGES), "web-capture")

    def test_a_capture_wins_over_the_words_on_the_captured_page(self):
        both = [CAPTURE_PAGES[0] + "\nUS Preventive Services Task Force Recommendation Statement"]
        self.assertEqual(gc.classify(both), "web-capture")

    def test_anything_else_is_a_guideline(self):
        self.assertEqual(gc.classify(["KDIGO 2024 Clinical Practice Guideline"]), "guideline")


class AccessLinesAreNotPublicationDates(unittest.TestCase):
    def test_the_download_stamp_does_not_become_the_year(self):
        self.assertEqual(gc.year_from_running_head(JOURNAL_PAGES), "2019")

    def test_the_year_in_the_running_head_wins_over_a_year_mentioned_once(self):
        self.assertEqual(gc.year_from_running_head(USPSTF_PAGES), "2022")

    def test_a_document_that_never_repeats_a_year_is_unsettled(self):
        self.assertEqual(gc.year_from_running_head(CAPTURE_PAGES), gc.UNSETTLED)

    def test_no_pages_at_all_is_unsettled(self):
        self.assertEqual(gc.year_from_running_head([]), gc.UNSETTLED)

    def test_a_year_in_the_title_beats_the_running_head(self):
        # The AHA fixture is the 2018 cholesterol guideline printed in a 2019
        # issue: the running head says 2019 on every page and the title says 2018.
        title = "2018 AHA/ACC Guideline on the Management of Blood Cholesterol"
        self.assertEqual(gc.year_guess(title, JOURNAL_PAGES), "2018")

    def test_without_a_year_in_the_title_the_running_head_is_used(self):
        self.assertEqual(gc.year_guess("Screening for COPD", USPSTF_PAGES), "2022")

    def test_a_tie_goes_to_the_later_year(self):
        # A reaffirmation prints the year it supersedes as often as its own, and
        # the earlier one is the superseded one. Ties only reach this rule when
        # the title carries no year, so the "2018 guideline in a 2019 issue" case
        # is not what is being decided here.
        reaffirmation = [
            "Screening for Asymptomatic Carotid Artery Stenosis\nJAMA. 2021 update of 2014",
            "The 2014 recommendation is reaffirmed. JAMA 2021;325(5):476-481",
        ]
        self.assertEqual(gc.year_from_running_head(reaffirmation), "2021")


class TitleGuess(unittest.TestCase):
    def test_a_usable_pdf_title_is_taken(self):
        got = gc.title_guess(
            "Screening for Chronic Obstructive Pulmonary Disease", USPSTF_PAGES, "copd.pdf"
        )
        self.assertEqual(got, "Screening for Chronic Obstructive Pulmonary Disease")

    def test_placeholder_pdf_titles_are_rejected(self):
        for junk in ("untitled", "Topic", "ajt_9_S3-cover", "KISU_v7_i1_COVER.indd"):
            self.assertFalse(gc.looks_like_title(junk, "x.pdf"), junk)

    def test_a_title_that_is_only_the_filename_is_rejected(self):
        self.assertFalse(gc.looks_like_title("GOLD REPORT 2026 v1", "GOLD REPORT 2026 v1.pdf"))

    def test_falling_back_to_the_title_page_takes_a_substantial_line(self):
        got = gc.title_guess("untitled", USPSTF_PAGES, "copd.pdf")
        self.assertEqual(got, "Screening for Chronic Obstructive Pulmonary Disease")

    def test_nothing_substantial_anywhere_is_unsettled(self):
        self.assertEqual(gc.title_guess(None, ["S3", "9", "2009"], "x.pdf"), gc.UNSETTLED)


class CheckAgainstTheCorpus(unittest.TestCase):
    def test_a_catalog_that_matches_the_corpus_passes(self):
        self.assertEqual(gc.check([row()], {}, [doc()]), [])

    def test_a_dropped_row_fails(self):
        failures = gc.check([], {}, [doc()])
        self.assertTrue(any("missing from the catalog" in f for f in failures))

    def test_a_row_for_a_file_that_is_gone_fails(self):
        failures = gc.check([row()], {}, [])
        self.assertTrue(any("missing from the corpus" in f for f in failures))

    def test_a_stale_page_count_fails(self):
        failures = gc.check([row(page_count="5")], {}, [doc()])
        self.assertTrue(any("page_count" in f for f in failures))

    def test_a_wrong_society_fails(self):
        failures = gc.check([row(society="IDSA")], {}, [doc()])
        self.assertTrue(any("society" in f for f in failures))

    def test_a_class_the_corpus_disagrees_with_fails(self):
        failures = gc.check([row(cls="guideline")], {}, [doc()])
        self.assertTrue(any("class is 'guideline'" in f for f in failures))

    def test_the_same_file_twice_fails(self):
        failures = gc.check([row(), row()], {}, [doc()])
        self.assertTrue(any("more than one row" in f for f in failures))


class CheckShape(unittest.TestCase):
    def test_an_unsettled_cell_nobody_listed_fails(self):
        failures = gc.check_shape([row(population="?")], {})
        self.assertTrue(any("is not listed under" in f for f in failures))

    def test_an_unsettled_cell_that_is_listed_passes(self):
        self.assertEqual(
            gc.check_shape([row(population="?")], {"copd-screening.pdf": {"population"}}), []
        )

    def test_a_listing_for_a_cell_the_table_fills_fails(self):
        failures = gc.check_shape([row()], {"copd-screening.pdf": {"population"}})
        self.assertTrue(any("but the table fills it" in f for f in failures))

    def test_a_listing_for_a_file_with_no_row_fails(self):
        failures = gc.check_shape([row()], {"gone.pdf": {"population"}})
        self.assertTrue(any("with no table row" in f for f in failures))

    def test_an_unknown_class_fails(self):
        failures = gc.check_shape([row(cls="review")], {})
        self.assertTrue(any("is not one of" in f for f in failures))

    def test_a_year_that_is_not_a_year_fails(self):
        failures = gc.check_shape([row(year="2022a")], {})
        self.assertTrue(any("not a 4-digit year" in f for f in failures))

    def test_a_column_that_may_not_be_unsettled_fails(self):
        failures = gc.check_shape([row(society="?")], {"copd-screening.pdf": {"society"}})
        self.assertTrue(any("society may not be ?" in f for f in failures))

    def test_an_empty_cell_fails(self):
        failures = gc.check_shape([row(topic="")], {})
        self.assertTrue(any("topic is empty" in f for f in failures))


class Rendering(unittest.TestCase):
    def test_a_rendered_table_parses_back_to_the_same_rows(self):
        original = [row(), row(filename="other.pdf", title="Adults | Vaccines | CDC")]
        text = "# x\n\n" + gc.render_table(original) + "\n"
        parsed, _, problems = gc.parse_catalog(text)
        self.assertEqual(problems, [])
        self.assertEqual(parsed, original)


if __name__ == "__main__":
    unittest.main()
