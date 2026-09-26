#!/usr/bin/env python3
"""Grade a course-assignment PowerPoint against its signed run bar.

    python tools/deck_scan.py <run directory> --pptx <PowerPoint file> [--show] [--submission <key>]

Container rows read slide XML plus referenced SmartArt data and chart parts.
The figure-claim row reads those slide faces and ``ppt/notesSlides/``. Counts
print by default because a course artifact can contain private material;
``--show`` exposes finding details.

The shared completion rows' ceilings belong to
``project_context.DECLARED_LIMITS`` and ``voice_read.DECLARED_LIMITS``; this
module copies no row.
"""

from __future__ import annotations

import re
import sys
import zipfile
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from posixpath import dirname, join, normpath
from xml.etree import ElementTree

import run_grader
import aar_scan
import assignment_bar
import assignment_submission
import heading_read
import research_ledger
import file_digest
import render_pass
import voice_model_identity
import voice_read
import project_context
from discussion_artifact import (
    CLAIM_BLOCK,
    PostedReading,
    claim_record_can_certify_values,
    read_posted_readings,
)
from discussion_post_scan import traceable_numeric_values
from research_ledger import REFUTATION_EVIDENCE_COMPLEMENT


A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
DGM = "{http://schemas.openxmlformats.org/drawingml/2006/diagram}"
DSP = "{http://schemas.microsoft.com/office/drawing/2008/diagram}"
C = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
PACKAGE_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
FIELD = re.compile(r"(?mi)^(?P<name>[A-Z][A-Z-]+)\s*:\s*(?P<value>[^\n]+?)\s*$")
SLIDE_PART = re.compile(r"^ppt/slides/slide(?P<number>[1-9]\d*)\.xml$")
NOTES_PART = re.compile(r"^ppt/notesSlides/notesSlide(?P<number>[1-9]\d*)\.xml$")
WORD = re.compile(r"(?:\$?\d[\d,.]*|[A-Za-z]+(?:[-'\u2019][A-Za-z]+)*)")
RENDERED_HEADER = re.compile(r"(?i)^[ \t]*#+[ \t]*RENDERED[ \t]*:[ \t]*(.*?)[ \t]*$")
RENDERED_FIELD = re.compile(
    r"(?i)^[ \t]*(PASS|SLIDES|SOURCE|UNSEEN|READ|VERDICT)[ \t]*:[ \t]*(.*?)[ \t]*$"
)
ADVERSARIAL_HEADER = re.compile(r"(?i)^[ \t]*#+[ \t]*ADVERSARIAL[ \t]*:[ \t]*(.*?)[ \t]*$")
ADVERSARIAL_FIELD = re.compile(
    r"(?i)^[ \t]*(PASS|SLIDES|UNSEEN|CLAIMS|VERDICT)[ \t]*:[ \t]*(.*?)[ \t]*$"
)
INTENT_HEADER = re.compile(r"(?i)^[ \t]*#+[ \t]*PRESENTATION-INTENT[ \t]*:[ \t]*(.*?)[ \t]*$")
INTENT_FIELDS = (
    "DRAFT",
    "CONTENT-SLIDES",
    "REFERENCE-SLIDES",
    "AUDIENCE-PURPOSE",
    "TALK-STYLE",
    "INTERNAL-COMMENTARY",
    "SPOKEN-ARC",
)
INTENT_FIELD = re.compile(
    rf"(?i)^[ \t]*({'|'.join(map(re.escape, INTENT_FIELDS))})[ \t]*:[ \t]*(.*?)[ \t]*$"
)
POSITIVE_INTEGER = re.compile(r"[1-9][0-9]*", re.ASCII)
SLIDES_READ = re.compile(r"([0-9]+)[ \t]+of[ \t]+([0-9]+)[ \t]+read", re.IGNORECASE | re.ASCII)

SLIDE_COUNT = "slide-count"
BULLETS_PER_SLIDE = "bullets-per-slide"
WORDS_PER_BULLET = "words-per-bullet"
FONT_POINTS = "font-points"
UNTRACED_FIGURE = "untraced-figure"
RENDERED_RECORD = "rendered-record"
ADVERSARIAL_RECORD = "adversarial-record"
PRESENTATION_INTENT_RECORD = "presentation-intent-record"
SUBMISSION_FINGERPRINT = "submission-fingerprint"
ROWS = (
    SLIDE_COUNT,
    BULLETS_PER_SLIDE,
    WORDS_PER_BULLET,
    FONT_POINTS,
    UNTRACED_FIGURE,
    RENDERED_RECORD,
    ADVERSARIAL_RECORD,
    PRESENTATION_INTENT_RECORD,
    SUBMISSION_FINGERPRINT,
) + heading_read.KINDS
KINDS = ROWS
HEADING_READ_ROWS = {kind: "the heading read agrees with the deck bytes and current claim headings" for kind in heading_read.KINDS}
EXPECTED_COMPLETION_CHECKS = (
    aar_scan.EXPECTED_ROW,
    voice_model_identity.EXPECTED_ROW,
    voice_read.EXPECTED_ROW,
    voice_read.PROFANITY_EXPECTED_ROW,
    project_context.EXPECTED_ROW,
)

REQUIRED_BAR_FIELDS = (
    "ASSIGNMENT",
    "SIGNED",
    "ARTIFACT",
    "SLIDE-MAX",
    "SLIDE-LIMIT-SCOPE",
    "BULLETS-PER-SLIDE",
    "WORDS-PER-BULLET",
    "FONT-POINTS",
    "FONT-DIRECTION",
    "AUDIENCE-PURPOSE",
    "TALK-STYLE",
    "SOURCE-CLASSES",
    "RECENCY-WINDOW-YEARS",
)
ACCEPTED_ARTIFACTS = ("deck",)
FONT_DIRECTIONS = ("ceiling", "floor")
SLIDE_LIMIT_SCOPES = ("all", "content")


@dataclass(frozen=True)
class DeclaredLimit:
    key: str
    limit: str


@dataclass(frozen=True)
class Relationship:
    kind: str
    target: str


UNJOINED_SOURCE_FIELDS = ", ".join(REFUTATION_EVIDENCE_COMPLEMENT)
SOURCED_FIELD_COMPLETENESS_LIMIT = DeclaredLimit(
    "sourced-field-completeness-unjoined",
    f"A sourced record missing one or more of {UNJOINED_SOURCE_FIELDS} is still believed by the figure certifier when both refutation-evidence fields carry substance; field completeness belongs to research_ledger.",
)

DECLARED_LIMITS = (
    DeclaredLimit(
        "presentation-intent-is-not-voice",
        "A clean presentation-intent record does not establish consistency with the clinician's canonical voice model; voice_read grades that separate ground.",
    ),
    DeclaredLimit(
        "claim-support-unverified",
        "A clean figure trace does not establish that a believed record supports the figure read from its heading.",
    ),
    DeclaredLimit(
        "record-slide-agreement-unverified",
        "No mechanical row checks that a believed record agrees with the slide it sources; the adversarial agreement read protects the deck the reader was given.",
    ),
    SOURCED_FIELD_COMPLETENESS_LIMIT,
    DeclaredLimit(
        "adversarial-completeness-unverified",
        "The adversarial artifact read has no closed expected set, so no mechanical row proves that it found every unsupported assertion.",
    ),
    DeclaredLimit(
        "image-provenance-unverified",
        "Nothing in a PowerPoint file proves whether an image is a photograph or generated, so no mechanical row can reject a generated image presented as the actual site.",
    ),
    DeclaredLimit(
        "slide-layout-text-unread",
        "Text drawn from the slide layout is not read, including text outside placeholders on a layout the slide uses.",
    ),
    DeclaredLimit(
        "alternative-text-unread",
        "Picture and 3D-model alternative text is not read as slide-face text.",
    ),
    DeclaredLimit(
        "value-axis-ticks-unread",
        "Computed value-axis tick labels are not stored as chart text and are not read.",
    ),
    DeclaredLimit(
        "chart-font-sizes-unread",
        "Chart font sizes are not graded because chart XML sizes did not agree with PowerPoint's rendered sizes in the measured population.",
    ),
    DeclaredLimit(
        "render-scan-run-unverified",
        "A skipped render_scan is not detected; the residue is a pass the producer did not write, one altered after retention, or a grading machine missing the PDF engine.",
    ),
    DeclaredLimit(
        "render-source-unproven",
        "The rendered-record SOURCE is declared and never proven.",
    ),
    DeclaredLimit(
        "platform-repair-after-reading-unobserved",
        "A platform-side repair after the recorded reading can change the submitted artifact without changing the local deck fingerprint.",
    ),
    DeclaredLimit(
        "submission-without-posting-evidence-unknown",
        "The command cannot infer that an absent posted-reading record represents a live submission rather than a deck that was never posted.",
    ),
    DeclaredLimit(
        "platform-bytes-unproven",
        "The deck digest identifies the local PowerPoint file and does not prove which bytes the learning platform retained.",
    ),
    DeclaredLimit(
        "reader-attention-unobservable",
        "A valid fingerprint proves file identity and cannot establish the attention or judgment behind the recorded verdict.",
    ),
)
NOT_REACHED = tuple(row.limit for row in DECLARED_LIMITS)


@dataclass(frozen=True)
class Bar:
    slide_max: int
    slide_limit_scope: str
    bullets_per_slide: int
    words_per_bullet: int
    font_points: int
    font_direction: str
    audience_purpose: str
    talk_style: str


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
    diagram_text_read: int = 0
    chart_text_read: int = 0
    unread_members: int = 0


@dataclass(frozen=True)
class RenderedRecord:
    deck: str
    fields: dict[str, str]
    counts: dict[str, int]

    def value(self, name: str) -> str:
        return self.fields.get(name, "")


@dataclass(frozen=True)
class RenderedAssessment:
    findings: tuple[Finding, ...]
    records: int
    passes: int
    unrecorded_passes: int
    report: str


@dataclass(frozen=True)
class Source:
    root: Path
    deck: Path
    deck_bytes: bytes
    bar: Bar
    slides: tuple[Slide, ...]
    notes: tuple[str, ...]
    claims: str
    rendered_text: str | None
    adversarial_text: str | None
    intent_text: str | None
    heading_read_text: str
    readings: tuple[PostedReading, ...]


@dataclass(frozen=True)
class Scan:
    slides_read: int
    slide_limit_scope: str
    slide_limit_count: int | None
    slide_limit_denominator: int
    slide_limit_matcher: str
    slide_limit_unread: int
    bullets_read: int
    words_read: int
    font_runs_read: int
    figures_read: int
    rendered_records: int
    retained_passes: int
    unrecorded_passes: int
    heading_reads: int
    heading_read_unread: int
    findings: tuple[Finding, ...]
    diagram_text_read: int = 0
    chart_text_read: int = 0
    unread_members: int = 0


def _integer(fields: dict[str, str], name: str) -> int:
    value = fields[name]
    if not value.isdigit():
        raise run_grader.SourceError(f"bar.md needs an integer {name} field")
    return int(value)


def _read_bar(
    text: str, envelope: assignment_bar.Envelope | None = None
) -> Bar:
    envelope = envelope or assignment_bar.parse(text)
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
    artifact = envelope.artifact
    if artifact not in ACCEPTED_ARTIFACTS:
        raise run_grader.SourceError(
            "bar.md ARTIFACT must be deck; deck is the only accepted value"
        )
    direction = fields["FONT-DIRECTION"].casefold()
    if direction not in FONT_DIRECTIONS:
        raise run_grader.SourceError("bar.md FONT-DIRECTION must be ceiling or floor")
    slide_limit_scope = fields["SLIDE-LIMIT-SCOPE"].casefold()
    if slide_limit_scope not in SLIDE_LIMIT_SCOPES:
        raise run_grader.SourceError("bar.md SLIDE-LIMIT-SCOPE must be all or content")
    if not fields["AUDIENCE-PURPOSE"].strip():
        raise run_grader.SourceError("bar.md AUDIENCE-PURPOSE needs a value")
    if not fields["TALK-STYLE"].strip():
        raise run_grader.SourceError("bar.md TALK-STYLE needs a value")
    return Bar(
        _integer(fields, "SLIDE-MAX"),
        slide_limit_scope,
        _integer(fields, "BULLETS-PER-SLIDE"),
        _integer(fields, "WORDS-PER-BULLET"),
        _integer(fields, "FONT-POINTS"),
        direction,
        fields["AUDIENCE-PURPOSE"],
        fields["TALK-STYLE"],
    )


def validate_bar(envelope: assignment_bar.Envelope) -> None:
    """Validate the deck branch fields without requiring a produced artifact."""

    text = "\n".join(
        f"{name}: {value}"
        for name, value in envelope.fields.items()
        for _ in range(envelope.counts.get(name, 0))
    )
    _read_bar(text, envelope)


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


def _paragraph_font_points(
    paragraph: ElementTree.Element,
) -> tuple[float | None, ...]:
    default = paragraph.find("./" + A + "pPr/" + A + "defRPr")
    ending = paragraph.find("./" + A + "endParaRPr")
    fallback = default if default is not None else ending
    fallback_size = fallback.get("sz") if fallback is not None else None
    points = []
    for run in paragraph.findall("./" + A + "r"):
        properties = run.find("./" + A + "rPr")
        raw = properties.get("sz") if properties is not None else fallback_size
        points.append(int(raw) / 100 if raw and raw.isdigit() else None)
    return tuple(points)


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


def _relationship_part(part: str) -> str:
    return join(dirname(part), "_rels", Path(part).name + ".rels")


def _relationships(archive: zipfile.ZipFile, part: str) -> dict[str, Relationship]:
    relationship_part = _relationship_part(part)
    if relationship_part not in archive.namelist():
        return {}
    root = ElementTree.fromstring(archive.read(relationship_part))
    return {
        relationship.get("Id", ""): Relationship(
            relationship.get("Type", ""),
            normpath(join(dirname(part), relationship.get("Target", ""))),
        )
        for relationship in root.findall(PACKAGE_REL + "Relationship")
        if relationship.get("Id") and relationship.get("Target")
    }


def _smartart_font_sizes(
    data_root: ElementTree.Element,
    drawing_root: ElementTree.Element,
) -> dict[str, tuple[tuple[float | None, ...], ...]]:
    presentation_ids: dict[str, str] = {}
    for point in data_root.iter(DGM + "pt"):
        properties = point.find("./" + DGM + "prSet")
        associated = properties.get("presAssocID") if properties is not None else None
        if point.get("type") == "pres" and point.get("modelId") and associated:
            presentation_ids[associated] = point.get("modelId", "")
    by_shape = {
        shape.get("modelId", ""): tuple(
            _paragraph_font_points(paragraph)
            for paragraph in shape.findall("./" + DSP + "txBody/" + A + "p")
        )
        for shape in drawing_root.iter(DSP + "sp")
        if shape.get("modelId")
    }
    return {
        point_id: by_shape.get(presentation_ids.get(point_id, point_id), ())
        for point_id in {
            point.get("modelId", "")
            for point in data_root.iter(DGM + "pt")
            if point.get("modelId")
        }
    }


def _read_smartart(
    archive: zipfile.ZipFile,
    relationships: dict[str, Relationship],
    data_id: str,
) -> tuple[tuple[str, ...], tuple[tuple[str, float | None], ...], int]:
    data_relationship = relationships.get(data_id)
    if data_relationship is None:
        return (), (), 1
    try:
        data_root = ElementTree.fromstring(archive.read(data_relationship.target))
    except (KeyError, ElementTree.ParseError):
        return (), (), 1
    extension = next(data_root.iter(DSP + "dataModelExt"), None)
    drawing_id = extension.get("relId", "") if extension is not None else ""
    drawing_relationship = relationships.get(drawing_id)
    if drawing_relationship is None:
        drawing_relationships = tuple(
            relationship
            for relationship in relationships.values()
            if relationship.kind.endswith("/diagramDrawing")
        )
        drawing_relationship = (
            drawing_relationships[0] if len(drawing_relationships) == 1 else None
        )
    if drawing_relationship is None:
        return (), (), 1
    try:
        drawing_root = ElementTree.fromstring(archive.read(drawing_relationship.target))
    except (KeyError, ElementTree.ParseError):
        return (), (), 1
    sizes_by_point = _smartart_font_sizes(data_root, drawing_root)
    paragraphs: list[str] = []
    font_sizes: list[tuple[str, float | None]] = []
    unread = 0
    for point in data_root.iter(DGM + "pt"):
        point_id = point.get("modelId", "")
        point_paragraphs = point.findall("./" + DGM + "t/" + A + "p")
        drawing_paragraphs = sizes_by_point.get(point_id, ())
        for index, paragraph in enumerate(point_paragraphs):
            text = _text(paragraph)
            if not text:
                continue
            paragraphs.append(text)
            if index < len(drawing_paragraphs) and drawing_paragraphs[index]:
                font_sizes.extend(
                    (text, points) for points in drawing_paragraphs[index]
                )
            else:
                unread = 1
    return tuple(paragraphs), tuple(font_sizes), unread


def _chart_cached_values(node: ElementTree.Element | None) -> tuple[str, ...]:
    if node is None:
        return ()
    return tuple(
        value.text.strip()
        for value in node.iter(C + "v")
        if value.text and value.text.strip()
    )


def _chart_points(node: ElementTree.Element | None) -> dict[int, str]:
    if node is None:
        return {}
    points: dict[int, str] = {}
    for point in node.iter(C + "pt"):
        index = point.get("idx")
        value = point.find("./" + C + "v")
        if index and index.isdigit() and value is not None and value.text:
            points[int(index)] = value.text.strip()
    return points


def _chart_flag(node: ElementTree.Element | None, name: str) -> bool | None:
    if node is None:
        return None
    flag = node.find("./" + C + name)
    if flag is None:
        return None
    return flag.get("val", "1") not in {"0", "false", "False"}


def _displayed_chart_value(value: str, format_code: str) -> str | None:
    try:
        number = Decimal(value)
    except InvalidOperation:
        return None
    if format_code == "0%":
        percent = (number * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return f"{percent:f}%"
    if format_code != "General":
        return None
    return format(float(number), ".15g")


def _read_chart(payload: bytes) -> tuple[tuple[str, ...], int]:
    root = ElementTree.fromstring(payload)
    text: list[str] = []
    title = root.find("./" + C + "chart/" + C + "title")
    if title is not None:
        title_text = _text(title)
        if title_text:
            text.append(title_text)
        else:
            text.extend(_chart_cached_values(title))
    unread = 0
    for series in root.iter(C + "ser"):
        series_text = _chart_cached_values(series.find("./" + C + "tx"))
        text.extend(series_text)
        text.extend(_chart_cached_values(series.find("./" + C + "cat")))
        value_source = series.find("./" + C + "val")
        values = _chart_points(value_source)
        cached_format = (
            next(
                (
                    item.text.strip()
                    for item in value_source.iter(C + "formatCode")
                    if item.text and item.text.strip()
                ),
                "",
            )
            if value_source is not None
            else ""
        )
        labels = series.find("./" + C + "dLbls")
        if labels is None:
            continue
        defaults = labels
        labels_by_index = {
            int(index.get("val", "")): label
            for label in labels.findall("./" + C + "dLbl")
            if (index := label.find("./" + C + "idx")) is not None
            and index.get("val", "").isdigit()
        }
        for index, value in values.items():
            label = labels_by_index.get(index)
            show_percent = _chart_flag(label, "showPercent")
            if show_percent is None:
                show_percent = _chart_flag(defaults, "showPercent")
            if show_percent:
                unread += 1
                continue
            show_value = _chart_flag(label, "showVal")
            if show_value is None:
                show_value = _chart_flag(defaults, "showVal")
            if not show_value:
                continue
            number_format = (
                label.find("./" + C + "numFmt") if label is not None else None
            )
            if number_format is None:
                number_format = defaults.find("./" + C + "numFmt")
            source_linked = (
                number_format is not None
                and number_format.get("sourceLinked", "0") not in {"0", "false", "False"}
            )
            format_code = (
                cached_format
                if source_linked and cached_format
                else number_format.get("formatCode", "")
                if number_format is not None
                else "General"
            )
            displayed = _displayed_chart_value(value, format_code)
            if displayed is None:
                unread += 1
            else:
                text.append(displayed)
    return tuple(text), unread


def _read_slide_objects(
    archive: zipfile.ZipFile,
    part: str,
    slide: Slide,
) -> Slide:
    root = ElementTree.fromstring(archive.read(part))
    relationships = _relationships(archive, part)
    diagram_text: list[str] = []
    diagram_fonts: list[tuple[str, float | None]] = []
    chart_text: list[str] = []
    unread = 0
    for relation in root.iter(DGM + "relIds"):
        text, fonts, missed = _read_smartart(
            archive, relationships, relation.get(R + "dm", "")
        )
        diagram_text.extend(text)
        diagram_fonts.extend(fonts)
        unread += missed
    for chart in root.iter(C + "chart"):
        relationship = relationships.get(chart.get(R + "id", ""))
        if relationship is None:
            unread += 1
            continue
        try:
            text, missed = _read_chart(archive.read(relationship.target))
        except (KeyError, ElementTree.ParseError):
            unread += 1
            continue
        chart_text.extend(text)
        unread += missed
    return Slide(
        slide.number,
        "\n".join(filter(None, (slide.text, *diagram_text, *chart_text))),
        slide.bullets + tuple(diagram_text),
        slide.font_sizes + tuple(diagram_fonts),
        len(diagram_text),
        len(chart_text),
        unread,
    )


def load(
    parsed: run_grader.Parsed,
    envelope: assignment_bar.Envelope | None = None,
) -> Source:
    root = Path(parsed.source)
    deck_value = parsed.value("--pptx")
    if not root.is_dir():
        raise run_grader.SourceError(f"no run directory at {root}")
    if deck_value is None:
        raise run_grader.SourceError("--pptx needs a PowerPoint file")
    deck = Path(deck_value)
    bar_path, claims_path, rendered_path = root / "bar.md", root / "claims.md", root / "rendered.md"
    adversarial_path = root / "adversarial.md"
    intent_path = root / "intent.md"
    reread_path = root / "reread.md"
    if not bar_path.is_file() or not claims_path.is_file():
        raise run_grader.SourceError("run needs bar.md and claims.md before it can be scanned")
    if not deck.is_file():
        raise run_grader.SourceError(f"no PowerPoint file at {deck}")
    try:
        bar = _read_bar(bar_path.read_text(encoding="utf-8"), envelope)
        claims = claims_path.read_text(encoding="utf-8")
        deck_bytes = deck.read_bytes()
        heading_read_path = root / "heading-read.md"
        heading_read_text = (
            heading_read_path.read_text(encoding="utf-8")
            if heading_read_path.is_file()
            else ""
        )
        with zipfile.ZipFile(deck) as archive:
            slide_parts = _parts(archive, SLIDE_PART)
            if not slide_parts:
                raise run_grader.SourceError("PowerPoint contains no readable slide parts")
            slides = tuple(
                _read_slide_objects(
                    archive, name, _read_slide(number, archive.read(name))
                )
                for number, name in slide_parts
            )
            notes = tuple(
                _read_notes(archive.read(name), number)
                for number, name in _parts(archive, NOTES_PART)
            )
    except (
        OSError,
        UnicodeError,
        zipfile.BadZipFile,
        KeyError,
        ElementTree.ParseError,
    ) as failure:
        raise run_grader.SourceError(f"could not read the deck run: {failure}") from failure
    try:
        rendered_text = rendered_path.read_text(encoding="utf-8") if rendered_path.is_file() else None
        adversarial_text = adversarial_path.read_text(encoding="utf-8") if adversarial_path.is_file() else None
        intent_text = intent_path.read_text(encoding="utf-8") if intent_path.is_file() else None
        readings = (
            read_posted_readings(reread_path.read_text(encoding="utf-8"))
            if reread_path.is_file()
            else ()
        )
    except (OSError, UnicodeError, ValueError) as failure:
        raise run_grader.SourceError(f"could not read the terminal deck records: {failure}") from failure
    return Source(
        root,
        deck,
        deck_bytes,
        bar,
        slides,
        notes,
        claims,
        rendered_text,
        adversarial_text,
        intent_text,
        heading_read_text,
        readings,
    )


def _submission_fingerprint_findings(
    source: Source, submission: str | None
) -> tuple[Finding, ...]:
    if submission is None:
        return ()
    reading = next(
        (item for item in source.readings if item.artifact == submission), None
    )
    if reading is None:
        return (
            Finding(
                SUBMISSION_FINGERPRINT,
                None,
                f"reread.md has no REREAD record for {submission}",
            ),
        )
    digest = file_digest.sha256(source.deck)
    if reading.submission_sha256_is_valid and reading.submission_sha256 == digest:
        return ()
    return (
        Finding(
            SUBMISSION_FINGERPRINT,
            None,
            f"{source.deck.name} SUBMISSION-SHA256 is missing, malformed, or stale",
        ),
    )


def _read_records(
    text: str, header_pattern: re.Pattern[str], field_pattern: re.Pattern[str]
) -> tuple[RenderedRecord, ...]:
    records: list[RenderedRecord] = []
    deck: str | None = None
    fields: dict[str, str] = {}
    counts: dict[str, int] = {}

    def close() -> None:
        if deck is not None:
            records.append(RenderedRecord(deck, dict(fields), dict(counts)))

    for line in text.splitlines():
        header = header_pattern.match(line)
        if header:
            close()
            deck, fields, counts = header.group(1).strip(), {}, {}
            continue
        if deck is None:
            continue
        named = field_pattern.match(line)
        if named:
            name = named.group(1).upper()
            counts[name] = counts.get(name, 0) + 1
            fields[name] = named.group(2).strip()
    close()
    return tuple(records)


def _rendered_records(text: str) -> tuple[RenderedRecord, ...]:
    return _read_records(text, RENDERED_HEADER, RENDERED_FIELD)


def _rendered_grade(
    source: Source, submission: str | None
) -> RenderedAssessment:
    records = _rendered_records(source.rendered_text or "")
    passes = render_pass.read_passes(source.root / "render")
    found: list[Finding] = []

    if source.rendered_text is not None and not records:
        found.append(Finding(RENDERED_RECORD, None, "rendered.md has no RENDERED record"))
    required = ("PASS", "SLIDES", "SOURCE", "UNSEEN", "READ", "VERDICT")
    parsed_passes: list[int | None] = []
    parsed_slides: list[tuple[int, int] | None] = []
    for record in records:
        invalid: list[str] = []
        if not record.deck.casefold().endswith(".pptx"):
            invalid.append("header does not name a .pptx")
        for name in required:
            if record.counts.get(name, 0) != 1 or not record.value(name):
                invalid.append(f"{name} must appear once with a value")
        pass_value = record.value("PASS")
        pass_number = int(pass_value) if POSITIVE_INTEGER.fullmatch(pass_value) else None
        parsed_passes.append(pass_number)
        if pass_number is None:
            invalid.append("PASS is not a positive integer")
        slides_match = SLIDES_READ.fullmatch(record.value("SLIDES"))
        parsed_slides.append(
            (int(slides_match.group(1)), int(slides_match.group(2))) if slides_match else None
        )
        if slides_match is None:
            invalid.append("SLIDES is not n of m read")
        if record.value("SOURCE").casefold() not in {"powerpoint-pdf", "clinician"}:
            invalid.append("SOURCE is not powerpoint-pdf or clinician")
        verdict = record.value("VERDICT")
        if verdict.casefold().startswith("clean") and not re.fullmatch(
            r"(?is)clean[ \t]+-[ \t]+.+", verdict
        ):
            invalid.append("a clean VERDICT needs a reason after clean -")
        if invalid:
            found.append(Finding(RENDERED_RECORD, None, "; ".join(invalid)))

    for pass_number in {number for number in parsed_passes if number is not None}:
        if parsed_passes.count(pass_number) > 1:
            found.append(
                Finding(
                    RENDERED_RECORD,
                    None,
                    f"PASS {pass_number} has more than one rendered record",
                )
            )

    pass_numbers = {number for number, _path in passes}
    recorded_numbers = {number for number in parsed_passes if number is not None}
    unrecorded = len(pass_numbers - recorded_numbers)
    if not passes:
        found.append(Finding(RENDERED_RECORD, None, "deck has no retained render pass"))
    if not records:
        found.append(Finding(RENDERED_RECORD, None, "deck has no rendered record"))
    highest = passes[-1][0] if passes else None
    for record, pass_number in zip(records, parsed_passes, strict=True):
        if record.deck != source.deck.name:
            found.append(Finding(RENDERED_RECORD, None, "rendered record names another deck"))
        if pass_number is not None and pass_number not in pass_numbers:
            found.append(Finding(RENDERED_RECORD, None, "rendered record names no retained pass"))
    highest_indexes = [index for index, number in enumerate(parsed_passes) if number == highest]
    if highest is not None and not highest_indexes:
        found.append(Finding(RENDERED_RECORD, None, "no rendered record names the highest retained pass"))
    elif highest_indexes:
        index = highest_indexes[-1]
        counts = parsed_slides[index]
        retained = passes[-1][1]
        png_count = sum(1 for path in retained.glob("*.png") if path.is_file())
        slide_count = len(source.slides)
        if counts is None or counts != (png_count, slide_count) or png_count != slide_count:
            found.append(
                Finding(RENDERED_RECORD, None, "highest-pass slide and PNG counts do not match the deck")
            )
        record = records[index]
        if record.value("UNSEEN").casefold() != "none":
            found.append(Finding(RENDERED_RECORD, None, "highest-pass UNSEEN is not none"))
        if not re.fullmatch(r"(?is)clean[ \t]+-[ \t]+.+", record.value("VERDICT")):
            found.append(Finding(RENDERED_RECORD, None, "highest-pass VERDICT is not clean with a reason"))
    if passes:
        fingerprint = passes[-1][1] / "deck.sha256"
        retained_digest = file_digest.recorded_sha256(fingerprint)
        if retained_digest != file_digest.sha256(source.deck):
            found.append(
                Finding(
                    RENDERED_RECORD,
                    None,
                    "highest retained pass has no matching deck fingerprint; re-render into a new pass",
                )
            )
    report = f"rendered record: {'finding' if found else 'clean'}"
    return RenderedAssessment(
        tuple(found), len(records), len(passes), unrecorded, report
    )


def _adversarial_findings(source: Source) -> tuple[Finding, ...]:
    records = _read_records(source.adversarial_text or "", ADVERSARIAL_HEADER, ADVERSARIAL_FIELD)
    passes = render_pass.read_passes(source.root / "render")
    found: list[Finding] = []
    if not records:
        return (Finding(ADVERSARIAL_RECORD, None, "adversarial.md has no ADVERSARIAL record"),)

    parsed_passes: list[int | None] = []
    parsed_slides: list[tuple[int, int] | None] = []
    for record in records:
        invalid: list[str] = []
        if not record.deck.casefold().endswith(".pptx"):
            invalid.append("header does not name a .pptx")
        for name in ("PASS", "SLIDES", "UNSEEN", "CLAIMS", "VERDICT"):
            if record.counts.get(name, 0) != 1 or not record.value(name):
                invalid.append(f"{name} must appear once with a value")
        pass_value = record.value("PASS")
        pass_number = int(pass_value) if POSITIVE_INTEGER.fullmatch(pass_value) else None
        parsed_passes.append(pass_number)
        if pass_number is None:
            invalid.append("PASS is not a positive integer")
        slides_match = SLIDES_READ.fullmatch(record.value("SLIDES"))
        parsed_slides.append(
            (int(slides_match.group(1)), int(slides_match.group(2))) if slides_match else None
        )
        if slides_match is None:
            invalid.append("SLIDES is not n of m read")
        if not re.fullmatch(r"[0-9a-f]{64}", record.value("CLAIMS"), re.ASCII):
            invalid.append("CLAIMS is not a SHA-256 digest")
        verdict = record.value("VERDICT")
        if not re.fullmatch(r"(?is)(?:clean|defect)[ \t]+-[ \t]+.+", verdict):
            invalid.append("VERDICT needs clean or defect with a reason")
        if invalid:
            found.append(Finding(ADVERSARIAL_RECORD, None, "; ".join(invalid)))
        if record.deck != source.deck.name:
            found.append(Finding(ADVERSARIAL_RECORD, None, "adversarial record names another deck"))
        if pass_number is not None and pass_number not in {number for number, _ in passes}:
            found.append(Finding(ADVERSARIAL_RECORD, None, "adversarial record names no retained pass"))

    highest = passes[-1][0] if passes else None
    if highest is None or highest not in parsed_passes:
        found.append(Finding(ADVERSARIAL_RECORD, None, "no adversarial record names the highest retained pass"))
    elif parsed_passes[-1] != highest:
        found.append(Finding(ADVERSARIAL_RECORD, None, "latest adversarial record does not name the highest retained pass"))
    else:
        record = records[-1]
        png_count = sum(1 for path in passes[-1][1].glob("*.png") if path.is_file())
        slide_count = len(source.slides)
        if parsed_slides[-1] != (png_count, slide_count) or png_count != slide_count:
            found.append(Finding(ADVERSARIAL_RECORD, None, "highest-pass slide and PNG counts do not match the deck"))
        if record.value("UNSEEN").casefold() != "none":
            found.append(Finding(ADVERSARIAL_RECORD, None, "highest-pass UNSEEN is not none"))
        if not re.fullmatch(r"(?is)clean[ \t]+-[ \t]+.+", record.value("VERDICT")):
            found.append(Finding(ADVERSARIAL_RECORD, None, "latest VERDICT is not clean with a reason"))
        if record.value("CLAIMS") != file_digest.sha256(source.root / "claims.md"):
            found.append(Finding(ADVERSARIAL_RECORD, None, "CLAIMS does not match current claims.md"))
        if file_digest.recorded_sha256(passes[-1][1] / "deck.sha256") != file_digest.sha256(source.deck):
            found.append(Finding(ADVERSARIAL_RECORD, None, "highest retained pass does not match the deck bytes"))
    return tuple(found)


def _presentation_intent_records(source: Source) -> tuple[RenderedRecord, ...]:
    return _read_records(source.intent_text or "", INTENT_HEADER, INTENT_FIELD)


def _slide_population(record: RenderedRecord, name: str) -> tuple[int, ...] | None:
    value = record.value(name)
    if value.casefold() == "none":
        return ()
    if not re.fullmatch(r"[1-9][0-9]*(?:,[ \t]*[1-9][0-9]*)*", value, re.ASCII):
        return None
    return tuple(int(item.strip()) for item in value.split(","))


def _presentation_intent_findings(source: Source) -> tuple[Finding, ...]:
    records = _presentation_intent_records(source)
    if len(records) != 1:
        return (
            Finding(
                PRESENTATION_INTENT_RECORD,
                None,
                "intent.md must contain exactly one PRESENTATION-INTENT record",
            ),
        )
    record = records[0]
    found: list[Finding] = []
    for name in INTENT_FIELDS:
        if record.counts.get(name, 0) != 1 or not record.value(name):
            found.append(
                Finding(
                    PRESENTATION_INTENT_RECORD,
                    None,
                    f"{name} must appear once with a value",
                )
            )
    if record.deck != source.deck.name:
        found.append(Finding(PRESENTATION_INTENT_RECORD, None, "intent record names another deck"))
    if record.value("DRAFT") != file_digest.sha256(source.deck):
        found.append(Finding(PRESENTATION_INTENT_RECORD, None, "intent record is stale for the deck bytes"))
    if record.value("AUDIENCE-PURPOSE") != source.bar.audience_purpose:
        found.append(Finding(PRESENTATION_INTENT_RECORD, None, "AUDIENCE-PURPOSE does not match bar.md"))
    if record.value("TALK-STYLE") != source.bar.talk_style:
        found.append(Finding(PRESENTATION_INTENT_RECORD, None, "TALK-STYLE does not match bar.md"))

    content = _slide_population(record, "CONTENT-SLIDES")
    references = _slide_population(record, "REFERENCE-SLIDES")
    if content is None or references is None:
        found.append(
            Finding(
                PRESENTATION_INTENT_RECORD,
                None,
                "slide populations must be none or comma-separated positive slide numbers",
            )
        )
    else:
        combined = content + references
        expected = tuple(slide.number for slide in source.slides)
        if len(combined) != len(set(combined)) or set(combined) != set(expected):
            found.append(
                Finding(
                    PRESENTATION_INTENT_RECORD,
                    None,
                    "content and reference populations must partition every deck slide exactly once",
                )
            )
    if record.value("INTERNAL-COMMENTARY").casefold() != "none":
        found.append(
            Finding(
                PRESENTATION_INTENT_RECORD,
                None,
                "INTERNAL-COMMENTARY must be none",
            )
        )
    if not re.fullmatch(r"(?is)follows[ \t]+-[ \t]+.+", record.value("SPOKEN-ARC")):
        found.append(
            Finding(
                PRESENTATION_INTENT_RECORD,
                None,
                "SPOKEN-ARC must be follows - with a reasoned verdict",
            )
        )
    return tuple(found)


def _figures(text: str) -> set[str]:
    return set(traceable_numeric_values(text))


def _claim_figures(text: str) -> tuple[set[str], set[str]]:
    traced: set[str] = set()
    mentioned: set[str] = set()
    for match in CLAIM_BLOCK.finditer(text):
        figures = _figures(match.group("block").splitlines()[0])
        mentioned.update(figures)
        if claim_record_can_certify_values(match.group("block")):
            traced.update(figures)
    return traced, mentioned


def survey(source: Source) -> Scan:
    heading = heading_read.scan(
        source.heading_read_text,
        (
            heading_read.Binding(
                source.deck.name,
                source.deck_bytes,
                tuple(research_ledger.read_records(source.claims)),
                project_context.recorded_digest(source.root),
            ),
        ),
    )
    findings: list[Finding] = [
        Finding(kind, None, finding.detail)
        for kind in HEADING_READ_ROWS
        for finding in heading.findings
        if finding.kind == kind
    ]
    slide_limit_denominator = len(source.slides)
    counted_slides: int | None = slide_limit_denominator
    slide_limit_matcher = "PowerPoint slide parts"
    slide_limit_unread = 0
    if source.bar.slide_limit_scope == "content":
        slide_limit_matcher = "intent.md CONTENT-SLIDES"
        intent_records = _presentation_intent_records(source)
        content_population = (
            _slide_population(intent_records[0], "CONTENT-SLIDES")
            if len(intent_records) == 1
            else None
        )
        reference_population = (
            _slide_population(intent_records[0], "REFERENCE-SLIDES")
            if len(intent_records) == 1
            else None
        )
        counted_slides = len(content_population) if content_population is not None else None
        if content_population is None or reference_population is None:
            slide_limit_unread = slide_limit_denominator
        else:
            classified = set(content_population + reference_population)
            slide_limit_unread = len(
                {slide.number for slide in source.slides} - classified
            )
    if counted_slides is not None and counted_slides > source.bar.slide_max:
        findings.append(
            Finding(
                SLIDE_COUNT,
                None,
                f"{counted_slides} {source.bar.slide_limit_scope} slides exceeds {source.bar.slide_max}",
            )
        )
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
    artifact_figures = _figures("\n".join([*(slide.text for slide in source.slides), *source.notes]))
    recorded_figures, mentioned_figures = _claim_figures(source.claims)
    for figure in sorted(artifact_figures - recorded_figures):
        detail = (
            f"{figure} appears only in a disbelieved claim record"
            if figure in mentioned_figures
            else f"{figure} has no claim record"
        )
        findings.append(Finding(UNTRACED_FIGURE, None, detail))
    return Scan(
        len(source.slides),
        source.bar.slide_limit_scope,
        counted_slides,
        slide_limit_denominator,
        slide_limit_matcher,
        slide_limit_unread,
        bullets_read,
        words_read,
        font_runs_read,
        len(artifact_figures),
        0,
        0,
        0,
        heading.records_read,
        heading.unread,
        tuple(findings),
        sum(slide.diagram_text_read for slide in source.slides),
        sum(slide.chart_text_read for slide in source.slides),
        sum(slide.unread_members for slide in source.slides),
    )


def format_report(scan: Scan, _source: str, show: bool = False) -> str:
    lines = [
        "deck scan",
        "",
        f"  slides read       {scan.slides_read}",
        f"  slide-limit scope {scan.slide_limit_scope}",
        "  slide-limit population "
        + (
            f"{scan.slide_limit_count} of {scan.slide_limit_denominator} deck slides"
            if scan.slide_limit_count is not None
            else f"NOT READ of {scan.slide_limit_denominator} deck slides"
        ),
        f"  slide-limit matcher {scan.slide_limit_matcher}",
        f"  bullets read      {scan.bullets_read}",
        f"  words read        {scan.words_read}",
        f"  font runs read    {scan.font_runs_read}",
        f"  figures           {scan.figures_read}",
        f"  diagram text read {scan.diagram_text_read}",
        f"  chart text read   {scan.chart_text_read}",
        f"  rendered records  {scan.rendered_records}",
        f"  retained passes   {scan.retained_passes}",
        f"  retained passes without a record {scan.unrecorded_passes}",
        f"  heading-read records {scan.heading_reads}",
        run_grader.format_unread_remainder(
            scan.heading_read_unread + scan.unread_members + scan.slide_limit_unread
        ),
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
    rendered = _rendered_grade(source, _parsed.value("--submission"))
    scanned = replace(
        scanned,
        rendered_records=rendered.records,
        retained_passes=rendered.passes,
        unrecorded_passes=rendered.unrecorded_passes,
        findings=scanned.findings
        + rendered.findings
        + _adversarial_findings(source)
        + _presentation_intent_findings(source)
        + _submission_fingerprint_findings(source, _parsed.value("--submission")),
    )
    aar_failed, aar_report = aar_scan.completion_gate(
        source.root, _parsed.value("--submission")
    )
    submission = _parsed.value("--submission")
    gate_failed, gate_report = (
        False,
        f"submission gates: {run_grader.NOT_GRADED} - --submission was not supplied",
    )
    if submission is not None:
        gate_failed, gate_report = assignment_submission.completion_gate(
            source.root, source.deck, submission=submission
        )
    no_slide_face_text = not any(slide.text.strip() for slide in source.slides)
    diagnostics = []
    if no_slide_face_text:
        diagnostics.append("no text run was read from any slide face")
    if scanned.unread_members:
        diagnostics.append(
            f"{scanned.unread_members} referenced diagram or chart member could not be read"
        )
    if scanned.findings:
        diagnostics.append("deck findings require review")
    grade = run_grader.Grade(
        scan=scanned,
        source=str(source.root),
        findings_failed=bool(scanned.findings) or aar_failed or gate_failed,
        coverage_failed=(
            no_slide_face_text
            or scanned.unread_members > 0
            or scanned.heading_read_unread > 0
            or scanned.slide_limit_unread > 0
        ),
        diagnostics=tuple(diagnostics),
        reports=(rendered.report, gate_report, aar_report),
    )
    grade = voice_model_identity.apply_completion_gate(
        grade, source.root, _parsed.value("--submission")
    )
    voice_text = "\n".join(
        tuple(slide.text for slide in source.slides) + source.notes
    )
    grade = voice_read.apply_completion_gate(
        grade,
        source.root,
        _parsed.value("--submission"),
        voice_read.draft_surface(
            ((source.deck, voice_text),),
            plantable_text="\n".join(source.notes),
        ),
    )
    return project_context.apply_completion_gate(
        grade, source.root, _parsed.value("--submission")
    )


GRADER = run_grader.Grader(
    usage="usage: deck_scan.py <run directory> --pptx <PowerPoint file> [--show] [--submission <key>]",
    load=load,
    grade=grade,
    format_report=format_report,
    options=(
        run_grader.Option("--pptx", takes_value=True, missing_value="--pptx needs a PowerPoint file", repeatable=False),
        run_grader.Option("--show", repeatable=False),
        run_grader.Option("--submission", takes_value=True, missing_value="--submission needs a key", repeatable=False),
    ),
)


def main(
    argv: list[str], envelope: assignment_bar.Envelope | None = None
) -> int:
    grader = (
        GRADER
        if envelope is None
        else replace(GRADER, load=lambda parsed: load(parsed, envelope))
    )
    return run_grader.run(grader, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
