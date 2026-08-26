# A bound recommendation record is a label and its marker anchor decides which way it reads

[ADR 0007](0007-a-threshold-sheet-is-drafted-per-topic-and-its-snippets-are-gated-against-the-record.md) point 3 gates every snippet against its own recommendation record, refusing on an `exact` source and reporting `NOT RUN` on a `bound` one. It measured the `bound` window on ADA alone — *"min 93, median 157, max 160 characters, and 0 of 126 end in a sentence terminator"* — and read that as an ADA property.

[#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436) established it is every `bound` document in the corpus: not one of the 48 has a record longer than 160 characters, and 97.3% of all 4,618 stop mid-sentence. Grilled on 2026-08-24. The clinician ruled every point below on the same day.

## What the ticket asked and what the tree had already answered

The ticket's decision 1 asks where the 160 comes from. It is a bare inline literal in one slice expression at `tools/guidelines_recs.py:356` — `text[match.start(): match.start() + 160]`. No named constant, and no test in `tools/` pins it.

But the framing question — *does widening it fix the finding* — was overtaken twice before the grilling opened.

**Nothing mechanically refuses a `bound` topic.** `gate_citation_tier0` skips it, `gate_coverage`'s membership refusal is guarded by `if mode == MODE_EXACT`, and the class check is guarded the same way. The truncated text reaches exactly one consumer that acts on it: `tools/threshold_draft.py:234`, which seeds a draft row's `snippet` cell from it.

**`gate_citation_tier2` is not mode-gated.** It grades every row's snippet against the page it cites whatever the mode.

**A bound topic has already shipped.** `reference/thresholds/diabetes.md` merged on 2026-08-23 under [#482](https://github.com/mshamblin5150-code/clinical-skills/issues/482) carrying 357 rows on a `bound` ADA source, with full 377-page accounting, via [ADR 0025](0025-a-section-read-is-the-unit-and-a-sheet-s-page-coverage-is-what-the-state-asserts.md)'s page read and [ADR 0026](0026-a-threshold-row-s-rec-is-a-source-locator-and-narrative-is-a-reserved-kind.md)'s `narrative` locator. Neither touches the marker record. Its `## Scope` declares tier 2 resolved against the real corpus on 2026-08-23, so all 357 rows were graded on the page and passed.

So the question was never *how long should a snippet be*. It was *is this text a snippet at all*.

## What is ruled

1. **A `bound` record's `text` is a label for the recommendation, not a quotable snippet.** Its job is to let a reader tell which recommendation an identifier names. Snippets on a bound source are read off the page, which is what `diabetes.md` already does and what ADR 0025 and ADR 0026 built the machinery for.
2. **On a bound source the drafter emits no snippet.** `tools/threshold_draft.py` leaves the `snippet` cell blank and the label moves to the `Candidate set` table, which is already a table of labels. The seeded-row containment test stops running on bound sources. `exact` sources are untouched — their record text is a real ruled-table cell or a curated USPSTF statement, so seeding and containment both stay.
3. **A label reads from whichever end its marker sits on.** `recommendation` and `practice-point` sit at the start of a recommendation and read forward from the match start, as today. `grade-spelled-out` and `grade-terse` are the GRADE parenthetical at the *end* of one and read backward from the match end.
4. **Both ends back off to a whole word**, and the 160 becomes a named constant with its reason written beside it and a test pinning it.
5. **The window fix and the direction fix land in one build.** They are the same slice expression, and two branches editing one expression in one window is this repo's recorded failure at `anchor_scan` against #150 and at the byte-identical figure git merged in silence.
6. **The changelog shape is declared and censused, never filtered.** `tools/guidelines_recs.py` gains a declared limit naming the ADA front-matter changelog, and an editorial-verb probe runs on every extraction and prints a per-document count into the record metadata and the run summary — explicitly a floor, explicitly never a gate.
7. **`CITATION tier 0 NOT RUN` names the consequence and the count**, not only the mode: the rows keep tier 1 and tier 2 and lose the membership pin to their named recommendation, and their `class` cell is ungraded.
8. **The 46 `blocked on #436` cells in `reference/thresholds/coverage.md` are corrected** to the reason the other 122 rows use. Those topics stay `unread`; only the stated reason changes.
9. **This build does not wait on [#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446) or [#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438).** It declares which of its figures #446 will move.

## What was measured before anything was ruled

All figures below were taken 2026-08-24 against `C:/codeing/guidelines-src`, which is outside this repo, so nothing committed re-derives them. They are re-derivable by command.

**The marker walk reproduces the standing figure exactly, which is what makes the rest of it evidence.** Walking every `TEXT_MARKERS` hit over the 48 bound documents returns **4,618** records, matching [`reference/thresholds/README.md`](../../reference/thresholds/README.md)'s committed table.

**44.5% of the corpus is anchored at the wrong end for a forward read.**

| marker | anchor | records | documents |
| --- | --- | ---: | ---: |
| `practice-point` | leading | 1,944 | 11 |
| `grade-terse` | trailing | 1,197 | 10 |
| `grade-spelled-out` | trailing | 857 | 20 |
| `recommendation` | leading | 620 | 19 |

2,054 records match a trailing marker, so their forward window reads off the end of the recommendation it matched and into the next one. `IDSA/ciu617.pdf` p4 returns recommendation 15's grade followed by recommendation 16's text. Reading backward from the match end returns the recommendation the grade belongs to, checked against a sample from four IDSA documents.

**The mid-word cut is 83% and the repair is nearly free.** Over 12 bound documents and 1,381 records, 1,146 are cut mid-word; backing off to the last whole word costs a median of 5 characters and 40 at worst.

**The ADA illustration is exact and its shipped rows fail containment.** `p261/recommendation/11.8` is 159 characters and ends `...that has been shown to be effec-`; `11.9` is 160 and ends on the literal word `UACR`, one token before the number its row cites. All four of `diabetes.md`'s p261 snippets fail `_normalize` containment against their own records, so re-drafting that sheet today would reject four correct rows and exit 2.

**The changelog shape does not recur.** Probing every leading-marker record for an editorial verb immediately after the reference: 2 documents of 19 have any hit — ADA with 53 and `KDIGO-2017-CKD-MBD` with 1. The other 17 have none. This answers the ticket's second *Done when*.

**That probe is a floor for a reason the ticket got wrong.** ADA has 98 records on pp.12-18 and the probe catches 53. The 45 it misses read `was divided into`, `was broadened`, `was enhanced`, `was amended`, `was moved`, `maintains`, `discusses`, and sub-references like `11.8a` break the anchor. The vocabulary is open. The ticket attributed the floor to truncation cutting the verb; on a leading marker the verb sits immediately after the reference, well inside 160.

**The obvious discriminator is dead.** Treating a reference that appears on more than one page as a changelog entry fires on **271 of the 620** `recommendation` records, almost all KDIGO, where a recommendation legitimately appears in both the executive summary and the body — `KDIGO-2025-ADPKD` alone has 45. Such a rule would refuse correct records.

**The 46 blocked cells and the counter-example landed in the same commit.** `3e722bb` (#482) promoted `diabetes mellitus` to `sheet` on a bound source *and* wrote all 46 `blocked on #436` cells. `tools/threshold_coverage.py` only requires the `record` cell to be non-empty; nothing grades what it says.

## What was rejected

- **Widening the window so a record carries its numbers.** ADR 0026 rule 8 has already ruled that `guidelines_recs.py` gains no second, prose-derived record family, and a window long enough to reach the values edges toward one. It also has a ceiling nothing can lift: the marker walk is per-page, so a recommendation continuing onto the next page cannot be completed by any window.
- **Ending a label at a sentence terminator.** Found within 400 characters for 86.2% of records, median 176 — so it buys little over 160 and needs a second rule for the other 13.8%.
- **Filtering the changelog records out of the count.** The verb vocabulary is open, so filtering drops real recommendations at an unknown rate — [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s failure direction a fifth time, a correct thing refused for a property the rule does not care about. A `bound` count is documented as an over-report and ADA's 126 is inside that contract; a filtered count would be a smaller number that looks exact and is not.
- **Requiring a bound row's `rec` to be present in its record.** A bound record under-reports as well as over-reports — `README.md` says the marker reader can miss a recommendation the document states differently — so a real recommendation can legitimately be absent and the rule would refuse a correct row. This is why `gate_coverage`'s membership guard is `MODE_EXACT` and it stays.
- **Grading the coverage registry's `record` cell.** It is prose stating why a topic sits where it does, and a reason is a reading — `guidelines_catalog.py --draft` leaves `population` blank on the ground that a guessed answer there is worse than a blank one. A check would be either a keyword ban somebody writes around or a claim about ticket state needing the network.
- **Marking the label in the `snippet` column rather than blanking it.** It invents a marker convention one week after ADR 0026 spent a grilling on reserved words in these cells.
- **Sequencing this behind #446.** Both #446 and #438 carry `grilling` and neither is ruled, so a settled ticket would wait on two unsettled ones. The three edit three different functions — `read_marker_recommendations`, `extract`, and the JSON write and read-back — so ADR 0026's one-expression argument does not apply; that argument is for rules sharing one parsed object. And the rebuild cost was priced too high: a `recs-<key>.json` is a build artifact outside every checkout, so rebuilding three times costs CPU rather than a merge.
- **One branch for all three tickets.** It folds a ruled ticket into two that still need grilling sessions and produces one branch rewriting a file three ways.

## Declared limits

**A label is not evidence and no gate may treat it as one.** Point 1 removes the only consumer that read it as a quotation; nothing replaces that with a weaker check, because there is no weaker check available that does not refuse correct rows.

**The changelog census is a floor on the verbs in its list.** It under-counts ADA's own instance 53 to 98, and that belongs printed beside the number. A society adopting a changelog format written in verbs the list does not hold arrives silently, exactly as ADA did.

**The direction rule is a property of the four markers named, not of markers in general.** A fifth marker arrives with no anchor declared, and the build must make that a failure rather than a default.

**Two figures here are measured against pre-[#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446) records and will move when it lands**: the 83% mid-word rate and the median-5-character backoff cost. Rerouting the reader to `rebuild_text` restores missing spaces, so word boundaries become commoner and the backoff loses less — the two compose in the helpful direction, and this fix cannot be made wrong by that one. The marker-anchor split is a count of which pattern matched and is spacing-independent, so #446 cannot move it.

**Correcting the 46 registry cells asserts nothing about those topics being ready.** They stay `unread`. What changes is only that the stated reason stops naming a blocker that measurement shows does not exist.
