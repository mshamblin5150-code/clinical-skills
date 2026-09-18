#!/usr/bin/env python3
"""Create or compare the four Medatrax form sections from an Entry copy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import run_grader
from console_codec import require_python_floor, use_utf8
from note_grammar import parse


DECLARED_LIMITS = (
    ("section meaning", "The grammar partitions text; a reader decides whether content belongs under its heading.", run_grader.EvidenceDisposition.DECLARED_READING),
    ("portal readback", "The stored strings record what was typed, not what Medatrax saved.", run_grader.EvidenceDisposition.DECLARED_READING),
    ("older differences", "Divergence reports a changed derivation and never authorizes correcting a posted note.", run_grader.EvidenceDisposition.BEHAVIOR),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_copy", type=Path)
    parser.add_argument("--replace", action="store_true", help="explicitly replace stored evidence")
    args = parser.parse_args(argv)
    copy = args.entry_copy
    try:
        if copy.parent.name != "entry-copies" or not re.fullmatch(r"note-\d+\.md", copy.name):
            raise ValueError("expected entry-copies/note-N.md")
        parsed = parse(copy.read_text(encoding="utf-8"))
        sections = {label: parsed.sections[label].strip() for label in "SOAP"}
        destination = copy.parent.parent / "private" / "form-sections" / (copy.stem + ".json")
        existed = destination.exists()
        if existed:
            stored = json.loads(destination.read_text(encoding="utf-8"))
            if not isinstance(stored, dict) or set(stored) != set("SOAP") or any(
                not isinstance(value, str) for value in stored.values()
            ):
                raise ValueError("stored form sections have invalid shape")
            diverged = [label for label in "SOAP" if stored[label] != sections[label]]
        else:
            diverged = []
        if not existed or args.replace:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(sections, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8", newline="")
            action = "replaced" if existed else "created"
        else:
            action = "diverged" if diverged else "matched"
        for name in ("preamble", "S", "O", "A", "P", "tail"):
            print(f"{name}: lines {parsed.line_counts[name]}, characters {len(parsed.buckets[name])}")
        print(f"form sections {copy.name}: {action}; differing sections {len(diverged)}")
        print(run_grader.format_unread_remainder(0))
        return 0
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        print(f"form sections refused: {type(error).__name__}", file=sys.stderr)
        print(run_grader.format_unread_remainder(1))
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
