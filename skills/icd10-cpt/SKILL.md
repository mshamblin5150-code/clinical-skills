---
name: icd10-cpt
description: Propose ICD-10-CM diagnosis codes and CPT procedure codes from a documented encounter, each anchored to the note text supporting it. Use when the user asks for codes, needs to code an encounter, or mentions ICD-10, CPT, or E/M level.
---

Codes are **proposed**, never asserted. A code you supply is a suggestion the clinician verifies against the real code set before it is entered anywhere — this skill's output is a worksheet, not a coding decision.

Two disciplines make that verification fast:

- **Anchor** — every code quotes the note text that documents it. A code with no anchor is not a code, it is a guess about the patient.
- **Descriptor** — every code carries its official descriptor next to its number. When the number and the descriptor disagree, the clinician sees it instantly. This is the defence against a fluent, plausible, wrong code number, and it is the reason the descriptor is never omitted to save space.

## Steps

### 1. Extract codable elements

Read the note and list what is documented — not what is implied. For each, capture the exact supporting text.

- **Diagnoses** — from the Assessment. A symptom is codable as a symptom; it does not become a disease.
- **Procedures** — from the Plan and Objective: laceration repair, splinting, incision and drainage, ECG interpretation, foreign body removal, and so on.

Completion: every Assessment problem and every Plan procedure appears in the list.

### 2. Propose codes

For each element:

```
ICD-10  <code>  <official descriptor>
  ANCHOR: "<verbatim note text>"
  SPECIFICITY: <complete | needs: laterality / episode / site / severity>
  CONFIDENCE: <the code exists and I am confident of the number | verify this number>
```

CPT entries take the same shape, plus the note text documenting anything the code's requirements hinge on — repair length, wound complexity, time.

Rules:

- Code to the specificity the documentation supports and no further. If the note says "wrist fracture" with no side, the laterality is `needs: laterality`, not a coin flip between left and right.
- Say `verify this number` whenever you are working from recall rather than a code you are certain of. An honest flag costs the clinician ten seconds; a confident wrong code costs a rejected claim or a bad log entry.
- Never invent a documented finding to justify a code. If a code needs an element the note lacks, that goes in step 3.

### 3. Report what documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
<element the code set wants — laterality, wound length, time spent, episode of care>
  affects: <which proposed code>
```

This is the section with the most value in it. It tells the clinician what to document *at the bedside next time* so the encounter codes cleanly, which is worth more over a rotation than any single code proposal.

### 4. E/M level — only if asked

Offer the supporting elements (problems addressed, data reviewed, risk) and let the clinician assign the level. Do not select an E/M level unprompted.

## Completion

Every proposed code has a code number, a descriptor, an anchor, a specificity flag, and a confidence flag — five parts, no exceptions. A code missing any of the five is not ready to hand over.
