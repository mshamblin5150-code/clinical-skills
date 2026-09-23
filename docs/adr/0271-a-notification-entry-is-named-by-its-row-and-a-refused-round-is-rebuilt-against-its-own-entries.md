# A notification entry is named by its row and a refused round is rebuilt against its own entries

**Measured at:** 9c70aa19551c6c0303d37a2a2530e8e18a03da9b

[#1391](https://github.com/mshamblin5150-code/clinical-skills/issues/1391) was filed from the
after-action review of a batch-shift run on 2026-09-22: `aar_scan.py --extract` wrote an extract
its own reader refused with `extract entry identifier is absent or duplicated`, and a second review
the same day, on a course-assignment run, hit it on a larger population with a completed
fourteen-correction review record already written. Grilled 2026-09-23 against `main`, where the
freshness gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

These were counted, not only read. Every count below was taken on the clinician's machine on
2026-09-23, printed integers only, and read no note or record text into this repository.

**The ticket's mechanism is mostly wrong, and the correction widens the defect.** The ticket says a
background task emits more than one notification over its life, so later notifications collide with
the first. What the transcripts hold is usually **one** notification written two or three times: a
`queue-operation` enqueue row, then the `user` or `attachment` row that delivered it, and often a
`queue-operation` remove row, each carrying the same envelope. `aar_scan.reduce_transcript` reads all
three row types as first-class, and `_human_identifier` names every one of them by the matched
`<task-id>`, so each copy collides with the others.

| over the main transcripts under `~/.claude/projects` | |
| --- | ---: |
| main transcripts read | 532 |
| task ids carried by more than one notification entry | 2,940 |
| of those, every copy byte-identical | 2,812 |
| of those, two or more distinct bodies | 128 |
| transcripts in which some task id is duplicated | 374 |

*Had the ticket's mechanism been the cause, the distinct-body count per task id would equal its copy
count; it printed one distinct body for 2,812 of 2,940.* The 128 are genuinely distinct
notifications for one task, such as monitor events and workflow progress, and they collide too.

**So any sitting that launches one background task is affected, not only one that launches
several.** Of the eight extracts under every registered checkout's `scratch/runs/`, the two that
contain a `task-notification` entry are both refused and the six that contain none all read. That
is a small population and is stated as one; it is also every extract that has ever held a
notification since [#1014](https://github.com/mshamblin5150-code/clinical-skills/issues/1014)
landed the envelope reading on 2026-09-12.

**The task id was chosen for a reason, and the reason survives.** The review record's
`CLASSIFIER-ENTRY` is written before the classifier returns, because its return lands after the
watermark and is labeled `prior-review` in the next round's extract
([ADR 0193](0193-an-extract-entry-s-kind-names-its-envelope-and-a-matcher-may-label-where-it-may-not-reduce.md)
ruling 6). The task id is the only name the session can know in advance; a row name cannot be.

**The one completed record on a refused extract cites no notification entry.** The course-assignment
review cites 19 entries by heading, and none of them names a `task-notification` entry; its
`CLASSIFIER-ENTRY` is not an entry of that extract either. So renaming notification entries
invalidates no correction or sustain that review already names. The batch-shift run's refused extract
has no record written.

**Collapsing the copies is already ruled out.** ADR 0193 ruling 11: *"five copies are five labeled
duplicates rather than five phantom clinician turns, and nothing narrows."* The ticket's own open
question, whether the notifications for one task should be one entry, is answered there and was not
reopened.

## Ruled 2026-09-23

### 1. A notification entry is named by its own row

A `task-notification` entry takes the identifier every other human-row entry takes: its row's
`uuid`, the `#text-N` form on an assistant block, or the `<transcript-stem>#row-<ordinal>` fallback
of [ADR 0222](0222-extract-entries-are-named-by-their-transcript-and-a-review-reads-every-sitting-by-scan-rather-than-by-pointer.md)
ruling 1. The `<task-id>` is no longer an identifier. It stays legible because it is in the entry's
own body, and it is carried as an alias for resolution, which makes it a key shared by every copy
rather than a second name for one entry.

Every copy remains its own entry, on ADR 0193 ruling 11.

### 2. `CLASSIFIER-ENTRY` holds the classifier's task id and labels every entry carrying it

The field keeps its name and its meaning changes: it records the task id the classifier's return
will carry, and the next round labels **every** entry carrying that task id `prior-review`. That is
each copy of the one return, and every one of them is the same stale verdict. The template line in
`skills/aar/SKILL.md` step 4 becomes *the task id the classifier's return will carry*, and step 2's
retention sentence says the same. Existing records need nothing: the field already held task ids in
practice.

### 3. A watermark that is a task id resolves to the first entry carrying it

A prior round's `WATERMARK` or `TRANSCRIPT-WATERMARKS` value can equal a task id only if that
round's extract read, which required its notifications to be single copies. The copy that existed
then is the first entry carrying the id; any later carrier is new. Resolution by alias therefore
takes the first match for a task id and is otherwise unchanged.

### 4. Extraction validates before it writes

`--extract` builds the extract text, runs the same reader the grader uses over it, and writes the
extract and the baseline only when the text reads. A refusal exits 2 and writes neither file. Today
it writes both and then refuses its own file, which leaves a round on disk that the grader will
never accept and that a classifier will be briefed against anyway, as the course-assignment run was.

### 5. A refused round is rebuilt in place against its own entries

`--extract --rebuild-round N` regenerates round N's extract under the current naming and accepts it
only if it is the population the refused extract recorded:

- each transcript starts where round N's own extraction started, from the earlier rounds' cursors,
  and is bounded by the number of entries that transcript contributed to the refused extract;
- the rebuilt entries match the refused ones one for one, in order, with the same `TRANSCRIPT`,
  `KIND` and body text;
- every identifier outside a `task-notification` entry is byte-identical, and only a
  `task-notification` entry's identifier may differ.

Any difference refuses, exit 2, and writes nothing. On success the refused extract is moved aside
under the run's `aar/` directory, where no round discovery reads it, never deleted; the baseline
and any record are left untouched, and the existing record is graded as written. The refused
extract is readable as text even though the grader refuses it, which is what makes the comparison
possible.

A count of entries was declined as the check: a different population of the same size prints the
same count, so it cannot tell the rebuilt population from another. Count plus resolvable citations
was declined for the same reason at a smaller scale.

### 6. The regression case is the harness's own shape

The failing case the build writes first is one notification recorded as a `queue-operation`
enqueue, the delivering `user` or `attachment` row, and a `queue-operation` remove, in that order,
with the extract read back by the grader's reader. A case with two distinct notifications for one
task is the second, narrower shape and is written beside it, not instead of it.

## Rejected options

**Collapsing a task's notifications into one entry.** ADR 0193 ruling 11.

**`<task-id>#<occurrence>` on every copy, or the bare id on the first copy and a suffix on later
ones.** Either keeps the id in the heading, and either makes an entry's name depend on how many
times the harness happened to write one notification, which is harness behavior that changes
without notice. The first-copy form also labels only one copy `prior-review` unless a further rule
reaches the rest.

**Renaming the field to `CLASSIFIER-TASK`.** A record-format change under ADR 0193 ruling 12's
dated cutoff, with the grader reading both spellings, for no grading gain. The name's mismatch is
answered by the template wording and by this record.

**A one-time repair script for the two runs.** It fixes these two and leaves the next naming change
with no count-checked repair.

**Moving the refused round aside and classifying afresh.** It discards a completed adversarial
review over a naming defect the review did not cause.

## Consequences

#1391 is respecified to these rulings and moves from `grilling` to `ready-for-agent`. The
batch-shift run and the course-assignment run each reach a gradeable round through ruling 5 once it
lands. `skills/aar/SKILL.md` changes only where ruling 2 says; the CLAUDE.md *After-action review*
section gains the rebuild command beside the two it lists.

**Not reached here:** the population is inflated by the harness's copies, two or three entries per
delivered notification, which ADR 0193 ruling 11 accepts and this record does not revisit. Nor does
it reach whether a `queue-operation` remove row ever carries text the delivering row lacks; the
2,812 byte-identical tasks say that is rare, and the 128 with distinct bodies were not broken down
by row type.
