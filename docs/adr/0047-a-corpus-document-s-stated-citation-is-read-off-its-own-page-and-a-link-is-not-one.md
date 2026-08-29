# A corpus document's stated citation is read off its own page and a link is not one

[#512](https://github.com/mshamblin5150-code/clinical-skills/issues/512) was split out of [#439](https://github.com/mshamblin5150-code/clinical-skills/issues/439)'s grilling on 2026-08-25 because a source link is a different kind of fact from the columns beside it. Its decision-reason 1: *"It introduces a class of committed fact nothing in the tree can re-derive or verify. Every other column in both ledgers is either read off the document or hand-audited against it. A URL is neither — it is a claim about the outside world, and the repo has no instrument that could ever grade one."*

Grilled on 2026-08-27, against `origin/main` `6f60fae`. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The measurement falsified the premise, which is why there is a column at all

The ticket asks whether to record a **link**. The corpus mostly records something else already, on its own pages.

Measured over all 179 extracted documents, 2026-08-27. **These figures are counted against a corpus outside every checkout and nothing committed re-derives one.**

| | documents |
| --- | ---: |
| print a DOI on their own **page 1** | 144 |
| carry their own document DOI, page 1 or deeper, each read with context | **163** |
| carry none — and 2 of those are unverified rather than known-absent | **16** |

A DOI printed in a document's own citation line — `JAMA. 2019;321(4):394-398. doi:10.1001/jama.2018.21367`, `Circulation. 2026;153:e1154-e1276. doi: 10.1161/CIR.0000000000001423` — is read off the document exactly the way `title` and `year` are, and the audit ledger's `page` and `evidence` columns already grade that class of fact.

**So decision-reason 1's premise is false for most of the corpus.** What survives it is narrower and is the whole of this record: *what a document states its citation is* is a reading, and *a link that resolves* is a claim about the outside world. Those were one sentence in the ticket and are two now — [ADR 0042](0042-a-refutation-declares-a-second-route-and-independence-stays-unreachable.md) ruling 5 forced the same split on `paywalled`.

## What is ruled

1. **The catalog gains a `citation` column and the tree records what a document prints, never where to download it.** The alternative that costs nothing — leave #439's banner and declare the absence — is refused, because the absence is not real for 163 documents.
2. **The value is *whatever locator the document prints for itself*, and three kinds are admitted**: a DOI, a URL where the document prints one, and a journal citation line where the document predates printed DOIs or is a compilation. A hand-found URL is **not** admitted, and neither is a publisher host.
3. **It is a judgment column, not a mechanical one.** It is not emitted by the extractor and `CACHE_IDENTITY` does not move. `guidelines_catalog.py --draft` scaffolds a page-1 candidate and marks it **unconfirmed**; a person confirms or corrects it, as `topic` and `population` already arrive blank rather than guessed.
4. **It joins `AUDITED_COLUMNS`**, which is the same object as `NULLABLE`. A blind second read is the only instrument here that catches a transposed digit, and a transposed digit is a locator resolving to a different document.
5. **No value-shape check.** No other audited column has one, and a pattern wide enough to accept `Ann Intern Med. 2011;155:246-251.` also accepts `www.annals.org`, which is the value ruling 2 refuses. Two readers agree or the clinician rules — that is the instrument, and it is the same one every other audited column uses.
6. **`?` keeps its catalog meaning: the document prints no way to find itself.** It never means nobody has looked. Every `?` takes its `## Unsettled cells` reason like any other, and every `?` still gets a full reading row recording the page the reader looked at.
7. **The value lives on the catalog and the reading on the audit ledger.** `CONTEXT.md` already draws that line — the catalog's subject is *metadata about documents* and the ledger's is *which exact bytes a reading rests on*. The third-file option is closed for the reason #439 closed it.
8. **The column is appended after `class`, and four things move with it — two positional readers and two prose enumerations.**

   **Positional readers.** `tools/test_guidelines_catalog.py:803` sums `int(cells[6])` for the page total, so inserting anywhere before index 6 silently changes what that test adds up. **And `tools/corpus_census.py:742` holds `CATALOG_CELL_COUNT = 10`** — the eight columns plus the two empty strings a leading and trailing pipe produce — tested with `==` at `:753`, so a ninth column matches no row at all: `read_catalog_topics` goes from **169 topics to 0**, measured 2026-08-27 by appending the column to a copy of the catalog. **Appending saves the first and not the second; only raising the constant saves the second.**

   **Prose enumerations that become false.** `CONTEXT.md:247`'s **Guideline catalog** entry and `CLAUDE.md:1175` each list all eight columns by name. Both are [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape and neither fails anything when it goes stale.

   *(Corrected in place under [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md) on 2026-08-27, hours after ratification, and the way it was found is worth more than the repair. The original named `test_guidelines_catalog.py` alone — a ruling **about a positional dependency** that had itself surveyed one of two, which is this record's own extractor-coverage warning arriving on the record within the hour. Two sweep subagents reading unrelated tickets found the `corpus_census` reader independently of each other, and one of them also found the two enumerations — including the one seven lines above the `Stated citation` entry **this record itself added to `CONTEXT.md`**. The anchor was `:804` and is `:803`; `:804` is the `assertEqual`.)*
9. **The scaffold reaches the catalog reader and must not reach the blind reader.** Both readers seeing the draft would agree on the regex's answer, and the audit would have measured the matcher against itself — a numerator and denominator built from one matcher, which this repo's extractor-coverage rule already forbids.
10. **The column ships filled, in one ticket.** Landing it with 179 `?` cells would put 179 false sentences in `## Unsettled cells`, which is a lie in the shape of a declared limit.
11. **It is independent of a threshold sheet's `url`, and the divergence is declared rather than bound.** The catalog answers *what does this copy say it is*; a sheet answers *where should a reader go*, which may legitimately be a society topic page. A co-published guideline prints one DOI and may be correctly cited by another, and a difference between the two files is not a defect.
12. **What is not claimed lives in one module object**, on `reference_scan.NOT_REACHED`'s arrangement — the catalog's prose and the `CONTEXT.md` entry point at it and copy no row, and a test binds both directions. [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s ground: a prose edit to a limit fails nothing, and three of these limits read as weaker than they are on a skim.

## `Stated citation`, and why not `locator`

`locator` is this repo's own word for the concept and it was refused. `git grep -i locator` returns hits across 25 files, and `Locator` is not one of `CONTEXT.md`'s 96 term headings — so there is no [ADR 0037](0037-a-contested-glossary-term-goes-to-the-higher-adr-number.md) contest to win. The problem is narrower and worse.

`research_ledger.LOCATOR` carries a **live, tested definition**: *"A locator is a URL or a bare DOI, and nothing else"*, with `UNRESOLVABLE_LOCATOR` firing on anything else and `test_research_ledger.TheAgentWritesDownWhatItRead` pinning all three directions. Ruling 2 admits a journal citation line, which that regex refuses. Taking the word would put two definitions in the tree that **disagree about a specific string** — ADR 0037's disease, and worse than its case, where the two definitions described different objects rather than contradicting each other about one. *(Evidence coordinates renamed to durable object and test-class names on 2026-08-28; the ruling is unchanged.)*

The other senses coexist harmlessly: ADR 0025's *"Page is a locator and not an atom"* and [ADR 0026](0026-a-threshold-row-s-rec-is-a-source-locator-and-narrative-is-a-reserved-kind.md)'s *source locator* are one idea at different scales. Only `research_ledger`'s would be made false, and paying for the word means changing a shipped skill's grading of a different artifact.

**`stated` is [ADR 0040](0040-a-stated-expiry-is-read-off-the-document-and-a-publication-cadence-is-not-one.md)'s adjective**, set eight records ago on a column with this exact rule: read off the document, never derived. It carries the invariant into the name, so a reader who sees `Stated citation` knows a hand-found URL does not belong in it.

## Three recorded instances of the trap, and the mechanical route fails all three

A guessed locator is worse than a blank one — `guidelines_catalog.py --draft`'s own rule about `population`. Each of these is a real document in the committed corpus, and each is a case where a regex publishes a locator resolving to **a different document**, with the same confidence it publishes a correct one.

| document | a matcher would publish | what it actually is |
| --- | --- | --- |
| `IDSA/ciab275` | `10.1093/cid/ciz628` | the article this errata **corrects** |
| `CDC` opioid 2022 | `MMWR Recomm Rep 2016;65[No. RR-1]:1-49` | the **2016 edition it replaces** |
| `USPSTF/testicuprs` | a page-3 `Ann Intern Med. 2010;153:396-9.` | a cited reference, not itself |

The filename shortcut fails the same way: **28 of 41 IDSA stems match their page-1 DOI**, and `ciab275` is among the 13 that do not. A rule built on the 28 would have shipped the errata's wrong locator.

That is ruling 3 and ruling 4's ground together. The value must be somebody's reading, and a second reader must take it cold.

## The cost was priced off the committed ledger rather than estimated

`reference/guidelines-catalog-audit.md` re-derives these, so unlike the corpus figures above they are checkable from a clone. Measured 2026-08-27.

`## Independent readings` holds **716 rows — exactly 4 × 179**. `## Clinician rulings` holds **322**:

| audited column | rulings | share | what the reader is doing |
| --- | ---: | ---: | --- |
| `title` | 128 | 72% | deciding what the title *is* |
| `topic` | 111 | 62% | choosing clinician-facing wording |
| `population` | 76 | 42% | deciding what the front matter states |
| `year` | **7** | **4%** | transcribing a figure |

**The ruling rate measures how much judgment a column takes, and a citation is `year`'s kind of fact.** The overlap is closer than the analogy: `year`'s evidence kind is `publication-line` for **108 of its 179** readings, and the publication line is where the DOI is printed. `year`'s page locator is page 1 for 176 of 179, and 144 DOIs are on page 1. **For most of the corpus the second reader is re-reading a line they are already standing on.**

**The ~7 figure is an inference from `year`, not a measurement**, and is recorded as one. The DOI read has not happened.

## What the ticket got wrong, and what it could not have known

**The premise sentence is narrower than it reads.** *"No committed file records where any corpus document came from"* is true of the two ledgers and **false of the tree**. Every committed threshold sheet carries a `Sources` table with a `url` column, and five corpus documents already have a recorded source in it — including `https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/cervical-cancer-screening`, which answers the ticket's own *"first thing to measure"* about a stable USPSTF per-topic address, in a committed file, in the affirmative.

**And the grilling's own instrument was wrong first, in the direction this repo keeps recording.** A round-1 table counted *a DOI anywhere in the document* as coverage. That matcher counts **reference-list** DOIs as the document's own: CDC's only DOIs are on page 30, GOLD's on pages 197+, and ADA's page-7 hit is the DOI of its five-page introduction, not of the 377-page compilation. The page-1 figure was sound; the "anywhere" figure was not, and the corrected total landing nearby does not rescue it. Every deeper hit was then re-read with context — KDIGO's 16 are genuinely its own, in the Foreword publication line.

## What was refused

- **A resolver.** Unchanged from the ticket, with its ground restated per #512's own sweep note: the honest form is **no tool opens a socket**, not **no route exists**. ADR 0042 established that an authenticated route exists at authoring time; #87 established the nine corpus societies were publicly downloadable anyway, so it opens no document a public download does not.
- **A hand-found URL for the residue.** It would have no page number, the blind second read could not grade it, and it would be the only cell in either ledger not traceable to a page — reintroducing decision-reason 1 for a dozen rows after three rounds eliminated it for 163.
- **Splitting `NULLABLE` from `AUDITED_COLUMNS`.** It would invent a column kind the tree does not have and make "was this value checked?" unanswerable from the code.
- **Binding a threshold sheet's `url` to the catalog's citation.** It fails `hypertension.md` today, where the sheet cites `10.1161/HYP.0000000000000249` and the corpus copy prints `10.1161/CIR.0000000000001356`. Neither is wrong — the guideline was co-published — and forcing the sheet onto the corpus copy's DOI is a correctness regression bought for tidiness.

## What none of it reaches

**Two people will have read the same string off a page. Nothing will have opened one.** That is the honest form of a passing `python tools/guidelines_catalog.py`, it is the same sentence every other audited column could carry, and ruling 12 puts it where a prose edit cannot quietly delete it.
