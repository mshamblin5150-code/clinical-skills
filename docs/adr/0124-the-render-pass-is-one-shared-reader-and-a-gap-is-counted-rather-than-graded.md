# The render pass is one shared reader and a gap is counted rather than graded

[#833](https://github.com/mshamblin5150-code/clinical-skills/issues/833) was filed by an
architecture review of `tools/`, 2026-09-03, over a live divergence between two render producers:
`deck_render` numbers a pass `max + 1` and tolerates a gap, `discussion_post_render` refuses a
non-consecutive set, and `render_scan` grades exactly that property for the deck's own run
directory. Five decisions were declared open. It is the remainder of the mechanism
[ADR 0111](0111-the-word-export-route-names-its-invocation-mechanism-and-the-hanging-methods-are-a-declared-list.md)
ruling 5 split three ways, asked about the pass the export lands in rather than about the export
call.

Grilled 2026-09-03. **Five decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## Measured before ruling, at `e61d96f`

Freshness gate `FRESH` at both checkpoints. Every figure below is re-derived by reading the four
modules end to end at that base.

### The ticket's table has two producers; there are four sites and three postures

| site | role | what a gap does |
| --- | --- | --- |
| `deck_render._next_pass` (`deck_render.py:28-35`) | deck producer | tolerates it, `max(numbers, default=0) + 1` |
| `discussion_post_render._next_pass` (`discussion_post_render.py:40-48`) | post producer | raises `RenderError` |
| `render_scan._pass_history_is_canonical` (`render_scan.py:115-120,204`) | deck and case-study grader | exit **2**, `NONCANONICAL_PASSES` |
| `discussion_post_scan._render_passes` (`discussion_post_scan.py:552-581`) | post grader | appends a fabricated empty `RenderPass`, so `rendered-pages` fails at exit **1** |

**The fourth is in no row of the ticket.** It is a fourth answer to what numbers a render pass, and
it is the site the ticket's *no third implementation* bullet is aimed at, already shipped.

### `render_scan` does not read both producers' output

Grepping every consumer, it is invoked from `skills/course-assignment/SKILL.md` and
`skills/practicum-case-study/SKILL.md` and from nowhere else. The post has its own grader. The real
pairings are **deck** → `deck_render` + `render_scan`, divergent; **post** →
`discussion_post_render` + `discussion_post_scan`, agreeing a gap is bad and disagreeing how loud;
**case study** → no producer + `render_scan`, which is
[#803](https://github.com/mshamblin5150-code/clinical-skills/issues/803)'s subject.

### The deck divergence is quieter than the ticket implies, and backwards

`NONCANONICAL_PASSES` is a coverage limb, and a measured finding outranks a limb. So a deck run
with a gap **and** a short final pass exits 1 with the limb invisible, while the same run with a
**complete** final pass exits 2. The check refuses hardest when the run is most correct.

### A third divergence nobody had named: the pass-directory name grammar

| site | `pass-01` | `pass-²` |
| --- | --- | --- |
| `deck_render`, `suffix.isdigit()` | accepted as 1 | `'²'.isdigit()` is `True` and `int('²')` raises — **the producer crashes** |
| `discussion_post_render`, `discussion_post_scan`, `\d+` | accepted as 1 | ignored |
| `render_scan`, `\d+` **plus** `path.name == f"pass-{number}"` | **refused as noncanonical** | ignored |

Four sites, three grammars, none of them chosen. `pass-01` is a directory no producer writes, so it
can arrive only by hand — which is exactly the population the whole gap question is about.

### The pass has a second grammar: the filenames inside it

| | export | images |
| --- | --- | --- |
| `deck_render` writes | `deck.pdf` | `slide-N.png` |
| `discussion_post_render` writes | `post.pdf` / `post.xps` | `page-N.png` |
| `render_scan` reads | any one `*.pdf`/`*.xps` | any `*.png` |
| `discussion_post_scan` reads | **`post.pdf`/`post.xps` only** | `page-N.png` |

`render_scan` grades both artifacts by accident of being the tolerant one. `discussion_post_scan`
pointed at a deck pass reports *keeps no retained export* about a directory holding one. Neither
name is written down anywhere as the rule, and #803's missing producer would invent a third with
nothing to constrain it.

### The four rows are not equally shareable

**Staging and retention** differ only by one-sided defects. `deck_render` computes its destination
number **after** the render and guards its cleanup — `_discard_building` refuses to `rmtree`
anything not named `.building-` under the render root. `discussion_post_render` computes the number
**before**, welds that stale number into the staging prefix, and cleans with an unguarded
`shutil.rmtree` in a `finally`.

**The page-count check differs in kind.** `deck_render` counts `ppt/slides/slideN.xml` in the
`.pptx` archive for its denominator; the `.docx` archive states no page count at all, which
[ADR 0098](0098-the-case-study-s-rendered-document-coverage-is-derived-from-kept-evidence-and-owned-by-its-own-run-directory-grader.md)
ruling 1 measures and `CONTEXT.md`'s **Render pass** entry records, so
`discussion_post_render` takes an optional `--expected-pages` instead. Only the *images cover the
exported pages* half is one question in both.

### `deck_scan` names render nowhere, and it runs before the render exists

`skills/course-assignment/SKILL.md` step 5 opens **"Run the retained render pass after the package
scan."** ADR 0098 ruling 3's refusal of `case_study_scan` — *its subject is the draft body's house
style, it opens no run evidence, and it runs before the render exists* — is true of `deck_scan`
clause by clause.

## Ruled 2026-09-03

### 1. A gap is counted and printed on every run, never graded, and both producers take `max + 1`

`render_scan` and `discussion_post_scan` report the number of missing pass numbers on every run and
neither changes its exit status for one. `NONCANONICAL_PASSES` leaves `EXIT_2_LIMBS`;
`discussion_post_scan`'s fabricated empty `RenderPass` at `:581` is deleted.

**Exit 2 was refused because the sentence it prints is false of the situation.** That limb means
*the evidence needed to measure coverage was unavailable*, and the evidence for the only row
`render_scan` grades — final-pass coverage — is present in a run whose last pass holds its export
and every image. Nothing either grader reports depends on the history: `render_scan`'s own docstring
already says earlier passes may be incomplete and are reported rather than failed, so an earlier
pass carries no evidentiary obligation and deleting one destroys no figure. The limb is filed under
a heading that lies, and the measurement above shows it already fires only when the run is otherwise
clean.

**Silence was refused too.** Every pass directory is written by a producer that only ever creates
the next number, so a hole is evidence that something outside the producers wrote in the render
root. That is worth one line.

**A graded row was refused, and it is the closest call in this record.** The remedy for a gap is
renaming a directory, not re-rendering, and a finding whose remedy is housekeeping is the kind a
reader learns to skim. Counted and never graded is the arrangement `block_scan` uses for its wrap
count and `case_study_scan` for the em dash. **What would reverse this is one fact**: if deleting a
pass directory is ever part of normal work the count is right, and if a gap can only ever mean
something went wrong then a row is the better call. The clinician ruled that it is not part of
normal work in the sense that matters — a hand-deleted pass is a housekeeping act, not a defect in
the submission — and the count stands.

**The producer never blocks on the history.** Refusing puts a hard stop on the critical path over a
property the producer does not need to know: delete a junk `pass-2`, fix the deck, and the post
producer's rule blocks the re-render. A producer's only pass-numbering obligation is never to
overwrite retained evidence, and `max + 1` discharges it under every history the consecutive rule
raises on.

**The obvious minimal edit is destructive and the build must not make it.**
`discussion_post_render._next_pass` returns `len(numbers) + 1`, not `max + 1`. Those agree only on a
consecutive set, which is why its raise is load-bearing for its own implementation: deleting the
raise alone leaves `{1, 3}` returning **3**, so the staged directory is renamed onto an occupied
number. The rule is `max + 1`, adopted whole.

### 2. The pass joins a shared helper, in three rows and not four

Shared: the **directory name grammar**, `max + 1` **numbering**, the **gap count**, the
**staged-then-renamed retention**, and the **images cover the exported pages** check. Sharing takes
the better half of each producer — deck's after-the-render numbering, which is the ordering `max + 1`
wants, and deck's guarded cleanup.

**The grammar is `pass-` followed by ASCII decimal digits with no leading zero**, so `pass-01`, `pass-0` and `pass-²` are not pass directories at all. That is exactly what both producers write, it makes a directory name a function of its number so `render_scan`'s separate `path.name == f"pass-{number}"` check folds into the grammar rather than being deleted, and it forbids the one shape that would make `max + 1` and the gap count disagree — two directories mapping to one number. It also retires `deck_render`'s `isdigit()` crash. This is the grammar the shared reader defines rather than a separate ruling; it is written here so the choice is not made silently in a build.

**The source-page-count comparison is not shared.** A `.pptx` states its slide count and a `.docx`
states nothing, so imposing one denominator would force on the post a figure that does not exist.
The rasterize loop is a vendor seam and stays filed separately.

**This is `repo_root.py`'s test passing rather than #253's refusal.**
[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253) refused extracting the two
ledgers' copied field parser because their populations genuinely differ and the copy existed to
permit divergence. Here the layout is a wire format a third and fourth module read, the population
is the one `render/` directory, and every divergence found is one side being wrong.

### 3. Both graders read the shared reader, and it is a function rather than a constant

`render_scan` and `discussion_post_scan` both import it. **`discussion_post_scan` is included by
name**, because it is the site the ticket omits and leaving it out fixes three sites and leaves the
fourth holding a fourth grammar.

**A function, because sharing an object is necessary and not sufficient.**
[#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218) is the recorded
counter-instance: `reference_scan` was made to import `docx_write.REFERENCE_HEADING`, an identity
test asserted the two were the same object and passed, and a behavioral test then found the two
implementations still disagreed about where a reference list ended. Exporting a regex would let a
grader import the grammar and hold its own idea of what a hole is. The seam is a reader returning
the parsed, sorted passes, with the producers' numbering and the graders' gap count both built on
it.

**The filenames inside a pass stay each producer's business, behind a globbed shape** — exactly one
`.pdf` or `.xps`, and `*.png` for the images. `render_scan` already grades both artifacts that way
and it works, so uniform names buy nothing a glob does not have, while imposing them is a
wire-format change that invalidates retained evidence already on disk. What must be shared is the
directory grammar, because the numbering and the gap count are computed from it; an export's
filename is computed from nothing. This closes `discussion_post_scan`'s hard-coded `post.pdf` and
gives #803's producer a rule to land inside.

**The cost is named.** Globbing means a pass holding a stray second PDF reads as malformed rather
than as the intended one plus junk. `render_scan` already refuses that shape at `render_scan.py:126-127`, so it is
the existing posture and not a new one.

### 4. `deck_scan` gains no render row, and the placement divergence is declared and filed

ADR 0098 ruling 3's refusal applies to `deck_scan` clause by clause, as measured above. A render
row would fail every correct run at the moment step 5 says to run it, and it would grade the deck's
render coverage twice — the third-implementation cost this ticket exists to price.

**What naming the split as correct exposes is not this ticket's to fix.** The post grades its render
coverage *inside* its package grader, gated on `--docx` and printing `not graded` without it, while
the deck and the case study use a separate command. Two artifacts, two architectures, and no
artifact-shaped reason for the difference — `discussion_post_scan` solved with a gate the very thing
ADR 0098 refused to build for the case study. Resolving it means moving the post's row out to
`render_scan` and deleting a working gate, which is larger than the pass. After ruling 3 both
arrangements read one shared pass reader, so the divergence is now only about **which command holds
the row** and never about what a pass is. It is declared here and filed as its own ticket.

### 5. #803's decision 1 is untouched

The shared helper gives #803's missing case-study producer a home for numbering, staging, retention
and the image-coverage check. It decides nothing about **where that producer lives**. #803's
decision 1 stays open and this record must not be read as answering it.

## What this does not reach

**Whether a gap means anything.** The count says a directory the producers would never create is
present. It does not say who removed the pass, whether the reader had already read it, or whether
the run's own record claims more passes than survive. Nothing checks the last of those and this
record does not build it.

**Whether the retained images are the pages a reader read.** Unchanged from ADR 0098 ruling 3 and
from `render_scan`'s own docstring: `checks_ledger` grades the substantiated verdict and this
mechanism grades coverage, and a clean run of both is not a checked render.

**Whether one export is the right export.** The globbed shape establishes that a pass keeps exactly
one page-faithful export. It cannot establish that the export is of the artifact that was submitted.

**Any part of ADR 0111 ruling 5.** Process ownership stays shared, the export bound stays a
parameter of the shared helper, and the Word method list stays unshared, for the reasons given
there.

**The rasterize loop.** Both producers keep their own `pymupdf` loop; it is a vendor seam filed as
its own ticket and no ruling here touches it.

**ADR 0116 ruling 1's read-failure posture.** A gap is not a read failure — the directory reads
fine — so the role-keyed posture does not bind this ruling, and `render_scan`'s retained-export
read stays the already-correct instance ADR 0116 names.
