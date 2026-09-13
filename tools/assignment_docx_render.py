#!/usr/bin/env python3
"""Retain a Microsoft Word export and page images for an assignment DOCX."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from console_codec import require_python_floor, use_utf8
import assignment_docx
import file_digest
import office_process
import page_image
import pdf_engine
import render_pass


RASTER_DPI = page_image.RASTER_DPI
EXPORT_TIMEOUT_SECONDS = 20
FINGERPRINT_FILE = assignment_docx.FINGERPRINT_FILE


class RenderError(Exception):
    pass


class ExportBoundReached(RenderError):
    pass


def _word_attempt(docx: Path, output_directory: Path, mode: str) -> tuple[str, Path]:
    script = Path(__file__).with_name("word_export.ps1")
    ownership = output_directory / f"{mode}-word-pid.txt"
    command = [
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
        "-Stem",
        "assignment-docx",
        "-OwnershipFile",
        str(ownership),
    ]
    try:
        completed = office_process.run_owned_process(
            command,
            ownership,
            timeout_seconds=EXPORT_TIMEOUT_SECONDS,
            application="Word",
            action=f"{mode} export",
            runner=subprocess.run,
            encoding="utf-8-sig",
        )
    except office_process.OwnedProcessError as failure:
        if isinstance(failure.__cause__, subprocess.TimeoutExpired):
            raise ExportBoundReached(str(failure)) from failure
        raise RenderError(str(failure)) from failure
    try:
        report = json.loads(completed.stdout)
        source = report["source"]
        output = Path(report["path"])
    except (json.JSONDecodeError, KeyError, TypeError) as failure:
        raise RenderError(f"Word export returned an invalid report: {failure}") from failure
    if source != f"word-{mode}" or not output.is_file():
        raise RenderError("Word export returned an unexpected artifact")
    return source, output


def _automated_export(docx: Path, conversion_directory: Path) -> tuple[str, Path]:
    try:
        return _word_attempt(docx, conversion_directory, "pdf")
    except ExportBoundReached:
        raise
    except RenderError as pdf_failure:
        try:
            return _word_attempt(docx, conversion_directory, "xps")
        except RenderError as xps_failure:
            raise RenderError(f"{pdf_failure}; {xps_failure}") from xps_failure


def _rasterize(exported: Path, staging: Path) -> int:
    try:
        return page_image.rasterize(exported, staging, name="page")
    except pdf_engine.EngineUnavailable as failure:
        raise RenderError(pdf_engine.RENDER_UNAVAILABLE) from failure
    except pdf_engine.SourceUnreadable as failure:
        raise RenderError(f"could not rasterize every page: {failure}") from failure


def render(run: Path, docx: Path) -> tuple[str, Path, int]:
    if not run.is_dir():
        raise RenderError(f"no run directory at {run}")
    if not docx.is_file() or docx.suffix.casefold() != ".docx":
        raise RenderError(f"no Word file at {docx}")
    docx_digest = file_digest.sha256(docx)

    def build(staging: Path) -> tuple[str, int]:
        with tempfile.TemporaryDirectory() as conversion_directory:
            source, exported = _automated_export(
                docx.resolve(), Path(conversion_directory)
            )
            pages = _rasterize(exported, staging)
            shutil.copy2(exported, staging / f"assignment-docx{exported.suffix.casefold()}")
        retained = tuple(staging.glob("*.png"))
        if not pages or not render_pass.images_cover_exported_pages(len(retained), pages):
            raise RenderError(
                f"rasterizer retained {len(retained)} page image(s) for {pages} pages"
            )
        file_digest.write_recorded_sha256(
            staging / FINGERPRINT_FILE, docx_digest
        )
        return source, pages

    destination, (source, pages) = render_pass.retain_staged_pass(
        run / "render", build
    )
    return source, destination, pages


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        usage="assignment_docx_render.py <run directory> --docx <Word file>"
    )
    parser.add_argument("run")
    parser.add_argument("--docx", required=True)
    try:
        args = parser.parse_args(argv)
        source, destination, pages = render(Path(args.run), Path(args.docx))
    except (RenderError, OSError) as failure:
        print(f"render did not complete: {failure}", file=sys.stderr)
        return 2
    print(f"SOURCE: {source}")
    print(f"PAGES: {pages} of {pages} imaged")
    print(f"PIXELS: {destination}")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
