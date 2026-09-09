# The map render stamps its producer and the graph draws only what carries an edge

[#756](https://github.com/mshamblin5150-code/clinical-skills/issues/756) was filed because #596's
Mermaid graph mostly drew collision sequencing rather than dependency.
[ADR 0108](0108-the-map-graph-draws-dependency-alone-and-the-render-is-declared-rather-than-bounded.md)
ruled that in, [ADR 0106](0106-the-implementation-map-is-reconciled-by-an-in-tree-tool-rather-than-gated-at-publication.md)
moved the helper in tree, both were built, both were tested, both were merged — and on the morning
this record was written the published map carried 123 collision links, nine duplicate edge lines and
no collision table.

**The rulings were built into a file that does not publish the map.** A second copy of the emitter
lives outside every checkout, is what the skill invokes, is nine days behind, and is what has been
writing #596. Every instrument this repository owns reported success, because every instrument was
pointed at the artifact that was built rather than at the artifact that was published.

This record rules the stamp that makes the two distinguishable, the graph shape that follows once
the collision links are gone, and the coverage statements that would have caught it. It supersedes
nothing: ADR 0106 ruling 1 and ADR 0108 rulings 1, 2, 3 and 4 were correct, and what is added here is
that a ruling built into a non-publishing artifact is indistinguishable from one built correctly.

## What was measured before ruling, on 2026-09-09

Freshness gate `FRESH` at `05d5094` at both checkpoints. Every tracker figure below is a measurement
of a moment and moves on the next rebuild; the figures taken from the committed emitter do not.

**The two artifacts disagreed, and the disagreement was the whole ticket.** Parsing #596's published
Mermaid block against `python tools/implementation_map.py render` from the same state:

| | committed emitter | published body, 02:21Z |
| --- | ---: | ---: |
| node definitions | 138 | 138 |
| edge lines | 58, all distinct | 181, 172 distinct |
| bare `-.-` collision links | 0 | 123 |
| `-->\|HARD\|` / `-.->\|saves rebuild\|` / `==>\|GATE\|` | 39 / 14 / 5 | 39 / 14 / 5 |
| `## Collision groups` | present | absent |

**#756 has oscillated across seven tracker sweeps and every one of them was right.** Six measured
the emitter and returned `STALE` or `FALSIFIED`; one measured the publication and returned the
finding live at a *higher* share than when filed. The ticket never declared which artifact it was
about, so each sweep chose one and contradicted its predecessor. Agreement across re-runs added no
support, because five of the six ran the same command against the same local render.

**`check` and `audit` print the same clean line and cover different populations.** `cmd_check` runs
`validate_shape + validate_against_live`, which read the state block and never the derived views;
`cmd_audit` additionally diffs every derived section against a fresh render. Both call `report`,
which prints `clean: no findings`. On the morning of 2026-09-09, with the graph 123 links wrong,
`check` printed `clean: no findings` and `audit` printed four `stale-derived-view` findings —
`Collision groups`, `Current frontier`, `Dependency graph`, `How to update this map`. **A tracker
comment written the previous night had used `check`'s clean line to certify that the published
derived sections matched the current emitter.** Under that claim's negation the command prints the
same thing.

**The producer was identified by a string no in-tree version has ever contained.** The published
`## How to update this map` named `~/.agents/skills/implementation-map/` and its helper
`scripts/implementation_map.py`; both in-tree versions, at `5772477` and at `HEAD`, name
`tools/implementation_map.py` and carry a bullet the published body lacked. That file is 56,749
bytes, last modified 2026-08-31, emits a bare `-.-` per adjacent pair of collision-group members,
and contains **zero** references to `verify_mermaid`, to a duplicate-edge guard, to a
`## Collision groups` section, or to `tracker_publish_hook.authorize_issue_body`.

**The obvious hypothesis was falsified before it was published.** *A local worktree behind the fix
ran `publish`* is the natural reading and it is wrong: of 36 registered worktrees, 10 hold the
emitter including commit `3df6ef9`, 26 hold no emitter at all, and **zero** hold it without the fix.
Had that hypothesis been true, at least one worktree would have held a `tools/implementation_map.py`
emitting a bare `-.-`. None does. The pre-`3df6ef9` in-tree emitter was also ruled out, on the
`## How to update this map` text: it matches the published body on collision links, on the missing
table and on the absent dedupe, and not on that fourth section.

**It is not a single regression; the map alternates.** The body's revision history shows at least
six flips between the two renderers on 2026-09-08 alone, and the stale renderer's collision count
rises monotonically — 110, 112, 114, 115, 117, 118, 123 — which establishes that it reads the
**live** state block and re-renders it, rather than restoring a cached body. Both producers share the
state block and neither refuses the other, because only the derived views differ and the state hash
does not cover them.

**The helper serves one repository.** Across the local Codex session store, 658 command lines name
`implementation_map.py` together with a `--repo` argument and every one of them is
`mshamblin5150-code/clinical-skills`. `~/.agents/skills/` holds 41 skills and this is its only
repository-workflow one; its `agents/openai.yaml` carries no repository binding and the script
hardcodes none. Had another repository used it, a second `owner/name` would appear on one of those
658 lines.

**ADR 0106 ruling 1's own words are what went wrong.** It reads *"A move, not a rewrite."* A move
leaves nothing behind, and the evidence of a move is the **absence** of a file outside the checkout.
Nothing in this repository looks outside the checkout — which that ADR records about itself, in its
own measured section: *"All of them were clean, and none of them looked under `~/.agents/`."* The
blind spot that made the record first report the helper as gone is the same one that let its ruling
be verified by searches that could not see the file it ruled on.

**ADR 0108 contains a contradiction that this record resolves.** Its decision 5 argues against an
edge bound partly on the ground that *"under decision 1 the drawn graph falls to roughly 49 nodes
and 51 edges."* It did not. Its decision 4 requires that **every state packet has a node**, so
removing the collision links converted the collision-only nodes into isolated ones instead of
removing them. Measured on the committed emitter: 138 nodes, 58 edges, and **77 nodes touch no edge
at all.** ADR 0108 ruling 2 blessed keeping isolated nodes, and it was ruled about 10 of 93.

**What a lone node carries was measured rather than argued.** `## Packet table` holds 133 rows with
`Packet`, `Tickets`, `Status`, `Blocked by`, `Outcome` and `Collisions` columns, and every packet
drawn in the graph has one. The 12 drawn nodes without a row are the four external-gate nodes, which
are not packets, and eight merged packets whose node id sanitises `+` to `_`. **No packet is drawn
that the table omits.**

**The map was repaired during this session** under the clinician's explicit authorization, after the
out-of-tree script and its test module were renamed aside and `SKILL.md` was repointed. One
`publish` reported `Mermaid coverage: 200 of 200 nonblank lines accounted; unread remainder 0`, and
the republished body re-measures at 58 edge lines all distinct, zero collision links, and a
`## Collision groups` section. ADR 0108 rulings 1 and 3 are in force in the published artifact for
the first time since they were ratified.

## Ruling 1. The render names the producer, in a derived section

The body carries the repository-relative path of the helper that rendered it and the commit that
helper was at — `tools/implementation_map.py at <sha>`. It goes in `## Snapshot`, which
`derived_sections` already drops from the audit diff, so it adds no staleness finding.

**Placement is forced by a measurement rather than chosen.** Both implementations write the state
back with `json.dumps(state, indent=2, sort_keys=True)`, so both round-trip the whole dictionary
including keys they do not know. A stamp inside the state block would be preserved verbatim by a
foreign producer and republished under its own render — a body carrying a stamp that certifies a
producer which did not write it, which is worse than no stamp. A derived section is regenerated
wholesale on every publish, so a producer with no stamping code emits none, and absence is the
signal.

**An absolute filesystem path is refused.** The natural thing to write is what actually ran, and
what actually ran was under a home directory. This repository is public and publishes a rebuilt map
several times a day; a repository-relative path and a commit say everything the check needs and
publish only what is already public.

**The commit is in the stamp because it catches a second failure the path cannot.** Ten worktrees
currently hold the emitter and not all are at head. A session publishing from one of those writes a
legitimate-looking body from an older in-tree renderer, which is this defect with a shorter fuse and
no foreign file involved.

## Ruling 2. The graph draws only nodes that carry an edge

The 77 packets touching no `HARD`, `GATE` or `REBUILD-SAVING` edge are not drawn. They remain in
`## Packet table` with `Blocked by: -`.

**This is ADR 0108 ruling 1's own argument, run backwards, and it is checkable rather than
asserted.** That ruling moved the collision links into a table because *"the drawing loses
information the table keeps"* — a dotted line could not say which module or which reason. Here the
reverse holds: the drawing keeps **nothing** the table lacks. A lone box says *free-standing*; the
table row says free-standing, and which packet, and its tickets, status, outcome and collisions,
133 times.

**ADR 0108 ruling 2 stays true and stops being load-bearing.** *This one is free-standing* is a true
and useful fact, it is published, and it is published in the section built to carry it. What changed
is the proportion: a claim ruled about a 10-of-93 residue was inherited by a 77-of-138 majority, and
the residue was the reason.

**A separate subgraph was considered and refused.** It is the right answer if the packet table does
not exist. It does, so a cluster is a third rendering of a fact already published twice.

## Ruling 3. The emitter's self-check becomes a partition, not a node per packet

ADR 0108 ruling 4 requires that every state packet has a node. Ruling 2 above breaks that literally,
and the requirement is **replaced rather than dropped**: every state packet is either drawn or
counted in the omitted free-standing set, and the two sum to the population, with the denominator
and the remainder printed on every run.

The discipline ruling 4 exists for is the extractor-coverage rule — derive the population, report the
denominator and the remainder, refuse to present a partial read as clean. A node-per-packet
requirement was one way to express it and not the property itself. The partition keeps the property
and stops forbidding the shape ruling 2 requires.

## Ruling 4. One predicate, four callers, two postures

The stamp check lives once, in `tools/implementation_map.py`, as a function over a body. Four
callers use it:

- `map_scan.py`, as a row, **advisory**.
- `.github/workflows/tracker.yml`, on the changed record at the `issues` `edited` event,
  **non-zero on a finding**.
- `implementation_map.py audit`, as a finding.
- `tracker_publish_hook.py`, refusing a #596 body edit that carries no stamp.

**The arrangement is `tracker_bodies.py`'s and is adopted for its reason** — the same predicate at
both publication hosts with different posture. Writing two is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220):
two copies of one rule, either editable without failing anything.

**`map_scan` is advisory because its red lands on the wrong session.** `checks.yml` runs it with
`exit $status` on every push to `main`, so a refusing row would fail the next push — for a session
that did not republish the map, about an issue it did not touch, with no remedy available to it but
telling someone else. That is how a check gets worked around, and this repository already ruled the
same shape once: ADR 0106 ruling 8 left `unmapped-ready` advisory on materially this argument.

**`tracker.yml` is non-zero because that host can attribute.** Its own header states the principle —
*scanning the changed record makes a red run belong to the edit that caused it* — and it is the only
host that fires at the republication rather than hours later.

**The publish hook is a fourth caller and not a fourth gate.** It reaches a Claude Code publisher
only; a Codex session running an out-of-tree script crosses no hook, which
`tracker_publish_hook.NOT_REACHED` already declares. It is nearly free once the predicate exists and
it is worth nothing as prevention. This is stated so that a reader counting four callers does not
read the map as protected.

## Ruling 5. A clean run says what it walked, and `check` is not `audit`

`report` states the walked population, so `check` and `audit` no longer print the same line. `check`
says the state block was graded and the derived views were not read, and names `audit` as the
command that compares them. `audit` states its section denominator and how many differed. Both print
on a clean run and not only beside a finding, which is [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
ruling: a reader who learns to read a qualifier reads its absence as the stronger claim.

`implementation_map.DECLARED_LIMITS` gains a row saying a clean `check` does not establish that the
published derived views match a fresh render.

**Both halves, because the failure had two readers.** The comment that certified the wrong artifact
was written by someone reading console output, so a limits row alone would not have reached them;
the next author to extend the module is reading source, so a printed line alone would not have
reached them either. They are two different claims — what was walked, and what a clean run does not
establish — not two copies of one.

**Folding the diff into `check` was refused.** `check` is the cheap pre-claim command; `audit` took
over two minutes against the live tracker in this session. Making `check` cost that is how it stops
being run.

## Ruling 6. ADR 0108 ruling 6's limit is relocated, and each grader declares its own

ADR 0108 ruling 6 placed the GitHub-renderability limit in `map_scan.DECLARED_LIMITS`. It was built
as `github-renderability` in `implementation_map.DECLARED_LIMITS`, and four tracker sweeps recorded
the divergence without action.

**The ruling's location is amended, because the ruling's own reasoning names the other object.** It
reads *"After decision 4 passes, what is established is that the block is internally consistent —
never that GitHub will draw it."* Decision 4 is the emitter's self-check, which lives in
`implementation_map.py`. The sentence describes one tool and its last clause names the other; the
build followed the sentence.

**`map_scan` gains a different row rather than a copy of that one.** After ruling 4 above it reads
the stamp, so it acquires a render-adjacent clean run of its own, and it declares that a clean stamp
check is not a render either. Each object's rows describe the tool they sit in, which is what makes
a `DECLARED_LIMITS` readable at the point of use. Placing the same row in both is #220.

**Neither object's row count is stated here or in either module's prose.** These counts have already
been published wrongly three times in tracker comments, at 6, 7 and 9, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) on a figure nothing
re-derives.

## Ruling 7. The out-of-tree helper is retired and the skill points at the committed one

`~/.agents/skills/implementation-map/scripts/implementation_map.py`, its test module and its
`__pycache__` are renamed aside, and `SKILL.md`'s two command references now name
`tools/implementation_map.py`. **The repoint and the retirement are one change**: deleting the script
while the skill text still names it leaves a session following the skill literally and failing on a
missing file.

Renamed rather than deleted. The file is tracked by nothing, so a delete is unrecoverable, and the
658-invocation reading that established it serves one repository is a claim about a session store
rather than a proof.

`SKILL.md` carries a paragraph stating that a copy beside the skill is outside every checkout, that
no test, hook, workflow or gate in the repository can see it, and that one rendered the map for nine
days silently.

**Junctioning the skill directory at an in-tree path was considered and refused as scope.** It is the
more durable shape and it is `skills_mirror.py`'s pattern, and it would couple a machine-global skill
directory to one checkout and require that tool to grow a second root and a second orphan drain — a
mechanism at least as large as this one, for a residue ruling 1 already covers. The stamp does not
care which foreign copy published, or whether anyone knew it existed.

## What this record does not settle

**It does not prevent a foreign publication.** Every mechanism here is detection. The stamp is read
after the body is on the tracker, and the one host that could refuse before publication reaches a
single publisher. A reader counting gates should read this paragraph first.

**A copy forked after the stamp lands would carry it and be indistinguishable.** The stamp bounds
accidental divergence, which is what happened here, and not a deliberate one.

**Which session performed the 01:02Z and 02:21Z republications is unknown.** Every body edit is
attributed to one account and GitHub exposes no per-token actor; the archived Codex rollouts that
invoke the retired path bracket the window without establishing it.

**Whether GitHub renders the block is still declared and not graded**, unchanged from ADR 0108
ruling 6, and now declared in the module whose self-check could be over-read as establishing it.

**Nothing here grades whether the drawn graph is the right picture.** Ruling 2 removes nodes that
carry no edge; it does not establish that the edges are the correct dependencies, which is ADR 0106
ruling 1's semantic-placement limit and stays a reading.

**The skill's own instructions remain out of tree.** `SKILL.md` is a file no test in this repository
reaches and it can drift again — it already had, since its edge taxonomy says *COLLISION-SEQUENCING …
Never an edge* while the script beside it emitted them as edges for nine days. Ruling 1 makes the
consequence detectable; it does not make the instruction checkable.

**The count of moments this map has been measured at is not a property of the map.** Three figures in
#756's history were recorded as three readings of one artifact and were three readings of a
republished one. Any count of the published body is a measurement of a moment, and this record's
tracker figures are dated for that reason.
