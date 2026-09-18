# Descriptor-agreement clinical-note path control

This is issue #1139's retained blind `clinical-note` path run over the neutral,
de-identified `fixtures/day-b/shorthand/case-01.md` input. The generating pass
saved the finished note and its private full coding worksheet in separate
stem-paired directories. A fresh reader received only the agreement brief and
wrote `agreement-read.json`; a non-authoring check accepted the record and the
bidirectional bind with exit 0.

ADR 0258 changed the worksheet shape after this run. Its differential and
refusal rows lack authored `ANCHOR` quotations, so the retained read now exits
2 with an unread remainder. The note, worksheet, and reader record remain
byte-for-byte as produced.

`generation-record.md` records the generating pass. These files are fixtures,
not patient records.

## Divergent run for drift row 24

The retained note is not rewritten to fit the later guideline-tail grammar. It
contains four refused classes: a sheet verdict naming a subject or source,
`grade` in place of `Class`, a narrative tail without `Class` and with a page,
and a `recalled` wording outside the documented set. Run
`python tools/differential_scan.py fixtures/descriptor-agreement-note-path-control/notes`;
its exit 1 is correct for this divergent row-24 record. The descriptor-agreement
reading above remains the purpose of the original path control.
