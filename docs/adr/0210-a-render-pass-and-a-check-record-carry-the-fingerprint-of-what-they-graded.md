# A render pass and a check record carry the fingerprint of what they graded

**Measured at:** 3e3a2cdbe33fcf92fb991266abd476e7a31905fc

[#1020](https://github.com/mshamblin5150-code/clinical-skills/issues/1020) was filed by the
after-action review of one `practicum-case-study` run (NUR 5144 Module 2). Its last retained render
pass was taken before the Markdown's final edit and before the submitted `.docx` was written;
`render_scan` exited 0 over it, and the run posted with no retained image of what it posted. Check
records had been banked against a draft still changing. Grilled 2026-09-13; the clinician ruled
every point below on the same day. Freshness gate `STALE` at `42069863`, then `FRESH` at `3e3a2cdb`
after a rebase. Nothing is built here; this is the record the build reads.

The ticket's decision 2, that a visual verdict names its pass, was already ruled by
[ADR 0161](0161-the-deck-and-case-study-render-records-name-the-final-pass-and-route.md) ruling 7 and
is built for the rendered-document record. It needs nothing further. Decisions 1 and 3 are ruled here.

## Measured before ruling

### The `.docx` hash moves on every re-render; its Word content does not

`tools/docx_write.py` was run twice on `skills/_shared/reference/apa7.md`, two seconds apart. Every
archive part was byte-identical, and the two archives hashed differently, because the zip stamps each
entry with its write time. *Had the renderer been byte-deterministic, the two file hashes would have
been equal.* So a fingerprint of the `.docx` file expires on a harmless re-render, while a comparison
of `docx_write.parts(markdown)` against the archive's parts is exact.

### The only pass check runs after the post

`checks_ledger.py` compares the rendered-document record with the retained passes only under
`--submission`, which `practicum-case-study` runs after the post, the re-read and `/AAR`. The
pre-go-ahead run names no document and reads no pass. A byte check added only there could record
Module 2's defect and could not have stopped it.

### A clinician's PDF cannot be tied to its `.docx` by text

The repository's own `word_export.ps1` exported `apa7.md` (59 pages), a copy with one number changed,
and a copy with one word deleted. Word sequences from the PDF's text layer were compared with
`docx_read.py`'s text of each `.docx`:

| PDF | `.docx` | differing tokens |
| --- | --- | --- |
| original | original | 71 |
| original | one number changed | 72 |
| original | one word deleted | 72 |

A correct export already differs by 71 tokens: numbers and words split across lines, numbering markers
Word draws, and words the text layer drops. An edit adds one. *Had text been a usable binding, the
first row would have read 0.* No exact rule accepts a correct export, and no measured cut separates 71
from 72. The clinician has also never used the manual export route; he has edited the `.docx` and said
so.

### The deck has no source behind its `.pptx`

`skills/course-assignment/SKILL.md` has the authoring agent write the `.pptx`; nothing in the
repository writes or rebuilds one, and the `.pptx` is the submitted file. `deck_scan.py` already takes
`--pptx` on its pre-go-ahead run, matches `rendered.md` to the deck by filename only, and does not read
`adversarial.md`.

### There is no shared file-digest helper

`day_file_text._digest`, `guidelines_build._raw_file_identity` and `uptodate_store._sha256` are three
private copies of the same streamed SHA-256. `artifact_provenance.text_file_identity` is public and
normalizes line endings, which is wrong for a binary archive.

## Ruled 2026-09-13

### 1. A case study's source fingerprint is of its Markdown, and the render refuses a `.docx` that is not its rendering

The fingerprint is the SHA-256 of the output Markdown, the file `practicum-case-study` step 8 already
calls authoritative. Before exporting, `case_study_render.py` rebuilds `docx_write.parts()` from the
Markdown beside the named `.docx` and refuses, exit 2, when any archive part differs. That refusal is
the answer to the ticket's question of whether a render may follow a failed write: in Module 2 the
23:21 pass would have been refused. A `.docx` edited in Word, or written by an older renderer, is
refused until the edit is recovered into the Markdown and re-rendered, which is what step 8 already
directs. A `.docx`-file fingerprint and a pair of fingerprints were declined as explained under
*Rejected options*.

### 2. The render command writes the fingerprint into each pass as it keeps it

`case_study_render.py` writes the fingerprint to a file inside the staged pass before
`render_pass.retain_staged_pass` renames it, so a retained pass cannot exist without one. The file name
is the producer's, behind ADR 0124 ruling 3's globbed shape; every current reader globs only `*.png`
and one `.pdf` or `.xps`, so the extra file changes no count. This supersedes ADR 0161 ruling 5 for
this value only. That ruling's objection was that a route label in the pass proves nothing; a
fingerprint is computed from bytes that ruling 1's check has already tied to the `.docx`. The route
stays out of the pass. It also supersedes
[ADR 0098](0098-the-case-study-s-rendered-document-coverage-is-derived-from-kept-evidence-and-owned-by-its-own-run-directory-grader.md)
ruling 3, as ADR 0161 already superseded it for a directory listing, to the extent `checks_ledger`
now reads one file inside the newest pass.

### 3. `checks_ledger` refuses before the go-ahead and repeats at submission

The pre-go-ahead run gains `--document <output Markdown>`. With it, `checks_ledger.py` returns a
finding, exit 1, when:

- no render pass is retained;
- the rendered-document record's `PASS` does not name the highest retained pass;
- the highest pass's fingerprint differs from the named Markdown's.

The `--submission` run repeats all three, locating the Markdown from the dated stem under
`output_root()`. The check reads files only, so it runs on the machine ADR 0175 ruling 1 leaves
without the PDF engine. `render_scan.py` keeps grading page coverage alone. Its declared behavior row
*whether the graded pass shows the submitted document* stays true of that command, and is repointed
from #1020 to this check. Its control
`test_a_complete_pass_beside_a_different_document_is_counted` is retired with the repointing, and the
refusals above carry their own tests. `checks_ledger`'s `render-document-bytes-unbound` row retires.

### 4. A pass with no fingerprint is refused like a mismatch

A highest retained pass without the fingerprint file is the same finding as a mismatch, and the
message directs a re-render into a new pass number. There is no cutoff date: a finished run is never
graded again, `checks_ledger` does not run in CI, and a run in flight when this lands pays one
re-render.

### 5. On the clinician's export route the `.docx` is bound and the PDF is declared

Ruling 1's check still runs on the `.docx` named by `--docx`, and the fingerprint is still written.
Nothing ties the clinician's PDF to that `.docx`; the measurement above shows text cannot, and the
record's `SOURCE: clinician` already names the route. A declared limit says so. Nothing is built for
a route never used.

### 6. A check record read against another draft is refused and re-run

Before the go-ahead, and again at submission, any `## CHECK:` record whose recorded draft fingerprint
differs from the named Markdown's is a finding. Every such row is re-run. A late one-word fix therefore
re-runs every reader row, which is automated work; reporting the stale records instead, or re-running
only rows the parent judges affected, leaves this ticket's section 3 standing.

### 7. The parent writes `DRAFT:` from a command run at dispatch, on every record

Every record carries `DRAFT: <SHA-256>`, including the rows filled from a command's output. The
parent, which is already the one writer of the checks file, computes it with a command when it sends
the reader off, names it in the brief, and writes it into the record. A draft changed during the read
leaves the record naming the old fingerprint, so ruling 6 refuses it with no further mechanism. This
binds a verdict to a draft; the declared limit that a reader's work is unobservable is unchanged. One
public file-digest helper serves this, ruling 2 and ruling 9, and replaces the three private copies.

### 8. Only the draft is bound

`claims.md`, `evidence.txt`, the faculty material and committed threshold sheets carry no fingerprint
in a record. A declared limit says a record is bound to the draft alone. The one plausible stale path,
a ledger correction to a dose, ends in a draft edit that ruling 6 already catches.

### 9. The deck gets the render binding on the `.pptx` bytes

`deck_render.py` writes the SHA-256 of the `.pptx` into each pass as ruling 2 describes, and
`deck_scan.py --pptx` makes ruling 3's three pass refusals before the go-ahead and again at
`--submission`, treating a missing fingerprint as ruling 4 does. Nothing re-renders a `.pptx` from a
source, so the timestamp problem in ruling 1 does not arise. `deck_scan`'s `render-document-bytes-unbound`
row retires. `adversarial.md` stays ungraded, and a declared limit says it is not bound to the deck's
bytes.

### 10. `--document` is required on the pre-go-ahead run

`checks_ledger.py` run without `--submission` and without `--document` exits 2, did not scan, and names
the missing argument. The `practicum-case-study` step 9 command gains the argument. An optional
argument printing `not graded` would leave exit 0 over the stale-verdict case this ticket exists for.

## Rejected options

**Fingerprint the `.docx` file.** It expires on every re-render of unchanged Markdown and never asks
whether the `.docx` matches the Markdown, which is how Module 2's refused write passed.

**Record the fingerprint in the rendered-document record, or once per run.** A value an agent copies
into `checks.md` proves it was copied. One run-level file, the day-file shape of
[ADR 0181](0181-a-day-file-reaches-the-corpus-through-one-command-and-a-rendered-page-waits-for-a-reading.md)
ruling 7, cannot say which draft produced which of several passes.

**Compare only at `--submission`, or in `render_scan`.** The first runs after the post. The second runs
before the draft stops changing and exits 2 without the PDF engine.

**Excuse old passes by date.** Nothing old is graded again.

**Bind the clinician's PDF by text or page count.** Text is 71 tokens of noise before an edit's one;
page count misses a same-length edit, which is Module 2's.

**Fingerprint `claims.md` and `evidence.txt` per row, or all inputs in one value.** Per row adds fields
and a grader table for a path no run has shown; one combined value re-runs every reader on a ledger
edit none of them read.

**Grade `adversarial.md` in this change.** It widens `deck_scan` into a record it does not read today.

## What none of this reaches

Whether a reader read what it recorded. Whether the clinician's own PDF shows the `.docx`. Whether a
verdict went stale through `claims.md` or the evidence alone. Whether the LMS holds the bytes that were
fingerprinted; the posted-upload readback is
[#1154](https://github.com/mshamblin5150-code/clinical-skills/issues/1154)'s. Whether a draft changed and
changed back to identical bytes during one read, which leaves the reader's draft the final one.
