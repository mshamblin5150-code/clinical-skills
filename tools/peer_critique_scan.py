#!/usr/bin/env python3
"""Grade one peer clinical critique in a ``scratch/runs/<run-key>/`` directory.

The artifact is ``critique.md``: one scholarly response to one classmate, written
under the eight headings the course spec fixes. Default output is counts only.
``--show`` includes finding detail and may name classmates, so its output is
private working material and must not be pasted.

Exit 0 means the scanned critique passes, 1 means at least one finding, and 2
means the run could not be completely scanned. The roster coverage ceiling is
every ``posts/*.md`` file carrying one ``AUTHOR:`` line; other post layouts are
unread.

**The word ceiling is reported and never graded.** The spec states a range, and
the house rule is that no stated maximum is honored, so the floor is a finding
and the ceiling is a count a reader weighs.

What a clean run does not establish is declared by ``NOT_REACHED``. The module
owns that complete inventory; this docstring copies no row from it.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from discussion_artifact import (
    CLAIM_BLOCK,
    NUMBER,
    RESTATEMENT,
    WORD,
    citation_occurrence_keys,
    read_citations,
    read_reference_section,
    reference_keys,
    strip_discussion_markers,
)
import run_grader
from run_grader import NOT_GRADED, EvidenceDisposition
import aar_scan

EXPECTED_COMPLETION_CHECKS = (aar_scan.EXPECTED_ROW,)


MISSING_HEADING = "missing-heading"
EMPTY_HEADING = "empty-heading"
HEADING_ORDER = "heading-order"
ADDRESSED_NAME = "addressed-name"
WORD_FLOOR = "word-floor"
REFERENCE_MINIMUM = "reference-minimum"
UNRESOLVED_CITATION = "unresolved-citation"
UNTRACED_NUMBER = "untraced-number"
MISSING_POSTED_READING = "missing-posted-reading"
UNKNOWN_VERDICT = "unknown-verdict"
BARE_VERDICT = "bare-verdict"

#: The floor the spec states. A critique under it has not answered eight headings.
WORD_FLOOR_COUNT = 500
#: The expectation the spec states. Reported, never graded -- see the module docstring.
WORD_CEILING_COUNT = 750
REFERENCE_FLOOR_COUNT = 2

#: The eight headings, in the order the course spec lists them. The order is the
#: spec's own and a critique that answers them out of order is still answering
#: them, so the row reports the transposition rather than the absence.
REQUIRED_HEADINGS = (
    "Clinical Assessment",
    "Clinical Reasoning",
    "Diagnostic Interpretation",
    "Pharmacotherapeutics",
    "Evidence-Based Practice",
    "Preventive Care",
    "Patient Education",
    "Professional Practice",
)

ROWS = {
    MISSING_HEADING: "every required heading appears in the critique",
    EMPTY_HEADING: "every required heading carries prose beneath it",
    HEADING_ORDER: "the headings appear in the order the spec lists them",
    ADDRESSED_NAME: "the addressed first name is on the run roster",
    WORD_FLOOR: f"the critique contains at least {WORD_FLOOR_COUNT} words",
    REFERENCE_MINIMUM: f"the critique carries at least {REFERENCE_FLOOR_COUNT} references",
    UNRESOLVED_CITATION: "every in-text citation resolves to the critique's own list",
    UNTRACED_NUMBER: "every body numeral traces to a believed claim record",
    MISSING_POSTED_READING: "the posted critique has been reread and recorded",
    UNKNOWN_VERDICT: "every posted reading carries a recognized verdict",
    BARE_VERDICT: "every posted reading verdict carries substantive text",
}
KINDS = tuple(ROWS)

REFERENCE_LABEL = re.compile(r"(?mi)^\*\*References\*\*\s*$")
AUTHOR_FIELD = re.compile(r"(?mi)^AUTHOR\s*:\s*(?P<value>[^\n]+)$")
#: A heading is a Markdown heading line or a bold-only line. The critique is
#: typed into an LMS box that has no renderer, so the bold form is what a posted
#: critique carries; the heading form is what its rendered sibling carries.
SECTION_HEADING = re.compile(r"(?m)^[ \t]*(?:#{1,6}[ \t]+|\*\*)(?P<name>[^\n*#]+?)(?:\*\*)?[ \t]*$")
RECOGNIZED_VERDICTS = ("matches", "diverges")

NO_RUN_DIRECTORY = "no run directory"
NO_CRITIQUE = "no critique in the run"
NO_ROSTER = "no roster post carries an AUTHOR line"
REFUSED_LABEL = "critique reference label refused"
INVALID_INVOCATION = "invalid invocation"
EXIT_2_LIMBS = (INVALID_INVOCATION, NO_RUN_DIRECTORY, NO_CRITIQUE, NO_ROSTER, REFUSED_LABEL)

DECLARED_LIMITS = (
    (
        "whether an absent item was ever in the case the assignment supplied",
        "The command reads the critique and never the case material, so it cannot tell a classmate's omission from a datum the assignment never gave anyone.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a named diagnosis that can kill was genuinely missed",
        "The row set grades structure, sourcing and tracing; deciding that a differential omission is clinically dangerous is the reading this critique exists to carry.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a heading's prose answers the sub-questions the spec states under it",
        "The command proves a required heading exists and carries words beneath it, and cannot judge whether those words address medication monitoring or cultural humility.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "whether the critique credits the classmate before it corrects them",
        "Leading with what is right is a rubric expectation and a register judgment; no mechanical row can separate a credit from a concession offered in bad faith.",
        EvidenceDisposition.DECLARED_READING,
    ),
    (
        "whether a believed record's restatement supports the number traced from it",
        "The tracing walk matches numeric tokens against claim records and never judges whether the record's restatement supports the fact the critique asserts.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "whether the critique's word count should have been cut to the stated ceiling",
        "The ceiling is reported rather than graded because no stated maximum is honored, so a long critique is a choice the clinician makes and never a finding here.",
        EvidenceDisposition.BEHAVIOR,
    ),
    (
        "whether a literal ampersand survives the surface the critique is posted to",
        "The count is reported from the artifact, and whether a given LMS box double-escapes it is a property of that page rather than of this file.",
        EvidenceDisposition.BEHAVIOR,
    ),
)
NOT_REACHED = tuple((subject, reason) for subject, reason, _ in DECLARED_LIMITS)


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    artifact: str
    detail: str


@dataclass(frozen=True)
class RunSource:
    path: Path
    critique: str
    body: str
    references: tuple[str, ...]
    refused_label: str | None
    roster: tuple[str, ...]
    posts_total: int
    claims: str
    reread: str


@dataclass(frozen=True)
class Scan:
    headings_found: int
    headings_expected: int
    posts_read: int
    posts_total: int
    words: int | None
    word_ceiling: int
    references: int | None
    citations: int | None
    numeric_claims: int | None
    ampersands: int | None
    reference_boundary_graded: bool
    findings: tuple[Finding, ...] = ()


def _heading_lines(text: str) -> list[str]:
    return [found.group("name").strip() for found in SECTION_HEADING.finditer(text)]


def _section_text(body: str, heading: str) -> str:
    """The prose beneath ``heading``, up to the next recognized heading."""

    found = next(
        (
            match
            for match in SECTION_HEADING.finditer(body)
            if match.group("name").strip().casefold() == heading.casefold()
        ),
        None,
    )
    if found is None:
        return ""
    rest = body[found.end() :]
    nxt = SECTION_HEADING.search(rest)
    return (rest[: nxt.start()] if nxt else rest).strip()


def _heading_findings(source: RunSource) -> tuple[Finding, ...]:
    present = {name.casefold() for name in _heading_lines(source.body)}
    findings: list[Finding] = []
    for heading in REQUIRED_HEADINGS:
        if heading.casefold() not in present:
            findings.append(Finding(MISSING_HEADING, "critique.md", heading))
        elif not _section_text(source.body, heading):
            findings.append(Finding(EMPTY_HEADING, "critique.md", heading))
    seen = [
        name
        for name in _heading_lines(source.body)
        if name.casefold() in {h.casefold() for h in REQUIRED_HEADINGS}
    ]
    expected = [h for h in REQUIRED_HEADINGS if h.casefold() in {s.casefold() for s in seen}]
    if [s.casefold() for s in seen] != [e.casefold() for e in expected]:
        findings.append(Finding(HEADING_ORDER, "critique.md", "headings are not in spec order"))
    return tuple(findings)


def _address_findings(source: RunSource) -> tuple[Finding, ...]:
    opening = next(
        (line.strip() for line in source.body.splitlines() if line.strip()),
        "",
    )
    firsts = {name.split()[0] for name in source.roster if name.split()}
    if not any(opening.startswith(f"{first},") for first in firsts):
        return (Finding(ADDRESSED_NAME, "critique.md", "opening addresses no roster first name"),)
    return ()


def _word_count(body: str) -> int:
    return len(WORD.findall(strip_discussion_markers(body)))


def _believed_tokens(claims: str) -> set[str]:
    tokens: set[str] = set()
    for block in CLAIM_BLOCK.finditer(claims):
        text = block.group("block")
        heading = text.splitlines()[0] if text.splitlines() else ""
        restatement = " ".join(found.group("value") for found in RESTATEMENT.finditer(text))
        tokens.update(NUMBER.findall(heading))
        tokens.update(NUMBER.findall(restatement))
    return tokens


def _numeric_findings(source: RunSource) -> tuple[Finding, ...]:
    believed = _believed_tokens(source.claims)
    citations = read_citations(source.body, _reference_key_set(source))
    spans = {(citation.start, citation.end) for citation in citations}
    findings = []
    for found in NUMBER.finditer(source.body):
        if any(start <= found.start() < end for start, end in spans):
            continue
        if found.group(0) not in believed:
            findings.append(Finding(UNTRACED_NUMBER, "critique.md", found.group(0)))
    return tuple(findings)


def _reference_key_set(source: RunSource) -> frozenset[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for reference in source.references:
        keys.update(reference_keys(reference))
    return frozenset(keys)


def _citation_findings(source: RunSource) -> tuple[Finding, ...]:
    references = _reference_key_set(source)
    citations = read_citations(source.body, references)
    return tuple(
        Finding(
            UNRESOLVED_CITATION,
            "critique.md",
            f"{citation.author}, {citation.year} has no matching reference",
        )
        for citation, keys in zip(citations, citation_occurrence_keys(citations))
        if not any(key in references for key in keys)
    )


def _reread_findings(source: RunSource) -> tuple[Finding, ...]:
    from discussion_artifact import read_posted_readings

    readings = read_posted_readings(source.reread)
    if not readings:
        return (Finding(MISSING_POSTED_READING, "critique.md", "no posted reading recorded"),)
    findings = []
    for reading in readings:
        verdict = (reading.verdict or "").strip().casefold()
        if verdict not in RECOGNIZED_VERDICTS:
            findings.append(Finding(UNKNOWN_VERDICT, reading.artifact, verdict or "absent"))
        elif not (reading.verdict_detail or "").strip():
            findings.append(Finding(BARE_VERDICT, reading.artifact, verdict))
    return tuple(findings)


def survey(source: RunSource) -> Scan:
    """Grade one run and return its counts and findings."""

    graded = source.refused_label is None
    structural = _heading_findings(source) + _address_findings(source) + _reread_findings(source)
    if not graded:
        return Scan(
            headings_found=len(REQUIRED_HEADINGS) - sum(
                finding.kind == MISSING_HEADING for finding in structural
            ),
            headings_expected=len(REQUIRED_HEADINGS),
            posts_read=len(source.roster),
            posts_total=source.posts_total,
            words=None,
            word_ceiling=WORD_CEILING_COUNT,
            references=None,
            citations=None,
            numeric_claims=None,
            ampersands=None,
            reference_boundary_graded=False,
            findings=structural,
        )
    words = _word_count(source.body)
    citations = read_citations(source.body, _reference_key_set(source))
    findings = list(structural)
    if words < WORD_FLOOR_COUNT:
        findings.append(Finding(WORD_FLOOR, "critique.md", f"{words} words"))
    if len(source.references) < REFERENCE_FLOOR_COUNT:
        findings.append(
            Finding(REFERENCE_MINIMUM, "critique.md", f"{len(source.references)} references")
        )
    findings.extend(_citation_findings(source))
    findings.extend(_numeric_findings(source))
    return Scan(
        headings_found=len(REQUIRED_HEADINGS) - sum(
            finding.kind == MISSING_HEADING for finding in findings
        ),
        headings_expected=len(REQUIRED_HEADINGS),
        posts_read=len(source.roster),
        posts_total=source.posts_total,
        words=words,
        word_ceiling=WORD_CEILING_COUNT,
        references=len(source.references),
        citations=len(citations),
        numeric_claims=len(_believed_tokens(source.claims)),
        ampersands=source.body.count("&"),
        reference_boundary_graded=True,
        findings=tuple(findings),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """Render one scan as counts, adding finding detail only under ``show``."""

    graded = scan.reference_boundary_graded
    lines = [
        f"peer critique in {source}",
        f"required headings: {scan.headings_found} of {scan.headings_expected}",
        f"roster posts read: {scan.posts_read} of {scan.posts_total}",
        f"words: {scan.words if graded else NOT_GRADED}",
        (
            f"word ceiling: {scan.word_ceiling} (reported, {NOT_GRADED})"
            if graded
            else f"word ceiling: {NOT_GRADED}"
        ),
        f"references: {scan.references if graded else NOT_GRADED}",
        f"citations: {scan.citations if graded else NOT_GRADED}",
        f"claim records: {scan.numeric_claims if graded else NOT_GRADED}",
        (
            f"literal ampersands: {scan.ampersands} (reported, {NOT_GRADED})"
            if graded
            else f"literal ampersands: {NOT_GRADED}"
        ),
        f"findings: {len(scan.findings)}",
    ]
    reference_rows = {
        WORD_FLOOR,
        REFERENCE_MINIMUM,
        UNRESOLVED_CITATION,
        UNTRACED_NUMBER,
    }
    for kind in ROWS:
        if kind in reference_rows and not graded:
            lines.append(f"{kind}: {NOT_GRADED}")
        else:
            lines.append(f"{kind}: {sum(finding.kind == kind for finding in scan.findings)}")
    if show:
        lines.extend(
            f"{finding.kind}: {finding.artifact}: {finding.detail}" for finding in scan.findings
        )
    return "\n".join(lines)


def load(parsed: run_grader.Parsed) -> RunSource:
    directory = Path(parsed.source)
    if not directory.is_dir():
        raise run_grader.SourceError(
            f"{parsed.source} is not a run directory", exit_2_limb=NO_RUN_DIRECTORY
        )
    critique_path = directory / "critique.md"
    if not critique_path.is_file():
        raise run_grader.SourceError(
            f"no critique.md in {directory.name}", exit_2_limb=NO_CRITIQUE
        )
    try:
        critique = critique_path.read_text(encoding="utf-8")
        posts = sorted((directory / "posts").glob("*.md"))
        roster = []
        for path in posts:
            found = AUTHOR_FIELD.search(path.read_text(encoding="utf-8"))
            if found:
                roster.append(found.group("value").strip())
        claims_path = directory / "claims.md"
        claims = claims_path.read_text(encoding="utf-8") if claims_path.is_file() else ""
        reread_path = directory / "reread.md"
        reread = reread_path.read_text(encoding="utf-8") if reread_path.is_file() else ""
    except (OSError, UnicodeError, ValueError) as failure:
        raise run_grader.SourceError(
            f"could not read the run: {failure}", exit_2_limb=NO_RUN_DIRECTORY
        ) from failure
    if not roster:
        raise run_grader.SourceError(
            f"no posts/*.md in {directory.name} carries an AUTHOR line", exit_2_limb=NO_ROSTER
        )
    section = read_reference_section(critique, REFERENCE_LABEL)
    return RunSource(
        path=directory,
        critique=critique,
        body=section.body,
        references=section.references,
        refused_label=section.refused_label,
        roster=tuple(roster),
        posts_total=len(posts),
        claims=claims,
        reread=reread,
    )


def grade(source: RunSource, parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scanned = survey(source)
    structural_kinds = {
        MISSING_HEADING,
        EMPTY_HEADING,
        HEADING_ORDER,
        ADDRESSED_NAME,
        MISSING_POSTED_READING,
        UNKNOWN_VERDICT,
        BARE_VERDICT,
    }
    structural_failed = any(finding.kind in structural_kinds for finding in scanned.findings)
    aar_failed, aar_report = aar_scan.completion_gate(source.path, parsed.value("--submission"))
    return run_grader.Grade(
        scan=scanned,
        source=str(source.path),
        findings_failed=(
            bool(scanned.findings)
            and (scanned.reference_boundary_graded or structural_failed)
        )
        or aar_failed,
        coverage_failed=not scanned.reference_boundary_graded,
        coverage_limbs=(REFUSED_LABEL,) if not scanned.reference_boundary_graded else (),
        diagnostics=(
            (f"refused reference label in critique.md: {source.refused_label}",)
            if source.refused_label is not None
            else ()
        ),
        reports=(aar_report,),
    )


GRADER = run_grader.Grader(
    usage="usage: peer_critique_scan.py <a run directory> [--show] [--submission <key>]",
    load=load,
    grade=grade,
    format_report=format_report,
    options=(
        run_grader.Option("--show", repeatable=False),
        run_grader.Option(
            "--submission",
            takes_value=True,
            missing_value="--submission needs a key",
            repeatable=False,
        ),
    ),
    allow_extra_positionals=False,
    exit_2_limbs=EXIT_2_LIMBS,
    invalid_invocation_limb=INVALID_INVOCATION,
)


def main(argv: list[str]) -> int:
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
