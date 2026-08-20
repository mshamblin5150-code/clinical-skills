"""Build and verify ``reference/guidelines-catalog.md``, the one-row-per-document
index of the guideline corpus.

    python tools/guidelines_catalog.py                         # check catalog and audit
    python tools/guidelines_catalog.py --draft <src-dir>       # emit a catalog scaffold
    python tools/guidelines_catalog.py --audit-draft <src-dir> # emit a blind audit

The corpus is 179 PDFs at ``C:/codeing/guidelines-src``. It lives **outside this
repo** and stays there: 410 MB, most of it society-copyrighted, and no consumer
needs the sources, they need the derived facts. Issue #87.

**The catalog is curated, not generated, and that is the point.** ``--draft``
fills the four columns a machine can settle — ``society``, ``filename``,
``page_count``, ``class`` — and takes a run at ``title`` and ``year``. It does
**not** fill ``topic`` or ``population``, because a rule that reads those off a
title page is guessing, and a guessed population is worse than a blank one: it is
the field that decides whether a threshold applies to the patient at all. Those
cells are read by a human or an agent and left ``?`` where the title page does not
settle them.

So the committed catalog remains the source of truth, but it is no longer its own
evidence. ``reference/guidelines-catalog-audit.md`` records a blind second read of
every judgment cell, a page locator, the kind of evidence used, an audit date, and
the SHA-256 of the PDF read. The audit draft exposes file identity only, never the
catalog values or the machine guesses. A disagreement remains a failure until a
clinician records a dated ruling that confirms the catalog value.

The normal command re-derives the mechanical columns from the corpus and refuses
a catalog that has drifted: a dropped row, a wrong page count, a row for a file
that no longer exists, a ``?`` that nobody listed in the closing comment. It also
checks audit completeness and agreement. When the corpus is absent, structural
and agreement checks still run and digest verification is reported as skipped;
the command never calls that partial result a digest pass.

**Why ``year`` is a column at all.** The corpus holds a KDIGO 2009 document and a
KDIGO 2013 document sitting beside a 2026 AHA one. There is no common release
event across nine societies, so per-document version is the only staleness signal
that exists here. Same reasoning that put ``meta.release`` in
``reference/icd10cm-2026.sqlite``.

**Metadata only.** No extracted body text goes in the catalog, audit, or this
file's output, and the checker never prints document text.

Stdlib for everything except reading the PDFs themselves, which needs ``pypdf``
or ``fitz``. That import is deliberately lazy and confined to ``read_corpus``:
the parsers and the comparison are pure functions over data, so
``test_guidelines_catalog.py`` covers them against committed fixtures without a
PDF or a corpus anywhere in reach.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from console_codec import use_utf8
from guidelines_extract import (
    CLASS_GUIDELINE,
    CLASS_RECOMMENDATION_STATEMENT,
    CLASS_WEB_CAPTURE,
    CLASSES,
    is_recommendation_statement,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
AUDIT = REPO_ROOT / "reference" / "guidelines-catalog-audit.md"
DEFAULT_SRC = Path("C:/codeing/guidelines-src")

COLUMNS = (
    "society",
    "filename",
    "title",
    "topic",
    "population",
    "year",
    "page_count",
    "class",
)

# The only columns that may be left unsettled. ``society``, ``filename`` and
# ``page_count`` are read off the corpus and cannot be in doubt; ``class`` is
# decided by a rule below and falls back to ``guideline`` rather than to ``?``.
NULLABLE = ("title", "topic", "population", "year")

# The four judgment columns ticket #106 requires a second reader to settle.
AUDITED_COLUMNS = NULLABLE

# ``CLASSES`` is imported from ``guidelines_extract`` rather than restated here.
# [#185](https://github.com/mshamblin5150-code/clinical-skills/issues/185): the
# producer owns the vocabulary it emits into ``manifest.json``, which is what the
# index stores and what ``guidelines_search.py --class`` filters on, so an auditor
# holding its own copy can pass a catalog publishing a value the index cannot
# answer -- which is the one failure this column's check exists to catch. Same
# arrangement as ``reference_scan.py`` importing ``docx_write.REFERENCE_HEADING``.

#: The ``class`` row in the *How to read a row* legend, and the backticked values in
#: its second cell. Read out of the file rather than compared against a list typed
#: here: a list goes stale the first time the legend moves and reads as coverage
#: while it does.
#:
#: This is checked as well as every row's cell, and the two catch different things --
#: [#185](https://github.com/mshamblin5150-code/clinical-skills/issues/185). A row
#: carrying a value the index cannot answer is one document unreachable; a **legend**
#: publishing one is an instruction to every reader to ask an unanswerable question,
#: and no row has to be wrong for that to be true.
LEGEND_CLASS_ROW = re.compile(r"^\|\s*`class`\s*\|(?P<values>[^|]*)\|\s*$", re.MULTILINE)
BACKTICKED = re.compile(r"`([^`]+)`")

UNSETTLED = "?"

# The heading the closing comment lives under. Every ``?`` cell in the table has
# to be named here, which is what stops a blank from reading as an answer.
UNSETTLED_HEADING = "## Unsettled cells"

YEAR_RE = re.compile(r"(?:19|20)\d{2}")

# A browser print-to-PDF stamps the page with the moment of capture and the URL
# it came from. The three ACIP files are captures of CDC schedule pages rather
# than guideline documents, and this is how they say so.
CAPTURE_STAMP_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2},\s*\d{1,2}:\d{2}\s*[AP]M\b")
CAPTURE_URL_RE = re.compile(r"https?://\S+")

# Years on these lines date the download, not the document. Every AHA/ACC and
# most IDSA files carry one on every page, so leaving them in makes 2026 the
# apparent publication year of a 2018 guideline.
ACCESS_LINE_RE = re.compile(
    r"downloaded from|by guest on|accessed on|retrieved on|last reviewed", re.I
)

# The recommendation-statement test is ``guidelines_extract.is_recommendation_statement``
# now, with ``TASK_FORCE_MARK``, ``RECOMMENDATION_STATEMENT_MARK`` and ``squash``. All
# four were written here and moved on #185, when the extractor gained the branch that
# needs them: two copies of a rule that must agree is what #253 cost. The reasoning
# they carry moved with them and is not restated here.


@dataclass(frozen=True)
class Row:
    """One catalog row. Every field is a string, including ``page_count`` and
    ``year``, because the committed table is the source of truth and comparing it
    to the corpus should compare what it literally says."""

    society: str
    filename: str
    title: str
    topic: str
    population: str
    year: str
    page_count: str
    cls: str

    @property
    def cells(self) -> dict[str, str]:
        return {
            "society": self.society,
            "filename": self.filename,
            "title": self.title,
            "topic": self.topic,
            "population": self.population,
            "year": self.year,
            "page_count": self.page_count,
            "class": self.cls,
        }

    def unsettled_columns(self) -> list[str]:
        return [c for c, v in self.cells.items() if v == UNSETTLED]


def row_from_cells(cells: list[str]) -> Row:
    """Build a row from one table line's cells, keyed by column name.

    Named rather than positional on purpose: ``render_table`` writes each cell by
    looking its column up in ``Row.cells``, so a positional constructor here
    would let a reordering of ``COLUMNS`` round-trip into silently mis-assigned
    fields rather than into an error. ``class`` is a keyword, so the dataclass
    calls that field ``cls`` and this is the one place the two names meet.
    """
    by_column = dict(zip(COLUMNS, cells, strict=True))
    return Row(cls=by_column.pop("class"), **by_column)


@dataclass(frozen=True)
class Document:
    """What the corpus can say about one PDF without anyone reading it."""

    society: str
    filename: str
    page_count: int
    cls: str
    title_guess: str
    year_guess: str


@dataclass(frozen=True)
class AuditReading:
    """One independent reading of one judgment column."""

    society: str
    filename: str
    column: str
    value: str
    page: str
    evidence: str


@dataclass(frozen=True)
class AuditDocument:
    """The exact corpus document to which an independent reading is bound."""

    society: str
    filename: str
    sha256: str
    audited: str


@dataclass(frozen=True)
class AuditRuling:
    """A clinician-confirmed resolution of one independent-read disagreement."""

    society: str
    filename: str
    column: str
    confirmed_value: str
    confirmed_date: str
    rationale: str


AUDIT_TABLES = {
    "## Documents": ("society", "filename", "sha256", "audited"),
    "## Independent readings": (
        "society",
        "filename",
        "column",
        "value",
        "page",
        "evidence",
    ),
    "## Clinician rulings": (
        "society",
        "filename",
        "column",
        "confirmed_value",
        "confirmed_date",
        "rationale",
    ),
}


def _parse_named_table(
    text: str, heading: str, columns: tuple[str, ...], problems: list[str]
) -> list[list[str]]:
    lines = text.splitlines()
    try:
        heading_at = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        problems.append(f"audit has no {heading!r} table")
        return []
    header_at = next(
        (
            i
            for i in range(heading_at + 1, len(lines))
            if lines[i].lstrip().startswith("|")
        ),
        None,
    )
    if header_at is None or tuple(split_table_row(lines[header_at])) != columns:
        problems.append(f"{heading}: expected columns {columns}")
        return []
    rows: list[list[str]] = []
    for lineno, line in enumerate(lines[header_at + 1 :], start=header_at + 2):
        if not line.lstrip().startswith("|"):
            if rows:
                break
            continue
        cells = split_table_row(line)
        if is_separator_row(cells):
            continue
        if len(cells) != len(columns):
            problems.append(
                f"{heading} line {lineno}: {len(cells)} cells, expected {len(columns)}"
            )
            continue
        rows.append(cells)
    return rows


def parse_audit(
    text: str,
) -> tuple[list[AuditDocument], list[AuditReading], list[AuditRuling], list[str]]:
    """Parse the independent-read ledger by its three named table headings."""
    problems: list[str] = []
    tables = {
        heading: _parse_named_table(text, heading, columns, problems)
        for heading, columns in AUDIT_TABLES.items()
    }
    documents = [AuditDocument(*cells) for cells in tables["## Documents"]]
    readings = [AuditReading(*cells) for cells in tables["## Independent readings"]]
    rulings = [AuditRuling(*cells) for cells in tables["## Clinician rulings"]]
    return documents, readings, rulings, problems


# --------------------------------------------------------------------------
# Parsing the committed catalog
# --------------------------------------------------------------------------


def split_table_row(line: str) -> list[str]:
    """Split one Markdown table line into cells.

    A cell may not contain a raw ``|``; escape it as ``\\|``. Titles do carry
    pipes in the wild — the ACIP captures are titled ``... | Vaccines &
    Immunizations | CDC`` — so this is a real case rather than a hypothetical,
    and a row that gets it wrong shows up as a column-count failure.
    """
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|") and not stripped.endswith(r"\|"):
        stripped = stripped[:-1]
    cells = re.split(r"(?<!\\)\|", stripped)
    return [c.strip().replace(r"\|", "|") for c in cells]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def parse_catalog(text: str) -> tuple[list[Row], dict[str, set[str]], list[str]]:
    """Parse the catalog into rows, the closing comment's unsettled index, and
    any structural complaints found along the way.

    The unsettled index maps filename to the set of column names the closing
    comment declares unsettled for that file.

    The catalog table is found by its header rather than by being the first table
    in the file: the prose above it carries a legend table of its own, and taking
    whichever table came first read that legend as 8 malformed catalog rows.
    """
    problems: list[str] = []
    rows: list[Row] = []

    lines = text.splitlines()
    unsettled_at = next(
        (i for i, l in enumerate(lines) if l.strip() == UNSETTLED_HEADING), len(lines)
    )
    body = lines[:unsettled_at]

    header_at = next(
        (
            i
            for i, line in enumerate(body)
            if line.lstrip().startswith("|")
            and [c.lower() for c in split_table_row(line)] == list(COLUMNS)
        ),
        None,
    )
    if header_at is None:
        problems.append(f"no table headed {list(COLUMNS)} found")
        return rows, parse_unsettled(lines[unsettled_at:], problems), problems

    for lineno, line in enumerate(body[header_at + 1 :], start=header_at + 2):
        if not line.lstrip().startswith("|"):
            break  # the table ends at the first line that is not one
        cells = split_table_row(line)
        if is_separator_row(cells):
            continue
        if len(cells) != len(COLUMNS):
            problems.append(
                f"line {lineno}: {len(cells)} cells, expected {len(COLUMNS)}"
                f" (escape any literal | as \\|): {cells[:2]}"
            )
            continue
        rows.append(row_from_cells(cells))

    unsettled_index = parse_unsettled(lines[unsettled_at:], problems)
    return rows, unsettled_index, problems


# ``- `filename` — `column` — why`` is the closing-comment line shape. The dash
# between fields is an em dash per the repo's punctuation house style, and a
# plain hyphen is accepted so a hand-typed line is not refused over a character.
UNSETTLED_LINE_RE = re.compile(
    r"^\s*[-*]\s*`(?P<filename>[^`]+)`\s*[\u2014-]\s*`(?P<column>[^`]+)`"
)


def parse_unsettled(lines: list[str], problems: list[str]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for line in lines:
        m = UNSETTLED_LINE_RE.match(line)
        if not m:
            continue
        column = m.group("column")
        if column not in NULLABLE:
            problems.append(
                f"closing comment names column {column!r}, which is not one of {NULLABLE}"
            )
            continue
        index.setdefault(m.group("filename"), set()).add(column)
    return index


# --------------------------------------------------------------------------
# Reading the corpus
# --------------------------------------------------------------------------


def classify(pages: list[str]) -> str:
    """Decide the document class from its text.

    Ordered, and the order matters: a browser capture of a page that happens to
    say "recommendation statement" is still a capture.
    """
    if any(CAPTURE_STAMP_RE.search(p) and CAPTURE_URL_RE.search(p) for p in pages[:3]):
        return CLASS_WEB_CAPTURE
    if is_recommendation_statement(pages[0] if pages else ""):
        return CLASS_RECOMMENDATION_STATEMENT
    return CLASS_GUIDELINE


def year_guess(title: str, pages: list[str]) -> str:
    """Guess the publication year, title first.

    Where a society dates its own title — ``2022 AHA/ACC/HFSA Guideline for...``,
    ``KDIGO 2024 Clinical Practice Guideline...`` — that year is the document's
    own answer and beats anything inferred from the page furniture. It matters
    for the AHA/ACC files in particular: a guideline dated 2018 that reached
    print in a 2019 issue carries 2019 on every page, and the running-head rule
    would return the issue.
    """
    in_title = YEAR_RE.findall(title)
    if in_title:
        return in_title[0]
    return year_from_running_head(pages)


def year_from_running_head(pages: list[str], threshold: float = 0.5) -> str:
    """Guess the publication year as the one the document prints on most pages.

    A journal running head or copyright footer repeats the year of the issue on
    every page, which makes it the most-repeated year in the document. Lines that
    stamp a *download* are excluded first, or the answer is the day the corpus was
    collected rather than the day the guideline was published.

    A guess, and named one: ``--check`` never recomputes it.
    """
    if not pages:
        return UNSETTLED
    hits: dict[int, int] = {}
    for page in pages:
        found: set[int] = set()
        for line in page.split("\n"):
            if ACCESS_LINE_RE.search(line):
                continue
            found.update(int(y) for y in YEAR_RE.findall(line))
        for year in found:
            hits[year] = hits.get(year, 0) + 1
    need = max(2, len(pages) * threshold)
    winners = {y: n for y, n in hits.items() if n >= need}
    if not winners:
        return UNSETTLED
    best = max(winners.values())
    # Ties go to the later year. The case for the earlier one — a guideline dated
    # 2018 that reached print in a 2019 issue carries both on every page — never
    # reaches here, because ``year_guess`` takes the title's year first and those
    # documents all date their own titles. What is left is reaffirmations, which
    # print the superseded year as often as the current one: on the four ties in
    # the corpus the later year is right three times (an ATS/IDSA pneumonia
    # guideline, and the USPSTF carotid stenosis and genital herpes
    # reaffirmations) and wrong once, on a five-page ASCO/IDSA reprint carrying an
    # access year this rule does not recognize as one.
    return str(max(y for y, n in winners.items() if n == best))


def title_guess(meta_title: str | None, pages: list[str], filename: str) -> str:
    """Prefer the PDF's own title when it is plausibly a title.

    Producers fill this field with cover-art filenames (``ajt_9_S3-cover``),
    placeholder words (``untitled``, ``Topic``) and InDesign document names, so it
    is taken only when it survives a sniff test. Otherwise the first substantial
    line of the title page is offered as a starting point for curation.
    """
    if meta_title and looks_like_title(meta_title, filename):
        return " ".join(meta_title.split())
    for line in (pages[0] if pages else "").split("\n"):
        line = " ".join(line.split())
        if len(line) >= 25 and " " in line:
            return line
    return UNSETTLED


def looks_like_title(candidate: str, filename: str) -> bool:
    text = " ".join(candidate.split())
    if len(text) < 20 or " " not in text:
        return False
    if text.lower() in {"untitled", "topic", "microsoft word document"}:
        return False
    if re.search(r"\.(indd|docx?|qxd|pdf|tex)\b", text, re.I):
        return False
    if text.lower() == Path(filename).stem.lower():
        return False
    return True


def read_corpus(src: Path) -> list[Document]:
    """Open every PDF under ``src`` and return what can be read without judgment.

    The only place a PDF is touched. ``fitz`` is preferred for speed and falls
    back to ``pypdf``; both are maintainer-only dependencies and neither is
    reachable from anything a consumer of these skills runs.
    """
    extract = _pdf_reader()
    docs: list[Document] = []
    for society_dir in sorted(p for p in src.iterdir() if p.is_dir()):
        for pdf in sorted(society_dir.glob("*.pdf")):
            meta_title, pages = extract(pdf)
            title = title_guess(meta_title, pages, pdf.name)
            docs.append(
                Document(
                    society=society_dir.name,
                    filename=pdf.name,
                    page_count=len(pages),
                    cls=classify(pages),
                    title_guess=title,
                    year_guess=year_guess(title, pages),
                )
            )
    return docs


def _pdf_reader():
    try:
        import fitz  # type: ignore

        def extract(path: Path) -> tuple[str | None, list[str]]:
            with fitz.open(path) as doc:
                meta = (doc.metadata or {}).get("title")
                return meta, [doc[i].get_text() for i in range(doc.page_count)]

        return extract
    except ImportError:
        pass
    try:
        from pypdf import PdfReader  # type: ignore

        def extract(path: Path) -> tuple[str | None, list[str]]:
            reader = PdfReader(str(path))
            meta = (reader.metadata or {}).get("/Title")
            return (str(meta) if meta else None), [p.extract_text() or "" for p in reader.pages]

        return extract
    except ImportError:
        raise SystemExit(
            "reading the corpus needs pypdf or PyMuPDF (fitz). Both are "
            "maintainer-only; --check without a corpus is not supported."
        )


# --------------------------------------------------------------------------
# Checking
# --------------------------------------------------------------------------


def check(
    rows: list[Row], unsettled_index: dict[str, set[str]], docs: list[Document]
) -> list[str]:
    """Compare the committed catalog to the corpus. Returns one string per
    failure, empty when the catalog holds. Reports filenames and column names
    only; no document text passes through here."""
    failures: list[str] = []

    by_filename: dict[str, Row] = {}
    for row in rows:
        if row.filename in by_filename:
            failures.append(f"{row.filename}: appears in more than one row")
            continue
        by_filename[row.filename] = row

    corpus = {d.filename: d for d in docs}

    for missing in sorted(set(corpus) - set(by_filename)):
        failures.append(f"{missing}: in the corpus, missing from the catalog")
    for extra in sorted(set(by_filename) - set(corpus)):
        failures.append(f"{extra}: in the catalog, missing from the corpus")

    for filename in sorted(set(corpus) & set(by_filename)):
        row, doc = by_filename[filename], corpus[filename]
        if row.society != doc.society:
            failures.append(
                f"{filename}: society is {row.society!r}, corpus says {doc.society!r}"
            )
        if row.page_count != str(doc.page_count):
            failures.append(
                f"{filename}: page_count is {row.page_count!r}, corpus says {doc.page_count}"
            )
        if row.cls != doc.cls:
            failures.append(
                f"{filename}: class is {row.cls!r}, corpus says {doc.cls!r}"
            )

    failures.extend(check_shape(rows, unsettled_index))
    return failures


def check_legend(text: str) -> list[str]:
    """The ``class`` legend publishes exactly the vocabulary the index can answer.

    Needs no corpus, which is the point: the artifacts that would otherwise settle this
    -- the 410 MB source corpus, the extracted text, the FTS index -- all live outside
    every checkout and are absent on most machines, so a check that needed them would
    be a check that mostly did not run. Both vocabularies are tracked, one as this
    legend row and one as ``guidelines_extract.CLASSES``.
    """
    match = LEGEND_CLASS_ROW.search(text)
    if match is None:
        return [
            "no `class` row in the column legend, so the vocabulary this file "
            "publishes cannot be read"
        ]
    published = set(BACKTICKED.findall(match.group("values")))
    failures = []
    for extra in sorted(published - set(CLASSES)):
        failures.append(
            f"the legend publishes class {extra!r}, which no document in the index "
            f"can carry, so `guidelines_search.py --class {extra}` cannot be answered"
        )
    for missing in sorted(set(CLASSES) - published):
        failures.append(
            f"the legend omits class {missing!r}, which the index does carry"
        )
    return failures


def check_shape(rows: list[Row], unsettled_index: dict[str, set[str]]) -> list[str]:
    """The checks that need no corpus: legal values, and every ``?`` accounted
    for in the closing comment."""
    failures: list[str] = []
    for row in rows:
        if row.cls not in CLASSES:
            failures.append(f"{row.filename}: class {row.cls!r} is not one of {CLASSES}")
        if row.year != UNSETTLED and not re.fullmatch(r"(?:19|20)\d{2}", row.year):
            failures.append(f"{row.filename}: year {row.year!r} is not a 4-digit year")
        if not re.fullmatch(r"\d+", row.page_count):
            failures.append(f"{row.filename}: page_count {row.page_count!r} is not a number")
        for column, value in row.cells.items():
            if value == UNSETTLED and column not in NULLABLE:
                failures.append(f"{row.filename}: {column} may not be {UNSETTLED}")
            if not value:
                failures.append(f"{row.filename}: {column} is empty")

        declared = unsettled_index.get(row.filename, set())
        actual = set(row.unsettled_columns())
        for column in sorted(actual - declared):
            failures.append(
                f"{row.filename}: {column} is {UNSETTLED} but is not listed under "
                f"{UNSETTLED_HEADING!r}"
            )
        for column in sorted(declared - actual):
            failures.append(
                f"{row.filename}: listed as an unsettled {column}, but the table fills it"
            )

    listed = set(unsettled_index) - {r.filename for r in rows}
    for filename in sorted(listed):
        failures.append(f"{filename}: listed under {UNSETTLED_HEADING!r} with no table row")
    return failures


def check_audit(
    rows: list[Row],
    documents: list[AuditDocument],
    readings: list[AuditReading],
    rulings: list[AuditRuling],
) -> list[str]:
    """Require one independent reading for every judgment cell in every row."""
    failures: list[str] = []
    catalog = {row.filename: row for row in rows}
    audited: dict[str, AuditDocument] = {}
    read: dict[tuple[str, str], AuditReading] = {}
    ruled: dict[tuple[str, str], AuditRuling] = {}

    def valid_date(value: str) -> bool:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return False
        try:
            from datetime import date

            date.fromisoformat(value)
        except ValueError:
            return False
        return True

    for document in documents:
        if document.filename in audited:
            failures.append(
                f"{document.filename}: document audit appears more than once"
            )
        else:
            audited[document.filename] = document
        row = catalog.get(document.filename)
        if row is None:
            failures.append(f"{document.filename}: document audit has no catalog row")
        elif document.society != row.society:
            failures.append(
                f"{document.filename}: document society is {document.society!r}, "
                f"catalog says {row.society!r}"
            )
        if not re.fullmatch(r"[0-9a-f]{64}", document.sha256):
            failures.append(f"{document.filename}: SHA-256 is not 64 lowercase hex digits")
        if not valid_date(document.audited):
            failures.append(f"{document.filename}: audit date is not a valid YYYY-MM-DD")

    for reading in readings:
        key = (reading.filename, reading.column)
        if key in read:
            failures.append(
                f"{reading.filename}: {reading.column} reading appears more than once"
            )
        else:
            read[key] = reading
        row = catalog.get(reading.filename)
        if reading.column not in AUDITED_COLUMNS:
            failures.append(
                f"{reading.filename}: {reading.column!r} is an unknown audit column"
            )
        if row is None:
            failures.append(f"{reading.filename}: independent reading has no catalog row")
        else:
            if reading.society != row.society:
                failures.append(
                    f"{reading.filename}: reading society is {reading.society!r}, "
                    f"catalog says {row.society!r}"
                )
            page_count = int(row.page_count) if row.page_count.isdigit() else 0
            if not reading.page.isdigit() or not 1 <= int(reading.page) <= page_count:
                failures.append(
                    f"{reading.filename}: {reading.column} page {reading.page!r} "
                    f"is not within 1..{page_count}"
                )
        if not reading.value:
            failures.append(f"{reading.filename}: {reading.column} reading is empty")
        if not reading.evidence:
            failures.append(f"{reading.filename}: {reading.column} evidence is empty")

    for ruling in rulings:
        key = (ruling.filename, ruling.column)
        if key in ruled:
            failures.append(
                f"{ruling.filename}: {ruling.column} ruling appears more than once"
            )
        else:
            ruled[key] = ruling
        row = catalog.get(ruling.filename)
        if ruling.column not in AUDITED_COLUMNS:
            failures.append(
                f"{ruling.filename}: {ruling.column!r} is an unknown ruling column"
            )
        if row is None:
            failures.append(f"{ruling.filename}: clinician ruling has no catalog row")
        elif ruling.society != row.society:
            failures.append(
                f"{ruling.filename}: ruling society is {ruling.society!r}, "
                f"catalog says {row.society!r}"
            )
        if not ruling.confirmed_value:
            failures.append(f"{ruling.filename}: {ruling.column} confirmed value is empty")
        if not valid_date(ruling.confirmed_date):
            failures.append(
                f"{ruling.filename}: {ruling.column} ruling date is not a valid YYYY-MM-DD"
            )
        if not ruling.rationale:
            failures.append(f"{ruling.filename}: {ruling.column} ruling rationale is empty")

    for row in rows:
        if row.filename not in audited:
            failures.append(f"{row.filename}: has no document audit")
        for column in AUDITED_COLUMNS:
            key = (row.filename, column)
            if key not in read:
                failures.append(
                    f"{row.filename}: {column} has no independent reading"
                )
                continue
            disagrees = read[key].value != row.cells[column]
            if not disagrees and key in ruled:
                failures.append(
                    f"{row.filename}: {column} ruling exists without a disagreement"
                )
            elif disagrees and (
                key not in ruled or ruled[key].confirmed_value != row.cells[column]
            ):
                failures.append(
                    f"{row.filename}: {column} disagrees between the catalog and "
                    "the independent reading"
                )
    return failures


def check_audit_digests(
    documents: list[AuditDocument], digests: dict[tuple[str, str], str]
) -> list[str]:
    """Bind every completed audit to the exact PDF bytes that were read."""
    failures: list[str] = []
    for document in documents:
        key = (document.society, document.filename)
        if key not in digests:
            failures.append(
                f"{document.filename}: missing from the corpus digest scan"
            )
        elif digests[key] != document.sha256:
            failures.append(
                f"{document.filename}: SHA-256 disagrees with the audited document"
            )
    audited = {(document.society, document.filename) for document in documents}
    for _, filename in sorted(set(digests) - audited):
        failures.append(f"{filename}: in the corpus digest scan without a document audit")
    return failures


# --------------------------------------------------------------------------
# Drafting
# --------------------------------------------------------------------------


def escape_cell(value: str) -> str:
    return value.replace("|", r"\|")


def render_table(rows: list[Row]) -> str:
    out = ["| " + " | ".join(COLUMNS) + " |", "| " + " | ".join("---" for _ in COLUMNS) + " |"]
    for row in rows:
        out.append("| " + " | ".join(escape_cell(row.cells[c]) for c in COLUMNS) + " |")
    return "\n".join(out)


def _render_markdown_table(columns: tuple[str, ...], rows: list[list[str]]) -> str:
    out = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    out.extend(
        "| " + " | ".join(escape_cell(value) for value in row) + " |"
        for row in rows
    )
    return "\n".join(out)


def scan_audit_documents(src: Path) -> list[AuditDocument]:
    """Read only corpus filenames and bytes; never open or interpret a PDF."""
    documents: list[AuditDocument] = []
    for society_dir in sorted(path for path in src.iterdir() if path.is_dir()):
        for pdf in sorted(society_dir.glob("*.pdf")):
            digest = hashlib.sha256()
            with pdf.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            documents.append(
                AuditDocument(
                    society=society_dir.name,
                    filename=pdf.name,
                    sha256=digest.hexdigest(),
                    audited=UNSETTLED,
                )
            )
    return documents


def render_audit_draft(docs: list[AuditDocument]) -> str:
    """Emit a blind worksheet containing identity and no judgment values."""
    document_rows = [
        [d.society, d.filename, d.sha256, d.audited]
        for d in docs
    ]
    reading_rows = [
        [d.society, d.filename, column, UNSETTLED, UNSETTLED, UNSETTLED]
        for d in docs
        for column in AUDITED_COLUMNS
    ]
    return "\n\n".join(
        [
            "# Guideline catalog independent audit",
            "## Documents\n\n"
            + _render_markdown_table(AUDIT_TABLES["## Documents"], document_rows),
            "## Independent readings\n\n"
            + _render_markdown_table(
                AUDIT_TABLES["## Independent readings"], reading_rows
            ),
            "## Clinician rulings\n\n"
            + _render_markdown_table(AUDIT_TABLES["## Clinician rulings"], []),
        ]
    )


def draft_rows(docs: list[Document]) -> list[Row]:
    return [
        Row(
            society=d.society,
            filename=d.filename,
            title=d.title_guess,
            topic=UNSETTLED,
            population=UNSETTLED,
            year=d.year_guess,
            page_count=str(d.page_count),
            cls=d.cls,
        )
        for d in docs
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0], allow_abbrev=False
    )
    parser.add_argument(
        "--draft",
        metavar="SRC",
        nargs="?",
        const=str(DEFAULT_SRC),
        help="emit a scaffold table read from the corpus at SRC instead of checking",
    )
    parser.add_argument(
        "--audit-draft",
        metavar="SRC",
        help="emit a blind independent-audit worksheet from corpus file identity",
    )
    parser.add_argument(
        "--src",
        default=str(DEFAULT_SRC),
        help=f"corpus directory to check against (default {DEFAULT_SRC})",
    )
    parser.add_argument(
        "--catalog",
        default=str(CATALOG),
        help=f"catalog to check (default {CATALOG})",
    )
    parser.add_argument(
        "--audit",
        default=str(AUDIT),
        help=f"independent audit ledger to check (default {AUDIT})",
    )
    args = parser.parse_args(argv)

    if args.audit_draft:
        src = Path(args.audit_draft)
        if not src.is_dir():
            print(f"no corpus at {src}", file=sys.stderr)
            return 2
        print(render_audit_draft(scan_audit_documents(src)))
        return 0

    if args.draft:
        src = Path(args.draft)
        if not src.is_dir():
            print(f"no corpus at {src}", file=sys.stderr)
            return 2
        print(render_table(draft_rows(read_corpus(src))))
        return 0

    catalog_path = Path(args.catalog)
    if not catalog_path.exists():
        print(f"no catalog at {catalog_path}", file=sys.stderr)
        return 2
    text = catalog_path.read_text(encoding="utf-8")
    rows, unsettled_index, problems = parse_catalog(text)
    problems = problems + check_legend(text)

    audit_path = Path(args.audit)
    if not audit_path.exists():
        print(f"no independent audit at {audit_path}", file=sys.stderr)
        return 2
    audit_text = audit_path.read_text(encoding="utf-8")
    audit_documents, readings, rulings, audit_problems = parse_audit(audit_text)
    problems = problems + audit_problems
    audit_failures = check_audit(rows, audit_documents, readings, rulings)

    src = Path(args.src)
    if src.is_dir():
        corpus_audits = scan_audit_documents(src)
        digests = {
            (document.society, document.filename): document.sha256
            for document in corpus_audits
        }
        failures = (
            problems
            + check(rows, unsettled_index, read_corpus(src))
            + audit_failures
            + check_audit_digests(audit_documents, digests)
        )
        scope = f"{len(rows)} row(s) against {src}"
        digest_status = f"verified {len(audit_documents)} document digest(s)"
    else:
        failures = problems + check_shape(rows, unsettled_index) + audit_failures
        scope = f"{len(rows)} row(s), shape only (no corpus at {src})"
        digest_status = "SKIPPED document digest verification: corpus unavailable"

    print(f"guidelines catalog: {scope}")
    print(f"  {digest_status}")
    for failure in failures:
        print(f"  FAIL {failure}")
    if failures:
        print(f"\n{len(failures)} failure(s).")
        return 1
    print("  ok")
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
