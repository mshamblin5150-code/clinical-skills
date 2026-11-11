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

The worksheets, the manifest code population and the selected level reach the reader only after
its record is placed. The reader applies icd10-cpt step 5 as the coding run does. Where the run
would ask the clinician a question, the reader writes an `EM-RULE` line naming both levels and
selects the lower one.

## The record

One element block per note, in the em-elements.md line format, at
`<run>/em-audit/rederivation/<note stem>.md`. The reader stages it; the orchestrator places it.
The re-derivation is complete when every note in the run has a placed record that
`python tools/em_audit.py <run>` reads without an unread remainder.
