# The go-ahead UpToDate block and the Medatrax posted reading are written by committed tools and checked before they are relied on

**Measured at:** 15edf43932187b09122100ba14a812657dae09e9

[#1808](https://github.com/mshamblin5150-code/clinical-skills/issues/1808) was filed from the
after-action review of a `batch-shift` run (NUR5144 clinic shift) on 2026-10-14. Two run artifacts
were hand-built by per-run scripts and both came out wrong. The clinician approved a go-ahead whose
Review sheet carried neither `UPTODATE CONFLICTS` nor `UPTODATE FAILED PULLS`, while the run had
four failed pulls. The `reread.md` posted-reading record was malformed, and the after-action extract
would not run until it was fixed. A later comment recorded the next shift's coordinator copying the
prior run's private scripts and breaking three more formats. Grilled 2026-10-18 against `main` at
the commit above, where the freshness gate read `FRESH`. The clinician ruled every point below in
that session, one question at a time. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The committed pull log keeps only pulls that worked.** `tools/outbound_search.py` writes a passed
search to the run's `outbound-searches.jsonl` and a live pull, as a search id and a dump id, to
`uptodate-pulls.jsonl`. It has no command or field for a failed pull. `skills/clinical-note/SKILL.md`
says to keep "the failure and the instrument tried in the private run record," which names no file
and no shape. The ticket's comment that the run's pull log "records each pull's outcome" describes
a per-run file, not a committed one.

**A note marks only half the failures.** Under
[ADR 0347](0347-a-real-encounter-consults-uptodate-at-the-gaps-and-a-live-search-carries-clinical-terms-only.md)
ruling 8, a failed pull for a sheet conflict falls back to the sheet with a tail ending
`; uptodate pull failed`, which `tools/differential_scan.py` grades. A failed pull at a gap keeps
its existing verdict and leaves no mark in the note. On the ticket's own account the shift recorded
no threshold-sheet conflict, so none of its four failures could have left that mark.

**The skill contradicted itself about where the lines go.** `skills/batch-shift/SKILL.md` step 7
opened by saying the Review sheet "carries" both lines. The same step then says the `.docx` "carries
exactly what the notes carry" and keeps `PRE-APPROVAL PATIENT QUESTIONS` and `REPAIRS` outside it.
ADR 0347 rulings 6 and 8 say a conflict and a failure are shown at the go-ahead. Only that record's
build checklist said "the go-ahead review sheet carries the conflict and failed-pull lines." A
checklist item is not a ruling, so this record supersedes no ruling there.

**Approval never opens the Review sheet.** `approval_record.approve` for `batch-shift` takes
`medatrax_posting.note_paths(run, batch=True)` as its sources. For the three shown-text skills it
already reads the session transcript through `verify_shown_text`.

**The posted-reading checks exist and run late.** `discussion_artifact.read_posted_readings` and the
Medatrax checks in `tools/medatrax_posting.py` refuse a malformed record. They run inside the
completion grader and the after-action extract. No committed tool writes `reread.md`, and
`medatrax_posting.py` has no command line, so nothing checks the record between writing it and the
after-action review. `clinical-note`'s single-note entry writes the same record shape.

## Ruling 1 — a failed pull is recorded by the search tool, and every search ends in an outcome

`tools/outbound_search.py` gains a command that records a failed live pull against a passed search
id, carrying the decision it was for and the instrument tried, in the run's private record. Every
passed search must end in either a recorded live pull or a recorded failed pull; a passed search
with neither is a finding. Counting only what the notes carry was declined because it would have
caught none of this shift's failures. Marking gap verdicts in the note was declined because the note
is what gets entered in Medatrax. Reading a passed search with no pull as a failure was declined
because it cannot tell a failure from an unused search and has nowhere to keep the decision and
instrument.

## Ruling 2 — the lines are shown in chat at the go-ahead, not inside the `.docx`

`UPTODATE CONFLICTS` and `UPTODATE FAILED PULLS`, each `none` when empty, are shown in chat beside
`PRE-APPROVAL PATIENT QUESTIONS` and `REPAIRS`. The Review sheet keeps carrying exactly what the
notes carry, and step 7's opening sentence is corrected to match. One check then serves both
`clinical-note`'s single-note go-ahead and the shift's. Putting the block inside the `.docx` was
declined because it puts working output in the approval document and leaves the single-note
go-ahead, which has no `.docx`, needing a second check.

## Ruling 3 — a committed command produces the block, and approval refuses a block that does not match

A committed command derives both lines from the notes' tails and the run's pull and failure
records, and the coordinator shows its output word for word. At approval, for `batch-shift` and
`clinical-note`, the check reruns the command and refuses when the block shown in chat before the
clinician's reply differs in count or in detail. An unreadable transcript is incomplete coverage,
never clean. A hand-written block checked only by count was declined because per-run writing is
the defect and wrong details would pass. A producer with no approval check was declined because
nothing would stop its output being edited or skipped, which is how this shift's line went missing.

## Ruling 4 — "what differs" is recorded on the live pull that settled the conflict

The live-pull command takes the threshold sheet, the row, and a short text saying what differs. The
check confirms that pull is the one the note's `[uptodate over thresholds/<sheet> <row>: ...]` tail
cites: same sheet, row, and dump id. The text is refused if it carries a corpus name or date
literal. The search's digit refusal does not apply, because a difference is usually two numbers.
Dropping the column from the go-ahead was declined because the after-action review would have to
reconstruct the difference from both sources. Writing it into the note's tail was declined because
the tail would carry sheet maintenance into a clinical note.

## Ruling 5 — a committed writer for the Medatrax posted reading, plus a standalone check

A committed writer takes the agent's Medatrax readings: each visit's copied locators, reference,
dates and verdict, plus the Time Log outcome as hours and minutes. It computes `SUBMISSION-SHA256`
and the `N of N read` count, formats the duration, writes only the record's known lines, and refuses
to save a record that fails the existing reader and Medatrax checks. The same check is a standalone
command for a record written or edited by hand. It runs before the after-action review so a
malformed record never reaches the extract. Both `batch-shift` and `clinical-note` use them. A check
alone was declined because it leaves the per-run writing. A writer alone was declined because a
record edited by hand would again surface only at the review.

## Ruling 6 — #1808 is limited to rulings 1 to 5

The other copied scripts the ticket names (the identity-map helper, the Review-sheet and freshness
manifest builder, and the Medatrax fill builders) are
[#1882](https://github.com/mshamblin5150-code/clinical-skills/issues/1882), labeled for grilling
because each needs its own input decisions. The CPT receipt path stays on
[#1811](https://github.com/mshamblin5150-code/clinical-skills/issues/1811). Widening #1808 was
declined because the settled pieces would wait on unsettled designs.

## Build checklist

- `tools/outbound_search.py`: the failed-pull command (ruling 1); the conflict arguments on the
  live-pull command (ruling 4); the completion gate refuses a passed search with no outcome; the
  `DECLARED_LIMITS` object gains this record's limits below.
- A committed command that prints the go-ahead UpToDate block from the notes and those records,
  with `none` for an empty list (ruling 3).
- `approval_record.approve` for `batch-shift` and `clinical-note`: rerun that command and compare it
  with the block shown before the matched reply; refuse a mismatch; report an unreadable transcript
  as incomplete coverage.
- A committed `reread.md` writer and a standalone check command for Medatrax posted readings, reusing
  `discussion_artifact.read_posted_readings` and the `medatrax_posting` checks (ruling 5).
- `skills/clinical-note/SKILL.md` and `skills/batch-shift/SKILL.md`: name the commands at the
  failure, conflict, go-ahead and posted-reading steps.
- `CLAUDE.md` maintainer tooling: name each new command and point to its limits object.
- Tests through each public command: a failed gap pull with no note mark is counted; a passed
  search with no outcome is refused; a shown block missing a line, or with a wrong count or detail,
  is refused at approval; `none` is required for an empty list; a posted reading with a stray line,
  or a duration in whole hours, is refused before it is written; a clean shift passes.

## What this record does not reach

- **A pull typed without the search check.** It leaves no search record, so no outcome can be
  required of it; ADR 0347 already declares this gap.
- **Whether "what differs" is clinically accurate.** It is checked for patient identifiers only.
- **Whether the Medatrax readings passed to the writer are what the portal shows.** The writer
  formats and checks what it is given; the reading itself remains the agent's.
- **The scripts left to #1882.** The identity-map helper, the Review-sheet and manifest builder, and
  the fill builders stay per-run until that ticket is ruled and built.
