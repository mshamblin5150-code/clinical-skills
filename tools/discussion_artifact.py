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
from urllib.parse import parse_qs, urlparse


WORD = re.compile(r"\b[\w'-]+\b", re.UNICODE)
NUMBER = re.compile(r"(?<![\w])\d+(?:[.,]\d+)*(?:%|st|nd|rd|th)?(?![\w])", re.IGNORECASE)
INVOKED_FORM = "<!-- INVOKED: <domain> | <property> -->"
INVOKED = re.compile(
    r"(?mi)^\s*<!--\s*INVOKED\s*:\s*(?P<domain>[^\n|>]*)"
    r"(?:\|\s*(?P<property>[^\n>]*))?-->\s*$"
)
AMPLIFICATION = re.compile(r"(?mi)^\s*<!--\s*AMPLIFICATION\s*:[^>]+-->\s*$")
PAREN_BLOCK = re.compile(r"\((?P<inside>[^()]+)\)")
NONNUMERIC_DATE = r"(?:n\.d\.|in press)"
YEAR = r"(?:(?:19|20)\d{2}[a-z]?|(?i:" + NONNUMERIC_DATE + r"(?:-[a-z])?))"
REPUBLISHED_ORIGINAL_DATE = (
    r"(?:(?i:ca\.)\s*)?\d{1,4}(?:\s*–\s*\d{1,4})?"
    r"(?:\s*(?i:B\.C\.E\.|C\.E\.))?"
)
REPUBLISHED_DATE_ELEMENT = REPUBLISHED_ORIGINAL_DATE + r"/" + YEAR
UPPER = re.escape(
    "".join(character for character in map(chr, range(sys.maxunicode + 1)) if character.isupper())
)
LOWER = re.escape(
    "".join(
        character
        for character in map(chr, range(sys.maxunicode + 1))
        if character.islower()
    )
)
LETTER = r"[^\W\d_]"
PAREN_PAIR = re.compile(
    r"(?P<author>[*_]?[" + UPPER + r"][^;]*?),\s*(?P<year>" + YEAR + r")"
    r"(?P<rest>(?:,\s*" + YEAR + r")*"
    r"(?:,\s*[^()]*)?)\s*$"
)
REPUBLISHED_PAREN_PAIR = re.compile(
    r"(?P<author>[" + UPPER + r"][^;]*?),\s*"
    r"(?P<year>" + REPUBLISHED_DATE_ELEMENT + r")"
    r"(?:,\s*[^()]*)?\s*$"
)
NAME = r"[" + UPPER + r"](?:" + LETTER + r"|['’.\-])*"
NOT_SENTENCE_END = r"(?!(?<!v\.)(?<=[" + LOWER + r"’']\.)\s)"
AUTHOR_PHRASE = (
    NAME
    + r"(?:"
    + NOT_SENTENCE_END
    + r"\s+(?:"
    + NAME
    + r"|of|for|the|and|&|v\.)){0,10}"
)
NARRATIVE_DEFINITION = re.compile(
    r"\b(?P<author>" + AUTHOR_PHRASE + r")\s*"
    r"\((?P<alias>[" + UPPER + r"][A-Z0-9.\-]*),\s*"
    r"(?P<year>" + YEAR + r")\)"
)
NARRATIVE_CITATION = re.compile(
    r"\b(?P<author>" + AUTHOR_PHRASE + r"(?:\s+et\s+al\.)?)\s*"
    r"\((?P<year>" + YEAR + r")"
    r"(?P<rest>(?:,\s*" + YEAR + r")*)"
    r"(?:,\s*(?:p{1,2}\.|para\.)\s*\d+(?:[-–]\d+)?)?\)"
)
ADDITIONAL_DATE = re.compile(r"^\s*,\s*(?P<year>" + YEAR + r")(?![A-Za-z0-9])")
DATE_VALUE = re.compile(r"(?P<year>" + YEAR + r")(?![A-Za-z0-9])")
EVIDENCE_DATE_VALUE = re.compile(
    r"(?P<year>" + REPUBLISHED_DATE_ELEMENT + r"|" + YEAR + r")(?![A-Za-z0-9])"
)
DATE_SERIES = re.compile(
    r"^\s*" + YEAR + r"(?:\s*,\s*" + YEAR + r")*"
    r"(?:,\s*(?:p{1,2}\.|para\.)\s*\d+(?:[-–]\d+)?)?\s*$"
)
FENCED_CODE = re.compile(r"(?ms)^(\x60\x60\x60|~~~).*?^\1[ \t]*$")
INLINE_CODE = re.compile(r"\x60+[^\x60\n]*\x60+")
REPUBLISHED_NARRATIVE_CITATION = re.compile(
    r"\b(?P<author>" + AUTHOR_PHRASE + r"(?:\s+et\s+al\.)?)\s*"
    r"\((?P<year>" + REPUBLISHED_DATE_ELEMENT + r")"
    r"(?:,\s*[^()]{0,100})?\)"
)
LEGAL_SECTION_NUMBER = (
    r"\d+[A-Za-z]*(?:\.\d+)*(?:\([\w]+\))*"
    r"(?:-\d+[A-Za-z]?(?:\.\d+)*(?:\([\w]+\))*)*"
)
LEGAL_SOURCE_VOCABULARY = (
    "W. Va. Code R.",
    "W. Va. Code",
)
_MIXED_CASE_LEGAL_SOURCE = "|".join(
    re.escape(source).replace(r"\ ", r"\s+")
    for source in LEGAL_SOURCE_VOCABULARY
)
_TITLE_NUMBER_LEGAL_SOURCE = r"\b\d+\s+(?-i:(?:[A-Z](?:\.\s*)?){2,})"
_LISTED_LEGAL_SOURCE = r"(?-i:" + _MIXED_CASE_LEGAL_SOURCE + r")"
LEGAL_SOURCE = (
    r"(?:" + _TITLE_NUMBER_LEGAL_SOURCE + r"|" + _LISTED_LEGAL_SOURCE + r")"
)
LEGAL_READER_NOT_REACHED = (
    (
        "unlisted legal Source",
        "An unlisted code reads as non-legal even when it is a valid legal source.",
    ),
    (
        "refused session-law forms",
        "Public Law and Pub. L. spellings are refused because they match prose, and a Statutes at Large parallel citation is refused because it would add a second legal span.",
    ),
    (
        "leftmost legal span",
        "The reader takes the leftmost legal span and cannot distinguish an entry's authority from a codification cross-reference.",
    ),
    (
        "legal form and authority status",
        "The code-section reader does not validate cases, legislative materials, proposed rules, executive orders, patents, constitutions, treaties, parallel reporters, official-version choice, state-specific form, or whether an authority remains current.",
    ),
)
_TITLE_NUMBER_LEGAL_AUTHOR = (
    _TITLE_NUMBER_LEGAL_SOURCE + r"\s*(?:§+|sections?\s+)\s*" + LEGAL_SECTION_NUMBER
)
_LISTED_LEGAL_AUTHOR = (
    _LISTED_LEGAL_SOURCE + r"\s*(?:§+|sections?\s+)\s*" + LEGAL_SECTION_NUMBER
)
_SESSION_LAW_AUTHOR = (
    r"(?-i:Pub\.\s+L\.\s+No\.)\s+\d+-\d+,\s*§+\s*" + LEGAL_SECTION_NUMBER
)
SESSION_LAW_AUTHOR_FORMS = (_SESSION_LAW_AUTHOR,)
LEGAL_READER_MECHANISMS = (
    (_TITLE_NUMBER_LEGAL_AUTHOR, "title-number uppercase codes by shape"),
    (
        _LISTED_LEGAL_AUTHOR,
        f"{len(LEGAL_SOURCE_VOCABULARY)} listed mixed-case Source forms",
    ),
    (
        r"(?:" + "|".join(SESSION_LAW_AUTHOR_FORMS) + r")",
        f"{len(SESSION_LAW_AUTHOR_FORMS)} fixed session-law form",
    ),
)
LEGAL_AUTHOR = (
    r"(?:" + "|".join(pattern for pattern, _description in LEGAL_READER_MECHANISMS) + r")"
)
LEGAL_CITATION = re.compile(
    r"(?:\(\s*(?P<parenthesized_author>" + LEGAL_AUTHOR + r")\s*,\s*"
    r"(?P<parenthesized_year>" + YEAR + r")(?:\s*\)|(?=\s*;))"
    r"|(?<=;)\s*(?P<continued_author>" + LEGAL_AUTHOR + r")\s*,\s*"
    r"(?P<continued_year>" + YEAR + r")(?=\s*(?:;|\)))"
    r"|(?P<author>" + LEGAL_AUTHOR + r")"
    r"(?:\s*\((?P<year>" + YEAR + r")\))?)",
    re.IGNORECASE,
)
REFERENCE_DATE_WORDS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
    "Spring",
    "Summer",
    "Fall",
    "Autumn",
    "Winter",
)
REFERENCE_YEAR = re.compile(
    r"\((?P<year>" + YEAR + r")"
    r"(?:,\s*(?:" + "|".join(REFERENCE_DATE_WORDS) + r")\b[^()]*)?\)"
)
CLAIM_BLOCK = re.compile(r"(?ms)^## CLAIM:\s*(?P<block>.*?)(?=^## CLAIM:|\Z)")
RESTATEMENT = re.compile(r"(?mi)^RESTATEMENT\s*:\s*(?P<value>.*(?:\n(?:[ \t]+\S.*))*)")
CLAIM_REFERENCE = re.compile(
    r"(?mi)^REFERENCE\s*:\s*(?P<value>.*(?:\n(?:[ \t]+\S.*))*)"
)
CLAIM_STATUS = re.compile(r"(?mi)^STATUS\s*:\s*(?P<value>[^\n]*)$")
CLAIM_REFUTATION = re.compile(r"(?mi)^REFUTATION\s*:\s*(?P<value>[^\n]*)$")
REFERENCE_LABEL_RECOGNIZER = re.compile(
    r"(?mi)^(?P<label>[ \t]*(?:#{1,6}[ \t]+)?"
    r"(?:\*\*References?\*\*|__References?__|\*References?\*|_References?_|References?)"
    r"\s*:?[ \t]*)$"
)
REREAD_BLOCK = re.compile(
    r"(?ms)^## REREAD:\s*(?P<artifact>[^\n]+?)\s*$"
    r"(?P<body>.*?)(?=^## REREAD:|\Z)"
)
REREAD_FIELD = re.compile(
    r"(?mi)^(?P<name>POST-URL|POSTED|READ|VERDICT)\s*:\s*(?P<value>[^\n]*)$"
)
REREAD_FIELDS = ("POST-URL", "POSTED", "READ", "VERDICT")
POSTED_READING_VERDICTS = frozenset({"matches", "diverges"})
AUTOMATED_RENDERED_SOURCES = frozenset(("word-pdf", "word-xps"))
RENDERED_SOURCES = AUTOMATED_RENDERED_SOURCES | {"canvas-box", "clinician"}


def claim_record_can_certify_values(block: str) -> bool:
    """Whether a downstream claim certifier may use this record's substance.

    Imports are deliberately local: ``research_ledger`` reaches this module
    through ``reference_scan``, while the ledger remains the one owner of both
    vocabularies and their keyword parser.
    """
    from research_ledger import (
        REFUTATION_REFUTED,
        REFUTATION_VALUES,
        STATUSES,
        UNREADABLE,
        UNSOURCED,
        keyword_of,
    )

    status_match = CLAIM_STATUS.search(block)
    refutation_match = CLAIM_REFUTATION.search(block)
    status = keyword_of(
        status_match.group("value") if status_match else "", STATUSES
    )[0]
    refutation = keyword_of(
        refutation_match.group("value") if refutation_match else "",
        REFUTATION_VALUES,
    )[0]
    return status not in {UNSOURCED, UNREADABLE} and refutation != REFUTATION_REFUTED


@dataclass(frozen=True)
class InvokedSource:
    domain: str
    property: str


@dataclass(frozen=True)
class PostedReading:
    artifact: str
    post_url: str
    posted: str
    read: str
    verdict: str
    verdict_detail: str
    missing_fields: tuple[str, ...]

    @property
    def missing_record_fields(self) -> tuple[str, ...]:
        return tuple(
            field for field in self.missing_fields if field in {"POSTED", "READ"}
        )

    @property
    def verdict_is_known(self) -> bool:
        return self.verdict in POSTED_READING_VERDICTS

    @property
    def verdict_has_substance(self) -> bool:
        return self.verdict_is_known and bool(self.verdict_detail)

    @property
    def entry_id(self) -> str | None:
        return discussion_entry_id(self.post_url)


def read_posted_readings(text: str) -> tuple[PostedReading, ...]:
    """Read run-level ``## REREAD: <artifact>`` records shared by both graders."""

    if not text.strip():
        return ()
    blocks = tuple(REREAD_BLOCK.finditer(text))
    if not blocks:
        raise ValueError("reread.md contains no readable REREAD records")
    if text[: blocks[0].start()].strip():
        raise ValueError("reread.md has unreadable content before its first REREAD record")
    artifacts: set[str] = set()
    records: list[PostedReading] = []
    for block in blocks:
        artifact = block.group("artifact").strip()
        if artifact in artifacts:
            raise ValueError(f"reread.md has a duplicate REREAD record for {artifact}")
        artifacts.add(artifact)
        matches = tuple(REREAD_FIELD.finditer(block.group("body")))
        if REREAD_FIELD.sub("", block.group("body")).strip():
            raise ValueError(f"reread.md has unreadable content in {artifact}")
        fields: dict[str, str] = {}
        for match in matches:
            name = match.group("name").upper()
            if name in fields:
                raise ValueError(f"reread.md has a duplicate {name} field for {artifact}")
            fields[name] = match.group("value").strip()
        verdict_text = fields.get("VERDICT", "")
        verdict_match = re.match(
            r"(?P<keyword>[^\s:—-]+)(?:\s*(?:-|—|:)\s*(?P<detail>.*))?$",
            verdict_text,
        )
        verdict = verdict_match.group("keyword").casefold() if verdict_match else ""
        detail = (verdict_match.group("detail") or "").strip() if verdict_match else ""
        records.append(
            PostedReading(
                artifact=artifact,
                post_url=fields.get("POST-URL", ""),
                posted=fields.get("POSTED", ""),
                read=fields.get("READ", ""),
                verdict=verdict,
                verdict_detail=detail,
                missing_fields=tuple(
                    name for name in REREAD_FIELDS if not fields.get(name, "")
                ),
            )
        )
    return tuple(records)


def discussion_entry_id(url: str) -> str | None:
    """Return one Canvas discussion entry id, or ``None`` for an unlocated URL."""

    values = parse_qs(urlparse(url).query).get("entry_id", ())
    return values[0] if len(values) == 1 and values[0] else None


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
class CitationCoverage:
    candidates: int = 0
    evidenced: int = 0
    grammar: int = 0
    unread: int = 0
    disagreements: tuple[tuple[str, str], ...] = ()

    def report_line(self) -> str:
        return (
            "citation reader coverage: "
            f"candidates {self.candidates}; "
            f"evidence {self.evidenced}; "
            f"grammar {self.grammar}; "
            f"unread {self.unread}; "
            f"key disagreement {len(self.disagreements)}"
        )

    def disagreement_lines(self) -> tuple[str, ...]:
        return tuple(
            f"citation key disagreement: evidence {evidenced} | grammar {grammar}"
            for evidenced, grammar in self.disagreements
        )


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
    personal = re.fullmatch(
        r"\s*(?P<surname>[^,]+),\s*"
        r"(?:[" + UPPER + r"](?:[.\-])?(?:\s+|$))+\s*",
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
        name_text = author_text[: legal.start()].rstrip("., ")
        keys = [author_key(name_text)] if name_text else []
    elif surnames:
        keys = [author_key(surnames[0])]
        if len(surnames) > 1:
            keys.insert(0, author_key(" and ".join(surnames)))
    else:
        keys = [author_key(author_text)]
    years = [year.group("year").casefold()] if year is not None else [""]
    keyed: list[tuple[str, str]] = []
    for key in dict.fromkeys(keys):
        if not key:
            continue
        keyed.append((key, years[0]))
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


def citation_year(date_element: str) -> str:
    """The year that identifies the cited version of a republished work."""

    return date_element.rsplit("/", 1)[-1].casefold()


def _inside_code(body: str, start: int, end: int) -> bool:
    return any(
        start < match.end() and match.start() < end
        for pattern in (FENCED_CODE, INLINE_CODE)
        for match in pattern.finditer(body)
    )


def _valid_evidenced_author(body: str, author: str, start: int, end: int) -> bool:
    first_letter = next(
        (character for character in author if character.isalpha()),
        "",
    )
    return (
        len(author_key(author)) >= 3
        and "\n" not in author
        and re.search(r"(?<!v)(?<=[" + LOWER + r"’'])\.\s", author) is None
        and first_letter.isupper()
        and not _inside_code(body, start, end)
    )


def _evidenced_citations(
    body: str,
    reference_key_set: Collection[tuple[str, str]],
    legal_spans: frozenset[tuple[int, int]],
) -> tuple[Citation, ...]:
    """Read exact reference keys before allowing the fallback grammar to split."""

    if not reference_key_set:
        return ()
    max_key_length = max(len(key) for key, _year in reference_key_set)
    found: list[Citation] = []
    identities: set[tuple[int, int, str]] = set()

    for block in PAREN_BLOCK.finditer(body):
        offset = block.start("inside")
        cursor = 0
        for part in block.group("inside").split(";"):
            leading = len(part) - len(part.lstrip())
            stripped = part.strip()
            start = offset + cursor + leading
            end = start + len(stripped)
            if any(start < legal_end and legal_start < end for legal_start, legal_end in legal_spans):
                cursor += len(part) + 1
                continue
            for date_match in EVIDENCE_DATE_VALUE.finditer(stripped):
                author = stripped[: date_match.start()].rstrip(" ,")
                key = author_key(author)
                if (
                    len(key) <= max_key_length
                    and any(reference_key == key for reference_key, _ in reference_key_set)
                    and _valid_evidenced_author(body, author, start, end)
                ):
                    for remaining in EVIDENCE_DATE_VALUE.finditer(
                        stripped, date_match.start()
                    ):
                        token = citation_year(remaining.group("year"))
                        identity = (start, end, token)
                        if identity not in identities:
                            identities.add(identity)
                            found.append(Citation(author, token, start, end))
                    break
            cursor += len(part) + 1

    for block in PAREN_BLOCK.finditer(body):
        if DATE_SERIES.fullmatch(block.group("inside")) is None:
            continue
        prefix = body[: block.start()]
        longest: Citation | None = None
        year_values = tuple(
            citation_year(match.group("year"))
            for match in EVIDENCE_DATE_VALUE.finditer(block.group("inside"))
        )
        for word_start in _reverse_word_starts(prefix):
            author = prefix[word_start:].strip()
            key = author_key(author)
            if len(key) > max_key_length:
                break
            if not _valid_evidenced_author(body, author, word_start, block.end()):
                continue
            if any(reference_key == key for reference_key, _ in reference_key_set):
                longest = Citation(author, year_values[0], word_start, block.end())
                break
        if longest is not None:
            for year in year_values:
                identity = (longest.start, longest.end, year)
                if identity not in identities:
                    identities.add(identity)
                    found.append(
                        Citation(longest.author, year, longest.start, longest.end)
                    )
    return tuple(found)


def _read_citations(
    body: str,
    reference_key_set: Collection[tuple[str, str]] = (),
) -> tuple[tuple[Citation, ...], CitationCoverage]:
    """Read APA citations, including narrative names evidenced by references."""

    found: list[Citation] = []
    legal_citations = tuple(LEGAL_CITATION.finditer(body))
    legal_spans = legal_citation_spans(body)
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
        if any(
            start <= block.start() and block.end() <= end
            for start, end in (*definition_spans, *legal_spans)
        ):
            continue
        offset = block.start("inside")
        cursor = 0
        for part in block.group("inside").split(";"):
            leading = len(part) - len(part.lstrip())
            stripped = part.strip()
            start = offset + cursor + leading
            end = start + len(stripped)
            if any(
                start < legal_end and legal_start < end
                for legal_start, legal_end in legal_spans
            ):
                cursor += len(part) + 1
                continue
            match = REPUBLISHED_PAREN_PAIR.match(stripped) or PAREN_PAIR.match(stripped)
            if match:
                author = match.group("author")
                found.append(
                    Citation(author, citation_year(match.group("year")), start, end)
                )
                rest = match.groupdict().get("rest") or ""
                while True:
                    extra = ADDITIONAL_DATE.match(rest)
                    if extra is None:
                        break
                    found.append(
                        Citation(author, citation_year(extra.group("year")), start, end)
                    )
                    rest = rest[extra.end() :]
            cursor += len(part) + 1
    narrative_citations = sorted(
        (
            *REPUBLISHED_NARRATIVE_CITATION.finditer(body),
            *NARRATIVE_CITATION.finditer(body),
        ),
        key=lambda match: match.start(),
    )
    for match in narrative_citations:
        if any(
            start <= match.start() and match.end() <= end
            for start, end in (*definition_spans, *legal_spans)
        ):
            continue
        found.append(
            Citation(
                match.group("author"),
                citation_year(match.group("year")),
                match.start(),
                match.end(),
            )
        )
        rest = match.groupdict().get("rest") or ""
        while True:
            extra = ADDITIONAL_DATE.match(rest)
            if extra is None:
                break
            found.append(
                Citation(
                    match.group("author"),
                    citation_year(extra.group("year")),
                    match.start(),
                    match.end(),
                )
            )
            rest = rest[extra.end() :]
    grammar_found = tuple(found)
    evidence_found = _evidenced_citations(body, reference_key_set, legal_spans)
    evidence_spans = {(citation.start, citation.end) for citation in evidence_found}
    disagreements: list[tuple[str, str]] = []
    for evidence in evidence_found:
        evidence_key = author_key(evidence.author)
        for grammar_citation in grammar_found:
            if (
                grammar_citation.start < evidence.end
                and evidence.start < grammar_citation.end
                and grammar_citation.year == evidence.year
            ):
                grammar_key = author_key(grammar_citation.author)
                if grammar_key != evidence_key:
                    disagreements.append((evidence_key, grammar_key))
    grammar_remainder = tuple(
        citation
        for citation in grammar_found
        if not any(
            citation.start < end and start < citation.end
            for start, end in evidence_spans
        )
    )
    combined = tuple(
        sorted(
            (*grammar_remainder, *evidence_found),
            key=lambda citation: (citation.start, citation.end, citation.year),
        )
    )
    deduplicated = tuple(
        {
            (citation.start, citation.end, citation.author, citation.year): citation
            for citation in combined
        }.values()
    )
    covered_spans = tuple(
        (citation.start, citation.end)
        for citation in (*evidence_found, *grammar_remainder)
    )
    unread = 0
    for block in PAREN_BLOCK.finditer(body):
        offset = block.start("inside")
        cursor = 0
        for part in block.group("inside").split(";"):
            leading = len(part) - len(part.lstrip())
            stripped = part.strip()
            start = offset + cursor + leading
            end = start + len(stripped)
            if (
                not any(
                    start < legal_end and legal_start < end
                    for legal_start, legal_end in legal_spans
                )
                and not any(
                    start < covered_end and covered_start < end
                    for covered_start, covered_end in covered_spans
                )
            ):
                unread += len(tuple(EVIDENCE_DATE_VALUE.finditer(stripped)))
            cursor += len(part) + 1
    coverage = CitationCoverage(
        candidates=len(evidence_found) + len(grammar_remainder) + unread,
        evidenced=len(evidence_found),
        grammar=len(grammar_remainder),
        unread=unread,
        disagreements=tuple(dict.fromkeys(disagreements)),
    )
    return deduplicated, coverage


def read_citations(
    body: str,
    reference_key_set: Collection[tuple[str, str]] = (),
) -> tuple[Citation, ...]:
    return _read_citations(body, reference_key_set)[0]


def citation_coverage(
    body: str,
    reference_key_set: Collection[tuple[str, str]] = (),
) -> CitationCoverage:
    return _read_citations(body, reference_key_set)[1]


def legal_citation_spans(body: str) -> frozenset[tuple[int, int]]:
    """Return spans already consumed by the shared legal-citation reader."""

    return frozenset(
        (match.start(), match.end()) for match in LEGAL_CITATION.finditer(body)
    )


def _without_signal_word(author: str) -> str:
    return re.sub(r"^(?:As|In|By|See)\s+", "", author).strip()


def _legal_author(match: re.Match[str]) -> str:
    return (
        match.group("parenthesized_author")
        or match.group("continued_author")
        or match.group("author")
    )


def _legal_year(match: re.Match[str]) -> str:
    value = (
        match.group("parenthesized_year")
        or match.group("continued_year")
        or match.group("year")
        or ""
    )
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
