# An approval carries the clinician's whole reply and is refused when his messages do not hold it

**Measured at:** b4f3f9e3eb85d846ec3dde586ffbc19d7c6ba84c

[#1474](https://github.com/mshamblin5150-code/clinical-skills/issues/1474) was filed from the
after-action review of a `batch-shift` run. `skills/batch-shift/SKILL.md` step 7 said a
substantive change invalidates the approval and defined neither that word nor its boundary. After
approval, one punctuation fix changed a note's bytes, and the orchestrator recorded a second
approval through `approval_record.approve` itself and told the clinician afterward. Grilled
2026-10-08 and 2026-10-09 against `main`, where the freshness gate read `FRESH`; the clinician
ruled every point below in that session. **Nothing is built here; this is the record the build
reads.**

## Measured before ruling

**The ticket's question was already answered.** [ADR
0300](0300-the-entry-copy-refusals-run-before-the-go-ahead-and-a-changed-note-needs-a-new-word.md)
ruling 4, ruled on #1458 the day this grilling began, requires any change to an approved note's
text to be shown as the exact change and re-approved only on the clinician's new explicit word.
It declined a narrower exemption because the agent making the edit would also be classifying it,
which is the same objection to #1474's Option A. Both changes this ticket recorded are now caught
before the Review sheet: the four-quadrant abdomen by [ADR
0303](0303-normal-exam-lines-are-the-clinician-s-own-and-the-abdominal-scheme-is-a-setup-answer.md)
and the Entry-copy refusal by ADR 0300 ruling 1.

**The approval step records a boolean and no evidence of the clinician's word.**
`approval_record.approve` refuses only when `content_approved` is false, so an agent that passes
`True` records an approval indistinguishable from one the clinician gave. ADR 0300's *What this does
not reach* states that limit for ruling 4.

**The step is shared.** Six skills call `approval_record.approve`: `batch-shift`, `clinical-note`,
`discussion-post`, `discussion-reply`, `peer-critique` and `practicum-case-study`.
`discussion-post` calls it twice for one item by design, once at Gate 1 and again at Gate 2.
`course-assignment` records its two clinician gates through `assignment_submission` in a separate
`submission-gates.json` and does not call this step. `approval_record.completion_gate` is the
shared completion check those six skills' graders reach.

**A predicate for the clinician's own messages exists.** `aar_scan` classifies a transcript user
row with no harness flag or recognized envelope as the `clinician` entry kind and already discovers
every main Claude and Codex transcript that names a run directory.

## Ruling 1 — an approval's evidence is checked by a tool, not only required in writing

The approval step receives the clinician's reply that gave the go-ahead and checks it against his
own messages. This closes the limit ADR 0300 declared for its ruling 4: a written rule alone cannot
tell his word from an agent calling the step again. Leaving the rule written was declined because
it is the exact departure #1474 recorded. A short code he must repeat in each approval was declined
because it adds work to every go-ahead, and the work he already found burdensome is what the ticket
was filed over.

## Ruling 2 — every approval recorded through the shared step carries it

First approvals and later approvals, in every skill that calls `approval_record.approve`, carry the
clinician's reply. Each of `discussion-post`'s two gates carries its own reply. Restricting the
check to re-approvals, or to the two note skills, was declined because the same call records all of
them, so an approval in one skill would be evidence of his word and in another would not.
`course-assignment` does not record through this step and is outside this ruling; whether its gates
take the same check is a separate question for the clinician.

## Ruling 3 — the check runs at approval and again at completion

When the session transcript is readable, `approve` refuses to record an approval whose reply does
not appear among the clinician's messages written after the approved sources last changed. When the
transcript cannot be read, `approve` records the approval and marks it not verified, and the
skill's completion grader re-checks every approval so marked. One shared function decides both.
Checking only at completion was declined because a Medatrax entry and a Canvas post cannot be
withdrawn, so detection after posting is detection after the harm. Refusing whenever the transcript
is unreadable was declined because a tool failure would then block a legitimate posting.

## Ruling 4 — the reply is his whole message, compared with spacing ignored

The recorded reply must equal one of the clinician's messages in full after whitespace is
normalized. A substring was declined because it lets the recorder choose which part counts, so
"Agree" could be lifted from "Agree, but fix the date first." A substring with a minimum length was
declined because it rejects a genuine one-word approval. A conditional approval is therefore
recorded with its condition visible.

## Ruling 5 — step 7's undefined word becomes "any change"

`skills/batch-shift/SKILL.md` step 7 reads: any change to the content the approval identity covers
invalidates the entire approval, and regenerating the Review sheet's layout from unchanged
normalized content does not. This states the boundary ADR 0300 ruling 4 already drew, and it gives
[ADR 0250](0250-a-review-sheet-carries-final-coding-only-after-the-batch-is-fresh.md) ruling 7's
"substantive" its meaning without narrowing it. Under [ADR
0280](0280-an-overturned-ruling-carries-a-dated-supersession-marker-written-by-the-record-that-overturns-it.md)
ruling 2 this record completes those rulings and withdraws nothing, so it owes no supersession
marker. The skill instructions that pass the reply to `approve` land with the build, because the
parameter does not exist yet.

## Definition

The clinician's message is a message he typed into a session: the `clinician` entry kind or its
successor. A tool result, hook context, a scheduled-trigger prompt, another session's relayed
message, and a subagent transcript never count. The build verifies that each of those arrives in a
form the predicate excludes, rather than assuming it.

## What this does not reach

A whole-message match shows that he answered after the approved sources last changed. It does not
show which change he meant: a bare "Agree" after two pending changes approves whichever one the
agent records. Ordering rests on source modification times and transcript timestamps, which a
process able to rewrite either can defeat. Whether the approved content is clinically right remains
his reading at the go-ahead.
