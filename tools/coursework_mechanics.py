"""Shared APA body mechanics, with closed evidence lists and keyed uncertain hits.

Read provenance: reference/coursework-mechanics-read-20261012.md. Only the
recognizers below establish a hit; the record establishes handling shape, not truth.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, replace
from pathlib import Path

import completion_checks
import coursework_style
import docx_write
import discussion_artifact
import reference_alphabets
import run_grader
import spelling_scan
from run_record_reader import read_handwritten_record, DamagedRecord, damaged_record_result


ABBREVIATION_EXEMPTIONS = frozenset((
    # APA 6.25 dictionary terms and 6.44 statistical symbols; ADR 0359 house set.
    "AIDS", "HIV", "IQ", "HEENT", "T", "HR", "RR", "BP", "SpO2",
    "N", "M", "SD", "SE", "SEM", "CI", "ES", "OR", "SS", "MS", "F", "R",
    # Read by the variant row instead of imposing a first-use definition.
    "US", "U.S.",
))
# A required form has Manual provenance on its own row. The bounded 6.2 read
# does not establish a noun-use rule, so the country row uses consistency only.
VARIANTS = (
    (("US", "U.S."), None, "APA 6.2, p. 153; ADR 0359 ruling 5", 0),
    (("healthcare", "health care", "health-care"), "health care", "APA 6.12, p. 161", re.I),
)
CLOSED_PREFIXES = {
    "pre-operative": "preoperative",
    "post-operative": "postoperative",
    "non-adherence": "nonadherence",
}
DICTIONARY_HYPHENATED = frozenset(("anti-inflammatory", "co-occur", "meta-analysis"))
PREFIXES = frozenset((
    # APA Table 6.2, p. 162: suffix-only entries are not prefixes.
    "after", "anti", "bi", "co", "cyber", "equi", "extra", "infra", "inter",
    "macro", "mega", "meta", "micro", "mid", "mini", "multi", "non", "over",
    "post", "pre", "pro", "pseudo", "quasi", "re", "semi", "socio", "sub",
    "super", "supra", "un", "under",
))
MEANING_EXCEPTIONS = frozenset(("re-pair", "re-form", "un-ionized"))  # APA Table 6.3, p. 164.
COUNT_NOUNS = frozenset(("patients", "participants", "studies", "visits", "factors", "criteria"))
NUMBER_WORDS = frozenset((
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
    "billion", "trillion",
))
NUMERIC_EXCEPTIONS = frozenset((
    "measurement", "statistic", "percentage", "ratio", "date", "age", "time",
    "score", "money", "series position",
))
UNITS = frozenset((
    "mg", "g", "kg", "mcg", "ml", "l", "mm", "cm", "m", "km", "lb", "lbs",
    "oz", "mmhg", "bpm", "hr", "hrs", "min", "mins", "s", "sec", "seconds",
    "minutes", "hours", "days", "weeks", "months", "years", "day", "week",
    "month", "year", "hour", "minute", "second",
))
ROWS = (
    "undefined-abbreviation", "spelling-variant", "closed-prefix",
    "uncertain-prefix", "small-count", "uncertain-digit", "large-number-word",
    "numeral-opening", "british-body-form", "mechanics-record", "mechanics-language",
)
CITATION_ABBREVIATIONS = ("p", "pp", "para", "paras", "ca")
# Only the plural page and paragraph forms introduce a list or range of locators.
CITATION_SPAN_ABBREVIATIONS = ("pp", "paras")
_CITATION_LIST = ", ".join(f"{word}." for word in CITATION_ABBREVIATIONS[:-1]) + f", and {CITATION_ABBREVIATIONS[-1]}."
DECLARED_LIMITS = (
    "Lowercase and mixed-case abbreviations are not recognized.",
    "Mixed terms and count nouns outside the committed lists have no dedicated list row; bare small digits still require handling.",
    "The truth of a recorded dictionary entry, APA exception, or changed disposition is not graded.",
    "The country variant row grades consistency; a noun-use directive was not established by the bounded Manual read.",
    f"Sentence boundaries follow punctuation; the lowercase APA citation abbreviations {_CITATION_LIST} and the lists and ranges after pp. and paras. are not boundaries for any opening or digit row, but a period inside any other abbreviation can produce an opening candidate.",
    "Only reference titles parsed from an italic span or the title immediately after the reference date are excluded as cited titles.",
    "A group author is recognized from the reference author field without personal-name initials; ambiguous author grammar remains outside this read.",
    "Word surfaces inherit coursework_style's projection limits.",
    "Damaged handwritten handling records withhold handling-dependent uncertain-hit checks; independent artifact mechanics still grade. Historical approval protection applies per artifact.",
)
RECORD_NAME = "coursework-mechanics.json"
ABBREVIATION = re.compile(r"(?<!\w)(?:[A-Z]\.){2,}|\b[A-Z]{2,}\b")
PREFIX = re.compile(r"\b([A-Za-z]+)-([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\b")
SMALL_DIGIT = re.compile(r"(?<!\w)([0-9])(?!\w)")
LARGE_WORD = re.compile(r"\b(?:" + "|".join(sorted(NUMBER_WORDS)) + r")\b", re.I)
DATE = re.compile(r"\b(?:\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}/\d{2,4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?)\b", re.I)
QUOTATION = re.compile(r'"[^"\n]*"|“[^”]*”|(?<!\w)‘[^’]*’(?!\w)|(?<!\w)\x27[^\x27\n]*\x27(?!\w)')
def _abbreviation_pattern(words: tuple[str, ...]) -> str:
    return r"(?<![A-Za-z])(?:" + "|".join(map(re.escape, words)) + r")\."


CITATION_ABBREVIATION = re.compile(_abbreviation_pattern(CITATION_ABBREVIATIONS) + r"$")
CITATION_CONTINUATION = re.compile(
    _abbreviation_pattern(CITATION_SPAN_ABBREVIATIONS)
    + r"\s*\d+(?:\s*[–-]\s*\d+)?(?:\s*,\s*\d+(?:\s*[–-]\s*\d+)?)*\s*[–,-]\s*$"
)


@dataclass(frozen=True)
class Finding:
    kind: str
    artifact: str
    line: int = 0
    column: int = 0
    hit: str = ""


@dataclass(frozen=True)
class Scan:
    language: str
    artifact: str
    findings: tuple[Finding, ...]
    surface_sha256: str = ""


def digest(markdown: str) -> str:
    return hashlib.sha256(markdown.encode("utf-8")).hexdigest()


def hit_id(kind: str, line: int, column: int, token: str) -> str:
    return f"{kind}:{line}:{column}:{digest(token)}"


def _mask(text: str, pattern: re.Pattern[str]) -> str:
    return pattern.sub(lambda match: " " * len(match[0]), text)


def _references(markdown: str) -> tuple[str, tuple[str, ...]]:
    return discussion_artifact.split_references(
        markdown, re.compile(r"(?im)^[ \t]*(?:#+[ \t]+)?(?:\*\*)?References(?:\*\*)?[ \t]*$")
    )


def _exclusions(markdown: str) -> tuple[str, tuple[str, ...]]:
    body, references = _references(markdown)
    titles: list[str] = []
    groups: list[str] = []
    for reference in references:
        author = re.match(r"(.+?)\s*\((?:\d{4}|n\.d\.)[^)]*\)\.\s*(.*)", reference)
        if not author:
            continue
        name = author[1].strip().rstrip(".")
        if not re.search(r",\s*[A-Z]\.", name):
            groups.append(name)
        italic = re.match(r"(?:\*|_)([^*_]+)(?:\*|_)", author[2])
        title = italic[1] if italic else re.split(r"(?<!\b[A-Z])[.?!](?:\s|$)", author[2], maxsplit=1)[0]
        if title:
            titles.append(title)
    body = _mask(body, QUOTATION)
    for title in sorted(titles, key=len, reverse=True):
        body = _mask(body, re.compile(r"(?<!\w)" + re.escape(title) + r"(?!\w)", re.I))
    return body, tuple(groups)


def _unmarked(text: str) -> str:
    return re.sub(r"[*_`]", "", text)


def _cited(before: str) -> bool:
    # APA page, paragraph, and circa abbreviations end in a period that ends no sentence.
    return bool(CITATION_ABBREVIATION.search(before) or CITATION_CONTINUATION.search(before))


def _opening(text: str, start: int) -> bool:
    before = _unmarked(text[:start]).rstrip()
    if _cited(before):
        return False
    return not before or before[-1] in ".!?"


def _numeric_exclusion(text: str, match: re.Match[str]) -> bool:
    after = text[match.end():]
    before = _unmarked(text[:match.start()])
    following = re.match(r"\s*-?\s*([A-Za-z]+)", after)
    return bool(
        re.match(r"\s*[%°]", after)
        or re.match(r"\.\d", after) or re.search(r"\d\.$", before)
        or (following and following[1].casefold() in UNITS)
        or re.search(r"\b(?:Table|Figure|Step|Stage|Grade|Chapter|Module|Item|Section)\s+$", before, re.I)
        or re.search(r"\bBook\s+$", before)
        or _cited(before.rstrip())
        or any(date.start() <= match.start() < date.end() for date in DATE.finditer(text))
        or re.search(r"[$€£]\s*$", before)
    )


def _handling_valid(kind: str, entry) -> bool:
    if not isinstance(entry, dict):
        return False
    if entry.get("action") == "changed":
        return True
    if entry.get("action") != "retained":
        return False
    if kind == "uncertain-prefix":
        return bool(re.fullmatch(r"https://(?:www\.)?merriam-webster\.com/dictionary/[^\s]+", str(entry.get("entry", ""))))
    return kind == "uncertain-digit" and entry.get("exception") in NUMERIC_EXCEPTIONS


def survey(markdown: str, artifact: str, language: str, handling: dict | None = None) -> Scan:
    if language != "en":
        return Scan(language, artifact, ())
    body, groups = _exclusions(markdown)
    findings: list[Finding] = []
    definitions: set[str] = set(ABBREVIATION_EXEMPTIONS)
    seen_variants: list[set[str]] = [set() for _ in VARIANTS]
    handling = handling or {}

    def add(kind: str, line: int, column: int = 0, token: str = "") -> None:
        findings.append(Finding(kind, artifact, line, column, hit_id(kind, line, column, token)))

    def uncertain(kind: str, block, match) -> None:
        key = hit_id(kind, block.line, match.start() + 1, match[0])
        entry = handling.get(key)
        if not _handling_valid(kind, entry):
            add(kind, block.line, match.start() + 1, match[0])

    for block in docx_write.blocks(body):
        if block.kind in {"blank", "separator", "block-quotation"}:
            continue
        text = block.text if block.kind != "table" else block.source
        # Every row excludes quotations and cited titles. Only variants exempt
        # names of the paper's own cited group authors.
        variants_text = text
        for group in groups:
            variants_text = _mask(variants_text, re.compile(r"(?<!\w)" + re.escape(group) + r"(?!\w)", re.I))
        for index, (forms, required, _source, flags) in enumerate(VARIANTS):
            for form in forms:
                if re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", variants_text, flags):
                    seen_variants[index].add(form)
                    if required is not None and form != required:
                        add("spelling-variant", block.line)
        for match in ABBREVIATION.finditer(text):
            token = match[0]
            if token in definitions:
                continue
            prefix = text[:match.start()]
            # Full term followed by (ABC), or [ABC] inside a parenthesis.
            expanded = re.search(r"([A-Za-z][A-Za-z /-]+)\s*[\[(]\s*$", prefix)
            initials = "".join(word[0].upper() for word in re.findall(r"[A-Za-z]+", expanded[1])) if expanded else ""
            if expanded and initials.endswith(token.replace(".", "")):
                definitions.add(token)
            else:
                add("undefined-abbreviation", block.line, match.start() + 1, token)
        for match in PREFIX.finditer(text):
            token = match[0].casefold()
            prefix, base = match[1].casefold(), match[2]
            if token in CLOSED_PREFIXES:
                add("closed-prefix", block.line, match.start() + 1, token)
            elif prefix in PREFIXES and token not in DICTIONARY_HYPHENATED:
                structural = (
                    base[0].isupper() or base[0].isdigit() or "-" in base
                    or token in MEANING_EXCEPTIONS
                    or (prefix[-1] == base[0].casefold() and prefix[-1] in "aio")
                )
                if not structural:
                    uncertain("uncertain-prefix", block, match)
        for match in SMALL_DIGIT.finditer(text):
            following = re.match(r"\s+([A-Za-z]+)\b", text[match.end():])
            if following and following[1].casefold() in COUNT_NOUNS:
                add("small-count", block.line, match.start() + 1, match[0])
            elif not _numeric_exclusion(text, match):
                uncertain("uncertain-digit", block, match)
        for match in LARGE_WORD.finditer(text):
            initial_number_phrase = re.fullmatch(r"(?:one|two|three|four|five|six|seven|eight|nine)(?:[ -])", text[:match.start()].casefold())
            if not _opening(text, match.start()) and not initial_number_phrase:
                add("large-number-word", block.line, match.start() + 1, match[0])
        for match in re.finditer(r"\b\d+(?:\.\d+)?\b", text):
            if _opening(text, match.start()):
                add("numeral-opening", block.line, match.start() + 1, match[0])
        for spelling in spelling_scan.scan_text(text, artifact):
            if spelling.form in spelling_scan.TABLE:
                add("british-body-form", block.line + spelling.line - 1, 0, spelling.form)
    for forms in seen_variants:
        if len(forms) > 1:
            add("spelling-variant", 0)
    return Scan(language, artifact, tuple(findings), digest(markdown))


def _read_handling(root: Path, artifact: str | None = None) -> tuple[dict, str | None, bool]:
    path = root / RECORD_NAME
    if not path.exists():
        return {}, None, False
    try:
        record = read_handwritten_record(path, "json").require_json(artifact=artifact)
    except (OSError, UnicodeError) as failure:
        return {}, f"mechanics record unread: {failure}", True
    except ValueError:
        return {}, "mechanics record is not JSON", False
    if not isinstance(record, dict) or not isinstance(record.get("artifacts"), list):
        return {}, "mechanics record requires an artifacts array", False
    result = {}
    for entry in record["artifacts"]:
        if (not isinstance(entry, dict) or not isinstance(entry.get("artifact"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", "")))
                or not isinstance(entry.get("hits"), dict) or entry["artifact"] in result):
            return {}, "mechanics artifact record is malformed or duplicated", False
        for key, handling in entry["hits"].items():
            if (not re.fullmatch(r"uncertain-(?:prefix|digit):\d+:\d+:[0-9a-f]{64}", key)
                    or not isinstance(handling, dict)
                    or handling.get("action") not in {"changed", "retained"}):
                return {}, "mechanics hit record has an invalid identity or action", False
            if not _handling_valid(key.partition(":")[0], handling):
                return {}, "mechanics retained hit requires its dictionary entry or closed APA exception", False
        result[entry["artifact"]] = entry
    return result, None, False


def format_report(scan: Scan, show: bool = False, *, handling_damaged: bool = False) -> str:
    lines = [f"coursework mechanics ({scan.artifact}; language {scan.language})"]
    for row in ROWS:
        outcome = str(sum(finding.kind == row for finding in scan.findings)) if scan.language == "en" else f"not graded - language {scan.language}"
        if handling_damaged and row in {"uncertain-prefix", "uncertain-digit"}:
            outcome = "not graded — damaged text"
        lines.append(f"{row}: {outcome}")
    if show:
        lines.append("SURFACE-SHA256: " + scan.surface_sha256)
        lines.extend(f"  {finding.kind}: line {finding.line}, column {finding.column}; HIT {finding.hit}" for finding in scan.findings)
    return "\n".join(lines)


def apply_grade(grade, root: Path, surfaces: tuple[tuple[str, str], ...], parsed, *, language: str | None = None, coverage_limb: str | None = None):
    if not completion_checks.active("coursework_mechanics:mechanics-language"):
        return replace(grade, reports=(*grade.reports, "coursework mechanics: not graded - predates check start"))
    if language is None:
        language = reference_alphabets.paper_language(
            parsed.value("--paper-language"),
            Path(parsed.value("--profile")) if parsed.value("--profile") else None,
        )
    language = reference_alphabets.language_name(language)
    reports = list(grade.reports)
    failed = False
    any_unread = False
    for name, markdown in surfaces:
        damaged = False
        try:
            records, error, unread = _read_handling(root, name) if language == "en" else ({}, None, False)
        except DamagedRecord as failure:
            damage_finding, report = damaged_record_result(failure, check="coursework mechanics handling", artifact=name)
            reports.append(report)
            failed |= damage_finding
            records, error, unread, damaged = {}, None, False, True
        failed |= bool(error) and not unread
        any_unread |= unread
        record = records.get(name)
        stale = record is not None and record["sha256"] != digest(markdown)
        scan = survey(markdown, name, language, record["hits"] if record and not stale else None)
        findings = completion_checks.filter_findings("coursework_mechanics", scan.findings)
        if damaged:
            findings = tuple(finding for finding in findings if not finding.kind.startswith("uncertain-"))
        if stale:
            findings = (*findings, Finding("mechanics-record", name))
        if error and not unread:
            findings = (*findings, Finding("mechanics-record", name))
        scan = replace(scan, findings=findings)
        failed = failed or bool(findings)
        reports.append(format_report(scan, parsed.show, handling_damaged=damaged))
        if error:
            reports.append(error)
    reports.extend("mechanics limit: " + limit for limit in DECLARED_LIMITS)
    return replace(grade, findings_failed=grade.findings_failed or failed,
                   coverage_failed=grade.coverage_failed or language != "en" or any_unread,
                   coverage_limbs=(*grade.coverage_limbs, *((coverage_limb,) if coverage_limb and (language != "en" or any_unread) else ())),
                   reports=tuple(reports))


word_surface = coursework_style.docx_mechanics_markdown
