# The base line reads the files Git lists under skills and a file that is not clean UTF-8 is read with replacement and counted

**Measured at:** 0bd3d566198a63206267fffbaa01ae4155dfe008

[#1914](https://github.com/mshamblin5150-code/clinical-skills/issues/1914) was filed from the
tracker sweep closing [#1888](https://github.com/mshamblin5150-code/clinical-skills/issues/1888)'s
grilling. The session-start **Base distance** line read
`base: main -- NOT ESTABLISHED: run-relevant path-set read failed` in a desktop worktree session.
`skills_mirror.run_relevant_paths` opens every file on disk under `skills/` as UTF-8 to find the
`tools/` scripts the instructions name, and one compiled cache file that Git ignores could not be
decoded, so the whole line was withheld. Grilled 2026-10-19 against `main` at the commit above,
where the freshness gate read `FRESH`. The clinician ruled every point below in that session, one
question at a time. **Nothing is built here; this is the record the build reads.**

## Supersedes

- [ADR 0432](0432-every-recursive-walk-in-tools-adopts-the-shared-walk-or-is-a-named-exception-and-each-walk-s-verdict-fails-closed-on-a-folder-it-could-not-read.md)
  ruling 10, the words "`skills_mirror.run_relevant_paths` walks `skills/` through the shared
  walk." The function no longer walks a folder (ruling 1 here), so the shared walk and that
  ruling's link and unopenable-folder postures have nothing to govern. Ruling 10 itself provided
  for this outcome and named this record as the one that marks it.

## Measured before ruling

Read-only, at the commit above:

- In the main checkout, `skills/` holds one `.pyc` file on disk, beneath
  `skills/vitalsource-chrome/scripts/__pycache__/`. `.gitignore` ignores both `__pycache__/` and
  `*.pyc`, and running the skill's tracked helper script recreates it.
- `git ls-files --cached --others --exclude-standard -- skills` lists the same files in the main
  checkout and in this session's worktree, and none of them is a `.pyc`. Every listed file decodes
  as UTF-8, so the count of ruling 2 is zero on both trees today.
- `run_relevant_paths` has one production caller, `read_base_distance`, which calls it only after
  the reflog read and the raw `rev-list` distance have already succeeded on the same checkout.
- `RunRelevantPathTests` calls the function on a temporary folder that is not a Git checkout.

## Ruling 1 — the population is Git's view of `skills/`

The instruction population is `AGENTS.md` plus the files
`git ls-files --cached --others --exclude-standard -- skills` lists: tracked files and new files
that `.gitignore` does not exclude, which is a **Source walk** in `CONTEXT.md`'s terms. No folder
walk remains in the function. The ignored cache file
is outside the population for the reason Git already records, that it is not source, and a skill
file being drafted but not yet staged still contributes the tools it names.

**Tracked files only was declined**: an unstaged draft skill file would drop out until staged, so
the line would omit tools it names. **Every file on disk, skipping and counting the undecodable
ones, was declined**: the ignored cache file returns whenever the helper runs, so the line would
carry a nonzero unread figure about routine build output, which is the warning that stops being
read.

## Ruling 2 — a file that is not clean UTF-8 is read with replacement and counted on the line

A listed file is read as bytes and decoded as UTF-8 with replacement, so every ASCII
`tools/<name>.py` citation it still holds is found. Each file that was not valid UTF-8 is counted,
and the rendered line names that count beside the distances whenever it is nonzero, as files read
with replacement. The distances still print. A clean tree prints no count.

**Replacing silently was declined**: a file saved as UTF-16 spreads every character over two bytes,
so replacement recovers no citation and nothing would say so. **Skipping and counting the file was
declined**: a file with one stray byte would contribute none of the citations it visibly holds.

## Ruling 3 — a failed listing leaves the line not established, with no disk fallback

If the Git listing fails, the line reads `NOT ESTABLISHED: run-relevant path-set read failed`
with the `origin/main` movement time, which is the wording it already uses for a failed read. The
tests that call the function on a plain folder become Git checkouts.

**Falling back to a disk walk was declined**: the listing can fail only after Git has already
answered twice on the same checkout, so the failure is real, and a fallback would restore the
decoding failure this record removes on exactly the path that runs when something is already wrong.

## Ruling 4 — this builds on its own, and #1896 drops the function

#1914 needs nothing from the shared walk module of
[ADR 0416](0416-a-recursive-walk-never-enters-a-link-and-one-shared-walk-serves-the-census-the-sweep-and-the-after-action-review.md),
so it is not blocked behind [#1841](https://github.com/mshamblin5150-code/clinical-skills/issues/1841)
or [#1896](https://github.com/mshamblin5150-code/clinical-skills/issues/1896). #1896's build no
longer converts `run_relevant_paths`, and its ruling-1 population test does not expect the
function to use the shared walk, because the function holds no recursive walk.

**Waiting for #1896 was declined**: the line stays lost on every desktop worktree session behind two
blocked builds, and the walk conversion would be discarded days later. **Folding this into #1896
was declined**: it enlarges a review ADR 0432 ruling 12 sized deliberately and inherits its block.

## Coordination the rulings fix without a further choice

- The **Skills mirror** section of `CLAUDE.md` says the tool subset "is derived from the tree on
  every reading". It is reworded to say the subset is derived on every reading from the files Git
  lists under `skills/`, tracked or new but not ignored.
- A listed file that cannot be opened at all, such as a tracked file deleted from disk, cannot be
  allowed to withhold the line, because #1914 requires that no single unreadable file does. It is
  counted on the line beside ruling 2's count rather than raising. This follows from #1914's stated
  requirement and ruling 2; it was not put as a separate question.
- ADR 0416 ruling 4's words "`run_relevant_paths` needs no limit", already superseded by ADR 0432
  ruling 10, stay superseded. The function has no folder walk now, but it still gains limit rows,
  listed under *What this does not reach* below.
- [ADR 0426](0426-a-desktop-worktree-session-is-served-the-main-checkout-s-skills-so-the-main-checkout-is-fast-forwarded-at-a-worktree-session-s-start.md)
  keeps the line computed in the main checkout. Nothing here changes which checkout it reads.
- `BaseDistanceGitTests.test_the_read_uses_only_the_declared_local_git_commands` gains the listing
  command. It still opens no socket and runs no `fetch`.

## What this does not reach

- An instruction file that `.gitignore` wrongly excludes is not read. Such a file can never reach
  `main`, so the commit distance it would add is not one the line could report.
- A file saved as UTF-16, or in another encoding whose ASCII letters are not single bytes, yields no
  citation. Ruling 2 makes it visible as a count, not readable.
- A citation written in a form `TOOL_PATH` does not recognize is outside the population, as before.

## Build checklist

- `tools/skills_mirror.py`: replace the `rglob` in `run_relevant_paths` with the Git listing of
  ruling 1, read through `_git_read` so a failure raises `BaseReadFailed` with the existing label
  (ruling 3).
- Return the read-with-replacement count of ruling 2 and the unopenable count from the
  coordination section with the path set, carry both into `BaseDistance`, and print them in
  `render_base_distance` only when nonzero.
- `skills_mirror.NOT_REACHED`: add the two rows of *What this does not reach* that are new here.
- `CLAUDE.md` **Skills mirror**: the rewording above, naming the new counts without copying the
  limits object.
- Tests: plant an undecodable file inside the listed set and drive it through `read_base_distance`;
  the line prints its distances and a count of one. Plant an ignored `.pyc` and assert it is not
  read and not counted. Plant an unstaged, unignored skill file citing a tool and assert the tool
  is in the path set. Delete a tracked file and assert the line still prints with its count. Make
  the listing fail and assert the not-established wording. Convert `RunRelevantPathTests` to a Git
  checkout.
