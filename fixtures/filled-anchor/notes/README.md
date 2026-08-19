# filled-anchor — inputs

Twelve **finished notes**, one per case, each a note body plus the tier block beneath it.

This is the first set in the repo whose inputs are not shorthand, and the reason is what the skill under test consumes. [icd10-cpt](../../../skills/icd10-cpt/SKILL.md) states it as a hard requirement: *"The input to this skill is the whole `clinical-note` output — the note body and the tier block beneath it — not the note body alone."* A set that fed it shorthand would be testing a shape the skill refuses.

## Where they came from

**day-b run 1**, produced 2026-08-11 by `clinical-note` on the comprehensive SOAP branch, over the twelve encounters in [day-b/shorthand](../../day-b/shorthand/). The run's own working copies live in `scratch/day-b-run-1/` and are gitignored; these are byte-for-byte copies of them.

**Case numbers match day-b's.** `notes/case-07.md` is the note generated from `day-b/shorthand/case-07.md`, and day-b's assertions about case 7 are assertions about the same encounter. Nothing here renumbers.

## De-identification could not be inherited, and assuming it could was wrong

This section used to say that a note generated from de-identified shorthand cannot reintroduce what its input did not carry, and that the twelve were therefore byte-for-byte copies needing nothing.

**That is false, and it was caught in review rather than by a tool.** Nine of the twelve named a practicum site in the Medatrax `Primary Payment Method` row, and **seven of those nine named both**:

```
The site pattern ([SITE-A] -> Self-pay/other; [SITE-B] -> Medicaid / ...)
could not be keyed, because Site is a GAP.
```

The generating skill reads the account profile in `scratch/` to decide a payer, so it had the site names whether or not its *encounter* input did. **A generated note's provenance is its whole context, not its prompt.** Both names are now `[SITE-A]` and `[SITE-B]`, and that is the one edit made to the run's output — the notes are otherwise byte-for-byte.

**Nothing in the repo would have caught this.** `phi_scan`'s corpus layer harvests patient names from `scratch/name-index.json`; a site name is not a patient name and no shape rule matches one. The claim in this file was the only control, and it was wrong. Filed as [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50), which carries the general form: **a fixture derived from generated output inherits the generator's whole context, not its input's.** Every set before this one derived from shorthand, so the reasoning never had to be right.

**Recompute those two figures rather than trusting this paragraph** — the first of them was wrong here for four days, and [#50](https://github.com/mshamblin5150-code/clinical-skills/issues/50) propagated *both* into three more files before anyone counted:

```bash
grep -l '\[SITE-A\]' fixtures/filled-anchor/notes/case-*.md | wc -l   # 9 -- name a site
grep -l '\[SITE-B\]' fixtures/filled-anchor/notes/case-*.md | wc -l   # 7 -- name both
```

The second line counts *both* only because no note carries `[SITE-B]` without `[SITE-A]`; `case-05` and `case-06` are the two that name one site, and each writes it as a *counterfactual* — `case-05` says the payer would be Self-pay/other **if** the site were that one. **This is the figure the other three files deliberately do not restate.**

**#50 closed `wontfix`, and it closed on the string rather than on the reasoning.** No site layer was built: the site names are portal mechanics — which placements the clinician works, a fact about him and not about any patient — in a private repo, in a fixture the visit date had already left. `phi_scan` still has no concept of an account profile, which is now listed among its known limits rather than absent from them. **The general form was kept and is [fixtures/README](../../README.md)'s**, where it binds the next set built from a skill's output.

**The redaction here stands, and so does the rule behind it.** [Standing rule 1](../../../AGENTS.md) defines a fixture as one with the visit date **and site** removed, and #50 changed nothing about that — it ruled only that the gap is not worth a scanner layer. The edit cost nothing, no assertion in this set ever touched it, and `[SITE-A]`/`[SITE-B]` is what the table below records.

**Do not match on how a note words the absence.** The nine phrase it every way — `Site is a GAP`, `Site is a GAPS entry`, `Site is unknown` — and only three of the nine use the first form. That is the same warning this file already gives about the `GAPS` date entries below, arrived at a second time from the other direction: #50's first draft rested its argument on that exact string and was wrong about six notes.

**What travels, and on whose authority:**

| | Removed by | Where |
| --- | --- | --- |
| Patient names | day-b, already `[PT]` | standing rule 1 |
| Visit date | day-b, before commit | [fixtures/README](../../README.md) |
| Site name | **here, on the way across** | [fixtures/README](../../README.md) — *"Date plus site plus age narrows the population sharply"* |
| Ages, findings | kept | they are what the assertions test |

Each of the twelve also records the missing date and site under `GAPS`, in its own wording — `case-01` reads *"Visit Date — removed in de-identification"*, `case-09` *"removed from the fixture"*, `case-05` *"not in the source"*. **The absence is recorded everywhere; the phrasing is not standard**, so nothing should match on the string.

## Its British spellings are deliberate

**Do not correct them.** The forms and their counts are `--record`'s to state and are **deliberately not listed here any more**: this paragraph read *eight forms, 20 times across six of the twelve notes* until 2026-08-18, when adding `neighbour` and then `judgement` to the scanner's table moved it to ten, 25 and seven **without a byte of these notes changing**. The figure was a property of the instrument and was written as though it were a property of the record. [Standing rule 4](../../../AGENTS.md) says American English always and has no exceptions in the output, and these are not an exception to it: they are **a record of it being broken**, which is a different thing and is the only reason they survive. Recompute the figures rather than trusting this paragraph:

```bash
python tools/spelling_scan.py --record
```

**The rule landed after this run.** Nothing in the repo stated it until 2026-08-12; these notes are from 2026-08-11. So the run was not disobeying an instruction, and that is what makes it evidence — the skill emitted British spellings **unprompted**, from an American corpus, with no British spelling anywhere in its input.

**The same run wrote both spellings of the same word**, which is the sharp end of it and is why the `--record` view puts the American count beside each form: `cesarean` eight times against `caesarean` twice, `dyspnea` seven against `dyspnoea` three, `fiber` three against `fibre` four. A note written in a British register would be a style; a note that switches inside one run is **drift**, and it is drift no reader would catch by reading one note.

**A later run does not clear them, and one has now been made.** The same twelve encounters were re-run on 2026-08-12 under the rule and emitted **none of the eight** — which changes what this record is for, not whether it is kept. It is the *only* committed evidence that the skill ever emitted them, so a reader who finds the clean run first has no way to see why the rule exists. See [fixtures/README](../../README.md); two of the eight cleared **vacuously**, and the skill's own *Conventions > Spelling* says which two.

**`programme` is the one to look at first.** It is not prose — it sits in the Medatrax `Course` row of `case-01` and `case-02`, which is **portal data entry**. The other seven would embarrass a note; that one would be typed into a field.

**Correcting them destroys the thing the set is for**, on exactly the argument the de-identification section above makes. The one edit ever made to these twelve was the two site names, and that section exists to record it precisely because byte-for-byte is the property that makes the set worth keeping. `tools/test_spelling_scan.py` pins the three figures above, so a tidy fails a test rather than quietly voiding this page. [Issue #73](https://github.com/mshamblin5150-code/clinical-skills/issues/73).

**No assertion row quotes one, and that was checked rather than assumed.** A row quoting a British-spelled span would pin the wrong spelling into a bar the sets are graded against — the one way these twelve could contaminate something. All five sets' `assertions.md` were swept 2026-08-12 against the eight forms the table then held, and a wider net of 56 stems, and every one was clean. **That sweep's denominator has since grown to ten**, so it certifies less than it appears to — which is why the test below matters more than the sweep does. **A negative result decays**, so it is also a test: `test_spelling_scan.py` asserts that no tracked Markdown outside this directory uses a listed form, which is that sweep run again on every commit that runs the suite.

**`tools/spelling_scan.py` knows about this directory and will not refuse it.** The exemption is `notes/case-*.md` by path, and it is deliberately not this file: a README is prose about the record rather than the record, so it takes the scanner's ordinary rule — **a form inside backticks is a mention, a form in running prose is a use.** Every British spelling on this page is backticked for that reason, and a sweep that finds one here that is not has found a real defect.

## How the twelve were selected

The selection rule is two clauses, and it is recomputable from day-b's shorthand without consulting this file:

| Clause | Cases | Count |
| --- | --- | --- |
| The BMI in the finished note has a **filled** height or weight | 1, 5, 6, 7, 8, 9, 10, 11, 12 | 9 |
| The shorthand supplies a **given** height and weight | 2, 3, 4 | 3 |
| | | **12** |

The two clauses are disjoint and they exhaust the shift, so **the set is day-b entire and there is no curation to defend.** That matters more here than in a set drawn from shorthand: these inputs are a skill's output, and a subset chosen after reading them would be a subset chosen knowing what each one says.

The second clause is not decoration. Without it the set cannot tell *declines to code a filled BMI* from *never codes `Z68` at all* — the vacuity [issue #17](https://github.com/mshamblin5150-code/clinical-skills/issues/17) opened by naming. See [assertions](../assertions.md), row A3.

## The notes' own ICD-10 fields are kept

Each note body carries `Preexisting diagnoses (ICD10)` and `Final diagnosis` lists, because those are Medatrax fields and a finished note has them filled in. **Nothing was stripped.**

That is the input `icd10-cpt` really receives, and it cuts two ways.

- **For the ANCHOR class it is a decoy, and the best one available.** Case 1's note offers `Z68.26` in its Final diagnosis list, with a caveat underneath saying the pair rests on a filled height. The rule requires refusing it anyway. A run that copies the list fails.
- **For the CODE class it is a partial answer key**, which is why that class is scoped to codes the skill *adds or upgrades* rather than to every code in the output. Stated plainly in [assertions](../assertions.md) rather than worked around.

**How partial, measured rather than assumed.** All ten of case 1's codes were checked against `reference/icd10cm-2026.sqlite` on 2026-08-11. All ten exist and all ten are billable — so a run that copies them clears C1 and C3 having coded nothing. **Five of the ten descriptors do not match the official string**, which is a good deal less of an answer key than it first looked:

| Code | The note writes | The release says |
| --- | --- | --- |
| `L02.612` | Cutaneous abscess of left foot**, plantar great toe** | Cutaneous abscess of left foot |
| `M79.5` | Residual foreign body in soft tissue**, suspected, to be confirmed at drainage** | Residual foreign body in soft tissue |
| `R06.89` | Other abnormalities of breathing **(diminished breath sounds in all four fields)** | Other abnormalities of breathing |
| `R79.89` | Other specified abnormal findings of blood chemistry **(history of elevated troponin)** | Other specified abnormal findings of blood chemistry |
| `Z68.26` | Body mass index 26.0–26.9, adult | Body mass index **[BMI]** 26.0-26.9, adult |

Four append the clinical detail that anchored the code, which is useful reading and is not the descriptor. The fifth drops the official `[BMI]` and swaps an en dash for the hyphen — a difference no reader would notice and `icd10_lookup.py` settles in one call, which is the argument for having the CODE class at all.

**So copying is not free even on CODE.** It clears C1 and C3 and fails C2 five times in one note. ANCHOR is still what tells coding from copying, but the descriptor discipline is doing real work here rather than rubber-stamping.

## What the inputs are not

**They are not a graded run.** day-b's own `DRIFT n/n` and `FILLED n/n` have no first value — [issue #26](https://github.com/mshamblin5150-code/clinical-skills/issues/26) is where that gets settled. These notes are used here as *input material*, and an input does not have to be correct to be real. Where a note is wrong, that is a fact about the input this set tests against, not a defect this set inherits.

**One of them is wrong in a way this set exists to catch**, and it is worth naming here so nobody treats the inputs as a reference. Case 1 wrote `E66.3` and `Z68.26` into its Final diagnosis list off a filled height. Cases 7, 8, 9, 10, 11 and 12 held the same code family back explicitly — case 11 by citing `icd10-cpt` by name — and cases 5 and 6 said nothing about theirs either way. **One launder in twelve, in output that reads perfectly well.** Filed against `clinical-note` as [issue #46](https://github.com/mshamblin5150-code/clinical-skills/issues/46); row A2 is what makes it cost something downstream.

**They are a second thing now, and it is a reason not to edit them.** These twelve are the only committed evidence in the repo for [issue #67](https://github.com/mshamblin5150-code/clinical-skills/issues/67) — filled heights collapsing onto a handful of values, filled pressures tilted to one side of a line the corpus splits about evenly. **The figures live in [day-b/assertions.md](../../day-b/assertions.md) and are deliberately not restated here.** Recompute them:

```bash
python tools/filled_vitals_census.py fixtures/filled-anchor/notes
```

**day-b's run 2 shows the same pattern worse and it is gitignored**, so a reader with only this repo cannot check it. These notes are what makes the claim in `skills/clinical-note/SKILL.md` verifiable at all, and `tools/test_filled_vitals_census.py` pins the figures so an edit fails a test rather than quietly voiding an argument. **That is the same standing rule 4 already places on them** — a run record is evidence, and [its British spellings](#its-british-spellings-are-deliberate) stay for the same reason these numbers do.

**They are not 484 KB of prose for its own sake.** A finished note is what the skill takes, so the whole note is the input. Excerpting the Assessment would be excerpting the thing under test — step 1 reads the tier block, step 2 reads the Assessment and the Plan, and step 4 reports against both.
