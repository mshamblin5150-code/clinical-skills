# A delegated answer names its note sections and a second reader checks it before the go-ahead quotes it

**Measured at:** 31b048a1a6dad7d1b01fc2da89db67caf00902ad

[#1813](https://github.com/mshamblin5150-code/clinical-skills/issues/1813) was filed from the
after-action review of a `batch-shift` run (NUR5144 clinic shift). The clinician
delegated the shift's open questions and approved the Review sheet without reading it. The
go-ahead message summarized how each delegated question was settled, and for two notes it
described what the shorthand recorded rather than what the finished note said: one summary read as
antibiotics only over a Plan recommending incision and drainage, and another read as no epinephrine
over a Plan prescribing an auto-injector. The orchestrator found both during portal entry, held the
two notes, and the clinician ruled to keep them as written. Nothing posted on the wrong description,
but the approval had rested on it. Grilled 2026-10-18 against `main` at the commit above, where the
freshness gate read `FRESH`. The clinician ruled every point below in that session, one question at
a time. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The text the clinician read is recorded nowhere.** `delegated-answers.md` holds three fields per
record, `## QUESTION:`, `RULE:` and `ANSWER:`, and `delegated_answers.grade_text` checks only that
`ANSWER:` is present and non-empty. The go-ahead message is new prose written in chat;
`delegated_answers.DECLARED_LIMITS` already says it is a message "which no file records". Both
mismatches arose in that prose, by paraphrase.

**Nothing ties an answer to a note.** The record grammar carries no note, stem, or section field,
so an answer names its note only where its free prose happens to.

**The delegable kinds do not include treatment.** ADR 0309 ruling 1 limits a delegate to the
`PRE-APPROVAL PATIENT QUESTIONS` kinds: an age or sex disagreement, an unresolved multiple-row
match, a combination-product allergy culprit, and a level-changing E/M question. The two treatment
questions in this run were settled under ruling 1 or 2 and recorded in the same file, so "which
answers describe treatment" is a line no field draws.

**The only independent reader in a shift checks codes.** The step-6 descriptor-agreement read
(`agreement-reader/read.json`, graded by `anchor_scan.py --agreement-read`) compares codes with note
wording and runs before the pre-approval questions are settled. The non-authoring `entry_copy.py
--check` handoff writes no record. The ticket's "existing pre-approval walk" does not exist in
`batch-shift`.

**A transcript check for shown text already exists.** `approval_record.verify_shown_text` confirms
that approved text appeared in main-session assistant messages between the sources' last change and
the clinician's reply, for `approval_record.SHOWN_TEXT_SKILLS` only; `batch-shift` and
`clinical-note` are outside it.

## Ruling 1 — the go-ahead quotes the recorded answers, word for word

The check applies to the `ANSWER:` lines in `delegated-answers.md`, not to a chat summary. The
go-ahead message quotes every recorded answer line exactly rather than summarizing it, so the text
the clinician reads is the text that was checked. Checking the go-ahead message itself was declined
because it exists nowhere on disk and no grader could confirm the check covered the message sent.
Checking both was declined because the summary would still drift from the record wherever it
paraphrased.

## Ruling 2 — every answer names its note and the sections it rests on

Each record carries two more lines: the note it concerns, or `shift` for a question about no single
note, and the note sections its answer rests on. `delegated_answers.py` confirms mechanically that
the named note is in the run and each named section is a section that note carries. Requiring the
pointers only for answers about treatment was declined because the orchestrator, the author whose
description failed, would choose which answers are checked, and an untagged answer would skip the
check invisibly. Requiring sections only where an answer describes note content was declined on the
same ground.

## Ruling 3 — a dedicated second reader checks each answer against its sections

A context that wrote neither the notes nor the answers receives each answer line and the current
text of the sections it names, and nothing else. It writes one verdict per answer: agrees, or does
not, with the words that disagree. Adding the job to the step-6 descriptor-agreement reader was
declined: that read runs before the questions are settled and its brief is deliberately narrow.
Giving it to the `entry_copy.py --check` handoff was declined because that context saves nothing a
grader could confirm.

## Ruling 4 — a disagreement holds the go-ahead until every answer agrees

The orchestrator corrects whichever side is wrong. A wrong description is a rewritten answer line;
a wrong note is corrected through standing rule 6's repair route and appears in the `REPAIRS` block
the go-ahead already shows. A fresh reader reads every changed answer again. The completion grade
refuses a run in which any answer's latest verdict is a disagreement. Putting the disagreement to
the clinician as an open question was declined because he delegated the questions and a wrong
description changes no clinical content; a printed warning was declined because a clinician who
approves without reading the sheet does not read it either.

## Ruling 5 — no second context is incomplete coverage, never clean

Where no second context can be started, the run records that declaration in place of verdicts. The
completion grade reads incomplete (exit 2), and the go-ahead message states plainly that the
delegated answers were not independently checked and names the sections each rests on. This is the
voice read's arrangement for the same gap. A self-check by the orchestrator was declined because a
self-read is not a second read, and refusing delegation in such a harness was declined because it
makes delegation unusable there.

## Ruling 6 — the check covers both note skills

The rule is written in `skills/clinical-note/SKILL.md`'s delegated-answer paragraph, which
`skills/batch-shift/SKILL.md` already adopts, and the check lives in `delegated_answers.py`'s shared
completion gate, which both `filled_vitals_census.py` and `differential_scan.py` call at
`--submission`. A `batch-shift`-only rule was declined because one record would then follow two
rules and the standalone note's approval would rest on unchecked descriptions.

## Ruling 7 — the reader's record is `answer-reader/read.json`

The verdicts, or the no-second-context declaration, go in `<run>/answer-reader/read.json`,
following the descriptor-agreement reader's layout. The record carries a fingerprint of
`delegated-answers.md` and of each section text read. An answer with no verdict, or whose verdict's
fingerprints no longer match the current answer file or section text, is unread and enters the
shared unread remainder; a current disagreement is a finding. ADR 0406 ruling 1's run-record list is
unchanged, since the record is neither Markdown nor top-level. A top-level `answer-check.md` was
declined because it grows that list and needs grammar parsing, and a verdict line in
`delegated-answers.md` was declined because the reader would write into the author's file and a
changed answer and a stale verdict would share one set of bytes.

## Ruling 8 — the approval record confirms the quote from the transcript

`approval_record` extends its shown-text transcript check to the `ANSWER:` lines of a
`batch-shift` or `clinical-note` run that has a `delegated-answers.md`. An answer line absent from
the window between the record's last change and the clinician's reply is a finding; an unreadable
transcript records as unverified, as it does today. Leaving the quote as a written instruction was
declined because it would rest the link between what was checked and what was read on the author
following an instruction, which this run showed is the failure. `verify_shown_text`'s recognition
ceiling applies unchanged: it proves the words were shown, not that they were read.

## Ruling 9 — older runs are not graded

Each new check takes a row in `reference/completion-check-starts.tsv` compared with the item's
approval time, so a run approved before the build, including the shift that filed this ticket, reads `not
graded` on these rows rather than failing over records it was never asked to write.

## Build checklist

- `tools/delegated_answers.py`: parse the note and sections lines; confirm the note is in the run
  and each section is one that note carries; read `answer-reader/read.json`, its fingerprints, and
  the no-second-context declaration; report verdicts, unread answers, and disagreements; replace
  the "naming at the go-ahead" row of `DECLARED_LIMITS` and add the reader's reading boundary.
- `tools/approval_record.py`: confirm every recorded `ANSWER:` line appears in the shown-text
  window for `batch-shift` and `clinical-note` runs with a delegated-answer record.
- `reference/completion-check-starts.tsv`: one row per new check, compared with approval.
- `skills/clinical-note/SKILL.md`: the delegated-answer paragraph states the two new lines, the
  reader brief and its record, the hold on a disagreement, the no-second-context wording, and that
  the go-ahead quotes every answer line. `skills/batch-shift/SKILL.md` keeps adopting it by
  reference and its step-7 go-ahead list names the quoted answers.
- `tools/test_delegated_answers.py` and `tools/test_approval_record.py`: drive the gate and the
  approval record through their public seams, including a planted answer that describes a section
  the note contradicts, a stale fingerprint, and a missing shown line.

## What this record does not reach

- **Whether the reader judged correctly.** The record proves a non-authoring verdict exists for the
  current bytes; whether an `agrees` is right remains a reading.
- **Whether an answer obeys the rule it quotes.** ADR 0309's limit stands: the reader compares an
  answer with its note, not with its rule.
- **Whether the clinician read the quoted answers.** Ruling 8 proves they were shown.
- **An unrecorded delegation.** A run that writes no `delegated-answers.md` still reads as having
  none, as `delegated_answers.DECLARED_LIMITS` already states.
