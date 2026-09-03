# The limit row type stays per module, the evidence disposition moves to the grader runner, and the declarer walk is candidacy derived

Found while grilling [#831](https://github.com/mshamblin5150-code/clinical-skills/issues/831),
2026-09-03, at `origin/main` `d27c2a4`, freshness gate `FRESH` before reading. **Ruled by the
clinician on that date.** Nothing is built here; this is the record the build reads.

[ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)
ruling 2 specifies a limits row as `key` / `limit` / `evidence` with **"`EvidenceDisposition`
imported rather than re-invented"**, and ruling 6 leaves the container to each module. #831 read
those two as one subject and asked one question about it. They are two subjects and this record
answers them in opposite directions.

## Measured before ruling, at `d27c2a4`

Every figure was re-derived by running the code rather than by reading it, and three of them
disagree with the ticket and with its own sweep comment.

**The count is 8, not 7.** *Matcher, stated because ruling 6 requires it: an AST walk of top-level
`ClassDef` named `DeclaredLimit` over non-test `tools/*.py`. Every count below is a floor — a row
type under another name is invisible to it.* `implementation_map` landed on
[#808](https://github.com/mshamblin5150-code/clinical-skills/issues/808) on 2026-09-03, after the
ticket's base `7ad784e` and after its sweep comment's base `6cd340a`. Both were correct when taken.
The population grew twice while the ticket was open, and nobody consulted it either time.

**The eight do not agree.** They share `key: str` and `limit: str` and split on everything else:

| shape | modules |
| --- | --- |
| `NamedTuple` + `evidence` | `checks_ledger` `closing_keyword_scan` `research_ledger` `threshold_sheet` |
| `NamedTuple`, no `evidence` | `implementation_map` `map_scan` |
| `dataclass(frozen=True)` + `evidence` | `guidelines_recs` |
| `dataclass(frozen=True)`, no `evidence` | `deck_scan` |

**All five importers import `case_study_scan` for nothing but the enum.** Not most of them —
`refusal_scan`, `discussion_post_scan`, `discussion_reply_scan`, `checks_ledger` and
`research_ledger` each carry exactly one `case_study_scan` reference and it is the import line.
Importing it pulls `docx_write`, `coursework_run`, `repo_root` and `run_grader` behind 886 lines, for
a two-member enum. Every one of the five, and `case_study_scan` itself, already imports
`run_grader`.

**No existing module all three enum definers already import.** `run_grader.MEMBERS` reaches
`case_study_scan` and all five importers and excludes `closing_keyword_scan` and `guidelines_recs`;
`console_codec` reaches those two and 41 others and is imported by none of the six, which delegate
`use_utf8` to the runner. `run_grader.REFUSED` names `threshold_sheet` — holder of 25 rows carrying
an evidence disposition — as not a member by name.

**`aar_scan` and `adr_next` are pointed at and bound by nothing.** `CLAUDE.md` says *"The complete
scanner boundary belongs to `aar_scan.DECLARED_LIMITS`"*; `test_aar_scan.py` is 17 KB and contains
zero occurrences of `DECLARED_LIMITS` or `NOT_REACHED`, and no file anywhere asserts that pointer
resolves or that the section copies no row. `CLAUDE.md` says `adr_next`'s boundaries are its
`DECLARED_LIMITS` and *"do not copy that moving list into prose"*; there is no `test_adr_next.py`.
Every other declarer carries at least one binding assertion. `aar_scan` landed on
[#814](https://github.com/mshamblin5150-code/clinical-skills/issues/814) on 2026-09-02, the day #831
was filed.

**Ruling 6's census argument has a live instance in this ticket's own evidence.**
`discussion_reply_scan.DECLARED_LIMITS` holds rows that read as two-tuples to an AST walk and expand
to three at run time through `*UNMARKED_INVOKED_SOURCE_LIMIT`. The census taken for this grilling
misread them and was corrected by importing the module. A matcher over limit shapes gets this
directory wrong, measured rather than argued.

**The prose pointer is not one spelling.** A regex for a backticked `<module>.<CONSTANT>` over
`CLAUDE.md` finds 50 pointers naming a real `tools/` module and **all 50 resolve** today. It reaches
11 of the 15 non-test modules holding a `DECLARED_LIMITS` and misses four, in three different ways:

| module | how `CLAUDE.md` names it |
| --- | --- |
| `adr_next` | module and constant in **separate** backticked spans |
| `discussion_post_scan` | module elided by conjunction — `` `…ROWS`, `KINDS` and … `` |
| `discussion_reply_scan` | the same conjunction shape |
| `threshold_sheet` | **not named at all** — 25 rows, no `CLAUDE.md` pointer |

The first of those is half of what a pointer-keyed walk was proposed to catch.

**Re-derived at `abe3716`, after the rulings and before this record was published.**
[#853](https://github.com/mshamblin5150-code/clinical-skills/issues/853) landed mid-session, adding
`office_process` and `word_automation_scan` and eleven lines to `CLAUDE.md`. **Every figure above is
unchanged** — 8 definitions, 3 enums, 5 importers, 15 non-test declarers, 50 pointers all resolving,
the same four misses, and `test_aar_scan` still at zero mentions. The check is run rather than
assumed because a new module carrying a limits object or a new `CLAUDE.md` pointer would have moved
three of these at once, and neither branch's suite could have said so.

## Ruled 2026-09-03

### 1. The row type stays eight, and only `EvidenceDisposition` is shared

ADR 0074 ruling 6's *"the container is each module's own ruling"* is read as reaching the row type,
and #831 decision 1 is answered **no**.

**It is a distinguish-and-affirm rather than a fresh reading**, because the shared named tuple has
already been refused once by name.
[ADR 0080](0080-a-gated-row-set-is-declared-per-gate-and-guarded-by-an-opt-in-walk-in-the-shared-conformance-kit.md)
ruling 3: *"`EvidenceDisposition` is added, the sentence stays the key, and no short slugs and no
`DeclaredLimit` named tuple are introduced."* Neither the ticket nor its sweep comment cites it.

**The measurement is what settles it.** The eight are not seven copies of one thing that happen to
agree; they are four shapes sharing two field names, and two field names agreeing is what any
`(name, sentence)` pair looks like. A shared type would either force an `evidence` field onto three
modules whose rows carry none, or ship the field optional — the nullable sentinel
[ADR 0071](0071-a-gated-row-set-is-derived-from-its-sentinel-and-guarded-by-a-walk-in-its-own-module.md)
refused, arriving one artifact over. Sharing the type is not recording an agreement; it is creating
one.

**The enum is the opposite case and ADR 0074 ruling 2 already ruled it.** Two members, no fields,
identical semantics in all three definitions, and nothing about a case study makes it a case-study
concept. Ruling 2's *imported rather than re-invented* is obeyed in the tree; what it never said is
what the import should point at, and that is the whole live defect.

### 2. The enum's home is `run_grader`, and two definitions survive on purpose

`EvidenceDisposition` moves out of `case_study_scan` into `run_grader`. The five importers change
one line each and gain no dependency they do not already have. `case_study_scan` stops being
upstream of five siblings with nothing to do with case studies.

**`closing_keyword_scan` and `guidelines_recs` keep their own, declared rather than apologized for.**
Neither imports `case_study_scan`, so neither is paying the cost this ticket measured, and moving
them to `run_grader` would give two non-graders a dependency on a runner they do not use. The home
is chosen by family, which is
[ADR 0116](0116-the-read-failure-posture-is-keyed-on-the-input-s-role-and-only-the-crash-is-ruled-family-wide.md)
ruling 4's discriminator applied honestly rather than borrowed for its conclusion.

**The category objection is recorded rather than dissolved.** The concept is a declared-limit
concept, not a grader concept — the two largest evidence-dispositioned populations in the directory
are `guidelines_recs` at 44 rows and `threshold_sheet` at 25, and the second is named in
`run_grader.REFUSED` as outside the family. A new module was refused on ruling 2's *more names is the
disease*: three definitions become two, and the cost being paid today is entirely inside the family
whose runner this is.

### 3. A declarer walk is in scope, and it is not the census ruling 6 refused

#831 decision 3 is answered **yes**, and its own proposed key is dead: under ruling 1 there is no
shared row type to key on.

**The distinguishing question is what the key reads.** Ruling 6 refused a mechanical cross-module
census because *"defining its matcher is a conformance instrument"* that *"would grade
`differential_scan.py` as nonconforming for a shape [ADR 0063](0063-a-draft-backed-citation-is-caught-per-row-by-the-parser-the-module-already-shares-and-the-class-set-is-draft-alone.md)
ruled correct."* A walk that reads no row and no container shape cannot do that. It is
`test_module_sections.py`'s arrangement — ADR 0092 ruling 4's *candidacy derived, membership
declared*, here with candidacy derived and membership not needed at all — and that walk's own
declared limit already says in writing that it does not establish a module's **coverage boundary**.
The gap #831 names is declared out of scope by the mechanism standing nearest it.

### 4. Candidacy is the module constant, the prose pointer is the second half, and the halves land apart

**Candidacy is a `tools/` module with a top-level constant named `DECLARED_LIMITS`.** Fifteen
non-test modules, sixteen with the one test module that has one, derived, keyed on that literal name
and never on a row's shape — so `differential_scan.NOT_VALIDATED_AGAINST` sits outside the walk
unfailed and ruling 6's named victim survives for the same reason it would have under a pointer key.
Test modules are in: it is one module, `test_glossary_collisions`, and it already binds itself.

**Assertion 1 — a test names the object — lands now.** Its failures are known and bounded:
`aar_scan` and `adr_next`, the whole of what the measurement found. `adr_next` gains a test module.

**Assertion 2 — the prose pointer copies no row — goes to its own ticket.** It is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s discipline generalized to
the promises rather than to the objects, and its bill is unknown until it runs red: each failure is
either a real prose edit or a declared exception, discovered at build time. Ruling the two as one
change lets the unbounded half hold the bounded half hostage, which is how a mechanism that repairs a
known defect fails to ship.

**The pointer key was ruled first and reversed on measurement**, and the reversal is the reason this
ruling is written the way it is: a pointer-keyed walk reports a clean 50 of 50 while reaching 11 of
15 and missing `adr_next`, one of the two defects it was chosen to catch. A matcher that could not
have worked, reading as coverage, arriving inside the mechanism proposed to prevent it.

### 5. The two surviving enum copies declare themselves at the code point

**Not in either module's `DECLARED_LIMITS`.** *This module defines its own because it is not
grader-family and importing the runner would add a dependency it does not use* is a why. `CONTEXT.md`
rules a declared limit to be *"a sentence telling a reader that a clean result covers less than it
appears to"* and a declared rationale to be *"why an option was declined… never a member of one"*,
and ADR 0074 ruling 1 names filing the second as the first as the error, decided *"on the sentence
and never on the constant's name."* The slot this ticket's whole subject points at is the one slot
ruled out.

**Not a third name-to-reason map in `run_grader` either.** `REFUSED` and `DEFERRED` register
**grader-family membership** — that is what those modules are outside of, and the map is the family's
register of its own edges. *Who defines their own enum* is not a fact about membership in anything.
Putting it there would make the runner the register of a concept it does not own, which is the
category error ruling 2 accepts once for measured cost and must not accept twice.

**Not a `WHY_` constant.** A named rationale constant is a thing prose points at —
`guidelines_recs.WHY_OUTSIDE` earns its name by being cited from `CLAUDE.md`. Nothing cites this
sentence and nobody outside the two modules needs to, so a constant here is a name for its own sake.

**So it is a comment at each class definition**, on
[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 6's *reasoning stays at the code point* and ADR 0074 ruling 4's application of it. The reader
it is written for is the next person meeting `class EvidenceDisposition(Enum):` in
`closing_keyword_scan` and wondering why it is not the import three siblings use.

### 6. **Evidence disposition** gains a `CONTEXT.md` entry, and no new bind

The term is defined only in code and in five ADR rulings while `CONTEXT.md` carries entries for
**Declared limit** and **Declared rationale**. The term whose home this record rules is the one the
glossary does not hold.

**No bind module is added.**
[ADR 0082](0082-the-declared-limit-criterion-is-a-glossary-pair-and-membership-is-decided-on-the-sentence.md)
gave the limit-and-rationale pair one because a ratified membership criterion turns on the
distinction between its two halves. Nothing ratified turns on this entry's wording; it names an
existing enum and points at it.

## What this does not reach, declared rather than left to be found

**Ruling 1 is not a claim that eight is right.** It is a claim that a shared type is wrong, which is
a different sentence. Eight is what the tree has and what ruling 6 entitles it to; that a ninth can
arrive without anything noticing is true after this record as before it, and assertion 1 grades its
*bind* rather than its *shape*.

**#831 decision 4 is answered by ruling 1 and gets no ruling of its own.** Nothing converts. The
modules holding a limits population as bare tuples, keys or a dict keep their shapes, and the five
grader-family modules ADR 0116 ruling 4 measured as carrying no limits object at all are outside
ruling 4's candidacy by construction — silently and correctly, on
[ADR 0093](0093-the-tracker-gate-section-population-is-derived-from-three-sources-and-a-ratified-limit-is-lifted-into-the-module-it-governs.md)
ruling 4's finding that a section with no limits object is legitimate.

**Assertion 1 cannot tell that a bind is any good.** A test naming the object passes whether it
asserts the pointer resolves, the rows are derived, or nothing at all. It is a floor on the
obligation having been discharged, which is `test_module_sections.py`'s own ceiling adopted whole.

**Assertion 2's floor is the pointer spelling and it is measured, not closed.** Four spellings are
recorded above and `threshold_sheet` has none, so a module whose limits object is named in `CLAUDE.md`
in a fifth shape, or not named at all, is outside that half of the walk and its silence means
nothing.

**Ruling 5 fails nothing.** Move the enum, delete the comment, and no test goes red — ADR 0093 ruling
3's *"the bind test cannot tell that a row has stopped being true"*, one level weaker still. The
comment is for a reader, and this record is the durable copy.

**Nothing here rules on the two non-graders' membership in anything.** `closing_keyword_scan` and
`guidelines_recs` are outside `run_grader.MEMBERS` today because of what they are, not because of
this record, and whether either should join is untouched.

## What must not come out of this

**A shared `DeclaredLimit`.** Refused here and already refused by ADR 0080 ruling 3. Re-proposing it
answers to two records.

**A matcher over limit shapes, or over container names beyond the one literal `DECLARED_LIMITS`.**
Ruled twice, with a named victim, and with a live misread of `discussion_reply_scan` in this
record's own measurement.

**A uniform container.** Untouched. No module's limits object moves, splits, or changes shape.

**A repository-wide limits-object count without its matcher.** ADR 0074's own prohibition; every
figure in this record states its instrument and is a floor.

**Widening assertion 2 to close its spelling floor by rewriting `CLAUDE.md` pointers into one
shape.** That converts a declared floor into a prose migration nobody asked for, and
`threshold_sheet` — which has no pointer at all — is not reached by it either way.
