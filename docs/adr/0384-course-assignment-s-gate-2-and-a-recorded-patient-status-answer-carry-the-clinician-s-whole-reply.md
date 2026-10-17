# Course-assignment's Gate 2 and a recorded patient-status answer carry the clinician's whole reply

**Measured at:** a1c440906ee7d1594dd7bcb6e66a21d7d6e54f1b

[#1648](https://github.com/mshamblin5150-code/clinical-skills/issues/1648) was filed from the
tracker sweep closing #1474's grilling on 2026-10-09. [ADR 0310](0310-an-approval-carries-the-clinician-s-whole-reply-and-is-refused-when-his-messages-do-not-hold-it.md)
requires every approval recorded through `approval_record.approve` to carry the clinician's whole
reply, checked against his own messages. The ticket named three other places where an agent writes a
record that stands for his word and nothing checks it. Grilled 2026-10-16 against `main`; the
clinician ruled every point below in that session. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

**Two of the three limbs had moved since filing.** #1501's build made `assignment_submission.stage`
(Gate 1) take `clinician_reply` and refuse unless `approval_record.verify_clinician_reply` returns
`verified`. [ADR 0355](0355-a-course-assignment-bar-is-signed-by-a-command-that-fingerprints-it-and-carries-the-clinician-s-reply.md)
rulings 2 and 3 ruled the bar signature, and #1569's build put `verify_clinician_reply` into
`tools/assignment_bar.py`. What remained was Gate 2 and the patient-status answer.

**Gate 2 is a boolean the agent supplies.** `assignment_submission.confirm` takes
`final_confirmation: bool`, refuses only when it is false, and records the agent upload route in
`submission-gates.json`. No reply text reaches it.

**The deck branch writes no stop before Submit.** `skills/course-assignment/SKILL.md`'s deck branch
says "wait for the explicit go-ahead once", stages, uploads, inspects, calls `confirm` with
`final_confirmation=True`, and submits. Only `skills/course-assignment/references/docx.md` defines a
separate Gate 2 ("Gate 1 never authorizes the **Submit Assignment** click").

**The completion grade does not read Gate 2.** `assignment_submission.completion_gate` requires
`gate1_approved`, an agent or clinician upload route, and the approved carrier population. A run
whose agent route was recorded with no reply grades as complete.

**The status answer is graded on its shape.** `coding_freshness.STATUS_EVIDENCE` accepts
`identity-map`, `medatrax` and `clinician-answer`, and the gate checks only that the evidence kind is
one of those and that `evidence_sha256` is shaped like a SHA-256. It never opens the evidence or
compares it with a message. `skills/batch-shift/SKILL.md` says "A delegate never answers this
question", and [#1461](https://github.com/mshamblin5150-code/clinical-skills/issues/1461) records a
delegated ruling standing in for the clinician in the same shift family.

**The other posting skills already wait and check.** [ADR 0331](0331-every-canvas-save-waits-at-the-loaded-box-for-a-recorded-go-ahead-and-plain-text-is-built-by-one-command.md)
ruling 2 records a Posting go-ahead for `discussion-post`, `discussion-reply`, `peer-critique` and
`practicum-case-study` through a second `approve` call, and its completion row refuses a run-posted
item without one. Its "What this does not reach" leaves `course-assignment`'s gates to #1648.

## Ruling 1 — both course-assignment branches stop after upload for the clinician's word

Deck and DOCX runs alike stop after the approved carriers are uploaded and the Canvas assignment page
is inspected, and wait for the clinician's word before the **Submit Assignment** click. Gate 1
authorizes the upload and never the click. The deck branch's single go-ahead is retired.

A boolean Gate 2 behind a stop was declined because the record still could not show that he said
submit, which is the hole ADR 0310 closed everywhere else. Giving the DOCX branch the reply check
while the deck kept its single go-ahead was declined: a deck is equally graded, the click is equally
irreversible on an append-only LMS, and one skill's two branches would treat the same click
differently. Leaving both unchanged was declined for the departure #1474 recorded.

## Ruling 2 — Gate 2 carries the whole reply through course-assignment's own record

`assignment_submission.confirm` takes the clinician's whole reply and calls
`approval_record.verify_clinician_reply` with ADR 0310's terms: the whole message compared with
spacing ignored, refused when his readable messages do not hold it or the transcript cannot be read.
The reply must follow Gate 1's matched reply and the uploaded carriers. It is stored beside Gate 1's
in `submission-gates.json` with its match time. Only the whole-reply predicate carries over;
[ADR 0318](0318-rendered-pages-waits-for-a-load-and-an-approval-needs-the-whole-text-shown.md)
ruling 4's shown-text check stays out, as its ruling 3 left `course-assignment` out because the
review is the rendered page images.

Moving both gates onto `approval_record.approve` was declined. It would rewrite the gate record and
its readers (the completion grade, the after-action review's read and the run-status hook's
registration) for no clinical gain, and it would import the shown-text check ruled not to fit this
skill or force a new exemption.

## Ruling 3 — the completion grade refuses an agent submission with no verified Gate 2 reply

`assignment_submission.completion_gate` refuses a run whose upload route is the agent's and whose
record holds no verified Gate 2 reply. A run recorded through `record_clinician_upload` owes none,
because the stop exists for the run's own click. Runs whose Gate 1 was recorded before the build
lands start the check through `reference/completion-check-starts.tsv` and report `not graded` for it.

Without the row, an agent that never calls `confirm` and clicks Submit anyway leaves nothing a later
grade notices, the failure ADR 0331 recorded twice. Grading historical runs without a start date was
declined because a correctly finished run would become a finding for a rule that did not exist when
it ran. This is ADR 0331 ruling 2's arrangement, so all five posting skills carry one rule.

## Ruling 4 — a clinician-answer status carries his whole reply and is checked before the pass

A patient-status record whose evidence is `clinician-answer` carries the clinician's whole reply to
the pre-approval questions block, verbatim, even where one message answers several questions.
`coding_freshness.py` checks that reply with `approval_record.verify_clinician_reply` under ADR
0310's terms and requires it to follow the day file or shorthand it answers. A reply his messages do
not hold, or messages that cannot be read, refuse the batch and write no pass receipt. A delegated
run cannot record `clinician-answer`; its fallback stays the skill's own (no record means new, named
in the go-ahead message), which uses `identity-map` or `medatrax` evidence.

Relying on the Review-sheet go-ahead with the worksheet naming the answer was declined: one approval
of a whole shift's sheet would stand as the only evidence of a single per-patient answer, and the
field sets a billed E/M code. Leaving the written rule was declined for #1461's departure.

*Superseded 2026-10-17.* The words "the clinician's whole reply to the pre-approval questions block, verbatim" are superseded by [ADR 0404](0404-an-ambiguous-answer-is-read-back-and-earlier-care-status-is-asked-at-the-first-stop.md) ruling 4. The recorded reply is his whole reply, verbatim, to whichever stop asked the earlier-visit question, the `batch-shift` step 4 stop or the pre-approval questions block. The check through `approval_record.verify_clinician_reply`, the requirement to follow the day file or shorthand, the refusal of an unheld reply, and the delegated fallback still stand.

## What this does not reach

- **Whether his words were about the click or the status.** The check proves he wrote those words
  after the named point, never what they referred to; ADR 0310 declares the same limit.
- **Whether he looked at the loaded Canvas page.** As ADR 0331 states for the other four skills.
- **ADR 0302 ruling 2 and ADR 0310 ruling 2.** Both stand. This record adds a reply requirement to
  the `clinician-answer` evidence kind ADR 0302 admitted, and answers the question ADR 0310 ruling 2
  left to the clinician; it overturns neither.
