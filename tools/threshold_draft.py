"""Print a threshold-sheet skeleton for one catalog topic.

The committed Markdown remains curated source of truth. This command only lifts
machine-settleable citation cells from recommendation records and prints them to
stdout; it never writes a sheet.
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
from urllib.parse import quote

import guidelines_catalog
from console_codec import use_utf8
from threshold_sheet import (
    CONFLICTS_HEADING,
    COVERAGE_HEADING,
    DEFAULT_RECS_ROOT,
    POPULATIONS_HEADING,
    ROW_COLUMNS,
    SCHEMA_MARKER,
    Sheet,
    SCOPE_HEADING,
    SECTION_HEADINGS,
    SOURCES_HEADING,
    THRESHOLDS_HEADING,
    _normalize,
    parse,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"
DEFAULT_SHEET_ROOT = REPO_ROOT / "reference" / "thresholds"

# The catalog uses the guideline's wording while the clinician names the clinical
# topic. This is a vocabulary bridge, not a fuzzy match: a request for hypertension
# must not silently absorb the separate "hypertension screening" topic.
TOPIC_ALIASES = {"hypertension": "high blood pressure"}


@dataclass(frozen=True)
class Source:
    key: str
    society: str
    document: str
    version: str
    published: str
    url: str
    mode: str
    record: dict


@dataclass(frozen=True)
class DraftRow:
    snippet: str
    source: str
    page: str
    rec: str
    klass: str


def _topic(value: str) -> str:
    normalized = " ".join(value.casefold().replace("-", " ").split())
    return TOPIC_ALIASES.get(normalized, normalized)


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
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or not isinstance(loaded.get("recommendations"), list):
        raise ValueError(f"{path} is not a recommendation record")
    return loaded


def _record_path(recs_root: Path, key: str, catalog_row: guidelines_catalog.Row) -> Path:
    expected = recs_root / f"recs-{key}.json"
    if expected.is_file():
        try:
            record = _load_record(expected)
        except (OSError, ValueError, json.JSONDecodeError):
            pass
        else:
            built_from = Path(str(record.get("source") or "").replace("\\", "/")).name
            if built_from.casefold() == catalog_row.filename.casefold():
                return expected

    filename = catalog_row.filename.casefold()
    matches: list[Path] = []
    for candidate in sorted(recs_root.glob("recs-*.json")):
        try:
            record = _load_record(candidate)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        built_from = Path(str(record.get("source") or "").replace("\\", "/")).name
        if built_from.casefold() == filename:
            matches.append(candidate)
    if matches:
        return matches[0]
    return expected


def _record_locator(record: dict) -> str:
    raw = str(record.get("source") or "").replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", raw):
        return "file:///" + quote(raw, safe="/:")
    if raw.startswith("/"):
        return "file://" + quote(raw, safe="/")
    return ""


def resolve_sources(
    topic: str,
    catalog_path: Path,
    recs_root: Path,
    seeded_sheet: Sheet | None,
) -> tuple[list[Source], list[str], list[str]]:
    catalog_rows, _, problems = guidelines_catalog.parse_catalog(
        catalog_path.read_text(encoding="utf-8")
    )
    if problems:
        return [], [], problems

    wanted = _topic(topic)
    candidates = [row for row in catalog_rows if _topic(row.topic) == wanted]
    raw_topic = " ".join(topic.casefold().replace("-", " ").split())
    nearby = [
        row
        for row in catalog_rows
        if row not in candidates
        and raw_topic
        and raw_topic in f"{row.topic} {row.title}".casefold()
    ]
    seeded_sources = seeded_sheet.sources if seeded_sheet else {}
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
        record_path = _record_path(recs_root, key, row)
        if not record_path.is_file():
            errors.append(f"{row.society}/{row.filename}: no recommendation record at {record_path}")
            continue
        try:
            record = _load_record(record_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{row.society}/{row.filename}: {error}")
            continue
        metadata = seeded[1] if seeded else {}
        url = metadata.get("url") or _record_locator(record)
        if not url:
            errors.append(
                f"{row.society}/{row.filename}: recommendation record carries no source locator"
            )
            continue
        sources.append(
            Source(
                key=key,
                society=metadata.get("society", row.society),
                document=metadata.get("document", document),
                version=metadata.get("version", row.year),
                published=metadata.get("published", row.year),
                url=url,
                mode=str(record.get("mode") or metadata.get("mode", "")),
                record=record,
            )
        )
    if not candidates:
        errors.append(f"no catalog row has topic '{wanted}'")
    return sources, rejected, errors


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
                snippet=" ".join(str(item.get("text") or "").split()),
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
    for row in seeded_sheet.rows:
        item = known.get((row.source, row.rec))
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
) -> str:
    known = _recommendations(sources)
    cited = {row.rec for row in rows}
    candidate_rows = [
        [source, rec, f"p{item.get('page', '')}", str(item.get("cor") or "")]
        for (source, rec), item in known.items()
    ]
    source_rows = [
        [
            source.key,
            source.society,
            source.document,
            source.version,
            source.published,
            source.url,
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
        "## Candidate set\n\n" + _table(("source", "rec", "page", "class"), candidate_rows),
        SOURCES_HEADING
        + "\n\n"
        + _table(
            ("key", "society", "document", "version", "published", "url", "mode"),
            source_rows,
        ),
        SCOPE_HEADING
        + "\n\n"
        + _table(
            ("candidate recommendations", "cited recommendations", "rejected recommendations"),
            [[str(len(known)), str(len(cited)), str(len(scoped_out))]],
        ),
        POPULATIONS_HEADING + "\n\n" + _table(("key", "verbatim"), []),
        THRESHOLDS_HEADING + "\n\n" + _table(ROW_COLUMNS, threshold_rows),
        CONFLICTS_HEADING,
        COVERAGE_HEADING
        + "\n\n"
        + "\n".join(f"- `{rec}` - {reason}" for rec, reason in scoped_out.items()),
        "## Rejected candidates\n\n" + _table(("candidate", "reason"), rejected_rows),
    ]
    return "\n\n".join(sections).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    parser.add_argument("topic")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--recs-root",
        type=Path,
        default=Path(os.environ.get("CLINICAL_GUIDELINES_RECS", DEFAULT_RECS_ROOT)),
    )
    parser.add_argument("--sheet-root", type=Path, default=DEFAULT_SHEET_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Importing the tuple is an executable assertion that the draft and auditor share
    # one section vocabulary rather than two lists that can drift independently.
    if len(SECTION_HEADINGS) != 6:
        print("threshold-sheet section interface is incomplete", file=sys.stderr)
        return 2
    seed_path = args.sheet_root / f"{args.topic.casefold().replace(' ', '-')}.md"
    seed_text = seed_path.read_text(encoding="utf-8") if seed_path.is_file() else None
    seeded_sheet = parse(seed_text, seed_path) if seed_text is not None else None
    if seeded_sheet is not None and not seeded_sheet.ok:
        print(f"existing sheet cannot seed the draft: {seeded_sheet.why_not}", file=sys.stderr)
        return 2
    try:
        sources, source_rejections, source_errors = resolve_sources(
            args.topic, args.catalog, args.recs_root, seeded_sheet
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 2
    rows, scoped_out, row_rejections = select_rows(sources, seeded_sheet)
    rejected = source_rejections + source_errors + row_rejections
    print(render(args.topic, sources, rows, scoped_out, rejected), end="")
    if source_errors or row_rejections:
        for reason in source_errors + row_rejections:
            print(f"REJECTED: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
