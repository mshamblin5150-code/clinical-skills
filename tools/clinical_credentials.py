#!/usr/bin/env python3
"""Read or record the account's signature and case-study prescribing credentials."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from repo_root import scratch_root


FIELDS = ("SIGNATURE-CREDENTIALS", "PRESCRIBING-CREDENTIALS")
LINES = tuple(re.compile(r"^" + field + r":[ \t]*(.*?)[ \t]*$", re.M) for field in FIELDS)


def read(profile: Path) -> tuple[str, str]:
    """Return both exact account choices; silence never supplies a default."""
    text = profile.read_text(encoding="utf-8")
    values = [line.findall(text) for line in LINES]
    if any(len(value) != 1 or not value[0] for value in values):
        raise ValueError("clinical credentials are silent or ambiguous; ask once for the missing choices and record the answer")
    return values[0][0], values[1][0]


def record(profile: Path, signature: str, prescribing: str) -> None:
    """Save the answered pair atomically, preserving unrelated profile fields."""
    answers = (signature, prescribing)
    if any(not answer.strip() or "\n" in answer or "\r" in answer for answer in answers):
        raise ValueError("record a single nonempty line for each clinical credential choice")
    text = profile.read_text(encoding="utf-8")
    if any(len(line.findall(text)) > 1 for line in LINES):
        raise ValueError("duplicate clinical credential settings need resolving")
    for field, pattern, answer in zip(FIELDS, LINES, answers):
        setting = f"{field}: {answer.strip()}"
        if pattern.search(text):
            text = pattern.sub(lambda _: setting, text)
        else:
            text = text.rstrip() + "\n" + setting + "\n"
    partial = profile.with_name(profile.name + ".clinical-credentials-building")
    try:
        partial.write_text(text, encoding="utf-8")
        partial.replace(profile)
    finally:
        partial.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=scratch_root() / "medatrax-profile.md")
    parser.add_argument("--signature", help="clinician's exact signature credential answer")
    parser.add_argument("--prescribing", help="clinician's exact prescribing-role credential answer")
    args = parser.parse_args(argv)
    try:
        if args.signature is not None or args.prescribing is not None:
            if args.signature is None or args.prescribing is None:
                raise ValueError("record both choices together; retain any already answered profile value")
            record(args.profile, args.signature, args.prescribing)
        signature, prescribing = read(args.profile)
        print(f"{FIELDS[0]}: {signature}\n{FIELDS[1]}: {prescribing}")
    except (OSError, ValueError) as failure:
        print(f"clinical credential settings unresolved: {failure}")
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
