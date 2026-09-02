# A collision group is a sequence or an exclusion, and an unclassified one over-constrains

The implementation map's `collision_groups` entries carry a name, an **ordered** list of packets and
a prose `why`. Reading the `why` fields during [#756](https://github.com/mshamblin5150-code/clinical-skills/issues/756)'s
grilling showed that one name is doing two jobs, and that the derived graph asserts an order most of
them explicitly deny.

This ADR records what a collision group means. [ADR 0106](0106-the-implementation-map-is-reconciled-by-an-in-tree-tool-rather-than-gated-at-publication.md)
records how the map is produced and [ADR 0108](0108-the-map-graph-draws-dependency-alone-and-the-render-is-declared-rather-than-bounded.md)
records what it draws. It amends the **Startable packet** entry ruled in
[ADR 0090](0090-the-readiness-refusal-lands-at-the-claim-rather-than-at-the-push-and-startability-and-readiness-stay-two-derived-properties.md)
and adds two glossary terms the repository has been using without defining.

## Measured before ruling, at `1f1c645`

Freshness gate `FRESH`. The tracker figures are re-derived from #596's body as of
`2026-09-01T22:42:56Z` and move on the next rebuild.

**Two obligations, one name.** Some `why` fields describe a real order whose violation destroys
work — *"one module; sequence 495, then 496, then 497+532"*, and *"must beat #438/#510 to main or
its one-cell rebuild invalidates recs records"*. Others deny order outright — *"Neither depends
semantically on the other; serialize the file edits and preserve both scopes"*, *"No semantic
dependency was ruled, so serialize and union the independent changes"*, and, on the group holding
three of the five packets on the current frontier, *"those shared-file relationships impose
sequencing and reconciliation, **not additional semantic dependencies**"*.

**A keyword floor over the 21 groups, and deliberately not a classification:** at least 9 are
explicitly unordered exclusions, at least 5 are ordered sequences, and 7 need a human read. The
floor is stated as a floor because a keyword match over prose is a matcher, and a matcher never
gets to turn a partial read into a clean whole.

**The graph draws all 21 identically** as `-.-` chains, so for at least 9 groups the picture asserts
an order the record denies — in the artifact the clinician uses to decide build order.

**Grouping is many-to-many, not chain-shaped.** 73 packets sit in a collision group and **26 are in
more than one**; `P587` and `P689` are each in five. Two consequences were measured rather than
reasoned. Mermaid `subgraph` clustering is impossible, because a node lives in one subgraph. And the
8 duplicate edge emissions recorded in ADR 0108 are explained by it: two groups sharing a
consecutive pair emit the same link twice.

**The chains are not a restatement of edges already held.** The session's hypothesis was that
ordered chains duplicate `REBUILD-SAVING` edges. **Only 14 of 88 consecutive pairs are also a
`HARD` or `REBUILD-SAVING` edge; 74 are recorded nowhere else.** The hypothesis is recorded because
it was wrong: the collision list carries mostly-new information.

**`Startable packet` reads neither kind.** Its definition is *"no open hard blocker, no uncleared
gate, no unmet rebuild-saving predecessor and nothing in flight"*. The rendered map surfaces
collisions separately, in a *"Must not build concurrently"* list beneath the frontier, so the
silence is deliberate presentation rather than an oversight — but it means the ordering constraint
is prose a reader merges by hand, and all five packets on the current frontier are in collision
groups with each other.

## Ruled 2026-09-01

### 1. `collision_groups` entries carry a `kind`

`sequence`, `exclusion`, or `unclassified`. A sequence group's `packets` list is an order and
violating it destroys work. An exclusion group's members must not be in flight together and carry no
order at all.

### 2. An unclassified group renders as a sequence

Twenty-one groups need classifying and seven need a genuine read. That is authored judgment, so an
unread group takes a blank kind rather than a keyword guess — but a blank has to render as
something, and the two errors are not symmetric. Rendering an exclusion group as ordered costs a
delay. Rendering a sequence group as unordered costs a destroyed rebuild, which is the outcome the
groups exist to prevent. **Over-constrain.**

### 3. An exclusion group's members are emitted sorted

The field stays a JSON list and will keep looking ordered. Sorting exclusion members by packet id
removes the only signal a reader could mistake for sequence, and the glossary entry says so. This is
a rendering rule, not a schema one: the authored order of an unclassified group is preserved until
somebody rules it.

### 4. `Startable packet` gains an unmet **sequence** predecessor and never an exclusion peer

An exclusion peer bears on concurrency, not on startability, and folding it in would make the
frontier refuse work that is genuinely startable. A sequence predecessor is the same kind of thing
as the unmet rebuild-saving predecessor already in the definition, and only this decision lets
*"don't start P757 until P716 lands"* be derived rather than read out of prose.

### 5. Two glossary terms are added and one is amended

**Collision group** is used throughout the map, the state block and this ADR series and appears
nowhere in `CONTEXT.md`. It enters with its two kinds beneath it, and **Startable packet** is
amended per decision 4.

### 6. Classification is a grilling job, not an agent's

The ticket carrying this work does not get `ready-for-agent`. Seven of the 21 groups need a reading
of the `why` prose against what the packets actually touch, and an unattended agent would guess —
which decision 2 exists to prevent one level down.

## What this does not reach

The kind is authored, so nothing establishes that a group classified `exclusion` genuinely carries
no order — a wrong classification in that direction is the destroyed-rebuild outcome decision 2
protects against everywhere except where somebody has actively ruled it. Nothing here grades whether
a group's membership is complete: a packet that touches a shared file and was never added to its
group is invisible to every rule above, and remains what the reconciliation's semantic judgment is
for. And the floor of 9 / 5 / 7 is a keyword read of prose, not a classification; it establishes
that both kinds exist and nothing about which group is which.
