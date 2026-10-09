# A refuted record fails the citation, and a clinician-supplied claim is asked about before a cut

**Measured at:** 74049d4bf00a5134718fa9cd54582377e50cf257

[#1481](https://github.com/mshamblin5150-code/clinical-skills/issues/1481) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 9) on 2026-10-01. A claim about the
authorship of a historical work was refuted because the one source tried, a tertiary encyclopedia,
introduces the fact with a hedging qualifier; step 4 mapped `refuted` to a cut, and the clinician
overruled the cut. The same family recurred on the NUR 5042 Module 10 `course-assignment` paper, where
a philosophical attribution was stripped rather than sourced. Grilled 2026-10-09 against `main`, where
the freshness gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

**`discussion-post` is the only coursework skill that cuts on the verdict.** Its step 4 reads
"`refuted`: the sentence is cut, not softened or hedged". `discussion-reply` says a refuted record "is
repaired or made honestly unsourced before drafting". `practicum-case-study` says a refuted record "is
a failure and not an outcome" whose claim "goes back through this step and comes out either with a
sound record or as `unsourced`". `course-assignment` and `peer-critique` state no disposition of their
own and rest on `research_ledger.py`'s refuted-citation row, whose remedy is to rewrite the record or
write `unsourced`. The ticket's open decision, whether re-sourcing reaches every skill, assumed a cut
rule the other four do not have.

**The refutation in the filed run was correct under the current rules.** ADR 0315 ruling 5 refutes a
broadening, and a dropped qualifier is one; an unqualified authorship claim cited to a source that
qualifies it claims more than that source states. What the verdict established is that the citation
fails. It established nothing about whether the claim is true.

**No grader observes the cut.** `discussion_artifact` refuses to believe a refuted record, so it can
certify no body number and back no citation, but nothing reads whether the refuted sentence is absent
from the draft. `tools/test_discussion_post_skill.py` pins the word "cut" in step 4's wording.

## Ruling 1 — a refuted record refutes the citation, not the claim

A `refuted` verdict in any coursework skill sends the claim back through research. It never removes a
sentence by itself. `discussion-post` step 4 adopts the disposition the other four skills already
use: the claim comes out with a sound record or as `unsourced`, and the existing `unsourced` rule then
decides the sentence.

The ticket's proposed diff, which re-sourced only a refutation resting on the source's own hedge and
kept the immediate cut for contrary evidence, was declined. It asks the refuter to sort hedging from
contradiction, a line no tool grades and one ADR 0315 ruling 5 deliberately does not draw, since a
dropped qualifier and a contrary statement are both broadenings. Contrary evidence is still caught:
a fresh source and a fresh refuter facing a false claim refute it again. Keeping the cut and answering
each recurrence with a memory ruling was declined because the next true claim one encyclopedia hedges
is cut the same way.

## Ruling 2 — one fresh round, never the refuted source again

A refuted claim gets exactly one further research round: a source other than the one already refuted,
checked by a fresh refuter. If that record also fails, the claim is `unsourced`. An unbounded loop was
declined because researching until some source agrees is the source-shopping the refutation pass
exists to resist; two rounds was declined for want of any measurement favoring it over one. The case
a further search would most often save is the clinician's own claim, and ruling 3 reaches that one
directly.

## Ruling 3 — a clinician-supplied claim is asked about before it is cut

When a claim that ends `unsourced` would be cut, and the claim is a
**Clinician-supplied claim** (`CONTEXT.md`) rather than one the run introduced during research, the run asks the
clinician before the draft is final. The question names each source tried and why each failed. The
clinician may supply a source, rule that the claim stays, or agree to the cut. A claim the run
introduced is cut and reported as `discussion-post` step 4 reports a cut today.

Keeping such a claim uncited by widening `unsourced` was declined: it puts an uncited factual
statement in graded work, and the clinician's standing ruling on philosophical attribution asks for
the name, an explaining sentence, and a reference. Cutting and reporting after the second round was
declined because it is the filed outcome one round later.

## Ruling 4 — a claim is clinician-supplied by where it came from, not by a marker

A claim is clinician-supplied when it came from the clinician: an invoked source in the clinician's
reasoning, the brief or notes the clinician handed over, a paper the clinician already approved, or a
domain the canonical voice model records as the clinician's. The run states that provenance when it
asks. Restricting the question to sentences carrying `discussion-post`'s invoked-source marker was
declined because a fact from the clinician's own earlier paper carries no such marker and would be
cut unasked. Asking about every failed claim was declined because the clinician's word adds nothing
to a fact the run found by itself.

## Ruling 5 — written once in the shared sourcing sheet, pointed to from five skills

Rulings 1 through 4 are written in `skills/_shared/reference/sourcing.md`, which all five coursework
skills already read first, and each skill's disposition step points to that rule. A test binds each
pointer. `discussion-post` alone, as filed, was declined because the Module 10 recurrence was a
`course-assignment` run. Five separate copies were declined as five prose copies of one rule.
`practicum-case-study` already lists `unsourced` claims at its go-ahead; under ruling 3 a
clinician-supplied one is asked about rather than merely listed.

## What the build changes

- `skills/_shared/reference/sourcing.md` gains rulings 1 through 4 as one rule.
- `discussion-post` step 4 drops "the sentence is cut" for `refuted` and points to that rule; its
  report-every-cut sentence stays for claims the run introduced.
- `discussion-reply`, `peer-critique`, `course-assignment` and `practicum-case-study` point to the
  same rule at their refutation disposition.
- `tools/test_discussion_post_skill.py` stops pinning the cut wording, and a test binds the five
  pointers to the sheet.

## What this record does not reach

- **Whether a claim was clinician-supplied.** The provenance is the run's statement; no ledger field
  records it and no grader reads it.
- **Whether the second round used a different source or refuter.** No row compares a re-researched
  record with the refuted one it replaced.
- **Whether a refuted sentence left the draft.** As measured above, nothing reads the draft for a
  refuted claim's sentence; this ruling changes when a cut happens, not whether one is graded.
