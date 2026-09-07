# A collision kind is unordered or sequence and is demanded when two members are live

[ADR 0107](0107-a-collision-group-is-a-sequence-or-an-exclusion-and-an-unclassified-one-over-constrains.md)
ruled that a collision group carries a kind and that
[#809](https://github.com/mshamblin5150-code/clinical-skills/issues/809) would classify all 21 of
them. Grilling that ticket measured the map's live state and found the classification half of it
rests on a premise that is no longer true. This record supersedes ADR 0107's rulings 1, 2 and 3,
narrows its ruling 6, and amends the glossary entries its ruling 5 added.

[ADR 0106](0106-the-implementation-map-is-reconciled-by-an-in-tree-tool-rather-than-gated-at-publication.md)
records how the map is produced and
[ADR 0108](0108-the-map-graph-draws-dependency-alone-and-the-render-is-declared-rather-than-bounded.md)
records what it draws.

## Measured before ruling

Freshness gate `FRESH` at `f7040fd`. Tracker figures are re-derived from
[#596](https://github.com/mshamblin5150-code/clinical-skills/issues/596)'s state block and all 426
issues as of `2026-09-06`, by the parent rather than relayed. Every figure below moves on the next
reconciliation.

**Every collision group is historical.** All 81 packets in a group are done — every ticket behind
every one of them is closed. Only three packets in the map have an open ticket, and **none of the
three is in any group**. So ADR 0107 ruling 4, folded into startability today, moves nothing:
otherwise-available packets before the collision rule, 3; after it, 3.

**The 22 verdicts ADR 0107 asks for are therefore verdicts about finished work**, and every one
would be inert on the day it was authored.

**But the gate that replaces them is not toothless.** Sweeping each packet's live interval
(earliest ticket `createdAt` to latest `closedAt`) for the peak number of simultaneously-live
members: **all 22 groups have had two or more live at once, and 17 have had three or more**. The
peak is 11, in `tools/threshold_sheet.py`.

**Over-constraining startability would have held a great deal and never starved the frontier.** At
the worst instant, 2026-08-27, 50 packets were live, 41 of them in a group, and **33 held**. The
maximum held share of grouped-live packets is 83%; 213 of 225 instants had at least one held
packet; and **there is no instant at which every live packet is held**. The maximum number of
groups simultaneously at two or more live members — that is, verdicts demanded at once — is 12.

**A group's list order is mostly not an authored plan.** Of 22 lists, 9 are sorted by packet
number, 9 by ticket creation, and **16 by ticket close** — a record of what landed, written after
the fact. **Five are sorted by none of the three**, and they are the biggest: `discussion skill
files` (12), `CONTEXT.md glossary` (12), `reference/thresholds/coverage.md` (9), `APA 7 and
reference scanner surface` (7), `tools/checks_ledger.py` (6).

**Treating every unclassified list as a sequence implies 362 ordered pairs, and three are
contradicted by another group.** `P498+500`, `P540` and `P624` each precede `P535` in `discussion
skill files` while `P535` precedes all three in `tools/research_ledger.py + tests`. Both groups are
unclassified, both are among the five whose order matches nothing, and all four packets are done.

**`exclusion` names the property both kinds share.** ADR 0107 ruling 1 distinguishes them by *"must
not be in flight together"* — but that is true of a sequence group as well, and `cmd_claim` warns
on an in-flight peer for **any** group with no branch on kind. The only discriminating property is
whether there is *also* an order.

**And the word already carries three senses here.** `exclusion` sits on the `_Avoid_` lists of both
**Refusal** and **Deferral** in `CONTEXT.md`, and the map's own state block has a top-level
`exclusions` key meaning tickets deliberately outside the packet queue, with delta verbs
`add_exclusions` / `remove_exclusions` and a finding named `excluded-and-mapped`. A fourth sense
would sit in the same JSON document as one of the others.

**Two prior findings are re-derived and unchanged.** The body's *"the graph draws all 21
identically"* stays false — `mermaid()` holds zero references to `collision_groups`. And of 97
consecutive pair instances, 15 are also a `HARD` or `REBUILD-SAVING` edge and **82 are recorded
nowhere else**, so the lists are not a restatement of the edge set.

**The third kind #771 proposed is intra-packet.** The byte-identical
`legal_source_vocabulary_covered` pair is verified identical in the tree, and **both copies are
edited by one packet, `P771`**. `hard_blockers_of` drops intra-packet edges as *"the packet's
own"*, and the two files sit in two different groups, which a per-group field cannot span.

## Ruled 2026-09-06

### 1. The kinds are `sequence`, `unordered` and `unclassified`

Superseding ADR 0107 ruling 1's name. `exclusion` describes the obligation both kinds carry rather
than the one that separates them, so a reader taking it literally concludes a sequence group's
members may build concurrently — which is false and is the destroyed-rebuild direction. `unordered`
states the axis startability actually reads. The collision with the state block's `exclusions` key
and with two `_Avoid_` lists goes away as a consequence rather than as the reason.

An absent field is `unclassified`. An unrecognized value is a finding named `bad-collision-kind`,
on `bad-edge-type`'s precedent in the same function and for its reason: the field selects which
rules run, so a third value passing silently is a rule nobody applied.

### 2. An unclassified group over-constrains startability, not only the render

Superseding ADR 0107 ruling 2, which was written about rendering alone. A sequence predecessor is
**every earlier not-done member** of the list, and an unclassified group's list is read as a
sequence. The asymmetry is 0107's unchanged: a wrong hold costs a delay, a missing one costs a
destroyed rebuild.

The measurement above is what makes this affordable rather than reckless — the frontier has never
emptied — and the 33-held figure is retroactive, computed against a history in which nobody was
ever asked for a kind. Under ruling 4 the verdict is demanded as the group crosses the threshold,
so a group is unclassified-with-two-live only for as long as one reconciliation takes.

**Classifying a group `sequence` is also the moment its list order is ruled.** Until then the order
is unverified — retrospective in 16 groups and arbitrary in 5 — and the hold is a precaution rather
than a claim. Without this sentence the frontier asserts an authored order for 22 lists nobody
authored, which is #809's own complaint moved from the drawing into the frontier.

### 3. The kind is set by `set_collision_kind`, which cannot change membership

Superseding ADR 0107 ruling 3. The delta verb takes `{name, kind}` and an optional `packets` that
is **refused unless it is a permutation of the current membership**: order may be re-authored,
the set may not. Membership changes stay with `remove_collision_groups` plus
`add_collision_groups`, where they are visible as what they are.

This exists because `add_collision_groups` refuses an existing name, so classification under the
verbs that exist means retyping the whole member list — and nothing would notice a dropped member.
`collision-off-map` fires on an *unknown* packet id, never on a *missing* one, so a typo would
silently shrink a group, producing the one shape ADR 0107 already declares it does not grade.

When the kind is `unordered` the verb stores the member list sorted by packet id. ADR 0107 made
this a rendering rule to avoid touching state; a reconciliation is the command allowed to change
state, and doing it here means the JSON an agent reads and the table a person reads carry the same
order. Sorting at the render instead would leave the ticket's own complaint in the JSON.

The `Kind` cell renders the word — `sequence`, `unordered` or `unclassified` — never the hardcoded
`-` it carries today. A dash reads as *not applicable*; the word reads as *nobody has ruled this*.

### 4. An unclassified group with two or more not-done members is a finding

The finding lives in `validate_against_live`, so it surfaces through `check`, `publish` and
`apply-delta`, and `report()` already exits non-zero. `apply-delta` applies the delta and *then*
reports: refusing would strand the authored outcome, and reconciliation is reviewed judgment.

Two or more, rather than one, because the kind only ever changes an answer when two members are
both unfinished. One live member with every peer done leaves no order to violate and no
concurrency to serialize, and demanding a verdict there is #809's dead-verdict problem returning
one packet at a time.

### 5. `claim` refuses a ruled `sequence` and warns an `unclassified`

The strength of the refusal matches the strength of the evidence behind it. A ruled order is a
claim somebody stood behind; an unverified list order is a precaution. Both messages name the kind
and the group.

This is a deliberate departure from how `claim` treats an unmet `REBUILD-SAVING` predecessor, which
warns and returns 0 — a gap against **Startable packet** that already exists and this record does
not touch. The justification is that the harm differs: that warning says the cost is *"a rebuild,
not correctness"*, while a sequence group's own `why` says a violation *"invalidates recs
records"*.

### 6. Collision-derived cycles are graded only among not-done packets

A separate check from `cycle_findings`, which keeps its liveness-blind walk over declared edges.
Otherwise the three contradictions measured above land as findings on day one, about work that
finished weeks ago and that ruling 4 is deliberately silent on — two mechanisms disagreeing about
whether a group needs a verdict.

Those three contradictions are real and this build deliberately does not report them. They are
evidence for ruling 2's order caveat, and they fire the moment either group gains two live members,
which is when somebody can act on them.

### 7. Classification stays the clinician's, and an agent leaves a group unclassified

Narrowing ADR 0107 ruling 6 rather than superseding it. What changes is not who rules but when the
ruling is demanded: at the reconciliation that makes it matter, attached to a packet that is
visibly held, instead of as a batch of verdicts on a ticket.

An agent meeting the ruling 4 finding leaves the kind absent. It may **not** rule `sequence` as a
safe-direction guess: that changes almost nothing operationally, since the packet is already held,
while clearing the one signal saying nobody has looked and discharging ruling 2's order obligation
with an order the agent cannot vouch for.

### 8. #809 carries no classification and becomes buildable unattended

It is the schema, the verb, the render, the startability limb, the claim split, the finding, the
cycle check, the glossary and this record. Ruling 6 of ADR 0107 withheld `ready-for-agent` because
21 classifications needed a human; the ticket no longer contains one.

## What this does not reach

The kind is authored, so nothing establishes that a group ruled `unordered` genuinely carries no
order — the wrong classification in that direction is the destroyed-rebuild outcome, and ruling 2's
over-constraint protects against it everywhere except where somebody has actively ruled otherwise.

Nothing grades whether a group's membership is complete. A packet that touches a shared file and
was never added to its group is invisible to every rule here, and ruling 3 narrows only the way
classification could newly *shrink* a group, never the pre-existing gap. `P781` touches
`tools/tracker_publish_hook.py` and is in the group of that name nowhere; whether that is a
reconciliation miss or a deliberate judgment that a fully-done group cannot collide is a reading.

Ruling 2's hold binds on an order that, for an unclassified group, nobody authored. The three
measured contradictions are the visible evidence that such an order can be wrong, and ruling 6
declines to report them until they are live.

Nothing here re-derives whether the kind a group is given is the kind its `why` prose describes.
The prose is the input to a reading, not a matcher's ground truth, and ADR 0107's 9 / 5 / 7 keyword
floor established only that both kinds exist.
