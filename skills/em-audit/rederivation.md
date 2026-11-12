# The re-derivation

Every coded note gets one re-derivation: an independent reading of its E/M level, written as an
element block before the reader sees how the coding run decided. This **Second reader** applies
[standing rule 6](../../AGENTS.md), first reads [sourcing.md](../_shared/reference/sourcing.md),
and is a different context from the one that wrote the worksheet.

## The brief

The brief carries exactly these, and the reader works from them alone:

- the finished note and its tier block, with the E/M paragraph and any `Coding worksheet` section cut out;
- the setting and office patient status from the manifest;
- the entries for that note in the run's [pre-approval answers](../_shared/reference/em-elements.md#the-pre-approval-answers-record) record;
- [icd10-cpt](../icd10-cpt/SKILL.md) step 5, the CPT MDM sheet, the
  [office check sheet](../../reference/office-mdm-check.md) for an office level, and
  [em-elements.md](../_shared/reference/em-elements.md).

The brief is given after the note's last pre-approval answer is recorded; an answer recorded later
makes the placed record stale, and the note is re-derived from a new brief. The worksheets, the
manifest code population and the selected level reach the reader only after its record is placed. The reader applies icd10-cpt step 5 as the coding run does. Where the run
would ask the clinician a question, the reader writes an `EM-RULE` line naming both levels and
selects the lower one.

## The record

One element block per note, in the em-elements.md line format, at
`<run>/em-audit/rederivation/<note stem>.md`. The reader stages it; the orchestrator places it.
The re-derivation is complete when `python tools/em_audit.py <run>` reports `absent 0`,
`damaged 0` and `findings 0` among the re-derivations, and its `agree` and `differ` counts add up to
the notes in the run: a re-derivation is placed for every note, with no re-derivation line unread
and no re-derivation finding. A `FINDING (re-derivation)` line names one of two defects. A record
that contradicts itself (an entry id, a quotation, its MDM line or its level against its own
elements) is repaired by the reader against the note, never toward the worksheet, and placed again.
A record placed before the note's last pre-approval answer is discarded: a fresh reader re-derives
the note from a new brief that carries that answer, and its record is placed. Editing or re-saving
the old record clears that finding without the answer ever being read, so it is never the repair. A level or
element that differs from the worksheet is a `DIFFERS` line the clinician sees, never a finding.
Other causes the
`unread remainder` counts, such as an unreadable answers record or a private worksheet
fingerprint not yet recorded, go to their own repair in em-audit step 1 and do not hold this step.
