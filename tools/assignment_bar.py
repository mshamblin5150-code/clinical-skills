"""Read the common signed envelope for a course-assignment artifact."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

import run_grader


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
