# day-b — inputs

Twelve encounters, one file each, transcribed from the day-file text. These are the **inputs** half of the set: feed one to `clinical-note` on the SOAP branch and check the output against [assertions.md](../assertions.md).

Read from the day file, never from a prior run's output. That is the whole point — see [fixtures/README](../README.md).

## What was changed on the way across

Everything else is verbatim, typos included. The shorthand is typo-ridden by nature and the skill has to handle it, so `infecgion`, `lypmadenopathy`, `wt 62in wt 131` and `abcess cutanius cellulit` are all preserved as written. Never repair one here; that hides the defect the set is meant to find.

| Substitution | Why |
| --- | --- |
| `[PT]` | Patient name. Standing rule 1. |
| `[DR]` | A named referral physician in case 11. A specialist by name plus a small county narrows the site as sharply as the site name would — the same reasoning that removes it. Nothing clinical is lost; what mattered was that follow-up is with a specific outside provider on a named day, and both survive. |

No visit date is removed, because none is written down. Every date-shaped token in these twelve is a pain score (`8/10`), heart sounds (`2/2`) or a duration (`3-4 days`); the relative days that do appear (`saturday`, `thursday`, `yesterday`) are clinical content and stay. Case 2's `1209` is a clock time, not a date.

The source is a single **text** file in `scratch/day-file-text/`, gitignored, holding **12 encounters** delimited by `Note <n>` lines whose capitalization varies (`Note 1`, `NOte 2`, `noTE 5`) and is preserved. Unlike day-a's source it has a text layer, so these were read directly rather than rendered and read visually. Its filename carries the visit date and the preceptor, so — as in day-a — it is named here by location rather than quoted.

## Nine of the twelve carry no vitals at all

This is the reason the set exists, so it is worth stating flatly: **cases 1, 5, 6, 7, 8, 9, 10, 11 and 12 have no blood pressure, no pulse, no temperature, no respiratory rate, no oxygen saturation, no height and no weight.** Not a partial set — nothing.

That is a genuine property of the source, not a transcription loss and not a redaction. It is the corpus-wide pattern in miniature. Measured 2026-08-11 across 551 encounters with `tools/corpus_census.py`:

| | |
| --- | --- |
| no vital at all | 256 — 46% |
| at least one vital | 295 |
| … of those, a complete set | 201 — 68% |
| … of those, partial | 94 — 32% |

So the vital line tends to be written whole or not at all, and this shift is the pattern concentrated: nine written not at all, three written whole, none partial. It is a tendency rather than a rule — a third of the encounters that carry anything carry only some of it — and day-b tests the two ends, not the middle.

**Do not add vitals to these files.** An input that already supplies the value cannot test whether the skill fills it, which is the same reasoning that keeps day-a case 10's age out of its input file.

## Cases 2, 3 and 4 are the control

These three carry a full vital line. They are here to test the other direction of the same license — that a **given** value survives unchanged and nothing is filled over it. Without them the set could not tell a skill that fills correctly from one that fills always.

Case 3's `bp 147/81` is a given abnormal, and it is now **drift row D1** — the submitted note recorded it and stopped. Case 2's `wt 62in` is a **height**, settled by the same reference read, so B4 covers it. Both in [assertions.md](../assertions.md).
