#!/usr/bin/env python3
"""Retract a bundled or incomplete grilling question after display. #1392."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping

from console_codec import require_python_floor, use_utf8


REPO_ROOT = Path(__file__).resolve().parent.parent
FORMAT_PATH = REPO_ROOT / "docs" / "agents" / "grilling.md"
AGENTS_PATH = Path.home() / ".codex" / "AGENTS.md"
BLOCK_START = "<!-- clinical-skills:grilling:start -->"
BLOCK_END = "<!-- clinical-skills:grilling:end -->"
CLOSING_LINE = "Frontier empty — confirm shared understanding."

SKILL_PATH = re.compile(
    r"(?i)(?:^|[/\\])(?:grilling|grill-me|grill-with-docs)"
    r"[/\\]SKILL\.md(?=$|[\s\"'])"
)
PLAIN_QUESTION_LABEL = re.compile(
    r"(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?"
    r"(?:Q\s*\d+|Question\s+\d+)(?:\*\*)?(?=\s|[.):-])"
)
RECOMMENDATION_LINE = re.compile(r"(?m)^\s*➡️")
HELD_LINE = re.compile(r"(?im)^\s*Held for later:\s*\S")

RETRACT_REASON = (
    "Retract the bundled or incomplete grilling question, then re-ask exactly one "
    "question using docs/agents/grilling.md: explain why it exists, give lettered "
    "options with costs, include one ❓ block, a ➡️ recommendation with reasons, "
    "and a Held for later line."
)

DECLARED_LIMITS = (
    "A skill load is recognized only in a completed Codex command record whose parsed command classifies the SKILL.md path as a read.",
    "A renamed grilling skill is not active until its SKILL.md directory name is added.",
    "Malformed or unreadable transcript rows cannot establish that grilling is active.",
    "Question labels are recognized only at the start of a line in the documented numbered forms.",
    "Quoted-question exemptions cover blockquotes, paired straight or curly double quotes, and one-line backticks.",
    "The hook does not grade whether the rationale is plain, the options are lettered, or each option states a cost.",
    "The hook does not grade the recommendation's reasons or the semantic content of the Held for later line.",
    "Several decisions hidden inside one ❓ block are outside the mechanical question-count check.",
)


def marked_block(format_text: str) -> str:
    """Return the exact user-level AGENTS block installed from the tracked format."""
    body = format_text.strip("\r\n")
    return f"{BLOCK_START}\n{body}\n{BLOCK_END}\n"


def _string_values(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list):
        return tuple(part for item in value for part in _string_values(item))
    if isinstance(value, dict):
        return tuple(part for item in value.values() for part in _string_values(item))
    return ()


def _opened_skill_paths(record: Mapping[str, Any]) -> tuple[str, ...]:
    """Return paths Codex reports as successfully read by one completed command."""
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return ()
    if record.get("type") == "event_msg":
        item = payload.get("item")
        if (
            isinstance(item, dict)
            and item.get("type") == "CommandExecution"
            and item.get("status") == "completed"
        ):
            parsed = item.get("parsed_cmd")
            if not isinstance(parsed, list):
                return ()
            return tuple(
                path
                for command in parsed
                if isinstance(command, dict) and command.get("type") == "read"
                for path in (command.get("path"), command.get("name"))
                if isinstance(path, str)
            )
    return ()


def _assistant_text(record: Mapping[str, Any]) -> str:
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return ""
    if (
        record.get("type") == "response_item"
        and payload.get("type") == "message"
        and payload.get("role") == "assistant"
    ):
        return "\n".join(_string_values(payload.get("content")))
    if record.get("type") == "event_msg":
        item = payload.get("item")
        if isinstance(item, dict) and item.get("type") == "AgentMessage":
            return "\n".join(_string_values(item.get("content")))
    return ""


def grilling_active(transcript_path: Path) -> bool:
    """Replay skill loads and closing replies to determine the current interval."""
    try:
        lines = transcript_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    active = False
    for line in lines:
        try:
            record = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(record, dict):
            continue
        if any(SKILL_PATH.search(path) for path in _opened_skill_paths(record)):
            active = True
        if CLOSING_LINE in _assistant_text(record):
            active = False
    return active


def _mask_exempt_text(message: str) -> str:
    text = re.sub(r"(?m)^\s*>.*$", "", message)
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r'"(?:[^"\\]|\\.)*"', "", text)
    text = re.sub(r"“[^”\n]*”", "", text)
    return text


def _outside_question_block(message: str) -> str:
    marker = message.find("❓")
    if marker < 0:
        return message
    boundaries = [
        match.start()
        for pattern in (RECOMMENDATION_LINE, HELD_LINE)
        for match in pattern.finditer(message, marker + 1)
    ]
    end = min(boundaries) if boundaries else len(message)
    return message[:marker] + (" " * (end - marker)) + message[end:]


def violations(message: str) -> tuple[str, ...]:
    """Return every one-question format failure visible in one assistant reply."""
    findings: list[str] = []
    question_blocks = message.count("❓")
    if question_blocks >= 2:
        findings.append("two or more ❓ question blocks")
    if PLAIN_QUESTION_LABEL.search(message):
        findings.append("a plain-text numbered question label")
    if question_blocks:
        if RECOMMENDATION_LINE.search(message) is None:
            findings.append("the ❓ question has no ➡️ recommendation")
        if HELD_LINE.search(message) is None:
            findings.append("the ❓ question has no Held for later line")
    outside = _mask_exempt_text(_outside_question_block(message))
    if "?" in outside:
        findings.append("a question appears outside the ❓ block")
    return tuple(findings)


def installed_block_is_current(format_path: Path, agents_path: Path) -> bool:
    try:
        expected = marked_block(format_path.read_text(encoding="utf-8")).strip()
        installed = agents_path.read_text(encoding="utf-8")
    except OSError:
        return False
    match = re.search(
        re.escape(BLOCK_START) + r".*?" + re.escape(BLOCK_END),
        installed,
        flags=re.DOTALL,
    )
    return match is not None and match.group(0).strip() == expected


def handle(
    payload: Mapping[str, Any],
    *,
    format_path: Path = FORMAT_PATH,
    agents_path: Path = AGENTS_PATH,
) -> dict[str, object]:
    """Return a Codex Stop-hook decision for one payload."""
    if payload.get("stop_hook_active") is True:
        return {}
    transcript = payload.get("transcript_path")
    message = payload.get("last_assistant_message")
    if not isinstance(transcript, str) or not isinstance(message, str):
        return {}
    if not grilling_active(Path(transcript)):
        return {}
    if CLOSING_LINE in message:
        return {}

    stale = not installed_block_is_current(format_path, agents_path)
    failures = violations(message)
    if failures:
        reason = RETRACT_REASON + " Found: " + "; ".join(failures) + "."
        if stale:
            reason += " The installed ~/.codex/AGENTS.md grilling block is stale; rerun the installer."
        return {"decision": "block", "reason": reason}
    if stale:
        return {
            "continue": True,
            "systemMessage": (
                "The installed ~/.codex/AGENTS.md grilling block is stale; run "
                "python tools/install_grilling_guard.py from the current clinical-skills checkout."
            ),
        }
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
