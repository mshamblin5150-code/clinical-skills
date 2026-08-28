# A recommendation record is resolved by exact name at both read sites and the directory scan hints rather than selects

[#456](https://github.com/mshamblin5150-code/clinical-skills/issues/456) recorded two silent behaviors where `tools/threshold_draft.py` picks the recommendation record a threshold sheet is drafted from: an unreadable candidate dropped with no count printed, and `matches[0]` choosing between several records that name one PDF with nothing saying which. Grilling it on 2026-08-25 found both claims true, a third and a fourth silent behavior at the same seam that the ticket does not name, and the ticket's own headline count produced by the matcher the ticket is about.

The clinician ruled on 2026-08-25.

1. **The directory scan discovers and never selects.** `_record_path` resolves `recs-<key>.json` by exact name and stops. Where that does not resolve, the run refuses and names any record on disk built from the same PDF as a hint — *you built this, it is under the wrong name*. The glob's ergonomic is kept; its vote is removed.
2. **A record under the expected name that was built from another PDF is refused, per source.** The comparison moves out of `_record_path`'s inline fall-through into `guidelines_recs.py` as one object both read sites import, taking *the PDF filename this source names* as an argument: the drafter supplies it from the catalog row, the gate from the sheet's `document` cell. One rule, two callers, and no test claiming they agree.
3. **The hint scan counts and names what it could not read**, distinguishing *would not parse* from *parsed and is not a record*, which `threshold_sheet.bind_recs` already distinguishes for its own reader.
4. **The denominator is owed where the scan runs and nowhere else.** A successful draft resolves one file by name and reads no population, so it declares nothing; a directory census on a run that never consulted the directory is a figure about nothing.
5. **The scan's population is every `*.json` in the recs root**, and its report splits three ways: records built from this PDF are named as hints, the remainder is counted, and a non-record is named **only when its filename claims to be one**.
6. **This is separate from [#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438) and does not fold into it**, and both bodies carry the collision. [#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446) does not interact.

## The defect the ticket was filed over is not the expensive one

#456's two behaviors are both about *choosing between candidates*. Two more live at the same seam and neither is about choosing.

**The drafter computes whether a record is about the right document and then discards the answer.** `_record_path`'s fast path loads `recs-<key>.json`, compares the PDF filename inside it against the catalog row's, and on a mismatch falls through to the glob. Where the glob matches nothing it `return expected` — the file it has just rejected — and `resolve_sources` loads it, finds it parses, and drafts from it.

Measured by putting the ADA diabetes record into a directory under the name `recs-aha-2025.json` and drafting hypertension:

```
sheet key      = aha-2025
sheet document = AHA ACC/jones-et-al-2025-...-prevention-detection
sheet mode     = bound                     <- lifted from the ADA record
record source  = standards-of-care-2026.pdf
record recs    = 126                       <- ADA's, not AHA's 103
errors         = []                        <- exit 0
```

Every threshold row in that draft is cited to the AHA/ACC hypertension guideline and read out of the ADA standards of care. That is a fabricated citation produced by a clean run, and it is the failure this repo's whole citation apparatus exists to make impossible.

**The sibling read site already refuses it.** `threshold_sheet._record_built_from_another_document` compares the record's `source` filename against the sheet's `document` cell, refuses, names the hazard in its own docstring, and is pinned by `test_a_record_built_from_another_document_is_refused`. So the rule was already written down and already tested; the drafter holds a second implementation of it whose only consumer is a filter it falls through.

**And the key printed into the sheet is not the file that was read.** With `recs-aha-2025.json` removed from a copy of the directory, drafting hypertension reads `recs-aha-htn-2025.json` by `matches[0]`, stamps the sheet's `## Sources` row with key `aha-2025`, and exits clean — after which `threshold_sheet.bind_recs`, which resolves `recs-<key>.json` by exact name with no glob and no fallback, looks for a file that is not there. Ruling 1 closes that by construction: with one resolution rule at both sites, the drafter and the gate cannot come to read different files.

## What was measured

Every figure was re-derived on `0c39452` with the freshness gate reporting `FRESH`, before the ruling.

**The ticket's evidence re-derives exactly.** `recs-aha-2025.json`, `recs-aha-htn-2025.json` and `recs-hypertension.json` name one PDF, report 103 recommendations across 27 tables, are byte-identical at `sha256 8feeb203d831...`, and none carries `counted_from`. `recs-sweep.json` still fails `_load_record` on every run with nothing printed.

**`recs-sweep.json` is not a malformed record.** It is a JSON list of 179 rows shaped `["ACIP/Recommended Vaccinations for Adults...", "none", 0]` — a corpus-wide mode tally. Nothing in `tools/` writes it. `guidelines_recs.py --json` accepts any path it is given, so `recs-<key>.json` is a convention the two readers hold and no producer enforces, which is why the live instance of *unreadable record* is a different artifact wearing the prefix.

**There are four records built from the AHA PDF, not three.** `verify-recs-htn.json` is a genuine record — same source, `mode: exact`, the same 103 recommendations across 27 tables — differing from the other three only in `doc_id`, the full document stem rather than `AHA ACC/jones-et-al-2025`, which accounts for its whole 10 KB of extra bytes. It does not match `recs-*.json` and no instrument in the ticket has ever seen it. **The ticket's headline count was produced by the matcher whose partial coverage is the ticket's subject**, which is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s shape arriving inside the ticket about it, and it is the single strongest argument for ruling 5.

**Widening the scan costs nothing that can be felt.** The recs root holds 17 `*.json` files, 1,690,831 bytes, parsed in **14 ms**; **eight are recommendation records and nine are not.**

*(Corrected in place 2026-08-26, on [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s terms. This read `seven … and ten`. Re-derived with `_load_record`'s own predicate — a dict carrying a list `recommendations` — the split is **8/9**, and the byte count is unchanged to the digit, so the directory had not drifted and the original figure was taken with the `recs-*` glob **this record is about**. The eighth is `verify-recs-htn.json`, which is the file this record's own headline names as the correction. The ruling is unaffected — the cost argument survives, and survives the recursive widening too: 66 files, 56 records, 51 ms. Found by the exhaustive tracker sweep on [#495](https://github.com/mshamblin5150-code/clinical-skills/issues/495).)*

**Ruling 2 refuses nothing correct that exists.** All five source keys declared by the four committed sheets pass `_record_built_from_another_document` against their sheets' `document` cells, and every readable record on disk resolves to a real catalog row — including the two AHA orphans and `verify-recs-htn.json`. The only file that fails is `recs-sweep.json`, and it fails for being a JSON list rather than on the comparison.

**The glob is reached by no committed sheet today**, so ruling 1 costs nothing at present. That was re-derived through `threshold_sheet.parse` rather than by an `awk` range over `## Sources`, because `prediabetes-type-2-diabetes-screening.md` declares two source keys and a per-sheet range undercounts it — the same instrument error [ADR 0030](0030-a-recommendation-record-is-owned-like-every-other-artifact-its-trust-floor-is-keyed-on-the-limb-that-built-it-and-the-drafter-takes-no-escape-hatch.md) records correcting in itself.

**Neither #438 nor #446 has been built.** `artifact_provenance.TRUST_FLOOR` carries no `recs` key and `grep -c "artifact_provenance\|allow_untrusted" tools/guidelines_recs.py` is `0`.

## Considered options

**Keep the glob and make it honest** — print the candidate count, name the file chosen, and carry the chosen *filename* into the sheet's `key` so the gate follows the drafter. Rejected. It keeps the ergonomic at the price of making a sheet's source key whatever a build artifact outside every checkout happened to be called, so the committed sheet's identity would be set by a filename in a directory eleven worktrees write.

**Delete the glob outright.** Rejected as the whole answer rather than as wrong. Both read sites would resolve by exact name and could never disagree, which ruling 1 keeps — but the discovery is the one thing the glob is genuinely good at, and the person it helps is the person drafting a **new** topic, who has no sheet to read a key off and cannot predict the derived one. Refusing with *the record is here under the wrong name* costs a rename; refusing with *no recommendation record at this path* costs a search.

**Report a name mismatch as a missing record**, reusing the absent-file message. Rejected: it says the file is missing while the file is sitting there, which is the message a reader acts on wrongly.

**Leave the name mismatch alone and let the filename win.** Rejected on the measurement above. It is the branch that drafts a sheet citing one society out of another's guideline, at exit 0.

**Keep the scan at `recs-*.json` and declare the limit.** Rejected, and this is the one place this record departs from the standing preference for declaring coverage over widening an instrument. That preference was ruled where the widening bought less than it looked like — [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s untracked files, [#141](https://github.com/mshamblin5150-code/clinical-skills/issues/141)'s name count. Here the widening was priced at 14 ms and it finds a real fourth record on disk today, which is [#275](https://github.com/mshamblin5150-code/clinical-skills/issues/275)'s refinement rather than a departure from it: **declare the limit you are keeping, and fix the hole you actually named.**

**Widen the population and name every non-record.** Rejected. Ten of seventeen files in that directory are not records and never were, so naming them on every refusal is a report whose loudest line is the machinery working, and *the same as last time* is the only reading anybody takes off one. That is `symbol_glyph_census`'s exclusion of glyphs already in its own replacement table, and ruling 5's split is that exclusion keyed on the `recs-` prefix: a file wearing it makes a claim the scan can check, and a file that is not wearing it makes none.

**Fold into #438.** Rejected. ADR 0030 spends a paragraph separating *what the scan may read* from *which candidate it picks*, and the separation is right. Folding also un-specs a `ready-for-agent` ticket carrying a full record.

**Delete `recs-sweep.json` or rename `verify-recs-htn.json` while doing this.** Rejected on ADR 0030's own delete-nothing reasoning, which named #456 as one of the two reasons it preserved the AHA orphans. Both files are now this record's evidence, and tidying them closes the ticket by accident and removes what a reader re-derives it from.

## What this does not reach

- **A record whose `source` key is absent or unparseable matches no PDF, and no scan reaches it.** It cannot be offered as a hint and cannot be refused as belonging to another document, because there is nothing to compare. That is the declared floor of both ruling 2 and ruling 5.
- **A record that resolves, is about the right document, and is wrong about the guideline** is untouched here. Ownership and identity answer *which file and which document*, never whether the extraction read the page correctly, which is #446's subject and stays there.
- **The producer enforces nothing.** `guidelines_recs.py --json` writes to any path, so the convention both readers depend on is held by neither of them and by nothing else. Filed rather than fixed here; both off-convention files on disk came through that door.
- **A read site built by indirection is invisible**, inherited from ADR 0030's own ceiling: the check is keyed on the `recs-` filename literal, so a path assembled at run time passes unseen. It is a floor on the shapes in the tree.

## Consequences

`threshold_draft` gains a refusal it did not have, and the only records on disk it would refuse today are ones no sheet resolves. No committed sheet reaches the changed branch, so nothing needs re-drafting to land this.

**`_record_path` and `guidelines_recs.py` are edited by two ruled-and-unbuilt tickets.** ADR 0030 ruling 7 puts a trust reader into `guidelines_recs.py` that both read sites import and rewrites `_record_path` into a two-tier read; ruling 2 here puts a second shared object into the same module and rewrites the same function. Whichever lands second re-runs the other's tests rather than trusting a green branch — `anchor_scan` against [#150](https://github.com/mshamblin5150-code/clinical-skills/issues/150) is this repo's record of neither branch's suite being able to see the break.

**Landing this first is the cheaper order, and nothing enforces it.** Ruling 1 leaves the scan selecting nothing, so ADR 0030's *untrusted peek that returns only a filename match* becomes advisory by construction rather than by careful wording, and trust is checked on a single unambiguous target. In the other order, #438's builder wraps a selector in a peek and this ticket's builder then deletes the selector.

**ADR 0030's rejected option gains a weaker premise and keeps its ruling.** *Trust-check the resolver's directory scan too* was refused because a strict read there makes one stale neighbor a hard failure for every topic. With a hint-only scan that premise no longer holds — a stale neighbor in a hint list is a hint you ignore — and the ruling still stands, because the answer a hint needs from an untrusted record is still only ever a path.
