# Medatrax reference

Single source of truth for the Medatrax NP portal. [clinical-note](../skills/clinical-note/SKILL.md) emits entry fields in the order below so they can be tabbed straight into the form.

Portal: `np.medatrax.com` — **not** `medatrax.com`, which is the Anesthesia-defaulted marketing login. Evaluations live on a third host, `evaluations.medatrax.com`.

Picklist strings below are exact — match them character for character, including `Wyoming County Health Dept.` with its period and `New River Health - Oak Hill` with spaced hyphen.

## The requirement

Authoritative source is the program's [Practicum Hours Breakdown](https://bluefield.instructure.com/courses/5935/pages/practicum-hours-breakdown) on Canvas. Medatrax's own Objectives page says 360 for NUR 5144 and is **stale** — do not use it.

| Course | Documented | Planning target |
| --- | --- | --- |
| NUR 5144 — Prim Care Across the Lifespan | 260 | **270** |
| NUR 5042 — Transition into Leadership | 90 | 90 |
| | | **360 total** |

Ten hours are carried above the documented 260 deliberately, as a hedge against another stale page. Both courses start **2026-08-10**, due **2026-11-20** — about 14.5 weeks, so roughly 25 hours a week.

**The 360 starts from zero.** The 515:55 under Hours to Date is prior coursework (NUR5143, NUR5111, NUR5153) and none of it carries.

### NUR 5144 area breakdown

| Area | Hours |
| --- | --- |
| Family practice across the lifespan | 150 |
| Pediatrics | 20 |
| Obstetrics | 20 |
| Gynecology | 20 |
| Geriatrics | 50 |

These map onto the `Patient Time` picklist, so the age band chosen per encounter is what accrues each bucket. Getting it wrong misallocates the requirement.

### NUR 5042 is a different pipeline

Transition into Leadership is business plans, leadership styles, reimbursement and quality improvement — **no patient encounters**. Its hours go in the Time Log using the **`Narrative: (Leadership/Education Students and Transition Entries)`** field. Nothing in `clinical-note` applies to it.

### The 48-hour rule

> If you fall more than 48 hours behind with documentation in Medatrax you will be removed from clinical until you are caught up.

This is the constraint the whole toolchain exists to satisfy. A shift documented within 48 hours is the only acceptable outcome.

### Evaluations for 5144

One preclinical self-evaluation; **three** evaluations of the student by the preceptor; **three** of the preceptor by the student; **three** of the clinical agency by the student; one post-clinical self-evaluation. Cadence is every 90 clinical hours. With more than one preceptor, only the primary completes it.

## Forms

| Medatrax form | Program packet calls it | Branch |
| --- | --- | --- |
| `1. FNP: H & P` | H&P (v9) | [HP.md](../skills/clinical-note/HP.md) |
| `2. FNP: Comprehensive Soap Note` | SOAP NOTE (v6) | [SOAP.md](../skills/clinical-note/SOAP.md) |

**Minimum six H&P forms per course, then SOAP by choice.** Also permitted: Anxiety Screening Tool, CAGE, Depression Screening Tool.

`2. FNP: Comprehensive Soap Note` has six boxes — Subjective, Objective, Assessment/Analysis, Plan, **Intervention**, **Evaluation**. Verified across 25 sampled notes: Intervention and Evaluation are always empty. Leave them empty.

### Working rules

> The system auto saves forms every 2 minutes. Only have 1 form/window open at a time, as the auto save could override progress.

Draft outside Medatrax, paste once, close. And: **paging a report grid past its last page throws an Application Error** that requires backing out to the home page. Never guess a page index — walk the pager.

## Current state (read 2026-08-09)

| | |
| --- | --- |
| Total new patients | 582 |
| Total visits | 592 |
| `2. FNP: Comprehensive Soap Note` | 587 |
| `1. FNP: H & P` | 19 |
| Total patient time | 221:56 |
| Total time log | 515:55 |
| Student comments | 0 |

**No structured visit data exists at all.** Diagnosis Statistics returns "No data for this selection" across all courses, and every Add Visit Data category is empty — no ICD-10, no medications, no CPT, no Clinical Experience Check. Whether the new courses require it is worth confirming, since NUR 5144 objective 25 names "documentation, billing and coding".

Assignments: none. Time Log `Confirmed` column: unchecked on every row.

## Picklists — exact strings

**Preceptor** (`Last,First`, no space; the Time Log displays them with a space):

```
Cecil,Sharon      Green,Marie       Karper,Kelli      Lester,Miranda
Lindley,Juddson   Rose,Brittany     Sharp,Jessica     Sison,Julie
```

**Location / Site:**

```
Bluestone Medical Center      New River Health - Oak Hill
Welch Community Hospital      Wyoming County Health Dept.
```

**Interaction Level:** `Level 0` … `Level 5`. Every existing entry is Level 5, the top of the scale.

**Race/Ethnicity:** African American/Black · Asian · Bi-racial · Caucasian/White · Hispanic/Latino · Native American/Alaskan · Other · Pacific Islander

**Gender:** Male · Female · Transgender · Non-binary

**Age unit:** Days · Weeks · Months · Years

**Marital status at first contact:** Married · Consensual Union · Single · Separated · Divorced · Widowed

**Primary Payment Method:** Commercial insurance/HMO/PPO · Medicaid · Medicare · Military/IHS/PHS · Worker's comp · Self-pay/other · none

**Case Type:** Cardiovascular · Dermatology · Endocrine Disorders · ENT · GI · GU · Mental Health · Musculoskeletal · Neurological · Opthalmic · Physical · Respiratory · Obstetrics · Gynecology

**Patient Time** — the hours bucket, derivable from age:

```
Pediatric (0 – 17) Hours     Adult (18 – 60) Hours     Gerontology (60 and>) Hours
Obstetrical Hours            Women's Health
```

Age decides the band; a gyn or obstetric visit overrides it — a 35-year-old seen for hormone review logs as Women's Health, not Adult.

## Per-encounter fields (`patientedit.aspx`)

| Field | Type | Source |
| --- | --- | --- |
| Patient Reference | auto | **generated by Medatrax** — never supply a name |
| Visit Date | date | given |
| Course | picklist | given |
| Site | picklist | given |
| Preceptor | picklist | from the day file |
| Interaction Level | picklist | given |
| Race/Ethnicity | picklist | given |
| Gender | picklist | given |
| Age + unit | text + picklist | given |
| Marital status at first contact | picklist | given |
| Primary Payment Method | picklist | given |
| Case Type | picklist | given |
| Patient Time | picklist | derived from age and visit type |
| Start time / End time | text | given |
| Blood pressure | two text boxes | given |
| Respiratory Rate | text | given |
| Height | text | given |
| BMI | text | derived |

**There is no weight, heart rate, temperature or SpO2 field.** The note rubric wants a complete vital set, so those are filled and listed for confirmation. Anything Medatrax does carry is a given the note must match exactly.

Visit Time is derived from start and end, and varies — 0:30 to 0:45 on 10/20/2025, a flat 0:15 across 4/8/2026. The program expects roughly 2 patients per hour in family practice.

## Add Visit Data

```
ICD-10-CM        Medications        FNP Clinical Experience Check List
FNP EMT/ICD Codes    Procedure Codes    Drug List
```

Plus PMHNP-only categories. `ICD-10-CM`, `Procedure Codes` and `FNP EMT/ICD Codes` are where [icd10-cpt](../skills/icd10-cpt/SKILL.md) output lands.

## Reports

`reports/` holds 17. The useful ones:

- **`studentoverview.aspx`** — the best single view: patient totals, forms by type, time log. Start here.
- **`reports/timesheet.aspx?View=1`** — Hours to Date and a monthly breakdown.
- **`reports/summary.aspx`** — case minimums by category. Pick a category, **then click Submit**; it shows "No Data Entered" otherwise.
- **`reports/diagnosisstatistics.aspx`** — needs Submit too.

Several reports render nothing until Submit is clicked. An empty report is not evidence of no data until you have run it.

## Still to confirm

- [ ] Does the `Confirmed` column on Time Log rows matter for credit?
- [ ] Do the new courses require structured visit data (ICD-10 / Clinical Experience Check), given none exists today?
- [ ] `Review Evals` on `evaluations.medatrax.com` — not yet opened.
- [ ] `Clinical Experience Check List: Level of Proficiency` under Objectives — not yet read.
- [ ] MxPortfolio, Mail Center, Clinical Data Detail — not yet opened.
