# The served base is reported without a fetch and never called current

Out of [#979](https://github.com/mshamblin5150-code/clinical-skills/issues/979), grilled on
2026-09-12 to an empty frontier. **Six rulings, by the clinician, on that date.** Nothing is built
here; this is the record the build reads.

**Measured at:** 1b279edddbe761419691d874a9b3c75255aea624

[ADR 0152](0152-the-skills-mirror-is-repaired-at-session-start-and-its-orphans-are-drained.md)
ruling 7 put branch currency out of the mirror's scope and stated the boundary it left behind: **a
repaired mirror is a consistent run, never a current one.** It refused folding a currency check into
the `SessionStart` hook **on cost rather than on relevance** — the check opens a socket, and that
hook runs at the head of every session including offline ones. #979 filed the boundary.

This record supersedes the scope of that refusal and leaves its reasoning intact: the cost objection
is sound about a fetch, and the report does not need one.

## What was measured before ruling, on 2026-09-12

Freshness gate `FRESH` at `1b279ed` before any figure below was taken, and every figure re-derived
against that base. **The branch was brought forward three times while this record was written** and
`main` moved twice in the hour before the merge, which is this record's own subject arriving inside
it.

**The ticket's subject is the wrong tree.** Its body and title are about the main checkout being 130
commits behind. Across the machine's registered checkouts — **52 enumerated, 52 read, 0 unread**:

| | raw | run-relevant |
| --- | ---: | ---: |
| at 0 behind | 1 | 2 |
| median behind | **125** | **19** |
| maximum | 1056 | 201 |
| 100 or more behind | 32 | — |
| more than 0 behind | 51 | **50** |
| carrying unmerged work | 2 | 1 |

The main checkout, on `codex/ticket-1014-aar-extract` at `416cfea`, reads **22 behind and 4
run-relevant** — among the freshest trees measured. **Staleness is the ordinary condition of a
checkout here, and the ticket as filed points at the good case.**

**The ticket's dissolving question is answered against dissolution.** It asked whether the distance
was an accident of one machine on one day. Its own thread records six instances across four branches
in four days; this reading is the seventh, on a fifth branch. Under the negation the population above
clusters at zero; its median is 125.

**Commit distance overstates instruction staleness by an order of magnitude.** Over a 600-commit
window ending at the measured base:

| counted paths | commits | share |
| --- | ---: | ---: |
| `skills/` | 43 | 7% |
| `skills/`, `reference/`, `AGENTS.md` | 51 | 8% |
| those plus the 37 `tools/*.py` modules a skill file **invokes** | 84 | 14% |
| those plus all of `tools/` | 187 | 31% |

**The middle row is a use and not a mention, and the distinction was measured rather than assumed.**
Reading every `tools/*.py` path *named* under `skills/` or in `AGENTS.md` finds **43** modules and
**88** commits; six of those are `tools/test_*.py`, discussed as the gate that pins a rule and
invoked by no run. Narrowing further to a literal `python tools/X.py` command finds 31 and 83 — and
**drops `block_scan.py`, `harvest_review.py` and `uptodate_sheet.py`, which runs do invoke**, so the
strictest rule is the one that errs unsafe. The three differ by five commits in six hundred; what
separates them is direction, not size.

**The cost objection was aimed at a fetch nobody needs.** Reading the cached `origin/main` costs
**46 ms and opens no socket**. All registered checkouts share one ref store, so any session's fetch
refreshes the copy for every one of them: over the seven days before the measurement `origin/main`
moved **164 times, median gap 20 minutes, 90th percentile 103 minutes, longest 20.6 hours.**

**The shipped harness reloads skills after `SessionStart` hooks** (`hook_session_start_reload_skills`,
"Skills restored") and carries both a `hook_blocking_error` and a `hook_non_blocking_error` path for
that event. A blocking error there would block the **session**, which is the wrong unit for a rule
about a run.

**`CONTEXT.md` already forbids the ticket's vocabulary.** **Owning checkout**'s `_Avoid_` row lists
*"main checkout (ambiguous with the `main` branch)"*, and #979 says "the main checkout" throughout.

## Ruling 1 — the report is a non-fetching read at session start, and ADR 0152 ruling 7 is superseded in scope only

The `SessionStart` hook that repairs the mirror also states the base the repaired mirror points into.
It reads the cached `origin/main` and **opens no socket**, so ADR 0152 ruling 7's cost objection is
met rather than overridden — that ruling refused a fetch, and no fetch is proposed.

**#979's decision 1, declare it and rely on somebody choosing to ask, is refused on the thread's own
evidence.** `tracker_freshness.py` has answered the adjacent question the whole time and is named by
no file under `skills/`. Six recorded instances in four days is what relying on the reader looks like.

**#979's decision 2 is structurally unavailable and is closed rather than declined.** For a skill's
step to state its base, something must compute it, which puts a command on the consumer path —
against [AGENTS.md](../../AGENTS.md)'s standing promise and against ADR 0152 ruling 1, and in any case
a `SKILL.md` body enters context before its own step 1 can run.

## Ruling 2 — the line carries a population and a finding, and the finding's path set is derived from the tree

The line reports the raw distance **and** a run-relevant count. **Run-relevant** means `skills/`,
`reference/`, `AGENTS.md`, and the `tools/*.py` modules the skill files and `AGENTS.md` literally
invoke — which excludes `tools/test_*.py`, named in those files as the gate that pins a rule and run
by nothing a consumer does — read out of the tree at run time, never a hand-kept list, so a skill that begins citing a
new command is covered without anyone maintaining a constant.

**Neither number stands alone.** Raw distance alone is an order of magnitude of noise. The
run-relevant count alone is unverifiable: a reader cannot tell *3 of 18* from *3 of 3*, and
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling is that a report
states what it was measured over.

**Blanket `tools/` was refused and bare `skills/` was refused, and the reason is one recorded
defect.** [#820](https://github.com/mshamblin5150-code/clinical-skills/issues/820)'s founding
instance was a grader constant — `discussion_reply_scan.WORD_FLOOR_COUNT` reading 150 while the
served instructions read 100 — so a set excluding `tools/` misses the class that produced the ticket
this one descends from. Blanket `tools/` doubles the noise for tracker and map tooling no clinical
run touches.

## Ruling 3 — the word *current* is unavailable to this instrument, and every line carries when the cached copy last moved

The report reads a copy. It can prove a checkout is behind; it can never prove one is not.
`tracker_freshness.py` has three verdicts and this mechanism structurally has only two of them:
**it has no `FRESH`.**

A zero therefore prints as **no newer commit known**, never as *current* and never as a bare `0`.
Every line states when `origin/main` last moved, read from that ref's reflog — shared across every
checkout, and recording when the ref **moved** rather than when anyone **looked**, so a fetch that
found nothing writes nothing and the age reads older than reality. **That errs toward distrusting the
number, which is the safe direction.**

**Fetching only when the cached copy looks old was refused.** It restores the socket ADR 0152 ruling 7
declined and it needs a cutoff nobody can ground, which is
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s objection and
`SPACE_ADVANCE_FRACTION`'s recorded failure of naming a value at an edge.

## Ruling 4 — nothing refuses, and the report fires at session start only

**#979's decision 4 is closed.** A refusal on the run-relevant count would turn away **50 of the 52
checkouts measured**, including the one the clinician works in, on a floor rather than on a
measurement. `docx_write.py` priced this trade already and its ruling holds here: the renderer warns
and never refuses because it sits on the consumer's critical path, and *a blocked submission is a
worse outcome than a separator on the page.* A clinical run is that path.

**A second report at skill invocation was also refused, and the reason is a property of the tree
rather than a cost.** `HEAD` does not move during a session, so **the tree a run is served at hour
three is exactly the tree the session-start line described.** Only the distance decays: a line
reading 3 may truly be 8 by evening. The floor weakens; it never becomes false.

Against that, a second seam costs another hook and another matcher roster —
`command_tool_roster.py` exists because a hook roster silently going incomplete is a live hole — and
**whether the `Skill` tool fires `PreToolUse` at all is unmeasured.** The shipped harness carries
`tool_name` as a free string, so it is plausible; nothing in this repository has ever matched a
non-shell tool. That is filed rather than assumed.

## Ruling 5 — the reported axis is both directions, and a checkout carrying unmerged work may not print the clean line

The line reports **behind and ahead**, each with its run-relevant sub-count, and **no newer commit
known becomes unavailable whenever anything is ahead.**

**The shape this guards was observed live and is already spent, which is the ticket's own pattern.**
A worktree measured earlier on 2026-09-12 read **0 behind and 1 ahead**; under ruling 3 alone it would
print the cleanest line the mechanism can produce while carrying a commit on no reviewed branch —
this record's defect rebuilt inside its own fix. At the measured base that instance has moved and two
checkouts carry unmerged run-relevant work instead.

**The two directions are not symmetric and the asymmetry is the argument.** Against a stale cached
copy, **behind is a floor and ahead is a ceiling**: an old copy makes a checkout look less behind than
it is and more ahead than it is. Only one of the two can quietly reassure a reader, and it is the one
that would have been reported alone.

The count costs nothing: `git rev-list --left-right --count` returns both numbers in the call already
being made.

## Ruling 6 — the subject is any checkout, and the ticket is rewritten around the condition

#979's subject widens from the main checkout to **whatever checkout a session starts in.** Its title
and body are rewritten around the condition; its measured instances are kept beneath as dated
evidence; a dated footer records the change and its `**Filed from:**` line is preserved word for word.

**A subject that names one checkout and one commit has an instance that expires, and this one has
expired seven times.** The body's `b26ea2a` and 130 are spent, as are the comment series
130 → 140 → 154 → 156 → 167, `ticket-772` at `b4c3fd8`, `ticket-835` at `96666be` across four further
readings, and `ticket-1014-aar-extract` at `416cfea` by the time this record merges. **A subject that
names the condition cannot expire**, and the seven readings read better as a series under a standing
claim than as corrections to a spent one.

**This is a vocabulary correction as much as a scope one.** The glossary already avoids *main
checkout* as ambiguous with the branch `main`, and the ticket's title carries it.

## Considered options

**Declare and rely on the reader** — #979 decision 1. Refused: the thread is the measurement of what
that produces.

**A statement in a skill's step 1** — decision 2. Closed as structurally unavailable, above.

**A fetching check at session start** — decision 3 as ADR 0152 refused it. Not revived; the
non-fetching read is what ruling 1 adopts, and it is a different mechanism rather than a softened
version of that one.

**A refusal on the run path** — decision 4. Refused on the measured population and on
`docx_write.py`'s precedent.

**A second report at skill invocation.** Refused on the tree property in ruling 4 and on an unmeasured
seam, and filed.

## Consequences for the build

The mechanism is one addition to an existing hook and one path-set derivation. It adds no file to the
consumer path, no dependency, and no socket. `AGENTS.md` is untouched and the seven clinical skills
gain no step.

The line is a floor in one direction and a ceiling in the other, and says so in its own words rather
than in a docstring a reader does not open. Its numbers are computed from one `git rev-list` pair and
one reflog read.

## What this does not reach

**It cannot establish that a checkout is current.** That needs a fetch, and `tracker_freshness.py` is
the instrument that does one.

**It reports and grades nothing.** No status changes, no run is refused, and a reader who ignores the
line is not stopped.

**Its run-relevant set is a floor on what a run reads.** A skill that reaches a file through a path no
skill file names — an import chain inside a cited tool, a reference sheet opened by a tool rather than
by a step — is outside the derived set and is counted only in the raw distance.

**It says nothing about the tracker.** A checkout current on commits may cite tracker records that
have moved, which is **Base freshness**'s declared boundary and is unchanged by this record.
