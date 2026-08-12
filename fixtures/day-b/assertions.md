# day-b — assertion set

Twelve encounters from a single walk-in shift, 2025. Visit date and site removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

This set exists for one thing day-a cannot test: **what the skill does with a vital it had to invent.** Every day-a case carries a complete vital line, so nothing there exercises the filled half of the license. Nine of these twelve carry no vital at all.

**It now carries the OLDCARTS half of the same license.** [Issue #30](https://github.com/mshamblin5150-code/clinical-skills/issues/30) admitted a third member to the filled class — the HPI severity — and it was found on **case 9 of this set**, whose run wrote `Aggravating - not documented ... Severity - not documented`. B5 and B6 are that half, and they reach **all twelve** rather than B1's nine — a case can carry a full vital line and still leave seven OLDCARTS boxes empty, so the two splits are independent. B7 and B8 then divide the twelve on where the severity comes from, which is a third split again: seven cases write a score, two write the absence of one, three write neither.

**And it now carries the direction all of those rows point the wrong way down.** B1 through B3 and B5 through B8 ask what work a generated value made the note do — B4 is the odd one out, guarding givens. [Issue #27](https://github.com/mshamblin5150-code/clinical-skills/issues/27) was a generated value making the note do **less** — case 9's filled `T 98.8 F` and `SpO2 97%` deferring a chest film for a documented `lung sounds diminished`, which the clinician read and agreed with. B9 is that direction, and D7 is the lung finding it turns on, which had no row until now.

**And it now carries the social and allergy half of the same license.** [Issue #29](https://github.com/mshamblin5150-code/clinical-skills/issues/29) ruled that the slots the branch templates enumerate are boxes like the OLDCARTS eight — a value is required and the shorthand constrains none — and that the hedge the fixtures were rewarding, `not documented this visit`, is a sentence **drift row 12 had already banned**. R2, R3 and R4 are that ruling, and **R1 is the row it reversed most of.** The reversal was not free: it struck two of R1's three claims and left the third standing on a different argument, which is written out under the row.

Opened for [issue #8](https://github.com/mshamblin5150-code/clinical-skills/issues/8).

## Status — both halves built

**The inputs are in.** All twelve encounters are in [shorthand/](shorthand/), one file per case, de-identified.

**The reference is read.** All twelve submitted notes were opened in the portal on 2026-08-11 and are kept, un-de-identified, in `scratch/day-b-reference/` — gitignored, because they carry the visit date, the site, a named outside physician and the patient references. Every row below now records what the submitted note actually did.

**Inputs must come from the day file, never from the generated notes**, and the same trap applies to the reference half. That is why the rule below stood:

> ~~Until it is, no drift row may be added to this set.~~ **Lifted 2026-08-11.** The reference is read, so a drift row can now be checked against what the submitted note did rather than against the skill's own prior output.

The rule was day-a's, and it was worth keeping: four of day-a's six DRIFT rows changed when its reference was finally read, and two had claimed the clinician abandoned a finding he had in fact carried into the Assessment and the Plan.

**Here it changed one of five.** D1 through D4 turn out to say what a careful read of the input would have said. D5 is the exception, and in the direction the rule exists to catch: the submitted note **addressed** the low magnesium, so a row asserting it was abandoned would have been false. Its `Reference did` cell reads *neither*, not *better*, and it is the set's only anti-regression row.

**D6 arrived after that count and is not in it.** It comes from [#32](https://github.com/mshamblin5150-code/clinical-skills/issues/32) — a `clinical-note` run over case 9, not the reference read — and the read is what lets it carry a verdict at all.

**D7 arrived after it too, from [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27), and is not in it either.** Unlike D6 it carries no verdict, because the read had already happened when it was written. So *"here it changed one of five"* is a statement about D1 through D5 and stays one.

**Run 1, 2026-08-11, on commit `d213e35`: `DRIFT 5/5` · `FILLED 3/4` · `REPORTED 0/1`. The run fails.** Output in `scratch/day-b-run-1/`, scorecard and reasoning in `SUMMARY.md` there.

FILLED is binary, and **B3 misses on case 5**: a filled BMI of 28.4 — the overweight band, so the row fires — reaches the Objective, the Medatrax field and the FILLED block and is named in neither the Assessment nor the Plan.

**Of B3's nine cases, seven produced an abnormal filled BMI and six of those addressed it.** Cases 6 and 12 landed normal, at 23.0 and 21.6, so the row never fired on them. Case 5 is the only case where it fired and was missed.

**The note's own drift matrix reported row 4 as PASS**, on the stated ground that the BMI was addressed through weight counseling in the Plan. That Plan contains no weight counseling. [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md) argues a self-report cannot grade a run because the run that misses a finding is the run that reports PASS; this is that argument happening rather than being made.

**Unlike day-a's run 1, this one was not graded by the pass that produced it.** Six subagents wrote the notes without access to this file, a fresh pass graded the output text against it, and the orchestrating pass re-derived every row from the output files having authored none of them. What that leaves is narrower than what it removes: one session directed both halves, so a framing shared between them is not excluded.

### Run 1 covers ten of this set's twenty-two rows, and the other twelve did not exist when it ran

**D6, B5–B8, C1 and C2 landed on `main` while run 1 was in flight** — [#32](https://github.com/mshamblin5150-code/clinical-skills/issues/32), [#30](https://github.com/mshamblin5150-code/clinical-skills/issues/30) and [#19](https://github.com/mshamblin5150-code/clinical-skills/issues/19), the same day, one of them arriving between the run's commit and its merge. The run was made against `d213e35`, where the set held D1–D5, B1–B4 and R1, and it graded every one of them. **So `DRIFT 5/5`, `FILLED 3/4` and `REPORTED 0/1` are complete for the commit they name, `CODING n/n` has no value at all, and the scorecard is not a full pass over the set as it now stands.**

**The new rows were deliberately not graded from run 1's output, and the reason is not laziness.** The output exists and the new rows are claims about note text, so scoring them would have been cheap. But B5 through B8 exist *because* `clinical-note` changed — #30 admitted the HPI severity to the filled class, #32 and #19 moved the same file — and those twelve notes were written before those changes. A score from them would measure neither the commit the notes came from nor the commit the rows came from. **A number that belongs to no commit is worse than a gap that names itself.**

**D7 and B9 landed after run 1 rather than during it**, from [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27), and the same reasoning holds with one wrinkle worth stating. They are ungraded here on the argument above: `clinical-note` gained drift row 15 with them, and those twelve notes were written before it.

**But run 1's output is what this ticket's evidence is drawn from, and evidence is not a verdict.** Case 9's note is quoted under *B9 is the subtractive half of the license* below, because it shows a run reaching for filled values to defer a chest film — the second such run, after the one #27 reports. That establishes the defect is real and recurring. **It does not score B9**, and reading it as `FILLED 3/5` would be the exact mistake the paragraph above refuses. What would settle both rows is run 2.

**R2, R3 and R4 landed after all of that, from [#29](https://github.com/mshamblin5150-code/clinical-skills/issues/29), and are ungraded on the same argument.** They exist because `clinical-note` gained drift row 16 and lost the hedge, and these twelve notes were written before either. R1 was rewritten in the same pass — its `0/1` from run 1 stands, because the miss run 1 committed is still a miss under the narrowed row, which is stated where the row is.

What this asks for is run 2, against current `main`, over all twenty-two rows. That is [fixtures/README](../README.md)'s own instruction — *re-run after every `SKILL.md` edit* — arriving immediately, and it is [#55](https://github.com/mshamblin5150-code/clinical-skills/issues/55).

## The reference is a baseline, not a target

Same four verdicts as [day-a](../day-a/assertions.md), and only *worse* is a regression. The `Reference did` columns below say which:

- **Better** — the skill caught something the submitted note dropped.
- **Worse** — the skill lost something the submitted note had. The most important thing this set can find.
- **Neither** — different wording for the same content.
- **Out of reach** — the submitted note is better on information the skill never had. The clinician was in the room; the skill has the shorthand and nothing else. Matching this is not a target and failing it is not a regression — **the skill is required not to try.**

**The fourth class arrived while this set could not host it.** It was added to day-a on 2026-08-11, and the commit that added it recorded why day-b was left on three: *"neither has read its reference, so neither can host the class yet, and both belong to other tickets."* This is that other ticket. day-b's one row of the class is **R1**, below.

**Reading it moved this set in both directions.** It supplied five drift rows the set was forbidden to carry, and it also **failed two of the four FILLED rows the set held then** — B4 on case 4 and B2 on case 8. (B5 through B9 and D7 arrived after the read and carry no verdict from it; see below.) A bar the reference clears everywhere is a bar set too low; a bar it fails is where the skill has something to be better than.

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

**Case 2 is the in-corpus proof the passing form is writable.** A *given* 121/61 with the same `htn` history, and the Assessment reads `HTN, controlled (I10)`. That is the shape B2 now asks for. `test_corpus_census.py::test_case_2_is_the_normal_hypertensive_the_rule_rests_on` pins that reading by value, so an edit to the shorthand voids the claim loudly.

**The skill file has since been brought into line, and the corpus is what settled it.** For a while this row and [SKILL.md](../../skills/clinical-note/SKILL.md) disagreed on purpose — B2 was rewritten and the clinical rule was left alone, because changing one is the clinician's call. He ruled on 2026-08-11 ([#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23)), and the count is what he ruled on: **175 of 551 encounters document hypertension, 96 transcribe a pressure, and 39 of those 96 are normal.** The retired rule would have contradicted 39 of his own readings. SKILL.md now carries B2's two exits as prose, the same four accepted forms of an account, and **drift row 14**, which is this row's rule stated where a run walks it while writing rather than only where a fixture scores it afterwards.

**The four ripple sites were checked rather than assumed**, which #23 asked for by name because a clinical rule does not change alone. `peds-bp` P2 and P3 needed nothing — P2's rationale was already rewritten on this ruling and P3 is a threshold row that never mentions a condition. `day-a` D3 and D10 needed nothing either, and for a reason row 14 now states outright: both are **given** pressures, and a given value cannot fail a row about filled ones. Drift row 4 is untouched and keeps its number. The one site that did need work was `fixtures/obesity-bmi`, which #23 did not list — its *Still unresolved* bullet had predicted this rewrite would reach O2, and it did.

**What did not change is the inferred regimen.** *"Infer the likely regimen"* survives untouched, and the ruling put it to work: an inferred antihypertensive in the Medications section **is** an account for a normal filled pressure. Two separately licensed fills agreeing is not the compounding standing rule 2 forbids, because the hypertension itself is a given.

## DRIFT — binary, all must pass

Each row is a finding the shorthand documented that a note can drop between the Objective and the Assessment. A run passes the row when the finding is named in the **Assessment or the Plan** — not merely recorded in the Objective.

**Five of the seven are findings the submitted note did drop. D5 is not** — see below the table. **D7 arrived after the reference read and carries no verdict**, for the reason B5 through B8 carry none.

| # | Case | The finding | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| D1 | 3 — 57 F | BP 147/81, with `htn` in the history | The elevated pressure is not named in the Assessment or the Plan. **A bare `BP` inside an age-based screening list is not a naming** — see below | Recorded it in the Objective and the portal field and stopped. The Assessment names scabies, traumatic otitis externa and tobacco use; **`hx htn` is dropped from the note entirely** — no I10, no recheck, no home log. Addressing it is *better*. |
| D2 | 1 — 36 M | Breath sounds diminished in all four fields, in a 1 PPD × 24-year smoker | Not named in the Assessment or the Plan | Carried it into the Objective and stopped. The Assessment codes `Tobacco use (Z72.0)` but never the finding; no spirometry, no film, no COPD consideration. Naming it is *better*. |
| D3 | 11 — 32 M | Inspiratory wheezing in all fields, in a documented asthmatic | Absent from the Assessment or the Plan | Recorded it on exam, then **recast it in the HPI as `inspiratory wheeze history`** — past tense — and carried asthma only in the *pre-existing* code list. No inhaler, no peak flow, no asthma plan item. Addressing it is *better*. |
| D4 | 7 — 67 F | Elevated liver enzymes — AST 48, ALP 136 — in a patient on a statin | The elevated enzymes are absent from the Assessment or the Plan | **Dropped them.** No AST, no ALP, no statin and no hepatic follow-up anywhere in the note, and a CMP ordered without saying why. The shorthand had already written the follow-up (`f/u pcp re elevated lft`). Keeping it is *better*. |
| D5 | 10 — 48 M | Magnesium 1.6, written in the shorthand as `labs good mg 1.6` | The low magnesium is absent from the Assessment or the Plan | **Caught it** — `Mg 1.6 → recommend OTC magnesium supplement`. Matching this is *neither*; losing it is *worse*. |
| D6 | 9 — 44 F | A documented positive COVID contact — `daughter inall was postive for covid` — alongside a congruent respiratory presentation | The Plan does not order COVID-19 testing and influenza testing, with a specimen named. Group A strep is required too, because this input documents the pharynx — `sore throat` and `pharyngeal erythema`. **Carrying the exposure in the HPI is not acting on it** — see below | **Ordered no testing at all.** The exposure reached the note — the HPI reads `COVID exposure in family` — and the Plan carries amoxicillin-clavulanate, a steroid dose pack, otic drops and an IM steroid, with no swab of any kind. Ordering it is *better*. |
| D7 | 9 — 44 F | `lung sounds diminished`, in a patient whose shorthand carries **no vital line at all** | Not named in the Assessment or the Plan | Not scored. See below. |

**D1's fail condition is worded against a real decoy.** The submitted note's Plan contains the string `BP` — inside `Screenings: Colon CA (age), mammogram, BP, smoking cessation`, boilerplate that appears on other notes from this shift regardless of the pressure recorded and would read identically had the pressure been 118/70. A row that passed on a substring match for `BP` would score the reference as having addressed 147/81. It did not.

**D5 does not fit the sentence above the table, and it is kept anyway.** Nothing was abandoned: the shorthand's own plan line already reads `recommend mg otc mg supplement`, and the submitted note carried it through. So D5 is not a defect the reference committed — it is the one place on this shift where the reference did the right thing, and the row asks the skill not to fall behind it. day-a keeps D3 and D5 on the same terms, both marked *neither*.

**What it still tests is the decoy in the input.** `labs good mg 1.6` wraps a low magnesium inside a phrase that says the labs were fine. A run that reads `labs good` and moves on drops the abnormal, and the recommendation two words later is the only thing that would catch it. The row is checkable from the input alone; what the reference added was the verdict — *neither*, not *better*.

**Case 2 is the counter-example that makes D1 legible.** The same `htn` history, a pressure of 121/61, and the Assessment reads `HTN, controlled (I10)`. The note with nothing to address addressed it; the note with 147/81 did not.

### D6 asks for an order, because for an exposure that is what acting on it is

**D6's fail condition is worded against a naming that is not an acting** — the same trap as D1, from the other end. The submitted note does carry the exposure: the HPI reads `COVID exposure in family`, so a row passing on the finding appearing *anywhere* would score the reference as having addressed it. It ordered no swab. For a documented contact the act is the order, with a named agent and a named specimen in the Plan, which is [#32](https://github.com/mshamblin5150-code/clinical-skills/issues/32)'s rule.

**Two reasons it could have been a B row instead, and why it is not.** It drops out of the *Subjective* rather than the Objective, since an exposure is history and not an exam finding; and what the row checks for is a **generated** order, which is FILLED's subject rather than DRIFT's under [fixtures/README](../README.md).

Both are real and neither moves it. The section it fell out of is incidental — the class is about a documented thing that never reaches the Assessment or the Plan, which is D5's ground for being kept too. And day-b's FILLED class is not generated content in general: it is the vitals license, and B1 through B3 are a chain about one value's plausibility band and what happens when it lands abnormal. An order has no band to land in and nothing to be plausible about. **What D6 tests is whether a given survived**, and the fact that surviving takes the form of an order rather than a sentence is what its fail condition spells out. That is D1's shape, not B2's.

**The DRIFT verdict is not the accusation [#32](https://github.com/mshamblin5150-code/clinical-skills/issues/32) forbids.** The ticket forbids the *skill's note* carrying a FLAG at the clinician on every encounter where he treated a documented contact empirically. It does not forbid this set recording that one encounter fell short — and the standard it fell short of is his own, stated on the ticket: *"you better believe that they are getting swabbed every which way."* A fixture row is read once by him; a FLAG is written into every note.

**Cases 8 and 12 are the in-corpus proof the passing form is writable.** Both document a contact — a daughter-in-law with COVID, a coach sick two days earlier — and both shorthand plans order the swab: `covid` on case 8, `covid, strep, flu` on case 12. Those are *given* orders, so D6 does not fire on them. What they establish is that swabbing a documented contact is this clinician's own practice, and case 9 is where a long shift lost it. `tools/test_corpus_census.py` asserts these two plan lines, and case 9's empty one, rather than trusting this paragraph.

**Case 10 is deliberately not a second row.** Its shorthand reads `has had no sick contacts` and then orders COVID, influenza and strep anyway, so the tests are given whatever the rule does and the case cannot separate a run that reasoned from one that copied. A row needs an input where the rule's output would otherwise be absent, and only case 9 has that.

**What D6 does not hold is #32's other half.** The ticket's complaint was the *route*: the run reached the order as a `FLAG` against the encounter for not swabbing, and then wrote the order to answer the flag. D6 grades the outcome and not the route, for two reasons. A submitted note carries no tier block, so the `Reference did` column has nothing to say about a FLAG that was or was not written. And the rule leaves the flag legal in a narrow case — where testing would have changed the management the encounter recorded — so a row forbidding it outright would fail a run for a judgment the rule permits. The route is a rule in [SKILL.md](../../skills/clinical-note/SKILL.md); the outcome is the bar here.

### D7 is the third lung finding in this set, and it was the one without a row

Cases 1 and 11 each carry a chest exam abnormal that has a row on it — D2's diminished breath sounds in a 24-year smoker, D3's inspiratory wheezing in a documented asthmatic. Case 9's `lung sounds diminished` had none. That is why [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27) was found by running the case and handing the output to the clinician, rather than by reading this file: the finding the whole ticket turns on was unasserted.

**It is anchored on the input alone.** `lung sounds diminished` is in the committed shorthand and so is the absent vital line. Nothing here needed a run to write, which is how D1 through D4 were written before the reference was opened, and both of the FILLED rows written the same way fired when it was.

**Case 7 is the in-corpus proof the passing form is writable**, and it is D6's cases 8 and 12 argument on this row. Its exam reads `lungs clear in the apeces, diminished in bases` and its plan orders `cxr` outright. So imaging a diminished lung base is this clinician's own practice on this shift, and case 9 is where a long day lost it. It is also why case 7 cannot host the row: the film is a *given* there, so a run that copied the input would pass having tested nothing — the same reason case 10 is not a second D6. `tools/test_corpus_census.py` asserts case 7's finding and its order, and case 9's finding and its empty plan, rather than trusting this paragraph.

**No reference verdict.** This row arrived after the 2026-08-11 read, and the submitted notes are un-de-identified PHI behind a signed-in portal session. Same position as B5 through B8.

### All three lung rows are passable by dismissing the finding, and B9 closes that

D2, D3 and D7 sit on cases 1, 11 and 9 — **every one of them on B1's list**, so every one is handed a complete filled vital set. Each row can then be answered like this:

```
Chest radiograph deferred: afebrile with SpO2 97%.
```

That names the finding in the Plan. **All three rows pass**, and the note has disposed of a documented abnormal on two numbers nobody measured. It is the output [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27) recorded verbatim, and the clinician read the finished note and agreed with the reasoning before anyone noticed the values were generated.

Naming a finding and dismissing it on invented grounds score identically here. B9 is the row that separates them, and it is DRIFT's cheat closed from the FILLED side — the same relationship B2 has to B3.

## FILLED — binary, all must pass

A third assertion class alongside DRIFT and REPORTED, defined in [fixtures/README](../README.md). Binary, like DRIFT.

**Enforced rather than counted, deliberately.** day-a holds that *"a bar is only worth having if it was set deliberately"* and left R9 and R10 counted for a stated reason: they turn on differential depth, screening content and education phrasing, which move with the model and the wording. Failing a run over those would be failing it over style.

These nine do not move with wording. Each resolves to a value or its absence — is there a blood pressure in the FILLED block, is it below 130 over 80, does the string naming it appear in the Assessment or the Plan, does the given value survive, does every one of the eight OLDCARTS headings carry something, is the severity a number, does a withheld workup cite a value the FILLED block declares. Two runs can word case 9 completely differently and still agree on all nine. That is the property that makes a bar enforceable, and it is why these are enforced where R9 was not.

**Two rows need a reader rather than a match, and both are bounded.** B2's second exit asks whether the Assessment calls the hypertension *controlled*, *treated*, *on therapy*, or names the medication — a code in a pre-existing list is not that, and neither is a monitoring instruction. B9 asks what a withholding decision rests on, and that is answered by joining the block to the sentence: take each decision not to act, list the values it cites, and look each one up in FILLED. Neither needs a taste. B8's second clause is not a third — it resolves the way B3's does, by whether something in the Plan answers the number.

**Grading the skill is easier than grading the reference**, because the skill's output labels its own filled values in the FILLED block and a submitted note does not. Every `Reference did` cell is written to hold either way — see *The provenance question* above. **B5 through B9 have no such cell**, and the reasons are below the table — a different one for B9 than for the four before it.

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| B1 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | A case whose shorthand carries no vitals is given a **complete filled set** — blood pressure, respiratory rate, height and weight, with BMI derived from the last two — each declared in the FILLED block | Any of the four is left blank, reported under GAPS, or silently omitted | **Produced a complete set on all nine** — blood pressure, pulse, respiratory rate, temperature, oxygen saturation, height, weight and a derived BMI on every one. Not a blank, not a GAPS line. Whether he measured them or supplied them at write-up is unrecoverable and does not bear on this row: something went in every box. Matching this is *neither*; anything less is *worse*. |
| B2 | 8 — 33 F, 9 — 44 F | The filled blood pressure for a patient with **documented hypertension** is either **not normal** — systolic 130 or above, *or* diastolic 80 or above — **or** normal *and* the Assessment names the hypertension as **controlled**, **treated**, or **on therapy**, or **names the medication** | A hypertensive with no recorded pressure is given a normal one and the note says nothing about why it is normal. A code in a pre-existing list is not an account, and neither is a monitoring instruction | **Split — one each way.** Case 9: 132/84, above on both limbs; passes on the first exit. Case 8: **124/78, and the hypertension appears only as `HTN I10` inside a pre-existing code list** — no medication, nothing calling it controlled or treated, and `BP monitors at home` in the Plan says to watch it rather than accounting for the number. Fails on both exits. Matching case 9 is *neither*; beating case 8 is *better*. |
| B3 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | Every **filled** vital or body measurement outside the normal range for that age is named in the Assessment or the Plan | It reaches the Objective and the FILLED block and stops | **Failed it everywhere it fired.** Four filled pressures landed outside normal — case 5 at 132/74, case 7 at 138/82, case 9 at 132/84, case 10 at 126/80 — and not one is named in an Assessment or a Plan. Case 9's filled **BMI of 37.8**, class II obesity, is not coded or mentioned anywhere at all. Naming them is *better*. |
| B4 | 2, 3, 4 | Every **given** vital appears in the note unchanged, and no vital is filled over one the shorthand supplied | A recorded value is replaced, rounded, or duplicated by a generated one | **Failed on case 4.** The given `ht 6'2"` — 74 inches — was recorded as `6'1" (73 in)`, and the BMI of 26.4 is derived from the altered value rather than the given one. Cases 2 and 3 came through unchanged, every value. Beating case 4 is *better*. |
| B5 | 1–12 | All eight OLDCARTS elements — onset, location, duration, character, aggravating, relieving, timing, severity — carry a value, and severity is written as a number out of 10 | Any element is blank, reads `not documented`, is reported under GAPS, or is dropped from the HPI. A severity written as a word — *moderate*, *severe* — fails too | Not scored. See below. |
| B6 | 1–12 | Every OLDCARTS element the shorthand does not supply is declared in `FILLED·asserted` **carrying its value** | The block names the field without its value, or omits the element. A complete HPI whose FILLED block cannot say which of the eight were invented fails | Not scored. See below. |
| B7 | 1, 2, 4, 5, 7, 8, 10, 11, 12 | A **given** severity survives. The seven cases that write a score carry that number unchanged — 8, 5, 2, 7, 8, 8 and 6 out of 10 on cases 1, 4, 5, 7, 8, 10 and 11 — and the two that write `no pain` are scored **0/10** | A written score is rounded, moved, or replaced by a generated one; or a documented absence of pain is scored above 0/10 | Not scored. See below. |
| B8 | 6, 9 | The severity is **filled**, lands **above 0/10**, and something in the Plan answers it — an analgesic, or the treatment of what is causing the pain | It lands at 0/10 for a patient with a sutured laceration or worsening facial pain; or it reaches the HPI and the FILLED block and the Plan responds to it with nothing | Not scored. See below. |
| B9 | 1, 3, 5, 6, 7, 8, 9, 10, 11, 12 | Every reassurance in the note traces to a **given**. No decision to withhold, defer or narrow the workup of a documented finding rests on a filled vital, body measurement or pain score, and any cause a filled abnormal is attributed to is a **given finding** | A filled normal is the ground for not acting: `Chest radiograph deferred: afebrile with SpO2 97%` on a case whose shorthand records no temperature and no saturation. A filled abnormal attributed to a filled cause fails too — a filled fever accounting for a filled pressure is both halves of one reassurance invented | Not scored. See below. |

### B1 through B3 are a chain, and each closes the one above

B3 is what [issue #8](https://github.com/mshamblin5150-code/clinical-skills/issues/8) asked for. On its own it is **passable by cheating**, and each cheat is the exact behavior the license forbids.

**B3 alone is passable by filling a bland value.** `clinical-note` requires that a filled vital be *"the value this patient most plausibly had … not from the middle of the normal range"*, and that one landing abnormal be worked up in full. But whether it lands abnormal is itself generated. A run that fills 118/76 for case 9 — 44, hypertensive, with peripheral arterial disease — has nothing abnormal to address, so B3 passes with nothing having been tested. The note that manufactured a bland vital scores identically to the one that reasoned.

**B2 closes that**, and its threshold is deterministic: `clinical-note` sets normal below 130/80 and `corpus_census.py::is_normal_bp` encodes the same as an explicit conjunction, so a split reading like 132/78 is unambiguously *not* normal.

**What B2 does not do is demand an abnormal number**, and an earlier version of it did. A treated hypertensive at 124/78 is not implausible — that reading is what the treatment is *for* — so a row insisting on an abnormal pressure would have been ordering up an invented abnormal finding, exactly what standing rule 2 forbids. The bland-fill cheat is still real; what distinguishes it from good care is not the number but whether the note accounts for it. Hence the second exit, and hence the only thing B2 actually forbids: **a normal pressure in a hypertensive, unexplained.**

**B2 alone is passable by filling nothing at all.** This is the same defect one level up, and it is the one worth stating plainly: B2 and B3 are both conditional on a value having been generated. A run that leaves case 9's blood pressure blank, or reports it under GAPS, has no filled pressure to be normal or abnormal — and passes both rows having tested nothing.

**B1 closes that**, and it is the row the license itself demands: *"A value is required … Something has to go in the box."* Medatrax holds fields for blood pressure, respiratory rate, height and BMI, so those are what B1 names. It is the precondition the other two rest on, which is why it comes first.

Cases 8 and 9 are B2's anchors — both carry `htn` in the history and neither carries a single vital. Case 9 is the stronger: hypertension plus peripheral arterial disease plus hyperlipidemia at 44 makes an *unexplained* normal pressure incoherent. Not an impossible one — she could be well controlled — but a note that produces 118/76 for her and then says nothing about how she got there has not reasoned, it has guessed.

**The reference read confirms the chain was not theoretical.** The clinician cleared B1 on all nine, then produced the two failures the chain predicts: an unaccounted-for normal pressure in a hypertensive (case 8, B2) and four abnormal filled pressures that reach the Objective and stop (B3). Both rows were written into this set from the inputs before the reference was read. Both fired.

**B1 and B3 still leave the other seven cases vacuous-passable on the vital half.** Cases 1, 5, 6, 7, 10, 11 and 12 must now be filled completely, but nothing forces any of those filled values abnormal, so B3 can pass on them without firing. Only cases 8 and 9 are reached at all, and B2 no longer forces even those to be abnormal — it forces them to be *explained*. That is a narrower hole than before and it is not closed.

### B5 through B8 are the same chain on the OLDCARTS half

[Issue #30](https://github.com/mshamblin5150-code/clinical-skills/issues/30) ruled that no OLDCARTS element may be blank and that severity is always a pain scale, taking the filled-vital treatment rather than the filled-finding one. These four are that ruling, and they are B1 → B2 → B3's argument again with the severity in the pressure's place.

**B8 alone is passable by filling nothing at all.** A run that leaves case 9's severity out, or writes `not documented`, has no score to be above 0/10 and passes having tested nothing. **B5 closes that**, and it is the row the ruling itself demands: eight, always eight.

**B5 alone is passable by writing 0/10 everywhere.** A blank is not the only way to say nothing — a note that scores every complaint at zero has satisfied every box while describing twelve patients in no pain, and one of them came in with a thumb laid open. That is *filled content is unremarkable* applied to a scale where unremarkable is a claim, which is exactly why the ruling put the severity in the vitals class. **B8 closes it**, on the two cases where the shorthand is silent and the complaint is unarguably painful.

**B5 and B8 together are passable by overwriting the givens.** Seven of these twelve write a score and two write the absence of one, so nine of the twelve have nothing to invent — and a run that "fills" a severity over `c/o 8/10 pain` has replaced a transcribed value, while a run that scores case 12 at 5/10 against `no pain` has invented a symptom outright. **B7 closes both**, and it is B4's job on this half: a given survives.

**B5 leaves the reader unable to tell which of the eight were invented**, which is the defect the FILLED block exists to prevent — the note body is written so given and filled content read identically. **B6 closes that**, on the rule `clinical-note` already states for a filled vital: the block carries the value, not the field name.

**The case lists are computed, not eyeballed.** `tools/test_corpus_census.py::DayBIsTheAbsenceSet` asserts the split from the committed inputs — which seven write a score and what it is, which two write `no pain`, which three write neither — so adding a score to one of these files fails a test instead of quietly voiding a row. The extractor it uses had a real bug that the guard found: two of the seven write the score at the end of a sentence, and the first version threw them away.

**Case 3 is the boundary, and B5 is the only one of these rows that reaches her.** Her complaint is itching, not pain. `clinical-note` rules on it — the scale still takes a number and names what it scores, `4/10 itching` — and it has to, because *eight, always eight* leaves no blank to fall back on. What the skill file cannot supply is a **ruled-on case**: #30 was raised about a patient in pain, so a row scoring case 3 would be this set enforcing the extension rather than the ruling. B5 still reaches her and forbids a blank. What no row here decides is whether **0/10** is the right answer for an itch. Listed under *Still unresolved*.

### B9 is the subtractive half of the license, and nothing else here reaches it

B1 through B3 and B5 through B8 are all one direction: a value gets generated, and the rows ask whether the note then did enough work. B9 is the other direction, and it is the one [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27) found — a generated value letting the note do **less** work. `clinical-note` states it as *a filled vital may raise an obligation and may never discharge one*.

**B9's ten cases are a union, not B1's nine.** The row reaches a case where *anything* in the license class was generated, so it is the vital-less nine plus **case 3**, whose vitals are complete and whose OLDCARTS severity the run has to invent — `DAY_B_SEVERITY_FILLED` in `tools/test_corpus_census.py`. Cases 2 and 4 are the only two outside it: both carry a full vital line and both settle the severity in the shorthand — case 4 with a score of 5, case 2 by writing `no pain`, which is a given scoring 0/10 rather than a value to invent. So a run has nothing generated to reason from and the row has nothing to check. Case 3 is easy to lose here, and the first draft of this row did lose her — she is B1's counter-example and B9's member at once, which is exactly the kind of split the case lists are computed rather than eyeballed to catch.

**No row above fires on it, which is worth being exact about.** Take the run [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27) reports, which filled case 9's `T 98.8 F` and `SpO2 97%`, both squarely normal. B1 passes — the box has a value. B3 never fires — the value is not abnormal, so there is nothing downstream to have lost. B2 reaches the pressure and says nothing about the other four. Every FILLED row in this set is satisfied by the run that deferred a chest film on two numbers nobody measured.

**And a filled normal is the harder case, not the easier one.** An invented abnormal has to be worked up and draws attention to itself doing it. An invented normal is what makes a workup stop, and it stops it in a sentence that reads like good clinical judgment. That asymmetry is why the row is worth its own line rather than a clause bolted onto B3.

**Two independent runs of case 9 both made the move, which is what takes B9 past a single anecdote.** The run [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27) reports filled `T 98.8 F` and `SpO2 97%` and deferred the film on them. **day-b run 1 filled different numbers and arrived at the same place** — it is committed, as [filled-anchor/notes/case-09.md](../filled-anchor/notes/case-09.md), and its Assessment reads:

> There are no wheezes, no crackles, no rhonchi, no shortness of breath and no hypoxia (SpO2 96% on room air, RR 18). Most consistent with reduced air movement in the setting of body habitus (BMI 35.2) plus the current acute upper respiratory illness, rather than a lower respiratory process.

Its own FILLED block declares all three numbers: `RR 18 filled`, `SpO2 96% on room air filled`, and a BMI derived from a filled height and a filled weight. **Every *number* in that sentence was generated**, and what they carry is the conclusion that the documented finding is not a lower respiratory process. No film is ordered; spirometry is deferred to *"once she is well."*

**The absent adventitious sounds in the same sentence are a different matter, and the row must not claim them.** `no wheezes, no crackles, no rhonchi` are filled *findings* — the shorthand mentions none of them — and `clinical-note` rules that filled findings keep their full force, because silence about a finding is evidence where silence about a vital is not. They may reassure. So the sentence is part legitimate reasoning and part invention, and B9 fails it on the numeric clause alone. That is the row at its narrowest, which is where it should be read.

**That run is the strongest argument for the row, because it is the careful one.** It heads the paragraph *"Diminished breath sounds — addressed, not filed"*, it names the finding, and it reaches the Assessment and the Plan — so D7 passes on it, and so do B1 and B3. Its own drift matrix records `Row 4 — Vitals: PASS`. A note doing everything the set asked still disposed of a documented abnormal on three invented numbers, and nothing in this file could see it. B9 is what sees it.

**What B9 catches is the stated dismissal, and it does not catch silence.** A run that simply orders no film, and says nothing at all, cites no value for the row to look up. That hole is real and it is covered here by the DRIFT side rather than this one: D2, D3 and D7 each demand their lung finding reach the Assessment or the Plan, so silence fails there. **The two halves are complete only together** — DRIFT forbids dropping the finding, B9 forbids disposing of it on an invented ground, and a run has to clear both.

**No reference verdict, and for a different reason than B5 through B8 carry none.** Those four were simply not scored in the 2026-08-11 read. B9 could not have been scored by it at all: a submitted note carries no tier block, so nothing in the reference says which of its values were measured, and *"deferred, afebrile"* in a portal note is unreadable either way. This is the asymmetry *Grading the skill is easier than grading the reference* records, in the one place where it is total rather than merely inconvenient.

### The reference was not re-opened for the HPI

The 2026-08-11 read answered the vital and drift questions this set was built on. **It was not scored for OLDCARTS**, so B5 through B8 carry no `Reference did` cell and no *better / worse / neither* verdict.

That is a smaller loss than it looks, and the reason is the one `obesity-bmi` states for its whole table: **every one of these four is anchored on the input and on the run's own output**, both readable without opening the portal. B7's nine values are in the committed shorthand. B5 and B6 are properties of the note the run produces. B8 asks what the run did with a number it invented, and a submitted note could not answer that even if it were read — it does not label its filled values, which is the asymmetry *Grading the skill is easier than grading the reference* already records.

**What the read would still add is the verdict**, and one of the four could genuinely turn on it. B5 is a claim about what a complete HPI looks like, and if the submitted notes leave OLDCARTS elements blank, then the row is one the reference fails — worth knowing, and the shape that reversed a day-b drift row once already. Filed as [#43](https://github.com/mshamblin5150-code/clinical-skills/issues/43), `ready-for-human` — the notes are un-de-identified PHI behind a signed-in portal session.

### Case 2's height: resolved, and B4 now covers it

Case 2's vital line reads `wt 62in wt 131` — `wt` written where `ht` was meant, the same defect day-a case 8 preserves as `hr 65 inches`. The set previously exempted case 2's height from B4, because the value was *given* under one reading and *absent* under the other and B4 would have punished a run for either choice.

**The reference settles it: 62 is a height.** The submitted note writes `5'2", 131 lb, BMI 24.0`, the portal Height field reads 62, and 131 lb at 62 in recomputes to 23.96 — so the BMI is derived from that reading and not from some other pair. The clinician was in the room; what the patient's height was is a fact he had and the shorthand mistyped.

**So the exemption is withdrawn and B4 covers all of case 2**, height included. A run that reads `62in` as a weight, or that treats the height as absent and fills one over it, fails B4. The suffix `in` is what makes this fair to enforce — it is a length whatever the label in front of it says.

This does **not** generalize to day-a case 8's `hr 65 inches`, which has no reference reading behind it in this set.

### The body-measurement half has an equivalent to B2, and this set cannot host it

Issue #8 asked for both halves — a filled vital and a filled body measurement — because [#7](https://github.com/mshamblin5150-code/clinical-skills/issues/7) widened drift row 4 to reach height, weight and a derived BMI.

**Delivered here:** B1 forces a height, a weight and a derived BMI on all nine cases, so the body measurement is always generated and always declared. B3 then covers it **whenever that BMI lands abnormal.**

**Settled on [#15](https://github.com/mshamblin5150-code/clinical-skills/issues/15), 2026-08-11.** The analogue is a real row and it is **not** contained in B3 — B3 fires only when the value lands abnormal, and the analogue fires on the *normal* branch, where a patient the shorthand calls obese is handed a BMI of 24 and nothing is said about it. There is no abnormal value for B3 to have lost, so B3 passes having tested nothing. The two rows are disjoint, not nested.

**What it needs is an anchor these twelve do not contain.** Cases 5 and 10 carry diabetes, which raises the odds of an obese BMI without documenting one; a row demanding an obese BMI from a documented diabetic would be demanding an invented abnormal finding, which standing rule 2 forbids outright. Nothing in this shift documents obesity itself.

**So the row lives in [obesity-bmi](../obesity-bmi/assertions.md) as O2**, on the two encounters in the whole corpus that write the word and supply no body measurement. This section is now a pointer rather than a gap: day-b's body-measurement half stays **conditional by construction**, and that is the correct answer for this shift rather than a hole in it.

**#15's own diagnosis of why was wrong, and it is worth recording which part.** The ticket held that the row could not be written at all, because any analogue would have to *force an abnormal BMI*. That was true of the **old** B2 and stopped being true when [#14](https://github.com/mshamblin5150-code/clinical-skills/issues/14) rewrote it: B2 no longer forces a value, it forces an account, and an account can be demanded of a normal value without ordering up an abnormal one. The obstacle was never the rule. It was the shift.

**The reference is evidence the gap matters.** The clinician generated a BMI of 37.8 for case 9 unprompted — from a shorthand that documents lymphedema, arthritis in both knees and a hip fracture, none of which requires it — and then addressed it nowhere. **B3 would already have fired on it**, which is the half this set does hold.

## CODING — binary, all must pass

A fourth assertion class alongside DRIFT, FILLED and REPORTED, defined in [fixtures/README](../README.md). Binary, on the same terms as the other two.

**It exists because [#19](https://github.com/mshamblin5150-code/clinical-skills/issues/19) put a code on every differential entry.** [SOAP.md](../../skills/clinical-note/SOAP.md) previously carried codes on the preexisting diagnoses and the final diagnosis and none on the differential; it now carries all three, and [drift row 13](../../skills/clinical-note/SKILL.md) is what checks it. That rule fires on **every output this set produces**, which makes it both the most-exercised rule the set can hold and the one that would erode most quietly — a differential with the codes missing reads perfectly well.

**C1 therefore spans all twelve rather than anchoring on one case.** The ticket that opened this class described two rows on case 9, and C2 is the one that needs case 9's particular input. C1 needs nothing particular: every case produces a differential, so scoping it to a single case would test one twelfth of a rule that fires twelve times and leave the other eleven outputs unchecked for free.

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| C1 | all twelve | Every entry in the Assessment's differential carries an ICD-10-CM code | Any entry carries none. **Two counts that either match or do not** — differential entries, and codes among them | **Not read for this row.** The submitted notes were read 2026-08-11 for the DRIFT and FILLED rows and were not examined for differential codes. What to check when they are: whether any submitted Assessment carries a coded differential at all, which would make matching it *neither* rather than *better*. |
| C2 | 9 — 44 F | The COVID-19 entry in the Assessment's differential carries a code **other than `U07.1`** | That entry's code **is** `U07.1`. The contact is documented and **no swab was taken**, so that descriptor asserts a disease nothing established | **Not read for this row**, and the reference cannot fail it in the same way: its Assessment carries no differential codes at all, so it has no code on that entry to be wrong. Producing `Z20.822 Contact with and (suspected) exposure to COVID-19` here is *better*; producing `U07.1` is *worse* than a note that coded nothing. |

**C2 is scoped to the code that entry carries, not to the string appearing anywhere.** An earlier wording failed when `U07.1` appeared anywhere in the output, and that would have failed a **correct** run: [icd10-cpt](../../skills/icd10-cpt/SKILL.md) step 4 *requires* the refused code be named — `NOT CODED: U07.1  COVID-19` — precisely so the clinician who gets a positive swab back tomorrow knows what it earns. A row that punished the refusal for naming what it refused would have inverted the rule it was written to hold. **Read the differential entry; the worksheet's refusal block is not the note.**

**Its pass and fail are complementary by construction**, which [fixtures/README](../README.md) asks of a binary row. The entry's code either is `U07.1` or it is not, and C1 is what guarantees there is a code to look at — without C1 an entry carrying none would resolve to neither. That is why these two rows ship together rather than C2 alone. Naming `Z20.822` as the expected shape stays commentary in the reference column, where a judgment is allowed; the row itself turns on one string.

**Case 9 is the only case in this set that can host C2.** The rule needs an input documenting a specific organism the encounter never tested for. Case 9 documents a positive COVID contact and orders no swab, which is the same property D6 rests on. Cases 8 and 12 document contacts too and **order the swab** — `covid` on case 8, `covid, strep, flu` on case 12 — so a run over either has a test to hang the diagnosis on and the row would not fire. Case 10 orders testing against no contact at all. That is the same reasoning that left D6 a single row.

**C2 and D6 are not the same row and neither contains the other.** D6 asks whether the Plan **orders the swab** — whether a documented given survived into an action. C2 asks what the Assessment **codes** when it has not. A run can pass D6 and fail C2 by ordering the swab and then coding `U07.1` as though the result were already in, and that is the more likely failure of the two: having written the order, the diagnosis feels established.

**Neither row is testable on a hedge in the input.** Zero of this set's twelve inputs carry a hedge token — verified by `tools/test_corpus_census.py` rather than asserted here — so #19's other half, what the skill does when the *shorthand itself* says `prob viral`, has no anchor in day-b and is owed a fixture of its own. Filed as [#49](https://github.com/mshamblin5150-code/clinical-skills/issues/49), which needs an encounter picked out of `scratch/` — [fixtures/README](../README.md) forbids authoring one.

## REPORTED — counted, not enforced

Four rows. R1 came out of the reference read, as a difference of the fourth class; **R2, R3 and R4 came out of [#29](https://github.com/mshamblin5150-code/clinical-skills/issues/29)**, which reversed most of what R1 originally claimed and left this set needing rows that say what a *passing* social history looks like rather than only what a failing one does. Counted rather than enforced on day-a's terms: *"a bar is only worth having if it was set deliberately"*.

**Run 1 scored `0/1`, and that score is now `0 of 1 row out of 4`.** Case 1 asserted an allergy status against a shorthand silent on allergies, plus an education level, a marital status and an occupational detail; case 2 asserted the allergy status again, plus an occupation and an education level.

**Two of those four assertions are correct under #29 and two are not**, which is the whole reason the row was rewritten rather than deleted. The allergy status is what [SOAP.md](../../skills/clinical-note/SOAP.md) instructs and what the corpus supports; the marital status `clinical-note` requires be inferred from age. The **occupation and the education level are grounded in nothing**, so the narrowed R1 still fails run 1 — the miss is real and it survives the reversal.

**R2 through R4 are ungraded from run 1, on this file's standing rule for that.** They exist because `clinical-note` changed, and those twelve notes were written before it changed, so a score from them would belong to neither commit. `REPORTED 0/1` is complete for the row and the commit it names, and **`0/4` is not what it means.**

**Two labels are in play here and they are not the same one.** The `Reference did` cell grades the *reference*, and it reads ***out of reach***: he asserted these having been in the room, which is what puts his version beyond the skill. Run 1's `0/1` grades the *skill*, and it is ***worse***: it was not in the room and asserted them anyway. #29 disturbs neither — it narrows *which* assertions count, and the two that survive are still ungrounded. (This paragraph read *"Graded worse, not out of reach"* and was briefly rewritten to say the opposite, which flipped the subject rather than the verdict.)

**The old rationale for keeping this counted is gone and a different one holds.** It used to read that R1 *"turns on phrasing"* — scoring whether a declaration reads as not-reported — which [fixtures/README](../README.md) disqualifies from being binary. **The narrowed row does not turn on phrasing at all**: it asks whether an asserted social detail is grounded in something the shorthand contains, which is a question about provenance and resolves the same way for any two runs. So all four rows could now be enforced, and *R2 through R4 are counted rather than binary* below says why they are not.

| # | Cases | Claim | Reference did |
| --- | --- | --- | --- |
| R1 | 1, 2 | No social detail the shorthand cannot **ground** is asserted — occupation and education are the two this set catches. `at work` grounds `Employed`; it does not ground `Works manual labor` | Asserted both. Case 1: `Social: Works manual labor` against a shorthand saying only that the injury happened `at work`, plus an education level. Case 2: an occupation and an education level, neither grounded in anything the shorthand carries. ***Out of reach*** — right in his note, forbidden in the skill's. |
| R2 | all twelve | Every social and allergy slot the branch template enumerates carries a value, and **none of them is a hedge** — no `not documented`, `not reported this visit`, `status unknown` or blank clause | Not read for this row. A submitted note is not scored for slot completeness here; what would settle it is [#43](https://github.com/mshamblin5150-code/clinical-skills/issues/43)'s read, which is already owed for B5. |
| R3 | all twelve | Every **filled** slot is declared in `FILLED·asserted` carrying its value — `SH tobacco Non-smoker filled`, not `social history filled` | **Unscoreable against the reference, permanently.** A submitted note carries no tier block, so it declares nothing and cannot pass or fail. Same position as B9. |
| R4 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | Where a **proposed** drug rests on an inferred allergy status, that `FILLED·asserted` line names the dependency. A drug the shorthand already ordered needs no such line — the prescription is the clinician's | Unscoreable, for R3's reason. |

### R1 was two claims and only one of them survived #29

The row previously read *"No social, allergy or medication detail is asserted where the shorthand supplies none. Absent or not-reported phrasing is the passing form"*, and it caught three things. [Issue #29](https://github.com/mshamblin5150-code/clinical-skills/issues/29) struck the first two and left the third.

**The allergy half is struck, and it was failing the skill for obeying its own template.** [SOAP.md](../../skills/clinical-note/SOAP.md) has always written `Allergies (reaction): <allergen - reaction; NKDA if none>` — the branch template **instructs** `NKDA` where the shorthand is silent, and this row scored it as a defect. That is precisely the objection the note below already made about case 2's inferred antihypertensive, arriving a second time in the same row and going unnoticed: *a row that failed it would be failing the skill for obeying its own instructions.*

**The corpus agrees with the template.** Over the 31 committed fixture inputs, **16 carry an allergy clause and 11 of the 16 say `NKDA`** — he fills that box whether or not there is anything in it, so silence is a transcription gap and `NKDA` is the value most plausibly held rather than a bland pick. Contrast the tobacco slot: 15 cases write it and **14 of 15 state a positive history**, so silence there is a real absence and a positive fill would be an invented abnormal. That asymmetry is why [day-a](../day-a/assertions.md) R14 survived intact while this half died. `tools/test_corpus_census.py::SocialSlotsSplitTwoWays` pins both splits per case.

**Case 2's reaction is struck with it.** `Allergies: Seasonal-itching/sneezing` against a bare `seasonal allergies` adds the reaction, and the template asks for one — `allergen - reaction`. Itching and sneezing are what seasonal allergies do, so the reaction is grounded in the given rather than invented beside it, which is the test the surviving half of this row now applies.

**The not-reported phrasing is struck as the *passing form*.** `Allergies (reaction): Not documented this visit` is a sentence that defends the note rather than reporting on the patient, which **drift row 12 has banned since [#28](https://github.com/mshamblin5150-code/clinical-skills/issues/28)**. This row was rewarding a row-12 violation. R2 is now what forbids it.

**What survives is the ungrounded biographical claim**, and it is the half the clinician's ruling never reached. `Works manual labor` is not an abnormal finding and not a sentence about this skill's process, so neither row 1 nor row 12 catches it — it is simply a fact about a patient's life that nothing in the encounter supplied. `at work` grounds `Employed` and stops there: nothing in a thumb laceration says manual labor rather than a paper cutter. That is [SKILL.md](../../skills/clinical-note/SKILL.md)'s own *grounded in what it contains, not invented beside it*, which was in the file the whole time and applied to the exam and the medication list but never to the `SH:` line. Drift row 16 is where it now gets walked.

**Run 1's `0/1` does not flip, and that is worth stating.** Run 1 asserted, on case 1, an allergy status plus an education level, a marital status and an occupational detail. Under #29 the allergy status is correct and the marital status is licensed outright — `clinical-note` instructs that it be inferred from age. **The education level and the occupation are still ungrounded**, so the narrowed row still fails that run. A reversal that retroactively awarded a pass would have been a reason to distrust the rewrite.

**One thing day-a's R14 has that this row does not.** R14 records *"Recalled from the encounters, not invented, per the clinician on 2026-08-11"* — he was asked, about those four. **He has not been asked about these**, so *out of reach* is carried over by analogy rather than confirmed. It does not change what the row demands. It changes only the label, and *worse* is the alternative.

**Case 1 is the row's own counter-example, in the same note.** It writes `Meds: None reported`, `No DM history reported` and `no PAD reported` — grounded absences, three times — and then `Works manual labor`. The distinction is available to him; it is not applied evenly.

### R2 through R4 are counted rather than binary, and they would qualify

Each resolves to a value or its absence, which is [fixtures/README](../README.md)'s stated criterion — count the template's slots, count the ones carrying a value, count the ones the block declares with a value, and read whether a withheld dependency is named. None of that moves with wording, so all three could be enforced.

**They are counted anyway, for two reasons.** Neither is about the rows' quality. The set already fails its binary bar at `FILLED 3/4` and has twelve rows never scored at all, so three more binary rows would widen a gap [#55](https://github.com/mshamblin5150-code/clinical-skills/issues/55) exists to close. And [#29](https://github.com/mshamblin5150-code/clinical-skills/issues/29) is one ruling landing in two sets: enforcing this set's half while day-a's waits would leave the two files holding the same rule to different standards. **The rows that ruling touches are five** — R1, R2, R3 and R4 here, and [day-a](../day-a/assertions.md) R14 — **and they are promoted together or not at all**, after run 2 has scored them once.

**They are R-numbered rather than B-numbered, and the reason is a genuine collision rather than a tidy rule.** By subject these belong to FILLED: [fixtures/README](../README.md) defines that class as *"what the skill does with a value the shorthand never supplied"*, which is exactly a filled slot value. By bar they belong to REPORTED, because the clinician ruled them counted. **README defines FILLED as binary in the same breath as defining its subject**, so a counted FILLED row is not a thing this repo has — `B10` would contradict the heading above it and `FILLED 3/7` would report a bar that was never set.

**The prefix follows the bar, because the bar is what a scorecard line reports.** `FILLED 3/4` and `REPORTED 0/4` are read off the `Last run` column, and a reader who cannot tell which rows a denominator covers cannot use it — which is the failure the row-count correction in [fixtures/README](../README.md) was made to stop. Subject is recoverable from the row text; the bar is not. **What this costs is that the class names no longer partition by subject alone**, and that cost is recorded rather than hidden: README now says which rows are counted for want of a run and which for turning on phrasing, because only the first kind is promotable.

**Case 2's `Meds: Unspecified antihypertensive` is deliberately not counted here.** The shorthand carries no meds line, so on its face it is the same defect — but [`clinical-note`](../../skills/clinical-note/SKILL.md) explicitly instructs the skill to *"infer the likely regimen"* in exactly that situation, and `Unspecified` is the hedge doing its job. A row that failed it would be failing the skill for obeying its own instructions. **The instruction survived [#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23)** and came out of it load-bearing: an inferred regimen is now one of the four things that can account for a normal filled pressure. So this stays uncounted for a stronger reason than it started with.

## What the reference surfaced that this set does not assert

Three defects in the submitted record are real and are **out of scope for a fixture whose inputs carry no dates and no portal fields.** They are recorded in `scratch/day-b-reference/README.md` so they are not lost:

- **Case 9's Visit Date is the day the note was typed, 78 days after the encounter.** The form's own date field carries the encounter date, so the two halves of the record disagree with each other. A date-range search for the shift therefore returns eleven of the twelve, and case 9 had to be found by patient creation order instead. (The dates themselves stay out of this file for the reason at the top of it.)
- **The shift had thirteen encounters, not twelve.** A thirteenth on the same date is not in the day file at all. A day file's note count is not a census of the shift.
- **Case 12's age is recorded as 18 against a shorthand that reads `16 yo F.`**, which put a pediatric hour into `Adult (18 – 60)`.

The inputs cannot test any of these: they carry no visit date, no portal entry fields, and the age is given correctly in the shorthand. Testing them needs a different kind of fixture than this one.

## Still unresolved

- **B3 fails, and the fix is not this set's to make.** Run 1 lost case 5's filled BMI between the FILLED block and the Assessment. The row is doing exactly its job; what it surfaced is a `clinical-note` behavior — an abnormal filled BMI addressed on six of the seven cases that produced one, and dropped on the seventh, which is the case with the busiest Plan. Filed as [#47](https://github.com/mshamblin5150-code/clinical-skills/issues/47), with peds-bp's identical P5 miss, and **not resolved by editing this row.**
- **Run 2 has not happened, and twelve rows have never been scored at all.** Run 1 is a first value over ten of the twenty-two, not a bar cleared: nothing exists yet to measure `DRIFT 5/5` and `FILLED 3/4` against, and `CODING n/n` has no value whatever. What run 1 does establish is that the assertions are checkable against real output by someone who did not produce it, and that they can fail a run whose own matrix says it passed. [#55](https://github.com/mshamblin5150-code/clinical-skills/issues/55).
- **B2's second exit has still never been exercised, and run 2 is the first chance it has.** [#26](https://github.com/mshamblin5150-code/clinical-skills/issues/26) expected run 1 to fail B2, as the visible cost of `clinical-note` and this row contradicting each other. It passed, and structurally rather than luckily: **B2's first exit is an abnormal pressure, and the rule as it then stood produced exactly that** — case 8 filled at 148/92 and case 9 at 146/90, both above on both limbs — so neither case reached the second exit and the clause the two documents fought over was never tested.

  **[#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23) has since been settled in B2's favor**, and that is what makes this worth keeping rather than deleting. The rule no longer orders up a hypertensive pressure, so a filled pressure for cases 8 and 9 may now legitimately land normal — which routes them to the **second** exit, the one asking whether the Assessment calls the hypertension controlled or treated. Run 1's `B2 PASS` was earned on a branch the skill can no longer be relied on to take. **Read it as untested rather than as a baseline**, and expect run 2 to say something different about the same row for reasons that are not a regression.
- **C1 and C2's `Reference did` cells are owed.** The reference read of 2026-08-11 was scoped to the rows that existed then, so nobody has looked at what the twelve submitted notes did about differential codes. Both rows are checkable against a run *today* — they assert on the skill's output text, not on the reference — so the set is not blocked. What is missing is the verdict: whether beating the reference here is *better* or merely *neither*. Re-reading `scratch/day-b-reference/` for that one question is a smaller job than the original read was.
- **Cases 6 and 12 are 17 and 16, and [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11) turned out not to reach them.** That issue asked whether a filled pediatric vital should be filled at all, and pointed here for the fixture. The corpus answered the boundary question first: measured 2026-08-11, a blood pressure going missing from a vital line that was otherwise written happens **only under 6** — every band from 9 up produces not one instance, and a 16-year-old is transcribed exactly like an adult. So these two are adolescent only in the sense that their filled values must suit their age, which B1 already demands. The ruling — filled, no exception — is fixtured in [peds-bp](../peds-bp/assertions.md), whose cases are young enough to test it.

  What is genuinely untested here is **B2's** analogue, not B1's: B2 reaches only cases 8 and 9 because only those two document a condition a normal value would owe an account of — *not* because a normal value is implausible there, which is the rationale the row was rewritten to drop, and neither of these adolescents documents one either way. (An earlier version of this bullet named B1 for that; B1's case list has covered 6 and 12 all along.)
- **Case 3's severity is the OLDCARTS boundary and no row here scores it.** Her complaint is itching. B5 forbids a blank; nothing says whether `0/10` or `4/10 itching` is right. `clinical-note` states the latter and had to state something, but [#30](https://github.com/mshamblin5150-code/clinical-skills/issues/30) was raised about a patient presenting in pain, so a row here would be fixturing the extension rather than the ruling. Cases 6 and 9 carry B8 instead. Filed as [#42](https://github.com/mshamblin5150-code/clinical-skills/issues/42), `grilling` — the corpus cannot settle it, because this is the case where he wrote nothing. The answer belongs in the skill file and this set together.
- **B5 through B8 have no reference verdict**, for the reason above. B5 is the one that could plausibly turn on it. [#43](https://github.com/mshamblin5150-code/clinical-skills/issues/43).
- **The social-slot split rests on 31 fixture cases and not on the corpus.** `tools/corpus_census.py` gained the two extractors on [#29](https://github.com/mshamblin5150-code/clinical-skills/issues/29) and **has not been run against `scratch/` since** — the figures quoted for R1, R2 and day-a's R14 are a floor over the committed inputs. 14 of 15 tobacco clauses positive against 11 of 16 allergy clauses saying `NKDA` is a direction a wider count is unlikely to reverse, and a direction is what the rows turn on; the numbers themselves should not be quoted as the corpus until someone with `scratch/` runs it.
- **R2 needs a reference read and R3 and R4 can never have one.** R2 asks whether the submitted notes leave social slots blank or hedged, which is readable off the portal on [#43](https://github.com/mshamblin5150-code/clinical-skills/issues/43)'s session alongside B5 and D7 — one read, three rows. R3 and R4 are in B9's permanent position: a submitted note carries no tier block, so it cannot declare a filled value or name a dependency, and no amount of reading will change that.
- **D7 has no reference verdict either, and it is worth getting.** Unlike B9 — which a submitted note cannot answer at all, since it labels no filled values — D7 asks only whether case 9's `lung sounds diminished` reached the Assessment or the Plan, and that is readable off the portal note the way D1 through D4 were. It rides on [#43](https://github.com/mshamblin5150-code/clinical-skills/issues/43)'s read rather than needing its own: same twelve notes, same signed-in session.
- **B9's pain-score limb rests on a ruling nobody made.** [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27) put the OLDCARTS severity inside drift row 15's class and never asked what that does about row 4, whose normal range for the scale is one value wide. The pass implementing it ruled that a filled `0/10` is not a discharge — no obligation arose — and shipped that. The alternative is that generating a zero into a silent box is exactly a filled value withholding a treatment. **B8 covers the two cases where it would bite hardest**, cases 6 and 9, so what actually turns on the answer is **case 3**, whose own score is open at [#42](https://github.com/mshamblin5150-code/clinical-skills/issues/42) and whom B8 does not reach. B9's membership is unchanged either way; what changes is what the row demands of her. [#59](https://github.com/mshamblin5150-code/clinical-skills/issues/59), and it wants settling before run 2 scores B9.
- **B9 leaves the silent withholding untested outside the three lung cases.** A run that declines a workup and cites nothing has no value for B9 to look up. D2, D3 and D7 cover that for cases 1, 11 and 9, because a dropped finding fails on the DRIFT side. The other six of B9's nine have no such backstop — a run could quietly not act and clear both halves. Narrower than the hole [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27) opened, and not closed.
- **A diabetic was given a steroid burst with no glucose comment** — case 10, methylprednisolone 125 mg IM plus a dose pack, `DM2 E11.9` coded in the same note. Case 5 has the shape too: diabetes carried into the HPI and absent from the Assessment. It is a plan-safety defect rather than a finding abandoned, so it does not fit the DRIFT shape, and a row turning on whether a caution was *worded* would belong in REPORTED — which this set does not define. Left out deliberately.
