# The clinician's evidence dumps are his own research and the store membership rule stands on checkability

**Measured at:** f20dd5b9718c6b0e6401a5fa3ceabeaa0c26d44d

[#1505](https://github.com/mshamblin5150-code/clinical-skills/issues/1505) was filed from the
after-action review of a `peer-critique` run (NUR 5144 Module 2) on 2026-10-01. Research and
refutation agents called the clinician's own UpToDate compilation "faculty-supplied" or "the faculty
dump", and a heading reader returned `CONTEXT-VERDICT: agrees` on that attribution because the dump's
topic list "confirmed the faculty supplied the topics". He compiled those topics himself; they were
part of his own submission. Grilled 2026-10-11 against `main`; the clinician ruled every point below
in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**No dump on record was handed over by the faculty.** Every UpToDate compilation the account holds,
on disk and in the **Evidence store**, is the clinician's own, and his 2026-10-01 correction says so.
The **Dump manifest** records module and date and has no field naming who supplied a dump.

**The membership row's stated ground is false for every dump.** `research_ledger.py` refuses an
UpToDate citation no accumulated manifest carries. `skills/practicum-case-study/SKILL.md`, the
research-ledger section of `CLAUDE.md`, and [ADR 0132](0132-the-uptodate-store-is-scratch-rooted-and-its-published-topic-sheets-carry-the-entitlement.md)
ground that row in "companion evidence" being "the required supplied-source set" of "faculty
material the clinician supplied".

**The row's checks need the stored copy.** The masthead, author-order, author-count, last-update
year, and literature-review currency rows all read the filed topic body, so a cited topic outside the
store escapes every one of them.

**[ADR 0332](0332-case-material-and-case-research-are-declared-context-places-and-both-libraries-come-first.md)
already changed what the store holds.** Its ruling 4 files every topic a run pulls through the
clinician's UpToDate account as a supplement dump, and `CONTEXT.md` now defines **Case research** as
his own dump, "never faculty-supplied". The store is his compilations plus his account's pulls.

**The drafting instructions already carry half of the provenance rule; the reader does not.**
`skills/_shared/reference/sourcing.md` tells the drafter that a document's self-description "is not
evidence of who wrote it, for whom, or what organization or program it covers". The heading reader's
brief in the same file says nothing about provenance, and the heading reader is the step that failed.

**The false framing sits in live files and in three ratified records.** At the measured commit the
live files are `AGENTS.md`, `CLAUDE.md`, `reference/uptodate/README.md`,
`skills/_shared/reference/apa7.md`, `skills/_shared/reference/style.md`,
`skills/practicum-case-study/SKILL.md`, `tools/reference_scan.py`, `tools/research_ledger.py` and
`tools/uptodate_store.py`. The records are ADR 0132, [ADR 0211](0211-an-uptodate-entry-is-checked-against-its-masthead-and-a-sourced-record-is-cited-or-dropped.md)
and [ADR 0212](0212-the-evidence-row-grades-only-an-ingested-file-and-an-untitled-dump-is-filed-as-a-titled-copy.md).
No committed fixture carries it.

## Ruling 1 — the membership rule stays and stands on checkability

A cited UpToDate topic must be filed in the **Evidence store** because its masthead, last-update
year, and review currency can be checked only against the stored copy. That is the row's whole
ground. Every live phrase that calls a dump companion evidence, faculty evidence or faculty material,
or calls the store a supplied-source set, is replaced with **Case research** or **Evidence store**.
Where a phrase says a dump was deliberately supplied, it says the dump was deliberately filed. No
grader outcome changes.

A supplier field on the manifest, with a requirement attached to a faculty value, was declined
because no faculty dump has ever existed; a ticket can add it if one arrives. Dropping the row was
declined because every masthead and currency check reads the stored copy and would go silent for an
unfiled citation.

## Ruling 2 — the heading reader judges provenance only against a stated source

The heading reader's brief in `skills/_shared/reference/sourcing.md` gains one sentence: a sentence
stating who wrote, compiled, or supplied a document agrees only when a confirmed project-context
header line, a memory entry, or the clinician's recorded answer states it, and never on the
document's own contents. Where none states it, the reader writes `CONTEXT-VERDICT: contradicts` and
names the sentence. ADR 0332's `CASE-RESEARCH` line is such a header line for his compilation.

A new verdict word for an unsupported provenance claim was declined because `contradicts` already
covers asserting what no opened item states, and the word would move the record grammar, the
heading-read grader, and every worked example for a judgment no tool can check. Leaving the brief
alone was declined because the reader was the step that failed.

## Ruling 3 — the three records are corrected in place

ADR 0132, ADR 0211 and ADR 0212 each carry a dated correction at the sentence stating the faculty
premise, naming this record. Their rulings stand. This follows
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
on correcting a ratified record's facts in place and
[ADR 0191](0191-a-carried-claim-is-corrected-where-it-stands-and-436-never-ruled-it.md) on correcting
a carried claim where it stands.

A supersession marker under [ADR 0280](0280-an-overturned-ruling-carries-a-dated-supersession-marker-written-by-the-record-that-overturns-it.md)
was declined because no ruling was overturned, and the marker would tell a reader the store layout,
masthead check, or titled-copy rules no longer hold. Leaving the records as written was declined
because a reader of ADR 0132 would copy its premise.

## Ruling 4 — research and refutation returns never assert provenance

`skills/_shared/reference/sourcing.md` states once, for all five coursework skills, that a research
or refutation return refers to the clinician's compilation as his **Case research** or to the
**Evidence store**, and never states who wrote, compiled, or supplied a document unless its brief
says so. Nothing grades it; ruling 2's reader is the backstop.

Relying on the vocabulary cleanup alone was declined because the heading reader reached the false
attribution from a topic list with no wording to prompt it. A line in each skill's research step was
declined because it would be five copies of one rule.

## Build checklist

- `skills/practicum-case-study/SKILL.md`, the research-ledger section of `CLAUDE.md`,
  `AGENTS.md`, `reference/uptodate/README.md`, `skills/_shared/reference/apa7.md`, and
  `skills/_shared/reference/style.md`: ruling 1's vocabulary, and the membership row's ground
  restated as checkability.
- `tools/research_ledger.py`, `tools/uptodate_store.py`, and `tools/reference_scan.py`: the same
  vocabulary in messages and declared limits, with any test asserting the old message text updated.
- `skills/_shared/reference/sourcing.md`: ruling 2's sentence in the heading reader's brief and
  ruling 4's sentence for research and refutation returns.

The three ADR corrections and the `CONTEXT.md` wording for **Evidence dump** and **Dump manifest**
land with this record.
