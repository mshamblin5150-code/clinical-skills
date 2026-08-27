# A declared limit is a keyed sentence and its reasoning stays at the code point

[#535](https://github.com/mshamblin5150-code/clinical-skills/issues/535) was separated out of
[#498](https://github.com/mshamblin5150-code/clinical-skills/issues/498) by
[ADR 0040](0040-a-stated-expiry-is-read-off-the-document-and-a-publication-cadence-is-not-one.md)
ruling 9: `tools/research_ledger.py` holds every limit it has in prose and no declared-limits
object, which is the arrangement
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) and
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) have already ruled
insufficient.

Grilled 2026-08-27. **Twelve decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## Measured before ruling, at `13ebd20`

The ticket says of its own five-bullet list that it is *"a starting list, not a measurement — derive
the population before trusting it"*, and every sweep on it since 2026-08-26 has found the list
short. So the population was derived rather than read.

**By an end-to-end read of all 1,880 lines of `tools/research_ledger.py`, and of every one of the
52 records in `docs/adr/`: thirty-six distinct limits.** Not five. Seventy-six prose statements of
one, once in-file restatements are counted; the most-restated is *a dateless ledger loses exactly
two rows*, at seven sites — the module docstring twice, a dataclass field comment, three function
docstrings and a printed stderr diagnostic.

**That figure is stated here, once, dated and stamped, and nowhere else.** It is a measurement of a
tree at a commit, not a live count, and the live count is the object's to state — #535's own *what
must not come out of this*, and this module has published a figure in five places before a review
re-derived it.

Four of the five bullets the ticket was filed with are **one limit each** out of the thirty-six. The
fifth is genuinely two: the claim-versus-restatement prohibition and `DOSE_NOT_CLAIMED`'s *a number
rather than the number* are separately tested, which settles the question
[#499](https://github.com/mshamblin5150-code/clinical-skills/issues/499)'s sweep left open as a
judgment.

**Three instruments were run and all three were partial, which is the ticket's own thesis arriving
three more times.** A matcher keyed on `NOT_REACHED` and `DECLARED_LIMITS` misses
`threshold_sheet.py`'s and `specificity_scan.py`'s `SECOND_READ_IS_A_SMOKE_TEST`, a constant that
**prints on every clean run** of both graders. A matcher widened with `WHY_`, `NOT_` and `CANNOT`
still misses it. Only reading found the thirty-six. The derivation is a full read and is still a
floor: a limit assembled at run time, or one written in a vocabulary nobody has used yet, is outside
any of it.

## Ruled 2026-08-27

### The population

**1. It builds now, and does not block on the three tickets that each queue a row.**

#498, #500 and #534's piece B each own a limit that is not true yet. The object covers what is true
of the module as it stands; each ticket appends its row when it lands. *Whole* means whole with
respect to today's module — a limit about a field that does not exist is not a limit this module
has, and the objection ADR 0040 ruling 9 raised was one row **while five stayed in prose**, never
one row while three future rows did not exist.

**And the order between #535 and #534 is not neutral, which
[ADR 0052](0052-a-codification-year-is-provenance-and-the-snapshot-behind-it-is-declared-unreached.md)'s
addendum ruled while looking at only one of them.** Its ruling 7 blocked #534's piece B on #498 and
declined *binding the docstring without building the object* as **half of #535's mechanism arriving
through a side door** — reasoning that holds exactly while this object does not exist. Once it does,
piece B stops being prose no test binds and becomes one row appended to a bound object, which is
what ruling 7 wanted and could not have. #534 is told; ruling 7's ground is contingent rather than
wrong.

Blocking was declined as a deadlock dressed as thoroughness: piece B is already blocked on #498, so
#535 would sit behind a chain, and the population has grown at every sweep — waiting for it to stop
moving is waiting.

**2. It stays one module, and `checks_ledger.py` is filed rather than absorbed.**

ADR 0052's correction found *"the only ledger grader without one"* false: `research_ledger.py`,
`checks_ledger.py` and `discussion_reply_scan.py` all hold none. Re-derived at `13ebd20` with one
refinement — **`discussion_reply_scan` is already owned.**
[ADR 0050](0050-a-posted-reading-is-read-off-the-board-and-the-reply-path-has-no-submission-to-stand-in-for-it.md)
ruling 11 orders `NOT_REACHED` built into it and the record is unbuilt rather than wrong. The
unowned residue is one module.

`checks_ledger.py` is `discussion_reply_scan`'s shape — one prose ceiling class, populated whole —
and not this module's, where the population is the hard part. Folding them together would make one
derivation answer to two denominators.
[#550](https://github.com/mshamblin5150-code/clinical-skills/issues/550) is the precedent: it exists
*because* `threshold_sheet.py`'s side was ruled a different question rather than more of this one.

**3. The inclusion criterion is coverage, and rationale is not a limit.**

**A limit tells a reader that a clean result covers less than it appears to. A rationale tells a
reader why the check was built the way it was.** That is `CONTEXT.md`'s own definition of the term —
*a boundary of what a mechanism reaches* — so taking any other criterion meant editing the glossary
in the same change, with #499 already open on that file.

Worked calls, so the criterion is ruled on cases:

- **In.** `DRUG_NAME` *"errs toward matching, so what it costs is a missed finding rather than a
  refused correct record."*
- **Out.** *"An unrecognized `STATUS` is a failure."* It describes a hole the row **closes** and
  names the silent-pass shape only as motivation.
- **In, on its consequence rather than its framing.** *"A body is recognized by its `Authors:`
  masthead, never by a heading."* Read as a rule it is prose; its consequence is that an
  unmastheaded body is invisible to `--evidence` and nothing says so, and that is a coverage
  statement however the sentence beside it is framed. The row is written as the consequence.

**The `WHY_` shape stays out.** `WHY_NO_WRITE_GUARD`, `WHY_OUTSIDE`, `WHY_NO_PUBLISH` and
`WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED` are declared **rationale for a declined option**, held as
named objects. This module has several of those — why no resolver was built, why the declined parser
row was refused — and they stay prose here. Whether that shape is a declared limit at all is
#550's, which already owns *three spellings in one module*.

**4. The class-wide R2 limit is one row, not five and not none.**

`tools/research_ledger.py:605-607` already states it once — *"Judging whether the reason is a real
search or a stock phrase takes a reader"* — and that single sentence underwrites `BARE_STATUS`,
`BARE_EXCUSE`, `BARE_REFUTATION`, `BARE_PAGE_YEAR` and `MISSING_FIELD`. So the ticket's fourth
bullet is not *five or none*; it is *this one or none*.

One row, as a declared reading. Five rows would be five copies of one claim with nothing between
them, which is the #220 shape. None was refused because *declared elsewhere in the directory* is
precisely the arrangement this ticket exists to end: a limit on **this** module's rows, held in
another module's prose, where an edit here fails nothing there.

**It does not absorb #500's limb.** R2 is *anybody can type a reason they did not earn*; #500's
subject is *the record certified its own transcription*, and a lazy reason is still a reason from a
second reader. That row is its own when it lands.

**5. One limit stated only in a record comes in; three do not.**

The #511 sweep's instruction — *the derivation has to read the ADR's declared limits as well as the
module's docstring* — collected. Four limits about this module's grading exist outside it with no
counterpart inside. Three are about **unbuilt fields** and ruling 1 defers them.

The fourth is true of today's code and becomes a row:
[ADR 0036](0036-a-references-label-is-a-per-pipeline-source-spelling-for-one-rendered-outcome.md)
line 47 — `skills/discussion-reply/SKILL.md` runs this grader **without `--draft`**, so
`reference_scan.read_document` is never reached and nothing on the reply path would refuse a
mis-spelled references label. It has no counterpart anywhere in the module and was found only by
reading every record.

### The object

**6. A row is the limit sentence. Its reasoning stays at the code point.**

`CONTEXT.md` requires prose that *"points at the object and copies no row of it"*. Read against
seventy-six prose statements that could mean everything moves — the DOI limit alone is a
thirteen-line comment carrying the limit, why it is not narrowable, and the argument that it only
weakens the weaker half of a pair.

**The limit and its reasoning are different objects, and only one of them can go stale.** The limit
— *the DOI branch matches text that is not a DOI* — is a claim about what the code does today,
falsified the day somebody tightens the regex. The reasoning is an argument; tightening the regex
does not make it wrong, it makes it superseded, and a reader needs it at the code point.

So *copies no row* is satisfied by prose that carries the argument and states no version of the
sentence — and that is **checkable rather than a judgment**, because `differential_scan`'s bind is
an eight-word shingle comparison that strips emphasis, not a substring search, with a mutation
control that plants each key and each reason and asserts both fire.

Keeping a second prose copy of the sentence under a bind test was refused on #535's own terms, and
the reason is worth the sentence: **a bind proves two strings match, never that either is true, so
it buys synchronized staleness.** Moving the reasoning into the object was refused on a measurement
— the argument at `LOCATOR` is the thing that stops the next author "fixing" the regex, and moving
it thirteen hundred lines away from the regex is how that gets fixed anyway.

**7. Every row carries an evidence disposition, and every re-derivable row gets a handler with a
positive control.**

[#323](https://github.com/mshamblin5150-code/clinical-skills/issues/323)'s arrangement whole:
`case_study_scan.EvidenceDisposition`'s two values, carried **on the row** because keeping it there
avoids a second list that can drift, with the behavior set pinned by identity so a new row typed
`behavior` fails the suite until it has its own handler. The control is the pattern rather than a
nicety — the blind spot is asserted with `assertNotIn`, which passes vacuously against a dead
detector, so the control asserts the same input **unwelded** with `assertIn` and proves the absence
was caused by the thing named.

The population splits into a substantial majority that is re-derivable and a minority that is a
declared reading, so this is the expensive half of the ticket and was ruled knowing that.

**A third `tripwire` value, on
[ADR 0043](0043-a-rendered-cell-is-a-page-transcription-and-its-marker-records-the-read-rather-than-an-extraction-failure.md)
ruling 5, was declined on a property of this module rather than on taste.** Tripwires exist there
and in `differential_scan` because those limits are about **committed material** — a fixture
directory, a shipped sheet — so the hazard becomes real only when somebody commits a file and no
honest control can be built until they do. **This module has no committed ledger and there will not
be one**; every test builds its own. A control is therefore always constructible, and a `tripwire`
value here would be the disposition a tired author reaches for when a control is merely awkward,
which nothing downstream can tell from one that was unbuildable.

One row sits in neither value cleanly and is ruled rather than left to the build: *whether
`keyword_of` and `checks_ledger`'s copy agree today is deliberately not asserted anywhere.* Its
subject is a test that deliberately does not exist. It takes the declared reading by elimination,
and the row says so.

**8. The row is a key, a sentence and a disposition.**

ADR 0052's correction caught itself specifying *`reference_scan.NOT_REACHED`'s payload with
`case_study_scan`'s derivation, and calling it established*, and left the shape here. So this is
ruled as a shape and cited as no precedent.

A three-field named row: `key`, `limit`, `evidence`. `DECLARED_LIMITS` is the object,
`NOT_REACHED` is the order-preserving derived view of the sentences, and handlers are keyed on
`key`.

**The deciding argument is ruling 11's.** Under `case_study_scan`'s two-field shape the only durable
name a row has is its own prose. Five ratified records already reason about this module's limits,
and the next one that wants to cite a row can cite a line number or a twenty-word sentence — both of
which are the failure ruling 11 repairs. A short key is a name that survives rewording and is the
thing a record should cite.

**The cost is named rather than buried.** Under a prose identity, rewording a limit forces a touch on
its handler; under a key it does not. That is paid because the prose bind still fails in every file
that points at the reworded sentence, so the rewording is not unwatched — it just does not drag the
behavior test with it. At this row count, positional pairs keyed on prose is the arrangement that
produces a wrong edit.

**9. The object does not print.**

Five of the six existing objects stay off the console; `voice_corpus` prints a handful of limbs.
This module is the heaviest user of
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258) in the tree, so the
question was live rather than settled by the majority.

**The distinction that decides it: #258's printed lines are coverage statements about *this run* —
how many topics were joined, that a row did not run — and a declared limit is a statement about the
*mechanism*, true of every run and of no run in particular.** Those are different objects and only
the first belongs on the console. Printing this object in full would put a screen of ceiling on every
clean scan, which is the arrangement this repository already refuses: a warning printed on every
clean run stops being read.

**The carve-out was measured rather than assumed.** Limits do reach printed strings here — the
`not graded` rows for `--draft` and `--evidence`, and two stderr diagnostics. Each of those is a
statement about the run, and the mechanism-level limit sits in the docstring beside it. **Those lines
stay exactly as they are.** Nothing a run prints today goes quiet, and this ticket does not narrow
what a run tells its reader.

### Where it lands

**10. Five prose surfaces take a point-at-and-no-copy bind. Nothing takes a completeness bind.**

`artifact_provenance.NOT_GUARDED`'s test class is the model — the most complete bind in the tree, and
the only one carrying both directions plus a liveness assertion plus a planted-copy mutation control,
through `tools/prose_bind.py` so a hard wrap or a dropped emphasis cannot decide the outcome. The
surfaces are the module docstring, `CLAUDE.md`'s section, and all three skills that publish this
module's ledger template.

**A completeness bind was refused on the row count rather than on principle.** `case_study_scan`
binds every row against `practicum-case-study` step 9 and it works there because that object is
small. At this size it means a consumer-facing skill enumerating every limit, which is a list a run
skims — and a bind satisfied by a skimmed list is a #220 repair that reads as coverage. The object is
the inventory; the skills keep a headline summary that is not a row, and a pointer.

**Leaving the skills alone was refused because it is the ticket's own secondary claim.** Three skills
publish the template and one is bound to the module at all. Binding only the docstring and
`CLAUDE.md` would put the limits under a check in the two files a maintainer reads while the three a
**run** reads stay free to drift.

`CLAUDE.md`'s section carries eight limit sentences, five of them near-verbatim copies of the module
docstring. That is the #220 shape, live, and it is this change's to repair.

**Two exclusions, ruled rather than assumed.** **No `CONTEXT.md` bind** — ADR 0047 ruling 12 makes a
glossary entry a legitimate target, but the three ledger-limit-bearing terms are all about unbuilt
fields that ruling 1 defers, and #499 is open on that file with the `Declared limit` term itself
duplicated byte-identically; binding into it now is two tickets editing one glossary. **No ADR
bind** — `artifact_provenance` binds one record that owns its ruling, and six records touch this
module. A ratified record is a dated statement of what was true when it was ruled, and
[ADR 0048](0048-a-tracker-citation-to-an-unmerged-path-is-dated-rather-than-rewritten-and-the-branch-scope-check-is-what-grades-it.md)'s
practice is to date a citation rather than rewrite it, so a no-copy bind on six would forbid the
going-stale a record is entitled to do.

**11.
[ADR 0047](0047-a-corpus-document-s-stated-citation-is-read-off-its-own-page-and-a-link-is-not-one.md)'s
two citations are converted from coordinates to names, in this change.**

That record's *why not `locator`* section refuses this repository's own word **because**
`tools/research_ledger.py:537` carries a live tested definition, with
`tools/test_research_ledger.py:688-699` pinning all three directions. **Both citations are exact and
current at `13ebd20`, checked rather than assumed.** They are repaired because *this* change
threatens them, not because they are stale.

The comment they point into carries two different things: the locator **definition**, which is not a
limit and which ADR 0047's whole argument rests on, and the DOI **limit**, which is a row. Placing
the object below the line to keep it byte-stable was refused: it buys a stable module coordinate,
**cannot** save the test coordinate — the bind test goes in that file, above the cited lines — and
pays a placement constraint chosen by a footnote for half the protection. Pointing the object at the
comment instead was refused because it inverts `CONTEXT.md`'s definition of the term.

So the cites name `research_ledger.LOCATOR` and the test class. **A one-line evidence repair with a
dated note, and not a correction header** — nothing in ruling 12 or the *why not `locator`* argument
changes, only where the evidence is pointed. The record is left more durable than it was found.

**12. It lands as one change.**

ADR 0052's addendum is the live precedent for splitting, on the shortest-half-life argument. It does
not transfer, because **every split point here is dishonest.** The behavior set is pinned by
identity, so splitting means either typing rows as declared readings that are not — a lie the object
exists to refuse — or landing behavior rows with no handler, which is the promise-nothing-checks
hazard. Splitting **by row group** is the numerator-with-no-denominator objection that filed the
ticket.

Splitting by disposition is the one that will look attractive to whoever builds it and is the trap:
an object holding only the rows nobody can check, shipped and bound, is the most complete possible
instance of *a declared limit with no live path is a promise nothing checks*, and it would sit on
`main` looking finished.

What splits out is **not code** — see *Filed rather than carried*.

### The ceiling

**13. Nothing mechanical stops a thirty-seventh limit arriving as prose. The ceiling is declared
instead, and it states how the population was derived.**

The shingle bind catches prose that **restates** a row. A genuinely new limit written into a
docstring next month is not a restatement, so it passes every check specified here and the module is
back to holding limits in prose with an object beside it reading *these are the limits*.

**A prose-shape predicate was refused on a property of this design.** Ruling 6 deliberately **keeps**
the reasoning paragraphs at their code points, and those paragraphs are written in exactly the
vocabulary such a matcher would key on — *cannot reach*, *nothing here*, *is not graded*. It would
fire on the material this record chose to leave, and the remedy would be an exemption list, which is
the instrument widening until it is a second copy of the object. A ceiling count on marker phrases
fails the same way and adds an underived figure.

So: *declare the coverage rather than widen the instrument*, which is this repository's standing call
on [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254),
[#278](https://github.com/mshamblin5150-code/clinical-skills/issues/278) and
[#141](https://github.com/mshamblin5150-code/clinical-skills/issues/141).

**What makes it a declaration rather than a shrug is that it states the method and not the fact.**
The population was derived by an end-to-end read of this module and of every record in `docs/adr/`,
on 2026-08-27; a limit written as prose after that date is caught by a reader and by nothing else.
That is `vocabulary_covered`'s and `usable_probes`' arrangement — the coverage claim sits beside the
result and names its own floor.

## Filed rather than carried

Four findings surfaced in this session that are not this ticket's subject. Filing them is the work;
leaving them in a merged record is what makes the next session re-derive them.

- **`checks_ledger.py` holds no declared-limits object.** Ruling 2's residue.
- **An underived count at `tools/research_ledger.py:928`.** `Scan`'s docstring reads *"Nine of the
  ten rows still grade; the window does not"*; `KINDS` holds far more than ten, and the sentence also
  contradicts the module's own *two rows need that date*. It reads as a #231-scoped sentence that
  drifted into a whole-module claim. `CONTEXT.md`'s **Underived count** applies: derive it or drop
  it, and the corrected number is as underived as the wrong one.
- **`DRAFT_ROWS` and `EVIDENCE_ROWS` carry the same #258 reasoning in five places with no shared
  object.** A third gated row set arrives as a sixth copy with nothing failing.
- **ADR 0042 ruling 8 ordered `skills/practicum-case-study/SKILL.md:727` corrected and the edit never
  landed.** A ratified ruling with an unbuilt limb, and the sentence it names — *cannot see whether
  the refutation came from a second agent at all* — is the one #500 is about to make wrong.

## What must not come out of this

**Do not restate the object's row count in prose.** How many there are is the object's to say. The
figure in *Measured before ruling* is a dated measurement of a tree at a commit and is not that
count; it is stated once and is not to be copied forward.
`tools/test_constant_prose_counts.py` already refuses a hand-typed count inside a module-level
constant, repo-wide, on
[ADR 0020](0020-a-count-inside-a-declared-limit-is-derived-or-dropped-and-the-check-walks-constants-rather-than-prose.md),
so the object itself is guarded automatically. The prose is not, and that is a reader's job.

**Do not let the object become a second copy of the docstring.** Ruling 6 is the whole of it: the
object carries sentences, the docstring carries arguments, and the shingle bind is what decides
whether the line was crossed.

**Do not model the object on `adr_next.DECLARED_LIMITS`.** `CLAUDE.md` cites it by name for *its
boundaries are the module-level `DECLARED_LIMITS`; do not copy that moving list into prose* — and
**no test binds it in any direction**, while a `WHY_NO_WRITE_GUARD` sits five lines away outside the
object. It is the weakest instance in the tree and reads like the strongest.

## Declared limits

**This record's own population figure is a floor, and the instrument was reading.** Three
name-keyed matchers were run before the read and all three under-reported; only an end-to-end read
found the set. A limit assembled at run time, or written in a vocabulary nobody has used, is outside
the read as well.

**Ruling 7 buys a control per row, never a correct row.** A handler proves the blind spot is caused
by the thing the row names. Whether the sentence describing it is the *best* description of what the
module fails to reach is a reading, and no test here touches it.

**Ruling 10's bind proves prose points and does not copy. It proves nothing about whether the prose
is true**, and the three skills keep headline summaries that no completeness check counts.

**Ruling 13 is a declaration and not a mechanism.** The ceiling is stated; nothing enforces it.

## Consequences

The build is large and lands whole: the object, a handler and control for every re-derivable row,
the limit sentence removed from every prose site that states one, five surfaces bound, and ADR
0047's citations renamed.

**#534's ruling 7 is contingent on this ticket not having landed, and that is now on the record.**
If this lands first, #534's piece B becomes one row appended to a bound object rather than prose no
test binds — cheaper, and what that ruling wanted.

**#498, #500 and #534 each gain an obligation they did not have**: their row goes into the object
rather than into prose, and the disposition and control come with it. That is the point of building
it whole rather than a cost of it.

**`skills/discussion-reply/SKILL.md` gains limit prose it does not currently carry** — a pointer and
a headline — because ruling 10 binds all three publishing skills and that one states no limit at all
today.
