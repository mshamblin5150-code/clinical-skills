"""Shared tri-state Git ancestry predicate."""

from __future__ import annotations

import subprocess
from collections.abc import Callable


Runner = Callable[..., subprocess.CompletedProcess[str]]


def is_ancestor(ancestor: str, descendant: str, *, run_git: Runner) -> bool | None:
    completed = run_git("merge-base", "--is-ancestor", ancestor, descendant)
    if completed.returncode == 0:
        return True
    if completed.returncode == 1:
        return False
    return None
