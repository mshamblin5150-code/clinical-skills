# The sweep alias and the recs root are two lookup roots with two resolution rules and the producer guarantees the prefix it writes

[#518](https://github.com/mshamblin5150-code/clinical-skills/issues/518) was carved out of [#456](https://github.com/mshamblin5150-code/clinical-skills/issues/456)'s grilling and records that `tools/guidelines_recs.py --json` writes a recommendation record to any path `ensure_outside_checkout` permits, so the `recs-<key>.json` convention both read sites resolve by is held by neither of them and by nothing else. Grilled 2026-08-27 at `origin/main` `f758c0b` with the freshness gate reporting `FRESH`. The clinician ruled every point below on the same day.

**Nothing is built here.** The producer half is buildable immediately; the reader half is blocked on [#510](https://github.com/mshamblin5150-code/clinical-skills/issues/510), per ruling 6.

## The ticket's frame moved twice while it sat, and its own newest comment is stale on the second move

[ADR 0034](0034-a-recommendation-record-is-resolved-by-exact-name-at-both-read-sites-and-the-directory-scan-hints-rather-than-selects.md) reached `main` at 2026-08-26T14:37:49Z. [ADR 0045](0045-the-recommendation-sweep-is-a-third-cache-stage-its-records-are-keyed-on-doc-id-and-a-document-that-yields-nothing-declares-itself.md) reached `main` at 2026-08-26T23:06:52Z — **twelve minutes after** this ticket's newest sweep comment, timestamped 22:54, which states that it is on PR #548 and not yet on `main`. That is [#516](https://github.com/mshamblin5150-code/clinical-skills/issues/516)'s class arriving for the second time on this one ticket: a live hedge about an unmerged path outliving the merge by a quarter of an hour.

Between them the two records reshaped all three of the ticket's decisions, and left one contradiction the ticket has no line about:

- **ADR 0034 ruling 1** — the directory scan **discovers and never selects**. Exact name resolves; the glob only hints. Its ground is that `matches[0]` picks arbitrarily where several records name one PDF.
- **ADR 0045 ruling 2** — teach both read sites to **resolve by document**, and hand that to this ticket as a measurement rather than build it.

**Resolve-by-document is the scan selecting.** Same mechanism, opposite verdicts, and the ambiguity ADR 0034 ruled out is on disk right now: four records name the AHA PDF. Decisions 1 and 2 of the ticket are both downstream of reconciling that, and rulings 1 and 2 below are the reconciliation.

## What was measured

Every figure re-derived at `origin/main` `f758c0b`, 2026-08-27, freshness `FRESH`, before the ruling.

**The recs root census is unchanged from ADR 0034's correction.** Read with `_load_record`'s own predicate — a dict carrying a list `recommendations` — the directory holds **8 records and 9 non-records**. Four records name `jones-et-al-2025-…-prevention-detection.pdf`: `recs-aha-2025.json`, `recs-aha-htn-2025.json`, `recs-hypertension.json` and `verify-recs-htn.json`, all `exact`, all 103 recommendations, differing in `doc_id` alone.

**Every committed sheet overlaps the sweep.** Five source keys across four sheets, and all five name a document that is a row of `reference/guidelines-catalog.md`:

| sheet | source key | document |
| --- | --- | --- |
| `cervical-cancer.md` | `uspstf-2018` | `USPSTF/cervical-cancer-final-rec-statement` |
| `diabetes.md` | `ada-2026` | `ADA/standards-of-care-2026` |
| `hypertension.md` | `aha-2025` | `AHA ACC/jones-et-al-2025-…` |
| `prediabetes-type-2-diabetes-screening.md` | `uspstf-2021` | `USPSTF/prediabetes-type2-diabetes-adult-final-recommendation` |
| `prediabetes-type-2-diabetes-screening.md` | `uspstf-2022` | `USPSTF/diabetes-child-final-recommendation` |

So precedence between the two roots is not a question about a future sheet. **It decides which bytes grade every committed sheet in the repo on the first run after the sweep lands.**

**No read site can query the cache without building it.** `tools/threshold_sheet.py` imports `artifact_provenance`, `guidelines_manifest`, `guidelines_catalog` and `guidelines_extract`, and **not** `guidelines_build`. That module exposes no public *verify or return nothing* selector — `_select_or_build` builds on a miss and `_existing` is private. And `threshold_sheet.py --all --quiet` runs from `tools/hooks/pre-commit:52`, so a read site that asked the cache directly could trigger ADR 0045's **56-minute** recs build inside `git commit`.

**The publish-alias precedent is exact and already consumed by this reader.** `guidelines_build:695-696` publishes extraction with `_publish_directory` to `guidelines_extract.default_output` and the index with `_publish_file` to `guidelines_index.default_database`, atomically, lock-held, with rollback. `_publish_directory` copies with `ignore_patterns(ARTIFACT_RECORD)` where `ARTIFACT_RECORD = "artifact.json"` — so **`manifest.json` survives into the alias**, and `threshold_sheet:1532` already reads that manifest out of the published extraction alias.

**A record that fails to resolve leaves the source ungraded and everything below it unrun.** `gate_coverage:2229-2232` is `if recs is None: ungraded.append(key); continue`, which skips the unaccounted-identifier refusal at `:2309`, the mode cross-check, and the scope-out membership grading at `:2318`. It is **not silent** — `COVERAGE NOT RUN` prints and `missing_records` adds *"a warning, not a clean COVERAGE pass"* — and it is **one message for what will shortly be four different events**.

**The producer refusal breaks nothing that exists.** All three `--json` calls in `test_write_guards.py` (`:186`, `:370`, `:403`) already write `recs-x.json`, and no `--json` example in `CLAUDE.md`, in any ADR, or in any skill uses a non-conforming stem.

**The recs root is the index directory, reused.** `DEFAULT_RECS_ROOT` is `C:/codeing/guidelines-index`, which is also `guidelines_index.default_database()`'s parent. That is why it holds a 61 MB SQLite file and nine non-records beside the eight records, and why almost none of that clutter came through `--json` at all.

## Ruling 1 — the `recs-<key>.json` convention survives in the recs root, and the sweep is addressed by a second lookup rather than by a replacement

Two roots, two resolution rules, because the two directories have different integrity guarantees and the rule follows the guarantee.

The **sweep alias** is single-writer, SHA-256-inventoried, `os.replace`d, lock-held, and holds one record per `doc_id` by construction. Document resolution there is unambiguous *because of how the directory is produced*, not because a rule says so.

The **recs root** is hand-fed, outside every checkout, written by eleven worktrees, and is the one place four records for one PDF actually exist. ADR 0034's exact-name rule stays there untouched. Extending document-resolution over it would import the `matches[0]` ambiguity that ADR ruled out, into the very directory whose contents are the evidence for ruling it out.

**This is not a rejection of ADR 0045 ruling 2.** That ruling asked for resolve-by-document and gets it, in the directory where it is safe.

## Ruling 2 — the alias wins, the recs root fills gaps, `--recs key=path` beats both, and the report names the root each source resolved from

Precedence is settled on this directory's measured history rather than on a preference for freshness. The recs root demonstrably accumulates stale artifacts and is forbidden to be tidied: four records for one PDF, nine non-records, files from 2026-08-16 still present eleven days later, and two ADRs refusing anyone the remedy. Letting it win would make an unstamped hand build shadow a verified one **permanently and silently**, for exactly the five documents anybody has ever worked on — which is ADR 0045's *"verified and unread"* interim state surviving the ticket written to end it.

**The override case is real and already has a home.** Someone iterating on a reader who will not spend 56 minutes writes `--recs <key>=<path>`, which is typed, per-run, and visible on the page. That is where an override belongs; a precedence rule that fires unannounced is not one.

**Naming the root is load-bearing and not decoration.** On the first run after the sweep lands, all four committed sheets are graded against different bytes than today. Nothing in this repo would say so unless the report says which root answered, per source, on every run — [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling arriving at a lookup rather than at a population.

## Ruling 3 — the recs stage publishes a directory alias into its own sibling directory, and neither read site imports the cache

`guidelines_build` gains a `_publish_directory` call for the `recs` stage, on extraction's shape and to a sibling of it — beside `guidelines-text/` and `guidelines-index/`, never into the recs root. Both read sites take a path with an environment override, exactly as `threshold_sheet` already takes `CLINICAL_GUIDELINES_TEXT`, and open `<doc_id>.json` inside it.

**Its own directory rather than the recs root**, because publishing `doc_id`-named files into the recs root would put a second naming scheme inside the one directory whose naming ruling 1 has just fixed at exact-name. This does not reopen ADR 0045's rejected option, which was **per-topic `recs-<key>.json` aliases** — a set that is a function of the catalog's `topic` column. A whole-directory alias is a function of nothing but the build.

**The 56 minutes stays off the commit path by construction**, rather than by a flag somebody has to remember not to pass inside a hook.

**The alias is unverified at the read site, and that limit is inherited rather than new.** `_publish_directory` strips `artifact.json`, so a published tree is indistinguishable from one somebody made by hand — extraction already has that hole. What covers it here is that ADR 0030's trust floor is **per record** and travels inside the file: stage verification stays at the build, per-record trust is checked at the read, and the alias is a transport rather than a claim.

## Ruling 4 — `guidelines_recs.py --json` refuses a stem that does not start with `recs-`, globally, before the PDF is opened

The check sits immediately beside `ensure_outside_checkout` at `guidelines_recs.py:663-671`, for the reason already written there: where the JSON lands is a question about the arguments alone, and an 18-second read should not be spent to earn a refusal. Same exit 1, same door.

**Global rather than scoped to the recs root.** Scoping would make the producer resolve `CLINICAL_GUIDELINES_RECS` to learn which directory it is writing into, and the only workflow a global rule inconveniences is *write a comparison record somewhere else*, which becomes one character of friction and a better destination anyway — a verification artifact has no business in the directory a lookup scans.

**One direction of the claim is bought and the other is not, and that asymmetry is the ruling rather than a caveat.** After this, *everything this producer writes wears the prefix*. It remains false that *everything wearing the prefix came from this producer* — `recs-sweep.json` is the standing counter-example and no producer-side check can ever reach it. So ADR 0034 ruling 5's hint scan keeps its job: the prefix becomes a claim the producer **guarantees it makes**, never a claim only the producer **can** make.

**A conforming-but-wrong name is not caught here and is not meant to be.** `recs-anything.json` is owned at the read: ADR 0034 ruling 2 checks the record's `source` against the document and refuses a mismatch, and ruling 5 names it as a hint. That is the read side owning what the write side cannot see.

## Ruling 5 — the alias manifest tells four absences apart, and none of them refuses at a read site

Once the sweep exists, ADR 0045 ruling 3 gives all 179 documents a record — including the 19 that yield nothing, which declare themselves. So *no record* for a corpus document can only be one of four events, and today they are one message:

| | what happened | remedy |
| --- | --- | --- |
| a | the alias directory is absent — no sweep on this machine | run the build |
| b | the manifest lists the document and the file is not there | the artifact is damaged; rebuild |
| c | the manifest does not list it — the sweep predates the PDF | rebuild |
| d | it is not a corpus document | the recs root, exact name, as today |

Each gets its own named reason, and the reason rides beside ruling 2's root name so one line says both *which root answered* and *why the better one did not*. The discriminator costs nothing new: the manifest already survives publication and this reader already consumes the extraction alias's copy of it.

**Refusal stays at the build layer, and that follows from ruling 3 rather than being a fresh call.** `threshold_sheet.py --all --quiet` runs inside `git commit`; refusing on **b** or **c** blocks a commit for machine state the commit never touched, and **c**'s only remedy is 56 minutes of CPU. `guidelines_build` already owns damage — it quarantines and re-hashes — and a read site that refuses on a damaged alias is a second, weaker copy of a check that already exists somewhere with the power to repair it.

So **b** falls back to the recs root like the others, loudly and named — which is strictly better than today, because the fallback yields a **graded** sheet where the present behavior yields `NOT RUN`.

## Ruling 6 — the build splits, and the producer half lands first and independently

`bind_recs` and `_record_path` now have four changes queued against them: ADR 0034's exact-name rewrite ([#456](https://github.com/mshamblin5150-code/clinical-skills/issues/456)), ADR 0030's trust reader ([#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438)), ADR 0045 ruling 2's document lookup, and ruling 2 above's root reporting. ADR 0034's own Consequences already say *"two green branches there produce a red merge."*

**Ruling 4's refusal is not on that seam at all.** It touches `guidelines_recs.py`'s argument handling and nothing else, so it can neither collide with those three nor wait behind them. It is also the ticket's **title** — the convention held by nothing — and the only half that repairs something live today, in the one directory that has demonstrably produced an off-convention record while tickets were in flight in it.

**The alias half waits, and not only for hygiene.** A lookup against a directory nothing writes is dead code. It is *testable* without #510 — every recs test in the tree builds a synthetic root in a temp directory — but it cannot be *exercised*, and it would be the fourth change to the contested seam rather than the last.

**The two ADRs' ordering clauses reconcile, and read like a conflict until they are put side by side.** ADR 0034 says landing itself first is the cheaper order **against #438**; ADR 0045 says #438 lands first **against #510**. One chain satisfies both: **#456 → #438 → #510 → #518's reader half**, with #518's producer half beside it and outside the chain.

**One thing the split hands back.** `CLAUDE.md` records that `test_build_artifacts_ignored.py` types `recs-<source key>.json` by hand *"because `guidelines_recs.py` has no default `--json` path to derive from"*, and names the consequence — [#177](https://github.com/mshamblin5150-code/clinical-skills/issues/177) renamed that convention with the check green throughout. Once the producer holds the prefix as a constant, the name becomes **derivable from the producer**, which closes the staleness that paragraph declares and cannot presently close.

## Ruling 7 — `recs-sweep.json` is preserved permanently on a ground the ticket does not state, and `verify-recs-htn.json` is deletable when #456 and #518 close

#518's decision 3 says of both files that the preservation reasoning *"is about the tickets, not about the directory, and it expires when they close."* **That is true of one of them.**

**`recs-sweep.json` never becomes re-derivable again.** ADR 0045 established that it is the pre-[#173](https://github.com/mshamblin5150-code/clinical-skills/issues/173) mode census, that it reconciles cell by cell against `reference/thresholds/README.md:504`, and — in that record's words — that *"the reader that produced it no longer exists. A sweep command retires one of those figures and cannot retire the other."* Its preservation reason is not an open ticket. It is an irreproducible measurement, and it does not expire.

**Moving it is refused, and moving is the tempting option.** It is the one file in the directory wearing a prefix it cannot honour, and it will be named as a non-record on every failed lookup once ADR 0034 ruling 5 is built. Moving it out would break the path a reader re-derives ADR 0045's census table from, which is the same class of act as deleting it; the noise bought back is one named line that ADR 0034 already priced and accepted.

**`verify-recs-htn.json`'s reason does expire.** It is a genuine record duplicating three others — same PDF, same `exact` mode, same 103 recommendations, `doc_id` alone differing — and its whole evidentiary value is being the fourth record #456's matcher could not see. When #456 and #518 both close it is **deletable and not renameable**: a conforming stem would put a fifth resolvable-shaped record for one PDF into the directory, which is the ambiguity this whole chain exists to remove. Deletion is the clinician's word per file; the trigger is recorded here so it is not rediscovered.

**After ruling 4 it acquires a property worth writing down: it becomes a file no tool in this repo can produce.** That is the producer refusal visible on disk rather than only in a message.

## What this does not reach

- **Whether a resolved record is right about the guideline.** Ownership, identity and resolution answer *which file and which document*. Whether `find_tables()` read the page correctly is [#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446)'s and stays there.
- **A record whose `source` is absent or unparseable.** It matches no document, so it can be neither resolved by document nor refused as belonging to another — ADR 0034's declared floor, inherited whole.
- **A read site built by indirection.** The producer check is keyed on the `recs-` literal and the read sites on a path constant, so a name or a path assembled at run time passes unseen. A floor on the shapes in the tree, inherited from ADR 0030's ceiling and ADR 0045's widening of it.
- **A file wearing the prefix that this producer did not write.** Ruling 4 buys one direction only, and `recs-sweep.json` is the standing instance.
- **Whether the alias a read site opened is the build's.** Ruling 3's declared limit: the published copy carries no `artifact.json`, so stage verification is not re-checkable at the read. Per-record trust is what travels.
- **The nine non-records in the recs root.** ADR 0034 ruled that naming them on every refusal is a report whose loudest line is the machinery working. Unchanged.

## Rejected options

**Retire the naming convention and resolve by document everywhere.** Rejected on the four AHA records: it imports `matches[0]` back into the directory ADR 0034 removed it from, one day after removing it.

**Let the recs root win over the alias.** Rejected on the measurement — five of five committed sheets overlap, so it shadows the verified artifact for every document anybody has worked on, permanently and silently.

**Consult both and refuse where they disagree.** Rejected: it deadlocks on day one, refusing all five, and ADR 0030 and ADR 0034 both forbid the only cheap remedy while #456 and #518 are open.

**Have the read sites query the build catalog.** Rejected on `tools/hooks/pre-commit:52` — no *verify or return nothing* selector exists, and the one that does builds on a miss, inside `git commit`, for 56 minutes.

**Publish the alias into the recs root.** Rejected: a second naming scheme in the directory ruling 1 has just fixed at exact-name. Distinct from ADR 0045's rejected per-topic aliases, and rejected for a different reason.

**Scope the producer refusal to the recs root.** Rejected: it couples the producer to `CLINICAL_GUIDELINES_RECS` to buy back a workflow that is better served by writing to a scratch directory.

**Derive the filename in the producer.** Rejected on ADR 0045's measurement: a source key is topic-scoped, 157 of 179 catalog rows disagree between the two scopes on whether to suffix, and the producer does not read the catalog.

**Refuse at the read site on a damaged or stale alias.** Rejected: it blocks commits on machine state the commit did not touch, and duplicates a check the build layer already owns with the power to repair.

**Land #518 as one change.** Rejected: it holds the producer door open through three `ready-for-agent` tickets working in that directory, and adds a fourth branch to a seam already flagged red-merge-prone.

**Move `recs-sweep.json` somewhere it stops wearing the prefix.** Rejected: the same class of act as deleting it, against a noise cost already priced.

## Consequences

**The first run after the sweep lands re-grades every committed sheet against different bytes.** Ruling 2's per-source root naming is what makes that visible rather than silent, and it is the reason that reporting is a ruling and not an ergonomic.

**`threshold_sheet` gains a second lookup root and no new dependency.** It already imports four modules from this family and consumes a published alias by path; ruling 3 adds a path, not a coupling.

**`guidelines_recs.py` gains its first constraint on `--json` beyond placement**, and with it a constant `test_build_artifacts_ignored.py` can derive rather than retype.

**Three open tickets still collide at `bind_recs` and `_record_path`, and the tracker records it in one place only.** ADR 0034 ruling 6 claims *"both bodies carry the collision"*; #510's sweep comment measured that false — this body and #438 mention each other zero times. Ruling 6's chain is the resolution, and it is owed to #438 and #456 as much as to this ticket.

**ADR 0045's *"until #518 lands the artifact is verified and unread"* is now split.** The producer half lands without making the stage reachable; the reader half is what discharges that sentence, and it is blocked on #510 rather than merely ordered after it.

## Addendum, 2026-08-27 — what the exhaustive sweep changed, hours after ratification

The sweep this record's own session ran — 47 open tickets, eight independent readers, every ticket
getting a verdict rather than the ones whose titles looked related — found **six** things about this
record and the change that carried it. Five are corrections in place on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms. None moves a ruling.

**8. Ruling 4 is a fifth invalidator of the `recs` cache stage, and this record said the opposite
shape of thing.** Ruling 6 argues the producer half *"touches `guidelines_recs.py`'s argument
handling and nothing else, so it can neither collide with those three nor wait behind them."* That is
true of the `bind_recs`/`_record_path` **seam** and silent about **cache identity**. ADR 0045 ruling 1
puts `_code_inputs` over the producing modules into the stage key, and every existing
`artifact_provenance.CACHE_IDENTITY` entry is a tuple of module paths — so a `recs` stage naming
`tools/guidelines_recs.py` is invalidated by any edit to it, including this one. ADR 0045's own
Consequences enumerates *"four open tickets each invalidate the whole stage once it exists, at roughly
56 minutes apiece"* — #434, #436, #446, #502. **This ticket's producer half is a fifth, and neither
record names it.** The ordering claim survives unchanged, because the two costs are different
questions: seam contention is about a red merge, stage identity is about CPU. Landing ruling 4 before
#510 costs nothing at all, since the stage does not exist yet to be invalidated — which is a further
argument for ruling 6's split rather than against it.

**9. The Consequences paragraph falsified the right claim with the wrong pair.** It reads *"ADR 0034
ruling 6 claims 'both bodies carry the collision'; #510's sweep comment measured that false — this
body and #438 mention each other zero times."* ADR 0034 is the record ruling [#456](https://github.com/mshamblin5150-code/clinical-skills/issues/456),
so *both bodies* means **#456 and #438**, not #518 and #438. Re-derived at `d3b59bc`: #456's body
matches `#438` **twice**, #438's body matches `#456` **zero** times. So the claim is false, and it is
false for a reason the cited measurement does not establish — the correct evidence is #438's body
being silent about **#456**. The inherited error came from #510's sweep comment, which measured its
own pair. **The conclusion stands and the evidence is replaced.**

**10. Ruling 6's chain is incomplete against [ADR 0032](0032-the-marker-limb-reads-the-repaired-text-the-other-two-limbs-declare-that-they-do-not-and-every-citation-gate-reads-one-reader.md)
ruling 4, which this record does not cite.** That record fixes *"Order: **#446, then #438, then
#436**"*. Ruling 6 fixes `#456 → #438 → #510 → #518's reader half` and names #446 once, in *What this
does not reach*, on an unrelated point. **The two do not contradict** — both put a predecessor before
#438 and they compose as `{#446, #456} → #438 → #510 → #518's reader half` — but a builder reading
only this record lands #438 with #446 unbuilt, which is the outcome ADR 0032 ruling 4 exists to
prevent. #446, #456 and #438 are all open and `ready-for-agent`, so the hazard is live. The chain as
stated in ruling 6 should be read with #446 beside #456, and that is a correction to a **statement of
somebody else's ordering** rather than to an ordering this record owns.

**11. `CONTEXT.md`'s new **Lookup root** term forbade the name this record uses seventeen times.** Its
`_Avoid_` line listed `recs root`, while this record uses *recs root* as the proper name of one of the
two roots throughout. The `_Avoid_` was meant to forbid it as a name for the **concept** and read as
forbidding it for the **root it genuinely names**. Narrowed. **Sweep alias**, this record's other
proper name, had no glossary entry at all and now has one. That is the class ADR 0041's *What no row
reaches* declares unreachable — *"nor does anything compare a definition to the ADR that contributed
it"* — with a live instance produced in the commit that coined the term.

## The record produced two instances of open tickets inside one hour

**[#530](https://github.com/mshamblin5150-code/clinical-skills/issues/530) — the merge bound
nothing.** PR #557 merged this record at `d3b59bc` with a body that says *"Ratifies the grilling of
#518"* in prose and carries no `Part of #518` line, so `tracker_merge_receipt.REFERENCE` matches
**zero** bindings across the body and every commit message, and **#518 carries no merge receipt for
the record that rules it.** The omission shape, third consecutive ratification merge to do it, and the
third time a sweep has produced its own instance. Recorded rather than repaired: the receipt job fires
at merge and there is no second merge to attach one to.

**[#554](https://github.com/mshamblin5150-code/clinical-skills/issues/554) — the glossary edit moved a
cited coordinate.** Inserting **Lookup root** moved `CONTEXT.md`'s **Orphaned figure** from `:376` to
`:380`, breaking that anchor in the newest comments on #496 and #529 — one of them written the same
morning while flagging the previous `:364` as a #554 instance. `git show f758c0b:CONTEXT.md | grep -n
"^\*\*Orphaned figure\*\*"` against the same command at `d3b59bc` re-derives it. **A line-number
citation into a file the next commit appends to is not a stable coordinate**, and this is the cheapest
demonstration of it the thread has: the drift was caused by adding a paragraph, not by editing one.

*Addendum written 2026-08-27 on the branch that carries it. Rulings 1–7 and the sections above them
are left exactly as ratified; rows 8–11 are corrections in place under ADR 0016 and say so where they
sit.*

*(Corrected in place 2026-08-28, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s terms. The ADR 0016 link before correction row 8 named a filename absent from the index; its target now uses the record's tracked filename. No ruling changed.)*
