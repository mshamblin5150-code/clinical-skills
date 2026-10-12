# A refuter return is applied by a helper and the ledger matches a kept return

**Measured at:** 59c440e7a6c2f5c81b33dcd14ce4f6e392693226

[#1564](https://github.com/mshamblin5150-code/clinical-skills/issues/1564) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M11) on 2026-10-04. Refutation results
came back from parallel refuters in many groups, and the orchestrator merged them into the claim
ledger with ad-hoc scripts. One script failed on shell quoting, and a hand count of the results was
wrong once. The ledger grader caught the record shapes, but nothing committed applied a returned
block to its record or reported what each group covered. Grilled 2026-10-12 against `main`, where
the freshness gate read `FRESH`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Five skills tell the orchestrator to copy a refutation into the ledger by hand.**
`course-assignment`, `discussion-post`, `discussion-reply`, `peer-critique`, and
`practicum-case-study` each say to run `research_ledger.py <ledger> --heading-digests` before
dispatch, name the printed fingerprint in the brief, and "write it as `TESTED-HEADING` with the
returned verdict and route." No command performs that write.

**The returned fields are wider than the ticket named.** The ticket listed `REFUTATION`,
`TESTED-HEADING`, and `SECOND-ROUTE`. The record shape also requires `INSTRUMENTS` with an
`unreadable` verdict, and ADR 0330 ruling 1 adds any number of `REMARK:` lines. A helper copying
only the first three would drop the failed-read instruments and the remarks, which is #1501's
failure.

**A duplicated field is read silently.** `research_ledger.read_records` keeps the last value of a
repeated field, so appending a new refutation below an old one leaves the old verdict in the file
where nothing reads it.

**The ledger grader writes nothing.** `research_ledger.py` is a `run_grader` member; its one other
mode, `--heading-digests`, prints fingerprints and changes no file.

**The input route is where the run broke.** A heredoc changes backslashes and non-ASCII text, the
heredoc guard refuses Bash heredoc writes into `scratch/`, and a pasted return leaves nothing to
check afterwards.

## Ruling 1 — the helper is its own module and the grader stays read-only

The helper is a new command, `tools/refutation_apply.py`. It imports `research_ledger`'s record
reader and `heading_digest` rather than holding copies, so the writer and the grader cannot disagree
about what a record or a fingerprint is. It copies `REFUTATION`, `TESTED-HEADING`, `SECOND-ROUTE`,
`INSTRUMENTS`, and every `REMARK:` line from a block to the record whose current heading it names.

A mode inside `research_ledger.py` was declined: the command that checks the ledger would also be
able to change it, and the writer's outcomes do not fit the grader's exit statuses. That is the line
ADR 0001 keeps between the pass that produces something and the pass that checks it.

## Ruling 2 — the stored fingerprint decides what an existing refutation means

When the matching record already carries refutation fields:

- an existing `TESTED-HEADING` that no longer matches the record's current heading has expired, and
  the new block replaces `REFUTATION`, `TESTED-HEADING`, `SECOND-ROUTE`, and `INSTRUMENTS`;
- an existing refutation that still matches and equals the incoming block is counted as already
  applied, and nothing is written, so re-running a group is harmless;
- an existing refutation that still matches and differs is refused, and the conflict is reported.

Existing `REMARK:` lines are never removed; new ones are added. A heading that names more than one
record is refused as ambiguous.

Refusing every record that already carries a refutation was declined because each legitimate
re-refutation after a heading change would need the hand edit this ticket removes. Always replacing
was declined because a second refuter's `stands` could silently overwrite a live `refuted`.

## Ruling 3 — a block with an unrecognized line is refused whole

The helper recognizes the `## CLAIM:` line, the five fields above, `REMARK:` lines, and indented
continuations of a wrapped field. A block containing any other line is refused whole, nothing from
it is written, and its lines count toward the run's unread remainder, on ADR 0330 ruling 5's terms.
A block with only recognized lines is copied exactly as returned; whether it carries every field
its verdict requires stays with `research_ledger.py`, which runs after the helper.

Writing the recognized half and counting the rest as unread was declined: the record would look
complete while the stray line, which may have been a remark in the wrong place, was gone from the
ledger. Checking completeness in the helper was declined because it would hold a second copy of the
grader's field rules, and an edit to either copy fails nothing in the other (#220).

## Ruling 4 — a return arrives as a file and is kept beside the ledger

The orchestrator saves each refuter's return verbatim with the Write tool and passes one or more
files to the helper. One file is one group, and counts are reported per file. Before writing the
ledger, the helper copies each input into `refutations/` under the ledger's run directory. A kept
file with the same name and different bytes is refused; an identical one is accepted as already
kept. A corrected return is saved under a new name and never over a refused one.

Standard input was declined because it is the quoting path that broke and leaves no record of what
the refuter said. Reading files in place without keeping them was declined because the scratchpad
is per session, so a refused block or a later doubt about the ledger would have nothing to check
against.

## Ruling 5 — every passing block is written and the exit status says what was left

The helper writes every block that is applied, replaced, or already applied, and replaces the ledger
in one step through a temporary file, so the ledger is never half-written. Exit 0 means every block
was applied, replaced, or already applied. Exit 1 means a block was refused for a conflict or a
stale fingerprint, or matched no record. Exit 2 means an input could not be read, the ledger held no
record, a file held no block, or there were unrecognized lines. The run prints the shared
`unread remainder N` line through `run_grader.format_unread_remainder`, and 1 still wins when both
hold, on ADR 0230's terms.

Writing nothing when any block is refused was declined: refused blocks need a new refuter round or
a corrected return either way, and ruling 2 makes re-running safe. A ledger missing some
refutations between runs is already refused by the grader.

## Ruling 6 — the default report names a block by number, never by its text

By default the helper prints, per file, the blocks read, applied, replaced, already applied,
refused, and unmatched, and for each block not applied a position and a fixed reason built only
from integers and the module's own words, such as
`file 3 of 10, block 2: refused, fingerprint no longer matches the heading`. `--show` adds the
claim heading and is private working material on `research_ledger.py`'s terms. A test drives a
marker string through every block outcome and asserts it never reaches the default output.

Counts alone were declined because the agent could not act on a refusal without `--show`. Printing
headings by default was declined because a ledger lives under `scratch/` and a case-study heading
can carry case details.

## Ruling 7 — a changing write leaves a ledger snapshot

Before any write that changes the ledger, the helper saves the current ledger beside it as a
**Ledger snapshot** with a sequence number, never overwriting an earlier one. A run that changes
nothing saves nothing. Nothing grades a snapshot; `claim_ledger_census.py` counts it as it counts
any snapshot beside a ledger.

Taking no copy was declined because ruling 2's replacement removes the old verdict's text, and a
refutation entered before the helper existed has no kept return. Copying only on replacement was
declined because a defect in the ordinary path would then leave nothing to recover from.

## Ruling 8 — the five skills require the helper

`course-assignment`, `discussion-post`, `discussion-reply`, `peer-critique`, and
`practicum-case-study` replace the hand instruction with: save each return with the Write tool, run
the helper, and resolve what it refuses. Copying a refutation into the ledger by hand is no longer a
permitted route. AGENTS.md lists the helper as a Required command under each of the five, with the
fallback `research_ledger.py` already has: the written rules by eye only when the command cannot
run after installation has been tried.

Switching only `course-assignment` was declined because the other four carry the same step and the
same failure. An optional command beside the hand instruction was declined because an agent under
time pressure takes the route it knows.

## Ruling 9 — the ledger grader checks each refutation against a kept return

`research_ledger.py` gains a row: every record carrying refutation fields must match a block, kept
under the ledger's `refutations/` directory, with the same heading and identical `REFUTATION`,
`TESTED-HEADING`, `SECOND-ROUTE`, and `INSTRUMENTS` values. A record that matches no kept block is a
finding. The row takes a start date in `reference/completion-check-starts.tsv`, so a run whose
ledger predates it is not graded on it.

Its limit is declared beside it in `research_ledger.DECLARED_LIMITS`: a match shows the ledger
agrees with a saved return, never that a separate refuter wrote that return. A return written by the
orchestrator and run through the helper passes, as refuter independence already does under
`refutation-independence-unverified`. What the row does catch is the route the helper's own
refusals invite: a conflicting verdict forced into the ledger by hand, and any merge done without
the helper.

Declaring the gap without a row was declined because a required command whose bypass looks like
compliance is #214's shape: a written instruction cannot fail.

## Ruling 10 — the term is Refuter return

The glossary term is **Refuter return**: a refuter's returned block saved word for word and kept
beside the ledger. "Refuter output" and "result file" were declined because neither says the bytes
are kept unchanged, and "verdict block" because the block carries a route, instruments, and remarks
as well as the verdict.

## What the build changes

- `tools/refutation_apply.py`: rulings 1 through 7, calling `use_utf8()` and
  `require_python_floor()` from its command path and exposing a `DECLARED_LIMITS` object.
- `tools/test_refutation_apply.py`: synthetic ledgers and returns driving every block outcome,
  each exit status, the kept-return refusal, the snapshot, the one-step write, and the bounded
  default output.
- `tools/research_ledger.py` and `tools/test_research_ledger.py`: ruling 9's row, its declared
  limit, and its start date in `reference/completion-check-starts.tsv`.
- The five skills and `skills/_shared/reference/sourcing.md`: ruling 8's step, stated once in the
  shared sheet and pointed at from each skill.
- `AGENTS.md`: the Required command under each of the five skills.
- `CLAUDE.md`: a **Refutation apply** section pointing at the module's declared limits, and the
  console-codec correction naming the new direct command.

## What this does not reach

- **Whether a refuter was independent or took the route it named.** ADR 0042's declared limit
  stands.
- **Whether a saved return is what the refuter actually said.** The orchestrator writes the file;
  ruling 9 shows only that the ledger agrees with it.
- **Refutations entered before the build.** Ruling 9's start date leaves them ungraded on that row.
- **The other readers' records.** Heading-read, check, and render records are written the same way
  by hand; this ruling covers the claim ledger only.
