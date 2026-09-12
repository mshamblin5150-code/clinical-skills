# Citation resolution is a named directional relation and the no-surname branch keys on the title proper

[#959](https://github.com/mshamblin5150-code/clinical-skills/issues/959) reports that a correctly cited translated work does not resolve, because the translator's credit enters the reference-side key while the in-text citation names only the title. Grilled 2026-09-12 on `main` at `595fbb88ea68eda1557487e35e7ba050062f6be9`; the freshness gate read `FRESH` at the opening checkpoint. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

Every figure in this record was taken by driving the modules, entries through `reference_keys` and citations through `read_citations` and `citation_occurrence_keys`. That is stated because [ADR 0150](0150-the-narrative-author-phrase-stops-at-a-sentence-boundary-and-a-leading-article-is-ignored-quote-aware.md) records two earlier sweeps on this exact seam reaching false conclusions, and names the cause: *"Both ran `reference_keys` — an entry parser — on a citation string."*

## The defect, end to end, on APA's own example

The pair is `apa7.md` §31's Gilgamesh row, which this repository publishes as the form a run should copy:

```
reference_keys('The epic of Gilgamesh (M. G. Kovaks, Trans.). (1998). ...')
    -> (('epicofgilgameshmgkovakstrans', '1998'),)
read_citations(...)        -> ('The Epic of Gilgamesh', '1998')
citation_occurrence_keys   -> (('epicofgilgamesh', '1998'),)
resolves: False
```

`peer_critique_scan` and `discussion_reply_scan` raise a false `unresolved-citation` and exit 1. This is not a silent negative: the citation is read, and the finding is loud and wrong.

## Two of the ticket's own premises are corrected

**The bar it rests on does not name the module it targets.** The body states that *"ADR 0145 ruling 3 explicitly barred entry-side key changes in #816, so this needs a separate design decision."* [ADR 0151](0151-the-citation-author-date-split-is-evidenced-by-the-reference-list.md) states the preserved prohibition exactly: *"The prohibition ADR 0150 ruling 1 preserves is on the entry side — `Entry.key`, `resolution_keys`, and new key vocabulary."* Those are `reference_scan` symbols. `discussion_artifact.reference_keys` is named in no prohibition, and [ADR 0145](0145-the-republished-date-element-is-shared-grammar-keyed-on-its-second-element.md) ruling 3's *"this ticket changes no entry-side code at all"* is a statement of #816's scope rather than a rule. The design decision is still real, because ruling 2 below is genuinely hard; the stated reason one was needed is not.

**The adjacent normalization limb does not exist in this module.** The ticket's first comment attributes a normalization-form-dependent truncation to `author_key`. Driven:

| input | `author_key` NFC | `author_key` NFD | `citation_key` NFC | `citation_key` NFD |
| --- | --- | --- | --- | --- |
| `Kübler-Ross` | `küblerross` | `küblerross` | `kubler ross` | `ku` |
| `Ångström` | `ångström` | `ångström` | `angstrom` | `a` |

`author_key` normalizes to NFC first and keeps the letter through `isalnum()`, so it never truncates and is normalization-stable. The truncation is `reference_scan.citation_key`'s, which is [#943](https://github.com/mshamblin5150-code/clinical-skills/issues/943) and closed. What is live is a residue of that fix rather than a limb of this ticket, and ruling 10 files it.

## Ruling 1 — the root is the no-surname branch, and the translator is one instance of it

`reference_keys` falls through to keying the whole author text whenever no `Surname, I.` pattern is present. So the credit is not special:

```
The epic of Gilgamesh (M. G. Kovaks, Trans.)  -> epicofgilgameshmgkovakstrans
The handbook of nursing (J. Smith, Ed.)       -> handbookofnursingjsmithed
Nursing today (2nd ed.)                       -> nursingtoday2nded
```

Widening from *translator* to that branch is the widen-not-split call, because the three are one `else` and no fix reaches only the first.

**The branch is not the title-as-author branch, and the record says so rather than leaving a reader to find it.** The same fall-through keys group authors — `World Health Organization` reaches it too — and nothing in the code separates a title from a corporate name. The population measurement hit the same wall independently. Every ruling below that says *this branch* means **the branch where no personal surname was detected**.

The three other producers the thread collected on this seam do not share this mechanism and leave with ruling 10: APA §8.20's in-text initials are a citation-side form, the fold above is `reference_scan`'s, and the en-dash citation form is a date grammar already carried as a measured member of [#1066](https://github.com/mshamblin5150-code/clinical-skills/issues/1066). This is ADR 0145 ruling 5's own test — shared row is not shared root — applied to the ticket that record spawned.

## Ruling 2 — a shortened title resolves, because that is APA's stated in-text form

`apa7-coverage.md` records §8.14 as `read-root`: *"A truly unnamed author is replaced in text by a shortened title and year."* The shortening is APA's rule, not slack a writer takes. So stripping the credit and requiring full-title equality leaves this failing on APA-correct input:

```
entry : Diagnostic and statistical manual of mental disorders (5th ed., text rev.). (2022).
        -> diagnosticandstatisticalmanualofmentaldisorders
cit   : (Diagnostic and Statistical Manual, 2022)
        -> diagnosticandstatisticalmanual                    MISS
```

The clinician's standing ruling, made on #816 and reaffirmed here, decides it: *"Pull the APA 7 rule. If the scanner cannot match what the APA rule is, it is a scanner defect and must be repaired."*

**The corpus argues the other way and is overruled on the same ground ADR 0145 used.** Measured across every root this account owns — tracked Markdown, `output/`, and `scratch/` — the shape has **one** live instance, and it is APA's own example in `apa7.md` itself:

| root | reference entries | title-as-author | with a credit before the year |
| --- | ---: | ---: | ---: |
| tracked `.md` | 52 | 14 | **1** |
| `output/` | 135 | 13 | **0** |
| `scratch/` | 6,886 occurrences, 1,049 distinct | 62 occurrences, 27 distinct | **0** |

ADR 0145 ruled this exact fact pattern for the narrative slash form, which had zero instances: *"the corpus alone would have argued against building it, and the clinician's ruling puts it in scope on APA's authority instead."* The honest statement is that this fix buys correctness against APA and nothing measurable against today's drafts, and that §31 teaches the next run to write the shape.

What exists in volume instead is legal-name entries — 13 in `output/`, 38 in `scratch/` — whose source and section `LEGAL_CITATION` already strips before the fall-through. Ruling 4's table is where that is checked rather than assumed.

## Ruling 3 — `discussion_artifact` only, and the divergence is already ratified

`reference_scan` holds a second implementation and resolves the same pair clean, which is what §31's table records. It does so by being lax rather than right:

```
entry: The epic of Gilgamesh (M. G. Kovaks, Trans.). (1998).  -> ('epic', '1998')
(The Epic of Gilgamesh, 1998)              -> epic   resolves   correct
(The Epic of American Civilization, 1998)  -> epic   resolves   a different work
(The epidemiology of sepsis, 1998)         -> ''     dropped    silent
```

So the two sit at opposite extremes of one rule: whole-string equality raises false alarms, one-word equality misses real ones.

Taking both was the strongest counter available, and it is ADR 0145 ruling 6 on this exact file pair: *"Split across two tickets this is the trap ADR 0135 ruling 6 recorded live in these exact two files: two modules, one rule, held in step by nothing."* It is refused because the divergence here is ratified rather than drifted. ADR 0151: *"the divergence is by design rather than drift."* ADR 0150: *"They now hold two different ones deliberately, and nothing binds them."* #942's prohibition refuses *"a shared candidate recogniser that forces one key function on both modules."* A shared recogniser is permitted; a shared key function is not.

`reference_scan` was lax before this ticket and stays lax without it, so it is inherited rather than entangled. Ruling 10 files it with the measurement, and with the `NOT_REACHED` row that states what its clean run means.

## Ruling 4 — the key is the title proper, taken by position rather than by vocabulary

The entry's first element is not the answer. For a work with no author APA moves the Title element into the author slot, and the credit is *inside* that element, closed by the period before the date — so keying on the element reproduces the bug. What APA drops in text is narrower: the **title proper**, with any trailing parenthesized group removed.

Removal is by position — a trailing run of `(...)` groups — and never by a vocabulary of `Trans.`, `Ed.`, `Eds.`, `nth ed.`, `Rev. ed.`. A list goes stale the next time APA is read, and a miss silently recreates today's bug.

**Driven before it was believed, and the legal non-regression is the half that matters:**

| entry | current key | under the rule |
| --- | --- | --- |
| `The epic of Gilgamesh (M. G. Kovaks, Trans.)` | `epicofgilgameshmgkovakstrans` | `epicofgilgamesh` |
| `Nursing today (2nd ed.)` | `nursingtoday2nded` | `nursingtoday` |
| `Professional and Vocational Regulations, 16 CCR § 1481` | `professionalandvocationalregulations` | unchanged |
| `Eligibility for prescriptive authority, W. Va. Code § 30-7-15b` | `eligibilityforprescriptiveauthority` | unchanged |
| `Payment for nurse practitioners' … services, 42 C.F.R. § 414.56` | `paymentfornursepractitioners…` | unchanged |
| `Consolidated Appropriations Act, 2023, Pub. L. No. 117-328, § 1263` | `consolidatedappropriationsact2023` | unchanged |
| `Advanced practice registered nurse licensure requirements (W. Va. Code R. § 19-7, 2024)` | `advancedpracticeregisterednurse…` | unchanged |
| `King James Bible.` / `World Health Organization.` / `Smith, J.` | — | unchanged |

`LEGAL_CITATION` takes every legal shape before the fall-through, including the one whose author slot is itself a parenthetical. The rule moves the branch it is aimed at and nothing else.

**The first version of that table was measured wrong and is recorded because the error is reusable.** It was taken against strings with the `§` removed, so the legal entries never took the legal branch and the safety claim rested on shapes that do not occur. The character is what selects the branch.

## Ruling 5 — the comparison is a named relation, never `in`

The join is written six times — in `peer_critique_scan`, in `discussion_reply_scan`, twice in `discussion_post_scan` including the per-record `ClaimReferenceIndex` walk, and inside `read_citations`, whose parameter is already typed `Collection[tuple[str, str]]`. Ruling 2 changes the comparison rather than the keys, so all six are copies of one rule and leaving them is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).

Overriding `__contains__` on a reference-key-set type would land for free — not one call site would change, because `Collection` is already the declared type, and `discussion_post_scan.ClaimReferenceIndex` already writes a hand-rolled `__contains__`. **It is refused anyway.** `CONTEXT.md` already rules why: **Citation key** is *"a name rather than an identity"*, membership is an identity relation, and after ruling 2 the relation is not even symmetric. A `Collection` whose `__contains__` answers a different question than its `__iter__` enumerates is a trap this repository has recorded passing for the wrong reason, and `key in refs` reads as membership to every reader who knows the protocol.

So the type exposes `resolves`, the six sites call it, and `read_citations`'s parameter widens with them. `ClaimReferenceIndex`'s per-record test takes the type too — otherwise claim tracing keeps the old comparison while citation resolution gets the new one, which is one rule answering two ways inside one grader.

## Ruling 6 — a plain character prefix, and the mid-word residue is declared

`author_key` ends in `isalnum()`, so the key carries no separators and containment on it is a plain character prefix. A boundary-aware comparison would need the key to keep its spaces, as `reference_scan.normalize` does, which moves every key this module produces and every comparison in three graders.

It is refused on the direction of the failure it prevents. A plain prefix resolves a citation that stops mid-word — `Nursing tod` against `Nursing today` — which nobody writes and no draft in the account contains, and which costs a **lost finding** on malformed input. The boundary-aware version costs a key-vocabulary change across three graders to refuse it.

Group authors ride the same branch, so a citation naming part of a group's name resolves although §8.21 does not license the short form. Same direction, same posture: declared, not fenced.

## Ruling 7 — `Citation resolution` enters the glossary and names the method

> **Citation resolution**:
> The directional relation one **Citation key** bears to an artifact's reference key set. The years must agree, a yearless entry key answering to any. The author halves must be **equal** where the entry yielded a personal surname, and the citation's may be a **character prefix** of the entry's where it did not — which is every entry whose author slot is a title or a group name, because APA replaces a missing author in text with a shortened title. So it is neither membership nor symmetric: a citation naming a shortened title resolves against the entry, and the entry's key does not resolve against the citation's. Distinct from the looser sense of resolving a path, a filename or a step citation, where one name is turned into one thing that either exists or does not.
> _Avoid_: match, key match, lookup, membership, citation hit

`resolve` rather than a fresh word, because the finding kind a reader sees is `unresolved-citation`, the symbol is `resolution_keys`, and **Citation key** already says *"before the citation counts as resolved"*; inventing one would make the glossary disagree with the row name on the page. The looser-sense clause follows **Spend**, which handles its own overloaded verb the same way. `match` leads the `_Avoid_` line because both **Citation key** and **Grouping key** already refuse it and it is the word a builder reaches for once the comparison stops being equality.

`test_glossary_collisions.DECLARED_CANDIDATES` already rules `Citation` a `COLLISION` whose compounds name *"other kinds of reference or how one is checked"*, which is the slot this falls into; its reason gains this member.

## Ruling 8 — the residues are one object spliced into three graders, superseding ADR 0145 ruling 9's placement

Three rows are declared: a citation shortening a title past the point a second entry also matches resolves against both; a citation naming part of a group author's name resolves; a citation stopping mid-word resolves. All three are `EvidenceDisposition.BEHAVIOR` — statements about what the comparison does, not readings assigned to a person.

`discussion_artifact.CITATION_RESOLUTION_NOT_REACHED` holds them in the graders' `(subject, reason, disposition)` shape, and each grader's `DECLARED_LIMITS` splices it in, so `NOT_REACHED` derives exactly as it does today. One statement, three complete views.

**ADR 0145 ruling 9 said the opposite and its reason is discharged.** It refused *"a fourth object beside it"* in `discussion_artifact` because that would settle a naming-convention question *"deferred to #867/#875"*. Both are closed. `discussion_artifact` is already a declarer — `test_declared_limits.declarers()` returns it, `LEGAL_READER_NOT_REACHED` is already walked, and the module is not in `NO_LIMITS` — so a second object is a further member of a convention the module already has rather than a new one.

**And the rule it stated has already failed in the tree, measurably:**

```
discussion_post_scan    17 limits rows  -> "whether a republished citation's original year matches its source"
discussion_reply_scan   17 limits rows  -> absent
peer_critique_scan       7 limits rows  -> absent
```

All three run the shared grammar. Two of them say nothing about a residue their own clean runs carry, which is the contract of that object broken by the record that wrote the rule.

Ruling 9 stands as to **where a reader finds a limit** and is superseded as to **where it is written**. The earlier record is not edited, on the practice ADR 0135 ruling 8 states and ADR 0145 itself follows.

## Ruling 9 — the fixtures are extracted from the sheet and synthetic beside it, and a legal control is mandatory

ADR 0145 ruling 8 requires §31's fixtures be extracted from `apa7.md` rather than retyped, because hand-typing APA's strings *"makes the sheet and the test two copies of one rule with nothing between them."* That holds and is the bind that fails when the sheet moves.

It does not reach this ticket's other shapes, because APA exemplifies none of them in §31 — no edition statement, no editor credit, no shortened title. Synthetic cases sit beside the extracted ones for those. Ruling 8's reason is not weakened: it refuses a hand-typed copy of an APA string, and APA publishes none of these to copy, so there is no second copy to drift.

**The legal control is not optional.** Ruling 4's whole safety argument is that `LEGAL_CITATION` is consulted first, and nothing in the suite asserts that ordering today. A reordering would silently change the key of 51 real reference entries with every test still green, so the control asserts ruling 4's table byte for byte.

## Ruling 10 — five findings are filed rather than built

None widens this ticket: #959's fix is correct without every one of them, and every one predates it.

1. **APA §8.20 in-text first-author initials.** `J. M. Taylor` keys `jmtaylor` against an entry keyed `taylor`; `reference_scan` keys `j` and misses it too; the plain-surname control resolves. Nothing on the tracker owns it. It is filed `grilling` rather than `ready-for-agent` because a reading is open underneath it: `apa7-coverage.md` grounds §8.20 in `apa7.md` §38, which says to disambiguate when the short form would collide and does not say to spell out initials, so whether a run ever writes the form is the clinician's to rule.
2. **`reference_scan.citation_key` still truncates NFD input.** #943's fix is NFC-only and #943 is closed.
3. **`reference_scan` resolves a citation naming a different work**, per ruling 3's table, and drops a lowercase-opening title silently. Carries the `NOT_REACHED` row ruling 3 leaves over.
4. **The republished-original-year limit is stated in one grader of three**, per ruling 8's counts. It is the closest call here, because ruling 8 builds the mechanism that repairs it in two lines — but it is a different rule about a different residue, and folding it in would have this ticket repair a row it never measured a defect in.
5. **§31's table column reads as a general resolution claim** while being scoped to `reference_scan`. This ticket's fix makes that row true for all four graders, so what is left is the column header.

## What none of this reaches

**Whether a cited work exists or says what the draft claims.** The research and refutation passes own it, unchanged.

**Whether `reference_scan` and `discussion_artifact` agree after this lands.** They agree less, not more: a citation naming a different work with the same first word now fires correctly in three graders and still resolves clean in `reference_scan`. That is ruling 3's accepted cost and ruling 10 item 3 is where it is stated.

**Whether the population survives the next draft.** One live instance grounds the shape today, and §31 exists to teach the next run to write it. The measurement moves the first time the clinician cites a translated work.
