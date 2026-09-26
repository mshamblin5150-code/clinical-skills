#!/usr/bin/env python3
"""Retract an approved graded-run reply whose terminal status is invalid. #1398."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Mapping

from console_codec import require_python_floor, use_utf8


@dataclass(frozen=True)
class RunKind:
    skill: str
    approval_record: str
    completion_command: str


RUN_KINDS = (
    RunKind(
        skill="course-assignment",
        approval_record="submission-gates.json",
        completion_command="course_assignment_scan.py",
    ),
    *(
        RunKind(
            skill=skill,
            approval_record="posting-approvals.json",
            completion_command=f"{command}.py",
        )
        for skill, command in (
            ("discussion-post", "discussion_post_scan"),
            ("discussion-reply", "discussion_reply_scan"),
            ("peer-critique", "peer_critique_scan"),
            ("practicum-case-study", "checks_ledger"),
            ("clinical-note", "differential_scan"),
            ("batch-shift", "filled_vitals_census"),
        )
    ),
)
RUN_KIND_BY_SKILL = {item.skill: item for item in RUN_KINDS}
MODULE_ROOT = Path(__file__).resolve().parent.parent
STATE_RECORD = "run-status.json"
RUN_PATH = re.compile(
    r"(?i)(?:[A-Z]:[\\/]|/)?[^\r\n\"'`<>|]*?scratch[\\/]runs[\\/]"
    r"[^\\/\s\"'`<>|]+"
)
STATUS_LINE = re.compile(
    r"(?m)^Run status: (?P<run_key>[A-Za-z0-9][A-Za-z0-9._-]*) — "
    r"(?P<status>awaiting posting|awaiting posted reading|awaiting AAR|complete|stopped(?: - (?P<reason>\S.*))?)\s*$"
)
ANY_STATUS_LINE = re.compile(r"(?m)^Run status:.*$")
SHA256 = re.compile(r"[0-9a-f]{64}")

DECLARED_LIMITS = (
    "A run is in scope only after its path appears in the session transcript and a readable durable approval record names an approved item.",
    "Every touched open run needs one keyed status line; a current completed approval revision is not reopened by an unrelated later reply.",
    "Waiting-status truth beyond complete and the presence of a stopped reason remains a clinician reading.",
    "A terminal grade is attempted only for complete and uses each approved item's recorded public grader invocation.",
    "Malformed transcript rows and unreadable approval records cannot establish an open approved run.",
)


def _string_values(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(part for item in value for part in _string_values(item))
    if isinstance(value, dict):
        return tuple(part for item in value.values() for part in _string_values(item))
    return ()


def _assistant_text(record: Mapping[str, Any]) -> str:
    payload = record.get("payload")
    if isinstance(payload, dict):
        if (
            record.get("type") == "response_item"
            and payload.get("type") == "message"
            and payload.get("role") == "assistant"
        ):
            return "\n".join(_string_values(payload.get("content")))
        item = payload.get("item")
        if isinstance(item, dict) and item.get("type") == "AgentMessage":
            return "\n".join(_string_values(item.get("content")))
    message = record.get("message")
    if isinstance(message, dict) and message.get("role") == "assistant":
        return "\n".join(_string_values(message.get("content")))
    return ""


def _records(transcript: Path) -> tuple[dict[str, object], ...]:
    try:
        lines = transcript.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    records: list[dict[str, object]] = []
    for line in lines:
        try:
            value = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(value, dict):
            records.append(value)
    return tuple(records)


def touched_runs(records: tuple[dict[str, object], ...]) -> tuple[Path, ...]:
    """Return transcript-mentioned run directories in last-mentioned order."""

    found: dict[Path, None] = {}
    for record in records:
        for value in _string_values(record):
            for match in RUN_PATH.finditer(value):
                path = Path(match.group(0).strip()).resolve()
                found.pop(path, None)
                found[path] = None
    return tuple(found)


def _read_object(path: Path) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def approvals(run: Path) -> tuple[tuple[RunKind, dict[str, object]], ...]:
    """Read every approved item in one run from either durable record shape."""

    found: list[tuple[RunKind, dict[str, object]]] = []
    assignment_spec = RUN_KIND_BY_SKILL.get("course-assignment")
    assignment = (
        _read_object(run / assignment_spec.approval_record)
        if assignment_spec is not None
        else None
    )
    if assignment is not None and assignment.get("gate1_approved") is True:
        artifact = assignment.get("artifact_path")
        if isinstance(artifact, str) and artifact:
            found.append(
                (
                    assignment_spec,
                    {
                        **assignment,
                        "skill": "course-assignment",
                        "submission": Path(artifact).stem,
                    },
                )
            )
    posting_specs = tuple(
        spec for spec in RUN_KIND_BY_SKILL.values() if spec.skill != "course-assignment"
    )
    record_names = {spec.approval_record for spec in posting_specs}
    if len(record_names) != 1:
        return tuple(found)
    posting = _read_object(run / next(iter(record_names)))
    if (
        posting is None
        or posting.get("version") != 1
        or not _positive_integer(posting.get("approval_revision"))
    ):
        return tuple(found)
    items = posting.get("items") if posting is not None else None
    if isinstance(items, list):
        validated: list[tuple[RunKind, dict[str, object]]] = []
        keys: set[tuple[str, str]] = set()
        for item in items:
            validated_item = _validated_posting_item(item)
            if validated_item is None:
                return tuple(found)
            spec, value = validated_item
            key = (spec.skill, str(value["submission"]))
            if key in keys:
                return tuple(found)
            keys.add(key)
            validated.append((spec, value))
        found.extend(validated)
    return tuple(found)


def _positive_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _validated_posting_item(
    item: object,
) -> tuple[RunKind, dict[str, object]] | None:
    if not isinstance(item, dict):
        return None
    skill = item.get("skill")
    spec = RUN_KIND_BY_SKILL.get(skill) if isinstance(skill, str) else None
    submission = item.get("submission")
    digest = item.get("sha256")
    sources = item.get("sources")
    grader_args = item.get("grader_args")
    if (
        spec is None
        or spec.skill == "course-assignment"
        or not isinstance(submission, str)
        or not submission
        or not isinstance(digest, str)
        or SHA256.fullmatch(digest) is None
        or not isinstance(sources, list)
        or not sources
        or not all(isinstance(source, str) and source for source in sources)
        or not isinstance(grader_args, list)
        or not grader_args
        or not all(isinstance(argument, str) for argument in grader_args)
        or "--submission" in grader_args
        or item.get("posting_route")
        not in {"awaiting-posting", "agent", "clinician"}
        or item.get("pregrade_status") not in {"clean", "incomplete"}
        or not _positive_integer(item.get("approval_revision"))
    ):
        return None
    return spec, item


def completion_is_clean(run: Path, spec: RunKind, approval: Mapping[str, object]) -> bool:
    if spec.skill == "course-assignment":
        artifact = approval.get("artifact_path")
        if not isinstance(artifact, str) or not artifact:
            return False
        path = Path(artifact)
        arguments = [str(run), "--artifact", str(path), "--submission", path.stem]
    else:
        stored = approval.get("grader_args")
        submission = approval.get("submission")
        if (
            not isinstance(stored, list)
            or not all(isinstance(value, str) for value in stored)
            or not isinstance(submission, str)
            or not submission
            or "--submission" in stored
        ):
            return False
        arguments = [*stored, "--submission", submission]
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(MODULE_ROOT / "tools" / spec.completion_command),
                *arguments,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=25,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def _approval_revision(items: tuple[tuple[RunKind, dict[str, object]], ...]) -> str:
    population = sorted(
        (
            spec.skill,
            str(item.get("submission", "")),
            item.get("approval_revision"),
        )
        for spec, item in items
    )
    return json.dumps(population, separators=(",", ":"))


def _state(run: Path) -> dict[str, object]:
    try:
        value = json.loads((run / STATE_RECORD).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _write_state(run: Path, value: Mapping[str, object]) -> None:
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=run, delete=False
    ) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, run / STATE_RECORD)


def _last_assistant_message(records: tuple[dict[str, object], ...]) -> str:
    return next(
        (text for record in reversed(records) if (text := _assistant_text(record))),
        "",
    )


def _blocked(reason: str) -> dict[str, object]:
    return {
        "decision": "block",
        "reason": "Retract the reply and end its replacement with the required keyed Run status: line block. "
        + reason,
    }


def handle(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return one Codex/Claude Stop-hook decision for an approved run."""

    if payload.get("stop_hook_active") is True:
        return {}
    transcript_path = payload.get("transcript_path")
    if not isinstance(transcript_path, str):
        return {}
    records = _records(Path(transcript_path))
    message = payload.get("last_assistant_message")
    if not isinstance(message, str):
        message = _last_assistant_message(records)
    if not message:
        return {}
    open_runs: list[
        tuple[Path, tuple[tuple[RunKind, dict[str, object]], ...], str]
    ] = []
    for run in touched_runs(records):
        approved = approvals(run)
        if not approved:
            continue
        revision = _approval_revision(approved)
        state = _state(run)
        if state.get("status") == "complete" and state.get("approval_revision") == revision:
            continue
        open_runs.append((run, approved, revision))
    if not open_runs:
        return {}
    lines = tuple(ANY_STATUS_LINE.finditer(message))
    if len(lines) != len(open_runs):
        return _blocked("Each touched approved run needs exactly one keyed Run status: line.")
    matches = tuple(STATUS_LINE.fullmatch(match.group(0)) for match in lines)
    if any(match is None for match in matches):
        if any(line.group(0).rstrip().endswith("stopped -") for line in lines):
            return _blocked("Run status: stopped needs a substantive reason after the hyphen.")
        return _blocked("A Run status: line is malformed.")
    first = lines[0].start()
    tail = message[first:].splitlines()
    if len(tail) != len(lines) or not all(STATUS_LINE.fullmatch(line) for line in tail):
        return _blocked("The keyed Run status: lines must be the reply's final contiguous block.")
    by_key = {match.group("run_key"): match for match in matches if match is not None}
    expected_keys = {run.name for run, _approved, _revision in open_runs}
    if len(by_key) != len(matches) or set(by_key) != expected_keys:
        return _blocked("The keyed Run status: lines must name every touched run key once.")
    for run, approved, revision in open_runs:
        match = by_key[run.name]
        status = match.group("status")
        state = _state(run)
        stopped_here = (
            state.get("status") == "stopped"
            and state.get("approval_revision") == revision
        )
        if stopped_here and not status.startswith("stopped") and status != "complete":
            return _blocked(
                f"Run {run.name} stays stopped until it completes or another approval is recorded."
            )
        if status == "complete" and not all(
            completion_is_clean(run, spec, approval) for spec, approval in approved
        ):
            return _blocked(
                f"Run status: {run.name} — complete requires a clean terminal grade for every approved item."
            )
    for run, _approved, revision in open_runs:
        match = by_key[run.name]
        status = match.group("status")
        if status.startswith("stopped"):
            _write_state(
                run,
                {
                    "status": "stopped",
                    "reason": match.group("reason"),
                    "approval_revision": revision,
                },
            )
        elif status == "complete":
            _write_state(
                run,
                {"status": "complete", "approval_revision": revision},
            )
    return {}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        payload = {}
    response = handle(payload if isinstance(payload, dict) else {})
    if response:
        json.dump(response, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
