#!/usr/bin/env python3
"""Render one discussion-post DOCX into a new retained render pass.

The command asks a freshly spawned Microsoft Word instance for a PDF, falling
back to XPS, then rasterizes every page with PyMuPDF. It never edits
``post.md``: the independent visual reader appends the ``RENDERED`` record only
after comparing these pixels with the Markdown.

Exit 0 means the page-faithful export and all of its page images were retained.
Exit 2 means rendering did not complete; a partial pass is removed and never
presented as evidence.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from console_codec import use_utf8
import office_process
import render_pass
from discussion_artifact import (
    AUTOMATED_RENDERED_SOURCES,
    RENDERED_RASTER_DPI as RASTER_DPI,
)


EXPORT_TIMEOUT_SECONDS = 20


class RenderError(Exception):
    pass


def _word_attempt(
    docx: Path, output_directory: Path, mode: str
) -> tuple[str, Path]:
    script = Path(__file__).with_suffix(".ps1")
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
        raise RenderError(str(failure)) from failure
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


def _pages_from_exports(
    pymupdf,
    docx: Path,
    conversion_directory: Path,
    staging: Path,
    expected_pages: int | None,
    clinician_export: Path | None,
) -> tuple[str | None, int | None, Path | None, tuple[str, ...]]:
    pages: int | None = None
    failures: list[str] = []
    routes: list[tuple[str, str, Path | None]] = [
        ("word-pdf", "pdf", None),
        ("word-xps", "xps", None),
    ]
    if clinician_export is not None:
        routes.append(
            (
                "clinician",
                clinician_export.suffix.lower().lstrip("."),
                clinician_export,
            )
        )
    for route_source, mode, supplied_export in routes:
        for prior_pixel in staging.glob("*.png"):
            prior_pixel.unlink()
        try:
            converted = supplied_export
            if converted is None:
                route_source, converted = _word_attempt(docx, conversion_directory, mode)
            with pymupdf.open(str(converted)) as document:
                route_pages = len(document)
                if route_pages < 1:
                    raise RenderError(f"{route_source} export contains no pages")
                if pages is not None and route_pages != pages:
                    raise RenderError(
                        f"{route_source} reports {route_pages} pages after the earlier "
                        f"route reported {pages}"
                    )
                pages = route_pages
                if expected_pages is not None and route_pages != expected_pages:
                    raise RenderError(
                        f"{route_source} reports {route_pages} pages, not "
                        f"--expected-pages {expected_pages}"
                    )
                missed: list[int] = []
                for number, page in enumerate(document, start=1):
                    target = staging / f"page-{number}.png"
                    partial = staging / f".page-{number}.{mode}.building.png"
                    try:
                        page.get_pixmap(dpi=RASTER_DPI).save(partial)
                        partial.replace(target)
                    except Exception:
                        partial.unlink(missing_ok=True)
                        missed.append(number)
                if not missed:
                    return route_source, pages, converted, tuple(failures)
                failures.append(
                    f"{route_source} could not rasterize page(s) "
                    + ", ".join(str(number) for number in missed)
                )
        except RenderError as failure:
            failures.append(str(failure))
        except Exception as failure:
            failures.append(f"could not read the {route_source} export: {failure}")
    return None, pages, None, tuple(failures)


def render(
    run: Path,
    docx: Path,
    expected_pages: int | None = None,
    clinician_export: Path | None = None,
) -> tuple[str, Path, int]:
    if not run.is_dir():
        raise RenderError(f"no run directory at {run}")
    if not docx.is_file():
        raise RenderError(f"no rendered document at {docx}")
    try:
        import pymupdf
    except ImportError as failure:
        raise RenderError("pymupdf is not installed") from failure

    if expected_pages is not None and expected_pages < 1:
        raise RenderError("--expected-pages must be a positive integer")
    if clinician_export is not None:
        if (
            clinician_export.suffix.lower() not in {".pdf", ".xps"}
            or not clinician_export.is_file()
        ):
            raise RenderError("--clinician-export must be an existing PDF or XPS")
    render_root = run / "render"
    def build(staging: Path) -> tuple[str, int]:
        with tempfile.TemporaryDirectory() as conversion_directory:
            source, pages, retained_export, failures = _pages_from_exports(
                pymupdf,
                docx.resolve(),
                Path(conversion_directory),
                staging,
                expected_pages,
                clinician_export,
            )
            if source is None or pages is None or retained_export is None:
                raise RenderError("; ".join(failures))
            shutil.copy2(
                retained_export,
                staging / f"post{retained_export.suffix.lower()}",
            )
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
        usage="discussion_post_render.py <run directory> --docx <Word file>"
    )
    parser.add_argument("run")
    parser.add_argument("--docx", required=True)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--clinician-export")
    try:
        args = parser.parse_args(argv)
        source, destination, pages = render(
            Path(args.run),
            Path(args.docx),
            args.expected_pages,
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
    raise SystemExit(main(sys.argv[1:]))
