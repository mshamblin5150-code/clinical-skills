# A table takes Word's default cell padding on its style and the padding is its own calibration

**Measured at:** 1718eceeb4d3f1045d8c86868a98c12e2c0b3d10

[#1585](https://github.com/mshamblin5150-code/clinical-skills/issues/1585) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4) in October 2026. A
rendered-document reader found a laboratory table whose first-column text ran into the next
column, and the run worked around it by rewording the cell. The ticket proposed a table cell margin
in `tools/docx_write.py`. Grilled 2026-10-16; the clinician ruled every point below in that
session, against `main` at the commit above, where the freshness gate read `FRESH`. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

### The defect was zero padding, not a long token or a column width

The run's retained Word-exported PDFs for render passes 2 and 3 were measured with PyMuPDF and their
page images were read. The offending first-column cell was an ordinary three-word phrase with real
spaces. It fit on one line ending about 1.5 pt short of the column border, and the second column's
text began 0.1 pt past that border, so the two cells read as one phrase. Nothing crossed the border.
Every second- and third-column entry on that page also began within 0.1 pt of its border. The table
had three equal 3120-twip columns. The submitted document, re-saved by Word, carries an explicit
zero `tblCellMar` on every table and on the `APATable` style. That is Word writing down the padding it
had drawn, not the renderer's output. *Had the cause been an unbreakable token, a glyph run would
have crossed the border; none did.*

### Word draws no padding on renderer tables and 5.4 pt on its own

Word 16.0 (build 16.0.20430) was driven through COM against synthetic documents, and each document
was repaginated before it was read.

| document | table padding read back, left / right / top / bottom (pt) |
| --- | --- |
| `docx_write.py` output, three columns, long first-column text | 0 / 0 / 0 / 0 |
| a table inserted into a fresh Word document | 5.4 / 5.4 / 0 / 0 |
| the renderer output with `tblCellMar` left and right 108 twips in each `tblPr` | 5.4 / 5.4 / 0 / 0 |
| the renderer output with the same margin on the `APATable` style instead | 5.4 / 5.4 / 0 / 0 |

The fresh document's `styles.xml` declares a default `TableNormal` style carrying `tblCellMar` top 0,
left 108, bottom 0, right 108 twips. The renderer's package has no `TableNormal` style and no
`word/settings.xml`, and `APATable` has no `basedOn`, so nothing supplies a margin. In the rendered
page images the zero-padding table set "Pending" directly against the first column's text. Both
108-twip variants drew a clear gap, left the horizontal rules where they were, and left every row
position and the following paragraph's position unchanged. One three-line first-column cell broke at
different words.

### The prescription pad keeps its measured layout

The `style.md` section 8 pad shape, filled with synthetic values, kept every row on one line, with
the same row positions and the same prose position, with and without the 108-twip margin. The
right-aligned bottom-row item ends 5.4 pt short of the rule end instead of flush with it.
`docx_word_probe._pad_markdown(n)` for 8 through 29 filler paragraphs, built both ways, came out
identical in all 22 placements: no pad split and no prose left its pad. A sweep of 18 pads whose
full-width `Sig` row grew from 61 to 150 characters moved the one-line limit from 98–101 characters
to 92–97. One 97-character `Sig` became two lines, which moved the two rows below it down 13.9 pt
on the same page. The filler sweep never wraps a pad row, so it cannot show a wrap's effect on
pagination.

### The tripwire would not have caught the change

`docx_word_probe`'s `table-horizontal-rules` renderer shape reads the table edges, the header
rule and the style name. The prescription-pad shapes read `keepNext` and the bound and control
pagination. Neither reads `tblCellMar`, so a margin added or removed passes every Word-free test,
including `EveryCalibrationHasAWordFreeRendererShape`, with no retake. `assignment_docx` writes no
table, but it builds its styles from `docx_write.STYLES`.

## Ruling 1 — the padding is Word's own default, 0.075 inch left and right and none top and bottom

That is 108 twips on the left and right and 0 on the top and bottom. APA sets no value. Word's
default gives the value a source rather than a taste, matches what a reader sees in any table made
in Word, and moved nothing but the gap in the live measurement. A wider invented value was declined
for having no source, and top and bottom padding were declined because they make every table and
every pad taller, reopening [ADR 0213](0213-a-prescription-pad-is-held-on-one-page-by-keep-with-next-and-cantsplit-does-not-do-it.md)'s
measured layout.

## Ruling 2 — the margin is declared once, on the `APATable` style

Every renderer table names the style, and a table that names it later gets the padding without a
second declaration. Padding is part of how the style draws, so the style is its home, on the
`TABLE_STYLE_ID` comment's ground that a style misstating its own appearance is a false statement
inside the file. A per-table declaration was declined because a table built another way would come
out padless again, which is this defect. Declaring both was declined as two copies of one value.
Assignment documents gain the margin in their style sheet and draw nothing from it, because they
contain no table.

## Ruling 3 — the prescription pad takes the same margin, and ADR 0213's rule is what must hold

ADR 0213 rules that a pad stays on one page with the start of its prose. It does not rule where a
row breaks, and its binding does not depend on line count. Exempting the pad would keep the flush
text this record exists to remove and would add a pad-only branch. The Word retake adds a pad whose
`Sig` row wraps to two lines to the `prescription-pad-pagination` sweep. That is the one shape the
filler sweep does not reach.

## Ruling 4 — cell padding is its own calibration entry, a house property named in `style.md`

ADR 0213 Ruling 4 gave the pad's pagination its own entry, because a calibrated property that APA
does not require must not sit in an `apa7.md` section 6 row. Cell padding is that kind of property,
so it is not folded into `table-horizontal-rules`, whose claim is APA's borders. The new entry's
renderer shape records the style's declared `tblCellMar`. Its Word observation records the padding
Word reads back on a renderer table, beside a control table with no margin that Word reads as 0, so
the record discriminates the margin working from luck. `style.md` names the behavior and its
calibration key, and the Word-free shape test then refuses any change to the margin until a dated
`python tools/docx_word_probe.py --word` retake records it. Shipping with no calibration was declined:
that is how this defect went unseen.

## What the build carries

- `tools/test_docx.py` asserts the `APATable` style emits the Ruling 1 margin in `CT_TblPr` schema
  order, after `tblBorders`, and that no `tblPr` in `word/document.xml` repeats it.
- The new calibration entry and its renderer shape land, and `style.md` names the key.
- One dated Word retake covers the new entry, `table-horizontal-rules`, `prescription-pad-pagination`
  with Ruling 3's wrapping-`Sig` case, and the assignment rows, whose style sheet changed. The retake
  needs installed Word on the maintainer's machine, so a session without Word cannot finish the build.
