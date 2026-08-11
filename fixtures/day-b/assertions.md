# day-b — assertion set

Twelve encounters from a single walk-in shift, 2025. Visit date and site removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

This set exists for one thing day-a cannot test: **what the skill does with a vital it had to invent.** Every day-a case carries a complete vital line, so nothing there exercises the filled half of the license. Nine of these twelve carry no vital at all.

Opened for [issue #8](https://github.com/mshamblin5150-code/clinical-skills/issues/8).

## Status — both halves built

**The inputs are in.** All twelve encounters are in [shorthand/](shorthand/), one file per case, de-identified.

**The reference is read.** All twelve submitted notes were opened in the portal on 2026-08-11 and are kept, un-de-identified, in `scratch/day-b-reference/` — gitignored, because they carry the visit date, the site, a named outside physician and the patient references. Every row below now records what the submitted note actually did.

**Inputs must come from the day file, never from the generated notes**, and the same trap applies to the reference half. That is why the rule below stood:

> ~~Until it is, no drift row may be added to this set.~~ **Lifted 2026-08-11.** The reference is read, so a drift row can now be checked against what the submitted note did rather than against the skill's own prior output.

The rule was day-a's, and it was worth keeping: four of day-a's six DRIFT rows changed when its reference was finally read, and two had claimed the clinician abandoned a finding he had in fact carried into the Assessment and the Plan.

**Here it changed one of five.** D1 through D4 turn out to say what a careful read of the input would have said. D5 is the exception, and in the direction the rule exists to catch: the submitted note **addressed** the low magnesium, so a row asserting it was abandoned would have been false. Its `Reference did` cell reads *neither*, not *better*, and it is the set's only anti-regression row.

**The set has never been run.** `DRIFT n/n` and `FILLED n/n` have no first value yet.

## The reference is a baseline, not a target

Same three verdicts as [day-a](../day-a/assertions.md): a difference from the submitted note is **better**, **worse**, or **neither**, and only *worse* is a regression. The `Reference did` columns below say which.

**Reading it moved this set in both directions.** It supplied five drift rows the set was forbidden to carry, and it also **failed two of the set's own four FILLED rows** — B4 on case 4 and B2 on case 8. A bar the reference clears everywhere is a bar set too low; a bar it fails is where the skill has something to be better than.

### The provenance question was asked, and it has no answer

A submitted note does not say whether a value was measured at the visit or supplied at write-up, and these were typed 78 days after the shift. **The clinician was asked directly, 2026-08-11, and could not answer**: *"i probably made them up… i can't give you a real answer."*

`reference/medatrax-fields.md` points the same way — every 2025 Fall and 2026 Spring encounter fills Height and BMI, *"inventing a height where the shorthand carries none"*, in his words *"the newer records everything is filled out."* That is a pattern, not a record of what happened at these nine bedsides, and no read of the portal will ever produce one.

**So no row here may depend on the answer, and none does.** Every `Reference did` cell below is worded to hold whether the value was measured or invented:

- **B1** asks only that something went in every box. True either way.
- **B3** asks what happened to a value *downstream* — Objective only, or named in the Assessment. True of the value whatever its origin.
- **B4** is about **given** vitals, where the shorthand supplies the value and the comparison is direct.
- **B2 used to depend on it**, and was rewritten so it no longer does. See below.

### B2 was wrong, and the clinician is what corrected it

The row previously read: a hypertensive with no recorded pressure must not be given a *normal* one, on the rationale that hypertension makes a normal pressure implausible. Asked about case 8's 124/78, he answered: **"hell she may be compliant with her BP meds."**

He is right, and it breaks the rationale. A treated, compliant hypertensive at 124/78 is not an implausible value — **it is the goal of the treatment.** A row demanding an abnormal pressure from every documented hypertensive was demanding an invented abnormal finding, which is the thing standing rule 2 exists to forbid. The set had it backwards.

**B2 now has two exits and forbids only silence.** A filled pressure for a documented hypertensive may be abnormal, or it may be normal *and* the note says the hypertension is controlled or treated. What fails is a normal number with no account of why it is normal — because that is the run that picked 124/78 out of the air, and it is indistinguishable from the run that reasoned unless the note says so.

**Case 2 is the in-corpus proof the passing form is writable.** A *given* 121/61 with the same `htn` history, and the Assessment reads `HTN, controlled (I10)`. That is the shape B2 now asks for.

## DRIFT — binary, all must pass

Each row is a finding the shorthand documented that a note can drop between the Objective and the Assessment. A run passes the row when the finding is named in the **Assessment or the Plan** — not merely recorded in the Objective.

**Four of the five are findings the submitted note did drop. D5 is not** — see below the table.

| # | Case | The finding | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| D1 | 3 — 57 F | BP 147/81, with `htn` in the history | The elevated pressure is not named in the Assessment or the Plan. **A bare `BP` inside an age-based screening list is not a naming** — see below | Recorded it in the Objective and the portal field and stopped. The Assessment names scabies, traumatic otitis externa and tobacco use; **`hx htn` is dropped from the note entirely** — no I10, no recheck, no home log. Addressing it is *better*. |
| D2 | 1 — 36 M | Breath sounds diminished in all four fields, in a 1 PPD × 24-year smoker | Not named in the Assessment or the Plan | Carried it into the Objective and stopped. The Assessment codes `Tobacco use (Z72.0)` but never the finding; no spirometry, no film, no COPD consideration. Naming it is *better*. |
| D3 | 11 — 32 M | Inspiratory wheezing in all fields, in a documented asthmatic | Absent from the Assessment or the Plan | Recorded it on exam, then **recast it in the HPI as `inspiratory wheeze history`** — past tense — and carried asthma only in the *pre-existing* code list. No inhaler, no peak flow, no asthma plan item. Addressing it is *better*. |
| D4 | 7 — 67 F | Elevated liver enzymes — AST 48, ALP 136 — in a patient on a statin | The elevated enzymes are absent from the Assessment or the Plan | **Dropped them.** No AST, no ALP, no statin and no hepatic follow-up anywhere in the note, and a CMP ordered without saying why. The shorthand had already written the follow-up (`f/u pcp re elevated lft`). Keeping it is *better*. |
| D5 | 10 — 48 M | Magnesium 1.6, written in the shorthand as `labs good mg 1.6` | The low magnesium is absent from the Assessment or the Plan | **Caught it** — `Mg 1.6 → recommend OTC magnesium supplement`. Matching this is *neither*; losing it is *worse*. |

**D1's fail condition is worded against a real decoy.** The submitted note's Plan contains the string `BP` — inside `Screenings: Colon CA (age), mammogram, BP, smoking cessation`, boilerplate that appears on other notes from this shift regardless of the pressure recorded and would read identically had the pressure been 118/70. A row that passed on a substring match for `BP` would score the reference as having addressed 147/81. It did not.

**D5 does not fit the sentence above the table, and it is kept anyway.** Nothing was abandoned: the shorthand's own plan line already reads `recommend mg otc mg supplement`, and the submitted note carried it through. So D5 is not a defect the reference committed — it is the one place on this shift where the reference did the right thing, and the row asks the skill not to fall behind it. day-a keeps D3 and D5 on the same terms, both marked *neither*.

**What it still tests is the decoy in the input.** `labs good mg 1.6` wraps a low magnesium inside a phrase that says the labs were fine. A run that reads `labs good` and moves on drops the abnormal, and the recommendation two words later is the only thing that would catch it. The row is checkable from the input alone; what the reference added was the verdict — *neither*, not *better*.

**Case 2 is the counter-example that makes D1 legible.** The same `htn` history, a pressure of 121/61, and the Assessment reads `HTN, controlled (I10)`. The note with nothing to address addressed it; the note with 147/81 did not.

## FILLED — binary, all must pass

A third assertion class alongside DRIFT and REPORTED, defined in [fixtures/README](../README.md). Binary, like DRIFT.

**Enforced rather than counted, deliberately.** day-a holds that *"a bar is only worth having if it was set deliberately"* and left R9 and R10 counted for a stated reason: they turn on differential depth, screening content and education phrasing, which move with the model and the wording. Failing a run over those would be failing it over style.

These four do not move with wording. Each resolves to a value or its absence — is there a blood pressure in the FILLED block, is it below 130 over 80, does the string naming it appear in the Assessment or the Plan, does the given value survive. Two runs can word case 9 completely differently and still agree on all four. That is the property that makes a bar enforceable, and it is why these are enforced where R9 was not.

**B2's second exit is the one word of judgment in the table**, and it is bounded: does the Assessment call the hypertension *controlled*, *treated*, *on therapy*, or name the medication. A code in a pre-existing list is not that, and neither is a monitoring instruction. Scoring it needs a reader, not a taste.

**Grading the skill is easier than grading the reference**, because the skill's output labels its own filled values in the FILLED block and a submitted note does not. Every `Reference did` cell is written to hold either way — see *The provenance question* above.

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| B1 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | A case whose shorthand carries no vitals is given a **complete filled set** — blood pressure, respiratory rate, height and weight, with BMI derived from the last two — each declared in the FILLED block | Any of the four is left blank, reported under GAPS, or silently omitted | **Produced a complete set on all nine** — blood pressure, pulse, respiratory rate, temperature, oxygen saturation, height, weight and a derived BMI on every one. Not a blank, not a GAPS line. Whether he measured them or supplied them at write-up is unrecoverable and does not bear on this row: something went in every box. Matching this is *neither*; anything less is *worse*. |
| B2 | 8 — 33 F, 9 — 44 F | The filled blood pressure for a patient with **documented hypertension** is either **not normal** — systolic 130 or above, *or* diastolic 80 or above — **or** normal *and* the Assessment names the hypertension as **controlled or treated** | A hypertensive with no recorded pressure is given a normal one and the note says nothing about why it is normal | **Split — one each way.** Case 9: 132/84, above on both limbs; passes on the first exit. Case 8: **124/78, and the hypertension appears only as `HTN I10` inside a pre-existing code list** — no medication, nothing calling it controlled or treated, and `BP monitors at home` in the Plan says to watch it rather than accounting for the number. Fails on both exits. Matching case 9 is *neither*; beating case 8 is *better*. |
| B3 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | Every **filled** vital or body measurement outside the normal range for that age is named in the Assessment or the Plan | It reaches the Objective and the FILLED block and stops | **Failed it everywhere it fired.** Four filled pressures landed outside normal — case 5 at 132/74, case 7 at 138/82, case 9 at 132/84, case 10 at 126/80 — and not one is named in an Assessment or a Plan. Case 9's filled **BMI of 37.8**, class II obesity, is not coded or mentioned anywhere at all. Naming them is *better*. |
| B4 | 2, 3, 4 | Every **given** vital appears in the note unchanged, and no vital is filled over one the shorthand supplied | A recorded value is replaced, rounded, or duplicated by a generated one | **Failed on case 4.** The given `ht 6'2"` — 74 inches — was recorded as `6'1" (73 in)`, and the BMI of 26.4 is derived from the altered value rather than the given one. Cases 2 and 3 came through unchanged, every value. Beating case 4 is *better*. |

### The three rows are a chain, and each closes the one above

B3 is what [issue #8](https://github.com/mshamblin5150-code/clinical-skills/issues/8) asked for. On its own it is **passable by cheating**, and each cheat is the exact behavior the license forbids.

**B3 alone is passable by filling a bland value.** `clinical-note` requires that a filled vital be *"the value this patient most plausibly had … not from the middle of the normal range"*, and that one landing abnormal be worked up in full. But whether it lands abnormal is itself generated. A run that fills 118/76 for case 9 — 44, hypertensive, with peripheral arterial disease — has nothing abnormal to address, so B3 passes with nothing having been tested. The note that manufactured a bland vital scores identically to the one that reasoned.

**B2 closes that**, and its threshold is deterministic: `clinical-note` sets normal below 130/80 and `corpus_census.py::is_normal_bp` encodes the same as an explicit conjunction, so a split reading like 132/78 is unambiguously *not* normal.

**What B2 does not do is demand an abnormal number**, and an earlier version of it did. A treated hypertensive at 124/78 is not implausible — that reading is what the treatment is *for* — so a row insisting on an abnormal pressure would have been ordering up an invented abnormal finding, exactly what standing rule 2 forbids. The bland-fill cheat is still real; what distinguishes it from good care is not the number but whether the note accounts for it. Hence the second exit, and hence the only thing B2 actually forbids: **a normal pressure in a hypertensive, unexplained.**

**B2 alone is passable by filling nothing at all.** This is the same defect one level up, and it is the one worth stating plainly: B2 and B3 are both conditional on a value having been generated. A run that leaves case 9's blood pressure blank, or reports it under GAPS, has no filled pressure to be normal or abnormal — and passes both rows having tested nothing.

**B1 closes that**, and it is the row the license itself demands: *"A value is required … Something has to go in the box."* Medatrax holds fields for blood pressure, respiratory rate, height and BMI, so those are what B1 names. It is the precondition the other two rest on, which is why it comes first.

Cases 8 and 9 are B2's anchors — both carry `htn` in the history and neither carries a single vital. Case 9 is the stronger: hypertension plus peripheral arterial disease plus hyperlipidemia at 44 makes an *unexplained* normal pressure incoherent. Not an impossible one — she could be well controlled — but a note that produces 118/76 for her and then says nothing about how she got there has not reasoned, it has guessed.

**The reference read confirms the chain was not theoretical.** The clinician cleared B1 on all nine, then produced the two failures the chain predicts: an unaccounted-for normal pressure in a hypertensive (case 8, B2) and four abnormal filled pressures that reach the Objective and stop (B3). Both rows were written into this set from the inputs before the reference was read. Both fired.

**B1 and B3 still leave the other seven cases vacuous-passable on the vital half.** Cases 1, 5, 6, 7, 10, 11 and 12 must now be filled completely, but nothing forces any of those filled values abnormal, so B3 can pass on them without firing. Only cases 8 and 9 are reached at all, and B2 no longer forces even those to be abnormal — it forces them to be *explained*. That is a narrower hole than before and it is not closed.

### Case 2's height: resolved, and B4 now covers it

Case 2's vital line reads `wt 62in wt 131` — `wt` written where `ht` was meant, the same defect day-a case 8 preserves as `hr 65 inches`. The set previously exempted case 2's height from B4, because the value was *given* under one reading and *absent* under the other and B4 would have punished a run for either choice.

**The reference settles it: 62 is a height.** The submitted note writes `5'2", 131 lb, BMI 24.0`, the portal Height field reads 62, and 131 lb at 62 in recomputes to 23.96 — so the BMI is derived from that reading and not from some other pair. The clinician was in the room; what the patient's height was is a fact he had and the shorthand mistyped.

**So the exemption is withdrawn and B4 covers all of case 2**, height included. A run that reads `62in` as a weight, or that treats the height as absent and fills one over it, fails B4. The suffix `in` is what makes this fair to enforce — it is a length whatever the label in front of it says.

This does **not** generalize to day-a case 8's `hr 65 inches`, which has no reference reading behind it in this set.

### The body-measurement half has no equivalent to B2

Issue #8 asked for both halves — a filled vital and a filled body measurement — because [#7](https://github.com/mshamblin5150-code/clinical-skills/issues/7) widened drift row 4 to reach height, weight and a derived BMI.

**Delivered:** B1 forces a height, a weight and a derived BMI on all nine cases, so the body measurement is always generated and always declared. B3 then covers it **whenever that BMI lands abnormal.**

**Not delivered:** nothing forces it to land abnormal, and that gap is real rather than an oversight:

- Hypertension is documented, so a normal pressure is a thing the note owes an account of. That is what B2 rests on — not that the pressure must be high.
- **No condition in these twelve does the same for BMI.** Cases 5 and 10 carry diabetes, which raises the odds of an obese BMI without requiring one. A row demanding an obese BMI from a documented diabetic would be demanding an invented abnormal finding — the thing standing rule 2 exists to forbid.

So a run can satisfy this set while never generating an abnormal BMI at all. Closing it needs a case whose shorthand documents obesity without a weight, and none of these twelve does.

**The reference is evidence the gap matters, not that it can be closed here.** The clinician generated a BMI of 37.8 for case 9 unprompted — from a shorthand that documents lymphedema, arthritis in both knees and a hip fracture, none of which requires it — and then addressed it nowhere. That is precisely the defect a body-measurement B2 would catch, and this set still cannot demand it.

## What the reference surfaced that this set does not assert

Three defects in the submitted record are real and are **out of scope for a fixture whose inputs carry no dates and no portal fields.** They are recorded in `scratch/day-b-reference/README.md` so they are not lost:

- **Case 9's Visit Date is the day the note was typed, 78 days after the encounter.** The form's own date field carries the encounter date, so the two halves of the record disagree with each other. A date-range search for the shift therefore returns eleven of the twelve, and case 9 had to be found by patient creation order instead. (The dates themselves stay out of this file for the reason at the top of it.)
- **The shift had thirteen encounters, not twelve.** A thirteenth on the same date is not in the day file at all. A day file's note count is not a census of the shift.
- **Case 12's age is recorded as 18 against a shorthand that reads `16 yo F.`**, which put a pediatric hour into `Adult (18 – 60)`.

The inputs cannot test any of these: they carry no visit date, no portal entry fields, and the age is given correctly in the shorthand. Testing them needs a different kind of fixture than this one.

## Still unresolved

- **`clinical-note` still says what B2 stopped saying.** [SKILL.md](../../skills/clinical-note/SKILL.md) reads *"A known hypertensive seen for a productive cough gets a hypertensive pressure"* — the rule B2 was written to fixture, and the one the clinician's *"she may be compliant with her BP meds"* contradicts. The same file also tells the skill to **infer a likely regimen** where a hypertensive history carries no `meds:` line, and to propose *"lisinopril where the history carries hypertension"*. So it currently instructs the skill to put a patient on an ACE inhibitor and then hand her a hypertensive pressure anyway. **B2 was changed and the skill rule was not**, deliberately: rewriting a clinical rule is the clinician's call and it would ripple into `peds-bp` and drift row 4. Filed as [#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23).
- **The set has never been run.** Until it is, `DRIFT n/n` and `FILLED n/n` have no first value to measure drift from — and a first run graded by the pass that produced it is a baseline, not a pass ([fixtures/README](../README.md)).
- **Cases 6 and 12 are 17 and 16, and [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11) turned out not to reach them.** That issue asked whether a filled pediatric vital should be filled at all, and pointed here for the fixture. The corpus answered the boundary question first: measured 2026-08-11, a blood pressure going missing from a vital line that was otherwise written happens **only under 6** — every band from 9 up produces not one instance, and a 16-year-old is transcribed exactly like an adult. So these two are adolescent only in the sense that their filled values must suit their age, which B1 already demands. The ruling — filled, no exception — is fixtured in [peds-bp](../peds-bp/assertions.md), whose cases are young enough to test it.

  What is genuinely untested here is **B2's** analogue, not B1's: B2 reaches only cases 8 and 9 because only those two document a condition making a normal value implausible, and neither of these adolescents does. (An earlier version of this bullet named B1 for that; B1's case list has covered 6 and 12 all along.)
- **A diabetic was given a steroid burst with no glucose comment** — case 10, methylprednisolone 125 mg IM plus a dose pack, `DM2 E11.9` coded in the same note. Case 5 has the shape too: diabetes carried into the HPI and absent from the Assessment. It is a plan-safety defect rather than a finding abandoned, so it does not fit the DRIFT shape, and a row turning on whether a caution was *worded* would belong in REPORTED — which this set does not define. Left out deliberately.
