---
name: course-assignment
description: Read one live course assignment, sign its artifact-specific bar, research and produce the requested artifact, independently grade and render it, and submit only after clinician approval. The only supported artifact is a PowerPoint deck.
---

# Course assignment

Use this skill for a graded course assignment whose prompt declares the artifact it wants and
which is not already owned by `discussion-post` or `practicum-case-study`. On day one the only
accepted artifact is a PowerPoint deck: write `ARTIFACT: deck`. The deck is the only accepted value;
do not invent `paper`, a dispatcher branch, or a second grader. The authoring agent produces the
`.pptx` and any images. This repository reads and grades the file; it does not write PowerPoint.

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
    adversarial.md
    render/pass-N/
```

Each sitting writes a new assignment snapshot. Never overwrite an earlier one. The finished deck
goes only to `output/course-assignments/<course>-<module>-course-assignment-<date>.pptx`. Images used
to author it stay in the run directory unless they are already durable public assets. Parallel
research, refutation, adversarial, and checking contexts each receive a new run-unique private
path. They return findings to the orchestrator, which alone writes the canonical run files, and
standing rule 6 governs independent checks and cleanup.

## 1. Read the live assignment and establish the bar

Read the assignment prompt, point value, due date, upload types, linked examples, rubric, and every
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
SLIDE-MAX: <integer>
BULLETS-PER-SLIDE: <integer>
WORDS-PER-BULLET: <integer>
FONT-POINTS: <integer>
FONT-DIRECTION: ceiling | floor
SOURCE-CLASSES: <one or more values separated by |>
RECENCY-WINDOW-YEARS: <positive integer>
```

Below the fields, copy the relevant assignment and syllabus wording and record the precedence
decision. Then show `bar.md` to the clinician and wait for explicit confirmation that the transcription,
direction, source classes, recency window, and precedence are right. Only then write `SIGNED:` and
continue. A missing field is not a default: both graders exit 2 because the run was not scanned.

The source-class vocabulary is `society guideline`, `peer-reviewed`, `government`,
`tertiary reference`, and `market source`. The bar selects the subset this artifact permits. A
clinical claim does not become sourceable from a commercial listing merely because a deck in
another run signed `market source`. `FONT-DIRECTION` is a signed reading of the professor's rule;
the grader does not decide whether that reading was correct.

## 2. Research before production

Derive the claim set from the assignment and planned deck. Include every factual assertion and
every costed figure that may appear on a slide or in speaker notes. Create `claims.md` with a
`DATE:` header and one `## CLAIM:` record per claim:

```text
## CLAIM: <claim, including the exact numeric token when it is numeric>
STATUS: sourced | unsourced - <what was searched>
SOURCE: <one class signed in bar.md>
REFERENCE: <full reference entry>
RESTATEMENT: <what the source says, including a number for a numeric claim>
RECENCY: current | within five | nothing newer - <reason> | guideline in force - <reason>
RESOLVED: <URL or DOI> - read <ISO date>
PAGE-YEAR: <year and where the page states it>
REFUTATION: stands | refuted | paywalled - <substantive reason>
SECOND-ROUTE: <research route> -> <different refutation route>
STATED-EXPIRY: none stated | <ISO date> - <where stated> | <ISO date>, superseded cited deliberately - <reason>
```

For `unsourced`, state what was searched on `STATUS` and omit every source field. Research produces claim records.
Refutation attacks each record that exists in a different context and
tries to disprove the reference, locator, year, bibliographic details, and restatement. It returns
`stands`, `refuted`, or `paywalled` with a reason and a genuinely different second route. The
orchestrator alone writes the records.

If the clinician's profile says an available research agent has an authenticated route, that agent
must try it before giving up on retrieval. An authenticated-route failure is evidence, not a
substitution for the required record; when no source can be recovered, preserve `STATUS: unsourced`
and remove the unsupported claim from the deck.

After those two passes, a fresh checker runs:

```bash
python tools/research_ledger.py scratch/runs/<course>-<module>-course-assignment/claims.md
```

Exit 0 means the signed source vocabulary, signed recency window, and record shapes passed. Exit 1
means a finding. Exit 2 means the ledger or its signed bar was not completely scanned. The full
coverage inventory is `research_ledger.DECLARED_LIMITS`; the source-support judgment remains a
reader's work.

## 3. Produce the deck

Read `scratch/voice-model.md` and use its reflective or argumentative register. If it is absent,
follow [voice.md](../practicum-case-study/reference/voice.md)'s no-model rule and keep the resulting
status in the private run record. Generate the `.pptx` agent-side. Do not build or call a repository PowerPoint writer. Keep the
slide face within the signed container and put the supporting narrative in speaker notes. Speaker
notes are outside the projected 6x6 container and inside the claim surface because the clinician
may say them to the audience.

A generated image may depict a concept, and a visible caption must call that space conceptual. A
generated image must never stand in for the actual site. Use a real site photograph where the
slide claims the actual site. This is a reader-owned convention, not something the file can prove.

After the deck exists, give only the rendered slide images, the speaker-note text, and `claims.md`
to a fresh adversarial context. The adversarial pass attacks the rendered artifact for records that do not exist.
It reads as the investor named by the assignment and returns every unsupported
assertion keyed to slide number. The orchestrator writes the result to `adversarial.md`. Research,
Refutation, and this adversarial read have three distinct subjects, and each may fail while the
other two pass. Add records for supported claims or remove the assertions; never convert a miss
into an unrecorded hedge.

## 4. Grade the PowerPoint package

A fresh non-authoring context runs:

```bash
python tools/deck_scan.py scratch/runs/<course>-<module>-course-assignment --pptx output/course-assignments/<course>-<module>-course-assignment-<date>.pptx
```

The container population is the slide face alone. A title is not a bullet; every non-title text
paragraph is counted as one. The claim population is the slide face and speaker notes together.
The rows are:

- `slide-count`: one finding when the deck exceeds `SLIDE-MAX`.
- `bullets-per-slide`: one finding for each slide exceeding `BULLETS-PER-SLIDE`.
- `words-per-bullet`: one finding for each non-title paragraph exceeding
  `WORDS-PER-BULLET`.
- `font-points`: one finding for each slide carrying an unmeasured font run or a run violating the
  signed `FONT-POINTS` in the signed `FONT-DIRECTION`.
- `untraced-costed-figure`: one finding for each distinct dollar value on a slide or in speaker
  notes that appears in no claim record.

The default report prints counts only. `--show` exposes artifact text and remains private. Exit 0
is clean, 1 means a finding, and 2 means the command did not completely scan the run, bar, or deck.
The command's reader-owned boundaries are in `deck_scan.DECLARED_LIMITS`:
`adversarial-completeness-unverified` and `image-provenance-unverified`. Walk both against the
finished artifact; this skill points to their objects and carries no second copy of either row.

## 5. Render and inspect every slide

Run the retained render pass after the package scan:

```bash
python tools/deck_render.py scratch/runs/<course>-<module>-course-assignment --pptx output/course-assignments/<course>-<module>-course-assignment-<date>.pptx
python tools/render_scan.py scratch/runs/<course>-<module>-course-assignment
```

`deck_render.py` asks a freshly spawned PowerPoint for one page-faithful PDF, then rasterizes it to
one 120-dpi PNG per slide in a new consecutive `render/pass-N/`. A failed route retains no pass.
If PowerPoint cannot export, ask the clinician for a clinician-supplied PDF and rerun with
`--clinician-export <PDF>`; PowerPoint is the fast path and never the only path.

`render_scan.py` reads canonical uninterrupted pass directories, the retained export's page count,
and readable PNGs. Earlier passes remain counted evidence; only the last pass must contain at least
one readable image for every exported page. Fewer final images than exported pages is exit 1. No
measurable retained export or noncanonical pass history is exit 2.

A vision-capable, non-authoring context opens every PNG in the final pass and compares it with the
deck and signed bar. It reports clipping, overflow, overlap, unreadable contrast, missing or
misplaced text, broken images, and any generated site image or conceptual image lacking its
caption. A package scan cannot substitute for this visual read. Preserve the original finding,
repair through the authoring context, render into the next pass, and give the correction to a new
non-authoring checker.

## 6. Approve, submit, and reread

Show the clinician the finished deck, notes, adversarial report, grader counts, and final rendered
slides. Wait for the explicit go-ahead. Upload the `.pptx`, inspect the LMS submission page before
committing the action, submit, and reread the posted artifact and timestamp. Record the submission
URL, posted time, and whether the uploaded file matches in the private run directory.

Invoke `/AAR` with the output deck stem as the submission key. Its completion report must say
`the after-action review: clean`. Completion requires clean final
ledger, deck, and render scans; a completed visual comparison; the clinician's submission approval;
the posted reread; and the after-action review. Keep the signed bar, snapshots, claims,
adversarial result, and retained render passes together under the run directory. Remove every
temporary per-context path; if cleanup fails, report the exact remaining path.
