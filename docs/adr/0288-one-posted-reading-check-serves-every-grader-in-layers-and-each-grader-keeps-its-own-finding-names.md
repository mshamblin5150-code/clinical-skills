# One posted-reading check serves every grader in layers and each grader keeps its own finding names

**Measured at:** aac9865729668a047d34a0aff20c4946cabb2e2c

[#1330](https://github.com/mshamblin5150-code/clinical-skills/issues/1330) was filed from an
architecture review on 2026-09-16. It found that `discussion_artifact.read_posted_readings` parses
the `## REREAD:` records once, while four graders each grade those records separately. Triage on
2026-10-03 counted eight. Grilled 2026-10-03 against `main`, where the freshness gate read `FRESH`;
the clinician ruled every point below in that session. **Nothing is built here; this is the record
the build reads.**

## Measured before ruling

### Eight modules grade a posted reading

`grep -ln read_posted_readings tools/*.py`, excluding tests and `discussion_artifact.py`, names
eight modules. Five are `run_grader` members: `discussion_post_scan`, `discussion_reply_scan`,
`peer_critique_scan`, `checks_ledger` and `deck_scan`. Three are completion gates that return a
pass or fail with report lines and file no finding kinds: `medatrax_posting`,
`assignment_submission` and `approval_record`. `aar_scan` does not call the parser. It fingerprints
the raw block and grades no field.

### Every one checks the fingerprint, and the rest is uneven

All eight check that a record exists and that `SUBMISSION-SHA256` is valid and equal to a digest.
The digest differs by member: the output Markdown, the reply, `critique.md`, the deck, the approved
digest, or the joined note bytes. The sentence `SUBMISSION-SHA256 is missing, malformed, or stale`
is written five times. A missing record is worded five ways. It is filed as
`missing-posted-reading` by the post, reply and critique graders and as `submission-fingerprint`
by `checks_ledger` and `deck_scan`.

The verdict is checked four ways. The post and reply graders use
`discussion_artifact.POSTED_READING_VERDICTS`. `peer_critique_scan.RECOGNIZED_VERDICTS` holds the
same two values in an unbound copy. `medatrax_posting` and `assignment_submission` accept only
`matches`, because a `diverges` reading is not a completed submission.

Other checks belong to only one or two members. `READ` in `N of N read` form and the VISIT grammar
are checked only by `medatrax_posting`. The `COMPOSER-OUTCOME` branch and the posted-attachment
comparison appear in both `discussion_post_scan` and `checks_ledger`. The roster and duplicate
`entry_id` check is in `discussion_reply_scan` only.

### The critique grader omits two posted fields and crashes on its own template

`peer_critique_scan._reread_findings` checks the verdict and the fingerprint. It does not check
`POSTED` or `READ`, which the peer-critique skill's record template requires. It does not check
`entry_id`; the skill's `POST-URL` names the reviewed submission's page, because
[ADR 0204](0204-a-peer-critique-posts-to-the-peer-review-comment-and-its-ampersand-is-typed-literally.md)
found no deep link for the comment itself.

The skill's template also requires `LEGACY-DISPLAY:`, which records what Canvas's legacy
peer-review page showed under ADR 0204 ruling 3. `read_posted_readings` refuses that field. Driven
on a synthetic run with one roster post, a `critique.md` and a template-shaped record, the command
printed a `ValueError` traceback and exited 1, which is the grader's finding status. Without the
line, the same record parsed. `approval_record.completion_gate`, which the critique's terminal grade
applies, parses the same file and turns that `ValueError` into a finding, so the terminal
`the approval record` row also fails on every template-shaped critique record.

## Ruling 1. One shared check serves all eight graders, in layers

`discussion_artifact` gains one posted-reading check. Its core always runs: the record for the
submission exists, and its fingerprint is valid and equal to the digest the caller supplies. Every
other check is a piece a caller opts into: the posted fields, the verdict, the entry link, the
Composer outcome and attachment, and the VISIT and `N of N read` grammar. A caller that requires a
completed submission opts into a verdict piece that accepts only `matches`. `aar_scan` stays out,
because it grades no field.

## Ruling 2. The critique grader requires the posting time and reading date

`peer_critique_scan` opts into the posted-fields piece, as the post and reply graders already do. A
critique record missing `POSTED` or `READ` is filed under its existing `missing-posted-reading`
kind. The entry-link piece stays off for the critique, because its `POST-URL` is the reviewed
submission's page, not the comment.

## Ruling 3. The shared reader accepts `LEGACY-DISPLAY` and the critique checks only its form

`LEGACY-DISPLAY` becomes a recognized field of `read_posted_readings`. The critique grader requires
it, and requires it to open with `expected`, `differs` or `unreadable` followed by a reason. It
never grades what the page showed, which ADR 0204 ruling 3 keeps outside grading. A missing or
malformed line is filed under `missing-posted-reading`, with the detail naming the field. This
settles [#1504](https://github.com/mshamblin5150-code/clinical-skills/issues/1504)'s third
decision.

## Ruling 4. The check returns neutral outcomes, and each caller names them

The shared check returns a fixed set of outcomes, each carrying one standard message. Each grader
holds a table mapping those outcomes to its own finding kinds, and each completion gate turns them
into its report lines. No member's `ROWS`, `KINDS` or `GATED_ROW_SETS` changes. Message wording
becomes uniform, so the five wordings of a missing record become one.

## Ruling 5. Each grader calls the check where it reads the record today

[ADR 0221](0221-a-posted-reading-carries-the-fingerprint-of-the-source-it-read.md) ruling 4 is
read as written. Each grader grades the record at the point it already does. `deck_scan` and
`checks_ledger` grade on their `--submission` run, the gates on the completion grade, and the post
grader once the post records that it was posted. No grader's timing moves.

## Ruling 6. The check is callable on a record by itself

The shared check runs on a parsed record and a supplied digest, with no surrounding grade.
[#1466](https://github.com/mshamblin5150-code/clinical-skills/issues/1466) keeps the decision of
where an early check runs before the after-action review fingerprints the record. Whatever that
ticket rules calls this check rather than building its own copy.

## Rejected options

**Share only among the four graders the ticket named.** The deck, Medatrax, course-assignment and
approval gates would keep their copies, and #1466's early gate would build another.

**Share only the fingerprint predicate.** It is the one line every member repeats, but the verdict
split and the five missing-record wordings would stay duplicated.

**Leave the critique's posted fields unchecked and declared.** The skill requires two lines that
nothing could fail.

**Accept `LEGACY-DISPLAY` and grade nothing about it.** The same rule that cannot fail, one field
over.

**Move the legacy-page observation into the verdict's text.** ADR 0204 keeps the display
observation separate from the stored-text comparison.

**Have each caller pass its finding names in.** The completion gates file no finding kinds, so
they would need a second path for one check.

**Share one set of finding names.** A deck run's missing record would change name, and so would
every consumer keyed on it.

**Call the check once, from `run_grader`.** The runner would need each member's timing rule, and
ADR 0221 ruling 4 would need a supersession marker for a behavior change this refactor was not
asked to make.

**Rule #1466's early-gate location here.** Its answer changes who calls the check, not how the
check is built, while its other two decisions would stay open there.

## Consequences

**Two changes are visible as grading changes**, both on the critique. A record missing `POSTED`,
`READ` or a well-formed `LEGACY-DISPLAY` now fails. A record following the skill's template is
unaffected, and is graded for the first time instead of crashing. Because ruling 3 widens the
shared reader, the approval gate's terminal row stops failing on that record too.

**A parse failure in the critique grader reports did-not-scan with exit 2**, like its siblings,
instead of a traceback with exit 1. This is a defect repaired, not a ruling.

**Report wording changes and finding names do not.** Tests keyed on the old message text move.

## What this does not reach

**Whether a member's digest is the right file.** Each caller still supplies its own digest, and
the shared check compares what it is handed.

**[#1504](https://github.com/mshamblin5150-code/clinical-skills/issues/1504)'s other three
defects**, and #1466's comment landings and round supersession.
