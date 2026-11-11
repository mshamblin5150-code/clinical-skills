---
name: em-audit
description: E/M audit check-off for each coded note, rendered from the run's coding records with a required blind re-derivation of the level. Use when a coded run needs its check-offs before completion, when the clinician asks for an audit packet, or when an audit request needs a printable copy.
---

# E/M audit check-off

A **check-off** shows the auditor, for one coded note, every coding decision its run recorded:
each code with its anchor, source and specificity, the refusals, the E/M level element by element,
and each pre-approval question with the clinician's whole reply, ending on his signature line.
`tools/em_audit.py` derives it from the run's own records and compares it with a blind
**re-derivation**, so the check-off and the records always agree. It reports; codes, notes and
worksheets keep the content the coding run gave them.

The check-off covers the clinician's professional level by MDM: office 99202–99215 and
emergency department 99281–99285, as
[ADR 0445](../../docs/adr/0445-an-e-m-audit-check-off-is-rendered-from-the-coding-records-and-every-level-gets-a-blind-re-derivation.md)
rules.

> **Extension point: facility level.** A section applying the
> [ED facility grid](../../reference/ed-facility-grid.md) could follow the E/M section if the
> clinician asks for one. Today the grid stays a reference.

A check-off is a patient record. It lives in the run's `em-audit/` folder under `scratch/`,
names the note by encounter number, service date and note filename, and the
[blank template](../../reference/em-audit-checkoff.md) is the only tracked copy. The element block
and the pre-approval answers record it reads are defined in
[em-elements.md](../_shared/reference/em-elements.md).

## 1. Confirm the coding records

Run `python tools/em_audit.py <run>` on the coding run named in
[Clinical status, manifest, and Review sheet](../_shared/reference/clinical-manifest.md). For an
already approved run, add `--submission <key>`: a run approved before this check started reports
its missing element blocks and re-derivations as not graded.

Done when it prints `notes in run` and exits 0 or 1. Exit 2 with `refused` means the manifest or
receipt is missing or stale, or a private worksheet changed after its fingerprint was recorded;
icd10-cpt rebuilds them, then repeat this step. A refusal naming the CPT MDM sheet version is a
tool defect: report it to a maintainer and tell the clinician the check-offs cannot be rendered
until it is fixed. Exit 2 with a nonzero `unread remainder` means an input could not be read:
repair it as step 3 says, then repeat this step. Where no private worksheet fingerprint is
recorded, building the manifest again records it in its own file beside the manifest and leaves an
unchanged manifest byte-identical, so the approval holds. A run approved before this check started
gives `--submission`, which reports it not graded.

## 2. Re-derive every note

Follow [rederivation.md](rederivation.md) once per note.

Done when every note in the run has a placed re-derivation record.

## 3. Render the check-offs

```bash
python tools/em_audit.py <run> --write
```

Done when the report shows `absent 0` for both element blocks and re-derivations, `findings 0`,
and it exits 0, or exits 1 only for `DIFFERS` lines the clinician has seen with their note numbers
before approval. Each difference is his to rule on through icd10-cpt, and the check-off keeps it as
found. A `FINDING` is a defect in the coding record, not a ruling for him: correct the element
block through icd10-cpt, rebuild the manifest and render again before approval. On exit 2, the
`unread remainder` counts inputs the command could not read, and each check-off names its own:
repair what it names and render again. When an input cannot be repaired, tell the clinician which
note and record it names and that the check-off for that note is incomplete; it stays counted,
never dropped.

## 4. Hand over

Give the clinician the check-off paths. When an audit request needs a printable copy, export the
notes it names:

```bash
python tools/em_audit.py <run> --docx --note <order>
```

The Word copies go to the main checkout's `output/em-audit/<run name>-<path fingerprint>/`, one
folder per run even where two runs share a name, through the shared renderer, which refuses to replace a copy edited by hand until `--force`, and they carry every
asterisk and backtick of the copied record text as written. `--force` and `--output-dir` are
refused without `--docx`. A refused copy names its note number and how many copies were already
written.

Done when the clinician has the paths and every Word copy he asked for.

icd10-cpt's completion grades this skill's result as `the E/M audit check-offs`. What a clean
check-off does not establish is `em_audit.DECLARED_LIMITS`.
