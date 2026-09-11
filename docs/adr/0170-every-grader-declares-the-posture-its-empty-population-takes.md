# Every grader declares the posture its empty population takes

[#922](https://github.com/mshamblin5150-code/clinical-skills/issues/922) was filed 2026-09-06 out of
[#790](https://github.com/mshamblin5150-code/clinical-skills/issues/790)'s grilling, whose record,
[ADR 0138](0138-an-absent-committing-scratch-root-is-nothing-to-grade-and-the-empty-population-rule-is-not-generalized.md),
stated the discriminator this record builds on in its ruling 9 and deliberately refused to rule it
repo-wide, because live modules broke it. `deck_scan` and `specificity_scan` graded populations only
a matcher could see and exited 0 when the matcher saw nothing. The ticket was open on whether every
`run_grader` member must declare how it handles that, or whether each module is decided on a
measurement.

Grilled 2026-09-10. The session began at `origin/main` `6222111`, was brought forward by merge to
`c90f5c7` (containing `9117908`) before this record was written, and no graded module changed in
that merge, so every line anchor below holds at both. **Twenty questions were ruled by the clinician
one at a time on that date.** Nothing is built here; this is the record the build reads.

Every exit status below was driven through the real command, or `main(argv)` in-process where the
member needs the test module's fake PDF engine, over synthetic inputs built from each member's own
test helpers. The drivers were written in parallel by four read-only agents and **re-run by the parent
at `c90f5c7`**, where every figure matched. They are not committed; the kit ruled in ruling 7 is what
makes them re-derivable.

## Measured before ruling

### The ticket's prohibition contradicted its own models and ADR 0138

The body's *What must not come out of this* refused `coverage_failed = not scan.bullets` as gating on
the thing under test. The members it cited as obeying do exactly that: `anchor_scan.py:382` gates
`not scan.subjects`, where `subjects` (`:195-197`) is three matcher counts; `refusal_scan.py:269`
gates `subjects == 0` over `refusals`; `block_scan.py:431` gates `not scan.notes_with_block`. ADR
0138 ruling 9 prescribes that shape: where the matcher is the only evidence, empty is *did not scan*.
[ADR 0151](0151-the-citation-author-date-split-is-evidenced-by-the-reference-list.md) ruling 1
refused a different object, a coverage *report* that printed the same figure under the claim's
negation.

### Both named defects hold, and each is narrower or wider than written

- **`deck_scan`**: a deck of picture-only slides reads zero text and exits 0. That zero is true. The
  strong case is a SmartArt slide: its text lives in a diagram part the parser never opens
  (`_read_slide`, `:239-270`, reads slide XML only), so an untraced `$99,000` and an overlong line
  exit 0 where the same line on an ordinary slide exits 1. Beside one ordinary slide it still exits 0
  with `costed figures 0`.
- **`specificity_scan`**: its `SPECIFICITY` pattern (`:98`) opens on whitespace only, so a bare
  `complete` flag written behind a list marker or in bold goes unread and exits 0 where the plain
  spelling exits 1. Worksheets whose codes carry no flag at all exit 0. Beside one recognized flag, a
  missed failing flag still exits 0. A separate `ENTRY` matcher (`read_entries`, `:233-258`) already
  finds every code with or without a flag, and `survey` (`:545-563`) never uses it.

### A third member breaks the rule, three refuse in `load`, and the rest comply

- **`discussion_post_scan`** exits 0 on an empty or headings-only draft under a bar signing
  `WORD-FLOOR: 0` and `REFERENCE-MINIMUM: 0`, which `skills/discussion-post/SKILL.md:98,100`
  documents as the legal value when none is stated. `_integer` (`:379-383`) accepts `0`, and the floor
  fires only when `words < floor` (`:1100`).
- **`discussion_reply_scan`** (`:473-474`), **`reference_scan`** (`:1991-1994`) and
  **`research_ledger`** (`:1575-1576`) refuse their empty population inside `load`, so no report
  prints. In `research_ledger`, a ledger with no claim records beside a draft whose prescription table
  is uncited exits 2, where one unrelated record makes it exit 1: the refusal swallows a real finding.
- **`refusal_scan`** exits 2 on an empty block with nothing on stderr (`_grade`, `:263-270`), so its
  report reads exactly like a clean one. **`case_study_scan`** states the condition in its report only
  (`:862-867`).
- The other ten members already never exit 0 on an empty population.

### Three members already gate other populations under earlier rulings

`differential_scan` gates having no numbered item (`:1490-1497`) and threshold-sheet failures;
`research_ledger` gates a draft with no prescription table (`:1722-1727`); `case_study_scan` gates a
skeleton disagreement (`:913`).

### The strict definition fails in two shapes

No single `differential_scan` count leaves every content row empty: a conclusion-only note still
grades row 22 and a note with only a FILLED-proposed item still reads row 24. And
`case_study_scan`'s whole-document rows (`:535`, `:590`, `:628`, `:714`, `:724`) read every block
`docx_write.blocks` yields, and it yields one for every line bar own-line comments (`:972-1062`), so
a strict reading would pick a population empty only in a blank file.

### A one-member twin cannot discriminate a floor

`discussion_reply_scan`'s empty reply exits 1 through `word-floor` against the fixed
`WORD_FLOOR_COUNT = 150` (`:60`); a reply of one word still exits 1. `peer_critique_scan` has a fixed
floor and eight required headings.

### `checks_ledger` zeroes its registry on an empty read, deliberately

Its `CHECK` pattern (`:238`) reads 0 of 13 correctly filled records written under `## Check -`
headings. On an empty read `_grade` zeroes the registry's missing-check findings (`:759-768`) and
names the condition (`:814-815`).

## Ruled 2026-09-10

### 1. A matcher zero gating to exit 2 is the rule applied, and the ticket's prohibition is corrected

What is forbidden is using a matcher's zero to *establish* an empty population and pass it clean. The
body of #922 is corrected accordingly.

### 2. The rule is ruled for `run_grader.MEMBERS`, with a posture declared per member

A population only the matcher says is empty never exits 0, for every name in `run_grader.MEMBERS`
(`run_grader.py:40-57`). Each member's **empty-population posture** is declared with a reason in one
mapping in `run_grader`, and a test fails unless every member appears exactly once. The arrangement is
`run_grader.UNDECODABLE_BYTE_POSTURES` and its family test
(`test_run_grader.TheUndecodableBytePostureIsDeclaredForTheFamily`). The mapping's name must not
match [ADR 0167](0167-the-limits-walk-reads-a-declared-name-list-and-a-module-without-limits-is-declared.md)
ruling 8's limits-looking pattern: it is a behavior declaration, not a limits object.

**It is a declaration the kit reads, not structure in the runner.**
[ADR 0112](0112-the-grader-membership-ratchet-grades-adoption-rather-than-source-shape-and-not-members-distinguishes-refused-from-deferred.md)
ruling 4 forecloses a gate inside `run_grader.run`, because the runner does not speak for its
members. `run` gains no branch here: each member's own `load` and `grade` produce the status, and
ruling 7's kit checks that status against the entry, the way `UNDECODABLE_BYTE_POSTURES` has sat
beside `MEMBERS` since `0636c26`.

### 3. A member names one load-bearing population, possibly a named union

The **load-bearing population** is the one population whose emptiness leaves every row grading the
artifact's matcher-read content with nothing to grade. Three kinds of row do not count toward "every
row": a row over which files or parts exist, a row over every line of the artifact, and a completion
row over a separate record such as the render record or the after-action review. Where no single
count qualifies, the population is the named union of the matcher-read populations the rows read,
and it is still one declared population.

### 4. Other populations may carry their own gates, and this rule requires none

The posture governs the load-bearing population only. The gates in *Three members already gate other
populations* stand, and a count nobody gates still prints on every run.

### 5. Three postures, and `finding` needs two conditions

- `not-scanned`: only the matcher saw the emptiness; exit 2.
- `finding`: the absence is settled without relying on the matcher **and** is the run's own unmet
  obligation; exit 1. An obligation alone does not qualify: `checks_ledger` stays `not-scanned`.
- `established`: the emptiness is settled independently, per **Established empty**; exit 0. No member
  takes it today.

### 6. A refusal in `load` stays there only when it reads a listing of names

A refusal over which files or parts exist (a zip's slide parts, a run directory's `response-*.md`
files) is the load-settled row ruling 3 excludes and stays in `load`. A refusal over what a matcher
reads inside a file moves from `load` into `grade` behind `coverage_failed`, so the report prints and
a finding outranks it in the runner's order. `reference_scan` and `research_ledger` move;
`discussion_reply_scan` does not.

### 7. The shared conformance kit drives every declaration

Each member's test module supplies an input whose primary source passes `load` and whose load-bearing
population is empty, and the kit drives it through the member's real `load` and `grade`:

- `not-scanned`: exit 2, a non-empty stderr diagnostic, the report printed (so a `SourceError` cannot
  pass for the wrong reason), and a twin identical except for one member of the population, chosen so
  no other gate fires, that does not exit 2.
- `finding`: exit 1, and the declared finding row's kind fires on the empty input, read from `grade`'s
  findings. No twin is needed: the row's identity discriminates. If a later ruling lowers a floor so
  the row stops firing, this test fails, which is the prompt to add an empty-body row then.
- `established`: exit 0.

Where a posture depends on a value the run signs, the empty input uses the most permissive legal
value; under `discussion_post_scan`'s helper bar (floor 100) the empty draft exits 1 whether or not
the fix exists.

### 8. The seventeen declarations

| member | load-bearing population | posture (row) | today | build |
| --- | --- | --- | --- | --- |
| `aar_scan` | the submission's review record (`is_file`, `:699`) | finding (`missing-review`) | exit 1 | none |
| `anchor_scan` | marked, listed and pediatric bands (`:195-197`) | not-scanned | exit 2, diagnostic | none |
| `block_scan` | notes carrying a tier block (`:338`) | not-scanned | exit 2, diagnostic | none |
| `case_study_scan` | recognized sections (`:469`) | not-scanned | exit 2, report line only | stderr diagnostic |
| `checks_ledger` | check records (`:238`) | not-scanned | exit 2, diagnostic | none |
| `deck_scan` | text runs read from slide faces | not-scanned | exit 0 | gate and diagnostic |
| `differential_scan` | differential and conclusion entries, labeled blocks, and FILLED-proposed items | not-scanned | exit 2, diagnostic | none |
| `discussion_post_scan` | the draft's body text | finding (`empty-body`, new) | exit 0 under a 0/0 bar | the row |
| `discussion_reply_scan` | the replies' text | finding (`word-floor`) | exit 1 | none |
| `filled_vitals_census` | filled heights and filled pressures | not-scanned | exit 2, diagnostic | none |
| `peer_critique_scan` | the critique's text | finding (`word-floor`) | exit 1 | none |
| `reference_scan` | reference entries | not-scanned | exit 2 in `load`, no report | move into `grade`, diagnostic |
| `refusal_scan` | `NOT CODED` lines in the refusal block, well-formed and malformed | not-scanned | exit 2, silent | diagnostic |
| `render_scan` | the final pass's exported pages | not-scanned | exit 2, diagnostic | none |
| `research_ledger` | claim records | not-scanned | exit 2 in `load`, no report | move into `grade`, diagnostic |
| `specificity_scan` | for-entry `SPECIFICITY` flags | not-scanned | exit 0 | gate, remainder, diagnostic |
| `voice_model_scan` | register headings (`:204`) | not-scanned | exit 2, diagnostic | none |

Every member also gains its mapping entry and its kit input. Row names beside `empty-body` are the
builder's. Two predicates are wider than their declared populations and stay: `refusal_scan` gates
well-formed refusals only, and the exit status is identical because a malformed mark is already a
finding; `render_scan` gates an unreadable export on any pass (`:217-219`), documented behavior.

### 9. `deck_scan` reads slide-face text, and its unread parts are a separate ticket

Text runs are counted for titles and table text as well as body text (`:258-269`), so a deck of
titles is graded. A picture-only deck and a SmartArt-only deck both exit 2: the command cannot tell
them apart, so it claims a pass for neither. Reading diagram, chart and other text-bearing parts is a
new population whose membership has to be measured, so it is filed rather than folded in.

### 10. `specificity_scan` reports its unread remainder

Every run reports the for-entry codes `read_entries` finds and how many carry no recognized flag. A
non-zero remainder is `not-scanned`, and a finding still outranks it. A missing flag stays C4's
matter for a reader: the module's own docstring (`:517-519`) refuses to fire C5 on a part count, and
no `missing-flag` row is added.

### 11. `discussion_post_scan` gains an `empty-body` finding

A draft whose body, headings removed (`:412-413`), holds no words is a finding whatever the signed
floors say, because an initial post that says nothing is the run's unmet obligation. The signed floors
are unchanged, and `0` stays legal.

### 12. The rule stops at `MEMBERS`

Outside the family there is no shared runner, kit or exit convention: `uptodate_store search` prints
`0 hit(s)` and exits 0 on an empty index while `guidelines_search` separates a genuine zero (1) from
not having searched (2). The non-member empty reads measured in this session are filed as one
ticket, each to be ruled against its own exit contract.

### 13. `CONTEXT.md` gains two terms

**Load-bearing population** and **Empty-population posture**, beside **Established empty**, which
stays as written and still asserts nothing about which modules sit inside it.

## Superseded, in part

- **ADR 0138 ruling 9**'s refusal to rule the empty-population discriminator beyond its own module is
  superseded for `run_grader.MEMBERS` only. Its reasoning stands, and so does its refusal everywhere
  outside the family. The record's open item *whether every `run_grader` member must declare a
  coverage limb* is answered: a posture, not a limb.

Not superseded:

- **[ADR 0093](0093-the-tracker-gate-section-population-is-derived-from-three-sources-and-a-ratified-limit-is-lifted-into-the-module-it-governs.md)
  ruling 4** refused a documentation object required by habit. This records an exit-status behavior
  whose absence was measured as a false exit 0 in three members.
- **[ADR 0161](0161-the-deck-and-case-study-render-records-name-the-final-pass-and-route.md)
  ruling 4** answered the empty render record as a finding over a directory listing, which ruling 5's
  `finding` conditions describe.
- **ADR 0167 ruling 1** keeps `EXIT_2_LIMBS` off the limits list. Ruling 7 above asserts a diagnostic
  rather than a limb for the same reason: a limb vocabulary on every member is a migration nobody has
  ruled.

## Rejected options

- **Deciding each module alone.** The next grader arrives with no contract, which is what the
  2026-09-09 comment recorded for `apa7_coverage`.
- **A rule with no declaration.** Nothing records how a member meets it.
- **A required coverage field on `Grade`.** A boolean names no population, and `aar_scan`'s finding
  posture has no coverage field to fill.
- **A posture per population.** A deck carrying no dollar figure would exit 2.
- **"Every row vacuous" as a computed property with no named population.** A declaration could not be
  checked against the module.
- **The strict row-count reading.** It is vacuous at `--submission`, where every completion grader's
  after-action review row is graded, and no kit input could get past `deck_scan`'s `load`.
- **Declaring whatever population the existing gate keys on.** It certifies that the code agrees with
  itself.
- **Forbidding a member's other gates.** It would overturn rulings this ticket never read.
- **Leaving postures for the builder to derive.** An unattended agent would be guessing seventeen
  times, and a driven test proves agreement with a declaration, not that it names the right
  population.
- **Declaration only, or an AST check of the predicate.** The first cannot see a false declaration,
  which is `deck_scan` today; the second proves wiring, not behavior.
- **Accepting a refusal in `load` as `not-scanned`.** It keeps the swallowed findings swallowed.
- **`finding` on obligation alone.** It would report thirteen missing checks the reader did.
- **A declared exit-2 limb in the kit.** It is ADR 0167's refused migration arriving through a test.
- **A smallest-clean twin for `finding` members.** The twin would differ in more than the population,
  so a deleted gate could hide behind another.
- **`empty-body` rows for replies and critiques now.** A one-word twin still fails their floors, and
  no measurement asks for them.
- **A `missing-flag` row in `specificity_scan`.** It grades C4 inside C5.
- **Widening `SPECIFICITY` to read a list marker or bold.** The remainder makes the miss visible
  without guessing at forms, and the next unrecognized spelling is caught the same way.
- **Forbidding `0` in the discussion bar.** It contradicts the template, and the floor would stand in
  for a check it is not.
- **Extending the rule to every command in `tools/`.** Those modules share no contract to hang it on.

## What this does not reach

**Whether a declaration names the right population.** The table was ratified on measurements; a
member added later has its population chosen by its author, and the kit proves only that the code
agrees with the declaration.

**A partial read in any member but `specificity_scan`.** The four agents saw exposures in several
members, each where one form goes unread beside forms that are read. They are filed together under
the extractor-coverage rule as [#1066](https://github.com/mshamblin5150-code/clinical-skills/issues/1066).

**Text in a deck part the parser never opens.**
[#1065](https://github.com/mshamblin5150-code/clinical-skills/issues/1065).

**The non-member empty reads.** [#1064](https://github.com/mshamblin5150-code/clinical-skills/issues/1064),
which also carries `guidelines_catalog`'s empty-table parser defect, because its repair exposes an
exit 0 that ruling belongs to.

**Three defects the classification drives found beside the question.** `uptodate_store`'s docstring
promises an exit status its module never returns
([#1067](https://github.com/mshamblin5150-code/clinical-skills/issues/1067)); `differential_scan`
prints row 22 as `NOT RUN` on a run that exits 1 on a row-22 finding
([#1068](https://github.com/mshamblin5150-code/clinical-skills/issues/1068)); and the three discussion
graders disagree on whether a refused reference label suppresses a graded finding
([#1069](https://github.com/mshamblin5150-code/clinical-skills/issues/1069)).

**A population read by indirection a builder's twin does not exercise.** The kit drives the inputs the
test module supplies.

## What must not come out of this

**The rule extended past `run_grader.MEMBERS`** by this record.

**A required coverage field or exit-2 vocabulary on every member.**

**Any member's other ruled gate removed** to fit ruling 3.

**A coverage limb whose predicate is keyed on a count the member no longer reads**, or a `finding`
declared where only a matcher saw the absence.

**A widened `SPECIFICITY` pattern** offered as the fix for the unread remainder.
