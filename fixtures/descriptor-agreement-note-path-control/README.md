# Descriptor-agreement clinical-note path control

This is issue #1139's retained blind `clinical-note` path run over the neutral,
de-identified `fixtures/day-b/shorthand/case-01.md` input. The generating pass
saved the finished note and its private full coding worksheet in separate
stem-paired directories. A fresh reader received only the agreement brief and
wrote `agreement-read.json`; a non-authoring check accepted the record and the
bidirectional bind with exit 0.

`generation-record.md` records the generating pass. These files are fixtures,
not patient records.
