#!/usr/bin/env python3
"""Check explicitly supplied Markdown notes against the saved abdominal scheme.

Only physical examination text is checked. Recognized boundaries are the SOAP
Objective/O section (ending at tests or Assessment/A), or an explicit Physical
Exam/Examination heading (ending at tests or Assessment). Missing, ambiguous,
empty, or unclosed examination sections remain unread. This is a vocabulary
check, not verification that the named region was examined.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from repo_root import scratch_root
from run_grader import format_unread_remainder


def heading(line: str) -> str:
    return line.strip().lstrip("#").strip().replace("**", "").rstrip(":").strip().lower()


def examination(note: str) -> str | None:
    lines = note.splitlines()
    explicit = [i for i, line in enumerate(lines) if re.fullmatch(
        r"physical (?:exam|examination)(?:\s*\([^)]*\))?", heading(line)
    )]
    starts = explicit or [i for i, line in enumerate(lines) if heading(line) in ("o", "objective")]
    if len(starts) != 1:
        return None
    start = starts[0] + 1
    for end in range(start, len(lines)):
        label = heading(lines[end])
        if re.match(r"^(?:labs?(?:/tests|, x-ray, other tests)?|tests|assessment|a)(?:$|\s|:)", label):
            body = "\n".join(lines[start:end]).strip()
            # Objective alone may contain only vitals or tests, not an exam.
            system_lines = [heading(line) for line in lines[start:end]]
            has_system = any(
                re.match(r"^[a-z][a-z /-]*:", line)
                and line.split(":", 1)[0] not in ("vs", "vital signs", "bp", "hr", "rr", "temp", "spo2", "height", "weight", "bmi")
                for line in system_lines
            )
            if body and (explicit or has_system):
                return body
            return None
    return None


def saved_scheme(profile: str) -> str:
    blocks = re.findall(r"(?ims)^## Normal examination\s*\n(.*?)(?=^## |\Z)", profile)
    if len(blocks) != 1:
        raise ValueError("normal-examination block missing or ambiguous")
    schemes = re.findall(r"(?im)^Abdominal scheme:\s*(.*?)\s*$", blocks[0])
    if len(schemes) != 1 or schemes[0] not in ("nine regions", "four quadrants"):
        raise ValueError("abdominal scheme missing or invalid")
    return schemes[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notes", nargs="+", type=Path, help="every final note, supplied explicitly")
    parser.add_argument("--profile", type=Path, default=scratch_root() / "medatrax-profile.md")
    args = parser.parse_args(argv)
    read = found = unread = violations = 0
    try:
        scheme = saved_scheme(args.profile.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        print(f"notes supplied {len(args.notes)}; notes read 0; examination sections found 0")
        print("profile unread or abdominal scheme unavailable")
        print(format_unread_remainder(len(args.notes)))
        return 2
    for path in args.notes:
        try:
            note = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            unread += 1
            continue
        read += 1
        exam = examination(note)
        if exam is None:
            unread += 1
            continue
        found += 1
        if scheme == "nine regions" and re.search(r"\b(?:quadrants?|[rl][ul]q)\b", exam, re.I):
            violations += 1
    print(f"notes supplied {len(args.notes)}; notes read {read}; examination sections found {found}")
    print(f"notes with quadrant examination wording {violations}")
    print(format_unread_remainder(unread))
    return 1 if violations else 2 if unread else 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
