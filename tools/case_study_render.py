#!/usr/bin/env python3
"""Render one case-study DOCX into a new retained render pass.

The automated route asks a freshly spawned Microsoft Word instance for PDF.
A returned failure advances to XPS; reaching the process bound ends automation
at this site. A clinician-supplied PDF or XPS is accepted on a later invocation.

Exit 0 means the page-faithful export and all page images were retained. Exit 2
means rendering did not complete; no partial pass is presented as evidence.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from console_codec import require_python_floor, use_utf8
import office_process
import page_image
import pdf_engine
import render_pass


RASTER_DPI = page_image.RASTER_DPI
# This bound is uncalibrated. It is a safety stop, not a timing measurement,
# and reaching it is terminal for automation at this site.
EXPORT_TIMEOUT_SECONDS = 20


class RenderError(Exception):
    pass


class ExportBoundReached(RenderError):
    pass


def _word_attempt(docx: Path, output_directory: Path, mode: str) -> tuple[str, Path]:
    script = Path(__file__).with_name("word_export.ps1")
    ownership_file = output_directory / f"{mode}-word-pid.txt"
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
        "case-study",
        "-OwnershipFile",
        str(ownership_file),
    ]
    try:
        completed = office_process.run_owned_process(
            command,
            ownership_file,
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
    expected_source = f"word-{mode}"
    if source != expected_source:
        raise RenderError(f"Word export returned an unrecognized source: {source!r}")
    if not output.is_file():
        raise RenderError(f"Word export did not create {output}")
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
        raise RenderError("pymupdf is not installed") from failure
    except pdf_engine.SourceUnreadable as failure:
        message = str(failure)
        if message == page_image.EMPTY_EXPORT or message.startswith("could not rasterize"):
            raise RenderError(message) from failure
        raise RenderError(f"could not read the export: {message}") from failure


def render(
    run: Path,
    docx: Path,
    clinician_export: Path | None = None,
) -> tuple[str, Path, int]:
    if not run.is_dir():
        raise RenderError(f"no run directory at {run}")
    if not docx.is_file():
        raise RenderError(f"no rendered document at {docx}")
    if clinician_export is not None and (
        clinician_export.suffix.lower() not in {".pdf", ".xps"}
        or not clinician_export.is_file()
    ):
        raise RenderError("--clinician-export must be an existing PDF or XPS")
    if pdf_engine.engine_version() is None:
        raise RenderError("pymupdf is not installed")

    render_root = run / "render"

    def build(staging: Path) -> tuple[str, int]:
        if clinician_export is not None:
            source, exported = "clinician", clinician_export
            pages = _rasterize(exported, staging)
            shutil.copy2(exported, staging / f"case-study{exported.suffix.lower()}")
        else:
            with tempfile.TemporaryDirectory() as conversion_directory:
                source, exported = _automated_export(
                    docx.resolve(), Path(conversion_directory)
                )
                pages = _rasterize(exported, staging)
                shutil.copy2(exported, staging / f"case-study{exported.suffix.lower()}")
        retained = tuple(staging.glob("*.png"))
        if not render_pass.images_cover_exported_pages(len(retained), pages):
            raise RenderError(
                f"rasterizer retained {len(retained)} page image(s) for {pages} pages"
            )
        return source, pages

    destination, (source, pages) = render_pass.retain_staged_pass(render_root, build)
    return source, destination, pages


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        usage="case_study_render.py <run directory> --docx <Word file>"
    )
    parser.add_argument("run")
    parser.add_argument("--docx", required=True)
    parser.add_argument("--clinician-export")
    try:
        args = parser.parse_args(argv)
        source, destination, pages = render(
            Path(args.run),
            Path(args.docx),
            Path(args.clinician_export) if args.clinician_export else None,
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
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
