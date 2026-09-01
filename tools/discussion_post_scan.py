#!/usr/bin/env python3
"""Grade one initial post against its signed mechanical bar.

The source is one ``scratch/runs/<course>-<module>-discussion/`` directory and ``--draft``
names the Markdown handoff under ``output/discussions/``. Default output is
counts only. ``--show`` includes finding detail and remains private working
material. Exit 0 means the mechanical rows pass, 1 means at least one finding,
and 2 means the run could not be completely scanned.

``--docx`` names the rendered handoff, grades its heading style, comment residue,
and page-reading record backed by retained pixels, and reports paragraph-text parity
with the Markdown. Without the option, those rows report ``not graded``; an absent
input never masquerades as a passing count.

What a clean run does not establish is ``NOT_REACHED``. The tuple is the one
reader-facing inventory of this command's limits; this docstring deliberately
copies none of its rows.
"""

from __future__ import annotations

import re
import sys
import zipfile
from collections.abc import Collection, Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from xml.etree import ElementTree

from discussion_artifact import (
    AMPLIFICATION,
    CLAIM_BLOCK,
    CLAIM_REFERENCE,
    Citation,
    LEGAL_SECTION_NUMBER,
    NUMBER,
    INVOKED,
    InvokedSource,
    PostedReading,
    RENDERED_SOURCES,
    RESTATEMENT,
    WORD,
    citation_occurrence_keys,
    invoked_source_has_substance,
    legal_reference_lacks_name,
    read_citations,
    read_invoked_sources,
    read_posted_readings,
    read_reference_section,
    reference_key,
    reference_keys,
    png_read_error,
    split_references,
    strip_discussion_markers,
)
import run_grader
import coursework_run
from case_study_scan import EvidenceDisposition
import docx_write


WORD_FLOOR = "word-floor"
REFERENCE_MINIMUM = "reference-minimum"
UNTRACED_NUMBER = "untraced-number"
UNTRACED_CITATION = "untraced-citation"
RESPENT_RECORD = "respent-record"
BOLD_HEADINGS = "bold-headings"
RENDERED_COMMENTS = "rendered-comments"
RENDERED_TEXT = "rendered-text"
RENDERED_PAGES = "rendered-pages"
LEGAL_REFERENCE_NAME = "legal-reference-name"
MISSING_POSTED_READING = "missing-posted-reading"
UNKNOWN_VERDICT = "unknown-verdict"
BARE_VERDICT = "bare-verdict"
UNLOCATED_READING = "unlocated-reading"
BORROWED_LOCATOR = "borrowed-locator"
ROWS = {
    WORD_FLOOR: "the post reaches the signed word floor",
    REFERENCE_MINIMUM: "the post reaches the signed reference minimum",
    UNTRACED_NUMBER: "every graded body number traces to claims.md",
    UNTRACED_CITATION: "every in-text citation has a claim record for its source",
    RESPENT_RECORD: "every in-text citation has its own claim record",
    BOLD_HEADINGS: "the rendered document carries no named heading style",
    RENDERED_COMMENTS: "the rendered document carries no HTML comment delimiter",
    RENDERED_PAGES: "every rendered pass has a complete page reading backed by kept pixels",
    LEGAL_REFERENCE_NAME: "every legal reference entry names its regulation",
    MISSING_POSTED_READING: "a posted initial entry has a complete posted reading",
    UNKNOWN_VERDICT: "the posted reading uses a declared verdict",
    BARE_VERDICT: "the posted reading says what it found",
    UNLOCATED_READING: "the posted reading carries its board entry id",
    BORROWED_LOCATOR: "the posted reading locator belongs to the initial post",
}
KINDS = tuple(ROWS)

GATED_ROW_SETS = {
    "docx_graded": (
        (BOLD_HEADINGS, RENDERED_COMMENTS, RENDERED_PAGES),
        ("rendered_text_mismatches",),
    ),
    "reference_boundary_graded": (
        (
            WORD_FLOOR,
            REFERENCE_MINIMUM,
            UNTRACED_NUMBER,
            UNTRACED_CITATION,
            RESPENT_RECORD,
            LEGAL_REFERENCE_NAME,
        ),
        (
            "words",
            "references",
            "numeric_claims",
            "claim_records",
            "citations",
            "invoked_sources",
            "unfilled_invoked_properties",
            "pre_496_markers",
        ),
    ),
}
ABSENT_BY_DESIGN_FIELDS = ("word_ceiling",)

DECLARED_LIMITS = (
    (
        "whether the bar transcription is complete",
        "The command can read structured values but cannot compare the quoted bar with the live topic and syllabus pages.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether the topic overrides the syllabus",
        "The command receives one signed result and cannot decide whether an observed topic statement should supersede the syllabus.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a prose bar element is satisfied",
        "A bar element such as including an ISBN has no honest general text pattern and remains an independent reading.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a reference actually supports the required proposition",
        "Counting an entry cannot establish that it supports the proposition required by the signed bar.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a claim record describes the cited sentence",
        "A source-and-year join establishes record presence but cannot decide whether the claim heading faithfully describes that sentence.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether equal numeric values always describe one fact",
        "Distinct-value tracing lets one claim record cover repeated equal values, even when two occurrences are different facts that happen to share a number.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "whether posted replies have posted readings",
        "This command grades only the initial post record; discussion_reply_scan owns every response artifact in the shared reread file.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether rendered-document rows were graded when --docx was omitted",
        "Without --docx, the command does not inspect document XML or retained page evidence, so the bold-headings, rendered-comments, rendered-pages, and rendered-text rows are not graded even when the remaining report exits cleanly.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "whether matching paragraph text proves the rendered structure is unchanged",
        "Paragraph-text parity cannot establish table structure, list markers, hyperlink destinations, header fields, or visual layout; those remain rendered-document readings.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a paragraph-text difference is a graded document defect",
        "A real rendered post measured on 2026-09-01 differed only after the shared prefix, with one fewer blank paragraph in the archive; because that false-alarm shape is not classified generally, rendered-text reports without changing exit status.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether reference-dependent rows ran after a refused reference label",
        "When the reference label is refused, the command does not grade the dependent body and reference rows; their not graded output is coverage refusal, not zero findings.",
        EvidenceDisposition.BEHAVIOR,
    ),
)
NOT_REACHED = tuple((subject, reason) for subject, reason, _ in DECLARED_LIMITS)

FIELD = re.compile(r"(?mi)^(?P<name>[A-Z][A-Z-]+)\s*:\s*(?P<value>[^\n]+?)\s*$")
REFERENCE_HEADING = re.compile(r"(?mi)^#{1,6}\s+References\s*$")
MARKDOWN_HEADING = re.compile(r"(?m)^\s*#{1,6}\s+.*$")
# This stays looser than the citation reader: over-stripping a number is cheaper
# than manufacturing a citation from ordinary prose such as ``§ 5``.
STATUTE = re.compile(
    r"(?i)(?:\b\d+\s+)?C\.\s*F\.\s*R\.\s*(?:§+|sections?\s+)?\s*"
    + LEGAL_SECTION_NUMBER
    + r"|§+\s*"
    + LEGAL_SECTION_NUMBER
)
RENDERED_BLOCK = re.compile(
    r"(?ms)^## RENDERED:\s*(?P<artifact>[^\n]+?)\s*$"
    r"(?P<body>.*?)(?=^##\s|\Z)"
)
RENDERED_PAGES_VALUE = re.compile(r"^(?P<seen>\d+) of (?P<expected>\d+) imaged$")
RENDERED_FIELDS = ("PAGES", "SOURCE", "UNSEEN", "READ", "VERDICT")
PAGE_LOCATOR = re.compile(
    r"(?i)\b(?:p{1,2}\.|pages?)\s*\d+(?:\s*[-–]\s*\d+)?"
)


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    artifact: str
    detail: str


@dataclass(frozen=True)
class Bar:
    word_floor: int
    word_ceiling: int | None
    reference_minimum: int


@dataclass(frozen=True)
class RenderPass:
    pixels: tuple[Path, ...]
    exports: tuple[Path, ...]


@dataclass(frozen=True)
class RunSource:
    path: Path
    draft: Path
    body: str
    references: tuple[str, ...]
    claims: str
    bar: Bar
    docx: Path | None
    named_heading_styles: tuple[str, ...]
    rendered_comment_paragraphs: int
    rendered_paragraph_texts: tuple[str, ...]
    expected_paragraph_texts: tuple[str, ...]
    rendered_readings: tuple[RenderedReading, ...]
    render_passes: tuple[RenderPass, ...]
    refused_label: str | None
    post_url: str | None
    post_posted: str | None
    readings: tuple[PostedReading, ...]


@dataclass(frozen=True)
class ClaimRecord:
    numbers: frozenset[str]
    references: frozenset[tuple[str, str]]


@dataclass(frozen=True)
class RenderedReading:
    artifact: str
    pages_seen: int | None
    pages_expected: int | None
    source: str | None
    unseen: str | None
    read: str | None
    verdict: str | None
    errors: tuple[str, ...]


@dataclass(frozen=True)
class ClaimReferenceIndex(Collection[tuple[str, str]]):
    records: tuple[ClaimRecord, ...]
    keys: frozenset[tuple[str, str]]

    @classmethod
    def from_records(cls, records: tuple[ClaimRecord, ...]) -> ClaimReferenceIndex:
        return cls(
            records,
            frozenset(key for record in records for key in record.references),
        )

    def __contains__(self, key: object) -> bool:
        return key in self.keys

    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self.keys)

    def __len__(self) -> int:
        return len(self.keys)

    def matching_record_indices(
        self, citation_keys: tuple[tuple[str, str], ...]
    ) -> tuple[int, ...]:
        return tuple(
            index
            for index, record in enumerate(self.records)
            if any(key in record.references for key in citation_keys)
        )


@dataclass(frozen=True)
class Scan:
    words: int | None
    word_floor: int
    word_ceiling: int | None
    references: int | None
    reference_minimum: int
    numeric_claims: int | None
    claim_records: int | None
    citations: int | None
    invoked_sources: tuple[InvokedSource, ...] | None
    unfilled_invoked_properties: int | None
    pre_496_markers: int | None
    rendered_text_mismatches: int | None
    docx_graded: bool
    reference_boundary_graded: bool
    findings: tuple[Finding, ...] = ()


def _integer(fields: dict[str, str], name: str) -> int:
    value = fields.get(name, "")
    if not value.isdigit():
        raise run_grader.SourceError(f"bar.md needs an integer {name} field")
    return int(value)


def _read_bar(text: str) -> Bar:
    matches = tuple(FIELD.finditer(text))
    fields = {match.group("name"): match.group("value").strip() for match in matches}
    for name in ("TOPIC", "SYLLABUS", "SIGNED", "WORD-FLOOR", "WORD-CEILING", "REFERENCE-MINIMUM"):
        if sum(match.group("name") == name for match in matches) > 1:
            raise run_grader.SourceError(f"bar.md has a duplicate {name} field")
        if name not in fields:
            raise run_grader.SourceError(f"bar.md needs a {name} field")
    try:
        date.fromisoformat(fields["SIGNED"])
    except ValueError as failure:
        raise run_grader.SourceError("bar.md SIGNED must be an ISO date") from failure
    floor = _integer(fields, "WORD-FLOOR")
    minimum = _integer(fields, "REFERENCE-MINIMUM")
    ceiling_text = fields["WORD-CEILING"].casefold()
    if ceiling_text == "none":
        ceiling = None
    elif ceiling_text.isdigit():
        ceiling = int(ceiling_text)
    else:
        raise run_grader.SourceError("bar.md WORD-CEILING must be an integer or none")
    if ceiling is not None and ceiling < floor:
        raise run_grader.SourceError("bar.md WORD-CEILING cannot be below WORD-FLOOR")
    return Bar(floor, ceiling, minimum)


def _countable_body(body: str) -> str:
    return MARKDOWN_HEADING.sub("", strip_discussion_markers(body))


def _numeric_values(
    body: str, citations: tuple[Citation, ...] | None = None
) -> tuple[str, ...]:
    cleaned = body
    citations = read_citations(body) if citations is None else citations
    for citation in reversed(citations):
        cleaned = cleaned[: citation.start] + cleaned[citation.end :]
    cleaned = PAGE_LOCATOR.sub("", cleaned)
    cleaned = STATUTE.sub("", cleaned)
    return tuple(NUMBER.findall(strip_discussion_markers(cleaned)))


def _claim_blocks(claims: str) -> tuple[str, ...]:
    return tuple(match.group("block") for match in CLAIM_BLOCK.finditer(claims))


def _citation_keys(
    body: str, reference_key_set: ClaimReferenceIndex
) -> tuple[tuple[Citation, ...], tuple[tuple[tuple[str, str], ...], ...]]:
    body_citations = read_citations(body, reference_key_set)
    return body_citations, citation_occurrence_keys(body_citations)


def _claim_records(claims: str) -> tuple[ClaimRecord, ...]:
    records: list[ClaimRecord] = []
    for block in _claim_blocks(claims):
        lines = block.splitlines()
        heading = lines[0] if lines else ""
        restatement = RESTATEMENT.search(block)
        trace_text = heading + "\n" + (
            restatement.group("value") if restatement else ""
        )
        reference = CLAIM_REFERENCE.search(block)
        keys = (
            reference_keys(reference.group("value").replace("\n", " "))
            if reference is not None
            else ()
        )
        records.append(
            ClaimRecord(
                numbers=frozenset(
                    value.casefold() for value in NUMBER.findall(trace_text)
                ),
                references=frozenset(keys),
            )
        )
    return tuple(records)


def _maximum_record_assignment(
    candidates: tuple[tuple[int, ...], ...],
) -> dict[int, int]:
    record_to_requirement: dict[int, int] = {}

    def assign(requirement: int, seen: set[int]) -> bool:
        for record in candidates[requirement]:
            if record in seen:
                continue
            seen.add(record)
            previous = record_to_requirement.get(record)
            if previous is None or assign(previous, seen):
                record_to_requirement[record] = requirement
                return True
        return False

    for requirement in range(len(candidates)):
        assign(requirement, set())
    return record_to_requirement


def _citation_deficiency(
    candidates: tuple[tuple[int, ...], ...],
) -> tuple[frozenset[int], frozenset[int]] | None:
    record_to_requirement = _maximum_record_assignment(candidates)
    requirement_to_record = {
        requirement: record for record, requirement in record_to_requirement.items()
    }
    unmatched = set(range(len(candidates))) - set(requirement_to_record)
    if not unmatched:
        return None
    reached_requirements = set(unmatched)
    reached_records: set[int] = set()
    pending = list(unmatched)
    while pending:
        requirement = pending.pop()
        for record in candidates[requirement]:
            if requirement_to_record.get(requirement) == record:
                continue
            if record in reached_records:
                continue
            reached_records.add(record)
            matched_requirement = record_to_requirement.get(record)
            if (
                matched_requirement is not None
                and matched_requirement not in reached_requirements
            ):
                reached_requirements.add(matched_requirement)
                pending.append(matched_requirement)
    return frozenset(reached_requirements), frozenset(reached_records)


def _citation_label(citation: Citation) -> str:
    return (
        f"{citation.author.strip()} ({citation.year})"
        if citation.year
        else citation.author.strip()
    )


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEADING_STYLE = re.compile(r"Heading\d+")


def _paragraph_texts(document: ElementTree.Element) -> tuple[str, ...]:
    return tuple(
        "".join(node.text or "" for node in paragraph.iter(W + "t"))
        for paragraph in document.iter(W + "p")
    )


def _expected_paragraph_texts(markdown: str) -> tuple[str, ...]:
    """Paragraph text from the renderer's own ``blocks`` path, not a second parser."""
    return _paragraph_texts(ElementTree.fromstring(docx_write.document_xml(markdown)))


def _docx_properties(path: Path) -> tuple[tuple[str, ...], int, tuple[str, ...]]:
    if not path.is_file():
        raise run_grader.SourceError(f"no rendered document at {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            document = ElementTree.fromstring(archive.read("word/document.xml"))
    except (OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as failure:
        raise run_grader.SourceError(
            f"could not read the rendered document: {failure}"
        ) from failure
    heading_styles = tuple(
        value
        for node in document.iter(W + "pStyle")
        if (value := node.get(W + "val")) is not None
        and HEADING_STYLE.fullmatch(value)
    )
    comment_paragraphs = sum(
        "<!--" in text or "-->" in text
        for paragraph in document.iter(W + "p")
        if (text := "".join(node.text or "" for node in paragraph.iter(W + "t")))
    )
    return heading_styles, comment_paragraphs, _paragraph_texts(document)


def _rendered_readings(text: str) -> tuple[RenderedReading, ...]:
    readings: list[RenderedReading] = []
    for block in RENDERED_BLOCK.finditer(text):
        matches = tuple(FIELD.finditer(block.group("body")))
        fields = {match.group("name"): match.group("value").strip() for match in matches}
        errors: list[str] = []
        if FIELD.sub("", block.group("body")).strip():
            errors.append("unrecognized record content")
        unknown_fields = sorted({match.group("name") for match in matches} - set(RENDERED_FIELDS))
        if unknown_fields:
            errors.append("unrecognized field(s): " + ", ".join(unknown_fields))
        for name in RENDERED_FIELDS:
            count = sum(match.group("name") == name for match in matches)
            if count == 0:
                errors.append(f"missing {name}")
            elif count > 1:
                errors.append(f"duplicate {name}")
        page_match = RENDERED_PAGES_VALUE.fullmatch(fields.get("PAGES", ""))
        if "PAGES" in fields and page_match is None:
            errors.append("PAGES must say '<seen> of <expected> imaged'")
        source = fields.get("SOURCE")
        if source is not None and source not in RENDERED_SOURCES:
            errors.append("unrecognized SOURCE")
        read = fields.get("READ")
        if read is not None:
            try:
                date.fromisoformat(read)
            except ValueError:
                errors.append("READ is not an ISO date")
        verdict = fields.get("VERDICT")
        if verdict is not None and not re.search(r"\S+\s+-\s+\S+", verdict):
            errors.append("VERDICT needs a keyword and substantive reading")
        readings.append(
            RenderedReading(
                artifact=block.group("artifact").strip(),
                pages_seen=int(page_match.group("seen")) if page_match else None,
                pages_expected=int(page_match.group("expected")) if page_match else None,
                source=source,
                unseen=fields.get("UNSEEN"),
                read=read,
                verdict=verdict,
                errors=tuple(errors),
            )
        )
    return tuple(readings)


def _render_passes(root: Path) -> tuple[RenderPass, ...]:
    render = root / "render"
    if not render.is_dir():
        return ()
    numbered: list[tuple[int, RenderPass]] = []
    for child in render.iterdir():
        match = re.fullmatch(r"pass-(\d+)", child.name)
        if child.is_dir() and match:
            pixels = tuple(
                sorted(
                    child.glob("*.png"),
                    key=lambda path: (
                        int(page.group(1))
                        if (page := re.fullmatch(r"page-(\d+)\.png", path.name))
                        else sys.maxsize,
                        path.name,
                    ),
                )
            )
            exports = tuple(
                path
                for path in (child / "post.pdf", child / "post.xps")
                if path.is_file()
            )
            numbered.append((int(match.group(1)), RenderPass(pixels, exports)))
    if not numbered:
        return ()
    numbered.sort()
    if [number for number, _ in numbered] != list(range(1, len(numbered) + 1)):
        return tuple(render_pass for _, render_pass in numbered) + (RenderPass((), ()),)
    return tuple(render_pass for _, render_pass in numbered)


def load(parsed: run_grader.Parsed) -> RunSource:
    root = Path(parsed.source)
    if not root.is_dir():
        raise run_grader.SourceError(f"no run directory at {root}")
    bar_path = root / "bar.md"
    claims_path = root / "claims.md"
    post_path = root / "post.md"
    reread_path = root / "reread.md"
    draft_value = parsed.value("--draft")
    if draft_value is None:
        raise run_grader.SourceError("--draft needs a Markdown file")
    draft = Path(draft_value)
    docx_value = parsed.value("--docx")
    docx = Path(docx_value) if docx_value is not None else None
    if not bar_path.is_file() or not claims_path.is_file():
        raise run_grader.SourceError("run needs bar.md and claims.md before it can be scanned")
    if not draft.is_file():
        raise run_grader.SourceError(f"no draft Markdown at {draft}")
    if coursework_run.is_submission(draft):
        expected = coursework_run.run_for_submission(draft)
        if (
            coursework_run.is_run_directory(root)
            and not coursework_run.submission_belongs_to_run(draft, root)
        ):
            raise run_grader.SourceError(
                f"submission {draft.name} does not belong to run directory {root.name}"
            )
        if not expected.is_dir():
            raise run_grader.SourceError(
                f"no run directory at {expected} for submission {draft.name}"
            )
        if root.resolve() != expected.resolve():
            raise run_grader.SourceError(
                f"submission {draft.name} does not belong to run directory {root.name}"
            )
    try:
        bar = _read_bar(bar_path.read_text(encoding="utf-8"))
        claims = claims_path.read_text(encoding="utf-8")
        draft_text = draft.read_text(encoding="utf-8")
        section = read_reference_section(draft_text, REFERENCE_HEADING)
        post_fields = (
            {
                match.group("name"): match.group("value").strip()
                for match in FIELD.finditer(post_path.read_text(encoding="utf-8"))
            }
            if post_path.is_file()
            else {}
        )
        readings = (
            read_posted_readings(reread_path.read_text(encoding="utf-8"))
            if reread_path.is_file()
            else ()
        )
        post_text = post_path.read_text(encoding="utf-8") if post_path.is_file() else ""
    except (OSError, UnicodeError, ValueError) as failure:
        raise run_grader.SourceError(f"could not read the discussion-post run: {failure}") from failure
    named_heading_styles, rendered_comment_paragraphs, rendered_paragraph_texts = (
        _docx_properties(docx) if docx is not None else ((), 0, ())
    )
    return RunSource(
        root,
        draft,
        section.body,
        section.references,
        claims,
        bar,
        docx,
        named_heading_styles,
        rendered_comment_paragraphs,
        rendered_paragraph_texts,
        _expected_paragraph_texts(draft_text) if docx is not None else (),
        _rendered_readings(post_text) if docx is not None else (),
        _render_passes(root) if docx is not None else (),
        section.refused_label,
        post_fields.get("POST-URL"),
        post_fields.get("POSTED"),
        readings,
    )


def _posted_reading_findings(source: RunSource) -> tuple[Finding, ...]:
    if source.post_url is None and source.post_posted is None:
        return ()
    reading = next(
        (item for item in source.readings if item.artifact == "post.md"), None
    )
    if reading is None:
        return (
            Finding(
                MISSING_POSTED_READING,
                "post.md",
                "no REREAD record for the posted initial entry",
            ),
        )
    findings: list[Finding] = []
    missing = list(reading.missing_record_fields)
    if not source.post_url:
        missing.append("post.md POST-URL")
    if not source.post_posted:
        missing.append("post.md POSTED")
    if missing:
        findings.append(
            Finding(
                MISSING_POSTED_READING,
                "post.md",
                "missing " + ", ".join(missing),
            )
        )
    if not reading.verdict_is_known:
        findings.append(
            Finding(UNKNOWN_VERDICT, "post.md", "verdict is outside the vocabulary")
        )
    elif not reading.verdict_has_substance:
        findings.append(
            Finding(BARE_VERDICT, "post.md", "verdict carries no reading substance")
        )
    if reading.entry_id is None:
        findings.append(
            Finding(UNLOCATED_READING, "post.md", "POST-URL has no entry_id")
        )
    elif reading.post_url != source.post_url:
        findings.append(
            Finding(BORROWED_LOCATOR, "post.md", "POST-URL does not match post.md")
        )
    return tuple(findings)


def _rendered_comment_findings(source: RunSource) -> tuple[Finding, ...]:
    if not source.rendered_comment_paragraphs:
        return ()
    assert source.docx is not None
    return tuple(
        Finding(
            RENDERED_COMMENTS,
            source.docx.name,
            "paragraph carries an HTML comment delimiter",
        )
        for _ in range(source.rendered_comment_paragraphs)
    )


def _rendered_page_findings(source: RunSource) -> tuple[Finding, ...]:
    if source.docx is None:
        return ()
    findings: list[Finding] = []
    if not source.rendered_readings:
        return (
            Finding(
                RENDERED_PAGES,
                "post.md",
                "no RENDERED record for the rendered document",
            ),
        )
    if len(source.rendered_readings) != len(source.render_passes):
        findings.append(
            Finding(
                RENDERED_PAGES,
                "render",
                "RENDERED record count does not match retained pass directories",
            )
        )
    try:
        import pymupdf
    except ImportError:
        pymupdf = None
    for index, reading in enumerate(source.rendered_readings, start=1):
        detail: list[str] = list(reading.errors)
        is_last = index == len(source.rendered_readings)
        render_pass = (
            source.render_passes[index - 1]
            if index <= len(source.render_passes)
            else RenderPass((), ())
        )
        pixels = render_pass.pixels
        if reading.artifact != "post.md":
            detail.append("record artifact is not post.md")
        if reading.pages_seen is not None and reading.pages_seen < 1:
            detail.append("PAGES imaged count must be positive")
        if reading.pages_expected is not None and reading.pages_expected < 1:
            detail.append("PAGES expected count must be positive")
        if reading.pages_seen is not None and len(pixels) != reading.pages_seen:
            detail.append(
                f"pass-{index} keeps {len(pixels)} page image(s), not {reading.pages_seen}"
            )
        expected_names = [f"page-{number}.png" for number in range(1, len(pixels) + 1)]
        if [pixel.name for pixel in pixels] != expected_names:
            detail.append(f"pass-{index} page image names are not consecutive from page-1.png")
        if pymupdf is None and pixels:
            detail.append("PyMuPDF is unavailable, so retained page pixels were not decoded")
        elif pymupdf is not None:
            for pixel in pixels:
                if failure := png_read_error(pymupdf, pixel):
                    detail.append(f"{pixel.name} {failure}")
        if len(render_pass.exports) != 1:
            detail.append(
                f"pass-{index} keeps {len(render_pass.exports)} page-faithful export(s), not 1"
            )
        elif pymupdf is None:
            detail.append("PyMuPDF is unavailable, so the retained export page count was not read")
        else:
            export = render_pass.exports[0]
            try:
                with pymupdf.open(str(export)) as document:
                    export_pages = len(document)
            except Exception as failure:
                detail.append(f"{export.name} is not a readable retained export: {failure}")
            else:
                if export_pages < 1:
                    detail.append(f"{export.name} contains no pages")
                if is_last and len(pixels) != export_pages:
                    detail.append(
                        f"pass-{index} keeps {len(pixels)} page image(s) for "
                        f"{export_pages} exported page(s)"
                    )
                if (
                    reading.pages_expected is not None
                    and reading.pages_expected != export_pages
                ):
                    detail.append(
                        f"PAGES expected count is {reading.pages_expected}, not the "
                        f"retained export's {export_pages}"
                    )
                expected_suffix = {
                    "word-pdf": ".pdf",
                    "word-xps": ".xps",
                }.get(reading.source)
                if expected_suffix is not None and export.suffix.lower() != expected_suffix:
                    detail.append(
                        f"SOURCE {reading.source} does not match retained {export.suffix.lower()} export"
                    )
        if (
            is_last
            and reading.pages_seen is not None
            and reading.pages_expected is not None
            and reading.pages_seen != reading.pages_expected
        ):
            detail.append("not every expected page was imaged")
        if (
            is_last
            and reading.unseen is not None
            and reading.unseen.casefold() != "none"
        ):
            detail.append("UNSEEN names an unchecked page")
        if detail:
            findings.append(
                Finding(RENDERED_PAGES, f"pass-{index}", "; ".join(detail))
            )
    last = source.rendered_readings[-1]
    if last.verdict is not None and not last.verdict.casefold().startswith("clean -"):
        findings.append(
            Finding(RENDERED_PAGES, "post.md", "the last rendered verdict is not clean")
        )
    return tuple(findings)


def survey(source: RunSource) -> Scan:
    if source.refused_label is not None:
        findings = (
            (
                Finding(
                    BOLD_HEADINGS,
                    source.docx.name,
                    "named heading styles: " + ", ".join(source.named_heading_styles),
                ),
            )
            if source.named_heading_styles
            else ()
        ) + _rendered_comment_findings(source) + _rendered_page_findings(source)
        return Scan(
            words=None,
            word_floor=source.bar.word_floor,
            word_ceiling=source.bar.word_ceiling,
            references=None,
            reference_minimum=source.bar.reference_minimum,
            numeric_claims=None,
            claim_records=None,
            citations=None,
            invoked_sources=None,
            unfilled_invoked_properties=None,
            pre_496_markers=None,
            rendered_text_mismatches=(
                int(source.rendered_paragraph_texts != source.expected_paragraph_texts)
                if source.docx is not None
                else None
            ),
            docx_graded=source.docx is not None,
            reference_boundary_graded=False,
            findings=findings + _posted_reading_findings(source),
        )
    words = len(WORD.findall(_countable_body(source.body)))
    records = _claim_records(source.claims)
    reference_key_set = ClaimReferenceIndex.from_records(records)
    body_citations, citations = _citation_keys(source.body, reference_key_set)
    numbers = _numeric_values(source.body, body_citations)
    findings: list[Finding] = list(_posted_reading_findings(source))
    for block in _claim_blocks(source.claims):
        reference = CLAIM_REFERENCE.search(block)
        if reference is not None and legal_reference_lacks_name(
            reference.group("value").replace("\n", " ")
        ):
            findings.append(
                Finding(
                    LEGAL_REFERENCE_NAME,
                    "claims.md",
                    "legal claim record has a section but no regulation name",
                )
            )
    if words < source.bar.word_floor:
        findings.append(Finding(WORD_FLOOR, source.draft.name, f"{words} words"))
    if len(source.references) < source.bar.reference_minimum:
        findings.append(
            Finding(
                REFERENCE_MINIMUM,
                source.draft.name,
                f"{len(source.references)} references",
            )
        )
    if source.named_heading_styles:
        findings.append(
            Finding(
                BOLD_HEADINGS,
                source.docx.name,
                "named heading styles: " + ", ".join(source.named_heading_styles),
            )
        )
    findings.extend(_rendered_comment_findings(source))
    findings.extend(_rendered_page_findings(source))
    traced_numbers = frozenset(
        value for record in records for value in record.numbers
    )
    distinct_numbers = tuple(dict.fromkeys(value.casefold() for value in numbers))
    for value in distinct_numbers:
        if value not in traced_numbers:
            findings.append(
                Finding(
                    UNTRACED_NUMBER,
                    source.draft.name,
                    f"{value} is absent from claims.md",
                )
            )
    citation_requirements: list[tuple[Citation, tuple[int, ...]]] = []
    for occurrence, (citation, keys) in enumerate(
        zip(body_citations, citations, strict=True), start=1
    ):
        candidates = reference_key_set.matching_record_indices(keys)
        if not candidates:
            findings.append(
                Finding(
                    UNTRACED_CITATION,
                    source.draft.name,
                    f"citation occurrence {occurrence} has no source-matched claim record",
                )
            )
        else:
            citation_requirements.append((citation, candidates))
    deficiency = _citation_deficiency(
        tuple(candidates for _, candidates in citation_requirements)
    )
    if deficiency is not None:
        reached_requirements, reached_records = deficiency
        citation_count = len(reached_requirements)
        record_count = len(reached_records)
        shortfall = citation_count - record_count
        labels = tuple(
            dict.fromkeys(
                _citation_label(citation_requirements[index][0])
                for index in sorted(reached_requirements)
            )
        )
        subject = labels[0] if len(labels) == 1 else ", ".join(labels)
        findings.append(
            Finding(
                RESPENT_RECORD,
                source.draft.name,
                f"{citation_count} citations of {subject} share {record_count} "
                f"claim record{'s' if record_count != 1 else ''} — "
                f"{shortfall} short",
            )
        )
    return Scan(
        words=words,
        word_floor=source.bar.word_floor,
        word_ceiling=source.bar.word_ceiling,
        references=len(source.references),
        reference_minimum=source.bar.reference_minimum,
        numeric_claims=len(distinct_numbers),
        claim_records=len(records),
        citations=len(citations),
        invoked_sources=read_invoked_sources(source.body),
        unfilled_invoked_properties=sum(
            not invoked_source_has_substance(invoked_source)
            for invoked_source in read_invoked_sources(source.body)
        ),
        pre_496_markers=len(AMPLIFICATION.findall(source.body)),
        rendered_text_mismatches=(
            int(source.rendered_paragraph_texts != source.expected_paragraph_texts)
            if source.docx is not None
            else None
        ),
        docx_graded=source.docx is not None,
        reference_boundary_graded=True,
        findings=tuple(findings),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    exceeded = (
        scan.reference_boundary_graded
        and scan.word_ceiling is not None
        and scan.words is not None
        and scan.words > scan.word_ceiling
    )
    lines = [
        f"initial post in {source}",
        (
            f"words: {scan.words} (floor {scan.word_floor})"
            if scan.reference_boundary_graded
            else "words: not graded"
        ),
        f"word ceiling: {scan.word_ceiling if scan.word_ceiling is not None else 'none'}",
        (
            f"word ceiling exceeded: {'yes' if exceeded else 'no'} (counted, never graded)"
            if scan.reference_boundary_graded
            else "word ceiling exceeded: not graded"
        ),
        (
            f"references: {scan.references} (minimum {scan.reference_minimum})"
            if scan.reference_boundary_graded
            else "references: not graded"
        ),
        f"numeric claims: {scan.numeric_claims if scan.reference_boundary_graded else 'not graded'}",
        f"claim records: {scan.claim_records if scan.reference_boundary_graded else 'not graded'}",
        f"citations: {scan.citations if scan.reference_boundary_graded else 'not graded'}",
        (
            f"invoked sources: {len(scan.invoked_sources or ())}"
            if scan.reference_boundary_graded
            else "invoked sources: not graded"
        ),
        (
            "unfilled invoked properties: "
            f"{scan.unfilled_invoked_properties} (counted, not graded)"
            if scan.reference_boundary_graded
            else "unfilled invoked properties: not graded"
        ),
        (
            f"pre-#496 markers: {scan.pre_496_markers} (counted, not graded)"
            if scan.reference_boundary_graded
            else "pre-#496 markers: not graded"
        ),
        (
            f"{RENDERED_TEXT}: {scan.rendered_text_mismatches} (reported, not graded)"
            if scan.docx_graded
            else f"{RENDERED_TEXT}: not graded"
        ),
        f"findings: {len(scan.findings)}",
    ]
    for kind in ROWS:
        if kind not in {
            BOLD_HEADINGS,
            RENDERED_COMMENTS,
            RENDERED_PAGES,
            MISSING_POSTED_READING,
            UNKNOWN_VERDICT,
            BARE_VERDICT,
            UNLOCATED_READING,
            BORROWED_LOCATOR,
        } and not scan.reference_boundary_graded:
            lines.append(f"{kind}: not graded")
        elif kind in {BOLD_HEADINGS, RENDERED_COMMENTS, RENDERED_PAGES} and not scan.docx_graded:
            lines.append(f"{kind}: not graded")
        else:
            lines.append(
                f"{kind}: {sum(finding.kind == kind for finding in scan.findings)}"
            )
    if show:
        lines.extend(
            f"invoked source: {invoked_source.domain} | {invoked_source.property}"
            for invoked_source in scan.invoked_sources or ()
        )
        lines.extend(
            f"{finding.kind}: {finding.artifact}: {finding.detail}"
            for finding in scan.findings
        )
    return "\n".join(lines)


def grade(source: RunSource, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scanned = survey(source)
    rendered_page_failed = any(
        finding.kind == RENDERED_PAGES for finding in scanned.findings
    )
    return run_grader.Grade(
        scan=scanned,
        source=str(source.path),
        findings_failed=bool(scanned.findings)
        and (scanned.reference_boundary_graded or rendered_page_failed),
        coverage_failed=not scanned.reference_boundary_graded,
        diagnostics=(
            (f"refused reference label in {source.draft.name}: {source.refused_label}",)
            if source.refused_label is not None
            else ()
        ),
    )


GRADER = run_grader.Grader(
    usage=(
        "usage: discussion_post_scan.py <run directory> --draft <Markdown file> "
        "[--docx <Word file>] [--show]"
    ),
    load=load,
    grade=grade,
    format_report=format_report,
    options=(
        run_grader.Option("--draft", takes_value=True, missing_value="--draft needs a Markdown file", repeatable=False),
        run_grader.Option("--docx", takes_value=True, missing_value="--docx needs a Word file", repeatable=False),
        run_grader.Option("--show", repeatable=False),
    ),
    allow_extra_positionals=False,
)


def main(argv: list[str]) -> int:
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
