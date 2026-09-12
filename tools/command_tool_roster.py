"""Report command-bearing transcript tools absent from the hook roster.

The SessionEnd command reads the transcript supplied by Claude Code, including
when that payload belongs to a subagent. A tool enters the population only when
its ``tool_use`` input carries a text ``command`` field, which is the field the
two repository command hooks consume. The roster is
``tracker_publish_hook.COMMAND_TOOLS`` rather than a second hand-kept list.

A complete read exits 0. An unreadable input or an unregistered tool exits 2
and writes a counts-free finding to stderr. SessionEnd cannot prevent session
termination, so that status reports the gap to the user without claiming that
the publication was prevented. The complete boundary belongs to
``command_tool_roster.DECLARED_LIMITS``.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys

from console_codec import require_python_floor, use_utf8
import tracker_publish_hook


DECLARED_LIMITS = (
    (
        "a command tool omitted from the transcript is invisible",
        "The detector can compare only tool calls serialized in the supplied "
        "transcript; a call absent from that file cannot enter its roster population.",
    ),
    (
        "a disabled or overridden SessionEnd hook produces no roster report",
        "A session that does not run the repository SessionEnd registration ends "
        "without this detector reading its transcript.",
    ),
)
NOT_REACHED = tuple(reason for _subject, reason in DECLARED_LIMITS)


@dataclass(frozen=True)
class Scan:
    command_tools: tuple[str, ...]
    unregistered: tuple[str, ...]


def scan_transcript(path: Path) -> Scan:
    """Read one Claude transcript and compare command tools with the roster."""
    command_tools: set[str] = set()
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
        if not isinstance(row, dict) or row.get("type") != "assistant":
            continue
        message = row.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            tool_input = block.get("input")
            name = block.get("name")
            if (
                isinstance(name, str)
                and isinstance(tool_input, dict)
                and isinstance(tool_input.get("command"), str)
            ):
                command_tools.add(name)
    ordered = tuple(sorted(command_tools))
    return Scan(
        command_tools=ordered,
        unregistered=tuple(
            name for name in ordered if name not in tracker_publish_hook.COMMAND_TOOLS
        ),
    )


def session_end(payload: object) -> Scan:
    """Read the transcript named by one SessionEnd payload."""
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "SessionEnd":
        raise ValueError("input is not a SessionEnd payload")
    transcript = payload.get("transcript_path")
    if not isinstance(transcript, str):
        raise ValueError("SessionEnd payload has no transcript path")
    return scan_transcript(Path(transcript))


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments != ["--session-end"]:
        print("command-tool roster: NOT CHECKED -- unsupported arguments", file=sys.stderr)
        return 2
    try:
        scan = session_end(json.load(sys.stdin))
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(
            "command-tool roster: NOT CHECKED -- " + str(exc),
            file=sys.stderr,
        )
        return 2
    if scan.unregistered:
        print(
            "command-tool roster: INCOMPLETE -- unregistered command tools: "
            + ", ".join(scan.unregistered)
            + "; publication was not prevented for any unregistered tool",
            file=sys.stderr,
        )
        return 2
    print(
        "command-tool roster: complete -- observed command tools: "
        + (", ".join(scan.command_tools) if scan.command_tools else "none")
    )
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
