---
name: em-audit
description: Render the coding decisions of a finished note as a per-note E/M audit check-off the clinician can hand to an auditor, with an independent re-derivation of the professional E/M level. Use when the clinician asks for an audit packet, an E/M audit sheet, or how the level on a note was derived, for one note or a whole run, at any time after the coding run wrote its records.
---

# E/M audit check-off

The check-off shows, code by code and element by element, how the coding run decided every code on
a finished note and how it reached the professional E/M level. It is rendered from the records the
coding run already wrote, so the packet and the records cannot disagree:

- the coding manifest `batch-codes.json` and its passing `batch-freshness.json` receipt;
- the visible `Coding worksheet`, with its problems, data and risk support and two-of-three conclusion;
- the private anchored worksheet `worksheets/<note stem>.md`, with every anchor, `SOURCE`,
  `SPECIFICITY` and `CONFIDENCE` line, the filled-anchor block and the refusal records;
- the office patient-status evidence, and the E/M paragraph of the note with any
  `[SOURCE: filled - ...]` mark.

[icd10-cpt](../icd10-cpt/SKILL.md) produces the sheet when it writes those records; this skill also
re-renders it later for one note or a whole run. It never changes a code, a note or a worksheet.

**Scope: the clinician's professional level only.** Office 99202–99215 and emergency department
99281–99285, both by MDM under [icd10-cpt](../icd10-cpt/SKILL.md) step 5, the committed
[CPT MDM sheet](../../reference/cpt-em-mdm-2026.md) and, for an office level, the
[office check sheet](../../reference/office-mdm-check.md). The hospital facility level is not
produced; the [ED facility grid](../../reference/ed-facility-grid.md) stays a reference, as
[ADR 0444](../../docs/adr/0444-the-repository-carries-a-tested-ed-facility-grid-and-office-mdm-check-sheet.md) rules.

> **Extension point: facility level.** A section applying the ED facility grid to an emergency
> department encounter could follow the E/M section if the clinician asks for one. It is not built,
> and nothing here selects a facility level.

**A filled sheet is a patient record.** It is written only into the private run under `em-audit/`,
beside the run's other records under `scratch/`, and is never committed. Only the blank
[template](../../reference/em-audit-checkoff.md) is tracked. The command prints counts only. Standing
rules 1 and 6 in [AGENTS.md](../../AGENTS.md) apply to every file this skill writes.

## Steps

### 1. Find the run and its records

Use the run directory that holds the manifest, receipt, notes, visible worksheets and private
worksheets named in [Clinical status, manifest, and Review sheet](../_shared/reference/clinical-manifest.md).
A run without a built manifest and a passing freshness receipt is not ready: icd10-cpt finishes its
completion first. Select every note, or one or more notes by their one-based order.

### 2. Re-derive the level before reading the worksheet

The independent re-derivation is the second section of the sheet. It is optional, and the sheet
says `Not performed` without it. When it is done, this **Second reader** applies
[standing rule 6](../../AGENTS.md), first reads [sourcing.md](../_shared/reference/sourcing.md), and is
never the context that wrote the worksheet. Its brief carries only:

- the finished note and its tier block, with the E/M paragraph and any `Coding worksheet` section removed;
- the setting and office patient status from the manifest, and the clinician's recorded pre-approval answers for that note;
- [icd10-cpt](../icd10-cpt/SKILL.md) step 5, the CPT MDM sheet and, for an office level, the office check sheet.

It never receives the visible or private worksheet, the selected code or the manifest code
population until its record is placed. It applies the same rules the coding run applied: what the
clinician addressed, documented-action wording, the filled-mark counterfactuals, directed agents and
the ECG rule. It cites CPT entries by id and never copies CPT text. A question the run would have
asked becomes a `RULE` line naming both levels; the reader asks the clinician nothing.

The reader stages the record and the orchestrator places it at
`<run>/em-audit/rederivation/<note stem>.md`, one record per note, in this shape:

```text
RE-DERIVATION: <manifest note id>
SETTING: <office | emergency department>
STATUS: <new | established | not applicable>
PROBLEM: <CPT sheet entry id> - "<verbatim note text>" - <counted | not counted: reason>
DATA: <CPT sheet entry id> - "<verbatim note text>"
RISK: <CPT sheet entry id> - "<verbatim note text>"
ANSWER: <the recorded clinician answer relied on, or none>
RULE: <the house rule, counting note, documentation check or ADR applied>
ECG: <the ADR 0443 limb applied, or not applicable>
MDM: problems <level>; data <level>; risk <level>; two of three <level>
RE-DERIVED LEVEL: <code>
```

Repeat `PROBLEM`, `DATA`, `RISK`, `ANSWER` and `RULE` as needed; write `DATA: none documented`
where nothing counts. Reasons say "not documented", never "not done". The renderer reads the
record only with `PROBLEM`, `DATA` and `RISK` lines, one `MDM` line and one `RE-DERIVED LEVEL`
line, and computes agreement itself.

### 3. Render the check-off

```bash
python tools/em_audit.py <run> --write
python tools/em_audit.py <run> --write --note <order>
```

The command validates the run as approval does, then writes `<run>/em-audit/<note stem>.md` per
selected note, section by section in the template order. Without `--write` it only counts.

- **Exit 0:** every selected sheet rendered, and no re-derivation disagrees.
- **Exit 1:** a re-derived level differs from the selected level, or a record carries content
  damage. Show the clinician each disagreeing note number and both levels. Change nothing: whether
  the code changes is his ruling, made through icd10-cpt. Repair a damaged record and render again.
- **Exit 2:** the manifest or receipt is missing or stale, a note number is unknown, or a
  re-derivation record lacks its shape (`unread remainder` counts it). A stale run is rebuilt by
  icd10-cpt, never by this skill.

What a clean render does not establish is `em_audit.DECLARED_LIMITS`.

### 4. Hand over

Give the clinician the sheet paths, never their contents in a ticket or chat transcript outside the
run. He reads each sheet against his note and signs the attestation line.

## Completion

Every selected note has a sheet written by an exit 0 render, or by an exit 1 render whose
disagreements were shown to the clinician. Every re-derivation record present was read, with
`unread remainder 0`. No code, note or worksheet changed, and every private staging path is removed.
