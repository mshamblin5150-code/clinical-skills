#!/usr/bin/env python3
"""Render one discussion-post DOCX into a new retained page-image pass.

The command asks a freshly spawned Microsoft Word instance for a PDF, falling
back to XPS, then rasterizes every page with PyMuPDF. It never edits
``post.md``: the independent visual reader appends the ``RENDERED`` record only
after comparing these pixels with the Markdown.

Exit 0 means a complete new pass was retained. Exit 2 means rendering did not
complete; a partial pass is removed and never presented as evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from console_codec import use_utf8
from discussion_artifact import (
    AUTOMATED_RENDERED_SOURCES,
    RENDERED_RASTER_DPI as RASTER_DPI,
    png_read_error,
)


EXPORT_TIMEOUT_SECONDS = 20


class RenderError(Exception):
    pass


def _next_pass(render_root: Path) -> int:
    numbers = sorted(
        int(match.group(1))
        for child in render_root.iterdir()
        if child.is_dir() and (match := re.fullmatch(r"pass-(\d+)", child.name))
    )
    if numbers != list(range(1, len(numbers) + 1)):
        raise RenderError("render pass directories are not consecutive from pass-1")
    return len(numbers) + 1


def _stop_owned_word(ownership_file: Path) -> None:
    try:
        process_id = ownership_file.read_text(encoding="ascii").split("|", 1)[0].strip()
    except OSError:
        return
    if not process_id.isdigit():
        return
    subprocess.run(
        ["taskkill.exe", "/PID", process_id, "/T", "/F"],
        check=False,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def _owned_word_stage(ownership_file: Path) -> str:
    try:
        parts = ownership_file.read_text(encoding="ascii").strip().split("|", 1)
    except OSError:
        return "before process ownership was recorded"
    return parts[1] if len(parts) == 2 and parts[1] else "after process creation"


def _word_attempt(
    docx: Path, output_directory: Path, mode: str
) -> tuple[str, Path]:
    script = Path(__file__).with_suffix(".ps1")
    ownership_file = output_directory / f"{mode}-word-pid.txt"
    try:
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Document",
                str(docx),
                "-OutputDirectory",
                str(output_directory),
                "-Mode",
                mode,
                "-OwnershipFile",
                str(ownership_file),
            ],
            check=False,
            capture_output=True,
            encoding="utf-8-sig",
            errors="replace",
            timeout=EXPORT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as failure:
        stage = _owned_word_stage(ownership_file)
        _stop_owned_word(ownership_file)
        raise RenderError(f"Word {mode} export timed out at stage {stage}") from failure
    if completed.returncode:
        _stop_owned_word(ownership_file)
        raise RenderError(completed.stderr.strip() or f"Word {mode} export failed")
    try:
        report = json.loads(completed.stdout)
        source = report["source"]
        output = Path(report["path"])
    except (json.JSONDecodeError, KeyError, TypeError) as failure:
        raise RenderError(f"Word export returned an invalid report: {failure}") from failure
    if source not in AUTOMATED_RENDERED_SOURCES:
        raise RenderError(f"Word export returned an unrecognized source: {source!r}")
    if not output.is_file():
        raise RenderError(f"Word export did not create {output}")
    return source, output


def _clinician_pages(values: list[str]) -> dict[int, Path]:
    pages: dict[int, Path] = {}
    for value in values:
        number_text, separator, path_text = value.partition("=")
        if not separator or not number_text.isdigit() or int(number_text) < 1:
            raise RenderError("--clinician-page must be PAGE=PNG with a positive page number")
        number = int(number_text)
        image = Path(path_text)
        if number in pages:
            raise RenderError(f"clinician page {number} was given twice")
        if image.suffix.lower() != ".png" or not image.is_file():
            raise RenderError(f"clinician page {number} is not an existing PNG: {image}")
        pages[number] = image
    return pages


def _validate_clinician_pages(pymupdf, pages: dict[int, Path]) -> None:
    for number, image in pages.items():
        if failure := png_read_error(pymupdf, image):
            raise RenderError(f"clinician page {number} is not a readable PNG: {failure}")


def _automated_pages(
    pymupdf,
    docx: Path,
    conversion_directory: Path,
    staging: Path,
    expected_pages: int | None,
) -> tuple[str | None, int | None, tuple[str, ...]]:
    source: str | None = None
    pages: int | None = None
    failures: list[str] = []
    for mode in ("pdf", "xps"):
        try:
            route_source, converted = _word_attempt(docx, conversion_directory, mode)
            with pymupdf.open(str(converted)) as document:
                route_pages = len(document)
                if route_pages < 1:
                    raise RenderError(f"Word {mode} export contains no pages")
                if pages is not None and route_pages != pages:
                    raise RenderError(
                        f"Word {mode} reports {route_pages} pages after the earlier route reported {pages}"
                    )
                pages = route_pages
                if expected_pages is not None and route_pages != expected_pages:
                    raise RenderError(
                        f"Word reports {route_pages} pages, not --expected-pages {expected_pages}"
                    )
                missed: list[int] = []
                for number, page in enumerate(document, start=1):
                    target = staging / f"page-{number}.png"
                    if target.is_file():
                        continue
                    partial = staging / f".page-{number}.{mode}.building.png"
                    try:
                        page.get_pixmap(dpi=RASTER_DPI).save(partial)
                        partial.replace(target)
                    except Exception:
                        partial.unlink(missing_ok=True)
                        missed.append(number)
                source = route_source
                if not missed:
                    return source, pages, tuple(failures)
                failures.append(
                    f"Word {mode} could not rasterize page(s) "
                    + ", ".join(str(number) for number in missed)
                )
        except RenderError as failure:
            failures.append(str(failure))
        except Exception as failure:
            failures.append(f"could not read the Word {mode} export: {failure}")
    return source, pages, tuple(failures)


def render(
    run: Path,
    docx: Path,
    clinician_pages: dict[int, Path] | None = None,
    expected_pages: int | None = None,
) -> tuple[str, Path, int]:
    if not run.is_dir():
        raise RenderError(f"no run directory at {run}")
    if not docx.is_file():
        raise RenderError(f"no rendered document at {docx}")
    try:
        import pymupdf
    except ImportError as failure:
        raise RenderError("pymupdf is not installed") from failure

    clinician_pages = clinician_pages or {}
    if expected_pages is not None and expected_pages < 1:
        raise RenderError("--expected-pages must be a positive integer")
    if clinician_pages and expected_pages is None:
        raise RenderError("--clinician-page requires --expected-pages")
    _validate_clinician_pages(pymupdf, clinician_pages)

    render_root = run / "render"
    render_root.mkdir(exist_ok=True)
    pass_number = _next_pass(render_root)
    destination = render_root / f"pass-{pass_number}"
    staging = Path(tempfile.mkdtemp(prefix=f".pass-{pass_number}-", dir=render_root))
    try:
        with tempfile.TemporaryDirectory() as conversion_directory:
            source, pages, failures = _automated_pages(
                pymupdf,
                docx.resolve(),
                Path(conversion_directory),
                staging,
                expected_pages,
            )
            if pages is None:
                pages = expected_pages
            if pages is None:
                raise RenderError("; ".join(failures))
            missing = {
                number
                for number in range(1, pages + 1)
                if not (staging / f"page-{number}.png").is_file()
            }
            unused = set(clinician_pages) - missing
            if unused:
                listed = ", ".join(str(number) for number in sorted(unused))
                raise RenderError(
                    f"clinician page(s) {listed} were not needed by the automated routes"
                )
            unavailable = missing - set(clinician_pages)
            if unavailable:
                detail = "; ".join(failures)
                listed = ", ".join(str(number) for number in sorted(unavailable))
                raise RenderError(f"{detail}; page(s) {listed} need clinician images")
            for number in missing:
                shutil.copy2(
                    clinician_pages[number], staging / f"page-{number}.png"
                )
            if missing:
                source = "clinician"
            if source is None:
                raise RenderError("; ".join(failures))
        retained = tuple(staging.glob("*.png"))
        if len(retained) != pages:
            raise RenderError(
                f"rasterizer retained {len(retained)} page image(s) for {pages} pages"
            )
        staging.rename(destination)
        return source, destination, pages
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        usage="discussion_post_render.py <run directory> --docx <Word file>"
    )
    parser.add_argument("run")
    parser.add_argument("--docx", required=True)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--clinician-page", action="append", default=[])
    try:
        args = parser.parse_args(argv)
        source, destination, pages = render(
            Path(args.run),
            Path(args.docx),
            _clinician_pages(args.clinician_page),
            args.expected_pages,
        )
    except (RenderError, OSError) as failure:
        print(f"render did not complete: {failure}", file=sys.stderr)
        return 2
    print(f"SOURCE: {source}")
    print(f"PAGES: {pages} of {pages} imaged")
    print(f"PIXELS: {destination}")
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
