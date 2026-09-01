"""Count reference-class coverage across the account-owned coursework corpus.

    python tools/reference_class_census.py

The population follows the two ownership rules that create it: every registered
checkout's ``scratch/`` root and the owning checkout's single ``output/`` root.
Using ``repo_root.scratch_root()`` would silently reduce that population to one
checkout. A separate clone has its own worktree registry and is invisible, and
material outside every checkout is outside this walk.

Only Markdown and text files can carry the Markdown reference heading consumed by
``reference_scan.read_document``. The report emits bucket names, coverage states,
and integers only; it has no ``--show`` aperture and never emits an entry, filename,
or path. Exit status is 0 with no populated finding-state bucket, 1 with one, and 2
whenever the complete registered population was not scanned.
"""

from __future__ import annotations

import sys
import re
from dataclasses import dataclass
from pathlib import Path

from console_codec import use_utf8
import reference_scan
import repo_root
import scratch_census

USAGE = "usage: reference_class_census.py"
TEXT_SUFFIXES = frozenset({".md", ".txt"})
REFERENCE_CANDIDATE = re.compile(
    r"(?im)^#{1,6}\s+(?:reference|references\b.*|works (?:cited|consulted)|bibliography|"
    r"reference list|references cited|literature cited|sources|citations)\s*#*\s*$"
)


@dataclass(frozen=True)
class FileRead:
    """Independent candidate decision and the extractor result for one file."""

    candidate: bool
    document: reference_scan.Document | None
    unreadable: bool


@dataclass(frozen=True)
class RootRead:
    """Population denominator and extractor result beneath one corpus root."""

    text_files: int
    candidate_documents: int
    documents: tuple[reference_scan.Document, ...]
    unreadable_documents: int


@dataclass(frozen=True)
class Census:
    checkouts: int
    roots_read: int
    roots_unreadable: int
    text_files: int
    candidate_documents: int
    documents: int
    documents_unreadable: int
    entries: int
    bucket_counts: tuple[reference_scan.BucketCount, ...]
    undecidable_remainder: int

    @property
    def uncovered(self) -> int:
        return sum(
            item.population
            for item in self.bucket_counts
            if item.state == reference_scan.COVERAGE_FINDING
        )


def read_text_file(path: Path) -> FileRead:
    """Detect a likely reference list independently, then run the extractor."""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return FileRead(candidate=False, document=None, unreadable=True)
    candidate = REFERENCE_CANDIDATE.search(text) is not None
    if not candidate:
        return FileRead(candidate=False, document=None, unreadable=False)
    parsed = reference_scan.read_document(text)
    if parsed.heading is None or not parsed.entries:
        return FileRead(candidate=True, document=None, unreadable=True)
    return FileRead(candidate=True, document=parsed, unreadable=False)


def read_root(root: Path) -> RootRead | None:
    """Read the independent candidate population beneath one corpus root."""

    if not root.exists():
        return None
    documents: list[reference_scan.Document] = []
    text_files = 0
    candidates = 0
    unreadable = 0
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text_files += 1
        found = read_text_file(path)
        candidates += int(found.candidate)
        unreadable += int(found.unreadable)
        if found.document is not None:
            documents.append(found.document)
    return RootRead(text_files, candidates, tuple(documents), unreadable)


def scan_corpus(checkout: Path) -> Census:
    """Scan all ruled roots while keeping paths and document text out of the result."""

    worktrees = scratch_census.worktree_roots(checkout)
    roots = tuple(root / "scratch" for root in worktrees) + (repo_root.output_root(),)
    documents: list[reference_scan.Document] = []
    roots_read = 0
    roots_unreadable = 0
    text_files = 0
    candidate_documents = 0
    documents_unreadable = 0
    for root in roots:
        try:
            found = read_root(root)
        except OSError:
            roots_unreadable += 1
            continue
        if found is None:
            continue
        roots_read += 1
        text_files += found.text_files
        candidate_documents += found.candidate_documents
        documents_unreadable += found.unreadable_documents
        documents.extend(found.documents)

    classified = tuple(
        reference_scan.classify_entry(entry)
        for document in documents
        for entry in document.entries
    )
    bucket_counts = reference_scan.summarize_buckets(classified)
    return Census(
        checkouts=len(worktrees),
        roots_read=roots_read,
        roots_unreadable=roots_unreadable,
        text_files=text_files,
        candidate_documents=candidate_documents,
        documents=len(documents),
        documents_unreadable=documents_unreadable,
        entries=len(classified),
        bucket_counts=bucket_counts,
        undecidable_remainder=sum(
            item.population
            for item in bucket_counts
            if item.state == reference_scan.COVERAGE_UNDECIDABLE
        ),
    )


def format_report(census: Census) -> str:
    lines = [
        f"checkouts enumerated              {census.checkouts}",
        f"roots read                        {census.roots_read}",
        f"roots unreadable                  {census.roots_unreadable}",
        f"text files considered             {census.text_files}",
        f"reference-list candidates         {census.candidate_documents}",
        f"candidate documents read          {census.documents}",
        f"candidate documents unreadable    {census.documents_unreadable}",
        f"reference entries read            {census.entries}",
        "",
        "source-class coverage",
    ]
    for item in census.bucket_counts:
        lines.append(f"  {item.name:<22} {item.state:<11} {item.population}")
    lines += [
        "",
        f"uncovered-class                   {census.uncovered}",
        f"undecidable remainder             {census.undecidable_remainder}",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if argv:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        result = scan_corpus(Path.cwd().resolve())
    except scratch_census.CensusNotRun as error:
        print("checkouts enumerated              0")
        print("roots read                        0")
        print("roots unreadable                  0")
        print(f"NOT SCANNED: {error}", file=sys.stderr)
        return 2
    print(format_report(result))
    if result.roots_unreadable or result.documents_unreadable:
        print(
            "NOT SCANNED: "
            f"{result.roots_unreadable} corpus root(s) and "
            f"{result.documents_unreadable} candidate document(s) unreadable",
            file=sys.stderr,
        )
        return 2
    return 1 if result.uncovered else 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
