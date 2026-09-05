"""Grade committed ``reference/uptodate/`` topic sheets against their dump.

    python tools/uptodate_sheet.py <sheet.md> [<sheet.md> ...]
    python tools/uptodate_sheet.py --all [--quiet]

This is a local staged-sheet refuser.  The raw source and its manifest live in
``scratch/uptodate/`` and never enter CI.  Exit 0 is clean, exit 1 means a
malformed sheet, and exit 2 means no source was available to grade it.

``DECLARED_LIMITS`` is the complete coverage boundary.  The cap counts exact
runs of at least five source words and refuses when those runs exceed either
10 percent of the restatement or 60 words.  Both limits are deliberate: the
share scales with a normal sheet while the absolute ceiling prevents a long
sheet from buying more quotation.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from console_codec import use_utf8
import uptodate_store

REQUIRED_FIELDS = (
    "AUTHORS",
    "TITLE",
    "APA-YEAR",
    "LITERATURE-REVIEW-CURRENT-THROUGH",
    "RETRIEVED",
    "URL",
    "DUMP-ID",
    "DISTILLATION-BASIS",
    "FAITHFULNESS-READING",
)
FIELD = re.compile(r"(?m)^(?P<name>[A-Z][A-Z-]+):\s*(?P<value>\S.*)\s*$")
RESTATEMENT = re.compile(r"(?im)^##\s+Restatement\s*$")
TITLE_HEADING = re.compile(r"(?m)^#\s+(?P<title>\S.*)\s*$")
WORD = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")

BODY_WORD_MINIMUM = 400
BODY_WORD_MAXIMUM = 550
VERBATIM_SEQUENCE_MINIMUM = 5
VERBATIM_WORD_MAXIMUM = 60
VERBATIM_SHARE_MAXIMUM = 0.10

MISSING_FIELD = "missing-field"
DUPLICATE_FIELD = "duplicate-field"
HEADING_TITLE_MISMATCH = "heading-title-mismatch"
UNKNOWN_DUMP = "unknown-dump"
TITLE_NOT_IN_DUMP = "title-not-in-dump"
AUTHORS_MISMATCH = "authors-mismatch"
APA_YEAR_MISMATCH = "apa-year-mismatch"
CURRENCY_MISMATCH = "currency-mismatch"
RETRIEVAL_BEFORE_DUMP = "retrieval-before-dump"
BAD_URL = "bad-url"
DISTILLATION_BASIS_MISMATCH = "distillation-basis-mismatch"
FAITHFULNESS_READING_MISMATCH = "faithfulness-reading-mismatch"
BODY_WORD_COUNT = "body-word-count"
VERBATIM_CAP_EXCEEDED = "verbatim-cap-exceeded"

DECLARED_LIMITS = {
    "faithfulness-reader-owned": "A completed reading field cannot prove that the restatement is faithful to the source.",
    "short-verbatim-runs-unseen": "Exact source runs shorter than five words are not counted as verbatim.",
    "common-language-overcounted": "A five-word run independently written by the author is counted when it also occurs in the source.",
}
NOT_REACHED = tuple(DECLARED_LIMITS.values())


@dataclass(frozen=True)
class Finding:
    kind: str
    detail: str


@dataclass(frozen=True)
class Scan:
    title: str
    body_words: int
    verbatim_words: int
    findings: tuple[Finding, ...]


class SourceError(ValueError):
    pass


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _words(value: str) -> list[str]:
    return [match.group(0).casefold().replace("’", "'") for match in WORD.finditer(value)]


def _verbatim_words(restatement: str, source: str) -> int:
    target = _words(restatement)
    source_words = _words(source)
    width = VERBATIM_SEQUENCE_MINIMUM
    starts: dict[tuple[str, ...], list[int]] = {}
    for index in range(0, len(source_words) - width + 1):
        starts.setdefault(tuple(source_words[index : index + width]), []).append(index)
    covered: set[int] = set()
    for index in range(0, len(target) - width + 1):
        candidates = starts.get(tuple(target[index : index + width]), ())
        longest = 0
        for source_index in candidates:
            length = width
            while (
                index + length < len(target)
                and source_index + length < len(source_words)
                and target[index + length] == source_words[source_index + length]
            ):
                length += 1
            longest = max(longest, length)
        if longest:
            covered.update(range(index, index + longest))
    return len(covered)


def _fields(text: str) -> dict[str, str]:
    return {match.group("name"): match.group("value").strip() for match in FIELD.finditer(text)}


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    host = (parsed.hostname or "").casefold()
    return (
        parsed.scheme == "https"
        and (host == "uptodate.com" or host.endswith(".uptodate.com"))
        and parsed.path.startswith("/contents/")
        and len(parsed.path) > len("/contents/")
    )


def grade_text(text: str, store: Path | None = None) -> Scan:
    fields = _fields(text)
    findings = [Finding(MISSING_FIELD, name) for name in REQUIRED_FIELDS if not fields.get(name)]
    matches = tuple(FIELD.finditer(text))
    findings.extend(
        Finding(DUPLICATE_FIELD, name)
        for name in REQUIRED_FIELDS
        if sum(match.group("name") == name for match in matches) > 1
    )
    heading = TITLE_HEADING.search(text)
    if heading is None:
        findings.append(Finding(MISSING_FIELD, "# topic heading"))
    elif fields.get("TITLE") and _normalize(heading.group("title")) != _normalize(fields["TITLE"]):
        findings.append(Finding(HEADING_TITLE_MISMATCH, heading.group("title")))
    marker = RESTATEMENT.search(text)
    if marker is None:
        findings.append(Finding(MISSING_FIELD, "## Restatement"))
        body = ""
    else:
        body = text[marker.end() :].strip()
    body_words = len(_words(body))
    if not BODY_WORD_MINIMUM <= body_words <= BODY_WORD_MAXIMUM:
        findings.append(
            Finding(BODY_WORD_COUNT, f"{body_words}; expected {BODY_WORD_MINIMUM}-{BODY_WORD_MAXIMUM}")
        )
    if findings and any(row.kind == MISSING_FIELD for row in findings):
        return Scan(fields.get("TITLE", "unknown topic"), body_words, 0, tuple(findings))

    dump_id = fields["DUMP-ID"]
    manifest = uptodate_store.manifest_for_dump(dump_id, store)
    if manifest is None:
        raise SourceError(f"no manifest for dump {dump_id}")
    source_topic = uptodate_store.source_topic(dump_id, fields["TITLE"], store)
    if source_topic is None:
        findings.append(Finding(TITLE_NOT_IN_DUMP, fields["TITLE"]))
        return Scan(fields["TITLE"], body_words, 0, tuple(findings))

    if _normalize(fields["AUTHORS"]) != _normalize(source_topic.authors):
        findings.append(Finding(AUTHORS_MISMATCH, fields["AUTHORS"]))
    source_updated = date.fromisoformat(source_topic.last_updated)
    if fields["APA-YEAR"] != str(source_updated.year):
        findings.append(Finding(APA_YEAR_MISMATCH, fields["APA-YEAR"]))
    if fields["LITERATURE-REVIEW-CURRENT-THROUGH"] != source_topic.literature_review_current_through:
        findings.append(Finding(CURRENCY_MISMATCH, fields["LITERATURE-REVIEW-CURRENT-THROUGH"]))
    try:
        retrieved = date.fromisoformat(fields["RETRIEVED"])
        received = date.fromisoformat(str(manifest["received_on"]))
        if retrieved < received:
            findings.append(Finding(RETRIEVAL_BEFORE_DUMP, fields["RETRIEVED"]))
    except (ValueError, TypeError):
        findings.append(Finding(RETRIEVAL_BEFORE_DUMP, fields["RETRIEVED"]))
    if not _valid_url(fields["URL"]):
        findings.append(Finding(BAD_URL, fields["URL"]))

    expected_basis = "summary and recommendations" if source_topic.has_summary else "whole article"
    if _normalize(fields["DISTILLATION-BASIS"]) != expected_basis:
        findings.append(Finding(DISTILLATION_BASIS_MISMATCH, fields["DISTILLATION-BASIS"]))
    expected_reading = f"completed against the {expected_basis}"
    if _normalize(fields["FAITHFULNESS-READING"]) != expected_reading:
        findings.append(Finding(FAITHFULNESS_READING_MISMATCH, fields["FAITHFULNESS-READING"]))

    verbatim = _verbatim_words(body, source_topic.body)
    if verbatim > VERBATIM_WORD_MAXIMUM or (
        body_words and verbatim / body_words > VERBATIM_SHARE_MAXIMUM
    ):
        findings.append(
            Finding(VERBATIM_CAP_EXCEEDED, f"{verbatim} of {body_words} words")
        )
    return Scan(fields["TITLE"], body_words, verbatim, tuple(findings))


def grade_path(path: Path, store: Path | None = None) -> Scan:
    if not path.is_file():
        raise SourceError(f"no topic sheet named {path.name}")
    return grade_text(path.read_text(encoding="utf-8", errors="replace"), store)


def _paths(all_sheets: bool, paths: list[Path]) -> list[Path]:
    if all_sheets:
        root = Path(__file__).resolve().parent.parent / "reference" / "uptodate"
        return sorted(path for path in root.glob("*.md") if path.name != "README.md")
    return paths


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--store", type=Path, default=uptodate_store.default_store())
    args = parser.parse_args(argv)
    paths = _paths(args.all, args.paths)
    if not paths:
        print("uptodate-sheet: no topic sheet was selected", file=sys.stderr)
        return 2
    try:
        scans = [(path, grade_path(path, args.store)) for path in paths]
    except (OSError, UnicodeError, ValueError, SourceError) as error:
        print(f"uptodate-sheet: not graded - {error}", file=sys.stderr)
        return 2
    findings = [(path, row) for path, scan in scans for row in scan.findings]
    if findings:
        for path, finding in findings:
            print(f"{path.name}: {finding.kind}: {finding.detail}", file=sys.stderr)
        return 1
    if not args.quiet:
        for path, scan in scans:
            print(
                f"{path.name}: clean - {scan.body_words} body words; "
                f"{scan.verbatim_words} counted verbatim words"
            )
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
