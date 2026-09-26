#!/usr/bin/env python3
"""Record and grade coursework imagery proposed by a drafting run.

The record is deliberately separate from the draft: an approved image remains
marked as co-written evidence after its temporary draft marker is removed.  A
later voice-model harvest can therefore exclude the exact approved text rather
than attesting it as the clinician's independent writing.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, TypeVar

import repo_root
import run_grader


RECORD_NAME = "imagery-proposals.json"
EXPECTED_ROW = "coursework imagery proposals"
SCOPED_SKILLS = frozenset(
    {
        "course-assignment",
        "discussion-post",
        "discussion-reply",
        "peer-critique",
        "practicum-case-study",
    }
)
COMPLETION_GRADERS = MappingProxyType(
    {
        "course-assignment": "course_assignment_scan",
        "discussion-post": "discussion_post_scan",
        "discussion-reply": "discussion_reply_scan",
        "peer-critique": "peer_critique_scan",
        "practicum-case-study": "checks_ledger",
    }
)
DECLARED_LIMITS = (
    (
        "domain evidence is textual",
        "The gate proves that the complete declared domain is an exact Domain-table cell or whole blockquote in the canonical model's Imagery domains section; it does not judge whether the proposal uses that domain well.",
    ),
    (
        "image matching is exact prose",
        "Whitespace-normalized equality binds approved and removed image text to the graded artifact; a semantically equivalent rewrite is a different image.",
    ),
)

_STATUSES = frozenset(
    {"proposed", "proposed-and-approved", "proposed-and-removed"}
)
_RECORD_KEYS = frozenset(
    {"key", "artifact", "image", "domain", "behavior", "status"}
)
_DOMAINS = re.compile(
    r"^## Imagery\s*$.*?^### The domains\s*$\n(?P<body>.*?)(?=^### |^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
_WORKING_MARKER = re.compile(
    r"\[\[PROPOSED IMAGE (?P<key>[^\]\n]+)\]\]"
)
TScan = TypeVar("TScan")


class RecordError(ValueError):
    """The proposal record cannot support a completion claim."""


@dataclass(frozen=True)
class Proposal:
    key: str
    artifact: str
    image: str
    domain: str
    behavior: str
    status: str


@dataclass(frozen=True)
class CompletionGate:
    finding: bool
    coverage: bool
    report: str


def _normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _unwrapped(value: str) -> str:
    value = _normalized(value)
    wrappers = (("`", "`"), ("**", "**"), ('"', '"'), ("“", "”"))
    for opening, closing in wrappers:
        if value.startswith(opening) and value.endswith(closing):
            return _normalized(value[len(opening) : -len(closing)])
    return value


def _domain_entries(body: str) -> set[str]:
    """Read exact domain entries from blockquotes or a Domain-column table."""
    entries: set[str] = set()

    quote: list[str] = []
    tables: list[list[list[str]]] = []
    table: list[list[str]] = []
    for line in (*body.splitlines(), ""):
        stripped = line.lstrip()
        if stripped.startswith(">"):
            quote.append(stripped[1:])
        elif quote:
            entry = _unwrapped(" ".join(quote))
            if entry:
                entries.add(entry)
            quote = []

        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            table.append(
                [_normalized(cell) for cell in stripped.strip("|").split("|")]
            )
        elif table:
            tables.append(table)
            table = []

    for table in tables:
        if len(table) < 2:
            continue
        domain_columns = [
            index
            for index, heading in enumerate(table[0])
            if _normalized(heading).casefold() == "domain"
        ]
        separators = table[1]
        for index in domain_columns:
            if index >= len(separators) or re.fullmatch(
                r":?-{3,}:?", separators[index]
            ) is None:
                continue
            entries.update(
                _unwrapped(row[index])
                for row in table[2:]
                if index < len(row) and _unwrapped(row[index])
            )
    return entries


def _read_records(run: Path) -> tuple[Proposal, ...]:
    path = run / RECORD_NAME
    if not path.is_file():
        return ()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as failure:
        raise RecordError("record is unreadable") from failure
    if not isinstance(payload, dict) or frozenset(payload) != {"proposals"}:
        raise RecordError("record envelope is invalid")
    rows = payload["proposals"]
    if not isinstance(rows, list):
        raise RecordError("proposals is not a list")
    proposals: list[Proposal] = []
    keys: set[str] = set()
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict) or frozenset(row) != _RECORD_KEYS:
            raise RecordError(f"proposal {index} has an invalid shape")
        if not all(isinstance(row[name], str) and row[name].strip() for name in _RECORD_KEYS):
            raise RecordError(f"proposal {index} has an empty field")
        if row["status"] not in _STATUSES:
            raise RecordError(f"proposal {index} has an unknown status")
        if row["key"] in keys:
            raise RecordError(f"proposal key {row['key']} is duplicated")
        keys.add(row["key"])
        proposals.append(Proposal(**row))
    return tuple(proposals)


def _domain_supported(proposal: Proposal, model_text: str) -> bool:
    section = _DOMAINS.search(model_text)
    if section is None:
        return False
    domain = _normalized(proposal.domain)
    return domain in _domain_entries(section.group("body"))


def completion_gate(
    run: Path,
    artifacts: Mapping[str, str] | None,
    *,
    partial: bool = False,
    known_artifacts: set[str] | frozenset[str] | None = None,
) -> CompletionGate:
    """Grade proposal records against terminal artifact text and the canonical model."""
    if artifacts is None:
        return CompletionGate(
            False,
            False,
            f"{EXPECTED_ROW}: not graded - --submission was not supplied",
        )
    try:
        all_proposals = _read_records(run)
    except RecordError as failure:
        return CompletionGate(
            True,
            True,
            f"{EXPECTED_ROW}: finding - {failure}",
        )

    proposals = tuple(
        proposal for proposal in all_proposals if proposal.artifact in artifacts
    )
    findings: list[str] = []
    known = set(artifacts) if known_artifacts is None else set(known_artifacts)
    for proposal in all_proposals:
        if proposal.artifact not in known:
            findings.append(f"{proposal.key} is not a known artifact")
    if not partial:
        for proposal in all_proposals:
            if proposal.artifact not in artifacts:
                findings.append(f"{proposal.key} is not bound to the submission")

    model_text: str | None = None
    if proposals:
        try:
            resolved = repo_root.canonical_voice_model()
            if not resolved.exists:
                findings.append("the canonical model is absent")
            else:
                model_text = resolved.path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return CompletionGate(
                bool(findings),
                True,
                f"{EXPECTED_ROW}: not scanned - canonical model imagery is unreadable",
            )

    for proposal in proposals:
        artifact = artifacts[proposal.artifact]
        image_present = _normalized(proposal.image) in _normalized(artifact)
        if model_text is None or not _domain_supported(proposal, model_text):
            findings.append(f"{proposal.key} domain is not supported by the canonical model")
        if proposal.status == "proposed":
            findings.append(f"{proposal.key} is unresolved")
        elif proposal.status == "proposed-and-approved" and not image_present:
            findings.append(f"{proposal.key} approved image is absent")
        elif proposal.status == "proposed-and-removed" and image_present:
            findings.append(f"{proposal.key} removed image remains")
    for artifact, text in artifacts.items():
        for marker in _WORKING_MARKER.finditer(text):
            findings.append(
                f"{marker.group('key').strip()} working marker remains in {artifact}"
            )

    approved = sum(
        proposal.status == "proposed-and-approved" for proposal in proposals
    )
    unresolved = sum(proposal.status == "proposed" for proposal in proposals)
    counts = (
        f"proposed {len(proposals)}; approved {approved}; unresolved {unresolved}"
    )
    detail = f"; finding - {'; '.join(findings)}" if findings else ""
    return CompletionGate(
        finding=bool(findings),
        coverage=False,
        report=f"{EXPECTED_ROW}: {counts}{detail}",
    )


def apply_completion_gate(
    grade: run_grader.Grade[TScan],
    run: Path,
    artifacts: Mapping[str, str] | None,
    *,
    partial: bool = False,
    known_artifacts: set[str] | frozenset[str] | None = None,
) -> run_grader.Grade[TScan]:
    """Add the shared proposal row to an existing completion grade."""
    result = completion_gate(
        run,
        artifacts,
        partial=partial,
        known_artifacts=known_artifacts,
    )
    return replace(
        grade,
        findings_failed=grade.findings_failed or result.finding,
        coverage_failed=grade.coverage_failed or result.coverage,
        reports=grade.reports + (result.report,),
    )


def harvest_exclusions(run: Path) -> tuple[str, ...]:
    """Return exact approved co-written text that must not become attestation."""
    return tuple(
        proposal.image
        for proposal in _read_records(run)
        if proposal.status == "proposed-and-approved"
    )
