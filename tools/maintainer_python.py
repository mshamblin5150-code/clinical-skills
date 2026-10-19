#!/usr/bin/env python3
"""Report local interpreter drift from the maintainer CI pin, advisory. #1890."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

from console_codec import require_python_floor, use_utf8


PIN = Path(__file__).resolve().parent.parent / ".github" / "maintainer-python-version"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pin", type=Path, default=PIN)
    args = parser.parse_args()
    try:
        pinned = args.pin.read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", pinned):
            raise ValueError("pin must name major.minor.micro")
        expected = tuple(map(int, pinned.split(".")))
    except (OSError, UnicodeError, ValueError):
        print("Python advisory: comparison not made; maintainer pin unreadable or invalid.")
        return 0
    if sys.version_info[:3] != expected:
        installed = ".".join(map(str, sys.version_info[:3]))
        print(f"Python advisory: running {installed}; maintainer CI pins {pinned}; review {args.pin.name} after an upgrade.")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    sys.exit(main())
