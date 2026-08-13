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

#### A given order is a given

The list above names numbers, doses, lab values, imaging results, stated findings and quoted patient speech. **An order is none of those and it is a given too** — a test sent, a film ordered, a referral made, a drug prescribed, an immunization directed. It is the part of the plan line the clinician unambiguously *did*, and it passes through unchanged like every other given: named in the Plan, named on the results line as ordered, and carried into GAPS where no answer came back.

**The note adds orders and never subtracts them.** Proposing an order the encounter did not run is most of what *What may be inferred* exists for, and it is cheap to be wrong about because the preceptor rules on it. Removing one the encounter *did* run is not the mirror of that and is not a proposal. **There is no tier it belongs to.** `FILLED·proposed` holds forward actions this skill contributes; declining to do what the clinician already did is not a forward action, and writing `Not sending a monospot` there dresses an erasure as a recommendation.

**A clinical objection to a given order is written beside it, never in place of it.** Where the order looks wrong — a contraindicated drug, a test the documented findings do not support — the order stays in the Plan with its sig, and the objection sits next to it as a recommendation for the preceptor to rule on. That is the conflict rule's shape exactly: *no given medication is dropped to dissolve a conflict*, reaching every kind of order rather than drugs alone. Deleting the order does not resolve the disagreement, it deletes the evidence that there was one. Drift rows 11 and 18.

**And the objection is written in the future tense, because the difference between a recommendation and a lie is the tense.** *Recommend the monospot be cancelled, the findings do not support it — preceptor to rule* is a proposal about what should happen next. *No monospot sent on those findings* is a claim about what did happen, and it is false. **Retaining the order does not make the second one true**: a note carrying `Monospot, ordered` on the results line and `No monospot sent` in the Assessment has satisfied the paragraph above and still contradicts itself, and the reader who is graded on the Assessment meets only the false half. So the rule has two limbs and both bind — **the order survives, and no sentence anywhere in the note says it was not placed.**

[peds-bp](../../fixtures/peds-bp/shorthand/case-08.md) is the worked example of it going right: the plan line prescribes a cough-and-cold combination to a five-year-old, which carries a labeled contraindication under six. The correct note keeps the drug in the Plan with its sig, and puts the contraindication beside it as a recommendation to withhold for the preceptor to rule on. It does not report that the drug was not given, because it was.

**Dropping one is worse than the defects it gets mistaken for, because the note then documents the opposite of what happened.** A drifted finding is something the note failed to say; a dropped order is something the note says that is **false about the encounter**, on a record signed under the clinician's name. A run over [day-b](../../fixtures/day-b/shorthand/case-12.md) carried six of that plan line's seven tests, omitted the monospot, and wrote `No monospot sent on those findings` into the Assessment. The submitted note carried all seven. Then the run cited its own omission under drift row 15 as a workup withheld on given findings — so the note **graded the erasure as a pass**, which is why row 18 exists rather than being left to row 15's reading. Issue #66.

#### A duration belongs to what it is written next to

Shorthand hangs one duration off the end of a multi-symptom complaint and then dates a symptom differently further down:

```
cc: sinus pressure, congestion, sneeze, cough x 2 days
exam: states this started yesterday, pain inface is worse
```

Read as one timeline stated twice, that is a contradiction, and resolving it means choosing one number over another — which the paragraph above forbids outright. Read as two facts about two symptoms, there is no contradiction to resolve.

**Read it as two facts.** A duration attaches to the symptoms it was written beside: the chief complaint's number covers the symptoms the chief complaint lists, and a later onset statement covers whatever that statement is about. The example is congestion, sneezing and cough for two days with facial pain newer and worsening, and a note saying so has dropped nothing and invented nothing. **It is a conflict only when the same symptom carries two numbers** — `cough x 5 days` against `cough started 2 days ago`.

That distinction is not bookkeeping here. Acute bacterial rhinosinusitis is defined by ten days or more, **or by worsening after initial improvement**, and the second criterion is exactly what a newer, worse facial pain is. A note that folds it into the chief complaint's two days has destroyed the finding the antibiotic decision turns on.

**Where the onset statement names its symptom, attaching it is reading.** `right earache yesterday` inside a complaint given as `x 2 days` needs no referent worked out — the same act as correcting `endometroises`, and disclosed the same way, which is to say not at all.

**Where it uses a pronoun — `this`, `it`, `sx` — it attaches to the newer symptom only if the same clause marks something new or worse.** `pain inface is worse` is that marker; so are `now also`, `new`, `worsening`, `worse today`. **With no marker a pronoun means the whole illness**, and then it is a genuine conflict. This is the one call in the rule that can be wrong, so it is the one that gets declared.

**A genuine conflict is written as a span containing both.** `Duration within the past 1 to 2 days`, never one endpoint chosen over the other. Both stated values survive as the span's endpoints, so nothing is rounded, replaced or corrected, and *Never "correct" a number* stands untouched. The form is his own rather than this file's invention: the shorthand writes `11-12 yrs ago` and `worsening in the past 3-4 days`, both in `fixtures/day-b/shorthand/case-11.md`, and `tools/test_corpus_census.py` asserts them rather than trusting this sentence.

**Drift row 11 does not own this, and what separates them is whether a span exists.** Row 11's conflicts — a drug against a documented condition, a drug against a drug — are *named* rather than resolved, because no single value contains both `ibuprofen 800 TID` and `GERD`; the only honest thing to do with them is say they clash. Two durations are points on one ordered scale, so a span contains both without preferring either. **The rule is written for durations because durations are what was ruled on.** The reasoning carries to any givens that order — two weights, two doses — and carrying it there is a decision somebody has to make, not a reading of this paragraph.

**And it is never a FLAG.** The run this rule replaces carried both durations into the note verbatim and raised `Onset - states this started yesterday; chief complaint records 2 days`, which is the note reporting that it could not read its own input. FLAG holds a documented finding the note failed to act on; a timeline the note read and wrote down is not one. Issue #33.

**A pronoun-resolved attribution is declared, carrying its value**, and so is a span. Neither is a filled *value* — every number involved is a given — but both are generated: the shorthand nowhere says which symptom started yesterday, and nowhere writes `1 to 2 days`. They are claims about the patient's past, so they go under `FILLED·asserted`, which is where a preceptor rules on an inference:

```
FILLED·asserted   DURATION facial pain 1 day, attached to "states this started
                  yesterday" on the "pain inface is worse" beside it; the chief
                  complaint's 2 days covers the congestion, sneezing and cough.

FILLED·asserted   DURATION 1 to 2 days spans a conflict — the chief complaint
                  says 2 days and the history says 1, both about the cough.
```

An attribution the onset line named for itself gets no such line. Declaring it would be reporting this skill's own compliance, which *What never goes under GAPS* already refuses one block down, and a block full of those is a block nobody reads.

**One OLDCARTS box, both values.** Onset and Duration are one element each, and *eight, always eight* forbids a blank rather than a compound value. A value naming two timelines is the only form that keeps every given inside the mandatory element; moving a symptom's onset out into the narrative paragraph puts a given somewhere nothing checks it.

**Each timeline is written duration-first, `<duration> for <symptoms>`**, and that is a requirement rather than a preference. Written symptoms-first, the clause boundary is a comma sitting among the commas of the symptom list, and `congestion, sneezing and cough 2 days ago, facial pain 1 day ago` gives a reader nothing to tell a new timeline from a fourth symptom. Duration-first, every clause opens with the one token that can only start a clause:

```
Duration: 2 days for congestion, sneezing and cough; 1 day for the facial pain, worsening
```

**The clause separator is the branch's, and on SOAP it cannot be the semicolon.** [HP.md](HP.md) gives each element its own line, so the semicolon above has nothing to collide with. [SOAP.md](SOAP.md) runs all eight onto **one semicolon-separated line**, where that same semicolon would read as the boundary between Duration and Character and silently split one element into two. There the clauses take a comma, and duration-first is what keeps them legible:

```
Duration - 2 days for congestion, sneezing and cough, 1 day for the facial pain, worsening
```

(The separator between the element and its value is a third thing again, and *Punctuation*'s business rather than this rule's — as it is for the severity.)

**Onset and Duration both take the compound value, and they are not interchangeable.** Duration is how long each symptom has run; Onset is when each began and what it began with. A conflict resolved to a span lands in whichever element states it — `Duration within the past 1 to 2 days`, and Onset the corresponding range of start times.

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
  - **History, medications, surgical, family, social, allergies** — an omitted section is inferred from the rest of the encounter. A history of hypertension and no `meds:` line means a med rec was not done, so infer the likely regimen.

  Either way it gets filled, never raised as a gap.

  **Which of the two readings a section takes is not always obvious, and for the social and allergy slots it is measurable.** *Which way a social or allergy slot reads* below settles those; nothing else in this file assigns a section to a reading by argument alone.

  **`Never write "none" where the shorthand is merely silent` used to close that second bullet, and it was too broad.** It is right about a `meds:` line: an absent line means no reconciliation was done, so *none* would be a conclusion drawn from silence, and inferring the regimen is the instruction instead. It is wrong about `NKDA`, which is not a conclusion drawn from silence — it is the value that patient most plausibly had, and [SOAP.md](SOAP.md) has instructed it all along. So the rule is narrower than it read: **never write "none" as a conclusion from silence.** Where the slot's own evidence points at the unremarkable value, writing it is the job. Issue #29.

Every filled *finding* is therefore normal, absent, or not reported — and says so in those words: `no chronic illness reported`, `fever by history`, `no smoke exposure reported`, `no treatment-limiting cultural practice reported`.

**`not reported` there is a claim about the patient, not a hedge, and the difference is drift row 12's.** `no smoke exposure reported` says the patient has no smoke exposure; `tobacco status not documented this visit` says this skill was not told. The first reports and stays; the second defends the note and is banned wherever it appears — see *Which way a social or allergy slot reads*, which is what stops this sentence being read as licensing a hedge in the `SH:` line.

Charted normals and filled normals read identically in the finished note. They are separated in the tier block so only the filled ones need confirming — and *identically* is literal, which is why *The tier language stays out of the note* below forbids annotating them apart.

#### Which way a social or allergy slot reads

**The templates enumerate these slots, so each one is a box.** [SOAP.md](SOAP.md) writes `SH: <occupation; education; marital; tobacco; alcohol; drugs; spiritual; environmental; nutrition; fitness; sleep — one clause each>` and `Allergies (reaction): <allergen - reaction; NKDA if none>`; [HP.md](HP.md) lists twelve social lines *"one line each, in that order"*. So the two-part test that licenses a filled vital holds of every one of them — a box demands a value, and the shorthand constrains none.

**No slot ever reads `not documented`, and that was never new law.** `Allergies (reaction): Not documented this visit.` reports nothing about the patient: strike the inference above it and the sentence has nothing left to do. It is `No medication reconciliation was performed this visit` with the nouns changed — the sentence issue #28 banned, and **drift row 12 has forbidden it since.** The same goes for `tobacco status not documented`, `alcohol not documented`, `status unknown` and `not reported this visit`. What row 12's test permits is a claim about the patient: `Non-smoker`, `no smoke exposure reported`, `No chronic illness reported` all report, and all stay. Issue #29.

**Which value the box takes depends on which reading its slot has, and the corpus decides that per slot.** *Silence is undocumented, never absent* reads two ways, and asking which way a slot goes is asking a question about this clinician's transcription rather than about clinical practice in general:

- **A slot he writes even when the answer is nothing** is a habitual template field. Silence in it is a transcription gap, so the note fills the **unremarkable** value — and that value is not a bland pick from the middle, it is what the record says such patients mostly are.
- **A slot he writes only when there is something in it** is charted the way an abnormal is. Silence in it is a real **absence**, so the note fills the **negative** — and filling a positive would be inventing an abnormal finding, which standing rule 2 forbids outright.

**Two slots are measured and they land opposite ways.** The figures below are over the **31 committed fixture inputs**, and `tools/test_corpus_census.py::SocialSlotsSplitTwoWays` is what recomputes them — it pins the classification case by case, so a fixture edit fails a test rather than quietly voiding the rule. `corpus_census.py` prints the same two rows against the corpus, which is the wider measurement and the one still owed:

| Slot | Written | Says nothing | So silence is | Filled value |
| --- | --- | --- | --- | --- |
| Allergies | 16 of 31 | `NKDA` 11 of 16 | a gap | `NKDA` |
| Tobacco | 15 of 31 | denied 1 of 15 | an absence | `Non-smoker` |

**Those figures are over the 31 committed fixture inputs, which is a floor and not the corpus.** `corpus_census.py` prints the same two rows against `scratch/`; **it has not been run against the corpus since it gained the ability to** — re-run before leaning on the numbers. What the fixture count establishes is the direction, and the direction is what the rule turns on: he writes the allergy slot to say *nothing* eleven times, and the tobacco slot to say *nothing* once.

**So a positive tobacco status is never filled.** Not `vapes occasionally`, not `former smoker`, not `smokes 0.5 PPD`, however plausible the patient makes it. This is the same argument the corpus settled for blood pressure at issue #23 — *a documented condition is an anchor to reason from, never a verdict to produce* — arriving at a slot instead of a value. A tobacco history is an abnormal finding, an abnormal finding in the note must be a given, and there is no exception for a slot that happens to be enumerated. `fixtures/day-a` R14 holds this.

**Every remaining slot takes the grounding rule, unchanged.** Occupation, education, marital status, spiritual, cultural, environmental, nutrition, fitness and sleep are transcribed too rarely to classify at all, and alcohol and recreational drugs are usually denied inside a shared list — `no smoke, drink, drugs` — where the negation does not sit beside the word it negates.

**Age grounds more than marital status, and occupation is the one worth naming.** *Marital status* under *Conventions* already infers from age; **`Retired` follows from an age past retirement on exactly the same footing**, and a 71-year-old's occupation slot is filled rather than hedged or guessed at. What age does not ground is *which* occupation, at any age — that is the `Works manual labor` failure with the anchor changed. So the slot reads `Retired` where age supplies it, `Employed` where the encounter supplies only that the patient works, and neither is stretched into a trade.

**Education, nutrition, fitness and sleep are the slots with no anchor at all**, and they are where an ungrounded assertion actually shows up in practice — `fixtures/day-b` R1 records a run asserting a diet, an exercise habit and a sleep duration on patients whose shorthand mentions none of the three. Grounded content exists for them: a documented diabetes grounds a dietary line, a documented sleep apnea grounds a sleep one. **Absent that, the slot takes the least it can say and stays there** — the rubric wants the line present, not a life story in it. (**No count is quoted, because the two branches enumerate different lists** — [SOAP.md](SOAP.md) writes eleven social clauses and [HP.md](HP.md) twelve, `cultural` being HP's alone. A number here would be wrong on one branch or the other.) For all of them, *What may be inferred* governs: **grounded in what the shorthand contains, never invented beside it.** `at work` grounds `Employed`; it does not ground `Works manual labor`, because nothing in a laceration says manual labor rather than a paper cutter. Age grounds `Married`, which *Marital status* under *Conventions* already instructs. The slot is never blank and never hedged, and the note does not write a biography it has no source for. `fixtures/day-b` R1 holds this.

**An inferred allergy status may raise an obligation and may never discharge one.** This is *A filled vital may raise an obligation and may never discharge one* below, reaching the one filled value outside that section's three members that can quietly make a decision look safe. A run that fills `NKDA` and then **proposes** a drug on it has let a generated value underwrite a prescription — `#27`'s move, in a place drift row 15's class does not reach.

**The note still proposes the drug.** Withholding treatment over a gap in the paperwork is the worse failure, and the givens are what the proposal rests on. What changes is the disclosure: **where a proposed drug rests on an inferred allergy status, that FILLED line says so**, in the shape *Where a filled normal pressure is what the Assessment's account rests on* uses below:

```
FILLED·asserted   ALLERGIES NKDA inferred; the Plan's amoxicillin-clavulanate
                  rests on it, and no allergy history was taken.
```

The reason is that rule's reason. Two independent FILLED lines say an allergy status was inferred and a drug was proposed; **neither says the second is standing on the first.** One of the sixteen written statuses in the fixtures names a drug allergy, so `NKDA` is usually right — and *usually* is exactly what a prescribing decision may not rest on silently.

**A given allergy status is never overwritten, and a stated allergen is never dropped.** `allergic to prednisone` is a given like any other, and it behaves like the conflict rule below: a drug proposed against a documented allergy is called out, and no inferred status dissolves it.

**The allergy slot is the only one of these that needs the disclosure, and that is a fact about the slots rather than a narrowing of the rule.** The rule is general — **an inferred detail that drives a downstream clinical action discloses what leans on it** — and it comes out satisfied everywhere else by construction. The tobacco slot never reaches it, because a positive fill is forbidden outright and a negative one triggers nothing: there is no screening, no cessation counseling and no differential entry owed for a non-smoker, and [SOAP.md](SOAP.md)'s pack-year screening line keys to a **given** history. The remaining slots carry no clinical action at all — an occupation, an education level and a marital status change nothing the Plan does. **A future slot that did would take this same disclosure**, and the test for it is the one stated here: does the note do something differently because of the inferred value.

**Every filled slot is declared in `FILLED·asserted` carrying its value**, on the rule the filled-vital block states for the same reason: the clinician confirms a value, not a category. Not `social history filled` — `SH tobacco Non-smoker filled`, `ALLERGIES NKDA filled`, `SH occupation Employed filled`.

#### Filled vitals, body measurements and the pain score

**Filled vitals, body measurements and the OLDCARTS pain score** are permitted where the rubric requires a complete set and the encounter supplies only some — or none. They are the one exception to *filled content is unremarkable*, and the exception is narrow enough to state exactly.

**The class is a test, not a list.** A value joins it when both of the next two paragraphs hold of it: a box demands a value, and the shorthand constrains none. Three members are named because three are known — anything else has to earn entry by those two arguments, and **no exam finding, symptom or result will ever pass them.** A result has no box standing empty, and an unmentioned system is already answered by *Silence is undocumented, never absent* one level up.

A vital is not a finding the clinician chose to record, and two things follow that do not follow for a finding.

**A value is required.** The rubric wants a complete vital set, and Medatrax holds fields for blood pressure, respiratory rate, height and BMI that are filled rather than left blank. The rubric's HPI is the same shape: eight OLDCARTS boxes, one of them severity. A result has no field standing empty in the same way — it exists only if testing was ordered and run. Something has to go in the box.

**Nothing in the shorthand constrains which value.** Transcription is all-or-nothing: measured 2026-08-11 across 551 encounters, 46% carry no vital at all, and of the 249 blood pressures he does transcribe, half are below 130/80. He is not writing them down because they were interesting, so an absent vital carries no information about its value — and never means it was normal. That is *Silence is undocumented, never absent* applied to the one kind of value where "undocumented" and "unremarkable" come apart. For a finding, silence is evidence, because abnormals get charted. For a vital, silence is evidence of nothing.

**Whether the measurement happened is beside the point**, which is what height makes obvious. In 15 encounters he transcribes a blood pressure and a weight and no height, and nothing in the record says whether that height was taken and left unwritten or never taken at all. Neither leg above asks. The license rests on the box needing a value and the shorthand constraining none, never on a tape measure having touched the wall.

> **A filled vital is the value this patient most plausibly had.**

Reason it from age, body habitus, the documented conditions and the presenting complaint — not from the middle of the normal range. A two-year-old gets a two-year-old's pressure, not a scaled-down adult's.

**A documented condition is an anchor to reason from, never a verdict to produce.** This paragraph read *a known hypertensive seen for a productive cough gets a hypertensive pressure and a raised respiratory rate* until 2026-08-11, and both halves failed the same way: they turned an anchor into an instruction to generate an abnormal, which is what standing rule 2 forbids outright.

The corpus settles the first half. Measured 2026-08-11, **175 of 551 encounters document hypertension, 96 of those transcribe a pressure, and 39 of the 96 are normal** — below 130/80 on every reading in the note. A rule demanding a hypertensive pressure from every documented hypertensive contradicts four of this clinician's own transcribed readings in ten, and the readings it contradicts are the treated patients sitting at target. `corpus_census.py` recomputes all four figures. Issue #23.

**The second half is retired by argument, not by count**, and the difference is worth stating rather than blurring: no equivalent measurement exists for respiratory rate, and none was made. The argument is the same one. A productive cough makes a raised rate *plausible*; it does not make a normal rate implausible, and only implausibility could license demanding the abnormal. That generalizes to every condition and every vital — hypertension is simply the one this repo has counted.

**A small child's anchors are different, not absent.** The adult anchors — documented hypertension, body habitus — are usually missing under 6, which invites the conclusion that there is nothing to reason from and the middle of the range is all that is left. The corpus says the reverse. Measured 2026-08-11, **18 of the 21 encounters under 6 carry a transcribed vital line with the blood pressure alone missing** — 17 a structured line, one a temperature written into the exam prose — where 95 of the 106 encounters aged 20 and over with no pressure carry no vital at all. Both figures are over the 357 encounters whose age the census can read; 194 state none, so 21 is a floor on the under-6 population rather than a count of it. A young child's fill is the best-anchored one in this record, not the worst: the pulse, temperature, respiratory rate and oxygen saturation are usually sitting right there as givens.

Work it in two steps:

- **The band comes from age, sex and height percentile** — which is how pediatric pressure norms are defined in the first place. Where the height is not given, fill it first and use it.
- **The position within the band comes from the encounter** — the given pulse and temperature, the distress the exam describes, any documented weight percentile. A fussy, febrile toddler with a pulse of 125 does not sit at the fiftieth percentile.

**No age boundary applies here.** The rule is continuous: the anchors shift with age and nothing switches on at a birthday. This repo already carries three incompatible age lines — `Patient Time` at 18, `Z68`'s BMI band at 2–19, and the 6 the corpus happens to show — and this is deliberately not a fourth.

**A missing pressure in a small child is still filled, and never a GAPS entry.** It is the one band where silence about a vital genuinely is informative: the pressure was decided against rather than merely left unwritten, eighteen times out of twenty-one. That changes the reasoning and not the outcome, because *whether the measurement happened is beside the point* — knowing the cuff never touched the arm still does not say what the reading would have been, and the Medatrax field is required whatever the patient's age. Issue #11.

**A filled vital that lands abnormal is worked up like any other abnormal.** It reaches the Assessment and the Plan; drift row 4 applies to it in full. This is the cost of the license and it is not optional — a note that invents 142/88 and then says nothing about it has manufactured the exact defect this skill exists to catch.

**Worked up does not mean the disease is worked up.** Where the encounter documents a cause for the elevation — fever, pain, a crying child — the response is to **name it, attribute it to that cause, and recheck when the patient is well**. A raised pressure in a febrile, distressed toddler is addressed by a recheck when afebrile and calm; never by an antihypertensive, an echocardiogram, a renal ultrasound or a nephrology referral. Row 4 asks that a generated value not be abandoned. It does not ask for the evaluation of a condition nothing documented — that is a second invention resting on the first, and it is the one standing rule 2 forbids outright.

**The cause has to be a given finding**, which is what *documents* means here. `cc: fever` with no temperature anywhere still accounts for the pressure — the documented fever does the work and the degrees are incidental, so filling them changes nothing. What fails is a cause that is itself generated: a run that fills a fever, fills a pressure, attributes the second to the first and books a recheck has invented both halves of its own reassurance. Row 4 reads as satisfied and nothing was worked up.

**A filled vital or measurement that lands normal against a documented condition owes an account.** This is the mirror of the abnormal-value paragraphs above, and it closes the opposite cheat. Where the value **is** that condition's own diagnostic measure, a normal number is a claim about the disease's state whether the note intends it as one or not. Filling 124/78 for a documented hypertensive and saying nothing about it is indistinguishable from picking a bland number out of the air, and *indistinguishable* is the whole problem: the two runs produce the same document.

**This repo has two instances of it, and they were arrived at separately.** Blood pressure against a documented hypertension is this one. **BMI against a documented obesity is the other**, and it was already fixtured before this rule was written — `fixtures/obesity-bmi` O2 asks for a filled BMI of 30.0 or above, *or* below 30.0 with the Assessment saying the obesity is resolved, improved or post-surgical, or naming the weight-loss intervention. That is the same rule with the nouns changed, including its exclusion: an `E66` sitting in a problem list is no more an account than an `I10` is. Two independent derivations landing on one shape is the argument for stating it generally.

The requirement is still narrow. It does not reach a documented asthmatic's filled oxygen saturation of 98%, because saturation is not what asthma is diagnosed by and a normal one makes no claim needing support. Only a value that measures the condition itself carries this obligation.

**The account takes one of four forms, and it is made in the Assessment.** For hypertension: the Assessment calls it **controlled**, **treated**, or **on therapy**, or it **names the medication**. These are bounded so that scoring them needs a reader rather than a taste. A code sitting in a pre-existing list is not an account — `HTN I10` among six others says the condition exists, not that the number makes sense — and neither is a monitoring instruction: `BP monitors at home` says to watch the value rather than explaining it. `fixtures/day-b` B2 scores these same four, and `fixtures/obesity-bmi` O2 scores obesity's equivalents.

**The Assessment is where it must appear, and that is not a formality.** A medication sitting in the Medications list is not an account on its own: a reader working through the Assessment — which is where the note's reasoning is graded — sees a normal number and no statement about it. The account has to be somewhere a reader of the reasoning will meet it.

**Either exit is legal, and only silence fails.** An abnormal filled pressure worked up per the paragraphs above passes. A normal one with an account passes. What fails is a normal number and no account of why it is normal.

**The inferred regimen may be what the account rests on, and that is not a second invention resting on the first.** *Silence is undocumented, never absent* already licenses inferring the likely regimen where a hypertension history carries no `meds:` line. That inferred drug is then available to the fourth form above: an Assessment reading `Essential hypertension (I10), controlled on lisinopril` has accounted for its own 124/78, and the inference is what makes that sentence writable. **The regimen enables the account; it does not substitute for it** — putting lisinopril in the Medications list and leaving the Assessment silent fails, per the paragraph above.

That resembles the compounding forbidden above without being it, and the difference is exactly one thing: **the condition is a given.** What is forbidden there is evaluating a condition nothing documented — an invention resting on an invention. Here the hypertension is in the shorthand, and two separately licensed fills are agreeing with each other rather than one propping the other up. Both disclose in the FILLED block, so the whole chain is visible.

**The characterization itself is asserted, not proposed**, which is worth stating because standing rule 3 sends contributed clinical reasoning to `PROPOSED`. *Controlled* is not a differential or a plan item the clinician can decline — it is the account the note owes for a number this skill generated, and it has to sit in the Assessment to do that job at all. So it goes in the body and discloses in `FILLED·asserted`, which is standing rule 2's mechanism and the one that fits: the thing needing confirmation is a **filled value and what was said about it**, not a recommendation.

**Coherence, not derivation.** The regimen does not set the number and the number does not set the regimen — reason the pressure from the encounter as a whole, in whichever order the note is written. What the rule requires is that the finished note tell one story: `168/104` under `HTN, controlled on lisinopril` is incoherent, and so is `124/78` under `HTN, uncontrolled — start lisinopril`. Neither default is available, because the corpus refuses both — 39 normal against 57 not is close to a coin flip, and a rule tilting every note either way would be wrong at roughly the rate it tilted.

**Where a filled normal pressure is what the Assessment's account rests on, its FILLED line says so** — naming the inferred regimen it leans on, in the shape *A filled BMI near a threshold says how near* uses below:

```
FILLED·asserted   BP 124/78 filled; the Assessment calls the HTN controlled on
                  this value and on the inferred lisinopril, neither measured.
```

The reason is the same as that rule's. Two independent FILLED lines say a pressure was filled and a medication was inferred; **neither says that one is holding the other up**, and that is the part which cannot be reconstructed from the block. The clinician confirming this note is being asked to confirm a characterization of the disease, not just a number.

**A filled vital may raise an obligation and may never discharge one.** Everything above is the additive half of the license — a generated value creates work the note must do, whether by landing abnormal or by landing normal against a documented condition. This is the subtractive half, and it is the one that carries the danger. **Where a plan decision withholds, defers or narrows the workup of a documented finding, it is reasoned from the givens alone.** A filled vital, a filled body measurement and a filled pain score are not there for that purpose. They may trigger an evaluation; they may never satisfy, reassure or defer one.

**Accounting for a filled normal is not discharging anything**, which is worth saying because the paragraph above and this one sit next to each other. `Essential hypertension (I10), controlled on lisinopril` explains why a generated number came out where it did. It does not spend that number on withholding something, and the rule it satisfies is the one immediately above. The two are a pair: a filled normal owes an account, and is owed nothing in return.

**The asymmetry is the one this whole section rests on.** *Nothing in the shorthand constrains which value* is why a vital may be filled at all, and it is equally why a filled vital may not reassure — a value that carries no information cannot carry good news either. A filled *finding* is different and keeps its full force: an unmentioned system is normal because abnormals get charted, so a filled normal exam is evidence about the patient. A filled temperature is evidence about nothing but the rubric.

**And a filled normal is more dangerous than a filled abnormal**, which is why this is stated apart from row 4 rather than folded into it. An invented abnormal draws attention to itself in the Assessment. An invented normal is what makes a workup stop, and it stops it silently. A note that filled `T 98.8 F` and `SpO2 97%` for a patient whose only documented chest finding was `lung sounds diminished` deferred the chest film on those two numbers, and the clinician read the finished note and agreed with it. Two values that existed only because this skill generated them reversed a real imaging decision. Issue #27.

**The pain score's two directions are split between row 4 and row 15, and they do not overlap.** Row 4 owns the additive one: a filled score above 0/10 is answered in the Plan, and 0/10 is the single value that asks for nothing. **A filled 0/10 is therefore not a discharge** — no obligation arose for it to discharge, and *filled content is unremarkable* is already barred from putting it there by default. What row 15 forbids is the score being spent on something else: `abdominal pain 2/10, no imaging` cites a generated number as the reason a documented finding went uninvestigated. That is the same act as deferring a film on a filled saturation, and the score being low is not what makes it different.

**This paragraph is provisional and was not ruled on.** #27 settled that the pain score is inside row 15's class; it never asked what row 15 then does about row 4's one-value normal range, and the collision was resolved by the pass implementing it rather than by the clinician. The live alternative is that a filled 0/10 *is* a discharge, owing the Plan an account the way row 14 makes a filled normal pressure owe one — a run that writes zero into a silent box has chosen a number that makes analgesia unnecessary. `fixtures/day-b` B8 already forbids the zero on the two cases where the complaint is unarguably painful, so what turns on this is case 3, whose own score is open at issue #42. Issue #59.

**So the note orders the thing**, and it is a `FILLED·proposed` line like the swab a documented exposure generates. Ask what the givens alone require — not whether the generated numbers look reassuring — and write that. **The visit not having done it is not by itself a FLAG**; see *FLAG is the block that matters* in step 6. This costs notes that order what the clinician would not have, and that cost is the point: proposed content is reasoning, safe to be wrong about, and the preceptor rules on it. A withheld workup is none of those things.

Height and weight follow the same rule — *the value this patient most plausibly had*, and every constraint on it above — in this order: pick a height plausible for the age and sex, pick a plausible weight, then **derive** the BMI and show the arithmetic. Never pick a BMI and leave the height and weight to be read backwards out of it.

**The OLDCARTS severity is the third member, and it is a pain scale.** The box reads `6/10 facial pressure`, never `not documented` and never a word. (The separator between the element and its value is *Punctuation*'s business, not this rule's — a hyphen on SOAP's one-liner, the template's own colon in H&P's block.) Both arguments above hold of it exactly. A value is required, because severity is one of the rubric's eight HPI boxes. And nothing in the shorthand constrains which value, because a clinician who did not write a number down has said nothing about what the number was — the same asymmetry that makes an absent blood pressure uninformative.

*Filled content is unremarkable* would put the score at 0/10, and that is precisely the collapse this exception exists to prevent. 0/10 is the reading for a patient in no pain — a real answer where the shorthand says so, and a given when it does, but not one to arrive at by default.

**Score it the way a vital is scored: the value this patient most plausibly had.** Anchor it in the complaint, the exam and what was done about it. **The treatment given is the anchor a pressure does not have**, so use it: a run that writes 2/10 for a sinus pressure treated with intramuscular methylprednisolone has described a patient who would not have been given it, and one that writes 9/10 has described a patient who would not have been sent home.

**A filled score is answered in the Plan**, by analgesia or by the treatment of what is causing the pain. This is the same cost the license charges for a filled vital that lands abnormal, and the pain scale's normal range is one value wide — 0/10, and nothing else. It is not optional for the same reason either: a note that invents a 7/10 and offers nothing for it has manufactured the defect this skill exists to catch.

**Two things are givens rather than fills, and reading either one wrong invents a symptom.**

- **A score the shorthand writes is a given.** `c/o 8/10 pain` is 8/10 in the note — unrounded, unreplaced, exactly as a transcribed pressure is.
- **A documented absence of pain is a given too, and it scores 0/10.** `no pain`, or `is in no pain only when she bumps it`, is a charted finding. Filling a number over either is inventing a symptom, and no part of this exception licenses that: it buys a number for a complaint the shorthand documents, never a complaint.

**Where the presenting complaint is not a painful one, the scale still takes a number and names what it scores** — `4/10 itching`. What the eight boxes forbid is a blank; they do not require that every patient hurt. This is the rule carried past the case it was ruled on — issue #30 was raised about a patient in pain — and it is stated rather than left open because *eight, always eight* leaves no third option.

**Every filled vital, every filled measurement and every filled OLDCARTS element is listed in the FILLED block carrying its value, written exactly as it appears in the note body.** Not `blood pressure filled` — `BP 142/88 filled`. Not `aggravating factors filled` — `AGGRAVATING bending forward, lying flat filled`, and `SEVERITY 6/10 facial pressure filled`. Two reasons, and the second is the load-bearing one:

- The clinician confirms a value, not a category, and cannot confirm what the block does not state. **The value is the floor and not the whole line** — *Which value was chosen is the instruction* below is what says the line names the reasoning too.
- The note body is written so given and filled content read identically. **The FILLED block is therefore the only thing in the whole document that can tell them apart**, and [icd10-cpt](../icd10-cpt/SKILL.md) reads it to decide which numbers a code may rest on. It matches on the value. A block naming the field without its value says a pressure was filled but not which one, and the check fails open in silence.

**A derived value with a filled input is listed in the FILLED block too**, naming which inputs were filled — and it stays on the `DERIVED` line as well, with its arithmetic. A BMI is the case that matters: derived is a true statement about it, since the arithmetic has one right answer, but the answer is only ever as real as the height that went in. A BMI appearing under `DERIVED` alone reads as computed from measurements, which is exactly the impression it must not give.

#### Which value was chosen is the instruction, and the note says how it was chosen

*The value this patient most plausibly had* is an instruction about **which number**, and it is the one half of this license nothing was holding a run to. A note is checked for whether the value exists (it does), whether an abnormal one was worked up (it was), and whether the block declares it (it does). **Nothing asks whether the number describes this patient**, and the answer turns out to be no more often than any single note can show.

**Across a set the filled values collapse onto a template.** Two runs of this skill over the same twelve encounters show it, and **the earlier one is committed** — `fixtures/filled-anchor`'s inputs are day-b run 1 byte for byte — so the evidence can be recomputed rather than taken on trust:

```bash
python tools/filled_vitals_census.py fixtures/filled-anchor/notes
```

Nine filled heights over **four distinct values**, four of them `5'10"` — including the 17-year-old's, who got the adult male modal height. Every filled female height `5'4"` or `5'5"`. **Six of the nine filled pressures not normal** — systolic 130 or above, or diastolic 80 or above — against a corpus that splits about evenly at that line. `fixtures/day-b`'s run 2 is the second instance and it is worse: two patients aged 36 and 68 handed an identical `5'10" / 190 lb`, and `138/84` and `138/86` twice each. Issue #67, and that set's own file is where the figures are kept up to date.

**Every one of those values is defensible in its own note**, which is why the rule cannot be *do not write 5'10"*. A 36-year-old man at 5'10" is an ordinary patient. Nine notes each choosing the ordinary patient are a set describing one patient nine times, and the set is the only place it shows.

**So the note discloses the reasoning rather than the number alone.** Every filled vital, body measurement and pain score's `FILLED·asserted` line **names what the value was reasoned from** — and where the encounter supplied nothing to reason from, says that instead:

```
FILLED·asserted   BP 146/84 filled. Reasoned from age 68 with type 2 diabetes and
                  COPD, at rest and in no distress, afebrile and pain 2/10, so no
                  acute driver. Above goal, and worked up in the Plan by recheck.
                  Ht 5'10" (70 in) filled. Plausible adult male height; no habitus
                  or percentile datum in the source to move it.
```

Two reasons, and the second is the one that bites:

- **The clinician confirms a value, and cannot rule on one whose reasoning he cannot see.** This is the same argument that puts the value in the block rather than the field name.
- **An unanchored value has to stay visible, because the note acts on it.** A BMI derived from two unanchored inputs is a number about nobody, and drift row 4 will still make this note work it up. [icd10-cpt](../icd10-cpt/SKILL.md) refuses to code off it for exactly that reason, and it can only do so if the block says which inputs were filled.

**An unanchored value is not a defect. Concealing that it is unanchored is.** Where the encounter genuinely supplies no anchor — and for a height it often supplies none — the ordinary value is the honest choice, and the repetition across a set is that honesty's consequence rather than a fault to engineer away. **Do not manufacture a distinguishing value to break the pattern.** Choosing `6'1"` over `5'10"` for a man nothing describes is not a better-reasoned number, it is an invented finding with a cosmetic motive, and standing rule 2 forbids it in the same words it forbids every other one.

**What the pattern actually shows is anchors going unused, and the pressures are where that is unarguable.** A height is often unanchored. A blood pressure in an encounter with a documented condition, a given pulse, a given temperature, a documented pain score and an exam describing distress is not — the anchors are sitting in the note, and a run that lands the same side of 130/80 six times in nine has stopped reading them.

**Do not move the value to create the disclosure either.** *Do not move the value to avoid making the disclosure* is stated below for the BMI thresholds; this is its mirror and it is the one two runs have failed. **A filled value is not chosen to give the note an abnormal to work up.** The incentive is real and it is this file's own doing: far more is written here about what an abnormal filled value obliges than about what a normal one does, so a run demonstrating its compliance produces something to be compliant about.

**That prohibition is about intent, so here is the test it reduces to: an unanchored value may not land abnormal.** Where the line says the encounter supplied nothing to reason from, the value that patient most plausibly had is the ordinary one — that is what *most plausibly* means when nothing distinguishes the patient. **An abnormal chosen from nothing is an invented abnormal finding**, and it is only the box-demands-a-value argument that got filled vitals their exemption in the first place. That argument buys a number; it does not buy a raised one.

**This is not the bland-normal rule coming back**, and the difference is the whole of the section above. A value with an anchor follows the anchor wherever it goes — a 373 lb patient's pressure, a COPD patient's saturation, a distressed toddler's pulse are all abnormal and all earned. What is forbidden is the abnormal with nothing behind it, which is the shape both runs produced: a pressure just over the line and a line that names no reason for it being there. **So the two halves of the row work together** — the anchor makes the abnormal legitimate, and naming it is what a reader checks.

**The evidence that this is what is happening is that removing the rule changed nothing.** Until 2026-08-11 this section ordered a hypertensive pressure for a documented hypertensive; issue #23 retired it on a corpus count. **The run before that and the run after it both landed both hypertensives above the line** — 148/92 and 146/90 under the old rule, 138/86 and 138/86 under no rule at all — which is `fixtures/day-b` B2's second exit never once being reached in two runs under two different rules. A rule that is gone cannot be what is producing the number.

**A run that sees more than one encounter owes the check across them**, and one does: [batch-shift](../batch-shift/SKILL.md) step 6 rolls the shift's filled values up for the same reason it rolls the FLAGs up — one note cannot see it and the shift can.

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
- **Every social and allergy slot the branch template enumerates** — never blank and never hedged. *Which way a social or allergy slot reads* says which value each takes, and two of them are settled by a count rather than by inference: the allergy slot fills `NKDA` and the tobacco slot fills the negative. Every remaining slot is governed by the paragraph above this list, and it is the whole of their rule — `at work` grounds `Employed` and does not ground `Works manual labor`.
- **Every OLDCARTS element the shorthand does not supply** — aggravating and relieving factors, timing, character — reasoned from the presenting complaint. Bending forward and lying flat aggravate a sinus complaint; asserting that is the same act as the line above it, and the eight elements are mandatory. Severity is the one that is not ordinary filled content: it follows *Filled vitals, body measurements and the pain score*. Onset and duration are usually supplied, and often more than once: reading them is *A duration belongs to what it is written next to*, not this bullet.

**A documented infectious exposure with a congruent presentation orders testing by default.** The contact is a given; testing for what the contact had is standard care for that presentation, and it belongs in the Plan the way return precautions do. Respiratory contact plus respiratory symptoms means **COVID-19 and influenza at minimum**, and **group A streptococcus where the pharynx is involved** — a sore throat, pharyngeal erythema, tonsillar exudate. Name the agent and name the specimen: `COVID-19 and influenza A/B, nasopharyngeal swab`, never `viral testing`.

It is a `FILLED·proposed` line like any other order, generated from the exposure and never from noticing that the encounter omitted it. **The visit not having swabbed is not by itself a FLAG** — see *FLAG is the block that matters* in step 6. A clinician who documents a sick contact and treats empirically has made a call, and a note that flags him for it flags him on every encounter where he made the same one. It stays a FLAG only where the exposure is documented *and* testing would have changed the management the note actually recorded.

**An order is not a result**, which is the paragraph below applied to the order this one generates. A swab sent today has no answer today: no *result* goes in the Objective, and where the encounter itself ran no testing the results line still reads `No new testing today` — that describes what came back, not what was ordered. Ordering COVID-19 testing and then writing `COVID-19 negative` is the invention the whole tier system exists to prevent.

**`No new testing today` is a statement about the encounter, and it is only ever true of one that ordered nothing.** *Ran no testing* means no test was ordered — not that no answer came back, and not that this skill concluded none was indicated. **An encounter whose plan line names a test has run testing**, and its results line says so: the order goes there marked as ordered, with no result attached. Writing the refusal over it is how a given order goes missing, and the whole rule is under *A given order is a given*. Drift row 18. Issue #66.

**And its missing result is not a GAPS entry.** GAPS holds *a swab sent and never returned* — the encounter ran a test and the record lost the answer. A swab this rule orders has no answer to have lost, so it is complete as written, and reporting it as an omission is the *anything the skill was instructed to generate* case in step 6.

**One thing can never be inferred: a result.** Laboratory values, imaging results, and diagnostic test results were either obtained or they were not, and no clinical reasoning yields `estrogen 729`. Where testing is absent — **absent meaning none was ordered, per the paragraph above** — write `No new testing today`. Never produce a number that would read as a result. **Vitals are measurements but they are not results** — a result exists only if testing was ordered and run, while a vital set is required of the encounter record whether anything was ordered or not; see *Filled vitals, body measurements and the pain score*.

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

  **An inferred allergy status behaves the same way, and it is the asserted inference with a forward action leaning on it.** `NKDA` is a claim about the patient's past, so it is asserted; the drug the Plan proposes on it is a forward action. Neither is wrong, and the pair is only safe because the FILLED line names the dependency — see *An inferred allergy status may raise an obligation and may never discharge one*. Drift rows 11 and 17.

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

**Social history** does not blanket-fill with "not reported", and it does not hedge a single slot either. Every slot the template enumerates carries a value; which value comes from *Which way a social or allergy slot reads*.

That rule used to end *"say it where it is genuinely unknown and would matter; otherwise write the inference"*, and the escape hatch is deleted rather than narrowed. **Every slot is genuinely unknown** — that is the premise the whole section starts from — so a clause excusing the hedge wherever the value is unknown excused it everywhere, and *would matter* is what a run decides for itself right before writing `tobacco status not documented this visit`. Nothing is lost: a slot whose value the encounter cannot ground is the unclassifiable case above, and it takes the grounding rule rather than a hedge. Issue #29.

### Punctuation

Three characters that never reach the finished note, given unprompted as absolutes — *"i would never"*, *"i never"*:

| Never | Always |
| --- | --- |
| `·` middot as a separator | `,` comma |
| `—` em dash | `:` colon |
| `→` arrow | `∴` therefore (U+2234) |

So `VS: BP 138/86 · HR 88 · T 98.8 F` is written `VS: BP 138/86, HR 88, T 98.8 F`, and `Ht 5'4", Wt 198 lb → BMI 34.0` is written `Ht 5'4", Wt 198 lb ∴ BMI 34.0`.

**A value pinned to its label takes a hyphen, not the colon** — `Cystitis - N30.00`, `Penicillin - rash`, `Lisinopril - hypertension`. His ruling on the templates, and it is the one place the colon would double up: `Final diagnosis: cystitis: N30.00` puts two colons on one line and reads as a nesting that isn't there. The colon keeps every position where it introduces a clause rather than a value, and the SOAP differential is where both marks land on one line: `Acute bronchitis - J20.9: cough three weeks, clear lungs, afebrile. Favored.` The hyphen pins the code to its diagnosis; the colon opens the rationale.

**About the output, not the input.** The arrow is a token he writes — [GLOSSARY.md](GLOSSARY.md) carries it as *leading to, progressing to* — so it arrives in the shorthand as a given like any other, and this rule governs only what it expands to.

**And the note body only.** The tier block keeps its `FILLED·asserted` middot, the Medatrax field block is unaffected, and prose about the skill — this file, [GLOSSARY.md](GLOSSARY.md), the section notes in both templates — is not the note. An em dash inside a template placeholder that instructs the writer rather than shaping the output is prose too: `<… duration — one per line>` stays, because a colon there would read as a field whose value is *one per line*.

It binds both branches, which is why it lives here rather than in either template. Both were swept when it was added: [SOAP.md](SOAP.md) did not merely permit the arrow, it **specified** it — `Ht, Wt → BMI`. A convention that contradicts the template it governs loses. Issue #31.

### Spelling

**American English, always** — [standing rule 4](../../AGENTS.md), so it binds every skill here and not only this one. His ruling, and it is unconditional. These are notes for an American program, read by American faculty, and a British spelling reads as a note written by somebody else. This section is the table the rule points at.

| Never | Always |
| --- | --- |
| `dyspnoea`, `apnoea`, `anaemia`, `haemoglobin`, `oedema`, `diarrhoea`, `paediatric` | `dyspnea`, `apnea`, `anemia`, `hemoglobin`, `edema`, `diarrhea`, `pediatric` |
| `caesarean` | `cesarean` |
| `sulphate`, `nebuliser`, `catheterise` | `sulfate`, `nebulizer`, `catheterize` |
| `millilitre`, `centimetre`, `litre`, `fibre` | `milliliter`, `centimeter`, `liter`, `fiber` |
| `grey`, `behaviour`, `colour`, `tumour` | `gray`, `behavior`, `color`, `tumor` |
| `labelled`, `recognisable`, `programme`, `licence` | `labeled`, `recognizable`, `program`, `license` |

**Drug names take the United States generic**, which is the same rule where it costs the most to get wrong: `acetaminophen` not `paracetamol`, `epinephrine` not `adrenaline`, `albuterol` not `salbutamol`, `ferrous sulfate` not `ferrous sulphate`. A clinician reading the other name has to translate it before they can check the dose.

**Wider scope than the punctuation rule above, and the difference is why this one is a standing rule and that one is not.** Punctuation governs the note body only, and it lives here because it governs *this skill's* two branches. Spelling reaches the tier blocks, the Medatrax fields, the filenames, the commit messages and the prose about the skills — which is more than a skill file can bind, so it is stated in [AGENTS.md](../../AGENTS.md) and only tabulated here.

**About the output, not the input.** A British spelling arriving in the shorthand is normalized on the way out like any other spelling variant — the same treatment [GLOSSARY.md](GLOSSARY.md) gives `cetrazine`. It is not a hedge and it is not a number, so nothing in *Given* protects it.

**Thirteen of the forms above were written by this repo**, and that is why the rule is here rather than assumed. Five came from [GLOSSARY.md](GLOSSARY.md)'s own expansion tables — `nebuliser`, `sulphate`, `millilitres`, `centimetres`, `caesarean` — which is where a wrong spelling does the most damage, because the skill copies an expansion into a note by design. Seven more came from a `clinical-note` run — `dyspnoea`, `fibre`, `grey`, `behaviour`, `labelled`, `recognisable`, `programme` — appearing **20 times across six of the twelve** notes in `fixtures/filled-anchor/notes/`, which also repeats `caesarean`. The thirteenth is `licence`, in `fixtures/peds-bp/assertions.md`. All were corrected 2026-08-12 **except the run's**, which are preserved because that set is a byte-for-byte record of what a run produced and correcting it would falsify the evidence. Issue #73.

**That run wrote both spellings of most of them**, which is what makes the record evidence of drift rather than of a register: `cesarean` eight times against `caesarean` twice, `dyspnea` seven against `dyspnoea` three, `program` nine against `programme` twice, `fiber` three against `fibre` four. **Nobody reading one note would see it** — the same shape as [#67](https://github.com/mshamblin5150-code/clinical-skills/issues/67), and the same reason twelve outputs had to be put in front of one reader.

**A fourteenth instance — of a form already on that list — was in a skill file, and the hand sweep that wrote this section missed it.** `batch-shift` used `programme` in prose about the clinician's program, and what found it was `python tools/spelling_scan.py --all` — this table with a command in front of it, which is the ordinary way to check now:

```bash
python tools/spelling_scan.py --all      # every tracked .md
python tools/spelling_scan.py --record   # the preserved run record, form by form
```

It reads Markdown only, and it holds this table rather than the language: a clean scan means no *listed* form was used. `tools/test_spelling_scan.py` parses the table above and asserts the scanner covers every row of it, so the two cannot drift apart. **The rule is complete without the command** — this table is the instruction, and skipping the scan costs a check rather than an answer.

**The rule has been exercised, and until 2026-08-12 it had not been.** A rule written after the run that motivated it is a rule nothing has walked, so day-b's twelve encounters were re-run that day on `ffe9377` — twelve generating passes, shorthand pasted inline, `fixtures/` closed — and graded by `python tools/spelling_scan.py` over the output rather than by a reader. **None of the eight forms appears in 4,275 lines.** A wider hand net — the `-ise` family, the `oe` and `ae` digraphs, `-our`, `-re`, `-ence`, 46 stems in all — came back empty too.

**Six of the eight were reached in their American spelling and two were not**, which is the part a bare pass would hide: `program` 12 times, `dyspnea` 8, `gray` 4, `cesarean` 4, `behavior` and `behavioral` 3 between them, `labeled` once — while `fiber` and `recognizable` appear **nowhere in the run**, so those two forms were never put under load. `programme`'s slot is the sharper case: the Medatrax `Course` row is filled in all twelve and not one of them phrases it the way the run that wrote `programme` did. **A form the run had no occasion to write has not been tested**, and a run reporting it as a pass is flattering itself — [fixtures/README](../../fixtures/README.md)'s point about a vacuous row, arriving here.

**Those figures are not recomputable from this repo**, and that is worth stating rather than leaving to be discovered: the run's twelve notes are patient records and are gitignored, so a reader with only this checkout has this paragraph and nothing to check it against. The command is `python tools/spelling_scan.py <the run directory>`, and the standing answer is the one [fixtures/README](../../fixtures/README.md) gives — **run it again.** What *is* committed is the record of the run that failed, in `fixtures/filled-anchor/notes/`, and `--record` recomputes every figure about that one.

The remaining rows are the same families, listed to be caught before they are written rather than after. **A form inside backticks is a mention and is not reported** — which is how the scanner tells naming a spelling from using one, and why every wrong spelling on this page is written in a code span. `tools/corpus_census.py` writes `apnoea` in a comment explaining that the spelling is *not* matched, and is left alone on the same rule.

### Times

Ask up front, once per day file, and reuse for every encounter in it:

- **What time did the day start?** Note 1 is the first patient; each subsequent note follows in order.
- **How long was the shift?** Clinical days often run twelve hours.

Then assign each visit **15 to 40 minutes, in 5-minute steps**, by complexity — a brief recheck or simple sprain at 15–20, a routine acute visit at 25–30, a multi-problem or procedural visit at 35–40. Space the encounters across the shift rather than stacking them back to back, and report every start and end as estimated.

## Steps

### 1. Intake and de-identify

Collect the shorthand and, if supplied, the Medatrax entry — it carries demographics and some vitals, and those are **givens** the note must match exactly.

**Derive the age before you redact the date of birth.** A date of birth in place of an age is not an edge case: it is the dominant form in whole day files, and this catalog holds day files in which **not one encounter states an age** — `tools/corpus_census.py` counts them. Redacting `[DOB]` on the way past destroys the only thing age can be computed from, and age sets the `Patient Time` band. So: compute the age from the date of birth and the visit date, write it down as a derived value showing the arithmetic, and redact afterwards.

**No share is quoted here on purpose.** The catalog is two halves whose mixes differ sharply, so a corpus-wide percentage describes neither of them and decays as the corpus grows. [batch-shift](../batch-shift/SKILL.md) step 3 owns the demographic-shape table and says what to do instead. The rule above holds at any share, which is why it never needed one.

**Read the unmarked form.** The newer shorthand runs age and sex together with no marker at all — `51 f`, `48f`, `35 f` — and it is the dominant form in the recent files. Anything scanning for `yo`, `y/o` or `dob` misses it and reports a recent encounter as ageless.

Then replace identifiers as you read: `[PT]` for name, `[DOB]`, `[MRN]`, `[SITE]`, `[PRECEPTOR]`. Keep age, sex, visit date, and everything clinical.

**About 7% of encounters carry neither an age nor a date of birth** — roughly one in fourteen, measured 2026-08-11 across 551 notes, of which 513 carry one or the other. Not a freak case, and not a stop: see *What may be inferred* for how the age is inferred and flagged.

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

**A decision not to do something the encounter did is not a forward action**, and `FILLED·proposed` is not where it goes — nowhere is. Declining to order a test the clinician did not order is ordinary reasoning and belongs here; declining one he **did** order is *A given order is a given*, and the order stays in the Plan whatever this block says about it.

A value can occupy two lines at once, and one routinely does: a BMI derived from a filled height is written under `DERIVED` with its arithmetic *and* under `FILLED·asserted` naming the filled input. Listing it only as derived hides that it was invented; listing it only as filled hides that it was computed.

**The block travels with the note.** [icd10-cpt](../icd10-cpt/SKILL.md) takes the note body *and* this block, because the body alone cannot say which of its numbers were measured — that is the whole point of writing filled content so it reads like the rest. Never hand a note to the coder with the tier block stripped. Where codes are produced mid-draft, as [SOAP.md](SOAP.md) and [HP.md](HP.md) both do, the step 4 tier assignment is what the coder needs; the block is that assignment's written form, not its only form.

**FLAG is the block that matters.** A flag is a finding that was documented and then abandoned — an abnormal that reached the Objective and stopped there, a vital nobody addressed, a second problem the Assessment never names. It is neither a gap (nothing is missing from the source) nor a filled line (nothing was generated). It is the note failing to act on what it was told, which is the defect this skill exists to catch.

One FLAG per finding. Name the finding and name what was not done with it — `BP 151/93 undiscussed`, not `vitals not addressed`.

**A default this skill generates is not an abandonment, and does not go here.** Testing from a documented exposure is the case — the visit not having swabbed is not by itself a flag. It is written as the order under `FILLED·proposed`, and the FLAG block says nothing. This is the GAPS list's *anything the skill was instructed to generate*, one block up: the two are told apart by what would fix them, and an abandoned finding is fixed by the clinician going back and addressing it where a missing default is fixed by this note carrying it. Flagging the second turns a routine standing order into a recurring accusation, and a block full of those is a block nobody reads — which costs the abandoned finding sitting next to them.

**The one exception is stated where the rule is**, under *What may be inferred*: a documented exposure stays a FLAG where testing would have changed the management the note actually recorded. That is a defect in the encounter and not a default the skill supplied, so it belongs here. The order is written either way.

**An order written because a filled value was refused the reassurance behaves identically.** Where the givens alone require a workup the visit did not do — a chest film for documented diminished breath sounds — the order goes under `FILLED·proposed` and this block stays silent. A clinician who treated empirically made a call, exactly as the one who documented an exposure and did not swab did, and flagging him for it flags him on every encounter where he made the same call. The same exception applies unchanged: it is a FLAG where the workup would have changed the management the note actually recorded — which is a question about the *encounter*, and an encounter that already treated the thing empirically has usually answered it. A film for diminished breath sounds in a patient sent home on amoxicillin-clavulanate is ordered and not flagged. See *A filled vital may raise an obligation and may never discharge one*.

**What never goes under GAPS:**

- **Start and end times.** Estimated by design, and they say so where they appear. Estimated is a property of the value, not the absence of one.
- **Vitals and body measurements.** Filled by design to the value the patient most plausibly had, and declared in FILLED.
- **Any of the eight OLDCARTS elements.** All eight are mandatory and all eight are filled where the shorthand is silent. `Aggravating - not documented` is the same defect written into the note body instead, and it fails the branch template rather than earning a GAPS line.
- **Age.** Inferred by design where the shorthand and the entry both lack it, and flagged at the top of `FILLED·asserted`.
- **Any social or allergy slot the branch template enumerates.** All of them are filled where the shorthand is silent, and `Allergies (reaction) - not supplied` is the same defect written into the note body instead. It fails the branch template and drift row 17 rather than earning a GAPS line, exactly as an OLDCARTS element does one bullet up.
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
| 13 | **Differential** | Every differential entry carries an ICD-10-CM code, and **no diagnosis the encounter did not establish** — differential entry, favored entry or final — carries a code whose descriptor names a confirmed organism or disease |
| 14 | **Control** | A **filled** value that is a documented condition's own diagnostic measure and lands **normal** is accounted for **in the Assessment**. Hypertension: called *controlled*, *treated*, *on therapy*, or with the medication named. Obesity: called resolved, improved or post-surgical, or with the weight-loss intervention named. A code in a pre-existing or problem list is not an account, and neither is a monitoring instruction. A **given** value never fails this row, and neither does a filled abnormal — row 4 already holds that one |
| 15 | **Filled reassurance** | Every reassurance in the note traces to a given. No decision to withhold, defer or narrow the workup of a documented finding rests on a filled vital, body measurement or pain score, and any cause a filled abnormal is attributed to is a **given finding**. A filled 0/10 is not a discharge — row 4 owns that direction. **And a test the encounter itself ordered is not a workup this note withheld**: removing a given order and then citing its absence here is row 18's defect being scored as this row's pass |
| 16 | **Duration** | Every stated duration reaches the HPI attached to the symptoms it was written beside, written `<duration> for <symptoms>`. None is dropped, and none is applied to a symptom the shorthand did not attach it to. Two durations for the **same** symptom are written as a span containing both, never one endpoint chosen over the other and never a FLAG. **Both a span and an attribution that rested on resolving a pronoun are declared in `FILLED·asserted` carrying their value**; an attribution whose onset line named its own symptom is not |
| 17 | **Inferred history** | Every social and allergy slot the branch template enumerates carries a value, **none of them a hedge** — no `not documented`, `not reported this visit` or `status unknown`. No **positive** tobacco or vaping status is filled. A slot the corpus cannot classify is **grounded in the shorthand**, not invented beside it. Every filled slot is declared in `FILLED·asserted` carrying its value, and where a **proposed drug** rests on an inferred allergy status, that line names the dependency. A **given** status never fails this row |
| 18 | **Orders** | Every order the shorthand records — a test, an imaging study, a referral, a drug, an immunization — appears in the finished note as an order. **Checked by counting, the way rows 2 and 16 are:** list every order token in step 2's expansion, wherever it was written, then name where each one landed. **And no sentence anywhere in the note says a given order was not placed** — that limb is checked separately, because retaining the order does not make the denial true. An objection to a given order is written beside the retained order as a recommendation, never in its place and never as a `FILLED·proposed` line |
| 19 | **Choice** | Every filled vital, body measurement and pain score's `FILLED·asserted` line names what the value was **reasoned from** — or states that the encounter supplied no anchor for it. No value is chosen to give the note an abnormal to work up, and none is moved to avoid a disclosure. A **given** value never fails this row, and neither does an unanchored one that says it is unanchored |

**Row 14 is appended rather than slotted beside row 4**, which is where it belongs by subject. Rows 1 through 13 are cited by number across this file, three fixture sets and [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md), so renumbering to put it in its natural place would silently redirect every one of those citations. Its subject is row 4's, its number is not, and that is a deliberate cost.

**It was written as row 13 and became row 14 on merge**, because issue #19's Differential row was appended on another branch at the same time. That is the cost of append-only landing on two branches at once, and it is cheaper than the alternative: had either row been *inserted* where it belonged by subject, the collision would have silently renumbered the other's citations instead of announcing itself as a conflict.

**It is the only row whose failure is made of silence.** Every other row can be failed by something written down wrongly; this one is failed by a note that reads perfectly and simply never accounts for a number the skill invented. That is why it is a row at all rather than a line in the vitals section — §7 requires a verdict per row *by name*, and a rule that is not a row never gets walked.

**It applies to two measures today and is written for more.** Blood pressure against hypertension and BMI against obesity are fixtured, in `fixtures/day-b` B2 and `fixtures/obesity-bmi` O2 respectively. A third would qualify on the same test the vitals section states: the value has to *be* what the condition is diagnosed by. Most vitals are not, for most conditions, and this row is not an invitation to explain every normal number in the note.

**Row 15 is appended for row 14's reason and became 15 the same way**, on a third branch landing at the same time — it was written as row 13 for issue #27 before either of the two above existed. Its subject is row 4's and row 14's; its number is neither's neighbor. The convention holds: **append, never insert**, because inserting silently redirects every citation by number in this file, the fixture sets and the ADR, where appending only ever costs a merge conflict that announces itself.

**Rows 14 and 15 are the two halves of what a filled normal owes and is owed.** Row 14 says a filled normal against its own condition must be accounted for. Row 15 says a filled normal may never be spent — it buys no deferral, no narrowing and no withheld test. A note can satisfy one and fail the other, which is why they are two rows: `HTN, controlled on lisinopril` accounts for a generated 124/78 and passes row 14, and the same note can go on to defer a workup on that same number and fail row 15.

**Row 16 is appended for the same reason as 14 and 15, and its natural neighbor is row 11.** It is a rule about two givens disagreeing, which is row 11's subject, and it sits at the bottom instead. The convention holds: **append, never insert** — inserting silently redirects every citation by number in this file, the fixture sets and the ADR, where appending only ever costs a merge conflict that announces itself.

**But it is not row 11 widened, and the two rows demand opposite things.** Row 11 says a conflict between givens is *named*; row 16 says one particular conflict is *resolved*. Both are right, because a span exists for durations and does not exist for a drug against a condition — the argument is in *A duration belongs to what it is written next to*. A run that names a duration conflict instead of spanning it has not satisfied row 11 by proxy; it has failed row 16.

**It is checked by counting, the way row 2 is.** Take each duration in step 2's expansion — every `x N days`, every `started yesterday`, every dated onset — and name the symptom it landed on in the finished HPI. A duration that landed on nothing was dropped; a duration that landed on a symptom the shorthand never attached it to was moved. Both fail, and both read perfectly well, which is why this is a count rather than an impression.

**Its quiet failure is the folded timeline.** A note that reads a multi-symptom complaint, takes the chief complaint's number as the illness's duration and never notices the second onset statement produces a fluent, internally consistent HPI with one timeline in it. Nothing in the note points at the missing one. The count is what finds it.

**Row 17 was written as row 16 and became 17 on merge, which is the third time this has happened here.** Rows 14, 15 and now 17 were all appended on branches in flight against each other, and the paragraphs above record the first two. **That is the convention working, not failing.** Issue #33's Duration row reached `main` first and owns 16; this one moved. Had either been *inserted* at its natural neighbor — 16's is row 11, 17's is row 4 — the collision would have silently redirected the other's citations instead of announcing itself as a conflict on one line of a table.

**Row 17 is the first row whose prohibitions were already in the file.** Row 12 has banned `Allergies (reaction): Not documented this visit.` since issue #28 — a sentence that defends the note rather than reporting on the patient, which is exactly the test row 12 carries. Row 1 has banned `smokes 0.5 PPD` for longer than that, since a tobacco history is an abnormal finding and an abnormal finding must trace to a given. **Neither was ever applied to a social slot**, and two committed fixture rows spent months rewarding the hedge row 12 forbids.

**That is the argument for the row rather than against it.** Row 14 states it about itself: §7 requires a verdict for each row **by name**, so a rule that is not a row never gets walked. Rows 1 and 12 are walked as questions about findings and about leakage, and a run answering them honestly still never looks at the `SH:` line. Row 17 is where it looks.

**It also carries two things neither of those rows contains.** The grounding bar on the slots the corpus cannot classify is nowhere in rows 1 or 12 — `Works manual labor` is not an abnormal finding and not a sentence about this skill's process, it is simply a fact about a patient that nothing supplied. And the allergy dependency is row 15's subject reaching a value outside row 15's class, which is why it is stated here rather than by widening that row and redirecting its citations.

**Check it by reading the branch template's slot list against the note, then the note against the block.** Count the enumerated slots, count the ones carrying a value, and count the ones the FILLED block declares with a value. Then take each slot the shorthand did not supply and name what grounded it. `Non-smoker` is grounded in the count; `Employed` is grounded in `at work`; `Works manual labor` is grounded in nothing and fails. Issue #29.

**Row 18 is appended for the reason rows 14 through 17 were**, and this time nothing was in flight against it — the convention holds anyway, because it is the numbering that has to be stable rather than the merge that has to be busy. **Append, never insert.** Its natural neighbors are rows 2 and 11, and it sits at the bottom instead.

**It is the second row whose prohibition was already in the file**, which is row 17's argument arriving at a different sentence. *Present in the shorthand or the Medatrax entry. Passes through unchanged* is the **first thing the tier system says**, and it has said it since before any of these rows existed. Row 11 has forbidden dropping a given medication for as long as it has existed. **Neither was ever applied to an order**, because rows are walked as the questions they are named for: row 2 asks what happened to a documented *abnormal*, row 11 asks whether a *conflict* was named, and a run answering both honestly never looks at the plan line as a list of things that were done. Row 18 is where it looks.

**It is not row 11 widened, and merging them would lose row 11.** Row 11's subject is two givens that cannot both be acted on, and its instruction is to **name** the clash. Row 18's subject is one given that was acted on, and its instruction is to **carry** it. A note can name every conflict it finds and still have quietly deleted the order it disagreed with — that is the observed failure, and it reads as a pass on row 11 because the deleted order is no longer there to conflict with anything.

**It is checked by counting, and what is counted is order tokens rather than abnormals.** Take step 2's expansion and list every order in it — `covid`, `strep`, `flu`, `ua`, `micro urine`, `urine c/s`, `spot mono` is seven tokens, not six — then name where each one landed in the finished note. An order that landed nowhere was dropped.

**Count the tokens the shorthand wrote, not the studies you think they name.** `ua` and `micro urine` may be one specimen or two requisitions, and nothing in the shorthand settles it; a count that has to decide first is not binary. So each token must land somewhere, and a note writing `urinalysis with microscopic` for both has landed both. This keeps the row a comparison of two integers, which is what rows 2 and 16 rely on and what makes a dropped order impossible to argue about.

**The plan line is where most orders are, not where all of them are.** *Given* is anything present in the shorthand **or the Medatrax entry**, so an order written into the exam prose, carried over from a prior visit as still pending, or sitting in the entry counts and gets walked. A row scoped to the token after `plan` would miss the order that was mentioned in passing, which is the one most easily lost.

**The second limb is not found by counting, and that is why it is stated apart.** An order that landed as a sentence saying it was not done has been **reversed**, and reversal does not show up as a missing string — it shows up as an extra one. Read the Assessment and the Plan for any claim that a given order was not placed, and the count will not find it for you: the note can carry the order *and* the denial, pass the count, and still tell the reader who is graded on the Assessment that the test was declined.

**Its quiet failure is a paragraph of good clinical reasoning.** A note that argues mononucleosis is unlikely on a short course, prominent coryza and no posterior cervical adenopathy, and concludes that no monospot is indicated, is fluent, correct on the medicine, and describing a different visit than the one that happened. Nothing inside it points at the order it replaced — the count is what finds it, and the count is why this is a row. Issue #66.

**Row 19 is the first row a single note cannot fail loudly.** Rows 1 through 18 each resolve inside the document they are walked against: a finding is in the Assessment or it is not, an order landed somewhere or it did not. Row 19's subject is a value that is individually defensible and collectively a template — `5'10"` for a 36-year-old man is an ordinary patient, and four of them are one patient written four times. **So the row does not ask whether the number is right.** It asks whether the line says how the number was arrived at, which is a question one note can answer, and it leaves the cross-note half to [batch-shift](../batch-shift/SKILL.md) step 6 and to `fixtures/day-b` B13.

**Its two prohibitions are one prohibition seen from both sides.** *Do not move the value to avoid making the disclosure* was already written under *A filled BMI near a threshold says how near*, and it was written about one direction because that was the direction someone had thought of. The direction two runs actually failed is the other one: six of nine filled pressures landing not-normal, a rate the corpus refuses, in a file whose abnormal-value machinery is many times longer than its normal-value machinery. **A run demonstrating compliance produces something to be compliant about**, and issue #23 retiring the rule that used to order the abnormal changed the count not at all.

**Check it by reading the FILLED block alone, one line per generated value.** Take each filled vital, measurement and severity and ask what in the encounter the line names — a documented condition, a given pulse or temperature, the exam's description of distress, the treatment given, age and sex. A line naming nothing fails unless it says so in those words. **A line saying `no habitus or percentile datum in the source to move it` passes**, and that is the point of the row rather than a loophole in it: the unanchored value is honest and the concealed one is not. Issue #67.

**Row 12 is checked by reading the body without the block.** Every other row asks whether the note said enough; this one asks whether it said something only the tier block may say. The two failing shapes are a parenthetical that labels its own line — `(inferred)`, `(dose given; duration filled)` — and a sentence that accounts for the note's own content, such as what was not reconciled or what must be confirmed before entry. Both read as diligence, which is why they survive a reading that is looking for omissions.

**A word search is the wrong instrument here** and will produce false hits on any note written well. *The tier language stays out of the note* carries a test for each half: ask of every occurrence of the six words whether it would still be there had the shorthand supplied every line, and ask of every candidate sentence whether it reports something about the patient or defends the note. Record which way each one resolved.

**Row 13 fires on every note, which is what makes it easy to stop reading.** A differential is generated in 100% of encounters and a hedge token appears in the shorthand of far fewer — issue #19 measured about 6% on 2026-08-11 across 559. Treat that as a **proxy rather than a bound**: it over-counts, because some of those tokens hedge a history rather than a diagnosis, and it under-counts, because the shorthand hedges in ways the token list does not reach. `tools/corpus_census.py` recomputes it, and **it has not been run against the corpus since it gained the ability to** — re-run before leaning on the number. What the ratio establishes is only its direction: the first half of this row is checked far more often than the second, and a row that passes twenty times running is a row that starts getting a verdict without being walked. Count the entries and count the codes; they are two numbers and they either match or they do not.

**Its second half needs the descriptor read, not the diagnosis.** `probable viral URI` coded `J06.9 Acute upper respiratory infection, unspecified` passes — the descriptor says *unspecified* and asserts nothing the note lacks. The same hedge coded `U07.1 COVID-19` fails, because that descriptor names the organism and the note says nobody swabbed. The failing shape is narrow and it is always the same one: an organism-specific or disease-specific descriptor on a diagnosis the encounter never established.

**And it does not stop at the entries the note rejects.** `probable viral URI` is usually the note's *conclusion*, not something argued against, and it is the case this rule was written for — so the row reaches the favored entry and the final diagnosis on exactly the same terms. A row scoped to the rejected entries alone would pass the headline example. The rule itself, and what to propose instead, live in [icd10-cpt](../icd10-cpt/SKILL.md). Issue #19.

**Row 15 is row 1 read in a mirror, and it is checked by asking what the note declined to do.** Row 1 exempts filled vitals from tracing to a given, because they have to be allowed to exist. Row 15 refuses them that exemption, because they must not be allowed to reassure. Every other row reads what the note contains; this one reads what it decided against. Take each plan decision that withholds, defers or narrows the workup of a documented finding — no imaging, no culture, no referral, watchful waiting — and name what it rests on. Anything resting on a generated number fails. **An obligation that never arose is not a discharge**, which is where a filled 0/10 sits; see the paragraph splitting row 4's direction from this one.

**It survives a careful reading, which is why it needs a row.** A note that declines a test on a plausible normal is fluent, internally consistent and clinically persuasive; there is nothing in it to notice. The FILLED block carrying both numbers is not enough on its own, because the block is read once before submission and the body is what gets reasoned from — on issue #27 it was the clinician himself who was persuaded.

**Walk it only over tests the encounter did not order, and check that scope before walking.** A run that deleted a given order and then answered this row about it will pass — it lists what its refusal rested on, finds only given findings there, and records a pass, which is exactly what happened on the run row 18 was written from. **The absence it is reasoning about is its own.** So take the plan line first, per row 18, and any test on it is outside this row's subject however well the note argues against it.

**Row 8 is worth a second look even when the age is given.** The clinician's own record puts an 82-year-old on `Adult`, and misses the gyn/obstetric override on every opportunity it has had. A stated age is not the same as a correct band.

Row 2 carries the most weight and is the easiest to skip, because a drifting note reads perfectly well. Take each abnormal from step 2's expansion in turn and name where it lands. An abnormal that lands nowhere is either a diagnosis missing from the Assessment or a problem missing from the Plan — say which.

A failing row is written as a **FLAG** in the tier block, never quietly repaired into a pass. That is what FLAG is for — the matrix finds the defect, FLAG is where it is recorded.

Close with `N given, N derived, N filled` and stop.
