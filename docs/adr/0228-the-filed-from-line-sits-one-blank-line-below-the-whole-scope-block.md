# The Filed-from line sits one blank line below the whole scope block

[#1092](https://github.com/mshamblin5150-code/clinical-skills/issues/1092) was found in the tracker
sweep closing [#1078](https://github.com/mshamblin5150-code/clinical-skills/issues/1078)'s grilling,
after the publish hook refused #1089's first create.
[ADR 0169](0169-a-ticket-states-what-filed-it-on-an-append-only-line.md) ruling 3 puts the
**Filed-from line** at *"the first line after any record-level scope block"*, and the build read that
as the very next physical line. Grilled 2026-09-14 at `origin/main` `90b16be0`; freshness gate `FRESH`.
The clinician ruled every point below, one at a time, on that date. Nothing is built here; this is the
record the build reads.

Every verdict below was driven by the grilling session at `90b16be0`, not taken from the ticket's
sweep comments, which had recorded the same pair several times. Line numbers are deliberately not
cited; a builder resolves each symbol by name.

## Measured before ruling

### The only shape the grader accepts renders inside the quote

`tracker_filed_from.fixed_position_line` skips the first `SCOPE_PATTERNS` match and requires
`**Filed from:**` at that match's end. Each of the three patterns in `tracker_branch_scope`
(`BRANCH_SCOPE`, `MAIN_SCOPE`, `CITED_RECORD_SCOPE`) ends by consuming exactly one line break. Driving
`grade_publication` on route `("issue", "create")` over synthetic bodies opened by a rests-on-`main`
Branch state line:

| body after the scope line | grade | GitHub render (`gh api markdown`, `mode=gfm`) |
| --- | --- | --- |
| `**Filed from:**` on the next line | clean | inside `<blockquote>`, joined to the Branch state sentence by `<br>` |
| the same, CRLF endings | clean | not rendered |
| one blank line, then the label | deny | its own `<p>` below the quote |
| the same, CRLF endings | deny | not rendered |
| two blank lines, then the label | deny | not rendered |
| a bare `>` line, then the label | deny | its own `<p>` below the quote |
| a whitespace-only line, then the label | not driven | its own `<p>` below the quote |

*Had the patterns stopped short of the line break, the blank-line row would be the one graded clean.*
Markdown's lazy continuation joins an unmarked paragraph line to the blockquote above it, so the
accepted shape states the ticket's provenance as part of the claim about its base.
`tools/test_tracker_filed_from.py` and `tools/test_tracker_publish_hook.py` both pin the adjacent shape
as accepted, the first for all three scope forms and the second under a Cited record state.

### Open bodies carry both shapes

Population: every open issue, 50 by GitHub's GraphQL `totalCount` and 50 returned by
`gh issue list --state open`, so the unread remainder is 0. Matcher: `SCOPE_PATTERNS` for the scope
line, then `FILED_FROM` at the offset, one line break later, or two or more.

| shape | created after `FILED_FROM_CUTOFF` | before |
| --- | --- | --- |
| scope block, label on the next line | #1133, #1134, #1135, #1139, #1198 | #1058 |
| scope block, one blank line, label | none | #1064, #1066, #1069 |
| scope block continuing on further `>` lines, no label | none | #823 |
| no scope block, label first | 35 | #1065 |
| no scope block, no label | none | #87, #596, #773, #776 |

#823 opens with a Branch state line, a bare `>` line, and a dated correction of that Branch state inside
the same quote, which is where [ADR 0191](0191-a-carried-claim-is-corrected-where-it-stands-and-436-never-ruled-it.md)
ruling 3 puts a correction.

### The measurement declaration has the same exposure and no current instance

`tracker_measurements.grade` finds a declaration by `line.startswith(LABEL)` and ignores what precedes
it. A `**Measured at:**` line directly under a Branch state line grades with no finding against a
matching SHA and renders inside the quote; with one blank line above it, it also grades clean and
renders as its own paragraph. Population: the 50 open issue bodies above and the 227 files in
`docs/adr/`, comments not read. Matcher: a line starting with the label whose preceding line starts
with `>`. The open bodies hold no declaration; the ADRs hold 19, none preceded by a `>` line.
[ADR 0196](0196-a-published-figure-names-its-population-and-is-re-derived-at-publication.md) ruling 7
already says *"Riding inside the Branch state block is refused"*; no reader enforces that sentence.

## Ruled 2026-09-14

### 1. The label follows the scope block and exactly one blank line

The fixed position is the line after the scope block and one blank line. A label on the line directly
beneath the block is refused, and so is a label after two or more blank lines. A line holding only
spaces or tabs counts as the blank line, because Markdown reads it as one. With no scope block the
label is the body's first line, as ADR 0169 ruling 3 already says. This is still one exact offset and
no search, which is what ADR 0169 refuses free placement for.

The Filed-from line says what produced the ticket; the scope block says what base the ticket's claims
rest on. Only this shape renders them as two statements.

### 2. The scope block is the whole quote

The block runs from the recognized scope line through every line after it that begins with `>`, and
ends at the first line that does not. An unmarked line directly beneath the quote ends it, which is
exactly the shape ruling 1 refuses. A dated correction of the scope block written inside its quote,
as #823 carries, is part of the block, so the correction and the Filed-from line can both stand at
their required positions.

### 3. The retired adjacent position is read only to protect an existing line

On an issue edit, a line at the retired position in the **current** body, directly beneath the scope
line with no blank line, counts as the existing Filed-from line. The proposed body must carry that line
word for word at ruling 1's position; an edit that drops it, alters it, or leaves it adjacent is refused.
The tracker workflow's edit report reads `changes.body.from` the same way. An issue create accepts only
ruling 1's shape, and the retired position never satisfies a create or a proposed body.

The open-ticket harvest counts a post-cutoff body whose line sits at the retired position on its own
row, `line at the retired position`, separate from a missing line, and does not make it a finding.
ADR 0169 ruling 5 leaves an existing body alone until its next respec, and the created body passed
the grade that was in force when it was filed.

### 4. A measurement declaration directly under a quote line is refused

One shared check answers whether a line directly follows a line beginning with `>`. The measurements
reader applies it, and a `**Measured at:**` declaration in that place is a finding the publish hook
refuses, with the remedy of a blank line above it. It applies on every record that reader grades,
comments included, and on staged and committed ADRs. This enforces ADR 0196 ruling 7 rather than adding
to it.

The check is deliberately wider than the rendering: a label after a bare `>` line renders outside the
quote, as measured above, and is still refused, because the check reads the preceding line and not the
Markdown parse.

### 5. Recorded here, with ADR 0169 left as written

ADR 0169 ruling 3 keeps its text with a dated pointer beneath it, on the arrangement that record already
uses for the ruling 7 sentence ADR 0191 superseded.
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
keeps a ruling's deciding paragraph untouchable. `CONTEXT.md` defines **Scope block**, which four names
in the repository had described without a definition.

## Rejected options

- **Accept the adjacent shape and the blank-line shape both.** It makes two positions, and the accepted
  adjacent shape still renders provenance as part of the scope claim.
- **Keep the adjacent shape and document the rendering.** It records the defect instead of repairing it.
- **The first non-blank line after the scope block.** Still free of wording, but a small search where
  ADR 0169 required one offset.
- **The single recognized scope line as the block.** A correction of the block inside its own quote would
  leave the Filed-from line nowhere it could be placed.
- **No retired-position read.** Five post-cutoff tickets would read as missing their line, and their edits
  would lose append-only protection exactly where a line exists.
- **Allowing an edit to leave the line adjacent.** A ticket edited but never respecced would render the
  defect indefinitely.
- **Editing the six adjacent bodies now.** ADR 0169 ruling 5 refuses it.
- **Rewriting ADR 0169 ruling 3's sentence.** ADR 0016 refuses edits to a deciding paragraph.
- **Parser, documentation and tests with no record.** The refusal of a shape the build shipped, and a
  read that is not a second accepted position, would not survive without their reasons.
- **The measurement declaration filed as its own ticket, or declared as a limit.** The defect and the
  check are the same; two builds would write two copies of the predicate.

## Consequences

The build is one ticket, #1092:

- `tracker_filed_from.fixed_position_line` and the create grade read ruling 1's position after ruling
  2's block; the edit grade, the event report and the harvest add ruling 3's read and row.
- One predicate for a line directly following a `>` line, used by `tracker_filed_from` and
  `tracker_measurements`, and the new measurement finding kind wired through the publish hook.
- The refusal message names the ruled shape, so a writer can repair it without reading this record.
- Tests pinning accept and refuse for the adjacent, one-blank, two-blank, whitespace-blank, bare-`>` and
  CRLF variants under all three scope forms, a multi-line scope block, and each ruling 3 edit outcome.
  The two tests that pin the adjacent shape as accepted change with the parser.
- `docs/agents/issue-tracker.md` states the position with a literal example.

## What this does not reach

- **The six adjacent bodies.** They render inside their quotes until an edit moves the line.
- **Comments.** The Filed-from rule grades issue bodies only; a comment's layout under a scope block is
  not graded for this line.
- **Pull request bodies**, which keep their own binding grammar under ADR 0169 ruling 6.
- **Whether a quote above a declaration is a scope block.** Ruling 4's check reads any `>` line.
- **Whether the line is true**, unchanged from ADR 0169.

## What must not come out of this

**A search for the label.** The position stays one exact offset.

**Rewriting existing bodies to the new shape** outside their next respec.

**The retired position accepted on a create or in a proposed body.**
