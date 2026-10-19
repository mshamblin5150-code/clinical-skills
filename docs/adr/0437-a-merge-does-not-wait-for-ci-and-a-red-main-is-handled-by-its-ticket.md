# A merge does not wait for CI, and a red main is handled by its ticket

**Measured at:** 0ee4d850268bd7276b40e6d9cac0c76ea630c8ea

[#1926](https://github.com/mshamblin5150-code/clinical-skills/issues/1926) was filed from the
grilling of #1916, as [ADR 0436](0436-a-closing-hazard-in-pull-request-text-a-merge-message-or-a-commit-message-is-refused-before-github-can-act-on-it.md)
ruling 5 directed. It asked whether a pull request must wait for CI before it merges, because PR
#1915 merged ten seconds after it was opened and its CI job went red afterward. Grilled 2026-10-19
against `main` at the commit above, where the freshness gate read `FRESH`. The clinician ruled each
point below in that session, one question at a time. **Nothing is built; this record is the reason
nothing is.**

## Measured before ruling

**The population** is the 200 most recently merged pull requests as `gh pr list --state merged
--limit 200` returned them, merged 2026-10-09T18:14:48Z through 2026-10-19T17:37:40Z, every one by
the maintainer's account. For each, the matcher read `statusCheckRollup` and kept the two
`.github/workflows/checks.yml` jobs, `suite + PHI shape layer` and `complete suite at the consumer
floor`, that started before the merge. The tracker workflow's jobs run on the merge event itself,
so a rollup-wide reading counts every merge as early and discriminates nothing; the first pass of
this measurement did exactly that, and it is why the population is the two CI jobs.

**Merges usually do not wait.** 104 of the 200 merged before both CI jobs had completed. Of the 96
that waited, 48 merged over a red result. The median merge came 13.5 minutes after the pull request
was opened; the CI jobs in those rollups that ran to a pass or a failure took a median of 11.8 minutes
and a 90th percentile of 18.4.

**#1915's suite passed.** Its `suite + PHI shape layer` job failed on one step, `Closing keyword
scan, pull request`; the `Test suite` step succeeded, read from the job's step conclusions. The push
run on its merge commit, `7020e852`, succeeded. The tree that landed was green. The one harm the
merge did was the closing hazard that took #1879 down, which is ADR 0436's subject and is refused
before the merge once that record is built.

**No merge in the window broke `main`'s tests through its own change.** 78 pull requests carried a
red CI job that started before their merge. Read from each failing job's step conclusions, 59 failed
`Test suite`, 14 failed only the closing-keyword step, 4 failed only `Publication measurement base,
committed ADRs`, and 1 failed both of those last two. All 59 fall between #1817 and #1902, the pull
requests that ran while `main` itself was red.

**`main` was red once, and the cause was the runner.** 120 push runs of `checks.yml` on `main` read
as 37 green, 62 red, 21 green, the red stretch running from `1b66dd90` (#1817's merge,
2026-10-16T13:08Z) until `5270598f` (#1900's merge, 2026-10-19T13:33Z). #1817 added one ADR. Its
CI ran on the runner's newly installed Python 3.14.8, where one test's twelve subtests failed;
[#1818](https://github.com/mshamblin5150-code/clinical-skills/issues/1818) was filed at 13:10Z, a
minute after the merge, and #1900 repaired the test. A wait-for-green gate would have refused every merge
for those three days over a break no pull request caused.

**The red stretch hid no second failure.** All 62 pre-merge `suite + PHI shape layer` failures from
#1817 through #1902 were read in full, 62 read and 0 unread. Every `FAIL:` and `ERROR:` name in them
is #1818's test. The reader is live: it found that test in each of the 62 logs, and any other test
name would have been printed beside it.

## Ruling 1. A merge does not wait for CI

No mechanism refuses a merge on CI's state. The pre-publication hook gains no `gh pr merge` refusal
keyed to check results, and no status check becomes required. [ADR 0002](0002-ci-runs-the-suite-at-the-merge.md)'s
advisory posture stands unchanged.

Waiting for a green result was declined because the window holds no merge it would have stopped
from landing broken code, and the only merges it would have refused were the three days in which
`main` was red for every pull request alike, where a refusal protected nothing and an override would
have become the ordinary path. Waiting for a result, red or green, with an explicit acknowledgment
to merge over red was declined because it charges a quarter hour on every merge to catch a failure
the window never produced. A required status check was declined on ADR 0002's own grounds: it ends
the local merge-and-push route and blocks every merge during an environmental red.

**What this costs is named rather than discovered.** A pull request whose own change breaks the
suite will land, and the push run on `main` will report it afterward. That happened twice in ADR
0002's history, `anchor_scan` and `block_scan`, both merge interactions, and zero times in this
window.

## Ruling 2. A red main is handled by its ticket

When `main` turns red, the ticket filed for the break is the handling, as #1818 was. No CI step
compares a pull request's failures with `main`'s, and the session-start context does not report
`main`'s CI state.

A comparing CI step was declined because it adds a tool that reads `main`'s run logs through the
API from inside CI to catch a masked failure the measurement found zero of. A session-start line was
declined because that hook reads only the cached `origin/main` and would gain a network read on
every session. **The trigger to revisit is a second distinct failing test name during a red
stretch**, which the reader above would print.

## Ruling 3. Two carried claims are corrected where they stand

ADR 0436 says #1915's suite job failed. The job by that name failed on its closing-keyword step and
its test suite passed, so that record carries a dated correction in place, per
[ADR 0191](0191-a-carried-claim-is-corrected-where-it-stands-and-436-never-ruled-it.md). Its
rulings are unchanged; ruling 5's deferral is answered here.

[ADR 0431](0431-the-maintainer-ci-job-pins-the-exact-python-release-and-a-canary-job-runs-the-newest-one.md)
ruling 5 describes a merge practice of waiting until every check succeeds as the one
[ADR 0382](0382-a-whole-ticket-binding-on-a-grilling-ticket-is-a-premature-close-refused-at-the-publish-hook-and-red-in-ci.md)
relies on. The measurement above shows that practice is not what the merges did, so ADR 0431
carries a dated correction too; its ruling that a red canary holds no merge is unchanged and agrees
with ruling 1 here. Found by this grilling's closing tracker sweep.

**What this means for ADR 0382.** Its pre-publication hook limb refuses a premature close before any
merge and is unaffected. Its CI limb turns the run red, which is read only by a merge that waits
for the run; for the 104 merges above that did not wait, that limb reported after the fact.

## What this does not reach

The measurement covers ten days of one maintainer's merges. It does not establish that a merge-time
break cannot happen, only that this window produced none, and it reads failing test names only for
the red stretch. A merge performed from the browser or by local push never passes the hook, so no
hook-side rule could have reached those merges either way.
