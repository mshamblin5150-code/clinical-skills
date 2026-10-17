# A cause the review's reader cannot see is marked unverified and lands only on a grilling ticket

[#1759](https://github.com/mshamblin5150-code/clinical-skills/issues/1759) was filed from the
grilling of [#1565](https://github.com/mshamblin5150-code/clinical-skills/issues/1565), which found
that ticket's after-action review had filed the wrong cause. In the NUR 5042 M11
`course-assignment` run (2026-10-04), `research_ledger.py`'s `undated-reference` row refused three
plain `(n.d.)` references that had no reasoned `RECENCY`. The agent then wrote that the grader
*"evidently doesn't parse some of my lettered years"*. Its next command printed the findings, which
disproved the guess, and it fixed them correctly. The review's reader classified the correction
from the agent's sentence, and #1565 was filed asking for lettered-year forms nobody had broken.
The clinician ruled every point below on 2026-10-17 against `main` at `ec4de36e`, where the
freshness gate read `FRESH`. **Nothing is built here; this is the record the build reads.**

## Read before ruling

**The reader could not have caught it.** `aar_scan.py --extract` keeps a tool call as its name
and a tool result as the tool's name plus `completed`. The command text and the output body are
both dropped. So the extract held the agent's explanation of the grader's output and not the
output itself.

**The declared limits named a neighbor, not this.** `aar_scan.DECLARED_LIMITS` already carries
*tool-result-only correction*: a correction that lived only in a tool's output. Here the correction
was in the extract. The agent was refused and changed course, both visible. Only its *cause* rested
on narration the reader could not check.

**The cost so far was a mis-aimed ticket, and a grilling caught it.** #1565's grilling reread the
transcript and corrected the ticket before anything was built. A ticket labeled `ready-for-agent`
would have had no such step before an unattended build.

**The grader can already open what was published.** To accept a `tracker-ticket` or `skill-file`
landing, `_successful_gh_call` finds the successful `gh` command that printed the landing address in
the raw transcripts named by the extract. That command's text names the `--body-file` it published,
and `skills/aar/SKILL.md` step 3 requires that file to sit under `<run-directory>/aar/publications/`.

## Ruling 1 — mark the cause, do not verify it or widen the extract

The review declares this blind spot and flags each case. It does not carry tool output into the
extract, and it does not require the orchestrator to check the cause before landing. Declaring the
limit alone was declined because an unattended build could act on a guess. An orchestrator check
was declined because the context that erred would grade its own diagnosis, the self-grading ADR
0109 ruling 2 exists to prevent, and a cheap grade could show only that a check was recorded.
Carrying tool output was declined because those bodies often hold patient material, are far larger
than the current extract, and would need a rule for which ones to keep.

## Ruling 2 — what raises the flag

The reader flags a correction whose cause rests on an agent's explanation, by the main agent or by a
subagent, of a tool output the extract does not carry, when no entry from anyone other than that
agent backs it up. A backing entry is the clinician's words, a different subagent's result, or a
grader's finding relayed through a notification. The same agent repeating or quoting itself does not
count, because a misquote would be trusted. The clinician's account of what he saw does not raise
the flag: his words are first-hand evidence. Neither does an agent's account of its own reasoning,
which hides no output. A cause asserted only by the party in error about anything was declined as
too noisy. Most corrections arrive with the erring agent's own account of why, and a flag that
appears on most records stops being read. Flagging every correction a tool made was declined because
it would flag many plain causes and miss a subagent's narration.

## Ruling 3 — every correction carries a cause line, and the grader counts it

Every correction record carries `CAUSE: shown - <entry>`, naming the extract entry the cause rests
on, or `CAUSE: unverified - <entry>`, naming the agent explanation it rests on. The classifier's
return supplies it. For rounds extracted after the build's cutoff, the grader refuses a correction
whose line is missing or malformed. Every report prints the unverified count for each round.
Writing the line only on flagged corrections was declined because a forgotten flag would read
exactly like a checked one, the reasoning of ADR 0381 ruling 2. A bare `CAUSE: shown` was declined
because a verdict with no pointer is the unsupported shape the grader already refuses for a
sustain.

## Ruling 4 — an unverified cause lands only on a ticket

A correction whose cause is unverified lands only as a `tracker-ticket` or a `skill-file`
disposition. The grader refuses one landed as a `memory-write` or a `check`. A ticket is grilled or
built later, and a skill-file diff waits for the clinician's ruling, so both pass the cause to a
person before anything acts on it. A memory loads into every later session as soon as it is saved,
and a check is built inside the review itself, so neither has a later reading step. Had #1565's
cause landed as a check, the suite would have gained a test for something that was never broken.
Landing anywhere with the warning carried along was declined because a memory saying "cause
unverified" still steers every session that loads it. Refusing to land until verified was declined
because it brings back ruling 1's declined check and blocks the review from finishing.

The flag concerns the cause, not the event. A memory or check about the agent's conduct that rests
on an event the extract shows has a `shown` cause and may land anywhere.

## Ruling 5 — the orchestrator may make a cause unverified, never shown

The orchestrator may change the classifier's `shown` to `unverified` with a reason. It may never
change `unverified` to `shown`. `shown` names an extract entry that backs the cause. The
orchestrator's reading of a raw transcript is not an extract entry, and it is the context whose
explanation is in doubt. ADR 0109 ruling 8 stands for every verdict it covers: this line is a
pointer whose `shown` value is a fact about the extract, so writing it from outside the extract would
misstate that fact rather than overrule a judgment. The orchestrator may write what it found in the
raw output into the ticket body. An overrule in both directions under ruling 8 was declined because
it would reopen unattended landings on a cause only the erring context had vouched for. An overrule
that cites the raw tool-call id was declined because the grader could prove only that the output
exists, not that it supports the cause.

## Ruling 6 — the ticket says so, and a new ticket is filed for grilling

A ticket body landing an unverified cause carries this sentence directly under its `Filed from:`
line:

```text
**Cause unverified:** the review's reader could not see the tool output this cause rests on; reread the run's transcript before building on it.
```

A new ticket is filed with `grilling` and never `ready-for-agent`, under `CLAUDE.md`'s rule that a
ticket with a decision still open never carries the label promising an unattended build. A landing
made as a comment on an existing ticket carries the sentence only, because that command sets no
labels. For each unverified correction, the grader opens the `--body-file` named by the `gh`
command that printed the landing address and requires the sentence there. On a create command it
also requires `grilling` and refuses `ready-for-agent`. A body passed inline rather than from a file
fails, which costs nothing: step 3 already requires publishing from a file. The sentence alone,
graded or not, was declined because an unattended build reads a ticket's label before its body.

## Ruling 7 — a reversal candidate gains `not shown`

Under ADR 0381 ruling 3, the reader answers each of the orchestrator's **reversal candidates** with
the entry of the correction it became, or with `not a correction` and a reason. ADR 0381 ruling 6
provided that a state this ticket added would join that answer set. The cause flag sits on the
correction, so a candidate that becomes a correction already carries its `CAUSE:` line. The answer
set instead gains `not shown - <reason>`. It is for a candidate whose reversal no extract entry
carries, typically one that happened only inside a tool output the orchestrator saw. The grader
counts it apart from `not a correction` and prints that count on every report. It lands nothing,
because ADR 0381 ruling 1 forbids a correction resting on the candidates entry. Folding it into
`not a correction` was declined because "it did not happen" and "the record cannot show it" would
share one answer and one count. Letting it land on an unverified cause was declined because the
orchestrator's own claim would become a correction's only evidence.

## Consequences

**A diagnosis the reader could not check reaches a person before anything is built on it.** The
event still lands, so the review still finishes.

**`aar_scan.DECLARED_LIMITS` gains an *unverified cause* row.** Its substance: a cause resting on an
agent's account of a tool output the extract drops is marked, not checked. The grader proves that
each correction carries a cause line, and that an unverified one lands only as a labeled ticket
carrying the sentence. It cannot prove that the reader recognized every such cause, or that a
`shown` entry supports the cause it names. The existing *tool-result-only correction* row stands
and now has the `not shown` count beside it.

**`CONTEXT.md` gains *Unverified cause*** under *Review*, beside **Correction**, and the
**Reversal candidate** entry gains its third answer.

**The build touches `tools/aar_scan.py`'s record grammar, grade, report, and declared limits, and
`skills/aar/SKILL.md` steps 2 to 4.** It shares the review record and grader with #1601's ADR 0381
build, and either may land first. If ADR 0381's candidates have not yet landed when this is built,
ruling 7 waits for them. Two mechanics are the build's to settle and are not ruled here: the cutoff
date's entry in `reference/completion-check-starts.tsv`, and how the grader reads `--body-file` out
of a command whose shape it does not recognize. That case refuses, consistent with ruling 6.

## What this does not reach

**A cause the reader wrongly marks `shown`.** The grader checks that the line names an entry, not
that the entry supports the cause.

**A narrated cause the reader does not notice.** The flag is a reading. A reader that misses one
writes `shown` against the agent's own sentence, and only a later reader of that record can see it.

**A comment landed on an existing `ready-for-agent` ticket.** It carries the sentence, but the
label it sits under still promises an unattended build.

**Whether a reread of the transcript would have found the true cause.** The ticket sends the work
to a person. It does not do the work.
