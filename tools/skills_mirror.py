"""Check that .claude/skills/ mirrors skills/ by link, and repair it when it does not.

`.claude/skills/` is how Claude Code loads this repo's skills natively. README.md
tells you to make each entry a **junction** to the canonical `skills/<name>/`, so
the mirror cannot hold a different answer than the skill does. That directory is
gitignored, so nothing about it is checked by anything git does.

**A junction that becomes a copy is the failure this exists for.** It reads exactly
like a working install -- same names, same files, same frontmatter -- and it answers
questions with whatever the skill said on the day the copy was made. An agent that
opens `.claude/skills/clinical-note/SKILL.md` instead of `skills/clinical-note/SKILL.md`
follows retired rules and has no way to notice. That is not hypothetical: it is how
this file came to exist. `git worktree` materialized `.claude/` by copying it, the
copy followed the junctions instead of recreating them, and the resulting worktree
carried the exact paragraph issue #23 had been filed to remove.

**Resolution, not readlink, is the test.** `os.path.islink` is False for a Windows
junction, and `os.path.isjunction` only exists on 3.12+. `os.path.realpath` resolves
junctions, symlinks and plain directories alike on every platform, so a mirror entry
is correct when it resolves to the same real path as the canonical skill and wrong
otherwise. Nothing here needs to know which link flavor made it.

**A copy that currently matches is still reported.** It is right by luck and by luck
only until the next edit to `skills/`; `identical` and `stale` differ in how much time
is left, not in whether the wiring is broken.

**Output is paths and status words only.** It reads `skills/` and `.claude/skills/`,
neither of which may contain PHI under standing rule 1, and it never prints file
contents. Its output is safe to paste into a ticket, like `corpus_census.py` and
unlike `harvest_review.py`.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path

from console_codec import use_utf8

MIRROR = Path(".claude") / "skills"
CANONICAL = Path("skills")

# A directory under skills/ is a skill when it carries a SKILL.md. Nothing here
# hardcodes the skill names: README's own `for s in clinical-note batch-shift
# icd10-cpt` list was written when there were three and never gained
# setup-clinical-skills, which is the same drift one level up.
SKILL_FILE = "SKILL.md"

LINKED = "linked"
MISSING = "missing"
IDENTICAL = "copy-identical"
STALE = "copy-stale"
FOREIGN = "linked-elsewhere"
NOT_A_DIR = "not-a-directory"

# Everything except LINKED is a finding. MISSING is the mildest -- the skill simply
# does not load -- and STALE is the one that answers questions wrongly.
OK_STATUSES = {LINKED}


def repo_root(start: Path | None = None) -> Path:
    """The checkout this script belongs to -- worktree root, not the main checkout.

    `git rev-parse --show-toplevel` is asked from the script's own directory rather
    than the process cwd, so running it from anywhere reports on the right tree.
    A worktree is a different toplevel than the checkout it was branched from, and
    conflating the two is precisely the bug this file is about.
    """
    here = (start or Path(__file__).resolve().parent)
    try:
        out = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
            encoding="utf-8", errors="replace",
        )
        return Path(out.stdout.strip()).resolve()
    except (OSError, subprocess.CalledProcessError):
        # No git, or not a checkout. tools/ sits one level under the root.
        return here.parent.resolve()


def skill_names(root: Path) -> list[str]:
    canonical = root / CANONICAL
    if not canonical.is_dir():
        return []
    return sorted(
        p.name for p in canonical.iterdir()
        if p.is_dir() and (p / SKILL_FILE).is_file()
    )


def _differing_files(canonical: Path, mirror: Path) -> tuple[list[str], list[str]]:
    """(files that differ or are missing from the mirror, files only in the mirror).

    The second list is the one that blocks repair. A file present only in the copy
    is either someone's stray edit or work that never reached `skills/`, and either
    way deleting the copy would be the only record of it going away.
    """
    differs: list[str] = []
    extra: list[str] = []

    canonical_rel = {
        p.relative_to(canonical).as_posix()
        for p in canonical.rglob("*") if p.is_file()
    }
    mirror_rel = {
        p.relative_to(mirror).as_posix()
        for p in mirror.rglob("*") if p.is_file()
    }

    for rel in sorted(canonical_rel - mirror_rel):
        differs.append(rel)
    for rel in sorted(mirror_rel - canonical_rel):
        extra.append(rel)
    for rel in sorted(canonical_rel & mirror_rel):
        if not filecmp.cmp(canonical / rel, mirror / rel, shallow=False):
            differs.append(rel)

    return sorted(differs), extra


class Entry:
    def __init__(self, name: str, status: str, differs=(), extra=(), target=None):
        self.name = name
        self.status = status
        self.differs = list(differs)
        self.extra = list(extra)
        self.target = target

    @property
    def ok(self) -> bool:
        return self.status in OK_STATUSES


def inspect(root: Path) -> list[Entry]:
    entries = []
    for name in skill_names(root):
        canonical = (root / CANONICAL / name).resolve()
        mirror = root / MIRROR / name

        if not mirror.exists():
            entries.append(Entry(name, MISSING))
            continue
        if not mirror.is_dir():
            entries.append(Entry(name, NOT_A_DIR))
            continue

        resolved = mirror.resolve()
        if resolved == canonical:
            entries.append(Entry(name, LINKED))
            continue

        # It resolves somewhere else. Either it is a real copy sitting inside
        # .claude/skills/, or it is a link aimed at another checkout -- a worktree
        # pointing back at the main tree reads current today and diverges the moment
        # the branch does. Both answer with the wrong file; only the repair differs.
        differs, extra = _differing_files(canonical, mirror)
        if _is_link(mirror):
            entries.append(Entry(name, FOREIGN, differs, extra, target=resolved))
        else:
            status = IDENTICAL if not differs and not extra else STALE
            entries.append(Entry(name, status, differs, extra))

    return entries


def _is_link(path: Path) -> bool:
    """True for a symlink or a Windows junction, on any supported Python.

    Only used to tell a plain copy from a link aimed elsewhere. The correctness
    test above never needs it.
    """
    if os.path.islink(path):
        return True
    isjunction = getattr(os.path, "isjunction", None)
    return bool(isjunction and isjunction(path))


def link(mirror_entry: Path, canonical: Path) -> None:
    """Point mirror_entry at canonical, using whatever this platform links with.

    Windows gets a junction rather than a symlink deliberately: `mklink /J` is what
    README documents and it needs no Developer Mode and no elevation, which a
    directory symlink does.
    """
    mirror_entry.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(mirror_entry), str(canonical)],
            check=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
    else:
        os.symlink(canonical, mirror_entry, target_is_directory=True)


def repair(root: Path, entries: list[Entry]) -> tuple[int, list[str]]:
    """Relink every broken entry. Returns (repaired, refusals)."""
    repaired = 0
    refusals = []

    for entry in entries:
        if entry.ok:
            continue
        canonical = (root / CANONICAL / entry.name).resolve()
        mirror_entry = root / MIRROR / entry.name

        if entry.extra:
            refusals.append(
                f"{entry.name}: mirror holds {len(entry.extra)} file(s) that "
                f"skills/{entry.name}/ does not -- "
                + ", ".join(entry.extra)
                + ". Relinking would delete them. Move or discard them first."
            )
            continue

        if mirror_entry.exists() or _is_link(mirror_entry):
            if _is_link(mirror_entry):
                # Removing the link, never what it points at.
                try:
                    os.rmdir(mirror_entry)
                except OSError:
                    os.unlink(mirror_entry)
            elif mirror_entry.is_dir():
                shutil.rmtree(mirror_entry)
            else:
                mirror_entry.unlink()

        link(mirror_entry, canonical)
        repaired += 1

    return repaired, refusals


def render(entries: list[Entry], root: Path, verbose: bool) -> list[str]:
    lines = [f"skills mirror: {root}"]
    if not entries:
        lines.append("  no skills found under skills/ -- nothing to mirror.")
        return lines

    width = max(len(e.name) for e in entries)
    for entry in entries:
        mark = "ok  " if entry.ok else "WARN"
        detail = ""
        if entry.status == STALE:
            detail = f" ({len(entry.differs)} file(s) differ)"
        elif entry.status == FOREIGN:
            detail = f" -> {entry.target}"
        elif entry.status == IDENTICAL:
            detail = " (matches today, will drift)"
        lines.append(f"  {mark} {entry.name:<{width}}  {entry.status}{detail}")
        if verbose and entry.differs:
            for rel in entry.differs:
                lines.append(f"         differs: {rel}")
        if entry.extra:
            for rel in entry.extra:
                lines.append(f"         only in mirror: {rel}")

    broken = [e for e in entries if not e.ok]
    if broken:
        lines.append("")
        lines.append(
            f"{len(broken)} of {len(entries)} skill(s) are not linked. An agent "
            "reading the mirror may follow a retired rule."
        )
        lines.append("Repair with: python tools/skills_mirror.py --repair")
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that .claude/skills/ links to skills/, and repair it.",
    )
    parser.add_argument(
        "--repair", action="store_true",
        help="replace copies and wrong links with junctions to skills/",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="name the files that differ (paths only, never contents)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="print nothing when every skill is linked; still exits non-zero when not",
    )
    parser.add_argument(
        "--root", type=Path, default=None,
        help="checkout to inspect (default: the one this script lives in)",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve() if args.root else repo_root()
    entries = inspect(root)

    if args.repair:
        repaired, refusals = repair(root, entries)
        entries = inspect(root)
        for line in render(entries, root, args.verbose):
            print(line)
        if repaired:
            print(f"\nrelinked {repaired} skill(s).")
        for refusal in refusals:
            print(f"REFUSED  {refusal}")
        return 1 if refusals or any(not e.ok for e in entries) else 0

    broken = [e for e in entries if not e.ok]
    if broken or not args.quiet:
        for line in render(entries, root, args.verbose):
            print(line)
    return 1 if broken else 0


if __name__ == "__main__":
    use_utf8()
    sys.exit(main())
