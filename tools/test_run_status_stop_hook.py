"""Public-contract tests for the approved-run Stop hook. #1398."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import run_status_stop_hook as hook


def command_record(run: Path) -> dict[str, object]:
    return {
        "type": "event_msg",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "CommandExecution",
                "command": ["python", "tool.py", str(run)],
                "parsed_cmd": [{"type": "read", "path": str(run / "bar.md")}],
                "status": "completed",
            },
        },
    }


def claude_assistant_record(message: str) -> dict[str, object]:
    return {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": message}],
        },
    }


class RunStatusContract(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run = self.root / "scratch" / "runs" / "nur-5042-module-5-course-assignment"
        self.run.mkdir(parents=True)
        self.artifact = self.root / "assignment.pptx"
        self.artifact.write_bytes(b"approved deck")
        (self.run / "submission-gates.json").write_text(
            json.dumps(
                {
                    "artifact": self.artifact.name,
                    "artifact_path": str(self.artifact),
                    "gate1_approved": True,
                    "approval_revision": 1,
                    "upload_route": "awaiting-upload",
                }
            ),
            encoding="utf-8",
        )
        self.transcript = self.root / "session.jsonl"
        self.transcript.write_text(json.dumps(command_record(self.run)) + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def grade(self, message: str) -> dict[str, object]:
        return hook.handle(
            {
                "last_assistant_message": message,
                "transcript_path": str(self.transcript),
                "stop_hook_active": False,
            }
        )

    def test_missing_status_line_is_retracted(self) -> None:
        result = self.grade("The deck is ready for your upload.")

        self.assertEqual("block", result["decision"])
        self.assertIn("Run status:", result["reason"])

    def test_awaiting_upload_is_accepted_after_approval(self) -> None:
        self.assertEqual(
            {},
            self.grade("The deck is ready.\n\nRun status: awaiting upload"),
        )

    def test_claude_reads_the_last_assistant_message_from_its_transcript(self) -> None:
        message = "The deck is ready.\n\nRun status: awaiting upload"
        self.transcript.write_text(
            json.dumps(command_record(self.run))
            + "\n"
            + json.dumps(claude_assistant_record(message))
            + "\n",
            encoding="utf-8",
        )

        self.assertEqual(
            {},
            hook.handle(
                {
                    "transcript_path": str(self.transcript),
                    "stop_hook_active": False,
                }
            ),
        )

    def test_early_complete_is_retracted(self) -> None:
        with mock.patch.object(hook, "completion_is_clean", return_value=False):
            result = self.grade("Submitted.\n\nRun status: complete")

        self.assertEqual("block", result["decision"])
        self.assertIn("terminal grade", result["reason"])

    def test_clean_completion_closes_the_run_for_later_replies(self) -> None:
        with mock.patch.object(hook, "completion_is_clean", return_value=True):
            self.assertEqual({}, self.grade("Done.\n\nRun status: complete"))

        self.assertEqual({}, self.grade("A later reply about another subject."))

    def test_reasonless_stopped_is_retracted(self) -> None:
        result = self.grade("I stopped here.\n\nRun status: stopped -")

        self.assertEqual("block", result["decision"])
        self.assertIn("reason", result["reason"])

    def test_a_stopped_run_stays_stopped_until_another_approval(self) -> None:
        self.assertEqual(
            {},
            self.grade("The posted file differs.\n\nRun status: stopped - posted file differs"),
        )

        result = self.grade("I am checking it.\n\nRun status: awaiting posted reading")
        self.assertEqual("block", result["decision"])
        self.assertIn("stays stopped", result["reason"])

        record = json.loads((self.run / "submission-gates.json").read_text(encoding="utf-8"))
        record["approval_revision"] = 2
        (self.run / "submission-gates.json").write_text(json.dumps(record), encoding="utf-8")
        self.assertEqual(
            {},
            self.grade("The revision is approved.\n\nRun status: awaiting upload"),
        )

    def test_the_claude_stop_registration_uses_the_same_hook(self) -> None:
        settings = json.loads(
            (Path(__file__).resolve().parents[1] / ".claude" / "settings.json").read_text(
                encoding="utf-8"
            )
        )
        commands = [
            handler["command"]
            for registration in settings["hooks"]["Stop"]
            for handler in registration["hooks"]
        ]

        self.assertTrue(any("run_status_stop_hook.py" in command for command in commands))

    def test_a_new_skill_row_is_discoverable_without_editing_the_path_matcher(self) -> None:
        other = self.root / "scratch" / "runs" / "course-module-other-submission"
        other.mkdir(parents=True)
        record = other / "approval.json"
        record.write_text('{"gate1_approved": true}', encoding="utf-8")
        spec = hook.RunKind(
            skill="other-submission",
            directory_suffix="-other-submission",
            approval_record=record.name,
            completion_command="other_scan.py",
        )

        with mock.patch.object(hook, "RUN_KINDS", (spec,)):
            self.assertEqual(
                ((other.resolve(), spec),), hook.touched_runs((command_record(other),))
            )


if __name__ == "__main__":
    unittest.main()
