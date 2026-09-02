# The implementation map is reconciled by an in-tree tool rather than gated at publication

[#756](https://github.com/mshamblin5150-code/clinical-skills/issues/756) was grilled after the
clinician reported two things in one sentence: the map's Mermaid graph no longer times out, and a
ticket that gains `ready-for-agent` does not reach the map without him editing its state block by
hand. The first retired the ticket's premise; the second opened a requirement the ticket never
carried.

The obvious remedy was available and is refused here. `tracker_publish_hook.PUBLISH_ROUTES` already
contains `("issue", "edit")` and `("issue", "create")`, so every label flip this repository performs
already crosses a pre-publication boundary that could refuse it. That gate is not built, for reasons
measured during the grilling rather than reasoned from taste.

This ADR records how the map is produced. [ADR 0108](0108-the-map-graph-draws-dependency-alone-and-the-render-is-declared-rather-than-bounded.md)
records what it draws and [ADR 0107](0107-a-collision-group-is-a-sequence-or-an-exclusion-and-an-unclassified-one-over-constrains.md)
records what its collision groups mean. It extends
[ADR 0089](0089-the-map-gate-is-an-offline-grader-over-a-harvest-and-the-reconciliation-obligation-is-anchored-on-a-field-the-delta-sets.md),
which built `map_scan.py` and the `reconciled_through` anchor, and does not disturb
[ADR 0090](0090-the-readiness-refusal-lands-at-the-claim-rather-than-at-the-push-and-startability-and-readiness-stay-two-derived-properties.md).

## Measured before ruling, at `1f1c645`

Freshness gate `FRESH` at both checkpoints. Every figure below is dated and scoped to that base;
the tracker figures are re-derived from #596's body as of `2026-09-01T22:42:56Z` and move on the
next rebuild.

**The helper is not out of tree; it is gone.** `git ls-files` matches nothing, which #756 already
recorded. It is also absent from every registered worktree searched at depth 3, from `scratch/` at
any depth by name, and from every `.py` in the owning checkout carrying the
`implementation-map:v1:state` marker — every such hit is `map_scan.py`, `test_map_scan.py`, or one
grilling session's throwaway measurement script. The only trace is an empty drained directory,
`scratch/runs/drained-363c-20260829-.../implementation-map-20260829-.../`.

**#596 was nevertheless rebuilt during the grilling**, at `22:42Z`, between two tracker sweeps that
read 87 nodes and a read that found 90. So the page is being maintained by a process nothing in the
tree describes, while its own preamble says *do not hand-edit; use `implementation_map.py`*.

**ADR 0089 describes that helper in detail** — a `GitHub` class whose methods are `issues`,
`blocked_by`, `get_issue`, `update_issue_body` and `create_issue`, plus `validate_against_live`,
`packet_status`, and a `check` subcommand. **The rebuild should be planned as a rewrite**, with ADR
0089's description of the seam as the closest surviving specification.

**A search by symbol across every scratch root confirms it**, with a live control: over the 10
scratch roots this checkout and its worktrees own — 21 `.py` files reachable, which is the control —
none of `update_issue_body`, `validate_against_live` or `collision_groups` appears. Those roots are
where session-local scripts actually live, and the first attempt at this search missed them by
reading only the owning checkout's `scratch/`, which is
[ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md)'s
*one root per checkout* catching the instrument built to look for the tool.

**A machine-wide search was attempted twice and never completed**, so no negative is claimed from
it: the first run's exit status was `head`'s rather than `grep`'s, and a rerun carrying a control
pattern exceeded its time bound before the control printed. **The bound on all of this is that every
completed search is keyed on a filename or on one of four symbols.** If the helper survives outside
a scratch root under a different name and a different symbol set, the *rewrite* framing is wrong and
recovery is cheaper than the build — worth one look before the work starts rather than a conclusion
recorded here.

**Detection already existed and was already running.** `map_scan.scan` emits
`Finding("unmapped-ready", ...)` for a ticket carrying a `ready_labels` label that sits in no packet
and no `exclusions` entry. `.github/workflows/checks.yml` runs `map_scan.py --advisory` on every
push to `main` and on `workflow_dispatch`, printing the report into the step summary. So the map has
been reporting this defect on every push, converted to exit 0, inside a green check.

**The gate cannot cover the routes the label actually arrives by.** The clinician named three — a
tracker sweep, the end of a grilling session, and filing a ticket already labeled. For
`issue edit --add-label` a gate can check that #596 already carries a packet for that ticket. For
`issue create --label` it **cannot**: GitHub assigns the number on creation, so no packet can
pre-exist. And `tracker_publish_hook.NOT_REACHED` already declares that the GitHub web UI never
crosses the hook at all. A gate would therefore cover one of four routes while reading as
prevention.

**The glossary had already ruled the shape.** `CONTEXT.md`'s **Reconciliation** entry defines the
operation as *"the reviewed judgment that places changed work into the map — written as a delta,
reviewed against the ADR's rulings, then applied. It is semantic and cannot be derived"*, names it
*"distinct from a **publish**, which re-renders the derived views from unchanged state and
reconciles nothing"*, and lists `sync` among its _Avoid_ terms. The session's first proposal was a
single command named `sync`, and the glossary refused all three of its properties.

## Ruled 2026-09-01

### 1. `tools/implementation_map.py` comes in tree

A derived view with no committed deriver is a hand-maintained artifact wearing a machine's clothes,
and readers extend it the trust the word *derived* buys. The map's whole standing rests on that
word: it is what lets the preamble say native blocked-by is authoritative and this page gets
rebuilt.

Leaving it out of tree and correcting the preamble to say so was considered and refused. It is
honest and it retires the artifact's value while leaving the artifact standing — a page that still
looks like a graph of authoritative state and now says nobody checked it. Retiring the derived block
entirely was preferred to that, and refused only because `collision_groups` is authored, is not
recoverable from GitHub, and is the one thing on the page GitHub cannot tell you.

### 2. Reconcile after, never gate at publication

The gate is refused on three grounds, in order of weight: it cannot cover `issue create --label`
because the ticket number does not exist yet; it cannot cover the web UI, already declared in
`tracker_publish_hook.NOT_REACHED`; and it contradicts `reconciled_through`, which exists precisely
to say how far behind the map is rather than to assert it is never behind.

Reconciliation is **route-blind**. It does not care whether the label arrived by create, by edit, by
sweep, by grilling, or by a browser click. That is the property a gate cannot have, and it is worth
more here than prevention.

### 3. Two subcommands, and the split is the glossary's

`reconcile` applies a delta and may advance the anchor. `publish` re-renders every derived view from
unchanged state and advances nothing. `reconcile` publishes as its last step; `publish` alone is
safe to run from anywhere, including CI.

Deduplicating drawn edges is a **publish** concern. Authoring a packet's `outcome` is a
**reconcile** concern. Nothing that requires judgment lives in `publish`.

### 4. A publish never advances the anchor, and a reconcile advances it only when nothing is left unmapped

`reconciled_through` is a claim of currency that `map_scan` grades ADRs against. A run that stamps a
fresh anchor while a ready ticket is still unmapped has published a map asserting it is current when
it is not — the repository's recurring shape landing on the one field whose entire job is to say how
stale the page is.

### 5. `reconcile` refuses to write a blank `outcome`

The clinician ruled this directly. A packet's `outcome` is authored judgment and a guessed one is
worse than a blank one, which is `guidelines_catalog.py --draft`'s rule arriving on the map. What
the command removes is the JSON surgery, the edge derivation, the re-render and the publish — never
the judgment.

The session first proposed auto-inserting a stub with an empty `outcome` on the argument that the
`outcome` is unknowable at flip time. That argument was wrong and is recorded because it is
plausible: on both routes the clinician named, the flip is performed by the agent that has *just*
ruled the packet, so the flip is the moment the `outcome` is most knowable.

### 6. Idempotent, with the denominator on every run

`reconcile` is additive for new tickets and inert for mapped ones, so it may be run repeatedly and
by anything. Every run prints packets written, ready tickets still unmapped, and where the anchor
stands — whether or not the unmapped count is zero. That is the extractor-coverage rule: report the
denominator and the unread remainder, and never present an incomplete read as clean.

### 7. A local lock and a state-block hash, and a refused write emits what it was about to write

Both, because each is weak alone. The lock is #276's arrangement — nonblocking, keyed on the
artifact, under the operating system's temporary directory — and it covers the observed failure
completely, because every session that has touched this map runs on one machine. It is also the half
that can be wrong: a crashed process, an unreachable temp directory, a write from a browser.

The hash is the half that cannot be fooled. It covers **the state block only**, not the rendered
halves, which are derived and differ after every publish — so two publishes never conflict and two
reconciles always do, which is the correct split.

A refused write must emit its authored `outcome` somewhere durable before returning. The judgment
was typed in a session; refusing without emitting it destroys work that exists nowhere else. That is
`docx_write`'s recorded lesson that `--force` is a promise and not a backup, applied before it can
bite rather than after.

### 8. `unmapped-ready` leaves `--advisory`

The finding has been printed inside a green check on every push. A detector whose report is
invisible is the written instruction this repository keeps ruling insufficient, wearing a scanner's
clothes.

## What this does not reach

The lock is local, so two machines remain uncoordinated; the hash is what covers them, and it
refuses rather than prevents. Nothing here establishes that a reconciliation's placement is
*correct* — `Reconciliation` is defined as semantic judgment, and a clean run means an authored
delta was applied, never that it was the right one. Nothing here grades the `outcome` prose beyond
requiring it to be non-empty, so a stock sentence satisfies it, which is `specificity_scan.py`'s
substance limit inherited whole. And the routes remain uncovered in the sense the gate would have
covered them: a ready ticket is unmapped from the moment of the flip until the next reconciliation,
and the map says so through its anchor rather than being prevented from entering that state.
