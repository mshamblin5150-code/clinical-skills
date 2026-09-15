# A peer scratch root is described by its files alone and no vocabulary is applied to it

[#1135](https://github.com/mshamblin5150-code/clinical-skills/issues/1135) found that
`tools/scratch_census.py` derives its accounted name set once, from the committing checkout, and
applies that one set to every registered root. For the two gating roots that is the gate's whole
ground. For a peer root it is a cross-branch measurement nothing declares: a peer's unaccounted count
is the number of its top-level entries that the committing branch happens not to cite. Grilled
2026-09-14 against `f90a66a5`; the clinician ruled every point below the same day. Nothing is built
here; this is the record the build reads.

## Measured before ruling

### The defect reaches the ordinary path

`peer_population` admits a peer to its own line when `files > 0` or, with `unaccounted_available`
true, when `unaccounted > 0`. `main` passes `unaccounted_available=False` only on the branch taken
when the accounted set cannot be derived, and that branch returns 2; the ordinary branch passes
`True` for the same two peer calls. So on an ordinary commit the committing branch's vocabulary
decides whether a peer holding an uncited empty directory prints at all, and `--worktrees` prints an
unaccounted figure for every peer that has a root.

**Two published claims on #1135 disagreed about this, and the later one is right.** The 2026-09-12
tracker-sweep comment read the two `False` call sites as the peer path and the two `True` call sites
as the gating path, and marked the ticket body's *"a peer that earns a line still prints its
unaccounted count beside its file count"* false. The four sites are one error-branch pair and one
ordinary-branch pair of the same peer calls, which the 2026-09-12 14:46 comment established by
running the command. This session re-derived that reading from the code and from a live run.

### The population, 2026-09-14

40 registered worktrees, 0 unreadable. 38 peer roots: 31 with no scratch root, 7 with one, 0 carrying
material. Two of the seven hold exactly one top-level entry each, an empty directory whose name is a
standing artifact cited by both the committing branch and the peer's own branch, and no file. So
every peer figure printed today is correct, and it is correct because the two branches happen to
agree. A walk of all 8 scratch roots found 0 symbolic links and 0 junctions.

### What a per-root vocabulary would cost

Median of five runs: one `accounted_names` call is 0.054 s; the whole census is 0.25 s. Deriving a set
per peer that holds an entry would add two `git grep` subprocesses today and one per such peer as the
registry grows, which is the growth
[ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md)
ruling 5 moved behind `--worktrees`.

## Ruled 2026-09-14

### 1. A peer root has no vocabulary

The accounted set is applied to the two gating roots and to nothing else. No peer line prints an
unaccounted figure, on the ordinary path or under `--worktrees`. **Declaring the cross-branch limit
was declined**: it keeps printing a number whose meaning depends on which checkout a commit is made
from. **Deriving a set per root was declined**: a peer is never graded and has no authorized
**Drain**, so an accounted-versus-unaccounted split tells a pruner nothing actionable, since removal
discards cited and uncited material alike, and it would buy that nothing with a subprocess per root.
The unaccounted figure was the only part of a peer's line that depended on anything but the
filesystem, so removing it removes the defect rather than documenting or maintaining it.

### 2. A peer earns a line by holding a file or by being unreadable

The peer predicate is **at least one file**, or a root that cannot be read. An empty top-level
directory is not material. This supersedes
[ADR 0185](0185-the-scratch-census-counts-peer-roots-and-names-only-the-exceptions.md) ruling 2's
*"any file, or any unaccounted entry"*. **Counting any top-level entry was declined** on the
measurement above: it would add two lines saying zero files to every commit, the zero-signal report
ADR 0185 exists to leave, and an empty directory holds nothing its removal can lose. Ruling 2's
hazard is measured in files, and `count_files` establishes a file count without a matcher, which is
[ADR 0138](0138-an-absent-committing-scratch-root-is-nothing-to-grade-and-the-empty-population-rule-is-not-generalized.md)
ruling 9's test.

### 3. Both branches report peers identically

The branch taken when the accounted set cannot be derived stops degrading its peer predicate and
stops printing `unaccounted not scanned`, because nothing about a peer depends on that set any more.
This supersedes ADR 0185 ruling 6's degraded predicate; that ruling's collapse of the failure branch
stands. The gating lines, the exit status, the summary partition and the line order are unchanged.

### 4. A link under a peer root is declared, not followed

`count_files` does not follow links, so a peer whose `scratch/` holds only a link to a directory of
files counts as holding no file and prints no line. Under the old predicate an uncited link at least
earned `1 unaccounted`. `scratch_census.DECLARED_LIMITS` gains one row saying a link under a peer root
counts as no file. **Counting a link as material was declined**: a second, link-specific predicate
for a population measured at zero. Removing a worktree removes the link and not its target, so the
removal hazard ruling 2 keys on does not reach the target.

### 5. `CONTEXT.md` is unchanged

**Gating root** already says a peer root is *"counted on every run and graded never"*, which stays
true. No term is added.

## Taken as conventions, not ruled

The wording of a peer line and of the new `DECLARED_LIMITS` row is the builder's, on ADR 0138's
assignment of wording to the build. Replacing the tests that assert a peer line carrying an
unaccounted figure is the build's; each must be replaced by a control proving the reversed behavior,
including a peer holding an uncited empty directory and no file printing no line.

## What this does not reach

**How the gating roots are measured.** Their vocabulary is correct and is the gate's whole ground;
#1135 forbade changing it.

**Per-root `git grep` on any path.** Ruling 1 removes the need rather than relocating it to
`--worktrees`.

**Whether a link's target is at risk.** Ruling 4 declares the boundary and does not follow a link.
