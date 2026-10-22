# One current-checkpoint maintainer pair

## Scope and authority

The clinician approved one matched baseline/candidate comparison on 2026-10-22,
after being told the fixed source, existing temporary branch, total runner cap,
passing-baseline gate, and exclusions. This packet prepares that comparison only.
Publication follows independent review. It authorizes no automatic rerun,
production adoption, PR, merge, production parallelism, or canary change.

The immutable application source is
`08db6360b453c2bf969a686f62f0477184d06351`. The observer comes from the reviewed
publication commit, never an arbitrary revision argument or environment override.
The existing temporary branch is `diagnostic/2013-parallel-proof-20261020`.
Only `ci-parallel-proof.yml` accepts push events on that branch; its jobs reject
rerun attempts. Discovery's branch and tag push routes are disabled so the
publication cannot start an extra job. The coordinator publishes only the one
approved launch; the push trigger is not a persistent one-shot lock.

## Admission and matched work

One baseline precedes one conditional candidate. Each job has the existing
90-minute cap, including setup, with 300 seconds reserved for owned-process
cleanup. The maximum is 180 runner-minutes, not an estimate of completion time.
The existing 4,200-second remaining-work admission estimate stays an estimate.
Expired work or hard cleanup budget cannot publish permission to continue.
Python remains 3.14.4 on Windows with the unchanged default worker topology.
No test timeout, test selection, worker override, or extra concurrent arm is added.

The candidate job requires baseline job success and both passing/safe outputs.
Before publishing those outputs, the baseline validates its complete bounded
receipt. The candidate independently validates the same receipt before creating
an owner session. It binds the fixed source, exact observer commit and workflow
run, environment, discovery, behavior controls, all commands in order, complete
native accounting, raw-source/output integrity, owned cleanup and hard budget.
Missing, duplicate, stale, malformed or partial evidence refuses. A failed
baseline cannot fund a candidate even if its original nonzero exit was accounted.

The receipt's complete environment/image schema, Windows/X64 and Python 3.14.4
pins, bounded image values and interpreter-build digest are validated. The full
candidate environment must match before any owner directory or session exists.
All native accounting fields are retained, including finite timing values,
critical-unit token and the explicit limits on skip/expected-failure reporting.

Both arms invoke the same unfiltered commands in the original order:

1. `python tools/phi_scan.py --layers --all`
2. `python tools/suite.py`
3. `python tools/tracker_measurements.py`
4. `python tools/threshold_sheet.py --all`
5. `python tools/phi_scan.py --all --allow-no-corpus`

The original always-after-suite ancillary behavior remains for ordinary nonzero
command exits. Ownership, source, output, accounting and deadline violations
still stop immediately. Both fresh clones require no initial weights and equal
native weights. Native suite accounting is not an independent executed-ID
manifest and does not separately expose aggregate skips or expected failures.

## Source and output boundary

Keep the existing raw Git-object oracle, strict first-status-before-repair rule,
full source history, detached HEAD, exact ref allowlist, native metadata and
source-byte checks. The only candidate delta remains `tools/test_suite_ids.py`:
SHA-256 `f2f97e56313d7f8957bec0bd20fd91c9efd8c48c44871c5c69056eb830d43275`.
The original module remains
`b3f804165e04ae0534c36882de699b7ae84e7ebb1df899539497ef1f6a97900c`.
No lazy target, hook, suite, clinical content or application file is changed here.

Each arm retains the validated short fresh workspace sibling outside actual
TEMP, no hardlinked/shared clones, unchanged environment, original hook-location
check, owner controls, retained-output controls, native generated-contract
controls, actual-method behavior controls, junction selector and synthetic writer
selectors. Raw observer and seed sources/refs and their output contracts are
checked between phases, as is the measured clone's current required output state.
All private raw captures and disposable clones stay on the runner. Process
cleanup verification does not claim capture erasure or complete runner teardown.

## Population and historical evidence

The completed discovery-only [run 39752292249](https://github.com/mshamblin5150-code/clinical-skills/actions/runs/39752292249)
on 2026-10-22 established the fixed checkpoint's expected discovery identity.
`CURRENT_POPULATION` retains that immutable receipt's counts and digests, not a
new full-suite pass claim. Each proposed arm re-derives independent IDs and actual
TestCase grouping, verifies every new Medatrax method, checks the exact stored
identity, and compares both arms. No discovered body is credited merely for
being listed; the complete maintainer suite must subsequently account for it.

Historical `104ee03c` proof code, budget documents and run records remain
historical. Their pins and byte hashes are not rewritten into current-source
evidence. Discovery alone does not establish current full-suite correctness or
performance. This one pair can reveal a current-source regression and provide a
diagnostic timing observation; it cannot prove stable speedup, all-interpreter
compatibility, production-event compatibility, or adoption readiness.

## Local checks and review

Use only bounded synthetic diagnostic tests locally, never the full application
suite. The agreed seams are fixed source/runtime and route admission, complete
receipt/population, source safety, unchanged maintainer commands, native accounting,
output contracts and candidate spending gate. Tests first observed route, stale
receipt, source/input, cleanup and output-publication failures, then passed after
the minimal implementation slices. Existing diagnostic controls remain in the
population, with obsolete active-route assertions updated, not removed.

Matt Pocock TDD and code-review skills are the implementation/review workflow.
Independent Standards and Spec axes review the frozen patch against its local
base equivalent to published `9da2586f51ae1491751f3421a7c50adbeb620cd0`.
Author-run tests are not a substitute for those non-authoring checks.

P-Stack v0.15.9 evidence principles were read from the preserved collection at
commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`, archive SHA-256
`710848a07df97788a7dccdbb1905bb3b39a918ac195566318545074346220d41`, after verifying
every manifest entry. Applied principles are benchmark-checklist,
explain-the-number, prove-it-works, sequence-verifiable-units and
test-behavior-not-implementation. Their repetition/limiter requirements remain
unmet by an authorized single pair. No extra profiling or repetitions are added
to satisfy them, and no upstream script was executed.
