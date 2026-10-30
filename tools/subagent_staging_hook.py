"""Read Claude launch briefs before dispatch. ADR 0375, #1593."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from console_codec import require_python_floor, use_utf8
from hook_payload import read_payload
from repo_root import scratch_path
from shell_reader import candidate_paths


DECLARED_LIMITS = (
    "Claude Code launches only; Codex launches are outside this guard.",
    "Live probe on 2026-10-19, Claude Code 2.1.284, with an explicit --settings hook: "
    "direct launch emitted Agent with tool_input.prompt and tool_input.subagent_type. "
    "Workflow emitted tool_input.script and its subagent did not emit an Agent/Task "
    "hook event. Workflow launches are outside this guard. Task is registered for compatibility.",
    "Path recognition is a literal floor: slash/backslash paths, quoted paths with spaces, "
    "common temp variables and location phrases are recognized; computed, split and "
    "unrecognized paths evade it. Mentions, including prohibitions, still match.",
    "A patient-work brief that never names scratch/runs/ or output/ owes no staging route.",
    "Existence cannot prove freshness: a staging folder missed by cleanup still passes.",
    "Unreadable payloads refuse only on recognized temp/scratchpad locations or scratch/runs/ "
    "or output/ in raw text (clinician ruling 2026-10-19); otherwise both audiences get a "
    "warning. A failed stream read allows with a warning; escaped or split triggers may evade it.",
    "Desktop worktrees can load hooks from the main checkout; branch-only settings supply "
    "no live protection until the owning checkout is refreshed.",
    "Claude session transcripts and saved tool outputs still hold patient text outside cleanup.",
)

ROOT = Path(__file__).resolve().parent.parent
RUN = re.compile(r"(?<![\w.-])(?:scratch/runs|output)/", re.I)
STAGING = re.compile(r"(?<![\w.-])scratch/sessions/", re.I)
TOKENS = re.compile(r'''`([^`\n]+)`|"([^"\n]+)"|'([^'\n]+)'|([^\s`"'<>()\[\]{},;]+)''')
TEMP = re.compile(
    r"(?<![\w.-])/(?:tmp|var/tmp|private/tmp)(?:/|\b)"
    r"|(?:appdata/local|windows)/temp(?:/|\b)"
    r"|%(?:temp|tmp)%|\$(?:env:)?(?:temp|tmp)\b|\$\{(?:temp|tmp)\}"
    r"|\bsession scratchpad\b|\bsystem temp(?:orary)? director(?:y|ies)\b"
    r"|\btempfile\.gettempdir\(", re.I,
)


def normalized(text: str) -> str:
    return re.sub(r"[\\/]+", "/", text)


def names_temp(text: str) -> bool:
    text = normalized(text)
    if TEMP.search(text):
        return True
    locations = [tempfile.gettempdir(), os.environ.get("TEMP", ""), os.environ.get("TMP", "")]
    return any(re.search(re.escape(normalized(location).rstrip("/")) + r"(?:/|\b)", text, re.I)
               for location in locations if location)


def raw_trigger(text: str) -> bool:
    return names_temp(text) or RUN.search(normalized(text)) is not None


def valid_payload(payload: dict) -> bool:
    inputs = payload.get("tool_input")
    return (isinstance(payload.get("tool_name"), str) and isinstance(inputs, dict)
            and isinstance(inputs.get("prompt"), str))


def refuse() -> dict:
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "Subagent staging refused: create the pass's "
        "scratch/sessions/<key>/<pass-label>/ folder in a registered checkout first, "
        "name that existing folder in the brief, and use it for staging instead of temp "
        "or the session scratchpad. Relative paths require the payload's absolute cwd.",
    }}


def registered_roots() -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "worktree", "list", "--porcelain", "-z"],
        capture_output=True, check=True, timeout=10,
    )
    return [Path(os.fsdecode(row.removeprefix(b"worktree "))).resolve()
            for row in result.stdout.split(b"\0") if row.startswith(b"worktree ")]


def staging_tokens(prompt: str) -> list[str]:
    """Return the brief's literal tokens under scratch/sessions/, as written."""
    tokens = (next(group for group in match.groups() if group is not None).rstrip(".")
              for match in TOKENS.finditer(normalized(prompt)))
    return [token for token in tokens if STAGING.search(token)]


def resolve_staging(tokens: list[str], cwd: str | None) -> list[Path]:
    """Resolve staging tokens, using the payload's cwd for a relative one."""
    paths = []
    for token in tokens:
        path = Path(candidate_paths(token)[-1])
        if not path.is_absolute():
            if not isinstance(cwd, str) or not Path(cwd).is_absolute():
                raise ValueError("relative staging path requires absolute cwd")
            path = Path(cwd) / path
        paths.append(path.resolve())
    return paths


def handle(payload: dict) -> dict:
    if payload["tool_name"] not in {"Agent", "Task"}:
        return {}
    prompt = payload["tool_input"]["prompt"]
    if names_temp(prompt):
        return refuse()
    if not RUN.search(normalized(prompt)):
        return {}
    try:
        roots = registered_roots()
        paths = resolve_staging(staging_tokens(prompt), payload.get("cwd"))
        for path in paths:
            if not path.is_dir() or not any(
                path != (base := scratch_path(root / "scratch", "sessions").resolve())
                and path.is_relative_to(base) and path.is_relative_to(root)
                for root in roots
            ):
                return refuse()
        return {} if paths else refuse()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
        return refuse()


def main() -> int:
    payload, response = read_payload("subagent_staging_hook", raw_trigger, validate=valid_payload)
    if payload is not None:
        response = handle(payload)
    if response:
        print(json.dumps(response))
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
