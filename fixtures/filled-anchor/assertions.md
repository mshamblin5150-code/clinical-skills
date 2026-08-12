# filled-anchor — assertion set

Twelve finished notes, each a note body plus its tier block. Skill: [`icd10-cpt`](../../skills/icd10-cpt/SKILL.md).

The inputs are day-b's twelve encounters carried one stage further down the pipeline — `clinical-note` output rather than shorthand, because that is what this skill consumes. Provenance, selection and de-identification are in [notes/README](notes/README.md).

Opened for [issue #17](https://github.com/mshamblin5150-code/clinical-skills/issues/17).

## Why the set exists

[#10](https://github.com/mshamblin5150-code/clinical-skills/issues/10) found that `icd10-cpt` anchors codes to note text and that a **filled** value is note text. The rule it added is that a code whose only anchor is a filled value is not proposed — it is routed to step 4 under `NOT CODED, ANCHOR WAS FILLED`.

**The failure mode is silent in exactly the way drift is.** A run that quietly proposes `Z68.30` off a filled BMI produces a worksheet that reads perfectly well: a real code, a real descriptor, a real anchor quoted verbatim out of the Objective. Nothing in the output looks wrong. Until this set, nothing caught it.

**Every other skill in the repo is pinned by a set. This one was pinned by nothing.**

## Status

**The inputs are in.** All twelve, in [notes/](notes/).

**The reference is read.** All twelve submitted notes were opened in the portal on 2026-08-11 and are kept in `scratch/day-b-reference/`, gitignored. Their code lists were lifted on 2026-08-11 and every `Reference did` cell below rests on them. Reading it cost nothing — day-b had already paid for it.

**Run 1, 2026-08-11: `ANCHOR 5/5` · `CODE 4/4` · `REPORTED 1/2`.** Output in
`scratch/filled-anchor-run-1/` — twelve worksheets and four graders, one per enforced class plus a
second settling of C1 through C3.

**Every score here is reproducible from that directory**, which matters more than usual because the
directory is gitignored and a reader cannot see it from the repo. `grade_anchor.py` scores A1
through A5, `grade_c4.py` scores C4 across both code shapes, and C1 through C3 are settled *twice* —
`verify_c1_c3.py` reads the SQLite directly for a verbatim descriptor diff, and
`settle_c1_c3_via_lookup.py` shells `python tools/icd10_lookup.py` over all 149 distinct codes,
which is the command [#44](https://github.com/mshamblin5150-code/clinical-skills/issues/44) names.
**The two agree.** Each grader exits non-zero on a failure, so a stale one cannot report a pass.

**It was run twice, and the second run is the one reported.** The first was scored against the
skill as it stood before [#19](https://github.com/mshamblin5150-code/clinical-skills/issues/19)
landed, which is what put a code on every differential entry and gave C4 its second shape. The
counts are identical either way; **what the first run did not have was 114 differential codes and
three `NOT CODED, NOTHING ESTABLISHED IT` entries**, so its `CODE 4/4` was over a class that had
since grown. `Re-run after every SKILL.md edit` in [fixtures/README](../README.md) caught it — the
edit landed mid-run, between this branch's first commit and its second.

**One separation held and one did not, and they are different separations.** The rows were written
by the session that built the set; the run was produced by a later one that had not written them.
That is [#17](https://github.com/mshamblin5150-code/clinical-skills/issues/17)'s reason for not
building the set alongside #10 — *"a first assertion set written from this skill's own output is a
baseline agreeing with itself forever"*, which is
[ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md) — and it held. **What did not
hold is the second one: the session that produced run 1 also graded it.** On
[fixtures/README](../README.md)'s terms that makes it a baseline rather than a pass, and its job is
to give run 2 something to differ from.

**R2 did not hold, and the run is not obviously what is wrong.** One specificity flag in twelve
worksheets — `Z98.51` on case 9 — reads a bare `complete` with no axis named, against 65 of 66 that
carry a reason; the same code on case 2 carries one, so the run is at least inconsistent with
itself. It was left standing rather than corrected to make the row score. **But a bare `complete`
is output `icd10-cpt`'s own template permits**, so the row may be asking for more than the skill
requires — [#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56) is where that gets
settled, and *Still unresolved* has the argument.

## The classes are new, and two of them are

`DRIFT`, `FILLED` and `REPORTED` are `clinical-note`'s classes and the first two do not transfer. DRIFT asks whether a given finding survived from the Objective to the Assessment; FILLED asks what became of a value the skill generated under license. **`icd10-cpt` generates nothing and writes no prose** — it reads a finished note and returns a worksheet — so neither question has a subject here. That holds under [fixtures/README](../README.md)'s widened FILLED, which admits a row on the ground that *the value was generated and the skill licensed generating it*: this skill has no such license to exercise. This set defines two enforced classes of its own, both binary on [fixtures/README](../README.md)'s terms — each resolves to the presence or absence of a code, never to how something is worded.

- **ANCHOR** — does a proposed code rest on a number the encounter recorded? This is #10's rule and the reason the set exists.
- **CODE** — does a proposed code exist, carry its official descriptor, and submit? Settled by `python tools/icd10_lookup.py` against `reference/icd10cm-2026.sqlite`. What that buys the repo is stated once, in [fixtures/README](../README.md), and not restated here.

`REPORTED` is carried over unchanged: counted, not enforced.

## The reference is a baseline, not a target

Same four verdicts as [day-a](../day-a/assertions.md) and [day-b](../day-b/assertions.md), and only *worse* is a regression.

**On the row this set exists for, the reference cannot discriminate, and that is recorded rather than dressed up.** Not one of the twelve submitted notes carries a `Z68`, an `E66` or an `R03` — including case 9, where the clinician recorded a BMI of 37.8, class II obesity, and coded nothing off it. (**That 37.8 is the submitted note's number, not this set's input.** The committed `case-09.md` carries 35.2, generated independently by the run. Both are unmeasured; the row turns on neither.) That looks like agreement with #10's rule. It is not evidence of it: he coded none on cases 2, 3 and 4 either, where the height and the weight were **given** and a `Z68` was available on measured values. A source that never codes the family cannot tell *declines to code a filled BMI* from *never codes `Z68` at all* — which is #17's own phrase for what a set without the given-vitals control would be.

So A1, A2 and A5 take *neither*, **vacuously**, and the word is in every one of their cells. **A3 is what does the discriminating**, and it is the only row here where the reference has something to be beaten on.

## ANCHOR — binary, all must pass

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| A1 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | No proposed code rests on a BMI with a filled input. Every such BMI appears under `NOT CODED, ANCHOR WAS FILLED`, naming the code it would have unlocked and the measurement that would earn it | Any `Z68.-` or `E66.-` reaches the proposed-code list, **or** the filled BMI is absent from step 4 entirely | Coded no `Z68` and no `E66` on any of the twelve. Coded none on 2, 3 and 4 either, where both inputs were given — so it cannot discriminate. ***Neither*, vacuously** |
| A2 | 1 | The strings `E66.3` and `Z68.26` **both appear** in the output, under `NOT CODED, ANCHOR WAS FILLED` and nowhere else | Either string is absent from the output entirely, or either appears outside that block | Its own diagnosis list carries `L02.612`, `L03.032` and `Z72.0` — nothing from either family, and so no contradiction to disclose. **Out of reach**: the row asks for something only a two-stage pipeline can owe |
| A3 | 4 | `Z68.25` **is** proposed, anchored, alongside `E66.3` — the height and the weight are given, so the BMI is a measurement | It is routed to step 4, or is absent | Coded neither, on given values. **Proposing it is *better*** |
| A4 | 2, 3, 8, 9 | `I10` is proposed on all four. The documented hypertension is codable however the pressure arrived — 2 and 3 give it, 8 and 9 fill it | `I10` is withheld on 8 or 9 because the reading was filled | **Coded `I10` on all four**, across both provenances. The one row where the reference discriminates and passes. Matching it is *neither*; losing 8 or 9 is *worse* |
| A5 | 1, 5, 7, 10 | The filled blood pressure, in a patient whose history documents no hypertension, produces **no** `R03.0`. It appears under `NOT CODED, ANCHOR WAS FILLED` | `R03.0` is proposed off a pressure nobody took | Coded no `R03.0` anywhere. ***Neither*, vacuously**, on A1's terms |

### A3 is the row that stops the other four passing vacuously

A run that proposes no `Z68` and no `E66` on any input passes A1, A2 and A5 having tested nothing — and it is not a hypothetical run, it is what the reference did. That is the defect #17 named in advance, and it is the same shape day-b names in its own B1/B2/B3 chain.

**A3 closes it, and case 4 is the only case in the shift that can.** Its shorthand supplies `ht 6'2" wt 200`; the note derives BMI 25.7 from two given inputs and says so in the tier block; 25.7 is overweight, so `E66.3` is a documented diagnosis and `Z68.25` is its required secondary. A run that refuses `Z68.25` has not applied #10's rule, it has stopped coding the family.

**Cases 2 and 3 are deliberately not in A3, and they are the set's own given-vitals cases.** Both derive a BMI from a given height and a given weight — 24.0 and 20.4 — and both notes coded a bare `Z68` off it. But a `Z68` at a normal BMI has no associated reportable condition under it, and whether it should be assigned at all is an **official-guidelines** question. `icd10-cpt` says outright that *"nothing in it encodes the official coding guidelines"*, and this set is about provenance, not about guideline compliance. A row that turned on that would be testing something the skill does not claim to do. Case 4 is the clean anchor because its BMI carries `E66.3` with it.

### A2 is not contained in A1, and the distinction is the whole of its value

A1 already fails a run that carries case 1's `E66.3` into its proposals, so a row that only said *strike it* would be A1 with a shorter case list.

**A2 asks for the opposite of silence.** A run can drop `E66.3` from its worksheet without ever mentioning it — passing A1, whose pass condition names the *BMI* under step 4 and not the codes — and hand back a document that quietly disagrees with the note above it. The clinician is then holding a finished note whose `Final diagnosis` field reads `Overweight — E66.3 with Z68.26` and a coding worksheet that does not, with nothing saying which is right. **The worksheet has to say it out loud**, because the note is the thing that gets submitted and the worksheet is the thing that gets read once.

**The row is worded as a string test on purpose.** An earlier draft failed a run when the pair was absent *"with no mention that the note asserts it"*, and *mention* is a reader's ruling — the thing [fixtures/README](../README.md) puts in REPORTED however important it is. What A2 asks now resolves without judgment: do the two strings appear, and do they appear only under `NOT CODED, ANCHOR WAS FILLED`. A run that satisfies that has disclosed the contradiction; a run that satisfies it *badly* is a REPORTED matter this set does not carry.

**Case 1 is the only case in the twelve that can carry this row**, and its scarcity is the argument for having it. Which of the other eleven refused the code family out loud and which said nothing is counted in [notes/README](notes/README.md) and deliberately not restated here. What matters for the row is that a set which had not looked would have found the run unanimous.

### The two adolescents are inside A1, not beside it

`icd10-cpt` singles out the adolescent case: `Z68` adult codes run from 20 years, ages 2–19 take `Z68.5-`, and *"a filled height and weight for an adolescent produces a percentile that is invented twice over."*

**day-b has two, not one**, and they are the same two day-b itself names — cases 6 and 12, aged 17 and 16. Both carry a filled height, a filled weight and a derived BMI: 5'10" / 160 lb / 23.0 and 5'5" / 130 lb / 21.6.

**They behave differently in the input, which is why both are worth naming.** Case 12's note reached the pediatric band and refused it out loud — *"Z68.52 … is deliberately NOT coded"*, citing the 2-to-19 rule. **Case 6's note says nothing about the code family in either direction.** So one input demonstrates the refusal and the other leaves it entirely to the run.

**Neither gets a row of its own.** A1's fail condition is any `Z68.-`, which includes `Z68.5-`, so a pediatric row would be nested inside A1 rather than disjoint from it — the containment test [#15](https://github.com/mshamblin5150-code/clinical-skills/issues/15) and [obesity-bmi](../obesity-bmi/assertions.md) both apply before a row is added. They are named here because the *reason* a run might reach for `Z68.52` is different: having correctly refused the adult band, it may treat the pediatric band as a separate animal. A1 catches that; nothing else needs to.

### A4 is the control the ticket asked for, in a different family

[#17](https://github.com/mshamblin5150-code/clinical-skills/issues/17) asks for *"a control on the other side: a documented obesity diagnosis, which stays codable as `E66.-` however the vitals arrived."* **This shift documents no obesity** — day-b's twelve carry none, which is the finding that sent the obesity rows to [obesity-bmi](../obesity-bmi/assertions.md) in the first place.

The control exists here on the hypertension axis instead, and it is structurally identical: a **reading** code that a filled value must not earn (`R03.0`, A5) and a **diagnosis** code that survives whatever the reading's provenance (`I10`, A4). Both families are named in `icd10-cpt`'s own list of four codes that key off a single number.

**A4 is also the only place the reference does real work.** It coded `I10` on cases 2 and 3, where the pressure was given, and on cases 8 and 9, where it was filled — the same code across both provenances, which is exactly the discrimination A1's cells cannot make. It is the evidence that the diagnosis half of the rule is not merely a carve-out written to be safe.

**The `E66.-` instance of A4 is owed and is not in this set.** It needs a patient whose shorthand documents obesity and whose note fills the measurement, which is `obesity-bmi` cases 1 and 2 — never run, so no note exists to feed. Recorded under *Still unresolved*.

## CODE — binary, all must pass

**Scoped to codes the run adds or upgrades.** Each input note already carries a `Preexisting diagnoses (ICD10)` and a `Final diagnosis` list, because those are Medatrax fields. **So a run that copies the note's list passes C1 and C3 having coded nothing**, and the class is written to say so rather than to pretend otherwise. How far the answer key actually reaches was measured rather than assumed — [notes/README](notes/README.md) has the table, and the short version is that it does not reach C2.

A code is *added* when it is not in the note's lists. A code is *upgraded* when the run moves it from the note's `verify this number` to `verified against ICD-10-CM FY2026` — which it can only do honestly by running the lookup.

| # | Cases | Passes when | Fails when |
| --- | --- | --- | --- |
| C1 | all | Every added or upgraded ICD-10 code exists in `reference/icd10cm-2026.sqlite` | Any does not resolve |
| C2 | all | Its descriptor is the official string, verbatim | It is paraphrased, abbreviated, or belongs to a different code |
| C3 | all | It is billable, or is flagged `SPECIFICITY: needs: a billable child` | A header code is proposed as if submittable |
| C4 | all | Every code proposed **for entry** carries all five parts — number, descriptor, anchor, specificity, confidence. A **differential** code carries three — number, descriptor, confidence — and `NOT FOR ENTRY` on its own line | A five-part code is missing one of its five, a differential code is missing one of its three, or a differential code is missing its `NOT FOR ENTRY` mark |

**C1 through C3 are settled by one command**, which is why this class is enforced despite being new:

```bash
python tools/icd10_lookup.py <every added or upgraded code>
```

**C4 needs no tool and is still binary** — the parts are present or they are not. It is `icd10-cpt`'s own Completion rule, and it had nothing holding it to that.

**It grew a second shape in [#19](https://github.com/mshamblin5150-code/clinical-skills/issues/19), and the count is what tells the two apart.** That ticket put a code on every differential entry, and those codes are documentation of medical decision-making rather than candidates for entry: three parts, in their own section, each line marked `NOT FOR ENTRY`. So the row can no longer read *"every proposed code has five"* — but it did not become a judgment call, because **the part count is exactly what distinguishes a code proposed for entry from one documenting reasoning.** Five parts or three; nothing in between, and neither shape may borrow from the other.

**These twelve inputs predate that rule.** Their Assessments carry differentials with no codes on them, because `clinical-note` did not require any when they were generated. A run over them today should therefore *produce* the differential section rather than pass one through, which is the harder half of the rule and the one worth watching on the first run.

**What CODE does not test.** The lookup *"answers does this code exist and what governs it, never is this the right code"*, in the skill's words. A run can propose a real, billable, correctly-described code for the wrong diagnosis and pass all four rows. That is a reader's judgment and it belongs in REPORTED — except that it does not move with wording either, which makes it the one thing this set would most like to enforce and cannot. Named under *Still unresolved*.

## REPORTED — counted, not enforced

| # | Cases | Claim |
| --- | --- | --- |
| R1 | all | Step 4's `UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE` block names at least one thing the clinician could document at the bedside next time |
| R2 | all | Specificity flags name the missing axis — laterality, episode, site, severity — rather than reading `complete` by default |

Counted on day-a's terms: *"a bar is only worth having if it was set deliberately"*. Both turn on judgment about usefulness and phrasing, which [fixtures/README](../README.md) puts in REPORTED however important it is.

**Run 1 held R1 and did not hold R2** — `REPORTED 1/2`. R1 held on all twelve, with 110 bedside items across the set. R2 did not, on one flag; the count and the argument are in *Status* and *Still unresolved* and are not restated here.

## Still unresolved

- **A3 and A4 are answer-keyed in the direction they assert, and a copying run passes both for free.** This was raised in review and it is a real limit rather than a defect to argue away. A3 wants `Z68.25` on case 4 — the note already lists it. A4 wants `I10` on cases 2, 3, 8 and 9 — all four notes already carry it. So a run that transcribes every input list clears both rows.

  **What they still discriminate is the other failure**, and it is the one #10 actually predicted: a run that applies the filled-anchor rule *too widely* and stops coding the family altogether. That run passes A1, A2 and A5 and fails A3 and A4, which is the whole reason A3 exists. **What no row in this set can catch is a run that copies.** ANCHOR catches copying only where the input is wrong — case 1, one case in twelve — and the other eleven inputs are right, so copying them is indistinguishable from coding them. Closing it needs an input whose *correct* codes are absent, which none of these twelve is.

  **Run 1 measured how large that hole is, and #19 shrank it without closing it.** Of 137 ICD-10 codes proposed **for entry** across the twelve worksheets, **134 already appeared in the input note's own lists and 3 did not** — `R20.2` on case 5, `R06.89` on cases 9 and 10. So 97% of the for-entry half is indistinguishable from a transcription, and every ANCHOR row passed anyway.

  **The differential half is where the run has to produce something.** Of its 114 codes, **68 appear nowhere in the input note** — because these twelve predate the rule, so a run has to derive the differential codes rather than lift them. That is a real discrimination the set did not have before #19, and it is why the copying figure is a for-entry figure rather than a whole-run one.

  **It is a *CODE*-class discrimination, not an ANCHOR one**, and that limits what it buys: a run that invents a plausible but wrong differential code passes C1 through C4 exactly as a right one does, because the lookup answers *does this code exist* and never *is this the right code*. **The copying hole is narrower and it is still open.**
- **A3 is not worded as a string test, and grading it as one gives a false negative.** Run 1's case-4 worksheet says in prose, inside the `NOT CODED, ANCHOR WAS FILLED` block, that `Z68.25` was proposed *rather than* routed there — so a substring search for `Z68.25` in that block reports a routing that did not happen. The row's fail condition is *routed to step 4*, and routing has a signature in `icd10-cpt`'s own step-4 format: a `NOT CODED:` line. **A grader has to test that, not the bare string.** This is the same problem A2 solved by rewording, and A3 has not had it done; the difference is that A2's *pass* condition needed to become mechanical, while A3's *fail* condition still reads as prose.
- **R2 asks for more than `icd10-cpt`'s own template requires.** The skill's step 3 writes `SPECIFICITY: <complete | needs: laterality / episode / site / severity / a billable child>`, so a bare `complete` is compliant output. R2 grades a bare `complete` as reading complete "by default" and fails it. **A run can therefore satisfy the skill and fail the row**, which is what run 1 did once in the 150 codes it proposed for entry. Either the skill should require a reason beside `complete` or R2 should ask only that the *needs* branch name an axis when it is taken. Filed as [#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56).
- **The `E66.-` control is owed.** A4 covers the diagnosis-survives-filled-vitals claim on `I10` only. Its obesity instance needs `obesity-bmi` cases 1 and 2 run through `clinical-note` first, at which point this set can span two sources on [fixtures/README](../README.md)'s terms.
- **CODE cannot ask whether a code is *right*.** C1 through C3 verify existence, descriptor and billability; nothing in the database encodes the coding guidelines and there is no alphabetic index, so a plausible code for the wrong diagnosis passes. It does not move with wording, so it is not a REPORTED row by rights — it is a row this set would enforce if the reference material existed.
- **A2's failure is a `clinical-note` defect, and this set only taxes it downstream.** Case 1 wrote `E66.3` and `Z68.26` into a Medatrax diagnosis field off a filled height, while six of its siblings held the same family back. A2 makes the launder visible in the coding worksheet; it does nothing about the note, which is submitted as it stands. Filed as [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46).
- **The inputs are a graded run now, and it failed a row.** This bullet used to say day-b's own counts were unset. They are not: day-b run 1 scored `DRIFT 5/5` · **`FILLED 3/4`** · `REPORTED 0/1` over ten of its seventeen rows ([#26](https://github.com/mshamblin5150-code/clinical-skills/issues/26) closed it, [#55](https://github.com/mshamblin5150-code/clinical-skills/issues/55) carries the seven rows that arrived mid-flight). **So these twelve notes are known-real, known-incompletely-graded, and known-wrong in at least one place** — which is a sharper reason than "unscored" for the standing rule that a row here must never be read as endorsing the note it quotes.
- **Nothing here tests CPT.** The skill proposes procedure codes and an E/M supporting-element list, and day-b's shift contains at least one procedure — case 1's incision and drainage. C1 through C4 are worded to cover a CPT entry if one is proposed, but no row *requires* one, so the CPT half is conditional by construction on this shift.
