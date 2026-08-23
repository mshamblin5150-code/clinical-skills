#!/usr/bin/env python3
"""Grade one initial post against its signed mechanical bar.

The source is one ``scratch/runs/<course>-<module>-discussion/`` directory and ``--draft``
names the Markdown handoff under ``output/discussions/``. Default output is
counts only. ``--show`` includes finding detail and remains private working
material. Exit 0 means the mechanical rows pass, 1 means at least one finding,
and 2 means the run could not be completely scanned.

``--docx`` names the rendered handoff and grades that its document XML carries no
``Heading{N}`` paragraph style. Without the option, that row reports ``not graded``;
an absent input never masquerades as a passing count.

What a clean run does not establish is ``NOT_REACHED``. The tuple is the one
reader-facing inventory of this command's limits; this docstring deliberately
copies none of its rows.
"""

from __future__ import annotations

import re
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from xml.etree import ElementTree

from discussion_artifact import (
    AMPLIFICATION,
    CLAIM_BLOCK,
    CLAIM_REFERENCE,
    NUMBER,
    RESTATEMENT,
    WORD,
    citation_occurrence_keys,
    read_citations,
    reference_key,
    reference_keys,
    split_references,
)
import run_grader
import coursework_run


WORD_FLOOR = "word-floor"
REFERENCE_MINIMUM = "reference-minimum"
UNTRACED_NUMBER = "untraced-number"
UNTRACED_CITATION = "untraced-citation"
BOLD_HEADINGS = "bold-headings"
ROWS = {
    WORD_FLOOR: "the post reaches the signed word floor",
    REFERENCE_MINIMUM: "the post reaches the signed reference minimum",
    UNTRACED_NUMBER: "every graded body number traces to claims.md",
    UNTRACED_CITATION: "every in-text citation has its own claim record",
    BOLD_HEADINGS: "the rendered document carries no named heading style",
}
KINDS = tuple(ROWS)

NOT_REACHED = (
    (
        "whether the bar transcription is complete",
        "The command can read structured values but cannot compare the quoted bar with the live topic and syllabus pages.",
    ),
    (
        "whether the topic overrides the syllabus",
        "The command receives one signed result and cannot decide whether an observed topic statement should supersede the syllabus.",
    ),
    (
        "whether a prose bar element is satisfied",
        "A bar element such as including an ISBN has no honest general text pattern and remains an independent reading.",
    ),
    (
        "whether a reference actually supports the required proposition",
        "Counting an entry cannot establish that it supports the proposition required by the signed bar.",
    ),
    (
        "whether a claim record describes the cited sentence",
        "A source-and-year join establishes record presence but cannot decide whether the claim heading faithfully describes that sentence.",
    ),
)

FIELD = re.compile(r"(?mi)^(?P<name>[A-Z][A-Z-]+)\s*:\s*(?P<value>[^\n]+?)\s*$")
REFERENCE_HEADING = re.compile(r"(?mi)^#{1,6}\s+References\s*$")
MARKDOWN_HEADING = re.compile(r"(?m)^\s*#{1,6}\s+.*$")
STATUTE = re.compile(
    r"(?i)(?:\b\d+\s+)?C\.\s*F\.\s*R\.\s*(?:§+|sections?\s+)?\s*\d+(?:\.\d+)*"
    r"|§+\s*\d+(?:\.\d+)*"
)
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
class RunSource:
    path: Path
    draft: Path
    body: str
    references: tuple[str, ...]
    claims: str
    bar: Bar
    docx: Path | None
    named_heading_styles: tuple[str, ...]


@dataclass(frozen=True)
class ClaimRecord:
    numbers: frozenset[str]
    references: frozenset[tuple[str, str]]


@dataclass(frozen=True)
class Scan:
    words: int
    word_floor: int
    word_ceiling: int | None
    references: int
    reference_minimum: int
    numeric_claims: int
    citations: int
    amplifications: int
    docx_graded: bool
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
    return MARKDOWN_HEADING.sub("", AMPLIFICATION.sub("", body))


def _numeric_values(body: str) -> tuple[str, ...]:
    cleaned = body
    citations = read_citations(body)
    for citation in reversed(citations):
        cleaned = cleaned[: citation.start] + cleaned[citation.end :]
    cleaned = PAGE_LOCATOR.sub("", cleaned)
    cleaned = STATUTE.sub("", cleaned)
    return tuple(NUMBER.findall(AMPLIFICATION.sub("", cleaned)))


def _claim_blocks(claims: str) -> tuple[str, ...]:
    return tuple(match.group("block") for match in CLAIM_BLOCK.finditer(claims))


def _citation_keys(body: str) -> tuple[tuple[tuple[str, str], ...], ...]:
    return citation_occurrence_keys(read_citations(body))


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


def _maximum_record_matching(candidates: tuple[tuple[int, ...], ...]) -> set[int]:
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

    matched: set[int] = set()
    for requirement in range(len(candidates)):
        if assign(requirement, set()):
            matched.add(requirement)
    return matched


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEADING_STYLE = re.compile(r"Heading\d+")


def _docx_heading_styles(path: Path) -> tuple[str, ...]:
    if not path.is_file():
        raise run_grader.SourceError(f"no rendered document at {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            document = ElementTree.fromstring(archive.read("word/document.xml"))
    except (OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as failure:
        raise run_grader.SourceError(
            f"could not read the rendered document: {failure}"
        ) from failure
    return tuple(
        value
        for node in document.iter(W + "pStyle")
        if (value := node.get(W + "val")) is not None
        and HEADING_STYLE.fullmatch(value)
    )


def load(parsed: run_grader.Parsed) -> RunSource:
    root = Path(parsed.source)
    if not root.is_dir():
        raise run_grader.SourceError(f"no run directory at {root}")
    bar_path = root / "bar.md"
    claims_path = root / "claims.md"
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
        run_key = coursework_run.key_of(draft.stem)
        expected = coursework_run.runs_root() / run_key
        if coursework_run.is_run_directory(root) and root.name != run_key:
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
        body, references = split_references(
            draft.read_text(encoding="utf-8"), REFERENCE_HEADING
        )
    except (OSError, UnicodeError) as failure:
        raise run_grader.SourceError(f"could not read the discussion-post run: {failure}") from failure
    named_heading_styles = _docx_heading_styles(docx) if docx is not None else ()
    return RunSource(
        root,
        draft,
        body,
        references,
        claims,
        bar,
        docx,
        named_heading_styles,
    )


def survey(source: RunSource) -> Scan:
    words = len(WORD.findall(_countable_body(source.body)))
    numbers = _numeric_values(source.body)
    citations = _citation_keys(source.body)
    records = _claim_records(source.claims)
    findings: list[Finding] = []
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
    requirements: list[tuple[str, str, tuple[int, ...]]] = []
    number_occurrences: Counter[str] = Counter()
    for value in numbers:
        folded = value.casefold()
        number_occurrences[folded] += 1
        requirements.append(
            (
                UNTRACED_NUMBER,
                f"{folded} occurrence {number_occurrences[folded]} has no claim record",
                tuple(
                    index
                    for index, record in enumerate(records)
                    if folded in record.numbers
                ),
            )
        )
    for occurrence, keys in enumerate(citations, start=1):
        requirements.append(
            (
                UNTRACED_CITATION,
                f"citation occurrence {occurrence} has no source-matched claim record",
                tuple(
                    index
                    for index, record in enumerate(records)
                    if any(key in record.references for key in keys)
                ),
            )
        )
    matched = _maximum_record_matching(
        tuple(candidates for _, _, candidates in requirements)
    )
    for index, (kind, detail, _) in enumerate(requirements):
        if index not in matched:
            if kind == UNTRACED_NUMBER:
                findings.append(
                    Finding(UNTRACED_NUMBER, source.draft.name, detail)
                )
            else:
                findings.append(
                    Finding(UNTRACED_CITATION, source.draft.name, detail)
                )
    return Scan(
        words=words,
        word_floor=source.bar.word_floor,
        word_ceiling=source.bar.word_ceiling,
        references=len(source.references),
        reference_minimum=source.bar.reference_minimum,
        numeric_claims=len(numbers),
        citations=len(citations),
        amplifications=len(AMPLIFICATION.findall(source.body)),
        docx_graded=source.docx is not None,
        findings=tuple(findings),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    exceeded = scan.word_ceiling is not None and scan.words > scan.word_ceiling
    lines = [
        f"initial post in {source}",
        f"words: {scan.words} (floor {scan.word_floor})",
        f"word ceiling: {scan.word_ceiling if scan.word_ceiling is not None else 'none'}",
        f"word ceiling exceeded: {'yes' if exceeded else 'no'} (counted, never graded)",
        f"references: {scan.references} (minimum {scan.reference_minimum})",
        f"numeric claims: {scan.numeric_claims}",
        f"citations: {scan.citations}",
        f"amplifications: {scan.amplifications} (counted, never graded)",
        f"findings: {len(scan.findings)}",
    ]
    for kind in ROWS:
        if kind == BOLD_HEADINGS and not scan.docx_graded:
            lines.append(f"{kind}: not graded")
        else:
            lines.append(
                f"{kind}: {sum(finding.kind == kind for finding in scan.findings)}"
            )
    if show:
        lines.extend(
            f"{finding.kind}: {finding.artifact}: {finding.detail}"
            for finding in scan.findings
        )
    return "\n".join(lines)


def grade(source: RunSource, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scanned = survey(source)
    return run_grader.Grade(
        scan=scanned,
        source=str(source.path),
        findings_failed=bool(scanned.findings),
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
