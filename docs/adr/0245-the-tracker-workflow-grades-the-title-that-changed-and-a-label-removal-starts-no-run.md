# The tracker workflow grades the title that changed and a label removal starts no run

[#1152](https://github.com/mshamblin5150-code/clinical-skills/issues/1152) was filed out of #1124's
grilling as four ways `.github/workflows/tracker.yml` is quieter than it reads. Its findings 3 and 4 were
moved to #1146 by [ADR 0242](0242-the-hook-and-the-workflow-are-bound-by-a-declared-correspondence.md)
ruling 13 and are built. This record rules the two that stayed: a label removal starts no run, and a
title-only edit receives no body grade.

Grilled 2026-09-15. **Five rulings, by the clinician, on that date.** Nothing is built here; this is the
record the build reads.

**Measured at:** 39d1bece5661c8b961973020267233dfe6c4b3e5

## Measured before ruling

**The pure removal the ticket names is an unwatched write.** The one publisher of a bare
`gh issue edit --remove-label` the ticket cites is the `merge-receipts` job, which authenticates with
the workflow's built-in token. [ADR 0241](0241-a-merge-receipt-is-graded-before-it-posts-and-a-workflow-token-write-is-an-unwatched-write.md)
measured that such a write starts no workflow run, so adding `unlabeled` to the trigger list would not
reach it. A paired removal and addition already starts a run through `labeled`, which #1014's sweep
measured live.

**A removal only takes a trigger away.** `tracker_branch_scope.grade_record` fires `branch:in-flight`
only while the label is present; its other two triggers, an unresolved path and a comment declaring its
own completion, are properties of a body graded when that body was published. An `unlabeled` run would
re-grade unchanged text, and the only new finding it could produce is a cited path deleted from `main`
since publication: repository drift, not the removal.

**The ticket's decision 2 named a reader that already carries titles.** `tracker_scan.records_from_github_event`
keeps a changed title on the `edited` path. The narrowing is in `tracker_bodies.records_from_github_event`,
which returns no record when `body` is absent from `changes`, as #928's sweep recorded.

**The title gap is wider than a title-only edit.** `tracker_bodies.records_from_github` reads `body` and
never `title`, so in CI no title has been graded for the two predicates
[ADR 0099](0099-a-control-character-in-a-published-tracker-body-is-refused-at-the-publish-event-and-graded-at-every-one.md)
ruling 5 ruled onto titles, on `opened` or on any edit. `tracker_coordinates` and `tracker_measurements`
mention no title in their event modes, and `tracker_records.from_actions_event` gives branch scope a
`body` surface for every `issues` and `pull_request_target` event. In CI a title receives the PHI shape
layer and nothing else of its own.

**At the hook, a title is graded by more.** `tracker_publish_hook.analyze` runs both control-character
predicates, the coordinate grader, the measurement grader and branch scope's path triggers over a title.

**The two ungated title calls have different histories.** The coordinate call arrived in `3aadafef` with
`test_an_unanchored_coordinate_in_a_title_is_denied`, so title grading there was built and tested.
The measurement call arrived in `3930c342` directly beneath it, and neither that commit, a test, nor
[ADR 0196](0196-a-published-figure-names-its-population-and-is-re-derived-at-publication.md) mentions a
title. Neither ADR 0189 nor ADR 0196 rules titles in or out.

**A declaration cannot live in a title.** `tracker_measurements.grade_current` recognizes the label only
at the start of a line, so on a one-line title it can do nothing except deny a title that happens to open
with the label.

## Ruling 1 — `unlabeled` stays out of the trigger list

A label removal is a row under ADR 0242 ruling 7 in which neither publication host runs anything, and the
row records why: a removal only takes triggers away, and the removal the ticket named is an unwatched
write no trigger reaches. **Adding `unlabeled` with branch scope alone was declined**: it costs a run per
removal and buys only a drift re-grade of text already graded. **Adding it with every check was
declined** for the same reason, plus a PHI re-scan of an unchanged body.

## Ruling 2 — CI grades a title for ADR 0099 ruling 5's two predicates

The body-integrity event reader emits a changed title as its own record, so a finding names the field a
reader has to edit. It does so on `opened` and on any edit whose changes include the title, and only the
control-character and flanked-carriage-return predicates run on that record; every other row stays
body-only, as at the hook. The dispatcher selects the body-integrity check on a title-only edit. The
workflow reports and the hook refuses, which is the asymmetry ADR 0099 already records. **Declaring the
gap instead was declined**: ADR 0099 ruled a control character graded at every publish event and its
ruling 5 ruled titles in, so a declaration would retract a ruling rather than state a limit.

## Ruling 3 — CI grades a title with the coordinate check

The coordinate grader reads the same title record ruling 2 introduces. ADR 0189 gains a dated line
ratifying titles as a graded surface at both hosts, which is what its build already did at the hook.
**Leaving titles out of CI was declined** as a tested hook posture with no workflow partner and no reason.
**Removing titles at both hosts was declined** because a coordinate in a title is a real shape and its
remedy, moving the coordinate out of the title, is one an author applies alone.

## Ruling 4 — titles leave the measurement check

The hook's measurement call gets the body gate the other body-only checks carry, and CI stays body-only.
ADR 0196 gains a dated line stating that the declaration is record-level, so a title is not a surface for
it. **Grading titles in CI too was declined** as spreading an accident to a second host. **Keeping the
hook as it stands and declaring the asymmetry was declined**: it asks ADR 0242's correspondence to record
as chosen a posture no ruling or test chose.

## Ruling 5 — CI's branch-scope run grades the text that changed

On `opened` it grades the title, with path triggers only, and the body. On a title-only edit it grades
the title and not the unchanged body. On a body edit it grades the body. On `labeled` it grades the body,
because adding a label adds a trigger. **Grading the title while still re-grading the body on a title edit
was declined** as the drift re-grade ruling 1 refused. **Leaving branch scope body-only was declined** as
ruling 3's objection again.

## Consequences recorded as derived rather than ruled

- **Pull request titles follow the same rulings.** `pull_request_target` `opened` and title edits take
  rulings 2, 3 and 5 as issues do, because the hook grades a pull request title the same way.
- **An edit changing both title and body grades both.**
- **The PHI shape layer needs no change.** `tracker_scan` already grades exactly the changed fields.
- **Filed-from and the map producer stamp stay body-only**, being properties of a body.
- **No build edge to #1149.** Under ADR 0242 rulings 10 and 14, whichever of #1149 and #1152 builds second
  updates the correspondence rows these rulings move.

## What this does not reach

- **An unwatched write of any kind.** Ruling 1 records that the removal is unreached; it does not reach it.
- **Drift in a published body.** A cited path deleted from `main` after publication is found only when some
  other event re-grades that body.
- **Whether a title's words are right.** Every ruling here grades mechanical properties of a title.
