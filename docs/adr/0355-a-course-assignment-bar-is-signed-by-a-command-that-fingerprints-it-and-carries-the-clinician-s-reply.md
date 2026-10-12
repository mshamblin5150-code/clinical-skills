# A course assignment bar is signed by a command that fingerprints it and carries the clinician's reply

**Measured at:** f25e53019d68cced53d58e5953b1920e630c9b25

[#1569](https://github.com/mshamblin5150-code/clinical-skills/issues/1569) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M11) on 2026-10-04. The signed bar for a
DOCX run promised a table in one section. The DOCX producer cannot write one, the agent found that
at the build, and it then edited the signed `bar.md` to say prose without asking the clinician to
sign again. The ticket proposed two checks: refuse a bar line requiring an element the producer
cannot write, and refuse an edit after `SIGNED:` unless a new `SIGNED:` date follows it. Grilled
2026-10-12 against `main`; the clinician ruled every point below in that session. It also rules the
bar-signature limb of [#1648](https://github.com/mshamblin5150-code/clinical-skills/issues/1648),
which asked to be ruled with this ticket. **Nothing is built here; this is the record the build
reads.**

## Measured before ruling

**The DOCX producer writes no table of any kind.** `tools/assignment_docx.py` contains no `w:tbl`.
Its specification carries a title page, Heading 1 sections of paragraphs, optional command rows,
at most one supplied figure with its caption, alt text and note, and references. The command rows
were a Word table until commit `b0da7a6d` (#1426) and are now written as paragraphs under a
`Command Matrix` heading.

**A body table is also forbidden by a ruled house rule.** `skills/_shared/reference/style.md`'s
shared narrative-body rule forbids bulleted lists, numbered lists, and tables in the graded body of
a `course-assignment` Word document, and `assignment_docx_scan.py` reports any such block as a
`narrative-body` finding. The M11 bar therefore promised something the house rule forbids as well
as something the producer cannot make.

**The bar has no line a gate could read for this.** `assignment_bar.py` reads the shared envelope
fields and each branch grader reads its container fields. Everything below those fields, including
the transcribed assignment wording where the table was promised, is free prose no tool reads.
`references/docx.md` describes what the producer writes only after the signing step.

**Nothing records what the clinician signed.** The agent writes the `SIGNED:` date into `bar.md`
by hand after his confirmation; `assignment_bar.parse` checks only that it is an ISO date. No tool
fingerprints `bar.md`. `assignment_submission.py` and `frozen_grade.py` fingerprint the artifact and
its carriers, never the bar. The ticket's proposed check rests on that same agent-written date,
which is the weakness #1648 names: [ADR 0310](0310-an-approval-carries-the-clinician-s-whole-reply-and-is-refused-when-his-messages-do-not-hold-it.md)
checks the clinician's whole reply against his own messages, but only for
`approval_record.approve`, and its ruling 2 leaves `course-assignment` outside.

**Deck and DOCX bars share one envelope.** `assignment_bar.py` parses both and dispatches through
`ADAPTERS`. `discussion-post`, `discussion-reply`, `peer-critique`, and `practicum-case-study` each
sign a bar of their own grammar, and none of the five skills detects an edit after signing.

## Ruling 1 — no required-elements field; the producer's reach is stated before signing

The bar gains no structured field listing required elements. Instead, before the DOCX bar is shown
to the clinician, the signing step states what the producer writes (prose sections, at most one
supplied figure, references) and what the narrative-body rule forbids (tables and lists). An
assignment requirement outside that set is put to the clinician before he signs: either the bar
records the requirement's omission and why, or the run pauses while the producer is extended
through a ticket. This follows the stop-at-the-clinician precedent of ADR 0255 ruling 8.

A closed required-elements field checked against a producer-exported set was declined: it grades
only what the agent transcribes into the field, so an element left out of it escapes the same way
the table's mismatch did, while every DOCX bar pays for one more required field. Changing nothing
here was declined because discovery at the build costs a sitting. The enforcement is Ruling 2: once
an edit to a signed bar cannot pass, an impossible promise found late can only come back to the
clinician.

## Ruling 2 — signing is a command that fingerprints the bar

After the clinician confirms, the agent signs by running one command. It writes the `SIGNED:` date,
records the SHA-256 of the resulting `bar.md` bytes, and retains a copy of each signed version in
the run. The bar check (`course_assignment_scan.py --bar-only`), the completion grade, and both
submission gates refuse when `bar.md` no longer matches its latest signature. Signing again means
running the command again after a new confirmation; the retained copies show what changed between
signings.

The ticket's form, a later `SIGNED:` date, was declined because the date carries no time of day,
so an edit on the signing day passes, and because a date is not evidence of what was signed.
Comparing file modification times was declined for the same day-granularity reason and because
copying a run between checkouts changes them. Keeping `bar.md` under version control was declined
because run directories are private and outside the tracked tree.

## Ruling 3 — the signature carries the clinician's reply, checked against his messages

The signing command receives the clinician's reply that confirmed the bar and checks it against his
own messages with ADR 0310's predicate and terms: the whole message compared with spacing ignored,
refused when his readable messages do not hold it, and recorded as not verified when the transcript
cannot be read. Every signing carries its own reply, the first and every later one. The reply is
kept beside the fingerprint of the bar it signed.

Without this, the fingerprint only moves the M11 departure: the agent that rewrote the bar could
re-run the signing command on its own. Recording the signature on the agent's word alone was
declined for that reason. The check proves he wrote those words, never that his words were about
the bar; that limit is the same one ADR 0310 declares. This rules #1648's bar-signature limb only.
Its two `course-assignment` submission gates and the recorded patient-status answer stay on #1648.

## Ruling 4 — the scope is the course-assignment bar, deck and DOCX alike

Rulings 2, 3 and 5 apply to every `course-assignment` bar, because both branches share the envelope
the command lands in. Ruling 1 is DOCX only, since the deck has no repository producer. Limiting the
signature to DOCX bars was declined: deck bars sign more fields an agent might rewrite (slide limit,
font, talk style) and share the same code. The other four skills that sign a bar share neither code
nor grammar with this one, so applying the same treatment to them is filed as its own ticket rather
than widening this one.

## Ruling 5 — a conflict found at the build is a re-signing that shows its change

When the build finds that the signed bar promises something the producer cannot make, or the house
rule forbids, the agent stops. It shows the clinician the old and new wording of each changed bar
line and the reason, and waits. His reply either signs the amended bar through Ruling 2's command
or keeps the requirement and pauses the run while the producer is extended. Every re-signing works
this way, including the mid-run admission of the clinician's own unpublished work under
[ADR 0322](0322-the-clinician-s-own-unpublished-work-is-a-source-class-a-bar-opts-into-and-is-located-by-path-and-fingerprint.md)
ruling 2, whose request message is the reply this command checks.

A re-signing request without the changed lines was declined because his approval would then cover
an edit he had not seen, which is the blind spot M11 used. Ending the run on any conflict was
declined because one sentence of agreement settles most of them.

## Not reached

A run whose bar was signed before the command exists has no recorded signature. Its new checks
start through `reference/completion-check-starts.tsv` like any later check and report `not graded`
for that run rather than refusing it. The M11 submission itself is recorded on #1569 and nowhere
changed: a Canvas submission is never edited or reposted to fix a defect.
