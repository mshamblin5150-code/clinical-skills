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
    directory_suffix: str
    approval_record: str
    completion_command: str


RUN_KINDS = (
    RunKind(
        skill="course-assignment",
        directory_suffix="-course-assignment",
        approval_record="submission-gates.json",
        completion_command="course_assignment_scan.py",
    ),
)
MODULE_ROOT = Path(__file__).resolve().parent.parent
STATE_RECORD = "run-status.json"
RUN_PATH = re.compile(
    r"(?i)(?:[A-Z]:[\\/]|/)?[^\r\n\"'`<>|]*?scratch[\\/]runs[\\/]"
    r"[^\\/\s\"'`<>|]+"
)
STATUS_LINE = re.compile(
    r"(?m)^Run status: (awaiting upload|awaiting posted reading|awaiting AAR|complete|stopped(?: - (?P<reason>\S.*))?)\s*$"
)
ANY_STATUS_LINE = re.compile(r"(?m)^Run status:.*$")

DECLARED_LIMITS = (
    "A run is in scope only after its path appears in the session transcript and its durable approval record says Gate 1 is approved.",
    "When several approved course-assignment runs appear in one session, the most recently mentioned run is graded.",
    "Waiting-status truth beyond complete and the presence of a stopped reason remains a clinician reading.",
    "A terminal grade is attempted only for complete and requires the artifact path recorded at approval.",
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


def touched_runs(records: tuple[dict[str, object], ...]) -> tuple[tuple[Path, RunKind], ...]:
    """Return transcript-mentioned run directories in last-mentioned order."""

    found: dict[Path, RunKind] = {}
    for record in records:
        for value in _string_values(record):
            for match in RUN_PATH.finditer(value):
                path = Path(match.group(0).strip()).resolve()
                spec = next(
                    (
                        item
                        for item in RUN_KINDS
                        if path.name.casefold().endswith(item.directory_suffix)
                    ),
                    None,
                )
                if spec is not None:
                    found.pop(path, None)
                    found[path] = spec
    return tuple(found.items())


def _approval(run: Path, spec: RunKind) -> dict[str, object] | None:
    try:
        value = json.loads((run / spec.approval_record).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) and value.get("gate1_approved") is True else None


def completion_is_clean(run: Path, spec: RunKind, approval: Mapping[str, object]) -> bool:
    artifact = approval.get("artifact_path")
    if not isinstance(artifact, str) or not artifact:
        return False
    path = Path(artifact)
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(MODULE_ROOT / "tools" / spec.completion_command),
                str(run),
                "--artifact",
                str(path),
                "--submission",
                path.stem,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=25,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


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
        "reason": "Retract the reply and end its replacement with exactly one valid Run status: line. "
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
    open_runs = [
        (run, spec, approval)
        for run, spec in touched_runs(records)
        if (approval := _approval(run, spec)) is not None
    ]
    if not open_runs:
        return {}
    run, spec, approval = open_runs[-1]
    revision = approval.get("approval_revision")
    state = _state(run)
    if state.get("status") == "complete" and state.get("approval_revision") == revision:
        return {}
    lines = ANY_STATUS_LINE.findall(message)
    if len(lines) != 1:
        return _blocked("An approved run reply needs exactly one Run status: line.")
    match = STATUS_LINE.search(message)
    if match is None or message[match.end() :].strip():
        if lines[0].rstrip().endswith("stopped -"):
            return _blocked("Run status: stopped needs a substantive reason after the hyphen.")
        return _blocked("The Run status: line is malformed or is not the reply's final line.")
    status = match.group(1)
    stopped_here = (
        state.get("status") == "stopped"
        and state.get("approval_revision") == revision
    )
    if stopped_here and not status.startswith("stopped") and status != "complete":
        return _blocked("This run stays stopped until it completes or another approval is recorded.")
    if status == "complete" and not completion_is_clean(run, spec, approval):
        return _blocked("Run status: complete requires a clean terminal grade.")
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
