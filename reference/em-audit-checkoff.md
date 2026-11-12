# E/M audit check-off: <encounter id>

Blank template. `python tools/em_audit.py <run> --write` fills one copy per note from the coding run
records, in this section order, into the private run under `em-audit/`; a filled check-off carries
patient information and stays there. The [em-audit](../skills/em-audit/SKILL.md) skill owns the
procedure and [em-elements.md](../skills/_shared/reference/em-elements.md) the record shapes.

## Encounter

- Encounter: <id> (order <n> of <total>)
- Note file: <note filename>
- Service date: <service date>
- Setting: <office | emergency department>
- Patient status: <new | established>; evidence: <identity map | Medatrax | clinician answer>; fingerprint <evidence SHA-256>
- Coding freshness: PASS
- Rendered from batch-codes.json, worksheets/<note stem>.md and <visible worksheet>
- Coding content fingerprint: <normalized SHA-256>

## Codes for entry

- [ ] <ICD-10-CM | CPT | HCPCS> <code> <official descriptor>
  - Anchor: <verbatim note text>
  - Source: <recorded (no SOURCE line) | the SOURCE line>
  - Specificity: <the SPECIFICITY line>
  - Confidence: <the CONFIDENCE line>
- Not for entry: <ICD-10-CM | CPT | HCPCS> <code> <descriptor>, with its recorded fields

## Codes resting on a filled anchor

> <the worksheet block, quoted>

## Codes refused, with what would establish them

> <the worksheet refusal records, quoted>

## Documentation that would support a more specific code

> <the worksheet block, quoted>

## E/M level, element by element

- [ ] E/M code: <code>
- MDM sheet: <CPT MDM sheet filename>, SHA-256 <digest>
- Filled marks: <each [SOURCE: filled - ...] mark, or none>
- ECG code: <office: the ADR 0443 line for 93000 or 93005, or no ECG code; emergency department: the ADR 0308 ruling 6 emergency department limb, and any billed ECG code shown as contrary to it>
- [ ] Problem: <entry id>, <counted | not counted>; note text "<note text>"; reason: <reason>
- [ ] Data: <entry id>, <counted | not counted>; note text "<note text>"; reason: <reason>
- [ ] Risk: <entry id>, <counted | not counted>; note text "<note text>"; reason: <reason>
- Rule applied: <rule>
- Answer relied on: <answer id>
- ECG: <limb>
- MDM: problems <level>; data <level>; risk <level>; two of three <level>
- Level: <code>

## Pre-approval questions and replies

- Question <answer id>; levels named: <codes, or none named>; reply check: <verified as a whole clinician message | not verified: the transcript was unreadable when it was recorded>

> <the question as shown, every line quoted>

Reply:

> <the whole reply, every line quoted; a blank line stays a paragraph break>

## Independent re-derivation

<The re-derivation element block, then: Compared (elements, MDM and level): the re-derivation agrees
with the worksheet. Or each DIFFERS line, flagged for the clinician.>

## Clinician attestation

I have reviewed this check-off against my note. The codes and level above reflect the services I
documented for this encounter.

Clinician signature: ______________________________    Date: ______________
