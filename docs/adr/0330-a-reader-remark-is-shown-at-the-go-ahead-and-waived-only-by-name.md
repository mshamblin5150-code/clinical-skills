# A reader remark is shown at the go-ahead and waived only by name

**Measured at:** a302efdd337b424b695e5a8cef73d1b5ecbfe1bf

[#1501](https://github.com/mshamblin5150-code/clinical-skills/issues/1501) was filed from the
after-action review of a `course-assignment` run (NUR 5042 Module 10) on 2026-10-01. Two readers
added remarks beside passing verdicts. A refuter answered `stands` and said the draft should present
a statistic as another body's finding that the web primer reports. The final heading reader answered
`clean` and noted that the paper cited that finding only through the primer, with no APA
secondary-citation form. Both graders passed, the orchestrator told the clinician every check had
passed, and the paper was submitted carrying the defect. A second comment, filed from a
`discussion-reply` run on 2026-10-08, records the same failure in the summary step: twice in one
sitting the go-ahead summary left out an `unread remainder 1` that the grader had printed. The second
time, the orchestrator had traced that remainder minutes earlier. Grilled 2026-10-11 against `main`,
where the freshness gate read `FRESH`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The three reader records lose an extra remark in three different ways.** In
`tools/heading_read.py`, `read_records` skips any line inside a record that matches no field, and the
unread remainder counts only `## HEADING-READ` headings. A prose remark under `VERDICT: clean`
therefore reaches no grader and is not counted as unread. A `FINDINGS:` line under `clean` is
already graded as a reported finding, so the loss is specific to prose. The `REFUTATION:` field of a
`research_ledger.py` claim record takes `<keyword> - <reason>`, and its reason is checked for
substance and never read for meaning. The `tools/checks_ledger.py` `## CHECK:` record folds an
unrecognized line into the field above it, and a clean record on a substantiated row must carry
`FINDINGS:` saying what it walked, so a remark written there looks the same as the required text.

**Nothing carries a remark to the go-ahead.** `tools/approval_record.py` stores no remark, waiver,
or grader report in its item. `verify_shown_text` checks only that the approved Markdown's blocks
appeared in the chat, for the three skills in `SHOWN_TEXT_SKILLS`.

**The grader report reaches the clinician after the go-ahead, not before.** `approve` runs the
paired grader after the clinician has replied, and each coursework skill then says to show its
`pregrade_report`. So any coverage line the go-ahead request carried was the orchestrator's summary
from memory, which is the step the second comment records failing.

**`course-assignment` has its own approval path.** It is not in `approval_record.SKILLS`; it uses
`assignment_submission.stage`, whose `approval_surface` prints only the attachment count and
filenames.

**ADR 0318 fixes part of the request this extends.** Its ruling 3 requires the go-ahead in
`discussion-post`, `discussion-reply`, and `peer-critique` to show the complete text and reference
list, and its ruling 4 makes `approve` check that the text was shown. It says nothing about reader
remarks or grader coverage lines.

**"Advisory" already has a meaning here.** It names a check that prints and cannot refuse, which is
how CONTEXT.md's **Refusing check** entry and several tools use it. The reader-side thing needs a
different name.

## Ruling 1 — a verdict answers its own question, and anything else is a reader remark

A reader's verdict answers only the question that reader was asked. A problem the reader notices
outside that question is a **Reader remark**. It is written on its own `REMARK:` line in the
reader's record, in each record kind the coursework readers write, and it never changes the
verdict. In the voice reader's JSON record, which admits an exact key set, it is a remarks list
rather than a line. The visual readers' `rendered.md` records carry the same line. The reader
briefs say so, and say that a remark goes on that line and nowhere else.

Making every outside problem a `defect` was declined: a verdict would no longer mean that the asked
question failed, a half-formed worry would stop the run, and readers would learn to stay quiet about
anything outside their question rather than fail a check that passed. Listing remarks at the
go-ahead without grading them was declined because it rests on the orchestrator's summary, which is
the step the ticket's second comment records failing.

## Ruling 2 — every remark is shown at the go-ahead with its outcome

Every reader remark from the run appears in the go-ahead request, numbered, with either what was
changed in the draft or a proposal to leave it as is. The approval step refuses unless the whole list
appeared in the chat between the last source change and the clinician's reply, by the same
transcript check ADR 0318 ruling 4 uses for the draft text. The clinician's approval accepts the
fixes. The approval is recognized from his actual reply, so a word like "fire", "go", or "send it"
counts; this ruling adds no fixed phrase.

Letting the orchestrator mark a remark fixed on its own was declined because "fixed" would be
self-certified by the party that reported every check as passed. Requiring a fresh reader to reread
every fix before the go-ahead was declined because it adds a reader round per remark while the
clinician is already the last checkpoint; he can ask for a reread when a fix looks thin.

## Ruling 3 — leaving a remark needs the clinician's word for it

A proposal to leave a remark as is stands only when the clinician's reply names it, by its number
("leave 2") or by an explicit phrase covering all of them ("leave all of them"). A bare approval
with any leave proposal unanswered is refused, and the refusal names the remarks still unanswered.
The approval record keeps each remark with its outcome: fixed, or left on the clinician's word.

Letting one approval cover the leave proposals was declined because it is the Module 10 path with
the remark printed above it: a known defect still ships on a general "go". Forbidding leave
proposals at the go-ahead was declined because it adds a separate round trip for remarks that are
plainly right to leave.

## Ruling 4 — the grader runs before the ask, and its coverage lines are shown verbatim

The paired grader runs before the go-ahead request, and every **Coverage qualifier** it prints, such
as `unread remainder N` or a `not graded` row, appears in the request exactly as printed. The
approval step refuses unless those lines appeared in the chat before the clinician's reply. They are
shown to be read, not waived.

Turning each coverage line into a remark to be fixed or waived was declined: lines expected before
posting, such as the posted reading not yet graded, would need a waiver on every run, which trains a
"leave all" typed without reading. Adding an instruction not to drop them was declined because the
second comment records that instruction being broken twice in one sitting.

## Ruling 5 — an unrecognized line in a reader record is unread

A line inside a reader record that is neither a recognized field nor a `REMARK:` line counts toward
the record's unread remainder, so the grade stays at exit 2 and names the record until the line is
rewritten as a remark or removed. Where a record kind folds extra lines into the field above, or
where a remark could sit inside free text that is checked only for substance, the code cannot tell
a remark from ordinary text. That limit is declared beside the grader rather than closed, and the
brief's placement rule from ruling 1 is the only control there.

Leaving unrecognized lines skipped was declined because it keeps the exact Module 10 path open
whenever a reader ignores its brief. Treating every unrecognized line as a remark was declined
because formatting noise would become remarks to waive, and the record would stop enforcing its own
shape.

## Ruling 6 — the five coursework skills, including course-assignment

Rulings 1 through 5 apply to `course-assignment`, `discussion-post`, `discussion-reply`,
`peer-critique`, and `practicum-case-study`. `course-assignment` gains the same remark list and
coverage-line check in its own approval path.

Limiting the change to the four skills on the shared approval step was declined because it leaves
out the skill where the defect reached a submitted paper. Moving `course-assignment` onto the shared
approval step as part of this change was declined because it would tie this ruling to its upload
staging, filename binding, and page-image review; that move, if wanted, is a separate ticket.
The clinician first ruled the clinical skills out on the stated ground that they had no reader
record that could lose a remark. The closing sweep showed that ground false: `icd10-cpt`, and
`batch-shift` through it, run a blind descriptor-agreement reader whose JSON rows are read for
their required fields, and any other key is ignored without being counted
(`tools/anchor_scan.py`). Told this, the clinician kept the scope and routed that reader to its own
grilling on [#1702](https://github.com/mshamblin5150-code/clinical-skills/issues/1702), because its
go-ahead is the Review sheet, which this session did not examine. Extending only ruling 5 there was
declined because a reader with no legal place for a remark would learn to say nothing.

## Ruling 7 — the term is Reader remark

The glossary term is **Reader remark**, written `REMARK:` in a record. "Advisory" was declined
because it already names a check that cannot refuse, "side finding" because a finding here is a
graded defect that sets a status, and "observation" because the late gate already counts waived
observations.

## What the build changes

- `skills/_shared/reference/sourcing.md`: the `REMARK:` line in the heading-read and refutation
  record shapes, the rule that a verdict answers only its own question, and the placement rule.
- `skills/practicum-case-study/SKILL.md`: the same line in the `## CHECK:` record shape.
- `tools/heading_read.py`, `tools/research_ledger.py`, and `tools/checks_ledger.py`: read `REMARK:`
  lines, return them to the completion graders, and, where a record kind skips unrecognized lines,
  count them as unread under ruling 5, with the declared limit for the kinds that cannot.
  `checks_ledger.py` also drops a line between a `## CHECK:` heading and its first field; that
  line counts as unread too. The count covers only the records the caller binds, so a shared
  heading-read file does not charge another artifact's record to this run; #1557 needs the same
  scoping for headings.
- The visual readers' `rendered.md` record shapes and their graders in `tools/deck_scan.py` and
  `tools/assignment_docx_scan.py`: the same `REMARK:` line, returned the same way.
- `tools/voice_read.py`: a remarks list in the reader's `voice-read.json` key set, returned the same
  way; today an extra key there is a finding, so a remark has nowhere to go.
- `tools/approval_record.py`: run the paired grader before the ask; refuse approval unless every
  reader remark and every coverage line appeared before the reply; refuse a bare approval with an
  unanswered leave proposal and name the open remarks; store each remark with its outcome.
- `tools/assignment_submission.py`: the same remark list, outcome check, and coverage-line check in
  the `course-assignment` approval path.
- The go-ahead steps of the five coursework skills: show the numbered remark list and the grader's
  coverage lines before the question.
- Tests that drive each refusal through the public approval seams and that a prose line in a
  heading-read record now counts as unread.

## What this does not reach

- **Whether a reader notices an outside problem at all.** A reader that sees nothing writes no
  remark, and nothing grades what it missed.
- **Whether a fix resolves its remark.** The clinician sees the change at the go-ahead; no grader
  compares the remark with the fix.
- **A remark hidden inside free text.** Ruling 5's declared limit stands for the record kinds that
  fold lines or check a reason only for substance.
- **Runs graded before this change.** Whether an already-posted run is re-graded under rulings 2
  through 5 is an adoption question, routed by ADR 0310 to
  [#1558](https://github.com/mshamblin5150-code/clinical-skills/issues/1558).
- **The coding agreement reader.** Ruling 6 routes it to #1702.
- **The Module 10 paper already submitted.** Its resubmission is a one-time fix outside this record.
