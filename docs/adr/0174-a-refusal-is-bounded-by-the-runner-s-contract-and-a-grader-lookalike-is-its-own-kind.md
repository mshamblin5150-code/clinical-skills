# A refusal is bounded by the runner's contract and a grader lookalike is its own kind

Found while grilling [#1006](https://github.com/mshamblin5150-code/clinical-skills/issues/1006),
2026-09-11, at `origin/main` `c58de26`, freshness gate `FRESH` before reading. **Ruled by the
clinician on that date, one question at a time.** Nothing is built here; this is the record the
build reads.

## Measured before ruling, at `c58de26`

### The three refusals do not share a ground

`run_grader.REFUSED` names three modules, and their reasons are about different things.

- **`corpus_census`** is refused as *"a census over the corpus, not a grader over a run"*. That is a
  statement about what the module is. The membership walk sees it because it carries a top-level
  `survey`, a top-level `format_report` and a `__main__` guard, and no change to the runner turns a
  census into a grader over a run.
- **`threshold_sheet`**'s two grounds are properties of the runner. `run_grader.run` prints
  `format_report` unconditionally, and `run_grader.parse` gives `Parsed` a single `source`, the first
  positional.
- **`tracker_bodies`**'s recorded reason names only the module's side, and its command meets the
  runner in three places:
  1. `run_grader.run` calls `format_report` with `show=`, and `tracker_bodies.format_report` takes no
     `show` by design.
  2. It grades several harvest files as one population, and `Parsed` carries one source even where a
     grader sets `allow_extra_positionals=True`.
  3. `--github-event` grades an event payload and takes no positional, which `run_grader.parse`
     refuses before `load` is reached.

  Only the first is recorded.

### The deferral side is empty

`run_grader.DEFERRED` is an empty mapping. ADR 0112 ruling 2's present-tense sentence naming
`filled_vitals_census` as a deferral is false of the tree, which carries it in `MEMBERS`, so ruling
3's distinction currently has no instance on the deferral side.

### The suite already refuses a move into `MEMBERS` until the family's obligations are met

Driven in process rather than read: with `threshold_sheet` added to `run_grader.MEMBERS` and removed
from `REFUSED`, `test_run_grader` goes from clean to three failures and two errors — the adoption
walk, the empty-population posture declaration, the undecodable-byte posture declaration and its AST
evidence check, and the refusal-specific test losing its key. *Had joining cost nothing, that run
would have been green; it was not.*

### Nothing keeps the verdict mappings apart

`test_run_grader` asserts that the walk population equals the union of `MEMBERS`, `REFUSED` and
`DEFERRED`, and asserts nothing about overlap. No module sits in two of them today. A name added to a
second mapping without leaving the first keeps the union equal and the suite green.

### Two candidate names were taken

*Non-grader* already carries two senses: ADR 0119 uses it for modules outside the family that the
walk does not see, and `run_grader.EarlyExit`'s docstring uses it for a member's declared
non-grading mode. `Corpus`, `Scan`, `Declared` and `Refusal` are single-word glossary headings, so a
heading containing any of them fires `test_glossary_collisions` and waits on a human verdict.

## Ruled 2026-09-11

### 1. The three refusals are two kinds

`threshold_sheet` and `tracker_bodies` are graders the shared runner cannot express under its
current contract. `corpus_census` is not a grader. This answers #1006 decision 3, and it is a finding
about the vocabulary rather than about any module.

### 2. A refusal is a verdict against the runner's current contract, and "permanent" is dropped

A refusal has no owner, nothing schedules it, and it reopens only on evidence that the runner's
contract changed. This answers decision 1.

**What ADR 0112 ruling 3 protects survives on a different word.** A refusal is a decision and a
deferral is a queue; that difference now rests on *no owner, no queue*, and no longer on permanence,
which was false of both modules the kind holds.

### 3. A grader lookalike is recorded in its own mapping

`run_grader.GRADER_LOOKALIKES` holds the modules the membership walk recognizes by source shape that
are not graders over a run, each with what it is instead. `corpus_census` moves there from
`REFUSED`. The ledger test's union gains the mapping, and its reasons must be non-empty.

**It is a declaration and not structure in the runner.** #1006's must-not line attributed a ban on
*structure added to `run_grader`* to ADR 0112 ruling 4. That ruling forecloses a structural redaction
gate inside `run_grader.run`. Declaration mappings have sat beside `MEMBERS` since
`UNDECODABLE_BYTE_POSTURES` arrived in `0636c26`, and ADR 0170 ruling 2 adds another on those terms,
so the must-not narrows to what the cited ruling says.

**The ticket's warning against a third mapping does not reach this one.** It was written against a
mapping for `threshold_sheet`'s conditional state, which ruling 2 declines.

### 4. The term is **Grader lookalike**

Not *non-grader*, which already has two senses, and not *shape match*, since every declared member
also matches the shape. `CONTEXT.md` carries the entry, and its **Refusal** entry is rewritten to
ruling 2.

### 5. A `REFUSED` value names the runner feature it lacks, and carries no reopening clause

This answers decision 2. Under ruling 2 the missing feature is the reopening condition, so naming it
is enough; a *reopens when* clause in every entry would be a second copy of the definition that an
edit to either copy never fails.

The test that `threshold_sheet`'s reason names both mismatches generalizes to every value naming the
shared runner's side. **It is a floor**: it proves the runner's side is named, never that the
sentence is true.

### 6. `tracker_bodies`'s value names two obstacles, and the third is recorded as unruled

The value names the runner passing `show` to a report that takes no show flag because it is safe to
paste, and the runner carrying one positional source to a harvest mode that grades several files as
one population. Both sit on the graded path.

**The `--github-event` mode is not named.** ADR 0117 ruling 2 kept `aar_scan`'s positional-free
`--session-end` in `main` beside the delegation, and ADR 0117 ruling 6 records that that mode is not a
reader in the grader family. Whether the arrangement reaches a mode that does grade is unruled, so
writing it into a `REFUSED` value would assert a kind nobody has decided — ADR 0112 ruling 3's
misclassification arriving from the other direction.

### 7. The verdict mappings are pairwise disjoint

`MEMBERS`, `REFUSED`, `DEFERRED` and `GRADER_LOOKALIKES` are asserted pairwise disjoint in the ledger
test. `OUTSIDE_WALK` is left out of that assertion because the union's equality with the walk
population already keeps it apart: a name there is one the walk does not see.

### 8. A reopened refusal joins on the terms every member does, and that is stated once

Adoption, an empty-population posture, and an undecodable-byte posture. The suite already refuses
the move until each is met, as measured above, so nothing is added to a `REFUSED` value or to
`CONTEXT.md`, and this paragraph is where a reader learns the cost is there.

## Superseded, in part

- **ADR 0112 ruling 2**'s *"A **refused** module is a permanent verdict"* is superseded by ruling 2
  here. Its separation of refusals from deferrals into two mappings stands, and so does ruling 3's
  distinction. The ruling's present-tense list of which modules were refused and deferred is
  corrected in place, on
  [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
  rule that a ratified record's facts may be.

## Rejected options

- **Keeping *permanent* in the house sense of *permanent rather than pending*.** The superseded
  sentence carries no contrast beside it, so it reads as *forever*, and that reading is how #1006 was
  filed.
- **A third state between refusal and deferral.** Four states for three modules.
- **Leaving `corpus_census` in `REFUSED` and drawing the distinction in prose.** One mapping would
  hold two kinds under one name, which is ADR 0112 ruling 2's own argument against a single mapping.
- **`OUTSIDE_WALK` for `corpus_census`.** That mapping names modules the walk does not see, and the
  walk sees this one.
- **All three of `tracker_bodies`'s obstacles in its value.** It asserts a kind for the unruled one.
- **Joining costs written into every `REFUSED` value.** A copy of the family's obligations, stale at
  the next obligation the family gains.

## What this does not reach

**Whether a `REFUSED` value's sentence is true.** Ruling 5's check proves the runner's side is named.

**Whether a grader lookalike is correctly placed.** A module filed there on a false account of what
it is instead passes every assertion here; placement stays a reading, as a refusal's reason does.

**Whether ADR 0117 ruling 2's arrangement reaches a mode that grades.** Ruling 6 records it as
unruled; nothing waits on it until a migration of `tracker_bodies` is proposed.

**Whether any refusal reopens.** Nothing schedules one, by ruling 2.

## What must not come out of this

**A migration of `threshold_sheet` or `tracker_bodies`, or a plan for one.**

**A branch in `run_grader.run` or `run_grader.parse`.** Everything ruled here is a declaration and a
test.

**A refusal reclassified as a deferral.** ADR 0112 ruling 3.
