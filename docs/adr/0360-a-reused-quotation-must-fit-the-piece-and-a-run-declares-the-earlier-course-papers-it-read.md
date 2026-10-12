# A reused quotation must fit the piece and a run declares the earlier course papers it read

**Measured at:** b6dc5d408fc3b56f22cfac505b331fcea65c5c5e

[#1573](https://github.com/mshamblin5150-code/clinical-skills/issues/1573) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M11) on 2026-10-04. The draft reused a
quotation and an image the clinician had used in the same course's previous module days earlier.
The voice read caught it and both were replaced. The ticket proposed telling `course-assignment`
to read the course's earlier submissions and not reuse a quotation or image already used there.
Grilled 2026-10-12 against `main`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Nothing reads a course's earlier papers today.** None of the five coursework skills tells a
run to read them, and no tool or grader compares a draft's quotations or images with an earlier
submission. The `OWN-SUBMISSION` line of
[ADR 0325](0325-a-classmate-s-order-counts-only-for-the-patient-the-case-presents-and-the-clinician-s-own-submission-is-a-declared-context-place.md)
ruling 4 covers a submission already handed in on the same board or case, never an earlier
module. The project registry names no course, and nothing in `tools/` models a course series.

**The M11 catch was incidental.** The voice reader receives only the planted copy, the supplied
voice record, and the canonical voice model. That model still carries, at line 609 under the
clinician's rules for philosophy in graded work, "Never reuse a quotation across papers," a rule
the clinician narrowed on 2026-10-01 to a within-series tendency. The narrowed wording approved
that day was never applied to the model.

**Every coursework skill carries the same image paragraph.** `course-assignment`,
`discussion-post`, `discussion-reply`, `peer-critique` and `practicum-case-study` each say
"Reuse a recorded image whole where it fits," under
[ADR 0276](0276-a-voice-model-records-what-the-writer-argues-from-and-a-stated-rule-binds-on-one-statement.md).

**Course codes in run keys and filenames are inconsistent.** Both `nur5042` and `nur-5042` occur,
likewise `nur5144` and `nur-5144`; one finished assignment is named by course title rather than
code; and course numbers in filenames are known to be transposed at times. A course's earlier
papers therefore cannot be enumerated reliably from names.

## Ruling 1 — a reused quotation or image is judged by fit, never by repetition

Reusing a quotation within a course is fine when it fits the work at hand. If a quotation was
already used earlier in the course, the run frames it for this piece rather than carrying the
earlier paper's framing, or uses a different quotation from the same source that fits better. The
defect is a quotation present because it was used before rather than because it fits, or one
carrying the earlier paper's framing. The clinician's recorded images take the same test: still
used whole under ADR 0276, but making this piece's point. The ticket's flat "do not reuse" was
declined, since he reuses quotations in his own work framed in different ways. The 2026-10-01
"prefer a fresh quotation within one series" reading is replaced by this one; it treated the
repeat itself as the problem. Fit is a reader's judgment and no tool grades it.

## Ruling 2 — the earlier papers are the whole **Course history**

The run reads every submission the clinician already handed in earlier in the same course: initial
posts, replies, assignments, case studies and critiques. Reading only earlier work of the same
type was declined, because the same instructor reads every type and a framing used in a
discussion post can return in the next assignment. Excluding replies to classmates was declined
as a small saving that leaves a gap someone must remember.

## Ruling 3 — all five coursework skills, from one shared section

The rule is written once, in a new section of
[voice.md](../../skills/_shared/reference/voice.md), and each of the five coursework skills points
to it beside its existing "Reuse a recorded image whole where it fits" paragraph. Placing it in
`course-assignment` alone, as the ticket proposed, was declined because the scope in ruling 2
counts every type of work; limiting it to the three long-form skills was declined because replies
and critiques carry quotations too.

## Ruling 4 — a declared, opened `COURSE-HISTORY` line in the project-context record

The project-context record gains a confirmed header line, repeated once per earlier paper:

```text
COURSE-HISTORY: <absolute path to one earlier submission in this course>
COURSE-HISTORY: none - <reason>
```

`tools/project_context.py` refuses a record with no `COURSE-HISTORY` line, a `none` without a
reason, `none` beside a path, a duplicated path, or a declared path not shown opened as an item of
a `read` place, on the same terms as `OWN-SUBMISSION`. The declared lines join the context digest
beside the other declared header lines. An instruction alone was declined: a skipped read and a
first module with no earlier papers leave the same silence, which is ADR 0325 ruling 4's reason
again. A tool deriving the expected list from file and folder names was declined while those names
are unreliable; it would miss papers or refuse correct runs. The accepted cost is that the gate
cannot tell whether the declared list is complete, and that limit is written into
`project_context.DECLARED_LIMITS`. Deriving the list becomes possible only after a separate change
gives every run a reliable course code.

## Ruling 5 — the go-ahead shows a reuse list, and says so when there is none

At the go-ahead, the run shows each quotation or image in the draft that also appears in an
earlier course paper, with that paper, one line on how it was framed there, and one line on how it
is framed now. When there is none, one line says so. The clinician judges fit from those two
framings side by side. Giving the voice reader the earlier papers was declined: that reader is
deliberately blind to everything except the canonical model and the draft, and its verdict would
reach him only when it flagged. The accepted cost is that the list is built by the drafting run
and no grader checks its contents or completeness.

## Ruling 6 — the voice model's line 609 is replaced when no recorded run is open

The build replaces line 609 of the canonical voice model with:

> - **A reused quotation must fit the piece.** Reusing a quotation across papers, including within one course, is fine when it fits the work at hand. Frame it for this piece rather than carrying over an earlier paper's framing, or use a different quotation from the same source that fits better. His recorded images take the same test: used whole, making this piece's point. *Restated by the clinician 2026-10-12 (#1573), replacing the 2025-07-16 instruction "Do not use the same quotes from Marcus and musashi used in the previous paper" and the 2026-10-01 narrowing.*

The edit is made only when no coursework run with a recorded voice-model identity remains open,
because it moves the digest those runs' completion graders recheck; the clinician then confirms the
model reads right. The 2026-10-01 replacement text is not applied. Applying the edit during the
grilling session was declined so the model and the shared voice section change together.

## Consequence for the build

The `COURSE-HISTORY` check enters `reference/completion-check-starts.tsv` like every later check,
under [ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md),
so a record confirmed before the build reports it `not graded` rather than failing.
