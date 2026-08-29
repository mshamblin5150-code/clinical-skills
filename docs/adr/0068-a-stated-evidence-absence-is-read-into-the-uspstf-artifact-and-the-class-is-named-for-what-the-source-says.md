# A stated evidence absence is read into the uspstf artifact and the class is named for what the source says

[ADR 0028](0028-the-uspstf-interval-derivation-reaches-one-sentence-and-that-reach-is-ruled-permanent.md)
ruled the `Interval` derivation's one-sentence reach permanent and closed with a section headed
*"The declared limit this ruling is known to be hiding"*: a class of USPSTF document that speaks to
the screening interval outside the statement sentence, whose rows therefore read `not stated` in a
cell that cannot tell it from a recommendation that is simply not periodic.
[#505](https://github.com/mshamblin5150-code/clinical-skills/issues/505) is that residue.

Grilled on 2026-08-29 against `origin/main` at `87b2ed9`. The clinician ruled all ten points below
on that date. **Nothing is built here; this is the record the build reads.**

## The measurement that reframed it

ADR 0028's declared-limit section named eight documents, measured on 2026-08-24 at `9dd61fd` by one
phrase family over the extracted corpus. #505 inherited the list. Seven tracker sweeps re-derived it
between 2026-08-24 and 2026-08-28 and every one of them reported it holding.

**Every one of those re-derivations checked the artifact's cells.** The eight contribute 14 rows and
all 14 read `Interval = not stated` — true, stable, and not the claim at risk. The membership claim
is about the *documents*, and confirming it needs the corpus rather than the index. Re-read against
`C:/codeing/guidelines-text` on 2026-08-29, the set is wrong in **both** directions.

**Two named documents do not carry the claim.**

`hypertension-screening-adults-final-rec-statement` states, at its own `Screening Intervals`
heading, *"Available evidence on optimal screening intervals for hypertension remains limited"* —
evidence characterized, not absent — and the same document states an interval of its own:
*"Screening for hypertension every year in adults 40 years or older."*

`syphilis-nonpregnant-adults-screening-final-recommendation` states *"Although evidence on optimal
screening intervals is limited for the general population, men who have sex with men or persons with
HIV infection may benefit from screening at least annually or more frequently (eg, every 3 to 6
months)"*, and separately *"Optimal screening frequency for persons who are at increased risk for
syphilis infection is not well established."*

**One document that carries it was never listed.**
`hepatitis-b-screening-adults-adolescents-final-rec-statement`, page 3: *"The USPSTF found no
evidence to determine optimal screening intervals."*

**And ADR 0028 already contradicted itself about `hypertension`.** Its measurement section calls that
document's `annual` *"genuinely the USPSTF's own interval, genuinely outside the statement"* and
names it as the attribution limb's one true recovery; its declared-limit section four paragraphs
later lists the same document as stating that no interval is established. Both cannot be true. The
measurement section is right.

**The class name was false of every member.** No document in the class says no interval is
established. Each says the USPSTF **found no evidence**, and most then offer an approach in the
absence of it — `latent-tuberulosis`: *"In the absence of evidence, a reasonable approach is to
repeat screening based on specific risk factors; screening frequency could range from 1-time only
screening among persons at low risk for future tuberculosis exposure to annual screening among those
at continued risk of exposure."* The wrong name is what admitted the two wrong members: both fit
*"no interval is established"* loosely and neither fits *"found no evidence"* at all.

## The ruling

**1. The stated absence is recorded rather than left as a declared limit.** ADR 0035 rulings 1 and 3
settled *read and found nothing gets a self-declaring artifact* at topic width and
[ADR 0045](0045-the-recommendation-sweep-is-a-third-cache-stage-its-records-are-keyed-on-doc-id-and-a-document-that-yields-nothing-declares-itself.md)
ruling 3 adopted it at document width. This is the same question at **quantity** width, and it now
has two ruled precedents rather than an argument.

**2. The venue is a generated section in `reference/guidelines-uspstf.md`, not a column and not a
sentinel.** A further column is refused on a measurement rather than on taste:
`guidelines_recs._markdown_rows(markdown, "Recommendations", 9)` drops every row whose width differs
and `parse_curated_table` then raises `DidNotScan`, which under ADR 0045 ruling 3 refuses the **whole
179-document recs build** with a message naming a missing table. A sentinel in the cell was declined
twice already — ADR 0027 ruling 6 for the dose rows, and
[ADR 0052](0052-a-codification-year-is-provenance-and-the-snapshot-behind-it-is-declared-unreached.md)
ruling 5 records sentinel dominance as *"a real cost"* at 21 of 22, where this column stands at 135
of 143. A new `##` section is the only venue that pays nothing beyond the artifact rebuild that every
venue pays.

**The rebuild is not free and is not this ruling's to avoid.** Any byte change to the file busts
`artifact_provenance.CACHE_IDENTITY["recs"]` and refuses every `curated-table` recommendation record
until re-produced — ADR 0030 ruling 2, priced by ADR 0045 at 56 minutes of CPU for byte-identical
records, because `interval` never leaves `CuratedRow` (`guidelines_recs.DECLARED_LIMITS`'s
`curated-metadata-unrecorded`). That cost was already paid once by the header sentence this record
replaces.

**3. Membership is read, never matched.** A declared `INTERVAL_ABSENCES` object in
`tools/uspstf_table.py`, on `INTERVAL_EXCLUSIONS`' precedent — a tuple read by no production code —
which the builder renders. There is no production matcher and there is no false-positive rate to
measure, because nothing proposes a member.

**ADR 0028 ruling 2 is why, and this ruling does not touch it.** That record put the declined
discriminators in `tools/uspstf_interval_reach.py` *"so a corpus refresh ... can re-run the question
without quietly turning either discriminator into a live derivation rule."* A production absence
matcher would run over the same region ADR 0028 measured as dominated by wrong candidates, and would
be tuned against a count already known — the outcome #505's own *What must not come out of this*
forbids in as many words.

**4. The instrument gains a candidate limb, and it builds nothing.**
`tools/uspstf_interval_reach.py` reports how many documents a naive absence phrase reaches and how
many of those the committed list already names. A corpus refresh then surfaces an unlisted candidate
as a number that moved on a command already run. This is what keeps ruling 3's read honest without
making it a rule, and it is what #505's first *Done when* is respecified to.

**5. The class is narrow: the source states it found no evidence on the screening interval.**
*Limited*, *not well established*, and every other characterization of evidence the source does have
are outside it. The reason is clinical rather than tidy: both documents carrying that language name
an interval of their own, so a row telling a clinician that the USPSTF established no interval for
hypertension — a document that says *screen every year over 40* — is worse than the `not stated` cell
this ticket was filed to improve on. It is ADR 0028 ruling 1's rejected *widen and mark* arriving
through a hand-read list rather than a regex.

**6. A row quotes the whole passage, including what the document offers in evidence's absence.**
The bare negative is very nearly what the cell already conveyed; the actionable half is the
continuation. `Page` is the page the quote was taken from.

**Two build hazards are named here rather than discovered.** `latent-tuberulosis` carries a complete
passage **twice**, on pages 3 and 4 in different wording — so the quote does not by itself settle the
page, and the rule is that the passage under the document's own standalone `Screening Intervals`
heading wins, which is page 4. *(This corrects an overstatement made during the grilling, where the
ambiguity was said to disappear; it narrows to a stated rule.)* And
`screening-anxiety-children`'s passage is **truncated in the extracted text** — it ends mid-sentence
at *"Repeated"* where a figure caption interrupts the stream. That is the one member whose complete
passage cannot be quoted from the extraction, and it needs the rendered page, on
`threshold_sheet.py`'s `RENDERED:` precedent.

**7. Five tier-1 limbs grade the committed list in CI; one tier-2 limb grades it where the corpus
is.** `threshold_sheet.py`'s citation arrangement and its reason — *there is no machine on which
checking drops to zero*. Tier 1: every named filename appears in `## Recommendations`; every one of
its rows reads `not stated`; `Page` is within that document's `page_count` in
`reference/guidelines-catalog.md`; the quote is not identical to any of that document's committed
`## Statements` entries; and the quote contains a phrase from a declared absence vocabulary. Tier 2:
the normalized quote occurs on the cited page of the extracted document, skipping with a banner that
survives `--quiet`.

**Limb 5 is the ruling and the other four are hygiene.** Limbs 1 through 4 would all have passed the
wrong eight. A vocabulary that can only **refuse** a row a human wrote — never propose one — is not
ruling 3 reversed, and the next reader meeting a regex over interval language in this module will
think it is. The direction is the whole difference.

**The incomplete quote is a declared reading.** A builder who stops one sentence early, dropping
`latent-tuberulosis`'s *1-time to annual*, passes every limb including tier 2. Under ruling 6 that is
the most expensive available failure and nothing mechanical reaches it.

**8. The header carries one pointing clause and the section preamble owns the boundary.** Not both.
ADR 0027 ruling 6's *"the header is the only place a consumer meets this column"* was true while
there was nothing else to read and stops being true when the section exists; two generated prose
copies of one rule, each editable and neither failing anything, is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).

**There is a third generated copy of the interval-derivation claim, and a builder must not make
it a fourth.** `reference/guidelines-uspstf.md:175` — the `## Statements` preamble, generated at
`tools/uspstf_table.py:932` — also states that *"`interval` is derived from the statement."* That
sentence stays **true** after this ruling and is therefore not corrected here; it is named because
ruling 8's *not both* has three sites to police rather than two, and because the sweep that found it
records that two earlier counts of these copies each missed this one. The retired *no interval is
established* clause exists only at `:5`.

**The preamble's non-membership paragraph is load-bearing and is not trimmable.** Once seven
documents are listed, absence from the list becomes a claim, and it is false for exactly the two
documents ruling 5 removes. A reader who looks up a `not stated` cell, finds nothing, and concludes
the document is silent has been misled harder than the bare cell misled them — which is
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s shape landing on a
mechanism built to fix a different instance of it. Any count in that preamble is rendered from
`len(INTERVAL_ABSENCES)` and never typed.

**9. ADR 0028's list of eight is deleted rather than corrected, and this record publishes no standing
list either.** Replacing eight prose stems with seven prose stems rebuilds the defect one member
smaller: an unre-derivable list inside a ratified record, which is where this error lived for five
days and where seven sweeps went to confirm it. `CONTEXT.md`'s **Underived count** already rules the
remedy — *"derive it or drop it; the corrected number is as underived as the wrong one."* Membership
becomes the generated section's to state, graded by ruling 7. ADR 0028 keeps the declared limit, is
corrected in place to withdraw the list and name the three movements, and its internal contradiction
about `hypertension` is resolved in favor of its measurement section.

**The dated observation below is not that list**, on ADR 0028's own precedent for a measurement
whose corpus lives outside the repo.

**10. #505 is unblocked from [#483](https://github.com/mshamblin5150-code/clinical-skills/issues/483)
and is not sequenced against [#545](https://github.com/mshamblin5150-code/clinical-skills/issues/545).**
The `blocked_by` relation was recorded on 2026-08-25 when the venue was assumed to be the coverage
registry's `none` state; ruling 2 replaced that assumption, and nothing in this build touches a
threshold sheet, the registry or a `none` row. ADR 0035:146 and ADR 0066:192 both say *"This does not
close #505"* — which reads correctly as *these are different mechanisms*, not as *#505 waits for
more*.

**What replaces sequencing is a named hazard in both records.** #545 proposes a provenance mark on
the same file's `Population` column and its cheapest option is header disclosure. Ruling 8 rewrites
the interval clause of the **same generated paragraph** at `reference/guidelines-uspstf.md:5`, which
ADR 0044 ruling 4 last reshaped and whose reshaping created #545. Whichever lands second re-reads
that paragraph from the generator at `tools/uspstf_table.py:832-845` and never from a quotation,
including the ones in this record. This is
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s byte-identical trap in a
file that has already produced one.

## The glossary term, and why ADR 0028 ruling 7 does not settle it

That ruling refused a term for `reach`, correctly: `reach` is a boundary of a **mechanism** and
`Declared limit` already covers it. This is a fact about a **source**, and nothing in the glossary
covers it. Four things in this tree now mean nearly-nothing-shaped things and none is the others — an
`Interval` cell's `not stated` (a derivation found nothing), a `nothing-found` recommendation record
(two reader limbs matched nothing), a `none` sweep state (a read found no decision point), and this.
ADR 0045 ruling on the word `none` already spent a whole ruling policing the boundary between the
second and third, which is evidence the vocabulary was under pressure at three members.

**The naming failure is this session's own finding**, so the entry's discriminating sentences are the
deliverable rather than the definition: that the source is the one speaking, that finding no evidence
is not saying the quantity is unestablished, and that characterizing evidence as *limited* does not
earn it.

**Checked and negative:** `skills/clinical-note/SKILL.md:1126`'s *"The three silences are not
interchangeable"* and ADR 0017's *"There is no fourth silence"* are both about the three meanings of a
missing row inside a threshold sheet, and `SKILL.md:645`'s two-silences section is about topic
coverage. Nothing here adds a fourth to either set and no committed claim about silences is
falsified.

## Dated observation — 2026-08-29

Read against `C:/codeing/guidelines-text` at `origin/main` `87b2ed9`. **A floor, not a set**: it is
what one read found, the corpus lives outside this repo, and ruling 4's instrument exists because the
next refresh moves it. Recorded so the build has a starting point, not so a later session can cite it
as membership — that is the generated section's to state once ruling 2 is built.

Seven documents, contributing 13 rows to `## Recommendations`, all 13 reading `Interval = not stated`:
`anxiety-adults-screening-final-recommendation` p4,
`depression-suicide-risk-adults-rs` p4,
`hepatitis-b-screening-adults-adolescents-final-rec-statement` p3,
`ipv-screening-final-rec-statement` p3,
`latent-tuberulosis-screening-final-rec-statement` p4,
`screening-anxiety-children-final-recommendation` p3,
`screening-depression-suicide-risk-children-final-recommendation` p4.

The two withdrawn documents also contributed rows reading `not stated` — which is why the cell check
seven sweeps ran agreed with the wrong set and the right one alike, and is the transferable finding
here: **a re-derivation that confirms an index cannot confirm a claim about the documents behind it.**
