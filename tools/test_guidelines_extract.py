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
list of page strings, and only ``extract_pages`` touches PyMuPDF. A test that
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


def rawline(text: str, size: float, gaps: list[float], font: str | None = None) -> dict:
    """A PyMuPDF ``rawdict`` page holding one line, laid out to a gap pattern.

    ``gaps[i]`` is the horizontal space between character ``i`` and ``i+1``, in
    points, which is the only geometry ``rebuild_text`` reads. Every glyph is given
    the same advance, so the gaps are the whole variable.

    ``font`` names the span's typeface where a test is about the font rather than
    about the geometry, and is left off the span entirely otherwise -- a span with
    no ``font`` key is what a caller that does not care looks like, and the
    substitution table has to survive one.

    Built as a literal rather than read from a PDF, on this file's standing rule:
    ``*.pdf`` is globally gitignored and the corpus is 179 copyrighted documents
    outside the repo, so a test that opened one could not run on a fresh clone.
    """
    advance = size * 0.5
    chars, cursor = [], 0.0
    for index, glyph in enumerate(text):
        chars.append({"c": glyph, "bbox": (cursor, 0.0, cursor + advance, size)})
        cursor += advance + (gaps[index] if index < len(gaps) else 0.0)
    span = {"size": size, "chars": chars}
    if font is not None:
        span["font"] = font
    return {"blocks": [{"type": 0, "lines": [{"spans": [span]}]}]}


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

    def test_a_normally_set_span_is_not_split_by_a_tightly_set_neighbor(self):
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


class SymbolFontsThatLieAboutTheirOwnEncoding(unittest.TestCase):
    """#172: the character a threshold is written with is the character that breaks.

    Two fonts in the corpus render a comparison operator through a slot their own
    ``ToUnicode`` map does not describe, so both readers hand back something else.
    **Every row below was settled by rendering the page and looking at the glyph**,
    which is ``span_baselines``'s method and the only evidence there is -- the PDFs
    make no true statement about these characters anywhere. ``GMBEDM+AdvPS_SSYB``
    declares ``/Encoding /WinAnsiEncoding``, which is a text encoding on a symbol
    font; it ships no ``ToUnicode`` at all; and its embedded CFF subset names its
    two glyphs ``sterling`` and ``daggerdbl``. All three statements are wrong.

    Measured over all 179 documents, 2026-08-19 -- 256 operators across 12 files:

    ==========  ======  =====  ====  =====
    font        glyph   means     n   docs
    ==========  ======  =====  ====  =====
    AdvPS_SSYB  U+00A3     <=    71      9
    AdvPS_SSYB  U+2021     >=   146     11
    SymbolMT    U+001E     <=     2      1
    SymbolMT    U+001F     >=    36      1
    SymbolMT    U+F0B3     >=     1      1
    ==========  ======  =====  ====  =====

    **The ticket asked for a heuristic and the evidence retired it.** #172 proposed
    a unit-aware rule -- a pound sign, a number, a clinical unit -- and priced it at
    ~67 of 73. Keyed on the font instead the rule reads no text at all, and the two
    genuine currency figures in the corpus are untouched *by construction* rather
    than by a rule that mostly avoids them: both are set in an ordinary text face,
    one ``MinionPro-Regular`` and one ``Berkeley-Medium``, each beside a euro sign
    in a price list.

    **The ticket was also understated threefold, and by looking at the wrong
    character.** It records the greater-or-equal side as clean on ``0 occurrences of
    the 0xB3 slot``, which is true; ``>=`` did not land on 0xB3. It landed on a
    double dagger 146 times, on two C0 control codes 38 times, and on 0xB3 once but
    in the *private use area*, which the ticket's scan could not have seen. So the
    unit-aware rule would have reached none of the 183 ``>=``.

    **39 of the 256 are worse than mangled -- they are deleted.** U+001E, U+001F and
    U+F0B3 all fall inside ``_DISCARDED_RANGES``, so today
    ``COPD and FEV1 <=50% predicted`` reaches the corpus as
    ``COPD and FEV1 50% predicted``: a threshold flattened into an equality, with
    no character left behind to notice it by.
    """

    def test_the_pound_sign_that_is_a_less_or_equal_becomes_one(self):
        self.assertEqual(
            extract.rebuild_text(rawline("\u00a3120", 9.0, [0.0] * 4, font="AdvPS_SSYB")),
            "\u2264120",
        )

    def test_the_double_dagger_that_is_a_greater_or_equal_becomes_one(self):
        """The 146 the ticket's own rule could not have reached. ``for >=6 months``
        and ``a >=40% decline in eGFR`` read as footnote markers to every text
        heuristic, and as prices to none of them."""
        self.assertEqual(
            extract.rebuild_text(rawline("\u20216", 9.0, [0.0] * 2, font="AdvPS_SSYB")),
            "\u22656",
        )

    def test_the_control_codes_normalize_would_have_deleted_become_operators(self):
        """These are the dangerous 38. Left alone they do not survive to be wrong:
        ``_DISCARDED_RANGES`` removes them and the threshold reads as an equality,
        so the second assertion is the one that matters."""
        for glyph, operator in (("\u001e", "\u2264"), ("\u001f", "\u2265")):
            with self.subTest(glyph=glyph):
                rebuilt = extract.rebuild_text(
                    rawline(glyph + "50", 9.0, [0.0] * 3, font="SymbolMT")
                )
                self.assertEqual(rebuilt, operator + "50")
                self.assertEqual(extract.normalize(rebuilt), operator + "50")

    def test_the_private_use_slot_that_is_a_greater_or_equal_becomes_one(self):
        """U+F0B3 is the Symbol font's own 0xB3 surfacing unmapped. It is the slot
        #172 went looking for, in the one place that ticket's scan could not see."""
        self.assertEqual(
            extract.rebuild_text(rawline("\uf0b34", 9.0, [0.0] * 3, font="SymbolMT")),
            "\u22654",
        )

    def test_a_pound_sign_in_an_ordinary_text_face_is_left_alone(self):
        """The corpus's two real currency figures, and the whole reason the rule is
        keyed on the font rather than on what follows the character."""
        for face in ("MinionPro-Regular", "Berkeley-Medium"):
            with self.subTest(font=face):
                self.assertEqual(
                    extract.rebuild_text(rawline("\u00a31272", 9.0, [0.0] * 5, font=face)),
                    "\u00a31272",
                )

    def test_a_double_dagger_in_an_ordinary_text_face_is_left_alone(self):
        """787 double daggers are in the corpus and 146 of them are this defect.
        The rest are footnote markers in AHA/ACC tables, and turning one into a
        ``>=`` would invent a threshold rather than recover one."""
        self.assertEqual(
            extract.rebuild_text(
                rawline("\u2021 p<0.05", 9.0, [0.0] * 8, font="TimesNewRomanPSMT")
            ),
            "\u2021 p<0.05",
        )

    def test_a_span_naming_no_font_is_not_an_error(self):
        """Most spans built in this file carry no ``font`` key at all, and a table
        lookup on a missing name has to come back empty rather than raise."""
        self.assertEqual(
            extract.rebuild_text(rawline("\u00a3120", 9.0, [0.0] * 4)), "\u00a3120"
        )

    def test_a_subset_prefix_does_not_hide_the_font(self):
        """PyMuPDF strips the six-letter subset tag before it reaches ``rawdict``,
        so the corpus never exercises this -- but the tag is in the PDF's own font
        dictionary (``GMBEDM+AdvPS_SSYB``), one call away, and a reader who reached
        for the name there would get one the table does not hold."""
        self.assertEqual(
            extract.rebuild_text(
                rawline("\u00a3120", 9.0, [0.0] * 4, font="GMBEDM+AdvPS_SSYB")
            ),
            "\u2264120",
        )

    def test_a_lowercase_word_before_the_plus_is_not_a_subset_tag(self):
        """A subset tag is exactly six uppercase letters. Stripping on the plus
        alone would map a font nobody measured."""
        self.assertEqual(extract.font_key("abcdef+AdvPS_SSYB"), "abcdef+AdvPS_SSYB")
        self.assertEqual(extract.font_key("GMBEDM+AdvPS_SSYB"), "AdvPS_SSYB")

    def test_the_substitution_does_not_disturb_the_space_reconstruction(self):
        """``rebuild_text``'s own rule reads geometry, and the substitution is 1:1
        and happens after the gap is measured. A replaced glyph must still take the
        space in front of it that the gap calls for."""
        text = "a\u00a3120"
        gaps = [0.0] * len(text)
        gaps[0] = 5.0
        self.assertEqual(
            extract.rebuild_text(rawline(text, 9.0, gaps, font="AdvPS_SSYB")),
            "a \u2264120",
        )


class TheSubstitutionTableHoldsWhatItClaims(unittest.TestCase):
    """The table is a set of measurements, so its shape is asserted rather than
    trusted -- ``NormalizationTablesHoldWhatTheyClaim``'s arrangement, for its
    reason. Nothing here re-derives a *count*: the corpus is 179 copyrighted PDFs
    outside the repo and no test in this file opens one.
    """

    def test_every_replacement_is_a_comparison_operator(self):
        """What the table may claim is narrow. #172 is about the character a threshold
        is written with, and a row producing anything else is a different ruling --
        it has to be argued for rather than appended."""
        for font, mapping in extract.SYMBOL_FONT_OPERATORS.items():
            for glyph, replacement in mapping.items():
                with self.subTest(font=font, glyph=glyph):
                    self.assertIn(replacement, ("\u2264", "\u2265"))

    def test_no_source_glyph_is_a_letter_or_a_digit(self):
        """``SymbolMT`` also renders ``n`` as an up arrow and ``p`` as a down arrow,
        in one KDIGO figure. Those are deliberately **not** here: mapping a letter
        means a font name that is ever wrong corrupts prose rather than one symbol,
        and an arrow is not what a threshold is written with."""
        for font, mapping in extract.SYMBOL_FONT_OPERATORS.items():
            for glyph in mapping:
                with self.subTest(font=font, glyph=glyph):
                    self.assertFalse(glyph.isalnum(), f"{font} maps {glyph!r}")

    def test_nothing_a_correct_font_emits_is_mapped(self):
        """``SymbolMT`` gets ``<=`` and ``>=`` right 2,078 times in this same
        corpus under this same font name, in other documents. So the table may only
        claim slots that are wrong *everywhere*: a mapping keyed on a character the
        font also emits correctly would rewrite a correct one somewhere."""
        for font, mapping in extract.SYMBOL_FONT_OPERATORS.items():
            for glyph in mapping:
                with self.subTest(font=font, glyph=glyph):
                    self.assertNotIn(glyph, ("\u2264", "\u2265", "<", ">", "="))

    def test_the_font_names_carry_no_subset_prefix(self):
        """A key with a tag on it matches one document's subset and no other's."""
        for font in extract.SYMBOL_FONT_OPERATORS:
            with self.subTest(font=font):
                self.assertEqual(extract.font_key(font), font)

    def test_the_font_that_proves_a_font_name_is_not_always_a_verdict_stays_out(self):
        """``MathematicalPi-One`` is the reason this table has a rule and not just
        rows, and it is the closest this repo has come to shipping an inverted
        threshold.

        It sets comparison operators in two C0 slots that ``_DISCARDED_RANGES``
        deletes -- the same class as ``SymbolMT``'s, in USPSTF, which is 90 of the
        179 documents. Every instinct says add two rows. **Rendered, the two slots
        are exactly inverted between two documents of the same society**:

            abdom-aortic-aneurysm-screening-final-rs   U+0002 = >=   U+0003 = <=
            osteoporosis-screening-final-recommendation U+0002 = <=   U+0003 = >=

        Measured at 700 dpi, 2026-08-19, after four samples at 400 dpi had agreed
        with each other and the fifth did not. Confirmed a second way, by hashing
        the rasterized glyph box of every occurrence: no shape appears under both
        of ``AdvPS_SSYB``'s codes, and **four shapes appear under both of
        ``MathematicalPi-One``'s**. That instrument cannot prove two glyphs are the
        same -- it hashes a rendering, so point size moves it -- but one shape
        under two codes is a difference noise cannot manufacture, and that is the
        only direction it was read in. A font-name-keyed row would
        therefore have turned ``>=90% of screen-detected AAAs`` into ``<=90%`` --
        **inverting a clinical threshold rather than losing one**, which is worse
        than the defect #172 was filed about and is the one outcome no downstream
        gate could catch, because the result is a well-formed operator.

        So the rule the table states is load-bearing rather than decorative: *a row
        may only claim a slot that is wrong everywhere*. A subsetted font reassigns
        its codes per document, and a font **name** is a verdict about a slot only
        where the outline behind it does not move. Settling that needs the embedded
        glyph outline or a rendered page, and neither is in this repo -- so this is
        a test that names the font and refuses it, and the census is what keeps it
        visible. Filed rather than folded in.
        """
        self.assertNotIn("MathematicalPi-One", extract.SYMBOL_FONT_OPERATORS)
        self.assertTrue(
            extract.is_symbol_font("MathematicalPi-One"),
            "the census must keep reporting it, or refusing to map it hides it",
        )
        self.assertEqual(
            extract.symbol_glyph_census(
                rawline("90", 9.0, [0.0] * 4, font="MathematicalPi-One")
            ),
            {"MathematicalPi-One U+0002": 1, "MathematicalPi-One U+0003": 1,
             "MathematicalPi-One U+0039": 1, "MathematicalPi-One U+0030": 1},
        )


class TheCensusThatStopsThisRecurringInSilence(unittest.TestCase):
    """``symbol_glyph_census`` -- the half of #172 that is not the substitution.

    The substitution fixes five slots somebody went and looked at. The defect it
    cannot fix is the next corpus refresh bringing a symbol font nobody has looked
    at, whose comparison operators land wherever its broken map sends them, with
    every check downstream reading clean. That is precisely the state this corpus
    was in for the whole of #83, and it is why the report is unfiltered: an
    allowlist of glyphs that look harmless is what would have hidden U+001F, which
    reads as extraction debris and is a greater-or-equal sign.
    """

    def test_it_counts_an_unmapped_glyph_from_a_symbol_font(self):
        census = extract.symbol_glyph_census(
            rawline("\u00aa\u00aa", 9.0, [0.0] * 2, font="AdvPSSym")
        )
        self.assertEqual(census, {"AdvPSSym U+00AA": 2})

    def test_it_says_nothing_about_a_glyph_the_table_already_maps(self):
        """A mapped slot is answered, not outstanding. Reporting it would put the
        two fonts this ticket fixed at the top of every refresh's diff forever, and
        a report nobody reads is the shape the whole directory refuses.

        The digits sit in a span of their own here because that is where the PDF
        puts them -- corpus-wide ``AdvPS_SSYB`` emits three characters and none of
        them is a digit. The first draft of this test wrote the whole of ``<=120``
        into the symbol span and got three digits back, which is the census being
        *right*: filtering ASCII to quiet it would have hidden ``SymbolMT``'s
        ``n``, an up arrow set in a letter's slot. So nothing is filtered, and the
        fixture moved instead of the rule.
        """
        self.assertEqual(
            extract.symbol_glyph_census(rawline("\u00a3", 9.0, [0.0], font="AdvPS_SSYB")),
            {},
        )

    def test_it_still_reports_an_unmapped_glyph_from_a_font_it_partly_maps(self):
        """``SymbolMT`` has three rows and emits a dozen other characters. Being
        named in the table exempts a *slot*, never a font."""
        self.assertEqual(
            extract.symbol_glyph_census(
                rawline("\u001f\u2248", 9.0, [0.0] * 2, font="SymbolMT")
            ),
            {"SymbolMT U+2248": 1},
        )

    def test_a_text_face_is_not_censused_however_odd_its_glyphs(self):
        """The report is scoped by the font-name guess, and that guess is only
        affordable because nothing here changes a character."""
        self.assertEqual(
            extract.symbol_glyph_census(
                rawline("\u00a31272", 9.0, [0.0] * 5, font="MinionPro-Regular")
            ),
            {},
        )

    def test_a_space_is_not_reported(self):
        """Every symbol font in the corpus sets them and none means anything by
        it, so 183 of ``AdvPS_SSYB``'s 400 glyphs would otherwise be the loudest
        line in the report."""
        self.assertEqual(
            extract.symbol_glyph_census(rawline("  ", 9.0, [0.0] * 2, font="ZapfDingbats")),
            {},
        )

    def test_the_subset_tag_does_not_split_one_font_into_two(self):
        """Two documents embedding the same face report under one key, or the
        report counts subsets rather than fonts and no total means anything."""
        census = extract.symbol_glyph_census(
            rawline("\u2248", 9.0, [0.0], font="ABCDEF+SymbolMT")
        )
        self.assertEqual(census, {"SymbolMT U+2248": 1})

    def test_an_operator_the_font_already_got_right_is_not_reported(self):
        """``SymbolMT`` renders 2,078 correct comparison operators across the
        corpus -- two thirds of everything this would otherwise print, and all of
        it the mechanism working. A report whose loudest line is the non-defect has
        no usable baseline, and *"the same as last time"* is the only reading a
        maintainer ever takes off it.

        This is a statement about the module's own output vocabulary and not the
        allowlist the class docstring refuses: what is dropped is a character
        ``SYMBOL_FONT_OPERATORS`` *produces*, never one somebody judged harmless.
        """
        self.assertEqual(
            extract.symbol_glyph_census(
                rawline("\u2264\u2265", 9.0, [0.0] * 2, font="SymbolMT")
            ),
            {},
        )

    def test_the_exclusion_is_derived_from_the_table_and_not_typed(self):
        """A sixth row replacing some third character must widen this with it, or
        the census starts reporting the module's own output as an open question."""
        replacements = {
            replacement
            for mapping in extract.SYMBOL_FONT_OPERATORS.values()
            for replacement in mapping.values()
        }
        for replacement in replacements:
            with self.subTest(replacement=f"U+{ord(replacement):04X}"):
                self.assertEqual(
                    extract.symbol_glyph_census(
                        rawline(replacement, 9.0, [0.0], font="ZapfDingbats")
                    ),
                    {},
                )

    def test_an_image_block_and_an_empty_dictionary_contribute_nothing(self):
        self.assertEqual(extract.symbol_glyph_census({"blocks": [{"type": 1}]}), {})
        self.assertEqual(extract.symbol_glyph_census({}), {})

    def test_it_survives_a_span_naming_no_font(self):
        self.assertEqual(extract.symbol_glyph_census(rawline("x", 9.0, [0.0])), {})


class TheCensusReachesTheManifest(unittest.TestCase):
    """A report nothing writes down is an instruction, and #214's rule is that a
    written instruction cannot fail. So the census is carried on the ``Record``,
    lands in ``manifest.json``, and is summed on the run's own summary."""

    def test_a_record_carries_the_census_it_was_built_with(self):
        record = extract.build_document(
            Path("SOC/doc.pdf"),
            ["a page"],
            Path(tempfile.mkdtemp()),
            symbol_glyphs={"SymbolMT U+2248": 3},
        )
        self.assertEqual(record.symbol_glyphs, {"SymbolMT U+2248": 3})

    def test_a_record_built_without_one_reports_nothing_rather_than_raising(self):
        """Every other caller of ``build_document`` in this file passes no census,
        and a default of "nothing was counted" is the only honest one -- the field
        says what the walk found, not what it was able to look at."""
        record = extract.build_document(
            Path("SOC/doc.pdf"), ["a page"], Path(tempfile.mkdtemp())
        )
        self.assertEqual(record.symbol_glyphs, {})

    def test_a_failed_document_carries_an_empty_census(self):
        """A document that could not be read counted nothing, which is not the same
        as a document whose symbol fonts were all mapped -- but the manifest field
        is the same either way, and ``error`` is what tells them apart."""
        self.assertEqual(extract.failed_document(Path("SOC/d.pdf"), "boom").symbol_glyphs, {})

class TheLineSaysWhatASpaceIsWorth(unittest.TestCase):
    """#178: the damage ``span_baselines`` could not reach, and what fixes it.

    That footer is three spans on 16 of its pages and **one span on 142**, and on
    the one-span pages there is no neighbor to borrow a baseline from. Measured
    off KDIGO-2009-Transplant-Recipient-Guideline-English.pdf p.18, Univers-Light
    8.717 pt: the per-glyph gaps run from -2.352 to 0.003 around a median of
    -1.358, so the top of the span's own spread clears any fixed offset from that
    median. It is a font with heavy and variable negative bearings, not tracked
    type, and no median-plus-offset rule can separate the two.

    **What separates them is that the line already contains real space glyphs.**
    The PDF has said where its words are: prev-right to next-left across one of
    those spaces measures 1.056 pt, and the gaps that were being split measure
    0.003. A word break on this line is worth 350 times what a letter join is,
    and the line states both.
    """

    # The footer, one span. Gaps mostly at the median; the few at the top of the
    # spread are the ones the old rule read as word breaks.
    FOOTER_SIZE = 8.7173
    FOOTER_TYPICAL = -1.358
    FOOTER_TOP = 0.003

    # USPSTF/hypertension-screening-adults-final-rec-statement.pdf p.4, and the
    # constraint the ticket names: a line may carry a real space and still have
    # its words glued, so "this line has a space, infer nothing" is too blunt.
    GLUED_SIZE = 8.48
    GLUED_INSIDE = -0.036
    GLUED_BOUNDARY = 1.145

    def footer(self, text: str) -> dict:
        gaps = [self.FOOTER_TYPICAL] * len(text)
        for index, glyph in enumerate(text):
            # Gaps after digits, brackets and some letters reach the top of the
            # real font's spread -- precisely the set that was being split.
            if glyph in "A0123456789();:-" and index + 1 < len(text):
                gaps[index] = self.FOOTER_TOP
        return rawline(text, self.FOOTER_SIZE, gaps)

    def test_the_footer_is_left_alone(self):
        text = "American Journal of Transplantation 2009; 9 (Suppl 3): S6-S9"
        self.assertEqual(extract.rebuild_text(self.footer(text)), text)

    def test_real_spaces_bound_local_spacing_regimes(self):
        """A long compressed phrase must not redefine normally spaced neighbors.

        CDC's opioid MMWR extracted page 27 sets one line in one span, but its
        ``Practice Guidelines ...`` middle is compressed by roughly 3 pt while
        ``In April 2021 ...`` on either side uses ordinary bearings. A single
        median for the span therefore turns every ordinary letter gap into an
        apparent word break even though real spaces already bound each phrase.
        """
        text = "In April Practice Guidelines Administration"
        gaps = [0.2] * len(text)
        for index, glyph in enumerate(text[:-1]):
            if glyph == " " or text[index + 1] == " ":
                # With rawline's 4.5 pt glyph advance, these two bearings make
                # the measured advance across a real space exactly 1.0 pt.
                gaps[index] = -1.75
        for word in ("Practice", "Guidelines", "Administration"):
            start = text.index(word)
            for index in range(start, start + len(word) - 1):
                gaps[index] = -3.0

        self.assertEqual(
            extract.rebuild_text(rawline(text, 9.0, gaps, font="Nunito-Regular")),
            text,
        )

    def test_without_the_second_bar_that_footer_is_split(self):
        """The counterfactual, so the test above cannot pass by having nothing to do.

        **It has to run ``rebuild_text``.** The first version of this asserted
        ``excess > threshold`` over two class constants and never called the
        module at all -- so breaking ``footer()`` would have left the positive test
        green with an unsplittable fixture and this one green beside it, which is
        the vacuous-check shape the rest of this repo is built to refuse. Found by
        the standards axis of ``/code-review``.

        The bar is disabled by driving ``SPACE_ADVANCE_FRACTION`` to zero rather
        than by reimplementing the rule, which is #178's own warning about the
        handoff script that reimplemented ``span_baselines`` and reported identical
        totals before and after a fix.
        """
        text = "American Journal of Transplantation 2009; 9 (Suppl 3): S6-S9"
        page = self.footer(text)
        original = extract.SPACE_ADVANCE_FRACTION
        try:
            extract.SPACE_ADVANCE_FRACTION = 0.0
            without = extract.rebuild_text(page)
        finally:
            extract.SPACE_ADVANCE_FRACTION = original
        self.assertNotEqual(without, text)
        # The damage this fixture reproduces is a gap at the top of the font's
        # spread becoming a word boundary. Real spaces now bound local baselines,
        # so the short digit run no longer demonstrates the second bar by itself;
        # the longer first word does, and keeps this counterfactual nonvacuous.
        self.assertIn("A merican", without)
        self.assertEqual(extract.rebuild_text(page), text)

    def test_a_glued_line_that_also_carries_a_space_still_splits(self):
        """The constraint that makes this non-trivial, and the case the whole
        reader change exists for. USPSTF sets a real space after a bullet and
        glues the words after it anyway."""
        text = "* Behavioralcounseling"
        gaps = [self.GLUED_INSIDE] * len(text)
        gaps[text.index("counseling") - 1] = self.GLUED_BOUNDARY
        self.assertEqual(
            extract.rebuild_text(rawline(text, self.GLUED_SIZE, gaps)),
            "* Behavioral counseling",
        )

    def test_a_line_with_no_space_glyph_is_outside_the_rule_entirely(self):
        """The safety property, and the reason this cannot regress the corpus's
        fully-glued lines: with nothing to calibrate against the rule does not
        fire, so the 59,092 inferences made on lines carrying no space at all are
        untouched by it."""
        text = "Behavioralcounseling"
        gaps = [self.GLUED_INSIDE] * len(text)
        gaps[len("Behavioral") - 1] = self.GLUED_BOUNDARY
        line = rawline(text, self.GLUED_SIZE, gaps)["blocks"][0]["lines"][0]
        self.assertIsNone(extract.span_space_advances(line)[0])
        self.assertEqual(
            extract.rebuild_text(rawline(text, self.GLUED_SIZE, gaps)),
            "Behavioral counseling",
        )

    def test_the_constant_is_not_perched_on_either_case(self):
        """Corpus-wide, every constant in (0.0025, 0.0974] suppresses exactly the
        same 2,809 inferences, and all 2,809 were read and are damage. The value
        is the midpoint of that plateau rather than the edge of it -- #83's
        tuning table named a value at an edge and it was the one setting worse
        than not making the change at all.
        """
        self.assertLess(0.0025, extract.SPACE_ADVANCE_FRACTION)
        self.assertLess(extract.SPACE_ADVANCE_FRACTION, 0.0974)

    def test_one_space_is_enough_and_that_is_not_span_baselines_rule(self):
        """The deliberate divergence from ``span_baselines``, pinned so it stays one.

        A baseline is a median and needs ``MINIMUM_GAPS_FOR_BASELINE`` samples
        before it means anything. An advance is not a summary -- one real space is
        one word break the typesetter set -- so a single sample is evidence and is
        used. Asserting both halves, because the claim is the *difference*: the
        same line gives an advance off one space and no baseline off one gap.
        """
        text = "ab cdefgh"
        gaps = [self.GLUED_INSIDE] * len(text)
        line = rawline(text, self.GLUED_SIZE, gaps)["blocks"][0]["lines"][0]
        spaces = [c for c in line["spans"][0]["chars"] if c["c"] == " "]
        self.assertEqual(len(spaces), 1)
        self.assertIsNotNone(extract.span_space_advances(line)[0])

        short = rawline("ab", self.GLUED_SIZE, [self.GLUED_BOUNDARY])
        glyphs = [
            (char, self.GLUED_SIZE)
            for char in short["blocks"][0]["lines"][0]["spans"][0]["chars"]
        ]
        self.assertEqual(extract.line_baseline(glyphs), 0.0)

    def test_a_non_positive_advance_disables_the_bar_rather_than_zeroing_it(self):
        """The third answer, which is neither a measurement nor silence.

        Bearings negative enough put the next glyph's left edge behind the
        previous glyph's right edge even across a real space. A floor computed
        from that is zero or backwards, so the bar is dropped -- because applying
        it would be applying a bar every gap on the line clears, which is the
        silent failure rather than a conservative one.
        """
        # A space whose neighbors close over it: the advance comes back negative.
        text = "ab cd ef gh"
        gaps = [-self.GLUED_SIZE] * len(text)
        line = rawline(text, self.GLUED_SIZE, gaps)["blocks"][0]["lines"][0]
        self.assertLess(extract.span_space_advances(line)[0], 0.0)

        # And a genuinely glued line whose only space is of that kind still splits,
        # which is what "disabled" has to mean for it to be the safe direction.
        glued = "ab cdefghij"
        gaps = [-self.GLUED_SIZE] * len(glued)
        gaps[glued.index("cdefghij") - 1] = -self.GLUED_SIZE
        gaps[glued.index("fghij") - 1] = self.GLUED_BOUNDARY - self.GLUED_SIZE
        page = rawline(glued, self.GLUED_SIZE, gaps)
        self.assertLess(extract.span_space_advances(page["blocks"][0]["lines"][0])[0], 0.0)
        self.assertIn(" ", extract.rebuild_text(page).strip()[3:])

    def test_the_advance_is_measured_across_the_space_and_not_of_it(self):
        """A space glyph's own width is not what separates two words -- the gaps
        on either side of it count too, and on this footer they are negative
        enough to halve it. Measuring the glyph alone would put the advance at
        3.776 where the real separation is 1.056."""
        line = self.footer("ab cd ef gh")["blocks"][0]["lines"][0]
        advance = extract.span_space_advances(line)[0]
        chars = line["spans"][0]["chars"]
        space = next(c for c in chars if c["c"] == " ")
        self.assertLess(advance, space["bbox"][2] - space["bbox"][0])

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
        clinical = "\u2265\u2264°µμ±×÷⁄/%.,"
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

    def test_a_running_head_carrying_its_page_number_is_not_a_literal_repeat(self):
        # These differ page to page, so the *literal* rule does not reach them.
        # That was a known limit until #100 ruled; `MarginPatterns` below is
        # where the same lines are now caught, and this stays as the statement
        # that the two rules are separate and that this one did not widen.
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


class MarginPatterns(unittest.TestCase):
    """Issue #100's ruled rule: mask digits, but only in the page margins.

    The ruling and the measurement it rests on are in ``guidelines_extract``'s
    docstring. What is pinned here is the pair of behaviors that make the rule
    safe, because either one alone is worse than not having the rule:

    - a line whose only page-to-page difference is a number, sitting in a
      margin, is stripped;
    - the same masked pattern **mid-page is not touched**, which is what keeps a
      contents-page entry and a table cell out of it.
    """

    @staticmethod
    def folioed(pages, folio_at="end", start=37):
        """Pages carrying a bare folio in a margin, one number higher each page."""
        built = []
        for offset, body in enumerate(pages):
            folio = f"S{start + offset}"
            built.append([folio] + body if folio_at == "start" else body + [folio])
        return built

    def test_a_welded_running_head_in_a_margin_is_caught(self):
        # The AHA excerpt's own head, and the reason this rule exists: it reads
        # "April 28, 2026 Circulation. 2026;153:e1154-e1276. DOI: ...e1155" and
        # the trailing folio differs on every page, so no literal repeats.
        patterns = extract.find_margin_patterns(extract.clean_pages(AHA))
        self.assertTrue([p for p in patterns if "DOI:" in p])

    def test_the_caught_pattern_is_recorded_with_its_digits_masked(self):
        # The manifest has to say what rule removed a line, and a masked pattern
        # is the only honest way to name a family whose members all differ.
        patterns = extract.find_margin_patterns(extract.clean_pages(AHA))
        head = next(p for p in patterns if "DOI:" in p)
        self.assertIn("#", head)
        self.assertNotIn("2026", head)

    def test_the_head_is_gone_from_the_pages_that_carried_it_in_a_margin(self):
        pages = extract.clean_pages(AHA)
        kept = extract.strip(pages, extract.find_boilerplate(pages),
                             extract.find_margin_patterns(pages))
        # Pages 1 to 3 carry it at index 1, inside the top margin.
        self.assertFalse([line for line in kept[1] + kept[2] + kept[3] if "DOI:" in line])

    def test_the_same_head_sitting_mid_page_is_left_where_it_is(self):
        # Page 0 of the excerpt is a cover: the same string sits at index 2 of 6,
        # outside both margins. It survives, and that residue is the price of the
        # restriction rather than a bug -- see the module docstring. Stripping the
        # pattern page-wide instead is what eats the table cells below.
        pages = extract.clean_pages(AHA)
        kept = extract.strip(pages, extract.find_boilerplate(pages),
                             extract.find_margin_patterns(pages))
        self.assertTrue([line for line in kept[0] if "DOI:" in line])

    @staticmethod
    def threshold_document():
        """Eight pages of a threshold table, a bare folio at the foot of each.

        Every line is unique to its page on purpose. A line repeated verbatim is
        the *literal* rule's business and would be stripped before this rule ran,
        which would make the assertions below pass for the wrong reason.
        """
        return [
            [f"opening remarks {letter}",
             f"table {letter}. blood pressure",
             f"Stage 1 hypertension {130 + n}-139 mm Hg",
             f"Stage 2 hypertension {140 + n}-159 mm Hg",
             f"closing remarks {letter}",
             f"S{40 + n}"]
            for n, letter in enumerate("abcdefgh")
        ]

    def test_a_threshold_row_repeated_mid_page_is_not_strippable(self):
        # Issue #100's explicit done-when, and the trade #80 refused. These rows
        # differ only in their numbers, so unrestricted masking folds all eight
        # onto "Stage # hypertension #-# mm Hg" and takes the table out. The
        # margin restriction is the only thing standing between the two, which is
        # why the rows sit at index 2 and 3 of a six-line page.
        pages = self.threshold_document()
        kept = extract.strip(pages, extract.find_boilerplate(pages),
                             extract.find_margin_patterns(pages))
        for n, page in enumerate(kept):
            self.assertIn(f"Stage 1 hypertension {130 + n}-139 mm Hg", page)
            self.assertIn(f"Stage 2 hypertension {140 + n}-159 mm Hg", page)

    def test_the_bare_folio_beside_that_table_is_still_taken(self):
        # The same document: the rule has to earn its keep on the page it is
        # being trusted not to damage, or "nothing was stripped" would pass it.
        pages = self.threshold_document()
        kept = extract.strip(pages, extract.find_boilerplate(pages),
                             extract.find_margin_patterns(pages))
        self.assertFalse([line for page in kept for line in page if line.startswith("S4")])

    def test_a_contents_entry_survives_a_folio_of_its_own_shape(self):
        # KDIGO-2021-Blood-Pressure made small. Its folio is "S37" at the foot of
        # 87 pages, and its contents page lists "S3" and "S7" mid-page. The two
        # mask identically, so page-wide stripping would clear the contents page
        # and record it as boilerplate removal. This is the single test the
        # margin restriction exists for.
        contents = ["Contents", "Chapter one", "S3", "Tables and figures", "S7",
                    "Executive Committee"]
        body = [[f"opening {a}", f"prose {a}", f"more {a}", f"further {a}",
                 f"closing {a}", f"end {a}"] for a in "bcdefgh"]
        pages = self.folioed([contents] + body)
        kept = extract.strip(pages, extract.find_boilerplate(pages),
                             extract.find_margin_patterns(pages))
        self.assertIn("S3", kept[0])
        self.assertIn("S7", kept[0])
        self.assertFalse([line for page in kept for line in page if line.startswith("S37")])
        self.assertFalse([line for page in kept for line in page if line.startswith("S4")])

    def test_a_number_that_only_ever_appears_mid_page_never_becomes_a_pattern(self):
        # KDIGO-2024-CKD's shape: 466 bare-number lines, every one a cell in a
        # risk table, none of them in a margin. Nothing here should clear.
        pages = [["head", "prose", "0.95", "1.4", "4", "0.96", "prose", "foot"]
                 for _ in range(8)]
        self.assertEqual(extract.find_margin_patterns(pages), [])

    def test_a_line_carrying_no_digit_is_not_this_rule_s_business(self):
        # It masks to itself, so a margin-only tally could strip it on evidence
        # the literal rule never saw. Left to `find_boilerplate`, which counts
        # the whole page.
        pages = [["RUNNING HEAD", "body", "more", "foot"] for _ in range(8)]
        self.assertEqual(extract.find_margin_patterns(pages), [])

    def test_a_literal_hash_is_not_swept_up_by_the_mask(self):
        # "Table #" masks to itself and so joins the family "Table 5" makes.
        # Requiring a digit in the line keeps a typeset number sign out of it.
        # It sits on 4 of 8 pages so the literal rule leaves it alone too --
        # otherwise this would pass without the guard existing.
        pages = [[f"Table {n}", f"body {a}", f"more {a}",
                  "Table #" if n < 4 else f"foot {a}"]
                 for n, a in enumerate("abcdefgh")]
        kept = extract.strip(pages, extract.find_boilerplate(pages),
                             extract.find_margin_patterns(pages))
        self.assertEqual(extract.find_margin_patterns(pages), ["Table #"])
        for page in kept[:4]:
            self.assertIn("Table #", page)
        self.assertFalse([line for page in kept for line in page if line == "Table 0"])

    def test_both_ends_of_the_page_are_margins(self):
        top = extract.find_margin_patterns(self.folioed(
            [["a", "b", "c", "d", "e", "f"] for _ in range(8)], folio_at="start"))
        foot = extract.find_margin_patterns(self.folioed(
            [["a", "b", "c", "d", "e", "f"] for _ in range(8)], folio_at="end"))
        self.assertEqual(top, ["S#"])
        self.assertEqual(foot, ["S#"])

    def test_the_second_line_in_is_still_a_margin(self):
        # KDIGO-2009 and idachildrenfinal set the folio one line in from the
        # foot. N=1 leaves both unstripped; this is the whole reason N is 2.
        pages = [["a", "b", "c", "d", f"S{40 + n}", "colophon"] for n in range(8)]
        self.assertEqual(extract.find_margin_patterns(pages), ["S#"])

    def test_the_third_line_in_is_not(self):
        # N=2 is a measured choice, not a taste: at N=3 the rule flips
        # KDIGO-2013-Lipids from stripping nothing to stripping its own figure
        # axis -- page 23 opens "20 / 10 / 5 / 2" and N=3 takes the first two.
        # The boundary has to be a test or the next reader widens it for free.
        pages = [["a", "b", "c", f"S{40 + n}", "d", "e", "colophon"] for n in range(8)]
        self.assertEqual(extract.find_margin_patterns(pages), [])

    def test_a_short_page_is_all_margin_and_still_votes_once(self):
        # Four lines with N=2 makes every line a margin line, and the top and
        # bottom halves overlap on a three-line page. A page votes once per
        # pattern either way.
        pages = [["head", f"S{40 + n}", "foot"] for n in range(8)]
        self.assertEqual(extract.find_margin_patterns(pages), ["S#"])

    def test_the_threshold_and_the_floor_are_the_ones_the_literal_rule_uses(self):
        # 3 of 8 clears the occurrence floor and fails the percentage.
        pages = [["a", "b", "c", f"S{40 + n}"] if n < 3 else ["a", "b", "c", "d"]
                 for n in range(8)]
        self.assertEqual(extract.find_margin_patterns(pages), [])

    def test_a_one_page_document_has_no_margin_pattern(self):
        self.assertEqual(extract.find_margin_patterns([["a", "1", "b"]]), [])

    def test_a_document_with_no_pages_has_no_margin_pattern(self):
        self.assertEqual(extract.find_margin_patterns([]), [])

    def test_the_recorded_set_is_ordered_so_two_runs_agree(self):
        pages = self.folioed([["a", "b", "c", "d", f"Page {n} of 8"] for n in range(8)])
        patterns = extract.find_margin_patterns(pages)
        self.assertEqual(patterns, sorted(patterns))

    def test_stripping_leaves_the_pages_in_place(self):
        pages = self.folioed([["a", "b", "c", "d"] for _ in range(8)])
        kept = extract.strip(pages, [], extract.find_margin_patterns(pages))
        self.assertEqual(len(kept), len(pages))

    def test_it_reports_the_exact_strings_it_took(self):
        # The manifest contract: a removal can be read back rather than believed.
        # A masked pattern alone cannot be read back -- it names a family, not a
        # line -- so the literals go in beside it.
        pages = self.folioed([["a", "b", "c", "d"] for _ in range(8)])
        taken = extract.margin_removals(pages, [], extract.find_margin_patterns(pages))
        self.assertEqual(taken, [f"S{37 + n}" for n in range(8)])

    def test_what_it_reports_taking_is_what_stripping_takes(self):
        pages = extract.clean_pages(AHA)
        literal = extract.find_boilerplate(pages)
        patterns = extract.find_margin_patterns(pages)
        kept = {line for page in extract.strip(pages, literal, patterns) for line in page}
        for line in extract.margin_removals(pages, literal, patterns):
            self.assertNotIn(line, kept)

    def test_a_pattern_that_removed_nothing_is_not_recorded_against_the_document(self):
        # "(c) 2021 American Medical Association" clears the margin rule on 68
        # USPSTF files, and the literal rule has already taken every member --
        # within one document the year does not vary. Recording it anyway put
        # 168 of 195 manifest entries against no removal at all, which reads as
        # a rule doing seven times the work it does.
        pages = [["© 2021 American Medical Association", f"body {a}", f"more {a}",
                  f"foot {a}"] for a in "abcdefgh"]
        with tempfile.TemporaryDirectory() as tmp:
            record = extract.build_document(
                Path("USPSTF/x.pdf"), ["\n".join(page) for page in pages], Path(tmp))
        self.assertIn("© 2021 American Medical Association", record.boilerplate)
        self.assertEqual(record.margin_patterns, [])
        self.assertEqual(record.margin_stripped, [])

    def test_the_recorded_patterns_are_the_masks_of_the_recorded_lines(self):
        pages = self.folioed([[f"opening {a}", f"body {a}", f"more {a}", f"foot {a}"]
                              for a in "abcdefgh"])
        with tempfile.TemporaryDirectory() as tmp:
            record = extract.build_document(
                Path("KDIGO/y.pdf"), ["\n".join(page) for page in pages], Path(tmp))
        self.assertEqual(record.margin_patterns, ["S#"])
        self.assertEqual(record.margin_stripped, [f"S{37 + n}" for n in range(8)])

    def test_the_stripped_lines_are_gone_from_the_file_that_was_written(self):
        pages = self.folioed([[f"opening {a}", f"body {a}", f"more {a}", f"foot {a}"]
                              for a in "abcdefgh"])
        with tempfile.TemporaryDirectory() as tmp:
            record = extract.build_document(
                Path("KDIGO/y.pdf"), ["\n".join(page) for page in pages], Path(tmp))
            written = (Path(tmp) / record.output).read_text(encoding="utf-8")
        for line in record.margin_stripped:
            self.assertNotIn(line, written)
        self.assertIn("opening a", written)

    def test_a_line_the_literal_rule_already_took_is_not_reported_twice(self):
        # "Downloaded from ... August 12, 2026" carries digits and sits at the
        # foot of every AHA page, so both rules see it. It belongs to the one
        # that ran first, or chars_stripped is counted against two owners.
        pages = extract.clean_pages(AHA)
        literal = extract.find_boilerplate(pages)
        taken = extract.margin_removals(pages, literal, extract.find_margin_patterns(pages))
        self.assertNotIn(DOWNLOADED, taken)


class DocumentClass(unittest.TestCase):
    @staticmethod
    def every_page_carries(line, count=4):
        return [["body text", line] for _ in range(count)]

    def test_the_acip_captures_are_not_read_as_guidelines(self):
        # The three ACIP/ files are browser print-to-PDF captures of CDC schedule
        # pages. Issue #80 asks for them flagged rather than parsed as guidelines.
        self.assertEqual(
            extract.classify(extract.clean_pages(ACIP)), extract.CLASS_WEB_CAPTURE
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
            extract.CLASS_WEB_CAPTURE,
        )

    def test_the_stamp_is_recognized_with_the_page_title_folded_in_after_it(self):
        # This is the only form the real files take. Requiring the stamp to be
        # the whole line passed the fixture and found zero captures in 179 files.
        self.assertEqual(
            extract.classify(
                self.every_page_carries("8/12/26, 10:25 AM Recommended Vaccinations | CDC")
            ),
            extract.CLASS_WEB_CAPTURE,
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
        self.assertEqual(extract.classify(pages), extract.CLASS_WEB_CAPTURE)

    def test_a_stamp_on_one_page_of_many_is_not_a_capture(self):
        pages = [["body"], ["body"], ["body"], ["8/12/26, 10:25 AM Something | CDC"]]
        self.assertEqual(extract.classify(pages), extract.CLASS_GUIDELINE)

    def test_a_document_with_no_pages_at_all_is_a_guideline(self):
        self.assertEqual(extract.classify([]), extract.CLASS_GUIDELINE)

    # ------------------------------------------------------------------
    # The recommendation-statement branch, #185
    # ------------------------------------------------------------------

    USPSTF_TITLE = [
        "US Preventive Services Task Force Recommendation Statement",
        "Screening for Colorectal Cancer",
    ]

    def test_a_document_that_titles_itself_a_recommendation_statement_is_one(self):
        self.assertEqual(
            extract.classify([self.USPSTF_TITLE, ["body"], ["body"], ["body"]]),
            extract.CLASS_RECOMMENDATION_STATEMENT,
        )

    def test_the_title_block_is_matched_with_its_spaces_lost(self):
        # Several USPSTF files render the line as one run of letters, which is
        # the extraction losing the space glyphs rather than the page saying so.
        glued = [["USPreventiveServicesTaskForceRecommendationStatement"]]
        self.assertEqual(
            extract.classify(glued + [["body"]] * 3),
            extract.CLASS_RECOMMENDATION_STATEMENT,
        )

    def test_both_marks_are_required(self):
        # "Summary of Recommendation Statements" is a table-of-contents line in
        # four KDIGO guidelines and in the CDC opioid guideline. Matching the
        # phrase alone classes all five wrongly.
        for line in (
            "Summary of Recommendation Statements",
            "US Preventive Services Task Force",
        ):
            with self.subTest(line=line):
                self.assertEqual(
                    extract.classify([[line], ["body"], ["body"], ["body"]]),
                    extract.CLASS_GUIDELINE,
                )

    def test_the_mark_is_read_off_the_first_page_only(self):
        # A guideline citing a USPSTF recommendation statement in its references
        # is not one. The document titles itself on its title page or not at all.
        pages = [["KDIGO 2024 Clinical Practice Guideline"], ["body"], ["body"]]
        pages.append(self.USPSTF_TITLE)
        self.assertEqual(extract.classify(pages), extract.CLASS_GUIDELINE)

    def test_a_capture_that_says_recommendation_statement_is_still_a_capture(self):
        # The order is the whole rule: a capture of a USPSTF page is still a
        # capture, and the catalog consumes this pre-strip answer from the manifest.
        stamped = [
            ["8/12/26, 10:25 AM Screening | USPSTF"] + self.USPSTF_TITLE
        ] + [["8/12/26, 10:25 AM Screening | USPSTF", "body"] for _ in range(3)]
        self.assertEqual(extract.classify(stamped), extract.CLASS_WEB_CAPTURE)

    def test_every_value_classify_can_return_is_in_the_published_vocabulary(self):
        # `CLASS_UNKNOWN` is deliberately outside `CLASSES` and is deliberately
        # not reachable from here: it is what a document that was never read
        # carries, and a document that was never read is never classified.
        for pages in (
            [],
            self.every_page_carries("8/12/26, 10:25 AM Adult Schedule | CDC"),
            [self.USPSTF_TITLE, ["body"], ["body"], ["body"]],
            [["KDIGO 2024 Clinical Practice Guideline"], ["body"], ["body"]],
        ):
            with self.subTest(pages=pages[:1]):
                self.assertIn(extract.classify(pages), extract.CLASSES)


class OutputStaysOutOfTheRepo(unittest.TestCase):
    """Anything written inside a worktree is copied into all of them.

    **How many are live is deliberately not stated**, on #143's terms: it moves
    on every ``git worktree add`` and nothing re-derives it. This docstring was
    the *third* copy of that count -- the review found one, the tracker sweep
    found its twin in ``guidelines_extract.py``, and a sweep agent then found
    this one, in the third file the same commit had open.
    """

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

    def test_the_reason_this_artifact_stays_out_is_stated_here(self):
        """**The rule moved and the reason did not.** ``repo_root`` holds one
        detection rule for four writers; why *this* artifact must stay out is
        this module's own -- a worktree materializes tracked files and copies
        gitignored ones, so anything landing in one lands in all twelve. The
        other two writers state #87's copyright and a list of patient names.

        The detection is graded in ``test_repo_root.py`` and the four sites are
        cross-checked in ``test_write_guards.py``; what is left here is that the
        sentence a user reads still explains this artifact.
        """
        self.assertIn("worktree", extract.WHY_OUTSIDE)
        self.assertIn("outside", extract.WHY_OUTSIDE)


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
            extract.CLASS_WEB_CAPTURE,
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
            self.documents["ACIP/adult"].document_class, extract.CLASS_WEB_CAPTURE
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
