# A worktree session that started without its skill mirror is told its skills came from the owning checkout

**Measured at:** 4dbf0795b56f31864d63103bb4a9584bcf6ee9ae

[#1806](https://github.com/mshamblin5150-code/clinical-skills/issues/1806) was filed from the
after-action review of a `batch-shift` run (NUR5144 clinic shift) on 2026-10-14. A worktree
session's `/batch-shift` text came from the owning checkout's `.claude/skills/` mirror, which was 548
commits behind the session's tree, while its session-start mirror repair reported every skill
linked. The ticket offered two remedies and asked that the resolving scope be measured first.
Grilled 2026-10-17 against `main` at the commit above, where the freshness gate read `FRESH`. The
clinician ruled every point below in that session, one question at a time. **Nothing is built here;
this is the record the build reads.**

## Measured before ruling

**Claude Code chooses the skill source once, at startup, by whether the worktree's skill folder
exists.** The Claude Code skills documentation (https://code.claude.com/docs/en/skills, read
2026-10-17) says that in a linked git worktree, parent directories are searched only up to the
worktree root, and that on v2.1.277 or later, "when the worktree checkout has no `.claude/skills`
directory at its root, Claude Code loads the main checkout's project skills instead." The installed
version was 2.1.284.

**The grilling session itself took that path.** Its worktree's `.claude/settings.json` was written at
18:51:29.99 and its `.claude/skills` directory at 18:51:33.82, by the session-start repair, which
reported all 12 entries `missing` and relinked them. `/grill-with-docs` exists only in the owning
checkout's mirror, and the session served it from there. That observation alone does not separate
the documented fallback from an ancestor-directory walk, since the worktree sits under the owning
checkout; the documentation's worktree-root bound is what separates them.

**The skill list does not reload during a session.** A probe skill written into the worktree's
`.claude/skills` and then into the owning checkout's was reported `Unknown skill` by the Skill tool,
once for the worktree probe and twice for the owning-checkout probe. Both probes were removed. So a repair made after startup cannot change
which text a session receives, and #1806's first proposed remedy reads a mirror the session never
loaded.

**The creation-time repair did not create the folder.** `tools/hooks/post-checkout` repairs the
mirror when Git reports a new worktree, but this worktree's folder was made by the session-start
hook four seconds after its settings file. Why the creation path skipped it was not measured.

**Git hooks take the same route by configuration.** `core.hooksPath` in the owning checkout's
`.git/config` is the absolute path `C:\codeing\clinical_skills\tools\hooks`, so every worktree commit
runs the owning checkout's hook files; the hooks resolve their tools through
`git rev-parse --show-toplevel`, so only the hook files themselves come from the owning checkout. The
documented setup command writes the relative `tools/hooks`. In a throwaway repository with that
relative setting, a commit in a linked worktree ran the worktree's edited hook and a commit in the
main checkout ran the main checkout's. The three hook files matched by content on the measured day;
12 commits touched `tools/hooks/` in the preceding seven weeks.

**Every repo skill was byte-identical between the two trees on the measured day.** The owning
checkout was on `main`, 37 commits behind `origin/main`.

## Ruling 1 — detect and redirect now; prevention is its own ticket

The session-start check detects a session whose skills came from the owning checkout and redirects
the agent to the session checkout's own skill files. Preventing the condition, by making the
worktree's skill folder exist before a session starts, is filed separately and waits for a
measurement of how the desktop app creates worktrees and why the creation-time repair did not run.
#1806's second remedy, having each skill state the commit its text came from, was declined: stale text
would carry a stale stamp, so the stamp vouches for itself.

## Ruling 2 — one line always, the warning only on a difference

The check fires when the session checkout is a linked worktree whose `.claude/skills` directory was
absent before the session-start repair ran. It then always contributes one plain line naming the
owning checkout as the source and counting how many files differ between what the owning checkout's
mirror serves and the session checkout's `skills/`, including zero. The comparison covers every file
under each repo skill's folder, because a skill opens sibling files from its base directory, and a
file the owning mirror lacks counts as differing. A skill that exists only in the owning checkout's
mirror has no counterpart and stays outside the count. When at least one file differs, the line is
followed by a warning telling the agent to read each skill from the session checkout's own
`skills/<name>/` folder rather than the invocation's base directory. Always printing the full warning
was declined because it fires on most worktree sessions when nothing differs; staying silent unless
files differ was declined because it makes "checked, identical" read the same as "never checked".

## Ruling 3 — the hooks path is its own ticket

The absolute `core.hooksPath` is filed as a separate ticket proposing the documented relative path, a
change to the clinician's Git settings that he approves there. Folding a hook-file comparison into
this check was declined because it detects a gap that one setting closes, and the gap is in the
pre-commit path that enforces standing rule 1.

## Ruling 4 — no owning-checkout commit distance on the Base distance line

The existing Base distance line keeps describing the session checkout alone. A commit count for the
owning checkout was declined because it reads the same whether or not the served skill text differs:
600 commits behind with identical skills is harmless and 3 behind with a changed `SKILL.md` is not.
A later path by which owning-checkout material reaches a session gets its own measured line.

## Build checklist

- `tools/skills_mirror.py --session-start`: record whether the session checkout's `.claude/skills`
  directory existed before repair; when it did not and the session checkout is a linked worktree,
  compare each repo skill's files as served by the owning checkout's mirror with the session
  checkout's `skills/` and contribute ruling 2's line, plus the warning when the count is nonzero.
- The retained pre-repair report under `.claude/skills-mirror-reports/` carries the same line.
- `skills_mirror.NOT_REACHED` gains this record's limits below.
- The `Skills mirror` section of `CLAUDE.md` describes the line by pointing at the module.
- Tests through the public `--session-start` command: an absent folder with identical owning files
  (line, count zero, no warning); an absent folder with one differing sibling file (line and
  warning); a present folder (no line); a skill only in the owning mirror (outside the count); and a
  session started in the owning checkout itself (no line).

## What this record does not reach

- **The cause.** The wrong text still loads; the check depends on the agent following the redirect.
  Prevention is the separate ticket.
- **Changes after startup.** The comparison is a snapshot at session start; an owning-checkout change
  later in the session is not seen.
- **An existing but empty skill folder.** Claude Code then loads the worktree's folder and the
  session has no project skills at all; that is not the fallback this check detects.
- **The `/aar` invocation in #1806's recorded session**, which resolved to the worktree's mirror
  while `/batch-shift` resolved to the owning checkout's. It was not reproduced, and no reload was
  observed that would explain it.
- **Claude Code's own behavior.** The trigger rests on the documented fallback as of v2.1.277; a
  later release that changes it would make the line's premise false without failing anything here.
