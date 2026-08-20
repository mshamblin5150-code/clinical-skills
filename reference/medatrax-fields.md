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
2. **`/login/forms/` has a lower panel — *"To retrieve an existing form"*.** It filters every submitted form by type, patient, location, course and plan keyword, and it is the only index of *form type* that does not require opening visits one at a time. Setting Form to the H&P and clicking Search returns the whole matching set in a single postback rather than paging it. **Do not touch the upper panel** — that one is `Open New Form` and offers only the live course.
3. **`patientdetail.aspx` `<Prev` / `Next>` walk the currently filtered patient list in entry order** (`Created` ascending), not grid order. One search plus five `Next>` reads a whole batch, turning a per-visit sweep from four round trips per patient into two. The entry ordering is itself evidence — it is how the six contiguous H&Ps were found.
4. **`patientdetail.aspx?patid=…` alone throws an Application Error.** `visitid` is required, and the only way to get one is the `Select$N` postback.
5. **Drive the grid by element id, not by accessibility ref** — ids survive postbacks where refs do not: `patList_txtFrom`, `patList_txtTo`, `patList_btnSearch`, `__doPostBack('patList$gvPatList','Select$N')`.

**Do not ask the page for hrefs or raw markup.** A `javascript_tool` call returning page HTML that contained `resultid=` query strings came back `[BLOCKED: Cookie/query string data]`. Returning a short slice of `innerText` works fine.

Picklist strings are exact — match them character for character, here and in the per-account lists this file points at. Site names are where that bites: on this account one entry ends in a trailing period and another sets its hyphen with spaces around it. A near-miss does not match.

**Scope.** This file currently documents Medatrax for *reading* — what the fields are, what they accept, and how a note supplies them. Entering encounters through the portal is out of scope for this pass, **not permanently**: the field table and selection rules below are written to serve entry when it lands, which is the destination of the whole toolchain.

## Hour requirements and deadlines

**The program's own hours breakdown is authoritative, not Medatrax's Objectives page** — on one account that page was stale by 100 hours, so a count read off the portal was wrong by more than a third of a course. Which courses, their documented hours, any planning hedge above the documented figure, the term dates, and whether prior hours carry or the count starts from zero are all per-program. [setup-clinical-skills](../skills/setup-clinical-skills/SKILL.md) step 3 collects them and `scratch/medatrax-profile.md` holds them.

**A course may carry an area breakdown** — family practice, pediatrics, obstetrics, gynecology, geriatrics, in hours. Those areas map onto the `Patient Time` picklist below, so the band chosen per encounter is what accrues each bucket and a wrong band misallocates the requirement. The breakdown itself is per-program and is in the profile.

**A course with no patient encounters logs its hours in the Time Log**, not through an encounter form, using the `Narrative: (Leadership/Education Students and Transition Entries)` field. A leadership or transition course is the usual shape — business plans, reimbursement, quality improvement — and nothing in [clinical-note](../skills/clinical-note/SKILL.md) applies to it.

### The documentation deadline

**Programs commonly impose one, and it is the constraint this whole toolchain exists to satisfy.** One program removes students from clinical until they are caught up if they fall more than a stated number of hours behind in Medatrax. Yours, its number, and its exact wording are in the profile; documenting a shift inside that window is the only acceptable outcome.

*(That sentence used to be this program's handbook quoted verbatim, with the number in it. It moved on [#226](https://github.com/mshamblin5150-code/clinical-skills/issues/226), 2026-08-19, and the motivation stayed — deleting the paragraph outright would have taken the reason the tooling exists out of the file a second clinician inherits, which is what decision 1 was about.)*

### Evaluations

Count, cadence and who completes them are per-program and in the profile. The one rule that is not: **with more than one preceptor, only the primary completes the preceptor-facing evaluations.**

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

## What the portal does with an empty account

**No structured visit data need exist at all**, and how the portal reports that is the part worth recording. Diagnosis Statistics returns "No data for this selection" across all courses rather than an empty table, and every Add Visit Data category comes back empty — no ICD-10, no medications, no CPT, no Clinical Experience Check. A reader who takes that message for a filter problem will go looking for the filter. Assignments and the Time Log `Confirmed` column behave the same way: absent and unchecked read identically to not-yet-loaded.

Whether a course *requires* structured visit data is worth confirming — a course objective naming "documentation, billing and coding" is what would make it mandatory, and the objective list is per-program and in the profile.

**Seven totals used to sit here and were deleted rather than moved** — new patients, visits, the per-form counts, patient time, hours to date, student comments — on [#235](https://github.com/mshamblin5150-code/clinical-skills/issues/235)'s ruling of 2026-08-19. Not one was Medatrax behavior; they were what one account held on one afternoon, in a file that opens *single source of truth for the Medatrax NP portal*. **Deleted and not moved, which was the decision rather than the default**: each is re-derivable in a single page load from the account it belongs to, and `scratch/medatrax-profile.md` already carries a later and more carefully reasoned form count than the one here — so relocating a staler figure beside it would have planted two totals that disagree with nothing to reconcile them.

**The hours-to-date figure was the sharp one.** [#226](https://github.com/mshamblin5150-code/clinical-skills/issues/226) moved the *ruling* about what that figure does and does not carry to the profile and left the figure thirty lines above where its explanation had been — so the file held an unexplained account-specific integer where it had held an explained one, which is worse than either end state. Naming it again to explain its removal would put it straight back, so this paragraph points and does not quote. `tools/test_skill_agreement.py` refuses an hours-to-date total anywhere in this file, and that limb reaches one shape rather than the class: a bare count of visits is an integer and has none.

**Two of the seven appeared elsewhere in this file, and [#244](https://github.com/mshamblin5150-code/clinical-skills/issues/244) settled them on 2026-08-19** — the patient-and-visit totals in *The identity problem* and the H&P count in *Navigating the portal* above, both of which used a figure to make an argument about how the portal behaves rather than to report a standing. **Neither was deleted the way the seven were, and that is the ruling rather than a softer version of it**: the arithmetic and the one-postback behavior are Medatrax behavior and stayed, and only the integers went — abstracted where the inference needed them, replaced by the behavior itself where any integer would have done. The patient-and-visit reading is one account's and lives in [setup-clinical-skills](../skills/setup-clinical-skills/SKILL.md) step 6, which this file now points at rather than copies. **This section was swept and the file was not**, which is the same partial instrument #235 was filed about arriving inside #235, and it is why #244 was found by pointing a reviewer at the file rather than at the diff. *(#235's own note here cited a section called `Duplicate patients`, which this file has never had — a heading citation that resolved to nothing, one paragraph away from the warning about stale cross-references. [#233](https://github.com/mshamblin5150-code/clinical-skills/issues/233) made a cited step number resolve or fail; a cited heading is reached by no check at all.)*

## Picklists — exact strings

**Preceptor and Location / Site are per-account, and their values are deliberately not recorded here.** They are names — a per-account list of people and places — and [setup-clinical-skills](../skills/setup-clinical-skills/SKILL.md) already rules the split this file lives under: *this file holds the universal Medatrax behavior and the profile holds everything about them.* Both lists sit in `scratch/medatrax-profile.md` under *Picklists*, which is gitignored. Read them off the portal for a new account rather than inheriting someone else's.

The **format** is the universal part and is what belongs here: `Preceptor` is `Last,First` with no space, and the Time Log renders that same value with a space.

**This file holds values for exactly these fields, and `tools/test_skill_agreement.py` enforces the list:** Interaction Level · Race/Ethnicity · Gender · Age unit · Marital status at first contact · Primary Payment Method · Case Type · Patient Time

Every one of those is a Medatrax dropdown that renders the same on every account. A ninth arriving anywhere in this file is either a genuine platform field — in which case it goes in the sentence above, and the diff says so in a line whose whole subject is *is this universal?* — or it is one account leaking back in, which is what this file did for its entire life until [#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212).

**The check reads the whole file, not this section**, because the hole [#222](https://github.com/mshamblin5150-code/clinical-skills/issues/222) was filed on is a per-account value arriving *under some other heading* — and a check bounded to this one is escapable by adding a heading, which a first version of it was.

**So no paragraph anywhere in this file may open with a bold span ending in a colon.** That is the field-label form, and the check reads one as a picklist it was not told about — the sentence below tripped it while being written. Bluntness is the point: a parse that tried to tell a label from a sentence would be a judgment, and a judgment is the seam a ninth picklist comes through.

**What that check does not reach is a value**, and there are two shapes of it. A per-account value appended to a field it has already been told about — a site name at the end of the `Case Type` list — reads as a declared field and passes. And a rule keyed on a site or a preceptor written as prose or as a table is the shape the `Primary Payment Method` rule had, which is the other half of what #212 found. Both need the name vocabulary [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50) declined to build and #212 re-ruled. **A green suite is not a read file** — *Field selection rules* below is still a person's job.

**Interaction Level:** `Level 0` … `Level 5`. Every existing entry is Level 5, the top of the scale.

**Race/Ethnicity:** African American/Black · Asian · Bi-racial · Caucasian/White · Hispanic/Latino · Native American/Alaskan · Other · Pacific Islander

**Gender:** Male · Female · Transgender · Non-binary

**Age unit:** Days · Weeks · Months · Years

**Marital status at first contact:** Married · Consensual Union · Single · Separated · Divorced · Widowed

**Primary Payment Method:** Commercial insurance/HMO/PPO · Medicaid · Medicare · Military/IHS/PHS · Worker's comp · Self-pay/other · none

**Case Type:** Cardiovascular · Dermatology · Endocrine Disorders · ENT · GI · GU · Mental Health · Musculoskeletal · Neurological · Opthalmic · Physical · Respiratory · Obstetrics · Gynecology

**Patient Time:** the hours bucket, derivable from age:

```
Pediatric (0 – 17) Hours     Adult (18 – 60) Hours     Gerontology (60 and>) Hours
Obstetrical Hours            Women's Health
```

Age decides the band; a gyn or obstetric visit overrides it — a 35-year-old seen for hormone review logs as Women's Health, not Adult.

**The override is the one this rule is most often missed on, and it is worth auditing rather than assuming.** On one account every gynecologic and obstetric visit in the entire record sat on an age band, and neither `Women's Health` nor `Obstetrical Hours` had ever been used once — with the age rule itself applied correctly throughout, so this is a gap in the habit rather than carelessness. Where a course's area breakdown wants gynecology and obstetrics hours in their own buckets, that habit supplies none of them.

**So sweep the account's own record before trusting the band.** The result is a measurement of one portal — counts, courses and whether the hours are recoverable — and it is a per-account finding: [setup-clinical-skills](../skills/setup-clinical-skills/SKILL.md) step 4 runs it and `scratch/medatrax-profile.md` holds it.

**No report exposes Patient Time.** Case Type Report gives case type, date and reference; the Statistics Report has a Case Type view but no Patient Time view; Data Totals covers visit-data categories, all empty. The value appears only on `patientdetail.aspx`, one visit at a time.

To audit a specific visit fast, `patList:txtSearch` on `/login/patient.aspx` accepts a Patient Reference and returns that single visit at `Select$0`. That is what makes a per-visit sweep possible without walking twelve pages of fifty.

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

**The arithmetic shows it has not been standing there, and it is worth running against any account.** Compare total patients against total visits on `studentoverview.aspx`. On one full record the overview reported about ten more visits than patients, and fifteen Patient Detail pages opened at random all read `1 Visit(s)`. A year of family practice does not produce ten returning patients, so most of that gap is duplicates already made. **The comparison is the universal part and the reading is not** — the totals it came from are one account's and sit in [setup-clinical-skills](../skills/setup-clinical-skills/SKILL.md) step 6, which runs this against a new account rather than inheriting someone else's answer. **The sampled Patient Detail pages are not there and are recorded nowhere else**, so that half of the evidence is re-derived by opening a handful of pages on the account in front of you rather than by following the pointer. And **abstracting the totals costs the argument its denominator**: ten against a record of hundreds is what makes ten returning patients implausible, and a reader who does not run the comparison has to supply that scale. Both are the price of the figures not standing here, named rather than absorbed.

Set the map up with `/setup-clinical-skills`. The encounters that cannot be fixed retroactively are the ones whose day-file note carried no name.

**There is no weight, heart rate, temperature or SpO2 field.** The note rubric wants a complete vital set, so those are filled and listed for confirmation. Anything Medatrax does carry is a given the note must match exactly.

Visit Time is derived from start and end, and varies — 0:30 to 0:45 across one sampled day, a flat 0:15 across another. The program expects roughly 2 patients per hour in family practice.

### Field selection rules

Some fields are administrative and never appear in bedside shorthand. Without a stated rule the skill reports them missing on every note, which is what trains a clinician to skim the block that is supposed to catch real omissions. Each one below has a rule, so it is answered once here rather than ten times a day.

**Primary Payment Method — a site, age and status pattern, corrected on sight.**

Payer data is not visible at the bedside. The value is *declared*, not derived — but it is not a constant either. The flat `Medicaid` default that used to sit here was wrong often enough that it must go under `FILLED·asserted` for confirmation rather than being filled silently. **The exact reading is per-account and lives in `scratch/medatrax-profile.md` under *Declared field defaults*.** It is not re-derivable without the account because it was read off the portal, not computed; any fixture evidence and count stay in the withheld fixture record.

**The rule keys on the site, so the rule is per-account and lives with the picklist.** It is in `scratch/medatrax-profile.md` under *Declared field defaults*, read off the clinician's own entries, and it fits 16 of the 18 H&P encounters and most of the SOAP comparison set. **What generalizes is that the site is a key at all, not the mapping** — [setup-clinical-skills](../skills/setup-clinical-skills/SKILL.md) step 5 says to measure this against the account's own record rather than carry another one's across, and a payer table is exactly the field that ruling was written about.

`Worker's comp` overrides all of it where the shorthand documents a work-related injury — and that exception is a **given**, read from the note, not a guess about the payer.

**This is not the rejected alternative.** The idea turned down earlier was varying the value to produce a realistic-*looking* payer mix, which fabricates administrative data to pass as plausible. This is a pattern read off the clinician's own record, and it is right more often than the constant was. Guessing a spread is invention; reproducing an observed one is not.

Still `FILLED·asserted`, still a starting value that genuinely needs a glance, still never under GAPS — it is filled, not missing.

**Race/Ethnicity — `Caucasian/White`, corrected on sight.**

Unlike payer, this one is observable — the clinician saw the patient. It simply never gets written down.

**The default is wrong about once in four**, measured the same way as the payer default above — every encounter of one account's sampled day, read field by field rather than estimated. **Unlike the payer reading, the breakdown behind this one is recorded in the profile only** and nowhere committed, so a clone without a profile has the ratio and not its working. Treat it as a starting value that genuinely needs a glance, not one that is usually safe to wave through — which is why it is filled under `FILLED·asserted` rather than written straight into the field.

**Blood pressure, Respiratory Rate, Height and BMI — filled, not left blank.**

The four vital and measurement fields are filled where the encounter does not supply them, to the value that patient most plausibly had. The rule and its cost — a filled vital that lands abnormal is worked up in the note like any other abnormal — are in [clinical-note](../skills/clinical-note/SKILL.md) under *Filled vitals, body measurements and the pain score*. Do not restate it here; do apply it. **Medatrax holds no severity field**, so the third member of that class never reaches this block — it lives in the note's HPI and in `FILLED·asserted`, and it is named here only so the section title reads as the same rule.

**The clinician's own practice settled this.** The 2025 Spring batch leaves `Height` and `BMI` blank; **every 2025 Fall and 2026 Spring encounter fills both**, inventing a height where the shorthand carries none. His words: *"the newer records everything is filled out."* The blank ones are the older habit, not the standard — the same shape as the flat visit lengths under Visit Time.

Order matters for the pair: pick a plausible height, pick a plausible weight, then **derive** the BMI and show the arithmetic. Never pick a BMI and read the height and weight backwards out of it. There is no weight field in Medatrax, so the weight lives in the note only — but the BMI in the field must recompute from it.

**A supplied but impossible number is not a value to enter and not an invitation to fill a replacement.** [clinical-note](../skills/clinical-note/SKILL.md)'s *An impossible given stays given* preserves the source token in the note, routes the ambiguity to `UNKNOWN` and the required verification to `FLAG`, and emits this structured field as `GAPS`: source value unusable, usable value unrecoverable, verify the source. A guessed correction never reaches the field.

**Start time / End time — estimated, not missing.**

The Times convention in [clinical-note](../skills/clinical-note/SKILL.md) assigns each visit 15–40 minutes across the shift and reports every time as estimated. Estimated is a property of the value, not the absence of one, so these do not belong under GAPS — a note that lists them there is spending a slot announcing that the skill obeyed its own instruction.

**Not every administrative field is equal.** `Patient Time` is the one where a wrong value has a real consequence: it feeds the course's area breakdown, so an error there misallocates clinical hours. Payment method and race/ethnicity feed no hours bucket at all. Treat them accordingly — `Patient Time` is worth stopping for, these are not.

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
