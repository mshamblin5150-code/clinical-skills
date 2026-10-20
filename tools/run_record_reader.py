"""Shared tool-written record read: missing is distinct from unreadable (ADR 0422).

The caller supplies the record's decoder and shape validator. This adapter does
not certify the content's truth or infer a schema from its filename.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")

# ADR 0421 outbound damage set; ADR 0423 applies it to reference sheets.
# CR is conditional: only CR immediately before LF is a line ending.
OUTBOUND_CONTROL_CHARACTERS = frozenset(
    chr(code) for code in (*range(32), *range(127, 160)) if code != 10
)


def outbound_text_damage(text: str, *, allow_tab: bool = False) -> tuple[tuple[int, str], ...]:
    """Name every damaged line/character pair without disclosing its text."""
    found: dict[tuple[int, str], None] = {}
    line = 1
    for offset, character in enumerate(text):
        if character == "\n":
            line += 1
        elif character in OUTBOUND_CONTROL_CHARACTERS:
            if character == "\r" and text[offset + 1:offset + 2] == "\n":
                continue
            if character == "\t" and allow_tab:
                continue
            found[(line, character)] = None
    return tuple(found)


class UnreadableRecord(ValueError):
    """An existing record could not be decoded into its declared shape."""


def read_tool_record(path: Path, decode: Callable[[str], T]) -> T | None:
    """Return None only for an absent file; never recover partial evidence."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError) as failure:
        raise UnreadableRecord(f"{path.name}: unreadable bytes") from failure
    try:
        return decode(text)
    except (ValueError, TypeError, KeyError) as failure:
        raise UnreadableRecord(f"{path.name}: unreadable record shape") from failure
