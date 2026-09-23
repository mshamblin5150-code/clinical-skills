"""Contract tests for the one-question grilling Stop hook. #1392."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import grilling_stop_hook as hook
from prose_bind import NAMING, bind


FORMAT = "one-question format\n"


def command_record(command: str) -> dict[str, object]:
    path_match = hook.SKILL_PATH.search(command)
    return {
        "type": "event_msg",
        "payload": {
            "type": "item_completed",
            "item": {
                "type": "CommandExecution",
                "command": ["pwsh", "-Command", command],
                "parsed_cmd": (
                    [{"type": "read", "path": path_match.group(0).lstrip("/\\")}]
                    if path_match
                    else [{"type": "unknown", "cmd": command}]
                ),
                "status": "completed",
            },
        },
    }


def assistant_record(message: str) -> dict[str, object]:
    return {
        "type": "response_item",
        "payload": {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": message}],
            "phase": "final_answer",
        },
    }


class HookContract(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.transcript = self.root / "session.jsonl"
        self.format_path = self.root / "grilling.md"
        self.agents_path = self.root / "AGENTS.md"
        self.format_path.write_text(FORMAT, encoding="utf-8")
        self.agents_path.write_text(
            hook.marked_block(FORMAT), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_transcript(self, *records: dict[str, object]) -> None:
        self.transcript.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )

    def grade(
        self, message: str, *, records: tuple[dict[str, object], ...] | None = None,
        stop_hook_active: bool = False,
    ) -> dict[str, object]:
        if records is None:
            records = (command_record("Get-Content C:/skills/grilling/SKILL.md"),)
        self.write_transcript(*records)
        return hook.handle(
            {
                "last_assistant_message": message,
                "stop_hook_active": stop_hook_active,
                "transcript_path": str(self.transcript),
            },
            format_path=self.format_path,
            agents_path=self.agents_path,
        )

    def assert_blocked(self, message: str) -> None:
        result = self.grade(message)
        self.assertEqual(result["decision"], "block")
        self.assertIn("retract", result["reason"].lower())
        self.assertIn("one question", result["reason"].lower())

    def test_the_2026_09_13_four_label_shape_is_blocked(self) -> None:
        self.assert_blocked(
            "# Grilling round 1\n\nQ1 First decision?\nQ2 Second decision?\n"
            "Q3 Third decision?\nQ4 Fourth decision?"
        )

    def test_two_emoji_questions_are_blocked(self) -> None:
        self.assert_blocked(
            "❓ First?\n➡️ Choose A.\nHeld for later: second.\n"
            "❓ Second?\n➡️ Choose B.\nHeld for later: nothing."
        )

    def test_a_question_requires_a_recommendation_and_held_line(self) -> None:
        self.assert_blocked("❓ Choose A or B?\nHeld for later: nothing.")
        self.assert_blocked("❓ Choose A or B?\n➡️ Choose A because it is safer.")

    def test_several_question_marks_inside_one_question_block_pass(self) -> None:
        result = self.grade(
            "Why this matters: the choice fixes the public contract.\n\n"
            "❓ Should this be A? If not, should it be B? Which cost is acceptable?\n\n"
            "A. A — costs one migration.\nB. B — costs one compatibility layer.\n\n"
            "➡️ Choose A because it keeps one source of truth.\n\n"
            "Held for later: naming."
        )

        self.assertNotEqual(result.get("decision"), "block")

    def test_a_reply_with_no_question_passes(self) -> None:
        self.assertNotEqual(
            self.grade("I incorporated the ruling and am checking the next frontier.").get(
                "decision"
            ),
            "block",
        )

    def test_a_lead_in_question_is_blocked_but_quoted_and_code_questions_pass(self) -> None:
        self.assert_blocked(
            "Is this the decision we need?\n❓ Choose A or B?\n"
            "➡️ Choose A because it is bounded.\nHeld for later: nothing."
        )

        for lead_in in (
            'The clinician asked "is this hard for you?" before ruling.',
            "The literal text is `is this hard for you?`.",
            "> Is this hard for you?\nThe answer was no.",
        ):
            with self.subTest(lead_in=lead_in):
                result = self.grade(
                    f"{lead_in}\n❓ Choose A or B?\n"
                    "➡️ Choose A because it is bounded.\nHeld for later: nothing."
                )
                self.assertNotEqual(result.get("decision"), "block")

    def test_a_session_without_a_grilling_skill_load_exits_without_grading(self) -> None:
        result = self.grade(
            "Q1 First?\nQ2 Second?",
            records=(command_record("Get-Content C:/skills/implement/SKILL.md"),),
        )

        self.assertEqual(result, {})

    def test_mentioning_a_skill_path_without_opening_it_does_not_activate(self) -> None:
        mention = command_record(
            "Write-Output 'C:/skills/grilling/SKILL.md is the documented path'"
        )
        mention["payload"]["item"]["parsed_cmd"] = [
            {"type": "unknown", "cmd": "Write-Output"}
        ]

        self.assertEqual(self.grade("Q1 First?\nQ2 Second?", records=(mention,)), {})

    def test_a_failed_skill_read_does_not_activate(self) -> None:
        failed = command_record("Get-Content C:/skills/grilling/SKILL.md")
        failed["payload"]["item"]["status"] = "failed"

        self.assertEqual(self.grade("Q1 First?\nQ2 Second?", records=(failed,)), {})

    def test_closing_ends_grading_and_reloading_restarts_it(self) -> None:
        closed = (
            command_record("Get-Content C:/skills/grill-with-docs/SKILL.md"),
            assistant_record(hook.CLOSING_LINE),
        )
        self.assertEqual(self.grade("Merge?", records=closed), {})

        reopened = closed + (
            command_record("Get-Content C:/skills/grill-me/SKILL.md"),
        )
        result = self.grade("Merge?", records=reopened)
        self.assertEqual(result["decision"], "block")

    def test_the_closing_reply_itself_passes(self) -> None:
        result = self.grade(
            "No questions remain.\n\n" + hook.CLOSING_LINE
        )

        self.assertNotEqual(result.get("decision"), "block")

    def test_apostrophes_do_not_hide_an_outside_question(self) -> None:
        self.assert_blocked(
            "It's settled? That's surprising.\n❓ Choose A or B?\n"
            "➡️ Choose A because it is bounded.\nHeld for later: nothing."
        )

    def test_stop_hook_retry_exits_without_grading(self) -> None:
        self.assertEqual(
            self.grade("Q1 First?\nQ2 Second?", stop_hook_active=True), {}
        )

    def test_a_stale_installed_block_is_reported(self) -> None:
        self.agents_path.write_text(
            hook.marked_block("old format\n"), encoding="utf-8"
        )

        result = self.grade("No question in this reply.")

        self.assertIn("systemMessage", result)
        self.assertIn("stale", str(result["systemMessage"]).lower())

    def test_claude_points_at_the_hook_limits_without_copying_them(self) -> None:
        claude = (Path(__file__).resolve().parents[1] / "CLAUDE.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual((), bind(hook.DECLARED_LIMITS, claude, mode=NAMING))


if __name__ == "__main__":
    unittest.main()
