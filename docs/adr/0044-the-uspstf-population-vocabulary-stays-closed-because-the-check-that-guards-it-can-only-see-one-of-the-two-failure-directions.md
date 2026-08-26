# The uspstf population vocabulary stays closed because the check that guards it can only see one of the two failure directions

[#502](https://github.com/mshamblin5150-code/clinical-skills/issues/502) was filed because
`reference/guidelines-uspstf.md:147` carries `not stated` in `Population` for the `rhrs.pdf`
grade-B row, whose statement plainly names one: *all unsensitized Rh (D)-negative women at
24-28 weeks' gestation*. It is the only such cell in 143 rows. The cause is isolated —
`_POP_QUALIFIER` at `tools/uspstf_table.py:407` is a closed list of adjectives permitted before
the person noun, `unsensitized` is on it and `Rh (D)-negative` is not, so the phrase fails to
match and the whole cell is lost.

**The vocabulary was extended for this very statement and still cannot read it.** That is the
ticket's sharpest observation and it is the argument this record has to answer, because the
cheap fix is the same edit that already half-worked once.

Grilled 2026-08-26. **Six decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## The ground the ticket was ruled on had already collapsed, and the replacement inverts it

The body's original ground for declining a fix was that the obvious widening *"fixes this row
and moves 26 others"*, 15 losing a correct population and 11 acquiring a different
recommendation's. **That figure is falsified by five independent re-derivations** — 2026-08-25
at `ae49d53` and `7c0a59f`, 2026-08-26 at `0c39452`, `863240c` and `6f82cca`, the last taken
during this grilling. All five reach one cell moved, zero regressed. The ticket body withdrew
the figure on 2026-08-26; the withdrawal is summarized there and is not re-published here.

**Why the two measurements disagree is structural rather than a slip, and it is the same fact
this record rules on in ruling 4.** `derive_population(statement, fallback)` is called at
`tools/uspstf_table.py:704` with `fallback = document_population(pages)` — the document's own
`POPULATION` abstract field, read from the corpus and **not carried in the artifact**. So a
re-derivation over the artifact's own `## Statements` table and a re-derivation through the
pipeline measure different quantities, and the first reads exactly like the second. The ticket's
*Done when* promised the first; three sweeps quoted that promise and none tested it.

## The grilling's own measurement, and it removes the last number that separated the options

Both candidate fixes were driven over all 90 USPSTF documents, keyed per
`(filename, row index)` rather than per topic — a topic-keyed dict collapses multi-row files
and can hide a move. The alternative must be added **in the source**; a runtime patch is inert,
because the constant is interpolated into `POPULATION_PHRASE` at import.

| | rows | cells that move | lost | gained | changed |
| --- | ---: | ---: | ---: | ---: | ---: |
| committed rule | 143 | — | — | — | — |
| literal `Rh \(D\)-negative` added | 143 | 1 | 0 | 1 | 0 |
| regex `[A-Za-z]+(?:\s*\([A-Z]\))?-[a-z]+` added | 143 | 1 | 0 | 1 | 0 |

**The two fixes are byte-identical in effect.** The one cell that moves is this ticket's own row
and it moves to the correct population. None of the files the withdrawn list named — `cervical`,
`hiv`, `tobacco`, `folic`, `carotid`, `afib`, `sleep-apnea` — moves under either.

The figures are measured against a corpus outside this repo, so nothing committed re-derives
them. The method is stated so the next reader repeats it rather than quotes it.

## So the decision could not be made on cost, and was made on failure direction

The widened qualifier is genuinely two-sided, which is why it is tempting and why it is refused:

```
'The USPSTF recommends counseling for tobacco-dependent adults.'
    committed 'not stated'   literal 'not stated'   regex 'tobacco-dependent adults'
'The USPSTF concludes the evidence is insufficient in low-quality patients.'
    committed 'not stated'   literal 'not stated'   regex 'low-quality patients'
```

The first is a real population the closed list misses and the widening reads correctly. The
second is a methodological adjective fabricated into a population. **Both are filled cells**, so
no presence check can tell them apart, and a filled cell is what
`skills/clinical-note/SKILL.md`'s `[uspstf: grade A, adults 50 to 75, 2021]` citation form puts
in front of a preceptor — read off the artifact by whoever writes the note, and required by that
skill to carry **every condition in the cell** through into the tail.

*(Corrected 2026-08-26: this sentence also named `guidelines_recs.CuratedRow.population` as a
consumer. `CuratedRow` **carries** the field and `curated_records` never passes it into a
`Recommendation`, so nothing in the record path consumes it. The severity argument stands on the
citation form, which is a real consumer; the second mechanism was not one.)*

The closed list fails only ever toward a **blank**, and a blank is exactly what ruling 3's pin
catches. The widened rule fails toward a **wrong value**, and nothing anywhere catches that.
**The failure directions are not symmetric and the only check available is sensitive to one of
them.**

## Rulings

**1. The literal, chosen over the regex on failure direction rather than on cost.**
`Rh \(D\)-negative` is added to `_POP_QUALIFIER`. The measurement above **supports the regex**
— it costs nothing today — and the regex is declined anyway. That is the unusual shape of this
record and the reason it exists: a declined option whose supporting measurement is correct is
the most dangerous kind, because every number in the room agrees with it.

**2. `_POP_QUALIFIER` stays a closed vocabulary, and every extension is a literal added on
evidence.** This is the same growth rule that put `unsensitized` there, and the ticket is right
that the edit is the same. It is not the same **move**: `unsensitized` landed with nothing
asserting the row it was added for actually derived, which is why it could half-work for the
life of the artifact. Ruling 3 is what makes the identical edit safe.

**3. The reopening signal is a presence-only count pin on the committed artifact.** A test
derives the `not stated` count in `Population` from `reference/guidelines-uspstf.md` and asserts
it is 0, with the failure message naming the instrument and this record. It lives in
`tools/test_uspstf_derived_cells.py` beside the interval check, is artifact-joined, and needs no
corpus, PDF or network.

**It reaches presence and never correctness, and that limit is [#432](https://github.com/mshamblin5150-code/clinical-skills/issues/432)'s
and is unchanged.** A population cell can be quoted from a document field the artifact does not
carry, so whether a cell is *right* is not re-derivable from the artifact. What is re-derivable
is whether the column is full, and that is precisely the property this ticket's defect broke.

**That file's docstring currently declares `population` out of scope by name**, and the
declaration is narrowed rather than left standing — from *the column* to *the column's content*.
A population check sitting in a file whose docstring says the column is out of scope is the
two-copies-disagreeing failure [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)
and [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) record, and the
reader misled is whichever one they read first.

**4. The artifact header's fused clause is split, because it is false for one of the two columns
it covers.** The header reads:

> `population` and `interval` are *derived from the statement text*, not quoted from a field the
> document declares — from the statement sentence alone

That is true of `interval` and false of `population`. Measured over the 90 documents,
**15 of 143 rows across 13 files are supplied by `document_population`** — the document's
declared `POPULATION` abstract field — with 127 from the statement and 1 from neither. The
header asserts the column is not what 15 of its rows are. `interval` keeps the clause;
`population` gains its own naming the fallback.

**The figure belongs to this record**, on [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s
terms, and it moves on the next refresh. **No figure goes in the header.**

**Corrected 2026-08-26 by the exhaustive sweep on this record.** This paragraph read *"it is
counted against a corpus outside the repo, nothing committed re-derives it"*, and the second
half is false. The **values** need the corpus; the **identity of the 15 rows** does not. Driving
`derive_population(statement, "")` over the artifact's own `## Statements` table and diffing
against the `Population` cells returns exactly those 15 rows across 13 files, with **zero other
disagreements over 143** — from `reference/guidelines-uspstf.md` and `tools/uspstf_table.py` and
nothing else. The condition is exact by construction: `derive_population` returns the fallback
precisely when the statement rule finds no phrase. **Three sweep agents re-derived it
independently and the parent re-derived it a fourth time.**

**And the denominator is matcher-dependent, which is worth stating beside it rather than leaving
for the next reader to trip on.** *Which route filled the cell* gives **15 rows across 13
files**. *Which cells a reader cannot attribute* — the cell string equal to the declared field —
gives **17 across 15**, the two extra being rows where the statement rule independently produced
the field's own wording. This ruling is about provenance, so 15 is the figure; the other is named
because two honest measurements of "the same" quantity differing by matcher is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137), and a reader who
derived 17 would otherwise conclude one of us was wrong.

**The clause has four copies and ruling 4 names one.** Besides the generated header, it is in
this module's own docstring at `tools/uspstf_table.py:30`, and in
`skills/clinical-note/SKILL.md:678` — a **consumer-facing skill** that restates it *and cites
the header as its authority* — which `tools/test_guideline_sheets.py:219` pins. All four move
together or the repair reinstates the defect one file over, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) inside the ruling whose
subject is a false clause.

**Ruling 1 also falsifies a live sentence in that skill, and no test catches it.**
`skills/clinical-note/SKILL.md:678` reads *"one row of the 143 has a population reading `not
stated`"* and teaches the citation tail from it. After the fix, **zero rows do**, and the
instruction loses its only live instance. `tools/test_guideline_sheets.py:220` asserts the string
`population not stated` is present, so it stays **green** while the claim around it becomes
false. That is this record's own subject — a check sensitive to the wrong thing — arriving on
the ruling rather than on the column.

**5. The declined widening is pinned by a test, as a floor and never a rate.** Both forms are
implemented and run rather than described, on
`test_research_ledger.TheDeclinedParserRowsFireOnCorrectOrders`'s arrangement, so re-proposing
the regex costs a failing test rather than an argument. Both directions: the widened qualifier
fills a cell from a sentence naming no population, and the chosen literal does not while still
reading the `rhrs.pdf` statement.

**The claim the test makes is narrower than the precedent's and must say so.** There the
declined rule fired on real correct orders — a measured cost. **Here the declined rule fires on
nothing in the corpus**: five measurements put its cost at zero. The sentences are constructed,
the pin is a floor on shapes, and the corpus cost is stated in the test as zero. A pin that let
a reader infer the widening had been measured as harmful would rebuild the withdrawn 26 inside
the fix for the withdrawn 26.

**6. The price is named rather than discovered**, on [ADR 0028](0028-the-uspstf-interval-derivation-reaches-one-sentence-and-that-reach-is-ruled-permanent.md)
ruling 5's terms: the next corpus refresh turns the suite red for a population change nobody
caused, and whoever refreshes pays for re-running the instrument and re-reading this record.
That is the cost of ruling 3 and it is what ruling 3 buys.

## Consequences

**This ticket blocks on [#434](https://github.com/mshamblin5150-code/clinical-skills/issues/434)
and rides its rebuild.** [ADR 0030](0030-a-recommendation-record-is-owned-like-every-other-artifact-its-trust-floor-is-keyed-on-the-limb-that-built-it-and-the-drafter-takes-no-escape-hatch.md)
ruling **2** keys a record's floor on `counted_from` and puts
`reference/guidelines-uspstf.md` in the `inputs` of every `curated-table` record. Three of the
five bound records are `curated-table`, so rebuilding the artifact invalidates their stamps and
`threshold_sheet --all` exits `2` until they are re-produced. #434's deliverable 5 rebuilds the
same file for its own reasons, so landing after it pays that bill once rather than twice.

**Corrected 2026-08-26 by the sweep, twice over, and the second correction is the one that
matters.** This paragraph cited **ruling 1**, which is the general principle — *a trust floor is
made of inputs, not of code* — where ruling 2 is what actually keys the floor. That imprecision
was copied from ADR 0030's own Consequences, which says *ruling 1* twice; it is now wrong in two
records rather than one, and is corrected here only.

**More seriously, the consequence was written in the present tense and is not live.**
`grep -c "artifact_provenance\|allow_untrusted" tools/guidelines_recs.py` returns **0** — nothing
stamps or validates a `recs-<key>.json` today, so no rebuild can refuse anything on this ground
until [#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438) builds ADR 0030.
The bill is real and it is **scheduled, not standing**. *(The absence of a `recs` key from
`artifact_provenance.TRUST_FLOOR` is **not** evidence of this — ruling 2 says in as many words
that the key lives in `guidelines_recs.py` beside the `SOURCE_*` constants and not in that
table. A sweep agent offered it as evidence, which would have been a wrong reason for a right
conclusion.)*

**And when it does land it is stamp-only.** `curated_records` builds each `Recommendation` from
`row.page`, `row.topic`, `row.grade` and `row.statement`; `population` and `interval` never leave
`CuratedRow`. So a Population-only rebuild moves no record's **content** — a re-produced record
is byte-identical apart from its stamp and its `inputs` hash. **#434 is `ready-for-agent` and can land without anyone reading this
record**, which is why the dependency is recorded on that ticket as well as here.

**The scope is this column on this artifact, deliberately.** The general argument — where two
fixes measure identically, prefer the one whose failure direction the available check can see —
is stated in full above so that whoever meets the same shape can cite it. It is **not** promoted
to a standing rule. One column, one artifact, one check is a single instance, and generalizing
from the files one pass happened to have open is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s recorded shape.

**What this does not rule, and it is filed rather than left implied.** Ruling 4 discloses the
fallback in the header; it does not **mark** which rows came from it. Whether a fallback-sourced
cell should carry a mark in the row is a change to the table's shape and to
`guidelines_recs.parse_curated_table`, and it has its own ticket —
[#545](https://github.com/mshamblin5150-code/clinical-skills/issues/545).

**Corrected 2026-08-26, and this is the sharpest thing the sweep found.** This paragraph read
*"A reader of the table still cannot tell a statement-derived cell from a document-derived one,
so the corpus-free re-derivation the ticket promised remains impossible for 15 rows."* **The
first half is false**, by the measurement recorded under ruling 5 above: the 15 rows are
identified exactly, corpus-free, from two committed files. It is a **fused clause with one true
half and one false half** — you cannot recompute the *value* from the statement, and you can
identify *which rows* — which is the identical defect ruling 4 exists to split, committed one
section later in the record that splits it. Found by three sweep agents independently.

**So what a mark buys is legibility, not possibility**, and #545 was filed on the stronger claim
and has been corrected to the weaker one. The residual argument is that a derivation is not a
record: identifying the rows re-runs *current* code against an artifact built by a possibly
different version, so it drifts silently where a mark would not.

**Nothing here reaches whether a population cell is correct.** The pin sees presence; the header
sees provenance; neither reads a document. A green suite is not a checked population.
