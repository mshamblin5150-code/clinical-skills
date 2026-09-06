# The guideline currency check is per society reads what its publisher lists and refuses to repoint a sheet

Ruled by the clinician on 2026-09-05, in the grilling of
[#767](https://github.com/mshamblin5150-code/clinical-skills/issues/767). Freshness gate `FRESH` at
both checkpoints; `main` moved once mid-session and the branch was brought forward before anything
was written. Nothing is built here; this is the record the build reads.

**The subject.** The corpus drift check watches the local PDF folder. Nothing watches the society
that published the guideline, so a threshold sheet can go on citing a page in a document its society
has retired while every gate in the tree reports `ok`.

## Measured before ruling, at `6540759`

**Every corpus document already carries a committed web address, and no row records a fetch.** The
`## Sources` table of the 169 sheets under `reference/thresholds/` holds 181 rows over **180 distinct
documents** — full coverage — with the schema
`key | society | document | source class | version | published | url | basis | mode`. The `url`
column splits **159 `doi.org` / 22 other**. The `basis` column reads **159 `stated`, 22 `chosen`**
and **zero `digest` or `gated`**, so the two dated network bases the format declares have never been
used by anything.

**Only 15 of those 22 are per-topic landing pages** — KDIGO 4, USPSTF 5, ACIP 4, IDSA 1, ACOG 1, and
**zero AHA/ACC**. The other seven are a reports index, two per-edition pages, a journal issue, a
direct PDF, a bare host, and a permanent article identifier on a non-`doi.org` host.

**The corpus is lopsided and it is already old.** USPSTF 90, IDSA 42, AHA/ACC 23, KDIGO 18, ACIP 3,
and ADA, CDC, GINA and GOLD one each. **Seventy of 180 documents are over five years old**, IDSA
worst at 20 of 42. Five carry no year. The catalog's `citation` column holds **163 bare DOIs**, 4
URLs, 6 journal citation lines and 7 unsettled `?`.

**Two live instances, and their shapes differ.** `reference/thresholds/blood-cholesterol.md` sources
the 2018 AHA/ACC blood cholesterol guideline; the corpus **also holds** the 2026 dyslipidemia
guideline whose own abstract says it *"retires and replaces"* it, distilled into its own sheet. Both
coverage rows read `sheet`. That instance needs no network at all.
`reference/thresholds/lipid-management-in-chronic-kidney-disease.md` sources the 2013 KDIGO lipids
guideline, and `https://kdigo.org/guidelines/lipids-in-ckd/` — already committed as that sheet's
`url` cell — states *"Updated KDIGO guidance on lipid management in CKD is incorporated into the
KDIGO 2024 CKD Guideline."* That one needed the network, and its supersession target is a document
filed under a **different topic**.

**The existing supersession mechanism cannot see either.** `uspstf_table.mark_superseded` compares
corpus to corpus within one society's topic cells, so it fires only after somebody has already
downloaded the replacement.

**The no-socket premise is narrower than the tree, and this was already on the ticket.**
`tools/tracker_freshness.py` and `tools/tracker_publish_hook.py` run `git fetch` and `gh issue view`
from committed modules. What the policy actually holds is that no committed **scanner** fetches a
**content** source.

**Reachability was measured from a shell, not reasoned about, and the first reading was wrong.** A
sub-agent's fetch tool returned HTTP 403 on eight `kdigo.org` requests including a static PDF, and
the session published `UNKNOWN` for KDIGO on that basis. Plain `curl` with the default user-agent
returns **200 and 84 KB** for the same URL. The 403 was an artifact of the instrument.

**Nine of nine societies are reachable, and three of the routes are the clinician's own.**

```
KDIGO      kdigo.org/guidelines/                              200 plain    18 topic pages; supersession in prose
ADA        professional.diabetes.org/standards-of-care        200 plain    current-edition dc26- DOIs in served HTML
GOLD       goldcopd.org -> Reports & Pocket Guides            200 plain    WordPress; must navigate, not guess
AHA/ACC    professional.heart.org/en/guidelines-statements-   403 -> 200   Coveo; guidelinepublishdate and
           search                                             (Chrome UA)  guidelinecategory are real fields
USPSTF     uspstf/topic_search_results?topic_status=P         200 plain    108 current, 22 inactive
IDSA       idsociety.org/.../alphabetical-guidelines/         302 -> 200   Current / Archived / Endorsed labels
GINA       ginasthma.org wp-json, sitemap, feed               200 plain    archived-reports page
ACIP       cdc.gov/vaccines/imz-schedules/*                   200 plain    date on page, no archive link
CDC        cdc.gov/mmwr/indrr_<year>.html                     200 plain    per-edition index, 1990-2025
```

**The Cloudflare wall is two publisher hosts the clinician never used** — `ahajournals.org` and
`diabetesjournals.org`. Headless Chrome with a fresh profile does **not** clear it: the render
returns *"Just a moment… performing security verification"*.

**A 200 over an empty page is the dangerous failure and it is in this set.** `ahajournals.org` with
a Chrome user-agent returns **200 with navigation chrome and no article text**, and
`idsociety.org/practice-guideline/practice-guidelines/` is a JavaScript *"Loading…"* shell with zero
guidelines in its HTML. Both read to a naive checker as a successful read that found no retirement
notice.

**Crossref carries no structured supersession for this corpus.** Measured directly on AHA
(`10.1161/CIR.0000000000000625` — `relation` empty, `updated-by` holding two **corrections**),
JAMA (`10.1001/jama.2019.18928`) and Wiley (`10.1111/j.1600-6143.2009.02834.x`). The 2026
guideline that retires the 2018 one carries no relation at all and states the supersession only as
free text. Crossref also cannot enumerate guidelines — every item is `type: journal-article`, so
editorials and conference abstracts sit indistinguishable from guidelines — and one of two AHA DOIs
checked disagreed with the catalog year.

**Three societies publish on a measured cadence and six do not.** ADA lands `10.2337/dcYY-srev`
every December, verified across `dc23`, `dc24`, `dc25` and `dc26`. GOLD and GINA are annual; GOLD's
2026 report published 2025-12-08. USPSTF, IDSA, AHA/ACC and KDIGO publish continuously.

**`goldcopd.org/gold-reports/` serves the 2020 report with no banner and no link to 2026.** The most
guessable canonical URL hands a six-year-old edition to a reader as though it were current.

**Where a signal could land.** `threshold_coverage.STATES` is
`("sheet", "none", "non-source", "unread")` and the registry currently holds **166 `sheet`, 2
`none`, 1 `non-source`, 0 `unread`**. `reference/guidelines-catalog-audit.md` holds three tables —
`## Documents` (180 rows, `society | filename | sha256 | bytes | audited`), `## Independent readings`
(900) and `## Clinician rulings` (323) — and `guidelines_catalog.py`, which owns and grades that
file, opens no socket. No `last-checked-upstream` column exists anywhere.

## Ruled 2026-09-05

### 1. The question is whether a newer edition exists, and an unchecked document says so

Not *did this document's bytes change* — for 159 of 180 the address is a permanent article
identifier that answers *no* forever, including after the society has replaced the guideline, so
that check reports clean on the exact scenario the ticket was filed over. The claim is
**edition currency**, and *never checked* is a state the tree carries rather than an absence it
implies.

### 2. The read is per society and joins back to our documents

One read of what a society currently publishes, joined to the catalog, rather than one lookup per
document. It is one fetch instead of ninety; it authors no addresses, where the per-document route
would need roughly 85 USPSTF slugs typed by hand because the corpus filenames are download names;
and it covers AHA/ACC, which has **no per-topic page at all** and therefore cannot be covered the
other way. It answers in both directions — a document of ours absent from their current set, and a
guideline in their current set the corpus does not hold, which nothing here can currently see.

**The join key is per society and never universal.** DOI for USPSTF, IDSA, AHA/ACC and KDIGO; the
year slug for GINA and GOLD, which are not Crossref members and have no DOI; the `dcYY-srev` pattern
for ADA; the printed schedule date for ACIP. A society publishing no index at all takes a named
per-document exception list rather than a second general mechanism.

### 3. The record is a new registry with its own grader

`reference/guidelines-currency.md`, holding both keys — one row per society with where to look and
how, and one row per document with the verdict — bound to the catalog on `filename` and graded in
**both** directions, so a document with no currency row and a currency row naming no document each
fail.

**The deciding reason is the no-socket boundary rather than the shape.** `guidelines_catalog.py`
owns `reference/guidelines-catalog-audit.md` and opens no socket. Network-sourced rows in a file
that offline grader audits leave it two bad options: ignore them, which is a silent hole in its own
file, or grade what it cannot verify. Supporting reasons: `CONTEXT.md` defines the **Audit ledger**
as being about file identity, *"the only place the tree states which exact bytes a reading rests
on,"* and an upstream check says nothing about our bytes; the ticket calls this mechanism #439's
mirror, and a mirror is a second artifact rather than a column; and no existing table is keyed for
the society-level half.

[ADR 0102](0102-a-clinical-subject-is-authored-per-registry-row-and-a-reworded-catalog-cell-loses-it.md)'s
refusal of *a fourth hand-kept list bound to the catalog by nothing* is answered the way
[#689](https://github.com/mshamblin5150-code/clinical-skills/issues/689) answered it: bind it on the
catalog's own key and grade the bind.

### 4. A stale guideline never refuses a commit; the registry's own integrity does

The grader refuses a corpus document with no currency row, a currency row naming no document, a
malformed row and an unruled verdict — all offline, at the pre-commit hook. It never refuses because
a guideline is stale.

**Refusing on a `superseded` verdict was available and is declined.** The verdict is a committed row,
so no network is needed to read it, which is why this needed a ruling rather than being ruled out by
mechanism. Resolving one is days of work — download, rebuild, re-read, re-audit — and gating an
unrelated typo fix behind that is how a refuser gets routed around. This grader refuses only what the
committer created in that commit and can fix in that commit, which is the property that makes
`threshold_coverage.py` and `subject_ledger.py` safe.

### 5. The threshold-sheet grader reports the verdict and the sheet stores no copy

`threshold_sheet.py` looks each `## Sources` row's document up in the currency registry and prints
the verdict beside it. It reports; it does not refuse.

**`CONTEXT.md` already argues for this placement.** The `source class` cell exists on that exact row
because *"a number read out of a public review draft is not guidance in force and a year alone does
not say so,"* and the glossary's definition of **Source class** ends: *"It says nothing about whether
a guideline is current or superseded."*

**A `coverage.md` state is the wrong instrument and the glossary says why.** **Sweep state** describes
*"the read behind a sheet and never whether a run may open one,"* and **Shipped artifact** is *"what a
run joins on and may consult, whatever the row's sweep state"* — so moving that row would record the
fact in the one column ruled not to carry it. And a copied cell on 169 curated sheets is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143): the registry is what
re-derives it.

### 6. Consume reaches the corpus and stops before the sheet

The mechanism offers to download the replacement and rebuild — fetch into the corpus root, then
`guidelines_build.py`, `guidelines_catalog.py`, the audit ledger's digest row, `threshold_coverage.py`
— and the affected topic's `coverage.md` row moves to **`unread`** with a record naming the
superseding document. **It refuses to repoint any sheet's `## Sources` row.**

**Re-sourcing without re-reading is the worst artifact this repository can produce.** A sheet whose
rows were distilled from the 2018 guideline while its source row names the 2026 one is a fabricated
citation, and every citation gate would pass it, because the pages and the snippets are real. The
full re-read is a clinical read and stays one.

**Stage 2 is not optional.** Without it the new PDF sits unindexed and `--check-corpus-size` fires on
an unexplained arrival — the local detector reporting a mystery instead of a completed handoff.

**`unread` is the right landing and is not a reversal of ruling 5.** That ruling places the
*superseded* fact; this places a different fact, *the read behind this sheet is now owed*, which is
what `Sweep state` is defined to carry. **Shipped artifact** already provides the shape: *"an artifact
on an `unread` row is a real sheet whose full-document read is pending."* The state the
[#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429) sweep drained to zero is the
one this refills, one row at a time, on purpose.

### 7. A committed command performs the index reads it can and every download

The agent supplies the judgment — which of our documents a newer guideline supersedes — and the index
read for societies the command cannot read. The command does the rest.

**This moves the no-socket policy for content, and that move is this record.** Two reasons carry it.
The **digest**: the sheet format already declares a `digest YYYY-MM-DD` basis with zero instances
because nothing here can fetch, and a subagent reporting *"this is the 2026 KDIGO guideline"* is a
claim, while a command recording the SHA-256 of the bytes it received is evidence the next audit
either matches or does not. The **denominator**: the report must say *read seven of nine, two unread*
rather than reporting clean over what it reached, and that is only enforceable when the reading is in
code.

**Each index reader is a matcher and the extractor-coverage rule binds it.** Every reader states its
denominator and its unread remainder, and none may turn a partial read into a clean whole.
`guidelines_recs.py`'s `exact`/`bound` split is the precedent for declaring per society what could
actually be read.

**A 200 over a page with no content is a failure, never a pass.** Two are in this set today, and both
would otherwise read as *looked, found no retirement notice*.

### 8. Four verdicts, an observation date, and a separate society state

`current`, `superseded` — which **names the superseding document**, and may name one filed under a
different catalog topic — `absent`, and `unjoinable`.

**`superseded` and `absent` do not collapse.** Collapsing upward claims a replacement nobody
identified, which is fabrication; collapsing downward loses that the society has taken the document
off its list. They carry different obligations: `superseded` offers ruling 6's fetch, `absent` sends a
person to look.

**Never checked is an absent date, not a fifth word.** A row with no observation date has never been
looked at. That carries the ticket's *a date that reads as a guarantee* warning in a field that
cannot be forgotten.

**A society that could not be read is a dated society-level state, never a per-document verdict, and
never a permanent one.** Its documents keep the verdict and date they last earned. Writing
`unreachable` into the tree as a settled property is the error this session made and had to withdraw.

### 9. Reachability is measured from a shell before it is written down

The `UNKNOWN` this session published for KDIGO came from one instrument's 403 and was false. A
reachability claim is re-derived with a plain fetch, and a fetch tool's refusal is a fact about the
tool until a second instrument agrees.

**The three routes the clinician supplied are recorded as supplied rather than discovered**, which is
stronger provenance and is what settles the GOLD trap: `goldcopd.org/gold-reports/` serves the 2020
report as though it were current, so the address is his rather than guessed.

### 10. A re-read window exists only where the cadence is measured

ADA, GINA and GOLD publish annually — measured, not chosen — so an observation older than their last
publication cycle is a finding. USPSTF, IDSA, AHA/ACC and KDIGO get **no window**, because inventing
one for a continuously-publishing society is
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s objection exactly. Their
rows carry a date and the report states its age.

**The trigger is the advisory line that already runs.** `tools/hooks/pre-commit` calls
`guidelines_catalog.py --check-corpus-size` on every commit; it also prints the oldest currency
observation date and the count of never-checked documents, and nothing more. That is
`name_index.py`'s arrangement: state the shortfall, name the remedy, write nothing, refuse nothing.

## What this record does not settle

**The registry's exact columns**, beyond the two keys, the four verdicts, the observation date and the
society state.

**Whether the AHA/ACC Coveo endpoint can be read without a browser.** Its fields are real and in the
served HTML; the results need a runtime token handshake, and whether a command can complete one was
not measured.

**Whether the clinician's signed-in Chrome is ever authorized for guideline publishers.** It was held
as an escape hatch and never needed, because his own routes reach every society. ADR 0132 ruling 10's
authorization names `uptodate.com` and is not stretched here.

**What `absent` obliges.** It sends a person to look; what they are asked to do is not ruled.

**Whether a guideline in a society's current set that the corpus does not hold is ever fetched.** The
read surfaces it; nothing here says it is acquired.
