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

**FILLED assertions are binary.** Same bar as DRIFT, different subject: what the skill does with a value the shorthand never supplied. DRIFT asks whether a *given* abnormal survived to the Assessment; FILLED asks whether a *generated* one was produced at all, was plausible for that patient, and then survived the same way. They are separate classes because they ask different questions of the same run, and a set can hold rows of one and none of the other. A set with no reference read may hold no DRIFT row. A set whose inputs supply every value the note needs holds no FILLED row.

**FILLED asks one more thing, and it runs the other way.** Everything above is additive — what work the generated value made the note do. [Issue #27](https://github.com/mshamblin5150-code/clinical-skills/issues/27) was the subtractive case: a generated value making the note do *less*, by becoming the reason a workup was withheld. `clinical-note` rules that a filled value may raise an obligation and never discharge one, and a row holding a set to that is a FILLED row for the same reason the others are — its subject is a value the shorthand never supplied. day-b's B9 is the worked example. **Note which side of a set's reference read this lands on:** a submitted note labels no filled values, so this is the one FILLED question a reference can never answer, however carefully it is read.

**But FILLED is no longer the vitals class**, and the difference is worth stating because it changes which sets can host one. What admits a row is that the value was generated and the skill licensed generating it; `clinical-note` states that license as a test — a box demands a value and the shorthand constrains none — and names three members. day-b's B1 through B4 are the vital and body-measurement half, and only its nine vital-less cases reach them. B5 through B8 are the OLDCARTS half, and they reach all twelve: shorthand never supplies eight OLDCARTS elements, so **that half of the class fires on every input there is.** A set with complete vitals throughout, like day-a, is no longer a set with no FILLED row to write. B9 belongs to neither half — it is the subtractive question above, asked of all three members at once, and it reaches whichever cases had a value generated for them.

**ANCHOR and CODE assertions are binary, and they belong to `icd10-cpt` rather than to `clinical-note`.** DRIFT asks what a note did with a finding it was given; FILLED asks what it did with one it generated under license. Neither question means anything for a skill that generates nothing and writes no prose — which is why `filled-anchor` brings two classes rather than reusing these. ANCHOR asks whether a proposed code rests on a number the encounter actually recorded — the rule [#10](https://github.com/mshamblin5150-code/clinical-skills/issues/10) added, whose whole failure mode is that it is invisible when it fails. CODE asks whether a proposed code exists, carries its official descriptor, and can be submitted.

**CODE is the only class in this repo a machine decides.** `python tools/icd10_lookup.py` answers all three of its questions against `reference/icd10cm-2026.sqlite`, so no reader is involved and two readers cannot disagree. Every other class here, binary ones included, needs someone to read the output and rule.

**CODING assertions are binary**, and they belong to `clinical-note` — the codes a **note** carries, as against the codes a worksheet proposes. DRIFT asks whether a given abnormal survived, FILLED asks what happened to a value nobody supplied, and CODING asks whether the codes attached to what survived say what the encounter can support. It is a separate class because a set can hold one and not the others: its rows turn on a code string being present or absent in the note text, which needs neither a reference read nor a vital-less input.

**CODING is not CODE, and the names sit close enough to be worth separating.** CODE asks whether a code number is real, correctly described and submittable, and `icd10_lookup.py` answers it. CODING asks whether the note attached a code that claims more than the encounter established, and **no lookup can decide that** — `U07.1` is a real, billable, correctly described code, which is precisely what makes it wrong on a COVID nobody swabbed. A set passing every CODE row can fail every CODING row with codes that all exist.

**REPORTED assertions are counted, not enforced.** Differential depth, screening content, education phrasing. They move with the model and the wording; tracking the count catches slow erosion without failing a run over style.

**CODING is binary and differential *depth* is not, which looks like a contradiction and is not.** How many entries a differential runs to moves with the model, so it is counted. Whether each of those entries carries a code does not move at all — it is two integers compared. The line is the one below: the subject can be soft while the claim about it stays hard.

**What makes a row enforceable is that it does not move with wording.** A row resolving to a value or its absence — is there a pressure in the FILLED block, is it below 130 over 80, does the finding appear in the Assessment — can be binary. A row turning on how well something is phrased cannot, and belongs in REPORTED however important it is.

## Running a set

1. Feed each case's input to the named skill, on the stated branch. For most sets that is the shorthand; for a set whose skill consumes a finished note it is the note and its tier block, and the set's own `Inputs` column says which.
2. Check the output text against that case's assertions.
3. Report every class the set defines — the binary ones must be full, and `REPORTED n/m` alongside. A set that defines no rows of a class omits its line rather than reporting `0/0`.
4. Any miss in a binary class names the case, the finding or the code, and where it landed instead. For a CODING miss that is the entry and the code it carried, or that it carried none.

Re-run after every `SKILL.md` edit. That is the entire point: a measurable delta instead of a judgment call.

**A first run graded by whoever wrote it is a baseline, not a pass.** The same objection that disqualified the drift-matrix verdicts in [ADR 0001](../docs/adr/0001-fixture-asserts-on-named-findings.md) applies to any run scored by the pass that produced it. Asserting against the output text rather than a self-report is what makes the score checkable at all — someone else can re-read the same text and disagree. Until someone does, the number's job is to give the next run something to differ from.

**So separate the two passes, and it is cheap enough that there is no excuse not to.** day-b and peds-bp were both run this way on 2026-08-11: subagents wrote the notes with the assertion files withheld, a fresh pass graded the output text against them, and the orchestrating pass re-derived every row from the output files having authored none of them. What it bought was immediate — **each set failed a row**, and in both cases the note's own drift matrix had reported that row as a pass, once citing Plan text the Plan did not contain. That is ADR 0001's argument happening rather than being made, twice in one sitting.

**day-b run 2 is the third instance and the most useful one, because the run passed.** Separated the same way on 2026-08-12 — twelve generating passes, five fresh grading passes split by class, and an orchestrating pass that authored no note — it cleared every binary row, **and a note's drift matrix was still wrong about a Plan**, on a row that passed anyway. The case and the quotation are in [day-b/assertions.md](day-b/assertions.md).

So the separation is not just for catching failures. **A self-report can be wrong in a run that passes**, where nothing else would ever prompt anyone to check it.

**Withhold the set's `shorthand/README.md` too, not just `assertions.md`.** Both inputs READMEs state what their set exists to test, and day-b's names two assertion rows outright. Three of the ten generation passes on that day read one — five of the seventeen cases — having reasoned that a file in the inputs directory was an input. All five were regenerated from scratch by passes that had not.

**Paste the input instead of pointing at it, and the reasoning has nowhere to go.** day-b run 2 gave each generating pass its shorthand inline and told it that `fixtures/` was closed for any purpose, naming this repo's own `AGENTS.md` link to this file as one not to follow. **Twelve of twelve reported opening nothing there, and nothing was regenerated** — against five of seventeen the run before. A path into the inputs directory is what makes the neighboring file look like an input; without one there is no directory to be curious about.

**That audit is a self-report, and it cannot be made anything better.** Each pass was asked afterwards to list every file it opened; three said yes, the rest said no, and the yeses are the only reason the regeneration happened. **Nothing in the output distinguishes a contaminated run from a clean one** — that is what makes the contamination worth avoiding, and it is also why no later check can catch it. ADR 0001 rejects a self-report as *evidence for a verdict*, which this is not: it is an admission against interest, and the correct response to one is to re-run rather than to trust it. **Withhold the file up front**, because the audit cannot be relied on to find what the prompt failed to prevent.

## Sets

| Set | Skill | Cases | Inputs | Reference | Last run |
| --- | --- | --- | --- | --- | --- |
| [day-a](day-a/assertions.md) | `clinical-note`, SOAP branch | 10 | [extracted](day-a/shorthand/) | read | `DRIFT 10/10` · `REPORTED 14/14` |
| [day-b](day-b/assertions.md) | `clinical-note`, SOAP branch | 12 | [extracted](day-b/shorthand/) | read | `DRIFT 7/7` · `FILLED 9/9` · `CODING 2/2` · `REPORTED 0/1` — all 19 rows, see below |
| [peds-bp](peds-bp/assertions.md) | `clinical-note`, SOAP branch | 5 | [extracted](peds-bp/shorthand/) | read | **`FILLED 5/6`** — **6 of 9 rows**, see below |
| [obesity-bmi](obesity-bmi/assertions.md) | `clinical-note`, SOAP branch | 4 | [extracted](obesity-bmi/shorthand/) | **owed** | never run |
| [filled-anchor](filled-anchor/assertions.md) | `icd10-cpt` | 12 | [finished notes](filled-anchor/notes/) | read | `ANCHOR 5/5` · `CODE 4/4` · `REPORTED 1/2` |

**One of the four sets that have run fails its bar** — `peds-bp`, on a filled value that reaches the Objective and stops, which is the defect this repo exists to catch appearing in the skill's own output. **day-b failed the same way on run 1 and passes on run 2**, which did not fix it: see below. Filed against the skill as [#47](https://github.com/mshamblin5150-code/clinical-skills/issues/47), and not resolved by editing a fixture. Which rows, on which cases, and where each finding landed instead live in the sets' own files.

**`filled-anchor` is not among them, and it could not have been.** Its binary rows are full, and the defect above has no subject in it: `icd10-cpt` writes no Objective and generates no value, so there is nothing there to reach one and stop. What it can catch is the same value one skill later, which is the whole of why it exists — and on run 1 it caught nothing, because the run refused every filled anchor it was offered. **A pass on a set this young is a baseline, not a clean bill.**

**day-b run 2, 2026-08-12, on `e4cd503`: all nineteen rows scored, every binary class passing.** It closed the nine-row gap run 1 left and run 1's one binary miss. Run 1's other miss was `REPORTED 0/1`, and run 2 scored that again. [#55](https://github.com/mshamblin5150-code/clinical-skills/issues/55).

**Run 1's own denominator is worth keeping, because the reason it was partial is the pattern below.** It graded **ten of nineteen**: D6, B5 through B8, C1 and C2 landed while it was in flight — three separate tickets, one arriving between its commit and its merge — and D7 and B9 landed after it, from [#27](https://github.com/mshamblin5150-code/clinical-skills/issues/27). Its `CODING` line is absent because the class did not exist, which is a different thing from a class with no rows. Scoring those rows from run 1's output was available and was refused: they exist *because* `clinical-note` changed, and the notes predate the change, so the number would have belonged to neither commit.

**That denominator read eighteen here until run 2 recounted it, and the missing row was D7.** #27 added *two* rows rather than one, and this file recorded only B9 while [day-b/assertions.md](day-b/assertions.md) said nineteen throughout. Two committed files disagreeing about how many rows a set has is the cheapest possible version of the problem the next paragraph describes, and it survived because nothing recomputes a denominator that is typed in prose.

**peds-bp's covers six of its nine, for the same reason and from a different direction.** Its reference read landed while the run was in flight ([#25](https://github.com/mshamblin5150-code/clinical-skills/issues/25)), bringing a DRIFT row and two REPORTED rows the run had no way to score. So one set gained rows from the skill changing under it and the other from its reference being read, and **both partial denominators come from the same cause: a set is worked on by more than one ticket at a time.**

**day-b run 2 is the counter-example, and it is worth saying what made it one.** `skills/` did not move between the commit it was generated on and the commit it merged to, and neither did day-b's own rows — so for once the notes, the rows and the skill all belong to the same state of the repo. That was luck rather than process: two other fixture tickets landed on `main` during the run, and both happened to touch other sets.

**A passing run is worth less than the column makes it look.** [#47](https://github.com/mshamblin5150-code/clinical-skills/issues/47) is unfixed and recurred on a case that still passed; B2 cleared on its first exit again, so the clause [#23](https://github.com/mshamblin5150-code/clinical-skills/issues/23) settled remains unexercised; and **two open tickets could move the recorded score**, [#69](https://github.com/mshamblin5150-code/clinical-skills/issues/69) and [#70](https://github.com/mshamblin5150-code/clinical-skills/issues/70), both turning on what a row means rather than on what the run did. Which rows, which cases and which numbers live in [day-b/assertions.md](day-b/assertions.md) and are deliberately not restated here.

**A set that is being added to faster than it is being run is worth noticing as a pattern**, not just as that run's bad luck. Rows are cheap to write and a run costs a generation per case plus a grading pass, so the gap widens by default. day-b closed a nine-row gap by running twelve generations and five graders; it had taken three tickets and one day to open.

The reference notes themselves live in `scratch/day-a-reference/`, `scratch/day-b-reference/` and `scratch/peds-bp-reference/`, gitignored — they carry the visit date, the site, patient references and social-history detail that the committed half deliberately does not.

**A reference is not always a date search.** day-b's twelve were filed under eleven visit dates: one encounter carries the *entry* date rather than the encounter date, so a date-range search returns eleven of the set plus one stranger seen the same day. It was found by patient creation order instead, and confirmed by content. Budget for a reference read to be a reconciliation rather than a query, and record how the set was matched — `scratch/day-b-reference/README.md` is the worked example.

**And when the date search does work, the reconciliation is still owed.** All ten of `peds-bp`'s source shift carry the right visit date, so the query half was trivial. Matching them to notes was not: one encounter's Age field disagrees with its own shorthand, so age alone matches nine of ten and leaves one record and one note unpaired. Patient creation order settled it there too. **The discriminator that survived both reads is the order the patients were created in, not the date and not the age.**

**A day file is sometimes a census of its shift and sometimes not.** day-b's shift held thirteen encounters against twelve notes; `peds-bp`'s source shift is ten against ten. Neither is the rule, which is why both were counted rather than assumed.

**A set is not always a day.** `day-a` and `day-b` are whole shifts and are named for that. `peds-bp` is the under-6 half of one shift, named for the question instead — because calling it `day-c` would claim a completeness it does not have. Either shape is fine; what is not fine is a partial set that reads as a whole one. **A set scoped to part of its source says so in its own README, and names what it left out.**

**And a set is not always for `clinical-note`.** `filled-anchor` is the first set for a different skill, and it is a fourth shape: its inputs are **finished notes** rather than shorthand, because [icd10-cpt](../skills/icd10-cpt/SKILL.md) states as a hard requirement that what it consumes is *"the note body and the tier block beneath it"*. A set that fed it shorthand would be testing a shape the skill refuses. It also brings two classes of its own — see the pass bar above — because DRIFT and FILLED both ask what a note did with a finding, and neither question means anything for a skill that generates no values. **What travels between skills is the discipline, not the row names.**

**And a set is not always one source.** `obesity-bmi` is four encounters from **three different day files**, which is a third shape and the one that needs the most care: a set drawn from across the corpus can look like a curated sample chosen to make a skill pass. It is not one — those four are the entirety of a shape the corpus contains twice over, which its README states as a count rather than an assurance. **A set spanning several sources says how it was selected, and the selection has to be recomputable** — `tools/corpus_census.py` carries the markers that found these, so the population can be re-derived rather than taken on trust.

**day-b exists to test the *filled* half of the vitals license,** which day-a cannot reach: all ten day-a cases carry a complete vital line, so nothing there exercises a vital the skill had to invent. Nine of day-b's twelve carry none at all.

**It hosts the first CODING rows too**, which is a different thing from what it was built for and needs no reference to check: [#19](https://github.com/mshamblin5150-code/clinical-skills/issues/19) put a code on every differential entry, and case 9 documents a COVID contact that was never swabbed — the one input in the set where an organism-specific code would assert what the note denies. Both rows read the output text alone. Their `Reference did` cells are owed, and the set's own file says so.

It shipped inputs-only for a while, on the argument that a filled vital was never in the shorthand and so has nothing to have drifted from — true of its FILLED rows, and it left the set unable to carry a drift row at all. **The reference was read 2026-08-11 and that half is now built.** It paid twice over: it supplied the set's DRIFT rows, and it *failed* rows day-b had written from the inputs alone — which is the outcome that makes a bar worth having, since a bar the reference clears everywhere is set too low. Counts and verdicts live in [day-b/assertions.md](day-b/assertions.md) and are deliberately not restated here.

**`obesity-bmi` tests the *other* thing day-b's inputs cannot reach.** day-b forces a height, a weight and a derived BMI onto all nine of its vital-less cases, and then covers that BMI only if it happens to land abnormal — nothing in those twelve makes it land anywhere. [Issue #15](https://github.com/mshamblin5150-code/clinical-skills/issues/15) settled 2026-08-11 that the missing row is real and is **not** contained in day-b's B3: B3 fires on an abnormal value, and the missing row fires on a *normal* one, where a patient the shorthand calls obese is handed a BMI of 24 and the note says nothing. Anchoring it needs documented obesity with no weight to compute from, and day-b has none. **The corpus has some, and every one of them is in this set** — with post-bariatric encounters as controls, since a past bypass is where a sub-30 BMI is genuinely accountable. How many, and how they were found, live in that set's own README and are deliberately not restated here. Its reference is owed on the same terms, across three day files rather than one.

**`peds-bp` tests the shape day-b's inputs cannot reach.** day-b's nine vital-less cases are the corpus's dominant pattern — the line written whole or not at all. Under 6 that pattern inverts: measured 2026-08-11, 18 of the 21 under-6 encounters carry a vital line with the **blood pressure alone** missing, against 11 of 106 for encounters aged 20 and over. A selective absence is a decision rather than a transcription gap, and [issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11) settled that it is filled anyway. `peds-bp` is what holds that ruling to it.

**Its reference was read 2026-08-11** ([#25](https://github.com/mshamblin5150-code/clinical-skills/issues/25)) and it confirms the ruling is the clinician's own practice: all four Medatrax vital boxes populated on all five under-6 encounters, a blood pressure generated every time, not one blank and not one gap. It also supplied the set's single DRIFT row — a documented 99.9th-percentile weight the submitted note states and never acts on — and the *out of reach* verdict class the set could not host unread.

**It pushed in the other direction too, and that is recorded rather than smoothed over.** day-b's read *failed* FILLED rows that set had written from its inputs alone; peds-bp's read failed none of them, and some passed **vacuously** — the reference generated no abnormal value, so the rows that price a filled abnormal were never put under load. **A row the reference never approached has not been tested, and a set that reports it as a pass is flattering itself.**

**Run 1 then failed one of exactly those rows**, which is the cleanest argument in this file for keeping both halves. A reference read and a run answer different questions: the read says what the clinician did and the run says what the skill does, and a row can look vacuous against one while biting on the other. **Neither half is a substitute for the other, and a set with only one of them does not know which it has.** Which rows, and the counts, live in [peds-bp/assertions.md](peds-bp/assertions.md) and are deliberately not restated here.

**`filled-anchor` tests what happens to a filled value one skill later.** day-b, `obesity-bmi` and `peds-bp` all grade the skill that *generates* a value. None of them can see what the next skill does with it, and [issue #10](https://github.com/mshamblin5150-code/clinical-skills/issues/10) found that `icd10-cpt` could not tell a filled value from a given one at all — a filled `BMI 36.4` is the same eleven characters as a measured one, and `Z68` is banded to 1.0 BMI units, so one invented inch moves a code. The rule #10 added routes such a code to `NOT CODED, ANCHOR WAS FILLED`; **its failure mode is that a run which ignores it produces a worksheet that reads perfectly well.** This set is what makes that cost something. Its inputs are day-b's own twelve encounters carried one stage further down the pipeline, and its reference was free — day-b had already read it. See [filled-anchor/assertions.md](filled-anchor/assertions.md).

## A set has two halves

**Inputs** are whatever the set's skill consumes, committed under the set. For every `clinical-note` set that is the shorthand — extracted from the day-file scan, de-identified, under `shorthand/`. For `filled-anchor` it is finished notes with their tier blocks, under `notes/`, because that is what `icd10-cpt` takes.

**An input further down the pipeline is a skill's output, and that carries one obligation.** A set built on generated material must not read as endorsing it: the note is *real input*, not *correct input*, and a row quoting it is quoting an artifact rather than a source. **`filled-anchor` names the generating run's score in its own *Still unresolved*, and it is no longer the absence of one that has to be disclosed** — day-b has since run and *failed a FILLED row*, so these twelve notes are known-real, known-incomplete, and known-wrong in at least one place. That is a stronger reason to keep the obligation than "unscored" ever was.

**Reference** is what the clinician actually submitted to the portal. It is a **baseline to beat, not a target to match**: the submitted notes were written under time pressure at the end of a long shift, and the skill exists to do better than that consistently. A difference from the reference is therefore *better*, *worse*, or *neither* — and only *worse* is a regression.

The reference has to be read, never inferred. Inferring it from the skill's own prior output produces a set that agrees with itself forever.
