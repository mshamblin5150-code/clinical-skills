# A refuted record is rewritten in place and DROPPED stays sourced-only

**Measured at:** 21a5f7615f9696ecf9bc8ba52049a00e4f64b218

[#1483](https://github.com/mshamblin5150-code/clinical-skills/issues/1483) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 9) on 2026-10-01. A refuted claim's
sentence was cut, and the run kept the record in `claims.md` with its `refuted` verdict and a
substantive `DROPPED` line, reading `skills/_shared/reference/sourcing.md`'s statement that a
`DROPPED` record certifies no value as the honest state for a cut claim. `tools/research_ledger.py`
still exited 1 on the refuted-citation row, so the run moved the record out of the ledger to pass.
Grilled 2026-10-10 against `main`, where the freshness gate read `FRESH`; the clinician ruled every
point below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**ADR 0316 changed the question after the ticket was filed.** Under its ruling 1 a refuted record
refutes the citation, not the claim: the claim gets one fresh research round and comes out with a
sound record or as `unsourced`. A refuted record left as a claim's final state, which is the shape
this ticket was filed over, is therefore no longer a disposition any skill reaches. What remained
open is what becomes of the failed first attempt.

**`DROPPED` was built for a sourced record.** ADR 0211 introduced it for a sourced record whose claim
the draft no longer makes, and `research_ledger.py` already reports `DROPPED` on a record whose
`STATUS` is not `sourced`. An `unsourced` record already states what was searched, and ADR 0316
ruling 3 already requires the question put to the clinician to name each source tried and why each
failed.

**PR #1666, building ADR 0316, leaves the record's fate open.** Its new sourcing-sheet section adds
"The refuted record itself certifies no value and is never cited." A reader can take that to mean the
refuted record stays in the ledger, which the refuted-citation row fails.

## Ruling 1 — the refuted record is rewritten in place

After its fresh round, the refuted record is rewritten in place. It becomes either the sound record
the round produced, or an `unsourced` record whose search text names each source tried and why each
failed, including the refuted source and the refuter's reason. The claim's provenance stays in the
ledger, in the record later readers grade.

The ticket's first option, letting `DROPPED` excuse the refuted-citation row, was declined: it would
let a run cut a refuted claim and pass without the fresh round, undoing ADR 0316 ruling 1. Keeping the
refuted attempt as a separate record marked as replaced was declined here: it needs a new field and a
grader join, and it would answer mechanically what ADR 0316 deliberately leaves declared, whether the
second round used a different source. That belongs on its own ticket if it is wanted.

## Ruling 2 — DROPPED stays on a sourced record

`DROPPED` keeps ADR 0211's meaning: a sourced record whose claim the draft no longer makes. A claim
that ends `unsourced` and is cut carries no `DROPPED`; its `unsourced` status already says the
document makes no sourced claim. The refuted-citation row keeps firing on any record still carrying a
`refuted` verdict, and its comment points to the sourcing-sheet rule rather than restating it.

## Ruling 3 — built after PR #1666, not inside it

This ruling lands in a follow-up build after PR #1666 merges, so no session changes a pull request
another session has open. Until it lands, a run that keeps a refuted record fails the grader, which
is the safe direction.

## What the build changes

- `skills/_shared/reference/sourcing.md`: the refuted-record section's "never cited" sentence becomes
  rulings 1 and 2, stated once.
- `tools/research_ledger.py`: the refuted-citation comment points to that section. No row, exit status
  or finding moves.

## What this record does not reach

- **Whether the `unsourced` search text truthfully names every source tried.** It is substantive prose
  the grader reads for substance, not for accuracy.
- **Whether the fresh round happened at all.** A run can rewrite a refuted record as `unsourced`
  without a second round; ADR 0316 already declares that nothing compares a re-researched record with
  the one it replaced.
