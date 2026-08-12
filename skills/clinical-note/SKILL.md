---
name: clinical-note
description: Turn ER-style clinical shorthand into a finished academic note — comprehensive SOAP or FNP H&P — plus the Medatrax patient entry fields. Use when the user pastes raw encounter shorthand, asks to "SOAP this", "write this up", "do an H&P", or needs an encounter formatted for Medatrax.
---

The input is **shorthand** — raw ER-style scratch for one encounter, typo-ridden, written at the bedside. The output is a finished note against a school rubric, plus the Medatrax entry fields.

These are **academic** notes documenting clinical hours, not the legal chart. The rubric demands complete sections — three-generation family history, age-appropriate screenings, a full ROS — that bedside shorthand never contains. Producing them is the job, and the tiers below are how it stays honest.

**Where the note goes.** A finished note or case study is written to **`output/notes/`** (case studies to `output/case-studies/`), never to the repo root and never to a tracked directory. `output/` and `scratch/` are the only two gitignored places; everywhere else is committed, and a note written there becomes a patient record on GitHub one `git add -A` later. Working material — day files, the identity map — stays in `scratch/`. Standing rule 1, and a pre-commit hook enforces it. Name files by date; a filename carries no patient name and no Patient Reference.

Output to the chat rather than a file when the clinician has not asked for one — but the moment it is written down, it is written down there.

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

- **An abnormal *finding* in the note must be a given.** No exceptions. This is the direction that carries the safety. A finding is something observed and chartable — an exam finding, a symptom, a result. It does not cover vitals, body measurements and the OLDCARTS pain score; those follow *Filled vitals, body measurements and the pain score* below.
- **A normal in the shorthand is still a given** — it means that system was examined. Keep it verbatim; do not move it to filled.
- **Silence is undocumented, never absent.** A section the shorthand omits means it was not written down that visit — not that the patient has nothing there. This holds everywhere, and it reads two ways depending on the section:
  - **Exam and ROS** — an unmentioned system is normal, because abnormals get charted.
  - **History, medications, surgical, family, social, allergies** — an omitted section is inferred from the rest of the encounter. A history of hypertension and no `meds:` line means a med rec was not done, so infer the likely regimen. Never write "none" where the shorthand is merely silent.

  Either way it gets filled, never raised as a gap.

Every filled *finding* is therefore normal, absent, or not reported — and says so in those words: `no chronic illness reported`, `fever by history`, `no smoke exposure reported`, `no treatment-limiting cultural practice reported`.

Charted normals and filled normals read identically in the finished note. They are separated in the tier block so only the filled ones need confirming — and *identically* is literal, which is why *The tier language stays out of the note* below forbids annotating them apart.

#### Filled vitals, body measurements and the pain score

**Filled vitals, body measurements and the OLDCARTS pain score** are permitted where the rubric requires a complete set and the encounter supplies only some — or none. They are the one exception to *filled content is unremarkable*, and the exception is narrow enough to state exactly.

**The class is a test, not a list.** A value joins it when both of the next two paragraphs hold of it: a box demands a value, and the shorthand constrains none. Three members are named because three are known — anything else has to earn entry by those two arguments, and **no exam finding, symptom or result will ever pass them.** A result has no box standing empty, and an unmentioned system is already answered by *Silence is undocumented, never absent* one level up.

A vital is not a finding the clinician chose to record, and two things follow that do not follow for a finding.

**A value is required.** The rubric wants a complete vital set, and Medatrax holds fields for blood pressure, respiratory rate, height and BMI that are filled rather than left blank. The rubric's HPI is the same shape: eight OLDCARTS boxes, one of them severity. A result has no field standing empty in the same way — it exists only if testing was ordered and run. Something has to go in the box.

**Nothing in the shorthand constrains which value.** Transcription is all-or-nothing: measured 2026-08-11 across 559 encounters, 47% carry no vital at all, and of the 249 blood pressures he does transcribe, half are below 130/80. He is not writing them down because they were interesting, so an absent vital carries no information about its value — and never means it was normal. That is *Silence is undocumented, never absent* applied to the one kind of value where "undocumented" and "unremarkable" come apart. For a finding, silence is evidence, because abnormals get charted. For a vital, silence is evidence of nothing.

**Whether the measurement happened is beside the point**, which is what height makes obvious. In 15 encounters he transcribes a blood pressure and a weight and no height, and nothing in the record says whether that height was taken and left unwritten or never taken at all. Neither leg above asks. The license rests on the box needing a value and the shorthand constraining none, never on a tape measure having touched the wall.

> **A filled vital is the value this patient most plausibly had.**

Reason it from age, body habitus, the documented conditions and the presenting complaint — not from the middle of the normal range. A known hypertensive seen for a productive cough gets a hypertensive pressure and a raised respiratory rate. A two-year-old gets a two-year-old's pressure, not a scaled-down adult's.

**A small child's anchors are different, not absent.** The adult anchors — documented hypertension, body habitus — are usually missing under 6, which invites the conclusion that there is nothing to reason from and the middle of the range is all that is left. The corpus says the reverse. Measured 2026-08-11, **18 of the 21 encounters under 6 carry a transcribed vital line with the blood pressure alone missing** — 17 a structured line, one a temperature written into the exam prose — where 95 of the 106 encounters aged 20 and over with no pressure carry no vital at all. Both figures are over the 357 encounters whose age the census can read; 202 state none, so 21 is a floor on the under-6 population rather than a count of it. A young child's fill is the best-anchored one in this record, not the worst: the pulse, temperature, respiratory rate and oxygen saturation are usually sitting right there as givens.

Work it in two steps:

- **The band comes from age, sex and height percentile** — which is how pediatric pressure norms are defined in the first place. Where the height is not given, fill it first and use it.
- **The position within the band comes from the encounter** — the given pulse and temperature, the distress the exam describes, any documented weight percentile. A fussy, febrile toddler with a pulse of 125 does not sit at the fiftieth percentile.

**No age boundary applies here.** The rule is continuous: the anchors shift with age and nothing switches on at a birthday. This repo already carries three incompatible age lines — `Patient Time` at 18, `Z68`'s BMI band at 2–19, and the 6 the corpus happens to show — and this is deliberately not a fourth.

**A missing pressure in a small child is still filled, and never a GAPS entry.** It is the one band where silence about a vital genuinely is informative: the pressure was decided against rather than merely left unwritten, eighteen times out of twenty-one. That changes the reasoning and not the outcome, because *whether the measurement happened is beside the point* — knowing the cuff never touched the arm still does not say what the reading would have been, and the Medatrax field is required whatever the patient's age. Issue #11.

**A filled vital that lands abnormal is worked up like any other abnormal.** It reaches the Assessment and the Plan; drift row 4 applies to it in full. This is the cost of the license and it is not optional — a note that invents 142/88 and then says nothing about it has manufactured the exact defect this skill exists to catch.

**Worked up does not mean the disease is worked up.** Where the encounter documents a cause for the elevation — fever, pain, a crying child — the response is to **name it, attribute it to that cause, and recheck when the patient is well**. A raised pressure in a febrile, distressed toddler is addressed by a recheck when afebrile and calm; never by an antihypertensive, an echocardiogram, a renal ultrasound or a nephrology referral. Row 4 asks that a generated value not be abandoned. It does not ask for the evaluation of a condition nothing documented — that is a second invention resting on the first, and it is the one standing rule 2 forbids outright.

Height and weight follow the same rule, in this order: pick a height plausible for the age and sex, pick a plausible weight, then **derive** the BMI and show the arithmetic. Never pick a BMI and leave the height and weight to be read backwards out of it.

**The OLDCARTS severity is the third member, and it is a pain scale.** The box reads `6/10 facial pressure`, never `not documented` and never a word. (The separator between the element and its value is *Punctuation*'s business, not this rule's — a hyphen on SOAP's one-liner, the template's own colon in H&P's block.) Both arguments above hold of it exactly. A value is required, because severity is one of the rubric's eight HPI boxes. And nothing in the shorthand constrains which value, because a clinician who did not write a number down has said nothing about what the number was — the same asymmetry that makes an absent blood pressure uninformative.

*Filled content is unremarkable* would put the score at 0/10, and that is precisely the collapse this exception exists to prevent. 0/10 is the reading for a patient in no pain — a real answer where the shorthand says so, and a given when it does, but not one to arrive at by default.

**Score it the way a vital is scored: the value this patient most plausibly had.** Anchor it in the complaint, the exam and what was done about it. **The treatment given is the anchor a pressure does not have**, so use it: a run that writes 2/10 for a sinus pressure treated with intramuscular methylprednisolone has described a patient who would not have been given it, and one that writes 9/10 has described a patient who would not have been sent home.

**A filled score is answered in the Plan**, by analgesia or by the treatment of what is causing the pain. This is the same cost the license charges for a filled vital that lands abnormal, and the pain scale's normal range is one value wide — 0/10, and nothing else. It is not optional for the same reason either: a note that invents a 7/10 and offers nothing for it has manufactured the defect this skill exists to catch.

**Two things are givens rather than fills, and reading either one wrong invents a symptom.**

- **A score the shorthand writes is a given.** `c/o 8/10 pain` is 8/10 in the note — unrounded, unreplaced, exactly as a transcribed pressure is.
- **A documented absence of pain is a given too, and it scores 0/10.** `no pain`, or `is in no pain only when she bumps it`, is a charted finding. Filling a number over either is inventing a symptom, and no part of this exception licenses that: it buys a number for a complaint the shorthand documents, never a complaint.

**Where the presenting complaint is not a painful one, the scale still takes a number and names what it scores** — `4/10 itching`. What the eight boxes forbid is a blank; they do not require that every patient hurt. This is the rule carried past the case it was ruled on — issue #30 was raised about a patient in pain — and it is stated rather than left open because *eight, always eight* leaves no third option.

**Every filled vital, every filled measurement and every filled OLDCARTS element is listed in the FILLED block carrying its value, written exactly as it appears in the note body.** Not `blood pressure filled` — `BP 142/88 filled`. Not `aggravating factors filled` — `AGGRAVATING bending forward, lying flat filled`, and `SEVERITY 6/10 facial pressure filled`. Two reasons, and the second is the load-bearing one:

- The clinician confirms a value, not a category, and cannot confirm what the block does not state.
- The note body is written so given and filled content read identically. **The FILLED block is therefore the only thing in the whole document that can tell them apart**, and [icd10-cpt](../icd10-cpt/SKILL.md) reads it to decide which numbers a code may rest on. It matches on the value. A block naming the field without its value says a pressure was filled but not which one, and the check fails open in silence.

**A derived value with a filled input is listed in the FILLED block too**, naming which inputs were filled — and it stays on the `DERIVED` line as well, with its arithmetic. A BMI is the case that matters: derived is a true statement about it, since the arithmetic has one right answer, but the answer is only ever as real as the height that went in. A BMI appearing under `DERIVED` alone reads as computed from measurements, which is exactly the impression it must not give.

#### A filled BMI near a threshold says how near

BMI is banded, and the bands do real work: an abnormal one must be worked up in full (drift row 4), and 30.0 diagnoses obesity where 29.1 does not. Where the BMI was derived from a filled height or a filled weight, a single invented inch decides which side of that line it falls on:

```
175 lb    5'4" -> 30.0    5'5" -> 29.1
150 lb    5'5" -> 25.0    5'6" -> 24.2
```

**Where a BMI with a filled input lands within 1.0 of 18.5, 25, 30, 35 or 40, say so on its own FILLED line** — naming the adjacent value and what it changes:

```
FILLED·asserted   HEIGHT 5'4" filled; BMI 30.0 = 703 x 175 / 64^2. Within 1.0 of the
                  obesity threshold — 5'5" gives 29.1, and the obesity workup drops.
```

**Do not move the value to avoid making the disclosure.** The rule is still *the value this patient most plausibly had*; the disclosure is what makes a plausible value safe to act on, never a reason to choose a safer one.

### What may be inferred

Inference is the job. What the shorthand omits should be **grounded** in what it contains — reasoned from the givens, not invented beside them.

Grounded, and expected:

- Route, frequency, and duration for a drug the shorthand names — `zithromax 200/5ml 3/4 t x 3 days` becomes azithromycin 3.75 mL PO **daily** for 3 days.
- A medication proposed in the **Plan** for a condition in the history — lisinopril where the history carries hypertension. This is the clinical reasoning being graded; make it.
- Standard supportive care, health promotion, and return precautions for the stated diagnosis.
- Testing for a documented infectious exposure — see below.
- Screenings appropriate to the patient's age.
- The exam of a system the shorthand never mentions.
- **Every OLDCARTS element the shorthand does not supply** — aggravating and relieving factors, timing, character — reasoned from the presenting complaint. Bending forward and lying flat aggravate a sinus complaint; asserting that is the same act as the line above it, and the eight elements are mandatory. Severity is the one that is not ordinary filled content: it follows *Filled vitals, body measurements and the pain score*.

**A documented infectious exposure with a congruent presentation orders testing by default.** The contact is a given; testing for what the contact had is standard care for that presentation, and it belongs in the Plan the way return precautions do. Respiratory contact plus respiratory symptoms means **COVID-19 and influenza at minimum**, and **group A streptococcus where the pharynx is involved** — a sore throat, pharyngeal erythema, tonsillar exudate. Name the agent and name the specimen: `COVID-19 and influenza A/B, nasopharyngeal swab`, never `viral testing`.

It is a `FILLED·proposed` line like any other order, generated from the exposure and never from noticing that the encounter omitted it. **The visit not having swabbed is not by itself a FLAG** — see *FLAG is the block that matters* in step 6. A clinician who documents a sick contact and treats empirically has made a call, and a note that flags him for it flags him on every encounter where he made the same one. It stays a FLAG only where the exposure is documented *and* testing would have changed the management the note actually recorded.

**An order is not a result**, which is the paragraph below applied to the order this one generates. A swab sent today has no answer today: nothing goes in the Objective, and where the encounter itself ran no testing the results line still reads `No new testing today` — that describes what came back, not what was ordered. Ordering COVID-19 testing and then writing `COVID-19 negative` is the invention the whole tier system exists to prevent.

**And its missing result is not a GAPS entry.** GAPS holds *a swab sent and never returned* — the encounter ran a test and the record lost the answer. A swab this rule orders has no answer to have lost, so it is complete as written, and reporting it as an omission is the *anything the skill was instructed to generate* case in step 6.

**One thing can never be inferred: a result.** Laboratory values, imaging results, and diagnostic test results were either obtained or they were not, and no clinical reasoning yields `estrogen 729`. Where testing is absent, write `No new testing today`. Never produce a number that would read as a result. **Vitals are measurements but they are not results** — a result exists only if testing was ordered and run, while a vital set is required of the encounter record whether anything was ordered or not; see *Filled vitals, body measurements and the pain score*.

**Age needs a date of birth looked for first.** About 93% of this clinician's encounters carry one or the other, and where a date of birth appears the age is *derived*, not missing — compute it. The newer shorthand runs age and sex together with no marker — `51 f`, `48f` — and that form is easy to miss.

**Where neither appears — about one note in fourteen — infer the age, and flag it harder than anything else in the block.** The old rule stopped, because age sets `Patient Time` and a wrong band misallocates clinical hours. But a note that stops cannot be entered at all, and the clinician infers and enters it himself: three confirmed cases, one carrying nothing but `1 ppd x 41 yrs`.

Anchor the age in whatever the narrative gives — pack-years, gravidity, post-menopausal status, school grade, a spouse's age — and name the anchor. Then put it at the **top of `FILLED·asserted`, on its own line, naming the band it sets**:

```
FILLED·asserted   AGE 60 y — inferred from 41 pack-years begun in adulthood;
                  sets Patient Time = Adult (18 – 60). CONFIRM BEFORE ENTRY.
```

An inferred age charges an hours bucket silently, which is why it is confirmed loudest rather than not made.

**Sex is not the same, because the narrative carries it.** Shorthand that never writes `M` or `F` but says `he states he fell yesterday` has documented sex in the pronouns, and that is a given like any other stated finding. Read it, and say that is where it came from.

Where the shorthand supplies no demographics at all, the Medatrax entry does — step 1 takes them from it as givens.

Separate two acts in the tier block, because they carry different weight:

- **Proposed** — a forward action: a drug started, a test ordered, a referral. Reasoning, and safe to be wrong about; the preceptor rules on it.
- **Asserted** — a claim about the patient's past: a medication they already take, a condition they already carry. Ground these in the history, then be specific. An absent `meds:` line usually means no medication reconciliation was done that visit, **not** that the patient takes nothing — infer the likely regimen from the conditions listed and name actual agents. This is the tier a preceptor checks hardest, so every asserted inference is listed.

  **An inferred regimen never answers a conflict the givens raise.** Motrin 800 TID against a documented GERD is called out whatever the inference contains — and a given drug is never dropped from the list to make the conflict disappear. Inferring the PPI is the instruction; letting it settle the question is the defect. Drift row 11.

### The tier language stays out of the note

The tiers govern how the note is written. **They are never written into it.**

- **No tier word appears in the note body** — not *given*, *filled*, *inferred*, *derived*, *asserted* or *proposed*. Not as a parenthetical, not as a suffix, not as an aside. In `Levothyroxine 88 mcg PO daily (hypothyroidism) (inferred)` the first parenthetical is the reason for taking and belongs there; the second is the defect in its shortest form.
- **No commentary about this skill's own process appears in the note body.** Whether a medication reconciliation was done, what needs confirming before entry, which condition an inference rests on, why a duration was chosen: all of that is the FILLED block's job and only the FILLED block's job.
- **A parenthetical in the Plan holds the trade name and nothing else** — `Amoxicillin-clavulanate (Augmentin) 875/125 mg PO twice daily x 10 days`. Reason for taking stays in the medication history, where both templates put it; rationale goes in the Assessment.

**This is not a style preference — it is the property the whole tier design rests on.** Charted normals and filled normals are written to read identically precisely so that the FILLED block can be the one thing in the document that tells them apart, which is the same reason a filled vital is listed carrying its value. Annotating tiers inline makes the note body a second tier record: partial, informal, and not the one [icd10-cpt](../icd10-cpt/SKILL.md) reads. Two records that disagree are worse than one.

And the note goes to a preceptor under the clinician's name. **No clinician writes `(given)` in a medication list**, and a note that explains its own construction is not the document that was asked for.

**What is banned is the word naming where the text came from, not the word itself.** English gives `given` two ordinary clinical senses that are nothing to do with tiers, and both are correct writing:

- **Administered** — `methylprednisolone 125 mg IM given in clinic`. A drug given to the patient, not a line labeled.
- **In view of** — `lipid panel, given hyperlipidemia and peripheral arterial disease`. Reasoning from the patient's history.

`filled` behaves the same way — a prescription is filled at a pharmacy. So the check is not a word search:

> **Would the word still be there if the shorthand had supplied every line in the note?**

If yes it is clinical and it stays. If no it is describing this skill's own work, and it goes. **The question is asked of an occurrence of one of the six words**, not of every sentence in the note.

**Reporting an absence is charting, not commentary.** `No chronic illness reported`, `fever by history`, `no smoke exposure reported`, `No new testing today` are all required phrasing elsewhere in this file, and none of them is a leak. Each is a finding about the patient, written in the words this skill asks for.

**The line between them is what the sentence is doing, not what it is grammatically about.** `No medication reconciliation was performed this visit` looks like a fact about the encounter, and that is exactly why it slipped past the first reading — but it is in the note to explain why the medication list above it was inferred. So the test is not what the sentence mentions:

> **Does the sentence report something about the patient, or does it defend the note?**

`No chronic illness reported` and `No new testing today` report. So does `acetaminophen, dose and frequency not documented` — an unverified dose is a real thing to know about a patient taking the drug. `No medication reconciliation was performed this visit` defends: strike the inferred medications and the sentence has nothing left to do.

**It fails twice over, and the second failure is the worse one.** Nothing in the shorthand says a reconciliation was not done — this file infers that from an absent `meds:` line, and inferring it is correct. Writing it into the note turns that inference into a documented claim about the visit, under the clinician's name. The inference belongs in `FILLED·asserted`, which is where a preceptor can rule on it. Drift row 12. Issue #28.

## Conventions

**Favor the more complex note.** Where a differential could run three deep or five, run five. Where a finding could be left in Objective or carried into Assessment, carry it. Thoroughness is the tiebreaker, always.

**Marital status** is inferred from age and written into the Social History, not left as unreported.

**Social history** does not blanket-fill with "not reported". Say it where it is genuinely unknown and would matter; otherwise write the inference.

### Punctuation

Three characters that never reach the finished note, given unprompted as absolutes — *"i would never"*, *"i never"*:

| Never | Always |
| --- | --- |
| `·` middot as a separator | `,` comma |
| `—` em dash | `:` colon |
| `→` arrow | `∴` therefore (U+2234) |

So `VS: BP 138/86 · HR 88 · T 98.8 F` is written `VS: BP 138/86, HR 88, T 98.8 F`, and `Ht 5'4", Wt 198 lb → BMI 34.0` is written `Ht 5'4", Wt 198 lb ∴ BMI 34.0`.

**A value pinned to its label takes a hyphen, not the colon** — `Cystitis - N30.00`, `Penicillin - rash`, `Lisinopril - hypertension`. His ruling on the templates, and it is the one place the colon would double up: `Final diagnosis: cystitis: N30.00` puts two colons on one line and reads as a nesting that isn't there. The colon keeps every position where it introduces a clause rather than a value — the differential rationale is the case in both branches: `Acute bronchitis: cough three weeks, clear lungs, afebrile. Favored.`

**About the output, not the input.** The arrow is a token he writes — [GLOSSARY.md](GLOSSARY.md) carries it as *leading to, progressing to* — so it arrives in the shorthand as a given like any other, and this rule governs only what it expands to.

**And the note body only.** The tier block keeps its `FILLED·asserted` middot, the Medatrax field block is unaffected, and prose about the skill — this file, [GLOSSARY.md](GLOSSARY.md), the section notes in both templates — is not the note. An em dash inside a template placeholder that instructs the writer rather than shaping the output is prose too: `<… duration — one per line>` stays, because a colon there would read as a field whose value is *one per line*.

It binds both branches, which is why it lives here rather than in either template. Both were swept when it was added: [SOAP.md](SOAP.md) did not merely permit the arrow, it **specified** it — `Ht, Wt → BMI`. A convention that contradicts the template it governs loses. Issue #31.

### Times

Ask up front, once per day file, and reuse for every encounter in it:

- **What time did the day start?** Note 1 is the first patient; each subsequent note follows in order.
- **How long was the shift?** Clinical days often run twelve hours.

Then assign each visit **15 to 40 minutes, in 5-minute steps**, by complexity — a brief recheck or simple sprain at 15–20, a routine acute visit at 25–30, a multi-problem or procedural visit at 35–40. Space the encounters across the shift rather than stacking them back to back, and report every start and end as estimated.

## Steps

### 1. Intake and de-identify

Collect the shorthand and, if supplied, the Medatrax entry — it carries demographics and some vitals, and those are **givens** the note must match exactly.

**Derive the age before you redact the date of birth.** Across the clinician's catalog — 353 encounters — the age is stated outright in 42% and a **date of birth appears instead in 47%**. Redacting `[DOB]` on the way past destroys the only thing age can be computed from, and age sets the `Patient Time` band. So: compute the age from the date of birth and the visit date, write it down as a derived value showing the arithmetic, and redact afterwards.

**Read the unmarked form.** The newer shorthand runs age and sex together with no marker at all — `51 f`, `48f`, `35 f` — and it is the dominant form in the recent files. Anything scanning for `yo`, `y/o` or `dob` misses it and reports a recent encounter as ageless.

Then replace identifiers as you read: `[PT]` for name, `[DOB]`, `[MRN]`, `[SITE]`, `[PRECEPTOR]`. Keep age, sex, visit date, and everything clinical.

**About 7% of encounters carry neither an age nor a date of birth** — roughly one in fourteen, measured 2026-08-11 across 559 notes, of which 521 carry one or the other. Not a freak case, and not a stop: see *What may be inferred* for how the age is inferred and flagged.

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

Produce the field block from [../../reference/medatrax-fields.md](../../reference/medatrax-fields.md) in that file's field order, so it can be tabbed straight into the form.

Fields carrying a **declared rule** there — `Primary Payment Method`, `Race/Ethnicity` — are filled from that rule rather than reported missing. Neither is visible in bedside shorthand, and reporting them missing on every note is what teaches a clinician to skim this block. The rules live in the reference; do not restate them here.

**Resolve the patient before the fields.** Medatrax stores no name — it generates a Patient Reference and that is its only handle on a person. An encounter entered without matching the existing record creates a **second** patient, silently and unmergeably. So look the name up in the clinician's identity map first, and emit either the matched Patient Reference or an explicit `NEW PATIENT` line. Where the day file gave no name to match on, say that: it is the exact mechanism by which duplicates are made, and it is worth one line rather than a discovery months later. Location and format of the map come from `/setup-clinical-skills`.

Everything else the encounter does not supply goes under GAPS rather than being invented — with three exceptions, each generated by design and declared rather than reported missing: start and end times, which the Times convention estimates; **vitals and body measurements**, which are filled to the value the patient most plausibly had; and **age**, which is inferred and flagged at the top of `FILLED·asserted`. The field that justifies the caution is `Patient Time`: it feeds the NUR 5144 area breakdown, so a wrong band misallocates clinical hours. Most of the rest feed no hours bucket at all.

### 6. Emit the tier block

Below the note, always, in this order:

```
DERIVED           <value = the arithmetic>
FILLED·asserted   <claims about the patient's past — inferred history, meds, family, social>
FILLED·proposed   <forward actions — drugs, tests, referrals, education, follow-up interval>
FLAG              <a documented finding the note failed to act on>
GAPS              <what the rubric needs and the encounter genuinely did not supply>
UNKNOWN           <tokens carried verbatim, any guess marked as a guess>
```

The two FILLED lines together are **the FILLED block** — everything generated, in one place, for confirmation before submission. It splits into **asserted** and **proposed** because they carry different weight, as set out under *What may be inferred*: a preceptor checks asserted hardest, while proposed is reasoning and safe to be wrong about. A declared administrative value is a claim about the patient, so it belongs under `FILLED·asserted`.

A value can occupy two lines at once, and one routinely does: a BMI derived from a filled height is written under `DERIVED` with its arithmetic *and* under `FILLED·asserted` naming the filled input. Listing it only as derived hides that it was invented; listing it only as filled hides that it was computed.

**The block travels with the note.** [icd10-cpt](../icd10-cpt/SKILL.md) takes the note body *and* this block, because the body alone cannot say which of its numbers were measured — that is the whole point of writing filled content so it reads like the rest. Never hand a note to the coder with the tier block stripped. Where codes are produced mid-draft, as [SOAP.md](SOAP.md) and [HP.md](HP.md) both do, the step 4 tier assignment is what the coder needs; the block is that assignment's written form, not its only form.

**FLAG is the block that matters.** A flag is a finding that was documented and then abandoned — an abnormal that reached the Objective and stopped there, a vital nobody addressed, a second problem the Assessment never names. It is neither a gap (nothing is missing from the source) nor a filled line (nothing was generated). It is the note failing to act on what it was told, which is the defect this skill exists to catch.

One FLAG per finding. Name the finding and name what was not done with it — `BP 151/93 undiscussed`, not `vitals not addressed`.

**A default this skill generates is not an abandonment, and does not go here.** Testing from a documented exposure is the case — the visit not having swabbed is not by itself a flag. It is written as the order under `FILLED·proposed`, and the FLAG block says nothing. This is the GAPS list's *anything the skill was instructed to generate*, one block up: the two are told apart by what would fix them, and an abandoned finding is fixed by the clinician going back and addressing it where a missing default is fixed by this note carrying it. Flagging the second turns a routine standing order into a recurring accusation, and a block full of those is a block nobody reads — which costs the abandoned finding sitting next to them.

**The one exception is stated where the rule is**, under *What may be inferred*: a documented exposure stays a FLAG where testing would have changed the management the note actually recorded. That is a defect in the encounter and not a default the skill supplied, so it belongs here. The order is written either way.

**What never goes under GAPS:**

- **Start and end times.** Estimated by design, and they say so where they appear. Estimated is a property of the value, not the absence of one.
- **Vitals and body measurements.** Filled by design to the value the patient most plausibly had, and declared in FILLED.
- **Any of the eight OLDCARTS elements.** All eight are mandatory and all eight are filled where the shorthand is silent. `Aggravating - not documented` is the same defect written into the note body instead, and it fails the branch template rather than earning a GAPS line.
- **Age.** Inferred by design where the shorthand and the entry both lack it, and flagged at the top of `FILLED·asserted`.
- **Primary Payment Method and Race/Ethnicity.** Both have declared rules and are filled, not missing.
- **Anything the skill was instructed to generate.** Reporting your own compliance as a defect is what makes the block unreadable, and an unreadable block hides the real omissions.

GAPS holds what the rubric needs and the encounter did not supply: an x-ray ordered with no result recorded, a swab sent and never returned.

### 7. Check for drift

A note **drifts** when a finding goes in the front and never comes out the back — documented in the shorthand, carried dutifully into Objective, and then absent from the Assessment and the Plan. Drift is what a long day does to documentation, and catching it is the reason this skill exists.

Walk every row. **Emit a verdict for each one by name** — a summary line invites declaring the set passed without walking it.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | **Invention** | Every abnormal finding, diagnosis and result in the note traces to a given. Filled vitals, body measurements and the pain score are exempt — they are declared in FILLED, not traced |
| 2 | **Drift** | Every abnormal *in the shorthand* appears in the Assessment or the Plan |
| 3 | **Results** | No laboratory value, imaging result or diagnostic finding is filled. Vitals, body measurements and the pain score are not results and do not fail this row |
| 4 | **Vitals** | Every vital **or body measurement** outside the normal range for this age is addressed somewhere, not just recorded — **filled ones included**, with no exemption for being generated. A filled height and weight yield a BMI, and an abnormal BMI is addressed like any other. A filled pain score is the same rule with a one-value normal range: **0/10 is the only unremarkable score**, so any other is answered in the Plan |
| 5 | **Sig** | Every drug carries dose, route, frequency and duration |
| 6 | **Red flags** | The return precautions name specific findings — *fever above 101, worsening flank pain, inability to keep fluids down* — never "red flags reviewed" |
| 7 | **Drug names** | Each drug reads as the shorthand wrote it, trade or generic, unconverted |
| 8 | **Band** | Patient Time follows Adult ≤ 59 / Gerontology ≥ 60 — overriding the Medatrax label's `Adult (18 – 60)` — with an obstetric or gynecologic visit taking precedence. An inferred age passes this row only if the inference is named on its own line in `FILLED·asserted` |
| 9 | **Arithmetic** | Every derived value shows its working and recomputes correctly |
| 10 | **Entry** | Every Medatrax field holds a given, a derived value, a declared value, or a GAPS entry |
| 11 | **Conflict** | A conflict between givens — a drug against a documented condition, or a drug against a drug — is named in the Assessment or the Plan. No inferred medication resolves one, and no given medication is dropped to dissolve one |
| 12 | **Leakage** | No tier word in the note body names where a line came from — *given*, *filled*, *inferred*, *derived*, *asserted*, *proposed* — no sentence describes this skill's own process, and every Plan parenthetical holds a trade name alone. The ordinary clinical senses pass: *given in clinic*, *given her hyperlipidemia*, *prescription filled* |

**Row 12 is checked by reading the body without the block.** Every other row asks whether the note said enough; this one asks whether it said something only the tier block may say. The two failing shapes are a parenthetical that labels its own line — `(inferred)`, `(dose given; duration filled)` — and a sentence that accounts for the note's own content, such as what was not reconciled or what must be confirmed before entry. Both read as diligence, which is why they survive a reading that is looking for omissions.

**A word search is the wrong instrument here** and will produce false hits on any note written well. *The tier language stays out of the note* carries a test for each half: ask of every occurrence of the six words whether it would still be there had the shorthand supplied every line, and ask of every candidate sentence whether it reports something about the patient or defends the note. Record which way each one resolved.

**Row 8 is worth a second look even when the age is given.** The clinician's own record puts an 82-year-old on `Adult`, and misses the gyn/obstetric override on every opportunity it has had. A stated age is not the same as a correct band.

Row 2 carries the most weight and is the easiest to skip, because a drifting note reads perfectly well. Take each abnormal from step 2's expansion in turn and name where it lands. An abnormal that lands nowhere is either a diagnosis missing from the Assessment or a problem missing from the Plan — say which.

A failing row is written as a **FLAG** in the tier block, never quietly repaired into a pass. That is what FLAG is for — the matrix finds the defect, FLAG is where it is recorded.

Close with `N given, N derived, N filled` and stop.
