# filled-anchor — inputs

Twelve **finished notes**, one per case, each a note body plus the tier block beneath it.

This is the first set in the repo whose inputs are not shorthand, and the reason is what the skill under test consumes. [icd10-cpt](../../../skills/icd10-cpt/SKILL.md) states it as a hard requirement: *"The input to this skill is the whole `clinical-note` output — the note body and the tier block beneath it — not the note body alone."* A set that fed it shorthand would be testing a shape the skill refuses.

## Where they came from

**day-b run 1**, produced 2026-08-11 by `clinical-note` on the comprehensive SOAP branch, over the twelve encounters in [day-b/shorthand](../../day-b/shorthand/). The run's own working copies live in `scratch/day-b-run-1/` and are gitignored; these are byte-for-byte copies of them.

**Case numbers match day-b's.** `notes/case-07.md` is the note generated from `day-b/shorthand/case-07.md`, and day-b's assertions about case 7 are assertions about the same encounter. Nothing here renumbers.

## De-identification is inherited, not reapplied

day-b's shorthand had the visit date and the site removed before it was committed ([fixtures/README](../../README.md)), and names were already `[PT]` under standing rule 1. A note generated from that shorthand cannot reintroduce what its input did not carry — each of these twelve records the absence explicitly, under `GAPS`:

```
GAPS              Visit Date — removed in de-identification.
                  Site — not named in the shorthand.
```

Ages and clinical findings stay, on the same terms as every other set: they are what the assertions test.

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
- **For the CODE class it is an answer key**, which is why that class is scoped to codes the skill *adds or upgrades* rather than to every code in the output. Stated plainly in [assertions](../assertions.md) rather than worked around.

Every one of case 1's ten codes was checked against `reference/icd10cm-2026.sqlite` on 2026-08-11: all ten exist, all ten are billable, and each descriptor matches the string written beside it. So a run that copies passes CODE having coded nothing. ANCHOR is what tells the two apart.

## What the inputs are not

**They are not a graded run.** day-b's own `DRIFT n/n` and `FILLED n/n` have no first value — [issue #26](https://github.com/mshamblin5150-code/clinical-skills/issues/26) is where that gets settled. These notes are used here as *input material*, and an input does not have to be correct to be real. Where a note is wrong, that is a fact about the input this set tests against, not a defect this set inherits.

**One of them is wrong in a way this set exists to catch**, and it is worth naming here so nobody treats the inputs as a reference. Case 1 wrote `E66.3` and `Z68.26` into its Final diagnosis list off a filled height. Cases 7, 8, 9, 10, 11 and 12 held the same code family back explicitly — case 11 by citing `icd10-cpt` by name — and cases 5 and 6 said nothing about theirs either way. **One launder in twelve, in output that reads perfectly well.** Filed against `clinical-note` as [issue #46](https://github.com/mshamblin5150-code/clinical-skills/issues/46); row A2 is what makes it cost something downstream.

**They are not 484 KB of prose for its own sake.** A finished note is what the skill takes, so the whole note is the input. Excerpting the Assessment would be excerpting the thing under test — step 1 reads the tier block, step 2 reads the Assessment and the Plan, and step 4 reports against both.
