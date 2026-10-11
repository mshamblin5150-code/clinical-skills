# A classmate's order counts only for the patient the case presents and the clinician's own submission is a declared context place

**Measured at:** d1bdbaa31d1e52c24c34d9c1c4f5934e759e3a30

[#1493](https://github.com/mshamblin5150-code/clinical-skills/issues/1493) was filed from the
after-action review of a `discussion-reply` run (NUR 5144 Module 2) on 2026-10-01. Four corrections
in that sitting traced to skill instructions rather than to a tool. Grilled 2026-10-11 against
`main`, where the worktree contained the fetched `origin/main`; the clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The ticket's proposed wording contradicts the clinician's house style.** The ticket proposed
that step 1 treat *a conditional order* as no agreement. `skills/_shared/reference/style.md`
section 6 records that the clinician writes conditional orders as conditionals, not deferrals, and
quotes one of his: a prediction-score branch choosing enoxaparin or early ambulation. That is a real
order for the patient in front of him. In the Module 2 run the classmate's only drug order was
written for a hypothetical steadier patient, and no drug was named for the patient the case
presented. The defect was which patient the order served, not the word "if".

**Peer-critique reads a classmate's plan with no such rule either.** `skills/peer-critique/SKILL.md`
steps 1 and 2 read the classmate's whole case study, plan included, and say nothing about an order
written for another patient. `skills/_shared/reference/rubric.md` is already cited by both
`discussion-reply` and `peer-critique`, and already carries this repository's analysis beside the
distilled course spec.

**The "what you can add" column is written before any research runs.** `discussion-reply` step 1
fills it; step 2 builds the claim ledger, whose headings are written in question form. The Module 2
column stated a specimen-contamination mechanism as fact and credited it to the clinician's own
case study; research narrowed it to a different specimen type.

**The clinician's own submission was not an opened item, so nothing could compare against it.**
`skills/_shared/reference/sourcing.md` says the clinician's own reasoning needs no claim-heading pair
and remains subject to the project-context verdict, which the heading read judges against the items
the run opened. The Module 2 run had not opened the case study he posted on the same case, and one
draft word contradicted a threshold in it; only the orchestrator's reread caught it. The
project-context record already declares the project with a refused-without header,
`PROJECT-CONTEXT: <project> | none - <reason>`, parsed by `tools/project_context.py`.

**The fingerprint instruction fails on a Git Bash path and is copied six times.** The inline
`python -c "... from tools.file_digest import sha256 ..."` command, given a `/c/...` path, raises
`FileNotFoundError`, prints nothing, and exits 1; the run wrote that empty output as
`SUBMISSION-SHA256` and the grader refused it. The command appears once each in `course-assignment`,
`discussion-post`, `discussion-reply` and `peer-critique`, and twice in `practicum-case-study`.
`tools/file_digest.py` has no command line. `tools/tracker_publish_hook.py` already tries a Git Bash
`/c/...` path in its Windows spelling.

## Ruling 1 — an order counts only when it applies to the patient the case presents

An **Applicable order** is an order in a classmate's plan that applies to the patient the case
actually presents, including a conditional whose branches cover that patient. Only an applicable
order is what the classmate decided, and only it can be listed as something the clinician can agree
with. An order written for a hypothetical other patient, an order put off until later, and a plan
naming a treatment class with no drug, dose or duration are not applicable orders. The missing
treatment decision is itself a finding about the classmate's plan.

Setting aside every conditional was declined because it contradicts `style.md` and would charge a
classmate who wrote the clinician's own kind of order with deferring treatment. Requiring only a
quotation of the classmate's order was declined because the Module 2 ranking already held the
deciding fact a few lines away and listed the agreement anyway. The judgment of whether an order
applies stays a reading; no tool checks it.

## Ruling 2 — the rule lives once in the shared rubric reference

The rule is one short section of `skills/_shared/reference/rubric.md`, labeled as this
repository's reading rule rather than the course's words. `discussion-reply` step 1 and
`peer-critique` step 2 each point to it and restate none of it.

Discussion-reply alone was declined because peer-critique reads the same kind of plan with the same
exposure. Copying the sentence into both skills was declined because two prose copies drift and an
edit to one fails nothing.

## Ruling 3 — the "what you can add" column carries research questions

Each entry in `discussion-reply` step 1's fourth column is written as the question the reply would
research, not as its answer, so it feeds step 2's question-form claim headings unchanged. An entry
may credit the clinician ("your case study argued ...") only with a quotation from his submission.

A working-claim tag beside an asserted claim was declined because the assertion stays on the page
and a tag is easily read past. Leaving the column alone was declined because research checks a
claim's source and never whether the clinician said it.

## Ruling 4 — the clinician's own submission is a declared, opened context place

The project-context record gains one confirmed header line in all five coursework skills
(`course-assignment`, `discussion-post`, `discussion-reply`, `peer-critique`,
`practicum-case-study`):

```text
OWN-SUBMISSION: <path> | none - <reason>
```

It declares the clinician's **Own submission**, a submission he already handed in on the same board
or the same case as the work being drafted, or that none exists and why. `tools/project_context.py`
refuses a record without exactly one such line, refuses `none` without a reason, and refuses a
declared path that the record does not show opened as an item of a read place. The path names a
file holding the submitted text: the handed-in file, or the run's own capture of the posted entry.
The declared line is part of the confirmed header the record's digest covers.

An instruction in `discussion-reply` step 3 alone was declined because the Module 2 miss was a
skipped written step, and an ungraded shared instruction was declined for the same reason: a
skipped step and a run with no prior submission produce the same silence.

## Ruling 5 — one shared fingerprint command replaces the inline one

`tools/file_digest.py` gains a direct command, `python tools/file_digest.py <file>`, which prints
the lowercase SHA-256 of the file's raw bytes. It also tries a Git Bash `/c/...` path in its Windows
spelling, and exits 2 with a plain message, never empty output, when the file cannot be read. All
six skill sites call it in place of the inline `python -c` command.

A caveat copied into six places was declined because the next skill to copy the command would
inherit the trap. Having the grader write the fingerprint was declined because it would certify
whatever bytes happened to be present, defeating the record ADR 0288 keeps the grader refusing.

## Build checklist

- `skills/_shared/reference/rubric.md`: the applicable-order section, labeled as a reading rule.
- `skills/discussion-reply/SKILL.md` step 1: the pointer to that section for the third column, and
  the fourth column written as research questions with the quote-only attribution rule.
- `skills/peer-critique/SKILL.md` step 2: the pointer to the applicable-order section.
- `skills/_shared/reference/sourcing.md`: the `OWN-SUBMISSION` header line in the project-context
  record and what the gate refuses.
- `tools/project_context.py`: parse, require and canonicalize the line, and refuse a declared path
  not shown opened; tests through its public command for a missing line, a reasonless `none`, an
  unopened declared path, and a clean declared path.
- `tools/file_digest.py`: the direct command, calling `use_utf8` and `require_python_floor`, with
  tests for a relative path, a Git Bash path, and an unreadable file; the six skill sites switched
  to it; the `CLAUDE.md` console-codec correction naming the new direct command.
