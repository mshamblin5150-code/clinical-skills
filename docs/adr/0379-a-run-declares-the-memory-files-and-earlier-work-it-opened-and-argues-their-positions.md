# A run declares the topic-matching memory files and same-subject earlier work it opened, and the draft argues their positions at least as strongly

**Measured at:** a22d9c58db035a2e5a2e4e17cd584c4189927079

[#1600](https://github.com/mshamblin5150-code/clinical-skills/issues/1600) was filed from the
after-action review of a `discussion-reply` run (NUR 5042 Module 10) on 2026-10-07. The clinician
ruled every point below on 2026-10-16, against `main` at the commit above, where the freshness gate
read `FRESH`. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**A reply missed a position the clinician had already taken twice.** It answered a classmate on two
nurses in conflict at shift handoff and said nothing about where report belongs. A week earlier the
clinician had written a graded paper on the same scenario arguing for bedside report, and the memory
whose index line reads "Shift report belongs at the bedside — handoff analyses should argue for it"
says the same. He supplied both at the go-ahead.

**The run recorded the memory index as read and opened no memory file.** The project-context
record treats the index as an owed place on a run that names a project. Reading it records that a
memory exists, but never puts the memory's rule in front of the drafter. No skill, `AGENTS.md`, or
`sourcing.md` tells a run to open an individual memory file; a search of `skills/` and `AGENTS.md`
found none.

**Two earlier rulings bound the choices.**
[ADR 0363](0363-a-render-reader-counts-blind-and-the-case-study-graders-rerun-as-handoffs-before-every-reader-round.md)
ruling 4 owes the memory index only on a run that names a project and declined to reopen that for
`none` runs, which most replies are.
[ADR 0360](0360-a-reused-quotation-must-fit-the-piece-and-a-run-declares-the-earlier-course-papers-it-read.md)
ruling 4 added `COURSE-HISTORY`, a declared header line the gate checks, which is a declared
retrieval that `tools/project_context.py` accepts on a `none` run (`_has_declared_retrieval`). Since
that build, a prior paper in the same course is read; a paper on the same subject in another course
is not.

**The clinician's coursework sits in three folders of the owning checkout's `output/`**: case
studies, course assignments, and discussions, about 39 files on 2026-10-16. A subject search across
all of it is cheap.

**The heading reader's context verdict compares the draft with statements about the clinician and
with Item descriptions.** It does not ask whether the draft takes a weaker clinical position than
one his opened items take, which is what the incident's draft did.

## Ruling 1 — one shared rule for all five coursework skills

The rule is written once in the **Draft order** section of
[sourcing.md](../../skills/_shared/reference/sourcing.md) and binds `course-assignment`,
`discussion-post`, `discussion-reply`, `peer-critique`, and `practicum-case-study`. The ticket's
diff to `discussion-reply` step 3 alone was declined because the gap is in the shared sourcing rule
every coursework run follows; a case study on a handoff scenario misses the same memory the same way.
Adding `clinical-note` and `batch-shift` was declined: they draft from shorthand by a different
route, and the memories that bear on them reach them through their own steps.

## Ruling 2 — a declared, opened `MEMORY-FILE` line

The confirmed project-context header gains a line, repeated once per opened memory file:

```text
MEMORY-FILE: <absolute path to one opened memory file>
MEMORY-FILE: none - <reason>
```

`tools/project_context.py` refuses it on `COURSE-HISTORY`'s terms: a missing line, `none` without a
reason, `none` beside a path, a duplicated path, or a declared path not opened as an item of a
`read` place. A declared path is a declared retrieval, so it is accepted on a `none` run through
`PROJECT-SEARCH` as `COURSE-HISTORY` is, and ADR 0363 ruling 4 stands unchanged. The lines join the
context digest and the go-ahead recheck; a memory file edited mid-run shows there as a moved place.
A written drafting instruction alone was declined because the incident was a skipped step that
nothing failed on. Making every memory file an owed place was declined because it contradicts ADR
0363 on `none` runs and forces unrelated files into every record.

## Ruling 3 — the drafting run matches by meaning, every memory's own description, and he confirms the list

The drafting run compares **every memory's own description** with the subject of the board or
assignment, by meaning and not by shared words, and declares each match. Where the index groups
memories under subject lines that point to subject indexes, the run opens whatever subject indexes
it needs to reach each memory's own description; matching on a subject line alone is not the
comparison. The declared `MEMORY-FILE` lines appear in the header the clinician already confirms
before prose, so he can add a file the run missed.

A fresh matcher agent was declined: the incident's failure was a comparison that never happened,
not a bad one, and the confirmed list exposes a miss at no new cost. If a miss survives the list in
front of him, that is the evidence for revisiting it. A word match was declined because it misses
synonyms ("handoff" and "shift report" share no word with "nurses in conflict at report") and reads
as coverage it does not provide. The gate cannot establish that the declared set is complete; that
limit belongs in `project_context.DECLARED_LIMITS`.

The shape-neutral wording is deliberate. [#1707](https://github.com/mshamblin5150-code/clinical-skills/issues/1707)
is weighing a two-level memory index; under it, wording that read "every index line" would let a
run match subject lines and never see the memory beneath. Writing for today's flat index and leaving
#1707's ruling to restate it was declined as a rule that weakens silently if nobody follows through.
Waiting for #1707 was declined as a block on a decision that does not bear on the incident.

## Ruling 4 — a declared, opened `PRIOR-WORK` line for same-subject work outside the course

The run searches all of the clinician's coursework outside the current course for work on the same
subject, matching by subject as in ruling 3, opens each match, and declares it on its own line:

```text
PRIOR-WORK: <absolute path to one earlier paper on the same subject>
PRIOR-WORK: none - <reason>
```

The gate checks it on `MEMORY-FILE`'s terms, and the clinician confirms it in the header. Course
history is unchanged: it remains every earlier paper in the same course, read whole, for ADR 0360's
reuse judgment. Widening it to every course was declined because that would read every file whole
on every run and build a reuse list across unrelated courses, which is a heavier duty aimed at a
different problem. Adding nothing was declined because a paper in another course on the same
scenario is missed unless a memory happens to name it.

`MEMORY-FILE` and `PRIOR-WORK` are two lines, one kind each, like every other declaration.

## Ruling 5 — the draft argues a declared item's position at least as strongly

The heading reader's existing context verdict also covers positions taken by declared `MEMORY-FILE`
and `PRIOR-WORK` items. Where such an item takes a position on a subject the draft argues, the draft
takes it at least as strongly. Leaving the position out where it bears on the draft's point is
`CONTEXT-VERDICT: narrows`; arguing the opposite is `contradicts`. Both are findings and block the
go-ahead, as today. The draft need not restate the earlier paper, only not take a weaker or opposite
stance. "Bears on the draft's point" is the test the Item-description omission rule already uses.

A drafting instruction alone was declined on ruling 2's ground. A position list at the go-ahead was
declined because nothing blocks and it adds a list to the go-ahead where his attention is most
stretched. The accepted cost is that whether a position bears on the point is the reader's judgment.

## Consequences recorded as derived rather than ruled

**Both new checks enter `reference/completion-check-starts.tsv`** under
[ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md),
so a record confirmed before the build reports them `not graded` rather than failing.

**The context verdict needs no new shape.** `heading_read.py` already requires `agrees` on every
run that is not a legacy `none` run, so ruling 5 widens what the reader compares and not the
grammar of the verdict.

**The [#1485](https://github.com/mshamblin5150-code/clinical-skills/issues/1485) drafting-time
agreement rule now reaches the opened memory files and earlier papers.** That rule binds only what
was opened; this record is what opens them.

## What this does not reach

A run that declares `MEMORY-FILE: none` with a plausible reason, when a memory did match, passes the
gate; only the clinician's look at the confirmed list catches it. Memory files the run never
compared are not counted anywhere. Earlier work outside the owning checkout's `output/` is outside
the search.
