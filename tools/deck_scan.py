#!/usr/bin/env python3
"""Grade a course-assignment PowerPoint against its signed run bar.

    python tools/deck_scan.py <run directory> --pptx <PowerPoint file> [--show]

Container rows read only ``ppt/slides/``. The cost-claim row reads both slide
faces and ``ppt/notesSlides/``. Counts print by default because a course
artifact can contain private material; ``--show`` exposes finding details.
"""

from __future__ import annotations

import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from xml.etree import ElementTree

import run_grader


A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
FIELD = re.compile(r"(?mi)^(?P<name>[A-Z][A-Z-]+)\s*:\s*(?P<value>[^\n]+?)\s*$")
SLIDE_PART = re.compile(r"^ppt/slides/slide(?P<number>[1-9]\d*)\.xml$")
NOTES_PART = re.compile(r"^ppt/notesSlides/notesSlide(?P<number>[1-9]\d*)\.xml$")
WORD = re.compile(r"(?:\$?\d[\d,.]*|[A-Za-z]+(?:[-'][A-Za-z]+)*)")
COST = re.compile(
    r"(?<![\w$])\$\s*(?P<amount>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?)(?![\d,])"
)
CLAIM_HEADING = re.compile(r"(?mi)^## CLAIM:\s*(?P<claim>[^\n]*)$")

SLIDE_COUNT = "slide-count"
BULLETS_PER_SLIDE = "bullets-per-slide"
WORDS_PER_BULLET = "words-per-bullet"
FONT_POINTS = "font-points"
UNTRACED_COST = "untraced-costed-figure"
ROWS = (
    SLIDE_COUNT,
    BULLETS_PER_SLIDE,
    WORDS_PER_BULLET,
    FONT_POINTS,
    UNTRACED_COST,
)

REQUIRED_BAR_FIELDS = (
    "ASSIGNMENT",
    "SIGNED",
    "ARTIFACT",
    "SLIDE-MAX",
    "BULLETS-PER-SLIDE",
    "WORDS-PER-BULLET",
    "FONT-POINTS",
    "FONT-DIRECTION",
    "SOURCE-CLASSES",
    "RECENCY-WINDOW-YEARS",
)
ACCEPTED_ARTIFACTS = ("deck",)
FONT_DIRECTIONS = ("ceiling", "floor")


@dataclass(frozen=True)
class DeclaredLimit:
    key: str
    limit: str


DECLARED_LIMITS = (
    DeclaredLimit(
        "adversarial-completeness-unverified",
        "The adversarial artifact read has no closed expected set, so no mechanical row proves that it found every unsupported assertion.",
    ),
    DeclaredLimit(
        "image-provenance-unverified",
        "Nothing in a PowerPoint file proves whether an image is a photograph or generated, so no mechanical row can reject a generated image presented as the actual site.",
    ),
)
NOT_REACHED = tuple(row.limit for row in DECLARED_LIMITS)


@dataclass(frozen=True)
class Bar:
    slide_max: int
    bullets_per_slide: int
    words_per_bullet: int
    font_points: int
    font_direction: str


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    slide: int | None = None
    detail: str = ""


@dataclass(frozen=True)
class Slide:
    number: int
    text: str
    bullets: tuple[str, ...]
    font_sizes: tuple[tuple[str, float | None], ...]


@dataclass(frozen=True)
class Source:
    root: Path
    deck: Path
    bar: Bar
    slides: tuple[Slide, ...]
    notes: tuple[str, ...]
    claims: str


@dataclass(frozen=True)
class Scan:
    slides_read: int
    bullets_read: int
    words_read: int
    font_runs_read: int
    costs_read: int
    findings: tuple[Finding, ...]


def _integer(fields: dict[str, str], name: str) -> int:
    value = fields[name]
    if not value.isdigit():
        raise run_grader.SourceError(f"bar.md needs an integer {name} field")
    return int(value)


def _read_bar(text: str) -> Bar:
    matches = tuple(FIELD.finditer(text))
    fields = {match.group("name"): match.group("value").strip() for match in matches}
    for name in REQUIRED_BAR_FIELDS:
        count = sum(match.group("name") == name for match in matches)
        if count > 1:
            raise run_grader.SourceError(f"bar.md has a duplicate {name} field")
        if count == 0:
            raise run_grader.SourceError(f"bar.md needs a {name} field")
    try:
        date.fromisoformat(fields["SIGNED"])
    except ValueError as failure:
        raise run_grader.SourceError("bar.md SIGNED must be an ISO date") from failure
    artifact = fields["ARTIFACT"].casefold()
    if artifact not in ACCEPTED_ARTIFACTS:
        raise run_grader.SourceError(
            "bar.md ARTIFACT must be deck; deck is the only accepted value"
        )
    direction = fields["FONT-DIRECTION"].casefold()
    if direction not in FONT_DIRECTIONS:
        raise run_grader.SourceError("bar.md FONT-DIRECTION must be ceiling or floor")
    return Bar(
        _integer(fields, "SLIDE-MAX"),
        _integer(fields, "BULLETS-PER-SLIDE"),
        _integer(fields, "WORDS-PER-BULLET"),
        _integer(fields, "FONT-POINTS"),
        direction,
    )


def _text(node: ElementTree.Element) -> str:
    return "".join(item.text or "" for item in node.iter(A + "t")).strip()


def _paragraph_font_sizes(paragraph: ElementTree.Element) -> tuple[tuple[str, float | None], ...]:
    default = paragraph.find("./" + A + "pPr/" + A + "defRPr")
    ending = paragraph.find("./" + A + "endParaRPr")
    fallback = (default if default is not None else ending)
    fallback_size = fallback.get("sz") if fallback is not None else None
    runs = []
    for run in paragraph.findall("./" + A + "r"):
        text = _text(run)
        if not text:
            continue
        properties = run.find("./" + A + "rPr")
        raw = properties.get("sz") if properties is not None else fallback_size
        points = int(raw) / 100 if raw and raw.isdigit() else None
        runs.append((text, points))
    return tuple(runs)


def _read_slide(number: int, payload: bytes) -> Slide:
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as failure:
        raise run_grader.SourceError(f"could not read slide {number} XML") from failure
    all_text: list[str] = []
    bullets: list[str] = []
    font_sizes: list[tuple[str, float | None]] = []
    for shape in root.iter(P + "sp"):
        placeholder = shape.find("./" + P + "nvSpPr/" + P + "nvPr/" + P + "ph")
        shape_type = placeholder.get("type", "body") if placeholder is not None else "body"
        title = shape_type in {"title", "ctrTitle"}
        body = shape.find("./" + P + "txBody")
        if body is None:
            continue
        for paragraph in body.findall("./" + A + "p"):
            text = _text(paragraph)
            if not text:
                continue
            all_text.append(text)
            if not title:
                bullets.append(text)
            font_sizes.extend(_paragraph_font_sizes(paragraph))
    for frame in root.iter(P + "graphicFrame"):
        for paragraph in frame.iter(A + "p"):
            text = _text(paragraph)
            if not text:
                continue
            all_text.append(text)
            bullets.append(text)
            font_sizes.extend(_paragraph_font_sizes(paragraph))
    return Slide(number, "\n".join(all_text), tuple(bullets), tuple(font_sizes))


def _read_notes(payload: bytes, number: int) -> str:
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as failure:
        raise run_grader.SourceError(f"could not read notes slide {number} XML") from failure
    return "\n".join(filter(None, (_text(item) for item in root.iter(A + "p"))))


def _parts(archive: zipfile.ZipFile, pattern: re.Pattern[str]) -> tuple[tuple[int, str], ...]:
    found = []
    for name in archive.namelist():
        match = pattern.fullmatch(name)
        if match:
            found.append((int(match.group("number")), name))
    return tuple(sorted(found))


def load(parsed: run_grader.Parsed) -> Source:
    root = Path(parsed.source)
    deck_value = parsed.value("--pptx")
    if not root.is_dir():
        raise run_grader.SourceError(f"no run directory at {root}")
    if deck_value is None:
        raise run_grader.SourceError("--pptx needs a PowerPoint file")
    deck = Path(deck_value)
    bar_path, claims_path = root / "bar.md", root / "claims.md"
    if not bar_path.is_file() or not claims_path.is_file():
        raise run_grader.SourceError("run needs bar.md and claims.md before it can be scanned")
    if not deck.is_file():
        raise run_grader.SourceError(f"no PowerPoint file at {deck}")
    try:
        bar = _read_bar(bar_path.read_text(encoding="utf-8"))
        claims = claims_path.read_text(encoding="utf-8")
        with zipfile.ZipFile(deck) as archive:
            slide_parts = _parts(archive, SLIDE_PART)
            if not slide_parts:
                raise run_grader.SourceError("PowerPoint contains no readable slide parts")
            slides = tuple(_read_slide(number, archive.read(name)) for number, name in slide_parts)
            notes = tuple(
                _read_notes(archive.read(name), number)
                for number, name in _parts(archive, NOTES_PART)
            )
    except (OSError, UnicodeError, zipfile.BadZipFile, KeyError) as failure:
        raise run_grader.SourceError(f"could not read the deck run: {failure}") from failure
    return Source(root, deck, bar, slides, notes, claims)


def _costs(text: str) -> set[str]:
    return {match.group("amount").replace(",", "") for match in COST.finditer(text)}


def _claim_costs(text: str) -> set[str]:
    return {
        amount
        for match in CLAIM_HEADING.finditer(text)
        for amount in _costs(match.group("claim"))
    }


def survey(source: Source) -> Scan:
    findings: list[Finding] = []
    if len(source.slides) > source.bar.slide_max:
        findings.append(Finding(SLIDE_COUNT, None, f"{len(source.slides)} slides exceeds {source.bar.slide_max}"))
    bullets_read = words_read = font_runs_read = 0
    for slide in source.slides:
        bullets_read += len(slide.bullets)
        if len(slide.bullets) > source.bar.bullets_per_slide:
            findings.append(Finding(BULLETS_PER_SLIDE, slide.number, f"{len(slide.bullets)} bullets exceeds {source.bar.bullets_per_slide}"))
        for bullet in slide.bullets:
            count = len(WORD.findall(bullet))
            words_read += count
            if count > source.bar.words_per_bullet:
                findings.append(Finding(WORDS_PER_BULLET, slide.number, f"{count} words exceeds {source.bar.words_per_bullet}"))
        font_failures = []
        for text, points in slide.font_sizes:
            font_runs_read += 1
            violates = points is None or (
                source.bar.font_direction == "ceiling" and points > source.bar.font_points
            ) or (
                source.bar.font_direction == "floor" and points < source.bar.font_points
            )
            if violates:
                detail = "font size is not explicit" if points is None else f"{points:g} points violates {source.bar.font_direction} {source.bar.font_points}"
                font_failures.append(detail)
        if font_failures:
            findings.append(Finding(FONT_POINTS, slide.number, font_failures[0]))
    artifact_costs = _costs("\n".join([*(slide.text for slide in source.slides), *source.notes]))
    recorded_costs = _claim_costs(source.claims)
    for amount in sorted(artifact_costs - recorded_costs):
        findings.append(Finding(UNTRACED_COST, None, f"${amount} has no claim record"))
    return Scan(
        len(source.slides),
        bullets_read,
        words_read,
        font_runs_read,
        len(artifact_costs),
        tuple(findings),
    )


def format_report(scan: Scan, _source: str, show: bool = False) -> str:
    lines = [
        "deck scan",
        "",
        f"  slides read       {scan.slides_read}",
        f"  bullets read      {scan.bullets_read}",
        f"  words read        {scan.words_read}",
        f"  font runs read    {scan.font_runs_read}",
        f"  costed figures    {scan.costs_read}",
        "",
    ]
    for row in ROWS:
        lines.append(f"{row}: {sum(finding.kind == row for finding in scan.findings)}")
    if show:
        lines += ["", "findings:"]
        for finding in scan.findings:
            location = f"slide {finding.slide}: " if finding.slide is not None else ""
            lines.append(f"  {finding.kind}: {location}{finding.detail}")
    return "\n".join(lines)


def grade(source: Source, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scanned = survey(source)
    return run_grader.Grade(
        scan=scanned,
        source=str(source.root),
        findings_failed=bool(scanned.findings),
        diagnostics=("deck findings require review",) if scanned.findings else (),
    )


GRADER = run_grader.Grader(
    usage="usage: deck_scan.py <run directory> --pptx <PowerPoint file> [--show]",
    load=load,
    grade=grade,
    format_report=format_report,
    options=(
        run_grader.Option("--pptx", takes_value=True, missing_value="--pptx needs a PowerPoint file", repeatable=False),
        run_grader.Option("--show", repeatable=False),
    ),
    allow_extra_positionals=False,
)


def main(argv: list[str]) -> int:
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
