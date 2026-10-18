# A matcher a note pass satisfies by rewording is retired and a uspstf citation names its topic by copying the sheet title

**Measured at:** aed463c377aa10dcb05a5ffe9932a279eef59372

[#1812](https://github.com/mshamblin5150-code/clinical-skills/issues/1812) was filed from the
after-action review of a `batch-shift` run (NUR5144 ED shift) on 2026-10-14. Two note passes
reworded correct clinical prose to get past a matcher. One replaced a vitamin name after a
`tools/anchor_scan.py` self-grade. The other renamed a proposed item until the row 24 USPSTF join in
`tools/differential_scan.py` stopped matching. Grilled 2026-10-18 against `main` at `04afe518`,
where the freshness gate read `FRESH`. The commit above adds only drafts of this record and its
glossary entries to that base. The clinician ruled every point below in that session, one question
at a time. **Nothing is built here; this is the record the build reads.**

A matcher that a pass can satisfy by rewording teaches the next pass to write for the tool rather
than the reader. Every ruling below either removes such a matcher, makes it report instead of fail,
or replaces it with something a pass copies rather than composes.

## Measured before ruling

**Case 1: the pass misread a line that already said "not a finding".** The pass's
`--agreement-read ... --stem` self-grade exited 0 with zero agreement, author code-label and bind
findings and an unread remainder of 0. The only nonzero lines were informational:
`code-shaped tokens excluded from the bind  1` and `excluded from bind, not a finding: ...: B12`.
Those are the lines [#1419](https://github.com/mshamblin5150-code/clinical-skills/issues/1419)
added so a mistyped real code stays visible. The pass then replaced "Vitamin B12" with "cobalamin"
and reported that B12 "was being caught". #1419's fix reached this path with and without `--stem`.

**Case 1 also exposed a defect this run did not trigger.** `ICD_TOKEN` has a second consumer,
`anchor_scan._code_labels`, which builds the whole **Code label** for the author code-label
finding in both `--agreement-brief` and `--agreement-read`. It treats every `ICD_TOKEN` match as the
code before the label, including tokens the code set does not hold. Driven on synthetic notes,
`Vitamin B12 deficiency - E53.8` and `Elevated A1C - R73.09` cut the label short and both modes
exit 1 with `author anchor differs from whole code label`. B6, D3, K2 and B1 are too short for the
pattern, and the A1C inside HbA1c is welded to the preceding letters, so neither reaches it.
Category headings such as D51 resolve in the code set and still behave as codes.
`AGREEMENT_READER_INSTRUCTIONS` states the same rule as "after the preceding code token".

**Case 2: the row 24 join reads the label and nothing else.**
- `_lexical_subject_topic_names` matches the item's words against USPSTF topic titles.
- `_uspstf_citation_matches` passes when any joined topic carries the cited grade and year.
- The cited population is checked only for being present, although the finding text names it.

On the shift, "Healthy diet counseling", citing grade B, adults with a body mass index of 30 or
higher, 2018, joined only the two diet-and-physical-activity topics, neither of which carries B
2018. So it was a finding. The intended topic, behavioral weight-loss interventions, carries exactly
that citation. Renamed "Nutrition counseling for weight loss", the item joined nothing and became an
unchecked candidate. The rename evaded the check rather than satisfying it.

Over the 74 well-formed USPSTF citations in `fixtures/slot-form-run` and the `clinical-note` skill
files, 27 join cleanly, none is a finding, and 47 join nothing and go unchecked. Of the 27, 14 join
several topics and pass because any one of them fits. Synthetic labels produced false findings,
such as "Weight counseling" joining only the pregnancy weight-gain topic. They also produced false
passes, such as an HIV screening item citing the PrEP grade and year. The two Rh(D) rows carry year
`not stated` and are dropped from the index, so 141 of the 143 sheet rows are indexed.

**Population cannot be compared without becoming the next rewording target.** Identifying the row
from grade, year and population word overlap instead of the label failed one committed citation that
is correct. Its dental caries population is written as "all infants and children from primary tooth
eruption", while the sheet reads "children younger than 5 years".

**Topic plus grade plus year needs no population.** The sheet holds 141 rows under 89 distinct topic
titles. Within one topic, grade and year identify one row except in 16 groups, and every row of each
of those groups shares that grade and year. Population separates them only by whom the
recommendation covers, which is a clinical judgment. None of the 89 titles contains a semicolon,
colon, bracket or pipe. Five contain a comma. Titles run 25 to 175 characters, median 53.

**The two other label matchers fire on nothing committed.**
- The `uspstf: no row` verdict is a finding when its label joins a USPSTF topic.
- The `recalled, no shipped sheet` verdict is a finding when its label joins a topic with a shipped
  threshold sheet.

Across committed fixtures and the `clinical-note` and `batch-shift` skill files, none of the 5 `no
row` tails or 37 `recalled, no shipped sheet` tails fires. Synthetic labels fired falsely: an adult
"Lipid screening" joined the children's lipid topic.

## Ruling 1 — an informational line is never a reason to change note text

The writer self-grade steps in `skills/batch-shift/SKILL.md`, `skills/clinical-note/SKILL.md` and
`skills/icd10-cpt/SKILL.md` say so. When an informational line names a token, the pass leaves
ordinary clinical prose as written. When the token is a mistyped code, the pass corrects the code.
The grader does not change.

Removing the informational line, which reverses #1419, and hiding the named token behind `--show`
were both declined. This pass ran `--show`, and the line already said "not a finding", so neither
would have prevented the rewording.

## Ruling 2 — a code-shaped token outside the code set is label text

`anchor_scan._code_labels` applies #1419's rule. A code-shaped token the code set does not resolve
neither ends the preceding label nor counts as the code before a label.
`AGREEMENT_READER_INSTRUCTIONS` says the same, so the blind reader and the check agree on one label.
A token the code set resolves, including a category heading, still behaves as a code.

This sharpens what [ADR 0301](0301-the-agreement-read-quotes-a-code-label-by-one-convention-stated-in-the-first-brief.md)
ruling 4 calls "the preceding code" rather than overturning it. B12 was never a code, and the
implementation read it as one. Recording it as a known limit was declined because a correct
diagnosis line would keep failing a gate that only rewording could clear.

## Ruling 3 — a USPSTF citation names its topic by copying the sheet title

The citation form becomes `[uspstf: <topic title>; grade <X>, <population>, <year>]`, and the `I
statement` form takes the same title-and-semicolon prefix. The title is copied from
`reference/guidelines-uspstf.md` and compared with the sheet's titles as an exact whole after case
and whitespace are folded. A title the sheet does not carry is a finding, `names no shipped topic`.
The semicolon is the separator because no title contains one. `[uspstf: no row]` keeps its shape.

The label-to-topic word match is deleted. The item's own words no longer decide which
recommendation a citation is checked against, so no rewording of the item changes the result. A
wrong choice of topic still surfaces when its grade or year disagrees with the topic named.

Three options were declined:
- **Keeping the label match with a written rule.** It leaves the shift's correct note failing and
  47 of 74 committed citations unchecked.
- **Identifying the row from grade, year and population word overlap.** It fails the committed
  dental caries citation and makes population wording the new rewording target.
- **Accepting a near-miss title above a similarity cutoff.** It restores a wording-sensitive matcher
  with an unmeasured cut point.

## Ruling 4 — grade and year are compared and population is not

The cited grade and year must match a row under the named topic. The population must be present and
stays in the writer's own words. The finding text stops claiming that population was compared.
Whether the recommendation's population fits the patient stays the second reader's reading.

A word-for-word copy of the sheet's population cell was declined. It lengthens every citation and
compares nothing the grade and year do not already settle.

## Ruling 5 — an old-form citation is graded by approval date

A USPSTF citation with no title is a finding when its note was approved after the new check's start
in `reference/completion-check-starts.tsv`. Before that start it is not graded. The worked examples
in the skill files move to the new form. Committed run records stay as written, and their pinned
row 24 figures in the tests move deliberately.

Two options were declined. Treating the old form as a reader candidate forever would make dropping
the title the next way around the check. Failing the old form everywhere would leave
preserved records with no repair but falsification.

## Ruling 6 — a topic whose sheet year is not stated is graded on grade alone

The two Rh(D) incompatibility rows are indexed. A citation naming their topic is compared on grade,
and the report prints on its own line that the year was not compared because the sheet states none.
Correcting the sheet's year is a question for `tools/uspstf_table.py`'s derivation rule and is filed
separately.

## Ruling 7 — "checked" counts only citations that were compared

The report's count of guideline tails checked against source evidence includes only tails actually
compared. Grade-only citations, citations not graded under ruling 5, and `no row` tails each print
on their own labeled line, and the lines sum to the tails read.

## Ruling 8 — the no-row and no-shipped-sheet contradictions are reported, never graded

A `uspstf: no row` or `recalled, no shipped sheet` tail whose label joins a topic is counted and,
under `--show`, listed as a label-and-topic pair for the second reader. The count never changes the
exit status. This is [ADR 0380](0380-a-pass-may-grammar-check-its-own-note-and-a-prior-run-is-a-record-not-a-template.md)
ruling 5's arrangement for the same risk. The label match survives only to choose which pairs a
reader is pointed at.

Keeping them as findings was declined, because a correct verdict would keep failing a gate that only
a rename could clear. Deleting them outright was declined because it would drop the pointer to the
items that deserve a reader's look.

## Coordination

[ADR 0409](0409-the-uptodate-pull-checks-the-query-it-sent-files-drug-pages-by-version-and-proves-a-failed-pull-opened-the-page.md)
rulings 4 and 7 add an `uptodate drug:` tail to the same row. Its branch is selected by the
`uptodate` prefix, and this record changes the grammar of only the `uspstf` and `recalled`
branches. One piece is shared: the `uptodate`, `recalled`, `uspstf` and threshold branches all add
to the single checked count in `differential_scan._guideline_floor` that ruling 7 splits. So the
drug tail lands on one of ruling 7's labeled lines, and whichever build lands second keeps the
other's branch and its line.

## Build checklist

- `tools/anchor_scan.py`: in `_code_labels`, skip a code-shaped token the code set does not resolve,
  through the same `_database_descriptor` helper the bind uses. Update
  `AGREEMENT_READER_INSTRUCTIONS` to match.
- `tools/test_anchor_scan.py`: add brief and read cases for `Vitamin B12 deficiency - E53.8` and
  `Elevated A1C - R73.09` grading clean. Add a control proving that a real code earlier on the line
  still ends the label. If the change makes the module a new reader of the code-set database, keep
  `python tools/code_set_database_reader_check.py` clean.
- `tools/differential_scan.py`:
  - Parse the titled USPSTF form and join the cited title exactly to the sheet.
  - Compare grade and year, and grade alone for a topic whose sheet year is not stated.
  - Add the `names no shipped topic` finding.
  - Correct the mismatch finding's text so it no longer names population.
  - Delete the label join from the citation path.
  - Turn the `no row` and `recalled, no shipped sheet` contradictions into a reported, never-graded
    count with `--show` pairs.
  - Split the checked count into its labeled lines.
  - Register each new check kind in `reference/completion-check-starts.tsv`.
  - Update `NOT_VALIDATED_AGAINST` to the new boundary.
- `tools/test_differential_scan.py`:
  - Cover the shift's case in the new form, a title not on the sheet, a wrong grade under a correct
    title, the Rh(D) grade-only line, and an old-form citation before and after the start.
  - Cover the reported contradiction count.
  - Re-pin the committed run's row 24 figures.
- `skills/clinical-note/SKILL.md` and `skills/batch-shift/SKILL.md`: document the titled citation
  form, rewrite the worked examples, and say the population is the writer's description and not a
  comparison.
- `skills/batch-shift/SKILL.md`, `skills/clinical-note/SKILL.md` and `skills/icd10-cpt/SKILL.md`:
  add ruling 1's sentence to the self-grade step.
- `CLAUDE.md` *Differential scan* section: replace the row 24 description of the USPSTF join.

## What this record does not reach

- **Whether the copied topic is the right recommendation for the item.** A topic whose grade and
  year match the citation passes, whether or not the item is about that topic. That stays a reading.
- **Whether the population fits the patient.** Ruling 4.
- **Whether a reader rules correctly on a reported contradiction pair.** Ruling 8 points the reader
  at the pair and grades nothing.
- **A pass rewording around a line no ruling here names.** Ruling 1 is a written rule, and a
  written instruction cannot fail; the after-action review is what sees a breach.


## The earlier ruling this overturns

Ruling 8 overturns the paragraph of
[ADR 0017](0017-a-run-joins-a-threshold-sheet-on-the-artifact-column-and-the-state-describes-the-read-behind-it.md)
that reads "`recalled, no shipped sheet` becomes a graded finding". That record's join on the
artifact column and its matching on registry topic names survive.

ADR 0017 states its rulings as unnumbered paragraphs. [ADR 0390](0390-an-overturned-passage-with-no-ruling-number-is-located-by-its-exact-quote-and-a-repair-s-mislabeled-opening-is-restored.md)
ruling 1 already rules this case: the exact quote is the coordinate, and the quoted words occur once
in ADR 0017. `tools/test_adr_supersession.py` does not read that quote form yet; building it is
[#1706](https://github.com/mshamblin5150-code/clinical-skills/issues/1706). Until then the
overturning is stated in this record alone. Whichever lands second, #1706's build or this record's
build, adds the marker beneath that ADR 0017 paragraph and the quote-form `## Supersedes` declaration
here.
