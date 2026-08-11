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

**Compute the age before removing either.** Nearly half this clinician's encounters give a date of birth and no age. Removing the visit date and redacting the date of birth in the same pass leaves a case whose age cannot be recovered by anyone — including the fixture, which needs it. Derive first, then strip both. A fixture that has lost its age is testing the missing-age rule whether it meant to or not.

## What an assertion is

A claim, in the clinician's own words, about what a correct run must contain — checked against the output text.

It is deliberately **not** a diff of the note prose: prose varies legitimately from run to run, and a bar that trips on style gets ignored within three runs.

It is also deliberately **not** the drift-matrix verdicts from `clinical-note` step 7. Those are the skill grading itself — a run that misses snuff box tenderness is precisely the run that also emits `row 2: PASS`. See [docs/adr/0001](../docs/adr/0001-fixture-asserts-on-named-findings.md).

## The pass bar

**DRIFT assertions are binary.** All of them, every run, no exceptions. Each one is a documented abnormal that reached the Objective and stopped there — the defect class the skill exists to catch. One miss fails the run.

**FILLED assertions are binary.** Same bar as DRIFT, different subject: what the skill does with a value the shorthand never supplied. DRIFT asks whether a *given* abnormal survived to the Assessment; FILLED asks whether a *generated* one was produced at all, was plausible for that patient, and then survived the same way. They are separate classes because a set can have one and not the other — a set whose inputs all carry complete vitals can hold no FILLED row, and a set with no reference read may hold no DRIFT row.

**REPORTED assertions are counted, not enforced.** Differential depth, screening content, education phrasing. They move with the model and the wording; tracking the count catches slow erosion without failing a run over style.

**What makes a row enforceable is that it does not move with wording.** A row resolving to a value or its absence — is there a pressure in the FILLED block, is it below 130 over 80, does the finding appear in the Assessment — can be binary. A row turning on how well something is phrased cannot, and belongs in REPORTED however important it is.

## Running a set

1. Feed each case's shorthand to the named skill, on the stated branch.
2. Check the output text against that case's assertions.
3. Report every class the set defines — `DRIFT n/n` and `FILLED n/n`, both of which must be full, and `REPORTED n/m`. A set that defines no rows of a class omits its line rather than reporting `0/0`.
4. Any DRIFT or FILLED miss names the case, the finding, and where the finding landed instead.

Re-run after every `SKILL.md` edit. That is the entire point: a measurable delta instead of a judgment call.

**A first run graded by whoever wrote it is a baseline, not a pass.** The same objection that disqualified the drift-matrix verdicts in [ADR 0001](../docs/adr/0001-fixture-asserts-on-named-findings.md) applies to any run scored by the pass that produced it. Asserting against the output text rather than a self-report is what makes the score checkable at all — someone else can re-read the same text and disagree. Until someone does, the number's job is to give the next run something to differ from.

## Sets

| Set | Skill | Cases | Inputs | Reference | Last run |
| --- | --- | --- | --- | --- | --- |
| [day-a](day-a/assertions.md) | `clinical-note`, SOAP branch | 10 | [extracted](day-a/shorthand/) | read | `DRIFT 10/10` · `REPORTED 14/14` |
| [day-b](day-b/assertions.md) | `clinical-note`, SOAP branch | 12 | [extracted](day-b/shorthand/) | read | never run |
| [peds-bp](peds-bp/assertions.md) | `clinical-note`, SOAP branch | 5 | [extracted](peds-bp/shorthand/) | **owed** | never run |

The reference notes themselves live in `scratch/day-a-reference/` and `scratch/day-b-reference/`, gitignored — they carry the visit date, the site, patient references and social-history detail that the committed half deliberately does not.

**A reference is not always a date search.** day-b's twelve were filed under eleven visit dates: one encounter carries the *entry* date rather than the encounter date, so a date-range search returns eleven of the set plus one stranger seen the same day. It was found by patient creation order instead, and confirmed by content. Budget for a reference read to be a reconciliation rather than a query, and record how the set was matched — `scratch/day-b-reference/README.md` is the worked example.

**A set is not always a day.** `day-a` and `day-b` are whole shifts and are named for that. `peds-bp` is the under-6 half of one shift, named for the question instead — because calling it `day-c` would claim a completeness it does not have. Either shape is fine; what is not fine is a partial set that reads as a whole one. **A set scoped to part of its source says so in its own README, and names what it left out.**

**day-b exists to test the *filled* half of the vitals license,** which day-a cannot reach: all ten day-a cases carry a complete vital line, so nothing there exercises a vital the skill had to invent. Nine of day-b's twelve carry none at all.

It shipped inputs-only for a while, on the argument that a filled vital was never in the shorthand and so has nothing to have drifted from — true of its FILLED rows, and it left the set unable to carry a drift row at all. **The reference was read 2026-08-11 and that half is now built.** It paid twice over: it supplied five DRIFT rows, and it failed two of day-b's own four FILLED rows — which is the outcome that makes a bar worth having, since a bar the reference clears everywhere is set too low. See [day-b/assertions.md](day-b/assertions.md).

**`peds-bp` tests the shape day-b's inputs cannot reach.** day-b's nine vital-less cases are the corpus's dominant pattern — the line written whole or not at all. Under 6 that pattern inverts: measured 2026-08-11, 18 of the 21 under-6 encounters carry a vital line with the **blood pressure alone** missing, against 11 of 106 for encounters aged 20 and over. A selective absence is a decision rather than a transcription gap, and [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11) settled that it is filled anyway. `peds-bp` is what holds that ruling to it. Its reference is owed on the same terms. See [peds-bp/assertions.md](peds-bp/assertions.md).

## A set has two halves

**Inputs** are the shorthand — extracted from the day-file scan, de-identified, committed under the set's `shorthand/`.

**Reference** is what the clinician actually submitted to the portal. It is a **baseline to beat, not a target to match**: the submitted notes were written under time pressure at the end of a long shift, and the skill exists to do better than that consistently. A difference from the reference is therefore *better*, *worse*, or *neither* — and only *worse* is a regression.

The reference has to be read, never inferred. Inferring it from the skill's own prior output produces a set that agrees with itself forever.
