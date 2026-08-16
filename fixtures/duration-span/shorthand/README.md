# duration-span — inputs

Three encounters, one file each, transcribed from the day-file text. These are the **inputs** half of the set: feed one to `clinical-note` on the SOAP branch and check the output against [assertions.md](../assertions.md).

Read from the day file, never from a prior run's output. That is the whole point — see [fixtures/README](../README.md).

## What the set is for

[Drift row 16](../../skills/clinical-note/SKILL.md) — *a duration belongs to what it is written next to* — has two limbs, and only one of them was ever fixtured.

The **attribution** limb is `day-b`'s B10 and B11: a duration hangs off a multi-symptom chief complaint and a later onset statement dates a *different* symptom, so there is no contradiction and nothing to resolve. The second limb is this set:

> **It is a conflict only when the same symptom carries two numbers** — `cough x 5 days` against `cough started 2 days ago`. **A genuine conflict is written as a span containing both.** `Duration within the past 1 to 2 days`, never one endpoint chosen over the other.

**None of `day-b`'s twelve carries that shape**, and that set's own file said so and named the gap as owed: cases 8 and 9 date a different symptom, cases 4 and 12 restate a timeline and agree with themselves, and the other eight state one timeline or none. So the limb shipped stated in `clinical-note` and unfixtured — a run that met a same-symptom conflict and picked the shorter number would have passed every row in this repo. [#65](https://github.com/mshamblin5150-code/clinical-skills/issues/65).

## This set is not a shift, and the numbering says so

`day-a` and `day-b` are whole shifts. `peds-bp` is part of one, and keeps that shift's numbering so the gaps show what was left out. **This set is neither.** Its three encounters come from **three different day files**, because a symptom dated two ways is not something a single shift reliably holds two of.

So the cases are renumbered `01`–`03` and the `Note <n>` line inside each file is renumbered to match. Which day file each came from is deliberately not recorded: file names carry the visit date and the preceptor.

## It is a pick, not a population, and that is stated rather than hidden

`obesity-bmi` clears [fixtures/README](../README.md)'s recomputability bar by being the **whole** of a shape a machine finds four times. **This set cannot do that, and the reason is the rule itself.** Row 16 turns on whether two durations are about the *same symptom*, and deciding that is reading rather than matching — the second statement may name its symptom, may use a pronoun, and may or may not carry the new-or-worse marker that redirects the pronoun to a newer complaint. No regex makes that call, so no filter can return the population.

`hedged-dx` is the precedent, and the arrangement is its: publish the pool, and say the pick was a judgment. Measured 2026-08-15 across 551 encounters with `tools/corpus_census.py`:

| | n | share |
| --- | --- | --- |
| **two different durations sharing a symptom** | **43** | **8%** |

Three of those forty-three are here, chosen by reading all forty-three. **What is recomputable is the pool, not the pick.** The whole pool sorts as follows, and *What was left out* below says what each rejection rests on:

| | n |
| --- | --- |
| the two durations are not about one symptom — the **attribution** limb | 20 |
| the symptom is restated and the two timelines **agree** | 10 |
| a same-symptom conflict, rejected for a stated reason | 9 |
| a treatment sig sitting beside the symptom it treats | 1 |
| **picked** | **3** |

**The pool over-counts, and its two worked over-counts are pinned as tests rather than described.** `day-b`'s cases 8 and 9 are in it — they are the attribution limb, the thing this set exists *not* to be about — and a treatment sig lands inside the window of the symptom it treats, so a zithromax course beside a cough counts. **Neither is filtered out.** A filter tuned until it returned exactly these three would read as recomputable and prove nothing, which [fixtures/README](../README.md) refuses by name.

**One exclusion is luck rather than design, and it is worth knowing before trusting the 43.** A restatement that *agrees* is excluded by its value — `day-b`'s case 4 writes `x 5 days` three times — but `day-b`'s case 12 writes `started saturday` and then `started saturdy`, which are two different strings. It is out only because no symptom sits within the window of the typo. The filter cannot spell-normalize, and normalizing would be guessing which spelling was meant. `tools/test_corpus_census.py` pins both cases and both reasons.

## The three, and what each one is for

**Case 1 is the conflict with nothing to infer.** `cc: cough, soar throat x 2 days` against `exam: c/o cough, soar throat started yesterday`. The onset statement **names both its symptoms**, so attaching it is reading rather than inference — `clinical-note` says as much — and the same two symptoms therefore carry two numbers. Two days and one day, and the span containing both is the one the skill file writes out in full: `1 to 2 days`.

**Case 2 is the same conflict reached through the pronoun clause.** `cc: cough, chest and sinus congestion x 2 days` against `exam: she states this all started yesterday`. `this all` names no symptom, and the clause carries **no** new-or-worse marker — no `now also`, no `new`, no `worsening`, no `worse today`. Row 16 routes an unmarked pronoun to the whole illness, and *then it is a genuine conflict*. So the two cases arrive at the same span by the two different paths the rule describes, and a run that only handles the named form passes case 1 and fails here.

**Case 3 is the control, and it carries both answers in one sentence.** Its chief complaint dates a group of symptoms `x 3 days` and a rash `x 4 days`; its exam then re-dates the **diarrhea and the sore throat** to `2 days ago` and the **rash** to `4 days ago`, running one clause into the next.

- The diarrhea and sore throat conflict — three days against two — and take a span.
- The rash **agrees with itself**, and there is nothing for a span to contain. It takes one value.

Without it, a run that spanned every restated timeline it met would score full marks on cases 1 and 2 while getting the rash wrong, which is the failure `hedged-dx`'s own case 3 exists to catch one skill over.

**The set is narrower than is comfortable.** All three patients are adult women and all three conflicts resolve to one or two days apart. That is worth knowing when reading a score off it, and it is not fixable from forty-three candidates without taking cases whose spans cannot be computed at all — see *What was left out* below.

## What was changed on the way across

Everything else is verbatim, typos included. `soar throat`, `guifenisen`, `phenergran`, `gestiational`, `arythmia`, `abilifiy`, `tegratol`, `effusioin`, `phayrngeal`, `sore thrat`, `carple`, `genetal herpies` and case 3's trailing comma after `contact dermatitis` are all preserved as written. Never repair one here; that hides the defect the set is meant to find.

| Substitution | Why |
| --- | --- |
| `[PT]` | Patient name. Standing rule 1. |
| `[DATE]` | The last menstrual period, written as a calendar date on all three. A date finer than a year is the identifier that matters here, and with the visit date gone the interval it encodes cannot be recovered anyway. Nothing in this set turns on it. |
| `2025` | Case 1's `last pap 7-2025`, with the month dropped. [fixtures/README](../README.md) removes dates finer than a year and says a year alone identifies nobody; `hedged-dx` keeps a bare year on the same rule. That a pap was recent survives. |

**A cataloging annotation was removed from cases 2 and 3, and it is not shorthand.** Both source encounters end with a bracketed `[NOTE: …]` paragraph written into the day file long afterwards — one naming an unrelated drift candidate, one reasoning about which patients share a surname. Neither is anything the clinician wrote in the room, and the second is a list of names. **They are removed as commentary, not redacted as PHI**, and the distinction matters: a fixture is derived from what the working file recorded of the encounter, and an annotation is a later reader's opinion about it. Nothing clinical is lost.

**No visit date is removed beyond the two above, because none is written down.** The relative days that appear — `yesterday` in cases 1 and 2 — are clinical content and stay; they are the whole subject of the set. Case 3's `Vape since march` is a bare month with no year and pins no visit.

**Every case states an age**, so no date of birth had to be resolved before the dates were stripped. `tools/test_corpus_census.py` asserts that rather than trusting this sentence.

## Do not reconcile the timelines in these files

An input whose chief complaint has been tidied to agree with its exam line cannot test what the skill does with a conflict, which is the entire set. `clinical-note` forbids the same move in the output — *Never "correct" a number* — and these three files are the only committed inputs that put its span rule under load.

**And do not repair case 3's rash into a conflict either.** `x 4 days` and `started 4 days ago` agreeing is not a transcription slip; it is S3's whole subject, and making the two differ would delete the only case in this repo that can tell a run which spans correctly from one that spans everything.

## What was left out, and why

**Thirty-one of the forty-three are not this set's shape at all**, and the table above splits them: twenty are the **attribution** limb `day-b`'s B10 already covers, ten restate a timeline that **agrees** with itself the way `day-b`'s cases 4 and 12 do, and one is the treatment sig the pool cannot see past. None of the thirty-one was rejected on judgment — a fourth attribution case would have added a denominator and no coverage, and an agreeing restatement has nothing for a span to contain.

**Nine are genuine same-symptom conflicts and were rejected one at a time.** They are the interesting rejections, and each names what a row over it would have had to rest on.

**Five cannot have their spans computed once the visit date is gone.** Each dates a symptom once as an interval and once as a **weekday or a holiday** — a rash given as `x 3 days` and then `it started sunday`, a cough given as `x 1 month` and then `since` a named holiday, an illness given as `x 4 days` and then `this started monday`. Every one resolves only against the day the patient was seen, which [fixtures/README](../README.md) removes on the way across. `peds-bp`'s R2 is the same collision from the other side: that set redacts a holiday anchor and then has to score the note for not writing one. A row here would be asking a run to span two values, one of which the input no longer contains.

**One was rejected on a vague endpoint.** It dates joint pain to `3 weeks` in one clause and `severl months` in another. A span needs two values to hold, and *several months* is not one — scoring it would need someone to decide what number it meant, which is the judgment [fixtures/README](../README.md) says a binary row may not rest on.

**One was rejected because the conflict is probably a typo.** `x 3 days` in the chief complaint against `gotten worse over the past 33 days` in the exam. A span of 3 to 33 days is arithmetically available and clinically absurd, and a fixture resting on it would be testing what a run does with a slipped keystroke rather than with two timelines. That is a real question — `hedged-dx` keeps an impossible `hr 1238` for it — and it is not this set's.

**One was rejected because its second statement dates a change rather than an onset.** A leg pain given as `x 3 months` in the chief complaint, and an exam line reading `for about 2 weeks she has noticed consistant pain`. Whether that is a second onset for one symptom or the point at which an old one turned constant is a reader's call, and a binary row resting on it would need the goodwill [fixtures/README](../README.md) says a binary row may not need.

**One was rejected although it is the strongest evidence for the span's *form*.** Its chief complaint reads `cough x 2 days` and its exam `she has had a dry cough [for the] past 2 - 3 days` — a conflict, and one where **the clinician writes a span himself**. It is left out because the second value is already a range, so a run that copied the exam line verbatim would produce a passing answer without ever spanning anything, and the row could not tell the two apart. `clinical-note` cites his `11-12 yrs ago` and `worsening in the past 3-4 days` for the same corroboration, and those are already pinned by a test.

Named here rather than silently dropped, on `peds-bp`'s terms: a set scoped to part of what it could have covered says what it left out.

## What these inputs contain that this set does not score

Two of the three carry findings that would anchor rows in other classes, and none of them is scored here.

- **Case 3's `bp 141/96` is a given abnormal** with no hypertension documented anywhere in the encounter, and its exam records `mild chest pain, mild sob` and dizziness in a patient whose family history is `DVT, CAD`. Its diagnosis line names COVID and contact dermatitis only.
- **Case 3 names a `covid exposure` and a `Dx COVID` with no swab documented** — `day-b`'s C2 shape exactly, one encounter further along.
- **Case 2 carries `hr 108` with orthostatic dizziness** against a diagnosis of URI.

Each is a DRIFT or CODING question, this set has a reference **owed** and no reading of these inputs alone settles what a *correct* note does with them. Recorded so a later reader knows they were seen and left, rather than missed.
