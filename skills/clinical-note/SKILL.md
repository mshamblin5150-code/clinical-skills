---
name: clinical-note
description: Turn ER-style clinical shorthand into a finished academic note — comprehensive SOAP or FNP H&P — plus the Medatrax patient entry fields. Use when the user pastes raw encounter shorthand, asks to "SOAP this", "write this up", "do an H&P", or needs an encounter formatted for Medatrax.
---

The input is **shorthand** — raw ER-style scratch for one encounter, typo-ridden, written at the bedside. The output is a finished note against a school rubric, plus the Medatrax entry fields.

These are **academic** notes documenting clinical hours, not the legal chart. The rubric demands complete sections — three-generation family history, age-appropriate screenings, a full ROS — that bedside shorthand never contains. Producing them is the job, and the tiers below are how it stays honest.

## Three tiers

Every line of the finished note is **given**, **derived**, or **filled**.

### Given

Present in the shorthand or the Medatrax entry. Passes through unchanged: numbers, doses, lab values, imaging results, stated findings, quoted patient speech. Never round, convert units, or soften a hedge — `prob viral` becomes `probable viral`, not `viral`.

Correct obvious misspellings of clinical terms as you read: `endometroises` → endometriosis, `oorphectomy` → oophorectomy, `prednisolono` → prednisolone, `tympansotomy` → tympanostomy. Transcription noise is not content. **Never "correct" a number.**

### Derived

Computed from a given by a rule with exactly one right answer:

- BMI from height and weight — or weight from BMI and height
- Age from date of birth and visit date
- Dose in mg from a mg/mL concentration and a volume
- Duration from a start date and the visit date

Show the arithmetic in the tier block. A value that does not compute is a **gap**, never an estimate.

### Filled

The rubric sections shorthand cannot supply: routine ROS negatives, normal exam of systems not documented, three-generation family history, social history, age-appropriate screenings, standard non-pharmacologic care, health promotion, return precautions. Generate these coherently with the givens.

One rule governs everything filled:

> **Filled content is unremarkable.**

The rule runs one way only. The clinician charts abnormals reliably and normals sometimes — `lungs are clear`, `well appearing` do appear in shorthand. So:

- **An abnormal in the note must be a given.** No exceptions. This is the direction that carries the safety.
- **A normal in the shorthand is still a given** — it means that system was examined. Keep it verbatim; do not move it to filled.
- **Silence is undocumented, never absent.** A section the shorthand omits means it was not written down that visit — not that the patient has nothing there. This holds everywhere, and it reads two ways depending on the section:
  - **Exam and ROS** — an unmentioned system is normal, because abnormals get charted.
  - **History, medications, surgical, family, social, allergies** — an omitted section is inferred from the rest of the encounter. A history of hypertension and no `meds:` line means a med rec was not done, so infer the likely regimen. Never write "none" where the shorthand is merely silent.

  Either way it gets filled, never raised as a gap.

Everything filled is therefore normal, absent, or not reported — and says so in those words: `no chronic illness reported`, `fever by history`, `no smoke exposure reported`, `no treatment-limiting cultural practice reported`.

Charted normals and filled normals read identically in the finished note. They are separated in the tier block so only the filled ones need confirming.

**Filled vitals** are permitted where the rubric requires a complete set and the encounter supplies only some. They must be within normal range for the patient's age, and every one of them is listed in the FILLED block for confirmation.

### What may be inferred

Inference is the job. What the shorthand omits should be **grounded** in what it contains — reasoned from the givens, not invented beside them.

Grounded, and expected:

- Route, frequency, and duration for a drug the shorthand names — `zithromax 200/5ml 3/4 t x 3 days` becomes azithromycin 3.75 mL PO **daily** for 3 days.
- A medication proposed in the **Plan** for a condition in the history — lisinopril where the history carries hypertension. This is the clinical reasoning being graded; make it.
- Standard supportive care, health promotion, and return precautions for the stated diagnosis.
- Screenings appropriate to the patient's age.
- The exam of a system the shorthand never mentions.

**One thing can never be inferred: a measurement.** Laboratory values, imaging results, and diagnostic test results were either obtained or they were not, and no clinical reasoning yields `estrogen 729`. Where testing is absent, write `No new testing today`. Never produce a number that would read as a result.

Separate two acts in the tier block, because they carry different weight:

- **Proposed** — a forward action: a drug started, a test ordered, a referral. Reasoning, and safe to be wrong about; the preceptor rules on it.
- **Asserted** — a claim about the patient's past: a medication they already take, a condition they already carry. Ground these in the history, then be specific. An absent `meds:` line usually means no medication reconciliation was done that visit, **not** that the patient takes nothing — infer the likely regimen from the conditions listed and name actual agents. This is the tier a preceptor checks hardest, so every asserted inference is listed.

## Steps

### 1. Intake and de-identify

Collect the shorthand and, if supplied, the Medatrax entry — it carries demographics and some vitals, and those are **givens** the note must match exactly.

Replace identifiers as you read: `[PT]` for name, `[DOB]`, `[MRN]`, `[SITE]`, `[PRECEPTOR]`. Keep age, sex, visit date, and everything clinical.

### 2. Expand the shorthand

Classify **every token** against [GLOSSARY.md](GLOSSARY.md) as expanded, verbatim, or unknown. An unknown token is carried forward as written and surfaced in the tier block — never dropped, never guessed at silently.

Completion: every token in the source is in exactly one of the three buckets.

### 3. Choose the branch

- **Comprehensive SOAP** → [SOAP.md](SOAP.md). The default.
- **FNP H&P** → [HP.md](HP.md). Use when the user says H&P, FNP, OLDCARTS, or asks for the long form.

Load only the branch's template.

### 4. Tier every element, then draft

Assign each element a tier before writing, then draft into the branch template. Obey the rubric's own formatting instructions inside that template exactly — they are the school's, not yours. Where it says short succinct statements and no sentences, write fragments.

### 5. Emit the Medatrax entry

Produce the field block from [../../reference/medatrax-fields.md](../../reference/medatrax-fields.md) in that file's field order, so it can be tabbed straight into the form. Any field the encounter does not supply is listed as missing rather than filled — Medatrax fields are administrative and a wrong one misattributes your hours.

### 6. Emit the tier block

Below the note, always:

```
--- FILLED (confirm before submitting) ---
<every generated line, grouped by section>

--- DERIVED ---
<value = the arithmetic>

--- GAPS ---
<what the rubric needs and nothing supplied>

--- UNKNOWN TOKENS ---
<verbatim, with any guess marked as a guess>

--- MISSING FOR MEDATRAX ---
<required entry fields not supplied>
```

### 7. Check

Walk the note line by line and confirm two things: every line carries a tier, and **no filled line contains an abnormality**. Report as one line — `N given, N derived, N filled, 0 abnormal filled` — then stop.

The second half of that check is the whole safety property. A filled abnormality is a finding you did not observe, in a note you sign.
