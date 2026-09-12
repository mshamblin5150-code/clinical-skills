"""Formatting-robust membership assertions for prose-backed tests."""

import re
from collections.abc import Iterable
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import NamedTuple


#: Quotes, comment marks and emphasis are prose marks rather than part of the
#: words. A backslash was once included here and was removed after it
#: changed no result over every tracked ``.md`` and ``.py`` file while turning a
#: literal ``\n`` into an ``n`` mid-sentence. A transform that changes text and
#: buys nothing is an undeclared escape route.
PROSE_MARK = re.compile(r"[\"'#>*`]")

# Shared by every normalized prose-copy detector. Shorter leaves use exact
# normalized substring comparison instead.
SHINGLE = 9

NAMING = "naming"
ENUMERATION = "enumeration"
LIMIT_CONSTANTS = (
    "DECLARED_LIMITS",
    "NOT_REACHED",
    "NOT_GUARDED",
    "NOT_APPLIED",
    "NOT_STRIPPED",
    "NOT_VALIDATED_AGAINST",
    "ORPHANED_FIGURES",
    "LEGAL_READER_NOT_REACHED",
    "README_NOT_REACHED",
)


class UnreadObject(AssertionError):
    """A declared object from which the bind could read no prose."""


def _is_backslash_escaped(text: str, index: int) -> bool:
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


# This object declares the check's ceiling: a portable path containing a
# directory separator or filename dot, followed by a positive decimal
# coordinate. Bare words before a colon are not path-shaped.
PATH_COORDINATE_CEILING = re.compile(
    r"(?<![\w./:-])(?:"
    r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+"
    r"|[A-Za-z_][A-Za-z0-9_-]*\.[A-Za-z][A-Za-z0-9_.-]*"
    r"):[1-9][0-9]*\b"
)
FENCE = re.compile(
    r"^(?:(?:[ ]{0,3}>[ ]?)+)?"
    r"(?:[ \t]*(?:[-+*]|[0-9]+[.)])[ \t]+)?"
    r"[ \t]*(`{3,}|~{3,})(.*)$"
)


def prose_outside_fences(text: str) -> str:
    """Return prose outside Markdown fences while preserving line positions.

    This is deliberately narrower than :func:`prose_outside_code`: inline code
    remains visible because tracker coordinates inside code spans are graded.
    """

    kept: list[str] = []
    marker = ""
    width = 0
    for line in text.splitlines(keepends=True):
        match = FENCE.match(line)
        if not marker:
            if match:
                marker = match.group(1)[0]
                width = len(match.group(1))
                kept.append("\n" if line.endswith("\n") else "")
            else:
                kept.append(line)
            continue
        if (
            match
            and match.group(1)[0] == marker
            and len(match.group(1)) >= width
            and not match.group(2).strip()
        ):
            marker = ""
            width = 0
        kept.append("\n" if line.endswith("\n") else "")
    return "".join(kept)


LIST_PREFIX = re.compile(r" {0,3}(?:[-+*]|[0-9]{1,9}[.)])[ \t]{1,4}")
QUOTE_PREFIX = re.compile(r" {0,3}>[ \t]?")


class ContainerPrefix(NamedTuple):
    kind: str
    continuation_indent: int


class FenceOpening(NamedTuple):
    marker: str
    width: int
    containers: tuple[ContainerPrefix, ...]
    prefix_width: int


def _container_prefix(content: str) -> tuple[int, tuple[ContainerPrefix, ...]]:
    cursor = 0
    containers: list[ContainerPrefix] = []
    while True:
        if match := QUOTE_PREFIX.match(content, cursor):
            cursor = match.end()
            containers.append(ContainerPrefix("quote", 0))
            continue
        if match := LIST_PREFIX.match(content, cursor):
            containers.append(ContainerPrefix("list", match.end() - cursor))
            cursor = match.end()
            continue
        return cursor, tuple(containers)


def _opening_fence(line: str) -> FenceOpening | None:
    content = line.rstrip("\r\n")
    cursor, containers = _container_prefix(content)
    indent = len(content[cursor:]) - len(content[cursor:].lstrip(" "))
    cursor += indent
    if indent > 3 or cursor == len(content):
        return None
    marker = content[cursor]
    if marker not in "`~":
        return None
    run_end = cursor
    while run_end < len(content) and content[run_end] == marker:
        run_end += 1
    width = run_end - cursor
    if width < 3 or (marker == "`" and "`" in content[run_end:]):
        return None
    return FenceOpening(marker, width, containers, cursor)


def _fence_container_width(line: str, opening: FenceOpening) -> int:
    content = line.rstrip("\r\n")
    cursor = 0
    for container in opening.containers:
        if container.kind == "quote":
            match = QUOTE_PREFIX.match(content, cursor)
            if match is None:
                return 0
            cursor = match.end()
            continue
        indentation = content[cursor : cursor + container.continuation_indent]
        if len(indentation) != container.continuation_indent or indentation.strip(" "):
            return 0
        cursor += container.continuation_indent
    return cursor


def _is_closing_fence(line: str, opening: FenceOpening) -> bool:
    content = line.rstrip("\r\n")
    cursor = _fence_container_width(line, opening)
    if opening.containers and cursor == 0:
        return False
    indent = len(content[cursor:]) - len(content[cursor:].lstrip(" "))
    cursor += indent
    if indent > 3 or cursor == len(content) or content[cursor] != opening.marker:
        return False
    run_end = cursor
    while run_end < len(content) and content[run_end] == opening.marker:
        run_end += 1
    return run_end - cursor >= opening.width and not content[run_end:].strip(" \t")


def _mask_range(visible: list[str], start: int, end: int) -> None:
    for index in range(start, end):
        if visible[index] not in "\r\n":
            visible[index] = " "


def prose_outside_code(text: str) -> str:
    """Mask Markdown code while preserving every offset and line break."""

    visible = list(text)
    offset = 0
    fence: FenceOpening | None = None
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if fence is not None:
            prefix = _fence_container_width(line, fence)
            _mask_range(visible, offset + prefix, offset + len(content))
            if _is_closing_fence(line, fence):
                fence = None
            offset += len(line)
            continue
        opening = _opening_fence(line)
        if opening is not None:
            fence = opening
            _mask_range(visible, offset + opening.prefix_width, offset + len(content))
            offset += len(line)
            continue

        index = 0
        while index < len(content):
            if content[index] != "`":
                index += 1
                continue
            if _is_backslash_escaped(content, index):
                index += 1
                continue
            end = index
            while end < len(content) and content[end] == "`":
                end += 1
            delimiter = content[index:end]
            search_from = end
            close = -1
            while True:
                candidate = content.find(delimiter, search_from)
                if candidate < 0:
                    break
                after = candidate + len(delimiter)
                if (
                    (candidate == 0 or content[candidate - 1] != "`")
                    and (after == len(content) or content[after] != "`")
                ):
                    close = candidate
                    break
                search_from = candidate + 1
            if close == -1:
                index = end
                continue
            _mask_range(visible, offset + index, offset + close + len(delimiter))
            index = close + len(delimiter)
        offset += len(line)
    return "".join(visible)


def section(text: str, heading: str) -> str:
    """Return one Markdown section through its first peer or parent heading.

    ``heading`` is the complete ATX heading without trailing whitespace. Code is
    masked before headings are found, so heading-shaped lines inside code do not
    open or close a section. A hash followed by prose, such as a hard-wrapped
    ``#264`` ticket reference, is not an ATX heading.
    """

    visible = prose_outside_code(text)
    opener = re.search(rf"(?m)^{re.escape(heading)}[ \t]*\r?$", visible)
    if opener is None:
        raise ValueError(f"heading not found: {heading}")
    level_match = re.fullmatch(r"(#{1,6})[ \t]+.+", heading)
    if level_match is None:
        raise ValueError(f"not an ATX heading: {heading}")
    level = len(level_match.group(1))
    heading_pattern = re.compile(r"(?m)^(#{1,6})[ \t]+[^\r\n]*")
    for candidate in heading_pattern.finditer(visible, opener.end()):
        if len(candidate.group(1)) <= level:
            return text[opener.start() : candidate.start()]
    return text[opener.start() :]


def normalized(text: str | Iterable[str]) -> str:
    """Remove prose marks and collapse whitespace for one membership operand."""

    if not isinstance(text, str):
        text = "\n".join(text)
    return re.sub(r"\s+", " ", PROSE_MARK.sub(" ", text)).strip()


def string_leaves(value: object, seen: set[int] | None = None) -> tuple[str, ...]:
    """Read string leaves from the declared row shapes used by this repository."""

    if isinstance(value, Enum):
        return ()
    if isinstance(value, str):
        return (value,)
    if value is None or isinstance(value, (int, float, complex, bytes, bool)):
        return ()
    visited = set() if seen is None else seen
    identity = id(value)
    if identity in visited:
        return ()
    visited.add(identity)
    if is_dataclass(value) and not isinstance(value, type):
        return tuple(
            leaf
            for field in fields(value)
            for leaf in string_leaves(getattr(value, field.name), visited)
        )
    if isinstance(value, dict):
        return tuple(
            leaf
            for item in value.items()
            for part in item
            for leaf in string_leaves(part, visited)
        )
    if isinstance(value, (tuple, list, set, frozenset)):
        return tuple(leaf for item in value for leaf in string_leaves(item, visited))
    return ()


def shingles(text: str) -> set[str]:
    """Return the shared-width normalized word shingles in ``text``."""

    words = normalized(text).split()
    return {
        " ".join(words[index : index + SHINGLE])
        for index in range(len(words) - SHINGLE + 1)
    }


def copied_leaves(value: object, prose: str) -> tuple[tuple[str, int], ...]:
    """Return declared string leaves copied by a naming surface."""

    leaves = string_leaves(value)
    if not leaves:
        raise UnreadObject("object yielded zero string leaves")
    clean_prose = normalized(prose)
    prose_shingles = shingles(clean_prose)
    copied = []
    for leaf in leaves:
        clean = normalized(leaf)
        if not clean:
            continue
        if len(clean.split()) < SHINGLE:
            occurrences = clean_prose.count(clean)
            if occurrences:
                copied.append((leaf, occurrences))
        elif shingles(clean) & prose_shingles:
            copied.append((leaf, 1))
    return tuple(copied)


def _enumeration_findings(value: object, prose: str) -> tuple[tuple[str, int], ...]:
    leaves = string_leaves(value)
    if not leaves:
        raise UnreadObject("object yielded zero string leaves")
    clean_prose = normalized(prose)
    cursor = 0
    findings = []
    for leaf in leaves:
        clean = normalized(leaf)
        if not clean:
            continue
        position = clean_prose.find(clean, cursor)
        if position < 0:
            findings.append((leaf, clean_prose.count(clean)))
            continue
        cursor = position + len(clean)
    return tuple(findings)


def bind(
    value: object,
    prose: str,
    *,
    mode: str,
) -> tuple[tuple[str, int], ...]:
    """Return violations of an explicitly selected prose-surface obligation."""

    if mode == NAMING:
        return copied_leaves(value, prose)
    if mode == ENUMERATION:
        return _enumeration_findings(value, prose)
    raise ValueError(f"unknown prose-bind mode: {mode!r}")


class ProseBind:
    """Assert membership after normalizing both the needle and the haystack.

    This mixin makes a prose bind robust to hard wrapping, Markdown emphasis,
    comment marks, and quotes split across adjacent literals. It does not make
    prose inspection complete: tests that enumerate or count prose can still
    undercount silently, and detecting those sites would require data-flow
    analysis outside this helper's declared ceiling.
    """

    def assertProseIn(
        self,
        needle: str | Iterable[str],
        haystack: str | Iterable[str],
        msg: str | None = None,
    ) -> None:
        self.assertIn(normalized(needle), normalized(haystack), msg)

    def assertProseNotIn(
        self,
        needle: str | Iterable[str],
        haystack: str | Iterable[str],
        msg: str | None = None,
    ) -> None:
        self.assertNotIn(normalized(needle), normalized(haystack), msg)
