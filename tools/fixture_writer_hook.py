#!/usr/bin/env python3
"""Guard fixture-generating Claude spawns. ADR 0403, #1800."""

from __future__ import annotations

import json
import re

from console_codec import require_python_floor, use_utf8
from hook_payload import read_payload


DECLARED_LIMITS = (
    "Unreadable payloads refuse when the raw text names scratch/fixture-runs after slash "
    "normalization; otherwise they allow with a warning. A failed stream read allows "
    "with a warning, and escaped or split raw triggers may evade that search.",
    "Output outside scratch/fixture-runs is invisible to this launch guard.",
    "Only literal paths in spawn inputs are recognized; computed or split paths evade it.",
    "This checks the requested subagent type, not whether the host honored omitClaudeMd; "
    "the per-run recall proof must pass before generation.",
    "Desktop worktrees may load hooks and agents from the main checkout; a branch-only "
    "installation supplies no live protection until that owning checkout is refreshed.",
)


def names_fixture_run(text: str) -> bool:
    normalized = re.sub(r"[\\/]+", "/", text)
    return re.search(r"(?<![\w.-])scratch/fixture-runs(?:/|\b(?![\w.-]))", normalized, re.I) is not None


def valid_payload(payload: dict) -> bool:
    inputs = payload.get("tool_input")
    return isinstance(payload.get("tool_name"), str) and isinstance(inputs, dict)


def handle(payload: dict) -> dict:
    """Return the host decision without disclosing any spawn text."""
    if payload.get("tool_name") not in {"Agent", "Task"}:
        return {}
    inputs = payload["tool_input"]
    if not names_fixture_run(json.dumps(inputs, ensure_ascii=False)):
        return {}
    if inputs.get("subagent_type") == "fixture-writer":
        return {}
    reason = "Fixture run spawn refused: use fixture-writer and pass the per-run recall proof before generation."
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}


def main() -> int:
    payload, response = read_payload(
        "fixture_writer_hook", names_fixture_run, validate=valid_payload,
    )
    if payload is not None:
        response = handle(payload)
    if response:
        print(json.dumps(response))
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
