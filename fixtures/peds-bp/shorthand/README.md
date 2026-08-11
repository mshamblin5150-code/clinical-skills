# peds-bp — inputs

Five encounters, one file each, transcribed from the day-file text. These are the **inputs** half of the set: feed one to `clinical-note` on the SOAP branch and check the output against [assertions.md](../assertions.md).

Read from the day file, never from a prior run's output. That is the whole point — see [fixtures/README](../README.md).

## The numbering has gaps, and that is the point

These are notes **2, 3, 5, 8 and 9** of a ten-encounter shift, and the filenames keep the shift's numbering rather than being renumbered `01`–`05`. The gaps are the five encounters left out, and leaving them visible is cheaper than a sentence explaining that some were.

**What was left out, and why it matters more than what was kept.** Notes 1, 4, 6 and 7 are 7, 9, 9 and 8 years old. **All four carry a blood pressure.** Note 10 is 28 and carries none.

So within a single shift, on a single day, in one clinician's hand:

| | |
| --- | --- |
| every child 7 and over | pressure recorded — 4 of 4 |
| every child 5 and under | no pressure recorded — 0 of 5 |

That contrast is the reason this shift was chosen over the other ten that carry an under-6 encounter. It is also why the four school-age controls are **named here but not extracted**: this set exists to test what the skill does with the missing half, and a set is scoped to its question ([issue #11](https://github.com/mshamblin5150-code/clinical-skills/issues/11)).

## What was changed on the way across

Everything else is verbatim, typos included — `intollaerance`, `surgiccal`, `autisim`, `phayrngitis`, `brith to 3 servies` and case 2's `she … gave him tylenol` are all preserved as written. Never repair one here; that hides the defect the set is meant to find.

| Substitution | Why |
| --- | --- |
| `[PT]` | Patient name. Standing rule 1. |
| `[HOLIDAY]` | A named holiday case 5 gives as the symptom onset. On its own it is clinical content, but this set states its year, and a fixed annual date plus `cough x 1 month` reconstructs the visit to within a week or two — which is the visit date arriving by the back door. The duration survives; only the anchor goes. |

**The visit date and the site are removed**, per [fixtures/README](../README.md) — the source day file carries both, and the site name also appears once inside the shift as a stray line between encounters. Neither is clinical.

**A holiday is a date.** Case 5's onset anchor was kept in the first draft of this set on the grounds that it is patient-reported content rather than the visit date. That reasoning is circular: `cough x 1 month` is the multiplier and the holiday is the anchor it was missing, and *Status* below states the year. Together they land the visit inside a fortnight. It is redacted for the same reason the visit date is.

The source is a single **text** file in `scratch/day-file-text/`, gitignored, holding **10 encounters** delimited by `Note <n>` lines. Its filename carries the visit date and the preceptor, so it is named here by location rather than quoted.

## Two of the five carry a partial vital line, three carry nothing

This split is the set's whole subject, so it is worth stating flatly:

| Case | Age | Vital line |
| --- | --- | --- |
| 2 | 5 y | none |
| 3 | 2 y | `hr 125 t 98 rr 24 spo2 95% 38in wt 46` — **no blood pressure** |
| 5 | 11 mo | `HR 113 T 98.0 axillary rr 26 Spo2 94%, wt 21 lbs` — **no blood pressure**, no height |
| 8 | 5 y | a temperature only — `temp this vist is 99.5`, inside the exam prose |
| 9 | 9 mo | none |

Cases 3 and 5 are the ones that matter. day-b's inputs are the corpus's dominant shape — a vital line written whole or not at all — and the ticket that opened this set assumed that shape held everywhere. **It does not hold under 6.** Measured 2026-08-11 with the extractors in `tools/corpus_census.py`, over the same 559 encounters:

| band | n | no pressure | … of those, carrying **no vital at all** | … of those, carrying **a vital line without one** |
| --- | --- | --- | --- | --- |
| 0–5 | 21 | 21 | 3 | **18** |
| 20+ | 256 | 106 | 95 | 11 |

Under 6 the pressure is the *only* thing missing, six times in seven. Over 20 the whole line is missing, nine times in ten. That inversion is what case 3 and case 5 put in front of the skill.

**Both denominators are floors, and the table would mislead without this.** The census reads an age from 357 of the 559 encounters; the other 202 state none in a form it recognizes. So *21 encounters under 6* is what it can see, not what exists — and 21 of those unreadable encounters do carry a vital line with no pressure, some of which are very likely small children. The **ratio** is what the argument rests on and it is untouched. The **counts** are not the corpus's pediatric population.

**Do not add a blood pressure to these files.** An input that already supplies the value cannot test whether the skill fills it — the same reasoning that keeps day-a case 10's age out of its input file.

## Case 3 is the anchor case

`weight 99.9th percentile height 59th percentil` is **given**, written by the clinician, alongside a given height of 38 inches and a given weight of 46 pounds. So case 3 is the one encounter in this repo where a small child's filled blood pressure has a documented, non-generated anchor pulling it off the middle of the range — and where a run that fills a bland mid-normal value can be shown to have ignored something that was right there in the shorthand.
