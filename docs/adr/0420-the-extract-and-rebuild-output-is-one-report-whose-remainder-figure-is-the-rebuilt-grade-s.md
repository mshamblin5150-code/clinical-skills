# The extract-and-rebuild output is one report whose remainder figure is the rebuilt grade's

**Measured at:** acaf672586f0bd62ac01550df43ffab8b6cdeb09

[#1855](https://github.com/mshamblin5150-code/clinical-skills/issues/1855) found that
`aar_scan.py --extract --rebuild-round <n>` can print two `unread remainder N` lines with nothing
saying which population each counts. [ADR 0393](0393-the-unread-remainder-is-one-line-per-report-that-counts-each-member-once-and-names-a-nonzero-population.md)
ruling 3 left this command to that ticket because nobody had measured whether the output is one
report printed with two figures or two reports in one run. Grilled 2026-10-19 against `main` at
`7821ce1f`, where the freshness gate read `FRESH`. Both measurements below were taken there and
taken again at the commit above, which adds only the first draft of this record to `main` at
`5270598f`; nothing between those two bases touches `aar_scan` or `run_grader`. The clinician
ruled every point below in that session.

This record settles the case ADR 0393 deferred. It overturns nothing in that record.

## Measured before ruling

**The two lines count the same members.** The `--extract` branch of `aar_scan.grade` prints the
shared line over the extract header's `UNREAD-REMAINDER`. When the rebuilt round already has a
review record, the branch then appends `format_report(survey(...))`, which prints the shared line
again over `Scan.unread_remainder`. Driven through `aar_scan.main` on the synthetic run behind
`test_rebuild_round_repairs_only_notification_identifiers`, with the refused round's header carrying
`UNREAD-REMAINDER: 2` and a matching `UNDECLARED-SYSTEM-SUBTYPES: 2`:

| output part | remainder line | exit |
| --- | --- | --- |
| the extract summary | `unread remainder 2` | 2 |
| the rebuilt grade's report | `unread remainder 2` | |

Had the two lines counted disjoint populations, a single planted population would have appeared on
one line and `unread remainder 0` on the other. Both carried it.

**The code explains why.** `rebuild_extract` keeps the refused extract's header verbatim and
re-reads no transcript, so the summary's figure is the refused round's recorded value. `survey`
reads that same header for the rebuilt round and sums every round's remainder into its total. The
summary's figure is therefore always a member of the rebuilt grade's figure: equal with one round,
contained in a larger total with several.

**A round recorded before the remainder count crashes the summary.** Format 2 extracts predate the
`UNREAD-REMAINDER` field, whose completion-check start is 2026-10-03. With that field removed from a
refused round's header, the same invocation raised `KeyError: 'UNREAD-REMAINDER'` out of
`aar_scan.grade` and the process exited 1, the status the grader family reserves for an established
finding. `format_report` already prints `unread remainder: not measured (extract predates the
count)` for such a round and does not fail coverage on it.

## Ruling 1 — one report, and its figure is the rebuilt grade's

When `--rebuild-round` produces a rebuilt grade, the extract summary prints no remainder line, and
the rebuilt grade's single line is the run's figure. The grade's existing naming lines, such as
`undeclared system subtypes N`, satisfy ADR 0393 ruling 2 for the populations behind a nonzero
figure. Without a rebuilt grade, the extract summary's line stays the run's one line, as it is
today. The exit status keeps reading the same populations.

**Two labeled lines were declined**: they keep two figures about overlapping members, which with
one round are identical and sum to twice the truth, the confusion ADR 0393 ruling 1 refused.
**Dropping the rebuilt grade from the repair command was declined**: it costs a second command
after every repair and removes the immediate evidence that the repaired round grades clean.

## Ruling 2 — an extract that predates the count prints "not measured"

Where the extract summary prints a remainder line and the header carries no `UNREAD-REMAINDER`,
it prints `format_report`'s `unread remainder: not measured (extract predates the count)` line and
takes that report's status for the case instead of raising. The fix belongs to #1855's build.
**A separate ticket was declined** because it is the same line in the same branch, and **refusing to
rebuild such rounds was declined** because the rebuild repairs entry identifiers and does not read
the missing count.

## Ruling 3 — recorded in a new ADR

ADR 0393 is left unedited. **A dated correction there was declined** because its measured-at
declaration belongs to a different session and code, and its subject is the reader-remark graders.
**Recording the ruling on the ticket alone was declined** because ADR 0393 would keep saying the case
is open with nothing in the tree saying how it closed.

## What this does not reach

- Whether every population inside the rebuilt grade's figure is admissible is ADR 0230's question.
- [ADR 0416](0416-a-recursive-walk-never-enters-a-link-and-one-shared-walk-serves-the-census-the-sweep-and-the-after-action-review.md)
  ruling 4 adds components to the extract's remainder. Those reach this output through the header
  the rebuilt grade reads, and whichever build lands second keeps both.
- The glossary's **Unread remainder** entry already says one figure per report; this record applies
  that definition and changes no term.

## Build checklist

- In the `--extract` branch of `aar_scan.grade`, omit the summary's shared remainder line when a
  rebuilt grade is appended; keep the status computation over both populations.
- Read `UNREAD-REMAINDER` without raising; when it is absent, print the "not measured" line above
  and follow `format_report`'s status for that case.
- Add `aar_scan` to the conformance kit's one-line unread-remainder assertion, or assert one line in
  `test_aar_scan.py` if it does not opt in.
- Keep this record's two measurements as tests: a rebuilt round with a planted nonzero remainder
  prints exactly one `unread remainder` line and exits 2, and a rebuilt round whose header lacks the
  field exits without a traceback and prints the "not measured" line.
