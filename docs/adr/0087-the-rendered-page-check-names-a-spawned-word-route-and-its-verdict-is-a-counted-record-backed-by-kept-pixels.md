# The rendered-page check names a spawned-Word route and its verdict is a counted record backed by kept pixels

> **Reconciled during #676 implementation, 2026-09-01.** The repository-wide **Render pass**
> definition introduced with ADR 0098 now governs this site too. One pass keeps one page-faithful
> PDF or XPS and only images rasterized from that export; a failed route contributes no pixels to
> the next route. The clinician escalation supplies an export rather than replacement page images.
> Every record and retained export remains graded, but only the last pass must be complete, carry
> `UNSEEN: none`, and end clean. This supersedes rulings 3, 6, 7, and 8 where their original text
> conflicts. The original record below is preserved as the decision history.

[#676](https://github.com/mshamblin5150-code/clinical-skills/issues/676) was filed over
`skills/discussion-post/SKILL.md` step 7 requiring *"a vision-capable, non-authoring context"* to
compare **every rendered page** with the Markdown while naming no way to rasterize the `.docx`. It
was found in a live run against NUR_5042 M3 on 2026-08-30, by the reviewer performing that step,
which imaged pages 1 and 2, never imaged page 3 — the entire reference list — and said so.

Grilled 2026-08-30. **Eight decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## Measured before ruling, at `0d26b95`

Freshness gate `FRESH` at both checkpoints. Six measurements. **The first falsifies the ticket's
central factual claim**, and three more move a decision.

**The three routes the ticket calls dead are alive.** #676 states that `ExportAsFixedFormat`,
`SaveAs2(..., wdFormatPDF)` and printing to Microsoft Print to PDF *"all hang. Fifty-four
CPU-seconds on three pages, never returns"*, and attributes it to the Acrobat PDFMaker add-in.
Measured twice, once by a fan-out and once independently, from a **freshly spawned** `WINWORD.EXE`
with PDFMaker loaded and connected and no admin:

| route | measured |
| --- | --- |
| `ExportAsFixedFormat2(path, 17)` | **0.71 s** export, 2.34 s end to end, 236,232 B |
| `ExportAsFixedFormat` v1 | 0.85 s, 236,236 B |
| `SaveAs2(path, wdFormatPDF)` | 1.16 s, 236,239 B |
| `SaveAs2(path, wdFormatXPS)` | 1.56 s, 531,772 B |

Three repeats of the chosen route returned 0.50 / 0.49 / 0.49 s with **byte-identical** output. The
add-in diagnosis is wrong: `COMAddIns.Connect = $false` does raise without admin — *"installed for
all users on this computer"* — but the export does not need it disconnected.

**The probable cause is contention, not the API.** An interactive `WINWORD.EXE` had been open since
2026-08-29 on an unrelated document with 276 CPU-seconds against it. A harness that spawns its own
process, opens `ReadOnly`, and never touches `Application.Visible` or calls `Quit` on a shared
instance could not reproduce the hang on synthetic or real documents, from a background job or the
main process.

**PyMuPDF opens a `.docx` directly, and that route is disqualified.** `pymupdf.open()` returns
`format='Office document'` in 0.04 s and renders non-blank pixels — and it **reflows**:
`is_reflowable = True`, page rect **400×600 pt (5.56×8.33 in)** against the document's 8.5×11, and
**10 pages where Word says 11**. `doc.layout(612, 792, 12)` re-paginates to 7. It cannot reproduce
Word's pagination or page setup, so it can serve a text preview and neither a page count nor a
check of margins, page breaks or APA layout.

**The Word PDF rasterizes page-faithfully.** PyMuPDF over `ExportAsFixedFormat2`'s output:
`PDF 1.7`, `is_reflowable = False`, rect **612×792 pt = 8.50×11.00 in**, 11 pages, full render at
120 dpi in 0.03 s, first page 1020×1320 with a dark-pixel fraction of 0.0314. XPS through the same
reader is equally faithful at 11 pages and the same rect.

**Nothing else on the machine converts.** `soffice`, `libreoffice`, `pandoc`, `wkhtmltopdf` and
`docx2pdf` are all absent. Acrobat DC is installed and neither `Acrobat.exe` nor `acrodist.exe` is
a supported `.docx` CLI. Edge and Chrome are present and print HTML, not `.docx`.

**The two verdicts in this skill are treated asymmetrically, and the wrong one has the machinery.**
`skills/discussion-post/SKILL.md`'s Completion section already requires a `rendered-page verdict`
to be reported, and that is the whole of it: it is written to no file, has no grammar, and is read
by nothing. The **posted-reading** verdict — a check on a page anyone can re-open in a browser —
is written to `reread.md` under `## REREAD:` with `VERDICT: matches - <substance>`, and
`discussion_post_scan.py` grades it. `discussion_post_scan.NOT_REACHED` holds eight rows and none
is about pages seen.

**The document carries no page count.** `docx_write.PART_NAMES` is seven parts —
`word/document.xml`, `word/styles.xml`, `word/numbering.xml`, `word/header1.xml`, both rels parts
and `[Content_Types].xml` — and **no `docProps/app.xml`**. Pagination is a property of a renderer,
not of the file, so no offline tool can derive the denominator from the archive.

**The sibling skills split.** `skills/discussion-reply/SKILL.md` has no render step at all — zero
hits for every rasterization and rendered-page term. `skills/practicum-case-study/SKILL.md` step 9
has the identical check, `the rendered document`, and is one notch better off: it is in
`checks_ledger.EXPECTED_CHECKS` **and** in `SUBSTANTIATED_CLEAN`, so a bare `VERDICT: clean` is
already refused there. It has neither a page count nor kept pixels.

## Ruled 2026-08-30

### 1. A page with no picture is a page not checked

The 2026-08-30 reviewer took page 3's geometry from Word's own pagination data and rendered that
page's content as a **separate document** to look at. That is not the check.

Word's pagination answers *where did I put this*. Every defect this step exists to catch is *what
does it look like where you put it* — clipping, overlap, a glyph rendering wrongly, text running
under a margin. The one defect the check has caught was eleven lines of `INVOKED` agent working
notes rendering as visible prose on a graded page, which every command exited 0 on; that is a
looks-like defect. And a second document is a second renderer run, so it cannot settle the first
one's reference-list hanging indent.

**Geometry survives as the denominator and never as the check**, which is ruling 4.

### 2. The verdict is a written record with a declared grammar, graded

Not prose in the Completion row. The run appends to the private `post.md`:

```text
## RENDERED: post.md
PAGES: 3 of 3 imaged
SOURCE: word-pdf
UNSEEN: none
READ: 2026-08-30
VERDICT: clean - three pages compared; headings bold, references hang, nothing clipped
```

`discussion_post_scan.py` grows a row that reads it. An absent record, an absent `PAGES:` or
`SOURCE:` line, an unrecognized `SOURCE:` value, or a `VERDICT:` keyword with nothing substantive
after it is a finding — the shape the `reread.md` row already has.

**The parity argument is the ruling.** The posted reading, on a board page anyone can re-open,
already has a file, a grammar and a grader. The rendered reading, on an artifact that exists for
about ninety seconds inside an off-screen Word instance and can never be re-examined, had none of
the three. That asymmetry is backwards.

**Strengthening the Completion row's prose was refused.** That is what the step already is, and
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s rule — *what a written
instruction cannot do is fail* — is why #676 exists.

**`post.md` and not `reread.md`.** Step 7 precedes submission; `reread.md` is a step-8 file shared
with `discussion_reply_scan`, and a render record there would sit in a file whose subject is the
board. `post.md` is the private working record of the very document that was rendered and already
gains `POST-URL:` and `POSTED:` later.

**The row is gated on `--docx`**, exactly like `bold-headings`, and reports `not graded` without
it: at step 6 the document does not exist yet. With `--docx` present, an absent record is a
**finding**, exit 1 — the set is fixed by the step, so this is `checks_ledger`'s missing-check
shape and not `research_ledger`'s empty-file shape.

### 3. The count is backed by kept files, not taken on the reviewer's word

The route writes page images to `scratch/runs/<course>-<module>-discussion/render/pass-N/`, they
stay with the run, and the grader counts them against that pass's `PAGES:` line.

Without this the row is a spelling check: the archive carries no page count, so both halves of
`PAGES: 2 of 3` are the reviewer's own claim and `2 of 2` passes every row in ruling 2. The
repository's extractor-coverage rule requires a population derived independently of the
extraction; here the extraction is a reader agent and the population is invisible to every offline
tool, so the numerator is made countable instead — a directory listing rather than a sentence.

**It also makes the check auditable at all.** Before this, a rendered-page verdict was the only
verdict in the skill that nobody could ever go back and check.

**The render directory is run evidence and survives step 7's cleanup line**, joining the keep-list
beside `post.md` and `reread.md`. It is not a temporary per-agent path.

### 4. The denominator is Word's pagination, and PyMuPDF's direct `.docx` reader may not supply it

`SOURCE:` names where the page count came from — `word-pdf` for the ruled route, `word-xps` for the
fallback, `clinician` for ruling 7's escalation.

Word is authoritative for how many pages there are; ruling 1 excludes its geometry from settling
what a page looks like and not from counting them. **PyMuPDF opened on the `.docx` directly is
refused as a `SOURCE:`** on the measurement above — 5.56×8.33 in and 10 pages against Word's 11.
It is the obvious one-liner and it silently answers a different question, which is why the refusal
is ruled rather than left to be rediscovered.

### 5. The named route is a freshly spawned Word instance, then PyMuPDF

`Document.ExportAsFixedFormat2(path, 17)` in a **newly created** `Word.Application`, opened
`ReadOnly` with `ConfirmConversions` false, never touching `Application.Visible` and never calling
`Quit` on a shared instance; then `pymupdf.open(pdf)` and `get_pixmap(dpi=120)` per page. About
2.3 s end to end, no new dependency — PyMuPDF is already in the tree — and no admin.

`SaveAs2(..., wdFormatXPS)` into the same reader is the declared fallback at about 2.4 s and equal
fidelity, for a machine whose Word PDF path is genuinely broken.

**Freshly spawned is load-bearing rather than hygiene**, and it is the whole of the ticket's
premise being wrong: the routes #676 records as hanging are the same API calls, and what differed
was the process they were made in.

**The ticket's own three options were all refused.** Word COM to PDF is not broken. `Read` with
`pages` against a PDF is downstream of a route rather than a route. Rendering the Markdown to a
second format is not the same check, because it does not exercise the renderer under test — which
#676 itself says.

### 6. Re-renders append; each pass keeps its own pixels

A defect found at step 7 is fixed through the drafting context and the document is rendered again,
so a real run has two renders and two verdicts — which is what happened on the M3 run. Each render
appends its own `## RENDERED:` record and writes its own `render/pass-N/`. Every record must
parse, each pass's files are counted against its own `PAGES:` line, and the **last** record must be
clean.

**Replacing the record was refused** because it deletes the only evidence the check earns its cost.
**Appending records while overwriting pixels was refused** as the worse of the two: the records
would say two passes happened while the directory holds one, so ruling 3's countable numerator
quietly stops matching the record it verifies.

### 7. The clinician is the named escalation, not an equal route and not excluded

The route order is written into the step. The automated route runs first; only for a page it
cannot reach does the run ask the clinician, recording `SOURCE: clinician` for those pages and
`UNSEEN:` for any he declines. The agent still performs the page-by-page comparison against the
Markdown for every page it images, so the clinician's read covers a remainder and never replaces
the comparison.

**Equal standing was refused** because it makes asking him the cheap path on every run, and step 8
already shows him the final post and waits for a go-ahead — so the check would collapse into the
approval he was giving anyway, and a check that reads as agreement is worse than none.

**Excluding him was refused** because it would have to record a page he can settle in ten seconds
as permanently unseen. He is vision-capable and non-authoring, which is what the step asks for.

### 8. An unimaged page fails, exit 1

`PAGES: 2 of 3`, or anything left in `UNSEEN:`, is a finding. This enforces itself through step 8's
existing requirement that the rerun's exit be 0; no new machinery.

The cost of this ruling changed with the measurement. When #676 was filed it looked as though no
route existed, so failing would have made the skill unusable on this machine; with a 2.3-second
route and the clinician as escalation, an unseen page means an available remedy was skipped.

**Declaring without failing was refused.** It repairs the *reading* and leaves the *exit status*
saying exactly what a complete check says — the ticket's own shape, relocated from the prose into
the status. **A conditional pass on a declined escalation was refused** because *"I asked and he
declined"* is a claim nothing can check, handing back the unverifiable path ruling 3 spent kept
pixels to close.

**It does not trap the clinician.** A direction to post with a page unchecked is an override and
stays visible as one; it is not encoded as a grader exemption that makes the row pass. These rules
bind the agent.

### 9. Scope is `discussion-post`, and the case study is filed rather than folded in

`discussion-reply` has no render step. `practicum-case-study` step 9's `the rendered document` has
the identical two holes — no page count, no kept pixels — and is filed as its own ticket in the
session that ruled this.

This is [#271](https://github.com/mshamblin5150-code/clinical-skills/issues/271)'s precedent:
[#185](https://github.com/mshamblin5150-code/clinical-skills/issues/185) found `--society` carrying
the identical defect as `--class`, deliberately left it, said so in the prose, and filed it — which
is what made it a ticket rather than a thing to be rediscovered. The two verdicts live in different
files with different graders, `post.md` and `discussion_post_scan` against `checks.md` and
`checks_ledger`, so this is a second implementation site and not a second call to one function.

**Leaving the case study unfiled was refused**: that is the version of this ruling that loses the
finding.

## What this does not reach

**Whether the reviewer's comparison is any good.** Every ruling here is about coverage — that a
page was imaged, that the images are on disk, that the count is not self-reported. A fluent
`VERDICT: clean` over three pages the reviewer looked at carelessly passes every row.
`specificity_scan.py`'s R2 limit, inherited by every substance test in this repository.

**Whether the clinician's own read was careful**, for the same reason and more so — his record is
graded for shape and never for what he saw.

**A machine where the Word PDF path is genuinely broken.** The XPS fallback is measured on this
machine only, and a machine with neither leaves `SOURCE: clinician` as the whole route.

**The page count where the run never renders at all.** `docx_write.write_docx` calls
`ensure_main_checkout`, so step 7 cannot render from a worktree; a run in one has no document to
image and the row cannot fire on a document that does not exist.

**Whether `PAGES:` names the pages a reader actually compared.** The grader counts files in
`render/pass-N/` and matches the numerator against them. A reviewer that renders every page and
reads two of them satisfies both.

**`practicum-case-study`'s identical hole**, until the ticket filed alongside this record is built.
