# Threshold sheets

The deliverable of the [#80](https://github.com/mshamblin5150-code/clinical-skills/issues/80)
series, in the shape [#83](https://github.com/mshamblin5150-code/clinical-skills/issues/83)
settled. Per topic, **the decision points only** — drug, dose, duration, target number,
referral and follow-up threshold, staging cutoff. Not full text.

That shape is deliberate and it is what makes the series shippable. **Facts are not
copyrightable; expression is.** A restated staging table is a fact this repo may hold
freely. A dumped guideline PDF is the copyrighted expression, and it also happens to be
too large to belong here. The distilled form is both the legally clean artifact and the only one small
enough to commit.

The 179 source PDFs stay outside this repo at `C:/codeing/guidelines-src`
([#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87)). Nothing a
consumer runs needs them — they need the derived facts.

## The quoting posture, ruled against a public repo

**Ruled 2026-08-18 by the clinician, on
[#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223).** The paragraphs
above were written while this repo was private, so they argued that the *format* is clean
and never asked whether *publishing* it is. That question is now asked and answered, and
the answer is that nothing here changes — but the judgment is written down rather than
implied, because #223's whole point is that it had never been made.

After [#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429), the
posture for every non-USPSTF work rests on **short, attributed quotation**, not on the
work being public domain. Public availability does not change copyright status. What
matters here is that each minimal snippet is tied to its society, document, page and
recommendation identifier and is used to make a fabricated clinical citation
detectable; USPSTF's separate public-domain status is not a premise for the other
sources.

**What is quoted, measured rather than characterized.** In
[hypertension.md](hypertension.md):

| | |
| --- | --- |
| rows | 74 |
| snippet cells, and distinct snippets among them | 74, of which **70** are distinct |
| words across the distinct snippets | **773** |
| longest / median / shortest snippet, in words | 15 / 11 / 6 |
| words in the `## Populations` table, 19 rows of verbatim scope wording | **115** |
| pages in the source guideline | **105** |

In [diabetes.md](diabetes.md), re-ruled on #482 after its complete source-page read
rather than inheriting the first sheet's answer:

| | |
| --- | --- |
| rows | **357** |
| snippet cells, and distinct snippets among them | 357, of which **354** are distinct |
| words across the distinct snippets, excluding the 36 `RENDERED:` markers | **5,063** |
| longest / median / shortest quoted fragment, in words | 55 / 12 / 1 |
| words in the `## Populations` table, 125 rows of verbatim scope wording | **1,022** |
| pages in the source guideline | **377** |

**Every row in both tables above is re-derived by a test, and none of them is a figure
only this paragraph holds** — which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143). The first five
come from the sheet, read through `threshold_sheet.parse` rather than a reader of the
test's own; **the page count comes from [guidelines-catalog.md](../guidelines-catalog.md)**,
because the sheet does not carry it and a remembered page count is exactly the sort of
figure that goes stale:

```bash
python -m unittest test_threshold_sheet -k Quoting   # run from tools/
```

**Why verbatim and not paraphrase, which is the part that is not a taste call.** The
snippet is the sheet's honesty mechanism rather than its prose. `threshold_sheet.py`'s
tier 0 requires the snippet from an exact source to occur in its own recommendation
record, tier 1 requires the number in a row's `value` to appear in that snippet, and
tier 2 requires the snippet to be found on the cited page of the source PDF.
**Paraphrase the snippet and those provenance gates stop working** — a restatement cannot be located on a page, so a
fabricated citation stops being detectable. The verbatim string is doing evidentiary work
that no paraphrase does, which is the fair-use factor that actually bites here.

**And the attribution is per row, not per file.** Every row carries the society, the
document, its source URL, the page, the recommendation identifier and the class of
recommendation. A reader who doubts a row jumps to the page in one move; that jump is the
whole reason `page` is a column.

**What this does not license.** The sheet is a set of decision points, not a substitute
for the guideline, and it says so in its own opener. Nothing here blesses committing a
`recs-*.json` — that file holds the society's recommendation text **in full** and is what
`guidelines_recs.py` refuses to write inside a checkout and `.gitignore` now catches
anyway. The 179 source PDFs stay outside the repo, unchanged by this ruling.

**No later sheet gets this for free.** Diabetes was re-asked against one 377-page ADA
standard and answered with 5,063 quoted words across 354 distinct minimal snippets. A directory
of twenty sheets quoting one society is still a different quantity question, and it is
worth re-asking there rather than reading either ruling as settling the class.

## Grading a sheet

```bash
# Build the recommendation record first, OUTSIDE the repo -- always. It holds the
# society's recommendation text in full, which is the copyrighted expression this
# whole format exists to avoid committing, and guidelines_recs.py refuses to write
# it inside any git checkout.
# One record per SOURCE, named for the key that source carries in the sheet's
# `## Sources` table -- `aha-2025` here.
python tools/guidelines_recs.py \
    "C:/codeing/guidelines-src/AHA ACC/jones-et-al-2025-....pdf" \
    --doc-id "AHA ACC/jones-et-al-2025" \
    --json C:/codeing/guidelines-index/recs-aha-2025.json

python tools/threshold_sheet.py reference/thresholds/hypertension.md \
    --recs aha-2025=C:/codeing/guidelines-index/recs-aha-2025.json

# `--recs` is repeatable, once per source. Give it twice for a sheet citing two
# societies, or leave it off and let `--recs-root` resolve `recs-<source key>.json`
# for every one of them -- which the command above does too since #177, so a sheet
# grades the same whichever way it is reached.
#
# `--all` resolves from `--recs-root` and takes no `--recs`: a source key is
# sheet-local, so which sheet's source a record answers for is unknowable across a
# directory. A sheet where ANY source has no record exits 2, never 0.
python tools/threshold_sheet.py --all
```

**A bare `--recs <path>` is still accepted where the sheet declares exactly one
source**, and refused where it declares two — because which source it answers for is
then a guess, and guessing is what
[#177](https://github.com/mshamblin5150-code/clinical-skills/issues/177) is about.

**The record is matched to the source by the PDF it was built from, not by
`--doc-id`.** `guidelines_recs.py` writes the PDF's path into the record's `source`
field, and that is what the grader compares against this table's `document` cell;
`--doc-id` is free text and the record behind the sheet above carries an abbreviated
one. A record built from another guideline is **refused** — see the holes below.

**Two more gates landed on
[#174](https://github.com/mshamblin5150-code/clinical-skills/issues/174)**, and both
need something this repo does not carry:

```bash
# WATERMARK, #83 gate 4. Reads the strings #80 stripped as page-repeated text out of
# `manifest.json` and REFUSES a row that carries one -- the text stream was
# interleaved there, so the row's label and its number may never have been adjacent.
# `--text-root` is derived from `--pdf-root` when it is not given; absent, the gate
# skips behind a banner and never passes.
python tools/threshold_sheet.py reference/thresholds/hypertension.md \
    --text-root C:/codeing/guidelines-text

# SECOND READ, #83 gate 5. Two commands and a reader in between.
python tools/threshold_sheet.py reference/thresholds/hypertension.md \
    --brief --span "narrative sections and evidence tables"
# ... hand that work order to somebody who has NOT seen the sheet, and grade what
# they hand back:
python tools/threshold_sheet.py reference/thresholds/hypertension.md \
    --second-read C:/codeing/guidelines-index/second-read-hypertension.json
```

**The read is written by an agent that has not read the sheet, and that independence
is the whole instrument.** `--brief --span` prints one document, span name and page
range and nothing else from the sheet — a
test drives a distinctive quantity, value and snippet through the sheet and asserts
none of them comes out. Naming the pages is itself a small leak and is named as one:
without it the reader has a hundred-page guideline to search, and the diff would
measure how thoroughly it searched rather than what it read.

**The record it hands back is:**

```json
{"read_on": "2026-08-19",
 "briefed": {"document": "AHA ACC/jones-et-al-2025-...",
              "span": "narrative sections and evidence tables",
              "pages": "11-74"},
 "values": [{"document": "AHA ACC/jones-et-al-2025-...",
             "page": 41,
             "value": "<130 mm Hg",
             "about": "the office systolic target for adults on treatment"}]}
```

Every field is required, including all three fields in `briefed`, and a record short of one is **not graded** rather than
graded on what is left — `bind_recs`' ruling, for its reason. `read_on` is required
too: a read carries no trace of which extraction of the corpus it was taken against,
and this repo has watched three review agents read one shared build directory a second
branch had overwritten.

**The gates.** What each one can see, and what it cannot, is written out in full in
`tools/threshold_sheet.py`'s docstring rather than summarized here, on
`icd10_lookup.py`'s terms: a rule is cheapest to keep true where the code that enforces
it lives. What belongs here is the part a reader of the *sheets* needs.

**What a reader of the sheets has to do by hand is gate 5's pairing.** The command
prints each row's `quantity` and `population` beside the independent reader's own
description of the number, and grades neither — comparing two free-text descriptions
is a reading. **That is the one thing that reaches the largest hole below**, and it
reaches it only if somebody reads the pairs.

## The file format

A sheet is Markdown, and every part of it is read by the grader. The
`<!-- schema: threshold-sheet/2 -->` marker is what says so; a file without it is
reported as **not graded** rather than as clean.

### `## Sources`

One row per document, with the key each threshold row cites, the society, the
document's `doc_id` (which is its path under the corpus root, no suffix), the version,
the publication date, the URL, and the **mode**.

**Version, publication date and URL are required, and a blank one is refused.** They
were parsed past until they were not — the grader kept society, document and mode and
dropped the other three, so a sheet could carry a threshold with no edition behind it
and grade clean. That is the failure this format exists to prevent: societies revise,
and 2017's number sitting under a 2025 heading is wrong in the most expensive way.

**The columns are read by name against the header row**, not by position, so adding a
column cannot silently redefine `mode` — which is the cell deciding whether an
omission refuses or merely warns.

**Mode is not a style choice and is not set by hand.** It comes from
`tools/guidelines_recs.py`, and it says whether that document's recommendations could
be counted *exactly* or only *bounded* by matching a marker in running text. An exact
source has its omissions **refused**; a bound source has them **warned**. See #83
decision 1.

**Identifier membership follows the same evidentiary split.** A row citing an
identifier absent from its source's `exact` record is refused. The same absence in a
`bound` record is not graded: the marker reader can under-report a recommendation the
sheet author read directly. A source-free `## Coverage` identifier absent from every
record refuses only when every declared source has a loaded `exact` record; otherwise
the gate cannot know which incomplete or absent record should have carried it.

**This is identifier-level accounting, not occurrence-level accounting.** A real
record can repeat one `rec_id` for more than one recommendation occurrence, so a set
membership pass does not prove that every repeated occurrence was separately audited.
That audit remains outside `COVERAGE`.

**Exact arrives two ways since [#173](https://github.com/mshamblin5150-code/clinical-skills/issues/173),
and the record's `counted_from` says which.** One is a ruled `COR | LOE` table in the
document itself. The other is [`reference/guidelines-uspstf.md`](../guidelines-uspstf.md),
which is **also** a ruled table — one recommendation per row, the grade in a cell — and
is where the 90 USPSTF documents are answered from. **That second one is read out of a
committed file rather than out of the PDF's own layout**, which is an objection the
first one does not have to meet, so every row is checked to be on the page it cites
before it is counted and a document whose rows do not check is reported as **not
scanned** rather than counted short. That check is what earns the word, and it is the
answer to #173's own prohibition — *do not promote a document to exact that is not read
out of a ruled table*.

**What the mode still does not say is whether the source is complete.** Neither reading
claims every recommendation in the document was found; a table the parser did not
recognize and a curated row the builder did not extract are the same hole, and gate 2 is
silent about both. *The sheet accounted for everything the record holds* and *the record
holds everything the guideline states* are separate claims, and only the first is
checked here.

### `## Scope`

The sections-read line, and it is load-bearing rather than courteous. **A synthesis
pass is a reading and readings miss things.** If only the recommendation tables were
read, the sheet says so, so that *absent from the sheet* is never misread as *absent
from the guideline*.

**Both halves are required and the grader refuses a sheet missing either.** The
section must say what was read and, separately, what was **not** — `Read:` and
`Not read:`. The second limb is the one doing the work: a list of what was covered
tells a clinician nothing about whether a number's absence here means the guideline
is silent. A sheet with no `## Scope` section at all is refused outright.

**That this is graded at all is recent, and the gap is worth naming.** The section
was described here as load-bearing while nothing checked it — deleting it entirely
from `hypertension.md` left every gate at `0` and the run at exit `0`. So the honesty
clause was the one part of the format a sheet could drop for free, and dropping it
scored *cleaner*, since the only trace was a `last resolved` line that touches no
exit status.

The grader reads these two phrases from **this section alone**, never from the
document as a whole, so a threshold row whose snippet happens to quote *"not read"*
cannot discharge the rule. That is `block_scan.py`'s mention-versus-use distinction,
which applies wherever a keyword decides a verdict.

It also carries `citations resolved against <corpus> on <date>`. That is a **held
declaration**, not a courteous footer. CITATION tier 2 refuses its absence whether the
live PDF gate ran or skipped. When the gate ran, it also refuses a corpus path that does
not resolve to the run's `--pdf-root` and a date in the future; an older date is not a
finding. When the gate skipped, the line's content cannot be checked and is the only
artifact-level distinction between *checked once against real PDFs* and *never checked*.

The corpus token deliberately remains a machine-local path. A second machine reaches a
disagreement only when its owner explicitly supplies a live `--pdf-root`; the ordinary hook
keeps the absent maintainer-path default there, so tier 2 skips and cannot compare the two
paths. After an explicit live run, updating the line makes the maintainer's next live run
refuse in the mirror direction. That one-edit ping-pong is a declared limit and a re-ruling
trigger, not a silent pass and not a request for date arithmetic.

Every line currently present in `## Scope` is held by something. SCHEMA refuses a missing
`Read:` or `Not read:` limb, and CITATION tier 2 holds the resolution declaration in both its
live and skipped states. ADR 0019's accepted-distrust declaration is another instance of the
same **Held declaration** principle, but its WATERMARK mechanism belongs to #460 and is not
claimed by this build: the resolution declaration holds a skip and presence, while that
separate declaration holds a pass.

When WATERMARK passes only because `--allow-untrusted-provenance` admitted the
extracted corpus, this section also carries the exact block the command prints:

```text
accepted distrust against <corpus> on <date>:
  - <one artifact_provenance reason, verbatim>
  - <another artifact_provenance reason, verbatim>
```

The source path and date identify that run, and every reason is copied without
combining or paraphrasing it. Without the block WATERMARK reports **NOT GRADED** and
the command exits 2; a block copied from another artifact or run refuses. A later
trusted WATERMARK pass supersedes the status and refuses until the entire block is
deleted. An absent corpus does neither: it skips the gate and leaves the last status
alone. This is the **held declaration** for accepted distrust, under ADR 0019; it is
not a replacement for the stderr trace or the checkout-publication refusal from ADR
0010.

The section also carries one `span | pages | read` table per source. A one-source
sheet may omit the source label; each table in a multi-source sheet is preceded by a
`Source:` line naming the source key in backticks. Page ranges may overlap because a page is a locator rather
than a partition. Their union must account for every page in the catalog's independently
derived `page_count`, and the command prints the unaccounted remainder on every run,
including `none`.

The `read` cell is `no`, `yes` where the span contains a threshold row, or
`read YYYY-MM-DD` when a completed read found no row. A `references` span alone may
instead use `exempt: <reason>`. A positive span with neither a row cited inside its
range nor a dated marker is refused. The marker records that a read happened; it never establishes that
the read was careful. Page coverage likewise catches an omitted span, not a boundary
drawn on the wrong page.

### `## Populations`

The controlled vocabulary, and the answer to the one correction that reshaped this
format. Each key is declared once with the guideline's **own wording verbatim** beside
it.

**Two rows disagreeing is not a conflict unless they are about the same patient.**
KDIGO targets SBP `<120` in CKD and AHA/ACC targets `<130/80` in general adults; those
are two rows, not a contradiction, and a sheet that called them one would be inventing
a disagreement. So the conflict rule keys on **quantity and population together**. The
machine can only compare strings, which is why the key is drawn from a fixed list and
the verbatim text sits beside it — a mis-keyed row is a wrong *word* a reader can see,
rather than a silent miss.

### `## Quantities`

The controlled vocabulary for what each row measures. Each key is declared once with
the guideline's own wording verbatim beside it, and the grader refuses a threshold row
whose key is absent from this table.

**The method belongs in this key when the value depends on the method.** Cervical
cancer screening is the calibration case: cytology alone and hrHPV testing legitimately
carry different intervals for the same patients. Putting the method in `population`
would misdescribe the patient; giving both rows one quantity would call alternatives a
conflict. Method-specific quantity keys represent the recommendation without either
distortion. [ADR 0009](../../docs/adr/0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md).

### `## Thresholds`

Eight columns: `quantity | population | value | snippet | source | page | rec | class`.

- `value` uses **ASCII comparison operators only** — `<`, `>`, `<=`, `>=`. This is a
  rule about the corpus rather than about taste: two fonts in it render a comparison
  operator through a slot their own encoding does not describe, so a reader hands
  back a pound sign, a double dagger or a control code. A sheet holds the fact and
  must not hold the mis-encoding.

  Since [#172](https://github.com/mshamblin5150-code/clinical-skills/issues/172) the
  extractor repairs those slots at the point the font is still known, so the extracted
  text a sheet is transcribed from carries the operator the document prints. **The gate
  stays**, because a sheet may be transcribed from a PDF opened by any reader on any
  machine, and it now takes its list from `guidelines_extract.SYMBOL_FONT_OPERATORS`
  rather than holding a copy. Destructive C0 slots would be erased by Python before the value
  gate could see them, so `threshold_sheet.parse` refuses those from the raw sheet,
  preserves the sheet line, and directs an agent to verify the intended operator from
  the rendered PDF page before writing its ASCII form. It never guesses the operator.
- `snippet` is a short **verbatim** run from the source containing the value's number.
  It is not decoration; it is what makes the citation checkable on a machine that does
  not have the PDFs.
- `rec` is the `rec_id` from `guidelines_recs.py`, which is what ties a row to the
  recommendation it came from and lets the omission gate work. **The `class` column is
  checked against it**: a row carrying Class 1 while its recommendation is Class 2a is
  refused, and that is the only check here that catches a row pinned to the *wrong*
  recommendation — every other gate passes such a row, because its number is real and
  its snippet is on the page it names.
- A snippet may begin `RENDERED:` to declare that the value was **read off the page as
  typeset** because extraction garbles that table. Tier 2 then skips the row and the
  run prints how many rows did this. It is the escape hatch #83 asks for, modeled on
  `phi-scan: synthetic` and narrowed the same way: the marker must *start* the cell, so
  a row that merely mentions the hatch cannot claim it. Tier 1 still grades the row —
  the hatch buys out of the page check, not out of the sheet being self-consistent.

### `## Conflicts`

`CONFLICT: <quantity>` followed by prose naming every distinct row value and **why
they differ**. The grader requires one wherever two rows share a quantity and a
population with different values, and reads the prose to require a distinct mention of
every value. One longer value cannot donate its matching prefix to a shorter one.
Ordinary inequality wording is accepted (`below 180/105 mm Hg` names `<180/105 mm Hg`).
This is a floor, not a clinical reading: it catches an empty block, `TODO`, or one side
left unnamed, but cannot decide whether the explanation is correct.

Why prose rather than a column: the KDIGO/AHA case turns entirely on *why* — different
measurement method, different population — and a cell has no room for the only thing
that resolves it.

### `## Coverage`

Every recommendation in an exact source is either cited by a row or listed here as
`` - `<rec_id>` - <reason> ``. **Omission is the failure no other gate can see**:
everything else checks what was written, only this checks what was not.

## Coverage of the topic sweep

[`coverage.md`](coverage.md) is the denominator for this directory. It carries one row
for every distinct topic derived from
[`reference/guidelines-catalog.md`](../guidelines-catalog.md), with one of these states:

- `sheet`: the named sheet holds the topic's decision points;
- `none`: the source documents were read and state no decision point;
- `unread`: the sources have not been read completely enough to decide.

The optional `artifact` column names a shipped sheet. It can accompany `unread` when
the sheet contains verified decision points but the full-document read is incomplete;
that artifact does not promote the topic to `sheet` or make its omissions meaningful.

Run `python tools/threshold_coverage.py` from the repository root to re-derive the topic
and state counts and to refuse missing, duplicate, or orphaned rows and artifacts.
`--draft` prints the catalog-derived topic column. An `unread` row is not a clinical finding, and a
`none` row does not change the rule inside a sheet: a missing threshold row still means
`sheet does not settle it`.

The registry also binds state to the artifact's page arithmetic in both directions. A
`sheet` row refuses while any declared span remains unread. A non-`sheet` row refuses
when the artifact's completed or exempt spans cover every catalog page. This prevents a
completed artifact from remaining stranded under `unread` as well as preventing an
incomplete artifact from being promoted.

## What the sources being absent means

Citation resolution needs the source PDFs. In a fresh clone, in another worktree,
and in CI it has nothing to resolve. So the gate is **three tiers**:

| tier | needs | checks | runs |
| --- | --- | --- | --- |
| 0 | `recs-<key>.json` | the snippet is in its own recommendation record | exact sources; `NOT RUN` on bound sources |
| 1 | nothing | the value's number is in the row's own snippet | everywhere |
| 2 | the PDFs | the snippet is on the page it cites | where the corpus is |

There is no machine on which citation checking drops to zero, and tier 2 skipping
prints a banner it is meant to be hard to read past. **A test that goes green because
its input vanished is worse than no test** — that is the same hole `tools/phi_scan.py`'s
corpus layer documents, and [#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93)
is the dated occasion it fired for real.

## The holes, written down the same day the gates were built

A machine gate does not fail, it goes silent. The risk is that the ungated majority
starts reading as covered because the gated part is green, so these are named here and
not left to be discovered:

- **No gate here checks that a row says what its recommendation says.** Tier 0 proves
  an exact recommendation record states the snippet, and tier 2 proves the snippet is
  on the page. Nothing proves the row's `quantity` is what that sentence
  was about, and **a sheet whose numbers are all real and all filed under the wrong
  heading passes every gate in this directory.**
- **The population key is a judgment.** The grader checks it is declared, never that it
  is right. A mis-keyed row hides a real conflict by making two rows look like
  different patients.
- **On a machine without the recommendation records, COVERAGE skips loudly and the
  hook does not refuse the edit.** `--all` resolves `recs-<source key>.json` under
  `--recs-root`, which defaults outside the repo and is **not committed**, because it
  holds the society's recommendation text in full. When a record was never built,
  `grade` prints `COVERAGE NOT RUN` even through `--quiet`, calls the result a warning
  rather than a clean COVERAGE pass, and exits 0 unless another gate refuses. An
  explicit `--recs` path that does not resolve or a record that exists but is unreadable
  still exits 2; a present record that exposes an exact-source omission still exits 1.

  This is [#181](https://github.com/mshamblin5150-code/clinical-skills/issues/181)'s
  ruling. Omission remains the one failure no other gate in this directory can see,
  but refusing every sheet edit on a fresh clone made an uncommitted build artifact a
  prerequisite even for a prose typo fix. The visible degradation preserves that
  distinction without teaching committers to bypass the whole hook. The directory
  `README.md` is not a sheet and does not trigger the grader.
- **A scope-out reason is required and cannot be graded.** `out: not relevant` passes.
- **A `bound` source is warned about and never refused.** `tools/guidelines_recs.py
  --json` reports which mode a document yields, and that is the number to look at
  before trusting a clean run. **This bullet used to close *so most of the corpus can
  only ever be warned about*, and #173 made that false without touching the sentence**
  — the majority of the corpus is `exact` now. The standing figure is the table below
  and is deliberately not restated here.
- **The topic sweep is recorded rather than summarized by a hand-maintained count.**
  [`coverage.md`](coverage.md) names every catalog topic and distinguishes a completed
  sheet, a completed read with no decision point, and an unread source. Its separate
  artifact column can name partial work without changing that state. Run
  `python tools/threshold_coverage.py` to re-derive the counts. An `unread` row is not
  a negative finding about a guideline.
- **Most of the corpus can be gated now, and the number is measured.**
  `tools/guidelines_recs.py` was run over all 179 documents on 2026-08-19, after
  [#173](https://github.com/mshamblin5150-code/clinical-skills/issues/173) added the
  two readings it was filed for. The bound limb was re-derived on 2026-08-28 after
  #446 moved its marker pages onto the repaired reader:

  | mode | `counted_from` | docs | recommendations | what a gate can do |
  | --- | --- | ---: | ---: | --- |
  | `exact` | `ruled-table` | **22** | 2,969 | omissions **refused**; 22 of 23 AHA/ACC files |
  | `exact` | `curated-table` | **90** | 143 | omissions **refused**; every USPSTF document |
  | `bound` | `text-marker` | 48 | 4,619 | omissions **warned**; 30 IDSA, 16 KDIGO, 1 ADA, 1 GOLD |
  | nothing found | — | **19** | 0 | nothing counted, so nothing gated |

  `python tools/guidelines_recs.py <corpus-root> --compare-readers` reports each
  document whose raw and repaired marker records differ, then derives the exposed
  document count. The set is not copied into this file.

  **It read 22 / 19 / 138 on 2026-08-16 and that is what #173 was filed over.** The
  138 was 90 USPSTF plus 39 IDSA plus 9 others — two house styles, not a scatter —
  and both were closed: USPSTF from the committed
  [`reference/guidelines-uspstf.md`](../guidelines-uspstf.md), IDSA by matching the
  GRADE parenthetical it writes in prose.

  **The 143 being small beside the 2,969 is the artifact and not a defect.** A USPSTF
  recommendation statement states one to four recommendations; an AHA/ACC guideline
  states a hundred.

  **The 19 left is still a limit of this extractor, not a finding about those
  guidelines** — 11 IDSA documents that state no graded recommendation in either form
  this reads, 3 ACIP print captures, 2 KDIGO, and one each of AHA/ACC, CDC and GINA.
  `guidelines_recs.py` exits 2 on them and says so in as many words rather than
  reporting a zero. **A sheet built on any of the 19 would have its omission gate
  silently do nothing**, which is why the mode is recorded per source and cross-checked
  rather than trusted.

  **One document moved from *nothing* to a bound of one and that is worth knowing
  before reading it as coverage.** The GOLD report states a single recommendation in
  GRADE terms in running prose, so the IDSA marker finds exactly one in a document
  holding hundreds. That is a true statement about markers and a poor description of
  the document; it is a bound, a bound may only warn, and no threshold on the number
  would be anything but invented.
- **Gate 4 refuses until a working agent checks the rendered page.** The clinician
  ruled the posture on
  [#296](https://github.com/mshamblin5150-code/clinical-skills/issues/296): routine
  visual confirmation belongs to a vision-capable agent rather than becoming a
  clinician bottleneck. The agent renders the cited page and confirms that the row's
  label and value belong together. If they do, the agent records the check with
  `RENDERED:`; if they do not, or the page is ambiguous, the row remains refusing
  until corrected. The marker also exempts the row from citation tier 2, so it is an
  audit claim that the rendered page was actually inspected, not a way to silence the
  gate without doing the read.
- **Gate 4, watermark interleave, is built on
  [#174](https://github.com/mshamblin5150-code/clinical-skills/issues/174), and what it
  cannot reach is the half the exposure figure is about.** It flags a row that
  *carries* a stripped string. It says nothing about the other direction — a stripped
  line sitting *between* a row's label and its number, removed cleanly, leaving two
  halves welded that were never adjacent on the page. Tier 2 catches that one where the
  PDFs are present, because a snippet spanning a removal is not on the raw page; on a
  machine without them nothing catches it. **The exposure figure is what makes that
  worth knowing**: boilerplate stripping went from 554,372 characters to **921,093**
  under #83's reader, across 167 of 179 documents, and **#100 widened it again** by
  42,272 characters and 2,688 lines across a further 27 documents, for 963,365 together
  — **9,277 of which is
  [#178](https://github.com/mshamblin5150-code/clinical-skills/issues/178)**, which
  fixed the KDIGO transplant footer's spacing and so let the margin rule see a running
  head it had never been able to match.
- **Gate 4's input is two fields, and it reads both.** #83 says the manifest "records
  the exact strings stripped per document, so this is a comparison against a recorded
  list". The list is split: `boilerplate` holds what the literal rule took and
  `margin_stripped` holds what #100's margin rule took. A detector reading only
  `boilerplate` misses 2,688 lines across 27 documents and reports a clean gate. The
  three documents that matter most lose a **welded running head** rather than a folio —
  `GOLD/GOLD-REPORT-2026`, `IDSA/ciw670` and, since #178,
  `KDIGO/KDIGO-2009-Transplant-Recipient-Guideline-English` — and prose is what
  interleaves.
- **Not every stripped string is a probe, and 11 of the 179 documents have none.** A
  string the extractor strips in one place and keeps in another proves nothing by
  appearing in a snippet, so a probe has to be absent from the document's own extracted
  body — a running head that the body also states is the worked case, and
  `threshold_sheet.usable_probes` names it with its counts. **A sheet citing one of the
  11 is a sheet gate 4 said nothing about**, and the command names those sources rather
  than printing a zero. Measured 2026-08-19 against a corpus outside this repo, so
  nothing committed re-derives it — which is why the figure is stated here and in no
  other file. **Re-derive it with the gate's own predicate**, not by reading the
  manifest: the manifest records the stripped strings, and what makes one a probe is
  the body test `usable_probes` applies to it.

  ```bash
  python -c "import sys, json, pathlib; sys.path.insert(0, 'tools'); \
    import threshold_sheet as g; \
    r = pathlib.Path('C:/codeing/guidelines-text'); \
    d = json.loads((r / 'manifest.json').read_text(encoding='utf-8'))['documents']; \
    print(sum(not g.usable_probes(e, (r / e['output']).read_text(encoding='utf-8', errors='replace')) for e in d), 'of', len(d))"
  ```
- **Gate 5, the second independent read, is built and it is half a mechanism by
  design.** #83 describes it as the only thing that catches *misreading* rather than
  *miscitation*, and says in the same breath that its weakness is correlated error —
  same model, same PDF, same mangling, same wrong answer — so it *"must be documented
  as a strong smoke test, never as proof."* **Correlated error weakens the pass and not
  the fail**, which is why a disagreement refuses while a clean run prints the
  smoke-test line every time. What the command cannot do is perform the read: there is
  no code path in `threshold_sheet.py` that produces a `--second-read` record, because
  one it produced would be the same code over the same page — the check that module's
  docstring calls worthless by name.
- **A second read is bound to one declared span.** A reader miss where the sheet has
  a row warns; a value found where the sheet retired the span as null refuses. The
  required `briefed` block makes a null read for one span distinguishable from every
  other null read and from a record produced without opening anything.
- **Gate 1's "different path" is different-function, not different-library, and #174
  settled that it does not need to be.** #83 asks that the citation gate *"pulls that
  page's text through a different path than the writer used"*. The writer reads
  `find_tables()`; tier 2 reads `get_text()`. Those are genuinely different code paths
  over different structures, and they did catch a planted defect. But both are PyMuPDF,
  so **a mis-extraction at the library level is invisible to tier 2** — it would corrupt
  the snippet and the page identically. **A second library would not help**, which
  [#172](https://github.com/mshamblin5150-code/clinical-skills/issues/172) measured
  rather than argued: the mis-encoding it is about is *in the PDF*, and `pypdf` and
  PyMuPDF return byte-for-byte identical wrong output on the same file. What settles
  that class is **rendering the page**, at a stated resolution — 400 dpi produced a
  confident wrong answer that only 700 dpi corrected
  ([#282](https://github.com/mshamblin5150-code/clinical-skills/issues/282)). So the
  hole stands, and the instrument that closes it is not a reader.
- **COVERAGE read one recommendation record per sheet until
  [#177](https://github.com/mshamblin5150-code/clinical-skills/issues/177).** A sheet
  citing two societies got omission checked against whichever record `--recs` named and
  silently not against the other, and the count that would have surfaced it was derived
  from *was there a record at all*, so it could not exceed 1 however many sources went
  unchecked. It is per source now — `known` filtered to the rows citing that source, the
  mode cross-check and the class check reading each source's own record, a real count of
  the sources with no record, and exit 2 where **any** of them lacks one. **Fixed on 2026-08-19, while
  one sheet with one source existed, which is the only reason it had cost nothing**:
  #83 decision 3 makes multi-source the normal case.
- **What that fix newly makes possible is a record bound to the wrong source**, because
  the lookup is keyed on a source key that is *sheet-local* — two sheets using `aha` for
  different guidelines resolve one `recs-aha.json`. The record names the PDF it was
  built from and the Sources table names the same file, so a mismatch is **refused**;
  the comparison is on the filename alone, since where the corpus was mounted when the
  record was built is not a finding. A record carrying no `source` field claims nothing.
