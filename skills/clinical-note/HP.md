# FNP H&P — template

The long-form branch of [clinical-note](SKILL.md). Tiering rules live in the skill; this file is the shape.

**The italicized instructions under each heading are the school's rubric, not commentary.** Obey them literally and keep them out of the finished note.

```
Chief Complaint
<one line>

Allergies (with reaction)
<allergen - reaction; and drug allergies separately; NKDA if none>

History of Present Illness (OLDCARTS)
<all eight carry a value; none is left blank or "not documented">
<Onset and Duration take a value naming more than one symptom's timeline where
the shorthand dates symptoms differently. Each is written duration-first as
"<duration> for <symptoms>", clauses separated by a semicolon — see SKILL.md>
Onset:
Location:
Duration:
Character:
Aggravating:
Relieving:
Timing:
Severity: <N/10, and the complaint it belongs to>

<then a short narrative paragraph: age, sex, who brought them, the course,
prior treatment and testing, current appearance>

Past Medical History including Medications (with reason for taking)
PMH:
<condition - ICD-10 code where the rubric's examples carry one>

Surgical history:

Medications:
<drug - reason for taking>

Family History (3 generations)
Patient:
Mother:
Father:
Maternal grandparents:
Paternal grandparents:
Siblings:

Social History:
Occupation, education, marital status, tobacco, alcohol, recreational drugs,
spiritual, cultural, environmental, nutrition, fitness, sleep
<one line each, in that order; every line carries a value and none is left blank
 or "not documented">

Subjective:
Review of Systems (systems pertinent to the chief complaint), Use short succinct
statements, and do not use sentences. You not allowed to use reviewed and negative.
<system: fragment; fragment>

Objective:
Vital signs
BP / HR / Temp / O2 Sat / Height / Weight / BMI

Physical Exam (pertinent to the differential)
Use short succinct statements, do not use sentences
<system: fragment; fragment>

Lab, x-ray, other tests
<given results; given orders carrying no result, marked as ordered;
 "No new testing today" only where the encounter ordered nothing>

Assessment
Give 3 differential diagnoses with rationale of how you excluded each to arrive at
the final diagnoses/diagnoses. Pre-existing diagnoses with ICD-9 codes, Actual
diagnosis/diagnoses with ICD-9 codes, Screenings appropriate for age, list them
even if you did not do any.

Pre-existing diagnoses with ICD-10 codes:
<condition - code>

Differential diagnoses with rationale:
<diagnosis - code>
<Most likely because … / Less likely because …>

Actual diagnosis/diagnoses with ICD-10 codes:
<condition - code>

Screenings appropriate for age:
<list>

Plan
Plan is decided upon by the preceptor, Non-pharmacologic, Pharmacologic,
Health Promotion/Patient Education, Referral/follow-up

Non-pharmacologic:
Pharmacologic:
<drug concentration; dose route frequency duration>
Health Promotion/Patient Education:
Referral/Follow-up:

Discussion
<short paragraph: why this presentation fits the chosen diagnosis, and the
significance of any genetic or chronic condition that is not driving the acute
illness but matters for counselling and future care>
```

## Section notes

**No OLDCARTS element is ever blank.** Eight headings, eight values — `not documented` beside any of them is a defect, not a disclosure. Where the shorthand supplies none, infer one that follows from the presenting complaint; that is the same act as the exam of a system the shorthand never mentions, which [SKILL.md](SKILL.md) lists as grounded and expected. Each filled element is declared in `FILLED·asserted` carrying its value.

**Severity is a numeric pain scale.** `6/10 facial pressure`, never a word and never blank. It is the one OLDCARTS element that is not ordinary filled content — it takes the filled-vital treatment, and the reasoning, the 0/10 boundary and the two forms in which the score is a *given* are all in [SKILL.md](SKILL.md) under *Filled vitals, body measurements and the pain score*. Do not restate them here; do apply them.

**ROS and Physical Exam** — the rubric bans sentences and bans the words *reviewed* and *negative*. Write `No wheeze; no increased work of breathing`, never `Respiratory reviewed and negative`.

**Family History** is filled almost entirely. Phrase every one as a report of absence — `No chronic illness reported` — never as an examined finding. Nothing in the shorthand grounds a grandparent's disease, and the rubric wants three generations regardless.

**Social History is no longer that**, and it used to be governed by the same sentence. Every one of the twelve lines carries a value, **and none of them is a hedge**: `tobacco not documented this visit` is a sentence defending the note rather than reporting on the patient, which drift row 12 has forbidden since issue #28. Which value each line takes is [SKILL.md](SKILL.md)'s business under *Which way a social or allergy slot reads* — two are settled by a count over the corpus, every other line by the grounding rule — and drift row 17 checks it. Do not restate those rules here; do apply them, and declare every filled line in `FILLED·asserted` carrying its value. Issue #29.

**Allergies (with reaction)** is the same class and takes the same treatment. `NKDA` where the shorthand is silent, never a hedge; a stated allergen is a given and survives unchanged; and where a drug the Plan proposes rests on an inferred `NKDA`, that FILLED line says so.

**`Lab, x-ray, other tests` is not a results-only line**, and its placeholder here said it was. A test the encounter ordered goes on it as an order carrying no result, because a given order is a given and having no value to report is not a reason to drop it. `No new testing today` is reserved for an encounter that ordered nothing — writing it over a plan line that names a test is a false statement about the visit, not a cautious one. [SKILL.md](SKILL.md)'s *A given order is a given* is the rule; drift row 18 counts it. Issue #66.

**ICD-9 vs ICD-10** — the rubric headings say ICD-9. That text is stale; supply ICD-10-CM codes under the heading as written. Codes follow [icd10-cpt](../icd10-cpt/SKILL.md): anchored to documented findings, and flagged for verification. Give it the tier assignment along with the text — it marks a code resting on a filled value `SOURCE: filled`, and the note body alone cannot say which values those are.

**Differential rationale** is the graded core. Each excluded diagnosis needs the specific finding that excludes it — `no facial swelling, no focal sinus tenderness` — drawn from the exam, whether that exam line is given or filled.

**The code on each differential entry stays in the note.** The rubric asks for it and this template has always carried it; what it is *for* is documenting medical decision-making, so it does not travel on to Medatrax's `ICD-10-CM` category the way the preexisting and actual diagnoses do. [SOAP.md](SOAP.md) now carries the same requirement, on one line rather than two — **the codes match across the branches, the layout does not have to.** Issue #19.

**No diagnosis the encounter did not establish gets a code that overstates it**, and that reaches `Actual diagnosis/diagnoses` as readily as the differential — a hedge is most often on the conclusion. [icd10-cpt](../icd10-cpt/SKILL.md) declines a descriptor naming a confirmed organism or disease where nothing established either: a suspected COVID-19 with no swab takes `Z20.822 Contact with and (suspected) exposure to COVID-19`, not `U07.1`. Drift row 13 in [SKILL.md](SKILL.md) checks it.

**Once a code is declined, the entry is named for the one that survives.** The rule is [SKILL.md](SKILL.md)'s under *Naming a differential entry*; what this template decides is where the refusal goes, and on this branch it is **line two**. The rubric's shape puts the code on its own line, so line one stays `<diagnosis - code>` and carries nothing else, and the rationale line absorbs the refusal along with everything else it already carries:

```
Pain in right leg - M79.604
Less likely because the 4/10 pain sits over a chronic wound and the tib/fib film ordered today has no result. M86.9 Osteomyelitis, unspecified NOT CODED, nothing established it.
```

**`Actual diagnosis/diagnoses` keeps the hedge instead**, the way [SOAP.md](SOAP.md)'s `Final diagnosis` does — **and so does the most-likely entry**, which on this branch means the hedge lands on line one and the refusal on line two exactly as it does for an entry argued against:

```
Differential diagnoses with rationale:
Community-acquired pneumonia, mycoplasma suspected - J18.9
Most likely because three weeks of cough, decreased air movement and a documented sick contact fit; the film ordered today has no result. J15.7 Pneumonia due to Mycoplasma pneumoniae NOT CODED, nothing tested for the organism.

Actual diagnosis/diagnoses with ICD-10 codes:
Community-acquired pneumonia, mycoplasma suspected - J18.9
Nothing tested for the organism, so J15.7 is NOT CODED; a positive titer would earn it.
```

**Drift row 22 names this branch's conclusion line by its own heading**, `Actual diagnosis/diagnoses`, rather than only [SOAP.md](SOAP.md)'s `Final diagnosis` — a grader who walked the row against the other branch's wording would fail the compliant note above for keeping the hedge the rule requires it to keep.

**That is the two-line layout absorbing a rule written for a one-line one, and it is the same rule.** What has to match across the branches is the codes and the naming, not the layout — the same encounter names the same entries whichever branch it is written in, and only the line breaks move. `python tools/differential_scan.py <a run directory>` reads this branch's shape as well as the other's, and checks the one limb of row 22 that is mechanical. Issue #68.

**Screenings** is a filled list keyed to the patient's age. The rubric wants it present even when nothing was done.

**Pharmacologic** carries doses. Concentration and volume are givens; the milligram equivalent is **derived** and its arithmetic goes in the tier block — in the block, never beside the drug. **A parenthetical on a Pharmacologic line, where there is one, holds the trade name and nothing else**: the tier of each part of the sig belongs in the tier block, and `Medications (with reason for taking)` is the heading where a reason lives. The rule itself is drift row 12 in [SKILL.md](SKILL.md).
