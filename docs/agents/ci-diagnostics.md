# CI diagnostic receipts

The checks workflow still runs every existing check and the complete suite in
each existing job. Classification is observational: `CANDIDATE` is a strict,
identified first-attempt title/body edit; every other event is `FULL`. Neither
value controls execution. Candidate identity also requires checkout/event/merge
agreement, matching base/head parents, workflow and source digests, run identity,
and runtime identity. Missing or inconsistent identity yields `FULL`.
The edited-event shape is pinned to
[Octokit's schema](https://github.com/octokit/webhooks/blob/aa80c24a3f55354465b8b1438d33dd5602956d0d/payload-schemas/api.github.com/pull_request/edited.schema.json).

Each suite step opts into a versioned JSON receipt through
`CI_DIAGNOSTIC_RECEIPT`. Its byte ceiling is `ci_diagnostics.MAX_BYTES`, enforced
before writing. Each job uploads only its named JSON file with explicit short
retention. There is no prior-run lookup or reuse decision. Receipts are evidence
for considering future changes, not evidence that a speedup is safe.

Provenance contains validated commit hashes, source digests, run identity, and
machine/runtime labels. Missing values remain null. Suite measurements come from
the runner's existing discovery, reports, accounting, timing and exit decision.
`mode: full` describes the requested execution; `full_suite_execution` is true
only when discovery is nonempty and accounting is complete. A failing assertion
can have complete accounting and exit 1. Loader failures, missing workers,
duplicate IDs, and empty discovery prevent a complete-execution claim.

Receipts contain counts, not test output or fixture error text. Population and
class identities are SHA-256 hashes of the runner's discovered IDs and class
names, respectively. The population hashes the JSON-encoded sorted ID list;
each class hashes its UTF-8 name. Class hashes can be joined to that checkout's
discovery for analysis without retaining arbitrary test names in the artifact.
Only the bounded slowest classes are included. Existing stdout remains unchanged.

A receipt failure emits a fixed diagnostic and preserves the suite's exit
status. An absent artifact means unavailable evidence, including an execution
that never reached the receipt seam; it never means tests passed. The receipt's
exit is the suite exit, not the final result of other workflow checks. The
receipt does not independently attest that its checkout or runner is trusted.
