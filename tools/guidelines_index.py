"""Build the FTS5 full-text index over extracted guideline text.

    python tools/guidelines_index.py <text-dir> [<db-path>]

``<text-dir>`` is the extracted-text directory produced by ``guidelines_extract.py``
(#80). This tool never opens a PDF, so it is stdlib only and carries no build
dependency; the PDF library lives entirely on the extraction side.

**Keyword search, deliberately, and not embeddings.** A full-text hit is a literal
string on a literal page, checkable in one jump against the source. An embedding hit
is a similarity score, and a score is not evidence. Nine societies with overlapping
scope, spanning 2009 to 2026, means a fuzzy match can return the right concept from
the wrong society, wrong year or wrong population *with a citation attached* -- and
more documents makes that likelier, not less. The concession is real: this cannot
reach "renal replacement therapy" from "kidney failure". The mitigation is that the
agent knows the synonyms and can fire six exact queries where a vector store would
take one fuzzy one. ``guidelines_search.py`` takes several queries per run for
exactly that reason.

**The database is written outside the repo and there is a guard, not a convention.**
``reference/`` and ``scratch/`` are both materialized into every worktree, so an
index committed or dropped in either is duplicated into all of them. ``repo_root.ensure_outside_checkout`` refuses any target inside *any* git
checkout, which is what keeps `git status` clean after a build. Whether the index
should ever *ship* is #87, and it is blocked; nothing here presumes an answer.

**That guard used to live here, and it was the weaker of the three copies #176
found.** It compared the target against this worktree and the clone that owns it,
which is blind to a sibling worktree -- the ordinary shape here, not an exotic one.
It walks up for a ``.git`` entry now, in one place, beside the resolver that already
answers the other half of the same question. ``main`` needs no new handler: the
refusal is a ``ValueError`` and lands on the one already there.

**The text-directory contract.** One layout: ``<text-dir>/<doc-id>.txt``, pages
separated by form feed. That is what ``tools/guidelines_extract.py`` emits and what
``pdftotext`` emits.

This used to read a second layout as well -- per-page files at
``<text-dir>/<doc-id>/page-0007.txt`` -- because "emit per-page text" admits both and
#80 had not landed. #80 landed emitting form feeds, so that branch is gone: a branch
no producer feeds is a branch no reader checks. **It also took a whole class of
ambiguity with it.** Reading an all-digit stem as a page number collides with a real
naming scheme -- ``USPSTF/2021.txt`` and ``USPSTF/2022.txt`` would collapse into one
document called ``USPSTF`` carrying pages 2021 and 2022, two documents lost and two
page citations invented with nothing downstream able to tell. That was a live bug
here, fixed by requiring a ``page`` prefix. With one layout there are no page files
at all, so the question cannot be asked.

``<doc-id>`` is the path relative to the text directory, so the society is its first
segment and a hit names a file that can be opened beside the PDF of the same name. A
blank page keeps its number: dropping it would slide every later page's citation by
one, and a citation off by a page is worse than no citation.

``manifest.json`` supplies ``title``, ``society`` and ``document_class`` per document
and names the clean commit that produced the extracted text. An index build requires
it: without the manifest, the shared text directory has no owner. A dirty, foreign,
unstamped or unreadable manifest **raises** rather than degrading to derived values.
``--allow-untrusted-provenance`` is the explicit development escape hatch; the index
records why its source was untrusted so a later search cannot launder the override.
A manifest entry with no extracted text is likewise **reported**, never swallowed,
because #80's contract is a recorded failure rather than a silent skip.
"""

from __future__ import annotations

import argparse
import artifact_lock
import artifact_provenance
import json
import os
import sqlite3
import sys
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from console_codec import use_utf8
from repo_root import ensure_outside_checkout, main_repo_root

SCHEMA_VERSION = 1
MANIFEST_NAME = "manifest.json"
UNCLASSIFIED = "unclassified"
DATABASE_ENVIRONMENT_VARIABLE = "CLINICAL_GUIDELINES_INDEX"
UntrustedProvenance = artifact_provenance.UntrustedProvenance

# A page break inside a single-file document. pdftotext writes form feed and so does
# every other extractor that keeps page boundaries at all.
PAGE_BREAK = "\f"

# The one key a manifest entry names its document with. Single on purpose: #80 owns
# the manifest's shape, and an alias list would absorb a mismatch instead of raising
# on it, leaving every title and document class quietly blank.
DOC_ID_KEY = "doc_id"


@dataclass(frozen=True)
class Page:
    number: int
    text: str


@dataclass(frozen=True)
class _FormFeedFile:
    """One document held as a single ``.txt`` with form feeds between pages."""

    path: Path

    def pages(self) -> list[Page]:
        body = _read(self.path)
        return [Page(n, text) for n, text in enumerate(body.split(PAGE_BREAK), start=1)]


def _read(path: Path) -> str:
    # errors='replace' rather than a raise: #80 records the codec it decoded with, and
    # one undecodable byte should cost one character, not a whole document's pages.
    return path.read_text(encoding="utf-8", errors="replace")


@dataclass(frozen=True)
class Document:
    doc_id: str  # path relative to the text directory, posix-style, no suffix
    society: str | None  # first path segment unless the manifest says otherwise
    title: str | None
    document_class: str
    pages: list[Page]


@dataclass(frozen=True)
class ExtractedDocument:
    """One successful #80 extraction, joined to its manifest record."""

    doc_id: str
    society: str | None
    title: str | None
    source: str
    document_class: str
    pages: list[Page]
    boilerplate: tuple[str, ...]
    margin_stripped: tuple[str, ...]
    year_page_counts: dict[str, int] | None


@dataclass(frozen=True)
class BuildReport:
    database: Path
    documents: int
    pages: int
    characters: int
    manifest_only: list[str]  # named by the manifest, no extracted text found


def default_database() -> Path:
    """Beside the sources, outside every checkout. Overridable per machine."""
    override = os.environ.get(DATABASE_ENVIRONMENT_VARIABLE)
    if override:
        return Path(override).expanduser()
    return main_repo_root().parent / "guidelines-index" / "guidelines.sqlite"


# Why *this* artifact stays out, which is not why the other two do: the index is
# large, and ``reference/`` and ``scratch/`` are both materialized into every
# worktree, so one dropped in either is duplicated into all of them. Whether it
# should ever *ship* is #87 and is blocked; nothing here presumes an answer.
# **How large is deliberately not stated here** -- #143, and this file has
# carried that figure in two units for the same bytes.
#
# **This is the site whose detection rule changed on #176.** It compared the
# target against ``[this worktree, main_repo_root()]``, which is blind to a
# *sibling* worktree -- and under ``.claude/worktrees/`` a sibling is the
# ordinary case here rather than an exotic one. ``enclosing_checkout`` walks up
# for a ``.git`` entry instead, so it catches all three for the same cost. The
# one property the old rule was careful about survives for free: containment is
# path ancestry, so ``clinical_skills-notes`` is correctly outside
# ``clinical_skills``.
WHY_OUTSIDE = (
    "The index is a build artifact and stays outside every checkout -- see issue "
    f"#87. Pass a path beside the guideline sources, or set {DATABASE_ENVIRONMENT_VARIABLE}."
)


def normalize_doc_id(value: str) -> str:
    """How a document is named. Public because it is a rule two modules share.

    `threshold_sheet.gate_watermark` joins a threshold sheet's `document` cell to
    these keys, and a second spelling of this rule over there would read as agreement
    while covering less -- `reference_scan.py` importing `docx_write.REFERENCE_HEADING`,
    for that module's reason. **Renamed rather than aliased**: an alias leaves the
    owner with two public names for one rule, which is the thing this comment argues
    against, one level up.
    """
    cleaned = value.strip().replace("\\", "/").strip("/")
    return cleaned[:-4] if cleaned.lower().endswith(".txt") else cleaned


def _read_manifest(
    text_dir: Path | str,
    *,
    allow_untrusted_provenance: bool = False,
    expected_commit: str | None = None,
) -> tuple[dict[str, dict], artifact_provenance.ProvenanceCheck | None]:
    """``manifest.json`` keyed by document id, or ``{}`` when there is none.

    A list of entries or ``{"documents": [...]}``, each entry naming its document
    with ``doc_id``. **Every way of being present but unusable raises** -- bad JSON,
    the wrong top-level shape, or not one entry carrying ``doc_id``. Absent is the
    only quiet case, because absent is the only one that is a choice: a manifest read
    but silently understood as empty leaves every title and document class blank,
    which is indistinguishable from a corpus that never had them.
    """
    path = Path(text_dir) / MANIFEST_NAME
    if not path.exists():
        return {}, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as bad:
        raise ValueError(f"{path} is present but could not be read as JSON: {bad}") from bad

    if isinstance(data, dict):
        provenance = artifact_provenance.check_producer(
            data.get("producer"),
            path,
            allow_untrusted=allow_untrusted_provenance,
            expected_commit=expected_commit,
        )
        data = data.get("documents")
    else:
        provenance = artifact_provenance.check_producer(
            None,
            path,
            allow_untrusted=allow_untrusted_provenance,
            expected_commit=expected_commit,
        )
    if not isinstance(data, list):
        raise ValueError(
            f"{path} is not a list of entries or a {{\"documents\": [...]}} object. "
            "#80 owns this file's shape; if it changed, change this reader rather "
            "than letting it read as empty."
        )
    entries = {
        normalize_doc_id(str(entry[DOC_ID_KEY])): entry
        for entry in data
        if isinstance(entry, dict) and entry.get(DOC_ID_KEY)
    }
    if not entries:
        raise ValueError(
            f"no entry in {path} carries a {DOC_ID_KEY!r}, so nothing in it can be "
            "matched to a document."
        )
    return entries, provenance


def read_manifest(
    text_dir: Path | str, *, allow_untrusted_provenance: bool = False
) -> dict[str, dict]:
    """Read and provenance-check ``manifest.json``; absent remains an optional input."""
    return _read_manifest(
        text_dir, allow_untrusted_provenance=allow_untrusted_provenance
    )[0]


def _describe(doc_id: str, entry: dict) -> tuple[str | None, str | None, str]:
    derived_society = doc_id.split("/")[0] if "/" in doc_id else None
    society = entry.get("society") or derived_society
    title = entry.get("title") or None
    document_class = entry.get("document_class") or UNCLASSIFIED
    return society, title, str(document_class)


def _sources(text_dir: Path) -> dict[str, _FormFeedFile]:
    """Every ``*.txt`` under the text directory, keyed by document id.

    One ``.txt`` is one document, whatever it is called. There is no filename that
    means anything other than a document id, which is what removing the per-page
    layout bought.
    """
    return {
        path.relative_to(text_dir).with_suffix("").as_posix(): _FormFeedFile(path)
        for path in sorted(text_dir.rglob("*.txt"))
    }


def discover(
    text_dir: Path | str, *, allow_untrusted_provenance: bool = False
) -> Iterator[Document]:
    """Yield one ``Document`` per source document, in document-id order.

    A generator rather than a list: 6,800 pages of extracted text is tens of
    megabytes, and only one document needs to be in memory at a time.
    """
    text_dir = Path(text_dir)
    if not text_dir.is_dir():
        raise FileNotFoundError(f"no extracted-text directory at {text_dir}")
    manifest = read_manifest(
        text_dir, allow_untrusted_provenance=allow_untrusted_provenance
    )
    yield from _discover(text_dir, manifest)


def _discover(text_dir: Path, manifest: dict[str, dict]) -> Iterator[Document]:
    """Read documents against the already-validated manifest from this operation."""
    sources = _sources(text_dir)

    for doc_id in sorted(sources):
        pages = sources[doc_id].pages()
        society, title, document_class = _describe(doc_id, manifest.get(doc_id, {}))
        yield Document(
            doc_id=doc_id,
            society=society,
            title=title,
            document_class=document_class,
            pages=pages,
        )


def read_extracted_corpus(
    text_dir: Path | str, *, allow_untrusted_provenance: bool = False
) -> list[ExtractedDocument]:
    """Read and validate #80's text/manifest handoff as one corpus.

    Unlike :func:`discover`, this is for consumers whose results depend on the
    manifest. Required keys are checked by presence, not truthiness: ``title``
    may legitimately be null, but an absent title key means the producer and
    consumer no longer agree on the contract.
    """
    text_dir = Path(text_dir)
    manifest = read_manifest(
        text_dir, allow_untrusted_provenance=allow_untrusted_provenance
    )
    if not manifest:
        raise ValueError(f"{text_dir / MANIFEST_NAME} is required")

    required = {
        "society",
        "title",
        "source",
        "output",
        "document_class",
        "pages",
        "boilerplate",
        "margin_stripped",
    }
    failed = sorted(doc_id for doc_id, entry in manifest.items() if entry.get("error"))
    if failed:
        raise ValueError(f"the extraction manifest records failed documents: {failed}")
    for doc_id, entry in manifest.items():
        missing_keys = sorted(required - entry.keys())
        if missing_keys:
            raise ValueError(f"{doc_id}: manifest entry is missing keys: {missing_keys}")
        if not entry["source"]:
            raise ValueError(f"{doc_id}: manifest entry has no source filename")
        if not entry["output"]:
            raise ValueError(f"{doc_id}: manifest entry has no output filename")

    discovered = {document.doc_id: document for document in _discover(text_dir, manifest)}
    expected = set(manifest)
    if set(discovered) != expected:
        missing = sorted(expected - set(discovered))
        extra = sorted(set(discovered) - expected)
        raise ValueError(
            f"extracted text and manifest disagree (missing text: {missing}; extra text: {extra})"
        )

    result: list[ExtractedDocument] = []
    for doc_id in sorted(expected):
        entry = manifest[doc_id]
        document = discovered[doc_id]
        if entry["pages"] != len(document.pages):
            raise ValueError(
                f"{doc_id}: manifest says {entry['pages']} pages, "
                f"extracted text contains {len(document.pages)}"
            )
        result.append(
            ExtractedDocument(
                doc_id=doc_id,
                society=entry["society"],
                title=entry["title"],
                source=str(entry["source"]),
                document_class=str(entry["document_class"]),
                pages=document.pages,
                boilerplate=tuple(entry["boilerplate"]),
                margin_stripped=tuple(entry["margin_stripped"]),
                year_page_counts=(
                    {str(year): int(count) for year, count in entry["year_page_counts"].items()}
                    if "year_page_counts" in entry
                    else None
                ),
            )
        )
    return result


SCHEMA = """
CREATE TABLE document (
    doc_pk         INTEGER PRIMARY KEY,
    doc_id         TEXT NOT NULL UNIQUE,
    society        TEXT,
    title          TEXT,
    document_class TEXT NOT NULL,
    pages          INTEGER NOT NULL
);
CREATE TABLE page (
    page_id INTEGER PRIMARY KEY,
    doc_pk  INTEGER NOT NULL REFERENCES document(doc_pk),
    number  INTEGER NOT NULL,
    text    TEXT NOT NULL
);
CREATE INDEX page_by_document ON page(doc_pk, number);
-- External content: the text lives once, in `page`. `page_fts` keeps only the
-- inverted index, which is what keeps the file near the size of the text itself.
CREATE VIRTUAL TABLE page_fts USING fts5(
    text,
    content='page',
    content_rowid='page_id',
    tokenize='unicode61 remove_diacritics 2'
);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def build(
    text_dir: Path | str,
    database: Path | str | None = None,
    *,
    allow_untrusted_provenance: bool = False,
) -> BuildReport:
    """Index every document under ``text_dir``, replacing any existing index.

    Built into a sibling temp file and moved into place, so a build that dies part
    way leaves the previous index intact rather than a half-written one that opens
    fine and answers short.
    """
    text_dir = Path(text_dir).resolve()
    with ExitStack() as locks:
        locks.enter_context(
            artifact_lock.hold(
                text_dir, "reading extracted guideline text for an index build"
            )
        )
        if not text_dir.is_dir():
            raise FileNotFoundError(f"no extracted-text directory at {text_dir}")
        target = ensure_outside_checkout(database or default_database(), detail=WHY_OUTSIDE)
        target.parent.mkdir(parents=True, exist_ok=True)
        locks.enter_context(artifact_lock.hold(target, "building guideline index"))
        producer = artifact_provenance.current_producer()
        producer_provenance = artifact_provenance.check_producer(
            producer,
            target,
            allow_untrusted=allow_untrusted_provenance,
            expected_commit=str(producer["commit"]),
        )
        manifest, source_provenance = _read_manifest(
            text_dir,
            allow_untrusted_provenance=allow_untrusted_provenance,
            expected_commit=str(producer["commit"]),
        )
        if source_provenance is None:
            source_provenance = artifact_provenance.check_producer(
                None,
                text_dir / MANIFEST_NAME,
                allow_untrusted=allow_untrusted_provenance,
                expected_commit=str(producer["commit"]),
            )
        partial = target.with_name(f"{target.name}.{os.getpid()}.building")
        partial.unlink(missing_ok=True)

        documents = pages = characters = 0
        seen: set[str] = set()
        connection = sqlite3.connect(partial)
        try:
            connection.executescript(SCHEMA)
            for document in _discover(text_dir, manifest):
                seen.add(document.doc_id)
                cursor = connection.execute(
                    "INSERT INTO document (doc_id, society, title, document_class, pages) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        document.doc_id,
                        document.society,
                        document.title,
                        document.document_class,
                        len(document.pages),
                    ),
                )
                doc_pk = cursor.lastrowid
                connection.executemany(
                    "INSERT INTO page (doc_pk, number, text) VALUES (?, ?, ?)",
                    [(doc_pk, page.number, page.text) for page in document.pages],
                )
                documents += 1
                pages += len(document.pages)
                characters += sum(len(page.text) for page in document.pages)

            if documents == 0:
                raise ValueError(
                    f"no .txt files under {text_dir}. An index over nothing answers every "
                    "query with zero hits, which is the one thing this must not do."
                )

            connection.execute("INSERT INTO page_fts(page_fts) VALUES ('rebuild')")
            untrusted_reasons = list(
                source_provenance.reasons + producer_provenance.reasons
            )
            provenance = {
                "producer": producer_provenance.producer,
                "source": source_provenance.producer,
                "untrusted_reasons": untrusted_reasons,
            }
            connection.executemany(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                [
                    ("schema_version", str(SCHEMA_VERSION)),
                    ("text_dir", str(text_dir)),
                    ("documents", str(documents)),
                    ("pages", str(pages)),
                    ("characters", str(characters)),
                    ("built_at", datetime.now(timezone.utc).isoformat(timespec="seconds")),
                    ("provenance", json.dumps(provenance, sort_keys=True)),
                ],
            )
            connection.commit()
        except BaseException:
            connection.close()
            partial.unlink(missing_ok=True)
            raise
        connection.close()
        os.replace(partial, target)

    manifest_only = sorted(set(manifest) - seen)
    return BuildReport(
        database=target,
        documents=documents,
        pages=pages,
        characters=characters,
        manifest_only=manifest_only,
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("text_dir", help="extracted-text directory from guidelines_extract.py")
    parser.add_argument(
        "database",
        nargs="?",
        help=f"where to write the index (default: {default_database()})",
    )
    parser.add_argument(
        "--allow-untrusted-provenance",
        action="store_true",
        help="index a dirty, foreign, or unstamped extracted corpus and warn",
    )
    args = parser.parse_args(argv)

    try:
        report = build(
            args.text_dir,
            args.database,
            allow_untrusted_provenance=args.allow_untrusted_provenance,
        )
    except (artifact_lock.ArtifactBusy, FileNotFoundError, ValueError) as failure:
        print(str(failure), file=sys.stderr)
        return 2

    print(
        f"indexed {report.documents} document(s), {report.pages} page(s), "
        f"{report.characters} character(s)"
    )
    print(f"  -> {report.database}")
    # Reported on stderr, and the exit status stays 0. A document the manifest names
    # with no text is #80's recorded extraction failure surfacing here, not a fault in
    # the index -- and a build that went red for one unextractable PDF would be red
    # every run, which is how a warning stops being read.
    for doc_id in report.manifest_only:
        print(f"  no extracted text for {doc_id} (named by {MANIFEST_NAME})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
