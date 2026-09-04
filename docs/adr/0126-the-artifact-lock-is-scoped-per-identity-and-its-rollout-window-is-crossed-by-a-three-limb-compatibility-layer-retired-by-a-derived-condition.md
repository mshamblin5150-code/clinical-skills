# The artifact lock is scoped per identity and its rollout window is crossed by a three-limb compatibility layer retired by a derived condition

[#870](https://github.com/mshamblin5150-code/clinical-skills/issues/870) was filed by an
architecture review of the repo-wide gate, 2026-09-03. It measured `388` seconds of a `746.2` second
suite into one line — `path.parent.glob(f"{path.stem}.reader.*")` at `tools/artifact_lock.py:169`,
scanning a flat shared temp directory that nothing prunes.

Grilled 2026-09-03. **Eight decisions, ruled by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## Measured before ruling, at `63e1ba1`

Freshness gate `FRESH` at both checkpoints. The branch was brought forward from `9500e6f` mid-session
and the merge touched none of `tools/artifact_lock.py`, `CONTEXT.md`, or
`tools/test_glossary_collisions.py`, so every figure below stands on the base this record rests on.

### The growth is live and it is test-driven

The shared directory held **384,840** entries when counted for this grilling — 192,420 `.lock`,
192,418 `.gate`, and 2 stray `.reader.*`. The ticket counted 380,582 the previous day, so it gained
**4,258 in one day**. `mtime` spans 2026-08-27 through 2026-09-03 at roughly 24,000 lock files per
day.

The lock key is `sha256` of the **resolved artifact path**. The dominant population of those paths is
`tempfile.TemporaryDirectory()` inside the suite — a path destroyed at the end of the test that can
never be locked again. So essentially the whole 192,420 is **dead identities by construction**,
rather than a backlog of live artifacts. That is the fact the ticket's three numbered decisions turn
on and it is not stated in the ticket.

### The lock identity need not be a file

`implementation_map.map_artifact` (`tools/implementation_map.py:237-241`) hands `hold()` a synthetic
path under `gettempdir()` that never exists on disk; the real artifact is a GitHub issue. So a lock
identity is a **name**, and "put the lock beside the artifact" is not an available option for this
module.

### The shape has almost no dependents

`clinical-skills-artifact-locks`, `<digest>.lock`, `.gate` and `.reader.*` occur only inside
`tools/artifact_lock.py`. Outside it there are two sites: `tools/test_guidelines.py:1270` calls
`lock_path` and reaches `_gate` directly, and `tools/test_guidelines.py:554` asserts the **negative**
shape that no lock is written beside an in-checkout input.

### The property the compatibility layer exists to protect is pinned once

`_hold_read` exists so a reader excludes a writer, and that direction is asserted at exactly one
site, `tools/test_guidelines.py:1257`. Nothing anywhere pins reader-file cleanup: no test greps
`.reader.`, inspects the lock directory, or asserts the unlink at `:145`, `:155` or `:180`. The crash
test at `:1279` kills a **writer**. The two strays counted above are consistent with a killed reader,
which is untested.

### The coexistence surface is 42, not twelve

`git worktree list --porcelain` reports **42** live worktrees. `CLAUDE.md` says twelve. The stale
figure is unrelated to this defect and is filed separately.

## Decision 1: the namespace is scoped, and pruning is refused on a correctness ground

`…-locks/<digest>/lock`, `/handoff`, `/reader.*`. The reader glob is then bounded by the live readers
of one artifact, so the cost is right by construction and does not depend on a cleanup path being
reached.

Pruning the flat pair was refused rather than deferred. **The handoff file cannot be safely
deleted**, because the handoff is the thing that serializes the ownership transfer — it would have to
protect its own deletion. Unlink a lock between one process's `open` and another's and two processes
hold locks on two different inodes, each believing it owns the artifact. Windows sharing semantics
narrow that window; they do not close it. Growth is ruled separately in decision 5.

## Decision 2: the rollout window is crossed by acquiring the legacy layout as well

A worktree on an old base takes `<digest>.lock`; one on the new base takes `<digest>/lock`. Different
files, so exclusion is gone between them. The window is measured in days against 42 worktrees.

**A schema marker was ruled unavailable rather than declined.** A marker constrains only code that
knows to read it, and the side needing constraint is the side that predates it.

So new code additionally acquires the legacy flat `<digest>.lock`. It costs one `open` and one
non-blocking lock, no `scandir`, so the whole `388` seconds still goes.

## Decision 3: the compatibility layer is three limbs, not one

Decision 2 alone does not deliver what it promises. Two further limbs are consequences of it rather
than separate choices, and each closes a direction the first leaves open:

1. A new **reader** also drops a legacy-named flat `<digest>.reader.<pid>.<uuid>`, because an old
   writer globs flat and cannot see a scoped reader file. Reader files are already unlinked on
   release, so this adds no growth.
2. Both versions share **one handoff file, the legacy flat `<digest>.gate`**, and the scoped
   `<digest>/handoff` does not exist until retirement. The handoff is what makes "check no writer
   holds, then drop my reader file" atomic against "take the writer lock, then scan the readers". Two
   handoff files do not serialize those sequences against each other, so a new reader can clear its
   writer check in the instant an old writer takes the flat lock and scans, before the new reader has
   dropped its legacy file — and both proceed.

With all three, exclusion holds in every direction across the window. With any two, it does not.

## Decision 4: retirement is derived and carried by a tripwire, never dated

A date is refused on the standing rule that elapsed time is not a verdict, since no artifact knows
what its reader's machine holds. The condition is that **no checkout able to run old code remains**,
read by walking `git worktree list --porcelain` and asking, per registered worktree, whether its
`tools/artifact_lock.py` carries the scoped layout — the instrument `adr_next.py` and
`scratch_census.py` already use.

Ancestry (`merge-base --is-ancestor`, `tracker_freshness.py`'s instrument) was declined: it answers
whether a commit has landed rather than whether the checkout's code uses the new layout, and it
breaks under cherry-pick.

It is carried by a **tripwire test** that asserts at least one registered worktree still lacks the
scoped layout, and fails with its own instruction on the day none does. It skips where the walk
reports a single checkout, because CI is exactly that and would otherwise fire on the first run; CI
is not a machine with a coexistence problem. The removal is **also** filed as its own ticket, because
a work item and a tripwire are different things rather than two mechanisms competing.

**The floor is stated rather than discovered**: an abandoned-but-registered worktree holds the window
open forever and the tripwire never fires. That is ADR 0059's registry limit, and it fails safe — the
layer stays and costs one `open` per acquisition.

## Decision 5: nothing deletes, and the generator is killed instead

Two limbs.

**Nothing deletes.** `hold()` leaves a directory per identity forever, and that becomes a stated fact
about the interface rather than a silence — which is how the ticket reads the defect, *what it omits
is a fact a caller must know*. A sweeper was declined: one that unlinks a lock another process is
about to open is decision 1's race, so it would have to take the handoff per identity, and then it is
the refused prune with extra steps. The 384,840 already present are removed by hand **after**
retirement, never before, because the compatibility layer acquires them; and by the maintainer rather
than by a tool, since a tool deleting files in `%TEMP%` it did not create this run is a liability out
of proportion to disk space.

**The generator is killed.** An overridable lock root, in the idiom of `CLINICAL_GUIDELINES_INDEX`
and `CLINICAL_GUIDELINES_BUILDS`, pointed by the suite at a per-run temp directory. Suite-driven
growth goes to zero and the shared root then holds only real artifacts, on the order of ten. It
changes no production behavior, and the cross-process race test at
`tools/test_guidelines_extract.py:1820` survives because an environment variable is inherited by the
subprocess it spawns.

## Decision 6: the override's hazard is declared and never warned about

Two processes pointed at different roots do not see each other, which is the failure #276 exists to
prevent.

**It is undetectable at run time by construction.** The only evidence would be a contention that
never occurred. A runtime signal would therefore be theater, and the `--allow-untrusted-provenance`
precedent argues against it from the other side too: the suite sets the override on every run, so the
line would print on every clean run and become the warning this repository has ruled stops being
read.

So it is declared in a new `artifact_lock.NOT_GUARDED`, bound to prose by a test in the house form,
alongside the permanent debris and the compatibility window's residual. `artifact_lock` carries no
declared-limits object today and every comparable module here does.

The override's **value** is constrained through `repo_root.ensure_outside_checkout`. That does not
stop two processes disagreeing; it forecloses the one misconfiguration a person would reach for, a
per-worktree root that looks reasonable.

## Decision 7: the cost is pinned by counting enumerations, never by wall-clock

The suite was green throughout the defect's life. Nothing failed while acquisition cost
O(every artifact ever locked); the only signal was wall-clock, read as *the suite is slow*. The same
silence is available again, so the invariant is pinned directly.

The invariant is not *no glob in the module*. It is **acquisition cost does not grow with the number
of artifacts ever locked on this machine**, and it is asserted by patching `os.scandir` for the
duration of one `hold()`, counting the entries it yields, and running that twice — with the shared
root empty and with 5,000 junk entries planted — asserting the two counts are **identical**. A
measurement rather than a threshold, with no elapsed time in it, and it survives indirection, a
helper and a library call because it measures what the process did rather than what the source looks
like. A wall-clock assertion is refused as machine-dependent and as a value named at an edge, which
is `SPACE_ADVANCE_FRACTION`'s recorded failure.

An AST walk sits alongside it, asserting the only directory enumeration in the module is rooted at
the per-artifact directory. It is declared a **floor**: enumeration through a helper, or a pattern
assembled at run time, is invisible to it.

Both live in a new `tools/test_artifact_lock.py`. The module has no test file today — its coverage is
scattered across seven modules that each exercise the lock incidentally while testing something else,
and none owns its invariants.

## Decision 8: two glossary terms, and the second sense of `gate` is never created

`CONTEXT.md` carries no lock vocabulary. Two terms earn an entry:

- **Lock identity**, whose load-bearing surprise is that it need not be a file.
- **Lock root**, because it is now overridable and the override silently disables mutual exclusion.

`_gate` **renames to `_handoff`**. `CONTEXT.md` already carries `Gated row set` and `Quotation gate`,
where a gate is a condition governing whether something runs or is reported; the lock's is a short
mutual-exclusion window serializing an ownership handoff. Declaring the collision in
`test_glossary_collisions.DECLARED_CANDIDATES` was available and was declined: it spends a permanent
declaration to keep an ambiguous word this module never needed. The identifier renames now; the
**filename** follows at retirement, because during the window the shared handoff file is necessarily
the legacy `<digest>.gate`.

## What is not ruled here

The gate is serial on a 22-core machine, which is
[#874](https://github.com/mshamblin5150-code/clinical-skills/issues/874) and is untouched by any of
the above. The `388` seconds is the ceiling for one line, not for the suite.

`%TEMP%` is not moved. Redirecting it was the review's instrument for isolating the cost and never a
proposed fix; the 7 errors it produced in
`tools/test_tracker_freshness.TrackerFreshnessCommand` are Windows path length and are a property of
neither this defect nor any fix for it.

Whether a killed reader's stranded `.reader.*` file should be reclaimed is untested today and stays
untested here. Scoping bounds its cost to one artifact's directory, which is why it did not have to
be settled to close this.
