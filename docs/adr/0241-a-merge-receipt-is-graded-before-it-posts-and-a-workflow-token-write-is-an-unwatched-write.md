# A merge receipt is graded before it posts and a workflow-token write is an unwatched write

[#1146](https://github.com/mshamblin5150-code/clinical-skills/issues/1146) found that the tracker's
own merge receipts are graded by neither host: `tracker_publish_hook.py` does not run on a GitHub
runner, and a comment published with the workflow's built-in token starts no `tracker.yml` run.
Grilled 2026-09-15 against `8b4e44fa` and recorded against `0fa62b25`; the clinician ruled every
point below on 2026-09-15. Nothing is built here; this is the record the build reads.

## Measured before ruling

### The trigger gap holds, and it is GitHub's documented behavior

The ticket measured 0 of 8 isolated bot comments producing a tracker workflow run against a control
of 65 of 65 human comments in the same window. Sweep comments on #1146 added live instances through
2026-09-15, the latest being two receipts on #1111 with no `issue_comment` run after them. An event
triggered by the built-in token does not itself trigger further workflow runs; the defect is that a
publisher here relied on it without counting it.

### The workflows write to the tracker at three sites, all with the built-in token

Derived from the three files under `.github/workflows/` and every tool they invoke, not assumed:

| workflow and job | write | checked before writing |
| --- | --- | --- |
| `tracker.yml`, `merge-receipts` | `gh issue comment` with the rendered receipt | nothing |
| `tracker.yml`, `merge-receipts` | `gh issue edit --remove-label "in flight"` | carries no text |
| `implementation-map-refresh.yml`, `publish` | a body edit of #596 inside `implementation_map.py publish --scheduled` | `authorize_issue_body` |

No workflow references a repository secret, and `gh secret list` returned no secret name, so no
personal access token exists today. `tracker_merge_receipt.py` imports no grader.

### The receipt text is not wholly fixed

`render_receipt` fills a fixed template, but its `Merge claim:` value is copied from a binding line
the pull request's author wrote. The binding grammar bounds that value; it does not fix it, and it
bounds only what today's producer writes.

### Two ratified premises rest on a run that never happens

[ADR 0099](0099-a-control-character-in-a-published-tracker-body-is-refused-at-the-publish-event-and-graded-at-every-one.md)
ruling 4 declares that the workflow covers both publishers after the fact.
[ADR 0105](0105-the-branch-scope-vocabulary-gains-a-verified-on-main-sentence-and-the-in-flight-label-is-discharged-at-merge.md)
ruling 7 keeps the receipt `fullmatch` escape on the ground that *"the workflow grades its own
publication"*, and the `merge-receipts` step carries the comment *"Publish first:
tracker_branch_scope's receipt fullmatch is the deliberate escape while the ticket still carries
`in flight`."* That grading run never occurs, so the escape has never been exercised in production.

### Nothing keys on who wrote a record

No module under `tools/` and no workflow reads a comment's author, a bot login or an author
association. A change of credential or a match on text alone breaks no identity check.

## Ruled 2026-09-15

### 1. The receipt job grades every receipt before it posts it

The job runs each rendered receipt through the checks `tracker.yml`'s `changed-record` job runs for
an `issue_comment: created` event, then publishes. **A personal access token was declined**: it adds
a secret to rotate and a second identity on the tracker, and it buys a report a minute after the
receipt lands rather than prevention; ADR 0224 ruling 2 declined the same credential for the map job.
**`authorize_issue_body` alone was declined**: it grades body shape, coordinates and measurements and
leaves branch scope and the PHI shape layer unread. **Correcting the declaration alone was declined**,
on #1146's own terms: a correction is not a grade.

### 2. Every receipt is graded before any posts, and one refusal posts none

The posture mirrors the command route: a row that refuses at the publish hook refuses here, and the
PHI shape layer advises and never stops a post, on
[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
ruling 4. On a refusal nothing posts, `in flight` stays on every bound ticket, and the job fails with
the finding. **Posting the receipts that pass was declined** because a re-run would publish the
already-posted ones a second time. **Reporting only was declined** as the after-the-fact report
ruling 1 refused.

### 3. One command owns which checks apply to a tracker event

A single tool takes one GitHub event record, decides which checks apply to it, runs them, and reports
one section per check. `changed-record` calls it in place of its separate steps, and the receipt job
builds an `issue_comment: created` event for each receipt and calls the same tool. A new check is
therefore added once and reaches both. **The reason is recorded drift, not a hypothetical one**: the
coordinate check from #928 and the measurement check from #961 were each wired into every seam by
hand, and both closing sweeps recorded on #1146 that the receipt path had not received them.
**Keeping the per-step YAML and binding it with a test was declined**: the suite is standard library
only, so the test would read YAML as text and a reworded `if:` could satisfy it. **A comment asking
both files to stay in step was declined** as the prose-only copy
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) ruled insufficient.

### 4. The event built for a receipt carries the ticket's live labels

The job reads each bound ticket's current labels into the event it grades. On an `in flight` ticket
the branch-scope trigger then fires, and ADR 0105 ruling 7's exact-receipt escape carries a correct
receipt through it, so a producer edit that breaks the template is refused before it posts. Comment
first, then label removal, is unchanged. **An event with no labels was declined**: the trigger could
never fire on a receipt, leaving the escape untested. **Removing the label before grading was
declined**: it contradicts ruling 2, which keeps the label when a receipt is refused.

### 5. A receipt already on its ticket is skipped, and the label removal still runs

Before posting, the job reads the ticket's comments. A comment whose whole body is an exact receipt
naming the same pull request and the same claim counts as landed: the job does not post it again
and still removes `in flight`. Re-running the job is then safe after a check refusal and after a
transport failure partway through posting alike. **Declaring the duplicate as a limit was declined**:
a duplicate immutable receipt is a permanent false record and the fix is one read. **An instruction
never to re-run was declined** as a written rule that cannot fail.

### 6. The landed-receipt match reads the text, not the author

A hand-posted exact receipt counts as landed. **Requiring the `github-actions` author was declined**:
it would add this repository's first identity key, and its only effect would be a second receipt on a
ticket whose missing receipt a person had already supplied, the gap
[ADR 0049](0049-the-sweep-alias-and-the-recs-root-are-two-lookup-roots-with-two-resolution-rules-and-the-producer-guarantees-the-prefix-it-writes.md)
recorded on #518. ADR 0105's escape already treats a receipt by what it says.

### 7. The hourly map refresh stays with #1148

`implementation-map-refresh.yml` renders, compares and writes inside one command, so the workflow
never holds the body and the in-process seam `authorize_issue_body` is the only place a check can
sit. Which grader families that seam gains, and how an exception-only seam carries an advisory PHI
row, is [#1148](https://github.com/mshamblin5150-code/clinical-skills/issues/1148)'s decision 2.
**Widening this ticket was declined** because the two share the symptom and not the fix. #1148's
decision 3, that the workflow grades direct-writer publications after the fact, is false for this
writer.

Correction, 2026-09-15: this ruling formerly left #1148's decision 2 as open. That ticket was ruled
the same day in
[ADR 0240](0240-the-map-s-direct-writer-grades-through-analyze-and-runs-no-readback.md), which merged
while this record was in review: the seam calls `analyze`, PHI stays advisory by construction, and its
decision 3 is answered per writer. This ruling is unchanged; the refresh's grade is ADR 0240's build.

### 8. A write made with the workflow's built-in token is an unwatched write

The term enters `CONTEXT.md`'s Tracker section. **Calling the receipt job a third publisher was
declined**: everywhere this repository says publisher it means a harness, the Claude Code hook's and
Codex's, and a count of three invites a fix that adds a harness to a list while the hourly job stays
invisible. The property that matters is that nothing watches the write after it lands.

## What this changes in earlier records

Corrected in this record's commit, in place with a dated line beneath, on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
arrangement for a ratified record's facts:

- **ADR 0099 ruling 4**'s declaration gains that the workflow reaches no unwatched write.
- **ADR 0105 ruling 7**'s *"the workflow grades its own publication"* is replaced by the receipt job's
  pre-publication grade.

ADR 0183 and ADR 0136 restate ADR 0099's declaration as *"one of two publishers"*. Both sentences are
about harnesses and stay true under ruling 8, so neither is corrected. ADR 0189 and ADR 0224 name
this gap in their residue sections as dated readings and are not corrected.

**Corrected by the build**, because each is code or prose describing the mechanism:

- the description of `tracker_publish_hook.NOT_REACHED`'s row *"the refusing hook covers one of two
  publishers"*;
- `tools/tracker_bodies.py`'s docstring sentence naming *"either known publisher"*;
- `CLAUDE.md`'s **Tracker bodies** paragraph and `docs/agents/issue-tracker.md`'s *"Both publication
  hosts now run one body row set"* paragraph, both naming *"either known publisher"*;
- the *"Publish first"* comment in the `merge-receipts` step.

## Taken as conventions, not ruled

The command's name and module, how it builds an event record from a rendered receipt (the
`tracker_records` adapters are the obvious seam), the step-summary layout, and message wording are
the builder's.

## What this does not reach

**The label removal.** It carries no text and is not graded.

**The PHI corpus layer.** A GitHub runner has no `scratch/`, so the receipt grade runs the shape layer
only, as `changed-record` already does.

**The hourly map refresh**, under ruling 7.

**A future unwatched write.** Nothing enumerates the workflows' built-in-token writes mechanically.
The term makes a new one nameable; it does not detect it.

**GitHub's retained pre-edit revisions**, the route ADR 0083 already named.
