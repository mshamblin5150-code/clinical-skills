# The republished date element is shared grammar keyed on its second element

[#816](https://github.com/mshamblin5150-code/clinical-skills/issues/816) reports that `reference_scan` refuses a correctly cited translated work, because APA puts two dates in text and one in the entry. Grilled 2026-09-07. `main` advanced mid-session from `1557ec7` to `6201156`; the gate caught it, the branch was brought forward, and **every figure below was re-derived unchanged on the merged base** — the three commits `main` gained touched `implementation_map.py`, its test and `CONTEXT.md`, and no file this record measures. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## The clinician's standing ruling, made in this session

> Pull the APA 7 rule. If the scanner cannot match what the APA rule is, it is a scanner defect and must be repaired.

That ruling decides the ticket's open question 3 before the design tree opens, and it decides it **per root** rather than globally: it is satisfiable only where APA publishes a rule. Ruling 5 below is where it runs out.

## APA's site is reachable, and ADR 0039's caveat is a fact about the fetch tool

[ADR 0039](0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md) records that `apastyle.apa.org` *"sits behind Imperva and returned an incident ID rather than a document"*, and rests its legal rulings on seven library guides instead. Re-derived 2026-09-07: `curl` and `WebFetch` receive an Incapsula interstitial — **HTTP 200, 212 bytes, no document**, which is worse than a refusal because the status reads as success. Chrome renders the same URLs normally.

So APA's own pages are readable evidence for any future record, and a `200` from that host is not. The guide-consensus caveat travels with ADR 0039's *legal* claims for the separate reason in ruling 5, not because the site cannot be read.

## Ruling 1 — the form is on-sheet, because the declared limit is not cheaper than the fix

`apa7.md` has thirty sections and none is a republished, translated or reissued work. §30 routes a writer off-sheet, and [ADR 0097](0097-the-apa-sheet-s-class-vocabulary-is-apa-s-nursing-set-and-coverage-is-decided-per-bucket-while-the-gate-is-a-bind-test.md) scopes the sheet to APA's nursing set — and all three live instances carry no journal, no DOI and no nursing marker, so the off-sheet reading was available.

It is refused on a measurement rather than on principle. The ticket's option 3 — a `NOT_REACHED` row — exempts `uncited-entry` only, and **the arabic root does not fire `uncited-entry`**; it fires `intext-year-mismatch`, which that exemption does not touch. Exempting *that* row requires first knowing the entry is republished, which means reading its `(Original work published …)` parenthetical — the whole entry-side detection, after which emitting the key is the cheaper remaining step. The limit is cheap for the classical root alone and delivers less than the fix everywhere.

## Ruling 2 — APA's rule, pulled verbatim, is wider than the ticket's guess in three ways

From APA's book-references page (§10.2), religious-works page, and the classical-works and translated-works blog posts, read 2026-09-07:

| source | form |
| --- | --- |
| §10.2 ex. 3 | `(Watson & Rayner, 1920/2013)` · narrative `Watson and Rayner (1920/2013)` |
| §10.2 ex. 4 | `(Kübler-Ross, 1969/2014, foreword by Byock, p. xv)` |
| Religious works | `(King James Bible, 1769/2017, Song of Solomon 8:6)` |
| Classical works | `(Alighieri, 1909/2001, Inferno, Canto XIII, Lines 72–74)` |
| Classical works | `(The Epic of Gilgamesh, ca. 2750–2500 B.C.E./1998, Tablet II)` |

APA states the rule twice in its own words: *"Both publication years appear in the in-text citation, separated with a slash, with the earlier year first"*, and *"place 'ca.' before the year (**or years if a date range is provided rather than a single year**)."*

**Three things #816's open question 1 did not reach.** The original element admits an **en-dash range**, not only `ca.` and `B.C.E.` The **narrative** form is documented three times, and the corpus contains **zero** — so the corpus alone would have argued against building it, and the clinician's ruling puts it in scope on APA's authority instead. And locators are **canonical parts** — `Song of Solomon 8:6`, `Inferno, Canto XIII, Lines 72–74`, `Tablet II` — not `p.`/`para.`; on the parenthetical path these fall after the date element and are already discarded, so **no locator work is in scope**, checked rather than assumed.

## Ruling 3 — the original half is parsed and never graded, because APA's own example fails that check

Open question 2 proposes reading the entry's `(Original work published …)` parenthetical so the row *"means anything beyond 'the second number matches'."*

**APA's classical-works page contradicts itself on exactly that join.** The Gilgamesh entry reads `(Original work published ca. 2500–2750 B.C.E.)` and its in-text citation reads `ca. 2750–2500 B.C.E./1998` — the range is reversed between the two. Both strings were pulled from the same DOM in one call. A rule joining the halves would report a defect against the example it is derived from.

So the original element is **parsed in order to find the slash and reach the year after it, and compared to nothing.** This is `SOURCE_CLASS_SETTLES_RETRIEVAL_DATE`'s declined join and [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s *refuse to invent a cut point where the corpus offers none*, arriving on a date element.

**The consequence is that this ticket changes no entry-side code at all.** Keying on the second element uses the year `resolution_keys` already yields.

## Ruling 4 — the grammar decides, and there is no anchoring

**This reverses a ruling made earlier in the same session, on evidence gathered after it.** The recommendation was ADR 0039 ruling 3's construction — accept the span only when its phrase keys to an entry listing the second element, *safe by construction because the key came out of the reference source*. It was made when the counter-example population was unknown.

Measured, over 700 corpus Markdown files:

```
slash-pair parentheticals                                    41
  author-shaped, in a document with no reference list        26
  never splits as <phrase>, <a>/<b>                          12
  author-shaped, in a grader-reachable document               3   all 3 resolve
```

All 26 out-of-list spans sit in documents with **no reference heading at all** — draft fragments, not prose with a coincidental slash — and 19 of 26 carry a one- or two-word author phrase. **29 author-shaped slash spans, zero false positives.** The `(4.8 percent in the 2013/2014 data)` class never splits, because the closing paren must follow the year or a comma-tail.

And anchoring costs something the baseline has: `(Smith, 1900/2010)` against no Smith entry is reported **today** as `unlisted-citation`. Under anchoring an unresolved span is never emitted, so it goes silent — on the row that catches a citation to a source in no reference list, which is what a fabricated citation looks like. **Trading a measured-zero false positive for a false negative on that row is the wrong direction**, and it is ruling 6's silent-versus-loud argument one row over.

So the grammar alone decides, the guard is `citation_key`'s existing proper-noun test, and the key is always the **second** element — which APA's *"earlier year first"* makes unambiguous without any lookup.

## Ruling 5 — the statute root leaves this ticket, and ADR 0135 ruling 1's assignment is superseded

[ADR 0135](0135-the-session-law-is-one-grammar-limb-the-loose-spelling-is-refused-and-the-legal-reader-states-its-composition.md) ruling 1 assigned #816 a second root — a year inside a statute's name — on the ground that *"the rule that has to change is the same one"*, the single-year equality in `_citation_findings`.

**Measured, neither fix changes that equality.** The republished fix changes what is *read as a citation*; the statute fix would change the author/date split. And the mechanism is not the one that record names — it needs a **comma-separated** year in the name **and** a differing entry year:

```
(Family & Medical Leave Act of 1993, 2006)      entry 2006   ->  clean
(Consolidated Appropriations Act, 2023, 2022)   entry 2022   ->  intext-year-mismatch
(Consolidated Appropriations Act, 2023, 2023)   entry 2023   ->  clean
(Widget Act, Special Edition, 2022)             entry 2022   ->  clean
```

`Act of 1993` is immune; `Act, 2023` is not. The name's own comma is read as the author/date separator, so the name's year becomes the date element and the entry's real year is read as a second year of one work.

**And the clinician's standing ruling is unsatisfiable here.** APA publishes no legal reference examples — confirmed against the live examples index, where legal is absent and Chapter 11 is manual-only. Of four library guides checked, two carry no paired in-text example at all and the two that do **contradict each other**:

| guide | entry | in-text |
| --- | --- | --- |
| College of St. Scholastica | `Family and Medical Leave Act of 1993, 29 U.S.C. § 2601-2654 (2006).` | `(Family & Medical Leave Act of 1993, 2006)` — full name, entry year |
| Franklin University | `No Child Left Behind Act of 2001, 20 U.S.C. § 6319 (2008)` | `(No Child Left Behind Act, 2001)` — shortened name, name's year |

There is no rule to check the scanner against. Settling it needs a clinician ruling on which convention this repository adopts — ADR 0039 ruling 1's kind of decision, not this one's.

**[#913](https://github.com/mshamblin5150-code/clinical-skills/issues/913) is the precedent and it points the same way**, having been filed separately on the explicit ground that it *"shares that ticket's two symptom rows and none of its root."* Three producers now land on these two rows; shared-row is not shared-root, or #913 would belong here too. ADR 0135's counter-warning — *splitting one equality across two tickets sends a builder at the wrong root* — governs two symptoms of one root, which measurement says these are not.

### ADR 0135's precision figure is corrected rather than superseded

That record states *"The row's live precision is 0 of 2."* The Bible finding is now confirmed false against APA's own page. The statute finding fires on `(Consolidated Appropriations Act, 2023)`, which is non-conforming under **both** guide conventions — a true positive with a misleading message — and the correct repair under the St. Scholastica convention *also* fires. **The honest figure is 1 confirmed false and 1 undecidable until this repository rules a legal convention.**

The earlier record is not edited, on the practice ADR 0135 ruling 8 states for itself: its verdict that the limb *does not cure the symptom* holds, and only the precision sentence is corrected here.

## Ruling 6 — both graders are repaired together, from one shared grammar object

The two failures have opposite signs, and the silent one is worse.

```
reference_scan        over-reports   exit 1   uncited-entry / intext-year-mismatch
discussion_post_scan  under-reports  exit 0   untraced-citation and respent-record skip
```

`discussion_artifact.read_citations` returns **nothing** for all five APA forms — including the plain arabic one `reference_scan` does read — so a republished citation gets a free pass on claim tracing and nothing says so. `discussion_reply_scan` shares that object under ADR 0039 ruling 4, so it is both graders. #816's open question 4 asked whether the sibling handles the form or never saw it; **it never saw it.**

The date element becomes one object in `discussion_artifact`, which `reference_scan` already imports `LEGAL_CITATION` and `LEGAL_SOURCE_VOCABULARY` from — **shared grammar, per-grader integration**, the established pattern one artifact over. Split across two tickets this is the trap ADR 0135 ruling 6 recorded live in these exact two files: two modules, one rule, held in step by nothing.

## Ruling 7 — `apa7.md` gains §31 as a date-element rule, and nothing renumbers

APA does not treat this as a reference form. §§9–29 are each `Reference form: <work type>`, and a republished work is a **state** any work type can be in — which is why APA carries the rule as §10.2 prose plus two blog posts rather than as a category.

§31 is appended, headed as a two-date rule spanning republished, translated, reissued, religious and classical works, taking [ADR 0129](0129-the-apa-form-heading-declares-itself-and-its-tail-is-exact.md)'s heading grammar and §29's four-part shape. Its **Provenance** names APA's own pages, and unlike §§9–29 its examples are APA's verbatim strings rather than synthesized ones.

**Nothing renumbers**, and that is not convenience: 52 section-number citations across 20 files, **10 of them ratified ADRs**. Editing those to keep a cross-reference alive is what ADR 0135 ruling 8 refuses, and [#233](https://github.com/mshamblin5150-code/clinical-skills/issues/233)/[#238](https://github.com/mshamblin5150-code/clinical-skills/issues/238) are this repository's recorded cost for renumbering a section anybody cites. §3 and §5 gain a pointer to §31; **the row labels do not repoint** — `intext-year-mismatch` stays `apa7 3`, since it serves the ordinary year disagreement too.

## Ruling 8 — the fixtures are APA's strings, extracted from the sheet rather than retyped

`tools/test_reference_scan.py` builds synthetic drafts and keeps doing so. But this ticket's whole authority is APA's published examples, and hand-typing them makes the sheet and the test two copies of one rule with nothing between them — [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) at the width of the evidence the ticket rests on.

`TheRxTableTheStyleSheetDocuments` is the pattern: it extracts the table from `style.md` and renders it, precisely because every `Rx:` test that shipped with that repair used rows typed into the test file. So the §31 test extracts APA's forms **from the sheet** and drives them through the scanner, in both directions — every published form parses and resolves clean, and each `NOT_REACHED` residue gets a positive control proving its path is live.

**Two mutants before the coverage claim is believed.** Drop the `ca.`-plus-range limb and the Gilgamesh form must go red; drop the narrative limb and `Watson and Rayner (1920/2013)` must go red. The second is the one that would otherwise pass for the wrong reason, since the corpus has zero narrative slash spans and only APA's own example exercises it.

## Ruling 9 — two residues are declared, and the naming-convention question is left alone

Into `reference_scan.NOT_REACHED`, which is inside `test_declared_limits.declarers()`'s walk:

- **The original half is parsed and never graded** — `(Freud, 1899/2010)` passes with a wrong original year. Ruling 3's reason rides on the row, because a reader who does not know about APA's Gilgamesh inconsistency will try to close it.
- **An author-shaped non-citation could raise `unlisted-citation`** — `(Cohort A, 2013/2014)`. Zero instances in 700 files, and the same residue `citation_key` already declares for a capitalized common noun.

`discussion_post_scan.DECLARED_LIMITS` gains one row for the shared grammar's behaviour on its two citation rows.

**The convention problem is deliberately not settled here.** `discussion_artifact` holds `LEGAL_READER_NOT_REACHED`, which ADR 0135 ruling 5 recorded as *"a third naming convention and the one convention no walk sees"* and deferred to [#867](https://github.com/mshamblin5150-code/clinical-skills/issues/867)/[#875](https://github.com/mshamblin5150-code/clinical-skills/issues/875). A fourth object beside it would settle that in passing from a ticket about a translated work. The shared **grammar** lives in `discussion_artifact`; its **limits** live in the two graders' walked objects.

## Ruling 10 — the pasteable guarantee does not widen

The fix adds no `BODY_ROWS` member: it touches `INTEXT_YEAR_MISMATCH` and `UNLISTED_CITATION`, both already members. `citation.year` carries **the second element only** — the original element is parsed and discarded, never emitted. `--show` stays the one output in `tools/` that may be pasted whole, on the terms ruled 2026-08-19, rather than being quietly widened by a grammar change.

## What none of this reaches

**Whether a cited republished work exists or says what the draft claims.** The research and refutation passes own it, unchanged.

**`King James Bible (1769/2017)`**, APA's own religious-work narrative example. It needs this ticket **and** #913: with the slash removed entirely the narrative form keys as `bible` against an entry keyed `king`, so neither ticket alone makes it work. Recorded in both.

**A non-ASCII surname.** `Kübler-Ross (2014)` — APA's §10.2 example-4 author, slash removed — keys as `ross` narratively and `k` in its entry, raising `unlisted-citation`. A fourth independent producer of these rows, filed separately from this session.

**An unread citation-shaped span.** Neither module reports one; `reference_scan` prints `in-text citations read` with no denominator, which is why this bug surfaced as `uncited-entry` two rows from its cause. That is CLAUDE.md's extractor rule — *a matcher never gets to turn a partial read into a clean whole* — unapplied at this seam. Filed separately, because it is a coverage-reporting change across two grader families rather than a citation-grammar fix.

**Whether the corpus figures survive the next draft.** Three live instances ground the republished root and zero ground the narrative limb; APA's page grounds the latter instead. The measurement moves the next time the clinician writes a case study.
