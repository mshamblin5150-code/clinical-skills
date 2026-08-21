"""Own the extracted-guideline manifest contract shared by producers and readers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

import artifact_lock
import artifact_provenance


MANIFEST_NAME = "manifest.json"


@dataclass(frozen=True)
class Document:
    """The fields every usable manifest document must carry."""

    doc_id: str
    society: str | None = None
    title: str | None = None
    source: str = ""
    output: str | None = None
    document_class: str = "unknown"
    pages: int = 0
    boilerplate: list[str] = field(default_factory=list)
    margin_stripped: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Record(Document):
    """A producer record: the shared fields plus its human-readable audit trail."""

    empty_pages: int = 0
    chars: int = 0
    chars_stripped: int = 0
    sampled_pages: int = 0
    codec: str = "utf-8"
    margin_patterns: list[str] = field(default_factory=list)
    year_page_counts: dict[str, int] = field(default_factory=dict)
    symbol_glyphs: dict[str, int] = field(default_factory=dict)
    error: str | None = None


# Dataclass inheritance groups the consumer fields before the audit fields. That is
# a useful in-memory shape but not the artifact format: this order preserves the
# bytes emitted before #407, because those bytes key the extraction build cache.
SERIALISED_ORDER = (
    "doc_id",
    "society",
    "title",
    "source",
    "output",
    "document_class",
    "pages",
    "empty_pages",
    "chars",
    "chars_stripped",
    "sampled_pages",
    "codec",
    "boilerplate",
    "margin_patterns",
    "margin_stripped",
    "year_page_counts",
    "symbol_glyphs",
    "error",
)

_ARTIFACT_ORDER = SERIALISED_ORDER

# ``doc_id`` is the dictionary key after reading; every other Document field is
# required in each entry. Deriving this set prevents the checked contract from
# drifting away from the declared one.
REQUIRED = frozenset(item.name for item in fields(Document) if item.name != "doc_id")


def serialize_record(record: Record) -> dict[str, Any]:
    """Return one record in the artifact's byte-significant key order."""
    record_fields = {item.name for item in fields(Record)}
    if (
        SERIALISED_ORDER != _ARTIFACT_ORDER
        or len(SERIALISED_ORDER) != len(record_fields)
        or set(SERIALISED_ORDER) != record_fields
    ):
        raise ValueError(
            "SERIALISED_ORDER changed; reordering manifest keys causes extraction "
            "cache invalidation"
        )
    return {name: getattr(record, name) for name in SERIALISED_ORDER}


@dataclass(frozen=True)
class Problem:
    """One document or artifact defect retained by the tolerant reader."""

    message: str
    doc_id: str | None = None
    cause: ValueError | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class Manifest:
    """Everything safely recovered from one locked manifest handoff."""

    root: Path
    entries: dict[str, dict[str, Any]]
    documents: dict[str, Record]
    pages: dict[str, tuple[str, ...]]
    problems: tuple[Problem, ...]
    provenance: artifact_provenance.ProvenanceCheck | None = None


def normalize_doc_id(value: str) -> str:
    """Normalize the manifest key and its corresponding relative text path."""
    cleaned = value.strip().replace("\\", "/").strip("/")
    return cleaned[:-4] if cleaned.lower().endswith(".txt") else cleaned


def _problem(
    root: Path,
    message: str,
    doc_id: str | None = None,
    cause: ValueError | None = None,
) -> Manifest:
    return Manifest(root, {}, {}, {}, (Problem(message, doc_id, cause),))


def _record(entry: dict[str, Any], doc_id: str) -> Record:
    values = {
        item.name: entry[item.name]
        for item in fields(Record)
        if item.name in entry
    }
    values["doc_id"] = doc_id
    return Record(**values)


def _read_locked(
    root: Path,
    *,
    allow_untrusted_provenance: bool,
    expected_commit: str | None,
) -> Manifest:
    if not root.is_dir():
        return _problem(root, f"extracted corpus not found at {root}")
    path = root / MANIFEST_NAME
    if not path.is_file():
        return _problem(root, f"{path} is required")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as failure:
        return _problem(root, f"{path} is present but could not be read as JSON: {failure}")

    stamped = data.get("producer") if isinstance(data, dict) else None
    try:
        provenance = artifact_provenance.check_producer(
            stamped,
            path,
            allow_untrusted=allow_untrusted_provenance,
            expected_commit=expected_commit,
            unchanged_paths=("tools/guidelines_extract.py",),
        )
    except ValueError as failure:
        return _problem(root, str(failure), cause=failure)

    entries = data.get("documents") if isinstance(data, dict) else data
    if not isinstance(entries, list):
        return _problem(
            root,
            f'{path} is not a list of entries or a {{"documents": [...]}} object',
        )

    documents: dict[str, Record] = {}
    raw_entries: dict[str, dict[str, Any]] = {}
    page_sets: dict[str, tuple[str, ...]] = {}
    problems: list[Problem] = []
    saw_key = False
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("doc_id"):
            problems.append(Problem(f"an entry in {path} carries no 'doc_id'"))
            continue
        saw_key = True
        doc_id = normalize_doc_id(str(entry["doc_id"]))
        raw_entries[doc_id] = entry
        if doc_id in documents:
            problems.append(Problem("manifest carries a duplicate document", doc_id))
            continue
        missing = sorted(REQUIRED - entry.keys())
        if missing:
            problems.append(
                Problem(f"{doc_id}: manifest entry is missing keys: {missing}", doc_id)
            )
            continue
        try:
            record = _record(entry, doc_id)
        except (TypeError, ValueError) as failure:
            problems.append(Problem(f"{doc_id}: invalid manifest entry: {failure}", doc_id))
            continue
        if record.error:
            problems.append(
                Problem(f"{doc_id}: extraction failed: {record.error}", doc_id)
            )
            continue
        if not record.source:
            problems.append(Problem(f"{doc_id}: manifest entry has no source filename", doc_id))
            continue
        if not record.output:
            problems.append(Problem(f"{doc_id}: manifest entry has no output filename", doc_id))
            continue
        body_path = root / record.output
        if not body_path.is_file():
            problems.append(Problem(f"{doc_id}: extracted text is missing: {record.output}", doc_id))
            continue
        body = body_path.read_text(encoding="utf-8", errors="replace")
        pages = tuple(body.split("\f"))
        if record.pages != len(pages):
            problems.append(
                Problem(
                    f"{doc_id}: manifest says {record.pages} pages, "
                    f"extracted text contains {len(pages)}",
                    doc_id,
                )
            )
            continue
        documents[doc_id] = record
        page_sets[doc_id] = pages

    if entries and not saw_key:
        problems.append(
            Problem(f"no entry in {path} carries a 'doc_id', so nothing can be matched")
        )
    expected_outputs = {
        str(Path(record.output).as_posix())
        for record in documents.values()
        if record.output
    }
    actual_outputs = {
        path.relative_to(root).as_posix() for path in root.rglob("*.txt")
    }
    for extra in sorted(actual_outputs - expected_outputs):
        problems.append(Problem(f"extracted text has no usable manifest entry: {extra}"))
    return Manifest(root, raw_entries, documents, page_sets, tuple(problems), provenance)


def read(
    text_dir: Path | str,
    *,
    allow_untrusted_provenance: bool = False,
    expected_commit: str | None = None,
) -> Manifest:
    """Tolerantly read one extraction while holding its shared read lock."""
    root = Path(text_dir).resolve()
    try:
        with artifact_lock.hold(
            root, "reading extracted guideline corpus", mode="read"
        ):
            return _read_locked(
                root,
                allow_untrusted_provenance=allow_untrusted_provenance,
                expected_commit=expected_commit,
            )
    except artifact_lock.ArtifactBusy as failure:
        return _problem(root, str(failure), cause=failure)


def read_or_raise(
    text_dir: Path | str, *, allow_untrusted_provenance: bool = False
) -> Manifest:
    """Strictly read one extraction, refusing if the tolerant reader found a problem."""
    result = read(text_dir, allow_untrusted_provenance=allow_untrusted_provenance)
    if result.problems:
        if len(result.problems) == 1 and result.problems[0].cause is not None:
            raise result.problems[0].cause
        raise ValueError("; ".join(problem.message for problem in result.problems))
    return result


def stamp(root: Path, producer: dict[str, object]) -> None:
    """Write cache-specific producer provenance without changing any other bytes."""
    path = root / MANIFEST_NAME
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("extraction manifest is not a JSON object")
    manifest["producer"] = producer
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
