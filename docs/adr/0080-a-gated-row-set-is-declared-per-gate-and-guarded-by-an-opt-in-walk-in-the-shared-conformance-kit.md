# A gated row set is declared per gate and guarded by an opt-in walk in the shared conformance kit

[#661](https://github.com/mshamblin5150-code/clinical-skills/issues/661) is the residue
[ADR 0071](0071-a-gated-row-set-is-derived-from-its-sentinel-and-guarded-by-a-walk-in-its-own-module.md)
ruling 1 ordered filed: `tools/discussion_post_scan.py` and `tools/discussion_reply_scan.py` both
carry [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s gated-row-set
convention — an omitted group prints `not graded`, never `0` — with nothing binding it.
[ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)
ruling 6 names this ticket, settles the width as *the rule is uniform and the container is each
module's own ruling*, and hands the decision back. Grilled 2026-08-30 against `origin/main` at
`c4e9fc9`, freshness gate `FRESH` at both checkpoints. `main` advanced to `a2536e7` between the
ruling and the write-up, and every measurement below was re-derived there rather than carried
forward: the census reproduces field for field, and the change touched neither scanner, neither
scanner's tests, `grader_conformance.py`, `case_study_scan.py` nor `differential_scan.py`. **Eight decisions, all the clinician's, all on that date.**
Nothing is built here.

## Measured before ruling, at `c4e9fc9` and re-derived at `a2536e7`

Every figure below is a dated measurement of a tree at a commit, and the instrument is named beside
it on ADR 0074 ruling 6's terms.

**The two gates do not share a consequence, and only one of them is unbacked.**
`reference_boundary_graded=False` sets `coverage_failed=True` in both modules, so its `not graded`
rows always ride an **exit 2** and a stderr diagnostic naming the refused label. `docx_graded=False`
sets nothing: omit `--docx` and the run reaches **exit 0** with `bold-headings: not graded` on the
page. That gate has **no backing field at all** — it suppresses a finding-kind row — so ADR 0071
ruling 2's sentinel-keyed instrument could never have reached it, and its limit is declared only as
prose in `discussion_post_scan`'s module docstring, which states it while telling the reader it
copies no row from `NOT_REACHED`. It appears in no row of it.

**The census of `Scan` shapes across every `grader_conformance.for_module` rider**, taken by parsing
each module's `Scan` class and classifying annotated fields as `bool` or as a union — the instrument
is an AST read of the class body and it is a floor, blind to a field whose annotation is assembled
or aliased:

| module | `bool` fields | union-annotated fields |
| --- | --- | --- |
| `discussion_post_scan` | `docx_graded`, `reference_boundary_graded` | 8 |
| `discussion_reply_scan` | `reference_boundary_graded` | 6 |
| `case_study_scan` | `no_section`, `skeleton_unread` | 0 |
| `research_ledger` | none | 4 |
| `reference_scan` | none | 2 |
| `anchor_scan`, `block_scan`, `checks_ledger`, `differential_scan`, `refusal_scan`, `specificity_scan` | none | 0 |

Two readings follow and both are load-bearing. **`differential_scan` has no `bool` field**, so a
gate-keyed walk is *vacuous* there rather than failing — it is not graded nonconforming, which is
the disanalogy from the sentinel matcher ADR 0071 ruling 5 refused. And **`case_study_scan`'s two
bools are banner flags, not gates**: each appends a trailing sentence and suppresses no row, so
every row still prints its count. An automatically applied gate walk would grade that module
nonconforming for a shape nobody ruled defective — ruling 5's failure mode arriving through a
different key.

**A third nullable meaning is live in `discussion_post_scan`.** `Scan.word_ceiling` is
union-annotated, and its `None` means *the signed bar declares no ceiling*, not *not graded*: the
report prints `none` for it, ungated, and both the degraded and the full construction set it from
the same bar field. A sentinel-keyed walk over that module therefore has a day-one finding that is
structurally identical to ADR 0071's `uptodate_citations` note and materially different from it —
there, the field had to join a kit or be re-typed; here the field is **correct as it stands** and
what is missing is a declaration that its `None` is absent-by-design.

**The kit exists and the ticket's premise is false as written.** `tools/grader_conformance.py`
exports `for_module`, and both discussion scanners already ride it, as do nine other graders. It
already asserts cross-module properties. What these modules lack is the *limits* kit, not a
conformance kit. Its `_empty_value` matches on the annotation string, so a union of an integer and
`None` falls through every branch and yields `0` — the generic builder therefore constructs
gate-off alongside integer sentinels of `0`, which is exactly the state this convention forbids.
And `test_findings_outrank_coverage_after_the_modules_report` already drives `run_grader.run` with a
stubbed loader, so the kit can reach command width generically without a fixture directory.

**`grader_conformance.py` has no prose home.** Its only Markdown mention in the tree is ADR 0071
ruling 5's refusal of a particular build inside it.

## Ruled 2026-08-30

**1. The guard is gate-keyed, with a sentinel no-orphan check beside it.**

The walk is over `Scan`'s `bool` fields, not its union-annotated ones. Sentinel-keying alone was
refused on the measurement rather than on preference: in `discussion_post_scan` it over-reads
`word_ceiling`, under-reads a gated field whose annotation is a tuple union, and cannot see
`docx_graded` at all — which is the one gate in either module that reaches a clean exit. The
no-orphan half is kept because dropping it gives up the `word_ceiling` class entirely: every
union-annotated field must be a member of some gate's declaration or declared absent-by-design.
`word_ceiling` takes the second, declared once in code; re-typing it was available and refused,
because the report's `none` and `not graded` are two correct words for two different things and the
field is not defective.

**2. Each gate declares its gated kinds positively and its gated fields by name.**

The per-gate declaration is a pair, either half possibly empty — `docx_graded`'s field half is
empty, since it suppresses a finding-kind row with no backing field. Kinds are named **positively**
rather than as the exempt set `format_report` holds inline today, so a row added to `ROWS` defaults
to **gated**: that is the fail-closed direction, and the inline literal already has it by accident
rather than by decision. Field names are strings and are cross-checked against the dataclass's own
fields, so a typo or a rename fails rather than silently shrinking the population.

Naming the exempt kinds alone was refused: it is the easy half and not the half that makes the
ticket's *Done when* true. Under a kinds-only declaration a re-typed field simply leaves the
population and nothing notices, which is ADR 0071 ruling 3's declared ceiling inherited rather than
closed — **and the re-type is quieter in these modules than in `research_ledger`**, where the
sentinel *is* the gate, because here the boolean survives the re-type intact and keeps working for
every other row. The named field set is what makes the membership declaration outlive the
annotation.

**Collapsing the boolean into a group sentinel is refused on the record.** It is not what the
ticket's prohibition says literally — that forbids a *guard asserting* `research_ledger`'s shape —
but it is the same convergence arriving voluntarily, and ADR 0071 ruling 1 and ADR 0074 ruling 6
both rest on these modules being entitled to the boolean-gate arrangement.

**3. The limits object takes `case_study_scan`'s shape, and both gates get a row.**

`EvidenceDisposition` is added, the sentence stays the key, and no short slugs and no
`DeclaredLimit` named tuple are introduced. `HANDLERS` binds the `BEHAVIOR` rows only, which is
where ADR 0071 ruling 2's blind-spot-and-positive-control pair has something to say. `post` gains
two rows and `reply` one.

The full keyed conversion was refused as out of proportion: it is ADR 0074's own build repeated
twice inside a ticket whose subject is a gated row set, and ADR 0074 ruling 2 required an
**end-to-end read of the module** to derive that population — real work this ticket has no mandate
for, and which a partial pass would get wrong. Adding a behavior row in the existing unkeyed
two-tuple was refused for the opposite reason: every existing row in both objects is a declared
*reading*, and a behavior row with no disposition beside it flattens *no rule can reach this* into
*this run did not run it*. Those are different claims and the reading-versus-behavior distinction is
the whole reason ADR 0071 ruling 2 asked for a `BEHAVIOR` row rather than any row.

**`reference_boundary_graded` gets a row too, not only `docx_graded`.** Its consequence is exit 2
rather than a clean zero, but it is still a gate whose rows print `not graded`, and giving one gate
a row while the other has none would make the object's silence about the second mean something it
does not mean.

**4. The walk lives in `grader_conformance.py` as an opt-in factory, and membership is declared
rather than discovered.**

A `gate_conformance(module)` factory sits alongside `for_module`, in its idiom, instantiated
explicitly by the two discussion test modules and by nobody else.

Per-module copies were refused: one rule in two copies is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s subject arriving in a
test, and the #253 protection it would buy is one this pair does not need — these two are not two
modules that happen to have written the same thing. They already share a production module and
already import across test modules, and ADR 0071 ruling 1 named them as **one shape**. The
divergence inside the pair is real and small, and the pair declaration absorbs it.

Automatic application inside `for_module` was refused on the census: it grades `case_study_scan` for
banner bools and would demand declarations from `research_ledger` and `reference_scan` that neither
has ruled. It is also fail-open on the one thing it exists for — a walk that must *discover* which
bools are gates discovers a bool that has stopped suppressing rows as a non-gate and passes. A
declared membership closes that: a gate that stops suppressing is still declared, and the walk still
demands its rows read `not graded`.

**5. The shared walk runs at report width with its own constructor; reachability and status are
module-local.**

The factory builds two `Scan`s per gate from the declaration — gate off with the declared fields
null, gate on with them integers — renders the module's own report for each, and asserts that every
declared kind and field reads `not graded` in the first and a count in the second, **and that no
undeclared line differs between them**. That second half is what makes the declaration honest in
both directions: without it a gate could suppress a row nobody declared and the walk would pass on
the declared subset.

It must not reuse the kit's existing generic builder, which constructs gate-off alongside zeros and
would leave the walk asserting against the very shape it forbids.

Command width was refused for the shared half. The two gates differ in exit status — 2 and 0 — so a
shared status assertion needs a fourth item in every declaration, which hoists a module-local ruling
into shared code for no gain. **Reachability lives in each module's `HANDLERS` pair instead**,
driving the real command over a real fixture run directory: omit the flag and assert the status and
the `not graded` line, supply it and assert the count. That is the half no hand-built rendering can
reach — a module could stop wiring a flag to its field entirely and every constructed `Scan` would
still pass — and it gives the two halves different subjects, so neither can pass for the other's
reason.

**6. `NOT_REACHED` is the derived view of every row, and the behavior rows appear in the reader's
walk.**

The view yields the existing pair shape with the disposition dropped, order preserved. Every
external citation resolves unchanged, both modules' completeness sentences stay true, and the two
named constants that are asserted to be elements of the tuple keep their names as rows the object
points at, on ADR 0074 ruling 3's *rows point, names survive*.

Restricting the view to the declared readings was refused: it splits the inventory across two names
and relocates what `AGENTS.md` and three ratified records cite the name for, to spare a reader two
lines. Narrowing the skill's item-by-item walk was refused for a better reason than economy — **a
behavior row has a cheaper remedy than a reading row, not none.** *Re-run with the flag* is an
action a run can take and close; *whether a reference supports the proposition* is a judgment it
must make and cannot discharge. Narrowing the walk would hide the one item on the list that has a
fix, and it is the item most likely to be silently true.

The reason-substance bind applies to the new rows, so naming the omitted flag is not a sufficient
sentence: a behavior row has to say what stops being covered.

**7. It lands as one change.**

ADR 0053 ruling 12, inherited as ADR 0074 inherited it. The module-by-module split was refused
because the second branch would edit a file the first created while both added near-identical
opt-in lines and handler blocks — [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s
*the merge is the unguarded moment* pointed at
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s byte-identical hazard,
which this repository has recorded twice, once on the very mechanism built to prevent it. The
migration-then-guard split was refused because it lands `main` in a state strictly worse than
today's: the convention would be unbound *and* wearing the machinery that implies it is bound, which
reads as coverage.

The size is real. It is also entirely mechanical, and that is the condition under which one change
is safe rather than merely tidy.

**8. `grader_conformance.py` gets a `CLAUDE.md` section.**

The ground is narrow rather than general tidiness: ADR 0071 ruling 5 refused a specific build **in
this module by name**, and this change builds something in it a reader could mistake for the refused
thing. The distinction turns on the census above, and a census that lives only in a test module
docstring is one the next author re-derives with their own matcher — ADR 0074 ruling 6's whole
subject. The section states what the module is, that `for_module`'s membership is universal by
convention while `gate_conformance`'s is opt-in, and why the refusal and this factory are
compatible. **No counts**: not riders, not rows, not gates.

## What the ticket had wrong, corrected here rather than left to be re-derived

**The premise.** *"These two modules have no `DECLARED_LIMITS`/`HANDLERS` machinery to ride, so
their walk would have to invent the kit it forces"* is false as written. They have no limits kit;
they ride a conformance kit already. The correction is what made ruling 4 a live decision rather
than a default, because the question stopped being *may we build a kit* and became *may this kit
have an opt-in member*.

**Decision 1 is dead.** *"Wait for #550, or guard now?"* is answered by ADR 0074 ruling 6, which
names this ticket and says it proceeds module-locally waiting on nothing further.

**The body's ADR 0071 citation.** It attributes the cross-module-width constraint to ruling 5, which
is the relabel of #571. The constraint is real and lives in the unnumbered section beneath the five
rulings, so the repair is a reword and not a renumber — there is no ordinal to point at. Recorded on
the ticket 2026-08-30 and carried here because it is
[ADR 0075](0075-a-ruling-ordinal-has-one-referent-addenda-continue-the-numbering-and-the-citation-resolver-is-a-third-walker-joining-against-the-record-s-own-list.md)
ruling 9's adjacent-ruling slip: in range, resolvable, and wrong.

**The framing understates the finding.** The ticket is filed as two modules carrying a convention
unbound. The sharpest thing in it is one gate — `docx_graded`, the one with no backing field —
producing a clean exit 0 over an ungraded row, with its limit stated only in prose.

## Declared limits

**Opt-in membership is blind to a third module.** A module arriving with this shape and never
calling the factory is invisible to the walk. That is ADR 0071 ruling 3's ceiling one level up: a
declaration, not a mechanism.

**ADR 0071 ruling 3's ceiling survives, narrowed rather than closed.** Ruling 2's named field set
means a re-typed field fails the walk while it is still declared. It does not reach an author who
re-types the field **and** removes its name from the declaration in the same edit; nothing
mechanical distinguishes that from a group legitimately leaving the gate.

**The census is an AST read of each `Scan` class body and is a floor.** A field whose annotation is
aliased or assembled is outside it, and the ruling that a shared walk is safe rests on that floor
rather than on a proof.

**The shared walk proves the report honors the gate. It proves nothing about the wiring.** That is
what the module-local positive controls are for, and their coverage is per gate rather than general.

**A `HANDLERS` pair proves a path is live. It does not prove a row's sentence is true.**

## Consequences

The build lands whole: the per-gate declarations in both scanners, the dispositions and the derived
view, the `gate_conformance` factory with its own constructor and its declared ceiling, the opt-in
call and the `HANDLERS` pairs in both test modules, the migration of both test files' hand-kept
membership sets to equality against the object, the `word_ceiling` absent-by-design declaration, and
the `CLAUDE.md` section. Nothing else in either module moves.
