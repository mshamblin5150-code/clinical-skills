"""Read general-purpose Markdown structures; declared boundaries live in data."""

from __future__ import annotations

import posixpath
import re
from pathlib import Path
from typing import Callable, Iterator, NamedTuple, Pattern

from prose_bind import prose_outside_code


DECLARED_LIMITS = (
    "Markdown link destinations are not checked against section anchors.",
    "Code spans and fenced blocks are excluded only from link destinations; step citations "
    "remain readable there.",
    "Step citations outside a known owner remain unresolved unless a subject is adjacent.",
)

STEP_CITATION = re.compile(r"\bsteps?[-‑\s]+(\d+)\b", re.IGNORECASE)
CODE_FENCE = re.compile(r"^\s*(```|~~~)")
REFERENCE_DESTINATION = re.compile(r"(?m)^[ \t]{0,3}\[[^\]\r\n]+\]:[ \t]*")
ABSOLUTE_TARGET = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)


def unfenced_lines(text: str) -> Iterator[str]:
    """Document lines excluding fenced specimens and their delimiters."""
    fence = None
    for line in text.splitlines():
        opener = CODE_FENCE.match(line)
        if fence is not None:
            if opener and line.strip().startswith(fence):
                fence = None
            continue
        if opener:
            fence = opener.group(1)
            continue
        yield line


def paragraphs(text: str) -> Iterator[tuple[int, str]]:
    """Blocks of consecutive non-blank lines, with the line each one opens on."""
    block: list[str] = []
    start = 1
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip():
            if not block:
                start = number
            block.append(line)
        elif block:
            yield start, "\n".join(block)
            block = []
    if block:
        yield start, "\n".join(block)


class MarkdownTarget(NamedTuple):
    """One Markdown link destination and its source offset."""

    offset: int
    target: str


def _angle_destination(text: str, start: int) -> tuple[str, int] | None:
    target = []
    cursor = start + 1
    while cursor < len(text):
        if text[cursor] == "\\" and cursor + 1 < len(text):
            target.append(text[cursor + 1])
            cursor += 2
            continue
        if text[cursor] == ">":
            return "".join(target), cursor + 1
        if text[cursor] in "\r\n":
            return None
        target.append(text[cursor])
        cursor += 1
    return None


def _raw_destination(
    text: str,
    start: int,
    *,
    inline: bool,
) -> tuple[str, int] | None:
    target = []
    depth = 0
    cursor = start
    while cursor < len(text):
        char = text[cursor]
        if char == "\\" and cursor + 1 < len(text):
            target.append(text[cursor + 1])
            cursor += 2
            continue
        if char == "(":
            depth += 1
            target.append(char)
            cursor += 1
            continue
        if char == ")":
            if inline and depth == 0:
                break
            if depth == 0:
                return None
            depth -= 1
            target.append(char)
            cursor += 1
            continue
        if char.isspace() and depth == 0:
            break
        target.append(char)
        cursor += 1
    if depth or (not target and not inline):
        return None
    return "".join(target), cursor


def _closing_inline_link(text: str, start: int) -> int | None:
    cursor = start
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    if cursor < len(text) and text[cursor] == ")":
        return cursor + 1
    if cursor >= len(text) or text[cursor] not in "\"'(":
        return None
    opener = text[cursor]
    closer = ")" if opener == "(" else opener
    cursor += 1
    while cursor < len(text):
        if text[cursor] == "\\" and cursor + 1 < len(text):
            cursor += 2
            continue
        if text[cursor] == closer:
            cursor += 1
            break
        cursor += 1
    else:
        return None
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    return cursor + 1 if cursor < len(text) and text[cursor] == ")" else None


def _inline_destination(text: str, start: int) -> tuple[str, int] | None:
    cursor = start
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    if cursor < len(text) and text[cursor] == "<":
        parsed = _angle_destination(text, cursor)
    else:
        parsed = _raw_destination(text, cursor, inline=True)
    if parsed is None:
        return None
    target, cursor = parsed
    end = _closing_inline_link(text, cursor)
    return (target, end) if end is not None else None


def markdown_targets(text: str) -> Iterator[MarkdownTarget]:
    """Inline and reference-style Markdown destinations outside code."""
    prose = prose_outside_code(text)
    for found in REFERENCE_DESTINATION.finditer(prose):
        cursor = found.end()
        if cursor < len(prose) and prose[cursor] == "<":
            parsed = _angle_destination(prose, cursor)
        else:
            parsed = _raw_destination(prose, cursor, inline=False)
        if parsed is not None:
            yield MarkdownTarget(found.start(), parsed[0])

    cursor = 0
    while cursor < len(prose):
        label = prose.find("[", cursor)
        if label < 0:
            return
        close = prose.find("]", label + 1)
        if close < 0:
            return
        if close + 1 >= len(prose) or prose[close + 1] != "(":
            cursor = close + 1
            continue
        parsed = _inline_destination(prose, close + 2)
        if parsed is None:
            cursor = close + 1
            continue
        target, cursor = parsed
        yield MarkdownTarget(label, target)


def dead_links(
    text: str,
    owner: Path,
    exists: Callable[[Path], bool],
) -> list[tuple[int, str]]:
    """Relative Markdown targets in ``text`` that ``exists`` cannot find."""
    dead = []
    parent = owner.parent.as_posix()
    for found in markdown_targets(text):
        target = found.target
        if ABSOLUTE_TARGET.match(target) or target.startswith(("/", "//")):
            continue
        path_target = target.split("#", 1)[0]
        resolved = owner if not path_target else Path(
            posixpath.normpath(posixpath.join(parent, path_target))
        )
        if not exists(resolved):
            dead.append((text.count("\n", 0, found.offset) + 1, target))
    return dead


class Exemption(NamedTuple):
    """One counted marker and the paragraph it covers."""

    marker: int
    first: int
    last: int
    declared: int


def marker_exemptions(text: str, marker: Pattern[str]) -> list[Exemption]:
    """Every ``marker`` in ``text``, paired with the next paragraph's line range."""
    blocks = list(paragraphs(text))
    found = []
    for index, (start, block) in enumerate(blocks):
        if "\n" in block:
            continue
        matched = marker.fullmatch(block.strip())
        if not matched:
            continue
        declared = int(matched.group(1))
        if index + 1 == len(blocks):
            found.append(Exemption(start, start, start, declared))
            continue
        next_start, next_block = blocks[index + 1]
        found.append(
            Exemption(start, next_start, next_start + next_block.count("\n"), declared)
        )
    return found


class StepCitation(NamedTuple):
    """One ``step N``, and whose step N it turned out to be."""

    line: int
    number: int
    subject: str | None
    how: str


def step_citations(
    text: str,
    owner: str | None,
    names: list[str],
) -> Iterator[StepCitation]:
    """Every ``step N`` in ``text``, resolved to its subject or to nothing."""
    beside = re.compile("(" + "|".join(re.escape(name) for name in names) + r")\S*\s*$")
    anywhere = re.compile("|".join(re.escape(name) for name in names))
    for start, block in paragraphs(text):
        previous: str | None = None
        end = 0
        for found in STEP_CITATION.finditer(block):
            before = block[: found.start()]
            adjacent = beside.search(before)
            if adjacent:
                subject, how = adjacent.group(1), "beside"
            elif previous and not anywhere.search(block[end : found.start()]):
                subject, how = previous, "carried"
            else:
                subject, how = owner, "owner"
            previous, end = subject, found.end()
            yield StepCitation(
                start + before.count("\n"), int(found.group(1)), subject, how
            )
