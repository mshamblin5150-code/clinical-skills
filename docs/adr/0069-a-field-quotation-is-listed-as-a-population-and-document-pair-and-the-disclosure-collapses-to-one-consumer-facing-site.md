# A field quotation is listed as a population-and-document pair and the disclosure collapses to one consumer-facing site

`reference/guidelines-uspstf.md` derives its `Population` column two ways.
`uspstf_table.derive_population(statement, fallback)` at `:716` quotes the recommendation
sentence where its rule finds a person-phrase, and otherwise takes `fallback =
document_population(pages)` at `:712`, which is the document's own `POPULATION` abstract
field. **15 of 143 rows are that second route and no row says which it is.**
[#545](https://github.com/mshamblin5150-code/clinical-skills/issues/545) is that residue.

Grilled 2026-08-29 and 2026-08-30 against `origin/main` at `3ef2e74`. The clinician ruled
all ten points below. **Nothing is built here; this is the record the build reads.**

## What moved under the ticket before it was grilled

Five comments on that thread are falsified at HEAD, and the ticket's own premise sentence
has flipped back to true. [#502](https://github.com/mshamblin5150-code/clinical-skills/issues/502)
closed with rulings 3 and 5 built, so `reference/guidelines-uspstf.md:5` now reads
*"`population` is quoted from the statement when possible and otherwise from the document's
declared `POPULATION` field"*, and `not stated` in that column is **0**, not the 1 that four
sweeps published.

[ADR 0068](0068-a-stated-evidence-absence-is-read-into-the-uspstf-artifact-and-the-class-is-named-for-what-the-source-says.md)
landed on the same file the week before and pre-prices two of this ticket's four decisions.
Its ruling 2 refuses a further column **on a measurement rather than on taste** —
`guidelines_recs._markdown_rows(markdown, "Recommendations", 9)` at `:1066` drops every row of
a differing width and `parse_curated_table` then raises `DidNotScan`, which under
[ADR 0045](0045-the-recommendation-sweep-is-a-third-cache-stage-its-records-are-keyed-on-doc-id-and-a-document-that-yields-nothing-declares-itself.md)
ruling 3 refuses the whole 179-document recs build. It refuses a cell sentinel too, and rules
the venue for the sibling problem to be a generated `##` section.

## The measurement, corpus-free and re-derived at `3ef2e74`

Joining `## Recommendations` to `## Statements` on `(File, Page, Grade)`, **keeping the
multiset**, and passing a row when any candidate statement derives its cell through
`derive_population(statement, "")`:

```
recs 143   stmts 143
distinct (File, Page, Grade) keys   126
keys carrying more than one statement 16
rows hidden by a collapse             17
field-quoted    15 rows, 13 files, 13 (Population, File, Page) pairs
not stated in Population               0
recommendation rows with no matching statement key   0
the same join with a dict collapse    26 rows across 21 files
```

The condition is exact by construction: `derive_population` returns the fallback precisely
when the statement rule finds no phrase. The 26 is the withdrawn regression figure this
ticket was filed downstream of, and it is a defect of the **container** rather than a
property of the artifact.

## Findings this grilling produced

**These are numbered `Finding N` and the rulings below are numbered `N`, deliberately.** A first draft numbered both `**N.**`, which made *"ADR 0069 ruling 3"* resolve to two different real items under a bold-shape extractor — [#554](https://github.com/mshamblin5150-code/clinical-skills/issues/554)'s over-count direction, in a record written after that ticket's own correction declared it uninstantiated. Found by the sweep this session ran.

**Finding 1. A document-level list over-claims, and that is the frame the ticket used.** Keying on
`File` alone puts a statement-quoted row inside the mark in **two** of the thirteen:
`dental-caries-young children-final-rec-statement.pdf` and
`ipv-screening-final-rec-statement.pdf` each carry a correctly quoted row beside a
field-quoted one. *"15 across 13 files"* appears in the ticket body and in seven sweeps and
reads as a claim about documents, which is false.

```
key                        distinct over the 15   buckets mixing the two routes
(File)                              13                 2
(File, Page, Grade)                 14                 1
(Topic, Grade, File)                14                 1
(Population, File, Page)            13                 0
whole row (all 9 cells)             14                 0
```

**Finding 2. Two of the 15 are byte-identical across all nine columns.** The `multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation.pdf`
grade-I pair differs only in its `## Statements` entries, beta carotene and vitamin E against
single or paired nutrients. Nothing in `## Recommendations` separates them.

**Finding 3. The population rule is stated in six places and no count on #545's thread reached
the last two.** The artifact header at `:5`, the `## Statements` preamble at `:175`, the module
docstring at `uspstf_table.py:29`, **`derive_population`'s own docstring at `:476-478`**,
`test_uspstf_derived_cells.py:11-12`, and **`skills/clinical-note/SKILL.md:678`**, which states
it verbatim — *"quoted from the statement when possible and otherwise from the document's
declared `POPULATION` field — the sheet says so at its top"* — and is pinned by
`tools/test_guideline_sheets.py:215-222`.

**The sixth was found by the sweep, after a first draft of this record had already published
five and concluded on that number.** It is the most consequential of the six and the one a
count keyed on the producer could never reach, because it is in **a different artifact with a
different audience**: `skills/` is what a consumer opens, and `reference/` is not.

**ADR 0068 ruling 8's *"three sites to police"* is not undercounting this, and a first draft
of this record said it was.** That count is about the **interval**-derivation claim — its
paragraph opens *"There is a third generated copy of the interval-derivation claim"* — and for
interval the sites are `:5`, `:175` and `uspstf_table.py:29-30`, which is exactly three.
`derive_interval` at `:534` carries a docstring, but it states which phrases the vocabulary
collects rather than the boundary, so it is correctly not counted. `derive_population`'s does
state the boundary, which is why the two columns have different totals over the same files.
**The error was generalizing one column's count onto the other from the files this session had
open**, which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s
subject arriving inside a record whose own subject is a claim copied to five places. It was
caught by re-deriving a finding this session had itself produced, before it reached a sweep
verdict.

**Finding 4. `Topic` has the same shape and is worse.** `derive_topic` at `:574` takes three routes —
page 1's title, the PDF metadata title (*"missing or reads `JAMA` in twelve of the ninety
documents"*), then the filename slug — and marks none. Unlike `Population` it is **not
recoverable corpus-free**: the artifact ships the statement, so a field quotation differences
out, but it ships neither page 1 nor the metadata title. The impossibility claim #545's body
made about `Population` and its own first comment withdrew is true about `Topic`. Filed
separately rather than folded in.

## The ruling

**1. A field-quoted cell is marked.** The ticket's filed motivation was impossibility and its
own first comment correctly withdrew it — the rows difference out exactly, corpus-free. What
survives is the deciding argument: **a derivation is not a record.** Differencing runs
*current* `derive_population` against an artifact built by a *possibly different* version of
it, and nothing announces when the two stop agreeing. A generated section is stamped at build
time and cannot drift from the table it ships in.

**2. The venue is a generated `##` section**, ADR 0068 ruling 2 adopted whole rather than
re-argued: a further column is refused on that ruling's measurement, and a sentinel in the
cell was already declined twice — ADR 0027 ruling 6 and
[ADR 0052](0052-a-codification-year-is-provenance-and-the-snapshot-behind-it-is-declared-unreached.md)
ruling 5. **The sharp reason is #545's own consequence 2 rather than the precedent.**
`guidelines_recs.CuratedRow.population` hands the cell to
`skills/clinical-note/SKILL.md:666`'s `[uspstf: grade A, adults 50 to 75, 2021]` form, which
copies it **verbatim in front of a preceptor**. A section puts no character into that string.

**ADR 0052 ruling 5's sentinel-dominance cost does not transfer and is not relied on.** That
argument runs at 21 of 22; this column is 128 of 143 statement-quoted, so a mark is the
minority and the ratio argument is silent here.

**3. One entry is a population-and-document pair, not a row.** Thirteen entries keyed on
`(Population, File, Page)`. Every readable row key collapses the `dental-caries` pair and
marks a statement-quoted row, and every key that separates them carries `Population` anyway —
which is the value the section is about and is already public in the cell. Each entry is a
true universal: *every row in this file bearing this population is field-quoted.* The
`multivitamin` pair stops being a defect and becomes a fact the pair-level claim absorbs.

**The heading follows the term and not the row count.** `## Population cells quoted from the
declared field`. A heading saying *rows* above thirteen entries against a stated fifteen is
the mismatch a reader trips on first.

**4. Both counts are rendered from `len()` and never typed**, and the preamble states both.
`CONTEXT.md`'s **Underived count**, and ADR 0068 ruling 8's rule for its own section's counts.
Fifteen rows and thirteen pairs are two honest figures for one population, and stating one
alone is [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s shape.

**5. The disclosure collapses, one disposition per site.** ADR 0068 ruling 8's *"the header
carries one pointing clause and the section preamble owns the boundary. Not both"*, applied
to five sites rather than three. Adding a sixth copy in the same file the week that was ruled
is the outcome this ruling exists to avoid.

- **Artifact header `:5`**, generated at `uspstf_table.py:835` — reduced to a pointing clause.
  ADR 0027 ruling 6's *"the header is the only place a consumer meets this column"* was true
  until the section exists, exactly as ruling 8 found for `interval`.
- **`## Statements` preamble `:175`**, generated at `:933` — becomes a pointer, **not a
  deletion.** Its population clause does real local work: it warns that for some rows the
  shipped statement cannot check the cell, which is the whole reason statements ship, and a
  section naming the rows sharpens that warning. Its interval half is untouched; ruling 8
  already declared that sentence true.
- **Module docstring `:29`** — pointing clause to `derive_population`, not to the artifact. A
  docstring points at the function that decides.
- **`derive_population:476-478`** — **untouched, and named as the owner.** It is the only site
  where the rule and the code applying it cannot drift apart, and collapsing it would delete
  the authoritative statement to preserve a rule about derivative ones.
- **`test_uspstf_derived_cells.py:11-12`** — justification corrected, conclusion kept verbatim.
  *"This check establishes presence, not correctness"* stays true; *"a document field that the
  committed table does not carry"* stops being the reason once the table names the cells.

**A sixth site exists in a second artifact, and a first draft of this ruling concluded on
five without it.** `skills/clinical-note/SKILL.md:678` states the rule verbatim — *"quoted from
the statement when possible and otherwise from the document's declared `POPULATION` field — the
sheet says so at its top"* — pinned by `tools/test_guideline_sheets.py:215-222`. **It stays, and
it is a second consumer-facing statement by design**: its audience is a run writing a note
rather than a reader of the table, and its work is the clinical caution that follows it, that a
row whose population decides care is a row to check against its page. `skills/` is what a
consumer opens and `reference/` is not, so collapsing it would move a caution out of the file
where it fires.

**But it takes a build item, because ruling 5 changes what it describes.** That sentence asserts
*the sheet says so at its top*, and this ruling reduces the top to a pointing clause. The
pointing clause must keep saying so, and the build re-reads `SKILL.md:678` against the emitted
paragraph. **Nothing mechanical couples them** — `test_guideline_sheets.py` asserts the substring
against `SKILL.md`, never against `reference/guidelines-uspstf.md`, so the two can disagree with
the suite green. That gap is declared here rather than closed, and it is the reason the site was
invisible to every count on #545's thread: those counts were keyed on the producer, and this one
lives in a different artifact with a different audience.

That leaves **two consumer-facing boundary statements with different audiences**, one
mechanism-facing owner, and three pointers. **It also answers what made the ticket's *not
marked* branch illusory**: the disclosure was never missing, it was duplicated six ways, and a
build adding a seventh without consolidating makes the original defect worse.

**6. The section is graded, in two tiers**, on `threshold_sheet.py`'s citation arrangement and
for its reason — *there is no machine on which checking drops to zero* — which ADR 0068 ruling
7 already adopted in this module.

**Tier 1, corpus-free, in CI.** The join above, multiset kept, asserting the field-quoted rows
are exactly the thirteen pairs the section names; every named triple matches at least one row;
every named file appears in `## Recommendations`; and the rendered counts equal `len()` of what
was rendered.

**Tier 2, where the corpus is.** The cell equals `document_population(pages)` for that document
verbatim. This is the only limb grading the **claim** rather than the bookkeeping — tier 1 can
establish that the statement did not produce the cell, never that the declared field did. Skips
with a banner surviving `--quiet`.

**7. ADR 0068 ruling 3's *read, never matched* does not transfer, and a liveness limb replaces
what it bought.** That ruling holds a hand-read tuple because membership cannot be matched, and
its vocabulary limb *"can only refuse a row a human wrote, never propose one."* Here
`derive_population` knows the route at build time, so there is no list to refuse and the section
is rendered. What that costs is independence: tier 1 shares `derive_population` with the
producer, so it grades the **committed section against the committed table** and not the
derivation. **Fed a `dict`-collapsed lookup it must go red at 26 across 21 files.** That mutant
is the recorded origin of the withdrawn figure, it is free, and a check passing under it is
measuring nothing.

**#545's *What must not come out of this* is narrowed rather than honored whole.** Its
prohibition on comparing the cell to the statement stands as a **substitute for the column** and
is lifted as a **provenance discriminator**, which is that ticket's own first comment and is
exact at zero error over 143.

**8. `not stated` is excluded explicitly, with the reason written beside it.**
`derive_population(stmt, "")` returns `""` both where the statement rule found nothing and where
neither route was available, so the naive predicate would list a `not stated` cell as quoting a
field it never read. **It is a no-op today at zero such rows** — #502 ruling 3 filled
`rhrs.pdf` — which is exactly why it must be written now: the distinction is currently
untestable against the artifact and the next corpus refresh reintroducing one would publish a
false claim in a public-domain artifact.

**9. The class is named `Field quotation` in `CONTEXT.md`.** Nothing in the glossary reaches it;
`Given`, `Derived` and `Filled` are note tiers. **`Second source` is disqualified on the existing
vocabulary** rather than on taste: in this repo a **source** is a corpus document
(`Source class`, `Declared non-source`), and the `POPULATION` abstract field is a second passage
of the *same* document. `Fallback` is the code's word, and this glossary's `_Avoid_` lines
reject implementation vocabulary consistently — `Derived` avoids *calculated*, `Declared` avoids
*hardcoded*. The term is written general to the artifact so the `Topic` ticket inherits
vocabulary instead of coining a rival.

**10. This lands with [#505](https://github.com/mshamblin5150-code/clinical-skills/issues/505)
on one branch, and neither blocks the other.** ADR 0068 ruling 10 already records the hazard:
#505 rewrites the interval clause of the **same generated paragraph** at
`reference/guidelines-uspstf.md:5`, and ruling 5 above rewrites its population clause.
**Whichever lands second re-reads that paragraph from the generator at `uspstf_table.py:832-845`
and never from a quotation, including the ones in this record.** That is
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s byte-identical trap
in a file that has produced one already.

**Co-landing is a saving and not a sequencing constraint.** Both rebuild the artifact and each
busts `artifact_provenance.CACHE_IDENTITY["recs"]`; landing together pays the rebuild once.

**The span above was cited as `:833-846` for one commit**, which is off by one — `:831` is the
`out.append(` and `:846` the closing paren — in the sentence whose whole point is to re-read the
paragraph from the generator rather than from a quotation. ADR 0068 ruling 10 cites it correctly.
Caught by the sweep this session ran, which is the citation this record makes about itself failing
in the one way it warns about.

**11. The section's width is safe by coincidence and the build says so.**
`differential_scan._uspstf_index` at `:742` walks **the whole artifact**, anchored to no section,
admitting any row of exactly nine cells whose third is a grade and whose fifth is a four-digit
year. The section ruled here is three cells wide and ADR 0068 ruling 2's is three, so neither is
picked up — **by column count, not by design.** A later section shaped like `## Recommendations`
would mint citation rows silently. That is [#641](https://github.com/mshamblin5150-code/clinical-skills/issues/641)'s
parser and belongs in its build; it is named here so the next author of a generated section in
this file meets it, rather than discovering it.

## Consequences

**The rebuild is not free and is not this ruling's to avoid.** Any byte change to
`reference/guidelines-uspstf.md` busts `CACHE_IDENTITY["recs"]` and refuses every
`curated-table` recommendation record until re-produced —
[ADR 0030](0030-a-recommendation-record-is-owned-like-every-other-artifact-its-trust-floor-is-keyed-on-the-limb-that-built-it-and-the-drafter-takes-no-escape-hatch.md)
ruling 2, priced by ADR 0045 at **56 minutes of CPU for 179 byte-identical records**,
byte-identical because `population` never leaves `CuratedRow`
(`guidelines_recs.DECLARED_LIMITS`'s `curated-metadata-unrecorded`, #589). **#545's *Done when*
prices this at three records**, which is stale by two orders of magnitude and predates
[ADR 0049](0049-the-sweep-alias-and-the-recs-root-are-two-lookup-roots-with-two-resolution-rules-and-the-producer-guarantees-the-prefix-it-writes.md)
ruling 2 making the sweep alias win, so hand-rebuilt recs-root records would be shadowed.
The remedy is *rerun the sweep*.

**Nothing downstream changes.** `parse_curated_table` and `CuratedRow` are untouched, the
`## Recommendations` table stays nine columns wide, and no character enters the string a note
copies. #545's decision 3 dissolves rather than being answered.

**What no limb reaches.** Whether a field-quoted population is the *right* population for the
recommendation, which is a reading of the document. Tier 1 cannot see it and tier 2 establishes
only that the cell is the declared field verbatim. **A listed pair is a provenance claim, never
a clinical one.**

## The glossary term

```
**Field quotation**:
A cell quoted from a structured field the document declares, where the column's rule
primarily reads a passage of its prose. It is a second passage of the same document, not a
second source. It cannot be checked against the statement the artifact ships beside its row,
which is why such cells are listed rather than left to a re-derivation.
_Avoid_: fallback, second source, default, secondary
```

It already covers `Topic`'s metadata-title route. It does **not** cover `Topic`'s filename-slug
route, which is not a quotation of the document at all — a reason to file that ticket rather
than fold it in.
