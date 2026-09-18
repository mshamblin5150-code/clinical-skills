# The claim ledger census reads claims.md and counts every other claims file without grading it

Out of the grilling of [#1187](https://github.com/mshamblin5150-code/clinical-skills/issues/1187).
Follows [ADR 0198](0198-a-number-is-certified-only-by-a-record-whose-refutation-pass-ran.md)
and the in-place correction to
[ADR 0153](0153-a-sourceless-record-claims-no-source-and-a-certifier-reads-the-status.md).

A figure counted by hand over `claims*.md` produced three premises in ADR 0153, each true of a
**Ledger snapshot** and false of the run's claim ledger. CLAUDE.md's extractor-coverage rule already
required a figure to name its population when those premises were written, so the rule alone did
not prevent them. The remedy is a command whose default population is the one every certifier
loads.

## Measured before ruling

**Which file is the ledger is not a per-family question.** The ticket asked it per artifact family.
Since #417 every family that keeps a claim ledger uses one run layout: `practicum-case-study` binds
its claims ledger to `<run-directory>/claims.md`, and `course-assignment`, `discussion-post`,
`discussion-reply` and `peer-critique` each create `claims.md`. Every number certifier and
`checks_ledger.py` resolve that exact name. The dated ledgers ADR 0040 and ADR 0052 cite predate
that layout; they were the ledgers of their day and are not the current rule.

**Across every registered checkout, the unread files fall into two shapes that mean different
things.** A snapshot beside a `claims.md` leaves the reading of that run complete. A run directory
holding `claims*.md` files and no `claims.md` has a ledger no command reads. Both shapes are live.
The counts are the command's to state and are deliberately not restated here, because they are
measured over `scratch/`, which nothing committed re-derives.

## Ruling 1 — a counts-only census reads `runs/*/claims.md`

`tools/claim_ledger_census.py` walks every registered checkout's scratch root, as
`reference_class_census.py` does, and reads only `runs/*/claims.md`. It imports `research_ledger`'s
record parser and its substantive-refutation predicate rather than parsing a second time, so its
counts cannot disagree with the grader's.

It prints checkouts enumerated, scratch roots read and unreadable, ledgers read and how many carry a
`DATE:` header, claim records by `STATUS`, and sourced records with no substantive refutation. It has
no `--show` and prints no name or path, so its output is safe to paste into a ticket.

Rejected: relying on the extractor-coverage rule alone. It was in force when the three premises were
written.

## Ruling 2 — the two unread shapes are counted apart

Snapshots beside a ledger print as one count and are not graded. Runs with `claims*.md` and no
`claims.md` print as a second count. Neither is folded into a single total over every `claims*.md`,
which is the defect this record answers.

## Ruling 3 — neither count changes the exit status

The census declines ADR 0230's unread-remainder seam although it has a countable candidate
population. A snapshot is preserved run material and ADR 0153 ruling 6 forbids editing or renaming it
so a figure comes out right, so an exit 2 keyed on either count would be permanent and would teach its
readers to ignore exit 2. The run with no `claims.md` becomes a `DECLARED_LIMITS` row instead: a
nonzero count on that line needs a reader, and the line keeps a new run with a misnamed ledger
visible.

Exit 0 is a complete census. Exit 2 means a registered scratch root could not be read. There is no
exit 1, because the census grades nothing; grading a run stays with `research_ledger.py`.

Rejected: recognizing a pre-#417 run by file modification time, which a copy resets. Rejected: reading
the newest `claims-<date>.md` where `claims.md` is absent, which builds a second name rule into the
instrument this record exists to replace.

## Ruling 4 — no snapshot naming convention

The census tells a snapshot from a ledger by the presence of `claims.md` beside it, not by its name.
A declared suffix would help only a hand-written glob that already knew to exclude snapshots, and the
defect was a hand-written glob.

## Ruling 5 — a published claim-record figure is read off the command

CLAUDE.md gains a maintainer-tooling section for the census. `docs/agents/issue-tracker.md`'s sweep
guidance gains the rule that a claim-record figure published to the tracker or to an ADR is read off
`python tools/claim_ledger_census.py`, never counted by hand over `claims*.md`. ADR 0153 and ADR 0198
already carry their corrections and are not edited.

## What none of this reaches

A figure about one run is still `research_ledger.py`'s to grade. A claim ledger kept outside
`runs/*/`, or under any name other than `claims.md` in a run that also has one, is outside the census
and is counted only when its name matches `claims*.md`. No snapshot filename enters a committed file.
