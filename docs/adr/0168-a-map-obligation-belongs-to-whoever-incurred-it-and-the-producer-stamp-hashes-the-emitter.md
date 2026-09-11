# A map obligation belongs to whoever incurred it and the producer stamp hashes the emitter

[#920](https://github.com/mshamblin5150-code/clinical-skills/issues/920) was filed because a
grilling session's standing tail loads implementation-map findings by construction: merging the ADR
puts `main` past the reconciliation anchor, and flipping the ticket to `ready-for-agent` puts a ready
ticket in no packet. Nothing in the ruled workflow names either. The ticket's thread then recorded an
instance at almost every grilling session between 2026-09-06 and 2026-09-11 UTC, and three further
shapes: an anchor one session could not move because of another session's ticket, a command that
could not see half of what it was asked about, and a producer stamp that refused correct publishes.

Grilled 2026-09-10. **Nine rulings, by the clinician, on that date.** Nothing is built here; this is
the record the build reads. It amends
[ADR 0089](0089-the-map-gate-is-an-offline-grader-over-a-harvest-and-the-reconciliation-obligation-is-anchored-on-a-field-the-delta-sets.md)
ruling 3's single-commit anchor,
[ADR 0106](0106-the-implementation-map-is-reconciled-by-an-in-tree-tool-rather-than-gated-at-publication.md)
ruling 4's second half, and
[ADR 0155](0155-the-map-render-stamps-its-producer-and-the-graph-draws-only-what-carries-an-edge.md)
ruling 1's commit. Ruling 7 also codifies the flip-time placement the clinician ruled on #920 on
2026-09-08, which until now existed only as a tracker comment.

## Measured before ruling, at `fd9f532`

Freshness gate `FRESH` at `fd9f532` when the session began. Before the record was written `main` had
moved to `6222111`, one merge touching only ADR 0166's file; the branch was brought forward and the
gate read `FRESH` again. Tracker figures are readings of a moment and are dated to the comment that
took them.

**The anchor waited on other sessions.** `_apply_delta_under_lock` sets `reconciled_through` only
when `placement_coverage` finds no unplaced ready ticket anywhere. #920's thread records it holding
three sessions on 2026-09-10 and 2026-09-11 UTC: #866's session behind #1029, #867's behind #1036,
and #875's behind #1047. In each case the session had placed its own ticket.

**The anchor row counts ADR commits and nothing else.** `map_scan._git_log_after` runs
`git log <anchor>..HEAD -- docs/adr/`. A code-only merge does not load it.

**`check` cannot see that row, and `audit`'s `stale-snapshot` is a different condition.** A
2026-09-07 comment on #920 called `stale-snapshot` the same condition under a second name. The code
says otherwise: `cmd_audit` compares the Snapshot's `default-branch commit` line with the branch head,
and `render` rewrites that line on every `publish`. Had the two been one condition, a publish with no
delta would leave `stale-snapshot` firing; instead it clears it. So `stale-snapshot` fires after every
merge, clears without a reconciliation, and its message, *"the map has not been reconciled since"*,
claims something it does not measure. It is the launderable anchor ADR 0089 ruling 3 refused.

**The producer stamp compares a commit, and the emitter had not changed.** `producer_stamp_problem`
requires the stamp to equal `git rev-parse HEAD` of the checkout running the check. On 2026-09-11 UTC
the edited-#596 workflow refused a publish stamped `da720d2` and the next one stamped `730fc1a`, both
from branch worktrees. `tools/implementation_map.py` is byte-identical at `da720d2`, `730fc1a` and
`b726bd1`, and its last change is `b92c7e3` on 2026-09-09; had the file differed, `git diff --quiet`
would have exited 1. Both refusals were of the renderer `main` held.

**Every ADR on `main` since 2026-08-27 came from a Claude Code session.** Of first-parent merges on
`main` from that date to `fd9f532` that add a file under `docs/adr/`: 64 from `claude/` branches, 37
from desktop `worktree-bridge-*` branches, 1 from `rescue`, and none from `codex/`. No direct
first-parent commit added one.

**The per-merge ADR unit is readable from local git.** `git log b726bd1^1..b726bd1 -- docs/adr/`
lists `acc5bf9`, the merge of `main` into #1047's branch, but
`git diff --name-only --diff-filter=AM b726bd1^1 b726bd1 -- docs/adr/` names ADR 0166 alone. The
diff against the first parent is the unit; the log is not.

**The installed Claude Code supports the hook ruling 7 needs.** The published hooks reference does not
document the fields, so they were read from the 2.1.261 build: the `PostToolUse` input carries
`tool_input` and `tool_response`, its output accepts `hookSpecificOutput.additionalContext`, and a
`Stop` hook may return `decision: "block"` guarded by `stop_hook_active`. `Stop` fires at the end of
every turn, not once per session.

## Ruling 1. Each finding has one owner, and the anchor no longer waits on ready tickets

A session discharges the ADR finding once its own ADRs are reviewed, whether or not some other
session's ready ticket is still unplaced. **This amends ADR 0106 ruling 4's second half.** Its first
half stands: a `publish` never advances the anchor.

ADR 0106 ruling 4 coupled the two because an anchor stamped over an unplaced ticket asserts a
currency the map does not have. But the unplaced ticket already has its own row, `unmapped-ready`,
and that row fails CI. The coupling let one finding hold the other, and made the anchor the property
of whoever placed the last ticket. Now the ticket row names the ticket, which points at the session
that flipped it, and the ADR row names ADRs, which point at the sessions that merged them.

Keeping the coupling was the alternative, and it is refused because it leaves one finding with no
owner. The 2026-09-08 flip-time placement already narrows the unplaced window to the placement's
running time, so the ticket row needs no backstop from the ADR row.

## Ruling 2. An ADR is discharged by its own review record, and the anchor is the floor beneath the records

The map's state holds one review record per ADR. `reconciled_through` becomes a floor: it advances
past a first-parent commit once every ADR that commit adds or changes has a record. `map_scan`
reports each ADR above the floor that has no record, by number, instead of a commit count.

**The unit is the ADR files a first-parent commit on `main` adds or changes, compared with its first
parent.** A branch that merged `main` into itself therefore owns only its own ADRs. A later
correction to an existing ADR loads that ADR again, which is what the current predicate already does
for any commit under `docs/adr/`.

Two alternatives were refused:

- **Strict: the anchor moves only if every ADR behind it is this session's.** That brings cross-session
  blocking back, keyed on merge order instead of on ready tickets.
- **Permissive: the anchor moves over anyone's ADR.** A session would vouch for ADRs it did not
  review. A comment on #920 refused this before the grilling as moving the instrument to meet the disk.

ADR 0089 ruling 3 refused a highest-cited-ADR anchor because most ADRs are cited by no packet, which
would leave an ADR that honestly creates no work with nowhere to be recorded. A review record is not
that anchor: ruling 6 gives it an explicit no-work disposition.

## Ruling 3. `check` reports unreconciled ADRs through the predicate `map_scan` calls

The per-ADR predicate lives once, in `tools/implementation_map.py`. `map_scan` calls it as a row and
`check` calls it as a finding; `audit` inherits it because it runs every `check` finding. `check`'s
printed scope line names the ADR records as graded. This is ADR 0155 ruling 4's one-predicate,
several-callers arrangement.

The predicate reads local `git` and one issue body, so `check` stays the cheap command ADR 0155
ruling 5 requires. **Sending the session to run `map_scan` over a fresh harvest instead is refused**:
that harvest is the `gh api --paginate` read
[#993](https://github.com/mshamblin5150-code/clinical-skills/issues/993) measured returning 151, 67
and 645 records on three identical calls.

## Ruling 4. `audit`'s `stale-snapshot` finding is deleted

The Snapshot's `default-branch commit` line stays, as information. What `stale-snapshot` purported to
catch is held by real findings: an unreviewed ADR by ruling 3, and an out-of-date published view by
`audit`'s existing `stale-derived-view`.

Rewording it honestly, *rendered at one commit, head is another*, was refused because it would still
fire after every merge, including one that changes nothing on the map, and name no action that
changes the map.

## Ruling 5. The producer stamp hashes the emitter, not the checkout commit

The stamp records a hash of `tools/implementation_map.py`, taken over git-normalized text bytes as
`artifact_provenance.text_file_identity` takes them, and the predicate compares it with the same hash
of that file in the checkout running the check. **This amends ADR 0155 ruling 1's commit.** Ruling 1's
placement in the derived Snapshot and its repository-relative path both stand, and the commit may stay
in the Snapshot as information.

ADR 0155 ruling 1 put the commit in the stamp to catch an older in-tree renderer. The property it
wanted is a different emitter file, and content identity states it directly. It passes both refused
publishes above, still fails an older renderer, and also fails an uncommitted local edit to the
emitter, which a commit stamp certifies falsely. The guideline build already uses producer-file
identity for the same reason.

Two alternatives were refused:

- **Accept an ancestor commit with an unchanged emitter.** A branch commit that has not merged is not an
  ancestor of `main`, so both refused publishes would still be refused.
- **Keep the commit and require publishing from `origin/main`.** #875's session tried it on 2026-09-11
  UTC: it fast-forwarded to `b726bd1`, the lock refused it twice, and `main` moved again meanwhile.

## Ruling 6. A review record holds its ADR and what the recording delta did

The record carries the ADR and the packets the recording delta added or changed, derived from the delta
rather than typed. When that list is empty the record requires one authored sentence saying why the ADR
creates no work, and a blank sentence is refused, as ADR 0106 ruling 5 refuses a blank `outcome`.

A record whose ADR the floor has passed is removed from the state. The ADR and the ticket comment
remain the durable history, and the state block does not grow with every ADR.

A bare ADR number was refused because it cannot distinguish *reviewed* from *not looked at*, which is
the bare-`clean` shape `checks_ledger.SUBSTANTIATED_CLEAN` exists to refuse. Requiring a sentence on
every record was refused because a derived packet list already says what the review decided.

## Ruling 7. A `PostToolUse` hook speaks at the flip and at the ADR merge

A hook registered in `.claude/settings.json` adds context to the session immediately after either act:

- **A flip to `ready-for-agent`**, by `gh issue edit --add-label` or `gh issue create --label`. The
  context names the ticket and says to place it now if it is not already in a packet, with the
  `apply-delta --ticket` form. On `create` the number comes from the command's output. It needs no
  map read, because `apply-delta` is inert for a mapped ticket (ADR 0106 ruling 6).
- **A merge that lands ADR files on `main`.** The context names each ADR the session's branch adds or
  changes and says to record its review. The ADR set comes from local `git`.

The hook reads no tracker record and refuses nothing; the command has already run. Command
classification reuses `tracker_publish_hook`'s parsing rather than a second parser, on
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s terms.

**This is not the mechanism ADR 0089 ruling 6 declined.** That ruling refused a new written closeout
step, and deferred a `PreToolUse` hook on `git push` because it would put a whole-tracker harvest in
front of every push. This hook harvests nothing and is not a written step. Prose in the grilling tail
was refused on ADR 0089 ruling 6's own ground, #214's *what a written instruction cannot do is fail*.
Leaving CI's post-merge red as the only signal was refused because it lands on the next session.

Declared limits, to live in the hook module's own limits object: a flip made in the GitHub web UI; any
session that runs no repository hook, which includes Codex; a merge made outside the session; and a
session that reads the context and does not act on it.

## Ruling 8. No `Stop` hook refuses to end a session that still owes a discharge

Two nets were priced and refused:

- **A `Stop` hook that reads #596.** `Stop` fires at every turn end, so this is a tracker read per turn
  in every session. It would also block turns that end while the ruled background placement is still
  running, interrupting correct work.
- **A `Stop` hook reading a session-local ledger.** It would mark an obligation discharged on
  `apply-delta`'s own report, which
  [#966](https://github.com/mshamblin5150-code/clinical-skills/issues/966) recorded printing
  `packets written: 1` while a placement was lost.

The residue is a session that ignores ruling 7's context and never runs `check`. CI fails on the next
push, and after rulings 1 and 2 the failing row names the ADR or ticket, which names its owner.

## Ruling 9. `stale-derived-view` is a separate ticket

Only `audit` reports a published view that differs from a fresh render. It is not loaded by the tail:
`render` computes status, frontier and ready count from the live tracker, so views go stale whenever a
ticket closes, is claimed, or changes label, and whenever a merge changes the emitter's output. It has
no owner in ruling 1's sense, and its most promising remedy, a CI publish after every push, cannot run
safely before #993. Filed as [#1058](https://github.com/mshamblin5150-code/clinical-skills/issues/1058).

## Consequences recorded as derived rather than ruled

- **An `unclassified-collision` finding needs nothing new.** It surfaces in the placing session's own
  `apply-delta` output, so rulings 1 and 7 already give it an owner.
- **Migration.** The floor starts at the current `reconciled_through` with no records.
- **Not reached here.** Two recording deltas conflict under the state-hash guard, and whether that guard
  refuses correctly is #966's. Whether a population read is complete is #993's. Nothing grades whether a
  record's no-work sentence is true, which is ADR 0106's substance limit inherited whole.

## What must not come out of this

- **A machine that writes review records or packets.** The hook speaks and the record is authored.
  Reconciliation stays the judgment `CONTEXT.md` defines.
- **A relaxed gate.** `map_scan` keeps failing on both rows. What changes is that each red row names
  the one session able to clear it.
