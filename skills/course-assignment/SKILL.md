---
name: course-assignment
description: Read one live course assignment, sign its deck or DOCX bar, research and produce the requested artifact, independently grade and render it, and submit only after clinician approval.
---

# Course assignment

Use this skill for a graded course assignment whose prompt declares the artifact it wants and
which is not already owned by `discussion-post` or `practicum-case-study`. The accepted signed
artifact values are `ARTIFACT: deck` and `ARTIFACT: docx`; an ambiguous, duplicate, or different
value stops before production. For `docx`, read and follow the complete
[DOCX branch](references/docx.md). The deck branch remains below. The common dispatcher is
`tools/course_assignment_scan.py`; it reads the signed artifact once and hands the run to the
matching deep grader.

The clinician signs the bar before research or production, reads the finished deck, and gives the
explicit go-ahead before upload. Permission to read, research, produce, grade, or render is not
submission permission.

## Inputs, outputs, and run identity

The input is the live LMS assignment URL in the clinician's signed-in browser. Read the course and
module breadcrumbs rather than typing them from memory. The fixed artifact word is
`course-assignment`, giving this private run directory:

```text
scratch/runs/<course>-<module>-course-assignment/
    assignment-<date>.md
    bar.md
    claims.md
    intent.md
    adversarial.md
    rendered.md
    submission.md
    submission.html
    submission-readback.html
    render/pass-N/
```

Each sitting writes a new assignment snapshot. Never overwrite an earlier one. The finished artifact
goes only to `output/course-assignments/<course>-<module>-course-assignment-<date>.pptx` or the same
stem ending in `.docx`, according to the signed branch. Images used
to author it stay in the run directory unless they are already durable public assets. Parallel
research, refutation, adversarial, and checking contexts each receive a new run-unique private
path. They return findings to the orchestrator, which alone writes the canonical run files, and
standing rule 6 governs independent checks and cleanup.

## 1. Read the live assignment and establish the bar

Read the assignment prompt, point value, due date, submission type, upload types, linked examples, rubric, and every
stated artifact rule. Follow links and report access failures rather than treating an unread link
as evidence. Open the course syllabus and read any assignment-wide requirements. The assignment
page overrides the syllabus on the same element; the syllabus fills silence. Record any conflict
or ambiguous precedence for the clinician instead of choosing silently.

Write the page language verbatim as block quotes in `assignment-<date>.md`, with its URL and read
date. Then write these mechanical fields exactly once at the top of `bar.md`:

```text
ASSIGNMENT: <live assignment URL>
SIGNED: <ISO date after clinician approval>
ARTIFACT: deck
SUBMISSION-TYPE: file-upload | canvas-composer
SLIDE-MAX: <integer>
SLIDE-LIMIT-SCOPE: all | content
BULLETS-PER-SLIDE: <integer>
WORDS-PER-BULLET: <integer>
FONT-POINTS: <integer>
FONT-DIRECTION: ceiling | floor
AUDIENCE-PURPOSE: <the assignment's audience-facing purpose>
TALK-STYLE: <the clinician-confirmed presentation style>
SOURCE-CLASSES: <one or more values separated by |>
RECENCY-WINDOW-YEARS: <positive integer>
```

Write one `SUBMISSION-TYPE` and one `SLIDE-LIMIT-SCOPE` value, not the alternatives shown above.
Use `content` only when the assignment excludes reference slides from its stated maximum; otherwise
use `all`. `AUDIENCE-PURPOSE` records what the presentation must do for its audience, and
`TALK-STYLE` records the clinician-confirmed way it should sound. Below
the fields, copy the relevant assignment and syllabus wording and record the precedence decision.
Then show `bar.md` to the clinician and wait for explicit confirmation that the transcription,
direction, slide-limit scope, audience purpose, talk style, source classes, recency window,
submission type, and precedence are right. Only then write `SIGNED:` and
continue. A missing field is not a default: both graders exit 2 because the run was not scanned.

The source-class vocabulary is `society guideline`, `peer-reviewed`, `government`,
`tertiary reference`, and `market source`. The bar selects the subset this artifact permits. A
clinical claim does not become sourceable from a commercial listing merely because a deck in
another run signed `market source`. `FONT-DIRECTION` is a signed reading of the professor's rule;
the grader does not decide whether that reading was correct.

## 2. Research before production

Derive the claim set from the assignment and planned deck. Include every factual assertion and
every figure that may appear on a slide or in speaker notes. Create `claims.md` with a
`DATE:` header and one `## CLAIM:` record per claim:

```text
## CLAIM: <claim, including the exact numeric token when it is numeric>
STATUS: sourced | unsourced | unreadable - <what was searched or what prevented the read>
SOURCE: <one class signed in bar.md>
REFERENCE: <full reference entry>
RESTATEMENT: <what the source says, including a number for a numeric claim>
PASSAGE: <where in the source the supporting language sits>
RECENCY: current | within five | nothing newer - <reason> | guideline in force - <reason>
RESOLVED: <URL or DOI> - read <ISO date>
PAGE-YEAR: <year and where the page states it>
REFUTATION: stands | refuted | paywalled | unreadable - <substantive reason>
TESTED-HEADING: <SHA-256 printed for this heading at refuter dispatch>
SECOND-ROUTE: <research route> -> <different refutation route>
INSTRUMENTS: <first instrument> -> <second instrument>
STATED-EXPIRY: none stated | <ISO date> - <where stated> | <ISO date>, superseded cited deliberately - <reason>
```

Apply the shared sourcing rules below to `unsourced` and `unreadable` records. `INSTRUMENTS` is
also required for `REFUTATION: unreadable` and forbidden elsewhere. Research produces claim records.
This **Fan-out brief** applies [standing rule 6](../../AGENTS.md). Every research and refutation
brief first reads and applies
[sourcing.md](../_shared/reference/sourcing.md).
Each refutation leg attacks the reference, locator, year, bibliographic details, heading, and restatement. It returns
`stands`, `refuted`, `paywalled`, or `unreadable` with a reason and a genuinely different second route. The
route requirement is a local narrowing.
Immediately before each refutation dispatch, run `python tools/research_ledger.py
scratch/runs/<course>-<module>-course-assignment/claims.md --heading-digests`, name that claim's
printed digest in the brief, and write it as `TESTED-HEADING` with the returned verdict and route.

If the clinician's profile says an available research agent has an authenticated route, that agent
must try it before giving up on retrieval. An authenticated-route failure is evidence, not a
substitution for the required record; when no source can be recovered, preserve `STATUS: unsourced`
and remove the unsupported claim from the deck.

After those two passes, this **Grader handoff** under [standing rule 6](../../AGENTS.md) runs:

```bash
python tools/research_ledger.py scratch/runs/<course>-<module>-course-assignment/claims.md
```

Exit 0 means the signed source vocabulary, signed recency window, and record shapes passed. Exit 1
means a finding. Exit 2 means the ledger or its signed bar was not completely scanned. The full
coverage inventory is `research_ledger.DECLARED_LIMITS`; the source-support judgment remains a
reader's work.

## 3. Produce the deck

Immediately before drafting the first prose, write and confirm the project declaration, retrieve
every place owed by [sourcing.md](../_shared/reference/sourcing.md), then run both gates:

```bash
python tools/project_context.py scratch/runs/<course>-<module>-course-assignment --write
python tools/voice_model_identity.py scratch/runs/<course>-<module>-course-assignment --write
```

The project-context command must exit 0. An unregistered project stops for the clinician's answer;
an unreachable place stops until it is readable or the clinician confirms its waiver. A later
search direction amends and re-confirms `project-context.md` before any prose resumes.

Read only the path the identity command reports and use its reflective or argumentative register.
If the command reports the existing absent-model banner, follow
[voice.md](../_shared/reference/voice.md)'s no-model rule; the machine-written identity record keeps
that state in the private run directory. Any other nonzero result refuses drafting. Generate the
`.pptx` agent-side. Do not build or call a repository PowerPoint writer. Keep the
slide face within the signed container and put the supporting narrative in speaker notes. Speaker
notes are outside the projected 6x6 container and inside the claim surface because the clinician
may say them to the audience.

A generated image may depict a concept, and a visible caption must call that space conceptual. A
generated image must never stand in for the actual site. Use a real site photograph where the
slide claims the actual site. This is a reader-owned convention, not something the file can prove.

## 4. Grade the PowerPoint package

This **Grader handoff** under [standing rule 6](../../AGENTS.md) runs:

```bash
python tools/deck_scan.py scratch/runs/<course>-<module>-course-assignment --pptx output/course-assignments/<course>-<module>-course-assignment-<date>.pptx
```

The container population is the slide face alone. A title is not a bullet; every non-title text
paragraph is counted as one. The claim population is the slide face and speaker notes together.
The rows are:

- `slide-count`: one finding when the population named by `SLIDE-LIMIT-SCOPE` exceeds `SLIDE-MAX`.
- `bullets-per-slide`: one finding for each slide exceeding `BULLETS-PER-SLIDE`.
- `words-per-bullet`: one finding for each non-title paragraph exceeding
  `WORDS-PER-BULLET`.
- `font-points`: one finding for each slide carrying an unmeasured font run or a run violating the
  signed `FONT-POINTS` in the signed `FONT-DIRECTION`.
- `untraced-figure`: one finding for each distinct figure on a slide or in speaker notes that
  appears in no believed claim-record heading. Citation years, page locators, and statute numbers
  are excluded.
- `rendered-record`: one finding for each malformed record or failed terminal join to the deck,
  highest retained pass, slide count, PNG count, unseen count, or clean visual verdict.
- `adversarial-record`: one finding for each malformed record or failed join to the final deck,
  highest retained pass, slide count, PNG count, unseen count, clean verdict, or current `claims.md`.
- `presentation-intent-record`: one finding for a missing or malformed `intent.md`, a stale deck
  digest, a slide population that is not a complete partition, a purpose or style that differs from
  the signed bar, exposed internal revision commentary, or a spoken arc without a reasoned
  `follows` verdict.
- `submission-fingerprint`: one finding when the terminal posted-reading record is missing its fingerprint
  or its fingerprint does not match the submitted `.pptx`.
- Heading-read enforcement uses `missing-heading-read`, `duplicate-heading-read`,
  `unread-heading-read`, `unknown-heading-read-route`, `heading-read-sentence-count`,
  `heading-read-unknown-heading`, `heading-read-dropped-heading`,
  `heading-read-draft-mismatch`, `heading-read-defect`, `heading-read-finding`,
  `heading-read-context-digest`, `heading-read-context-verdict-shape`, and
  `heading-read-context-defect`.

The default report prints counts only. `--show` exposes artifact text and remains private. Exit 0
is clean, 1 means a finding, and 2 means the command did not completely scan the run, bar, or deck.
The command's reader-owned boundaries are in `deck_scan.DECLARED_LIMITS`. Walk that object against
the finished artifact; this skill points to it and carries no second copy of its inventory.

## 5. Render and inspect every slide

Before the render and coverage commands, run:

```bash
python tools/pdf_engine.py
```

On exit 1, ask the clinician for permission to run the install line the check printed and run the
check again after an attempted install. If permission is declined or the install fails, walk the
retained-render and coverage rules below by eye. Exit 2 from the check does not establish that the
engine is missing and stops this step for investigation.

Run the retained render pass after the package scan:

```bash
python tools/deck_render.py scratch/runs/<course>-<module>-course-assignment --pptx output/course-assignments/<course>-<module>-course-assignment-<date>.pptx
python tools/render_scan.py scratch/runs/<course>-<module>-course-assignment
```

`deck_render.py` asks a freshly spawned PowerPoint for one page-faithful PDF, then rasterizes it to
one 120-dpi PNG per slide in a new `render/pass-N/` above the highest retained number. A failed
route retains no pass. Before retaining the pass it computes the raw-byte SHA-256 of the `.pptx`
and writes it to `deck.sha256` inside that pass.
If PowerPoint cannot export, ask the clinician for a clinician-supplied PDF and rerun with
`--clinician-export <PDF>`; PowerPoint is the fast path and never the only path.

`render_scan.py` reads pass directories whose number is an ASCII positive integer with no leading
zero, the retained export's page count, and readable PNGs. Earlier passes remain counted evidence;
only the last pass must contain exactly one readable image for every exported page. Fewer or more
final images than exported pages is exit 1. No measurable retained export is exit 2. The gap count is
reported on every run and never graded.

The engine-reaching grader must exit 0 unless this run's engine check reported the engine missing
and the install did not happen. Only in that case may its exit 2 be accepted; report that the run is
not mechanically verified and that the retained-render and coverage rows were walked by eye. A
finding still stops the run.

This vision-capable **Second reader** under [standing rule 6](../../AGENTS.md) opens every PNG in
the final pass and compares it with the
deck and signed bar. It reports clipping, overflow, overlap, unreadable contrast, missing or
misplaced text, broken images, and any generated site image or conceptual image lacking its
caption. A package scan cannot substitute for this visual read. Preserve the original finding and
repair through the authoring context; the correction takes the same Second reader surface.

The orchestrator writes each visual reader's result to `rendered.md`, one record per
read pass:

```text
## RENDERED: <course>-<module>-course-assignment-<date>.pptx
PASS: <positive retained pass number>
SLIDES: <read PNG count> of <deck slide count> read
SOURCE: powerpoint-pdf | clinician
UNSEEN: none | <what was not read>
READ: <what was compared against the retained slide images>
VERDICT: clean - <reason> | defect - <reason>
```

Every package scan grades this record's shape when the file exists. At the terminal call, the
record must name the output deck and highest retained pass, all deck slides must have retained PNGs,
and `UNSEEN` must be `none` with a reasoned clean verdict. Earlier retained passes need no record;
the report counts them without grading their absence.

After that visual read, give a fresh **Second reader** under [standing rule 6](../../AGENTS.md) the
signed `bar.md`, the final `.pptx` including speaker notes, and every PNG in the highest retained
pass. The reader classifies slides by their audience job, checks every audience-facing slide and
speaker-note sentence for internal revision commentary, and compares the final spoken arc with the
signed audience purpose and talk style. Content and reference populations must partition every deck slide exactly once.
Write the result to `intent.md`:

```text
## PRESENTATION-INTENT: <course>-<module>-course-assignment-<date>.pptx
DRAFT: <SHA-256 of the output .pptx>
CONTENT-SLIDES: <comma-separated slide numbers> | none
REFERENCE-SLIDES: <comma-separated slide numbers> | none
AUDIENCE-PURPOSE: <exact value from bar.md>
TALK-STYLE: <exact value from bar.md>
INTERNAL-COMMENTARY: none | found - <slide and commentary>
SPOKEN-ARC: follows - <reason> | departs - <reason>
```

`INTERNAL-COMMENTARY: found` and `SPOKEN-ARC: departs` are findings, not alternative clean states.
The reader's reason explains how the order and close realize or miss the signed direction; a bare
`follows` is not a verdict. `DRAFT` binds this reading to the PowerPoint bytes, so any deck repair
requires a fresh presentation-intent read.

The adversarial investor reader first reads and applies
[sourcing.md](../_shared/reference/sourcing.md). After the visual read, give this fresh
**Second reader** under [standing rule 6](../../AGENTS.md) only the highest retained pass's PNGs,
the final speaker-note text from the output `.pptx`, and `claims.md`. The orchestrator computes
`file_digest.sha256` of `claims.md` when briefing the reader and names that digest in the brief.
The reader attacks the rendered artifact for records that do not exist. It also compares each slide
with the believed records behind it and reports when a figure or assertion's value or sense differs
from the claim heading, when a record qualifier is absent, or when a record heading no longer
matches the slide text it sources. For this check, a qualifier appears on the same slide face as its
claim; speaker notes do not satisfy the qualifier. If the condition cannot fit the signed bullet
limit, move or split the claim. It reads as the investor named by the assignment and returns every
unsupported assertion and agreement finding keyed to slide number for `adversarial.md`. Correcting a
stale heading creates a new claim under ADR 0208 ruling 3. Research, Refutation, and this
adversarial read have three distinct subjects, and each may fail while the other two pass. Add
records for supported claims or remove the assertions; never convert a miss into an unrecorded hedge.

The orchestrator writes one `adversarial.md` record per read:

```text
## ADVERSARIAL: <course>-<module>-course-assignment-<date>.pptx
PASS: <positive retained pass number>
SLIDES: <read PNG count> of <deck slide count> read
UNSEEN: none | <what was not read>
CLAIMS: <SHA-256 of claims.md when the reader was briefed>
VERDICT: clean - <reason> | defect - <reason>
<findings keyed to slide number>
```

Before the go-ahead, this fresh **Second reader** under [standing rule 6](../../AGENTS.md) receives only the final `.pptx` (including its slide
bullets and speaker-note sentences), `claims.md`, and the printed heading digests. Do not give it
sources. It writes the shared `## HEADING-READ: <deck>.pptx` record from
[sourcing.md](../_shared/reference/sourcing.md) to `<run-directory>/heading-read.md`; locations name
slide bullets and speaker-note sentences. Repair every `unrecorded` or `drifted` finding and repeat
the read after any repair. With no second context, write `ROUTE: orchestrator walk`. Rerun
`deck_scan.py --pptx <deck>`; it refuses a missing record, a stale deck digest, or a pair to an old
heading before the go-ahead.

Both this scan and the terminal `--submission` scan require a current clean presentation-intent
record and a clean adversarial record naming the highest retained pass and current `claims.md`.
They also refuse a missing retained pass, a rendered record naming another pass, a missing
`deck.sha256`, or a fingerprint that differs from the named `.pptx`. A deck repair returns to
`deck_render.py` and repeats the visual, presentation-intent, adversarial, and heading reads on the
new pass. A `claims.md`-only repair returns to the adversarial read, followed by the heading read
and `deck_scan.py --pptx <deck>`.

## 6. Approve, submit, and reread

Branch on the signed `SUBMISSION-TYPE` before preparing the LMS carrier:

- For `file-upload`, the carrier is the finished `.pptx`; the shared Canvas sheet does not trigger.
- For `canvas-composer`, write the exact deck-accompanying text to `submission.md`, render it to
  `submission.html` with `python tools/post_html.py <submission.md> <submission.html>`, read
  [canvas-editor.md](../_shared/reference/canvas-editor.md), and select its first supported **Load
  route** before loading. A Composer-only prose assignment is not the supported deck artifact and
  stops this skill.

Show the clinician the finished deck, notes, presentation-intent record, adversarial report, grader counts, final rendered
slides, submission type, and this exact carrier approval surface:

```text
ATTACHMENT-COUNT: <total number of files that will be uploaded>
FILENAME: <one exact basename, repeated once for every file>
```

The finished `.pptx` is the only approved carrier by default. A review companion is excluded by
default and remains outside the upload set unless the clinician explicitly names it before
approval; merely creating or showing that companion never adds it. For a Canvas Composer, also
show the selected route and its cost.
This is the existing submission gate; wait for the explicit go-ahead once. Then call
`assignment_submission.stage(run, deck, artifact_approved=True, approved_carriers=(...))` with
exactly the approved files and show `assignment_submission.approval_surface(staged)`. Any mismatch
with the surface the clinician approved returns to the gate.

Before each file-picker action, require
`assignment_submission.upload_is_allowed(staged, candidate)` to be true. A false result refuses
that file; never widen the approved set during upload. For `file-upload`, upload the approved files
and inspect the LMS submission page before committing the action. For `canvas-composer`, load `submission.html` through the declared route, attach the `.pptx`
when the live assignment requires it, and serialize the Composer HTML to
`submission-readback.html`. Compare the built and serialized HTML as the shared sheet requires. A
non-clean comparison stops and returns to the clinician; do not switch routes or retry the load.
This skill already attaches its graded deck or document as the selected carrier and takes no
Initial-post attachment fallback after a Composer size refusal. Read the LMS for a created entry,
report the refusal and what was found, and stop at the clinician.
Pass the inspected filename population to
`assignment_submission.confirm(staged, uploaded_carriers=(...), final_confirmation=True)` and
require `assignment_submission.submit_is_authorized(staged)` immediately before submitting.
Then submit and read the posted artifact back from the LMS. Append this exact record to
`reread.md`, using the output deck stem as the heading on both submission branches:

```text
## REREAD: <deck stem>
POST-URL: <the submitted artifact's LMS URL>
POSTED: <the LMS's posted timestamp>
READ: <ISO date of this reading>
ATTACHMENT-COUNT: <submitted file count>
SUBMITTED-FILE: <submitted basename, repeated once for every submitted file>
SUBMISSION-SHA256: <SHA-256 of the output .pptx>
VERDICT: matches - <whether the submitted filename population, carrier bytes, and deck match>
```

Use `diverges - <what differs>` when the posted artifact does not match. A divergence stops the
completion path for clinician direction.

Compute the fingerprint with `python -c "from pathlib import Path; from tools.file_digest import sha256; print(sha256(Path(r'<output .pptx>')))"` and write it before `/AAR`
extracts the record; adding or changing the line afterwards makes that review stale because
`aar_scan` fingerprints the whole block. Invoke `/AAR`
with the output deck stem as the submission key. Its completion report must say
`the after-action review: clean`. Completion requires clean final
ledger, deck, and render scans, a walk of `deck_scan.NOT_REACHED`, a completed visual comparison, the clinician's submission approval,
the posted reading, and the after-action review. Keep the signed bar, snapshots, claims,
presentation-intent and adversarial results, Composer files when present, and retained render passes together under the run directory. Remove every
temporary per-context path; if cleanup fails, report the exact remaining path.

After `/AAR` is clean, run the artifact-aware completion grader with that same deck stem:

```bash
python tools/course_assignment_scan.py <run-directory> --artifact <deck> --submission <deck-stem>
```
