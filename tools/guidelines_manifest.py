"""Own the extracted-guideline manifest contract shared by producers and readers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from pathlib import Path, PureWindowsPath
from typing import Any

import artifact_lock
import artifact_provenance


MANIFEST_NAME = "manifest.json"

# This lexical walk is a floor for the shapes present in this tree. It cannot see a
# filename assembled by concatenation or JSON reached through an already-open file.
DISCOVERY_CEILING = (
    "MANIFEST_NAME",
    MANIFEST_NAME,
    "read_manifest",
    "read_extracted_corpus",
)

# Other artifact families may deliberately own a different manifest contract under
# the same conventional filename. Naming each owner here keeps the lexical consumer
# walk refusing by default without pretending those producers consume this module.
NON_EXTRACTION_MANIFEST_OWNERS = {
    "guidelines_recs.py": "recommendation sweep manifest",
}

# The refusing walk remains runnable during staged migration. Each exception must
# say why it exists and is removed in the commit that migrates that consumer.
NOT_MIGRATED: dict[str, str] = {}


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
    split_boundaries: dict[str, int] = field(default_factory=dict)
    quantity_split_shapes: dict[str, int] = field(default_factory=dict)
    error: str | None = None


# Dataclass inheritance groups the consumer fields before the audit fields. That is
# a useful in-memory shape but not the artifact format: this order preserves the
# bytes emitted before #407, because those bytes key the extraction build cache.
SERIALIZED_ORDER = (
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
    "split_boundaries",
    "quantity_split_shapes",
    "error",
)

_ARTIFACT_ORDER = SERIALIZED_ORDER

# ``doc_id`` is the dictionary key after reading; every other Document field is
# required in each entry. Deriving this set prevents the checked contract from
# drifting away from the declared one.
REQUIRED = frozenset(item.name for item in fields(Document) if item.name != "doc_id")


def serialize_record(record: Record) -> dict[str, Any]:
    """Return one record in the artifact's byte-significant key order."""
    record_fields = {item.name for item in fields(Record)}
    if (
        SERIALIZED_ORDER != _ARTIFACT_ORDER
        or len(SERIALIZED_ORDER) != len(record_fields)
        or set(SERIALIZED_ORDER) != record_fields
    ):
        raise ValueError(
            "SERIALIZED_ORDER changed; reordering manifest keys causes extraction "
            "cache invalidation"
        )
    return {name: getattr(record, name) for name in SERIALIZED_ORDER}


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
    scalar_types: dict[str, type | tuple[type, ...]] = {
        "society": (str, type(None)),
        "title": (str, type(None)),
        "source": str,
        "output": (str, type(None)),
        "document_class": str,
        "codec": str,
        "error": (str, type(None)),
    }
    integer_fields = {
        "pages",
        "empty_pages",
        "chars",
        "chars_stripped",
        "sampled_pages",
    }
    list_fields = {"boilerplate", "margin_patterns", "margin_stripped"}
    count_fields = {
        "year_page_counts",
        "symbol_glyphs",
        "split_boundaries",
        "quantity_split_shapes",
    }
    for name, expected in scalar_types.items():
        if name in entry and not isinstance(entry[name], expected):
            raise TypeError(f"{name} must be a string or null")
    for name in integer_fields:
        if name in entry and (
            not isinstance(entry[name], int) or isinstance(entry[name], bool)
        ):
            raise TypeError(f"{name} must be an integer")
    for name in list_fields:
        value = entry.get(name)
        if value is not None and (
            not isinstance(value, list)
            or any(not isinstance(item, str) for item in value)
        ):
            raise TypeError(f"{name} must be a list of strings")
    for name in count_fields:
        value = entry.get(name)
        if value is not None and (
            not isinstance(value, dict)
            or any(not isinstance(key, str) for key in value)
            or any(
                not isinstance(count, int) or isinstance(count, bool)
                for count in value.values()
            )
        ):
            raise TypeError(f"{name} must map strings to integers")
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
    verify_provenance: bool = True,
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
    provenance = None
    if verify_provenance:
        try:
            provenance = artifact_provenance.check_producer(
                stamped,
                path,
                allow_untrusted=allow_untrusted_provenance,
                expected_commit=expected_commit,
                unchanged_paths=artifact_provenance.TRUST_FLOOR["extraction"],
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
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("doc_id"), str)
            or not entry["doc_id"].strip()
        ):
            problems.append(Problem(f"an entry in {path} carries no 'doc_id'"))
            continue
        saw_key = True
        raw_doc_id = entry["doc_id"].replace("\\", "/")
        doc_id = normalize_doc_id(raw_doc_id)
        raw_entries[doc_id] = entry
        if (
            raw_doc_id.startswith("/")
            or PureWindowsPath(raw_doc_id).is_absolute()
            or bool(PureWindowsPath(raw_doc_id).drive)
            or any(part in {".", ".."} for part in raw_doc_id.split("/"))
        ):
            problems.append(
                Problem(f"{doc_id}: document ID must be a safe relative path", doc_id)
            )
            continue
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
        expected_output = f"{doc_id}.txt"
        normalized_output = record.output.replace("\\", "/")
        if normalized_output != expected_output:
            problems.append(
                Problem(
                    f"{doc_id}: output must be {expected_output}, got {record.output}",
                    doc_id,
                )
            )
            continue
        body_path = (root / Path(*normalized_output.split("/"))).resolve()
        try:
            body_path.relative_to(root)
        except ValueError:
            problems.append(
                Problem(f"{doc_id}: output must remain inside the extracted corpus", doc_id)
            )
            continue
        if not body_path.is_file():
            problems.append(Problem(f"{doc_id}: extracted text is missing: {record.output}", doc_id))
            continue
        try:
            body = body_path.read_text(encoding="utf-8", errors="replace")
        except OSError as failure:
            problems.append(
                Problem(f"{doc_id}: extracted text could not be read: {failure}", doc_id)
            )
            continue
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
    try:
        actual_outputs = {
            path.relative_to(root).as_posix() for path in root.rglob("*.txt")
        }
    except OSError as failure:
        problems.append(Problem(f"extracted text files could not be listed: {failure}"))
        actual_outputs = set()
    for extra in sorted(actual_outputs - expected_outputs):
        problems.append(Problem(f"extracted text has no usable manifest entry: {extra}"))
    return Manifest(root, raw_entries, documents, page_sets, tuple(problems), provenance)


def read(
    text_dir: Path | str,
    *,
    expected_commit: str,
    allow_untrusted_provenance: bool = False,
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
                verify_provenance=True,
            )
    except artifact_lock.ArtifactBusy as failure:
        return _problem(root, str(failure), cause=failure)


def read_or_raise(
    text_dir: Path | str,
    *,
    expected_commit: str,
    allow_untrusted_provenance: bool = False,
) -> Manifest:
    """Strictly read one extraction, refusing if the tolerant reader found a problem."""
    result = read(
        text_dir,
        expected_commit=expected_commit,
        allow_untrusted_provenance=allow_untrusted_provenance,
    )
    if result.problems:
        if len(result.problems) == 1 and result.problems[0].cause is not None:
            raise result.problems[0].cause
        raise ValueError("; ".join(problem.message for problem in result.problems))
    return result


def validate(root: Path) -> Manifest:
    """Validate a newly produced artifact whose caller already owns its trust stamp."""
    resolved = root.resolve()
    with artifact_lock.hold(
        resolved, "validating extracted guideline corpus", mode="read"
    ):
        result = _read_locked(
            resolved,
            allow_untrusted_provenance=False,
            expected_commit=None,
            verify_provenance=False,
        )
    if result.problems:
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


def load(root: Path) -> dict[str, Any]:
    """Load the top-level object for callers already holding the artifact lock."""
    path = root / MANIFEST_NAME
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as failure:
        raise ValueError(f"extraction did not produce a readable manifest: {failure}") from failure
    if not isinstance(value, dict):
        raise ValueError("extraction manifest is not a JSON object")
    return value
