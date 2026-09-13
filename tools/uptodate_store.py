"""Ingest, index, search, and census the shared UpToDate evidence store.

The store is account-owned working material at ``scratch/uptodate/``.  An
ingest copies only a file the clinician deliberately names; ``sweep`` is a
read-only count of topic-shaped bodies elsewhere and never calls ``ingest``.

    python tools/uptodate_store.py ingest <dump> --dump-id <id> --module <name>
        --received-on YYYY-MM-DD [--references <file>]
    python tools/uptodate_store.py search <query> [<query> ...]
    python tools/uptodate_store.py sweep [<root> ...]

The SQLite index is derived from the per-dump manifests and retained source
copies.  FTS5 keeps literal retrieval cheap without turning similarity into
evidence.  Topic coverage uses the widest of three independently counted
markers: author mastheads, publisher-review lines, and last-update lines.  An
input carrying none of those markers remains outside that floor; the command
states that ceiling rather than calling it complete coverage.  Exit 0 means
completed; exit 2 covers every refusal or unreadable source.
"""

from __future__ import annotations

import argparse
import file_digest
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

import docx_read
from console_codec import require_python_floor, use_utf8
from repo_root import scratch_root

SCHEMA_VERSION = 1
STORE_DIRECTORY = "uptodate"
SOURCE_NAME = "source.txt"
REFERENCE_NAME = "references.txt"
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
class _TopicBlock:
    title_index: int | None
    masthead_index: int
    end_index: int
    title: str
    authored_body: str


@dataclass(frozen=True)
class StoredTopic:
    """The citation-verification fields retained in a validated manifest."""

    title: str
    authors: str
    last_updated: str
    received_on: str = ""
    literature_review_current_through: str = ""


@dataclass(frozen=True)
class StoreSnapshot:
    """One validated read of every field the evidence graders join."""

    source_digests: frozenset[str]
    topics: tuple[StoredTopic, ...]
    currencies: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class IngestReport:
    manifest: Path
    index: Path
    blocks_read: int
    candidates: int
    unread: int
    merged: int


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


def topic_key(title: str) -> str:
    """Case-and-spacing identity for exact stored-topic lookup."""
    return " ".join(title.casefold().split())


def citation_title_key(title: str) -> str:
    """Punctuation-insensitive title identity used by citation joins."""
    return " ".join(re.sub(r"[^0-9a-z]+", " ", title.casefold()).split())


def topic_population_count(text: str) -> int:
    """Independent floor: the widest authored/reviewed/updated marker count."""
    authored = sum(bool(TOPIC_MASTHEAD.match(line)) for line in text.splitlines())
    return max(authored, len(REVIEW_LINE.findall(text)), len(UPDATED_LINE.findall(text)))


def _topic_blocks(text: str) -> list[_TopicBlock]:
    """Locate candidate titles and byte-preserving authored blocks."""
    lines = text.splitlines(keepends=True)
    mastheads = [index for index, line in enumerate(lines) if TOPIC_MASTHEAD.match(line)]
    candidates: list[int | None] = []
    for masthead_index in mastheads:
        title_index = masthead_index - 1
        while title_index >= 0 and not lines[title_index].strip():
            title_index -= 1
        candidates.append(title_index if title_index >= 0 else None)

    blocks: list[_TopicBlock] = []
    for position, masthead_index in enumerate(mastheads):
        next_masthead = mastheads[position + 1] if position + 1 < len(mastheads) else len(lines)
        next_title = candidates[position + 1] if position + 1 < len(candidates) else None
        end_index = (
            next_title
            if next_title is not None and next_title > masthead_index
            else next_masthead
        )
        title_index = candidates[position]
        blocks.append(
            _TopicBlock(
                title_index=title_index,
                masthead_index=masthead_index,
                end_index=end_index,
                title=lines[title_index].strip() if title_index is not None else "",
                authored_body="".join(lines[masthead_index:end_index]),
            )
        )
    return blocks


def _unique_blocks(blocks: list[_TopicBlock]) -> tuple[list[_TopicBlock], int]:
    retained: list[_TopicBlock] = []
    seen: set[str] = set()
    for block in blocks:
        if block.authored_body in seen:
            continue
        seen.add(block.authored_body)
        retained.append(block)
    return retained, len(blocks) - len(retained)


def _untitled_count(blocks: list[_TopicBlock]) -> int:
    retained, _merged = _unique_blocks(blocks)
    by_candidate: dict[str, list[_TopicBlock]] = {}
    for block in retained:
        if block.title:
            by_candidate.setdefault(topic_key(block.title), []).append(block)
    ambiguous = {key for key, group in by_candidate.items() if len(group) >= 2}
    return sum(
        not block.title or topic_key(block.title) in ambiguous
        for block in blocks
    )


def parse_topics(text: str) -> list[Topic]:
    """Read authored topic bodies; cross-references never become topics."""
    population = topic_population_count(text)
    blocks = _topic_blocks(text)
    retained, merged = _unique_blocks(blocks)
    untitled = _untitled_count(blocks)
    if untitled:
        raise ValueError(
            f"untitled topic blocks: untitled {untitled} of {population}; write a titled copy, "
            "keep the block-to-title mapping in the run directory, and ingest the copy"
        )
    lines = text.splitlines(keepends=True)
    topics: list[Topic] = []
    for block in retained:
        masthead = TOPIC_MASTHEAD.match(lines[block.masthead_index])
        if masthead is None:
            raise ValueError("topic masthead disappeared during parsing")
        author = masthead.group(1).strip()
        if not author:
            author_index = block.masthead_index + 1
            authors: list[str] = []
            while author_index < block.end_index:
                value = lines[author_index].strip()
                if SECTION_EDITOR.match(value):
                    break
                if value:
                    authors.append(value)
                author_index += 1
            author = " ".join(authors)
        title = block.title
        body = "".join(lines[block.title_index:block.end_index]).strip() + "\n"
        review = REVIEW_LINE.search(body)
        updated = UPDATED_LINE.search(body)
        if not author or review is None or updated is None:
            raise ValueError(f"topic metadata is incomplete: {title}")
        last_updated = datetime.strptime(updated.group("value"), "%b %d, %Y").date()
        topics.append(
            Topic(
                title=title,
                authors=author,
                literature_review_current_through=_parse_month(review),
                last_updated=last_updated.isoformat(),
                has_summary=bool(SUMMARY.search(body)),
                body=body,
            )
        )
    marker_counts = (
        len(blocks),
        len(REVIEW_LINE.findall(text)),
        len(UPDATED_LINE.findall(text)),
    )
    if len(topics) + merged != population or any(count != population for count in marker_counts):
        raise ValueError(
            f"topic population incomplete: read {len(topics) + merged} of {population}; "
            f"author/review/update markers are {marker_counts}"
        )
    return topics


def topic_shape_count(text: str) -> int:
    """Report the widest of three markers without claiming complete recognition."""
    return topic_population_count(text)


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
    source_path = manifest_path.parent / SOURCE_NAME
    if not source_path.is_file() or file_digest.sha256(source_path) != manifest["source_sha256"]:
        raise ValueError(f"source does not match manifest: {dump_id}")
    reference_file = manifest.get("reference_file")
    reference_digest = manifest.get("reference_sha256")
    if reference_file is not None or reference_digest is not None:
        if reference_file != REFERENCE_NAME:
            raise ValueError(f"manifest reference file is invalid: {dump_id}")
        if not re.fullmatch(r"[0-9a-f]{64}", str(reference_digest or "")):
            raise ValueError(f"manifest reference digest is invalid: {dump_id}")
        reference_path = manifest_path.parent / REFERENCE_NAME
        if not reference_path.is_file() or file_digest.sha256(reference_path) != reference_digest:
            raise ValueError(f"reference list does not match manifest: {dump_id}")
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
        key = topic_key(title)
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


def store_snapshot(store: Path | None = None) -> StoreSnapshot:
    """Read filed digests, newest topic mastheads, and currencies together."""
    root = (store or default_store()).resolve()
    digests: set[str] = set()
    newest: dict[str, tuple[str, StoredTopic, str]] = {}
    for path, manifest in _manifest_rows(root):
        digests.add(str(manifest["source_sha256"]))
        received = str(manifest["received_on"])
        currency = str(manifest["literature_review_current_through"])
        for row in manifest.get("topics", []):
            if not isinstance(row, dict):
                raise ValueError("manifest topic must hold an object")
            title, authors, last_updated = (
                row.get("title"),
                row.get("authors"),
                row.get("last_updated"),
            )
            if not all(isinstance(value, str) for value in (title, authors, last_updated)):
                raise ValueError("manifest topic needs title, authors and last updated")
            topic = StoredTopic(title, authors, last_updated, received, currency)
            key = citation_title_key(title)
            prior = newest.get(key)
            if prior is not None and received == prior[0] and (
                topic != prior[1] or currency != prior[2]
            ):
                raise ValueError(
                    f"topic has conflicting versions received on {received}: {title}"
                )
            if prior is None or received > prior[0]:
                newest[key] = (received, topic, currency)
    return StoreSnapshot(
        frozenset(digests),
        tuple(row[1] for _key, row in sorted(newest.items())),
        tuple((key, row[2]) for key, row in sorted(newest.items())),
    )


def entitled_topic_details(store: Path | None = None) -> tuple[StoredTopic, ...]:
    """Citation-verification fields from the newest accumulated topic versions."""
    return store_snapshot(store).topics


def entitled_topics(store: Path | None = None) -> set[str]:
    """Every topic deliberately ingested into any per-dump manifest."""
    return {topic.title for topic in entitled_topic_details(store)}


def is_filed_source(
    source: Path,
    store: Path | None = None,
    *,
    snapshot: StoreSnapshot | None = None,
) -> bool:
    """Whether ``source`` exactly matches a validated dump manifest."""
    digest = file_digest.sha256(source.expanduser().resolve())
    return digest in (snapshot or store_snapshot(store)).source_digests


def topic_currencies(store: Path | None = None) -> dict[str, str]:
    """Newest literature-review month per accumulated topic title."""
    return dict(store_snapshot(store).currencies)


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
    if not source.is_file() or file_digest.sha256(source) != manifest.get("source_sha256"):
        raise ValueError(f"source does not match manifest: {dump_id}")
    wanted = topic_key(title)
    for topic in parse_topics(source.read_text(encoding="utf-8", errors="replace")):
        if topic_key(topic.title) == wanted:
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
            if not source_path.is_file() or file_digest.sha256(source_path) != manifest.get("source_sha256"):
                raise ValueError(f"source does not match manifest: {manifest_path.parent.name}")
            normalized_source = docx_read.normalize(
                source_path.read_text(encoding="utf-8", errors="replace")
            )
            for report_line in docx_read.non_latin_letter_report(normalized_source):
                print(
                    f"dump {manifest_path.parent.name}: {report_line}",
                    file=sys.stderr,
                )
            bodies = {
                topic_key(topic.title): topic.body
                for topic in parse_topics(normalized_source)
            }
            for row in manifest["topics"]:
                title = str(row["title"])
                normalized_title = docx_read.normalize(title)
                key = topic_key(normalized_title)
                if key not in bodies:
                    raise ValueError(f"manifest topic missing from source: {title}")
                connection.execute(
                    "INSERT INTO topic_fts(dump_id, title, body) VALUES (?, ?, ?)",
                    (manifest["dump_id"], normalized_title, bodies[key]),
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
    references: Path | None = None,
) -> IngestReport:
    source = source.expanduser().resolve()
    root = (store or default_store()).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"no dump file named {source.name}")
    if references is not None:
        references = references.expanduser().resolve()
        if not references.is_file():
            raise ValueError(f"no reference-list file named {references.name}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", dump_id):
        raise ValueError("dump id must use lowercase letters, numbers, dot, underscore, or hyphen")
    destination = root / "dumps" / dump_id
    if destination.exists():
        raise ValueError(f"dump id already exists: {dump_id}")
    text = source.read_text(encoding="utf-8", errors="replace")
    topics = parse_topics(text)
    merged = len(_topic_blocks(text)) - len(topics)
    if not topics:
        raise ValueError(f"no authored topic body found in {source.name}")
    keys = [topic_key(topic.title) for topic in topics]
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
            "source_sha256": file_digest.sha256(copied),
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
        if references is not None:
            copied_references = destination / REFERENCE_NAME
            shutil.copyfile(references, copied_references)
            manifest["reference_file"] = REFERENCE_NAME
            manifest["reference_sha256"] = file_digest.sha256(copied_references)
        manifest_path = destination / DUMP_MANIFEST_NAME
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        index = rebuild_index(root)
    except Exception:
        shutil.rmtree(destination)
        raise
    population = topic_population_count(text)
    read = len(topics) + merged
    return IngestReport(manifest_path, index, read, population, population - read, merged)


def search(store: Path | None, query: str, *, limit: int = 20) -> list[SearchHit]:
    root = (store or default_store()).expanduser().resolve()
    database = root / INDEX_NAME
    if not database.is_file():
        raise ValueError(f"no UpToDate index at {database}")
    connection = sqlite3.connect(database)
    try:
        rows = connection.execute(
            "SELECT dump_id, title FROM topic_fts WHERE topic_fts MATCH ? ORDER BY rank LIMIT ?",
            (docx_read.normalize(query), limit),
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
    filed_hashes = {
        str(manifest["source_sha256"])
        for _path, manifest in _manifest_rows(evidence_store)
    }
    if not root.is_dir():
        return SweepReport(0, 0)
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in {".txt", ".md"}:
            continue
        resolved = path.resolve()
        if resolved.is_relative_to(evidence_store):
            continue
        if file_digest.sha256(resolved) in filed_hashes:
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
    ingest.add_argument("--references", type=Path)
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
                references=args.references,
            )
            print(
                f"ingested topic blocks read {report.blocks_read} of {report.candidates}; "
                f"merged {report.merged}; unread {report.unread}; "
                f"manifest {report.manifest.name}; index {report.index.name}"
            )
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
            print(
                "candidate bound is the widest author/review/update marker count per file; "
                "a body carrying none of those markers is outside this report"
            )
        return 0
    except (OSError, UnicodeError, ValueError, sqlite3.Error) as error:
        print(f"uptodate-store: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
