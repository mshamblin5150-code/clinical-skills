# A prescription pad is held on one page by keep-with-next and cantSplit does not do it

**Measured at:** 928e26cec9f6efad853d9f362cd423e69e3b2c56

[#1023](https://github.com/mshamblin5150-code/clinical-skills/issues/1023) was filed by the
after-action review of one `practicum-case-study` run (NUR 5144 Module 2). Page images from three
render passes showed a prescription pad split between rows, with its drug on one page and its `Sig`
and signature on the next. The continuation page opened with the pad's empty first row repeated as a
header. In another pass the pad sat on one page and its pharmacologic prose block on the next. The
ticket proposed `<w:cantSplit/>` on table rows. Grilled 2026-09-13; the clinician ruled every point
below the same day. Nothing is built here; this is the record the build reads.

## Measured before ruling

### `cantSplit` changes nothing, and keep-with-next on the rows does

`tools/docx_write.py` rendered a synthetic style.md section 8 pad with a prose paragraph under it,
preceded by 8 to 29 one-line filler paragraphs. Each render was rewritten into five variants and
opened in Word 16.0 through COM after `Repaginate`. The page on which each row and the prose began
was read.

| variant | positions where the pad split between rows | positions where the prose left the pad |
| --- | --- | --- |
| today's renderer | 3 (19, 20, 21 fillers) | 2 (17, 18) |
| `cantSplit` on every row | the same 3 | the same 2 |
| `keepNext` on every cell paragraph but the last row's | 0 | 2 |
| that, plus the last row | 0 | the same 2 |
| that, plus the empty paragraph `table()` emits after the table | 0 | 0 |

*Had `cantSplit` held a pad together, its row would have matched the third row rather than the
first.* `cantSplit` stops one row's own content from breaking across a page. Every pad row is one
line, so it has nothing to stop. The last row's `keepNext` binds to the paragraph `table()` appends
after every table, which carries no binding, so the prose stays free until that paragraph is bound
too.

### Keeping every table together costs a page on a long table

A 70-row, three-column table after 3, 10 and 16 fillers: with `keepNext` on all but its last row,
Word started it on page 2 every time, leaving page 1 mostly blank, then broke it across pages 2 and
3 anyway. After 3 fillers that added a page; unbound, 38 rows had fit on page 1.

### The scanner and the renderer did not share a definition of a pad

`case_study_scan._rx_findings` drops the header row unread (`block.rows[1:]`), so a pad whose first
row carries text passes `rx-table-shape` clean.

### The calibration registry has no home for a house-style property

`docx_word_probe.CALIBRATIONS` is bound one-to-one to apa7.md section 6's APA rule rows, and
`PASTE_CALIBRATIONS` to ADR 0013's paste limits. The tracker sweep of 2026-09-10 on #1023 showed the
`table-horizontal-rules` tripwire stays green with `cantSplit` added. Separately,
[ADR 0148](0148-a-markdown-blank-line-renders-nothing-and-a-heading-has-one-declaration.md) ruling 6
gave heading keep-with-next parity "a calibration identity and **no** section 6 row". No such key
exists in `word-renderer-calibration.json` at the measured commit.

## Ruling 1. Only a prescription pad is held together, and a pad is a table whose first row is empty

style.md section 8 already requires the empty first row, so recognizing a pad by it is a declared
shape rather than a guess. Every other table keeps today's behavior and may break across pages with
its header repeated, which APA permits. Keeping every table together was declined on the measured
blank page, and a row-count cap was declined because rows are not height.

## Ruling 2. The pad stays with the paragraph under it

The pad's last row and every paragraph the renderer emits between the table and the next paragraph
carrying text are bound with keep-with-next. That paragraph itself carries no binding, so pads never
chain to each other and a long prose paragraph continues onto the next page normally.

## Ruling 3. `cantSplit` is not emitted, and the pad keeps its header marking

`cantSplit` was measured to do nothing for a one-line row. The pad's first row keeps `tblHeader` and
the header rule. Once the pad is held together, the marking never shows on a continuation page, and a
second pad-only branch would have no visible effect for a test to observe.

## Ruling 4. The Word measurement lives in a third calibration family bound to style.md section 8

This is a **calibrated property** in the glossary's sense: Word's behavior is observed and recorded,
and no APA rule requires it. It takes no apa7.md section 6 row, which would present a house rule as
APA. It is also not folded into `table-horizontal-rules`, whose claim is borders. style.md section 8
names the behavior and its calibration key, the same way apa7.md section 6 names its keys. The Word
record gains its own section, and the probe sweeps a pad across a page boundary with an unbound
control that splits at some position, so the recorded result can tell the binding from luck.

## Ruling 5. `rx-table-shape` fails a pad whose first row carries text

The scanner and the renderer then recognize the same tables as pads, so a pad that passes the scan
is always one the renderer keeps together. `NOT_APPLIED` gains nothing: a non-pad table breaking
across pages is permitted by APA, not an APA rule left undone.

## Ruling 6. No author-facing page-break marker

Rulings 1 and 2 fix the recorded defect. A hand-placed break is tuned to one pagination and wrong
after the next edit above it, and an own-line HTML comment is already markup that #673's rule
strips. A future non-pad layout defect that needs one comes on its own ticket with its own evidence.

## What this record does not settle

Whether the empty paragraph `table()` appends after every table should exist, given that
[ADR 0148](0148-a-markdown-blank-line-renders-nothing-and-a-heading-has-one-declaration.md) stopped
drawing Markdown blank lines. Ruling 2 is written so that it holds either way.

Whether ADR 0148 ruling 6's heading-parity calibration identity lands in the family ruling 4 creates.
This record only observes that it is absent.
