"""The shared grammar for one ``icd10-cpt`` worksheet.

This module has no command line.  It owns the line shapes and the lower bound
used by graders that attribute an indented detail line to a code entry.
"""

from __future__ import annotations

import re


CODE = r"(?:[A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?|[0-9]{5}|[A-Z][0-9]{4})"

ENTRY = re.compile(
    rf"(?mi)^[ \t]*(?P<system>ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]+"
    rf"(?P<code>{CODE})[ \t]+(?P<descriptor>.+?)[ \t]*$"
)

FIELD = re.compile(
    r"(?mi)^[ \t]*(?P<field>ANCHOR|SOURCE|SPECIFICITY|CONFIDENCE|NOTE)[ \t]*:"
)

NOT_FOR_ENTRY = re.compile(r"(?mi)[ \t]NOT FOR ENTRY[ \t]*$")


def entry_is_for_entry(
    text: str, entries: list[re.Match[str]], index: int
) -> bool:
    """Whether one entry header lacks a line ending in ``NOT FOR ENTRY``.

    A field or the next entry closes the header. This retains readable historical
    worksheets whose official descriptor wrapped before the line-scoped marker.
    """

    start = entries[index].start()
    end = entries[index + 1].start() if index + 1 < len(entries) else len(text)
    field = FIELD.search(text, start, end)
    header = text[start : field.start() if field else end]
    return NOT_FOR_ENTRY.search(header) is None


def detail_belongs_to_entry(text: str, entry: re.Match[str], detail: re.Match[str]) -> bool:
    """Whether ``detail`` is in ``entry``'s contiguous indented body.

    The entry line itself ends at ``entry.end()``.  Every complete physical line
    after that and before the detail must contain text and begin with indentation.
    """

    if detail.start() <= entry.end():
        return False
    between = text[entry.end() : detail.start()]
    lines = between.splitlines()
    intervening = lines[1:] if lines else ()
    return all(line.strip() and line[0] in " \t" for line in intervening)


def paired_entry(
    text: str, entries: list[re.Match[str]], detail: re.Match[str]
) -> re.Match[str] | None:
    """Return the nearest entry above a detail when the pairing bound holds."""

    owner = next((entry for entry in reversed(entries) if entry.start() < detail.start()), None)
    if owner is None or not detail_belongs_to_entry(text, owner, detail):
        return None
    return owner
