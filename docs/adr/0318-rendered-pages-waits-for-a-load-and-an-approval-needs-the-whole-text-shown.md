# The rendered-pages row waits for a load, and an approval needs the whole text shown

**Measured at:** bb2caf2a07e6c2bf08f9be3cba76b00b7805c7ad

[#1484](https://github.com/mshamblin5150-code/clinical-skills/issues/1484) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 9) on 2026-10-01, and its second and
third limbs recurred on the Module 10 run the same day. It names three sequencing defects in step 8:
a Gate 1 re-ask made without the post's text, posting fields that a render record absorbed, and a
Gate 1 approval that cannot pass. Grilled 2026-10-10 against `main`, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this is the
record the build reads.**

## Measured before ruling

**Two pre-load grader runs in step 8 fail on every first load.** Step 8 calls
`approval_record.approve` at Gate 1 with `--html` and `--docx`, and separately says "Before loading,
regenerate both `.html` and `.docx` from the checked Markdown and rerun the grader with both
carriers." `discussion_post_scan._rendered_page_findings` files `rendered-pages: no RENDERED record
for the Canvas box` whenever `--html` is given and no render record exists, and none can exist before
the load. `approve` refuses on any grader exit other than 0 or 2, so Gate 1 is refused. Both filed runs
recorded Gate 1 with `--draft` alone and called `approve` again with both carriers at Gate 2. The
pre-load rerun was read, not driven; it is the same grader call on the same run state. ADR 0283
ruling 2 put that rerun before loading to catch a stale carrier, a finding that the always-firing
rendered-pages finding makes indistinguishable by exit status.

**Only the render-record parser rejects the posting fields.** `RENDERED_BLOCK` ends a record at the
next `## ` heading or the end of the file, so `POST-URL:` and `POSTED:` appended after the last record
are read as its fields and refused as unrecognized. The scanner's whole-file field read and
`check_posted_reading`'s comparison with `reread.md` find both fields wherever they sit.

**The text-posting skills ask for approval without requiring the whole text.** `discussion-post` says
"Show the final post", `discussion-reply` "Show the clean reply", and `peer-critique` "Show the clean
critique". None requires the complete text and reference list, and none says what a re-ask after a
revision shows. `approve` already reads the session transcripts to match the clinician's whole reply
after the sources last changed (ADR 0310), so the assistant messages in the same window are readable
by the same discovery.

**The sequencing concern in #1484's last comment is settled.** #1474 has closed, and step 8 already
passes `clinician_reply` at both gates.

## Ruling 1 — rendered-pages is not graded before anything was loaded

When the run directory holds no Canvas-box render pass and the posting is not recorded, the
rendered-pages row of `discussion_post_scan.py` is reported not graded and counts as incomplete
coverage, exit 2, instead of a finding. Once a Canvas-box render pass exists, or the posting is
recorded, a missing render record is a finding exactly as today. The Gate 1 call keeps `--html` and
`--docx`, so its fingerprint check still compares both carriers with the approved Markdown; `approve`
discloses the incomplete row and records the approval. The pre-load rerun follows the same posture:
exit 1 stops the load, and exit 2 is disclosed and does not block.

The ticket's proposal, Gate 1 grading `--draft` alone, was declined because it drops the carrier
fingerprint check at the point the clinician approves, and it leaves the pre-load rerun failing on
every run, whose only cure under that proposal also drops the stale-carrier check ADR 0283 ruling 2
placed there. A `--before-load` flag was declined because nothing catches it passed at the wrong time.
The state is read from the run directory, so no caller can declare it. A run that never takes the
Canvas-box render still cannot finish: the final post-posting run must exit 0.

## Ruling 2 — the posting fields get their own heading

After posting, the run appends a `## POSTING: post.md` block holding `POST-URL:` and `POSTED:`. The
heading ends any render record above it, and the whole-file field read still finds both fields. The
render-record parser is unchanged. Older runs that wrote the bare fields above their first record
still read.

Writing the bare fields above the first render record, as filed, was declined because it is an
instruction to insert into the middle of a file, which is the instruction missed on both runs, and
nothing grades the placement. Ending a render record at its own field set was declined because it
weakens the parser: a misspelled field at the end of a real record would fall outside it silently.
The heading reads `POSTING` rather than `POSTED` so it cannot be read as the field beneath it.

## Ruling 3 — every approval ask shows the whole text, in three skills

At `discussion-post` Gate 1 and at the `discussion-reply` and `peer-critique` go-aheads, every ask for
approval shows the complete final text with its full reference list before the approval question,
including an ask repeated after a revision. `course-assignment` is unchanged because its review is
the rendered page images.

Writing the rule in `discussion-post` alone, as filed, was declined because the same gap stands at the
other two text-posting go-aheads and closing it there costs one sentence each. A separate ticket for
those two was declined as a second sitting for that sentence.

## Ruling 4 — the approval refuses when the text was not shown

For those three skills, `approval_record.approve` refuses the first approval of each source
fingerprint unless the assistant messages after the sources last changed and before the clinician's
matched reply contain every nonblank block of the approved text that `docx_write.blocks` derives,
headings, paragraphs and reference entries alike, compared with whitespace collapsed. The refusal
names how many blocks were missing and quotes none of them. A revision changes the fingerprint and
moves the window, so a bare re-ask after an edit is refused. A later approval of an unchanged
fingerprint, which is `discussion-post` Gate 2's approval of the loaded box, is exempt. An unreadable
transcript leaves the check incomplete, as the reply check is today.

A written rule alone was declined because a skipped instruction is the defect this ticket records, and
the transcript reading that catches it already exists. Recording the shown count without refusing was
declined because it documents a summarized approval after it was accepted. The cost accepted is a
false refusal when the agent reformats a block in chat; the remedy is to show the text verbatim.

## What the build changes

- `tools/discussion_post_scan.py`: rendered-pages is not graded, exit 2, until a Canvas-box render
  pass exists or the posting is recorded.
- `skills/discussion-post/SKILL.md` step 8: the pre-load rerun's exit posture; the
  `## POSTING: post.md` block in place of the bare fields; the whole-text rule at Gate 1.
- `skills/discussion-reply/SKILL.md` and `skills/peer-critique/SKILL.md`: the whole-text rule at the
  go-ahead.
- `tools/approval_record.py`: the shown-text check of ruling 4 for the three skills, with tests that
  drive a summarized ask, a bare re-ask after a revision, a verbatim ask, an exempt Gate 2, and an
  unreadable transcript.
- Tests that a posting block after a render record scans clean and that each skill carries the rule.

## What this does not reach

- **Whether the text shown was read.** The check proves the blocks were in the agent's messages, not
  that the clinician read them.
- **Completion.** The shown-text check runs at approval; nothing re-runs it when the run completes.
- **Text shown outside the transcript.** A post displayed by another route, such as a file the
  clinician opened, is not seen and the approval is refused.
