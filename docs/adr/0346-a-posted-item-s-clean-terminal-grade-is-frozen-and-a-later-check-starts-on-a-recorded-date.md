# A posted item's clean terminal grade is frozen and a later check starts on a recorded date

**Measured at:** 3f95fe9d3e0e858d7bc3ec2a9376ca8681bd2ee7

[#1558](https://github.com/mshamblin5150-code/clinical-skills/issues/1558) was filed from the
after-action review of a `discussion-reply` run (NUR 5042 Module 9) on 2026-10-04. A discussion
initial post was approved, posted, read back, reviewed and graded `complete` on 2026-10-01. Three
days later a reply sitting reused the run directory, and the initial post's terminal grade then
failed on a check that did not exist when it was approved. The ticket's comments added the second
limb: a later change to shared project context, including another session's memory write, breaks
the heading read of work already on the board. Grilled 2026-10-12 against `main` at `fb7c9b93`,
where the freshness gate read `FRESH`; `main` then advanced to `3f95fe9d`, and every claim below was
checked against that tree. The clinician ruled each point below in that session. This record also
answers the adoption question [ADR 0310](0310-an-approval-carries-the-clinician-s-whole-reply-and-is-refused-when-his-messages-do-not-hold-it.md)
and [ADR 0330](0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md) routed
here. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**A later sitting re-grades every approved item in the run.** `run_status_stop_hook.handle` grades
a touched run only when the reply says `complete`, and then calls `completion_is_clean` for every
approved item, including items posted and graded clean in an earlier sitting. The only stored
result is the run's `run-status.json`, whose `approval_revision` is the sorted list of every approved
item in the run. Approving one more reply changes that list, so the run reopens and every earlier
item is graded again under the rules in force today.

**Three checks have no start date, and two of them fail work approved before they existed.** The
draft-order observation ([ADR 0290](0290-the-pre-draft-gates-observe-that-the-draft-does-not-yet-exist-and-a-late-gate-is-a-finding-the-clinician-clears.md)
ruling 1) arrived on 2026-10-03. `coursework_run.grade_order` runs after `project_context`'s posted
carry-forward for every key, so a record written before then reports
`first draft observation is missing`, and `voice_model_identity.completion_gate` reports
`draft observation shape is invalid` for the same reason. Neither can be satisfied after the fact. The
posted-reading `TIME-LOG` line (#1464) arrived on 2026-10-08 and is required for every Medatrax
reading regardless of its date.

**Every heading read is tied to the live context digest.** Each completion grader builds the
heading-read binding from `project_context.recorded_digest`, the digest of the run's current
record, and `heading_read` refuses a record whose `CONTEXT-DIGEST` differs. Any rerun of the
project-context gate moves that digest, including one that only refreshes a memory index another
session appended to. `discussion_reply_scan` binds every reply in the run to the same digest, so one
move breaks every earlier reply's read. The 2026-10-07 comment records the cost: a fresh reader
returned `narrows` on a posted post whose original reader had returned `agrees`.

**Five rulings in one week each answered this case for one check.** `approval_record` carries a
dated cutoff for the Posting go-ahead (ADR 0331 ruling 2), compared with the content approval's
time. `aar_scan` carries five cutoffs compared with a review round's extraction time, the last
being the memory-index measurement of ADR 0333 ruling 7. `project_context` carries one compared with
the record's confirmation date, and `research_ledger` one compared with the ledger's date.
`research_ledger`'s `STATED-EXPIRY` field has none and reports a ledger without it as unread.

**Existing runs, measured 2026-10-12.** Read with `run_status_stop_hook.approvals` and the stored
run state, integers only, across every registered checkout's run directories: 10 runs carry
approvals covering 12 approved items, 10 of them with a recorded posting. 3 runs hold a stored
`complete` result that still matches their current approvals, covering 3 items. The other 7 runs
are stopped or carry no state. These figures were measured against private run records that
nothing committed re-derives.

## Ruling 1 — a posted item is frozen at its first clean terminal grade

The first time an approved item's own terminal grade passes, that result is stored for the item and
tied to its approval revision. Later sittings never grade a frozen item again: the run is
`complete` when every approved item is either frozen or grades clean now. A new approval of the
same item is new work, so its freeze no longer applies and it is graded fresh. Every consumer that
would grade a frozen item under current rules honors the freeze, including a later review round's
posted-reading check.

Giving every later check a start date instead was refused as the general answer, because builders
have forgotten that date for the draft-order observation and for `TIME-LOG`, and because a moved
context digest is not a new check: another session's write moves it under checks that already
existed. Freezing at the recorded posting was refused because the posted reading and the after-action
review are graded after posting, so a missing readback or review would pass permanently. Keeping
the run-level `complete` result as the freeze was refused because approving another item in the
run reopens it, which is the defect.

## Ruling 2 — a frozen item prints one line, and only its own submitted file is compared

A later grade reports a frozen item in one line naming the item and the date it froze. The item's
own approved sources are compared with the fingerprint recorded when it froze; a change is reported
as a note and never changes the status. Shared project context moving after posting is not reported
at all.

Re-running the full grader and listing every differing row as a note was refused. It costs a
grader run per frozen item on every stop, it would print a context note on almost every sitting
because the memory index moves constantly, and no action can follow from it because the post
cannot be edited. Any move before posting was already shown to the clinician at the go-ahead under
[ADR 0328](0328-project-context-items-are-rechecked-at-the-go-ahead-and-an-appended-memory-line-is-not-a-move.md).
Printing the line alone was refused because an edit to the posted item's own source would then
leave the record describing something other than what is on the surface, with nothing saying so.

## Ruling 3 — items posted before the build are frozen when it lands, and the line says how

When the build lands, an item whose run holds a stored `complete` result covering it is frozen as
graded clean. Every other item with a recorded posting is frozen as *frozen at adoption, never
graded clean*, but only when its **Posted reading** and its after-action review record both exist.
An item missing either is left unfrozen and graded as normal.

This is ADR 0328 ruling 4's shape: the exemption is named and counted beside the result, and it
cannot reach a new run because every later freeze rests on a clean grade. A one-time clinician
confirmation of the list was refused as asking him to re-approve finished, posted work. Leaving
those items to fail was refused because every reply sitting that reuses their run directory would
reopen and fail them again on checks that postdate the work.

## Ruling 4 — every completion check has a start date in one table, and a test enforces it

One table lists every check a completion grade can raise, with the date it took effect. A check
whose start date falls after the moment it is compared with reports `not graded` for that item. A
suite test fails when a completion check is missing from the table, so a new check cannot arrive
without a date. This covers the window ruling 1 leaves: an item posted but not yet graded clean when
a new check lands.

Doing nothing in that window was refused because a check that cannot be satisfied after posting,
such as the draft-order observation, would leave finished work stopped behind a rule that did not
exist when it was approved. Dating only the checks that cannot be met after posting was refused
because it leaves each builder a judgment call and the same forgetting risk.

## Ruling 5 — each existing cutoff keeps the moment it compares against

The table records, for each check, which moment it is compared with. New checks default to the
item's approval time. The existing cutoffs keep theirs and are entered as they stand: the Posting
go-ahead against the content approval, the after-action review cutoffs and the memory-index
measurement against the round's extraction, the classmate declarations against the record's
confirmation, and the ledger qualifiers against the ledger's date. `STATED-EXPIRY` gains an entry
compared with the ledger's date. The draft-order observation, the heading-read context binding and
`TIME-LOG` gain entries at their landing dates.

Moving every cutoff to the approval time was refused because several moments were chosen
deliberately; a review round extracted days after approval would fall under rules that did not
exist when it ran. Leaving the existing cutoffs out of the table was refused because the test could
no longer say every check is listed.

## Ruling 6 — an unposted item's heading read is broken only by a change to what the reader saw

A heading read records what the project context held when it was taken. It is broken when an item
it saw is edited or removed (for the memory index, a line that was edited or removed), or when a new
place or item is added to the confirmed context, as happens when the clinician gives a direction
mid-draft. A line appended to the memory index does not break it; those lines are shown to the
clinician at the go-ahead under ADR 0328 ruling 2. A posted item's read is governed by rulings 1
and 2 and is not re-bound.

Keeping the whole-digest binding was refused because unrelated appends from other sessions force
fresh reads, and each fresh read is another chance for a different reader to flip the verdict on
unchanged text. Never breaking a read once taken was refused because a real revision to a planning
file, or a direction given after the read, would never be read against.

## Supersedes

- [ADR 0277](0277-the-run-status-check-covers-every-posting-skill-through-one-approval-record.md)
  ruling 4, its words "`complete` requires every approved item's terminal grade to be clean". A
  frozen item counts by its stored clean grade and is not graded again.
- [ADR 0272](0272-project-context-is-retrieved-into-a-confirmed-record-before-drafting.md)
  ruling 10, its binding "CONTEXT-DIGEST: <must equal the project context record's digest>". The
  read is broken only by a change to what it saw, and a posted item's read is not re-bound. The
  `CONTEXT-VERDICT` field and the reader's obligations stand.

## Build checklist

- `tools/run_status_stop_hook.py`: a per-item freeze record written when an item's terminal grade
  passes, keyed to its approval revision and carrying its sources' fingerprint; `complete` counts a
  frozen item without grading it; the one-line report and the source-change note.
- The build's adoption step: freeze items posted before it lands under ruling 3, naming and counting
  each kind.
- A shared start-date table with a "compared with" column, consulted by every completion grader,
  with the existing cutoffs in `approval_record`, `aar_scan`, `project_context` and `research_ledger`
  entered rather than moved; a suite test deriving the completion checks and failing on any absent
  from the table, with its derivation bound declared beside it.
- `tools/heading_read.py` and the graders that build its binding: bind to the items the context held
  at the read, apply ADR 0328 ruling 2's memory-index rule, and break on an added place or item.
- `aar_scan --extract` and every other current-rule consumer of a posted item honor the freeze.
- Tests through the public seams: a reply sitting after a frozen post, a new approval of a frozen
  item, an edited frozen source, a pre-build posted item with and without its readback and review,
  a check landing between posting and the clean grade, and an appended versus an edited memory line
  under an unposted heading read.

## What this record does not reach

- **Whether a frozen item's posted content was right.** The freeze records that every check in
  force passed; a later check's verdict on it is not graded.
- **A frozen-at-adoption item's quality.** The line says it was never graded clean; nothing grades
  it now.
- **Whether an appended memory line bears on an unposted draft.** The clinician reads the added lines
  at the go-ahead; nothing grades them.
