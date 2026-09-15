#!/usr/bin/env python3
"""Extract and grade the private after-action review for one submission.

    python tools/aar_scan.py <run-directory> --transcript <session.jsonl> \
        --submission <submission-key> --memory-index <MEMORY.md> --extract
    python tools/aar_scan.py <run-directory> --submission <submission-key> [--show]

The first form writes a reduced, private review packet under ``<run>/aar/``.
It keeps human turns, assistant text, subagent result bodies, and tool names and
statuses. Tool-result bodies are otherwise dropped. The packet fixes the
candidate population; a fresh adversarial reader, not this command, classifies
which candidates are observed corrections and writes the review record.
``ENTRY_KINDS`` owns the extract label vocabulary and its generated legend.

The second form grades that record. Counts are safe to paste; ``--show`` names
private findings and must not be pasted. A run directory and every artifact
under ``aar/`` are private working material.

The complete coverage boundary is ``DECLARED_LIMITS``. This docstring points at
that object and does not maintain a second copy of its rows. #814.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from console_codec import use_utf8
from discussion_artifact import REREAD_BLOCK
import git_paths
import shell_reader
import repo_root
import run_grader
import browser_tab_hook


NOT_GRADED = run_grader.NOT_GRADED
REVIEW_CLASSIFIER_ENTRY_CUTOFF = datetime(2026, 9, 12, tzinfo=timezone.utc)
POSTED_READING_FINGERPRINT_CUTOFF = datetime(2026, 9, 13, tzinfo=timezone.utc)


SCOPED_SKILLS = frozenset(
    {
        "batch-shift",
        "clinical-note",
        "course-assignment",
        "discussion-post",
        "discussion-reply",
        "icd10-cpt",
        "peer-critique",
        "practicum-case-study",
    }
)
COMPLETION_GRADERS: Mapping[str, str] = MappingProxyType(
    {
        "batch-shift": "filled_vitals_census",
        "clinical-note": "differential_scan",
        "course-assignment": "course_assignment_scan",
        "discussion-post": "discussion_post_scan",
        "discussion-reply": "discussion_reply_scan",
        "icd10-cpt": "specificity_scan",
        "peer-critique": "peer_critique_scan",
        "practicum-case-study": "checks_ledger",
    }
)


def validate_completion_graders(
    scoped_skills: Iterable[str], graders: Mapping[str, str]
) -> None:
    """Refuse a scoped skill with no completion grader or an off-scope pairing."""
    scoped = set(scoped_skills)
    paired = set(graders)
    missing = sorted(scoped - paired)
    extra = sorted(paired - scoped)
    if missing or extra:
        raise ValueError(
            f"completion grader mapping mismatch; missing={missing}; extra={extra}"
        )


validate_completion_graders(SCOPED_SKILLS, COMPLETION_GRADERS)
EXPECTED_ROW = "the after-action review"
DISPOSITIONS = frozenset({"skill-file", "tracker-ticket", "memory-write", "check"})
CORRECTORS = frozenset({"clinician", "agent-or-tool", "orchestrator"})
PRIVATE_TEXT_SUFFIXES = frozenset({".md", ".txt", ".json"})
SUBAGENT_TOOLS = frozenset({"Agent", "Task", "Monitor", "TaskStop"})
EXTRACTOR_WRITTEN_ENTRY_KINDS = frozenset(
    {"tool-call", "subagent-launch", "inter-agent-metadata"}
)

ENTRY_KIND_DESCRIPTIONS: Mapping[str, str] = MappingProxyType(
    {
        "clinician": "user row with no harness flag or recognized envelope",
        "assistant": "assistant text block",
        "tool-call": "tool invocation",
        "tool-status": "tool completion status",
        "subagent-launch": "subagent launch acknowledgment",
        "subagent-result": "subagent return body",
        "task-notification": "task notification envelope",
        "skill-prompt": "flagged skill prompt injection",
        "harness-meta": "flagged harness row with no recognized envelope",
        "compaction-summary": "harness compaction summary",
        "inter-agent-metadata": "Codex inter-agent communication marker",
        "system-reminder": "system reminder envelope",
        "command-name": "command-name envelope",
        "local-command-stdout": "local command output envelope",
        "ci-monitor-event": "CI monitor envelope",
        "recommended-plugins": "recommended-plugins envelope",
        "codex-delegation": "Codex delegation envelope",
        "environment-context": "environment-context envelope",
        "prior-review": "a prior classifier return identified by its review record",
    }
)
ENTRY_KINDS = tuple(ENTRY_KIND_DESCRIPTIONS)
ENVELOPE_KINDS: Mapping[str, str] = MappingProxyType(
    {
        "task-notification": "task-notification",
        "system-reminder": "system-reminder",
        "command-name": "command-name",
        "local-command-stdout": "local-command-stdout",
        "ci-monitor-event": "ci-monitor-event",
        "recommended_plugins": "recommended-plugins",
        "codex_delegation": "codex-delegation",
        "environment_context": "environment-context",
    }
)
ENVELOPE_ENTRY_KINDS = frozenset(
    {
        "task-notification",
        "system-reminder",
        "command-name",
        "local-command-stdout",
        "ci-monitor-event",
        "recommended-plugins",
        "codex-delegation",
        "environment-context",
    }
)
ENVELOPE_TAG = re.compile(r"<(?P<tag>[a-z][a-z0-9_-]*)(?:\s|>)")
TASK_ID = re.compile(r"<task-id>\s*(?P<id>[^<\s]+)\s*</task-id>")
TOOL_USE_ID = re.compile(r"<tool-use-id>\s*(?P<id>[^<\s]+)\s*</tool-use-id>")
AGENT_ID = re.compile(r"(?im)^agentId:\s*(?P<id>\S+)")
SKILL_PROMPT_PREFIX = "Base directory for this skill:"
SUBAGENT_LAUNCH_PREFIX = "Async agent launched successfully."
CODEX_ROW_TYPES = frozenset(
    {
        "event_msg",
        "response_item",
        "turn_context",
        "token_usage_record",
        "inter_agent_communication_metadata",
        "world_state",
        "session_meta",
        "compacted",
    }
)
CODEX_RESPONSE_TYPES = frozenset(
    {
        "agent_message",
        "custom_tool_call",
        "custom_tool_call_output",
        "function_call",
        "function_call_output",
        "message",
        "reasoning",
    }
)
CLAUDE_ROW_TYPES = frozenset(
    {
        "assistant",
        "attachment",
        "file-history-snapshot",
        "progress",
        "queue-operation",
        "system",
        "user",
    }
)

ROWS: Mapping[str, str] = MappingProxyType(
    {
        "missing-review": "the submission has no review record",
        "unscannable-review": "the review record or its evidence cannot be scanned",
        "unscannable-extract": "the extract cannot be scanned",
        "posted-reading-mismatch": "the extract has no current fingerprint of its posted reading",
        "missing-classifier-entry": "a post-cutoff review does not identify its classifier return",
        "unmarked-prior-review": "a prior watermark has no classifier return identity",
        "missing-header-field": "a required review header field is absent",
        "wrong-submission": "the review names another submission",
        "non-numeric-coverage": "the population or unread count is not numeric",
        "population-mismatch": "the review and extract populations disagree",
        "unread-candidates": "the review leaves candidate records unread",
        "watermark-mismatch": "the review and extract watermarks disagree",
        "transcript-mismatch": "the review and extract transcript sets disagree",
        "missing-correction-verdict": "the correction population has no verdict",
        "contradictory-correction-verdict": "correction records contradict a none verdict",
        "missing-sustain-verdict": "the sustain population has no verdict",
        "contradictory-sustain-verdict": "sustain records contradict a none verdict",
        "unknown-correction-event": "a correction names no extracted candidate",
        "correction-on-extractor-written-entry": "a correction names an entry whose text was written by the extractor",
        "missing-correction-field": "a correction lacks a required field",
        "unknown-corrector": "a correction names no declared corrector",
        "unknown-error-party": "a correction names no declared party in error",
        "unknown-disposition": "a correction names no declared disposition",
        "unlanded-ticket": "a tracker-ticket correction has no landed ticket",
        "unlanded-memory": "a memory correction has no changed memory target",
        "unlanded-check": "a check correction has no changed tracked check",
        "unknown-sustain-event": "a sustain names no extracted candidate",
        "bare-sustain": "a sustain lacks substantive classification",
        "missing-gh-call": "a tracker disposition has no successful GitHub call",
    }
)
KINDS = tuple(ROWS)

DECLARED_LIMITS = (
    (
        "semantic classification",
        "The command fixes the candidate population and cannot decide whether a candidate is a correction or whether the classifier's disposition is right.",
    ),
    (
        "tool-result-only correction",
        "Ordinary tool-result bodies are dropped; a correction that lived only there and was silently acted on is not extractable.",
    ),
    (
        "uncorrected error",
        "An error nobody contradicted is not an observed correction and cannot enter this review.",
    ),
    (
        "orchestrator veto",
        "The grader records disagreements but cannot prevent an orchestrator from overruling every unflattering classification.",
    ),
    (
        "subagent silence",
        "A subagent error never contradicted in the main transcript remains invisible.",
    ),
    (
        "transcript flush",
        "A harness writes transcripts asynchronously; a final entry not flushed before extraction is outside the measured population.",
    ),
    (
        "run-key discovery",
        "A sitting whose retained tool calls never name the run directory cannot be discovered safely.",
    ),
    (
        "subagent launch-result drift",
        "Launch accounting covers only this extract population and an unjoined launch means only that no matching result is present in this population.",
    ),
    (
        "correction kind misplacement",
        "A correction misplaced onto a tool-status or skill-prompt entry is shown in the kind table and is not refused.",
    ),
    (
        "browser tab ownership",
        "The transcript cannot reveal a clinician handover or prove a conditional tab creation unless the tool result marks it, so ownership is reported conservatively and never graded.",
    ),
)
NOT_REACHED = tuple(reason for _subject, reason in DECLARED_LIMITS)

HEADER_FIELDS = (
    "SUBMISSION",
    "TRANSCRIPTS",
    "POPULATION",
    "UNREAD",
    "WATERMARK",
    "MEMORY-INDEX",
    "CLASSIFIER",
    "DISAGREEMENTS",
)
CORRECTION_FIELDS = (
    "CORRECTOR",
    "IN-ERROR",
    "SUMMARY",
    "CLASSIFIER",
    "ORCHESTRATOR",
    "DISPOSITION",
    "TARGET",
    "LANDING",
)

FIELD = re.compile(r"^(?P<name>[A-Z][A-Z-]*):\s*(?P<value>.*)$")
CORRECTION_HEADING = re.compile(r"^## CORRECTION:\s*(?P<event>\S+)\s*$")
SUSTAIN_HEADING = re.compile(r"^## SUSTAIN:\s*(?P<event>\S+)\s*$")
RUN_REFERENCE = re.compile(
    r"(?i)(?:[A-Za-z]:)?[^\s\"'<>|]*scratch[\\/]runs[\\/](?P<key>[^\\/\s\"'<>|]+)"
)
GH_ISSUE = re.compile(r"https://github\.com/[^/]+/[^/]+/issues/[0-9]+\Z")


@dataclass(frozen=True)
class Candidate:
    identifier: str
    transcript_id: str
    kind: str
    text: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class Correction:
    event: str
    fields: Mapping[str, str]


@dataclass(frozen=True)
class Sustain:
    event: str
    fields: Mapping[str, str]


@dataclass(frozen=True)
class Review:
    path: Path
    fields: Mapping[str, str]
    corrections: tuple[Correction, ...]
    sustains: tuple[Sustain, ...]
    corrections_none: bool
    sustains_none: bool


@dataclass(frozen=True)
class Finding(run_grader.Finding):
    detail: str


class UnknownExtractFormat(ValueError):
    pass


@dataclass(frozen=True)
class BrowserDiagnostics:
    unowned_page_actions: int = 0
    creation_parses_tabs_create_mcp: int = 0
    creation_parses_tabs_context_mcp: int = 0
    creation_parses_navigate_without_tab: int = 0


@dataclass(frozen=True)
class ExtractDiagnostics:
    harness_versions: tuple[str, ...]
    undeclared_envelopes: int
    undeclared_codex_row_types: int
    undeclared_codex_payload_types: int
    subagent_launches: int
    joined_results: int
    unjoined_launches: int
    notifications_without_join_key: int
    browser: BrowserDiagnostics


@dataclass(frozen=True)
class TranscriptDiscovery:
    paths: tuple[Path, ...]
    found: int
    skipped_by_time: int
    skipped_by_byte_search: int
    read: int


@dataclass(frozen=True)
class EntryKindCount:
    record: str
    corrector: str
    kind: str
    count: int


@dataclass(frozen=True)
class Scan:
    submission: str
    records: int
    population: int
    corrections: int
    sustains: int
    unread: int
    findings: tuple[Finding, ...]
    rounds: tuple[RoundScan, ...] = ()
    kind_counts: tuple[EntryKindCount, ...] = ()
    later_sittings: int = 0
    transcripts_found: int = 0
    transcripts_skipped_by_time: int = 0
    transcripts_skipped_by_byte_search: int = 0
    transcripts_read: int = 0
    browser: BrowserDiagnostics = BrowserDiagnostics()


@dataclass(frozen=True)
class RoundScan:
    number: int
    corrections: int
    unlanded: int


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _content_blocks(message: Any) -> list[dict[str, Any]]:
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    return [row for row in content if isinstance(row, dict)] if isinstance(content, list) else []


def _codex_payload(row: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = row.get("payload")
    return payload if row.get("type") == "response_item" and isinstance(payload, dict) else {}


def _codex_tool_name(payload: Mapping[str, Any]) -> str:
    name = _text(payload.get("name")) or "unknown-tool"
    namespace = _text(payload.get("namespace"))
    return f"{namespace}.{name}" if namespace else name


def _codex_content_text(payload: Mapping[str, Any], block_type: str) -> str:
    content = payload.get("content")
    if not isinstance(content, list):
        return ""
    return "\n".join(
        _text(block.get("text"))
        for block in content
        if isinstance(block, dict) and block.get("type") == block_type
    ).strip()


def _codex_compaction_text(payload: Mapping[str, Any]) -> str:
    direct = _text(payload.get("message")).strip()
    if direct:
        return direct
    history = payload.get("replacement_history")
    if not isinstance(history, list):
        return "compaction summary unavailable"
    for item in reversed(history):
        if not isinstance(item, dict) or item.get("type") != "compaction":
            continue
        for field in ("summary", "message", "text"):
            value = _text(item.get(field)).strip()
            if value:
                return value
        if item.get("encrypted_content"):
            return "encrypted compaction summary"
    return "compaction summary unavailable"


def read_transcript(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read transcript {path.name}") from exc
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on transcript line {number}") from exc
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _tool_index(rows: Iterable[dict[str, Any]]) -> dict[str, str]:
    tools: dict[str, str] = {}
    for row in rows:
        if row.get("type") == "assistant":
            for block in _content_blocks(row.get("message")):
                if block.get("type") == "tool_use" and isinstance(block.get("id"), str):
                    tools[block["id"]] = _text(block.get("name")) or "unknown-tool"
        payload = _codex_payload(row)
        if payload.get("type") in {"custom_tool_call", "function_call"}:
            call_id = _text(payload.get("call_id"))
            if call_id:
                tools[call_id] = _codex_tool_name(payload)
    return tools


def _result_status(block: Mapping[str, Any]) -> str:
    return "failed" if block.get("is_error") is True else "completed"


def _human_text(row: Mapping[str, Any]) -> str:
    message = row.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        value = content.strip()
    elif isinstance(content, list):
        value = "\n".join(
            _text(block.get("text"))
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
    else:
        return ""
    if value.startswith("<command-message>") or value.startswith("<local-command-caveat>"):
        return ""
    return value


def _envelope_kind(value: str) -> str | None:
    for match in ENVELOPE_TAG.finditer(value):
        kind = ENVELOPE_KINDS.get(match.group("tag"))
        if kind is not None:
            return kind
    return None


def _human_kind(row: Mapping[str, Any], value: str) -> str:
    envelope = _envelope_kind(value)
    if envelope is not None:
        return envelope
    if row.get("isCompactSummary") is True:
        return "compaction-summary"
    if row.get("isMeta") is True:
        return "skill-prompt" if value.startswith(SKILL_PROMPT_PREFIX) else "harness-meta"
    return "clinician"


def _human_identifier(uuid: str, kind: str, value: str) -> str:
    if kind == "task-notification":
        matched = TASK_ID.search(value)
        if matched:
            return matched.group("id")
    return uuid


def _human_candidate(
    uuid: str,
    transcript_id: str,
    value: str,
    *,
    default_kind: str,
    row: Mapping[str, Any] | None = None,
) -> Candidate:
    kind = _human_kind(row, value) if row is not None else (_envelope_kind(value) or default_kind)
    identifier = _human_identifier(uuid, kind, value)
    return Candidate(
        identifier,
        transcript_id,
        _declared_entry_kind(kind),
        value,
        (uuid,) if identifier != uuid else (),
    )


def _declared_entry_kind(kind: str) -> str:
    if kind not in ENTRY_KINDS:
        raise ValueError(f"undeclared extract entry kind {kind}")
    return kind


def reduce_transcript(path: Path) -> list[Candidate]:
    """The fixed candidate population, in transcript order."""
    rows = read_transcript(path)
    tools = _tool_index(rows)
    transcript_id = path.stem
    candidates: list[Candidate] = []
    for ordinal, row in enumerate(rows, 1):
        legacy_fallback = f"line-{ordinal}"
        uuid = _text(row.get("uuid")) or f"{transcript_id}#row-{ordinal}"
        row_start = len(candidates)
        if row.get("type") == "user":
            human = _human_text(row)
            if human:
                candidates.append(
                    _human_candidate(
                        uuid, transcript_id, human, default_kind="clinician", row=row
                    )
                )
            for index, block in enumerate(_content_blocks(row.get("message")), 1):
                if block.get("type") != "tool_result":
                    continue
                tool_id = _text(block.get("tool_use_id"))
                tool = tools.get(tool_id, "unknown-tool")
                if tool in SUBAGENT_TOOLS:
                    body = block.get("content")
                    if isinstance(body, list):
                        body = "\n".join(
                            _text(part.get("text"))
                            for part in body
                            if isinstance(part, dict) and part.get("type") == "text"
                        )
                    body = _text(body).strip()
                    if body:
                        candidates.append(
                            Candidate(
                                f"{uuid}#subagent-{index}",
                                transcript_id,
                                _declared_entry_kind(
                                    "subagent-launch"
                                    if body.startswith(SUBAGENT_LAUNCH_PREFIX)
                                    else "subagent-result"
                                ),
                                body,
                            )
                        )
                candidates.append(
                    Candidate(
                        f"{uuid}#status-{index}",
                        transcript_id,
                        "tool-status",
                        f"{tool}: {_result_status(block)}",
                    )
                )
        elif row.get("type") == "assistant":
            for index, block in enumerate(_content_blocks(row.get("message")), 1):
                if block.get("type") == "text" and _text(block.get("text")).strip():
                    body = _text(block.get("text")).strip()
                    candidates.append(
                        _human_candidate(
                            f"{uuid}#text-{index}",
                            transcript_id,
                            body,
                            default_kind="assistant",
                        )
                    )
                elif block.get("type") == "tool_use":
                    candidates.append(
                        Candidate(
                            f"{uuid}#tool-{index}",
                            transcript_id,
                            "tool-call",
                            _text(block.get("name")) or "unknown-tool",
                        )
                    )
        elif row.get("type") == "response_item":
            payload = _codex_payload(row)
            payload_type = payload.get("type")
            identifier = _text(payload.get("id")) or uuid
            if payload_type == "message":
                role = payload.get("role")
                block_type = "input_text" if role == "user" else "output_text"
                body = _codex_content_text(payload, block_type)
                if body and role in {"user", "assistant"}:
                    candidates.append(
                        _human_candidate(
                            identifier,
                            transcript_id,
                            body,
                            default_kind="clinician" if role == "user" else "assistant",
                        )
                    )
            elif payload_type in {"custom_tool_call", "function_call"}:
                candidates.append(
                    Candidate(identifier, transcript_id, "tool-call", _codex_tool_name(payload))
                )
            elif payload_type in {"custom_tool_call_output", "function_call_output"}:
                call_id = _text(payload.get("call_id"))
                tool = tools.get(call_id, "unknown-tool")
                candidates.append(
                    Candidate(identifier, transcript_id, "tool-status", f"{tool}: completed")
                )
            elif payload_type == "agent_message":
                body = _codex_content_text(payload, "input_text")
                if body:
                    candidates.append(Candidate(identifier, transcript_id, "subagent-result", body))
        elif row.get("type") == "compacted":
            payload = row.get("payload")
            body = _codex_compaction_text(payload if isinstance(payload, dict) else {})
            candidates.append(Candidate(uuid, transcript_id, "compaction-summary", body))
        elif row.get("type") == "inter_agent_communication_metadata":
            candidates.append(
                Candidate(uuid, transcript_id, "inter-agent-metadata", "inter-agent communication metadata")
            )
        elif row.get("type") == "attachment":
            attachment = row.get("attachment")
            body = (
                _text(attachment.get("prompt")).strip()
                if isinstance(attachment, dict)
                else ""
            )
            if body:
                candidates.append(
                    _human_candidate(
                        uuid, transcript_id, body, default_kind="harness-meta"
                    )
                )
        elif row.get("type") == "queue-operation":
            body = _text(row.get("content")).strip()
            if body:
                candidates.append(
                    _human_candidate(
                        uuid, transcript_id, body, default_kind="harness-meta"
                    )
                )
        if uuid != legacy_fallback and not _text(row.get("uuid")):
            candidates[row_start:] = [
                replace(
                    candidate,
                    aliases=(
                        *candidate.aliases,
                        candidate.identifier.replace(uuid, legacy_fallback, 1),
                    ),
                )
                for candidate in candidates[row_start:]
            ]
    return candidates


def _safe_submission(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    if not safe:
        raise ValueError("submission key has no filename-safe characters")
    return safe


def _round_stem(submission: str, round_number: int) -> str:
    if round_number < 1:
        raise ValueError("review round must be positive")
    safe = _safe_submission(submission)
    return safe if round_number == 1 else f"{safe}.round-{round_number}"


def review_path(run: Path, submission: str, round_number: int = 1) -> Path:
    return run / "aar" / f"{_round_stem(submission, round_number)}.md"


def extract_path(run: Path, submission: str, round_number: int = 1) -> Path:
    return run / "aar" / f"{_round_stem(submission, round_number)}.extract.md"


def baseline_path(run: Path, submission: str, round_number: int = 1) -> Path:
    return run / "aar" / f"{_round_stem(submission, round_number)}.baseline.json"


def _review_round_numbers(run: Path, submission: str) -> tuple[int, ...]:
    root = run / "aar"
    if not root.is_dir():
        return ()
    safe = re.escape(_safe_submission(submission))
    pattern = re.compile(
        rf"^{safe}(?:\.round-(?P<round>[1-9][0-9]*))?"
        rf"(?:\.extract\.md|\.baseline\.json|\.md)$"
    )
    numbers: set[int] = set()
    for path in root.iterdir():
        if not path.is_file():
            continue
        match = pattern.fullmatch(path.name)
        if match:
            numbers.add(int(match.group("round") or "1"))
    return tuple(sorted(numbers))


def _next_review_round(run: Path, submission: str) -> int:
    existing = _review_round_numbers(run, submission)
    return existing[-1] + 1 if existing else 1


def _posted_reading_block(run: Path, submission: str) -> str:
    path = run / "reread.md"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(
            f"reread.md has no REREAD record for {submission}"
        ) from exc
    matches = [
        match
        for match in REREAD_BLOCK.finditer(text)
        if match.group("artifact").strip() == submission
    ]
    if len(matches) != 1:
        raise ValueError(
            f"reread.md must have exactly one REREAD record for {submission}"
        )
    return matches[0].group(0).strip()


def _posted_reading_fingerprint(run: Path, submission: str) -> str:
    return sha256(_posted_reading_block(run, submission).encode("utf-8")).hexdigest()


def legacy_orphan_paths(run: Path) -> tuple[Path, ...]:
    root = run / "aar"
    return tuple(sorted(root.glob("orphaned-*.json"))) if root.is_dir() else ()


def retire_orphan_pointers(run: Path) -> None:
    """Move legacy pointer files aside in place; their evidence is never deleted."""
    for path in legacy_orphan_paths(run):
        destination = path.with_name(f"retired-{path.name}")
        suffix = 2
        while destination.exists():
            destination = path.with_name(f"retired-{suffix}-{path.name}")
            suffix += 1
        path.replace(destination)


def _hash(path: Path) -> str | None:
    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _tracked_files() -> tuple[Path, ...]:
    """Tracked files used for landing evidence; untracked files are not visible."""
    root = Path(__file__).resolve().parent.parent
    return tuple(
        root / path
        for path in git_paths.read_path_records(root, "ls-files", "-z")
    )


def _memory_files(index: Path) -> tuple[Path, ...]:
    root = index.parent
    return tuple(sorted(path for path in root.rglob("*") if path.is_file()))


def snapshot(memory_index: Path) -> dict[str, str | None]:
    paths = (*_tracked_files(), *_memory_files(memory_index))
    return {str(path.resolve()): _hash(path) for path in paths}


def _transcript_watermarks(value: str) -> dict[str, str]:
    watermarks: dict[str, str] = {}
    for item in value.split("|"):
        transcript, separator, identifier = item.strip().partition("=")
        if separator and transcript and identifier:
            watermarks[transcript] = identifier
    return watermarks


def _review_cursors(run: Path) -> dict[str, list[tuple[str, str | None]]]:
    cursors: dict[str, list[tuple[str, str | None]]] = {}
    root = run / "aar"
    if not root.is_dir():
        return cursors
    for path in sorted(root.glob("*.md")):
        if path.name.endswith(".extract.md"):
            continue
        try:
            review = read_review(path)
        except ValueError:
            continue
        transcripts = [value.strip() for value in review.fields.get("TRANSCRIPTS", "").split(",")]
        extract = path.with_name(f"{path.stem}.extract.md")
        watermarks: dict[str, str] = {}
        if extract.is_file():
            try:
                extract_fields, _identifiers = _extract_metadata(extract)
                watermarks = _transcript_watermarks(
                    extract_fields.get("TRANSCRIPT-WATERMARKS", "")
                )
            except ValueError:
                watermarks = {}
        if watermarks:
            for transcript, watermark in watermarks.items():
                classifier = (
                    review.fields.get("CLASSIFIER-ENTRY", "")
                    if watermark == review.fields.get("WATERMARK")
                    else None
                )
                cursors.setdefault(transcript, []).append((watermark, classifier))
        elif transcripts and review.fields.get("WATERMARK"):
            cursors.setdefault(transcripts[-1], []).append(
                (review.fields["WATERMARK"], review.fields.get("CLASSIFIER-ENTRY", ""))
            )
    return cursors


def _furthest_cursor(
    rows: Iterable[Candidate], cursors: Iterable[tuple[str, str | None]]
) -> tuple[str, str | None] | None:
    candidates_by_identifier = {
        identifier: index
        for index, candidate in enumerate(rows)
        for identifier in (candidate.identifier, *candidate.aliases)
    }
    available = tuple(cursors)
    if not available:
        return None
    return max(
        available,
        key=lambda cursor: candidates_by_identifier.get(cursor[0], -1),
    )


def _unmarked_prior_reviews(run: Path, transcripts: Iterable[Path]) -> int:
    cursors = _review_cursors(run)
    return sum(
        1
        for transcript in transcripts
        for selected in [_furthest_cursor(reduce_transcript(transcript), cursors.get(transcript.stem, ()))]
        if selected is not None and selected[1] == ""
    )


def _after_watermark(candidates: list[Candidate], watermark: str | None) -> list[Candidate]:
    if watermark is None:
        return candidates
    indexes = [
        index
        for index, row in enumerate(candidates)
        if row.identifier == watermark or watermark in row.aliases
    ]
    if not indexes:
        raise ValueError("prior watermark is not in its transcript population")
    return candidates[indexes[-1] + 1 :]


def _collect_population(
    run: Path, transcript: Path | None
) -> tuple[list[Candidate], tuple[Path, ...], TranscriptDiscovery]:
    discovery = discover_transcripts(run, transcript)
    cursors = _review_cursors(run)
    population: list[Candidate] = []
    transcripts: list[Path] = []
    seen: set[str] = set()
    for source in discovery.paths:
        if source.stem in seen:
            continue
        seen.add(source.stem)
        rows = reduce_transcript(source)
        furthest_cursor = _furthest_cursor(rows, cursors.get(source.stem, ()))
        watermark, prior_review = furthest_cursor or ("", None)
        current = _after_watermark(rows, watermark or None)
        if prior_review:
            current = [
                replace(candidate, kind="prior-review")
                if candidate.identifier == prior_review
                or prior_review in candidate.aliases
                else candidate
                for candidate in current
            ]
        if not current:
            continue
        transcripts.append(source)
        population.extend(current)
    selected_transcripts = tuple(transcripts)
    return population, selected_transcripts, replace(
        discovery,
        paths=selected_transcripts,
        read=len(selected_transcripts),
    )


def collect_population(
    run: Path, transcript: Path | None
) -> tuple[list[Candidate], tuple[Path, ...]]:
    population, transcripts, _discovery = _collect_population(run, transcript)
    return population, transcripts


def _notification_keys(value: str) -> set[str]:
    return {
        match.group("id")
        for pattern in (TASK_ID, TOOL_USE_ID)
        for match in pattern.finditer(value)
    }


def _tool_results(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for row in rows:
        if row.get("type") != "user":
            continue
        for block in _content_blocks(row.get("message")):
            tool_id = _text(block.get("tool_use_id"))
            if block.get("type") == "tool_result" and tool_id:
                results[tool_id] = block.get("content")
    return results


def _decoded_json(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _tab_ids(value: Any) -> set[str]:
    value = _decoded_json(value)
    if isinstance(value, str):
        return set(
            re.findall(r"\b(?:Tab ID|tabId|tab_id)\s*[:=]\s*([A-Za-z0-9_-]+)", value)
        )
    if isinstance(value, list):
        return {tab for item in value for tab in _tab_ids(item)}
    if isinstance(value, dict):
        found = {
            str(item)
            for name, item in value.items()
            if name in {"tabId", "tab_id"} and item is not None and item != ""
        }
        return found | {tab for item in value.values() for tab in _tab_ids(item)}
    return set()


def _created_tab_ids(value: Any) -> set[str]:
    value = _decoded_json(value)
    if isinstance(value, str):
        return set(
            re.findall(
                r"\bCreated new tab\b[^\r\n]{0,160}?\b(?:Tab ID|tabId|tab_id)\s*[:=]\s*([A-Za-z0-9_-]+)",
                value,
                flags=re.IGNORECASE,
            )
        )
    if isinstance(value, list):
        return {tab for item in value for tab in _created_tab_ids(item)}
    if not isinstance(value, dict):
        return set()
    direct = (
        {
            str(value[name])
            for name in ("tabId", "tab_id")
            if value.get("created") is True and value.get(name) not in {None, ""}
        }
    )
    return direct | {tab for item in value.values() for tab in _created_tab_ids(item)}


def _browser_diagnostics(rows: Iterable[Mapping[str, Any]]) -> BrowserDiagnostics:
    rows = tuple(rows)
    results = _tool_results(rows)
    owned: set[str] = set()
    unowned = 0
    created_directly = 0
    created_from_context = 0
    created_by_navigation = 0
    for row in rows:
        if row.get("type") != "assistant":
            continue
        for block in _content_blocks(row.get("message")):
            if block.get("type") != "tool_use":
                continue
            name = _text(block.get("name"))
            tool_input = block.get("input")
            if not isinstance(tool_input, dict):
                tool_input = {}
            local = browser_tab_hook.local_tool_name(name)
            family = browser_tab_hook.tool_family(name)
            roles = browser_tab_hook.BROWSER_TOOL_ROLES.get(family, {})
            report_creation_coverage = roles.get("reportCreationCoverage") is True
            result_tabs = _tab_ids(results.get(_text(block.get("id"))))
            created_tabs = _created_tab_ids(results.get(_text(block.get("id"))))
            if local == roles.get("create"):
                created_directly += bool(result_tabs) and report_creation_coverage
                owned.update(result_tabs)
                continue
            if local == roles.get("context") and tool_input.get("createIfEmpty") is True:
                created_from_context += bool(created_tabs) and report_creation_coverage
                owned.update(created_tabs)
                continue
            if local == roles.get("batch"):
                creation_routes = {
                    "create"
                    if action == roles.get("create")
                    else "context"
                    if action == roles.get("context")
                    and action_input.get("createIfEmpty") is True
                    else "navigate"
                    if action == roles.get("navigate")
                    and not action_input.get("tabId")
                    else ""
                    for action, action_input in browser_tab_hook.batch_actions(
                        name, tool_input
                    )
                } - {""}
                if creation_routes:
                    owned.update(created_tabs)
                if len(creation_routes) == 1 and created_tabs and report_creation_coverage:
                    route = next(iter(creation_routes))
                    created_directly += route == "create"
                    created_from_context += route == "context"
                    created_by_navigation += route == "navigate"
            for action, action_input in browser_tab_hook.page_actions(name, tool_input):
                tab = action_input.get("tabId")
                if (
                    local != roles.get("batch")
                    and action == roles.get("navigate")
                    and (tab is None or tab == "")
                ):
                    created_by_navigation += bool(created_tabs) and report_creation_coverage
                    owned.update(created_tabs)
                elif tab is not None and tab != "" and str(tab) not in owned:
                    unowned += 1
    return BrowserDiagnostics(
        unowned_page_actions=unowned,
        creation_parses_tabs_create_mcp=created_directly,
        creation_parses_tabs_context_mcp=created_from_context,
        creation_parses_navigate_without_tab=created_by_navigation,
    )


def _sum_browser_diagnostics(
    diagnostics: Iterable[BrowserDiagnostics],
) -> BrowserDiagnostics:
    rows = tuple(diagnostics)
    return BrowserDiagnostics(
        unowned_page_actions=sum(row.unowned_page_actions for row in rows),
        creation_parses_tabs_create_mcp=sum(
            row.creation_parses_tabs_create_mcp for row in rows
        ),
        creation_parses_tabs_context_mcp=sum(
            row.creation_parses_tabs_context_mcp for row in rows
        ),
        creation_parses_navigate_without_tab=sum(
            row.creation_parses_navigate_without_tab for row in rows
        ),
    )


def extract_diagnostics(
    transcripts: Iterable[Path], population: Iterable[Candidate]
) -> ExtractDiagnostics:
    candidates = tuple(population)
    transcript_rows = [read_transcript(path) for path in transcripts]
    rows = [row for source_rows in transcript_rows for row in source_rows]
    versions = tuple(sorted({_text(row.get("version")) for row in rows if _text(row.get("version"))}))
    codex = any(row.get("type") in CODEX_ROW_TYPES for row in rows)
    undeclared_rows = (
        sum(
            1
            for row in rows
            if _text(row.get("type")) not in CODEX_ROW_TYPES | CLAUDE_ROW_TYPES
        )
        if codex
        else 0
    )
    undeclared_payloads = sum(
        1
        for row in rows
        if row.get("type") == "response_item"
        and _text(_codex_payload(row).get("type")) not in CODEX_RESPONSE_TYPES
    )
    undeclared_envelopes = sum(
        1
        for candidate in candidates
        if candidate.kind not in ENVELOPE_ENTRY_KINDS
        for match in ENVELOPE_TAG.finditer(candidate.text)
        if match.group("tag") not in ENVELOPE_KINDS
    )
    launches = [candidate for candidate in candidates if candidate.kind == "subagent-launch"]
    launch_keys = {
        matched.group("id")
        for candidate in launches
        for matched in [AGENT_ID.search(candidate.text)]
        if matched is not None
    }
    notifications = [candidate for candidate in candidates if candidate.kind == "task-notification"]
    result_keys = {
        key
        for candidate in notifications
        if "<result>" in candidate.text
        for key in _notification_keys(candidate.text)
    }
    joined = len(launch_keys & result_keys)
    browser = _sum_browser_diagnostics(map(_browser_diagnostics, transcript_rows))
    return ExtractDiagnostics(
        harness_versions=versions,
        undeclared_envelopes=undeclared_envelopes,
        undeclared_codex_row_types=undeclared_rows,
        undeclared_codex_payload_types=undeclared_payloads,
        subagent_launches=len(launches),
        joined_results=joined,
        unjoined_launches=len(launches) - joined,
        notifications_without_join_key=sum(
            1 for candidate in notifications if not _notification_keys(candidate.text)
        ),
        browser=browser,
    )


def write_extract(
    run: Path,
    transcript: Path | None,
    submission: str,
    memory_index: Path,
) -> tuple[Path, int]:
    retire_orphan_pointers(run)
    posted_reading_fingerprint = _posted_reading_fingerprint(run, submission)
    population, transcripts, discovery = _collect_population(run, transcript)
    if not population:
        raise ValueError("candidate population is empty")
    round_number = _next_review_round(run, submission)
    destination = extract_path(run, submission, round_number)
    destination.parent.mkdir(parents=True, exist_ok=True)
    diagnostics = extract_diagnostics(transcripts, population)
    transcript_watermarks: dict[str, str] = {}
    for candidate in population:
        transcript_watermarks[candidate.transcript_id] = candidate.identifier
    lines = [
        "# PRIVATE AAR EXTRACT",
        "FORMAT: 2",
        "EXTRACTED-AT: " + datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        f"SUBMISSION: {submission}",
        f"POSTED-READING-FINGERPRINT: {posted_reading_fingerprint}",
        "TRANSCRIPTS: " + ", ".join(path.stem for path in transcripts),
        "TRANSCRIPT-PATHS: " + " | ".join(str(path.resolve()) for path in transcripts),
        "TRANSCRIPT-WATERMARKS: "
        + " | ".join(
            f"{transcript}={watermark}"
            for transcript, watermark in transcript_watermarks.items()
        ),
        f"TRANSCRIPTS-FOUND: {discovery.found}",
        f"TRANSCRIPTS-SKIPPED-BY-TIME: {discovery.skipped_by_time}",
        f"TRANSCRIPTS-SKIPPED-BY-BYTE-SEARCH: {discovery.skipped_by_byte_search}",
        f"TRANSCRIPTS-READ: {discovery.read}",
        f"POPULATION: {len(population)}",
        f"WATERMARK: {population[-1].identifier}",
        f"MEMORY-INDEX: {memory_index.resolve()}",
        "HARNESS-VERSIONS: " + (", ".join(diagnostics.harness_versions) or "none observed"),
        f"UNDECLARED-ENVELOPES: {diagnostics.undeclared_envelopes}",
        f"UNDECLARED-CODEX-ROW-TYPES: {diagnostics.undeclared_codex_row_types}",
        f"UNDECLARED-CODEX-PAYLOAD-TYPES: {diagnostics.undeclared_codex_payload_types}",
        f"SUBAGENT-LAUNCHES: {diagnostics.subagent_launches}",
        f"SUBAGENT-JOINED-RESULTS: {diagnostics.joined_results}",
        f"SUBAGENT-UNJOINED: {diagnostics.unjoined_launches}",
        f"NOTIFICATIONS-WITHOUT-JOIN-KEY: {diagnostics.notifications_without_join_key}",
        f"UNOWNED-BROWSER-PAGE-ACTIONS: {diagnostics.browser.unowned_page_actions}",
        f"TAB-CREATION-PARSES-TABS-CREATE-MCP: {diagnostics.browser.creation_parses_tabs_create_mcp}",
        f"TAB-CREATION-PARSES-TABS-CONTEXT-MCP: {diagnostics.browser.creation_parses_tabs_context_mcp}",
        f"TAB-CREATION-PARSES-NAVIGATE-WITHOUT-TAB: {diagnostics.browser.creation_parses_navigate_without_tab}",
        f"UNMARKED-PRIOR-REVIEWS: {_unmarked_prior_reviews(run, transcripts)}",
        "ENTRY-KINDS: "
        + " | ".join(
            f"{kind} = {description}"
            for kind, description in ENTRY_KIND_DESCRIPTIONS.items()
        ),
        "",
    ]
    for row in population:
        text_lines = row.text.splitlines() or [""]
        lines.extend(
            [
                f"## ENTRY: {row.identifier}",
                f"TRANSCRIPT: {row.transcript_id}",
                f"KIND: {row.kind}",
                f"TEXT-LINES: {len(text_lines)}",
                "TEXT:",
                *text_lines,
                "",
            ]
        )
    destination.write_text("\n".join(lines), encoding="utf-8")
    baseline_path(run, submission, round_number).write_text(
        json.dumps(snapshot(memory_index), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination, len(population)


def _parse_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    current: str | None = None
    for line in lines:
        match = FIELD.match(line)
        if match:
            current = match.group("name")
            fields[current] = match.group("value").strip()
        elif current and line.strip():
            fields[current] = f"{fields[current]} {line.strip()}".strip()
    return fields


def read_review(path: Path) -> Review:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read review {path.name}") from exc
    header: list[str] = []
    corrections: list[Correction] = []
    sustains: list[Sustain] = []
    current_event: str | None = None
    current_lines: list[str] = []
    mode = "header"

    def close() -> None:
        nonlocal current_event, current_lines
        if mode == "correction" and current_event is not None:
            corrections.append(
                Correction(current_event, MappingProxyType(_parse_fields(current_lines)))
            )
        elif mode == "sustain" and current_event is not None:
            sustains.append(
                Sustain(current_event, MappingProxyType(_parse_fields(current_lines)))
            )
        current_event, current_lines = None, []

    for line in lines:
        correction = CORRECTION_HEADING.match(line)
        sustain = SUSTAIN_HEADING.match(line)
        if correction:
            close()
            mode, current_event = "correction", correction.group("event")
        elif sustain:
            close()
            mode, current_event = "sustain", sustain.group("event")
        elif mode == "header":
            header.append(line)
        else:
            current_lines.append(line)
    close()
    fields = _parse_fields(header)
    return Review(
        path=path,
        fields=MappingProxyType(fields),
        corrections=tuple(corrections),
        sustains=tuple(sustains),
        corrections_none=fields.get("CORRECTIONS", "").casefold() == "none",
        sustains_none=fields.get("SUSTAINS", "").casefold() == "none",
    )


def _extract_document(
    path: Path,
) -> tuple[dict[str, str], set[str], dict[str, str]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read extract {path.name}") from exc
    try:
        header_end = lines.index("")
    except ValueError as exc:
        raise ValueError("extract header has no blank-line terminator") from exc
    fields = _parse_fields(lines[:header_end])
    format_version = fields.get("FORMAT", "1")
    extracted_at = fields.get("EXTRACTED-AT", "")
    if extracted_at:
        _utc_timestamp(extracted_at, "EXTRACTED-AT")
    if format_version == "1":
        identifiers = {
            line.partition(":")[2].strip()
            for line in lines[header_end + 1 :]
            if line.startswith("## ENTRY:")
        }
        return fields, identifiers, {}
    if format_version != "2":
        raise UnknownExtractFormat(f"unknown extract format {format_version}")
    if not fields.get("EXTRACTED-AT"):
        raise ValueError("format 2 extract has no EXTRACTED-AT field")
    identifiers: set[str] = set()
    entry_kinds: dict[str, str] = {}
    index = header_end + 1
    while index < len(lines):
        if not lines[index]:
            index += 1
            continue
        if not lines[index].startswith("## ENTRY:"):
            raise ValueError(f"extract entry expected at line {index + 1}")
        identifier = lines[index].partition(":")[2].strip()
        if not identifier or identifier in identifiers:
            raise ValueError("extract entry identifier is absent or duplicated")
        identifiers.add(identifier)
        index += 1
        entry_fields: list[str] = []
        while index < len(lines) and not lines[index].startswith("TEXT-LINES:"):
            entry_fields.append(lines[index])
            index += 1
        parsed_entry_fields = _parse_fields(entry_fields)
        if not _substance(parsed_entry_fields.get("TRANSCRIPT", "")):
            raise ValueError(f"extract entry {identifier} has no TRANSCRIPT field")
        entry_kind = parsed_entry_fields.get("KIND", "")
        if entry_kind not in ENTRY_KINDS:
            raise ValueError(f"extract entry {identifier} has an unknown KIND field")
        entry_kinds[identifier] = entry_kind
        if index >= len(lines):
            raise ValueError(f"extract entry {identifier} has no TEXT-LINES field")
        count_value = lines[index].partition(":")[2].strip()
        try:
            text_lines = int(count_value)
        except ValueError as exc:
            raise ValueError(f"extract entry {identifier} has a non-numeric TEXT-LINES field") from exc
        if text_lines < 0 or index + text_lines + 1 >= len(lines):
            raise ValueError(f"extract entry {identifier} has a truncated body")
        if lines[index + 1] != "TEXT:":
            raise ValueError(f"extract entry {identifier} has no TEXT field")
        index += text_lines + 2
    return fields, identifiers, entry_kinds


def _extract_metadata(path: Path) -> tuple[dict[str, str], set[str]]:
    fields, identifiers, _entry_kinds = _extract_document(path)
    return fields, identifiers


def _substance(value: str) -> bool:
    return bool(re.search(r"[A-Za-z0-9]{3}", value))


def _utc_timestamp(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} is not an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label} has no UTC offset")
    return parsed.astimezone(timezone.utc)


def _baseline(
    run: Path, submission: str, round_number: int = 1
) -> dict[str, str | None]:
    try:
        payload = json.loads(
            baseline_path(run, submission, round_number).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("baseline is absent or unreadable") from exc
    if not isinstance(payload, dict):
        raise ValueError("baseline is not an object")
    return {str(key): value if isinstance(value, str) else None for key, value in payload.items()}


def _target_changed(target: str, baseline: Mapping[str, str | None]) -> bool:
    path = Path(target).expanduser().resolve()
    return _hash(path) is not None and _hash(path) != baseline.get(str(path))


def _successful_gh_call(transcripts: Iterable[Path]) -> bool:
    for transcript in transcripts:
        rows = read_transcript(transcript)
        for row in rows:
            if row.get("type") != "event_msg":
                continue
            payload = row.get("payload")
            if not isinstance(payload, dict) or payload.get("type") != "item_completed":
                continue
            item = payload.get("item")
            if not isinstance(item, dict) or item.get("type") != "CommandExecution":
                continue
            command = item.get("command")
            commands = command if isinstance(command, list) else [command]
            if (
                item.get("status") == "completed"
                and item.get("exit_code") == 0
                and any(
                    isinstance(value, str) and shell_reader.has_executable(value, "gh")
                    for value in commands
                )
            ):
                return True
        tools = _tool_index(rows)
        gh_ids: set[str] = set()
        for row in rows:
            if row.get("type") != "assistant":
                continue
            for block in _content_blocks(row.get("message")):
                command = block.get("input", {}).get("command") if isinstance(block.get("input"), dict) else None
                if block.get("type") == "tool_use" and isinstance(command, str) and shell_reader.has_executable(command, "gh"):
                    gh_ids.add(_text(block.get("id")))
        for row in rows:
            if row.get("type") != "user":
                continue
            for block in _content_blocks(row.get("message")):
                if block.get("type") == "tool_result" and block.get("tool_use_id") in gh_ids and block.get("is_error") is not True:
                    return True
        if any(tool == "Bash" for tool in tools.values()) and gh_ids:
            # Older transcript rows omit ``is_error`` on a successful result.
            continue
    return False


def _survey_round(run: Path, submission: str, round_number: int) -> Scan:
    findings: list[Finding] = []
    record_path = review_path(run, submission, round_number)
    records = int(record_path.is_file())
    if not records:
        return Scan(submission, 0, 0, 0, 0, 0, (Finding("missing-review", submission),))
    try:
        review = read_review(record_path)
        baseline = _baseline(run, submission, round_number)
    except ValueError as exc:
        return Scan(submission, 1, 0, 0, 0, 0, (Finding("unscannable-review", str(exc)),))
    try:
        extract_fields, identifiers, entry_kinds = _extract_document(
            extract_path(run, submission, round_number)
        )
    except UnknownExtractFormat:
        raise
    except ValueError as exc:
        return Scan(submission, 1, 0, 0, 0, 0, (Finding("unscannable-extract", str(exc)),))

    for field in HEADER_FIELDS:
        value = review.fields.get(field, "")
        present = bool(value.strip()) if field in {"POPULATION", "UNREAD"} else _substance(value)
        if not present:
            findings.append(Finding("missing-header-field", field))
    extracted_at = extract_fields.get("EXTRACTED-AT", "")
    later_sittings = (
        count_later_sittings(run, _utc_timestamp(extracted_at, "EXTRACTED-AT"))
        if extracted_at
        else 0
    )
    post_cutoff = (
        extract_fields.get("FORMAT", "1") == "2"
        and _utc_timestamp(extracted_at, "EXTRACTED-AT")
        >= REVIEW_CLASSIFIER_ENTRY_CUTOFF
    )
    fingerprint_cutoff = bool(extracted_at) and (
        _utc_timestamp(extracted_at, "EXTRACTED-AT")
        >= POSTED_READING_FINGERPRINT_CUTOFF
    )
    if fingerprint_cutoff:
        recorded_fingerprint = extract_fields.get("POSTED-READING-FINGERPRINT", "")
        try:
            current_fingerprint = _posted_reading_fingerprint(run, submission)
        except ValueError:
            current_fingerprint = ""
        if (
            not re.fullmatch(r"[0-9a-f]{64}", recorded_fingerprint)
            or recorded_fingerprint != current_fingerprint
        ):
            findings.append(Finding("posted-reading-mismatch", submission))
    if post_cutoff and not _substance(review.fields.get("CLASSIFIER-ENTRY", "")):
        findings.append(Finding("missing-classifier-entry", "CLASSIFIER-ENTRY"))
    if extract_fields.get("UNMARKED-PRIOR-REVIEWS", "0") != "0":
        findings.append(
            Finding(
                "unmarked-prior-review",
                extract_fields.get("UNMARKED-PRIOR-REVIEWS", ""),
            )
        )
    if review.fields.get("SUBMISSION") != submission:
        findings.append(Finding("wrong-submission", review.fields.get("SUBMISSION", "")))
    try:
        population = int(review.fields.get("POPULATION", ""))
        unread = int(review.fields.get("UNREAD", ""))
    except ValueError:
        population, unread = 0, -1
        findings.append(Finding("non-numeric-coverage", "POPULATION or UNREAD"))
    expected_population = len(identifiers)
    if population != expected_population or review.fields.get("POPULATION") != extract_fields.get("POPULATION"):
        findings.append(Finding("population-mismatch", f"record {population}; extract {expected_population}"))
    if unread != 0:
        findings.append(Finding("unread-candidates", str(unread)))
    if review.fields.get("WATERMARK") != extract_fields.get("WATERMARK") or review.fields.get("WATERMARK") not in identifiers:
        findings.append(Finding("watermark-mismatch", review.fields.get("WATERMARK", "")))
    if review.fields.get("TRANSCRIPTS") != extract_fields.get("TRANSCRIPTS"):
        findings.append(Finding("transcript-mismatch", review.fields.get("TRANSCRIPTS", "")))
    if not review.corrections and not review.corrections_none:
        findings.append(Finding("missing-correction-verdict", "neither records nor CORRECTIONS: none"))
    if review.corrections and review.corrections_none:
        findings.append(Finding("contradictory-correction-verdict", "records and CORRECTIONS: none"))
    if not review.sustains and not review.sustains_none:
        findings.append(Finding("missing-sustain-verdict", "neither records nor SUSTAINS: none"))
    if review.sustains and review.sustains_none:
        findings.append(Finding("contradictory-sustain-verdict", "records and SUSTAINS: none"))

    transcript_paths = [
        Path(value.strip())
        for value in extract_fields.get("TRANSCRIPT-PATHS", "").split("|")
        if value.strip()
    ]
    tracked_files = {path.resolve() for path in _tracked_files()}
    for correction in review.corrections:
        if correction.event not in identifiers:
            findings.append(Finding("unknown-correction-event", correction.event))
        elif entry_kinds.get(correction.event) in EXTRACTOR_WRITTEN_ENTRY_KINDS:
            findings.append(
                Finding("correction-on-extractor-written-entry", correction.event)
            )
        for field in CORRECTION_FIELDS:
            if not _substance(correction.fields.get(field, "")):
                findings.append(Finding("missing-correction-field", f"{correction.event}: {field}"))
        if correction.fields.get("CORRECTOR") not in CORRECTORS:
            findings.append(Finding("unknown-corrector", correction.fields.get("CORRECTOR", "")))
        if correction.fields.get("IN-ERROR") not in CORRECTORS:
            findings.append(Finding("unknown-error-party", correction.fields.get("IN-ERROR", "")))
        disposition = correction.fields.get("DISPOSITION", "")
        if disposition not in DISPOSITIONS:
            findings.append(Finding("unknown-disposition", disposition or correction.event))
            continue
        target = correction.fields.get("TARGET", "")
        landing = correction.fields.get("LANDING", "")
        if disposition in {"skill-file", "tracker-ticket"}:
            if not GH_ISSUE.fullmatch(landing):
                findings.append(Finding("unlanded-ticket", correction.event))
            elif transcript_paths and not _successful_gh_call(transcript_paths):
                findings.append(Finding("missing-gh-call", correction.event))
        elif disposition == "memory-write":
            if not _target_changed(target, baseline):
                findings.append(Finding("unlanded-memory", correction.event))
        elif disposition == "check":
            resolved = Path(target).expanduser().resolve()
            if resolved not in tracked_files or not _target_changed(target, baseline):
                findings.append(Finding("unlanded-check", correction.event))

    for sustain in review.sustains:
        if sustain.event not in identifiers:
            findings.append(Finding("unknown-sustain-event", sustain.event))
        if not _substance(sustain.fields.get("SUMMARY", "")):
            findings.append(Finding("bare-sustain", sustain.event))
    counts: dict[tuple[str, str, str], int] = {}
    for correction in review.corrections:
        key = (
            "correction",
            correction.fields.get("CORRECTOR", "unknown") or "unknown",
            entry_kinds.get(correction.event, "unknown"),
        )
        counts[key] = counts.get(key, 0) + 1
    for sustain in review.sustains:
        key = ("sustain", "n/a", entry_kinds.get(sustain.event, "unknown"))
        counts[key] = counts.get(key, 0) + 1
    kind_counts = tuple(
        EntryKindCount(record, corrector, kind, count)
        for (record, corrector, kind), count in sorted(counts.items())
    )
    diagnostic_counts = {
        name: _optional_count(extract_fields, field)
        for name, field in {
            "transcripts_found": "TRANSCRIPTS-FOUND",
            "transcripts_skipped_by_time": "TRANSCRIPTS-SKIPPED-BY-TIME",
            "transcripts_skipped_by_byte_search": "TRANSCRIPTS-SKIPPED-BY-BYTE-SEARCH",
            "transcripts_read": "TRANSCRIPTS-READ",
        }.items()
    }
    browser = BrowserDiagnostics(
        unowned_page_actions=_optional_count(
            extract_fields, "UNOWNED-BROWSER-PAGE-ACTIONS"
        ),
        creation_parses_tabs_create_mcp=_optional_count(
            extract_fields, "TAB-CREATION-PARSES-TABS-CREATE-MCP"
        ),
        creation_parses_tabs_context_mcp=_optional_count(
            extract_fields, "TAB-CREATION-PARSES-TABS-CONTEXT-MCP"
        ),
        creation_parses_navigate_without_tab=_optional_count(
            extract_fields, "TAB-CREATION-PARSES-NAVIGATE-WITHOUT-TAB"
        ),
    )
    return Scan(
        submission=submission,
        records=records,
        population=population,
        corrections=len(review.corrections),
        sustains=len(review.sustains),
        unread=unread,
        findings=tuple(findings),
        kind_counts=kind_counts,
        later_sittings=later_sittings,
        browser=browser,
        **diagnostic_counts,
    )


def _optional_count(fields: Mapping[str, str], name: str) -> int:
    try:
        return int(fields.get(name, "0") or "0")
    except ValueError:
        return 0


def survey(run: Path, submission: str) -> Scan:
    round_numbers = _review_round_numbers(run, submission) or (1,)
    scans = tuple(
        _survey_round(run, submission, round_number)
        for round_number in round_numbers
    )
    rounds = tuple(
        RoundScan(
            number=round_number,
            corrections=scan.corrections,
            unlanded=sum(
                finding.kind.startswith("unlanded-") for finding in scan.findings
            ),
        )
        for round_number, scan in zip(round_numbers, scans)
        if scan.records or extract_path(run, submission, round_number).is_file()
    )
    combined_counts: dict[tuple[str, str, str], int] = {}
    for scan in scans:
        for row in scan.kind_counts:
            key = (row.record, row.corrector, row.kind)
            combined_counts[key] = combined_counts.get(key, 0) + row.count
    return Scan(
        submission=submission,
        records=sum(scan.records for scan in scans),
        population=sum(scan.population for scan in scans),
        corrections=sum(scan.corrections for scan in scans),
        sustains=sum(scan.sustains for scan in scans),
        unread=sum(scan.unread for scan in scans),
        findings=tuple(finding for scan in scans for finding in scan.findings),
        rounds=rounds,
        kind_counts=tuple(
            EntryKindCount(record, corrector, kind, count)
            for (record, corrector, kind), count in sorted(combined_counts.items())
        ),
        later_sittings=sum(scan.later_sittings for scan in scans),
        transcripts_found=sum(scan.transcripts_found for scan in scans),
        transcripts_skipped_by_time=sum(
            scan.transcripts_skipped_by_time for scan in scans
        ),
        transcripts_skipped_by_byte_search=sum(
            scan.transcripts_skipped_by_byte_search for scan in scans
        ),
        transcripts_read=sum(scan.transcripts_read for scan in scans),
        browser=_sum_browser_diagnostics(scan.browser for scan in scans),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    lines = [
        f"after-action review over {source}",
        "",
        f"  review records                  {scan.records}",
        f"  candidate population            {scan.population}",
        f"  correction records              {scan.corrections}",
        f"  sustain records                 {scan.sustains}",
        f"  unread candidates               {scan.unread}",
        f"  transcripts found               {scan.transcripts_found}",
        f"  transcripts skipped by time     {scan.transcripts_skipped_by_time}",
        f"  transcripts skipped by bytes    {scan.transcripts_skipped_by_byte_search}",
        f"  transcripts read                {scan.transcripts_read}",
        f"  sittings begun after extract    {scan.later_sittings}",
        f"  unowned browser page actions    {scan.browser.unowned_page_actions} (reported, {NOT_GRADED})",
        f"  tab creation parses: tabs_create_mcp  {scan.browser.creation_parses_tabs_create_mcp}",
        f"  tab creation parses: tabs_context_mcp {scan.browser.creation_parses_tabs_context_mcp}",
        f"  tab creation parses: navigate no tab  {scan.browser.creation_parses_navigate_without_tab}",
        f"  findings                        {len(scan.findings)}",
    ]
    lines.extend(
        f"  round {round.number} corrections {round.corrections}; "
        f"unlanded {round.unlanded}"
        for round in scan.rounds
    )
    if scan.kind_counts:
        lines.extend(["", "  corrector by entry kind"])
        lines.extend(
            f"    {row.record} | {row.corrector} | {row.kind} | {row.count}"
            for row in scan.kind_counts
        )
    if show and scan.findings:
        lines.extend(["", "  findings (private - read, do not paste):"])
        lines.extend(f"    {row.kind}: {row.detail}" for row in scan.findings)
    lines.extend(["", "  declared limits:"])
    lines.extend(f"    {subject}" for subject, _reason in DECLARED_LIMITS)
    return "\n".join(lines)


def completion_finding(run: Path, submissions: Iterable[str]) -> str | None:
    """The expected row shared by ``COMPLETION_GRADERS``."""
    for submission in submissions:
        scan = survey(run, submission)
        if scan.findings or scan.unread:
            return f"{EXPECTED_ROW} is incomplete for {submission}"
    return None


def _same_path(left: Path, right: Path) -> bool:
    """Compare existing paths by identity before falling back to spelling."""
    try:
        return left.samefile(right)
    except OSError:
        return left.resolve() == right.resolve()


def is_live_run(run: Path) -> bool:
    root = (repo_root.scratch_root() / "runs").resolve()
    return _same_path(run.parent, root)


def completion_gate(run: Path, submission: str | None) -> tuple[bool, str]:
    """Grade the shared expected row only for an explicitly terminal submission."""
    if submission is None:
        return False, f"{EXPECTED_ROW}: {NOT_GRADED} - --submission was not supplied"
    finding = completion_finding(run, (submission,))
    return (finding is not None, f"{EXPECTED_ROW}: {'finding - ' + finding if finding else 'clean'}")


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        if value.lstrip().startswith(("{", "[")):
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError:
                decoded = None
            if decoded is not None and decoded != value:
                yield from _strings(decoded)
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _strings(nested)


def discover_run_directories(rows: Iterable[dict[str, Any]]) -> tuple[Path, ...]:
    root = repo_root.scratch_root() / "runs"
    found: set[Path] = set()
    for row in rows:
        inputs: list[Any] = []
        if row.get("type") == "assistant":
            inputs.extend(
                block.get("input")
                for block in _content_blocks(row.get("message"))
                if block.get("type") == "tool_use"
            )
        payload = _codex_payload(row)
        if payload.get("type") in {"custom_tool_call", "function_call"}:
            inputs.extend((payload.get("input"), payload.get("arguments")))
        for input_value in inputs:
            for value in _strings(input_value):
                normalized = value
                while "\\\\" in normalized:
                    normalized = normalized.replace("\\\\", "\\")
                for match in RUN_REFERENCE.finditer(normalized):
                    candidate = (root / match.group("key")).resolve()
                    if candidate.is_dir() and candidate.is_relative_to(root.resolve()):
                        found.add(candidate)
    return tuple(sorted(found))


def transcript_roots() -> tuple[Path, ...]:
    home = Path.home()
    return (
        home / ".claude" / "projects",
        home / ".codex" / "sessions",
        home / ".codex" / "archived_sessions",
    )


def _run_created_at(run: Path) -> float | None:
    stat = run.stat()
    birthtime = getattr(stat, "st_birthtime", None)
    if isinstance(birthtime, (int, float)):
        return float(birthtime)
    if sys.platform == "win32":
        return float(stat.st_ctime)
    return None


def _raw_contains(path: Path, needle: bytes) -> bool:
    overlap = max(len(needle) - 1, 0)
    tail = b""
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            block = tail + chunk
            if needle in block:
                return True
            tail = block[-overlap:] if overlap else b""
    return False


def _is_codex_subagent(rows: Iterable[dict[str, Any]]) -> bool:
    for row in rows:
        if row.get("type") != "session_meta":
            continue
        payload = row.get("payload")
        source = payload.get("source") if isinstance(payload, dict) else None
        if isinstance(source, str):
            return "subagent" in source.casefold()
        if isinstance(source, dict):
            return "subagent" in source
        return False
    return False


def discover_transcripts(run: Path, explicit: Path | None = None) -> TranscriptDiscovery:
    """Find every main sitting that names ``run``, bounded before parsing."""
    forced = explicit.resolve() if explicit is not None else None
    paths: set[Path] = {forced} if forced is not None else set()
    if is_live_run(run):
        paths.update(
            path.resolve()
            for root in transcript_roots()
            if root.is_dir()
            for path in root.rglob("*.jsonl")
        )
    ordered = tuple(sorted(paths, key=lambda path: str(path).casefold()))
    created_at = _run_created_at(run)
    needle = run.name.encode("utf-8")
    selected: list[Path] = []
    skipped_by_time = 0
    skipped_by_byte_search = 0
    for path in ordered:
        if "subagents" in {part.casefold() for part in path.parts}:
            continue
        try:
            if (
                path != forced
                and created_at is not None
                and path.stat().st_mtime < created_at - 24 * 60 * 60
            ):
                skipped_by_time += 1
                continue
            if path != forced and not _raw_contains(path, needle):
                skipped_by_byte_search += 1
                continue
            rows = read_transcript(path)
        except (OSError, ValueError):
            continue
        if _is_codex_subagent(rows):
            continue
        if path == forced or any(
            _same_path(run, candidate) for candidate in discover_run_directories(rows)
        ):
            selected.append(path)
    return TranscriptDiscovery(
        paths=tuple(selected),
        found=len(ordered),
        skipped_by_time=skipped_by_time,
        skipped_by_byte_search=skipped_by_byte_search,
        read=len(selected),
    )


def _transcript_started_at(rows: Iterable[dict[str, Any]]) -> datetime | None:
    for row in rows:
        timestamp = _text(row.get("timestamp"))
        if timestamp:
            try:
                return _utc_timestamp(timestamp, "transcript timestamp")
            except ValueError:
                continue
    return None


def count_later_sittings(run: Path, extracted_at: datetime) -> int:
    return sum(
        1
        for path in discover_transcripts(run).paths
        for started_at in [_transcript_started_at(read_transcript(path))]
        if started_at is not None and started_at > extracted_at
    )


USAGE = (
    "usage: aar_scan.py <run-directory> --submission <key> "
    "[--transcript <jsonl> --memory-index <path> --extract] [--show]"
)


def validate(parsed: run_grader.Parsed) -> str | None:
    if not parsed.value("--submission"):
        return "--submission is required"
    if parsed.enabled("--extract") and not parsed.value("--memory-index"):
        return "--extract requires --memory-index"
    return None


def load(parsed: run_grader.Parsed) -> Path:
    run = Path(parsed.source).expanduser().resolve()
    if not run.is_dir():
        raise run_grader.SourceError(f"no directory named {run.name}")
    return run


def grade(run: Path, parsed: run_grader.Parsed) -> run_grader.Grade[Scan] | run_grader.EarlyExit:
    submission = parsed.value("--submission")
    assert submission is not None  # validate owns this invocation requirement
    try:
        retire_orphan_pointers(run)
    except OSError as exc:
        return run_grader.EarlyExit(
            2,
            stderr=(f"after-action review NOT SCANNED: {exc}",),
        )
    if parsed.enabled("--extract"):
        transcript_value = parsed.value("--transcript")
        memory_value = parsed.value("--memory-index")
        assert memory_value is not None  # validate owns this invocation requirement
        try:
            transcript = (
                Path(transcript_value).expanduser().resolve()
                if transcript_value
                else None
            )
            destination, count = write_extract(
                run, transcript, submission, Path(memory_value).expanduser().resolve()
            )
            extract_fields, _identifiers = _extract_metadata(destination)
        except (OSError, ValueError, subprocess.SubprocessError, git_paths.GitPathError) as exc:
            return run_grader.EarlyExit(
                2,
                stderr=(f"after-action review NOT SCANNED: {exc}",),
            )
        return run_grader.EarlyExit(
            0,
            stdout=(
                f"after-action review extract over {run.name}",
                f"  candidate population            {count}",
                f"  transcripts found               {extract_fields['TRANSCRIPTS-FOUND']}",
                f"  transcripts skipped by time     {extract_fields['TRANSCRIPTS-SKIPPED-BY-TIME']}",
                f"  transcripts skipped by bytes    {extract_fields['TRANSCRIPTS-SKIPPED-BY-BYTE-SEARCH']}",
                f"  transcripts read                {extract_fields['TRANSCRIPTS-READ']}",
                f"  private extract written         {destination.name}",
            ),
        )

    try:
        scan = survey(run, submission)
    except UnknownExtractFormat as exc:
        return run_grader.EarlyExit(
            2,
            stderr=(f"after-action review NOT SCANNED: {exc}",),
        )
    return run_grader.Grade(
        scan=scan,
        source=run.name,
        findings_failed=bool(scan.findings),
    )


GRADER = run_grader.Grader(
    usage=USAGE,
    load=load,
    grade=grade,
    format_report=format_report,
    options=(
        run_grader.Option("--show"),
        run_grader.Option(
            "--submission", takes_value=True, missing_value="--submission needs a key"
        ),
        run_grader.Option("--transcript", takes_value=True),
        run_grader.Option("--memory-index", takes_value=True),
        run_grader.Option("--extract"),
    ),
    validate=validate,
    source_error_to_stdout=False,
)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    return run_grader.run(GRADER, arguments)


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
