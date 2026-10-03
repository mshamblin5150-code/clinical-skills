# A deck strips a citation year only when a claim record names the source

**Measured at:** f223749c6124bf0c311e9827cdeaa9a9dc17883f

[#1254](https://github.com/mshamblin5150-code/clinical-skills/issues/1254) was filed from
[#1034](https://github.com/mshamblin5150-code/clinical-skills/issues/1034)'s post-merge sweep.
[ADR 0218](0218-a-slide-s-agreement-with-its-record-is-read-and-every-deck-number-is-traced.md)
ruling 3 made `untraced-figure` read every deck number through the stripping
`discussion_post_scan.traceable_numeric_values` applies, and that stripping removes every span the
shared citation reader recognizes. An ordinary slide label in the shape `Opening (2027)` is one of
those spans, so a deck could state an unrecorded schedule year and exit clean. Grilled 2026-10-03
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

### The false clean is live

At this record's commit, `traceable_numeric_values` returns no number for `Phase II (2027)` or for
`Opening (2027)`, and returns `2027` for `Opening in 2027`. Had the year not been stripped, the first
two would have returned `2027` as the third does, so the reading discriminates. #1254's sweep
comments add that SmartArt text and chart titles reach the same reader since #1276.

### Wording cannot separate a label from an author

The shared reader returns `(Opening, 2027)` and `(Phase II, 2027)` as author-year pairs in exactly
the shape it returns `(Smith, 2020)`. No lexical rule tells a schedule label from a surname, so a
narrower citation pattern is not a fix.

### The evidence that separates them is already in the run

`ReferenceKeySet.from_references` turns a claim record's `REFERENCE` value into author-year keys:
`Smith, J. (2020)` yields `smith` and `jsmith` with `2020`. The reference key set the shared reader
accepts narrows only abbreviation definitions, not narrative or parenthetical citations, so passing
it unchanged would not have helped. `deck_scan` passes no reference evidence at all today.

### The two sibling graders are not false-clean

`assignment_docx_scan` and `discussion_post_scan` also strip the year, and each then runs an
`untraced-citation` row that requires every in-text citation to resolve to a claim record's source.
`Opening (2027)` resolves to none and is reported there. This was read from the code at this
record's commit and was not driven; ruling 3 makes the build drive it.

### Reference slides carry no reader

`deck_scan` knows which slides are references only when the presentation-intent record declares
`REFERENCE-SLIDES`, and uses that population only for the slide limit. Nothing in the tree reads APA
entries out of slide text.

## Ruled 2026-10-03

### 1. A deck strips a citation-shaped year only on reference evidence

Before `untraced-figure` reads a deck number, a span the shared citation reader recognizes is
removed only when its author and year resolve to a reference named in the run. Every other
citation-shaped span stays in the text, and its year is a number that needs a claim record like any
other. `deck_scan` keeps calling `traceable_numeric_values` and supplies the filtered citations
through its existing `citations` parameter, so ADR 0218 ruling 3's single number reader and shared
stripping stand; only the set of spans stripped narrows. Resolution uses the matching the sibling
`untraced-citation` rows already use, not a new author comparison.

### 2. The evidence is the claim records' REFERENCE fields, believed or not

The references that count are the `REFERENCE` values of every claim record in the run's ledger. A
disbelieved record still counts: whether a record was refuted does not change whether
`(Smith, 2020)` is a citation. The deck's reference slides are not read and no slide-entry reader is
written. A slide citing a source no claim record names therefore has its year reported, which is the
gap ADR 0208 and ADR 0218 already want surfaced.

### 3. The fix is the deck's alone

`discussion_post_scan.traceable_numeric_values`, `discussion_artifact`'s citation reader,
`assignment_docx_scan` and `discussion_post_scan` do not change. The build adds one synthetic control
to each sibling's tests showing `Opening (2027)` produces `untraced-citation`, so their coverage is
driven rather than read and cannot be removed unnoticed.

### 4. Coverage and the remaining boundary

Synthetic deck tests cover, through the public `deck_scan` seam:

- `Opening (2027)` and `Phase II (2027)` on a slide face with no claim record: `untraced-figure` for
  `2027` and exit 1;
- the same text in a SmartArt node and in a chart title: the same finding;
- `(Smith, 2020)` beside a claim record whose `REFERENCE` is a Smith 2020 entry: `2020` is not
  reported;
- the same citation whose only matching record is disbelieved: `2020` is not reported;
- `(Smith, 2020)` with no claim record naming Smith 2020: `2020` is reported.

`deck_scan.DECLARED_LIMITS` gains a row: a label whose words and year coincide with a cited
author and year in the run's claim references is still stripped.

## Rejected options

**Keep the shared stripping and declare the false clean.** The row would stay blind to an
unrecorded schedule year, and the backstop would be a prose reader ADR 0218 already declares
unverified.

**Stop stripping citations on decks.** Every correct citation year on a slide would be reported
unless a claim heading happened to carry the year, which is a false alarm on correct decks.

**Read the deck's reference slides, alone or beside the ledger.** It needs a new APA-entry reader,
works only where `REFERENCE-SLIDES` is declared, and its one gain over the ledger is to silence a
cited source no claim record names.

**Move the reference gate into the shared stripping for all three graders.** The siblings are not
broken; each would then report `Opening (2027)` twice, as a number and as a citation.

## What none of this reaches

- **A coincident label.** A schedule label spelled like a cited author with the same year is still
  stripped; ruling 4's limit row names it.
- **Sibling coverage beyond the one control each.** Ruling 3 drives one shape per sibling.
- **Whether a stripped citation's source supports the slide.** That stays the adversarial reader's
  agreement job under ADR 0218 ruling 1.
