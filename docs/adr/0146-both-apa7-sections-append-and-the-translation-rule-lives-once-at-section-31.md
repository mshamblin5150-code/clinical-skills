# Both apa7 sections append and the translation rule lives once at section 31

[#945](https://github.com/mshamblin5150-code/clinical-skills/issues/945) reports that two ratified ADRs both claim `apa7.md` section 31, and that both rest on an unpublished section-citation matcher giving contradictory counts. Grilled 2026-09-07, hours after [ADR 0145](0145-the-republished-date-element-is-shared-grammar-keyed-on-its-second-element.md) merged and was found defective by the exhaustive tracker sweep of its own branch. Every measurement below was taken in process at `43b93c8` with the freshness gate `FRESH`. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The collision, and what falsified the argument under it

The sheet's highest section is **§30, "Outside the nursing set: APA reference example index"** (`skills/_shared/reference/apa7.md:645`).

- [ADR 0143](0143-the-block-quotation-is-authored-markup-the-renderer-obeys-and-its-citation-keyed-grader-lives-where-the-docx-is-submitted.md) ruling 5, for [#815](https://github.com/mshamblin5150-code/clinical-skills/issues/815), inserts a block-quotation section **at §30** and moves the index **to §31**.
- ADR 0145 ruling 7, for [#816](https://github.com/mshamblin5150-code/clinical-skills/issues/816), claims **§31** for the republished date-element rule and rules that **nothing renumbers**.

Neither cites the other. `grep` for `0143` or `815` in ADR 0145 returns nothing; ADR 0143 cites #816 only for an unrelated grader defect.

**ADR 0143's insertion rests on exactly one condition, and ADR 0145 falsified it three days later.** Its words: *"this is the one insertion point in the sheet where the number that moves is cited nowhere."* The number that moves is §30. ADR 0145 ruling 1 reads:

> `apa7.md` has thirty sections … **§30 routes a writer off-sheet**

That is a citation of §30 **as the index**, in a ratified record on `main` that this repository does not edit. The condition no longer holds, and it was retired by the very record that collided with it.

## Ruling 1 — both sections append, and the index stays §30

`apa7.md` gains **§31** and **§32**. Nothing renumbers.

The declined branch is executing ADR 0143 ruling 5 as written. Its cost is that it renumbers a section ADR 0145 ruling 7 forbids moving *and* which is now cited, so the renumber would have to be justified on a condition that is false — and ADR 0129's warning about silently re-pointing citations applies to it and not to appending.

**What appending costs is tidiness alone**: the index stops sitting last. ADR 0143 gave no rule requiring it to, and a closer's position is presentation rather than a citation contract.

## Ruling 2 — the numbers are assigned now rather than raced

**§31 is the republished date-element rule. §32 is the block quotation and its locators.**

#816 is buildable and #815 is `blocked` on a browser read, so a *whoever-lands-first* convention is a race between two ratified records — the same shape [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180) records for a figure edited on two branches, arriving on a section number. Naming both now costs one sentence and removes it entirely.

## Ruling 3 — the translation rule lives once, at §31, and §32 points at it

ADR 0143 ruling 5's section covers, in its own fourth bullet, *"a translation carries both years earliest first and slashed"* — which is §31's whole subject.

§32 states the block form and the locator rules and **cites §31** for the two-date form. It does not restate it. Two sections of one sheet stating one APA rule, with a prose edit to either failing nothing, is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) inside the sheet the graders read.

## Ruling 4 — neither section-citation count is instrumented, because neither decides anything now

| record | figure | what it was for |
| --- | --- | --- |
| ADR 0143 | 50 citations, all in sections 1–8 | so moving §30 to §31 is safe |
| ADR 0145 | 52 citations across 20 files, 10 ratified ADRs | so nothing may renumber |

**Neither published a matcher.** ADR 0145's own matcher re-derives as **53 across 22** at `43b93c8` — it moved because that ADR added itself to the tree — and a sweep agent's three plausible matchers returned 12/7, 54/16 and 75/25. Two ratified records reached **opposite rulings** from unreproducible counts of one population, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) producing a contradiction rather than a stale number.

**No instrument is built and no test is added.** Under ruling 1 nothing renumbers, so neither figure is load-bearing any more. **The repair for a figure with no matcher that decides nothing is to stop citing it, not to build a gate for it** — and building one here would be a mechanism whose only purpose is to keep a retired argument checkable.

**What that leaves standing is declared rather than hidden:** if a future record proposes renumbering, it inherits an uninstrumented population and must publish its matcher before its count is worth anything. That is the standing price of ruling 4 and it is named here so the next session does not discover it as a gap.

## Ruling 5 — ADR 0143's classical-works bullet is re-derived before §32 is written, not copied

ADR 0143 ruling 5's fourth bullet states *"Ancient Greek and Roman works and classical religious works: **no reference list entry is required**."* That record also states plainly that *"Every `apastyle.apa.org` fetch attempted during this grilling was stopped by an Imperva challenge, so the wording above was read through a search index"*, and makes opening those pages in a browser a **build prerequisite** — which is why #815 is `blocked`.

**That read was performed on 2026-09-07** and it points the other way. APA's religious-work references page and its classical-and-religious-works post both give **full reference entries** — the Bhagavad Gita, the King James Bible, Alighieri, the Epic of Gilgamesh — and the post opens *"A classical or religious work is cited as either a book or a webpage."* Neither page says an entry is optional.

**This record does not rule the bullet wrong.** Absence from the two pages that would carry it is strong evidence and is not the *Publication Manual*, which is not in this repository — the caveat `apa7.md` already travels with its own section numbers. What is ruled is narrower and is enough: **the bullet is re-derived from APA's own pages before §32 is written**, and it may not be copied forward from a search-index read. It also points opposite to §31, which exists precisely because such works **do** carry an entry bearing one date, so the two cannot both stand as written.

## Ruling 6 — ADR 0145's three defects are corrected on the tracker and that record is not edited

The sweep of ADR 0145's own branch found four defects in it within the hour. Three are corrected on #816 and #867/#921; the fourth is this record's subject.

1. Ruling 9's *"`reference_scan.NOT_REACHED`, which is inside `test_declared_limits.declarers()`'s walk"* is **false**. Driven in process: `declarers()` is keyed on the literal name `DECLARED_LIMITS`, returns 18 modules, and `reference_scan` is not among them — its only object is `NOT_REACHED` at `reference_scan.py:627`. Of the three rows ruling 9 places, one is inside the walk and two are outside it. **The placement stands; only the claim about it is withdrawn.**
2. Ruling 9 and #816 named `discussion_artifact.LEGAL_READER_NOT_REACHED`, which **does not exist** — the tree carries `LEGAL_SOURCE_NOT_REACHED` at `discussion_artifact.py:64`, and the rename is ADR 0135 ruling 5's, unbuilt and pending [#771](https://github.com/mshamblin5150-code/clinical-skills/issues/771). That is ADR 0135 ruling 5's **own recorded defect repeated**, in the record that cites it.
3. #816's *Done when* had inherited defect 1 as an **unsatisfiable acceptance criterion** — *"the three declared-limit rows are in walked objects"* — which no builder could meet without creating the fourth naming convention the ruling one paragraph earlier forbids. Corrected in place on #816 under [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s reasoning that a correction below the advice is not a correction for anyone who acts on the advice.

**ADR 0145 is not edited**, on this repository's practice of superseding ratified prose rather than rewriting it — ADR 0100 ruling 3, ADR 0134 and ADR 0135 ruling 8 — because a rewrite points its merge receipt at text that no longer exists.

## What none of this reaches

**Whether §32's content is right.** Ruling 5 orders a re-derivation and does not perform it. #815 stays `blocked` on that read plus [#817](https://github.com/mshamblin5150-code/clinical-skills/issues/817) and [#828](https://github.com/mshamblin5150-code/clinical-skills/issues/828), which are untouched here.

**Whether any other apa7 section number is contested.** Two were found because two records collided. Nothing walks the sheet's numbering, and ruling 4 declines to build something that would.

**Whether the declared-limits naming convention should change.** Ruling 6 corrects a false claim about the walk and settles nothing about its population, which belongs to [#867](https://github.com/mshamblin5150-code/clinical-skills/issues/867), [#875](https://github.com/mshamblin5150-code/clinical-skills/issues/875) and [#921](https://github.com/mshamblin5150-code/clinical-skills/issues/921).

*Corrected 2026-09-12 under ADR 0016 and ADR 0191: “under #436's rule” attributed a correction rule to #436, which rules nothing about corrections. The sentence now names the reasoning in ADR 0016 that existed when #816 was corrected.*
