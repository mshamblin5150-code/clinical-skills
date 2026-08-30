"""Extract per-page text from the guideline PDF corpus and strip page-repeated boilerplate.

phi-scan: synthetic

The pragma is here because PRINT_CAPTURE_STAMP's comment quotes the browser print
header off a public CDC page, and that header is date-shaped. Writing it in pieces
to slip past the scanner would dodge the rule without declaring anything. The
corpus layer is untouched by this and still applies.

    python tools/guidelines_extract.py <source-directory> [--out <directory>]

``<source-directory>`` is the corpus as downloaded: one subdirectory per society,
PDFs inside. It lives outside this repo and stays there -- most
of them society-copyrighted. Issue #87 rules on that and is not reopened here.

**Nothing this writes goes inside the repo, and the script refuses to.** Output
defaults to a sibling of the source directory (``guidelines-src`` next door becomes
``guidelines-text``). ``reference/`` and ``scratch/`` are both wrong for it for the
same reason: tracked files are materialized in every worktree and gitignored ones
are copied into every worktree. **How many are live is deliberately not stated** --
it moves on every ``git worktree add``, nothing re-derives it, and this sentence
held ``six`` while its twin in ``guidelines_index.py`` held it too and ``CLAUDE.md``
said twelve. #143, and the argument survives the figure intact: *every* worktree
gets a copy, so one is one too many.

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

The dated reader comparison and the four unrecoverable rows of its five-bucket
classification live once in ``ORPHANED_FIGURES``. They are not restated in this
docstring because #404 deletes their producers: every row was measured before
#178's second bar and #172's operator repair.

**These figures replace a 14-document, 4-page-each sample, and the sample was
wrong in a way worth recording.** It reported 117 glued for pypdf against 4,168,
and it reported the splitting cost as *"11 words out of 11,522 distinct"* when the
corpus figure is three orders of magnitude larger. Worse, the tuning table it
produced said 0.14 wrongly split nothing; over the whole corpus 0.14 leaves 5,094
glued runs, which is **worse than the library it replaced**. A reader trusting that
table would have picked the one value that loses to pypdf. #83 published it, and it
was caught by being asked to read every document rather than a selection.

**Historical measurement, 2026-08-16.** The old ``wrongly split`` figure was a set
difference produced by the now-deleted ``reader_compare.py``. The five-bucket
classifier genuinely was never saved. ``split_census.py`` owns the historical shape
figures that still have evidence and consumes this module's current glyph generator;
its current result is therefore a new measurement, not a restatement of that table.

**The historical safety reading covered only the 390 ``digit|digit`` breaks.** Every
distinct run in that narrow population was citation apparatus. It did not examine
decimal-and-comma-adjacent shapes, which are how a dose such as ``0.5`` breaks. The
continuous census now records all five digit-adjacent boundary classes and every
quantity-shaped split per document, then prints the corpus totals, distinct shapes,
and a finding on every extraction refresh.

**The historical classification is pre-#178 and is left as it was measured.** In that classification,
284 of the 696 were
one running footer in one document, and that footer is fixed below; the table is not
restated against the new extraction because the classifier that produced its five
buckets was never saved. The exact re-derivable partition lives in
``split_census.py`` and ``ORPHANED_FIGURES`` rather than as a third prose copy.
Reasonable bucket rules put ``letter-spaced word`` anywhere from 128 to 466. What
replaces the table is the measured delta in the next paragraphs, which does
re-derive from this module's own functions.

**That footer is fixed -- #178.**
``KDIGO-2009-Transplant-Recipient-Guideline-English.pdf`` carries

    American Journal of Transplantation 2009; 9 (Suppl 3): S6-S9

on every page. ``span_baselines`` fixed the 16 pages where it is set as three spans
and **not the 142 where it is one**: there the whole footer is a single
Univers-Light span whose per-glyph gaps run from -2.35 to 0.00 around a median of
-1.36, so the top of its own spread clears any fixed offset from that median. Heavy
and highly variable negative bearings, not tracked type, and no median-plus-offset
rule separates the two.

**What separates them is that the line already carries real space glyphs**, which
is the lead #178 named and ``SPACE_ADVANCE_FRACTION`` is. The PDF has already said
where that line's words are -- 1.056 pt across one of its own spaces, against the
0.003 pt gaps that were being split -- so a candidate gap is measured against what
this line charges for a word break rather than against the font size alone. The
constraint the ticket names is met and is measured rather than asserted: **"the
line has a space, infer nothing" is too blunt**, because 12,003 of the corpus's
inferences are made on lines that already carry one -- USPSTF sets a real space
after a bullet and glues the words after it anyway -- and the great majority are
correct. So the rule is a floor on the gap, never a veto on the line.

**Corpus-wide it removes 2,809 inferences and creates no glued run**, measured over
all 179 documents and all 7,733 pages, 2026-08-19, by running this module's own
``rebuild_text`` twice. All 2,809 were read and fall across **five** documents:
2,741 are that footer, 33 are letter-spaced runs in ``ADA/standards-of-care-2026``
and 33 in the CDC opioid MMWR, and the last two are one each in the ACIP captures
and are a space after an opening bracket rather than letter-spacing. The footer's surviving lines in the
extracted text fall from **159 to 11, and the 142 letter-split ones to 0**; the 11
are the roman-numeral front-matter pages, which the margin rule cannot reach by
design and which stay.

**The CDC opioid MMWR extracted page 27 is repaired.** Its one span holds normally
spaced prose on both sides of a middle compressed by roughly 3 pt, so one median
made the ordinary letter gaps look like word breaks. ``glyph_baselines`` lets the
real space glyphs bound those regimes, and the line now reads as plain text. A
same-source comparison over all 179 documents changes exactly two lines, both in
that MMWR and both visibly repaired, removing 40 false spaces in all. The generic
version was rejected because it erased real evidence-table footnote spaces in
IDSA; the measured font boundary and its reason live on
``LOCAL_SPACING_BASELINE_FONTS``.

**And the footer is boilerplate that should never have reached a reader**: its page
range varies per page, so the 75% rule never strips it. #178 read that as #100's
cause 1 and expected #100 to remove the damage without touching the space rule.

**#100 landed and it did not, and the reason was #178's own subject.** The
letter-spacing damage set every digit as its own run, so the page range masked to a
different pattern depending on how many digits it had: ``S # - S #`` on one page and
``S # # - S # #`` on the next. The footer produced **8 distinct masked patterns**
across 32 sampled pages, the largest reaching 16, against a floor of 24 -- so
nothing cleared and all 166 lines stayed. Measured 2026-08-16.

**So the two had to meet, and they have.** With the spacing fixed the footer
extracts identically on every arabic-folio page, the margin rule sees one repeated
line, and ``American Journal of Transplantation #; # (Suppl #): S#-S#`` is a
recorded margin pattern for the first time. That document's ``chars_stripped`` goes
from 516 to 9,793, and the corpus's margin rule from 2,649 distinct lines to 2,688
-- **the 39 added are all that one footer and nothing was removed anywhere**.
Measured 2026-08-19. The dependency ran the other way round from the one #178
stated: the space rule had to be fixed first.

The trade favors the body over the front matter, which is the right way round: what
splits is display type in headings and reference lists, and what is repaired is
running prose, where a threshold lives.

**Fonts that lie about their own encoding, and the one thing that settles it.**
#172. A comparison operator set in ``AdvPS_SSYB`` or in three slots of ``SymbolMT``
comes back as a pound sign, a double dagger or a C0 control code, from ``pypdf``
and PyMuPDF alike -- the mis-encoding is in the PDF, not in either reader.
``rebuild_text`` repairs those slots, and it is the only place that can: it is the
last function here that knows what typeface a character was set in. See
``SYMBOL_FONT_OPERATORS`` for the table, the evidence and the counts.

**The evidence is the rendered page, because the PDF offers nothing else.**
``GMBEDM+AdvPS_SSYB`` declares ``/Encoding /WinAnsiEncoding``, a text encoding on a
symbol font; it ships no ``ToUnicode``; and its embedded CFF subset names its two
glyphs ``sterling`` and ``daggerdbl``. All three statements are false, so the page
had to be rasterized and looked at -- ``span_baselines``'s method, for
``span_baselines``'s reason, and the second time in this file that a rendered page
found what no text metric could.

**Keyed on the font, which is what makes it a decoding fix rather than a
heuristic.** #172 proposed a unit-aware rule over the text -- a pound sign, a
number, a clinical unit -- and this repo does not rewrite source text on a guess.
It does not have to: the corpus's two genuine currency figures are set in an
ordinary text face and are untouched *by construction*. The clinician ruled the
substitution on 2026-08-19 on that basis.

**One font needs the rendered glyph as well as its name.** #282 found that
``MathematicalPi-One`` assigns the same character slots to opposite comparison
operators in different USPSTF documents. A ticket comment proposed the embedded
glyph ID as a stable identity; the 2026-08-20 full-corpus check falsified it -- the
same ID renders opposite operators in different subsets. ``rawdict`` and
``get_texttrace`` therefore cannot decode this font. The extractor clips each known
slot from the rendered page and reads the direction of its upper stroke, with a
center margin that refuses an ambiguous shape and leaves it in the census.

**And the ticket was understated threefold by looking at the wrong character.** It
recorded the greater-or-equal side as clean on ``0 occurrences of the 0xB3 slot``,
which is true and is not what it reads as. 183 of the 256 operators are ``>=``, and
they landed on a double dagger, on two control codes, and on 0xB3 exactly once but
in the private use area. A rule keyed on the pound sign reaches none of them.

**``symbol_glyph_census`` is the other half, and it is the durable one.** The
substitution repairs five slots somebody went and looked at. What it cannot reach
is the next corpus refresh bringing a symbol font nobody has looked at -- decoded
however the PDF says, with every check downstream reading clean, which is the state
this corpus was in for the whole of #83. So every unmapped glyph from a symbol face
is counted per document into ``manifest.json`` and summed on the run summary, and a
refresh leaves a diff somebody has to look at rather than a silence somebody has to
think of.

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
bare folios and welded running heads **and nothing else at all** -- 2,382 folios and
306 head lines at N=2, the head count having risen by 39 when #178 fixed the KDIGO
transplant footer's spacing and the rule could see it for the first time. N=3 removes a further 574 lines across 11 documents, and
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
2,688 distinct lines, of which 2,382 are bare folios and 306 are the three welded
heads -- re-derived 2026-08-19. It read 2,649 and two heads until #178: the third
head is the KDIGO transplant footer, which the rule could not see while the space
reconstruction was setting each of its digits as a separate run. Documents with nothing stripped by either rule fall from 12 to 5. The two
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
import artifact_lock
import artifact_provenance
import collections
import json
import os
import re
import statistics
import sys
import unicodedata
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from console_codec import use_utf8
from guidelines_manifest import MANIFEST_NAME, Record, serialize_record
from repo_root import InsideCheckout, ensure_outside_checkout

REPO_ROOT = Path(__file__).resolve().parent.parent

# Figures whose producers #404 deletes. Each row names why it is historical rather
# than current: all were measured before #178's second spacing bar and #172's
# operator repair, by an instrument that no longer exists. ``CLAUDE.md`` points at
# this object and copies no row, so this is the one place their dated evidence lives.
ORPHANED_FIGURES = (
    ("pypdf words", "5,340,439", "pre-#178 reader comparison producer deleted"),
    ("pypdf glued", "4,168", "pre-#178 reader comparison producer deleted"),
    ("pypdf time", "342 s", "pre-#178 reader comparison producer deleted"),
    ("fitz default words", "5,319,299", "pre-#178 reader comparison producer deleted"),
    ("fitz default glued", "6,568", "pre-#178 reader comparison producer deleted"),
    ("rebuilt words", "5,369,614", "pre-#178 reader comparison producer deleted"),
    ("rebuilt glued", "719", "pre-#178 reader comparison producer deleted"),
    ("rebuilt split", "6,881", "pre-#178 reader comparison producer deleted"),
    ("rebuild time", "195 s", "pre-#178 reader comparison producer deleted"),
    ("glued run fixed", "9,622", "pre-#178 five-bucket classifier was never saved"),
    (
        "punctuation, tab or bullet",
        "3,179",
        "pre-#178 five-bucket classifier was never saved",
    ),
    (
        "letter-spaced word",
        "306",
        "pre-#178 five-bucket classifier was never saved",
    ),
    (
        "word broken, pieces not all single",
        "188",
        "pre-#178 five-bucket classifier was never saved",
    ),
)

# Written with an explicit codec on every call and recorded in the manifest. This
# is not ceremony: the en dash in "130-139 mm Hg" survives extraction intact and
# then dies on the way out, because the default encoding on a Windows console is
# cp1252 and cannot represent it. A recorded codec is how that stays visible.
OUTPUT_CODEC = "utf-8"

PAGE_SEPARATOR = "\f"

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

# The fraction of a line's *own* observed space advance that a gap has to reach
# before it may be read as a word break -- #178.
#
# `span_baselines` fixed the pages where the running footer of
# KDIGO-2009-Transplant-Recipient-Guideline-English.pdf is set as three spans. It
# cannot fix the 142 where it is one: there the per-glyph gaps run from -2.35 to
# 0.00 around a median of -1.36, so the top of the span's own spread clears any
# fixed offset from that median. Heavy and variable negative bearings, not tracked
# type, and no median-plus-offset rule separates the two.
#
# What separates them is that the line carries real space glyphs. The PDF has
# already said where its words are -- 1.056 pt from the previous glyph's right
# edge to the next glyph's left, across one of its own spaces -- while the gaps
# being split measure 0.003. So a word break on that line is worth 350 times what
# a letter join is, and the line states both quantities itself.
#
# **"The line has a space, so infer nothing" is too blunt, and that is measured
# rather than assumed.** 12,003 of the corpus's inferences are made on lines that
# already carry a space -- USPSTF sets a real space after a bullet and glues the
# words after it anyway -- and the great majority are correct. So the rule is a
# floor on the gap, not a veto on the line.
#
# **The value is the midpoint of a plateau rather than a tuned edge.** Every
# constant in (0.0025, 0.0974] suppresses exactly the same 2,809 inferences -- a
# 39-fold interval in which the answer does not move at all, because the highest
# damaged ratio in the corpus is 0.0025 and the next ratio of any kind is 0.0974.
# No tuning table is written out here: five rows reading 2,809 say only what that
# sentence says, and #83's lesson is that a published tuning table is what goes
# stale.
#
# All 2,809 were read, and they fall across **five** documents. 2,741 are that one
# footer. 33 are letter-spaced runs in `ADA/standards-of-care-2026`
# (`S i l v e r S p r i n g`, `D e x c o m , I n c`, `B e t h e s d a`) and 33 more
# in the CDC opioid MMWR (`e x e m p t e d e l i g i b l e p h y s i c i a n s`).
# The last two are one each in the two ACIP captures and are **not** letter-spacing
# at all -- a space inserted after an opening bracket, `Hib ( Haemophilus`.
#
# The first *correct* split lost is at 0.1173, a GOLD citation marker
# (`studied.(1650)` -> `studied. (1650)`), so 0.05 sits a factor of 2.3 below the
# nearest real cost and a factor of 20 above the damage it exists to stop.
#
# Measured over all 179 documents and all 7,733 pages, 2026-08-19. #83 published a
# tuning table built from 10 documents that named a value at an edge, and over the
# corpus that value was the one setting worse than not making the change at all --
# which is why the plateau matters more here than the number does.
SPACE_ADVANCE_FRACTION = 0.05

# How many inter-character gaps a line needs before its median is trusted as a
# baseline. See `line_baseline` for why a low floor would be worse than none.
MINIMUM_GAPS_FOR_BASELINE = 4

# A font whose one-span lines contain two incompatible spacing regimes. On CDC's
# opioid MMWR extracted page 27, ``Nunito-Regular`` compresses the middle of a
# sentence by roughly 3 pt while leaving both ends at ordinary bearings. A local
# baseline repairs that line; applying the same rule to every font erases real
# inferred spaces before evidence-table footnotes in IDSA, so the boundary is a
# measured font property rather than a general spacing heuristic. #178.
LOCAL_SPACING_BASELINE_FONTS = frozenset({"Nunito-Regular"})

# Fonts that lie about their own encoding, and what their glyphs really are --
# #172. A comparison operator set in one of these comes back as something else,
# from `pypdf` and PyMuPDF alike, because the mis-encoding is in the PDF rather
# than in either reader's interpretation of it.
#
# **Keyed on the font, so no rule reads the text.** The ticket proposed a
# unit-aware rule -- a pound sign, then a number, then a clinical unit -- and
# priced it at ~67 of the 73 it knew about. Keyed on the font instead, the two
# genuine currency figures in the corpus are untouched *by construction* rather
# than by a rule that mostly avoids them: both are set in an ordinary text face,
# one `MinionPro-Regular` and one `Berkeley-Medium`, each beside a euro sign in a
# price list. That is what makes this a decoding fix and not a heuristic, and it
# is why the clinician's ruling on 2026-08-19 was to substitute at all.
#
# **The evidence is the rendered glyph, because the PDF offers no other.**
# `GMBEDM+AdvPS_SSYB` declares `/Encoding /WinAnsiEncoding`, which is a text
# encoding on a symbol font; it ships no `ToUnicode` at all; and its embedded CFF
# subset names its two glyphs `sterling` and `daggerdbl`. All three statements are
# wrong, so nothing in the file can be trusted and the page had to be rasterized
# and looked at -- `span_baselines`'s method, for `span_baselines`'s reason.
#
# Measured over all 179 documents, 2026-08-19. **256 operators across 12 files**,
# against the 73 the ticket recorded:
#
#     AdvPS_SSYB  U+00A3 -> <=    71   9 docs, all KDIGO
#     AdvPS_SSYB  U+2021 -> >=   146  11 docs, all KDIGO
#     SymbolMT    U+001E -> <=     2   1 doc, AHA/ACC aortic disease 2022
#     SymbolMT    U+001F -> >=    36   1 doc, the same one
#     SymbolMT    U+F0B3 -> >=     1   1 doc, IDSA GAS pharyngitis
#
# **The ticket looked at the wrong character for the >= side.** It records that
# side as clean on `0 occurrences of the 0xB3 slot`, which is true and does not
# mean what it reads as: >= landed on a double dagger 146 times, on two C0 control
# codes 38 times, and on 0xB3 exactly once but in the *private use area*, where a
# scan for U+00B3 cannot see it. A rule keyed on the pound sign reaches none of
# the 183.
#
# **39 of the 256 are deleted rather than mangled, which is worse.** U+001E,
# U+001F and U+F0B3 all fall inside `_DISCARDED_RANGES`, so before this landed
# `COPD and FEV1 <=50% predicted` reached the corpus as
# `COPD and FEV1 50% predicted`: a threshold flattened into an equality with no
# character left behind to notice it by. Nothing downstream could have caught
# that -- `threshold_sheet.py`'s gate refuses a mis-encoded character in a value
# cell, and there is no character.
#
# **What this cannot reach, and it is the reason for `symbol_glyph_census`
# below.** A symbol font this table does not name is decoded however the PDF says
# and passes in silence, which is exactly the state the corpus was in until
# somebody went looking. `SymbolMT` is the standing warning: under that one font
# name the corpus emits <= and >= *correctly* 2,078 times in other documents, so a
# font name is not a verdict on a document, only on a slot -- and a row may only
# claim a slot that is wrong everywhere.
#
# **`MathematicalPi-One` is the font that cannot go here, and it is why the rule
# above is load-bearing rather than decorative.** It sets comparison operators in
# two C0 slots `_DISCARDED_RANGES` deletes, but the slots are exactly inverted
# between two documents of the same society:
#
#     abdom-aortic-aneurysm-screening-final-rs     U+0002 = >=   U+0003 = <=
#     osteoporosis-screening-final-recommendation  U+0002 = <=   U+0003 = >=
#
# So a font-name-keyed row would have turned `>=90% of screen-detected AAAs` into
# `<=90%` -- **inverting a threshold rather than losing one**, which is worse than
# the defect this table was built for and is the one outcome no gate downstream
# can catch, because the result is a well-formed operator in a plausible place.
#
# **Neither the character code nor the glyph ID is the identity.** A 2026-08-20
# full-corpus check found both reused for opposite operators in different subsets.
# The page rendering is the only truthful layer. `rendered_operator_map` clips each
# U+0002, U+0003 and legal-looking U+003A colon and classifies the direction of the
# upper stroke. A shape too near the center is refused and remains in the census.
#
# **#283's named font-glyph cases are deliberately not here.** `AdvPSSym`
# renders a copyright sign; `SymbolMT` renders an up arrow as `n` and a down
# arrow as `p` in a KDIGO figure; `Universal-GreekwithMathP` renders an equals
# sign in a deleted C0 slot. Ruled 2026-08-20: these remain report-only. None is
# a character a threshold is written with, which is the boundary of what this
# table may claim, and mapping a *letter* would mean a font name that is ever
# wrong corrupts prose rather than one symbol. All of them stay visible in
# `symbol_glyph_census`; no row here rewrites one.
SYMBOL_FONT_OPERATORS = {
    "AdvPS_SSYB": {
        "\u00a3": "\u2264",  # rendered: a less-or-equal sign
        "\u2021": "\u2265",  # rendered: a greater-or-equal sign
    },
    "SymbolMT": {
        "\u001e": "\u2264",
        "\u001f": "\u2265",
        "\uf0b3": "\u2265",  # the Symbol font's own 0xB3, surfacing unmapped
    },
}

OPERATOR_INK_CUTOFF = 245
OPERATOR_ORIENTATION_MARGIN = 0.03
OPERATOR_RENDER_SCALE = 12.0
MATHEMATICAL_PI_OPERATOR_SLOTS = {"\u0002", "\u0003", ":"}
RenderedOperatorKey = tuple[str, tuple]


def rendered_operator_key(name: str, char: dict) -> RenderedOperatorKey | None:
    """The identity shared by a raw glyph and its rendered-page classification."""
    origin = tuple(char.get("origin", ()))
    if len(origin) != 2:
        return None
    return name, origin


def comparison_operator_from_grayscale(
    samples: bytes,
    width: int,
    height: int,
    direction: tuple[float, float] = (1.0, 0.0),
) -> str | None:
    """Classify a rendered <= or >= by the direction of its upper stroke.

    The equality bar is symmetric. In the upper third of the remaining ink, a
    greater-than stroke occupies the left side and a less-than stroke the right.
    A centroid inside the center margin is refused rather than guessed.
    """
    if width < 2 or height < 3 or len(samples) != width * height:
        return None
    dx, dy = direction
    ink = [
        (dx * x + dy * y, -dy * x + dx * y, 255 - samples[y * width + x])
        for y in range(height)
        for x in range(width)
        if samples[y * width + x] < OPERATOR_INK_CUTOFF
    ]
    if not ink:
        return None
    x0 = min(x for x, _y, _weight in ink)
    x1 = max(x for x, _y, _weight in ink)
    y0 = min(y for _x, y, _weight in ink)
    y1 = max(y for _x, y, _weight in ink)
    ink_width = x1 - x0 + 1
    upper_edge = y0 + (y1 - y0 + 1) / 3
    upper = [(x, weight) for x, y, weight in ink if y < upper_edge]
    mass = sum(weight for _x, weight in upper)
    if not mass:
        return None
    centroid = (
        sum((x + 0.5) * weight for x, weight in upper) / mass - x0
    ) / ink_width
    if centroid <= 0.5 - OPERATOR_ORIENTATION_MARGIN:
        return "\u2265"
    if centroid >= 0.5 + OPERATOR_ORIENTATION_MARGIN:
        return "\u2264"
    return None


def rendered_operator_map(raw: dict, render_glyph) -> dict[RenderedOperatorKey, str]:
    """Resolved MathematicalPi-One operators keyed by font and glyph origin."""
    resolved: dict[RenderedOperatorKey, str] = {}
    for block in raw.get("blocks", ()):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", ()):
            for span in line.get("spans", ()):
                name = font_key(span.get("font", ""))
                if name != "MathematicalPi-One":
                    continue
                for char in span.get("chars", ()):
                    if char["c"] not in MATHEMATICAL_PI_OPERATOR_SLOTS:
                        continue
                    try:
                        samples, width, height = render_glyph(char["bbox"])
                        operator = comparison_operator_from_grayscale(
                            samples,
                            width,
                            height,
                            direction=tuple(line.get("dir", (1.0, 0.0))),
                        )
                    except Exception:  # noqa: BLE001 - an unresolved slot stays censused
                        continue
                    key = rendered_operator_key(name, char)
                    if operator is not None and key is not None:
                        resolved[key] = operator
    return resolved

# A PDF font subset tag: exactly six uppercase letters and a plus, as in
# `GMBEDM+AdvPS_SSYB`. PyMuPDF strips it before `rawdict`, so the corpus never
# exercises this -- but the tag is one call away in the font dictionary itself,
# and matching on the plus alone would let `abcdef+AdvPS_SSYB` through as a font
# nobody measured.
SUBSET_TAG = re.compile(r"^[A-Z]{6}\+")

# Font names whose glyphs are worth counting even where nothing maps them. A
# substring match and therefore a guess -- which is affordable here and nowhere
# else in this module, because `symbol_glyph_census` only ever *reports*. Nothing
# below changes a character.
SYMBOL_FONT_MARKERS = (
    "sym", "ssy", "dingbat", "wingding", "mathematicalpi", "mathpi", "universal",
)


CLASS_GUIDELINE = "guideline"
# USPSTF's document type and nobody else's in this corpus: the 90 USPSTF files each
# title themselves one. #82 built a separate table for exactly that distinction.
CLASS_RECOMMENDATION_STATEMENT = "recommendation-statement"
# A browser print-to-PDF of a web page rather than a published document, which is the
# three ACIP/ files and only those.
CLASS_WEB_CAPTURE = "web-capture"
# A document whose own title page says it is not final. Kept narrower than the word
# ``draft`` so a final guideline discussing an earlier draft is not reclassified.
CLASS_DRAFT = "draft"
# A correction document that titles itself ``Errata`` or ``Erratum``. The classifier
# matches a whole title line, never the word in body prose.
CLASS_ERRATA = "errata"
# Planning material for a guideline that has not been written. Both identity marks
# are required so an ordinary scope section does not decide the document class.
CLASS_SCOPE_OF_WORK = "scope-of-work"
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
#: **``guidelines_index.UNCLASSIFIED`` is an additional value the index can carry and this
#: is deliberately not it either.** That one describes a *build* -- a document with no
#: manifest entry at all -- rather than a document, so no catalog row could sensibly
#: hold it. It is named here rather than left to be discovered, and pinned in
#: ``test_class_vocabulary.py``.
#:
#: ``guidelines_catalog.py`` imports this rather than restating it, and
#: ``guidelines_catalog.check_legend`` asserts the catalog's own legend row is this set.
CLASSES = (
    CLASS_GUIDELINE,
    CLASS_RECOMMENDATION_STATEMENT,
    CLASS_WEB_CAPTURE,
    CLASS_DRAFT,
    CLASS_ERRATA,
    CLASS_SCOPE_OF_WORK,
)

# The pre-strip page vote used by the catalog's publication-year guess. It lives
# with the producer because the manifest has to retain the page frequency that
# deduplicated ``boilerplate`` and ``margin_stripped`` literals cannot express.
PUBLICATION_YEAR_RE = re.compile(r"(?:19|20)\d{2}")
ACCESS_LINE_RE = re.compile(
    r"downloaded from|by guest on|accessed on|retrieved on|last reviewed", re.I
)


def publication_year_page_counts(pages: list[list[str]]) -> dict[str, int]:
    """How many pages carry each non-access year before anything is stripped."""
    hits: dict[str, int] = {}
    for page in pages:
        found: set[str] = set()
        for line in page:
            if ACCESS_LINE_RE.search(line):
                continue
            found.update(PUBLICATION_YEAR_RE.findall(line))
        for year in found:
            hits[year] = hits.get(year, 0) + 1
    return dict(sorted(hits.items()))

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
# written, because the producer owns the vocabulary it emits and the auditor consumes
# the manifest value. Two copies of a rule that must agree is what #253 cost.
TASK_FORCE_MARK = "taskforce"
RECOMMENDATION_STATEMENT_MARK = "recommendationstatement"
PUBLIC_REVIEW_DRAFT_TITLE = re.compile(
    r"^\s*public\s+review\s+draft\s*$", re.IGNORECASE | re.MULTILINE
)
ERRATA_TITLE = re.compile(r"^\s*errat(?:a|um)\s*$", re.IGNORECASE | re.MULTILINE)
ERRATA_RUNNING_HEAD = re.compile(r"errata\s*$", re.IGNORECASE | re.MULTILINE)
ERRATUM_CORRECTION_TITLE = re.compile(
    r"^\s*erratum\s+to\s*:", re.IGNORECASE | re.MULTILINE
)
GUIDELINE_MARK = "guideline"
SCOPE_OF_WORK_TITLE = re.compile(r"^\s*scope\s+of\s+work\s*$", re.IGNORECASE | re.MULTILINE)

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
    """Whether a title block says the document is a USPSTF recommendation statement."""
    squashed = squash(title_block)
    return TASK_FORCE_MARK in squashed and RECOMMENDATION_STATEMENT_MARK in squashed


def is_public_review_draft(title_block: str) -> bool:
    """Whether the document identifies itself as a public review draft."""
    return PUBLIC_REVIEW_DRAFT_TITLE.search(title_block) is not None


def is_errata(title_block: str) -> bool:
    """Whether a title line identifies the whole document as errata."""
    return ERRATA_TITLE.search(title_block) is not None or (
        ERRATA_RUNNING_HEAD.search(title_block) is not None
        and ERRATUM_CORRECTION_TITLE.search(title_block) is not None
    )


def is_guideline_scope_of_work(title_block: str) -> bool:
    """Whether the title identifies planning material for a future guideline."""
    squashed = squash(title_block)
    return GUIDELINE_MARK in squashed and SCOPE_OF_WORK_TITLE.search(title_block) is not None


def classify(pages: list[list[str]]) -> str:
    """Which of ``CLASSES`` this document is.

    **Ordered, and the order matters**: a browser capture of a page that happens to say
    "recommendation statement" is still a capture.

    The capture test is counted over the sampled pages directly rather than read off
    the boilerplate set. Those look interchangeable on the three real captures, where
    the stamp is on every page and clears every bar -- but reading the boilerplate set
    makes the class a side effect of boilerplate detection, so a capture short enough
    to trip MINIMUM_OCCURRENCES, or one whose stamp missed the threshold by a page,
    would come back a guideline with nothing saying otherwise.

    **Every content-form test reads the first page only**, which is where the document
    identifies itself. The three #107 forms use whole title lines, so a final guideline
    mentioning an earlier draft, errata, or its scope in prose keeps the fallback class.
    This runs here rather than in ``guidelines_catalog.py`` alone because #185 ruled the
    producer's vocabulary is the catalog's. The catalog consumes this manifest value;
    it does not reclassify extracted text. The extractor sees the pages **before**
    stripping, which is why the capture test must live here: its timestamp is
    boilerplate and is absent from the extracted text the index reads.
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
    if pages and is_public_review_draft("\n".join(pages[0])):
        return CLASS_DRAFT
    if pages and is_errata("\n".join(pages[0])):
        return CLASS_ERRATA
    if pages and is_guideline_scope_of_work("\n".join(pages[0])):
        return CLASS_SCOPE_OF_WORK
    if pages and is_recommendation_statement(" ".join(pages[0])):
        return CLASS_RECOMMENDATION_STATEMENT
    return CLASS_GUIDELINE


def document_id(relative: Path) -> str:
    """The key #84 matches a document by: the relative path, no suffix, posix.

    Its first segment is the society, which is how a hit names a file that can be
    opened beside the PDF of the same name.
    """
    return relative.with_suffix("").as_posix()


def society_of(doc_id: str) -> str | None:
    return doc_id.split("/")[0] if "/" in doc_id else None


def build_document(
    relative: Path,
    raw_pages: list[str],
    out_root: Path,
    title: str | None = None,
    symbol_glyphs: dict[str, int] | None = None,
    split_boundaries: dict[str, int] | None = None,
    quantity_split_shapes: dict[str, int] | None = None,
) -> Record:
    """Normalize, strip, write one text file, and describe what was done to it.

    ``symbol_glyphs`` is #172's census, which cannot be computed here: this takes
    page *strings* and a font name exists only in the ``rawdict`` ``extract_pages``
    walked. It is carried rather than derived for exactly that reason, and defaults
    to nothing counted -- which is what every caller in the test file is.
    """
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
        year_page_counts=publication_year_page_counts(pages),
        symbol_glyphs=dict(symbol_glyphs or {}),
        split_boundaries=dict(split_boundaries or {}),
        quantity_split_shapes=dict(quantity_split_shapes or {}),
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


def font_key(name: str) -> str:
    """A span's font name with any subset tag dropped.

    ``GMBEDM+AdvPS_SSYB`` and ``AdvPS_SSYB`` are the same typeface, and every
    document embeds its own subset under its own tag -- so a table keyed on the
    tagged name would match one document and no other.
    """
    return SUBSET_TAG.sub("", name)


def is_symbol_font(name: str) -> bool:
    """Whether a font name marks it as a symbol face rather than a text one."""
    lowered = font_key(name).lower()
    return any(marker in lowered for marker in SYMBOL_FONT_MARKERS)


def symbol_glyph_census(
    raw: dict, rendered_operators: dict[RenderedOperatorKey, str] | None = None
) -> dict[str, int]:
    """Glyphs from a symbol font that ``SYMBOL_FONT_OPERATORS`` does not map.

    **A report and never a rule** -- this is what stops #172 recurring in silence.
    The defect it exists for is not a character that came out wrong; it is a
    *corpus refresh* bringing a font nobody has looked at, whose comparison
    operators land wherever its broken map sends them, with every downstream check
    reading clean. That is the state this corpus was in for the whole of #83.
    Recorded per document in ``manifest.json``, so a refresh produces a diff
    somebody has to look at rather than a silence somebody has to think of.

    Keyed ``<font> U+XXXX`` and counted. **Deliberately unfiltered beyond the two
    exclusions below**, and an allowlist of glyphs that look harmless is exactly
    what would have hidden U+001F -- which reads as extraction debris and is a
    greater-or-equal sign.

    A space is dropped because every symbol font in the corpus sets them and means
    nothing by it. A glyph resolved by the character table or the rendered map is
    dropped too, as is a glyph already equal to one of
    ``SYMBOL_FONT_OPERATORS``'s *replacements*. That is a line about this module's
    own vocabulary rather than a judgment about what looks harmless: a symbol font
    emitting a correct ``<=`` is the non-defect this whole table exists to produce.
    Measured
    2026-08-19 it is not a nicety -- ``SymbolMT`` alone renders 2,078 correct
    operators across the corpus, which is two thirds of everything the census would
    otherwise print, and a report whose loudest line is the thing working is a
    report with no usable baseline.

    **What that costs, named rather than discovered.** A font emitting ``<=`` where
    the page shows ``<`` is now invisible here. It was never visible: no census over
    a text layer can see a glyph that decoded to a plausible character, which is the
    same reason the five rows above had to be settled by rendering a page.
    """
    rendered_operators = rendered_operators or {}
    replacements = {
        replacement
        for mapping in SYMBOL_FONT_OPERATORS.values()
        for replacement in mapping.values()
    }
    census: dict[str, int] = {}
    for block in raw.get("blocks", ()):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", ()):
            for span in line.get("spans", ()):
                name = font_key(span.get("font", ""))
                if not is_symbol_font(name):
                    continue
                mapped = SYMBOL_FONT_OPERATORS.get(name, {})
                for char in span.get("chars", ()):
                    glyph = char["c"]
                    rendered_key = rendered_operator_key(name, char)
                    if (
                        glyph in mapped
                        or (
                            rendered_key is not None
                            and rendered_key in rendered_operators
                        )
                        or glyph in replacements
                        or glyph == " "
                    ):
                        continue
                    key = f"{name} U+{ord(glyph):04X}"
                    census[key] = census.get(key, 0) + 1
    return census

def span_space_advances(line: dict) -> list[float | None]:
    """What a word break is worth on this line, read off the spaces it already has.

    One value per span, because a line's spans do not share metrics: a span with
    spaces of its own is measured on them, a span with none borrows the line's, and
    a line with none at all gets ``None``.

    **That is ``span_baselines``'s fallback order with its count floor deliberately
    absent, and the difference is not an oversight.** A *baseline* is a median gap,
    so over one or two samples it is the gap itself -- degenerate, which is what
    ``MINIMUM_GAPS_FOR_BASELINE`` exists for. An *advance* is not a summary of a
    distribution: **one real space glyph is one word break the typesetter actually
    set**, and is direct evidence rather than an estimate of it. A floor here would
    throw that evidence away on exactly the short lines that have least of it, and
    the quantity is used as a 5% floor with two orders of magnitude of headroom, so
    an unrepresentative single sample cannot reach the decision. Pinned by a test
    so the divergence is a decision rather than a copy that drifted.

    **The advance is measured across the space, never of it.** A space glyph's own
    width is not what separates two words -- the gaps on either side count too, and
    on the KDIGO footer they are negative enough to more than halve it: the glyph
    is 3.776 pt wide and the real separation is 1.056. So the quantity is the
    previous glyph's right edge to the next glyph's left, which is exactly the
    quantity a candidate gap is, and the two are comparable without adjustment.

    A space beside another space is skipped, because a run of them is padding
    rather than one word break and would report an advance no single break has.

    **``None`` is not zero.** It means the line said nothing about what a space is
    worth, and the caller must then infer on the older rule alone -- which is the
    property that keeps this from reaching the 59,092 inferences the corpus makes
    on lines carrying no space at all.

    **A non-positive advance is the third answer and is treated as the same
    silence.** Bearings negative enough can put the next glyph's left edge at or
    behind the previous glyph's right edge even across a real space, and a floor
    computed from such a value is either zero or backwards -- so ``rebuild_text``
    disables the second bar there rather than applying a bar that cannot bind. It
    is not observed in this corpus and is guarded anyway, because the failure it
    would cause is the silent one: every gap on the line clearing a bar of zero.
    """
    def advances(chars: list[dict]) -> list[float]:
        return [
            chars[index + 1]["bbox"][0] - chars[index - 1]["bbox"][2]
            for index in range(1, len(chars) - 1)
            if chars[index]["c"] == " "
            and chars[index - 1]["c"] != " "
            and chars[index + 1]["c"] != " "
        ]

    spans = [list(span.get("chars", ())) for span in line.get("spans", ())]
    fallback = advances([char for span in spans for char in span])
    return [
        statistics.median(own or fallback) if (own or fallback) else None
        for own in (advances(span) for span in spans)
    ]


def glyph_baselines(line: dict) -> list[list[float]]:
    """One spacing baseline per glyph, bounded by real space glyphs where present.

    A span normally owns one spacing regime, and ``span_baselines`` remains the
    fallback for spans that contain no real spaces. CDC's opioid MMWR extracted
    page 27 is the counterexample: one span holds a normally spaced phrase, a
    heavily compressed phrase, and normally spaced prose again. The compressed
    middle dominates the span median and makes ordinary letter gaps on either
    side look like word breaks.

    Real spaces are boundaries the PDF supplied, so each run between them gets
    its own baseline. A short run deliberately falls through ``line_baseline`` to
    its absolute-rule value of zero; borrowing the compressed neighbor's median
    would recreate the defect this boundary exists to prevent. Lines without a
    real space keep the existing span behavior unchanged.
    """
    span_fallbacks = span_baselines(line)
    result: list[list[float]] = []
    for span_index, span in enumerate(line.get("spans", ())):
        chars = list(span.get("chars", ()))
        if (
            font_key(span.get("font", "")) not in LOCAL_SPACING_BASELINE_FONTS
            or not any(char["c"] == " " for char in chars)
        ):
            result.append([span_fallbacks[span_index]] * len(chars))
            continue

        segments: list[tuple[int, int, float]] = []
        start = 0
        while start < len(chars):
            if chars[start]["c"] == " ":
                start += 1
                continue
            end = start
            while end < len(chars) and chars[end]["c"] != " ":
                end += 1
            baseline = line_baseline(
                [(char, span.get("size", 0.0)) for char in chars[start:end]]
            )
            segments.append((start, end, baseline))
            start = end

        # Local baselines are a repair for a compressed regime that dominates the
        # whole span, not a general replacement for its median. Ordinary kerning
        # varies by word, and a compressed citation inside otherwise normal prose
        # must not activate this rule. The span median itself has to overlap by
        # more than this size's existing word-break threshold.
        threshold = max(
            SPACE_GAP_FRACTION * span.get("size", 0.0), SPACE_GAP_FLOOR
        )
        if not segments or span_fallbacks[span_index] >= -threshold:
            result.append([span_fallbacks[span_index]] * len(chars))
            continue

        baselines = [0.0] * len(chars)
        for start, end, baseline in segments:
            baselines[start:end] = [baseline] * (end - start)
        result.append(baselines)
    return result

def walk_line_glyphs(
    line: dict,
    rendered_operators: dict[RenderedOperatorKey, str] | None = None,
) -> Iterable[tuple[str, bool]]:
    """Yield each repaired glyph and whether the gap rule inserts space before it.

    This is the one owner of the spacing decision. ``rebuild_text`` renders it and
    ``split_census`` observes it; the audit therefore moves whenever the production
    rule moves rather than carrying a second implementation that can go stale.
    """
    rendered_operators = rendered_operators or {}
    baselines = glyph_baselines(line)
    if not baselines:
        return
    advances = span_space_advances(line)
    buffer: list[str] = []
    previous_right: float | None = None
    for index, span in enumerate(line.get("spans", ())):
        size = span.get("size", 0.0)
        advance = advances[index]
        threshold = max(SPACE_GAP_FRACTION * size, SPACE_GAP_FLOOR)
        # #172. Looked up once per span rather than once per character, and empty
        # for every font in the corpus but two.
        name = font_key(span.get("font", ""))
        operators = SYMBOL_FONT_OPERATORS.get(name, {})
        for char_index, char in enumerate(span.get("chars", ())):
            baseline = baselines[index][char_index]
            # Substituted before the gap rule reads it. Every mapping is 1:1 and
            # none produces a space, so the spacing decision is unchanged.
            rendered_key = rendered_operator_key(name, char)
            glyph = (
                rendered_operators.get(rendered_key)
                if rendered_key is not None
                else None
            )
            if glyph is None:
                glyph = operators.get(char["c"], char["c"])
            left, _, right, _ = char["bbox"]
            # Two independent bars: the gap must stand out against its line and,
            # where the line supplies a real-space advance, resemble a word break.
            gap_is_wide = (
                previous_right is not None
                and (left - previous_right) - baseline > threshold
                and (
                    advance is None
                    or advance <= 0.0
                    or (left - previous_right) >= SPACE_ADVANCE_FRACTION * advance
                )
            )
            inserted = (
                gap_is_wide and glyph != " " and bool(buffer) and buffer[-1] != " "
            )
            yield glyph, inserted
            # Keep the buffer because preventing a second inferred space is part
            # of the production rule the yielded decision represents.
            if inserted:
                buffer.append(" ")
            buffer.append(glyph)
            previous_right = right


def rebuild_text(
    raw: dict, rendered_operators: dict[RenderedOperatorKey, str] | None = None
) -> str:
    """One page of PyMuPDF data as text, with word spacing and operators recovered.

    **Takes ``rawdict`` and already-classified rendered operators rather than the
    page**, so every rule in here is exercisable from a literal in a test file and
    the suite still never opens a PDF. That is the same line
    ``test_guidelines_extract.py`` already draws around the ``.txt`` excerpts in
    ``tools/testdata/``.

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
            walked = list(walk_line_glyphs(line, rendered_operators))
            if not walked:
                continue
            lines.append(
                "".join((" " if inserted else "") + glyph for glyph, inserted in walked)
            )
    return "\n".join(lines)


def rendered_operator_map_for_page(page, raw: dict) -> dict[RenderedOperatorKey, str]:
    """Classify rendered operator glyphs for one already-open PyMuPDF page."""
    import pymupdf

    def render_glyph(bbox):
        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(OPERATOR_RENDER_SCALE, OPERATOR_RENDER_SCALE),
            clip=pymupdf.Rect(bbox),
            colorspace=pymupdf.csGRAY,
            alpha=False,
        )
        return bytes(pixmap.samples), pixmap.width, pixmap.height

    return rendered_operator_map(raw, render_glyph)


def extract_pages(
    path: Path,
) -> tuple[list[str], str | None, dict[str, int], dict[str, int], dict[str, int]]:
    """Every page of a PDF as raw text, its embedded title, and #172's census.

    The census comes back from here and not from anywhere downstream because this
    is the last place a font name and rendered glyph exist -- ``rebuild_text``
    returns a string, and every function after it takes page text.

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
    pages: list[str] = []
    symbol_glyphs: dict[str, int] = {}
    import split_census

    split_boundaries = split_census.empty_boundaries()
    quantity_split_shapes: collections.Counter[str] = collections.Counter()
    for page in document:
        try:
            raw = page.get_text("rawdict")

            rendered_operators = rendered_operator_map_for_page(page, raw)
            pages.append(rebuild_text(raw, rendered_operators))
            split_result = split_census.census_rawdict(raw, rendered_operators)
            split_boundaries.update(split_result.boundaries)
            quantity_split_shapes.update(split_result.quantity_shapes)
            for key, count in symbol_glyph_census(raw, rendered_operators).items():
                symbol_glyphs[key] = symbol_glyphs.get(key, 0) + count
        except Exception:  # noqa: BLE001 - any per-page failure degrades to an empty page
            pages.append("")

    try:
        title = ((document.metadata or {}).get("title") or "").strip() or None
    except Exception:  # noqa: BLE001 - a broken metadata dictionary is not a failed read
        title = None
    document.close()
    return (
        pages,
        title,
        dict(sorted(symbol_glyphs.items())),
        dict(split_boundaries),
        dict(sorted(quantity_split_shapes.items())),
    )


def _engine_version() -> str:
    try:
        import pymupdf

        return f"pymupdf {pymupdf.__version__}"
    except ImportError:
        return "pymupdf (not installed)"


def require_pymupdf() -> None:
    """Fail once, up front, rather than once per document.

    Every per-document failure is caught and recorded, which is what #80 asks for
    -- so without this an uninstalled ``pymupdf`` reads as an unreadable corpus and a
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
        raw_pages, title, symbol_glyphs, split_boundaries, quantity_shapes = extract_pages(
            source_root / relative
        )
        return build_document(
            relative,
            raw_pages,
            out_root,
            title,
            symbol_glyphs,
            split_boundaries,
            quantity_shapes,
        )
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


def split_census_summary(records: list[Record], limit: int = 12) -> list[str]:
    """Bounded run-summary lines for #404's continuous split-safety census."""
    import split_census

    boundaries = split_census.empty_boundaries()
    quantity_shapes: collections.Counter[str] = collections.Counter()
    for record in records:
        boundaries.update(record.split_boundaries)
        quantity_shapes.update(record.quantity_split_shapes)
    lines = [
        "splits      "
        + ", ".join(
            f"{name} {boundaries[name]:,}" for name in split_census.BOUNDARY_CLASSES
        )
    ]
    quantity = sum(quantity_shapes.values())
    lines.append(
        f"split safety {quantity:,} quantity-shaped occurrence(s), "
        f"{len(quantity_shapes):,} distinct shape(s)"
    )
    lines.extend(
        f"            {count:>6,}  {shape[:160]}"
        for shape, count in quantity_shapes.most_common(max(0, limit))
    )
    lines.append(
        "            FINDING quantity-shaped inferred split(s) require review"
        if quantity
        else "            clean"
    )
    return lines


def write_manifest(
    out_root: Path,
    records: list[Record],
    source_root: Path,
    *,
    producer: dict[str, str | bool] | None = None,
) -> Path:
    """The audit trail, and #84's input. One entry per document, in source order.

    ``documents`` is the **list of entries**, which is the shape
    ``guidelines_index.read_manifest`` requires -- it does ``data.get("documents")``
    and raises unless what comes back is a list. The run totals live under
    ``totals`` for that reason: ``"documents": 179`` as a count read as a manifest
    of the wrong shape, and the indexer raised rather than indexing 179 documents
    with no title, society or class. That refusal is the contract working.
    """
    recorded_producer = dict(producer or artifact_provenance.current_producer())
    recorded_producer["inputs"] = artifact_provenance.producer_file_identity(
        artifact_provenance.TRUST_FLOOR["extraction"]
    )
    manifest = {
        "producer": recorded_producer,
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
        "documents": [serialize_record(record) for record in records],
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


# Why *this* artifact stays out, which is not why the other two do. ``REPO_ROOT``
# alone was never enough: run from a worktree it is the worktree, so it says
# nothing about the main clone's ``reference/``, one of the two directories #80
# names by name. The rule that catches the main clone, every sibling worktree and
# any other repo nearby is ``repo_root.enclosing_checkout`` -- #176, which found
# this module holding one of three answers to one question.
WHY_OUTSIDE = (
    "Tracked files are materialized in every worktree and gitignored ones "
    "are copied into every worktree. Pick a directory outside it."
)


def build_parser() -> argparse.ArgumentParser:
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
    return parser


def _run(args: argparse.Namespace, source_root: Path, out_root: Path) -> int:
    """Extract one corpus while ``main`` owns its shared output lock."""
    require_pymupdf()

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
                # is progress output over the whole corpus, and nothing to do with
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
    # #172. Printed on every run rather than only when it is non-zero, because a
    # line that appears when something is wrong is a line nobody has a baseline
    # for -- and the number a reader needs is "the same as last time".
    unmapped = sum(sum(r.symbol_glyphs.values()) for r in records)
    carriers = sum(1 for r in records if r.symbol_glyphs)
    print(
        f"symbols     {unmapped:,} glyph(s) in {carriers:,} document(s) from a symbol "
        "font this build does not map; see symbol_glyphs in the manifest"
    )
    for line in split_census_summary(records):
        print(line)
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


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    if not args.source.is_dir():
        raise SystemExit(f"not a directory: {args.source}")

    source_root = args.source.resolve()
    # Before the dependency check, not after it. Where the output lands is a
    # question about the arguments alone, and answering it first means a
    # machine with no PDF library still refuses a path inside a checkout --
    # which is what lets the cross-check in `test_write_guards.py` drive this
    # command line at all, since the suite installs nothing.
    try:
        out_root = ensure_outside_checkout(
            args.out or default_output(source_root), detail=WHY_OUTSIDE
        )
    except InsideCheckout as refused:
        raise SystemExit(str(refused)) from refused
    try:
        with artifact_lock.hold(out_root, "extracting guideline text"):
            return _run(args, source_root, out_root)
    except artifact_lock.ArtifactBusy as busy:
        print(str(busy), file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
