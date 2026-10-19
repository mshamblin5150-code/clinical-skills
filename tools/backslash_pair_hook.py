"""Refuse doubled backslashes before Claude Code changes them. ADR 0368, #1581."""

from __future__ import annotations

import json

from console_codec import require_python_floor, use_utf8
from hook_payload import read_payload


PROBE = r"printf '%s\n' 'backslash-probe: a\\b'"
DECLARED_LIMITS = (
    "Reads only tool_input.command; no shell parsing, target resolution, or heredoc detection.",
    'Refuses even a correct double-quoted doubled backslash before an ordinary character; '
    'one backslash is its fix, with or without the harness defect.',
    f"Exempts only {PROBE}; one output backslash means the defect stands, two means a ticket retires this hook.",
    "Measurement: 2026-10-16, Claude Code 2.1.284, Bash and Monitor halve backslash runs. "
    "Reports: anthropics/claude-code#85856, #97409, #100063.",
    "Repo settings only: older checkouts, other repositories, and Codex are outside its reach. "
    "Desktop worktree sessions may load main-checkout hooks; a bridged CLI session must test this copy.",
    "Unreadable JSON, non-object payloads, and missing or non-text commands use ADR 0392: "
    "refuse four consecutive backslashes in the original raw text, otherwise allow with "
    "backslash check: unread in additionalContext and systemMessage. A failed read has no raw trigger.",
    "Raw literal search cannot see escaped, split, or rewritten triggers; "
    "emitted warning fields alone do not prove host display.",
)
REMEDY = (
    "Backslash pair refused: Bash and Monitor halve backslash runs. Put the content in a file "
    "with the Write tool and run that file, or write a single backslash where the shell keeps it literal. "
    "A correct double-quoted doubled backslash before an ordinary character is refused too; "
    "one backslash is its fix. "
    f"The only exempt probe is {PROBE}. One output backslash means the defect stands; "
    "two means a ticket retires the hook. See backslash_pair_hook.DECLARED_LIMITS."
)


def readable_command(payload: dict) -> bool:
    tool_input = payload.get("tool_input")
    return isinstance(tool_input, dict) and isinstance(tool_input.get("command"), str)


def main() -> int:
    payload, response = read_payload(
        "backslash check: unread", lambda raw: chr(92) * 4 in raw,
        validate=readable_command,
    )
    if payload is not None:
        command = payload["tool_input"]["command"]
        if command != PROBE and chr(92) * 2 in command:
            response = {"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": "deny",
                "permissionDecisionReason": REMEDY,
            }}
    print(json.dumps(response))
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
