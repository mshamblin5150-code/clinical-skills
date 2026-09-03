# The `CLAUDE.md` limits-pointer walk is name-keyed, section-scoped and shape-blind, and an unreadable object is not a clean one

Found while grilling [#855](https://github.com/mshamblin5150-code/clinical-skills/issues/855),
2026-09-03, at `origin/main` `a820d8bd12ec1a64c408f9fc1cd7f1c11e3c9673`, freshness gate `FRESH`
before reading and before publishing. **Ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

[ADR 0119](0119-the-limit-row-type-stays-per-module-the-evidence-disposition-moves-to-the-grader-runner-and-the-declarer-walk-is-candidacy-derived.md)
ruling 4 split the declarer walk in two so the unbounded half could not hold the bounded one
hostage. #831 builds assertion 1 — a test names the object. This record rules assertion 2 — the
prose pointer copies no row — and it rules three questions the ticket did not have, each of which
turned out to be upstream of the three it did.

## Measured before ruling

**Every ADR 0119 figure re-derives at `a820d8b`**: 50 backticked `` `<module>.<CONSTANT>` `` pointers
in `CLAUDE.md` naming a real `tools/` module, **all 50 resolving**, 15 non-test modules holding a
top-level `DECLARED_LIMITS`, 11 reached by the pointer spelling and the same four missed —
`adr_next`, `discussion_post_scan`, `discussion_reply_scan`, `threshold_sheet`.

**The first attempt at that measurement was void, and how says more than what.** A script written
under `scratch/` resolved `CLAUDE.md` by walking up from its own location, which is the checkout that
owns `scratch/` — the **main checkout**, sitting on `codex/tickets-550-645` at `4bc0658`. It returned
49 pointers, 14 declarers and 10 reached: three figures, all plausible, none about this tree. The
same resolution rule this repository adopted deliberately in
[#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93) for account-owned state is
wrong for a measurement, and it fails silently in both directions.

**The 50 pointers are not one kind of object.** They are three, and only the first carries the
promise ADR 0074 ruling 5 makes:

| kind | count | example |
| --- | ---: | --- |
| limits-shaped constant | 27 | `refusal_scan.DECLARED_LIMITS` |
| a vocabulary the prose is meant to name | 18 | `threshold_coverage.STATES`, `guidelines_search.FILTERS` |
| no rows at all — `Pattern`, `int`, `str` | 5 | `docx_write.REFERENCE_HEADING` |

**The house already holds two disagreeing definitions of a copy, both live.** `checks_ledger` and
`research_ledger` use an 8-word shingle plus the row key; `voice_corpus` uses a whole-row normalized
substring and already binds `CLAUDE.md`. Over the 27 limits-shaped pointers the whole-row rule fires
**zero** times and the shingle rule fires nine. Twenty test modules assert some `CLAUDE.md` no-copy
bind today.

**The bill is knowable, and the ticket's *unknown until it runs red* was answerable before building
anything.** Under the rules below it is **9 hits over 6 pointers** — eight real prose edits and one
collision. Four of the six sit under a sentence promising in writing that the section copies no row.

## Ruled 2026-09-03

### 1. The population is the limits-shaped pointer, not every pointer

The walk opens a pointer whose constant is one of seven declared names — `DECLARED_LIMITS`,
`NOT_REACHED`, `NOT_GUARDED`, `NOT_APPLIED`, `NOT_STRIPPED`, `NOT_VALIDATED_AGAINST`,
`ORPHANED_FIGURES`. Twenty-seven of the fifty.

**A vocabulary makes no such promise, and the prose is supposed to be able to name a member.**
`CLAUDE.md` writes *"`the reference list` staying out is the part of the ruling worth keeping"* —
naming a `checks_ledger.EXPECTED_CHECKS` row on purpose, in a sentence whose whole point is which row
it is. Generalizing to the eighteen converts a real defect into an argument about whether `guideline`
is a row: measured, the wider population fires on `guidelines_extract.CLASSES` for the word
`guideline`, on `threshold_coverage.STATES` for `sheet` and `none`, and on
`research_ledger.SOURCE_CLASS_VOCABULARY` for `government`.

**A declared rationale stays out on principle rather than on cost.**
`docx_write.WHY_FENCED_COMMENTS_ARE_STRIPPED` is pointed at and promised over, and ADR 0074 ruling 1
names filing a rationale as a limit as *the* error.

**`split_census.HISTORICAL_SHAPE_FIGURES` was weighed and stays out on measurement.** It is a figures
object with a no-copy promise, the same kind as `ORPHANED_FIGURES` which is in, so excluding it needs
a reason rather than an omission. Adding it costs two hits, both false — the key `occurrences`, an
ordinary English word, and `digit|digit`, whose own section reads *"That denominator is repeated here
deliberately"* — and buys nothing, because the figure it would catch is stored as an `int` and is
outside ruling 3 either way.

### 2. Membership is a declared literal list with a derived reporter beside it

*Candidacy derived, membership declared* — [ADR 0092](0092-a-glossary-sense-collision-is-recorded-on-the-entry-standing-alone-and-the-candidate-population-is-a-declared-object.md)
ruling 4's arrangement, which ADR 0119 ruling 3 already named for this walk. The seven are typed out;
a companion test reports any `CLAUDE.md`-pointed constant matching a broad limits-ish name shape that
is not among them, so the list cannot go stale in silence.

**The apparent collision with [ADR 0082](0082-the-declared-limit-criterion-is-a-glossary-pair-and-membership-is-decided-on-the-sentence.md)
is recorded rather than left to be rediscovered.** That record rules *"Which it is, is decided on the
sentence and never on the constant's name."* It governs whether a **sentence** is a declared limit or
a declared rationale. This rules which **objects a walk opens**, which is the same candidacy-by-
literal-name ADR 0119 ruling 4 took when it keyed the declarer walk on `DECLARED_LIMITS`. The next
reader will meet the two sentences together and the answer belongs here.

### 3. A row's text is every string reachable inside the object, and nothing about its shape is read

ADR 0119 ruling 1 has just ruled the row type stays per module, and the consequence lands here: the
27 objects carry **six** row shapes — plain 2-tuple, `NamedTuple` with `.limit`, bare string, plain
3-tuple, `(key, evidence)` with no sentence at all, and `dict`. #855's *What must not come out of
this* forbids a matcher over limit shapes, and a per-shape adapter is exactly that.

So the extraction recurses structurally to every `str` leaf and reads no field name, arity or
container kind. `case_study_scan.DECLARED_LIMITS` is why it must: those rows are `(key, evidence)`
and carry no sentence, so a rule reading `.limit` grades the object clean without reading it.

**The extractor's own first version had that defect, in the grilling that ruled against it.** A
recursion covering tuples, lists, sets and dicts silently skipped
`dataclass(frozen=True)`, which is `DeclaredLimit` in `guidelines_recs` and `deck_scan` — the largest
limits object in the directory at 44 rows, and one more. Both yielded **zero** leaves and both graded
clean. The repair recovered 92 leaves of 437 and moved the bill by nothing, which is the point: the
walk could not have known they were clean. ADR 0119 ruling 1's shape table predicted it in writing
and was not consulted.

**What this cannot reach is declared with its two live instances rather than hedged.** A limit held
as anything but a `str` is outside the walk: `split_census.HISTORICAL_SHAPE_FIGURES` stores
`{'digit|digit': 390}` as integers, so the figure `CLAUDE.md` restates one line from the pointer is
invisible, while `guidelines_extract.ORPHANED_FIGURES` stores `'4,168'` as a string and is caught.
**Whether a figure is graded depends on how its own module happened to type it.**

### 4. An object that yields no text is *did not read*, never clean

The `0` / `1` / `2` convention every graded command here states, turned on the walk itself. A pointer
whose object yields zero string leaves fails as unread.

**This is ruling 3's defect converted from silent to loud**, and it is the highest-value line in the
change: with it, the dataclass bug fails on first run instead of shipping a clean report over 46
rows. Reporting the zero and passing is the shape this directory has a limb against in every scanner
it owns.

### 5. The comparison is scoped to the `###` section holding the pointer

Sixty-six sections. Each occurrence of a pointer is graded against its own section; four of the 27
appear in more than one.

**Every cross-section hit in the tree, at every width, is a false alarm**, and they were checked one
at a time: `docx_write.NOT_APPLIED`'s two-word `one paragraph` landing in three unrelated sections;
`ORPHANED_FIGURES`'s `306` matching the ticket reference **#306**; `differential_scan`'s 171-word row
brushing eleven sections on a five-word overlap.

**The sharpest is the one that is not noise.** `scratch_census.DECLARED_LIMITS` holds *"material
outside every checkout is outside this walk"*, and the **Reference-class census** section says the
same thing about **its own** boundary. Two modules can honestly share a limit sentence, and
document-scoping cannot tell *section B copied A's row* from *section B stated B's own limit in the
same words*. Section-scoping can, because the pointer is what licenses the reading.

**The floor is real and is declared**: a section that copies a row without carrying the pointer is
never read. The walk grades a promise rather than a document — which is ADR 0119 ruling 4's
arrangement, and the same floor the pointer-spelling half accepted when it reached 11 declarers
out of 15. The `###` boundary is part of the rule and is stated: content under a `##` heading
before the next `###` falls into the preceding section.

**A second assertion was declined on measurement.** Requiring the section to *make* the no-copy
promise would fail five pointed sections that make none — `aar_scan`, `closing_keyword_scan`,
`test_glossary_collisions`, `tracker_freshness`, `voice_model_scan` — every one of which is clean. It
converts a behavior check into a prose-wording check and fires on correct sections.

### 6. A copy is a nine-word shingle, or an exact substring below that width, and `SHINGLE` is held once

**Nine is the midpoint of the measured plateau.** Section-scoped, widths 8, 9 and 10 give identical
membership; 7 differs, 11 loses a `voice_corpus` row, 13 loses two more. The house's existing
`SHINGLE = 8` sits at the plateau's lower edge, which is `SPACE_ADVANCE_FRACTION`'s recorded failure —
*naming a value at an edge is how a constant goes wrong* — and #83's `0.14` is the instance where the
edge value lost to the library it replaced.

**One constant, in `prose_bind` beside `normalized`.** Three classes carry their own `SHINGLE = 8`
today; a fourth copy is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) with
no test between them. Moving 8 to 9 cannot redden the three: 9 is the weaker test and all three pass
at 8.

**The short-leaf branch survives, and no narrowing separates its two outcomes.** A leaf under nine
words is compared by exact substring, which covers 158 of the 437 leaves. It buys
`ORPHANED_FIGURES`'s `4,168` — a live #143 figure restatement under *"this file deliberately copies
no row"* — and `case_study_scan`'s seven-word key. It costs one collision:
`('letter-spaced word', '306')` against *"306 lines of the three welded running heads"*, which is a
different figure entirely. A minimum word count, a letter requirement and a token-boundary rule
each lose `4,168` with it.

**An instrument property that has to be written down**: `prose_bind.normalized` strips emphasis,
quotes and comment marks but **not sentence punctuation**, so a shingle whose final token carries a
period never matches. `case_study_scan`'s key is invisible to the shingle branch purely because
`CLAUDE.md` writes it as `…written yet.`, and it is caught only by the short-leaf branch.

### 7. Eight failures are a build; the collision is a counted exception and is the clinician's

**The eight are prose edits and change no ruling** — each restores a section to what it already claims
to be, so *recording what you found does not need the clinician* applies and they are buildable. They
are not deletions: the reasoning stays in prose and the row text goes, which is
[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 6's split.

**`306` has no edit available in either direction.** The row is a recorded figure and the prose
sentence is true, so the only repair would be rewording a correct sentence to satisfy a checker,
which this repository has refused since [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215).

**The exception is a declared tuple in the test module carrying a count**, on
`test_glossary_collisions.DECLARED_CANDIDATES`'s arrangement of human verdicts with reasons, and on
[#246](https://github.com/mshamblin5150-code/clinical-skills/issues/246)'s discipline that a bare
exemption is an off switch while a counted one is not. Each entry declares how many times that leaf
appears in that section, so a further occurrence fails rather than inheriting the pardon, and a
ceiling deliberately close to one makes the second exception a decision somebody writes down.

### 8. The walk owns the `CLAUDE.md` surface and takes it from the three hand-written classes

`test_claude_pointers.py`, importing `test_module_sections.SECTION` rather than restating the `###`
rule. Not merged into that module: its subject is *every command module has a section* and this one's
is *every limits pointer's section copies no row* — different populations, different declared lists.

**`checks_ledger`, `research_ledger` and `threshold_sheet` drop `CLAUDE.md` from their surfaces and
keep the rest.** Leaving them ships two mechanisms grading one document at two widths under two
scopes, and they would disagree — not in principle but in fact, since theirs is document-scoped at 8
with a key limb. That is [#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218)'s
recorded failure, where sharing the object was not enough because two implementations survived.
Nothing is lost: `research_ledger`'s class keeps three `SKILL.md` surfaces and the module docstring,
`checks_ledger`'s keeps the module prose, and none of that is in this walk's population.

**The resolve half stays, explicitly.** It is free — reading leaves requires importing the module and
getting the attribute — but without an assertion ahead of it a broken pointer surfaces as an
`AttributeError` inside the leaf walk. All 50 resolve today, and that is what a tripwire is for.

### 9. The instrument is proved live before it is believed

Four controls, each driven red by mutation: a planted verbatim row fires; a planted nine-word overlap
fires; a section that only points passes; and **an object yielding zero leaves is reported unread**.
The last is the control ruling 3's own defect would have failed, and it is the reason it is a control
rather than a comment.

`test_declared_limit_glossary_pair.TheInstrumentIsLive` is the precedent, and this file's standing
rule is the reason: a check keyed on today's tree proves only that the walk found nothing.

## What this record does not establish

A clean walk means **no leaf of a listed object appears in a section carrying that object's pointer**.
It does not establish that the section describes the limit well, that the pointer is the right
pointer, that a section without a pointer is free of copies, or that a limit held as something other
than a string is uncopied. Those are ruling 5's floor and ruling 3's ceiling, and both are stated
where the walk states its own coverage rather than only here.
