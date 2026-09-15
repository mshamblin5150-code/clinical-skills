# Deck scan reads what the slide face draws

**Measured at:** 25daf9a9789cb2b92e9e249fa847a6fffb68d260

[#1065](https://github.com/mshamblin5150-code/clinical-skills/issues/1065) was filed from
[ADR 0170](0170-every-grader-declares-the-posture-its-empty-population-takes.md) ruling 9, which
kept it out of #922 because reading text stored outside slide XML is a new population whose
membership had to be measured. `tools/deck_scan.py` opens only slide parts and speaker-notes parts,
so text PowerPoint keeps in a SmartArt data part or a chart part is never read. Grilled 2026-09-14;
the clinician ruled every point below the same day. Freshness gate `STALE` at `ac2fa385`, then
`FRESH` at this record's commit after a rebase that changed none of `tools/deck_scan.py`,
`tools/discussion_artifact.py`, `tools/run_grader.py` or ADR 0170. Nothing is built here; this is the
record the build reads.

## Measured before ruling

### The blind spot, re-driven

Synthetic decks built with `tools/test_deck_scan.py`'s helpers, one claim record for a different
figure, a bar of six words per bullet, and the line `Build-out costs $99,000 across nine separate
synthetic budget lines here`:

| deck | figures | findings | exit |
| --- | --- | --- | --- |
| the line on an ordinary slide | 1 | `words-per-bullet`, `untraced-figure` | 1 |
| the line in a grouped shape beside an ordinary slide | 1 | `words-per-bullet`, `untraced-figure` | 1 |
| the line in a SmartArt data part beside an ordinary slide | 0 | none | **0** |
| the line in a chart title and category label beside an ordinary slide | 0 | none | **0** |
| the line in a SmartArt data part alone | 0 | none | 2, for reading no text at all |

*Had the parser read those parts, the third and fourth decks would report what the first does.*
Grouped shapes are already read, so they are not part of this population.

### Which parts carry text in real PowerPoint output

Counted over 19 distinct decks the clinician holds, 18 of them saved by desktop PowerPoint and one
produced by a `course-assignment` run. Counts only; the decks are private and nothing committed
re-derives these figures.

- Slides carry text in almost every deck, and speaker notes in 13.
- SmartArt appears in 4 decks as 23 diagrams. Every diagram's non-empty text multiset is identical
  between its data part and its drawing part, 23 of 23. All text sits on `node` points; none is
  orphaned or hidden. The data parts hold 12 figures found nowhere else in their decks.
- Charts appear in 2 decks as 8 parts, plus one text box laid over a chart. Titles, series names and
  category labels carry text. The plotted-value caches hold 27 figures found nowhere else.
- Four layouts in 2 decks carry text outside placeholders, and no slide uses any of those layouts.
- Picture and 3D-model alternative text is common and holds 2 figures.
- Masters, comments and embedded workbooks carry no text; notes and handout masters carry only
  header, footer and date placeholders.

The skill's own producer writes decks with python-pptx, which can write charts and cannot write
SmartArt; the one produced deck carries slide and notes text only.

### What a chart displays is not what it stores

Across 41 plotted values, 16 carry a data label on the slide and 25 show no number. No deck holds a
pie chart. Stored values carry binary rounding noise, so 11 of the 16 labeled values fail to match
their label as stored strings; rendering each stored value through its effective format code
(`General` or `0%`, the only two present) reproduced PowerPoint's own label text for 16 of 16, read
through PowerPoint automation on copies of the two decks. Value-axis tick numbers are computed at
draw time and are never stored.

### Where SmartArt and chart font sizes resolve

In SmartArt data parts 128 of 141 runs carry no size. Drawing parts carry a size on all 141, and
those sizes agree with what PowerPoint reports for every node read. SmartArt boxes run long: median
17 words, 48 of 86 boxes over 15. Chart sizes do not resolve cleanly: one inherited title reports a
size no chart-level default explains, and 3 of 16 data labels resolve to 16 pt in the XML where
PowerPoint reports 18.

## Ruled 2026-09-14

### 1. Read, and declare only what cannot be read soundly

`deck_scan` reads text PowerPoint stores outside slide XML. A figure in a SmartArt box or on a chart
is the same claim as a figure in a bullet, and the text is plain XML inside the package. Declaring
the gap would leave a graded deck able to carry an unsourced cost past the scan with a counter
beside it.

### 2. The read population is measured membership

Read: SmartArt data parts, and chart titles, series names, category labels and text boxes laid over
a chart. Not read for text: SmartArt drawing parts, whose text duplicates the data part and would
count every figure twice. Not read: layout text, picture and 3D-model alternative text, and notes and
handout masters. Text on a layout a slide actually uses and alternative text each gain a
`deck_scan.DECLARED_LIMITS` row; no deck measured shows the first, and nobody in the room reads the
second.

### 3. That text is slide-face text for ADR 0170's population

Text read from those parts counts toward "text runs read from slide faces". **This does not reopen
ADR 0170.** Its rule, that a deck from which nothing was read is not scanned, stands as written; its
population named text drawn on slide faces and counted only slide XML because that was all the
parser opened. Keeping the old count would report a deck whose SmartArt was read and graded as
having read nothing. `CONTEXT.md` defines **Slide-face text** for this.

### 4. A chart's graded figures are its labeled values, as displayed

`untraced-figure` grades the values a chart labels on the slide, rendered through their effective
format code, and only `General` and `0%`, the two measured. Unlabeled values are not graded, because
nothing is written on the slide for them, and stored values are never graded as stored, because
rounding noise fails correct charts. Value-axis tick numbers gain a `DECLARED_LIMITS` row.

### 5. A recognized member left unread is not scanned

These count as unread: a SmartArt or chart part a slide references that is absent or will not
parse; a labeled value whose format code is outside the measured set; and a pie chart's percentage
labels, which PowerPoint computes rather than stores. The count is derived from slide relationships
and label settings, independently of the text read, and prints on every run. A non-zero count is
`not-scanned`; a finding outranks it. Axis ticks, alternative text and layout text are declared
limits and are not counted, since counting axis ticks would make every chart deck exit 2. The
measured format set grows when a real deck brings a new code.

### 6. Proof is a committed deck PowerPoint authored

A maintainer-only command drives PowerPoint once to author one synthetic deck with invented text: an
ordinary slide, a SmartArt diagram carrying an untraced figure, and a bar chart with one labeled
`General` value and one labeled `0%` value. It is committed under `tools/testdata/`, and the suite
reads it without PowerPoint. Its tests include mutated copies, one with the diagram part removed and
one with a currency format code, each expected to exit 2. Hand-built XML covers the remaining edge
cases. A hand-built part alone could agree with the reader while both disagree with PowerPoint, which
is how this population was missed.

### 7. SmartArt boxes follow the bar's slide limits; chart text does not

Each paragraph in a SmartArt data part is a bullet for `bullets-per-slide` and `words-per-bullet`.
Its size comes from the matching drawing part, read for sizes and never for text; a diagram with no
drawing part has unread sizes and is not scanned under ruling 5. Chart titles and labels are not
bullets, and chart font sizes gain a `DECLARED_LIMITS` row because the XML disagrees with PowerPoint
on real labels.

## Consequences

The bar's words-per-bullet ceiling now reaches SmartArt as it is ordinarily written, and a tight bar
will find long boxes. That is the bar's own limit applied to text an audience reads as a bullet, not
a new house rule.

[#823](https://github.com/mshamblin5150-code/clinical-skills/issues/823)'s recorded untraced figures
for a live deck remain a floor until this is built.
