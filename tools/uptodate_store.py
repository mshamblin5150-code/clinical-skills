"""Ingest, index, search, and census the shared UpToDate evidence store.

The store is account-owned working material at ``scratch/uptodate/``.  An
ingest copies only a file the clinician deliberately names; ``sweep`` is a
read-only count of topic-shaped bodies elsewhere and never calls ``ingest``.

    python tools/uptodate_store.py ingest <dump> --dump-id <id> --module <name>
        --received-on YYYY-MM-DD
    python tools/uptodate_store.py search <query> [<query> ...]
    python tools/uptodate_store.py sweep [<root> ...]

The SQLite index is derived from the per-dump manifests and retained source
copies.  FTS5 keeps literal retrieval cheap without turning similarity into
evidence.  Exit 0 completed, exit 1 is a refused ingest, and exit 2 means the
command could not read a required source or store.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from console_codec import use_utf8
from repo_root import scratch_root

SCHEMA_VERSION = 1
STORE_DIRECTORY = "uptodate"
SOURCE_NAME = "source.txt"
DUMP_MANIFEST_NAME = "manifest.json"
INDEX_NAME = "index.sqlite"

TOPIC_MASTHEAD = re.compile(r"(?i)^\s*authors?\s*:\s*(.*)$")
SECTION_EDITOR = re.compile(r"(?i)^\s*section editors?\s*:")
REVIEW_LINE = re.compile(
    r"(?im)^\s*Literature review current through:\s*"
    r"(?P<month>[A-Z][a-z]{2})\s+(?P<year>\d{4})\.\s*$"
)
UPDATED_LINE = re.compile(
    r"(?im)^\s*This topic last updated:\s*"
    r"(?P<value>[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})\.\s*$"
)
SUMMARY = re.compile(r"(?im)^\s*SUMMARY AND RECOMMENDATIONS\s*$")


@dataclass(frozen=True)
class Topic:
    title: str
    authors: str
    literature_review_current_through: str
    last_updated: str
    has_summary: bool
    body: str


@dataclass(frozen=True)
class IngestReport:
    manifest: Path
    index: Path
    topics: int


@dataclass(frozen=True)
class SearchHit:
    dump_id: str
    title: str


@dataclass(frozen=True)
class SweepReport:
    files: int
    topic_bodies: int


def default_store() -> Path:
    """The one store in the checkout that owns account state."""
    override = os.environ.get("CLINICAL_UPTODATE_STORE")
    return Path(override).expanduser() if override else scratch_root() / STORE_DIRECTORY


def _parse_month(value: re.Match[str]) -> str:
    parsed = datetime.strptime(
        f"{value.group('month')} {value.group('year')}", "%b %Y"
    )
    return parsed.strftime("%Y-%m")


def parse_topics(text: str) -> list[Topic]:
    """Read authored topic bodies; cross-references never become topics."""
    lines = text.splitlines()
    starts: list[tuple[int, int, str, str]] = []
    for masthead_index, line in enumerate(lines):
        masthead = TOPIC_MASTHEAD.match(line)
        if not masthead:
            continue
        title_index = masthead_index - 1
        while title_index >= 0 and not lines[title_index].strip():
            title_index -= 1
        if title_index < 0:
            continue
        author = masthead.group(1).strip()
        if not author:
            author_index = masthead_index + 1
            authors: list[str] = []
            while author_index < len(lines):
                value = lines[author_index].strip()
                if SECTION_EDITOR.match(value):
                    break
                if value:
                    authors.append(value)
                author_index += 1
            author = " ".join(authors)
        starts.append((title_index, masthead_index, lines[title_index].strip(), author))

    topics: list[Topic] = []
    for position, (title_index, _masthead_index, title, authors) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        body = "\n".join(lines[title_index:end]).strip() + "\n"
        review = REVIEW_LINE.search(body)
        updated = UPDATED_LINE.search(body)
        if not authors or review is None or updated is None:
            raise ValueError(f"topic metadata is incomplete: {title}")
        last_updated = datetime.strptime(updated.group("value"), "%b %d, %Y").date()
        topics.append(
            Topic(
                title=title,
                authors=authors,
                literature_review_current_through=_parse_month(review),
                last_updated=last_updated.isoformat(),
                has_summary=bool(SUMMARY.search(body)),
                body=body,
            )
        )
    return topics


def topic_shape_count(text: str) -> int:
    """Count title-plus-masthead shapes without claiming their bodies are complete."""
    lines = text.splitlines()
    count = 0
    for index, line in enumerate(lines):
        if not TOPIC_MASTHEAD.match(line):
            continue
        above = index - 1
        while above >= 0 and not lines[above].strip():
            above -= 1
        if above >= 0:
            count += 1
    return count


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_manifest(manifest_path: Path, manifest: object) -> dict[str, object]:
    """Refuse malformed private state before it can grant citation membership."""
    dump_id = manifest_path.parent.name
    if not isinstance(manifest, dict):
        raise ValueError(f"manifest must hold an object: {dump_id}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported manifest schema: {dump_id}")
    if manifest.get("dump_id") != dump_id:
        raise ValueError(f"manifest dump id does not match its directory: {dump_id}")
    if not isinstance(manifest.get("module"), str) or not str(manifest["module"]).strip():
        raise ValueError(f"manifest module is missing: {dump_id}")
    try:
        date.fromisoformat(str(manifest.get("received_on", "")))
    except ValueError as error:
        raise ValueError(f"manifest received date is invalid: {dump_id}") from error
    if not re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", str(manifest.get("literature_review_current_through", ""))):
        raise ValueError(f"manifest currency stamp is invalid: {dump_id}")
    if manifest.get("source_file") != SOURCE_NAME:
        raise ValueError(f"manifest source file is invalid: {dump_id}")
    if not re.fullmatch(r"[0-9a-f]{64}", str(manifest.get("source_sha256", ""))):
        raise ValueError(f"manifest source digest is invalid: {dump_id}")
    topics = manifest.get("topics")
    if not isinstance(topics, list) or not topics:
        raise ValueError(f"manifest topics must be a nonempty list: {dump_id}")
    titles: set[str] = set()
    for topic in topics:
        if not isinstance(topic, dict):
            raise ValueError(f"manifest topic must hold an object: {dump_id}")
        title = topic.get("title")
        authors = topic.get("authors")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"manifest topic needs a title: {dump_id}")
        if not isinstance(authors, str) or not authors.strip():
            raise ValueError(f"manifest topic needs authors: {title}")
        try:
            date.fromisoformat(str(topic.get("last_updated", "")))
        except ValueError as error:
            raise ValueError(f"manifest topic has an invalid update date: {title}") from error
        if not isinstance(topic.get("has_summary"), bool):
            raise ValueError(f"manifest topic needs a summary flag: {title}")
        key = " ".join(title.casefold().split())
        if key in titles:
            raise ValueError(f"manifest has a duplicate topic title: {title}")
        titles.add(key)
    return manifest


def _manifest_rows(store: Path) -> Iterable[tuple[Path, dict[str, object]]]:
    dumps = store / "dumps"
    if not dumps.is_dir():
        return
    for manifest_path in sorted(dumps.glob(f"*/{DUMP_MANIFEST_NAME}")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(f"unreadable manifest: {manifest_path.name}: {error}") from error
        yield manifest_path, _validate_manifest(manifest_path, manifest)


def entitled_topics(store: Path | None = None) -> set[str]:
    """Every topic deliberately ingested into any per-dump manifest."""
    root = (store or default_store()).resolve()
    titles: set[str] = set()
    for _path, manifest in _manifest_rows(root):
        rows = manifest.get("topics")
        if not isinstance(rows, list):
            raise ValueError("manifest topics must be a list")
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("title"), str):
                raise ValueError("manifest topic needs a title")
            titles.add(row["title"])
    return titles


def topic_currencies(store: Path | None = None) -> dict[str, str]:
    """Newest literature-review month per accumulated topic title."""
    root = (store or default_store()).resolve()
    rows: dict[str, tuple[str, str]] = {}
    for _path, manifest in _manifest_rows(root):
        received = str(manifest.get("received_on", ""))
        currency = str(manifest.get("literature_review_current_through", ""))
        for topic in manifest.get("topics", []):
            if not isinstance(topic, dict) or not isinstance(topic.get("title"), str):
                raise ValueError("manifest topic needs a title")
            title = topic["title"]
            key = " ".join(title.casefold().split())
            if key not in rows or received > rows[key][0]:
                rows[key] = (received, currency)
    return {key: value[1] for key, value in rows.items()}


def topic_record(title: str, store: Path | None = None) -> tuple[dict[str, object], dict[str, object]] | None:
    """Return the newest manifest/topic pair with an exact normalized title."""
    wanted = " ".join(title.casefold().split())
    matches: list[tuple[dict[str, object], dict[str, object]]] = []
    for _path, manifest in _manifest_rows((store or default_store()).resolve()):
        for row in manifest.get("topics", []):
            if isinstance(row, dict) and " ".join(str(row.get("title", "")).casefold().split()) == wanted:
                matches.append((manifest, row))
    if not matches:
        return None
    return max(matches, key=lambda item: str(item[0].get("received_on", "")))


def manifest_for_dump(dump_id: str, store: Path | None = None) -> dict[str, object] | None:
    for _path, manifest in _manifest_rows((store or default_store()).resolve()):
        if manifest.get("dump_id") == dump_id:
            return manifest
    return None


def source_topic(dump_id: str, title: str, store: Path | None = None) -> Topic | None:
    root = (store or default_store()).resolve()
    manifest = manifest_for_dump(dump_id, root)
    if manifest is None:
        return None
    source = root / "dumps" / dump_id / str(manifest.get("source_file", SOURCE_NAME))
    if not source.is_file() or _sha256(source) != manifest.get("source_sha256"):
        raise ValueError(f"source does not match manifest: {dump_id}")
    wanted = " ".join(title.casefold().split())
    for topic in parse_topics(source.read_text(encoding="utf-8", errors="replace")):
        if " ".join(topic.title.casefold().split()) == wanted:
            return topic
    return None


def rebuild_index(store: Path) -> Path:
    store.mkdir(parents=True, exist_ok=True)
    target = store / INDEX_NAME
    building = store / f"{INDEX_NAME}.building"
    if building.exists():
        building.unlink()
    connection = sqlite3.connect(building)
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE topic_fts USING fts5(dump_id UNINDEXED, title, body)"
        )
        for manifest_path, manifest in _manifest_rows(store):
            source_path = manifest_path.with_name(str(manifest.get("source_file", SOURCE_NAME)))
            if not source_path.is_file() or _sha256(source_path) != manifest.get("source_sha256"):
                raise ValueError(f"source does not match manifest: {manifest_path.parent.name}")
            bodies = {topic.title: topic.body for topic in parse_topics(source_path.read_text(encoding="utf-8", errors="replace"))}
            for row in manifest["topics"]:
                title = str(row["title"])
                if title not in bodies:
                    raise ValueError(f"manifest topic missing from source: {title}")
                connection.execute(
                    "INSERT INTO topic_fts(dump_id, title, body) VALUES (?, ?, ?)",
                    (manifest["dump_id"], title, bodies[title]),
                )
        connection.commit()
    finally:
        connection.close()
    os.replace(building, target)
    return target


def ingest_dump(
    source: Path,
    store: Path | None,
    *,
    dump_id: str,
    module: str,
    received_on: date,
) -> IngestReport:
    source = source.expanduser().resolve()
    root = (store or default_store()).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"no dump file named {source.name}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", dump_id):
        raise ValueError("dump id must use lowercase letters, numbers, dot, underscore, or hyphen")
    destination = root / "dumps" / dump_id
    if destination.exists():
        raise ValueError(f"dump id already exists: {dump_id}")
    text = source.read_text(encoding="utf-8", errors="replace")
    topics = parse_topics(text)
    if not topics:
        raise ValueError(f"no authored topic body found in {source.name}")
    keys = [" ".join(topic.title.casefold().split()) for topic in topics]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate topic title in one dump")
    currencies = {topic.literature_review_current_through for topic in topics}
    if len(currencies) != 1:
        raise ValueError("one dump must carry one literature-review currency stamp")

    destination.mkdir(parents=True)
    copied = destination / SOURCE_NAME
    try:
        shutil.copyfile(source, copied)
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "dump_id": dump_id,
            "module": module,
            "received_on": received_on.isoformat(),
            "literature_review_current_through": next(iter(currencies)),
            "source_file": SOURCE_NAME,
            "source_sha256": _sha256(copied),
            "topics": [
                {
                    "title": topic.title,
                    "authors": topic.authors,
                    "last_updated": topic.last_updated,
                    "has_summary": topic.has_summary,
                }
                for topic in topics
            ],
        }
        manifest_path = destination / DUMP_MANIFEST_NAME
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        index = rebuild_index(root)
    except Exception:
        shutil.rmtree(destination)
        raise
    return IngestReport(manifest_path, index, len(topics))


def search(store: Path | None, query: str, *, limit: int = 20) -> list[SearchHit]:
    root = (store or default_store()).expanduser().resolve()
    database = root / INDEX_NAME
    if not database.is_file():
        raise ValueError(f"no UpToDate index at {database}")
    connection = sqlite3.connect(database)
    try:
        rows = connection.execute(
            "SELECT dump_id, title FROM topic_fts WHERE topic_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, limit),
        ).fetchall()
    finally:
        connection.close()
    return [SearchHit(str(row[0]), str(row[1])) for row in rows]


def sweep_unfiled(scan_root: Path, store: Path | None = None) -> SweepReport:
    """Count topic-shaped files outside the store without storing any content."""
    root = scan_root.expanduser().resolve()
    evidence_store = (store or default_store()).expanduser().resolve()
    files = 0
    bodies = 0
    if not root.is_dir():
        return SweepReport(0, 0)
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in {".txt", ".md"}:
            continue
        resolved = path.resolve()
        if resolved.is_relative_to(evidence_store):
            continue
        try:
            count = topic_shape_count(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if count:
            files += 1
            bodies += count
    return SweepReport(files, bodies)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", type=Path, default=default_store())
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest")
    ingest.add_argument("source", type=Path)
    ingest.add_argument("--dump-id", required=True)
    ingest.add_argument("--module", required=True)
    ingest.add_argument("--received-on", type=date.fromisoformat, required=True)
    find = sub.add_parser("search")
    find.add_argument("queries", nargs="+")
    find.add_argument("--limit", type=int, default=20)
    sweep = sub.add_parser("sweep")
    sweep.add_argument("roots", nargs="*", type=Path)
    return parser


def main(argv: list[str]) -> int:
    try:
        args = _parser().parse_args(argv)
        if args.command == "ingest":
            report = ingest_dump(
                args.source,
                args.store,
                dump_id=args.dump_id,
                module=args.module,
                received_on=args.received_on,
            )
            print(f"ingested {report.topics} topic(s); manifest {report.manifest.name}; index {report.index.name}")
        elif args.command == "search":
            for query in args.queries:
                hits = search(args.store, query, limit=args.limit)
                print(f"QUERY {query}: {len(hits)} hit(s)")
                for hit in hits:
                    print(f"  {hit.dump_id}: {hit.title}")
        else:
            roots = args.roots or [scratch_root()]
            reports = [sweep_unfiled(root, args.store) for root in roots]
            print(
                f"unfiled topic-shaped material: {sum(row.files for row in reports)} file(s), "
                f"{sum(row.topic_bodies for row in reports)} topic body/bodies"
            )
            print("nothing was ingested; pass a deliberate file to the ingest command")
        return 0
    except (OSError, UnicodeError, ValueError, sqlite3.Error) as error:
        print(f"uptodate-store: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
