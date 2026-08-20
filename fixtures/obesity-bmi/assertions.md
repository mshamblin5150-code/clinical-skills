# obesity-bmi — assertion set

Four encounters carrying a documented obesity or a bariatric history and **no body measurement at all**, drawn from three day files. Visit dates and sites removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

**No year is claimed for the set**, unlike day-a, day-b and peds-bp. Three of the four come from dated clinic files, 2026; case 2 comes from a **backlog**, where the file's own date bounds the encounter from above and does not date it. A single year across the four would be an assertion about case 2 that nothing supports.

This set opened for one thing day-a, day-b and peds-bp cannot test: **what the skill does with a BMI it invented for a patient whose history says what that BMI ought to look like.** Its third case now carries a second ruling too: [issue #138](https://github.com/mshamblin5150-code/clinical-skills/issues/138)'s legitimate filled `0/10`.

Opened for [issue #15](https://github.com/mshamblin5150-code/clinical-skills/issues/15).

## Why the set is not a day

day-a and day-b are whole shifts; peds-bp is part of one. This is neither — its four cases come from three different day files, because the shape is rare enough that no single day holds two. [shorthand/README](shorthand/README.md) carries the numbering consequences and the substitutions.

**It is not a sample of that shape. It is the whole of it** — every encounter in the corpus that writes the word and supplies no body measurement is in here, so there is no larger version of this set to be had without new day files.

**The counts are in [shorthand/README](shorthand/README.md) and deliberately not restated here**, on day-b's terms: a figure written in two places is a figure that goes stale in one of them. This set already lost one that way — an earlier draft quoted the pre-`lobes`-fix anchor count in a test docstring, and it survived the correction because nothing recomputes prose.

## Status

**The inputs are in.** All four encounters are in [shorthand/](shorthand/), one file per case, de-identified.

**The reference has not been read.** day-b's rule stands here for the reason it stood there:

> **Until it is read, no drift row may be added to this set.**

That rule earned its keep twice. Four of day-a's six DRIFT rows changed when its reference was finally read, and day-b's reference **reversed** one — the submitted note had addressed the finding a row was about to claim it abandoned. Every row below is anchored on the **input** and on the run's own output, both readable before any portal is opened.

**The set has never been run.** `FILLED n/n` has no first value yet. O6 and O7 each carry a targeted `PASS` read from the committed blind-run output; those two verdicts are not a scorecard and do not turn that output into a run.

## The ruling this set enforces

Settled on [issue #15](https://github.com/mshamblin5150-code/clinical-skills/issues/15), 2026-08-11.

day-b's B2 was rewritten the day before, on [#14](https://github.com/mshamblin5150-code/clinical-skills/issues/14), and stopped demanding an abnormal value: a treated hypertensive at 124/78 is the treatment working, not an implausible reading. **What B2 forbids now is a normal value the note gives no account of.** The open question #15 carried was whether the body-measurement half needed an analogue of that, or whether day-b's B3 already contained one.

**It does not contain one, and the two rows are disjoint rather than nested.**

- **B3 fires only when the value lands abnormal.** It asks what happened to it downstream.
- **The analogue fires on the *normal* branch** — a patient the shorthand calls obese, handed a BMI of 24, with nothing said about how she got there. There is no abnormal value for B3 to have lost, so B3 passes having tested nothing.

Neither row reaches the other's case. **The gap #15 described is real; what was wrong was its diagnosis of why.** The ticket held that no case could anchor the row because a row demanding an obese BMI from a documented diabetic would be ordering up an invented abnormal finding. True — and the same objection retires under new-B2's shape, which demands no value at all. What the row actually needed was a patient whose history documents obesity itself, and day-b's twelve have none.

**The corpus has two.** They are cases 1 and 2.

### Why the row is not drift-class

Obesity written in the shorthand is a **given**, and a given finding reaching the Assessment is what the DRIFT class already asserts — so a row reading "the documented obesity must be named" would be a drift row wearing a FILLED badge, and the unread reference forbids it besides.

**O2 is anchored on the number the skill invented, not on the finding the clinician wrote.** It consults the Assessment only to resolve its second exit, the way B2 does. The drift-class row about these cases — does a documented obesity survive into the Assessment at all — is listed under *Still unresolved*, to be promoted with the reference or not at all.

### The two anchors are not the same anchor

**Case 1's `is obese` is present tense**, sitting in the exam line for a 41-year-old with PCOS. Its second exit is very nearly dead: there is no reading of that shorthand on which a BMI of 24 is the right answer.

**Case 2's `obesity` sits in a history list** — `hx anxiety, htn, restlessleg, obesity, copd` — where it could as easily be a condition carried forward as one observed today. That is where the second exit does real work, and it is why the row has one.

### Cases 3 and 4 are controls, not anchors

A lap band or a gastric bypass documents a **past** obesity and claims nothing about the present one. That makes them the place a sub-30 BMI is both plausible and accountable.

**They are the *candidate* for day-b case 2's job, not yet the equivalent of it.** Case 2 is proof the passing form is writable because its reference was **read**: a given 121/61 next to an Assessment reading `HTN, controlled (I10)`. This set's reference is owed, so all cases 3 and 4 establish today is that a patient exists for whom the passing form *would* be the right answer. They become the proof when the reference is read, and not before — the distinction matters because a set that claims a worked precedent it does not have is exactly what an unread reference produces.

**So they carry no O2 row.** Nothing in their shorthand forces the BMI either way, and a row that pushed it would be demanding an invented value in one direction or the other. They carry **O5** instead, which forbids something else entirely — see below.

## FILLED — binary, all must pass

The rows use the same class and same bar as day-b's. Each resolves to a value, a threshold, or the presence of a string; none moves with wording.

| # | Cases | Passes when | Fails when |
| --- | --- | --- | --- |
| O1 | 1, 2, 3, 4 | All four Medatrax vital fields hold a value — blood pressure, respiratory rate, height, and **BMI derived from a filled height and a filled weight** — and every one is declared in the FILLED block **carrying its value**. The shorthand supplies none of them, so all four are filled on all four cases | Any is left blank, reported under GAPS, or silently omitted. A FILLED line naming the field without its value fails too. **A BMI appearing under `DERIVED` alone fails**, because it reads as computed from measurements |
| O2 | 1, 2 | The filled BMI is **30.0 or above** — *or* below 30.0 **and the Assessment** says the obesity is resolved, improved or post-surgical, or names the weight-loss intervention | A BMI below 30.0 with no such account. **An `E66` code inside a pre-existing or problem list is not an account**, and neither is weight-loss counseling attached to no statement about the number |
| O3 | 1, 2, 3, 4 | Every **filled** vital or body measurement outside the normal range for that age is named in the Assessment or the Plan | It reaches the Objective and the FILLED block and stops |
| O4 | 1, 2, 3, 4 | Where a filled BMI lands **within 1.0 of 18.5, 25, 30, 35 or 40**, the FILLED block carries a disclosure line stating **an adjacent height or weight and the BMI that value would yield** | The BMI lands within 1.0 of a band edge and the block states the value alone |
| O5 | 3, 4 | Obesity is **never stated as a given**. The word, and any `E66` code, appear only in the Assessment or Plan resting on the filled BMI — which the FILLED block declares. **The bariatric procedure itself is a given and belongs in the history** | Obesity or an `E66` appears in the HPI, the past medical history, or a pre-existing or problem code list — asserted about a patient whose shorthand documents the surgery and never the diagnosis |
| O6 | 3 | **The filled `0/10` itself is not a failure** where the complaint does not hurt and the exam holds no pain source. It **creates no Plan obligation and discharges none**: no pain-directed Plan item is required solely to make the zero pass, and the zero is not cited to withhold, defer or narrow anything. **`PASS`, 2026-08-20, on `733a396`**, a targeted scoring of case 3's blind-run output after the **clinician confirmed** the semantic judgment, rather than a run of this set | The zero itself is rejected despite both surfaces holding no pain source; the zero is used as a reason to do less; or the note is failed solely because no analgesia, pain workup or other pain-directed Plan item was added for it |
| O7 | 3 | The `FILLED·asserted` severity line **names the search**: it says what was read in the complaint and the exam and that neither held a pain source. **`PASS`, 2026-08-20, on `733a396`**, the same targeted scoring as O6 | The line takes drift row 19's no-anchor exit — `the encounter supplied no anchor` or any equivalent — or states the zero without naming both surfaces searched and the result |

### The rows are a chain, and each closes the one below it

O1 → O2 → O3 is day-b's B1 → B2 → B3 argument transposed onto the measurement half. **O4 and O5 are the two rows day-b never needed** — one because its cases never reach a BMI with a filled input, the other because none of its twelve carries a history that invites a diagnosis the shorthand never made.

**O2 alone is passable by filling nothing at all.** A run that leaves height and weight blank, or files them under GAPS, has no BMI to be obese or not, and passes having tested nothing. **O1 closes that**, and it is the row the license itself demands: *"A value is required … Something has to go in the box."*

**O1 alone is passable by filling blandly.** `clinical-note` requires a filled measurement be *"the value this patient most plausibly had … not from the middle of the normal range"*, but whether it lands abnormal is itself generated. A run that gives case 1 a BMI of 23.4 has nothing to work up. **O2 closes that**, and its threshold is the one `clinical-note` already names: *"30.0 diagnoses obesity where 29.1 does not."*

**Why 30.0 and not 25.** The documented condition is obesity, so the value consistent with the given is an obese one. A filled 27 contradicts `is obese` exactly as a filled 24 does, and owes the same account; setting the bar at "not normal" would let it through unexplained. This is the one place O2 is *stricter* than the B2 it mirrors, and the reason is that hypertension and obesity are documented differently — a pressure has a treated form that reads normal, and "obese with a BMI of 27" has no reading at all.

**O2 alone is passable without addressing anything.** A BMI of 34 satisfies O2 and can still sit in the Objective and stop — the exact defect the skill exists to catch, and the one the reference committed on day-b case 9's BMI of 37.8. **O3 closes that.**

**O2's second exit reads the Assessment and not the Plan**, which is narrower than O3 beside it and is B2's boundary rather than B3's. It is deliberate: the exit is a claim about *what the patient's obesity is* — resolved, treated, post-surgical — and that is a diagnostic statement, which is what an Assessment holds. A weight-loss item in the Plan says what will be done next and nothing about why the number came out below 30. O3 reads both because naming an abnormal is a different act from accounting for a normal one.

**O3 and O2 together are passable at exactly 30.0**, which is the cheapest pass in the set: a run that picks a height making the BMI land one tenth over the line satisfies both rows while the arithmetic rests on an invented inch. **O4 closes that, and it is O2's honesty clause.** `clinical-note` already requires the disclosure; nothing in the repo tested it until this set, because it can only fire on a BMI with a filled input and day-b's rows never had to reach one.

**O4 enforces less than `clinical-note` asks for, on purpose.** The skill file wants the disclosure to name the adjacent value *"and what it changes"* — *"5'5" gives 29.1, and the obesity workup drops."* That trailing clause is a sentence-quality judgment, and [fixtures/README](../README.md) is explicit that a row turning on phrasing belongs in REPORTED however important it is. So the enforceable core is **two numbers**: an adjacent height or weight, and the BMI it yields. A run that states both and stops satisfies O4 while falling short of the skill file — which is the right way round for a binary row, and the gap is named here rather than smuggled into a pass condition.

**O4 is conditional, and can pass having fired on nothing.** A run whose filled BMIs all land clear of 18.5, 25, 30, 35 and 40 satisfies it vacuously — the same limit `peds-bp` states outright for P6. O2 is what makes that unlikely rather than impossible on cases 1 and 2, since a BMI pushed just over 30 is precisely the cheap pass O4 exists to tax; on cases 3 and 4 nothing constrains where the value lands, and O4 may never fire on them at all.

**What no row here does is demand an abnormal number.** O2 has two exits and forbids only silence, which is the shape #14 settled and the shape standing rule 2 requires — a row ordering up an invented abnormal finding is the thing that rule exists to forbid.

### O5 runs the other way, and it is not about the number

O1 through O4 all ask what the run did with a value it generated. **O5 forbids a claim** — it is `peds-bp` P6's shape, where the cost of a license is a row saying what the license does *not* buy.

The defect it catches: a run reads `gastric bypass`, concludes the patient is obese today, and writes obesity into her history. That is an invented **finding**, from a shorthand that documents a past procedure and no present diagnosis — and standing rule 2 forbids it outright: *"No exam finding, symptom, or result is ever filled, however plausible."* The body-measurement exception does not reach it. The exception licenses a *measurement*; it licenses no diagnosis at all.

**O5 says nothing about where the BMI lands, and that is the whole of its design.** A post-bariatric patient plausibly still carries a BMI of 33, and filling one is exactly what the license asks for. A row forbidding an obese BMI on cases 3 and 4 would be demanding a normal value — the mirror of demanding an abnormal one, invented in the other direction, and it would contradict both O3 and the paragraph above saying nothing forces those cases' BMI either way.

**So the row is about provenance, not magnitude.** Obesity may appear for these two — but only downstream of the filled BMI, in the Assessment or Plan, with the FILLED block declaring the measurement it rests on. What fails is obesity presented as something the clinician documented.

**That distinction is exactly what the FILLED block exists to carry.** `clinical-note` puts it plainly: the note body is written so given and filled content read identically, so *"the FILLED block is therefore the only thing in the whole document that can tell them apart"* — and [icd10-cpt](../../skills/icd10-cpt/SKILL.md) reads it to decide which numbers a code may rest on. An `E66` sitting in a pre-existing list has no filled value under it and is indistinguishable from one the clinician diagnosed. **O5 is the row that makes that difference cost something.**

**Why the case list is 3 and 4 only.** For cases 1 and 2 obesity *is* a given, so it belongs in the history and O5 would fail a correct note. The two case lists are the contrast that makes the row legible: the same word, required in the history on one pair and forbidden there on the other, decided entirely by what the shorthand said.

**And O2's carve-out is the same idea seen from the other end.** O2 refuses to accept an `E66` in a pre-existing list as an *account*; O5 refuses to let it be written there at all. Both rest on the claim that a code in a history list asserts provenance the shorthand never supplied.

### O6 and O7 close the two limbs of #138

The ticket was filed before [the blind run](../blind-run/README.md) put these four outputs in the tree. Its comments had narrowed the route to a counts-only shortlist followed by an authorized read and a clinical judgment. **The later committed evidence makes the shortlist and the PHI-bearing read unnecessary:** case 3 is already a de-identified fixture input, writes neither a pain score nor `no pain`, and its blind-run output fills `0/10` after reading the complaint and exam and finding no pain source. On 2026-08-20, the clinician confirmed that this routine annual encounter with daytime sleepiness is a complaint that does not hurt and that its documented normal exam holds no pain source. Case 4 was not selected because its shorthand carries no exam.

**O6 pins what the zero does downstream.** It raises no pain-directed obligation, so the absence of analgesia or a pain workup is not a failure; it also discharges nothing, so spending it as a reason to withhold an otherwise owed action fails. That is drift row 15's rule on the branch #59 settled rather than its ordinary nonzero branch.

**O7 pins the disclosure that makes the choice inspectable.** For this one value, drift row 19's `no anchor exists` exit is unavailable. The line has to name both surfaces searched — complaint and exam — and say that neither held a pain source. Case 3 does that in its `FILLED·asserted` line; a bare `0/10 filled` would fail even if the note happened to choose the same number.

**Both verdicts are targeted scores, not a first run.** The output was generated on `733a396` while drift rows 15 and 19 were already in force, and this separate pass read case 3 against O6 and O7 after the clinician's confirmation on 2026-08-20. O1 through O5 remain unscored, `FILLED n/n` remains unwritten, and the blind-run README remains right to call its notes evidence rather than a scored set.

## Still unresolved

- **The set has never been run.** Until it is, `FILLED n/n` has no first value to measure drift from — and a first run graded by the pass that produced it is a baseline, not a pass ([fixtures/README](../README.md)). O6 and O7's targeted verdicts do not move that fraction.
- **The reference.** Owed, across three day files rather than one. Reading it is what would let this set carry drift rows and answer *better / worse / neither*, and it is a reconciliation rather than a query — see [fixtures/README](../README.md).
- **The drift-class row is deferred, not dropped.** Does a documented obesity reach the Assessment at all? Cases 1 and 2 are exactly where that can be asked, and the unread reference is what forbids asking it now.
- **O5 forbids the invented diagnosis and not the invented emphasis.** A run can satisfy it and still lean the whole note toward a patient it has decided is obese — filling a high BMI, ordering weight-related workup, and keeping every mention formally downstream of the measurement. That is a shape judgment, so it belongs in REPORTED, and this set defines no REPORTED rows. Stated rather than hidden, on `peds-bp` P6's terms.
- ~~**`clinical-note` still says a known hypertensive *"gets a hypertensive pressure"*.**~~ **Resolved 2026-08-11 by [#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23)**, and this bullet's forecast — *"a rewrite that touches the filled-vitals license will reach O2"* — is what happened. The rule is gone from [SKILL.md](../../skills/clinical-note/SKILL.md), replaced by *a documented condition is an anchor to reason from, never a verdict to produce*, on a corpus count: 96 encounters document hypertension and transcribe a pressure, and **39 of them are normal.** O2 turns out not to have been the analogue-free case this bullet assumed. It is **the second instance of the same rule**, and SKILL.md now says so by name: a filled value that is a documented condition's own diagnostic measure and lands normal owes an account in the Assessment, which is O2's two exits exactly, with `E66`-in-a-problem-list excluded for the same reason `I10` is. **Drift row 14** is that rule where a run walks it while writing. Nothing in this set changed — O2 was already the right shape, and what changed is that the skill file now agrees with it.
- **O3 carries drift row 4's old disjunction, and the rule underneath it has narrowed.** [#47](https://github.com/mshamblin5150-code/clinical-skills/issues/47) was ruled on 2026-08-15: *addressed* now means the **Plan** carries education, an order or treatment for the value, or the **Assessment attributes it to something the Plan is already treating** — a recheck of the value is not an address, and neither is a sentence promising a Plan item the Plan does not contain. O3 still reads *named in the Assessment or the Plan*, so **a note satisfying O3 can now fail drift row 4**, and the divergence is deliberate rather than an oversight.

  **No row is added here, on this set's own discipline.** day-b gained B15 and B16 and `peds-bp` gained P7 and P8 because the defect was **observed** in their runs — three cases across three runs in one, and case 2 in the other. **This set has never been run**, so a row written here would be authored against a defect nobody has seen in it, which is [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md)'s asserts-on-named-findings discipline and day-b's *"this file does not author rows against defects nobody has seen."* Adding two more unscored rows to a set with no first value would widen the gap and measure nothing.

  **The divergence is safe in the direction it runs.** The skill file is *stricter* than O3, so a run obeying `clinical-note` passes O3 and a run passing O3 may still fail the skill — which means O3 cannot reward the defect, only fail to catch it. **What is owed is the first run**, and whether O3 is then tightened or joined by an analogue of B15 is a decision for whoever has that output. The precedent for leaving a row looser than the rule while the evidence is gathered is B2, which sat deliberately at odds with [SKILL.md](../../skills/clinical-note/SKILL.md) until [#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23) settled it.
- **`FILLED·proposed` items are unfixtured here, and O1 is the nearest row rather than a cover.** Drift row 21 counts every proposed item against the note body; O1 counts filled *values* into the FILLED block, which is the opposite direction and a different list. All four of these cases will produce a proposed block, so the shape is available across the set — it is not written for the reason the bullet above gives.
- **Case 2's age is derived from a date of birth against a backlog file and carries ±1 year.** No row turns on it; see [shorthand/README](shorthand/README.md).
