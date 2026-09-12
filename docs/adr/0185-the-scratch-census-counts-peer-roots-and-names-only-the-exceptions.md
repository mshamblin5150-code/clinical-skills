# The scratch census counts peer roots and names only the exceptions

Ruled by the clinician on 2026-09-11, in the grilling of
[#924](https://github.com/mshamblin5150-code/clinical-skills/issues/924). Freshness gate `FRESH` at
both checkpoints; the gate went `STALE` once mid-session and every figure below was re-derived on the
merged base rather than carried across. Nothing is built here; this is the record the build reads.

**The subject.** `tools/scratch_census.py` prints one line per registered checkout on every commit.
Two of those lines are `GATING:` and explain the verdict; the rest are `REPORT ONLY:` peer lines that
are never graded and cannot change the exit status.
[#790](https://github.com/mshamblin5150-code/clinical-skills/issues/790) named the cost in its own
words — *"the one `GATING` line that explains the refusal sitting among them."*
[ADR 0138](0138-an-absent-committing-scratch-root-is-nothing-to-grade-and-the-empty-population-rule-is-not-generalized.md)
ruling 1 removed the acute instance, since a fresh worktree no longer refuses, and filed the
condition separately with the constraint analysis attached: summarizing is **available** rather than
forbidden, and the trade is against
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258) rather than against
[ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md).

## Measured before ruling, at `82092fc`

**Every peer line in this repository today carries zero signal, and that is a measurement the ticket
did not have.** 64 peer roots: 46 with no scratch root at all, 18 with one. **All 18 report `0`
unaccounted entries and `0` files.** Total files beneath every peer root in the registry: **zero**.
Every file the census counts sits under the owning checkout and the committing worktree. So the 64
lines are 64 descriptions of checkouts holding nothing.

The ticket's Option 2 — collapse the absent peers, keep a line for every peer carrying a count — was
written against the belief that a counted peer is a peer with something in it. On this tree it is
not: Option 2 removes 46 lines and keeps 18 that all say zero.

**The report is almost the whole of what the hook says.** On an ordinary commit touching no threshold,
subject, coverage or UpToDate artifact, the unconditional checks print 74 lines: `phi_scan` 3,
`guidelines_currency --hook-summary` 1, `adr_next --check-staged` 1, `skills_mirror`,
`spelling_scan` and `guidelines_catalog` nothing, and **`scratch_census` 69, of which 64 are peer
lines.** The census runs in 0.28s across three runs, so the cost is a reader's attention and not
time. ADR 0059 ruling 5's subprocess-cost argument does not reach these lines: they fall out of a
walk already made.

**The population is not stable enough to be enumerated.** #924 measured 42 worktrees on 2026-09-06.
This session measured **67** at `5460c6f` and **66** twenty minutes later at `82092fc`, without
anyone acting on the registry. The 66 come from four competing conventions — 19 under
`.claude/worktrees/`, 17 under `.codex/worktrees/`, 1 under the Windows temporary directory, and 29
elsewhere — and none of the tooling that deletes those directories runs `git worktree prune`.

**No ratified record requires a per-peer line.** ADR 0059 ruling 1's obligation is *"say how many were
enumerated and name every root that could not be read"* — a count for the enumeration, a name only
for the unreadable — and the `coverage:` line already discharges it by printing those paths inline.
ADR 0059 ruling 4's *"how many roots exist and how many files sit beneath them prints beside every
verdict"* is discharged by the `scratch roots:` summary. ADR 0138 ruling 5's *"the report prints one
line per root either way"* is a measurement offered to defeat a proactive `mkdir`, not an obligation.

**The house rule is already written down, in another module.** A survey of all 33 non-test commands
that print an unconditional coverage statement found **31 printing aggregate counts**. Fifteen of
those also print one line per member of a fixed, module-owned tuple, and `checks_ledger.py:688-694`
states the license for it: *"those strings are `EXPECTED_CHECKS` members, so they are this module's
own text and never the run's."* **Exactly two commands enumerate one line per member of the run's
own population: `render_scan.py` and `scratch_census.py`.** The formulation is *enumerate what the
module owns, count what the run produced*, and a peer root is what the run produced.
`differential_scan.py:1292-1293` carries the brake on reading #258 maximally, beside its own coverage
row: *"a caveat printed unconditionally is one nobody reads."*

**There are two peer loops, and the ticket named one.** `scratch_census.py:302-321` is the branch
taken when the accounted-name set cannot be derived. It ignores the counts, prints one line per root
with every peer reading `not scanned`, and exits 2. That is #790's complaint in its strongest form —
the two lines explaining a refusal sitting among sixty-six — and ADR 0138 ruling 1 never touched it.
On that branch the unaccounted number is genuinely unknowable, because the accounted set is empty;
the **file** count is not, because `count_files` never consults it.

**`CONTEXT.md`'s `Gating root` entry is falsified by the obvious fix.** It reads *"Every other root is
a **peer root**: reported on every run and graded never."*

## Ruling 1 — a peer with nothing to report is counted rather than named

The peer block becomes one summary line that prints on every run and states the complete partition:
how many peer roots, how many with no root, how many empty, how many carrying material, how many
unreadable, how many stale. A peer earns its own line back when it has something to report.

**This satisfies #258 rather than evading it.** What that ruling is against is a clean line with no
population beside it. The summary prints unconditionally and its categories sum to the peer count, so
nothing about coverage becomes silent; what stops printing is sixty-four repetitions of *nothing
here*.

**The cut is licensed by ADR 0138 ruling 9's own test.** An empty population may pass quietly *"only
where the emptiness is established independently of the matcher that would have recognized a
member."* A peer root that does not exist, or that exists and holds nothing, has its emptiness
established by the filesystem rather than by anything the census matches. That is the discriminator
which made ruling 1 of that record safe, applied one step over rather than a fresh concession.

The ticket's Option 2 is refused on the measurement above: it keeps eighteen lines that all say zero,
and a line that says zero on every commit for months is a line that stops being read, which is the
same failure #258 describes arriving more quietly.

## Ruling 2 — the predicate is material held, not the ratchet number

A peer earns a line when its root holds **anything at all** — any file, or any unaccounted entry — or
when it could not be read. Not when its unaccounted count is above zero.

**A peer is never graded, so the ratchet number is not why its line exists.** The only reason to print
a peer at all is ADR 0059 ruling 4's worktree-root hazard, and that hazard is measured in files that
vanish on `git worktree remove`, not in entries that fail a rule nobody applies to them. The case
that separates the two is an abandoned worktree holding four hundred properly filed files under
`scratch/sessions/ticket-912/`: every name in it is cited, so its unaccounted count is zero, and
`scratch_census.DECLARED_LIMITS` already says its removal *"can discard unrecoverable material
without warning."* A ratchet-keyed predicate prints nothing about it.

The predicate is quiet in ordinary operation by measurement rather than by hope. `scratch_work.py`
resolves to the owning checkout, so a session working normally writes nothing into its own worktree's
scratch root — which is why all eighteen are at zero. It fires when something wrote locally and then
walked away, which is the one event worth a line.

## Ruling 3 — unreadable keeps a line and a stale registration does not

An unreadable peer root is named. A stale registration is counted in the summary and not named a
second time.

**Stale collapses on ruling 1's own test.** A directory that is gone holds nothing, and the filesystem
establishes that without a matcher. Its remedy is also collective — one `git worktree prune` clears
every one of them — so a line per stale root is N copies of one instruction. With four worktree
conventions and none of them pruning, that is the report re-growing to the state this record exists
to leave, through a door nobody was watching.

**Unreadable keeps its line, and the duplication with `coverage:` is paid for deliberately.** The two
lines do not say the same thing: `coverage:` says *this could not be read*, and the peer line says
*and it is a peer, so it did not refuse you*.
[ADR 0091](0091-the-scratch-ratchet-refuses-only-roots-the-committing-session-can-write-into-and-the-session-directory-is-ticket-keyed-and-produced.md)
ruling 7 made gating-versus-reporting the report's organizing axis, and unreadable is the one state
where that classification decides the exit status, an unreadable gating root being a refusal and an
unreadable peer being nothing. It also passes ruling 2 honestly: an unreadable root is the hazard at
its worst, because material may be there and the check cannot measure how much.

ADR 0138 ruling 6's distinct printed state for stale survives in the `coverage:` line, which names
every one of them by path, and as its own category in the summary.

## Ruling 4 — `--worktrees` restores the full per-peer enumeration

The flag keeps its removability line and gains the complete per-peer list.

**This is what makes the change a summarization rather than a loss**, which is the residual #258
exposure and the one thing that would have made the collapse a genuine narrowing. Nothing that prints
today stops being obtainable; it moves to the command run at the only moment anyone wants it.

ADR 0059 ruling 5 defines that moment: the removability breakdown lives behind this flag because it
is *"the only moment it is actionable, being the moment somebody is pruning."* A pruner needs to know
which worktree is holding material and which is merged and removable, and three aggregate integers
answer neither. The addition costs nothing to compute, since the per-peer counts already fall out of
the census walk and the flag is already paying for the expensive git half.

**It stays `--worktrees` and does not become `--show`.** In sixteen other commands here `--show`
means private working material that must not be pasted. This command deliberately has none and its
output is pasteable; a `--show` that printed pasteable output would teach the wrong thing about the
flag everywhere else.

On the accounted-set failure branch the per-peer unaccounted numbers are unavailable, and the flag
says so rather than printing a number it cannot stand behind.

## Ruling 5 — the prune remedy is said only under `--worktrees`

`REMEDY: run git worktree prune` prints under the flag, once, when the stale count is non-zero. The
bare command carries the count and not the instruction.

**A remedy on every clean commit is this record's own subject arriving again.** Four harnesses create
worktrees here and none prunes, so a non-zero stale count is the steady state rather than an event: a
line keyed on it prints on every commit forever, telling a reader to run a command nobody runs in the
middle of a commit. ADR 0138 ruling 2 set the placement principle when it put the do-not-delete
warning on the finding line — the instruction belongs at the moment somebody is blocked, because that
is the only moment anybody acts on it. Nobody is blocked by a stale registration.

Printing nothing at all was the alternative and is defensible; it was refused only because it leaves
the counted category with no instruction anywhere a reader will meet it.

## Ruling 6 — the accounted-set failure branch collapses too

The second peer loop takes ruling 1 and ruling 2, with the predicate degraded to files alone and the
report saying so.

**More strongly than on the ordinary path, not less.** On a clean run the collapse is about attention;
here it is about a reader finding why the commit was refused, which is what the ticket was filed
over, and it is the one moment somebody is reading this output rather than scrolling past it.

The degraded predicate is **more** honest than what prints today. Right now every peer on this branch
reads `not scanned` whether it holds four hundred files or nothing, so the report flattens the one
distinction that would say whether anything is at risk. Under this ruling a peer holding files says
so and names which half of its number is unknown.

## Ruling 7 — the peer block moves above the gating lines

Order becomes `coverage:`, `scratch roots:`, the peer summary and its exceptions, the gating lines,
the verdict, the remedy. This is #924's own Option 3, which the ticket offered as an alternative to
summarizing and which becomes nearly free once the summarizing is done.

The ground is where output lands. This runs inside the pre-commit hook with its stream redirected
alongside the other checks, so what a person sees is the bottom of the terminal; putting *what was
graded*, *what the verdict is* and *what to do* in one unbroken block at the end makes a refusal
legible without scrolling. It also keeps every statement about scope in the top three lines and every
statement about this commit in the bottom block, where today the graded lines sit in the middle of
the coverage material.

It costs nothing to make. No assertion in `tools/test_scratch_census.py` reads line order; all 46 are
`assertIn`. ADR 0059 ruling 4's *"beside every verdict"* is satisfied by three lines above it, and
`filled_vitals_census.py:608-613`'s ordering comment asks that counts print ahead of caveats, which
this satisfies.

## Ruling 8 — `CONTEXT.md` loses one word and gains one term

`Gating root` reads *counted on every run and graded never*. The word `reported` goes and nothing
replaces it.

**That sentence went stale because it described the report.** Repairing it with a more accurate
description of the report buys a sentence that goes stale on the next change; `counted` is true under
every arrangement weighed here, and it is the repo's own distinction from `checks_ledger`. The fact
that a peer holding material is also named is true and is deliberately **not** added, because it is
the report's shape and it belongs in the module and in this record.

`Stale registration` gains an entry. ADR 0138 ruling 6 introduced the concept and ruling 8 of that
record added three other terms and not this one, and ruling 3 above makes it a counted category the
report prints — a word with no settled meaning behind it. The entry defines it against
`Unreadable source` and records that it can only ever be a peer, the owning checkout resolving
through its `.git` pointer and the committing checkout being the one a session is standing in.

The unmounted-volume hazard is deliberately kept out of that entry. It is a finding rather than a
ruling and it is filed.

## Alternatives refused

**Leave it, #924's Option 4.** Refused on the measurement: 64 of the hook's 74 lines say nothing, and
the population that generates them grew by 25 in five days and moved twice inside this session.

**Summarize the absent peers only, #924's Option 2.** Refused above. It was the strongest option on
the ticket's own numbers and the weakest once the counted peers were measured.

**Reorder without shortening, #924's Option 3.** Taken as ruling 7 rather than refused, but it is not
a substitute: with 64 peer lines, moving two gating lines adjacent to the verdict still leaves the
report unreadable at a glance.

**Name the per-peer list `--show`.** Refused under ruling 4 on the repo-wide meaning of that flag.

**Print the prune remedy unconditionally.** Refused under ruling 5.

**Drop the unreadable peer's line as redundant with `coverage:`.** Refused under ruling 3. It is the
tidy-looking change a later session will propose, and the reason it is wrong is that the two lines
carry different axes.

## What none of this reaches

**Whether a peer root's unaccounted count means anything.** `accounted_names` derives one set from
the **committing** checkout's tracked files and applies it to every root, so a peer's count is
measured against this branch's vocabulary rather than its own. Today every peer is at zero and
nothing rests on it. It is not in `DECLARED_LIMITS` and it is filed.

**The registry population itself.** 66 registrations from four conventions, none of them pruning, is
the pressure that produced this record and it is not a report question. Filed.

**Whether a stale registration is a deleted worktree or an unmounted volume.** The census decides by
asking whether the directory exists now, so a missing network path or external disk reads identically
to a deletion, and following ADR 0138 ruling 6's prune in that state unregisters a live worktree and
makes `DECLARED_LIMITS`' abandoned-worktree hazard permanent. Filed.

**Whether the summary's categories are the right ones.** The partition must sum to the peer count;
the category names and the line's exact wording are the builder's, on ADR 0138's own assignment of
wording to the build.

**Whether `scratch_census` should move onto `run_grader`.** Untouched, as ADR 0138 ruling 7 scoped it.

**An end-to-end test through the hook.** Still unavailable for ADR 0138 ruling 10's reason, unchanged
by anything here.
