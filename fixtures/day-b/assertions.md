# day-b — assertion set

Twelve encounters from a single walk-in shift, 2025. Visit date and site removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

This set exists for one thing day-a cannot test: **what the skill does with a vital it had to invent.** Every day-a case carries a complete vital line, so nothing there exercises the filled half of the license. Nine of these twelve carry no vital at all.

**It now carries the OLDCARTS half of the same license.** [Issue #30](https://github.com/mshamblin5150-code/clinical-skills/issues/30) admitted a third member to the filled class — the HPI severity — and it was found on **case 9 of this set**, whose run wrote `Aggravating - not documented ... Severity - not documented`. B5 and B6 are that half, and they reach **all twelve** rather than B1's nine — a case can carry a full vital line and still leave seven OLDCARTS boxes empty, so the two splits are independent. B7 and B8 then divide the twelve on where the severity comes from, which is a third split again: seven cases write a score, two write the absence of one, three write neither.

Opened for [issue #8](https://github.com/mshamblin5150-code/clinical-skills/issues/8).

## Status — both halves built

**The inputs are in.** All twelve encounters are in [shorthand/](shorthand/), one file per case, de-identified.

**The reference is read.** All twelve submitted notes were opened in the portal on 2026-08-11 and are kept, un-de-identified, in `scratch/day-b-reference/` — gitignored, because they carry the visit date, the site, a named outside physician and the patient references. Every row below now records what the submitted note actually did.

**Inputs must come from the day file, never from the generated notes**, and the same trap applies to the reference half. That is why the rule below stood:

> ~~Until it is, no drift row may be added to this set.~~ **Lifted 2026-08-11.** The reference is read, so a drift row can now be checked against what the submitted note did rather than against the skill's own prior output.

The rule was day-a's, and it was worth keeping: four of day-a's six DRIFT rows changed when its reference was finally read, and two had claimed the clinician abandoned a finding he had in fact carried into the Assessment and the Plan.

**Here it changed one of five.** D1 through D4 turn out to say what a careful read of the input would have said. D5 is the exception, and in the direction the rule exists to catch: the submitted note **addressed** the low magnesium, so a row asserting it was abandoned would have been false. Its `Reference did` cell reads *neither*, not *better*, and it is the set's only anti-regression row.

**D6 arrived after that count and is not in it.** It comes from [#32](https://github.com/mshamblin5150-code/clinical-skills/issues/32) — a `clinical-note` run over case 9, not the reference read — and the read is what lets it carry a verdict at all.

**The set has never been run.** `DRIFT n/n`, `FILLED n/n` and `REPORTED n/m` have no first value yet.

## The reference is a baseline, not a target

Same four verdicts as [day-a](../day-a/assertions.md), and only *worse* is a regression. The `Reference did` columns below say which:

- **Better** — the skill caught something the submitted note dropped.
- **Worse** — the skill lost something the submitted note had. The most important thing this set can find.
- **Neither** — different wording for the same content.
- **Out of reach** — the submitted note is better on information the skill never had. The clinician was in the room; the skill has the shorthand and nothing else. Matching this is not a target and failing it is not a regression — **the skill is required not to try.**

**The fourth class arrived while this set could not host it.** It was added to day-a on 2026-08-11, and the commit that added it recorded why day-b was left on three: *"neither has read its reference, so neither can host the class yet, and both belong to other tickets."* This is that other ticket. day-b's one row of the class is **R1**, below.

**Reading it moved this set in both directions.** It supplied five drift rows the set was forbidden to carry, and it also **failed two of the four FILLED rows the set held then** — B4 on case 4 and B2 on case 8. (B5 through B8 arrived after the read and carry no verdict from it; see below.) A bar the reference clears everywhere is a bar set too low; a bar it fails is where the skill has something to be better than.

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

**Five of the six are findings the submitted note did drop. D5 is not** — see below the table.

| # | Case | The finding | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| D1 | 3 — 57 F | BP 147/81, with `htn` in the history | The elevated pressure is not named in the Assessment or the Plan. **A bare `BP` inside an age-based screening list is not a naming** — see below | Recorded it in the Objective and the portal field and stopped. The Assessment names scabies, traumatic otitis externa and tobacco use; **`hx htn` is dropped from the note entirely** — no I10, no recheck, no home log. Addressing it is *better*. |
| D2 | 1 — 36 M | Breath sounds diminished in all four fields, in a 1 PPD × 24-year smoker | Not named in the Assessment or the Plan | Carried it into the Objective and stopped. The Assessment codes `Tobacco use (Z72.0)` but never the finding; no spirometry, no film, no COPD consideration. Naming it is *better*. |
| D3 | 11 — 32 M | Inspiratory wheezing in all fields, in a documented asthmatic | Absent from the Assessment or the Plan | Recorded it on exam, then **recast it in the HPI as `inspiratory wheeze history`** — past tense — and carried asthma only in the *pre-existing* code list. No inhaler, no peak flow, no asthma plan item. Addressing it is *better*. |
| D4 | 7 — 67 F | Elevated liver enzymes — AST 48, ALP 136 — in a patient on a statin | The elevated enzymes are absent from the Assessment or the Plan | **Dropped them.** No AST, no ALP, no statin and no hepatic follow-up anywhere in the note, and a CMP ordered without saying why. The shorthand had already written the follow-up (`f/u pcp re elevated lft`). Keeping it is *better*. |
| D5 | 10 — 48 M | Magnesium 1.6, written in the shorthand as `labs good mg 1.6` | The low magnesium is absent from the Assessment or the Plan | **Caught it** — `Mg 1.6 → recommend OTC magnesium supplement`. Matching this is *neither*; losing it is *worse*. |
| D6 | 9 — 44 F | A documented positive COVID contact — `daughter inall was postive for covid` — alongside a congruent respiratory presentation | The Plan does not order COVID-19 testing and influenza testing, with a specimen named. Group A strep is required too, because this input documents the pharynx — `sore throat` and `pharyngeal erythema`. **Carrying the exposure in the HPI is not acting on it** — see below | **Ordered no testing at all.** The exposure reached the note — the HPI reads `COVID exposure in family` — and the Plan carries amoxicillin-clavulanate, a steroid dose pack, otic drops and an IM steroid, with no swab of any kind. Ordering it is *better*. |

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

## FILLED — binary, all must pass

A third assertion class alongside DRIFT and REPORTED, defined in [fixtures/README](../README.md). Binary, like DRIFT.

**Enforced rather than counted, deliberately.** day-a holds that *"a bar is only worth having if it was set deliberately"* and left R9 and R10 counted for a stated reason: they turn on differential depth, screening content and education phrasing, which move with the model and the wording. Failing a run over those would be failing it over style.

These eight do not move with wording. Each resolves to a value or its absence — is there a blood pressure in the FILLED block, is it below 130 over 80, does the string naming it appear in the Assessment or the Plan, does the given value survive, does every one of the eight OLDCARTS headings carry something, is the severity a number. Two runs can word case 9 completely differently and still agree on all eight. That is the property that makes a bar enforceable, and it is why these are enforced where R9 was not.

**B2's second exit is the one word of judgment in the table**, and it is bounded: does the Assessment call the hypertension *controlled*, *treated*, *on therapy*, or name the medication. A code in a pre-existing list is not that, and neither is a monitoring instruction. Scoring it needs a reader, not a taste. B8's second clause is not a second one — it resolves the way B3's does, by whether something in the Plan answers the number.

**Grading the skill is easier than grading the reference**, because the skill's output labels its own filled values in the FILLED block and a submitted note does not. Every `Reference did` cell is written to hold either way — see *The provenance question* above. **B5 through B8 have no such cell**, and the reason is below the table.

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| B1 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | A case whose shorthand carries no vitals is given a **complete filled set** — blood pressure, respiratory rate, height and weight, with BMI derived from the last two — each declared in the FILLED block | Any of the four is left blank, reported under GAPS, or silently omitted | **Produced a complete set on all nine** — blood pressure, pulse, respiratory rate, temperature, oxygen saturation, height, weight and a derived BMI on every one. Not a blank, not a GAPS line. Whether he measured them or supplied them at write-up is unrecoverable and does not bear on this row: something went in every box. Matching this is *neither*; anything less is *worse*. |
| B2 | 8 — 33 F, 9 — 44 F | The filled blood pressure for a patient with **documented hypertension** is either **not normal** — systolic 130 or above, *or* diastolic 80 or above — **or** normal *and* the Assessment names the hypertension as **controlled or treated** | A hypertensive with no recorded pressure is given a normal one and the note says nothing about why it is normal | **Split — one each way.** Case 9: 132/84, above on both limbs; passes on the first exit. Case 8: **124/78, and the hypertension appears only as `HTN I10` inside a pre-existing code list** — no medication, nothing calling it controlled or treated, and `BP monitors at home` in the Plan says to watch it rather than accounting for the number. Fails on both exits. Matching case 9 is *neither*; beating case 8 is *better*. |
| B3 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | Every **filled** vital or body measurement outside the normal range for that age is named in the Assessment or the Plan | It reaches the Objective and the FILLED block and stops | **Failed it everywhere it fired.** Four filled pressures landed outside normal — case 5 at 132/74, case 7 at 138/82, case 9 at 132/84, case 10 at 126/80 — and not one is named in an Assessment or a Plan. Case 9's filled **BMI of 37.8**, class II obesity, is not coded or mentioned anywhere at all. Naming them is *better*. |
| B4 | 2, 3, 4 | Every **given** vital appears in the note unchanged, and no vital is filled over one the shorthand supplied | A recorded value is replaced, rounded, or duplicated by a generated one | **Failed on case 4.** The given `ht 6'2"` — 74 inches — was recorded as `6'1" (73 in)`, and the BMI of 26.4 is derived from the altered value rather than the given one. Cases 2 and 3 came through unchanged, every value. Beating case 4 is *better*. |
| B5 | 1–12 | All eight OLDCARTS elements — onset, location, duration, character, aggravating, relieving, timing, severity — carry a value, and severity is written as a number out of 10 | Any element is blank, reads `not documented`, is reported under GAPS, or is dropped from the HPI. A severity written as a word — *moderate*, *severe* — fails too | Not scored. See below. |
| B6 | 1–12 | Every OLDCARTS element the shorthand does not supply is declared in `FILLED·asserted` **carrying its value** | The block names the field without its value, or omits the element. A complete HPI whose FILLED block cannot say which of the eight were invented fails | Not scored. See below. |
| B7 | 1, 2, 4, 5, 7, 8, 10, 11, 12 | A **given** severity survives. The seven cases that write a score carry that number unchanged — 8, 5, 2, 7, 8, 8 and 6 out of 10 on cases 1, 4, 5, 7, 8, 10 and 11 — and the two that write `no pain` are scored **0/10** | A written score is rounded, moved, or replaced by a generated one; or a documented absence of pain is scored above 0/10 | Not scored. See below. |
| B8 | 6, 9 | The severity is **filled**, lands **above 0/10**, and something in the Plan answers it — an analgesic, or the treatment of what is causing the pain | It lands at 0/10 for a patient with a sutured laceration or worsening facial pain; or it reaches the HPI and the FILLED block and the Plan responds to it with nothing | Not scored. See below. |

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

## REPORTED — counted, not enforced

One row, and it exists because the reference read produced a difference of the fourth class. Counted rather than enforced on day-a's terms: *"a bar is only worth having if it was set deliberately"*, and this one has not been run even once.

| # | Cases | Claim | Reference did |
| --- | --- | --- | --- |
| R1 | 1, 2 | No social, allergy or medication detail is asserted where the shorthand supplies none. Absent or not-reported phrasing is the passing form | Asserted three. Case 1: `Social: Works manual labor` against a shorthand saying only that the injury happened `at work`, and `Allergies: NKDA` against a shorthand silent on allergies. Case 2: `Allergies: Seasonal-itching/sneezing` against a bare `seasonal allergies` — the reaction is new. ***Out of reach*** — right in his note, forbidden in the skill's. |

**This is day-a's R14 with two cases instead of four**, and it is the same argument: he was in the room and knew these; the skill has the shorthand and would be inventing them. His note is right and the skill's would not be.

**One thing day-a's R14 has that this row does not.** R14 records *"Recalled from the encounters, not invented, per the clinician on 2026-08-11"* — he was asked, about those four. **He has not been asked about these three**, so *out of reach* is carried over by analogy rather than confirmed. It does not change what the row demands: the skill is forbidden to assert them whether he recalled them or invented them. It changes only the label, and *worse* is the alternative.

**Case 1 is the row's own counter-example, in the same note.** It writes `Meds: None reported`, `No DM history reported` and `no PAD reported` — the passing form, three times — and then `Works manual labor`. The distinction is available to him; it is not applied evenly.

**Case 2's `Meds: Unspecified antihypertensive` is deliberately not counted here.** The shorthand carries no meds line, so on its face it is the same defect — but [`clinical-note`](../../skills/clinical-note/SKILL.md) explicitly instructs the skill to *"infer the likely regimen"* in exactly that situation, and `Unspecified` is the hedge doing its job. A row that failed it would be failing the skill for obeying its own instructions. Whether that instruction should survive is [#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23).

## What the reference surfaced that this set does not assert

Three defects in the submitted record are real and are **out of scope for a fixture whose inputs carry no dates and no portal fields.** They are recorded in `scratch/day-b-reference/README.md` so they are not lost:

- **Case 9's Visit Date is the day the note was typed, 78 days after the encounter.** The form's own date field carries the encounter date, so the two halves of the record disagree with each other. A date-range search for the shift therefore returns eleven of the twelve, and case 9 had to be found by patient creation order instead. (The dates themselves stay out of this file for the reason at the top of it.)
- **The shift had thirteen encounters, not twelve.** A thirteenth on the same date is not in the day file at all. A day file's note count is not a census of the shift.
- **Case 12's age is recorded as 18 against a shorthand that reads `16 yo F.`**, which put a pediatric hour into `Adult (18 – 60)`.

The inputs cannot test any of these: they carry no visit date, no portal entry fields, and the age is given correctly in the shorthand. Testing them needs a different kind of fixture than this one.

## Still unresolved

- **`clinical-note` still says what B2 stopped saying.** [SKILL.md](../../skills/clinical-note/SKILL.md) reads *"A known hypertensive seen for a productive cough gets a hypertensive pressure"* — the rule B2 was written to fixture, and the one the clinician's *"she may be compliant with her BP meds"* contradicts. The same file also tells the skill to **infer a likely regimen** where a hypertensive history carries no `meds:` line, and to propose *"lisinopril where the history carries hypertension"*. So it currently instructs the skill to put a patient on an ACE inhibitor and then hand her a hypertensive pressure anyway. **B2 was changed and the skill rule was not**, deliberately: rewriting a clinical rule is the clinician's call and it would ripple into `peds-bp` and drift row 4. Filed as [#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23).
- **The set has never been run.** Until it is, `DRIFT n/n`, `FILLED n/n` and `REPORTED n/m` have no first value to measure drift from — and a first run graded by the pass that produced it is a baseline, not a pass ([fixtures/README](../README.md)).
- **Cases 6 and 12 are 17 and 16, and [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11) turned out not to reach them.** That issue asked whether a filled pediatric vital should be filled at all, and pointed here for the fixture. The corpus answered the boundary question first: measured 2026-08-11, a blood pressure going missing from a vital line that was otherwise written happens **only under 6** — every band from 9 up produces not one instance, and a 16-year-old is transcribed exactly like an adult. So these two are adolescent only in the sense that their filled values must suit their age, which B1 already demands. The ruling — filled, no exception — is fixtured in [peds-bp](../peds-bp/assertions.md), whose cases are young enough to test it.

  What is genuinely untested here is **B2's** analogue, not B1's: B2 reaches only cases 8 and 9 because only those two document a condition making a normal value implausible, and neither of these adolescents does. (An earlier version of this bullet named B1 for that; B1's case list has covered 6 and 12 all along.)
- **Case 3's severity is the OLDCARTS boundary and no row here scores it.** Her complaint is itching. B5 forbids a blank; nothing says whether `0/10` or `4/10 itching` is right. `clinical-note` states the latter and had to state something, but [#30](https://github.com/mshamblin5150-code/clinical-skills/issues/30) was raised about a patient presenting in pain, so a row here would be fixturing the extension rather than the ruling. Cases 6 and 9 carry B8 instead. Filed as [#42](https://github.com/mshamblin5150-code/clinical-skills/issues/42), `grilling` — the corpus cannot settle it, because this is the case where he wrote nothing. The answer belongs in the skill file and this set together.
- **B5 through B8 have no reference verdict**, for the reason above. B5 is the one that could plausibly turn on it. [#43](https://github.com/mshamblin5150-code/clinical-skills/issues/43).
- **A diabetic was given a steroid burst with no glucose comment** — case 10, methylprednisolone 125 mg IM plus a dose pack, `DM2 E11.9` coded in the same note. Case 5 has the shape too: diabetes carried into the HPI and absent from the Assessment. It is a plan-safety defect rather than a finding abandoned, so it does not fit the DRIFT shape, and a row turning on whether a caution was *worded* would belong in REPORTED — which this set does not define. Left out deliberately.
