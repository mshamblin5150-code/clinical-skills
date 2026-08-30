# Blocked is one kind-agnostic gate label on an axis orthogonal to the roles and the sweep holds its invariant

[#573](https://github.com/mshamblin5150-code/clinical-skills/issues/573) found `blocked` live on
the tracker, documented in neither `docs/agents/triage-labels.md` nor `CLAUDE.md`, with a GitHub
description — *"Gated on a maintainer decision; do not start"* — that its own carriers contradict
in their bodies. The ticket forbade the cheap move (ratify the description as written) and the
destructive one (relabel before ruling), and put the vocabulary question to the clinician.

Grilled 2026-08-29. **Four decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## Measured before ruling, at `3ef2e74` (re-derived after merge at `eb0395a`)

**Seven open tickets carried `blocked`: #87, #429, #471, #519, #551, #587, #641.** The list is a
dated measurement, enumerated so the next re-derivation can check itself — the ticket's own thread
watched the population move from nine to twelve to seven inside three days, so the live set is
`gh issue list --state open --label blocked`'s to state, never this record's.

Of the seven, **one** fit the stated description. #87's gate is the maintainer's word at ship
time, unrecordable as an edge (`blocked_by` is `[]`, correctly). The other six were gated on
unlanded builds: #429 on four open blockers, #471 and #641 on #587, #519 on #483 and #587, #551
on #512. #483 — named decision-gated by two earlier sweeps — was `ready-for-agent` at measurement,
so every gate in the build column was a build.

Three shapes the description could not account for:

- **#551 carried `bug, ready-for-agent, blocked`** — under the documented definitions, a ticket an
  unattended agent may pick up and must not start, the defect `triage-labels.md` cites #8 for.
- **#587 carried `blocked` with no recorded edge at all** — its gate on #483 lived only in prose,
  the shape [#589](https://github.com/mshamblin5150-code/clinical-skills/issues/589) had already
  demonstrated once and had repaired.
- **ADR 0056 ruling 3's piece-split tickets (#498, #500, #541) recorded edges and deliberately
  withheld the label**, because one piece is startable while another waits — so whatever `blocked`
  means, an open `blocked_by` edge cannot imply it.

Also measured: `215 follow up` is live on zero open tickets — all eight carriers (#277–#300) are
closed. `in flight` is documented in `docs/agents/issue-tracker.md` and is mechanically
load-bearing (`tracker.yml` fires `tracker_branch_scope.py` on it); [#573]'s first sweep comment
ruled its *"or the undeclared ones are deleted"* limb must not reach it.

## Ruled 2026-08-29

**1. One word, kind-agnostic.**

`blocked` stays and is redefined: **an unmet gate exists — an open `blocked_by` edge, or a gate
named in the body that no edge can record; do not start any part of the ticket until it clears.**
The GitHub description string, the `triage-labels.md` entry, and `CLAUDE.md`'s label sentence move
together.

The alternatives fail on the measurement. *Two words* (decision-gated vs build-gated) died on the
decision column collapsing to one ticket — and #429's history shows a single ticket's gate
flipping kind as its blockers get ruled, so a kind-bearing label needs re-choosing every time a
blocker changes character. *None* (delete, let the edges carry it) died on #87: its gate is
exactly the one an edge cannot record, and `grilling` — which it also carries — claims *decisions
are open*, not *do not start*, which are different statements. The word already functioned as
"unmet gate, do not start" on six of seven; the ruling makes the description say what the usage
says.

**2. `blocked` is orthogonal to the role axis.**

A role label says *what work the ticket owes* — a ruling to grill, a build an agent can do, a
build a human must do. `blocked` says *whether it may start now*. Two axes:

- `ready-for-agent` + `blocked` = fully specified, dispatchable the instant the last gate clears,
  no respec needed. #551's shape becomes correct as labeled.
- `grilling` + `blocked` = a decision is owed and it, or something else, gates the whole ticket.
  #87's shape stays correct.
- The documented exclusivity of `grilling` and `ready-for-agent` is untouched — that is
  exclusivity *within* the role axis.
- **An open `blocked_by` edge does not imply the label.** The label claims the whole ticket must
  not start; a piece-split ticket records edges and carries no label, per ADR 0056 ruling 3.

The exclusive reading — `blocked` supersedes any role — was refused because it destroys exactly
the information that makes the pairing useful: a cleared gate would leave the ticket roleless,
needing re-triage before anyone knows what kind of work it owes. The tracker had already generated
both pairings unprompted.

**3. The invariant is the sweep's, in prose, and no tool is built.**

The invariant: *every open `blocked` ticket has an open `blocked_by` edge, or a body naming a gate
no edge can record.* The reverse direction is deliberately not required (ruling 2). It lands as a
paragraph in `docs/agents/issue-tracker.md`'s sweep guidance with the two repairs: all gates
cleared and none named → pull the label and re-triage; gate in prose only → record the edge.

A tracker-family scanner was priced and refused. The tools open no sockets, so a grader would need
a new documented harvest step feeding a new tool — to certify an invariant the ordinary sweeps
caught by hand three times in the week before this ruling (#545's stale label, #589's missing
edge, #587's prose-only gate). Declare the coverage; do not widen the instrument.

**4. Every label is documented and none is deleted.**

`triage-labels.md` names everything the repository has: the five canonical roles, `grilling`, the
`blocked` entry per ruling 1, a **pointer** to `in flight`'s home in `issue-tracker.md` (not a
second copy — a prose edit to either of two copies fails nothing, which is #220), and one line
ruling `215 follow up` a **retired orthogonal cohort tag** — not a role, applied to nothing new.
Deletion was refused for `215 follow up` because stripping a label strips it from its eight closed
carriers too, and the cohort grouping on the Module 1 episode is the only cheap way back into
those findings.

## Consequences

The seven carriers are disposed by mechanical application, which is the build: #87 keeps
`grilling + blocked`; #587's edge on #483 is recorded; the fully-ruled build-gated tickets gain
`ready-for-agent` beside `blocked` where they meet `triage-labels.md`'s own test; every carrier
ends with a role the mapping defines. `CLAUDE.md`'s *"plus a local `grilling`"* sentence is
corrected to defer to `triage-labels.md` as the one home of the label vocabulary.

The ticket's Done-when is restated as predicates over `gh label list` and the dependency API
rather than an enumerated ticket list — the thread demonstrated the list decays on ordinary
tracker traffic, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)
with a schedule.

What this does not settle: whether a living derived view (#596's shape) wants a role label at all.
That question is flagged on #596 and stays there.

## Addendum — a piece-split ticket is not wholly blocked

Ruled by the clinician on 2026-08-30 after the implementation review exposed the live dependency
direction.

**5. #587 carries no `blocked` label and gains no reverse edge.** Its body makes items 1, 2 and 6
independently startable while the remaining items wait on #483. Ruling 2 therefore excludes the
whole-ticket label. The tracker already records #483 as blocked by #587; adding the reverse edge
would create a cycle and would still overstate #587's partial gate. Remove `blocked` from #587,
keep its `ready-for-agent` role, and leave the dependency graph unchanged.

This supersedes only the Consequences sentence directing the build to record #587's edge on #483.
The rest of the carrier disposition and every earlier ruling remain unchanged.
