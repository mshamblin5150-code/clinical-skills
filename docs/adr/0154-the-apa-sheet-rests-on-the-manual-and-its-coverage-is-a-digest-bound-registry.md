# The APA sheet rests on the manual and its coverage is a digest-bound registry

Out of [#976](https://github.com/mshamblin5150-code/clinical-skills/issues/976), grilled on
2026-09-08. Measured at `6e0dd3b` with the freshness gate `FRESH`.

`skills/_shared/reference/apa7.md` carried a header saying the *Publication Manual*'s section
numbers **are not themselves checked here**, on the ground that the manual is not in this repository
and cannot be. That sentence fused two claims. *Cannot be committed* is true and stays true: the
manual is copyrighted and this repository is public. *Cannot be checked* is false — the clinician
owns the seventh edition and it is readable in a signed-in browser.

**Section titles are used below as citation metadata, the way any citation carries them. No manual
prose is reproduced in this record, and none may enter the tree.**

## What was measured before ruling, on 2026-09-08

**The sheet's own citation count was an undercount produced by its own instrument.** #976's body
reports *11 explicit `§` citations*. Twelve section numbers are written, and the ticket's
enumeration omits `§2.27` outright. Two of the twelve are range endpoints — line 40's
`§9.43 to §9.49` and line 201's `§§2.26–2.27` — so **sixteen manual sections are cited**, not
eleven. The omitted members include **`§9.44`**, which is the section #976's own headline evidence
rests on. A numerator and a denominator built from the same eyeball grep agreed while both dropped
the section that produced the finding.

**The sheet's unpointed population is larger than either of the ticket's two options.** Roughly
thirty-six rule statements carry no section and no URL: twenty-one top-level bullets in §§1–5 that
inherit only their section header's pointer, ten rows of §6's first table, and all five rows of its
second. Some are provably outside the pointer they sit under — line 55's page-number rule hangs
under a reference-list pointer, and line 133's undated-letter rule cites nothing at all.

**The sheet already had two provenance vocabularies and one of them covered nothing.** Twenty-six
of its thirty-two sections carry a dated `**Provenance:**` line; §§8–29 name an APA Style web page
and an item number with **no URL at all**, so an exemption keyed on hostname would have exempted
three sections and sent twenty-two back to the manual. The six with no such line — §§1, 3, 4, 5, 6,
7 — are covered by one range sentence in the header, which had already gone stale-shaped once: §6
needed a second date appended on 2026-09-08.

**The manual's structure, read in the clinician's Bookshelf on 2026-09-08.** Twelve chapters,
**336 numbered sections**, and a separately published *List of Tables and Figures* holding **43
tables and 39 figures**, 82 in all. The sixteen cited sections are 4.8% of 336. `apa7.md` cites
**zero** tables and **zero** figures.

| Ch | | sections | tables | figures |
| --- | --- | ---: | ---: | ---: |
| 1 | Scholarly Writing and Publishing Principles | 24 | 0 | 0 |
| 2 | Paper Elements and Format | 28 | 3 | 5 |
| 3 | Journal Article Reporting Standards | 18 | 3 | 1 |
| 4 | Writing Style and Grammar | 30 | 1 | 0 |
| 5 | Bias-Free Language Guidelines | 10 | 0 | 0 |
| 6 | Mechanics of Style | 52 | 5 | 0 |
| 7 | Tables and Figures | 36 | 24 | 21 |
| 8 | Works Credited in the Text | 36 | 2 | 7 |
| 9 | Reference List | 52 | 1 | 4 |
| 10 | Reference Examples | 16 | 0 | 0 |
| 11 | Legal References | 10 | 2 | 0 |
| 12 | Publication Process | 24 | 2 | 1 |

**Declared limit on that census.** Each section count is the chapter's highest section number,
assuming sequential numbering with no gaps. The sequence was seen whole for chapters 1, 2, 3, 9, 10
and 11 and only at the tail for 4, 5, 6, 7, 8 and 12. A gap anywhere makes the count an over-count.

**One heading group was then read at the source, and produced six findings from eleven items.**
Chapter 9's *Reference List Format and Order*, §9.43 to §9.52, with Figure 9.2 and its Full
Description, plus §9.16.

1. **§9.44's rule is not in §9.44's body, and not in Figure 9.2's image either.** The body gives six
   rules the sheet carries none of, among them a shorter-name-before-longer-name principle and the
   disregarding of parenthesized and bracketed matter. The letter-by-letter, prefix-included and
   capitalization-disregarded clauses live **only** in the figure's collapsed `Full Description`
   block, across twelve numbered explanations. The rendered figure carries the examples without the
   explanations, and its twelfth example sits below the fold.
2. **§9.47 is a section the sheet cites correctly and never read to its root.** `apa7.md` §3 states
   the second of APA's two steps for assigning `a`/`b` letters and omits the first, which orders on
   date specificity before title. It also omits the series exception, and carries two of the three
   letter formats.
3. **§9.46 is absent from the sheet, and its absence is a defect in committed code.** It governs the
   ordering of one-author against multiple-author entries sharing a first author, and of undated and
   in-press entries. That is the rule behind a case this repository has already litigated, and
   neither the sheet nor the ADR that settled it cites §9.46.
4. **§9.49's numeral rule is absent, and a naive sort inverts it.** `reference_scan`'s
   `list-not-sorted` row fails a correctly ordered list on it.
5. **§9.16 is the retrieval-date rule; the sheet cites §10.16, the webpage examples section.** §9.16
   names the database `apa7.md` §2 is written about, and turns on whether an archived version is
   retrievable — a test the sheet and `reference_scan` implement as the presence of a DOI. §9.16
   also fixes the retrieval date's position relative to the URL, which the sheet does not state.
6. **§9.43's own internal pointer for ordering is narrower than the sheet's range**, and §9.43's
   bullets do not contain the page-number rule `apa7.md` §1 lists beneath its pointer.

**The record shape precedents were priced against the tree.** `threshold_sheet.py`'s recorded
citation date is a **whole-sheet header**, last match wins, and its per-row `RENDERED:` marker
carries no date at all — so the arrangement #976 proposed as the per-section option is in fact the
single dated header it rejected. `reference/guidelines-currency.md` is the only true per-item
verification date in the repository and about **178 of its 180** document rows are blank. **Nothing
in any of the three detects an item edited after its verification date** — no `git blame`, no
per-row digest. The one mechanism that binds a human verdict to the bytes it ruled is
`reference/tracker-scan-rulings.json`, which keys on a SHA-256 of the line. `tools/voice_model_scan.py`
is the precedent for parsing a marker out of a shared reference sheet.

## Ruling 1. The sheet's authority is the manual, and the two units are different

`apa7.md` draws from the *Publication Manual*. `apastyle.apa.org` remains a legitimate APA source
and stops being the sheet's ceiling. The **reading unit is the manual section**, because a rule the
sheet omits is only visible from the manual side. The **record unit is the sheet section**, because
that is where the claim lives and where an edit invalidates a verification, and because roughly
thirty-six of the sheet's claims cite no manual section to be recorded against.

The self-contradiction #976 reports resolves in the opposite direction from the one it assumed. §2's
line claiming its form was read from the manual is the **model**; the header's caveat is what was
false. Line 3's *"Distilled, not downloaded"* is untouched and is not up for revision.

## Ruling 2. The denominator is derived from the manual, not from the sheet's citations

Twelve chapter rulings, each with a written reason. **Nine chapters are in scope** — 2, 4, 5, 6, 7,
8, 9, 10, 11 — and **three are out** — 1, 3 and 12, which concern getting into a journal rather than
writing a student paper. Every section and every table and figure in an in-scope chapter gets a row.

| | |
| --- | ---: |
| chapter rulings | 12 |
| in-scope sections | 270 |
| in-scope tables and figures | 75 |
| **registry rows** | **345** |
| declared out under three chapter rulings | 73 |

Chapter 4 is in because the clinician rules what a paper reads like and wants the source of truth
for it. Chapter 5 is in for the same reason and on a measurement: **this repository carries no
bias-free language rule at all**, while its ten sections govern the axes on which a clinical case
study describes a patient. Chapter 5 is therefore expected to produce additions rather than
corrections.

**The declined alternatives are recorded because each will be re-proposed.** Keying the population
on the sheet's own citations is falsified above — that instrument dropped §9.44. Keying it on the
heading group containing each cited section is bounded and elegant and **would have missed §9.16**,
because the sheet cites nothing in that group. Giving all 336 sections a row buys nothing over a
chapter ruling with a written reason.

## Ruling 3. A read means the body, its tables and figures, and their Full Description blocks

A manual section counts as read when its body text, every table and figure it owns, and each of
those figures' `Full Description` blocks have been read. Nothing less is a read. Finding 1 above is
the recorded instance: a reader who read §9.44's prose and looked at Figure 9.2 would have written
down a confident and wrong account of the rule.

**The state vocabulary distinguishes a root read from a section opened and ruled out of scope**, and
the report states them separately. A single figure covering both reads stronger than the reading
was, which is the shape this whole record exists to refuse.

## Ruling 4. The registry ships inside `skills/` and the bind is graded both ways

`skills/_shared/reference/apa7-coverage.md`, beside the sheet it grades, so that whoever takes
`skills/` gets the rule, the audit trail and the command that checks they still agree.
`reference/thresholds/coverage.md` sits at the repository root because threshold sheets are
maintainer-built; this one does not.

`tools/apa7_coverage.py` grades the bind in both directions and refuses drift, on
`threshold_coverage.py`'s arrangement. The sheet keeps its rule in this repository's own words; the
registry keeps what was checked, when, and the verdict — **never what the manual says**. Together
they are complete without the book, which is what shipping everything with the skill has to mean
when the book itself cannot travel.

## Ruling 5. A verification binds to a normalized digest of the claim it verified

Each row carries a digest of its sheet section's normalized text. Normalization is
`tools/prose_bind.py`'s, which collapses whitespace and strips quotes, `#`, `>`, `*` and backticks —
so a hard wrap, a reflow or an emphasis edit does not fire, and a changed word does.

A date alone is what all three existing registries record, and it is the gap
`reference/tracker-scan-rulings.json` was built to close. Without a digest a verification dated
today survives a rewrite of the claim beneath it and reads as current to the next person who takes
this skill.

## Ruling 6. Evidence is substantive and every in-scope row is refuted

A row's record states what only a reader could have written, and a non-substantive row fails the
grader. That is `specificity_scan`'s rule and its ground: **the reason is the evidence the check
happened**, and anybody can write a state and a date. The discrimination test is that under a
date-only record, a row that was read and a row that was not are byte-identical.

**Every in-scope row is refuted by a second reader briefed to refute rather than confirm**, recorded
the way `reference/thresholds/subjects.md` records a refutation. Consequence-keyed refutation was
recommended and the clinician widened it: at the rate measured, findings touched five of ten
sections in the one group read, so a consequence-keyed set is not a small sample and the saving is
not worth the hole.

## Ruling 7. Every repair lands in this ticket, and the work is two-phase

A finding is always recorded in its row; that needs no permission. **Every repair lands in #976** —
prose repairs to `apa7.md` and to the restatements in `style.md`, and repairs to committed scanner
behavior such as findings 3, 4 and 5 above. A registry stating that the sheet is wrong beside a
sheet that is still wrong is worse than not knowing.

**That makes the repair scope unknowable until the read is done, so the ticket is two phases in one
ticket.** Phase 1 is the read, the registry, the grader, its tests and its hook line; it is fully
specifiable now and **its output is the complete finding list**. Phase 2 is every repair, specced
from phase 1's registry rather than from a guess. #976 does not claim to be specified for phase 2
until phase 1 lands.

**The label is `ready-for-human`.** Reading the manual needs a signed-in Bookshelf session, which no
unattended agent has; an anonymous fetch reaches a paywall the way ADR 0145 measured an interstitial
on `apastyle.apa.org`. `ready-for-agent` would promise what cannot be delivered.

## Ruling 8. Structural drift refuses and staleness reports

**Refuse**: a sheet section with no registry row, a row naming a section that no longer exists, a
state outside the vocabulary, a missing schema marker. **Report**: a digest mismatch downgrades its
row and raises the never-checked count.

The cheapest escape from a refusal on staleness is to recompute the hash, and **no tool here can
tell a re-read from a recompute** — so refusing staleness buys forged evidence rather than fresh
reading. A broken bind is a mistake; a stale verification is a fact. `threshold_coverage.py`,
`guidelines_currency.py` and `threshold_sheet.py` already draw the line in that place.

**The counts print through `--quiet`.** `threshold_sheet.py`'s never-recorded line sits inside
`format_report` while `tools/hooks/pre-commit` runs that command with `--quiet`, so the one line
telling a committer the check has never run is the line a committer never sees. Its tier-2 banner
was deliberately built to survive `--quiet`; this grader's counts go where the banner goes, or
ruling 8's reporting half never reaches anybody positioned to act on it.

## What this record does not settle

**A reader who opens the page and misreads it.** Ruling 6 narrows that and nothing closes it,
because no committed checker in this repository can open the book. The limit is permanent.

**The 73 items declared out.** Three chapter rulings carry written reasons; nothing reads those
sections, and a rule the sheet should carry that lives in chapter 1, 3 or 12 is outside every net
here.

**Whether the census counts are exact**, under the sequential-numbering limit declared above.

**What phase 2 contains.** By construction that is phase 1's output, and this record deliberately
does not enumerate it from a sample of eleven items.

**Whether `apastyle.apa.org` and the manual ever disagree**, and which wins if they do. No instance
was found; none was looked for.

## Correction, 2026-09-08. Ruling 2's census and findings 2, 3 and 4 were measured at a base `main` left before this record merged

Found by the tracker sweep of this record's own session, hours after it merged. **The eight rulings
are unchanged; what follows corrects the measurements they were argued from.**

**The base moved between measurement and merge.** Every figure above was taken at `6e0dd3b`.
`3a1b521` — [#942](https://github.com/mshamblin5150-code/clinical-skills/issues/942)'s build,
merged as `b3ea628` twenty minutes before this record — edited `skills/_shared/reference/apa7.md`,
which grew 749 to 758 lines. Re-derived at the merge commit `f7fd264`:

| stated above | at `f7fd264` |
| --- | --- |
| sixteen manual sections cited, 4.8% of 336 | **eighteen, 5.4%** — `§11.3` and `§11.5` added at `apa7.md:368` |
| line 133's undated-letter rule, line 201's `§§2.26–2.27` | `:134` and `:206` |
| `apa7.md:117`, `apa7.md:202` | `:120`, `:207` |

**Finding 2 is half superseded.** The sheet now carries the `in press-` letter format, so *"carries
two of the three letter formats"* is false at the merge. **The two-step half stands**: `apa7.md` §3
still states only the alphabetize-by-title step and carries no series exception.

**Finding 3's sheet half is false at the merge and its code half is falsified outright.**
`apa7.md:137` cites `§9.46` by number and carries its no-date, dated, in-press ordering. And the
claim that its absence *"is a defect in committed code"* does not reproduce. Driven against
`reference_scan` at `f7fd264` with a liveness control that fires:

```
control, obviously out of order   -> list-not-sorted   (control fires)
9.46 APA-correct, one-author 2019 before joint 2015  -> clean
9.46 naive order, joint 2015 before one-author 2019  -> list-not-sorted
```

**The scanner already implements `§9.46` correctly.** That claim was asserted from a reading of the
manual without driving the code, which is this repository's own standing rule broken inside the
record that restates it.

**Finding 4 is confirmed, and only now on a discriminating measurement.**

```
9.49 APA-correct, "Top 100" before "Top 10"  -> list-not-sorted   (false alarm on a correct list)
9.49 naive order,  "Top 10" before "Top 100" -> clean
```

**Three counting instruments were partial in three different ways while making this correction**,
which is the finding worth more than the numbers. The record's own citation count is the third: a
pattern reading `§` runs missed `§11.5`, because that section is written without its own section
symbol after an `and`; widening the separator set then merged across `and` and silently stopped
expanding `§9.43 to §9.49`, dropping four interior sections while reporting a plausible total. Only
a pass that expands ranges *within* a segment reconciles base to sixteen and merge to eighteen.
**The ticket's instrument that this record was written to correct failed in the same family**, and
so did both of its replacements.

**What this changes for [#976](https://github.com/mshamblin5150-code/clinical-skills/issues/976).**
Nothing in phase 1's shape. It removes one item from phase 2's expected repair list, moves finding
2's remainder to a narrower claim, and establishes that **a finding about scanner behavior is not
established until the scanner has been driven with a control that fires** — which phase 1's rows
must record rather than assume.
