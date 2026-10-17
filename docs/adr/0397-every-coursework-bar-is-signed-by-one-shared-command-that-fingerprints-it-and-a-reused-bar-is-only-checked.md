# Every coursework bar is signed by one shared command that fingerprints it and a reused bar is only checked

**Measured at:** b64ee902f449b9d08754cadacfe7579a2c052b17

[#1769](https://github.com/mshamblin5150-code/clinical-skills/issues/1769) was filed from the
grilling of #1569, which produced
[ADR 0355](0355-a-course-assignment-bar-is-signed-by-a-command-that-fingerprints-it-and-carries-the-clinician-s-reply.md).
That record signs a `course-assignment` bar with a command that fingerprints `bar.md` and carries
the clinician's confirming reply, and its ruling 4 left the other four skills that sign a bar to
this ticket. Grilled 2026-10-17 against `main` at `ec4de36e`, where the freshness gate read `FRESH`;
the merge to the commit above changed none of the measured files. The clinician ruled every point
below in that session. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**All four skills date the bar by hand.** `discussion-post`, `discussion-reply`, `peer-critique`
and `practicum-case-study` each tell the agent to write the `SIGNED:` ISO date after the
clinician's confirmation. No tool fingerprints `bar.md` or records what he confirmed in any of
them.

**The research fields are reread when the ledger is graded.** The ticket priced the reply and
critique bars as signing "three research fields that no grader rereads at completion".
`research_ledger.read_bar` reads `SOURCE-CLASSES` and `RECENCY-WINDOW-YEARS` on every grading
run. In `discussion-reply` and `peer-critique` that is the grader handoff after every claim and
refutation is gathered; `practicum-case-study` grades the ledger again with `--draft` and
`--evidence`. The `--heading-digests` mode run before each refutation dispatch does not open the
bar. A failing ledger is therefore read against exactly the fields an agent could widen to make it
pass. `research_ledger` also admits the clinician's own unpublished work only when the bar carries
one valid `SIGNED:` date, which is the agent's own write.

**The post bar's graded numbers are read by its grader.** `discussion_post_scan` reads `SIGNED`,
`WORD-FLOOR`, `WORD-CEILING` and `REFERENCE-MINIMUM` from `bar.md`. `discussion_reply_scan` and
`peer_critique_scan` do not open `bar.md`.

**A reply run can read the post's bar.** `discussion-reply` uses the initial post's signed
`bar.md` when the run directory already holds one, writes no second bar, and shows its lines
beside the classmate ranking.

**The case-study bar walk names no bar.** `checks_ledger` grades `bar-walk.json`'s shape. It
opens `bar.md` only for `SUBMISSION-TYPE` and never compares a walk with the bar it walked.

**The existing command accepts only a course-assignment bar.** `assignment_bar.sign` parses the
shared course-assignment envelope, dispatches through `ADAPTERS` to a deck or DOCX validator, and
refuses any other grammar. Its fingerprint, retained copies, `approval_record.verify_clinician_reply`
call and `completion_gate` comparison are not specific to that envelope.

## Ruling 1 — all four skills sign their bar with ADR 0355's mechanism

`discussion-post`, `discussion-reply`, `peer-critique` and `practicum-case-study` sign every bar
by the command, never by a hand-written date. ADR 0355 rulings 2, 3 and 5 apply to them as they
apply to `course-assignment`:

- the command writes `SIGNED:`, fingerprints the result, and retains each signed version;
- the signature carries the clinician's reply, checked against his own messages by ADR 0310's
  predicate, and is recorded as not verified when the transcript cannot be read;
- a conflict found later is a re-signing that shows him the old and new wording of each changed
  line. This includes a mid-run admission of his own unpublished work, whose request message is
  the reply checked.

Every command that reads a signed bar refuses one that no longer matches its latest signature: each
skill's completion grade, and `research_ledger` when it grades a ledger. ADR 0355 ruling 1, the
producer's reach stated before signing, stays DOCX only.

Signing only the `discussion-post` and `practicum-case-study` bars was declined. It rested on the
research-only bars not being reread, and they are reread at the ledger grade, which is when
widening them pays. It would also check a post's bar in the post's run and leave the same file
unchecked when a reply run reads it. Changing nothing was declined: an edit after signing would
stay invisible in all four skills.

## Ruling 2 — a reply run that reuses the post's signed bar checks it and signs nothing

When a `discussion-reply` run uses the initial post's signed bar, its commands refuse unless
`bar.md` still matches its latest signature. The clinician's ranking answer chooses the targets
and signs nothing. A reply board that needs a different source class or recency window goes
through Ruling 1's re-signing, with the changed lines shown.

Having the ranking answer re-sign the reused bar was declined. The command signs whatever bytes
are present, so a bar edited between the post's sitting and the reply's would be signed by a
message about classmates without his ever seeing which lines changed. That is the blind spot ADR
0355 ruling 5 closes.

## Ruling 3 — a fresh bar is signed by the answer the clinician already gives at that stop

A fresh `discussion-reply` bar is signed with the clinician's ranking answer, and a
`peer-critique` bar with his answer to the spec reading. Both are shown beside the bar lines at
the existing stop, as ADR 0327 ruling 4 requires. `discussion-post` and `practicum-case-study`
sign with the reply that answers their existing bar approval.

A separate confirming message for a fresh bar was declined. An edit after signing is already
caught by the fingerprint. The remaining gap, a bar written differently from the lines shown, is
the same for any wording of reply, because the check proves he wrote the words and never that
they were about the bar. An added message would cost a stop on every reply and critique run and
close nothing.

## Ruling 4 — the case-study bar walk records the signature it walked

`bar-walk.json` records the fingerprint of the signed bar it was made against. `checks_ledger`
refuses a walk whose fingerprint is not the bar's latest signature; the remedy is to walk again.
The walk's declared limit, that it cannot prove completeness, is unchanged.

Leaving the walk unbound was declined. A re-signing exists because a bar element changed, and a
walk written before it would pass while the changed element went unwalked.

## Ruling 5 — one shared signing module and command, named by skill

The fingerprint, retained copies, reply verification, signing history and the comparison with
the latest signature move into one shared module. Its signing command takes the skill by name and
runs that skill's own bar check before signing. `assignment_bar.py` remains a working command and
calls the shared module, so runs and instructions that cite it keep working. Every grader named in
Ruling 1 uses the one shared comparison.

Inferring the skill from the bar's fields was declined because one discussion run directory can
hold either a post bar or a reply-only bar. A copy of the mechanism beside each skill was declined
because a fix to one copy would fail nothing in the others.

## Not reached

A run whose bar was dated by hand before the command exists has no recorded signature. Its new
checks start through `reference/completion-check-starts.tsv` and report `not graded` for that run
rather than refusing it, as ADR 0355 rules for `course-assignment`.

The build that implements this record edits at least the four skills' signing steps,
`tools/assignment_bar.py`, `tools/research_ledger.py`, `tools/discussion_post_scan.py`,
`tools/discussion_reply_scan.py`, `tools/peer_critique_scan.py`, `tools/checks_ledger.py`,
`reference/completion-check-starts.tsv`, and `CLAUDE.md`'s *Course assignment artifact grading*
section, which names `assignment_bar.py` as the signer. It also edits
`skills/_shared/reference/sourcing.md`'s own-work section, which tells a run with no bar to write
one with `SIGNED` and names the signing command only for `course-assignment`.

## Supersedes

- [ADR 0327](0327-an-unposted-reply-or-critique-s-posted-reading-is-not-graded-and-both-skills-sign-a-bar.md)
  ruling 4, the words "the run writes the date into `SIGNED` only then". The date is written by the
  shared signing command, which fingerprints the bar and carries the clinician's answer at that
  stop. The stop, the three fields, their defaults, the reused post bar and `research_ledger`'s
  refusal of a run with no bar still stand.
