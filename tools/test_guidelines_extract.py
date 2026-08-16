"""Tests for the guideline PDF text extractor.

phi-scan: synthetic

The pragma is above because ``DocumentClass`` pins the browser print timestamp
that tells an ACIP print-to-PDF capture apart from a guideline, and a timestamp
classifier cannot be tested without a timestamp-shaped literal. It is an artifact
of a public CDC page and no patient is near it, but the shape layer cannot know
that. Exempting the literal by writing it in pieces would dodge the scanner
without declaring anything, which is worse than saying so here. The corpus layer
is untouched by this and still applies.

These run against the committed ``.txt`` page excerpts in ``tools/testdata/`` and
never against ``C:/codeing/guidelines-src``, the same way ``test_icd10.py`` runs
against release excerpts and never against the shipped database. No PDF is read
here and none is committed -- ``*.pdf`` is globally gitignored and stays that way.

The excerpts are page text, not PDFs, which is the whole reason the module is cut
where it is: everything that decides what the output says is a function over a
list of page strings, and only ``extract_pages`` touches ``pypdf``. A test that
had to open a PDF could not be committed at all.

Two claims carry the most weight here:

- ``NormalizeText`` pins the en dash. ``130-139 mm Hg`` is a threshold, and issue
  #80 exists because a mangled dash in that string is not cosmetic.
- ``BoilerplateIsFoundAndRecorded`` pins the ``Downloaded from`` line, which is on
  nearly every page of all 23 AHA/ACC files and sits in the page's reading order
  rather than off in a margin, so it can land between a table row's label and its
  number.
"""

from __future__ import annotations

import json
import tempfile
import unicodedata
import unittest
from pathlib import Path

import guidelines_extract as extract
import guidelines_index as index

TESTDATA = Path(__file__).resolve().parent / "testdata"


def load_excerpt(name: str) -> list[str]:
    """The pages of a committed excerpt file, with its comment header dropped.

    Leading ``#`` lines are the header. They exist so a fixture can say where it
    came from and, in the ACIP case, declare the ``phi-scan`` pragma without that
    line becoming page one.
    """
    # Split on "\n" and not with splitlines(), which treats a form feed as a line
    # break and would swallow the page separator this file is built around.
    lines = (TESTDATA / name).read_text(encoding="utf-8").split("\n")
    body = lines
    for index, line in enumerate(lines):
        if not line.startswith("#"):
            body = lines[index:]
            break
    return [page.strip("\n") for page in "\n".join(body).strip("\n").split("\f")]


AHA = load_excerpt("guidelines_ahaacc_pages.txt")
ACIP = load_excerpt("guidelines_acip_pages.txt")

DOWNLOADED = "Downloaded from http://ahajournals.org by on August 12, 2026"
RUNNING_HEAD = "CLINICAL STATEMENTS AND GUIDELINES"


class ExcerptsAreWhatTheTestsThinkTheyAre(unittest.TestCase):
    """A silently reshaped fixture makes every assertion below vacuous."""

    def test_the_excerpts_hold_four_pages_each(self):
        self.assertEqual(len(AHA), 4)
        self.assertEqual(len(ACIP), 4)

    def test_the_acip_excerpt_keeps_the_stamp_on_a_line_of_its_own(self):
        # The shape is the test, and this assertion has now been written both ways.
        #
        # It required the stamp welded to the title, because pypdf produces that and
        # a fixture with the stamp alone let the classifier pass while finding zero
        # print-captures in all 179 documents. #83 moved the extractor to PyMuPDF,
        # which puts the four header parts on four lines, so the welded form is now
        # the one no real file produces and the shapes have swapped places.
        #
        # Checked against ACIP/Recommended Vaccinations for Adults ... CDC.pdf on
        # 2026-08-16. The lesson from the first round is that reasoning about what an
        # extractor emits is not a substitute for running it, so the fixture was
        # rebuilt from the real file rather than edited into the shape expected.
        lines = [line for page in ACIP for line in page.split("\n")]
        stamps = [line for line in lines if line.startswith("8/12/26,")]
        self.assertEqual(len(stamps), len(ACIP))
        for line in stamps:
            # Exactly the stamp, nothing welded on. The title is its own line, and
            # that is the whole difference this test exists to hold.
            self.assertEqual(line, "8/12/26, 10:25 AM")
        self.assertEqual(sum(1 for line in lines if line.endswith("| CDC")), len(ACIP))

    def test_the_acip_excerpt_repeats_three_header_lines_not_one(self):
        # The corpus consequence of the shape change, pinned so it cannot regress
        # quietly: under pypdf a capture contributed one page-repeated line, under
        # PyMuPDF it contributes three. The folio is deliberately not among them --
        # it differs per page, which is #100's subject rather than this fixture's.
        boilerplate = extract.find_boilerplate(extract.clean_pages(ACIP))
        self.assertEqual(len(boilerplate), 3)
        self.assertIn("8/12/26, 10:25 AM", boilerplate)
        self.assertTrue(any(line.endswith("| CDC") for line in boilerplate))
        self.assertTrue(any(line.startswith("https://") for line in boilerplate))
        self.assertFalse(any(line.strip().endswith("/4") for line in boilerplate))

    def test_the_aha_excerpt_still_carries_the_raw_quirks(self):
        joined = "\n".join(AHA)
        self.assertIn("\x08", joined)  # backspace after the issue date
        self.assertIn("\u00ad", joined)  # soft hyphen
        self.assertIn("\u2013", joined)  # en dash, in a threshold range
        self.assertIn("\uf17b", joined)  # private-use icon glyph
        self.assertIn("\ufb01", joined)  # fi ligature


def rawline(text: str, size: float, gaps: list[float]) -> dict:
    """A PyMuPDF ``rawdict`` page holding one line, laid out to a gap pattern.

    ``gaps[i]`` is the horizontal space between character ``i`` and ``i+1``, in
    points, which is the only geometry ``rebuild_text`` reads. Every glyph is given
    the same advance, so the gaps are the whole variable.

    Built as a literal rather than read from a PDF, on this file's standing rule:
    ``*.pdf`` is globally gitignored and the corpus is 179 copyrighted documents
    outside the repo, so a test that opened one could not run on a fresh clone.
    """
    advance = size * 0.5
    chars, cursor = [], 0.0
    for index, glyph in enumerate(text):
        chars.append({"c": glyph, "bbox": (cursor, 0.0, cursor + advance, size)})
        cursor += advance + (gaps[index] if index < len(gaps) else 0.0)
    return {"blocks": [{"type": 0, "lines": [{"spans": [{"size": size, "chars": chars}]}]}]}


class RebuildText(unittest.TestCase):
    """The space reconstruction #83 rests on, and the reason the reader changed.

    Both cases below are **real geometry**, measured off the corpus on 2026-08-16
    and written down here so the rule cannot drift away from what it was built for.
    They are the two lines the algorithm has to tell apart, and an absolute
    threshold cannot: in tracked type every gap is wide, so the word break is an
    outlier *within the line's own distribution* rather than a large number.
    """

    # USPSTF/hypertension-screening-adults-final-rec-statement.pdf p.4, 8.48 pt:
    # gaps inside a word measure -0.036 and the word boundary measures 1.145.
    GLUED_SIZE = 8.48
    GLUED_INSIDE = -0.036
    GLUED_BOUNDARY = 1.145

    # KDIGO/KDIGO-2024-CKD-Guideline.pdf p.3, 10.959 pt: the section header
    # `contents`, letter-spaced, every gap 1.475 and a spread of exactly zero.
    TRACKED_SIZE = 10.959
    TRACKED_GAP = 1.475

    def test_a_glued_run_is_split_at_its_word_boundary(self):
        text = "Behavioralcounseling"
        gaps = [self.GLUED_INSIDE] * len(text)
        gaps[len("Behavioral") - 1] = self.GLUED_BOUNDARY
        self.assertEqual(
            extract.rebuild_text(rawline(text, self.GLUED_SIZE, gaps)),
            "Behavioral counseling",
        )

    def test_letter_spaced_display_type_is_left_alone(self):
        """`contents` must not become `c o n t e n t s`.

        This is the case the absolute threshold got wrong, and it is why the rule
        measures a gap against its line rather than against the font size: 1.475 pt
        clears 0.10 x 10.959 outright, so every gap in the word was a word break.
        """
        text = "contents"
        gaps = [self.TRACKED_GAP] * len(text)
        self.assertEqual(
            extract.rebuild_text(rawline(text, self.TRACKED_SIZE, gaps)),
            "contents",
        )

    def test_a_tracked_line_still_splits_where_it_is_tracked_wider_still(self):
        """The baseline shifts the bar, it does not remove it. A tracked heading of
        two words has a gap wider than its own tracking, and that is still a space
        -- otherwise the rule would trade one failure for the other."""
        text = "contentshere"
        gaps = [self.TRACKED_GAP] * len(text)
        gaps[len("contents") - 1] = self.TRACKED_GAP + self.TRACKED_SIZE * 0.5
        self.assertEqual(
            extract.rebuild_text(rawline(text, self.TRACKED_SIZE, gaps)),
            "contents here",
        )

    def test_a_short_line_falls_back_to_the_absolute_rule(self):
        """Below MINIMUM_GAPS_FOR_BASELINE a median is the gap itself, which would
        make every excess zero and suppress every split. A two-word line is exactly
        where a lost space cannot be recovered from context, so the rule degrades to
        the absolute one rather than to silence."""
        self.assertLess(3, extract.MINIMUM_GAPS_FOR_BASELINE + 1)
        self.assertEqual(
            extract.rebuild_text(rawline("ab", self.GLUED_SIZE, [self.GLUED_BOUNDARY])),
            "a b",
        )

    def test_a_space_the_pdf_already_set_is_not_doubled(self):
        """Most of AHA/ACC sets real space glyphs AND wide inter-word gaps. Without
        the guard the output is double-spaced, and `normalize` collapsing runs of
        spaces would hide that rather than make it correct."""
        text = "one two"
        gaps = [self.GLUED_INSIDE] * len(text)
        gaps[len("one") - 1] = self.GLUED_BOUNDARY
        gaps[len("one")] = self.GLUED_BOUNDARY
        self.assertEqual(extract.rebuild_text(rawline(text, self.GLUED_SIZE, gaps)), "one two")

    def test_an_image_block_contributes_no_line(self):
        self.assertEqual(extract.rebuild_text({"blocks": [{"type": 1}]}), "")

    def test_an_empty_dictionary_is_not_an_error(self):
        self.assertEqual(extract.rebuild_text({}), "")


class SpansDoNotShareMetrics(unittest.TestCase):
    """The bug a rendered page found and no text metric did.

    KDIGO-2009-Transplant-Recipient-Guideline-English.pdf's running footer is one
    line of three spans, all Univers-Light 9 pt. The first is set with negative
    tracking and measures -1.38 pt between glyphs; the last is set normally and
    measures 0.00. Taking one median across the line gives -1.38, so every 0.00 gap
    in the last span reads as an excess of +1.38 against a 0.90 threshold, and the
    rebuild split every character of it:

        American Journal of Transplantation 2 0 0 9 ; 9 ( S u p p l 3 ) : S i - S i

    That one footer repeats on 158 pages and was the single largest source of
    damage in the corpus. The geometry below is the real line's.
    """

    TIGHT, NORMAL, SIZE = -1.38, 0.0, 9.0

    def line(self, first: str, second: str) -> dict:
        def chars(text, gap, start):
            advance = self.SIZE * 0.5
            out, cursor = [], start
            for glyph in text:
                out.append({"c": glyph, "bbox": (cursor, 0.0, cursor + advance, self.SIZE)})
                cursor += advance + gap
            return out, cursor

        left, cursor = chars(first, self.TIGHT, 0.0)
        right, _ = chars(second, self.NORMAL, cursor)
        return {
            "blocks": [{"type": 0, "lines": [{"spans": [
                {"size": self.SIZE, "chars": left},
                {"size": self.SIZE, "chars": right},
            ]}]}]
        }

    def test_a_normally_set_span_is_not_split_by_a_tightly_set_neighbour(self):
        page = self.line("AmericanJournalofTransplantation", "2009;9(Suppl3)")
        self.assertEqual(
            extract.rebuild_text(page), "AmericanJournalofTransplantation2009;9(Suppl3)"
        )

    def test_the_line_median_alone_would_have_split_it(self):
        """The counterfactual, so the test fails for the right reason. Against the
        whole line the baseline is the tight span's, and the normal span's every gap
        clears the bar."""
        page = self.line("AmericanJournalofTransplantation", "2009;9(Suppl3)")
        glyphs = [
            (char, self.SIZE)
            for span in page["blocks"][0]["lines"][0]["spans"]
            for char in span["chars"]
        ]
        whole_line = extract.line_baseline(glyphs)
        self.assertAlmostEqual(whole_line, self.TIGHT, places=6)
        self.assertGreater(
            self.NORMAL - whole_line,
            max(extract.SPACE_GAP_FRACTION * self.SIZE, extract.SPACE_GAP_FLOOR),
        )

    def test_a_span_too_short_for_its_own_median_borrows_the_line(self):
        """Right where a line is one typeface broken into spans by a bold word: the
        short span has no distribution of its own to measure."""
        page = self.line("aaaaaaaaaa", "bb")
        baselines = extract.span_baselines(page["blocks"][0]["lines"][0])
        self.assertAlmostEqual(baselines[0], self.TIGHT, places=6)
        self.assertAlmostEqual(baselines[1], baselines[0], places=6)


class LineBaseline(unittest.TestCase):
    def test_it_is_the_median_gap(self):
        page = rawline("abcdef", 10.0, [1.0, 1.0, 5.0, 1.0, 1.0])
        glyphs = [
            (char, 10.0)
            for char in page["blocks"][0]["lines"][0]["spans"][0]["chars"]
        ]
        self.assertAlmostEqual(extract.line_baseline(glyphs), 1.0, places=6)

    def test_too_few_gaps_returns_zero_rather_than_a_guess(self):
        page = rawline("ab", 10.0, [1.0])
        glyphs = [
            (char, 10.0)
            for char in page["blocks"][0]["lines"][0]["spans"][0]["chars"]
        ]
        self.assertEqual(extract.line_baseline(glyphs), 0.0)


class NormalizeText(unittest.TestCase):
    def test_an_en_dash_range_becomes_an_ascii_range(self):
        # The reason this ticket exists. A DOI with a mangled dash is cosmetic;
        # a threshold with one is a number the clinician cannot read back.
        self.assertEqual(
            extract.normalize("Stage 1 hypertension 130\u2013139 mm Hg"),
            "Stage 1 hypertension 130-139 mm Hg",
        )

    def test_every_dash_variant_lands_on_the_same_character(self):
        # Six characters render as a dash in these PDFs. A search for one range
        # must not depend on which one the typesetter reached for.
        for dash in "\u2010\u2011\u2012\u2013\u2014\u2212":
            self.assertEqual(extract.normalize(f"130{dash}139"), "130-139")

    def test_drops_the_control_characters_the_extractor_emits(self):
        self.assertEqual(extract.normalize("April 28, 2026\x08"), "April 28, 2026")

    def test_drops_a_private_use_glyph_rather_than_keeping_the_icon(self):
        # U+F17B and friends are icon-font code points. They carry no text and
        # would otherwise ride into the index as if they did.
        self.assertEqual(extract.normalize("readings\uf17b"), "readings")

    def test_joins_a_word_split_by_a_soft_hyphen(self):
        # A soft hyphen is invisible on the page, so "hyper\xadtension" reads as
        # one word and has to be indexed as one.
        self.assertEqual(extract.normalize("hyper\u00adtension"), "hypertension")

    def test_expands_a_ligature_into_its_letters(self):
        self.assertEqual(extract.normalize("con\ufb01rmed"), "confirmed")

    def test_collapses_the_typographic_spaces_into_plain_ones(self):
        for space in "\u00a0\u2002\u2003\u2009\u202f\u205f":
            self.assertEqual(extract.normalize(f"Stage 1{space}130-139"), "Stage 1 130-139")

    def test_keeps_the_comparison_operators_a_threshold_is_written_with(self):
        # These are not typographic noise, they are the recommendation. Mapping
        # them to anything would be the same defect the dash rule exists for.
        self.assertEqual(extract.normalize("\u2265140/\u226490 mm Hg"), "\u2265140/\u226490 mm Hg")

    def test_keeps_the_units_a_lab_value_is_written_with(self):
        self.assertEqual(extract.normalize("37.5 \u00b0C, 5 \u00b5g, 12 \u00b1 2"), "37.5 \u00b0C, 5 \u00b5g, 12 \u00b1 2")


class NormalizationTablesHoldWhatTheyClaim(unittest.TestCase):
    """The tables are bare code points, so a typo'd hex digit is invisible.

    It also lands on some real character and quietly rewrites it everywhere in the
    corpus. Checking each table by Unicode category catches that; restating the
    numbers here would only assert that a copy-paste succeeded.
    """

    def test_every_entry_in_the_dash_table_is_a_dash(self):
        for code in extract._DASHES:
            with self.subTest(code=f"U+{code:04X}"):
                name = unicodedata.name(chr(code))
                self.assertTrue(
                    any(word in name for word in ("HYPHEN", "DASH", "MINUS", "BAR")), name
                )

    def test_every_entry_in_the_space_table_is_a_space_separator(self):
        for code in extract._SPACES:
            with self.subTest(code=f"U+{code:04X}"):
                self.assertEqual(unicodedata.category(chr(code)), "Zs")

    def test_every_entry_in_the_deleted_table_is_a_format_character(self):
        # Category Cf: it has no width and no meaning in extracted text. Anything
        # else in this table is a character being deleted rather than normalized.
        for code in extract._DELETED:
            with self.subTest(code=f"U+{code:04X}"):
                self.assertEqual(unicodedata.category(chr(code)), "Cf")

    def test_every_entry_in_the_ligature_table_is_a_ligature(self):
        for code in extract._LIGATURES:
            with self.subTest(code=f"U+{code:04X}"):
                self.assertIn("LIGATURE", unicodedata.name(chr(code)))

    def test_every_entry_in_the_quote_table_is_a_quote_or_a_prime(self):
        for code in extract._QUOTES:
            with self.subTest(code=f"U+{code:04X}"):
                name = unicodedata.name(chr(code))
                self.assertTrue(("QUOTATION MARK" in name) or ("PRIME" in name), name)

    def test_no_character_is_claimed_by_two_tables(self):
        tables = (extract._DASHES, extract._SPACES, extract._DELETED,
                  tuple(extract._LIGATURES), tuple(extract._QUOTES))
        seen: set[int] = set()
        for table in tables:
            self.assertFalse(seen & set(table), sorted(seen & set(table)))
            seen |= set(table)

    def test_nothing_a_threshold_is_written_with_is_in_any_table(self):
        # The tables are the blast radius. A clinical operator or unit landing in
        # one of them changes every number in the corpus that uses it.
        clinical = "≥≤°µμ±×÷⁄/%.,"
        clinical += "0123456789<>=()[]-"
        for character in clinical:
            with self.subTest(character=f"U+{ord(character):04X}"):
                self.assertNotIn(ord(character), extract._TRANSLATION)
                self.assertEqual(extract.normalize(f"a{character}b"), f"a{character}b")

    def test_the_newline_survives_the_discarded_ranges(self):
        # page_lines splits on it. Discarding it would make every page one line.
        for low, high in extract._DISCARDED_RANGES:
            self.assertFalse(low <= 0x0A <= high, f"U+{low:04X}-U+{high:04X}")


class PageLines(unittest.TestCase):
    def test_normalizes_and_collapses_each_line(self):
        self.assertEqual(
            extract.page_lines("  a\u2003b  \n\n\tc\u00add  \n"), ["a b", "cd"]
        )

    def test_drops_a_line_that_is_only_whitespace(self):
        # A blank line matches every other blank line, so leaving them in makes
        # "" the most frequent line in every document and boilerplate in all of them.
        self.assertEqual(extract.page_lines("a\n \n\u2002\nb"), ["a", "b"])

    def test_an_empty_page_yields_no_lines(self):
        self.assertEqual(extract.page_lines(""), [])


class SampleIndexes(unittest.TestCase):
    def test_a_short_document_is_sampled_whole(self):
        self.assertEqual(extract.sample_indexes(4), [0, 1, 2, 3])

    def test_a_document_at_the_sample_size_is_still_sampled_whole(self):
        self.assertEqual(len(extract.sample_indexes(extract.SAMPLE_SIZE)), extract.SAMPLE_SIZE)

    def test_a_long_document_is_sampled_evenly_and_not_off_the_front(self):
        # Front matter and back matter do not carry the running head. A sample
        # taken from the first pages would conclude there is no boilerplate.
        indexes = extract.sample_indexes(400)
        self.assertEqual(len(indexes), extract.SAMPLE_SIZE)
        self.assertEqual(indexes, sorted(set(indexes)))
        self.assertLess(max(indexes), 400)
        self.assertGreater(max(indexes), 300)

    def test_the_sample_size_cannot_be_turned_below_the_ticket_floor(self):
        # #80 asks for at least 8 sampled pages. SAMPLE_SIZE is the knob someone
        # would actually reach for, so what needs pinning is that turning it down
        # cannot take the tool under the floor -- not that 32 is bigger than 8.
        self.assertGreaterEqual(extract.SAMPLE_SIZE, extract.MINIMUM_SAMPLE)
        self.assertGreaterEqual(len(extract.sample_indexes(1000)), extract.MINIMUM_SAMPLE)

    def test_a_single_page_document_samples_that_page(self):
        self.assertEqual(extract.sample_indexes(1), [0])


class BoilerplateIsFoundAndRecorded(unittest.TestCase):
    def setUp(self):
        self.pages = extract.clean_pages(AHA)
        self.boilerplate = extract.find_boilerplate(self.pages)

    def test_finds_the_downloaded_from_line(self):
        # Issue #80's explicit done-when. All 23 AHA/ACC files carry it.
        self.assertIn(DOWNLOADED, self.boilerplate)

    def test_a_line_on_exactly_three_quarters_of_pages_is_boilerplate(self):
        # The running head is on 3 of the 4 excerpt pages; the cover page has
        # none. 75% is the rule's boundary and it is inclusive.
        self.assertIn(RUNNING_HEAD, self.boilerplate)

    def test_a_running_head_carrying_its_page_number_is_left_alone(self):
        # These differ page to page, so the rule does not reach them. Stated as
        # a test because it is a known limit, not an oversight: the alternative
        # is masking digits, which would also reach a repeated table row.
        self.assertFalse([line for line in self.boilerplate if "DOI:" in line])

    def test_a_line_appearing_once_is_not_boilerplate(self):
        self.assertNotIn("2026 Guideline on the Management of Blood Cholesterol", self.boilerplate)

    def test_a_threshold_row_survives_stripping(self):
        # The one thing this must never eat.
        kept = "\n".join("\n".join(page) for page in extract.strip(self.pages, self.boilerplate))
        self.assertIn("Stage 1 hypertension 130-139 mm Hg systolic", kept)

    def test_stripping_removes_the_line_from_every_page(self):
        stripped = extract.strip(self.pages, self.boilerplate)
        self.assertFalse([page for page in stripped if DOWNLOADED in page])
        self.assertFalse([page for page in stripped if RUNNING_HEAD in page])

    def test_stripping_leaves_the_pages_in_place(self):
        # One text file per document, pages in order. A dropped page would
        # renumber every page after it against the source PDF.
        self.assertEqual(len(extract.strip(self.pages, self.boilerplate)), len(self.pages))

    def test_the_recorded_set_is_ordered_so_two_runs_agree(self):
        # The stripped set goes into a manifest that gets read and diffed. Set
        # iteration order would make every rebuild look like a change.
        self.assertEqual(self.boilerplate, sorted(self.boilerplate))


class BoilerplateDegenerateCases(unittest.TestCase):
    def test_a_one_page_document_has_no_boilerplate(self):
        # Every line of a single page appears on 100% of its pages. Without a
        # floor the rule strips the whole document and reports it as clean.
        pages = extract.clean_pages(["a\nb\nc"])
        self.assertEqual(extract.find_boilerplate(pages), [])

    def test_a_two_page_document_has_no_boilerplate(self):
        pages = extract.clean_pages(["head\nbody one", "head\nbody two"])
        self.assertEqual(extract.find_boilerplate(pages), [])

    def test_three_repeats_is_the_floor_and_it_is_inclusive(self):
        pages = extract.clean_pages(["head\none", "head\ntwo", "head\nthree"])
        self.assertEqual(extract.find_boilerplate(pages), ["head"])

    def test_a_document_with_no_pages_has_no_boilerplate(self):
        self.assertEqual(extract.find_boilerplate([]), [])

    def test_a_line_below_the_threshold_survives_however_often_it_repeats(self):
        # 3 of 5 is 60%. It clears the occurrence floor and fails the rule.
        pages = extract.clean_pages(["x\n1", "x\n2", "x\n3", "4", "5"])
        self.assertEqual(extract.find_boilerplate(pages), [])

    def test_a_line_repeated_within_one_page_counts_once(self):
        # Otherwise a two-column page whose column headers repeat reads as two
        # pages' worth of evidence for stripping them.
        pages = extract.clean_pages(["x\nx\nx\n1", "2", "3", "4"])
        self.assertEqual(extract.find_boilerplate(pages), [])


class DocumentClass(unittest.TestCase):
    @staticmethod
    def every_page_carries(line, count=4):
        return [["body text", line] for _ in range(count)]

    def test_the_acip_captures_are_not_read_as_guidelines(self):
        # The three ACIP/ files are browser print-to-PDF captures of CDC schedule
        # pages. Issue #80 asks for them flagged rather than parsed as guidelines.
        self.assertEqual(
            extract.classify(extract.clean_pages(ACIP)), extract.CLASS_PRINT_CAPTURE
        )

    def test_a_journal_pdf_is_a_guideline(self):
        self.assertEqual(
            extract.classify(extract.clean_pages(AHA)), extract.CLASS_GUIDELINE
        )

    def test_the_print_timestamp_is_what_says_so_and_not_the_url(self):
        # A guideline PDF can carry a repeated URL footer -- KDIGO does. Only the
        # browser's print timestamp is unambiguous.
        self.assertEqual(
            extract.classify(self.every_page_carries("https://www.cdc.gov/vaccines/index.html")),
            extract.CLASS_GUIDELINE,
        )
        self.assertEqual(
            extract.classify(self.every_page_carries("8/12/26, 10:25 AM")),
            extract.CLASS_PRINT_CAPTURE,
        )

    def test_the_stamp_is_recognized_with_the_page_title_folded_in_after_it(self):
        # This is the only form the real files take. Requiring the stamp to be
        # the whole line passed the fixture and found zero captures in 179 files.
        self.assertEqual(
            extract.classify(
                self.every_page_carries("8/12/26, 10:25 AM Recommended Vaccinations | CDC")
            ),
            extract.CLASS_PRINT_CAPTURE,
        )

    def test_a_date_and_time_part_way_through_a_line_is_prose(self):
        # Anchoring at the front is what keeps the rule from reading a guideline
        # that happens to repeat a dated footer as a browser capture.
        self.assertEqual(
            extract.classify(
                self.every_page_carries("Accessed 8/12/26, 10:25 AM from the society website")
            ),
            extract.CLASS_GUIDELINE,
        )

    def test_a_bare_date_with_no_time_is_not_a_print_stamp(self):
        self.assertEqual(
            extract.classify(self.every_page_carries("8/12/26 Recommended Vaccinations")),
            extract.CLASS_GUIDELINE,
        )

    def test_a_two_page_capture_is_still_a_capture(self):
        # The reason the class is counted over pages rather than read off the
        # boilerplate set: MINIMUM_OCCURRENCES refuses to call anything on a
        # 2-page document boilerplate, and the class must not ride on that.
        pages = self.every_page_carries("8/12/26, 10:25 AM Adult Schedule | CDC", count=2)
        self.assertEqual(extract.find_boilerplate(pages), [])
        self.assertEqual(extract.classify(pages), extract.CLASS_PRINT_CAPTURE)

    def test_a_stamp_on_one_page_of_many_is_not_a_capture(self):
        pages = [["body"], ["body"], ["body"], ["8/12/26, 10:25 AM Something | CDC"]]
        self.assertEqual(extract.classify(pages), extract.CLASS_GUIDELINE)

    def test_a_document_with_no_pages_at_all_is_a_guideline(self):
        self.assertEqual(extract.classify([]), extract.CLASS_GUIDELINE)


class OutputStaysOutOfTheRepo(unittest.TestCase):
    """Six worktrees are live. Anything written inside one is copied into all of them."""

    def test_the_default_output_is_a_sibling_of_the_source(self):
        self.assertEqual(
            extract.default_output(Path("C:/codeing/guidelines-src")),
            Path("C:/codeing/guidelines-text"),
        )

    def test_a_source_directory_not_named_src_still_gets_a_sibling(self):
        self.assertEqual(
            extract.default_output(Path("/data/guidelines")),
            Path("/data/guidelines-text"),
        )

    def test_refuses_an_output_directory_inside_the_repo(self):
        # The two #80 names by name, plus a path that does not exist yet.
        for inside in ("reference", "scratch", "tools/testdata", "guidelines-text"):
            with self.subTest(inside=inside):
                with self.assertRaises(SystemExit):
                    extract.check_outside_repo(extract.REPO_ROOT / inside)

    def test_refuses_the_repo_root_itself(self):
        with self.assertRaises(SystemExit):
            extract.check_outside_repo(extract.REPO_ROOT)

    def test_refuses_a_sibling_worktree_and_not_only_this_one(self):
        # Run from a worktree, REPO_ROOT is the worktree. It says nothing about
        # the main clone, whose reference/ is the directory #80 rules out.
        checkout = Path(tempfile.mkdtemp())
        (checkout / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            extract.check_outside_repo(checkout / "reference")

    def test_accepts_a_directory_under_no_checkout_at_all(self):
        extract.check_outside_repo(Path(tempfile.mkdtemp()) / "guidelines-text")


class WritingADocument(unittest.TestCase):
    """The half that touches disk, driven from page text so no PDF is needed."""

    def setUp(self):
        self.out = Path(tempfile.mkdtemp())

    def record(self, pages=AHA, name="AHA ACC/paper.pdf"):
        return extract.build_document(Path(name), pages, self.out)

    def test_writes_one_text_file_per_document(self):
        record = self.record()
        written = self.out / "AHA ACC" / "paper.txt"
        self.assertTrue(written.is_file())
        self.assertEqual(record.output, "AHA ACC/paper.txt")

    def test_the_doc_id_is_the_relative_path_with_the_suffix_dropped(self):
        # The key #84 matches a document by, and the reason the output file sits
        # at the source stem: a hit has to name a file openable beside its PDF.
        record = self.record()
        self.assertEqual(record.doc_id, "AHA ACC/paper")
        self.assertEqual(record.society, "AHA ACC")

    def test_a_document_at_the_root_has_no_society(self):
        # The society is the first path segment, so a file with no directory has
        # none. Reporting the stem as a society would invent one.
        self.assertIsNone(extract.society_of(extract.document_id(Path("loose.pdf"))))

    def test_the_title_is_carried_through_when_the_pdf_has_one(self):
        record = extract.build_document(
            Path("AHA ACC/paper.pdf"), AHA, self.out, "2026 Guideline on Blood Cholesterol"
        )
        self.assertEqual(record.title, "2026 Guideline on Blood Cholesterol")

    def test_a_document_with_no_embedded_title_records_none(self):
        self.assertIsNone(self.record().title)

    def test_the_written_file_reads_back_as_the_same_pages(self):
        self.record()
        text = (self.out / "AHA ACC" / "paper.txt").read_text(encoding="utf-8")
        self.assertEqual(len(text.split("\f")), 4)

    def test_the_written_file_is_utf8_and_says_so(self):
        # The codec is recorded because getting it wrong is exactly how the en
        # dash gets mangled: this text through a cp1252 stream either raises or
        # comes back as question marks.
        record = self.record()
        self.assertEqual(record.codec, "utf-8")
        raw = (self.out / "AHA ACC" / "paper.txt").read_bytes()
        self.assertIn("130-139".encode("utf-8"), raw)
        self.assertIn("\u2265140".encode("utf-8"), raw)

    def test_records_the_page_count_and_the_characters_extracted(self):
        record = self.record()
        self.assertEqual(record.pages, 4)
        self.assertGreater(record.chars, 0)

    def test_records_the_stripped_set_rather_than_only_the_count(self):
        # "Auditable rather than magic" is the requirement. A count would let a
        # rule that ate a table row look identical to one that ate a footer.
        record = self.record()
        self.assertIn(DOWNLOADED, record.boilerplate)
        self.assertGreater(record.chars_stripped, 0)

    def test_records_the_document_class(self):
        self.assertEqual(self.record().document_class, extract.CLASS_GUIDELINE)
        self.assertEqual(
            self.record(pages=ACIP, name="ACIP/adult.pdf").document_class,
            extract.CLASS_PRINT_CAPTURE,
        )

    def test_records_how_many_pages_came_back_empty(self):
        record = self.record(pages=["text", "", "  ", "more"])
        self.assertEqual(record.empty_pages, 2)

    def test_a_failure_is_recorded_and_writes_no_text_file(self):
        # "No silent skips." A document that could not be read has to be
        # distinguishable from one that read as empty.
        record = extract.failed_document(Path("IDSA/broken.pdf"), "PdfReadError: x")
        self.assertIsNotNone(record.error)
        self.assertIsNone(record.output)
        self.assertEqual(record.pages, 0)

    def test_a_document_that_was_never_read_has_no_class(self):
        # Not "guideline". Nobody knows what it is, and defaulting to the common
        # case lets a failure read as a finding when the manifest is counted.
        record = extract.failed_document(Path("IDSA/broken.pdf"), "PdfReadError: x")
        self.assertEqual(record.document_class, extract.CLASS_UNKNOWN)

    def test_a_stale_text_file_no_source_claims_is_reported(self):
        # A re-run overwrites and never deletes, so a renamed source leaves its
        # old output behind. #84 will index the directory, not the manifest.
        record = self.record()
        stale = self.out / "AHA ACC" / "renamed-last-time.txt"
        stale.write_text("old\n", encoding="utf-8")
        self.assertEqual(extract.orphaned_outputs(self.out, [record]), [stale])

    def test_nothing_is_orphaned_when_every_file_is_claimed(self):
        self.assertEqual(extract.orphaned_outputs(self.out, [self.record()]), [])

    def test_the_manifest_holds_one_entry_per_document_and_round_trips(self):
        records = [self.record(), extract.failed_document(Path("IDSA/b.pdf"), "boom")]
        extract.write_manifest(self.out, records, Path("C:/codeing/guidelines-src"))
        manifest = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["documents"]), 2)
        self.assertEqual(manifest["totals"]["documents"], 2)
        self.assertEqual(manifest["totals"]["failures"], 1)
        self.assertEqual(manifest["codec"], "utf-8")
        self.assertIn(DOWNLOADED, manifest["documents"][0]["boilerplate"])

    def test_a_failed_document_still_carries_a_doc_id(self):
        # #84 reports a manifest entry it found no text for on stderr and stays
        # green. That is this tool's recorded failure surfacing over there, and it
        # only works if the entry can be matched to a document at all.
        extract.write_manifest(
            self.out,
            [extract.failed_document(Path("IDSA/b.pdf"), "boom")],
            Path("C:/codeing/guidelines-src"),
        )
        manifest = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["documents"][0]["doc_id"], "IDSA/b")

    def test_the_manifest_names_the_corpus_it_was_built_from(self):
        # Same reasoning as the ICD-10 database's release string. A derived
        # artifact that cannot say what it came from cannot be audited.
        extract.write_manifest(self.out, [self.record()], Path("C:/codeing/guidelines-src"))
        manifest = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn("guidelines-src", manifest["source"])


class TheIndexerCanReadWhatThisWrites(unittest.TestCase):
    """#84 landed first and reads this output, so the contract is executable here.

    It is asserted on this side rather than only in ``test_guidelines.py`` because
    #80 owns the manifest's shape. Change it and these go red, which is the whole
    point: the first version of this writer emitted ``"documents": 179`` as a count,
    ``read_manifest`` does ``data.get("documents")`` and raises unless that is a
    list, and nothing in either test suite noticed.

    Deliberately not a full index build -- that needs a database and is
    ``test_guidelines.py``'s job. What is pinned here is the handoff.
    """

    def setUp(self):
        self.out = Path(tempfile.mkdtemp())
        self.records = [
            extract.build_document(Path("AHA ACC/paper.pdf"), AHA, self.out, "A Guideline"),
            extract.build_document(Path("ACIP/adult.pdf"), ACIP, self.out),
            extract.failed_document(Path("IDSA/broken.pdf"), "PdfReadError: x"),
        ]
        extract.write_manifest(self.out, self.records, Path("C:/codeing/guidelines-src"))
        self.documents = {doc.doc_id: doc for doc in index.discover(self.out)}

    def test_the_manifest_is_a_shape_the_indexer_accepts(self):
        self.assertIn("AHA ACC/paper", index.read_manifest(self.out))

    def test_every_document_written_is_a_document_found(self):
        written = {r.doc_id for r in self.records if r.output}
        self.assertEqual(set(self.documents), written)

    def test_the_society_the_title_and_the_class_survive_the_handoff(self):
        paper = self.documents["AHA ACC/paper"]
        self.assertEqual(paper.society, "AHA ACC")
        self.assertEqual(paper.title, "A Guideline")
        self.assertEqual(paper.document_class, extract.CLASS_GUIDELINE)

    def test_the_print_capture_stays_separable_on_the_other_side(self):
        # The single reason document_class is in the manifest at all: it is a
        # column on `document` and guidelines_search.py --class filters on it.
        self.assertEqual(
            self.documents["ACIP/adult"].document_class, extract.CLASS_PRINT_CAPTURE
        )

    def test_the_page_count_survives_the_form_feeds(self):
        self.assertEqual(len(self.documents["AHA ACC/paper"].pages), len(AHA))

    def test_a_page_that_extracted_to_nothing_keeps_its_number(self):
        # Dropping it would slide every later citation by one, and a citation off
        # by a page is worse than no citation.
        extract.build_document(Path("KDIGO/gappy.pdf"), ["one", "", "three"], self.out)
        extract.write_manifest(self.out, self.records, Path("C:/codeing/guidelines-src"))
        pages = {d.doc_id: d for d in index.discover(self.out)}["KDIGO/gappy"].pages
        self.assertEqual([page.number for page in pages], [1, 2, 3])
        self.assertIn("three", pages[2].text)

    def test_a_failure_is_named_by_the_manifest_and_has_no_text(self):
        # The indexer reports this on stderr and still exits 0 -- a build that
        # went red for one unextractable PDF would be red every run.
        self.assertIn("IDSA/broken", index.read_manifest(self.out))
        self.assertNotIn("IDSA/broken", self.documents)


if __name__ == "__main__":
    unittest.main()
