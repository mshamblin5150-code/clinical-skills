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

This limb is fixtured as `fixtures/duration-span`, which scores whether the duration element carries both stated values. **The cases are deliberately not described here**, and neither is which of them is the control: [fixtures/README](../../fixtures/README.md) requires a set's inputs be withheld from a generating pass and pasted in rather than pointed at, and this file is the one a generating pass always reads.

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

**The templates enumerate these slots, so each one is a box.** [SOAP.md](SOAP.md) writes `SH: <occupation; education; marital; tobacco; alcohol; drugs; spiritual; environmental; nutrition; fitness; sleep — one clause each>` and `Allergies (reaction): <allergen - reaction; drug status first, NKDA if none; then environmental and food, each named by its kind>`; [HP.md](HP.md) lists twelve social lines *"one line each, in that order"*. So the two-part test that licenses a filled vital holds of every one of them — a box demands a value, and the shorthand constrains none.

**No slot ever reads `not documented`, and that was never new law.** `Allergies (reaction): Not documented this visit.` reports nothing about the patient: strike the inference above it and the sentence has nothing left to do. It is `No medication reconciliation was performed this visit` with the nouns changed — the sentence issue #28 banned, and **drift row 12 has forbidden it since.** The same goes for `tobacco status not documented`, `alcohol not documented`, `status unknown` and `not reported this visit`. What row 12's test permits is a claim about the patient: `Non-smoker`, `no smoke exposure reported`, `No chronic illness reported` all report, and all stay. Issue #29.

**Which value the box takes depends on which reading its slot has, and the corpus decides that per slot.** *Silence is undocumented, never absent* reads two ways, and asking which way a slot goes is asking a question about this clinician's transcription rather than about clinical practice in general:

- **A slot he writes even when the answer is nothing** is a habitual template field. Silence in it is a transcription gap, so the note fills the **unremarkable** value — and that value is not a bland pick from the middle, it is what the record says such patients mostly are.
- **A slot he writes only when there is something in it** is charted the way an abnormal is. Silence in it is a real **absence**, so the note fills the **negative** — and filling a positive would be inventing an abnormal finding, which standing rule 2 forbids outright.

**Two slots are measured and they land opposite ways.** The figures below are over **the corpus — 551 encounters**, re-derived 2026-08-16 by `python tools/corpus_census.py`. `tools/test_corpus_census.py` pins the committed-fixture classification case by case, so a fixture edit fails a test rather than quietly voiding the rule:

| Slot | Written | Says the unremarkable thing | So silence is | Filled value |
| --- | --- | --- | --- | --- |
| Allergies | 284 of 551 | **no drug allergen, 195 of 284 — 69%** | a gap | `NKDA` |
| Tobacco | 197 of 551 | denied, 25 of 197 — 13% | an absence | `Non-smoker` |

**The allergy row counts *no drug allergen* and not *says nothing*, and that distinction is the whole of issue #78.** `NKDA` is *no known **drug** allergy*, so a patient with hay fever is NKDA and a note naming a seasonal allergy is no evidence against filling it. Counted undivided the corpus says only 111 of 284 written statuses say nothing — 39%, a minority, and the reverse of the fixture floor. That was #78's own trigger for reopening the ruling, and it fired on a column measuring the wrong thing: three of the five fixture cases in it name nothing but a seasonal allergy. **Split on the kind `NKDA` is a claim about, the two slots land as far apart as they ever did — 69% against 13%** — and the clinician confirmed the reading on 2026-08-16: *silence about drug allergies takes `NKDA`; seasonal allergies fall under environmental, which is a separate category, as is food.*

**The corpus corroborates that reading directly rather than only permitting it.** 18 of the 111 encounters writing a denial name an allergen anyway, and **17 of the 18 name an environmental one** — this clinician writes the drug-allergy denial beside a seasonal allergy seventeen times, in the same slot, himself.

**69% is a floor, and the worst case is published rather than promised.** Three errors bear on it and their directions are measured, not assumed. The drug column is a token list matched near an allergy mention and cannot tell an allergen from a medication written beside it, so it over-counts drugs. 16 of the 173 name something the lists do not carry and are reported as `unclassified` rather than assigned; charge **every** one of them as a drug allergy and the share falls only to 63%. Running the other way — the one shape that could hide a real drug allergy on the *no drug* side — is a denial that names a drug anyway, and there is **exactly one** in 551 encounters. The ruling does not turn on the estimate being tight.

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

The reason is that rule's reason. Two independent FILLED lines say an allergy status was inferred and a drug was proposed; **neither says the second is standing on the first.** Eighty-nine of the 284 written statuses in the corpus name a drug allergy, so `NKDA` is usually right — and *usually* is exactly what a prescribing decision may not rest on silently. **That is roughly one written status in three, which is a good deal less comfortable than the figure this sentence used to quote** — *one of the sixteen written statuses in the fixtures*, which was an undercount of the fixtures as well as the wrong population to quote. Corrected 2026-08-16 on #78; the fixture figure and which case moved it are recorded in `fixtures/day-b/assertions.md`, which is withheld from a generating pass and is where an input belongs.

**A given allergy status is never overwritten, and a stated allergen is never dropped.** `allergic to prednisone` is a given like any other, and it behaves like the conflict rule below: a drug proposed against a documented allergy is called out, and no inferred status dissolves it.

**Never dropped means never moved out of the box either, and the box names which kind each allergen is.** Ruled by the clinician 2026-08-16, issue [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96). The box states the drug status first and then names any environmental or food allergen after it, each named by its kind:

```
Allergies (reaction): NKDA for drug allergies. Seasonal environmental allergies -
itching and sneezing. Lactose intolerance, a food intolerance rather than an allergy.
```

**The kind is carried in the allergen's own wording rather than as a sub-heading, and that is *Punctuation*'s doing rather than a style preference.** `Environmental: seasonal allergies` pins a value to a label with a colon, which is the `Penicillin - rash` shape that section rules on — **and that section names this box as its example.** The box has already spent its one colon on its own label, so a second is the doubling-up the rule exists to stop. `seasonal environmental allergies` says which kind without spending anything, and it is what day-b run 3's case 11 wrote unprompted.

**The reaction on that line is grounded, not invented, and #29 is why it is shown.** Itching and sneezing are what seasonal allergies do, so they are read off the given rather than added beside it — `fixtures/day-b/assertions.md` records that ruling and records a run being wrongly marked down for obeying it. **An example writing the allergen bare would model the opposite**, which is a position #96 has no business taking on the way past.

**Both halves are required and each one alone has been written.** A bare `NKDA` with the seasonal allergy routed to `PMH/PSH` fails — `fixtures/day-b` case 2 under run 3 and `fixtures/day-a` case 6 under run 2 both did that, independently, on two sets. And a box naming the seasonal allergy with no drug statement fails too, which is what the placement reading below would have produced for `fixtures/hedged-dx` case 3. The drug status is owed whether or not a drug allergen was named, because `NKDA` is the only thing in the note that answers *may this patient have the drug the Plan is proposing*.

**Where the clinician typed the words does not decide it.** #96 tested placement as the discriminator — words under an `allergies:` label to the box, words inside an `hx:` list to `PMH` — and it does not survive its own count: the committed inputs naming an allergen split **evenly**, so placement decides half a set and nothing more. **The count itself is stated once, in `fixtures/day-b/assertions.md` under R6 and R7, and is deliberately not written here** — it has moved four times as fixture sets landed, and it is re-derived there by `tools/test_allergy_slot.py` rather than typed. The corpus argues against placement directly as well, in the paragraph four above this one: the clinician writes the drug denial beside an environmental allergen in **that same slot**, so he puts both in one box himself regardless of any label. **The kind decides, not the label** — and a rule keyed to where a word landed in shorthand would put the same clinical fact in different sections of two notes.

**Neither figure is restated in this paragraph, and the first draft of it restated both** — in the clause claiming it had not. Caught by review on this ticket's own branch, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape committed by a sentence written to avoid it.

**A food intolerance is carried, and the word `intolerance` on the line is what makes it safe to carry.** `lactose intolerance` is an enzyme deficiency and not an immune reaction, so it is not an allergy at all — and it belongs in the box because lactose is an excipient in many oral drugs and the box is the list of what not to give this patient. Naming it without the word would assert a food allergy she does not have; omitting it loses a real constraint on prescribing. `fixtures/peds-bp` case 5 is the input, and it is the only committed one. Ruled with the paragraph above.

**None of this settles what a named allergen's *reaction* reads**, which is [#94](https://github.com/mshamblin5150-code/clinical-skills/issues/94)'s. #96 decides which allergens reach the box and how each is named; #94 decides what the box says where the shorthand names an allergen and no reaction. The two were one ticket and were split because either can be settled without the other — **and both were ruled on 2026-08-16, on separate branches, neither able to see the other.** *The reaction beside a given allergen* below is #94's answer; this paragraph said it was still open for as long as it took the two branches to meet, which is [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s *the merge is the unguarded moment* arriving in a cross-reference rather than in a suite.

**The split held under the test that matters: the two rulings do not contradict each other.** #94 makes the `- reaction` half of the line satisfiable; #96 decides how many entries that line carries and what each is called. Drift row 17 carries both sets of limbs, and the reaction limb applies to every entry #96 puts in the box rather than only to the drug one — so a `seasonal environmental allergies` entry takes an inferred reaction like any other, which is what the worked example above already shows.

**And a `FILLED·asserted` line may not deny a given the note itself read.** `ALLERGIES NKDA filled. No allergy history was taken this visit.` was written by a run whose own note had read `seasonal allergies` out of the shorthand and used it four more times — in `PMH`, in a code, in the Plan and in the Assessment. **That is worse than the hedge drift row 12 bans and not a milder cousin of it:** `tobacco status not documented` is evasive about the record, and this is false about it. Where the shorthand names any allergen, the declaration names the kind the fill covers and names the given beside it rather than in place of it:

```
FILLED·asserted   ALLERGIES NKDA inferred — drug allergies only; the Plan's
                  azithromycin rests on it. The GIVEN seasonal allergies are
                  environmental and are carried in the box as a given, not filled.
```

**That shape is not invented here.** `fixtures/filled-anchor/notes/case-02.md` produced it unprompted in day-b run 1 and it is the committed evidence the ruling was chosen from; what it lacked was anything requiring it. Drift row 17 now does.

**The box is also where the coding step reads.** `fixtures/filled-anchor/run-2/case-02.md` anchors `J30.2` to the allergy-box line and quotes it, so a note that writes a bare `NKDA` and leaves the allergen in `PMH` hands `icd10-cpt` a different sentence to code from — and no committed run shows whether that still reaches `J30.2`. **So the placement was never presentational**, which is the strongest single reason this needed a ruling rather than a convention.
##### The reaction beside a given allergen

**Where the allergen is a given and the reaction is not, the reaction is inferred.** The clinician ruled it on 2026-08-16, [#94](https://github.com/mshamblin5150-code/clinical-skills/issues/94). The shorthand names the allergen and stops: over the **37 committed inputs**, 20 carry an allergy clause and **8 name an allergen, of which not one names a reaction** — re-derived 2026-08-16 over `git ls-files 'fixtures/*/shorthand/case-*.md'`. So the template's `allergen - reaction` shape is satisfiable from the shorthand only where the answer is `NKDA`, and until this ruling a run that found nothing to write had **no legal value at all**: the box demanded one, the grounding rule supplied none, and drift row 12 banned the hedge. **Three independent runs reached for the hedge anyway**, and one of the three is committed — `fixtures/filled-anchor/` carries the class **18 times across six files**: 12 in three `notes/` cases, and 6 more in three `run-2/` worksheets, which are [icd10-cpt](../icd10-cpt/SKILL.md) quoting those notes verbatim as `ANCHOR` strings rather than a fourth run writing it. **That is why the ruling changes the rule and leaves both run records alone** — every one of those anchors stops matching a re-run's input, and an anchor is a quotation.

**Counting it needs a pattern rather than a string, and that is the reusable part.** The class is written **five** ways in one run — `reaction not documented`, the same capitalized, `reaction pattern not documented`, `reaction to <drug> is not documented`, and `Reaction for the seasonal allergies: not documented`. (The fourth is redacted here because the run wrote a committed input's own allergen into it, and [#147](https://github.com/mshamblin5150-code/clinical-skills/issues/147) is why this file does not repeat one.) A `grep -c` on the literal reports 6 and 1 in two files and **misses a third note entirely**; `grep -oi "reaction[^.]\{0,40\}not documented"` reports the 18. **This paragraph published the undercount first**, which is the shape a banned string takes once runs start paraphrasing it, and it is why drift row 17 forbids *any* hedge rather than enumerating the ones seen so far.

**The box carries a reaction, reasoned the way every filled value here is** — the one this patient most plausibly had, from the drug class and what the encounter supplies, never a bland pick. `Penicillin - rash`. **The note body says nothing about where it came from**: drift row 12 bans every tier word from the note, and the tier block is the audit trail that travels beside it.

```
FILLED·asserted   ALLERGIES penicillin reaction rash filled; no reaction was
                  elicited this visit, and the Plan's cephalexin is proposed on
                  the allergen rather than on the reaction.
```

**The worked example is deliberately an allergen no committed fixture names**, and the first draft of this section was not — it used a drug allergen and the plan drug from one `day-b` case, which is the pair `fixtures/day-b` R6 grades. That is [#147](https://github.com/mshamblin5150-code/clinical-skills/issues/147)'s subject arriving a third time, and worse than the two instances that ticket names: **this file is the one every generating pass is required to read**, so a run scoring R6 would have read the answer to its own row here. Caught in review, the same way [#65](https://github.com/mshamblin5150-code/clinical-skills/issues/65)'s was. **#147 is still undecided and this is not a ruling on it** — it is the one position all three of its candidates agree on.

**This does not make the reaction a fourth member of the filled-vital class.** It is licensed by the two-part test at the top of this section, which the allergy box already passes as a whole — a box demands a value, and the shorthand constrains none.

**An inferred reaction may never discharge an obligation.** This is *An inferred allergy status may raise an obligation and may never discharge one* reaching the sub-field rather than the status, and it is the limb the ruling rests on. A penicillin allergy whose reaction reads `rash` is one a cephalosporin may be given against; one that reads `anaphylaxis` is not. So an inferred reaction **never licenses** a drug the documented allergen would otherwise bar — the generated value may tighten a decision and may never be what makes it safe. **The clinician named this case himself while ruling**: he asks what the reaction was before giving rocephin, and rocephin is a cephalosporin, so a fabricated `rash` is exactly the value that would answer his own question wrongly. The drug is still proposed where the **givens** support it.

**Where the reaction would change management, the FILLED line names what leans on it**, in the shape that rule already uses. **The test is floored at drug and food**, and the floor is where the code set draws it rather than where it is convenient — verified against `reference/icd10cm-2026.sqlite` on 2026-08-16 with `python tools/icd10_lookup.py --find "allergy status"`:

| Allergen | Codes as | Is the reaction in the code? |
| --- | --- | --- |
| Drug | `Z88.0`–`Z88.9`, keyed on drug class | **No** — `Z88` carries no reaction axis |
| Food | `Z91.01-` status **or** `T78.0-` anaphylactic reaction | **Yes, and the reaction picks which** |
| Environmental | usually `J30.1`, `J30.2`, `J30.81` — a disease | **Usually** — `J30`'s descriptor is the reaction |

So a **drug or food** allergen with no documented reaction always takes the disclosure, and an **environmental** one takes it only where knowing the reaction would change what the Plan does. The middle row is the one neither the ticket nor its eight comments had: for food the reaction does not refine a code, it **chooses the code family**.

**The third row says *usually* rather than *always*, and the qualifier is load-bearing rather than cautious.** `Z91.09` and `Z91.048` are billable allergy **status** codes for non-drug allergens and neither carries a reaction axis, so an environmental allergen coded as a status is in `Z88`'s position and not `J30`'s. **That is why the row is on the management test rather than excluded from the floor**: the floor is for the categories where the reaction is always owed, and environmental is the one where it depends. This paragraph read *a disease, not a status* and was over-stated — caught in review against the same `--find "allergy status"` output the section cites.

**Of the 8 inputs naming an allergen, 4 name a drug and 4 name *only* an environmental one** — and the `only` is doing work rather than decorating, because **two of the drug four name an environmental allergen as well**, so the two counts are not a partition and a reader who took them for one would have the wrong denominator for either. [#78](https://github.com/mshamblin5150-code/clinical-skills/issues/78)'s kind split counts 4 food in 173 across 551 encounters, so the food row is a corpus concern rather than a fixture one. **The nearest thing to a food case is not one**: `peds-bp` case 5 carries a lactose intolerance beside its seasonal allergy, and an intolerance is an enzyme deficiency rather than an allergy, so it names no food *allergen* and `Z91.01` is not its code. **Whether it reaches this box at all is [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96)'s**, which names that case, and nothing here rules on it.

**No GAPS entry, and that is a ruling rather than an omission.** The clinician was offered a variant that filed the missing reaction under GAPS as well and did not take it. A reaction written into the box is **supplied**, so there is nothing absent for the block to hold — *What never goes under GAPS* already covers the whole slot and now covers the sub-field for the same reason. A run writing `GAPS penicillin reaction not documented` has not found a gap; it has failed to fill a box, and drift row 17 is what catches it.

**Which allergens reach this box is not settled here.** The rule is category-neutral by construction — whatever allergen the box carries, a reaction absent from the shorthand is inferred — and #96 is where the prior question lives. The four environmental inputs therefore take an inferred reaction like any other, which for a seasonal allergy is the grounded one #29 blessed: itching and sneezing are what seasonal allergies do.

**What this narrows is stated where the absolute is**, under *Filled vitals, body measurements and the pain score*: that section closed its class test with *no exam finding, symptom or result will ever pass them*, and **a drug reaction is a finding, so the sentence forbade this ruling as written.** A file carrying both would contradict itself on two pages that each read as coherent alone, which is the defect [#90](https://github.com/mshamblin5150-code/clinical-skills/issues/90) exists over.

**What it costs is published rather than promised.** An inferred reaction is the **first generated value in this repo a reader can act on at the bedside** — a filled temperature is evidence about nothing but the rubric, and a filled reaction is evidence about what may be prescribed. The never-discharge limb is the whole of the mitigation, and it is the one clause here that may not be softened. The clinician was shown that argument before ruling and ruled anyway: the rubric's own heading is `Allergies (with reaction)`, so naming the allergen alone cost him a graded section.

**The allergy slot is the only one of these that needs the disclosure, and that is a fact about the slots rather than a narrowing of the rule.** The rule is general — **an inferred detail that drives a downstream clinical action discloses what leans on it** — and it comes out satisfied everywhere else by construction. The tobacco slot never reaches it, because a positive fill is forbidden outright and a negative one triggers nothing: there is no screening, no cessation counseling and no differential entry owed for a non-smoker, and [SOAP.md](SOAP.md)'s pack-year screening line keys to a **given** history. The remaining slots carry no clinical action at all — an occupation, an education level and a marital status change nothing the Plan does. **A future slot that did would take this same disclosure**, and the test for it is the one stated here: does the note do something differently because of the inferred value.

**Every filled slot is declared in `FILLED·asserted` carrying its value**, on the rule the filled-vital block states for the same reason: the clinician confirms a value, not a category. Not `social history filled` — `SH tobacco Non-smoker filled`, `ALLERGIES NKDA filled`, `SH occupation Employed filled`.

#### Filled vitals, body measurements and the pain score

**Filled vitals, body measurements and the OLDCARTS pain score** are permitted where the rubric requires a complete set and the encounter supplies only some — or none. They are the one exception to *filled content is unremarkable*, and the exception is narrow enough to state exactly.

**The class is a test, not a list.** A value joins it when both of the next two paragraphs hold of it: a box demands a value, and the shorthand constrains none. Three members are named because three are known — anything else has to earn entry by those two arguments, and **no finding this encounter would have produced — an exam finding, a symptom, a result — will ever pass them.** A result has no box standing empty, and an unmentioned system is already answered by *Silence is undocumented, never absent* one level up.

**That absolute read *no exam finding, symptom or result* until 2026-08-16, and [#94](https://github.com/mshamblin5150-code/clinical-skills/issues/94) narrowed it.** A drug reaction is a finding, so the old wording forbade the ruling that a given allergen with no documented reaction carries an inferred one — and the qualifier is what tells the two apart. **A reaction from years ago is a historical attribute of the patient**, sitting in a box the rubric enumerates, which is the class `NKDA` has always been in and which this file has instructed filling all along. A finding *this visit* would have produced is still absolutely barred, and nothing about the narrowing reaches a lab value or an unexamined system. The ruling, its floor and what it costs are under *The reaction beside a given allergen*; **an inferred reaction is not a fourth member of this class** and is licensed by the allergy box's own two-part test.

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

**Worked up does not mean the disease is worked up.** Where the encounter documents a cause for the elevation — fever, pain, a crying child — the response is to **name it and attribute it to that cause**, with a recheck once the patient is well. A raised pressure in a febrile, distressed toddler is addressed by attributing it to the documented fever the Plan is already treating; never by an antihypertensive, an echocardiogram, a renal ultrasound or a nephrology referral. Row 4 asks that a generated value not be abandoned. It does not ask for the evaluation of a condition nothing documented — that is a second invention resting on the first, and it is the one standing rule 2 forbids outright.

**The cause has to be a given finding**, which is what *documents* means here. `cc: fever` with no temperature anywhere still accounts for the pressure — the documented fever does the work and the degrees are incidental, so filling them changes nothing. What fails is a cause that is itself generated: a run that fills a fever, fills a pressure, attributes the second to the first and books a recheck has invented both halves of its own reassurance. Row 4 reads as satisfied and nothing was worked up.

**What *addressed* means was ruled 2026-08-15, and it narrows the word to two exits.** The old wording was a disjunction — the Assessment **or** the Plan — and four notes across three runs satisfied it while doing nothing about the number. The rule as ruled:

> A filled abnormal value reaches the **Plan** as **education, an order, or treatment** — or the **Assessment attributes it to something the Plan is already treating**. Confirming the measurement at follow-up does not count, and neither does an Assessment sentence whose only content is a promise of a Plan item that does not exist.

**A differential can be discharged by reasoning; a value cannot**, and that is the argument for closing the Assessment-only limb. Medical decision-making works through the differentials, saying why the less likely ones are less likely, and that reasoning *is* the addressing for a ruled-out differential — appendicitis ruled out owes no Plan line, where mesenteric ischemia, being the diagnosis, owes one. **A measurement is in neither group.** There is no ruling out 28.3, so the Assessment has nothing to decide about it, and the Assessment-only limb was never doing legitimate work for the values row 4 covers. **MDM is not treatment**: the Assessment reasons, the Plan acts, and any further workup — more labs, more imaging, a referral — goes in the Plan.

**A recheck is not an address.** *Confirm the height and weight at follow-up* is how you find out whether the number is real; it is not doing anything about it, and a rule accepting it is one any note satisfies for free, since confirming vitals at follow-up is boilerplate. This is the same distinction drift row 14 already draws for a filled *normal* — a monitoring instruction says to watch the value rather than accounting for it.

**Treating the cause counts, and the note has to say so.** A pulse of 122 and a respiratory rate of 28 in a febrile five-year-old with pneumonia are already being treated — by the azithromycin and the antipyretics — and neither owes its own Plan line. What it owes is **one clause in the Assessment** attributing the values to what the Plan is treating: *tachycardia and tachypnea consistent with the fever, expected to settle with treatment.* **Left silent, that note cannot be told from one that never thought about the numbers**, which is this whole rule's subject; and left silent, a Plan monitoring a documented diabetes would arguably discharge an overweight BMI too, since weight bears on diabetes.

**And the promise is not the item.** *Addressed with nutrition and activity counseling at the primary care follow-up* is a real sentence in a real Assessment whose Plan carries no weight, nutrition or activity line at all. It reads as an address, quotes as an address, and is a claim about a Plan item that does not exist. **Drift row 21 is what finds it**, by counting rather than by reading: the counseling was generated, written into `FILLED·proposed`, and never carried across. Issue [#47](https://github.com/mshamblin5150-code/clinical-skills/issues/47).

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

**Ruled 2026-08-15, and the paragraph above is what the clinician ratified.** #27 put the pain score inside row 15's class and never asked what row 15 then does about row 4's one-value normal range; the pass implementing it resolved the collision inline and shipped it, which is the thing this repo says an agent does not do, so issue #59 was filed to say so rather than leave it buried in a merged diff. The reading that shipped is the reading that stands: a filled `0/10` raises nothing, so it discharges nothing.

**The rejected alternative is kept here because it is what the ruling costs.** A filled `0/10` could have been a discharge like any other, owing the Plan an account the way row 14 makes a filled normal pressure owe one — a run that writes zero into a silent box has chosen a number that makes analgesia unnecessary, and under this ruling that run passes row 15. **So the Plan catches nothing here, and every guard on a bland zero is upstream of the Plan.** Three sit in the choosing — `fixtures/day-b` B8 forbids the zero where the complaint unarguably hurts, B14 forbids it where the exam holds a pain source, and *A reasoned 0/10 is not the default* below bars *filled content is unremarkable* from putting it there by itself. **One sits in the disclosure**, and it is *a filled 0/10 may not take drift row 19's no anchor exit* below, which makes the line name the search instead. That is the shape of this decision — three guards on which number gets chosen, one on how it is declared, and nothing at all after it reaches the note — and it is worth knowing before trusting a zero.

**And the case #59 asked for was never found.** The ticket named a complaint that does not hurt in an encounter with **no pain source in it** — the patient #42's ruling created, which reasons to zero honestly — and **no fixture in this repo holds one**, `fixtures/day-b`'s twelve least of all. The clinician ruled against the question rather than against a note. That is weaker than how the rules around it were settled and is stated rather than smoothed over; the fixture is still owed, and it is [#138](https://github.com/mshamblin5150-code/clinical-skills/issues/138). Issue #59.

**So the note orders the thing**, and it is a `FILLED·proposed` line like the swab a documented exposure generates. Ask what the givens alone require — not whether the generated numbers look reassuring — and write that. **The visit not having done it is not by itself a FLAG**; see *FLAG is the block that matters* in step 6. This costs notes that order what the clinician would not have, and that cost is the point: proposed content is reasoning, safe to be wrong about, and the preceptor rules on it. A withheld workup is none of those things.

Height and weight follow the same rule — *the value this patient most plausibly had*, and every constraint on it above — in this order: pick a height plausible for the age and sex, pick a plausible weight, then **derive** the BMI and show the arithmetic. Never pick a BMI and leave the height and weight to be read backwards out of it.

**The OLDCARTS severity is the third member, and it is a pain scale.** The box reads `6/10 facial pressure`, never `not documented` and never a word. (The separator between the element and its value is *Punctuation*'s business, not this rule's — a hyphen on SOAP's one-liner, the template's own colon in H&P's block.) Both arguments above hold of it exactly. A value is required, because severity is one of the rubric's eight HPI boxes. And nothing in the shorthand constrains which value, because a clinician who did not write a number down has said nothing about what the number was — the same asymmetry that makes an absent blood pressure uninformative.

*Filled content is unremarkable* would put the score at 0/10, and that is precisely the collapse this exception exists to prevent. 0/10 is the reading for a patient in no pain — a real answer where the shorthand says so, and a given when it does, but not one to arrive at by default.

**Score it the way a vital is scored: the value this patient most plausibly had.** Anchor it in the complaint, the exam and what was done about it. **The treatment given is the anchor a pressure does not have**, so use it: a run that writes 2/10 for a sinus pressure treated with intramuscular methylprednisolone has described a patient who would not have been given it, and one that writes 9/10 has described a patient who would not have been sent home.

**A filled score is answered in the Plan**, by analgesia or by the treatment of what is causing the pain. This is the same cost the license charges for a filled vital that lands abnormal, and the pain scale's normal range is one value wide — 0/10, and nothing else. It is not optional for the same reason either: a note that invents a 7/10 and offers nothing for it has manufactured the defect this skill exists to catch.

**Two things are givens rather than fills, and reading either one wrong invents a symptom.**

- **A score the shorthand writes is a given.** `c/o 8/10 pain` is 8/10 in the note — unrounded, unreplaced, exactly as a transcribed pressure is.
- **A documented absence of pain is a given too, and it scores 0/10.** `no pain`, or `is in no pain only when she bumps it`, is a charted finding. Filling a number over either is inventing a symptom, and no part of this exception licenses that: it buys a number for a complaint the shorthand documents, never a complaint.

**The scale scores pain, and the words after the number name the complaint rather than what is scored.** `6/10 facial pressure` is a pain score of 6/10 on a complaint of facial pressure; it does not grade the pressure. So a complaint that does not hurt needs no second form and gets no second rule — the number is still a pain score and the label is still the complaint. `3/10 nausea`.

**Where the complaint is not a painful one, reason the score from the encounter like any other filled value.** A documented pain source anchors it — a tissue injury, an inflamed joint, an infiltrated site — and a complaint with nothing of the kind behind it reasons to 0/10. This is *the value this patient most plausibly had* with no special case bolted on. The only thing that differs is where the anchor sits: in the exam rather than in the complaint, which is why the paragraph above tells you to read all three.

**A reasoned 0/10 is not the default the paragraph above forbids**, and the two have to be told apart or that sentence reads as a ban on ever writing zero. *Filled content is unremarkable* is barred from putting a zero in the box. Reading the encounter, looking for a pain source and finding none is not that rule — it is the instruction above arriving at zero honestly, and the `FILLED·asserted` line naming what the value was reasoned from is what a reader checks.

**Ruled 2026-08-13, and it corrects the sentence it replaces rather than confirming it.** That sentence said the scale *names what it scores*, which made the number a measure of the complaint; the ruling is that the number never stops being a pain score. It was settled by the clinician against a real encounter of exactly this shape — a patient whose complaint did not hurt, who returned a non-zero score when she was asked — which is why the reading that such a patient scores zero is now closed rather than open. Issue #42, carrying past issue #30 the way that extension was flagged as needing.

**Which encounter, and what she said, are deliberately not written here.** They are in `fixtures/day-b` under B14, which is withheld from a generating pass on [fixtures/README](../../fixtures/README.md)'s separation rule. A run that could read the answer off this file would recall it instead of reasoning to it, and no grader could tell the difference — which is the whole defect that separation exists to prevent, arriving by way of a rule's own provenance.

**And a filled 0/10 may not take drift row 19's *no anchor* exit, which is the one value that may not.** Every other generated value's line is allowed to say the encounter supplied nothing to reason from, and that admission passes — an unanchored height is honest, and *An unanchored value is not a defect* below is why. **For a zero the two sentences are one sentence.** *Nothing anchored this* and *I read the complaint and the exam and there was no pain source in either* produce the same number in nearly the same words, and the difference between them is only whether anybody looked. No reader can tell them apart, so the exit that is a disclosure everywhere else is an unchecked claim here.

**The zero's line therefore names the search rather than its outcome** — what in the complaint and the exam was read, and that no pain source was in either:

```
FILLED·asserted   SEVERITY 0/10 tick bite filled. Read the complaint and the exam
                  for a pain source: attached tick to the right shoulder, no
                  erythema, no swelling, no tenderness on palpation. Nothing in the
                  encounter documents pain, so the score is zero.
```

**That line is the whole of what stands between a legitimate zero and a lazy one once the number is in the note**, which is why it is a rule rather than a style note: a filled `0/10` discharges nothing and so owes the Plan nothing, and every other guard on it — `fixtures/day-b` B8, B14, and *A reasoned 0/10 is not the default* above — acts before the number is chosen. **Ruled by the clinician on 2026-08-15**, put to him alongside the row 4 / row 15 question above and answered separately from it. Issue #59.

**A given 0/10 is untouched, and so is a filled score above zero.** `no pain` in the shorthand is a charted finding scoring zero, and row 19 never fails a given. A filled `4/10` has a pain source by construction and names it the way every other filled value does.

**Every filled vital, every filled measurement and every filled OLDCARTS element is listed in the FILLED block carrying its value, written exactly as it appears in the note body.** Not `blood pressure filled` — `BP 142/88 filled`. Not `aggravating factors filled` — `AGGRAVATING bending forward, lying flat filled`, and `SEVERITY 6/10 facial pressure filled`. Two reasons, and the second is the load-bearing one:

- The clinician confirms a value, not a category, and cannot confirm what the block does not state. **The value is the floor and not the whole line** — *Which value was chosen is the instruction* below is what says the line names the reasoning too.
- The note body is written so given and filled content read identically. **The FILLED block is therefore the only thing in the whole document that can tell them apart**, and [icd10-cpt](../icd10-cpt/SKILL.md) reads it to decide which codes carry a `SOURCE: filled` mark. It matches on the value. A block naming the field without its value says a pressure was filled but not which one, and the mark fails open in silence.

**A derived value with a filled input is listed in the FILLED block too**, naming which inputs were filled — and it stays on the `DERIVED` line as well, with its arithmetic. A BMI is the case that matters: derived is a true statement about it, since the arithmetic has one right answer, but the answer is only ever as real as the height that went in. A BMI appearing under `DERIVED` alone reads as computed from measurements, which is exactly the impression it must not give.

#### A diagnosis code resting on a filled value is written, and says so

`Preexisting diagnoses (ICD10)` and `Final diagnosis` are Medatrax fields and they take codes, so this skill writes them. **A code whose supporting value was filled is written like any other** — derived from the note's own stated value, verified against `reference/icd10cm-2026.sqlite` rather than recalled, and followed by a line naming which inputs were filled.

**Not withheld.** A BMI of 26.5 from a filled height and weight produces `E66.3` and `Z68.26`, and the note carries both. The reason is not that the codes are earned — they are not, and [icd10-cpt](../icd10-cpt/SKILL.md) marks them `SOURCE: filled` for that reason. It is that **withholding them here made two skills disagree about one number**, with the note asserting what the worksheet refused and nothing telling the clinician which to believe. Two documents from one pipeline contradicting each other is a worse failure than a code that needs confirming, because the second is visible and the first is not.

**The disclosure line names the codes, not just the value**, and it sits directly beneath the field it qualifies:

```
Final diagnosis:
Cutaneous abscess of left foot, plantar great toe - L02.612
Overweight - E66.3 with Body mass index 26.0-26.9, adult - Z68.26

E66.3 and Z68.26 rest on a filled height (5'10") and a filled weight (185 lb);
the BMI of 26.5 is derived from those two and nothing measured. Confirm the
measurements before entry.
```

**Naming the codes rather than the value is the whole of what makes it usable.** *The BMI rests on filled values* leaves the reader to work out which of five entries that reaches; naming `E66.3` and `Z68.26` says which lines to confirm. It is the same argument the FILLED block runs on — the clinician confirms a value, not a category — arriving at a code instead of a vital.

**And withholding was never a rule this file stated**, which is how one run produced three behaviors over the same decision: six notes refused the family with a written block, two said nothing at all, and one wrote `E66.3` with `Z68.26` into `Final diagnosis`. All three were compliant with a file that did not speak. This paragraph is what it now says. Issue [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46).

**Two limits, and neither is about provenance.**

- **No code family is refused for resting on a filled value, and none is silently coded as if measured.** Both halves fail row 20.
- **A code the encounter cannot support is still not written**, however the numbers arrived. `I10` needs a documented hypertension because **no single reading diagnoses it** — a filled 138/86 supports `R03.0` and never `I10`, and a *given* 138/86 does not support `I10` either. That is a clinical limit and it stands where this rule does not reach.

**The adolescent case is the one where the code cannot be looked up.** Ages 2–19 take `Z68.5-`, a CDC growth-chart percentile rather than a BMI band, and this repo ships the codes without the charts — so the band is recalled and the note says so. [#123](https://github.com/mshamblin5150-code/clinical-skills/issues/123) removes that.

#### Which value was chosen is the instruction, and the note says how it was chosen

*The value this patient most plausibly had* is an instruction about **which number**, and it is the one half of this license nothing was holding a run to. A note is checked for whether the value exists (it does), whether an abnormal one was worked up (it was), and whether the block declares it (it does). **Nothing asks whether the number describes this patient**, and the answer turns out to be no more often than any single note can show.

**Across a set the filled values collapse onto a template.** Two runs of this skill over the same twelve encounters show it, and **the earlier one is committed** — `fixtures/filled-anchor`'s inputs are day-b run 1 byte for byte apart from two redacted site names — so the evidence can be recomputed rather than taken on trust:

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
                  Ht 5'10" (70 in) filled. Mid-range for a 68-year-old man; no
                  habitus or percentile datum in the source to move it.
```

Two reasons, and the second is the one that bites:

- **The clinician confirms a value, and cannot rule on one whose reasoning he cannot see.** This is the same argument that puts the value in the block rather than the field name.
- **An unanchored value has to stay visible, because the note acts on it.** A BMI derived from two unanchored inputs is a number about nobody, and drift row 4 will still make this note work it up. [icd10-cpt](../icd10-cpt/SKILL.md) codes off it and marks the code `SOURCE: filled` for exactly that reason, and it can only do so if the block says which inputs were filled.

**An unanchored value is not a defect. Concealing that it is unanchored is.** Where the encounter genuinely supplies no anchor — and for a height it often supplies none — the ordinary value is the honest choice, and the repetition across a set is that honesty's consequence rather than a fault to engineer away. **Do not manufacture a distinguishing value to break the pattern.** Choosing `6'1"` over `5'10"` for a man nothing describes is not a better-reasoned number, it is an invented finding with a cosmetic motive, and standing rule 2 forbids it in the same words it forbids every other one.

**What the pattern actually shows is anchors going unused, and the pressures are where that is unarguable.** A height is often unanchored. A blood pressure in an encounter with a documented condition, a given pulse, a given temperature, a documented pain score and an exam describing distress is not — the anchors are sitting in the note, and a run that lands the same side of 130/80 six times in nine has stopped reading them.

**Do not move the value to create the disclosure either.** *Do not move the value to avoid making the disclosure* is stated below for the BMI thresholds; this is its mirror and it is the one two runs have failed. **A filled value is not chosen to give the note an abnormal to work up.** The incentive is real and it is this file's own doing: far more is written here about what an abnormal filled value obliges than about what a normal one does, so a run demonstrating its compliance produces something to be compliant about.

**That prohibition is about intent, so here is the test it reduces to: an unanchored value may not land abnormal.** Where the line says the encounter supplied nothing to reason from, the value that patient most plausibly had is the ordinary one — that is what *most plausibly* means when nothing distinguishes the patient. **An abnormal chosen from nothing is an invented abnormal finding**, and it is only the box-demands-a-value argument that got filled vitals their exemption in the first place. That argument buys a number; it does not buy a raised one.

**This is not the bland-normal rule coming back**, and the difference is the whole of the section above. A value with an anchor follows the anchor wherever it goes — a 373 lb patient's pressure, a COPD patient's saturation, a distressed toddler's pulse are all abnormal and all earned. What is forbidden is the abnormal with nothing behind it, which is the shape both runs produced: a pressure just over the line and a line that names no reason for it being there. **So the two halves of the row work together** — the anchor makes the abnormal legitimate, and naming it is what a reader checks.

**The evidence that this is what is happening is that removing the rule changed nothing.** Until 2026-08-11 this section ordered a hypertensive pressure for a documented hypertensive; issue #23 retired it on a corpus count. **The run before that and the run after it both landed both hypertensives above the line** — 148/92 and 146/90 under the old rule, 138/86 and 138/86 under no rule at all — which is `fixtures/day-b` B2's second exit never once being reached in two runs under two different rules. A rule that is gone cannot be what is producing the number.

##### Two of these are graded now, and one of them needed no threshold

Ruled by the clinician on **2026-08-17**, [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97). That ticket asked what rate of repeated or not-normal filled vitals is wrong and objected to its own answer: *a row saying no more than N needs an N that nothing grounds.* **One of the two rules needs no N, and the other's N is not invented.** Both are settled by one command over a finished run:

```bash
python tools/filled_vitals_census.py <the run directory>
```

**A filled height's clause names the age and the sex** — the span from its own label to the next declared value, which is what the scanner reads and is **not** the physical line: several declared values share one. [#127](https://github.com/mshamblin5150-code/clinical-skills/issues/127) is the same undefined-unit question in the neighboring block, and this is the first place the unit is pinned rather than assumed. **36 of the 37 committed inputs give both**, so however little the encounter says about the body a height there is never *truly* unanchored — the two anchors are sitting in the shorthand. The rule was ruled on the stronger claim that *every* patient is given both, and that claim is false: `fixtures/day-a/shorthand/case-10.md` carries no age line, which is [#158](https://github.com/mshamblin5150-code/clinical-skills/issues/158)'s own case. **On such an input the height leans on an inferred age**, which is a real cost and is named here rather than left to be found — it is #158's *row 19 does not ask what else the note then built on it*, arriving with a second consumer. `Plausible adult male height` names a sex and no age and fails; `Mid-range for a 68-year-old man` and `plausible for a 44-year-old female` pass. **What is graded is the naming, not the claim** — `Approximately the 60th percentile for a 17-year-old male` satisfies this rule and rests on a band no committed file can check, because the repo ships the codes without the CDC growth charts. [#123](https://github.com/mshamblin5150-code/clinical-skills/issues/123) is that, and this rule must not be read as endorsing a recalled percentile. **Spell the sex** — a bare `M` or `F` does not count, because `T 98.4 F filled` sits in the same block and its Fahrenheit mark would otherwise satisfy the rule for whatever height is beside it. **The `no habitus or percentile datum` exit is untouched**: it still passes, and the age and sex are named alongside it rather than instead of it.

**Repetition itself is still not graded, and that is the ruling rather than a gap left in it.** Nothing counts how many heights land on one value. The paragraphs above are why — the repetition is honesty's consequence where the encounter supplies no habitus datum, and a bar on it would leave a compliant run no escape but inventing a distinguishing value, which standing rule 2 forbids in the same words. **A rule whose only available remedy is a banned act is not a rule.**

**Filled pressures may not land not-normal far more often than a fair split explains.** The corpus is what grounds this: 249 transcribed pressures split about evenly at 130/80, so an honestly reasoned set of filled pressures should land like that many coin flips. What was chosen is not a count but **how often an honest run may be failed for nothing** — 2%, which puts the bar at **8 or more of 9**. Six of 9 is a coin-flip outcome one time in four and **passes deliberately**; a bar failing it would fire on an honest set a quarter of the time, which is the rate at which a warning stops being read. **Six is the smallest set this can fail**, and only by failing every pressure in it.

**One-sided, on purpose.** Filled pressures clustering *normal* is the bland normal — a different defect, guarded upstream in the choosing — and a two-sided test here would fail a run for the opposite of what this section is about.

**A clean run is not a walked section, and the gap is named rather than left implicit.** Three vital classes are graded. **Temperature, heart rate, respiratory rate, oxygen saturation and pain score are counted and not graded** — the corpus offers no even split for any of them to ground a bar the way 130/80 grounds the pressure one — and in the committed run those classes carry **36 filled values against the 27 the graded rules read**, the severity being the one none of the twelve declares. Whether a filled temperature was reasoned is still a question for a reader.

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
- Screenings appropriate to the patient's age — **checked against the shipped sheet rather than recalled**. The Plan line reads as it always did; the population the recommendation is keyed to goes in the **tier block**, never beside the screening in the note. See *Guideline sheets*. This is the bullet a note followed to build a nine-item screening list on an age it had invented.
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

## Guideline sheets

Two sheets ship in this repo, and where one covers what a Plan item asserts, it is **consulted rather than recalled**. This is the [icd10-cpt](../icd10-cpt/SKILL.md) code-set arrangement arriving one document over: a fact this repo holds is looked up, and a fact it does not hold says so. Issue [#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85).

| Sheet | Holds | Covers |
| --- | --- | --- |
| [`reference/guidelines-uspstf.md`](../../reference/guidelines-uspstf.md) | 143 recommendation statements, each with grade, population, interval, year, file and page, plus the verbatim statement text | preventive screening and counseling, **90 of 90** USPSTF documents |
| [`reference/thresholds/`](../../reference/thresholds/) | per topic, the numeric decision points — target, cutoff, dose, interval — each with a verbatim snippet, source, page and class | **one topic**, hypertension, out of a 179-document corpus |

**The obligation fires on the item's subject, never on whether the item states a number.** Before writing a Plan item whose appropriateness rests on a **population or a threshold** — every screening, counseling and immunization item, and every treatment item resting on a target or a cutoff — open the sheet that covers it. An item resting on neither is outside this rule entirely: `return precautions given`, `ibuprofen 400 mg PO q6h PRN for the sore throat`, `follow up as needed`. So is every part of the note that is not the Plan.

**Gating this on a stated number was the live alternative and it was rejected.** `Colorectal cancer screening discussed` names no band and rests on one exactly as hard as `colorectal cancer screening from 45` does — the age decided whether to write the line at all. A number-gated rule would consult the sheet for the second and not the first, **which lets a line escape by being vague**, and that is the direction this repo refuses everywhere else: an unnumbered screening item is the *harder* one to check, not the exempt one.

### The two silences are not the same silence

Absence of a row means different things in the two sheets, and writing one wording over both is the defect this section exists to prevent.

- **USPSTF is complete for what it covers.** 143 rows drawn from 90 of 90 documents, so a topic with no row is a topic the USPSTF has issued no statement on. The note may write `no USPSTF row` and mean it.
- **A threshold sheet is not**, and its own [README](../../reference/thresholds/README.md) says so: *an empty directory entry is not a negative finding about a guideline.* A missing row there means one of three things, and the note may never claim it means the first:
  1. the guideline holds no such number,
  2. the recommendation was **scoped out by name** for carrying nothing a decision-point sheet can hold — 50 of hypertension's 103 are, each with its own reason in `## Coverage`, **28 of them reading exactly `no number`** and the rest naming what was missing more precisely: `no numeric trigger`, `no threshold value`, `no dose or duration stated`, and twice a number that exists only in a footnote. `single-pill combination recommended` and `shared decision-making principle` are both in that list,
  3. the section it would be in was **never read** — every sheet's `## Scope` carries a `Not read:` limb, and hypertension's excludes the narrative sections, the evidence tables, the appendices and the reference list.

So a threshold sheet that holds no row for what the note asserts earns `sheet does not settle it` and never `no guideline applies`.

### The citation

**Block only. It never appears in the note body.** A citation for a line this skill generated is this skill defending its own work, which is *The tier language stays out of the note* one section up, and it is the sharper half of the ticket's own constraint: a cited threshold reads as more authoritative than a recalled one **whether or not it applies**, and the note must not be more persuasive than it is correct.

A bracketed tail on the item's own line, so the citation survives the line being copied out — the reasoning [icd10-cpt](../icd10-cpt/SKILL.md) gives for `SOURCE: filled` and `NOT FOR ENTRY`, that a block heading does not survive being copied one line at a time.

**The sheet is named first**, because every field after it resolves only inside that sheet: `aha-2025` is a key in one sheet's `## Sources` and `adults-htn` is a key in its `## Populations`.

```
FILLED·proposed   Colorectal cancer screening discussed [uspstf: grade A, adults 50 to 75, 2021]
FILLED·proposed   Continue lisinopril 20 mg daily, recheck 4 weeks [thresholds/hypertension: aha-2025 Class 1, adults-htn, SBP >=140]
FILLED·proposed   Zoster vaccination discussed [uspstf: no row]
FILLED·proposed   Inhaled maintenance therapy reviewed [recalled, no shipped sheet; catalog lists GOLD 2026]
```

**`no USPSTF row` says the USPSTF has issued no statement. It never says the item is not indicated**, and the zoster line is the case that shows the difference: the sheet holds **zero** immunization rows, because vaccine schedules are ACIP's remit and the USPSTF does not write them. So that verdict is a true and checkable fact about the sheet sitting on an item that is entirely appropriate — which is why the wording names the sheet rather than the medicine.

**The tail stays on the item's line however long the line gets, and the lines above are not shortened to make that look comfortable.** The rule is about **the tail**, and nothing else in the block inherits it — a `DERIVED` line's arithmetic wraps the way the inferred-age line does, because arithmetic is not a marker and loses nothing by being read on two lines. A citation pushed onto a continuation line is the defect the same-line rule exists to prevent, and it is worse here than for `NOT FOR ENTRY` because a citation is three to five times longer and so likelier to wrap by accident. Four differential entries in `fixtures/filled-anchor/run-2/` already wrapped their descriptor and put an end-of-line marker on a continuation line, which is [#70](https://github.com/mshamblin5150-code/clinical-skills/issues/70) — **so a marker on the item's own line is countable, not reliably countable**, and that limit is named here rather than left for a counter to discover.

**The filename and page are never written into the note.** Both sheets carry them per row, so the citation identifies the row and the sheet supplies the jump — which also means a corpus refresh that renames a file cannot leave a past note citing something that no longer exists.

**The population is taken from the sheet's own cell. It may be shortened; it may never be softened.** Every condition in the cell survives into the tail — the wording may compress, and nothing may drop out. `adults aged 40 to 75 years who have 1 or more CVD risk factors and an estimated 10-year CVD risk of 10% or greater` becomes `adults 40 to 75 with 1+ risk factor and 10-year CVD risk 10%+`, which is shorter and asserts the same three things. Dropping the risk threshold would be softening, and it is the one edit that makes an unmet population read as met. **The test is whether a reader could be surprised by the cell**, and the two examples above are the calibration: nothing in either sheet's row would surprise someone who had read only the tail. Two things about that cell are worth knowing before it is trusted. In the USPSTF sheet the column is **derived from the statement text rather than quoted from a declared field** — the sheet says so at its top — so it is a reading, and a row whose population decides the patient's care is a row to check against the page it names. And **one row of the 143 has a population reading `not stated`**: the tail carries `population not stated` verbatim rather than inventing one, which is the same refusal as a `needs:` and reads as an instruction to open the source.

**A population this repo cannot evaluate takes `verify this number`, and it is not a `needs:`.** The two are different: `needs:` names a measurement nobody took, and this names one that was taken and cannot be banded here. The case is pediatric, and it is the same hole [#123](https://github.com/mshamblin5150-code/clinical-skills/issues/123) holds open for `Z68.5-`: `Interventions for High Body Mass Index in Children and Adolescents` is keyed to *a high BMI (95th percentile for age and sex)*, and **this repo ships the codes and the recommendations without the CDC growth charts**, so whether a child is at that percentile is recalled however carefully it was checked. Writing the citation without the mark would put the most authoritative-looking tail in the section on the one population nothing here can check.

```
FILLED·proposed   Weight management counseling discussed [uspstf: grade B, children and adolescents 6 years or older with a high BMI (95th percentile for age and sex), 2024] verify this number
```

**The population is the field that is not optional**, and it is there because of a real failure: a note filled an age of 55, built a nine-item age-keyed screening list on it, and the patient was 25. Every recommendation on that list may have been individually correct and none of them was owed to that patient. A citation without its population makes that note look better without making it truer. Issue [#158](https://github.com/mshamblin5150-code/clinical-skills/issues/158).

### What the note owes when the population is not met

**A filled population key is marked, never withheld.** Where the age, sex or measurement the row is keyed to was itself filled, the item says so — `age filled` — and the item is still written. This is drift row 20's ruling for codes applied one document over: *no code is withheld for resting on a filled value, and none is written as if measured.* Both halves fail here too.

**A population condition the encounter never established takes `needs:`**, which is [icd10-cpt](../icd10-cpt/SKILL.md)'s own word for the measurement nobody took. A population **key** hides its own definition — `adults-htn-lowrisk` expands to *"adults with hypertension, no clinical CVD, 10-year PREVENT risk <7.5%"* — so the unmet limb has to be named beside it rather than left inside the key:

```
FILLED·proposed   Statin discussed for primary prevention [uspstf: grade B, adults 40 to 75 with 1+ risk factor and 10-year CVD risk 10%+, 2022] needs: 10-year risk not calculated
```

**Compute the risk where every input is present, and never invent one to get there.** A risk score is arithmetic on stated values, so it belongs under `DERIVED` with its arithmetic like a body mass index — but only when the note holds **every** input the equation takes. Any input missing and the item takes `needs:` instead.

**Nothing is filled in order to complete a score, and that is not the same as refusing a filled input.** This paragraph read *no input to a risk score is ever filled*, which is wrong twice: it contradicts the example below it, which runs on a filled age and a filled pressure, and it would bar the ordinary case. Age and vitals are filled by rules that already govern them, and a score reads them like any other stated value. **What is barred is filling something because the equation wanted it** — a value chosen to produce a number rather than to describe the patient, which is outside standing rule 2's exception in both of its limbs.

**A lipid value is barred outright, on a stronger ground than either.** It is a *result*, and *What may be inferred* refuses one however plausible. So an encounter with no panel back takes `needs:` and never a computed score, which is the common case and the reason this rule is worth writing down.

**And a score resting on a filled input carries that up into the citation it keys.** A risk computed from a filled age decides which population row applies, so the tail says `age filled` exactly as it would had the age been read off the row directly — otherwise the disclosure is lost at the one step that most looks like arithmetic.

**Name the calculator the cited row keys on, not a favorite.** The two sheets do not agree: AHA/ACC 2025 keys its populations on **PREVENT**, the USPSTF statin rows on an *estimated 10-year CVD risk*. And this repo ships no calculator, so the coefficients are recalled — the number carries `verify this number`, on [icd10-cpt](../icd10-cpt/SKILL.md)'s rule for working from recall.

```
DERIVED           10-year risk 12.4% = PREVENT, age 58 / male / SBP 148 treated /
                  TC 214 / HDL 38 / smoker / no diabetes — verify this number
```

### When nothing ships

Where no sheet covers the topic, the item reads `recalled, no shipped sheet` and the note may name **one** further thing: a document from [`reference/guidelines-catalog.md`](../../reference/guidelines-catalog.md), **and only on a literal match**. The catalog says what each of the 179 documents *is* and never what it says, so naming one is a checkable fact about which documents exist rather than a clinical claim — and gating it on a grep is what keeps it that way.

- `grep -i "chronic obstructive" reference/guidelines-catalog.md` hits, so a COPD item may read `[recalled, no shipped sheet; catalog lists GOLD 2026]`.
- `grep -i "zoster" reference/guidelines-catalog.md` returns nothing — the ACIP row's topic reads `adult immunization schedule`, which shares no word with it. So a zoster item names no document. **Finding it would take knowing that zoster is ACIP's business, which is recall wearing a citation.**

It fails closed: no hit, no name.

### What a citation can never carry

**Whether the recommendation applies to this patient is not machine-checkable, and no wording here makes it so.** The population is quoted so a reader can compare it in one jump; that is the whole of what this buys. Two further limits are the sheets' own, written down in [reference/thresholds/README.md](../../reference/thresholds/README.md) rather than discovered: a sheet whose numbers are all real and all filed under the wrong heading passes every gate in that directory, and 138 of the 179 documents cannot be omission-gated at all — so *the sheet was consulted* and *the sheet is complete* are separate claims and only the first one is cheap.

## Conventions

**Favor the more complex note.** Where a differential could run three deep or five, run five. Where a finding could be left in Objective or carried into Assessment, carry it. Thoroughness is the tiebreaker, always.

**Marital status** is inferred from age and written into the Social History, not left as unreported.

**Social history** does not blanket-fill with "not reported", and it does not hedge a single slot either. Every slot the template enumerates carries a value; which value comes from *Which way a social or allergy slot reads*.

That rule used to end *"say it where it is genuinely unknown and would matter; otherwise write the inference"*, and the escape hatch is deleted rather than narrowed. **Every slot is genuinely unknown** — that is the premise the whole section starts from — so a clause excusing the hedge wherever the value is unknown excused it everywhere, and *would matter* is what a run decides for itself right before writing `tobacco status not documented this visit`. Nothing is lost: a slot whose value the encounter cannot ground is the unclassifiable case above, and it takes the grounding rule rather than a hedge. Issue #29.

### Voice

**Where `scratch/voice-model.md` exists, it governs the prose this skill writes.** His ruling,
2026-08-18: the voice applies to output, not only to a case study. The model is per-account and
lives in `scratch/`, so it is already in reach of every skill here — what this section settles is
**how much of it applies where**.

[practicum-case-study/reference/voice.md](../practicum-case-study/reference/voice.md) §2 names three
registers. A note is not a case study and does not take all three:

| Register | In a note | Where |
| --- | --- | --- |
| 1 — clinical argument | **Yes** | Assessment, the differential's reasoning, a `NOT CODED` rationale |
| 2 — spoken patient education | **Yes** | Patient education, return precautions, discharge instructions |
| 3 — reflective and argumentative | **No** | Nowhere in a note |

**Register 3 is excluded, and that is a ruling rather than an omission.** It is where the metaphor
and the aphorism live, and a chart is not the place for either — another clinician reads a note to
find out what happened, and a figure of speech between them and a finding is a cost with no
benefit. **The exclusion is about the register, not about force**: register 1's flat verdict and
register 2's *state the cost, then say do it anyway* are the strongest things in the model and both
belong in a note.

**Nothing in the model bends a structural rule, and the list is closed.** The tier block's grammar,
the Medatrax field strings, the drift matrix, an ICD-10 descriptor, the template's own formatting
instructions, **row 22's welded refusal — `NOT CODED: <code> <descriptor>, <reason>`, on one line**
— and the two rules below this one, *Punctuation* and *Spelling*, are all fixed. **The model governs
the prose between them and nothing else.**

**The refusal is on that list because the table above hands its rationale to the model, and the two
together were a hole.** A `NOT CODED` rationale is register-1 prose and reads as the model's to
shape; the welded form is also **the only string `tools/differential_scan.py` reads**, and
[#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153) established what happens
when it is reshaped — hard-wrap the rationale and the refusal becomes invisible, `codes marked NOT
CODED 0`, **exit 0, a silent pass**. So a per-account model could have rewritten the one string
whose rewriting the scanner cannot survive, and
[#162](https://github.com/mshamblin5150-code/clinical-skills/issues/162) is why nothing would have
caught it: that scanner's exit-1 path has never fired on a real run. **The reason goes in the
clause; the clause stays welded and stays on its line.** A voice model is the last thing consulted
and the first thing dropped: where it pulls against a rule anywhere else in this file, the rule
wins, on [voice.md](../practicum-case-study/reference/voice.md) §9's terms.

**Punctuation is the live conflict and it is already decided.** His own prose is full of em dashes;
the rule below forbids them in a note body. **The rule wins**, and this is exactly why the model is
consulted last — a register is how the reasoning sounds, not which glyph carries a pause.

**Where there is no model, nothing changes.** This skill's existing conventions are the whole
answer and no run declares anything, because a note has no `PROPOSED` block to declare it in and a
tier block is for claims about the patient. **That is the one place this differs from
`practicum-case-study`**, which declares an unmodeled voice because it has somewhere to put it.

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

### The shape of the differential

**The differential is a numbered list, ranked most likely first, and `1.` is the favored entry.** The numerals are written rather than implied. A grader reading the school's *"3 differential diagnoses"* counts items, and a ranking nobody can see is a ranking that was not made. `Favored.` and `Less likely.` stay on the entries as well — drift row 22 exempts the favored entry from its naming limb, and something has to say which entry that is on a branch where position alone would have to carry it.

**The `Name - CODE: rationale` form stopped being permitted and started being required**, and that is the half of the ruling a numeral does not carry. The hyphen pinning a code to its label is the *Punctuation* rule above, and until now nothing made a run use it. **`day-a` run 2 pinned every entry with a hyphen and not one of the committed [filled-anchor notes](../../fixtures/filled-anchor/notes/) does** — the same skill text, two runs, opposite habits; the counts are in `fixtures/day-a/assertions.md` and pinned by `tools/test_differential_scan.py` respectively, and are deliberately not repeated here. A form that emerges under one run and vanishes under another is not something a binary row can rest on. So `COVID-19 (U07.1): …` and `Acute bronchitis: J20.9 …` both fail row 23 however well-reasoned the rationale is, and the conclusion line is the one exemption — row 22 reads it by position instead, and says why.

**One entry per numbered item, and the item is the unit rather than the line.** [SOAP.md](SOAP.md) writes an item on one line, code and rationale together; [HP.md](HP.md) writes it on two, the code line and the rationale beneath, because the school's template puts the code on its own line. **A wrapped line belongs to the item that opened it and never opens one** — the numeral is what opens an item, which is `tools/block_scan.py`'s entry-versus-wrap distinction reused here for its reason. That sentence is not pedantry: mandating a form moves the ambiguity from *what is an entry* down to *what is a line* rather than deleting it. Four entries in [fixtures/filled-anchor/run-2](../../fixtures/filled-anchor/run-2/) wrapped a long descriptor so a marker landed on a continuation line, a grader reading physical lines published a figure short on both counts, and **the suite was green over the wrong number** because the test pinned the parser's answer and the parser was what was wrong. The corrected figures and the correction are in that run's own README, once — [#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124) found it. This rule is written so the question arrives with the mandate instead of after it.

**A diagnosis argued down inside a paragraph is a defect, not an entry.** `day-b` run 2's case 11 argued three diagnoses down inside prose carrying no code:

```
Genital ulcer disease is the frame. Herpes simplex is the usual cause at this age, but there are no vesicles and no prodrome; a primary syphilitic chancre would be painless and this one is tender; molluscum contagiosum is umbilicated and this is not. None is favored.
```

Read as prose that is one thing and no code is owed; read as three diagnoses it is three entries and three codes are missing. **Both readings were defensible, and a recorded score depended on which one a grader picked.** The form is what removes the question rather than adjudicating it: three diagnoses argued down are three numbered items, each carrying its code and the specific finding that rejects it. The reasoning in that paragraph is good and nothing in it is lost by numbering it.

**Where the differential ends is not where the heading does.** All twelve `day-b` run 3 notes wrote a second, separately headed block after the conclusion — `Additional problems addressed today`, `Also addressed this visit`, `Reasoning carried forward` — and in four of them the items were diagnosis-shaped and mixed, coded and uncoded side by side:

```
Also addressed this visit:
Essential hypertension - I10, elevated today at 148/92
Drug and condition conflict: methylprednisolone 125 mg IM was administered
Body mass index 28.6, in the overweight range
Nicotine dependence, cigarettes - F17.210
Lightheadedness - R42
```

**A diagnosis-shaped line anywhere in the Assessment is an entry and carries a code**, whatever heading a run writes above it. The narrow reading — count the block the note itself headed `Differential:`, which is how run 3 scored — was the live alternative, and it is escapable by moving an uncoded diagnosis one heading down. That is the same defect in a new place, so it lost.

**Two of those five lines are not diagnoses, and they part company.** A **measurement of the patient's own body is a diagnosis for this rule** and takes its code — `Body mass index 28.6, in the overweight range - Z68.28`, out of the `Z68` family [icd10-cpt](../icd10-cpt/SKILL.md) already anchors and drift row 20 already verifies. A **line of reasoning is not**, and does not get a line of its own: a drug-against-condition conflict belongs inside the rationale of the entry it concerns. **That is not an escape from drift row 11**, which asks that a conflict between givens be *named in the Assessment or the Plan* — it is still named there, inside an entry, rather than standing as a problem line nobody can code.

**The clinician ruled all four of these on 2026-08-16**, each against a rendered example rather than a description of one, which is #68's method reused. Drift rows 13 and 23 walk them. [#70](https://github.com/mshamblin5150-code/clinical-skills/issues/70).

**What no tool checks, and that is a consequence of the ruling rather than a gap in the tooling.** Deciding that `Body mass index 28.6, in the overweight range` is a diagnosis and `Drug and condition conflict: …` is not takes a reader, and so does finding a diagnosis-shaped line under a heading a run invented. A scanner could read the block headed `Differential:` and would then be checking the narrow reading this ruling rejected — reporting clean on exactly the note that moved a line one heading down. **So these rows are counted by a reader**, the way rows 2, 16, 18 and 21 are counted by one, and [#164](https://github.com/mshamblin5150-code/clinical-skills/issues/164) holds what a partial scanner could still be worth.

### Naming a differential entry

**An entry is named for the code it carries.** Label and code always agree — `Acute bronchitis - J20.9` names what `J20.9` says — and that is unremarkable until the two can come apart. [icd10-cpt](../icd10-cpt/SKILL.md) refuses a code whose descriptor names a confirmed organism or disease the encounter never established, and the entry still has to be called something. **It is called what the surviving code says**, with the refused disease named in the rationale:

```
2. Pain in right leg - M79.604: 4/10 pain over a chronic right leg wound, tib/fib film ordered today to rule out contiguous osteomyelitis, no result. NOT CODED: M86.9 Osteomyelitis, unspecified, nothing established it. Less likely.
```

**That leaves a symptom on the left-hand side, and it is the ruling rather than a side effect.** Put to the clinician on 2026-08-15 against a whole differential rendered this way — `Pain in right leg`, `Chills` and `Shortness of breath` standing where a grader reading the school's *"3 differential diagnoses"* expects diagnoses — and answered: the disease belongs in the rationale, which is where the differential is graded. Nothing is lost, because every disease considered is still named there with the specific finding that rejects it.

**What the convention buys is that a label cannot assert.** Issue #68 was filed because one run produced three renderings of a single rule — the entry named for the refused disease, two entries collapsed under one refusal, and the entry renamed to the suspicion with the organism demoted into an adjectival clause. All three happened to keep the refused code out of the code slot and **nothing required them to.** A fourth rendering putting `M86.9` on the label with the refusal in a footnote would have read as compliant while asserting a disease nobody established. Pin the label to the code and there is no slot left to hide one in.

**A refusal is written `NOT CODED: <code> <official descriptor>, <reason>` — the mark first, the code welded to it by the colon.** Never the other way round, and never with the descriptor between them. This is `icd10-cpt` step 4's own form, and it is the form all twelve worksheets in [fixtures/filled-anchor/run-2](../../fixtures/filled-anchor/run-2/) use; until 2026-08-16 this file wrote the code first and the two skills rendered the same thing two ways.

**The reason is that the mark has to be findable without guessing.** `tools/differential_scan.py` used to pair a mark with the last code before it on the same line, and that guess broke in both directions. Hard-wrap a rationale so `NOT CODED` starts a line and the refusal became **invisible** — the scan reported nothing refused and passed. Write a drift-row-22 verdict saying *"the slot after the hyphen carries `M79.604`, never a code marked `NOT CODED`"* and the note was read as refusing its own final diagnosis. **Describing the rule was what broke it.** With the pair welded, a wrap cannot separate them and a sentence writing the mark without a colon is not a refusal. [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153).

**Two refusals on one entry are joined by a semicolon, and the mark is repeated:**

```
NOT CODED: A41.9 Sepsis, unspecified organism, the vitals do not support it; NOT CODED: R78.81 Bacteremia, no blood culture drawn.
```

The semicolon is what bounds a refusal and its reason, so the second mark is not optional shorthand — `NOT CODED: A41.9 …; R78.81 Bacteremia, no blood culture drawn` reads as one refusal with a long reason, and `R78.81` is then a code the note names and never accounts for.

**Two refusals resting on one documented finding are one entry, not two.** The supported code is written once and the rationale names both:

```
3. Chills - R68.83: chills over a chronic infected wound growing a resistant Klebsiella, but afebrile at 97.3, heart rate 77 and respiratory rate 18, so no SIRS criteria are met. CBC and lactate ordered today with no result. NOT CODED: A41.9 Sepsis, unspecified organism, the vitals do not support it; NOT CODED: R78.81 Bacteremia, no blood culture drawn. Less likely.
```

**Those two refusals do not share a reason, and one reason covering both would be wrong.** `R78.81 Bacteremia` is bacteria demonstrated in blood, so a pending culture is genuinely what it waits on. **Sepsis is not a culture finding** — it is diagnosed at the bedside from vitals, white count and lactate, and `A41.9`'s descriptor names no organism a culture could supply. So sepsis is rejected on *this patient's* vitals, never on the pending culture. The clinician's ruling, 2026-08-15; [#149](https://github.com/mshamblin5150-code/clinical-skills/issues/149) carries the general form, and until it lands this example is the only place the distinction is written down.

**The favored entry and the conclusion line are the exception, and they keep the hedge.** Those are the clinician's own conclusion rather than the skill's reasoning, so *never soften a hedge* wins there and the label keeps his words. **`Final diagnosis` on both branches** since 2026-08-16 — see [HP.md](HP.md) on what that replaced and what it cost:

```
Final diagnosis: Community-acquired pneumonia, mycoplasma suspected - J18.9
Pneumonia, unspecified organism. Nothing tested for the organism, so NOT CODED: J15.7 Pneumonia due to Mycoplasma pneumoniae; a positive titer would earn it.
```

**The conclusion is the one place a code is read by position rather than by punctuation**, and it is worth knowing before writing one. Every code in the `Final diagnosis` block that is not inside a `NOT CODED:` clause is read as asserted, whatever pins it — so a code floated there as an alternative, or pinned with a colon instead of the hyphen, is an assertion. `day-a` run 2's case 7 wrote `Final diagnosis: Streptococcal pharyngitis, suspected: J02.0` beside a refusal of `J02.0`, and the colon alone is what hid it from a scanner reading only hyphens. **Nothing pinned in a conclusion escapes on punctuation.**

The code is still only what the encounter supports, and **the refusal goes on the line beneath rather than into the label** — the second line above is what that looks like, and a conclusion line carrying a hedge and no refusal beneath it has dropped half the rule. **So one note calls one thing two names three lines apart** — the hedge on the favored entry and on the final, the strict code-name form on every entry argued against. That was put to the clinician as an inconsistency and kept deliberately: the entries argued against are this skill's contribution and take the discipline, the conclusion is his and keeps his wording.

It binds both branches, which is why it lives here rather than in either template — [SOAP.md](SOAP.md) and [HP.md](HP.md) carry only the rendering, which differs between them. Drift row 22 walks it, and `python tools/differential_scan.py <a run directory>` checks the one limb that is mechanical: **no code marked `NOT CODED` anywhere in a note may appear in any entry's code slot.** Issues #68 and [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153).

**A run written in the retired form exits 2, not 0**, and that is the scanner refusing to grade rather than breakage. It reads only the welded pair, so a note writing `M86.9 Osteomyelitis, unspecified NOT CODED, …` has refusals it cannot pair with a code — and *nothing refused* is the same output as *row 22 satisfied by construction*. **One bare mark anywhere in a run is enough**, because a run part-written in each form is the worst of the two: the welded refusals are graded, the bare ones are invisible, and the clean verdict line covers both. Rewriting a run into the welded form is what makes it gradable, and the `unwelded NOT CODED marks` count printed above the verdict says how much is owed.

**So when a note talks *about* the mark rather than making one, put it in backticks.** That is standing rule 4's own mention-versus-use distinction — the one `tools/spelling_scan.py` runs on — reused here because the problem is identical. A row-22 verdict written `no code marked `NOT CODED` sits in a slot` is a mention and costs nothing; the same sentence with the mark bare is indistinguishable from a refusal the parser could not pair, and takes the whole run to exit 2. **A drift matrix row is already safe** without the backticks, because a pipe table is skipped outright — it is the loose sentence, in a `FLAG` or a `GAPS` entry or a discussion paragraph, that needs them.

**And a violation outranks an incomplete scan.** A run with a genuine row-22 failure *and* a bare mark exits **1**, not 2, because the failure is the strongest thing known about it. The exit-1 message then says the finding is a floor rather than the whole count.

### Spelling

**American English, always** — [standing rule 4](../../AGENTS.md), so it binds every skill here and not only this one. His ruling, and it is unconditional. These are notes for an American program, read by American faculty, and a British spelling reads as a note written by somebody else. This section is the table the rule points at.

| Never | Always |
| --- | --- |
| `dyspnoea`, `apnoea`, `anaemia`, `haemoglobin`, `oedema`, `diarrhoea`, `paediatric` | `dyspnea`, `apnea`, `anemia`, `hemoglobin`, `edema`, `diarrhea`, `pediatric` |
| `caesarean` | `cesarean` |
| `sulphate`, `nebuliser`, `catheterise` | `sulfate`, `nebulizer`, `catheterize` |
| `millilitre`, `centimetre`, `litre`, `fibre` | `milliliter`, `centimeter`, `liter`, `fiber` |
| `grey`, `behaviour`, `colour`, `tumour`, `favour` | `gray`, `behavior`, `color`, `tumor`, `favor` |
| `labelled`, `recognisable`, `programme`, `licence` | `labeled`, `recognizable`, `program`, `license` |
| `neighbour`, `judgement` | `neighbor`, `judgment` |

**Drug names take the United States generic**, which is the same rule where it costs the most to get wrong: `acetaminophen` not `paracetamol`, `epinephrine` not `adrenaline`, `albuterol` not `salbutamol`, `ferrous sulfate` not `ferrous sulphate`. A clinician reading the other name has to translate it before they can check the dose.

**Wider scope than the punctuation rule above, and the difference is why this one is a standing rule and that one is not.** Punctuation governs the note body only, and it lives here because it governs *this skill's* two branches. Spelling reaches the tier blocks, the Medatrax fields, the filenames, the commit messages and the prose about the skills — which is more than a skill file can bind, so it is stated in [AGENTS.md](../../AGENTS.md) and only tabulated here.

**About the output, not the input.** A British spelling arriving in the shorthand is normalized on the way out like any other spelling variant — the same treatment [GLOSSARY.md](GLOSSARY.md) gives `cetrazine`. It is not a hedge and it is not a number, so nothing in *Given* protects it.

**Most of the forms above were written by this repo**, and that is why the rule is here rather than assumed. **The tally that used to open this sentence is gone on purpose** — it read `thirteen`, then `fourteen`, and was one short of its own enumeration within the hour, which is a prose integer nothing recomputes sitting in the paragraph about figures announcing themselves. Five came from [GLOSSARY.md](GLOSSARY.md)'s own expansion tables — `nebuliser`, `sulphate`, `millilitres`, `centimetres`, `caesarean` — which is where a wrong spelling does the most damage, because the skill copies an expansion into a note by design. Seven more came from a `clinical-note` run — `dyspnoea`, `fibre`, `grey`, `behaviour`, `labelled`, `recognisable`, `programme` — and `licence` came from `fixtures/peds-bp/assertions.md`. All were corrected 2026-08-12 **except the run's**, which are preserved because `fixtures/filled-anchor/notes/` is a byte-for-byte record of what a day-b run produced — apart from two redacted site names — and correcting it would falsify the evidence. Issue #73.

**The fourteenth is `neighbour`, added 2026-08-18, and how it was found is the reusable part.** It sat in [GLOSSARY.md](GLOSSARY.md), in the sentence `the tell is the neighbouring word`, in a file this repo wrote, while the same repo writes `neighboring` correctly ten times in this one. **`spelling_scan.py --all` reported clean on every run, because the table did not hold the form**, which is the tool's own stated limit arriving as a real miss: *it holds the table rather than the language, so a clean scan means no listed form was used.* It was caught by eye during unrelated work, not by the scanner. **And the backticks in the sentence above are load-bearing** — this paragraph quoted the defect in italics first and the scanner failed the build, correctly: a form in running prose is a use however clearly the sentence around it is about the form. That is `spelling_scan.py`'s mention-versus-use rule working on the paragraph that documents it.

**Adding it moved the preserved run record's figures without the record moving**, and the two facts have to be kept apart. **The run produced exactly what it always produced; the instrument got better.** `tools/test_spelling_scan.py` pins all three figures, which is why each change announced itself rather than passing quietly.

**The fifteenth is `judgement`, added the same day, and it was named in this repo's own documentation the whole time.** [docs/agents/issue-tracker.md](../../docs/agents/issue-tracker.md) lists it beside `neighbouring` as a British form the table does not hold — written to warn about **ticket text**, which nothing scans. **Both were also sitting in the committed run record**, which that sentence did not say and nobody checked: `judgement` three times in `case-07` and `case-08`. **Naming a form in prose is not adding it to the table**, and a form documented as invisible is still invisible.

**So the record's figures moved twice in one session**, 8 forms / 20 occurrences / 6 notes, then 9 / 22 / 7, then **10 / 25 / 7** — `case-07` and `case-08` were already in the set, so the tenth form added occurrences without adding a note. Re-derive with `python tools/spelling_scan.py --record` rather than quoting this sentence; that is the whole reason the command prints the breakdown.

**That run wrote both spellings of most of them**, which is what makes the record evidence of drift rather than of a register: `cesarean` eight times against `caesarean` twice, `dyspnea` seven against `dyspnoea` three, `program` nine against `programme` twice, `fiber` three against `fibre` four. **Nobody reading one note would see it** — the same shape as [#67](https://github.com/mshamblin5150-code/clinical-skills/issues/67), and the same reason twelve outputs had to be put in front of one reader.

**A fourteenth instance — of a form already on that list — was in a skill file, and the hand sweep that wrote this section missed it.** `batch-shift` used `programme` in prose about the clinician's program, and what found it was `python tools/spelling_scan.py --all` — this table with a command in front of it, which is the ordinary way to check now:

```bash
python tools/spelling_scan.py --all      # every tracked .md
python tools/spelling_scan.py --record   # the preserved run record, form by form
```

It reads Markdown only, and it holds this table rather than the language: a clean scan means no *listed* form was used. `tools/test_spelling_scan.py` parses the table above and asserts the scanner covers every row of it, so the two cannot drift apart. **The rule is complete without the command** — this table is the instruction, and skipping the scan costs a check rather than an answer.

**The rule has been exercised, and until 2026-08-12 it had not been.** A rule written after the run that motivated it is a rule nothing has walked, so day-b's twelve encounters were re-run that day on `ffe9377` — twelve generating passes, shorthand pasted inline, `fixtures/` closed — and graded by `python tools/spelling_scan.py` over the output rather than by a reader. **None of the eight forms the table then held appears in 4,275 lines.** A wider hand net — the `-ise` family, the `oe` and `ae` digraphs, `-our`, `-re`, `-ence`, 46 stems in all — came back empty too. **The denominator has since moved to ten and the notes that run produced are gitignored and gone**, so this clean verdict cannot be re-derived in either direction — it certifies eight forms over an artifact nobody can re-grade. Kept as the dated measurement it is, and not restated as a current one.

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

**Read `scratch/shorthand.md` first if it exists**, then [GLOSSARY.md](GLOSSARY.md). Two glossaries: this clinician's own forms and the field's, and **where they disagree the per-account file wins**. [GLOSSARY.md](GLOSSARY.md)'s *Two glossaries* section is the rule, and [setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 9 is where the per-account one gets collected.

Classify **every token** against both as expanded, verbatim, or unknown. An unknown token is carried forward as written and surfaced in the tier block — never dropped, never guessed at silently.

**A genuinely absent `scratch/shorthand.md` is not an error and the fallback is safe** — the field glossary expands what it holds and everything else surfaces as an unknown token, which is the shape a reader can act on. **What is not safe is expanding one clinician's form by another's rule**, and that is the case the split exists to prevent.

**But check where you are standing before calling it absent.** `scratch/` is gitignored, so a `git worktree` has none at all and the file may be sitting in the main checkout — see *Where `scratch/` actually is* in [setup-clinical-skills](../setup-clinical-skills/SKILL.md). **Not-collected and not-reachable look identical from here and are not the same finding**, and the sentence above would bless the second as safely as the first. That is [#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93)'s silent degradation, which this repo already fixed once for `phi_scan` and has now had to fix a second time in prose a consumer reads.

Completion: every token in the source is in exactly one of the three buckets.

### 3. Choose the branch

The program sets the rule: **the first six documented encounters of a practicum course must be H&P forms.** After six, SOAP is the student's choice and is the practical default.

- **FNP H&P** → [HP.md](HP.md). The first six encounters of a course, or whenever the user says H&P, FNP, OLDCARTS, or asks for the long form.
- **Comprehensive SOAP** → [SOAP.md](SOAP.md). Everything after that.

Check the count before assuming. `Student Overview` in Medatrax reports forms by type; if the current course has fewer than six H&Ps, this encounter is an H&P regardless of what is convenient. State which branch you chose and why.

**Where a branch was named, that is the branch.** A user who says *H&P* has decided, and [batch-shift](../batch-shift/SKILL.md) step 4 settles one for a whole shift. **This does not suspend the rule above**: if you can see the count and it disagrees — fewer than six H&Ps on the course, and SOAP named — say so and let the clinician choose. The program's rule is the program's, and a named branch is an instruction rather than a ruling on whether the form is the right one.

**Where nobody named one and the count cannot be checked, write SOAP, say which you chose, and offer to redo it as an H&P.** Ruled 2026-08-16. The rule above needs the `Student Overview` count, and a run outside `batch-shift` usually has no Medatrax session to read it from — so what happens is not that the rule is applied, but that it is **guessed at from the same words that state it**. `fixtures/day-a` run 2 is the evidence: given the shorthand with no branch stated, several of its passes chose the FNP H&P unprompted and were discarded. Nothing was wrong with their reasoning; the branch is simply not derivable without the portal. **The count is stated once, in [fixtures/day-a/assertions.md](../../fixtures/day-a/assertions.md)**, because it was measured against a directory under `scratch/` and nothing committed re-derives it.

**The default is wrong during the first six encounters of a course, and saying so out loud is the whole of the mitigation.** That is the one window where it is wrong, and it is also the window where nobody thinks to name a branch — a course starting from zero has no habit yet. So *state which branch you chose and why* is load-bearing here rather than a formality: it is the clinician's chance to catch it on note one instead of note eleven. **Never silently default during a course whose count you have not seen.**

Load only the branch's template.

### 4. Tier every element, then draft

Assign each element a tier before writing, then draft into the branch template. Obey the rubric's own formatting instructions inside that template exactly — they are the school's, not yours. Where it says short succinct statements and no sentences, write fragments.

**One heading departs from the rubric, and it is the only one.** The H&P's conclusion is written `Final diagnosis:` rather than the rubric's `Actual diagnosis/diagnoses with ICD-10 codes:` — the clinician's ruling on 2026-08-16, so that both branches name the conclusion the same way. [HP.md](HP.md) carries the reasoning and what it costs. **The authorization is named here because the instruction above is here**: a pass reading this step and then finding a template that does not match the rubric quoted inside it would otherwise have to guess which of the two was stale, and guessing against a rubric is how a graded heading gets silently restored.

### 5. Emit the Medatrax entry

Produce the field block from [../../reference/medatrax-fields.md](../../reference/medatrax-fields.md) in that file's field order, so it can be tabbed straight into the form.

Fields carrying a **declared rule** — `Primary Payment Method`, `Race/Ethnicity` — are filled from that rule rather than reported missing. Neither is visible in bedside shorthand, and reporting them missing on every note is what teaches a clinician to skim this block. **The two rules do not live in the same file.** `Race/Ethnicity` is universal Medatrax behavior and is in the reference. `Primary Payment Method` keys on the site, which makes it per-account, so it is in `scratch/medatrax-profile.md` under *Declared field defaults* — the reference names that location where it describes the field, so following the field order still finds it. Do not restate either here.

**Resolve the patient before the fields.** Medatrax stores no name — it generates a Patient Reference and that is its only handle on a person. An encounter entered without matching the existing record creates a **second** patient, silently and unmergeably. So look the name up in the clinician's identity map first, and emit either the matched Patient Reference or an explicit `NEW PATIENT` line. Where the day file gave no name to match on, say that: it is the exact mechanism by which duplicates are made, and it is worth one line rather than a discovery months later. Location and format of the map come from `/setup-clinical-skills`.

Everything else the encounter does not supply goes under GAPS rather than being invented — with three exceptions, each generated by design and declared rather than reported missing: start and end times, which the Times convention estimates; **vitals and body measurements**, which are filled to the value the patient most plausibly had; and **age**, which is inferred and flagged at the top of `FILLED·asserted`. The field that justifies the caution is `Patient Time`: it feeds the course's area breakdown, so a wrong band misallocates clinical hours. Most of the rest feed no hours bucket at all.

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

**`FILLED·proposed` is a record of what the note contains, not a list of what it meant to.** Every item on it is a line the note body actually carries — a Plan order, an education point, a follow-up interval — written down here so the clinician can see which of them this skill contributed. **An item with nothing behind it in the body is not a milder defect than a missing one; it is the block describing a note nobody wrote.** A run that proposed *"Nutrition and activity counseling for the overweight body mass index"*, wrote no such Plan line, and then reported the BMI as addressed is the shape, and drift row 21 is what counts it. Fixed by writing the item or by striking it from the block — never by a verdict saying it is there. Issue [#47](https://github.com/mshamblin5150-code/clinical-skills/issues/47).

**A decision not to do something the encounter did is not a forward action**, and `FILLED·proposed` is not where it goes — nowhere is. Declining to order a test the clinician did not order is ordinary reasoning and belongs here; declining one he **did** order is *A given order is a given*, and the order stays in the Plan whatever this block says about it.

A value can occupy two lines at once, and one routinely does: a BMI derived from a filled height is written under `DERIVED` with its arithmetic *and* under `FILLED·asserted` naming the filled input. Listing it only as derived hides that it was invented; listing it only as filled hides that it was computed.

**A guideline citation rides on the `FILLED·proposed` item and does not move it.** There is no fourth tier and no `FILLED·cited` line. The three tiers answer *what did this encounter supply*, and for a screening item the answer is still **nothing — this skill wrote it**; a citation answers a different question, which is what stands behind the content. Two axes, so the citation is a tail on the line rather than a new heading. **The load-bearing part is that a cited item stays under FILLED**, where the clinician's confirmation pass reads it: a tier that moved cited items out would have taken the nine-item screening list off the one block a preceptor reads hardest, at the exact moment it most needed reading. Format and obligation are under *Guideline sheets*.

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
| 4 | **Vitals** | Every vital **or body measurement** outside the normal range for this age is **addressed**, not just recorded — **filled ones included**, with no exemption for being generated. **Addressed has two exits**: the **Plan** carries **education, an order or treatment** for it, or the **Assessment attributes it to something the Plan is already treating**. **Re-measuring the value at follow-up is not an address**, and neither is a sentence promising a Plan item the Plan does not contain. A filled height and weight yield a BMI, and an abnormal BMI is addressed like any other. A filled pain score is the same rule with a one-value normal range: **0/10 is the only unremarkable score**, so any other is answered in the Plan |
| 5 | **Sig** | Every drug carries dose, route, frequency and duration |
| 6 | **Red flags** | The return precautions name specific findings — *fever above 101, worsening flank pain, inability to keep fluids down* — never "red flags reviewed" |
| 7 | **Drug names** | Each drug reads as the shorthand wrote it, trade or generic, unconverted |
| 8 | **Band** | Patient Time follows Adult ≤ 59 / Gerontology ≥ 60 — overriding the Medatrax label's `Adult (18 – 60)` — with an obstetric or gynecologic visit taking precedence. An inferred age passes this row only if the inference is named on its own line in `FILLED·asserted` |
| 9 | **Arithmetic** | Every derived value shows its working and recomputes correctly |
| 10 | **Entry** | Every Medatrax field holds a given, a derived value, a declared value, or a GAPS entry |
| 11 | **Conflict** | A conflict between givens — a drug against a documented condition, or a drug against a drug — is named in the Assessment or the Plan. No inferred medication resolves one, and no given medication is dropped to dissolve one |
| 12 | **Leakage** | No tier word in the note body names where a line came from — *given*, *filled*, *inferred*, *derived*, *asserted*, *proposed* — no sentence describes this skill's own process, and every Plan parenthetical holds a trade name alone. The ordinary clinical senses pass: *given in clinic*, *given her hyperlipidemia*, *prescription filled* |
| 13 | **Differential** | Every differential entry carries an ICD-10-CM code, and **no diagnosis the encounter did not establish** — differential entry, favored entry or final — carries a code whose descriptor names a confirmed organism or disease. **An entry is one numbered item, and the count is not bounded by the `Differential:` heading**: a diagnosis-shaped line anywhere in the Assessment — under `Also addressed this visit`, `Reasoning carried forward` or any heading a run invents — is an entry and owes a code. **A measurement of the patient's own body is a diagnosis here** and takes its code; **a line of reasoning is not**, and belongs in the rationale of the entry it concerns rather than on a line of its own |
| 14 | **Control** | A **filled** value that is a documented condition's own diagnostic measure and lands **normal** is accounted for **in the Assessment**. Hypertension: called *controlled*, *treated*, *on therapy*, or with the medication named. Obesity: called resolved, improved or post-surgical, or with the weight-loss intervention named. A code in a pre-existing or problem list is not an account, and neither is a monitoring instruction. A **given** value never fails this row, and neither does a filled abnormal — row 4 already holds that one |
| 15 | **Filled reassurance** | No decision to withhold, defer or narrow the workup of a documented finding rests on a filled vital, body measurement or pain score, and any cause a filled abnormal is attributed to is a **given finding**. **A reassuring clause that changes no action is not a discharge** — a filled normal named inside a differential ranking passes where the workup is ordered anyway. A filled 0/10 is not a discharge — row 4 owns that direction. **And a test the encounter itself ordered is not a workup this note withheld**: removing a given order and then citing its absence here is row 18's defect being scored as this row's pass |
| 16 | **Duration** | Every stated duration reaches the HPI attached to the symptoms it was written beside, written `<duration> for <symptoms>`. None is dropped, and none is applied to a symptom the shorthand did not attach it to. Two durations for the **same** symptom are written as a span containing both, never one endpoint chosen over the other and never a FLAG. **Both a span and an attribution that rested on resolving a pronoun are declared in `FILLED·asserted` carrying their value**; an attribution whose onset line named its own symptom is not |
| 17 | **Inferred history** | Every social and allergy slot the branch template enumerates carries a value, **none of them a hedge** — no `not documented`, `not reported this visit` or `status unknown`. No **positive** tobacco or vaping status is filled. A slot the corpus cannot classify is **grounded in the shorthand**, not invented beside it. Every filled slot is declared in `FILLED·asserted` carrying its value, and where a **proposed drug** rests on an inferred allergy status, that line names the dependency. **Every allergen the shorthand names reaches the Allergies box named by its kind** — drug, environmental or food — and the box states a drug status whether or not a drug allergen was named: routing a stated allergen to `PMH` instead fails, and so does a box carrying an allergen and no drug status. A food intolerance is carried and is **called an intolerance**. **A given allergen with no documented reaction carries an inferred reaction** — never `reaction not documented` — declared the same way, and for a **drug or food** allergen that line also names what leans on it. **No inferred reaction licenses a drug the allergen would otherwise bar.** **And no `FILLED·asserted` line denies a given the note read** — `NKDA filled. No allergy history was taken this visit.` beside a stated seasonal allergy fails this row, and fails it for being false rather than for hedging. A **given** status never fails this row, but a reaction inferred beside a given allergen is graded like any other filled value |
| 18 | **Orders** | Every order the shorthand records — a test, an imaging study, a referral, a drug, an immunization — appears in the finished note as an order. **Checked by counting, the way rows 2 and 16 are:** list every order token in step 2's expansion, wherever it was written, then name where each one landed. **And no sentence anywhere in the note says a given order was not placed** — that limb is checked separately, because retaining the order does not make the denial true. An objection to a given order is written beside the retained order as a recommendation, never in its place and never as a `FILLED·proposed` line |
| 19 | **Choice** | Every filled vital, body measurement and pain score's `FILLED·asserted` line names what the value was **reasoned from** — or states that the encounter supplied no anchor for it, **which every value but one may say**. No value is chosen to give the note an abnormal to work up, and none is moved to avoid a disclosure. A **given** value never fails this row, and neither does an unanchored one that says it is unanchored. **The one exception is a filled `0/10` pain score, which may not say it had no anchor and names the search instead** — what in the complaint and the exam was read, and that no pain source was in either. **A filled height names the age and the sex as well**, and the *no anchor* exit still passes beside them rather than instead of them. **Across a set, the filled pressures may not land not-normal far more often than a fair split explains** — `python tools/filled_vitals_census.py <the run directory>` settles both, and a clean run leaves the rest of this row to a reader |
| 20 | **Filled-anchored codes** | Every ICD-10-CM code in `Preexisting diagnoses` or `Final diagnosis` is derived from the note's own stated value and **verified against `reference/icd10cm-2026.sqlite`** — **except a pediatric `Z68.5-`**, which is a growth-chart percentile the database cannot settle and which carries `verify this number` instead. Where a code's supporting value was filled — or derived from any filled input — the note **names which inputs were filled**, beside the field. **No code is withheld *for resting on a filled value*, and none is written as if measured**: both halves fail. Withholding on a **coding-guidelines** ground is outside this row, and a code resting only on **given** values never fails it |
| 21 | **Proposals** | Every `FILLED·proposed` item appears in the note body. **Checked by counting, the way rows 2, 16 and 18 are:** list every item the block proposes, then name where each one landed — the Plan order, the education point, the follow-up interval, the results line. **An item that landed nowhere was dropped**, and the block is describing a note that was not written. Fixed by writing the item or by striking it from the block, **never by a verdict saying it is there**. An `UNKNOWN`, a `FLAG` or a `GAPS` line is not a landing |
| 22 | **Entry name** | Three limbs. **Naming** — every differential entry is named for the code it carries. **Slot** — no code marked `NOT CODED` anywhere in the note appears in any entry's code slot; the mark is the welded `NOT CODED: <code>` and a bare one is not read as a refusal at all. **Collapse** — two refusals resting on one documented finding are **one** entry naming both, not two entries sharing a label. **The favored entry and the conclusion line are exempt from the naming limb and from neither of the others** — `Final diagnosis` on **both branches** since 2026-08-16, and inside it every code not in a `NOT CODED:` clause is slot-held whatever pins it — because those keep the clinician's hedge, with a code beside it that is still only what the encounter supports. Where nothing was refused this row is satisfied by construction; it is failed by a label asserting a disease its code does not |
| 23 | **Ranking** | The Assessment's differential is a **numbered list ordered most likely first** — `1.` is the favored entry — and **one entry per numbered item**. No diagnosis is argued down inside a paragraph: a differential written as prose fails this row however good the reasoning in it. The item is the unit, not the line — [SOAP.md](SOAP.md) writes one on one line and [HP.md](HP.md) on two — and **a wrapped line belongs to the item that opened it and never opens one**. **And the form is required rather than permitted**: the entry pins its code to its label with a hyphen, `Name - CODE: rationale`, so a code in parentheses or pinned with a colon fails this row. The conclusion line is exempt and row 22 says why |
| 24 | **Guideline backing** | Every Plan item whose appropriateness rests on a **population or a threshold** — every screening, counseling and immunization item, and every treatment item resting on a target or cutoff — was **checked against the shipped sheet that covers it**, and its `FILLED·proposed` line carries the verdict as a tail on that line: a citation naming the sheet, the source and strength, the **population**, and the value — or `no USPSTF row`, or `sheet does not settle it`, or `recalled, no shipped sheet`. **The trigger is the item's subject and never whether it states a number**, so an unnumbered screening line owes this row exactly what a numbered one does. **The three silences are not interchangeable**, and a threshold sheet's may never be written as `no guideline applies`. A population key that was **filled** says so; a population condition the encounter never established takes `needs:`. **No citation appears in the note body.** An item resting on neither a population nor a threshold never fails this row |

**Row 14 is appended rather than slotted beside row 4**, which is where it belongs by subject. Rows 1 through 13 are cited by number across this file, three fixture sets and [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md), so renumbering to put it in its natural place would silently redirect every one of those citations. Its subject is row 4's, its number is not, and that is a deliberate cost.

**It was written as row 13 and became row 14 on merge**, because issue #19's Differential row was appended on another branch at the same time. That is the cost of append-only landing on two branches at once, and it is cheaper than the alternative: had either row been *inserted* where it belonged by subject, the collision would have silently renumbered the other's citations instead of announcing itself as a conflict.

**It is the only row whose failure is made of silence.** Every other row can be failed by something written down wrongly; this one is failed by a note that reads perfectly and simply never accounts for a number the skill invented. That is why it is a row at all rather than a line in the vitals section — §7 requires a verdict per row *by name*, and a rule that is not a row never gets walked.

**It applies to two measures today and is written for more.** Blood pressure against hypertension and BMI against obesity are fixtured, in `fixtures/day-b` B2 and `fixtures/obesity-bmi` O2 respectively. A third would qualify on the same test the vitals section states: the value has to *be* what the condition is diagnosed by. Most vitals are not, for most conditions, and this row is not an invitation to explain every normal number in the note.

**Row 15 is appended for row 14's reason and became 15 the same way**, on a third branch landing at the same time — it was written as row 13 for issue #27 before either of the two above existed. Its subject is row 4's and row 14's; its number is neither's neighbor. The convention holds: **append, never insert**, because inserting silently redirects every citation by number in this file, the fixture sets and the ADR, where appending only ever costs a merge conflict that announces itself.

**Rows 14 and 15 are the two halves of what a filled normal owes and is owed.** Row 14 says a filled normal against its own condition must be accounted for. Row 15 says a filled normal may never be spent — it buys no deferral, no narrowing and no withheld test. A note can satisfy one and fail the other, which is why they are two rows: `HTN, controlled on lisinopril` accounts for a generated 124/78 and passes row 14, and the same note can go on to defer a workup on that same number and fail row 15.

**Row 15's pain-score clause shipped unruled on 2026-08-12 and was ratified on 2026-08-15.** `A filled 0/10 is not a discharge — row 4 owns that direction` decides where this row stops against row 4's one-value normal range, and #27 never asked the question — the pass implementing it answered it inline, and filed #59 the same day to say so. The clause reads today exactly as it read then; what changed is that it is now the clinician's. **The alternative was live and it was not obviously worse**: a run that writes zero into a silent box has chosen a number that makes analgesia unnecessary, and reading that as a discharge would have made the note owe the Plan an account the way row 14 does. The argument for the clause, and what the ruling costs, are in *The pain score's two directions are split between row 4 and row 15* above. Issue #59.

**Row 15 also shipped with an opening sentence broader than the rest of the row, and it was struck on 2026-08-16.** It read *Every reassurance in the note traces to a given*, and the sentence after it — the one that is the row today — reaches only a decision to withhold, defer or narrow. **A clause can reassure without changing anything the note does.** The shape that forced the question is a differential entry ranking a diagnosis down partly on a normal saturation the note's own block declares filled, in a note that orders the imaging anyway and says in writing that the filled value played no part in ordering it. Under the broad sentence that note fails; under the rest of the row it passes. **The clinician ruled for the row**, and *a reassuring clause that changes no action is not a discharge* is that ruling written into the cell. **The runs, the cases and the clauses are in `fixtures/day-b`'s record and are deliberately not repeated here** — [#147](https://github.com/mshamblin5150-code/clinical-skills/issues/147) is why, and a rule needs its shape rather than the notes it was found in. Issue [#69](https://github.com/mshamblin5150-code/clinical-skills/issues/69).

**What the ruling costs is that the sentence a reader sees is not the sentence this row grades.** `no hypoxia` in a finished note offers a measurement as evidence, and nothing in the prose says nobody took it. Three things carry that instead — row 19 makes the value declare what it was reasoned from, the FILLED block names it filled, and row 12 keeps both out of the body — and **none of them is visible in the clinical sentence itself**. Widening the row was the alternative and it was rejected on what it would have failed: **this file's own worked example under *Naming a differential entry* is the disputed shape**, ranking sepsis down on `afebrile at 97.3, heart rate 77 and respiratory rate 18, so no SIRS criteria are met` while ordering the CBC and lactate regardless. Reasoning a differential from the vitals in front of you is what a differential is; this row forbids **spending** them, and those are different acts.

**That example does not itself fail the widened row, and the difference matters enough to state.** Nothing there declares those three vitals filled, and this row reaches only filled values — so *the skill prints a failing example* would have been too strong, and the honest claim is narrower: **widening would have failed that shape wherever the vitals behind it were filled** — which is not an edge case but the ordinary one, because a shorthand carrying no vital line makes every number in that sentence invented. The rejected reading would have been unable to print its own best output over any encounter that arrives without vitals.

**`fixtures/day-b` B9 is this row written a second time, and since the ruling a test holds the two together.** `Row15AndB9StateOneRule` in `tools/test_corpus_census.py` reads the *Passes when* cell out of each table and asserts neither still states the retired sentence and both state the ruling. It reads the **cell** rather than the file, because both files argue about the retired sentence in prose below their tables and must go on being able to — the third test asserts exactly that, so deleting the record fails as loudly as leaving the rule broad.

**The two paragraphs above were rewritten before this landed, and what they lost is the point.** They first carried the runs, the clause quoted verbatim, and a count of how many of that set's encounters arrive without vitals — a **census over a scored set's inputs**, which is a shape [#147](https://github.com/mshamblin5150-code/clinical-skills/issues/147)'s three positions were not written against and which is worse than a quotation: it tells a generating pass what its own inputs look like before it writes a word. Caught by the tracker sweep this ruling was obliged to run, on the pass that wrote it. **A rule earns its place here by its shape; the evidence lives with the set that produced it.**

**Row 16 is appended for the same reason as 14 and 15, and its natural neighbor is row 11.** It is a rule about two givens disagreeing, which is row 11's subject, and it sits at the bottom instead. The convention holds: **append, never insert** — inserting silently redirects every citation by number in this file, the fixture sets and the ADR, where appending only ever costs a merge conflict that announces itself.

**But it is not row 11 widened, and the two rows demand opposite things.** Row 11 says a conflict between givens is *named*; row 16 says one particular conflict is *resolved*. Both are right, because a span exists for durations and does not exist for a drug against a condition — the argument is in *A duration belongs to what it is written next to*. A run that names a duration conflict instead of spanning it has not satisfied row 11 by proxy; it has failed row 16.

**It is checked by counting, the way row 2 is.** Take each duration in step 2's expansion — every `x N days`, every `started yesterday`, every dated onset — and name the symptom it landed on in the finished HPI. A duration that landed on nothing was dropped; a duration that landed on a symptom the shorthand never attached it to was moved. Both fail, and both read perfectly well, which is why this is a count rather than an impression.

**Its quiet failure is the folded timeline.** A note that reads a multi-symptom complaint, takes the chief complaint's number as the illness's duration and never notices the second onset statement produces a fluent, internally consistent HPI with one timeline in it. Nothing in the note points at the missing one. The count is what finds it.

**Row 17 was written as row 16 and became 17 on merge, which is the third time this has happened here.** Rows 14, 15 and now 17 were all appended on branches in flight against each other, and the paragraphs above record the first two. **That is the convention working, not failing.** Issue #33's Duration row reached `main` first and owns 16; this one moved. Had either been *inserted* at its natural neighbor — 16's is row 11, 17's is row 4 — the collision would have silently redirected the other's citations instead of announcing itself as a conflict on one line of a table.

**Row 17 is the first row whose prohibitions were already in the file.** Row 12 has banned `Allergies (reaction): Not documented this visit.` since issue #28 — a sentence that defends the note rather than reporting on the patient, which is exactly the test row 12 carries. Row 1 has banned `smokes 0.5 PPD` for longer than that, since a tobacco history is an abnormal finding and an abnormal finding must trace to a given. **Neither was ever applied to a social slot**, and two committed fixture rows spent months rewarding the hedge row 12 forbids.

**That is the argument for the row rather than against it.** Row 14 states it about itself: §7 requires a verdict for each row **by name**, so a rule that is not a row never gets walked. Rows 1 and 12 are walked as questions about findings and about leakage, and a run answering them honestly still never looks at the `SH:` line. Row 17 is where it looks.

**It also carries two things neither of those rows contains.** The grounding bar on the slots the corpus cannot classify is nowhere in rows 1 or 12 — `Works manual labor` is not an abnormal finding and not a sentence about this skill's process, it is simply a fact about a patient that nothing supplied. And the allergy dependency is row 15's subject reaching a value outside row 15's class, which is why it is stated here rather than by widening that row and redirecting its citations.

**Check it by reading the branch template's slot list against the note, then the note against the block.** Count the enumerated slots, count the ones carrying a value, and count the ones the FILLED block declares with a value. Then take each slot the shorthand did not supply and name what grounded it. `Non-smoker` is grounded in the count; `Employed` is grounded in `at work`; `Works manual labor` is grounded in nothing and fails. Issue #29.

**The allergy limbs are checked the other way round, from the shorthand in rather than from the template out**, and that is why they had to be written rather than left to the walk above. Every limb already in this row is satisfiable by reading the note alone — a slot either carries a value or it does not. **A dropped allergen is invisible in the note**: the box reads `NKDA`, the value is present, it is not a hedge, it is declared, and the row passes on every other limb it has. So the check starts at the input — list every allergen the shorthand names, then name which box line carries each one and what kind it was called. Then read the FILLED line against the same list and check it does not deny what the list holds. **This is the one row whose walk needs the shorthand open beside the note.** Issue [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96).

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

**A second narrowing landed on 2026-08-17 and it is the mirror of the one below.** The zero's carve-out removes the *no anchor* exit; the height's leaves it and adds to it — a filled height's line **names the age and the sex** as well, because both are given on all but one committed input and a value with two anchors available is not one the encounter supplied nothing for. So `no habitus or percentile datum in the source to move it` still passes and no longer passes *alone*. **Ruled by the clinician**, with the pressure bar beside it, and both are settled by `python tools/filled_vitals_census.py`. The argument is in *Two of these are graded now* above. Issue #97.

**The one exception was added later and it narrows that exit rather than widening the row.** A filled `0/10` pain score may not say the encounter supplied no anchor, because for a zero *nothing anchored this* and *I looked for a pain source and found none* are the same sentence — the admission that passes everywhere else is indistinguishable here from not having looked. So the zero's line names the search. The argument is in *a filled 0/10 may not take drift row 19's no anchor exit* above, and the reason it is load-bearing is that a filled `0/10` owes the Plan nothing under drift row 15: this line is the only check on it that happens after the value is chosen. **Ruled by the clinician on 2026-08-15**, and asked for rather than assumed — a row narrowed by the pass implementing #59 would have been that ticket's own defect committed inside its fix. Issue #59.

**Nothing in this repo fixtures that limb**, and it is stated here rather than left to be found. A legitimate filled zero needs a complaint that does not hurt in an encounter with no pain source, `fixtures/day-b` holds none — B8 and B14 forbid all three of its invented severities a zero — and [fixtures/README](../../fixtures/README.md) forbids authoring one. [#138](https://github.com/mshamblin5150-code/clinical-skills/issues/138).

**Row 20 is appended for the reason rows 14 through 19 were. Append, never insert.** Its natural neighbor is row 13, which is the other row about codes, and it sits at the bottom instead.

**It is the first row whose failures were all compliant when they happened**, which is a different thing from rows 17 and 18's *the prohibition was already in the file*. Here there was no prohibition and no permission. One run over twelve encounters produced **three** behaviors on one decision — six notes refusing the `E66`/`Z68` family in a written block, two silent about it, one writing `E66.3` with `Z68.26` into `Final diagnosis` — and every one of them was consistent with what this file said, because this file said nothing. **A run cannot be graded against silence**, so the row exists to end the silence rather than to catch a defect the old text forbade.

**Its two limbs fail in opposite directions and a note can only fail one.** Withholding the family is the six-note behavior; writing it as though the height were measured is the one-note behavior. The pass is the narrow thing between them — write the code, verify it, say what it rests on — and a row with only the second limb would have scored six refusals as passes.

**Check it by reading the two diagnosis fields against the FILLED block.** For each code, find the value it rests on and ask whether that value appears in the block. If it does, the note owes a line naming the filled inputs; if it does not, the code needs nothing. **Then check the codes themselves against the code set** — `python tools/icd10_lookup.py <every code>` — because this row's *verified* limb is the one that costs nothing to claim and a command to establish.

**Its two carve-outs are narrow and neither is a general escape.** A pediatric `Z68.5-` is exempt from *verified* because the database holds the codes and not the CDC charts, so the band genuinely cannot be looked up — it is `verify this number` on the recall rule, and [#123](https://github.com/mshamblin5150-code/clinical-skills/issues/123) closes it. And a code withheld on a **coding-guidelines** ground is outside the row because nothing here encodes those guidelines: whether a `Z68` should be assigned at a *normal* BMI, with no reportable condition under it, is the open question `fixtures/filled-anchor` names when it keeps cases 2 and 3 out of A3. **Neither carve-out reaches provenance.** *This value was filled* is never a reason to withhold, and a run citing one of these to hold back an `E66.3` has used a guidelines exemption to do a provenance refusal. Issue #46.

**Row 21 is appended for the reason rows 14 through 20 were. Append, never insert.** Its natural neighbor is row 4, whose defect it exists to catch, and it sits at the bottom instead.

**It is row 20's position rather than rows 17 and 18's, and the difference decides what the row had to bring with it.** Those two made walkable a prohibition the file already carried — a hedge was banned, a given passes through unchanged. **Nothing anywhere required a `FILLED·proposed` item to reach the note body.** No skill rule said it, no drift row scored it and no fixture row scored it, so a note could generate a Plan item, write it into the block, omit it from the Plan and be wrong about nothing this file had written down. **A run cannot be graded against silence**, which is row 20's own sentence — so the row arrives alongside a new paragraph under *Emit the tier block* stating the rule, rather than pointing at one already there.

**It is not row 18 widened, and the two rows have opposite subjects.** Row 18's subject is a **given** order — something the clinician did, which the note must carry. Row 21's is a **generated** proposal — something this skill contributed, which the note must actually contain rather than merely list. A note can carry every given order and still promise itself a counseling line it never wrote, and it reads as a pass on row 18 because nothing the shorthand ordered went missing. Widening 18 would also redate what `GIVEN 1/1` means in `fixtures/day-b`, which is the cost *append, never insert* exists to avoid.

**It is checked by counting, and what is counted is proposed items.** Take the `FILLED·proposed` block, number it, and name where each item landed in the finished note. An item that landed nowhere was dropped. That keeps the row a comparison of two integers, which is what rows 2, 16 and 18 rely on and what makes a false self-report impossible to argue about.

**Its quiet failure is a note that grades itself as compliant.** One run wrote `FILLED·proposed  Nutrition and activity counseling for the overweight body mass index`, wrote no weight, nutrition or activity line in the Plan, and then reported drift row 4 as a pass on the ground that the BMI *"is addressed with counseling and confirmed measurements at follow-up."* Its Assessment carried a matching sentence, so the claim had a real string behind it at every level except the one that acts. **The same run wrote the line correctly six times** on six other encounters, so this is not the skill being unable to write it — it is one note claiming a line its neighbors wrote and it did not.

**Row 22 is appended for the reason rows 14 through 21 were. Append, never insert.** Its natural neighbor is row 13, which is the other row about the differential, and it sits at the bottom instead.

**It is not row 13 widened, and the two rows fail on different objects.** Row 13's subject is the **code**: does a code whose descriptor names a confirmed organism or disease sit on a diagnosis the encounter did not establish. Row 22's is the **label**, and a note can pass row 13 perfectly while failing this one — `Contiguous osteomyelitis of the right tibia or fibula - M79.604 Pain in right leg` assigns no over-claiming code anywhere and still puts a disease nobody established at the head of an entry. **Row 13 was already satisfied by all three of the renderings issue #68 was filed over**, which is exactly why a second row was needed rather than a wider first one.

**Its slot limb is the mechanical one and it is the one that was reachable.** `tools/differential_scan.py` is that limb made runnable, on `tools/specificity_scan.py`'s terms and for its reason — see *Naming a differential entry* above for what the three renderings did and did not require.

**The scanner reaches the slot limb and neither of the other two.** Naming needs a reader who can compare a label to a descriptor, and paraphrase is permitted — `Shortness of breath - R06.02` and `Mild dyspnea - R06.02` are both correct. **Collapse needs one too**, and for a harder reason: deciding that two refusals rest on *one* documented finding is a clinical judgment about the encounter, not a string comparison, and a note that split them across two findings may be right to have done so. **So one limb of three is machine-checked and a clean scan is not a walked row** — which is `filled-anchor`'s **R2** residue arriving on a different rule, and the reason this sentence sits next to the command rather than in a footnote.

**Row 23 is appended for the reason rows 14 through 22 were. Append, never insert.** Its natural neighbor is row 13, whose two undefined terms it exists to remove, and it sits at the bottom instead.

**It is not row 13 widened, and the two rows fail on different objects.** Row 13's subject is the **code** — is there one on every entry, and does any of them overstate what the encounter established. Row 23's is the **shape**, and a note can pass row 13 while failing this one: a prose paragraph carrying no diagnosis-shaped line owes row 13 nothing to count, which is precisely how `day-b` run 2's case 11 was scored. **Row 13 could not be failed by the thing it was written to catch**, because the run chose the denominator. That is why the shape became a row rather than a clause.

**And a run that fails row 23 has not been graded on row 13**, which is the ordering to record when both are walked. An unnumbered differential leaves row 13's *two counts that either match or do not* resting on which grader read which line as an entry, so a `13 pass` beneath a `23 fail` is a verdict about nothing. Write the row-23 FLAG and say row 13 was not reachable, rather than reporting a pass on a count nobody could make. [#70](https://github.com/mshamblin5150-code/clinical-skills/issues/70).

**Row 24 is appended for the reason row 23 was, and it is not row 21 widened.** Row 21 asks whether every `FILLED·proposed` item landed somewhere in the body — two counts, and a note that wrote all of them passes. Row 24 asks a question about the same items that counting cannot reach: **was the number in it looked up or recalled.** Case 10's nine-item screening list passes row 21 outright. Every item was in the Plan, every one was in the block, and not one had been checked against a sheet that holds three of them.

**Its quiet failure is a note that reads better for having failed.** A recalled threshold and a cited one are the same sentence in the body — that is what *Block only* guarantees — so the only place the difference shows is the block, and a note that simply omits the tail looks tidier than one carrying `needs: 10-year risk not calculated`. **The row is failed by an absence that improves the document**, which is the shape rows 12 and 19 also have and the reason none of them survives being skimmed for.

**Nothing checks this row, and that is worth stating rather than leaving to be found.** `tools/differential_scan.py` reaches one limb of row 22 and nothing else — **not row 23 either**, whose `malformed slot pins` count is scoped to the conclusion line that row exempts. So rows 23 and 24 both go unchecked, and every limb of this one is walked by a reader today. This sentence said the scanner reached a limb of each; it does not, and the tool's own docstring said so while this file claimed otherwise. The mechanical limbs are there to be built — a tail is a string on a line and the sheets are greppable — but until something exists, *a clean read is the only read there is*.

**And no scanner ever built for it will reach the limb that matters.** Whether a correctly extracted recommendation applies to the patient in front of the clinician is a clinical judgment, and the citation exists to put the population where a reader can rule on it — never to rule on it. A row that scored applicability would be asserting exactly the thing this whole section is arranged to avoid asserting. Issue [#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85).

**Counting is why this is a row rather than a requirement to quote the evidence.** The live alternative was to make row 4's verdict quote the Assessment or Plan words carrying each filled abnormal, and it fails on the case above: *"Addressed with nutrition and activity counseling at the primary care follow-up"* is a real sentence in that note, quotable, and false. **The most rigorous-looking check does not catch the most recent recurrence, because the false sentence is already inside the note.** Two integers do not have that problem. The clinician ruled on 2026-08-15. Issue [#47](https://github.com/mshamblin5150-code/clinical-skills/issues/47).

**It reaches wider than the defect that produced it**, which is the other half of why counting was chosen: the row is about any proposed item the note generates and drops, not the weight ones alone. A dropped swab, a dropped referral and a dropped return-precaution line all fail it on the same two integers.

**Row 12 is checked by reading the body without the block.** Every other row asks whether the note said enough; this one asks whether it said something only the tier block may say. The two failing shapes are a parenthetical that labels its own line — `(inferred)`, `(dose given; duration filled)` — and a sentence that accounts for the note's own content, such as what was not reconciled or what must be confirmed before entry. Both read as diligence, which is why they survive a reading that is looking for omissions.

**A word search is the wrong instrument here** and will produce false hits on any note written well. *The tier language stays out of the note* carries a test for each half: ask of every occurrence of the six words whether it would still be there had the shorthand supplied every line, and ask of every candidate sentence whether it reports something about the patient or defends the note. Record which way each one resolved.

**Row 13 fires on every note, which is what makes it easy to stop reading.** A differential is generated in 100% of encounters and a hedge token appears in the shorthand of far fewer — **33 of 551 encounters, 6%, re-derived 2026-08-15** with `tools/corpus_census.py`. Treat that as a **proxy rather than a bound**: it over-counts, because some of those tokens hedge a history rather than a diagnosis, and it under-counts, because the shorthand hedges in ways the token list does not reach. **Issue #19's original figure was about 6% across 559**, measured 2026-08-11 — earlier the same day as `da6f791`, *"stop the census double-counting a shift"*, which taught `read_corpus` to drop byte-identical day files. Reading the directory without that dedup still returns 559 encounters and 34 hedges today, so **the rate is unchanged and the denominator is what moved**. That is also why this number is quoted with its date: the corpus did not grow, the counter got more careful. What the ratio establishes is only its direction: the first half of this row is checked far more often than the second, and a row that passes twenty times running is a row that starts getting a verdict without being walked. Count the entries and count the codes; they are two numbers and they either match or they do not.

**They were two numbers only once *entry* was defined, and it took a ticket to notice.** [#70](https://github.com/mshamblin5150-code/clinical-skills/issues/70) was filed because this row promised two counts and never said what it was counting, and the recorded digit turned on an unstated choice on two separate runs — a paragraph read as one thing or as three, a headed block read as inside the differential or outside it. **A binary row with an undefined unit is not binary**, it is a reader's judgment wearing a ratio's clothes. The definition now sits in the row itself and in *The shape of the differential* above; row 23 is what makes the unit countable in the first place.

**Its second half needs the descriptor read, not the diagnosis.** `probable viral URI` coded `J06.9 Acute upper respiratory infection, unspecified` passes — the descriptor says *unspecified* and asserts nothing the note lacks. The same hedge coded `U07.1 COVID-19` fails, because that descriptor names the organism and the note says nobody swabbed. The failing shape is narrow and it is always the same one: an organism-specific or disease-specific descriptor on a diagnosis the encounter never established.

**And it does not stop at the entries the note rejects.** `probable viral URI` is usually the note's *conclusion*, not something argued against, and it is the case this rule was written for — so the row reaches the favored entry and the final diagnosis on exactly the same terms. A row scoped to the rejected entries alone would pass the headline example. The rule itself, and what to propose instead, live in [icd10-cpt](../icd10-cpt/SKILL.md). Issue #19.

**Row 15 is row 1 read in a mirror, and it is checked by asking what the note declined to do.** Row 1 exempts filled vitals from tracing to a given, because they have to be allowed to exist. Row 15 refuses them that exemption, because they must not be allowed to reassure. Every other row reads what the note contains; this one reads what it decided against. Take each plan decision that withholds, defers or narrows the workup of a documented finding — no imaging, no culture, no referral, watchful waiting — and name what it rests on. Anything resting on a generated number fails. **An obligation that never arose is not a discharge**, which is where a filled 0/10 sits; see the paragraph splitting row 4's direction from this one.

**It survives a careful reading, which is why it needs a row.** A note that declines a test on a plausible normal is fluent, internally consistent and clinically persuasive; there is nothing in it to notice. The FILLED block carrying both numbers is not enough on its own, because the block is read once before submission and the body is what gets reasoned from — on issue #27 it was the clinician himself who was persuaded.

**Walk it only over tests the encounter did not order, and check that scope before walking.** A run that deleted a given order and then answered this row about it will pass — it lists what its refusal rested on, finds only given findings there, and records a pass, which is exactly what happened on the run row 18 was written from. **The absence it is reasoning about is its own.** So take the plan line first, per row 18, and any test on it is outside this row's subject however well the note argues against it.

**Row 8 is worth a second look even when the age is given.** The clinician's own record puts an 82-year-old on `Adult`, and misses the gyn/obstetric override on every opportunity it has had. A stated age is not the same as a correct band.

Row 2 carries the most weight and is the easiest to skip, because a drifting note reads perfectly well. Take each abnormal from step 2's expansion in turn and name where it lands. An abnormal that lands nowhere is either a diagnosis missing from the Assessment or a problem missing from the Plan — say which.

A failing row is written as a **FLAG** in the tier block, never quietly repaired into a pass. That is what FLAG is for — the matrix finds the defect, FLAG is where it is recorded.

Close with `N given, N derived, N filled` and stop.
