# The clinical go-ahead shows its paired grader's coverage lines before the ask and refuses an approval that did not

**Measured at:** 90877cef78cd9cbacec1c867dfe1926b23fe8f07

[#1845](https://github.com/mshamblin5150-code/clinical-skills/issues/1845) was filed from #1702's
grilling. ADR 0330 ruling 4 requires the coursework go-ahead to run its paired grader before the
ask and show every **Coverage qualifier** it prints exactly as printed, and approval refuses unless
those lines appeared in the chat before the clinician's reply. The clinical skills have no
counterpart, so at a `batch-shift` or `clinical-note` go-ahead any coverage line the clinician sees
is the orchestrator's own summary, which is the step ADR 0330's second source comment records
failing twice in one sitting. Grilled 2026-10-19 against `main` at `1b98c073`, where the freshness
gate read `FRESH`; `main` then moved to the commit above, which changed none of the files measured
here. The clinician ruled every point below in that session, one question at a time; the
widened vocabulary in ruling 4 and the whole of ruling 6 were ruled after the closing tracker sweep
found what they answer. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The coursework check is built and the clinical skills cannot reach it.** In
`tools/approval_record.py`, `prepare` runs the paired grader before the ask and writes a receipt
through `reader_remarks.prepare`; `approve` then calls `reader_remarks.verify`, which refuses unless
every line `reader_remarks.coverage_lines` selects appeared in the transcript between that grade
and the reply, and unless the grade at approval equals the receipt's. `prepare` refuses any skill
outside `reader_remarks.SCOPED_SKILLS`, the five coursework skills. For `batch-shift` and
`clinical-note`, `approve` runs the paired grader only after the reply, stores
`coverage_lines` in the item, and checks nothing about them; both skill files say to show
`pregrade_report` after the record is written.

**The pre-approval report carries lines that are the same on every run.** On
`fixtures/filled-anchor/notes`, `python tools/filled_vitals_census.py` without `--submission`
prints `unread remainder 0`, one `counted, not graded` line, `the shift summary: NOT GRADED -
absent`, and six rows reading `not graded - --submission was not supplied`. Every one of them
matches the shared selector. `python tools/differential_scan.py fixtures/slot-form-run` prints the
same six `--submission` rows.

**The coding graders cannot carry a gap to the go-ahead.** `batch-shift` requires exit 0 from the
descriptor-agreement grades in `tools/anchor_scan.py` before its roll-up is complete, from
`tools/exam_scheme.py` and `tools/entry_copy.py --check` before the Review sheet is built, and from
`tools/coding_freshness.py` before it is rendered; `clinical-note` requires the exam-scheme and
Entry copy checks to exit 0 before the note is shown. Any unread item there stops the run. The
paired completion grader is the only grade `approve` accepts at exit 2.

**The selector is a wording floor.** `reader_remarks.coverage_lines` keeps a line containing
`unread`, `not graded` or `not-graded`, `not scanned`, or `incomplete coverage`, case-insensitively.
Lines recorded but not yet built would fall outside it: ADR 0410's visit-times row in its
not-checked state, ADR 0412 ruling 6's line that an Rh(D) citation's year was not compared, and ADR
0412 ruling 8's never-graded contradiction count. ADR 0404 ruling 7's rapid-screen row and ADR 0412
ruling 7's line for citations not graded before the start date already match.

**The closing sweep found two more wordings outside it.** `tools/differential_scan.py` already prints
`was not run` and `NOT RUN` when a labeled Differential block holds no numbered item: on a one-note
run whose differential entries were unnumbered it exited 2 and printed `row 13 floor was not run in
...` and `row 13 floor - numbered item without a code  NOT RUN`, and the selector kept 0 of the 2.
No coursework paired grader prints that wording; the one `NOT RUN` string in
`tools/checks_ledger.py` is a docstring. And ADR 0394 ruling 6, not yet built (#1743), reports an
unreadable transcript in the six coursework graders as `not verified`, which the selector does not
keep: `the image answer: not verified - transcript unreadable` is not selected and the same line
worded `not graded` is.

**An unreadable transcript is handled two ways at the clinical go-ahead.** `reader_remarks.verify`
reads the transcript through `approval_record.assistant_text`; when nothing readable carries the
required lines it refuses, naming the transcript as unreadable. ADR 0408 ruling 3 and ADR 0413
ruling 8, ruled for checks at the same go-ahead, record an unreadable transcript as incomplete
coverage and as unverified respectively, never clean, and the built shown-text check in `approve` sets the grade incomplete and
still records the approval.

**The ADR 0405 ordering hazard does not arise in this check.** A comment on #1845 said the grade
`approve` runs after a reply that both accepts a failed repair comparison and approves the item must
already see the supersession record, or the repair-chain row refuses. `approve` refuses a grader
invocation carrying `--submission`, and without it both paired graders print `the repair hash chain:
NOT GRADED - --submission was not supplied` before the ask and at approval alike. The supersession
record cannot move the pre-approval report.

## Ruling 1 — the clinical go-ahead takes ADR 0330 ruling 4

`batch-shift` and `clinical-note` run their paired grader before the go-ahead request, show every
coverage line it prints exactly as printed, and approval refuses unless those lines appeared in the
chat between that grade and the clinician's reply. This is the built coursework check widened to
the two clinical skills; nothing in ADR 0330's reader-remark rulings comes with it, since #1702
settled remarks for the coding readers separately.

Showing the lines by instruction alone was declined because ADR 0330 records that instruction
broken twice in one sitting, and a shift's go-ahead is the longest summary this repository writes.
Leaving the lines after approval was declined because a shift with an unread note could then be
approved before the gap was seen. The cost accepted is one more command before every go-ahead and
roughly a dozen lines in each request, most of them identical from shift to shift, which is the
cost ADR 0330 ruling 4 already accepted for coursework.

## Ruling 2 — only the paired completion grader's lines are in scope

The lines shown and checked are those of the paired completion grader in
`aar_scan.COMPLETION_GRADERS`: `filled_vitals_census` for `batch-shift`, `differential_scan` for
`clinical-note`. The coding graders are out of scope **because** each one's own exit-0 requirement
already turns every gap into a stop before the go-ahead. A later change that lets one of them pass
at exit 2 brings it into scope; this ruling does not exempt it by name.

Showing both families was declined because the coding graders could only ever print `unread
remainder 0` there, so each go-ahead would gain lines that cannot say anything else, and the
approval step would have to rerun four or five more commands with their per-note record paths.

## Ruling 3 — the lines appear in chat, outside the Review sheet

The coverage lines are shown in the chat message beside `PRE-APPROVAL PATIENT QUESTIONS`,
`REPAIRS`, and the UpToDate lines, outside the Review sheet. This is ADR 0408 ruling 2's reasoning
applied unchanged: the check reads the transcript, a single-note go-ahead has no `.docx`, and the
Review sheet carries exactly what the notes carry. Putting the lines inside the document was declined
because it would need a second, document-reading check and still leave the single note needing the
chat form; putting them in both places was declined because the document copy would be checked by
nothing.

## Ruling 4 — one definition of a coverage line, with the floor declared

A coverage line at any go-ahead, coursework or clinical, is a grader line saying that some
population or row was not read, graded, checked, or compared. The shared selector is that
definition. It gains `not checked`, `not compared`, `never graded` (with its hyphenated form),
`not run`, and `not verified`, so the pending ADR 0410 and ADR 0412 lines, `differential_scan`'s
existing not-run lines, and ADR 0394 ruling 6's unreadable-transcript rows are selected. The last two
wordings were found by the closing sweep and ruled under this ruling's definition: a row that did
not run, or a transcript that was not verified, is something not graded. The selector remains a floor over
wording: a later gap line written in other words is not selected, and that limit is declared beside
the selector rather than claimed closed. A builder adding a gap line to either paired grader words it
in the selector's vocabulary.

Two kinds of line stay outside it. The UpToDate block of ADR 0408 and ADR 0409 is produced by its own
command and already has its own show-and-verify check at approval, so it is not paired-grader
output. ADR 0406 ruling 1's line naming the run records a grader set aside is not a gap: those files
are run records rather than notes, and excluding them is correct coverage.

Showing the paired grader's whole report was declined because a shift's go-ahead would gain forty
or more lines, one `GENERATION:` line per note among them, which the shift summary already shows. A
hand-kept list of row names per grader was declined because it goes stale with every new row.

## Ruling 5 — a changed grade refuses, as in coursework

When the grade at approval differs in any way from the grade shown before the ask, approval refuses:
the grader reruns, the new lines are shown, and the clinician is asked again. This is the built
coursework behavior, so one rule covers all seven skills on the shared approval step. The case that
would make it costly is mostly a note change, which already invalidates the approval under the
existing re-approval rule: a shift window stated in the approval reply moves the notes' visit times.
Every other row graded without `--submission` reads only the notes.

Accepting a change that only removes gaps was declined because it adds a second comparison rule
coursework does not have, for a case the measurement shows is rare. Checking only the lines shown
before the ask was declined because a gap appearing after the ask would be approved unseen.

## Ruling 6 — an unreadable transcript at the clinical go-ahead is incomplete, not refused

For `batch-shift` and `clinical-note`, when the transcript cannot be read to establish that the
coverage lines were shown, approval is recorded with the grade marked incomplete and the reason
named in the record, never as clean. A readable transcript that lacks a required line still refuses
under ruling 1. Coursework keeps the built refusal. This matches ADR 0408 ruling 3 and ADR 0413
ruling 8 at the same go-ahead, and the three clinical transcript checks share one read.

Refusing, as coursework does, was declined: an unreadable transcript is a tooling failure rather
than the dropped line this check guards against, and refusing would leave the clinician unable to
record a shift's approval until the reader was repaired while the sibling checks recorded the same
state as incomplete. Changing coursework to match was declined because it would reopen ADR 0330's
built behavior inside a clinical ticket.

## What the build changes

- `tools/approval_record.py`: `prepare` accepts `batch-shift` and `clinical-note`, running their
  paired grader and writing the same receipt; `approve` verifies the clinical coverage lines and the
  unchanged grade through the same seam, without reader remarks or the project-context check;
  ruling 6's unreadable-transcript outcome differs from coursework's.
- `tools/reader_remarks.py`: `coverage_lines` gains `not checked`, `not compared`, `never graded`,
  `not run`, and `not verified`, and the wording floor is declared in a module-level limits object
  beside it.
- The clinical transcript check: an unreadable transcript records the approval as incomplete with
  its reason under ruling 6, through the same transcript read as the ADR 0408 and ADR 0413 checks.
- `skills/batch-shift/SKILL.md` step 7 and `skills/clinical-note/SKILL.md`'s go-ahead: call `prepare`
  before the ask and show its coverage lines in chat beside `PRE-APPROVAL PATIENT QUESTIONS`,
  `REPAIRS`, and the UpToDate lines; the sentence saying incomplete coverage does not block stays,
  since a shown gap still does not block.
- Tests that drive a clinical approval through the public seams and refuse it when a coverage line
  was not shown, when the grade changed after the ask, and when the grade ran after the reply; that
  an unreadable transcript records an incomplete clinical approval; and that the five new wordings
  are selected.

## What this does not reach

- **Whether the clinician reads the lines.** The check proves they were shown before his reply.
- **A clinical approval recorded over an unreadable transcript.** Ruling 6 names it incomplete; it
  does not prove the lines were shown.
- **A gap line worded outside the selector's vocabulary.** Ruling 4's floor stands.
- **The coding graders' coverage.** Ruling 2 rests on their exit-0 requirement; the check does not
  verify that requirement was met.
- **Runs approved before this change.** Their frozen grades stand under ADR 0346; whether any is
  re-graded is an adoption question, not this record's.
- **The UpToDate block.** ADR 0408 ruling 3 owns its check.
