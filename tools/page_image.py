"""Rasterize PDF exports and validate the retained page images they produced."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

import pdf_engine


EngineUnavailable = pdf_engine.EngineUnavailable
SourceUnreadable = pdf_engine.SourceUnreadable


RASTER_DPI = 120
DECODE_PROBE_DPI = 1
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EMPTY_EXPORT = "export contains no pages"


@contextmanager
def _opened(export: Path) -> Iterator[object]:
    """Hold one engine document and type every failure across its lifetime."""
    engine = pdf_engine.acquire()
    try:
        with engine.open(str(export)) as document:
            yield document
    except pdf_engine.SourceUnreadable:
        raise
    except Exception as failure:
        raise pdf_engine.SourceUnreadable(str(failure)) from failure


def rasterize(
    export: Path,
    destination: Path,
    *,
    name: str,
    dpi: int = RASTER_DPI,
    page_numbers: Iterable[int] | None = None,
) -> int:
    """Write one staged PNG per page, collecting every failed page number."""
    with _opened(export) as document:
        pages = len(document)
        if pages < 1:
            raise pdf_engine.SourceUnreadable(EMPTY_EXPORT)
        selected = None if page_numbers is None else set(page_numbers)
        found: set[int] = set()
        missed: list[tuple[int, str]] = []
        for number, page in enumerate(document, start=1):
            if selected is not None and number not in selected:
                continue
            found.add(number)
            target = destination / f"{name}-{number}.png"
            partial = destination / f".{name}-{number}.building.png"
            try:
                page.get_pixmap(dpi=dpi).save(partial)
                partial.replace(target)
            except Exception as failure:
                partial.unlink(missing_ok=True)
                missed.append((number, str(failure)))
        if selected is not None:
            missed.extend(
                (number, "page does not exist") for number in sorted(selected - found)
            )
    if missed:
        raise pdf_engine.SourceUnreadable(
            "could not rasterize page(s) "
            + ", ".join(
                f"{number} ({detail})" if detail else str(number)
                for number, detail in missed
            )
        )
    return pages if selected is None else len(selected)


def export_page_count(export: Path) -> int:
    """Return the page count of one readable export."""
    with _opened(export) as document:
        pages = len(document)
    if pages < 1:
        raise pdf_engine.SourceUnreadable(EMPTY_EXPORT)
    return pages


def page_read_error(path: Path) -> str | None:
    """Return why a retained page is not one readable PNG, or ``None``."""
    if not path.is_file():
        return "is not a regular file"
    try:
        with path.open("rb") as stream:
            signature = stream.read(len(PNG_SIGNATURE))
    except OSError as failure:
        return f"is not decodable as PNG: {failure}"
    if signature != PNG_SIGNATURE:
        return "does not carry a PNG signature"
    engine = pdf_engine.acquire()
    try:
        with engine.open(str(path)) as document:
            if len(document) != 1:
                return "does not contain exactly one image page"
            next(iter(document)).get_pixmap(dpi=DECODE_PROBE_DPI)
    except Exception as failure:
        return f"is not decodable as PNG: {failure}"
    return None
