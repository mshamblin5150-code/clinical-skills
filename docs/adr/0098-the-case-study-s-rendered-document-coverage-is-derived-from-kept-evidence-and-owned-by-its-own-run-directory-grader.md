# The case study's rendered-document coverage is derived from kept evidence and owned by its own run-directory grader

[#714](https://github.com/mshamblin5150-code/clinical-skills/issues/714) was filed from
[#676](https://github.com/mshamblin5150-code/clinical-skills/issues/676)'s grilling, on
[ADR 0087](0087-the-rendered-page-check-names-a-spawned-word-route-and-its-verdict-is-a-counted-record-backed-by-kept-pixels.md)
ruling 9's split: `skills/practicum-case-study/SKILL.md` step 9's `the rendered document` check has
the identical two holes as its sibling — no page count and no kept pixels — so a reviewer that
images five of nine pages and writes a fluent sentence about hanging indents passes every row.

Grilled 2026-09-01. **Seven decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

## Measured before ruling, at `8c8696b`

Freshness gate `FRESH` at both checkpoints. `main` moved five times during the session and every figure
below was re-derived at the final base. **The last measurement falsifies the rationale this ticket
was going to lift wholesale**, and two more move a decision.

**The check is better off than its sibling was, which is what the ticket says.**
`checks_ledger.EXPECTED_CHECKS` holds **13** rows including `the rendered document`;
`SUBSTANTIATED_CLEAN` holds **7** and includes it, so a bare `VERDICT: clean` is already refused.
The record grammar admits `VERDICT` and `FINDINGS` and nothing else.

**The archive carries no page count.** `docx_write.PART_NAMES` resolves to **7** parts with no
`docProps/app.xml`, so no offline tool can derive a denominator from the `.docx`.

**PyMuPDF on a `docx_write` document reflows**, which extends ADR 0087 ruling 4's refusal from that
record's evidence to this renderer's output: `is_reflowable=True`, page rect **400×600 pt
(5.56×8.33 in)** against the document's 8.5×11, and **9 pages**. It cannot supply the denominator.

**The two candidate graders differ in what they already do.** `checks_ledger` reads its argument
and touches the filesystem nowhere else. `case_study_scan` already resolves the run directory
through `coursework_run.run_for_submission` and raises `SourceError` when a submission has none —
but it runs **twice**, on the Markdown before step 8 renders and again after each repair, so on the
pre-render pass there is no render directory to count.

**A run-directory grader is the shape the house already has.** Five commands in `tools/` take
`<a run directory>`: `anchor_scan`, `block_scan`, `differential_scan`, `filled_vitals_census` and
`specificity_scan`.

**#676 is ruled and unbuilt.** Before this record, `UNSEEN:` and `PAGES:` appeared in exactly one
tracked file, and it was ADR 0087 itself — not the skill, not any tool. What a builder would find by
going to look at the sibling's shipped record is a specimen block in a record. *(This sentence is
written in the past tense because committing this record made the count two: it names those fields
in ruling 2 in order to retire them. The measurement was taken while it was still untracked, which
is [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s window and the same
window that hid this branch's parser defect for one run.)*

### ADR 0087 ruling 5's route does not return on this machine

Eight attempts, 2026-09-01. `Documents.Open` and `Documents.Add` returned in 1–3 s **every time**;
only the export hung, burning 45–85 CPU-seconds and writing no file.

| # | context | other Word running | document | call |
| --- | --- | --- | --- | --- |
| 1 | direct | yes | `docx_write`, 9pp | `ComputeStatistics` + `ExportAsFixedFormat2(p,17)` |
| 2 | direct | yes | `docx_write` | `ExportAsFixedFormat2(p,17)` |
| 3 | direct, `Visible=$false`, `DisplayAlerts=wdAlertsNone` | yes | `docx_write` | `ExportAsFixedFormat2(p,17)` |
| 4 | job | yes | `docx_write` | `SaveAs2(p, wdFormatXPS)` |
| 5 | job | none | `docx_write` | `ExportAsFixedFormat2(p,17)` |
| 6 | direct | orphan | `docx_write` | `ExportAsFixedFormat2(p,17)` |
| 7 | direct | **none** | `docx_write` | `ExportAsFixedFormat2(p,17)` |
| 8 | direct | **none** | **Word-authored, one paragraph** | `ExportAsFixedFormat2(p,17)` |

**The rationale is falsified rather than the figures.** Ruling 5 says *freshly spawned is
load-bearing rather than hygiene* and attributes #676's original hang to a contended shared
instance. Attempts 7 and 8 were freshly spawned with **zero** `WINWORD.EXE` on the machine, and 8
was a document Word authored itself — so neither `docx_write`'s output nor contention explains it.
This record does not claim the 2026-08-30 measurements were wrong; it claims they do not reproduce,
so the route may not be lifted as settled. The declared XPS fallback is dead on the same evidence.

**The failure mode matters to a build.** The hang is in the export call and not the open, so a
wrapper with no bound hangs a run rather than failing it, and killing `WINWORD` does not release the
calling host — each hung PowerShell host here reached 3,100–4,600 CPU-seconds and had to be killed
separately.

## Ruled 2026-09-01

### 1. A pass keeps its pixels and its exported render

ADR 0087 ruling 3 keeps page images and counts them against a self-reported `PAGES:` line, on the
ground that the archive has no page count. That is true of the **archive** and false of Word's
exported **PDF**, which ruling 4 already measures as page-faithful. Keeping the export beside the
images makes the denominator `page_count` on a file that is on disk.

**Pixels only was refused** because it leaves half the count a claim, in the skill where the stakes
are higher — the graded APA artifact whose hanging indents, centered `References` heading and page
breaks exist only in the render, and whose reference list is routinely not on page 1. **The export
alone was refused** because ruling 1's *a page with no picture is a page not checked* then has
nothing left to count.

The cost is about 236 KB per pass, on ADR 0087's measurement, of a second copy of a patient-bearing
document under `scratch/runs/<course>-<module>-case-study/render/pass-N/`. That is the PHI
firewall's own directory, it is not a top-level scratch entry, and the run directory already holds
`evidence.txt` and `claims.md`.

### 2. Coverage is derived from that evidence, and the record gains no fields

The numerator is the image count in `render/pass-N/`; the denominator is `page_count` of the kept
render beside them. The `## CHECK:` record keeps `VERDICT` and `FINDINGS` and gains nothing.

Each of ADR 0087's three fields has no work left once the export is kept. `PAGES:` carried a
denominator that is now on disk. `SOURCE:` named where the count came from, and the kept file is
that — `.pdf` or `.xps` by extension. `UNSEEN:` recorded pages nobody reached, which ruling 8
already refuses to permit.

**Extending the shared grammar was refused**: it is a schema change to a grammar 13 rows share, for
one row, and it re-introduces a self-reported numerator beside the countable one — the hole ADR 0087
spent kept pixels to close, reopened one field over. **A second file was refused** on the same
ground plus a second grammar to parse and a new artifact in the keep-list.

**What this makes visible rather than creates.** A clinician-route read under ADR 0087 leaves no
image files, so ruling 3's count already fails for those pages while ruling 7 blesses them. That
conflict is in ADR 0087 unreconciled; deriving the count surfaces it instead of leaving it in the
gap between two fields. Ruling 6 below is where it lands.

### 3. A new run-directory grader owns the count, and `checks_ledger` keeps the verdict

`tools/render_scan.py`, taking `<a run directory>`, cited in step 9's table as a command row the way
`the house style` is. It inherits `run_grader` and `grader_conformance`.

**The two claims are different and stay apart.** `checks_ledger` grades that a reader filed a
substantiated verdict; `render_scan` grades that the pages were imaged. Folding both into one
command lets a fluent record and an empty directory sit behind a single exit 0, which is what this
repository's extractor-coverage rule refuses and what ADR 0087 spent kept pixels on.

**`checks_ledger` was refused** because it reads exactly one file and nothing else; counting a
sibling directory is a filesystem contract it has never had. **`case_study_scan` was refused**
because its subject is the draft body's house style, it opens no run evidence, and it runs before
the render exists — so it would need a gate to avoid failing a correct pre-render pass.

**The cost is named.** It is a fourteenth grader in a directory that tracks its own count, and it is
the thing #676 would most want to reuse against ADR 0087 ruling 9's *two implementation sites, not a
second call to one function*. That ruling is not revisited here; the tension is recorded on #676.

### 4. A short count is exit 1, absent evidence is exit 2, and 1 wins where both hold

Images present but fewer than the kept render's `page_count` is a **finding**: the command measured
coverage and coverage is short. No `render/` directory, or images with no kept render to supply a
denominator, is **did not scan**: the command could not measure coverage at all. Where both hold
across passes, 1 wins, on `differential_scan.py`'s ordering.

**This reconciles ADR 0087 ruling 8 with ADR 0089 ruling 5 rather than choosing between them.** The
distinction is *measured and short* against *could not measure*. **Everything-is-1 was refused**
because an absent render directory would then carry the same status as a nine-of-ten read, which is
[#150](https://github.com/mshamblin5150-code/clinical-skills/issues/150)'s defect — a check that
never ran reading as one that did. **Everything-is-2 was refused** because it files the strongest
thing known about the run under the weakest heading.

**Ruled with the consequence in view.** While the export route hangs, no run can produce a render,
so **every case-study run exits 2 on this row** until the route is repaired. That is the correct
report rather than a broken build: it says nobody looked at the rendered pages, which is true, and
it makes the route failure loud instead of letting a fluent `clean` stand over an empty directory.

### 5. `the rendered document` stays in `SUBSTANTIATED_CLEAN`, unchanged

#714's decision 3 asked whether the narration requirement becomes redundant once a `PAGES:` field
exists. Ruling 2 means no such field exists, so the premise never arrived.

**Dropping it was refused** because it is the worse outcome for the split ruling 3 builds:
`render_scan` says which pages were imaged and the substantiated `clean` says what was looked for,
and without the second a run can image nine pages, read two, and satisfy everything.

**Tightening it was refused deliberately.** Requiring the `clean` to name which defect classes it
walked adds a rule to `checks_ledger` that the step does not ask for, which is the test every row of
that grader has to pass, and
[#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255) ruled the narration
requirement narrow on purpose. Widening it inside a ticket about coverage would be doing it sideways.

### 6. The route is the automated one first, then a clinician export, and the agent always compares

Step 9 names a route order rather than pointing at a route measured as working and now measured as
hanging. The automated route runs first, **bounded**; where it does not return, the clinician
performs `File ▸ Export ▸ Create PDF/XPS` by hand into `render/pass-N/`, and the agent images that
file with PyMuPDF and performs the page-by-page comparison itself.

**The escalation is an export and not a read**, which is where this departs from ADR 0087 ruling 7
and why. Under derived coverage a clinician who looks at the screen produces nothing on disk, so the
row cannot pass that way. Asking for the export asks for the one thing only an interactive Word can
currently do, leaves the comparison with the agent — ruling 7's own principle, *the clinician's read
covers a remainder and never replaces the comparison* — and dissolves ruling 7's stated worry that
the escalation collapses into the go-ahead he was already giving, because he returns a file rather
than a verdict. It also makes the row satisfiable while the automated route is dead.

**The bound is not a measurement and is declared as one that is not.** The call never returns at
all, so there is no plateau to sit in the middle of and nothing to tune against. It exists to stop a
run hanging. `SPACE_ADVANCE_FRACTION` is the record of what naming a value at an edge costs, and the
honest form here is that no edge was found because the distribution has no far side.

### 7. Only the last pass must be complete

A real run re-renders: step 9 finds a defect, it is repaired, the document is rendered again. ADR
0087 ruling 6 appends one `## RENDERED:` record per pass; that cannot transfer, because
`checks_ledger` has a `duplicate-check` row and step 9 says **one record per check**, so
`## CHECK: the rendered document` appears once and describes the final state. Only the directory
carries passes.

Each pass writes its own `render/pass-N/`. Earlier passes are counted and reported and **never
failed**; the last pass must be whole.

**Per-pass completeness was refused.** A reviewer that images page 2, finds a broken table and stops
to get it fixed has behaved **correctly**, and requiring it to image the remaining seven pages of a
render it is about to discard is work that buys nothing — the false-alarm-on-correct-work shape
refused on `spelling_scan`'s suffix rules, `case_study_scan`'s stop-criterion row and
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215). Ruling 6's reason for
per-pass completeness was that `PAGES:` was self-reported per pass, so an incomplete pass could hide
behind its own number; with the count derived, an earlier pass hides nothing and is simply fewer
files, reported.

**Overwriting a pass stays refused**, on ADR 0087 ruling 6's ground: it deletes the evidence the
check earns its cost with.

The render directories are run evidence and survive step 9's line about removing the run's private
paths, joining `claims.md` and `checks.md` in what the run keeps.

## What this does not reach

**Whether the reviewer's comparison is any good.** Every ruling here is about coverage — that a page
was imaged, that the image is on disk, that neither half of the count is self-reported. A fluent
`VERDICT: clean` over nine pages the reviewer looked at carelessly passes every row.
`specificity_scan.py`'s R2 limit, inherited by every substance test in this repository, and ADR 0087
declares the same residue.

**Whether the pages imaged are the pages read.** `render_scan` counts files against a page count. A
run that images every page and reads two satisfies it, which is why ruling 5 keeps the narration
requirement rather than treating the count as its replacement.

**Why the export route hangs.** Eight attempts establish that it does, on this machine, on
2026-09-01, for a document Word authored itself. They do not establish a cause, and no cause is
ruled here. It is filed rather than diagnosed.

**Whether the clinician's own export is of the finished document.** Ruling 6 asks him for a file and
grades its page count; nothing checks that the file he exported is the submission rather than an
older copy open in the same Word instance. A shared instance holding several documents is the
recorded state of this machine.

**`discussion-post`'s arrangement.** ADR 0087 ruling 9 rules the two sites apart and this record
does not revisit it. Rulings 1, 2 and 6 would each apply there, and each is recorded on #676 as a
finding for the clinician rather than applied.
