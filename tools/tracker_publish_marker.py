"""Write and locate the date-only tracker hook record for one checkout."""

from __future__ import annotations

from datetime import date as CalendarDate
from hashlib import sha256
import json
import os
from pathlib import Path

from repo_root import scratch_root


SCHEMA_VERSION = 2
MARKER_DIRECTORY = "tracker-publish-hook"


def _module_file(module_file: Path | None = None) -> Path:
    return (Path(__file__) if module_file is None else module_file).resolve()


def checkout_identity(module_file: Path | None = None) -> str:
    """Return a filename-safe identity derived from the module's checkout."""
    checkout = _module_file(module_file).parent.parent
    normalized = os.path.normcase(str(checkout))
    return sha256(normalized.encode("utf-8")).hexdigest()


def marker_path(
    module_file: Path | None = None,
    runs_root: Path | None = None,
) -> Path:
    """Locate this checkout's record below the owning ``scratch/runs``."""
    source = _module_file(module_file)
    runs = (
        scratch_root(source.parent) / "runs"
        if runs_root is None
        else Path(runs_root)
    )
    return runs / MARKER_DIRECTORY / f"{checkout_identity(source)}.json"


def write_marker(
    module_file: Path | None = None,
    runs_root: Path | None = None,
    today: CalendarDate | None = None,
) -> Path:
    """Write today's counts-free record and return its path."""
    target = marker_path(module_file=module_file, runs_root=runs_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    ran_on = CalendarDate.today() if today is None else today
    target.write_text(
        json.dumps(
            {"version": SCHEMA_VERSION, "ran_on": ran_on.isoformat()},
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def record_run() -> None:
    """Attempt a marker write without allowing I/O to affect the caller."""
    try:
        write_marker()
    except Exception:
        pass
