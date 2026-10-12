# The DOCX heading read runs before the render, and overstated evidence is drift

**Measured at:** 05c8cf44a16557ac46c50ee193d65a918390f108

[#1567](https://github.com/mshamblin5150-code/clinical-skills/issues/1567) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M11) on 2026-10-04. Across many
rebuilds, each fresh heading read found one to seven DOCX sentences that claimed more than the
claim heading they rest on. Each finding cost a full rebuild, a Word render, and three fresh reads,
and one instance (a single trial written as though a review corroborated it) remains in the
submitted paper. The ticket proposed a dry-run heading read on a Markdown draft before the first
build. Grilled 2026-10-12 against `main`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The heading read does not need the render.** `tools/assignment_docx_scan.py` binds the heading
read with `heading_read.Binding(source.docx.name, source.docx_bytes, ...)`: the `.docx` name and raw
bytes, `claims.md`, and the project-context digest. No retained pass, page image, or `rendered.md`
record enters the binding. `tools/heading_read.py` refuses a record whose `DRAFT` digest differs
from the current bytes as `heading-read-draft-mismatch`, so a read taken before a later change
cannot pass the grader.

**The render is what each heading fix paid for.** The DOCX is written from a private JSON
specification by `tools/assignment_docx.py` in seconds without Office. `skills/course-assignment/references/docx.md`
then requires a fresh Word render and a fresh visual read after every change. Neither
`skills/course-assignment/SKILL.md` ("Heading read for both artifacts") nor `docx.md` orders the
DOCX heading read relative to the render; it says only "before the go-ahead". So a heading-read
repair paid for a render and a visual read it never needed, and the voice read that follows the
final artifact repeated as well.

**The DOCX branch has no Markdown draft.** `docx.md` names the JSON specification as authoritative
and says Markdown is not a substitute submission. A heading-read record for any other filename is
counted by `_other_files` and never graded, so a dry run on a draft file would be an ungraded read.

**ADR 0262's order does not carry over.** That record keeps the deck heading read last because the
deck's adversarial (investor) read can change `claims.md` after the render. The DOCX branch has no
adversarial read.

**Two of the ticket's six shapes fall outside the written definition of `drifted`.** The shared
brief in `skills/_shared/reference/sourcing.md` names a broader population or subject, a changed
number, an added entity or condition, and a dropped limitation. A dropped population or medium
limit, a dropped search window, an added comparison, and a regulation widened from texts to calls
fit those words. One physician's opinion written as a general standard, and one trial written as
two corroborating sources, overstate the strength or number of the evidence and are named by none
of them. The ticket's word "observation" for the reader notes that carried several of these is
the term ADR 0330 ruling 7 declined; such a note is a **Reader remark**.

## Ruling 1 — the DOCX heading read runs on the built file before the Word render

In the DOCX branch, the order becomes: build the `.docx` from the specification, run the real,
recorded heading read on it, and repair through the specification and re-read until the record is
clean. Only then run `assignment_docx_render.py`, `render_scan.py`, and the visual read. When a
visual repair changes the `.docx`, the heading read repeats on the new bytes, exactly as a stale
`DRAFT` digest already requires. The voice read still runs after the artifact is final.

The pre-render loop uses the existing grader. `assignment_docx_scan.py` reports the heading-read
rows on that run; its `rendered-record` row is expected to fire until the render and is not a stop
at that point. No new command, record kind, or grader row is added.

A dry-run heading read on a draft before the first build was declined: the branch has no draft in
that form, the grader cannot see a record for another filename, and an ungraded read can be skipped
without anyone knowing. Keeping both the dry run and the reorder was declined for the same reason,
plus two kinds of heading read that a reader of the record could confuse.

## Ruling 2 — overstated evidence is `drifted`

The shared heading-reader definition names overstated evidence as `drifted`. A sentence that
presents one opinion as a general standard, or one source as several agreeing sources, claims more
than its heading. The rule lives in the shared brief and therefore applies to every coursework
heading reader, not only `course-assignment`.

Leaving such sentences to the remark route was declined because each would wait for the clinician
at the go-ahead, and a remark approved past without a fix still ships, which is how the
single-trial sentence reached the submitted paper. Naming the shapes only in the
`course-assignment` brief was declined because one question would then get two answers across the
coursework skills.

## Ruling 3 — the fresh complete read is the re-check

No writer self-check against earlier findings is added, and the fresh reader is not given the list
of earlier findings. Every heading read is a complete read of every factual sentence, so a repaired
shape that returns is caught by the next read, and under Ruling 1 a recurrence costs one reader
rather than a render and three reads. A written self-check was declined because nothing grades it.
Priming the reader was declined because a reader looking for familiar mistakes may miss new ones.

## Ruling 4 — the deck branch is unchanged

ADR 0262's deck order stands. No deck run has measured the drift loop, and the deck order rests on
the adversarial read's ledger edits, which the DOCX branch lacks. A deck run that hits the same loop
is filed by its own after-action review with a measurement.

## Not reached

The single-trial sentence in the submitted NUR 5042 M11 paper is recorded on #1567 and nowhere
changed: a Canvas submission is never edited or reposted to fix a defect.
