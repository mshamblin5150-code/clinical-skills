# DOCX branch

Follow this branch only after the live assignment and syllabus establish that the graded artifact
is a Word document. The canonical artifact is the raw `.docx`; Markdown, HTML, and a PDF export are
not substitute submissions. The common course-assignment rules for live reading, source classes,
research/refutation, claim records, voice, private paths, and standing rule 6 remain in force.

## Sign the DOCX bar

Write these fields exactly once at the top of `bar.md`:

```text
ASSIGNMENT: <live assignment URL>
SIGNED: <ISO date after clinician approval>
ARTIFACT: docx
SUBMISSION-TYPE: file-upload
WORD-MIN: <positive integer>
WORD-MAX: none | <positive integer>
REFERENCE-MIN: <positive integer>
SOURCE-CLASSES: <one or more values separated by |>
RECENCY-WINDOW-YEARS: <positive integer>
```

Write one `WORD-MAX` value: the course's positive integer when the live assignment or syllabus
states a ceiling, otherwise `none`. `WORD-MIN` governs the prose body after the title page and
before References; references and captions are outside that count. A numeric course maximum is
transcribed into the bar but never enforced by removing evidence-bearing prose or its qualifiers.
When the course supplies no minimum, resolve `WORD-MIN` to a positive integer with the clinician.
Show the bar to the clinician and wait for explicit confirmation before writing `SIGNED:`.
Run `python tools/course_assignment_scan.py <run-directory> --bar-only`; exit 2 means the signed
envelope or DOCX branch bar was ambiguous, incomplete, or unreadable and production stops.

## Research and author the rich Word artifact

Complete the shared research and refutation pass in the main skill before authoring. Every factual
assertion and decision-changing number in the paper has a `claims.md` record, and every in-text
citation has its own believed record carrying the matching reference. Grade that ledger with
`tools/research_ledger.py` and grade the reference list with `tools/reference_scan.py`; commands save
the walk but do not replace the row contracts written in those tools' invoking skill sections.

Immediately before drafting, run
`python tools/voice_model_identity.py <run-directory> --write`. Read only the
canonical path that command records under the main skill's voice rule. Build the document with
`tools/assignment_docx.py` or its narrow `AssignmentSpec` interface, supplying title-page metadata
from the signed run rather than source-code constants. The title page supports a long credential
line as one fitted line and instructor credentials without embedding personal data in a fixture.
The document uses native Word `Title`, heading, caption, and reference styles; running page numbers;
restrained graphite and blue accents; narrative command relationships; and inline figures with
captions and alt text. The graded body follows the shared `narrative-body` rule in
[style.md](../../_shared/reference/style.md). The visual direction is APA-dominant: no trademarked insignia, brochure
treatment, or invented organizational identity.

Write the selected metadata, sections, command rows, relationship labels, references, and figure
alt text to a private run-unique JSON specification, then run:

```bash
python tools/assignment_docx.py <assignment.json> <docx> [--force]
```

The finished file goes only to
`output/course-assignments/<course>-<module>-course-assignment-<date>.docx`. Run state and image
sources stay under the run directory. The raw `.docx` is canonical after it is written; any later
edit changes its identity and requires a new retained render pass and a fresh review.
The producer refuses an existing document unless `--force` is explicit; recover any human edit
into the authoritative specification before forcing a replacement.

## Grade the DOCX package

This **Grader handoff** under standing rule 6 runs:

```bash
python tools/assignment_docx_scan.py <run-directory> --docx <docx>
```

The grader reads these rows:

- `package-structure`: every required package part, native style, title metadata, running page
  field, caption class, and figure alt text is present.
- `word-range`: the prose body reaches the signed minimum. A numeric `WORD-MAX` is recorded but
  never graded.
- `reference-minimum`: the References section reaches the signed entry floor.
- `reference-defect`: the unchanged shared reference reader found an APA reference defect.
- `claim-ledger`: at least one claim record exists for a paper that makes sourced claims.
- `untraced-number`: a body number appears in no claim heading.
- `untraced-citation`: an in-text citation has no matching claim-record reference.
- `rendered-record`: the final visual record, retained export, page images, highest pass, and raw
  DOCX fingerprint do not form one complete join.
- `narrative-body`: the shared house-style body row is clean.
- Heading-read enforcement uses `missing-heading-read`, `duplicate-heading-read`,
  `unknown-heading-read-route`, `heading-read-sentence-count`,
  `heading-read-unknown-heading`, `heading-read-dropped-heading`,
  `heading-read-draft-mismatch`, `heading-read-defect`, `heading-read-finding`,
  `heading-read-context-digest`, `heading-read-context-verdict-shape`, and
  `heading-read-context-defect`.

Default output is counts only; `--show` exposes private details. Exit 0 is clean, exit 1 is a
finding, and exit 2 means the run was not completely scanned. Independently walk source support,
assignment-specific prose requirements, whether every visual is warranted, and whether the signed
bar faithfully transcribes the live pages; the package grader cannot decide those questions.
If the command is unavailable, walk its named `narrative-body` row against the same body boundary
and the shared style reference; do not restate a second list rule in this branch.

The reader-owned boundaries are in `assignment_docx_scan.DECLARED_LIMITS`:

- `claim-support-unverified`
- `assignment-fit-unverified`
- `visual-purpose-unverified`
- `bar-transcription-unverified`

## Render and inspect every page

Run `python tools/pdf_engine.py`, applying the main skill's install-attempt rule. Then run:

```bash
python tools/assignment_docx_render.py <run-directory> --docx <docx>
python tools/render_scan.py <run-directory>
```

`assignment_docx_render.py` asks a freshly spawned Microsoft Word instance for a page-faithful PDF,
falling through to Word's XPS export only when the PDF route returns a failure. A reached process
bound stops the automated route. The command retains the export and one 120-dpi `page-N.png` per
page in a new `render/pass-N/`, writes the canonical raw file's SHA-256 to
`assignment-docx.sha256`, and retains no partial pass. A run with no Word-produced page-faithful
export stops; a generic office conversion or unbound PDF cannot be called verified.

Run `render_scan.py` to grade readable pixel coverage. A vision-capable **Second reader** opens every
PNG in the highest pass at 100% and compares it with the DOCX and signed bar. It reports clipping,
overlap, broken tables, font substitution, stranded captions, missing content, page-number defects,
and unreadable contrast. Preserve each original finding, repair through the authoring context, and
repeat both the render and the independent read after every change.

The orchestrator writes one final record to `rendered.md`:

```text
## RENDERED: <course>-<module>-course-assignment-<date>.docx
PASS: <positive retained pass number>
PAGES: <read PNG count> of <exported page count> read
SOURCE: word-pdf | word-xps
UNSEEN: none | <what was not read>
READ: <what was compared against the retained pages>
VERDICT: clean - <reason> | defect - <reason>
```

Rerun `assignment_docx_scan.py` after the record is written. It refuses a missing export, a final
record that names an older pass, or a retained `assignment-docx.sha256` that differs from the raw
`.docx` now being graded.

## Review and submit through two gates

Show the clinician the `.docx`, complete reference and claim results, grader counts, every final
page image, and this exact approval surface:

```text
ATTACHMENT-COUNT: <total number of files that will be uploaded>
FILENAME: <one exact basename, repeated once for every file>
```

The reviewed `.docx` is the only approved carrier by default. A review companion remains outside
the upload set unless the clinician explicitly names it before approval. Every revision writes its
retained render passes and review records only in the run directory; another scratch workspace is
work in progress and supplies no approval evidence. Run `python tools/course_assignment_scan.py
<run-directory> --artifact <docx>` before approval and require its pre-upload grade to exit 0.
**Gate 1** is explicit
approval of that exact filename population; it authorizes choosing and staging only those files in
Canvas. Bind that decision with
`assignment_submission.stage(run, docx, artifact_approved=True, approved_carriers=(...))`, which
records every approved filename and SHA-256 plus the attachment count in the run's durable
`submission-gates.json` only after it reruns that clean pre-upload grade against the run directory.
Show `assignment_submission.approval_surface(staged)` and return to Gate 1
if it differs from the approved surface. Before every file-picker action, require
`assignment_submission.upload_is_allowed(staged, candidate)` to be true; a false result refuses the
file. Inspect the staged
filename and Canvas assignment page, then stop again. Gate 1 never authorizes the **Submit
Assignment** click. Per-context scratch paths may be removed after approval is recorded.

From that approval onward, read and apply the shared [run-status.md](run-status.md) contract. End
every reply that touches the open DOCX run with its single `Run status:` line.

**Gate 2** is a separate explicit confirmation given after the staged-file inspection. Immediately
before clicking **Submit Assignment**, confirm that the staged file's SHA-256 still matches Gate 1.
A changed file returns to rendering and Gate 1. Persist the separate decision with
`assignment_submission.confirm(staged, uploaded_carriers=(...), final_confirmation=True)`. Only a true
`assignment_submission.submit_is_authorized(staged)` result after that Gate 2 record authorizes
the click. If the clinician reports that he uploaded the approved DOCX himself, record the route
instead with
`assignment_submission.record_clinician_upload(run, docx, uploaded_carriers=(...))`; this refuses
without the same recorded approval and does not authorize an agent click. In either route, download
and read the posted artifact before continuing. After submission,
read the posted artifact and append the main skill's `## REREAD:` record using the DOCX stem,
including `ATTACHMENT-COUNT:` and one `SUBMITTED-FILE:` for every submitted filename.

Invoke `/AAR` with that stem. Its completion report must say `the after-action review: clean`.
Then run the artifact-aware completion grader:

```bash
python tools/course_assignment_scan.py <run-directory> --artifact <docx> --submission <docx-stem>
```

Completion requires clean research, reference, DOCX, and render scans; a completed independent page
read; Gate 1 and Gate 2 records; a matching posted reread; and a clean after-action review. Remove
every run-unique temporary writer and checker path; report an exact path only if cleanup fails.
