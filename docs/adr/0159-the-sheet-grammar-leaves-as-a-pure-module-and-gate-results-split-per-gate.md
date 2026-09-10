# The sheet grammar leaves as a pure module and gate results split per gate

Out of [#836](https://github.com/mshamblin5150-code/clinical-skills/issues/836), grilled on
2026-09-09 to an empty frontier. Measured at `9bb259e` with the freshness gate `FRESH` before
reading and before publishing.

[#410](https://github.com/mshamblin5150-code/clinical-skills/issues/410) found eight gates returning
six tuple shapes and collapsed them into one `GateResult`. #836's charge is that the repair partly
undid itself: the record carries nineteen fields, two of them the emitter's, and
`tools/threshold_draft.py` reaches the sheet grammar through an import list that is a header file.
Every structural claim in that body re-derives. Two of its figures do not, and one of its
measurements could not have worked.

**Row counts of this module's limit population are not stated anywhere in this record**, on
[ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)'s
closing instruction.

## What was measured before ruling, on 2026-09-09

Every figure below was taken by an AST read at `9bb259e`, not by a text search.

**`GateResult` is a common core plus a per-gate tail.** Fourteen functions construct one. Two fields
are set by all fourteen — `gate` and `report`; `findings` by ten. **Eight of the nineteen fields
have exactly one owner**, and **five of those eight belong to `gate_second_read`** — `pairings`,
`undiffed`, `uncovered`, `report_after_stdout`, `stdout_before_footer`. The rest are
`unprobed_sources` (`gate_watermark`) and `tier2_skip_diagnostics` and `fatal`
(`_watermark_not_run`).

**The tuple-position problem #410 killed is alive in the constructor.** `gate_second_read` builds
its result with six positional arguments — `GateResult("SECOND READ", refusals, warnings, pairings,
undiffed, uncovered, ...)` — so a reader still counts positions to learn that `undiffed` is the
fifth.

**And the six tuple shapes did not die; they moved to the reading side.** `tools/test_threshold_sheet.py`
contains **65 lines** that unpack a `GateResult` straight back into a tuple, in **five distinct
shapes**, and they map one-to-one onto #410's six with the same arity and the same order:

| reconstructed in the test module | count | #410's measured shape |
| --- | ---: | --- |
| `(findings, warnings, ungraded_sources)` | 22 | `gate_coverage`, three-`list[str]` |
| `(findings, skip_reason, rendered, unprobed_sources)` | 17 | `gate_watermark`, four-tuple |
| `(findings, warnings, pairings, undiffed, uncovered)` | 14 | `gate_second_read`, five-`list[str]` |
| `(findings, ungraded)` | 8 | `gate_range`, `tuple[list[str], int]` |
| `(findings, skip_reason, rendered)` | 4 | `gate_citation_tier2`, three-tuple |

The sixth — bare `list[str]` for schema and tier 1 — survives as a one-element read. This is the
discriminating measurement of #836's thesis, and it is the one the body did not have.

**Splitting the nineteen by who reads them gives three tiers.** `gate`, `findings`, `warnings`,
`skip_reason`, `diagnostics`, `not_graded`, `fatal`, `report` and `stdout` are read by
`format_report`, `_emit_scan`, `main` or `survey`. `pairings`, `undiffed`, `uncovered` and
`tier2_skip_diagnostics` are read by `survey` alone — which already names every gate explicitly.
And **`rendered`, `ungraded`, `ungraded_sources` and `unprobed_sources` have no production reader
outside the gate that sets them**; their only readers are tests.

**`survey`'s emission list is hand-written, and it is the real interface.** `refusals` is a
concatenation naming eleven gates one at a time. `gate_edition_currency` is not among them, so a
finding on that gate would emit nowhere. `pairings` reaches no list in `survey` at all, so under
`--quiet` the smoke-test caveat prints and the pairings it exists to send a reader to are dropped.

**The emitter's two fields belong to one gate, not to every gate.** `format_report` reads
`stdout_before_footer` to splice a gate's `stdout` in before the footer, and `_emit_scan` reads it
again to choose what prints first under `--quiet`. `gate_second_read` is the only function that sets
either flag. So the coupling #836 names is real and its scope is one gate of fourteen — and
`stdout_before_footer` is not an ordering flag but a **placement**: an unsuppressible line goes
either in position or trailing, and the bool is which.

**`survey`'s parameter list is loop-invariant but one.** It takes eleven positional parameters and
one keyword-only `expected_commit`. In `main`'s `--all` loop, **exactly one of the twelve varies per
sheet**. Both call sites pass nine of twelve, two of them as bare positional literals — `[]` in slot
two and `None` in slot six.

**Three parameters have no production caller**, and that is a legitimate injection seam rather than a
defect: `page_counts`, `catalog_source_classes` and `currency_registry` are never supplied by `main`,
and `survey` lazily loads each when it sees `None`.

**But the catalog pair is a live coupling.** `page_counts` and `catalog_source_classes` are two
fields of one `load_catalog_facts()` read, and the loader runs only when `page_counts is None`.
Supply `page_counts` alone and `catalog_source_classes` stays `None`, so `gate_schema` grades with
its source-class check silently inert. Two tests in `test_threshold_sheet.py` do exactly that. This
is the shape [#881](https://github.com/mshamblin5150-code/clinical-skills/issues/881) recorded,
alive at a second site — and unlike that ticket's `extraction_identity_from_manifest` anchor, which
three sweeps have reported unresolvable, this one re-derives.

**The grammar is pure and the import list splits unevenly.** `parse`, `gate_schema`, `gate_null_span`,
`gate_range`, `source_locator`, `_normalize`, `extraction_identity_from_handoff` and
`render_extraction_identity` reach no filesystem; only `load_catalog_facts` does. Of the names
`tools/threshold_draft.py` imports in its single `ImportFrom`, **nineteen are grammar** — the
`*_HEADING` names, `SECTION_HEADINGS`, `ROW_COLUMNS`, `SOURCE_COLUMNS`, `SCHEMA_MARKER`,
`NARRATIVE_KIND`, `Sheet`, `parse`, `source_locator`, `_normalize` and the `ExtractionIdentity`
trio — and **four are not**: `DEFAULT_PDF_ROOT`, `DEFAULT_RECS_ROOT`, `DEFAULT_RECS_ALIAS` and
`RECS_ALIAS_ENV`. Those four are the same population decision 4 is about, which is a coupling
between two of #836's decisions that its body does not record.

**There is no second consumer of this grammar, and that answers an open sweep question by
measurement.** The 2026-09-05 sweep asked whether the extracted grammar serves one grammar or becomes
the shared one, because ADR 0132 ruling 8 added a second staged-sheet grader. `tools/uptodate_sheet.py`
does not import `threshold_sheet` and shares no heading, column, schema marker or regex with it.
`tools/threshold_coverage.py` and `tools/differential_scan.py` are the only other production
importers, and `threshold_coverage` calls `parse` and `gate_schema` on adjacent lines.

**`gate_schema` is two gates, and its limits are what pins it in place.** It spans 214 lines and
answers both *is this sheet structurally valid* and the scope-summary comparison — the `Not read:`
sentence, span labels, compound labels, with `_not_read_scope_items` as its helper. Every row in the
`SCOPE_SUMMARY_NOT_REACHED` view of `DECLARED_LIMITS` is a limit of that second half.

**#410 decision 3's two grounds both stand.** In `tools/run_grader.py` the word `quiet` occurs only
inside the `REFUSED["threshold_sheet"]` string; `run()` prints `format_report` unconditionally; and
`parse()` refuses extra positionals with `"one source at a time"` and keeps `positionals[0]`.

**Three of #836's own figures are wrong and one of its measurements is void.** The **title's 24** is
23, and was 23 at the ticket's own measurement commit — six sweeps have said so. The body's *"`survey`
takes ten parameters"* is twelve; it has grown twice while the ticket sat. And the testability
section's headline — *"`threshold_sheet.main(` appears zero times"* — is a matcher that prints 0
under the claim and under its negation, because `tools/test_threshold_sheet.py` imports the module as
`gate` and calls `gate.main(` thirteen times. It was already non-discriminating at the commit the
body measured.

**One argument for urgency was false.** `tools/apa7_coverage.py` already exists and satisfies
[ADR 0154](0154-the-apa-sheet-rests-on-the-manual-and-its-coverage-is-a-digest-bound-registry.md)
ruling 8 by making its `--quiet` **inert** rather than by copying the two-channel shape. The copier
landed and took a third route, so "rule this before a second author arrives" was not available.

**A limits object is not universal.** Thirty-two of eighty-six non-test modules in `tools/` carry
one, and every shared pure module carries none — `repo_root`, `console_codec`, `prose_bind`,
`git_paths`, `tracker_records`, `scratch_work`.

## Ruling 1. The sheet grammar leaves as `threshold_grammar`, and no gate goes with it

`parse`, `Sheet`, `Row`, `Span`, `SourceLocator`, `ExtractionIdentity`, the heading and column
vocabularies, `SCHEMA_MARKER`, `NARRATIVE_KIND`, `_normalize`, `source_locator` and the
extraction-identity trio move to `tools/threshold_grammar.py`. It is pure text with no I/O.

**The schema gate stays, and the reason is the limits object rather than the seam.** `gate_schema`
is the one gate whose behavior the `SCOPE_SUMMARY_NOT_REACHED` view bounds. Moving it would leave
those rows in `threshold_sheet.DECLARED_LIMITS` describing code in another module, which is
ADR 0074 ruling 2's *one module-wide `DECLARED_LIMITS`* broken by side effect, and it moves the home
of one of the five names that record protects. **The cost is accepted and named**: `threshold_coverage`
imports `threshold_grammar.parse` and `threshold_sheet.gate_schema` to perform one act. That is a
thin edge, not a header file, and decision 1's payoff survives whole — 23 names become two.

`load_catalog_facts` stays, because it reads the filesystem and the new module does not.

## Ruling 2. Emission collapses to one channel, and suppressibility is a property of a line

`report`, `stdout`, `report_after_stdout` and `stdout_before_footer` are replaced by one ordered
`lines: tuple[Line, ...]`, where `Line` carries its own `suppressible` and `placement`. The two
placements the code has today — in position, and trailing after the footer — survive as two values
of one enum rather than as a bool plus a second report tuple.

**This is what #836 asks for and what #410 decision 1 was reaching at.** *"An ordering flag
travelling on the result is a second emission channel, reached by data rather than by a `print`"* is
answered by there being one channel. The two emitter fields cease to exist; the record drops from
nineteen fields to sixteen before ruling 3 touches it.

The charge as filed is narrowed by the measurement: the coupling is one gate's, not every gate's.
It is ruled anyway, because a type that entitles fourteen gates to steer the renderer is the shape
that has to be wrong, not the count of gates currently doing it.

## Ruling 3. `GateResult` splits into a core and per-gate result types

The core is what `format_report`, `_emit_scan` and `main` read. Each gate returns its own frozen
record carrying that core plus its private tail, and `survey` — which already names every gate
explicitly — reads each tail off the concrete type it named.

**The seam is who reads the field, and it is already cut.** `survey` names every gate;
`format_report` names none.

**The four fields with no production reader become locals**, and the tests assert on the gate's
emitted line rather than on a field kept alive only to be asserted on.

**A typed `Finding` stays refused, on unmoved evidence rather than on precedent.** #410 decision 2
refused it because there is no row set here to bind against. `threshold_sheet` still declares no
`ROWS` and no `KINDS`, so the ground is unchanged. This was checked, not assumed.

**The price is named**: roughly 65 test lines change and four asserted-on fields disappear.
Byte-identity of emitted output survives; *no test moves* does not.

## Ruling 4. `survey` takes `(sheet_path, inputs)`, and `Roots` stays in `threshold_sheet`

```python
Roots(pdf_root, recs_root, text_root, recs_alias)
SurveyInputs(roots, recs_arguments, second_read_path, allow_untrusted_provenance,
             catalog_facts, currency_registry, expected_commit)
survey(sheet_path, inputs)
```

Twelve parameters become two, and the two bare positional literals disappear.

**`catalog_facts` replaces both catalog parameters**, so the combination that silently disables
`gate_schema`'s source-class check becomes unrepresentable rather than merely undocumented. That is
the half of this ruling that closes a live defect rather than shortening a signature.

**`Roots` is decision 1's remainder**, so `threshold_draft` imports `threshold_grammar` and `Roots`
and nothing else. It stays in `threshold_sheet`: a new file for four path constants moves complexity
rather than removing it.

## Ruling 5. #410 decision 3 is untouched, and its two grounds are no longer equally durable

Nothing here changes `run_grader`. It has no quiet path and grades one source to one status, so
`threshold_sheet` stays in `REFUSED` and the entry's wording is not edited from this ticket.

**What changed is what would have to migrate.** The grammar leaves and would never migrate.
`survey(sheet_path, inputs)` is `Grader.grade`'s shape rather than a twelve-argument outlier.
`Finding` still does not apply. And ruling 2 makes suppressibility a property of a line — which is
not the runner growing a quiet path, but is the exact data shape one would need. **The reopening
condition drops from *design a quiet contract* to *filter on a flag the member already publishes*.**

So worst-of-N across `--all` is now the load-bearing ground. The quiet-path ground is a missing
runner feature with a known shape.

## Ruling 6. The build is a pure refactor, and byte-identity is the landing term

`python tools/threshold_sheet.py --all` and `--all --quiet` are byte-identical before and after,
against the committed sheets, on #410's own landing terms. Every line keeps the exact channel it has
today.

**Two reporting holes are therefore left alone by this build, deliberately.** The `pairings` drop
under `--quiet` goes to [#986](https://github.com/mshamblin5150-code/clinical-skills/issues/986),
whose own open question is which lines survive `--quiet` — answering it here would settle a grilling
ticket from a ticket that is not it. `gate_edition_currency`'s unreachable findings channel is
inherited rather than entangled and is filed on its own.

**A behavior change smuggled inside a shape change is how a byte-identity term stops meaning
anything.** Ruling 2 is what makes both holes one-line changes afterward.

## Ruling 7. One pull request, four commits, in dependency order

`ruling 1` → `ruling 2` → `ruling 3` → `ruling 4`. Each is independently byte-identity-verifiable.

**Ruling 2 must precede ruling 3**, because ruling 3 partitions the field set ruling 2 leaves behind;
done the other way it partitions three fields about to be deleted. Ruling 4 is independent of all
three. With no gate moving under ruling 1, the grammar extraction has no prerequisite and goes first,
where it shrinks the file before the harder edits — which is #836's own *"cleanest lift"*, holding.

Four separate pull requests were declined: three of the four would leave the module mid-transition on
`main`, multiplying the merge window across a file that `threshold_draft`, `threshold_coverage` and
`differential_scan` all import, for no gain that four commits inside one review does not give.

## Ruling 8. `threshold_grammar` carries no limits object, and `DECLARED_LIMITS` neither moves nor splits

The new module is pure grammar with no gate, no command line and no run contract, so it declares no
limits — `repo_root`, `console_codec`, `prose_bind`, `git_paths`, `tracker_records` and
`scratch_work` are the precedent, and
[ADR 0093](0093-the-tracker-gate-section-population-is-derived-from-three-sources-and-a-ratified-limit-is-lifted-into-the-module-it-governs.md)
ruling 4's *a section does not oblige a limits object* is the rule.

`threshold_sheet.DECLARED_LIMITS` stays whole and in place. All five names ADR 0074 protects —
`WHY_NO_WRITE_GUARD`, `WHY_BOUND_REC_MEMBERSHIP_IS_NOT_GRADED`,
`PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES`, `SECOND_READ_IS_A_SMOKE_TEST` and
`SCOPE_SUMMARY_NOT_REACHED` — resolve unchanged, checked against the tree rather than promised.

## What this record does not settle

**Whether `gate_schema` should be two gates.** The measurement says it is: one half's limits already
have their own derived view. Splitting it would let the structural half join the grammar and would
leave the scope rows with the code they bound. It is not ruled here because `threshold_coverage`
reads `gate_schema(...).findings` and refuses on it, so the split changes what a second command
refuses on — a behavior change inside a build whose landing term is byte-identity. Filed.

**Which lines survive `--quiet`.** #986's question, unmoved by ruling 6 and made cheaper by ruling 2.

**Whether `run_grader.REFUSED`'s classification is durable.** ADR 0112 ruling 2 calls a refusal *a
permanent verdict*; #410 decision 3 says the question *reopens on evidence*. A reader of the ADR
alone would not learn that the entry is conditional. Filed rather than settled here, because editing
a grader-family record from a module-shape ticket is #836's own *"migrating onto `run_grader` by side
effect"* arriving through the wording instead of through the code.

**Whether the emitted output is right.** Everything here is shape. A clean byte-identical diff proves
the refactor preserved behavior; it proves nothing about whether the behavior preserved is the
behavior anybody wants.
