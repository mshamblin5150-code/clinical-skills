# A refused reference label voids only its declared kinds, and a partial gate keeps what it read

[#1069](https://github.com/mshamblin5150-code/clinical-skills/issues/1069) found that
`discussion_post_scan`, `discussion_reply_scan` and `peer_critique_scan` disagree on what a refused
reference label does to a finding the run did grade. Grilled 2026-09-14 against `ac2fa385`; the
clinician ruled every point below on the same day. Nothing is built here; this is the record the build
reads.

## Measured before ruling

### The three graders compose precedence three ways

Read from each module's `grade` at `ac2fa385`:

| member | a finding computed beside a refused label counts when | computed and not counted |
| --- | --- | --- |
| `discussion_reply_scan` | its kind is `editor-readback` or a heading-read kind | `addressed-name`, the posted-reading kinds, `submission-fingerprint`: exit 2 |
| `discussion_post_scan` | its kind is in `submission_failed`'s set or is a heading-read kind | `missing-posted-reading`, `unknown-verdict`, `bare-verdict`, `unlocated-reading`, `borrowed-locator`: exit 2 |
| `peer_critique_scan` | its kind is in `structural_kinds`, which covers every kind its refused path computes | none: exit 1 |

Driven at `ac2fa385`: `test_a_refused_label_keeps_exit_two_when_the_addressed_name_also_fails` passes,
asserting exit 2 with `addressed-name: 1`, and
`test_a_render_finding_keeps_exit_one_when_the_reference_boundary_is_refused` passes, asserting exit 1
with `bold-headings: 1`. *Had the graders agreed, those two runs, each carrying one computed finding
outside the refused label's rows, would assert the same status; one asserts 2 and the other 1.* The
peer case was driven by #1069 at `c90f5c7`, exit 1; the post's posted-reading case was read and not
driven.

### Every refused path computes only kinds the label does not void

Under a refused label each module's `survey` returns early and assembles its findings from families
that never read the reference boundary: address, posted reading, editor readback, submission and
render carriers, and the heading read. `GATED_ROW_SETS["reference_boundary_graded"]` in the post and
reply modules names the kinds that do read it, and ADR 0080's gate walk binds their report lines to
that declaration. `peer_critique_scan` declares no gated row set; its report's `reference_rows` holds
the four kinds that read the boundary.

### ADR 0036's reason covers the voided kinds and nothing more

[ADR 0036](0036-a-references-label-is-a-per-pipeline-source-spelling-for-one-rendered-outcome.md)
ruling 2 exempted the refused label from the house precedence: *"the findings that would have
outranked the 2 are exactly the ones that could not be computed."* Three later changes each let one
more computed kind outrank it: #948's `editor-readback`, #1257's heading-read kinds, and #1260's
`submission-fingerprint`, which reached the post and the critique and not the reply.

### A render finding can exist when the engine is unavailable

`_rendered_page_findings` appends the record-count and last-verdict findings without the render
engine, and sets `engine_available` false only when reading a page image raises `EngineUnavailable`,
keeping what it already appended. Today such a finding counts through `submission_failed` while the
report prints `rendered-pages: not graded`. Read and not driven.

### ADR 0080 holds the forcing function and refused a shared status check

[ADR 0080](0080-a-gated-row-set-is-declared-per-gate-and-guarded-by-an-opt-in-walk-in-the-shared-conformance-kit.md)
ruling 2 names gated kinds positively so the report's inline exempt set, checked against the
declaration by the walk, forces a decision on every new kind. Its ruling 5 refused a shared status
assertion as *"a module-local ruling"* hoisted into shared code. `for_module`'s precedence case
replaces the member's `grade`, so it tests `run_grader.run`'s ordering and never a member's
composition.

## Ruled 2026-09-14

### 1. A refused reference label is a voiding gate

It suppresses only the kinds declared under it. Every other finding the run computed counts, so the
exit is 1, while the report still prints the voided rows as `not graded` and stderr still names the
refused label, because `run_grader.run` prints both before it returns. The three graders agree. This
supersedes ADR 0036 ruling 2's sentence *"The house rule that **1 wins over 2** does not apply"* for
any finding outside the declared kinds; its reason and the rest of that record stand. **Aligning the
three hand-kept lists was declined**: that is how #1260 reached two graders and not the third.
**Suppressing every finding was declined**: #948 and #1257 had already refused it for their kinds.

### 2. Each grader derives precedence from its own gated row set

A finding counts unless its kind is declared under a gate that is off and is not partial. This
replaces the reply's editor-readback and heading-read clauses, the post's `submission_failed` set,
and the critique's `structural_kinds`. `aar_scan.completion_gate` is not a gate and is untouched.
**Deciding in `run_grader` was declined**: it widens the shared runner for three members when most
members declare no gate.

### 3. A partial gate keeps what it read

A gate whose off state means a read stopped partway is partial. A finding it already produced counts,
and its row prints that count with the reason the read stopped, never a bare `not graded`. Each module
declares its partial gates by key in a `PARTIAL_GATES` tuple beside `GATED_ROW_SETS`.
`rendered_pages_graded` is the only one today; `reference_boundary_graded` and `html_graded` void.
**Voiding every off gate was declined**: it would swallow a non-clean render verdict that was read
without the engine. **Reading only the reference boundary was declined**: the next gate would fall
outside the derivation.

### 4. ADR 0080 stands, narrowed for a partial gate

- The report's inline exempt sets stay as ADR 0080 ruling 2's forcing function, and the walk keeps
  binding them to the declaration. `grade` reads that same declaration, so the exit and the report
  answer to one checked object.
- ADR 0080 ruling 5's assertion that every declared kind reads `not graded` with its gate off is
  narrowed: under a gate in `PARTIAL_GATES` the walk asserts the qualified count instead. Its refusal
  of a shared status assertion stands.
- The status check stays module-local. Each of the three test modules drives a refused label beside
  one computed finding outside the voided kinds and asserts exit 1.
  `test_a_refused_label_keeps_exit_two_when_the_addressed_name_also_fails` becomes that control for
  the reply, flipped deliberately.

**Superseding ADR 0080 rulings 2 and 5 was declined.** Deriving the report from the declaration would
leave the walk comparing an object with itself, and a new kind would default to printing a count
beside a row that never ran. **Superseding ruling 5 alone was declined**: the post's `docx_graded`
gate reaches exit 0 where the reference boundary reaches 2, so a shared status check would carry
per-gate outcomes.

### 5. `peer_critique_scan` declares its gate and opts in

It declares `GATED_ROW_SETS` with the four kinds its report calls `reference_rows` and the fields its
report prints as `not graded`, and its test module calls `gate_conformance` by name. ADR 0080 ruling 4
makes membership declared rather than discovered, and that record's declared limit names this case:
*"A module arriving with this shape and never calling the factory is invisible to the walk."*

## Taken as conventions, not ruled

- `CONTEXT.md` gains **Voiding gate** and **Partial gate**, and **Gated row set** names both.
- ADR 0036 and ADR 0080 are not edited. Whether a superseded record carries a marker is
  [#1201](https://github.com/mshamblin5150-code/clinical-skills/issues/1201)'s open decision, and
  ADR 0219 left its two targets unmarked on the same ground. Both targets here belong to that ticket's
  population.
- The partial row's exact wording is the build's.

## Consequences

- The three `grade` functions derive precedence per rulings 1 to 3; the post report's `rendered-pages`
  line prints a qualified count under an off partial gate.
- `grader_conformance`'s gate walk reads `PARTIAL_GATES`, and `CLAUDE.md`'s *Grader conformance*
  section stops saying that every omitted group reads `not graded`.
- Each test module gains the exit-1 control. Other tests asserting exit 2 beside a computed finding
  outside the voided kinds change deliberately; which ones is established by running the suite, not
  listed here.

## What this does not reach

**Whether a declared kind truly depends on the reference boundary.** The declaration is authored; the
walk proves the report honors it, not that it is right.

**[#1253](https://github.com/mshamblin5150-code/clinical-skills/issues/1253)'s retained-pass
comparison.** It is a different question in the same function and stays open.

**[#1066](https://github.com/mshamblin5150-code/clinical-skills/issues/1066)'s family-wide remainder
obligation.** Ruling 3 rules one gate in one family and is a precedent there, not an answer.
