"""Shared identity and population policy for graded coursework runs.

Issue #417 joins a submission to the run directory that produced it. That join
is policy several graders must agree on, so its key parser and path populations
live here rather than as similar local predicates.
"""

from __future__ import annotations

import re
from pathlib import Path

from repo_root import output_root, scratch_root


TRAILING_DATE = re.compile(r"-\d{4}-\d{2}-\d{2}$")


def key_of(stem: str) -> str:
    """Return the assignment key carried by a submission stem.

    A run is undated and each sitting is dated, so the only syntax removed is a
    trailing ISO date. Companion phase tokens do not exist under ``output/``.
    """
    return TRAILING_DATE.sub("", stem)


def runs_root(start: Path | None = None) -> Path:
    """The canonical container for assignment-owned provenance records."""
    return scratch_root(start) / "runs"


def is_run_directory(path: Path | str, start: Path | None = None) -> bool:
    """Whether ``path`` is one direct assignment directory under ``runs_root``."""
    candidate = Path(path).expanduser().resolve()
    return candidate.parent == runs_root(start).resolve()


def is_submission(path: Path | str, start: Path | None = None) -> bool:
    """Whether ``path`` resolves under the main checkout's ``output/`` tree."""
    candidate = Path(path).expanduser().resolve()
    return candidate.is_relative_to(output_root(start).resolve())
