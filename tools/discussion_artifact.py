"""Shared artifact parsing primitives for initial posts and replies.

The module owns syntax both graders consume and the reference-aware citation
boundary they share. It knows nothing about a signed bar, a roster, or which
findings either grader emits.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from collections.abc import Collection, Iterator
from dataclasses import dataclass


WORD = re.compile(r"\b[\w'-]+\b", re.UNICODE)
NUMBER = re.compile(r"(?<![\w])\d+(?:[.,]\d+)*(?:%|st|nd|rd|th)?(?![\w])", re.IGNORECASE)
INVOKED_FORM = "<!-- INVOKED: <domain> | <property> -->"
INVOKED = re.compile(
    r"(?mi)^\s*<!--\s*INVOKED\s*:\s*(?P<domain>[^\n|>]*)"
    r"(?:\|\s*(?P<property>[^\n>]*))?-->\s*$"
)
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
LEGAL_AUTHOR = r"(?:\b\d+\s+)?C\.\s*F\.\s*R\.\s*(?:§+|sections?\s+)\s*\d+(?:\.\d+)*"
LEGAL_CITATION = re.compile(
    r"(?:\(\s*(?P<parenthesized_author>" + LEGAL_AUTHOR + r")\s*,\s*"
    r"(?P<parenthesized_year>" + YEAR + r")\s*\)"
    r"|(?P<author>" + LEGAL_AUTHOR + r")"
    r"(?:\s*\((?P<year>" + YEAR + r")\))?)",
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
class InvokedSource:
    domain: str
    property: str


def read_invoked_sources(text: str) -> tuple[InvokedSource, ...]:
    """Read every current marker, including incomplete markers the graders reject."""

    return tuple(
        InvokedSource(
            marker.group("domain").strip(),
            (marker.group("property") or "").strip(),
        )
        for marker in INVOKED.finditer(text)
    )


def strip_discussion_markers(text: str) -> str:
    """Remove current and retired invisible working annotations."""

    return INVOKED.sub("", AMPLIFICATION.sub("", text))


def invoked_source_has_substance(source: InvokedSource) -> bool:
    """Return whether the property has lexical content beyond the domain noun."""

    grammar_only = {
        "a",
        "am",
        "an",
        "are",
        "be",
        "been",
        "being",
        "can",
        "could",
        "did",
        "do",
        "does",
        "had",
        "has",
        "have",
        "he",
        "i",
        "is",
        "it",
        "its",
        "may",
        "might",
        "must",
        "shall",
        "she",
        "should",
        "that",
        "the",
        "they",
        "this",
        "was",
        "we",
        "were",
        "will",
        "would",
        "you",
    }
    generic_only = {
        "action",
        "anything",
        "behavior",
        "domain",
        "effect",
        "everything",
        "nothing",
        "property",
        "something",
        "thing",
    }
    def terms(value: str) -> tuple[str, ...]:
        return tuple(
            token
            for token in re.findall(r"[a-z0-9]+", value.casefold())
            if token not in grammar_only
        )

    def singular(token: str) -> str:
        irregular = {"analyses": "analysis", "buses": "bus"}
        if token in irregular:
            return irregular[token]
        if len(token) > 4 and token.endswith("ies"):
            return token[:-3] + "y"
        if len(token) > 4 and token.endswith(("ches", "shes", "sses", "xes", "zes")):
            return token[:-2]
        if len(token) > 3 and token.endswith("s") and not token.endswith(("ics", "is", "ss", "us")):
            return token[:-1]
        return token

    domain_terms = {singular(token) for token in terms(source.domain)}
    added_terms = tuple(
        token
        for token in terms(source.property)
        if singular(token) not in domain_terms and singular(token) not in generic_only
    )
    return bool(domain_terms) and bool(added_terms)


@dataclass(frozen=True)
class Citation:
    author: str
    year: str
    start: int
    end: int


@dataclass(frozen=True)
class ReferenceSection:
    body: str
    references: tuple[str, ...]
    refused_label: str | None


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


def read_reference_section(
    text: str, accepted_label: re.Pattern[str]
) -> ReferenceSection:
    """Split a reference section and retain a recognizable refused label."""

    body, references = split_references(text, accepted_label)
    refused_label = (
        None if accepted_label.search(text) else recognized_reference_label(text)
    )
    return ReferenceSection(body, references, refused_label)


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
    legal = LEGAL_CITATION.search(author_text)
    if year is None and legal is None:
        return ()
    surnames = re.findall(
        r"(?:^|(?:,\s*&?|\s+&|\s+and)\s*)([" + UPPER + r"](?:" + LETTER + r"|['’.\-])*),\s*[" + UPPER + r"](?:[.\-]|\s|$)",
        author_text,
    )
    keys: list[str]
    if legal is not None:
        legal_author = _legal_author(legal)
        name_text = author_text[: legal.start()].rstrip("., ")
        if not name_text and year is not None:
            name_text = reference[year.end() :].strip(". ").split(".", 1)[0].strip()
        keys = [author_key(name_text)] if name_text else []
        keys.append(author_key(legal_author))
    elif surnames:
        keys = [author_key(surnames[0])]
        if len(surnames) > 1:
            keys.insert(0, author_key(" and ".join(surnames)))
    else:
        keys = [author_key(author_text)]
    years = [year.group("year").casefold()] if year is not None else [""]
    if legal is not None and "" not in years:
        years.append("")
    keyed: list[tuple[str, str]] = []
    for key in dict.fromkeys(keys):
        if not key:
            continue
        keyed.append((key, years[0]))
        if legal is not None and key == author_key(_legal_author(legal)) and len(years) > 1:
            keyed.append((key, ""))
    return tuple(keyed)


def legal_reference_lacks_name(reference: str) -> bool:
    """Return whether a legal entry's author slot is only its section."""

    year = REFERENCE_YEAR.search(reference)
    author_text = (
        reference[: year.start()].rstrip(". ")
        if year is not None
        else reference.rstrip(". ")
    )
    return LEGAL_CITATION.fullmatch(author_text) is not None


def reference_key(reference: str) -> tuple[str, str] | None:
    keys = reference_keys(reference)
    return keys[0] if keys else None


def read_citations(
    body: str,
    reference_key_set: Collection[tuple[str, str]] = (),
) -> tuple[Citation, ...]:
    """Read APA citations, including narrative names evidenced by references."""

    found: list[Citation] = []
    legal_citations = tuple(LEGAL_CITATION.finditer(body))
    legal_spans = tuple((match.start(), match.end()) for match in legal_citations)
    found.extend(
        Citation(
            _legal_author(match),
            _legal_year(match),
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
    if reference_key_set:
        max_key_length = max(len(key) for key, _year in reference_key_set)
        for year_match in REFERENCE_YEAR.finditer(body):
            if any(
                citation.start <= year_match.start()
                and year_match.end() <= citation.end
                for citation in found
            ):
                continue
            prefix = body[: year_match.start()]
            longest: Citation | None = None
            year_value = year_match.group("year").casefold()
            for word_start in _reverse_word_starts(prefix):
                author = prefix[word_start:].strip()
                key = author_key(author)
                if len(key) > max_key_length and not _personal_key_possible_to_left(
                    prefix, word_start
                ):
                    break
                if (key, year_value) in reference_key_set or (key, "") in reference_key_set:
                    longest = Citation(
                        author,
                        year_value,
                        word_start,
                        year_match.end(),
                    )
            if longest is not None:
                found.append(longest)
    return tuple(sorted(found, key=lambda citation: citation.start))


def _without_signal_word(author: str) -> str:
    return re.sub(r"^(?:As|In|By|See)\s+", "", author).strip()


def _legal_author(match: re.Match[str]) -> str:
    return match.group("parenthesized_author") or match.group("author")


def _legal_year(match: re.Match[str]) -> str:
    value = match.group("parenthesized_year") or match.group("year") or ""
    return value.casefold()


def _reverse_word_starts(value: str) -> Iterator[int]:
    """Yield word starts from the end without tokenizing the whole prefix."""

    cursor = len(value)
    while cursor:
        while cursor and not _author_word_character(value[cursor - 1]):
            cursor -= 1
        if not cursor:
            return
        while cursor and _author_word_character(value[cursor - 1]):
            cursor -= 1
        yield cursor


def _author_word_character(character: str) -> bool:
    return character.isalnum() or character == "_" or character in "'’&.-"


def _personal_key_possible_to_left(value: str, candidate_start: int) -> bool:
    """Return whether extending left can still trigger author_key's comma rule."""

    earlier = value[:candidate_start]
    sentence_start = max(
        earlier.rfind(". "),
        earlier.rfind("! "),
        earlier.rfind("? "),
    )
    return "," in earlier[sentence_start + 2 :]
