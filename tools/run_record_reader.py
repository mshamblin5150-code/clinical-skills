"""Shared tool-written record read: missing is distinct from unreadable (ADR 0422).

The caller supplies the record's decoder and shape validator. This adapter does
not certify the content's truth or infer a schema from its filename.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


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
