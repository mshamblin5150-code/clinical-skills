"""Shared parsing primitives for initial posts and replies.

This module owns only syntax both graders consume. It knows
nothing about a signed bar, a roster, or which findings either grader emits.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass


WORD = re.compile(r"\b[\w'-]+\b", re.UNICODE)
NUMBER = re.compile(r"(?<![\w])\d+(?:[.,]\d+)*(?:%|st|nd|rd|th)?(?![\w])", re.IGNORECASE)
AMPLIFICATION = re.compile(r"(?mi)^\s*<!--\s*AMPLIFICATION\s*:[^>]+-->\s*$")
PAREN_BLOCK = re.compile(r"\((?P<inside>[^()]+)\)")
YEAR = r"(?:(?:19|20)\d{2}[a-z]?|(?i:n\.d\.(?:-[a-z])?))"
UPPER = re.escape(
    "".join(character for character in map(chr, range(sys.maxunicode + 1)) if character.isupper())
)
LETTER = r"[^\W\d_]"
PAREN_PAIR = re.compile(
    r"(?P<author>[" + UPPER + r"][^;]*?),\s*(?P<year>" + YEAR + r")"
    r"(?:,\s*(?:p{1,2}\.\s*)?\d+(?:[-–]\d+)?)?\s*$"
)
NAME = r"[" + UPPER + r"](?:" + LETTER + r"|['’.\-])*"
AUTHOR_PHRASE = NAME + r"(?:\s+(?:" + NAME + r"|of|for|the|and|&)){0,10}"
NARRATIVE_DEFINITION = re.compile(
    r"\b(?P<author>" + AUTHOR_PHRASE + r")\s*"
    r"\((?P<alias>[" + UPPER + r"][A-Z0-9.\-]*),\s*"
    r"(?P<year>" + YEAR + r")\)"
)
NARRATIVE_CITATION = re.compile(
    r"\b(?P<author>" + AUTHOR_PHRASE + r"(?:\s+et\s+al\.)?)\s*"
    r"\((?P<year>" + YEAR + r")"
    r"(?:,\s*(?:p{1,2}\.|para\.)\s*\d+(?:[-–]\d+)?)?\)"
)
LEGAL_CITATION = re.compile(
    r"(?P<author>(?:\b\d+\s+)?C\.\s*F\.\s*R\.\s*(?:§+|sections?\s+)\s*\d+(?:\.\d+)*)"
    r"(?:\s*\((?P<year>" + YEAR + r")\))?",
    re.IGNORECASE,
)
REFERENCE_YEAR = re.compile(r"\((?P<year>" + YEAR + r")\)")
CLAIM_BLOCK = re.compile(r"(?ms)^## CLAIM:\s*(?P<block>.*?)(?=^## CLAIM:|\Z)")
RESTATEMENT = re.compile(r"(?mi)^RESTATEMENT\s*:\s*(?P<value>.*(?:\n(?:[ \t]+\S.*))*)")
CLAIM_REFERENCE = re.compile(
    r"(?mi)^REFERENCE\s*:\s*(?P<value>.*(?:\n(?:[ \t]+\S.*))*)"
)
REFERENCE_LABEL_RECOGNIZER = re.compile(
    r"(?mi)^(?P<label>[ \t]*(?:#{1,6}[ \t]+)?"
    r"(?:\*\*References?\*\*|__References?__|\*References?\*|_References?_|References?)"
    r"\s*:?[ \t]*)$"
)


@dataclass(frozen=True)
class Citation:
    author: str
    year: str
    start: int
    end: int


def split_references(text: str, heading: re.Pattern[str]) -> tuple[str, tuple[str, ...]]:
    """Split one artifact at its declared reference heading."""

    match = heading.search(text)
    body = text[: match.start()] if match else text
    reference_text = text[match.end() :] if match else ""
    references = tuple(
        block.strip().replace("\n", " ")
        for block in re.split(r"\n\s*\n", reference_text.strip())
        if block.strip()
    )
    return body, references


def recognized_reference_label(text: str) -> str | None:
    """Return a plainly recognizable reference-label line, without accepting it."""

    match = REFERENCE_LABEL_RECOGNIZER.search(text)
    return match.group("label") if match else None


def author_key(value: str) -> str:
    value = unicodedata.normalize("NFC", value.strip())
    personal = re.match(
        r"^\s*(?P<surname>[^,]+),\s*[" + UPPER + r"](?:[.\-]|\s|$)",
        value,
    )
    if personal is not None:
        value = personal.group("surname")
    elif re.search(r"(?i)\s+et\s+al\.", value):
        value = re.split(r"(?i)\s+et\s+al\.", value, maxsplit=1)[0]
    value = re.sub(r"(?i)^the\s+", "", value.strip())
    value = value.replace("&", " and ")
    return "".join(character for character in value.casefold() if character.isalnum())


def citation_author_keys(value: str) -> tuple[str, ...]:
    """Return the exact key expressed by one citation phrase."""

    definition = re.fullmatch(r"\s*(?P<full>.+?)\s*\[(?P<alias>[^\]]+)\]\s*", value)
    if definition is not None:
        full = definition.group("full")
        values: tuple[str, ...] = (
            author_key(full),
            author_key(definition.group("alias")),
        )
        stripped = _without_signal_word(full)
        if stripped != full:
            values += (author_key(stripped),)
    else:
        values = (author_key(value),)
        stripped = _without_signal_word(value)
        if stripped != value:
            values += (author_key(stripped),)
    return tuple(dict.fromkeys(key for key in values if key))


def citation_occurrence_keys(
    citations: tuple[Citation, ...],
) -> tuple[tuple[tuple[str, str], ...], ...]:
    """Resolve full-name abbreviation definitions across citation occurrences."""

    aliases: dict[str, tuple[str, ...]] = {}
    occurrences: list[tuple[tuple[str, str], ...]] = []
    for citation in citations:
        author_keys = list(citation_author_keys(citation.author))
        if len(author_keys) > 1:
            full, alias, *alternates = author_keys
            aliases[alias] = tuple(dict.fromkeys((full, *alternates)))
        elif author_keys:
            full_keys = aliases.get(author_keys[0], ())
            author_keys.extend(full_keys)
        occurrences.append(
            tuple((key, citation.year) for key in dict.fromkeys(author_keys))
        )
    return tuple(occurrences)


def reference_keys(reference: str) -> tuple[tuple[str, str], ...]:
    """Return citation keys evidenced by one APA reference entry."""

    year = REFERENCE_YEAR.search(reference)
    author_text = (
        reference[: year.start()].rstrip(". ")
        if year is not None
        else reference.rstrip(". ")
    )
    legal = LEGAL_CITATION.fullmatch(author_text)
    if year is None and legal is None:
        return ()
    surnames = re.findall(
        r"(?:^|(?:,\s*&?|\s+&|\s+and)\s*)([" + UPPER + r"](?:" + LETTER + r"|['’.\-])*),\s*[" + UPPER + r"](?:[.\-]|\s|$)",
        author_text,
    )
    keys: list[str]
    if surnames:
        keys = [author_key(surnames[0])]
        if len(surnames) > 1:
            keys.insert(0, author_key(" and ".join(surnames)))
    else:
        keys = [author_key(author_text)]
    years = [year.group("year").casefold()] if year is not None else [""]
    if legal is not None and "" not in years:
        years.append("")
    return tuple(
        (key, year_value)
        for key in dict.fromkeys(keys)
        if key
        for year_value in years
    )


def reference_key(reference: str) -> tuple[str, str] | None:
    keys = reference_keys(reference)
    return keys[0] if keys else None


def read_citations(body: str) -> tuple[Citation, ...]:
    """Read recognized APA parenthetical and narrative citation occurrences."""

    found: list[Citation] = []
    legal_citations = tuple(LEGAL_CITATION.finditer(body))
    legal_spans = tuple((match.start(), match.end()) for match in legal_citations)
    found.extend(
        Citation(
            match.group("author"),
            match.group("year").casefold() if match.group("year") else "",
            match.start(),
            match.end(),
        )
        for match in legal_citations
    )
    definitions = tuple(NARRATIVE_DEFINITION.finditer(body))
    definition_spans = tuple((match.start(), match.end()) for match in definitions)
    found.extend(
        Citation(
            match.group("author")
            + " ["
            + match.group("alias")
            + "]",
            match.group("year").casefold(),
            match.start(),
            match.end(),
        )
        for match in definitions
    )
    for block in PAREN_BLOCK.finditer(body):
        if any(start <= block.start() and block.end() <= end for start, end in definition_spans + legal_spans):
            continue
        offset = block.start("inside")
        cursor = 0
        for part in block.group("inside").split(";"):
            leading = len(part) - len(part.lstrip())
            match = PAREN_PAIR.match(part.strip())
            if match:
                start = offset + cursor + leading
                found.append(
                    Citation(
                        match.group("author"),
                        match.group("year").casefold(),
                        start,
                        start + len(part.strip()),
                    )
                )
            cursor += len(part) + 1
    for match in NARRATIVE_CITATION.finditer(body):
        if any(start <= match.start() and match.end() <= end for start, end in definition_spans + legal_spans):
            continue
        found.append(
            Citation(
                match.group("author"),
                match.group("year").casefold(),
                match.start(),
                match.end(),
            )
        )
    return tuple(sorted(found, key=lambda citation: citation.start))


def _without_signal_word(author: str) -> str:
    return re.sub(r"^(?:As|In|By|See)\s+", "", author).strip()
