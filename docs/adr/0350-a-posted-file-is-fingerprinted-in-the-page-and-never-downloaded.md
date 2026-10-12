# A posted file is fingerprinted in the page and never downloaded

**Measured at:** 9cf60f4168ef78666c9505d17def3e2d3df6792f

[#1562](https://github.com/mshamblin5150-code/clinical-skills/issues/1562) was filed from the
after-action review of a `course-assignment` run (NUR 5042 Module 11) on 2026-10-04. After
submission the posted reading needed the submitted Word document's bytes. A page fetch of the
attachment failed, a scripted download saved nothing visible, and the agent then clicked the LMS
Download link, looked in the wrong folder, and clicked again, opening a duplicate-download dialog
the clinician had to cancel. Grilled 2026-10-12 against `main`; the clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Every route that reads a posted file says to download it, and none says how.**
`skills/course-assignment/references/docx.md` says "download and read the posted artifact" on both
the agent and clinician upload routes, and `skills/course-assignment/SKILL.md` says "download the
posted artifact" on the deck branch's clinician route. `skills/_shared/reference/canvas-editor.md`
tells the attachment fallback of
[ADR 0255](0255-a-composer-size-refusal-is-discovered-and-falls-back-to-an-attached-document.md) to
download the posted entry's attachment into `<run>/posted/`, and `discussion-post` and
`practicum-case-study` repeat it.

**Only the attachment fallback grades the posted bytes.** `discussion_post_scan` and
`checks_ledger` require the `posted/` copy and compare its SHA-256 with the local `.docx` under
ADR 0255 ruling 4. `course-assignment`'s posted reading is graded by `discussion_artifact` for its
attachment count and submitted filenames only; whether the posted bytes match is the reader's
written verdict.

**The download is the step that fails.** [ADR 0324](0324-a-faculty-or-classmate-file-is-identified-on-the-live-page-and-matched-by-fingerprint-before-a-run-reads-it.md)
measured that the clinician's Chrome asks where to save every download, so only he can answer the
dialog and the run cannot know where the file went unless he says. The same record measured that a
page script fetching a course-site file record's `url` with credentials reads the whole file and
computes its SHA-256, while the page's `/download` link fails across origins. That measurement was
taken on a faculty file. A submission attachment and a discussion-entry attachment have not been
measured.

**A page script has the bytes but cannot read the document out.** The bytes sit in page memory; the
browser tool truncates returned values near 1,000 characters, so neither the file nor its extracted
text can be carried into the run byte-exactly. A SHA-256 equality with the approved file makes that
unnecessary: identical bytes are an identical document, so reading the local approved file is
reading what the surface holds.

**The tab half of the incident is already enforced.** `tools/browser_tab_hook.py` has been
registered for both browser families since
[#1120](https://github.com/mshamblin5150-code/clinical-skills/issues/1120), before the Module 11
run. The refused tabless navigation the review recorded was that hook working.

## Ruling 1 — a posted file is identified by a fingerprint the page computes, and never downloaded

After a file is posted, the run identifies the posted entry's attachment by the course site's own
record of it, fetches that record's `url` with credentials in a page script, and computes its
SHA-256 there, exactly as ADR 0324 does for a **Faculty file**. When that **Posted fingerprint**
equals the approved file's fingerprint, the run reads the local approved file, and that reading is
the posted reading's reading of the content. The run never clicks a posted entry's Download link
and never searches a download folder.

The ticket's procedure, one agent-clicked download followed by a search of a configured folder,
was declined because it keeps the save dialog only the clinician can answer, the guess about where
the file landed, and a "never click twice" rule that exists only as an instruction. A clinician
save on every sitting was declined as a manual step the page route makes unnecessary.

## Ruling 2 — one rule governs every posted file in the coursework skills

The rule lives once in `skills/_shared/reference/lms-attachments.md`, beside ADR 0324's rule for
files a run reads, and governs `course-assignment` on both its DOCX and deck branches and the
attachment fallback of `discussion-post` and `practicum-case-study` through
`skills/_shared/reference/canvas-editor.md`. Each of those points to it in place of its download
sentence. Writing it for `course-assignment` alone was declined because the failure, the browser
setting and the fix are the same on every route, and ADR 0324 ruling 1 already declined one rule
written twice on two schedules.

## Ruling 3 — when the page cannot fingerprint the file, the clinician saves it once

When the page script cannot read the posted attachment, the run stops and asks the clinician once to
save it from the posted entry's own attachment link and say where. The run copies that file into
`<run>/posted/<basename>`, fingerprints the copy against the approved file, and records that the
clinician supplied it. A copy from the clinician's general files area is still not evidence of what
the entry carries.

A byte-size fallback, which ADR 0324 allows for faculty files, was declined because an edited
document can keep its size and the posted reading exists to prove the approved bytes. An
agent-clicked download as the fallback was declined because it is the failure this record exists
to remove.

## Ruling 4 — the posted reading records each posted fingerprint and its route, and the grader compares

The posted reading carries one `POSTED-FILE:` line per submitted file, replacing the attachment
fallback's `ATTACHMENT:` line:

```text
POSTED-FILE: <submitted basename> | sha256=<64 hex> | route=page
POSTED-FILE: <submitted basename> | sha256=<64 hex> | route=clinician-supplied | path=posted/<basename>
```

The completion grader requires one line for every `SUBMITTED-FILE` on `course-assignment` and one
line on an attachment fallback, and requires each fingerprint to equal the approved file's: the
Gate 1 fingerprint recorded for that filename in `course-assignment`, and the local `.docx` for
`discussion-post` and `practicum-case-study`. On the `clinician-supplied` route it also
re-fingerprints the named `posted/` copy and requires it to equal the recorded value. A missing,
malformed or unequal line is a finding. The reader still reads the local file and writes its
verdict as before; the fingerprint proves which file that is.

The grader cannot show that a `page` fingerprint was computed by the page rather than copied from
the approved record. That is declared beside the implementation, as ADR 0324 declares that its
check cannot show the page was read before the disk search. Keeping the reader's written verdict as
the only proof of the posted bytes was declined because it grades nothing and would drop the byte
check the attachment fallback has today.

## Ruling 5 — the attachment fallback's grader trusts the recorded page fingerprint

On the attachment fallback the grader no longer re-derives the posted bytes from a downloaded copy
on the `page` route; it compares the recorded posted fingerprint. ADR 0255 ruling 4 declined a
recorded digest because the grader would trust the agent's report, and the clinician overturned
that with the cost named: the download it required is the step that fails, and the page computes
its fingerprint from the course site's own bytes. Keeping ADR 0255's download on those two routes,
with the clinician saving the copy, was declined because the rule would not be one rule and the
saved copy would cost a dialog on every fallback post. Carrying the page's bytes into the run was
not available, by the measurement above.

## Ruling 6 — the browser-tab rule stays with its hook

No skill sentence restates that every browser action names the run's own tab. The hook refuses a
tabless page action in every skill and both browsers and names the remedy; a sentence in one skill
would be a second copy that drifts silently when the hook changes.

## Supersedes

- [ADR 0255](0255-a-composer-size-refusal-is-discovered-and-falls-back-to-an-attached-document.md)
  ruling 4, its words "the agent downloads the attachment from the posted entry's own link into the
  run directory under `posted/`. The grader hashes that copy" and "a recorded digest was declined".
  The page fingerprint is recorded and compared; a `posted/` copy exists only on the
  clinician-supplied route.
- [ADR 0255](0255-a-composer-size-refusal-is-discovered-and-falls-back-to-an-attached-document.md)
  ruling 6, its words "`ATTACHMENT:` naming the retained `posted/` copy". The record carries a
  `POSTED-FILE:` line instead.
- [ADR 0255](0255-a-composer-size-refusal-is-discovered-and-falls-back-to-an-attached-document.md)
  ruling 7, its words "and the posted-attachment download". The shared sheet points to the posted
  file rule in `lms-attachments.md` instead.

## Build checklist

- **Measure first, read-only.** In the clinician's signed-in Chrome, against an already posted
  `course-assignment` submission and an already posted discussion entry carrying an attachment,
  read each attachment's course-site file record, fetch its `url` with credentials in a page script,
  and compare the page's SHA-256 with the local file posted. Submit nothing. Record the dated
  observation, including the API paths used, beside the rule. If a route fails, ruling 3's
  clinician-supplied route is that surface's only route and the sheet says so.
- `skills/_shared/reference/lms-attachments.md`: a section for posted files carrying rulings 1, 3
  and 4, the page script, the `POSTED-FILE:` grammar, and the sentence that the run never clicks a
  posted entry's Download link.
- `skills/course-assignment/references/docx.md` and `skills/course-assignment/SKILL.md`: replace
  each "download the posted artifact" with a pointer to that section and add `POSTED-FILE:` to the
  `## REREAD:` template, written before `/AAR` extracts the block.
- `skills/_shared/reference/canvas-editor.md`, `skills/discussion-post/SKILL.md` and
  `skills/practicum-case-study/SKILL.md`: replace the `posted/` download and `ATTACHMENT:` field with
  the pointer and `POSTED-FILE:`.
- `tools/discussion_artifact.py`: parse `POSTED-FILE:` and retire `ATTACHMENT:`, with findings for a
  missing, malformed or unequal line and a clinician-supplied copy that is absent or differs.
- `discussion_post_scan`, `checks_ledger` and the `course-assignment` posted-reading check: grade the
  new line against each skill's approved fingerprint, with a `DECLARED_LIMITS` row naming ruling 4's
  copied-fingerprint gap; tests through the public commands for a page match, a page mismatch, a
  clinician-supplied match, a changed supplied copy, a missing line and a clean control.
- `CONTEXT.md`: **Posted fingerprint**, written with this record.

## What this record does not reach

- **Whether a `page` fingerprint was computed by the page.** A run that copies the approved value
  into the line passes.
- **Whether the course's grader opens the same attachment.** The fingerprint proves what the entry
  carries, not how the course displays it, as ADR 0255 already records.
- **Whether the page route works on submission and discussion attachments.** It is measured by the
  build, not here; ruling 3 governs a surface where it fails.
