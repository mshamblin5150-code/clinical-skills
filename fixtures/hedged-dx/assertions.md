# hedged-dx — assertion set

Three encounters from three separate day files, 2025–2026. Visit dates and site names removed per [fixtures/README](../README.md). Skill: `clinical-note`, comprehensive SOAP branch.

This set exists for one thing `day-b` cannot test: **what the skill does when the clinician's own shorthand hedges a diagnosis.** Zero of `day-b`'s twelve inputs carry a hedge token, which that set's own file records — so [drift row 13](../../skills/clinical-note/SKILL.md)'s second half has been checked only against a diagnosis the *skill* generated, never against one the clinician wrote hedged. Opened for [issue #49](https://github.com/mshamblin5150-code/clinical-skills/issues/49).

Which three encounters, how they were selected out of seventeen candidates, and what the inputs are known to leave out are in [shorthand/README.md](shorthand/README.md) and are deliberately not restated here.

## Status — inputs in, run 1 scored, five rows added under it, reference owed

**Run 1, 2026-08-15: `CODING 5/5` · `DRIFT 1/1` · `REPORTED 1/1`.** Those three classes were scored on the day and the run passes every row in them. **`NAMING` did not exist yet**, was added under the run later the same day, and is scored here retrospectively: **`N3` passes, `N1` and `N2` fail, and `N4` cannot be scored at all.** That is deliberately not written as a fraction — three of the four rows have verdicts and the fourth has none, so any denominator would either hide the unscoreable row or count it as a loss. A reader taking the three fractions above as the set's verdict is reading a set that has since grown a class. Three generating passes with the shorthand pasted inline and `fixtures/` declared closed; two grading passes split by class, neither having written a note; an orchestrating pass that authored none and re-derived every quotation from the output text.

**That was `7` rows and this section called it six**, in two places, until [#151](https://github.com/mshamblin5150-code/clinical-skills/issues/151) counted them: `C1`–`C5`, `D1`, `R1`. The digits `5/5`, `1/1` and `1/1` were right the whole time and their total was written down wrong — **which is this section's own subject arriving in this section**, three paragraphs below a note being faulted for enumerating seven things after announcing six. Nothing recomputes an integer typed into prose. The wording above no longer states a total; the tables are the count.

**A fifth row was added on 2026-08-16 for [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96) — `R2`, on case 3's allergy line — and run 1 is not scored against it**, on the standing rule that a row existing because the skill changed cannot be graded from notes predating the change. Its own section below says why this set is where that ruling was decided.

**Four NAMING rows were added later the same day for [#68](https://github.com/mshamblin5150-code/clinical-skills/issues/68), and run 1 fails two of them.** **None of the seven verdicts above moves** — nothing in `CODING`, `DRIFT` or `REPORTED` turns on what an entry is called. *(Seven **rows**, three **fractions**. A code review caught this sentence saying "the seven digits", which is neither, one paragraph below the one faulting this section for exactly that.)* See *NAMING* below for what run 1 wrote and why it was compliant when it wrote it. **This is `filled-anchor`'s shape arriving here** — that set also passed its first run and had rows reversed underneath it by [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) — with one difference worth keeping straight: #46 **reversed** rows that were wrong, and #68 **added** rows for a question nothing had asked. The old rows were not wrong; they were silent.

**The output is in `scratch/hedged-dx-run-1/` and that path is a weaker citation than it looks.** `scratch/` is gitignored and this run was generated inside a worktree, so the notes exist on one machine and in no commit — which is [#122](https://github.com/mshamblin5150-code/clinical-skills/issues/122) exactly, filed because run 3's output is gone and `day-b`'s file still cites its path as though it were there. **Every quotation this section relies on is reproduced inline** for that reason; nothing below asks a reader to go and open a file that may not exist. **All three generating passes reported opening nothing under `fixtures/`**, which is a self-report and is treated as one — see [fixtures/README](../README.md) on why that audit is an admission against interest rather than evidence.

**A first run is a baseline, not a clean bill**, and this one is a narrow baseline: three cases, six rows, one pass each. `filled-anchor` also passed its first run and the score was later voided when [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) reversed three rows underneath it.

**Five of the six rows were edited before the score above was recorded — four defects and one clarification.** C1, C2 and C5 failed a *correct* note as first written; R1 counted something [SKILL.md](../../skills/clinical-note/SKILL.md) forbids; those are the four. D1's pass column did not exempt an ordered film, which was ambiguous rather than wrong. C3 is the only row untouched. The fixes are written out beside their rows. The verdicts do not turn on any of them — no note assigned a refused code to a diagnosis under either wording — but four rows would have been wrong for the next run, and a row that fails a compliant note gets deleted rather than believed.

**That count was itself wrong when this section was first written**, which is worth leaving in rather than smoothing away: it said *three of six* in one clause and *all five were fixed* in the next, and [fixtures/README](../README.md) said *four*. **Three committed statements, three numbers, in a section whose subject is a note that miscounted its own codes.** A code review caught it. Nothing recomputes an integer typed into prose — which is the finding this repo has now recorded at a row count, a denominator, a character count and here.

**That is three sets in a row where the first run's most useful product was a corrected row rather than a score.** `day-b` run 1 and `peds-bp` run 1 each failed a row whose own drift matrix reported a pass; this one passed every row and still edited five of six. **The separation is what did it every time** — a pass that had written the notes would have read its own compliance back off rows written to match it.

### What the run found that no row asked for

**Two of the three notes wrote refusal records this set says it cannot check.** *Still unresolved* below states that a note has no `NOT CODED` block, so the `icd10-cpt` half is unreachable. Case 2 built one inline for seven differential entries — `Community-acquired pneumonia - J18.9 NOT CODED, nothing established it, chest film ordered today with no result; coded as shortness of breath - R06.02` — and case 3 did it in prose for both `J15.7` and a pertussis `A37.90`. **The behavior the owed set was going to test turns out to be producible by this one**, unprompted, which is an argument for writing that set and not for widening this one: it is evidence of one run's habit, not of a rule.

**Case 2's drift matrix miscounts on the row whose job is counting.** Row 13 states `Six entries carry an inline NOT CODED` and then enumerates seven; row 20 states `13 codes` and lists fourteen. Its Assessment carries **seven** such entries, and the eighth occurrence of the string is inside the matrix row doing the miscounting. **Nothing in the CODING verdicts moves** — every code named is where the matrix says it is — but this is [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md)'s argument arriving again on a passing run: a self-report can be wrong about an integer it computes itself, in a note nothing else caught, and only a reader who counted independently would ever know.

**Case 1 declined to invent a radiograph while reasoning its way to needing one.** It argued the pneumonia from `decreased air movement in the lungs on exam` and a documented sick contact, restricted the mycoplasma impression to `the clinical picture`, ordered a chest film prospectively, and attached no result to it. That is D1 under load rather than vacuously — the row's failure mode was available on every line and was not taken.

## Status — the reference

**The inputs are in.** Three encounters in [shorthand/](shorthand/), one file per case, de-identified.

**The reference is owed.** None of this repo's three reference reads covers these shifts — `day-a`, `day-b` and `peds-bp` each read one shift, and these three cases come from three others. So every `Reference did` cell below reads **owed**, on `obesity-bmi`'s terms rather than as an oversight.

**And one row here is one a reference could never settle**, which is worth saying before anyone reads the owed cells as a gap of uniform size. D1 turns on the input omitting a chest film that was taken — the clinician said so, and the day file does not — so a submitted note that mentions the film is not evidence the note under test should have, and one that omits it is not evidence it should not. [fixtures/README](../README.md) already names this class of permanently-open question, about filled vitals; this is the same shape reaching an imaging study.

## CODING — binary, all must pass

The class [`day-b` hosts first](../day-b/assertions.md), defined in [fixtures/README](../README.md). CODING asks whether the codes attached to what survived say what the encounter can support. **It is not CODE**: every code named below is real, billable and correctly described, verified against `reference/icd10cm-2026.sqlite` on 2026-08-15. `J15.7` is a perfectly good code, which is exactly what makes it wrong on a pneumonia nobody cultured.

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| C1 | 1 — 7 yo f | The pneumonia is **assigned** `J18.9 Pneumonia, unspecified organism`, **and** no diagnosis in the note is assigned a code naming mycoplasma | A diagnosis is assigned `J15.7`, `B96.0` or `A49.3` — **or** no pneumonia code is assigned at all. Both limbs fail | **Owed.** |
| C2 | 2 — 32 yo M | No diagnosis is assigned a code naming osteomyelitis | Any `M86.-` is **assigned** to an entry in the differential, `Preexisting diagnoses` or `Final diagnosis`. The film was ordered `r/o osteomyelitis` and **nothing resulted**, so the descriptor asserts a disease the encounter did not establish | **Owed.** |
| C3 | 2 — 32 yo M | The Assessment carries `B96.1` | It does not. The culture **came back and grew the organism** — `c/s from [DATE] of wound reveald klebsiella pneumonea` — so this is an established organism, and a claim without it is undercoded | **Owed.** |
| C4 | 3 — 3 yo | `J06.9 Acute upper respiratory infection, unspecified` is assigned to a diagnosis | It is not — including when the note withholds it *because* the diagnosis is hedged. The descriptor says **unspecified** and asserts nothing the note lacks, so the hedge costs nothing here | **Owed.** |
| C5 | 3 — 3 yo | No diagnosis is assigned a code naming mycoplasma | One is. Mycoplasma was never tested on this encounter; strep, influenza and COVID were, and all three returned negative | **Owed.** |

**Assigned, not present — and these three rows were written the wrong way round first.** C1, C2 and C5 originally failed when the code *appeared anywhere in the note*. **That wording fails a correct run**, and `day-b`'s C2 had already learned it and written it down: *"An earlier wording failed when `U07.1` appeared anywhere in the output, and that would have failed a correct run… A row that punished the refusal for naming what it refused would have inverted the rule it was written to hold."* [icd10-cpt](../../skills/icd10-cpt/SKILL.md) step 4 **requires** a refused code be named, so `M86.9` and `J15.7` are supposed to be in the text. What the row asks is whether a diagnosis **carries** one.

**Run 1 is what caught it, and it caught it by producing the correct behavior.** All three notes named their refused codes — `J15.7` five times in case 3 alone, two of them in the note body — so the rows as first written would have failed every case for doing exactly what the skill demands. Fixed before the score was recorded, and recorded here because the same lesson has now been learned twice in two sets.

**C3 quotes the code and not its descriptor, deliberately.** The official string is `Klebsiella pneumoniae [K. pneumoniae] as the cause of diseases classified elsewhere`, with a bracketed alias a note will not usually reproduce. C3's subject is whether the established organism is coded at all; descriptor fidelity is CODE's question and this set defines no CODE rows. An earlier draft quoted the descriptor without the alias, which invited a stricter reader to enforce a string the row does not mean.

**C1's second limb is the one that would be dropped by accident, and it is the more common failure.** Refusing `J15.7` is the visible half of drift row 13, and a run that refuses it and then writes no pneumonia code at all has not passed — it has deleted the diagnosis rather than coded it honestly. [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) is the precedent and it is exact: `filled-anchor` run 1 withheld a whole code family, scored `5/5`, and the row was later reversed because withholding was never the pass. **A row with only the refusal limb would score that behavior as correct.**

**C4 is the control, and without it the other four are close to worthless.** A run that refuses every organism-adjacent code passes C1's first limb, C2 and C5 outright, and looks disciplined doing it. C4 is where that run fails: `J06.9` names nothing, asserts nothing, and must be written. **The set's pass therefore cannot be bought by refusing**, which is the only property that makes C1, C2 and C5 mean anything.

**C3 is a clinician ruling and not a reading of the guidelines.** Asked on 2026-08-15 with two Assessments differing only in whether `B96.1` sat on the diagnosis line — identical prose, both naming the organism and the resistance — the answer was that the version without it **fails**. That is what makes this a binary row rather than a coding opinion embedded in a fixture. Recorded because a later reader will otherwise reasonably ask why `L97.909` alone was not enough.

**C2 and C3 are the same encounter pulling opposite ways, and that is the point of case 2.** One organism the encounter **established** by culture, one disease it **did not** establish by imaging, in one Assessment. A note can only pass both by reasoning about each, and the two most likely wrong answers — code everything, refuse everything — each fail exactly one.

**C1 and C5 are the same claim asked of two cases, deliberately.** `day-b`'s C1 spans all twelve of its cases on the reasoning that a rule firing on every output should not be tested on one twelfth of them. This is the narrow version: two of three cases hedge mycoplasma, on two different grounds — case 1 radiographic, case 3 a failed first-line course — and a run that gets one right and the other wrong has not understood the rule.

**No row here reads the worksheet, because there is no worksheet.** [icd10-cpt](../../skills/icd10-cpt/SKILL.md) step 4 requires a refused code be **named** — `NOT CODED, NOTHING ESTABLISHED IT`, with the supported code proposed in its place — precisely so a later positive result has a code waiting for it. **A note has no refusal block**, so nothing in this set can check that half, and a run that silently drops `J15.7` scores identically to one that refuses it for the right reason. That limb needs finished notes as inputs, which is `filled-anchor`'s shape and a separate set. It is owed and named in *Still unresolved* below.

## NAMING — binary, all must pass

Added 2026-08-15 for [#68](https://github.com/mshamblin5150-code/clinical-skills/issues/68), which this set's run 1 raised and which the clinician settled the same day. **These rows did not exist when run 1 was scored**, and run 1 fails N1 — see *What run 1 produced, and what it now fails* below.

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| N1 | all three | **No code marked `NOT CODED` anywhere in the note sits in any entry's code slot** — the position after the hyphen that pins a code to a label. **The `Final diagnosis` line is a slot for this row and is read by position**, so every code on it outside a `NOT CODED:` clause counts whatever pins it | One does. `Contiguous osteomyelitis … - M86.9 NOT CODED, …` fails: the refusal is adjacent, and the label still heads an entry with a disease code pinned to it | **Owed.** |
| N2 | all three | Every entry whose specific code was refused is **named for the code it carries** — the label says what the surviving code says. `Pain in right leg - M79.604` | The label names a disease the encounter did not establish while the slot holds something else, or the label names the suspicion with the organism demoted into a clause. Both are renderings run 1 produced | **Owed.** |
| N3 | 2 — 32 yo M | Two refusals resting on **one** documented finding are **one** entry naming both refused codes in its rationale | Two entries carry the same label and the same code, or the second refusal is dropped to avoid the collision | **Owed.** |
| N4 | 1 — 7 yo f | The **favored** entry and the `Final diagnosis` keep the clinician's hedge — `Community-acquired pneumonia, mycoplasma suspected` — with a code the encounter supports beside it | The hedge is softened away to the code's own descriptor, or the label keeps the hedge and the slot holds `J15.7` | **Owed.** |

**N1 is the only row here a machine can settle, and `tools/differential_scan.py` is it.** N2 and N3 each need a reader, for the two reasons [SKILL.md](../../skills/clinical-note/SKILL.md) gives beside the command and which are not restated here. **A clean scan is therefore not a passed NAMING class** — it is one row of four — and reading it as one is the failure mode this sentence exists to prevent.

**And since [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153) the machine no longer settles it *on this run*.** Row 22 now reads only the welded `NOT CODED: <code>` pair, and run 1 predates that form, so the scanner reports run 1 as **unscanned** — exit 2, one bare mark, no refusal read — rather than as a failure. **N1's verdict below does not move.** The finding was reclassified, not lost: it is failed by a reader now, on the same sentence, and what changed is only which instrument settles it. A row scored by a tool that has stopped reading the run is a row nobody scored, and saying so is the whole reason the exit status has a 2.

**N1 and N2 are two rows because they fail independently, and N1 is the one that was reachable.** [#68](https://github.com/mshamblin5150-code/clinical-skills/issues/68) records that run 1's three renderings **all** kept the refused code out of the slot and that **nothing required them to** — a fourth putting `M86.9` after the hyphen with the refusal in a footnote would have passed every row this set had. N1 is that hole closed. N2 is the convention that makes the hole impossible to reopen by a different route, and it is the one nothing can check by machine.

**N4 is the exception row, and without it N2 would be scored wrong.** The naming rule is deliberately **not** applied to the favored entry or the final diagnosis: those are the clinician's own conclusion, `clinical-note` forbids softening a hedge, and the ruling on 2026-08-15 was that his wording wins there. A grader applying N2 uniformly would fail a compliant note on its best line. **The two forms sit four lines apart in one note on purpose** — see [SKILL.md](../../skills/clinical-note/SKILL.md) under *Naming a differential entry*.

**N3 is scored on case 2 alone because it is the only case that can host it.** Two suspected diagnoses resting on one documented finding needs an encounter with two organism-shaped suspicions and one symptom underneath, and cases 1 and 3 each hedge a single organism.

### What run 1 produced, and what it now fails

**Run 1 scored `CODING 5/5 · DRIFT 1/1 · REPORTED 1/1` and none of that moves** — no note assigned a refused code to a diagnosis, which is all five CODING rows ask. **Against the rows above it fails N1 and N2 on two of three cases**, and that is the convention being new rather than the run being newly wrong. Both renderings were compliant with everything written down on the day they were produced.

| Case | What run 1 wrote | Row |
| --- | --- | --- |
| 2 | `Contiguous osteomyelitis of the right tibia or fibula - M86.9 NOT CODED, nothing established it, right tibia and fibula film ordered today with no result; coded as pain in right leg - M79.604` | **fails N1** — `M86.9` is in a slot and marked in the same breath — **and N2** |
| 2 | `Systemic infection arising from the wound - A41.50 and R78.81 NOT CODED, nothing established either, no blood culture drawn; coded as chills - R68.83` | **fails N2**; passes N3 in shape, having already collapsed to one entry |
| 3 | `Atypical respiratory infection, Mycoplasma pneumoniae suspected - R05.9 for the documented cough` … `Nothing tested for the organism, so J15.7 … is not coded.` | **fails N2** — the organism is demoted into a clause and still heads the entry |

**Case 3's `R05.9` worksheet was re-read before these rows were worded, and it moved nothing.** [#68](https://github.com/mshamblin5150-code/clinical-skills/issues/68)'s second comment asked for that check: `R05.9 Cough, unspecified` is one of the 23 codes in `fixtures/filled-anchor/notes` whose official descriptor carries `unspecified`, so under [#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56) it may not read `SPECIFICITY: complete`, takes `needs: duration`, and earns a step-4 bedside line. The comment's worry was that a naming convention reading well against `complete` might read redundantly against `needs: duration` plus a bedside item about the same symptom. **It does not, because the two live in different documents.** N1 through N4 govern what an entry in the **note** is called; `SPECIFICITY` and the step-4 line are on the **worksheet**. Case 3's entry reads `Cough - R05.9` under N2 either way, and the `needs: duration` line sits beside it rather than inside it. Recorded here rather than only in the ticket, because a later reader re-opening that comment should find the check already done.

**N4 is unscored against run 1, and that is a gap in the evidence rather than a pass.** Scoring it needs case 1's favored entry and its `Final diagnosis` line in full, and neither is reproduced anywhere — [#122](https://github.com/mshamblin5150-code/clinical-skills/issues/122) is why: the output is in `scratch/hedged-dx-run-1/`, gitignored, on one machine, in no commit. The three quotations above survive only because they were copied into [#68](https://github.com/mshamblin5150-code/clinical-skills/issues/68) while the run was still open. **A row nobody can score is not a row that passed**, and reading the table's four rows as four verdicts would make this set's second score wrong the way its first total was.

**Case 2's second line carries a separate defect that no row here scores, and it is filed rather than fixtured.** `A41.50 Gram-negative sepsis, unspecified` was refused for *"no blood culture drawn"*, which is the wrong reason: sepsis is diagnosed at the bedside from vitals, white count and lactate, and `A41.9 Sepsis, unspecified organism` — the code that should have been on the table — names no organism for a culture to supply. What rejects sepsis here is the vitals, which meet **no** SIRS criterion: `bp 126/80 hr 77 t 97.3 rr 18`. `R78.81 Bacteremia` refuses correctly, because bacteria demonstrated in blood **is** a culture finding. [#149](https://github.com/mshamblin5150-code/clinical-skills/issues/149) holds the general rule and names what it would take to make this a row.

## DRIFT — binary, all must pass

| # | Case | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| D1 | 1 — 7 yo f | The note states **no radiographic result**. An imaging study **ordered** and carrying no result does not fail this row | It supplies a result — `CXR with infiltrate`, `chest film consistent with atypical pneumonia`, `imaging showed patchy consolidation` — that the shorthand never recorded | **Owed, and out of reach.** See *Status* above |

**This row is not about coding and it is on this set because only this set can anchor it.** Case 1's shorthand diagnoses a community-acquired pneumonia and contains **no imaging token at all**. A pneumonia cannot be diagnosed by auscultation — the clinician's own words, 2026-08-15 — so the diagnosis presupposes a film, and a note reasoning fluently from `dx CAP` toward what the film must have shown is writing a result nobody recorded.

**Drift row 3 already forbids it in as many words**: *no laboratory value, imaging result or diagnostic finding is filled*. What this row adds is a case where filling one is **invited by the input** rather than merely possible, which is the condition under which a prohibition actually gets tested.

**Its quiet failure is a sentence that reads like competence.** *"Chest radiography demonstrated a patchy interstitial pattern consistent with atypical pneumonia"* is clinically apt, consistent with the diagnosis, consistent with the treatment, and entirely invented. Nothing else in the note contradicts it.

## GIVEN — binary, all must pass

This set's fourth section, and the class is [day-b](../day-b/assertions.md)'s — defined in [fixtures/README](../README.md), hosted there first, and arriving here because [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96)'s ruling landed in four sets and needed one class in all four. CODING asks what the codes claim and NAMING asks what an entry is called; GIVEN asks the prior question, **did a given survive at all, unchanged**, and README names *a stated allergen* among its subjects outright.

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| G1 | 3 — 3 yo | **The `allergy: seasonal` line appears in the `Allergies (reaction)` box named as environmental, *and* the box states a drug status.** Both limbs, not one instead of the other. Appearing in `PMH/PSH` **as well as** in the box passes; the box is what is graded. And **no `FILLED·asserted` entry denies the allergen the note read** | The allergen is absent from the box; or sits in it unnamed by its kind; or the box states no drug status; or a `FILLED·asserted` entry denies the given. **The unit of that last limb is the entry and its wrapped lines**, not the sentence. What the **reaction** beside the allergen reads is not this row's | **Owed.** Same standing as this set's other rows. **Scored `PASS`, 2026-08-18, against `48ac3ca`** — a targeted run, [#201](https://github.com/mshamblin5150-code/clinical-skills/issues/201); the walk is below. |

### G1 is R2 promoted, and this set held the input the whole ruling turned on

**[#201](https://github.com/mshamblin5150-code/clinical-skills/issues/201), scored 2026-08-18 against `48ac3ca`: PASS.** R2 was counted **for want of a run** and promotable only with the other three; the run came, all four passed, and each gained an enforced successor. **R2 stays and is not renumbered** — G1 is its successor, not its replacement.

**Case 3 is the only committed input where the two candidate rules give opposite answers** — `allergy: seasonal` is labeled *and* environmental, so label placement puts it in the box and a drug-only box keeps it out. That is why the clinician was asked on this case rather than on the abstraction, and it is why this row is worth a walk rather than a fraction. The targeted run wrote:

```
Allergies (reaction): NKDA for drug allergies. Seasonal environmental allergies -
itching and sneezing.
```

**The drug half is what the Plan needed**, and it is the second limb rather than a courtesy: this encounter's Plan carries azithromycin and prednisolone, and `NKDA` is the only thing in the note that answers whether they may be given.

**One thing the row's own prose gets loose about, recorded rather than quietly fixed.** R2 reads *"the Plan proposes azithromycin and prednisolone, so the drug half is what says the two may be given"*, and both drugs are in the **shorthand** — they are givens, not proposals. The note's `FILLED·asserted` entry accordingly names the **proposed** acetaminophen as what rests on the inferred `NKDA` and names neither given drug, which is [day-b](../day-b/assertions.md) R4's rule exactly: *naming a given fails as surely as omitting a proposed one*. **So the note is right and the sentence is imprecise**, and G1 is written without that limb rather than inheriting it — what a `FILLED·asserted` line must enumerate is R4's subject and not #96's. R2's text is left alone: **changing a ruling needs the clinician, and recording what was found does not.**

**No denominator moves.** Run 1's `CODING 5/5`, `DRIFT 1/1`, `REPORTED 1/1` stand, and `NAMING`'s three verdicts are untouched. One encounter scored on one row is not a run, and this set's reference is still owed.

## REPORTED — counted, not enforced

| # | Case | Counted | Reference did |
| --- | --- | --- | --- |
| R1 | 1 — 7 yo f | **What the note does about the missing radiographic basis.** Three shapes seen so far: it orders a film prospectively under `FILLED·proposed`; it records the pneumonia entry as resting on a film with no result; it says nothing | **Owed, and out of reach.** Same reasoning as D1 |
| R2 | 3 — 3 yo | **The `allergy: seasonal` line reaches the `Allergies (reaction)` box named as environmental, *and* the box states a drug status.** Both limbs, not one instead of the other: a box reading only `Environmental: seasonal allergies` fails as surely as a bare `NKDA` with the allergen routed to `PMH/PSH`. The Plan proposes azithromycin and prednisolone, so the drug half is what says the two may be given. **And where the `NKDA` is inferred, its `FILLED·asserted` line names the drugs leaning on it and does not deny the seasonal allergy** | **Owed.** Same standing as this set's other rows. **Promoted 2026-08-18 on [#201](https://github.com/mshamblin5150-code/clinical-skills/issues/201) — G1 under GIVEN is its enforced successor and passed.** This row keeps its identity and its text; what moved is the bar. |

**R1 was drafted as the second limb of D1, split out before the run, and then rewritten because the run proved it wrong.** All three states are recorded because the reasoning is the argument, not the outcome.

**As drafted it counted a `GAPS` entry for the absent film, and that was a defect rather than a soft bar.** [SKILL.md](../../skills/clinical-note/SKILL.md) bars *"anything the skill was instructed to generate"* from `GAPS` outright, and one paragraph earlier it routes this exact study elsewhere: *"Where the givens alone require a workup the visit did not do — a chest film for documented diminished breath sounds — the order goes under `FILLED·proposed` and this block stays silent."* Case 1's shorthand ordered no film, so any film in the note is one the skill supplied — which makes a `GAPS` line for it **forbidden**, not merely unrequired. A row counting it would have rewarded a rule violation.

**The `GAPS` sentence the row leaned on is about a different film.** *"An x-ray ordered with no result recorded"* is an x-ray the **encounter** ordered. Case 1's encounter ordered none. Two studies, one phrase, opposite obligations — and the draft row read the phrase without asking whose order it described.

**So the promotability claim it shipped with was wrong and is withdrawn.** It said a clinician ruling would make the row binary *as written*. It would not: the row would still contradict `SKILL.md`, and closing that would mean **editing the skill too**. A ruling alone leaves the fixture and the skill directing opposite behavior, which is the state this repo has twice paid to get out of.

**What is left is genuinely counted, and it is counted for the third reason [fixtures/README](../README.md) names — the claim is hard and there is no bar to set.** Ordering the film prospectively and naming the pneumonia as film-dependent are both defensible, both licensed, and nothing ranks them. Run 1 produced one of each on two different cases, which is the evidence that this is a real fork rather than a right answer and a wrong one.

**Splitting from D1 still costs nothing and keeps D1 clean.** D1's subject is invention, which every rule here already forbids. R1's is a choice between two permitted behaviors. Bundling them would have made a binary row fail on its soft limb and taken the hard one down with it.

### R2 is here because case 3's three-word allergy line decided a ruling for four sets

**This set holds the one input in the repo where the two candidate rules gave opposite answers**, and it was not in the ticket's own table until a sweep put it there. [#96](https://github.com/mshamblin5150-code/clinical-skills/issues/96) asked whether an environmental allergy belongs in a box where `NKDA` conventionally means no known **drug** allergy, and it tested a second hypothesis alongside: that the discriminator is **where the clinician typed the words** — under an `allergies:` label to the box, inside an `hx:` list to the history.

**Case 3 reads `allergy: seasonal` — labeled *and* environmental.** Label placement puts it in the box; a drug-only reading of the box keeps it out. Every other committed input naming an allergen is either environmental-inside-`hx:` or drug-under-a-label, where the two rules agree and neither is tested. **So one input of eight decided it**, and it was put in front of the clinician as the concrete case, with this note's azithromycin beside it, on 2026-08-16.

**He ruled that the box carries both, each named by its kind**, which retires the placement hypothesis rather than choosing between its outcomes. The population and the four-and-four count that killed that hypothesis are stated once in [day-b](../day-b/assertions.md) under R6 and R7 and deliberately not repeated here.

**Counted rather than binary on #29's reason**, one ruling across four sets — this row, [day-a](../day-a/assertions.md) R15, [day-b](../day-b/assertions.md) R7 and [peds-bp](../peds-bp/assertions.md) R3. **Promotable, for want of a run, and the four go together.** **They went, on 2026-08-18**: all four passed a targeted run and all four gained an enforced successor, which for this set is **G1** under GIVEN. The cohort is closed. It sits in REPORTED rather than beside the CODING and NAMING rows despite resolving to a value a reader compares, which is the same tension R2 carries in peds-bp and is recorded for the same reason.

## Still unresolved

**The `icd10-cpt` half of drift row 13's second half is untested and this set cannot reach it.** What lands here is the note's codes; what is missing is the **refusal record** — `J15.7` written out by name under `NOT CODED, NOTHING ESTABLISHED IT` with `J18.9` proposed in its place, so that a mycoplasma titer returning positive next week has a code waiting for it. A note has no block for that. Building it means feeding finished notes to `icd10-cpt`, which is `filled-anchor`'s shape, and it should reuse these three encounters rather than pick new ones.

**The reference is owed on three separate shifts**, which is three reconciliations rather than one. `day-b`'s took patient creation order to settle and `peds-bp`'s did too; budget for the same here. D1 and R1 are out of reach of it either way. Filed as [#128](https://github.com/mshamblin5150-code/clinical-skills/issues/128).

**Case 3's three negative tests carry no row, and that was ruled rather than overlooked.** Its shorthand records `strep, flu and COVID testing all negative` — three organisms the encounter tested and excluded — so a sixth row was drafted forbidding any code naming streptococcus, influenza or COVID. The clinician struck it on 2026-08-15: **there is no need to code an organism whose test results were negative.** A row stating so would police behavior no run has produced, and run 1 bears that out — case 3 coded none of the three, and case 2 wrote `Streptococcal pharyngitis - J02.0 NOT CODED, the rapid strep run today was negative` unprompted.

**Case 2 carries the same shape and is likewise unscored.** Its plan line reads `strep (was negative)`, a test performed in clinic with a documented result, alongside a panel of labs whose results are absent. The ruling above reaches it for the same reason.

**Case 1's impossible heart rate is unscored.** `hr 1238` is a given the note must do *something* with, and no rule in this repo says what. It is preserved rather than repaired — see [shorthand/README.md](shorthand/README.md) — and named here so that a run doing something surprising with it is read as an open question rather than as a miss.

**The set is two-thirds pediatric respiratory and both of those hedge the same organism.** A score off three cases is a baseline, and a narrow one. The seventeen-encounter candidate pool is recomputable from `tools/corpus_census.py`, so widening the set is a reading task rather than a search.
