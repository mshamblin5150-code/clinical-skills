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

**The set has never been run.** `ANCHOR n/n` and `CODE n/n` have no first value yet, and `REPORTED n/m` has none either.

That is deliberate rather than unfinished. [#17](https://github.com/mshamblin5150-code/clinical-skills/issues/17) opens by explaining why this set was not built alongside #10 — *"a first assertion set written from this skill's own output is a baseline agreeing with itself forever"*, which is [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md). Writing the rows and grading the run in one session reproduces that defect exactly. **The rows below were written from the inputs and the reference, before `icd10-cpt` was run over any of them.** Running it is [issue #44](https://github.com/mshamblin5150-code/clinical-skills/issues/44).

## The classes are new, and two of them are

`DRIFT`, `FILLED` and `REPORTED` are `clinical-note`'s classes and they do not transfer: nothing here generates a value, so there is no filled half to grade and no finding to lose between the Objective and the Assessment. This set defines two enforced classes of its own, both binary on [fixtures/README](../README.md)'s terms — each resolves to the presence or absence of a code, never to how something is worded.

- **ANCHOR** — does a proposed code rest on a number the encounter recorded? This is #10's rule and the reason the set exists.
- **CODE** — does a proposed code exist, carry its official descriptor, and submit? Settled by `python tools/icd10_lookup.py` against `reference/icd10cm-2026.sqlite`, which makes it **the only class in this repo a machine decides.** No reader is involved and two readers cannot disagree.

`REPORTED` is carried over unchanged: counted, not enforced.

## The reference is a baseline, not a target

Same four verdicts as [day-a](../day-a/assertions.md) and [day-b](../day-b/assertions.md), and only *worse* is a regression.

**On the row this set exists for, the reference cannot discriminate, and that is recorded rather than dressed up.** Not one of the twelve submitted notes carries a `Z68`, an `E66` or an `R03` — including case 9, whose BMI the clinician himself generated at 37.8. That looks like agreement with #10's rule. It is not evidence of it: he coded none on cases 2, 3 and 4 either, where the height and the weight were **given** and a `Z68` was available on measured values. A source that never codes the family cannot tell *declines to code a filled BMI* from *never codes `Z68` at all* — which is #17's own phrase for what a set without the given-vitals control would be.

So A1, A2 and A5 take *neither*, **vacuously**, and the word is in every one of their cells. **A3 is what does the discriminating**, and it is the only row here where the reference has something to be beaten on.

## ANCHOR — binary, all must pass

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| A1 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | No proposed code rests on a BMI with a filled input. Every such BMI appears under `NOT CODED, ANCHOR WAS FILLED`, naming the code it would have unlocked and the measurement that would earn it | Any `Z68.-` or `E66.-` reaches the proposed-code list, **or** the filled BMI is absent from step 4 entirely | Coded no `Z68` and no `E66` on any of the twelve. Coded none on 2, 3 and 4 either, where both inputs were given — so it cannot discriminate. ***Neither*, vacuously** |
| A2 | 1 | Step 4's entry records that **the note body's own `Final diagnosis` list already asserts** `E66.3` and `Z68.26`, so the clinician is told the note and the worksheet disagree | The pair is simply absent from the worksheet, with no mention that the note asserts it | Its own diagnosis list carries `L02.612`, `L03.032` and `Z72.0` — nothing from either family, and so no contradiction to disclose. **Out of reach**: the row asks for something only a two-stage pipeline can owe |
| A3 | 4 | `Z68.25` **is** proposed, anchored, alongside `E66.3` — the height and the weight are given, so the BMI is a measurement | It is routed to step 4, or is absent | Coded neither, on given values. **Proposing it is *better*** |
| A4 | 2, 3, 8, 9 | `I10` is proposed on all four. The documented hypertension is codable however the pressure arrived — 2 and 3 give it, 8 and 9 fill it | `I10` is withheld on 8 or 9 because the reading was filled | **Coded `I10` on all four**, across both provenances. The one row where the reference discriminates and passes. Matching it is *neither*; losing 8 or 9 is *worse* |
| A5 | 1, 5, 7, 10 | The filled blood pressure, in a patient whose history documents no hypertension, produces **no** `R03.0`. It appears under `NOT CODED, ANCHOR WAS FILLED` | `R03.0` is proposed off a pressure nobody took | Coded no `R03.0` anywhere. ***Neither*, vacuously**, on A1's terms |

### A3 is the row that stops the other four passing vacuously

A run that proposes no `Z68` and no `E66` on any input passes A1, A2 and A5 having tested nothing — and it is not a hypothetical run, it is what the reference did. That is the defect #17 named in advance, and it is the same shape day-b names in its own B1/B2/B3 chain.

**A3 closes it, and case 4 is the only case in the shift that can.** Its shorthand supplies `ht 6'2" wt 200`; the note derives BMI 25.7 from two given inputs and says so in the tier block; 25.7 is overweight, so `E66.3` is a documented diagnosis and `Z68.25` is its required secondary. A run that refuses `Z68.25` has not applied #10's rule, it has stopped coding the family.

**Cases 2 and 3 are deliberately not in A3, and they are the set's own given-vitals cases.** Both derive a BMI from a given height and a given weight — 24.0 and 20.4 — and both notes coded a bare `Z68` off it. But a `Z68` at a normal BMI has no associated reportable condition under it, and whether it should be assigned at all is an **official-guidelines** question. `icd10-cpt` says outright that *"nothing in it encodes the official coding guidelines"*, and this set is about provenance, not about guideline compliance. A row that turned on that would be testing something the skill does not claim to do. Case 4 is the clean anchor because its BMI carries `E66.3` with it.

### A2 is not contained in A1, and the distinction is the whole of its value

A1 already fails a run that carries case 1's `E66.3` into its proposals, so a row that only said *strike it* would be A1 with a shorter case list.

**A2 asks for the opposite of silence.** A run can drop `E66.3` from its worksheet without ever mentioning it — passing A1 — and hand back a document that quietly disagrees with the note above it. The clinician is then holding a finished note whose `Final diagnosis` field reads `Overweight — E66.3 with Z68.26` and a coding worksheet that does not, with nothing saying which is right. **The worksheet has to say it out loud**, because the note is the thing that gets submitted and the worksheet is the thing that gets read once.

**Case 1 is the only case in the twelve that can carry this row**, and its scarcity is the argument for having it. Cases 7, 8, 9, 10, 11 and 12 all held the same code family back explicitly — case 11 by citing `icd10-cpt` by name — and cases 5 and 6 said nothing about theirs in either direction. **One launder in twelve, in output that reads perfectly well.** A set that had not looked would have found the run unanimous.

### Case 12 is inside A1, not beside it

`icd10-cpt` singles out the adolescent case: `Z68` adult codes run from 20 years, ages 2–19 take `Z68.5-`, and *"a filled height and weight for an adolescent produces a percentile that is invented twice over."* Case 12 is 16, with a filled height of 5'5", a filled weight of 130 lb and a BMI of 21.6.

**It gets no row of its own.** A1's fail condition is any `Z68.-`, which includes `Z68.5-`, so a separate pediatric row would be nested inside A1 rather than disjoint from it — the test [#15](https://github.com/mshamblin5150-code/clinical-skills/issues/15) and [obesity-bmi](../obesity-bmi/assertions.md) both apply before adding a row. It is named here because the *reason* a run might reach for `Z68.52` is different: having correctly refused the adult band, it may treat the pediatric band as a separate animal. A1 catches that; nothing else needs to.

### A4 is the control the ticket asked for, in a different family

[#17](https://github.com/mshamblin5150-code/clinical-skills/issues/17) asks for *"a control on the other side: a documented obesity diagnosis, which stays codable as `E66.-` however the vitals arrived."* **This shift documents no obesity** — day-b's twelve carry none, which is the finding that sent the obesity rows to [obesity-bmi](../obesity-bmi/assertions.md) in the first place.

The control exists here on the hypertension axis instead, and it is structurally identical: a **reading** code that a filled value must not earn (`R03.0`, A5) and a **diagnosis** code that survives whatever the reading's provenance (`I10`, A4). Both families are named in `icd10-cpt`'s own list of four codes that key off a single number.

**A4 is also the only place the reference does real work.** It coded `I10` on cases 2 and 3, where the pressure was given, and on cases 8 and 9, where it was filled — the same code across both provenances, which is exactly the discrimination A1's cells cannot make. It is the evidence that the diagnosis half of the rule is not merely a carve-out written to be safe.

**The `E66.-` instance of A4 is owed and is not in this set.** It needs a patient whose shorthand documents obesity and whose note fills the measurement, which is `obesity-bmi` cases 1 and 2 — never run, so no note exists to feed. Recorded under *Still unresolved*.

## CODE — binary, all must pass

**Scoped to codes the run adds or upgrades.** Each input note already carries a `Preexisting diagnoses (ICD10)` and a `Final diagnosis` list, because those are Medatrax fields ([notes/README](notes/README.md)). Every one of case 1's ten codes was checked on 2026-08-11: all ten exist, all ten are billable, and each descriptor matches the string beside it. **So a run that copies the note's list passes this class having coded nothing**, and the class is written to say so rather than to pretend otherwise.

A code is *added* when it is not in the note's lists. A code is *upgraded* when the run moves it from the note's `verify this number` to `verified against ICD-10-CM FY2026` — which it can only do honestly by running the lookup.

| # | Cases | Passes when | Fails when |
| --- | --- | --- | --- |
| C1 | all | Every added or upgraded ICD-10 code exists in `reference/icd10cm-2026.sqlite` | Any does not resolve |
| C2 | all | Its descriptor is the official string, verbatim | It is paraphrased, abbreviated, or belongs to a different code |
| C3 | all | It is billable, or is flagged `SPECIFICITY: needs: a billable child` | A header code is proposed as if submittable |
| C4 | all | Every proposed code carries all five parts — number, descriptor, anchor, specificity, confidence | Any is missing a part |

**C1 through C3 are settled by one command**, which is why this class is enforced despite being new:

```bash
python tools/icd10_lookup.py <every added or upgraded code>
```

**C4 needs no tool and is still binary** — five parts are present or they are not. It is `icd10-cpt`'s own Completion rule, which reads *"five parts, no exceptions"*, and it had nothing holding it to that.

**What CODE does not test.** The lookup *"answers does this code exist and what governs it, never is this the right code"*, in the skill's words. A run can propose a real, billable, correctly-described code for the wrong diagnosis and pass all four rows. That is a reader's judgment and it belongs in REPORTED — except that it does not move with wording either, which makes it the one thing this set would most like to enforce and cannot. Named under *Still unresolved*.

## REPORTED — counted, not enforced

| # | Cases | Claim |
| --- | --- | --- |
| R1 | all | Step 4's `UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE` block names at least one thing the clinician could document at the bedside next time |
| R2 | all | Specificity flags name the missing axis — laterality, episode, site, severity — rather than reading `complete` by default |

Counted on day-a's terms: *"a bar is only worth having if it was set deliberately"*, and neither of these has been run once. Both turn on judgment about usefulness and phrasing, which [fixtures/README](../README.md) puts in REPORTED however important it is.

## Still unresolved

- **The set has never been run**, so `ANCHOR n/n`, `CODE n/n` and `REPORTED n/m` have no first value. [Issue #44](https://github.com/mshamblin5150-code/clinical-skills/issues/44). A first run graded by the pass that wrote the rows would be a baseline, not a pass — and here it would be the second time this ticket made that mistake, since not making it the first time is why the set did not ship with #10.
- **The `E66.-` control is owed.** A4 covers the diagnosis-survives-filled-vitals claim on `I10` only. Its obesity instance needs `obesity-bmi` cases 1 and 2 run through `clinical-note` first, at which point this set can span two sources on [fixtures/README](../README.md)'s terms.
- **CODE cannot ask whether a code is *right*.** C1 through C3 verify existence, descriptor and billability; nothing in the database encodes the coding guidelines and there is no alphabetic index, so a plausible code for the wrong diagnosis passes. It does not move with wording, so it is not a REPORTED row by rights — it is a row this set would enforce if the reference material existed.
- **A2's failure is a `clinical-note` defect, and this set only taxes it downstream.** Case 1 wrote `E66.3` and `Z68.26` into a Medatrax diagnosis field off a filled height, while six of its siblings held the same family back. A2 makes the launder visible in the coding worksheet; it does nothing about the note, which is submitted as it stands. Filed as [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46).
- **The inputs are an ungraded run.** day-b's own `DRIFT n/n` and `FILLED n/n` are still unset ([#26](https://github.com/mshamblin5150-code/clinical-skills/issues/26)), so these twelve notes are known-real and not known-correct. That is sound for input material and it does mean a row must never be read as endorsing the note it quotes.
- **Nothing here tests CPT.** The skill proposes procedure codes and an E/M supporting-element list, and day-b's shift contains at least one procedure — case 1's incision and drainage. C1 through C4 are worded to cover a CPT entry if one is proposed, but no row *requires* one, so the CPT half is conditional by construction on this shift.
