"""Draft or audit the one-row-per-topic threshold-sheet coverage registry."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import guidelines_catalog
from console_codec import use_utf8


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
DEFAULT_COVERAGE = REPO_ROOT / "reference" / "thresholds" / "coverage.md"
DEFAULT_SHEET_ROOT = REPO_ROOT / "reference" / "thresholds"
SCHEMA_MARKER = "<!-- schema: threshold-coverage/2 -->"
STATES = ("sheet", "none", "unread")


@dataclass(frozen=True)
class Entry:
    topic: str
    state: str
    artifact: str
    record: str
    line: int


def catalog_topics(path: Path) -> tuple[list[str], list[str]]:
    rows, _, problems = guidelines_catalog.parse_catalog(path.read_text(encoding="utf-8"))
    topics = sorted({" ".join(row.topic.split()) for row in rows}, key=str.casefold)
    return topics, problems


def parse_registry(text: str) -> tuple[list[Entry], list[str]]:
    problems: list[str] = []
    if SCHEMA_MARKER not in text:
        problems.append(f"coverage registry has no {SCHEMA_MARKER} marker")
    entries: list[Entry] = []
    in_table = False
    for number, line in enumerate(text.splitlines(), start=1):
        if re.match(
            r"^\|\s*topic\s*\|\s*state\s*\|\s*artifact\s*\|\s*record\s*\|\s*$",
            line,
            re.I,
        ):
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4 or all(set(cell) <= set("-: ") and cell for cell in cells):
            continue
        entries.append(Entry(cells[0], cells[1].casefold(), cells[2], cells[3], number))
    return entries, problems


def render_draft(topics: list[str]) -> str:
    rows = "\n".join(f"| {topic} |  |  |  |" for topic in topics)
    return (
        "# Threshold-sheet coverage\n\n"
        f"{SCHEMA_MARKER}\n\n"
        "| topic | state | artifact | record |\n"
        "| --- | --- | --- | --- |\n"
        f"{rows}\n"
    )


def audit(
    topics: list[str], entries: list[Entry], sheet_root: Path
) -> tuple[list[str], Counter[str]]:
    failures: list[str] = []
    counts = Counter(entry.state for entry in entries if entry.state in STATES)
    by_topic: dict[str, list[Entry]] = {}
    for entry in entries:
        by_topic.setdefault(entry.topic.casefold(), []).append(entry)
        if entry.state not in STATES:
            failures.append(
                f"coverage.md:{entry.line} topic '{entry.topic}' has unknown state '{entry.state}'"
            )
        if entry.state in STATES and not entry.record:
            failures.append(
                f"coverage.md:{entry.line} topic '{entry.topic}' state '{entry.state}' has no record"
            )
        if entry.state == "sheet" and not entry.artifact:
            failures.append(
                f"coverage.md:{entry.line} topic '{entry.topic}' state 'sheet' has no artifact"
            )
        if entry.artifact:
            artifact = Path(entry.artifact)
            if artifact.name != entry.artifact or artifact.suffix.casefold() != ".md":
                failures.append(
                    f"coverage.md:{entry.line} topic '{entry.topic}' has invalid artifact '{entry.artifact}'"
                )
            elif not (sheet_root / artifact).is_file():
                failures.append(
                    f"coverage.md:{entry.line} artifact '{entry.artifact}' does not exist"
                )

    wanted = {topic.casefold(): topic for topic in topics}
    for key, display in wanted.items():
        matches = by_topic.get(key, [])
        if not matches:
            failures.append(f"missing topic '{display}'")
        elif len(matches) > 1:
            failures.append(f"duplicate topic '{display}'")
    for key, matches in by_topic.items():
        if key not in wanted:
            for entry in matches:
                failures.append(f"coverage.md:{entry.line} unknown topic '{entry.topic}'")

    registered = {
        entry.artifact.casefold()
        for entry in entries
        if entry.artifact
    }
    for path in sorted(sheet_root.glob("*.md")):
        if path.name.casefold() in {"readme.md", "coverage.md"}:
            continue
        if path.name.casefold() not in registered:
            failures.append(f"sheet '{path.name}' has no registry artifact")
    return failures, counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--sheet-root", type=Path, default=DEFAULT_SHEET_ROOT)
    parser.add_argument("--draft", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        topics, problems = catalog_topics(args.catalog)
    except OSError as error:
        print(error, file=sys.stderr)
        return 2
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 2
    if args.draft:
        print(render_draft(topics), end="")
        return 0
    try:
        entries, parse_problems = parse_registry(args.coverage.read_text(encoding="utf-8"))
    except OSError as error:
        print(error, file=sys.stderr)
        return 2
    failures, counts = audit(topics, entries, args.sheet_root)
    failures = parse_problems + failures
    if failures:
        for failure in failures:
            print(f"REFUSING: {failure}", file=sys.stderr)
        return 1
    print(f"topics     {len(topics)}")
    for state in STATES:
        print(f"{state:<10} {counts[state]}")
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
