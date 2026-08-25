# The marker limb reads the repaired text, the other two limbs declare that they do not, and every citation gate reads one reader

[#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446) was filed because
`tools/guidelines_recs.py` builds every recommendation record through a raw PyMuPDF read, and
`rebuild_text` — the function [#83](https://github.com/mshamblin5150-code/clinical-skills/issues/83),
[#178](https://github.com/mshamblin5150-code/clinical-skills/issues/178) and
[#172](https://github.com/mshamblin5150-code/clinical-skills/issues/172) exist to get right —
appears nowhere in it. The ticket's charge was that `CITATION tier 0` cannot see the consequence,
because both sides of that comparison come from the same reader and a glued run agrees with itself.

Grilled 2026-08-25. **Four decisions, ruled by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## The measurement came first, and it moved the ruling twice

**Round one recommended the gate and was wrong, on evidence taken from one document.** ADA is this
ticket's own worked example and the corpus's worst non-USPSTF document for glued runs, and rerouting
its marker limb produces **byte-identical records** — 126 records, 116 identifiers, zero text
differences. On that evidence the reroute buys nothing and the honest answer is
[#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s: declare the coverage.

**The corpus-wide run falsified it.** ADA is not representative. Across all 48 bound documents the
reroute changes 144 record texts in 25 of them, removes every glued record, and **recovers a
recommendation the raw reader cannot see at all.** That is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s shape — a generalization
made from the files the pass had open — arriving inside the grilling of a ticket whose own subject
is an instrument that cannot see what it is measuring.

**The recovered record is the whole ruling.** `IDSA/taplitz-et-al-2018`, page 3:

```
get_text:  ...moderate).\nRecommendation3.3Yearlyinfluenzavaccinationwithinactivatedvaccineisrecomme
rebuild:   ...moderate).\nRecommendation 3.3 Yearly influenza vaccination with inactivated vaccine is
```

The marker pattern needs `Recommendation 3.3` and the line is welded, so **Recommendation 3.3 is
absent from the record set entirely** and that document reports 9 recommendations where it states 10.
Two further records on the same page carry welded prose in their text.

**An omission is invisible to every gate over the output.** A check scanning record text for welded
runs flags 3.1 and 4.1 on that page and cannot flag 3.3, because there is no record there to scan.
The only check that sees a missing record is one that reads both readers and compares — and a check
that has already paid for both readers is more expensive than the repair it declines to make. That,
and not the 144, is why the gate answer does not hold for this limb.

## The dated figures the ruling rests on

Measured 2026-08-25 at `0c39452`, against the live corpus. **Dated evidence and not live figures**:
the corpus is outside every checkout, so nothing committed re-derives any of them and the next
refresh moves all of them. The build re-derives them by command rather than citing this table.

| limb | docs | records | what the repaired reader changes |
| --- | ---: | ---: | --- |
| curated verification | 90 | 143 | **nothing by construction** — verification folds to letters and digits |
| ruled table | 22 | 2,969 | **nothing measured** — one long run in 2,969, `esophagogastroduodenoscopy`, a real word |
| text marker | 48 | 4,618 → **4,619** | 144 record texts in 25 documents; 6 glued records to 0; one recommendation recovered |

The document and record counts reproduce
[`reference/thresholds/README.md`](../../reference/thresholds/README.md)'s committed table exactly,
which is the check that the measurement read the population the tree already names.

Cost, same date: `get_text("text")` over ADA's 377 pages is **1.7 s**; `rawdict` plus operator
classification plus `rebuild_text` over the same pages is **11.1 s**, a factor of **6.4**. The
corpus-wide comparison run, which reads every non-curated document twice and runs the table pass as
well, took **2,293 s**.

## Ruling 1 — the marker limb reads `rebuild_text`; the other two do not

`extract`'s marker read moves onto the repaired text, with `rendered_operator_map_for_page` threaded
through so [#172](https://github.com/mshamblin5150-code/clinical-skills/issues/172)'s operator repair
applies. The curated and ruled-table limbs are untouched.

**The three limbs get different answers, which the ticket predicted and the measurement confirmed.**
Curated verification folds to letters and digits before comparing, so spacing is already invisible to
it and rerouting would change no verdict; the USPSTF row text a sheet actually cites comes from
[`reference/guidelines-uspstf.md`](../../reference/guidelines-uspstf.md), built by `uspstf_table.py`
from the extracted `.txt`, which already carries the repair. The ruled-table limb measured clean over
2,969 records and is the limb where the repair is hardest to build — `table.extract()` returns
strings rather than glyph boxes — so it is the one place where paying that cost buys nothing measured.

**This is not a retreat from
[#275](https://github.com/mshamblin5150-code/clinical-skills/issues/275)'s refinement, it is that
refinement applied.** *Declare the limit you are keeping, and fix the thing you actually named.* What
is actually named, once the corpus is read rather than one document, is a dropped recommendation.

## Ruling 2 — the two unrepaired limbs are a declared limit, and a census stands behind it

A named object in `tools/guidelines_recs.py` states which limbs skip the space reconstruction and
what that costs. Prose points at it and copies no row of it, on
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s terms.

**A declaration alone was refused, on
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s ground**: a prose edit to
a limit fails nothing, so a limit written as prose goes stale in the direction nobody notices. A
glued-run census runs at record build time over **all three limbs**, counts per document into the
record JSON, and prints on every run — `symbol_glyph_census`'s arrangement and its reason, that a
refresh should leave a diff somebody has to look at rather than a silence somebody has to think of.

**It reports and never refuses.** The instrument has a real false positive in the corpus today:
over 2,969 ruled-table records it returns exactly one hit, and that hit is a genuine 26-letter word.
A check that fails on `esophagogastroduodenoscopy` is one people learn to route around, and these
records are a build artifact rather than a shipped one.

**The census keys on a floor and the floor is declared beside whichever instrument is chosen.** A
length threshold is a value named at an edge, which is `SPACE_ADVANCE_FRACTION`'s recorded failure;
`split_census.harvest_lexicon` already builds a word list out of the corpus's own real space glyphs,
so a welded run can be recognized as *decomposes into two corpus words* rather than as *is long*.
Either is acceptable. Neither may be presented as complete: a weld of two short words is invisible to
the first and a weld of two words the lexicon lacks is invisible to the second.

## Ruling 3 — `CITATION tier 2` reads the same reader as the records

`tools/threshold_sheet.py`'s tier-2 page cache moves onto `rebuild_text`.

**This is forced by ruling 1 rather than chosen beside it.** Leave tier 2 raw and the repair becomes
a false-alarm generator: `_normalize` flattens whitespace runs but does not remove them, so a snippet
lifted from a repaired record cannot match a welded page. Measured on the taplitz page — *"induction
therapy should receive prophylaxis with a nucleoside analog"* is **not found** in tier 2's raw page
text and **is found** in the repaired one. Nothing shipped is hit today, because the only shipped
bound sheet is ADA and ADA's records do not move; the 144 repaired records across 25 documents are
waiting for [#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429)'s sweep to reach
them.

**One reader everywhere is the property being bought.** A drafter writes a snippet from one of two
places — the record, which after ruling 1 is repaired, or the rendered page, which the typesetter
spaced correctly. `rebuild_text` approximates the rendered page and so matches both; the raw reader
reliably matches neither. Accepting a match under *either* reader was priced and declined: it never
refuses a correct row, and it lets a welded snippet pass, which is a gate that reads as agreement.

**Tier 0 stays a tautology on spacing and that is declared, not fixed.** After ruling 1 both of its
sides come from `rebuild_text`, so the shared-reader blindness the ticket's title names survives the
repair. **The hole is wider than the title claims**: on a `bound` source tier 0 is `NOT RUN`
entirely, so `diabetes.md`'s rows are gated by tier 2 alone, and the declaration says so.

## Ruling 4 — this lands before #438 and #436, and #429 keeps sweeping the clean documents

Order: **#446, then [#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438), then
[#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436)**.

[ADR 0030](0030-a-recommendation-record-is-owned-like-every-other-artifact-its-trust-floor-is-keyed-on-the-limb-that-built-it-and-the-drafter-takes-no-escape-hatch.md)'s
Consequences reads *"#446 edits ruling 2's tuple … invalidating everything stamped here."* **That is
true only if #438 lands first.** `artifact_provenance.TRUST_FLOOR` today carries `index` and
`extraction` and no `recs` key, so #438 is ruled and unbuilt. Land this first and there is nothing
stamped to invalidate: #438's build writes `tools/guidelines_extract.py` into the recs floor from the
start, because by then the marker limb reads through it. One rebuild instead of two, and one file
writes that tuple once.

Same argument for #436, whose headline figure — the 83.0% mid-word cut rate — was measured on
damaged text. Grilling it after this lands measures the text that will exist rather than the text
being replaced.

**#429 is not blocked.** The exposed population is measured and narrow: 25 of 48 bound documents
carry a record that moves, and 121 of the 169 registry topics sit on documents measured clean.
Blocking the whole sweep costs its momentum and buys nothing. The sweep holds only topics whose
source is one of the affected bound documents, and that set is enumerable by command rather than
by this record.

## Consequences

- **Every stamped recommendation record is rebuilt**, once, by this build. That is CPU rather than a
  merge: a `recs-<key>.json` is a build artifact outside every checkout.
- **`reference/thresholds/README.md`'s committed table moves** — the bound row's record count goes
  from 4,618 to 4,619 — and the rebuild is not finished until that artifact is re-derived. That is
  [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s rule: a change to a
  producer is not finished until the artifact it feeds is rebuilt.
- **#436's two measurements move in the helpful direction.** Restoring spaces makes word boundaries
  commoner, so the mid-word cut rate falls and the backoff loses less. The marker-anchor split is a
  count of which pattern matched and is spacing-independent, so it does not move.
- **#438's spec gains a line** rather than this ticket editing its tuple: the recs trust floor
  includes `tools/guidelines_extract.py`.
- **A sheet drafted from one of the 25 affected documents before this lands may need re-drafting**,
  because its snippet was copied out of a damaged record and tier 2 will change reader underneath it.

## What this does not reach

- **Whether a snippet is the *right* text.** Every gate here is a provenance floor. A row whose
  numbers are real and whose heading is wrong passes all of them, which is the threshold directory's
  standing residue and stays there.
- **`rebuild_text` is a reconstruction and not ground truth.** Four distinct non-header glued runs
  survive it on ADA. It is better than the raw reader by measurement, not perfect.
- **The census instrument is a floor**, whichever of the two forms it takes. A numerator and a
  denominator built from the same matcher can agree while both omit a member.
- **The ruled-table limb's clean reading is dated.** It says the 22 documents in the corpus on
  2026-08-25 carry no damage this instrument can see; it says nothing about the next document a
  society publishes. The census is what makes that visible rather than the declaration.
- **Tier 0's shared-reader blindness survives**, by ruling rather than by oversight.
