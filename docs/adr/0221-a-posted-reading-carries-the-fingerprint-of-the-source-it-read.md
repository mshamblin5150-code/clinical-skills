# A posted reading carries the fingerprint of the source it read

[#1035](https://github.com/mshamblin5150-code/clinical-skills/issues/1035) was filed on a
`discussion-post` run whose private `post.md` differed from the entry on the board while its posted
reading said `matches`. [ADR 0206](0206-a-final-review-follows-a-posted-record-and-every-review-round-keeps-its-own-files.md)
ruling 6 has since renamed that record's heading to the submission key, which settled the heading.
What the ticket left open was whether anything ties a reading's verdict to the file it describes.
Grilled 2026-09-13; the clinician ruled every point below on the same day. Nothing is built here; this
is the record the build reads.

## Measured before ruling

### The measured run's submission matched the board

The run is NUR 5042 Module 5. Its output Markdown and its Word archive were each reduced to word
tokens and aligned with the initial post in that run's board capture using
`difflib.SequenceMatcher(..., autojunk=False)`. Both matched **2,778 of 2,778** tokens with no
non-equal span. The ticket's thousand-word gap was between the board and `post.md`, a working record
the skill never required to hold the posted text. *Had the output artifact been edited after posting,
the ratio would have fallen below 1 with at least one differing span.* Word tokens drop punctuation
and link markup, so this does not show that a link rendered as a link. The figures are counted against
material under `scratch/` and nothing committed re-derives them.

### No real run shows the defect, and a synthetic run shows the hole

Five `discussion-post` run directories exist on disk. None has an output `.html`, so none was
produced under the current Canvas-box route. On a synthetic run built from the scanner's test
fixtures, with a `matches` reading appended after its render record:

| Mutation after the reading | `discussion_post_scan` |
| --- | --- |
| one word changed in the `.md` only | exit 1, `submission-text` |
| one word changed in the `.html` only | exit 1, `submission-text` and `rendered-pages` |
| the same word changed in `.md`, `.html` and `.docx` | exit 1, `rendered-pages` from the older pass's retained bytes |
| the above, re-rendered into a new pass, with the older pass's `post.html` overwritten | **exit 0** |

The only catch comes from an older render pass that still holds the old HTML. The same finding fires
on an edit made before posting, so it does not distinguish the two, and it vanishes once that pass is
overwritten. Nothing in the scanner reads the reading and the render passes together.

### The HTML is rebuilt byte for byte and the Word file is not

`tools/post_html.py` run twice on one Markdown file two seconds apart wrote byte-identical output.
[ADR 0210](0210-a-render-pass-and-a-check-record-carry-the-fingerprint-of-what-they-graded.md)
measured that a `.docx` hashes differently on every render because the zip stamps each entry's
write time, and that `docx_write.parts()` compares exactly.

### Five skills write the record and one parser reads it

`discussion-post`, `discussion-reply`, `peer-critique`, `course-assignment` and
`practicum-case-study` each append a `## REREAD:` record. `discussion_artifact.read_posted_readings`
refuses a field outside `POST-URL`, `POSTED`, `READ` and `VERDICT`, and it is read by
`discussion_post_scan`, `discussion_reply_scan` and `peer_critique_scan`. The deck's and the case
study's records are read only by `aar_scan`, which requires exactly one record per submission and
fingerprints that block when it extracts.

## Ruled 2026-09-13

### 1. A posted reading is bound to its source by a fingerprint

Every `## REREAD:` record carries `SUBMISSION-SHA256:`, and a grader refuses the record when that
fingerprint no longer matches. **Refusing edits by prose alone was declined**: the skill already says
not to change the graded artifact after a divergence, and nothing could fail it. **Storing the posted
text was declined** on [ADR 0050](0050-a-posted-reading-is-read-off-the-board-and-the-reply-path-has-no-submission-to-stand-in-for-it.md)
ruling 1's measurement that the capture strips formatting. **Comparing modification times against the
reading date was declined** on ADR 0206 ruling 1 and ADR 0050's refused freshness join.

### 2. The fingerprint is of the source, and the submitted forms are rebuilt from it

For `discussion-post` and `practicum-case-study` the fingerprint is the SHA-256 of the output
Markdown. Where it grades the record, `discussion_post_scan` also rebuilds the HTML from that Markdown
and requires the `.html` byte for byte, and rebuilds `docx_write.parts()` and requires the `.docx`
part for part. A post is sometimes too large for the Canvas box and goes up as an attached `.docx`;
this binding holds on either route, so the record carries no route field. A reply fingerprints its
`response-<name>.md`, a critique its `critique.md`, and a deck its `.pptx`, which has no source
behind it. **Fingerprinting the `.html` alone was declined** because it leaves the attachment route
unbound. **Fingerprinting whichever file was submitted, with a route field, was declined** because a
`.docx` fingerprint expires on a harmless re-render.

### 3. The attachment fallback belongs to #1154

`discussion-post` has no step for a Composer refusal or an attached `.docx`.
[#1154](https://github.com/mshamblin5150-code/clinical-skills/issues/1154) is widened from
`practicum-case-study` to every skill posting through the Composer, so the size refusal, the response
that counts as one, and the upload readback are ruled once. **A sibling ticket was declined** as the
same three decisions filed twice. **Widening #1035 was declined** because ruling 2 is correct on
either route and needs nothing from the route's ruling.

### 4. Every record carries it and every record is graded

`discussion_post_scan`, `discussion_reply_scan` and `peer_critique_scan` grade the fingerprint where
they already read the record. `deck_scan` and `checks_ledger` grade it on their `--submission` run,
beside the ADR 0210 digests they already compute. **Writing the line with no grader for the deck and
the case study was declined** as a rule that cannot fail.

### 5. A missing fingerprint is refused like a mismatch

There is no cutoff date. A finished run is never graded again, these graders do not run in CI, and a
run in flight when the build lands adds the line and grades again. **A cutoff on `READ` was declined**:
nothing graded later needs it, and `READ` is a typed date that could excuse the line by being
backdated.

## Taken as conventions, not ruled

- The agent writing the record computes the digest with `file_digest` before `/AAR` extracts, because
  `aar_scan` fingerprints the whole block and a line added afterwards refuses the review.
- Ruling 2's rebuild bindings are graded only within the posted-reading row, so the archival `.docx`
  stays report-only until a post exists.
- A `diverges` verdict carries the fingerprint too.

## Consequences

- `discussion_artifact.REREAD_FIELDS` gains `SUBMISSION-SHA256`, and the five skills' record templates
  gain the line.
- Each of the five graders named in ruling 4 gains a mismatch finding; its tests drive a mismatch, a
  missing line, and a clean control.
- #1154 is retitled and its body widened per ruling 3.

## What this does not reach

**A board repair the clinician directs.** It changes the board and not the source, so the fingerprint
still matches while the verdict describes the board before the repair.

**`discussion_post_scan`'s silence when `post.md` carries neither posted-reading field.** At the final
grade the review's own requirement of a record for the submission refuses that run, so the only runs
it lets through have not posted.
[#1066](https://github.com/mshamblin5150-code/clinical-skills/issues/1066) keeps the general
partial-read question.

**Whether the LMS holds the fingerprinted bytes.** That readback is #1154's.

**Whether the reader read what the verdict says.** A fingerprint binds a verdict to a file, not to
attention.
