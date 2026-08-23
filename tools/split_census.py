"""Audit inferred guideline-text splits with the extractor's current rule.

Maintainer-only: this command reads the society PDF corpus and therefore needs
PyMuPDF. It has two modes over the same input. The default prints ``run -> pieces``
shapes and the five digit-adjacent boundary classes; ``--classify`` rebuilds a
lexicon from real PDF space glyphs and separates ``wrong``, ``fix``, ``ambiguous``
and ``undecidable`` evidence.

The historical pre-#178 shape artifact held 13,685 occurrences over 10,731 distinct
shapes, including 390 ``digit|digit`` boundaries. Those figures remain dated: this
command consumes ``guidelines_extract.walk_line_glyphs`` and therefore answers the
live question under #178's second bar and #172's operator repair. It does not carry
the retired gap rule needed to reproduce the old run.

Output is source guideline expression. It prints at most a small number of
single-line shapes and never page context: a line into a ticket, never a page.
Nothing is written, so no result or lexicon cache can outlive the rule that made it.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from collections.abc import Iterable, Iterator
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import guidelines_extract
from console_codec import use_utf8


WHY_NO_WRITE_GUARD = (
    "This maintainer audit writes nothing: the lexicon and every census result stay "
    "in memory and are printed only as a bounded summary."
)

BOUNDARY_CLASSES = (
    "alpha|digit",
    "digit|alpha",
    "punct|digit",
    "digit|punct",
    "digit|digit",
)
QUANTITY_PUNCTUATION = frozenset(".,")
ALPHA = re.compile(r"^[A-Za-z]+$")
EDGE = re.compile(r"^[^A-Za-z]+|[^A-Za-z]+$")
LEXICON_MIN = 2
LEXICON_MAX = 24
LEXICON_FLOOR = 3
DEFAULT_LIMIT = 12
HISTORICAL_SHAPE_FIGURES = {
    "occurrences": 13_685,
    "distinct_shapes": 10_731,
    "digit|digit": 390,
}


def empty_boundaries() -> collections.Counter[str]:
    return collections.Counter({name: 0 for name in BOUNDARY_CLASSES})


@dataclass
class Census:
    shapes: collections.Counter[str] = field(default_factory=collections.Counter)
    boundaries: collections.Counter[str] = field(default_factory=empty_boundaries)
    quantity_shapes: collections.Counter[str] = field(default_factory=collections.Counter)

    def update(self, other: "Census") -> None:
        self.shapes.update(other.shapes)
        self.boundaries.update(other.boundaries)
        self.quantity_shapes.update(other.quantity_shapes)


def _kind(glyph: str) -> str:
    if glyph.isalpha():
        return "alpha"
    if glyph.isdigit():
        return "digit"
    return "punct"


def _boundary(left: str, right: str) -> str | None:
    name = f"{_kind(left)}|{_kind(right)}"
    return name if name in BOUNDARY_CLASSES else None


def _quantity_shaped(left: str, right: str) -> bool:
    return (
        left.isdigit()
        and right.isdigit()
        or left in QUANTITY_PUNCTUATION
        and right.isdigit()
        or left.isdigit()
        and right in QUANTITY_PUNCTUATION
    )


def line_runs(
    line: dict,
    rendered_operators: dict[guidelines_extract.RenderedOperatorKey, str] | None = None,
) -> Iterator[tuple[str, list[str]]]:
    """Real-space-delimited runs and the pieces inferred inside each one."""
    run: list[str] = []
    pieces = [""]

    def current() -> tuple[str, list[str]] | None:
        joined = "".join(run)
        if joined.strip() and len(pieces) > 1:
            return joined, pieces.copy()
        return None

    for glyph, inserted in guidelines_extract.walk_line_glyphs(
        line, rendered_operators
    ):
        if glyph == " ":
            found = current()
            if found is not None:
                yield found
            run = []
            pieces = [""]
            continue
        if inserted and run:
            pieces.append("")
        run.append(glyph)
        pieces[-1] += glyph
    found = current()
    if found is not None:
        yield found


def census_rawdict(
    raw: dict,
    rendered_operators: dict[guidelines_extract.RenderedOperatorKey, str] | None = None,
) -> Census:
    result = Census()
    for block in raw.get("blocks", ()):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", ()):
            for run, pieces in line_runs(line, rendered_operators):
                shape = f"{run} -> {'|'.join(pieces)}"
                result.shapes[shape] += 1
                for left_piece, right_piece in zip(pieces, pieces[1:]):
                    if not left_piece or not right_piece:
                        continue
                    left, right = left_piece[-1], right_piece[0]
                    boundary = _boundary(left, right)
                    if boundary is not None:
                        result.boundaries[boundary] += 1
                    if _quantity_shaped(left, right):
                        result.quantity_shapes[shape] += 1
    return result


def _scan_document(path: str) -> Census:
    import pymupdf

    result = Census()
    document = pymupdf.open(path)
    try:
        for page in document:
            raw = page.get_text("rawdict")
            rendered = guidelines_extract.rendered_operator_map_for_page(page, raw)
            result.update(census_rawdict(raw, rendered))
    finally:
        document.close()
    return result


def _pdfs(source: Path) -> list[Path]:
    return sorted(source.rglob("*.pdf"), key=lambda path: path.relative_to(source).as_posix())


def scan_corpus(source: Path, workers: int | None = None) -> Census:
    result = Census()
    jobs = [str(path) for path in _pdfs(source)]
    if workers == 1:
        rows: Iterable[Census] = (_scan_document(path) for path in jobs)
    else:
        pool = ProcessPoolExecutor(max_workers=workers)
        rows = pool.map(_scan_document, jobs)
    try:
        for row in rows:
            result.update(row)
    finally:
        if workers != 1:
            pool.shutdown()
    return result


def _harvest_document(path: str) -> collections.Counter[str]:
    import pymupdf

    seen: collections.Counter[str] = collections.Counter()
    document = pymupdf.open(path)
    try:
        for page in document:
            raw = page.get_text("rawdict")
            for block in raw.get("blocks", ()):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", ()):
                    token: list[str] = []
                    for span in line.get("spans", ()):
                        for char in span.get("chars", ()):
                            glyph = char["c"]
                            if glyph == " ":
                                _count_token(token, seen)
                                token = []
                            else:
                                token.append(glyph)
                    _count_token(token, seen)
    finally:
        document.close()
    return seen


def _count_token(token: list[str], seen: collections.Counter[str]) -> None:
    word = EDGE.sub("", "".join(token))
    if ALPHA.fullmatch(word) and LEXICON_MIN <= len(word) <= LEXICON_MAX:
        seen[word.lower()] += 1


def harvest_lexicon(source: Path, workers: int | None = None) -> set[str]:
    total: collections.Counter[str] = collections.Counter()
    jobs = [str(path) for path in _pdfs(source)]
    if workers == 1:
        rows: Iterable[collections.Counter[str]] = (_harvest_document(path) for path in jobs)
    else:
        pool = ProcessPoolExecutor(max_workers=workers)
        rows = pool.map(_harvest_document, jobs)
    try:
        for row in rows:
            total.update(row)
    finally:
        if workers != 1:
            pool.shutdown()
    return {word for word, count in total.items() if count >= LEXICON_FLOOR}


def classify_shapes(shapes: dict[str, int], lexicon: set[str]) -> dict[str, int]:
    counts = {name: 0 for name in ("ambiguous", "fix", "wrong", "undecidable")}
    for shape, occurrences in shapes.items():
        run, divided = shape.split(" -> ", 1)
        word = EDGE.sub("", run).lower()
        pieces = [EDGE.sub("", piece).lower() for piece in divided.split("|")]
        if not ALPHA.fullmatch(word) or any(not ALPHA.fullmatch(piece) for piece in pieces):
            continue
        run_known = word in lexicon
        pieces_known = all(len(piece) >= LEXICON_MIN and piece in lexicon for piece in pieces)
        if run_known and pieces_known:
            bucket = "ambiguous"
        elif run_known:
            bucket = "wrong"
        elif pieces_known:
            bucket = "fix"
        else:
            bucket = "undecidable"
        counts[bucket] += occurrences
    return counts


def _print_shapes(measured: Census, limit: int) -> None:
    print(
        f"shapes      {len(measured.shapes):,} distinct, "
        f"{sum(measured.shapes.values()):,} occurrence(s)"
    )
    for name in BOUNDARY_CLASSES:
        print(f"{name:12} {measured.boundaries[name]:,}")
    quantity = sum(measured.quantity_shapes.values())
    print(
        f"quantity    {quantity:,} occurrence(s), "
        f"{len(measured.quantity_shapes):,} distinct shape(s)"
    )
    for shape, count in measured.quantity_shapes.most_common(limit):
        print(f"  {count:>6,}  {shape[:160]}")
    print("FINDING quantity-shaped inferred split(s) require review" if quantity else "clean")


def _print_classification(measured: Census, lexicon: set[str]) -> dict[str, int]:
    counts = classify_shapes(measured.shapes, lexicon)
    print(f"lexicon     {len(lexicon):,} token(s), rebuilt this run")
    for name in ("wrong", "fix", "ambiguous", "undecidable"):
        print(f"{name:12} {counts[name]:,}")
    return counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    parser.add_argument("source", type=Path, help="society PDF corpus root")
    parser.add_argument("--classify", action="store_true", help="classify alpha-only split shapes")
    parser.add_argument("--jobs", type=int, default=None, help="worker count (default: CPU count)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="maximum quantity shapes to print")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.source.is_dir():
        print(f"no corpus at {args.source}", file=sys.stderr)
        return 2
    if not _pdfs(args.source):
        print(f"no PDF files under {args.source}", file=sys.stderr)
        return 2
    try:
        guidelines_extract.require_pymupdf()
    except SystemExit as unavailable:
        print(str(unavailable), file=sys.stderr)
        return 2
    try:
        measured = scan_corpus(args.source, args.jobs)
        if args.classify:
            counts = _print_classification(
                measured, harvest_lexicon(args.source, args.jobs)
            )
            return 1 if counts["wrong"] or counts["undecidable"] else 0
        _print_shapes(measured, max(0, args.limit))
        return 1 if measured.quantity_shapes else 0
    except Exception as error:  # noqa: BLE001 - every incomplete audit is status 2
        print(f"not scanned: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
