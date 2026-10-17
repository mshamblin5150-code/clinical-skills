# The coding readers carry reader remarks to the clinical go-ahead

**Measured at:** 62a755eb242a1c54a513b5bcc070c9f02c19ee2d

[ADR 0330](0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md) gave the
coursework readers a place for a **Reader remark** and kept the clinical skills out of it on the
stated ground that they had no reader record that could lose one. Its closing sweep showed that
ground false, and its ruling 6 routed the coding agreement reader to
[#1702](https://github.com/mshamblin5150-code/clinical-skills/issues/1702). Grilled 2026-10-17
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in
that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Three skills run the agreement reader, not two.** `icd10-cpt` and `batch-shift` run the blind
descriptor-agreement read, as #1702 says, and so does a standalone `clinical-note` run.

**The agreement read drops anything outside its required answers, at every level.**
`anchor_scan._grade_agreement` reads each code row for its six required answers and its identity
fields. Any other key in a row, any key in a note's entry beside `stem` and `codes`, and any
top-level key beside `pairs` is ignored and not counted as unread. A non-object row or a duplicate
subject is counted as unread. The Writer self-grade record has the same shape and the same grader.

**The specificity second reader loses a remark the same way.** `specificity_scan.load_second_read_record`
and `_record_problem` ignore extra keys at every level of that record. Its `about` field is checked
only for being nonempty, is never graded, and appears only in private `--show` output, so it is the
easiest place for a remark to disappear. This reader is blind to the notes: it receives code
numbers and nothing else.

**The other clinical records do not lose a remark this way, or are not reader judgments.** The CPT
book-page record (`cpt-rendered-pages.json`) ignores extra keys, but it is a transcription of a
page. The CPT E/M sheet's two transcripts already refuse an extra line, since the two bodies must
agree exactly. The `batch-shift` correction handoff reruns a command and writes no record.

**Nothing on the clinical approval path reads a remark.** `approval_record.approve` collects reader
remarks only for `reader_remarks.SCOPED_SKILLS`, the five coursework skills; for `batch-shift` and
`clinical-note` the stored remark list is always empty. `approval_record.prepare` refuses any
skill outside that set. `icd10-cpt` has no approval of its own: its worksheet rides on the note's
approval and submission key.

**The shared instructions already point clinical readers at a channel they do not have.** Every
clinical second reader is told to read `skills/_shared/reference/sourcing.md` first. Its remark
section tells a reader to write `REMARK:` lines and tells the orchestrator to call
`approval_record.prepare`, which refuses the clinical skills.

**#1591's 2026-10-07 comment is a different defect.** There the coordinator overruled the reader in
a retry brief and the readers wrote that overrule into their own answers. That is a missing place
for a coordinator's overrule, not a reader's remark, and it stays on #1591.

## Ruling 1 — the coding readers get a remark place

The descriptor-agreement reader and the specificity second reader may write a reader remark: a
problem noticed outside the question asked, written beside the answers and never changing them.
This completes ADR 0330 ruling 6's routing rather than overturning it.

Extending only an unread count, with no legal place for a remark, was declined again for ADR 0330
ruling 6's reason: a reader with nowhere to speak learns to say nothing. Leaving the records as they
are was declined because it keeps the Module 10 path open on every coded encounter.

## Ruling 2 — a remark is a list beside the answers it does not change

In the agreement read, each note's entry carries a `remarks` list of nonempty strings, empty when
there are none. A remark about one code names that code in its sentence; a remark about no given
code, such as a documented problem with no code at all, still has a home. Because the specificity
reader never sees a note, its record carries one top-level `remarks` list for the whole read, and
each remark names its code. Both readers' briefs say a remark goes there and nowhere else. A remark
survives a retry: a replacement record keeps the remarks of the record it replaces, as
`sourcing.md` already requires for coursework.

A remark field on each code row was declined because the most valuable outside catch belongs to no
code the reader was given. Both a note list and a row field were declined as two places to read and
grade with no difference at the go-ahead. One list for a whole shift's agreement read was declined
because a remark would lose which patient it is about unless the reader remembered to say so.

## Ruling 3 — remarks are shown in their own block beside the Review sheet

Every coding reader remark from the run appears, numbered, in a `READER REMARKS` block in the chat
beside `PRE-APPROVAL PATIENT QUESTIONS` and `REPAIRS`, with either what was changed or a proposal
to leave it as is. It is never written into the Review sheet. The same block precedes a standalone
note's go-ahead. An `icd10-cpt` run's remarks ride on the approval of the note its worksheet
belongs to. The approval step refuses unless the whole block appeared in the chat between the last
source change and the clinician's reply, by the transcript check ADR 0330 ruling 2 uses.

Writing remarks into the Review sheet was declined because that document's content is what the
approval locks, so a fix would change the artifact carrying its own remark, and a standalone note
has no Review sheet. Listing remarks inside `PRE-APPROVAL PATIENT QUESTIONS` was declined because
that block can be delegated, which would let a remark be waved through by someone other than the
clinician.

## Ruling 4 — leaving a remark needs the clinician's own word, never a delegate's

A proposal to leave a coding remark as is stands only when the clinician's own reply names it, by
its number or by an explicit phrase covering all of them, as ADR 0330 ruling 3 requires for
coursework. A bare approval with any leave proposal unanswered is refused, and the refusal names the
open remarks. **A delegate never answers a leave proposal**, so it is outside the question kinds
[ADR 0309](0309-a-delegated-answer-never-decides-what-a-written-rule-already-settles-and-a-missing-bmi-code-is-refused.md)
lets a delegate answer; a delegated, unattended shift therefore stops at the go-ahead while a leave
proposal is open. A fixed remark needs nothing beyond the clinician's ordinary approval of the
changed note. The approval record keeps each remark with its outcome.

Letting a delegate answer a leave proposal was declined because a known problem could then reach
Medatrax without the clinician ever seeing it. Letting a general approval cover leave proposals was
declined for ADR 0330 ruling 3's reason.

## Ruling 5 — an unexpected entry in either record is unread

Once both records admit their `remarks` list, any other unexpected key, whether in the whole file,
a note's entry, or a code row, counts toward that record's unread remainder, so the grade stays at
exit 2 and names the record until the entry is moved into remarks or removed. This lands in the same
change as the remarks list, so a reader always has a legal place for a stray remark. A remark
written inside a free-text answer, such as the specificity `about` field or the agreement
`threshold` field, cannot be told from ordinary text; that limit is declared beside each grader
rather than closed. The Writer self-grade record shares the agreement grader's shape rule but has no
remarks list, because the writer fixes its own work rather than remarking on it.

Counting an unexpected key as a finding, as the voice reader's record does, was declined because a
layout slip would read as a defect in the clinician's coding and refuse the approval outright.
Continuing to ignore unexpected keys was declined for ADR 0330 ruling 5's reason.

## Ruling 6 — scope

Rulings 1 through 5 apply to the descriptor-agreement reader and the specificity second reader in
`icd10-cpt`, `batch-shift`, and `clinical-note`. The Writer self-grade record, the CPT book-page
record, and the CPT E/M sheet are outside them.

Limiting the change to the agreement reader, as #1702 was filed, was declined because the
specificity reader has the same hole and `sourcing.md` already tells it to write remarks that
nothing reads. Adding the CPT book-page record was declined because it is a transcription job, and
a remark about the page belongs with the agreement reader that reads it.

## What the build changes

- `skills/_shared/reference/sourcing.md`: a clinical clause routing the two coding readers'
  remarks to their record's `remarks` list and the clinical go-ahead block, replacing the
  coursework-only instruction for those readers.
- `tools/anchor_scan.py`: `AGREEMENT_READER_INSTRUCTIONS` names the per-note `remarks` list and the
  placement rule; `_grade_agreement` reads and returns remarks and counts every other unexpected key
  as unread, with the free-text limit declared.
- `tools/specificity_scan.py`: the second reader's brief and record admit the top-level `remarks`
  list; the loader returns remarks and counts every other unexpected key as unread, with the
  `about` limit declared.
- `tools/approval_record.py` and `tools/reader_remarks.py`: the `batch-shift` and `clinical-note`
  approval collects the run's coding remarks, refuses unless the `READER REMARKS` block appeared
  before the reply, refuses a bare approval with an unanswered leave proposal and names the open
  remarks, refuses a leave answered only by a delegated reply, and stores each remark with its
  outcome.
- `skills/icd10-cpt/SKILL.md`, `skills/batch-shift/SKILL.md`, and `skills/clinical-note/SKILL.md`:
  the record shapes and the `READER REMARKS` block at each go-ahead.
- `reference/completion-check-starts.tsv`: a start-date row for every new check and refusal
  above, under ADR 0346 ruling 4.
- Tests that drive each refusal through the public approval seam and that an unexpected key in each
  record now counts as unread.

## What this does not reach

- **Whether a reader notices an outside problem at all**, and **whether a fix resolves its
  remark**: ADR 0330's limits, unchanged.
- **A remark hidden inside a free-text answer**: ruling 5's declared limit.
- **Runs approved before this change**: **corrected 2026-10-17, the day this record merged.** It
  first said this was an open adoption question routed by ADR 0310 to
  [#1558](https://github.com/mshamblin5150-code/clinical-skills/issues/1558). #1558 had already
  closed:
  [ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md)
  freezes a posted item's clean terminal grade, and its ruling 4 gives every later completion check
  a start date, so earlier work reports `not graded` on it. This record's checks take those start
  dates, as the build list now says.
- **The coordinator's overrule of a reader**: #1591.
- **Whether the clinical go-ahead shows the grader's coverage lines**: ADR 0330 ruling 4 has no
  clinical counterpart, and the clinical approval stores those lines without checking that they
  were shown. That is separate from remarks and is filed as
  [#1845](https://github.com/mshamblin5150-code/clinical-skills/issues/1845).
