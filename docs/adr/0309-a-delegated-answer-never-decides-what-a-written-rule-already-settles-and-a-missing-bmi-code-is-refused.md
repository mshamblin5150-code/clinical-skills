# A delegated answer never decides what a written rule already settles and a missing BMI code is refused

**Measured at:** b4f3f9e3eb85d846ec3dde586ffbc19d7c6ba84c

[#1461](https://github.com/mshamblin5150-code/clinical-skills/issues/1461) was filed from the
after-action review of a NUR5144 `batch-shift` run. The clinician
delegated the run's open pre-approval questions. The orchestrator answered one of them by holding
that a weight diagnosis is not coded where no weight assessment was documented, and six note
passes removed their BMI-derived `E66` and `Z68` codes. `skills/clinical-note/SKILL.md` already
answered that question the other way: a measurement of the patient's own body takes its code
(#70), and a BMI from the note's own values is *not withheld* (#46). Every gate passed afterward
and the six notes were posted. In the same run the orchestrator called a patient established from
the shorthand alone, which [ADR 0302](0302-patient-status-is-never-guessed-and-an-unsupplied-earlier-visit-is-never-written-as-given.md)
ruled and whose ruling 5 left the general bound on delegation to this ticket. Grilled 2026-10-09
against `main` at the commit above, where the freshness gate read `FRESH`; the clinician ruled
every point below in that session, and the build lands with this record.

## Measured before ruling

**Neither error in that run answered an open question.** The BMI codes were settled by
`clinical-note`'s written rule and the patient status by ADR 0250 ruling 4. Each delegated answer
overrode a written rule because nothing required the orchestrator to look for one first.

**No grader computed a BMI from a note's own values.** `filled_vitals_census.py` read only declared
filled heights and weights, and no row compared a note's height and weight with the codes it
carries. The six notes' tier blocks said no weight diagnosis was coded, and that statement passed
every check.

**The committed records carry two instances of the gap.** `fixtures/filled-anchor/notes/case-05.md`
computes an overweight adult BMI and carries neither code; it is day-b run 1 and predates #46.
`fixtures/slot-form-run/hedged-dx-case-03.md` computes a three-year-old's BMI in the overweight
band of both CDC charts and carries neither code; it predates the committed calculator (#123).
Neither record is edited.

## Ruling 1 — a delegate answers only the question kinds the skills list as the clinician's

Delegation reaches the question kinds `PRE-APPROVAL PATIENT QUESTIONS` names, less the
earlier-visit status question ADR 0302 ruling 4 never delegates. Any other question a run meets is
settled by the written rule that governs it, quoted from this repository, and an answer that
contradicts a quoted rule is not applied. A fixed list of never-delegable subjects was declined
because nobody would have listed weight coding before this run. Narrowing delegation alone was
declined because a genuine gap with no governing rule would stall a run the clinician had told to
proceed.

## Ruling 2 — a question no written rule governs is recorded and named at the go-ahead

Where the run finds no governing rule, the delegate may answer, and the go-ahead message names that
answer. Every question settled under ruling 1 or this ruling is recorded in the run's
`delegated-answers.md` with the quoted rule or `none found` and what the run did.
`tools/delegated_answers.py` grades that record at `--submission` from both note graders and
refuses a quoted rule that the cited file does not contain.

## Ruling 3 — a grader computes each note's BMI and refuses a missing code

`filled_vitals_census.py` computes a BMI from the height and weight each note states, given or
filled. An adult at 25.0 or above owes the exact `Z68` band and an `E66` code of the matching
family; ages 2 through 19 read through `tools/cdc_percentile.py`, and a band with a paired `E66`
code owes it and its `Z68.5-` band. A missing code fails the run before the go-ahead. A normal or
low BMI is reported and never graded, which leaves the open coding-guidelines question about a
`Z68` at a normal BMI where `clinical-note` left it. A reader-owned verdict was declined because
the arithmetic is mechanical and a reader can return `clean` without doing it.

## Ruling 4 — the six notes that run posted stay as posted

The six Medatrax entries, and the run's notes, worksheets and records, are not changed. Restoring
them was declined as a full approval and portal pass for secondary findings on a past shift.
Correcting only the local files was declined because it makes the record and the submission
disagree, the failure the *not withheld* rule was written to prevent.

## Ruling 5 — an orchestrator's answer for the clinician is a delegated answer

`CONTEXT.md` defines **Delegated answer**, with *ruling*, *delegated ruling* and *coordinator
ruling* on its avoid row. A **Ruling** remains a ratified ADR decision only. *Delegated decision*
was declined because *decision* is already on **Ruling**'s avoid row.

## What this does not reach

The record is graded only where it exists, so a delegation the run never records reads as none;
the BMI row reaches the instance that caused this ticket regardless. `RULE: none found` is taken as
written, and whether an answer obeys the rule it quotes is the clinician's reading at the go-ahead.
The BMI row's reading boundary belongs to `bmi_codes.DECLARED_LIMITS`, and the record grader's to
`delegated_answers.DECLARED_LIMITS`.
