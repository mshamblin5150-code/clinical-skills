# An absent committing scratch root is nothing to grade and the empty population rule is not generalized

Ruled by the clinician on 2026-09-06, in the grilling of
[#790](https://github.com/mshamblin5150-code/clinical-skills/issues/790). Freshness gate `FRESH` at
both checkpoints. Nothing is built here; this is the record the build reads.

**The subject.** A fresh worktree has no `scratch/` directory, because `scratch/` is gitignored and
`git worktree` does not materialize gitignored root content. `tools/scratch_census.py` reads that
absence as a gating root it could not scan, exits 2, and the pre-commit hook refuses the commit. The
message names no remedy. The thread carries eleven independent live reproductions across five days
and two agent harnesses, and this session was the twelfth.

## Measured before ruling, at `4b8e884`

**The gate is one line and it pools four states.** `tools/scratch_census.py:304-306`:

```python
gating_unavailable = [root for root in (*absent, *unreadable) if root in (owning, checkout)]
```

Owning-absent, owning-unreadable, committing-absent and committing-unreadable collapse into one exit
2. An absent owning root means the corpus is gone; an absent committing root is what `git worktree
add` produces every time.

**`absent` cannot mean what the ticket's own decision 1 says it might.** `count_root` at `:166-177`
raises `FileNotFoundError` when the checkout directory itself is missing, returns `None` only when
that directory exists and has no `scratch/` child, and lets `iterdir()` raise for a root that cannot
be walked. So a vanished disk lands in `unreadable`. **`absent` has exactly one meaning already —
this checkout exists and has never had a scratch root** — and it cannot be reached by a fault. The
predicate the ticket worries is ambiguous is precise; only the status pools it.

**The report was already ahead of the gate.** `:331-333` prints `absent` and `unreadable` distinctly
while `gating_unavailable` does not distinguish them. `REMEDY:` sits inside `if finding:` at
`:358-363`, the exit-1 path only, so the failing case that blocks a commit is the one that says
nothing about how to clear it.

**The defect is a pinned property, not an oversight.**
`tools/test_scratch_census.py:249`, `test_an_absent_committing_scratch_root_is_not_a_clean_scan`,
builds a fresh worktree with `add_worktree()` and asserts exit 2, `absent; not scanned`, and no
`CLEAN`. It carries no docstring and no stated ground, so it reads as symmetry with its owning twin
at `:234` rather than as a reasoned position.

**A second fixture already knows a state the vocabulary does not.** `:262`,
`test_an_unreadable_peer_root_reports_without_refusing`, constructs its subject with
`shutil.rmtree` on a worktree named `registered-but-gone` — a stale registration — and asserts it
prints `unreadable; never graded`.

**Nothing exercises the failure end to end.** The chain is *fresh worktree, census exit 2, hook ORs
it, commit refused*. `:377` covers the last link with a substring search over the hook text. No test
runs a commit.

**The producer cannot help and that was executed rather than read.** `tools/scratch_work.py:19` is
`repo_root.scratch_root().resolve()` unconditionally, so no argument to it produces a worktree-local
root. `tools/hooks/post-checkout` is on `main`, fires at worktree birth, and repairs the skills
mirror only.

**Live at this base.** `coverage: 42 worktrees enumerated; 0 unreadable`, 2 `GATING` and 40 `REPORT
ONLY`, 26 peers reading `absent; never graded`, and this worktree's own root absent and not scanned.
Exit 2.

**One precedent for the exception, and five counterexamples against generalizing it.**
`tools/subject_ledger.py:156-166` returns 0 for an empty ledger, and its population comes from
`threshold_coverage.parse_registry` rather than from its own matcher. A sweep of all 60 command-line
modules in `tools/` then found matcher-inferred empty populations exiting 0 in `deck_scan.py`
(`grade()` at `:340-348` passes no `coverage_failed` and no `coverage_limbs`, and the module names
`EXIT_2_LIMBS` nowhere), `specificity_scan.py` (`coverage_failed = False` at `:679`, set true only on
the `--second-read` limbs), `harvest_review.py:153-159`, `uspstf_interval_reach.py` and
`uptodate_store.py`.

## Ruled 2026-09-06

### 1. The gate is a two-by-two and the committing-absent cell leaves it

Owning-absent, owning-unreadable and committing-unreadable refuse. **Committing-absent does not.**

*Which root* decides whether emptiness is expected; *absent versus unreadable* decides whether it is
knowable. Both axes are load-bearing and neither is redundant. This is not a new distinction being
introduced — it is the distinction `count_root` already computes being carried one line further,
into the status that currently discards it.

`docs/agents/scratch.md`'s *"A clone with no owning scratch root says did not scan, never clean"*
stays true as written, which is why the owning column is untouched. And
[ADR 0091](0091-the-scratch-ratchet-refuses-only-roots-the-committing-session-can-write-into-and-the-session-directory-is-ticket-keyed-and-produced.md)
ruling 2 already grounds the gate on the refused party being a candidate author: where the committing
root is absent there is no material, so there is no author, so nobody refused is a candidate.

### 2. That opens a delete-to-pass hole, and it is accepted and declared rather than closed

Today a worktree with three unaccounted entries is refused at exit 1, and `rm -rf scratch` moves it
to exit 2 — still refused. Under ruling 1 that same deletion produces exit 0 and `CLEAN`. **The
not-scanned limb was doing a job nobody had credited it with.**

One new `DECLARED_LIMITS` row: a committing root deleted rather than drained reports as one never
created. That is
[ADR 0091](0091-the-scratch-ratchet-refuses-only-roots-the-committing-session-can-write-into-and-the-session-directory-is-ticket-keyed-and-produced.md)
ruling 3's own pattern, where the peer-root hole was stated in `DECLARED_LIMITS` rather than argued
away.

**Two closures were refused as unavailable rather than expensive.** Creating the root at worktree
birth so that a later absence means deletion has no discriminator: a worktree made before the hook
landed, or in a clone with `core.hooksPath` unset, is absent innocently. Making absent-is-clean
conditional on the worktree's age reintroduces the threshold ADR 0091 ruling 1 already refused, on
the same measurement — nothing here grounds the cut point.

**The mitigation is placement, not mechanism.** `do not delete a scratch root to clear this` prints
on the committing-root finding line beside the existing `do not raise OWNING_BASELINE`, which is
ADR 0091 ruling 7's arrangement and its reason: the prohibition belongs at the moment somebody is
blocked, because that is the only moment anybody is tempted. That ruling anticipated a blocked
session reaching for the worst available remedy; it anticipated the wrong one.

### 3. A passing absent root keeps a `GATING:` line and a qualifier, and `CLEAN` prints

`GATING: <root>/scratch: absent; nothing to grade`, and never `0 unaccounted, 0 above baseline`.

**That second form is the trap rather than the tidy option.** It is byte-identical to what a
worktree prints after `mkdir scratch` — the exact string every reproduction on the thread quotes as
its confirming fix — so it would make the report unable to distinguish a root that was walked and
found empty from one that was never created. That is this ticket's own defect moved from the exit
status down into the report, inside the change whose subject is that conflation.

It stays a `GATING:` line because it is still a gating root; it is one that passes. ADR 0091 ruling 7
set that label as the axis of *whether this root can refuse me*, not *whether it did*.

`CLEAN` prints unchanged. *Scratch top levels are within their ratchets* is true of a root with no
top level, and
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s discipline is satisfied by
the qualifier printing on the root's own line on every run.

### 4. The exit-2 path gains a remedy, and owning-absent gets no escape hatch

`REMEDY:` moves out of `if finding:` and gains an exit-2 form with text per state, including the
ruling 2 prohibition on the unreadable cells.

The ticket's decision 2 asked for this because of the fresh-worktree case, which ruling 1 removes
from exit 2 entirely. **It is kept anyway, and delivered to the cases where the refusal is correct.**
The asymmetry was the finding independent of which cell motivated it: exit 1 tells you what to do and
exit 2 tells you nothing, and after ruling 1 exit 2 is only reachable in states a person must act on.

**No hatch for owning-absent, and the `phi_scan` precedent does not transfer.**
`clinical.phiAllowNoCorpus` exists because an absent corpus has no remedy — a clone that legitimately
holds no patient records must still be able to commit. An absent owning scratch root is fixed
completely by one `mkdir`, or by `tools/scratch_work.py`, whose `mkdir(parents=True)` creates it. **A
hatch is for a state you cannot leave; this is a state you leave once**, beside the existing
once-per-clone `git config core.hooksPath tools/hooks`.

### 5. Nothing creates a worktree-local scratch root

`tools/hooks/post-checkout` stays mirror-only and `tools/scratch_work.py` is untouched.

**The measurement is that the report prints one line per root either way.** A peer with an empty root
prints `0 unaccounted; never graded`; one with no root prints `absent; never graded`. Creating the
directory changes the text of a line and never the count of lines, so the signal-to-noise complaint —
the one thing a proactive `mkdir` looked like it would address — is untouched by it.

And it runs the wrong way against a declared hazard.
[ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md)
ruling 5 and ADR 0091 ruling 3 both record that `git worktree remove` takes a scratch root with it
and nothing warns. Creating a root in every new worktree increases the number of roots that can
accumulate material and then be silently destroyed, in exchange for a cosmetic change to a line
nobody grades.

The ticket's own third candidate — a local mode on `scratch_work.py` — is closed rather than left
open. It was measured on the thread, not reasoned: the command was run from a worktree and returned
the owning checkout's path. Giving it a local mode would also put a producer in the business of
creating a root ADR 0091 ruling 4 deliberately routes away from.

### 6. A stale worktree registration gets its own printed state

A worktree deleted without `git worktree prune` stays in `git worktree list --porcelain` and reaches
`count_root`'s `FileNotFoundError`, so it prints as an unreadable root and is named in the coverage
line among roots that could not be read. **It is not unreadable. It is not there, and the fix is
`git worktree prune`.**

The report distinguishes it; the gate still pools it. That is exactly the arrangement `:331-333`
already uses for `absent` versus `unreadable`, applied one state over, and it changes no exit status —
the condition can only reach a peer, since the committing checkout is the one you are standing in and
the owning checkout resolves through its `.git` pointer.

### 7. The exit-status contract becomes a module-owned object

This ruling falsifies the same sentence in two tracked files at once — `docs/agents/scratch.md:73`
and `CLAUDE.md:2156` — and `scratch.md:89` stops being the whole story.
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape arriving as a
demonstration rather than a hypothesis: two hand-kept copies, a prose edit to either fails nothing,
and here they go wrong together, which is the case where drift is invisible because the copies still
agree with each other.

`scratch_census.py` owns the contract; both documents point at it and reproduce no limb; **a test
asserts they point and do not copy.** `EXIT_2_LIMBS` in `differential_scan.py`, `render_scan.py` and
`voice_model_scan.py` is the precedent for the object; `reference_scan.NOT_REACHED` and
`case_study_scan.DECLARED_LIMITS` are the precedent for the pointer-plus-test arrangement.

**Scoped deliberately: the constant and a pointer, not a migration onto `run_grader`.** Those three
modules pass `EXIT_2_LIMBS` into `run_grader.py:361`, where it is validated. `scratch_census` owns
its own `main`. Moving it onto the shared runner may well be worth doing and it is not this ticket.

**The test is the load-bearing half.** A tuple that prose merely happens to agree with today is the
old arrangement in new clothes.

### 8. `CONTEXT.md` gains the three terms this ruling turns on

**Committing checkout**, **Gating root** with peer root as its complement, and **Established empty**.

The first two are pure gap-filling: they appear today only as inline phrases inside **Ratchet** and
**Drain**, while ADR 0091 ruling 7 makes gating-versus-reporting the report's organizing axis and the
command prints it on every line. `Owning checkout` and `Module root` both have entries; `Committing
checkout` is the missing third member of that family.

The third names a distinction the glossary lacked entirely. **Unreadable source** and **Unreadable
body** both name *the subject could not be obtained*; nothing named *there is no subject*. That gap
is the most likely reason the census conflated them — there was no word for the state it was in.

### 9. The empty-population rule is the reasoning here and is deliberately not generalized

The discriminator that makes ruling 1 safe rather than a silenced gate: **an empty population may
pass clean only where the emptiness is established independently of the matcher that would have
recognized a member.** Where the matcher is the only evidence of emptiness, empty must be *did not
scan*, because empty is then indistinguishable from unrecognized. A directory that does not exist
cannot contain something the census failed to recognize; the filesystem, not a matcher, establishes
that.

That is why seven graders correctly exit 2 on an empty population and why `subject_ledger.py`
correctly exits 0.

**It is not ruled repo-wide, and the refusal is recorded because it is the obvious next proposal.**
A sweep of all 60 command-line modules found five that return 0 on a matcher-inferred empty
population. A ratified record asserting a rule five live modules break would be a claim measured
against a tree that contradicts it — this repository's own recurring shape, arriving inside the
record written to prevent it. The `CONTEXT.md` entry therefore *defines* the concept and asserts
nothing about how many modules comply; `CONTEXT.md` is a glossary and not a conformance claim.

The five are filed rather than fixed here, because whether every `run_grader` member must declare a
coverage limb is a decision and not a repair.

### 10. There is no end-to-end test, and that limit is declared where the substring search lives

`tools/hooks/pre-commit` runs seven graders, and `phi_scan.py` is one of them. In a throwaway
checkout there is no corpus, so `phi_scan` exits 2 and the hook refuses **for a different reason than
the one under test**. A test asserting the hook does not refuse would fail on a correct fix; one
asserting it does refuse would pass while the census was right and `phi_scan` was merely corpus-less.

So the end-to-end path is unavailable in a fixture without standing up a fake corpus or stubbing six
unrelated graders, and both make the test assert the harness rather than the hook. `:377` is the
honest instrument and it is reading as more than it is: it proves the hook contains a line, and
nothing about what that line does. Its docstring says so.

That is [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s ruling —
declare the coverage rather than widen the instrument — arriving on a hook instead of on a walk.

## What this record does not settle

**The report's volume.** 40 `REPORT ONLY` lines print on every commit. Ruling 1 removes the acute
instance, since a fresh worktree no longer produces a refusal there is a line to hunt for, but not
the condition. Filed separately. The constraint analysis belongs with it: summarizing is
**available** rather than forbidden, because ADR 0059 ruling 1's naming obligation binds the
`unreadable` set only — under ruling 1 above, an absent root is not one that could not be read — and
the `coverage:` line already discharges it. It trades against #258, not against ADR 0059, and that is
its own grilling.

**Whether every `run_grader` member must declare a coverage limb.** Ruling 9 names five modules that
do not. Filed.

**`harvest_review.py`'s yield-versus-disk test.** `phi_scan.harvest_entries` returns `[]` for a file
that is absent *and* one that will not parse, and says so in its own docstring;
`phi_scan.missing_corpus_sources` tests the disk instead, with the reason stated —
*"the two are not the same claim"*. `harvest_review` tests the yield and prints a claim about the
disk. Found during ruling 9's sweep, adjacent rather than in scope, filed.

**Whether `scratch_census` should move onto `run_grader`.** Ruling 7 is scoped to exclude it.

**What an absent *owning* root obliges beyond the remedy line.** Ruling 4 gives it a remedy; whether a
clone in that state should be able to do anything else is not asked.

**The exact wording after `absent;` in ruling 3**, and the exact per-state remedy strings in ruling 4.
Those are the builder's.
