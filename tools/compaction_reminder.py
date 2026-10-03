#!/usr/bin/env python3
"""Remind a compacted Claude Code session to read standing rule 7. #1206.

This is an instruction, never a reply-blocking check. SessionStart applies to
subagent sessions too; the hook selects only its compact source.
"""

from __future__ import annotations

import json
import sys

from console_codec import require_python_floor, use_utf8


DECLARED_LIMITS = (
    "A result misremembered with no compaction in between is outside this reminder.",
    "Whether an agent obeys the reminder is not checked.",
    "What a Codex summary keeps is not inspected.",
    "A piped or chained status in ordinary work belongs to #1457, not this reminder.",
)

REMINDER = (
    "The compaction summary holds no command result that may be stated. "
    "Read AGENTS.md standing rule 7 before reporting a command result: "
    "re-observe it after this compaction, or use the rule's last-resort label."
)


def main() -> int:
    try:
        # #1520's shared stdin helper has not landed. Decode the wire bytes,
        # rather than the Windows locale's text wrapper.
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (ValueError, UnicodeError):
        return 0
    if not isinstance(payload, dict) or payload.get("source") != "compact":
        return 0
    if payload.get("hook_event_name") != "SessionStart":
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": REMINDER,
    }}))
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
