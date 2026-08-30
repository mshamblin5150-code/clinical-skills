"""Build or reuse content-addressed extraction, index, and recommendation artifacts.

    python tools/guidelines_build.py <source-folder>

Completed builds live outside every checkout under immutable identities. The
catalog is an index, not a trust boundary: every hit is verified against the
artifact's own SHA-256 inventory before it is returned. The familiar
extracted-text and index paths are compatibility mirrors, never cache inputs.
"""

from __future__ import annotations

import argparse
import artifact_lock
import artifact_provenance
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import uuid
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

import guidelines_extract
import guidelines_index
import guidelines_index_artifact
import guidelines_manifest
import guidelines_recs
from console_codec import use_utf8
from repo_root import ensure_outside_checkout, main_repo_root


CATALOG_SCHEMA_VERSION = 2
ARTIFACT_SCHEMA_VERSION = 1
ARTIFACT_RECORD = "artifact.json"
CATALOG_NAME = "catalog.json"
CATALOG_ENVIRONMENT_VARIABLE = "CLINICAL_GUIDELINES_BUILDS"
WHY_OUTSIDE = (
    "Guideline build artifacts contain society-copyrighted text and must stay "
    "outside every git checkout."
)
stamp_manifest = guidelines_manifest.stamp


@dataclass(frozen=True)
class SelectedArtifact:
    kind: str
    key: str
    path: Path
    reused: bool
    files: tuple[dict[str, str | int], ...]


@dataclass(frozen=True)
class ArtifactCandidate:
    catalog_root: Path
    catalog_path: Path
    kind: str
    key: str
    identity: dict[str, object]
    path: Path


def default_catalog_root() -> Path:
    override = os.environ.get(CATALOG_ENVIRONMENT_VARIABLE)
    if override:
        return Path(override).expanduser()
    return main_repo_root().parent / "guidelines-builds"


def _raw_file_identity(path: Path) -> str:
    """Hash corpus and built-artifact bytes without text normalization."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _files(root: Path, pattern: str = "*") -> tuple[dict[str, str | int], ...]:
    rows = []
    for path in sorted(root.rglob(pattern), key=lambda item: item.relative_to(root).as_posix()):
        if not path.is_file() or path.name == ARTIFACT_RECORD:
            continue
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": _raw_file_identity(path),
                "bytes": path.stat().st_size,
            }
        )
    return tuple(rows)


def identity_key(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _code_inputs(*paths: str) -> tuple[dict[str, str], ...]:
    repo = Path(__file__).resolve().parent.parent
    return tuple(
        {
            "path": path,
            "sha256": artifact_provenance.text_file_identity(repo / path),
        }
        for path in paths
    )


def _package_version(distribution: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "unavailable"


def extraction_identity(source: Path) -> dict[str, object]:
    source_files = _files(source, "*.pdf")
    if not source_files:
        raise ValueError(f"no PDFs under {source}")
    return {
        "kind": "extraction",
        "schema": ARTIFACT_SCHEMA_VERSION,
        "source_files": source_files,
        "producer_files": _code_inputs(
            *artifact_provenance.CACHE_IDENTITY["extraction"]
        ),
        "runtime": {
            "python": platform.python_version(),
            "pymupdf": _package_version("PyMuPDF"),
        },
        "options": {"codec": guidelines_extract.OUTPUT_CODEC},
    }


def index_identity(extraction: SelectedArtifact) -> dict[str, object]:
    return {
        "kind": "index",
        "schema": ARTIFACT_SCHEMA_VERSION,
        "extraction_key": extraction.key,
        "extraction_inventory": _extraction_inventory(extraction),
        "producer_files": _code_inputs(*artifact_provenance.CACHE_IDENTITY["index"]),
        "runtime": {
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
        },
        "options": {"schema_version": guidelines_index.SCHEMA_VERSION},
    }


def recs_identity(source: Path) -> dict[str, object]:
    source_files = _files(source, "*.pdf")
    if not source_files:
        raise ValueError(f"no PDFs under {source}")
    return {
        "kind": "recs",
        "schema": ARTIFACT_SCHEMA_VERSION,
        # Sweep records preserve absolute source paths for strict consumers,
        # so corpus location is part of their byte-level identity.
        "source_root": str(source.resolve()),
        "source_files": source_files,
        "producer_files": _code_inputs(*artifact_provenance.CACHE_IDENTITY["recs"]),
        "runtime": {
            "python": platform.python_version(),
            "pymupdf": _package_version("PyMuPDF"),
        },
        "curated_table": {
            "path": "reference/guidelines-uspstf.md",
            "sha256": artifact_provenance.text_file_identity(
                guidelines_recs.CURATED_TABLE
            ),
        },
    }


def _extraction_inventory(extraction: SelectedArtifact) -> str:
    """Identify extracted content without allowing lineage metadata to key it."""
    rows: list[dict[str, object]] = []
    for row in extraction.files:
        normalized = dict(row)
        if row["path"] == guidelines_manifest.MANIFEST_NAME:
            manifest = guidelines_manifest.load(extraction.path)
            manifest.pop("producer", None)
            normalized["sha256"] = identity_key(manifest)
            normalized.pop("bytes", None)
        rows.append(normalized)
    return identity_key(rows)


def _empty_catalog() -> dict[str, object]:
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "artifacts": {kind: {} for kind in artifact_provenance.CACHE_IDENTITY},
    }


def _read_catalog_unlocked(path: Path) -> dict[str, object]:
    if not path.exists():
        return _empty_catalog()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as failure:
        raise ValueError(f"catalog {path} is unreadable: {failure}") from failure
    if (
        isinstance(data, dict)
        and data.get("schema_version") == 1
        and isinstance(data.get("artifacts"), dict)
        and all(
            isinstance(data["artifacts"].get(kind), dict)
            for kind in ("extraction", "index")
        )
    ):
        return _empty_catalog()
    if not isinstance(data, dict) or data.get("schema_version") != CATALOG_SCHEMA_VERSION:
        raise ValueError(f"catalog {path} has an unsupported schema")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict) or any(
        not isinstance(artifacts.get(kind), dict)
        for kind in artifact_provenance.CACHE_IDENTITY
    ):
        raise ValueError(f"catalog {path} does not map every artifact kind")
    return data


def _write_catalog_unlocked(path: Path, catalog: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.building")
    temporary.write_text(
        json.dumps(catalog, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _catalog_entry(path: Path, kind: str, key: str) -> dict[str, object] | None:
    with artifact_lock.hold(path, "reading guideline build catalog", mode="read"):
        catalog = _read_catalog_unlocked(path)
    artifacts = catalog["artifacts"]
    assert isinstance(artifacts, dict)
    entries = artifacts[kind]
    assert isinstance(entries, dict)
    entry = entries.get(key)
    return entry if isinstance(entry, dict) else None


def _set_catalog_entry(
    path: Path, kind: str, key: str, entry: dict[str, object]
) -> None:
    with artifact_lock.hold(path, "updating guideline build catalog"):
        catalog = _read_catalog_unlocked(path)
        artifacts = catalog["artifacts"]
        assert isinstance(artifacts, dict)
        entries = artifacts[kind]
        assert isinstance(entries, dict)
        previous = entries.get(key)
        aliases = []
        if isinstance(previous, dict) and isinstance(previous.get("aliases"), list):
            aliases = previous["aliases"]
        entry["aliases"] = aliases
        entries[key] = entry
        _write_catalog_unlocked(path, catalog)


def _remove_catalog_entry(path: Path, kind: str, key: str) -> None:
    with artifact_lock.hold(path, "repairing guideline build catalog"):
        catalog = _read_catalog_unlocked(path)
        artifacts = catalog["artifacts"]
        assert isinstance(artifacts, dict)
        entries = artifacts[kind]
        assert isinstance(entries, dict)
        entries.pop(key, None)
        _write_catalog_unlocked(path, catalog)


def _remember_alias(path: Path, kind: str, key: str, alias: Path) -> None:
    with artifact_lock.hold(path, "recording guideline artifact alias"):
        catalog = _read_catalog_unlocked(path)
        artifacts = catalog["artifacts"]
        assert isinstance(artifacts, dict)
        entries = artifacts[kind]
        assert isinstance(entries, dict)
        entry = entries.get(key)
        if not isinstance(entry, dict):
            raise ValueError(f"catalog lost {kind} build {key}")
        aliases = entry.setdefault("aliases", [])
        if not isinstance(aliases, list):
            raise ValueError(f"catalog aliases for {kind} build {key} are invalid")
        rendered = str(alias)
        if rendered not in aliases:
            aliases.append(rendered)
            aliases.sort()
            _write_catalog_unlocked(path, catalog)


def _write_artifact_record(
    root: Path,
    *,
    kind: str,
    key: str,
    identity: dict[str, object],
    producer: dict[str, object],
) -> tuple[dict[str, str | int], ...]:
    files = _files(root)
    record = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "kind": kind,
        "key": key,
        "identity": identity,
        "producer": producer,
        "files": files,
    }
    (root / ARTIFACT_RECORD).write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return files


def _verify_artifact(
    root: Path, kind: str, key: str, identity: dict[str, object]
) -> tuple[dict[str, str | int], ...]:
    record_path = root / ARTIFACT_RECORD
    if not root.is_dir() or not record_path.is_file():
        raise ValueError(f"{kind} build {key} is missing or incomplete")
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as failure:
        raise ValueError(f"{kind} build {key} has an unreadable record: {failure}") from failure
    if not isinstance(record, dict):
        raise ValueError(f"{kind} build {key} has an invalid record")
    if (
        record.get("schema_version") != ARTIFACT_SCHEMA_VERSION
        or record.get("kind") != kind
        or record.get("key") != key
        or identity_key(record.get("identity")) != identity_key(identity)
    ):
        raise ValueError(f"{kind} build {key} does not match its catalog identity")
    producer = record.get("producer")
    if (
        not isinstance(producer, dict)
        or not isinstance(producer.get("commit"), str)
        or not producer["commit"]
        or producer.get("dirty") is not False
    ):
        raise ValueError(f"{kind} build {key} has no trusted clean producer")
    if identity_key(producer.get("inputs")) != identity_key(
        _trust_floor_inputs(identity)
    ):
        raise ValueError(f"{kind} build {key} has the wrong producer identity")
    recorded = record.get("files")
    actual = _files(root)
    if list(actual) != recorded:
        raise ValueError(f"{kind} build {key} failed SHA-256 verification")
    return actual


def _validate_extraction(root: Path) -> None:
    handoff = guidelines_manifest.validate(root)
    if not handoff.documents:
        raise ValueError("extraction manifest contains no documents")


def _validate_index(database: Path) -> None:
    if not database.is_file():
        raise ValueError("index producer did not create a database")
    try:
        with closing(sqlite3.connect(f"file:{database}?mode=ro", uri=True)) as connection:
            verdict = connection.execute("PRAGMA quick_check").fetchone()
    except sqlite3.Error as failure:
        raise ValueError(f"index database could not be opened: {failure}") from failure
    if verdict != ("ok",):
        raise ValueError(f"index database failed SQLite verification: {verdict}")


def _trust_floor_inputs(identity: dict[str, object]) -> tuple[dict[str, str], ...]:
    kind = identity.get("kind")
    inputs = identity.get("producer_files")
    if kind not in artifact_provenance.TRUST_FLOOR:
        raise ValueError(f"unknown artifact kind {kind!r}")
    if not isinstance(inputs, tuple) or not inputs:
        raise ValueError("build identity has no producer-file fingerprints")
    floor = set(artifact_provenance.TRUST_FLOOR[str(kind)])
    selected = tuple(row for row in inputs if row.get("path") in floor)
    if {row.get("path") for row in selected} != floor:
        raise ValueError("build identity does not cover the artifact trust floor")
    return selected


def _trusted_producer(
    producer: dict[str, str | bool], identity: dict[str, object]
) -> dict[str, object]:
    return {**producer, "inputs": list(_trust_floor_inputs(identity))}


def _run_producer(command: list[str], label: str) -> None:
    finished = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if finished.returncode != 0:
        detail = finished.stderr.strip() or finished.stdout.strip()
        raise ValueError(f"{label} failed with status {finished.returncode}: {detail}")


def _catalog_record(root: Path, producer: dict[str, object]) -> dict[str, object]:
    return {"path": str(root), "producer": producer}


def _quarantine(root: Path, catalog_root: Path) -> None:
    if not root.exists():
        return
    destination = catalog_root / "quarantine" / f"{root.parent.name}-{root.name}-{uuid.uuid4().hex}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(root, destination)


class InvalidCachedArtifact(ValueError):
    """A catalog candidate needs exclusive repair ownership."""


def _existing(
    candidate: ArtifactCandidate,
    *,
    repair: bool,
    register: bool,
) -> SelectedArtifact | None:
    entry = _catalog_entry(candidate.catalog_path, candidate.kind, candidate.key)
    if (
        entry is not None
        and Path(str(entry.get("path", ""))).resolve() != candidate.path.resolve()
    ):
        if not repair:
            raise InvalidCachedArtifact(
                f"{candidate.kind} build {candidate.key} has a stale catalog path"
            )
        _remove_catalog_entry(
            candidate.catalog_path, candidate.kind, candidate.key
        )
        entry = None
    if entry is not None or candidate.path.exists():
        try:
            files = _verify_artifact(
                candidate.path,
                candidate.kind,
                candidate.key,
                candidate.identity,
            )
        except ValueError as failure:
            if not repair:
                raise InvalidCachedArtifact(str(failure)) from failure
            _remove_catalog_entry(
                candidate.catalog_path, candidate.kind, candidate.key
            )
            _quarantine(candidate.path, candidate.catalog_root)
            return None
        if entry is None:
            if not register:
                return None
            record = json.loads(
                (candidate.path / ARTIFACT_RECORD).read_text(encoding="utf-8")
            )
            _set_catalog_entry(
                candidate.catalog_path,
                candidate.kind,
                candidate.key,
                _catalog_record(candidate.path, record["producer"]),
            )
        return SelectedArtifact(
            candidate.kind, candidate.key, candidate.path, True, files
        )
    return None


def _clean_partials(parent: Path, key: str) -> None:
    if not parent.exists():
        return
    for path in parent.glob(f".{key}.*.building"):
        if path.is_dir() and path.resolve().is_relative_to(parent.resolve()):
            shutil.rmtree(path)


def _clean_abandoned_partials(final: Path) -> None:
    if not final.parent.exists() or not any(
        final.parent.glob(f".{final.name}.*.building")
    ):
        return
    with artifact_lock.hold(final, f"cleaning incomplete {final.parent.name} build"):
        _clean_partials(final.parent, final.name)


def _select_or_build(
    kind: str,
    catalog_root: Path,
    catalog_path: Path,
    identity: dict[str, object],
    producer: dict[str, str | bool],
    build_temporary: Callable[[Path, dict[str, object]], None],
) -> SelectedArtifact:
    key = identity_key(identity)
    final = catalog_root / "artifacts" / kind / key
    candidate = ArtifactCandidate(
        catalog_root, catalog_path, kind, key, identity, final
    )
    _clean_abandoned_partials(final)
    try:
        with artifact_lock.hold(final, f"verifying cached {kind} build", mode="read"):
            existing = _existing(
                candidate,
                repair=False,
                register=producer["dirty"] is False,
            )
    except InvalidCachedArtifact:
        existing = None
    if existing is not None:
        return existing
    if producer["dirty"]:
        raise ValueError(
            "a dirty checkout may reuse a trusted build but may not publish a new one"
        )
    final.parent.mkdir(parents=True, exist_ok=True)
    trusted_producer = _trusted_producer(producer, identity)
    with artifact_lock.hold(final, f"building guideline {kind} {key}"):
        existing = _existing(candidate, repair=True, register=True)
        if existing is not None:
            return existing
        _clean_partials(final.parent, key)
        temporary = final.parent / f".{key}.{uuid.uuid4().hex}.building"
        temporary.mkdir()
        try:
            build_temporary(temporary, trusted_producer)
            files = _write_artifact_record(
                temporary,
                kind=kind,
                key=key,
                identity=identity,
                producer=trusted_producer,
            )
            os.replace(temporary, final)
        except BaseException:
            shutil.rmtree(temporary, ignore_errors=True)
            raise
        _set_catalog_entry(
            catalog_path, kind, key, _catalog_record(final, trusted_producer)
        )
    return SelectedArtifact(kind, key, final, False, files)


def _build_extraction(
    source: Path,
    catalog_root: Path,
    catalog_path: Path,
    identity: dict[str, object],
    producer: dict[str, str | bool],
    jobs: int,
) -> SelectedArtifact:
    def build_temporary(temporary: Path, trusted: dict[str, object]) -> None:
        command = [
            sys.executable,
            str(Path(__file__).with_name("guidelines_extract.py")),
            str(source),
            "--out",
            str(temporary),
            "--quiet",
        ]
        if jobs:
            command.extend(["--jobs", str(jobs)])
        _run_producer(command, "guideline extraction")
        if _files(source, "*.pdf") != identity["source_files"]:
            raise ValueError("source files changed during extraction; retry the build")
        stamp_manifest(temporary, trusted)
        _validate_extraction(temporary)

    return _select_or_build(
        "extraction",
        catalog_root,
        catalog_path,
        identity,
        producer,
        build_temporary,
    )


def _build_index(
    extraction: SelectedArtifact,
    catalog_root: Path,
    catalog_path: Path,
    identity: dict[str, object],
    producer: dict[str, str | bool],
) -> SelectedArtifact:
    def build_temporary(temporary: Path, trusted: dict[str, object]) -> None:
        database = temporary / "guidelines.sqlite"
        with artifact_lock.hold(
            extraction.path,
            "reading cached extraction for guideline index",
            mode="read",
        ):
            if _files(extraction.path) != extraction.files:
                raise ValueError("cached extraction changed before index production")
            manifest = guidelines_manifest.load(extraction.path)
            source_producer = manifest.get("producer")
            if not isinstance(source_producer, dict):
                raise ValueError("cached extraction has no producer record")
            _run_producer(
                [
                    sys.executable,
                    str(Path(__file__).with_name("guidelines_index.py")),
                    str(extraction.path),
                    str(database),
                ],
                "guideline index",
            )
            if _files(extraction.path) != extraction.files:
                raise ValueError("cached extraction changed during index production")
        guidelines_index_artifact.stamp(database, trusted, source_producer)
        _validate_index(database)

    return _select_or_build(
        "index",
        catalog_root,
        catalog_path,
        identity,
        producer,
        build_temporary,
    )


def _build_recs(
    source: Path,
    catalog_root: Path,
    catalog_path: Path,
    identity: dict[str, object],
    producer: dict[str, str | bool],
) -> SelectedArtifact:
    def build_temporary(temporary: Path, _: dict[str, object]) -> None:
        try:
            guidelines_recs.build_sweep(source, temporary, producer)
        except guidelines_recs.DidNotScan as failure:
            raise ValueError(
                f"recommendation sweep did not scan {failure}"
            ) from failure
        if _files(source, "*.pdf") != identity["source_files"]:
            raise ValueError(
                "source files changed during recommendation sweep; retry the build"
            )
        curated_identity = identity.get("curated_table")
        if (
            not isinstance(curated_identity, dict)
            or curated_identity.get("sha256")
            != artifact_provenance.text_file_identity(guidelines_recs.CURATED_TABLE)
        ):
            raise ValueError(
                "curated table changed during recommendation sweep; retry the build"
            )

    return _select_or_build(
        "recs",
        catalog_root,
        catalog_path,
        identity,
        producer,
        build_temporary,
    )


def _recs_coverage(root: Path) -> tuple[int, int, int]:
    manifest = json.loads(
        (root / guidelines_recs.SWEEP_MANIFEST).read_text(encoding="utf-8")
    )
    documents = manifest.get("documents") if isinstance(manifest, dict) else None
    if not isinstance(documents, list) or any(
        not isinstance(row, dict) for row in documents
    ):
        raise ValueError("recommendation manifest has no document rows")
    records = sum(
        1
        for row in documents
        if isinstance(row.get("record"), str) and (root / row["record"]).is_file()
    )
    nothing_found = sum(
        1 for row in documents if row.get("outcome") == guidelines_recs.NOTHING_FOUND
    )
    if records != len(documents):
        raise ValueError("recommendation manifest does not resolve every record")
    return len(documents), records, nothing_found


def default_recs_alias(source: Path) -> Path:
    return source.parent / "guidelines-recs"


def _publish_directory(source: Path, alias: Path) -> None:
    alias = ensure_outside_checkout(alias, detail=WHY_OUTSIDE)
    if alias.resolve() == source.resolve():
        return
    alias.parent.mkdir(parents=True, exist_ok=True)
    temporary = alias.with_name(f".{alias.name}.{uuid.uuid4().hex}.building")
    backup = alias.with_name(f".{alias.name}.{uuid.uuid4().hex}.previous")
    try:
        shutil.copytree(source, temporary, ignore=shutil.ignore_patterns(ARTIFACT_RECORD))
        with artifact_lock.hold(alias, "publishing guideline directory compatibility path"):
            moved_previous = False
            try:
                if alias.exists():
                    os.replace(alias, backup)
                    moved_previous = True
                os.replace(temporary, alias)
            except BaseException:
                if moved_previous and not alias.exists():
                    os.replace(backup, alias)
                raise
    finally:
        shutil.rmtree(temporary, ignore_errors=True)
        if alias.exists():
            shutil.rmtree(backup, ignore_errors=True)


def _publish_file(source: Path, alias: Path) -> None:
    alias = ensure_outside_checkout(alias, detail=WHY_OUTSIDE)
    if alias.resolve() == source.resolve():
        return
    alias.parent.mkdir(parents=True, exist_ok=True)
    temporary = alias.with_name(f".{alias.name}.{uuid.uuid4().hex}.building")
    shutil.copy2(source, temporary)
    try:
        with artifact_lock.hold(alias, "publishing guideline index compatibility path"):
            os.replace(temporary, alias)
    finally:
        temporary.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="directory holding guideline PDFs")
    parser.add_argument(
        "--catalog-root",
        type=Path,
        default=None,
        help=f"content-addressed build root (default: {default_catalog_root()})",
    )
    parser.add_argument(
        "--text-alias",
        type=Path,
        default=None,
        help="compatibility extracted-text path (default: beside the source)",
    )
    parser.add_argument(
        "--index-alias",
        type=Path,
        default=None,
        help="compatibility index path (default: the existing index default)",
    )
    parser.add_argument(
        "--recs-alias",
        type=Path,
        default=None,
        help="compatibility recommendation-record path (default: beside the source)",
    )
    parser.add_argument(
        "--no-recs",
        action="store_true",
        help="skip the default recommendation-record stage",
    )
    parser.add_argument(
        "--jobs", type=int, default=0, help="extractor worker processes"
    )
    return parser


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    source = args.source.expanduser().resolve()
    try:
        catalog_root = ensure_outside_checkout(
            args.catalog_root or default_catalog_root(), detail=WHY_OUTSIDE
        )
        catalog_path = catalog_root / CATALOG_NAME
        text_alias = (args.text_alias or guidelines_extract.default_output(source)).resolve()
        index_alias = (args.index_alias or guidelines_index.default_database()).resolve()
        recs_alias = (args.recs_alias or default_recs_alias(source)).resolve()
        producer = artifact_provenance.current_producer()
        recs = None
        if not args.no_recs:
            recs_spec = recs_identity(source)
            recs = _build_recs(
                source, catalog_root, catalog_path, recs_spec, producer
            )
        extraction_spec = extraction_identity(source)
        extraction = _build_extraction(
            source,
            catalog_root,
            catalog_path,
            extraction_spec,
            producer,
            args.jobs,
        )
        index_spec = index_identity(extraction)
        index = _build_index(
            extraction, catalog_root, catalog_path, index_spec, producer
        )
        _publish_directory(extraction.path, text_alias)
        _publish_file(index.path / "guidelines.sqlite", index_alias)
        if recs is not None:
            _publish_directory(recs.path, recs_alias)
        _remember_alias(catalog_path, "extraction", extraction.key, text_alias)
        _remember_alias(catalog_path, "index", index.key, index_alias)
        if recs is not None:
            _remember_alias(catalog_path, "recs", recs.key, recs_alias)
            recs_coverage = _recs_coverage(recs.path)
    except (artifact_lock.ArtifactBusy, OSError, ValueError) as failure:
        print(str(failure), file=sys.stderr)
        return 2

    print(f"extraction  {'REUSED' if extraction.reused else 'BUILT'}  {extraction.path}")
    print(f"index       {'REUSED' if index.reused else 'BUILT'}  {index.path / 'guidelines.sqlite'}")
    if recs is None:
        print("recs        SKIPPED (--no-recs)")
    else:
        print(f"recs        {'REUSED' if recs.reused else 'BUILT'}  {recs.path}")
        print(
            "recs coverage  "
            f"documents read {recs_coverage[0]}; "
            f"records written {recs_coverage[1]}; "
            f"yielded nothing {recs_coverage[2]}"
        )
    print(f"text alias  {text_alias}")
    print(f"index alias {index_alias}")
    if recs is not None:
        print(f"recs alias  {recs_alias}")
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
