# A threshold row's rec is a source locator and narrative is a reserved kind

[ADR 0007](0007-a-threshold-sheet-is-drafted-per-topic-and-its-snippets-are-gated-against-the-record.md) point 3 gates every snippet against its own recommendation record — refusing on an `exact` source, reporting `NOT RUN` on a `bound` one. [ADR 0009](0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md) point 2 says the opposite thing about the same document: **the document is the population and a recommendation record is only an index into it.**

[#464](https://github.com/mshamblin5150-code/clinical-skills/issues/464) is where those two meet. A USPSTF recommendation statement puts a decision point in *Practice Considerations* — an ever smoker is *commonly defined as smoking 100 or more cigarettes*, which decides whether grade B or grade C applies to a man aged 65 to 75 — and the format has nowhere to put it. Every escape the ticket enumerates fails: an invented identifier is refused by the exact record, attaching the value to a real identifier falsely claims it came from that recommendation, `RENDERED:` does not make the identifier true, and scoping it out leaves the topic unpromotable.

Grilled on 2026-08-24. The clinician ruled every point below on the same day.

## The ticket's premise had already been overtaken, and that reframed the question

`reference/thresholds/diabetes.md` merged to `main` on 2026-08-23 under [#482](https://github.com/mshamblin5150-code/clinical-skills/issues/482) carrying **357 threshold rows. 25 carry an extractor-emitted `rec`. 332 carry `p<page>/narrative/<n>`.** All 332 also carry the literal string `narrative` in the `class` column.

`narrative` is not a `TEXT_MARKERS` name and no code path in `tools/guidelines_recs.py` emits it — a `rec_id` is only ever `p{page}/{slug(table_title)}/{n}`, `p{page}/{slug(topic)}/{n}`, or `p{page}/{marker_name}/{ref}`. And [`reference/thresholds/README.md`](../../reference/thresholds/README.md) says flatly that `rec` **is** the `rec_id` from `guidelines_recs.py`.

Both conventions were undocumented, unruled and ungraded. They survived because ADA is `bound`: `CITATION tier 0` reports `NOT RUN`, and `gate_coverage`'s membership refusal is guarded by `if mode == MODE_EXACT`. The class check is guarded too — `expected = classes.get(row.rec)` then `if expected and ...`, so an identifier absent from the record skips it and the cell becomes free text.

So #464's first decision — *does a threshold row gain a narrative source locator distinct from `rec`* — was not a green field. It was a ratify-or-reverse question about something already in the tree with 332 instances.

## What is ruled

1. **A row's `rec` is a source locator, not necessarily a recommendation identifier.** Its middle segment names the kind. `p227/recommendation/10.5` and `p45/narrative/3` are both well-formed. ADR 0007 point 3 is narrowed rather than overruled: tier 0 still refuses on an exact source, for the rows that claim to come from the record.
2. **`narrative` is a reserved kind**, meaning *not from the recommendation index*. Every other middle segment asserts a recommendation identifier and must be in the loaded record, exactly as today.
3. **The locator's shape is enforced** as `p<digits>/<kind>/<id>`, and **its page prefix must equal the row's `page` column.** A collision guard refuses if a loaded record itself carries `narrative` as a kind segment.
4. **On an exact source, a narrative row whose snippet is a verbatim run inside a recommendation record on the same page refuses.** Tier 0 run backwards, page-scoped.
5. **`class` reserves `narrative` too, bound in both directions.** A narrative locator must carry class `narrative`; a recommendation locator must not.
6. **A row's page must sit in at least one span whose `## Scope` table `read` cell is `yes`** — not `no`, not a dated null marker, not `exempt:`. At least one, never every, because ADR 0025 point 3 permits overlap.
7. **`RENDERED:` on a narrative row is counted and declared, never banned**, and `COVERAGE` prints a qualifier on every run naming narrative rows as outside the recommendation index.
8. **`guidelines_recs.py` gains no second record family.** A prose extractor could only ever be `bound`, which would put a bound record under a source declared `exact` and destroy the one thing the mode decides.

The build stays on #464 rather than moving to a new ticket, because ADR 0025 point 10 names #464 by number.

## What was measured before anything was ruled

**The exact record cannot be discharged by a narrative row, by construction rather than by a new rule.** `gate_coverage` computes `unaccounted = known - {row.rec for row in rows} - set(sheet.scoped_out)`, and a narrative locator is not in `known`, so subtracting it removes nothing. #464's third *Done when* holds without a check being added for it.

**The AAA case needs no other change.** The four recommendation records for `abdom-aortic-aneurysm-screening-final-rs` are all on p1; the ever-smoker definition is on p2 and p3. A row citing p3 subtracts nothing from `known`, and tier 1 and tier 2 both grade it and both pass. Re-derived 2026-08-24 by building the record and reading the pages.

**The negative check's width was chosen by measurement, not by reasoning.** Against `diabetes.md`'s 332 narrative rows, a document-wide containment test fires on **2** and a page-scoped one on **0**. Both of the two are on p224 — chapter narrative restating a blood-pressure goal that a recommendation states on p227 — and both rows are correctly narrative. The wider rule refuses correct rows; the page-scoped rule fires only where the dodge lives, because relabeling a row changes its `rec` cell and leaves its page where it was.

**Banning `RENDERED:` on a narrative row was killed by a measurement.** Of `diabetes.md`'s 34 `RENDERED:` narrative rows, **32 genuinely need the hatch** — welded table cells from drug-interference, insulin-titration and IWGDF risk-category tables. Only 2 would have passed tier 2 anyway. Measured 2026-08-24 against a corpus outside this repo, so nothing committed re-derives it; the 2 unnecessary ones are filed separately.

**There is no closed vocabulary of recommendation kinds to distinguish `narrative` from.** The kind segment for a real recommendation is `slug(table_title)`, and `hypertension.md` alone carries **21 distinct ones**. That is what forces a reserved word rather than a rule keyed on absence from the record.

**One direction of ADR 0025's arithmetic was never run.** `_rows_cited_within_span` has exactly two callers — `gate_schema`, which refuses a span marked `read: yes` holding no rows, and `gate_second_read`. Nothing stopped a row citing a page inside a span its own sheet marks unread.

**`row.rec` is opaque everywhere.** It appears at 11 sites in `tools/threshold_sheet.py` and every one uses it as a dictionary key. Nothing parses its segments, and nothing reconciles its page prefix against the `page` column.

**The second read needs nothing.** `brief()` emits document, span and pages and no sheet content, and `gate_second_read` never touches `row.rec`; pairing is `page` plus the numbers in `value`. A narrative row already pairs like any other, and the recommendation-row gates cannot weaken because there is no locator branch to add one to. #464's fourth decision is a null result.

**Every rule was measured against the whole tree before it was believed.** All seven pass against **all 438 rows in all four committed sheets** — zero shape failures, zero page-pin failures, zero class-bind failures, zero negative-tier-0 failures, zero collision guards, zero span-floor failures. Nothing on `main` moves.

## What was rejected

- **A second column for the narrative locator.** It expresses what the middle segment already expresses, and pays for it with a second parse path and a rewrite of 332 rows.
- **Reversing #482's narrative rows.** It throws away a real read of 377 pages over a naming defect.
- **Narrative meaning *absent from the record*.** A single dropped letter in `p18/white-coat-hypertension-and-maskd/1` would stop being a refusal and silently become a narrative row, exempt from tier 0's substring check and from the class check — which `README.md` calls *the only check here that catches a row pinned to the wrong recommendation.*
- **A richer kind vocabulary.** `table` and `figure` describe 32 of `diabetes.md`'s narrative rows more precisely, but no gate would branch on the distinction and a field nothing consumes goes stale.
- **A narrative count per span in `## Coverage`.** It reads as a denominator and there is none, which asserts exactly the thing #464's second decision forbids claiming.
- **Requiring every covering span to be read.** ADR 0025 point 3 permits overlap explicitly — *the check is coverage, never partition* — so a conjunctive rule would refuse properly cited rows.
- **Splitting the build across tickets.** Seven rules sharing one parsed locator have no seam worth two branches editing `tools/threshold_sheet.py` in one window, which is this repo's recorded failure at `anchor_scan` against #150 and at the byte-identical figure git merged in silence.

## Declared limits

**A narrative row's provenance floor is lower than a recommendation row's, and the qualifier says so rather than closing it.** `RENDERED:` already suspends tier 0, tier 2 and `WATERMARK` on any row, so a `RENDERED:` recommendation row is down to tier 1 for snippet provenance too. What a narrative row loses in addition is the membership pin and the class grade — neither of which validates a snippet. The delta is real and narrower than *provenance-free*, and it is declared rather than gated, on [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s ruling: declare the coverage rather than widen the instrument.

**Nothing enumerates prose.** No denominator exists for how many decision points a document's narrative holds. What bounds a narrative row is the `## Scope` span table and nothing else, and the `COVERAGE` qualifier prints on every run rather than only when it fires, on [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling — a reader who learns to read a qualifier reads its absence as the stronger claim.

**The negative check is page-scoped and therefore reaches only the dodge it was built for.** A row relabeled `narrative` and *moved to a different page* escapes it. The wider rule was measured and refuses correct rows, so this is a chosen floor rather than an oversight.

**The span floor asserts that somebody declared the page read, never that they read it.** It is the same thing ADR 0025 point 7's dated marker asserts, and that record already says the marker records that a read happened, never that it was careful.

**The class bind checks a sentinel, not a grade.** It stops a narrative row carrying a fabricated grade and stops the sentinel muting a real one. It says nothing about whether a recommendation row's grade is the right grade — that remains `gate_coverage`'s existing check against the record.

**A reserved word in two columns is a bet about the corpus.** No society in the corpus grades a recommendation with the literal word `narrative`, and the collision guard refuses the locator side loudly if one ever does. The class side is covered by the same guard rather than a second one.

## Consequences

ADR 0025 point 10's sequencing dependency is discharged when this record's build lands, not when the record is ratified. Until then [#479](https://github.com/mshamblin5150-code/clinical-skills/issues/479), [#480](https://github.com/mshamblin5150-code/clinical-skills/issues/480) and [#481](https://github.com/mshamblin5150-code/clinical-skills/issues/481) keep the half-block point 10 gave them: a span holding nothing may be retired, a span yielding a narrative row waits.

ADR 0007 point 3 keeps its text with a forward pointer rather than being amended, on ADR 0025's arrangement with ADR 0009 point 5 and for its reason: the collision was not known on the day it was ruled, and rewriting the sentence would make the original ruling look wider than it was.

`reference/thresholds/README.md`'s `rec` specification is rewritten by the build, and `diabetes.md`'s 332 rows become documented rather than tolerated.
