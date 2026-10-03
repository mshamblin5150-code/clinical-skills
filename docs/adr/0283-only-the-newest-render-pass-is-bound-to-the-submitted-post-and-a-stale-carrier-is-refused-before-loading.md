# Only the newest render pass is bound to the submitted post and a stale carrier is refused before loading

**Measured at:** 7075404991afc27320992a7d4e307a4b3ebb82e6

[#1253](https://github.com/mshamblin5150-code/clinical-skills/issues/1253) was filed from
[#1035](https://github.com/mshamblin5150-code/clinical-skills/issues/1035)'s grilling, where a
mutation drive found that `discussion-post` makes two promises about retained Canvas-box passes that
cannot both hold after a fix. The skill says *"each pass must keep exactly one `.html` export whose
bytes equal the submitted HTML"* and also says *"An earlier pass may stop after a defect; only the
last pass must account for every block."* A defect found in the box is fixed in the Markdown, the
fix changes the HTML, and the earlier pass still holds the pre-fix bytes. Grilled 2026-10-03 against
`main`, where the freshness gate read `FRESH` after a rebase; the clinician ruled every point below
in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

### Every retained box pass is compared with the current HTML

`_rendered_page_findings` in `tools/discussion_post_scan.py` loops over every `RENDERED` record and
its aligned pass, reads that pass's one `.html` export, and appends
`retained HTML differs from the submitted HTML` whenever the bytes differ from `--html`. It does not
distinguish the highest pass from the others.

The defect was re-driven on 2026-10-03 through the test module's own `Run` builder and
`CanvasSubmissionRows.rendered` fixture. Pass 1 recorded a defect stop and pass 2 a complete clean
read of the current HTML:

| pass 1's retained `.html` | `discussion_post_scan --html` |
| --- | --- |
| the same bytes as the current HTML | exit 0, `rendered-pages: 0` |
| the current HTML with one word added, standing for the pre-fix render | exit 1, `rendered-pages: 1` |

*Had the scanner compared only the highest pass, the second row would have read exit 0.* The
existing `test_an_abandoned_defect_can_precede_a_complete_final_canvas_read` reuses one HTML file
for both passes, so it is the first row and never exercises a fix.

### The HTML and Word carriers are compared with the Markdown only after posting

`html_matches_rebuild` and `docx_matches_rebuild` are computed whenever `--html` and `--docx` are
passed, but their findings are emitted only inside `_posted_reading_findings`, which runs once a
`## REREAD:` record exists. Before posting, nothing compares a carrier with
`post_html.render` or `docx_write.parts` of the current Markdown.

The `submission-text` row already compares the HTML's text with the Markdown's, and it caught both
text-level changes driven on 2026-10-03: a word changed in the Markdown after the HTML was written,
and the imagery working marker `[[PROPOSED IMAGE <key>]]` removed after the HTML was written, which is
the transition the ticket's 2026-09-26 comment recorded. **What it does not catch is a change that
alters the HTML's bytes and not its text.** One word wrapped in `*...*` in the Markdown after the
HTML was written gave `post_html.render` different bytes, and the scan exited 0 with
`submission-text: 0` and `rendered-pages: 0`. *Had the pre-post run compared the HTML with its
rebuild, that row would have been a finding.*

### Older passes were never the only guard, and the glossary already ruled them history

[ADR 0221](0221-a-posted-reading-carries-the-fingerprint-of-the-source-it-read.md) measured that an
older pass holding stale HTML was the only thing catching an edit made after a posted reading, that
it could not tell that edit from an edit made before posting, and that it vanished once the pass was
overwritten. It then ruled the posted reading's own fingerprint and, through
[PR #1260](https://github.com/mshamblin5150-code/clinical-skills/pull/1260), the terminal rebuild
comparison. The `CONTEXT.md` entry for **Render pass** already reads *"only the last must be whole,
because a pass abandoned on a defect found at page 2 did what it should."*
[ADR 0210](0210-a-render-pass-and-a-check-record-carry-the-fingerprint-of-what-they-graded.md) binds
only the highest pass for the case study and the deck, and `_attachment_page_findings` already reads
only the highest pass on an attachment run.

## Ruled 2026-10-03

### 1. Only the newest Canvas-box pass is bound to the submitted HTML

On an inline run, the highest retained pass's one `.html` export must equal the `--html` file byte
for byte. Every earlier pass must still parse as a record, keep exactly one `.html` export and keep at
least one readable PNG capture, and its record must still meet the existing shape rules. Its export's
bytes are not compared with anything. An earlier pass is history of a reading that stopped, and the
Markdown it came from no longer exists to compare it with. The `discussion-post` skill sentence that
requires every pass to equal the submitted HTML is rewritten to say this.

The ticket's own option of a per-pass fingerprint file was declined. The agent copies `post.html` into
the pass by hand, so a fingerprint it also writes there proves only that it was copied, which is the
ground ADR 0210 refused an agent-written fingerprint on. Dropping the byte comparison for every pass
was declined because it removes the only tie, before posting, between the box that was read and the
file to be submitted.

### 2. The carrier rebuild comparisons run before loading, on every run that names a carrier

Whenever `--html` is passed, a difference from `post_html.render` of the `--draft` Markdown is a
finding, exit 1, whether or not a posted reading exists. Whenever `--docx` is passed, a difference
between its archive parts and `docx_write.parts` of the Markdown is the same. This moves the two
existing comparisons out of the posted-reading branch rather than adding a new one. The
`discussion-post` skill also says to regenerate both carriers after every proposed-image ruling and
before loading, so the written step and the refusal say the same thing.

Ruling 1 makes this necessary rather than tidy. The newest pass proves that the box showed the `.html`
file; this proves that the `.html` file is what the approved Markdown produces. Without it, a
formatting-only edit after the carriers were written reaches Gate 2 on a clean scan, and a Canvas
post cannot be withdrawn after submission. Keeping the comparison after posting, with only a written
instruction to regenerate, was declined for that reason. Moving only the HTML comparison and leaving
the Word one after posting was declined because it saves nothing and leaves two rules to remember.

### 3. On an attachment run, the box passes from the refused inline attempt stay ungraded

When the posted reading names `COMPOSER-OUTCOME: attachment`, the Word render pass is the newest pass
and is the one bound to the submission, through its `post-draft.sha256` Markdown fingerprint under
[ADR 0255](0255-a-composer-size-refusal-is-discovered-and-falls-back-to-an-attached-document.md)
ruling 5. The Canvas-box passes left by the refused inline attempt are not compared with the HTML and
not otherwise graded, which is what `_attachment_page_findings` already does. This settles the
interaction the ticket's 2026-09-17 and 2026-09-29 comments asked to have settled explicitly, and it
follows from ruling 1 rather than adding a branch. Holding the newest box pass to the HTML here was
declined because it would grade a submission Canvas refused. Requiring the box passes to be removed
before the Word render was declined because passes append and are never overwritten.

## Consequences

The build changes `_rendered_page_findings` to compare bytes only for the highest retained pass, and
moves the two rebuild findings out of `_posted_reading_findings` into a branch that runs whenever the
corresponding carrier is passed. On a posted inline reading the HTML rebuild finding must not be
reported twice. The `discussion-post` skill's Canvas-box paragraph and its grader paragraph name only
the newest pass, and its Gate 1 step names the regeneration. The tests add the ticket's reproduction,
in which a fix changes the HTML between pass 1 and pass 2 and the run passes, and the formatting-only
stale carrier measured above, which must now exit 1 before posting.

## What this does not reach

Whether an earlier pass's `post.html` was ever what its Markdown produced. Whether the box reader
compared anything, which is ADR 0147's limit. Whether Canvas stored the bytes that were loaded, which
is the posted reading's. Whether a carrier regenerated from the right Markdown was the one loaded into
the box; ruling 1's newest-pass comparison binds the pass to the file, and the file to the box is the
reader's claim.
