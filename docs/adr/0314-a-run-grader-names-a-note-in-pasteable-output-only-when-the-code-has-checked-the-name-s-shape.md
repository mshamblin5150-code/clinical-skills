# A run grader names a note in pasteable output only when the code has checked the name's shape

**Measured at:** fa4fbc1dfd47a6f9213c996fb24ec5d23a0ff279

[#1479](https://github.com/mshamblin5150-code/clinical-skills/issues/1479) was filed from the
after-action review of a NUR5144 `batch-shift` run (shift of 2026-09-30). `differential_scan.py`
over the whole run reported a row-24 guideline-tail violation as a count, eleven note passes each
saw it, and the orchestrator guessed which note held it and guessed wrong. Grilled 2026-10-09
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The filename is gone before any grading starts.** `run_grader.read_run_directory` returns each
Markdown artifact's text and nothing else, so no `Note` or `Scan` in the family carries the file it
came from. `differential_scan`'s `--show` block prints `line N ROW 24 <label>` with no file, so on a
run of eleven notes even the private view cannot place a finding.

**Six graders share that reader and that gap.** `differential_scan`, `block_scan`,
`filled_vitals_census`, `specificity_scan`, `refusal_scan` and `anchor_scan` read a run through
`read_run_directory`; none of their reports names a file beside a finding, in either mode.

**Batch notes have one checked name shape and standalone notes have a rule.** `batch-shift` enters
each finished note as `note-N.md`, and `medatrax_posting.NOTE_NUMBER` already matches exactly that
shape. A standalone `clinical-note` file is named by date with no patient name, which is a written
rule that no code enforces, and `docs/agents/scratch.md` treats a filename under `scratch/` as
something that may itself carry PHI.

**Per-note counts already exist one note at a time.** `differential_scan.py --note <path>` scopes
the read to one file with counts-only output. It answers "what is wrong with this note"; it does not
answer "which note holds the row-24 violation", which is the orchestrator's question once
[ADR 0291](0291-a-writing-pass-stages-patient-text-in-a-scratch-root-and-a-hook-refuses-heredoc-writes-there.md)
ruling 3 makes the whole-run roll-up the orchestrator's.

## Ruling 1 — the pasteable report prints a name only when it matches `note-N`

The default report prints a file's stem only when the filename fully matches the batch shape
`note-N.md`, with decimal `N`, case-insensitively. Any other file is named by its position instead,
as `file K of M`, where `M` is the number of artifacts the grader read and `K` is the file's place
in the reader's name order; the position is stated beside the count where a name would go. The safety of the pasteable
output rests on a shape the code checked, never on a naming rule an author is expected to follow;
this is `reference_scan.py`'s bounded-output argument applied to a filename.

Printing every name as it is was declined because one hand-named standalone file would put a
patient name into output this repository calls safe to paste. Printing no name was declined because
it leaves the 2026-09-30 guess standing for every pasted report.

## Ruling 2 — the scope is every grader that reads a run through the shared reader

The shared run reader carries each artifact's path beside its text and owns the `note-N` rule in one
place. All six graders named above adopt it in this ticket. A seventh that later reads a run through
the same reader inherits both the attribution and the test in ruling 7. Splitting the five siblings
to a second ticket was declined: it is the same defect one module over, in one shared reader.

## Ruling 3 — `--show` names the real file, whatever its shape

Every `--show` finding line carries the file's real name. `--show` output is already private
working material that is read and never pasted, so restricting it buys no safety, and it is the only
place a hand-named file can be located without counting positions.

## Ruling 4 — violations, candidates and unread items are all named

A note is named beside each count that sends a reader to a note: a violation that fails the run, a
candidate that needs a reader and changes no status, and an item that contributes to the shared
`unread remainder N`. A count that names no note is the guessing this ticket removes, whichever kind
it is.

## Ruling 5 — a set-level row names its group or names nothing

`filled_vitals_census`'s shared-body row (`fixtures/day-b` B13) names every note in each group that
shares a filled height-and-weight pair. Its pressure-tilt row (B17) names no note and says the
finding is a property of the set. Listing every note with a not-normal filled pressure was declined:
those notes are individually correct, and pointing a fix at them invites moving an honest pressure
under the bar that [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s 2%
false-alarm rate was chosen to protect. Rows that already concern one note, such as a height naming
no age and sex or a missing BMI code, are named like any other row.

## Ruling 6 — names sit beside each row's count, and a clean report is unchanged

The names follow the count on the row's own line, as `(note-3, note-7 x2)`, where `xK` marks more
than one item in one note. A row whose count is zero, or a row that did not run, prints exactly as it
does today, so a clean report is byte-identical to the report before this change. No separate
per-note block is added, because a second place stating the same attribution is the copy that
drifts. This adds names, not measurements, so it does not put any measurement on the page twice and
leaves [ADR 0118](0118-the-conformance-kit-shapes-a-migrating-grader-s-value-and-vocabulary-and-the-fixture-row-is-the-finding-kind.md)
ruling 4's reason standing.

## Ruling 7 — the guarantee is an opt-in check in the shared conformance kit

`tools/grader_conformance.py` gains an opt-in case that drives each member's real command over a
temporary run directory holding a `note-N.md` with a planted finding and a hand-named file whose name
carries a marker. It asserts that the default report names `note-N` beside the fired row, that the
marker never appears in the default report, and that it does appear under `--show`. A separate test
derives the membership: every non-test module calling the path-carrying reader must opt in, so a
grader that adopts the reader cannot arrive without the check. Making it universal across the family
was declined because most members do not read a run of notes. Six hand-written per-module tests were
declined as six copies of one safety property, and a test of the shared rule alone was declined
because it cannot see a report that prints `path.name` directly.

## What this does not reach

A file named `note-N.md` whose author put patient text elsewhere in the run is outside this record;
the shape check certifies the name and nothing about the content. Whether a named note's finding is
clinically right remains each row's existing reading.
