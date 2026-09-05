r"""Check that .claude/skills/ mirrors skills/ by link, and repair it when it does not.

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

**A difference in line endings alone is named rather than normalized away.** `filecmp`
is byte-exact, so a mirror copy made before anything rewrote a skill file with `\n`
reads `copy-stale` on carriage returns and nothing else -- and `copy-stale` is the word
this repo cites as evidence that an agent has *already* followed a retired rule. #93's
one citable instance is in a worktree that is gone, so it can no longer be told apart
from three carriage returns, which is the cost. Normalizing the comparison was declined:
a copy that differs on disk is still a copy, and a byte check is the thing that cannot
be argued with. **So the comparison is untouched and every differing file carries its
reason** -- `content` or `line endings only` -- with both counts printed on every run,
whether or not each fired.

**`_normalized` is where the rule that decides the word lives**, and it is the only
authoritative statement of it -- every other one in the tree, this paragraph included,
describes that line. A file the copy does not hold at all counts as content, because it
is not carriage returns, which is the whole question the split answers; and the partition
is two-way so the two counts sum to the total, which is the one thing a reader checks the
summary line against.

**Output is paths and status words only.** It reads `skills/` and `.claude/skills/`,
neither of which may contain PHI under standing rule 1, and it never prints file
contents. The reason beside a differing file is one of two fixed strings held here
rather than anything read out of the file. Its output is safe to paste into a ticket,
like `corpus_census.py` and unlike `harvest_review.py`.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, NamedTuple

from console_codec import use_utf8

MIRROR = Path(".claude") / "skills"
CANONICAL = Path("skills")

# A directory under skills/ is mirrored when it carries a SKILL.md or when this
# explicit set names shared instruction that has no owning skill. Skill names stay
# discovered from their files; the exception is named because widening to every
# directory would silently make a future non-instruction directory loadable.
SKILL_FILE = "SKILL.md"
SHARED_INSTRUCTION_DIRECTORIES = {"_shared"}

LINKED = "linked"
MISSING = "missing"
IDENTICAL = "copy-identical"
STALE = "copy-stale"
FOREIGN = "linked-elsewhere"
NOT_A_DIR = "not-a-directory"

# Everything except LINKED is a finding. MISSING is the mildest -- the skill simply
# does not load -- and STALE is the one that answers questions wrongly.
OK_STATUSES = {LINKED}

# Why a file under a STALE copy differs. Two values and no third, so the counts in
# the report sum to the number of differing files. #198.
CONTENT = "content"
LINE_ENDINGS = "line endings only"


class Difference(NamedTuple):
    """One file the copy gets wrong, and which of the two ways it gets it wrong.

    A plain pair would compare and sort identically; naming the fields is what stops
    `differs` reading as a list of paths at the one signature a reader checks.
    """

    rel: str
    reason: str


def _normalized(data: bytes) -> bytes:
    r"""`\r\n` -> `\n`, and nothing else. **This function is the rule.**

    Deliberately not *strip every* `\r`, so a lone carriage return sitting inside
    content stays a content difference -- under-claiming that a difference is
    harmless is the safe direction. Every other statement of this in the tree is a
    description of this line and none of them is authoritative.
    """
    return data.replace(b"\r\n", b"\n")


def difference_reason(canonical_file: Path, mirror_file: Path) -> str | None:
    """CONTENT, LINE_ENDINGS, or None when the two files are byte-identical.

    The byte comparison comes first and decides *whether* they differ. Normalization
    only ever names a difference the byte check has already found, which is what
    keeps `copy-stale` byte-exact.
    """
    if filecmp.cmp(canonical_file, mirror_file, shallow=False):
        return None
    if _normalized(canonical_file.read_bytes()) == _normalized(mirror_file.read_bytes()):
        return LINE_ENDINGS
    return CONTENT


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
        if p.is_dir()
        and (
            (p / SKILL_FILE).is_file()
            or p.name in SHARED_INSTRUCTION_DIRECTORIES
        )
    )


def _differing_files(
    canonical: Path, mirror: Path,
) -> tuple[list[Difference], list[str]]:
    """(one Difference per file that differs or is missing, files only in the mirror).

    The second list is the one that blocks repair. A file present only in the copy
    is either someone's stray edit or work that never reached `skills/`, and either
    way deleting the copy would be the only record of it going away.

    A file the mirror does not hold is CONTENT rather than a third reason -- see the
    module docstring for why the partition is two-way.
    """
    differs: list[Difference] = []
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
        differs.append(Difference(rel, CONTENT))
    for rel in sorted(mirror_rel - canonical_rel):
        extra.append(rel)
    for rel in sorted(canonical_rel & mirror_rel):
        reason = difference_reason(canonical / rel, mirror / rel)
        if reason is not None:
            differs.append(Difference(rel, reason))

    return sorted(differs), extra


class Entry:
    def __init__(
        self,
        name: str,
        status: str,
        differs: Iterable[Difference] = (),
        extra: Iterable[str] = (),
        target: Path | None = None,
    ):
        self.name = name
        self.status = status
        self.differs = list(differs)
        self.extra = list(extra)
        self.target = target

    @property
    def ok(self) -> bool:
        return self.status in OK_STATUSES

    def _differs_for(self, reason: str) -> list[str]:
        return [d.rel for d in self.differs if d.reason == reason]

    @property
    def content_differs(self) -> list[str]:
        """The files a reader has to act on. This is the drift `copy-stale` means."""
        return self._differs_for(CONTENT)

    @property
    def endings_differs(self) -> list[str]:
        """The files that differ and say nothing about drift. Still a copy, still
        a finding, and not evidence that a rule was answered wrongly."""
        return self._differs_for(LINE_ENDINGS)


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
            # Both counts on every run, whether or not each fired. A reader who has
            # learned to read one of them reads its absence as the other being zero,
            # which is checks_ledger.py's argument for naming its rows unconditionally.
            detail = (
                f" ({len(entry.differs)} file(s) differ: "
                f"{len(entry.content_differs)} {CONTENT}, "
                f"{len(entry.endings_differs)} {LINE_ENDINGS})"
            )
        elif entry.status == FOREIGN:
            detail = f" -> {entry.target}"
        elif entry.status == IDENTICAL:
            detail = " (matches today, will drift)"
        lines.append(f"  {mark} {entry.name:<{width}}  {entry.status}{detail}")
        if verbose and entry.differs:
            for difference in entry.differs:
                lines.append(
                    f"         differs ({difference.reason}): {difference.rel}"
                )
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
        # That sentence is what `copy-stale` is cited for, and it is the claim a
        # CRLF-only difference cannot support. The rows above already say which kind
        # each file is; this qualifies the sentence a skimming reader actually reads,
        # which is #198's stated harm rather than the row. Withdrawn by a single
        # content difference anywhere, because the sentence is about the whole report.
        found = [d for e in entries for d in e.differs]
        if found and not any(d.reason == CONTENT for d in found):
            lines.append(
                "No copy differs in content: every difference found is line endings "
                "only, which is not evidence a rule has been answered wrongly."
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
