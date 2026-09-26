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

    def test_awaiting_posting_is_accepted_after_approval(self) -> None:
        self.assertEqual(
            {},
            self.grade(
                f"The deck is ready.\n\nRun status: {self.run.name} — awaiting posting"
            ),
        )

    def test_claude_reads_the_last_assistant_message_from_its_transcript(self) -> None:
        message = f"The deck is ready.\n\nRun status: {self.run.name} — awaiting posting"
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
            result = self.grade(
                f"Submitted.\n\nRun status: {self.run.name} — complete"
            )

        self.assertEqual("block", result["decision"])
        self.assertIn("terminal grade", result["reason"])

    def test_clean_completion_closes_the_run_for_later_replies(self) -> None:
        with mock.patch.object(hook, "completion_is_clean", return_value=True):
            self.assertEqual(
                {}, self.grade(f"Done.\n\nRun status: {self.run.name} — complete")
            )

        self.assertEqual({}, self.grade("A later reply about another subject."))

    def test_reasonless_stopped_is_retracted(self) -> None:
        result = self.grade(
            f"I stopped here.\n\nRun status: {self.run.name} — stopped -"
        )

        self.assertEqual("block", result["decision"])
        self.assertIn("reason", result["reason"])

    def test_a_stopped_run_stays_stopped_until_another_approval(self) -> None:
        self.assertEqual(
            {},
            self.grade(
                f"The posted file differs.\n\nRun status: {self.run.name} — stopped - posted file differs"
            ),
        )

        result = self.grade(
            f"I am checking it.\n\nRun status: {self.run.name} — awaiting posted reading"
        )
        self.assertEqual("block", result["decision"])
        self.assertIn("stays stopped", result["reason"])

        record = json.loads((self.run / "submission-gates.json").read_text(encoding="utf-8"))
        record["approval_revision"] = 2
        (self.run / "submission-gates.json").write_text(json.dumps(record), encoding="utf-8")
        self.assertEqual(
            {},
            self.grade(
                f"The revision is approved.\n\nRun status: {self.run.name} — awaiting posting"
            ),
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

    def test_a_new_skill_row_is_discoverable_from_the_approval_record(self) -> None:
        other = self.root / "scratch" / "runs" / "course-module-other-submission"
        other.mkdir(parents=True)
        record = other / "approval.json"
        item = {
            "skill": "other-submission",
            "submission": "one",
            "sha256": "0" * 64,
            "sources": [str(self.artifact)],
            "grader_args": [str(other)],
            "posting_route": "awaiting-posting",
            "approval_revision": 1,
            "pregrade_status": "clean",
        }
        record.write_text(
            json.dumps({"version": 1, "approval_revision": 1, "items": [item]}),
            encoding="utf-8",
        )
        spec = hook.RunKind(
            skill="other-submission",
            approval_record=record.name,
            completion_command="other_scan.py",
        )

        with mock.patch.object(hook, "RUN_KIND_BY_SKILL", {spec.skill: spec}):
            self.assertEqual(
                ((spec, item),),
                hook.approvals(other.resolve()),
            )

    def test_a_malformed_posting_item_opens_no_run(self) -> None:
        run = self.root / "scratch" / "runs" / "malformed-discussion"
        run.mkdir(parents=True)
        (run / "posting-approvals.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "approval_revision": 1,
                    "items": [
                        {
                            "skill": "discussion-post",
                            "submission": "post",
                            "grader_args": [str(run)],
                            "approval_revision": 1,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.transcript.write_text(
            json.dumps(command_record(run)) + "\n", encoding="utf-8"
        )

        self.assertEqual({}, self.grade("The record is incomplete."))

    def test_each_posting_skill_opens_from_its_record_and_retracts_early_complete(self) -> None:
        for skill in (
            "discussion-post",
            "discussion-reply",
            "peer-critique",
            "practicum-case-study",
            "clinical-note",
            "batch-shift",
        ):
            with self.subTest(skill=skill):
                run = self.root / "scratch" / "runs" / f"key-{skill}"
                run.mkdir(parents=True)
                artifact = run / "approved.md"
                artifact.write_text("approved\n", encoding="utf-8")
                (run / "posting-approvals.json").write_text(
                    json.dumps(
                        {
                            "version": 1,
                            "approval_revision": 1,
                            "items": [
                                {
                                    "skill": skill,
                                    "submission": "submission-key",
                                    "sha256": "0" * 64,
                                    "sources": [str(artifact)],
                                    "grader_args": [str(run)],
                                    "posting_route": "awaiting-posting",
                                    "approval_revision": 1,
                                    "pregrade_status": "clean",
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                self.transcript.write_text(
                    json.dumps(command_record(run)) + "\n", encoding="utf-8"
                )
                with mock.patch.object(hook, "completion_is_clean", return_value=False):
                    result = self.grade(
                        f"Done.\n\nRun status: {run.name} — complete"
                    )
                self.assertEqual("block", result["decision"])
                self.assertIn("terminal grade", result["reason"])

    def test_two_touched_approved_runs_each_need_their_own_keyed_line(self) -> None:
        other = self.root / "scratch" / "runs" / "nur-5042-module-6-course-assignment"
        other.mkdir(parents=True)
        other_artifact = self.root / "assignment-2.pptx"
        other_artifact.write_bytes(b"approved deck two")
        (other / "submission-gates.json").write_text(
            json.dumps(
                {
                    "artifact": other_artifact.name,
                    "artifact_path": str(other_artifact),
                    "gate1_approved": True,
                    "approval_revision": 1,
                    "upload_route": "awaiting-upload",
                }
            ),
            encoding="utf-8",
        )
        self.transcript.write_text(
            json.dumps(command_record(self.run))
            + "\n"
            + json.dumps(command_record(other))
            + "\n",
            encoding="utf-8",
        )

        result = self.grade(
            f"Both are ready.\n\nRun status: {other.name} — awaiting posting"
        )
        self.assertEqual("block", result["decision"])

        self.assertEqual(
            {},
            self.grade(
                "Both are ready.\n\n"
                f"Run status: {self.run.name} — awaiting posting\n"
                f"Run status: {other.name} — awaiting posting"
            ),
        )

    def test_two_reply_run_stays_open_while_one_approved_reply_is_unposted(self) -> None:
        run = self.root / "scratch" / "runs" / "nur-5042-module-7-discussion"
        run.mkdir(parents=True)
        (run / "posting-approvals.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "approval_revision": 2,
                    "items": [
                        {
                            "skill": "discussion-reply",
                            "submission": f"response-{number}.md",
                            "sha256": "0" * 64,
                            "sources": [str(run / f"response-{number}.md")],
                            "grader_args": [str(run)],
                            "posting_route": "awaiting-posting",
                            "approval_revision": number,
                            "pregrade_status": "clean",
                        }
                        for number in (1, 2)
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.transcript.write_text(
            json.dumps(command_record(run)) + "\n", encoding="utf-8"
        )

        with mock.patch.object(
            hook, "completion_is_clean", side_effect=(True, False)
        ):
            result = self.grade(f"Done.\n\nRun status: {run.name} — complete")

        self.assertEqual("block", result["decision"])
        self.assertIn("every approved item", result["reason"])

    def test_a_code_lookup_with_no_approval_record_opens_nothing(self) -> None:
        lookup = self.root / "scratch" / "runs" / "code-lookup"
        lookup.mkdir(parents=True)
        self.transcript.write_text(
            json.dumps(command_record(lookup)) + "\n", encoding="utf-8"
        )

        self.assertEqual({}, self.grade("The requested code was located."))


if __name__ == "__main__":
    unittest.main()
