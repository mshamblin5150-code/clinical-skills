# The PDF engine is reached through one seam, the page questions are four, and the availability verdict is the caller's role

Found while grilling [#837](https://github.com/mshamblin5150-code/clinical-skills/issues/837),
2026-09-09, at `origin/main` `bf79efd`, freshness gate `FRESH` at both checkpoints. **Ruled by the
clinician on that date.** Nothing is built here; this is the record the build reads.

The ticket's finding is that each site holds *its own open, its own iteration, its own close and its
own answer to* not installed *and* unreadable. Its 2026-09-03 comment narrowed that against
[ADR 0116](0116-the-read-failure-posture-is-keyed-on-the-input-s-role-and-only-the-crash-is-ruled-family-wide.md)
ruling 1, which keys the **unreadable** verdict on the input's role. Everything below either
extends that narrowing or is measured against it.

## Measured before ruling, at `bf79efd`

Every figure was re-derived by running the code rather than by reading it, and four of the
measurements move a claim the ticket or its own thread carries.

**The importer population is nine over a denominator of 86**, not the title's eight: 198 files in
`tools/`, 112 of them tests, 14 import statements across the nine. The ninth,
`tools/case_study_render.py`, is this ticket's own 2026-09-06 forecast collecting.

**The ticket's matcher misses a consumer it was never going to match.** Fourteen non-test modules
*name* the engine and nine import it. `discussion_artifact` takes it as a parameter; `docx_read`,
`docx_write` and `run_grader` name it in prose refusing it; and **`guidelines_build` consumes it by
distribution string** -- `importlib.metadata.version("PyMuPDF")` at `:141` and `:176` -- hashing the
result into the content-addressed build identity and answering *not installed* with `"unavailable"`.
That is a tenth dependence expressed in a form `grep -c 'import pymupdf'` cannot see. The body
declares its matcher a floor; this is what the floor missed.

**`guidelines_recs` exits 1 with an uncaught traceback when the engine is absent.** Driven with a
`meta_path` finder refusing the import:

```
tools/guidelines_recs.py, line 1275, in extract
    import pymupdf
ImportError: No module named 'pymupdf'
```

It carries **zero** `ImportError` handlers and never calls `require_pymupdf`, in a module that
otherwise returns 2 for *not a file*, 2 for `DidNotScan`, and 2 for zero recommendations with an
explicit *which is not the same as this document having no recommendations*. `guidelines_build.py:655`
reaches it through `build_sweep` catching only `DidNotScan`. This is
[#150](https://github.com/mshamblin5150-code/clinical-skills/issues/150)'s shape -- a dead process
presenting in the status reserved for a real finding -- which ADR 0116 ruling 3 rules family wide for
the grader family. `guidelines_recs` is not in that family; the shape is the same and the module is
the recorded instance of what an undeclared role produces.

**Seven answers to *not installed* across the nine**, all verified:

| module | answer | status |
| --- | --- | --- |
| `guidelines_extract` | `require_pymupdf()` raising `SystemExit(message)` | 1 |
| `split_census` | the same call, caught at `:309` and converted | 2 |
| `threshold_sheet` | caught, non-failing `SKIPPED` with a banner surviving `--quiet` | gate result |
| `guidelines_recs` | nothing | 1, uncaught |
| `case_study_render`, `discussion_post_render` | `RenderError("pymupdf is not installed")` | 2 |
| `deck_render` | `RenderError("PyMuPDF is unavailable")` | 2 |
| `render_scan` | a truthy return string reading as zero readable pages | 2 |
| `discussion_post_scan` | `pymupdf = None`, appended to a graded finding; ruling 9 changes this | 1 as a finding |

**One check already has two verdicts, which is the existence proof ruling 2 rests on.** Driven:
`require_pymupdf()` exits **1** from `guidelines_extract` and **2** from `split_census`, from the
identical call, because the second catches and converts.

**And three answers to *is the engine available* live in one process.** With the import blocked and
distribution metadata untouched:

```
guidelines_build._package_version("PyMuPDF")  -> '1.27.2.3'                  the cache key
guidelines_extract._engine_version()          -> 'pymupdf (not installed)'   the manifest's engine field
require_pymupdf()                             -> refuses
```

Two of those are written into the same build artifact and contradict each other. It is **latent
rather than live**: the build refuses before any artifact registers, and on this installation
`pymupdf.__version__` and `importlib.metadata.version("PyMuPDF")` agree at `1.27.2.3`. What is
measured is that they answer different questions and one of them feeds a content-addressed key.

**The two image probes disagree on a real file.** A one-page PDF copied to `page-1.png`:
`render_scan._pixel_read_error` returns `''` -- clean -- and `discussion_artifact.png_read_error`
returns `'does not carry a PNG signature'`. Same file, two graders, opposite verdicts.

**The four `120`s are two unrelated numbers.** A page rasterized at 300 probes clean at `dpi=1`, and
the probe's pixmap is `992x1404` at probe 120 whether the PNG was produced at 72, 120 or 300. Two of
the four are a reading resolution (`case_study_render.RASTER_DPI`, `deck_render.RASTER_DPI`); two are
a decode-probe argument (`png_read_error`, `render_scan._pixel_read_error` as a bare literal); and
`discussion_artifact.RENDERED_RASTER_DPI` is **one constant doing both jobs**, re-exported into
`discussion_post_render` as its production resolution. At `dpi=1` the probe allocates `9x12` rather
than `992x1404`, once per retained page image, in two graders.

**Both probes accept a 60-byte truncation.** Every truncation from 100 bytes up is caught by both
with `premature end of data in png image`; at 60 bytes the first eight bytes are a valid PNG
signature, PyMuPDF opens the stub as one page and pixmaps it, and both return clean.

**The rasterize loop is a hole in the middle of a shared pipeline.** All three producers export
through `office_process.run_owned_process` and retain through `render_pass.retain_staged_pass`; only
the step between them is written three ways. `render_pass` touches the engine nowhere.

**The text seam the ticket asks for already exists as a parameter.**
`guidelines_extract.rendered_operator_map(raw, render_glyph)` at `:623` takes an injected renderer,
written so the pure code never touches the engine. `rendered_operator_map_for_page(page, raw)` at
`:1576` is that parameter filled in, and it is the one function taking a live page. It is called from
`guidelines_recs:1004`, `split_census:166` and `threshold_sheet:1840`.

**In all five text sites the `open` call sits outside the `try` that guards the page loop** --
`guidelines_extract:1613`, `split_census:162` and `:198`, `guidelines_recs:1278`,
`threshold_sheet:1836` -- so an unopenable PDF escapes every local handler; `threshold_sheet` handles
*absent* and *unreadable page* and lets *unopenable* fly past its caller at `:3356`. And
`extract_pages` closes with a bare `document.close()` at `:1638` rather than a `finally`, so a raising
page iteration leaks the handle.

**`discussion_artifact` is not a discussion module and the probe is a lodger in it.** Six non-test
importers span case-study, deck, discussion-post, discussion-reply and reference grading, and every
one takes citation or prose syntax -- `read_citations`, `CLAIM_BLOCK`, `LEGAL_CITATION`,
`REFERENCE_YEAR`. Its docstring: *the module owns syntax both graders consume and the reference-aware
citation boundary they share.* `png_read_error` is the only function in its 939 lines that opens a
binary file or names the engine.

**The counts are dated and are deliberately restated nowhere else**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. They move the day a
producer lands or a corpus reader is extracted.

## Ruled 2026-09-09

### 1. The seam is keyed on the question asked of a page, and there are four questions

Not on the engine, which would be one adapter the ticket forbids, and not on the ticket's two halves,
which the measurement splits differently in both directions. The four are: **rasterize an export to
one image per page**; **is this retained file one readable page image**; **read a page's glyphs**;
and **how many pages does this export have**.

**Two become new modules and two do not.** The page-count question is one line inside the raster
module and inside `render_scan`; it earns a function, not a seam. The image probe already has an
implementation worth keeping and gains a home rather than a module (ruling 5).

**The ground is that the ticket's pixels half is not one question and its text half's adapter partly
existed.** The rasterize loop has three producers and sits between two modules the same three callers
already share; the probe has two consumers that disagree on a real file; and the two do not share so
much as a constant. On the other side, `rendered_operator_map`'s injected renderer was the seam and
`rendered_operator_map_for_page` was it filled in the wrong place.

### 2. Engine availability is one detection with a role-keyed verdict, and `require_pymupdf` is retired

The ticket's 2026-09-03 comment holds that *one decision rather than one per module still holds for
the not-installed axis, which is genuinely one policy across all eight.* **That does not survive
measurement, and it fails to that comment's own argument one axis over.**

`threshold_sheet`'s non-failing `SKIPPED` is a correct **optional secondary** posture under ADR 0116
ruling 1, and so is `discussion_post_scan`'s rendered-pages row -- whose graded finding on a missing
engine is not that posture, which ruling 9 corrects; the producers' and `guidelines_extract`'s
hard stop is a correct **primary source** posture. One verdict across the population would overwrite a
ruled distinction, which is exactly why that comment kept *unreadable* out of the adapter.

**What is one decision is the detection and the remedy sentence, not the status.** The seam raises one
typed absence carrying the sentence; every caller converts it at its own boundary under a declared
role. `require_pymupdf` is retired into that: it is the same detection with a verdict welded on, and
`split_census.py:309` is a module unwelding it by hand.

**The same applies to a failed open.** ADR 0116 ruling 1 governs the unreadable axis already, so the
seam raises one typed read failure and callers convert. That closes the outside-the-`try` open in all
five text sites and the leaked handle in `extract_pages` by construction rather than by five repairs.

### 3. The page-text unit is a document held open, and the live page crosses as a callable

The ticket's decision 2 worries that *an interface that has to expose all three is not obviously
deeper than what exists.* It does not have to. Only one of the five readings needs a live page.

```
page_text.open_document(path)     -> context manager, DocumentRead
page_text.read_page(path, number) -> PageRead

DocumentRead:  .title  .page_count  .pages()  .page(n)
PageRead:      .number  .rawdict  .render_glyph(bbox)  .plain_text()  .tables()
```

**No engine object is ever returned.** `render_glyph(bbox) -> (samples, width, height)` is precisely
the parameter `rendered_operator_map` was declared to take, so the three foreign call sites become
`guidelines_extract.rendered_operator_map(page.rawdict, page.render_glyph)` and
**`rendered_operator_map_for_page` is deleted rather than moved**. `RenderedOperatorKey`,
`SYMBOL_FONT_OPERATORS`, `font_key`, `rebuild_text`, `walk_line_glyphs` and `symbol_glyph_census` stay
in `guidelines_extract` untouched, with no cycle in either direction -- which is why the operator
classifier could not move: it needs `font_key` and `RenderedOperatorKey` back, and
`threshold_sheet.py:459` consumes `SYMBOL_FONT_OPERATORS` independently.

**One helper stops the two-step being copied three ways.** `guidelines_extract.repaired_text(page)`
composes the map and the rebuild, lives with the machinery it composes, and takes a duck-typed page so
`guidelines_extract` need not import the adapter.

**Lazy rather than an eager record**, because `render_glyph` rasterizes per candidate slot at
`OPERATOR_RENDER_SCALE = 12.0` and `guidelines_recs`' curated and table limbs want neither operators
nor repaired text -- its own comment says the reconstruction *costs substantially more than a plain
read*. **A document context manager rather than only a page read**, because `threshold_sheet` tier 2
calls `open` once per cache miss, so a sheet citing five pages of one PDF opens it five times.

### 4. The raster interface is one parameter, one shared constant and five owned behaviors

```
page_image.rasterize(export, destination, *, name, dpi=RASTER_DPI) -> int
page_image.export_page_count(export) -> int
```

| divergence across the three loops | ruled | ground |
| --- | --- | --- |
| filename, `page-N.png` against `slide-N.png` | a parameter | `CONTEXT.md` Render pass already rules it: *the filenames inside are each producer's business behind a globbed shape* |
| the route loop | stays with the caller | [ADR 0142](0142-the-word-export-route-is-shared-by-stem-and-a-reached-bound-ends-it.md) ruling 1: *what is shared is the script and not the route loop* |
| production DPI, three copies of 120 | one constant, overridable | nothing rules it per producer and all three chose the same value independently |
| per-page failure, collect against abort | the adapter collects and names the pages | `deck_render` is the only aborter and both paths end in a discarded pass, so this is message quality rather than behavior |
| partial-file staging | the adapter owns it, `deck_render` gains it | redundant against `render_pass`'s directory rename for a single-route caller, but load-bearing for `discussion_post_render`, which wipes `staging.glob("*.png")` between routes and would otherwise count a partial from a failed one |
| empty-export message | one message, callers may wrap | the domain wording is the producer's, the fact is the adapter's |
| page count | a function, not a module | ruling 1 |

**`export_page_count` pays for itself immediately**: with it and ruling 5, `render_scan` names the
engine's product name nowhere -- it still catches the seam's typed absence, which is what ruling 2
requires of every caller and what preserves its one coverage limb. Driven with the import blocked,
`_read_export_pages` returns `(None, "PyMuPDF is unavailable")`, which reaches `UNREADABLE_EXPORT`
and exits 2; an `int`-returning adapter that swallowed the absence would delete that limb, so the
rise out of `page_image` is load-bearing rather than tidy.

### 5. The image probe moves into the raster module, loses its engine parameter, and the two DPIs become two constants

The pixels module owns three functions on one subject -- the page images a render pass keeps and the
export they came from -- so `page_image` is its name. `PNG_SIGNATURE` and `RENDERED_RASTER_DPI` move
with the probe; neither has another consumer once ruling 4 redirects `discussion_post_render`'s
re-export.

**The parameter goes**, because ruling 2 makes the detection the seam's and an adapter that makes its
caller detect pushes one decision back out to two callers -- and it is what would keep `render_scan`
importing the engine for no reason but to hand it in. `render_scan` catches the absence into its
existing read-error string, unchanged. `discussion_post_scan` catches it and, under ruling 9, reports
its rendered-pages row `not graded` at exit 2 rather than folding the absence into a finding.

**Which behavior wins on the three divergences:** the signature check, the interpolated failure and
the `str | None` return, all three from `png_read_error`, all three strictly more informative.

**`DECODE_PROBE_DPI` is named apart from `RASTER_DPI`** so no reader infers a relationship the
measurement denies, and it is `1`.

**What is traded away**, named rather than found: the body cites `png_read_error`'s parameter as the
existence proof precisely because *its tests substitute a fake public interface without touching
`sys.modules`*. That property goes, against one acquisition seam instead of nine. Whether the build
exposes a private accessor for tests to patch is wiring and is not ruled here.

### 6. The engine-version read is one importing read, and the declaration population is ten

Ruling 2 reaches the detection and the verdict. The **report** had two implementations answering
different questions -- `pymupdf.__version__` from the imported module and
`importlib.metadata.version("PyMuPDF")` from distribution metadata without importing -- one of which
feeds a content-addressed key.

**One function on the seam**, `engine_version() -> str | None`, which **imports**, because that is the
question a run actually asks, and reports absence rather than a version. `guidelines_extract._engine_version`
and `guidelines_build._package_version("PyMuPDF")` both consume it, so the manifest's `engine` field
and the identity's `runtime.pymupdf` can no longer disagree about one fact in one artifact.
`_package_version` keeps its generic signature for `python` and `sqlite` and stops being the engine's
second opinion.

**`guidelines_build` declares a role like the other nine**, and its corpus is a primary source, so
*not installed* refuses. Ruling 2's conversion in `guidelines_recs` closes the traceback that escapes
it today without a further ruling.

**Whether a build identity should key on what is installed or on what imports is not settled here.**
The importing read is ruled because a key computed for a build that cannot run is never consulted;
that is a reason, not a proof about cache correctness.

### 7. The shared seam is its own module, reversing the placement recommended under ruling 2

Ruling 2 was recommended with *not a third module*, on `console_codec`'s bar -- *infrastructure rather
than a tool another tool happens to need* -- applied to a module holding one `try: import`. **The
shared surface grew across rulings 2, 3, 6 and 8 and the ground moved with it**: a typed absence and
its remedy sentence, a typed read failure, an importing version read, and a ten-row role map spanning
producers, graders and a build orchestrator.

Under the recommended placement one adapter arbitrarily owns the exception and the other imports it, a
directed dependency between peers chosen by nothing; `guidelines_build` must import a rasterizer or a
glyph reader to ask a version question; and the role map has no home, ADR 0116 ruling 4's `run_grader`
being wrong for a population where six of ten are not graders.

```
pdf_engine.EngineUnavailable   the typed absence, carrying the one remedy sentence
pdf_engine.SourceUnreadable    the typed failed open
pdf_engine.acquire()           the single try: import, called from inside the caller's opening function
pdf_engine.engine_version()    ruling 6's importing read
pdf_engine.ROLES               name -> (role, reason), ten rows, non-adapters included
```

**`page_image` and `page_text` become its only two callers of `acquire()`, so exactly one module in
the tree imports the engine** -- nine to one. The producers, `guidelines_recs`, `split_census`,
`threshold_sheet`, `render_scan`, `discussion_post_scan` and `guidelines_build` reach it only through
an adapter.

**Decision 4 is untouched and becomes checkable in one place.** `pdf_engine` imports nothing but
stdlib at module scope, so importing it costs nothing, and the engine import lives inside `acquire()`
which callers invoke from inside the function that opens the file.

### 8. Three walks hold the mechanical half and the rest is declared

In `tools/test_pdf_engine.py`, tests only and no command, on `test_ls_files_coverage.py`'s and
`test_write_guards.py`'s precedent.

- **`pdf_engine` is the sole acquirer.** No non-test `tools/*.py` outside it names the engine in a
  *use* position -- no import of `pymupdf` or `fitz`, no `importlib.metadata.version` or
  `importlib.import_module` call with an engine literal. *Under the negation the walk names the
  module; under the claim it names none.*
- **The acquisition is not at module scope.** One assertion where decision 4 was nine.
- **`ROLES` is complete in both directions.** Every module importing `pdf_engine` has a row and every
  row names such a module.

**By AST and not by substring**, because `docx_read`, `docx_write`, `run_grader` and `threshold_sheet`
all name the engine in prose -- mostly to explain why they do not use it -- and this repository has
already broken `spelling_scan` on its own homoglyph map, `differential_scan` on prose describing the
row it grades, and `phi_scan` on two files that exempted themselves by explaining its pragma. A
substring walk would need an allowlist; an AST walk cannot see a docstring.

**`pdf_engine` carries a `DECLARED_LIMITS` naming what this record's residue section names**, so the
seam is visible to the repository's own limits walk rather than declared only in prose here. The
first draft of this record ordered two new modules and three tree walks and named no limits object of
any spelling, which is exactly the blind spot
[#921](https://github.com/mshamblin5150-code/clinical-skills/issues/921) is about, arriving in a
record published while that ticket was open.

*(Corrected in place 2026-09-12, on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms, found by [#948](https://github.com/mshamblin5150-code/clinical-skills/issues/948)'s grilling.
**This record's cardinality has moved and its membership has not.** `ROLES` held ten rows when this
was ruled; it holds 11 today, and the "six of ten are not graders" split above is now
8 primary source to 3 optional secondary. The ruling-8 walk pins membership in
both directions and **does not pin a count**, so those rows arrived with the suite green and correct
— the figures above are historical and the module is the only current authority for them, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. Re-derive with
`len(pdf_engine.ROLES)` rather than from this paragraph.)*

**Its ceiling is stated beside the claim**: an engine name assembled at run time, or a distribution
string held in a constant and passed to `version()`, is invisible. That ceiling is **not hypothetical**
-- `guidelines_build` reaches the engine by a distribution literal today and the body's matcher cannot
see it. The walk reports its denominator and unread remainder, and is fed a zero-match and a
partial-match mutant and driven red before its coverage claim is believed.

### 9. A grader that lacks the engine does not fail a clean submission

Found by driving rather than by reading, while re-deriving the tracker sweep's last six verdicts at
`ffbe5c6`. **Ruled by the clinician on 2026-09-10.**

**Ruling 2 as first written classified `discussion_post_scan`'s missing-engine behavior two ways.** The
measured table above records it as *"1 as a finding"*; ruling 2 called it a correct optional-secondary
posture, degrade and state the narrowing. ADR 0116's table keeps those postures apart. Driven on
`test_discussion_post_scan.CanvasSubmissionRows`, each test run once with the suite's fake engine and
once with the import blocked, **4 of 14 clean submissions change from exit 0 to exit 1 on the missing
engine alone**, with `rendered-pages` going 0 to 1: `tools/discussion_post_scan.py:995` appends the
absence to `detail`, and `:1026` turns any non-empty `detail` into a `RENDERED_PAGES` finding. The
fake-engine run is the control; had the fixtures produced the finding, it would have exited 1 too.

**A missing engine says something about the grading machine, not about the post.** When
`discussion_post_scan` cannot decode retained captures because the engine is unavailable, the
`rendered-pages` row reports `not graded` and names the missing engine, and the command reports that it
did not scan -- exit 2 -- through its existing coverage-failure route. A real finding on the same run
still exits 1, on the family's ordering. An absent input never masquerades as a passing count, and it
does not masquerade as a failing one either.

**This is a second behavior change**, beside `guidelines_recs`'s traceback. Every other status and
message stays as measured.

**Already consistent and unchanged:** `render_scan` reaches `UNREADABLE_EXPORT`, an exit-2 coverage
limb, and `threshold_sheet` tier 2's `SKIPPED` fails nothing. Neither fails a clean artifact on a
missing engine.

## What this does not reach, declared rather than left to be found

**Whether a declared role is the right role.** ADR 0116 ruling 1's price inherited verbatim -- role is
not a mechanical property, so this is enforced by declaration and never by a conformance walk, over a
population of ten rather than sixteen. `guidelines_recs` is the recorded instance of what an
undeclared role produces.

**Whether an adapter leaks an engine object.** That `PageRead.render_glyph` returns
`(samples, width, height)` rather than a page is a reading of the code and not a shape a walk settles.

**The image probe's 60-byte window**, inherited from both implementations and closed by nothing short
of a byte-length floor named at an edge with no corpus behind it, which is
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s refusal.

**That a file decoding at `DECODE_PROBE_DPI` decodes at a reading resolution.** Measured only that the
two agreed on every truncation tried.

**Splitting `guidelines_extract`.** It is 1,988 lines doing two jobs -- page-level glyph reading and
corpus-level document building -- and nothing in ruling 3 requires touching that. It is a roughly
700-line diff with its own argument.

**The consumer contract.** [AGENTS.md](../../AGENTS.md) names `case_study_render.py`, `deck_render.py`
and `render_scan.py` as skill dependencies and **never says any of them needs an install**, while
saying of the ICD path that *there is still nothing to install*. Decision 4's protected property is
that the modules **import** with nothing installed; four consumer-required commands cannot **run**
without the engine. Ruling 7 gives that gap an address it lacked; changing the file a consumer reads
is its own decision and is filed rather than claimed here.

**#410's three unlocked gates in `threshold_sheet`.** The ticket records them and declines to claim
them; so does this.

## A glossary correction the session made on itself

The grilling ran on `vendor` for six rounds before the glossary was checked. The tree's word for the
library is **engine**, already in the *Extraction identity* entry and in the extraction manifest's
`engine` field, so `CONTEXT.md` gains the term with a distinction clause against **reader**.

**Three corrections to this paragraph's own first draft, all found by the tracker sweep of this
branch and all re-derived before being believed.**

**The figures were stated without an instrument or a base.** At the record's declared base `bf79efd`,
`grep -c "reader" CONTEXT.md` is **38 lines** while `grep -oE "\breader\b"` is **49 occurrences** and a
substring count is 50. The draft published *"`reader` appears 38"*, which is a line count sold as an
occurrence count -- the unit trap this repository already records for MB against MiB, recurring
inside a ratified record. `vendor` is **0** at that base and **1** at the commit that publishes the
claim, because this record's own `_Avoid_` row is the occurrence.

**And `vendor` is not absent from the tree, only from `CONTEXT.md`.** It is live in ten tracked files,
including three ratified records -- and `ADR 0124`, the record that **filed #837**, calls this exact
object *"a vendor seam"* twice, at its `:147` and `:222`. So the `_Avoid_` row is a deliberate
retirement of an incumbent term rather than the naming of an unused one, and saying so is the
difference between a ruling and an observation.

**The first draft of this record then used the retired word three times**, naming the seam's exception
`VendorUnavailable` and its version read `vendor_version()`, one paragraph from the sentence ruling
that word out. Corrected above to `EngineUnavailable` and `engine_version()`. That is this
repository's oldest recorded shape -- describing a rule breaking the thing that checks it -- arriving
on the record that writes the rule.
