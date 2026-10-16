# A Word edit after the checks is carried into the Markdown and a directed attachment is his to post

**Measured at:** 8eebbe514c829a0fdb93768d237dd7c6a5b96996

[#1588](https://github.com/mshamblin5150-code/clinical-skills/issues/1588) was filed from the
terminal completion grade of a `practicum-case-study` run (NUR 5144 Module 4) in October 2026. After
every step 9 check was clean, the clinician opened the rendered `.docx` in Word, changed one link,
saved it, said the change needed no further read, and directed the run to upload that file. The run
attached his saved file under the pointer body with no inline attempt. The terminal
`checks_ledger.py --submission` grade then failed four rows, each accurate about the record. The
clinician ruled every point below on 2026-10-16, against `main` at the commit above, where the
freshness gate read `FRESH`. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The skill has no route for an edit made after the checks.** Its only Word-edit rule is the
destination-guard paragraph in step 9: the Markdown is the authoritative artifact, and an edit found
before a render is recovered into the Markdown, and into the claim ledger where it changes a
supported claim, before `docx_write.py --force`. `case_study_render.py` refuses a pass whose Word
parts differ from the parts rebuilt from the same-stem Markdown. `course-assignment`'s DOCX branch
states the stricter form: any edit to the finished `.docx` changes its identity and requires a new
retained render pass and a fresh review. No skill keeps a clinician-edited file as the submission.

**No completion grader has a clinician-ruled exemption for a grader row.** The exemptions that exist
are [ADR 0330](0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md)'s waiver of
a named reader remark and
[ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md)'s
freeze and historical adoption. A declared divergence would have been a new mechanism.

**A multi-source approval cannot join the posted reading.** `approval_record.source_sha256` hashes
the concatenated bytes of every source, so a two-source population matches no single file's digest,
while `checks_ledger.py` requires the posted reading's `SUBMISSION-SHA256` to equal the Markdown
digest and `approval_record.completion_gate` requires it to equal the approval's population hash.

**The Word writer cannot reproduce every Word edit.** `docx_write.py` writes a URL as plain text, has
no hyperlink construct, and writes a fixed style vocabulary.

**The shared posted-reading check is blind to who posted.** `discussion_artifact.check_posted_reading`
requires a dated `REFUSAL` on every Composer attachment outcome. `approval_record` already records a
posting route of `agent` or `clinician`, and its completion gate requires a Posting go-ahead only for
`agent`.

## Ruling 1. A Word edit after the checks is carried into the Markdown and re-rendered

When the clinician edits the rendered `.docx` after the step 9 checks, the run reads his saved
document, carries the edit into the Markdown and, where it changes a supported claim, the claim
ledger. It then re-renders and retains a new render pass. The re-render is the file posted, and the
Markdown remains the only authoritative artifact. The next showing carries
[ADR 0348](0348-a-revised-draft-is-shown-with-a-computed-change-list-and-the-aar-command-names-its-record-file.md)'s
computed change list, which lists his edit, and the item takes a fresh content go-ahead.

Posting his file as saved under a declared, clinician-ruled divergence was declined. It needed a new
exemption in the completion grader, it moved the approval's fingerprint to the `.docx`, and the
posted file would have been read by no reader, by no render scan, and by no change list. Posting his
file while carrying the edit into the Markdown under a paragraph-text parity check was declined as
well: it would have split the posted artifact from the artifact every reader and the approval cover.

## Ruling 2. The approval population stays the Markdown alone

This follows from ruling 1. The content approval and the Posting go-ahead pass
`sources=(output_markdown,)`, the posted reading's `SUBMISSION-SHA256` is the Markdown digest, and
the join `completion_gate` makes stays one digest on both sides. No multi-source population is
admitted on this skill.

## Ruling 3. The clinician's "no re-read" does not waive a reader

His edit opens a new round of changes. The leftovers read under
`the leftovers of every change after the first draft` and the visual read of the new render pass
under `the rendered document` both run. His instruction that the change needs no further read means
he does not read it again himself; he sees the change list and the new render at the go-ahead.

A clinician waiver of both reads, recorded by name at the go-ahead, was declined because it would
have left the posted file's visual check on the render before his edit. Skipping the leftovers read
for an edit that changes no clinical claim was declined because the run would have had to draw that
line on every edit and a grader could not verify the declaration.

## Ruling 4. An edit the Word writer cannot reproduce stops at the clinician

Where part of the edit has no form the Word writer produces, such as a live Word hyperlink, a manual
font or spacing change, a comment, or a tracked change, the run stops before re-rendering. It shows
him exactly what cannot be carried and the closest form it can produce, for example a URL as plain
text. He accepts that form, which then goes through ruling 1, or he directs otherwise. No renderer
work is filed unless he asks for it.

Silently carrying what can be carried and recording the rest only in the run was declined, because he
would learn of the loss from the posted file. Filing a renderer ticket on every new gap was declined
for a case that has occurred once; APA 7 does not require live links in a student paper.

## Ruling 5. The Composer branch posts inline first, always

On a `canvas-composer` route the run posts the full body inline. The shared initial-post attachment
fallback stays reachable only through a visible message-size refusal, as
`skills/_shared/reference/canvas-editor.md` states. When the clinician directs an attachment without
such a refusal, the run says once that his standing rule for these boards is inline first and that
the inline body now carries his edit, then posts inline unless he repeats the direction.

Making his direction an admissible route reason beside a size refusal was declined. It needed a route
value naming his words, a second fixed pointer text, because the existing one states that Canvas
refused the full text, and grader changes in the three skills that share the fallback. Ruling 1
removed the reason the Module 4 run had to attach: its Markdown did not carry his edit.
[ADR 0331](0331-every-canvas-save-waits-at-the-loaded-box-for-a-recorded-go-ahead-and-plain-text-is-built-by-one-command.md)'s
loaded-box stop and Posting go-ahead are unchanged.

## Ruling 6. A repeated direction to attach is handed to the clinician to post

When he repeats the direction after the run's one sentence, the run does not submit the entry. It
hands him the checked `.docx`, the re-render that passed both reads, to attach and post himself, and
records the item through `approval_record.record_clinician_posting`. The posted reading still
records the board state and the posted file.

**One build follows.** `discussion_artifact.check_posted_reading` stops requiring a dated `REFUSAL` on
a Composer attachment outcome when the item's posting route is `clinician`. It still requires the
posted file's fingerprint to equal the checked local `.docx`. The run-posted attachment keeps every
existing requirement.

A run-posted attachment carrying his words as its route reason was declined for ruling 5's reasons.
Refusing with no handoff was declined because a post he then attached himself would fail the
terminal grade on the same refusal row this ticket was filed over.

## Ruling 7. The Module 4 run is left to historical adoption

Nothing in this build reaches the Module 4 run. ADR 0346 ruling 3's historical adoption closes it as
`frozen at adoption, never graded clean` if its private evidence qualifies; otherwise its terminal
grade stays failing, which is an accurate account of a run the rules did not yet cover. No session
has read that run's private records to establish which.

Copying the edit into that run's Markdown and re-grading was declined because it would state that the
Markdown matched the posted file at the time it was posted. A named one-run exemption in the grader
was declined as a permanent special case for one past event.

## Consequences

- `skills/practicum-case-study/SKILL.md` gains the post-check Word-edit route of rulings 1, 3 and 4
  beside its destination-guard paragraph, and rulings 5 and 6 in its approval and posting paragraphs,
  apart from the paragraph ADR 0348's change-list pointer occupies.
- `discussion_artifact.check_posted_reading` gains the route condition of ruling 6, with tests that a
  clinician-posted attachment without a refusal passes, that a run-posted one still fails, and that a
  clinician-posted attachment whose posted file differs from the local `.docx` still fails.
- `discussion-post` and `course-assignment` share the fallback. Ruling 5 changes no text they read;
  ruling 6's checker condition applies wherever the shared function runs with a clinician route.
