# The map check fails only on new debt and the debt it inherited is frozen and drained

**Measured at:** 36d6029b25913c4ec8590e568aa38197a0dc3313

[#1199](https://github.com/mshamblin5150-code/clinical-skills/issues/1199) found the
`Implementation map disagreement` step in `.github/workflows/checks.yml` red on most pushes to
`main`, so its result carried no signal, and left four questions to settle before building. Grilled
2026-10-03 against `main`, where the freshness gate read `FRESH`; the clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

The run figures were read from the GitHub Actions record for `checks.yml` push runs on `main`. They
are dated readings of a moving record and are stated here once.

**The step is red on every push, not on most.** The last green push run is 34724726542, on
2026-09-12. Every push run from 2026-09-13 through run 37122709769 on 2026-10-03 failed, 200 in a
row. In the last 100 of them the map step is the only failed step in every run, and every row that
fired was either `unreconciled-adr` or `unmapped-ready`.

**The failing gate has not paid the debt down.** The unreconciled-ADR count read off the step's own
report was 48 in run 35014161946 and 62 in run 37122709769, the newest. Ticket #1348 has been a
ready ticket in no packet for at least ten days.

**The red skips the maintainer's suite.** `Test suite` is the one step after the map step without
`if: always()`, and the PHI-disclosure step beside it has none either. Both were skipped on every
red push since the map step first ran on 2026-09-03, so the Python 3.14 suite has not run on a
push to `main` since then. The separate floor job ran the complete suite at Python 3.10 throughout.

**The landing push is red by construction.** A review record is stamped with a default-branch
commit, and `_review_covers` in `tools/implementation_map.py` accepts it only for a first-parent
commit at or after the ADR's own. So no review can be recorded until the merge commit exists, and
the push that creates that commit triggers the step at once. The `PostToolUse` hook prompts the
review after the merge; the step nearly always runs first.

**The failing posture was wider than its ruling.**
[ADR 0089](0089-the-map-gate-is-an-offline-grader-over-a-harvest-and-the-reconciliation-obligation-is-anchored-on-a-field-the-delta-sets.md)
ruling 5 made every finding advisory, on the stated ground that pending debt would make the report
always red.
[ADR 0106](0106-the-implementation-map-is-reconciled-by-an-in-tree-tool-rather-than-gated-at-publication.md)
ruling 8 took `unmapped-ready` alone out of advisory; its build, `57724777`, removed `--advisory`
from the whole scan.
[ADR 0168](0168-a-map-obligation-belongs-to-whoever-incurred-it-and-the-producer-stamp-hashes-the-emitter.md)
then kept failing on both owned rows.
[ADR 0202](0202-a-paginated-read-carries-a-denominator-and-a-short-read-refuses.md) ruling 6 named
the rate as signal-destroying and left it to this ticket.

## Ruling 1 — the step refuses only on new debt

Every unreconciled ADR and every ready ticket in no packet that is owed when this is built becomes
**grandfathered map debt**. It prints on every push and refuses none. Any finding outside that set
refuses as it does today. Every row still prints, and no step gains `continue-on-error`.

Keeping every finding refusing was refused: 200 consecutive red runs did not drive the backlog
down, and while it stands a new failure on this step reads as the usual one. Reporting all debt and
refusing none was refused because the step could then never be red for debt, which is ADR 0089's
posture and the condition ADR 0106 ruling 8 was written against. Moving the debt check to its own
workflow was refused because that workflow would be permanently red instead, on a page opened less
often.

## Ruling 2 — the grandfathered set is a declared list that can only shrink

The set is a declared constant in `tools/map_scan.py` naming each ADR path and ticket number. A
test fails when an entry has been discharged, so the list shrinks as reconciliations land, and
adding an entry needs a visible diff. It names its members rather than counting them, unlike
[ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md)'s
scratch baseline, because ADR paths and ticket numbers are not PHI.

## Ruling 3 — an ADR is owed from the push after the one that landed it

On the push whose commit range lands an ADR, that ADR is reported as owed by this merge and refuses
nothing. Any later push refuses while it remains unreviewed and outside the grandfathered set, and
the refusing row names the ADR, so its owner remains identifiable under ADR 0168 ruling 1. The
range is the push event's `before..sha`; a manual run has none, so every ADR outside the
grandfathered set is owed.

A fixed time window was refused because no measurement grounds any value for it, and a result keyed
on the clock depends on when a push happens rather than on what it carries. Recording a review
before the merge was refused: the `gh pr merge` route has no merge commit beforehand, and on the
local-merge route a rejected push would leave the record on a commit that never reached `main`.

The grace exists only because the review cannot be recorded earlier. A ready ticket can be placed
before the merge, so it gets none and refuses on the next push as it does today. The rarer rows,
`mapped-not-ready` and `missing-limits-pointer`, refuse when they arise; this records the posture
build `57724777` adopted without a ruling naming them.

## Ruling 4 — the report states the three populations

The step's report prints the grandfathered count, the count owed by this merge, and the refusing
count on every run, so a green result reads as nothing new owed and never as nothing owed. Exit
status precedence is unchanged: a refusing finding wins over did-not-scan, and a did-not-scan run
still exits 2 under ADR 0202.

## Ruling 5 — one ticket drains the grandfathered set for real

A single ticket reconciles every grandfathered entry, recording for each ADR either the packets it
changes or one no-work sentence, and places each grandfathered ready ticket. It is finished when
the declared list is empty.

Leaving the set to drain opportunistically was refused: no owner is accountable, and that is how the
backlog grew from 48 to 62. A bulk record marking every entry grandfathered and not reviewed was
refused because the map would never learn what those ADRs changed, and the entries are real work by
the ticket's own account.

## Ruling 6 — the suite runs after a map failure

`Test suite` and the PHI-disclosure step run whatever the map step's result, as the steps after them
already do. This is widened into #1199 because the map step's redness is what skips them.

## Ruling 7 — no healthy-rate figure

A red result now names one owed item rather than a rate crossing a line, so the ticket's fourth
question needs no cut point and none is named.

## Relation to earlier records

ADR 0168's *"`map_scan` keeps failing on both rows"* is narrowed to findings outside the
grandfathered set and the landing push's ADRs; its ownership rulings stand. ADR 0089 ruling 5's
all-advisory posture is not revived. The `producer-stamp` row keeps its existing harvest-mode
posture.

[ADR 0155](0155-the-map-render-stamps-its-producer-and-the-graph-draws-only-what-carries-an-edge.md)
ruling 4 says ADR 0106 ruling 8 *left* `unmapped-ready` advisory. ADR 0106 ruling 8 took it out of
advisory. The citation is recorded here and is corrected at that record by the tracker's procedure.

## What this record does not settle

**How much work the drain finds.** Whether the grandfathered ADRs change packets or mostly record no
work is unknown until they are read, and no prediction is stated.

**A push carrying several merges.** Every ADR its range lands is treated as landed by that push.
Whether that leaves a missed review unrefused for one push longer than ruling 3 intends is not
measured.
