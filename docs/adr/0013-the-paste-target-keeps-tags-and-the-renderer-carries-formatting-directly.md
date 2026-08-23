# The paste target keeps tags, so the renderer carries heading formatting directly

Issue [#418](https://github.com/mshamblin5150-code/clinical-skills/issues/418)
recorded that headings render huge in the LMS paste while the `.docx` they came from is
correct APA. The ticket's account of the mechanism was right and it rested on a reasoned
model of two hops that nobody had measured. Both were measured on 2026-08-22, and the
measurement retired the fix the model implied.

The clinician ruled on 2026-08-23: **a document destined for a paste box carries its
heading formatting as direct run properties, and everything else is left alone.**

## What was measured

**Word to clipboard**, Word 16.0, four variants of one document differing only in how the
heading formatting is carried. A style named `heading N` becomes `<h1>`; a style stripped
of that name becomes `<p class=MsoNormal>` **with the bold gone**; a renamed style keeps
its class and puts the bold in the embedded `<style>` block; direct `<w:b/>` on the run is
the only form Word writes inline.

**Clipboard to Canvas**, one institution, one course, one theme. The paste sanitizer keeps
**tags only** — every `style` attribute, every `class` attribute and the whole `<style>`
block are discarded. No heading level renders bold at any level, and `<p><strong>` is the
only shape that comes out at body size and bold.

Together those say the obvious repair is wrong in a way no reading of either end would
have shown: removing the heading semantics removes the bold with it, because the bold was
never inline.

## The arrangement

`docx_write.py` takes `--bold-headings`. A heading renders as a directly-formatted bold
paragraph — bold, level 3 bold-italic, level 4 keeping its indent — with no named heading
style and no `outlineLvl`. Nothing else changes: the hanging indent, the page break, the
first-line indent and the centering are still emitted and are still discarded at the
destination. The flag is a third consumer of `blocks` rather than a second parser.

The flag is named for what it does rather than for where the document is going. A
destination-shaped name reads as a promise to mirror the target, which is the wider change
this ADR declines.

The Markdown is untouched, so `reference_scan.py` and `discussion_post_scan.py` keep
grading exactly what they grade today. The graded artifact and the posted artifact do not
diverge, because only the rendering moves.

`discussion_post_scan.py` takes `--docx <path>`, opens the archive and refuses a
`Heading{N}` `pStyle` in `word/document.xml`. Without the flag the row reports `not graded`
rather than `0`. A written instruction cannot fail, and this defect exists because a
forgettable manual step was the only thing between the renderer and a deduction; replacing
it with a forgettable flag would be motion rather than a fix.

Both external observations are recorded rather than remembered. The Word rows join the
calibration record with a Word-free shape tripwire, on [ADR 0008](0008-word-is-a-one-time-calibration-instrument.md)'s
arrangement. The paste-target observation gets its own dated record, and its disclosure —
the date, the institution, that it is one course and one theme — lives in the record's own
fields rather than in prose beside them. Tests assert the renderer shape only.

## What this does not settle

The gate proves a render was bold-headed. It cannot prove the paste target still draws it
as recorded; nothing offline reaches that, and the dated record is evidence rather than a
live check. It cannot tell which `.docx` was copied from, which is why the skill renders
one file rather than an APA copy beside a paste copy.

Centering and the hanging indent are unreachable in the box by any tool from any source.
The record is a figure nothing in this repo can re-derive, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape accepted
deliberately, and it is why the disclosure is a field.

## Rejected alternatives

**Strip the heading semantics and keep the style.** Rejected on measurement: it takes the
bold with it, because Word expresses style-borne run formatting only in the `<style>` block
that the paste target discards. This was the fix the ticket's model implied.

**Demote the headings to a lower level.** Rejected because no heading level in the paste
target renders bold, and the level that matches body size is still not bold. The answer is
not a heading rather than a different heading.

**Mirror the destination** — strip every property the target discards, so the document on
screen predicts the box. Rejected because it produces byte-identical results at the
destination and weakens the one visual check in the workflow, which compares a rendered
page against the Markdown and needs the document to still read as a paper.

**Render an APA copy beside a paste copy.** Rejected because nothing uploads or grades the
rendered file, so the APA copy has no consumer, and two near-identical files in one
directory reproduce this defect silently when the wrong one is copied.

**Drop headings from the initial post**, as replies already do. Rejected because
`reference_scan.py` is keyed on the reference heading and exits 2 without one, so it trades
a formatting defect for an ungraded reference list.

**Keep the manual demotion one more cycle.** Rejected because it protects against the one
thing it cannot see, and the reread of the posted version already sits one step later in
the workflow.
