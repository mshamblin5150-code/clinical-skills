# E/M audit check-off: <encounter id>

Blank template. `python tools/em_audit.py <run> --write` fills one copy per note from the coding
run records, in this section order, and writes it into the private run under `em-audit/`. A filled
sheet carries patient information and is never committed. The
[em-audit](../skills/em-audit/SKILL.md) skill owns the procedure; this file holds no patient data.

## Encounter

- Encounter: <id> (order <n> of <total>)
- Note file: <note filename>
- Service date: <service date>
- Setting: <office | emergency department>
- Patient status: <new | established>; evidence: <identity-map | medatrax | clinician-answer>; pointer: <pointer> (emergency department: not applicable)
- Coding freshness: PASS, checked <date>
- Rendered <date> from batch-codes.json, worksheets/<note stem>.md and <visible worksheet>
- Coding content fingerprint: <normalized SHA-256>

## Codes for entry

- [ ] <ICD-10-CM | CPT | HCPCS> <code> <official descriptor>
  - Anchor: <verbatim note text>
  - Source: <recorded (no SOURCE line) | the SOURCE line, filled inputs named>
  - Specificity: <the SPECIFICITY line>
  - Confidence: <the CONFIDENCE line>

## Codes resting on a filled anchor

<The worksheet block, verbatim, or: None recorded in the worksheet.>

## Codes refused, with what would establish them

<The worksheet refusal records, verbatim, each with what would establish the code and what was proposed instead.>

## Documentation that would support a more specific code

<The worksheet block, verbatim.>

## E/M level as the run selected it

- [ ] E/M code: <code>
- MDM sheet: <CPT MDM sheet filename>, SHA-256 <digest>
- Filled marks: <each [SOURCE: filled - data: ...] or [SOURCE: filled - risk: ...] mark, or none>
- ECG: <the ADR 0443 line for 93000 or 93005, or the no-ECG-code line>
- Clinician answers relied on: <recorded answers, or none held in a machine-readable run record>

Governing rules for this setting: <the CPT MDM sheet entries; for an office level also
reference/office-mdm-check.md; ADR 0308, 0376, 0442 and 0443>

The E/M paragraph of the note: <verbatim>

The visible Coding worksheet, as approved: <verbatim, with its problems, data and risk support and
the two-of-three conclusion>

## Independent re-derivation

<The re-derivation record, verbatim, then: Agreement: the re-derived level <code> agrees with the
selected level <code>. Or: DISAGREES: the re-derived level is <code> and the selected level is
<code>. Flagged for the clinician; no code or note was changed. Or: Not performed.>

## Clinician attestation

I have reviewed this check-off against my note. The codes and level above reflect the services I
documented for this encounter.

Clinician signature: ______________________________    Date: ______________
