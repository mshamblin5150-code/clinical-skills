# A scratch link is one entry never entered and a deep read failure qualifies the count

**Measured at:** a1c440906ee7d1594dd7bcb6e66a21d7d6e54f1b

[#1685](https://github.com/mshamblin5150-code/clinical-skills/issues/1685) was filed from the
grilling session for #1491, when the pre-commit scratch census refused every commit in
every checkout with the owning scratch root reported `unreadable; not scanned`. The cause was twelve
dangling directory junctions inside another session's Ticket directory. The clinician authorized
removing them, which cleared it, and ruled every point below on 2026-10-16. **Nothing is built
here; this is the record the build reads.**

## Measured before ruling

**The failure came from a figure the gate does not grade.** `tools/scratch_census.py` grades a
**gating root** on its top-level entries, read by `count_root` through `scratch.iterdir()`. That
read succeeded. The exception came from `count_files`, the recursive walk behind the `files
beneath` figure, which ADR 0059 ruling 4 makes printed and never graded. `count_files` passes an
`onerror` that re-raises, so any error anywhere below the top level reaches the census loop's
`except FileNotFoundError` or `except OSError` branch and marks the whole root `unreadable`.

**`followlinks=False` does not stop a junction.** Measured on this machine under Python 3.14.4 with
two junctions made by `mklink /J`, one live and one dangling: `os.scandir` reports both with
`is_dir()` true, `is_symlink()` false and `is_junction()` true, and `os.walk(...,
followlinks=False)` descends into both. The dangling one raises `FileNotFoundError` (WinError 3),
which is #1685's error. The live one is walked, so its target's files are counted again, and a
junction pointing at an ancestor would make the walk repeat itself. So `PEER_DIRECTORY_LINK_LIMIT`,
which says the census does not traverse a directory link, is true of a symbolic link and false of a
junction.

**One walk feeds three readers.** `count_files` supplies the gating roots' `files beneath` total,
each peer root's file count (which decides whether it is reported `empty` or `carrying material`),
and, through `optional_tree_file_count`, the `--worktrees` pre-removal read of each worktree's
`scratch/` and `output/`. A pre-removal read that raises reports that worktree `not read; HELD
BACK`.

## Ruling 1 — a link or junction under a scratch root is one entry and is never entered

The walk treats every symbolic link and every junction below any scratch root as one entry and
never descends into it, live or dangling, in gating and peer roots alike. The top-level grade is
unchanged, because a link at the top level is already one top-level entry. The link itself counts
toward the root's file total as one entry, so a root holding only a link is not reported empty. What
is lost is the content behind a live link; `PEER_DIRECTORY_LINK_LIMIT` is rewritten to say that,
naming junctions and every root, and its false claim that a link counts as no file is retired.

The two refused options were refusing with the offending path named, which would print a scratch
filename that may itself carry PHI, and walking live links while reporting dangling ones, which
keeps the double count and the loop.

## Ruling 2 — a read failure below the top level qualifies the count and does not refuse the root

A subdirectory below the top level that cannot be read leaves the root graded. The census counts the
failure and keeps walking. Only a top level that cannot be listed, or a root that is not a
directory, still marks the root `unreadable` and takes the existing exit-2 limb. The gate's verdict
rests only on what it grades, and the walk's figure is reported for context. Keeping the refusal
would reproduce #1685 from any other deep error; dropping the failure silently would present a
short count as a complete one.

## Ruling 3 — the file-count line states both shortfalls, without names

Beside each file total the report states how many subdirectories could not be read and how many
links were not entered, as integers and on every run, zero included. For example: `N files beneath;
M subdirectories could not be read; K links not entered`. Neither number changes the exit status
and neither names an entry, so the module's rule that it never prints an entry's name stands. A peer
root's per-root line carries the same two counts.

## Consequences the rulings fix without a further choice

**The pre-removal hold-back keeps its fail-safe.** The `--worktrees` pre-removal report exists so a worktree whose scratch material is unrecoverable is not removed. Under ruling 1 a link
counts as one entry, so a worktree whose `scratch/` holds only a link is held back as before. Under
ruling 2 the pre-removal read no longer raises on a deep failure, so a worktree with any unreadable
subdirectory under `scratch/` or `output/` is held back on that count, keeping today's
`HELD BACK` outcome for that case.

**A peer root is not reported empty on a partial read.** A peer root with an unreadable
subdirectory or a link counts as carrying material rather than empty, for ruling 2's reason.

**The unreadable-root remedy text becomes accurate again.** After ruling 2, `restore access to the
owning scratch root` is printed only when the top level itself cannot be listed, which is what it
says. It is not changed. ADR 0338's edits to the finding-remedy block are already on `main`; this
build is based on them.

## What this does not reach

A file the walk could list but whose name or type it misreads is outside this record. A link's target
outside the scratch root is never read, so material reachable only through a live link appears in
no count; ruling 1 accepts that and the rewritten limit declares it. A directory deleted during the
walk is counted as unreadable, not distinguished from a permission failure. Nothing here changes the
top-level ratchet, the baselines, or what the census accounts for.

## Build checklist

- `tools/scratch_census.py`: replace `count_files` with a walk that does not descend into a symbolic
  link or junction, counts each as one entry, and returns files, unreadable subdirectories and links
  not entered without raising below the top level. Feed all three readers from it. Rewrite
  `PEER_DIRECTORY_LINK_LIMIT`. Add the two counts to the gating-root `files beneath` line and the
  peer per-root lines. Hold a pre-removal read back when its unreadable-subdirectory count is nonzero,
  and class a peer root with any unreadable subdirectory or link as carrying material.
- `docs/agents/scratch.md` and `CLAUDE.md` **Scratch census**: name the new counts without copying
  `DECLARED_LIMITS`.
- Tests: a dangling junction under a gating root's Ticket directory leaves the census clean with the
  owning root graded and `1 links not entered`; a live junction pointing at an ancestor terminates
  and counts once; a live junction's target files are not counted; an unreadable subdirectory below
  the top level leaves the root graded and reports `1 subdirectories could not be read`; an
  unlistable top level still exits 2 with the existing remedy; a worktree whose `scratch/` holds only
  a dangling junction, and one holding an unreadable subdirectory, are each `HELD BACK`; no new line
  prints an entry name. Junction tests skip off Windows; symbolic-link tests run everywhere.
