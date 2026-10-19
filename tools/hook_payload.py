"""Shared unreadable harness-payload policy. ADR 0392, #1728.

The caller owns its literal trigger; a missing trigger means a Stop check.
No raw input or exception text is copied into the response.
"""

from __future__ import annotations

from collections.abc import Callable
import json
import sys


DECLARED_LIMITS = (
    "Raw literal searches cannot see escaped, split, or otherwise rewritten triggers.",
    "A failed stream read supplies no raw text and allows with a warning.",
    "A parsed object is passed to the guard unless its optional field validator rejects it; "
    "rejected fields use the same original-raw-text policy as unreadable JSON.",
    "Response fields are tested as emitted JSON; their display by a host is not established here.",
)


def read_payload(
    guard: str, trigger: Callable[[str], bool] | None = None,
    *, validate: Callable[[dict], bool] | None = None,
) -> tuple[dict | None, dict]:
    """Return a parsed object or a visible unreadable outcome for this event."""
    raw = None
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
        if isinstance(payload, dict) and (validate is None or validate(payload)):
            return payload, {}
    except (ValueError, OSError, UnicodeError, TypeError, RecursionError):
        pass

    note = f"{guard}: unreadable hook payload; did not grade the {'call' if trigger else 'turn'}."
    if trigger is None:
        return None, {"continue": True, "systemMessage": note}

    denied = raw is not None and trigger(raw)
    note += " Refused on the raw trigger." if denied else " Allowed with no raw trigger."
    specific = {"hookEventName": "PreToolUse", "additionalContext": note}
    if denied:
        specific.update(permissionDecision="deny", permissionDecisionReason=note)
    return None, {"hookSpecificOutput": specific, "systemMessage": note}
