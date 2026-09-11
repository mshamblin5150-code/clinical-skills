# The limits walk reads a declared name list and a module without limits is declared

[#921](https://github.com/mshamblin5150-code/clinical-skills/issues/921) was found during the tracker
sweep out of [#781](https://github.com/mshamblin5150-code/clinical-skills/issues/781)'s grilling,
2026-09-06. `test_declared_limits.declarers()` counts a module only when it binds the literal name
`DECLARED_LIMITS`, so a module that declares its limits under `NOT_REACHED` is invisible to the walk
that polices the population.

That key was chosen on purpose.
[ADR 0119](0119-the-limit-row-type-stays-per-module-the-evidence-disposition-moves-to-the-grader-runner-and-the-declarer-walk-is-candidacy-derived.md)
ruling 4 made candidacy the one literal and listed a matcher over any other container name under
*what must not come out*. The same day,
[ADR 0120](0120-the-claude-md-limits-pointer-walk-is-name-keyed-section-scoped-and-shape-blind-and-an-unreadable-object-is-not-a-clean-one.md)
ruling 1 gave the `CLAUDE.md` pointer walk seven names. Later records deferred the difference:
[ADR 0135](0135-the-session-law-is-one-grammar-limb-the-loose-spelling-is-refused-and-the-legal-reader-states-its-composition.md)
ruling 5, [ADR 0145](0145-the-republished-date-element-is-shared-grammar-keyed-on-its-second-element.md)
ruling 9, [ADR 0162](0162-render-scan-earns-its-limits-object-on-a-measurement-and-counts-exactly-one-image-per-page.md)
ruling 6 and [ADR 0165](0165-tests-list-git-paths-through-git-paths-and-no-shared-tree-reader-is-built.md)
each left it here, and
[ADR 0158](0158-the-prose-bind-is-one-instrument-and-its-rule-carries-an-identity.md) ruling 7
assigned this ticket a bind rule over the same objects.

Grilled 2026-09-10. The session began at `origin/main` `b726bd1` and was fast-forwarded to `6222111`
before this record was written; every figure below was re-derived at `6222111` unless it says
otherwise. **Eight questions were ruled by the clinician one at a time on that date.** Nothing is
built here; this is the record the build reads. Every count is a dated measurement with its
instrument named, and every one is a floor.

## Measured before ruling

### The two walks disagree about one population

`declarers()` returns **24**. An AST walk over every `tools/*.py` for a module-level binding of one
of the nine names in ruling 2, counting a binding computed from another listed object in the same
module as a view rather than an authored object, finds **43 authored objects in 41 modules**. Of
those modules, **17** are outside `declarers()`: `artifact_lock`, `artifact_provenance`,
`differential_scan`, `discussion_artifact`, `docx_write`, `guidelines_catalog`, `guidelines_extract`,
`reference_scan`, `test_skill_agreement`, the six tracker modules `tracker_bodies`,
`tracker_branch_scope`, `tracker_freshness`, `tracker_merge_receipt`, `tracker_publish_hook` and
`tracker_readback`, and `voice_corpus` and `voice_model_scan`. *Had the walk seen every module that
declares limits, that difference would be empty; it is 17.*

The blind spot has already published a false clause. ADR 0145 ruling 9 placed rows into
`reference_scan.NOT_REACHED` *"which is inside `test_declared_limits.declarers()`'s walk"*; it is not,
[ADR 0146](0146-both-apa7-sections-append-and-the-translation-rule-lives-once-at-section-31.md)
ruling 6 withdrew the claim, and the suite stayed green throughout.

### Every candidate row reads as the same concept, except one

`pdf_engine.DECLARED_LIMITS` holds *"A declaration does not establish that a consumer has the right
role."*; `tracker_freshness.NOT_REACHED` holds *"The gate reads the commit base and no tracker
record."* Both tell a reader that a clean run covers less than it appears to, which is the whole of
`CONTEXT.md`'s **Declared limit**, decided *"on the sentence and never on the constant's name."*

`EXIT_2_LIMBS` is not that. `render_scan`'s five limbs are exit-2 conditions, and the five wrong runs
ADR 0162 drove all exit 0 and match no limb.

### The shared name list cannot take a qualified name without moving its pointer test

Measured at `b726bd1`; `tools/test_claude_pointers.py` did not change in the merge. Appending
`LEGAL_READER_NOT_REACHED` and `README_NOT_REACHED` to `LIMIT_CONSTANTS` in process turns exactly one
of its eight tests red: `test_limits_ish_candidates_are_deliberately_classified`, which asserts the
list **equals** the limits-looking constants `CLAUDE.md` points at. `LIMITS_ISH` matches neither
qualified name. ADR 0120 ruling 2 rules that reporter as naming a pointed constant *"that is not among
them"*, a subset; the equality is the build's and is stricter than its ruling.

### Most modules carry nothing, and five arrivals were caught by eye

Of **92** non-test modules, **53** bind none of the nine names: 4 are `run_grader.MEMBERS`
(`anchor_scan`, `block_scan`, `filled_vitals_census`, `specificity_scan`, owned by
[#1038](https://github.com/mshamblin5150-code/clinical-skills/issues/1038)), 30 are other modules
whose source contains `__main__`, and 19 are helpers.

#921's thread records five modules ordered or built with no limits object and nobody deciding
whether one was owed: `apa7_coverage` (ADR 0154), `pdf_engine` (ADR 0160), `grader_conformance`
(ADR 0163), `case_study_render` (ADR 0142), and `post_html`'s URL matcher on PR #1043. A sweep reader
caught each. `pdf_engine` and `grader_conformance` contain no `__main__`, so a register of commands
alone would have missed two of the five.

### Binds, counted

A read-only census at `b726bd1` over the 40 objects then authored under the seven names counted, per
object, test methods calling `prose_bind`'s `bind` or `copied_leaves` in `NAMING` mode on a prose
surface with the object or a view of it as the first argument, plus `test_claude_pointers`' `CLAUDE.md`
walk, which calls the same `bind`: **3 objects had none, 18 had exactly one, 19 had two or three.**
The parent re-derived the walk's call, the three unbound objects (`adr_next`, `discussion_post_scan`,
`pdf_engine`, none bound in any test and none pointed at from `CLAUDE.md`), and at `6222111` that the
new `suite.DECLARED_LIMITS` is pointed at from `CLAUDE.md`. The 18 and 19 split is the census's and
was not re-derived by the parent.

ADR 0119's mention check, widened to the nine names, misses one object: `voice_model_scan.NOT_REACHED`,
bound only through `CLAUDE.md` and named by no test.

### Real limits sit under other names

`run_grader.WALK_CEILING` holds *"…grader shapes assembled differently are invisible"* and
`run_grader.TEXT_READ_WALK_CEILING` holds *"AST floor over direct .read_text calls… indirect readers,
and computed error modes are invisible"*; ADR 0112, ADR 0117 and `test_run_grader` cite both names.
`guidelines_catalog.CORPUS_SIZE_CHECK_LIMITS` holds *"a same-name same-size rewrite is outside its
reach"* beside the module's `NOT_REACHED`, and nothing outside the module names it.
`guidelines_manifest.DISCOVERY_CEILING` is a tuple of tokens a walk looks for, and
`threshold_sheet.SCOPE_SUMMARY_NOT_REACHED` is already a view of `DECLARED_LIMITS` under ADR 0074
ruling 3; neither is a limit.

### A warning's price depends on its pattern

Over module-level constants in non-test modules, excluding the nine names and the three constants
above: ADR 0120's `LIMITS_ISH` fires on **40**, mostly finding labels such as `NOT_SCANNED` and
`NOT_FOR_ENTRY`. The pattern `(?<!DE)LIMIT|CEILING|LIMBS|ORPHAN|NOT_REACHED` fires on **23**: 9 are
referenced inside a listed object in the same module (`scratch_census`'s seven `*_LIMIT`,
`discussion_reply_scan`'s two), and **14** are not limits: five `EXIT_2_LIMBS`, two `DEFAULT_LIMIT`,
`apa7_coverage.SECTION_LIMITS` and `MEDIA_LIMITS`, `peer_critique_scan.WORD_CEILING_COUNT`,
`guidelines_manifest.DISCOVERY_CEILING`, `map_scan.LIMITS_POINTER`, `skills_mirror.ORPHANS`, and
`threshold_sheet.SCOPE_SUMMARY_NOT_REACHED`.

## Ruled 2026-09-10

### 1. A limits object is one concept under several names, and the walk reads a declared name list

`declarers()` stops keying on the literal `DECLARED_LIMITS` and reads a declared list of names. This
supersedes ADR 0119 ruling 4's single literal and the line under that record's *what must not come
out* refusing any other container name. That ruling's reason survives the change: the literal was
chosen so the walk would never grade a module on the shape of its rows, and a list of names reads no
row either.

`EXIT_2_LIMBS` is not on the list. It names ways a run could not be measured, not what a clean run
fails to establish.

### 2. The list is nine names, held once

The seven from `test_claude_pointers.LIMIT_CONSTANTS` plus `LEGAL_READER_NOT_REACHED` and
`README_NOT_REACHED`. Neither qualified object is renamed: ADR 0135 ruling 5 chose the first name on
purpose, citations in `CONTEXT.md`, `apa7.md` and `test_reference_scan` resolve through it, and the
second scopes one gate in a module that holds many.

The list moves into `prose_bind`, as ADR 0158 ruling 7 already sends the vocabulary with ruling 2's
lift, and both walks import it. `test_limits_ish_candidates_are_deliberately_classified` changes from
equality to the subset ADR 0120 ruling 2 rules: every limits-looking constant `CLAUDE.md` points at is
on the list.

### 3. A module that carries no limits object says so, with a reason

Every non-test module in `tools/` either binds a listed name or appears on a declared **no-limits**
list with a one-line reason. A module with neither fails. This adds no obligation to carry an object:
ADR 0093 ruling 4 and ADR 0119's acceptance of a module with none both stand, and what changes is only
that the absence is recorded rather than silent. The four graders' entries name #1038 as the owner of
their per-module verdict, and a module that later earns an object leaves the list.

### 4. The no-limits list is one map beside the walk

A `module → reason` map in `tools/test_declared_limits.py`, in the arrangement of
`test_module_sections.DECLARED_SECTIONS` and `run_grader.REFUSED`. An entry for a module that no
longer exists, or that now binds a listed name, fails. A reason must be non-empty and nothing more,
the bar `test_run_grader` applies to `REFUSED`. The walk stays a disk walk in that module, which is
ADR 0165's constraint.

### 5. Every limits object carries at least one no-copy bind

Every authored object under a listed name, in a test module or not, has at least one no-copy bind
through `prose_bind` on a real prose surface, and `test_claude_pointers`' `CLAUDE.md` walk counts as
one. This supersedes the word *exactly* in ADR 0158 ruling 7. That ruling closes the hole of an object
with **no** bind; its extra binds guard different documents, and removing them to reach a count
would remove coverage.

### 6. The mention check retires

ADR 0119 ruling 4's assertion that some test names the object is removed. ADR 0119 called it a floor
that passes *"whether it asserts the pointer resolves, the rows are derived, or nothing at all"*, and
ruling 5 is the real form of the same obligation over the same population.

### 7. A limit under another name folds into its module's one object, and the old name survives as a view

ADR 0074 ruling 3's arrangement for `SCOPE_SUMMARY_NOT_REACHED`, applied twice:

- `run_grader` gains a limits object holding the two ceilings, and `WALK_CEILING` and
  `TEXT_READ_WALK_CEILING` become views of its rows, so ADR 0112, ADR 0117 and `test_run_grader`
  still resolve.
- `guidelines_catalog.CORPUS_SIZE_CHECK_LIMITS`'s two rows join `guidelines_catalog.NOT_REACHED`; no
  citation outside the module needs the old name, so it goes.

The name list stays at nine and each module keeps one limits object.

### 8. A new limits-looking constant fails until it is classified

Over module-level constants in non-test modules, a name matching
`(?<!DE)LIMIT|CEILING|LIMBS|ORPHAN|NOT_REACHED` that is not a listed name passes only when a listed
object in the same module references it, when its value is built from a listed object, or when it is
on a declared *not a limit* map with a reason. The 14 constants measured above take entries. An entry
naming a constant that no longer exists fails. ADR 0120's pointer pattern is untouched; it reads a
different population.

## Superseded, in part

- **ADR 0119 ruling 4**: candidacy by the literal `DECLARED_LIMITS`, assertion 1, and the *must not*
  line against container names beyond that literal. Rulings 1, 2, 3 and 5 stand, and so does the refusal
  of a shared row type and of a matcher over row shapes.
- **ADR 0158 ruling 7**: *exactly one* becomes *at least one*. The rest stands, including the shared
  detector and `test_prose_bind`'s walk staying untouched.

ADR 0120 is not superseded; the equality test changed by ruling 2 is stricter than its own ruling 2.
The deferrals in ADR 0135 ruling 5, ADR 0145 ruling 9, ADR 0146 ruling 6 and ADR 0162 ruling 6 are
answered.

## Rejected options

- **Renaming every object to `DECLARED_LIMITS`.** `docx_write` holds three separate objects, and
  ratified records, `CLAUDE.md` and `CONTEXT.md` cite the names.
- **Keeping the single literal and labeling the walk's scope.** The blind spot stays; only its label
  changes.
- **Matching a `*_NOT_REACHED` suffix instead of adding two exact names.** A pattern as the population
  key is what the declared list replaces, and a pattern reads every future constant that happens to
  share the suffix.
- **Renaming the two qualified objects to plain `NOT_REACHED`.** It reverses ADR 0135 ruling 5 and
  makes `README_NOT_REACHED` read as the limits of all of `test_skill_agreement`.
- **Leaving a module with no object silent.** Five arrivals were caught only by a reader.
- **A count ratchet of modules with none.** It records no reason, and one module gaining an object
  while another loses one nets to zero.
- **A register of commands only.** Two of the five recorded arrivals are not commands.
- **A per-module constant or a docstring sentence carrying the reason.** Fifty-three files and a new
  name for the first; a walk keyed on prose wording for the second. ADR 0119 ruling 5 refused a
  per-module reason constant that nothing cites.
- **Exactly one bind.** Nineteen objects would lose binds that guard other documents.
- **Taking the bind rule off this ticket.** ADR 0158 ruling 7 named this ticket its home, and the
  missing-bind hole would stay open.
- **Keeping the mention check beside the bind rule, or requiring a bind in the module's own tests.**
  The first is two walks over one population; the second reverses ruling 5's counting of the
  `CLAUDE.md` walk.
- **Adding `WALK_CEILING`, `TEXT_READ_WALK_CEILING` and `CORPUS_SIZE_CHECK_LIMITS` to the list.**
  Generic names would join a list read in every module, and `guidelines_catalog` would hold two limits
  objects.
- **Listing `run_grader` as having no limits.** The entry would contradict what the list means.
- **No warning for limits-looking constants, or one reading test modules too.** Three real limits were
  found by hand; test modules add twelve entries that are mostly exemption ceilings.
- **ADR 0120's `LIMITS_ISH` as the warning's pattern.** Forty hits, mostly finding labels.

## What this does not reach

**A limit held under a name the warning's pattern does not match.** A plain-named constant carrying a
limit sentence passes every assertion here.

**Whether a no-limits reason or a not-a-limit reason is true.** The walk checks that one exists.

**Whether a bind is on the right surface or the prose describes the limit correctly.** ADR 0158's own
ceiling, inherited.

**A limit held as something other than a string.** ADR 0120 ruling 3's ceiling, inherited.

**A test module that carries no limits object.** Test modules are outside the no-limits list and the
warning.

**A binding assembled at run time, or a bind reached through `getattr` or a loop variable.** An AST
walk cannot resolve either; an object bound only that way needs a resolvable bind or a `CLAUDE.md`
pointer.

**Which of `anchor_scan`, `block_scan`, `filled_vitals_census` and `specificity_scan` earns an
object.** That is #1038.

## What must not come out of this

**A requirement that every module carry a limits object.** Ruling 3 records a reason; ADR 0093
ruling 4 stands.

**A shared row type or uniform container.** ADR 0119 ruling 1 and ADR 0080 ruling 3 stand.

**A rename of any object to fit the list.** Names survive; the list grows by exact name or a limit
folds into its module's object.

**A deleted bind to satisfy a count.**

**A repository-wide limits-object count in prose without its instrument.** The walk owns the
population; `CLAUDE.md` and ticket text point at it.
