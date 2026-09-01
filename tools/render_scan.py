#!/usr/bin/env python3
"""Grade retained page coverage for a practicum case-study run.

    python tools/render_scan.py <a run directory> [--show]

Each canonical uninterrupted ``render/pass-N`` keeps exactly one page-faithful
PDF or XPS and one readable PNG per imaged page. The export supplies the
page-count denominator; the readable-PNG count supplies the numerator. Earlier passes are reported and may be incomplete after
a reader stopped on a defect. Only the last pass must cover every exported page.

Default output reports aggregate and per-pass counts only. ``--show`` adds
pass-level finding detail. Exit 0
means the final pass is complete, 1 means its measurable page coverage is short,
and 2 means the evidence needed to measure coverage was unavailable. A measured
finding outranks unavailable evidence elsewhere in the run.

All output is pasteable. Reports and diagnostics carry only counts, ``pass-N``
labels, and fixed explanations; they never print a run path, export filename, or
page image filename.

This does not establish that the retained images are the pages a reader actually
read, or that the visual comparison was careful. ``checks_ledger.py`` separately
grades the substantiated ``the rendered document`` verdict for that reading.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import run_grader


FINAL_PAGE_COVERAGE = "final-page-coverage"

ROWS = {
    FINAL_PAGE_COVERAGE: (
        "practicum-case-study step 9 - final retained render covers every exported page"
    ),
}
KINDS = tuple(ROWS)

INVALID_INVOCATION = "invalid invocation"
NO_RUN_DIRECTORY = "no run directory"
NO_RENDER_DIRECTORY = "no render directory"
NO_RENDER_PASSES = "no numbered render passes"
NONCANONICAL_PASSES = "render passes are not canonical and uninterrupted"
UNREADABLE_EXPORT = "render pass has no readable retained export"
EXIT_2_LIMBS = (
    INVALID_INVOCATION,
    NO_RUN_DIRECTORY,
    NO_RENDER_DIRECTORY,
    NO_RENDER_PASSES,
    NONCANONICAL_PASSES,
    UNREADABLE_EXPORT,
)

EXPORT_SUFFIXES = frozenset({".pdf", ".xps"})
PASS_DIRECTORY = re.compile(r"pass-(\d+)")


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    pass_name: str = "unknown"
    detail: str = ""


@dataclass(frozen=True)
class RenderPass:
    number: int
    path: Path
    pixels: tuple[Path, ...]
    exports: tuple[Path, ...]
    exported_pages: int | None
    read_error: str = ""
    unreadable_pixels: int = 0


@dataclass(frozen=True)
class PassCoverage:
    pass_name: str
    exported_pages: int | None
    page_images: int


@dataclass(frozen=True)
class Source:
    root: Path
    passes: tuple[RenderPass, ...]
    coverage_limbs: tuple[str, ...] = ()


@dataclass(frozen=True)
class Scan:
    passes_read: int
    exported_pages: int
    page_images: int
    incomplete_earlier_passes: int
    unscanned_passes: int
    pass_coverage: tuple[PassCoverage, ...]
    findings: tuple[Finding, ...] = ()


def _numbered_passes(render_root: Path) -> tuple[tuple[int, Path], ...]:
    found = []
    for child in render_root.iterdir():
        match = PASS_DIRECTORY.fullmatch(child.name)
        if child.is_dir() and match:
            found.append((int(match.group(1)), child))
    return tuple(sorted(found))


def _pass_history_is_canonical(numbered: tuple[tuple[int, Path], ...]) -> bool:
    expected = tuple(range(1, len(numbered) + 1))
    actual = tuple(number for number, _path in numbered)
    return actual == expected and all(
        path.name == f"pass-{number}" for number, path in numbered
    )


def _read_export_pages(exports: tuple[Path, ...]) -> tuple[int | None, str]:
    if not exports:
        return None, "keeps no retained PDF or XPS export"
    if len(exports) != 1:
        return None, f"keeps {len(exports)} retained PDF or XPS exports, not 1"
    try:
        import pymupdf
    except ImportError:
        return None, "PyMuPDF is unavailable"
    try:
        with pymupdf.open(str(exports[0])) as document:
            pages = len(document)
    except Exception:
        return None, "could not read the retained export"
    if pages < 1:
        return None, "the retained export contains no pages"
    return pages, ""


def _pixel_read_error(path: Path) -> str:
    try:
        import pymupdf
    except ImportError:
        return "PyMuPDF is unavailable"
    try:
        with pymupdf.open(str(path)) as document:
            if len(document) != 1:
                return "does not decode as one image page"
            next(iter(document)).get_pixmap(dpi=120)
    except Exception:
        return "could not decode the retained page image"
    return ""


def _load(parsed: run_grader.Parsed) -> Source:
    root = Path(parsed.source)
    if not root.is_dir():
        raise run_grader.SourceError(
            "no run directory at the supplied path", exit_2_limb=NO_RUN_DIRECTORY
        )
    render_root = root / "render"
    if not render_root.is_dir():
        raise run_grader.SourceError(
            "no render directory in the supplied run", exit_2_limb=NO_RENDER_DIRECTORY
        )
    numbered = _numbered_passes(render_root)
    if not numbered:
        raise run_grader.SourceError(
            f"no numbered render passes in {render_root.name}",
            exit_2_limb=NO_RENDER_PASSES,
        )

    passes = []
    for number, path in numbered:
        nominal_pixels = tuple(
            sorted(item for item in path.glob("*.png") if item.is_file())
        )
        pixel_errors = tuple(_pixel_read_error(item) for item in nominal_pixels)
        pixels = tuple(
            item for item, error in zip(nominal_pixels, pixel_errors) if not error
        )
        exports = tuple(
            sorted(
                item
                for item in path.iterdir()
                if item.is_file() and item.suffix.lower() in EXPORT_SUFFIXES
            )
        )
        exported_pages, read_error = _read_export_pages(exports)
        passes.append(
            RenderPass(
                number,
                path,
                pixels,
                exports,
                exported_pages,
                read_error,
                sum(bool(error) for error in pixel_errors),
            )
        )
    limbs = []
    if not _pass_history_is_canonical(numbered):
        limbs.append(NONCANONICAL_PASSES)
    if any(render_pass.exported_pages is None for render_pass in passes):
        limbs.append(UNREADABLE_EXPORT)
    return Source(root, tuple(passes), tuple(limbs))


def survey(passes: tuple[RenderPass, ...]) -> Scan:
    final = passes[-1]
    findings = []
    if (
        final.exported_pages is not None
        and len(final.pixels) < final.exported_pages
    ):
        findings.append(
            Finding(
                FINAL_PAGE_COVERAGE,
                final.path.name,
                f"keeps {len(final.pixels)} page image(s) for "
                f"{final.exported_pages} exported page(s)",
            )
        )
    return Scan(
        passes_read=len(passes),
        exported_pages=sum(item.exported_pages or 0 for item in passes),
        page_images=sum(len(item.pixels) for item in passes),
        incomplete_earlier_passes=sum(
            1
            for item in passes[:-1]
            if item.exported_pages is not None
            and len(item.pixels) < item.exported_pages
        ),
        unscanned_passes=sum(item.exported_pages is None for item in passes),
        pass_coverage=tuple(
            PassCoverage(item.path.name, item.exported_pages, len(item.pixels))
            for item in passes
        ),
        findings=tuple(findings),
    )


def format_report(scan: Scan, _source: str, show: bool = False) -> str:
    lines = [
        "render scan",
        "",
        f"  passes read                 {scan.passes_read}",
        f"  exported pages              {scan.exported_pages}",
        f"  page images                 {scan.page_images}",
        f"  incomplete earlier passes   {scan.incomplete_earlier_passes}",
        f"  unscanned passes            {scan.unscanned_passes}",
        "",
        "pass coverage:",
    ]
    lines.extend(
        f"  {item.pass_name}: {item.page_images} of {item.exported_pages} readable page images"
        if item.exported_pages is not None
        else f"  {item.pass_name}: unmeasured"
        for item in scan.pass_coverage
    )
    lines += [
        "",
        f"{FINAL_PAGE_COVERAGE}: {len(scan.findings)}",
    ]
    if show:
        lines += ["", "findings:"]
        lines.extend(
            f"  {finding.pass_name}: {finding.detail}"
            for finding in scan.findings
        )
    return "\n".join(lines)


def _grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey(source.passes)
    diagnostics = []
    if NONCANONICAL_PASSES in source.coverage_limbs:
        diagnostics.append(
            "render passes must use canonical uninterrupted pass-1 through pass-N directories"
        )
    for render_pass in source.passes:
        if render_pass.read_error:
            diagnostics.append(f"{render_pass.path.name}: {render_pass.read_error}")
        if render_pass.unreadable_pixels:
            noun = "image" if render_pass.unreadable_pixels == 1 else "images"
            diagnostics.append(
                f"{render_pass.path.name}: {render_pass.unreadable_pixels} unreadable page {noun}"
            )
    if scan.findings:
        diagnostics.append("final render pass is short of its exported page count")
    return run_grader.Grade(
        scan=scan,
        source="run directory",
        findings_failed=bool(scan.findings),
        coverage_failed=bool(source.coverage_limbs),
        coverage_limbs=source.coverage_limbs,
        diagnostics=tuple(diagnostics),
    )


GRADER = run_grader.Grader(
    usage="usage: render_scan.py <a run directory> [--show]",
    options=(run_grader.Option("--show"),),
    load=_load,
    grade=_grade,
    format_report=format_report,
    exit_2_limbs=EXIT_2_LIMBS,
    invalid_invocation_limb=INVALID_INVOCATION,
)


def main(argv: list[str]) -> int:
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
