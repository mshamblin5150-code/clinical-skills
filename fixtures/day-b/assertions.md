# day-b — assertion set

Twelve encounters from a single walk-in shift, 2025. Visit date and site removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

This set exists for one thing day-a cannot test: **what the skill does with a vital it had to invent.** Every day-a case carries a complete vital line, so nothing there exercises the filled half of the license. Nine of these twelve carry no vital at all.

Opened for [issue #8](https://github.com/mshamblin5150-code/clinical-skills/issues/8).

## Status — one half, deliberately

**The inputs are in.** All twelve encounters are in [shorthand/](shorthand/), one file per case, de-identified.

**The reference has not been read, and that is a stated scope, not a missing half.** The reference answers *better / worse / neither* about a finding the **shorthand recorded**. A filled vital was never in the shorthand, so there is nothing for the submitted note to have drifted from — the rows below are entirely about the skill's own generated content, and they are checkable without it.

**The reference is owed, not unnecessary.** The point of the fixture system is that the skill compares its output against what was actually recorded in the portal and beats it. day-b will not do that until its reference is read.

> **Until it is, no drift row may be added to this set.**

That is the rule day-a paid for. Four of its six DRIFT rows changed when its reference was finally read, and two — D3 and D5 — had claimed the clinician abandoned a finding he had in fact carried into the Assessment and the Plan. Both were written from the skill's own prior output. A row derived from output that has no reference to check it against agrees with itself forever.

The rows below are safe under that rule because each is anchored on the **input**: the absence of a vital is a property of the shorthand, readable before any run happens.

**The set has never been run.** `FILLED n/n` has no first value yet.

## FILLED — binary, all must pass

A third assertion class alongside DRIFT and REPORTED, defined in [fixtures/README](../README.md). Binary, like DRIFT.

**Enforced rather than counted, deliberately.** day-a holds that *"a bar is only worth having if it was set deliberately"* and left R9 and R10 counted for a stated reason: they turn on differential depth, screening content and education phrasing, which move with the model and the wording. Failing a run over those would be failing it over style.

These four do not move with wording. Each resolves to a value or its absence — is there a blood pressure in the FILLED block, is it below 130 over 80, does the string naming it appear in the Assessment or the Plan, does the given value survive. Two runs can word case 9 completely differently and still agree on all four. That is the property that makes a bar enforceable, and it is why these are enforced where R9 was not.

| # | Cases | Passes when | Fails when |
| --- | --- | --- | --- |
| B1 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | A case whose shorthand carries no vitals is given a **complete filled set** — blood pressure, respiratory rate, height and weight, with BMI derived from the last two — each declared in the FILLED block | Any of the four is left blank, reported under GAPS, or silently omitted |
| B2 | 8 — 33 F, 9 — 44 F | The filled blood pressure for a patient with **documented hypertension** is **not normal** — normal being systolic below 130 *and* diastolic below 80 | A hypertensive with no recorded pressure is given a normal one |
| B3 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | Every **filled** vital or body measurement outside the normal range for that age is named in the Assessment or the Plan | It reaches the Objective and the FILLED block and stops |
| B4 | 2, 3, 4 | Every **given** vital appears in the note unchanged, and no vital is filled over one the shorthand supplied | A recorded value is replaced, rounded, or duplicated by a generated one |

### The three rows are a chain, and each closes the one above

B3 is what [issue #8](https://github.com/mshamblin5150-code/clinical-skills/issues/8) asked for. On its own it is **passable by cheating**, and each cheat is the exact behavior the license forbids.

**B3 alone is passable by filling a bland value.** `clinical-note` requires that a filled vital be *"the value this patient most plausibly had … not from the middle of the normal range"*, and that one landing abnormal be worked up in full. But whether it lands abnormal is itself generated. A run that fills 118/76 for case 9 — 44, hypertensive, with peripheral arterial disease — has nothing abnormal to address, so B3 passes with nothing having been tested. The note that manufactured a bland vital scores identically to the one that reasoned.

**B2 closes that, and is deterministic.** `clinical-note` sets normal below 130/80 and `corpus_census.py::is_normal_bp` encodes the same threshold as an explicit conjunction, so a split reading like 132/78 is unambiguously *not* normal and B2 fires on it. Checkable against the output text without judgment.

**B2 alone is passable by filling nothing at all.** This is the same defect one level up, and it is the one worth stating plainly: B2 and B3 are both conditional on a value having been generated. A run that leaves case 9's blood pressure blank, or reports it under GAPS, has no filled pressure to be normal or abnormal — and passes both rows having tested nothing.

**B1 closes that**, and it is the row the licence itself demands: *"A value is required … Something has to go in the box."* Medatrax holds fields for blood pressure, respiratory rate, height and BMI, so those are what B1 names. It is the precondition the other two rest on, which is why it comes first.

Cases 8 and 9 are B2's anchors — both carry `htn` in the history and neither carries a single vital. Case 9 is the stronger: hypertension plus peripheral arterial disease plus hyperlipidemia at 44 makes a normal pressure not merely unlikely but clinically incoherent.

**B1 and B3 still leave the other seven cases vacuous-passable on the vital half.** Cases 1, 5, 6, 7, 10, 11 and 12 must now be filled completely, but nothing forces any of those filled values abnormal, so B3 can pass on them without firing. Only cases 8 and 9 are forced. That is a narrower hole than before and it is not closed — closing it needs a documented condition per case that makes a normal value implausible, which these seven do not supply.

### Case 2 is exempt from B4 on its height

Case 2's vital line reads `wt 62in wt 131` — `wt` written where `ht` was meant, the same defect day-a case 8 preserves as `hr 65 inches`. So the height is *given* under one reading and *absent* under the other, and B4 would punish a run for either choice.

**B4 therefore covers case 2's blood pressure, pulse, temperature, respiratory rate, oxygen saturation and weight, and says nothing about its height.** Cases 3 and 4 are covered in full. Which reading is correct is listed under *Still unresolved*.

### The body-measurement half has no equivalent to B2

Issue #8 asked for both halves — a filled vital and a filled body measurement — because [#7](https://github.com/mshamblin5150-code/clinical-skills/issues/7) widened drift row 4 to reach height, weight and a derived BMI.

**Delivered:** B1 forces a height, a weight and a derived BMI on all nine cases, so the body measurement is always generated and always declared. B3 then covers it **whenever that BMI lands abnormal.**

**Not delivered:** nothing forces it to land abnormal, and that gap is real rather than an oversight:

- Hypertension is documented, and it makes a normal blood pressure affirmatively implausible. That is what B2 rests on.
- **No condition in these twelve does the same for BMI.** Cases 5 and 10 carry diabetes, which raises the odds of an obese BMI without requiring one. A row demanding an obese BMI from a documented diabetic would be demanding an invented abnormal finding — the thing standing rule 2 exists to forbid.

So a run can satisfy this set while never generating an abnormal BMI at all. Closing it needs a case whose shorthand documents obesity without a weight, and none of these twelve does.

## Still unresolved

- **The set has never been run.** Until it is, `FILLED n/n` has no first value to measure drift from — and a first run graded by the pass that produced it is a baseline, not a pass ([fixtures/README](../README.md)).
- **The reference.** Owed, per *Status* above. Reading it is what would let day-b carry drift rows and answer *better / worse / neither*.
- **Case 3's `bp 147/81` is a given abnormal and this set claims nothing about it.** It is drift-class — the pass condition would be readable from the output alone — but it is a row about a *recorded* finding, and those are exactly what the no-drift-rows rule defers until the reference is read. Promote it deliberately, with the reference, or not at all.
- **Case 2's `wt 62in wt 131` writes `wt` where `ht` was meant**, the same defect day-a case 8 preserves as `hr 65 inches`. Whether the skill reads 62 inches as a height is untested here.
- **Cases 6 and 12 are 17 and 16.** Their filled vitals are adolescent, not adult, and B1 does not reach them because neither carries hypertension. Whether a filled pediatric vital should be filled at all is a live question — [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11).
