"""Read a note's four sections while accounting for every physical line."""

from __future__ import annotations

import re
from dataclasses import dataclass


HEADING = re.compile(r"^\s*(?:#{1,6}\s*)?([SOAP]):?\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(?:[^`]*)$")
CLOSER = re.compile(
    r"^\s*(?:-{3,}\s*$|`{3,}\s*$|(?:#{1,6}\s*)?"
    r"(?:Coding worksheet|Medatrax entry(?: block| fields)?|Tier block|"
    r"Drift matrix|Drift verdicts)\b)",
    re.IGNORECASE,
)
ORDER = "SOAP"


@dataclass(frozen=True)
class NoteSections:
    buckets: dict[str, str]
    sections: dict[str, str]

    @property
    def line_counts(self) -> dict[str, int]:
        return {name: len(text.splitlines()) for name, text in self.buckets.items()}


def parse(note: str) -> NoteSections:
    """Partition note into preamble, S/O/A/P, tail; refuse ambiguous boundaries."""
    lines = note.splitlines(keepends=True)
    fence: str | None = None
    for line in lines:
        plain = line.rstrip("\r\n")
        marker = FENCE.match(plain)
        if marker:
            run = marker.group(1)
            if fence is None:
                fence = run[0]
            elif run[0] == fence:
                fence = None
            continue
        if fence and (HEADING.fullmatch(plain) or CLOSER.match(plain)):
            raise ValueError("section boundary inside fence")
    starts: dict[str, int] = {}
    for index, line in enumerate(lines):
        heading = HEADING.fullmatch(line.rstrip("\r\n"))
        if heading:
            label = heading.group(1)
            if label in starts or label != ORDER[len(starts)]:
                raise ValueError("duplicate or out-of-order note section")
            starts[label] = index
            if len(starts) == 4:
                break
    if len(starts) != 4:
        raise ValueError("S, O, A, or P heading missing")
    end = next(
        (index for index in range(starts["P"] + 1, len(lines))
         if CLOSER.match(lines[index])), None
    )
    if end is None:
        raise ValueError("Plan has no recognized closer")
    for line in lines[starts["P"] + 1:end]:
        if HEADING.fullmatch(line.rstrip("\r\n")) or re.match(r"^\s*#{1,6}\s+", line):
            raise ValueError("unrecognized heading inside Plan")
    boundaries = [starts[label] for label in ORDER] + [end]
    buckets = {"preamble": "".join(lines[:boundaries[0]])}
    sections: dict[str, str] = {}
    for index, label in enumerate(ORDER):
        begin, stop = boundaries[index:index + 2]
        buckets[label] = "".join(lines[begin:stop])
        sections[label] = "".join(lines[begin + 1:stop])
        if not sections[label].strip():
            raise ValueError(f"{label} section empty")
    buckets["tail"] = "".join(lines[end:])
    return NoteSections(buckets, sections)
