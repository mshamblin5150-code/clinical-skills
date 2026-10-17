# The memory index keeps everywhere rules flat and files situation memories under generated subject lists

**Measured at:** 4edb3153b9ca6cb8114da429f39d97bc2b0f3a71

[#1707](https://github.com/mshamblin5150-code/clinical-skills/issues/1707) was routed here by
[ADR 0333](0333-a-bold-references-label-is-read-off-the-word-path-and-an-oversized-memory-index-fails-the-review.md)
ruling 6. Claude Code loads one memory file into every session, the auto-memory index `MEMORY.md`,
and cuts it at 200 lines or 25,000 characters. ADR 0333 made the after-action review fail an
oversized index; it did not raise the ceiling. Grilled 2026-10-17 against `main` at
`66aaf05b1bcf7ee185f7f7010af35d1e66ac5eff`, where the freshness gate read `FRESH`; the clinician
ruled every point below in that session.

## Measured before ruling

**The index is near its character limit.** On 2026-10-17 `MEMORY.md` held 159 lines and 20,210
characters as a string length, every line a link to one of 159 memory files with no dangling link
and no unlinked file. Lines average 126 characters, so the character limit binds first, at about
195 lines. ADR 0333 recorded 146 lines six days earlier, about two new lines a day.

**A flat matching line is already skipped.** ADR 0379 records a reply that never opened the
shift-report memory whose index line matched its subject, and ADR 0363 records a case study that
never opened the Write-tool memory whose line matched its task. Both happened on today's flat
index with no second level involved.

**A memory file's `type` does not separate the two kinds of memory.** Of the 159 files, 92 carry
`feedback`, 19 `user`, 23 `project`, 19 `reference`, and six carry no frontmatter at all.
`feedback` holds both "never git stash" and the Canvas box pause; `reference` holds the Medatrax
Time Log clicks.

**Claude Code's own memory instruction tells every session to add one line to `MEMORY.md` per new
memory.** Any second level holds only if the writing session reads a rule that overrides that
instruction at the moment it writes.

**The checks that read the index read one file.** `project_context` fingerprints each nonblank line
of `MEMORY.md` and compares them as a multiset ([ADR 0328](0328-project-context-items-are-rechecked-at-the-go-ahead-and-an-appended-memory-line-is-not-a-move.md)
ruling 2). `aar_scan --measure-memory` measures `MEMORY.md` alone. `aar_scan`'s landing snapshot
already hashes every file beneath the index's directory, subdirectories included.

## Ruling 1 — a hybrid index

Rules that apply in every session stay as flat lines in `MEMORY.md`. Situation memories move behind
one line per subject, each pointing to a subject list with no length limit. A full two-level index
was declined because it hides the everywhere rules one more read away, which is the failure ADR 0379
and ADR 0363 already observed with no second level. Managing a budget on the flat list alone was
declined because the ceiling never rises and the work repeats every few weeks.

## Ruling 2 — a memory goes behind a subject only when it matters solely during that subject's work

A memory moves behind a subject when it matters only while a named portal, tool, course, project,
or kind of task is the work. Everything else stays flat, including a trap a session can walk into
without knowing it is in that subject. Sorting by the memory's `type` was declined on the
measurement above. A fixed cap on the flat section was declined as an invented figure, on ADR 0333
ruling 5's terms.

## Ruling 3 — the filing rule is tracked and installed into the top of `MEMORY.md`

The rule lives in [docs/agents/memory.md](../agents/memory.md). A command installs it into a marked
block at the top of `MEMORY.md` and refreshes only that block, on the grilling guard's pattern. A
hand-written header was declined because nothing protects its wording; a section in `CLAUDE.md` was
declined because a session about to write follows the built-in instruction it already holds.

## Ruling 4 — the subject list is fixed in the tracked rule file

The writer picks a subject from that list. A memory that fits none stays flat until an ordinary
reviewed change adds a subject; no ruling from the clinician is needed for that change. Letting
writers create subjects was declined because a second name for one subject hides memories behind a
line nobody opens. Letting a writer edit the tracked list mid-task was declined because a review or
side-project session usually cannot make a reviewed change.

## Ruling 5 — subject lists are generated from each memory's own header

Each memory file states its subjects in its own header, as `subjects: canvas, coursework` or
`subjects: none`. One command rebuilds every subject list and the flat part of `MEMORY.md` from those
headers and the files' own descriptions. A memory that fits two subjects lists both. A memory with
no `subjects` header keeps its existing flat line; where a session cannot run the command it appends
a flat line as the built-in instruction says, and the next rebuild files it. The after-action review
runs the rebuild at its memory-write step. Hand-written subject lists were declined because their
copies of each summary drift and nothing can list what is filed where.

## Ruling 6 — an observed miss promotes the memory one step

When an after-action review finds a correction that an existing memory already covered, it promotes
that memory one step: from a subject to a flat line, or from a flat line to a tracked rule in
`AGENTS.md`, a skill, or a reference sheet, as ADR 0363 ruling 5 did. A second reader judging every
new memory's filing was declined because it guesses without evidence. This also answers the
question #1707's 2026-10-12 comment raised: a memory becomes a tracked rule when a flat line has
already failed to get it applied.

## Ruling 7 — one cleanup pass, confirmed item by item, and nothing is deleted

The migration drafts a reasoned list of superseded or duplicate memories. The clinician confirms it
item by item. Confirmed memories move to a `retired/` folder beside the memory files and drop out of
every index. A standing check on memories that cite a closed ticket was declined because it fires on
deliberate regression warnings, such as the memory recording that #1084's fix makes a refusal a
regression.

## Ruling 8 — the project-context check reads the whole index as one

`project_context` fingerprints the nonblank lines of `MEMORY.md` and of every subject list together,
under ADR 0328 ruling 2's rule: an added line is shown, an edited or removed line is a move. A
subject line in `MEMORY.md` carries no member count, so filing a new memory edits no existing line.
Fingerprinting `MEMORY.md` alone was declined because a memory rewritten or retired under a subject
mid-run would never reach the go-ahead; fingerprinting only the subject lists a run opened was
declined because a run that skipped a subject would also skip its protection.

## Ruling 9 — the review grades the load limits and an unplaced memory

The after-action review still grades `MEMORY.md` against the 200-line and 25,000-character limits.
It reports each subject list's line count without grading it. It fails when a memory cannot be
placed in any index: its header names a subject not on the fixed list, or it needs a generated line
and has no readable description. Grading subject lists against the file reader's 2,000-line default
was declined as a check on a limit nothing approaches.

## Ruling 10 — seven starting subjects

The starting subjects are clinical notes, coding, and Medatrax; coursework writing and voice; Canvas
and LMS posting; research sources; tracker, pull requests, and the publish hook; ADRs and grilling;
and Axion, DAVID, and side projects. Each memory's assignment is drafted by the build and confirmed
by the clinician alongside the cleanup list. A finer split of about twelve was declined because one
subject list is one read either way; a coarser split of four was declined because "repo work" would
be opened in nearly every build session.

## Ruling 11 — tools first, then one migration sitting

The tools merge first. A memory with no `subjects` header stays flat, so the rebuild run before any
header exists leaves the index unchanged, and installing the rule block is its own explicit step.
The cleanup, the subject assignments, the headers, the rebuild, and the block install then happen in
one confirmation sitting, held when no coursework run is open, so the one-time rewrite of
`MEMORY.md` does not appear at an open run's go-ahead as a burst of moved places. Migrating by hand
first was declined because the checks that protect the migration would not yet exist.

## What this does not reach

- Whether a session opens a subject list it should have opened. Ruling 6 acts after a miss is
  observed; nothing prevents the first one.
- Whether a memory's own description describes it well. The lists repeat each file's description;
  a poor description is a poor line in every list it reaches.
- A memory written outside a scoped skill's review and never rebuilt. It stays a flat line, fully
  seen, until the next rebuild.
- Claude Code changing its loading limits or its memory instruction without a release change, which
  stays outside ADR 0333 ruling 4's release line as before.

## Build checklist

- `docs/agents/memory.md`: the filing rule, the fixed subject table, and the installed block's text.
- `tools/memory_index.py`: survey and rebuild. Reports counts by default; `--write` rebuilds the
  subject lists and the flat part of `MEMORY.md`; `--install-rule` inserts the marked block, and
  `--write` refreshes it once present. Exit 0 every memory placed, 1 an unplaced memory, 2 not read.
- `tools/project_context.py`: the memory index's line population includes every subject list.
- `tools/aar_scan.py`: the measurement records each subject list's line count and the unplaced
  count; the grade reports the first and fails on the second.
- `skills/aar/SKILL.md`: run the rebuild after memory writes and before measuring; apply ruling 6's
  promotion as a `memory-write`, `skill-file`, or `check` landing.
- The migration sitting under ruling 11, after the merge.
