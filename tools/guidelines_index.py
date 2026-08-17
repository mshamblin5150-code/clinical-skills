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
``reference/`` and ``scratch/`` are both materialized into every worktree and there
are six live, so a 65 MB index committed or dropped in either is duplicated into all
of them. ``ensure_outside_repo`` refuses any target inside the main checkout or
inside this worktree, which is what keeps `git status` clean after a build. Whether
the index should ever *ship* is #87, and it is blocked; nothing here presumes an
answer.

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

An optional ``manifest.json`` supplies ``title``, ``society`` and ``document_class``
per document -- the last of these is how the three ACIP browser captures stay
distinguishable from guidelines. No manifest means derived values. A manifest that is
present but unreadable, or present and keyed by something other than ``doc_id``,
**raises** rather than degrading to derived values: a title silently missing from
every hit looks exactly like a corpus that never had one. A manifest entry with no
extracted text is likewise **reported**, never swallowed, because #80's contract is a
recorded failure rather than a silent skip.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

from console_codec import use_utf8
from repo_root import main_repo_root

SCHEMA_VERSION = 1
MANIFEST_NAME = "manifest.json"
UNCLASSIFIED = "unclassified"
DATABASE_ENVIRONMENT_VARIABLE = "CLINICAL_GUIDELINES_INDEX"

# A page break inside a single-file document. pdftotext writes form feed and so does
# every other extractor that keeps page boundaries at all.
PAGE_BREAK = "\f"

# The one key a manifest entry names its document with. Single on purpose: #80 owns
# the manifest's shape, and an alias list would absorb a mismatch instead of raising
# on it, leaving every title and document class quietly blank.
DOC_ID_KEY = "doc_id"


class InsideRepo(ValueError):
    """The index was aimed at a path inside the repo. See #87 and the module docstring."""


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
class BuildReport:
    database: Path
    documents: int
    pages: int
    characters: int
    manifest_only: list[str]  # named by the manifest, no extracted text found


def default_repo_roots() -> list[Path]:
    """Both roots that must stay clean: this worktree, and the checkout it came from."""
    worktree = Path(__file__).resolve().parent.parent
    return [worktree, main_repo_root()]


def default_database() -> Path:
    """Beside the sources, outside every checkout. Overridable per machine."""
    override = os.environ.get(DATABASE_ENVIRONMENT_VARIABLE)
    if override:
        return Path(override).expanduser()
    return main_repo_root().parent / "guidelines-index" / "guidelines.sqlite"


def ensure_outside_repo(path: Path | str, repo_roots: Iterable[Path] | None = None) -> Path:
    """Raise ``InsideRepo`` if ``path`` is the repo or sits under it.

    Compared as path ancestry rather than string prefix, so ``clinical_skills-notes``
    is correctly outside ``clinical_skills``.
    """
    target = Path(path).expanduser().resolve()
    for root in repo_roots if repo_roots is not None else default_repo_roots():
        root = Path(root).resolve()
        if target == root or root in target.parents:
            raise InsideRepo(
                f"{target} is inside the repo at {root}. The index is a build artifact "
                "and stays outside every checkout -- see issue #87. Pass a path beside "
                f"the guideline sources, or set {DATABASE_ENVIRONMENT_VARIABLE}."
            )
    return target


def _normalize_doc_id(value: str) -> str:
    cleaned = value.strip().replace("\\", "/").strip("/")
    return cleaned[:-4] if cleaned.lower().endswith(".txt") else cleaned


def read_manifest(text_dir: Path | str) -> dict[str, dict]:
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
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as bad:
        raise ValueError(f"{path} is present but could not be read as JSON: {bad}") from bad

    if isinstance(data, dict):
        data = data.get("documents")
    if not isinstance(data, list):
        raise ValueError(
            f"{path} is not a list of entries or a {{\"documents\": [...]}} object. "
            "#80 owns this file's shape; if it changed, change this reader rather "
            "than letting it read as empty."
        )
    entries = {
        _normalize_doc_id(str(entry[DOC_ID_KEY])): entry
        for entry in data
        if isinstance(entry, dict) and entry.get(DOC_ID_KEY)
    }
    if not entries:
        raise ValueError(
            f"no entry in {path} carries a {DOC_ID_KEY!r}, so nothing in it can be "
            "matched to a document."
        )
    return entries


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


def discover(text_dir: Path | str) -> Iterator[Document]:
    """Yield one ``Document`` per source document, in document-id order.

    A generator rather than a list: 6,800 pages of extracted text is tens of
    megabytes, and only one document needs to be in memory at a time.
    """
    text_dir = Path(text_dir)
    if not text_dir.is_dir():
        raise FileNotFoundError(f"no extracted-text directory at {text_dir}")
    manifest = read_manifest(text_dir)
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
    repo_roots: Iterable[Path] | None = None,
) -> BuildReport:
    """Index every document under ``text_dir``, replacing any existing index.

    Built into a sibling temp file and moved into place, so a build that dies part
    way leaves the previous index intact rather than a half-written one that opens
    fine and answers short.
    """
    text_dir = Path(text_dir).resolve()
    target = ensure_outside_repo(database or default_database(), repo_roots)
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".building")
    partial.unlink(missing_ok=True)

    documents = pages = characters = 0
    seen: set[str] = set()
    connection = sqlite3.connect(partial)
    try:
        connection.executescript(SCHEMA)
        for document in discover(text_dir):
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
        connection.executemany(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            [
                ("schema_version", str(SCHEMA_VERSION)),
                ("text_dir", str(text_dir)),
                ("documents", str(documents)),
                ("pages", str(pages)),
                ("characters", str(characters)),
                ("built_at", datetime.now(timezone.utc).isoformat(timespec="seconds")),
            ],
        )
        connection.commit()
    except BaseException:
        connection.close()
        partial.unlink(missing_ok=True)
        raise
    connection.close()
    os.replace(partial, target)

    manifest_only = sorted(set(read_manifest(text_dir)) - seen)
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
    args = parser.parse_args(argv)

    try:
        report = build(args.text_dir, args.database)
    except (FileNotFoundError, ValueError) as failure:
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
