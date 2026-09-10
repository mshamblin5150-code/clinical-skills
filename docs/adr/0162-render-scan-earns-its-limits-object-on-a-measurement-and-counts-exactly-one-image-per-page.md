# `render_scan` earns its limits object on a measurement and counts exactly one image per page

[#867](https://github.com/mshamblin5150-code/clinical-skills/issues/867) was filed out of
[#864](https://github.com/mshamblin5150-code/clinical-skills/issues/864)'s grilling, 2026-09-03.
[ADR 0125](0125-render-coverage-and-the-render-record-are-two-properties-and-each-artifact-wires-them-its-own-way.md)
ruling 2 refused to give `render_scan` a limits object just so a pointer had somewhere to sit, and
its ruling 3 filed the question of whether the module earns one.
[ADR 0093](0093-the-tracker-gate-section-population-is-derived-from-three-sources-and-a-ratified-limit-is-lifted-into-the-module-it-governs.md)
ruling 4 declined to require a limits object of every module that has a section, and `CLAUDE.md`'s
**Refusal scan** section records `refusal_scan` earning one on a measurement. So the object follows a
measurement of what a clean run fails to establish, never symmetry with the siblings.

Grilled 2026-09-10. The session began at `origin/main` `65090e0`, was fast-forwarded to `ed52607`
before this record was first written, and was merged forward to `2461c4b`, which carries
[#866](https://github.com/mshamblin5150-code/clinical-skills/issues/866)'s build, before it was
corrected. **Six questions were ruled by the clinician on that date.** The second was ruled, then
re-put after the session found a ratified ruling its framing had omitted, and ruled again. An
adversarial read of the first draft found a duplicated control row, an incomplete test-module list,
two misattributed rulings and several wording errors; they are corrected in place below. Nothing is
built here; this is the record the build reads. A figure counted under `scratch/` below is a dated
floor that nothing committed re-derives.

## Measured before ruling

### Five wrong shapes exit clean, and no export in them is Word's

The module docstring states two limits: a clean run *"does not establish that the retained images are
the pages a reader actually read, or that the visual comparison was careful."* The shapes below were
not derived from those sentences. Each breaks one link in the chain a clean result implies (the
retained export, the page images, the pass graded), so the set could have agreed with the sentences and
did not.

Driven through the real `tools/render_scan.py` against real PyMuPDF 1.27.2.3 output, one pass each
unless stated, a three-page export in every row. **Every export in the table, the controls included,
was written by PyMuPDF and not by Word.**

| retained final pass | exit |
| --- | --- |
| three images rasterized from that export (control) | 0 |
| two images rasterized from that export (control) | 1 |
| a run with no `render/` directory (control) | 2 |
| page 1's image kept under three names | 0 |
| pages 1 and 2 plus two images of another document | 0 |
| three images of another document | 0 |
| three blank images | 0 |
| a lower pass holding the document and a higher pass holding another one | 0 |

Under the negation, that the two sentences are complete, every clean row would be wrong only in a way
an absent or careless reader explains. Read literally, the sentences name none of the five shapes.
Read generously, a careful reader comparing every image with the Markdown catches all five. **What
survives any reader is common to every row, the first control included:** its pages really are the
pages of its export, and neither the command nor the images can tell that the export was not Word's
pagination.

### The two prose copies are unbound and already differ

`CLAUDE.md`'s **Render scan** section states the same two limits as *"the PNG files are the pages a
reader opened or that the comparison was careful"*, against the docstring's *retained images*,
*actually read* and *visual comparison*. The same section says `tools/test_render_scan.py` covers
*"the prose binding"*. Every tracked-prose assertion in that file reads
`skills/practicum-case-study/SKILL.md`, and its one docstring assertion reads the ADR 0125 line;
neither copy of the limits is read by any test.

### The comparator's `>=` has no ruling, and no caller relies on it

`render_pass.images_cover_exported_pages` returns `image_count >= exported_pages`. No ADR rules the
inequality, and the written contracts disagree with each other. `render_scan`'s module docstring says
*one readable PNG per imaged page*, `skills/practicum-case-study/SKILL.md` step 9 says *one 120-dpi PNG
per page* and `skills/course-assignment/SKILL.md` *one 120-dpi PNG per slide*; the helper's own
docstring, step 9's *at least one PNG for every page* and course-assignment's *at least one readable
image for every exported page* state the inequality. The helper has four callers: `render_scan` and
the three producers, each of which counts `*.png` in a fresh staging directory after
`page_image.rasterize` wrote exactly one image per page, with no image written in between.

With the helper replaced at run time by `==`, the seven test modules that name a caller ran 194 tests
at `2461c4b` with no failure or error: `test_case_study_render`, `test_course_assignment_skill`,
`test_deck_render`, `test_discussion_post_render`, `test_discussion_post_scan`, `test_module_sections`
and `test_render_scan`. Had any test encoded a surplus pass as legitimate, that run would have failed;
the suite cannot speak for an untested path, and the producers' code covers that half. The first draft
of this record reported 215 tests over a hand-picked module list that left out
`test_course_assignment_skill`.

Across 44 registered checkouts, 10 hold a scratch root, and together they hold 4 render roots. Of
their 4 final passes, 3 have a single readable export and exactly as many readable images as exported
pages, every set named one stem from 1 through N; the fourth has no readable export and already exits
2. Neither equality nor a naming rule would flip one of them.

### The in-pass filename ruling exists and was nearly reversed by omission

[ADR 0124](0124-the-render-pass-is-one-shared-reader-and-a-gap-is-counted-rather-than-graded.md) rules
*"the filenames inside a pass stay each producer's business, behind a globbed shape"*, on two grounds:
uniform names buy nothing a glob does not have, and imposing them invalidates retained evidence.
`CONTEXT.md`'s **Render pass** states the rule, and
[ADR 0160](0160-the-pdf-engine-is-reached-through-one-seam-the-page-questions-are-four-and-the-availability-verdict-is-the-caller-role.md)
relies on that entry. The first framing of the comparator question offered a naming rule without
citing it. The second ground does not re-derive today, since no retained final pass would flip; the
first still holds, because whether an image shows its page is a content question no name answers.

### The population behind the ticket's decision 3

`run_grader.MEMBERS` holds 17 modules. Checked by import for eight object names, the seven in
`test_claude_pointers.LIMIT_CONSTANTS` plus `EXIT_2_LIMBS`, four hold none: `anchor_scan`,
`block_scan`, `filled_vitals_census` and `specificity_scan`. `differential_scan` holds
`NOT_VALIDATED_AGAINST`, and `render_scan` held only `EXIT_2_LIMBS`, which states what a run could not
measure rather than what a clean run fails to establish. Each of the four states limits in prose in its
module docstring and in its `CLAUDE.md` section, with nothing binding the two surfaces, which is
#867's shape. For `specificity_scan` the two surfaces state different limits: its `CLAUDE.md` section
rests the advisory count on C2, and its module docstring never names C2.

## Ruled 2026-09-10

### 1. `render_scan` earns `DECLARED_LIMITS`

The earned object is `render_scan.DECLARED_LIMITS`, of `(subject, reason, EvidenceDisposition)`
triples using `run_grader.EvidenceDisposition`, as `discussion_post_scan` does. It is earned by the
route alone, which survives any reader; the five shapes add to it only on a literal reading of the
docstring's two sentences. ADR 0125 ruling 2's refusal stands as written: it refused an object added
for symmetry, and this one is added on a measurement.

The object is spelled `DECLARED_LIMITS` so that `test_declared_limits.declarers()` sees it; whether
that walk should count other spellings is not decided here (ruling 6).

### 2. The comparison is exact, and filenames stay each producer's business

`render_pass.images_cover_exported_pages` returns `image_count == exported_pages`, and its docstring
says exactly one retained image per exported page. The shared helper changes rather than a local
comparison in `render_scan`, because every producer already writes exactly one image per page.

A final pass holding more readable images than exported pages becomes an exit 1
`final-page-coverage` finding. Earlier passes stay reported and ungraded. The sentences that state the
inequality or name only a short pass change with it: `skills/practicum-case-study/SKILL.md` step 9's
*at least one PNG for every page* and *fewer PNGs than exported pages is exit 1*;
`skills/course-assignment/SKILL.md`'s *at least one readable image for every exported page* and its
matching exit-1 sentence; `render_scan`'s module docstring exit statement; and `CLAUDE.md`'s *a
measurable short final pass is exit 1*. The assertion in `test_render_scan.TheSkillSaysWhatThisGrades`
that pins step 9's exit-1 sentence moves with it.

ADR 0124's in-pass filename ruling stands. A final pass with the right count and names outside a
`<stem>-1..N.png` sequence stays clean, and falls under ruling 3's content row.

### 3. The object holds six rows

- **whether the retained images are the pages a reader actually read**: the docstring's first clause,
  kept in its words; declared reading.
- **whether the visual comparison was careful**: the docstring's second clause, kept in its words;
  declared reading.
- **whether the retained images show the export's pages**: coverage counts readable PNG files against
  the export's page count and never compares an image with a page, so a blank image, an image of
  another document, or one page kept under several names is counted; behavior.
- **whether the export is Word's pagination**: the command counts the pages of whatever single PDF or
  XPS a pass retains and reads nothing naming the route that produced it; behavior.
- **whether the graded pass shows the submitted document**: the command reads only `render/` and opens
  no document, so a complete final pass exported from an earlier draft is clean;
  [#1020](https://github.com/mshamblin5150-code/clinical-skills/issues/1020) is named as the open
  owner of binding a pass to the document's bytes; behavior.
- **the authority for render wiring**: ADR 0125 is the governing record, as in
  `discussion_post_scan.DECLARED_LIMITS`; declared reading.

The route and document rows are carried even though #866's build, merged as PR #1041, gave
`deck_scan.DECLARED_LIMITS` and `checks_ledger.DECLARED_LIMITS` record-side rows for a skipped
`render_scan`, an unproven `SOURCE` and unbound document bytes. Those rows say what a record grader
does not establish about a reader's record; these say what a clean `render_scan` exit does not
establish, and `render_scan` is the command that passed #1020's submission.

### 4. The docstring and `CLAUDE.md` point at the object and copy no row

The docstring's limits paragraph becomes one sentence naming `render_scan.DECLARED_LIMITS`, followed
by its unchanged sentence that `checks_ledger.py` separately grades the substantiated
`the rendered document` verdict. That sentence is an ownership statement and not a limit. The ADR 0125
line leaves the docstring for the object.

`CLAUDE.md`'s **Render scan** section replaces *"It cannot establish that the PNG files are the pages a
reader opened or that the comparison was careful"* with the same pointer, and its *"the prose binding"*
names the surface that sentence actually binds.

`tools/test_render_scan.py` asserts the pointer appears exactly once in the module docstring and
exactly once in the **Render scan** section, and that
`prose_bind.bind(render_scan.DECLARED_LIMITS, surface, mode=NAMING)` returns nothing for each.
`test_scratch_census` is the precedent. `TheRenderWiringDecisionIsPublished` reads `"ADR 0125"` from
`render_scan.DECLARED_LIMITS` rather than from `render_scan.__doc__`. `test_claude_pointers` then
covers the section's pointer by construction.

### 5. Each row carries one disposition, and the three behavior rows have controls

`tools/test_render_scan.py` gains, on its existing fake engine:

- a partition test in `test_case_study_scan.EveryDeclaredLimitHasAnEvidenceDisposition`'s form: every
  row carries one disposition, and the behavior rows are exactly the content, route and document rows;
- a content control: three byte-identical images for a three-page export exit 0;
- a route control: a pass whose export no Word instance produced exits 0;
- a document control: a complete final pass beside a differing `case-study.docx` in the run directory
  exits 0;
- a comparator control: four readable images for a three-page export exit 1.

Each behavior control asserts its boundary still holds, so a build that closes one fails its control
and has to retire the row in the same change. The document control is the one expected to fire first,
when #1020 is built. The real-engine table above stays in this record and is not rebuilt as a test.

### 6. #867 closes on `render_scan`, and the other four go to their own ticket

The ticket's decision 3 fired on its own trigger. The name-keyed population question belongs to
[#921](https://github.com/mshamblin5150-code/clinical-skills/issues/921), which already owns it. The
four members holding no limits object under any of the eight names go to one new `grilling` ticket,
[#1038](https://github.com/mshamblin5150-code/clinical-skills/issues/1038), that applies this record's
method to each: shapes built from the command's own input chain, a stated negation, and one verdict per
module. That ticket inherits ADR 0125 ruling 2's refusal of an object added for symmetry.

## Rejected options

- **Declaring the surplus comparison instead of fixing it.** The row would declare a gap between the
  module's code and its own written contract, not a boundary of what the instrument can reach.
- **A pixel join between each retained image and a fresh rasterization of the export.** Exact equality
  assumes the same PyMuPDF on the rendering and the grading machine, which is unmeasured here with one
  installed version; a tolerance would be an ungrounded threshold. It also overlaps #1020's decision 1.
- **A `<stem>-1..N.png` naming rule beside equality.** It supersedes ADR 0124 and the glossary entry
  ADR 0160 relies on, for a check a hand-placed pass satisfies by naming its files, while the content
  question it seems to answer stays open.
- **Only the route row, or neither record-side row.** Only the route row would leave #1020's recorded
  failure undeclared in the module that produced it. Neither row would send a reader standing in
  `render_scan` to a different grader about a different artifact half.
- **Keeping the docstring's sentences beside the object, or keeping both prose copies bound to it by
  an agreement test.** The first leaves a second copy inside one file, which is
  [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape. The second is
  three copies held by one test, which is what
  [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241) replaced.
- **All six rows as declared readings.** Nothing would fail when #1020 closes the document row.
- **A real-PyMuPDF test class reproducing the table.** It skips on every machine without the library,
  CI included, and adds no row the fake-engine controls do not already evidence.
- **Measuring the other four members inside #867, filing one ticket each, or recording them only on
  #921.** None of them bears on `render_scan`'s correctness. Four tickets would re-derive one method
  four times. A comment on #921 would leave the per-module question with no owner.

## What this does not reach

**Whether a retained image shows its page, whether an export is Word's, and whether a pass shows the
submitted document.** Each is declared by ruling 3 and closed by nothing here. The last is #1020's.

**Whether `render_scan` was run at all.** #866's build declares that in `deck_scan` and
`checks_ledger`.

**Whether `anchor_scan`, `block_scan`, `filled_vitals_census` or `specificity_scan` earns an object.**
That is #1038.

**Which object names `test_declared_limits.declarers()` counts.** That is #921's.

**Whether the pointer sentences stay true.** Ruling 4's tests assert that the pointers exist and copy
no row; a row that is wrong about the tree is caught only where ruling 5 gives it a control.
