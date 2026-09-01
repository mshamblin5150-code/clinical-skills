"""Print a threshold-sheet skeleton for one catalog topic.

The committed Markdown remains curated source of truth. This command only lifts
machine-settleable citation cells from recommendation records and prints them to
stdout; it never writes a sheet.

A bound source deliberately drafts blank snippets. The sheet's structure gate then
refuses every row until a reader fills those cells from the rendered source pages;
that non-zero result on a fresh bound scaffold is the required workflow, not a
broken draft.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import guidelines_catalog
import guidelines_extract
import threshold_coverage
from console_codec import use_utf8
from guidelines_recs import (
    RECS_PREFIX,
    RecommendationRecordLocation,
    UntrustedRecommendationRecord,
    locate_recommendation_record,
    load_recommendation_record,
    peek_recommendation_source,
    record_built_from_another_document,
    source_filename_matches_document,
)
from threshold_sheet import (
    CONFLICTS_HEADING,
    COVERAGE_HEADING,
    DEFAULT_PDF_ROOT,
    DEFAULT_RECS_ALIAS,
    DEFAULT_RECS_ROOT,
    ExtractionIdentity,
    NARRATIVE_KIND,
    POPULATIONS_HEADING,
    QUANTITIES_HEADING,
    ROW_COLUMNS,
    SOURCE_COLUMNS,
    RECS_ALIAS_ENV,
    SCHEMA_MARKER,
    Sheet,
    SCOPE_HEADING,
    SECTION_HEADINGS,
    SOURCES_HEADING,
    THRESHOLDS_HEADING,
    _normalize,
    extraction_identity_from_manifest,
    parse,
    render_extraction_identity,
    source_locator,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
DEFAULT_COVERAGE = REPO_ROOT / "reference" / "thresholds" / "coverage.md"
DEFAULT_SHEET_ROOT = REPO_ROOT / "reference" / "thresholds"

NEARBY_REPORT_BOUND = (
    "This list is bounded. A catalog row is reported only where one of the "
    "drafted topic's ruled subject names appears in that row's topic or title; "
    "{ruled_cell_count} of the catalog's {catalog_topic_count} topics has a "
    "subject ruling. {subject_status}"
)

# Deliberately no --allow-untrusted-provenance: this command turns a transient
# record into prose a person can curate into a committed sheet, erasing the origin
# of any accepted distrust. ADR 0030 ruling 6 forbids that laundering path.


@dataclass(frozen=True)
class Source:
    key: str
    society: str
    document: str
    source_class: str
    version: str
    published: str
    download_address: str
    download_basis: str
    mode: str
    record: dict
    record_location: RecommendationRecordLocation


@dataclass(frozen=True)
class DraftRow:
    snippet: str
    source: str
    page: str
    rec: str
    klass: str


def _normalized_topic(value: str) -> str:
    return " ".join(value.casefold().replace("-", " ").split())


def _registry_topic(
    value: str, entries: list[threshold_coverage.Entry]
) -> str:
    """Resolve a typed catalog topic or its one registered sheet filename."""
    normalized = _normalized_topic(value)
    for entry in entries:
        artifact_name = _normalized_topic(Path(entry.artifact).stem)
        if entry.artifact and artifact_name == normalized:
            return _normalized_topic(entry.topic)
    for entry in entries:
        if _normalized_topic(entry.topic) == normalized:
            return _normalized_topic(entry.topic)
    return normalized


def _subject_report_names(
    topic: str, entries: list[threshold_coverage.Entry]
) -> tuple[frozenset[str], bool]:
    entry = next(
        (item for item in entries if _normalized_topic(item.topic) == topic), None
    )
    if entry is None or entry.subject == "?":
        return frozenset((topic,)), False
    topics = [item.topic for item in entries]
    subject_keys = {
        _normalized_topic(subject)
        for subject in threshold_coverage.parse_subject_cell(entry.subject, topics) or ()
    }
    names = {
        _normalized_topic(item.topic)
        for item in entries
        if item.subject != "?"
        and subject_keys
        & {
            _normalized_topic(subject)
            for subject in threshold_coverage.parse_subject_cell(item.subject, topics) or ()
        }
    }
    return frozenset(names or (topic,)), True


def _source_key(row: guidelines_catalog.Row) -> str:
    society = re.sub(r"[^a-z0-9]+", "-", row.society.casefold()).strip("-")
    return f"{society.split('-', 1)[0]}-{row.year}"


def _source_keys(rows: list[guidelines_catalog.Row]) -> dict[guidelines_catalog.Row, str]:
    bases = [_source_key(row) for row in rows]
    counts = Counter(bases)
    keys: dict[guidelines_catalog.Row, str] = {}
    for row, base in zip(rows, bases, strict=True):
        if counts[base] == 1:
            keys[row] = base
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", Path(row.filename).stem.casefold()).strip("-")
        digest = hashlib.sha256(row.filename.casefold().encode("utf-8")).hexdigest()[:6]
        keys[row] = f"{base}-{slug[:32]}-{digest}"
    return keys


def _document(row: guidelines_catalog.Row) -> str:
    return f"{row.society}/{Path(row.filename).stem}"


def _load_record(path: Path) -> dict:
    try:
        return load_recommendation_record(path, require_source_pdf=True)
    except UntrustedRecommendationRecord as error:
        raise ValueError(
            f"untrusted recommendation record {path}: {'; '.join(error.reasons)}"
        ) from error


def _record_path(recs_root: Path, key: str) -> Path:
    return recs_root / f"{RECS_PREFIX}{key}.json"


def _record_hint_errors(recs_root: Path, key: str, document: str) -> list[str]:
    """Describe the lookup root after exact-name resolution has refused."""
    candidates = sorted(recs_root.glob("*.json"))
    record_count = 0
    messages: list[str] = []
    for candidate in candidates:
        try:
            built_from = peek_recommendation_source(candidate)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            if candidate.name.startswith(RECS_PREFIX):
                messages.append(f"{candidate}: would not parse: {error}")
            continue
        except ValueError:
            if candidate.name.startswith(RECS_PREFIX):
                messages.append(
                    f"{candidate}: parsed and is not a recommendation record"
                )
            continue
        record_count += 1
        if source_filename_matches_document(built_from, document):
            messages.append(
                f"{candidate}: built from {built_from}; rename this to "
                f"{RECS_PREFIX}{key}.json"
            )
    messages.append(
        f"scanned {len(candidates)}, {record_count} recommendation records, "
        f"{len(candidates) - record_count} not"
    )
    return messages


def _stated_citation_download_address(citation: str) -> str:
    if guidelines_catalog.DOI_RE.fullmatch(citation):
        return f"https://doi.org/{citation}"
    if re.fullmatch(r"https?://\S+", citation):
        return citation
    return ""


def resolve_sources(
    topic: str,
    catalog_path: Path,
    recs_root: Path,
    seeded_sheet: Sheet | None,
    recs_alias: Path | None = None,
    registry_entries: list[threshold_coverage.Entry] | None = None,
) -> tuple[list[Source], list[str], list[str], int, int, bool]:
    catalog_rows, _, problems = guidelines_catalog.parse_catalog(
        catalog_path.read_text(encoding="utf-8")
    )
    if problems:
        return [], [], problems, 0, 0

    registry_entries = registry_entries or []
    wanted = _registry_topic(topic, registry_entries)
    candidates = [
        row for row in catalog_rows if _normalized_topic(row.topic) == wanted
    ]
    report_names, subject_ruled = _subject_report_names(wanted, registry_entries)
    seeded_sources = seeded_sheet.sources if seeded_sheet else {}
    seeded_documents = {
        source.get("document", "").casefold()
        for source in seeded_sources.values()
    }
    nearby = [
        row
        for row in catalog_rows
        if row not in candidates
        and _document(row).casefold() not in seeded_documents
        and any(
            name and name in f"{row.topic} {row.title}".casefold()
            for name in report_names
        )
    ]
    source_keys = _source_keys(candidates)
    sources: list[Source] = []
    rejected = [
        f"{row.society}/{row.filename}: catalog topic is '{row.topic}', not '{wanted}'"
        for row in nearby
    ]
    errors: list[str] = []
    for row in candidates:
        document = _document(row)
        seeded = next(
            (
                (key, source)
                for key, source in seeded_sources.items()
                if source.get("document", "").casefold() == document.casefold()
            ),
            None,
        )
        key = seeded[0] if seeded else source_keys[row]
        location = locate_recommendation_record(
            document=document,
            key=key,
            recs_alias=recs_alias,
            recs_root=recs_root,
            corpus_documents={_document(item) for item in catalog_rows},
        )
        record_path = location.path
        if record_path is None or not record_path.is_file():
            errors.append(f"{row.society}/{row.filename}: {location.description}")
            errors.extend(_record_hint_errors(recs_root, key, row.filename))
            continue
        try:
            record = _load_record(record_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(
                f"{row.society}/{row.filename}: {location.description}: {error}"
            )
            errors.extend(_record_hint_errors(recs_root, key, row.filename))
            continue
        built_from = record_built_from_another_document(record, row.filename)
        if built_from:
            errors.append(
                f"{row.society}/{row.filename}: {location.description}: "
                f"recommendation record {record_path} "
                f"was built from {built_from}"
            )
            errors.extend(_record_hint_errors(recs_root, key, row.filename))
            continue
        metadata = seeded[1] if seeded else {}
        stated_download_address = _stated_citation_download_address(row.citation)
        download_address = metadata.get("url") or stated_download_address or "?"
        download_basis = metadata.get("basis") or (
            "stated" if stated_download_address else "?"
        )
        sources.append(
            Source(
                key=key,
                society=metadata.get("society", row.society),
                document=metadata.get("document", document),
                source_class=row.cls,
                version=metadata.get("version", row.year),
                published=metadata.get("published", row.year),
                download_address=download_address,
                download_basis=download_basis,
                mode=str(record.get("mode") or metadata.get("mode", "")),
                record=record,
                record_location=location,
            )
        )
    if not candidates:
        errors.append(f"no catalog row has topic '{wanted}'")
    ruled_cell_count = sum(entry.subject != "?" for entry in registry_entries)
    catalog_topic_count = len(
        {_normalized_topic(row.topic) for row in catalog_rows}
    )
    return (
        sources,
        rejected,
        errors,
        ruled_cell_count,
        catalog_topic_count,
        subject_ruled,
    )


def _recommendations(sources: list[Source]) -> dict[tuple[str, str], dict]:
    return {
        (source.key, str(item["rec_id"])): item
        for source in sources
        for item in source.record.get("recommendations", [])
        if isinstance(item, dict) and item.get("rec_id")
    }


def select_rows(
    sources: list[Source], seeded_sheet: Sheet | None
) -> tuple[list[DraftRow], dict[str, str], list[str]]:
    known = _recommendations(sources)
    rejected: list[str] = []
    if seeded_sheet is None:
        rows = [
            DraftRow(
                snippet=(
                    ""
                    if source.mode == "bound"
                    else " ".join(str(item.get("text") or "").split())
                ),
                source=source.key,
                page=f"p{item.get('page', '')}",
                rec=str(item["rec_id"]),
                klass=str(item.get("cor") or ""),
            )
            for source in sources
            for item in source.record.get("recommendations", [])
            if isinstance(item, dict) and item.get("rec_id")
        ]
        return rows, {}, rejected

    rows: list[DraftRow] = []
    modes = {source.key: source.mode for source in sources}
    for row in seeded_sheet.rows:
        item = known.get((row.source, row.rec))
        locator = source_locator(row.rec)
        is_narrative = (
            locator is not None
            and locator.is_narrative
            and row.klass.strip().casefold() == NARRATIVE_KIND
        )
        if modes.get(row.source) == "bound" or is_narrative:
            rows.append(
                DraftRow(
                    snippet=row.snippet,
                    source=row.source,
                    page=f"p{row.page or ''}",
                    rec=row.rec,
                    klass=row.klass,
                )
            )
            continue
        if item is None:
            rejected.append(f"{row.source}/{row.rec}: not in its recommendation record")
            continue
        record_text = " ".join(str(item.get("text") or "").split())
        if _normalize(row.snippet) not in _normalize(record_text):
            rejected.append(f"{row.source}/{row.rec}: seeded snippet is not in its record")
            continue
        rows.append(
            DraftRow(
                snippet=row.snippet,
                source=row.source,
                page=f"p{item.get('page', '')}",
                rec=row.rec,
                klass=str(item.get("cor") or ""),
            )
        )
    return rows, dict(seeded_sheet.scoped_out), rejected


def _table(columns: tuple[str, ...], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render(
    topic: str,
    sources: list[Source],
    rows: list[DraftRow],
    scoped_out: dict[str, str],
    rejected: list[str],
    extraction_identity: ExtractionIdentity,
    ruled_cell_count: int,
    catalog_topic_count: int,
    subject_ruled: bool,
    subject_topic: str,
) -> str:
    known = _recommendations(sources)
    cited = {row.rec for row in rows}
    has_bound_source = any(source.mode == "bound" for source in sources)
    candidate_columns = (
        ("source", "rec", "page", "class", "label")
        if has_bound_source
        else ("source", "rec", "page", "class")
    )
    candidate_rows = []
    for (source, rec), item in known.items():
        candidate = [source, rec, f"p{item.get('page', '')}", str(item.get("cor") or "")]
        if has_bound_source:
            candidate.append(" ".join(str(item.get("text") or "").split()))
        candidate_rows.append(candidate)
    source_rows = [
        [
            source.key,
            source.society,
            source.document,
            source.source_class,
            source.version,
            source.published,
            source.download_address,
            source.download_basis,
            source.mode,
        ]
        for source in sources
    ]
    threshold_rows = [
        ["", "", "", f'"{row.snippet}"', row.source, row.page, row.rec, row.klass]
        for row in rows
    ]
    rejected_rows = [[rec, reason] for rec, reason in scoped_out.items()]
    rejected_rows.extend([["candidate", reason] for reason in rejected])

    sections = [
        f"# {topic.title()} — threshold sheet draft",
        SCHEMA_MARKER,
        "Machine-owned citation cells are filled; quantity, population, and value are blank for a reader.",
        "## Candidate set\n\n"
        + _table(candidate_columns, candidate_rows),
        SOURCES_HEADING
        + "\n\n"
        + _table(
            SOURCE_COLUMNS,
            source_rows,
        ),
        SCOPE_HEADING
        + "\n\n"
        + _table(
            ("candidate recommendations", "cited recommendations", "rejected recommendations"),
            [[str(len(known)), str(len(cited)), str(len(scoped_out))]],
        )
        + "\n\n"
        + render_extraction_identity(extraction_identity),
        POPULATIONS_HEADING + "\n\n" + _table(("key", "verbatim"), []),
        QUANTITIES_HEADING + "\n\n" + _table(("key", "verbatim"), []),
        THRESHOLDS_HEADING + "\n\n" + _table(ROW_COLUMNS, threshold_rows),
        CONFLICTS_HEADING,
        COVERAGE_HEADING
        + "\n\n"
        + "\n".join(f"- `{rec}` - {reason}" for rec, reason in scoped_out.items()),
        "## Rejected candidates\n\n"
        + NEARBY_REPORT_BOUND.format(
            ruled_cell_count=ruled_cell_count,
            catalog_topic_count=catalog_topic_count,
            subject_status=(
                "An empty list is not a checked topic join."
                if subject_ruled
                else f"The subject for '{subject_topic}' is unruled (`?`), so an empty list "
                "does not mean nothing further to consider."
            ),
        )
        + "\n\n"
        + _table(("candidate", "reason"), rejected_rows),
    ]
    if has_bound_source:
        sections.insert(
            3,
            "A drafted bound sheet intentionally fails structure until a page read fills every blank snippet.",
        )
    return "\n\n".join(sections).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    parser.add_argument("topic")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument(
        "--recs-root",
        type=Path,
        default=Path(os.environ.get("CLINICAL_GUIDELINES_RECS", DEFAULT_RECS_ROOT)),
    )
    parser.add_argument(
        "--recs-alias",
        type=Path,
        default=Path(
            os.environ.get(RECS_ALIAS_ENV, DEFAULT_RECS_ALIAS)
        ),
        help=(
            "published sweep alias containing <doc_id>.json records; "
            f"defaults from {RECS_ALIAS_ENV}"
        ),
    )
    parser.add_argument("--sheet-root", type=Path, default=DEFAULT_SHEET_ROOT)
    parser.add_argument(
        "--text-root",
        type=Path,
        default=(
            Path(os.environ["CLINICAL_GUIDELINES_TEXT"])
            if os.environ.get("CLINICAL_GUIDELINES_TEXT")
            else guidelines_extract.default_output(DEFAULT_PDF_ROOT)
        ),
        help="extracted corpus whose manifest supplies the draft's identity",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Importing the tuple is an executable assertion that the draft and auditor share
    # one section vocabulary rather than two lists that can drift independently.
    if len(SECTION_HEADINGS) != 7:
        print("threshold-sheet section interface is incomplete", file=sys.stderr)
        return 2
    try:
        registry_entries, registry_problems = threshold_coverage.parse_registry(
            args.coverage.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError) as error:
        print(
            "threshold coverage registry cannot be read: "
            f"{error}; run python tools/threshold_coverage.py",
            file=sys.stderr,
        )
        return 2
    if registry_problems:
        print(
            "threshold coverage registry cannot be read: "
            f"{'; '.join(registry_problems)}; run python tools/threshold_coverage.py",
            file=sys.stderr,
        )
        return 2
    seed_path = args.sheet_root / f"{args.topic.casefold().replace(' ', '-')}.md"
    subject_topic = _registry_topic(args.topic, registry_entries)
    seed_text = seed_path.read_text(encoding="utf-8") if seed_path.is_file() else None
    seeded_sheet = parse(seed_text, seed_path) if seed_text is not None else None
    if seeded_sheet is not None and not seeded_sheet.ok:
        print(f"existing sheet cannot seed the draft: {seeded_sheet.why_not}", file=sys.stderr)
        return 2
    try:
        (
            sources,
            source_rejections,
            source_errors,
            ruled_cell_count,
            catalog_topic_count,
            subject_ruled,
        ) = resolve_sources(
            args.topic,
            args.catalog,
            args.recs_root,
            seeded_sheet,
            args.recs_alias,
            registry_entries,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 2
    rows, scoped_out, row_rejections = select_rows(sources, seeded_sheet)
    rejected = source_rejections + source_errors + row_rejections
    extraction_identity, identity_problems = extraction_identity_from_manifest(args.text_root)
    if extraction_identity is None:
        for problem in identity_problems:
            print(problem, file=sys.stderr)
        return 2
    print(
        render(
            args.topic,
            sources,
            rows,
            scoped_out,
            rejected,
            extraction_identity,
            ruled_cell_count,
            catalog_topic_count,
            subject_ruled,
            subject_topic,
        ),
        end="",
    )
    for source in sources:
        print(
            f"RECOMMENDATION RECORD source '{source.key}' -- "
            f"{source.record_location.description}",
            file=sys.stderr,
        )
    if source_errors or row_rejections:
        for reason in source_errors + row_rejections:
            print(f"REJECTED: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
