# A proposed image is ruled at its own stop before any grade render or reader and the ruling is the clinician's verified reply

**Measured at:** 5d32d8490b61bba071e0dba6013349aff84d97ad

[#1743](https://github.com/mshamblin5150-code/clinical-skills/issues/1743) was filed from #1559's
grilling. [imagery-proposals.md](../../skills/_shared/reference/imagery-proposals.md) marks a
proposed image in the working draft with an own-line `[[PROPOSED IMAGE <key>]]` and asks the
clinician about it at the go-ahead, after the carriers, page renders, heading read and voice read
were all bound to the marked draft. Grilled 2026-10-17 against `main` at the commit above, where the
freshness gate read `FRESH`; the clinician ruled every point below in that session.

## Measured before ruling

**Every imagery ruling forced a second go-ahead ask, and no skill said so.**
`approval_record.verify_clinician_reply` accepts only a whole clinician message written after the
latest modification time of the approved sources. An imagery ruling edits the draft, and a yes
still deletes the marker line, so the reply that carried the ruling can never be recorded as the
approval of the edited draft. This was read from the function, not driven.

**Nothing strips the working marker before a binding.** `discussion_artifact.strip_discussion_markers`
removes it only for word and number counts. The case-study render fingerprint and
`checks_ledger`'s draft and render digests, the Word-assignment and deck render fingerprints, the
voice-read draft digest and planted-copy comparison, the heading-read `DRAFT` digest, the approval
source fingerprint and the reader-remarks receipt all hash raw bytes that contain the marker line.
`docx_write`, `post_html` and `assignment_docx` copy the marker into the carriers, as #1559 ruled.

**The rework after a ruling differs by skill.** `practicum-case-study` reruns every step 9 row on a
changed draft, and `course-assignment` and `discussion-post` rebuild and re-render, while each says
little more than "rerun the grader". `discussion-reply` and `peer-critique` build their carriers
after approval and render nothing, so only their heading read, voice read and approval repeat.

**The image rows run only at submission.** `imagery_proposals.apply_completion_gate` reports
`not graded` without `--submission`, and `approval_record` refuses `--submission` in the grade it
takes at approval. A run that never asked would discover it after posting.

**The image status has never been verified.** The run writes `proposed-and-approved` into
`imagery-proposals.json` itself. Until now the clinician's answer rode inside the go-ahead reply,
which `approval_record` verifies; the status field was never tied to any message.

**A deck has no text draft before its carrier.** `course-assignment` step 3 generates the `.pptx`
agent-side, so in that branch the deck is the draft. The Word branch writes a JSON spec before
`assignment_docx.py` builds the `.docx`.

## Ruling 1 — a proposed image is ruled at its own stop

When a run proposes an image, it stops once the draft is complete and before the first grade,
carrier build, render or reader. The stop shows each proposal in its surrounding paragraph with
its recorded domain and the behavior it spends, and asks yes or no. The run applies the answer
under `imagery-proposals.md`, so every later binding is computed once over a draft with no marker.
The final go-ahead asks only about substance, except under ruling 2.

Keeping the question at the go-ahead and naming the full rework in each skill was declined: it
documents a rebuild, re-render, reader round, heading read, voice read and second ask that the stop
removes. Keeping it there and having the bindings ignore the marker was declined: the carrier still
prints the marker, the rendered pages showed it, a no still removes a real sentence, and the
approval reply still predates the edit.

## Ruling 2 — a later change to an approved image is reconfirmed at the go-ahead

A repair that rewords or removes an approved image proceeds, and the run marks that image as
changed since the clinician's yes. The final go-ahead shows old and new wording as a separate image
question. A yes updates only the record, so nothing is rebuilt or reread and no second ask follows.
A no restores or removes the sentence, and the skill names the redo that edit owes: rebuild,
re-render with its reader, heading and voice reads, and a new ask. In `course-assignment` this
question sits at Gate 1, because the upload follows it;
[ADR 0384](0384-course-assignment-s-gate-2-and-a-recorded-patient-status-answer-carry-the-clinician-s-whole-reply.md)
ruling 1 gives both branches that gate, and until its build the deck branch calls it the submission
gate.

Reopening the image mid-checks was declined as a second interruption for a change the clinician
will usually accept. Freezing approved images was declined because a finding that can only be fixed
by rewording the sentence falls back to asking anyway.

## Ruling 3 — every grade before submission refuses an unanswered image and a surviving marker

Each of the six coursework graders refuses, without `--submission` and in the grade taken at
approval, a proposal still awaiting the clinician's answer and any working marker in the draft or a
built carrier. An image changed since the clinician's yes is counted there and refused only by the
submission grade when it was never reconfirmed. The row takes a start date in
`reference/completion-check-starts.tsv`, so historical runs are not regraded.

Leaving enforcement to the submission grade was declined because a skipped stop is then found after
the render and every reader have run on a marked draft. Refusing only at approval was declined for
the same reason.

## Ruling 4 — the image stop is not a showing

The stop shows proposals, not the draft. The final go-ahead is the clinician's first full look and
carries no change list under [revisions.md](../../skills/_shared/reference/revisions.md); later asks
compare against it. Retaining a copy at the stop was declined because the first change list would
then compare against a draft the clinician never read. Ruling 2 already covers the one part of the
draft the stop showed.

## Ruling 5 — the stop comes before the first byte-bound step, and a deck's draft is its `.pptx`

The rule is stated as after the draft is complete and before the first grade, render or reader. In
the deck branch the stop follows generation of the `.pptx` and precedes `deck_scan.py`; the answer is
applied by editing the deck. Writing a separate text draft for decks was declined as an artifact
that exists only for this and a second copy of the slide text that can drift from the deck.

## Ruling 6 — the clinician's image answer is recorded as his verified whole reply

The stop records the clinician's whole reply and its time in `imagery-proposals.json`, and the
graders verify it against the transcript with the whole-message verification approvals and bar
signing already use. The reply is verified as written after the draft the stop showed, not after
the edit that applies it; checked against the edited draft's modification time it could never be
found. An unreadable transcript is reported as not verified, never as passed. A
ruling-2 reconfirmation records the go-ahead reply the same way. Keeping the status alone was
declined: ruling 1 removed the verification the answer used to receive inside the go-ahead reply,
and an approved image is excluded from later voice-model harvest as co-written, so its status must
rest on the clinician's words.

## What this record declines from #1743

**Decision 2**, naming the rework after an imagery ruling, survives only for ruling 2's no.

**Decision 3**, having the bindings read the draft with working markers removed, is declined as
moot. No marker reaches a carrier, render, reader, change list or approval once ruling 1 holds, and
ruling 3 refuses one that does. The same holds for the ticket comments' later additions: the
change list, the heading-read digest, and ADR 0363's handoff reruns and blind recount.

**`CLAUDE.md`'s *Coursework imagery proposals* section** says the go-ahead shows each proposal;
the build that implements this record corrects it with the five skills, `imagery-proposals.md`,
`tools/imagery_proposals.py` and the six graders.

[#1559](https://github.com/mshamblin5150-code/clinical-skills/issues/1559)'s ruling stands: the
marker grammar and its stripping for counts are unchanged.

## Supersedes

- [ADR 0276](0276-a-voice-model-records-what-the-writer-argues-from-and-a-stated-rule-binds-on-one-statement.md)
  ruling 9, the words "and shown at the go-ahead". A proposed image is shown and ruled at its own
  stop before any grade, render or reader. Its domain, the property it spends, the separate
  question, the clinician's yes and the harvest exclusion still stand.
