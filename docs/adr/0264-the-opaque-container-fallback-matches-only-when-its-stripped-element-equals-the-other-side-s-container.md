# The opaque-container fallback matches only when its stripped element equals the other side's container

**Measured at:** 726c97123730d3e652861bbe60055cc1f1f75f50

[#1243](https://github.com/mshamblin5150-code/clinical-skills/issues/1243) was filed by the tracker sweep after [#1021](https://github.com/mshamblin5150-code/clinical-skills/issues/1021) and PR #1241. Grilled against `main` at `726c9712`; the freshness gate read `FRESH` there. The clinician ruled every point below in that session. **Nothing is built here; this is the record the build reads.**

## What was measured before ruling

`research_ledger.reference_identities` was driven directly, author and year held at `Author, A. (2026).`:

```text
Care in the U.S. Alpha.        vs  Care in the U.S. Beta.              match
Care in the U.S. Alpha.        vs  Care in the U.S. Beta, 1(2), 3-4.   match
Care in the U.S. Alpha.        vs  Care in the U.S. Alpha, 1(2), 3-4.  match
Care in the U.S. Clinicalgada. vs  Care in the U.S. Dynafoo.           match
Care in the U.S. Journal A.    vs  Care in the U.S. Journal B.         match
U.S. Healthcare. Journal.      vs  U.S. Medicine. Journal.             differ
```

The first row is the ticket's defect: a sourced record for Alpha reads as listed when only Beta is in the draft, and the command exits 0. The second row is the same collapse through the mixed path, which the ticket did not name.

**The ticket's two requirements collide byte for byte.** It asks for Alpha and Beta to differ while preserving #1021's behavior for unfamiliar one-word and multi-word containers, and `test_a_one_word_unfamiliar_container_after_an_abbreviation_is_metadata` pins row 4 as a match. Rows 1 and 4 have one shape: shared text ending in an initialism, a period, and one unrecognized capitalized element. No function of the two strings separates them, so one requirement has to give.

That preservation clause rested on a builder's test, not a ruling. [ADR 0211](0211-an-uptodate-entry-is-checked-against-its-masthead-and-a-sourced-record-is-cited-or-dropped.md) ruling 5 requires the key and the normalized title to agree, and names italics, a retrieval date and an added DOI as the ordinary edits a match must survive. It never ruled a container change ignorable. The opaque alias arrived in `8567cac7`, the #1021 build.

## Ruling 1 — the stripped element is part of identity

When the fallback supplies a title by stripping a final unrecognized element as an opaque container, that element counts toward identity. A fallback identity matches another fallback identity only when their stripped elements are equal after normalization. Row 1 now raises `sourced-record-not-listed`. The two #1021 tests pairing *different* unfamiliar containers — `Clinicalgada` with `Dynafoo`, and `Clinicalgada Archive` with `Dynafoo Library` — flip from exit 0 to exit 1. The same unfamiliar container on both sides still matches.

## Ruling 2 — in the mixed case the stripped element must equal the named container

When one side's title comes from the fallback and the other side's title is read ordinarily ahead of a container it names, the stripped element must equal that container name after normalization. The container name is the text after the title up to its first comma. `Alpha.` against `Alpha, 1(2), 3-4` matches; `Alpha.` against `Beta, 1(2), 3-4` does not. The rule is symmetric: it applies whichever of the record or the draft entry carries the fallback.

## Ruling 3 — ruling 5 is unchanged where both titles read unambiguously

The equality applies only where the fallback produced a title, because only there is the element a container by assumption. Where both titles read ordinarily, ADR 0211 ruling 5 stands as written: key plus title, container ignored. `Journal A` against `Journal B` and `ClinicalKey, 1` against `DynaMed, 2` keep matching, and their tests do not move.

## Rejected options

**Declare the collapse and keep the match.** It is the silent direction: a sourced record whose source never reached the draft exits 0. A disagreement between record and draft over a container is a real inconsistency, and reporting it is the loud failure this gate should have.

**Refuse any reference whose final element after an abbreviation cannot be classified.** It would refuse a record and entry that name the same unfamiliar container, a pair ruling 1 matches correctly.

**Compare containers on every entry.** It rewrites ruling 5 for the whole list and fails one journal written two ways, `N Engl J Med` against `New England Journal of Medicine`, an ordinary difference between research and the final list that ruling 5 was written to survive. No recorded defect asks for it.

**Stop only fallback-to-fallback matches.** It leaves row 2 matching, so a title-only record would satisfy every same-author, same-year entry whose title is a prefix of it followed by any container with metadata.

## What the build owes

- `tools/test_research_ledger.py`: rows 1 and 2 as failing cases before the fix; the two differing-unfamiliar-container tests flipped to exit 1 and renamed for what they now assert; same-container one-word and multi-word controls at exit 0; `Alpha.` against `Alpha, 1(2), 3-4` at exit 0 in both directions.
- `reference_identities`' docstring states ruling 1's equality and ruling 3's scope.
