# The implementation map is retired and a wholly withdrawn record carries one supersession banner

**Measured at:** dbb3bd3d5219b3dbe77198f5ab19ae6b832204e1

[#1547](https://github.com/mshamblin5150-code/clinical-skills/issues/1547) was filed on 2026-10-03
because the implementation map on
[#596](https://github.com/mshamblin5150-code/clinical-skills/issues/596) had reached GitHub's body
size ceiling, and every placement that tried to grow it printed `READ-BACK FAILED` while nothing was
written. It asked how the map should stay under the ceiling and whether the publisher should refuse an
oversized body before sending it. Grilled 2026-10-11 against `main`. Partway through, the clinician
said he no longer uses the map at all: it helped when he made it and is useless now. That turned the
question from repairing the map into retiring it, and he ruled every point below in that session. This
record and the retirement are built in one change.

## Measured before ruling

**The ceiling was still live after part of #1547 had landed.** PR
[#1715](https://github.com/mshamblin5150-code/clinical-skills/pull/1715) changed the message to say a
failed read-back leaves the write unconfirmed, and tightened the map's formatting. A REST read of #596
on 2026-10-11 returned a body of 261,960 characters, against a limit of 65,536 four-byte characters.
The publisher still sent an oversized body without measuring it first.

**The map had become a ledger of finished work.** The same read parsed the machine state block. 264 of
its 266 packets named only tickets that `gh issue list --state open` (70 open issues) did not return,
so they belonged to closed tickets. Those packets took about 108,000 characters of state, and the
derived packet table rendered from them took about 83,000 more.

**Nothing outside the map's own machinery read it.** A search of every tracked non-ADR file for the
map's module names, its issue number and its terms found readers only in the map tools, its CI step,
its hourly workflow, its `PostToolUse` hook, the publish-hook and Filed-from exemptions for its producer
stamp, and the tracker-event and publication-correspondence tables. No skill, no `docs/agents/` page
and no work-selection step consulted it. The only production callers of
`tracker_publish_hook.authorize_issue_body` were the map tool's two publication paths.

**What it cost.** From 2026-10-03 to 2026-10-11, #1547 collected more than forty comments recording a
placement that did not land or was refused at the map's lock. Each attempt harvested the whole tracker
first. `main`'s push runs failed at the map step for unplaced tickets and unreviewed ADRs that no
session could clear while the ceiling held.

## Ruling 1 — the implementation map is retired, not repaired

The clinician does not use the map, and nothing else reads it to decide anything. So the remedy is to
stop maintaining it, not to make room in it. The map's obligations end with this record: no ready
ticket owes a placement, and no ADR owes a review record. Both of #1547's original decisions, how the
map stays under the ceiling and whether its publisher refuses an oversized body, are moot.

## Ruling 2 — nothing of the map survives

Every part goes:

- the packets, collision groups, edges and exclusions;
- the ADR review records and the reconciliation floor;
- the frontier and the derived views;
- `tools/implementation_map.py`, `tools/map_scan.py` and `tools/implementation_map_post_hook.py`,
  with their tests;
- the hourly refresh workflow and the CI map step;
- the hook registrations, the producer-stamp exemptions in the Filed-from rule and the tracker
  checks, and the revision-break reference.

**GitHub's native blocked-by relationships stay authoritative for ordering between tickets.** They
always were; the map only mirrored them. Two agents building tickets that touch the same file are no
longer warned in advance. Git reports the conflict at the merge, and CI runs the suite on the merged
tree, which is what [ADR 0002](0002-ci-runs-the-suite-at-the-merge.md) exists for. A hand-kept
replacement for collision groups was refused because it would go stale the same way the map did.

## Ruling 3 — the direct-writer seam goes with the map

`tracker_publish_hook.authorize_issue_body` gated a writer that published by calling `gh` from inside
its own process, where no hook could see the call. The map tool was that writer. A gate with no traffic
is kept only by the suite that grades it, and every grader added to the command route would have to be
wired into it as well. So the seam, its tests and the publication-correspondence table's direct-writer
column are deleted. The command route, `analyze`, remains the one place a tracker publication is graded.

## Ruling 4 — the map's vocabulary leaves the glossary

`CONTEXT.md` names what exists now. The terms that existed only for the map are removed:

- Packet, Collision group, Startable packet;
- Reconciliation, Unreconciled ADR, Grandfathered map debt;
- Map disagreement, Map view, Map overwriter, Revision chain.

Revision chain was worded generally, but the map's clobber attribution was its only user. The map
clauses in Ready ticket and Lock identity are cut. The retired ADRs, with the banners ruling 5
introduces, are where a reader looks up what one of those words meant.

## Ruling 5 — a wholly withdrawn record carries one banner

[ADR 0280](0280-an-overturned-ruling-carries-a-dated-supersession-marker-written-by-the-record-that-overturns-it.md)
puts a dated marker beneath every withdrawn ruling. Retiring the map withdraws more than eighty
rulings across twelve records for one reason. One marker per ruling would repeat that reason eighty
times and tell a reader nothing more.

So a record whose every ruling is withdrawn carries **one banner** instead. It is a paragraph above
the record's first `##` heading. It opens `*Superseded YYYY-MM-DD.*`, quotes the record, links the
overturning record and its ruling, says `every ruling`, and says what still stands. The overturning
record declares it with one bullet that reads `every ruling,` where a per-ruling bullet reads
`ruling N,`. A record that keeps one ruling says so in both places with
`every ruling except ruling N`, and the two must agree. The binding test reads both forms in both
directions. A record that withdraws only some rulings still marks each one beneath it.

This narrows ADR 0280's placement and declaration rulings for the whole-record case only. Every other
part of ADR 0280 stands.

## Ruling 6 — #1547 carries the retirement, and the map's tickets close with it

#1547 is widened from repairing the ceiling to retiring the map. Its comments stay as the record of
why. [#596](https://github.com/mshamblin5150-code/clinical-skills/issues/596), the map page, and
[#1513](https://github.com/mshamblin5150-code/clinical-skills/issues/1513), the drain of the map's
frozen debt, close as superseded when this change merges. #596 keeps its last body as frozen history.
The deferred `apply-delta` placements and ADR review records recorded on #1547 are void.

## What this record does not reach

The ADRs that only mention the map in passing are unchanged, because none of their rulings governs
it. [ADR 0202](0202-a-paginated-read-carries-a-denominator-and-a-short-read-refuses.md)'s
paginated-read rule stands for its remaining consumers. Git history and the retired records hold the
map's design if it is ever wanted again; reviving it would be a new decision.

## Supersedes

- [ADR 0089](0089-the-map-gate-is-an-offline-grader-over-a-harvest-and-the-reconciliation-obligation-is-anchored-on-a-field-the-delta-sets.md)
  every ruling except ruling 9, the record "The map gate is an offline grader over a harvest". Its
  ruling 9, that `Drift` stays clinical, stands.
- [ADR 0090](0090-the-readiness-refusal-lands-at-the-claim-rather-than-at-the-push-and-startability-and-readiness-stay-two-derived-properties.md)
  every ruling, the record "The readiness refusal lands at the claim". Nothing stands.
- [ADR 0106](0106-the-implementation-map-is-reconciled-by-an-in-tree-tool-rather-than-gated-at-publication.md)
  every ruling, the record "The implementation map is reconciled by an in-tree tool". Nothing stands.
- [ADR 0107](0107-a-collision-group-is-a-sequence-or-an-exclusion-and-an-unclassified-one-over-constrains.md)
  every ruling, the record "A collision group is a sequence or an exclusion". Nothing stands.
- [ADR 0108](0108-the-map-graph-draws-dependency-alone-and-the-render-is-declared-rather-than-bounded.md)
  every ruling, the record "The map graph draws dependency alone". Nothing stands.
- [ADR 0144](0144-a-collision-kind-is-unordered-or-sequence-and-is-demanded-when-two-members-are-live.md)
  every ruling, the record "A collision kind is unordered or sequence". Nothing stands.
- [ADR 0155](0155-the-map-render-stamps-its-producer-and-the-graph-draws-only-what-carries-an-edge.md)
  every ruling, the record "The map render stamps its producer". Nothing stands.
- [ADR 0168](0168-a-map-obligation-belongs-to-whoever-incurred-it-and-the-producer-stamp-hashes-the-emitter.md)
  every ruling, the record "A map obligation belongs to whoever incurred it". Nothing stands.
- [ADR 0169](0169-a-ticket-states-what-filed-it-on-an-append-only-line.md) ruling 10, "A body
  carrying the map's producer stamp is outside these rules". The Filed-from rule stands for every
  ticket.
- [ADR 0199](0199-a-map-overwrite-is-attributed-rather-than-prevented.md) every ruling, the record
  "A map overwrite is attributed rather than prevented". Nothing stands.
- [ADR 0202](0202-a-paginated-read-carries-a-denominator-and-a-short-read-refuses.md) ruling 3,
  "Four consumers, and the harvest command is not consolidated". The two map consumers are gone; the
  `tracker_bodies` population and the label-overflow sentence stand.
- [ADR 0224](0224-the-map-s-views-refresh-hourly-and-a-stale-view-is-reported-rather-than-failed.md)
  every ruling, the record "The map's views refresh hourly". Nothing stands.
- [ADR 0240](0240-the-map-s-direct-writer-grades-through-analyze-and-runs-no-readback.md) every
  ruling, the record "The map's direct writer grades through analyze". Nothing stands.
- [ADR 0279](0279-the-map-check-fails-only-on-new-debt-and-the-debt-it-inherited-is-frozen-and-drained.md)
  every ruling, the record "The map check fails only on new debt". Nothing stands.
- [ADR 0280](0280-an-overturned-ruling-carries-a-dated-supersession-marker-written-by-the-record-that-overturns-it.md)
  ruling 4, "The marker sits directly beneath the overturned ruling or ground." A wholly withdrawn
  record carries one banner above its first section instead; the opening and the four parts stand.
- [ADR 0280](0280-an-overturned-ruling-carries-a-dated-supersession-marker-written-by-the-record-that-overturns-it.md)
  ruling 5, "naming each target and its ruling". A wholly withdrawn record is declared with
  `every ruling`; the binding in both directions stands.
