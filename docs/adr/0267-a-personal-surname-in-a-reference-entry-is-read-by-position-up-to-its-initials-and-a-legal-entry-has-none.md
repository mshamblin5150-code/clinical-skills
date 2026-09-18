# A personal surname in a reference entry is read by position up to its initials, and a legal entry has none

**Measured at:** 143c30cc543cb7c809f6c15fb464acc51be25a96

[#1368](https://github.com/mshamblin5150-code/clinical-skills/issues/1368) was filed from [ADR 0263](0263-reference-scan-resolves-a-no-surname-entry-by-title-proper-prefix-and-reads-apa-8-21-group-abbreviations-through-one-shared-recognizer.md) ruling 2, which kept an unhyphenated multi-word first-author surname on the surname path and refused to widen the detector inside #1169. Grilled against `main` at `143c30cc`; the freshness gate read `FRESH` there. The clinician ruled every point below in that session. **Nothing is built here; this is the record the build reads.**

## What was measured before ruling

Both readers detect a personal author as one capitalized token followed by `, I.`. Driven at `143c30cc` on the citation side:

```text
reference_scan.citation_key('M. Garcia Lopez')      -> 'mgarcia'
reference_scan.citation_key('A. Van der Berg')      -> 'avan'
discussion_artifact.author_key('M. Garcia Lopez')   -> 'mgarcialopez'
discussion_artifact.missing_first_author_initials('Garcia Lopez')
    reads 'Garcia', finds remainder 'Lopez' is not &/and/et al.  -> False
```

The entry-side misreads are the ticket's own table and are not restated here.

A positional read — everything before the comma that precedes `I.` initials — was run over every reference list reachable from this checkout: the owning checkout's `output/` and every tracked `.md` file. 182 documents carrying a reference list, 512 entries:

| shape of the author slot | entries |
| --- | ---: |
| no `, I.` initials anywhere in the first author position | 409 |
| single-token surname, read correctly today | 93 |
| multi-word run before `, I.` | 10 |

Of the 10, **three are real personal surnames** — `Lindholm Olinder`, `Aptilon Duque` and `St. Peter` — and **seven are West Virginia Code legal entries** whose `, W. Va. Code §` reads as an initial. The shared legal-citation grammar classifies all seven as legal and none of the three, so it separates the population exactly, ten of ten.

**This corrects #1169's figure.** That measurement found one live entry; there are three, and `St. Peter` — a period inside the surname followed by a space — is a third shape the single-token rule misses. The population is the working set as it stood on the day measured and moves with the next draft, so no count here is pinned.

## Ruling 1 — a personal surname is read by position, not by vocabulary

In a reference entry APA §9.8 writes every personal author `Surname, I.`, so the entry itself marks where a surname ends: the comma immediately before the initials. The surname is everything from the start of that author — the start of the slot, or the preceding author separator — up to that comma. `Garcia Lopez, M.` reads `garcia lopez`; `Van der Berg, A.` reads `van der berg`. This holds for every author in the slot, not only the first.

A particle vocabulary was refused. It would still miss `Garcia Lopez`, which carries no particle and is the shape the real drafts contain, and a surname nobody anticipated would silently recreate the defect. `PARTICLES` belongs to the in-text side, where there are no initials to mark the boundary.

## Ruling 2 — a legal entry has no personal author

An entry matching the shared legal-citation grammar is never read as having a personal author, whatever its `, W.` looks like. Its keys stay exactly as today; the single-token rule already returned nothing on all seven measured legal entries, so nothing legal moves.

## Ruling 3 — `reference_scan` stays first-word lax

`Entry.key`, the `a`/`b` grouping and bare citation matching do not change, which answers [ADR 0150](0150-the-narrative-author-phrase-stops-at-a-sentence-boundary-and-a-leading-article-is-ignored-quote-aware.md) ruling 1's *neither key moves* by leaving both keys where they are. `first_author_initials` reads the positional surname, so the initialed resolution key and the `missing-first-author-initials` row see it. This is the laxness [ADR 0195](0195-citation-resolution-is-a-named-directional-relation-and-the-no-surname-branch-keys-on-the-title-proper.md) ruling 3 ratified: `(Garcia Martinez, 2020)` still resolves clean against `Garcia Lopez, M. (2020)` through the first-word key, and `reference_scan`'s `NOT_REACHED` gains that row.

Making `reference_scan` exact — the citation side reading the whole phrase and the first-word match dropped where a surname is known — was declined here as not entangled with this ticket's correctness. It would need its own corpus measurement and its own answer to ADR 0150.

## Ruling 4 — the citation side reads the surname by position in two places only

Widening the entry side alone makes the `missing-first-author-initials` row go silent on multi-word surnames in both modules and leaves `(M. Garcia Lopez, 2020)` a false unlisted citation in `reference_scan`. So on the citation side the surname runs from after any leading initials to `&`, `and`, `et al.` or the end of the author phrase, and it is read that way in exactly two places:

- the initialed citation form: `(M. Garcia Lopez, 2020)` keys `mgarcialopez` in `reference_scan`, which `discussion_artifact` already does;
- the `missing-first-author-initials` comparison in both modules, where `reference_scan` reads `Citation.phrase` rather than `key`. `(Garcia Lopez, 2020)` against `Garcia Lopez, M.` and `Garcia Lopez, R.` fires; against `Garcia Lopez, M.` and `Garcia Martinez, R.` it does not.

The bare narrative and parenthetical key in `reference_scan` stays the first word, per ruling 3.

## Ruling 5 — `discussion_artifact` becomes exact

With ruling 1 its reference keys read `garcialopez` and `garcialopezandsmith`, which repairs all three of its reported failures: keying the entry on its second author, the false unresolved citation for `(Garcia Lopez & Smith, 2020)`, and accepting `(Smith, 2020)`.

## Ruling 6 — one shared positional recognizer, two key functions

The positional surname recognizer is built once in `discussion_artifact` and consumed by `reference_scan` under its own normalization, on ADR 0263 ruling 7's arrangement. #942 and ADR 0195 ruling 3 permit a shared recognizer and forbid a shared key function; each module keeps its own.

## Ruling 7 — controls

Driven through both modules' public seams:

- the three live shapes as liveness cases: a double surname, a double surname with a coauthor, and a surname carrying an internal period and space;
- `Van der Berg, A.` for the particle form;
- the committed West Virginia Code legal shapes and ADR 0195 ruling 4's legal table as the non-regression control, keys asserted unchanged;
- `World Health Organization.` as a group author, unchanged;
- `Garcia, M.`, `Smith, J.` and a hyphenated `Garcia-Lopez, M.` as single-token controls, unchanged;
- the missing-initials row fired by two same-surname multi-word entries and not fired by two entries sharing only a first word.

## What none of this reaches

A non-legal group author written with a trailing initial-shaped abbreviation, such as `Department of Health and Human Services, U.S.`, reads as a personal author. The measured population holds none; it is declared in both modules' limits objects rather than guarded by a vocabulary. `reference_scan`'s first-word false clean, per ruling 3. Whether a cited work exists or says what the draft claims.
