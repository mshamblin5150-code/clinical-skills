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
from run_record_reader import read_tool_record, object_record, RecordShapeError, UnreadableRecord, fault_report


DECLARED_LIMITS = (
    ("unreadable tool-written records", "Existing stored evidence refuses through the shared record reader and is never replaced after a failed read.", run_grader.EvidenceDisposition.BEHAVIOR),
    ("section meaning", "The grammar partitions text; a reader decides whether content belongs under its heading.", run_grader.EvidenceDisposition.DECLARED_READING),
    ("portal readback", "The stored strings record what was typed, not what Medatrax saved.", run_grader.EvidenceDisposition.DECLARED_READING),
    ("older differences", "Divergence reports a changed derivation and never authorizes correcting a posted note.", run_grader.EvidenceDisposition.BEHAVIOR),
)


def _decode_sections(text: str) -> dict:
    stored = object_record(text)
    if set(stored) != set("SOAP") or any(not isinstance(value, str) for value in stored.values()):
        raise RecordShapeError("record fields")
    return stored


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
        stored = read_tool_record(destination, _decode_sections)
        existed = stored is not None
        if existed:
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
    except UnreadableRecord as error:
        print(fault_report(error, check="form sections"))
        print(run_grader.format_unread_remainder(1))
        return 2
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        print(f"form sections refused: {type(error).__name__}", file=sys.stderr)
        print(run_grader.format_unread_remainder(1))
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
