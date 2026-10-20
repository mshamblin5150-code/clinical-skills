"""Read the common signed envelope for a course-assignment artifact."""

from __future__ import annotations

import re
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass
from datetime import date

import run_grader
from console_codec import use_utf8, require_python_floor
from run_record_reader import UnreadableRecord, fault_report, DamagedRecord, damaged_record_result


FIELD = re.compile(r"(?mi)^(?P<name>[A-Z][A-Z-]+)\s*:\s*(?P<value>[^\n]+?)\s*$")
COMMON_FIELDS = (
    "ASSIGNMENT",
    "SIGNED",
    "ARTIFACT",
    "SOURCE-CLASSES",
    "RECENCY-WINDOW-YEARS",
)
ADAPTERS = {
    "deck": "deck_scan",
    "docx": "assignment_docx_scan",
}
RECORD = "bar-signatures.json"
EXPECTED_ROW = "the assignment bar signature"
REMEDY = "show the changed lines, take a new reply, run the signing command"


@dataclass(frozen=True)
class Envelope:
    artifact: str
    fields: dict[str, str]
    counts: dict[str, int]


def parse(text: str) -> Envelope:
    """Return one validated common envelope without reading branch fields."""

    matches = tuple(FIELD.finditer(text))
    fields = {match.group("name"): match.group("value").strip() for match in matches}
    counts = {
        name: sum(match.group("name") == name for match in matches)
        for name in {match.group("name") for match in matches}
    }
    for name in COMMON_FIELDS:
        count = counts.get(name, 0)
        if count > 1:
            raise run_grader.SourceError(f"bar.md has a duplicate {name} field")
        if count == 0:
            raise run_grader.SourceError(f"bar.md needs a {name} field")
    try:
        date.fromisoformat(fields["SIGNED"])
    except ValueError as failure:
        raise run_grader.SourceError("bar.md SIGNED must be an ISO date") from failure
    artifact = fields["ARTIFACT"].casefold()
    if artifact not in ADAPTERS:
        raise run_grader.SourceError("bar.md ARTIFACT must be deck or docx")
    return Envelope(artifact, fields, counts)


def adapter_name(envelope: Envelope) -> str:
    """Return the deep artifact adapter selected by a signed envelope."""

    return ADAPTERS[envelope.artifact]


def _decode_signatures(text: str) -> dict:
    """Compatibility entrypoint; the shared signer owns the only schema."""
    import bar_signatures
    return bar_signatures._decode_signatures(text)


def _signatures(run: Path) -> list[dict]:
    import bar_signatures
    return bar_signatures._signatures(run)


def sign(run: Path, clinician_reply: str) -> dict:
    import bar_signatures
    return bar_signatures.sign(run, clinician_reply, skill="course-assignment")


def completion_gate(run: Path) -> tuple[bool, str]:
    import bar_signatures
    failed, report = bar_signatures.completion_gate(run, skill="course-assignment")
    return failed, report.replace(bar_signatures.EXPECTED_ROW, EXPECTED_ROW, 1)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sign a course-assignment bar after clinician confirmation.")
    parser.add_argument("run", type=Path)
    parser.add_argument("--reply", required=True, help="whole confirming clinician message")
    args = parser.parse_args(argv)
    try:
        entry = sign(args.run, args.reply)
    except DamagedRecord as failure:
        print(damaged_record_result(failure, check=EXPECTED_ROW, force=True)[1])
        return 1
    except UnreadableRecord as failure:
        print(fault_report(failure, check=EXPECTED_ROW))
        print(run_grader.format_unread_remainder(1))
        return 2
    except (OSError, UnicodeError, run_grader.SourceError) as failure:
        print(f"bar not signed: {failure}", file=sys.stderr)
        return 2
    print("assignment bar signed: " + entry["reply_verification"])
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
