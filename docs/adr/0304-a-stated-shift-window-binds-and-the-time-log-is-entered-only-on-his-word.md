# A stated shift window binds and the time log is entered only on his word

**Measured at:** f9350d209fa75142b1e0ab78a75f2ae8c0abdddd

[#1464](https://github.com/mshamblin5150-code/clinical-skills/issues/1464) was filed from the
after-action review of a NUR5144 `batch-shift` run. The clinician
supplied the shift start and its total hours before entry, and the orchestrator said it would not
need the Medatrax Time Log. At approval it said it would still need the start confirmed against the
Time Log. Grilled 2026-10-08 against `main`, where the freshness gate read `FRESH`; the clinician
ruled every point below in that session. **Nothing is built here; this is the record the build
reads.**

## Measured before ruling

**The skill sentence reads as though the Time Log is always read.** `skills/batch-shift/SKILL.md`
says *"Ask the shift start once. Read that date's hours from the Time Log"*, and
`skills/clinical-note/SKILL.md` says the same in its *Times* section and in step 9. Each carries the
only exception, a date with no Time Log row, and none says what a duration the clinician has stated
does.

**The Time Log holds a duration and no clock time.**
[ADR 0223](0223-a-shift-is-entered-into-medatrax-after-one-go-ahead-and-confirmed-by-one-posted-reading.md)
measurement 1 records its saved-entry list as `Date`, `Hours` as a duration, and `Confirmed`, and its
entry form as hours and minutes. It can supply a missing duration and never a start.

**No skill writes the Time Log.** Every rule in the tree reads it, and ADR 0223's portal readers
opened it view only. The posted reading ADR 0223 ruling 13 defines carries one line per visit and
nothing about the Time Log.

## Ruling 1 — a stated start and duration bind and the Time Log is not read

When the clinician has stated the shift start and its duration, the two set the shift window and
the agent does not open the Time Log for that date or ask him to confirm against it. He enters the
Time Log row himself, so a read would check him against himself, and ADR 0223 ruling 4 already places
the timing check at review, where every visit's start and end is shown. Reading the Time Log and
reporting a difference without asking was declined because it returns the confirmation this ticket
was filed over, softened. Letting the Time Log win was declined because it overrides what he said.

## Ruling 2 — a partial statement is completed without re-asking what he stated

With a start stated alone, the agent reads that date's duration from the Time Log, as before, and
asks for the duration when no row exists. With a duration stated alone, the agent asks the start once
and the stated duration binds without a Time Log read. Asking for the missing number in every case
was declined because the Time Log answers a start-only shift without him. Asking for both again was
declined because it re-confirms a number he already gave.

## Ruling 3 — the duration is hours and minutes

The shift's duration is a span in hours and minutes, as the Time Log stores it, and every comparison
this record requires reads both.

## Ruling 4 — what he states is recorded in the run when he states it

A start or duration the clinician states for a shift, in any sitting, is written into that shift's
run directory at once, and every later step, sitting and subagent reads that record before asking.
That is what makes a value already supplied. The run that filed #1464 had the values and re-asked at a
later step, and a written record is the one place every step can see. Counting only the current
sitting was declined because a shift split across sittings would re-ask. Recording which values came
from him and which from the Time Log, shown at the go-ahead, was declined as a label he would read
past; the review already shows every visit's times.

## Ruling 5 — the agent enters the Time Log row only on his explicit word

The agent creates the shift's Time Log row only when the clinician tells it to in that run. It
enters the date and the stated duration, saves, and reads the saved row back against them. A
mismatch is corrected to the stated values and read again; any other discrepancy stops for him.
Letting the shift's go-ahead authorize the write was declined because an approval would then cover a
portal write he never named.

## Ruling 6 — an existing row is never duplicated or edited

When he asks for the entry and a row for that date already exists, a row whose duration matches the
stated one is the entry, and nothing is written. A row that differs stops the agent, which shows him
both durations. The agent never adds a second row for the date and never edits his. Stopping on a
matching row was declined as a question where nothing is wrong. Overwriting was declined because a
mistyped statement would replace a correct row with no second look, on the hours his documentation
deadline counts.

## Ruling 7 — the posted reading records the Time Log in one line

The shift's posted reading gains one Time Log line carrying the date, the duration as read back, and
whether the agent entered the row or found a matching one. A shift where he asked for no entry
writes `not requested`, so an omitted entry never reads as a clean one. This extends ADR 0223 ruling
13's record and withdraws none of it. Leaving the read-back in chat alone was declined because an
agent's write to his hours would leave nothing the after-action review can check. A separate run
file was declined as a second place the review's population would not include.

## Ruling 8 — both skills take the rule

`batch-shift` and `clinical-note`, in its *Times* section and in step 9, take rulings 1 through 7. A
standalone note is a one-encounter batch under ADR 0223 ruling 1, so the two skills set the window
the same way. The glossary names the span as the **Shift window**.

## ADR 0223 ruling 4 is narrowed, and its marker is deferred

Ruling 1 supersedes ADR 0223 ruling 4's sentence "the end is that start plus the hours the Time Log
holds for that date." Every visit still falls inside the shift, the start is still asked once, and a
re-read of the Time Log before entry is still refused.

**The ADR 0280 marker and declaration are deferred, not skipped.** `tools/test_adr_supersession.py`
reads a marker only beneath a `## Ruling N` heading, and ADR 0223 numbers its rulings as `### N.`
items, so writing both turns the suite red; measured on this branch, the pair produced *unread
supersession marker* for ADR 0223 and *ruling 4 has no matching marker* for this record.
[#1540](https://github.com/mshamblin5150-code/clinical-skills/issues/1540) repairs that reader, and
ADR 0286 ruling 6 deferred its own marker to it for the same reason. #1540 now carries this pair.

## What this does not reach

Whether the duration he states is right stays his reading at review, where every visit's times are
shown. The Time Log entry form's fields beyond date and duration, such as the course it is logged
against, were not measured in this session; the build reads the live form view only before writing
its first row. The `Confirmed` column decides nothing here. No check establishes that a step read
ruling 4's record before asking.
