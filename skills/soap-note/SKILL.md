---
name: soap-note
description: Convert ER-style clinical shorthand into a SOAP note. Use when the user pastes raw patient shorthand, asks to "SOAP this", "write this patient up", "turn this into a note", or needs an encounter formatted for Medatrax.
---

The input is **shorthand** — a clinician's raw ER-style scratch for one encounter. The output is a SOAP note plus a **gaps** list.

Two disciplines carry this skill, and everything below serves them:

- **Traceable** — every clinical claim in the note maps back to a token in the shorthand. Nothing arrives from clinical plausibility.
- **Gap** — what the shorthand does not say is surfaced to the clinician, never filled in. A gap in the note is safe; an invention in the note is a signed falsehood.

## De-identify

Render identifiers as placeholders as you read: `[PT]` for name, `[DOB]`, `[MRN]`, `[DATE]`, `[SITE]`, `[PRECEPTOR]`. Keep age and sex — Medatrax logs them and they are not identifiers on their own. Keep everything clinical.

## Steps

### 1. Expand the shorthand

Read [GLOSSARY.md](GLOSSARY.md) and classify **every token** in the shorthand as one of:

- **Expanded** — glossary hit, written out in full.
- **Verbatim** — numbers, vitals, lab values, dose/route/frequency, quoted patient speech. These pass through unchanged; never round, convert units, or normalize.
- **Unknown** — no glossary hit and not self-evident. Carry it forward *as written* and list it under Gaps.

Completion: every token in the source is in exactly one of the three buckets. A token you skipped is a token you silently deleted.

### 2. Sort into S / O / A / P

Place each expanded item into exactly one section:

- **S** — what the patient reports: HPI, pertinent positives/negatives *the shorthand states*, PMH/meds/allergies/social as given.
- **O** — what you measured or observed: vitals, physical exam findings, labs, imaging, ECG, point-of-care results.
- **A** — the impression the shorthand states. If the shorthand records no impression, **A is a gap** (see step 4).
- **P** — orders, meds given, procedures, consults, disposition, follow-up, patient education — as the shorthand states them.

Items that fit nowhere go to an **Unused** list, surfaced in step 4. Completion: every expanded item is in one section or in Unused — the counts reconcile against step 1.

### 3. Draft the note

```
SUBJECTIVE
Chief Complaint: <one line>
HPI: <narrative, past tense, third person>
ROS: <only systems the shorthand addresses>
PMH / PSH / Meds / Allergies / Social: <as given; omit any line the shorthand is silent on>

OBJECTIVE
Vitals: <verbatim>
Physical Exam: <only systems examined>
Diagnostics: <labs, imaging, ECG — verbatim values>

ASSESSMENT
<numbered problem list, most acute first>

PLAN
<numbered, aligned 1:1 with the assessment problems>
Disposition: <as stated>
```

Omit any heading the shorthand gives you nothing for. An empty heading invites the next reader — or the next agent — to fill it.

### 4. Emit the gaps block

Below the note, always, even when empty:

```
--- GAPS (not part of the note) ---
UNKNOWN TOKENS: <verbatim, with your best guess marked as a guess>
MISSING FOR MEDATRAX: <required fields the shorthand did not supply>
UNUSED: <shorthand that landed nowhere>
PROPOSED (verify before use): <differential or plan suggestions>
```

`PROPOSED` is the only place clinical reasoning of your own may appear, and it never migrates into the note body. The clinician moves it up, or does not.

### 5. Trace check

Walk the finished note clause by clause and name the source token for each. Completion: every clause has a source, and every source token from step 1 is accounted for in the note or in Unused. Report the check as one line — `Traced: N clauses, N sources, 0 unsourced` — then stop.

## Invariants

- A negative the shorthand does not state is an invention. "Denies chest pain" appears only if the shorthand says so.
- A normal finding is a finding. Do not write "lungs clear" for a system the shorthand never mentions.
- Never upgrade hedged language: "prob viral" becomes "probable viral", not "viral".
- Never supply an ICD-10 or CPT code in the note. Codes belong to the coding skill, where they carry a verification flag.
