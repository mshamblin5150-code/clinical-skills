# The initial post is posted when its approval record says so, and its saved link is read only from the posting block

**Measured at:** facb29d452bac3431393882ed80d2c79902db8c2

[#1694](https://github.com/mshamblin5150-code/clinical-skills/issues/1694) was filed from the
grilling of #1495, whose [ADR 0327](0327-an-unposted-reply-or-critique-s-posted-reading-is-not-graded-and-both-skills-sign-a-bar.md)
ruling 3 kept the initial post's posting fields out of that build. `discussion_post_scan` decides
whether the initial post was posted from any column-0 `POST-URL:` or `POSTED:` line anywhere in the
private `post.md`, so one stray line marks an unposted post as posted, and a stray link below the
real one replaces it. Grilled 2026-10-17 against `main` at the commit above, where the freshness
gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is built here;
this is the record the build reads.**

## Measured before ruling

**Two whole-file reads decide posting.** `load` and `posted_reading_check` each build a field map
with `FIELD.finditer` over all of `post.md`; the last occurrence of a key wins, and neither checks
for the `## POSTING: post.md` heading
[ADR 0318](0318-rendered-pages-waits-for-a-load-and-an-approval-needs-the-whole-text-shown.md)
ruling 2 added. The same presence test also decides whether the rendered-page rows wait for a load
and whether a reading with no posting fields is an unread remainder. The ticket's reproduction, on
`main` at `dd704cfe14f6408abdabfb96833efaf43b31d70a`, was not re-driven here; the code it describes
is unchanged at the commit above.

**The skill already records posting on the approval record.** `skills/discussion-post/SKILL.md`
calls `approval_record.record_agent_posting` immediately after the run posts, or
`record_clinician_posting` when the clinician posts the approved item himself, keyed on the output
Markdown's stem. `discussion_reply_scan` and `peer_critique_scan` build
`approval_record.PostedReadingState` from that route under ADR 0327 ruling 2, and
`approval_record.completion_gate` already refuses an approved key with no recorded posting route.

**The saved timestamp is checked only for presence.** `discussion_artifact.check_posted_reading`
reports `post-metadata` when either saved field is missing and `post-link` when the reading's link
differs from the saved one. Nothing compares the saved `POSTED` value with anything; the graded
timestamp is the one in the `## REREAD:` record.

**No real run uses the block.** The population is every `scratch/runs/*/post.md` under the scratch
roots of every registered checkout: two roots read, none unreadable, six files. The matcher is a
column-0 uppercase `POST-URL` or `POSTED` key and the exact `## POSTING: post.md` heading; indented
or mixed-case keys are outside it and were not counted. All six carry the bare fields and none
carries the heading, so a block-only read would have counted a nonzero number had any run used it.
Two of the six have a `posting-approvals.json` whose `discussion-post` item reads posted, and both
already carry `frozen-grades.json`. The other four have no approval record; three of them carry a
`## REREAD:` record. Frozen-grade adoption under ADR 0346 needs an approval revision and cannot
reach those four. These counts are measured against gitignored material nothing committed
re-derives, and are stated here only because rulings 2 and 5 rest on them.

## Ruling 1 — the approval record's posting route decides whether the initial post was posted

`discussion_post_scan` treats the initial post as posted when the run's approval record holds
`skill="discussion-post"` and the output Markdown's stem with `posting_route` of `agent` or
`clinician`, the route `approval_record.posting_route` already returns. No line in `post.md`
decides it. This is ADR 0327 ruling 2's rule, reached through the same keys the skill already
passes to `approve`.

Reading the fields only inside the posting block was declined because it keeps two records of one
fact and narrows the defect instead of removing it. Keeping the whole-file read and refusing a
second occurrence was declined because one stray line on an unposted post would still read as
posted.

## Ruling 2 — the saved link is read only from inside the posting block

When the post is posted, the grader reads its saved `POST-URL` only from inside the
`## POSTING: post.md` block, and the posted reading's link is compared with that value. A run that
writes the link as a bare line gets the existing incomplete-posted-reading finding at completion.

Refusing two differing `POST-URL` values across the whole file was declined because a bare line
would still stand as the saved link when no block exists. Keeping the last line in the file was
declined because a stray link below the real one replaces it and raises a false `borrowed-locator`.

## Ruling 3 — a posting-field line outside the block never changes status

A `POSTED:` or `POST-URL:` line outside the block marks nothing posted, supplies no link, adds no
row and changes no exit status. When a posted post has no link inside the block, the
incomplete-posted-reading message adds how many such lines were found outside it and says to move
the link under `## POSTING: post.md`. Default output stays counts only.

Counting the line as an unread remainder, or refusing it as a finding, was declined because a
template pasted early on an unposted post would again block a clean grade, which is the false
failure the ticket was filed over. Ignoring it with no mention was declined because the one case
where it matters, a real link in the old bare form, would then fail without naming its cause.

## Ruling 4 — the initial post takes the reply and critique posture whole

The grader builds `approval_record.PostedReadingState` from the posting route and the presence of a
`## REREAD:` record for the output stem, as the reply and critique graders do. Posted with a link in
the block is graded. Posted with no link in the block is the incomplete-posted-reading finding. A
reading whose posting is not recorded reports incomplete coverage that posting is not recorded,
exit 2. A posting block whose posting is not recorded is not graded during the run and is refused
at completion by the existing `no recorded posting route` check. Every other consumer of the old
field-presence test, including the rendered-page wait and the reading-without-fields remainder,
reads the same route.

Refusing a posting block with no recorded route immediately was declined because it would let text
in `post.md` decide status again and would make the initial post differ from its two siblings.

## Ruling 5 — a run older than the approval record reads as posting not recorded

A run with no approval record has no recorded posting route. Its posted reading, where one exists,
reports incomplete coverage under ruling 4; with no reading it is not graded. The grader's
`DECLARED_LIMITS` gains a row saying a run older than the approval record cannot show it was posted.
No legacy path reads the bare fields, and no approval record is written for such a run after the
fact.

Falling back to the whole-file read where no approval record exists was declined because it keeps
the defect alive for runs nothing grades again, behind a second code path. Backfilling approval
records was declined because it writes go-ahead evidence nobody recorded at the time, into the
record the grader trusts. Those runs already fail the terminal approval check, so their verdict at
completion does not move.

## Ruling 6 — the posting block holds the link alone

The skill's posting step appends `## POSTING: post.md` followed by `POST-URL:`; it no longer writes
`POSTED:` there. A `POSTED:` line inside the block is ignored rather than refused. The
`post-metadata` outcome names only the missing saved link. The `## REREAD:` record's own `POSTED`
field is unchanged and stays the graded timestamp.

Keeping both fields required was declined because nothing reads the saved timestamp, so requiring
it adds a way to fail for a value with no use.

## Supersedes

- [ADR 0318](0318-rendered-pages-waits-for-a-load-and-an-approval-needs-the-whole-text-shown.md)
  ruling 2, its words "holding `POST-URL:` and `POSTED:`", "the whole-file field read still finds
  both fields" and "Older runs that wrote the bare fields above their first record still read".
  The block holds the link alone, is the only place the link is read, and posting is decided by the
  approval record. The heading, its name, and its ending any render record above it stand.
- [ADR 0327](0327-an-unposted-reply-or-critique-s-posted-reading-is-not-graded-and-both-skills-sign-a-bar.md)
  ruling 3, its words "`discussion_post_scan` keeps deciding posting from the `POST-URL` and
  `POSTED` fields". The initial post now decides posting from the approval record under ruling 1
  here. Its declining to move the initial post inside #1495's build stands as a statement about
  that build.

## What this does not reach

Nothing here proves the agent recorded its posting at the moment it posted; an unrecorded posting
stays not graded until completion refuses it, the gap ADR 0327 already accepted for replies.
Whether the saved link is the post's real deep link stays the posted reading's judgment.
Preserved run records are not edited, and the four runs older than the approval record are not
re-graded.

## Build checklist

- `tools/discussion_post_scan.py`: decide posting from `approval_record.posting_route` through
  `approval_record.PostedReadingState` in `load`, `posted_reading_check`, `_posted_reading_findings`,
  the rendered-page wait and the posted-reading graded and unread computation; read the saved
  `POST-URL` only inside the `## POSTING: post.md` block; count posting-field lines outside the
  block for the ruling 3 message only; add the ruling 5 `DECLARED_LIMITS` row.
- `tools/discussion_artifact.py`: `post-metadata` fires on a posted post with no saved link and
  names only `POST-URL`; the saved `POSTED` is no longer required.
- `tools/test_discussion_post_scan.py`: the ticket's cases through the public command — a stray
  column-0 `POSTED:` or `POST-URL:` before posting exits 0 with the posted-reading rows not graded;
  a stray `POST-URL:` after a real block leaves the block's link in force; a posted route with only
  a bare link fails with the outside-the-block count in its message; a reading with no recorded
  route reports incomplete coverage; a block with no recorded route is not graded and completion
  refuses it; a run with no approval record reads as posting not recorded.
- `skills/discussion-post/SKILL.md`: the posting step writes the heading and `POST-URL:` only.
- `CLAUDE.md` **Discussion post grading**: the unread-remainder sentence names a reading whose
  posting is not recorded rather than a post lacking `POST-URL` and `POSTED`.
