# A ticket states what filed it on an append-only line

[#1054](https://github.com/mshamblin5150-code/clinical-skills/issues/1054) was found while grilling
[#1047](https://github.com/mshamblin5150-code/clinical-skills/issues/1047).
[ADR 0166](0166-codebase-architecture-marks-a-lineage-by-descent.md) ruling 2 makes lineage membership a
matter of descent, and the only evidence of descent a sweep can read is the sentence in a ticket's body
saying where the ticket came from. A respec replaces the body, and nothing said to keep that sentence.

Grilled 2026-09-10 at `origin/main` `4eaf6be`. **Nine questions were ruled by the clinician one at a
time on that date.** Nothing is built here; this is the record the build reads. Every count below is a
dated measurement, not a current property of the tracker.

## Measured before ruling

### Respecs removed the line from closed tickets

#1054's body records nine closed `codebase-architecture` carriers whose oldest body revision had the
line and whose current body does not: #830, #832, #834, #835, #836, #837, #839, #843 and #874. Their
descent is now readable only through GitHub's GraphQL edit history, which `gh issue view` does not
show and no sweep reads.

### One open ticket had lost it

A read-only agent read the body edit history of all 60 open tickets on 2026-09-10, and none failed to
load. It sorted them into five classes that sum to 60:

| Class | Count |
| --- | ---: |
| never edited | 42 |
| edited, line still present | 13 |
| edited, line in the oldest revision and not the current one | 1 |
| edited, no line in the oldest revision either | 4 |
| history unreadable | 0 |

The one loss is #875, whose early revision says *"Found by an architecture review of the repo-wide
gate."* The parent re-derived it from #875's own edit history. Had the respec kept the line, the
current body would have matched `Found by` as the early revision does; it did not. Twelve open
tickets never had a line: #87, #596, #966, #979, #991, #993, #994, #1032, #1033, #1034, #1035 and
#1042. Most narrate a run or an after-action review rather than a parent ticket.

### Free wording defeats the instrument

The pattern #1054's first measurement used missed #1028's *"Found live during #866's grilling"*. The
agent's wider pattern missed #776's *"Ruled by the clinician on 2026-09-01 while grilling #401"*, which
it found only by eye. Each widening catches the phrasing that broke the last one and not the next.

### Keeping it costs one sentence

#1047's respec, written in the session that found this gap, kept *"Found by the tracker sweep out of
#873's grilling, 2026-09-10."* beneath its ruling paragraph. At `4eaf6be`, `docs/agents/issue-tracker.md`
does not contain the word *respec*.

### The enforcement surfaces already carry both bodies

`.github/workflows/tracker.yml` runs on `issues` `opened` and `edited`, and an edit event's
`changes.body.from` holds the body before the edit. `tools/tracker_publish_hook.py` already tells
`("issue", "create")` from `("issue", "edit")` and knows which record an edit targets. ADR 0166
ruling 5 declined a tool because comparing the label vocabulary needed a new harvest step. Holding
this line needs none.

## Ruled 2026-09-10

### 1. A respec keeps the line word for word

A rewritten body carries the line exactly as it was filed. The filing session is the only one that saw
where the ticket came from, so a paraphrase replaces that reading with the respecer's.

### 2. Every ticket is filed with one

The line names what produced the ticket, whatever that was: a ticket's grilling or build, a closing
sweep, an architecture review, a run or its after-action review, or the clinician's own request. A
ticket filed from a run says so, which is an answer. A body without the line is then a missing record,
never a statement that no parent ticket exists.

### 3. The line has a fixed label at a fixed position

The line is the first line after any Branch state block, or the body's first line when there is none.
It opens with the bold label `**Filed from:**`, and free text follows. A sweep or a hook finds it by
exact match, so deciding that it is missing takes no judgment of wording.

### 4. The label is Filed from and the term is Filed-from line

`CONTEXT.md` defines **Filed-from line**. *Provenance line* was refused because `CONTEXT.md` already
lists it under _Avoid_ for **Held declaration**. *Origin* was refused because `origin` is git's remote,
and the Branch state block directly above the line is verified against `origin/main`. *Descends from*
was refused because it names the judgment rather than the fact the judgment rests on.

### 5. Existing tickets change only where a line was lost

The build restores #875's line from its own edit history, word for word under the label. Every other
ticket filed before the cutoff keeps what it has until its next respec. That respec moves the existing
line under the label word for word, or, where the ticket never had one, writes a line marked as a
reconstruction. Closed tickets are untouched, on ADR 0166 ruling 7's footing.

### 6. The publish hook prevents and the tracker workflow reports

The hook refuses an issue create whose body lacks the label, and an issue edit that drops or alters an
existing `**Filed from:**` line. The workflow reports the same two shapes after publication, reading an
`opened` body and an `edited` event's `changes.body.from`, so it reaches publishers the hook does not.
Both apply to issues only; a pull request body keeps its own binding grammar. The edit refusal concerns
an existing line: an edit to a post-cutoff ticket that never got one is not refused for leaving it out,
and adding the line later is allowed.

### 7. The line is append-only

The line's text never changes and the line is never removed. A correction goes in the body's dated
footer, beside the original, as sweep corrections already do. There is no escape, so the hook's test
stays exact: the same line is present or it is not.

### 8. The after-action review names the skill and the date

`skills/aar/SKILL.md`, where it tells the review to write each ticket body under
`<run-directory>/aar/publications/`, requires the body to open with
`**Filed from:** the after-action review of a <skill> run, <YYYY-MM-DD>.` It names no run key and no
run directory, because the review's own publication gate exists to keep a run's material off the
tracker. The skill edit lands with the hook refusal; landed apart, every review ticket is refused.

### 9. The cutoff is a committed UTC timestamp, and the sweep reads it too

The build commits one UTC timestamp. The hook, the workflow and the sweep compare an issue's `createdAt`
against it. Once per sweep, the sweep lists open tickets created at or after the cutoff that lack the
label. That covers tickets filed between the constant being written and the merge, sessions on older
bases whose hook predates the rule, and any workflow report nobody acted on.

## Rejected options

- **A new fixed wording in place of the filed sentence.** Refused under ruling 1: it trades the filing
  session's reading for the respecer's.
- **No rule, with descent read from edit history.** Refused because nothing reads that history and
  `gh issue view` does not show it.
- **Provenance in a creation-time comment.** No respec overwrites a comment, but a sweep reads bodies
  and a comment is easy to miss among many.
- **A line only on tickets with a parent ticket.** Refused under ruling 2: a forgotten line and a
  parentless ticket would look the same.
- **Free wording, anywhere or at a fixed position.** Refused under ruling 3, on the measurement above.
- **Backfill every open ticket.** About 60 body edits, each racing concurrent sessions and each leaving
  a retained revision, for a label every older ticket reaches at its next respec anyway. A
  reconstruction for the twelve tickets that never had one would be the respecer's reading.
- **Change nothing already filed, #875 included.** Refused because #875 is the one real loss and a
  lineage carrier, and restoring it is one edit from its own history.
- **Prose and a sweep step alone.** Refused because #875 shows a respec dropping the line with nothing
  to stop it, which is [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what
  a written instruction cannot do is fail*.
- **The workflow alone, or the hook alone.** The workflow reports after GitHub has kept the damaged
  revision; the hook does not reach the web UI or another publisher.
- **A line that may change when the edit adds a correction footer.** Refused under ruling 7: the hook
  would have to judge whether a footer explains the change.
- **A separate skill-file ticket for the after-action review.** Refused under ruling 8.
- **An issue-number cutoff.** Pull requests share the number space, and the build cannot know the right
  number before merging either.

## Consequences

The build is: the two refusals in `tools/tracker_publish_hook.py`, the two reports run from
`.github/workflows/tracker.yml`, the committed cutoff, the rule and the sweep step in
`docs/agents/issue-tracker.md`, the edit to `skills/aar/SKILL.md`, and #875's restored line. #1054's
body carries the build spec.

## What this does not reach

- **Whether a line is true.** The hook and workflow check that the label is present and unchanged.
  Whether it names what actually produced the ticket is the filing session's judgment, as ADR 0166
  already says of descent.
- **Converting an older ticket's free-worded line.** Ruling 3 refused pattern matching, so nothing can
  recognize the old sentence in order to check that a respec moved it word for word.
- **The web UI and sessions on older bases.** Neither runs the new hook. The workflow reports their
  tickets after publication, and the sweep lists what it missed.
- **Tickets filed before the cutoff that never had a line.** Nothing reports them until a respec reaches
  them.
- **Closed tickets.** Ruling 5 leaves them as they are, so a closed ticket's body is not evidence of its
  descent in either direction.
