# A none topic is a null threshold sheet and the state is derived from its span table

[ADR 0009](0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md) created three registry states and refused an empty sheet, so `none` — *the named source documents were read and state no decision point* — got no artifact. [ADR 0025](0025-a-section-read-is-the-unit-and-a-sheet-s-page-coverage-is-what-the-state-asserts.md) then made `sheet` derivable from a span table checked against the catalog's `page_count`, and closed by naming the residue:

> **Nothing here says anything about `none`.** A `none` topic has no artifact, so it has nowhere to carry a page-coverage table, which leaves the registry's most substantive claim its least checkable one. That is the symmetric hole and it is filed rather than ruled here.

[#483](https://github.com/mshamblin5150-code/clinical-skills/issues/483) is that hole. Grilled on 2026-08-25. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The measurement came first and falsified the ticket's own account of the stakes

**Nothing consumes `none`.** `grep` finds no reader of the string anywhere in `tools/` outside `threshold_coverage.STATES`, which counts it. [ADR 0017](0017-a-run-joins-a-threshold-sheet-on-the-artifact-column-and-the-state-describes-the-read-behind-it.md) keyed the consumer on the `artifact` column *"whatever the row's state"*, and `differential_scan._threshold_artifact_topics` (`tools/differential_scan.py:810-817`) filters `if entry.artifact` with that sentence as its docstring.

So the ticket's stated stakes — *"a topic in `none` tells a clinician the guideline is silent"* — **is false of this tree.** A `none` topic has no artifact, joins nothing, and a Plan item on it writes `recalled, no shipped sheet`, which the row-24 floor cannot contradict because there is no artifact to contradict it with. `none` today tells a registry reader something and tells a run nothing.

That also breaks the discriminator a sweep comment offered against [ADR 0027](0027-the-uspstf-interval-column-names-the-recurrence-of-a-service.md) ruling 6 and [ADR 0028](0028-the-uspstf-interval-derivation-reaches-one-sentence-and-that-reach-is-ruled-permanent.md) ruling 6, which merge sentinels where the merged states are indistinguishable to a consumer. To a consumer `none` and `unread` are **exactly** indistinguishable — both join nothing. They differ only to someone reading `coverage.md`. The 0027 pattern is answered below, on the ground that ruling 1 *creates* the distinction mechanically rather than on the ground the sweep gave.

**The null sheet's shape is already closed by the existing grammar.** ADR 0026 rule 6 requires a row's page to sit in a span whose `read` cell is `yes`, and `gate_schema` (`tools/threshold_sheet.py:940-943`) refuses a `read: yes` span holding no rows. A zero-row sheet therefore cannot carry a `yes` span at all: every span is forced to `read YYYY-MM-DD` or `exempt:`. No span vocabulary is added by anything here.

**The zero-row refusal is doing safety work that must survive.** `tools/threshold_sheet.py:857-859` parses a threshold row only when `len(cells) >= len(ROW_COLUMNS)`, so a row with fewer than eight cells is **silently skipped**. Change one column in `diabetes.md`'s `## Thresholds` header and all 357 rows vanish from the parse. The refusal at `:877-879` is the only thing that catches it, and lifting it naively turns a 377-page guideline with 357 measured thresholds into a sheet that audits as *states no decision point*.

**A zero-row sheet behaves in opposite directions across the two source modes, and the inverse of the intuition decision 4 was written on.** `unaccounted = known - {row.rec for row in rows} - set(sheet.scoped_out)` (`:2237`), so with no rows it is `known - scoped_out`. On an `exact` source that **refuses** unless every recommendation identifier is scoped out by name with a reason; on `bound` it only **warns**, tagged `(source mode is 'bound', so this over-reports)` (`:2308-2312`); with no record loaded it is `COVERAGE NOT RUN`. `none` is therefore harder to reach on `exact` than on `bound`.

**No live wrong claim exists.** `python tools/threshold_coverage.py` reports `topics 169 / sheet 1 / none 0 / unread 168`, and a `none` row's entire grading today is `threshold_coverage.py:91-94` — a non-empty `record` prose cell.

**[ADR 0031](0031-corpus-drift-is-reported-at-the-commit-and-the-cheap-limb-reads-the-audit-ledger.md)'s build has not landed.** `7f20bb1` moved `CONTEXT.md` and the record only, and `main()` still prints a bare `topics 169`.

## Ruling 1 — a `none` topic carries a threshold sheet whose `## Thresholds` holds no row

The evidence lives in the artifact, not in the registry's `record` cell and not nowhere.

This is not the empty sheet ADR 0009 refused. That refusal is stated on directory silence — *"directory silence would become indistinguishable from a clinical negative finding"* — and a sheet carrying a full span table, dated null markers per span and a declaration is the opposite of silence. It is the evidence ADR 0009 said an empty sheet could not carry.

**It is the only arrangement that makes `none` reach a run.** ADR 0017 keyed the consumer on the artifact column precisely so the state word could stay honest. An artifact-less `none` discards the read at the exact point it was supposed to pay: the note still says `recalled, no shipped sheet`, and `differential_scan` gains no topic. With an artifact the verdict moves one step up the ladder of three and the row-24 floor can disprove a wrong one.

### Rejected: structure the registry's `record` cell into a span table

ADR 0025 rejected per-section rows in `coverage.md` by name: that file's population is derived from the catalog's topic column and `threshold_coverage.py` refuses any row that is not a catalog topic. The cell also stays unreachable by a run, so it inherits ruling 1's whole objection.

### Rejected: no evidence anywhere, and the registry declares the gap permanently

It is the honest fallback and it forfeits the read. It also leaves `none`'s only backing a free-prose cell, which is the artifact class this registry has already produced a wrong claim at scale in — 46 rows asserting a blocker measurement shows does not exist.

## Ruling 2 — the state is derived across all three values, and there is no fourth state

Every page read **and** rows → `sheet`. Every page read **and no rows** → `none`. Any span `read: no` → `unread`. [#478](https://github.com/mshamblin5150-code/clinical-skills/issues/478)'s both-directions refusal then covers `none` for free, and `CONTEXT.md`'s sentence about `sheet` — *"derived from the sheet's own span table rather than typed"* — becomes true of the whole partition.

`none` survives as a distinct word and is now bookkeeping, exactly as ADR 0025 point 1 says of `sheet`. **ADR 0027 ruling 6's merge-and-disclose arrangement does not transfer**, and the reason is not ADR 0009's. Those merges were forced because the merged situations were indistinguishable and separating four rows would have split them from 39 identical in kind. Here ruling 1 *manufactures* the distinction: after it, a `none` topic and an `unread` topic differ by a committed artifact a command re-derives in both directions. A sentinel that was indistinguishable becomes distinguishable, which is the condition 0027 did not have.

ADR 0017 rejected a third state (`partial`) and nothing here adds one.

## Ruling 3 — a null sheet declares itself, and the declaration is what lifts the zero-row refusal

No rows and no declaration stays refused, with today's message. No rows **and** a declaration parses:

```markdown
## Thresholds

**No decision point.** Every span in `## Scope` was read and this source states no
quantity that changes what is done to a patient.
```

This preserves the dropped-column catch exactly: the mangled `diabetes.md` above still refuses, because nobody wrote the declaration. It is `CLAUDE.md`'s standing extractor-coverage rule — *a deliberately partial report may keep its ordinary status only when its contract names the bound beside the result; silence never means full coverage* — arriving at a zero-row report.

The form invents nothing. `RENDERED:`, `exempt: <reason>` and the accepted-distrust block are three held declarations already in this format, and [ADR 0019](0019-accepted-distrust-is-declared-in-the-artifact-it-reached.md) rules that such a thing is declared in the artifact it reached. ADR 0017 puts a run in this artifact, which is why the declaration belongs here and not in `coverage.md`.

**The declaration carries no figures.** Not a span count, not a page count. The arithmetic stays in the span table where the auditor re-derives it against the catalog's `page_count`. A number in the prose is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) with a schedule, and ADR 0031 ruling 5's *nothing in the line is a literal*.

### Rejected: derive the null claim from the span table alone

Every span `read`/`exempt:` plus complete page coverage is cheaper and admits the mangled sheet: nothing distinguishes *no rows* from *no rows parsed*. It also makes the ticket's second *Done when* unwritable, because under it absence is the signal and no failing case can be constructed.

## Ruling 4 — a run writes `sheet does not settle it`, and no fourth silence is minted

The ticket's own *What must not come out of this* is the argument:

> a topic in `none` tells a clinician the guideline is silent, which is the one thing `sheet does not settle it` was built to never say by accident.

A fourth verdict whose whole content is *the guideline is silent* mints that sentence as vocabulary and writes it into notes. The existing verdict says nothing about the guideline, which is what it is for, and the warning becomes a rule the wording obeys rather than a caution somebody has to remember.

ADR 0017 already rejected this shape with reasoning that transfers: *"The tail would qualify a verdict that already concedes everything, and the sheet's `## Scope` states the same gap per topic and more precisely. One jump, and the jump is what the citation exists to enable."* A null sheet's `## Scope` reads `**Not read:** nothing in the source page range`, so the jump delivers a stronger completeness claim than a partial sheet's does.

**`no USPSTF row` is the tempting analogy and it does not carry.** That verdict may mean it because USPSTF is complete for what it covers, 143 rows from 90 of 90 documents. A null sheet gives *one topic* that property while the skill's rule is written per family, so a verdict true for the `none` topics and false for every other threshold topic puts a reader one row from a wording that means the opposite next door.

**The prose cost is named.** `skills/clinical-note/SKILL.md:650`'s three-meanings list is written for a partial sheet; its meaning 3, *"the section it would be in was never read"*, is false of a null sheet. That list gains a sentence saying a sheet whose `## Scope` reports nothing unread has eliminated meaning 3, so the jump pays. ADR 0017 already binds that prose with a test.

## Ruling 5 — the registry refuses a `none` row with no artifact, and qualifies the row on every run

`none N   artifacts M` with `M < N` becomes a refusal, parallel to the existing `state 'sheet' has no artifact` at `threshold_coverage.py:95-98`.

The `none` row carries a qualifier whether or not it fires, on [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s rule:

```
none       2   artifacts   2   -- every span retired on a marker or a class exemption; no row carries a gated citation
```

**The qualifier states the kind of evidence, not its absence, and that distinction is the ruling.** *No second read was re-run* is true of every sheet in the directory, is ADR 0025 point 7's ruling, and is already reported per-sheet by `threshold_sheet.py` — putting it here is the second mechanism for one trigger that ADR 0028 ruling 6 refused, quoting `docx_write`: *a second mechanism that cannot fail is not a belt and braces; it is a line that costs a test.* What is true only of `none` is that **no span can be `yes`**, so every span rests on a marker or a class exemption and not one row anywhere carries a citation gate. That is a categorical difference a reader seeing `sheet 1 / none 2` cannot otherwise infer, and it is derivable from the artifact.

The ticket's first *Done when* is met on its **first** limb for most of the claim: a command re-derives that the artifact exists, parses, carries the declaration, covers every catalog page, lists no unread span and holds no row. The qualifier is the residue clause for what remains.

### Rejected: print the qualifier only when `none > 0`

A reader who learns to read a qualifier reads its absence as the stronger claim, and `none 0` today is silence standing for *nothing was checked about `none`* — ADR 0031 ruling 4's shape.

### Rejected: print nothing, and let the sheet's declaration be the whole disclosure

`threshold_sheet.py`'s report is per-sheet and reaches whoever grades one artifact. `threshold_coverage.py`'s report is the sweep's own output, and ADR 0009 calls that *the sweep records its denominator*. Publishing the count in one place and its evidence class in another is how `phi_scan`'s scope statement ended up attached to the wrong layer.

## Ruling 6 — `none` is reachable on a `bound` source, and the sheet declares what it does not claim

ADR 0025 point 5 replaced the recommendation index with page coverage as the instrument — *"a read is now a named span with a page range, checked against the catalog's `page_count`, and it opens no recommendation record at all"* — and `diabetes.md` shipped `sheet` on bound ADA over 377 pages on that ruling. Refusing `none` on `bound` would say page coverage suffices for finding numbers and not for failing to find them, when a page read is one act and ADR 0025 point 2 already prices the difference between its two outcomes.

**`none` is not cheaper than `sheet`, by arithmetic rather than by a new rule.** Every span in a null sheet is a null retirement, so ADR 0025 point 2's blind independent second read applies to **all** of them. `diabetes.md` owed one on two spans; a `none` topic owes one on every span it has.

On a `bound` source the sheet carries the non-claim `diabetes.md` already writes beside its declaration:

> The recommendation record remains `bound`, so its identifier accounting warns rather than refuses and does not claim that the extraction is a complete recommendation index.

On an `exact` source nothing is added: the scope-out-everything requirement fires by construction, each entry carrying its own reason, which is `hypertension.md`'s 50 reasons — 28 reading exactly `no number` — at full width.

### Rejected: make the COVERAGE warning a refusal for `none` on `bound`

It makes one gate mean different things in two states of a registry no gate reads, and re-opens ADR 0025 point 5 for a claim page coverage already carries.

## Ruling 7 — the mechanism ships with constructed failures; the first reading is its own ticket

Two failing cases, both one edit, and both required: delete `**No decision point.**` from a null sheet, and break a column in a populated sheet so its rows silently stop parsing. That is the ticket's second *Done when* — exercised against a topic constructed to fail it rather than a green run over an empty set.

ADR 0025 point 6 already rules *"the mechanism and the readings are separate tickets"*, and ADR 0017 rejected the same fold in as many words: *"mixing a clinical reading into a ticket whose subject is a mechanism, where the reading is the half no command can review."* Under ruling 1 the reading half grew — a `none` promotion owes a blind second read on every span, refusing on disagreement — so folding it in is #434's warning that two evidence bars in one commit is how the weaker one rides in on the stronger one's credibility.

`latent tuberculosis infection screening` (USPSTF 2023, `page_count 8`) is the first reading ticket, blocked on this mechanism, in ADR 0009's order.

**The ticket's worry is answered by the fixtures rather than by a real row.** What it fears is a precedent written by whoever holds the pen. Once the declaration is required, the span table is checked against `page_count`, the state is derived in both directions and the failing cases are committed tests, the precedent is in the code and the first reader has nothing left to invent.

## The venue collision the build must not repeat

[#439](https://github.com/mshamblin5150-code/clinical-skills/issues/439)'s build lands ADR 0031 ruling 3's denominator-basis line in the same `print` block ruling 5 edits. Two branches editing one block is this repo's recorded failure — `anchor_scan` against #150, and the byte-identical `**24**` git merged in silence. Whichever ships second rebases onto the first and re-derives the whole block rather than patching a line.

## Declared limits

**A null sheet's claim is declared and page-checkable, not re-derivable.** The declaration asserts a reading and a lazy reader writes it as easily as a careful one — the floor ADR 0025 point 7 states for the dated marker, *"records that a read happened, never that it was careful"*, and the one `specificity_scan`'s reason test lives with. What backs it is the per-span second read, which is out-of-repo evidence the hook never runs.

**The read reaches the run and not the note body.** Under ruling 4 a `none` topic's item is worded exactly as a partial sheet's is, and the strength is one jump away in `## Scope`. No citation reaches the body, which is the skill's rule and not a concession here.

**This does not close [#505](https://github.com/mshamblin5150-code/clinical-skills/issues/505).** *The USPSTF looked and found no evidence for an interval* still reaches a note as `sheet does not settle it`, the same words as an unstated absence. What ruling 6 does is make a home exist: an `exact`-source null sheet must scope out every identifier with a reason, which is the per-recommendation account of *why* each holds nothing that #505 is looking for. Whether that is #505's answer is #505's to rule, and whether a bound source with no record has identifiers to scope out is a measurement nobody has taken.

**Nothing here reaches a sheet whose spans are drawn on the wrong pages.** ADR 0025 already declares it — *"page coverage catches an omitted span, not a misdrawn one"* — and a null sheet inherits it at full width, because every one of its pages is claimed by a span nothing else checks.

**ADR 0029 is not on `main`.** It exists at `8cb3bc1` on `origin/pr/508`, and `git merge-base --is-ancestor 8cb3bc1 origin/main` is false, so there is no record to link to in this tree. Sweep comments on #483 cite it as ruled; no ruling here depends on it, and the rejection of the `record`-cell option rests on ADR 0025 alone.
