"""Extract cited tracker records and render metadata-only readback lines.

The module is deliberately offline: callers supply publication text and
already-fetched records.  It reports current metadata and asserts no drift.

Mention exclusions used by refusing scanners do not transfer here.  An extra
record costs one informational line, while an excluded record loses the very
readback this module exists to provide.  Therefore citations inside code,
quotes, and every other text position remain in the set.

What a completed read does not establish belongs to ``NOT_REACHED`` below.
"""

from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any


NOT_REACHED = (
    (
        "a fingerprint says a record moved, never what moved",
        "The fingerprint exposes current metadata and body length, but never "
        "the body text needed to identify what changed.",
    ),
    (
        "class (c), a verdict naming no record, is permanently unreachable",
        "A readback can inspect the publication target and named records only; "
        "an aggregate verdict naming no record has no bounded record to read.",
    ),
)

BARE_RECORD = re.compile(r"#(?P<number>[1-9][0-9]*)(?![0-9])")
URL_RECORD = re.compile(
    r"/(?:issues|pull)/(?P<number>[1-9][0-9]*)(?![0-9])",
    re.IGNORECASE,
)


def citation_numbers(
    text: str,
    publication_number: int | None = None,
) -> frozenset[int]:
    """Return every cited record number plus the publication target, if any."""
    numbers = {
        int(match.group("number"))
        for pattern in (BARE_RECORD, URL_RECORD)
        for match in pattern.finditer(text)
    }
    if publication_number is not None:
        numbers.add(publication_number)
    return frozenset(numbers)


def _label_names(record: Mapping[str, Any]) -> tuple[str, ...]:
    labels = record.get("labels", {})
    nodes = labels.get("nodes", []) if isinstance(labels, Mapping) else labels
    if not isinstance(nodes, list):
        raise ValueError("record labels were not a list")
    names = []
    for node in nodes:
        if isinstance(node, Mapping):
            name = node.get("name")
        else:
            name = node
        if not isinstance(name, str):
            raise ValueError("record label name was not text")
        names.append(name)
    return tuple(sorted(names))


def fingerprint_lines(
    records: Mapping[int, Mapping[str, Any] | None],
) -> tuple[str, ...]:
    """Render one metadata-only line for every resolved or unresolved record."""
    lines: list[str] = []
    for requested_number in sorted(records):
        record = records[requested_number]
        if record is None:
            lines.append(f"tracker readback: #{requested_number} unresolved")
            continue
        number = record.get("number")
        state = record.get("state")
        updated_at = record.get("updatedAt")
        body = record.get("body")
        if not isinstance(number, int) or not isinstance(state, str):
            raise ValueError("record number or state had the wrong type")
        if not isinstance(updated_at, str) or not isinstance(body, str):
            raise ValueError("record timestamp or body had the wrong type")
        labels = ", ".join(_label_names(record))
        lines.append(
            f"tracker readback: #{number} state={state} labels=[{labels}] "
            f"updatedAt={updated_at} body_length={len(body)}"
        )
    return tuple(lines)


def empty_citation_line() -> str:
    """Name the permanently unreachable aggregate class after a real scan."""
    return (
        "tracker readback: no cited record number; "
        "class (c) is reached by no mechanism"
    )
