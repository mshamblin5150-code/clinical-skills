# filled-anchor — assertion set

Twelve finished notes, each a note body plus its tier block. Skill: [`icd10-cpt`](../../skills/icd10-cpt/SKILL.md).

The inputs are day-b's twelve encounters carried one stage further down the pipeline — `clinical-note` output rather than shorthand, because that is what this skill consumes. Provenance, selection and de-identification are in [notes/README](notes/README.md).

Opened for [issue #17](https://github.com/mshamblin5150-code/clinical-skills/issues/17).

## Why the set exists

[#10](https://github.com/mshamblin5150-code/clinical-skills/issues/10) found that `icd10-cpt` anchors codes to note text and that a **filled** value is note text.

**The rule it added has since been reversed, and the set survives the reversal.** #10 routed a filled-anchored code to step 4 *uncoded*, under `NOT CODED, ANCHOR WAS FILLED`. [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) found that this made `clinical-note` and `icd10-cpt` apply different rules to one number — the note writing `E66.3` into a submitted Medatrax field while the worksheet refused it — and ruled the disagreement a defect in itself. **So the code is now proposed and marked** `SOURCE: filled`, listed under `CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING`. The rows moved with it; what they test did not.

**The failure mode is silent in exactly the way drift is, and marking did not retire it.** A run that quietly proposes `Z68.30` off a filled BMI **with no `SOURCE` line** produces a worksheet that reads perfectly well: a real code, a real descriptor, a real anchor quoted verbatim out of the Objective. Nothing in the output looks wrong. That is still the thing this set catches — the pass condition changed from *absent* to *marked*, and the failure is unchanged.

**Every other skill in the repo is pinned by a set. This one was pinned by nothing.**

## Status

**The inputs are in.** All twelve, in [notes/](notes/).

**The reference is read.** All twelve submitted notes were opened in the portal on 2026-08-11 and are kept in `scratch/day-b-reference/`, gitignored. Their code lists were lifted on 2026-08-11 and every `Reference did` cell below rests on them. Reading it cost nothing — day-b had already paid for it.

**Run 2, 2026-08-16, on `184462d`: `ANCHOR 5/5` · `CODE 1/1` · `REPORTED 1/1` — seven of twelve
rows, and it passes.** [#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124).
Twelve generating passes with the input at a neutral path and `fixtures/` closed, four grading
passes split by row, and an orchestrating pass that wrote no worksheet. **The output is committed**
at [run-2/](run-2/), which no run in this repo has been before; that directory's README carries the
figures, the commands that recompute them, and what the generating passes disclosed about what they
opened.

**The denominators say what was scored rather than what exists**, on
[fixtures/README](../README.md)'s rule. ANCHOR is whole — A1 through A5, all five. `CODE 1/1` is
**C5 alone**: C1 through C4 were not re-run for their own sake, so their run-1 verdicts stand
against text and an output that are both gone, and mixing them into a run-2 digit would produce a
number belonging to neither commit. `REPORTED 1/1` is **R2 alone**, for the same reason on the other
side — R1 held on run 1 and was not re-scored.

**Nothing moved under it while it ran**, which is worth one sentence because
[fixtures/README](../README.md) has now counted six consecutive runs where something did.
`skills/icd10-cpt/SKILL.md` was last edited by `f8ac2f8` the day before, and neither it nor these
rows moved between the run's base commit and its merge.

**What each row cost is not the same as what each row proved.** A1's nine cases all mark and list
correctly, and two of them — 6 and 12, the adolescents — carry the double disclosure the row's
second limb was written for, each naming the CDC growth chart the repo does not ship. **Only case
12 enumerates `Z68.51`, `Z68.52` and `Z68.53` as the set the recall picks from**; case 6 names the
chart and the percentile it placed the patient at and does not list the bands. The distinction is
kept because a first draft of this paragraph claimed it of both and a second reader recounted.
**A3 is the row that had something to catch and did
not need to**: case 4 proposed `Z68.25` and `E66.3` unmarked off two given inputs, so the run
applied the rule narrowly rather than stopping coding the family. **A5's second limb bit on nothing
and was checked anyway** — `I10` appears on all four of its cases, and every appearance is a
refusal or a sentence declining the code rather than a proposal.

**Two things the rows did not ask for and the run did.** Cases 8 and 9 **withheld** `R03.0`,
quoting its own tabular note that the category records an episode in a patient with no formal
diagnosis — no row asks for that, and it means the run did not clear A4 and A5 jointly by proposing
both codes everywhere. And `SOURCE: filled` reached past the four families the skill names, onto
CPT `12001` and onto `R50.9` off a filled temperature. That is the skill's general form working —
*"The rule is general. It is not a rule about `Z68`"* — arriving somewhere this set had not
anticipated.

**Run 1, 2026-08-11: `ANCHOR 5/5` · `CODE 4/4` · `REPORTED 1/2`.** Output in
`scratch/filled-anchor-run-1/` — twelve worksheets and four graders, one per enforced class plus a
second settling of C1 through C3.

**That output no longer exists**, and it is worth saying plainly rather than leaving a reader to
discover it. `scratch/filled-anchor-run-1/` is in neither the main checkout nor any worktree as of
2026-08-15. So the paragraphs below describing what run 1 did are **the record of the run rather
than a thing anyone can now re-derive** — including the 65-of-66 figure #56 turned on. Nothing here
was reconstructed from it; #56's audit reads the committed *inputs* instead, which is why that is
the evidence C5 rests on. `scratch/` is gitignored by design and a worktree is removed when it
merges; **the run record is the first casualty of that this repo has had to write down.**

**That `ANCHOR 5/5` is now a score against superseded text, and it is withdrawn rather than
carried.** [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) reversed A1, A2
and A5 from *withhold the code* to *propose it marked*. Run 1 refused every filled anchor it was
offered, which is what earned the 5/5 — and under the rewritten rows that same behavior **fails
A1, A2 and A5 outright**, on thirteen case-instances. Nothing about the run changed and nothing
about it was wrong at the time; the bar moved underneath it.

**ANCHOR read `— (superseded)` from that ruling until run 2 refilled it**, on
[fixtures/README](../README.md)'s rule that *an unscored row shows up as a denominator; a row
scored against superseded text does not*. It now reads `5/5` again, against different text and a
different run — **the digit is the same and it is not the same number.** C1 through C3 are untouched by #46, and C4 gained a
sixth part that no run-1 worksheet could have carried, so its score is over a class that has since
grown in exactly the way that column already records. This is the
[#29](https://github.com/mshamblin5150-code/clinical-skills/issues/29) situation with the nouns
changed, and it takes #29's remedy: a disclosure here and a re-run ticket, filed as
[#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124).

**[#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56) then moved both remaining
columns, and it moved them in opposite directions.** It tightened `icd10-cpt` — a `complete` flag
now carries its reason, and a code whose descriptor says `unspecified` may not read `complete` at
all — and split the enforceable half of R2 out into a new binary row, **C5**.

- **`CODE` read `4/5` for run 1.** C5 is a row run 1 could not have been scored against, because
  the rule it holds a run to landed after it. That is the same growing-denominator story the
  paragraph above tells about C4 and #46, and the same one [fixtures/README](../README.md) has now
  recorded across every run this repo has made. The rows were not re-scored from run-1 output; that
  output no longer exists, and scoring it would have produced a number belonging to neither commit.
  **Run 2 scored C5 and it passes** — 0 faults over 200 flags, one command over a directory a
  reader can now open.
- **`REPORTED` read `1/1` for run 1, and that was a withdrawal rather than a correction.** R1 held
  on all twelve and stands. **R2's verdict was withdrawn**, on the same rule ANCHOR was withdrawn
  under: the row it was scored against had been replaced. The bare `complete` on `Z98.51` that cost
  run 1 the row is a **C5** failure rather than an R2 one, and what R2 asks today — is the reason a
  check or a stock phrase — was never scored against run 1's other 65 flags and now cannot be,
  because those worksheets are gone. **Run 2 scored it and it holds**, on evidence run 1's format
  could not have produced: see beneath the REPORTED table.

**So the run's one recorded miss has not been made to disappear**, which is the thing to check
whenever a denominator shrinks. It moved classes and got stricter: it was a counted miss in a
class the set still passed, and under C5 the identical flag fails an enforced row outright.
[#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124) is the re-run, and it now
covers C5 and R2 as well as ANCHOR.

**Every score here *was* reproducible from that directory, and the past tense is the point.** It
held four graders: `grade_anchor.py` for A1 through A5, `grade_c4.py` for C4 across both code
shapes, and C1 through C3 settled *twice* — `verify_c1_c3.py` reading the SQLite directly for a
verbatim descriptor diff, and `settle_c1_c3_via_lookup.py` shelling `python tools/icd10_lookup.py`
over all 149 distinct codes, which is the command
[#44](https://github.com/mshamblin5150-code/clinical-skills/issues/44) names. **The two agreed**,
and each grader exited non-zero on a failure so a stale one could not report a pass.

**None of that can be run today**, because the graders were in the run directory with the output
they graded. This paragraph used to open *"every score here is reproducible from that directory,
which matters more than usual because the directory is gitignored and a reader cannot see it from
the repo"* — and the sentence was describing the exposure at the moment it stopped being a
hypothetical. **Gitignored and reproducible are not compatible for longer than the directory
lasts.**

**Run 2 fixed both halves of that, and the second half is the one that was not asked for.**
[#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124) said the graders should
not go back in the same place, and they did not — `tools/anchor_scan.py` is committed and tested
beside `tools/specificity_scan.py`. **But a committed grader with nothing to point at is the same
problem one step along**, so the run's own output is committed too, at [run-2/](run-2/). Every
figure this file now states about run 2 is a command over a directory in the repo rather than a
number somebody wrote down.

**It was run twice, and the second run is the one reported.** The first was scored against the
skill as it stood before [#19](https://github.com/mshamblin5150-code/clinical-skills/issues/19)
landed, which is what put a code on every differential entry and gave C4 its second shape. The
counts are identical either way; **what the first run did not have was 114 differential codes and
three `NOT CODED, NOTHING ESTABLISHED IT` entries**, so its `CODE 4/4` was over a class that had
since grown. `Re-run after every SKILL.md edit` in [fixtures/README](../README.md) caught it — the
edit landed mid-run, between this branch's first commit and its second.

**One separation held and one did not, and they are different separations.** The rows were written
by the session that built the set; the run was produced by a later one that had not written them.
That is [#17](https://github.com/mshamblin5150-code/clinical-skills/issues/17)'s reason for not
building the set alongside #10 — *"a first assertion set written from this skill's own output is a
baseline agreeing with itself forever"*, which is
[ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md) — and it held. **What did not
hold is the second one: the session that produced run 1 also graded it.** On
[fixtures/README](../README.md)'s terms that makes it a baseline rather than a pass, and its job is
to give run 2 something to differ from.

**R2 did not hold, and the run was not what was wrong.** One specificity flag in twelve
worksheets — `Z98.51` on case 9 — read a bare `complete` with no axis named, against 65 of 66 that
carried a reason; the same code on case 2 carried one, so the run was at least inconsistent with
itself. It was left standing rather than corrected to make the row score, which is
[ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md)'s reasoning about editing
output to pass a row.

**A bare `complete` was output `icd10-cpt`'s own template permitted**, so the row was asking for
more than the skill required, and a run could satisfy the skill in full and lose the row.
[#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56) settled it on 2026-08-15 by
**tightening the skill rather than loosening the row** — the option that keeps what R2 was written
to catch, a run reaching for `complete` because it did not look. The audit that settled it, and
what it turned up that nobody had asked about, are under *CODE* beside C5.

## The classes are new, and two of them are

`DRIFT`, `FILLED` and `REPORTED` are `clinical-note`'s classes and the first two do not transfer. DRIFT asks whether a given finding survived from the Objective to the Assessment; FILLED asks what became of a value the skill generated under license. **`icd10-cpt` generates nothing and writes no prose** — it reads a finished note and returns a worksheet — so neither question has a subject here. That holds under [fixtures/README](../README.md)'s widened FILLED, which admits a row on the ground that *the value was generated and the skill licensed generating it*: this skill has no such license to exercise. This set defines two enforced classes of its own, both binary on [fixtures/README](../README.md)'s terms — each resolves to the presence or absence of a code, never to how something is worded.

- **ANCHOR** — does a proposed code rest on a number the encounter recorded? This is #10's rule and the reason the set exists.
- **CODE** — does a proposed code exist, carry its official descriptor, and submit? Settled by `python tools/icd10_lookup.py` against `reference/icd10cm-2026.sqlite`. What that buys the repo is stated once, in [fixtures/README](../README.md), and not restated here.

`REPORTED` is carried over unchanged: counted, not enforced.

## The reference is a baseline, not a target

Same four verdicts as [day-a](../day-a/assertions.md) and [day-b](../day-b/assertions.md), and only *worse* is a regression.

**On the row this set exists for, the reference cannot discriminate, and that is recorded rather than dressed up.** Not one of the twelve submitted notes carries a `Z68`, an `E66` or an `R03` — including case 9, where the clinician recorded a BMI of 37.8, class II obesity, and coded nothing off it. (**That 37.8 is the submitted note's number, not this set's input.** The committed `case-09.md` carries 35.2, generated independently by the run. Both are unmeasured; the row turns on neither.) Under #10 that looked like agreement with the rule, and it was not evidence of it: he coded none on cases 2, 3 and 4 either, where the height and the weight were **given** and a `Z68` was available on measured values. A source that never codes the family cannot tell *declines to code a filled BMI* from *never codes `Z68` at all* — which is #17's own phrase for what a set without the given-vitals control would be.

**Under [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) the same silence reads as a plain miss rather than as ambiguous agreement**, because the rows now ask for the codes rather than their absence. That is a cleaner position for the set and not a better reference: what changed is which direction the reference fails in, not how much it can discriminate. The paragraph is kept because the *reason* it cannot discriminate is unchanged, and a future set that swaps this reference for another has to satisfy it again.

**[#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) changed what that silence is worth, and it changed it in the reference's disfavor.** While the rows asked a run to *withhold* these codes, a source that never coded the family agreed with them for no reason — *neither*, vacuously, in all three cells. Now the rows ask a run to **propose them marked**, and never coding the family is a straightforward miss: A1 and A5 read ***better*** for a run that proposes them, rather than *neither* for a run that matches. **A2 stays out of reach** — it asks the worksheet to agree with a note's diagnosis field, and a submitted note has no worksheet to agree with.

**A3 still does the most discriminating**, and it is the row where the reference has something to be beaten on with both provenances present.

## ANCHOR — binary, all must pass

| # | Cases | Passes when | Fails when | Reference did |
| --- | --- | --- | --- | --- |
| A1 | 1, 5, 6, 7, 8, 9, 10, 11, 12 | Every code resting on a BMI with a filled input **is proposed**, carries `SOURCE: filled` naming the filled inputs, **and** appears under `CODED, ANCHOR WAS FILLED`. **On cases 6 and 12 the `Z68.5-` band also carries `CONFIDENCE: verify this number`** — the percentile is recalled, not looked up | Any `Z68.-` or `E66.-` the note's BMI supports is **withheld**; or reaches the proposed-code list **without** its `SOURCE` line; or is absent from step 4. **Or a pediatric `Z68.5-` claims `verified against ICD-10-CM FY2026`**, which the database cannot settle for a percentile | Coded no `Z68` and no `E66` on any of the twelve. Coded none on 2, 3 and 4 either, where both inputs were given — so it cannot discriminate between *declines to code* and *never codes the family*. **Proposing them marked is *better***|
| A2 | 1 | The strings `E66.3` and `Z68.26` **both appear** in the proposed-code list, each carrying `SOURCE: filled`, **and** both appear under `CODED, ANCHOR WAS FILLED`. The worksheet's for-entry codes **agree with the note's `Final diagnosis` field** on this pair | Either string is absent; either appears in the proposed list without its `SOURCE` line; **either is absent from the step-4 block**; or either is withheld while the note asserts it | Its own diagnosis list carries `L02.612`, `L03.032` and `Z72.0` — nothing from either family, and so no disagreement to reconcile. **Out of reach**: the row asks for something only a two-stage pipeline can owe |
| A3 | 4 | `Z68.25` **is** proposed, anchored, alongside `E66.3`, and **carries no `SOURCE` line** — the height and the weight are given, so the BMI is a measurement and nothing about it needs confirming | It is withheld or absent; **or it carries `SOURCE: filled`**, which misreports two given values as generated and would appear under `CODED, ANCHOR WAS FILLED` where it does not belong | Coded neither, on given values. **Proposing it is *better*** |
| A4 | 2, 3, 8, 9 | `I10` is proposed on all four. The documented hypertension is codable however the pressure arrived — 2 and 3 give it, 8 and 9 fill it | `I10` is withheld on 8 or 9 because the reading was filled | **Coded `I10` on all four**, across both provenances. The one row where the reference discriminates and passes. Matching it is *neither*; losing 8 or 9 is *worse* |
| A5 | 1, 5, 7, 10 | The filled blood pressure, in a patient whose history documents no hypertension, produces `R03.0` **carrying `SOURCE: filled`**, and it appears under `CODED, ANCHOR WAS FILLED`. **`I10` is not proposed on any of the four** — no single reading diagnoses hypertension, and none of these four documents one | `R03.0` is withheld, is proposed without its `SOURCE` line, **or is absent from the step-4 block**; **or `I10` is proposed off a filled pressure**, which is the failure marking does not license | Coded no `R03.0` anywhere, and no `I10` on these four. The `I10` limb is *neither*; proposing `R03.0` marked is *better* |

**Part of these five is settled by one command, and it is deliberately not the whole of any of them:**

```bash
python tools/anchor_scan.py <the run directory>
```

It checks two things no reader is needed for. **The mark and the listing must agree** — every code
carrying `SOURCE: filled` appears under `CODED, ANCHOR WAS FILLED`, and every code that block lists
carries `SOURCE: filled` on its own entry — which is A1's, A2's and A5's fail condition with the
reading taken out of it. And **a pediatric `Z68.5-` may not read `verified against ICD-10-CM
FY2026`**, which is A1's second limb.

**A clean scan is not a walked row, and the gap is most of ANCHOR.** Whether a note's BMI *had* a
filled input, whether `I10` was rightly absent, whether case 4's `Z68.25` rests on two given values
— each compares a worksheet to a note, and **the note is not in the run directory**. A3 in
particular is invisible to it: a run that stopped coding the family altogether marks nothing, lists
nothing, and the tool reports **not having scanned** rather than a pass. That refusal is the same
one `guidelines_search.py` makes, and here it is load-bearing: the pre-#46 heading
`NOT CODED, ANCHOR WAS FILLED` is deliberately not read as this block, so a run reproducing run 1
exits 2 rather than scoring clean for the behavior #46 reversed.

### A3 is the row that stops the other four passing vacuously

A run that proposes no `Z68` and no `E66` on any input passes A1, A2 and A5 having tested nothing — and it is not a hypothetical run, it is what the reference did. That is the defect #17 named in advance, and it is the same shape day-b names in its own B1/B2/B3 chain.

**A3 closes it, and case 4 is the only case in the shift that can.** Its shorthand supplies `ht 6'2" wt 200`; the note derives BMI 25.7 from two given inputs and says so in the tier block; 25.7 is overweight, so `E66.3` is a documented diagnosis and `Z68.25` is its required secondary. A run that refuses `Z68.25` has not applied #10's rule, it has stopped coding the family.

**Cases 2 and 3 are deliberately not in A3, and they are the set's own given-vitals cases.** Both derive a BMI from a given height and a given weight — 24.0 and 20.4 — and both notes coded a bare `Z68` off it. But a `Z68` at a normal BMI has no associated reportable condition under it, and whether it should be assigned at all is an **official-guidelines** question. `icd10-cpt` says outright that *"nothing in it encodes the official coding guidelines"*, and this set is about provenance, not about guideline compliance. A row that turned on that would be testing something the skill does not claim to do. Case 4 is the clean anchor because its BMI carries `E66.3` with it.

### A2 is not contained in A1, and the distinction is the whole of its value

A1 fails a run that proposes case 1's `E66.3` unmarked, so a row that only said *mark it* would be A1 with a shorter case list.

**A2 is the agreement row**, and it is the one #46 changed most. Under #10 it asked the worksheet to *contradict* the note out loud. Under #46 the two are not allowed to disagree at all, so A2 asks the opposite: **does the worksheet's for-entry list carry the same pair the note's `Final diagnosis` field carries, marked?** A run can still fail it by dropping `E66.3` silently — passing A1, whose pass condition names the *BMI* and not the codes — and hand back a worksheet that disagrees with the note above it with nothing saying which is right. That was the #10-era defect and it is still a defect; only the direction of the fix moved.

**The row is worded as a string test on purpose.** An earlier draft failed a run when the pair was absent *"with no mention that the note asserts it"*, and *mention* is a reader's ruling — the thing [fixtures/README](../README.md) puts in REPORTED however important it is. What A2 asks now resolves without judgment: do the two strings appear in the proposed list, does each carry a `SOURCE` line, and do both appear under `CODED, ANCHOR WAS FILLED`. A run that satisfies that has agreed with the note and disclosed the provenance; a run that satisfies it *badly* is a REPORTED matter this set does not carry.

**Case 1 has changed roles and the row has not.** Under #10 it was the input's one defect, the case where the note asserted what the worksheet had to refuse. Under #46 it is the input's one **correct** case, and the other eleven are the deviation — six refusing the family outright, two silent. Nothing about A2 needed rewriting for that beyond its pass condition, which is the argument for having written it as a string test rather than as a judgment about disclosure.

**Case 1 is the only case in the twelve that can carry this row**, and its scarcity is the argument for having it. Which of the other eleven refused the code family out loud and which said nothing is counted in [notes/README](notes/README.md) and deliberately not restated here. What matters for the row is that a set which had not looked would have found the run unanimous.

### The two adolescents are inside A1, not beside it

`icd10-cpt` singles out the adolescent case: `Z68` adult codes run from 20 years, ages 2–19 take `Z68.5-`, and *"a filled height and weight for an adolescent produces a percentile that is invented twice over."*

**day-b has two, not one**, and they are the same two day-b itself names — cases 6 and 12, aged 17 and 16. Both carry a filled height, a filled weight and a derived BMI: 5'10" / 160 lb / 23.0 and 5'5" / 130 lb / 21.6.

**They behave differently in the input, which is why both are worth naming.** Case 12's note reached the pediatric band and refused it out loud — *"Z68.52 … is deliberately NOT coded"*, citing the 2-to-19 rule. **Case 6's note says nothing about the code family in either direction.** So one input demonstrates the refusal and the other leaves it entirely to the run.

**Neither gets a row of its own, and [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) gave A1 a second limb instead.** A pediatric row would be nested inside A1's `SOURCE` requirement rather than disjoint from it — the containment test [#15](https://github.com/mshamblin5150-code/clinical-skills/issues/15) and [obesity-bmi](../obesity-bmi/assertions.md) both apply before a row is added. **But the confidence limb is not nested**, and it needed adding: `Z68.5-` is a CDC growth-chart percentile, this repo ships the codes without the charts, and a run that looks up the *code* has still only recalled the *band*. A worksheet claiming `verified against ICD-10-CM FY2026` on `Z68.52` is asserting a check nothing performed.

**So an adolescent's disclosure has two limbs where an adult's has one** — the filled inputs, and the recalled percentile — and A1 now fails a run that carries only the first. [#123](https://github.com/mshamblin5150-code/clinical-skills/issues/123) ships the charts and retires the second limb; until then the row is what keeps it from going unsaid. **The direction of the failure has flipped since these notes were generated**: case 12's input refuses `Z68.52` outright and case 6 says nothing, and under #46 both are wrong where the refusal used to be right.

### A4 is the control the ticket asked for, in a different family

[#17](https://github.com/mshamblin5150-code/clinical-skills/issues/17) asks for *"a control on the other side: a documented obesity diagnosis, which stays codable as `E66.-` however the vitals arrived."* **This shift documents no obesity** — day-b's twelve carry none, which is the finding that sent the obesity rows to [obesity-bmi](../obesity-bmi/assertions.md) in the first place.

The control exists here on the hypertension axis instead, and it is structurally identical: a **reading** code that a filled value must not earn (`R03.0`, A5) and a **diagnosis** code that survives whatever the reading's provenance (`I10`, A4). Both families are named in `icd10-cpt`'s own list of four codes that key off a single number.

**A4 is also the only place the reference does real work.** It coded `I10` on cases 2 and 3, where the pressure was given, and on cases 8 and 9, where it was filled — the same code across both provenances, which is exactly the discrimination A1's cells cannot make. It is the evidence that the diagnosis half of the rule is not merely a carve-out written to be safe.

**The `E66.-` instance of A4 is owed and is not in this set.** It needs a patient whose shorthand documents obesity and whose note fills the measurement, which is `obesity-bmi` cases 1 and 2 — never run, so no note exists to feed. Recorded under *Still unresolved*.

## CODE — binary, all must pass

**Scoped to codes the run adds or upgrades.** Each input note already carries a `Preexisting diagnoses (ICD10)` and a `Final diagnosis` list, because those are Medatrax fields. **So a run that copies the note's list passes C1 and C3 having coded nothing**, and the class is written to say so rather than to pretend otherwise. How far the answer key actually reaches was measured rather than assumed — [notes/README](notes/README.md) has the table, and the short version is that it does not reach C2.

A code is *added* when it is not in the note's lists. A code is *upgraded* when the run moves it from the note's `verify this number` to `verified against ICD-10-CM FY2026` — which it can only do honestly by running the lookup.

**That scope is C1 through C3's, and C4 and C5 are deliberately outside it.** The three above ask whether a code number is real, and a copied one is somebody else's answer. C4 and C5 ask about the **worksheet's own output** — the parts an entry carries, and what its specificity flag says — and an input note carries neither, because a Medatrax diagnosis field is a code and a descriptor with no anchor, no source and no flag beneath it. **There is nothing there to copy**, so the scoping sentence has no work to do on them and applying it would exempt the two rows the run cannot pass by transcription.

| # | Cases | Passes when | Fails when |
| --- | --- | --- | --- |
| C1 | all | Every added or upgraded ICD-10 code exists in `reference/icd10cm-2026.sqlite` | Any does not resolve |
| C2 | all | Its descriptor is the official string, verbatim | It is paraphrased, abbreviated, or belongs to a different code |
| C3 | all | It is billable, or is flagged `SPECIFICITY: needs: a billable child` | A header code is proposed as if submittable |
| C4 | all | Every code proposed **for entry** carries all five parts — number, descriptor, anchor, specificity, confidence — **and a sixth, `SOURCE`, where its anchor was filled**. A **differential** code carries three — number, descriptor, confidence — and `NOT FOR ENTRY` on its own line | A for-entry code is missing one of its five; a filled-anchored one is missing its `SOURCE`; a differential code is missing one of its three or its `NOT FOR ENTRY` mark |
| C5 | all | Every `SPECIFICITY` flag carries substance beyond its keyword — `complete — I10 has no further axis`, `needs: site` — **and** no code whose official descriptor contains `unspecified` or `not specified` reads `complete` | Any flag reads a bare `complete` or a bare `needs:`; **or** a code whose descriptor says `unspecified` is flagged `complete` |

**C1 through C3 are settled by one command**, which is why this class is enforced despite being new:

```bash
python tools/icd10_lookup.py <every added or upgraded code>
```

**C4 needs no tool and is still binary** — the parts are present or they are not. It is `icd10-cpt`'s own Completion rule, and it had nothing holding it to that.

**C5 is settled by one command too, and it is the third machine-decided row in this repo** — the CODE class is the first and day-b's B13 the second:

```bash
python tools/specificity_scan.py <the run directory>
```

It exits non-zero on either failure, prints counts and never a descriptor, and `--show` names the flags — which is PHI, because a code with its descriptor is a diagnosis attached to an encounter. [fixtures/README](../README.md) asks for exactly this where it is available: *"Where a row can be reduced to a command, reduce it"*, and what that buys is not speed but that **a second grader gets the same answer**.

**C5 is [#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56), and it exists because R2 could not be made to hold.** The skill's template read `SPECIFICITY: <complete | needs: ...>`, so a bare `complete` was compliant output that R2 nonetheless failed — a run could satisfy the skill in full and lose the row. #56 tightened the skill rather than loosening the row: `complete` now carries its reason, the way `needs:` already carried an axis. **The reason is the evidence that the check happened.** Nobody writes *"`Z98.51` has no further axis"* without having looked at `Z98.51`'s axes, and anybody can write `complete`.

**The second limb came out of the audit and is the sharper of the two.** #56 read the twelve notes' own diagnosis lists against `reference/icd10cm-2026.sqlite`: **106 distinct codes, all 106 resolving, and 23 carrying `unspecified` or `not specified` in their official descriptor** — `M19.90 Unspecified osteoarthritis, unspecified site`, `J01.90 Acute sinusitis, unspecified`, `E78.5 Hyperlipidemia, unspecified`. A flag calling one of those `complete` contradicts the line directly above it, and for most of them the flag has also **swallowed a step-4 bedside item**, which is R1's subject: a lipid panel for `E78.5`, a rapid strep for `J02.9`, the joint for `M19.90`, the duration for `R05.9`.

**Every one of those figures is pinned by `tools/test_specificity_scan.py` against the committed notes**, and that is not decoration. Run 1's output is gone, so this count is the whole of C5's evidence — and the first version of it **was wrong**, published as *52 distinct codes, 11 unspecified*. Six of the twelve notes bold the `Preexisting diagnoses (ICD10):` header and six do not; a matcher requiring the bold markers read half the set and reported a clean figure for it. **A count nothing recomputes is a count nobody notices going wrong**, which is this file's own standing complaint about denominators typed in prose, arriving on a number written to settle a ticket about exactly that.

**Two of the 23 are the row's known false positives, and they are recorded rather than smoothed.** `R00.1 Bradycardia, unspecified` and `R19.7 Diarrhea, unspecified` have no sibling naming a more specific form of the same condition — `R00.1`'s neighbors are tachycardia and palpitations, `R19.7`'s are abdominal swelling and bowel sounds. Nothing at the bedside moves either code, so **C5 fails a worksheet that got them right**, and on a binary row that costs the class. It is shipped that way because no mechanical test separates *the documentation is thin* from *the descriptor happens to contain the word*, and an exception list hand-written into a scanner is a worse thing than a known cost. [#135](https://github.com/mshamblin5150-code/clinical-skills/issues/135) holds it open; **weigh it before reading a C5 failure as a run defect.**

**Two more things the audit settled, and both stop a run getting the row wrong for the wrong reason.** **105 of the 106 are leaves**, so `needs: a billable child` has almost no subject here — and the one non-leaf is not a proposed code at all, but a header (`E11`) that a note's own aside discusses while proposing `E11.9`. And an `Other ...` residual is **not** an `unspecified` one: `R06.89 Other abnormalities of breathing` says the finding fits no named code, not that the documentation is thin, and it reads `complete` with a reason like anything else.

**C5 rests on C2 and would prove nothing without it.** The descriptor test is only checkable because C2 requires the **verbatim official string**; against a paraphrase, *does the descriptor say `unspecified`* is a question about the run's wording rather than about the code set. A run that failed C2 and passed C5 has not been graded on anything.

**It grew a second shape in [#19](https://github.com/mshamblin5150-code/clinical-skills/issues/19), and the count is what tells the two apart.** That ticket put a code on every differential entry, and those codes are documentation of medical decision-making rather than candidates for entry: three parts, in their own section, each line marked `NOT FOR ENTRY`. So the row can no longer read *"every proposed code has five"* — but it did not become a judgment call, because **the part count is exactly what distinguishes a code proposed for entry from one documenting reasoning.**

**It grew a third shape in [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46), and the count still discriminates.** A filled-anchored code carries `SOURCE` as a sixth part. So the gap is **five-or-six against three**, with nothing landing between, and neither shape may borrow from the other. The sixth part is not optional decoration on a five-part code: a `Z68.-` without it is a filled measurement presented as a recorded one, which is the defect the whole set exists for.

**These twelve inputs predate that rule.** Their Assessments carry differentials with no codes on them, because `clinical-note` did not require any when they were generated. A run over them today should therefore *produce* the differential section rather than pass one through, which is the harder half of the rule and the one worth watching on the first run.

**What CODE does not test.** The lookup *"answers does this code exist and what governs it, never is this the right code"*, in the skill's words. A run can propose a real, billable, correctly-described code for the wrong diagnosis and pass all four rows. That is a reader's judgment and it belongs in REPORTED — except that it does not move with wording either, which makes it the one thing this set would most like to enforce and cannot. Named under *Still unresolved*.

## REPORTED — counted, not enforced

| # | Cases | Claim |
| --- | --- | --- |
| R1 | all | Step 4's `UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE` block names at least one thing the clinician could document at the bedside next time |
| R2 | all | The reason beside `complete` is a **check on that code** rather than a stock phrase — `complete — Z98.51 has no further axis` rather than the same words on every code in the worksheet |

Counted on day-a's terms: *"a bar is only worth having if it was set deliberately"*. Both turn on judgment about usefulness and phrasing, which [fixtures/README](../README.md) puts in REPORTED however important it is.

**R2 is what was left of R2 after [#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56) took the enforceable half out**, and it is the clearest case in this repo of a row splitting rather than moving. It used to read *"specificity flags name the missing axis … rather than reading `complete` by default"*, which mixed two claims: that the flag says something at all, which is a string test and is now **C5**, and that what it says was arrived at by looking, which is not.

**No string test reaches the second one, and the audit is why.** `L85.3` has five siblings and `Z98.51` has one. Ruling that those are different conditions rather than axes of one thing takes a reader — so `complete — L85.3 has no further axis` is **true**, and a scanner confirming it would be confirming that words are present. That is [fixtures/README](../README.md)'s line exactly: *"a row turning on how well something is phrased cannot [be binary], and belongs in REPORTED however important it is."*

**It is counted for phrasing, so it is not promotable**, unlike a row counted for want of a run. That distinction is [#29](https://github.com/mshamblin5150-code/clinical-skills/issues/29)'s and the set says which kind each of its counted rows is.

**Run 1 held R1, and R2's run-1 verdict is withdrawn** — see *Status*.

**Run 2 holds R2, and what settled it is a test no single worksheet permits.** 132 `complete` flags
across 90 distinct codes, and **24 of those codes carry a flag in more than one worksheet — 62
flags, of which 61 reasons are distinct.** The one collision is `I10 has no further axis` on cases
2 and 9. `E66.3` appears in six worksheets with six different reasons; `R20.2` in two, each naming
the inclusion term matching its own note. **Twelve passes that could not see each other's text did
not converge on a sentence**, which is the strongest evidence available that the reasons were
arrived at by looking — and it is only visible across a run, exactly the way
[#67](https://github.com/mshamblin5150-code/clinical-skills/issues/67)'s defect was.

**Four flags in 132 were graded stock, and all four are wordings this repo publishes as
compliant** — `complete — I10 has no further axis` is [icd10-cpt](../../skills/icd10-cpt/SKILL.md)'s
own example and `complete — Z98.51 has no further axis` is R2's. The grader docked them on what was
added beyond the published formula and said so; a reader taking the exemplars at face value scores
132 of 132. **The row is counted rather than enforced precisely so that disagreement is recordable
instead of fatal**, and this is the first run where it has actually been exercised.

**The grading turned up a defect neither R2 nor C5 asks about, and it is recorded here rather than
made to fit a row.** Four `complete` reasons are **specific, checkable and wrong about the code
set** — a claim that `Z90.4` names the stomach, which is `Z90.3`; a claim that `Z88.1` is a named
class when its own descriptor above it reads *other antibiotic agents*; a `Z88` range enumeration
that skips a code and misplaces another. **C5 cannot see these** — it tests that substance is
present, and substance is present. **R2 cannot fail them** — they are real checks rather than stock
phrases, which is the only thing R2 asks. And **the run contradicts itself on two of them**, giving
`Z90.49` and `Z88.1` correct readings in one worksheet and wrong ones in another, which is again a
thing no single worksheet shows. Filed as
[#154](https://github.com/mshamblin5150-code/clinical-skills/issues/154).

## Still unresolved

- **A3 and A4 are answer-keyed in the direction they assert, and a copying run passes both for free.** This was raised in review and it is a real limit rather than a defect to argue away. A3 wants `Z68.25` on case 4 — the note already lists it. A4 wants `I10` on cases 2, 3, 8 and 9 — all four notes already carry it. So a run that transcribes every input list clears both rows.

  **What they still discriminate is the other failure**, and it is the one #10 actually predicted: a run that applies the filled-anchor rule *too widely* and stops coding the family altogether. That run passes A1, A2 and A5 and fails A3 and A4, which is the whole reason A3 exists. **What no row in this set can catch is a run that copies.** ANCHOR catches copying only where the input is wrong — case 1, one case in twelve — and the other eleven inputs are right, so copying them is indistinguishable from coding them. Closing it needs an input whose *correct* codes are absent, which none of these twelve is.

  **Run 1 measured how large that hole is, and #19 shrank it without closing it.** Of 137 ICD-10 codes proposed **for entry** across the twelve worksheets, **134 already appeared in the input note's own lists and 3 did not** — `R20.2` on case 5, `R06.89` on cases 9 and 10. So 97% of the for-entry half is indistinguishable from a transcription, and every ANCHOR row passed anyway.

  **The differential half is where the run has to produce something.** Of its 114 codes, **68 appear nowhere in the input note** — because these twelve predate the rule, so a run has to derive the differential codes rather than lift them. That is a real discrimination the set did not have before #19, and it is why the copying figure is a for-entry figure rather than a whole-run one.

  **It is a *CODE*-class discrimination, not an ANCHOR one**, and that limits what it buys: a run that invents a plausible but wrong differential code passes C1 through C4 exactly as a right one does, because the lookup answers *does this code exist* and never *is this the right code*. **The copying hole is narrower and it is still open.**
- **A3 was not worded as a string test, and [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) made one available.** Run 1's case-4 worksheet said in prose, inside the old `NOT CODED, ANCHOR WAS FILLED` block, that `Z68.25` was proposed *rather than* routed there — so a substring search for `Z68.25` in that block reported a routing that had not happened, and a grader had to read the sentence. **The rewritten fail condition resolves mechanically**: does the code carry a `SOURCE` line, and does it appear under `CODED, ANCHOR WAS FILLED`. Both are string tests over `icd10-cpt`'s own format, and a run may not narrate its way past either. This is what A2 got by rewording; A3 now has it for the opposite reason — its *fail* condition became mechanical rather than its pass.

  **The prose hazard has not gone away, it has moved.** A run can still write *"`Z68.25` needs no `SOURCE` line, the inputs were given"* **inside** the step-4 block, which puts both strings in the same place the fail condition looks. A grader tests for the block's own line format — `<code> — <value>` — not for the code number appearing anywhere in the section.

  **Run 2 wrote it, on the first run after this paragraph was written down.** Case 4's step-4 filled block reads `None.` and then a sentence naming both `E66.3` and `Z68.25` inside the block, explaining that they are proposed unmarked because the inputs were given. **The routing is correct and a substring search reports two codes routed there.** `tools/anchor_scan.py` reads the line format and reports none, which is why it was built that way rather than as a substring test — and it is why the tool reports case 4 as **not having been scanned** rather than as clean, since a case with nothing marked and nothing listed has nothing for this row to grade. **A predicted hazard arriving unprompted is the strongest evidence available that the prediction was worth writing**, and it cost nothing because the grader was written from the prediction rather than from the run.
- ~~**R2 asks for more than `icd10-cpt`'s own template requires.**~~ **Settled by [#56](https://github.com/mshamblin5150-code/clinical-skills/issues/56) on 2026-08-15, and the exit was the one that made the row stricter.** The skill's step 3 wrote `SPECIFICITY: <complete | needs: ...>`, so a bare `complete` was compliant output that R2 failed — a run could satisfy the skill and lose the row, which is what run 1 did once in the 150 codes it proposed for entry. The two exits were *require a reason beside `complete`* and *stop R2 asking about `complete`*, and the second would have made the row weaker in exactly the direction that lets a lazy run through. **The skill was tightened.** `complete` carries its reason, the enforceable half of R2 became **C5**, and R2 keeps the judgment half.

  **The audit that settled it found something nobody had asked about**, which is the part worth keeping here. Reading all **106** codes in the twelve notes against `reference/icd10cm-2026.sqlite` turned up **23 whose own official descriptor says `unspecified`** — a code set's own statement that an axis exists and this code declines to name it. A `complete` flag on one of those was permitted by the old template, permitted by R2 as it stood, and **swallows a step-4 bedside item**, which is R1's subject. The second limb of C5 exists because of that and not because #56 asked for it.

  **It also retired the ticket's own leading argument, and the correction is worth keeping.** #56 opened with *"66 of 67 `complete` flags carry a reason"* — corrected in its first comment to **65 of 66**, which is the figure this file has always carried — and read it as evidence that the cost was already being paid voluntarily. It is still the record of what run 1 did. But the worksheets are gone, so it cannot be re-derived, and **C5 rests on the committed inputs instead**, pinned by a test. **A figure that can only be cited is a weaker thing than one that can be recomputed** — a standard the first draft of that replacement audit promptly failed, publishing *52 distinct codes* for a set of 106 because it read only the six notes that bold their header. Both halves of that lesson are the same lesson.
- **The `E66.-` control is owed.** A4 covers the diagnosis-survives-filled-vitals claim on `I10` only. Its obesity instance needs `obesity-bmi` cases 1 and 2 run through `clinical-note` first, at which point this set can span two sources on [fixtures/README](../README.md)'s terms.
- **CODE cannot ask whether a code is *right*.** C1 through C3 verify existence, descriptor and billability; nothing in the database encodes the coding guidelines and there is no alphabetic index, so a plausible code for the wrong diagnosis passes. It does not move with wording, so it is not a REPORTED row by rights — it is a row this set would enforce if the reference material existed.
- ~~**A2's failure is a `clinical-note` defect, and this set only taxes it downstream.**~~ **Settled by [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46), and it inverted which case was wrong.** This bullet used to read that case 1 laundered a filled height into a Medatrax diagnosis field while six siblings held the family back, and that A2 could only make it visible downstream. #46 ruled the other way: the note codes it, the worksheet codes it, and both mark it. **Case 1 is the compliant case and the six refusals are the deviation.** What made the old arrangement untenable was not which behavior was right but that the two skills disagreed about one number with nothing telling the clinician which to believe.

  **What the ticket did not fix, and deliberately.** The `5'10"` under case 1's `Z68.26` is still a template value rather than a reasoned one — that is [#67](https://github.com/mshamblin5150-code/clinical-skills/issues/67), and marking a code does not improve the height beneath it. And the pediatric band stays **recalled** rather than looked up until [#123](https://github.com/mshamblin5150-code/clinical-skills/issues/123) ships the CDC growth charts, so cases 6 and 12 carry a disclosure with two limbs where the adults carry one.
- **The inputs are a graded run now, and it failed a row.** This bullet used to say day-b's own counts were unset. They are not — day-b ran on 2026-08-11 and **did not clear its FILLED bar**, with part of the set ungraded because rows landed while the run was in flight ([#26](https://github.com/mshamblin5150-code/clinical-skills/issues/26) closed it; [#55](https://github.com/mshamblin5150-code/clinical-skills/issues/55) carries the remainder). **The counts and which rows they cover live in [day-b/assertions.md](../day-b/assertions.md) and are deliberately not restated here** — they have moved twice already, and a copy of them in this file is a second place to keep true.

  What matters here is only the consequence: **these twelve notes are known-real, known-incompletely-graded, and known-wrong in at least one place.** That is a sharper reason than "unscored" for the standing rule that a row here must never be read as endorsing the note it quotes.
- **These twelve notes write the banned allergy hedge and no row here noticed for four days.** **The set carries the class 18 times across six files** — 1, 7 and 4 in `notes/` cases 2, 7 and 11, and 1, 3 and 2 in the matching `run-2/` worksheets, where `icd10-cpt` quotes the notes verbatim as `ANCHOR` strings. Re-derived 2026-08-16 with `grep -oi "reaction[^.]\{0,40\}not documented"`.

  **This bullet published two wrong figures before that one, and both were wrong the same way.** It first said *six times and once*, then *12 across four files*. Both came from `grep -c` on the literal `reaction not documented` — which **counts lines rather than occurrences** and matches one phrasing of five. `case-11` writes two on a single line; `case-07` capitalizes one; `case-02` writes `reaction pattern not documented` and was **missing from both counts entirely**, so the set carries the class in **three** notes and this bullet twice said two. Caught in the tracker sweep on the second pass, having survived the first. **The instrument was the defect both times**, which is why the figure above is stated with the command that produces it. This set is day-b run 1 byte for byte and has been cited for its British spellings and its filled vitals; **nobody read its allergy line**, and the string was found by [#94](https://github.com/mshamblin5150-code/clinical-skills/issues/94)'s tracker sweep rather than by any row. That is the standing rule at the top of this section arriving with an instance: *a row here must never be read as endorsing the note it quotes*, and the notes were carrying a drift-row-12 violation the whole time.

  **The finding is recorded and the notes are not edited.** [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md)'s terms: this set is a preserved run record, `spelling_scan.py` already exempts it by path for exactly this reason, and tidying the hedge away would destroy the evidence that three independent runs hit the same wall — which is the whole of #94's *a rule with no exit* argument. **The rule now has an exit** and `day-b`'s R6 grades it; **run-2's worksheets quote the hedge in their `ANCHOR` strings**, so those stop matching a re-run's input, which is a second reason to rule on the rule and leave both run records alone.
- **Nothing here tests CPT.** The skill proposes procedure codes and an E/M supporting-element list, and day-b's shift contains at least one procedure — case 1's incision and drainage. C1 through C4 are worded to cover a CPT entry if one is proposed, but no row *requires* one, so the CPT half is conditional by construction on this shift.
