# A gate result field has a production reader or it is a local

[#1078](https://github.com/mshamblin5150-code/clinical-skills/issues/1078) was filed during
[#1004](https://github.com/mshamblin5150-code/clinical-skills/issues/1004)'s grilling:
`GateResult.skip_reason` in `tools/threshold_sheet.py` sits on the core every per-gate result
inherits, is set by four gates and by `survey`, and is read in production for citation tier 2 alone.
The grilling found a second field of the same shape in the same result types, and found that nothing
is lost to either.

Grilled 2026-09-11 to an empty frontier. **Three rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads. It applies
[ADR 0159](0159-the-sheet-grammar-leaves-as-a-pure-module-and-gate-results-split-per-gate.md)
ruling 3's rule for a field with no production reader, corrects that record's measurement of which
fields `survey` reads, and leaves
[ADR 0172](0172-survey-reads-every-gate-result-and-not-graded-means-the-run-exits-2.md) unchanged.

**Row counts of this module's limit population are not stated anywhere in this record**, on
[ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)'s
closing instruction.

## Measured before ruling, at `6da1f7b`

Freshness gate `FRESH` at `6da1f7b` before any reading and at `5dae592` before recording; nothing
under `tools/` changed between the two. Fields were read with `dataclasses.fields`, readers by an AST
walk of loaded attributes, and every reason by driving `survey` in process and emitting its result with
and without `--quiet`.

**Two fields fail ADR 0159 ruling 3's reader test, and one of them is not the ticket's.** The reader
population is `tools/threshold_sheet.py` and the three non-test modules that import it:
`differential_scan`, `threshold_coverage` and `threshold_draft`. Every field declared on `GateResult`
or a subclass has a loaded attribute of its name there except two. `skip_reason` is loaded in
`_hold_tier2_resolution_declaration` and in `survey`, and both receivers are citation tier 2's result.
**`SecondReadResult.pairings` is loaded nowhere.** *Had a production function read `pairings`, the
walk would have named it; had `skip_reason` been read off another gate's result, it would have named a
receiver other than `result` and `tier2`.*

**The population has to be the importers, not `tools/`.** `specificity_scan` loads `gate.pairings`
and `gate.uncovered` on its own gate object, and `name_index` and `phi_scan` load `uncovered` on
theirs; none imports `threshold_sheet`. A walk over every module would count `specificity_scan`'s
attribute as a reader and pass `pairings`, printing the same result under the claim and its negation.

**The walk cannot see a field read by name through `getattr`, `dataclasses.asdict`, `astuple` or
`vars`.** The module's one `getattr` reads a manifest entry rather than a gate result, at `6da1f7b` and
at `9bb259e` alike.

**Neither reader of tier 2's value reads its text.** `_hold_tier2_resolution_declaration` asks whether
it is `None`; `survey` asks whether it is truthy. The two agree only because both reasons tier 2
writes are nonempty: an f-string naming the PDF root, and `pdf_engine.TIER2_UNAVAILABLE`. An empty
reason would read as skipped to the first and as run to the second.

**ADR 0159's three-tier split was wrong about `pairings` when it was written.** The same walk at
`9bb259e` finds no loaded `.pairings`, while that record listed it among the fields read by `survey`
alone; its own ruling 6 already said the pairings reach no list in `survey`. Its placement of
`skip_reason` among the fields the core's readers read was true of tier 2's value alone, as #1078
recorded. Both are corrected in place in that record.

**Every reason reaches the page without the field.** Driven over `reference/thresholds/diabetes.md`
through five input compositions, each emitted with and without `--quiet`:

| reason | without `--quiet` | with `--quiet` |
| --- | --- | --- |
| extraction identity, not run | report line and stderr | stderr |
| page coverage, unresolved page count | every unresolved document on an unsuppressible trailing line | the same |
| `survey`'s catalog-problem replacement of page coverage | every problem on stderr | the same |
| watermark, not run | report line | neither channel |
| citation tier 2, skipped | report line | neither channel |

*Watermark's row discriminates only where no text root is given. Where a missing root is named,
extraction identity reads the same manifest and prints an identical reason, so a substring search of
stderr finds the text whether or not watermark's line carried it. Tier 2's reason is printed by no
other gate, so its row discriminates wherever it was measured.*

**So nothing is lost to the unread field.** The `--quiet` gap holds for tier 2, whose field is read,
exactly as it holds for watermark, whose field is not: the field was never an output channel.
`--quiet` suppresses the report line that carries the text, and each gate's unsuppressible banner
prints without it. Which lines survive `--quiet` is
[#986](https://github.com/mshamblin5150-code/clinical-skills/issues/986)'s question and is not moved.

**`pairings` is a duplicate of emitted text too.** `gate_second_read` writes each pairing onto a
suppressible report line from the same local list it stores on the result.

**The tests carry both fields.** `tools/test_threshold_sheet.py` reads `skip_reason` on 20 lines and
unpacks `pairings` through the five-value shape on 14.

**One wording defect surfaced while driving it.** With no text root, watermark's line reads
`WATERMARK       NOT RUN -- extracted corpus not found at None`, formatting the value of a variable
the branch has just established is `None`. Filed as
[#1089](https://github.com/mshamblin5150-code/clinical-skills/issues/1089) rather than ruled here,
because it changes an emitted byte and this build's landing term is that none changes.

## Ruling 1. Citation tier 2 carries `skipped`, and every skip reason is a local

`skip_reason` leaves the `GateResult` core. `CitationTier2Result` gains `skipped: bool`, set by
`_citation_tier2_not_run`, and `_hold_tier2_resolution_declaration` and `survey` both read it.
Extraction identity, page coverage, watermark's not-run path, `survey`'s catalog-problem replacement
and tier 2 itself hold their reason as a local that feeds the line each already emits. Tests asserting
on reason text move to the emitted lines or diagnostics that carry it.

**Moving `skip_reason: str | None` to tier 2 unchanged is declined.** No production code reads the
text, and the two readers' presence tests disagree about an empty string. Keeping the string would keep
a value nothing reads on the one type that has the field, which is #1078's shape moved rather than
removed.

**Keeping the field on the core and printing every gate's reason from `survey` is declined.** It would
close the `--quiet` gap above by changing stderr on every run, which answers #986 from a shape ticket.

## Ruling 2. A test requires a production reader for every result field, and `pairings` becomes a local

A test walks every field declared on `GateResult` and each of its subclasses and fails, naming the
field, where no loaded attribute of that name occurs in `tools/threshold_sheet.py` or in a non-test
module of `tools/` that imports it. The importing modules are read from the modules' own import
statements, not typed.

**Against today's code it fails on `pairings` and on nothing else**, which is what makes it
discriminate rather than confirm. So `pairings` becomes a local of `gate_second_read`, whose report
lines already carry the text, and the 14 unpacking lines move to asserting on those lines.

**The test states its ceiling beside the walk.** An attribute of the same name on an unrelated object
in the population counts as a reader, so the walk is a floor rather than proof. A field read only
through `getattr`, `asdict`, `astuple` or `vars` reads as unread. It does not catch a core field read
for one gate only; after ruling 1 the type itself prevents that for `skipped`, since no other result
type declares it.

**A narrow test pinning `skipped` to tier 2's type is declined.** Python already refuses the argument
on every other type, so it would re-check the language, and it would leave `pairings` and the next
field of this shape to be found by hand.

**`pairings` rides in this build rather than being filed.** It is the same defect in the same result
types, and the test ruling 2 requires cannot land green without it. The #986 question about the
pairing lines under `--quiet` does not need the field either: since ADR 0159 ruling 2 it is a property
of those lines.

## Ruling 3. The build does not wait for #1004's

Neither build reads what the other produces. #1004's planted test adds findings, warnings, flags and
diagnostics to real gate results and touches neither `skip_reason` nor `pairings`; this build's walk
still passes after #1004 lands, because that build makes `survey` read more fields generically and
removes no reader.

**The one coupling is textual.** `survey`'s `if tier2.skip_reason:` line, which becomes
`if tier2.skipped:`, sits directly above where #1004's ruling 5 appends its diagnostics remainder and a
few lines above the floor note its ruling 4 rebuilds. Whichever lands second resolves that hunk and runs
both records' tests.

**Declaring a hard dependency is declined.** A few adjacent lines are a rebase rather than a missing
prerequisite, and blocking would hold a ready ticket behind another ticket's build for no correctness
gain.

## What the build verifies

**`python tools/threshold_sheet.py --all` and `--all --quiet` produce byte-identical output and the same
exit status before and after**, against the committed sheets. ADR 0172's correction applies here as
well: on a machine where the committed sheets end on watermark's fatal result and carry no finding, that
comparison is a no-change check and cannot show a reason line being dropped.

**What discriminates is the five compositions above, driven before and after.** For each — no text
root, a named text root that is missing, a missing PDF root, page counts unresolved, and a catalog
problem — the stdout and stderr bytes `_emit_scan` produces with and without `--quiet` are identical
before and after the build. Had the build dropped a reason from a line, that composition's bytes would
differ.

**Ruling 2's test fails on `pairings` before `pairings` becomes a local**, and passes after. The suite,
run through `python tools/suite.py`, is green.

## What this record does not settle

**Which lines survive `--quiet`**, including the two reasons above that reach no channel under it, is
#986's.

**The watermark wording** is #1089's.

**Whether the other command result types in `tools/` have fields of this shape.** The walk is scoped to
`threshold_sheet`'s gate results, and no other module was measured.

**Whether the emitted output is right.** A byte-identical comparison proves the build preserved
behavior, not that the preserved behavior is wanted.
