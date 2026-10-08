# Medatrax note entry is a verified scripted fill, and a form is finished only when Date Finished says so

[#1420](https://github.com/mshamblin5150-code/clinical-skills/issues/1420)'s third defect is that
the documented Medatrax route depends on a clipboard the agent cannot always reach.
[#1446](https://github.com/mshamblin5150-code/clinical-skills/issues/1446) records three ways the
same procedure's **Finish** step lost or stalled a form, and
[#1467](https://github.com/mshamblin5150-code/clinical-skills/issues/1467) records a `VISIT:` line
numbered so the grader refused it. All three describe one procedure and one template line, so the
clinician folded #1446 and #1467 into #1420 and ruled them together on 2026-10-08. The facts below
were read from `main` at `1b8ffa93`, and none of the files they rest on changed before this record
was written on `main` at `472632e4`. **Nothing is built here; this is the record the build reads.**

[ADR 0294](0294-an-orchestrator-s-per-note-claims-and-every-repair-pass-are-derived-from-the-record.md)
records the same grilling's other two defects.

## Measured before ruling

**The reference documents the route that failed.** `reference/medatrax-fields.md` *Note form* step 3
says "Paste each note section into its matching box." On one shift the paste arrived empty and then
Windows refused clipboard access while the clinician was remote. Setting each box's value by page
script and reading it back posted all 12 notes. The next shift posted its 11 notes the same
way.

**Three Finish failures on that next shift, recorded on #1446.** A navigation immediately after
**Finish** cut the save off. The page's two-minute autosave shares one page-level request slot with
the commit; an autosave firing during a commit made the page treat the commit's response as an
autosave, and the redirect never came. One form saved, read back exactly and showed no edit buttons,
yet its **Date Finished** cell in the lower Forms panel was empty while ten others carried a date.
The commit path can also raise a native `confirm()` dialog that freezes the tab the automation
drives.

**Two triggers have each finished forms.** A coordinate click on **Finish** failed to commit for 3
of 11 forms. Cancelling the autosave timer and calling the page's `Commit()` finished every later
note in #1446's body; a scripted `click()` on the button element followed by waiting for
`/login/forms/` committed every one of the 6 forms it was used on.

**Two completion readbacks exist, and one is measured to discriminate.** The lower Forms panel's
**Date Finished** column printed an empty cell for the form that saved without finishing. Patient
Detail's Forms table carries a **Finished** checkmark, recorded in
[ADR 0223](0223-a-shift-is-entered-into-medatrax-after-one-go-ahead-and-confirmed-by-one-posted-reading.md)'s
measurements, but no saved-but-unfinished form has been observed there.

**The `VISIT:` grammar lives in the shared posted-reading check.** #1330 is closed, and the line's
required field patterns sit in `tools/discussion_artifact.py`, called by `medatrax_posting`. That
check requires the lines to count 1 to N without a gap, while `batch-shift` step 7's template writes
the opener as `<N>`, the same letter the step uses for note files.

## Ruling 1 — scripted fill is the primary route, and paste is the named fallback

The run reads the four section strings from `private/form-sections/note-N.json`, sets each box's
value, dispatches input and change events, and reads each value back, comparing its length and
SHA-256 with the stored string. Nothing proceeds to **Finish** until all four match; any mismatch
stops the run for the clinician. Paste is used only when no page-script tool is available, and the
reference states that the paste route has no readback before **Finish**. The post-save View read
against the Entry copy stays in place on both routes: the readback proves what was typed, and the
View read proves what was saved.

## Ruling 2 — the autosave and the confirm dialog are overridden in the form's tab, and re-derived when they move

Immediately before committing, in the form's own tab only, the run cancels the autosave timer,
disables the autosave function, and replaces `confirm()` with a recorder. A recorded `confirm()`
message stops the run for the clinician rather than being answered. No request's content is altered
and nothing is changed on the server. When the page no longer carries the names the reference
records, the run re-reads the form page's own script, finds the current timer and autosave names,
adjusts the override and proceeds, and the finished-state readback of ruling 4 still decides whether
the form finished. Each such re-derivation lands through the after-action review as a correction to
the reference. If the run cannot re-derive the names it stops for the clinician; it never commits
without the override.

## Ruling 3 — Finish is a scripted click on the button, then a wait for the redirect

The run triggers **Finish** with a scripted `click()` on the button element, found by its visible
label, and waits for the page itself to return to the Forms page before any navigation. Calling
`Commit()` directly was refused because it skips whatever the button's handler checks first and adds
an internal name the run would have to re-derive.

## Ruling 4 — Date Finished is the canonical completion readback

After entry, the lower Forms panel filtered to the visit date must show a **Date Finished** value for
every posted form. Patient Detail's **Finished** checkmark may be reported beside it and decides
nothing until a saved-but-unfinished form shows what it does.

## Ruling 5 — every VISIT line carries the finished state

Every `VISIT:` line carries a required `finished=<Date Finished as displayed>` field, copied from the
lower panel like every other locator on the line, and the shared posted-reading check refuses a line
without it. This widens [ADR 0223](0223-a-shift-is-entered-into-medatrax-after-one-go-ahead-and-confirmed-by-one-posted-reading.md)
ruling 13's line and does not reverse it.

## Ruling 6 — the VISIT line opens with the entry order

The `VISIT:` opener is the order of entry, 1 to N with no gaps, which is what the shared check
already requires, and the `patient` field carries the note-file number so each line still traces to
its note. Relaxing the check to note-file numbering was refused, because a gap would then be
legitimate whenever a day file skipped a number, and a missing form would stop being visible.

## Consequences

- `reference/medatrax-fields.md` *Note form* gains rulings 1 through 4 in procedure order.
- `skills/batch-shift/SKILL.md` step 7's `VISIT:` template gains rulings 5 and 6.
- `tools/discussion_artifact.py`'s `VISIT:` patterns gain the `finished=` field, with its tests.
- #1446 and #1467 close as folded into #1420.

## What none of this reaches

The grader proves a `finished=` value was written in the right shape, not that it was copied from
the panel truthfully, as with every other locator on the line. The override depends on portal
internals Medatrax can change at any time; ruling 2 makes that a re-derivation rather than a silent
failure, not a guarantee. The paste fallback's lack of a pre-**Finish** readback is declared, not
closed.
