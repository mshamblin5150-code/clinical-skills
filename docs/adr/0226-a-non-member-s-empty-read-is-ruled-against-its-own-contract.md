# A non-member's empty read is ruled against its own contract

[#1064](https://github.com/mshamblin5150-code/clinical-skills/issues/1064) was filed out of
[#922](https://github.com/mshamblin5150-code/clinical-skills/issues/922)'s grilling under
[ADR 0170](0170-every-grader-declares-the-posture-its-empty-population-takes.md) ruling 12, which
stopped the empty-population rule at `run_grader.MEMBERS` and filed the commands outside that family
as one ticket, each to be ruled against its own exit contract. Grilled 2026-09-14 at `origin/main`
`ac2fa385`; freshness gate `FRESH`. The clinician ruled every point below, one at a time, on that
date. Nothing is built here; this is the record the build reads.

Every exit status below was driven through the command's `main` over synthetic inputs, first by a
read-only agent and then re-derived by the grilling session at `ac2fa385`, except where a paragraph
says a behavior was read from the code. **The line anchors are dated, not durable**: the build this
record orders moves the ones in the code it changes, so a builder resolves each coordinate by the
symbol beside it.

## Measured before ruling

### An empty catalog reaches exit 0 only when three populations are empty at once

`threshold_coverage.main` loads the catalog through `guidelines_catalog.parse_catalog`, which finds
the catalog header and ends the table at the first line not starting with a pipe
(`guidelines_catalog.py:388-390`). A header followed by zero rows parses as an empty list with no
problem.

| input to `threshold_coverage` | exit | output |
| --- | ---: | --- |
| empty catalog, committed registry and sheets | 1 | 510 `REFUSING` lines |
| empty catalog, empty registry, empty sheet directory | 0 | `topics     0 from 0 catalog rows` |
| empty catalog, `--draft` | 0 | a registry with a header and no topic |

The catalog was made empty by removing the committed catalog's rows and keeping everything else. The
exit 0 needs the registry and the sheet directory emptied too, so the default command cannot reach it
today; `audit`'s two-direction join catches the empty catalog only because the other two populations
happen to be full. `--draft` and `--source-class` return before that join (`threshold_coverage.py:310-315`).
*Had the zero-row catalog been refused anywhere on this path, the all-empty run would not have
printed a clean topic line and exited 0.*

### A catalog broken by a blank line is caught by the joins, not by the parser

Inserting one blank line after the committed catalog's 90th row makes `parse_catalog` return 90 of
180 rows with no problem. The joins catch it: `guidelines_catalog` exits 1 with 704 failures, 450
readings, 163 rulings and 90 document audits with no catalog row plus one unsettled-cell entry, and
`threshold_coverage` exits 1 with 253 `REFUSING` lines. *Had the committed ledger and registry not
named every catalog document, both runs would have graded the 90 rows read and exited 0.*

### Five commands read that parser, and each already refuses on a parse problem

Read from the code, not driven: `guidelines_catalog.main` folds a parse problem into its failures and
exits 1 (`:1216-1226`); `threshold_coverage.main` exits 2 (`:304-307`); `threshold_draft.main`
prints `REJECTED` and exits 2 (`:631-634`); `uspstf_table.main` exits 2 on the raised `ValueError`
(`:1215-1217`); `guidelines_currency.main` prints `NOT GRADED` and exits 2 (`:1391-1393`). No test
parses a header-only catalog expecting zero problems.

### The audit ledger's empty table reads into its neighbor, silently where widths agree

`guidelines_catalog._parse_named_table` skips a non-table line with `continue` until it has read a
row (`:297-301`), so an empty table runs on into whatever table follows. `## Independent readings`
and `## Clinician rulings` are both six columns wide (`AUDIT_TABLES`, `:255-273`).

| ledger | readings | rulings | problems |
| --- | ---: | ---: | ---: |
| committed | 900 | 323 | 0 |
| committed, readings table emptied | 324 | 323 | 0 |

The 324 are the rulings table's header row, whose `column` cell reads `column`, and all 323 rulings.
Ending the table at the first non-table line, the rule `parse_catalog` already follows, parses the
committed ledger as 180 documents, 900 readings and 323 rulings with 0 problems, and the emptied
table as 0 readings. The line dates from `7ce906e5` (#106), whose message gives no reason for it.

`check_audit` joins catalog and ledger in both directions (`:703-833`). Over an empty catalog and the
committed ledger it reports 1,403 failures, one per document audit, reading and ruling with no catalog
row. With the catalog's `## Unsettled cells` list left in place, that list's 45 entries fail too; with
`parse_audit` stubbed to an empty audit those 45 are the only failures, so an empty catalog, an empty
unsettled list and an empty audit together exit 0.

### `uspstf_interval_reach` compares against a copy of the producer's sentinel

`uspstf_interval_reach.measure` selects its population by exact equality against its own
`NOT_STATED = "not stated"` (`:36`, `:123`), not `uspstf_table.NOT_STATED` (`:66`), which is the value
the producer writes. `test_uspstf_derived_cells.py` holds a third copy (`:38`). `read_table` reads
every row's `interval` cell through `guidelines_recs.parse_curated_table`, which raises when the
table's halves disagree: 143 rows, 135 `not stated`.

Respelling that one value in the committed rows and passing them to `measure` prints
`not stated rows: 0` and every ratio as `0 of 0`; nothing raises, so `main` returns 0. ADR 0028
ruling 5's pin (`(143, 135, 89, 83)`) turns the suite red on the committed table, but the command
reports a clean measurement of nothing. A header-only table already exits 2, through
`parse_curated_table`, with the message `no '## Recommendations' table` for a table that is present
and holds no row (`guidelines_recs.py:1084-1085`).

### `uptodate_store` prints one line for an empty index and a miss, and one for a missing and an empty root

| command | input | exit | output |
| --- | --- | ---: | --- |
| `search zebrafish` | index rebuilt over a store with no manifest | 0 | `QUERY zebrafish: 0 hit(s)` |
| `search zebrafish` | index holding one ingested topic | 0 | byte-identical |
| `sweep <root>` | a root that does not exist | 0 | byte-identical to the next row |
| `sweep <root>` | an empty directory | 0 | `unfiled topic-shaped material: 0 file(s), ...` |

`main` returns 0 for every search and sweep that raises nothing (`:625-643`). `ingest_dump` refuses a
dump with no topic, so an empty index is reachable only through `rebuild_index` over a store with no
manifest (`:428-439`). The index is one FTS table, so its row count is available without a match.
Read from the code: `sweep_unfiled` returns `SweepReport(0, 0)` for a missing root before walking
(`:570-571`), skips a file whose `read_text` raises (`:580-583`), and lets a failed `file_digest.sha256`
escape to exit 2 (`:578`). With no root argument it sweeps only `scratch_root()` (`:632`). No caller
reads either subcommand's status; `skills/practicum-case-study/SKILL.md:779-781` and `README.md:210-211`
name the commands only, and `research_ledger.py`'s membership join reads the manifests rather than a
search.

### `harvest_review` prints one sentence over three different populations

`harvest_review.main` exits 0 for an absent index, 2 for an unreadable one, and 0 otherwise
(`:153-177`); `test_harvest_review.py:164-190` pins all three. A readable `[]` index and an index whose
one entry's window holds nothing name-shaped print byte-identical output:
`harvest review: nothing unruled. Every harvested string has been decided.` Read from the code, the
same sentence prints when real harvested strings have all been ruled on (`render`, `:107-109`), the
only one of the three states it describes. No hook or tool runs the command or parses `--count`, and
its docstring states why its status is safe: it writes nothing, so an abandoned or empty review leaves
the firewall at full strength.

### The commands added to the ticket after filing already declare an empty read

The ticket's comments added `tracker_filed_from --harvest`, `tracker_population`, `python_floor`,
`command_tool_roster`, `tracker_coordinates`, `skills_mirror`, `tracker_bodies`, `map_scan`,
`day_file_text` and `research_ledger --heading-digests`, each with a posture stated by the record or
module that built it. `apa7_coverage` exits 1 with 388 refusing findings on an empty registry, measured
2026-09-11 and re-run by the agent here. `implementation_map.harvest_revision_chain` states its
high-water mark and unread remainder under [ADR 0199](0199-a-map-overwrite-is-attributed-rather-than-prevented.md)
ruling 5.

## Ruled 2026-09-14

### 1. The record rules six commands and one parser

`threshold_coverage`, `guidelines_catalog`, `uspstf_interval_reach`, `uptodate_store search`,
`uptodate_store sweep` and `harvest_review`, with the audit ledger's empty-table defect. The commands
in *The commands added to the ticket after filing* are decided where they were built and are not
re-ruled here. The revision-chain harvest stays with ADR 0199.

### 2. A ruling is held by a driven test, with no posture constant

Each command's test module drives its empty input through `main` and asserts the status and the line
this record names. The module docstring states the behavior once, and the `CLAUDE.md` section points
at the test. There is no module-level declaration and no repo-wide mapping: with no shared kit to read
it, a constant is a second copy of the test, the documentation object ADR 0093 ruling 4 refused, and a
mapping of non-members is the shared rule ADR 0170 ruling 12 refused under another name.

### 3. A catalog with no row is not scanned by `threshold_coverage`

It exits 2, on every path, `--draft` and `--source-class` included. The catalog is this command's
primary source and only a table parser establishes its row count; the registry and sheet directory
catching an empty catalog in the default run is a property of their default paths, not a contract.
`--draft` is the sharpest case, since it writes a header-only registry from nothing and a person may
commit it. A catalog whose table is broken by a blank line, so later rows go unread beside earlier
rows that are read, is a partial read rather than an empty one. It is not ruled here and takes no
ticket: on the committed tree the ledger and registry joins already refuse it, as measured above.

### 4. The zero-row problem lives in `parse_catalog`

`guidelines_catalog.parse_catalog` reports a catalog table holding no row as a problem. Every reader
refuses through the path it already has: `guidelines_catalog` exits 1, because the catalog is the
artifact it grades and the committed ledger's documents already establish the missing rows;
`threshold_coverage`, `threshold_draft`, `uspstf_table` and `guidelines_currency` exit 2, because for
them the catalog is an input. One empty catalog correctly taking 1 in its grader and 2 in its
consumers is ADR 0170 ruling 12's refusal of a shared exit rule, demonstrated. The three consumers
beyond this record's scope are reached by the parser change and nothing new is ruled about them.

### 5. The audit ledger's tables end at the first non-table line, and an empty one takes no check of its own

`_parse_named_table` adopts `parse_catalog`'s table end whether or not a row has been read. No
empty-table problem is added. Once ruling 4 guarantees a catalog row, `check_audit`'s join settles each
table's emptiness independently of the table parser: an empty `## Documents` or `## Independent
readings` table fails once per missing row, and an empty `## Clinician rulings` table is correct
wherever no reading disagrees with the catalog. A separate check would duplicate the join and misjudge
the rulings table. The regression test is the emptied-readings ledger, which returns 324 readings
today.

### 6. `uspstf_interval_reach` takes zero `not stated` rows as established

It keeps exit 0. `uspstf_interval_reach` and `test_uspstf_derived_cells` import `uspstf_table.NOT_STATED`,
so the comparison is against the producer's own value over a fully read table and a zero is true: the
derivation reached every interval. The render replaces the ratios with one qualifier, of the form
`no row reads "not stated": ADR 0028's reach has nothing to measure`, so a zero no longer prints the
lines a respelled sentinel printed. The header-only message in `parse_curated_table` says the table
holds no row; its status is unchanged. Refusing a zero would make the best outcome of ADR 0028's
question unreportable.

### 7. `uptodate_store search` refuses an empty index and states what a miss searched

An index holding no topic exits 2 with a diagnostic naming `ingest`. A miss stays exit 0, and each
query line states the indexed topic and dump counts beside its hits, of the form
`QUERY zebrafish: 0 hit(s) over <n> topic(s) in <m> dump(s)`. The counts are taken without the full-text
match. A miss is not moved to 1: no ruling reads a search zero, and a further meaning of 1 is ruling
10's declined question.

### 8. `uptodate_store sweep` refuses what it did not read

A root that does not exist exits 2 and names the root. An empty directory keeps exit 0. Every run
prints the roots read, the files examined, and the files that could not be read, counting a failed
`read_text` and a failed digest alike; any unread file exits 2 with the report still printed. Finding
unfiled material keeps exit 0. A missing root is a sweep that never ran and the silent skip is the
partial read shown as a clean whole that ADR 0132 ruling 7 refused mining for; the roots line is what
makes the `scratch/`-only default visible to a reader expecting another location covered.

### 9. `harvest_review` keeps every status and states its population

The absent, unreadable and `[]` statuses stay as pinned. The clean sentence becomes counts, of the
form `harvest review: 0 unruled of <h> harvested (<p> in a name position, <r> ruled) from <e> entries`,
integers only and safe to paste; `--count` is unchanged. The pinned `[]` status survives on its own
reason: the status gates nothing and an empty review weakens nothing. What was false was the sentence,
which claimed decisions over populations where none were made. Refusing entries that harvest nothing
would refuse a state `name_index.py` already reports, in a command whose status no caller reads.

### 10. Whether a shortfall status is a finding is declined, with no ticket

[ADR 0181](0181-a-day-file-reaches-the-corpus-through-one-command-and-a-rendered-page-waits-for-a-reading.md)'s
2026-09-11 correction routed this question to #1064. It is not ruled. Exit 1 carries several
meanings outside the grader family, each declared where its command lives: a shortfall
`name_index` and `skills_mirror` report and their write and repair modes close, pages awaiting a
reading in `day_file_text`, and a genuine zero in `guidelines_search`. No caller has been measured
reading one as another, so there is nothing for a ticket to act on, which `docs/agents/issue-tracker.md`
makes the condition for filing one. **The first measured misreading reopens it.** Ruling it here
would be the repo-wide exit convention ADR 0170 ruling 12 refused, reached from the other side. ADR
0181 carries a dated correction pointing here.

### 11. The build is one ticket

#1064's body is respecified as four independent clusters: the catalog parser (rulings 3 to 5),
`uspstf_interval_reach` (ruling 6), `uptodate_store` (rulings 7 and 8), and `harvest_review` (ruling
9). Each carries its driven tests, docstring, and `CLAUDE.md` section. The clusters share no code and
may land as separate commits on one branch.

## Not superseded

- **ADR 0170 ruling 12** stands. Nothing here extends its rule past `run_grader.MEMBERS`; each ruling
  above is taken against the one command's contract.
- **ADR 0138 ruling 9** stands, including its refusal to rule the discriminator repo-wide. Rulings 6
  and 9 apply its test per command.
- **ADR 0132 ruling 7** stands; ruling 8 above gives its report a denominator.

## Rejected options

- **A repo-wide mapping of non-member postures.** It is ADR 0170 ruling 12's refused shared rule.
- **A posture constant in each module.** Nothing but the module's own test would read it.
- **Relying on the registry and sheet directory to catch an empty catalog.** A default path is not a
  contract, and `--draft` bypasses both.
- **The zero-row refusal in `threshold_coverage` alone.** Three consumers would keep reading an empty
  catalog as a catalog.
- **An empty-table problem per audit table.** It duplicates the join and fails a correct empty rulings
  table.
- **Declaring the audit parser's misreading as a limit.** The defect reads a neighbor's rows as data
  with no problem reported; the repair is one line and changes nothing on the committed ledger.
- **Zero `not stated` rows as not scanned.** A fully read table's true zero would be unreportable.
- **Keeping `uspstf_interval_reach`'s copied sentinel with the suite pin as the guard.** The command
  itself would still report a measurement of nothing as clean.
- **`guidelines_search`'s contract whole for `uptodate_store search`.** It moves a miss to 1 with no
  measured need and adds a meaning to 1.
- **Only printing the count line on search.** An empty store would still answer every query with exit 0.
- **Refusing only the missing sweep root.** The silent skip would stay.
- **Coverage lines on the sweep with no status change.** A sweep that never ran would still exit 0.
- **Refusing `harvest_review` entries that harvest nothing.** It refuses an already reported state in a
  command whose status nobody reads.
- **A `grilling` ticket for the meaning of exit 1.** It is an observation with no measured failure.
- **Four build tickets.** Four placements and four closing sweeps for work one branch finishes.

## What this does not reach

**A partial read of the catalog table**, where a blank line hides later rows beside earlier rows that
are read. The committed ledger and registry catch it today; a catalog graded against a ledger and a
registry that share the same gap would not be caught.

**The three catalog consumers beyond scope**, whose refusal on an empty catalog comes from ruling 4's
parser change and whose other empty reads are not measured here.

**Whether a sweep root was the right root.** Ruling 8 prints the roots read; it does not know where
material ought to be.

**A name the harvest predicate does not recognize.** It is never harvested and so never unruled; that
limit is declared by `name_index.py` and `skills/batch-shift/SKILL.md` step 3.

**The meaning of exit 1 outside the grader family.** Ruling 10.

## What must not come out of this

**A retrofit onto `run_grader`** offered as the fix for any of these. A module's membership is a
separate question with its own records: `run_grader.REFUSED`, `run_grader.DEFERRED`,
`run_grader.GRADER_LOOKALIKES` and `run_grader.OUTSIDE_WALK`.

**`harvest_review`'s pinned `[]` status changed.** Ruling 9 changes the sentence and not the status.

**A search miss moved to exit 1**, or any other new meaning given to 1, by this record.

**A widened catalog parser** offered as the repair for ruling 3's blank-line partial read.
