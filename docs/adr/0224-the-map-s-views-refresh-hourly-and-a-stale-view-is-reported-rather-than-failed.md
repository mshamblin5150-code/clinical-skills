# The map's views refresh hourly and a stale view is reported rather than failed

[#1058](https://github.com/mshamblin5150-code/clinical-skills/issues/1058) was split out of #920's
grilling by [ADR 0168](0168-a-map-obligation-belongs-to-whoever-incurred-it-and-the-producer-stamp-hashes-the-emitter.md)
ruling 9. The implementation map's derived views (the frontier, the packet table, the dependency
graph and the sections drawn beside them) are rendered from the state block and the **live**
tracker. They go stale whenever a ticket closes, is claimed or changes label, and whenever a merge
changes the emitter's output. Only `implementation_map.py audit` compared them with a fresh render,
and nobody ran it. The ticket's thread recorded six stale instances on 2026-09-13 alone, after the
closes of #1019, #1021, #1032, #1034, #1035 and #1056.

Grilled 2026-09-14. **Seven rulings, by the clinician, on that date.** Nothing is built here; this
is the record the build reads. It supersedes
[ADR 0155](0155-the-map-render-stamps-its-producer-and-the-graph-draws-only-what-carries-an-edge.md)
ruling 5's refusal to fold the comparison into `check`, and it answers ADR 0168 ruling 9.
[ADR 0199](0199-a-map-overwrite-is-attributed-rather-than-prevented.md) stands unchanged.

## Measured before ruling, at `ac2fa385`

**`check` and `audit` cost the same.** Against the live tracker, with a population of 1,262 records
read and no unread remainder, `check` took 1m35.5s and `audit` took 1m34.8s. Both build the same
`Live` read: the issue harvest plus one `blocked_by` call per mapped ticket. What `audit` adds is an
in-memory `render` and a string comparison per section in `derived_sections`. ADR 0155 ruling 5
refused the fold because *"`audit` took over two minutes"*; that figure was the tracker read, which
`check` already pays. Had the comparison been the cost, `audit` would have measured materially
slower than `check`. At that reading `audit` reported `Current frontier` and `Packet table` as
`stale-derived-view`.

**One `publish` costs about 440 requests.** The state block mapped 212 tickets across 200 packets.
`publish_body` builds a `Live` read, and `cmd_publish` then calls `revalidate_after_publish`, which
builds a second one. The harvest's cache spares the second issue read but not the second set of 212
`blocked_by` calls. GitHub's documented REST allowance for `GITHUB_TOKEN` is 1,000 requests per hour
per repository.

**Ticket activity outruns that allowance per event.** The repository's issue events counted 168,
175, 207 and 190 closes, reopens, label changes and assignment changes on 2026-09-10 through
2026-09-13, with a peak of 30 in one hour. GitHub's workflow triggers include no event for adding or
removing an issue dependency.

**Nothing requires a refresh.** No skill, agent doc, hook or workflow runs or requires `publish`
after a merge. The only instruction is rendered into #596 itself: `MAINTENANCE_RULE` item 8 and the
`HOW_TO_UPDATE` line. `checks.yml` runs `map_scan.py` with read-only issue permission, and
`implementation_map_post_hook.py` speaks only at a ready flip and at an ADR merge.

**`publish` rewrites unconditionally.** `publish_body` calls `update_issue_body` whenever the
state-hash comparison passes, whether or not any section changed.

## Ruling 1. The views are both detected and refreshed

`check` compares the published derived sections with a fresh render, and a scheduled job refreshes
them. **This supersedes ADR 0155 ruling 5's refusal**, whose ground is the measurement above.
ADR 0155 ruling 5's walked-population line and its limits row stand in substance; both change to say
the views were compared.

Detection alone was refused because the published frontier stays wrong between sessions, and the
thread shows the written instruction is not followed. Refresh alone was refused because a broken
refresher would then fail silently, with nothing in the everyday command to notice.

## Ruling 2. The refresh is an hourly scheduled workflow on `main`

A GitHub Actions workflow on a schedule runs `implementation_map.py publish` from `main`, with the
built-in `GITHUB_TOKEN` granted `issues: write`. One mechanism covers both triggers ADR 0168 ruling 9
named: tracker movement, and a merge that changes the emitter.

**A per-event trigger was refused on the measurement above.** At 2026-09-13's pace it would exceed
the built-in token's hourly allowance, and dependency changes would still need a timer. A personal
access token with write access to issues would lift the allowance; that credential was not adopted.
**A 30-minute schedule with CI skipping the post-publish revalidation was refused** because it
changes the command's behavior, not only its schedule.

The gap between runs is covered by ruling 6, and `claim` reads the live tracker, so an hour-old view
cannot produce a wrong claim.

## Ruling 3. The job writes only when a view or the stamp changed

The scheduled publish writes #596 only when a derived section differs from a fresh render or the
producer stamp no longer matches the emitter in the checkout. Otherwise it logs that the views are
current and writes nothing. The Snapshot's date is excluded from the comparison, as
`derived_sections` already excludes the Snapshot.

**Always rewriting was refused.** It would add up to 24 no-op edits a day to #596, and the host caps
how far back a record's **revision chain** can be read; ADR 0199 ruling 5 makes that chain the
durable trail by which a lost overwrite is attributed. The cost is stated: the Snapshot's date then
records the last change, not the last check. The workflow's run log carries the last check.

## Ruling 4. A collision relies on the existing guard, and `STATE CHANGED` is a green skip

No cross-machine exclusion is added, and ADR 0199 ruling 1 stands. `cmd_publish`'s state-hash
comparison immediately before the write refuses when the state changed during the read. In the
scheduled job that refusal means another writer just wrote: the job logs it, succeeds, and the next
run retries.

The window left is between that last comparison and the write. An `apply-delta` landing there is
overwritten; its own read-back exits 1 with `READ-BACK FAILED`, and re-running the same delta repairs
it because placement accumulates. Ruling 3 makes the job's writes rare.

**A lease on #596 honored by every writer was refused**: it reverses ADR 0199 ruling 1 and obliges
every local tool. **Failing the job on `STATE CHANGED` was refused**, because a red run for someone
else's legitimate write teaches that red means nothing.

## Ruling 5. A real failure fails the run and stops

A short tracker read, a refused body, a failed read-back, a failed revision harvest, or an exhausted
allowance fails the workflow run with the tool's own message. The job does not retry within the run
and writes nothing to the tracker about the failure. The run blocks nothing, as ADR 0002 rules for
every check here. It is visible through GitHub's failure notice for a scheduled workflow and through
ruling 6's report in the next `check`.

**A tracker comment on failure was refused**: an unattended writer would accumulate one per failed
hour. **A retry within the run was refused**: it doubles the spend on the failure most likely to be
the allowance, and a failed read-back is exactly what should end the run.

## Ruling 6. A stale view is reported by `check`, and neither `check` nor `map_scan` fails on it

`check` prints, on every run, how many of the published derived sections differ from a fresh render
and names them, with the remedy of waiting for the scheduled refresh or running `publish`. A stale
section is not a finding and does not change `check`'s exit status. `map_scan.py` does not grade
stale views.

**A failing finding was refused.** ADR 0168 ruling 1 ties each finding to the session that incurred
it, and ruling 9 found that a stale view has no such owner. As a finding it would turn `check` red for
up to an hour after nearly every ticket close, for sessions that owe nothing, and it would put a red
row on `main` after every merge.

`audit` keeps its `stale-derived-view` finding as the full rebuild-and-compare.

## Ruling 7. #596's own maintenance text moves the refresh off the closeout

`MAINTENANCE_RULE` item 8 is rewritten to say that closing a ticket or a native blocker stales the
frontier, graph and packet table; that a scheduled job refreshes them hourly, so a closeout owes no
`publish`; and that `publish` remains available when the views are needed current immediately. Its
pointer to `map_scan.DECLARED_LIMITS` stays. The `HOW_TO_UPDATE` line reads that the derived views
refresh hourly, and names `publish` as the way to refresh them now.

**Keeping the closeout duty was refused**: it keeps a written obligation the record shows is not
followed, and adds a manual overwriter where the job already writes. **Deleting item 8 was refused**:
it also removes the sentence explaining why a closed blocker leaves the graph stale.

## Consequences recorded as derived rather than ruled

- **The limits row changes.** `implementation_map.DECLARED_LIMITS["clean-check-derived-views"]`
  states that a clean `check` does not establish view agreement; after ruling 1 it states instead
  that `check` reports agreement without grading it.
- **Declared limits the build writes into the owning objects**: a dependency change is reflected only
  at the next scheduled run, and GitHub may delay a scheduled run under load; an edit made with
  `GITHUB_TOKEN` starts no workflow run, so `tracker.yml`'s edited-#596 producer-stamp step does not
  grade the job's own writes; and ruling 4's collision window remains.
- **Not reached here.** Whether the in-process `authorize_issue_body` grades everything the command
  route grades for this writer is #1148's. Whether a `GITHUB_TOKEN` publication is graded by any host
  is #1146's.

## What must not come out of this

- **A job that reconciles.** The scheduled job runs `publish` only. Reconciliation stays the reviewed
  judgment `CONTEXT.md` defines, and the job never runs `apply-delta` or moves `reconciled_through`.
- **A publish from an unverified population.** #993's short-read refusal stays in front of every
  render the job makes.
- **A red `check` for a view nobody owns.**
