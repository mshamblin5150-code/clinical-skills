#!/usr/bin/env python3
"""Grade discussion replies in one ``scratch/runs/<run-key>/`` directory.

Default output is counts only. ``--show`` includes finding details and may name
classmates, so its output is private working material and must not be pasted.
Exit 0 means the scanned replies pass, 1 means at least one finding, and 2 means
the run could not be completely scanned. The roster coverage ceiling is every
``posts/*.md`` file carrying one ``AUTHOR:`` line; other post layouts are unread.

What a clean run does not establish is declared by
``UNMARKED_INVOKED_SOURCE_LIMIT`` and ``INVOKED_PROPERTY_LIMIT``. The module
owns those limits; this docstring copies no part of either.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from discussion_artifact import (
    AMPLIFICATION,
    CLAIM_BLOCK,
    CLAIM_REFERENCE,
    NUMBER,
    INVOKED,
    REFERENCE_YEAR,
    RESTATEMENT,
    WORD,
    Citation,
    author_key,
    citation_occurrence_keys,
    invoked_source_has_substance,
    legal_reference_lacks_name,
    read_citations,
    read_invoked_sources,
    read_reference_section,
    reference_key,
    reference_keys,
    split_references,
    strip_discussion_markers,
)
import run_grader


ADDRESSED_NAME = "addressed-name"
WORD_FLOOR = "word-floor"
REFERENCE_MINIMUM = "reference-minimum"
UNRESOLVED_CITATION = "unresolved-citation"
UNTRACED_NUMBER = "untraced-number"
RESPENT_SOURCE = "respent-source"
INVOKED_PROPERTY = "invoked-property"
LEGAL_REFERENCE_NAME = "legal-reference-name"
ROWS = {
    ADDRESSED_NAME: "the addressed first name is on the run roster",
    WORD_FLOOR: "the reply contains at least 100 words",
    REFERENCE_MINIMUM: "the reply contains at least one reference",
    UNRESOLVED_CITATION: "every in-text citation resolves within the reply",
    UNTRACED_NUMBER: "every body number traces to claims.md",
    RESPENT_SOURCE: "a later reply does not spend an earlier reply's source",
    INVOKED_PROPERTY: "every invoked source names a property beyond its domain noun",
    LEGAL_REFERENCE_NAME: "every legal reference entry names its regulation",
}
KINDS = tuple(ROWS)

UNMARKED_INVOKED_SOURCE_LIMIT = (
    "whether every invoked source was marked",
    "The command can grade only INVOKED markers that exist and cannot see an invoked source the drafter never marked.",
)
INVOKED_PROPERTY_LIMIT = (
    "whether an invoked property is a grammatical behavior clause",
    "The row refuses an empty field or lexical restatement of the domain noun; the clinician judges whether the remaining words state the real behavior.",
)

REFERENCE_LABEL = re.compile(r"(?mi)^\*\*References\*\*\s*$")
AUTHOR = re.compile(r"(?mi)^AUTHOR\s*:\s*(?P<name>[^\n]+?)\s*$")
CLAIM_TARGET = re.compile(r"^\[REPLY:\s*(?P<target>[^\]]+)\]\s*(?P<claim>.*)$", re.IGNORECASE)


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    response: str
    detail: str


@dataclass(frozen=True)
class Reply:
    path: Path
    text: str
    body: str
    references: tuple[str, ...]
    refused_label: str | None


@dataclass(frozen=True)
class RunSource:
    path: Path
    replies: tuple[Reply, ...]
    claims: str
    roster: tuple[str, ...]
    posts_total: int


@dataclass(frozen=True)
class Scan:
    responses: int
    posts_read: int
    posts_total: int
    words: int | None
    references: int | None
    citations: int | None
    numeric_claims: int | None
    invoked_sources: int | None
    pre_496_markers: int | None
    reference_boundary_graded: bool
    findings: tuple[Finding, ...] = ()


def _split_reply(path: Path) -> Reply:
    text = path.read_text(encoding="utf-8")
    section = read_reference_section(text, REFERENCE_LABEL)
    return Reply(
        path=path,
        text=text,
        body=section.body,
        references=section.references,
        refused_label=section.refused_label,
    )


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _target_name(reply: Reply, roster: tuple[str, ...]) -> str | None:
    target = reply.path.stem.removeprefix("response-")
    matches = [
        name
        for name in roster
        if target in {_slug(name), _slug(name.split()[0])}
    ]
    return matches[0] if len(matches) == 1 else None


def _address_finding(reply: Reply, roster: tuple[str, ...]) -> Finding | None:
    target = _target_name(reply, roster)
    opening = next(
        (line.strip() for line in reply.body.splitlines() if line.strip() and not line.lstrip().startswith("<!--")),
        "",
    )
    if target is None:
        return Finding(ADDRESSED_NAME, reply.path.name, "filename target is not unique on the roster")
    first = target.split()[0]
    if not opening.startswith(f"{first},"):
        return Finding(ADDRESSED_NAME, reply.path.name, f"opening does not address {first}")
    return None


def _word_finding(reply: Reply) -> Finding | None:
    count = len(WORD.findall(strip_discussion_markers(reply.body)))
    if count < 100:
        return Finding(WORD_FLOOR, reply.path.name, f"{count} words")
    return None


def _reference_finding(reply: Reply, claims: str) -> Finding | None:
    if not _claimed_references(reply, claims):
        return Finding(
            REFERENCE_MINIMUM,
            reply.path.name,
            "no APA author-year reference backed by this reply's claim record",
        )
    return None


def _valid_references(reply: Reply) -> tuple[str, ...]:
    valid: list[str] = []
    for entry in reply.references:
        year = REFERENCE_YEAR.search(entry)
        if (
            year
            and author_key(entry[: year.start()].rstrip(". "))
            and re.search(r"[A-Za-z]{2,}", entry[year.end() :])
        ):
            valid.append(entry)
    return tuple(valid)


def _scoped_claim_blocks(claims: str, target: str) -> tuple[tuple[str, str], ...]:
    scoped_blocks: list[tuple[str, str]] = []
    for match in CLAIM_BLOCK.finditer(claims):
        block = match.group("block")
        claim_line = block.splitlines()[0] if block.splitlines() else ""
        scoped = CLAIM_TARGET.match(claim_line)
        if scoped is not None and _slug(scoped.group("target")) == target:
            scoped_blocks.append((scoped.group("claim"), block))
    return tuple(scoped_blocks)


def _claimed_references(reply: Reply, claims: str) -> tuple[str, ...]:
    target = reply.path.stem.removeprefix("response-")
    ledger_keys = {
        _source_key(reference.group("value").replace("\n", " "))
        for _claim, block in _scoped_claim_blocks(claims, target)
        for reference in [CLAIM_REFERENCE.search(block)]
        if reference is not None
    }
    return tuple(
        reference
        for reference in _valid_references(reply)
        if _source_key(reference) in ledger_keys
    )


def _reference_keys(reply: Reply) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for entry in _valid_references(reply):
        keys.update(reference_keys(entry))
    return keys


def _legal_reference_name_findings(reply: Reply) -> tuple[Finding, ...]:
    return tuple(
        Finding(
            LEGAL_REFERENCE_NAME,
            reply.path.name,
            "legal reference has a section but no regulation name",
        )
        for entry in _valid_references(reply)
        if legal_reference_lacks_name(entry)
    )


def _citation_findings(reply: Reply, citations: tuple[Citation, ...]) -> tuple[Finding, ...]:
    references = _reference_keys(reply)
    return tuple(
        Finding(
            UNRESOLVED_CITATION,
            reply.path.name,
            f"{citation.author}, {citation.year} has no matching reference",
        )
        for citation, keys in zip(citations, citation_occurrence_keys(citations))
        if not any(key in references for key in keys)
    )


def _numeric_values(reply: Reply, citations: tuple[Citation, ...]) -> tuple[str, ...]:
    body = _without_citation_years(reply.body, citations)
    return tuple(NUMBER.findall(strip_discussion_markers(body)))


def _number_findings(
    reply: Reply, citations: tuple[Citation, ...], claims: str
) -> tuple[Finding, ...]:
    traced: set[str] = set()
    target = reply.path.stem.removeprefix("response-")
    for claim, block in _scoped_claim_blocks(claims, target):
        restatement = RESTATEMENT.search(block)
        trace_text = claim + "\n" + (
            restatement.group("value") if restatement else ""
        )
        traced.update(value.casefold() for value in NUMBER.findall(trace_text))
    return tuple(
        Finding(UNTRACED_NUMBER, reply.path.name, f"{value} is absent from claims.md")
        for value in dict.fromkeys(_numeric_values(reply, citations))
        if value.casefold() not in traced
    )


def _source_key(reference: str) -> str:
    doi = re.search(r"(?i)\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", reference)
    if doi:
        return doi.group(0).casefold().rstrip(".")
    url = re.search(r"(?i)https?://\S+", reference)
    if url:
        return re.sub(r"^https?://", "", url.group(0).casefold()).rstrip("/.,)")
    return re.sub(r"[^a-z0-9]", "", reference.casefold())


def _reuse_findings(replies: tuple[Reply, ...]) -> tuple[Finding, ...]:
    seen: dict[str, str] = {}
    findings: list[Finding] = []
    for reply in replies:
        for reference in _valid_references(reply):
            key = _source_key(reference)
            if key in seen:
                findings.append(
                    Finding(
                        RESPENT_SOURCE,
                        reply.path.name,
                        f"source already appears in {seen[key]}",
                    )
                )
            else:
                seen[key] = reply.path.name
    return tuple(findings)


def _invoked_findings(reply: Reply) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    for source in read_invoked_sources(reply.body):
        if not source.domain:
            detail = "invoked source has an empty domain"
        elif not source.property:
            detail = "invoked source has an empty property"
        elif not invoked_source_has_substance(source):
            detail = "invoked property only restates the domain"
        else:
            continue
        findings.append(Finding(INVOKED_PROPERTY, reply.path.name, detail))
    return tuple(findings)


def _without_citation_years(body: str, citations: tuple[Citation, ...]) -> str:
    cleaned = body
    for citation in reversed(citations):
        span = cleaned[citation.start : citation.end]
        cleaned = cleaned[: citation.start] + re.sub(r"\d", "", span) + cleaned[citation.end :]
    return cleaned


def load(parsed: run_grader.Parsed) -> RunSource:
    root = Path(parsed.source)
    if not root.is_dir():
        raise run_grader.SourceError(f"no run directory at {root}")
    board_paths = sorted(root.glob("board-*.md"))
    posts = root / "posts"
    claims_path = root / "claims.md"
    if not board_paths or not posts.is_dir() or not claims_path.is_file():
        raise run_grader.SourceError(
            "run needs board-<date>.md, posts/, and claims.md before it can be scanned"
        )
    response_paths = sorted(root.glob("response-*.md"))
    if not response_paths:
        raise run_grader.SourceError("run contains no response-<name>.md files")
    post_paths = sorted(posts.glob("*.md"))
    try:
        replies = tuple(_split_reply(path) for path in response_paths)
        claims = claims_path.read_text(encoding="utf-8")
        roster = tuple(
            match.group("name").strip()
            for path in post_paths
            for match in [AUTHOR.search(path.read_text(encoding="utf-8"))]
            if match
        )
    except (OSError, UnicodeError) as failure:
        raise run_grader.SourceError(f"could not read the run: {failure}") from failure
    if len(roster) != len(post_paths):
        raise run_grader.SourceError(
            f"roster read {len(roster)} of {len(post_paths)} post files; "
            f"unread remainder {len(post_paths) - len(roster)}"
        )
    if not roster:
        raise run_grader.SourceError("roster read 0 of 0 post files; unread remainder 0")
    return RunSource(
        path=root,
        replies=replies,
        claims=claims,
        roster=roster,
        posts_total=len(post_paths),
    )


def survey(source: RunSource) -> Scan:
    reference_boundary_graded = not any(reply.refused_label for reply in source.replies)
    if not reference_boundary_graded:
        address_findings = tuple(
            finding
            for reply in source.replies
            for finding in (_address_finding(reply, source.roster),)
            if finding is not None
        )
        return Scan(
            responses=len(source.replies),
            posts_read=len(source.roster),
            posts_total=source.posts_total,
            words=None,
            references=None,
            citations=None,
            numeric_claims=None,
            invoked_sources=None,
            pre_496_markers=None,
            reference_boundary_graded=False,
            findings=address_findings,
        )
    citations = tuple(read_citations(reply.body) for reply in source.replies)
    base_findings = tuple(
        finding
        for reply in source.replies
        for finding in (
            _address_finding(reply, source.roster),
            _word_finding(reply),
            _reference_finding(reply, source.claims),
        )
        if finding is not None
    )
    findings = base_findings + tuple(
        finding
        for reply in source.replies
        for finding in _legal_reference_name_findings(reply)
    ) + tuple(
        finding
        for reply, reply_citations in zip(source.replies, citations)
        for finding in _citation_findings(reply, reply_citations)
    ) + tuple(
        finding
        for reply, reply_citations in zip(source.replies, citations)
        for finding in _number_findings(reply, reply_citations, source.claims)
    ) + _reuse_findings(source.replies) + tuple(
        finding
        for reply in source.replies
        for finding in _invoked_findings(reply)
    )
    return Scan(
        responses=len(source.replies),
        posts_read=len(source.roster),
        posts_total=source.posts_total,
        words=sum(
            len(WORD.findall(strip_discussion_markers(reply.body)))
            for reply in source.replies
        ),
        references=sum(
            len(_claimed_references(reply, source.claims)) for reply in source.replies
        ),
        citations=sum(len(reply_citations) for reply_citations in citations),
        numeric_claims=sum(
            len(_numeric_values(reply, reply_citations))
            for reply, reply_citations in zip(source.replies, citations)
        ),
        invoked_sources=sum(
            len(read_invoked_sources(reply.body)) for reply in source.replies
        ),
        pre_496_markers=sum(
            len(AMPLIFICATION.findall(reply.body)) for reply in source.replies
        ),
        reference_boundary_graded=True,
        findings=findings,
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    lines = [
        f"discussion replies in {source}",
        f"responses: {scan.responses}",
        f"roster posts read: {scan.posts_read} of {scan.posts_total}",
        f"words: {scan.words if scan.reference_boundary_graded else 'not graded'}",
        f"references: {scan.references if scan.reference_boundary_graded else 'not graded'}",
        f"citations: {scan.citations if scan.reference_boundary_graded else 'not graded'}",
        f"numeric claims: {scan.numeric_claims if scan.reference_boundary_graded else 'not graded'}",
        (
            f"invoked sources: {scan.invoked_sources}"
            if scan.reference_boundary_graded
            else "invoked sources: not graded"
        ),
        (
            f"pre-#496 markers: {scan.pre_496_markers} (counted, not graded)"
            if scan.reference_boundary_graded
            else "pre-#496 markers: not graded"
        ),
        f"findings: {len(scan.findings)}",
    ]
    for kind in ROWS:
        if kind != ADDRESSED_NAME and not scan.reference_boundary_graded:
            lines.append(f"{kind}: not graded")
        else:
            lines.append(f"{kind}: {sum(finding.kind == kind for finding in scan.findings)}")
    if show:
        lines.extend(
            f"{finding.kind}: {finding.response}: {finding.detail}"
            for finding in scan.findings
        )
    return "\n".join(lines)


def grade(source: RunSource, _parsed: run_grader.Parsed) -> run_grader.Grade[Scan]:
    scanned = survey(source)
    refused = tuple(
        f"refused reference label in {reply.path.name}: {reply.refused_label}"
        for reply in source.replies
        if reply.refused_label is not None
    )
    return run_grader.Grade(
        scan=scanned,
        source=str(source.path),
        findings_failed=bool(scanned.findings) and scanned.reference_boundary_graded,
        coverage_failed=not scanned.reference_boundary_graded,
        diagnostics=refused,
    )


GRADER = run_grader.Grader(
    usage="usage: discussion_reply_scan.py <run directory> [--show]",
    load=load,
    grade=grade,
    format_report=format_report,
    options=(run_grader.Option("--show", repeatable=False),),
    allow_extra_positionals=False,
)


def main(argv: list[str]) -> int:
    return run_grader.run(GRADER, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
