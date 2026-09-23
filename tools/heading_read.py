"""Parse and grade ADR 0219 heading-read records.

The caller owns sentence identification and pairing. This module grades the
recorded shape, its draft and project-context fingerprints, and each pair
against current claim headings. ``heading_read.DECLARED_LIMITS`` owns the
pairing boundary; the project-context row's ceiling belongs to
``project_context.DECLARED_LIMITS`` and is not copied here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import NamedTuple

import file_digest
import research_ledger
import run_grader
from run_grader import EvidenceDisposition


class DeclaredLimit(NamedTuple):
    key: str
    limit: str
    evidence: EvidenceDisposition


DECLARED_LIMITS = (
    DeclaredLimit(
        "pairing-correctness-unverified",
        "The record cannot prove that a reader paired each factual sentence correctly or judged that it claims no more than its heading.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "refutation-substance-unverified",
        "A current TESTED-HEADING cannot prove that the refuter actually tested the heading.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "reader-independence-unverified",
        "ROUTE cannot prove that a separate context performed the heading read.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "identical-byte-reversion-unseen",
        "A draft that changes and returns to identical bytes cannot be distinguished from an unchanged draft.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "peer-critique-certifier-pending",
        "peer_critique_scan does not disbelieve a mismatched claim record until issue 1056 lands.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "ratified-record-markers-unchanged",
        "This change adds no marker to ratified records and does not establish whether those records may be edited to carry one.",
        EvidenceDisposition.DECLARED_READING,
    ),
    DeclaredLimit(
        "heading-candidate-recognition-floor",
        "The candidate matcher recognizes only level-two HEADING-READ headings; an alternate spelling or heading level remains invisible.",
        EvidenceDisposition.DECLARED_READING,
    ),
)
NOT_REACHED = tuple(row.limit for row in DECLARED_LIMITS)


HEADER = re.compile(r"(?mi)^[ \t]*##[ \t]+HEADING-READ[ \t]*:[ \t]*(.*?)[ \t]*$")
HEADING_CANDIDATE = re.compile(r"(?mi)^[ \t]*##[ \t]+HEADING-READ\b.*$")
OTHER_HEADER = re.compile(r"^[ \t]*#{1,6}[ \t]+")
FIELD = re.compile(
    r"(?i)^[ \t]*(DRAFT|ROUTE|SENTENCES|PAIR|CONTEXT-DIGEST|CONTEXT-VERDICT|VERDICT|FINDINGS)[ \t]*:[ \t]*(.*?)[ \t]*$"
)
SENTENCES = re.compile(
    r"(?i)^(?P<factual>[0-9]+)[ \t]+factual,[ \t]*(?P<own>[0-9]+)[ \t]+clinician's own$",
    re.ASCII,
)
PAIR = re.compile(r"^(?P<location>.+?)[ \t]+->[ \t]+(?P<prefix>[0-9a-fA-F]{8})$", re.ASCII)
ROUTES = frozenset(("separate context", "orchestrator walk"))

MISSING_RECORD = "missing-heading-read"
DUPLICATE_RECORD = "duplicate-heading-read"
UNKNOWN_ROUTE = "unknown-heading-read-route"
SENTENCE_COUNT_MISMATCH = "heading-read-sentence-count"
UNKNOWN_HEADING = "heading-read-unknown-heading"
DROPPED_HEADING = "heading-read-dropped-heading"
DRAFT_MISMATCH = "heading-read-draft-mismatch"
DEFECT_VERDICT = "heading-read-defect"
REPORTED_FINDING = "heading-read-finding"
CONTEXT_DIGEST_MISMATCH = "heading-read-context-digest"
CONTEXT_VERDICT_SHAPE = "heading-read-context-verdict-shape"
CONTEXT_DEFECT_VERDICT = "heading-read-context-defect"
KINDS = (
    MISSING_RECORD,
    DUPLICATE_RECORD,
    UNKNOWN_ROUTE,
    SENTENCE_COUNT_MISMATCH,
    UNKNOWN_HEADING,
    DROPPED_HEADING,
    DRAFT_MISMATCH,
    DEFECT_VERDICT,
    REPORTED_FINDING,
    CONTEXT_DIGEST_MISMATCH,
    CONTEXT_VERDICT_SHAPE,
    CONTEXT_DEFECT_VERDICT,
)


@dataclass(frozen=True)
class Record:
    artifact: str
    fields: dict[str, str] = field(default_factory=dict)
    pairs: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()

    def value(self, name: str) -> str:
        return self.fields.get(name, "")


@dataclass(frozen=True)
class Binding:
    artifact: str
    draft: bytes
    claims: tuple[research_ledger.Record, ...]
    context_digest: str


@dataclass(frozen=True)
class Finding:
    kind: str
    artifact: str
    detail: str


@dataclass(frozen=True)
class Scan:
    records_read: int
    unread: int
    findings: tuple[Finding, ...]


def read_records(text: str) -> tuple[Record, ...]:
    records: list[Record] = []
    artifact: str | None = None
    fields: dict[str, str] = {}
    pairs: list[str] = []
    findings: list[str] = []

    def close() -> None:
        if artifact is not None:
            records.append(Record(artifact, dict(fields), tuple(pairs), tuple(findings)))

    for line in text.splitlines():
        heading = HEADER.match(line)
        if heading:
            close()
            artifact = heading.group(1).strip()
            fields, pairs, findings = {}, [], []
            continue
        if artifact is not None and OTHER_HEADER.match(line):
            close()
            artifact, fields, pairs, findings = None, {}, [], []
            continue
        if artifact is None:
            continue
        named = FIELD.match(line)
        if not named:
            continue
        name, value = named.group(1).upper(), named.group(2).strip()
        if name == "PAIR":
            pairs.append(value)
        elif name == "FINDINGS":
            findings.append(value)
        else:
            fields[name] = value
    close()
    return tuple(records)


def _record_findings(record: Record, binding: Binding) -> list[Finding]:
    found: list[Finding] = []
    artifact = record.artifact
    if record.value("ROUTE").casefold() not in ROUTES:
        found.append(Finding(UNKNOWN_ROUTE, artifact, record.value("ROUTE") or "ROUTE is missing"))

    sentence_match = SENTENCES.fullmatch(record.value("SENTENCES"))
    factual = int(sentence_match.group("factual")) if sentence_match else -1
    if factual < 0 or len(record.pairs) + len(record.findings) != factual:
        found.append(
            Finding(
                SENTENCE_COUNT_MISMATCH,
                artifact,
                f"{len(record.pairs)} pairs plus {len(record.findings)} findings; SENTENCES says {record.value('SENTENCES') or 'nothing'}",
            )
        )

    headings: dict[str, tuple[research_ledger.Record, ...]] = {}
    for claim in binding.claims:
        prefix = research_ledger.heading_digest(claim.claim)[:8]
        headings[prefix] = headings.get(prefix, ()) + (claim,)
    for pair in record.pairs:
        parsed = PAIR.fullmatch(pair)
        prefix = parsed.group("prefix").casefold() if parsed else ""
        matches = headings.get(prefix, ())
        if not matches:
            found.append(Finding(UNKNOWN_HEADING, artifact, pair))
        elif any("DROPPED" in claim.fields for claim in matches):
            found.append(Finding(DROPPED_HEADING, artifact, pair))

    current_digest = file_digest.sha256_bytes(binding.draft)
    if record.value("DRAFT").casefold() != current_digest:
        found.append(
            Finding(
                DRAFT_MISMATCH,
                artifact,
                f"recorded {record.value('DRAFT') or 'nothing'}, current {current_digest}",
            )
        )

    recorded_context = record.value("CONTEXT-DIGEST").casefold()
    expected_context = binding.context_digest.casefold()
    if recorded_context != expected_context:
        found.append(
            Finding(
                CONTEXT_DIGEST_MISMATCH,
                artifact,
                f"recorded {recorded_context or 'nothing'}, expected {expected_context or 'nothing'}",
            )
        )

    context_verdict = record.value("CONTEXT-VERDICT")
    if expected_context == "none":
        if context_verdict.casefold() != "none":
            found.append(
                Finding(
                    CONTEXT_DEFECT_VERDICT,
                    artifact,
                    context_verdict or "CONTEXT-VERDICT is missing",
                )
            )
    elif context_verdict.casefold() != "agrees":
        shaped = re.fullmatch(
            r"(?i)(narrows|contradicts)[ \t]+-[ \t]+[^,]+,[ \t]+.+",
            context_verdict,
        )
        if shaped is None:
            conflict = re.fullmatch(
                r"(?i)sources-conflict[ \t]+-[ \t]+(?P<left>[^,]+?)[ \t]+and[ \t]+(?P<right>[^,]*),[ \t]+(?P<difference>.+)",
                context_verdict,
            )
            if conflict is not None:
                left = conflict.group("left").strip()
                right = conflict.group("right").strip()
                if left and right and left.casefold() != right.casefold():
                    shaped = conflict
        if shaped is None:
            found.append(
                Finding(
                    CONTEXT_VERDICT_SHAPE,
                    artifact,
                    context_verdict or "CONTEXT-VERDICT is missing",
                )
            )
        found.append(
            Finding(
                CONTEXT_DEFECT_VERDICT,
                artifact,
                context_verdict or "CONTEXT-VERDICT is missing",
            )
        )

    verdict = record.value("VERDICT")
    if verdict.casefold() != "clean":
        found.append(Finding(DEFECT_VERDICT, artifact, verdict or "VERDICT is missing"))
    for detail in record.findings:
        found.append(Finding(REPORTED_FINDING, artifact, detail or "empty FINDINGS line"))
    return found


def scan(text: str, bindings: tuple[Binding, ...]) -> Scan:
    """Grade records for the caller's expected drafts and claim scopes."""
    records = read_records(text)
    population = len(HEADING_CANDIDATE.findall(text))
    read = 0
    found: list[Finding] = []
    expected = {binding.artifact: binding for binding in bindings}
    for artifact, binding in expected.items():
        matches = tuple(record for record in records if record.artifact == artifact)
        if not matches:
            found.append(Finding(MISSING_RECORD, artifact, "no HEADING-READ record"))
            continue
        read += len(matches)
        if len(matches) > 1:
            found.append(
                Finding(DUPLICATE_RECORD, artifact, f"expected one record, found {len(matches)}")
            )
        for record in matches:
            found.extend(_record_findings(record, binding))
    unread = max(0, population - read)
    return Scan(read, unread, tuple(found))


def format_coverage(result: Scan) -> str:
    return "\n".join(
        (
            f"heading-read records: {result.records_read}",
            run_grader.format_unread_remainder(result.unread),
        )
    )
