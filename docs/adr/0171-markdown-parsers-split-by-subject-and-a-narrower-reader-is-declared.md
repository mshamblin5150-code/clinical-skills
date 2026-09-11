# Markdown parsers split by subject and a narrower reader is declared

[#1002](https://github.com/mshamblin5150-code/clinical-skills/issues/1002) was filed out of
[#835](https://github.com/mshamblin5150-code/clinical-skills/issues/835)'s grilling, 2026-09-09.
[ADR 0158](0158-the-prose-bind-is-one-instrument-and-its-rule-carries-an-identity.md) ruling 6 sent
the general-purpose Markdown parsers in `tools/test_skill_agreement.py` out of that module and left
their destination open. No tool imports a test module, and nothing imports `test_skill_agreement`, so
the tree's only ruling-ordinal parser and its strongest link resolver were unreachable from any tool.

Grilled 2026-09-11 at `origin/main` `d148087`. Every figure below was measured at that commit unless
it names another source.

## Measured before ruling

### The population is wider than the ticket's four

The ticket names a step-citation resolver, a link resolver, a ruling-ordinal parser and a
ruling-citation resolver. Three more readers belong to the same subject:

- **A second link extractor in the same module.** `README_MARKDOWN_TARGET` is `\]\(([^)]+)\)`,
  feeding `readme_repository_paths`. It keeps an angle-bracket destination's brackets, truncates at a
  nested parenthesis, keeps a link title inside the destination and never reads a reference-style
  link. Over `README.md` it returns the same 11 destinations as `markdown_targets`, in the same order.
- **Two exemption readers that are one function.** `exemptions` and `ruling_exemptions` differ only
  in the marker pattern they match, and both return the shared `Exemption` type.
- **A second paragraph splitter in another test module.** `test_run_record_claim.blocks` states the
  same one-indexed contract as `paragraphs`. Over all 704 tracked `.md` and `.py` files the two return
  identical output; a control that differs only by a blank line proves the comparison can report a
  difference. `docx_write.blocks` is a renderer lexer with a different contract and is outside this
  population.

A tree-wide search for the ruling heading and item patterns finds them in `test_skill_agreement.py`
alone, so `ruling_ordinals` is the only implementation of its kind that a pattern search can find.

### What the moving code reads from the module it leaves

A walk of each moving definition's syntax tree, collecting every name it reads that the module itself
defines, finds one name that stays: `exemptions` reads `EXEMPT_MARKER`. The same walk over the four
liveness classes finds four cases reading stay-behind logic, listed under ruling 6; every other
module-defined name those classes read is `REPO_ROOT` or the file reader `read`. The walk reads names
rather than calls, so it reports a constant such as `STEP_HEADING`; a search for call syntax would
not have. It does not count imported names.

### Corrections to the ticket's own account

- `paragraphs` and `exemptions` are not exercised only transitively. A case-study test calls
  `paragraphs` directly and the escape-hatch ceiling assertion calls `exemptions` directly. What is
  true is narrower: none of the three substrate readers has a liveness class of its own.
- Every case of `TheDeadLinkResolverIsLive` that drives the link resolver is synthetic. Its one
  real-tree case tests `graded_files`, and ruling 6 keeps it with that helper. The only real-tree read
  of the link resolver is `EveryRelativeLinkResolvesToAnIndexedPath`, a gate over the skill-agreement
  population.

### The publish gate's link reader, against the population it reads

`tracker_branch_scope.REPO_RELATIVE_MARKDOWN_PATH` feeds the `branch:repo-relative-link` rule, which
refuses every repository-relative Markdown link in tracker text, because such a link resolves against
the issue URL rather than the repository. It is a refusal of the form, not a check that the path
exists. Its agreement with `markdown_targets` over tracked files measured a different population.
Driven through the gate's `grade` on a synthetic comment:

| form | the gate's reader | the refusal |
| --- | --- | --- |
| a title after the destination | reads the path correctly | fires |
| a nested parenthesis | truncates the path | fires |
| an angle-bracket destination without whitespace | reads it with its brackets | fires |
| an angle-bracket destination containing whitespace | reads nothing | does not fire; undeclared |
| a reference-style link definition | reads nothing | does not fire; undeclared |

The 2026-09-10 sweep harvest holds 6,205 non-empty title and body fields across the issues endpoint
and issue comments. Across them, `markdown_targets` read no repository-relative destination that the
gate's reader missed, and a raw count finds no field carrying an angle-bracket destination or a
reference-style definition. A control proves `markdown_targets` reads a reference-style link the
gate's reader does not, so a field carrying either silent form would have appeared. In the other
direction, the gate's unmasked pattern read something `markdown_targets` did not in 19 fields; the one
audited is a link inside a code span, which `markdown_targets` masks, and the gate masks code before it
extracts.

## Ruling 1. Two modules, split by subject

`tools/markdown_read.py` holds the generic Markdown readers. `tools/adr_read.py` holds the ADR-record
readers and imports `markdown_read`. The consumer sets do not overlap: a tool that resolves links has
no use for ruling ordinals, and the publish gate must not import ADR vocabulary to reach a paragraph
splitter.

`markdown_read` receives `unfenced_lines`, `paragraphs`, `MarkdownTarget`, `markdown_targets` with its
private destination helpers, `dead_links`, the exemption reader under ruling 2, and the step reader
under ruling 5. `adr_read` receives `ruling_ordinals`, `RulingCitation`, `ruling_citations`,
`unresolved_ruling_citations`, and `RULING_EXEMPT_MARKER`. Each module also receives every module-level
pattern its definitions read.

`walk_ruling_citations` and `declared_rulings` stay in `test_skill_agreement.py`: each walks a
population the test module grades, and a walk's population is named where it is used
([ADR 0165](0165-tests-list-git-paths-through-git-paths-and-no-shared-tree-reader-is-built.md)
ruling 2). `ruling_shape_findings` and the other ruling-shape assertion helpers stay with the
assertions they serve. Anything else this record does not name as moving stays.

Both are libraries with no command. Each arrives with a limits object rather than a no-limits entry,
the choice
[ADR 0167](0167-the-limits-walk-reads-a-declared-name-list-and-a-module-without-limits-is-declared.md)
ruling 3 requires every non-test module to make, because each has a real boundary to state. ADR 0167
ruling 5 obliges a no-copy bind on each object, and ADR 0167 ruling 8 classifies any new constant that
looks like one.

## Ruling 2. The substrate is public, and the two exemption readers become one

`unfenced_lines`, `paragraphs` and the exemption reader are public in `markdown_read`, because callers
other than the moved parsers use them. `test_skill_agreement.py` imports them back.

`exemptions` and `ruling_exemptions` collapse into `marker_exemptions(text, marker)`, and the caller
passes the compiled marker pattern. That also removes the only stay-behind name any moving definition
reads. `RULING_EXEMPT_MARKER` moves to `adr_read` beside `unresolved_ruling_citations`, and the ruling
ceiling assertion imports it. `EXEMPT_MARKER`, `EXEMPT_CEILING`, `RULING_EXEMPT_CEILING`,
`RULING_UNNUMBERED_CEILING` and every assertion reading them stay in `test_skill_agreement.py`.

The ground is the measurement that the two functions differ only in their pattern. ADR 0158 ruling 3
is the nearest precedent, where a shared helper takes the variant as an argument rather than
inferring it, though that ruling concerned the mode of a prose bind rather than a marker.

## Ruling 3. The README gate reads its links through `markdown_targets`

`readme_repository_paths` takes its linked candidates from `markdown_read.markdown_targets`, and
`README_MARKDOWN_TARGET` is deleted. The code-token candidates and the resolution policy in
`_readme_path` are unchanged.

No recorded defect asks for this. It is made because the module's thesis is that general-purpose
Markdown parsers leave it, and a weaker one would otherwise stay. It is a measured no-op on today's
`README.md`. It adds angle-bracket and reference-style destinations the regex did not read as paths,
and reads parenthesized and titled destinations correctly where the regex read a wrong path. It
narrows the gate in one direction: `markdown_targets` masks code, so a link inside a code span or a
fenced block stops being read as a link. The code-token reader still reads a code span, and nothing
reads a fenced block.

## Ruling 4. The publish gate keeps its reader and declares the two silent forms

`tracker_branch_scope` takes neither `markdown_targets` nor `dead_links`.
`tracker_branch_scope.NOT_REACHED` gains two rows: a reference-style link definition, and an
angle-bracket destination containing whitespace, each read as no repository-relative link, so a
relative link written either way publishes without the refusal.

The gate's reader is a declared narrower reader. No field in the harvest carried either form, and
converging would change what a publication gate decides on no recorded defect. If such a link is
recorded escaping the refusal, converging is the remedy, and the harvest measurement above is its
baseline rather than its justification.

## Ruling 5. The step reader moves under neutral names

`step_citations` moves to `markdown_read` and keeps its name, because its pattern matches the literal
word. `Citation` becomes `StepCitation` and its `skill` field becomes `subject`. The limb values
`beside`, `carried` and `owner` are unchanged. The reader already takes its names and owner as
arguments and holds no skill vocabulary.

`owning_skill`, `declared_steps`, `STEP_HEADING`, `graded_files`, `skill_names`, `walk_citations`,
`stale_citations` and `undeclared_citations` stay in `test_skill_agreement.py`.

## Ruling 6. A liveness case moves with the reader it proves, and the link resolver gains a real-tree case

The cases of `TheStepResolverIsLive` and `TheDeadLinkResolverIsLive` move to
`tools/test_markdown_read.py`, and the cases of `TheRulingOrdinalParserIsLive` and
`TheRulingCitationResolverIsLive` move to `tools/test_adr_read.py`, except four cases that test a
helper this record keeps. Those four stay in `test_skill_agreement.py`, under class names describing
the helper each tests:

| case | the helper it tests |
| --- | --- |
| `test_a_step_heading_is_read_and_a_numbered_list_is_not` | `declared_steps` and `STEP_HEADING` |
| `test_graded_files_returns_a_nontrivial_population` | `graded_files` |
| `test_a_restarted_addendum_sequence_is_ambiguous` | `ruling_shape_findings` |
| `test_the_four_live_alternate_spellings_resolve_to_their_ordinals` | `declared_rulings` |

Each new test module states its own repository root and reads files directly, so no test module
imports another and no helper moves to make a class whole.

No moved case can live in a library module: `suite.DECLARED_LIMITS` declares that discovery defines
the suite's population and excludes every other file shape
([ADR 0164](0164-the-suite-runs-through-one-module-that-accounts-for-every-discovered-test.md)
ruling 15), so a case outside a `test*.py` module stops running and nothing reports it.

`test_markdown_read.py` adds a case driving `markdown_targets` over the committed ADR records and
asserting a floor on destinations read, so the resolver's real-tree evidence no longer rests on a
skill-agreement gate. The synthetic cases stay, because the committed records hold none of the forms
they grade. The new case names its population where it reads it, on ADR 0165 ruling 2.

## Ruling 7. `test_run_record_claim` reads `paragraphs`

`test_run_record_claim.blocks` is deleted and its callers read `markdown_read.paragraphs`.
`docx_write.blocks` is unchanged.

## Rejected options

- **One module for all four.** It puts ADR vocabulary behind every link-resolver import and forces one
  limits object over two unrelated boundaries.
- **A third module for the step reader.** The reader has one consumer, so there is no second consumer
  set to separate.
- **A private substrate.** Callers other than the moved parsers would keep copies.
- **One exemption reader per module.** It publishes a duplicate across a module boundary.
- **Converging the publish gate.** See ruling 4.
- **A prose pointer in place of a real-tree case.** A pointer fails nothing when either side changes.
- **Moving the helpers a stay-behind case tests.** `declared_steps` and `graded_files` are skill
  vocabulary and population, `ruling_shape_findings` is an assertion, and `declared_rulings` walks a
  population the test module grades.
- **A new test module importing `test_skill_agreement`.** It rebuilds the inversion this record
  removes.

## What this does not reach

- Whether a resolving link points at the right section. Every reader here tests membership only.
- A citation written in code. `markdown_targets` masks code spans and fenced blocks as mentions; the
  step-citation and ruling-citation readers mask neither, and `ruling_ordinals` masks fenced blocks
  only.
- Paragraph splitting in `docx_write`, which has a different contract.
- A dependency assembled at run time, which the syntax-tree walk behind rulings 2 and 6 cannot see.
- Any change to what a moved parser returns. Only ruling 3 changes a gate's input, and ruling 5 renames
  a type and a field.

## What must not come out of this

- **Collapsed assertions.** Every assertion, ceiling and gate stays in the test module that holds it.
- **Converging the publish gate on this record.** Ruling 4 declares it.
- **A line count or coordinate table in prose.** Anchor on names; the ticket's line numbers moved twice
  while it was open.
