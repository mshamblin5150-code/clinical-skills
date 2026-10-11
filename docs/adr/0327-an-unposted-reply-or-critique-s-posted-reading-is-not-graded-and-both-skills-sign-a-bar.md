# An unposted reply or critique's posted reading is not graded, and both skills sign a bar

**Measured at:** dd704cfe14f6408abdabfb96833efaf43b31d70a

[#1495](https://github.com/mshamblin5150-code/clinical-skills/issues/1495) was filed from the
after-action review of a `discussion-reply` run (NUR 5144 Module 2) on 2026-10-01. Its comments
record the same approval refusal on a `peer-critique` run and on three more `discussion-reply` runs
through 2026-10-07. It names two tool contracts the two skills cannot satisfy: the go-ahead approval
refuses the grade every unposted reply or critique produces, and the claim checker refuses a run
with no bar file. Grilled 2026-10-11 against `main`, where the freshness gate read `FRESH`; the
clinician ruled every point below in that session. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

**The approval refuses the grade the skill says to expect.** `approval_record.approve` runs the
skill's paired grader without `--submission` and raises "the pre-post grade has a finding" on any
exit other than 0 or 2. `discussion_reply_scan._posted_reading_findings` runs the posted-reading
check over every `response-*.md` in the run, and `peer_critique_scan._reread_findings` runs it over
`critique.md`, whether or not anything was posted. With no `reread.md` record the shared check
returns its missing-record outcome, filed as `missing-posted-reading`, and both graders exit 1.
`skills/discussion-reply/SKILL.md` step 4 says that finding is the one expected before a reply is
posted and, a few paragraphs later, that a finding refuses the record; `skills/peer-critique/SKILL.md`
says only the second. The reply grader also files the finding for a drafted reply that was never
approved.

**The other four approval skills do not hit it.** Their graders' posting-dependent rows report not
graded without `--submission`, which `approve` never passes. In `discussion_post_scan`, a run whose
`post.md` carries neither `POST-URL` nor `POSTED` and whose `reread.md` holds no reading reports the
posted-reading rows not graded, and that state does not set incomplete coverage; only a reading with
no posting fields does.

**The approval record already says whether an item was posted.** `approve` writes
`posting_route: awaiting-posting` on every call, including a re-approval after an edit, and
`record_agent_posting` or `record_clinician_posting` replace it with `agent` or `clinician` after
re-hashing the approved sources. `approval_record.completion_gate` already returns a finding for an
approved key whose route is neither. During `approve` the grader runs before the record is written, so
it reads the previous item or none.

**Peer-critique runs never have a bar; reply runs have one only by sharing a folder.**
`research_ledger._load` raises "the ledger run needs bar.md" before any mode runs. Neither skill
writes a bar. `discussion-reply` keys its run directory to the board with the artifact word
`discussion`, the same directory `discussion-post` signs `bar.md` in, so a reply run on a board whose
initial post this repo wrote finds that bar; any other reply run, and every
`scratch/runs/<course>-<module>-peer-critique/` run, does not. The first filed run wrote a bar itself
from the skill's prose so the checker would run. ADR 0322 already tells both skills to write one
when the clinician admits his own unpublished work and none exists.

**Both skills already stop for the clinician before research.** `discussion-reply` step 1 asks him
to answer the ranking with two numbers before drafting, and `peer-critique` says to read the spec
live and sign what it says on this sitting.

## Ruling 1 — an unposted item's posted reading is not graded

In `discussion_reply_scan` and `peer_critique_scan`, a reply or critique whose posting is not recorded
and that has no posted reading reports its posted-reading rows not graded, and that state is neither
a finding nor incomplete coverage. So the go-ahead grade exits 0 when every other row passes, and
`approve` records the approval. Once the posting is recorded, a missing or failing reading is a finding
exactly as today. A reading that exists for an item whose posting is not recorded is incomplete
coverage, exit 2, as `discussion_post_scan` treats a reading with no posting fields. The rule is
per item, so a posted reply one with no reading still refuses reply two's approval.

Reporting the unposted state as incomplete coverage, exit 2, as ADR 0318 ruling 1 does for
rendered pages, was declined: every reply and critique go-ahead would carry an incomplete line for an
expected reason, which teaches the reader to skip the word that marks a real coverage gap. Here the
population of posted items is empty and counted correctly, so nothing went unread. A list of expected
rows inside `approve` was declined because it applies to the whole run and passes reply one's
missing reading at reply two's approval. A caller-passed before-posting flag was declined for ADR
0318's reason: nothing catches it passed at the wrong time. A run still cannot finish without its
readings, because the terminal grade runs with `--submission` and the approval-record row requires
every approved item's posting route and reading.

## Ruling 2 — posted means the approval record's posting route

The two graders treat an item as posted when the run's approval record holds that skill and
submission with `posting_route` of `agent` or `clinician`. The submission key is the response
filename for a reply and `critique.md` for a critique, the keys the two skills already pass to
`approve`. A re-approval resets the route to `awaiting-posting`, so an edited item reads as unposted
until it is posted again. A posting the agent made without recording it stays not graded during the
run and is refused at completion by the existing route check.

A posting block written into a run file, as `discussion-post` writes `POST-URL` and `POSTED` into
`post.md`, was declined as a second, hand-written copy of a fact the tools already write per item.
Reading the live board at grading time was declined because graders here open no network and the
posted reading is already that read.

## Ruling 3 — the initial post's posting fields are not moved here

`discussion_post_scan` keeps deciding posting from the `POST-URL` and `POSTED` fields, which ADR
0318 ruling 2 placed under a `## POSTING: post.md` heading and whose `POST-URL` is also compared with
the reading. Its whole-file field read, which counts such a line anywhere in `post.md`, is filed as
its own ticket. Moving the initial post onto the approval record here was declined because nothing in
rulings 1 and 2 depends on it and it would bring a third grader and its disagreement cases into this
build.

## Ruling 4 — reply and critique runs sign a bar at the stop they already have

At its existing stop for the clinician, before any claim is researched, each skill writes `bar.md`
with `SIGNED`, `SOURCE-CLASSES`, and `RECENCY-WINDOW-YEARS`, taking the four default classes and
five years from the skill unless the live board or spec states otherwise, and shows those
lines beside the ranking or the spec reading. The clinician's answer at that stop signs it, and the
run writes the date into `SIGNED` only then. A `discussion-reply` run whose directory already holds the
initial post's signed `bar.md` uses that bar and writes none. `research_ledger` keeps refusing a run
with no bar.

A fallback inside `research_ledger` to the skills' fixed vocabulary when no bar exists was declined:
a missing file would silently become a default, which `course-assignment` forbids by name, and the
own-work admission would still need a bar, leaving two paths. Having the caller name the skill so the
checker applies that skill's built-in rules was declined because it copies skill prose into code and
rests on the caller declaring correctly. Either way the rules applied would be ones the clinician never
saw, which is the defect the first filed run produced.

## Ruling 5 — the filed runs are left as they stand

The runs #1495 records are not repaired. Four posted with no approval record and one wrote its
record after posting. A reply that touches one of the four reports
`stopped - posted before the approval recorder could record it (#1495)`. Writing their approval
records now from the clinician's chat messages was declined because each would claim a pre-posting
check that never ran. A new after-the-fact approval state was declined as machinery for runs that
will not post again.

## What the build changes

- `tools/discussion_reply_scan.py` and `tools/peer_critique_scan.py`: rulings 1 and 2, with tests
  that drive an unposted item exiting 0, a posted item with no reading exiting 1, a reading with no
  recorded posting exiting 2, a re-approved item reading as unposted, and reply two's approval refused
  while posted reply one has no reading.
- `tools/approval_record.py`: a public read of one item's posting route for the graders, in place of
  the private `_read` and `_matching_item` pair.
- `skills/discussion-reply/SKILL.md` and `skills/peer-critique/SKILL.md`: the go-ahead expects a
  clean grade with the posted-reading rows not graded; the bar is written and shown at the existing
  stop; the reply skill's reuse of the initial post's bar.
- A test that each skill names the bar step and that a reply run sharing a signed initial-post bar
  passes `research_ledger` without writing a second one.

## What this does not reach

- **Whether the bar's classes match the course.** The clinician signs what the agent wrote; the
  record proves he answered the stop, not that the agent transcribed the course correctly.
- **An unrecorded posting during the run.** Ruling 2 leaves it not graded until completion, where
  the route check refuses it.
- **The initial post.** Its posting decision and its whole-file field read are unchanged here.
