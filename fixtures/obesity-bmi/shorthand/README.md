# obesity-bmi — inputs

Four encounters, one file each, transcribed from the day-file text. These are the **inputs** half of the set: feed one to `clinical-note` on the SOAP branch and check the output against [assertions.md](../assertions.md).

Read from the day file, never from a prior run's output. That is the whole point — see [fixtures/README](../README.md).

## This set is not a shift, and the numbering says so

`day-a` and `day-b` are whole shifts. `peds-bp` is part of one, and keeps that shift's numbering so the gaps show what was left out. **This set is neither.** Its four encounters come from **three different day files** — two clinic days and one backlog — because the shape it needs is rare and no single day holds two of them.

So the cases are renumbered `01`–`04` and the `Note <n>` line inside each file is renumbered to match. There is no shift numbering to preserve, and keeping four unrelated source indices would imply an order the set does not have.

**They are recoverable without a mapping.** `tools/corpus_census.py` carries the markers that found them — `OBESITY`, `BARIATRIC`, `has_body_measurement` — so a reference read starts by re-running the census rather than by trusting a note-to-file table written here. Which day file each case came from is deliberately not recorded: file names carry the visit date and the preceptor.

## The shape the set is built on

**All four carry no vital and no body measurement at all** — no blood pressure, no pulse, no temperature, no respiratory rate, no oxygen saturation, **no height and no weight**. That is day-b's dominant shape, and it is what makes the BMI wholly generated: there is no given input for the arithmetic to rest on.

What day-b cannot supply is the other half of the pair. Measured 2026-08-11 across 559 encounters with `tools/corpus_census.py`:

| | any | with no height and no weight |
| --- | --- | --- |
| obesity written in the note | 2 | **2** |
| bariatric surgery in the history | 4 | **2** |
| sleep apnea or CPAP | 8 | 1 |

Those first two rows are this set. **Both encounters in the whole corpus that write the word are here**, which is why the set is four cases and not forty — it is not a sample, it is the population.

**Cases 1 and 2 are the anchors.** The shorthand says the patient is obese and supplies nothing to compute a BMI from, so a generated BMI below 30 contradicts a given.

**Cases 3 and 4 are the controls.** A history of lap band surgery or gastric bypass documents a *past* obesity and says nothing about the present one — which makes them the place a sub-30 BMI is both plausible and accountable. Without them the set could not tell a skill that reasons from one that writes "obese" every time. They are day-b case 2's job, transposed: in-corpus proof that the passing form is writable.

## What was changed on the way across

Everything else is verbatim, typos included. `shere roprts`, `utrasounds`, `estabilish`, `restlessleg`, `deficency`, `reviewd` and case 4's missing comma after `deficiency` are all preserved as written. Never repair one here; that hides the defect the set is meant to find.

| Substitution | Why |
| --- | --- |
| `[PT]` | Patient name. Standing rule 1. |
| `[DR]` | A named physician case 1 says has retired. Named provider plus age plus a small county narrows the population the way the site name does. What mattered clinically — that prior care was with someone no longer reachable — survives. |
| `[SITE]` | Named outside facilities: four in case 1, one in case 2, one in case 4. Case 1's four are **four separate tokens on purpose** — that her records are scattered across that many places is the entire reason for the visit's plan. |
| `[DATE]` | Case 4's scheduled procedure date. A fixed calendar day plus `rtc 1 week prior` reconstructs the visit to within a week, which is the visit date arriving by the back door — the same reasoning behind `peds-bp`'s `[HOLIDAY]`. The interval survives; only the anchor goes. |
| `62 f` | Case 2's source gives a date of birth and no age. [fixtures/README](../README.md) requires the age be **derived before** the date is stripped, or the case silently becomes a missing-age test. See the caveat below. |

No visit date is removed from cases 1, 3 and 4, because none is written down. Every remaining date-shaped token is a pain score (`9/10`), heart sounds (`2/2`), a dose (`150 mg`) or a duration (`3 weeks later`).

### Case 2's age is derived and carries ±1 year

Its source is a **backlog** file — notes written up some time after the encounters — so the only date bounding the visit is the file's own, and that is an upper bound rather than the visit date. The derived age is therefore 62 or 61.

**No row in this set turns on it.** O1 asks for a plausible-for-age fill and O2 for consistency with a documented obesity; neither reads differently at 61. It is recorded because a fixture that quietly rounds an age it could not really compute is the kind of thing that gets quoted back as a measurement later.

## What was left out, and why

**The one sleep-apnea encounter with no body measurement.** OSA associates with obesity strongly and entails it not at all — a lean patient with OSA is ordinary — so a row anchored on it would demand a BMI the shorthand never documented. That is an invented abnormal finding, which standing rule 2 forbids outright, and it is the same test [issue #15](https://github.com/mshamblin5150-code/clinical-skills/issues/15) already applied to rule diabetes out as an anchor.

It is named here rather than silently dropped, on `peds-bp`'s terms: a set scoped to part of what it could have covered says what it left out.

## Do not add measurements to these files

An input that already supplies a height or a weight cannot test whether the skill fills them, and cannot test what it does with the BMI it derived — which is the entire set. The same rule day-b states about vitals applies here with one extra edge: **a weight alone would be enough to void it**, because a given weight plus a filled height makes the BMI partly real, and every row below is about a number that is wholly invented.
