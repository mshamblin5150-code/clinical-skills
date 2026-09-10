"""Pure text grammar for distilled threshold sheets.

The parser and its value records live here so producers and consumers can share the
sheet language without importing the gate runner or any of its filesystem policy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import artifact_provenance
import guidelines_manifest


SCHEMA_MARKER = "<!-- schema: threshold-sheet/2 -->"

NARRATIVE_KIND = "narrative"

_SOURCE_LOCATOR = re.compile(
    r"^p(?P<page>\d+)/(?P<kind>[^/\s]+)/(?P<identifier>[^/\s]+)$"
)

# Section headings are production vocabulary shared with the draft scaffolder.
SOURCES_HEADING = "## Sources"

SOURCE_COLUMNS = (
    "key",
    "society",
    "document",
    "source class",
    "version",
    "published",
    "url",
    "basis",
    "mode",
)

SCOPE_HEADING = "## Scope"

POPULATIONS_HEADING = "## Populations"

QUANTITIES_HEADING = "## Quantities"

THRESHOLDS_HEADING = "## Thresholds"

NONE_DECLARATION = (
    "**No decision point.** Every span in `## Scope` has left the unread list and "
    "this source states no quantity that changes what is done to a patient."
)

NON_SOURCE_DECLARATION = (
    "**Declared non-source.** Every span in `## Scope` has left the unread list and "
    "this source is a scope of work that states what a future guideline will cover."
)

CONFLICTS_HEADING = "## Conflicts"

COVERAGE_HEADING = "## Coverage"

SECTION_HEADINGS = (
    SOURCES_HEADING,
    SCOPE_HEADING,
    POPULATIONS_HEADING,
    QUANTITIES_HEADING,
    THRESHOLDS_HEADING,
    CONFLICTS_HEADING,
    COVERAGE_HEADING,
)

# The eight columns of a threshold row, in order.
ROW_COLUMNS = ("quantity", "population", "value", "snippet", "source", "page", "rec", "class")

# Refuse the two C0 slots Python would erase as whitespace or a line break before
# the parser can preserve their row and source location.
FORBIDDEN_IN_RAW_TEXT = {
    "\u001e": "line splitting would erase it with its row",
    "\u001f": "cell trimming would erase it",
}

_ROW_PIPE = re.compile(r"^\s*\|(?P<body>.+)\|\s*$")

_CONFLICT = re.compile(r"^\s*\*{0,2}CONFLICT\*{0,2}:\s*(?P<quantity>[a-z0-9-]+)\b(?P<rest>.*)$", re.IGNORECASE)

_OUT_LINE = re.compile(r"^\s*-\s*`(?P<rec_id>[^`]+)`\s*[-\u2014:]\s*(?P<reason>.+?)\s*$")

_RESOLVED = re.compile(r"citations resolved against\s+(?P<corpus>\S+)\s+on\s+(?P<date>\d{4}-\d{2}-\d{2})", re.IGNORECASE)

_EXTRACTION_IDENTITY = re.compile(
    r"^extraction identity:\s*producer\s+(?P<commit>[0-9a-f]{40});\s*"
    r"tools/guidelines_extract\.py\s+sha256\s+(?P<sha256>[0-9a-f]{64})\s*$",
    re.IGNORECASE,
)

_SPAN_SOURCE = re.compile(
    r"^\s*\*{0,2}Source:\s*`?(?P<source>[a-z0-9-]+)`?\*{0,2}\s*$",
    re.IGNORECASE,
)

_SPAN_RANGE = re.compile(r"^p?(?P<first>\d+)(?:\s*-\s*p?(?P<last>\d+))?$", re.I)

_DATED_SPAN_READ = re.compile(
    r"^read\s+(?P<date>\d{4}-\d{2}-\d{2})"
    r"(?:;\s*blind\s+(?P<blind_date>\d{4}-\d{2}-\d{2}))?$",
    re.I,
)

_SPAN_EXEMPTION = re.compile(r"^exempt:\s*(?P<reason>\S.+)$", re.I)

@dataclass(frozen=True)
class Row:
    quantity: str
    population: str
    value: str
    snippet: str
    source: str
    page: int | None
    rec: str
    klass: str
    line: int

@dataclass(frozen=True)
class SourceLocator:
    """The page, kind, and identifier carried by one threshold-row locator."""

    page: int
    kind: str
    identifier: str

    @property
    def is_narrative(self) -> bool:
        return self.kind == NARRATIVE_KIND

def source_locator(value: str) -> SourceLocator | None:
    """Parse ``p<digits>/<kind>/<id>`` without inferring an unknown kind."""

    match = _SOURCE_LOCATOR.fullmatch(value)
    if match is None:
        return None
    return SourceLocator(
        page=int(match.group("page")),
        kind=match.group("kind"),
        identifier=match.group("identifier"),
    )

@dataclass(frozen=True)
class Span:
    source: str
    name: str
    first_page: int
    last_page: int
    read: str
    line: int

    @property
    def is_unread(self) -> bool:
        return self.read.casefold() == "no"

    @property
    def has_dated_marker(self) -> bool:
        match = _DATED_SPAN_READ.fullmatch(self.read)
        if match is None:
            return False
        for group in ("date", "blind_date"):
            value = match.group(group)
            if value is None:
                continue
            try:
                date.fromisoformat(value)
            except ValueError:
                return False
        return True

    @property
    def blind_read_date(self) -> date | None:
        match = _DATED_SPAN_READ.fullmatch(self.read)
        if match is None or not self.has_dated_marker:
            return None
        value = match.group("blind_date")
        return date.fromisoformat(value) if value is not None else None

    @property
    def exemption_reason(self) -> str | None:
        match = _SPAN_EXEMPTION.fullmatch(self.read)
        return match.group("reason") if match else None

@dataclass(frozen=True)
class ExtractionIdentity:
    """The two manifest fields a sheet binds its extracted-text reading to."""

    producer_commit: str
    extractor_sha256: str

def extraction_identity_from_handoff(
    handoff: guidelines_manifest.Manifest,
) -> tuple[ExtractionIdentity | None, list[str]]:
    """Derive the extraction identity from one validated manifest handoff."""

    path = handoff.root / guidelines_manifest.MANIFEST_NAME
    producer = handoff.provenance.producer if handoff.provenance else None
    if not isinstance(producer, dict):
        problems = [problem.message for problem in handoff.problems]
        return None, problems or [f"{path} has no validated producer record"]
    commit = producer.get("commit")
    inputs = producer.get("inputs")
    extractor = next(
        (
            item.get("sha256")
            for item in inputs
            if isinstance(item, dict)
            and item.get("path") == "tools/guidelines_extract.py"
        ),
        None,
    ) if isinstance(inputs, list) else None
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        return None, [f"{path} producer has no 40-character commit"]
    if not isinstance(extractor, str) or re.fullmatch(r"[0-9a-f]{64}", extractor) is None:
        return None, [f"{path} validated producer has no extractor SHA-256"]
    return ExtractionIdentity(commit, extractor), []

def render_extraction_identity(identity: ExtractionIdentity) -> str:
    """Render the declaration shared by the draft producer and sheet parser."""

    return (
        f"extraction identity: producer {identity.producer_commit}; "
        f"tools/guidelines_extract.py sha256 {identity.extractor_sha256}"
    )

@dataclass
class Sheet:
    """A parsed sheet. ``ok`` is false when it could not be read as one at all."""

    path: Path
    rows: list[Row] = field(default_factory=list)
    sources: dict[str, dict[str, str]] = field(default_factory=dict)
    populations: dict[str, str] = field(default_factory=dict)
    quantities: dict[str, str] = field(default_factory=dict)
    conflicts: dict[str, str] = field(default_factory=dict)
    scoped_out: dict[str, str] = field(default_factory=dict)
    spans: list[Span] = field(default_factory=list)
    span_problems: list[str] = field(default_factory=list)
    # The prose of the ``## Scope`` section, and nothing from anywhere else. Kept as
    # its own field rather than searched for over the whole document because the two
    # phrases that satisfy it are ordinary English: a threshold row whose snippet
    # quotes "not read" would otherwise discharge the sheet's honesty clause.
    scope: str = ""
    thresholds: str = ""
    has_scope_section: bool = False
    resolved_corpus: str | None = None
    resolved_date: str | None = None
    extraction_identity: ExtractionIdentity | None = None
    accepted_distrust: artifact_provenance.AcceptedDistrust | None = None
    accepted_distrust_problems: tuple[str, ...] = ()
    ok: bool = True
    why_not: str | None = None

def _cells(line: str) -> list[str] | None:
    """A Markdown table row as its cells, or None if the line is not one."""
    match = _ROW_PIPE.match(line)
    if not match:
        return None
    return [cell.strip() for cell in match.group("body").split("|")]

def _is_rule(cells: list[str]) -> bool:
    """The ``| --- | --- |`` line under a header."""
    return all(set(cell) <= set("-: ") and cell for cell in cells)

def parse(text: str, path: Path) -> Sheet:
    """Read a sheet into its parts.

    Sections are found by heading, and a row is only read inside the section that
    owns it. **That is the load-bearing choice in here.** A sheet's prose discusses
    its own rules -- this file's docstring is full of pipe characters and quantity
    keys -- and a parser matching a row shape anywhere would read the explanation of
    a conflict as a conflict. ``block_scan.py`` learned the same rule the hard way:
    a row fires on what opens a section, never on a mention inside one.
    """
    sheet = Sheet(path=path)
    raw_findings = [
        (offset, character, why)
        for character, why in FORBIDDEN_IN_RAW_TEXT.items()
        if (offset := text.find(character)) != -1
    ]
    if raw_findings:
        offset, character, why = min(raw_findings)
        line = text.count("\n", 0, offset) + 1
        sheet.ok = False
        sheet.why_not = (
            f"{path.name}:{line} contains U+{ord(character):04X}, a mis-encoded "
            f"comparison operator that {why}; render the cited PDF page (for example "
            "with PyMuPDF), visually verify the operator, and replace it with ASCII "
            "<= or >="
        )
        return sheet
    if SCHEMA_MARKER not in text:
        sheet.ok = False
        sheet.why_not = f"no {SCHEMA_MARKER} marker"
        return sheet

    section: str | None = None
    source_columns: list[str] = []
    span_source: str | None = None
    reading_span_table = False
    for number, line in enumerate(text.splitlines(), start=1):
        heading = re.match(r"^\s*#{1,6}\s+(?P<name>.+?)\s*$", line)
        if heading:
            section = heading.group("name").strip().lower()
            if section == SCOPE_HEADING.removeprefix("## ").lower():
                sheet.has_scope_section = True
                span_source = None
                reading_span_table = False
            continue

        if section == SCOPE_HEADING.removeprefix("## ").lower():
            sheet.scope += line + "\n"
            source_match = _SPAN_SOURCE.match(line)
            if source_match:
                span_source = source_match.group("source")
                reading_span_table = False
            resolved = _RESOLVED.search(line)
            if resolved:
                sheet.resolved_corpus = resolved.group("corpus")
                sheet.resolved_date = resolved.group("date")
            extraction_identity = _EXTRACTION_IDENTITY.fullmatch(line.strip())
            if extraction_identity:
                sheet.extraction_identity = ExtractionIdentity(
                    extraction_identity.group("commit").lower(),
                    extraction_identity.group("sha256").lower(),
                )

        if section == THRESHOLDS_HEADING.removeprefix("## ").lower():
            sheet.thresholds += line + "\n"

        if section == CONFLICTS_HEADING.removeprefix("## ").lower():
            conflict = _CONFLICT.match(line)
            if conflict:
                sheet.conflicts[conflict.group("quantity").lower()] = conflict.group("rest").strip()
            continue

        if section == COVERAGE_HEADING.removeprefix("## ").lower():
            out = _OUT_LINE.match(line)
            if out:
                sheet.scoped_out[out.group("rec_id")] = out.group("reason")
            continue

        cells = _cells(line)
        if cells is None or _is_rule(cells):
            continue

        if (
            section == SCOPE_HEADING.removeprefix("## ").lower()
            and [cell.casefold() for cell in cells] == ["span", "pages", "read"]
        ):
            reading_span_table = True
            continue

        if section == SCOPE_HEADING.removeprefix("## ").lower() and reading_span_table:
            if len(cells) != 3:
                sheet.span_problems.append(
                    f"{path.name}:{number} span row has {len(cells)} cells, expected 3"
                )
                continue
            source = span_source
            if source is None and len(sheet.sources) == 1:
                source = next(iter(sheet.sources))
            if source is None:
                sheet.span_problems.append(
                    f"{path.name}:{number} span table in a multi-source sheet has no "
                    "preceding 'Source: `<source key>`' line"
                )
                continue
            page_match = _SPAN_RANGE.fullmatch(cells[1])
            if page_match is None:
                sheet.span_problems.append(
                    f"{path.name}:{number} span '{cells[0]}' has invalid page range '{cells[1]}'"
                )
                continue
            first = int(page_match.group("first"))
            last = int(page_match.group("last") or first)
            if first < 1 or last < first:
                sheet.span_problems.append(
                    f"{path.name}:{number} span '{cells[0]}' has invalid page range '{cells[1]}'"
                )
                continue
            sheet.spans.append(Span(source, cells[0], first, last, cells[2], number))
            continue

        if section == SOURCES_HEADING.removeprefix("## ").lower() and not source_columns:
            if cells != list(SOURCE_COLUMNS):
                sheet.ok = False
                sheet.why_not = (
                    f"{path.name}:{number} unreadable '## Sources' header; expected "
                    + " | ".join(SOURCE_COLUMNS)
                )
                return sheet
            source_columns = list(SOURCE_COLUMNS)
            continue

        if (
            section == SOURCES_HEADING.removeprefix("## ").lower()
            and len(cells) == len(SOURCE_COLUMNS)
            and cells[0] != "key"
        ):
            named = dict(zip(source_columns, cells, strict=True))
            sheet.sources[cells[0]] = {
                column: named[column]
                for column in SOURCE_COLUMNS
                if column != "key"
            }
        elif (
            section == POPULATIONS_HEADING.removeprefix("## ").lower()
            and len(cells) >= 2
            and cells[0] != "key"
        ):
            sheet.populations[cells[0]] = cells[1]
        elif (
            section == QUANTITIES_HEADING.removeprefix("## ").lower()
            and len(cells) >= 2
            and cells[0] != "key"
        ):
            sheet.quantities[cells[0]] = cells[1]
        elif (
            section == THRESHOLDS_HEADING.removeprefix("## ").lower()
            and len(cells) >= len(ROW_COLUMNS)
            and cells[0] != "quantity"
        ):
            page = re.sub(r"^p", "", cells[5], flags=re.IGNORECASE)
            sheet.rows.append(
                Row(
                    quantity=cells[0],
                    population=cells[1],
                    value=cells[2],
                    snippet=cells[3].strip('"'),
                    source=cells[4],
                    page=int(page) if page.isdigit() else None,
                    rec=cells[6],
                    klass=cells[7],
                    line=number,
                )
            )

    declaration_text = " ".join(sheet.thresholds.split())
    has_null_declaration = declaration_text in {
        " ".join(NONE_DECLARATION.split()),
        " ".join(NON_SOURCE_DECLARATION.split()),
    }
    if not sheet.rows and not has_null_declaration:
        sheet.ok = False
        sheet.why_not = "no row under a '## Thresholds' heading"
    sheet.accepted_distrust, sheet.accepted_distrust_problems = (
        artifact_provenance.parse_accepted_distrust(sheet.scope)
    )
    return sheet

def _normalize(text: str) -> str:
    """Whitespace-flattened and dash-folded, for comparing a snippet to a page.

    A snippet is copied out of a table cell and the page sets the same words with a
    line break in the middle of them; comparing raw would fail on typography rather
    than on the citation. Nothing here touches a digit.
    """
    text = re.sub(r"[\u2010-\u2015\u2212]", "-", text)
    text = re.sub(r"[\u2018\u2019\u201c\u201d]", "'", text)
    return re.sub(r"\s+", " ", text).strip().lower()
