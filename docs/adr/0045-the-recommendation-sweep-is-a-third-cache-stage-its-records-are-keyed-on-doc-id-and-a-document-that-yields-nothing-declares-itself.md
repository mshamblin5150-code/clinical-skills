# The recommendation sweep is a third cache stage its records are keyed on doc_id and a document that yields nothing declares itself

[ADR 0030](0030-a-recommendation-record-is-owned-like-every-other-artifact-its-trust-floor-is-keyed-on-the-limb-that-built-it-and-the-drafter-takes-no-escape-hatch.md) ruling 3 declined to make a recommendation record part of the content-addressed cache, and named its ground rather than leaving it implied:

> The record is stamped and both read sites validate. It does not become a third stage of `guidelines_build`'s content-addressed cache; that needs a batch producer this repo does not have.

[#510](https://github.com/mshamblin5150-code/clinical-skills/issues/510) is that batch producer. Grilled on 2026-08-26 at `origin/main` `a058158`; the clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## Two of the ticket's three decisions rested on premises the measurement falsified

**Decision 1's premise was that a recs record is the wrong shape for the cache.** The ticket put it as *"The cache is per-corpus with one build directory per stage; a recs record is per-document."* The extraction stage is **also** per-document: `guidelines_extract` writes one `<doc_id>.txt` per PDF (`tools/guidelines_extract.py:1158`, the identifier derived at `:1113`) and `guidelines_manifest` enforces `output == f"{doc_id}.txt"` (`tools/guidelines_manifest.py:296`), inside one build directory whose identity hashes the whole PDF set as a single `source_files` list (`tools/guidelines_build.py:123`). Per-document contents inside a per-corpus key is not a tension this cache has ever had to resolve — it is what the cache already does.

**Decision 2's premise was that a corpus walk cannot name a file.** The ticket put it as *"A corpus walk has no sheet to read a key from, so it has to answer this before it can name a file."* It has one. `_source_key` derives the key from a **catalog row**, not from a sheet — `{society first token}-{year}` at `tools/threshold_draft.py:77` — and a sheet only *seeds* an override at `:183`.

**The real obstacle is that the key is scoped to a topic**, because `_source_keys` computes its collision suffix over `candidates`, and `candidates` is `[row for row in catalog_rows if _topic(row.topic) == wanted]` (`tools/threshold_draft.py:156`). Measured against `reference/guidelines-catalog.md`, 179 rows, 0 parse problems:

| | |
| --- | --- |
| distinct bare source keys corpus-wide | 51 |
| rows whose bare key collides **corpus-wide** | **163** of 179 |
| rows whose bare key collides **within its own topic** | **6** of 179 |
| rows where the two scopes **disagree on whether to suffix** | **157** of 179 |
| distinct topics | 169 |

`uspstf-2022` is the bare key for 15 catalog rows and `uspstf-2021` for 13. A sweep deriving keys over the whole catalog would suffix 157 documents that `threshold_draft` leaves bare, and write 157 filenames neither read site ever looks up. **A source key is not a document identifier and cannot be made into one.** This is [#456](https://github.com/mshamblin5150-code/clinical-skills/issues/456)'s finding inverted: that ticket found three names for one AHA document, and this is one name for thirteen USPSTF documents.

## The mode census reconciles across two readers, and one of its two figures can never be re-derived again

`recs-sweep.json` is the **pre-#173** census and the figures at `reference/thresholds/README.md:504` are the current ones. Both are correct for their date:

| | exact/ruled-table | exact/curated-table | bound | nothing found |
| --- | ---: | ---: | ---: | ---: |
| `recs-sweep.json`, 2026-08-16 | 22 | — | 19 | 138 |
| README, 2026-08-19, post-[#173](https://github.com/mshamblin5150-code/clinical-skills/issues/173) | 22 | 90 | 48 | **19** |

138 = 90 USPSTF + 39 IDSA + 9 others, which is `README:511`'s own sentence. #173 moved the 90 USPSTF documents to `curated-table` and 28 IDSA plus 1 GOLD to `bound`, leaving 19. Every cell reconciles.

**That sharpens ADR 0030's reason for preserving the file beyond what the ADR states.** It called `recs-sweep.json` *"plausibly the last surviving re-derivation"* behind the README's corpus-wide mode figure. It is the re-derivation behind the **historical** sentence, not the current table — and the two have opposite futures. The current table becomes re-derivable the moment the sweep below ships. The 2026-08-16 reading never becomes re-derivable again, because the reader that produced it no longer exists. A sweep command retires one of those figures and cannot retire the other.

## The rebuild was priced rather than called CPU

Six documents sampled at random from the corpus, 2026-08-26:

| pass | mean per document | 179 serial |
| --- | ---: | ---: |
| `guidelines_extract.extract_pages` | 2.90 s | 8.6 min |
| `guidelines_recs.extract` | 18.81 s | **56.1 min** |

Recommendation reading is **6.5×** text extraction, because `find_tables()` does table geometry that text extraction never touches. Every ruling below that trades CPU is trading this number and not a guess.

## Ruling 1 — the sweep is a third `CACHE_IDENTITY` stage named `recs`, on `extraction`'s shape

One build directory per corpus identity, one record per document inside it, one manifest carrying a row per document. Identity is the PDF inventory, `_code_inputs` over the producing modules, the runtime, and ruling 4's committed table. Not a plain walk.

What that buys is already written and already verified: the SHA-256 inventory re-hash at `tools/guidelines_build.py:326`, the refusal to ever serve a dirty-built artifact at `:313`, the atomic `os.replace` at `:515`, the per-path reader/writer locks in `tools/artifact_lock.py`, and quarantine on damage at `:386`.

**The stage needs an `artifact_provenance.TRUST_FLOOR` entry of its own, and that is not ADR 0030 ruling 2's floor.** `_verify_artifact` compares the recorded producer inputs against `_trust_floor_inputs(identity)` (`tools/guidelines_build.py:320`), which raises on an unknown kind, so a `recs` stage cannot verify without one. That entry is a **stage**-level input set answering *was this whole build produced cleanly from these inputs*. ADR 0030 ruling 2's floor is **per record**, keyed on `counted_from`, and lives in `guidelines_recs.py` beside the `SOURCE_*` constants. [ADR 0044](0044-the-uspstf-population-vocabulary-stays-closed-because-the-check-that-guards-it-can-only-see-one-of-the-two-failure-directions.md) corrected a record on 2026-08-26 for conflating exactly these two, so the distinction is named here rather than left to be inferred: two tables, two questions, and the per-record floor does not move into `TRUST_FLOOR`.

**The stage is independent of `extraction` rather than hanging off it**, unlike `index`. The producer reads PDFs, not extracted text, and after [ADR 0032](0032-the-marker-limb-reads-the-repaired-text-the-other-two-limbs-declare-that-they-do-not-and-every-citation-gate-reads-one-reader.md) the marker limb still reads a PDF — through `rebuild_text` rather than `get_text`. So a recs rebuild never waits on an extraction rebuild.

**The declared cost is one full extraction-and-index rebuild, and two independent mechanisms each force it.** The stage list is hardcoded at `tools/guidelines_build.py:172` and `:187`, and `CATALOG_SCHEMA_VERSION` is compared exactly at `:184`, so adding a stage invalidates every existing catalog. Separately, `_code_inputs` (`:107`) hashes file *contents* and `tools/artifact_provenance.py` is named in **both** existing identity tuples (`:47`), so adding a `recs` key to `CACHE_IDENTITY` invalidates extraction and index by itself. The cost is the same either way; both are named so that a builder who finds a way around the schema bump does not conclude the rebuild is avoidable.

## Ruling 2 — a record is keyed on `doc_id`, the sweep publishes nothing into the recs root, and resolve-by-document is #518's to build

Inside the build directory a record is named from `doc_id`, exactly as extraction names `<doc_id>.txt`. The sweep publishes **no** compatibility alias into the recs root, because the measurement above says there is no name it could publish under that both read sites would resolve.

Teaching `threshold_sheet.bind_recs` (`tools/threshold_sheet.py:2128`) and `threshold_draft._record_path` (`tools/threshold_draft.py:107`) to resolve **by document** is handed to [#518](https://github.com/mshamblin5150-code/clinical-skills/issues/518) as a measurement rather than built here. Both sites already hold the document identity and already compare on it — the drafter checks `built_from.casefold() == catalog_row.filename.casefold()` at `:115`, and `_record_built_from_another_document` compares the record's `source` filename to the sheet's `document` cell at `tools/threshold_sheet.py:2170`. The lookup is the last thing keyed on a name.

**This answers #518's own decision 2** — *"is the `recs-` prefix a claim worth checking, or is the whole convention the wrong instrument?"* — with a number rather than a preference: a filename built from a sheet-local key cannot address a corpus. #518's *"do not fold this into a batch producer"* is honored, because what crosses is evidence and not a build.

**The consequence is stated rather than left to be found: until #518 lands, this stage is a verified artifact neither reader can see.** #510's *Done when* bullet 3 — the remedy is a command a person runs over the corpus — is therefore delivered by the pair and not by this ticket alone.

## Ruling 3 — all 179 documents get a record, the 19 that yield nothing declare themselves, and `DidNotScan` refuses the build

`guidelines_recs` returns **2** for two different things: *no recommendation found* (`tools/guidelines_recs.py:697`) and `DidNotScan` (`:691`). They are not one outcome and the sweep does not treat them as one.

**A document that yields nothing is an answer and gets an artifact.** [ADR 0035](0035-a-none-topic-is-a-null-threshold-sheet-and-the-state-is-derived-from-its-span-table.md) ruling 1 settled the topic-level form of this question on the ground that *"the evidence lives in the artifact, not in the registry's `record` cell and not nowhere"*, and it transfers one artifact class down. Its ruling 3 supplies the discriminator that makes the empty artifact safe — a null artifact **declares itself**, because silence and an unfinished read are otherwise the same bytes — and that transfers with it. The record holds no recommendations and a required declaration, checkable, carrying no figures.

**The manifest was the losing option and its defence was good.** In a cache stage the manifest sits *inside* the verified build directory and is hashed into the artifact inventory, so recording the 19 as manifest rows is not ADR 0035's rejected shape, where the registry was a separate committed file. It loses on the reader: under ruling 2 both sites resolve by document, and a nothing-found document with no file returns the same *no recommendation record* as a document nobody ever swept — at the site where the distinction costs something.

**`DidNotScan` refuses the whole build.** It means the curated table disagrees with the document, which is a mismatch between the artifact and its declared inputs — precisely what a content-addressed identity exists to make impossible. Recording it per document would let a build complete while one of its inputs was wrong.

**The word `none` is refused for this bucket, and that is a ruling rather than a style note.** `CONTEXT.md`'s **Sweep state** defines `none` as *"the guideline was read and states no decision point"* — a **topic**-level claim about content. This bucket is a **document**-level claim about a reader: neither limb matched. The two are not the same fact and one of them is very nearly the negation of the other, so this record is a **nothing-found** or **empty** record throughout, matching `reference/thresholds/README.md:509`'s own column, and `none` stays the coverage registry's word.

## Ruling 4 — the stage identity contains `reference/guidelines-uspstf.md`

Editing the curated table changes the stage key, so no verified hit can serve a stale `curated-table` record. The precedent is exact: `extraction_identity` hashes the whole PDF set, so adding one PDF already re-extracts all 179 and nobody has minded.

**The price is corpus-wide over-invalidation.** A curated-table edit rebuilds all 179 records — **~56 minutes serial** — when only 90 of them ever read that file.

**And ADR 0044 sharpens that price rather than softening it.** Its 2026-08-26 correction establishes that a Population-only edit to the curated table moves no record's *content* at all, because `curated_records` builds each `Recommendation` from `row.page`, `row.topic`, `row.grade` and `row.statement` and `population` never leaves `CuratedRow`. A content-addressed identity hashes the **file**, so such an edit is still a full cache miss: **56 minutes of CPU to produce 179 byte-identical records.** That is the sharpest form of this ruling's cost and it is accepted with the cost known, because the alternative is a cache that decides for itself which edits to a declared input do not matter. [#434](https://github.com/mshamblin5150-code/clinical-skills/issues/434) is `ready-for-agent` and rebuilds exactly that table, so it will invalidate the whole recs stage.

**The losing option was the more elegant reading of the existing split**, and it is worth recording why it lost. `_verify_artifact` answers *are these the bytes this build wrote* (`tools/guidelines_build.py:293`); ADR 0030's trust floor answers *are this record's inputs still current*, checked at both read sites. Leaving the table out of the identity would let those two mechanisms divide the work cleanly, and a curated-table edit would surface as 90 untrusted records at exit 2 under ADR 0030 ruling 5, rebuilding nothing that did not change.

It loses because it manufactures a **verified hit that is wrong**. `guidelines_build` would report `reused=True` and print a clean build, and the defect would appear one command later, in a different tool, for 90 documents at once. That is the shape this repo refuses everywhere else — a check answering cleanly about something it could not see — and 48 minutes of CPU is the wrong thing to buy with it.

**This is the first place in the cache where a committed repo file is an input**, so an ordinary documentation-shaped commit can now invalidate an hour of build. That is a new property of the cache and not a detail of this stage.

## Ruling 5 — `recs` is a default stage of `guidelines_build.py`, with `--no-recs`

A cold build goes from roughly 9 minutes to roughly 65. Warm builds are unchanged, because a verified hit costs a re-hash and not a re-read, so the 56 minutes is paid once per genuine identity change — a PDF added or altered, `guidelines_recs.py` edited, `guidelines_extract.py` edited, the PyMuPDF version, or the curated table.

**Opt-in was rejected on a stronger ground than ergonomics.** `guidelines_build.py <src>` would report a successful build having left one of its three artifacts stale, with nothing on the page saying so. `--no-recs` keeps the correct default and gives the 6.5× multiplier somewhere to go that is not *stop running the build*.

**`tools/guidelines_extract.py` sits in both stages' identities.** After ADR 0032 the marker limb reads through it, so a single edit to that module rebuilds extraction, index and recs together — roughly 65 minutes.

## What this does not reach

- **Whether a record is *right*.** The stage verifies that a record is the bytes this build wrote from these inputs. Whether `find_tables()` read the table correctly, and whether a marker match is a recommendation rather than a table-of-contents line, are untouched — the bound mode is an over-report and ADR 0030 and the README both already say so.
- **The 19 nothing-found documents' truth.** An empty record asserts that neither limb matched, never that the document states no recommendation. `guidelines_recs.py:695` already draws that distinction in its own message and this ruling preserves it.
- **The one-PDF command's output.** `guidelines_recs.py --json` still writes to any path `ensure_outside_checkout` permits. That is #518's subject and no ruling here narrows it.
- **A record this stage writes is invisible to #438's Done-when 5 walk, and that miss is outside the ceiling that walk declares.** That walk asserts no other module opens a `recs-*.json` its own way, and ADR 0030's declared ceiling covers only *a path built by indirection*. Under ruling 2 these records are keyed on `doc_id` and are not named `recs-*.json` at all, so a module opening one is invisible for a reason the ceiling does not name — a differently *named* artifact of the same class rather than an indirect path. The walk's ceiling has to widen, or key on the class rather than the prefix.
- **Anything about the recs root's existing contents.** ADR 0030 and [ADR 0034](0034-a-recommendation-record-is-resolved-by-exact-name-at-both-read-sites-and-the-directory-scan-hints-rather-than-selects.md) both refuse to delete or rename the orphaned records and `recs-sweep.json`, and this ruling adds a reason to keep the sweep file rather than a reason to remove it.

## Rejected options

**A plain walk with a `--jobs` flag**, on `guidelines_extract.py`'s shape. Rejected: it rebuilds 179 documents every run and notices nothing, so [#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446)'s corpus-wide rebuild would still be remembered rather than detected, and #438's stamp remedy would stay *remember to re-run it*.

**Publishing per-topic `recs-<key>.json` aliases into the recs root.** Rejected on the measurement: the alias set would be a function of the catalog's `topic` column, so one topic-cell edit silently renames files that ADR 0034 has just finished ruling are resolved by **exact name** — reintroducing the failure that ADR ruled out, one layer down. Six rows would still collide inside their own topic.

**Building the stage and changing no reader, permanently.** Rejected as a resting place rather than as a step: it delivers #510's *Done when* 1 and 2 and leaves 3 unmet, because a verified build directory the readers cannot see is not yet a remedy. It is the interim state ruling 2 accepts, not the end state.

**Dropping the per-record stamp once the stage stamp exists.** Rejected: the one-PDF command survives and produces a standalone record with no build directory around it, and both read sites read a record *file*. The two stamps answer different questions and coexist — ADR 0030's per-record floor keyed on `counted_from`, and the stage's `artifact.json` answering whether the whole build is verified and clean.

## Ordering, and it is not optional

- **[#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438) lands first and is unchanged by this.** Its Done-when 1 writes the per-record stamp, which the rejected option above preserves. This stage wraps its output.
- **[#518](https://github.com/mshamblin5150-code/clinical-skills/issues/518) is what makes the stage reachable**, per ruling 2. Until it lands the artifact is verified and unread.
- **Four open tickets each invalidate the whole stage once it exists, at roughly 56 minutes apiece**, and only one of them names #510 anywhere. [#434](https://github.com/mshamblin5150-code/clinical-skills/issues/434) rebuilds the curated table, per ruling 4, and is `ready-for-agent`. [#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436) edits `read_marker_recommendations`, changing the producer's own identity. [#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446) edits `tools/guidelines_extract.py`, which sits in this stage's identity and extraction's both. [#502](https://github.com/mshamblin5150-code/clinical-skills/issues/502) rides #434's rebuild.
- **#446's Ordering section is falsified by ruling 1 and needs one sentence.** It reads *"this ticket edits no tuple"*, which is true only while `CACHE_IDENTITY` has no `recs` key. If this stage lands first, #446 must add `tools/guidelines_extract.py` to it or the stage serves a verified hit built by the unrepaired reader — which is the precise failure ruling 4 exists to prevent.
- **#502 and #505 each price a curated-table edit as invalidating three records**, which is exactly right today: three of the eight records on disk are `curated-table`. Ruling 4 makes it 179. Whichever lands first sets the cost for the other.
- **#505's ninth column becomes more expensive than its own ticket states.** A ninth column in the curated table makes `parse_curated_table` raise `DidNotScan` (`tools/guidelines_recs.py:433`), and under ruling 3 that refuses the **whole** 179-document build rather than two sheets.
- **Three open tickets now touch `bind_recs` and `_record_path`**: #438's shared trust reader, #518's naming, and ruling 2's resolve-by-document. Two green branches there produce a red merge.

*(Corrected in place 2026-08-28, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s terms. The ADR 0044 link named a remembered title rather than that record's tracked filename; its target now matches the index. No ruling changed.)*
