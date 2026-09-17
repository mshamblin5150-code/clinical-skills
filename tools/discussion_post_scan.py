#!/usr/bin/env python3
"""Grade one initial post against its signed mechanical bar.

The source is one ``scratch/runs/<course>-<module>-discussion/`` directory and ``--draft``
names the Markdown handoff under ``output/discussions/``. Default output is
counts only. ``--show`` includes finding detail and remains private working
material. Exit 0 means the mechanical rows pass, 1 means at least one finding,
and 2 means the run could not be completely scanned.

``--html`` names the full Canvas body. An inline outcome grades its bold headings,
comments, paragraph text, and retained box reading. An attachment outcome instead
grades the final Word page reading and the copy downloaded from the posted entry.
``--docx`` names the Word render; its paragraph-text parity is reported on either
route. Without the relevant input, artifact-specific rows cannot pass.

What a clean run does not establish is ``NOT_REACHED``. The tuple is the one
reader-facing inventory of this command's limits; this docstring deliberately
copies none of its rows.
"""

from __future__ import annotations

import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

from discussion_artifact import (
    AMPLIFICATION,
    CLAIM_BLOCK,
    CLAIM_REFERENCE,
    CITATION_RESOLUTION_NOT_REACHED,
    Citation,
    CitationCoverage,
    LEGAL_SECTION_NUMBER,
    LEGAL_READER_MECHANISMS,
    LEGAL_SOURCE,
    NUMBER,
    INVOKED,
    InvokedSource,
    PostedReading,
    ReferenceKeySet,
    RENDERED_SOURCES,
    RESTATEMENT,
    WORD,
    citation_occurrence_keys,
    citation_coverage,
    claim_record_can_certify_values,
    invoked_source_has_substance,
    legal_reference_lacks_name,
    read_citations,
    read_invoked_sources,
    read_posted_readings,
    read_reference_section,
    reference_key,
    split_references,
    strip_discussion_markers,
)
import run_grader
import render_pass
import page_image
import pdf_engine
from run_grader import NOT_GRADED
import aar_scan
import heading_read
import research_ledger

EXPECTED_COMPLETION_CHECKS = (aar_scan.EXPECTED_ROW,)
import coursework_run
from run_grader import EvidenceDisposition
import docx_write
import file_digest
import post_html
from research_ledger import REFUTATION_EVIDENCE_COMPLEMENT


WORD_FLOOR = "word-floor"
EMPTY_BODY = "empty-body"
REFERENCE_MINIMUM = "reference-minimum"
UNTRACED_NUMBER = "untraced-number"
UNTRACED_CITATION = "untraced-citation"
MISSING_FIRST_AUTHOR_INITIALS = "missing-first-author-initials"
RESPENT_RECORD = "respent-record"
BOLD_HEADINGS = "bold-headings"
RENDERED_COMMENTS = "rendered-comments"
SUBMISSION_TEXT = "submission-text"
RENDERED_TEXT = "rendered-text"
RENDERED_PAGES = "rendered-pages"
LEGAL_REFERENCE_NAME = "legal-reference-name"
MISSING_POSTED_READING = "missing-posted-reading"
UNKNOWN_VERDICT = "unknown-verdict"
BARE_VERDICT = "bare-verdict"
UNLOCATED_READING = "unlocated-reading"
BORROWED_LOCATOR = "borrowed-locator"
SUBMISSION_FINGERPRINT = "submission-fingerprint"
POSTED_ATTACHMENT = "posted-attachment"
ROWS = {
    WORD_FLOOR: "the post reaches the signed word floor",
    EMPTY_BODY: "the post contains body text after headings are removed",
    REFERENCE_MINIMUM: "the post reaches the signed reference minimum",
    UNTRACED_NUMBER: "every graded body number traces to a believed claim record",
    UNTRACED_CITATION: "every in-text citation has a claim record for its source",
    MISSING_FIRST_AUTHOR_INITIALS: "same-surname first authors with different initials are distinguished in text",
    RESPENT_RECORD: "every in-text citation has its own claim record",
    BOLD_HEADINGS: "every submission heading is a bold paragraph",
    RENDERED_COMMENTS: "the HTML submission carries no comment delimiter",
    SUBMISSION_TEXT: "the HTML submission paragraph text matches the Markdown",
    RENDERED_PAGES: "the selected carrier has a complete visual reading backed by kept pixels",
    LEGAL_REFERENCE_NAME: "every legal reference entry names its legal source",
    MISSING_POSTED_READING: "a posted initial entry has a complete posted reading",
    UNKNOWN_VERDICT: "the posted reading uses a declared verdict",
    BARE_VERDICT: "the posted reading says what it found",
    UNLOCATED_READING: "the posted reading carries its board entry id",
    BORROWED_LOCATOR: "the posted reading locator belongs to the initial post",
    SUBMISSION_FINGERPRINT: "the posted reading is bound to the current submission files",
    POSTED_ATTACHMENT: "the posted entry carries the checked Word document's bytes",
    **{kind: "the heading read agrees with the final draft and current claim headings" for kind in heading_read.KINDS},
}
KINDS = tuple(ROWS)
HEADING_READ_ROWS = {kind: ROWS[kind] for kind in heading_read.KINDS}
POSTED_READING_ROWS = (
    MISSING_POSTED_READING,
    UNKNOWN_VERDICT,
    BARE_VERDICT,
    UNLOCATED_READING,
    BORROWED_LOCATOR,
    SUBMISSION_FINGERPRINT,
    POSTED_ATTACHMENT,
)

GATED_ROW_SETS = {
    "posted_reading_graded": (POSTED_READING_ROWS, ()),
    "html_graded": (
        (BOLD_HEADINGS, RENDERED_COMMENTS, SUBMISSION_TEXT, RENDERED_PAGES),
        (),
    ),
    "docx_graded": (
        (),
        ("rendered_text_mismatches",),
    ),
    "rendered_pages_graded": (
        (RENDERED_PAGES,),
        (),
    ),
    "reference_boundary_graded": (
        (
            WORD_FLOOR,
            EMPTY_BODY,
            REFERENCE_MINIMUM,
            UNTRACED_NUMBER,
            UNTRACED_CITATION,
            MISSING_FIRST_AUTHOR_INITIALS,
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
PARTIAL_GATES = ("rendered_pages_graded",)
ABSENT_BY_DESIGN_FIELDS = ("word_ceiling",)

UNJOINED_SOURCE_FIELDS = ", ".join(REFUTATION_EVIDENCE_COMPLEMENT)
UNJOINED_SOURCE_FIELDS_LIMIT = (
    f"whether a sourced record missing one or more of {UNJOINED_SOURCE_FIELDS} is still believed",
    f"Field completeness for {UNJOINED_SOURCE_FIELDS} belongs to research_ledger; this certifier still reads numbers and reference keys from a record carrying both substantive refutation-evidence fields.",
    EvidenceDisposition.BEHAVIOR,
)

DECLARED_LIMITS = (
    *CITATION_RESOLUTION_NOT_REACHED,
    (
        "whether a believed record's heading and restatement support the number traced from it",
        "The certifier reads numeric tokens and never judges support. The refutation leg owns source-to-heading agreement, and the heading read owns draft-to-heading agreement.",
        EvidenceDisposition.BEHAVIOR,
    ),
    UNJOINED_SOURCE_FIELDS_LIMIT,
    (
        "the authority for render wiring",
        "The governing architecture record for this declaration is ADR 0125.",
        EvidenceDisposition.DECLARED_READING,
    ),
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
        "whether HTML-submission rows were graded when --html was omitted",
        "Without --html, the command does not inspect the submitted bytes or retained Canvas-box evidence, so bold-headings, rendered-comments, submission-text, and rendered-pages are not graded even when the remaining report exits cleanly.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "whether each reference URL was submitted as a link",
        "The submission-text row compares visible text, so a reference URL left unlinked in the submitted HTML reads the same as its anchor; whether the board shows a link remains the posted reading.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "whether archival text parity was reported when --docx was omitted",
        "Without --docx, the command does not inspect the archival Word document, so rendered-text is not graded even when the remaining report exits cleanly.",
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
    (
        "whether a platform-side repair after the recorded reading changed the comparison",
        "The fingerprint binds the record to its source file, while a later platform edit can change the posted entry without changing that file.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a run with no posting evidence was ever submitted",
        "The command cannot infer a submission from silence when neither the working record nor reread.md carries posting evidence.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether the learning platform stored the fingerprinted bytes",
        "The digest identifies a local source and generated carriers but does not prove which bytes the learning platform retained.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether the reader actually compared the artifact",
        "A valid fingerprint proves file identity and cannot establish the attention or judgment behind the recorded verdict.",
        EvidenceDisposition.DECLARED_READING,
    ),
)
NOT_REACHED = tuple((subject, reason) for subject, reason, _ in DECLARED_LIMITS)

FIELD = re.compile(r"(?mi)^(?P<name>[A-Z][A-Z-]+)\s*:\s*(?P<value>[^\n]+?)\s*$")
REFERENCE_HEADING = re.compile(r"(?mi)^#{1,6}\s+References\s*$")
MARKDOWN_HEADING = re.compile(r"(?m)^\s*#{1,6}\s+.*$")
# This stays looser than the citation reader: over-stripping a number is cheaper
# than manufacturing a citation from ordinary prose such as ``§ 5``.
STATUTE = re.compile(
    r"(?i)" + LEGAL_SOURCE + r"\s*(?:§+|sections?\s+)?\s*"
    + LEGAL_SECTION_NUMBER
    + r"|§+\s*"
    + LEGAL_SECTION_NUMBER
)
RENDERED_BLOCK = re.compile(
    r"(?ms)^## RENDERED:\s*(?P<artifact>[^\n]+?)\s*$"
    r"(?P<body>.*?)(?=^##\s|\Z)"
)
RENDERED_PAGES_VALUE = re.compile(r"^(?P<seen>\d+) of (?P<expected>\d+) imaged$")
RENDERED_BLOCKS_VALUE = re.compile(r"^(?P<seen>\d+) of (?P<expected>\d+) read$")
RENDERED_COMMON_FIELDS = ("SOURCE", "UNSEEN", "READ", "VERDICT")
RENDERED_FIELDS = ("PAGES", "BLOCKS") + RENDERED_COMMON_FIELDS
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
    draft_text: str
    body: str
    references: tuple[str, ...]
    claims: str
    draft_bytes: bytes
    heading_read_text: str
    bar: Bar
    html: Path | None
    submission_heading_failures: int
    submission_comment_count: int
    submission_text_mismatches: int | None
    submitted_blocks: int | None
    docx: Path | None
    rendered_paragraph_texts: tuple[str, ...]
    expected_paragraph_texts: tuple[str, ...]
    html_matches_rebuild: bool | None
    docx_matches_rebuild: bool | None
    rendered_readings: tuple[RenderedReading, ...]
    render_passes: tuple[tuple[int, RenderPass], ...]
    missing_pass_numbers: int
    refused_label: str | None
    post_url: str | None
    post_posted: str | None
    readings: tuple[PostedReading, ...]


@dataclass(frozen=True)
class ClaimRecord:
    numbers: frozenset[str]
    references: ReferenceKeySet
    all_numbers: frozenset[str] = frozenset()


@dataclass(frozen=True)
class RenderedReading:
    artifact: str
    units_seen: int | None
    units_expected: int | None
    measure: str | None
    source: str | None
    unseen: str | None
    read: str | None
    verdict: str | None
    errors: tuple[str, ...]


@dataclass(frozen=True)
class ClaimReferenceIndex(ReferenceKeySet):
    records: tuple[ClaimRecord, ...] = ()

    @classmethod
    def from_records(cls, records: tuple[ClaimRecord, ...]) -> ClaimReferenceIndex:
        keys = ReferenceKeySet.union(tuple(record.references for record in records))
        return cls(
            keys.keys,
            keys.prefix_keys,
            keys.first_authors,
            records,
        )

    def matching_record_indices(
        self, citation_keys: tuple[tuple[str, str], ...]
    ) -> tuple[int, ...]:
        return tuple(
            index
            for index, record in enumerate(self.records)
            if any(record.references.resolves(key) for key in citation_keys)
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
    missing_pass_numbers: int
    html_graded: bool
    render_route: str
    rendered_pages_graded: bool
    docx_graded: bool
    reference_boundary_graded: bool
    posted_reading_graded: bool
    heading_reads: int
    heading_read_unread: int
    posted_reading_unread: int
    findings: tuple[Finding, ...] = ()
    citation_coverage: CitationCoverage = CitationCoverage()


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


def traceable_numeric_values(
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
) -> tuple[
    tuple[Citation, ...],
    tuple[tuple[tuple[str, str], ...], ...],
    CitationCoverage,
]:
    body_citations = read_citations(body, reference_key_set)
    return (
        body_citations,
        citation_occurrence_keys(body_citations),
        citation_coverage(body, reference_key_set),
    )


def _claim_records(claims: str) -> tuple[ClaimRecord, ...]:
    records: list[ClaimRecord] = []
    for block in _claim_blocks(claims):
        lines = block.splitlines()
        heading = lines[0] if lines else ""
        restatement = RESTATEMENT.search(block)
        trace_text = heading + "\n" + (
            restatement.group("value") if restatement else ""
        )
        all_numbers = frozenset(
            value.casefold() for value in NUMBER.findall(trace_text)
        )
        numbers = (
            all_numbers if claim_record_can_certify_values(block) else frozenset()
        )
        reference = CLAIM_REFERENCE.search(block)
        keys = (
            ReferenceKeySet.from_references(
                (reference.group("value").replace("\n", " "),)
            )
            if reference is not None
            else ReferenceKeySet()
        )
        # Reference keys remain visible even when the record cannot certify a
        # number. Removing them would hide a narrative citation rather than
        # refusing its unsupported claim.
        records.append(
            ClaimRecord(
                numbers=numbers,
                all_numbers=all_numbers,
                references=keys,
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


@dataclass(frozen=True)
class HtmlUnit:
    tag: str
    text: str
    fully_bold: bool


class SubmissionHtmlParser(HTMLParser):
    """Read visible paragraph-shaped units and comments from the submitted HTML."""

    UNIT_TAGS = frozenset(("p", "li", "th", "td", "blockquote"))

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.units: list[HtmlUnit] = []
        self.comments = 0
        self.block_count = 0
        self._unit_tag: str | None = None
        self._text: list[str] = []
        self._depth = 0
        self._strong_depth = 0
        self._all_text_bold = True

    def handle_starttag(self, tag: str, _attrs) -> None:
        tag = tag.casefold()
        if tag in {"p", "li", "table", "hr", "blockquote"}:
            self.block_count += 1
        if self._unit_tag is None and tag in self.UNIT_TAGS:
            self._unit_tag = tag
            self._text = []
            self._depth = 1
            self._strong_depth = 0
            self._all_text_bold = True
            return
        if self._unit_tag is not None:
            self._depth += 1
            if tag == "strong":
                self._strong_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._unit_tag is None:
            return
        tag = tag.casefold()
        if tag == self._unit_tag and self._depth == 1:
            self.units.append(
                HtmlUnit(self._unit_tag, "".join(self._text), self._all_text_bold)
            )
            self._unit_tag = None
            return
        if tag == "strong" and self._strong_depth:
            self._strong_depth -= 1
        self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._unit_tag is None:
            return
        self._text.append(data)
        if data.strip() and self._strong_depth == 0:
            self._all_text_bold = False

    def handle_comment(self, _data: str) -> None:
        self.comments += 1


def _plain_inline(text: str) -> str:
    return "".join(span.text for span in docx_write.inline_spans(text))


def _expected_html_units(markdown: str) -> tuple[tuple[HtmlUnit, ...], int]:
    units: list[HtmlUnit] = []
    block_count = 0
    for block in docx_write.blocks(markdown):
        if block.kind == "blank":
            continue
        block_count += 1
        if block.kind == "separator":
            continue
        if block.kind == "heading":
            units.append(HtmlUnit("p", _plain_inline(block.text), True))
        elif block.kind == "paragraph":
            units.append(HtmlUnit("p", _plain_inline(block.text), False))
        elif block.kind == "block-quotation":
            units.append(HtmlUnit("blockquote", _plain_inline(block.text), False))
        elif block.kind in {"bullet", "numbered"}:
            units.append(HtmlUnit("li", _plain_inline(block.text), False))
        elif block.kind == "table":
            for row_index, row in enumerate(block.rows):
                tag = "th" if row_index == 0 else "td"
                units.extend(HtmlUnit(tag, _plain_inline(cell), False) for cell in row)
    return tuple(units), block_count


def _html_properties(path: Path, markdown: str) -> tuple[int, int, int, int]:
    if not path.is_file():
        raise run_grader.SourceError(f"no HTML submission at {path}")
    try:
        submitted = path.read_text(encoding="utf-8")
        parser = SubmissionHtmlParser()
        parser.feed(submitted)
        parser.close()
    except (OSError, UnicodeError) as failure:
        raise run_grader.SourceError(f"could not read the HTML submission: {failure}") from failure
    expected, expected_block_count = _expected_html_units(markdown)
    actual = tuple(parser.units)
    heading_failures = sum(
        actual[index].tag != "p" or not actual[index].fully_bold
        for index, unit in enumerate(expected)
        if unit.fully_bold and index < len(actual)
    ) + sum(unit.fully_bold for unit in expected[len(actual) :])
    text_mismatches = int(
        tuple((unit.tag, unit.text) for unit in actual)
        != tuple((unit.tag, unit.text) for unit in expected)
        or parser.block_count != expected_block_count
    )
    comment_count = len(re.findall(r"<!--.*?-->|<!--|-->", submitted, re.DOTALL))
    return heading_failures, comment_count, text_mismatches, parser.block_count


def _paragraph_texts(document: ElementTree.Element) -> tuple[str, ...]:
    return tuple(
        "".join(node.text or "" for node in paragraph.iter(W + "t"))
        for paragraph in document.iter(W + "p")
    )


def _expected_paragraph_texts(markdown: str) -> tuple[str, ...]:
    """Paragraph text from the renderer's own ``blocks`` path, not a second parser."""
    return _paragraph_texts(ElementTree.fromstring(docx_write.document_xml(markdown)))


def _docx_paragraph_texts(path: Path) -> tuple[str, ...]:
    if not path.is_file():
        raise run_grader.SourceError(f"no rendered document at {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            document = ElementTree.fromstring(archive.read("word/document.xml"))
    except (OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as failure:
        raise run_grader.SourceError(
            f"could not read the rendered document: {failure}"
        ) from failure
    return _paragraph_texts(document)


def _docx_matches_rebuild(path: Path, markdown: str) -> bool:
    expected = {
        name: value.encode("utf-8") if isinstance(value, str) else value
        for name, value in docx_write.parts(markdown).items()
    }
    try:
        with zipfile.ZipFile(path) as archive:
            actual = {name: archive.read(name) for name in archive.namelist()}
    except (OSError, KeyError, zipfile.BadZipFile) as failure:
        raise run_grader.SourceError(
            f"could not read the rendered document: {failure}"
        ) from failure
    return actual == expected


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
        for name in RENDERED_COMMON_FIELDS:
            count = sum(match.group("name") == name for match in matches)
            if count == 0:
                errors.append(f"missing {name}")
            elif count > 1:
                errors.append(f"duplicate {name}")
        measures = [name for name in ("PAGES", "BLOCKS") if name in fields]
        if len(measures) != 1:
            errors.append("record needs exactly one of PAGES or BLOCKS")
        for name in ("PAGES", "BLOCKS"):
            if sum(match.group("name") == name for match in matches) > 1:
                errors.append(f"duplicate {name}")
        measure = measures[0] if len(measures) == 1 else None
        page_match = RENDERED_PAGES_VALUE.fullmatch(fields.get("PAGES", ""))
        if "PAGES" in fields and page_match is None:
            errors.append("PAGES must say '<seen> of <expected> imaged'")
        block_match = RENDERED_BLOCKS_VALUE.fullmatch(fields.get("BLOCKS", ""))
        if "BLOCKS" in fields and block_match is None:
            errors.append("BLOCKS must say '<seen> of <expected> read'")
        unit_match = block_match or page_match
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
                units_seen=int(unit_match.group("seen")) if unit_match else None,
                units_expected=int(unit_match.group("expected")) if unit_match else None,
                measure=measure,
                source=source,
                unseen=fields.get("UNSEEN"),
                read=read,
                verdict=verdict,
                errors=tuple(errors),
            )
        )
    return tuple(readings)


def _render_passes(root: Path) -> tuple[tuple[tuple[int, RenderPass], ...], int]:
    render = root / "render"
    numbered = render_pass.read_passes(render)
    passes = tuple(
        (
            number,
            RenderPass(
                tuple(sorted(path for path in child.glob("*.png") if path.is_file())),
                tuple(
                    sorted(
                        path
                        for path in child.iterdir()
                        if path.is_file() and path.suffix.lower() in {".pdf", ".xps", ".html"}
                    )
                ),
            ),
        )
        for number, child in numbered
    )
    return passes, render_pass.missing_pass_numbers(numbered)


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
    html_value = parsed.value("--html")
    html = Path(html_value) if html_value is not None else None
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
        draft_bytes = draft.read_bytes()
        draft_text = draft.read_text(encoding="utf-8")
        heading_read_path = root / "heading-read.md"
        heading_read_text = (
            heading_read_path.read_text(encoding="utf-8")
            if heading_read_path.is_file()
            else ""
        )
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
        initial_reading = next(
            (item for item in readings if item.artifact == draft.stem), None
        )
        if initial_reading is not None and initial_reading.composer_outcome not in {
            "inline", "attachment"
        }:
            raise run_grader.SourceError(
                "initial post REREAD needs COMPOSER-OUTCOME: inline or attachment"
            )
        post_text = post_path.read_text(encoding="utf-8") if post_path.is_file() else ""
    except (OSError, UnicodeError, ValueError) as failure:
        raise run_grader.SourceError(f"could not read the discussion-post run: {failure}") from failure
    rendered_paragraph_texts = _docx_paragraph_texts(docx) if docx is not None else ()
    (
        submission_heading_failures,
        submission_comment_count,
        submission_text_mismatches,
        submitted_blocks,
    ) = _html_properties(html, draft_text) if html is not None else (0, 0, None, None)
    render_passes, missing_pass_numbers = _render_passes(root)
    return RunSource(
        path=root,
        draft=draft,
        draft_text=draft_text,
        body=section.body,
        references=section.references,
        claims=claims,
        draft_bytes=draft_bytes,
        heading_read_text=heading_read_text,
        bar=bar,
        html=html,
        submission_heading_failures=submission_heading_failures,
        submission_comment_count=submission_comment_count,
        submission_text_mismatches=submission_text_mismatches,
        submitted_blocks=submitted_blocks,
        docx=docx,
        rendered_paragraph_texts=rendered_paragraph_texts,
        expected_paragraph_texts=_expected_paragraph_texts(draft_text) if docx is not None else (),
        html_matches_rebuild=(
            html.read_bytes() == post_html.render(draft_text).encode("utf-8")
            if html is not None
            else None
        ),
        docx_matches_rebuild=(
            _docx_matches_rebuild(docx, draft_text) if docx is not None else None
        ),
        rendered_readings=_rendered_readings(post_text) if html is not None else (),
        render_passes=render_passes,
        missing_pass_numbers=missing_pass_numbers,
        refused_label=section.refused_label,
        post_url=post_fields.get("POST-URL"),
        post_posted=post_fields.get("POSTED"),
        readings=readings,
    )


def _posted_reading_findings(source: RunSource) -> tuple[Finding, ...]:
    submission = source.draft.stem
    reading = next(
        (item for item in source.readings if item.artifact == submission), None
    )
    posting_absent = source.post_url is None and source.post_posted is None
    if posting_absent and reading is None:
        return ()
    if reading is None:
        return (
            Finding(
                MISSING_POSTED_READING,
                submission,
                "no REREAD record for the posted initial entry",
            ),
        )
    findings: list[Finding] = []
    missing = list(reading.missing_record_fields)
    if (
        not reading.html_bytes.isdigit()
        or (source.html is not None and int(reading.html_bytes) != source.html.stat().st_size)
    ):
        missing.append("HTML-BYTES matching the built HTML")
    if reading.composer_outcome == "attachment":
        if not reading.refusal_is_dated:
            missing.append("REFUSAL with date and observed wording")
        if not reading.attachment:
            missing.append("ATTACHMENT")
    if not posting_absent and not source.post_url:
        missing.append(f"{submission} POST-URL")
    if not posting_absent and not source.post_posted:
        missing.append(f"{submission} POSTED")
    if missing:
        findings.append(
            Finding(
                MISSING_POSTED_READING,
                submission,
                "missing " + ", ".join(missing),
            )
        )
    if not reading.verdict_is_known:
        findings.append(
            Finding(UNKNOWN_VERDICT, submission, "verdict is outside the vocabulary")
        )
    elif not reading.verdict_has_substance:
        findings.append(
            Finding(BARE_VERDICT, submission, "verdict carries no reading substance")
        )
    if reading.entry_id is None:
        findings.append(
            Finding(UNLOCATED_READING, submission, "POST-URL has no entry_id")
        )
    elif not posting_absent and reading.post_url != source.post_url:
        findings.append(
            Finding(
                BORROWED_LOCATOR,
                submission,
                f"POST-URL does not match {submission}",
            )
        )
    digest = file_digest.sha256(source.draft)
    if not reading.submission_sha256_is_valid or reading.submission_sha256 != digest:
        findings.append(
            Finding(
                SUBMISSION_FINGERPRINT,
                submission,
                f"{source.draft.name} SUBMISSION-SHA256 is missing, malformed, or stale",
            )
        )
    if (
        reading.composer_outcome == "inline"
        and source.html is not None
        and not source.html_matches_rebuild
    ):
        findings.append(
            Finding(
                SUBMISSION_FINGERPRINT,
                submission,
                f"{source.html.name} differs from post_html's rebuild of {source.draft.name}",
            )
        )
    if source.docx is not None and not source.docx_matches_rebuild:
        findings.append(
            Finding(
                SUBMISSION_FINGERPRINT,
                submission,
                f"{source.docx.name} parts differ from docx_write.parts() for {source.draft.name}",
            )
        )
    if reading.composer_outcome == "attachment":
        retained = reading.posted_attachment(source.path)
        if source.docx is None or retained is None or not retained.is_file():
            findings.append(Finding(
                POSTED_ATTACHMENT, submission,
                "ATTACHMENT must name an existing posted/ Word copy and --docx is required",
            ))
        elif (
            retained.name != source.docx.name
            or file_digest.sha256(retained) != file_digest.sha256(source.docx)
        ):
            findings.append(Finding(
                POSTED_ATTACHMENT, submission,
                "posted attachment filename or SHA-256 differs from the local Word document",
            ))
    return tuple(findings)


def _rendered_comment_findings(source: RunSource) -> tuple[Finding, ...]:
    if not source.submission_comment_count:
        return ()
    assert source.html is not None
    return tuple(
        Finding(
            RENDERED_COMMENTS,
            source.html.name,
            "submission carries an HTML comment",
        )
        for _ in range(source.submission_comment_count)
    )


def _submission_findings(source: RunSource) -> tuple[Finding, ...]:
    reading = next(
        (item for item in source.readings if item.artifact == source.draft.stem), None
    )
    if reading is not None and reading.composer_outcome == "attachment":
        return ()
    if source.html is None:
        return ()
    headings = tuple(
        Finding(BOLD_HEADINGS, source.html.name, "heading is not a fully bold paragraph")
        for _ in range(source.submission_heading_failures)
    )
    text = (
        (
            Finding(
                SUBMISSION_TEXT,
                source.html.name,
                "submission paragraph text differs from the Markdown",
            ),
        )
        if source.submission_text_mismatches
        else ()
    )
    return headings + _rendered_comment_findings(source) + text


@dataclass(frozen=True)
class RenderedPageSurvey:
    findings: tuple[Finding, ...]
    engine_available: bool = True


def _rendered_page_findings(source: RunSource) -> RenderedPageSurvey:
    if source.html is None:
        return RenderedPageSurvey(())
    if not source.rendered_readings:
        return RenderedPageSurvey(
            (
                Finding(
                    RENDERED_PAGES,
                    "post.md",
                    "no RENDERED record for the Canvas box",
                ),
            )
        )
    findings: list[Finding] = []
    engine_available = True
    retained_count = len(source.render_passes)
    highest_pass_number = source.render_passes[-1][0] if source.render_passes else 0
    reading_count = len(source.rendered_readings)
    if reading_count not in {retained_count, highest_pass_number}:
        findings.append(
            Finding(
                RENDERED_PAGES,
                "render",
                "RENDERED record count does not match retained pass directories",
            )
        )
    passes_by_number = dict(source.render_passes)
    align_by_number = reading_count == highest_pass_number
    submitted_bytes = source.html.read_bytes()
    for index, reading in enumerate(source.rendered_readings, start=1):
        detail: list[str] = list(reading.errors)
        is_last = index == reading_count
        retained = (
            (index, passes_by_number[index])
            if align_by_number and index in passes_by_number
            else source.render_passes[index - 1]
            if not align_by_number and index <= retained_count
            else None
        )
        pass_number, retained_pass = (
            retained if retained is not None else (index, RenderPass((), ()))
        )
        missing_retained_pass_is_gap = align_by_number and retained is None
        pass_name = f"pass-{pass_number}"
        if reading.artifact != "post.md":
            detail.append("record artifact is not post.md")
        if reading.measure != "BLOCKS":
            detail.append("Canvas-box record must use BLOCKS")
        if reading.source != "canvas-box":
            detail.append("Canvas-box record must use SOURCE canvas-box")
        if reading.units_seen is not None and reading.units_seen < 1:
            detail.append("BLOCKS read count must be positive")
        if reading.units_expected is not None and reading.units_expected < 1:
            detail.append("BLOCKS expected count must be positive")
        if (
            reading.units_expected is not None
            and source.submitted_blocks is not None
            and reading.units_expected != source.submitted_blocks
        ):
            detail.append(
                f"BLOCKS expected count is {reading.units_expected}, not the "
                f"submitted HTML's {source.submitted_blocks}"
            )
        if not missing_retained_pass_is_gap:
            if not retained_pass.pixels:
                detail.append(f"{pass_name} keeps no Canvas-box capture")
            else:
                for pixel in retained_pass.pixels:
                    try:
                        failure = page_image.page_read_error(pixel)
                    except pdf_engine.EngineUnavailable:
                        engine_available = False
                        break
                    if failure:
                        detail.append(f"{pixel.name} {failure}")
            if len(retained_pass.exports) != 1:
                detail.append(
                    f"{pass_name} keeps {len(retained_pass.exports)} exports, not 1"
                )
            else:
                export = retained_pass.exports[0]
                if export.suffix.casefold() != ".html":
                    detail.append(f"{pass_name} export is not HTML")
                else:
                    try:
                        retained_bytes = export.read_bytes()
                    except OSError as failure:
                        detail.append(f"could not read {export.name}: {failure}")
                    else:
                        if retained_bytes != submitted_bytes:
                            detail.append("retained HTML differs from the submitted HTML")
        if (
            is_last
            and reading.units_seen is not None
            and reading.units_expected is not None
            and reading.units_seen != reading.units_expected
        ):
            detail.append("not every expected block was read")
        if is_last and reading.unseen is not None and reading.unseen.casefold() != "none":
            detail.append("UNSEEN names an unchecked block")
        if detail:
            findings.append(Finding(RENDERED_PAGES, pass_name, "; ".join(detail)))
    last = source.rendered_readings[-1]
    if last.verdict is not None and not last.verdict.casefold().startswith("clean -"):
        findings.append(
            Finding(RENDERED_PAGES, "post.md", "the last rendered verdict is not clean")
        )
    return RenderedPageSurvey(tuple(findings), engine_available)


def _attachment_page_findings(source: RunSource) -> RenderedPageSurvey:
    """Grade the last retained Word pass after a refused inline attempt."""
    if not source.render_passes or not source.rendered_readings:
        return RenderedPageSurvey((Finding(
            RENDERED_PAGES, "render", "no visually checked Word render pass"
        ),))
    number, retained = source.render_passes[-1]
    reading = source.rendered_readings[-1]
    details = list(reading.errors)
    if len(source.rendered_readings) not in {
        len(source.render_passes), source.render_passes[-1][0]
    }:
        details.append("RENDERED record count differs from retained pass count")
    if reading.artifact != "post.md" or reading.measure != "PAGES":
        details.append("attachment render needs a post.md PAGES reading")
    if reading.source not in {"word-pdf", "word-xps", "clinician"}:
        details.append("attachment render needs a Word export SOURCE")
    if (
        reading.units_seen is None
        or reading.units_seen < 1
        or reading.units_seen != reading.units_expected
    ):
        details.append("not every Word page was read")
    if reading.unseen is None or reading.unseen.casefold() != "none":
        details.append("UNSEEN must say none")
    if reading.verdict is None or not reading.verdict.casefold().startswith("clean -"):
        details.append("last Word render verdict is not clean")
    exports = [
        item for item in retained.exports if item.suffix.casefold() in {".pdf", ".xps"}
    ]
    if len(exports) != 1:
        details.append("Word pass needs exactly one PDF or XPS export")
    else:
        try:
            pages = page_image.export_page_count(exports[0])
            if pages != reading.units_expected or len(retained.pixels) != pages:
                details.append("Word export page count differs from the reading or pixels")
        except pdf_engine.EngineUnavailable:
            return RenderedPageSurvey(
                tuple(Finding(RENDERED_PAGES, f"pass-{number}", detail) for detail in details),
                False,
            )
        except pdf_engine.SourceUnreadable as failure:
            details.append(str(failure))
    for pixel in retained.pixels:
        try:
            failure = page_image.page_read_error(pixel)
        except pdf_engine.EngineUnavailable:
            return RenderedPageSurvey(
                tuple(Finding(RENDERED_PAGES, f"pass-{number}", detail) for detail in details),
                False,
            )
        if failure:
            details.append(f"{pixel.name} {failure}")
    digest = file_digest.recorded_sha256(
        source.path / "render" / f"pass-{number}" / "post-draft.sha256"
    )
    if digest != file_digest.sha256(source.draft):
        details.append("Word pass has no matching Markdown fingerprint")
    return RenderedPageSurvey(
        (Finding(RENDERED_PAGES, f"pass-{number}", "; ".join(details)),)
        if details else ()
    )


def survey(source: RunSource) -> Scan:
    initial_reading = next(
        (item for item in source.readings if item.artifact == source.draft.stem), None
    )
    attachment = initial_reading is not None and initial_reading.composer_outcome == "attachment"
    rendered_pages = (
        _attachment_page_findings(source)
        if attachment else _rendered_page_findings(source)
    )
    has_posted_reading = any(
        item.artifact == source.draft.stem for item in source.readings
    )
    posting_fields_absent = source.post_url is None and source.post_posted is None
    posted_reading_graded = has_posted_reading or not posting_fields_absent
    posted_reading_unread = int(has_posted_reading and posting_fields_absent)
    heading = heading_read.scan(
        source.heading_read_text,
        (
            heading_read.Binding(
                source.draft.name,
                source.draft_bytes,
                tuple(research_ledger.read_records(source.claims)),
            ),
        ),
    )
    heading_findings = tuple(
        Finding(kind, finding.artifact, finding.detail)
        for kind in HEADING_READ_ROWS
        for finding in heading.findings
        if finding.kind == kind
    )
    if source.refused_label is not None:
        findings = _submission_findings(source) + rendered_pages.findings + heading_findings
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
            missing_pass_numbers=source.missing_pass_numbers,
            html_graded=source.html is not None and not attachment,
            render_route="attachment" if attachment else "inline",
            rendered_pages_graded=rendered_pages.engine_available,
            docx_graded=source.docx is not None,
            reference_boundary_graded=False,
            posted_reading_graded=posted_reading_graded,
            heading_reads=heading.records_read,
            heading_read_unread=heading.unread,
            posted_reading_unread=posted_reading_unread,
            findings=findings + _posted_reading_findings(source),
        )
    words = len(WORD.findall(_countable_body(source.body)))
    records = _claim_records(source.claims)
    reference_key_set = ClaimReferenceIndex.from_records(records)
    listed_references = ReferenceKeySet.from_references(source.references)
    body_citations, citations, coverage = _citation_keys(source.body, reference_key_set)
    numbers = traceable_numeric_values(source.body, body_citations)
    findings: list[Finding] = list(_posted_reading_findings(source) + heading_findings)
    for block in _claim_blocks(source.claims):
        reference = CLAIM_REFERENCE.search(block)
        if reference is not None and legal_reference_lacks_name(
            reference.group("value").replace("\n", " ")
        ):
            findings.append(
                Finding(
                    LEGAL_REFERENCE_NAME,
                    "claims.md",
                    "legal claim record has a section but no legal source name",
                )
            )
    if words < source.bar.word_floor:
        findings.append(Finding(WORD_FLOOR, source.draft.name, f"{words} words"))
    if words == 0:
        findings.append(Finding(EMPTY_BODY, source.draft.name, "no body words"))
    if len(source.references) < source.bar.reference_minimum:
        findings.append(
            Finding(
                REFERENCE_MINIMUM,
                source.draft.name,
                f"{len(source.references)} references",
            )
        )
    findings.extend(_submission_findings(source))
    findings.extend(rendered_pages.findings)
    traced_numbers = frozenset(
        value for record in records for value in record.numbers
    )
    all_claim_numbers = frozenset(
        value for record in records for value in record.all_numbers
    )
    distinct_numbers = tuple(dict.fromkeys(value.casefold() for value in numbers))
    for value in distinct_numbers:
        if value not in traced_numbers:
            findings.append(
                Finding(
                    UNTRACED_NUMBER,
                    source.draft.name,
                    (
                        f"{value} appears only in a disbelieved claim record"
                        if value in all_claim_numbers
                        else f"{value} is absent from claims.md"
                    ),
                )
            )
    citation_requirements: list[tuple[Citation, tuple[int, ...]]] = []
    for occurrence, (citation, keys) in enumerate(
        zip(body_citations, citations, strict=True), start=1
    ):
        if listed_references.missing_first_author_initials(citation.author):
            findings.append(
                Finding(
                    MISSING_FIRST_AUTHOR_INITIALS,
                    source.draft.name,
                    f"citation occurrence {occurrence} omits required first-author initials",
                )
            )
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
        missing_pass_numbers=source.missing_pass_numbers,
        html_graded=source.html is not None and not attachment,
        render_route="attachment" if attachment else "inline",
        rendered_pages_graded=rendered_pages.engine_available,
        docx_graded=source.docx is not None,
        reference_boundary_graded=True,
        posted_reading_graded=posted_reading_graded,
        heading_reads=heading.records_read,
        heading_read_unread=heading.unread,
        posted_reading_unread=posted_reading_unread,
        findings=tuple(findings),
        citation_coverage=coverage,
    )


def legal_reader_covered() -> str:
    """State the derived composition of the narrow code-section recognizer."""

    return (
        f"code-section recognizer coverage: {len(LEGAL_READER_MECHANISMS)} mechanisms -- "
        + ", ".join(description for _pattern, description in LEGAL_READER_MECHANISMS)
        + "."
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
            else f"words: {NOT_GRADED}"
        ),
        f"word ceiling: {scan.word_ceiling if scan.word_ceiling is not None else 'none'}",
        (
            f"word ceiling exceeded: {'yes' if exceeded else 'no'} (counted, never graded)"
            if scan.reference_boundary_graded
            else f"word ceiling exceeded: {NOT_GRADED}"
        ),
        (
            f"references: {scan.references} (minimum {scan.reference_minimum})"
            if scan.reference_boundary_graded
            else f"references: {NOT_GRADED}"
        ),
        f"numeric claims: {scan.numeric_claims if scan.reference_boundary_graded else NOT_GRADED}",
        f"claim records: {scan.claim_records if scan.reference_boundary_graded else NOT_GRADED}",
        f"citations: {scan.citations if scan.reference_boundary_graded else NOT_GRADED}",
        (
            scan.citation_coverage.report_line()
            if scan.reference_boundary_graded
            else CitationCoverage().report_line()
        ),
        (
            f"invoked sources: {len(scan.invoked_sources or ())}"
            if scan.reference_boundary_graded
            else f"invoked sources: {NOT_GRADED}"
        ),
        (
            "unfilled invoked properties: "
            f"{scan.unfilled_invoked_properties} (counted, {NOT_GRADED})"
            if scan.reference_boundary_graded
            else f"unfilled invoked properties: {NOT_GRADED}"
        ),
        (
            f"pre-#496 markers: {scan.pre_496_markers} (counted, {NOT_GRADED})"
            if scan.reference_boundary_graded
            else f"pre-#496 markers: {NOT_GRADED}"
        ),
        f"heading-read records: {scan.heading_reads}",
        run_grader.format_unread_remainder(
            scan.heading_read_unread + scan.posted_reading_unread
        ),
        (
            f"{RENDERED_TEXT}: {scan.rendered_text_mismatches} (reported, {NOT_GRADED})"
            if scan.docx_graded
            else f"{RENDERED_TEXT}: {NOT_GRADED}"
        ),
        f"missing pass numbers: {scan.missing_pass_numbers} (counted, {NOT_GRADED})",
        legal_reader_covered(),
        f"findings: {len(scan.findings)}",
    ]
    for kind in ROWS:
        if kind in POSTED_READING_ROWS and not scan.posted_reading_graded:
            lines.append(f"{kind}: {NOT_GRADED}")
        elif kind not in {
            BOLD_HEADINGS,
            RENDERED_COMMENTS,
            SUBMISSION_TEXT,
            RENDERED_PAGES,
            MISSING_POSTED_READING,
            UNKNOWN_VERDICT,
            BARE_VERDICT,
            UNLOCATED_READING,
            BORROWED_LOCATOR,
            *heading_read.KINDS,
            SUBMISSION_FINGERPRINT,
            POSTED_ATTACHMENT,
        } and not scan.reference_boundary_graded:
            lines.append(f"{kind}: {NOT_GRADED}")
        elif kind == RENDERED_PAGES and not scan.rendered_pages_graded:
            lines.append(
                f"{kind}: {sum(finding.kind == kind for finding in scan.findings)} - "
                f"{pdf_engine.RENDER_UNAVAILABLE}; "
                "not mechanically verified"
            )
        elif kind in {BOLD_HEADINGS, RENDERED_COMMENTS, SUBMISSION_TEXT} and not scan.html_graded:
            lines.append(f"{kind}: {NOT_GRADED}")
        elif (
            kind == RENDERED_PAGES
            and not scan.html_graded
            and scan.render_route != "attachment"
        ):
            lines.append(f"{kind}: {NOT_GRADED}")
        else:
            lines.append(
                f"{kind}: {sum(finding.kind == kind for finding in scan.findings)}"
            )
    if show:
        lines.extend(scan.citation_coverage.disagreement_lines())
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
    aar_failed, aar_report = aar_scan.completion_gate(
        source.path, _parsed.value("--submission")
    )
    return run_grader.Grade(
        scan=scanned,
        source=str(source.path),
        findings_failed=any(
            all(
                getattr(scanned, gate)
                or gate in PARTIAL_GATES
                or finding.kind not in kinds
                or (
                    gate == "html_graded"
                    and scanned.render_route == "attachment"
                    and finding.kind == RENDERED_PAGES
                )
                for gate, (kinds, _field_names) in GATED_ROW_SETS.items()
            )
            for finding in scanned.findings
        )
        or aar_failed,
        coverage_failed=(
            not scanned.reference_boundary_graded
            or not scanned.rendered_pages_graded
            or scanned.heading_read_unread > 0
            or scanned.posted_reading_unread > 0
        ),
        diagnostics=(
            (f"refused reference label in {source.draft.name}: {source.refused_label}",)
            if source.refused_label is not None
            else ()
        ),
        reports=(aar_report,),
    )


GRADER = run_grader.Grader(
    usage=(
        "usage: discussion_post_scan.py <run directory> --draft <Markdown file> "
        "[--html <HTML file>] [--docx <Word file>] [--show] [--submission <key>]"
    ),
    load=load,
    grade=grade,
    format_report=format_report,
    options=(
        run_grader.Option("--draft", takes_value=True, missing_value="--draft needs a Markdown file", repeatable=False),
        run_grader.Option("--html", takes_value=True, missing_value="--html needs an HTML file", repeatable=False),
        run_grader.Option("--docx", takes_value=True, missing_value="--docx needs a Word file", repeatable=False),
        run_grader.Option("--show", repeatable=False),
        run_grader.Option("--submission", takes_value=True, missing_value="--submission needs a key", repeatable=False),
    ),
)


def main(argv: list[str]) -> int:
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
