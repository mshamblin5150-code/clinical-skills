# A pass may grammar-check its own note and a prior run is a record not a template

**Measured at:** ebd72f7777493c6b26709fd5a5fa29d1e24f147a

[#1596](https://github.com/mshamblin5150-code/clinical-skills/issues/1596) was filed from the
after-action review of a `batch-shift` run on a NUR5144 clinic shift, 2026-10-07, and gathered
proposed diffs from the reviews of the next two shifts, a clinic shift and then an ED shift. It
proposed that `skills/batch-shift/SKILL.md` step 1 take the shift constants from the profile and
that step 5 give every note pass a checklist to run on its own note before handing it back. The
clinician ruled every point below on 2026-10-16. The record was re-measured against `main` at the
commit above, after ADRs 0375 to 0378 landed, where the freshness gate read `FRESH`. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The touched-run premise is retired.** The 2026-10-07 incident was an orchestrator reading a prior
shift's fill record to learn the course, site and preceptor, after which every reply owed that
run's keyed status line. [#1519](https://github.com/mshamblin5150-code/clinical-skills/issues/1519)
has since changed `run_status_stop_hook.touched_runs`: a run is touched only when a tool call names
it and a file beneath it changed after session start. A read alone no longer binds the sitting.

**What the remaining gap is.** Step 1 says the preceptor mapping lives in
`scratch/medatrax-profile.md`. Nothing says where Course, Site, or Interaction Level come from;
`reference/medatrax-fields.md` lists all three as `given`, so the orchestrator went to the nearest
record that held them.

**Most checklist lines are already enforced.** An argued-down differential's code and a
history-only condition on the for-entry list are both read by the Writer self-grade that step 5's
brief already names, through `anchor_scan.AGREEMENT_READER_INSTRUCTIONS`. `skills/icd10-cpt/SKILL.md`
already requires `ANCHOR` on every refusal row, and `anchor_scan --agreement-read` counts a refusal
without one as unread. The proposed differential wording went further than current rules: icd10-cpt
codes a differential the findings argue against at its own unspecified level and marks it not for
entry.

**One line reverses a ruling.** The proposed self-run of `entry_copy.py --check` is what
[ADR 0300](0300-the-entry-copy-refusals-run-before-the-go-ahead-and-a-changed-note-needs-a-new-word.md)
ruling 1 placed outside the writing pass, by `AGENTS.md` standing rule 6's rule that authors do not
check their own generated artifacts. The cost the ED shift's review recorded is that two grammar
refusals surfaced only after placement, so each fix became a repair-chain record, the chain where
#1804 and #1815 recorded permanent broken-chain findings on correct content.

**The MDM Data line already has its rule.** icd10-cpt step 5's *Orders and provenance* counts the
clinician's own ordered, resulted, or reviewed tests and skill-proposed tests written as actual Plan
orders, with the data-dependency mark, and never a recommendation left for the preceptor
([ADR 0292](0292-directed-otc-agents-are-drug-management-and-modifier-25-joins-the-committed-cpt-sheet.md)
ruling 7). The proposed "tests the clinician ordered" wording would remove the second half.

**`entry_copy.py --check` is not inert.** Batch-shift step 7 says the check "writes nothing". On a
refused-code grammar failure it deletes any prior derived copy at the destination, as
[ADR 0307](0307-a-refused-code-clause-opens-its-own-sentence-and-its-semicolon-only-joins-two-clauses.md)
ruled. Before placement no derived copy exists, so the deletion is harmless at the moment ruling 1
places the check.

**A proposed test may land on the results line.** `skills/clinical-note/SKILL.md` drift row 21 names
the results line among the places a `FILLED·proposed` item lands, and its order rule writes a test
the Plan names on the results line as ordered. The later clinic shift's defect was therefore not a proposed
test in Objective: a repair pass applying one clinician answer turned a recommendation into an order
that answer never gave, which raised the Data element a level.

## Ruling 1 — a pass may run the entry-copy check on its own note

A note pass may run `python tools/entry_copy.py --check <run>/note-N.md` on its own note before
handing it back, and corrects any refusal before hand-back. This is a second narrow author exception
in `AGENTS.md` standing rule 6, beside the Writer self-grade. The orchestrating context's
check over every note before the Review sheet, run by a non-authoring context as a **Grader
handoff**, is unchanged and still required; the author's run never substitutes for it. Batch-shift
step 7's "This check writes nothing" is corrected to say that it writes no copy and deletes a prior
derived copy on a refused-code grammar failure.

Keeping rule 6 unchanged was declined because a grammar refusal is cheap before placement and a
permanent repair-chain record after it. Adopting the full checklist was declined because it would
overturn "authors do not check their own work" for clinical judgment to buy coverage the self-grade
already gives. The check is mechanical form, a semicolon or a short Plan line, which is why the
rewording risk #1812 records is small here. [ADR 0375](0375-a-subagent-launch-hook-refuses-a-patient-work-brief-that-names-temp-or-no-existing-staging-folder.md) ruling 6 declined a different second exception,
a writer's identifier self-scan, because a writer searching for the source spelling does not find its
own guessed one; a grammar check has no such blind spot, since the tool reads the note it was given.

## Ruling 2 — step 1 names the source of each shift constant

Course and Site come from the profile; where the shift is already in Medatrax, its record wins for
Site, as step 1 already says for Preceptor. Interaction Level comes from the profile's saved account
default; `reference/medatrax-fields.md` names the scale and not an answer. A value the profile does
not hold is asked once and saved to the profile. A prior run is never the source, because it
records what applied then and a new term or site makes it wrong silently. The touched-run reason is
not carried into the skill.

Dropping the item was declined because the gap that sent the orchestrator to a prior run still
stands. A grader comparing the Review sheet's constants line with the profile was declined because
the clinician reads that line before approving.

## Ruling 3 — a prior run is a record, not a template

`AGENTS.md` standing rule 6 gains one sentence for every skill whose orchestrator writes briefs:
each pass brief is built from the current skill, standing rules and memory, never adapted from an
earlier run's brief; and a format example handed to a pass is the skill's own worked example, never
a prior run's note, worksheet, or other output. `skills/batch-shift/SKILL.md` already points at rule
6 and copies nothing.

Reuse after a walk against a named list was declined because that list is a second copy of rules
held elsewhere, and reuse failed on both later shifts, one day apart. [ADR 0375](0375-a-subagent-launch-hook-refuses-a-patient-work-brief-that-names-temp-or-no-existing-staging-folder.md), ruled the same
day on [#1593](https://github.com/mshamblin5150-code/clinical-skills/issues/1593), catches a reused
brief mechanically only through its staging route: its launch hook refuses a temp or scratchpad
location and a named staging folder that no longer exists. That ADR declined a prose line asking the
orchestrator to confirm a brief's paths, because the hook reaches paths. This sentence covers what
the hook cannot read: a reused brief's Times line, result handling, placement step, and format
examples, which carried the other defects the ED shift's review recorded.

## Ruling 4 — no pass turns a recommendation into an order without the clinician's words

No pass, first draft or repair, turns a test, drug, or referral the note recommends into an order,
given or ordered, unless the clinician's own words say so. ADR 0292 ruling 7 stands: a skill-proposed
test written as an actual Plan order still counts toward Data with its mark, and still lands on the
results line as ordered under drift row 21. The proposed restriction of the Data line to the
clinician's own orders is not adopted.

A blanket "never enters Objective" was confirmed first and withdrawn on measurement, because it
contradicts drift row 21's results-line landing and the order rule beside it. Adopting the
clinician-only Data wording was declined because it lowers E/M levels to fix a defect it does not
reach.

## Ruling 5 — a reported count of proposed items named in Objective

`tools/differential_scan.py`, which already reads the run's physical `FILLED·proposed` openers for
row 24, reports how many proposed items share a name with text in the note's Objective section and
lists each pair under `--show`. The count never changes the exit status. Batch-shift's second
reader rules on each one in the drift row 21 walk: a proposed test the Plan writes as an actual order
is allowed, and a recommendation that reached Objective as given or ordered is a defect.

A graded row was declined because a prior given result can share a proposed test's name, and a
matcher a pass satisfies by rewording is #1812's shape. No check was declined because the later
clinic shift's defect was caught only by comparing a repair with the clinician's answers.

## Ruling 6 — the refusal template carries its anchor

The `NOT CODED, NOTHING ESTABLISHED IT` template in `skills/icd10-cpt/SKILL.md` step 4, and every
worked refusal example beneath it, gains
`ANCHOR: "<the code-and-descriptor half of the note's welded NOT CODED: clause>"` directly under the
`NOT CODED:` line, matching the anchor rule the skill already states and `anchor_scan` already
enforces.

## Ruling 7 — the remaining proposed lines are not adopted

The checklist lines for argued-down differentials, history-only codes, and anchors on every row are
not added to the batch-shift brief: the Writer self-grade the brief names already reads them. The
MDM Data line wording is not adopted, by ruling 4.

## Supersedes

- [ADR 0300](0300-the-entry-copy-refusals-run-before-the-go-ahead-and-a-changed-note-needs-a-new-word.md) ruling 1,
  its words "The writing pass never runs it on its own output". Ruling 1 here lets a pass run the
  check-only mode on its own note before hand-back; the orchestrating context's non-authoring run
  before the Review sheet survives unchanged.

## What this does not reach

Ruling 1's author run is a convenience and not a check: the independent run is what grades. Ruling 2
names a source and does not verify that the profile's values are current. Ruling 3 is a written rule
with no mechanical check that a brief was built fresh; ADR 0375's launch hook reaches only the
staging route a brief names. Ruling 4 does not rule whether a blanket delegation, such as "do whatever you think is correct",
counts as the clinician's words for a promotion. Ruling 5's count reaches names written alike; a proposed test written with a
different name in Objective is invisible to it, and whether a matched pair is a promotion stays the
reader's judgment.

## Build checklist

- `AGENTS.md` standing rule 6: the entry-copy author exception (ruling 1) and the prior-run sentence
  (ruling 3).
- `skills/batch-shift/SKILL.md` step 1: the shift-constant sources (ruling 2); step 7: the
  entry-copy author exception and the corrected "writes nothing" sentence (ruling 1).
- `skills/clinical-note/SKILL.md` and `skills/batch-shift/SKILL.md`: the promotion limit (ruling 4),
  in the clinical-note proposal rules that batch passes inherit.
- `tools/differential_scan.py`: the never-graded Objective candidate count (ruling 5), with tests
  pinning that it never changes the exit status.
- `skills/icd10-cpt/SKILL.md` step 4: the refusal template and examples (ruling 6).
