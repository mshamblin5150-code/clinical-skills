# A topic is swept on what the guideline states, and the sweep records its own coverage

[#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429) asked how to sweep
the corpus into threshold sheets now that [#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223)'s
copyright bound is ruled away and [ADR 0007](0007-a-threshold-sheet-is-drafted-per-topic-and-its-snippets-are-gated-against-the-record.md)
has settled that a sheet is drafted per topic and gated against the record. It carried three
decisions. Grilling it on 2026-08-22 found that all three rest on one term the repo uses
constantly and had defined without defending — *the topic has decision points* — and that
`CONTEXT.md` had already answered it in a way the ticket's own decision 1 was arguing against.

The clinician ruled, 2026-08-22:

1. **A topic has a decision point when the guideline states a number that changes what is
   done to a patient** — a dose, a period, a cutoff, a target — **read off what the guideline
   states and never off an index derived from it.**
2. **The document is the population and the recommendation records are an index into it.**
   The draft reports what it read and what it did not, on `CLAUDE.md`'s extractor-coverage
   rule.
3. **The sweep records its own coverage** in `reference/thresholds/coverage.md`, one row per
   topic, whose topic column is derived from `reference/guidelines-catalog.md` rather than
   typed. Its **sweep state** is one of `sheet`, `none`, `unread`.
4. **Where one guideline states several values for one quantity depending on the method
   chosen, the method belongs in the quantity key**, and quantity keys gain a `## Quantities`
   declaration block on the same terms as `## Populations`.
5. **The 47 `bound`-only topics are held at `unread`**, blocked on
   [#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436).

## What was measured

**Decision 1's stated reason is false, and the counter-example is a row that looks empty.**
#429 reasoned that the 90 USPSTF documents want no sheets because *a screening grade is not a
threshold*. That is true of a grade. `reference/guidelines-uspstf.md`'s row for
`aspirin-preeclampsia-prevention-final-rec.pdf` reads population *"persons who are at high
risk for preeclampsia"*, grade B, interval `not stated` — no number anywhere. Its statement,
in the same committed file, is *"the use of low-dose aspirin (81 mg/d) as preventive
medication for preeclampsia after 12 weeks of gestation."* Two numbers, and neither is
representable: **the Recommendations table's five columns are Topic, Population, Grade,
Interval, Year, and there is no dose column at all.** Counted over all 143 statements in that
file, **4 statements across 3 documents name a dose in the recommendation sentence** — a
floor, since it does not catch a dose written in words.

So decision-point presence cannot be read off that table, which is what ruling 1 generalizes.
The two figures that look like they would answer it — 12 rows carrying an interval, 36 of the
90 topics carrying a digit in the population cell — both miss this row.

**`CONTEXT.md` had already located the test correctly.** Its **Decision point** entry read
*"A quantity a guideline attaches a value to, which a clinician acts on... A recommendation
carrying no such quantity has none"* — on the recommendation, not on an index of it. #429's
decision 1 was arguing against the repo's own glossary rather than filling a gap. The entry is
sharpened rather than replaced.

**The topics partition cleanly by source mode, and no topic mixes them.** 169 distinct topic
cells: **104 `exact` only, 47 `bound` only, 18 nothing found.** Of the 9 topics carrying more
than one document — the only ones that can exercise `CONFLICT` and per-source `COVERAGE`,
neither of which has ever run — **8 are `exact` and one, `sepsis and septic shock`, is
`bound`.** (USPSTF and AHA/ACC modes are taken from `reference/thresholds/README.md`'s table
rather than re-run, so one AHA/ACC document is filed here as `exact` that is not.)

**The `bound` records cannot carry the test.** #436 measured it across all 48 `bound`
documents; the two facts this decision turns on are that no document has a record longer than
160 characters and that almost none ends in a sentence terminator. **Those figures are #436's
to state and are deliberately not restated here** — they were counted against source PDFs
outside every checkout, and one such figure copied into a second file is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143).

## Considered options

**Exclude the 90 USPSTF documents wholesale, and let `reference/guidelines-uspstf.md` stand
as their artifact.** #429's own decision 1, and the option a future reader will most want
explained. Rejected on the preeclampsia row: a rule that sorts by society excludes both the
one topic in the corpus that exercises `CONFLICT` from inside a single document — cervical
cancer's three screening arms — and every topic whose number the table has no column for.
What sorts is whether the topic has a decision point, which is the ticket's own stated unit.

**Apply the decision-point test to the recommendation records.** The intuitive answer, and
what `tools/threshold_draft.py` does today: it joins the catalog on topic, globs
`recs-*.json`, and its candidate set is whatever those hold. Rejected because it derives the
population **from** the extraction, which is the one arrangement `CLAUDE.md`'s
extractor-coverage rule refuses in as many words — and #436 is what that looks like when it
goes wrong, a partial read presenting as a whole one with a tidy count attached.

**Record the sweep's coverage as a column on `reference/guidelines-catalog.md`.** No second
file, and that file already has the discipline wanted — 43 cells read `?` and every one is
named at the bottom with why. Rejected on the unit: catalog rows are documents and the
sweep's unit is the topic, so the 9 multi-document topics would carry the verdict three times
over and the copies can disagree. The registry pays the cost the catalog would have avoided —
a reworded topic cell orphans a row — and pays it with a test asserting the two topic sets are
equal in both directions.

**Let a topic with no decision point be recorded by a command rather than in a file.** The
cheapest option and it fails #429's own Done-when: a command can see that a topic has no
sheet and cannot see whether anyone looked. That is the silence the ticket refuses, restated
as a feature.

**Write cervical's three arms as three rows and let `CONFLICT` fire**, with prose saying they
are alternatives. Rejected because it costs the block its meaning. `CONFLICT` today says *the
guidelines disagree and here is why*; the README's own justification for prose over a column
is the KDIGO-versus-AHA case, which **is** a disagreement. A block that also means *here is a
menu* cannot be read either way, which is
[#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85)'s erosion one level
down.

**Put the modality in the `population` cell.** Not a guess — the document states it. Rejected
because `population` is what decides whether a threshold applies to **the patient**, and
`CONFLICT`'s whole discrimination rests on that column meaning *who* rather than *which test
was chosen*. It is also the column this repo has twice ruled must never be filled on
inference.

**A ninth column for modality.** The most honest shape and the most expensive: eight columns
become nine, both shipped sheets move, and every gate and parser moves with them. Rejected as
larger than the `## Quantities` block, which buys the same legibility and generalizes to every
sheet rather than to this one case.

**Sweep the 47 `bound` topics now, on `diabetes.md`'s precedent.** Rejected on ADR 0007's own
argument: that ADR rejected freehand authoring because it *"makes a language model retype the
snippet, which is the one cell that exists to be un-retypeable."* Shipping 47 topics whose
snippets tier 0 reports `NOT RUN` on is that rejected option at scale, and it would land while
#436 describes the cause. `diabetes.md` is one sheet and 12 of its 23 gated rows fail tier 0
today.

## The order this sets

1. **Cervical cancer.** One document, and it is what forces the `## Quantities` block. Moving
   the format before 160 sheets exist is cheap and moving it after is not.
2. **The 8 `exact` multi-document topics.** The first run `CONFLICT` and per-source
   `COVERAGE` have ever had, fully gated while they have it.
3. **The remaining `exact` topics**, every sheet tier-0 gated.
4. **The 18 nothing-found topics**, read and recorded `none` or `unread` as the read decides.
5. **The 47 `bound` topics and `sepsis and septic shock`**, `unread`, on #436.

## The cost this accepts

**The registry can go stale against the catalog, and only a test says so.** Its topic column
is derived rather than typed, so a reworded catalog cell fails the suite. Nothing checks that
a `none` was reached by reading anything — the `read` column names documents and pages, and a
row can name them without them having been opened. **A recorded `none` is a claim about a
read, not evidence of one.**

**A quantity key is now load-bearing and was free text.** Declaring it in `## Quantities`
with the guideline's verbatim wording is what makes a mis-keyed row *a wrong word a reader can
see rather than a silent miss* — the README's stated reason for declaring populations, applied
to the column it was never applied to. The gate is a floor: it can check that the key is
declared and that the wording is verbatim, and cannot check that the row's number belongs
under that key.

**#85 survives and gains a denominator rather than being re-ruled.** #429 asked whether *sheet
does not settle it* survives a comprehensive directory. Today an absent sheet means one thing —
nobody looked. After a sweep it would mean two at once, which is how silence starts reading as
a finding. `none` and `unread` split them: `none` is close to a negative finding and a reader
may lean on it, `unread` establishes nothing, and inside a sheet a missing row is still *sheet
does not settle it*, unchanged.

**47 of 169 topics are unswept for as long as #436 is open**, and the registry is what keeps
that a recorded state rather than an absence.

**`skills/clinical-note/SKILL.md`, `AGENTS.md` and `tools/test_guideline_sheets.py` say
`two topics`, not `one topic`.** #429's Done-when names the older figure and a line number
that has since moved. Every sheet this sweep adds makes that string false, which is the pin
working.
