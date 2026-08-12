# peds-bp — assertion set

Five encounters, all under 6, drawn from one walk-in shift, 2026. Visit date and site removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

This set exists for one thing day-a and day-b cannot test: **what the skill does with a vital the clinician deliberately did not take.** day-b's nine vital-less cases are the corpus's dominant shape — the line written whole or not at all. These five are the shape that inverts under 6, where the blood pressure alone goes missing out of a line that was otherwise written.

Opened for [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11).

## Why the set is not a day

day-a and day-b are whole shifts. This one is **the under-6 half of a shift, and it says so** — the five school-age and adult encounters of the same day are named in [shorthand/README](shorthand/README.md) and deliberately not extracted. A set is scoped to its question; this question is about small children, and four of the five omitted cases exist in that README to make one point, which they make better as prose than as fixtures:

**Within that single shift, all four children aged 7 to 9 carry a blood pressure and none of the five aged 5 and under does.**

## Status — both halves built

**The inputs are in.** All five encounters are in [shorthand/](shorthand/), one file per case, de-identified.

**The reference is read.** All five submitted notes were opened in the portal on 2026-08-11 and are kept, un-de-identified, in `scratch/peds-bp-reference/` — gitignored, because they carry the visit date, the site, the preceptor and the patient references. The rule that stood until then:

> ~~Until it is read, no drift row may be added to this set.~~ **Lifted 2026-08-11.** [Issue #25](https://github.com/mshamblin5150-code/clinical-skills/issues/25).

**One drift row was added and the reference fails it.** D1 is case 3's 99.9th-percentile weight — the given abnormal this file had listed under *Still unresolved* as drift-class, to be promoted with the reference or not at all. It is promoted, and the submitted note states the percentile and never acts on it.

**Every FILLED row passes**, which is not the outcome [day-b](../day-b/assertions.md) had — its read *failed* two of the four rows that set held. Two of these five pass **vacuously**, and that is recorded in the table rather than counted as a win. See *What the reference could not test*.

Every row below is anchored on the **input** — the absence of a pressure, and the values the shorthand does supply — both readable before any run happens. The `Reference did` column is what the read added.

**The set has never been run.** `DRIFT n/n`, `FILLED n/n` and `REPORTED n/m` have no first value yet.

## The reference is a baseline, not a target

Same four verdicts as [day-a](../day-a/assertions.md) and [day-b](../day-b/assertions.md), and only *worse* is a regression.

- **Better** — the skill caught something the submitted note dropped.
- **Worse** — the skill lost something the submitted note had. The most important thing this set can find.
- **Neither** — different wording for the same content.
- **Out of reach** — the submitted note is better on information the skill never had. Matching this is not a target and failing it is not a regression — **the skill is required not to try.**

**The fourth class was owed here.** It was added to day-a on 2026-08-11, and the commit that added it recorded why peds-bp was left on three: *"neither has read its reference, so neither can host the class yet, and both belong to other tickets."* This is that other ticket.

**This set's instance of the class is sharper than day-a's or day-b's**, and the difference is worth stating. Theirs turn on what the clinician recalled from the room — a social history, an allergy reaction — where *out of reach* is an inference about his memory. **R2 turns on something the fixture itself removed.** Case 5's submitted note dates the cough from a named holiday; [shorthand/README](shorthand/README.md) redacts that anchor to `[HOLIDAY]` deliberately, because a fixed annual date plus `cough x 1 month` reconstructs the visit date. The skill's input *cannot* contain it. Nothing about the clinician's memory has to be assumed.

**Which holiday stays out of this file, for the reason it was redacted in the first place.** This set states its year, so naming it here would put the visit date back into the committed half by the same back door — the redaction has to hold in the assertions as well as the inputs. It is in `scratch/peds-bp-reference/case-05-submitted.md`, which is gitignored.

### The provenance question was asked, and it has no answer

These five were typed 52 days after the shift, and a submitted note does not say whether a value was measured at the bedside or supplied at write-up. **The clinician was asked directly, 2026-08-11, and could not answer**: *"i probably made them up… i can't give you a real answer."*

**So no row here may depend on the answer, and none does.** P1 asks only that something went in every box. P2 and P3 are properties of the numbers whatever produced them. P4 is about **given** values, where the shorthand supplies the comparison directly. P5 and P6 ask what happened downstream of a value, which is true of it whatever its origin.

## Where the exam lives is not consistent, and it constrains how a row may be worded

The read turned up one structural fact that changes what a DRIFT row can say here. **Three of the five notes put the entire physical exam in the Assessment box** and leave the Objective as a bare vital line; **two put it in the Objective** under a *Focused Physical Assessment* heading and leave the Assessment to the differential alone.

| | Objective box | Assessment box |
| --- | --- | --- |
| Cases 2, 3, 5 | vitals only | **exam narrative** + differential |
| Cases 8, 9 | **vitals + exam** | differential only |

A DRIFT row's whole shape is *did the finding get past the Objective into the Assessment*. On cases 2, 3 and 5 the exam narrative lands in the Assessment box **by default**, so "it reached the Assessment" is true of every exam finding on those three and tests nothing at all.

**So D1 fires on the differential, the Most Likely Diagnosis or the Plan**, and not on the Assessment box as a whole. That is day-b's D1 argument widened: there, a bare `BP` inside a boilerplate screening list was ruled not to be a naming; here a whole box is ruled not to be one.

## The ruling this set enforces

Settled on [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11), 2026-08-11, against a reader's annotation in the corpus that had claimed the opposite.

**A small child's missing blood pressure is filled, like any other missing vital. There is no pediatric exception.** The Medatrax field is required, so something has to go in the box, and that leg carries the ruling on its own.

**The annotation was corrected the same day**, and this paragraph is the only durable record of it. The annotation lives in `scratch/`, gitignored, so nothing about it can be committed — but it had asserted that a small child's missing pressure is *"a genuine gap, not a fill"*, which is exactly what this ruling overturns, and it now records the ruling instead. That was the fourth of issue #11's asks.

**What the corpus changed, and what it did not.** The license's second leg reads *"transcription is all-or-nothing … so an absent vital carries no information about its value."* Measured 2026-08-11 over 551 encounters, that is true from 20 up — 95 of those 106 encounters with no pressure carry **no vital at all** — and false under 6, where 18 of 21 carry a line with the pressure alone missing. The absence there is a decision, written down eighteen times.

It changes the reasoning and not the outcome, because `clinical-note` had already answered it: *"Whether the measurement happened is beside the point."* Knowing the cuff never touched the arm still does not say what the reading would have been.

**And the ticket's other argument runs backwards.** It held that a small child's pressure has "almost nothing to reason from." The opposite is the case — 18 of those 21 encounters hand the skill a pulse, a temperature, a respiratory rate and an oxygen saturation as **givens**, where 95 of the 106 ungrounded encounters aged 20 and over hand it nothing. The under-6 fill is the *best*-anchored fill in this corpus, not the worst.

## DRIFT — binary, all must pass

One row. A finding the shorthand documented that a note can drop between the Objective and the Assessment.

**It fires on the differential, the Most Likely Diagnosis or the Plan** rather than on the Assessment box, for the reason above.

| # | Case | The finding | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| D1 | 3 — 2 y M | `weight 99.9th percentile height 59th percentil`, written by the clinician alongside a given height of 38 in and a given weight of 46 lb | The weight is absent from the **differential, the Most Likely Diagnosis and the Plan**. **A sentence stating the percentile inside an exam narrative is not addressing it** — see below | **Stated it and stopped.** The Assessment box's exam narrative reads *"Weight is at the 99.9th percentile and height at the 59th percentile"*; the differential is developmental delay, autism spectrum disorder and sensory processing difficulty; the Most Likely Diagnosis is a well-child exam with developmental delay; and the Plan — psychology referral, screen time, school readiness, routine follow-up — **contains no mention of weight, growth, diet or nutrition.** Addressing it is *better*. |

**D1's fail condition is worded against the decoy the reference itself supplies.** The submitted note does contain the string `99.9th percentile`, so a row passing on the finding appearing *anywhere* would score the reference as having addressed it. It did not: the sentence is a transcription of the shorthand's own words into the box where this note happens to keep its exam, and the note's three diagnoses and four plan items are about autism.

**This is the row [issue #15](https://github.com/mshamblin5150-code/clinical-skills/issues/15) predicted from the other side.** #15 settled that a documented obesity handed a normal BMI with nothing said about it is a real defect, and put that row in [obesity-bmi](../obesity-bmi/assertions.md) as O2 because day-b had no anchor for it. **D1 is the anchored version**: the body measurement here is not generated at all, so nothing has to be assumed about plausibility. The percentile is in the clinician's own hand.

**And the BMI the record carries makes the point twice over.** The portal's BMI field reads **22.4** — arithmetically correct from 46 lb at 38 in, unremarkable on an adult chart, and above the 99th percentile for a 2-year-old. D1 does not assert anything about the BMI, because the BMI is derived from two **given** values and so belongs to neither class cleanly. What it asserts is that the abnormal the shorthand named in words has to reach the part of the note that decides something.

**Only one drift row was added, and the second candidate was declined deliberately.** Case 5's `Spo2 94%` is a given abnormal in an 11-month-old with a month of cough and a chest film read as CAP. The reference does not name the saturation anywhere outside the vital line — but it reads the film as CAP, makes that the diagnosis, and prescribes azithromycin, so the thing the saturation indicates is diagnosed and treated. A row would have to pass on *"the cause is treated"* as well as *"the number is named"*, and a second exit turning on whether treating pneumonia counts as addressing a saturation is a judgment call, not a value. [fixtures/README](../README.md) puts those in REPORTED rather than letting them wear a binary badge. It stays in *Still unresolved*.

## FILLED — binary, all must pass

Six rows, same class and same bar as day-b's four. Each resolves to a value, an ordering, or the presence of a string — none of them moves with wording.

**Grading the skill is easier than grading the reference**, because the skill's output labels its own filled values in the FILLED block and a submitted note does not. Every `Reference did` cell is written to hold whether the value was measured or invented.

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| P1 | 2, 3, 5, 8, 9 | All four Medatrax vital fields hold a value — blood pressure, respiratory rate, height, and BMI derived from height and weight — and **every one the shorthand did not supply is declared in the FILLED block carrying its value** | Any is left blank, reported under GAPS, or silently omitted. A FILLED line naming the field without its value fails too | **Populated all four on all five.** Blood pressure generated every time — 98/60, 94/58, 90/54, 100/62, 90/54 — plus a respiratory rate on three, a height on four and a weight on three, with the BMI derived from height and weight in every case. Not a blank, not a GAPS line. **This is the ruling being the clinician's own practice, five for five.** Whether he measured them or supplied them at write-up does not bear on the row: something went in every box. Matching this is *neither*; anything less is *worse*. |
| P2 | 5, 9 vs 2, 3, 8 | Both infants' filled systolic is **below** every filled systolic in the three older cases | An infant is given a pressure at or above a preschooler's — the signature of one value pasted across the set | **Passed, and showed the row's ceiling.** Both infants are at 90 systolic, against 94 for the 2-year-old, 98 and 100 for the two 5-year-olds — the ordering holds with four points of clearance. **But the two infants carry the identical 90/54.** The reference reasoned by age *band* and not by patient, which is a pass P2 cannot distinguish from a better one. Matching this is *neither*. |
| P3 | 2, 3, 5, 8, 9 | No filled pressure reads as an adult value — systolic **below 120** and diastolic **below 80** | Systolic ≥ 120 or diastolic ≥ 80 on any of the five | **Passed everywhere, with room to spare.** Highest systolic 100, highest diastolic 62. Nothing on this shift is near the 120/80 line. Matching this is *neither*. |
| P4 | 3, 5 | Every **given** value appears unchanged and nothing is filled over it — case 3's `hr 125 t 98 rr 24 spo2 95%`, height 38 in and weight 46 lb; case 5's `HR 113 T 98.0 rr 26 Spo2 94%` and weight 21 lb | A recorded value is replaced, rounded, unit-converted, or duplicated by a generated one | **Passed on both, every value.** Nothing rounded, nothing converted, nothing duplicated — and case 5's `axillary` survives as the route. **Case 8 is the stronger evidence and is not in the row's list**: `temp this vist is 99.5` sits inside exam prose rather than on a vital line, and the note reads it as a given, carrying T 99.5°F while keeping the 103°F at home as history. Matching this is *neither*. |
| P5 | 2, 3, 5, 8, 9 | Every **filled** vital or measurement outside the range for that age is named in the Assessment or the Plan | It reaches the Objective and the FILLED block and stops | **Never fired.** Every generated value landed inside the range for its age — the pressures, the heart rates, the respiratory rates, the heights, the weights and the derived BMIs alike. There was no filled abnormal for the row to lose, so it passes having tested nothing. *Neither*, and see *What the reference could not test*. |
| P6 | 2, 3, 5, 8, 9 | **No** antihypertensive, echocardiogram, renal ultrasound, or nephrology or cardiology referral appears anywhere in the note | Any of those five appears — a hypertension evaluation generated off a number nobody measured | **Passed on all five, and vacuously.** None of the five orders appears anywhere. But P6 is the price of a filled abnormal pressure and no filled pressure landed abnormal, so nothing put the row under load. *Neither*. |

### The rows are a chain, and P6 is the one that is new

P1, P4 and P5 are day-b's B1, B4 and B3 with the ages changed. **P2 is not B2 with the ages changed**, and that is the one place the two sets genuinely diverge — see below. **P1 is the ruling itself** — a run that files the pressure under GAPS fails here and nowhere else. **P5** is what makes a filled abnormal cost something. **P2 closes the cheat P5 leaves open**, and it does the job B2 does for day-b without needing a documented condition. day-b can lean on hypertension because a normal pressure in a hypertensive is something the note owes an account of — **not because it is implausible**; a treated hypertensive at 124/78 is the treatment working, and day-b's B2 was rewritten 2026-08-11 when the clinician said so. No small child in this corpus carries a condition that puts the same question to the note, so the enforceable claim here is about the *relationship between the five values* rather than about any one of them.

**P2 needs no external table**, which is why it is stated as an ordering. Pediatric pressure rises with age, so a run that reasons will put a 9-month-old below a 5-year-old whatever numbers it picks, and a run that pastes 118/76 across all five cannot. The comparison is between two of the run's own outputs, so nothing has to be looked up to score it.

**P2 deliberately says nothing about case 3 against cases 2 and 8.** A 2-year-old at the 99.9th weight percentile can legitimately come in above a 5-year-old, and a row that punished that would be punishing the reasoning it exists to reward. Only the infant-to-preschooler gap is wide enough to assert.

#### P2 was re-read against the rewritten B2, and it survives

[Issue #25](https://github.com/mshamblin5150-code/clinical-skills/issues/25) flagged that P2's design borrowed from the **old** B2 — the one that demanded an abnormal value from a documented hypertensive on the argument that a normal one was implausible, and that [#14](https://github.com/mshamblin5150-code/clinical-skills/issues/14) rewrote when the clinician said *"hell she may be compliant with her BP meds."* Read against the new shape, P2 does not inherit the defect, and the reason is worth pinning down because the two rows do look alike.

**Old B2 failed on two counts.** It demanded a specific *value*, which meant demanding an invented abnormal finding — the thing standing rule 2 forbids outright. And the population fact it rested on had a common, clinically *desirable* exception, so the row punished the best-treated patients.

**P2 has neither property.** It demands a *relationship* between two of the run's own outputs, and every value satisfying it is normal — 90 and 100 are both unremarkable pressures, so nothing abnormal has to be invented to pass. And its exception has nothing to protect: no input in this set argues for putting an infant above a preschooler, so a run that does has not made a defensible clinical call, it has stopped reasoning about age.

**What that means for the fix B2 got.** B2 gained a second exit — normal *and* the note accounts for it — and the analogous move here would be *infant below preschooler, or the note says why not*. **It is deliberately not made.** No child in this set carries a condition that puts the question, so there is nothing for an account to be an account *of*; and P5 already requires a filled value outside the range for age to be named in the Assessment or the Plan, so a run with a real reason to raise an infant's pressure already owes one there. A second exit on P2 would duplicate P5 and hand the pasting cheat an escape hatch.

**What the reference did expose is a different limit, and a real one.** It passed P2 while giving both infants **the identical 90/54**. So P2 certifies that a run separated the bands, and says nothing about whether it separated the patients. That is the ceiling of any row built to need no percentile table, and it is why the table stays in *Still unresolved*.

**P3's thresholds are neither the repo's nor a pediatric table's, and that is worth being exact about.** `corpus_census.py` sets normal below **130** over 80, and that bar is useless here — a 5-year-old filled at 125 systolic would sail through it. P3 uses 120/80 instead, which is the textbook adult-normal reading rather than anything this repo had already ratified. So the row fires on exactly one thing: a value that would look unremarkable on an adult chart, and is therefore evidence the age was never reasoned about at all. It is deliberately loose at the top, because a genuinely high-for-age pressure in a small child still sits well below 120 and a tighter ceiling would fail the very runs P5 exists to elicit. **This set holds no pediatric percentile table**, and P3 is not a substitute for one; see *Still unresolved*.

**P6 is the row this ticket added to the repo**, and it is the cost of ruling *fill, no exception*. Drift row 4 grants a filled vital no exemption for being generated, so an elevated toddler pressure must be addressed — and the addressing is where an invented number can turn into an invented disease. Naming it, attributing it to the fever the shorthand documents, and rechecking when the child is well satisfies the row. Working it up does not. The failure condition is written as a list of specific orders because that is checkable against the output text without judgment.

**Only the absence of those orders is the pass condition**, and the row was narrowed to that deliberately. Naming the elevation and attributing it to the documented fever is what a good note does, but *how well* it does so is a sentence-quality judgment, and [fixtures/README](../README.md) puts those in REPORTED rather than letting them wear a binary badge. P5 already forces the naming; P6 only forbids the workup. **On case 3 — a well-child visit documenting no fever or distress — P6 has nothing to fire on and passes by default.** That is a real limit of the row, stated rather than hidden.

### Case 3 is the anchor, and D1 is where it pays

`weight 99.9th percentile height 59th percentil` is written by the clinician, next to a given height and a given weight. It is the only place in this repo where a small child's filled pressure has a documented reason to sit off the middle of the range.

**It is now D1**, promoted with the reference as this section previously said it would be. The 99.9th percentile weight is a *given* abnormal, which makes it drift-class rather than FILLED-class, and the read is what let a drift row be checked against what the submitted note did rather than against the skill's own prior output.

**What no row asserts is the second half of the anchor** — whether the *filled pressure* reflects the documented weight. The reference put case 3 at 94/58, between the infants and the 5-year-olds, with nothing to say about whether the percentile moved it. P2 explicitly declines to compare case 3 with cases 2 and 8, so nothing here scores that. It stays in *Still unresolved*, and closing it needs the percentile table rather than another reference read.

## REPORTED — counted, not enforced

Two rows, and both exist because the reference read produced differences of the fourth class. Counted rather than enforced on day-a's terms: *"a bar is only worth having if it was set deliberately"*, and neither has been run even once.

| # | Cases | Claim | Reference did |
| --- | --- | --- | --- |
| R1 | 2, 3, 5, 8, 9 | No social, allergy or spiritual detail is asserted where the shorthand supplies none. Absent or not-reported phrasing is the passing form | Asserted on all five. `Social History: No tobacco, alcohol, or drug exposure` and `Spiritual History: No concerns reported` appear in every note and in none of the five shorthands. `Allergies: No known drug allergies reported` appears on **cases 3, 5 and 8**, whose shorthands carry no allergy line at all — cases 2 and 9 write `allergies nkda`, so those two are given and do not count. ***Out of reach*** — right in his note, forbidden in the skill's. |
| R2 | 5 | The onset of the cough is expressed as a **duration**. No named calendar date, holiday or season appears as the onset anchor | **Wrote the anchor**, naming the holiday the input redacts and dating the cough from it. ***Out of reach*** — [shorthand/README](shorthand/README.md) removes it on purpose, so the skill's input cannot contain it. |

**R1 is day-b's R1 with three cases instead of two, and one difference worth stating.** day-b's version covers social and allergy detail about adults, where asserting `NKDA` or `Works manual labor` is a claim with clinical weight. Here the assertions are about small children, and *no tobacco, alcohol, or drug exposure* in a 9-month-old is very nearly a tautology. **The row is kept at the same bar anyway**, because what it forbids is asserting the unsupplied, and a rule that relaxed when the assertion happened to be safe would not be checkable.

**R2 does not conflict with [#30](https://github.com/mshamblin5150-code/clinical-skills/issues/30).** That issue rules no OLDCARTS element may be blank, so the run *must* write an onset. The shorthand supplies `cough x 1 month`, which is a duration and satisfies it. What R2 forbids is converting that duration into a calendar anchor the input never carried.

**Both are counted, not enforced, and R2 is the one that could reasonably be promoted.** It resolves to the presence or absence of a date-shaped string, which is exactly the property [fixtures/README](../README.md) says makes a row enforceable. It is left counted only because the set has never been run and a bar nobody has measured is a guess. R1 turns on judging whether a sentence asserts or hedges, and stays counted for the reason day-a keeps R9 and R10 there.

## What the reference could not test

**Two of the six FILLED rows passed vacuously, and the table says so rather than banking them.**

P5 asks what a run does with a filled value that lands outside the range for its age. **No filled value on this shift landed outside its range** — the pressures, heart rates, respiratory rates, heights, weights and derived BMIs are all unremarkable for the ages carried. So there was nothing for P5 to lose track of, and it passed having tested nothing.

P6 forbids a hypertension workup generated off an invented number. **No invented number was elevated**, so nothing put the row under load either.

**That is the opposite of what day-b's read produced**, and the asymmetry is the point. day-b's reference *failed* two of its four FILLED rows — an unaccounted-for normal pressure in a hypertensive, and four abnormal filled pressures that reached the Objective and stopped. A bar the reference clears everywhere is a bar that may be set too low, and here two of them were not so much cleared as never approached.

**What that does not mean is that P5 and P6 are unnecessary.** They fire on a run, not on the reference, and the run has not happened. `clinical-note` is instructed to fill *"the value this patient most plausibly had … not from the middle of the normal range"*, and case 3 hands it a documented 99.9th-percentile weight to reason from. A run that takes that instruction seriously is exactly the run that produces the elevated toddler pressure P5 and P6 were written for. **The first run is what will say whether they bite.**

## Still unresolved

- **The set has never been run.** Until it is, `DRIFT n/n`, `FILLED n/n` and `REPORTED n/m` have no first value to measure drift from — and a first run graded by the pass that produced it is a baseline, not a pass ([fixtures/README](../README.md)).
- **P5 and P6 have never been under load.** The reference produced no filled abnormal, so both passed vacuously. Only a run can say whether they bite. See *What the reference could not test*.
- **Case 5's `Spo2 94%` is a given abnormal, and no row asserts it.** The reference does not name the saturation outside the vital line, but diagnoses the CAP the chest film shows and treats it — so a row would need a second exit turning on whether treating the cause counts as addressing the number, which is a judgment rather than a value. Declined as a DRIFT row on those grounds, 2026-08-11. Reconsider if a run drops the finding *and* the diagnosis.
- **Whether case 3's filled pressure reflects the documented 99.9th-percentile weight is not scored.** D1 covers the weight reaching the differential or the Plan; nothing covers the pressure moving with it, and P2 explicitly declines to compare case 3 against cases 2 and 8. Needs the percentile table, not another reference read.
- **No sourced pediatric blood-pressure table is in this repo.** P2 and P3 are built to need none, and the read measured what that costs: **the reference passed P2 with both infants on the identical 90/54.** So P2 certifies that a run separated the age bands and says nothing about whether it separated the patients — it cannot tell a well-reasoned 96/58 from a lazy 100/60 in a 2-year-old. Closing that needs the age/sex/height percentile tables as a checkable reference, the way `icd10-cpt` needed the code set — [#10](https://github.com/mshamblin5150-code/clinical-skills/issues/10) is the shape of that argument.
- **R2 is counted and could be enforced.** It resolves to the presence of a date-shaped string, which is the property that makes a row binary. Left counted until the set has been run once.

### Resolved by the reference read, 2026-08-11

- ~~**The reference.** Owed.~~ Read. `scratch/peds-bp-reference/`.
- ~~**Case 3's `weight 99.9th percentile` … Promote it with the reference or not at all.**~~ Promoted as **D1**, and the reference fails it.
- ~~**Case 8's `temp this vist is 99.5` sits inside the exam prose rather than on a vital line.**~~ The submitted note **reads it as a given** — T 99.5°F in the Objective, with the 103°F at home kept as history — and fills no temperature over it. Recorded in P4's `Reference did` cell. It remains untested *for the skill*, which is what the first run will answer; what is settled is that the clinician's own practice treats it as a value, so a run that fills over it is diverging from the reference rather than resolving an ambiguity.
- ~~**Case 2's `she … gave him tylenol` writes the wrong pronoun for a patient the same line calls `5 yo F`.**~~ **The patient is female.** The portal Gender field reads Female and the submitted note uses *she* throughout; the `him` is a slip in the shorthand. This is day-b case 2's `wt 62in wt 131` again — an input defect the fixture preserves and the reference settles. Whether the skill silently adopts the wrong sex is still untested, but there is now a right answer to test against.
