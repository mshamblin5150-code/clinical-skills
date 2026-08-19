"""Extract per-page text from the guideline PDF corpus and strip page-repeated boilerplate.

phi-scan: synthetic

The pragma is here because PRINT_CAPTURE_STAMP's comment quotes the browser print
header off a public CDC page, and that header is date-shaped. Writing it in pieces
to slip past the scanner would dodge the rule without declaring anything. The
corpus layer is untouched by this and still applies.

    python tools/guidelines_extract.py <source-directory> [--out <directory>]

``<source-directory>`` is the corpus as downloaded: one subdirectory per society,
PDFs inside. It lives outside this repo and stays there -- 179 files, 410 MB, most
of them society-copyrighted. Issue #87 rules on that and is not reopened here.

**Nothing this writes goes inside the repo, and the script refuses to.** Output
defaults to a sibling of the source directory (``guidelines-src`` next door becomes
``guidelines-text``). ``reference/`` and ``scratch/`` are both wrong for it for the
same reason: tracked files are materialized in every worktree and gitignored ones
are copied into every worktree, and there are six live.

**Maintainer-only, and that is what buys the dependency.** Everything else in
``tools/`` is stdlib. This reads PDFs, so it needs ``pymupdf``, and it runs once per
corpus refresh rather than on anything a consumer does. The dependency must not
leak: the artifacts downstream tickets read are the ``.txt`` files this emits.

**Why PyMuPDF, and why that reverses what this file used to say.** This module read
the corpus with ``pypdf`` until #83, on a recorded reason: ``fitz`` loses the spaces
between words on the USPSTF files -- whole sentences come back as
``primarycarebecauseofitshighsensitivity`` -- and 90 of the 179 documents are
USPSTF. **That observation was true and the conclusion drawn from it was wrong.** It
was measured against ``page.get_text()``, which is one of several things PyMuPDF
will do, and the glued words are not lost information: the *geometry* still carries
the word boundary. On a glued USPSTF line, the gap between two characters inside a
word measures -0.036 pt and the gap at a word boundary measures 1.145 pt, at an 8.48
pt font. A twelve-fold separation is not a hard call.

So ``rebuild_text`` walks ``rawdict``'s per-character boxes and inserts a space
wherever the horizontal gap stands out against the line's own spacing -- see
``line_baseline`` for why *against the line* and not against the font size.

**Measured over all 179 documents and all 7,733 pages, 2026-08-16.** Zero read
errors from either library:

=========================  =========  =====  ======  =====
reader                         words  glued   split   time
=========================  =========  =====  ======  =====
pypdf                      5,340,439   4168      --  342 s
fitz get_text (default)    5,319,299   6568      --     --
fitz + rebuild_text        5,369,614    719   6,881  195 s
=========================  =========  =====  ======  =====

``glued`` is words longer than 25 characters -- a run whose spaces were lost.
``split`` is the reverse and is defined under *What the rebuild costs*.

**These figures replace a 14-document, 4-page-each sample, and the sample was
wrong in a way worth recording.** It reported 117 glued for pypdf against 4,168,
and it reported the splitting cost as *"11 words out of 11,522 distinct"* when the
corpus figure is three orders of magnitude larger. Worse, the tuning table it
produced said 0.14 wrongly split nothing; over the whole corpus 0.14 leaves 5,094
glued runs, which is **worse than the library it replaced**. A reader trusting that
table would have picked the one value that loses to pypdf. #83 published it, and it
was caught by being asked to read every document rather than a selection.

**What the rebuild costs, isolated rather than bounded.** ``split`` above is a set
difference -- words present in ``get_text``'s output and absent after the rebuild --
and it counts every short glued run the rebuild correctly broke apart as though it
were damage. ``seethe`` -> ``see the`` is in it. So every split the rebuild makes
was recorded as ``run -> pieces`` and classified against a lexicon built from tokens
**the PDF itself delimited with real space glyphs**, which needs no outside
dictionary and cannot be defined by the inference under test:

=================================  ======  =====  ==========================
class                                   n      %  verdict
=================================  ======  =====  ==========================
glued run fixed                     9,622  70.3%  correct, the point
punctuation, tab or bullet          3,179  23.2%  harmless separation
digit-break                           390   2.8%  damage, all in citations
letter-spaced word                    306   2.2%  **the real cost**
word broken, pieces not all single    188   1.4%  mostly a footnote marker
=================================  ======  =====  ==========================

13,685 split occurrences over 10,731 distinct shapes, all 179 documents, 2026-08-16.

**The number that matters for this repo is zero.** Of the 390 digit-breaks, every
distinct run is citation apparatus -- a year (``2009;``, 158 of them),
supplement page ranges (``S131-S155``), a superscript reference marker welded to
its word (``al,23``). **Not one carries a clinical unit**, so no threshold value is
broken anywhere in the corpus. That was the risk worth measuring: a repo whose
subject is numbers cannot afford a reader that splits them, and this one does not.

So the true cost is **306 letter-spaced words** in readable text, or 696 counting
the citation digit-breaks -- against 6,881 by set difference. The ``word broken`` row
is mostly ``bThe -> b|The``, which is the rebuild correctly separating a footnote
marker from the word after it and is miscounted as damage here rather than credited.

**284 of those 696 are one running footer in one document, and it is unfinished
work.** ``KDIGO-2009-Transplant-Recipient-Guideline-English.pdf`` carries

    American Journal of Transplantation 2009; 9 (Suppl 3): S6-S9

on every page, and it accounts for 142 of the 306 letter-spaced splits and 142 of
the 390 digit-breaks. ``span_baselines`` fixed the 16 pages where that footer is set
as three spans and **not the 142 where it is one**: there the whole footer is a
single Univers-Light span whose per-glyph gaps run from -2.35 to 0.00 around a
median of -1.36, so the top of its own spread clears any fixed offset from that
median. It is a font with heavy and highly variable negative bearings, not tracked
type, and the median-plus-offset rule cannot separate the two.

**The line already carries real space glyphs**, which is the lead worth following:
the PDF has already said where its words are, and nothing on that line needed
inferring at all. A rule that measured a candidate gap against the width of an
actual space on the same line -- rather than against the median -- would leave it
alone. That is not built here, because the same rule must not undo the USPSTF case,
where a line has a space after its bullet and its words are glued anyway. See #178.

**And the footer is boilerplate that should never have reached a reader**: its page
range varies per page, so the 75% rule never strips it. #178 reads that as #100's
cause 1 and expects #100 to remove the damage without touching the space rule.

**#100 has landed and it does not, and the reason is #178's own subject.** The
letter-spacing damage sets every digit as its own run, so the page range masks to a
different pattern depending on how many digits it has: ``S # - S #`` on one page and
``S # # - S # #`` on the next. The footer produces **8 distinct masked patterns**
across 32 sampled pages, the largest reaching 16, against a floor of 24 -- so
nothing clears and all 166 lines stay. Measured 2026-08-16. The dependency runs the
other way round from the one #178 states: the space rule has to be fixed first, or
the two have to meet.

The trade favors the body over the front matter, which is the right way round: what
splits is display type in headings and reference lists, and what is repaired is
running prose, where a threshold lives.

**The boilerplate rule.** A line appearing on 75% or more of a document's sampled
pages is boilerplate, is stripped from every page, and is recorded per document so
the removal can be audited rather than believed. This is the point of the whole
script: every AHA/ACC file carries ``Downloaded from http://ahajournals.org by on
August 12, 2026``, and strings like it sit in the page's reading order -- they can
land between a table row's label and its number, which is the one thing a threshold
sheet cannot survive.

**The margin rule, and #100's ruling.** Inside ``MARGIN_LINES`` of either end of a
page, a line's digits are masked before it is counted, so a running head with its
folio welded into it repeats and is seen. Outside the margins nothing is masked and
nothing is compared, on the way in or on the way out.

**The restriction is the whole safety property, and it is not a tuning knob.**
Unrestricted masking is the trade #80 refused: ``130-139 mm Hg`` and
``140-159 mm Hg`` become the same line, and the failure is silent -- the manifest
records a masked pattern, the number is gone, and nothing says which it was. That
is not hypothetical here. Masked corpus-wide, the rule takes 466 lines out of
``KDIGO-2024-CKD-Guideline``, every one a cell in a risk table; it clears the
contents page of ``KDIGO-2021-Blood-Pressure-in-CKD``, whose ``S3`` and ``S7``
entries mask exactly like the ``S37`` folio at the foot of 87 pages; and it takes
the axis labels off Figure 2 of the USPSTF colorectal statement. Restricted to the
margins it takes none of them, because a running head lives at a page edge and a
table row does not.

**Two is measured, not chosen.** Against the 179-document corpus, N=1 and N=2 remove
bare folios and two welded running heads **and nothing else at all** -- 2,382 folios
and 267 head lines at N=2. N=3 removes a further 574 lines across 11 documents, and
most are genuine folios, but it also flips ``KDIGO-2013-Lipids-Guideline`` from
stripping nothing to stripping its own **figure axis**: page 23 opens ``20 / 10 / 5
/ 2`` and N=3 takes the ``20`` and the ``10``. That is the same damage class the
restriction exists to avoid, arriving at the third line in. N=2 over N=1 because
``KDIGO-2009-Transplant-Recipient`` and ``USPSTF/idachildrenfinal`` set the folio one
line in from the foot. ``test_guidelines_extract.py`` pins the boundary at N=2 and at
N=3 in both directions, because widening it by one line is exactly the change that
looks free.

**The figure above was published wrong once and the error is worth keeping.** This
paragraph first said N=3 takes ``0000000000001122``, a DOI, out of the colorectal
references. It does not. That measurement was taken over the **already-stripped**
``.txt`` corpus rather than over the PDFs, so it was answering a different question
than the one it was quoted for, and it came out both wrong and plausible. Every
figure here is now re-derived by running this module's own functions over
``guidelines-src``. Measured 2026-08-16.

**#100's cause 2 gets no code here, because it stopped existing before the ruling.**
The ticket describes a running head alternating recto and verso -- two strings, each
below the threshold, together above it -- and names
``USPSTF/Screening for Thyroid Dysfunction`` as the case. Under PyMuPDF that document
strips ``CLINICAL GUIDELINE``, ``Screening for Thyroid Dysfunction`` and
``www.annals.org`` as three separate literal lines: the reader sets them on separate
lines instead of concatenating them, so each clears 75% on its own and there is no
alternation left to catch. Swept across all 179 documents, no surviving case has the
shape. Like cause 1, it was a property of ``pypdf`` rather than of the documents --
which #100's own comment says of cause 1 and explicitly denies of cause 2. Recorded
because a rule that was never needed is invisible afterwards, and the next reader
would otherwise find option 1 implemented and option 2 apparently forgotten.

**What the run does.** 27 of 179 documents gain something the literal rule missed,
2,649 distinct lines, of which 2,382 are bare folios and 267 are the two welded
heads. Documents with nothing stripped by either rule fall from 12 to 5. The two
#100 names as true negatives that must stay true negatives -- the CDC opioid MMWR,
a web-page print with no running head, and the 2-page ``IDSA/ciab275`` erratum --
still report nothing stripped.

**Known limits, stated so nobody reads more into the output than is there.**

- **A folio set in roman numerals is not masked, and will not be.** ``GOLD-REPORT-2026``
  loses its disclaimer head on 236 pages and keeps it on the 10 front-matter pages
  foliated ``i`` to ``x``, plus one page carrying no folio at all. Masking roman
  numerals means masking the letters i, v, x, l, c, d and m, which are letters in
  words; the residue is 11 lines of 247 in one document and the cure is worse.
- **A line the margin rule catches survives where it sits mid-page.** The AHA
  excerpt's cover page carries the same running head at line 3 of 6, outside both
  margins, and it stays. That is the price of the restriction rather than a bug --
  the alternative is the contents page above.
- **Hyphenation at a line break is left alone.** ``speci-`` / ``ficity`` stays two
  lines. Rejoining it needs a lexicon to avoid welding real compounds together, and
  the indexer (#84) is a better place to decide that than the extractor.
- **A page whose text layer is empty is recorded, not repaired.** No OCR anywhere;
  the survey found every sampled document carries an extractable layer.
- **The output is derived and lossy, and the PDFs stay the source of record.**
  ``normalize`` deletes soft hyphens and icon glyphs and folds curly quotes to
  ASCII, none of which can be undone from the text. Anything downstream that needs
  the page as typeset has to go back to the PDF.
- **A re-run overwrites but never deletes.** Rename a source file and the old
  ``.txt`` stays behind, claimed by no manifest entry. The summary names orphans
  rather than removing them: this is the maintainer's directory, and a tool that
  deletes from it on the strength of a glob is a worse trade than a printed list.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

from console_codec import use_utf8

REPO_ROOT = Path(__file__).resolve().parent.parent

# Written with an explicit codec on every call and recorded in the manifest. This
# is not ceremony: the en dash in "130-139 mm Hg" survives extraction intact and
# then dies on the way out, because the default encoding on a Windows console is
# cp1252 and cannot represent it. A recorded codec is how that stays visible.
OUTPUT_CODEC = "utf-8"

PAGE_SEPARATOR = "\f"
MANIFEST_NAME = "manifest.json"

# A line has to clear both bars. The percentage is #80's rule verbatim, and both
# bars are shared with the margin rule below rather than restated by it.
#
# **The occurrence floor narrows #80's rule; #100's margin rule widens it, and
# they are the only two departures.** Every line of a one-page document appears on
# 100% of its pages, so the percentage alone strips such a document to nothing and
# records it as clean. The floor binds only where 75% of the sampled pages is fewer
# than 3 -- documents of 1, 2 or 3 pages -- and is arithmetically inert above that.
# Corpus impact at the time of writing is one 2-page file.
BOILERPLATE_THRESHOLD = 0.75
MINIMUM_OCCURRENCES = 3

# #100's ruling. How far in from either end of a page a line's digits are masked
# before it is counted. Why the rule exists, why it is restricted, and why 2
# rather than 1 or 3 are in this module's docstring under "The margin rule" --
# stated there once rather than twice here, on `icd10_lookup.py`'s terms.
MARGIN_LINES = 2

_DIGIT_RUN = re.compile(r"\d+")
DIGIT_MASK = "#"

# Sample evenly across the document rather than off the front: covers, contents
# and reference pages carry no running head, so a front-loaded sample of a
# 400-page report concludes there is no boilerplate in it.
#
# #80's floor is 8 pages. SAMPLE_SIZE sits well above it because sampling costs
# nothing here -- the pages are already extracted and in memory by the time the
# rule runs -- and a wider sample puts the measured rate closer to the true one.
SAMPLE_SIZE = 32
MINIMUM_SAMPLE = 8

# How far a gap has to EXCEED its line's baseline before ``rebuild_text`` calls it
# a space, as a fraction of the span's font size.
#
# **Tuned over all 179 documents and all 7,733 pages, 2026-08-16** -- the previous
# table here was a 10-document sample and it was wrong at the top end:
#
#     fraction   words still glued
#     0.06                     717
#     0.08                     722
#     0.10                     849
#     0.12                   1,977
#     0.14                   5,094
#
# The sample reported 0.14 as the value that split nothing; over the corpus it
# leaves more glued runs than pypdf's 4,168, so it is the one setting that would
# have been worse than not making this change at all. Gluing is the failure that
# destroys a threshold -- a heading that loses its spaces is a heading, a
# `130-139 mm Hg` welded to its neighbor is a number nobody can search for.
#
# 0.10 is kept rather than 0.06. The 132 additional glued runs are the price of a
# threshold that is not tuned to the last measurement, and the three values from
# 0.06 to 0.10 are within a rounding error of each other on a 5.37-million-word
# corpus while 0.12 is already more than double.
SPACE_GAP_FRACTION = 0.10

# An absolute floor in points, for a span whose recorded size is 0 or absurdly
# small. Without it such a span makes the threshold 0 and every character boundary
# becomes a space, which turns one bad span into a page of single letters.
SPACE_GAP_FLOOR = 0.25

# How many inter-character gaps a line needs before its median is trusted as a
# baseline. See `line_baseline` for why a low floor would be worse than none.
MINIMUM_GAPS_FOR_BASELINE = 4

CLASS_GUIDELINE = "guideline"
# USPSTF's document type and nobody else's in this corpus: the 90 USPSTF files each
# title themselves one. #82 built a separate table for exactly that distinction.
CLASS_RECOMMENDATION_STATEMENT = "recommendation-statement"
# A browser print-to-PDF of a web page rather than a published document, which is the
# three ACIP/ files and only those.
CLASS_WEB_CAPTURE = "web-capture"
# For a document that was never read. It is not a guideline; nobody knows what it
# is, and recording it as the default class would let a failure read as a finding.
CLASS_UNKNOWN = "unknown"

#: The vocabulary a document that was **read** can carry, and the one
#: ``reference/guidelines-catalog.md``'s ``class`` column publishes --
#: [#185](https://github.com/mshamblin5150-code/clinical-skills/issues/185), where the
#: two were different sets overlapping on ``guideline`` alone, so every document not
#: classed ``guideline`` answered ``guidelines_search.py --class`` with a certified
#: zero. **The count is stated in ``test_class_vocabulary.py`` and deliberately
#: nowhere else**: it is a fact about a tree that no longer exists and nothing
#: committed re-derives it.
#:
#: **``CLASS_UNKNOWN`` is deliberately not in it.** A document that failed to read has
#: no ``.txt``, so ``guidelines_index.py`` never sees it and no row in the index can
#: carry that value -- and a catalog row that did carry it would be a filter value the
#: index cannot answer, which is the whole defect. It is a manifest value only.
#:
#: **``guidelines_index.UNCLASSIFIED`` is a fourth value the index can carry and this
#: is deliberately not it either.** That one describes a *build* -- a document with no
#: manifest entry at all -- rather than a document, so no catalog row could sensibly
#: hold it. It is named here rather than left to be discovered, and pinned in
#: ``test_class_vocabulary.py``.
#:
#: ``guidelines_catalog.py`` imports this rather than restating it, and
#: ``guidelines_catalog.check_legend`` asserts the catalog's own legend row is this set.
CLASSES = (CLASS_GUIDELINE, CLASS_RECOMMENDATION_STATEMENT, CLASS_WEB_CAPTURE)

# A recommendation statement is a document that titles itself one. The two marks have
# to be *both* present: "Summary of Recommendation Statements" is a table-of-contents
# line in four KDIGO guidelines and in the CDC opioid guideline, and matching the
# phrase alone classes all five wrongly.
#
# Whitespace is squashed before matching because the extraction loses the spaces in
# some of these title blocks: several USPSTF files render the line as
# ``USPreventiveServicesTaskForceRecommendationStatement``.
#
# These live here rather than in ``guidelines_catalog.py``, which is where they were
# written, because the producer owns the vocabulary it emits and the auditor imports
# it. Two copies of a rule that must agree is what #253 cost.
TASK_FORCE_MARK = "taskforce"
RECOMMENDATION_STATEMENT_MARK = "recommendationstatement"

# The three ACIP/ files are browser print-to-PDF captures of CDC schedule pages
# rather than guideline documents, and this header is what says so. The URL and
# the "n of m" folio come with it, but a guideline PDF can carry a repeated URL
# footer -- KDIGO does -- so only the timestamp is allowed to decide.
#
# Anchored at the start of the line and not at both ends, and that survived #83
# for a different reason than it was written for. Under pypdf the page title was
# welded in after the stamp -- "8/12/26, 10:25 AM Recommended Vaccinations for
# Adults | ... | CDC" -- so a whole-line match found none of the three real files.
# Under PyMuPDF the stamp is the entire line, so a whole-line match would now work
# and the front anchor is doing nothing on this corpus.
#
# It stays anyway: a front anchor is the weaker claim, it costs nothing, and the
# next capture whose header the typesetter runs together is not hypothetical --
# this corpus has already produced both layouts from the same three files. What it
# must never become is unanchored: a date and time part way through a sentence is
# prose, and this must not read a guideline as a browser capture.
#
# All three ACIP files re-checked as web-capture under PyMuPDF on 2026-08-19.
# The constant is named for the shape it matches -- a browser print stamp -- and the
# class it decides is named for what the document is. #185 renamed the second and
# deliberately left the first.
PRINT_CAPTURE_STAMP = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*[AP]M\b")

# Characters that are noise or that render as something else, replaced explicitly
# rather than by a normalization form. NFKC would do most of this and would also
# turn a superscript footnote marker into a digit, which next to a threshold reads
# as part of the number.
#
# Written as code points, never as literals. Most of these are invisible and the
# rest are eight dashes nothing in a monospace editor tells apart, so a literal here
# is a constant nobody can review. Each one is asserted by number in
# test_guidelines_extract.py rather than taken on trust.
_DASHES = (
    0x2010, 0x2011,  # hyphen, non-breaking hyphen
    0x2012, 0x2013, 0x2014, 0x2015,  # figure dash, en dash, em dash, horizontal bar
    0x2212, 0x2043,  # minus sign, hyphen bullet
)
_SPACES = (
    0x00A0, 0x1680,  # no-break space, ogham space mark
    *range(0x2000, 0x200B),  # the en quad through hair space family
    0x202F, 0x205F, 0x3000,  # narrow no-break, medium mathematical, ideographic
)
_DELETED = (
    0x00AD,  # soft hyphen: invisible, and splits a word the index needs whole
    0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF,  # zero-width space, joiners, word joiner, BOM
    *range(0x200E, 0x2010), *range(0x202A, 0x202F),  # bidi controls
)
_LIGATURES = {
    0xFB00: "ff",
    0xFB01: "fi",
    0xFB02: "fl",
    0xFB03: "ffi",
    0xFB04: "ffl",
    0xFB05: "st",  # long s with t
    0xFB06: "st",
}
_QUOTES = {
    0x2018: "'", 0x2019: "'", 0x201A: "'", 0x201B: "'", 0x2032: "'",
    0x201C: '"', 0x201D: '"', 0x201E: '"', 0x201F: '"', 0x2033: '"',
}

_TRANSLATION = {
    **{code: "-" for code in _DASHES},
    **{code: " " for code in _SPACES},
    **{code: None for code in _DELETED},
    **_LIGATURES,
    **_QUOTES,
    0x2026: "...",  # horizontal ellipsis
    0x0009: " ",  # tab
}

# Whole ranges that come out empty rather than mapped. The controls are extractor
# debris -- U+0008 turns up after the issue date on every AHA/ACC page. The private
# use areas are icon-font glyphs: a chevron or a padlock, carrying no text at all.
#
# U+000A survives because page_lines splits on it. U+000C does not need to: the page
# separator is written by build_document, not carried through normalize.
_DISCARDED_RANGES = (
    (0x0000, 0x0008), (0x000B, 0x001F), (0x007F, 0x009F),  # C0 and C1, keeping U+000A
    (0xE000, 0xF8FF),  # private use area
    (0xF0000, 0x10FFFF),  # supplementary private use areas A and B
)
_DISCARDED = re.compile(
    "[" + "".join(f"{re.escape(chr(lo))}-{re.escape(chr(hi))}" for lo, hi in _DISCARDED_RANGES) + "]"
)

_WHITESPACE = re.compile(r"[ \t]+")


def normalize(text: str) -> str:
    """One page of extracted text, with its typography made searchable.

    Every mapping here is deliberate and none of them touch a character a
    threshold is written with: the comparison operators, the degree sign, the micro
    sign and the plus-minus sign all pass through untouched, with a test for each.
    """
    text = _DISCARDED.sub("", text.translate(_TRANSLATION))
    text = unicodedata.normalize("NFC", text)
    return _WHITESPACE.sub(" ", text).strip()


def page_lines(page_text: str) -> list[str]:
    """A page as its non-empty normalized lines.

    Blank lines are dropped rather than kept, because a blank line matches every
    other blank line: left in, ``""`` is the most frequent line in every document
    and therefore boilerplate in all of them.
    """
    return [line for line in (normalize(raw) for raw in page_text.splitlines()) if line]


def clean_pages(raw_pages: list[str]) -> list[list[str]]:
    return [page_lines(page) for page in raw_pages]


def sample_indexes(page_count: int) -> list[int]:
    """Which pages the boilerplate rule looks at. Evenly spaced, or all of them."""
    size = max(SAMPLE_SIZE, MINIMUM_SAMPLE)
    if page_count <= size:
        return list(range(page_count))
    step = page_count / size
    return sorted({int(index * step) for index in range(size)})


def repeated_keys(pages: list[list[str]], key_of) -> list[str]:
    """Whatever ``key_of`` yields on 75% or more of this document's sampled pages.

    Both rules are this function; only the key differs. ``find_boilerplate`` keys a
    line by itself and ``find_margin_patterns`` keys it by its masked form, and
    keeping the tally in one place is what stops the two bars drifting apart --
    there is one ``floor`` expression rather than a copy per rule.

    ``key_of(position, line, page_length)`` returns the key to count, or None to
    ignore the line. It is passed the position because #100's rule is about where
    on the page a line sits, which a line alone cannot answer.

    Sorted, because the result is recorded in a manifest that gets diffed across
    rebuilds and set iteration order would make every rebuild look like a change.
    """
    sampled = sample_indexes(len(pages))
    if not sampled:
        return []
    counts: dict[str, int] = {}
    for index in sampled:
        page = pages[index]
        # A page votes once per distinct key. Otherwise a two-column page whose
        # column headers repeat reads as two pages' worth of evidence, and a folio
        # set at both the head and the foot of one page reads as two.
        seen: set[str] = set()
        for position, line in enumerate(page):
            key = key_of(position, line, len(page))
            if key is None or key in seen:
                continue
            seen.add(key)
            counts[key] = counts.get(key, 0) + 1
    floor = max(MINIMUM_OCCURRENCES, BOILERPLATE_THRESHOLD * len(sampled))
    return sorted(key for key, count in counts.items() if count >= floor)


def find_boilerplate(pages: list[list[str]]) -> list[str]:
    """The lines this document repeats on 75% or more of its sampled pages."""
    return repeated_keys(pages, lambda _position, line, _length: line)


def mask_digits(line: str) -> str:
    """A line with each run of digits replaced by a single mask character.

    Runs rather than digits, so ``S37`` and ``S8`` land on the same pattern.
    """
    return _DIGIT_RUN.sub(DIGIT_MASK, line)


def in_margin(position: int, page_length: int) -> bool:
    """Whether a line sits within ``MARGIN_LINES`` of either end of its page.

    On a page short enough for the two margins to overlap, every line is a
    margin line. That is the right answer rather than an edge case: a page with
    four lines on it has no middle for a table to sit in.
    """
    return position < MARGIN_LINES or position >= page_length - MARGIN_LINES


def find_margin_patterns(pages: list[list[str]]) -> list[str]:
    """The masked line patterns this document repeats in its page margins.

    #100's rule. A line is counted only if it **carries a digit**: without that,
    a line that masks to itself would be tallied on margin-only evidence the
    literal rule never saw, and a typeset ``Table #`` would join the family
    ``Table 5`` makes.

    Same threshold and same floor as the literal rule, because it is the same
    function underneath -- see ``repeated_keys``.
    """
    return repeated_keys(
        pages,
        lambda position, line, length: (
            mask_digits(line)
            if in_margin(position, length) and _DIGIT_RUN.search(line)
            else None
        ),
    )


def _matches_margin_pattern(line: str, position: int, page_length: int,
                            patterns: set[str]) -> bool:
    """Whether this line, *here on this page*, is one the margin rule takes.

    The position test is repeated on the way out and that is the safety property
    rather than belt-and-braces: a pattern that cleared from a folio in a margin
    would otherwise match the same digits mid-page, where they are a table cell.
    The digit test is repeated for ``find_margin_patterns``' reason -- a typeset
    ``Table #`` masks to itself and must not be taken by the family ``Table 5``
    makes.
    """
    return (
        bool(patterns)
        and in_margin(position, page_length)
        and bool(_DIGIT_RUN.search(line))
        and mask_digits(line) in patterns
    )


def strip(
    pages: list[list[str]],
    boilerplate: list[str],
    margin_patterns: list[str] | tuple[str, ...] = (),
) -> list[list[str]]:
    """Every page with the boilerplate lines removed, and no page removed.

    Two rules, and the second one is **restricted to the margins on the way out
    as well as on the way in.** That restriction is the whole safety property:
    ``KDIGO-2021-Blood-Pressure`` sets ``S37`` at the foot of 87 pages and lists
    ``S3`` and ``S7`` mid-page on its contents page, and the two mask to the same
    pattern. Stripping the pattern page-wide would clear the contents page and
    record it as boilerplate removal.
    """
    removed = set(boilerplate)
    patterns = set(margin_patterns)
    kept = []
    for page in pages:
        length = len(page)
        kept.append([
            line
            for position, line in enumerate(page)
            if line not in removed
            and not _matches_margin_pattern(line, position, length, patterns)
        ])
    return kept


def margin_removals(
    pages: list[list[str]],
    boilerplate: list[str],
    margin_patterns: list[str] | tuple[str, ...],
) -> list[str]:
    """The exact lines the margin rule takes, sorted and deduplicated.

    The manifest's contract is that a removal can be read back rather than
    believed, and a masked pattern cannot be read back -- it names a family, not
    a line. A line the literal rule already claimed is left out, so the two
    records do not both bill for it.
    """
    already = set(boilerplate)
    patterns = set(margin_patterns)
    taken: set[str] = set()
    for page in pages:
        length = len(page)
        for position, line in enumerate(page):
            if line not in already and _matches_margin_pattern(line, position, length, patterns):
                taken.add(line)
    return sorted(taken)


def squash(text: str) -> str:
    """Whitespace out, lowercase, for matching a title block the extraction glued."""
    return re.sub(r"\s+", "", text).lower()


def is_recommendation_statement(title_block: str) -> bool:
    """Whether a title block says the document is a USPSTF recommendation statement.

    Shared with ``guidelines_catalog.classify`` by import rather than by copy, so the
    producer and the auditor cannot come to hold different answers.
    """
    squashed = squash(title_block)
    return TASK_FORCE_MARK in squashed and RECOMMENDATION_STATEMENT_MARK in squashed


def classify(pages: list[list[str]]) -> str:
    """Which of ``CLASSES`` this document is.

    **Ordered, and the order matters**: a browser capture of a page that happens to say
    "recommendation statement" is still a capture. ``guidelines_catalog.classify`` has
    always read the two in that order and this adopts it.

    The capture test is counted over the sampled pages directly rather than read off
    the boilerplate set. Those look interchangeable on the three real captures, where
    the stamp is on every page and clears every bar -- but reading the boilerplate set
    makes the class a side effect of boilerplate detection, so a capture short enough
    to trip MINIMUM_OCCURRENCES, or one whose stamp missed the threshold by a page,
    would come back a guideline with nothing saying otherwise.

    **The recommendation-statement test reads the first page only**, which is where the
    document titles itself, and it runs here rather than in ``guidelines_catalog.py``
    alone because #185 ruled the producer's vocabulary is the catalog's. Running the
    catalog's classifier over the extracted ``.txt`` corpus reproduces 90
    recommendation statements and 86 guidelines exactly and misses all three captures
    -- because the stamp it keys on is boilerplate and has been stripped by then. This
    sees the pages **before** stripping, which is why both halves can live here and
    neither could live there.
    """
    sampled = sample_indexes(len(pages))
    if not sampled:
        return CLASS_GUIDELINE
    stamped = sum(
        1
        for index in sampled
        if any(PRINT_CAPTURE_STAMP.match(line) for line in pages[index])
    )
    if stamped >= BOILERPLATE_THRESHOLD * len(sampled):
        return CLASS_WEB_CAPTURE
    if pages and is_recommendation_statement(" ".join(pages[0])):
        return CLASS_RECOMMENDATION_STATEMENT
    return CLASS_GUIDELINE


@dataclass(frozen=True)
class Record:
    """One document's manifest entry. ``output`` is None exactly when it failed.

    Everything but ``doc_id`` defaults to the nothing-was-read state, so a failure
    is ``Record(doc_id=..., error=...)`` and a field added later does not have to
    be spelled out twice in two constructors that must not disagree.

    ``doc_id``, ``society``, ``title`` and ``document_class`` are the four fields
    #84's indexer reads (`tools/guidelines_index.py`), and ``doc_id`` is the key it
    matches a document by. The rest is this tool's own audit trail. A failed
    document still gets an entry with a ``doc_id``: the indexer reports a manifest
    entry it found no text for on stderr, which is exactly this tool's recorded
    extraction failure surfacing rather than a silent skip on either side.
    """

    doc_id: str
    society: str | None = None
    title: str | None = None
    source: str = ""
    output: str | None = None
    document_class: str = CLASS_UNKNOWN
    pages: int = 0
    empty_pages: int = 0
    chars: int = 0
    chars_stripped: int = 0
    sampled_pages: int = 0
    codec: str = OUTPUT_CODEC
    boilerplate: list[str] = field(default_factory=list)
    # #100's rule, recorded as two fields rather than folded into ``boilerplate``.
    # The pattern says which rule fired; the literals say what actually left the
    # page. Neither alone can be read back: a pattern names a family, and a list
    # of 140 folios does not say why they went. ``boilerplate`` keeps its meaning
    # so a manifest diff across the change shows the new rule rather than a
    # reshuffle of the old one.
    margin_patterns: list[str] = field(default_factory=list)
    margin_stripped: list[str] = field(default_factory=list)
    error: str | None = None


def document_id(relative: Path) -> str:
    """The key #84 matches a document by: the relative path, no suffix, posix.

    Its first segment is the society, which is how a hit names a file that can be
    opened beside the PDF of the same name.
    """
    return relative.with_suffix("").as_posix()


def society_of(doc_id: str) -> str | None:
    return doc_id.split("/")[0] if "/" in doc_id else None


def build_document(
    relative: Path, raw_pages: list[str], out_root: Path, title: str | None = None
) -> Record:
    """Normalize, strip, write one text file, and describe what was done to it."""
    pages = clean_pages(raw_pages)
    boilerplate = find_boilerplate(pages)
    margin_patterns = find_margin_patterns(pages)
    kept = strip(pages, boilerplate, margin_patterns)
    margin_stripped = margin_removals(pages, boilerplate, margin_patterns)
    # Only the patterns that actually took a line are recorded. Most of them do
    # not: `(c) 2021 American Medical Association` clears the margin rule on 68
    # USPSTF files and the literal rule has already removed every one of its
    # members, because within one document the year does not vary. Recording the
    # pattern anyway put 168 of 195 entries in the manifest against no removal at
    # all, which reads as a rule doing seven times the work it does.
    fired = sorted({mask_digits(line) for line in margin_stripped})

    chars = sum(len(line) for page in pages for line in page)
    chars_kept = sum(len(line) for page in kept for line in page)

    destination = out_root / relative.with_suffix(".txt")
    destination.parent.mkdir(parents=True, exist_ok=True)
    body = ("\n" + PAGE_SEPARATOR + "\n").join("\n".join(page) for page in kept)
    destination.write_text(body + "\n", encoding=OUTPUT_CODEC, newline="\n")

    doc_id = document_id(relative)
    return Record(
        doc_id=doc_id,
        society=society_of(doc_id),
        title=title,
        source=relative.as_posix(),
        output=relative.with_suffix(".txt").as_posix(),
        document_class=classify(pages),
        pages=len(pages),
        empty_pages=sum(1 for page in pages if not page),
        chars=chars,
        chars_stripped=chars - chars_kept,
        sampled_pages=len(sample_indexes(len(pages))),
        codec=OUTPUT_CODEC,
        boilerplate=boilerplate,
        margin_patterns=fired,
        margin_stripped=margin_stripped,
        error=None,
    )


def failed_document(relative: Path, error: str) -> Record:
    """A document that could not be read. Recorded, never skipped."""
    doc_id = document_id(relative)
    return Record(
        doc_id=doc_id,
        society=society_of(doc_id),
        source=relative.as_posix(),
        error=error,
    )


def line_baseline(glyphs: list[tuple[dict, float]]) -> float:
    """The gap this line calls "no gap at all" -- its median inter-character gap.

    **This is what tells letter-spaced type from a word break, and nothing else
    can.** A typesetter who tracks a heading out widens *every* gap on the line, so
    an absolute threshold sees them all as word breaks. Measured on
    KDIGO-2024-CKD-Guideline p.3, the section header ``contents``:

        gaps 1.48 1.48 1.48 1.48 1.48 1.48 1.48   median 1.475   spread 0.00

    against a genuinely glued USPSTF line on the same rule:

        median -0.036   max 1.145   spread 1.181

    Tracking shifts the whole distribution; a word break is an **outlier within**
    it. So the gap that matters is the excess over the line's own median, and
    ``contents`` stops becoming ``c o n t e n t s``.

    Measured over all 179 documents and all 7,733 pages, 2026-08-16 -- against the
    absolute rule it recovers 4,285 more words, leaves 130 fewer glued runs, and
    wrongly splits 1,694 fewer words. It is better on every axis, which is why it
    replaced the absolute rule outright rather than being offered as an option.

    **The floor of 4 gaps is not decoration.** A median over one or two gaps is the
    gap itself, which would make the excess 0 and suppress every split on short
    lines -- and a two-word line is exactly where a lost space is unrecoverable
    from context. Below the floor the rule degrades to the absolute one.
    """
    gaps = [
        glyphs[index][0]["bbox"][0] - glyphs[index - 1][0]["bbox"][2]
        for index in range(1, len(glyphs))
    ]
    if len(gaps) < MINIMUM_GAPS_FOR_BASELINE:
        return 0.0
    return statistics.median(gaps)


def span_baselines(line: dict) -> list[float]:
    """One baseline per span, falling back to the line's and then to nothing.

    **Per span, because a line's spans do not share metrics, and taking the median
    across them measures nothing.** Found by rendering a page and looking at it
    rather than by any text metric. The running footer of
    KDIGO-2009-Transplant-Recipient-Guideline-English.pdf --

        American Journal of Transplantation 2009; 9 (Suppl 3): Si-Si

    -- is a single line of three spans, all Univers-Light 9 pt. The first 35
    characters are set with negative tracking and measure -1.38 between glyphs; the
    last 24 are set normally and measure 0.00. The line median is -1.38, so every
    0.00 gap in the third span reads as an excess of +1.38 against a threshold of
    0.90, and the rebuild split **every character of it**:

        American Journal of Transplantation 2 0 0 9 ; 9 ( S u p p l 3 ) : S i - S i

    That one footer is the largest single source of damage in the corpus. **The
    figures live in this module's own docstring and are deliberately not restated
    here** -- 142 of the 306 letter-spaced splits and 142 of the 390 digit-breaks,
    284 of 696 in all. This paragraph carried its own copy, taken before the fix
    below landed, and so went on quoting the pre-fix 349 and 762 in the present
    tense inside the docstring of the function that changed them. #143's shape,
    one scroll apart.

    The fallback order matters. A span too short for its own median borrows the
    line's, which is right where a line is one typeface broken into spans by a bold
    word; and a line too short for that gets 0.0, which is the absolute rule.
    """
    glyphs_by_span = [
        [(char, span.get("size", 0.0)) for char in span.get("chars", ())]
        for span in line.get("spans", ())
    ]
    whole_line = [pair for span in glyphs_by_span for pair in span]
    fallback = line_baseline(whole_line)
    return [
        line_baseline(span) if len(span) > MINIMUM_GAPS_FOR_BASELINE else fallback
        for span in glyphs_by_span
    ]


def rebuild_text(raw: dict) -> str:
    """One page of PyMuPDF ``rawdict`` as text, with word spacing recovered.

    **Takes the dictionary rather than the page**, so every rule in here is
    exercisable from a literal in a test file and the suite still never opens a
    PDF. That is the same line ``test_guidelines_extract.py`` already draws around
    the ``.txt`` excerpts in ``tools/testdata/``.

    The rule is one comparison: a horizontal gap wider than ``SPACE_GAP_FRACTION``
    of the span's font size is a word boundary. Everything around it is guarding
    against inserting a space next to one that is already there -- a PDF that sets
    real space glyphs and one that positions glyphs with no spaces at all are both
    common, and a document may do both on the same page.

    Blocks whose ``type`` is not 0 are images and carry no characters. Lines come
    back in PyMuPDF's reading order and are joined with newlines, because
    ``page_lines`` splits on them and the boilerplate rule counts whole lines.
    """
    lines: list[str] = []
    for block in raw.get("blocks", ()):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", ()):
            baselines = span_baselines(line)
            if not baselines:
                continue
            buffer: list[str] = []
            previous_right: float | None = None
            for index, span in enumerate(line.get("spans", ())):
                size = span.get("size", 0.0)
                baseline = baselines[index]
                threshold = max(SPACE_GAP_FRACTION * size, SPACE_GAP_FLOOR)
                for char in span.get("chars", ()):
                    glyph = char["c"]
                    left, _, right, _ = char["bbox"]
                    gap_is_wide = (
                        previous_right is not None
                        and (left - previous_right) - baseline > threshold
                    )
                    # Never two spaces, and never a space before one the PDF set
                    # itself: `buffer[-1] != " "` covers the first and
                    # `glyph != " "` the second. Without them a document with real
                    # space glyphs AND wide inter-word gaps -- which is most of
                    # AHA/ACC -- comes back double-spaced, and `normalize`
                    # collapsing runs of spaces would hide that rather than make
                    # it correct.
                    if gap_is_wide and glyph != " " and buffer and buffer[-1] != " ":
                        buffer.append(" ")
                    buffer.append(glyph)
                    previous_right = right
            lines.append("".join(buffer))
    return "\n".join(lines)


def extract_pages(path: Path) -> tuple[list[str], str | None]:
    """Every page of a PDF as raw text in reading order, and its embedded title.

    A page that raises comes back as an empty string rather than taking the
    document down with it -- the manifest counts it, and one unreadable page in a
    250-page report is not a failed extraction.

    The title is ``/Title`` verbatim, or None. **Verbatim and unfiltered**: 147 of
    the 179 carry one and they are real guideline titles, measured 2026-08-12, but
    the rest include the usual ``Microsoft Word - ...`` debris. Inventing a
    junk-detection heuristic here would put an unreviewable rule between the PDF
    and the record; curating them is the catalog's job (#81).
    """
    import pymupdf  # imported here so the pure functions above stay importable without it

    document = pymupdf.open(str(path))
    pages = []
    for page in document:
        try:
            pages.append(rebuild_text(page.get_text("rawdict")))
        except Exception:  # noqa: BLE001 - any per-page failure degrades to an empty page
            pages.append("")

    try:
        title = ((document.metadata or {}).get("title") or "").strip() or None
    except Exception:  # noqa: BLE001 - a broken metadata dictionary is not a failed read
        title = None
    document.close()
    return pages, title


def _engine_version() -> str:
    try:
        import pymupdf

        return f"pymupdf {pymupdf.__version__}"
    except ImportError:
        return "pymupdf (not installed)"


def require_pymupdf() -> None:
    """Fail once, up front, rather than 179 times.

    Every per-document failure is caught and recorded, which is what #80 asks for
    -- so without this an uninstalled ``pymupdf`` reads as 179 unreadable PDFs and a
    manifest full of identical ImportErrors, next to a summary line cheerfully
    reporting the engine as not installed.
    """
    try:
        import pymupdf  # noqa: F401
    except ImportError:
        raise SystemExit(
            "pymupdf is not installed. This is one of the tools in tools/ that is "
            "not stdlib, because it reads a PDF:\n"
            "    python -m pip install pymupdf"
        ) from None


def _extract_one(job: tuple[Path, Path, Path]) -> Record:
    """One document, end to end. Top level because a pool has to pickle it.

    The whole per-document pipeline runs in the worker, writing its own ``.txt``,
    so nothing but the finished ``Record`` crosses back. Documents never share an
    output path -- it is derived from the source path -- so there is no ordering
    hazard in the writes, and the manifest is assembled in source order by the
    parent from results the pool returns in order.
    """
    source_root, relative, out_root = job
    try:
        raw_pages, title = extract_pages(source_root / relative)
        return build_document(relative, raw_pages, out_root, title)
    except Exception as error:  # noqa: BLE001 - a failure is recorded, never skipped
        return failed_document(relative, f"{type(error).__name__}: {error}")


def orphaned_outputs(out_root: Path, records: list[Record]) -> list[Path]:
    """Text files under the output root that no record in this run claims.

    A re-run overwrites what it writes and knows nothing about what it wrote last
    time, so renaming a source file leaves its old ``.txt`` behind. #84 will index
    the directory, not the manifest, and would pick the stale copy up.
    """
    claimed = {(out_root / record.output) for record in records if record.output}
    return sorted(path for path in out_root.rglob("*.txt") if path not in claimed)


def write_manifest(out_root: Path, records: list[Record], source_root: Path) -> Path:
    """The audit trail, and #84's input. One entry per document, in source order.

    ``documents`` is the **list of entries**, which is the shape
    ``guidelines_index.read_manifest`` requires -- it does ``data.get("documents")``
    and raises unless what comes back is a list. The run totals live under
    ``totals`` for that reason: ``"documents": 179`` as a count read as a manifest
    of the wrong shape, and the indexer raised rather than indexing 179 documents
    with no title, society or class. That refusal is the contract working.
    """
    manifest = {
        "source": str(source_root),
        "codec": OUTPUT_CODEC,
        "engine": _engine_version(),
        "boilerplate_threshold": BOILERPLATE_THRESHOLD,
        "minimum_occurrences": MINIMUM_OCCURRENCES,
        "margin_lines": MARGIN_LINES,
        "totals": {
            "documents": len(records),
            "failures": sum(1 for record in records if record.error),
            "pages": sum(record.pages for record in records),
            "chars": sum(record.chars for record in records),
        },
        "documents": [asdict(record) for record in records],
    }
    path = out_root / MANIFEST_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding=OUTPUT_CODEC,
        newline="\n",
    )
    return path


def default_output(source: Path) -> Path:
    """A sibling of the source directory, never a child of the repo."""
    name = source.name
    stem = name[: -len("-src")] if name.endswith("-src") else name
    return source.parent / f"{stem}-text"


def check_outside_repo(out_root: Path) -> None:
    """Refuse an output directory inside any git checkout, not just this one.

    ``REPO_ROOT`` alone is not enough. Run from a worktree it is the worktree, so
    it says nothing about the main clone's ``reference/`` -- and that is one of the
    two directories #80 names by name. Walking up for a ``.git`` entry catches the
    main clone, every sibling worktree, and any other repo the maintainer keeps
    nearby. A worktree's ``.git`` is a file rather than a directory, so this tests
    for existence and not for a directory.
    """
    resolved = out_root.resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / ".git").exists():
            raise SystemExit(
                f"refusing to write inside a git checkout: {resolved}\n"
                f"  {candidate} is a repository.\n"
                "Tracked files are materialized in every worktree and gitignored ones "
                "are copied into every worktree. Pick a directory outside it."
            )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="directory holding the guideline PDFs")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory, outside the repo (default: a sibling of <source>)",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="summary only, no per-document line"
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=0,
        help="worker processes (default: one per CPU; 1 runs in this process)",
    )
    args = parser.parse_args(argv)

    if not args.source.is_dir():
        raise SystemExit(f"not a directory: {args.source}")
    require_pymupdf()

    source_root = args.source.resolve()
    out_root = (args.out or default_output(source_root)).resolve()
    check_outside_repo(out_root)

    pdfs = sorted(source_root.rglob("*.pdf"), key=lambda p: p.relative_to(source_root).as_posix())
    if not pdfs:
        raise SystemExit(f"no PDFs under {source_root}")

    jobs = [(source_root, path.relative_to(source_root), out_root) for path in pdfs]
    workers = args.jobs if args.jobs > 0 else (os.cpu_count() or 1)
    workers = max(1, min(workers, len(jobs)))

    records: list[Record] = []

    def collect(results: Iterable[Record]) -> None:
        for record in results:
            records.append(record)
            if not args.quiet:
                # `use_utf8` in `__main__` is what keeps a society directory or a
                # file name outside cp1252 from taking the run down at the print,
                # having already done the work. This used to encode by hand through
                # `sys.stdout.buffer`, which did the same job for this one line and
                # left every other print in the file exposed -- including
                # `record.error` on the failure path, where the reporting is what
                # dies. Issue #150.
                #
                # The trade is real and worth naming: that hand-rolled line protected
                # itself wherever it ran, and this one is protected by the entry
                # point, so an in-process caller of `main` no longer gets it. There
                # is no such caller, `sys.stdout.buffer` does not exist on the
                # `StringIO` a test would redirect into, and one mechanism for the
                # whole file beats one line that was safe alone. `flush` stays: that
                # is progress output over 179 documents, and nothing to do with
                # encoding -- and it matters more now, because with a pool the lines
                # arrive in bursts as the in-order `map` releases completed work.
                print(f"  {record.source}", flush=True)

    # `map` yields in submission order, so the manifest stays in source order and a
    # rebuild diffs clean against the last one rather than reordering on every run.
    #
    # Serial when workers == 1, and that is a real branch rather than a pool of one:
    # a single-worker pool is all of the overhead and none of the benefit, and it is
    # the mode a traceback out of `extract_pages` is readable in.
    if workers == 1:
        collect(_extract_one(job) for job in jobs)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            collect(pool.map(_extract_one, jobs))

    manifest = write_manifest(out_root, records, source_root)

    failures = [record for record in records if record.error]
    # Every class, not only the captures. Since #185 this is the vocabulary
    # `reference/guidelines-catalog.md` publishes and `guidelines_search.py --class`
    # filters on, so the breakdown is the one command that re-derives the figures
    # CLAUDE.md states -- and a class that fell to zero is visible rather than
    # implied by the one that did not.
    #
    # `CLASS_UNKNOWN` is counted here and is deliberately outside `CLASSES`, because a
    # breakdown that did not sum to the document count would be a line inviting the
    # reader to work out the difference -- and the missing term would be exactly the
    # documents that failed to read. It prints only when it is non-zero, so an ordinary
    # run is not given a column for a class it does not have.
    counted = {cls: sum(1 for r in records if r.document_class == cls) for cls in CLASSES}
    unread = sum(1 for r in records if r.document_class == CLASS_UNKNOWN)
    if unread:
        counted[CLASS_UNKNOWN] = unread
    breakdown = ", ".join(f"{n} {cls}" for cls, n in counted.items())

    print()
    print(f"source      {source_root}")
    print(f"output      {out_root}")
    print(f"engine      {_engine_version()}, codec {OUTPUT_CODEC}")
    print(f"documents   {len(records):,}  ({breakdown})")
    print(
        f"pages       {sum(r.pages for r in records):,}  "
        f"({sum(r.empty_pages for r in records):,} with no text layer)"
    )
    print(
        f"chars       {sum(r.chars for r in records):,}  "
        f"({sum(r.chars_stripped for r in records):,} stripped as boilerplate)"
    )
    print(
        f"boilerplate {sum(1 for r in records if r.boilerplate):,} of {len(records):,} "
        "documents carry a page-repeated line"
    )
    # Reported separately rather than folded into the line above. The two rules
    # overlap on most documents, so one combined count would say nothing about
    # what #100's rule adds -- and what it adds is the whole reason it exists.
    print(
        f"margins     {sum(1 for r in records if r.margin_patterns):,} of {len(records):,} "
        f"documents carry a page-repeated line once its digits are masked, within "
        f"{MARGIN_LINES} line(s) of a page edge"
    )
    print(
        f"            {sum(len(r.margin_stripped) for r in records):,} distinct line(s) "
        "removed by that rule and not by the one above"
    )
    unstripped = [r for r in records if r.output and not r.boilerplate and not r.margin_patterns]
    print(f"            {len(unstripped):,} document(s) had nothing stripped by either rule")
    print(f"manifest    {manifest}")

    orphans = orphaned_outputs(out_root, records)
    if orphans:
        print()
        print(f"ORPHANED {len(orphans)} text file(s) no source in this run claims.")
        print("Left in place deliberately -- delete them yourself once you have looked:")
        for path in orphans:
            print(f"  {path.relative_to(out_root).as_posix()}")

    if failures:
        print()
        print(f"FAILED {len(failures)}:")
        for record in failures:
            print(f"  {record.source}: {record.error}")
        return 1
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
