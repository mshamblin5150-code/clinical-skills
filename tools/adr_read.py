"""Read ADR ruling declarations and citations; declared boundaries live in data."""

from __future__ import annotations

import re
from typing import Iterator, NamedTuple

from markdown_read import marker_exemptions, unfenced_lines


DECLARED_LIMITS = (
    "Ruling ordinals identify declared positions without deciding what a ruling means.",
    "Ruling citations are read only when the ADR number and ordinal word are adjacent.",
    "Dependencies assembled at run time are outside these syntax-directed readers.",
)

ADR_HEADING = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
RULING_HEADING = re.compile(r"^(?:ruling|decision)\s+(\d+)\b", re.IGNORECASE)
NUMBERED_HEADING = re.compile(r"^(\d+)\.\s")
RULING_SECTION = re.compile(
    r"^(?:what is ruled|the ruling|rulings|the decisions|ruled\b|(?:\w+\s+)?addendum\b)",
    re.IGNORECASE,
)
RULING_ITEM = re.compile(r"^(?:\*\*(?:ruling\s+)?)?(\d+)\.\s", re.IGNORECASE)
RULING_CITATION = re.compile(
    r"\bADR\s+0*(\d+)(?:\]\([^\r\n]+?\))?(?:'s)?\s+"
    r"(ruling|point|decision|rule)\s+(\d+)\b",
    re.IGNORECASE,
)
RULING_EXEMPT_MARKER = re.compile(
    r"<!--\s*unresolved-ruling-citations:\s*(\d+)\s*-->"
)


def ruling_ordinals(text: str) -> list[int]:
    """Ruling ordinals in document order, across the record and its addenda."""
    ordinals = []
    in_ruling_section = True
    accepts_items = True
    for line in unfenced_lines(text):
        heading = ADR_HEADING.match(line)
        if heading:
            level, title = len(heading.group(1)), heading.group(2)
            numbered = RULING_HEADING.match(title)
            if level == 2 and numbered:
                ordinals.append(int(numbered.group(1)))
                in_ruling_section = False
                accepts_items = False
            elif level == 2:
                in_ruling_section = bool(RULING_SECTION.match(title))
                accepts_items = in_ruling_section
            elif in_ruling_section:
                numbered_item = NUMBERED_HEADING.match(title)
                if numbered_item and (
                    accepts_items or int(numbered_item.group(1)) == len(ordinals) + 1
                ):
                    ordinals.append(int(numbered_item.group(1)))
                    accepts_items = True
                    continue
                accepts_items = bool(RULING_SECTION.match(title))
            else:
                accepts_items = False
            continue
        if in_ruling_section:
            numbered = RULING_ITEM.match(line)
            if numbered and (accepts_items or int(numbered.group(1)) == len(ordinals) + 1):
                ordinals.append(int(numbered.group(1)))
                accepts_items = True
    return ordinals


class RulingCitation(NamedTuple):
    """One ADR coordinate citation found at the adjacency ruled by ADR 0075."""

    line: int
    record: int
    number: int
    word: str


def ruling_citations(text: str) -> Iterator[RulingCitation]:
    """Every adjacent ``ADR NNNN`` plus one of the four ordinal words."""
    for found in RULING_CITATION.finditer(text):
        yield RulingCitation(
            text.count("\n", 0, found.start()) + 1,
            int(found.group(1)),
            int(found.group(3)),
            found.group(2).lower(),
        )


def unresolved_ruling_citations(
    text: str,
    declared: dict[int, set[int]],
) -> list[str]:
    """Dangling ADR coordinates not exactly covered by a counted marker."""
    unresolved = [
        cite
        for cite in ruling_citations(text)
        if cite.record not in declared or cite.number not in declared[cite.record]
    ]
    spans = marker_exemptions(text, RULING_EXEMPT_MARKER)
    covering = [span for span in spans if span.declared >= 1]
    complaints = []
    for cite in unresolved:
        if not any(span.first <= cite.line <= span.last for span in covering):
            complaints.append(
                f"{cite.line}: ADR {cite.record:04d} {cite.word} {cite.number} does not exist"
            )
    for span in spans:
        held = len([cite for cite in unresolved if span.first <= cite.line <= span.last])
        if span.declared < 1:
            complaints.append(f"{span.marker}: a marker declaring nothing exempts nothing")
        elif held != span.declared:
            complaints.append(f"{span.marker}: declares {span.declared}, paragraph holds {held}")
    return sorted(complaints, key=lambda line: int(line.split(":")[0]))
