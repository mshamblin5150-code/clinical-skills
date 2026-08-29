# A threshold sheet's sources are not joined to its topic because the catalog cell is the guideline's wording

[#645](https://github.com/mshamblin5150-code/clinical-skills/issues/645) was filed out of
[ADR 0063](0063-a-draft-backed-citation-is-caught-per-row-by-the-parser-the-module-already-shares-and-the-class-set-is-draft-alone.md)'s
Consequences: a threshold sheet may declare a source from another topic, and nothing joins its
`## Sources` table to its own `coverage.md` registry row. Grilled 2026-08-29 against `origin/main`
at `d9890e3`. **Four decisions, all the clinician's, all on that date.** Nothing is built here; this
is the record the build reads.

The ticket poses three decisions. The measurement retires all three by falsifying the instrument
they are all keyed on, and the fourth decision here is the vocabulary defect that produced the
ticket in the first place.

## Measured before ruling, at `d9890e3`

**The catalog's `topic` column holds no `?` cells.** The ticket says the column is curated *"with 43
`?` cells in the file today"* and rules out *"a check that reads the catalog's `?` cells as an
answer"* on that ground. The 43 are the file's total across every column: **population 36, year 5,
title 2, topic 0.** That prohibition names a real hazard in the `population` column and does not
reach this one.

**The four shipped sheets all cite sources their own topic owns.** Re-derived over all five source
rows: `cervical-cancer.md`/`cervical cancer screening`, `diabetes.md`/`diabetes mellitus`,
`hypertension.md`/`high blood pressure`, and both of
`prediabetes-type-2-diabetes-screening.md`/`prediabetes and type 2 diabetes screening`. The ticket's
claim that the clean path has real material is true.

**The topic column is per document, not per condition.** 179 rows, 169 distinct topics: **160 own
exactly one document, 8 own two, 1 owns three.** High blood pressure alone is four cells across four
documents — `high blood pressure` (AHA/ACC 2025), `hypertension screening` (USPSTF 2021, adults),
`high blood pressure screening` (USPSTF 2020, children) and `blood pressure in chronic kidney
disease` (KDIGO 2021). COPD is two — `chronic obstructive pulmonary disease` (GOLD) and `COPD
screening` (USPSTF).

**`threshold_draft.py` already performs this join, at draft time and in the useful direction.**
`:196` seeds a sheet with the requested topic's rows only, and `:198-209` prints a rejected list of
near-miss documents as `"<society>/<file>: catalog topic is 'X', not 'Y'"`. Its `TOPIC_ALIASES`
comment states the distinction this record rules on: *"The catalog uses the guideline's wording
while the clinician names the clinical topic."*

**That near-miss report is keyed on the typed string, so which siblings surface depends on which
name was typed.** Measured: drafting `hypertension` surfaces `hypertension screening` and not `high
blood pressure screening`; drafting `high blood pressure` surfaces `high blood pressure screening`
and not `hypertension screening`. `hypertension.md` is registered under `high blood pressure`, so
the name it is actually drafted under is the one that never surfaces the USPSTF adult statement —
its most likely second source.

## What is ruled

1. **A source from another catalog topic is not a defect, and no gate is keyed on the topic
   column.** The column cannot see the difference the ticket was filed about, in either direction. A
   correct citation is refused: `hypertension.md` gaining the USPSTF adult hypertension screening
   interval is a different catalog topic and is the right thing to have done, and with 160 of 169
   topics owning one document, nearly every second source any sheet ever gains is cross-topic. A
   wrong citation is not caught: `hypertension.md` citing the ADA diabetes standards is *also*
   merely `!= 'high blood pressure'`, indistinguishable from the correct case. **A report fails for
   the same reason as a refusal** — it fires on the normal case, which is
   [#164](https://github.com/mshamblin5150-code/clinical-skills/issues/164)'s declared floor with no
   reader. #645's decisions 2 and 3 fall with it.
2. **The limit is declared as a sixth bullet on the list that already exists**, in
   `tools/threshold_sheet.py`'s docstring under *"What no gate here reaches, stated the same day the
   gates were built"*, immediately after the wrong-heading bullet it is the neighbor of, with the
   sheet README's matching bullet saying the same thing or pointing at it, and a test that fails if
   the sentence goes missing. **It does not start a declared-limits object**, because
   [#550](https://github.com/mshamblin5150-code/clinical-skills/issues/550) owns the shape question
   for this module and is open and unruled. A sixth bullet on an existing list is shape-neutral
   under every ruling #550 can make: absorbed with the other five, or made a pointer with them. A
   new object would decide #550's decision 1 in passing, and blocking would leave the module silent
   about a ruled hole for an open-ended wait.
3. **The drafter's near-miss report is a separate ticket, filed `grilling`.** It is the one thing
   here that is measurably broken and cheap, and it fires while the author is choosing sources
   rather than at grade time when the decision is already made. **A reader attestation on each
   `## Sources` row was refused**: it would be demanded on nearly every second source a sheet ever
   gains, and anyone can type it, so it buys a keystroke rather than a reading. The mechanism is
   unruled — widening `TOPIC_ALIASES` is a hand-kept synonym list, and reporting any topic sharing a
   significant word is a cut point nobody can ground,
   [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s objection — so it is not
   `ready-for-agent`.
4. **`topic` is two terms and `CONTEXT.md` names them apart.** The glossary entry stays the clinical
   subject, and a second entry names the catalog cell. Rewriting the existing entry to mean the cell
   would silently change what every ratified sentence using the word claims —
   [#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429)'s *"the unit is the
   topic, not the document"* means the clinical sense. **Nothing in this repo derives which catalog
   cells are one clinical topic**, and that is the sentence ruling 1 rests on.

## Consequences

The declared limit is the only thing standing between the sheet gates and a reader's assumption that
they check source membership. Its honest form has three limbs: no gate checks it; `threshold_draft`
reports near-miss documents at draft time only, and only where the typed topic words appear in the
other row's topic or title; and a source added to a sheet after drafting, or one from an unrelated
topic, is surfaced by nothing.

`TOPIC_ALIASES` is the only bridge between the two senses of `topic` that exists, it holds one entry,
and it is one-way. Every population counted per catalog topic — the 169-row registry, the sweep's
denominator, the drafter's seed set — is counted in the cell sense. Nothing counts in the clinical
sense, and no committed artifact records which cells belong together.

ADR 0063's Consequences paragraph filing #645 is **factually correct and is not corrected**. It
states that nothing binds a sheet's `## Sources` documents to its own topic's catalog documents, and
that remains true — ruling 1 is that the absence is deliberate rather than a gap. It gains a dated
line recording that disposition under
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms, its deciding paragraphs untouched, so that the sentence calling it *a finding* does not read
as an open one. **The `?`-cell premise is #645's body alone**, and is patched there. A first draft of
this record placed it in ADR 0063 as well, which is a claim wider than the measurement behind it —
the defect this record's own ruling 1 turns on.

## What must not come out of this

**A second attempt at the same join through a different column.** Society, year and class are all
blind to condition in the same way the topic cell is; the reason the join fails is that no committed
artifact groups catalog cells by clinical subject, not that the wrong column was chosen.

**A derived grouping of catalog cells.** Any rule that decides `hypertension screening` and `high
blood pressure` are one subject is a similarity judgment over society-written wording, which is what
`guidelines_index.py` refuses embeddings for by name: *"a fuzzy match can return the right concept
from the wrong society, wrong year or wrong population with a citation attached."* If the grouping
is ever wanted it is authored and committed, not inferred.

**Widening `load_catalog_page_counts`.** #645's own prohibition and it survives: it answers what the
catalog says a document's page count is, and making it also answer whether the document belongs is
two questions in one read.

**Reading the drafter's rejected list as coverage.** It is a floor bounded by string overlap with
the name that was typed, and ruling 3's ticket exists because that floor is lower than it reads.
