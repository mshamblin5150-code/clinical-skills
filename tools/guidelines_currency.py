"""Audit and refresh the guideline edition-currency registry.

    python tools/guidelines_currency.py
    python tools/guidelines_currency.py --read USPSTF --read IDSA
    python tools/guidelines_currency.py --read AHA-ACC --capture AHA-ACC=page.html
    python tools/guidelines_currency.py --fetch-replacement URL --filename SOCIETY/file.pdf ...

The ordinary command is an offline, two-way bind between the catalog and
``reference/guidelines-currency.md``.  ``--read`` and ``--fetch-replacement`` are
the deliberately requested network operations from ADR 0134; neither runs from a
hook.  A currency finding is report-only.  Damage to the registry is a refusal.

Exit 0 means the registry was graded and is structurally clean, even when one or
more documents are superseded or an annual observation is old.  Exit 1 means the
offline grader found registry damage.  Exit 2 means the requested grading or read
did not run.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse

import guidelines_catalog
from console_codec import use_utf8
from repo_root import ensure_outside_checkout


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
DEFAULT_REGISTRY = REPO_ROOT / "reference" / "guidelines-currency.md"
DEFAULT_COVERAGE = REPO_ROOT / "reference" / "thresholds" / "coverage.md"
DEFAULT_AUDIT = REPO_ROOT / "reference" / "guidelines-catalog-audit.md"
SCHEMA_MARKER = "<!-- schema: guidelines-currency/1 -->"
SOCIETY_COLUMNS = (
    "society",
    "index",
    "reader",
    "join key",
    "access",
    "last observed",
    "state",
    "state observed",
)
DOCUMENT_COLUMNS = (
    "filename",
    "society",
    "join value",
    "verdict",
    "observed",
    "superseded by",
)
VERDICTS = ("current", "superseded", "absent", "unjoinable")
SOCIETY_STATES = ("read", "unread")
ANNUAL_SOCIETIES = frozenset({"ADA", "GINA", "GOLD"})
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# The route, access shape and join are ADR 0134's nine measured society reads.
# ``coverage`` is the denominator the reader counts, not a promise that a partial
# page represents the whole index.
SOCIETY_INDEXES = {
    "USPSTF": ("https://www.uspreventiveservicestaskforce.org/uspstf/topic_search_results?topic_status=P", "uspstf", "DOI", "plain"),
    "IDSA": ("https://www.idsociety.org/practice-guideline/alphabetical-guidelines/", "idsa", "DOI", "plain"),
    "KDIGO": ("https://kdigo.org/guidelines/", "kdigo", "DOI", "plain"),
    "AHA ACC": ("https://professional.heart.org/en/guidelines-statements-search", "aha-acc", "DOI", "agent"),
    "ADA": ("https://professional.diabetes.org/standards-of-care", "ada", "10.2337/dcYY-srev", "plain"),
    "GOLD": ("https://goldcopd.org/", "gold", "year slug", "agent"),
    "GINA": ("https://ginasthma.org/", "gina", "year slug", "plain"),
    "ACIP": ("https://www.cdc.gov/vaccines/imz-schedules/", "acip", "printed schedule date", "plain"),
    "CDC": ("https://www.cdc.gov/mmwr/", "cdc", "per-edition", "plain"),
}
SOCIETY_COVERAGE = {
    "USPSTF": "recommendation entries exposed by topic search for topic_status=P",
    "IDSA": "current, archived, and endorsed entries on the alphabetical index",
    "KDIGO": "guideline topic entries exposed by the guidelines index",
    "AHA ACC": "guideline and statement result cards returned by the Coveo search",
    "ADA": "Standards of Care edition entries exposed by the publisher page",
    "GOLD": "report and pocket-guide entries reached from the site navigation",
    "GINA": "report entries exposed by the WordPress API, sitemap, or feed capture",
    "ACIP": "schedule entries exposed by the immunization-schedules index",
    "CDC": "guideline editions exposed by the MMWR recommendations indexes",
}

DECLARED_LIMITS = (
    (
        "publisher completeness",
        "An index reader counts the guideline-shaped entries visible in the supplied "
        "response; it cannot establish that a publisher omitted hidden or paginated entries.",
    ),
    (
        "agent capture provenance",
        "A supplied agent capture establishes only the bytes this command read, not which "
        "browser identity or authorization produced them.",
    ),
    (
        "download identity",
        "A recorded SHA-256 proves which bytes were received, not that they are the right "
        "replacement or that a clinical re-read has occurred.",
    ),
)


@dataclass(frozen=True)
class SocietyEntry:
    society: str
    index: str
    reader: str
    join_key: str
    access: str
    last_observed: str
    state: str
    state_observed: str
    line: int


@dataclass(frozen=True)
class DocumentEntry:
    filename: str
    society: str
    join_value: str
    verdict: str
    observed: str
    superseded_by: str
    line: int


@dataclass(frozen=True)
class Registry:
    societies: tuple[SocietyEntry, ...]
    documents: tuple[DocumentEntry, ...]
    problems: tuple[str, ...]


@dataclass(frozen=True)
class AuditResult:
    failures: tuple[str, ...]
    findings: tuple[str, ...]
    society_count: int
    document_count: int
    never_checked: int
    oldest_observation: date | None


@dataclass(frozen=True)
class ReaderResult:
    society: str
    denominator: int
    join_values: tuple[str, ...]
    unread: int


@dataclass(frozen=True)
class IndexComparison:
    corpus_absent: tuple[str, ...]
    publisher_additions: tuple[str, ...]


@dataclass(frozen=True)
class FetchRecord:
    url: str
    filename: str
    sha256: str
    bytes: int
    fetched: str


class ReadError(RuntimeError):
    """The society index could not be read as a complete, countable surface."""


def _cells(line: str) -> list[str] | None:
    if not line.strip().startswith("|") or not line.strip().endswith("|"):
        return None
    return [html.unescape(cell.strip()) for cell in line.strip().strip("|").split("|")]


def _is_rule(cells: list[str]) -> bool:
    return bool(cells) and all(cell and set(cell) <= set("-: ") for cell in cells)


def parse_registry(text: str) -> Registry:
    """Parse both registry tables without guessing around a malformed row."""

    problems: list[str] = []
    if SCHEMA_MARKER not in text:
        problems.append(f"registry has no {SCHEMA_MARKER} marker")
    section = ""
    columns: tuple[str, ...] | None = None
    societies: list[SocietyEntry] = []
    documents: list[DocumentEntry] = []
    seen_sections: set[str] = set()
    for number, line in enumerate(text.splitlines(), start=1):
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            section = heading.group(1).casefold()
            columns = None
            continue
        cells = _cells(line)
        if cells is None or _is_rule(cells):
            continue
        expected: tuple[str, ...] | None = None
        if section == "society indexes":
            expected = SOCIETY_COLUMNS
        elif section == "documents":
            expected = DOCUMENT_COLUMNS
        if expected is None:
            continue
        if columns is None:
            if tuple(cell.casefold() for cell in cells) != expected:
                problems.append(
                    f"line {number}: unreadable {section!r} header; expected "
                    + " | ".join(expected)
                )
                section = ""
                continue
            columns = expected
            seen_sections.add(section)
            continue
        if len(cells) != len(expected):
            problems.append(
                f"line {number}: malformed {section!r} row has {len(cells)} cells, "
                f"expected {len(expected)}"
            )
            continue
        named = dict(zip(expected, cells, strict=True))
        if section == "society indexes":
            societies.append(
                SocietyEntry(
                    society=named["society"],
                    index=named["index"],
                    reader=named["reader"],
                    join_key=named["join key"],
                    access=named["access"].casefold(),
                    last_observed=named["last observed"],
                    state=named["state"].casefold(),
                    state_observed=named["state observed"],
                    line=number,
                )
            )
        else:
            documents.append(
                DocumentEntry(
                    filename=named["filename"],
                    society=named["society"],
                    join_value=named["join value"],
                    verdict=named["verdict"].casefold(),
                    observed=named["observed"],
                    superseded_by=named["superseded by"],
                    line=number,
                )
            )
    for wanted in ("society indexes", "documents"):
        if wanted not in seen_sections:
            problems.append(f"registry has no readable '## {wanted.title()}' table")
    return Registry(tuple(societies), tuple(documents), tuple(problems))


def _parsed_date(value: str, where: str, failures: list[str]) -> date | None:
    if not value:
        return None
    if DATE_RE.fullmatch(value) is None:
        failures.append(f"{where} has invalid date {value!r}")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        failures.append(f"{where} has invalid date {value!r}")
        return None


def audit(
    catalog_rows: list[guidelines_catalog.Row],
    registry: Registry,
    *,
    today: date | None = None,
) -> AuditResult:
    """Grade registry shape and both catalog joins; currency itself only reports."""

    today = today or date.today()
    failures = list(registry.problems)
    findings: list[str] = []
    catalog_by_filename = {row.filename: row for row in catalog_rows}
    if len(catalog_by_filename) != len(catalog_rows):
        failures.append("catalog filenames are not unique, so filename cannot be graded")
    catalog_societies = {row.society for row in catalog_rows}
    society_rows: dict[str, SocietyEntry] = {}
    observation_dates: list[date] = []
    for entry in registry.societies:
        where = f"currency:{entry.line} society {entry.society!r}"
        if not entry.society:
            failures.append(f"{where} is blank")
        elif entry.society in society_rows:
            failures.append(f"duplicate society row {entry.society!r}")
        else:
            society_rows[entry.society] = entry
        for column, value in (
            ("index", entry.index),
            ("reader", entry.reader),
            ("join key", entry.join_key),
        ):
            if not value:
                failures.append(f"{where} has blank {column}")
        if entry.access not in {"plain", "agent"}:
            failures.append(f"{where} has unknown access {entry.access!r}")
        ruled = SOCIETY_INDEXES.get(entry.society)
        declared = (entry.index, entry.reader, entry.join_key, entry.access)
        if ruled is not None and declared != ruled:
            failures.append(
                f"{where} route, reader, join key, or access disagrees with the "
                "ruled contract"
            )
        if entry.state not in SOCIETY_STATES:
            failures.append(f"{where} has unknown state {entry.state!r}")
        last_observed = _parsed_date(entry.last_observed, where, failures)
        state_observed = _parsed_date(entry.state_observed, where, failures)
        if entry.state == "read" and last_observed is None:
            failures.append(f"{where} state 'read' has no last observed date")
        if entry.state == "read" and state_observed is not None:
            failures.append(f"{where} state 'read' carries an unread-state date")
        if entry.state == "unread" and state_observed is None:
            failures.append(f"{where} state 'unread' has no state observed date")
        for label, value in (
            ("last observed", last_observed),
            ("state observed", state_observed),
        ):
            if value is not None and value > today:
                failures.append(f"{where} {label} date is in the future")
        if last_observed is not None:
            observation_dates.append(last_observed)

    for society in sorted(catalog_societies - set(society_rows)):
        failures.append(f"catalog society {society!r} has no society-index row")
    for society in sorted(set(society_rows) - catalog_societies):
        failures.append(f"society-index row {society!r} names no catalog society")

    document_rows: dict[str, DocumentEntry] = {}
    never_checked = 0
    for entry in registry.documents:
        where = f"currency:{entry.line} document {entry.filename!r}"
        if not entry.filename:
            failures.append(f"{where} is blank")
        elif entry.filename in document_rows:
            failures.append(f"duplicate currency row {entry.filename!r}")
        else:
            document_rows[entry.filename] = entry
        if entry.verdict not in VERDICTS:
            failures.append(f"{where} has unruled verdict {entry.verdict!r}")
        if entry.verdict == "unjoinable" and entry.join_value:
            failures.append(f"{where} is unjoinable but carries a join value")
        elif entry.verdict in set(VERDICTS) - {"unjoinable"} and not entry.join_value:
            failures.append(f"{where} verdict {entry.verdict!r} has no join value")
        observed = _parsed_date(entry.observed, where, failures)
        if observed is None:
            never_checked += 1
        else:
            observation_dates.append(observed)
            if observed > today:
                failures.append(f"{where} observation date is in the future")
        if entry.verdict == "superseded":
            if not entry.superseded_by:
                failures.append(f"{where} is superseded but names no replacement")
            elif entry.superseded_by not in catalog_by_filename:
                failures.append(
                    f"{where} names unknown superseding document {entry.superseded_by!r}"
                )
            elif entry.superseded_by == entry.filename:
                failures.append(f"{where} supersedes itself")
            else:
                findings.append(
                    f"{entry.filename}: superseded by {entry.superseded_by}"
                )
        elif entry.superseded_by:
            failures.append(
                f"{where} verdict {entry.verdict!r} carries a superseding document"
            )
        elif entry.verdict in {"absent", "unjoinable"}:
            findings.append(f"{entry.filename}: {entry.verdict}")
        catalog_row = catalog_by_filename.get(entry.filename)
        if catalog_row is not None and entry.society != catalog_row.society:
            failures.append(
                f"{where} society {entry.society!r} disagrees with catalog "
                f"{catalog_row.society!r}"
            )
    for filename in sorted(set(catalog_by_filename) - set(document_rows), key=str.casefold):
        failures.append(f"catalog document {filename!r} has no currency row")
    for filename in sorted(set(document_rows) - set(catalog_by_filename), key=str.casefold):
        failures.append(f"currency row {filename!r} names no catalog document")

    for society in sorted(ANNUAL_SOCIETIES & catalog_societies):
        editions = [
            int(row.year)
            for row in catalog_rows
            if row.society == society and row.year.isdigit()
        ]
        entry = society_rows.get(society)
        observed = (
            date.fromisoformat(entry.last_observed)
            if entry and DATE_RE.fullmatch(entry.last_observed)
            else None
        )
        publication_cycle = max([today.year, *editions]) if editions else today.year
        if observed is not None and observed.year < publication_cycle:
            findings.append(
                f"{society} observation {observed.isoformat()} predates its "
                f"{publication_cycle} publication cycle"
            )

    return AuditResult(
        tuple(failures),
        tuple(findings),
        len(catalog_societies),
        len(catalog_rows),
        never_checked,
        min(observation_dates) if observation_dates else None,
    )


class _AnchorReader(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.href = ""
        self.text: list[str] = []
        self.anchors: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() == "a":
            self.href = dict(attrs).get("href") or ""
            self.text = []

    def handle_data(self, data: str) -> None:
        if self.href:
            self.text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "a" and self.href:
            self.anchors.append((self.href, " ".join(self.text).strip()))
            self.href = ""
            self.text = []


def _normalize_doi(value: str) -> str | None:
    match = DOI_RE.search(value)
    return match.group(0).rstrip(".,;)").casefold() if match else None


def _guideline_anchors(society: str, content: str) -> tuple[str, list[tuple[str, str]]]:
    normalized = society.replace("-", " ").upper()
    aliases = {"AHA ACC": "AHA ACC"}
    normalized = aliases.get(normalized, normalized)
    parser = _AnchorReader()
    parser.feed(content)
    guideline_anchors = [
        (href, text)
        for href, text in parser.anchors
        if "guideline" in f"{href} {text}".casefold()
        or normalized in {"USPSTF", "ADA", "GINA", "GOLD", "ACIP", "CDC"}
        and any(token in f"{href} {text}".casefold() for token in ("recommend", "standard", "report", "schedule"))
    ]
    if not guideline_anchors:
        raise ReadError(
            f"{normalized} returned content but no guideline content was countable"
        )
    return normalized, guideline_anchors


def _join_from_anchor(normalized: str, combined: str) -> str | None:
    if normalized in {"USPSTF", "IDSA", "KDIGO", "AHA ACC"}:
        return _normalize_doi(combined)
    if normalized == "ADA":
        match = re.search(r"dc\d{2}-srev", combined, re.I)
        return match.group(0).casefold() if match else None
    if normalized in {"GINA", "GOLD"}:
        match = re.search(r"\b20\d{2}\b", combined)
        return match.group(0) if match else None
    if normalized == "ACIP":
        match = re.search(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+20\d{2}\b", combined, re.I)
        return match.group(0) if match else None
    if normalized == "CDC":
        match = re.search(r"\b(?:19|20)\d{2}\b", combined)
        return match.group(0) if match else None
    raise ReadError(f"no declared reader for society {normalized!r}")


def _detectable_unread_remainder(content: str, visible: int) -> int:
    """Return a lower bound for publisher entries visibly withheld by the response."""

    totals = (
        re.search(r"showing\s+\d+(?:\s*[-–]\s*\d+)?\s+of\s+(\d+)", content, re.I),
        re.search(r'"total(?:Results|Count)"\s*:\s*(\d+)', content, re.I),
    )
    for match in totals:
        if match is not None:
            return max(0, int(match.group(1)) - visible)
    has_next = re.search(
        r"\brel\s*=\s*['\"][^'\"]*\bnext\b|\bload\s+more\b|"
        r"['\"]hasMore['\"]\s*:\s*true",
        content,
        re.I,
    )
    return 1 if has_next else 0


def read_society_index(society: str, content: str) -> ReaderResult:
    """Read one supplied index capture and state its countable coverage."""

    normalized, guideline_anchors = _guideline_anchors(society, content)
    joins: list[str] = []
    unread = 0
    for href, text in guideline_anchors:
        combined = f"{href} {text}"
        value = _join_from_anchor(normalized, combined)
        if value and value not in joins:
            joins.append(value)
        if value is None:
            unread += 1
    hidden = _detectable_unread_remainder(content, len(guideline_anchors))
    return ReaderResult(
        normalized,
        len(guideline_anchors) + hidden,
        tuple(joins),
        unread + hidden,
    )


def follow_index_links(
    society: str,
    content: str,
    index_url: str,
    fetcher=None,
) -> ReaderResult:
    """Resolve join-less counted entries through publisher-owned detail pages."""

    if fetcher is None:
        fetcher = download_text
    normalized, anchors = _guideline_anchors(society, content)
    direct = [_join_from_anchor(normalized, f"{href} {text}") for href, text in anchors]
    missing_urls = [
        urljoin(index_url, href)
        for (href, _), value in zip(anchors, direct, strict=True)
        if value is None and href and not href.casefold().startswith(("javascript:", "mailto:"))
    ]

    def safe_fetch(url: str) -> str:
        try:
            return fetcher(url)
        except (OSError, KeyError, ReadError):
            return ""

    with ThreadPoolExecutor(max_workers=min(8, len(missing_urls) or 1)) as pool:
        followed = iter(pool.map(safe_fetch, missing_urls))
        values: list[str | None] = []
        for (href, _), value in zip(anchors, direct, strict=True):
            if value is not None:
                values.append(value)
            elif href and not href.casefold().startswith(("javascript:", "mailto:")):
                values.append(_join_from_anchor(normalized, next(followed)))
            else:
                values.append(None)
    joins = tuple(dict.fromkeys(value for value in values if value is not None))
    hidden = _detectable_unread_remainder(content, len(anchors))
    return ReaderResult(
        normalized,
        len(anchors) + hidden,
        joins,
        sum(value is None for value in values) + hidden,
    )


def follow_doi_links(
    society: str,
    content: str,
    index_url: str,
    fetcher=None,
) -> ReaderResult:
    """Compatibility name for the DOI-reader public seam."""

    return follow_index_links(society, content, index_url, fetcher)


def compare_index(
    documents: tuple[DocumentEntry, ...] | list[DocumentEntry],
    result: ReaderResult,
) -> IndexComparison:
    """Compare one complete or partial society read in both join directions."""

    by_join: dict[str, list[str]] = {}
    for row in documents:
        if row.society.upper() != result.society.upper() or not row.join_value:
            continue
        by_join.setdefault(row.join_value.casefold(), []).append(row.filename)
    published = {value.casefold(): value for value in result.join_values}
    corpus_absent = tuple(
        sorted(
            (
                filename
                for join, filenames in by_join.items()
                if join not in published
                for filename in filenames
            ),
            key=str.casefold,
        )
    )
    publisher_additions = tuple(
        published[join] for join in sorted(set(published) - set(by_join))
    )
    return IndexComparison(corpus_absent, publisher_additions)


def download_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "clinical-skills-guideline-currency/1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
    except (OSError, urllib.error.URLError) as error:
        raise ReadError(f"download failed for {url}: {error}") from error
    if not payload:
        raise ReadError(f"download returned no bytes for {url}")
    return payload


def download_text(url: str) -> str:
    payload = download_bytes(url)
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload.decode("windows-1252")


def validate_pdf_bytes(payload: bytes) -> None:
    """Refuse a successful HTML challenge or empty body masquerading as a PDF."""

    if not payload.startswith(b"%PDF-"):
        raise ReadError("downloaded replacement is not a PDF")


def run_rebuild_pipeline(
    corpus_root: Path,
    catalog_path: Path = DEFAULT_CATALOG,
    audit_path: Path = DEFAULT_AUDIT,
    coverage_path: Path = DEFAULT_COVERAGE,
) -> None:
    """Run the governed rebuild stages after a replacement reaches the corpus."""

    commands = (
        [sys.executable, str(REPO_ROOT / "tools" / "guidelines_build.py"), str(corpus_root)],
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "guidelines_catalog.py"),
            "--pdf-src",
            str(corpus_root),
            "--catalog",
            str(catalog_path),
            "--audit",
            str(audit_path),
        ],
        [
            sys.executable,
            str(REPO_ROOT / "tools" / "threshold_coverage.py"),
            "--catalog",
            str(catalog_path),
            "--coverage",
            str(coverage_path),
        ],
    )
    for command in commands:
        subprocess.run(command, cwd=REPO_ROOT, check=True)


def _mark_topic_unread(
    coverage_path: Path,
    topic: str,
    old_filename: str,
    replacement: str,
    digest: str,
    observed: str,
) -> None:
    lines = coverage_path.read_text(encoding="utf-8").splitlines()
    found = False
    for index, line in enumerate(lines):
        cells = _cells(line)
        if cells is None or len(cells) != 5 or cells[0].casefold() != topic.casefold():
            continue
        found = True
        cells[2] = "unread"
        cells[4] = (
            f"superseded {old_filename} by {replacement}; fetched {observed}; "
            f"sha256 {digest}"
        )
        lines[index] = "| " + " | ".join(cells) + " |"
        break
    if not found:
        raise ValueError(f"coverage registry has no topic {topic!r}")
    coverage_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _upsert_audit_digest(
    audit_path: Path,
    society: str,
    filename: str,
    digest: str,
    byte_count: int,
    observed: str,
) -> None:
    """Bind the received bytes into the audit ledger's Documents table."""

    lines = audit_path.read_text(encoding="utf-8").splitlines()
    heading = next(
        (index for index, line in enumerate(lines) if line.strip() == "## Documents"),
        None,
    )
    if heading is None:
        raise ValueError("audit ledger has no '## Documents' table")
    table_header = next(
        (
            index
            for index in range(heading + 1, len(lines))
            if _cells(lines[index]) == ["society", "filename", "sha256", "bytes", "audited"]
        ),
        None,
    )
    if table_header is None:
        raise ValueError("audit ledger has no readable Documents header")
    rendered = f"| {society} | {filename} | {digest} | {byte_count} | {observed} |"
    insertion = len(lines)
    replaced = False
    for index in range(table_header + 2, len(lines)):
        if lines[index].startswith("## "):
            insertion = index
            break
        cells = _cells(lines[index])
        if cells and len(cells) == 5 and cells[0] == society and cells[1] == filename:
            lines[index] = rendered
            replaced = True
            break
    if not replaced:
        while insertion > table_header + 2 and not lines[insertion - 1].strip():
            insertion -= 1
        lines.insert(insertion, rendered)
    audit_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fetch_replacement(
    url: str,
    filename: str,
    corpus_root: Path,
    coverage_path: Path,
    topic: str,
    old_filename: str,
    audit_path: Path = DEFAULT_AUDIT,
    catalog_path: Path = DEFAULT_CATALOG,
    registry_path: Path = DEFAULT_REGISTRY,
) -> FetchRecord:
    """Fetch a replacement, record its bytes, rebuild, and stop before the sheet."""

    relative = PurePosixPath(filename)
    if relative.is_absolute() or ".." in relative.parts or relative.suffix.casefold() != ".pdf":
        raise ValueError("--filename must be a relative SOCIETY/name.pdf path")
    if len(relative.parts) < 2 or relative.parts[0] not in SOCIETY_INDEXES:
        raise ValueError("--filename must begin with a catalog society directory")
    if urlparse(url).scheme.casefold() not in {"http", "https"}:
        raise ValueError("--fetch-replacement URL must use HTTP(S)")
    corpus_root = ensure_outside_checkout(
        corpus_root,
        detail=(
            "Guideline PDFs contain society-copyrighted expression and belong in "
            "the external corpus."
        ),
    )
    destination = corpus_root.joinpath(*relative.parts)
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing corpus document {destination}")
    catalog_text = _read_text(catalog_path, "catalog")
    catalog_rows, _, catalog_problems = guidelines_catalog.parse_catalog(catalog_text)
    if catalog_problems:
        raise ValueError("catalog did not parse: " + "; ".join(catalog_problems))
    matching_catalog = [
        row
        for row in catalog_rows
        if row.filename == relative.name and row.society == relative.parts[0]
    ]
    if len(matching_catalog) != 1:
        raise ValueError(
            f"catalog has no replacement {relative.parts[0]}/{relative.name}; "
            "curate its row before fetching"
        )
    registry = parse_registry(_read_text(registry_path, "currency registry"))
    preflight = audit(catalog_rows, registry)
    if preflight.failures:
        raise ValueError("currency handoff is not ready: " + "; ".join(preflight.failures))
    by_filename = {row.filename: row for row in registry.documents}
    old_entry = by_filename.get(old_filename)
    replacement_entry = by_filename.get(relative.name)
    if (
        old_entry is None
        or old_entry.verdict != "superseded"
        or old_entry.superseded_by != relative.name
        or replacement_entry is None
        or replacement_entry.society != relative.parts[0]
    ):
        raise ValueError(
            "currency registry must bind the retired document to the cataloged replacement"
        )
    audit_text = _read_text(audit_path, "audit ledger")
    audit_lines = audit_text.splitlines()
    if "## Documents" not in audit_lines or not any(
        _cells(line) == ["society", "filename", "sha256", "bytes", "audited"]
        for line in audit_lines
    ):
        raise ValueError("audit ledger has no readable '## Documents' table")
    coverage_text = _read_text(coverage_path, "coverage registry")
    if not any(
        cells is not None and len(cells) == 5 and cells[0].casefold() == topic.casefold()
        for cells in (_cells(line) for line in coverage_text.splitlines())
    ):
        raise ValueError(f"coverage registry has no topic {topic!r}")
    payload = download_bytes(url)
    validate_pdf_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    observed = date.today().isoformat()
    destination.parent.mkdir(parents=True, exist_ok=True)
    sidecar = destination.with_suffix(destination.suffix + ".fetch.json")
    destination.write_bytes(payload)
    record = FetchRecord(url, filename, digest, len(payload), observed)
    try:
        sidecar.write_text(
            json.dumps(record.__dict__, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _upsert_audit_digest(
            audit_path,
            relative.parts[0],
            relative.name,
            digest,
            len(payload),
            observed,
        )
        _mark_topic_unread(
            coverage_path, topic, old_filename, filename, digest, observed
        )
        run_rebuild_pipeline(corpus_root, catalog_path, audit_path, coverage_path)
    except Exception:
        audit_path.write_text(audit_text, encoding="utf-8")
        coverage_path.write_text(coverage_text, encoding="utf-8")
        sidecar.unlink(missing_ok=True)
        destination.unlink(missing_ok=True)
        raise
    return record


def _source_metadata(sheet_root: Path) -> dict[str, dict[str, str]]:
    """Read only the governed Sources tables; importing the sheet grader would cycle."""

    found: dict[str, dict[str, str]] = {}
    columns = ("key", "society", "document", "source class", "version", "published", "url", "basis", "mode")
    for path in sorted(sheet_root.glob("*.md")):
        section = ""
        active = False
        for line in path.read_text(encoding="utf-8").splitlines():
            heading = re.match(r"^##\s+(.+?)\s*$", line)
            if heading:
                section = heading.group(1).casefold()
                active = False
                continue
            cells = _cells(line)
            if section != "sources" or cells is None or _is_rule(cells):
                continue
            if not active:
                active = tuple(cell.casefold() for cell in cells) == columns
                continue
            if len(cells) != len(columns):
                continue
            named = dict(zip(columns, cells, strict=True))
            filename = Path(named["document"]).name + ".pdf"
            found[filename] = named
    return found


def _join_value(
    row: guidelines_catalog.Row, source: dict[str, str] | None = None
) -> str:
    source = source or {}
    if row.society in {"USPSTF", "IDSA", "KDIGO", "AHA ACC"}:
        return _normalize_doi(row.citation) or _normalize_doi(source.get("url", "")) or ""
    if row.society == "ADA" and row.year.isdigit():
        return f"10.2337/dc{row.year[-2:]}-srev"
    if row.society in {"GINA", "GOLD"}:
        match = re.search(r"\b20\d{2}\b", source.get("url", ""))
        return match.group(0) if match else (row.year if row.year.isdigit() else "")
    if row.society == "ACIP":
        return source.get("published", "") if DATE_RE.fullmatch(source.get("published", "")) else ""
    if row.society == "CDC":
        match = re.search(r"\b(?:19|20)\d{2}\b", source.get("published", ""))
        return match.group(0) if match else (row.year if row.year.isdigit() else "")
    return ""


def render_draft(
    catalog_rows: list[guidelines_catalog.Row],
    source_metadata: dict[str, dict[str, str]] | None = None,
) -> str:
    """Render a complete initial registry without inventing missing join values."""

    societies = sorted({row.society for row in catalog_rows}, key=str.casefold)
    society_lines = []
    for society in societies:
        route, reader, join_key, access = SOCIETY_INDEXES.get(
            society, ("?", "?", "?", "agent")
        )
        society_lines.append(
            f"| {society} | {route} | {reader} | {join_key} | {access} | "
            " | unread |  |"
        )
    document_lines = []
    for row in sorted(catalog_rows, key=lambda item: item.filename.casefold()):
        join_value = _join_value(row, (source_metadata or {}).get(row.filename))
        verdict = "current" if join_value else "unjoinable"
        document_lines.append(
            f"| {row.filename} | {row.society} | {join_value} | {verdict} | "
            " |  |"
        )
    return (
        "# Guideline edition currency\n\n"
        "One publisher-index observation per society and one edition-currency "
        "verdict per catalog document. An observation date records that somebody "
        "looked; it is not a guarantee that a document remains current.\n\n"
        f"{SCHEMA_MARKER}\n\n"
        "## Society indexes\n\n"
        "| " + " | ".join(SOCIETY_COLUMNS) + " |\n"
        "| " + " | ".join("---" for _ in SOCIETY_COLUMNS) + " |\n"
        + "\n".join(society_lines)
        + "\n\n## Documents\n\n"
        "| " + " | ".join(DOCUMENT_COLUMNS) + " |\n"
        "| " + " | ".join("---" for _ in DOCUMENT_COLUMNS) + " |\n"
        + "\n".join(document_lines)
        + "\n"
    )


def _read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ReadError(f"{label} {path} is unreadable: {error}") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--hook-summary",
        action="store_true",
        help="print only the non-refusing oldest-observation and never-checked advisory",
    )
    parser.add_argument(
        "--draft",
        type=Path,
        metavar="PATH",
        help="write a complete registry scaffold bound to --catalog",
    )
    parser.add_argument(
        "--read",
        action="append",
        metavar="SOCIETY",
        help="read one society index; repeatable (networked unless --capture supplies it)",
    )
    parser.add_argument(
        "--capture",
        action="append",
        default=[],
        metavar="SOCIETY=PATH",
        help="agent- or browser-supplied society-index capture",
    )
    parser.add_argument("--fetch-replacement", metavar="URL")
    parser.add_argument("--filename", help="relative SOCIETY/name.pdf destination")
    parser.add_argument("--corpus-root", type=Path)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--topic")
    parser.add_argument("--supersedes", help="catalog filename replaced by the download")
    return parser


def _captures(arguments: list[str]) -> dict[str, Path]:
    captures: dict[str, Path] = {}
    for argument in arguments:
        society, separator, raw_path = argument.partition("=")
        if not separator or not society or not raw_path:
            raise ReadError(f"invalid --capture {argument!r}; expected SOCIETY=PATH")
        key = society.replace("-", " ").upper()
        if key in captures:
            raise ReadError(f"--capture names {society!r} twice")
        captures[key] = Path(raw_path)
    return captures


def _run_reads(args: argparse.Namespace, registry: Registry) -> int:
    if registry.problems:
        raise ReadError("registry did not parse: " + "; ".join(registry.problems))
    by_society = {entry.society.upper(): entry for entry in registry.societies}
    captures = _captures(args.capture)
    incomplete = False
    for requested in args.read:
        key = requested.replace("-", " ").upper()
        entry = by_society.get(key)
        if entry is None:
            raise ReadError(f"registry has no society {requested!r}")
        capture = captures.get(key)
        if capture is not None:
            content = _read_text(capture, f"{entry.society} capture")
        elif entry.access == "agent":
            raise ReadError(
                f"{entry.society} is an agent read; supply --capture "
                f"{entry.society.replace(' ', '-')}=PATH"
            )
        else:
            content = download_text(entry.index)
        if entry.access == "plain" and capture is None:
            result = follow_index_links(entry.society, content, entry.index)
        else:
            result = read_society_index(entry.society, content)
        comparison = compare_index(registry.documents, result)
        print(
            f"{entry.society}: read {result.denominator - result.unread} of "
            f"{result.denominator}; unread {result.unread}; corpus absent "
            f"{len(comparison.corpus_absent)}; publisher additions "
            f"{len(comparison.publisher_additions)}"
        )
        if args.verbose:
            print(f"  coverage: {SOCIETY_COVERAGE[entry.society]}")
            for filename in comparison.corpus_absent:
                print(f"  corpus absent: {filename}")
            for value in comparison.publisher_additions:
                print(f"  publisher addition: {value}")
        incomplete = incomplete or result.unread > 0
    return 2 if incomplete else 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    selected_modes = sum(bool(value) for value in (args.draft, args.read, args.fetch_replacement))
    if selected_modes > 1:
        parser.error("--draft, --read, and --fetch-replacement are separate operations")
    if args.capture and not args.read:
        parser.error("--capture is meaningful only with --read")
    try:
        catalog_text = _read_text(args.catalog, "catalog")
        catalog_rows, _, catalog_problems = guidelines_catalog.parse_catalog(catalog_text)
        if catalog_problems:
            raise ReadError("catalog did not parse: " + "; ".join(catalog_problems))
        if args.draft:
            args.draft.write_text(
                render_draft(
                    catalog_rows,
                    _source_metadata(REPO_ROOT / "reference" / "thresholds"),
                ),
                encoding="utf-8",
            )
            print(f"wrote {len(catalog_rows)} document rows to {args.draft}")
            return 0
        registry_text = _read_text(args.registry, "registry")
        parsed = parse_registry(registry_text)
        if args.read:
            preflight = audit(catalog_rows, parsed)
            if preflight.failures:
                raise ReadError(
                    "currency registry did not grade: " + "; ".join(preflight.failures)
                )
            return _run_reads(args, parsed)
        if args.fetch_replacement:
            missing = [
                name
                for name, value in (
                    ("--filename", args.filename),
                    ("--corpus-root", args.corpus_root),
                    ("--topic", args.topic),
                    ("--supersedes", args.supersedes),
                )
                if not value
            ]
            if missing:
                raise ReadError(
                    "--fetch-replacement also needs " + ", ".join(missing)
                )
            fetched = fetch_replacement(
                args.fetch_replacement,
                args.filename,
                args.corpus_root,
                args.coverage,
                args.topic,
                args.supersedes,
                args.audit,
                args.catalog,
                args.registry,
            )
            print(
                f"fetched {fetched.filename}: {fetched.bytes} bytes; "
                f"sha256 {fetched.sha256}; stopped before every threshold sheet"
            )
            return 0
        result = audit(catalog_rows, parsed)
    except (ReadError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"NOT GRADED: {error}", file=sys.stderr)
        return 2

    counts = {verdict: 0 for verdict in VERDICTS}
    for row in parsed.documents:
        if row.verdict in counts:
            counts[row.verdict] += 1
    oldest = result.oldest_observation.isoformat() if result.oldest_observation else "none"
    if args.hook_summary:
        print(
            f"guideline currency: oldest observation {oldest}; never checked "
            f"{result.never_checked}. Remedy: run guidelines_currency.py --read SOCIETY."
        )
        return 0
    print(
        f"societies {result.society_count} catalog; society index rows "
        f"{len(parsed.societies)}; unread societies "
        f"{sum(row.state == 'unread' for row in parsed.societies)}; "
        f"documents {result.document_count}; "
        + "; ".join(f"{key} {counts[key]}" for key in VERDICTS)
    )
    print(f"oldest observation {oldest}; never checked {result.never_checked}")
    print(f"currency findings {len(result.findings)}; registry failures {len(result.failures)}")
    if args.verbose:
        for message in result.findings:
            print(f"FINDING: {message}")
    for message in result.failures:
        print(f"FAIL: {message}", file=sys.stderr)
    return 1 if result.failures else 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
