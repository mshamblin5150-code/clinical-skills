#!/usr/bin/env python3
"""Extract and grade the private after-action review for one submission.

    python tools/aar_scan.py <run-directory> --transcript <session.jsonl> \
        --submission <submission-key> --memory-index <MEMORY.md> --extract
    python tools/aar_scan.py <run-directory> --submission <submission-key> \
        --memory-index <MEMORY.md> --extract --rebuild-round <number>
    python tools/aar_scan.py <run-directory> --submission <submission-key> [--show]
    python tools/aar_scan.py <run-directory> --submission <submission-key> \
        --measure-memory [--round <number>]

The first form writes a reduced, private review packet under ``<run>/aar/``.
It keeps human turns, assistant text, subagent result bodies, and tool names and
statuses. Tool-result bodies are otherwise dropped. The packet fixes the
candidate population; a fresh adversarial reader, not this command, classifies
which candidates are observed corrections and writes the review record.
``ENTRY_KINDS`` owns the extract label vocabulary and its generated legend.

The rebuild form repairs a refused round only when its recorded entries match.
The final form grades the record. Counts are safe to paste; ``--show`` names
private findings and must not be pasted. A run directory and every artifact
under ``aar/`` are private working material.
The measuring form retains the newest round's memory index counts after memory
writes. Grading reads the retained measurement rather than the live index.

The complete coverage boundary is ``DECLARED_LIMITS``. This docstring points at
that object and does not maintain a second copy of its rows. #814.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256
import completion_checks
import json
import os
import importlib
from pathlib import Path
import re
import subprocess
import sys
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from console_codec import use_utf8
from discussion_artifact import REREAD_BLOCK
import git_paths
import memory_index
import shell_reader
import command_reader
import shlex
import repo_root
import run_grader
import browser_tab_hook
import tree_walk
from run_record_reader import (
    RecordShapeError, UnreadableRecord, fault_report, object_record, read_tool_record,
    locked_record, update_tool_record, RecordUpdate, mark_not_graded,
    read_handwritten_record, check_handwritten_text, HandwrittenKind, DamagedRecord, damaged_record_result,
)


NOT_GRADED = run_grader.NOT_GRADED
REVIEW_CLASSIFIER_ENTRY_CUTOFF = completion_checks.registry()["aar_scan:review-classifier-entry"][0]
POSTED_READING_FINGERPRINT_CUTOFF = completion_checks.registry()["aar_scan:posted-reading-fingerprint"][0]
UNREAD_REMAINDER_CUTOFF = completion_checks.registry()["aar_scan:unread-remainder"][0]
LANDING_OUTPUT_CUTOFF = completion_checks.registry()["aar_scan:landing-output"][0]
MEMORY_MEASUREMENT_CUTOFF = completion_checks.registry()["aar_scan:memory-measurement"][0]
SYSTEM_SUBTYPE_CUTOFF = completion_checks.registry()["aar_scan:system-subtype"][0]
REVERSAL_CANDIDATES_CUTOFF = completion_checks.registry()["aar_scan:reversal-candidates"][0]
UNVERIFIED_CAUSE_CUTOFF = completion_checks.registry()["aar_scan:cause-line"][0]
UNVERIFIED_CAUSE_WARNING = "**Cause unverified:** the review's reader could not see the tool output this cause rests on; reread the run's transcript before building on it."
MEMORY_INDEX_LIMITS = MappingProxyType({"lines": 200, "characters": 25000, "release": "2.1.284"})


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
    {"tool-call", "subagent-launch", "inter-agent-metadata", "departure-list", "reversal-candidates"}
)

ENTRY_KIND_DESCRIPTIONS: Mapping[str, str] = MappingProxyType(
    {
        "clinician": "Clinician's words in an unflagged user row, apart from recognized envelopes",
        "agents-instructions": "Codex injected instructions item",
        "codex-question": "Codex question and question identifier",
        "codex-app-page": "Codex open page envelope",
        "codex-skill": "Codex skill envelope",
        "cross-session-message": "relayed session envelope",
        "david-lifecycle-wake": "DAVID lifecycle wake envelope",
        "assistant": "assistant text block",
        "tool-call": "tool invocation",
        "tool-status": "tool completion status",
        "subagent-launch": "subagent launch acknowledgment",
        "subagent-result": "subagent return body",
        "task-notification": "task notification envelope",
        "skill-prompt": "flagged skill prompt injection",
        "harness-meta": "flagged user or read system harness row with no recognized envelope",
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
        "departure-list": "recorded departures and their go-ahead from a dated proposal file",
        "reversal-candidates": "the orchestrator's per-round observed reversals for independent re-derivation",
    }
)
ENTRY_KINDS = tuple(ENTRY_KIND_DESCRIPTIONS)
ENVELOPE_KINDS: Mapping[str, str] = MappingProxyType(
    {
        "task-notification": "task-notification",
        "system-reminder": "system-reminder",
        "command-name": "command-name",
        "command-message": "command-name",
        "external_codex_apps_open_page": "codex-app-page",
        "skill": "codex-skill",
        "cross-session-message": "cross-session-message",
        "david_lifecycle_wake": "david-lifecycle-wake",
        "send_user_message_question_reply": "codex-question",
        "local-command-stdout": "local-command-stdout",
        "ci-monitor-event": "ci-monitor-event",
        "recommended_plugins": "recommended-plugins",
        "codex_delegation": "codex-delegation",
        "environment_context": "environment-context",
    }
)
ENVELOPE_ENTRY_KINDS = frozenset(ENVELOPE_KINDS.values()) | {"agents-instructions"}
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

# Top-level rows, Codex payloads, and Claude blocks deliberately left unread.
NAMED_UNREAD_TYPES: Mapping[str, str] = MappingProxyType(
    {
        "last-prompt": "A 200-character echo of a turn the review already reads (ADR 0285 ruling 4).",
        "api-request": "Request bookkeeping: model parameters, cache control and digests (#2052).",
        "api-request-shape": "Request bookkeeping: the system prompt and tool definitions (#2052).",
        "api-request-blob": "The API-request copy of turns the review already reads (#2052).",
        "tools-used": "Tool names used before a context summary; no turn text (#2072).",
        "bridge-session": "Session and harness state.",
        "atis-latch": "Session and harness state.",
        "mode": "Session and harness state.",
        "permission-mode": "Session and harness state.",
        "cost-state": "Session and harness state.",
        "custom-title": "Session names, mostly generated.",
        "ai-title": "Session names, mostly generated.",
        "agent-name": "Session names, mostly generated.",
        "pr-link": "A link to a pull request.",
        "frame-link": "A link to an artifact.",
        "file-history-delta": "File bookkeeping.",
        "artifact-autoreact-ledger": "Artifact bookkeeping.",
        "artifact-comment-monitor": "Artifact bookkeeping.",
        "file-history-snapshot": "File bookkeeping.",
        "progress": "Harness progress.",
        "event_msg": "Harness event state; tool success is read separately for landing evidence.",
        "turn_context": "Session and harness state.",
        "token_usage_record": "Harness usage state.",
        "world_state": "Session and harness state.",
        "session_meta": "Session metadata.",
        "web_search_call": "Native web-search operation metadata; ordinary result bodies are outside the review.",
        "tool_search_call": "Harness tool-discovery operation metadata.",
        "tool_search_output": "Harness tool definitions; ordinary tool-result bodies are outside the review.",
        "image_generation_call": "Native image-generation metadata; image content is outside the text review.",
        "reasoning": "Reasoning is outside the population (ADR 0285 ruling 3).",
        "thinking": "Reasoning is outside the population (ADR 0285 ruling 3).",
    }
)

READ_SYSTEM_SUBTYPES = frozenset({"local_command", "model_refusal_fallback", "informational"})
NAMED_UNREAD_SYSTEM_SUBTYPES: Mapping[str, str] = MappingProxyType(
    {
        "stop_hook_summary": "Hook bookkeeping; any hook feedback the session saw is read where it was delivered.",
        "api_error": "A failed request and its retry; nothing said was reversed.",
        "compact_boundary": "Compaction marker; the summary it bounds is read.",
        "turn_duration": "Timing.",
    }
)

ROWS: Mapping[str, str] = MappingProxyType(
    {
        "coverage-mismatch": "The unread remainder differs from its recorded components.",
        "missing-review": "the submission has no review record",
        "memory-index-measurement": "the round has no valid memory-index measurement",
        "memory-index-overflow": "the recorded memory index exceeds its load limits",
        "memory-index-unplaced": "a recorded memory file has no place in any memory index",
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
        "reversal-candidates": "the round's reversal candidates or their answers are missing or invalid",
        "sustain-on-reversal-candidates": "a sustain rests on the orchestrator's reversal claims",
        "missing-landing-search": "a tracker landing has no preceding successful issue search",
        "cause-line": "a correction has no well-formed cause pointers to real entries in its round",
        "cause-overrule": "a cause changes other than shown to unverified with a reason",
        "unverified-disposition": "an unverified cause lands outside a tracker or skill-file ticket",
        "unverified-publication": "an unverified landing has no recognized body-file warning and required create labels",
    }
)
KINDS = tuple(ROWS)

DECLARED_LIMITS = (
    ("aar_scan-record-coverage", 'aar_scan record reads use the shared decoder boundary; damaged bookkeeping leaves its dependent checks not graded and contributes one record per command to coverage. Absence preserves the existing caller meaning.'),
    ("reversal candidate completeness", "A careless none or an omitted reversal is not detected; answers establish neither independent discovery nor correct classification."),
    ("landing search adequacy", "A successful issue search proves neither adequate terms nor a correct landing target; shell_reader bounds recognized commands and transcript result shapes."),
    (
        "withdrawn reply text",
        "A refusal-fallback notice is read, but withdrawn replies not stored by the harness cannot enter the population.",
    ),
    (
        "system subtype meaning",
        "Only the subtype key identifies a system row; changed meaning under the same subtype is not detected.",
    ),
    (
        "memory index outside the sitting",
        "Only the recorded Claude Code index measurement is graded; later growth, other memory mechanisms, and limit changes without a release change are outside this row. Subject list sizes are reported and never graded (ADR 0391 ruling 9).",
    ),
    (
        "reasoning-only correction",
        "A correction that appears only in Codex reasoning or Claude thinking is outside the population by ADR 0285 ruling 3.",
    ),
    (
        "last-prompt-only text",
        "Text that appears only in last-prompt is not reachable.",
    ),
    (
        "api-request-blob-only text",
        "Text that appears only in an api-request-blob is not reachable (#2052).",
    ),
    (
        "wrong unread reason",
        "A type named for the wrong reason stays unread until its reason is revisited.",
    ),
    (
        "nested named content",
        "Nested content inside a named type is not walked by the remainder count.",
    ),
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
        "departure list shape",
        "Only direct proposed-YYYY-MM-DD.md files and their first literal ## Departures section through the next level-1/2 heading are read; differently named or headed material is outside this population.",
    ),
    (
        "browser tab ownership",
        "The transcript cannot reveal a clinician handover or prove a conditional tab creation unless the tool result marks it, so ownership is reported conservatively and never graded.",
    ),
    ("locked record publication", "AAR writers take the allocation resource before round, retirement and archive decisions, then lock each actual record for its shared atomic update. Extract and baseline are separate publications, not a multi-file atomic transaction; an extract may remain if its later baseline publication fails."),
    ("unverified cause", "A cause resting on an agent's explanation of dropped tool output is marked, not checked. The grader requires cause pointers and restricts unverified landings to warning-bearing tickets, but cannot prove that the reader noticed every narrated cause or that a shown entry supports it. A not-shown candidate is counted separately and establishes no correction. Publication recognition uses the existing successful Claude tool-result and Codex CommandExecution shapes and command_reader body-file grammar. Multiple command strings sharing output refuse; a single gh publication may have only literal cd && prefixes. Other compound or unknown shapes refuse. The file is read at grading time, not retained as its publication-time bytes; matching command evidence cannot prove the file was unchanged."),
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
GH_ISSUE = re.compile(r"https://github\.com/[^/]+/[^/]+/issues/[0-9]+(?:#issuecomment-[0-9]+)?\Z")


@dataclass(frozen=True)
class Candidate:
    identifier: str
    transcript_id: str
    kind: str
    text: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExtractEntry:
    identifier: str
    transcript_id: str
    kind: str
    text: str


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
    candidate_answers: tuple[tuple[str, str], ...] = ()


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
    undeclared_row_types: int
    undeclared_codex_payload_types: int
    subagent_launches: int
    joined_results: int
    unjoined_launches: int
    notifications_without_join_key: int
    browser: BrowserDiagnostics
    undeclared_system_subtypes: int = 0
    agents_instructions: int = 0

    @property
    def unread_remainder(self) -> int:
        return self.undeclared_row_types + self.undeclared_codex_payload_types + self.undeclared_system_subtypes


@dataclass(frozen=True)
class TranscriptDiscovery:
    paths: tuple[Path, ...]
    found: int
    skipped_by_time: int
    skipped_by_byte_search: int
    read: int
    unread: int = 0
    unreadable_directories: int = 0
    links_not_entered: int = 0


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
    transcripts_unread: int = 0
    unreadable_directories: int = 0
    links_not_entered: int = 0
    browser: BrowserDiagnostics = BrowserDiagnostics()
    unread_remainder: int | None = None
    unmeasured_rounds: int = 0
    memory_reports: tuple[str, ...] = ()
    system_reports: tuple[str, ...] = ()


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
    if value.startswith("<local-command-caveat>"):
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


def _text_pieces(value: str) -> list[tuple[str, str]]:
    """Read declared envelopes without opening their contents, except answer fields."""
    pieces: list[tuple[str, str]] = []
    cursor = 0
    tags = ENVELOPE_KINDS.keys() | {"command-args"}
    for match in ENVELOPE_TAG.finditer(value):
        if match.start() < cursor or match.group("tag") not in tags:
            continue
        tag = match.group("tag")
        # Match nested instances of the same envelope before resuming outside it.
        tokens = re.finditer(r"</?" + re.escape(tag) + r"(?:\s[^>]*|)>", value[match.start():])
        depth = 0
        end = len(value)
        content_start = match.end()
        content_end = end
        for token in tokens:
            if token.start() == 0:
                content_start = match.start() + token.end()
            depth += -1 if token.group().startswith("</") else 1
            if depth == 0:
                content_end = match.start() + token.start()
                end = match.start() + token.end()
                break
        before = value[cursor:match.start()].strip()
        if before:
            pieces.append(("clinician", before))
        body = value[match.start():end].strip()
        inside = value[content_start:content_end].strip()
        if tag == "command-args":
            if inside:
                pieces.append(("clinician", inside))
        elif tag == "send_user_message_question_reply":
            try:
                answers = json.loads(inside)
            except (ValueError, TypeError):
                answers = None
            if (isinstance(answers, list) and answers and all(
                isinstance(item, dict) and all(isinstance(item.get(key), str)
                for key in ("question", "questionItemId", "answer")) for item in answers
            )):
                pieces.append(("codex-question", json.dumps([
                    {key: item[key] for key in ("question", "questionItemId")}
                    for item in answers
                ], ensure_ascii=False)))
                pieces.extend(("clinician", item["answer"].strip())
                              for item in answers if item["answer"].strip())
            else:
                pieces.append(("codex-question", body))
        else:
            pieces.append((ENVELOPE_KINDS[tag], body))
        cursor = end
    if value[cursor:].strip():
        pieces.append(("clinician", value[cursor:].strip()))
    return pieces


def _agents_instructions(value: str) -> bool:
    return value.strip().startswith("# AGENTS.md instructions")


def _user_pieces(row: Mapping[str, Any]) -> list[tuple[str, str]]:
    if row.get("type") == "user":
        values = [_human_text(row)]
    elif row.get("type") == "response_item":
        payload = _codex_payload(row)
        if payload.get("type") != "message" or payload.get("role") != "user":
            return []
        # Only injected instructions require item boundaries. Ordinary text
        # remains one contiguous run, even when the harness stores several items.
        values: list[str] = []
        for block in _content_blocks(payload):
            if block.get("type") != "input_text":
                continue
            value = _text(block.get("text")).strip()
            if not value:
                continue
            if values and not _agents_instructions(value) and not _agents_instructions(values[-1]):
                values[-1] += "\n" + value
            else:
                values.append(value)
    else:
        return []
    pieces: list[tuple[str, str]] = []
    for value in values:
        if not value:
            continue
        if row.get("isMeta") or row.get("isCompactSummary") or row.get("isSidechain"):
            pieces.append((_human_kind(row, value) if not row.get("isSidechain")
                           else "harness-meta", value))
        elif _agents_instructions(value) and row.get("type") == "response_item":
            pieces.append(("agents-instructions", value))
        else:
            pieces.extend(_text_pieces(value))
    # Adjacent machine envelopes form one entry labeled by the first envelope.
    merged: list[tuple[str, str]] = []
    for kind, text in pieces:
        if merged and kind in ENVELOPE_ENTRY_KINDS and merged[-1][0] in ENVELOPE_ENTRY_KINDS:
            previous_kind, previous_text = merged[-1]
            merged[-1] = (previous_kind, previous_text + "\n" + text)
        else:
            merged.append((kind, text))
    return merged


def clinician_pieces(row: Mapping[str, Any]) -> tuple[str, ...]:
    """Each whole piece of the Clinician's words, shared with approval readers."""
    if row.get("isSidechain") or row.get("isMeta") or row.get("isCompactSummary"):
        return ()
    # Legacy relay prefixes still cannot supply approval evidence (ADR 0310).
    # Their extractor label remains unchanged; a prefix is not a declared envelope.
    return tuple(text for kind, text in _user_pieces(row) if kind == "clinician"
                 and not text.startswith(("Message Type:", "[Message from ")))


def _user_candidates(identifier: str, transcript_id: str, row: Mapping[str, Any]) -> list[Candidate]:
    return [Candidate(identifier if number == 1 else f"{identifier}#{number}",
                      transcript_id, _declared_entry_kind(kind), text, _human_aliases(kind, text))
            for number, (kind, text) in enumerate(_user_pieces(row), 1)]


def _human_aliases(kind: str, value: str) -> tuple[str, ...]:
    if kind == "task-notification":
        matched = TASK_ID.search(value)
        if matched:
            return (matched.group("id"),)
    return ()


def _human_candidate(
    uuid: str,
    transcript_id: str,
    value: str,
    *,
    default_kind: str,
    row: Mapping[str, Any] | None = None,
) -> Candidate:
    kind = _human_kind(row, value) if row is not None else (_envelope_kind(value) or default_kind)
    return Candidate(
        uuid,
        transcript_id,
        _declared_entry_kind(kind),
        value,
        _human_aliases(kind, value),
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
            candidates.extend(_user_candidates(uuid, transcript_id, row))
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
        elif row.get("type") == "system" and _text(row.get("subtype")) in READ_SYSTEM_SUBTYPES:
            body = _text(row.get("content")).strip()
            if body:
                candidates.append(
                    _human_candidate(uuid, transcript_id, body, default_kind="harness-meta")
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
                    if role == "user":
                        candidates.extend(_user_candidates(identifier, transcript_id, row))
                    else:
                        candidates.append(_human_candidate(identifier, transcript_id, body, default_kind="assistant"))
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


def memory_measurement_path(run: Path, submission: str, round_number: int = 1) -> Path:
    return run / "aar" / f"{_round_stem(submission, round_number)}.memory-index.json"


def measure_memory(run: Path, submission: str, round_number: int | None) -> Path:
    """Retain this round's index counts after its memory writes have landed."""
    with locked_record(run / "aar" / ".record-allocation"):
        if round_number is None:
            round_number = max(_review_round_numbers(run, submission), default=1)
        return _measure_memory(run, submission, round_number)


def _measure_memory(run: Path, submission: str, round_number: int) -> Path:
    extract = extract_path(run, submission, round_number)
    fields, _identifiers = _extract_metadata(extract)
    value = fields.get("MEMORY-INDEX", "")
    if not value.strip():
        raise ValueError("extract has no MEMORY-INDEX path")
    index = Path(value).expanduser()
    if not index.is_absolute():
        raise ValueError("extract MEMORY-INDEX must be absolute")
    # ADR 0391 ruling 9: subject list sizes are reported, an unplaced memory is graded.
    placement = memory_index.survey(index)
    lines, characters = placement.lines, placement.characters
    limits = dict(MEMORY_INDEX_LIMITS)
    record = {
        "submission": submission, "round": round_number,
        "extracted_at": fields.get("EXTRACTED-AT", ""),
        "memory_index": value, "measured_at": datetime.now(timezone.utc).isoformat(),
        "lines": lines, "characters": characters, "limits": limits,
        "verdict": "fail" if lines > limits["lines"] or characters > limits["characters"] else "pass",
        "subject_lists": dict(placement.subject_lists),
        "unplaced": len(placement.unplaced),
    }
    destination = memory_measurement_path(run, submission, round_number)
    update_tool_record(destination, _memory_measurement_record,
                       lambda previous: RecordUpdate((json.dumps(record, indent=2) + "\n").encode("utf-8")))
    return destination


def _memory_index_grade(
    run: Path, submission: str, round_number: int, fields: Mapping[str, str]
) -> tuple[tuple[str, ...], tuple[Finding, ...]]:
    prefix = f"memory index round {round_number}"
    extracted_at = fields.get("EXTRACTED-AT", "")
    required = bool(extracted_at) and _utc_timestamp(extracted_at, "EXTRACTED-AT") >= MEMORY_MEASUREMENT_CUTOFF
    path = memory_measurement_path(run, submission, round_number)
    try:
        record = read_tool_record(path, _memory_measurement_record)
        if record is None:
            if not required:
                return (f"{prefix}: {NOT_GRADED} - extract predates the measurement",), ()
            raise ValueError("measurement is absent")
        limits = record["limits"]
        overflow = record["lines"] > limits["lines"] or record["characters"] > limits["characters"]
        if (
            record["submission"] != submission or record["round"] != round_number
            or record["memory_index"] != fields.get("MEMORY-INDEX")
            or record["extracted_at"] != extracted_at
            or record["verdict"] != ("fail" if overflow else "pass")
        ):
            raise ValueError("measurement does not match the round or its verdict")
    except UnreadableRecord as exc:
        return (fault_report(exc, check=prefix),), ()
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        return (f"{prefix}: measurement missing or invalid",), (Finding("memory-index-measurement", str(exc)),)
    reports = [
        f"{prefix}: {record['lines']}/{limits['lines']} lines; "
        f"{record['characters']}/{limits['characters']} characters; "
        f"Claude Code {limits['release']}; {record['verdict']}"
    ]
    if "unplaced" in record:
        reports.append(
            f"{prefix}: {memory_index.subject_list_summary(record['subject_lists'])}"
            f"; unplaced memories {record['unplaced']}"
        )
    else:
        reports.append(f"{prefix}: unplaced memories {NOT_GRADED} - measured before ADR 0391")
    versions = tuple(value.strip() for value in fields.get("HARNESS-VERSIONS", "").split(","))
    mismatched = tuple(value for value in versions if re.fullmatch(r"\d+\.\d+\.\d+", value) and value != limits["release"])
    if mismatched:
        reports.append(f"Claude Code {', '.join(mismatched)} differs from measured release {limits['release']}; re-measure memory index limits.")
    findings = [Finding("memory-index-overflow", f"round {round_number}")] if overflow else []
    if record.get("unplaced"):
        findings.append(Finding("memory-index-unplaced", f"round {round_number}: {record['unplaced']}"))
    return tuple(reports), tuple(findings)


def _memory_measurement_record(text: str) -> dict:
    record = object_record(text)
    limits = record.get("limits")
    if not isinstance(limits, dict):
        raise RecordShapeError("record fields")
    for counts in (record, limits):
        if any(type(counts.get(name)) is not int or counts[name] < (1 if counts is limits else 0)
               for name in ("lines", "characters")):
            raise RecordShapeError("record fields")
    if (type(record.get("round")) is not int or record["round"] < 1
            or any(not isinstance(record.get(name), str) or not record[name]
                   for name in ("submission", "memory_index", "extracted_at", "measured_at"))
            or not isinstance(limits.get("release"), str)
            or not re.fullmatch(r"\d+\.\d+\.\d+", limits["release"])
            or record.get("verdict") not in {"pass", "fail"}):
        raise RecordShapeError("record fields")
    for name in ("extracted_at", "measured_at"):
        _utc_timestamp(record[name], name)
    # Both optional placement fields are absent on pre-ADR 0391 records.
    if "unplaced" in record or "subject_lists" in record:
        lists = record.get("subject_lists")
        if (type(record.get("unplaced")) is not int or record["unplaced"] < 0
                or not isinstance(lists, dict)
                or any(not isinstance(k, str) or type(v) is not int or v < 0 for k, v in lists.items())):
            raise RecordShapeError("record fields")
    return record


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


def _posted_reading_block(run: Path, submission: str, *, force: bool = False) -> str:
    from discussion_artifact import decode_posted_readings
    path = run / "reread.md"
    def decode(text):
        text = check_handwritten_text(text, path, "raw-text").require_text(force=force, artifact=submission)
        decode_posted_readings(text)
        return text.replace("\r\n", "\n")
    text = read_tool_record(path, decode)
    if text is None:
        raise ValueError(f"reread.md has no REREAD record for {submission}")
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


def _posted_reading_fingerprint(run: Path, submission: str, *, force: bool = False) -> str:
    return sha256(_posted_reading_block(run, submission, force=force).encode("utf-8")).hexdigest()


def legacy_orphan_paths(run: Path) -> tuple[Path, ...]:
    root = run / "aar"
    return tuple(sorted(root.glob("orphaned-*.json"))) if root.is_dir() else ()


def retire_orphan_pointers(run: Path) -> None:
    """Move legacy pointer files aside in place; their evidence is never deleted."""
    if not legacy_orphan_paths(run):
        return
    with locked_record(run / "aar" / ".record-allocation"):
        _retire_orphan_pointers(run)


def _retire_orphan_pointers(run: Path) -> None:
    for path in legacy_orphan_paths(run):
        with locked_record(path):
            destination = path.with_name(f"retired-{path.name}")
            suffix = 2
            while destination.exists():
                destination = path.with_name(f"retired-{suffix}-{path.name}")
                suffix += 1
            try:
                path.replace(destination)
            except OSError as failure:
                raise UnreadableRecord(path, "could not be opened") from failure


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
    return tuple(sorted(tree_walk.walk_files(index.parent).files))


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
        if path.name.endswith((".extract.md", ".reversal-candidates.md")):
            continue
        try:
            review = read_review(path, force=True)
        except ValueError:
            continue
        extract = path.with_name(f"{path.stem}.extract.md")
        extract_fields: dict[str, str] = {}
        try:
            extract_fields, _identifiers = _extract_metadata(extract)
        except UnreadableRecord:
            raise
        except ValueError:
            extract_fields = {}
        _append_review_cursors(cursors, review, extract_fields)
    return cursors


def _append_review_cursors(
    cursors: dict[str, list[tuple[str, str | None]]],
    review: Review,
    extract_fields: Mapping[str, str],
) -> None:
    watermarks = _transcript_watermarks(
        extract_fields.get("TRANSCRIPT-WATERMARKS", "")
    )
    if watermarks:
        for transcript_id, watermark in watermarks.items():
            classifier = (
                review.fields.get("CLASSIFIER-ENTRY", "")
                if watermark == review.fields.get("WATERMARK")
                else None
            )
            cursors.setdefault(transcript_id, []).append((watermark, classifier))
        return
    transcripts = [
        value.strip()
        for value in review.fields.get("TRANSCRIPTS", "").split(",")
        if value.strip()
    ]
    watermark = review.fields.get("WATERMARK", "")
    if transcripts and watermark:
        cursors.setdefault(transcripts[-1], []).append(
            (watermark, review.fields.get("CLASSIFIER-ENTRY", ""))
        )


def _furthest_cursor(
    rows: Iterable[Candidate], cursors: Iterable[tuple[str, str | None]]
) -> tuple[str, str | None] | None:
    population = tuple(rows)
    available = tuple(cursors)
    if not available:
        return None
    return max(
        available,
        key=lambda cursor: _cursor_index(population, cursor[0]),
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
    index = _cursor_index(candidates, watermark)
    if index < 0:
        raise ValueError("prior watermark is not in its transcript population")
    return candidates[index + 1 :]


def _cursor_index(candidates: Iterable[Candidate], cursor: str) -> int:
    population = tuple(candidates)
    for index, candidate in enumerate(population):
        if candidate.kind == "task-notification" and cursor in candidate.aliases:
            return index
    for index, candidate in enumerate(population):
        if candidate.identifier == cursor:
            return index
    for index, candidate in enumerate(population):
        if cursor in candidate.aliases:
            return index
    return -1


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
    undeclared_rows = sum(
        1
        for row in rows
        if _text(row.get("type"))
        not in CODEX_ROW_TYPES | CLAUDE_ROW_TYPES | NAMED_UNREAD_TYPES.keys()
    )
    undeclared_payloads = sum(
        1
        for row in rows
        if row.get("type") == "response_item"
        and _text(_codex_payload(row).get("type")) not in CODEX_RESPONSE_TYPES | NAMED_UNREAD_TYPES.keys()
    )
    undeclared_system_subtypes = sum(
        1 for row in rows
        if row.get("type") == "system"
        and _text(row.get("subtype")) not in READ_SYSTEM_SUBTYPES | NAMED_UNREAD_SYSTEM_SUBTYPES.keys()
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
        undeclared_row_types=undeclared_rows,
        undeclared_codex_payload_types=undeclared_payloads,
        undeclared_system_subtypes=undeclared_system_subtypes,
        subagent_launches=len(launches),
        joined_results=joined,
        unjoined_launches=len(launches) - joined,
        notifications_without_join_key=sum(
            1 for candidate in notifications if not _notification_keys(candidate.text)
        ),
        browser=browser,
        agents_instructions=sum(
            1 for row in rows if row.get("type") == "response_item"
            and _codex_payload(row).get("role") == "user"
            for block in _content_blocks(_codex_payload(row))
            if block.get("type") == "input_text"
            and _agents_instructions(_text(block.get("text")))
        ),
    )


def _departure_population(run: Path) -> list[Candidate]:
    """Carry the only scoped departure-list surface, including its ruling. #1217."""
    population: list[Candidate] = []
    for source in sorted(run.glob("proposed-*.md")):
        if not source.is_file() or not re.fullmatch(
            r"proposed-\d{4}-\d{2}-\d{2}\.md", source.name
        ):
            continue
        text = source.read_bytes().decode("utf-8")
        section = re.search(
            r"(?m)^## Departures[ \t]*\r?$(?:\n|\Z)", text
        )
        if section is None:
            continue
        following = re.search(r"(?m)^#{1,2} ", text[section.end():])
        end = section.end() + following.start() if following else len(text)
        population.append(
            Candidate(
                f"departure:{source.name}",
                f"departure:{source.name}",
                "departure-list",
                text[section.start():end],
            )
        )
    return population


def reversal_candidates_path(run: Path, submission: str, round_number: int) -> Path:
    return run / "aar" / f"{_round_stem(submission, round_number)}.reversal-candidates.md"


def _reversal_population(run: Path, submission: str, round_number: int, *,
                         artifact: str | None = None, force: bool = False) -> list[Candidate]:
    path = reversal_candidates_path(run, submission, round_number)
    try:
        text = read_handwritten_record(path).require_text(artifact=artifact, force=force)
    except (OSError, UnicodeError) as failure:
        raise ValueError("the round needs a readable reversal-candidates file; write none when empty") from failure
    lines = tuple(line.strip() for line in text.splitlines() if line.strip())
    if not lines or ("none" in {line.casefold() for line in lines} and lines != ("none",)):
        raise ValueError("reversal candidates need one reversal per line or exactly none")
    return [Candidate(f"reversals:{_round_stem(submission, round_number)}", "reversals",
                      "reversal-candidates", text)]


def _check_snapshot_posted_reading(run: Path, submission: str) -> None:
    """Resolve the approved skill; its grader owns every posted-reading rule."""
    import approval_record
    import assignment_submission
    import frozen_grade
    if frozen_grade.report(run, submission) is not None:
        return

    items = approval_record._read(run, missing_ok=True).get("items", [])
    matching = [
        item for item in items
        if isinstance(item, dict) and item.get("submission") == submission
    ]
    if len(matching) > 1:
        raise ValueError("submission has ambiguous skill approval records")
    if matching:
        skill = matching[0].get("skill")
        args = matching[0].get("grader_args")
    else:
        from run_record_reader import submission_record
        gate = read_tool_record(run / assignment_submission.RECORD, submission_record)
        if gate is None:
            raise ValueError("cannot determine the submission's skill from its approval record")
        skill = "course-assignment"
        artifact = gate.get("artifact_path")
        args = [str(run), "--artifact", artifact] if isinstance(artifact, str) and artifact else None
    if not isinstance(skill, str) or skill not in COMPLETION_GRADERS:
        raise ValueError("approval record has no supported skill")
    if not isinstance(args, list) or not args or not all(isinstance(arg, str) for arg in args):
        raise ValueError("approval record has no readable completion grader arguments")
    try:
        grader = importlib.import_module(COMPLETION_GRADERS[skill])
    except ImportError as failure:
        raise ValueError(f"{skill} posted-reading checker could not be loaded") from failure
    check = getattr(grader, "posted_reading_check", None)
    if not callable(check):
        raise ValueError(f"{skill} has no posted-reading-only entry point")
    try:
        outcomes = check(run, submission, tuple(args))
    except run_grader.SourceError as failure:
        raise ValueError(str(failure)) from failure
    if outcomes:
        raise ValueError("; ".join(outcome.message for outcome in outcomes))


def write_extract(
    run: Path,
    transcript: Path | None,
    submission: str,
    memory_index: Path,
) -> tuple[Path, int]:
    with locked_record(run / "aar" / ".record-allocation"):
        return _write_extract(run, transcript, submission, memory_index)


def _write_extract(run: Path, transcript: Path | None, submission: str,
                   memory_index: Path) -> tuple[Path, int]:
    _retire_orphan_pointers(run)
    _check_snapshot_posted_reading(run, submission)
    posted_reading_fingerprint = _posted_reading_fingerprint(run, submission, force=True)
    round_number = _next_review_round(run, submission)
    reversals = (_reversal_population(run, submission, round_number, force=True)
                 if datetime.now(timezone.utc) >= REVERSAL_CANDIDATES_CUTOFF else [])
    population, transcripts, discovery = _collect_population(run, transcript)
    if not population:
        raise ValueError("candidate population is empty")
    population = _departure_population(run) + reversals + population
    destination = extract_path(run, submission, round_number)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as failure:
        raise UnreadableRecord(destination, "could not be opened") from failure
    diagnostics = extract_diagnostics(transcripts, population)
    memory_walk = tree_walk.walk_files(memory_index.parent)
    baseline = {
        str(path.resolve()): _hash(path)
        for path in (*_tracked_files(), *memory_walk.files)
    }
    unreadable_directories = discovery.unreadable_directories + memory_walk.unreadable_directories
    links_not_entered = discovery.links_not_entered + memory_walk.links_not_entered
    transcript_watermarks: dict[str, str] = {}
    for candidate in population:
        if candidate.kind not in {"departure-list", "reversal-candidates"}:
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
        f"TRANSCRIPTS-UNREAD: {discovery.unread}",
        f"UNREADABLE-DIRECTORIES: {unreadable_directories}",
        f"LINKS-NOT-ENTERED: {links_not_entered}",
        f"POPULATION: {len(population)}",
        f"WATERMARK: {population[-1].identifier}",
        f"MEMORY-INDEX: {memory_index.resolve()}",
        "HARNESS-VERSIONS: " + (", ".join(diagnostics.harness_versions) or "none observed"),
        f"UNDECLARED-ENVELOPES: {diagnostics.undeclared_envelopes}",
        f"AGENTS-INSTRUCTIONS: {diagnostics.agents_instructions}",
        f"UNREAD-REMAINDER: {diagnostics.unread_remainder + discovery.unread + unreadable_directories}",
        f"UNDECLARED-ROW-TYPES: {diagnostics.undeclared_row_types}",
        f"UNDECLARED-CODEX-PAYLOAD-TYPES: {diagnostics.undeclared_codex_payload_types}",
        f"UNDECLARED-SYSTEM-SUBTYPES: {diagnostics.undeclared_system_subtypes}",
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
        lines.extend(_extract_entry_lines(row))
    extract_text = "\n".join(lines)
    _extract_document_text(extract_text)
    update_tool_record(destination, _tool_extract_entries,
                       lambda previous: RecordUpdate(extract_text.encode("utf-8")))
    update_tool_record(baseline_path(run, submission, round_number), _baseline_record,
                       lambda previous: RecordUpdate((json.dumps(baseline, sort_keys=True) + "\n").encode("utf-8")))
    return destination, len(population)


def _review_cursors_before_round(
    run: Path, submission: str, round_number: int
) -> dict[str, list[tuple[str, str | None]]]:
    cursors: dict[str, list[tuple[str, str | None]]] = {}
    for earlier in range(1, round_number):
        review_file = review_path(run, submission, earlier)
        extract_file = extract_path(run, submission, earlier)
        if not review_file.is_file():
            raise ValueError(f"earlier review round {earlier} is incomplete")
        review = read_review(review_file, force=True)
        fields, _identifiers = _extract_metadata(extract_file)
        _append_review_cursors(cursors, review, fields)
    return cursors


def _rebuild_population(
    run: Path,
    submission: str,
    round_number: int,
    fields: Mapping[str, str],
    refused_entries: tuple[ExtractEntry, ...],
) -> list[Candidate]:
    transcript_paths = [
        Path(value.strip()).expanduser().resolve()
        for value in fields.get("TRANSCRIPT-PATHS", "").split("|")
        if value.strip()
    ]
    if not transcript_paths:
        raise ValueError("refused extract has no transcript paths")
    recorded_entry_counts: dict[str, int] = {}
    for entry in refused_entries:
        if entry.kind in {"departure-list", "reversal-candidates"}:
            continue
        recorded_entry_counts[entry.transcript_id] = (
            recorded_entry_counts.get(entry.transcript_id, 0) + 1
        )
    if set(recorded_entry_counts) != {path.stem for path in transcript_paths}:
        raise ValueError("refused extract transcript paths do not match its entries")
    cursors = _review_cursors_before_round(run, submission, round_number)
    rebuilt = _departure_population(run)
    # A refused round retains its candidate input exactly; an edited or absent
    # file refuses the rebuild rather than silently replacing the reader's set.
    if any(entry.kind == "reversal-candidates" for entry in refused_entries):
        rebuilt += _reversal_population(run, submission, round_number, force=True)
    for transcript_path in transcript_paths:
        rows = reduce_transcript(transcript_path)
        selected = _furthest_cursor(rows, cursors.get(transcript_path.stem, ()))
        watermark, prior_review = selected or ("", None)
        current = _after_watermark(rows, watermark or None)
        if prior_review:
            current = [
                replace(candidate, kind="prior-review")
                if candidate.identifier == prior_review
                or prior_review in candidate.aliases
                else candidate
                for candidate in current
            ]
        recorded_entry_count = recorded_entry_counts[transcript_path.stem]
        if len(current) < recorded_entry_count:
            raise ValueError(
                f"transcript {transcript_path.stem} has fewer entries than the refused extract"
            )
        rebuilt.extend(current[:recorded_entry_count])
    return rebuilt


def _render_rebuilt_extract(header: str, population: Iterable[Candidate]) -> str:
    lines = [header, ""]
    for candidate in population:
        lines.extend(_extract_entry_lines(candidate))
    return "\n".join(lines)


def _extract_entry_lines(candidate: Candidate) -> list[str]:
    text_lines = (
        candidate.text.split("\n")
        if candidate.kind in {"departure-list", "reversal-candidates"}
        else candidate.text.splitlines() or [""]
    )
    return [
        f"## ENTRY: {candidate.identifier}",
        f"TRANSCRIPT: {candidate.transcript_id}",
        f"KIND: {candidate.kind}",
        f"TEXT-LINES: {len(text_lines)}",
        "TEXT:",
        *text_lines,
        "",
    ]


def _rendered_candidate_text(candidate: Candidate) -> str:
    if candidate.kind in {"departure-list", "reversal-candidates"}:
        return candidate.text.replace("\r\n", "\n")
    return "\n".join(candidate.text.splitlines() or [""])


def rebuild_extract(
    run: Path, submission: str, round_number: int
) -> tuple[Path, int, Path]:
    with locked_record(run / "aar" / ".record-allocation"):
        return _rebuild_extract(run, submission, round_number)


def _rebuild_extract(run: Path, submission: str, round_number: int) -> tuple[Path, int, Path]:
    destination = extract_path(run, submission, round_number)
    def refused_record(text: str) -> str:
        _tool_extract_entries(text, allow_duplicate_identifiers=True)
        return text
    def change(refused_text):
        return _rebuilt_update(run, submission, round_number, destination, refused_text)
    return update_tool_record(destination, refused_record, change)


def _rebuilt_update(run: Path, submission: str, round_number: int,
                    destination: Path, refused_text: str | None) -> RecordUpdate:
    if refused_text is None:
        raise ValueError(f"cannot read refused round {round_number}")
    fields, refused_entries = _extract_entries_text(
        refused_text, allow_duplicate_identifiers=True
    )
    if fields.get("FORMAT", "1") != "2":
        raise ValueError("only format 2 extracts can be rebuilt")
    population = _rebuild_population(
        run, submission, round_number, fields, refused_entries
    )
    if len(population) != len(refused_entries):
        raise ValueError("rebuilt extract population does not match the refused extract")
    for refused, rebuilt in zip(refused_entries, population):
        if (
            refused.transcript_id != rebuilt.transcript_id
            or refused.kind != rebuilt.kind
            or refused.text != _rendered_candidate_text(rebuilt)
        ):
            raise ValueError("rebuilt extract entries do not match the refused extract")
        if (
            refused.kind != "task-notification"
            and refused.identifier != rebuilt.identifier
        ):
            raise ValueError(
                "rebuilt extract changed a non-notification entry identifier"
            )
    header = "\n".join(refused_text.splitlines()).split("\n\n", 1)[0]
    rebuilt_text = _render_rebuilt_extract(header, population)
    _extract_document_text(rebuilt_text)
    refused_root = run / "aar" / "refused"
    archived = refused_root / destination.name
    created_archive = False
    try:
        refused_root.mkdir(parents=True, exist_ok=True)
        suffix = 2
        while archived.exists():
            archived = refused_root / f"{destination.stem}.{suffix}{destination.suffix}"
            suffix += 1
        with archived.open("xb") as stream:
            created_archive = True
            stream.write(refused_text.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException as failure:
        if created_archive:
            try:
                archived.unlink(missing_ok=True)
            except OSError:
                pass
        if isinstance(failure, OSError):
            raise UnreadableRecord(destination, "could not be opened") from failure
        raise
    return RecordUpdate(rebuilt_text.encode("utf-8"), (destination, len(population), archived),
                        rollback=lambda: archived.unlink(missing_ok=True))


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


def read_review(path: Path, *, force: bool = False, artifact: str | None = None) -> Review:
    try:
        lines = read_handwritten_record(path, HandwrittenKind("aar-review", decode_errors="replace")).require_text(force=force, artifact=artifact).splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read review {path.name}") from exc
    header: list[str] = []
    corrections: list[Correction] = []
    sustains: list[Sustain] = []
    candidate_answers: list[tuple[str, str]] = []
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
        elif mode == "candidate" and current_event is not None:
            candidate_answers.append((current_event, _parse_fields(current_lines).get("ANSWER", "")))
        current_event, current_lines = None, []

    for line in lines:
        correction = CORRECTION_HEADING.match(line)
        sustain = SUSTAIN_HEADING.match(line)
        candidate = re.fullmatch(r"## CANDIDATE: ([0-9]+)[ \t]*", line)
        if correction:
            close()
            mode, current_event = "correction", correction.group("event")
        elif sustain:
            close()
            mode, current_event = "sustain", sustain.group("event")
        elif candidate:
            close()
            mode, current_event = "candidate", candidate.group(1)
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
        candidate_answers=tuple(candidate_answers),
    )


def _extract_document(
    path: Path,
) -> tuple[dict[str, str], set[str], dict[str, str], set[str], tuple[ExtractEntry, ...]]:
    def decode(text: str):
        _fields, entries = _tool_extract_entries(text)
        return (*_extract_document_text(text), entries)
    document = read_tool_record(path, decode)
    if document is None:
        raise ValueError(f"cannot read extract {path.name}")
    return document


def _tool_extract_entries(text: str, *, allow_duplicate_identifiers: bool = False):
    fields, entries = _extract_entries_text(text, allow_duplicate_identifiers=allow_duplicate_identifiers)
    # Historical extracts lack later diagnostic fields. Present counters must
    # have their declared shape; absence retains the dated grading semantics.
    counters = {"POPULATION", "UNREAD-REMAINDER", "UNMARKED-PRIOR-REVIEWS", "AGENTS-INSTRUCTIONS"}
    counters.update(name for name in fields if name.startswith(("TRANSCRIPTS-", "UNDECLARED-", "TAB-CREATION-")))
    counters.difference_update({"TRANSCRIPT-PATHS"})
    counters.update({"UNREADABLE-DIRECTORIES", "LINKS-NOT-ENTERED", "UNOWNED-BROWSER-PAGE-ACTIONS"})
    if any(name in fields and not re.fullmatch(r"[0-9]+", fields[name]) for name in counters):
        raise RecordShapeError("record header fields")
    if any(not fields.get(name) for name in ("SUBMISSION", "POPULATION", "TRANSCRIPTS", "WATERMARK")):
        raise RecordShapeError("record header fields")
    return fields, entries


def _extract_document_text(
    text: str,
) -> tuple[dict[str, str], set[str], dict[str, str], set[str]]:
    fields, entries = _extract_entries_text(text)
    identifiers = {entry.identifier for entry in entries}
    task_aliases = {
        matched.group("id")
        for entry in entries
        if entry.kind == "task-notification"
        for matched in [TASK_ID.search(entry.text)]
        if matched is not None
    }
    return (
        fields,
        identifiers,
        {entry.identifier: entry.kind for entry in entries},
        task_aliases,
    )


def _extract_entries_text(
    text: str, *, allow_duplicate_identifiers: bool = False
) -> tuple[dict[str, str], tuple[ExtractEntry, ...]]:
    lines = text.splitlines()
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
        entries = tuple(
            ExtractEntry(line.partition(":")[2].strip(), "", "", "")
            for line in lines[header_end + 1 :]
            if line.startswith("## ENTRY:")
        )
        return fields, entries
    if format_version != "2":
        raise UnknownExtractFormat(f"unknown extract format {format_version}")
    if not fields.get("EXTRACTED-AT"):
        raise ValueError("format 2 extract has no EXTRACTED-AT field")
    identifiers: set[str] = set()
    entries: list[ExtractEntry] = []
    index = header_end + 1
    while index < len(lines):
        if not lines[index]:
            index += 1
            continue
        if not lines[index].startswith("## ENTRY:"):
            raise ValueError(f"extract entry expected at line {index + 1}")
        identifier = lines[index].partition(":")[2].strip()
        if not identifier or (
            not allow_duplicate_identifiers and identifier in identifiers
        ):
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
        body = "\n".join(lines[index + 2 : index + text_lines + 2])
        entries.append(
            ExtractEntry(
                identifier,
                parsed_entry_fields["TRANSCRIPT"],
                entry_kind,
                body,
            )
        )
        index += text_lines + 2
    return fields, tuple(entries)


def _extract_metadata(path: Path) -> tuple[dict[str, str], set[str]]:
    fields, identifiers, _entry_kinds, _task_aliases, _entries = _extract_document(path)
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


def _baseline_record(text: str) -> dict[str, str | None]:
    payload = object_record(text)
    if any(not key or (value is not None and (not isinstance(value, str)
               or not re.fullmatch(r"[0-9a-f]{64}", value))) for key, value in payload.items()):
        raise RecordShapeError("record item fields")
    return payload


def _baseline(
    run: Path, submission: str, round_number: int = 1
) -> dict[str, str | None]:
    payload = read_tool_record(baseline_path(run, submission, round_number), _baseline_record)
    if payload is None:
        raise ValueError("baseline is absent or unreadable")
    return payload


def _target_changed(target: str, baseline: Mapping[str, str | None]) -> bool:
    path = Path(target).expanduser().resolve()
    return _hash(path) is not None and _hash(path) != baseline.get(str(path))


@dataclass(frozen=True)
class GhCommand:
    command: str
    cwd: str | None
    output: str
    timestamp: datetime | None
    shared_output: bool = False


def _successful_gh_commands(transcripts: Iterable[Path]) -> tuple[GhCommand, ...]:
    """Retain successful command evidence; never replay a recorded command."""
    results = []
    for transcript in transcripts:
        rows = read_transcript(transcript)
        calls = {}
        for row in rows:
            if row.get("type") != "assistant":
                continue
            for block in _content_blocks(row.get("message")):
                source = block.get("input")
                command = source.get("command") if isinstance(source, dict) else None
                if block.get("type") == "tool_use" and isinstance(command, str) and shell_reader.has_executable(command, "gh"):
                    calls[_text(block.get("id"))] = (command, _text(row.get("cwd")) or None)
        for row in rows:
            try:
                timestamp = _utc_timestamp(_text(row.get("timestamp")), "command timestamp")
            except ValueError:
                timestamp = None
            if row.get("type") == "event_msg":
                payload = row.get("payload")
                item = payload.get("item") if isinstance(payload, dict) and payload.get("type") == "item_completed" else None
                if not isinstance(item, dict) or item.get("type") != "CommandExecution":
                    continue
                if item.get("status") != "completed" or item.get("exit_code") != 0:
                    continue
                commands = item.get("command")
                commands = commands if isinstance(commands, list) else [commands]
                for command in commands:
                    if isinstance(command, str) and shell_reader.has_executable(command, "gh"):
                        results.append(GhCommand(
                            command, _text(item.get("cwd") or item.get("workdir") or row.get("cwd")) or None,
                            "\n".join(_text(item.get(field)) for field in ("stdout", "aggregated_output")),
                            timestamp,
                            len(commands) != 1,
                        ))
            elif row.get("type") == "user":
                for block in _content_blocks(row.get("message")):
                    if block.get("type") != "tool_result" or block.get("tool_use_id") not in calls or block.get("is_error") is True:
                        continue
                    command, cwd = calls[block["tool_use_id"]]
                    content = block.get("content")
                    output = content if isinstance(content, str) else "\n".join(
                        _text(part.get("text")) for part in (content or [])
                        if isinstance(part, dict) and part.get("type") == "text"
                    )
                    results.append(GhCommand(command, cwd, output, timestamp))
    return tuple(results)


def _printed_landing(call: GhCommand, landing: str, extracted_at: datetime) -> bool:
    return (call.timestamp is not None and call.timestamp >= extracted_at
            and landing in re.findall(r"https://[^\s<>\"']+", call.output))


def _successful_gh_call(
    transcripts: Iterable[Path], landing: str | None = None,
    extracted_at: datetime | None = None,
    *, require_search: bool = False,
) -> bool:
    search_times = _successful_issue_search_times(transcripts) if require_search else ()
    return any(
        landing is None or (
            extracted_at is not None and _printed_landing(call, landing, extracted_at)
            and (not require_search or any(search < call.timestamp for search in search_times))
        )
        for call in _successful_gh_commands(transcripts)
    )


def _review_content(review: Review) -> tuple[int, int, list[Finding]]:
    """Checks whose evidence is entirely in the handwritten review."""
    findings: list[Finding] = []
    try:
        population = int(review.fields.get("POPULATION", ""))
        unread = int(review.fields.get("UNREAD", ""))
    except ValueError:
        population, unread = 0, -1
        findings.append(Finding("non-numeric-coverage", "POPULATION or UNREAD"))
    if unread != 0:
        findings.append(Finding("unread-candidates", str(unread)))
    if not review.corrections and not review.corrections_none:
        findings.append(Finding("missing-correction-verdict", "neither records nor CORRECTIONS: none"))
    if review.corrections and review.corrections_none:
        findings.append(Finding("contradictory-correction-verdict", "records and CORRECTIONS: none"))
    if not review.sustains and not review.sustains_none:
        findings.append(Finding("missing-sustain-verdict", "neither records nor SUSTAINS: none"))
    if review.sustains and review.sustains_none:
        findings.append(Finding("contradictory-sustain-verdict", "records and SUSTAINS: none"))
    for correction in review.corrections:
        for field in CORRECTION_FIELDS:
            if not _substance(correction.fields.get(field, "")):
                findings.append(Finding("missing-correction-field", f"{correction.event}: {field}"))
        if correction.fields.get("CORRECTOR") not in CORRECTORS:
            findings.append(Finding("unknown-corrector", correction.fields.get("CORRECTOR", "")))
        if correction.fields.get("IN-ERROR") not in CORRECTORS:
            findings.append(Finding("unknown-error-party", correction.fields.get("IN-ERROR", "")))
        if correction.fields.get("DISPOSITION", "") not in DISPOSITIONS:
            findings.append(Finding("unknown-disposition", correction.fields.get("DISPOSITION") or correction.event))
    for sustain in review.sustains:
        if not _substance(sustain.fields.get("SUMMARY", "")):
            findings.append(Finding("bare-sustain", sustain.event))
    return population, unread, findings


def _successful_issue_search_times(transcripts: Iterable[Path]) -> tuple[datetime, ...]:
    """Recognize successful direct issue searches in the same raw evidence as landings."""
    def searches(command):
        for tokens, index in shell_reader.executable_calls(command, "gh"):
            args = tokens[index + 1:]
            if args[:2] == ["issue", "list"]:
                searched = any(arg == "--search" or arg.startswith("--search=") for arg in args[2:])
                if searched and ("--state=all" in args or any(args[i:i + 2] == ["--state", "all"] for i in range(len(args)))):
                    return True
            if args[:2] == ["search", "issues"] and not any(arg.startswith("--state") for arg in args[2:]):
                return True
            if args[:1] == ["api"] and any(re.search(r"(?:^|/)search/issues(?:\?|$)", arg) for arg in args[1:]):
                return True
        return False
    return tuple(call.timestamp for call in _successful_gh_commands(transcripts)
                 if call.timestamp is not None and searches(call.command))


def _grade_reversal_candidates(run: Path, submission: str, round_number: int,
                               review: Review, entries: tuple[ExtractEntry, ...]):
    findings = []
    candidates = [entry for entry in entries if entry.kind == "reversal-candidates"]
    try:
        supplied = _reversal_population(run, submission, round_number, artifact=submission)[0]
        if len(candidates) != 1 or candidates[0].text != _rendered_candidate_text(supplied):
            raise ValueError("candidate file no longer matches this round's extract")
        lines = tuple(line.strip() for line in supplied.text.splitlines() if line.strip())
        population = 0 if lines == ("none",) else len(lines)
    except DamagedRecord as failure:
        finding, report = damaged_record_result(failure, check="reversal candidates", artifact=submission)
        return ((Finding("reversal-candidates", report),) if finding else ()), report
    except ValueError as failure:
        return (Finding("reversal-candidates", str(failure)),), f"reversal candidates: {NOT_GRADED} - missing or changed input"
    expected = {str(number) for number in range(1, population + 1)}
    keys = [key for key, _ in review.candidate_answers]
    if set(keys) != expected or len(keys) != len(expected):
        findings.append(Finding("reversal-candidates", "each candidate needs exactly one numbered answer"))
    corrections = {correction.event for correction in review.corrections}
    rejected = not_shown = 0
    for key, answer in review.candidate_answers:
        if answer in corrections:
            continue
        if answer.startswith("not a correction - ") and _substance(answer[len("not a correction - "):]):
            rejected += 1
        elif answer.startswith("not shown - ") and _substance(answer[len("not shown - "):]):
            not_shown += 1
        else:
            findings.append(Finding("reversal-candidates", f"candidate {key} needs a correction entry or reasoned not-a-correction/not-shown answer"))
    return tuple(findings), f"reversal candidates: {population}; answered {len(keys)}; not a correction {rejected}; not shown {not_shown}"


def _cause_fields(correction: Correction, entry_kinds: Mapping[str, str]):
    """Read classifier and final pointers without deciding what their evidence proves."""
    causes = []
    for name in ("CLASSIFIER-CAUSE", "CAUSE"):
        match = re.fullmatch(r"(shown|unverified) - (\S+)", correction.fields.get(name, ""))
        if (match is None or match[2] not in entry_kinds
                or entry_kinds[match[2]] in EXTRACTOR_WRITTEN_ENTRY_KINDS):
            return None
        causes.append((match[1], match[2]))
    return tuple(causes)


def _grade_causes(review: Review, entry_kinds: Mapping[str, str], active: bool):
    findings = []
    unverified = 0
    for correction in review.corrections:
        unverified += int(bool(re.fullmatch(r"unverified - \S+", correction.fields.get("CAUSE", ""))))
        causes = _cause_fields(correction, entry_kinds)
        if causes is None:
            if active:
                findings.append(Finding("cause-line", correction.event))
            continue
        classifier, final = causes
        if not active:
            continue
        if classifier != final and (
            classifier[0] != "shown" or final[0] != "unverified"
            or not _substance(correction.fields.get("CAUSE-OVERRULE", ""))
        ):
            findings.append(Finding("cause-overrule", correction.event))
        if final[0] == "unverified" and correction.fields.get("DISPOSITION") not in {"tracker-ticket", "skill-file"}:
            findings.append(Finding("unverified-disposition", correction.event))
    return tuple(findings), unverified


def _publication_labels(command: str) -> set[str]:
    labels = set()
    parsed = command_reader.gh_command_tokens(command, (("issue", "create"),))
    if parsed is None:
        return labels
    tokens, start = parsed
    arguments = tokens[start + 3:]
    for index, argument in enumerate(arguments):
        if argument in {"--label", "-l"} and index + 1 < len(arguments):
            labels.update(arguments[index + 1].split(","))
        elif argument.startswith(("--label=", "-l=")):
            labels.update(argument.split("=", 1)[1].split(","))
    return labels


def _warning_after_origin(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    origins = [index for index, line in enumerate(lines)
               if re.match(r"^(?:\*\*)?Filed from:(?:\*\*)?\s", line)]
    return (len(origins) == 1 and origins[0] + 1 < len(lines)
            and lines[origins[0] + 1] == UNVERIFIED_CAUSE_WARNING)


def _unverified_publication(transcripts: Iterable[Path], landing: str,
                            extracted_at: datetime | None) -> bool:
    if extracted_at is None:
        return False
    for call in _successful_gh_commands(transcripts):
        if call.shared_output or not _printed_landing(call, landing, extracted_at):
            continue
        # Shared output cannot identify which executable printed the address.
        # Recognize only one gh command, optionally preceded by literal cd &&.
        pieces = [piece.strip() for piece in shell_reader.shell_pieces(call.command) if piece.strip()]
        if (not pieces or len(pieces) % 2 != 1
                or any((shell_reader.LITERAL_CD.fullmatch(piece) is None if index % 2 == 0
                        else piece != "&&") for index, piece in enumerate(pieces[:-1]))
                or len(tuple(shell_reader.executable_calls(pieces[-1], "gh"))) != 1):
            continue
        command = call.command
        if call.cwd and Path(call.cwd).is_absolute():
            command = f"cd {shlex.quote(call.cwd)} && {command}"
        try:
            published = command_reader.extract(command)
        except (OSError, UnicodeError, ValueError):
            continue
        if published.route not in {("issue", "create"), ("issue", "comment")} or published.unreadable:
            continue
        bodies = [field for field in published.publications if field.field == "body"]
        if len(bodies) != 1 or bodies[0].origin != "body-file" or not _warning_after_origin(bodies[0].text):
            continue
        if published.route == ("issue", "create"):
            labels = _publication_labels(command)
            if "grilling" not in labels or "ready-for-agent" in labels:
                continue
        return True
    return False


def _survey_round(
    run: Path, submission: str, round_number: int, *, newest_round: bool = True
) -> Scan:
    findings: list[Finding] = []
    record_path = review_path(run, submission, round_number)
    records = int(record_path.is_file())
    if not records:
        return Scan(submission, 0, 0, 0, 0, 0, (Finding("missing-review", str(record_path)),))
    try:
        review = read_review(record_path, artifact=submission)
    except DamagedRecord as failure:
        finding, report = damaged_record_result(failure, check="the after-action review", artifact=submission)
        findings = [Finding("unscannable-review", report)] if finding else []
        reports = [report]
        # The damaged review cannot establish a population. Only the strict
        # retained extract may establish that this round owes the sibling input.
        try:
            fields, _ids, _kinds, _aliases, _entries = _extract_document(
                extract_path(run, submission, round_number)
            )
            if _utc_timestamp(fields["EXTRACTED-AT"], "EXTRACTED-AT") >= REVERSAL_CANDIDATES_CUTOFF:
                _reversal_population(run, submission, round_number, artifact=submission)
        except DamagedRecord as sibling:
            sibling_finding, sibling_report = damaged_record_result(
                sibling, check="reversal candidates", artifact=submission
            )
            reports.append(sibling_report)
            if sibling_finding:
                findings.append(Finding("reversal-candidates", sibling_report))
        except UnreadableRecord as sibling:
            reports.append(fault_report(sibling, check="extract-dependent checks"))
        except (KeyError, ValueError):
            # No trustworthy candidate joins can be graded without the review.
            pass
        return Scan(submission, 1, 0, 0, 0, 0,
                    tuple(findings), memory_reports=tuple(reports))
    except ValueError as exc:
        return Scan(submission, 1, 0, 0, 0, 0, (Finding("unscannable-review", str(exc)),))
    record_reports: list[str] = []
    try:
        baseline = _baseline(run, submission, round_number)
    except UnreadableRecord as exc:
        baseline = None
        record_reports.append(fault_report(exc, check="memory and check landings"))
    except ValueError as exc:
        return Scan(submission, 1, 0, 0, 0, 0, (Finding("unscannable-review", str(exc)),))
    for field in HEADER_FIELDS:
        value = review.fields.get(field, "")
        present = bool(value.strip()) if field in {"POPULATION", "UNREAD"} else _substance(value)
        if not present:
            findings.append(Finding("missing-header-field", field))
    if review.fields.get("SUBMISSION") != submission:
        findings.append(Finding("wrong-submission", review.fields.get("SUBMISSION", "")))
    population, unread, review_findings = _review_content(review)
    findings.extend(review_findings)
    try:
        extract_fields, identifiers, entry_kinds, task_aliases, entries = _extract_document(
            extract_path(run, submission, round_number)
        )
    except UnreadableRecord as exc:
        return Scan(submission, 1, population, len(review.corrections), len(review.sustains), unread,
                    tuple(findings), memory_reports=(*record_reports, fault_report(exc, check="extract-dependent checks")))
    except ValueError as exc:
        return Scan(submission, 1, 0, 0, 0, 0, (Finding("unscannable-extract", str(exc)),))

    extracted_at = extract_fields.get("EXTRACTED-AT", "")
    cause_check = not extracted_at or _utc_timestamp(extracted_at, "EXTRACTED-AT") >= UNVERIFIED_CAUSE_CUTOFF
    cause_findings, unverified = _grade_causes(review, entry_kinds, cause_check)
    findings.extend(cause_findings)
    reversal_check = bool(extracted_at) and _utc_timestamp(extracted_at, "EXTRACTED-AT") >= REVERSAL_CANDIDATES_CUTOFF
    if reversal_check:
        reversal_findings, reversal_report = _grade_reversal_candidates(run, submission, round_number, review, entries)
        findings.extend(reversal_findings)
    else:
        reversal_report = f"reversal candidates and landing search: {NOT_GRADED} - extract predates check"
    memory_reports, memory_findings = _memory_index_grade(run, submission, round_number, extract_fields)
    findings.extend(memory_findings)
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
    unread_remainder = None
    remainder_cutoff = bool(extracted_at) and (
        _utc_timestamp(extracted_at, "EXTRACTED-AT") >= UNREAD_REMAINDER_CUTOFF
    )
    if remainder_cutoff:
        try:
            count = int(extract_fields["UNREAD-REMAINDER"])
            if count < 0:
                raise ValueError("negative remainder")
            unread_remainder = count
        except (KeyError, ValueError):
            findings.append(Finding("non-numeric-coverage", "UNREAD-REMAINDER"))
    system_reports = ()
    if extracted_at and _utc_timestamp(extracted_at, "EXTRACTED-AT") >= SYSTEM_SUBTYPE_CUTOFF:
        try:
            system_count = int(extract_fields["UNDECLARED-SYSTEM-SUBTYPES"])
            components = tuple(int(extract_fields[field]) for field in (
                "UNDECLARED-ROW-TYPES", "UNDECLARED-CODEX-PAYLOAD-TYPES",
            )) + tuple(int(extract_fields.get(field, "0")) for field in (
                "TRANSCRIPTS-UNREAD", "UNREADABLE-DIRECTORIES",
            ))
            if system_count < 0 or any(count < 0 for count in components):
                raise ValueError("negative remainder component")
            if unread_remainder != system_count + sum(components):
                findings.append(Finding("coverage-mismatch", "UNREAD-REMAINDER"))
            system_reports = (f"undeclared system subtypes {system_count}",)
        except (KeyError, ValueError):
            findings.append(Finding("non-numeric-coverage", "UNDECLARED-SYSTEM-SUBTYPES"))
    elif extracted_at:
        system_reports = ("system-subtype count: not measured (extract predates the count)",)
    system_reports += (reversal_report,)
    system_reports += (f"round {round_number} unverified causes: {unverified}" +
                       ("" if cause_check else f" ({NOT_GRADED} - extract predates check)"),)
    if fingerprint_cutoff and newest_round:
        recorded_fingerprint = extract_fields.get("POSTED-READING-FINGERPRINT", "")
        try:
            current_fingerprint = _posted_reading_fingerprint(run, submission)
        except DamagedRecord as exc:
            finding, report = damaged_record_result(exc, check="the posted-reading fingerprint", artifact=submission)
            current_fingerprint = None
            record_reports.append(report)
            if finding:
                findings.append(Finding("unscannable-review", report))
        except UnreadableRecord as exc:
            current_fingerprint = None
            record_reports.append(fault_report(exc, check="the posted-reading fingerprint"))
        except ValueError:
            current_fingerprint = ""
        if current_fingerprint is not None and (
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
    expected_population = len(identifiers)
    if population != expected_population or review.fields.get("POPULATION") != extract_fields.get("POPULATION"):
        findings.append(Finding("population-mismatch", f"record {population}; extract {expected_population}"))
    if review.fields.get("WATERMARK") != extract_fields.get("WATERMARK") or (
        review.fields.get("WATERMARK") not in identifiers
        and review.fields.get("WATERMARK") not in task_aliases
    ):
        findings.append(Finding("watermark-mismatch", review.fields.get("WATERMARK", "")))
    if review.fields.get("TRANSCRIPTS") != extract_fields.get("TRANSCRIPTS"):
        findings.append(Finding("transcript-mismatch", review.fields.get("TRANSCRIPTS", "")))

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
        disposition = correction.fields.get("DISPOSITION", "")
        if disposition not in DISPOSITIONS:
            continue
        target = correction.fields.get("TARGET", "")
        landing = correction.fields.get("LANDING", "")
        if disposition in {"skill-file", "tracker-ticket"}:
            if not GH_ISSUE.fullmatch(landing):
                findings.append(Finding("unlanded-ticket", correction.event))
            elif (
                _utc_timestamp(extracted_at, "EXTRACTED-AT") >= LANDING_OUTPUT_CUTOFF
                if extracted_at else False
            ):
                if not _successful_gh_call(
                    transcript_paths, landing, _utc_timestamp(extracted_at, "EXTRACTED-AT")
                ):
                    findings.append(Finding("missing-gh-call", correction.event))
            elif transcript_paths and not _successful_gh_call(transcript_paths):
                findings.append(Finding("missing-gh-call", correction.event))
            if reversal_check and GH_ISSUE.fullmatch(landing) and not _successful_gh_call(
                transcript_paths, landing, _utc_timestamp(extracted_at, "EXTRACTED-AT"), require_search=True,
            ):
                findings.append(Finding("missing-landing-search", correction.event))
            causes = _cause_fields(correction, entry_kinds)
            if cause_check and causes is not None and causes[1][0] == "unverified" and not _unverified_publication(
                transcript_paths, landing,
                _utc_timestamp(extracted_at, "EXTRACTED-AT") if extracted_at else None,
            ):
                findings.append(Finding("unverified-publication", correction.event))
        elif disposition == "memory-write":
            if baseline is not None and not _target_changed(target, baseline):
                findings.append(Finding("unlanded-memory", correction.event))
        elif disposition == "check":
            resolved = Path(target).expanduser().resolve()
            if baseline is not None and (resolved not in tracked_files or not _target_changed(target, baseline)):
                findings.append(Finding("unlanded-check", correction.event))

    for sustain in review.sustains:
        if sustain.event not in identifiers:
            findings.append(Finding("unknown-sustain-event", sustain.event))
        if reversal_check and entry_kinds.get(sustain.event) == "reversal-candidates":
            findings.append(Finding("sustain-on-reversal-candidates", sustain.event))
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
            "transcripts_unread": "TRANSCRIPTS-UNREAD",
            "unreadable_directories": "UNREADABLE-DIRECTORIES",
            "links_not_entered": "LINKS-NOT-ENTERED",
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
        unread_remainder=unread_remainder,
        unmeasured_rounds=int(not remainder_cutoff),
        memory_reports=(*record_reports, *memory_reports),
        system_reports=system_reports,
        **diagnostic_counts,
    )


def _optional_count(fields: Mapping[str, str], name: str) -> int:
    try:
        return int(fields.get(name, "0") or "0")
    except ValueError:
        return 0


@completion_checks.dated_scan
def survey(run: Path, submission: str) -> Scan:
    round_numbers = _review_round_numbers(run, submission) or (1,)
    scans = tuple(
        _survey_round(run, submission, round_number, newest_round=round_number == max(round_numbers))
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
        transcripts_unread=sum(scan.transcripts_unread for scan in scans),
        unreadable_directories=sum(scan.unreadable_directories for scan in scans),
        links_not_entered=sum(scan.links_not_entered for scan in scans),
        browser=_sum_browser_diagnostics(scan.browser for scan in scans),
        unread_remainder=(
            sum(scan.unread_remainder or 0 for scan in scans)
            if any(scan.unread_remainder is not None for scan in scans)
            else None
        ),
        unmeasured_rounds=sum(scan.unmeasured_rounds for scan in scans),
        memory_reports=tuple(dict.fromkeys(report for scan in scans for report in scan.memory_reports)),
        system_reports=tuple(dict.fromkeys(report for scan in scans for report in scan.system_reports)),
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
        f"  transcripts unread              {scan.transcripts_unread}",
        f"  unreadable directories          {scan.unreadable_directories}",
        f"  links not entered               {scan.links_not_entered}",
        f"  sittings begun after extract    {scan.later_sittings}",
        f"  unowned browser page actions    {scan.browser.unowned_page_actions} (reported, {NOT_GRADED})",
        f"  tab creation parses: tabs_create_mcp  {scan.browser.creation_parses_tabs_create_mcp}",
        f"  tab creation parses: tabs_context_mcp {scan.browser.creation_parses_tabs_context_mcp}",
        f"  tab creation parses: navigate no tab  {scan.browser.creation_parses_navigate_without_tab}",
        f"  findings                        {len(scan.findings)}",
    ]
    if scan.unread_remainder is not None:
        lines.append(run_grader.format_unread_remainder(scan.unread_remainder))
    lines.extend(scan.memory_reports)
    lines.extend(scan.system_reports)
    if scan.unmeasured_rounds:
        lines.append("unread remainder: not measured (extract predates the count)")
    elif scan.unread_remainder is None:
        lines.append("unread remainder: not measured (extract unavailable or invalid)")
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
    import frozen_grade
    for submission in submissions:
        if frozen_grade.report(run, submission) is not None:
            continue
        scan = survey(run, submission)
        if scan.findings or scan.unread or scan.unread_remainder:
            damage_reports = tuple(report for report in scan.memory_reports if f"{NOT_GRADED} — damaged text" in report)
            return "\n".join((f"{EXPECTED_ROW} is incomplete for {submission}", *damage_reports))
    return None


def _same_path(left: Path, right: Path) -> bool:
    """Compare existing paths by identity before falling back to spelling."""
    try:
        return left.samefile(right)
    except OSError:
        return left.resolve() == right.resolve()


def is_live_run(run: Path) -> bool:
    root = (repo_root.scratch_path(repo_root.scratch_root(), "runs")).resolve()
    return _same_path(run.parent, root)


def completion_gate(run: Path, submission: str | None) -> tuple[bool, str]:
    """Grade the shared expected row only for an explicitly terminal submission."""
    frozen = completion_checks.exemption(run, submission, "aar_scan", EXPECTED_ROW)
    if frozen is not None:
        return False, frozen
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
    root = repo_root.scratch_path(repo_root.scratch_root(), "runs")
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
    unreadable_directories = 0
    links_not_entered = 0
    if is_live_run(run):
        for root in transcript_roots():
            if not root.exists():
                continue
            walk = tree_walk.walk_files(root)
            paths.update(path.resolve() for path in walk.files if path.suffix == ".jsonl")
            unreadable_directories += walk.unreadable_directories
            links_not_entered += walk.links_not_entered
    ordered = tuple(sorted(paths, key=lambda path: str(path).casefold()))
    created_at = _run_created_at(run)
    needle = run.name.encode("utf-8")
    selected: list[Path] = []
    skipped_by_time = 0
    skipped_by_byte_search = 0
    unread = 0
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
            unread += 1
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
        unread=unread,
        unreadable_directories=unreadable_directories,
        links_not_entered=links_not_entered,
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
    "[--transcript <jsonl> --memory-index <path> --extract "
    "[--rebuild-round <number>]] [--measure-memory [--round <number>]] [--show]"
)


def validate(parsed: run_grader.Parsed) -> str | None:
    if not parsed.value("--submission"):
        return "--submission is required"
    if parsed.enabled("--measure-memory") and parsed.enabled("--extract"):
        return "--measure-memory and --extract are separate steps"
    measured_round = parsed.value("--round")
    if measured_round:
        if not parsed.enabled("--measure-memory"):
            return "--round requires --measure-memory"
        if not measured_round.isdecimal() or int(measured_round) < 1:
            return "--round needs a positive round number"
    if parsed.enabled("--extract") and not parsed.value("--memory-index"):
        return "--extract requires --memory-index"
    rebuild = parsed.value("--rebuild-round")
    if rebuild and not parsed.enabled("--extract"):
        return "--rebuild-round requires --extract"
    if rebuild:
        try:
            round_number = int(rebuild)
        except ValueError:
            return "--rebuild-round needs a positive round number"
        if round_number < 1:
            return "--rebuild-round needs a positive round number"
    return None


def load(parsed: run_grader.Parsed) -> Path:
    run = Path(parsed.source).expanduser().resolve()
    if not run.is_dir():
        raise run_grader.SourceError(f"no directory named {run.name}")
    return run


def grade(run: Path, parsed: run_grader.Parsed) -> run_grader.Grade[Scan] | run_grader.EarlyExit:
    submission = parsed.value("--submission")
    assert submission is not None  # validate owns this invocation requirement
    if parsed.enabled("--measure-memory"):
        try:
            round_value = parsed.value("--round")
            round_number = int(round_value) if round_value else None
            destination = measure_memory(run, submission, round_number)
        except UnreadableRecord as exc:
            return run_grader.EarlyExit(2, stdout=(fault_report(exc, check="memory measurement"),))
        except (OSError, UnicodeError, ValueError) as exc:
            return run_grader.EarlyExit(2, stderr=(f"memory index NOT MEASURED: {exc}",))
        return run_grader.EarlyExit(0, stdout=(f"private memory index measurement written: {destination.name}",))
    try:
        retire_orphan_pointers(run)
    except UnreadableRecord as exc:
        if parsed.enabled("--extract"):
            return run_grader.EarlyExit(2, stdout=(fault_report(exc, check="legacy AAR pointer retirement"),))
        mark_not_graded(exc, check="legacy AAR pointer retirement")
    except OSError as exc:
        return run_grader.EarlyExit(
            2,
            stderr=(f"after-action review NOT SCANNED: {exc}",),
        )
    if parsed.enabled("--extract"):
        transcript_value = parsed.value("--transcript")
        memory_value = parsed.value("--memory-index")
        rebuild_value = parsed.value("--rebuild-round")
        assert memory_value is not None  # validate owns this invocation requirement
        rebuilt_scan: Scan | None = None
        try:
            transcript = (
                Path(transcript_value).expanduser().resolve()
                if transcript_value
                else None
            )
            if rebuild_value:
                rebuilt_round = int(rebuild_value)
                record_round = rebuilt_round
                destination, count, _archived = rebuild_extract(
                    run, submission, rebuilt_round
                )
                if review_path(run, submission, rebuilt_round).is_file():
                    rebuilt_scan = survey(run, submission)
            else:
                destination, count = write_extract(
                    run, transcript, submission, Path(memory_value).expanduser().resolve()
                )
                matched_round = re.fullmatch(re.escape(_safe_submission(submission)) + r"(?:\.round-([1-9][0-9]*))?\.extract\.md", destination.name)
                assert matched_round is not None
                record_round = int(matched_round[1] or "1")
            extract_fields, _identifiers = _extract_metadata(destination)
        except DamagedRecord as exc:
            return run_grader.EarlyExit(1, stdout=(damaged_record_result(exc, check="extract", force=True)[1],))
        except UnreadableRecord as exc:
            return run_grader.EarlyExit(2, stdout=(fault_report(exc, check="extract"),))
        except (OSError, ValueError, subprocess.SubprocessError, git_paths.GitPathError) as exc:
            return run_grader.EarlyExit(
                2,
                stderr=(f"after-action review NOT SCANNED: {exc}",),
            )
        stdout = (
                f"after-action review extract over {run.name}",
                f"  candidate population            {count}",
                f"  transcripts found               {extract_fields['TRANSCRIPTS-FOUND']}",
                f"  transcripts skipped by time     {extract_fields['TRANSCRIPTS-SKIPPED-BY-TIME']}",
                f"  transcripts skipped by bytes    {extract_fields['TRANSCRIPTS-SKIPPED-BY-BYTE-SEARCH']}",
                f"  transcripts read                {extract_fields['TRANSCRIPTS-READ']}",
                f"  transcripts unread              {extract_fields.get('TRANSCRIPTS-UNREAD', '0')}",
                f"  unreadable directories          {extract_fields.get('UNREADABLE-DIRECTORIES', '0')}",
                f"  links not entered               {extract_fields.get('LINKS-NOT-ENTERED', '0')}",
                f"  agents instructions recognized  {extract_fields.get('AGENTS-INSTRUCTIONS', '0')}",
                *(
                    (f"  rebuilt round                 {rebuild_value}",)
                    if rebuild_value
                    else ()
                ),
                f"  private extract written         {destination.name}",
                f"  review record filename          {review_path(run, submission, record_round).name}",
        )
        recorded_remainder = extract_fields.get("UNREAD-REMAINDER")
        remainder = int(recorded_remainder) if recorded_remainder is not None else None
        if rebuilt_scan is not None:
            stdout = (*stdout, "", format_report(rebuilt_scan, run.name))
        elif remainder is None:
            stdout = (*stdout, "unread remainder: not measured (extract predates the count)")
        else:
            stdout = (*stdout, run_grader.format_unread_remainder(remainder))
        if rebuilt_scan is not None and rebuilt_scan.findings:
            status = 1
        elif remainder or (rebuilt_scan is not None and rebuilt_scan.unread_remainder):
            status = 2
        else:
            status = 0
        return run_grader.EarlyExit(status, stdout=stdout)

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
        coverage_failed=bool(scan.unread_remainder),
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
        run_grader.Option("--measure-memory"),
        run_grader.Option("--round", takes_value=True),
        run_grader.Option(
            "--rebuild-round",
            takes_value=True,
            missing_value="--rebuild-round needs a positive round number",
        ),
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
