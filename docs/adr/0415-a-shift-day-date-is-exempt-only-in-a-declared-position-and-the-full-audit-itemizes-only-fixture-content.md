# A shift-day date is exempt only in a declared position and the full audit itemizes only fixture content

**Measured at:** 0bd3d566198a63206267fffbaa01ae4155dfe008

[#1839](https://github.com/mshamblin5150-code/clinical-skills/issues/1839) was filed from the
tracker sweep that closed #1657's grilling. `python tools/phi_scan.py --all` reports so many
`corpus-date` lines in tracked prose that a date which really accompanies patient text would read
exactly like the rest. The ticket's comment later drove the commit-time half: the pre-commit hook
refused this repository's own ADR 0407 over one ruling-adjacent date in an ordinary sentence.
Grilled 2026-10-18 against `main` at `31b048a1`, where the freshness gate read `FRESH`; the figures
below were re-derived at `1b98c073` when ruling 2's list was amended. The clinician ruled every point below in that session, one question at a time. **Nothing is built here;
this is the record the build reads.**

[#1894](https://github.com/mshamblin5150-code/clinical-skills/issues/1894), filed from the tracker
sweep that closed this record's grilling, was grilled on 2026-10-19 against `main` at `592067b0`.
Its rulings are folded in below: one position added to ruling 2, and ruling 6. At `98bb35f3`,
where the freshness gate read `FRESH`, the audit's totals re-derive unchanged at 1,460 date lines
across 323 files, and the welded-date census under *Measured before ruling* was re-derived there
with the same figures it had at `a4bceb36`. The per-position rows of the census table were not
re-run.

[#1921](https://github.com/mshamblin5150-code/clinical-skills/issues/1921), filed from the tracker
sweep that closed #1894's grilling, was grilled on 2026-10-19 against `main` at `0bd3d566`, where
the freshness gate read `FRESH`. Its rulings are ruling 7 below, which extends rulings 2 to 4 to
`tracker_scan --history`. At the commit above, the audit's totals re-derive unchanged at 1,460 date
lines across 323 files. The welded-date census re-derives unchanged at 196 lines, 189 of them silent,
in 13 files, with the same four row figures. This session wrote its own digit-bounded reader for it.

**No date value, file line or line number from the scan appears in this record, and none may be
added.** A line coordinate in a tracked file points at the date on that line, and the date then says
which days carry a corpus entry. Re-derive with `--show` from a clone where `scratch/` is present,
and read it without pasting it.

## Measured before ruling

`python tools/phi_scan.py --all --allow-no-corpus`, run in a worktree whose corpus layer reads
`ACTIVE` through the owning checkout, exits 1 with **1,460 `corpus-date` lines across 323 tracked
files**, carrying **21 distinct dates, every one of them in 2026**; 1,447 of the lines are ISO
renderings. The same run reports 119 `corpus-name` lines, and the 21 harvested strings that have
never been ruled on are the clinician's to review through `harvest_review.py`. Names are outside
this record.

The census below sorted every date line by the text immediately before the date. Its matchers are
this session's, not a committed tool's, so its figures are a baseline and the build re-derives them
with its own grammar.

| Where the date sits | Lines |
|---|---:|
| `reference/guidelines-catalog-audit.md`, the `confirmed_date` cell | 323 |
| `reference/thresholds/*.md`, the `read <date>; blind <date>` cell | 258 |
| `reference/thresholds/*.md`, the `citations resolved against <path> on <date>` line | 73 |
| `reference/thresholds/*.md`, the `DATE: <date>` line | 44 |
| A dated ruling or correction marker anywhere (the openers listed in ruling 2) | 157 |
| A file under `fixtures/` other than a `README.md` or `assertions.md` | 1 |
| Everything else: ordinary prose and test strings | 604 |

That last row includes 77 lines in fixture-set `README.md` and `assertions.md` files, which are
dated measurement and claim prose about a run, and 164 under `tools/`, mostly test strings. **No
preserved note or worksheet carries a shift-day date.** The single fixture-content line is in
`fixtures/classmate-context/project-context.md.in`, a copy of a run's project-context record used
as test input.

**The 1,460 is a floor, not a count.** `ISO_CORPUS_DATE` is `\b\d{4}-\d{2}-\d{2}\b`, and a word
boundary needs a non-word character on each side, so a date welded to a letter, digit or underscore
is never read. A separate session reader at the commit above, one digit-bounded ISO pattern joined to
`corpus_identifiers()` and `build_index()`, counts **196 tracked lines carrying a shift-day date the
committed matcher cannot see**, 189 of them on lines that matcher reports nothing on, in 13 files:

| Where the welded date sits | Lines |
|---|---:|
| `reference/completion-check-starts.tsv`, the `start` cell, a date joined to a time by `T` | 149 |
| `tools/`, test strings carrying a `T`-joined timestamp | 31 |
| One ADR, a `T`-joined timestamp | 1 |
| `docs/adr/supersession-classification-1518.json`, a date directly after a JSON `\n` escape | 15 |

The same reader's US-numeric and written-English variants, with the trailing word boundary replaced
by a digit boundary, find no further shift-day date. None of the 196 is fixture content. Every one of
the 149 start-table dates sits in that file's second tab-separated cell; none is anywhere else in it.

**One position is already exempt, and it was never ruled as a principle.** `_scan_line` masks the
`checked` cell of `skills/_shared/reference/apa7-coverage.md`, because a visit on the day a public
manual page was read does not make that read a patient date. It arrived inside #1350's citation
fix, with no record. The three flagged lines in that registry are in its `refutation` cell and in
re-confirmation prose, not in the masked cell.

**#1518's objection is to value, not to position.** `phi_scan.public_adr_date_text` exempts only
ADR opening metadata and exactly attested historical quote spans, and its docstring states why: a
date matching a public date by value alone establishes nothing about the surrounding patient text.
A cell that can hold only a date is evidence about what surrounds the date, which a value never is.

## Ruling 1 — a shift-day date is exempt only in a declared position

A corpus date is exempt only where it sits in a **declared position**: a place the repository's own
rules require a date to be written and that cannot hold patient text. A position is named by an
exact grammar keyed on its file and its surrounding fixed text, as the APA `checked` cell already
is. Nothing is ever exempted by matching its value against a list of public dates.

Rejected: keeping every shift-day date a finding and declaring the audit red by design (the audit
never singles out a real date, and every ruling dated on a shift day is refused at commit); and
ceasing to write literal dates (it contradicts ADR 0280's dated markers and the dated correction
style throughout `CLAUDE.md`, and preserved records cannot be edited).

## Ruling 2 — the declared positions are the dates the repository requires

The positions are exactly these, and only the date token in each is masked:

- `reference/guidelines-catalog-audit.md`: the `confirmed_date` cell of its table.
- `reference/thresholds/*.md`: each date in the `read <date>; blind <date>` cell, the date ending
  `citations resolved against <path> on <date>`, and the date in `DATE: <date>`.
- `skills/_shared/reference/apa7-coverage.md`: the existing `checked`-cell position, moved into the
  same declaration without changing what it matches.
- `reference/completion-check-starts.tsv`: the date opening the `start` cell, the second
  tab-separated cell of a data row, whether the cell is the date alone or the date joined by `T` to
  a time and offset. The time after the date is not a date and stays scanned like any other text.
- A **dated ruling or correction marker** in any tracked file outside fixture content: a date
  directly after `## Ruled `, `## Addendum, `, `Grilled `, `Grilled on `, `**Correction, `,
  `**Corrected `, `**Corrected in place `, `*(Corrected `, `*(Corrected in place `, `*Corrected `,
  `*Corrected in place `, `*Superseded `, `*Superseded in part ` or `*Superseded grounding marked `.
  The text after the date stays scanned.

**Corrected in place 2026-10-19:** the clinician ruled that the marker list also takes
`*Corrected `, `*Corrected in place `, `*Superseded in part ` and `*Superseded grounding marked `.
As first recorded it named only the double-asterisk and parenthesized correction forms and the bare
`*Superseded `, which left out the single-asterisk correction form used across 17 ADR files, one of
them carrying a shift-day date the scan flags. The census matcher had the same omission, which is
why its marker row moved by one. Found by the tracker sweep closing this record's grilling
([#1839](https://github.com/mshamblin5150-code/clinical-skills/issues/1839)).

**Corrected in place 2026-10-19:** the clinician ruled the start-date table's `start` cell a
declared position ([#1894](https://github.com/mshamblin5150-code/clinical-skills/issues/1894)). It
was absent from the list because the committed matcher could not see a `T`-joined date, so its 149
shift-day rows never reached the census. Once ruling 6 makes them visible, a build landing on a shift
day would be refused at commit, and the only way past that refusal is to move the time the check
starts grading. That is the back-dating ruling 5 exists to prevent. Rejected: widening the matcher
with no new position (that refusal), and leaving the `T`-joined form unread with a declared limit
(a measured blind spot in the one scanner whose job is to have none).

Record fields in tests and skill examples (`READ:`, `POSTED:`, `"measured_on":`) are **not**
positions. Their dates are arbitrary test values, and the same field shape is the shape a real run
record uses.

The cost is accepted: a patient date typed into one of these positions passes. Each position holds
a date by construction, and nothing checks that construction. The start-date table is the partial
exception: `completion_checks.registry` raises on a `start` cell that does not parse as an ISO date
or timestamp, so that cell is checked to hold a date, though not checked to hold the right one.

## Ruling 3 — the full audit itemizes fixture content and counts the rest

`--all` splits its `corpus-date` report:

- A date in **fixture content** (ruling 4) is listed one line at a time, as today, and sets exit 1.
- A date anywhere else outside a declared position is printed as **a count per top-level area**,
  and does not change the exit status. `--show` still lists every such line.

The audit's question is whether a date of service sits with patient text, and fixture content is
the only tracked place patient text lives. A dated ruling in an ADR or in a fixture-set README is
the same kind of line wherever it sits.

Rejected: rewording the committed prose dates once. It rewrites ratified records to quiet a
matcher, and it does not stay done: a new shift day can match an old ruling date at any time.

`corpus-name` and shape findings are untouched by this ruling: they stay listed and graded.

## Ruling 4 — fixture content is defined by exclusion

**Fixture content** is every tracked file under `fixtures/` except files named `README.md` or
`assertions.md`. A fixture set's notes, worksheets, JSON and JSONL records, templates and any file
of a kind not yet seen are fixture content by default. A new prose file under `fixtures/` with
another name is itemized and fails the audit until it is renamed or this rule is revisited, which is
the safe direction. A declared list of record layouts was rejected: it is the fixture-format catalog
`CLAUDE.md`'s extractor-coverage rule refuses as a control, and a set left off it would have its
dates fall silently into the count.

Fixture content is not exempt by any ruling-2 marker.

## Ruling 5 — the positions apply at commit as well as in the audit

The staged check and `--all` read dates through the same exemption, and both honor ruling 2. A
required date must not be refusable at commit, because the only ways past that refusal are to
back-date a registry cell or to leave out a marker ADR 0280 requires.

Ordinary prose is unchanged at commit: a newly added line carrying a shift-day date outside a
declared position is still refused, and a reword is the remedy. Ruling 3's counting applies only to
lines already committed, as `--all` reports them.

## Ruling 6 — a date is read wherever no digit touches it

Ruled 2026-10-19 on [#1894](https://github.com/mshamblin5150-code/clinical-skills/issues/1894).
The corpus layer reads a date wherever the characters on either side of it are not digits. A letter,
an underscore, a `T` joining a time, or an escape such as JSON's `\n` no longer hides a date; a digit
still does, because a longer number is not a date. Every hit must still parse as a real calendar
date, as today.

This applies to all three renderings the corpus layer reads. In the US-numeric form both ends become
digit boundaries. In the written-English form only the year end does: the month name at its start
keeps its word boundary, because a letter before a month name makes it part of another word. The
census above finds no shift-day date that only those two widenings would reach. They are included so
that the scanner's boundary rule is one rule rather than an ISO special case.

What the newly visible lines become follows rulings 2 to 5 unchanged. The 149 start-table dates fall
in ruling 2's new position. The 15 escaped dates in the #1518 classification report, the 31 test
strings and the one ADR line are outside fixture content, so `--all` counts under ruling 3 each one
that `public_adr_date_text`'s existing #1518 attestation does not already mask; the census read raw
text and did not apply that view, so how many it masks is the build's to re-derive. A
newly added line of that kind is refused at commit under ruling 5, and changing an arbitrary test
value is the remedy.

Rejected: reading the `T`-joined form alone. It fixes the instance the ticket measured and leaves
every other welded form unread, which is the partial matcher `CLAUDE.md`'s extractor-coverage rule
refuses to treat as a clean read.

## Ruling 7 — the history scan follows the same rule as the full audit

Ruled 2026-10-19 on [#1921](https://github.com/mshamblin5150-code/clinical-skills/issues/1921).

**Measured before ruling.** A session reader at `0bd3d566` imported `tracker_scan.blob_records` and
`phi_scan.scan_file_text` from this checkout and ran them with the corpus layer `ACTIVE` and the
pull-head refspec configured. It printed counts only. It read **9,080 reachable text blobs**. Scanned
under their `blob <id> <path>` labels, as `--history` scans them, **3,377** carry a `corpus-date`
finding, for **20,029** findings. **One** is in fixture content as ruling 4 defines it, and it is the
same project-context test input the full audit reports. The same blobs carry 373 `corpus-name`
findings, 139 of them in fixture content, and 60 shape findings, none in fixture content. A
digit-bounded ISO reader, ruling 6's boundary, finds about 4,000 further shift-day dates. 3,262 of
those are in the 22 versions of the start-date table. So the history scan already had #1839's
problem before ruling 6, and at roughly fourteen times the full audit's size.

Scanning the same blobs under their label's path, with no position built yet, drops 473 findings.
Those are today's two path-keyed exemptions, the APA `checked` cell and the ADR opening and #1518
attestation view. About 15,000 findings in ordinary prose and test strings sit outside every ruling-2
position, so positions alone would leave the scan unable to single out a real date.

A second reader walked all 2,803 distinct trees reachable from the clone's refs. **8** blobs are
reachable under more than one path, and **none** is under both a fixture-content path and another
path. `git rev-list --objects` attaches one path to an object, the first it meets. So the single
label classifies every blob correctly today, but nothing keeps it that way.

**The ruling.**

- `--history` scans each blob under the path its label carries, so ruling 2's positions and
  `public_adr_date_text`'s path-keyed view apply to a blob as they apply to the tracked file. A
  historical blob is read with today's grammar. Under the next limb that grammar changes only a
  count, never the exit status.
- `--history` partitions `corpus-date` findings as ruling 3 partitions `--all`. A date in a fixture-
  content blob is listed and sets exit 1. Any other date outside a declared position is printed as a
  count per top-level area of the label's path, and does not change the exit status. `--show` still
  lists every such finding. `corpus-name` and shape findings stay listed and graded.
- **A blob is fixture content if any path it was ever committed under is fixture content**, by
  ruling 4's definition. That decision is not made from the single label. The report prints how many
  blobs are reachable under more than one path.

Rejected: positions alone, because about 15,000 prose findings would remain and the scan still could
not single out a real date. No exemption at all, because it would leave the history scan with about
24,000 findings once ruling 6 is built, which is #1839's problem on another surface. Trusting the
single label for fixture content, because a fixture blob saved byte-for-byte under another name
would have its dates counted instead of graded, silently, in the one class that decides the result.

## Build checklist

- `tools/phi_scan.py`: replace the inline APA rewrite in `_scan_line` with one declared-position
  object holding ruling 2's grammar, applied through the same date-only view
  `public_adr_date_text` produces so that names and shapes keep reading the original bytes.
- `tools/phi_scan.py`: in `--all`, partition `corpus-date` findings into fixture content (listed,
  graded) and the remainder (counted per top-level area, not graded); keep the layer report's
  scope row on every run and print the remainder count even when it is zero.
- `tools/test_phi_scan.py`: for each declared position, a positive control on a synthetic corpus
  date and a mutant one character off the grammar that is still refused; a date in each position
  inside a fixture-content file still refused; the staged path honoring the positions; an `--all`
  run whose only date findings are in prose exiting 0 with the count printed; one in fixture
  content exiting 1; and a file under `fixtures/` of an unseen kind treated as fixture content.
- `tools/phi_scan.py`: replace the word boundaries in `ISO_CORPUS_DATE` and `NUMERIC_CORPUS_DATE`
  and the trailing one in `WRITTEN_CORPUS_DATE` with digit boundaries (ruling 6), and give the
  start-date table's `start` cell its place in the declared-position object.
- `tools/test_phi_scan.py`: for ruling 6, a synthetic corpus date read when joined by `T` to a
  time, after a JSON `\n` escape, and before an underscore, in each rendering it applies to; the
  same date with a digit on either side not read; and a month name preceded by a letter still not
  read. For the start-date position, a positive control on a `T`-joined row and on a date-only row,
  a mutant with the date in the `check` cell still refused, and a `T`-joined date in an ordinary
  test string still refused at commit.
- `tools/outbound_search.py`: its pretyping refusal reads `phi_scan`'s three date patterns
  directly, so ruling 6 widens it too, in the safe direction. Name that in the build and add one
  control: a query carrying a `T`-joined corpus date is refused.
- `tools/tracker_scan.py` (ruling 7): recover every path each reachable blob was committed under
  with one history read, for example `git log --all --raw --root --no-renames -z`, rather than one
  `ls-tree` per tree. Pass the label's path to `phi_scan.scan_file_text`, and partition
  `corpus-date` findings with the same fixture-content predicate and per-area count `--all` uses,
  imported from `phi_scan` and not restated. Print the count of blobs reachable under more than one
  path on every `--history` run.
- `tools/test_tracker_scan.py` (ruling 7): in a throwaway repository, a declared-position date in an
  old version of a position file is masked; a date in an old fixture-content blob is listed and
  exits 1; a run whose only date findings are in prose blobs exits 0 with the count printed; a blob
  committed byte-for-byte under a fixture path and under a non-fixture path, labeled with the
  non-fixture one, is still graded; a `corpus-name` finding in a prose blob is still listed.
- `CLAUDE.md`: the *Tracker scan* section states that `--history` follows ADR 0415's positions and
  partition, and names ruling 7 instead of copying it.
- `CLAUDE.md`: the *PHI pre-commit hook* section's audit sentence states that `--all` itemizes
  fixture-content dates and counts the rest, and names the declared positions by their object
  rather than copying them.

## What this record does not reach

- **Whether any of the 21 dates is in fact PHI beside its text.** That is a reading, and ADR 0077
  already records it as one.
- **The tracker surfaces.** Ruling 2's positions are keyed on tracked file paths; `tracker_scan`'s
  issue, comment and review records and `tracker_publish_hook`'s publications gain no position.
- **The other git-history surfaces.** Ruling 7 reaches `--history`'s blobs only. `--commits` and
  `--paths` read text that was never a file, so no position applies to them and their findings are
  not partitioned. A blob reachable from no ref is still not scanned, as the `tracker_scan`
  docstring already states.
- **A blob whose path no longer matches its grammar.** Ruling 7 reads an old version of a position
  file with today's grammar. A date the old grammar held in a different place is counted instead
  of masked. That moves a count and never a result.
- **A date in an exempt position that is not what the position says.** Ruling 2's accepted cost.
- **The 119 name lines.** `--all` keeps exiting 1 on them until the harvested strings are ruled.
- **A date rendering none of the three patterns reads.** Ruling 6 changes where a date may sit
  relative to its neighbors, not which renderings exist; a day written in an unsupported order or
  spelled out is still read only if the shape layer recognizes it, as `CLAUDE.md` already states.
