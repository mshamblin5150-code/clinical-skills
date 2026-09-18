# Descriptor-agreement positive control

This is issue #1139's retained blind positive run. A generating pass wrote the
note and private worksheet from a neutral de-identified input after the skill
edits. A separate reader received only the agreement brief and wrote
`agreement-read.json`; a non-authoring check accepted that record with exit 0.

ADR 0258 changed the worksheet shape after this run. Differential and refusal
rows here have no authored `ANCHOR` quotation, so the retained read now exits 2
with an unread remainder. The original note, worksheet, and reader record remain
byte-for-byte as produced.

The note and worksheet are paired by the `case-01` stem. `generation-record.md`
records the generating pass. These files are fixtures, not patient records.
