# The unread remainder is one line per report that counts each member once and names a nonzero population

**Measured at:** 5d32d8490b61bba071e0dba6013349aff84d97ad

[#1740](https://github.com/mshamblin5150-code/clinical-skills/issues/1740) found a coursework
grader printing the shared `unread remainder N` line twice with different values, so the last line
could read 0 on a run that exited 2. Grilled 2026-10-17 against `main` at
`5d32d8490b61bba071e0dba6013349aff84d97ad`, where the freshness gate read `FRESH`; the clinician
ruled every point below in that session.

This record sharpens [ADR 0230](0230-a-measured-partial-read-prints-an-admissible-unread-remainder-that-exits-not-scanned-and-is-declared-only-where-no-candidate-count-is-admissible.md)
ruling 6, which holds the grader family to "one shared remainder line" without saying how many
times a report may print it. It overturns nothing in that ruling.

## Measured before ruling

**Two counters see the same heading-read line.** `heading_read.survey` adds every bound record's
unread lines into the grader's own `heading_read_unread`, and `reader_remarks.apply_readers` sums
the same records' `unread` again into the line it appends. Driven through
`discussion_reply_scan.main` over `test_discussion_reply_scan.Run`:

| planted shape | first remainder line | appended remainder line | exit |
| --- | --- | --- | --- |
| a bare `## HEADING-READ` heading with no artifact | `unread remainder 1` | `unread remainder 0` | 2 |
| one unrecognized line inside the bound heading-read record | `unread remainder 1` | `unread remainder 1` | 2 |

The second row discriminates the ruling below: a plain sum of the printed lines would report 2
for one unread line. Had the two counters been disjoint, that row would have printed
`unread remainder 1` and `unread remainder 0`, the way the first row does.

**Claim records are counted by one counter only.** In `discussion_reply_scan`,
`discussion_post_scan`, `peer_critique_scan` and `deck_scan`, the grader's own figure sums
heading-read, reference, roster, posted-reading, member or slide-limit populations and not claim
records; `apply_readers` alone counts claims.

**A report can print three lines.** `assignment_docx_scan` prints `heading_read_unread` on its own
line and again through `heading_read.format_coverage`, then `apply_readers` appends a third.
`checks_ledger` prints the heading-read coverage line, its `CHECK` reader line, and the `CLAIM`
line `apply_readers` appends; those three count separate records.

**`research_ledger.py` has the same shape outside `reader_remarks`.** With an own-work record whose
local document had been moved (the `test_own_work_ledger` fixture), the command exited 2 and printed
`unread remainder 0` on standard output and `unread remainder 1` on standard error. Without the
defect it would have printed one line.

**Some unread populations are named nowhere but the total.** The unbound heading-read heading,
`deck_scan`'s slide-limit count, and `discussion_post_scan`'s posted-reading remainder have no row
naming them. Reader-record unread lines, reference entries, roster posts and diagram or chart
members already have one.

**The shared conformance kit cannot see a second line.** `grader_conformance`'s unread-remainder
case asserts that some output line equals `unread remainder N`, not that only one does.
`assignment_docx_scan`, `checks_ledger` and `research_ledger` are not kit members at all.

## Ruling 1 — one line, each member counted once

A report prints exactly one `unread remainder N` line, standard output and standard error together,
and N counts each unread member once however many counters see it. **Summing the printed lines was
declined** on the measurement above: it double-counts every unread line inside a bound heading-read
record. **Printing several labeled remainder lines with no total was declined** because the
clinician would still add the figures to learn what the exit status rests on, which is the
confusion #1740 was filed over.

## Ruling 2 — a nonzero total names each population behind it

When N is nonzero, each population contributing to it prints one line naming it and its count. A
population at zero prints nothing, so a clean report keeps the output it has today. An existing row
or `unread reader record: <kind>: <artifact>` line that already names the population and its count
satisfies this. Every such line contains the word `unread`, so ADR 0330 ruling 4's verbatim coverage
lines reach the go-ahead. **Printing every population's line on every run was declined**: it lengthens
every coursework go-ahead whether or not anything is unread.

## Ruling 3 — the scope is the six reader-remark graders and `research_ledger`, held by a tightened kit

The rule binds `discussion_reply_scan`, `discussion_post_scan`, `peer_critique_scan`, `deck_scan`,
`assignment_docx_scan`, `checks_ledger` and `research_ledger`. The conformance kit's unread-remainder
case asserts exactly one remainder line for every member that opts in. Members outside the kit that
this ruling binds carry the same assertion in their own test modules.

**`aar_scan`'s extract-and-rebuild output is left to its own ticket.** It prints the extract's
remainder and then a rebuilt grade's report, which may be two reports in one run rather than one
report printed twice; that question was not measured here. **Taking the whole family now was
declined** for that reason, and **taking only the six graders #1740 named was declined** because
`research_ledger` shows the same two disagreeing lines in the same go-ahead.

## Ruling 4 — recorded in a new ADR

The ruling is recorded here rather than as a dated correction inside ADR 0230 so the declined sum
stays where the next proposer will look. **A dated correction in ADR 0230 was declined** because that
record's subject is exit status and admissibility, and **no record at all was declined** because the
kit can enforce one line but cannot say why a sum is wrong.

## What this does not reach

- Whether every population contributing to N is the right population is ADR 0230's admissibility
  question and is untouched.
- The tightened kit asserts the count of remainder lines in a member's output. It does not assert
  that N counts each member once; that rests on each module's own tests of its overlapping
  counters.
- Graders outside ruling 3's list keep whatever they print today until a measurement brings them in.

## Build checklist

- `reader_remarks.apply_readers` stops appending its own remainder line. It returns its count of
  unread records not already in the caller's figure, and each caller folds that into its one line.
  Heading-read records are counted by the caller's heading-read survey alone.
- `heading_read.format_coverage` no longer prints the shared line when its output is composed into a
  grader's report; `assignment_docx_scan` and `checks_ledger` print one total.
- `research_ledger` prints one line carrying reader-record and local-document unread together, and
  its local-document population gains a naming line when nonzero.
- Add naming lines for the three populations named nowhere today.
- Tighten `grader_conformance`'s unread-remainder case to exactly one remainder line across standard
  output and standard error. If `aar_scan`'s kit input prints two lines, stop and route it to the
  `aar_scan` ticket rather than resolving it in this build.
- Add a one-line assertion to `test_assignment_docx_scan.py`, `test_checks_ledger.py` and
  `test_own_work_ledger.py` on each module's unread control.
- Keep #1740's two planted shapes as tests: the bare heading must print `unread remainder 1` once,
  and the unrecognized line inside a bound record must print `unread remainder 1` once with its
  `unread reader record` line.
