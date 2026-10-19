"""Walk ordinary files without entering links; see ``DECLARED_LIMITS``.

An unlistable root raises OSError. Failures below it qualify the returned read.
The caller owns the meaning of those counts and never receives failed names.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path


DECLARED_LIMITS = (
    "material reachable only through a link or junction is never read",
    "a listed entry whose name or type is misread is outside this walk",
    "a directory deleted during the walk counts as unreadable, without distinguishing permission failures",
    "the walk is a momentary read; an entry replaced after its link check can change what is reached",
)

# ADR 0432: comparisons intentionally enter mirrors made from junctions.
# Session start uses the same comparison, so it needs no separate exception.
RECURSIVE_WALK_EXCEPTIONS = {
    ("skills_mirror.py", "_differing_files"): (
        "Copy-stale and session-start comparisons must enter the canonical "
        "skills and mirror junctions; skills_mirror.NOT_REACHED declares the boundary."
    ),
}


@dataclass(frozen=True)
class WalkResult:
    files: tuple[Path, ...] = ()
    unreadable_directories: int = 0
    links_not_entered: int = 0


def is_link(path: Path) -> bool:
    """Recognize symbolic links and Windows reparse points, including on 3.10."""
    if os.path.islink(path):
        return True
    isjunction = getattr(os.path, "isjunction", None)
    if isjunction and isjunction(path):
        return True
    if os.name == "nt":
        try:
            attributes = os.lstat(path).st_file_attributes
        except (AttributeError, OSError):
            return False
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    return False


def walk_files(root: Path) -> WalkResult:
    """Return reached files and count boundaries; explicitly supplied roots are opened."""
    files: list[Path] = []
    unreadable = 0
    links = 0
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    path = Path(entry.path)
                    if is_link(path):
                        links += 1
                    elif entry.is_dir(follow_symlinks=False):
                        pending.append(path)
                    else:
                        files.append(path)
        except OSError:
            if directory == root:
                raise
            unreadable += 1
    return WalkResult(tuple(files), unreadable, links)


def corpus_files(root: Path, pattern: str = "*") -> tuple[Path, ...]:
    """Read a corpus completely or refuse, reporting excluded links every time."""
    result = walk_files(root)
    print(f"links not entered {result.links_not_entered}")
    if result.unreadable_directories:
        raise OSError(
            f"corpus subfolders unreadable: {result.unreadable_directories}; "
            "restore read access and retry"
        )
    return tuple(path for path in result.files if path.match(pattern))
