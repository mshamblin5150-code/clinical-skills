# A read-once cache of a committed reference file gets a public reset and a declared limit and the pattern is not generalized

[#883](https://github.com/mshamblin5150-code/clinical-skills/issues/883) asked whether a latent,
unreachable staleness is worth a seam. It is one of two process-lifetime caches of a committed
`reference/` file in `tools/`, and the ticket's framing — *two facts do not compose into a defect
until something joins them* — turned out to be the right instrument pointed one level too high. The
join is inside `guidelines_recs.py`, not one import away.

## Measured before ruling, at `966d966`, re-derived after merging `e1a37c5`

`main` advanced mid-session. Every figure and line reference below was re-derived against the
merged tree; `guidelines_recs.py` and `cdc_percentile.py` were untouched by that merge and
`test_guidelines_recs.py` moved by one line, which is why its references are not the ones the
#883 ruling comment carries.

**The cache.** `tools/guidelines_recs.py:1199` holds `_CURATED_CACHE`, populated once in
`curated_rows_for` at `:1227` and never invalidated. What it caches is the parsed contents of
`reference/guidelines-uspstf.md`, a member of `artifact_provenance.TRUST_FLOOR["recs"]`,
`artifact_provenance.CACHE_IDENTITY["recs"]`, and `guidelines_recs.RECORD_TRUST_FLOOR` under
`SOURCE_CURATED_TABLE`. It is written by `tools/uspstf_table.py`, whose `DEFAULT_OUT` at `:58` is
that path.

**The join, which the ticket did not have.** `_record` at `:1307` stamps
`record_producer["inputs"] = artifact_provenance.producer_file_identity(RECORD_TRUST_FLOOR[floor_key])`,
which for `curated-table` hashes `reference/guidelines-uspstf.md` **off disk at write time**. The
`recommendations` in that same payload came from `_CURATED_CACHE`, parsed at first call. **The
stamp and the rows read the same file at two different moments, and nothing makes those one read.**
So the record's identity can certify bytes its contents did not come from. It still takes an
external writer to make the bytes differ, so the ticket's *latent, not live* verdict stands — but
the mechanism is one function call away rather than one import away, and that is what priced the
seam.

**The test seams, which do not all want the same thing.** Four sites in
`tools/test_guidelines_recs.py` touch the private global, and they split two ways. `:1308` and
`:1324` assign `None` to force a re-read of the committed table: those want a reset. `:648`
installs a synthetic parsed table so the precedence tests run against invented rows, and `:1339`
installs a hand-built two-key dict to reach the case-collision refusal: those want an injection. The
ticket's option 2 — *give the module the reset the test suite already needs* — therefore buys half
of what it claims. A reset removes two pokes and leaves two.

**Both injection sites carry recorded reasoning for being deliberate.** The comment at `:644` says
that passing rows into `extract` would test the injected value rather than the precedence, and the
docstring at `:1339` says the case collision is unreachable against the committed table and must be
synthesized. Read against the stamp finding above, those are not a module missing a seam. They are
tests reaching for something the production path must not offer.

**Where a declared limit is allowed to live.**
`test_guidelines_recs.py:904` reads the module docstring and `CLAUDE.md` and asserts each names
`guidelines_recs.DECLARED_LIMITS` while carrying no row's key and no row's limit sentence. So the
ticket's option 3 — *say so in the docstring* — has no form that is both legal and durable: as a
registry row's sentence it turns the suite red, and as prose alone it is the shape
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) records as insufficient
because a prose edit to a limit fails nothing.

**The second cache, and the asymmetry the ticket did not have.** A sweep of all 176 `.py` files in
`tools/` finds exactly one `global` cache and exactly one `functools.lru_cache`, and both cache a
committed `reference/` file. The ticket's fourth consideration — that this is the **only** such
cache, so the ruling is the tree's standing answer on the pattern — is false as written.

| | `guidelines_recs._CURATED_CACHE:1199` | `cdc_percentile.load_chart:106` |
| --- | --- | --- |
| caches | `reference/guidelines-uspstf.md` | `reference/cdc-bmi-for-age-2022.csv` |
| in a `TRUST_FLOOR` | yes, `["recs"]` | no, in none |
| written by a tool here | yes, `uspstf_table.py` | no; the only `tools/` reference is `DEFAULT_CHART:34`, and the file is downloaded byte-for-byte from CDC and committed |
| public reset | none | `load_chart.cache_clear`, free from the decorator, called nowhere in the repo |
| consumer critical path | maintainer-only | yes — `AGENTS.md` runs it from `clinical-note` and `icd10-cpt` |

## Ruled 2026-09-04

### 1. The seam is a public reset, and injection stays private

`guidelines_recs` gains a public `reset_curated_cache()`. `:1308` and `:1324` call it. The two
injection sites keep reaching for the private name, and their existing comments are what justifies
that.

**The declined option is a single settable accessor** — `set_curated_table(rows | None)`, `None`
meaning re-read — which was the first ruling of this session's grilling and was reversed by the
stamp finding. It removes all four pokes, and it also gives any importer a public path to put rows
into a record whose stamp certifies a trust-floor file those rows never came from. A reset cannot
do that: it forces a re-read of the real file, which strictly reduces the divergence. **The
injection seam is not missing; it is withheld**, and the difference is what a caller would be able
to certify with it.

Documenting a settable accessor as test-only was refused on this repository's standing ground that a
written instruction cannot fail.

### 2. The limit is a registry row phrased as a coverage claim, not prose

`DECLARED_LIMITS` gains one row, `curated-table-read-once`, carrying
`EvidenceDisposition.BEHAVIOR`. It is phrased as what a run fails to establish rather than as how
the code is built, which is the register every existing row is written in — `nothing-found-is-not-negative`
and `ownership-does-not-prove-content` are the two closest.

**An implementation note was declined.** *The parsed curated table is cached for the life of the
process* is legal and is the wrong register: every row in that registry states what a scan does not
establish about a document, and a cache lifetime is a property of the process. Stating the limit as
a coverage claim keeps the registry's meaning and has the further property of staying true whether
or not any writer is reachable, so it does not have to be revisited on the day the join goes live.

**`DECLARED_READING` was declined.** No reader owns this and nobody is being asked to check it.
`BEHAVIOR` is provable today despite the staleness being unreachable, and the control is the stamp
finding made executable: rewrite `reference/guidelines-uspstf.md` between `curated_rows_for` and
`_record`, then assert the stamped `inputs` identity and the returned rows disagree. That proves the
mechanism is live without claiming the harm is.

### 3. The ruling binds `guidelines_recs` alone, and `cdc_percentile` is not a precedent

No pattern is stated. `cdc_percentile.load_chart` is untouched, and this record carries the table
above so the next reader starts from the measurement rather than re-deriving it.

**The join is present for one cache and absent for the other.** Nothing in this repository writes
`reference/cdc-bmi-for-age-2022.csv`; refreshing it is a person replacing a committed file, which is
a new process. It is in no trust floor, so no record's identity is computed from its bytes.
Extending the ruling to it would be asserting a rule against a workload nobody has measured — which
is the error [#883](https://github.com/mshamblin5150-code/clinical-skills/issues/883) was filed to
prevent, committed on the second instance, inside the ruling that cites the first.

**And the free `cache_clear` makes the generalization cheap in a misleading way.** A rule reading *a
process-lifetime cache of a committed reference file gets a public reset* would be satisfied at
`cdc_percentile` on the day it was written, by a decorator rather than by anyone acting on it. A
pattern one of its two members satisfies by accident is not evidence the pattern was adopted.

**What that leaves unstated is named rather than hidden.** `cdc_percentile` is the one of the two on
the consumer critical path, so if this shape ever bites clinically it bites there. This record
carries the table for that reason.

### 4. The stamp-follows-rows fix is named and not built

The fix that would end the subject rather than declare it: have the cache hold the file's `sha256`
beside the parse, and have `_record` stamp that rather than re-hashing at write time. The stamp then
follows the rows, injection stops being able to certify anything false, and ruling 2's row becomes
false and is retired.

**It is not built.** It is a mechanism against a workload nobody has measured on a path nobody can
reach, which is what [#871](https://github.com/mshamblin5150-code/clinical-skills/issues/871) ruled
against and what ADR 0127 refused for a git answer one artifact over. It is written down here so
that the day something joins a writer of the curated table to a reader of the cache, the remedy is
already priced and the next session does not re-derive it.

## What this record does not settle

**Whether the join stays absent.** The check is the join and never the shape: if `uspstf_table` ever
imports `guidelines_recs`, or any other writer of the curated table becomes reachable from a reader
in one process, ruling 4 is the day's work and ruling 2's row is retired.

**Whether a record that declares no rulings is a defect or a second accepted spelling.** Found while
measuring for this record, and it is two shapes rather than one. `RULING_HEADING` is
`^ruling\s+(\d+)\b`, so `## Decision N` headings declare nothing — ADRs 0126 and 0127.
`RULING_ITEM` is `^(?:\*\*)?(\d+)\.\s`, which expects a digit where those records write a word, so
`**Ruling 1. …**` under `## What is ruled` also declares nothing — ADRs 0094 and 0096. **Writing the
word `Ruling` into the item form is what breaks the item form**, while writing it into an H2 is what
makes the heading form work, and the two failures look nothing alike from inside either record. Of
the 22 records declaring no ruling, those four are the recent ones; the rest are 0001–0022 and 0037,
which the parser's own comment says place their list under the H1.

It is latent: nothing cites any of the four by ordinal today. It would go live on the first
citation, because `RULING_CITATION` accepts `decision` as an ordinal word — so the natural way to
cite one is unresolvable, against a ceiling of 2 with one slot already spent. This record therefore
refers to ADR 0127 without an ordinal deliberately. Filed as
[#886](https://github.com/mshamblin5150-code/clinical-skills/issues/886) rather than folded in here,
because it has nothing to do with this cache and it carries a decision of its own.

**Whether the two injection sites should ever become public.** Ruling 1 withholds the seam on what a
caller could certify with it. If ruling 4 is ever built, that objection dissolves and the question
is open again.
