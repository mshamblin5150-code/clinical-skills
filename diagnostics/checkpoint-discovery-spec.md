# Fixed-checkpoint discovery and behavior diagnostic

Status: local preparation for separate Spec and Standards review. Publication,
the single hosted attempt, PR/merge, production adoption and any larger run remain
held. This specification applies only to the new checkpoint-discovery route.
It does not reactivate or repin any historical qualification route.

## Immutable source and distinct route

- Application source: `08db6360b453c2bf969a686f62f0477184d06351`, never moving main.
- Baseline target SHA-256: `b3f804165e04ae0534c36882de699b7ae84e7ebb1df899539497ef1f6a97900c`.
- Candidate target SHA-256: `f2f97e56313d7f8957bec0bd20fd91c9efd8c48c44871c5c69056eb830d43275`.
- The same reviewed lazy-only bytes replace only `tools/test_suite_ids.py` in the
  candidate's disposable workfile. The helper, other application code, tests,
  clinical policy, lock behavior and production workflow are not modified.
- Entrypoint: `diagnostics/diagnose_checkpoint_discovery.py`. The dedicated
  `ci-checkpoint-discovery.yml` accepts only a first-attempt push to
  `diagnostic/2013-parallel-proof-20261020`, one Windows/Python 3.14.4 job.
  There is no dispatch, matrix, downstream job, artifact upload or automatic retry.
- The observer's exact changed-path set against the historical observer base is
  the historical allowlist plus the five new checkpoint files. The historical
  full-pair/lazy entrypoints retain their original 104ee03c pin and scope, so the
  new packet does not satisfy their scope gate. They have no new-pin option.
  Explicit source-pin arguments are diagnostic helper seams only; the new route
  supplies the immutable constant, never a user or environment revision.

## Whole-job budget and retained ownership

The workflow has a hard 600-second runner limit. Its first step records the job
budget origin before checkout/setup. Elapsed setup time is deducted from that
origin; new work stops at origin plus 540 seconds, leaving 60 seconds inside the
same envelope for owned process cleanup. Invalid/future/nonfinite clocks or an
already consumed work window refuse. There is no 4,200-second admission, timeout
extension, borrowed cleanup time, per-test/lock timeout change or promise that
the packet fits. The platform timeout remains an independent hard stop.

All Git, setup, controls and discovery subprocesses use the existing Windows Job
owner. Serial commands return only after the owned tree is reaped and empty.
The existing 1 GiB free-space reserve and 16 MiB per-capture bound remain.
Final cleanup retains every owner and its evidence, limits each cancellation to
the lesser of five seconds and the original hard deadline's remaining time,
and cannot report success after that deadline. Unverified cleanup is inconclusive.
Process cleanup is not proof of complete runner teardown or erased artifacts.

## Exact execution boundary

1. Verify observer scope and first clean status, exact seed HEAD and first status,
   then raw Git tree/blob identities for every source file. Check the unchanged
   original target and reviewed candidate hashes and the exact budget contract.
2. Run the existing nine native ownership controls, five retained-output controls
   and 41 generated-output contract controls. Original validators and all native
   metadata protections remain unchanged; no skip/failure waiver is added.
3. Allocate a fresh short sibling of the canonical workflow workspace, outside
   actual TEMP/TMP/gettempdir, disjoint from observer, seed and owner captures.
   Preserve the existing nonreparse ancestry and UTF-16 path-length gates.
4. Prepare and finish baseline, then prepare and finish candidate. Each is a fresh
   independent full-history clone, detached at the fixed source, with unchanged
   index and finite source-only refs. Conversion is disabled before checkout.
   First status is never repaired or retried into acceptance. Candidate bytes
   are applied only after that first clean status and original inventory.
5. For each arm, validate unchanged TEMP and the unchanged source hook's location
   judgment. Run the same six actual-method lazy-message controls. Baseline must
   have exactly the two named deliberate failures in the existing classifier;
   candidate must pass all six. Arbitrary baseline failures are not accepted.
6. Preserve the existing one junction and four synthetic writer selectors on each
   arm, as the unchanged prior precommand control group. These are explicitly
   selected safety controls, not execution of a newly discovered population.
   They establish neither new contention reproduction nor a lock repair.
7. Discover the complete application population in one fresh child using the
   independent unittest walker, then in a second fresh child using the pinned
   suite's actual-object walker and unit grouper. Neither discovery child runs
   discovered bodies. Require no loader errors, unique IDs and unit names, and
   an exact partition of the discovered objects into units. Compare the
   independent count/digest and target-module count to the actual-object result.
8. Require the actual `test_medatrax_fill.FillCommand` unit to contain exactly the
   twelve reviewed methods in `NEW_METHODS`, with no extra IDs from that module.
   The observed 8,487 baseline count from fixed-checkpoint main-push
   [run 39644301218](https://github.com/mshamblin5150-code/clinical-skills/actions/runs/39644301218)
   is corroborated, not inferred by adding twelve to an old count. Unit count and
   digests are measured, not copied from the old population. Full sorted ID and
   unit-name tuples must match exactly between baseline and candidate.
9. Before and after every subsequent phase, recheck observer/seed raw bytes,
   index and refs, unchanged environment, and every prepared clone's exact source,
   detached HEAD and source-only refs. Use the complete native output scanner in
   the pre-suite state: marker absent, weights absent, sessions optional but empty
   if present. The final identity comparison is also bracketed by these guards.

The explicit control group is `JUNCTION` and the four `SYNTHETIC_SELECTORS` in the
unchanged lazy harness. No twelve new Medatrax bodies, timed three-test target
module, unfiltered suite, database-reader audit, other interpreter lane, profiler
or concurrency-repair experiment is run. Imports are real execution and may
write temporary state; zero discovered-body execution is not a no-write claim.

## Integrity, privacy and interpretation

The generated-output contract is byte-identical to the reviewed prior packet:
raw-object source checks, native actual ChangeTime, all eight metadata fields,
access/sharing flags, the two additional identity handles, safe-read identity,
link/reparse/hardlink/race refusals and cleanup ownership are not relaxed. Unknown
output still refuses. No source, lock override, TEMP setting or private corpus
is substituted to make a gate pass.

Complete identity lists and raw child output remain bounded private captures.
Public receipts contain only finite phases, outcomes, counts, digests and vetted
reason categories. They retain completed arm identity when a later phase fails;
unknown exception text, fixture contents and paths are never forwarded. A pass
requires both exact identities, the expected behavior controls, every source and
output guard, unchanged environment, verified process cleanup and remaining hard
budget. Otherwise the result is inconclusive, with no automatic follow-on.

Success qualifies only this checkpoint's observed import/discovery identities,
controlled lazy-message behavior and containment checks. It is not current-pin
whole-suite correctness/performance, zero-skip or live portal proof, clinical
corpus coverage, adoption permission, lock repair or independent teardown proof.
The historical single-pair 27.29% suite-owned-wall reduction remains evidence
only for 104ee03c. It is not transferred to this checkpoint or pooled with other
measurements. Product, clinical, security/data and teardown holds remain.

## Preparation evidence

Portable tests exercise the dedicated route, setup/cleanup budgets, preserved
historical pin defaults, genuine synthetic Git history, independent identity
corruption, actual-object membership and body-free child discovery. These are
local Linux/Python controls, not Windows or real-08db runtime qualification.
The real fixed-checkpoint discovery is the separately approved future diagnostic.
The author receipt preserves sequential RED/GREEN logs and exact final tree/file
counts for independent review. No broad workflow-completion claim is made.

The established diagnostic branch is reused; no new branch is part of this packet.
The historical full-pair workflow excludes every push branch and tag with exact
`branches-ignore: ['**']` and `tags-ignore: ['**']` filters. Its job definitions,
source pin, entrypoint and budget remain dormant historical source. Thus a later
approved publication on the established branch cannot activate both diagnostics.
