# A ruling ordinal has one referent: addenda continue the numbering, and the citation resolver is a third walker joining against the record's own list

[#554](https://github.com/mshamblin5150-code/clinical-skills/issues/554)'s subject: a citation can
name a live file at a working URL and still point at nothing — #510 cited a ninth ruling of
[ADR 0030](0030-a-recommendation-record-is-owned-like-every-other-artifact-its-trust-floor-is-keyed-on-the-limb-that-built-it-and-the-drafter-takes-no-escape-hatch.md),
which carries eight.

Grilled 2026-08-29 at `origin/main` `6b3c2b5`, one question at a time, each agreed. Nothing is
built here; this is the record the build reads.

## The evidence inverted the ticket before the grilling started

Filed on the **dangling ordinal**, the class turned out to be rare: one exhaustive sweep checked 53
ordinal citations across every ruling shape and all resolved except the ticket's own subject. The
**adjacent-ruling slip** — in range, resolvable, wrong — happened twice in one session and no
existence check can see it. The live, recurring class is the **ambiguous ordinal**: a record whose
numbering restarts, so one ordinal names two real items.

Re-measured whole at `6b3c2b5` rather than relayed, because two prior sweep claims on the thread
were false at this HEAD: the `Finding N` repair precedent never landed on `main` (it lives on an
unmerged branch, and no record on `main` carries that label), and
[ADR 0049](0049-the-sweep-alias-and-the-recs-root-are-two-lookup-roots-with-two-resolution-rules-and-the-producer-guarantees-the-prefix-it-writes.md)
is not a two-sequence record — its addendum **continues** the numbering across a shape change, one
monotonic sequence, no collision. What is true at this HEAD, across 72 records:

- **Five records carry two numbering sequences.** ADR 0050 is genuinely ambiguous — a corrections
  list and a rulings list, both bare ordered lists. ADR 0052 and ADR 0058 restart their **ruling**
  numbering at 1 in a later addendum, so low ordinals collide. ADR 0062 and ADR 0070 are
  distinguishable by heading.
- **The ambiguity is entirely latent.** Zero citations anywhere in the tree reach a colliding
  ordinal; the five citations into these records all land in exactly one sequence.
- **Zero live misresolutions**, in 204 coordinate citations across four coordinate words.

So the mechanism is scoped to the class with recurrences, priced while the collision is still
latent, and honest about the classes it cannot reach.

## Rulings

1. **Two mechanisms, gate first.** A record-shape gate over `docs/adr/` and a citation resolver
   over tracked files, in that order — the gate makes each record's ordinal set derivable, and the
   resolver is then a join against a clean denominator. The gate is the load-bearing half; the
   resolver is the cheap rider that catches the next out-of-range ordinal. Declaring without
   building was weighed and declined: what a written instruction cannot do is fail, and the one
   near-instance caught before merge was caught only because a session happened to read #554.

2. **A record's rulings form one monotonic sequence, addenda included.** ADR 0049 is the worked
   precedent: its addendum continues `8` through `11` across a shape change, and that is the
   blessed form. Any other numbered sequence in a record — corrections, findings, classes — must be
   distinguishable from the rulings: under a heading that is not a ruling heading, or carrying
   per-item labels. The gate fails a record whose ruling ordinals have two referents. A sequence
   that continues across a shape change is one sequence, not two — the gate's parser must read
   ADR 0049 as `1–11` or it re-derives the misreading this thread already recorded.

3. **Three in-place corrections, made safe by measurement.** ADR 0052's addendum rulings `1–3`
   become `9–11`; ADR 0058's `1–2` become `12–13`; ADR 0050's corrections list gets a heading or
   labels that take it out of the ruling shape. Zero citations reach any colliding ordinal today,
   so the renumbering breaks nothing — and it is the inverse of the renumbering #554 prohibits,
   which was renumbering a record to make a *wrong citation* resolve. These land on
   [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
   terms, each with a note naming this record.

4. **Tree-side only.** The resolver grades tracked files in the suite, on
   [ADR 0041](0041-a-glossary-term-is-filed-with-the-term-it-is-defined-against-and-a-duplicate-fails-the-suite-rather-than-the-hook.md)'s
   placement reasoning. Tracker text is declared unreached, and the counterexample that decided it
   is #554's own title — plain prose deliberately naming a nonexistent ordinal, as does nearly
   every sweep comment on the thread. A tracker-side checker fires on the ticket describing the
   defect, which would be the sixth recorded instance of describing a rule breaking the tool that
   checks it, and the quote-span parsing needed to prevent that is an unreviewable heuristic. The
   tracker keeps what has demonstrably worked there: sweep discipline. No repair sweep of dated
   comments.

5. **A sibling class in `tools/test_skill_agreement.py`, and one parser.**
   [ADR 0054](0054-a-relative-link-resolves-against-the-index-and-the-fixture-exclusion-is-shared-rather-than-copied.md)
   ruling 3 put the relative-link walk beside the step resolver as the same defect at two widths;
   this is the third walker. Not a widening of `EveryCitedStepResolvesToADeclaredStep`: a `step N`
   citation needs three resolution limbs because it does not name its skill, while an ADR-ruling
   citation names its record inline every time — nothing to resolve, only a record to open. The
   gate and the resolver read one ordinal parser, so the two cannot drift about what a record's
   rulings are. The class shares the module's `graded_files()` population and fixture exclusion.

6. **Four coordinate words, adjacency-keyed.** `ruling N`, `point N`, `decision N` and `rule N`
   are all live in the tree and all synonyms over one ordinal set per record, so all four are read
   by one alternation. The predicate is adjacency, not proximity: the measured false positives are
   all possessive drift — a ruling ordinal near an ADR number that belongs to a different record —
   and adjacency-only reproduced none of them. No normalization sweep of `point` or `decision` to
   `ruling`: every such citation resolves, and a rewording sweep is the repair sweep #554
   prohibits.

7. **The resolver fails; a deliberate mention is a declared count.** A dangling ordinal is a
   defect, not residue — unlike the step resolver there is no unresolvable class to stay humble
   about, so the posture is fail rather than counted. Exactly one tree-side citation overshoots
   today, and it is
   [ADR 0048](0048-a-tracker-citation-to-an-unmerged-path-is-dated-rather-than-rewritten-and-the-branch-scope-check-is-what-grades-it.md)
   ruling 15 quoting #510's defect on purpose. The exemption is #246's declared count marker —
   `<!-- unresolved-ruling-citations: 1 -->` on its own line, covering the next paragraph only,
   with a ceiling of 2 held just above the one declaration — a count, not an opt-out: an
   undeclared second mention in the paragraph fails, a stale marker fails, a zero exempts nothing.
   A quote-span or backtick exemption was refused on #246's own measurement: this repo writes
   backticked citations meaning real ones. ADR 0048 gains the marker as an in-place correction,
   content untouched.

8. **Durable records cite names and ordinals, never line numbers into files that take
   insertions.** A glossary term heading, a ruling ordinal, a module constant — stable anchors
   that survive an insertion above them.
   [ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
   ruling 11 applied this once, prospectively; the `CONTEXT.md` drift threads proposed it twice
   and neither adopted it, and five open tickets then broke on one glossary commit. This sentence
   is guidance and nothing enforces it — it is ruled so the next sweep that finds line drift has a
   record to cite instead of deriving the remedy a fourth time.

9. **What the mechanism does not reach is a `DECLARED_LIMITS` row each**, on the house pattern,
   with the evidence at the row: the **adjacent-ruling slip** (in range, resolvable, wrong —
   invisible to any existence check, and the reason a green resolver is not a checked citation);
   **line coordinates** (`file:line` and glossary term lines — they break on every insertion above
   them, and a check grading them goes red on unrelated commits); **tracker text** (ruling 4);
   **possessive drift** (ruling 6's adjacency bound leaves a mis-attributed ordinal beside the
   wrong ADR number unread); and **ticket-number citations** — a live file citing `#N` for the
   wrong ticket is the same defect, but the join is against the tracker rather than the tree, so
   it is out with the tracker surface.

## What none of this reaches

A citation that resolves to a real ruling and means the wrong one is untouched by every mechanism
here — the adjacent-slip row is permanent, not pending. A clean resolver run is a floor: every
cited ordinal exists, in a record whose ordinals have one referent each. Whether the ruling says
what the citing sentence claims it says stays a reading.
