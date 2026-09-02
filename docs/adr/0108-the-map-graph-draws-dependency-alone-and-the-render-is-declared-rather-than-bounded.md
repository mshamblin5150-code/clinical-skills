# The map graph draws dependency alone and the render is declared rather than bounded

[#756](https://github.com/mshamblin5150-code/clinical-skills/issues/756) was filed because #596's
Mermaid graph failed to render on GitHub, and argued from there to a remedy: 70% of the drawn edges
are collision-sequence chains rather than dependencies, they are the layout cost, move them to a
table. During the grilling the clinician reported that the graph **renders now**, and that he does
not know whether anything fixed it.

That retires the ticket's premise and, more importantly, removes the ground under its causal claim.
This ADR records what the graph draws, and — the half certain to be re-proposed — **why no bound on
its size is adopted**. [ADR 0106](0106-the-implementation-map-is-reconciled-by-an-in-tree-tool-rather-than-gated-at-publication.md)
records how the map is produced and [ADR 0107](0107-a-collision-group-is-a-sequence-or-an-exclusion-and-an-unclassified-one-over-constrains.md)
records what its collision groups mean.

## Measured before ruling, at `1f1c645`

Freshness gate `FRESH`. Every tracker figure is re-derived from #596's body as of
`2026-09-01T22:42:56Z` and moves on the next rebuild.

**The graph renders, and it is larger than when it failed.** Two loads of the issue page reached
`is-render-ready` with no `.render-error` and no *Unable to render rich display*, at
`viewscreen.githubusercontent.com/markdown/mermaid`. A tracker sweep recorded one clean load an hour
earlier. The block is **6,026 characters, 93 nodes and 140 edges** against the **4,915 characters,
77 nodes and 115 edges** the ticket recorded as failing.

**The population, derived independently of the extraction.** Of 237 non-blank lines: 93 node
definitions, 140 edges, and a remainder of 4, all directives — `graph TD`, two `classDef`s and one
`class` line. No edge references an undefined node.

| drawn shape | count | what it is |
| --- | ---: | --- |
| `-.-` | 88 | collision-sequence links — exactly the sum of `len(group) - 1` over the 21 groups |
| `-->\|HARD\|` | 34 | dependency |
| `-.->\|saves rebuild\|` | 14 | `REBUILD-SAVING` |
| `==>\|GATE\|` | 4 | external gate |

**The collision share is 62.9%, not the 70.4% the ticket recorded nor the 72.9% a first pass here
published.** Both higher figures counted the 14 `REBUILD-SAVING` edges, which are dotted and are
**not** collision chains. Three separate figures for one quantity, each from a matcher nobody had
checked against the whole population.

**Node partition:** 40 nodes touch a `HARD`, `GATE` or `REBUILD-SAVING` edge; **41 appear only in
collision chains**; 12 are isolated. **53 of 93 drawn nodes carry no dependency relationship.**

**Eight edge lines are emitted twice** — `P495 -.- P496`, `P498_500 -.- P540`, `P540 -.- P624`,
`P584 -.- P587`, `P587 -.- P662`, `P700 -.- P702`, each once over. 88 drawn, 80 distinct. `HARD`
edges are deduplicated after packet collapse and collision links are not, which is an emitter
inconsistency rather than a data one; ADR 0107 records the many-to-many membership that causes it.

**Three figures in this session were wrong before they were right, and every one was a partial
matcher reading as a finding.** A regex that did not sanitize `+` to `_` reported 4 missing `HARD`
edges, which are fully explained by packet collapse dropping two self-edges and deduplicating three
into one. A node pattern keyed on `[` missed the three external gates, which mermaid defines with
the stadium shape `(["…"])`. And the dotted count above. This is the extractor-coverage rule earning
itself three times inside one grilling.

## Ruled 2026-09-01

### 1. The graph draws `HARD`, `GATE` and `REBUILD-SAVING`; collision groups become a table

**The decisive argument is not the edge count, it is that the drawing loses information the table
keeps.** `P495 -.- P496` says those two are adjacent in some chain. It does not say the module is
`tools/discussion_artifact.py`, and it does not say the reason. The state block holds both and the
graph discards them to draw a line. That argument holds at 88 edges and would hold at 8.

It is also the only representation that can be correct. 26 of 73 grouped packets are in more than
one group, so a dotted line cannot say *which* constraint it belongs to and no styling can make it
say so. A table can: one row per named constraint, with its kind, its packets and its `why`.

Two mermaid blocks — a dependency graph and a collision graph — was the option to take if the
information were symmetric. It is not: a 21-group membership structure is a table's native shape and
a graph's worst one.

### 2. The 12 isolated nodes stay drawn

A packet with no dependency and no collision is a true and useful fact — *this one is free-standing*
— and dropping it would leave a picture of only the entangled work.

### 3. The 8 duplicate emissions are a defect and are fixed in `publish`

Deduplicating drawn edges requires no judgment, so it belongs on the rendering side of ADR 0106's
split.

### 4. The emitter self-checks its own block before publishing

Every referenced node id is defined; no duplicate edge lines; every line accounted for as a node, an
edge or a known directive; every state packet has a node. Offline, deterministic, stdlib. **It would
have caught decision 3's defect**, and it is the extractor-coverage discipline applied to the
emitter: derive the population, report the denominator and the remainder, refuse to present a
partial read as clean.

### 5. No bound on drawn edges or nodes is adopted, and this is the decision to read before proposing one

#756 already forbade a threshold named at an edge, on `SPACE_ADVANCE_FRACTION`'s recorded failure
and [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s objection to inventing
a cut point the corpus does not ground. The situation is now worse than unprincipled: **the block
failed at 115 edges and renders at 140.** The only natural experiment available produced a
*contradiction*, not a cut point, so there is no measurement to ground a bound on in either
direction and any value would be invented. Under decision 1 the drawn graph falls to roughly 40
nodes and 52 edges, so a bound would guard a number nothing is near.

*The graph timed out once, so bound the edges* is the proposal a future session will make from this
ticket's title alone. This decision is where it is answered.

### 6. Whether GitHub renders the block is declared, not graded

After decision 4 passes, what is established is that the block is internally consistent — never that
GitHub will draw it. A row in `map_scan.DECLARED_LIMITS` carries the difference, so a clean run
cannot be read as the second claim.

Checking the live render after publishing was considered and is unavailable rather than declined on
taste: no tool in `tools/` opens a socket, CI has no browser, and the failure was declared
intermittent — a tracker sweep had already recorded that its own single clean load could not
falsify an intermittent timeout.

### 7. The timeout is recorded as resolved and unexplained

Not fixed. Nobody knows why it failed and nobody knows why it stopped, and an artifact whose
reliability is unexplained is this repository's recurring shape. Recording it as *fixed* would
retire a live uncertainty by wording.

## What this does not reach

Nothing here establishes that #596 will render tomorrow, and decision 7 is the honest form of that.
Nothing grades whether the collision table's contents are *right* — ADR 0107 owns the classification
and it is authored. The self-check in decision 4 is a floor on internal consistency and matches the
shapes this emitter writes, so a construct nobody has written yet passes it unseen. And the
node-partition figures above describe one rebuild of a moving artifact: every one of them moved
during the grilling that measured them, three times in the ticket's own history, and they are dated
rather than durable.
