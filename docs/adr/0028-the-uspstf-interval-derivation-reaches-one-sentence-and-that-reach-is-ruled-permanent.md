# The uspstf interval derivation reaches one sentence and that reach is ruled permanent

[#435](https://github.com/mshamblin5150-code/clinical-skills/issues/435) was filed because
`uspstf_table.derive_interval` reads **one sentence** — the recommendation statement its row
was cut from — and 135 of 143 rows therefore read `not stated`. The ticket's charge is that
`not stated` reads as *this document states no interval* when the honest claim is *no interval
appears in this sentence*, and that USPSTF states screening intervals in sections one headline
sentence cannot reach.

The charge is correct about the reach and wrong about what widening the reach would buy.

Grilled 2026-08-24. **The decisions below were ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads. [ADR 0027](0027-the-uspstf-interval-column-names-the-recurrence-of-a-service.md)
ruled *what the column is*; this rules *how far the derivation reaches*, and rules that the
reach is a decision rather than a limitation awaiting a fix.

## The measurement came before the ruling and inverts the ticket's premise

The ticket's own first *Done when* asks how many documents state an interval outside the
statement sentence, and names that as its first job rather than its premise. It was measured
against the extracted USPSTF text before anything was decided. The current measurement was
taken on 2026-08-29, in files, rows, and files with a matching discriminator, against a trusted
branch-private extraction produced by `tools/guidelines_extract.py`; it is a dated observation
rather than a claim about an untracked corpus's present state. Reproduce it with
`python tools/uspstf_interval_reach.py C:/codeing/guidelines-text`.
`tools/uspstf_interval_reach.py` owns every mechanically derived corpus figure below and this
record copies no count it does not print.

**The population is files, not rows.** 143 rows, 135 `not stated`, **89 files carrying at least
one**, 83 where every row is one. The ticket asks its question against a document population
but supplies a row count; the widening's denominator is 89. That unit error is this ticket's own
subject one level up — a reach mistaken for an absence, in the measurement rather than in the
tool.

**A naive read says the 135 is not empty, and answers the wrong question.** Run
`INTERVAL_PHRASE` over the whole document and 64 of the 89 carry a phrase the statement lacks.
That pool is references, trial arms, comparator schedules and other societies' recommendations.

**Both discriminators the ticket's decision 2 names were implemented and run.** A region rule
keyed on a standalone `Screening Interval(s)` heading — the sharpest named region the corpus
offers — and an attribution rule keyed on a USPSTF-subject recommending verb anywhere in the
document.

| against the 89 | post-#434 vocabulary and artifact |
| --- | ---: |
| naive whole-document phrase | 64 |
| `Screening Interval` region, new phrase | 9 |
| attributed sentence, new phrase | 5 |
| … at least one unhedged | 2 |

**The region is dominated by wrong candidates.** `hypertension-screening-adults`
states *"The USPSTF suggests annual screening for hypertension in adults 40 years or older"* —
genuinely the USPSTF's own interval, genuinely outside the statement. *(This sentence and the
declared-limit section below contradicted each other about this document until 2026-08-29, when
[ADR 0068](0068-a-stated-evidence-absence-is-read-into-the-uspstf-artifact-and-the-class-is-named-for-what-the-source-says.md)
resolved it in favor of this one and withdrew the list.)*
`colorectal-cancer-screening` carries a per-modality table against rows of differing grade.
The rest are evidence discussion, and some fire on the sentence stating that no interval exists:

> The USPSTF found no evidence on appropriate or recommended screening intervals, and the
> optimal interval is unknown. **Repeated** screening may be…

`repeated` and `1-time` are in `INTERVAL_PHRASE` and ADR 0027 ruling 7 keeps them deliberately.
So a widened rule converts *the document states there is no interval* into a cell asserting one,
in the region best positioned to be trustworthy. That is worse than `not stated`, and it is the
failure the ticket's own *What must not come out of this* forbids.

**The attribution limb fails the ticket's own calibration row.** Of its two unhedged hits,
`hypertension` is a genuine recovery and `vitamind-calcium` takes `annual` off *"A single study
suggested that an annual high dose of vitamin D…"*, the trial arm #435's body names as the
expensive direction, caught live.

**And the clean recovery does not fit its cell.** The `hypertension` row's `population` is
*adults 18 years or older*; the recovered interval attaches to *adults 40 years or older*. The
best available recovery in the corpus would put a cell on a row whose population contradicts it.

**The ruling did not depend on which way #434 went**, and that is a finding rather than a
convenience. The dependency removed `\bdaily\b` from ADR 0027 ruling 2 before this measurement.
The committed measurement above is the required single pairing: the post-#434 vocabulary
against the post-#434 artifact.

## The ruling

**1. The region is not widened, and the reach is permanent.** Not deferred, not blocked on a
better discriminator. Measured yield is slight and false positives dominate the best regions
the corpus offers, including misses that invert a stated absence into an asserted interval.
This is *declare the coverage rather than
widen the instrument* — [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)
and [#141](https://github.com/mshamblin5150-code/clinical-skills/issues/141)'s standing rule —
arriving at a clinical index.

The two rejected options are recorded because the next reader will reach for one. **Widen
narrowly** — attributed, unhedged, population-compatible — moves very little on a
small calibration set, which is `SPACE_ADVANCE_FRACTION` named at an
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
*the naive whole-document read mentions a period often*; it is *both best discriminators have
low yield and the sharpest region remains dominated by wrong candidates*, and only code
implementing the rejected rules produces that.
Dropped, the figure is orphaned the day it is written — ADR 0012 ruling 3 — and the next reader
re-derives 64 of 89, finds it damning, and refiles.

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
Its vocabulary change moves the measured candidates, so an instrument calibrated before it
has fixtures that stop firing when #434 merges — a declined-option test going green for
the wrong reason. One tree, one vocabulary, one artifact, per
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180). The price is that
#435 is the first ticket to depend on #434 being built and stalls if it stalls; the fallback at
that point is publishing both vocabularies' figures, not re-litigating ruling 1.

**5. The reopening signal is a row-count pin against the committed artifact.** *Population* here
means the size of the row set this ruling was measured over, and never the artifact's
`Population` column, which is
[#502](https://github.com/mshamblin5150-code/clinical-skills/issues/502)'s subject and is
untouched by anything here. A test derives
row count, `not stated` count, the count of files carrying at least one, and the count whose
rows are all `not stated` from
`reference/guidelines-uspstf.md` and asserts them, with the failure message naming the
instrument and this record. Pinned at rows and files rather than at the whole derivation, so it
fires when documents or intervals move and stays quiet otherwise.

Prose fails nothing — ADR 0027 ruling 4, [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)
and [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) — and here the
concrete failure is a reader running a grep, finding periods across many documents, and
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
takes `not stated` to mean the document is silent, while some documents are the
opposite of silent.

**7. No new glossary term.** `Reach` is already covered by `Declared limit`, whose definition is
*a boundary of what a mechanism reaches*, and `Interval` was scoped to this column at `07de8dd`.
A term here would be a sixth location rather than a clarification.

## The declared limit this ruling is known to be hiding

**Some documents state, outside the statement sentence, that the USPSTF looked for evidence on
the screening interval and found none.** They carry `not stated` rows, and in the cell that is
indistinguishable from a recommendation that is simply not periodic.

**Corrected in place on 2026-08-29.** This paragraph named eight documents. That membership was
measured by one phrase family on 2026-08-24 at `9dd61fd` and **was wrong in both directions**;
the list is withdrawn rather than reprinted one member shorter, because an unre-derivable list
inside a ratified record is where the error lived and where seven sweeps went to confirm it —
`CONTEXT.md`'s **Underived count**, *derive it or drop it*. The three movements are named because
a later session will otherwise re-derive eight from this record's history: `hypertension` and
`syphilis` were **not** members — each characterizes its evidence as *limited* rather than absent
and each states an interval of its own — and `hepatitis-b` was a member and was missing.
Membership belongs to the generated section ruled in
[ADR 0068](0068-a-stated-evidence-absence-is-read-into-the-uspstf-artifact-and-the-class-is-named-for-what-the-source-says.md),
which is graded rather than asserted.

**And the class was misnamed here.** No document says no interval is established; each says the
USPSTF *found no evidence*, and most then offer an approach in its absence. The wrong name is
what admitted the two wrong members, since both fit it and neither fits the right one.

*The USPSTF looked and found no evidence for an interval* is a different fact from silence, and
a clinician can act on it. It is out of reach for exactly the reason ruling 1 gives, and
**some are the same documents that would have poisoned a widened rule** — the
sentence carrying the real clinical fact is the sentence that injects `repeated` into a cell.

It gets its own ticket rather than a sentinel in this column.
[ADR 0009](0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md)
rules that decision-point presence is read off what the guideline **states** and never off an
index derived from it, and `reference/guidelines-uspstf.md` is exactly such an index — so this
table is the wrong artifact by an existing ruling. ADR 0027 ruling 6 reached the same outcome
for the dose rows by a different argument.

**Where it goes instead is unsettled, and the tracker sweep of 2026-08-24 found that saying
*the threshold sheet* is wrong.** A stated absence carries **no quantity**, so it is not a
decision point under ADR 0009 point 1; [#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429)
rules that *a document with no quantity gets no sheet*; `tools/threshold_sheet.py` refuses a
sheet carrying zero rows; and ADR 0026's `narrative` locator — which solved
[#464](https://github.com/mshamblin5150-code/clinical-skills/issues/464)'s Practice
Considerations gap — still requires a row with a value. The registry's `none` state is the one
vocabulary that expresses *read and states no decision point*, and
[#483](https://github.com/mshamblin5150-code/clinical-skills/issues/483) is open precisely
because `none` has nowhere to put its evidence.

So the stated-absence class currently has **no artifact anywhere in the tree**, and #505 is
open on where it goes rather than on how it is written. That is recorded here because the
first draft of this record asserted the routing as settled.

**Settled on 2026-08-29 by ADR 0068**, and by neither candidate above: the class is recorded in a
generated `##` section of `reference/guidelines-uspstf.md`, membership is read rather than matched,
and #505 is unblocked from #483 because nothing in that build touches a threshold sheet, the
coverage registry or a `none` row. Ruling 1 above is untouched — no derivation widens and no cell
moves.

## Dated observation after #434 — 2026-08-29

`python tools/uspstf_interval_reach.py C:/codeing/guidelines-text` prints the population and
all four mechanical yields in the measurement table above. The population pin independently
derives 143 rows, 135 `not stated` rows, 89 files carrying at least one, and 83 files where every
row is `not stated` from the committed artifact.

The original 2026-08-24 measurement at `9dd61fd` used the pre-#434 artifact and is preserved in
the ticket's ruling comment. It is historical evidence rather than the current measurement;
mixing its row population with the post-#434 vocabulary was the hybrid this build order forbade.

- The population denominator was re-derived and corrected: it is 89 files rather than the
  row count supplied by the ticket. The named `vitamind-calcium-fracture-prevention`
  calibration rows are at `reference/guidelines-uspstf.md:166` and `:168`.
- #435's *Done when* clause *"no correct row loses its cell to the change"* is satisfied
  trivially under ruling 1 — nothing here moves a cell. It remains contradicted by #434, under
  which dose rows deliberately lose theirs on the ground that those cells were never correct.
