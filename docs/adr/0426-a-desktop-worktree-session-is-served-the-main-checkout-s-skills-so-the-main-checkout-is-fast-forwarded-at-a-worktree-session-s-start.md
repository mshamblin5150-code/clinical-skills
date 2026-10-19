# A desktop worktree session is served the main checkout's skills, so the main checkout is fast-forwarded at a worktree session's start

**Measured at:** aa5d6d302a3ad9639a4f19c12280908de6877446

[#1879](https://github.com/mshamblin5150-code/clinical-skills/issues/1879) was filed from the
grilling of #1806 under
[ADR 0407](0407-a-worktree-session-that-started-without-its-skill-mirror-is-told-its-skills-came-from-the-owning-checkout.md)
ruling 1. It asked which mechanism makes a worktree's skill folder exist, correctly linked, before
Claude Code reads it, and it asked for a measurement of how the desktop app creates a worktree first.
Grilled 2026-10-19 against `main` at the commit above, where the freshness gate read `FRESH`. The
clinician ruled every point below in that session, one question at a time. **Nothing is built here;
this is the record the build reads.**

## Measured before ruling

**A desktop-app worktree session reads its project configuration from the main checkout's root.**
The Claude Code worktree documentation (https://code.claude.com/docs/en/worktrees, section "What
worktrees share with the main checkout", read 2026-10-19) says that for a worktree session started
from the desktop app, settings, hooks, skills, agents, commands and `.mcp.json` servers come from the
main checkout's root rather than from the worktree. Hook commands run in that root and
`${CLAUDE_PROJECT_DIR}` points at it; only `CLAUDE.md` files and `.claude/rules/` load from the
worktree. The fallback ADR 0407 relied on, where the main checkout's skills load only when the
worktree has no `.claude/skills` directory, is the separate rule for worktrees made with
`--worktree` or `git worktree add` and started outside the desktop app. The installed version was
2.1.299.

**The grilling session took that path, and the hook's location separates the two explanations.** In
the session's worktree, the root directory was created at 11:36:04.06 local time, `.claude/settings.json`
at 11:36:04.79, and `.claude/skills` at 11:36:05.61, holding copied real folders for the
maintainer's non-repository skills. The session-start hook wrote its report at 11:36:08.5, about three
seconds after that folder existed. The report is in the main checkout's
`.claude/skills-mirror-reports/`, names `C:\codeing\clinical_skills`, and lists every entry `linked`.
`/grill-with-docs` was served from `C:\codeing\clinical_skills\.claude\skills\grill-with-docs`. Had
the worktree's own configuration applied, as ADR 0407's explanation requires once the folder exists,
`${CLAUDE_PROJECT_DIR}` would have been the worktree, the hook would have run the worktree's
`tools/skills_mirror.py`, and its report would have named the worktree. The sweeps closing #1860's
and #1861's grillings recorded the same report location twice on the same day.

**`post-checkout` runs, after the session has started, and its timing no longer matters.** The
worktree's twelve junctions were created between 11:36:10.35 and 11:36:10.81, after the tracked files
were written at about 11:36:06, and an empty `vitalsource-chrome` folder the app had copied was
drained to `.claude/skills-orphaned/` in the same second. Because a desktop session never reads the
worktree's skill folder, none of #1879's three candidates (an earlier `post-checkout`, a
worktree-creation hook, a tracked placeholder folder) changes the text a desktop session receives.

**What a desktop worktree session is served is the main checkout's working-tree `skills/`.** The
main checkout's mirror holds junctions into `C:\codeing\clinical_skills\skills\`. That text differs
from the session's own in two cases: the main checkout lags `origin/main`, which ADR 0407 measured at
37 commits and #1806 at 548, or the session's branch carries skill text that `main` does not. At this
grilling the main checkout was on `main`, level with `origin/main`.

**A fetch of `origin/main` from the worktree took 0.41 to 0.45 seconds**, three runs with nothing new
to receive. Claude Code caps its own fetch for a fresh worktree base at five seconds.

**ADR 0407's detection was never built, and as written it would not fire in a desktop session.** Its
trigger is a worktree whose skill folder was absent before the session-start repair; the
session-start hook runs the main checkout's script, whose `repo_root()` is the main checkout, so the
hook inspects the main checkout and never the worktree.

## Ruling 1 — keep what is served current, at the source the app reads

At the start of a worktree session, the session-start hook fast-forwards the main checkout to
`origin/main`. It does so only when the main checkout is on `main`, carries no uncommitted edits to
tracked files, and can be fast-forwarded; otherwise it declines. The fetch is capped at five seconds,
matching Claude Code's own fresh-base fetch; a timeout is a decline. The cap was set as a default in
the session, not put to the clinician. Making the worktree's own skill folder exist earlier was
declined because a desktop session never reads it. Closing #1879 and leaving everything to detection
was declined because the recorded defect is lag, and detection leaves the stale text loaded. Moving
skill-running sessions off the desktop app's worktree option was declined as a change to how the
clinician works that would need its own measurement.

## Ruling 2 — one line always, the warning only on a difference

Every worktree session start contributes one plain line. When the fast-forward ran, the line names
the commit the main checkout moved to and how many files under `skills/` changed. When it declined,
the line names the reason and counts the files under `skills/` that differ between the main
checkout's `HEAD` and `origin/main`, including zero. When the fetch failed or timed out, the line
says the count was not measured, so a failed check never reads as "nothing differs". A nonzero count
adds a warning telling the agent to read each skill from the session worktree's own
`skills/<name>/` folder rather than the invocation's base directory. Saying something only on a
difference was declined because "declined, nothing differs" would read the same as "never checked",
the reasoning of ADR 0407 ruling 2. Stopping the session was declined: a SessionStart hook cannot
block, and the condition is not the clinician's to clear. A bare commit distance stays declined on
ADR 0407 ruling 4's ground.

## Ruling 3 — #1806's detection is re-premised on the worktree's own path

The hook reads the session's worktree path from its input's `cwd` field, compares that worktree's
`skills/` with what the main checkout serves, file by file under each repo skill's folder, and adds
that count to ruling 2's line. ADR 0407 ruling 2's comparison rules stand: every file under a repo
skill's folder counts, a file the served side lacks counts as differing, and a skill only the main
checkout's mirror holds stays outside the count. This covers a resumed worktree on an older branch.
A session that edits a skill and then invokes it is a declared limit rather than a check, because a
session-start snapshot cannot see a later edit. Closing #1806 was declined because a resumed older
branch would then run current `main` skill text silently. Catching the edit-then-invoke case with an
invocation hook was declined as an unmeasured new hook surface.

## Ruling 4 — worktree sessions only

The fast-forward and the comparison run only when the hook's `cwd` is a linked worktree. A session
started in the main checkout is served its own tree, so it has no mismatch to repair, and moving that
checkout at every start would change files under any other agent working there. Running at every
session start was declined for that reason.

## Build checklist

- `tools/skills_mirror.py --session-start`: read `cwd` from the hook payload; when it resolves to a
  linked worktree of the checkout the script lives in, run ruling 1's guarded fetch and fast-forward
  of the main checkout, then ruling 3's comparison, and contribute ruling 2's line and warning. The
  existing mirror repair and Base distance line keep their current subjects.
- The retained report under the main checkout's `.claude/skills-mirror-reports/` carries the same
  line and names the worktree it was taken for.
- `skills_mirror.NOT_REACHED` gains this record's limits below.
- The `Skills mirror` section of `CLAUDE.md` points at the module for the line.
- Measure before the line's wording is fixed: whether an edit to a `SKILL.md` in the main checkout
  after startup reaches a later invocation in the same session. The skills documentation describes
  live change detection for `SKILL.md` text, while ADR 0407 measured that an added probe skill stayed
  unknown. If an edit does not reach the session, the line says the fast-forward serves the next
  session.
- Tests through the public `--session-start` command: a worktree start with a clean, behind main
  checkout (fast-forward, count of changed skill files); a dirty main checkout (decline, reason,
  count); a main checkout on another branch (decline); a diverged `main` (decline); a failed fetch
  (not measured); a worktree whose `skills/` differs from the served text (warning); and a session
  started in the main checkout itself (no fetch, no fast-forward, no line).
- #1806 and #1879 are built by one change; whichever of this and the ADR 0416 build lands second
  keeps both sets of `skills_mirror` edits.

## What this record does not reach

- **A skill edited and then invoked in the same session.** The invocation is served the main
  checkout's text.
- **The current session, if live change detection does not cover it.** Until the build's measurement,
  a fast-forward at start may serve only later sessions.
- **Another agent working in the main checkout on a clean `main`.** A fast-forward moves files under
  it; the guards refuse only uncommitted tracked edits.
- **Claude Code's own behavior.** The rulings rest on the desktop-app paragraph of the documentation
  as read on 2026-10-19; a release that changes it would make the premise false without failing
  anything here.
- **The `/aar` invocation in #1806's recorded session** that resolved to the worktree's mirror. The
  documented desktop rule does not explain it either, and it was not reproduced.
- **Claude Code hooks.** They also come from the main checkout's `.claude/settings.json` in a
  desktop session. That is the same shape as #1880's Git hooks path, but this record does not rule
  on it.

## Supersedes

- [ADR 0407](0407-a-worktree-session-that-started-without-its-skill-mirror-is-told-its-skills-came-from-the-owning-checkout.md)
  ruling 1, the words "Preventing the condition, by making the worktree's skill folder exist before a
  session starts". Prevention now keeps the main checkout current, because a desktop session never
  reads the worktree's folder. Detection and redirection, and declining the commit stamp, stand.
- [ADR 0407](0407-a-worktree-session-that-started-without-its-skill-mirror-is-told-its-skills-came-from-the-owning-checkout.md)
  ruling 2, the words "The check fires when the session checkout is a linked worktree whose
  `.claude/skills` directory was absent before the session-start repair ran." The check now fires for
  every worktree session, located through the hook's `cwd`. The one line, the warning on a nonzero
  count and the comparison rules stand.
