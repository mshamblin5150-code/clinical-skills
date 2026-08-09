# Fixtures

A fixture is a **regression set** for the skills in this repo. Without one, every edit to a `SKILL.md` is settled by opinion — which is exactly how sediment survives a pruning pass.

## Working file vs fixture

Two artifacts, same encounters, opposite lifecycles. The repo used to have one word for both.

| | Working file | Fixture |
| --- | --- | --- |
| Lives in | `scratch/` | `fixtures/` |
| Committed | never | always |
| Carries | everything needed for Medatrax entry | ages and clinical findings only |
| Job | doing the work | proving the skill still does the work |

A fixture is **derived from** a working file, never a copy of one. Two things are removed on the way across:

- **The visit date.** Dates finer than a year are the identifier that matters here.
- **The site name.** Date plus site plus age narrows the population sharply in a small county.

Names are already `[PT]` under standing rule 1. Ages and findings stay, because they are what the assertions test.

## What an assertion is

A claim, in the clinician's own words, about what a correct run must contain — checked against the output text.

It is deliberately **not** a diff of the note prose: prose varies legitimately from run to run, and a bar that trips on style gets ignored within three runs.

It is also deliberately **not** the drift-matrix verdicts from `clinical-note` step 7. Those are the skill grading itself — a run that misses snuff box tenderness is precisely the run that also emits `row 2: PASS`. See [docs/adr/0001](../docs/adr/0001-fixture-asserts-on-named-findings.md).

## The pass bar

**DRIFT assertions are binary.** All of them, every run, no exceptions. Each one is a documented abnormal that reached the Objective and stopped there — the defect class the skill exists to catch. One miss fails the run.

**REPORTED assertions are counted, not enforced.** Differential depth, screening content, education phrasing. They move with the model and the wording; tracking the count catches slow erosion without failing a run over style.

## Running a set

1. Feed each case's shorthand to the named skill, on the stated branch.
2. Check the output text against that case's assertions.
3. Report `DRIFT n/n` — which must be full — and `REPORTED n/m`.
4. Any DRIFT miss names the case, the finding, and where the finding landed instead.

Re-run after every `SKILL.md` edit. That is the entire point: a measurable delta instead of a judgment call.

## Sets

| Set | Skill | Cases | Inputs | Reference |
| --- | --- | --- | --- | --- |
| [day-a](day-a/assertions.md) | `clinical-note`, SOAP branch | 10 | [extracted](day-a/shorthand/) | **not read** |

## A set has two halves

**Inputs** are the shorthand — extracted from the day-file scan, de-identified, committed under the set's `shorthand/`.

**Reference** is what the clinician actually submitted to the portal. It is a **baseline to beat, not a target to match**: the submitted notes were written under time pressure at the end of a long shift, and the skill exists to do better than that consistently. A difference from the reference is therefore *better*, *worse*, or *neither* — and only *worse* is a regression.

The reference has to be read, never inferred. Inferring it from the skill's own prior output produces a set that agrees with itself forever.
