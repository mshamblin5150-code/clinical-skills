# peds-bp — assertion set

Five encounters, all under 6, drawn from one walk-in shift, 2026. Visit date and site removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

This set exists for one thing day-a and day-b cannot test: **what the skill does with a vital the clinician deliberately did not take.** day-b's nine vital-less cases are the corpus's dominant shape — the line written whole or not at all. These five are the shape that inverts under 6, where the blood pressure alone goes missing out of a line that was otherwise written.

Opened for [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11).

## Why the set is not a day

day-a and day-b are whole shifts. This one is **the under-6 half of a shift, and it says so** — the five school-age and adult encounters of the same day are named in [shorthand/README](shorthand/README.md) and deliberately not extracted. A set is scoped to its question; this question is about small children, and four of the five omitted cases exist in that README to make one point, which they make better as prose than as fixtures:

**Within that single shift, all four children aged 7 to 9 carry a blood pressure and none of the five aged 5 and under does.**

## Status — one half, deliberately

**The inputs are in.** All five encounters are in [shorthand/](shorthand/), one file per case, de-identified.

**The reference has not been read.** The standing day-b held until 2026-08-11, for the same reason and under the same rule:

> **Until it is read, no drift row may be added to this set.**

[day-b](../day-b/assertions.md) is now the worked example of what lifting that rule buys: its reference read supplied every DRIFT row that set carries, and *failed* rows it had written from the inputs alone. One row came back **the opposite way round** from what the input suggested — the submitted note had addressed the finding, so a row claiming it was abandoned would have been false. Expect the same here.

Every row below is anchored on the **input** — the absence of a pressure, and the values the shorthand does supply — both readable before any run happens.

**The set has never been run.** `FILLED n/n` has no first value yet.

## The ruling this set enforces

Settled on [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11), 2026-08-11, against a reader's annotation in the corpus that had claimed the opposite.

**A small child's missing blood pressure is filled, like any other missing vital. There is no pediatric exception.** The Medatrax field is required, so something has to go in the box, and that leg carries the ruling on its own.

**The annotation was corrected the same day**, and this paragraph is the only durable record of it. The annotation lives in `scratch/`, gitignored, so nothing about it can be committed — but it had asserted that a small child's missing pressure is *"a genuine gap, not a fill"*, which is exactly what this ruling overturns, and it now records the ruling instead. That was the fourth of issue #11's asks.

**What the corpus changed, and what it did not.** The license's second leg reads *"transcription is all-or-nothing … so an absent vital carries no information about its value."* Measured 2026-08-11 over 559 encounters, that is true from 20 up — 95 of those 106 encounters with no pressure carry **no vital at all** — and false under 6, where 18 of 21 carry a line with the pressure alone missing. The absence there is a decision, written down eighteen times.

It changes the reasoning and not the outcome, because `clinical-note` had already answered it: *"Whether the measurement happened is beside the point."* Knowing the cuff never touched the arm still does not say what the reading would have been.

**And the ticket's other argument runs backwards.** It held that a small child's pressure has "almost nothing to reason from." The opposite is the case — 18 of those 21 encounters hand the skill a pulse, a temperature, a respiratory rate and an oxygen saturation as **givens**, where 95 of the 106 ungrounded encounters aged 20 and over hand it nothing. The under-6 fill is the *best*-anchored fill in this corpus, not the worst.

## FILLED — binary, all must pass

Six rows, same class and same bar as day-b's four. Each resolves to a value, an ordering, or the presence of a string — none of them moves with wording.

| # | Cases | Passes when | Fails when |
| --- | --- | --- | --- |
| P1 | 2, 3, 5, 8, 9 | All four Medatrax vital fields hold a value — blood pressure, respiratory rate, height, and BMI derived from height and weight — and **every one the shorthand did not supply is declared in the FILLED block carrying its value** | Any is left blank, reported under GAPS, or silently omitted. A FILLED line naming the field without its value fails too |
| P2 | 5, 9 vs 2, 3, 8 | Both infants' filled systolic is **below** every filled systolic in the three older cases | An infant is given a pressure at or above a preschooler's — the signature of one value pasted across the set |
| P3 | 2, 3, 5, 8, 9 | No filled pressure reads as an adult value — systolic **below 120** and diastolic **below 80** | Systolic ≥ 120 or diastolic ≥ 80 on any of the five |
| P4 | 3, 5 | Every **given** value appears unchanged and nothing is filled over it — case 3's `hr 125 t 98 rr 24 spo2 95%`, height 38 in and weight 46 lb; case 5's `HR 113 T 98.0 rr 26 Spo2 94%` and weight 21 lb | A recorded value is replaced, rounded, unit-converted, or duplicated by a generated one |
| P5 | 2, 3, 5, 8, 9 | Every **filled** vital or measurement outside the range for that age is named in the Assessment or the Plan | It reaches the Objective and the FILLED block and stops |
| P6 | 2, 3, 5, 8, 9 | **No** antihypertensive, echocardiogram, renal ultrasound, or nephrology or cardiology referral appears anywhere in the note | Any of those five appears — a hypertension evaluation generated off a number nobody measured |

### The rows are a chain, and P6 is the one that is new

P1, P4 and P5 are day-b's B1, B4 and B3 with the ages changed. **P2 is not B2 with the ages changed**, and that is the one place the two sets genuinely diverge — see below. **P1 is the ruling itself** — a run that files the pressure under GAPS fails here and nowhere else. **P5** is what makes a filled abnormal cost something. **P2 closes the cheat P5 leaves open**, and it does the job B2 does for day-b without needing a documented condition: hypertension is what makes an adult's normal pressure implausible, and no small child in this corpus carries a condition that does the same, so the enforceable claim is about the *relationship between the five values* rather than about any one of them.

**P2 needs no external table**, which is why it is stated as an ordering. Pediatric pressure rises with age, so a run that reasons will put a 9-month-old below a 5-year-old whatever numbers it picks, and a run that pastes 118/76 across all five cannot. The comparison is between two of the run's own outputs, so nothing has to be looked up to score it.

**P2 deliberately says nothing about case 3 against cases 2 and 8.** A 2-year-old at the 99.9th weight percentile can legitimately come in above a 5-year-old, and a row that punished that would be punishing the reasoning it exists to reward. Only the infant-to-preschooler gap is wide enough to assert.

**P3's thresholds are neither the repo's nor a pediatric table's, and that is worth being exact about.** `corpus_census.py` sets normal below **130** over 80, and that bar is useless here — a 5-year-old filled at 125 systolic would sail through it. P3 uses 120/80 instead, which is the textbook adult-normal reading rather than anything this repo had already ratified. So the row fires on exactly one thing: a value that would look unremarkable on an adult chart, and is therefore evidence the age was never reasoned about at all. It is deliberately loose at the top, because a genuinely high-for-age pressure in a small child still sits well below 120 and a tighter ceiling would fail the very runs P5 exists to elicit. **This set holds no pediatric percentile table**, and P3 is not a substitute for one; see *Still unresolved*.

**P6 is the row this ticket added to the repo**, and it is the cost of ruling *fill, no exception*. Drift row 4 grants a filled vital no exemption for being generated, so an elevated toddler pressure must be addressed — and the addressing is where an invented number can turn into an invented disease. Naming it, attributing it to the fever the shorthand documents, and rechecking when the child is well satisfies the row. Working it up does not. The failure condition is written as a list of specific orders because that is checkable against the output text without judgment.

**Only the absence of those orders is the pass condition**, and the row was narrowed to that deliberately. Naming the elevation and attributing it to the documented fever is what a good note does, but *how well* it does so is a sentence-quality judgment, and [fixtures/README](../README.md) puts those in REPORTED rather than letting them wear a binary badge. P5 already forces the naming; P6 only forbids the workup. **On case 3 — a well-child visit documenting no fever or distress — P6 has nothing to fire on and passes by default.** That is a real limit of the row, stated rather than hidden.

### Case 3 is the anchor, and P5 is where it pays

`weight 99.9th percentile height 59th percentil` is written by the clinician, next to a given height and a given weight. It is the only place in this repo where a small child's filled pressure has a documented reason to sit off the middle of the range.

**No row asserts that**, and the omission is deliberate. The 99.9th percentile weight is a *given* abnormal, so a row about it is drift-class, and drift rows are what the unread reference forbids. It is listed under *Still unresolved* to be promoted with the reference, not before.

## Still unresolved

- **The set has never been run.** Until it is, `FILLED n/n` has no first value to measure drift from — and a first run graded by the pass that produced it is a baseline, not a pass ([fixtures/README](../README.md)).
- **The reference.** Owed, per *Status* above. Reading it is what would let this set carry drift rows and answer *better / worse / neither*.
- **Case 3's `weight 99.9th percentile` is a given abnormal and this set claims nothing about it** — including whether the run carries it into the Assessment, and whether the filled pressure reflects it. Drift-class. Promote it with the reference or not at all.
- **Case 5's `Spo2 94%` is a given abnormal in an 11-month-old with a month of cough and a chest film read as CAP.** Same class, same deferral.
- **No sourced pediatric blood-pressure table is in this repo.** P2 and P3 are built to need none, and that is a constraint on how sharply this set can grade a filled value: neither row can tell a well-reasoned 96/58 from a lazy 100/60 in a 2-year-old. Closing that needs the age/sex/height percentile tables as a checkable reference, the way `icd10-cpt` needed the code set — [#10](https://github.com/mshamblin5150-code/clinical-skills/issues/10) is the shape of that argument.
- **Case 8's `temp this vist is 99.5` sits inside the exam prose rather than on a vital line.** Whether the skill reads it as a given temperature — and so declines to fill one — is untested here, and `corpus_census.py` counts it as a vital only because the word `temp` appears.
- **Case 2's `she … gave him tylenol` writes the wrong pronoun for a patient the same line calls `5 yo F`.** Preserved as written, like day-b case 2's `wt 62in wt 131`. Whether the skill silently adopts the wrong sex is untested.
