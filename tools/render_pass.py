"""Shared reader and retention mechanics for numbered render passes."""

from __future__ import annotations

import re
import shutil
import tempfile
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TypeVar


PASS_DIRECTORY = re.compile(r"pass-([1-9][0-9]*)", re.ASCII)
_Result = TypeVar("_Result")


class RenderPassError(OSError):
    """The shared pass mechanism could not safely retain or discard a pass."""


def read_passes(render_root: Path) -> tuple[tuple[int, Path], ...]:
    """Return parsed pass directories in numeric order."""

    if not render_root.is_dir():
        return ()
    found = []
    for child in render_root.iterdir():
        match = PASS_DIRECTORY.fullmatch(child.name)
        if child.is_dir() and match:
            found.append((int(match.group(1)), child))
    return tuple(sorted(found, key=lambda item: item[0]))


def next_pass_number(render_root: Path) -> int:
    """Return one greater than the highest retained pass number."""

    passes = read_passes(render_root)
    return passes[-1][0] + 1 if passes else 1


def missing_pass_numbers(passes: Iterable[tuple[int, Path]]) -> int:
    """Count absent positive numbers through the highest retained pass."""

    numbers = tuple(number for number, _path in passes)
    return max(numbers, default=0) - len(numbers)


def images_cover_exported_pages(image_count: int, exported_pages: int) -> bool:
    """Return whether every exported page has at least one retained image."""

    return image_count >= exported_pages


def _discard_staging(staging: Path, render_root: Path) -> None:
    resolved = staging.resolve()
    if (
        resolved.parent != render_root.resolve()
        or not resolved.name.startswith(".building-")
    ):
        raise RenderPassError(
            f"refused to remove unexpected temporary path {resolved}"
        )
    if staging.exists():
        shutil.rmtree(staging)


def retain_staged_pass(
    render_root: Path,
    build: Callable[[Path], _Result],
) -> tuple[Path, _Result]:
    """Build privately, then retain at the next number derived after the build."""

    render_root.mkdir(exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".building-", dir=render_root))
    try:
        result = build(staging)
        destination = render_root / f"pass-{next_pass_number(render_root)}"
        staging.rename(destination)
        return destination, result
    except Exception:
        _discard_staging(staging, render_root)
        raise
