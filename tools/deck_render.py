#!/usr/bin/env python3
"""Retain a page-faithful PowerPoint export and one PNG per slide."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from console_codec import use_utf8
import office_process
import render_pass


RASTER_DPI = 120
EXPORT_TIMEOUT_SECONDS = 30
SLIDE_PART = re.compile(r"^ppt/slides/slide[1-9]\d*\.xml$")


class RenderError(Exception):
    pass


def _powerpoint_export(deck: Path, output: Path, ownership_file: Path) -> None:
    script = Path(__file__).with_suffix(".ps1")
    command = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-Pptx",
        str(deck),
        "-OutputPdf",
        str(output),
        "-OwnershipFile",
        str(ownership_file),
    ]
    try:
        result = office_process.run_owned_process(
            command,
            ownership_file,
            timeout_seconds=EXPORT_TIMEOUT_SECONDS,
            application="PowerPoint",
            action="PDF export",
            runner=subprocess.run,
        )
    except office_process.OwnedProcessError as failure:
        raise RenderError(str(failure)) from failure
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as failure:
        raise RenderError("PowerPoint export returned no readable result") from failure
    if response.get("source") != "powerpoint-pdf" or Path(response.get("path", "")) != output:
        raise RenderError("PowerPoint export returned an unexpected artifact")
    if not output.is_file():
        raise RenderError("PowerPoint reported success without a PDF")


def _rasterize(export: Path, destination: Path) -> int:
    try:
        import pymupdf
    except ImportError as failure:
        raise RenderError("PyMuPDF is unavailable") from failure
    try:
        with pymupdf.open(str(export)) as document:
            pages = len(document)
            if pages < 1:
                raise RenderError("the retained PDF contains no slides")
            for number, page in enumerate(document, 1):
                page.get_pixmap(dpi=RASTER_DPI).save(destination / f"slide-{number}.png")
    except RenderError:
        raise
    except Exception as failure:
        raise RenderError(f"could not rasterize every slide: {failure}") from failure
    return pages


def _slide_count(deck: Path) -> int:
    try:
        with zipfile.ZipFile(deck) as archive:
            count = sum(bool(SLIDE_PART.fullmatch(name)) for name in archive.namelist())
    except (OSError, zipfile.BadZipFile) as failure:
        raise RenderError(f"could not read PowerPoint slide count: {failure}") from failure
    if count < 1:
        raise RenderError("the PowerPoint contains no slides")
    return count


def render(
    run: Path,
    deck: Path,
    clinician_export: Path | None = None,
) -> tuple[str, Path, int]:
    if not run.is_dir():
        raise RenderError(f"no run directory at {run}")
    if not deck.is_file() or deck.suffix.casefold() != ".pptx":
        raise RenderError(f"no PowerPoint file at {deck}")
    if clinician_export is not None and (
        not clinician_export.is_file() or clinician_export.suffix.casefold() != ".pdf"
    ):
        raise RenderError("clinician export must be an existing PDF")
    slide_count = _slide_count(deck)
    render_root = run / "render"
    def build(building: Path) -> tuple[str, int]:
        ownership = building / "powerpoint-owned.txt"
        export = building / "deck.pdf"
        source = "powerpoint-pdf"
        try:
            _powerpoint_export(deck.resolve(), export.resolve(), ownership.resolve())
        except RenderError:
            if clinician_export is None:
                raise
            shutil.copyfile(clinician_export, export)
            source = "clinician"
        pages = _rasterize(export, building)
        if pages != slide_count:
            raise RenderError(
                f"retained PDF has {pages} pages for {slide_count} slides"
            )
        ownership.unlink(missing_ok=True)
        if not render_pass.images_cover_exported_pages(
            len(tuple(building.glob("*.png"))), pages
        ):
            raise RenderError("not every exported slide has a retained page image")
        return source, pages

    destination, (source, pages) = render_pass.retain_staged_pass(render_root, build)
    return source, destination, pages


def main(argv: list[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        usage="deck_render.py <run directory> --pptx <PowerPoint file> [--clinician-export <PDF>]"
    )
    parser.add_argument("run")
    parser.add_argument("--pptx", required=True)
    parser.add_argument("--clinician-export")
    try:
        args = parser.parse_args(argv)
        source, destination, pages = render(
            Path(args.run),
            Path(args.pptx),
            Path(args.clinician_export) if args.clinician_export else None,
        )
    except (RenderError, OSError) as failure:
        print(f"render did not complete: {failure}", file=sys.stderr)
        return 2
    print(f"SOURCE: {source}")
    print(f"SLIDES: {pages} of {pages} imaged")
    print(f"PIXELS: {destination}")
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
