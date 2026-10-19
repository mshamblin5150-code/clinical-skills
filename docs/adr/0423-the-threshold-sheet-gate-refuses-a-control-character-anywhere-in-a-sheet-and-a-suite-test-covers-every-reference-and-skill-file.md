# The threshold sheet gate refuses a control character anywhere in a sheet and a suite test covers every reference and skill file

**Measured at:** 514b9b1c63634b9a2b4d82e649425855c5439021

[#1861](https://github.com/mshamblin5150-code/clinical-skills/issues/1861) was filed from the
grilling of #1755 under
[ADR 0395](0395-a-hand-written-run-record-is-read-through-one-shared-reader-that-refuses-a-control-character-by-line-or-field.md)
ruling 6, which set committed reference sheets apart from run records. It found 474 bell
characters (U+0007) on 167 rows of `reference/thresholds/sepsis-and-septic-shock.md` and asked two
questions: whether the sheet gate refuses a control character, and how the sheet is repaired. Grilled
2026-10-19 against `main`, where the freshness gate read `FRESH`. The clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The gate already refuses two control characters, anywhere in the sheet.**
`threshold_grammar.FORBIDDEN_IN_RAW_TEXT` holds U+001E and U+001F, the two mis-encoded comparison
operator slots from #285, and `parse` checks them on the raw text before any line is split. The
ticket's body said the gate refused none; two sweep comments on the ticket corrected that. Driven
here on a copy of the sepsis sheet with every bell replaced by U+001F, the command printed
`NOT GRADED`, named only the first damaged line, and exited 2.

**The bells sit in two columns and always after a space.** 152 value cells and all 167 snippet
cells carry one. Every one of the 474 has a space before it and a non-space character after it: 430
come before a letter, and 44 come before a recommendation number, as in ` ␇54. ␇We suggest`. None is
next to a threshold value. Every one of the 167 snippets carries the `RENDERED:` marker, so the
cited-page check never compared them with the PDF text.

**The recommendation reader kept the bell, and the corpus extraction did not.**
`guidelines_recs.rebuilt_page_text` calls `guidelines_extract.repaired_text`, which rebuilds a page
without `normalize`. `normalize` is the step that deletes the C0 and C1 ranges from the extracted
corpus. So the published recommendation records for the two Surviving Sepsis Campaign documents
still carry the bell, escaped in their JSON (159 and 95 occurrences). `threshold_draft.py` prints
from those records, which is how the bells reached the sheet. The sweep closing this grilling
widened the count. Every published record was decoded and its strings walked: 22 of 180 carry a
control character, 8 AHA/ACC, 5 IDSA and 9 KDIGO, as U+0007 (1,196), U+0003 (100) and U+0004 (2).
So a sheet drafted from any of those sources would arrive carrying them, and U+0003 sits outside
the USPSTF documents where `MathematicalPi-One` was measured. Whether those U+0003 and U+0004
characters are separators or operators was not rendered.

**Deleting control characters in this corpus can delete an operator.** `MathematicalPi-One` sets
comparison operators in U+0002 and U+0003, and the mapping is inverted between two USPSTF documents.
That is why `guidelines_extract` keeps it out of `SYMBOL_FONT_OPERATORS`. `normalize` deletes both
slots in the corpus text.

**Nothing else committed carries the damage.** A count of every tracked file found C0 characters
other than a line ending only in the sepsis sheet and in deliberate test data under `tools/`. The
one legitimate tab is the column separator in `reference/completion-check-starts.tsv`. Every
committed JSON file under `reference/` and `skills/` was also decoded and walked, and none holds a
control character in a key or string.

## Ruling 1 — the sheet gate refuses, and the recommendation reader is left alone

The threshold sheet gate refuses a control character. The recommendation reader keeps passing
control characters through to its records.

Deleting them in the reader as well was declined. It would silently delete the inverted operator
slots of `MathematicalPi-One`, where a gate refusal forces someone to look at the rendered page.
It would also move the recommendation build's identity and rerun its pass over every PDF. Deleting
them in the reader instead of refusing at the gate was declined because a character reaching a
sheet by another route, such as a script that turns `\t` into a tab, would still pass. This is ADR
0421 ruling 1's reason applied to a sheet: a refusal makes a person look, and a deletion is a guess.

## Ruling 2 — damage is ADR 0421's set

Damage is every C0 character except a line feed or a carriage return directly before a line feed,
plus DEL (U+007F) and the C1 range (U+0080 to U+009F). Tab is damage.

A threshold sheet's values flow into clinical notes and code selection, so its exposure is closer to
an **Outbound artifact** than to a **Hand-written run record**. ADR 0395's narrower C0-only set was
declined because a DEL or C1 character from a PDF text layer would pass, and the corpus extraction
already treats that whole range as junk. Adding only the bell was declined because the next
invisible separator in another font is likely a different code. The wider set costs nothing today:
no committed sheet holds a tab, DEL or C1 character.

## Ruling 3 — the check reads the whole sheet's raw text

The set is refused anywhere in the file, on the raw text before line splitting, as
`FORBIDDEN_IN_RAW_TEXT` already is. Refusing only in value and snippet cells was declined because it
is narrower than the existing rule, and the source, population and quantity cells feed lookups and
conflict checks. A carriage return or form feed can also split a row before any cell exists to
inspect.

## Ruling 4 — damage exits 1 and names every damaged line

A damaged sheet is a finding. The command exits 1 and names every damaged line with its character,
for example `line 326: U+0007`. That sheet's other checks print `not graded — damaged text`. Other
sheets in an `--all` run are graded normally. U+001E and U+001F move to this behavior from their
current exit 2 and first-line-only report.

Keeping exit 2 and the first line was declined because the command read the whole file, and because
the sepsis sheet would take one fix-and-rerun round per damaged line. ADR 0395 ruling 5 and ADR 0421
both rule damage a finding. Grading the rest of a damaged sheet was declined because U+001E and
U+001F break rows apart, so the other checks would run on a wrong reading. This follows ADR 0395
ruling 5's reason: a damaged reading cannot be trusted for its own file and says nothing about its
neighbors. The pre-commit hook and CI refuse on either status, so the change is in what the report
claims, not in whether a commit is blocked.

## Ruling 5 — one suite test covers every reference and skill file

One suite test checks every tracked text file under `reference/` and `skills/`, and `AGENTS.md`,
for ruling 2's set. Tab is allowed only in a `.tsv` file.

Covering threshold sheets only was declined because a bell pasted into a **Topic sheet** or a skill
file would pass every check, and agents writing notes read those files. Adding the check to each
other reference gate was declined: five or more gates would change, and a file with no gate, such as
a skill file or `reference/medatrax-fields.md`, would stay uncovered. The test runs in the suite and
in CI rather than the pre-commit hook, so damage in a file other than a threshold sheet is caught at
the merge (ADR 0002), not at the commit.

## Ruling 6 — the sepsis sheet is repaired by a guarded deletion

The 474 bells are deleted by a script that deletes a bell only when a space precedes it and a
non-space character follows it, and refuses any other. One cited page from each of the two sources
is then rendered and checked by eye against the cleaned rows.

The clinician first ruled the guard as "a space before and a letter after". The 44 bells before a
recommendation number were then measured, and the guard was re-ruled to a non-space after, because
the space before is what keeps a deletion from joining two words. Re-deriving the 167 rows from the
rendered pages was declined: the `RENDERED:` marker already records that reading, the defect is an
invisible byte, and re-drafting from the recommendation records would bring the bells back.
Replacing each bell with a space was declined because it leaves a double space and the cells would
no longer match the rendered text.

## Ruling 7 — two refusal wordings, both sending the writer to the rendered page

U+001E and U+001F keep their current operator remedy. Every other character gets a general remedy,
in substance: the character is a control character, either an invisible byte from the PDF's text
layer or a typing mistake; render the cited page and write what it shows there, which is usually
nothing, so delete it; if a comparison operator belongs there, write `<=` or `>=`.

The existing operator text would plant a false threshold where a bell stood. A plain "delete it"
would erase the inverted `MathematicalPi-One` operators. One wording for all characters was declined
because it drops the measured fact that U+001E and U+001F are always operators. A message per
character was declined because it grows with every font finding for little gain over the page.

## What this record does not reach

- **Damage that produces printable characters**, such as a lost backslash. ADRs 0351, 0395 and
  0421 name the same limit.
- **The recommendation records.** Ruling 1 leaves them carrying control characters; the gate
  refuses them when they reach a sheet.
- **Tracked files outside `reference/`, `skills/` and `AGENTS.md`**, such as `docs/`, `CLAUDE.md`
  and `tools/`, where test data carries control characters on purpose.
- **Damage in a reference file other than a threshold sheet before the merge.** Ruling 5's test
  runs in the suite, not at commit.
- **The adult source's rows beyond the one rendered page.** Ruling 6's guard carries the rest.

## Build checklist

- `threshold_grammar`: widen the raw-text refusal to ruling 2's set, which is ADR 0421's outbound
  set and never ADR 0395's narrower run-record set (C0 only, tab allowed in copied posts). The
  shared module that ADR 0395, ADR 0421 and ADR 0422 ruling 6 each defer to whichever build lands
  first is not built yet. If it has landed and carries ADR 0421's set under its own name, import
  that set. Otherwise keep the set named in `threshold_grammar` with the reason it matches ADR
  0421's, and whichever of the #1859 and #1861 builds lands second points `threshold_grammar` at the
  shared set so the two copies cannot drift. Keep U+001E and U+001F in `threshold_grammar` as a
  named subset carrying the operator remedy.
- `parse` collects every damaged line instead of the first, reading with `newline=""` so a bare
  carriage return stays visible, and reports `line N: U+XXXX` per damage.
- `threshold_sheet`: a damaged sheet exits 1, names every line, and prints
  `not graded — damaged text` for its other checks; other sheets in an `--all` run are graded.
  The existing exit-2 expectation for U+001E and U+001F in `tools/test_threshold_sheet.py` moves to
  exit 1.
- Ruling 7's two wordings, each pinned by a test.
- The prose that describes today's two-character refusal moves with it:
  `reference/thresholds/README.md`'s paragraph on destructive control slots, and the matching
  sentence in `CLAUDE.md`'s **Guideline text extraction** section. The README is inside
  `tools/test_blind_fixture_instructions.py`'s guarded population, which reads a bare "C1" token as
  an assertion identifier, so the README names that range by its code points (U+0080 to U+009F).
- The repair script for ruling 6 runs once, refuses any bell without a space before and a non-space
  after, and leaves the sheet's `RENDERED:` markers untouched. Render one cited page per source
  before committing the repair, and land the repair before or with the widened refusal so `main`
  stays green.
- The suite test from ruling 5, reading each file's raw bytes, with the `.tsv` tab exception named
  beside its reason. A JSON file is also decoded and its keys and strings walked, on ADR 0395 ruling
  4's reason; every committed JSON file under `reference/` and `skills/` decodes clean today. The
  test walks the index, so its function states the tracked-only boundary that
  `tools/test_ls_files_coverage.py` requires: a clean result means no tracked file fails, and an
  untracked file is not read.
- Tests drive `threshold_sheet.py` on a synthetic sheet with a planted tab, bell, NUL, form feed,
  vertical tab, bare carriage return, DEL and U+0085, and expect exit 1 naming each line. A
  Windows-line-ending sheet grades clean. A second clean sheet in the same `--all` run is still
  graded. Name as a control the sepsis sheet as committed before the repair, which today grades
  `ok` with 474 bells.
