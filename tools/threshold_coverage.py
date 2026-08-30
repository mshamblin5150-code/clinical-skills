"""Draft or audit the one-row-per-topic threshold-sheet coverage registry."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import guidelines_catalog
import threshold_sheet
from console_codec import use_utf8


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
DEFAULT_COVERAGE = REPO_ROOT / "reference" / "thresholds" / "coverage.md"
DEFAULT_SHEET_ROOT = REPO_ROOT / "reference" / "thresholds"
SCHEMA_MARKER = "<!-- schema: threshold-coverage/2 -->"
STATES = ("sheet", "none", "non-source", "unread")


@dataclass(frozen=True)
class Entry:
    topic: str
    state: str
    artifact: str
    record: str
    line: int


def catalog_topics(rows: list[guidelines_catalog.Row]) -> list[str]:
    topics = sorted({" ".join(row.topic.split()) for row in rows}, key=str.casefold)
    return topics


def render_source_class_topics(
    rows: list[guidelines_catalog.Row], source_classes: list[str]
) -> str:
    wanted = {source_class.casefold() for source_class in source_classes}
    matches = sorted(
        {
            (row.cls, " ".join(row.topic.split()))
            for row in rows
            if row.cls.casefold() in wanted
        },
        key=lambda match: (match[0].casefold(), match[1].casefold()),
    )
    return "source class\ttopic\n" + "".join(
        f"{source_class}\t{topic}\n" for source_class, topic in matches
    )


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
    topics: list[str], entries: list[Entry], sheet_root: Path,
    page_counts: dict[str, int] | None = None,
    source_classes: dict[str, str] | None = None,
) -> tuple[list[str], Counter[str], Counter[str]]:
    failures: list[str] = []
    counts = Counter(entry.state for entry in entries if entry.state in STATES)
    artifact_counts = Counter(
        entry.state for entry in entries if entry.state in STATES and entry.artifact
    )
    by_topic: dict[str, list[Entry]] = {}
    page_counts = page_counts or {}
    source_classes = source_classes or {}
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
        if entry.state in {"sheet", "none", "non-source"} and not entry.artifact:
            failures.append(
                f"coverage.md:{entry.line} topic '{entry.topic}' state '{entry.state}' has no artifact"
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
            else:
                artifact_path = sheet_root / artifact
                sheet = threshold_sheet.parse(
                    artifact_path.read_text(encoding="utf-8"), artifact_path
                )
                if not sheet.ok:
                    failures.append(
                        f"coverage.md:{entry.line} artifact '{entry.artifact}' is not "
                        f"a usable threshold-sheet/2: {sheet.why_not}"
                    )
                    continue
                schema_findings = threshold_sheet.gate_schema(sheet, source_classes).findings
                if schema_findings:
                    failures.append(
                        f"coverage.md:{entry.line} artifact '{entry.artifact}' fails "
                        "threshold-sheet/2 schema: " + "; ".join(schema_findings)
                    )
                    continue
                unread = [span for span in sheet.spans if span.is_unread]
                # An overlapping positive span may cover the same page range as an
                # unread span. Completion requires both the page union and the
                # named-span inventory, or neither registry state could be valid.
                all_pages_read = bool(sheet.sources) and not unread
                for source_key, source in sheet.sources.items():
                    page_count = page_counts.get(source.get("document", ""))
                    if page_count is None:
                        all_pages_read = False
                        break
                    read_pages = {
                        page
                        for span in sheet.spans
                        if span.source == source_key and not span.is_unread
                        for page in range(span.first_page, span.last_page + 1)
                    }
                    if not set(range(1, page_count + 1)) <= read_pages:
                        all_pages_read = False
                        break
                if not sheet.rows and not all_pages_read:
                    failures.append(
                        f"coverage.md:{entry.line} zero-row artifact "
                        f"'{entry.artifact}' does not cover every catalog page and "
                        "cannot represent a completed null-sheet state"
                    )
                all_declared_non_source = bool(sheet.sources) and all(
                    source.get("source class")
                    in threshold_sheet.DECLARED_NON_SOURCE_CLASSES
                    for source in sheet.sources.values()
                )
                if all_pages_read and all_declared_non_source:
                    derived_state = "non-source"
                elif all_pages_read and sheet.rows:
                    derived_state = "sheet"
                elif all_pages_read:
                    derived_state = "none"
                else:
                    derived_state = "unread"
                if entry.state != derived_state:
                    failures.append(
                        f"coverage.md:{entry.line} topic '{entry.topic}' state "
                        f"'{entry.state}' disagrees with derived state '{derived_state}' "
                        f"from artifact '{entry.artifact}'"
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
    return failures, counts, artifact_counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--sheet-root", type=Path, default=DEFAULT_SHEET_ROOT)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--draft", action="store_true")
    output.add_argument(
        "--source-class",
        dest="source_classes",
        action="append",
        metavar="CLASS",
        help="print the distinct catalog topics supplied by CLASS; repeatable",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    catalog_facts = threshold_sheet.load_catalog_facts(args.catalog)
    if catalog_facts.parse_problems:
        for problem in catalog_facts.parse_problems:
            print(problem, file=sys.stderr)
        return 2
    rows = list(catalog_facts.rows)
    topics = catalog_topics(rows)
    if args.draft:
        print(render_draft(topics), end="")
        return 0
    if args.source_classes:
        print(render_source_class_topics(rows, args.source_classes), end="")
        return 0
    try:
        entries, parse_problems = parse_registry(args.coverage.read_text(encoding="utf-8"))
    except OSError as error:
        print(error, file=sys.stderr)
        return 2
    failures, counts, artifact_counts = audit(
        topics,
        entries,
        args.sheet_root,
        catalog_facts.page_counts,
        catalog_facts.source_classes,
    )
    failures = list(catalog_facts.problems) + failures
    failures = parse_problems + failures
    if failures:
        for failure in failures:
            print(f"REFUSING: {failure}", file=sys.stderr)
        return 1
    print(f"topics     {len(topics)} from {len(rows)} catalog rows")
    for state in STATES:
        qualifier = ""
        if state == "none":
            qualifier = (
                "   -- every span retired on a marker or a class exemption; "
                "no row carries a gated citation"
            )
        elif state == "non-source":
            qualifier = (
                "   -- every span retired; source form is in the declared "
                "non-source class set"
            )
        print(
            f"{state:<10} {counts[state]}   artifacts   {artifact_counts[state]}"
            f"{qualifier}"
        )
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
