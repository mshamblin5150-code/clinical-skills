# The threshold tail class is the sheet cell and the sheet decides where it ends

**Measured at:** 75e50da8866a025298cd2752ab7a2c4e1510c220

Ticket [#1334](https://github.com/mshamblin5150-code/clinical-skills/issues/1334) was filed when
an independent `differential_scan` pass over a `batch-shift` run reported drift row 24 findings on
threshold citations written exactly as the cited sheet writes them. `THRESHOLD_CITATION` accepts a
tail's class only as one run of letters and digits, while the sheets' `class` cells carry the
source's own wording: `practice-point`, `B/C`, `strong recommendation, moderate-quality evidence`.
The clinician ruled the grammar in a grilling on 2026-09-16.

The measurement behind the rulings parsed every file under `reference/thresholds/` except
`README.md`, `coverage.md`, and `subjects.md` with `threshold_grammar.parse` and tested each row's
`klass` against `^[A-Za-z0-9]+$`, the class token the tail pattern requires. It read 169 sheets,
refused none, and returned 11,097 rows. Of those, 190 rows in 8 sheets carry an empty class cell,
and 1,214 rows in 33 sheets carry a non-empty class the pattern cannot accept; 477 of the 1,214
contain a comma. Within any one source of any one sheet, no class is followed by a comma at the
start of another class of that source: 0 such pairs. The matcher is a floor, because a row the
parser does not return is outside every one of these counts.

## Ruling 1 — the tail keeps its shape and the sheet decides where the class ends

A threshold tail stays `<source> Class <class>, <population>, <value>`. The class is the cited
row's `class` cell verbatim, commas included. The scanner does not find the end of the class by
punctuation. It reads the classes the cited sheet holds for the named source and takes a class as
written when the tail continues with that class followed by a comma. A tail citing
`reference/thresholds/babesiosis.md` therefore reads
`idsa-2020 Class strong recommendation, moderate-quality evidence, suspected-acute-babesiosis, ...`
and passes.

The alternatives were a separator other than the comma, which rewrites every existing tail and
collides with the three class cells that already contain a semicolon; a normalized class key added
as a column to every sheet, which is a second copy of the class to keep equal; and dropping the
class from the tail, which cannot tell apart rows that differ only by class. Resolving the grammar
against the sheet's own cells changes no tail that passes today and keeps a class the sheet does not
hold failing.

## Ruling 2 — an empty class cell writes no class

A row whose `class` cell is empty is cited without the `Class` word and without a class:
`<source>, <population>, <value>`. That form passes only against a matching row whose class cell is
empty. The same tail against rows that all carry a class still fails, as a tail missing its class
fails today. This widens #1334 beyond its filed count to the 190 empty-class rows, because its
completion condition names any shipped row.

## Ruling 3 — every reading is tried

Where more than one class the source holds could end at a comma in the tail, the scanner tries every
reading. The tail passes when any reading names a shipped row and fails only when none does. No
longest-match order is imposed, because an order can only turn a correct tail into a failure, and
no rule is placed on sheet authors against a collision that no shipped sheet contains.

## Ruling 4 — the two findings keep their meanings

A tail that splits into source, class, population, and value but names a class the source does not
hold, or otherwise names no shipped row, is reported as `threshold source, strength, population, and
value do not match a shipped row`. `malformed threshold verdict` is reserved for a tail that cannot
be split into those fields under any reading. The first finding tells the note's author to check the
sheet; the second tells the author to fix the tail's shape. #1334 was a correct tail reported under
the second.

## Ruling 5 — preserved records are not re-graded

Every threshold tail in a committed record cites a one-token class, so no committed row 24 result
moves under rulings 1 through 3. Committed records and any count recorded beside them stay as they
are. The scanner applies the grammar when it runs, so an in-flight run is graded under this record
by rerunning `differential_scan`.

## Ruling 6 — the skill shows both new forms with real rows

`skills/clinical-note/SKILL.md` gains one worked tail citing a class that contains a comma and one
citing a row with an empty class, both copied from shipped sheet rows, and a sentence stating that
the class is the sheet's cell verbatim and that an empty cell writes no class. The existing test
that runs the scanner over the skill's worked examples grades the new lines against the sheets.

## Ruling 7 — a committed test re-derives the population

A test builds a tail from every row `threshold_grammar.parse` returns and asserts each passes row 24
through the scanner's public entry point. For each source it also plants a tail naming a class that
source does not hold and asserts the does-not-match finding. The test asserts no row count, and a
sheet the parser refuses fails it rather than shrinking the population. Its runtime is measured
before the whole population is committed as the per-run shape.

## Consequences

- `tools/differential_scan.py`, its tests, and `skills/clinical-note/SKILL.md` change together.
- One committed fixture, `fixtures/descriptor-agreement-note-path-control/notes/case-01.md`, carries
  8 row 24 `malformed threshold verdict` findings that are not this record's defect: source-keyed
  `sheet does not settle` verdicts and a narrative row cited without `Class` and with a page. Their
  result is unchanged here, and whether those shapes are valid is a separate ticket.
