"""Grade the threshold-subject evidence ledger and its bind to coverage.md.

Counts only by default. The committed ledger contains authored clinical evidence,
so findings name record fields and catalog topics without printing their contents.
Exit 0 means the record shape and two-way bind are clean, exit 1 means a finding,
and exit 2 means one of the two input files could not be read.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import threshold_coverage
from console_codec import use_utf8


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COVERAGE = REPO_ROOT / "reference" / "thresholds" / "coverage.md"
DEFAULT_LEDGER = REPO_ROOT / "reference" / "thresholds" / "subjects.md"
SCHEMA_MARKER = "<!-- schema: threshold-subjects/1 -->"
SUBJECT = re.compile(r"(?mi)^##[ \t]+SUBJECT[ \t]*:[ \t]*(.*?)[ \t]*$")
FIELD = re.compile(
    r"(?mi)^(DATE|ELECTED|ELECTION|REFUTATION)[ \t]*:[ \t]*(.*?)[ \t]*$"
)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Record:
    subject: str
    fields: dict[str, str]
    members: tuple[str, ...]
    evidence: dict[str, str]
    line: int


def _section(body: str, heading: str) -> str:
    match = re.search(
        rf"(?mis)^###[ \t]+{re.escape(heading)}[ \t]*$\n(.*?)(?=^##[#]?[ \t]+|\Z)",
        body,
    )
    return match.group(1) if match else ""


def _bullets(text: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"(?m)^[ \t]*-[ \t]+(.+?)[ \t]*$", text)
    ]


def parse_ledger(text: str) -> tuple[list[Record], list[str]]:
    problems: list[str] = []
    if SCHEMA_MARKER not in text:
        problems.append(f"subjects.md has no {SCHEMA_MARKER} marker")
    visible = re.sub(
        r"(?ms)^```.*?^```[ \t]*$",
        lambda match: "\n" * match.group(0).count("\n"),
        text,
    )
    matches = list(SUBJECT.finditer(visible))
    records: list[Record] = []
    for index, match in enumerate(matches):
        body = visible[
            match.end() : matches[index + 1].start() if index + 1 < len(matches) else None
        ]
        fields = {name.casefold(): value.strip() for name, value in FIELD.findall(body)}
        members = tuple(_bullets(_section(body, "MEMBERS")))
        evidence: dict[str, str] = {}
        for bullet in _bullets(_section(body, "EVIDENCE")):
            if ":" in bullet:
                member, value = bullet.split(":", 1)
                evidence[member.strip().casefold()] = value.strip()
        records.append(
            Record(
                subject=match.group(1).strip(),
                fields=fields,
                members=members,
                evidence=evidence,
                line=visible.count("\n", 0, match.start()) + 1,
            )
        )
    return records, problems


def audit(
    entries: list[threshold_coverage.Entry], records: list[Record]
) -> list[str]:
    findings: list[str] = []
    groups: dict[str, set[str]] = {}
    display: dict[str, str] = {}
    topics = [entry.topic for entry in entries]
    for entry in entries:
        if entry.subject == "?":
            continue
        for subject in threshold_coverage.parse_subject_cell(entry.subject, topics) or ():
            key = subject.casefold()
            groups.setdefault(key, set()).add(entry.topic.casefold())
            display.setdefault(key, subject)
    expected = {key: members for key, members in groups.items() if len(members) > 1}

    by_subject: dict[str, list[Record]] = {}
    for record in records:
        key = record.subject.casefold()
        by_subject.setdefault(key, []).append(record)
        label = f"subjects.md:{record.line} subject '{record.subject}'"
        for field in ("date", "elected", "election", "refutation"):
            if not record.fields.get(field):
                findings.append(f"{label} has no {field.upper()}")
        if record.fields.get("date") and not DATE.fullmatch(record.fields["date"]):
            findings.append(f"{label} has invalid DATE")
        if record.fields.get("elected", "").casefold() != key:
            findings.append(f"{label} ELECTED does not match its subject heading")
        if not record.members:
            findings.append(f"{label} has no MEMBERS")
        member_keys = {member.casefold() for member in record.members}
        if len(member_keys) != len(record.members):
            findings.append(f"{label} has a duplicate member")
        for member in record.members:
            if not record.evidence.get(member.casefold()):
                findings.append(f"{label} has no evidence for member '{member}'")
        wanted_members = expected.get(key)
        if wanted_members is None:
            findings.append(f"{label} has no multi-member group in coverage.md")
        elif member_keys != wanted_members:
            findings.append(f"{label} members disagree with coverage.md")

    for key, members in expected.items():
        matches = by_subject.get(key, [])
        if not matches:
            findings.append(f"missing record for subject '{display[key]}'")
        elif len(matches) > 1:
            findings.append(f"duplicate record for subject '{display[key]}'")
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        coverage_text = args.coverage.read_text(encoding="utf-8")
        ledger_text = args.ledger.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(error, file=sys.stderr)
        return 2
    entries, coverage_problems = threshold_coverage.parse_registry(coverage_text)
    records, ledger_problems = parse_ledger(ledger_text)
    findings = coverage_problems + ledger_problems + audit(entries, records)
    ruled_cells = sum(entry.subject != "?" for entry in entries)
    print(f"records      {len(records)}")
    print(f"ruled cells  {ruled_cells} / {len(entries)}")
    if findings:
        for finding in findings:
            print(f"REFUSING: {finding}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
