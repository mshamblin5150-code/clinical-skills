# The uspstf interval derivation reaches one sentence and that reach is ruled permanent

[#435](https://github.com/mshamblin5150-code/clinical-skills/issues/435) was filed because
`uspstf_table.derive_interval` reads **one sentence** — the recommendation statement its row
was cut from — and 131 of 143 rows therefore read `not stated`. The ticket's charge is that
`not stated` reads as *this document states no interval* when the honest claim is *no interval
appears in this sentence*, and that USPSTF states screening intervals in sections one headline
sentence cannot reach.

The charge is correct about the reach and wrong about what widening the reach would buy.

Grilled 2026-08-24. **Seven decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads. [ADR 0027](0027-the-uspstf-interval-column-names-the-recurrence-of-a-service.md)
ruled *what the column is*; this rules *how far the derivation reaches*, and rules that the
reach is a decision rather than a limitation awaiting a fix.

## The measurement came before the ruling and inverts the ticket's premise

The ticket's own first *Done when* asks how many documents state an interval outside the
statement sentence, and names that as its first job rather than its premise. It was measured
against the extracted text of the 90 USPSTF documents before anything was decided.
`tools/uspstf_interval_reach.py` owns every figure below and this record copies no row it does
not print.

**The population is files, not rows.** 143 rows, 131 `not stated`, **88 files carrying at least
one**, 80 where every row is one. The ticket asks its question against "the 131 documents";
131 is a row count and the widening's denominator is 88. That unit error is this ticket's own
subject one level up — a reach mistaken for an absence, in the measurement rather than in the
tool.

**A naive read says the 131 is not empty, and answers the wrong question.** Run
`INTERVAL_PHRASE` over the whole document and 71 of the 88 carry a phrase the statement lacks.
That pool is references, trial arms, comparator schedules and other societies' recommendations.

**Both discriminators the ticket's decision 2 names were implemented and run.** A region rule
keyed on a standalone `Screening Interval(s)` heading — the sharpest named region the corpus
offers — and an attribution rule keyed on a USPSTF-subject recommending verb anywhere in the
document.

| against the 88 | pre-#434 vocabulary | post-#434 vocabulary |
| --- | ---: | ---: |
| naive whole-document phrase | 71 | 64 |
| `Screening Interval` region, new phrase | 9 | 9 |
| attributed sentence, new phrase | 9 | 5 |
| … at least one unhedged | 5 | 2 |

**Of the region's nine, two are real recoveries and seven are wrong.** `hypertension-screening-adults`
states *"The USPSTF suggests annual screening for hypertension in adults 40 years or older"* —
genuinely the USPSTF's own interval, genuinely outside the statement.
`colorectal-cancer-screening` carries a per-modality table of six intervals against three rows
of differing grade. The other seven are evidence discussion, and **three of them fire on the
sentence stating that no interval exists**:

> The USPSTF found no evidence on appropriate or recommended screening intervals, and the
> optimal interval is unknown. **Repeated** screening may be…

`repeated` and `1-time` are in `INTERVAL_PHRASE` and ADR 0027 ruling 7 keeps them deliberately.
So a widened rule converts *the document states there is no interval* into a cell asserting one,
in the region best positioned to be trustworthy. That is worse than `not stated`, and it is the
failure the ticket's own *What must not come out of this* forbids.

**The attribution limb fails the ticket's own calibration row.** Of its five unhedged hits, one
is real, two are doses, one is cross-topic bleed — `falls-prevention` picking up the osteoporosis
recommendation from *Other Related USPSTF Recommendations* — and one is
`vitamind-calcium` taking `annual` off *"A single study suggested that an annual high dose of
vitamin D…"*, the trial arm #435's body names as the expensive direction, caught live.

**And the one clean recovery does not fit its cell.** The `hypertension` row's `population` is
*adults 18 years or older*; the recovered interval attaches to *adults 40 years or older*. The
best available recovery in the corpus would put a cell on a row whose population contradicts it.

**The ruling does not depend on which way #434 goes**, and that is a finding rather than a
convenience. ADR 0027 ruling 2 removes `\bdaily\b`, and three of the five unhedged attribution
candidates were `daily`. Under both vocabularies the two discriminators reach 9 and 2 files out
of 88 and the region's candidates stay seven-eighths wrong. The next reader's first move will
be to ask whether the measurement predates the column's contract changing; it was taken through
both.

## The ruling

**1. The region is not widened, and the reach is permanent.** Not deferred, not blocked on a
better discriminator. Measured yield is one to two rows out of 88 against false-positive rates
of four to one and seven to one in the best regions the corpus offers, with three of the misses
inverting a stated absence into an asserted interval. This is *declare the coverage rather than
widen the instrument* — [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)
and [#141](https://github.com/mshamblin5150-code/clinical-skills/issues/141)'s standing rule —
arriving at a clinical index.

The two rejected options are recorded because the next reader will reach for one. **Widen
narrowly** — attributed, unhedged, population-compatible — moves roughly one cell on a
discriminator calibrated against five instances, which is `SPACE_ADVANCE_FRACTION` named at an
edge and `case_study_scan`'s `ENDPOINT` failing correct orders, both already in this tree.
**Widen and mark** puts the trial-arm value in the column and asks the reader to discount it,
which is the contract failure #435 forbids in as many words. The ticket's decisions 2 and 3
dissolve with ruling 1: there is no region to choose and no marker for cells that will not
exist.

**2. The instrument becomes a `tools/` module and carries both declined discriminators.**
[ADR 0012](0012-a-measurement-instrument-becomes-a-tools-module-when-its-question-reopens.md)'s
test 1 is an unambiguous yes — a corpus refresh adds statements and #434 edits `INTERVAL_PHRASE`
itself, which moves the *phrase the statement lacks* denominator directly.

Carrying the declined rules is the part that is not automatic. The ruling's force is not
*71 of 88 mention a period*; it is *the two best discriminators yield 2 and 1, and seven of nine
sharpest candidates are wrong*, and only code implementing the rejected rules produces that.
Dropped, the figure is orphaned the day it is written — ADR 0012 ruling 3 — and the next reader
re-derives 64-of-88, finds it damning, and refiles.

`INTERVAL_PHRASE` is imported rather than copied, per ADR 0012 ruling 4. **The two declined
discriminators are the module's own, and that is a departure from that ruling's spirit named
here rather than left for a reviewer**: they implement no live rule, so there is nothing to
share them with.

**3. Committed excerpts make re-proposal cost a failing test rather than an argument.** The
`screening-anxiety-children` and `latent-tuberculosis` pages join `tools/testdata/uspstf/`, and
a test asserts the declined region rule fires on them. USPSTF text is federal public domain,
that directory already holds six such excerpts, and `reference/guidelines-uspstf.md` ships
statements wholesale on the same ground.

This is `test_research_ledger.TheDeclinedParserRowsFireOnCorrectOrders`'s arrangement, which
this tree already built for a declined parser row. Without it the whole ruling rests on figures
only the maintainer's machine can produce, because the corpus is outside the repo and **nothing
in CI can ever run the instrument**.

**4. The build waits on [#434](https://github.com/mshamblin5150-code/clinical-skills/issues/434).**
Its vocabulary change moves three of the five unhedged fixtures, so an instrument calibrated
today has fixtures that stop firing when #434 merges — a declined-option test going green for
the wrong reason. One tree, one vocabulary, one artifact, per
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180). The price is that
#435 is the first ticket to depend on #434 being built and stalls if it stalls; the fallback at
that point is publishing both vocabularies' figures, not re-litigating ruling 1.

**5. The reopening signal is a population pin against the committed artifact.** A test derives
row count, `not stated` count and the count of files carrying at least one from
`reference/guidelines-uspstf.md` and asserts them, with the failure message naming the
instrument and this record. Pinned at rows and files rather than at the whole derivation, so it
fires when documents or intervals move and stays quiet otherwise.

Prose fails nothing — ADR 0027 ruling 4, [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)
and [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) — and here the
concrete failure is a reader running a grep, finding 64 of 88 documents mentioning a period, and
widening the rule.

**Having the builder also report was declined.** `guidelines_extract`'s `symbol_glyph_census`
earns its place because a symbol font nobody has looked at is otherwise invisible; here the
artifact's own row population moves visibly on the same event, so a builder report is a second
mechanism for one trigger and puts a figure a consumer does not need into the one file a
consumer meets. `docx_write`'s finding: *a second mechanism that cannot fail is not a belt and
braces; it is a line that costs a test.*

**The price is named rather than discovered**, on ADR 0027 ruling 5's terms: the next corpus
refresh turns the suite red for a population change nobody caused, and whoever refreshes pays
for re-running the instrument and re-reading this record.

**6. The header states the reach as a ruling and discloses the residue, in one clause each.**
Generated at `tools/uspstf_table.py`, so there is no prose-drift hazard on it. ADR 0027 ruling 6
already has #434 disclose the dose exclusion in this paragraph; these fold into the list that
edit builds rather than appending sentences to it. **No figure goes in the header** — the
figures belong to the instrument and to this record.

The residue clause is [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
rule where the failure is live: a reader who meets *"outside the rule's reach"* and nothing else
takes `not stated` to mean the document is silent, and for eight documents the document is the
opposite of silent.

**7. No new glossary term.** `Reach` is already covered by `Declared limit`, whose definition is
*a boundary of what a mechanism reaches*, and `Interval` was scoped to this column at `07de8dd`.
A term here would be a sixth location rather than a clarification.

## The declared limit this ruling is known to be hiding

**Eight documents state, outside the statement sentence, that no interval is established** —
`anxiety-adults`, `depression-suicide-risk-adults`, `hypertension`, `ipv`,
`latent-tuberculosis`, `screening-anxiety-children`, `screening-depression-children`,
`syphilis`. All eight carry `not stated` rows, and in the cell that is indistinguishable from a
recommendation that is simply not periodic.

*The USPSTF looked and found no evidence for an interval* is a different fact from silence, and
a clinician can act on it. It is out of reach for exactly the reason ruling 1 gives, and
**three of these eight are the same documents that would have poisoned a widened rule** — the
sentence carrying the real clinical fact is the sentence that injects `repeated` into a cell.

It gets its own ticket rather than a sentinel in this column.
[ADR 0009](0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md)
rules that decision-point presence is read off what the guideline **states** and never off an
index derived from it, and `reference/guidelines-uspstf.md` is exactly such an index — so the
threshold sheet is the likely home and this table is the wrong artifact by an existing ruling.
ADR 0027 ruling 6 reached the same outcome for the four dose rows by a different argument.

## Measured before ruling, at `9dd61fd`

- 143 rows, 131 `not stated`, 88 files with at least one, 80 all `not stated`. Re-derived in
  this session rather than taken from #417's sweep, which reports the same.
- The post-#434 column is a **hybrid** and is labeled one: the new vocabulary was run against the
  committed artifact's `not stated` set, which is the pre-#434 one. After #434 rebuilds, the row
  count goes 131 to 135 and the file set may move. The artifact was not rebuilt, because a figure
  correct about a measurement and wrong about the artifact is #180's subject.
- Two of #435's body facts were re-derived and corrected: the population denominator is 88 rather
  than 131, and `vitamind-calcium-fracture-prevention` carries **two** calibration rows rather
  than one, at `reference/guidelines-uspstf.md:164` and `:166`.
- #435's *Done when* clause *"no correct row loses its cell to the change"* is satisfied
  trivially under ruling 1 — nothing here moves a cell. It remains contradicted by #434, under
  which four rows deliberately lose theirs on the ground that those cells were never correct.
