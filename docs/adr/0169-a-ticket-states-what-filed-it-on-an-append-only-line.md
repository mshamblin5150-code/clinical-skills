# A ticket states what filed it on an append-only line

[#1054](https://github.com/mshamblin5150-code/clinical-skills/issues/1054) was found while grilling
[#1047](https://github.com/mshamblin5150-code/clinical-skills/issues/1047).
[ADR 0166](0166-codebase-architecture-marks-a-lineage-by-descent.md) ruling 2 makes lineage membership a
matter of descent, and the only evidence of descent a sweep can read is the sentence in a ticket's body
saying where the ticket came from. A respec replaces the body, and nothing said to keep that sentence.

Grilled 2026-09-10 at `origin/main` `4eaf6be`. **Fourteen questions were ruled by the clinician one at
a time on that date.** The first nine produced rulings 1 to 9. The session's own tracker sweep then read
all 60 open tickets against that draft before it merged, and found gaps in rulings 3, 5, 7 and 8 and a
writer the rules had not considered. Four more questions amended rulings 5, 7 and 8 and added ruling 10.
A fourteenth amended ruling 5 again after #875 closed while the record was waiting to merge. The sweep's
corrections of fact are folded into the text below. Nothing is built here; this is the record the build
reads. Every count below is a dated measurement, not a current property of the tracker.

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
current body would have matched `Found by` as the early revision does; it did not. #875 then closed at
2026-09-11T01:23Z UTC, when PR #1063 merged its build, before this record merged.

The agent classed twelve open tickets as never having had a line: #87, #596, #966, #979, #991, #993,
#994, #1032, #1033, #1034, #1035 and #1042. Most narrate a run or an after-action review rather than a
parent ticket. *Two of the twelve are wording judgments, not clear absences: never-edited #979 says
"This is that boundary filed" of an ADR 0152 ruling, and never-edited #994 says it was "Filed separately
rather than folded in" from #772's work. Found by the session's sweep.*

### Free wording defeats the instrument

The pattern #1054's first measurement used missed #1028's *"Found live during #866's grilling"*. The
agent's wider pattern missed #776's *"Ruled by the clinician on 2026-09-01 while grilling #401"*, which
it found only by eye. Each widening catches the phrasing that broke the last one and not the next.

### Keeping it costs one sentence

#1047's respec, written in the session that found this gap, kept *"Found by the tracker sweep out of
#873's grilling, 2026-09-10."* beneath its ruling paragraph. At `4eaf6be`, `docs/agents/issue-tracker.md`
does not contain the word *respec*.

### The enforcement surfaces can reach both bodies

`.github/workflows/tracker.yml` runs on `issues` `opened` and `edited`, and an edit event's
`changes.body.from` holds the body before the edit. `tools/tracker_publish_hook.py` already tells
`("issue", "create")` from `("issue", "edit")` and knows which record an edit targets. Its readback
fetches the cited record's body, but `tools/tracker_readback.py` reduces it to a length, and that
module's `NOT_REACHED` says the body text is never exposed. So the edit refusal reads the text itself.
ADR 0166 ruling 5 declined a tool because comparing the label vocabulary needed a new harvest step.
Holding this line needs none.

### What the sweep found against the first draft

- **Another block must open a body.** `docs/agents/issue-tracker.md` has record-level qualifiers that
  share the first line, and `tracker_branch_scope.CITED_RECORD_SCOPE` is anchored at the start of the
  text, as `BRANCH_SCOPE` is. On a draft body citing a path not on `main`, a Filed-from line above a
  `Cited record state` block graded status 1, and below it status 0; a control with a resolved path
  graded 0. #920 and #921 open with that block today.
- **Old origin sentences share a paragraph.** In each of the 13 tickets one reader checked, the origin
  sentence sits with one to three other sentences. #1004's is followed by *"Freshness gate `FRESH` before
  reading and before publishing."*
- **Sweeps also correct at the top.** #948 carries a `Corrected 2026-09-10` paragraph directly after its
  Branch state block, above its origin sentence, besides a footer correction.
- **The review skill's gate is narrower than the first draft said.** `skills/aar/SKILL.md` forbids
  reproducing *"the patient, classmate, preceptor, site, faculty, or board material."* A course and
  module are not in that list, and the nine review tickets #1014 to #1022 already name both.
- **The implementation map writes whole bodies.** `tools/implementation_map.py`'s `render(state, live,
  snapshot)` takes no current body, and `publish_body` replaces #596's body with its output. A line added
  to #596 would be erased by the next publish. The map's body calls itself *"a coordination artifact, not
  an implementation ticket"* and carries an exact producer stamp that `tools/map_scan.py` grades.
- **The hook's manual mode grades no route.** `python tools/tracker_publish_hook.py --text` analyzes a
  body with no issue and no route, so a refusal tied to the create route would not run there.

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

The line is the first line after any record-level scope block, which today means a Branch state or
Cited record state block, or the body's first line when there is none. It opens with the bold label
`**Filed from:**`, and free text follows. A sweep or a hook finds it by exact match, so deciding that it
is missing takes no judgment of wording. *Amended before merge: the first draft named only the Branch
state block, and the sweep's measurement above showed the other qualifier must also stay first.*

### 4. The label is Filed from and the term is Filed-from line

`CONTEXT.md` defines **Filed-from line**. *Provenance line* was refused because `CONTEXT.md` already
lists it under _Avoid_ for **Held declaration**. *Origin* was refused because `origin` is git's remote,
and a scope block directly above the line can be verified against `origin/main`. *Descends from* was
refused because it names the judgment rather than the fact the judgment rests on.

### 5. No existing ticket's body is edited to add the line

A ticket filed before the cutoff keeps what it has until its next respec. That respec moves the origin
sentence alone under the label, word for word, and leaves any other sentences of its paragraph in the
body as they were. Where a ticket never had one, the respec writes a line marked as a reconstruction.
Closed tickets are untouched, on ADR 0166 ruling 7's footing, and #875 is among them.

*Amended twice before merge.* The first draft said "the existing line", which the sweep found is usually
a sentence inside a longer paragraph. The second draft had the build restore #875's lost line, because
#875 was the one open ticket that had lost it. #875 closed before this record merged, which put it in
the same position as the nine closed carriers this ruling leaves alone, and the clinician dropped the
restoration.

### 6. The publish hook prevents and the tracker workflow reports

The hook refuses an issue create whose body lacks the label, and an issue edit that drops or alters an
existing `**Filed from:**` line. The workflow reports the same two shapes after publication, reading an
`opened` body and an `edited` event's `changes.body.from`, so it reaches publishers the hook does not.
Both apply to issues only; a pull request body keeps its own binding grammar. The edit refusal concerns
an existing line: an edit to a post-cutoff ticket that never got one is not refused for leaving it out,
and adding the line later is allowed.

### 7. The line is append-only, and its correction sits beneath it

The line's text never changes and the line is never removed. A correction of it goes on its own dated
line directly beneath the unchanged line, for example
`*Corrected 2026-09-12: filed during #836's build, not its grilling.*`. Other corrections of the body
may go anywhere below the line, never above it. There is no escape, so the hook's test stays exact: the
same line is present at its position or it is not.

A bottom footer was ruled first and then refused, for the reason
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
refused correcting a figure by annotation only: a reader who acts on the line does not scroll to the
footer. *Amended before merge.*

### 8. The after-action review names the skill, course, module and date

`skills/aar/SKILL.md`, where it tells the review to write each ticket body under
`<run-directory>/aar/publications/`, requires the body to open with
`**Filed from:** the after-action review of a <skill> run (<course> <module>), <YYYY-MM-DD>.`
That matches what the nine existing review tickets already write, and it lets a reader group every
ticket one run produced. None of it is material the skill forbids reproducing. The skill edit lands
with the hook refusal; landed apart, every review ticket is refused. *Amended before merge: the first
draft named skill and date only, on the claim that the review's gate keeps a run key off the tracker.
The gate forbids a narrower list, measured above, so that claim was wrong and the clinician ruled
again.*

### 9. The cutoff is a committed UTC timestamp, and the sweep reads it too

The build commits one UTC timestamp. The hook, the workflow and the sweep compare an issue's `createdAt`
against it. Once per sweep, the sweep lists open tickets created at or after the cutoff that lack the
label. That covers tickets filed between the constant being written and the merge, sessions on older
bases whose hook predates the rule, and any workflow report nobody acted on.

### 10. A body carrying the map's producer stamp is outside these rules

The rules reach tickets. A body the implementation map renders whole, identified by the exact producer
stamp `tools/map_scan.py` already grades, is a coordination artifact with no descent to trace; its
stamp already says what made it. The hook, the workflow and the sweep skip such a body, and ruling 5's
reconstruction never reaches #596.

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
  reconstruction for the twelve tickets the agent classed as never having a line would be the
  respecer's reading.
- **Restore #875's line after it closed, or quote it in a comment.** Refused under ruling 5: #875 was
  singled out only because it was open, and repairing one closed carrier of ten would be arbitrary.
- **Prose and a sweep step alone.** Refused because #875 shows a respec dropping the line with nothing
  to stop it, which is [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what
  a written instruction cannot do is fail*.
- **The workflow alone, or the hook alone.** The workflow reports after GitHub has kept the damaged
  revision; the hook does not reach the web UI or another publisher.
- **A line that may change when the edit adds a correction.** Refused under ruling 7: the hook would
  have to judge whether the correction explains the change.
- **The correction in a bottom footer.** Refused under ruling 7, on ADR 0016's reasoning.
- **Moving the whole paragraph, or trimming the sentence.** The first freezes unrelated notes under an
  append-only label; the second is a paraphrase ruling 1 refuses.
- **Skill and date only in a review-sourced line.** Refused under ruling 8.
- **A separate skill-file ticket for the after-action review.** Refused under ruling 8.
- **The map renderer writing its own Filed-from line.** It repeats what the producer stamp already
  says, and changes a renderer whose every consumer would have to accept a new first line.
- **An issue-number cutoff.** Pull requests share the number space, and the build cannot know the right
  number before merging either.

## Consequences

The build is: the two refusals in `tools/tracker_publish_hook.py`, including its read of the current
body text; the two reports run from `.github/workflows/tracker.yml`; the committed cutoff; the
map-stamp exemption in all three readers; the rule and the sweep step in
`docs/agents/issue-tracker.md`; and the edit to `skills/aar/SKILL.md`. #1054's body carries the build
spec.

## What this does not reach

- **Whether a line is true.** The hook and workflow check that the label is present and unchanged.
  Whether it names what actually produced the ticket is the filing session's judgment, as ADR 0166
  already says of descent.
- **Converting an older ticket's origin sentence.** Ruling 3 refused pattern matching, so nothing can
  recognize the old sentence in order to check that a respec moved it word for word.
- **The web UI and sessions on older bases.** Neither runs the new hook. The workflow reports their
  tickets after publication, and the sweep lists what it missed.
- **The hook's manual `--text` mode.** It grades no route, so it reports the Filed-from rule as not
  graded rather than clean. Whether it gains a route is
  [#1026](https://github.com/mshamblin5150-code/clinical-skills/issues/1026)'s question.
- **Tickets filed before the cutoff that never had a line.** Nothing reports them until a respec reaches
  them.
- **Closed tickets, #875 and the nine carriers included.** Ruling 5 leaves them as they are, so a closed
  ticket's body is not evidence of its descent in either direction.
