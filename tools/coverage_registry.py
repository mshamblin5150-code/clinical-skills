"""Pure owning reader and topic rewrite for threshold-coverage/3."""

from __future__ import annotations

import re
from dataclasses import dataclass

SCHEMA_MARKER = "<!-- schema: threshold-coverage/3 -->"


@dataclass(frozen=True)
class Entry:
    topic: str
    subject: str
    state: str
    artifact: str
    record: str
    line: int


def parse_registry(text: str) -> tuple[list[Entry], list[str]]:
    problems: list[str] = []
    if SCHEMA_MARKER not in text:
        problems.append(f"coverage registry has no {SCHEMA_MARKER} marker")
    entries: list[Entry] = []
    in_table = False
    for number, line in enumerate(text.splitlines(), start=1):
        if re.match(
            r"^\|\s*topic\s*\|\s*subject\s*\|\s*state\s*\|\s*artifact\s*\|\s*record\s*\|\s*$",
            line,
            re.I,
        ):
            in_table = True
            continue
        if in_table and not line.startswith("|"):
            in_table = False
        if not in_table:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= set("-: ") and cell for cell in cells):
            continue
        if len(cells) != 5:
            problems.append(f"coverage registry line {number}: {len(cells)} cells, expected 5")
            continue
        entries.append(
            Entry(cells[0], cells[1], cells[2].casefold(), cells[3], cells[4], number)
        )
    if not entries:
        problems.append("coverage registry table holds no row")
    return entries, problems


def topic_entry(text: str, topic: str) -> Entry:
    """Require a readable registry with exactly one matching topic."""
    entries, problems = parse_registry(text)
    if problems:
        raise ValueError("coverage registry: " + "; ".join(problems))
    matches = [entry for entry in entries if entry.topic.casefold() == topic.casefold()]
    if not matches:
        raise ValueError(f"coverage registry has no topic {topic!r}")
    if len(matches) != 1:
        raise ValueError(f"coverage registry has duplicate topic {topic!r}")
    return matches[0]


def mark_topic_unread(text: str, topic: str, record: str) -> str:
    """Rewrite only the topic line identified by the owning reader."""
    entry = topic_entry(text, topic)
    lines = text.splitlines()
    cells = (entry.topic, entry.subject, "unread", entry.artifact, record)
    lines[entry.line - 1] = "| " + " | ".join(cells) + " |"
    return "\n".join(lines) + "\n"
