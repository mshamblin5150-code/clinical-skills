# A worksheet block heading is read in three forms by one grammar and a near miss is unread remainder

**Measured at:** 53c2514544ed554a5bee129c9676f39dbc546860

[#1357](https://github.com/mshamblin5150-code/clinical-skills/issues/1357) was filed from the
2026-09-17 grilling of [#1355](https://github.com/mshamblin5150-code/clinical-skills/issues/1355).
Grilled 2026-09-17; the clinician ruled every point below the same day. Freshness gate `FRESH` at
`53c25145`. Nothing is built here; this is the record the build reads.

## Measured before ruling

`icd10-cpt` step 4's template writes every block heading in one form, `--- PHRASE ---`. Two
committed run records diverge from it in two different directions, and both are real skill output:

- `fixtures/filled-anchor/run-2` cases 2, 4 and 8 prefix the delimited form with `###`.
- `fixtures/descriptor-agreement-note-path-control/worksheets` writes plain Markdown headings in
  sentence case, such as `## Not coded, nothing established it`.

The ticket named two graders. The same step-4 phrases are matched at five sites in four modules,
and no two of the grammars agree:

| module | object | forms read |
| --- | --- | --- |
| `anchor_scan` | `DIFFERENTIAL_HEADING`, `REFUSAL_HEADING` | bare delimited, plain Markdown |
| `anchor_scan` | `BLOCK_HEADING` (filled-anchor block) | bare delimited only |
| `anchor_scan`, `specificity_scan` | `STEP_FOUR_START`, two identical copies | bare delimited only |
| `refusal_scan` | `REFUSAL_HEADING` | bare delimited, `#`-prefixed delimited |
| `differential_scan` | `BLOCK_HEADING` | case-sensitive substring, used to scrub scaffolding |

So on `run-2` `refusal_scan` reads 52 refusal records and `anchor_scan` 41; on the note-path control
`refusal_scan` reads 0 and `anchor_scan` 3; and every one of these reports `unread remainder 0`.
`STEP_FOUR_START` is the quietest site: it bounds ADR 0230's relaxed-candidate window in two
graders, so on cases 4 and 8 the window runs to the end of the file and takes in the step-4
listings. The run-2 README currently praises the filled-anchor opener's refusal of the `###` form as
*the strict opener doing its job*.

## Ruling 1 — a block heading is recognized in three forms

The bare delimited form `--- PHRASE ---`, the Markdown-prefixed delimited form `### --- PHRASE ---`,
and a plain Markdown heading `## PHRASE` in any letter case are one heading. The phrase decides
which block it is and the prefix carries no meaning. The pre-#46 `NOT CODED, ANCHOR WAS FILLED`
trap is a property of the phrase and survives unchanged.

Rejected: reading only the template's form and counting the other two as unread. That would make
every grader refuse content it understands, and both divergent forms are recorded real output.
Also rejected: giving each grader the form the other reads, which leaves the next form to partition
them again in silence.

## Ruling 2 — `worksheet_grammar` owns every step-4 phrase at all five sites

The phrases and the three-form grammar move into `worksheet_grammar`, and `anchor_scan`,
`refusal_scan`, `specificity_scan` and `differential_scan` import them, including both
`STEP_FOUR_START` copies and the scrubber. `refusal_scan`'s comment calling its heading
*intentionally local* argued about entry lines rather than headings, and is retired. A test walks
`tools/` by AST and asserts no other module holds a literal copy of a step-4 phrase; like every such
walk in this repository it is a floor on the literal shapes it recognizes.

## Ruling 3 — a near-miss heading enters the shared unread remainder

In `anchor_scan`, `refusal_scan` and `specificity_scan`, a heading-shaped line (`--- ... ---` or
`#`-prefixed) carrying a step-4 keyword — `DIFFERENTIAL`, `NOT FOR ENTRY`, `NOT CODED`,
`ANCHOR WAS FILLED`, `UNDOCUMENTED`, case-insensitively — that matches no block phrase is counted
through `run_grader.format_unread_remainder`. That exits 2, and a finding on the same run still
exits 1. The candidate population is wider than the strict reader, grades nothing, is zero on every
committed worksheet once Ruling 1 lands, and is fired by a planted control, so ADR 0230 admits it
and a declared limit would not be enough.

## Ruling 4 — the off-template form is counted and never graded

The same three graders print, on every run, how many block headings were written in one of the two
non-template forms. The count never changes the exit status. Two independent runs drifting in two
directions is evidence the template's instruction is not holding, and a visible count is how the
next drift is seen; grading it would refuse a worksheet the graders read correctly.

## Ruling 5 — the run record is untouched and its tooling prose is corrected

The `run-2` worksheets stay byte-for-byte run evidence. The README's case-4 paragraph, which is prose
about the tooling rather than evidence, is rewritten: the prefix still diverges from the template, and
is now read and counted under Ruling 4. Every figure pinned to a grader's output on `run-2` is
re-derived by running the command, never edited by hand. A test asserts `anchor_scan` and
`refusal_scan` read the same refusal population on `run-2` and on the note-path control, because the
defect was two graders disagreeing and nothing checked that they agree.

## What none of this reaches

A heading-shaped line naming a block in words that carry none of the keywords is outside Ruling 3's
candidate population and stays unseen. Whether a block's contents are correct is unchanged by
recognizing its heading.
