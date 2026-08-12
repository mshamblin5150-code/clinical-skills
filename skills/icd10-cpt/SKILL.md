---
name: icd10-cpt
description: Propose ICD-10-CM diagnosis codes and CPT procedure codes from a documented encounter, each anchored to the note text supporting it. Use when the user asks for codes, needs to code an encounter, or mentions ICD-10, CPT, or E/M level.
---

Codes are **proposed**, never asserted. A code you supply is a suggestion the clinician verifies before it is entered anywhere — this skill's output is a worksheet, not a coding decision.

Three disciplines make that verification fast:

- **Anchor** — every code quotes the note text that documents it. A code with no anchor is not a code, it is a guess about the patient.
- **Descriptor** — every code carries its official descriptor next to its number. When the number and the descriptor disagree, the clinician sees it instantly. This is the defense against a fluent, plausible, wrong code number, and it is the reason the descriptor is never omitted to save space.
- **Source** — the anchor has to be something the encounter *recorded*. A note carries filled content by design, and filled content reads exactly like recorded content. Codes are proposed from what was recorded, never from what was supplied to satisfy a rubric.

The third one is invisible and is the reason for *The input* below.

## The input

**The input to this skill is the whole `clinical-note` output — the note body and the tier block beneath it — not the note body alone.**

That is a hard requirement, not a convenience. Every line of a finished note is **given**, **derived**, or **filled** ([clinical-note](../clinical-note/SKILL.md)), and the finished note is written so those three read identically. `BMI 36.4` in the Objective is the same eleven characters whether it was measured or generated. The tier block is the only place the difference is recorded, so a note arriving without one has had its source information stripped.

**Where the tier block is missing, say so and treat every vital, body measurement and BMI in the note as filled.** Not as a punishment — as the accurate reading. Measured 2026-08-11 with `tools/corpus_census.py` across 551 encounters, 46% carry no vital at all and only 41% carry a height — so **59% have no height to write down**. An unmarked measurement in a note from this pipeline is more likely to have been filled than recorded. Being wrong in that direction costs a code that had to be earned by measuring; being wrong in the other direction puts a number nobody measured onto a claim.

## The code set

This repo ships the ICD-10-CM code set at `reference/icd10cm-2026.sqlite`, so a code can be **looked up rather than recalled**:

```bash
python tools/icd10_lookup.py Z68.36 E66.811
```

```bash
python tools/icd10_lookup.py --find "body mass index" --billable
```

It answers four things: does the code exist, what is its official descriptor, is it billable, and what notes govern it. Use it for every code you propose. Three things it changes:

- **The descriptor stops being recalled.** Paste the official one.
- **`CONFIDENCE` means something narrower.** `verify this number` is for a code you did not look up. A code you did look up is verified against a named release and says so.
- **Billability is checked, and it is the quiet one.** `Z68.2` is a real code with a real descriptor that cannot be submitted — it is a header, and only its children are billable. A proposal carrying a header code reads as correct right up to the rejection.

**What the lookup cannot do.** There is no alphabetic index in the database, so it verifies a candidate rather than finding one from a diagnosis phrase. `--find` is a substring match over descriptors, which is weaker: a miss is not evidence that no code exists. And nothing in it encodes the official coding guidelines. It answers *does this code exist and what governs it*, never *is this the right code*.

## Steps

### 1. Read the FILLED and DERIVED lines first

Before reading the note body, list every value the tier block gives as filled — every filled vital, every filled body measurement.

**Then read `DERIVED` as well, because that is where the BMI lives.** A BMI computed from a filled height is *derived* under [clinical-note](../clinical-note/SKILL.md)'s tiers — the arithmetic has one right answer — so it is written on the `DERIVED` line, not a `FILLED` one. A step that read only the FILLED lines would miss the single value this whole rule was written for. **A derived value is treated as filled here whenever any input to it was filled**, and its FILLED line names those inputs.

That combined list is the set of numbers **no code may rest on**. Hold it while doing step 2.

Completion: every entry under `DERIVED`, `FILLED·asserted` and `FILLED·proposed` has been read; every filled vital and measurement is written down with its value; and every derived value has been checked for a filled input.

### 2. Extract codable elements

Read the note and list what is documented — not what is implied. For each, capture the exact supporting text.

- **Diagnoses** — from the Assessment. A symptom is codable as a symptom; it does not become a disease.
- **Procedures** — from the Plan and Objective: laceration repair, splinting, incision and drainage, ECG interpretation, foreign body removal, and so on.

Then strike out every element whose only support is a value from step 1. Those are not codable here — they go to step 4.

Completion: every Assessment problem and every Plan procedure appears in the list, marked codable or filled-anchored.

### 3. Propose codes

For each codable element:

```
ICD-10  <code>  <official descriptor>
  ANCHOR: "<verbatim note text>"
  SPECIFICITY: <complete | needs: laterality / episode / site / severity / a billable child>
  CONFIDENCE: <verified against ICD-10-CM FY2026 | verify this number>
```

CPT entries take the same shape, plus the note text documenting anything the code's requirements hinge on — repair length, wound complexity, time.

Rules:

- Code to the specificity the documentation supports and no further. If the note says "wrist fracture" with no side, the laterality is `needs: laterality`, not a coin flip between left and right.
- Say `verify this number` whenever you are working from recall rather than the code set. An honest flag costs the clinician ten seconds; a confident wrong code costs a rejected claim or a bad log entry.
- Never invent a documented finding to justify a code. If a code needs an element the note lacks, that goes in step 4.
- **Never propose a code whose only anchor is a filled value.** The rule and its reasoning are below.
- **A hedged diagnosis is coded, and the documented symptoms are coded with it** — with one limit, on the code rather than the hedge. Below.
- **Every differential entry carries a code, and none of those codes is for entry.** Below.

#### A filled value is not documentation

**A code whose only anchor is a filled value is not proposed at all.** It goes to step 4, naming the code it would unlock and the measurement that would earn it.

The rule is general. It is not a rule about `Z68`, which is only its sharpest instance.

**Why the general form.** These four all code directly off a single number with no clinical judgment in between, and every one of them is a value `clinical-note` is *required* to generate when the shorthand omits it:

```
Z68.-    Body mass index, banded to 1.0 BMI units through the 30s
E66.-    Overweight and obesity
R03.0    Elevated blood-pressure reading, without diagnosis of hypertension
R06.82   Tachypnea, not elsewhere classified
```

An enumerated list would be a snapshot of what was thought of once. The test is structural: *does this code rest on a number the encounter recorded?*

**Two of those four say it themselves, in CMS's words.** `E66` carries the instruction

> code to identify body mass index (BMI), if known

and `R03.0` carries

> This category is to be used to record an episode of elevated blood pressure

**`if known`** and **`an episode`** are the tabular's own language. A filled BMI is not known — it is the value the patient most plausibly had. A filled blood pressure records no episode. Neither code was meant to be assigned from a number nobody measured, and declining to do so is following the tabular rather than overriding it.

**`Z68` and `R06.82` carry no such instruction, and the rule still covers them.** Check for yourself — `Z68`'s only notes are its age boundaries and the growth-chart provenance, and `R06.82` carries an inclusion term and a list of exclusions. So the rule is not *derived* from the tabular; it is **confirmed** by it where the tabular happens to speak. What the rule actually rests on is the structural test in the paragraph above: does this code turn on a number the encounter recorded? Citing `E66` where it helps is not the same as claiming the code set decides every case, and a rule that needed a supporting note per family would fail on two of its own four examples.

**Why one filled value is enough to matter.** `Z68` is banded to 1.0 BMI units through the 30s, and a height is invented in well over half of this corpus. From a real encounter — 48 F, weight 212, no height recorded:

```
5'4"  ->  BMI 36.4  ->  Z68.36
5'5"  ->  BMI 35.3  ->  Z68.35
```

One invented inch, a different code. Nothing in the finished note distinguishes the two, and nothing downstream can tell that an inch was chosen rather than measured.

**Age matters here too.** `Z68` adult codes are for persons 20 years and older; ages 2–19 take `Z68.5-`, which is a **CDC growth-chart percentile**. A filled height and weight for an adolescent produces a percentile that is invented twice over.

**What is still codable, and this is most of it.** The rule reaches the value, not the patient.

- A **documented** diagnosis of obesity, hypertension or asthma is codable from the Assessment however the vitals got there — **where the source documented it.** `E66.9` off a charted diagnosis is a given anchored to given text.

  **"Charted" means charted by the clinician, not written into the Assessment by the upstream skill.** The note arriving here is generated, so its Assessment can name a diagnosis that rests on nothing but a filled measurement — `clinical-note` is permitted to write one there, provided the FILLED block declares what it rests on. That entry is the measurement wearing a diagnosis, and step 2 strikes it: its only support is a value from step 1. Reading this bullet as blanket permission to code any `E66` sitting in an Assessment launders a filled height into a code in two moves, and the output reads perfectly well.
- A **given** vital codes normally. Only the filled ones are struck.
- A **derived** value whose inputs were all given is given for this purpose — a BMI computed from a recorded height and a recorded weight is a measurement, not an invention.

#### A hedged diagnosis is a given, and it is coded

`probable viral URI` is something the clinician wrote. [clinical-note](../clinical-note/SKILL.md) preserves the hedge on purpose — *"Never … soften a hedge — `prob viral` becomes `probable viral`, not `viral`"* — so it reaches this skill intact, and it reaches it as a **given**.

**So it is coded, and the documented symptoms are coded alongside it.** Both, not one instead of the other. A suspected diagnosis is usually the reason the encounter happened and the reason codes were asked for at all; a worksheet that refused it would be missing the thing it was opened for.

**That is the opposite of the rule above it, and the difference is what each one rests on.** A filled BMI is a number *nobody recorded* — the note reads identically whether it was measured or generated, and a code resting on it rests on an invention. `probable viral URI` was recorded, hedge and all. The uncertainty there is **documented rather than manufactured**, and a code proposed from it rests on something the encounter actually says. Uncertainty is not the same defect as invention, and the rule for one does not reach the other.

**The limit is on the code, not on the hedge.** Where the code's own descriptor names a **confirmed organism or a confirmed disease** and the encounter established neither, that code is not proposed. Propose what the encounter does document, and send the specific code to step 4 naming what would earn it:

```
COVID-19 — documented household contact, congruent symptoms, no test obtained

  propose:  Z20.822  Contact with and (suspected) exposure to COVID-19
  not:      U07.1    COVID-19 — the descriptor asserts the disease, and nothing tested for it
```

**The test is the descriptor, read against the note.** `Acute upper respiratory infection, unspecified` says *unspecified* and asserts nothing the note lacks, so `probable viral URI` codes to `J06.9` and the hedge costs nothing. `COVID-19` names the organism, and a note saying nobody swabbed cannot support it. The limit is narrow by construction — it fires on organism-specific and disease-specific descriptors, not on every hedge.

**Submission coding for a claim is generally taught the other way, and this differs from it deliberately.** Outpatient claim coding is taught to code the signs and symptoms rather than a `probable`, `suspected` or `rule out` diagnosis. **That is recalled, and nothing in this repo verifies it** — the official guidelines are prose in a PDF, they are not shipped here, and `reference/icd10cm-2026.sqlite` holds the tabular alone. Say it as recall if it comes up; do not cite a section number this repo cannot check. The difference stands either way, because this worksheet feeds an academic clinical-hours record rather than a claim, and the differential codes below are documentation of reasoning rather than candidates for submission.

**`Z03.-` is not proposed here**: it carries `excludes1: signs or symptoms under study- code to signs or symptoms`, every encounter in this corpus arrives with a complaint, and coding the symptoms is what the rule above already does.

#### The differential is coded, and none of it is for entry

Both branches of [clinical-note](../clinical-note/SKILL.md) carry a differential and both put a code on every entry — [SOAP.md](../clinical-note/SOAP.md) and [HP.md](../clinical-note/HP.md). Those codes **document medical decision-making**; they are not candidates for entry anywhere. Step 5 says what they document.

They get their own section, and **three parts rather than five**:

```
--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---
ICD-10  J20.9  Acute bronchitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**`NOT FOR ENTRY` is on the code's own line, and the heading is not enough by itself.** That is step 4's reasoning applied to a second block, for the same reason: a block heading does not survive being copied one line at a time. A note runs its differential five to seven deep, so this is five to seven code numbers sitting above the ones the clinician is actually there to enter.

**Two of the five parts drop, and two do not.**

- **Anchor** is the differential entry itself, named rather than re-quoted. The entry is in the Assessment with its rationale attached, which is more than a quoted fragment would carry.
- **Specificity** drops. A differential is coded at the unspecified level on purpose, so `needs: laterality` on a diagnosis the note is arguing against is noise in a block that already runs long.
- **Descriptor and confidence stay.** They are the two defenses against a fluent, plausible, wrong code number, and a differential code is exactly as easy to invent as any other. Look each one up.

**Where they must not go.** `reference/medatrax-fields.md` names `ICD-10-CM` as an Add Visit Data category, and that category takes the **preexisting diagnoses and the final diagnoses only** — what the patient had. `reports/diagnosisstatistics.aspx` reports across a whole rotation, and loading it with five to seven entries per encounter, most of them diagnoses the note argues *against*, would make it describe a caseload nobody saw.

**The uncertainty rule above applies inside the differential too, and this is where it bites hardest.** The entries most worth coding are the ones the encounter could not establish — a suspected pneumonia, an untested influenza — and those are exactly the entries where an organism-specific descriptor would assert what the note denies. `Z20.822` over `U07.1` is that rule, on a differential line.

### 4. Report what documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
<element the code set wants — laterality, wound length, time spent, episode of care>
  affects: <which proposed code>

--- NOT CODED, ANCHOR WAS FILLED ---
<the value, and that it was filled>
  NOT CODED: <code and official descriptor>
  needs: <the measurement that would earn it>

--- NOT CODED, NOTHING ESTABLISHED IT ---
<the suspected diagnosis, and what documents the suspicion>
  NOT CODED: <code and official descriptor>
  needs: <the result that would establish it>
  proposed instead: <the code the encounter does document>
```

This is the section with the most value in it. It tells the clinician what to document *at the bedside next time* so the encounter codes cleanly, which is worth more over a rotation than any single code proposal.

The second and third blocks are the same statement about different causes. `laterality not documented`, `height not measured` and `nobody swabbed` are all *this encounter did not record the thing the code needs*, and all three are fixed the same way — at the bedside, next time. Write them so the clinician can act on them:

```
--- NOT CODED, ANCHOR WAS FILLED ---
BMI 36.4 — derived from a filled height (5'4") and a given weight (212 lb)
  NOT CODED: Z68.36  Body mass index [BMI] 36.0-36.9, adult
  needs: a measured height. One inch moves this to Z68.35

--- NOT CODED, NOTHING ESTABLISHED IT ---
COVID-19, suspected from a documented household contact and a congruent presentation
  NOT CODED: U07.1  COVID-19
  needs: a positive test. The contact alone does not establish the disease
  proposed instead: Z20.822  Contact with and (suspected) exposure to COVID-19
```

**The third block is not the hedge rule refusing a diagnosis.** A hedged diagnosis is coded — that is settled above. What lands here is the narrower thing: a code whose **descriptor** asserts a confirmed organism or disease that the encounter never established. The diagnosis is still coded, by the code the encounter does support, and this block records what the specific one was waiting on.

**Every line in all three carries `NOT CODED` inline, on the same line as the number.** The code has to be named — the clinician who does know the true height, or who gets the swab back tomorrow, needs to know what it would have earned — so the defense cannot be hiding it. It is that the number never appears without its refusal attached, and never in the proposed-codes list where a reader is scanning for things to enter. A block heading alone does not survive being copied one line at a time.

### 5. E/M level — only if asked

Offer the supporting elements (problems addressed, data reviewed, risk) and let the clinician assign the level. Do not select an E/M level unprompted.

**The differential is where the first element is documented, and that is the job those codes do.** A differential entry with its rationale is a problem addressed. A suspected diagnosis that drove an order — a swab sent, a film taken — is what *data reviewed* is reviewing. And an entry the encounter could not exclude is the one that carries the most weight in that column, because an undiagnosed new problem with an uncertain prognosis is not a low-complexity problem however ordinary the visit felt.

So the codes on the differential are required, and none of them is for entry. They are not a claim in miniature; they are the written form of the reasoning, and the reasoning is the element.

**The MDM phrasing here is recalled, and nothing in this repo verifies it** — the same posture as the outpatient rule in step 3, and for the same reason: no guidelines ship here. Offer the elements, name that they are recalled, and let the clinician map them to a level.

## Completion

Every proposed code has a code number, a descriptor, an anchor, a specificity flag, and a confidence flag — five parts, no exceptions. A code missing any of the five is not ready to hand over.

**A differential code is the one shape with fewer, and it is not an exception to that sentence** — it is a different thing being written down. Number, descriptor, confidence, three parts, plus `NOT FOR ENTRY` on the line. Anything with five parts is a code proposed for entry; anything with three is documentation of reasoning. **The count is how the two are told apart**, which is why neither shape may borrow from the other.

And every value the FILLED block declared has been accounted for: either it supports no code, or it appears under `NOT CODED, ANCHOR WAS FILLED`. A filled value that quietly supports a proposed code is the defect this skill was rewritten to catch.

Every hedged diagnosis in the Assessment has been accounted for the same way: coded, or sent to `NOT CODED, NOTHING ESTABLISHED IT` with the code the encounter does support proposed in its place. A hedge that produced no code and no refusal is a diagnosis this worksheet silently dropped.
