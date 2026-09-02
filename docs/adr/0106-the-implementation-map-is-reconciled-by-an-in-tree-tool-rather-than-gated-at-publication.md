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
the tracker figures are re-derived from #596's body as of `2026-09-02T00:21:08Z` and move on the
next rebuild.

**The helper is out of tree and it is alive.** It lives at
`~/.agents/skills/implementation-map/scripts/implementation_map.py` — 1,338 lines beside a 47 KB
test module — with subcommands `init`, `check`, `claim`, `render`, `publish`, `apply-delta` and
`audit`. `git ls-files` matches nothing, which is #756's true and narrow claim, and which says
nothing about a file outside the checkout.

**This section first recorded it as *gone*, and the correction is the finding rather than an
embarrassment.** The searches run during the grilling covered every registered worktree at depth 3
by filename, every `scratch/` root at any depth by filename, and every `.py` across the 10 scratch
roots this checkout and its worktrees own for `update_issue_body`, `validate_against_live` and
`collision_groups` — with a live control of 21 reachable files. All of them were clean, and **none
of them looked under `~/.agents/`.** Two attempts at a machine-wide search never completed, one
because a pipeline returned `head`'s exit status rather than `grep`'s. **A search that could not
reach its subject, answering like a settled negative** — this repository's most-recorded shape,
arriving four times inside one grilling and once more in the record of it.

**It was caught by a merge and not by a reader.** `main` moved between this session's two freshness
checkpoints, and the commit that landed —
[#728](https://github.com/mshamblin5150-code/clinical-skills/issues/728)'s `1cd40e1` — withdraws the
same false claim from
[ADR 0104](0104-the-freshness-gate-s-subject-is-the-commit-base-and-a-publication-s-cited-records-are-read-back-without-a-baseline.md),
having found the file the same way. **Two sessions published the same untrue negative about the same
file on the same day**, from different instruments, and the second learned it only because the gate
refused a stale base. That is [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s
*the merge is the unguarded moment* arriving as a correction rather than as a breakage.

**#596 was rebuilt during the grilling**, at `22:42Z`, between two tracker sweeps that read 87 nodes
and a read that found 90 — by that helper, run from outside the checkout.

**Two of this ADR's rulings describe behavior the helper already has**, checked rather than assumed.
`apply-delta` validates and applies a reviewed delta and `publish` re-renders and updates the issue,
so the reconcile-and-publish split ruled below already exists under those names. And
`reconciled_through` is assigned at exactly one place in the module, inside the delta path;
`publish_body` renders, writes and reads its own write back without touching it. **The anchor rule
ruled below is therefore a property to preserve rather than one to build.**

**What the helper does not do is the clinician's requirement.** `apply-delta` takes an authored
delta JSON file, so placing a newly-ready ticket means hand-writing that delta — which is the hand
work he reported. `publish_body` also verifies its own write round-trips, but reads nothing before
writing, so the lost-update race below is live and unaddressed.

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

### 1. The helper moves in tree as `tools/implementation_map.py`

**A move, not a rewrite.** It exists, it works, and it carries its own test module; what it lacks
is every binding this repository puts on a tool — a suite the merge runs, `DECLARED_LIMITS`, the
`console_codec` line, a `CLAUDE.md` section, and the extractor-coverage rule on what it reports.

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

### 3. Two operations, and the split is the glossary's — which the helper already has

`apply-delta` applies a reviewed delta and may advance the anchor. `publish` re-renders every
derived view from unchanged state and advances nothing. `publish` alone is safe to run from
anywhere, including CI.

**This is ratified rather than introduced.** The session ruled the split before knowing the helper
existed, and proposed a single command named `sync` before the glossary refused all three of its
properties. The helper had already landed on the same two operations under those names, so what this
decision does is bind them — a future author may not merge them back.

Deduplicating drawn edges is a **publish** concern. Authoring a packet's `outcome` is a
delta concern. Nothing that requires judgment lives in `publish`.

### 4. A publish never advances the anchor, and a delta advances it only when nothing is left unmapped

**The first half is preserved rather than built** — the helper assigns `reconciled_through` at one
place, inside the delta path, and `publish_body` never touches it. The second half is new.

`reconciled_through` is a claim of currency that `map_scan` grades ADRs against. A run that stamps a
fresh anchor while a ready ticket is still unmapped has published a map asserting it is current when
it is not — the repository's recurring shape landing on the one field whose entire job is to say how
stale the page is.

### 5. A delta refuses to place a packet with a blank `outcome`

The clinician ruled this directly. A packet's `outcome` is authored judgment and a guessed one is
worse than a blank one, which is `guidelines_catalog.py --draft`'s rule arriving on the map. What
the command removes is the JSON surgery, the edge derivation, the re-render and the publish — never
the judgment.

The session first proposed auto-inserting a stub with an empty `outcome` on the argument that the
`outcome` is unknowable at flip time. That argument was wrong and is recorded because it is
plausible: on both routes the clinician named, the flip is performed by the agent that has *just*
ruled the packet, so the flip is the moment the `outcome` is most knowable.

### 6. Idempotent, with the denominator on every run

The placement is additive for new tickets and inert for mapped ones, so it may be run repeatedly and
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
deltas always do, which is the correct split.

**It is not what the helper does today.** `publish_body` reads its own write back and refuses on a
round-trip mismatch, which catches a damaged write and not a concurrent one: nothing is read
*before* writing, so a second session's authored delta is overwritten silently and the read-back
still passes.

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
