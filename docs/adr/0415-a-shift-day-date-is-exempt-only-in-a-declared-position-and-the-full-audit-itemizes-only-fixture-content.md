# A shift-day date is exempt only in a declared position and the full audit itemizes only fixture content

**Measured at:** 1b98c073528a8bd0074a6ba589715228132759fc

[#1839](https://github.com/mshamblin5150-code/clinical-skills/issues/1839) was filed from the
tracker sweep that closed #1657's grilling. `python tools/phi_scan.py --all` reports so many
`corpus-date` lines in tracked prose that a date which really accompanies patient text would read
exactly like the rest. The ticket's comment later drove the commit-time half: the pre-commit hook
refused this repository's own ADR 0407 over one ruling-adjacent date in an ordinary sentence.
Grilled 2026-10-18 against `main` at `31b048a1`, where the freshness gate read `FRESH`; the figures
below were re-derived at the commit above when ruling 2's list was amended. The clinician ruled every point below in that session, one question at a time. **Nothing is built here;
this is the record the build reads.**

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

Record fields in tests and skill examples (`READ:`, `POSTED:`, `"measured_on":`) are **not**
positions. Their dates are arbitrary test values, and the same field shape is the shape a real run
record uses.

The cost is accepted: a patient date typed into one of these positions passes. Each position holds
a date by construction, and nothing checks that construction.

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
- `CLAUDE.md`: the *PHI pre-commit hook* section's audit sentence states that `--all` itemizes
  fixture-content dates and counts the rest, and names the declared positions by their object
  rather than copying them.

## What this record does not reach

- **Whether any of the 21 dates is in fact PHI beside its text.** That is a reading, and ADR 0077
  already records it as one.
- **The tracker surfaces.** Ruling 2's positions are keyed on tracked file paths; `tracker_scan`'s
  issue, comment and review records and `tracker_publish_hook`'s publications gain no position.
- **A date in an exempt position that is not what the position says.** Ruling 2's accepted cost.
- **The 119 name lines.** `--all` keeps exiting 1 on them until the harvested strings are ruled.
