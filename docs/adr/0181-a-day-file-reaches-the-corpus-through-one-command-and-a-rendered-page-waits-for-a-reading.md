# A day file reaches the corpus through one command and a rendered page waits for a reading

[#1086](https://github.com/mshamblin5150-code/clinical-skills/issues/1086) was filed from
[#1009](https://github.com/mshamblin5150-code/clinical-skills/issues/1009)'s grilling:
`skills/batch-shift/SKILL.md` step 2 reaches the PDF engine through a fenced Python block opening
`import fitz`, which is the one use of the engine on the clinical path and sits outside the seam
[ADR 0160](0160-the-pdf-engine-is-reached-through-one-seam-the-page-questions-are-four-and-the-availability-verdict-is-the-caller-role.md)
built. The ticket asked whether step 2 calls a command instead, whether the seam's walks widen to
skill Markdown or declare the snippet, and whether the snippet moves from `fitz` to `pymupdf`.

Grilled 2026-09-11 to an empty frontier. **Sixteen rulings, by the clinician, on that date.**
Nothing is built here; this is the record the build reads. ADR 0160 stands unchanged, and
[ADR 0175](0175-a-skill-needing-the-pdf-engine-asks-to-install-it-and-walks-by-eye-only-when-it-cannot.md)
stands unchanged except that its ruling 10's snippet source is retired here, which that record says
this ticket would decide.

**The ticket widened once, under the standing rule that a subject entangled with a ticket's
correctness widens it.** No skill or tool says where a `batch-shift` run directory is or what it is
called, and the command ruled below cannot be specified without one, so ruling 7 names it.

## Measured before ruling, at `d096104`

Freshness gate `FRESH` before reading. Every figure was taken by running a command rather than by
reading prose.

**`scratch/day-file-text/` has three readers in `tools/` and no writer anywhere.** `corpus_census`,
`name_index` and `phi_scan` each resolve it; a `git grep` for the folder name across `skills/`,
`tools/`, `docs/` and `AGENTS.md` returns those readers, two ADRs describing them, and two fixture
READMEs naming it as a location. *Had a skill or tool written the folder, that grep would have
returned it.* It holds **49** files, all with a `.txt` suffix, counted by extension so no filename
was printed.

**Step 2 writes nothing and step 3 reads that folder.** The snippet extracts into the agent's own
session and saves no file, while step 3 runs `python tools/name_index.py` with no argument, whose
default is `scratch_root() / "day-file-text"`. So a newly scanned shift reaches neither the name
index nor the PHI corpus layer unless somebody saves its text by hand.

**The three readers disagree about what a day file is named.** `phi_scan.corpus_identifiers` globs
`*.txt`; `corpus_census` keeps `.txt` and `.md`; `name_index.read_corpus` filters on its own suffix
set and deduplicates by content digest rather than by filename. `.txt` is the only suffix all three
read.

**No producer in `tools/` returns 1.** `case_study_render`, `deck_render` and `docx_write` return 0
and 2 only. Across this repository, exit 1 is a grader's finding.

**The seam cannot see the snippet, and its own walk says why.** `test_pdf_engine.non_test_tool_sources`
iterates `TOOLS.glob("*.py")`, so skill Markdown is outside every engine walk. `page_text.py` and
`page_image.py` carry no `__main__` block, so no command offered what the snippet does.

**The glossary contradicted the path this record names.** **Run directory** read *"Named by the run
key, so it carries no date and outlives every sitting"*, and `coursework_run.py` repeats it: *"A run
is undated and each sitting is dated."* A shift's key carries its visit date. No test pinned that
wording; `ADR 0109` quotes it as history and is left as written.

**`AGENTS.md` names four engine-dependent skills and no command that uses the engine**, beside its
own rule that a skill *depends on* a tool only when the instruction is incomplete without it.

## Ruling 1. Step 2 calls a command and the snippet goes

`batch-shift` step 2 reaches the engine through a committed command rather than through a fenced
snippet. That puts the clinical path behind ADR 0160's one detection and inside the seam's walks,
and it retires the only reason #1009's derivation reads skill Markdown for Python imports.

Declined: a snippet importing `page_text` and `page_image`, which needs the agent to repair
`sys.path` from wherever it is standing and still sits outside the `ROLES` walk; and keeping the
snippet, which leaves the clinical path the one engine use nothing grades.

## Ruling 2. The command writes the day file's text into the account corpus

A day file with a text layer is written to `scratch/day-file-text/<day file name>.txt`. The command
is that folder's first writer, so a scanned shift reaches `name_index`, the PHI corpus layer and the
census without anyone remembering a manual copy.

Declined: writing only into the shift's run directory, and printing without writing, both of which
leave the three readers blind to every new shift.

## Ruling 3. An identical file is a no-op, a different one is refused

When the destination exists and the extraction is byte-identical, the command says so and exits 0,
so a rerun is harmless. When it differs, the command writes nothing, names the path and exits 2.
`--force` replaces it, for a rescanned or corrected source. The write goes through a temporary file
and `os.replace`.

The ground is that some of the 49 files were transcribed by eye from image-only scans and any of
them may carry hand corrections, so an extraction that returned nothing could destroy a curated
file with no recovery. This is `docx_write`'s refusal to overwrite what it did not write, and
`name_index`'s refusal to rebuild what a human corrected.

## Ruling 4. A scan is detected per page

A page whose text layer holds nothing beyond whitespace is rendered; a page with text contributes
its text. The report counts pages read as text and pages rendered, so no page leaves the run
uncounted.

The whole-document test the snippet used loses a scanned page inside a text-layer file: its
encounters vanish and step 2's rule that a zero-length extraction is a scan never fires, because the
document was not empty. Whether any catalog file mixes the two kinds of page is **not measured** —
it means opening source PDFs, which is reading PHI.

**One boundary is declared rather than guessed at.** A page carrying only a scanner stamp over an
image body counts as a text page. No length cut point is invented to catch it, on
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s refusal to name a threshold
with no corpus behind it.

## Ruling 5. No text file lands until every rendered page has a transcription

The first run renders `page-N.png` for each textless page, writes no `.txt`, and names the pages
that need reading. The agent reads each image and writes `page-N.txt` beside it. A later run on the
same source assembles the typed text and the transcriptions in page order and writes the `.txt`
through ruling 3's guard. The page count comes from the document and the transcription count from
disk; where they disagree the command writes nothing and names the missing pages.

The command stays the only writer of the `.txt`. A partial file holding only the typed pages would
be read as whole by all three readers, which is the partial-read-as-clean shape the repository's
extractor-coverage rule forbids.

## Ruling 6. The rendered pages and their transcriptions live in the shift's run directory

They go under `<run directory>/day-file/`, as `page-N.png` and `page-N.txt`. They are the evidence
of how the day file was read, which is what a run directory is for.

Declined: a sibling of the corpus text, which puts working material inside a reader population's
own folder, where a future recursive reader would take a transcription for a day file; and a
ticket-keyed working directory, which gives a clinical run's evidence the wrong owner.

## Ruling 7. A shift's run directory is `scratch/runs/shift-<YYYY-MM-DD>/`

The date is the visit date, which step 1 has already settled, asking the clinician where the
filename carries none. It matches the submission key the after-action review already uses, so the
directory and the submission share one date. `aar_scan` takes a run directory's own name as its run
key and applies no coursework grammar to it, so nothing else moves.

**Two sources for one date are refused rather than merged.** The command records the source
document's SHA-256 at `day-file/source.sha256` and exits 2 when a later run for that date names a
different document. Without it, a rescan's pages and the original's would assemble into one text.

## Ruling 8. The glossary widens rather than growing a second term

**Run key** is the identity of one unit of work: course, module and artifact for a graded artifact,
`shift-` and the visit date for a shift. **Run directory** carries no *sitting* date, and a shift's
visit date is identity rather than a sitting — a shift split on Monday and finished on Tuesday is
two sittings and one key. Both entries are edited in `CONTEXT.md` in this record's own change.

Declined: a separate *shift run* term, which gives two names to what `aar_scan` and
`filled_vitals_census` already treat as one thing.

## Ruling 9. Exit 1 means pages await a reading

The command returns 0 when the text file is written or already identical, **1** when it read every
page and found pages that must be read by eye, and 2 for every way of not producing the text: the
engine absent, a document that will not open, and rulings 3 and 7's refusals.

**This widens what 1 means beyond a grader's finding**, which no producer here has done, and it is
ruled because the alternative is worse. Under a single 2, step 2 would have to tell *pending* from
*refused* by looking at disk — and after ruling 7's hash guard refuses, the previous document's
images are still present with no transcriptions beside them, so disk state reads as pending and the
agent would transcribe the wrong day file's pages. ADR 0175 ruling 2 forbids a skill keying on a
printed reason, so the status is the only thing left to carry the distinction.

## Ruling 10. When the engine cannot be installed, nothing is written and the skill says so

ADR 0175 rulings 1, 3 and 5 already route that case to the agent's own PDF reader. No command runs,
so no `.txt` is written and that shift's names do not reach the PHI check. Step 4's
`Day file read with:` line gains that the shift's text did not reach the corpus, and step 2 says to
run the command on the same document once the engine is installed.

Declined: the agent writing the corpus file itself, which is a second writer past ruling 3's guard;
and a no-engine mode taking a page count the agent reports, where the denominator and the reading
come from the same party.

## Ruling 11. The command is `tools/day_file_text.py`

```bash
python tools/day_file_text.py <the day file.pdf> --date YYYY-MM-DD
```

It imports `page_text` and `page_image`, carries a `ROLES` row as a primary source, and resolves
both `scratch/runs/shift-<date>/day-file/` and `scratch/day-file-text/` through
`repo_root.scratch_root()`, so it answers from a worktree. It calls `use_utf8` on its command path
and joins the console-codec record in `CLAUDE.md` as the most recent direct command.

**Not `day_file_read.py`**: `CONTEXT.md` reserves **reader** for the party that judges, and this
decodes. Declined: a `__main__` on `page_text`, which would put a route loop spanning both adapters
inside one of them, against ADR 0160 ruling 4; and extending a module that reads the corpus folder.

## Ruling 12. #1009's snippet matcher becomes a prohibition

`tools/test_pdf_engine_contract.py` derives the engine-dependent skills from `ROLES` command names
alone, and asserts separately that **no** skill Markdown holds a fenced Python block importing the
engine. It is fed a fixture containing one, so the rule is proven live rather than green because the
tree is clean. `pdf_engine.DECLARED_LIMITS` gains a row saying what that still does not reach: a
skill may call the engine from a shell block, a `python -c` line, or prose, and none of those is a
fenced Python import.

That answers the ticket's decision 2 — the population widens to skill Markdown for the one shape a
walk can see, and the rest is declared. Its decision 3 falls away with the snippet: nothing is left
to move from `fitz` to `pymupdf`.

## Ruling 13. Textless pages render at 140 DPI through the seam's override

Step 2 records 140 as the resolution that renders these scans legibly, and
`page_image.rasterize` already takes a `dpi` argument over its shared constant. ADR 0160 ruling 4
set that constant from three producers rendering **exports they made themselves**; a scanned
handwritten page is a different subject. The value is inherited rather than re-measured, and
settling it would mean rendering real day files at both resolutions and reading them, which is
reading PHI and is the clinician's call.

## Ruling 14. The command deletes nothing

The rendered pages and their transcriptions stay after the text file is assembled, as the shift's
provenance. Disposing of patient material is the clinician's word, per file, and no tool schedules
the removal —
[ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md)
and [#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417).

## Ruling 15. `AGENTS.md` names the command in its engine paragraph

One clause: step 2 runs `python tools/day_file_text.py`, and skipping it costs the shift's text
reaching the PHI name check. That consequence is what separates this command from the tools
`AGENTS.md` lists as named but optional, none of which costs a firewall's coverage when skipped.
`batch-shift` is not moved into the depends-on-a-tool group, because the notes are still written
without it.

Declined: no change at all, which leaves a consumer knowing `batch-shift` needs the engine and never
what runs it.

## Ruling 16. The command prints counts and paths only

Pages read as text, pages rendered, pages awaiting a reading, and the path written. There is no
`--show`: the artifact is the file, so nothing is being withheld, and the command's output stays
pasteable into a ticket on the house rule every scanner here follows.

## What the build verifies

- **The three statuses are driven rather than read**: a text-layer document writing its `.txt`, a
  document with a textless page returning 1 and naming it, and each exit-2 limb including the engine
  blocked from import.
- **The overwrite guard both ways**: an identical rerun exits 0 and rewrites nothing, a differing
  extraction refuses and leaves the existing bytes untouched, and `--force` replaces.
- **The transcription loop**: a partial set of `page-N.txt` writes no `.txt` and names the missing
  pages, and a complete set assembles in page order.
- **The source guard**: a second document for one date exits 2 rather than assembling across two.
- **The prohibition in ruling 12 is fed a fixture holding a fenced engine import** and driven red.
- **The derivation still returns `batch-shift`** through the command name rather than the snippet,
  and `AGENTS.md` carries no copy of `pdf_engine.REMEDY`.

## What this record does not settle

**Whether any catalog day file mixes text-layer and scanned pages.** Ruling 4 is decided on the
shape of the failure, not on a count.

**Whether 140 DPI is the right resolution**, per ruling 13.

**What a transcription is worth.** Nothing here grades whether an agent read a rendered page
correctly; the clinician's own confirmation at step 4, against quoted first and last lines, is where
a misread shows.

**A consumer with no Python at all.** ADR 0175 leaves that harness's by-eye routes unchanged, and
ruling 10 adds only the disclosure that the corpus did not receive the shift.
