# The heading read has no self walk and one course assignment brief covers both artifacts

**Measured at:** 5857d147ba83dc0ff59caa2b471b91bb049470c8

[#1524](https://github.com/mshamblin5150-code/clinical-skills/issues/1524) was filed from #1217's
grilling, whose measurement of every Second reader outside `practicum-case-study` found three defects
in the heading-read surfaces: input lists naming three inputs where the protocol gives four, a route
that lets the read finish with no second context, and a DOCX branch with no heading-read brief.
Grilled 2026-10-11 against `main`, where the freshness gate read `FRESH`; the clinician ruled both
points below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Two records answer the no-second-context case oppositely, a day apart, and neither names the
other.** [ADR 0194](0194-a-briefing-surface-declares-its-kind-and-points-at-standing-rule-6.md)
ruling 4, grilled 2026-09-12, rules that a Second reader stops when the reader would be the author,
and [AGENTS.md](../../AGENTS.md) standing rule 6 carries it: "A **Second reader** does not complete
when no second context is available." [ADR 0219](0219-a-refutation-fingerprints-its-heading-and-a-reader-pairs-the-draft.md)
ruling 9, grilled 2026-09-13, lets a harness with no subagent tool use "a written walk by the
orchestrator", recorded as `ROUTE: orchestrator walk`. ADR 0219 does not cite ADR 0194.

**The walk is written into six surfaces and the shared grader.** A tracked search for the phrase
outside `docs/adr/` finds it in `skills/_shared/reference/sourcing.md` (the prose and the record
shape), the heading-read paragraphs of `discussion-post`, `discussion-reply`, `peer-critique` and
`course-assignment`, the `practicum-case-study` step 9 heading-read row and that skill's
`unknown-heading-read-route` legend row, `tools/heading_read.py`'s `ROUTES`, and one test in
`tools/test_heading_read.py` asserting a walk record grades clean. `practicum-case-study` step 9's
own floor says a row with no second context stays incomplete and the document is not submitted, so
that skill carried both answers.

**No run has used the walk.** Thirty-nine `.md` files under the owning checkout's `scratch/` and
`output/` and every registered worktree's `scratch/` carry a line beginning `ROUTE: separate
context`; none carries one beginning `ROUTE: orchestrator walk`. The search reads `.md` files only,
so the count is a floor.

**The DOCX heading read is already fully specified by its grader.** `tools/assignment_docx_scan.py`
reads `<run-directory>/heading-read.md` and binds it through `heading_read.scan` to the final
`.docx`'s name and bytes, the run's `claims.md`, the recorded project-context digest and its opened
items, which is the deck binding with the artifact swapped. What is missing is only the brief: the
`course-assignment` heading-read paragraph names the `.pptx` alone, and
`skills/course-assignment/references/docx.md` lists the rows and states no input.

**Two of item 1's four surfaces are already repaired.** [ADR 0336](0336-a-classmate-s-words-are-declared-context-items-keyed-to-the-reply-that-owes-them.md)
ruling 5 gave #1506's build the project-context item pointers in `discussion-reply` and
`peer-critique`, and that build has landed them. `discussion-post` and `course-assignment` remain.

## Ruling 1 — a heading read with no second context does not complete

The heading read is a Second reader under standing rule 6, with no exception. When no second context
can be obtained the record is not written, the go-ahead is not given, and the artifact is not
submitted. The shared record's `ROUTE` field takes the single value `separate context`, and
`tools/heading_read.py` refuses any other value, `orchestrator walk` included, as an
`unknown-heading-read-route` finding. No preserved record uses the walk, so nothing is grandfathered.

The written walk was declined because it brings back the failure the heading read exists to catch:
#1032's run rewrote a claim and checked its own work. Keeping the walk as a named exception to
standing rule 6, with the self-authorship shown in the record and at the go-ahead, was declined for
the same reason and because the floor carries no exception today. Keeping the walk but blocking the
submission until the clinician waives it by name was declined as a third posture with a new waiver
path in five graders, for a route no run has taken. The cost is stated rather than hidden: a harness
without a subagent tool cannot finish `discussion-post`, `discussion-reply`, `peer-critique`,
`course-assignment` or `practicum-case-study`, the same stop the voice read already imposes.

## Ruling 2 — one course-assignment heading-read paragraph covers the deck and the DOCX

The `course-assignment` SKILL.md heading-read paragraph becomes the brief for both artifacts. Its
reader receives the final `.pptx` or `.docx`, `claims.md`, the printed heading digests, and every
item pointer recorded in `project-context.md`, which it opens itself. Locations name slide bullets
and speaker-note sentences for a deck, and body paragraphs, table cells, captions and figure notes
for a DOCX. `references/docx.md` keeps its list of heading-read rows and links to that paragraph
rather than carrying a brief of its own.

A separate DOCX brief in `docx.md` was declined as two copies of one brief inside one skill: a later
change such as ADR 0330's remark line or ruling 1's removed route would have to land twice, and an
edit to one copy fails nothing when the other is missed. The voice-read paragraph directly above
already covers "the deck or DOCX" in one place.

## Supersedes

- [ADR 0219](0219-a-refutation-fingerprints-its-heading-and-a-reader-pairs-the-draft.md) ruling 9,
  the words "A harness with no subagent tool uses a written walk by the orchestrator, and the
  record's `ROUTE:` states which ran." The fresh reader, its blinding from the sources, and the
  copied digests stand.
- [ADR 0219](0219-a-refutation-fingerprints-its-heading-and-a-reader-pairs-the-draft.md) ruling 10,
  the words "ROUTE: separate context | orchestrator walk". The record shape, its other fields, and
  each skill's grader requirement stand.

## Build checklist

- `tools/heading_read.py`: `ROUTES` holds `separate context` alone; the
  `unknown-heading-read-route` row's description follows. `tools/test_heading_read.py`: the walk
  record becomes a refused case, and a `separate context` record stays clean.
- `skills/_shared/reference/sourcing.md`: the sentence permitting the walk is replaced by the stop
  rule, pointing at standing rule 6; the record shape reads `ROUTE: separate context`.
- `skills/discussion-post/SKILL.md`, `skills/discussion-reply/SKILL.md`,
  `skills/peer-critique/SKILL.md`: the sentence "With no second context, write `ROUTE: orchestrator
  walk`" becomes the stop rule. `discussion-post`'s "receives only" sentence also gains every item
  pointer recorded in `project-context.md`, which the reader opens itself.
- `skills/course-assignment/SKILL.md`: the heading-read paragraph is rewritten under ruling 2 and
  ends with the stop rule.
- `skills/course-assignment/references/docx.md`: the heading-read row list links to that paragraph.
- `skills/practicum-case-study/SKILL.md`: the heading-read row's final sentence becomes the stop
  rule, and the `unknown-heading-read-route` legend row reads "`ROUTE` is not `separate context`".
- Every grader row list or legend that names the route values is re-derived from `heading_read`
  rather than edited by hand where one already imports it.

[ADR 0330](0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md)'s build also
edits these heading-read paragraphs to add the `REMARK:` placement sentence. Whichever build lands
second carries both edits, and the one shared course-assignment paragraph now states that sentence
for the DOCX as well.

## What this record does not reach

- **Whether `ROUTE: separate context` is true.** Reader independence stays orchestrator-owned, as
  `heading_read`'s declared limits already say.
- **Which harnesses can spawn a reader.** No harness was measured for subagent capability; ruling 1
  states the consequence for one that cannot.
- **The other Second readers.** Their routes and floors are their own records'; only the heading
  read's walk is withdrawn here.
