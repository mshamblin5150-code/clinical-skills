#!/usr/bin/env python3
"""Persist the account's title-page credential choice for Word and slide runs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from repo_root import scratch_path, scratch_root


FIELD = "TITLE-PAGE-CREDENTIALS"
LINE = re.compile(r"^TITLE-PAGE-CREDENTIALS:[ \t]*(.*?)[ \t]*$", re.M)


def read(profile: Path) -> str:
    """Return the saved line, with an explicit ``none`` choice represented as empty."""
    text = profile.read_text(encoding="utf-8")
    matches = LINE.findall(text)
    if len(matches) != 1 or not matches[0]:
        raise ValueError("title-page credentials are silent or ambiguous; ask once and record the answer")
    return "" if matches[0] == "none" else matches[0]


def record(profile: Path, credentials: str) -> None:
    """Write an answered choice while preserving every other profile line."""
    if not credentials.strip() or "\n" in credentials or "\r" in credentials:
        raise ValueError("record a single nonempty credential line, or none")
    text = profile.read_text(encoding="utf-8")
    if len(LINE.findall(text)) > 1:
        raise ValueError("duplicate title-page credential settings need resolving")
    line = f"{FIELD}: {credentials.strip()}"
    if LINE.search(text):
        text = LINE.sub(lambda _: line, text)
    else:
        text = text.rstrip() + "\n\n## Title-page credentials\n\n" + line + "\n"
    partial = profile.with_name(profile.name + ".credentials-building")
    try:
        partial.write_text(text, encoding="utf-8")
        partial.replace(profile)
    finally:
        partial.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=scratch_path(scratch_root(), "medatrax-profile.md"))
    parser.add_argument("--record", metavar="LINE", help="clinician's answer; none omits credentials")
    args = parser.parse_args(argv)
    try:
        if args.record is not None:
            record(args.profile, args.record)
        print(read(args.profile))
    except (OSError, ValueError) as failure:
        print(f"title-page setting unresolved: {failure}")
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
