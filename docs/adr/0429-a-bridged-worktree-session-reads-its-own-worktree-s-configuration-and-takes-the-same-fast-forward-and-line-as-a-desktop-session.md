# A bridged worktree session reads its own worktree's configuration and takes the same fast-forward and line as a desktop session

**Measured at:** 592067b0598e89b7fae3429b31459b713ce157e8

The tracker sweep that closed
[#1879](https://github.com/mshamblin5150-code/clinical-skills/issues/1879)'s grilling found that
[ADR 0426](0426-a-desktop-worktree-session-is-served-the-main-checkout-s-skills-so-the-main-checkout-is-fast-forwarded-at-a-worktree-session-s-start.md)
described one kind of worktree session, while #1879's own measurements came from another. The
clinician ruled the point below on 2026-10-19 in the same session, after ADR 0426 merged.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Two kinds of worktree session run here, and they read configuration from different places.**
Sessions the desktop app starts carry `"entrypoint":"claude-desktop"` in their transcripts and run in
`grill-with-docs-*` and `triage-issues-*` worktrees. ADR 0426 measured that they take hooks and
skills from the main checkout's root. Bridged sessions carry `"entrypoint":"sdk-cli"` and run in
`bridge-cse_*` worktrees. All 28 `bridge-cse_*` worktrees that hold a session-start report hold it
in their own `.claude/skills-mirror-reports/`, and each newest report's first line names that
worktree. So a bridged session ran the worktree's own `tools/skills_mirror.py`, which means the
worktree's own `.claude/settings.json` applied. If bridged sessions followed the desktop rule, their
reports would sit in the main checkout and name it, as every `grill-with-docs-*` report does. Both
kinds ran on 2026-10-18, so the split is the session kind, not a Claude Code release.

**In a bridged session ADR 0407's premise appears to hold.** The newest bridged report, in
`bridge-cse_01VNUWeEUg4t7EKPPMW8em1f`, lists every skill `missing`, and in the four bridged
worktrees the sweep timed, `.claude/skills` was created at the report's second, about 3.5 to 5
seconds after `settings.json`. A bridged session therefore starts with no skill folder and is served
the main checkout's skills under the fallback the Claude Code skills documentation describes. Unlike
a desktop session, it would read the worktree's folder if the folder existed at start. How bridged
worktrees are created, and whether `post-checkout` runs before such a session starts, was not
measured.

**#1806's 2026-10-16 observation came from a bridged session.** Its finding, that a worktree's own
settings ran the heredoc hook, comes from a transcript carrying `"entrypoint":"sdk-cli"` on 430 rows.
It agrees with this record and does not conflict with ADR 0426.

**The script's location and the hook's `cwd` tell the two kinds apart.** In a desktop session the
hook runs the main checkout's script while the payload's `cwd` is the worktree. In a bridged session
both are the worktree. This follows from the two measurements above. No hook has yet been driven to
show it.

## Ruling 1 — one mechanism for both kinds

ADR 0426's rulings 1 to 4 apply to bridged worktree sessions as well as desktop ones. At the start
of either kind, the main checkout is fast-forwarded under ADR 0426 ruling 1's guards, and the session
gets ADR 0426 ruling 2's line, carrying ruling 3's comparison of the worktree's `skills/` with what
the main checkout serves. The build tells the kinds apart by comparing the checkout the running
script lives in with the checkout the hook's `cwd` resolves to. In a bridged session the script
finds the main checkout through Git's common directory. A session in the main checkout itself still
gets nothing, as ADR 0426 ruling 4 says.

## Ruling 2 — a bridged session's own skill folder is not made to exist earlier

Making a bridged worktree's skill folder exist before the session reads it was declined for now.
That fix would serve the branch's own skill text, but bridged worktrees are created by the bridge
rather than this repository, so the fix may not be controllable. It would also need its own
measurement of that creation path first. A tracked placeholder folder was declined again on #1879's
original ground: a session that starts before the junctions exist would load no project skills at
all. If a bridged session's branch-specific skill text turns out to matter in practice, that becomes
its own ticket.

## Build checklist

These amend ADR 0426's checklist. Where the two differ, follow this one.

- `tools/skills_mirror.py --session-start`: resolve the hook payload's `cwd` to its checkout. When
  that checkout is a linked worktree, whether it is the one the script lives in (bridged) or not
  (desktop), run ADR 0426's fetch, fast-forward, comparison and line. Locate the main checkout
  through `git rev-parse --git-common-dir` from `cwd`, never from the script's own location alone.
- In a bridged session the existing mirror repair keeps acting on the worktree it already acts on.
  The line's comparison reads the served side from the main checkout's mirror. In a bridged session
  that is what the session was served, because its own folder was missing at start.
- Tests through the public `--session-start` command add a bridged start, where the script's root
  and `cwd` are the same linked worktree, beside ADR 0426's desktop cases.
- The `Skills mirror` section of `CLAUDE.md` says "follows the junctions instead of recreating
  them". The build replaces that sentence with what each session kind does. In the desktop worktree
  measured for ADR 0426, the app copied only real folders and left an empty folder where the main
  checkout's mirror has a `vitalsource-chrome` junction.
- `skills_mirror.NOT_REACHED` gains this record's limits below.

## What this record does not reach

- **A bridged session's branch-specific skill text.** It is served the main checkout's text and
  warned about the difference, per ruling 2.
- **The bridged creation path.** Who creates a `bridge-cse_*` worktree, and when `post-checkout` runs
  there, was not measured.
- **The discriminator itself.** Script location against `cwd` is derived from two measurements, not
  from a driven hook. The build's tests are its first demonstration.
- **A third kind of session.** A worktree session started from a terminal with `claude --worktree`
  or `git worktree add` was not measured here. The documentation places it under the same fallback
  rule as a bridged session.

## Supersedes

- [ADR 0426](0426-a-desktop-worktree-session-is-served-the-main-checkout-s-skills-so-the-main-checkout-is-fast-forwarded-at-a-worktree-session-s-start.md)
  ruling 1, the words "Making the worktree's own skill folder exist earlier was declined because a
  desktop session never reads it." That ground holds for desktop sessions only. A bridged session
  would read its own folder; the earlier fix is declined there on ruling 2's ground instead. The
  fast-forward, its guards and the fetch cap stand.
