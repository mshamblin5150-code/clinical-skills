"""Read PDF page text while keeping engine objects behind a narrow adapter."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pdf_engine


OPERATOR_RENDER_SCALE = 12.0


class PageRead:
    """The four text-side questions callers may ask of one open page."""

    def __init__(self, engine, page, number: int, owner=None) -> None:
        self._engine = engine
        self._page = page
        self._owner = owner
        self.number = number

    @property
    def rawdict(self) -> dict:
        return self._page.get_text("rawdict")

    def render_glyph(self, bbox) -> tuple[bytes, int, int]:
        pixmap = self._page.get_pixmap(
            matrix=self._engine.Matrix(OPERATOR_RENDER_SCALE, OPERATOR_RENDER_SCALE),
            clip=self._engine.Rect(bbox),
            colorspace=self._engine.csGRAY,
            alpha=False,
        )
        return bytes(pixmap.samples), pixmap.width, pixmap.height

    def plain_text(self) -> str:
        return self._page.get_text("text")

    def tables(self) -> tuple[list[list[str | None]], ...]:
        """Return extracted cell payloads without leaking engine table objects."""
        return tuple(table.extract() for table in self._page.find_tables().tables)

    def __del__(self) -> None:
        owner = getattr(self, "_owner", None)
        if owner is not None:
            try:
                owner.close()
            except Exception:
                pass
            self._owner = None


class DocumentRead:
    """An open document whose engine representation never crosses the seam."""

    def __init__(self, engine, document) -> None:
        self._engine = engine
        self._document = document

    @property
    def title(self) -> str | None:
        try:
            return ((self._document.metadata or {}).get("title") or "").strip() or None
        except Exception:
            return None

    @property
    def page_count(self) -> int:
        return len(self._document)

    def pages(self) -> Iterator[PageRead]:
        for number, page in enumerate(self._document, start=1):
            yield PageRead(self._engine, page, number)

    def page(self, number: int) -> PageRead:
        return PageRead(self._engine, self._document[number - 1], number)


def _open(path: Path):
    engine = pdf_engine.acquire()
    try:
        document = engine.open(str(path))
    except Exception as failure:
        raise pdf_engine.SourceUnreadable(str(failure)) from failure
    return engine, document


@contextmanager
def open_document(path: Path) -> Iterator[DocumentRead]:
    """Open ``path`` for several page questions and always close it."""
    engine, document = _open(path)
    try:
        yield DocumentRead(engine, document)
    finally:
        document.close()


def read_page(path: Path, number: int) -> PageRead:
    """Open one numbered page; its wrapper owns the document lifetime."""
    engine, document = _open(path)
    try:
        page = document[number - 1]
    except Exception:
        document.close()
        raise
    return PageRead(engine, page, number, owner=document)
