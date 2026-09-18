"""The shared grammar for one ``icd10-cpt`` worksheet.

This module has no command line.  It owns the line shapes and the lower bound
used by graders that attribute an indented detail line to a code entry.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# icd10-cpt step 4 has one set of phrases. The optional confirmation tail is part of the
# filled-anchor heading, while the old NOT CODED phrase remains a different block.
_PHRASES = {
    "differential": r"DIFFERENTIAL,[ \t]+DOCUMENTS[ \t]+MDM,[ \t]+NOT[ \t]+FOR[ \t]+ENTRY",
    "undocumented": r"UNDOCUMENTED,[ \t]+WOULD[ \t]+SUPPORT[ \t]+A[ \t]+MORE[ \t]+SPECIFIC[ \t]+CODE",
    "filled": r"CODED,[ \t]+ANCHOR[ \t]+WAS[ \t]+FILLED(?:[ \t]+[—-][ \t]+CONFIRM[ \t]+BEFORE[ \t]+SUBMITTING|:[ \t]*CONFIRM[ \t]+BEFORE[ \t]+SUBMITTING)?",
    "refusal": r"NOT[ \t]+CODED,[ \t]+NOTHING[ \t]+ESTABLISHED[ \t]+IT",
}


def _heading(phrase: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?im)^[ \t]*(?:---[ \t]*{phrase}[ \t]*---|"
        rf"#{{1,6}}[ \t]+(?:---[ \t]*{phrase}[ \t]*---|{phrase}))[ \t]*$"
    )


DIFFERENTIAL_HEADING = _heading(_PHRASES["differential"])
UNDOCUMENTED_HEADING = _heading(_PHRASES["undocumented"])
BLOCK_HEADING = _heading(_PHRASES["filled"])
REFUSAL_HEADING = _heading(_PHRASES["refusal"])
STEP_FOUR_START = _heading(
    rf"(?:{_PHRASES['undocumented']}|{_PHRASES['filled']}|{_PHRASES['refusal']})"
)
_BLOCKS = (DIFFERENTIAL_HEADING, UNDOCUMENTED_HEADING, BLOCK_HEADING, REFUSAL_HEADING)
_HEADING_SHAPE = re.compile(r"^[ \t]*(?:(?:#{1,6}[ \t]+)?---[^\r\n]+---|#{1,6}[ \t]+[^\r\n]+)[ \t]*$")
ANY_HEADING = re.compile(r"^[ \t]*(?:#{1,6}[ \t]+|---[ \t]+\S.*---[ \t]*$)")
_STEP_FOUR_WORD = re.compile(
    r"DIFFERENTIAL|NOT[ \t]+FOR[ \t]+ENTRY|NOT[ \t]+CODED|"
    r"ANCHOR[ \t]+WAS[ \t]+FILLED|UNDOCUMENTED",
    re.IGNORECASE,
)
_GENERIC_DIFFERENTIAL = re.compile(r"^[ \t]*#{1,6}[ \t]+DIFFERENTIAL[ \t]*$", re.IGNORECASE)


@dataclass(frozen=True)
class HeadingCounts:
    candidates: int
    unread: int
    off_template: int
    generic_differential: int


def heading_counts(text: str) -> HeadingCounts:
    """Return the keyword-heading population and its three dispositions.

    The candidate floor is limited to heading-shaped keyword lines. A generic
    ``### Differential`` is a known section label, counted separately so the
    preserved worksheets' section scaffolding never masquerades as an icd10-cpt step-4 block.
    Other titles without these words remain outside the population.
    """
    candidates = unread = off_template = generic_differential = 0
    for line in text.splitlines():
        if not _HEADING_SHAPE.fullmatch(line):
            continue
        if any(pattern.fullmatch(line) for pattern in _BLOCKS):
            candidates += 1
            off_template += int(not line.lstrip().startswith("---"))
        elif _STEP_FOUR_WORD.search(line):
            candidates += 1
            if _GENERIC_DIFFERENTIAL.fullmatch(line):
                generic_differential += 1
            else:
                unread += 1
    return HeadingCounts(candidates, unread, off_template, generic_differential)


CODE = r"(?:[A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?|[0-9]{5}|[A-Z][0-9]{4})"

ENTRY = re.compile(
    rf"(?mi)^[ \t]*(?P<system>ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]+"
    rf"(?P<code>{CODE})[ \t]+(?P<descriptor>.+?)[ \t]*$"
)

# Candidate forms deliberately admit common Markdown decoration around the same
# entry and field tokens.  Graders subtract their strict reads from these wider
# populations; they do not treat this grammar as a second accepted syntax.
ENTRY_CANDIDATE = re.compile(
    rf"(?mi)^[ \t]*(?:[-+*][ \t]+)?(?:\*\*)?"
    rf"(?P<system>ICD-?10(?:-CM)?|CPT|HCPCS)(?:\*\*)?[ \t]+"
    rf"(?P<code>{CODE})\b[^\r\n]*$"
)

FIELD = re.compile(
    r"(?mi)^[ \t]*(?P<field>ANCHOR|SOURCE|SPECIFICITY|CONFIDENCE|NOTE)[ \t]*:"
)


def field_candidates(text: str, field: str) -> list[re.Match[str]]:
    """Relaxed-prefix physical lines beginning with one named detail field."""
    return list(
        re.finditer(
            rf"(?mi)^[ \t]*(?:[-+*][ \t]+)?(?:\*\*)?"
            rf"{re.escape(field)}(?:\*\*)?[ \t]*:",
            text,
        )
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
