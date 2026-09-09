#!/usr/bin/env python3
"""Audit the manual-to-sheet bind recorded in the APA 7 coverage registry."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from console_codec import use_utf8
from prose_bind import normalized


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SHEET = REPO_ROOT / "skills" / "_shared" / "reference" / "apa7.md"
DEFAULT_COVERAGE = (
    REPO_ROOT / "skills" / "_shared" / "reference" / "apa7-coverage.md"
)
SCHEMA_MARKER = "<!-- schema: apa7-coverage/1 -->"
STATES = ("read-root", "ruled-out", "never-checked")
EMPTY = {"", "-", "—"}
SUBSTANCE_WORD = re.compile(r"[0-9A-Za-z]+")
MIN_SUBSTANCE_WORDS = 8
MIN_SPECIFIC_WORDS = 2
GENERIC_VERDICT_WORDS = {
    "a",
    "against",
    "all",
    "and",
    "carefully",
    "checked",
    "complete",
    "completely",
    "confirm",
    "confirmed",
    "correct",
    "evidence",
    "found",
    "independent",
    "independently",
    "it",
    "manual",
    "material",
    "opened",
    "read",
    "reader",
    "refutation",
    "reviewed",
    "section",
    "source",
    "the",
    "this",
    "today",
    "verified",
    "was",
}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
SHEET_HEADING = re.compile(r"^##\s+(\d+)\.\s+", re.MULTILINE)

# Historical manual-structure measurement recorded in ADR 0154 on 2026-09-08.
# Numbered sections are sequential through each chapter's recorded last number.
SECTION_LIMITS = {2: 28, 4: 30, 5: 10, 6: 52, 7: 36, 8: 36, 9: 52, 10: 16, 11: 10}
MEDIA_LIMITS = {
    2: (3, 5),
    4: (1, 0),
    5: (0, 0),
    6: (5, 0),
    7: (24, 21),
    8: (2, 7),
    9: (1, 4),
    10: (0, 0),
    11: (2, 0),
}

# The permanent boundary measured and ruled in ADR 0154. This command can grade
# recorded structure and evidence; it cannot widen what the source reads established.
DECLARED_LIMITS = {
    "reader-accuracy": (
        "A substantive record and independent refutation narrow, but cannot detect, "
        "a reader who opened the source and misread it."
    ),
    "out-of-scope-chapters": (
        "Chapters 1, 3, and 12 are governed only by written chapter rulings; their "
        "individual sections and media were not read for this registry."
    ),
    "sequential-census": (
        "The section population assumes every chapter's numbering is sequential "
        "through the recorded final section."
    ),
    "manual-site-agreement": (
        "The audit did not compare the manual with apastyle.apa.org for disagreement."
    ),
}


@dataclass(frozen=True)
class Entry:
    item: str
    title: str
    state: str
    checked: str
    evidence: str
    refutation: str
    sections: tuple[int, ...]
    digests: dict[int, str]
    line: int


def expected_items() -> tuple[str, ...]:
    items = [
        f"{chapter}.{number}"
        for chapter, last in SECTION_LIMITS.items()
        for number in range(1, last + 1)
    ]
    for chapter, (tables, figures) in MEDIA_LIMITS.items():
        items.extend(f"Table {chapter}.{number}" for number in range(1, tables + 1))
        items.extend(f"Figure {chapter}.{number}" for number in range(1, figures + 1))
    return tuple(items)


def substantive(cell: str) -> bool:
    """Reject terse or boilerplate verdicts while leaving accuracy to a reader."""
    words = [word.casefold() for word in SUBSTANCE_WORD.findall(cell)]
    specific = [word for word in words if word not in GENERIC_VERDICT_WORDS]
    return (
        cell not in EMPTY
        and len(words) >= MIN_SUBSTANCE_WORDS
        and len(specific) >= MIN_SPECIFIC_WORDS
    )


def sheet_sections(text: str) -> dict[int, str]:
    matches = list(SHEET_HEADING.finditer(text))
    return {
        int(match.group(1)): text[match.start() : matches[index + 1].start()]
        if index + 1 < len(matches)
        else text[match.start() :]
        for index, match in enumerate(matches)
    }


def section_digest(text: str) -> str:
    return hashlib.sha256(normalized(text).encode("utf-8")).hexdigest()


def _numbers(cell: str) -> tuple[int, ...]:
    if cell.strip() in EMPTY:
        return ()
    return tuple(int(value.strip()) for value in cell.split(","))


def _digests(cell: str) -> dict[int, str]:
    if cell.strip() in EMPTY:
        return {}
    result: dict[int, str] = {}
    for pair in cell.split(";"):
        key, separator, value = pair.strip().partition("=")
        if not separator:
            raise ValueError(f"invalid digest binding '{pair.strip()}'")
        section = int(key.strip())
        if section in result:
            raise ValueError(f"duplicate digest binding for section {section}")
        result[section] = value.strip()
    return result


def parse_registry(text: str) -> tuple[list[Entry], list[str]]:
    problems: list[str] = []
    if SCHEMA_MARKER not in text:
        problems.append(f"coverage registry has no {SCHEMA_MARKER} marker")
    entries: list[Entry] = []
    in_table = False
    for number, line in enumerate(text.splitlines(), start=1):
        if re.match(
            r"^\|\s*manual item\s*\|\s*title\s*\|\s*state\s*\|\s*checked\s*\|"
            r"\s*evidence\s*\|\s*refutation\s*\|\s*apa7 sections\s*\|\s*digests\s*\|\s*$",
            line,
            re.I,
        ):
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8 or all(set(cell) <= set("-: ") and cell for cell in cells):
            continue
        try:
            sections = _numbers(cells[6])
            digests = _digests(cells[7])
        except (ValueError, TypeError) as error:
            problems.append(f"apa7-coverage.md:{number} {error}")
            sections, digests = (), {}
        entries.append(
            Entry(
                item=cells[0],
                title=cells[1],
                state=cells[2].casefold(),
                checked=cells[3],
                evidence=cells[4],
                refutation=cells[5],
                sections=sections,
                digests=digests,
                line=number,
            )
        )
    return entries, problems


def audit(entries: list[Entry], sections: dict[int, str]) -> tuple[list[str], set[str]]:
    failures: list[str] = []
    stale: set[str] = set()
    expected = set(expected_items())
    by_item: dict[str, list[Entry]] = {}
    grounded: set[int] = set()

    for entry in entries:
        by_item.setdefault(entry.item, []).append(entry)
        if not entry.title or entry.title in EMPTY:
            failures.append(f"apa7-coverage.md:{entry.line} manual item '{entry.item}' has no title")
        if entry.state not in STATES:
            failures.append(
                f"apa7-coverage.md:{entry.line} manual item '{entry.item}' "
                f"has unknown state '{entry.state}'"
            )
        if entry.state in {"read-root", "ruled-out"}:
            if not DATE.fullmatch(entry.checked):
                failures.append(
                    f"apa7-coverage.md:{entry.line} manual item '{entry.item}' "
                    "has no YYYY-MM-DD checked date"
                )
            if not substantive(entry.evidence):
                failures.append(
                    f"apa7-coverage.md:{entry.line} manual item '{entry.item}' "
                    "has no substantive evidence"
                )
            if not substantive(entry.refutation):
                failures.append(
                    f"apa7-coverage.md:{entry.line} manual item '{entry.item}' "
                    "has no substantive refutation"
                )
        if entry.state == "read-root" and not entry.sections:
            failures.append(
                f"apa7-coverage.md:{entry.line} manual item '{entry.item}' "
                "has no apa7 section and digest bind"
            )
        if set(entry.sections) != set(entry.digests):
            failures.append(
                f"apa7-coverage.md:{entry.line} manual item '{entry.item}' "
                "has different apa7 section and digest keys"
            )
        for section in entry.sections:
            grounded.add(section)
            if section not in sections:
                failures.append(
                    f"apa7-coverage.md:{entry.line} manual item '{entry.item}' "
                    f"names nonexistent apa7.md section {section}"
                )
                continue
            digest = entry.digests.get(section, "")
            if not DIGEST.fullmatch(digest):
                failures.append(
                    f"apa7-coverage.md:{entry.line} manual item '{entry.item}' "
                    f"has invalid digest for apa7.md section {section}"
                )
                continue
            if digest != section_digest(sections[section]):
                stale.add(entry.item)
                print(
                    f"STALE: manual item '{entry.item}' bind for apa7.md section {section}",
                    file=sys.stderr,
                )

    for item in expected_items():
        matches = by_item.get(item, [])
        if not matches:
            failures.append(f"missing manual item '{item}'")
        elif len(matches) > 1:
            failures.append(f"duplicate manual item '{item}'")
    for item, matches in by_item.items():
        if item not in expected:
            for entry in matches:
                failures.append(
                    f"apa7-coverage.md:{entry.line} unknown manual item '{item}'"
                )
    for section in sorted(set(sections) - grounded):
        failures.append(f"apa7.md section {section} has no registry row")
    return failures, stale


def format_report(entries: list[Entry], stale: set[str]) -> str:
    counts = Counter(
        entry.state
        for entry in entries
        if entry.item not in stale and entry.state in STATES
    )
    return (
        f"manual items   {len(entries)}\n"
        f"read-to-root   {counts['read-root']}\n"
        f"ruled-out      {counts['ruled-out']}\n"
        f"never-checked  {counts['never-checked']}\n"
        f"gone-stale     {len(stale)}\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--sheet", type=Path, default=DEFAULT_SHEET)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--quiet", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sheet_text = args.sheet.read_text(encoding="utf-8")
        coverage_text = args.coverage.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(error, file=sys.stderr)
        return 2
    sections = sheet_sections(sheet_text)
    entries, parse_problems = parse_registry(coverage_text)
    failures, stale = audit(entries, sections)
    for failure in parse_problems + failures:
        print(f"REFUSING: {failure}", file=sys.stderr)
    print(format_report(entries, stale), end="")
    if parse_problems or failures:
        return 1
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
