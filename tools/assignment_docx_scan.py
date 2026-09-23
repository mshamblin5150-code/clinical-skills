#!/usr/bin/env python3
"""Grade the canonical Word artifact for a course-assignment DOCX run."""

from __future__ import annotations

import re
import sys
import zipfile
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree

import aar_scan
import assignment_bar
import assignment_docx
import assignment_submission
from discussion_artifact import (
    CLAIM_BLOCK,
    CLAIM_REFERENCE,
    ReferenceKeySet,
    citation_occurrence_keys,
    claim_record_can_certify_values,
    read_citations,
    reference_keys,
)
from discussion_post_scan import traceable_numeric_values
import file_digest
import reference_scan
import render_pass
import research_ledger
import run_grader
import voice_model_identity
from run_grader import NOT_GRADED


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
DC = "{http://purl.org/dc/elements/1.1/}"
POSITIVE_INTEGER = re.compile(r"[1-9][0-9]*", re.ASCII)
RENDERED_HEADER = re.compile(r"(?i)^#+\s*RENDERED\s*:\s*(.*?)\s*$")
RENDERED_FIELD = re.compile(
    r"(?i)^(PASS|PAGES|SOURCE|UNSEEN|READ|VERDICT)\s*:\s*(.*?)\s*$"
)
PAGES_READ = re.compile(r"([0-9]+)\s+of\s+([0-9]+)\s+read", re.I | re.ASCII)
WORD = re.compile(r"(?:\$?\d[\d,.]*|[A-Za-z]+(?:[-'\u2019][A-Za-z]+)*)")

PACKAGE_STRUCTURE = "package-structure"
WORD_RANGE = "word-range"
REFERENCE_MINIMUM = "reference-minimum"
REFERENCE_DEFECT = "reference-defect"
CLAIM_LEDGER = "claim-ledger"
UNTRACED_NUMBER = "untraced-number"
UNTRACED_CITATION = "untraced-citation"
RENDERED_RECORD = "rendered-record"
ROWS = (
    PACKAGE_STRUCTURE,
    WORD_RANGE,
    REFERENCE_MINIMUM,
    REFERENCE_DEFECT,
    CLAIM_LEDGER,
    UNTRACED_NUMBER,
    UNTRACED_CITATION,
    RENDERED_RECORD,
)
KINDS = ROWS
EXPECTED_COMPLETION_CHECKS = (
    aar_scan.EXPECTED_ROW,
    voice_model_identity.EXPECTED_ROW,
)


@dataclass(frozen=True)
class DeclaredLimit:
    key: str
    limit: str


DECLARED_LIMITS = (
    DeclaredLimit(
        "claim-support-unverified",
        "Token tracing does not establish that a believed record supports the paper's factual assertion.",
    ),
    DeclaredLimit(
        "assignment-fit-unverified",
        "No mechanical row judges whether the paper answers every assignment-specific prose requirement.",
    ),
    DeclaredLimit(
        "visual-purpose-unverified",
        "Package structure cannot decide whether each visual materially improves the assignment.",
    ),
    DeclaredLimit(
        "bar-transcription-unverified",
        "A structurally valid signed bar does not prove that it faithfully transcribes the live course pages.",
    ),
)
REQUIRED_BAR_FIELDS = (
    "ASSIGNMENT",
    "SIGNED",
    "ARTIFACT",
    "SUBMISSION-TYPE",
    "WORD-MIN",
    "WORD-MAX",
    "REFERENCE-MIN",
    "SOURCE-CLASSES",
    "RECENCY-WINDOW-YEARS",
)
FINGERPRINT_FILE = assignment_docx.FINGERPRINT_FILE


@dataclass(frozen=True)
class Bar:
    signed: date
    word_min: int
    word_max: int | None
    reference_min: int


@dataclass(frozen=True)
class Paragraph:
    text: str
    style: str


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    detail: str = ""


@dataclass(frozen=True)
class Source:
    root: Path
    docx: Path
    docx_bytes: bytes
    bar: Bar
    paragraphs: tuple[Paragraph, ...]
    package_findings: tuple[Finding, ...]
    claims: str
    rendered: str


@dataclass(frozen=True)
class Scan:
    paragraphs_read: int
    body_words: int
    references_read: int
    claim_records: int
    retained_passes: int
    rendered_records: int
    findings: tuple[Finding, ...]


def _positive(envelope: assignment_bar.Envelope, name: str) -> int:
    value = envelope.fields[name]
    if not POSITIVE_INTEGER.fullmatch(value):
        raise run_grader.SourceError(f"bar.md {name} must be a positive integer")
    return int(value)


def _word_max(envelope: assignment_bar.Envelope) -> int | None:
    value = envelope.fields["WORD-MAX"]
    if value.casefold() == "none":
        return None
    return _positive(envelope, "WORD-MAX")


def _read_bar(text: str, envelope: assignment_bar.Envelope | None = None) -> Bar:
    envelope = envelope or assignment_bar.parse(text)
    for name in REQUIRED_BAR_FIELDS:
        count = envelope.counts.get(name, 0)
        if count > 1:
            raise run_grader.SourceError(f"bar.md has a duplicate {name} field")
        if count == 0:
            raise run_grader.SourceError(f"bar.md needs a {name} field")
    if envelope.artifact != "docx":
        raise run_grader.SourceError("bar.md ARTIFACT must be docx for this grader")
    if envelope.fields["SUBMISSION-TYPE"].casefold() != "file-upload":
        raise run_grader.SourceError(
            "a DOCX course assignment requires SUBMISSION-TYPE file-upload"
        )
    word_min = _positive(envelope, "WORD-MIN")
    word_max = _word_max(envelope)
    research_ledger.read_bar(
        "SOURCE-CLASSES: "
        + envelope.fields["SOURCE-CLASSES"]
        + "\nRECENCY-WINDOW-YEARS: "
        + envelope.fields["RECENCY-WINDOW-YEARS"]
        + "\n"
    )
    return Bar(
        date.fromisoformat(envelope.fields["SIGNED"]),
        word_min,
        word_max,
        _positive(envelope, "REFERENCE-MIN"),
    )


def validate_bar(envelope: assignment_bar.Envelope) -> None:
    """Validate the DOCX branch fields without requiring a produced artifact."""

    _read_bar("", envelope)


def _paragraphs(root: ElementTree.Element) -> tuple[Paragraph, ...]:
    found = []
    for paragraph in root.iter(W + "p"):
        text = "".join(node.text or "" for node in paragraph.iter(W + "t")).strip()
        if not text:
            continue
        style_node = paragraph.find("./" + W + "pPr/" + W + "pStyle")
        found.append(
            Paragraph(text, style_node.get(W + "val", "") if style_node is not None else "")
        )
    return tuple(found)


def _package(
    archive: zipfile.ZipFile, paragraphs: tuple[Paragraph, ...]
) -> tuple[Finding, ...]:
    names = set(archive.namelist())
    required = {
        "[Content_Types].xml",
        "_rels/.rels",
        "docProps/core.xml",
        "word/document.xml",
        "word/styles.xml",
        "word/header1.xml",
        "word/_rels/document.xml.rels",
    }
    defects = []
    missing = sorted(required - names)
    if missing:
        defects.append("missing package parts: " + ", ".join(missing))
    if "word/styles.xml" in names:
        styles = archive.read("word/styles.xml").decode("utf-8")
        for style in ("Title", "Heading1", "Caption", "Reference"):
            if f'w:styleId="{style}"' not in styles:
                defects.append(f"missing native {style} style")
    document_bytes = archive.read("word/document.xml")
    document = document_bytes.decode("utf-8")
    if "<w:tblHeader" not in document:
        defects.append("no repeating table header was found")
    document_root = ElementTree.fromstring(document_bytes)
    drawings = tuple(document_root.iter(WP + "docPr"))
    if not drawings:
        defects.append("no figure carries alt text")
    elif any(not (node.get("descr") or "").strip() for node in drawings):
        defects.append("every figure must carry alt text")
    if "word/_rels/document.xml.rels" in names:
        rels_root = ElementTree.fromstring(
            archive.read("word/_rels/document.xml.rels")
        )
        relationships = {
            node.get("Id", ""): node.get("Target", "")
            for node in rels_root.iter(REL + "Relationship")
        }
        for blip in document_root.iter(A + "blip"):
            target = relationships.get(blip.get(R + "embed", ""), "")
            package_target = str(PurePosixPath("word") / target)
            if not target or package_target not in names:
                defects.append("a figure relationship has no readable media target")
    captions = [paragraph.text for paragraph in paragraphs if paragraph.style == "Caption"]
    if not any(text.casefold().startswith("table ") for text in captions):
        defects.append("no table caption was found")
    if not any(text.casefold().startswith("figure ") for text in captions):
        defects.append("no figure caption was found")
    if "word/header1.xml" in names and 'w:instr="PAGE"' not in archive.read("word/header1.xml").decode("utf-8"):
        defects.append("the running page-number field is missing")
    if "docProps/core.xml" in names:
        core = ElementTree.fromstring(archive.read("docProps/core.xml"))
        if not (core.findtext(DC + "title") or "").strip():
            defects.append("core title metadata is empty")
        if not (core.findtext(DC + "creator") or "").strip():
            defects.append("core creator metadata is empty")
    return tuple(Finding(PACKAGE_STRUCTURE, defect) for defect in defects)


def load(
    parsed: run_grader.Parsed,
    envelope: assignment_bar.Envelope | None = None,
) -> Source:
    root = Path(parsed.source)
    docx_value = parsed.value("--docx")
    if not root.is_dir():
        raise run_grader.SourceError(f"no run directory at {root}")
    if docx_value is None:
        raise run_grader.SourceError("--docx needs a Word file")
    docx = Path(docx_value)
    if not docx.is_file() or docx.suffix.casefold() != ".docx":
        raise run_grader.SourceError(f"no Word file at {docx}")
    bar_path, claims_path = root / "bar.md", root / "claims.md"
    if not bar_path.is_file() or not claims_path.is_file():
        raise run_grader.SourceError("run needs bar.md and claims.md before it can be scanned")
    try:
        bar_text = bar_path.read_text(encoding="utf-8")
        bar = _read_bar(bar_text, envelope)
        claims = claims_path.read_text(encoding="utf-8")
        docx_bytes = docx.read_bytes()
        with zipfile.ZipFile(docx) as archive:
            document = ElementTree.fromstring(archive.read("word/document.xml"))
            paragraphs = _paragraphs(document)
            package_findings = _package(archive, paragraphs)
        rendered_path = root / "rendered.md"
        rendered = rendered_path.read_text(encoding="utf-8") if rendered_path.is_file() else ""
    except (OSError, UnicodeError, zipfile.BadZipFile, KeyError, ElementTree.ParseError) as failure:
        raise run_grader.SourceError(f"could not read the DOCX run: {failure}") from failure
    return Source(root, docx, docx_bytes, bar, paragraphs, package_findings, claims, rendered)


def _document_parts(paragraphs: tuple[Paragraph, ...]) -> tuple[str, tuple[str, ...]]:
    body_lines = []
    references = []
    in_body = False
    in_references = False
    for paragraph in paragraphs:
        if paragraph.style == "Heading1":
            if paragraph.text.casefold() == "references":
                in_references = True
                body_lines.append("# References")
                continue
            in_body = True
            body_lines.append("# " + paragraph.text)
            continue
        if in_references and paragraph.style == "Reference":
            references.append(paragraph.text)
            body_lines.append(paragraph.text)
        elif in_body and not in_references and paragraph.style != "Caption":
            body_lines.append(paragraph.text)
    return "\n\n".join(body_lines), tuple(references)


def _claim_keys(claims: str) -> tuple[set[tuple[str, str]], set[str], int]:
    keys: set[tuple[str, str]] = set()
    numbers: set[str] = set()
    records = 0
    for match in CLAIM_BLOCK.finditer(claims):
        records += 1
        block = match.group("block")
        if not claim_record_can_certify_values(block):
            continue
        numbers.update(value.casefold() for value in traceable_numeric_values(block.splitlines()[0]))
        reference = CLAIM_REFERENCE.search(block)
        if reference is not None:
            keys.update(reference_keys(reference.group("value").replace("\n", " ")))
    return keys, numbers, records


def _rendered_findings(source: Source) -> tuple[tuple[Finding, ...], int, int]:
    fields: dict[str, str] = {}
    counts: dict[str, int] = {}
    header = ""
    records = 0
    for line in source.rendered.splitlines():
        match = RENDERED_HEADER.match(line)
        if match:
            records += 1
            header = match.group(1).strip()
            continue
        match = RENDERED_FIELD.match(line)
        if match and records:
            name = match.group(1).upper()
            counts[name] = counts.get(name, 0) + 1
            fields[name] = match.group(2).strip()
    passes = render_pass.read_passes(source.root / "render")
    defects = []
    if records != 1:
        defects.append("rendered.md must carry exactly one RENDERED record")
    if header and header != source.docx.name:
        defects.append("rendered record names another DOCX")
    for name in ("PASS", "PAGES", "SOURCE", "UNSEEN", "READ", "VERDICT"):
        if counts.get(name, 0) != 1 or not fields.get(name, ""):
            defects.append(f"{name} must appear once with a value")
    highest = passes[-1] if passes else None
    if highest is None:
        defects.append("DOCX has no retained render pass")
    elif fields.get("PASS") != str(highest[0]):
        defects.append("rendered record does not name the highest retained pass")
    if highest is not None:
        png_count = sum(path.is_file() for path in highest[1].glob("*.png"))
        exports = tuple(
            path
            for path in highest[1].iterdir()
            if path.is_file() and path.suffix.casefold() in {".pdf", ".xps"}
        )
        if len(exports) != 1:
            defects.append("highest retained pass must contain one page-faithful PDF or XPS export")
        elif fields.get("SOURCE", "").casefold() != f"word-{exports[0].suffix[1:].casefold()}":
            defects.append("SOURCE does not match the retained Word export type")
        page_match = PAGES_READ.fullmatch(fields.get("PAGES", ""))
        if page_match is None or (int(page_match.group(1)), int(page_match.group(2))) != (png_count, png_count):
            defects.append("highest-pass page and PNG counts do not agree")
        retained = file_digest.recorded_sha256(highest[1] / FINGERPRINT_FILE)
        if retained != file_digest.sha256(source.docx):
            defects.append("highest retained pass does not match the canonical DOCX fingerprint")
    if fields.get("SOURCE", "").casefold() not in {"word-pdf", "word-xps"}:
        defects.append("SOURCE must be word-pdf or word-xps")
    if fields.get("UNSEEN", "").casefold() != "none":
        defects.append("UNSEEN must be none")
    if not re.fullmatch(r"(?is)clean\s+-\s+.+", fields.get("VERDICT", "")):
        defects.append("VERDICT must be clean with a reason")
    return tuple(Finding(RENDERED_RECORD, defect) for defect in defects), len(passes), records


def survey(source: Source) -> Scan:
    markdown, references = _document_parts(source.paragraphs)
    document = reference_scan.read_document(markdown)
    reference_grade = reference_scan.survey(document, source.bar.signed)
    findings = list(source.package_findings)
    body = document.body
    body_words = len(WORD.findall(body))
    if body_words < source.bar.word_min:
        findings.append(
            Finding(
                WORD_RANGE,
                f"{body_words} body words is below {source.bar.word_min}",
            )
        )
    if len(references) < source.bar.reference_min:
        findings.append(
            Finding(
                REFERENCE_MINIMUM,
                f"{len(references)} references is below {source.bar.reference_min}",
            )
        )
    findings.extend(Finding(REFERENCE_DEFECT, finding.detail) for finding in reference_grade.findings)
    claim_keys, claim_numbers, claim_records = _claim_keys(source.claims)
    if not claim_records:
        findings.append(Finding(CLAIM_LEDGER, "claims.md has no CLAIM record"))
    for number in sorted(set(traceable_numeric_values(body)) - claim_numbers):
        findings.append(Finding(UNTRACED_NUMBER, f"{number} has no claim record"))
    reference_key_set = ReferenceKeySet.from_references(references)
    cited = read_citations(body, reference_key_set)
    claim_key_set = ReferenceKeySet.exact(claim_keys)
    for citation, candidates in zip(
        cited, citation_occurrence_keys(cited, body, reference_key_set), strict=True
    ):
        if not any(claim_key_set.resolves(candidate) for candidate in candidates):
            findings.append(
                Finding(
                    UNTRACED_CITATION,
                    f"{citation.author} {citation.year} has no claim record",
                )
            )
    rendered_findings, passes, rendered_records = _rendered_findings(source)
    findings.extend(rendered_findings)
    return Scan(
        len(source.paragraphs),
        body_words,
        len(references),
        claim_records,
        passes,
        rendered_records,
        tuple(findings),
    )


def format_report(scan: Scan, _source: str, show: bool = False) -> str:
    lines = [
        "assignment DOCX scan",
        "",
        f"  paragraphs read   {scan.paragraphs_read}",
        f"  body words        {scan.body_words}",
        f"  references read   {scan.references_read}",
        f"  claim records     {scan.claim_records}",
        f"  retained passes   {scan.retained_passes}",
        f"  rendered records  {scan.rendered_records}",
        "",
    ]
    lines.extend(
        f"{row}: {sum(finding.kind == row for finding in scan.findings)}"
        for row in ROWS
    )
    if show:
        lines.extend(("", "findings:"))
        lines.extend(f"  {finding.kind}: {finding.detail}" for finding in scan.findings)
    return "\n".join(lines)


def grade(source: Source, parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scan = survey(source)
    submission = parsed.value("--submission")
    aar_failed, aar_report = aar_scan.completion_gate(
        source.root, submission
    )
    gate_failed, gate_report = (
        False,
        f"submission gates: {NOT_GRADED} - --submission was not supplied",
    )
    if submission is not None:
        gate_failed, gate_report = assignment_submission.completion_gate(
            source.root, source.docx, submission=submission
        )
    grade = run_grader.Grade(
        scan=scan,
        source=str(source.root),
        findings_failed=bool(scan.findings) or aar_failed or gate_failed,
        coverage_failed=not source.paragraphs,
        diagnostics=("DOCX findings require review",) if scan.findings else (),
        reports=(gate_report, aar_report),
    )
    return voice_model_identity.apply_completion_gate(
        grade, source.root, submission
    )


GRADER = run_grader.Grader(
    usage="usage: assignment_docx_scan.py <run directory> --docx <Word file> [--show] [--submission <key>]",
    load=load,
    grade=grade,
    format_report=format_report,
    options=(
        run_grader.Option("--docx", takes_value=True, missing_value="--docx needs a Word file", repeatable=False),
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
