"""Assemble one day file into the account-owned text corpus.

The PDF engine stays behind ``page_text`` and ``page_image``. Output is limited
to counts and paths because both the source and the assembled text contain PHI.
The complete coverage boundary is ``DECLARED_LIMITS``.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
from datetime import date
from pathlib import Path

from console_codec import use_utf8
import page_image
import page_text
import pdf_engine
import repo_root


DAY_FILE_DPI = 140

DECLARED_LIMITS = {
    "scanner-stamp": (
        "A page carrying any non-whitespace text counts as a text page even when its body is an image."
    ),
    "reading-faithfulness": (
        "A transcription file's presence does not establish that it matches the rendered page."
    ),
    "render-resolution": "The command does not establish that 140 DPI is the right reading resolution.",
    "date-correctness": "The source digest does not establish that --date is the document's visit date.",
    "concurrent-runs": "Atomic replacement does not serialize two commands for the same shift.",
}


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Write a day file's complete page text into the PHI corpus."
    )
    command.add_argument("day_file", type=Path)
    command.add_argument("--date", required=True, type=date.fromisoformat)
    command.add_argument("--force", action="store_true")
    return command


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write(path: Path, payload: bytes) -> None:
    """Replace ``path`` from a same-directory temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _page_join(parts: list[str]) -> str:
    """Preserve page payloads while keeping adjacent pages on separate lines."""
    return "".join(part if part.endswith(("\n", "\r")) else f"{part}\n" for part in parts)


def _report(*, text_pages: int, rendered_pages: int, target: Path) -> None:
    print(f"Pages read as text: {text_pages}")
    print(f"Pages rendered: {rendered_pages}")
    print(f"Text file: {target}")


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    source = arguments.day_file.expanduser().resolve()
    scratch = repo_root.scratch_root()
    day_directory = scratch / "runs" / f"shift-{arguments.date.isoformat()}" / "day-file"
    hash_path = day_directory / "source.sha256"
    target = scratch / "day-file-text" / f"{source.stem}.txt"

    try:
        source_hash = _digest(source)
    except OSError:
        print(f"Could not read source document: {source}", file=sys.stderr)
        return 2

    if hash_path.exists():
        try:
            recorded_hash = hash_path.read_text(encoding="ascii").strip()
        except OSError:
            print(f"Could not read source record: {hash_path}", file=sys.stderr)
            return 2
        if recorded_hash != source_hash:
            print(
                f"Refusing a different source for this shift: {hash_path}",
                file=sys.stderr,
            )
            return 2

    try:
        with page_text.open_document(source) as document:
            pages = tuple(document.pages())
            page_texts = [page.plain_text() for page in pages]
    except pdf_engine.EngineUnavailable:
        print(f"PDF engine unavailable; no text written for: {source}", file=sys.stderr)
        return 2
    except (pdf_engine.SourceUnreadable, OSError):
        print(f"Could not open day file: {source}", file=sys.stderr)
        return 2
    except Exception:
        print(f"Could not read day file: {source}", file=sys.stderr)
        return 2

    if not page_texts:
        print(f"Day file contains no pages: {source}", file=sys.stderr)
        return 2

    textless = tuple(
        number
        for number, text in enumerate(page_texts, start=1)
        if not text.strip()
    )
    text_pages = len(page_texts) - len(textless)

    try:
        if not hash_path.exists():
            _atomic_write(hash_path, f"{source_hash}\n".encode("ascii"))
        if textless:
            page_image.rasterize(
                source,
                day_directory,
                name="page",
                dpi=DAY_FILE_DPI,
                page_numbers=textless,
            )
    except (pdf_engine.EngineUnavailable, pdf_engine.SourceUnreadable, OSError):
        print(f"Could not render day file: {source}", file=sys.stderr)
        return 2

    transcriptions = {
        number: day_directory / f"page-{number}.txt" for number in textless
    }
    missing = [number for number, path in transcriptions.items() if not path.is_file()]
    if missing:
        _report(text_pages=text_pages, rendered_pages=len(textless), target=target)
        print(f"Pages awaiting reading: {len(missing)}")
        for number in missing:
            print(f"Awaiting: {day_directory / f'page-{number}.png'}")
        return 1

    assembled = list(page_texts)
    try:
        for number, transcription in transcriptions.items():
            assembled[number - 1] = transcription.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        print(f"Could not read transcription: {transcription}", file=sys.stderr)
        return 2
    payload = _page_join(assembled).encode("utf-8")

    if target.exists():
        try:
            existing = target.read_bytes()
        except OSError:
            print(f"Could not read existing text file: {target}", file=sys.stderr)
            return 2
        if existing == payload:
            _report(text_pages=text_pages, rendered_pages=len(textless), target=target)
            print(f"Already byte-identical: {target}")
            return 0
        if not arguments.force:
            print(f"Refusing to replace different text: {target}", file=sys.stderr)
            return 2

    try:
        _atomic_write(target, payload)
    except OSError:
        print(f"Could not write text file: {target}", file=sys.stderr)
        return 2
    _report(text_pages=text_pages, rendered_pages=len(textless), target=target)
    print(f"Written: {target}")
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
