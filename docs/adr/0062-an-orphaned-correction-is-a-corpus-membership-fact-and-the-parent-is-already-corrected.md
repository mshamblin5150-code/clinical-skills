# An orphaned correction is a corpus membership fact and the parent is already corrected

[ADR 0061](0061-a-declared-non-source-is-an-enumerated-class-and-it-earns-a-fourth-sweep-state.md)
kept `errata` out of the declared-non-source set and filed the orphaned parent separately, as
[#640](https://github.com/mshamblin5150-code/clinical-skills/issues/640). Grilled 2026-08-29
against `origin/main` at `5ea7d28`. **Seven decisions, all the clinician's, all on that date.**

The corpus change ruled here was made during the session: `IDSA/ciaa1216.pdf` is on disk, and the
corpus is 180 documents. Everything else is the record the build reads.

## What is ruled

1. **`ciaa1216` joins the corpus and both IDSA rows curate to one `babesiosis` topic.** The
   `topic` column is the join, and the 2026-08-20 audit ruling on the errata's topic cell is
   re-taken.
2. **A corpus figure belongs to one of four classes, and the classes have different nets.** The
   ADR states them; no check is built.
3. **`CONTEXT.md`'s `Corpus` term drops its false clause and points at `Corpus drift`.**
4. **No orphaned-correction detector.** The limit is declared. The narrower *sole source is class
   `errata`* variant is declined with it.
5. **A correction wins and the superseded row is never written.** No new format rule, and no
   `CONFLICT` block is owed where nothing collides.
6. **#640 stays one ticket and carries the corpus, catalog, audit and figure work.** The sheet is
   #429's.
7. **The errata is a source of the babesiosis topic that yields no rows**, and its `## Sources`
   line is the only record in the tree that a correction happened.

## The premise the ticket was filed on was false, and the glossary is where it came from

#640 decision 1 weighs adding the parent against *"a change to the corpus, which grows by a person
putting a file into it and which no artifact in the tree witnesses."* Three artifacts witness it,
and [#439](https://github.com/mshamblin5150-code/clinical-skills/issues/439) — closed — built them
under [ADR 0031](0031-corpus-drift-is-reported-at-the-commit-and-the-cheap-limb-reads-the-audit-ledger.md):
`tools/hooks/pre-commit:28` runs `guidelines_catalog.py --check-corpus-size` **unconditionally and
advisory on every commit**, `check_audit_digests` reports *present in the corpus without an audit
row*, and the audit ledger already carries the `bytes` column that cheap limb reads.

Run against the corpus with `ciaa1216.pdf` in it, on the day of this record:

```
guideline corpus: filename-and-size drift
  ciaa1216.pdf: in the corpus, missing from the audit ledger
  the check reports a corpus; it does not verify PDF contents
  a same-name same-size rewrite is outside its reach; python tools/guidelines_catalog.py catches one
```

**The false sentence was `CONTEXT.md`'s, verbatim, and it had exactly one copy in the tree.** The
**Corpus** term ended *"which is an event no artifact in the tree witnesses."* It was written by ADR
0031's own record commit, `7f20bb1`, 2026-08-25 — the commit that ruled the repair — and #439's build
landed the check three days later in `fac5a5d`, 2026-08-28. So a glossary term stated its ticket's
motivating defect as a standing property and went stale at the build, one day before #640 was filed
on it.

**The repair is a deletion rather than a reword, because the neighboring term already owns the
rule.** **Corpus drift** reads *"a document added, removed, or reissued under an unchanged
filename… what is a defect is a tree that carries on answering without saying it happened."* The
false clause was therefore a second copy of a rule its neighbor holds correctly, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape — a prose edit to
either fails nothing, and the reader misled is whichever they opened. Rewording it to state what is
now witnessed was rejected: it puts a mechanism's shape into a file whose rule is that it holds a
glossary and nothing else, and it re-creates the second copy, correct today and decaying the same
way.

## Why the topic merges, and why that is not overturning a considered decision

`CONTEXT.md`'s **Topic** term reads *"The subject a threshold sheet is keyed to… the unit a
clinician cites; a guideline document is not one, and several documents may address the same
topic."* Nine catalog topics already carry two or more documents, so a shared topic is an
established shape and not an invention.

By that definition the errata's cell — `hepatitis C treatment trial, babesiosis treatment tables
(corrections)` — is already non-conforming: no clinician cites it, and it names a document rather
than a subject. The cell was ruled on 2026-08-20 at `reference/guidelines-catalog-audit.md:968`,
against a blind auditor who read `hepatitis C trial and babesiosis guideline corrections`. **The
`Topic` term arrived 2026-08-22, in `e41aa16`** — two days after the ruling. So the merge is the
cell being brought under a model that did not exist when it was set, rather than a ruling being
overturned.

**The hepatitis C half carries no clinical quantity at all.** It is a contributor-affiliation
tagging correction to a trial the corpus does not hold. Every number in `ciab275.pdf` is
babesiosis, so the topic cell named two subjects of which only one could ever produce a threshold
row.

## Why the merge needed no new mechanism, and what it actually buys

Two documents on one topic land in one sheet. `reference/thresholds/README.md` requires a
`CONFLICT: <quantity>` block *"wherever two rows share a quantity and a population with different
values"*, with prose naming every distinct value and why they differ — so the superseded-versus-
corrected pair would have been graded rather than merely visible.

**That mechanism will not fire here, and the reason is the session's sharpest measurement.** See
below. What the merge buys instead is that both documents sit in one sheet's `## Sources` table, so
whoever reads the topic has the guideline and its correction in front of them at once.

## The parent already carries the correction, and says nothing about it

Measured 2026-08-29 against `IDSA/ciaa1216.pdf`, `sha256
e3210dee9d0e417263bccf45a7e1e2f939bd4888459e38e622355fc9d32f9775`, 16,724,109 bytes, 16 pages.
**Dated evidence on ADR 0031's terms** — counted against an out-of-repo corpus that nothing
committed re-derives, and the audit ledger's SHA-256 is what pins which bytes it is a claim about.

The corrigendum states that it added a rule and revised two dosing intervals. The parent contains
the added sentence — *"subsequent doses should be reduced to 500 mg daily"* — and the revised
clindamycin and quinine intervals, oral and intravenous, adult and pediatric. A pre-correction
parent could not contain the sentence the correction says it introduced.

Of the **23 distinct quantity-shaped tokens** in the corrigendum's babesiosis half, **23 appear in
the parent.** The single apparent miss was `250 mg/dose`, which the parent hard-wraps as `250 mg/`
and `dose)` across a line break; all three occurrences of `250` were read to confirm it.

And the parent **carries no notice that it was ever corrected**: `corrigend|erratum|has been
corrected` matches nowhere in its 16 pages.

So the copy of the version of record now in the corpus silently absorbed its own corrigendum. Three
things follow. There is **no superseded value anywhere in this corpus**, so ruling 5 is satisfied by
having nothing to write and no `CONFLICT` block is owed. The errata contributes **no clinical
quantity the parent lacks**, which is ruling 7. And ADR 0061 ruling 2's stated ground — *"it carries
a full revised dose table"* — is true of the document and **redundant within the corpus**; that
ruling stands and its ground is narrower than it reads.

**What no gate reaches, declared.** A source that yields no rows is invisible to every check here.
If a later copy of `ciaa1216` were the pre-correction text, the errata would matter again and
nothing would say so. The SHA-256 in the audit ledger is the only thing that distinguishes the two
versions, and it does not know what the difference means.

## Why there is no detector

#640 decision 2 proposes reading a corrigendum's parent off page 1 and joining it to the catalog,
on the ground that *"this one prints its parent's full citation and DOI on page 1."* It does. It
also prints a **second** parent, and two of its own DOIs.

[ADR 0047](0047-a-corpus-document-s-stated-citation-is-read-off-its-own-page-and-a-link-is-not-one.md)
already adjudicated this instrument on this document. Ruling 3 makes the catalog's `citation`
column *"a judgment column, not a mechanical one"*, scaffolded and then confirmed by a person;
ruling 5 refuses a value-shape check; and its trap table's **first row is `IDSA/ciab275`** — *"a
matcher would publish `10.1093/cid/ciz628`, the article this errata corrects."* That is the
hepatitis C parent, the half with no clinical content. The babesiosis parent, `ciaa1216`, is the
second DOI on the same page.

Three further reasons. The `errata` class has **n=1**, so a general rule is built from one document
— the [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137) shape #640's own
body invokes to keep `errata` out of the non-source set. Anything mechanical rides on the
`citation` column, which is ratified and **unbuilt**, owned by open
[#512](https://github.com/mshamblin5150-code/clinical-skills/issues/512). And the ticket's *Done
when* is discharged without new code: `guidelines_catalog.py` verifies 180 rows against 180 audit
digests against the live corpus, and `threshold_coverage.py` prints `topics 169 from 180 catalog
rows` — re-derivable by command, which is what was asked for.

**The narrower variant was declined too, and it is the one worth recording.** *A topic whose only
source is class `errata`* is one catalog query, corpus-free, needs no matcher and no `citation`
column, and **fires on the tree as it stood before this record**. It is refused because it is keyed
on the **curation** rather than on the membership — the topic merge silences it, so the thing that
removes its only true positive is the same commit that would add it, and it can never again be
tested against a real instance. The class it misses is the one that matters: an orphaned correction
classed `guideline` rather than `errata`, which ADR 0047's trap instance 2 already records in the
CDC opioid 2022 document, printing the 2016 edition it replaces.

## The four classes a corpus figure falls into

The corpus had never grown before this record. The figure surface is **110 lines matching `\b179\b`
across 27 tracked files**, and `7,733` on 12 — and a find-and-replace over either is wrong in three
distinct ways. Declared rather than checked, because the distinction a check would need is not one
any matcher can make; see the detector section above, and
[#275](https://github.com/mshamblin5150-code/clinical-skills/issues/275).

**1. Must move, and the suite says so.** Four assertions go red and force the edit:

```
tools/test_guidelines_catalog.py:927   assertEqual(len(rows), 179)
tools/test_guidelines_catalog.py:932   assertEqual(total, 7733)
tools/test_guideline_sheets.py:452     assertEqual(len(societies), 179)
tools/test_threshold_coverage.py:301   assertRegex(r"(?m)^topics\s+169 from 179 catalog rows$")
```

`tools/test_guideline_sheets.py:453` additionally pins the literal `"179"` into `AGENTS.md` and
`skills/clinical-note/SKILL.md`, so those two move as a pair or go red with them.

**2. Must not move, and nothing says so.** Roughly thirteen of `tools/guidelines_extract.py`'s
occurrences are of the form *measured over all 179 documents and all 7,733 pages*, dated 2026-08-16 or 2026-08-19.
ADR 0031's own table is labeled *"dated evidence and not live figures"*. ADRs 0045, 0047, 0007,
0030, 0057, 0049, 0034, 0012 and 0002 carry more, and `tools/test_class_vocabulary.py:14` records
*93 of 179* about a tree that no longer exists. **Editing any of these leaves the suite green**,
and this is the class a careful reader corrupts precisely by being careful.

**3. Not the corpus count at all.** `tools/guidelines_extract.py:330` holds the literal `"3,179"`,
a stripped-boilerplate figure inside `ORPHANED_FIGURES` — and `\b179\b` **matches inside it**,
because the comma is a word boundary. Mutating it to `"3,180"` fails nothing:
`tools/test_split_census.py:197` asserts only that `CLAUDE.md` does *not* copy the pair, which stays
true. `reference/cdc-bmi-for-age-2022.csv` and `tools/test_proposal_shape.py:35`, a SHA-256, also
match.

**4. Re-derive, never increment.** `tools/test_guideline_sheets.py:549` pins *"19 of the 179
documents cannot be omission-gated"* into the skill — a 180th document is either omission-gateable
or it is not, so `19` is a fresh measurement. Likewise ADR 0057's *146 of 179 print a DOI*, the
margin rule's *27 of 179*, every character count — `39,394,780`, `39,258,016`, `61,399,040` — and
**`CLAUDE.md`'s reconciliation table, which that file already says must be re-derived whole rather
than patched, because it has twice been published not balancing.**

## Consequences

The corpus is 180 documents and every checkout on the machine prints the drift line on its next
commit until the audit and catalog rows land. It is advisory and refuses nothing.

`reference/guidelines-catalog.md` gains a row and the errata's `topic` changes, so its
`## Unsettled cells` reason for that row — *"an errata document, correcting two unrelated
articles"* — is rewritten with it. `reference/guidelines-catalog-audit.md` gains a digest row and a
blind reading row; the blind reader must not be shown the scaffold, on ADR 0047 ruling 9's terms.
`reference/thresholds/coverage.md`'s topic name changes and its population stays **169**, because
one name retires and one arrives onto the same cell.

All three content-addressed stages re-run — extraction, index and the recommendation sweep — because
the source hash moved.

`babesiosis` stays `unread`. Writing its sheet is [#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429)'s
sweep, which is blocked on six builds and two rulings, so #640 ends at the catalog either way. That
is also why splitting #640 was rejected: the catalog row, the audit row, the topic merge and the
figure work are one event, and a child ticket would put the topic change in a different diff from
the document that justifies it.

Two records are corrected in place on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms: ADR 0061's two statements that the corrected document is absent from the corpus, and ADR
0057's errata sentence, which pointed at ADR 0061 for a fact this record supersedes. **No ruling of
either changes.**

## Rejected

- **Leaving the corpus alone and constraining what the sweep may ship.** Leaves the corpus's entire
  babesiosis holding a two-page corrigendum whose own text sends a reader to a Table 3 nobody has,
  and the constraint has to be built as new format work on top of #587's unbuilt column.
- **Adding the parent and leaving the topics apart.** Builds the artifact #640 calls the worse risk
  — two unjoined sheets — and hands the join to
  [#584](https://github.com/mshamblin5150-code/clinical-skills/issues/584)'s reader row.
- **Reading a corrigendum's parent off page 1.** The instrument ADR 0047 refused, on the document
  that is its own recorded counter-example, with a 1-to-many problem that record did not know about.
- **A check on *a topic whose only source is class `errata`*.** Keyed on curation rather than
  membership; its only true positive is removed by the commit that would add it.
- **Rewording `CONTEXT.md`'s `Corpus` term to state what is now witnessed.** Puts a mechanism into a
  glossary and re-creates the second copy.
- **Writing both the superseded and the corrected row with a `CONFLICT` block.** Puts a known-wrong
  dose into an artifact `differential_scan` joins and a case study cites, settled only by prose —
  which is [#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289) arriving inside
  its own repair. Moot in this corpus in any case: there is no superseded value in it.
- **A sheet declaration explaining why the errata yields nothing.** Format machinery for a document
  that produces no rows.
- **A new `babesiosis` topic beside the retained corrections topic.** Takes the registry to 170 and
  reintroduces a sole-source errata topic needing a sweep state of its own, which is the shape ADR
  0061 spent six decisions avoiding.
- **A `status` column.** [#107](https://github.com/mshamblin5150-code/clinical-skills/issues/107)
  refused one and #640 forbids reopening it. Nothing here reopens it.
