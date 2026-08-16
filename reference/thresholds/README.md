# Threshold sheets

The deliverable of the [#80](https://github.com/mshamblin5150-code/clinical-skills/issues/80)
series, in the shape [#83](https://github.com/mshamblin5150-code/clinical-skills/issues/83)
settled. Per topic, **the decision points only** — drug, dose, duration, target number,
referral and follow-up threshold, staging cutoff. Not full text.

That shape is deliberate and it is what makes the series shippable. **Facts are not
copyrightable; expression is.** A restated staging table is a fact this repo may hold
freely. A dumped guideline PDF is the copyrighted expression, and it also happens to be
410 MB. The distilled form is both the legally clean artifact and the only one small
enough to commit.

The 179 source PDFs stay outside this repo at `C:/codeing/guidelines-src`
([#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87)). Nothing a
consumer runs needs them — they need the derived facts.

## Grading a sheet

```bash
# Build the recommendation record first, OUTSIDE the repo -- always. It holds the
# society's recommendation text in full, which is the copyrighted expression this
# whole format exists to avoid committing, and guidelines_recs.py refuses to write
# it inside any git checkout.
python tools/guidelines_recs.py \
    "C:/codeing/guidelines-src/AHA ACC/jones-et-al-2025-....pdf" \
    --doc-id "AHA ACC/jones-et-al-2025" \
    --json C:/codeing/guidelines-index/recs-hypertension.json

python tools/threshold_sheet.py reference/thresholds/hypertension.md \
    --recs C:/codeing/guidelines-index/recs-hypertension.json

# --all resolves recs-<sheet stem>.json from --recs-root, which defaults outside the
# repo for the same reason. A sheet whose record it cannot find exits 2, never 0.
python tools/threshold_sheet.py --all
```

Four gates. What each one can see, and what it cannot, is written out in full in
`tools/threshold_sheet.py`'s docstring rather than summarized here, on
`icd10_lookup.py`'s terms: a rule is cheapest to keep true where the code that enforces
it lives. What belongs here is the part a reader of the *sheets* needs.

## The file format

A sheet is Markdown, and every part of it is read by the grader. The
`<!-- schema: threshold-sheet/1 -->` marker is what says so; a file without it is
reported as **not graded** rather than as clean.

### `## Sources`

One row per document, with the key each threshold row cites, the society, the
document's `doc_id` (which is its path under the corpus root, no suffix), the version,
the publication date, the URL, and the **mode**.

**Mode is not a style choice and is not set by hand.** It comes from
`tools/guidelines_recs.py`, and it says whether that document's recommendations could
be counted *exactly* — read out of a ruled `COR | LOE` table — or only *bounded* by
matching a marker in running text. An exact source has its omissions **refused**; a
bound source has them **warned**. See #83 decision 1.

### `## Scope`

The sections-read line, and it is load-bearing rather than courteous. **A synthesis
pass is a reading and readings miss things.** If only the recommendation tables were
read, the sheet says so, so that *absent from the sheet* is never misread as *absent
from the guideline*.

It also carries `citations resolved against <corpus> on <date>`. That is the artifact's
own record of when the citation gate last ran against real PDFs — see below.

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

### `## Thresholds`

Eight columns: `quantity | population | value | snippet | source | page | rec | class`.

- `value` uses **ASCII comparison operators only** — `<`, `>`, `<=`, `>=`. This is a
  rule about the corpus rather than about taste: KDIGO's tables render the
  less-or-equal sign through a Symbol-font slot that extracts as a pound sign, **73
  times across the 179 documents**, measured 2026-08-16. A sheet holds the fact and
  must not hold the mis-encoding.
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

`CONFLICT: <quantity>` followed by prose naming every society, its number, and **why
they differ**. The grader requires one wherever two rows share a quantity and a
population with different values — so the honesty is structural rather than remembered,
the same move as `differential_scan.py`'s welded `NOT CODED` pair.

Why prose rather than a column: the KDIGO/AHA case turns entirely on *why* — different
measurement method, different population — and a cell has no room for the only thing
that resolves it.

### `## Coverage`

Every recommendation in an exact source is either cited by a row or listed here as
`` - `<rec_id>` - <reason> ``. **Omission is the failure no other gate can see**:
everything else checks what was written, only this checks what was not.

## What the sources being absent means

Citation resolution needs the 410 MB of PDFs. In a fresh clone, in another worktree,
and in CI it has nothing to resolve. So the gate is **two tiers**:

| tier | needs | checks | runs |
| --- | --- | --- | --- |
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

- **No gate here checks that a row says what its recommendation says.** Tier 2 proves
  the snippet is on the page. Nothing proves the row's `quantity` is what that sentence
  was about, and **a sheet whose numbers are all real and all filed under the wrong
  heading passes every gate in this directory.**
- **The population key is a judgment.** The grader checks it is declared, never that it
  is right. A mis-keyed row hides a real conflict by making two rows look like
  different patients.
- **On a machine without the recommendation records, the hook refuses every edit to a
  sheet — including a prose typo fix.** `--all` resolves `recs-<stem>.json` under
  `--recs-root`, which defaults outside the repo and is **not committed**, because it
  holds the society's recommendation text in full. Absent, COVERAGE cannot run, `grade`
  returns 2, and `tools/hooks/pre-commit` turns any non-zero into a refusal. So a fresh
  clone, a new worktree and CI can all stage a sheet and be told no, with the recovery
  being to rebuild the record with `tools/guidelines_recs.py` as shown at the top of
  this file, or `--no-verify`.

  **This is deliberate and it is the opposite of what tier 2 does two bullets down**,
  which skips loudly and passes. The asymmetry is the point: tier 2 not running leaves
  every value still checked against its own snippet, whereas COVERAGE not running
  leaves **omission** unchecked, and omission is the one failure no other gate in this
  directory can see. A sheet that cannot be checked for what it left out is not a sheet
  anyone should be able to commit by accident. **Named here rather than smoothed over**,
  because the cost lands on someone editing prose who has done nothing wrong.
- **A scope-out reason is required and cannot be graded.** `out: not relevant` passes.
- **A `bound` source is warned about and never refused**, so most of the corpus can
  only ever be warned about. `tools/guidelines_recs.py --json` reports which mode a
  document yields, and that is the number to look at before trusting a clean run.
- **One topic has a sheet.** Everything else in the 179-document corpus is reachable
  through `tools/guidelines_search.py` and has not been distilled. An empty directory
  entry is not a negative finding about a guideline.
- **Most of the corpus cannot be gated at all yet, and the number is measured.**
  `tools/guidelines_recs.py` was run over all 179 documents on 2026-08-16:

  | mode | docs | what a gate can do |
  | --- | ---: | --- |
  | `exact` | **22** | omissions **refused**; 22 of 23 AHA/ACC files, 2,969 recommendations |
  | `bound` | 19 | omissions **warned**; 16 KDIGO, 2 IDSA, 1 ADA |
  | nothing found | **138** | nothing counted, so nothing gated |

  **The 138 is a limit of this extractor, not a finding about those guidelines.** It
  knows two house styles — a ruled `COR | LOE` table and a `Recommendation N.N.N` /
  `Practice Point` marker. USPSTF grades recommendations with a letter (A/B/C/D/I) and
  IDSA writes *"strong recommendation, moderate-quality evidence"* in prose; neither is
  matched. `guidelines_recs.py` exits 2 on those and says so in as many words rather
  than reporting a zero, and all 90 USPSTF documents are separately covered by
  `reference/guidelines-uspstf.md`. **A sheet built on any of the 138 would have its
  omission gate silently do nothing**, which is why the mode is recorded per source and
  cross-checked rather than trusted.
- **Gate 4, watermark interleave, was not built.** #83 describes it: *"If a string
  stripped by #80 appears inside an extracted table row, that row is suspect and must
  be read off the rendered page."* **This ticket widened the exposure rather than
  narrowing it** — boilerplate stripping went from 554,372 characters to 921,168 under
  the new reader, so there is more stripped text that could have been interleaved, not
  less. The `RENDERED:` marker gives a row a way to *declare* it was read off the page;
  nothing yet *detects* that it should have been.
- **Gate 5, the second independent read, was not built.** #83 describes it as the only
  mechanism that catches *misreading* rather than *miscitation*, and says in the same
  breath that its weakness is correlated error — same model, same PDF, same mangling,
  same wrong answer — so it *"must be documented as a strong smoke test, never as
  proof."* Not built here; recorded so that the absence is visible rather than
  inferred.
- **Gate 1's "different path" is different-function, not different-library.** #83 asks
  that the citation gate *"pulls that page's text through a different path than the
  writer used"*. The writer reads `find_tables()`; tier 2 reads `get_text()`. Those are
  genuinely different code paths over different structures, and they did catch a
  planted defect. But both are PyMuPDF, so **a mis-extraction at the library level is
  invisible to tier 2** — it would corrupt the snippet and the page identically.
- **COVERAGE reads one recommendation record per sheet.** A sheet citing two societies
  gets omission checked against whichever record `--recs` names and silently not
  against the other. The one sheet that exists has one source; a second source is the
  point at which this has to change, and the count printed as "source(s) had no
  recommendation record" cannot currently exceed 1.
