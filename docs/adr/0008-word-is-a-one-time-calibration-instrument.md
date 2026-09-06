# Word is a one-time calibration instrument
<!-- no-numbered-rulings -->

Issue [#424](https://github.com/mshamblin5150-code/clinical-skills/issues/424)
found that every verdict in `apa7.md` section 6 had been inferred from the renderer's
OOXML. That proves what the renderer emitted, not what Microsoft Word draws from it.
The same evidence class had already failed for numbered-list restarts on #422.

The clinician ruled on 2026-08-22: **installed Word is consulted once for each renderer
claim, and the observed result is committed with the Word version and date.** Word is a
calibration instrument, not a test dependency. Fixed OOXML behavior is not made safer by
opening Office on every CI run, and consumers must never need Office to use the skill.

## The arrangement

`python tools/docx_word_probe.py --word` renders synthetic probes, opens them through
Word COM, and prints the paragraph, section, header, field, table, and border properties
Word reports. The command is maintainer-only and runs only on a Windows machine with
Word installed. It imports no consumer module into Word; instead, it calls the existing
renderer and observes the resulting documents from outside.

The dated result is
`skills/practicum-case-study/reference/word-renderer-calibration.json`. Each section-6
row carries its own calibration key, date, Word version, verdict, observed Word behavior,
and the semantic XML shape that produced that behavior. The record is evidence, not an
executable Word test.

`python tools/docx_word_probe.py --shapes` opens no Word process. It reports the current
renderer shapes, and `tools/test_docx_word_probe.py` compares every one with the shape in
the dated record. If the renderer leaves the measured set, the test tells the maintainer
to retake that row with Word. A new section-6 row also fails until it has a distinct
calibration identity and record.

## What the calibration changed

The committed Word record confirmed every applied row and declared limit in section 6.
It also settled a separate destination-guard premise after #675 repaired the probe to
edit before saving: Word changed the archive part set and the guard refused the saved
document. The original no-op was not a measurement of a save. `docx_write.NOT_GUARDED`
now records the surviving limit generically: an editor that preserves exactly the
renderer part names is not detected. A Word owner file still protects a document while
it is open.

## Rejected alternatives

**Keep the XML-only behavior tests as the measurement.** Rejected because the renderer
and those tests read the same specification and representation. Agreement between them
does not say what Word displays.

**Keep a permanent Word integration test.** Rejected by the clinician. It would put
Office on the repository's verification path and repeat a settled calibration without
reducing uncertainty.

**Use a simulator as evidence.** Rejected. A simulator written from the same OOXML rules
as the renderer has the same correlated-error problem. It may help inspect a shape; it
cannot promote a row to applied.

Correction, 2026-09-01: #675 and ADR 0086 established that the earlier destination-guard
probe performed no edit. The repaired probe edits before saving, and the Word save changes
the part set and is refused. The one-time calibration ruling is unchanged.
