# A composer size refusal is discovered and falls back to an attached document

[#1154](https://github.com/mshamblin5150-code/clinical-skills/issues/1154) owns everything after
[ADR 0190](0190-the-canvas-editor-surface-is-one-shared-route-and-the-reply-prefers-the-raw-editor.md)
ruling 5's route selection on the `canvas-composer` branch: the size refusal, the fallback it
triggers, and which file is graded. [ADR 0221](0221-a-posted-reading-carries-the-fingerprint-of-the-source-it-read.md)
ruling 3 widened it from `practicum-case-study` to every skill posting an **Initial post** through
the Composer. Grilled 2026-09-17; the clinician ruled every point below on the same day. Nothing is
built here; this is the record the build reads.

## Measured before ruling

### The refusal appears only after the submit click

Two NUR 5144 case-study sittings are the whole evidence, both recorded in run directories under
`scratch/` that nothing committed re-derives:

| Sitting | Composer body | Outcome |
| --- | --- | --- |
| Module 2, run dated 2026-09-08 | `post_html.py` output of 73,029 bytes | refused; the clinician read *message size exceeds maximum length* |
| Module 3, run dated 2026-09-10 | about 52,824 editor characters | accepted inline |

The ticket body had dated the Module 2 sitting 2026-09-10; its run key and submission record say
2026-09-08. The two figures are in different units and on different submissions, so they locate no
boundary. In the Module 3 sitting the clinician stated that the message appears only after clicking
Reply. The editor's own state therefore cannot predict the outcome, and the click that discovers a
refusal is the same click that submits an accepted post.

### Four skills post through a Composer and two post a large body

`practicum-case-study` and `discussion-post` load a graded **Initial post** body. `course-assignment`
already attaches its graded deck or document beside short Composer text, and `discussion-reply` loads
a short **Reply** into the threaded Composer. `discussion-post` renders its archival `.docx` without
a page reading; its Canvas-box pixels are the visual check.

## Ruled 2026-09-17

### 1. The limit is discovered by the submit attempt and never predicted

After the clinician's existing submit authorization, the agent clicks Reply on the full body and
reads what Canvas does. The HTML byte count is recorded beside the outcome and branches nothing.
**A byte threshold was declined** on [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s
objection: one refusal and one acceptance, in two units on two submissions, would name a constant at
an edge.

### 2. Only an observed size refusal triggers the fallback

The agent must see Canvas's message-size refusal on the page after the click, and records the wording
it observed with the date. Every other outcome, including an unfamiliar error, no response or an
uncertain result, reads the board for a created entry, reports what it found and stops at the
clinician. **Falling back on any non-success was declined** because a board is append-only for the
clinician and a transient failure could leave a second entry beside one that landed. **Matching the
refusal wording mechanically was declined**: no tool sees the browser, and one sighting of the text is
a dated observation rather than a Canvas contract.

### 3. The fallback takes its own go-ahead

On a size refusal the agent loads the pointer body, attaches the `.docx`, reads back the body text and
the attachment's filename and size from the Composer, shows them to the clinician and waits for an
explicit authorization to submit that entry. **One two-branch authorization before the first click was
declined** because it approves a body and attachment nobody has loaded or read back, and the fallback
changes which file is graded.

### 4. The grader re-derives the posted attachment's bytes

After an attachment post, the agent downloads the attachment from the posted entry's own link into the
run directory under `posted/`. The grader hashes that copy and the local `.docx` and requires equal
SHA-256 digests. A download from the clinician's general files area is not evidence that the entry
carries the file. **A written byte-size comparison was declined** because equal sizes do not establish
equal bytes, and **a recorded digest was declined** because the grader would trust the agent's report
instead of re-deriving it.

### 5. The attached document is visually checked before its go-ahead

`practicum-case-study` keeps rendering and visually checking its `.docx` before submission on every
route, as it already does. `discussion-post` renders the `.docx` pages and obtains a visually checked
verdict only after a size refusal, before ruling 3's go-ahead. **Rendering ahead on every
`discussion-post` route was declined** as a cost paid by every post for a path few take.
[ADR 0210](0210-a-render-pass-and-a-check-record-carry-the-fingerprint-of-what-they-graded.md)'s
fingerprint already refuses a pass that differs from the Markdown.

### 6. The posted reading names the outcome and the graders branch on it

The `## REREAD:` record gains `COMPOSER-OUTCOME:` with the value `inline` or `attachment`, and an
informational `HTML-BYTES:`. On `attachment` it also carries `REFUSAL:` with the date and observed
wording, and `ATTACHMENT:` naming the retained `posted/` copy. The graders grade the HTML's rows on
`inline`, and ruling 4's digest and ruling 5's render on `attachment`. A missing or unrecognized
outcome on a Composer run is not scanned and exits 2; it never reads as `inline`. The fields are
written before `/AAR` extracts the block, like `SUBMISSION-SHA256`. **A separate per-attempt record
was declined** because ruling 2 allows at most one refusal before stopping, and **inferring the outcome
from a `posted/` file was declined** because a missing download would pass as inline.

This does not reopen ADR 0221 ruling 2. `SUBMISSION-SHA256` stays the output Markdown's fingerprint on
both outcomes. That ruling declined a route field that would choose which file is fingerprinted; this
field chooses which rows are graded.

### 7. The mechanics live in the shared sheet and the Initial-post skills opt in

`skills/_shared/reference/canvas-editor.md` carries the refusal recognition, the stop, the fallback
load and readback, the pointer template and the posted-attachment download.
`practicum-case-study` and `discussion-post` opt in. `discussion-reply` states that a size refusal
stops at the clinician with no attachment path, because a Reply that became an attached document
would no longer be a Reply. `course-assignment` states that it already attaches its graded file and
takes no fallback. **Inheriting the fallback in every Composer skill was declined** because whether an
artifact may be graded as an attachment is each calling skill's decision, which the sheet already
leaves to the caller.

### 8. The pointer body is a fixed template, and a bar needing body text stops

The body posted above the attachment is a fixed template held in the shared sheet, carrying the
artifact's title, the attachment filename, and that Canvas refused the full text inline for message
size. It makes no clinical claim and needs no source. When the signed bar requires content in the
post body itself, the fallback cannot meet it and the skill stops at the clinician instead of posting
a pointer. **A per-run authored introduction was declined** because it is unchecked prose published
on an append-only surface.

## Consequences

- `canvas-editor.md` gains the fallback procedure; the four Composer skills gain their opt-in or
  opt-out statements.
- `discussion_artifact.REREAD_FIELDS` and the case study's record template gain the ruling 6 fields,
  and `discussion_post_scan` and `checks_ledger` gain the outcome branch, the posted-attachment digest
  finding, and the exit-2 limb for a missing outcome, each driven by a mismatch, a missing value and a
  clean control.
- `CONTEXT.md` gains **Attachment fallback**.

## What this does not reach

**Whether Canvas refuses by message size at the same point tomorrow.** Every figure here is one
institution, one account and two sittings.

**Whether the posted entry is the one a grader opens.** The download proves the entry carries the
bytes, not how the course's grader views them.

**A refusal of the attachment itself.** An upload size limit or a refused file type is ruling 2's
other outcome and stops at the clinician.
