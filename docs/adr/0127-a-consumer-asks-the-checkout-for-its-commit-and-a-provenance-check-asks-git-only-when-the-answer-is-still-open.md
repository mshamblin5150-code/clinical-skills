# A consumer asks the checkout for its commit and a provenance check asks git only when the answer is still open

[#871](https://github.com/mshamblin5150-code/clinical-skills/issues/871) was filed 2026-09-03 by an
architecture review of the repo-wide gate, reporting that every manifest read re-asks git for `HEAD`
and the working tree's dirty state.

Grilled 2026-09-03. **Nine decisions, ruled by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## Measured before ruling, at `9500e6f`

Freshness gate `FRESH` at the first checkpoint and **`STALE` at the second** — `main` reached
`fcef52f` mid-session, carrying [ADR 0126](0126-the-artifact-lock-is-scoped-per-identity-and-its-rollout-window-is-crossed-by-a-three-limb-compatibility-layer-retired-by-a-derived-condition.md)
and the shared render pass. The gate blocked the publication, the branch was brought forward, and
the figures were re-checked rather than re-asserted: **not one of the six files they read changed
between the two bases** — `artifact_provenance.py`, `guidelines_manifest.py`, `threshold_sheet.py`,
`guidelines_index.py`, `guidelines_recs.py` and `artifact_lock.py` are byte-identical across
`9500e6f..fcef52f`. Every figure below therefore stands at both.

Note that ADR 0126 is the *record* for #870 and not its build, so the `artifact_lock` cost named in
premise 5 below was live in the tree these figures were taken from and is still live today. When
#870's build lands, the non-git remainder of a manifest read shrinks and nothing else here moves.

Every figure below was taken on the grilling machine
rather than the maintainer's, Python 3.14, by wrapping `subprocess.run` and keying a counter on the
git subcommand, over `test_threshold_sheet.RangeGate` — 12 tests, 0 failures in every configuration
run.

**Process counts here are exact and reproduce run to run. Wall times on this machine do not** — the
identical shipped configuration measured between 42.7 s and 58.4 s across five runs. That spread is
wider than several of the differences the ticket reasons from, which is why every ruling below rests
on a process count and none rests on a wall-clock pair.

### Four commands, not the one pair the ticket names

| git command | calls | reached through |
| --- | ---: | --- |
| `merge-base --is-ancestor` | 232 | `_is_checkout_ancestor`, twice per call (`HEAD`, `MERGE_HEAD`) |
| `diff --quiet` | 116 | `_paths_unchanged` |
| `rev-parse HEAD` | 116 | `current_producer` |
| `status --porcelain` | 116 | `current_producer` |
| **total** | **580** | five processes per `guidelines_manifest._read_locked` |

### All five of the ticket's premises are false or incomplete as written

1. *"`git status --porcelain` is the expensive half — it stats the whole working tree, and this
   repo's is large."* `git --version`, which opens no repository, costs **25.2 ms** here.
   `rev-parse HEAD` costs 29.5 ms and `status --porcelain --untracked-files=normal` costs 38.7 ms,
   over 702 files. **The cost is process creation, paid twice per call.** The tree walk is about
   14 ms on top of a 25 ms floor, so "which git command is slow" is the wrong question and "how many
   times is git started" is the right one. This is the correction the whole ADR turns on: it is what
   takes the ticket from a 232-process subject to a 522-process one.

2. *"580 processes for 12 tests … they are asking one question with one answer."* They are asking
   four questions. The pair the ticket names is 232 of the 580.

3. *"Is a process-lifetime cache sound for `dirty`?"* — the ticket's first thing to settle — **has no
   consumer.** `check_producer` calls `current_producer` on exactly one line
   (`artifact_provenance.py:417`) and subscripts `["commit"]`; the `dirty` value that
   `git status` was run to produce is discarded on that same line. The `dirty` that `check_producer`
   acts on (`:460`) is `producer.get("dirty")` — the flag stamped into the artifact when it was
   built. `uspstf_table.py` is named in the ticket as "the case to check rather than assume"; it
   never reads live `dirty`, and it verifies once *before* its write with nothing after.

4. The memoization figure (50.6 s → 32.2 s, an 18.4 s saving) **exceeds the total cost of the two
   commands it memoized**. The same change measures 45.0 s → 35.2 s here. A different machine
   explains a different magnitude, not an internal inconsistency.

5. *"the remainder is file reads rather than process spawns … not diagnosed here and may be a second
   ticket."* It is not a second ticket, it is the same call. `guidelines_manifest._read_locked`
   accounts for **42.3 s of a 43.7 s** instrumented run: the git subprocesses, plus the
   `artifact_lock` acquisition that [#870](https://github.com/mshamblin5150-code/clinical-skills/issues/870)
   is about, plus the JSON parse.

### The configurations measured

Each row is the shipped tree with one change, 12 tests, 0 failures:

| change | manifest reads | processes |
| --- | ---: | ---: |
| as shipped | 116 | 580 |
| stop computing the discarded `dirty` | 116 | 464 |
| `survey` reads the manifest once, not twice | 58 | 290 |
| memoize the three git helpers for the run | 116 | 5 |
| ask git only when the answer is still open | 116 | 232 |
| *(memoize the manifest read for the process — upper bound, never a proposal)* | 1 | 5 |

The last row is recorded because it bounds the whole problem, not because anyone proposed it: a
manifest can change on disk during a run, which is exactly what `artifact_lock` exists to
coordinate.

## Decision 1 — the ticket is re-scoped from a cache to a set of deletions

**Ruled: re-scoped.** The ticket asks whether a cache is sound. Three of the four repetitions it
was filed over are not repetitions that need remembering — they are work computed before the guard
that makes it irrelevant, and the remedy is to not compute it.

## Decision 2 — the duplicated manifest read is its own ticket

`threshold_sheet.survey` reads the same manifest twice, thirty lines apart, for two fields of one
object: `:3278` through `extraction_identity_from_manifest` for `handoff.provenance.producer`, and
`:3309` through `gate_watermark` for `handoff.documents`. Same root, same
`allow_untrusted_provenance`, nothing between them writes the file. Reading once eagerly in `survey`
adds no read, because the identity call already reads unconditionally whenever `text_root is not
None`, which is the only case in which `gate_watermark` would have read at all.

**Ruled: its own ticket, filed with these numbers.** It is a different module and a different seam,
it needs no ruling from #871 to be correct, and it must be priced before the rest, because every
figure #871 reasons from is written against 580 processes and the honest denominator after it is
**290**.

## Decision 3 — a consumer asks the checkout for its commit

`check_producer` is a **consumer**. It called `current_producer` — documented as *"the commit and
dirty state of the checkout running a producer"* — to learn its own commit, and took a
`git status --porcelain` it never wanted as the price of asking.

**Ruled: split, and name the new function for the question the consumer is asking.**
`checkout_commit(repo_root) -> str` runs one `rev-parse`. `current_producer` calls it and adds
`dirty`, and keeps `dirty` for producers alone. Not `current_commit`: the caller is not producing
anything, and it is the producer framing that hid the defect.

A keyword flag on `current_producer` was refused. It is the smallest diff and it leaves the wrong
question being asked under a quieter name.

## Decision 4 — the commit is supplied by the command, and the parameter is required

**Ruled: required, through the whole chain.** No default on `check_producer`, `_read_locked`, `read`
or `read_or_raise`. Each command computes `checkout_commit(repo_root)` once in `main` and passes it
down as the `expected_commit` these signatures already carry and that `guidelines_index.py:319`
already supplies.

One `rev-parse` per run then follows from the signatures rather than from anyone's diligence, with
**no cache, no lifetime and nothing for a test to reset** — the lifetime lands where it is true, since
a command knows how long its own run is and a module-level dict has to be told.

Threading by convention with an optional parameter was refused: a caller who omits it pays two git
calls and **nothing fails**, which is how the present cost arrived. An AST walk asserting no call
site omits it was also refused — this repository has twice recorded that such a walk cannot see a
call built by indirection or reached through a wrapper, so it reports that the defect has not
arrived rather than that it cannot.

The price is named rather than discovered: `read_or_raise` stops being the wrapper you can call
without knowing which checkout you are reading against, and that is precisely the convenience that
turned out to be expensive. Its four command call sites each gain one line in a `main` they already
have.

## Decision 5 — git runs only when the answer is still open

`check_producer` builds `unchanged_ancestor` eagerly, and evaluates
`not _paths_unchanged("HEAD", …)` to the left of the `inputs_match is not True` test that can make
it irrelevant. So `merge-base` and `diff` run when the artifact's commit already equals the
checkout's, and when a content-addressed stamp has already matched by hash. It is the same defect as
the discarded `dirty`, twice more.

**Ruled: reordered so git is asked only after the in-memory tests leave the answer open.** The truth
value is unchanged — these are pure reads and `and` is commutative over booleans — so this is a
reordering and not a rule change.

Measured: `RangeGate` **580 → 232** processes, every `merge-base` and `diff` gone, 12 tests, 0
failures. Over the modules that exercise the provenance branches rather than the gate —
`test_artifact_provenance` and `test_guidelines_manifest`, 69 tests, 0 failures — the same
reordering with decision 3 gives **99 → 72**, with `merge-base` at 6 and `diff` at 9 rather than 0.
The branches are still reached; the calls that went are the ones nothing read.

## Decision 6 — the cost is asserted, with a positive control

Two of the three landings defend themselves: a required parameter cannot be forgotten. **The
reordering is just code**, and a later tidy back into eager `and` chains restores 348 processes with
every test green, because nothing in this repository has ever measured what a check costs — which is
how the discarded `dirty` survived for as long as `check_producer` has existed.

**Ruled: assert it, both halves.** A test counts git subprocesses and asserts that verifying a stamp
whose `inputs` match the checkout, with `expected_commit` supplied, spawns **zero** git processes —
and a positive control asserts the merge-parent path still spawns them.

The positive control is not optional. A zero-process assertion passes just as well when the guards
have gone unreachable as when they are correctly skipped, and *a check that could not have seen the
thing it was named for* is the failure this repository has recorded more often than any other,
including once inside the fix for it.

## Decision 7 — no per-process cache of a git answer

**Ruled: not built, and recorded rather than dropped in silence.**

The reordering takes the cache's subject away in the measured workload but not in every workload. It
skips `merge-base` and `diff` when the artifact's commit equals the checkout's **or** when
`inputs_match is True`, which is the content-addressed case, so modern builds skip. It does not skip
for a legacy stamp recording no `inputs`: there a run reading N artifacts asks the same `merge-base`
and `diff` N times, and a per-run cache would still collapse them. **That workload has not been
measured here**, and this repository does not build a mechanism against an unmeasured workload.

Three findings stand behind the refusal, and they are recorded because the next reader of
`check_producer` will otherwise re-derive them:

- **Nothing in `tools/` verifies, writes into the checkout, then verifies again.** `uspstf_table.py`
  is the only command that writes a git-tracked path, and it writes after its single verification
  and returns. `guidelines_build`, `guidelines_index` and `implementation_map` write outside every
  checkout by construction.
- **A cache would be observable by two test seams.** `test_artifact_provenance.py:104` calls
  `check_producer` twice on one `repo_root` with a producer-file rewrite between them.
  `test_guidelines.py:315` patches only `current_producer`, so `_paths_unchanged` and
  `_is_checkout_ancestor` there still shell against the live worktree — a cache not keyed on
  `repo_root` would collide those with `MergeParentTrustTests`' throwaway repositories. The
  cross-process handoff tests in `test_guidelines.ProducerEditHandoffTests` would survive a
  per-process memo and would not survive an on-disk one.
- **There is no precedent.** No ADR and nothing in `CONTEXT.md` rules on caching a git answer for
  the life of a process, and `repo_root.py:64` records the opposite instinct in as many words —
  *"No subprocess, deliberately."*

## Decision 8 — one ADR, and `CONTEXT.md` gains the term pair

**Ruled: one ADR, and two terms.** The defect is a terminology collision in the plainest form this
repository has seen: `check_producer` called `current_producer` to learn its own commit, and the
name is why nobody noticed a consumer was asking a producer's question. `CONTEXT.md` had a term for
neither. **Checkout commit** and **Producer commit** land under *Artifacts*, each naming the other
in its `_Avoid_` line so the collision is recorded rather than left to be made again.

**No prose figure goes into `CLAUDE.md`.** The 25 ms process floor is a dated measurement on one
machine, so it belongs here where it is dated. The durable form of it is decision 6's test, which
re-derives the property on every run rather than asserting a number nothing recomputes.

## Decision 9 — two build tickets, the reordering first

**Ruled: split, reordering first.** The two landings are orthogonal — the seam removes `status` and
collapses `rev-parse`, the reordering removes `merge-base` and `diff`, and neither moves the other's
denominator:

| | processes | what remains |
| --- | ---: | --- |
| as shipped | 580 | 116 `rev-parse`, 116 `status`, 232 `merge-base`, 116 `diff` |
| seam only (decisions 3–4) | 406 | 58 `rev-parse`, 232 `merge-base`, 116 `diff` |
| reordering only (decisions 5–6) | 232 | 116 `rev-parse`, 116 `status` |
| both | **58** | 58 `rev-parse`, one per command run |

They are opposite in shape. The seam is a small change with churn across seven call sites in five
modules plus every test that omits `expected_commit`; the reordering is a reordering inside one
function. **The smaller one is the bigger win** — 348 processes against 174 — so bundling makes the
larger win wait behind the larger review. The reordering landing first also means the zero-process
assertion and its positive control are already in the tree when the seam change arrives, so the seam
lands against a test that measures exactly what it changes.

Splitting decision 3 from decision 4 was refused: decision 4 deletes `check_producer`'s fallback,
which is what gives `checkout_commit` a caller at all, so separating them lands a function with no
purpose for one merge.

## What this does not reach

**A clean provenance check is not a checked artifact.** Nothing here changes what the verification
concludes; every decision is about how many times it asks. The ownership ruling
[#184](https://github.com/mshamblin5150-code/clinical-skills/issues/184) rests on is untouched, and
that is the ticket's own *what must not come out of this*.

**The legacy-stamp residual in decision 7 is unmeasured**, not absent. It is stated as a shape with
its two test seams named, so whoever meets the volume starts from the measurement rather than
re-deriving it.

**One live staleness of exactly the kind the ticket feared is already in the tree, on a different
file, and is not #871's.** `TRUST_FLOOR["recs"]` contains `reference/guidelines-uspstf.md`, which
`uspstf_table.py` writes — and `guidelines_recs.py:1199` caches that file's parsed contents for the
life of the process with no reset the module offers. Filed separately.

**Every wall-clock figure in the originating ticket is retained rather than corrected.** The
machines differ and the ticket's measurements were honestly taken; what is corrected is the
attribution built on them.
