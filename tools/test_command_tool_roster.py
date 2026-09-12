"""Public-contract tests for the SessionEnd command-tool roster detector."""

from __future__ import annotations

import json
import io
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import command_tool_roster as roster
from prose_bind import NAMING, bind


def tool_call(name: str, tool_input: object) -> dict[str, object]:
    return {
        "type": "assistant",
        "message": {
            "content": [
                {
                    "type": "tool_use",
                    "id": f"tool-{name}",
                    "name": name,
                    "input": tool_input,
                }
            ]
        },
    }


def write_transcript(path: Path, *rows: dict[str, object]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
    )


def invoke_main(arguments: list[str], stdin: str) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with (
        mock.patch("sys.stdin", io.StringIO(stdin)),
        redirect_stdout(stdout),
        redirect_stderr(stderr),
    ):
        status = roster.main(arguments)
    return status, stdout.getvalue(), stderr.getvalue()


class TranscriptRoster(unittest.TestCase):
    def test_only_tools_carrying_a_command_field_enter_the_population(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session.jsonl"
            write_transcript(
                transcript,
                tool_call("Bash", {"command": "echo ready"}),
                tool_call("Read", {"file_path": "README.md"}),
            )

            scan = roster.scan_transcript(transcript)

        self.assertEqual(scan.command_tools, ("Bash",))
        self.assertEqual(scan.unregistered, ())

    def test_an_unknown_command_tool_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session.jsonl"
            write_transcript(
                transcript,
                tool_call("Bash", {"command": "echo ready"}),
                tool_call("FutureShell", {"command": "publish"}),
            )

            scan = roster.scan_transcript(transcript)

        self.assertEqual(scan.command_tools, ("Bash", "FutureShell"))
        self.assertEqual(scan.unregistered, ("FutureShell",))

    def test_session_end_surfaces_an_unregistered_tool_without_preventing_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session.jsonl"
            write_transcript(
                transcript,
                tool_call("FutureShell", {"command": "publish"}),
            )
            payload = json.dumps(
                {
                    "hook_event_name": "SessionEnd",
                    "transcript_path": str(transcript),
                    "session_id": "session-1",
                    "reason": "other",
                }
            )

            status, stdout, stderr = invoke_main(["--session-end"], payload)

        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertIn("command-tool roster: INCOMPLETE", stderr)
        self.assertIn("FutureShell", stderr)
        self.assertIn("publication was not prevented", stderr)

    def test_session_end_records_a_complete_roster_in_the_debug_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session.jsonl"
            write_transcript(
                transcript,
                tool_call("PowerShell", {"command": "Get-ChildItem"}),
                tool_call("Monitor", {"command": "while true; do break; done"}),
            )
            payload = json.dumps(
                {
                    "hook_event_name": "SessionEnd",
                    "transcript_path": str(transcript),
                }
            )

            status, stdout, stderr = invoke_main(["--session-end"], payload)

        self.assertEqual(status, 0)
        self.assertIn("command-tool roster: complete", stdout)
        self.assertIn("Monitor, PowerShell", stdout)
        self.assertEqual(stderr, "")

    def test_a_subagent_session_is_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "subagent.jsonl"
            write_transcript(
                transcript,
                tool_call("FutureShell", {"command": "publish"}),
            )

            scan = roster.session_end(
                {
                    "hook_event_name": "SessionEnd",
                    "agent_id": "agent-1",
                    "transcript_path": str(transcript),
                }
            )

        self.assertEqual(scan.unregistered, ("FutureShell",))


class ProjectRegistration(unittest.TestCase):
    def test_the_declared_limits_are_owned_and_named_without_a_second_copy(self) -> None:
        self.assertEqual(
            (), bind(roster.DECLARED_LIMITS, roster.__doc__ or "", mode=NAMING)
        )

    def test_the_roster_and_both_command_hooks_name_the_same_tools(self) -> None:
        root = Path(__file__).resolve().parents[1]
        settings = json.loads(
            (root / ".claude" / "settings.json").read_text(encoding="utf-8")
        )

        for event in ("PreToolUse", "PostToolUse"):
            with self.subTest(event=event):
                self.assertEqual(
                    {row["matcher"] for row in settings["hooks"][event]},
                    set(roster.tracker_publish_hook.COMMAND_TOOLS),
                )

    def test_roster_detection_is_a_second_session_end_module(self) -> None:
        root = Path(__file__).resolve().parents[1]
        settings = json.loads(
            (root / ".claude" / "settings.json").read_text(encoding="utf-8")
        )
        commands = [
            handler["command"]
            for registration in settings["hooks"]["SessionEnd"]
            for handler in registration["hooks"]
        ]

        self.assertEqual(len(commands), 2)
        self.assertTrue(any("aar_scan.py" in command for command in commands))
        self.assertTrue(
            any("command_tool_roster.py" in command for command in commands)
        )


if __name__ == "__main__":
    unittest.main()
