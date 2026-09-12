#!/usr/bin/env python3
"""Grade coordinate accompaniment in tracker records and new ADRs.

The public ``grade`` seam reads only the supplied record text. A clean result
establishes only the bounded properties declared in
``tracker_coordinates.DECLARED_LIMITS``; it does not resolve a coordinate or
judge whether the accompanying anchor is the right one.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple, Sequence
import re
import subprocess
import sys

from console_codec import require_python_floor, use_utf8
from git_paths import GitPathError, read_path_records
from prose_bind import FENCE, PATH_COORDINATE_CEILING, prose_outside_fences
import tracker_bodies


UNANCHORED = "coordinate:unanchored"
CLEAN = 0
FOUND = 1
NOT_SCANNED = 2
ADR_CUTOFF = datetime(2026, 9, 12, 9, 51, 6, tzinfo=timezone.utc)

INVALID_INVOCATION = "arguments do not match the command surface"
EVENT_FILE_UNREADABLE = "the GitHub event file is absent or unreadable"
EVENT_SHAPE_UNREADABLE = "the GitHub event does not carry a readable record population"
EVENT_BODY_UNREADABLE = "a GitHub event record has no readable body"
ADR_POPULATION_UNREADABLE = "the tracked ADR population is absent or unreadable"
ADR_LAST_TOUCH_UNREADABLE = "an ADR last-touch commit or date is unreadable"
ADR_BODY_UNREADABLE = "an eligible ADR body is unreadable"
NOT_SCANNED_LIMBS = (
    INVALID_INVOCATION,
    EVENT_FILE_UNREADABLE,
    EVENT_SHAPE_UNREADABLE,
    EVENT_BODY_UNREADABLE,
    ADR_POPULATION_UNREADABLE,
    ADR_LAST_TOUCH_UNREADABLE,
    ADR_BODY_UNREADABLE,
)

DECLARED_LIMITS = (
    "An anchor is checked for presence, not resolution or relevance.",
    "Only welded path-and-line coordinates recognized by PATH_COORDINATE_CEILING are graded.",
    "A mention of coordinate decay is graded by the same accompaniment rule.",
    "Commit messages are outside the tracker and ADR populations.",
    "An ADR last touched before the declared cutoff remains outside the forward-only walk.",
)

BACKTICK_SPAN = re.compile(r"(?<!`)`([^`\r\n]+)`(?!`)")
PROSE_QUOTATION = re.compile(r'(?:"[^"\r\n]+"|“[^”\r\n]+”)')
BLOCK_QUOTE = re.compile(r" {0,3}>[ \t]?")
LIST_ITEM_START = re.compile(r"^[ \t]*(?:[-+*]|[0-9]+[.)])[ \t]+")
HEADING_START = re.compile(r"^ {0,3}#{1,6}[ \t]+")
SEARCHABLE_ANCHOR = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*")
NEXT_BLOCK_LINES = 3
REPO_ROOT = Path(__file__).resolve().parent.parent


class Finding(NamedTuple):
    rule: str
    locator: str
    coordinate: str


class AdrScan(NamedTuple):
    records: int
    eligible: int
    findings: tuple[Finding, ...]


class Scan(NamedTuple):
    records: int
    findings: tuple[Finding, ...]


class SourceError(Exception):
    """The requested population could not be read completely."""


def _paragraph_lines(visible: str, line_number: int) -> tuple[int, int]:
    lines = visible.splitlines()
    start = line_number
    while start > 0 and lines[start - 1].strip():
        if _begins_block(lines[start]) or _quote_state_changes(
            lines[start - 1], lines[start]
        ):
            break
        start -= 1
        if _begins_block(lines[start]):
            break
    end = line_number + 1
    while end < len(lines) and lines[end].strip():
        if _begins_block(lines[end]) or _quote_state_changes(
            lines[end - 1], lines[end]
        ):
            break
        end += 1
    return start, end


def _begins_block(line: str) -> bool:
    quote = BLOCK_QUOTE.match(line)
    while quote is not None:
        line = line[quote.end() :]
        quote = BLOCK_QUOTE.match(line)
    return LIST_ITEM_START.match(line) is not None or HEADING_START.match(line) is not None


def _quote_state_changes(left: str, right: str) -> bool:
    return (BLOCK_QUOTE.match(left) is None) != (BLOCK_QUOTE.match(right) is None)


def _has_paragraph_anchor(paragraph: str) -> bool:
    without_coordinates = PATH_COORDINATE_CEILING.sub("", paragraph)
    if any(
        SEARCHABLE_ANCHOR.search(match.group(0)) is not None
        for match in PROSE_QUOTATION.finditer(without_coordinates)
    ):
        return True
    for match in BACKTICK_SPAN.finditer(paragraph):
        content = match.group(1)
        remainder = PATH_COORDINATE_CEILING.sub("", content)
        if remainder == content:
            return bool(content.strip())
        if SEARCHABLE_ANCHOR.search(remainder) is not None:
            return True
        if re.search(r"[0-9=<>+*/&|~-]", remainder):
            return True
    return False


def _has_following_block(lines: list[str], paragraph_end: int) -> bool:
    candidates = lines[paragraph_end : paragraph_end + NEXT_BLOCK_LINES]
    for offset, line in enumerate(candidates):
        if not line.strip():
            continue
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)[0]
            width = len(fence.group(1))
            for content in lines[paragraph_end + offset + 1 :]:
                closing = FENCE.match(content)
                if (
                    closing
                    and closing.group(1)[0] == marker
                    and len(closing.group(1)) >= width
                    and not closing.group(2).strip()
                ):
                    return False
                if content.strip():
                    return True
            return False
        quote = BLOCK_QUOTE.match(line)
        return quote is not None and bool(line[quote.end() :].strip())
    return False


def grade(text: str, locator: str) -> tuple[Finding, ...]:
    """Return every unanchored coordinate in one supplied record string."""

    visible = prose_outside_fences(text)
    source_lines = text.splitlines()
    findings: list[Finding] = []
    for match in PATH_COORDINATE_CEILING.finditer(visible):
        line_number = visible.count("\n", 0, match.start())
        start, end = _paragraph_lines(visible, line_number)
        paragraph = "\n".join(source_lines[start:end])
        if (
            not _has_paragraph_anchor(paragraph)
            and not _has_following_block(source_lines, end)
        ):
            findings.append(Finding(UNANCHORED, locator, match.group(0)))
    return tuple(findings)


def survey(records: Sequence[tracker_bodies.Record]) -> Scan:
    """Grade one completely loaded tracker-event population."""

    if any(record.body is None for record in records):
        raise SourceError(EVENT_BODY_UNREADABLE)
    findings = tuple(
        finding
        for record in records
        for finding in grade(record.body, record.label)
    )
    return Scan(len(records), findings)


def _last_touch(root: Path, relative: str) -> datetime:
    try:
        completed = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", relative],
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
    except OSError as error:
        raise SourceError(f"{ADR_LAST_TOUCH_UNREADABLE}: {relative}") from error
    stamp = completed.stdout.strip()
    if completed.returncode != 0 or not stamp:
        raise SourceError(f"{ADR_LAST_TOUCH_UNREADABLE}: {relative}")
    try:
        return datetime.fromisoformat(stamp)
    except ValueError as error:
        raise SourceError(f"{ADR_LAST_TOUCH_UNREADABLE}: {relative}") from error


def grade_adrs(root: Path) -> AdrScan:
    """Grade tracked ADRs whose own last-touching commit meets the cutoff.

    A clean result means no eligible tracked ADR carries an unanchored
    coordinate. Untracked or unstaged ADRs remain invisible to the Git index.
    """

    try:
        relatives = tuple(
            sorted(
                read_path_records(
                    root, "ls-files", "--cached", "-z", "--", "docs/adr/*.md"
                )
            )
        )
    except GitPathError as error:
        raise SourceError(ADR_POPULATION_UNREADABLE) from error
    if not relatives:
        raise SourceError(ADR_POPULATION_UNREADABLE)

    findings: list[Finding] = []
    eligible = 0
    for relative in relatives:
        if _last_touch(root, relative) < ADR_CUTOFF:
            continue
        eligible += 1
        try:
            text = (root / relative).read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            raise SourceError(f"{ADR_BODY_UNREADABLE}: {relative}") from error
        findings.extend(grade(text, relative))
    return AdrScan(len(relatives), eligible, tuple(findings))


def format_report(
    findings: tuple[Finding, ...],
    source: str,
    records: int,
    *,
    eligible: int | None = None,
) -> str:
    lines = [
        f"tracker coordinates over {source}",
        "",
        f"  records read {records}",
    ]
    if eligible is not None:
        lines.append(f"  records at or after cutoff {eligible}")
    lines.append(f"  {UNANCHORED} {len(findings)}")
    if findings:
        lines.extend(("", "  each finding:"))
        lines.extend(
            f"    {row.rule} {row.locator} {row.coordinate}"
            for row in findings
        )
    return "\n".join(lines)


USAGE = (
    "usage: tracker_coordinates.py [--github-event <event.json> "
    "--event-name <name>]"
)


def main(argv: list[str], *, root: Path = REPO_ROOT) -> int:
    if not argv:
        try:
            scan = grade_adrs(root)
        except SourceError as error:
            print(str(error), file=sys.stderr)
            return NOT_SCANNED
        print(format_report(
            scan.findings,
            "forward-only docs/adr",
            scan.records,
            eligible=scan.eligible,
        ))
        return FOUND if scan.findings else CLEAN
    if (
        len(argv) != 4
        or argv.count("--github-event") != 1
        or argv.count("--event-name") != 1
    ):
        print(f"{INVALID_INVOCATION}; {USAGE}", file=sys.stderr)
        return NOT_SCANNED
    event_path = Path(argv[argv.index("--github-event") + 1])
    event_name = argv[argv.index("--event-name") + 1]
    if not event_path.is_file():
        print(f"{EVENT_FILE_UNREADABLE}: {event_path.name}", file=sys.stderr)
        return NOT_SCANNED
    try:
        records = tracker_bodies.load_github_event(event_path, event_name)
    except tracker_bodies.HarvestError as error:
        print(f"{EVENT_SHAPE_UNREADABLE}: {error}", file=sys.stderr)
        return NOT_SCANNED
    if not records:
        print(f"{EVENT_SHAPE_UNREADABLE}: no record in {event_path.name}", file=sys.stderr)
        return NOT_SCANNED
    try:
        scan = survey(records)
    except SourceError as error:
        print(str(error), file=sys.stderr)
        return NOT_SCANNED
    print(format_report(
        scan.findings, f"{event_name} event {event_path.name}", scan.records
    ))
    return FOUND if scan.findings else CLEAN


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
