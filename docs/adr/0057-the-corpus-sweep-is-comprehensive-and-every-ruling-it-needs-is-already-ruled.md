# The corpus sweep is comprehensive, and every ruling it needs is already ruled

[#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429) asked how the
169-topic threshold-sheet sweep runs. [ADR 0009](0009-a-topic-is-swept-on-what-the-guideline-states-and-the-sweep-records-its-own-coverage.md)
answered its three original decisions on 2026-08-22 and declared the frontier empty. The
ticket then took 27 sweep comments in five days, and **not one of them closed a decision —
every one added a dependency or falsified a claim in the body.** Grilled again on
2026-08-27 against `origin/main` at `851d3d4`. Ten rulings, all the clinician's, all on
the same day.

The finding that shaped the session is that **#429 is not blocked on a decision anywhere.**
It is blocked on the builds of decisions already ruled. Measured at `851d3d4`:

```
grep -n "narrative"         tools/threshold_sheet.py  ->  0   (ADR 0026, ratified 2026-08-24)
grep -n "No decision point" tools/threshold_sheet.py  ->  0   (ADR 0035, ratified 2026-08-25)
```

## What is ruled

1. **The sweep is comprehensive.** All 169 topics are disposed; `unread` is a defect to be
   burned down and not a resting state. The considered alternative was reading a topic on
   the day a paper needs it.
2. **The six builds and two rulings land before the sweep starts.** No topic is swept while
   the format cannot represent what a guideline states.
3. **The reading order is re-keyed on the machinery that has never run**, beginning with
   `abdominal aortic aneurysm screening`. ADR 0009's order becomes the tail and its stated
   reason is retired.
4. **#429 stays one ticket and acquires no children.**
   [`reference/thresholds/coverage.md`](../../reference/thresholds/coverage.md) is the work
   list; the reviewable unit is a pull request per batch; the ticket closes when
   `python tools/threshold_coverage.py` reports `unread 0`.
5. **ADR 0009 point 5 is discharged for every `bound`-only topic**, not for `diabetes.md`
   alone. [#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436) leaves
   #429's dependency list and keeps the recommendation accounting inside a sheet.
6. **The guideline catalog gains a `url` column**, filled once and audited like every other
   mechanical column, rather than a per-sheet lookup.
7. **A threshold sheet records the extraction identity it was read against.** A mismatch
   against the current extraction warns and names the affected sheets; it does not refuse.
8. **A source document's `class` enters the sheet's `## Sources` table.** A source whose
   class is `scope-of-work` is a declared non-source, and its registry row states that
   reason rather than `none`.
9. **Population and quantity keys stay sheet-local, the directory declares it, and the
   cross-sheet reading is assigned** to a named row of
   [practicum-case-study](../../skills/practicum-case-study/SKILL.md) step 9's check table.
10. **The USPSTF recommendation table and the threshold sheets are joined on filename**,
    which both artifacts already carry, and never on topic name, which they spell
    differently and always have.

## Why comprehensive, when the ticket's own motivation is demand-shaped

#429 quotes the clinician on why the machinery exists: *"the whole point was to get an
agent to read whatever guideline it was and know what it says, so we can use said guideline
in our references and in our paper."* *Whatever guideline it was* is a lookup, and the
first draft of this session recommended reading on demand for that reason. **It was wrong
twice.**

It priced a bottleneck that does not exist. [ADR 0025](0025-a-section-read-is-the-unit-and-a-sheet-s-page-coverage-is-what-the-state-asserts.md)
point 2 rules that an agent performs the read and a blind second **agent** reads a null
span. The clinician is not in the loop per sheet, so the 7,356 remaining pages are agent
cost — the resource the quoted sentence says he is spending to stop being the bottleneck.

And on-demand fails at the one moment the machinery exists for. `tools/differential_scan.py:946-953`
makes the `recalled, no shipped sheet` verdict a finding **only where the subject joins a
topic that has a shipped artifact**. On an unread topic that verdict passes uncontradicted.
On-demand therefore guarantees the miss surfaces mid-paper, silently, as a pass.

## Why the builds land first

ADR 0025 point 10 permits a reading ticket to retire null spans before
[#464](https://github.com/mshamblin5150-code/clinical-skills/issues/464) lands. That was
ruled for four sheets and does not scale to 169, for a reason the tracker already records.

The one implementation attempt started, and the first exact-source slice anyone tried —
`abdominal aortic aneurysm screening` — reached a decision point stated in narrative
(*ever smoked*, commonly defined as 100 or more cigarettes, which decides grade B against
grade C). The sheet, the registry promotion, the recommendation record and the second-read
record were all removed and the tree restored to 169 `unread`. Two independent
non-authoring checks reproduced the failure **while every mechanical gate passed**.

**Which topics #464 blocks cannot be computed.** Whether a guideline states its cutoff in a
curated recommendation row or in Practice Considerations is not knowable from the catalog,
the registry, or the recommendation record. Finding out *is* the read. So there is no
partition of the 104 `exact` topics anyone can hand an agent, and "sweep the unblocked ones
first" is not an instruction that can be written.

## Why the order is re-keyed

ADR 0009 ordered exact multi-document topics early so that `CONFLICT` and per-source
`COVERAGE` would run before single-source work could hide defects in them. **That premise
is false in both halves**, re-derived at `851d3d4`:

```
sed -n '213p;215p' reference/thresholds/hypertension.md   ->  two live CONFLICT: blocks
grep -c "^| aha-2025" reference/thresholds/hypertension.md ->  1   (single-source)
```

The gate has run, and it ran on a single-source sheet, since before #429 was filed. Comment
5 on the ticket got this right on 2026-08-23; comments 12 and 17 overturned it by
re-deriving against `diabetes.md` instead, agreed with each other, and the body was patched
to match the wrong answer. **Two independent re-derivations agreeing is not evidence when
both used the same wrong input.**

What has never run against a real topic is ADR 0026's `narrative` kind, ADR 0035's null
sheet, ADR 0046's scope gate and ADR 0049's two lookup roots. The order is keyed on those
instead. `abdominal aortic aneurysm screening` is first because it is 8 pages, one document,
`exact`, the corpus's one proven narrative case, the named acceptance criterion in #464's
own *Done when*, and the topic that already rolled a sweep back once.

## Why there are no per-topic tickets

[#471](https://github.com/mshamblin5150-code/clinical-skills/issues/471) set the precedent
at four sheets: one reading ticket per sheet. Applied literally that is 169 tickets, taking
the tracker from **53 open to 222**. `CLAUDE.md` requires that finishing a ticket means
sweeping every open ticket one at a time, so every future session's mandatory sweep becomes
4.2 times longer, permanently, until the reading finishes — and #429's own thread is 27
sweep comments long, so that cost is measured rather than feared.

The registry is also already the answer. Its topic column is derived from the catalog rather
than typed, and `tools/threshold_coverage.py` audits both the population and the state
counts. A parallel set of 169 tickets is a hand-kept second copy of it, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s subject at a
scale of 169 — and #429's own *Done when* already demands the opposite: *"the count of each
is re-derivable by command rather than stated in prose."*

The reviewable unit is a pull request per batch, each carrying its own `coverage.md` diff,
so a reviewer sees which rows moved and on what evidence.

## Why ADR 0009 point 5 is discharged generally

ADR 0025 point 5 reads *"ADR 0009 point 5 no longer blocks `diabetes.md`"*, and ADR 0009's
own annotation reads *"Point 5 is discharged rather than overruled."* General reasoning, one
named example, in both records.

The reason given is the instrument: a page-coverage read is a named span with a page range
checked against the catalog's `page_count`, and **it opens no recommendation record at all**,
so a marker window that ends before a decision point cannot corrupt the claim. That argument
does not know which document it is about. ADR 0025's own rejected option confirms the scope,
refusing to hang the state on the recommendation index because *"the state asserts pages
read"*. `diabetes.md` is named because it was the sheet in front of that grilling.

**46 rows of the registry carry `blocked on #436` for a block discharged on 2026-08-23**, and
`tools/threshold_coverage.py:91` grades the record cell for non-emptiness only, so nothing
can fail on a retired reason. That is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s
shape — a prose claim no code change fails against — telling the next agent that a third of
the sweep is blocked when it is not.

## Why the `url` moves to the catalog

`tools/threshold_sheet.py:948-951` refuses a source with an empty `url`, so no sheet ships
without one. [#551](https://github.com/mshamblin5150-code/clinical-skills/issues/551) records
that the drafter's unseeded path — **this sweep's path** — writes
`file:///C:/codeing/guidelines-src/...`, a maintainer's local disk.

Re-derived over the extracted corpus, page 1 taken as the text before the first form feed,
**146 of 179 documents print a DOI on page 1**: USPSTF 86/90, IDSA 38/41, AHA ACC 22/23, and
**KDIGO 0/18, ACIP 0/3, ADA and CDC and GINA and GOLD 0/4**. Joined to the registry,
**33 topics sit entirely on documents whose page 1 prints nothing.** *(Comment 26 on #429
published 144/179 and 25 topics from a different DOI pattern; the discrepancy is in the
pattern rather than the finding, and settling it belongs to #551's build. The hand step is a
third larger than the thread says.)*

Those 33 are KDIGO's 18 topics at 2,368 pages, the three ACIP captures, and the four
single-document societies — the largest documents in the corpus and the last block of the
reading order, so a per-sheet discovery would land at the most expensive possible moment.
A catalog column converts 33 per-sheet inventions into one auditable pass over an artifact
`tools/guidelines_catalog.py` already re-derives.

[ADR 0047](0047-a-corpus-document-s-stated-citation-is-read-off-its-own-page-and-a-link-is-not-one.md)
ruling 11 declares the catalog's `citation` column independent of a sheet's `url` — *the
catalog answers what does this copy say it is; a sheet answers where should a reader go*. A
separate `url` column is a different column and does not merge them, but that record is read
before this is built rather than after.

## Why a sheet records its extraction identity

`manifest.json` carries an exact content-addressed identity — the producer commit, a
`sha256` per producing file, the engine version, and all three boilerplate knobs. A sheet
carries `citations resolved against C:/codeing/guidelines-src on <date>`: a local directory
path and a date.

`reference/thresholds/hypertension.md:55` says **2026-08-16**, and the extractor moved on
2026-08-19 ([#178](https://github.com/mshamblin5150-code/clinical-skills/issues/178), 2,809
inferred spaces removed) and 2026-08-20 ([#172](https://github.com/mshamblin5150-code/clinical-skills/issues/172),
operator repair). Its citations were resolved against an extraction that no longer exists
and nothing in the file can say so.

At one sheet that is settled by looking. At 169 it is unanswerable: a corpus refresh moves
every snippet's substrate at once. `reference/thresholds/README.md:279` already calls the
existing line *"a held claim"*, which is its honest name and too weak for the scale this
sweep creates.

The mismatch **warns** rather than refuses. A re-extraction that changed nothing relevant
would otherwise refuse all 169 sheets at once and turn the pre-commit hook into a check
people learn to `--no-verify` around, which is the cost `CLAUDE.md` names for the threshold
gates by name. The refusal stays where the evidence is: tier 1 and tier 2 already fail a
snippet that stops resolving, and the identity line says *why* and *which*. Tier 2 opens the
real PDFs and survives a re-extraction; tier 0 and tier 1 rest on extracted bytes and are the
two that run on every commit.

## Why document class sorts

ADR 0009 rejected sorting by society and by recommendation grade and never considered
`class`. [#107](https://github.com/mshamblin5150-code/clinical-skills/issues/107) ruled that
`class` records document **form** and deliberately added no `status` column — *"this still
does not answer whether a guideline is current or superseded."* Nothing therefore says a
draft's numbers may not ship as thresholds.

Three non-guideline documents are the **sole** source for their topic, and no topic mixes
classes:

| class | pages | topic |
| --- | ---: | --- |
| `draft` | 499 | `acute kidney injury and acute kidney disease` |
| `scope-of-work` | 9 | `heart failure in chronic kidney disease` |
| `errata` | 2 | `hepatitis C treatment trial, babesiosis treatment tables (corrections)` |

The KDIGO AKI public review draft is the **largest document in the corpus** and the last,
most expensive item in the reading order. Under ruling 1 an agent reads all 499 pages and
ships rows that `differential_scan` joins into a run and a case study cites. A public review
draft is not in force, and the `## Sources` table carries `version` and `published` but no
cell that says so. The numbers are worth having; they ship **labeled** rather than
suppressed, because dropping them would pretend the document is not in the corpus.

The scope-of-work is the opposite failure and the cheaper one. It states what a *future*
guideline will cover and holds no clinical quantity by design, so it reads cover to cover and
lands `none` — and by [#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85)'s
rule `none` is *"close to a negative finding, and a reader may lean on it."* A `none` on
**heart failure in chronic kidney disease** asserts that KDIGO states no decision point on
it: true of the document, false about the world, since KDIGO has not written the guideline
yet. That is precisely the defect ADR 0009 built `none` against `unread` to prevent, arriving
through a door neither record checked. It becomes a declared non-source instead.

The `errata` needs none of this. Its topic is named *(corrections)* and nobody will lean on
it.

## Why sheet-local vocabularies stay

`gate_schema` groups `(quantity, population)` within **one** sheet, and `--all`
(`tools/threshold_sheet.py:2751-2761`) iterates sheets independently. `## Populations` and
`## Quantities` are declared per sheet. Four sheets already carry **149 population keys and
407 quantity keys** in four vocabularies nothing binds:

```
diabetes.md   populations 125  quantities 356      cervical-cancer.md            populations 4  quantities 5
hypertension.md populations 19 quantities  45      prediabetes-…-screening.md    populations 1  quantities 1
```

There is a live overlap. `hypertension.md` declares `adults-dm` — *"adults with diabetes"* —
while `diabetes.md` declares 125 population keys over the same patients with no key in
common. A case study on a diabetic hypertensive joins both topics and pulls rows from both
sheets. At four sheets a person holds that in their head; at 169 nobody does.

The comment at `tools/threshold_sheet.py:975-977` names the cross-society case — KDIGO's
`SBP <120` in CKD against AHA/ACC's `<130/80` in adults — as why population is in the key,
and records it as the clinician's ruling. **Those two live in different topics**, so they
land in different sheets and the mechanism that ruling asked for never sees them.

A shared directory vocabulary was rejected: a population is defined by the guideline's own
words, which is why #429's body puts the verbatim wording beside the key so that *"a mis-keyed
row is a wrong word a reader can see rather than a silent miss"*, and forcing 169 societies'
populations into one vocabulary would invent a clinical rule no guideline states. A
cross-sheet similarity gate was rejected because it needs a threshold nobody can ground —
`SPACE_ADVANCE_FRACTION`'s recorded failure and [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s
objection, a value named at an edge.

Declaring it is half the ruling. Whether two sheets' rows apply to one patient is a clinical
reading, so it becomes a named row of step 9's check table expected by
`checks_ledger.EXPECTED_CHECKS`, on the arrangement that already holds *the dose against the
record that sourced it*.

## Why the join is on filename

Decision 1 was answered *yes* and ADR 0009 kept the table: *"`reference/guidelines-uspstf.md`
remains the recommendation artifact for the federal documents."* Both artifacts stay by
design. What no record settled is that they are **keyed differently**:

```
reference/guidelines-uspstf.md    topic = "Screening for Cervical Cancer"   (derived from the PDF title)
reference/guidelines-catalog.md   topic = "cervical cancer screening"       (hand-curated)
```

Zero of the four shipped sheets' topics appear in the table's 97-name vocabulary today, so
the problem is invisible; after the sweep all 84 USPSTF topics carry both.
`tools/differential_scan.py` consults `USPSTF_ROWS` at `:806` and `THRESHOLD_ARTIFACT_TOPICS`
at `:948` and reconciles neither.

The disagreement is already visible in the worked case. For women aged 30 to 65 the table's
interval cell reads `every 3 years or every 5 years` —
[#432](https://github.com/mshamblin5150-code/clinical-skills/issues/432)'s correction, one
cell naming both periods with the modalities dropped. The sheet, under ADR 0009 ruling 4,
puts the method in the quantity key: three rows, cytology at 3 years, hrHPV at 5, cotesting
at 5. Two committed answers to one clinical question at two resolutions, with no pointer
between them.

The filename is in both files already, so the column is computed rather than hand-kept.
Retiring the table for topics that gain a sheet was rejected: it contradicts a ratified
record and discards 143 curated statements to solve a pointer problem.

## Consequences

The sweep does not start today, and the calendar cost is real. Six tickets carry
`ready-for-agent` and two need rulings before the first topic is read.

Four artifacts gain a column or a declaration — the catalog's `url`, the sheet's `class` and
extraction identity, the directory README's statement that a clean `--all` over 169 sheets is
**not** a claim of internal consistency. Three of those are format changes to
`threshold-sheet/2` and belong to that schema's owner rather than to #429, which is where
they become true rather than where they are built.

`none` remains the registry's strongest claim and is now bounded on two sides: it is a claim
about the **named source documents** and never about the topic, and a source that is not a
guideline cannot produce one.

## Rejected

- **Read a topic on the day a paper needs it.** The miss surfaces mid-paper as an
  uncontradicted pass, which is the worst available moment and the worst available shape.
- **Sweep USPSTF's 84 topics and hold the rest.** Priced on a clinician bottleneck that ADR
  0025 point 2 had already removed.
- **Start on the representable half.** Which topics #464 blocks is discovered by the read
  itself, so the partition cannot be written.
- **Start on null spans only.** Spends the doubled agent cost first on the spans that by
  definition yield no rows, and leaves 169 half-read artifacts whose completion is scheduled
  by nothing.
- **One reading ticket per topic.** 53 open issues becomes 222 and every future mandatory
  sweep becomes 4.2 times longer.
- **A shared population vocabulary across the directory.** Invents a clinical rule no
  guideline states.
- **A cross-sheet similarity gate.** Needs a threshold nobody can ground.
- **Retire the USPSTF table where a sheet exists.** Contradicts ADR 0009 and discards 143
  curated statements.
- **Drop the draft and scope-of-work topics from the denominator.** 499 pages of KDIGO's
  proposed AKI thresholds are worth having, labeled.
- **Gate the extraction-identity mismatch as a refusal.** One irrelevant re-extraction
  refuses all 169 sheets and teaches people to bypass the hook.
