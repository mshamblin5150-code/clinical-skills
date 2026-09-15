# A missing worktree git reports as locked is a locked registration and the prune remedy is qualified

[#1133](https://github.com/mshamblin5150-code/clinical-skills/issues/1133) was filed on
2026-09-11 from the grilling of [#924](https://github.com/mshamblin5150-code/clinical-skills/issues/924),
and [ADR 0185](0185-the-scratch-census-counts-peer-roots-and-names-only-the-exceptions.md) closed
on it as filed: `tools/scratch_census.py` decides a missing registered root is a **stale
registration** by asking whether its directory exists now, so a worktree on an unmounted volume
reads identically to a deleted one. [ADR 0138](0138-an-absent-committing-scratch-root-is-nothing-to-grade-and-the-empty-population-rule-is-not-generalized.md)
ruling 6 attaches the remedy *"the fix is `git worktree prune`"* to that state, and ADR 0185 ruling
5 made the census print it under `--worktrees`. Following it while a volume is down unregisters a
live checkout, and `git worktree list` is the census's whole population, so that checkout's scratch
material leaves the walk permanently.

Grilled 2026-09-15 to an empty frontier. **Seven rulings, by the clinician, on that date.** Nothing
is built here; this is the record the build reads.

## Measured before ruling

Every figure here is a historical measurement taken 2026-09-14 and 2026-09-15.

**Git cannot separate the two states, and that was measured rather than reasoned.** A throwaway
repository registered one worktree on a `subst` drive letter and one on the system drive, then the
drive letter was removed and the other directory deleted. `git worktree list --porcelain` printed
the identical line under both, `prunable gitdir file points to non-existent location`, and
`git worktree prune -n -v` listed both for removal. Remounting restored the first. The administrative
directory under `.git/worktrees/` survives both states, so it discriminates nothing either. The
ticket's first open question is therefore settled as a fact: no probe of what git records separates
a deleted checkout from an unavailable one.

**Git already carries the declaration this needs.** A worktree marked with `git worktree lock`
whose directory is then removed prints `locked <reason>` and no `prunable` line, and
`git worktree prune` skips it. The lock exists, in git's own documentation, for a checkout on
portable or network storage that is not always mounted.

**The census discards that line.** `worktree_roots` keeps only lines beginning `worktree ` and
reads neither `locked` nor `prunable`.

**A volume-root probe reaches one form only.** Where a drive letter is unmounted its root does not
exist, while a deleted directory on a present drive keeps its root. A share mounted without the
path, or a volume mounted into a folder, defeats it.

**This repository has no instance today.** At `f90a66a5` the registry held 40 worktrees, none
locked, none prunable, none off the system drive; at `80af0e48` the census enumerated 36 with zero
stale.

## Ruling 1. A missing root git reports as locked is a locked registration

The census reads git's `locked` attribute from `git worktree list --porcelain`. A registered root
whose directory is not present and which git reports as locked is a **locked registration**: its
own state, outside the stale count, and never a trigger for the prune remedy. A missing root git
does not report as locked stays a **stale registration**. A locked root whose directory is present
is counted exactly as any other root, because the lock says nothing about what it holds.

This is not a widened instrument. The census stops discarding a line git already prints, and that
line is git's own declaration of the one condition the ticket is about. #254's standing preference
for declaring coverage over widening is kept by ruling 6 for every worktree nobody locked.

Neither gating root can be a locked registration. The owning checkout resolves through its `.git`
pointer, and the committing checkout is where the command runs, so its directory is present.

## Ruling 2. Each locked registration is named on every run and graded never

The peer summary gains a locked count beside its stale count. Each locked registration also prints
its own report-only line with its root path, on the bare command as well as under `--worktrees`,
and never changes the exit status on ADR 0091 ruling 7.

ADR 0185's formulation is *count the peers, name only the exceptions*. A stale registration stays
counted because one `git worktree prune` clears every one of them. A locked registration is an
exception: material may sit under it outside this run's walk, and no command clears it.

## Ruling 3. The report says `locked`, and never the lock reason

The line states that the root is locked and whether git holds a reason. It never prints the reason
text. That reason is the only free text a person types that the census would otherwise reach, and
the census output is pasteable on
[ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md)'s
terms; its bound is what the code can draw from, on `reference_scan.py`'s precedent.
`git worktree list --porcelain` shows the reason to anyone who needs it.

## Ruling 4. The glossary gains locked registration and narrows stale registration

`CONTEXT.md` defines **Locked registration** and amends **Stale registration** to assert only that
the directory is not present and the worktree is not locked. The previous definition said a stale
registration holds nothing because nothing is left to hold it, which is false for an unlocked
checkout on an unmounted volume. *Unmounted* is on the new term's avoid line because the census
never observes mounting.

## Ruling 5. The prune remedy carries its qualifier where it is printed

Under `--worktrees` only, on both the normal branch and the accounted-set failure branch, the line
`REMEDY: run git worktree prune` gains two indented lines directly beneath it. The first says to
prune only after confirming each stale directory was deleted rather than on an unmounted volume,
and that a prune cannot be undone. The second names `git worktree lock <path>` for a worktree on
removable or network storage. Wording is the builder's within that content.

ADR 0185 ruling 5 stands: the bare command carries the count and not the instruction. The
qualifier rides on the remedy line on ADR 0091 ruling 7's placement principle, because the moment a
reader is about to act is the only moment the warning reaches anyone.

## Ruling 6. One declared limit covers the case nobody locked

`scratch_census.DECLARED_LIMITS` gains one row stating that an unlocked worktree on an unmounted
volume reports as a stale registration, and that pruning it unregisters a live checkout whose
scratch material then leaves the walk permanently. No row is added for locked registrations: each
is named on every run, so its unread material is on the page rather than silently absent.

## Ruling 7. The ticket's two exclusions stand

No threshold on how long a root has been missing, on ADR 0138 ruling 2. No refusal on a stale or
locked registration: a peer never changes the exit status, and a missing volume is not a commit's
fault.

## Refused

**A volume-root probe.** It answers confidently for an unmounted drive letter and silently for
every other form of the same condition, and this repository holds no off-drive worktree to measure
it against. It is the partial instrument the extractor-coverage rule forbids presenting as a whole.

**Declaration alone.** It would leave the census discarding git's own marker for the condition
while printing a remedy that marker exists to prevent.

**Printing the lock reason**, verbatim or under `--worktrees`. Refused under ruling 3.

## What this record does not settle

**Whether a worktree on removable storage gets locked.** Nothing here locks one, and no harness in
this repository does. The remedy names the command; adopting it is the clinician's.

**`tools/adr_next.py`'s own worktree walk**, which reports a missing directory as unreadable and
reads no attribute either. It prunes nothing and recommends no prune, so the hazard does not reach
it.

**The build.** The peer summary's exact wording, the per-root line, the limit row's constant
name, `docs/agents/scratch.md`'s account of unavailable roots, which describes the census as built
and so moves with the code rather than ahead of it, and the tests: a locked and missing worktree
fixture, and a stale registration on the accounted-set failure branch, which no test drives today.
