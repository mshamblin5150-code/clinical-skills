"""Create one agent session's accounted working directory under scratch.

This producer deduplicates the destination used by documented commands.  It is
not enforcement: ``scratch_census.py`` remains the gate for material written at
a scratch root's top level.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import repo_root
from console_codec import use_utf8


def _create(child: str) -> Path:
    scratch = repo_root.scratch_root().resolve()
    sessions = scratch / "sessions"
    target = (sessions / child).resolve()
    if target.parent != sessions or sessions.parent != scratch:
        raise ValueError("refusing to create a path at the scratch top level")
    target.mkdir(parents=True, exist_ok=True)
    return target


def ticket_directory(ticket: int) -> Path:
    if ticket < 1:
        raise ValueError("ticket number must be a positive integer")
    return _create(f"ticket-{ticket}")


def sweep_directory(day: str) -> Path:
    try:
        parsed = date.fromisoformat(day)
    except ValueError:
        raise ValueError("sweep date must use YYYY-MM-DD") from None
    if parsed.isoformat() != day:
        raise ValueError("sweep date must use YYYY-MM-DD")
    return _create(f"sweep-{day}")


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] not in ("ticket", "sweep"):
        print(
            "usage: scratch_work.py (ticket <n> | sweep <YYYY-MM-DD>)",
            file=sys.stderr,
        )
        return 2
    try:
        if argv[0] == "ticket":
            if not argv[1].isdecimal():
                raise ValueError("ticket number must be a positive integer")
            target = ticket_directory(int(argv[1]))
        else:
            target = sweep_directory(argv[1])
    except (OSError, ValueError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2
    print(target)
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
