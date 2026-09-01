# A glossary sense collision is recorded on the entry standing alone and the candidate population is a declared object

[#702](https://github.com/mshamblin5150-code/clinical-skills/issues/702) was filed out of
[#667](https://github.com/mshamblin5150-code/clinical-skills/issues/667)'s grilling on 2026-08-30,
recording that `CONTEXT.md` carries **`Declared`** in two senses and that
`tools/test_glossary_terms.py` cannot see it. Three later sweeps added instances to it without
ruling it. Grilled 2026-09-01, at `origin/main` `ca318be`. **Five decisions, ruled by the clinician
on that date.** Nothing is built here; this is the record the build reads.

**The freshness gate refused the first checkpoint and the refusal was load-bearing.** It read
`STALE` at `84cb99a` with `origin/main` at `ca318be`, and `CONTEXT.md` was in the incoming set — the
evidence base for every measurement below. The branch was brought forward by merging, the suite was
re-run on the merged tree (**4246 tests, `OK`, 3 skipped**), and every measurement was re-derived
against `ca318be` before any of it was believed. Six terms landed in that delta and **none of them
moved a single figure here**, which is worth recording only because it could not have been known
without re-deriving.

## What this corrects in the ticket, and both corrections change the answer

**1. The body prices option 2 — *rename the tier* — on a claim that is false as written.** It reads
*"The tier vocabulary is cited by `skills/clinical-note/SKILL.md`'s tier blocks and by
`filled_vitals_census.py`'s parser, so this is not a glossary-only edit and the cost has to be
measured before it is priced."* Measured:

- `git grep -w DECLARED` over the whole tree returns **two hits, both an unrelated dict in
  `tools/test_skill_agreement.py`**. There is no `DECLARED` tier token anywhere.
- `filled_vitals_census.py`'s block-boundary regex enumerates the tier tokens it knows —
  `DERIVED|FLAG|GAPS|UNKNOWN|PROPOSED|FILLED`. **`DECLARED` is not in it**, so no parser reads the
  tier.
- Across `fixtures/*` and `skills/*` the emitted tier tokens count `FILLED` 278, `DERIVED` 124,
  `PROPOSED` 55, `GIVEN` 54, **`DECLARED` 0**.
- `### Tiers` opens *"Every line of a finished note is a given, a derived value, or a filled one"* —
  **three**, and the tier is not one of them. Every use of the word in `clinical-note/SKILL.md` is
  the adjective in prose, and a declared value's tier-block home is `FILLED·asserted`.

So the tier is a glossary entry with no token, no parser, no fixture and no membership in its own
section's opening enumeration. Renaming it is a glossary-plus-prose edit, and the ticket's stated
ground for treating option 2 as expensive does not exist.

**2. The [#679](https://github.com/mshamblin5150-code/clinical-skills/issues/679) sweep's conclusion
inverts on that measurement.** That comment applied
[ADR 0089](0089-the-map-gate-is-an-offline-grader-over-a-harvest-and-the-reconciliation-obligation-is-anchored-on-a-field-the-delta-sets.md)
ruling 9 — *the tie-break by number is what a clinician overrides when the older concept is the
load-bearing one* — read the tier as the load-bearing sense because it is the older one, and
concluded **option 3**, the shape the body calls *"worse on its face."* Older is right: the tier is
`23f4312`, 2026-08-09; `Declared limit` is `f6ab6e7`, 2026-08-23. **Load-bearing is wrong.**
`Declared limit` is live in **51 files**, owns
[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md) and
[ADR 0082](0082-the-declared-limit-criterion-is-a-glossary-pair-and-membership-is-decided-on-the-sentence.md)
and a dedicated test module, and **ADR 0082 ruling 3 chose the shared word deliberately** — *"the
shared word carries the shared structure and the differing word carries the whole distinction."*

**Age and load are two tests and this instance separates them.** ADR 0089 ruling 9 names them
together because on `Drift` they agreed. Where they part, the ruling's own ground — *the older
concept is the load-bearing one* — is a claim about load, and age was the evidence for it rather
than the test.

## Measured before ruling, at `ca318be`

**The candidate predicate**: a single-word heading whose word also appears as a word in another
heading. Over **145 headings, 41 of them single-word, it fires 10 times**:

| fire | verdict |
| --- | --- |
| `Declared` 123 → `Declared non-source` 374, `Declared limit` 504, `Declared rationale` 512, `Declared no-binding` 580 | **collision** |
| `Drift` 129 (clinical) → `Corpus drift` 330 (corpus versus tree) | **collision** |
| `Topic` 338 (clinical subject) → `Catalog topic` 342 (a document's own wording) | **collision, already repaired** |
| `Citation` 560 (a ticket reference) → `Citation key` 159, `Legal citation` 171, `Stated citation` 318 (all bibliographic) | **collision** |
| `Assertion` 211 → `Promoted assertion` 223 | narrowing |
| `Publish` 259 → `Publish route` 584 | narrowing |
| `Corpus` 306 → `Corpus drift` 330 | narrowing |
| `Span` 444 → `Null span` 448 | narrowing |
| `Recommendation` 476 → `Recommendation record` 346, `Recommendation sweep` 358, `Recommendation label` 394, `Dropped recommendation` 492 | narrowing |
| `Packet` 592 → `Startable packet` 600 | narrowing |

**Four collisions in ten fires, and ten rows a person reads in one sitting.** The broader predicate —
any two headings sharing any word — fires on **102 pairs of 10,440**, and is the name-keyed
instrument [ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)
ruling 1 refuses.

**The predicate found the fifth instance on its first run, which is the whole evidence for it.**
`Topic` / `Catalog topic` is repaired **on both sides** — `Topic` reads *"Distinct from the catalog
topic"*, `Catalog topic` reads *"It is **not** the clinical topic"*, and that entry's `_Avoid_` line
is the strongest disambiguation in the file: *"topic — unqualified, that word means the clinical
subject here; say which."* **Nothing counts it**, and #702's tally, which three sweeps had already
called a floor, did not know it existed.

**The file has three 1-to-1 collisions arranged three different ways**, which is why the anchor
needed ruling rather than inferring:

| collision | arrangement |
| --- | --- |
| `Sitting` / `Session` | pointer in the older's `_Avoid_` **and** a full clause on the newer |
| `Section read` / `Section number` | clause on the newer only, nothing on the older |
| `Topic` / `Catalog topic` | clause on **both**, plus an `_Avoid_` line |

## What is ruled

### 1. The collision is recorded and nothing is renamed

`Declared` keeps the tier sense and the `Declared *` family keeps the second, on the
`Sitting` / `Session` precedent this file already runs.

The tier is the loser on the load-bearing test, so the only live question was whether the loser is
**renamed** or **marked**. Renaming needs a replacement word, and the tier's definition — *a value
fixed by a stated rule* — rests on the ordinary English meaning of the one it would give up, so
every candidate reads worse than what it replaces. Marking costs one clause and is precedented three
times in this file.

**Option 3 is refused on the measurement rather than on its face.** The correction above removed the
argument that was pointing at it. **Option 4 — record nothing — is refused on the ticket's own
evidence**: three separate sweeps have each had to re-derive this collision from scratch, which is
the cost of not recording it, paid three times and visible on the ticket.

### 2. The clause anchors on the entry standing alone against the rest; where neither stands alone, on the newer

**One clause per collision**, never one per member.

For `Declared` that is the tier at 123, and for `Citation` the bare term at 560. For a 1-to-1 shape
neither term stands alone, and the anchor falls to the newer term — so `Drift`'s clause goes on
`Corpus drift` at 330.

**Both halves select the same thing: the entry where a reader has just met the *unexpected* sense.**
That is what `Session`, `Section number` and `Catalog topic` have in common, and it is what standing
alone buys in the many-sided shapes, because four neighbours and three neighbours respectively teach
the other reading.

**Following the stated precedent literally was refused**, and this is the half most easily got wrong.
"Clause on the newer term" holds in every existing instance, and applied to `Declared` it puts
**four copies of one rule across three sections with nothing between them** — which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s defect landing inside the
repair for a ticket whose subject is that hand-written disambiguations do not scale.

**"The entry a reader hits first" was tried and dropped.** It is true of `Declared` 123 and of
`Section number` 151, and false of `Citation` 560 and `Recommendation` 476, whose compounds are
written above them. It was a coincidence of two instances, not a rule.

**The three already-repaired instances stay exactly as they are.** `Section`, `Topic` and
`Sitting` / `Session` keep their arrangements. This rule governs the next repair; rewriting three
working disambiguations to match a rule derived from them is churn that buys a reader nothing.

### 3. Scope is `Declared`, `Citation` and `Drift`, plus the standing rule — and it is not a census

#702's *do not widen* forbids **a name-keyed sweep for shared first words**, which is ADR 0074
ruling 1's instrument. Repairing instances that three sweeps have already hand-enumerated on the
record is not that sweep: the enumeration exists and cost this session nothing.

Leaving `Citation` and `Drift` unmarked after ruling the shape for `Declared` pays the ticket's own
stated cost a fourth time — green, hundreds of lines from their twins, findable only by whoever
happens to be reading the right ticket that day, which is how all five were found.

**`Declared limit` and `Declared rationale` are not re-opened.** #667's ruling and ADR 0082 stand;
this record renames nothing and touches neither.

### 4. The candidate population is a declared object — candidacy derived, membership declared

The predicate derives the fires. Each carries a person's one-word ruling, **collision** or
**narrowing**. A **new** fire has no row and fails the suite; the remedy is a person reading it and
writing one word. Beside it, a prose bind asserting the clauses on the three repaired entries are
still there.

**This does not break ADR 0074 ruling 1, and the line is worth being precise about.** That ruling
refuses deciding **membership** by name — *"applied to sentences and never to names."* This decides
**candidacy** by name and leaves membership a reading, held as a declared row. The distinction is
the whole permission, and if it is rejected the object goes with it and the prose bind is what
survives.

**#702 says option 1 is *"checkable by nothing beyond a prose bind."* The measurement falsifies
that**, and the evidence is not the predicate's existence but its first run finding an instance five
sweeps had missed.

### 5. It is not a gate, and the tally is a floor

**Six of today's ten fires are legitimate narrowings**, so refusing a new fire outright would refuse
correct work. The object fails on an **unruled** row, never on a fire.

**The tally stated here is a floor and not a count**, on the ticket's own terms and one instance
further along: it is what one predicate over one shape found, and that predicate cannot see the
shape `Section` has.

## What this does not reach, declared rather than left to be found

**The `Section` shape is invisible to the predicate.** `Section read` and `Section number` share a
word and **neither is a bare heading**, so no single-word rule reaches them — and `Section` is a
confirmed member of the class. The predicate is a floor on one shape, and the object says so beside
itself.

**The predicate cannot read sense, and nothing here proposes that it could.** Six of ten fires today
are one sense narrowed, and telling those apart from two senses is what the declared row records a
person having done.

**The six declared narrowings are hand-ruled rows, and this repo refuses hand-kept lists** —
`symbol_glyph_census` records that *an allowlist of glyphs that look harmless is exactly what would
have hidden U+001F*. The distinction claimed is that the glyph population is open and unbounded
while this one is 145 headings in one tracked file, and each row is a ruling rather than a shape
that looked harmless. **It is a claimed distinction and not a proved one**; if it fails, the object
fails with it and ruling 4's prose bind is the honest remainder.

**A clause can be present and wrong.** The bind asserts a clause exists at the anchor, never that it
distinguishes the two senses correctly, and no check reaches that.

**It reaches `CONTEXT.md` headings and nothing else.** A term heading colliding with a word already
live in the file's **prose** is ADR 0041's declared hole and stays open — ADR 0088's `Form coverage`
entry, which uses the `Declared limit` sense in running prose 377 lines below the tier entry, is a
live instance this record does not close.

**Nothing detects the collision that has not been enumerated.** ADR 0037's *"nothing detects a
collision"* narrows here rather than retiring: one shape now has a candidate generator, and the
other shapes still wait for somebody to be reading the right ticket.
