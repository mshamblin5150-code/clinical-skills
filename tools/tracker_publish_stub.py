"""Cheap Bash registration stub for the tracker pre-publication hook."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from console_codec import require_python_floor, use_utf8


HOOK = Path(__file__).with_name("tracker_publish_hook.py")


def _decoded_command(payload: bytes) -> str | None:
    try:
        decoded = json.loads(payload)
        command = decoded["tool_input"]["command"]
    except (KeyError, TypeError, UnicodeError, json.JSONDecodeError):
        return None
    return command if isinstance(command, str) else None


def dispatch(payload: bytes) -> bytes:
    """Return an empty response only when decoded command text cannot name gh."""
    command = _decoded_command(payload)
    if command is not None and "gh" not in command:
        return b"{}"
    completed = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        check=False,
    )
    if completed.stderr:
        sys.stderr.buffer.write(completed.stderr)
    return completed.stdout


def main() -> int:
    sys.stdout.buffer.write(dispatch(sys.stdin.buffer.read()))
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
