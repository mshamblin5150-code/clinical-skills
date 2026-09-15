# The map's direct writer grades through analyze and runs no readback

[#1148](https://github.com/mshamblin5150-code/clinical-skills/issues/1148) was split out of #1124's
grilling by [ADR 0188](0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md)
ruling 5. `tools/implementation_map.py` publishes by calling `gh` from inside the process, so no
`PreToolUse` hook ever sees a `gh` token, and `tracker_publish_hook.authorize_issue_body` is the only
gate on that route. That seam assembled its checks by hand, one call per grader, while the command
route runs `analyze`. The ticket's own figure for how many graders the seam ran went stale three
times as each new grader was wired into both routes separately, and the seam never ran the PHI layer
or branch scope. [ADR 0224](0224-the-map-s-views-refresh-hourly-and-a-stale-view-is-reported-rather-than-failed.md)
then added an hourly writer using `GITHUB_TOKEN`, whose edits start no `tracker.yml` run, so for that
writer the seam is the only grader before or after publication.

Grilled 2026-09-15. **Three rulings, by the clinician, on that date.** Nothing is built here; this is
the record the build reads.

**Measured at:** 8b4e44faab1403b858e522f37385291b00ebe112

## Measured before ruling

**The writer's publication population is two calls.** `update_issue_body` is reached only through
`publish_body`, which `publish`, `apply-delta` (including its direct placement form) and
`init --adopt` use; `create_issue` is reached only through `init`. `claim` is read-only, so the
ticket's verb table overstates the publishing population by that verb. `init` passes its title to
`gh` with no grade at all.

**Every retained revision of #596 grades clean through `analyze`.** The issue's `userContentEdits`
reported 100 revisions and 100 were read, unread remainder 0. Each was passed to
`tracker_publish_hook.analyze` as an issue-body edit with #596's live labels, a complete corpus index
and a freshly fetched `origin/main`. All 100 returned no finding of either posture, and the current
body returned none as an edit or as a create. **The measurement discriminates:** the same call on the
current body with one planted defect returned `branch:unresolved-path` (deny) for a `blob/main` URL to
an absent file, `branch:repo-relative-link` (deny) for a relative Markdown link, and `phi:ssn`
(advise) for a synthetic SSN shape. Had the history carried those shapes, the run would have printed
them.

**Three of the ticket's listed families cannot fire on this writer.** Filed-from already returns
`not-graded` for a body carrying the map's producer stamp, which is
[ADR 0177](0177-both-publish-routes-grade-a-body-through-one-grader-and-a-lost-body-refuses.md)
ruling 3's command-form exemption. The AAR quotation gate reads a body file under a run's
`aar/publications/`, and this writer holds a string. The missing-discriminator row runs only on
comment routes, and this writer edits issue bodies.

**The readback would cite 245 records per write.** `tracker_readback.citation_numbers` over the
current #596 body returns 245 numbers. The readback lives in `grade_command`, outside `analyze`, and
refuses nothing.

## Ruling 1 — the direct writer grades through `analyze`

`authorize_issue_body` stops assembling graders and calls `analyze` on the body, with the title graded
the same way where one is published. A `deny` finding refuses the publication; an `advise` finding is
returned as a report line the writer prints. The producer-stamp check stays on top as the one grade
only this writer has.

**Whatever `analyze` grades, the direct writer gets.** That is the repair for the drift, not a list of
families moved: a grader added to `analyze` later reaches both routes without a second wiring. A rule
on the command's form still does not fire, because this writer supplies no command, which leaves
ADR 0177 ruling 3 unchanged.

**PHI stays advisory by construction.** `analyze` already emits PHI findings with the `advise`
posture, so an exception-only seam turning [ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
ruling 4's advisory half into a refusal is not a reachable outcome of this design.

Adding PHI and branch scope to the hand-built list was refused: it needs a second advisory channel
and keeps the drift. Declaring the gap without a build was refused: the hourly writer has no other
grader.

## Ruling 2 — an absent corpus is reported and the publication proceeds

When the corpus layer cannot load, which is every scheduled run because `scratch/` never reaches a
runner, the writer prints that the PHI corpus layer is incomplete, grades with the shape layer, and
publishes. That is the command route's arrangement in `grade_command`.

Refusing unless the caller acknowledged the absence with a flag, which is `phi_scan.py`'s own
arrangement, was refused: it would reopen the split between routes that ruling 1 closes, and it would
turn the hourly job red over a layer that can never load there. Skipping PHI in `--scheduled` mode was
refused because it rests on the job authoring no new text, which nothing checks.

## Ruling 3 — the direct writer runs no readback

The readback exists so an author sees the current state of records they are about to cite. The map
writer renders from a population-gated live read of every record it cites, the readback refuses
nothing, and at 245 aliases per write it would add a large GraphQL request to every `apply-delta`,
`publish` and hourly run. The absence is a declared limit rather than a silence.

Running it on every write was refused on that cost. Running it on hand-typed verbs only was refused
because it would split one writer's report by who launched it.

## Consequences recorded as derived rather than ruled

- **Record context.** `publish_body` reads #596 before grading and passes that record, labels
  included, to `analyze`, and the writer refreshes `origin/main` as `grade_command` does. `init`
  without `--adopt` has no number yet and grades context-blind, as a typed `gh issue create` does.
- **The limits row narrows.** `implementation_map.DECLARED_LIMITS["direct-writer-publication-gates"]`
  names the readback's absence and ruling 3's ground instead of PHI and branch scope.
  `github-token-no-follow-up-workflow` stands: the scheduled job is graded before publication and still
  never after it.
- **Decision 3 of the ticket, answered per writer.** The hourly `GITHUB_TOKEN` writer is graded by
  the seam before publication only. A session's `publish` or `apply-delta` is graded by the seam
  before publication and by `tracker.yml` after it.
- **One sentence in `docs/agents/issue-tracker.md` moves.** The paragraph opening *"Both publication
  hosts now run one body row set"* becomes an account of both routes running `analyze`, keeping its
  statement that the hook's publisher boundary belongs to `tracker_publish_hook.NOT_REACHED`.
- **A future refusal is preserved.** A packet outcome that later cites an unresolved `blob/main` path
  refuses the write; `preserve_refused_outcomes` already keeps the authored outcome, and a refused
  scheduled run fails under ADR 0224 ruling 5.
- **The hook marker is not written.** `write_marker` records the pre-publication hook's activity, and
  the direct writer is not that hook.

## What must not come out of this

- **PHI becoming a refusal on either route.** ADR 0083 ruling 4's reasoning is unchanged.
- **A second hand-assembled list inside the seam.** A grader wired only into `authorize_issue_body`
  reintroduces the drift ruling 1 retires.
- **A claim that the map writer is covered for the argv-list publications.** ADR 0188 ruling 5's
  13 measured ad-hoc argv-list publications call neither route, and nothing here reaches them.
