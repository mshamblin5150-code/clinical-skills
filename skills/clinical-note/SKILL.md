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

## Conventions

**Favor the more complex note.** Where a differential could run three deep or five, run five. Where a finding could be left in Objective or carried into Assessment, carry it. Thoroughness is the tiebreaker, always.

**Marital status** is inferred from age and written into the Social History, not left as unreported.

**Social history** does not blanket-fill with "not reported". Say it where it is genuinely unknown and would matter; otherwise write the inference.

### Times

Ask up front, once per day file, and reuse for every encounter in it:

- **What time did the day start?** Note 1 is the first patient; each subsequent note follows in order.
- **How long was the shift?** Clinical days often run twelve hours.

Then assign each visit **15 to 40 minutes, in 5-minute steps**, by complexity — a brief recheck or simple sprain at 15–20, a routine acute visit at 25–30, a multi-problem or procedural visit at 35–40. Space the encounters across the shift rather than stacking them back to back, and report every start and end as estimated.

## Steps

### 1. Intake and de-identify

Collect the shorthand and, if supplied, the Medatrax entry — it carries demographics and some vitals, and those are **givens** the note must match exactly.

Replace identifiers as you read: `[PT]` for name, `[DOB]`, `[MRN]`, `[SITE]`, `[PRECEPTOR]`. Keep age, sex, visit date, and everything clinical.

### 2. Expand the shorthand

Classify **every token** against [GLOSSARY.md](GLOSSARY.md) as expanded, verbatim, or unknown. An unknown token is carried forward as written and surfaced in the tier block — never dropped, never guessed at silently.

Completion: every token in the source is in exactly one of the three buckets.

### 3. Choose the branch

The program sets the rule: **the first six documented encounters of a practicum course must be H&P forms.** After six, SOAP is the student's choice and is the practical default.

- **FNP H&P** → [HP.md](HP.md). The first six encounters of a course, or whenever the user says H&P, FNP, OLDCARTS, or asks for the long form.
- **Comprehensive SOAP** → [SOAP.md](SOAP.md). Everything after that.

Check the count before assuming. `Student Overview` in Medatrax reports forms by type; if the current course has fewer than six H&Ps, this encounter is an H&P regardless of what is convenient. State which branch you chose and why.

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

### 7. Check for drift

A note **drifts** when a finding goes in the front and never comes out the back — documented in the shorthand, carried dutifully into Objective, and then absent from the Assessment and the Plan. Drift is what a long day does to documentation, and catching it is the reason this skill exists.

Walk every row. **Emit a verdict for each one by name** — a summary line invites declaring the set passed without walking it.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | **Invention** | Every abnormal, diagnosis and clinically meaningful value in the note traces to a given |
| 2 | **Drift** | Every abnormal *in the shorthand* appears in the Assessment or the Plan |
| 3 | **Measurements** | No laboratory value, imaging result or diagnostic finding is filled |
| 4 | **Vitals** | Every vital outside the normal range for this age is addressed somewhere, not just recorded |
| 5 | **Sig** | Every drug carries dose, route, frequency and duration |
| 6 | **Red flags** | The return precautions name specific findings — *fever above 101, worsening flank pain, inability to keep fluids down* — never "red flags reviewed" |
| 7 | **Drug names** | Each drug reads as the shorthand wrote it, trade or generic, unconverted |
| 8 | **Band** | Patient Time follows Adult ≤ 59 / Gerontology ≥ 60 — overriding the Medatrax label's `Adult (18 – 60)` — with an obstetric or gynaecologic visit taking precedence |
| 9 | **Arithmetic** | Every derived value shows its working and recomputes correctly |
| 10 | **Entry** | Every Medatrax field holds a value or is listed under GAPS |

Row 2 carries the most weight and is the easiest to skip, because a drifting note reads perfectly well. Take each abnormal from step 2's expansion in turn and name where it lands. An abnormal that lands nowhere is either a diagnosis missing from the Assessment or a problem missing from the Plan — say which.

A failing row is reported, never quietly repaired into a pass.

Close with `N given, N derived, N filled` and stop.
