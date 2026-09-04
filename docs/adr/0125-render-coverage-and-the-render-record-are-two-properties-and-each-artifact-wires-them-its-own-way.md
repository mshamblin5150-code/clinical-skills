# Render coverage and the render record are two properties and each artifact wires them its own way

[#864](https://github.com/mshamblin5150-code/clinical-skills/issues/864) was filed out of
[#833](https://github.com/mshamblin5150-code/clinical-skills/issues/833)'s grilling, 2026-09-03, and
declared rather than fixed there:
[ADR 0124](0124-the-render-pass-is-one-shared-reader-and-a-gap-is-counted-rather-than-graded.md)
ruling 4 named the placement divergence — the post grades its render coverage inside its package
grader behind a `--docx` gate, the deck and the case study use the separate `render_scan` command —
and filed it as larger than that pass.

Grilled 2026-09-03. **Four decisions, ruled by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## Measured before ruling, at `e3defa1`

Freshness gate `FRESH` at both checkpoints. Every figure below is re-derived by reading the modules
and the three skills end to end at that base. **All three of the ticket's premises are false as
written**, and the third is not merely false but inverted.

### The two rows are not the same property

`render_scan.ROWS` holds one row, `final-page-coverage`, and `survey` fires it on one condition: the
**final** pass has a measurable `exported_pages` and keeps fewer page images than that
(`render_scan.py:214-225`). Earlier passes are counted into `incomplete_earlier_passes` and never
failed.

`discussion_post_scan`'s `rendered-pages` grades that comparison and, before reaching it, a second
property entirely — the `## RENDERED:` record in the run's `post.md` against the evidence on disk
(`discussion_post_scan.py:726-800`). It fires when no `RENDERED` record exists at all, when the
record count and the retained pass directories disagree, when a record names an artifact other than
`post.md`, when a `PAGES` count is not positive, when the pixels on disk do not match the
self-reported count, when the images are not named consecutively from `page-1.png`, when an image
does not decode, and when a pass keeps other than exactly one export. It applies those to **every**
pass; only the pixels-against-exported-pages comparison is gated on `is_last`.

So the post's row is the `render_scan` row *plus* the case study's `checks_ledger` row's subject,
welded together. ADR 0124 ruling 4's *"nothing is measured differently; the same property is graded
from two places"* is not what the tree holds, and the divergence was never only about which command
holds a row.

**The status vocabularies also diverge on the same evidence.** An unreadable retained export and a
non-canonical pass sequence are `render_scan` **exit 2** coverage limbs; the equivalent conditions in
`discussion_post_scan` are exit **1** findings. One command says *coverage could not be measured*
where the other says *coverage is short*.

### There are three arrangements, not two

| artifact | coverage | the record | joined by |
| --- | --- | --- | --- |
| post | `discussion_post_scan.rendered-pages` | the same row | one command |
| case study | `render_scan.final-page-coverage` | `checks_ledger`'s `the rendered document`, also in `SUBSTANTIATED_CLEAN` | prose |
| deck | `render_scan.final-page-coverage` | **nothing** | — |

`skills/course-assignment/SKILL.md` names `checks_ledger` nowhere, `deck_scan.ROWS` is `slide-count`,
`bullets-per-slide`, `words-per-bullet`, `font-points` and `untraced-costed-figure` with no render
row, and `deck_scan` takes no `--submission`. The deck therefore has render coverage and no record
half of any kind, which is a third posture and not an instance of either named one.

### The ticket's decision 3 is inverted

#864 asks what the `--docx` gate costs that a separate command does not, and asserts that
*"`render_scan` invoked separately cannot be skipped without leaving a command row unrun."* **Nothing
leaves a row unrun.** `checks_ledger.EXPECTED_CHECKS` holds no row naming `render_scan`, and
`checks_ledger` opens no directory at all — `the rendered document` is a reader's record, satisfied
by writing the record, and that grader's own declared limit says a well-formed verdict cannot prove
its reader opened anything. What ties the command to the ledger is one sentence at
`skills/practicum-case-study/SKILL.md:1061` and one by-eye checklist line at `:1347`, neither of
which fails a run. For the deck there is not even that.

So the gated arrangement is the **stronger** one on the axis the ticket assumed it was weaker: the
post's row fails when the `RENDERED` records and the retained pass directories disagree, so a run
that skipped the renderer is caught by the artifact it did not produce. The separate command catches
a skipped render only if somebody runs it, and nothing does.

### The post's real hole is narrower than the ticket's, and it is a wrong gate key

`rendered-pages` is gated on `--docx` and reads no part of the `.docx`. `_rendered_page_findings`
returns `()` on `source.docx is None` (`discussion_post_scan.py:726-728`), and `load` does not open
`render/` at all without the flag (`:657`). Its two gate-siblings, `bold-headings` and
`rendered-comments`, do read the document; this one reads `render/pass-N/` and `post.md`.

The gate is nonetheless load-bearing rather than gratuitous: `skills/discussion-post/SKILL.md:262`
runs the grader with `--draft` alone, before the render exists, so an ungated row would fail every
correct pre-render pass — which is
[ADR 0098](0098-the-case-study-s-rendered-document-coverage-is-derived-from-kept-evidence-and-owned-by-its-own-run-directory-grader.md)
ruling 3's refusal arriving on the post. What it cannot survive is the terminal invocation: `:396`
reruns the grader with `--submission <stem>` and carries `--docx` in prose only, so omitting one flag
prints `rendered-pages: not graded` and exits 0 over a run that never rendered.

## Ruled 2026-09-03

### 1. The post's row does not move, and the divergence is not a defect

The only stated reason to move it is falsified above. Moving it would also split a row that grades
two properties into a command that grades one, and the post has no `checks_ledger` to receive the
record half, so that half would need a second new mechanism built for it.

**Uniformity was refused because it costs the post its join.** The post holds the record and the
evidence in one command, so the two cannot be satisfied independently; the case study holds them in
two commands joined by prose, and the measurement above is what that costs. Making the post look
like the case study would move it toward the weaker arrangement in order to make a table tidy.

**Retiring `render_scan` into the package graders was refused for the third time**, by ADR 0098
ruling 3 and ADR 0124 ruling 4 before this record. Nothing measured here disturbs either.

**What is ruled is the placement and not the strength.** Both arrangements are legitimate homes for
the row; neither is measured here as adequate. The three defects below are what the measurement
found, and not one of them is a placement question.

### 2. The split is declared in this record and pointed at from both graders

The pointer lands where each grader already declares what it does not reach, names this record and
copies no part of it, and is bound by a test asserting both name it. For the post that is
`discussion_post_scan.DECLARED_LIMITS`. For `render_scan` it is the module docstring, because that
module has no limits object at all. One authority, two pointers —
[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s repair, adopted because
the reader who is misled is standing in a module rather than in `docs/adr/`.

**Creating a limits object for `render_scan` to hold the pointer was refused, on a ruling rather
than on cost.** [ADR 0093](0093-the-tracker-gate-section-population-is-derived-from-three-sources-and-a-ratified-limit-is-lifted-into-the-module-it-governs.md)
ruling 4 states that a section does not oblige a limits object and that `refusal_scan` earned one on
a measurement. Bolting one on here to give a pointer somewhere tidy to sit decides by habit the thing
that record says is decided by measurement, and it widens a ticket whose other two findings were
deliberately filed rather than built.

**The asymmetry is declared rather than smoothed.** `render_scan`'s two limits are stated in its
module docstring and again in `CLAUDE.md`'s **Render scan** section, with nothing binding the two
copies — [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape. Whether
that module earns a limits object is a separate question, it needs its own measurement, and it is
filed under ruling 3.

**This record alone was refused** because it is what ADR 0124 ruling 4 already did, and #864 exists
because a reader of either grader finds nothing there.

**A shared constant in #833's pass reader was refused.** It would be one copy with no drift possible,
and it waits on #833 and parks an architecture sentence inside a module whose subject is a directory
grammar. ADR 0124 ruling 3 was explicit that the shared seam is a reader returning parsed passes; a
declaration is not a pass.

**`CONTEXT.md` was refused for the wiring and taken for the vocabulary.** Which command holds a row is
implementation and the glossary is not a place for it. But the measurement found the tree had never
named the distinction the wiring is a wiring *of*, which is why ADR 0124 could write *nothing is
measured differently* without anything contradicting it. `CONTEXT.md` gains **render record** as a
term beside **render pass**, defining the reader's claim joined to the retained evidence and holding
it apart from coverage, which is what a page count establishes. No module is named.

### 3. The three defects the measurement found are new tickets, not this one

**The post's gate key.** `rendered-pages` is gated on an input it does not read, and the flag is
optional at the invocation that decides completion. Two repairs are priced and neither is ruled here:
re-gate on the evidence, grading when the run holds a `render/` directory or a `RENDERED:` record and
reporting not graded when it holds neither, which closes flag-omission and leaves *never rendered*
reading as not graded; or require the row at `--submission`, not graded on the drafting and rendered
passes and refusing at the terminal one, which is `aar_scan.completion_gate`'s shipped shape in the
same module — `grade` already calls it at `discussion_post_scan.py:1085` — closes *never rendered*,
and presupposes the decoupling.

**`render_scan`'s reachability.** Skipping it produces no signal in either skill that runs it, and
the deck has no record half to notice the absence.

**`render_scan`'s unbound limits.** Its two declared limits live in the module docstring and in
`CLAUDE.md` and neither copy fails when the other is edited. The question is whether the module earns
a limits object on ADR 0093 ruling 4's terms, and it is not answered here.

**Ruling them here was refused** because it turns #864 into a build ticket about
`discussion_post_scan`'s gate and `render_scan`'s reachability, which is not the divergence it was
filed over, and both repairs land after #833's shared reader in any case. **Declaring the gate and
building nothing was refused specifically**: it is already declared, at `discussion_post_scan.py:166-170`
as an `EvidenceDisposition.BEHAVIOR` limit, and the declaration is exactly what let it sit until a
measurement went looking.

### 4. ADR 0124 ruling 4's two false fact sentences are corrected in place

[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
permits a ratified record's **facts** to be corrected in place behind a dated line while the
paragraph that does the deciding stays untouchable, and
[ADR 0022](0022-an-adr-carries-no-status-field-because-no-record-waits-on-main-for-a-decision.md)
applied it to a fact clause sitting inside a `## What is ruled` heading, so location does not decide
it. Ruling 4's decision — `deck_scan` gains no render row, the divergence is declared and filed — is
untouched.

Corrected: *"the divergence is now only about which command holds the row and never about what a pass
is"*, false independently of #833's build because ruling 3 shares the pass **reader** and not the row
set; and *"Two artifacts, two architectures"*, which is three.

**[ADR 0014](0014-a-run-is-keyed-to-the-graded-artifact.md)'s forward-pointer arrangement was
refused.** That one is for a collision unknowable on the day the earlier record was ruled, and ADR
0022 drew the line explicitly. ADR 0124 read all four render sites in detail at `e61d96f` and did not
compare what their rows grade; the comparison was available to it.

## What this does not reach

**Whether either arrangement is adequate.** Ruling 1 settles which command holds the row and says
nothing about whether the row is reachable, which is decision 3's finding and is filed.

**Whether a declaration is read.** The pointer rows make the split findable from the modules; nothing
makes a reader open them, and no test can assert that the sentence a pointer names is still true of
the tree it describes.

**Whether the retained images are the pages a reader read.** Unchanged from ADR 0098 ruling 3 and ADR
0124: `checks_ledger` grades the substantiated verdict for the case study, the `RENDERED` record does
for the post, the deck has neither, and a clean run of any of them is not a checked render.

**Anything in ADR 0124's rulings 1, 2, 3 or 5.** The shared pass reader, `max + 1`, the counted-not-
graded gap, *no row in `deck_scan`* and #803's untouched decision 1 all stand.
