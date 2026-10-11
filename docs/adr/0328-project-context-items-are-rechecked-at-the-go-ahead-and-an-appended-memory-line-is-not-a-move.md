# Project context items are rechecked at the go-ahead and an appended memory line is not a move

**Measured at:** dd704cfe14f6408abdabfb96833efaf43b31d70a

[#1496](https://github.com/mshamblin5150-code/clinical-skills/issues/1496) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 10) on 2026-10-01. That review
landed a memory write, the write added a line to the memory index, and the terminal completion
grade then reported `the confirmed project context: not scanned - file item moved` with every other
row clean. The same row stopped a `discussion-reply` run (NUR 5144 Module 3) on 2026-10-02 and a
`course-assignment` run (NUR 5042 Module 11) on 2026-10-04. Grilled 2026-10-11 against `main`,
where the freshness gate read `FRESH`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

This record says *moved* for a retrieved item whose bytes changed after retrieval. `CONTEXT.md`
already defines *Drift* as a clinical-note defect, so the word is not used here for this sense.

## Measured before ruling

**The moved-item check runs only after posting and after the after-action review.**
[ADR 0272](0272-project-context-is-retrieved-into-a-confirmed-record-before-drafting.md) ruling 9
re-hashes every opened file item at completion. `project_context.completion_gate` grades nothing
without `--submission`, and `approval_record.approve` refuses a pre-post grader that receives
`--submission`. So the pre-post grade taken at each go-ahead reports the row as not graded. In all
five bound coursework skills the first `--submission` grade is the terminal one, which each skill
runs after `/AAR` exits clean because the same invocation must report `the after-action review:
clean`. The check therefore never runs at a moment where its result could change the work.

**Any after-action review that lands a memory write moves an owed item before that grade.** The
memory index is owed on every run whose declaration is not `none`. It is a file place, so the only
item a run can open under it is the index itself, hashed whole. A `memory-write` disposition adds a
pointer line to that file, so the terminal grade cannot exit 0 on any run whose review landed one.

**The memory index moves for reasons unrelated to the draft.** Every session on the account writes
to it. On 2026-10-11, 42 files under the account's memory directory carried a modification time on
or after 2026-09-27, by `find -newermt`. Each new memory file adds an index line, so that figure is
a proxy for how often the index moves; it is not a count of index edits, since a rewrite of an
existing memory need not touch the index. A coursework run usually spans hours between first prose
and the go-ahead, so a whole-file hash of the index taken at the go-ahead would report most runs
moved.

**The recovery no longer creates a late gate.** The 2026-10-03 sweep comment predicted that rerunning
`tools/project_context.py --write` after submission would replace a clean draft observation with a
late gate. [ADR 0290](0290-the-pre-draft-gates-observe-that-the-draft-does-not-yet-exist-and-a-late-gate-is-a-finding-the-clinician-clears.md)
ruling 9 keeps the first observation for a submission key, so that interaction is settled. The
recovery still costs a fresh independent heading read against the new context digest and judges a
posted artifact against context written after it.

**The approval record verifies what draft text was shown, not every notice.**
`approval_record.verify_shown_text` matches the source's Markdown blocks in assistant text between
the last source change and the clinician's reply. Nothing reads whether a particular notice was
shown.

## Ruling 1 — the moved-item check runs at the go-ahead, and the terminal grade carries it forward

Each go-ahead on a bound coursework submission re-hashes that run's opened file items and records the
result for that submission key. A moved item makes the pre-post grade incomplete, the way an exit 2
pre-post grade already records `incomplete`, and the clinician sees which places moved before he
approves.

Once a posting is recorded for the key, the terminal `--submission` grade does not re-hash file
items. It reports the result recorded at the go-ahead instead.

Stopping the check after posting with nothing in its place was refused, because it removes ADR 0272
ruling 9 in practice. Leaving the terminal check in place and excluding only the memory index was
refused, because a planning file edited after posting would still block completion and the check
would still fire too late to change anything. Recording fresh hashes when the after-action review
finishes was refused for the same lateness, because another session can still move the index in the
gap, and because it would make that review own project-context bookkeeping.

## Ruling 2 — the memory index has moved only when a line present at retrieval was edited or removed

At retrieval the gate records a fingerprint for each line of the memory index. At the go-ahead a
retrieved line that is missing or changed means the index moved. A line added since retrieval is
not a move. The go-ahead shows the clinician every added line so he can judge whether one bears on
the draft. Every other opened file item keeps its whole-file hash.

A whole-file comparison was refused because unrelated pointers appended by other sessions would make
the notice fire on most runs, which teaches reading past it. Leaving the memory index out of the
go-ahead check was refused because an edited or removed pointer the draft relied on is the one
revision that matters.

## Ruling 3 — the clinician's approval clears a move shown at the go-ahead

The terminal grade reports what the go-ahead check found, including the moved places and that the
clinician approved over them. A move recorded at the go-ahead does not by itself keep the terminal
grade from exiting 0. This narrows ADR 0272 ruling 9's *"an honest run can end in a 2"* to the
runs where no go-ahead result exists for a posted submission; see ruling 4.

That the clearing rests on the clinician having seen the notice is a declared limit, because the
approval record verifies the draft text shown and not the notice. Keeping a moved item as a
permanent exit 2 was refused, because every run with a real move would end short of `complete`
whatever the clinician decided, and the only way out is the costly recovery this ticket recorded.
Saying nothing about the move at completion was refused, because the run's permanent record would
lose that it was approved over changed material. This follows ADR 0290 ruling 4's shape, where a
fact the clinician saw is cleared by his word rather than held open.

## Ruling 4 — a posting approved before the go-ahead check existed is named and passes

When a posting is recorded for the key and no go-ahead result exists, the terminal grade reports the
row as not checked at the go-ahead because the approval predates that check, prints a count, and
does not block exit 0 for that alone. Every approval recorded after the build carries the result, so
the exemption cannot reach a new run. This is the extractor-coverage rule's partial read with its
bound named beside the result.

Leaving those runs at exit 2 for the clinician to close as stopped was refused, because finished,
posted work would be recorded as incomplete over a check that did not exist when he approved it. A
per-run waiver line was refused as a confirmation asked for runs whose substance is already
approved.

## Supersedes

- [ADR 0272](0272-project-context-is-retrieved-into-a-confirmed-record-before-drafting.md)
  ruling 9, its placement "At completion the file items are hashed again." Ruling 9's coverage
  state for a moved item, its finding-wins order and its exclusion of thought items stand.

## Build checklist

- `tools/project_context.py`: a public go-ahead function recording a per-key machine-written result
  in the project context record, beside `ORDER-OBSERVATION`; per-line fingerprints for the memory
  index at retrieval; the terminal grade reading the go-ahead result once a posting is recorded,
  through `approval_record`'s public reader; and `DECLARED_LIMITS` rows for the approval-sight limit,
  added memory lines shown and not graded, and the pre-check approvals.
- `tools/approval_record.py`: the approval of a bound coursework submission calls that function and
  folds a moved item into the pre-post status as `incomplete`.
- The five bound skills' go-ahead steps: show the moved places and every added memory-index line.
- Tests through the public commands: an appended index line, an edited index line, a moved planning
  file, a terminal grade after a recorded posting, and a posted run with no go-ahead result.

## What this record does not reach

- **Whether an added memory line bears on the draft.** The clinician reads the added lines; nothing
  grades them.
- **Service items.** They are still not hashed again, on ADR 0272 ruling 9.
- **Whether the clinician read the notice.** The approval record verifies the draft text shown.
