# Medatrax reference

Single source of truth for the Medatrax NP portal. [clinical-note](../skills/clinical-note/SKILL.md) emits entry fields in the order below so they can be tabbed straight into the form.

Portal: `np.medatrax.com` — **not** `medatrax.com`, which is the Anesthesia-defaulted marketing login. Evaluations live on a third host, `evaluations.medatrax.com`.

### Getting in

**Use the clinician's real Chrome, not an in-app or preview browser.** The password manager autofills the Medatrax login form there. A fresh in-app browser carries no session and no stored credentials, so the login page is the only page it will ever reach — the tools to reach for are the Chrome ones (`claude-in-chrome`), not the built-in browser pane.

The agent **never types credentials**. Open `np.medatrax.com/default.aspx` in Chrome, let the password manager populate both fields, click Login, and go no further into the account.

`default.aspx` renders the public marketing page whether or not a session exists, so it is useless as an auth check. Load `/login/patient.aspx` instead: the patient list means signed in, a bounce back to the form means signed out.

**Every authenticated page lives under `/login/`.** `np.medatrax.com/patient.aspx` returns Page Not Found; `np.medatrax.com/login/patient.aspx` is the patient list. Page names recorded below are relative to that prefix:

| Page | URL |
| --- | --- |
| Patient Visit List | `/login/patient.aspx` — date-range and course filters, 50 rows per page |
| Patient Detail | `/login/patientdetail.aspx?patid=…&visitid=…` — the whole visit record on one page, read-only |
| Time Log entry | `/login/timesheetentry.aspx` |
| Reports index | `/login/reports` |

**Patient Detail is the field-by-field view.** It renders every per-encounter field as text without opening an edit form, which makes it the safe way to read an existing encounter.

### Navigating the portal

Five behaviors that decide whether a sweep works at all. Each one has cost a pass.

1. **`patient.aspx` opens with `Course` preset to a single course**, and every date search runs inside it — so an encounter in any other course reads as "not found". Set `Course` to `(All Courses)` before searching; it persists for the session. One whole pass matched 1 of 10 encounters and concluded the rest were unfindable, on nothing but this.
2. **`/login/forms/` has a lower panel — *"To retrieve an existing form"*.** It filters every submitted form by type, patient, location, course and plan keyword, and it is the only index of *form type* that does not require opening visits one at a time. Setting Form to the H&P and clicking Search returns all 19 in a single postback. **Do not touch the upper panel** — that one is `Open New Form` and offers only the live course.
3. **`patientdetail.aspx` `<Prev` / `Next>` walk the currently filtered patient list in entry order** (`Created` ascending), not grid order. One search plus five `Next>` reads a whole batch, turning a per-visit sweep from four round trips per patient into two. The entry ordering is itself evidence — it is how the six contiguous H&Ps were found.
4. **`patientdetail.aspx?patid=…` alone throws an Application Error.** `visitid` is required, and the only way to get one is the `Select$N` postback.
5. **Drive the grid by element id, not by accessibility ref** — ids survive postbacks where refs do not: `patList_txtFrom`, `patList_txtTo`, `patList_btnSearch`, `__doPostBack('patList$gvPatList','Select$N')`.

**Do not ask the page for hrefs or raw markup.** A `javascript_tool` call returning page HTML that contained `resultid=` query strings came back `[BLOCKED: Cookie/query string data]`. Returning a short slice of `innerText` works fine.

Picklist strings below are exact — match them character for character, including `Wyoming County Health Dept.` with its period and `New River Health - Oak Hill` with spaced hyphen.

**Scope.** This file currently documents Medatrax for *reading* — what the fields are, what they accept, and how a note supplies them. Entering encounters through the portal is out of scope for this pass, **not permanently**: the field table and selection rules below are written to serve entry when it lands, which is the destination of the whole toolchain.

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

Draft outside Medatrax, paste once, close.

**Reading a submitted form is safe.** The `View` link opens `forms/ComprehensiveSoapNoteV2.aspx?resultid=…`, and that page renders the real edit form — enabled textareas, autosave and all — which reads alarming and is not. Autosave overwrites *progress*, and there is no progress unless something was typed. Open a submitted note, read it, leave it: nothing changes. The rule above is about two windows racing each other during entry, not about looking.

So the reference half of a fixture set is read straight off these pages. `resultid` comes from the `View` link on Patient Detail; there is no other index of them, and it is never guessed — a wrong `resultid` is another student's note.

**View the form. Do not fetch its HTML.** Requesting the page and parsing the markup looks equivalent and is not: what a submitted note actually contains is what the *rendered* fields hold, and treating the served HTML as the answer is how a field that populates after load gets silently recorded as empty. Open the page, read the field values off it. The caution that makes this tempting — autosave — is the paragraph above, and it does not apply. And: **paging a report grid past its last page throws an Application Error** that requires backing out to the home page. Never guess a page index — walk the pager.

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

**The override has never been applied. Swept 2026-08-09: 30 of 30.**

Every `Gynecology` and `Obstetrics` visit in the entire record sits on an age band. Twenty-seven gynecologic visits — 23 on `Adult (18 – 60) Hours`, 4 on `Gerontology (60 and>)` — and three obstetric visits, all on `Adult`. **`Women's Health` and `Obstetrical Hours` have never been used once.** Ages ran 18 to 79 and the age rule was applied correctly throughout, so this is not carelessness; the override simply is not part of the habit.

Those hours are not recoverable and do not need to be. All 30 belong to NUR5153, NUR5111 and NUR5143, and the 360 starts from zero — correcting them shuffles buckets inside closed courses. What matters is that NUR 5144 wants 20 Gynecology and 20 Obstetrics hours in their own buckets, and the habit has a perfect record of not supplying them.

**No report exposes Patient Time.** Case Type Report gives case type, date and reference; the Statistics Report has a Case Type view but no Patient Time view; Data Totals covers visit-data categories, all empty. The value appears only on `patientdetail.aspx`, one visit at a time.

**To audit a specific visit fast:** `patList:txtSearch` on `/login/patient.aspx` accepts a Patient Reference and returns that single visit at `Select$0`. That is what makes a per-visit sweep possible without walking twelve pages of fifty.

## Per-encounter fields (`patientedit.aspx`)

| Field | Type | Source |
| --- | --- | --- |
| Patient Reference | auto | **generated by Medatrax** — never supply a name. Match a returning patient through the identity map; see below |
| Visit Date | date | given |
| Course | picklist | given |
| Site | picklist | given |
| Preceptor | picklist | from the day file |
| Interaction Level | picklist | given |
| Race/Ethnicity | picklist | declared default — see Field selection rules |
| Gender | picklist | given |
| Age + unit | text + picklist | given |
| Marital status at first contact | picklist | given |
| Primary Payment Method | picklist | declared pattern — see Field selection rules |
| Case Type | picklist | given |
| Patient Time | picklist | derived from age and visit type |
| Start time / End time | text | estimated — see Field selection rules |
| Blood pressure | two text boxes | given, or filled — see Field selection rules |
| Respiratory Rate | text | given, or filled — see Field selection rules |
| Height | text | given, or filled — see Field selection rules |
| BMI | text | derived from the height and a weight, filled or given |

### The identity problem

**Medatrax has no name field, anywhere.** `Patient Reference` is generated, opaque, and the only handle the portal has on a person. Nothing in the record says who a patient is.

So a returning patient can only be recognized from outside the portal, and an encounter entered without that match **creates a second patient**. No warning, no merge, and afterwards the two records are indistinguishable. The clinician's identity map — name to Patient Reference, kept in `scratch/` — is the only thing standing between a repeat visit and a duplicate.

**The arithmetic shows it has not been standing there.** `studentoverview.aspx` reports **582 patients against 592 visits**: ten repeat visits across the whole record. Fifteen Patient Detail pages opened at random all read `1 Visit(s)`. A year of family practice does not produce ten returning patients, so most of that gap is duplicates already made.

Set the map up with `/setup-clinical-skills`. The encounters that cannot be fixed retroactively are the ones whose day-file note carried no name.

**There is no weight, heart rate, temperature or SpO2 field.** The note rubric wants a complete vital set, so those are filled and listed for confirmation. Anything Medatrax does carry is a given the note must match exactly.

Visit Time is derived from start and end, and varies — 0:30 to 0:45 across one sampled day, a flat 0:15 across another. The program expects roughly 2 patients per hour in family practice.

### Field selection rules

Some fields are administrative and never appear in bedside shorthand. Without a stated rule the skill reports them missing on every note, which is what trains a clinician to skim the block that is supposed to catch real omissions. Each one below has a rule, so it is answered once here rather than ten times a day.

**Primary Payment Method — a site, age and status pattern, corrected on sight.**

Payer data is not visible at the bedside. The value is *declared*, not derived — but it is not a constant either. The flat `Medicaid` default that used to sit here was wrong close to two times in five: all eleven encounters on a sampled day were read field by field on 2026-08-09 and carry **six `Medicaid`, three `Commercial insurance/HMO/PPO`, two `Medicare`** — including `Medicare` on a 23-year-old.

Read off the clinician's own entries, the pattern below fits 16 of the 18 H&P encounters and most of the SOAP comparison set:

| Site | Rule |
| --- | --- |
| Bluestone | `Self-pay/other` |
| Welch | `Medicaid` for pediatric patients and single adults · `Commercial insurance/HMO/PPO` for married working-age patients · `Medicare` from about 60 |

`Worker's comp` overrides all of it where the shorthand documents a work-related injury — and that exception is a **given**, read from the note, not a guess about the payer.

**This is not the rejected alternative.** The idea turned down earlier was varying the value to produce a realistic-*looking* payer mix, which fabricates administrative data to pass as plausible. This is a pattern read off the clinician's own record, and it is right more often than the constant was. Guessing a spread is invention; reproducing an observed one is not.

Still `FILLED·asserted`, still a starting value that genuinely needs a glance, still never under GAPS — it is filled, not missing.

**Race/Ethnicity — `Caucasian/White`, corrected on sight.**

Unlike payer, this one is observable — the clinician saw the patient. It simply never gets written down.

**The default is wrong about once in four.** On a sampled day, eight of eleven encounters were `Caucasian/White` and three `African American/Black`. Treat it as a starting value that genuinely needs a glance, not one that is usually safe to wave through — which is why it is filled under `FILLED·asserted` rather than written straight into the field.

**Blood pressure, Respiratory Rate, Height and BMI — filled, not left blank.**

The four vital and measurement fields are filled where the encounter does not supply them, to the value that patient most plausibly had. The rule and its cost — a filled vital that lands abnormal is worked up in the note like any other abnormal — are in [clinical-note](../skills/clinical-note/SKILL.md) under *Filled vitals, body measurements and the pain score*. Do not restate it here; do apply it. **Medatrax holds no severity field**, so the third member of that class never reaches this block — it lives in the note's HPI and in `FILLED·asserted`, and it is named here only so the section title reads as the same rule.

**The clinician's own practice settled this.** The 2025 Spring batch leaves `Height` and `BMI` blank; **every 2025 Fall and 2026 Spring encounter fills both**, inventing a height where the shorthand carries none. His words: *"the newer records everything is filled out."* The blank ones are the older habit, not the standard — the same shape as the flat visit lengths under Visit Time.

Order matters for the pair: pick a plausible height, pick a plausible weight, then **derive** the BMI and show the arithmetic. Never pick a BMI and read the height and weight backwards out of it. There is no weight field in Medatrax, so the weight lives in the note only — but the BMI in the field must recompute from it.

**Start time / End time — estimated, not missing.**

The Times convention in [clinical-note](../skills/clinical-note/SKILL.md) assigns each visit 15–40 minutes across the shift and reports every time as estimated. Estimated is a property of the value, not the absence of one, so these do not belong under GAPS — a note that lists them there is spending a slot announcing that the skill obeyed its own instruction.

**Not every administrative field is equal.** `Patient Time` is the one where a wrong value has a real consequence: it feeds the NUR 5144 area breakdown, so an error there misallocates clinical hours. Payment method and race/ethnicity feed no hours bucket at all. Treat them accordingly — `Patient Time` is worth stopping for, these are not.

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
