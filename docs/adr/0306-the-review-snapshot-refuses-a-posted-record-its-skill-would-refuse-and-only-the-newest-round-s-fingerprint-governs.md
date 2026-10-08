# The review snapshot refuses a posted record its skill would refuse and only the newest round's fingerprint governs

**Measured at:** 7147b01c9e9960987a0b45996ee20ea22c944416

[#1466](https://github.com/mshamblin5150-code/clinical-skills/issues/1466) was filed from the
after-action review of a batch-shift run. Grilled 2026-10-08 against `main`, where
the freshness gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

### The snapshot fingerprints a record that no check has read

`aar_scan._posted_reading_block` requires exactly one `## REREAD: <submission key>` block and
fingerprints its bytes. It grades no field. The Medatrax `READ` and VISIT grammar is checked by
`medatrax_posting.completion_gate`, which runs only inside the completion grade after the review.
On that shift the grade refused a VISIT line after round 1 had fingerprinted the record.
Correcting the line changed the fingerprinted bytes and forced a second round.

The check the snapshot needs already exists in one place. `discussion_artifact.check_posted_reading`
grades a parsed record against a caller-supplied digest with no surrounding grade, which is
[ADR 0288](0288-one-posted-reading-check-serves-every-grader-in-layers-and-each-grader-keeps-its-own-finding-names.md)
ruling 6. Every scoped run's approval record names its skill, and `aar_scan.COMPLETION_GRADERS`
already pairs each skill with its completion grader.

### The stuck run fails only on its first round's fingerprint

`python tools/aar_scan.py <the run> --submission <its shift key>`, run 2026-10-08, reports two
review records, 20 corrections with none unlanded, and one finding, exit 1. The ticket's
2026-09-30 comment identifies it as round 1's posted-reading mismatch. Restoring round 1's block
fails the completion grader, and the corrected block fails round 1's fingerprint. Under
[ADR 0206](0206-a-final-review-follows-a-posted-record-and-every-review-round-keeps-its-own-files.md)
rulings 5 and 7 neither grade can pass.

### A landing is matched by shape, and its proof is any `gh` call

`aar_scan.GH_ISSUE` fullmatches only `https://github.com/<owner>/<repo>/issues/<N>`, so a
`#issuecomment-<M>` anchor is graded `unlanded-ticket`. Five corrections in that run
landed as comments on open tickets. `aar_scan._successful_gh_call` accepts any successful `gh`
command in the round's transcripts, tied neither to the named issue nor to the round.

Both harnesses keep a command's printed output. Claude records it in the `tool_result` block, and a
Codex rollout's `CommandExecution` item carries `stdout` and `aggregated_output`; those key names were
read from a local rollout on 2026-10-08 without reading their values. `gh issue create` prints the
new issue's address and `gh issue comment` prints the comment's address. The build drives both
before relying on them.

## Ruling 1 — the snapshot refuses a posted record its own skill's check refuses

`aar_scan --extract` reads the skill from the run's approval record. Before it writes the
fingerprint, it runs that skill's posted-reading check with the options its completion grader
applies. If the check refuses, the extract refuses and writes no snapshot. This applies to every
skill in `aar_scan.SCOPED_SKILLS`, not only batch-shift, because the Canvas skills post, write the
record and snapshot in the same order.

The completion grader keeps ownership of its options. Each grader exposes its posted-reading check
as one callable entry point, and the extract calls it rather than holding a second copy of any
skill's rules. **A written step in each skill before `/AAR` was refused**, because a missed step
recreates this deadlock and the snapshot is the one place nothing can skip. **Gating batch-shift
alone was refused**, because the five Canvas skills would keep the same defect.

## Ruling 2 — only the newest round's fingerprint must match the current posted record

The final grade still walks every round for the key. Each round is still graded on its own
corrections against its own extract and baseline, and a later round still never re-rules an earlier
round's corrections. The posted-record fingerprint is the exception: only the newest round's
recorded fingerprint must equal the current block. Earlier rounds' fingerprints are history.

The fingerprint exists to show that the review read the hand-off as it now stands. When the newest
round fingerprinted the current record, that holds, and requiring an earlier round to match a record
correctly fixed afterwards protects nothing. This also covers a posted entry corrected after a
review, which Ruling 1 cannot reach: that change needs a fresh round, which reads the sitting where
the change happened. **A one-time release for the stuck run was refused**, because it adds an
exception mechanism and leaves that second route open. **Leaving the run stopped was refused** for
the same route.

## Ruling 3 — a landing is an address printed by a successful `gh` command in its round

For `tracker-ticket` and `skill-file` corrections, `LANDING` may be an issue address or an issue
comment address ending in `#issuecomment-<M>`. Either one counts only when the exact address appears
in the printed output of a successful `gh` command, in that round's transcripts, at or after that
round's `EXTRACTED-AT`. That replaces the any-`gh`-call evidence for new tickets as well.

A comment address is unique, so output containing it shows that this round created that comment.
**Reading the comment's creation time from GitHub at grade time was refused**, because the grader
reads offline and its verdict would depend on the network. **Filing every such correction as a new
ticket was refused**, because it duplicates a ticket that already exists.

## Taken as conventions, not ruled

- A pull-request address is not a landing. Both dispositions name a ticket.
- Ruling 3 binds rounds whose `EXTRACTED-AT` is on or after a cutoff constant, following
  `POSTED_READING_FINGERPRINT_CUTOFF` and `UNREAD_REMAINDER_CUTOFF`, so a re-grade of an older run
  is not newly failed.
- Ruling 1 refuses only new extracts, because an existing extract is never rewritten.
- The stuck run needs no new round: its round 2 already fingerprinted the corrected block, so
  re-running its terminal grade after the build is its release.

## Consequences

Eight completion graders each gain one posted-reading entry point, and the extract gains one
refusal. The stuck run can reach a clean terminal grade. A landing claimed in a round's record is
bound to that round's own transcript output rather than to any successful command.

## What this does not reach

- A landing made by hand outside every session transcript is graded unlanded until it is recorded
  another way.
- A record that passes its skill's check can still misreport what the portal shows; that remains
  the reading the record attests.
- A posted record changed after the newest round still refuses until another round snapshots it.

## Supersedes

- [ADR 0206](0206-a-final-review-follows-a-posted-record-and-every-review-round-keeps-its-own-files.md)
  ruling 5, its refusal whenever a round's record no longer matches that round's fingerprint. Ruling 2
  narrows it to the newest round. The snapshot refusal and the single-record fingerprint stand.
- [ADR 0206](0206-a-final-review-follows-a-posted-record-and-every-review-round-keeps-its-own-files.md)
  ruling 7, its requirement that every round be clean against its own extract, for the fingerprint
  only. Ruling 2 exempts earlier rounds' fingerprints. Per-round records, extracts, baselines and
  correction landings stand.
