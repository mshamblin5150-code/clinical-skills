# A worktree is removed only after the census holds nothing back

[#1134](https://github.com/mshamblin5150-code/clinical-skills/issues/1134) found 66 registered
worktrees from four conventions, none pruned, and no documented workflow that reaches the moment
[ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md)
ruling 5 names, *"the moment somebody is pruning."* Grilled 2026-09-14 and 2026-09-15 against
`80af0e48`; the clinician ruled every point below on 2026-09-15. Nothing is built here; this is the
record the build reads.

## Measured before ruling

### The population is not the cost

Dated measurement at `80af0e48`, 2026-09-15, and not a current count: 40 registered worktrees, 38
peer roots, 0 stale registrations, 0 peers carrying scratch material. The ad hoc pass recorded on
#1134 on 2026-09-12 had taken the registry from 66 to 41, and a fifth location outside the ticket's
four conventions is registered. The bare census ran in about 0.43 s and `adr_next.py --check-staged`
in about 0.7 to 0.9 s. **Nothing is degraded by the count.**

### Git does not protect a gitignored scratch root

In a throwaway repository with `scratch/` gitignored, plain `git worktree remove`, with no `--force`,
exited 0 on a worktree whose only content was one file under `scratch/`, and the file was gone. The
same command refused a worktree holding one ordinary untracked file. So the refusal a reader expects
from git does not reach the material this repository cares most about.

### The harnesses remove worktrees on their own schedule

Claude Code's worktree documentation describes three removers: removal on exit of a clean worktree
or after a keep-or-remove prompt, a periodic sweep of subagent and background-session worktrees, and
the desktop app's archive action. Its work check reads *"changed or untracked files, and new
commits"*; whether that sees a gitignored file is not stated, and the inference that it does not is
not verified. Codex removes its own worktrees. None of them reads this repository's documentation,
and none runs `git worktree prune`.

### The existing `--worktrees` breakdown cannot serve a pruner

`worktree_breakdown` measures only the checkouts that already own a scratch root, 7 of the 39
non-owning checkouts on that run, and gives the other 32 no removability verdict at all. It decides
"merged" by whether a worktree's commit is in the **owning checkout**'s current history. That
checkout was on a feature branch behind `origin/main`, and 3 of the 7 measured checkouts it reported
as ahead were already on `origin/main`. And it keys on commits alone: the 2026-09-12 pass found two
worktrees holding ADRs that existed nowhere on `main` while `git rev-list --count origin/main..HEAD`
read 0, because the files were untracked.

### Ignored files cannot be the test, and activity cannot be measured

`git status --ignored` across 35 peers: 1 with untracked files, 4 with tracked changes, 2 with commits
not on `origin/main`, 0 with anything under `scratch/`, `output/`, `cases/` or `patients/`. Harmless
ignored entries are nearly universal, `tools/` caches in 34 and the `.claude/skills` junctions in 26,
so a test keyed on any ignored file never reads clean. 0 of the 35 peers were locked. The only
activity signal found, the last write to a worktree's index or HEAD log, spread smoothly from 0 to 17
days with no gap, and `git status` can rewrite the index, so the report would reset the signal it
reads.

## Ruled 2026-09-15

### 1. The removal moment is the problem, not the count

The population stays without an owner, a ceiling or a scheduled pruning step. What is missing is a
check that runs before a worktree is removed. **Treating the count as the problem was declined**: it
needs either a threshold nothing grounds or a routine removal step, and #1134 forbids both. Every
recorded loss happened at a removal, not because of the population's size.

### 2. The check binds deliberate removals, and harness removal is declared

The check binds a removal that a session or the clinician chooses to perform. A removal by a harness
is covered by the arrangement already in place, not by a new mechanism: `scratch_work.py` resolves
session material to the owning checkout, so a worktree normally holds nothing, and the census names
any peer carrying material on every commit. `scratch_census.DECLARED_LIMITS` gains a row saying a
harness can remove a worktree without running the check. **Intercepting harness removal with Claude
Code's `WorktreeRemove` hook was declined**: the documentation describes that hook as replacing the
removal logic rather than checking before it, does not say it can block a removal, and it reaches one
harness of several. **Making harness removal harmless, for example by junctioning each worktree's
`scratch/` to the owning root, was declined**: it reverses ADR 0059's premise that a worktree owns
its own scratch root, `output/` would need the same, and it closes a hole measured at zero.

### 3. `scratch_census.py --worktrees` becomes the pre-removal report

Every registered checkout other than the owning checkout gets one line under the flag carrying: its
file count under `scratch/`, its file count under `output/`, its untracked file count, its tracked
change count, its count of commits not on `origin/main`, and whether it is locked. The flag's
existing breakdown is replaced by those lines, so removability is reported for every peer and not only
for those with a scratch root, and "on `main`" is measured against `origin/main` and never against the
owning checkout's current commit. **The command removes nothing.** Paths stay pasteable on
[ADR 0185](0185-the-scratch-census-counts-peer-roots-and-names-only-the-exceptions.md) ruling 4's
terms, and nothing beneath a root is named: every figure is a count. The flag stays behind a flag, on
ADR 0059 ruling 5's cost ground. **A separate command was declined**: two ratified records already
make this flag the pruner's tool, and a second would split that moment in two. **A documented list of
raw commands was declined** on the 2026-09-12 pass, where the step that got skipped was the one a
remover had to remember.

### 4. The pointer is a conditional rule in two places

`docs/agents/scratch.md` gains a subsection *Before removing a worktree* carrying the rule, the counts,
and what to do with a worktree the report holds back. `CLAUDE.md`'s *The scratch root* section gains
one sentence: if you are about to remove a worktree, run `python tools/scratch_census.py --worktrees`
first and remove none it holds back. **Adding a step to the ticket-finishing workflow was declined**:
it would put a removal on a work list, which #417 ruling 11 and ADR 0059 ruling 6 forbid, a worktree
removal being a scratch-root deletion by another name. **The subsection alone was declined**: a rule
nobody reads before acting is #1134's own defect.

### 5. A held-back worktree is drained or left alone

Material under a held-back worktree's `scratch/` or `output/` may be **drained**. Anything else that
holds it back leaves the worktree alone: the remover does not commit, push, stash or move another
session's work, and the worktree becomes removable only when a later report holds nothing back.
**Committing and pushing the work so it survives removal was declined**: it publishes unreviewed
material to a public repository, sometimes from a session still running. **Referring every held-back
worktree to the clinician was declined**: the scratch drain is already authorized.

### 6. A lock holds a worktree back, and liveness is declared

A locked worktree is held back; `git worktree remove` already refuses one, and the report says so.
Beyond the lock, a running session is indistinguishable from an abandoned worktree, and
`scratch_census.DECLARED_LIMITS` gains a row saying a worktree the report does not hold back may
still belong to a running session. The subsection says the same. **An age floor was declined**: the
measured ages have no gap to ground a cutoff. **Printing a last-activity age as information was
declined**: the report's own `git status` can reset the value it would print.

### 7. An unreadable peer is held back and the exit status is unchanged

A peer whose counts cannot be read prints `not read`, which holds it back. Every `--worktrees` run
states how many peers were read and how many were not. The exit status remains the gating verdict, on
ADR 0059 ruling 4's terms for peers. **Exiting 2 on an unread peer was declined**, and **exiting
non-zero on any held-back peer was declined**: removability is decided line by line, and an exit status
keyed on it invites a loop that removes whatever exits 0, which is the removal command #1134 forbids.

### 8. `CONTEXT.md` widens **Drain**

**Drain** covers two occasions: a gating root's rise, and a peer root's material before its worktree
is removed. Scratch material goes under the owning checkout's **Ticket directory**; `output/` material
goes to the same relative path under the owning checkout's `output/`. A move that would overwrite an
existing file is refused, because an overwrite is a deletion. **A separate term for the pre-removal
move was declined**: it is the same act with the same properties.

### 9. `CONTEXT.md` gains **Held back**

**Held back** names a peer's worktree the report stops a remover from removing, and it is one-sided:
a worktree that is not held back has not been shown safe to remove. **A positive term such as a
removable worktree was declined**: it would assert what ruling 6 declares unknowable. The entry's
avoid list carries `prunable` because git uses that word for a **Stale registration**.

## What this changes in earlier records

ADR 0236 ruling 1 declined a per-root vocabulary partly because a peer *"has no authorized
**Drain**"*. Ruling 5 above authorizes one before removal, so that premise no longer holds. **ADR 0236
ruling 1 stands**, on its other ground: a drain moves cited and uncited material alike, so an
accounted-versus-unaccounted split still tells a pruner nothing actionable.

[ADR 0237](0237-a-missing-worktree-git-reports-as-locked-is-a-locked-registration-and-the-prune-remedy-is-qualified.md),
ruled the same day on #1133, makes the census read git's `locked` attribute and holds that a locked
root whose directory is present is counted exactly as any other root. **Nothing here changes that
count.** Ruling 6 above uses the same attribute for a different purpose: on the pre-removal line, a
lock holds a worktree back. A **locked registration**, whose directory is absent, keeps ADR 0237
ruling 2's own line and gets no pre-removal line, since there is no directory to remove. The two
builds read one porcelain attribute in one module, so whichever lands second reuses the other's
reading.

## Taken as conventions, not ruled

The wording of the per-peer line, the read summary, the two `DECLARED_LIMITS` rows, the subsection and
the `CLAUDE.md` sentence is the builder's, on ADR 0138's assignment of wording to the build. Whether
the committing checkout's own line appears beside the peers is the builder's. A stale `origin/main`
ref over-counts commits not on `main`, which holds a worktree back rather than releasing one, so it
needs no fetch.

## What this does not reach

**A stale registration that is really an unmounted volume.** ADR 0237 rules it, including the
qualifier on the prune remedy. The subsection does not direct anyone to prune.

**A separate clone's worktrees**, already declared in `scratch_census.DECLARED_LIMITS`.

**Material outside every checkout**, likewise already declared.
