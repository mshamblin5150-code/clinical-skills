# A final review follows a posted record and every review round keeps its own files

[#1015](https://github.com/mshamblin5150-code/clinical-skills/issues/1015) was filed by the
after-action review of one `practicum-case-study` run (NUR 5144 Module 2, submitted 2026-09-10). The
review read that sitting once, when the draft was finished. The clinician's revision round and the
submission came after its watermark, the completion grader reported the review clean, and a second
review then overwrote the first review's record, baseline and fourteen unlanded corrections.

The ticket listed four defects and three open decisions. **One defect was already built, and one of
the ticket's own premises was false.**

Grilled 2026-09-12 to an empty frontier. **Eight rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads.

## Measured before ruling, at `03872097`

**1. Defect 3 is built.** PR #1173 replaced the last-file-wins watermark reader with
`aar_scan._review_cursors` and `_furthest_cursor`, which select the prior cursor furthest through the
transcript whatever the prior record is named. Nothing about it is ruled here.

**2. The ticket's claim that the case study already reviews at submission is false.**
`skills/practicum-case-study/SKILL.md` invokes the review at the end of its post-draft checks, under
*"Invoke `/AAR` before declaring the submission complete"*, and no later step submits or records a
submission. The run did what the skill said. The four skills that post to Canvas do post first:
`discussion-post` records `POST-URL:` and `POSTED:` under *"After submission, read the initial
entry's Copy Link"*, `discussion-reply` and `peer-critique` append the same `## REREAD:` record, and
`course-assignment` step 6 reads *"Then submit, reread the posted artifact and timestamp, and record
the submission URL, posted time"* in no fixed format.

**3. Nothing parses a posted time.** `discussion_artifact.read_posted_readings` keeps `POSTED` as the
board's displayed text, `READ` is a date with no time, and an extract `Candidate` carries no
timestamp.

**4. The record heading does not equal the review key in one skill.** `discussion-post` heads its
record `## REREAD: post.md` while its review key is the output Markdown stem, and
`discussion_post_scan` selects `item.artifact == "post.md"` in its posted-reading check.
`discussion_reply_scan` indexes records by response filename (`by_artifact`), so it does not select
that heading. `deck_scan` reads no posted record at all.

**5. One review record per submission key.** `survey` reads `review_path(run, submission)` and
`extract_path(run, submission)` and requires every correction event in that one extract;
`write_extract` rewrites `baseline_path(run, submission)` on every extract; `_target_changed` treats
a path absent from the baseline as changed. A second extract for the same key replaces all three.

## Ruled 2026-09-12

### 1. A final review must come after a written record of the submission

The review exists to read a sitting whose work has been handed over, so the event it must follow is
the hand-off itself. **The clinician's last turn was refused**: he routinely speaks during the review
("agree", "file it"), so a review could never follow his last turn. **The submitted file's
modification time was refused**: it catches a revision round and misses a correction after an upload
that changed no file, such as a divergence found on the board.

### 2. The note skills hand off by posting to Medatrax

`clinical-note`, `icd10-cpt` and `batch-shift` have not been used yet; they will post to Medatrax the
way the Canvas skills post to a board. The framing that they hand off only in conversation, and so
could take an acceptance record or an exemption, was the clinician's to correct and he corrected it.

### 3. No exception for skills without a posting step

Until a note skill records a Medatrax post, its final grade fails with no posted record. The step is
[#1205](https://github.com/mshamblin5150-code/clinical-skills/issues/1205). The failure costs nothing
while the skills are unused and points at the missing step the first time one runs for real.
**Grading them `not graded` was refused**: that label would persist in silence into real use.

### 4. The case study's record-the-post step is built with this ticket

After the clinician's go-ahead and the post, read the entry back, write the posted record, then invoke
the review. It lands with the grader rule so a skill used every module never has a window in which its
final grade always fails. [#1154](https://github.com/mshamblin5150-code/clinical-skills/issues/1154)
keeps the Composer size refusal, the attachment fallback and which file is graded; both of its branches
end with an entry to read back, so neither changes this step.

### 5. The posted record must exist when the review takes its snapshot

`aar_scan --extract` refuses to snapshot unless the submission's posted record exists, and writes a
fingerprint of that record into the extract. The final grade refuses when the extract carries no
fingerprint or the record no longer matches it. **The fingerprint covers that one record, never the
whole `reread.md`**: `discussion-reply` appends reply two's record after reply one's review, and a
whole-file fingerprint would refuse a review that was correct.

**Comparing times was refused.** It needs a parser for Canvas's displayed time and another for
Medatrax, a timezone, and a timestamp on every extract entry, and it would first refuse the Module 2
review at the final grade rather than at the moment the review began.

### 6. A posted record's heading is the review key, in every skill

Every scoped skill writes `## REREAD: <submission key>` in the run's `reread.md`. `discussion-post`
renames its heading from `post.md` to its output Markdown stem and `discussion_post_scan` moves with
it; `course-assignment`, the case study and #1205's step adopt the same record.

**Naming the record at extract time was refused**: `--extract --posted <heading>` lets an orchestrator
tie a review to another submission's real record, which is a choice the grader cannot check and the
invisible veto [ADR 0109](0109-the-after-action-review-s-signal-is-an-observed-correction-and-its-findings-land-or-the-run-is-not-done.md)
ruling 8 closes. **A per-skill lookup table was refused**: it would be a second copy of what each skill
already states.

### 7. Every review round over one submission keeps its own record, extract and baseline

The first round keeps `aar/<key>.md` and its extract and baseline. Each later round writes its own
numbered record, extract and baseline beside them; the names are the build's, within the non-extract
`aar/*.md` set `_review_cursors` already reads. **The final grade walks every round for the key and
requires each clean against its own extract and its own baseline.** An unlanded correction is landed
by completing its own round's record; a later round never re-rules it, which is ADR 0109 ruling 10's
refusal of a fresh verdict from a context that never saw the reasoning.

Measuring each landing against the snapshot of the round that recorded it retires defect 2: a later
snapshot can no longer flip a landing that already happened, and no round borrows another round's
baseline. **Carrying unlanded corrections forward into the newest record was refused**, because it has
the orchestrator retype verdicts it did not make. **One record with appended sections was refused**,
because rewriting the file each round is the overwrite this ticket is about.

### 8. Reporting a status from memory after a compaction is its own ticket

The grader reported exit 1 correctly; the orchestrator reported clean from a compaction summary that
kept the unlanded corrections and dropped the exit status. That can happen to any command in any skill,
so it is [#1206](https://github.com/mshamblin5150-code/clinical-skills/issues/1206) and nothing here
depends on it.

## Taken as conventions, not ruled

- **The report prints every round** with its correction count and unlanded count on every run, which
  is #258's printed-denominator convention; the ticket's fourteen went uncounted.
- **Extracts taken before the build are graded under a dated UTC cutoff** for the posted-record
  fingerprint, which is ADR 0193 ruling 12's arrangement for `CLASSIFIER-ENTRY` and
  `tracker_filed_from.FILED_FROM_CUTOFF`'s before it.

## Consequences

- `skills/aar/SKILL.md` states that the posted record must exist before extracting and how a later
  round is written and landed.
- `skills/practicum-case-study/SKILL.md` gains ruling 4's step; `skills/discussion-post/SKILL.md` and
  `skills/course-assignment/SKILL.md` change their record per ruling 6.
- [#1016](https://github.com/mshamblin5150-code/clinical-skills/issues/1016)'s proposed sentence
  *"do not submit before then"* contradicts ruling 1 and is overruled; the wait it guarded against,
  a review blocked on tracker publications before submission, no longer precedes submission.
- [ADR 0170](0170-every-grader-declares-the-posture-its-empty-population-takes.md)'s posture entry
  for `aar_scan` names the review record as its population; a build that grades every round
  re-derives that entry. Ruling 7 loosens no watermark comparison, but a round-walking grade still
  needs its own empty-extract test, as #1015's sweep from #922 recorded.
- `CONTEXT.md` widens **Posted reading** past a board and adds **Review round**.

## What this does not reach

**Whether the post happened.** The agent writes `POSTED` either way; the reread and the clinician own
that.

**A correction after the last round's watermark.** A turn during landing or after the final grade is in
no round; ruling 1 refused the only rule that would reach it.

**Whether the posted record describes the right entry.** Ruling 6 ties a review to a heading, not to
what the board holds.
