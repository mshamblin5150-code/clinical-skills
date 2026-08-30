# A module's limit population is one object and the shapes it replaces survive as views and pointers

[#550](https://github.com/mshamblin5150-code/clinical-skills/issues/550) is the shape-proliferation
ticket for `tools/threshold_sheet.py` — the module stating what its gates cannot reach in four live
shapes at once — and it is the ticket four ratified records queued their own rows into rather than
deciding its questions by side effect:
[ADR 0046](0046-the-scope-summary-is-graded-in-one-direction-and-the-unread-list-is-the-span-table.md)
ruling 9 filed the migration question here,
[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 3 assigned the `WHY_` membership question here,
[ADR 0064](0064-a-threshold-sheet-s-sources-are-not-joined-to-its-topic-because-the-catalog-cell-is-the-guideline-s-wording.md)
ruling 2 declared a limit as a bullet rather than start an object because this ticket was open, and
[ADR 0071](0071-a-gated-row-set-is-derived-from-its-sentinel-and-guarded-by-a-walk-in-its-own-module.md)
ruling 1 scoped a guard module-local so the cross-module width would be decided here and nowhere
else.

Grilled 2026-08-29. **Six decisions, ruled by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## Measured before ruling, at `6b3c2b5`

The four live shapes, re-derived rather than inherited from the ticket's sweeps, and named rather
than pinned to coordinates on
[ADR 0075](0075-a-ruling-ordinal-has-one-referent-addenda-continue-the-numbering-and-the-citation-resolver-is-a-third-walker-joining-against-the-record-s-own-list.md)
ruling 8's terms — this ticket's own thread is that ruling's worked instance, ten sweeps reporting
the body's constant anchors stale after the module moved them by 41 to 358 lines:

**Five docstring bullets** under the heading *"What no gate here reaches, stated the same day the
gates were built"*, followed by two prose paragraphs — the *deliberately not built, because it
would pass for the wrong reason* one and the `SECOND READ` independence argument. **Four loose
constants** — `WHY_NO_WRITE_GUARD`, `WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED`,
`PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES`, and `SECOND_READ_IS_A_SMOKE_TEST`, which is the one
of the four that prints, from the `--brief --span` work order and from gate 5's own result. The
**eight-row two-tuple** `SCOPE_SUMMARY_NOT_REACHED`, the only shape carrying a tested no-copy
README pointer. And **untested prose copies** in `reference/thresholds/README.md`'s per-gate
sections and its *"The holes, written down the same day the gates were built"* list, one of which
has already drifted — the README's wrong-heading bullet says *"passes every gate in this
directory"* where the module's corrected sentence says *"every **automatic** gate here"* and adds
the `SECOND READ` qualifier the README lacks.

**Three ratified rows are queued into this population with no home**: ADR 0064's cross-topic
limit (ratified and unbuilt — the docstring list still holds five bullets, parsed rather than
eyeballed),
[ADR 0049](0049-the-sweep-alias-and-the-recs-root-are-two-lookup-roots-with-two-resolution-rules-and-the-producer-guarantees-the-prefix-it-writes.md)'s
alias-unverified-at-the-read residue (ADR prose only — #518's build landed the behavior and no
declared row), and
[ADR 0062](0062-an-orphaned-correction-is-a-corpus-membership-fact-and-the-parent-is-already-corrected.md)'s
source-that-yields-no-rows limit (ADR prose only, parked there in as many words until this
ruling).

**Decision 4 arrived pre-demonstrated.** Seven sweeps re-derived *how many modules hold a limits
object* with unstated and different matchers, published 5, 8, 11, 14 and 24 over one tree,
converged on one another, and were confidently wrong together — including the standing
correction demanding *eight* become *five*, which the last exhaustive sweep falsified at its own
instrument. And the module's own `SCOPE_SUMMARY_NOT_REACHED` scores zero on every name-keyed
spelling tried, because its prefix is the scope rather than the word.

One premise of the thread is dead and is recorded so nobody re-derives it: the tier-2 skip comment
that stated
[ADR 0043](0043-a-rendered-cell-is-a-page-transcription-and-its-marker-records-the-read-rather-than-an-extraction-failure.md)
ruling 1's rejected reading — the skip justifying itself as avoiding a citation failure that is
really an extraction failure — is **already gone**. That repair landed with #501's build; it is
not this build's to make, and a sweep re-deriving it from the ticket's coordinates will find code
with no comment there.

## Ruled 2026-08-29

**1. Membership is ADR 0053 ruling 3's criterion, applied to sentences and never to names.**

A limit tells a reader that a clean result covers less than it appears to; rationale for a
declined option is not a limit. Classifying by the `WHY_` prefix would be decision 4's own error
— a name-keyed instrument — imported into the membership ruling. So `WHY_NO_WRITE_GUARD` stays
out untouched: pure declined-option rationale, cited by name from `CLAUDE.md`, deliberately
divergent copies in two other modules. `WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED` is a limit
wearing a rationale name: its sentence joins the population, its name survives — no rename, no
delete — and its row points at the constant rather than restating it. A consequence ratified in
passing: `adr_next.py` holding `WHY_NO_WRITE_GUARD` five lines outside its `DECLARED_LIMITS` is
**correct as it stands** — rationale does not belong in a limits object — and the ticket's
numerator-with-no-denominator hazard framing for that module retires.

**2. The destination is one module-wide `DECLARED_LIMITS`, built whole, in ADR 0053 ruling 8's
shape.**

Rows of `key` / `limit` / `evidence`, `NOT_REACHED` the order-preserving derived view of the
sentences, `EvidenceDisposition` imported rather than re-invented, handlers per
[ADR 0070](0070-a-four-row-limits-object-takes-the-enumerated-skill-bind-the-sibling-s-size-refused.md)
ruling 2's arrangement where a row is re-derivable. The population is derived by an **end-to-end
read of the module** — the ADR 0053 and ADR 0070 method, and non-negotiable here because the
thread just demonstrated that every instrument short of reading gets this module's population
wrong. The object does not print (ADR 0053 ruling 9); every printed line the module has stays
exactly where it is as the run-scoped face of its limit, and a row for a printed limit points at
the constant that prints. Per-gate sibling objects were refused — more names is the disease —
and the all-onto-the-report route was refused on ADR 0063 ruling 7's own split: most of this
module's limits are mechanism-scoped and have no count to sit beside. The three queued rows land
**unconditionally**, on
[ADR 0058](0058-a-bound-label-reads-to-its-own-recommendation-and-every-window-adr-0029-measured-was-forward.md)
ruling 7's build-whole arrangement — never a row if the object exists, prose if not.

**3. `SCOPE_SUMMARY_NOT_REACHED` folds in, and the name survives as a derived view.**

Its eight rows join `DECLARED_LIMITS` with their **keys verbatim** — a key is the name that
survives rewording and is what a record cites — each gaining an evidence disposition.
`SCOPE_SUMMARY_NOT_REACHED` is redefined as the order-preserving derived view of those rows,
selected mechanically (a key scope, never a hand-kept list), so the name ADR 0046 ruled and the
README sentence a test binds both still resolve, and ADR 0046's rulings survive whole with only
the container redefined. The peer-with-a-pointer arrangement was refused because it re-creates
the disease — eight limits invisible from the canonical object, population claims
matcher-dependent again; fold-and-delete was refused because it breaks a ratified citation for
nothing the view does not also deliver. The boundary row's pointer at
`PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES` becomes an ordinary row whose limit **is** the
constant — the ticket's named two-shapes-of-one-row overlap, resolved on ruling 1's own
arrangement.

**4. The five docstring bullets migrate, and the two paragraphs under them do not.**

Each bullet's limit sentence becomes a row or rows — the end-to-end read owns the split, not the
bullet count, on ADR 0053's finding that a bullet can hold two limits — and the section
collapses to a pointer on `differential_scan.py`'s pattern: what no gate reaches is the object,
not the paragraph. The reasoning braided into the bullets stays at the code points of the gates
it explains (ruling 6's anatomy), and the two closing paragraphs — *deliberately not built,
because it would pass for the wrong reason*, and the SECOND READ independence argument — stay as
prose untouched, because both are ruling 1's rationale class and a limits object that held them
would misfile *why a check was refused* as *what a clean run does not cover*. ADR 0064's sixth
limit lands as a row, which its own shape-neutrality clause blesses.

**5. The README points for module limits and keeps what it owns.**

Every `reference/thresholds/README.md` sentence that restates a module limit collapses to the
point-at-and-no-copy arrangement already built and tested for its scope-summary section, with the
no-copy test extended over the new object. Every passage the README **owns** stays untouched:
the figures the module defers to it by name, their re-derivation commands, the runnable grading
walkthrough, and the directory-scoped holes that are not module limits. The drifted wrong-heading
bullet resolves in the module's favor — the module's sentence is the corrected, richer form. The
full-second-copy-under-equivalence-test option was refused as Q4's refusal one file over: two
full copies held together by machinery, where ruling 10 already priced the cheaper bind.

**6. A matcher-defined figure states its instrument or does not exist, and the cross-module
uniform is the rule, never the container.**

A population figure whose membership is matcher-defined is publishable only with its instrument
named beside it, and is always a floor — the extractor-coverage standing rule applied to prose
and tracker claims. With no instrument stated, no figure: the thread's instance is seven sweeps
striking one unstated figure with another. A mechanical cross-module census was refused because
defining its matcher is a conformance instrument — it would grade `differential_scan.py` as
nonconforming for a shape
[ADR 0063](0063-a-draft-backed-citation-is-caught-per-row-by-the-parser-the-module-already-shares-and-the-class-set-is-draft-alone.md)
ruled correct. Across modules, what is uniform is the rule — a limit is declared, keyed where
object-held, prose points and copies no row; the container is each module's own ruling, on #253's
refusal at the width ADR 0071 ruling 5 already stated it transfers. Printed floors are not a
competing shape but the run-scoped face of a limit, ADR 0070 ruling 5's split. #661 inherits
this width principle and proceeds module-locally, waiting on nothing further here.

### Inherited without re-grilling

ADR 0053 ruling 12 — **it lands as one change** — and ruling 13 scaled: the ceiling is declared
and states its method, the population having been derived by an end-to-end read dated at the
build, with a limit written as prose after that date caught by a reader and by nothing else.

## What must not come out of this

**Do not restate the object's row count in prose, anywhere, ever.** How many limits this module
has is the object's to say. Every count in this record is a dated measurement of a tree at a
commit.

**Do not rename or delete `WHY_NO_WRITE_GUARD`, `WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED`,
`PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES`, `SECOND_READ_IS_A_SMOKE_TEST` or
`SCOPE_SUMMARY_NOT_REACHED`.** Ratified records, `CLAUDE.md`, the README bind and two sibling
modules cite them by name. Rows point; names survive.

**Do not let the fold reopen ADR 0046.** The eight rows, the one-direction grading and the
no-copy bind are settled; the container is all that moves, and the derived view is what keeps
every citation resolving.

**Do not publish a repository-wide limits-object count without its matcher.** Ruling 6 is the
rule; the ticket body's own *eight* is the worked instance and is repaired by respec, not by a
competing bare figure.

## Declared limits

**The end-to-end read is a floor, and reading is the instrument.** A limit assembled at run time,
or written in a vocabulary nobody has used, is outside the read — ADR 0070's declared limit,
inherited whole.

**The binds prove that prose points and copies no row. They prove nothing about whether a row is
true.**

**Ruling 6 governs figures about matcher-defined populations. It does not make any matcher
correct** — a stated instrument is honest about its floor and still blind past it.

**The ceiling is a declaration and not a mechanism.** Nothing mechanical stops the next limit
arriving as prose, a bullet, or a loose constant; what changed is that each of those now has a
ruled destination a reviewer can point at.

## Consequences

The build lands whole: the object and its derived view, the fold of the eight scope-summary rows
with keys verbatim, the docstring collapse to a pointer with reasoning relocated to code points,
the README pointer conversion with the ownership carve-out, the three queued rows from ADR 0049,
0062 and 0064, the row pointing at each surviving named constant, and the test moves — key-set
equality, the no-copy binds, and the boundary-row name pin transferring to the new container.
The stale *"consolidating the four"* figure beside `WHY_NO_WRITE_GUARD`, which
[ADR 0020](0020-a-count-inside-a-declared-limit-is-derived-or-dropped-and-the-check-walks-constants-rather-than-prose.md)
records as stale, is de-figured in passing on that record's own rule: derived or dropped, and the
corrected number is as underived as the wrong one.

[#550](https://github.com/mshamblin5150-code/clinical-skills/issues/550) is respecced for a
build drone and moves from `grilling` to `ready-for-agent`: every decision is closed, and the
end-to-end read applies a twice-worked ruled criterion rather than a judgment left open. #661
proceeds on ruling 6's width principle without returning here.
