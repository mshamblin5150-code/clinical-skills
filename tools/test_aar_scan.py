"""Contract tests for the submission-keyed after-action review. #814."""

# phi-scan: synthetic

from __future__ import annotations

import io
import importlib
import ast
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import artifact_lock_test_support  # noqa: F401

import aar_scan
import checks_ledger
import differential_scan
import discussion_post_scan
import discussion_reply_scan
import filled_vitals_census
import grader_conformance
import imagery_proposals
import specificity_scan
import voice_model_identity
import voice_read
import project_context


GraderConformance = grader_conformance.for_module(aar_scan)


class CheckTargetGitState(Enum):
    UNTRACKED = "untracked"
    UNCHANGED = "unchanged"
    UNSTAGED = "unstaged"
    STAGED = "staged"
    COMMITTED = "committed"


class CorrectionDisposition(Enum):
    MEMORY_WRITE = "memory-write"
    CHECK = "check"


@dataclass(frozen=True)
class CorrectionRecord:
    event: str
    disposition: CorrectionDisposition
    target: Path
    landing: str


def empty_population_input(root: Path) -> grader_conformance.EmptyPopulationInput:
    run = root / "run"
    run.mkdir()
    return grader_conformance.EmptyPopulationInput(
        (str(run), "--submission", "synthetic-submission"),
        population_size=lambda result: result.population,
    )


class DeclaredLimitsAreBound(unittest.TestCase):
    def test_the_test_suite_names_the_declared_limits_object(self):
        self.assertTrue(aar_scan.DECLARED_LIMITS)
        self.assertEqual(
            tuple(reason for _subject, reason in aar_scan.DECLARED_LIMITS),
            aar_scan.NOT_REACHED,
        )


def row(kind: str, uuid: str, message: object, **extra: object) -> dict[str, object]:
    return {
        "type": kind,
        "uuid": uuid,
        "sessionId": "session-1",
        "message": message,
        **extra,
    }


def write_transcript(path: Path, run: Path | None = None) -> None:
    command = "echo ready" if run is None else f'python tools/discussion_post_scan.py "{run}"'
    rows = [
        row(
            "user",
            "u1",
            {"content": "That is the wrong section; use the nurse practitioner section."},
            attributionSkill="discussion-post",
        ),
        row(
            "assistant",
            "a1",
            {
                "content": [
                    {"type": "text", "text": "You are right. I corrected the citation."},
                    {
                        "type": "tool_use",
                        "id": "tool-1",
                        "name": "Bash",
                        "input": {"command": command},
                    },
                ]
            },
            attributionSkill="discussion-post",
        ),
        row(
            "user",
            "u2",
            {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool-1",
                        "content": "patient-bearing output that must be dropped",
                        "is_error": False,
                    }
                ]
            },
            attributionSkill="discussion-post",
        ),
    ]
    path.write_text("\n".join(json.dumps(item) for item in rows) + "\n", encoding="utf-8")


def codex_row(payload: object, **extra: object) -> dict[str, object]:
    return {"type": "response_item", "payload": payload, **extra}


def write_codex_transcript(path: Path, run: Path | None = None) -> None:
    command = "echo ready" if run is None else f'python tools/discussion_post_scan.py "{run}"'
    rows = [
        codex_row(
            {
                "type": "message",
                "id": "u1",
                "role": "user",
                "content": [{"type": "input_text", "text": "That is the wrong section."}],
            }
        ),
        codex_row(
            {
                "type": "message",
                "id": "a1",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "I corrected the citation."}],
            }
        ),
        codex_row(
            {
                "type": "custom_tool_call",
                "id": "call-item-1",
                "call_id": "call-1",
                "name": "exec",
                "input": json.dumps({"cmd": command}),
                "status": "completed",
            }
        ),
        codex_row(
            {
                "type": "custom_tool_call_output",
                "id": "output-1",
                "call_id": "call-1",
                "output": [{"type": "input_text", "text": "patient-bearing output"}],
            }
        ),
        codex_row(
            {
                "type": "agent_message",
                "id": "agent-1",
                "author": "/root/checker",
                "recipient": "/root",
                "content": [{"type": "input_text", "text": "The checker found one mismatch."}],
            }
        ),
        codex_row(
            {
                "type": "message",
                "id": "developer-1",
                "role": "developer",
                "content": [{"type": "input_text", "text": "private developer instruction"}],
            }
        ),
        {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "item": {"type": "UserMessage", "id": "u1", "content": [{"type": "text", "text": "That is the wrong section."}]},
            },
        },
    ]
    path.write_text("\n".join(json.dumps(item) for item in rows) + "\n", encoding="utf-8")


class GithubPublicationEvidence(unittest.TestCase):
    def test_a_successful_codex_command_execution_proves_the_gh_call(self):
        with tempfile.TemporaryDirectory() as temp:
            transcript = Path(temp) / "codex.jsonl"
            event = {
                "type": "event_msg",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "CommandExecution",
                        "command": ["pwsh", "-Command", "gh issue create --title follow-up"],
                        "status": "completed",
                        "exit_code": 0,
                    },
                },
            }
            transcript.write_text(json.dumps(event) + "\n", encoding="utf-8")

            self.assertTrue(aar_scan._successful_gh_call((transcript,)))


def invoke_main(arguments: list[str], stdin: str | None = None) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    original_stdin = aar_scan.sys.stdin
    if stdin is not None:
        aar_scan.sys.stdin = io.StringIO(stdin)
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = aar_scan.main(arguments)
    finally:
        aar_scan.sys.stdin = original_stdin
    return status, stdout.getvalue(), stderr.getvalue()


class CommandModes(unittest.TestCase):
    """The three command modes whose routing #840 migrated."""

    def test_the_graded_mode_prints_the_report_and_returns_its_finding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()

            status, stdout, stderr = invoke_main(
                [str(run), "--submission", "post-1"]
            )

        self.assertEqual(status, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(
            stdout,
            "after-action review over run\n\n"
            "  review records                  0\n"
            "  candidate population            0\n"
            "  correction records              0\n"
            "  sustain records                 0\n"
            "  unread candidates               0\n"
            "  transcripts found               0\n"
            "  transcripts skipped by time     0\n"
            "  transcripts skipped by bytes    0\n"
            "  transcripts read                0\n"
            "  sittings begun after extract    0\n"
            "  unowned browser page actions    0 (reported, not graded)\n"
            "  tab creation parses: tabs_create_mcp  0\n"
            "  tab creation parses: tabs_context_mcp 0\n"
            "  tab creation parses: navigate no tab  0\n"
            "  findings                        1\n\n"
            "  declared limits:\n"
            "    semantic classification\n"
            "    tool-result-only correction\n"
            "    uncorrected error\n"
            "    orchestrator veto\n"
            "    subagent silence\n"
            "    transcript flush\n"
            "    run-key discovery\n"
            "    subagent launch-result drift\n"
            "    correction kind misplacement\n"
            "    browser tab ownership\n",
        )

    def test_the_extract_mode_writes_and_reports_its_private_packet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            run.mkdir()
            transcript = root / "session-1.jsonl"
            write_transcript(transcript)
            memory = root / "memory" / "MEMORY.md"
            memory.parent.mkdir()
            memory.write_text("# Index\n", encoding="utf-8")
            (run / "reread.md").write_text(
                "## REREAD: post-1\n"
                "POST-URL: https://example.org/submissions/1\n"
                "POSTED: 2026-09-13T12:00:00Z\n"
                "READ: 2026-09-13\n"
                "VERDICT: matches - the posted artifact was read back\n",
                encoding="utf-8",
            )

            status, stdout, stderr = invoke_main(
                [
                    str(run),
                    "--submission", "post-1",
                    "--transcript", str(transcript),
                    "--memory-index", str(memory),
                    "--extract",
                ]
            )

            self.assertTrue(aar_scan.extract_path(run, "post-1").is_file())
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(
            stdout,
            "after-action review extract over run\n"
            "  candidate population            4\n"
            "  transcripts found               1\n"
            "  transcripts skipped by time     0\n"
            "  transcripts skipped by bytes    0\n"
            "  transcripts read                1\n"
            "  private extract written         post-1.extract.md\n",
        )

    def test_a_refused_review_open_is_a_finding_without_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "alias-parent").mkdir()
            # Drive an unresolved spelling on every platform. Windows CI's
            # short temporary-directory alias exposed this same mismatch.
            run = root / "alias-parent" / ".." / "run"
            (run / "aar").mkdir(parents=True)
            review = aar_scan.review_path(run, "post-1")
            review.write_text("# AFTER-ACTION REVIEW\n", encoding="utf-8")
            original = Path.read_text

            def refusing(path: Path, *args: object, **kwargs: object) -> str:
                if path.resolve() == review.resolve():
                    raise PermissionError(13, "denied", str(review))
                return original(path, *args, **kwargs)

            with mock.patch.object(Path, "read_text", refusing):
                status, stdout, stderr = invoke_main(
                    [str(run), "--submission", "post-1", "--show"]
                )

        self.assertEqual((status, stderr), (1, ""))
        self.assertIn("unscannable-review: cannot read review", stdout)

    def test_the_runner_refuses_unknown_flags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            status, _stdout, stderr = invoke_main(
                [str(run), "--submission", "post-1", "--unknown"]
            )
        self.assertEqual(status, 2)
        self.assertEqual(stderr, "unrecognized option --unknown\n")

    def test_the_runner_accepts_a_flag_first_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            status, stdout, stderr = invoke_main(
                ["--show", str(run), "--submission", "post-1"]
            )
        self.assertEqual((status, stderr), (1, ""))
        self.assertIn("after-action review over run", stdout)

    def test_the_runner_refuses_show_as_a_submission_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            status, stdout, stderr = invoke_main(
                [str(run), "--submission", "--show"]
            )
        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "--submission needs a key\n")


class ReductionByEntryShape(unittest.TestCase):
    def test_claude_user_rows_are_labeled_by_harness_envelope_and_flags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            rows = [
                row("user", "typed", {"content": "Please keep the assessment concise."}),
                row(
                    "user",
                    "notification",
                    {"content": "[SYSTEM NOTIFICATION — NOT USER INPUT]\n<task-notification>done</task-notification>"},
                ),
                row(
                    "user",
                    "skill",
                    {"content": "Base directory for this skill: C:\\skills\\aar\nInstructions"},
                    isMeta=True,
                ),
                row("user", "meta", {"content": "Harness resumed the task."}, isMeta=True),
                row(
                    "user",
                    "compact",
                    {"content": "Summary of the earlier context."},
                    isCompactSummary=True,
                ),
            ]
            transcript.write_text(
                "\n".join(json.dumps(item) for item in rows) + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [candidate.kind for candidate in candidates],
            [
                "clinician",
                "task-notification",
                "skill-prompt",
                "harness-meta",
                "compaction-summary",
            ],
        )
    def test_subagent_launch_acknowledgment_is_not_labeled_as_a_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            rows = [
                row(
                    "assistant",
                    "a1",
                    {
                        "content": [
                            {"type": "tool_use", "id": "agent-call", "name": "Agent", "input": {}}
                        ]
                    },
                ),
                row(
                    "user",
                    "launch",
                    {
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "agent-call",
                                "content": "Async agent launched successfully.\nagentId: agent-7",
                            }
                        ]
                    },
                ),
            ]
            transcript.write_text(
                "\n".join(json.dumps(item) for item in rows) + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [candidate.kind for candidate in candidates],
            ["tool-call", "subagent-launch", "tool-status"],
        )

    def test_attachment_task_notification_is_a_first_class_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            transcript.write_text(
                json.dumps(
                    {
                        "type": "attachment",
                        "uuid": "attachment-row",
                        "attachment": {
                            "type": "queued_command",
                            "commandMode": "task-notification",
                            "prompt": (
                                "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
                                "<task-notification><task-id>reader-9</task-id>"
                                "<result>Finished.</result></task-notification>"
                            ),
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [
                (candidate.identifier, candidate.kind, candidate.aliases)
                for candidate in candidates
            ],
            [("attachment-row", "task-notification", ("reader-9",))],
        )

    def test_assistant_and_queue_notification_envelopes_are_first_class_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            banner = (
                "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
                "<task-notification><task-id>reader-10</task-id>"
                "<result>Finished.</result></task-notification>"
            )
            transcript.write_text(
                "\n".join(
                    json.dumps(item)
                    for item in (
                        row(
                            "assistant",
                            "assistant-row",
                            {"content": [{"type": "text", "text": banner}]},
                        ),
                        {
                            "type": "queue-operation",
                            "uuid": "queue-row",
                            "operation": "enqueue",
                            "content": banner.replace("reader-10", "reader-11"),
                        },
                        {
                            "type": "queue-operation",
                            "uuid": "unknown-queue-row",
                            "operation": "enqueue",
                            "content": "<future-harness-event>Queued.</future-harness-event>",
                        },
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [
                (candidate.identifier, candidate.kind, candidate.aliases)
                for candidate in candidates
            ],
            [
                ("assistant-row#text-1", "task-notification", ("reader-10",)),
                ("queue-row", "task-notification", ("reader-11",)),
                ("unknown-queue-row", "harness-meta", ()),
            ],
        )

    def test_distinct_notifications_for_one_task_keep_their_own_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            notifications = tuple(
                (
                    "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
                    "<task-notification><task-id>reader-shared</task-id>"
                    f"<result>{result}</result></task-notification>"
                )
                for result in ("First update.", "Second update.")
            )
            transcript.write_text(
                "\n".join(
                    json.dumps(
                        row("user", f"notification-{index}", {"content": notification})
                    )
                    for index, notification in enumerate(notifications, 1)
                )
                + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [(candidate.identifier, candidate.aliases) for candidate in candidates],
            [
                ("notification-1", ("reader-shared",)),
                ("notification-2", ("reader-shared",)),
            ],
        )

    def test_keeps_conversation_and_status_but_drops_ordinary_result_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "session-1.jsonl"
            write_transcript(transcript)

            candidates = aar_scan.reduce_transcript(transcript)
            joined = "\n".join(row.text for row in candidates)

            self.assertIn("wrong section", joined)
            self.assertIn("I corrected", joined)
            self.assertIn("Bash", joined)
            self.assertIn("completed", joined)
            self.assertNotIn("patient-bearing", joined)

    def test_keeps_a_short_human_correction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "short.jsonl"
            transcript.write_text(
                json.dumps(row("user", "u1", {"content": "agree"})) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(aar_scan.reduce_transcript(transcript)[0].text, "agree")

    def test_codex_keeps_conversation_tools_and_agent_results_without_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "rollout.jsonl"
            write_codex_transcript(transcript)

            candidates = aar_scan.reduce_transcript(transcript)
            joined = "\n".join(candidate.text for candidate in candidates)

            self.assertEqual(
                [candidate.kind for candidate in candidates],
                ["clinician", "assistant", "tool-call", "tool-status", "subagent-result"],
            )
            self.assertEqual(joined.count("That is the wrong section."), 1)
            self.assertIn("exec: completed", joined)
            self.assertIn("The checker found one mismatch.", joined)
            self.assertNotIn("patient-bearing output", joined)
            self.assertNotIn("private developer instruction", joined)

    def test_codex_rows_without_payload_identifiers_are_named_by_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "rollout-main.jsonl"
            transcript.write_text(
                json.dumps(
                    codex_row(
                        {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "Keep the full identifier."}],
                        }
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            candidate = aar_scan.reduce_transcript(transcript)[0]

            self.assertEqual(candidate.identifier, "rollout-main#row-1")
            self.assertEqual(candidate.aliases, ("line-1",))

    def test_codex_labels_harness_envelopes_compaction_and_delegation_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "rollout.jsonl"
            rows = [
                codex_row(
                    {
                        "type": "message",
                        "id": "context-1",
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "<environment_context>private context</environment_context>"}
                        ],
                    }
                ),
                {
                    "type": "compacted",
                    "payload": {
                        "message": "Summary of the earlier context.",
                        "replacement_history": [],
                    },
                },
                {
                    "type": "inter_agent_communication_metadata",
                    "payload": {"trigger_turn": True},
                },
            ]
            transcript.write_text(
                "\n".join(json.dumps(item) for item in rows) + "\n",
                encoding="utf-8",
            )

            candidates = aar_scan.reduce_transcript(transcript)

        self.assertEqual(
            [candidate.kind for candidate in candidates],
            ["environment-context", "compaction-summary", "inter-agent-metadata"],
        )
        self.assertEqual(candidates[1].text, "Summary of the earlier context.")

    def test_codex_function_call_keeps_its_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript = Path(directory) / "rollout.jsonl"
            transcript.write_text(
                json.dumps(
                    codex_row(
                        {
                            "type": "function_call",
                            "id": "call-item-1",
                            "call_id": "call-1",
                            "namespace": "mcp__cua_repl",
                            "name": "js",
                            "arguments": "{}",
                        }
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            candidate = aar_scan.reduce_transcript(transcript)[0]

            self.assertEqual(candidate.text, "mcp__cua_repl.js")

    def test_codex_tool_input_discovers_the_run_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory) / "scratch"
            run = scratch / "runs" / "case-study"
            run.mkdir(parents=True)
            transcript = Path(directory) / "rollout.jsonl"
            write_codex_transcript(transcript, run)
            with mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=scratch):
                found = aar_scan.discover_run_directories(aar_scan.read_transcript(transcript))

            self.assertEqual(found, (run.resolve(),))

    def test_nested_codex_tool_code_discovers_an_escaped_windows_run_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory) / "scratch"
            run = scratch / "runs" / "case-study"
            run.mkdir(parents=True)
            transcript = Path(directory) / "rollout.jsonl"
            escaped = str(run).replace("\\", "\\\\")
            transcript.write_text(
                json.dumps(
                    codex_row(
                        {
                            "type": "custom_tool_call",
                            "id": "call-1",
                            "name": "exec",
                            "input": json.dumps(
                                {"code": f"const run = '{escaped}'; use(run);"}
                            ),
                        }
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            with mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=scratch):
                found = aar_scan.discover_run_directories(
                    aar_scan.read_transcript(transcript)
                )

            self.assertEqual(found, (run.resolve(),))


class EntryKindsAreBound(unittest.TestCase):
    def test_the_extractor_written_kind_backstop_is_one_exact_set(self) -> None:
        self.assertEqual(
            aar_scan.EXTRACTOR_WRITTEN_ENTRY_KINDS,
            {"tool-call", "subagent-launch", "inter-agent-metadata"},
        )

    def test_every_candidate_kind_is_literal_or_passes_the_declared_kind_guard(self) -> None:
        tree = ast.parse(Path(aar_scan.__file__).read_text(encoding="utf-8"))
        checked = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "Candidate" or len(node.args) < 3:
                continue
            checked += 1
            kind = node.args[2]
            if isinstance(kind, ast.Constant) and isinstance(kind.value, str):
                self.assertIn(kind.value, aar_scan.ENTRY_KINDS)
                continue
            self.assertIsInstance(kind, ast.Call)
            self.assertIsInstance(kind.func, ast.Name)
            self.assertEqual(kind.func.id, "_declared_entry_kind")
        self.assertGreater(checked, 0)

    def test_the_envelope_table_and_envelope_kind_vocabulary_match_both_ways(self) -> None:
        self.assertEqual(
            set(aar_scan.ENVELOPE_KINDS.values()),
            set(aar_scan.ENVELOPE_ENTRY_KINDS),
        )
        self.assertLessEqual(
            set(aar_scan.ENVELOPE_ENTRY_KINDS),
            set(aar_scan.ENTRY_KINDS),
        )
        self.assertEqual(
            {
                aar_scan._envelope_kind(f"prefix <{tag}>body</{tag}>")
                for tag in aar_scan.ENVELOPE_KINDS
            },
            set(aar_scan.ENVELOPE_ENTRY_KINDS),
        )

    def test_the_measured_codex_row_type_vocabulary_is_declared(self) -> None:
        self.assertEqual(
            aar_scan.CODEX_ROW_TYPES,
            {
                "compacted",
                "event_msg",
                "inter_agent_communication_metadata",
                "response_item",
                "session_meta",
                "token_usage_record",
                "turn_context",
                "world_state",
            },
        )


class ScanBasedSittingDiscovery(unittest.TestCase):
    def test_two_identifierless_codex_rollouts_form_one_readable_extract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"
            run = scratch / "runs" / "course-module-discussion"
            run.mkdir(parents=True)
            home = root / "home"
            sessions = home / ".codex" / "sessions" / "2026" / "09" / "13"
            sessions.mkdir(parents=True)
            memory = root / "memory" / "MEMORY.md"
            memory.parent.mkdir()
            memory.write_text("# Index\n", encoding="utf-8")
            submission = "post-2026-09-13"
            (run / "reread.md").write_text(
                f"## REREAD: {submission}\n"
                "POST-URL: https://example.org/submissions/1\n"
                "POSTED: 2026-09-13T12:00:00Z\n"
                "READ: 2026-09-13\n"
                "VERDICT: matches - the posted artifact was read back\n",
                encoding="utf-8",
            )

            transcripts = tuple(sessions / f"rollout-{name}.jsonl" for name in ("first", "second"))
            for transcript in transcripts:
                rows = [
                    {"type": "session_meta", "payload": {"source": "cli"}},
                    codex_row(
                        {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "Review this sitting."}],
                        }
                    ),
                    codex_row(
                        {
                            "type": "custom_tool_call",
                            "name": "exec",
                            "input": json.dumps({"cmd": f'python tools/aar_scan.py "{run}"'}),
                        }
                    ),
                ]
                transcript.write_text(
                    "\n".join(json.dumps(item) for item in rows) + "\n",
                    encoding="utf-8",
                )

            with (
                mock.patch.object(Path, "home", return_value=home),
                mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=scratch),
            ):
                destination, count = aar_scan.write_extract(
                    run, transcripts[0], submission, memory
                )

            fields, identifiers = aar_scan._extract_metadata(destination)
            self.assertEqual(count, 4)
            self.assertEqual(len(identifiers), 4)
            self.assertEqual(fields["TRANSCRIPTS-READ"], "2")
            self.assertTrue(any(identifier.startswith("rollout-first#row-") for identifier in identifiers))
            self.assertTrue(any(identifier.startswith("rollout-second#row-") for identifier in identifiers))

            aar_scan.review_path(run, submission).write_text(
                f"TRANSCRIPTS: {fields['TRANSCRIPTS']}\n"
                f"WATERMARK: {fields['WATERMARK']}\n"
                "CLASSIFIER-ENTRY: reader-1\n",
                encoding="utf-8",
            )
            with transcripts[0].open("a", encoding="utf-8") as destination_file:
                destination_file.write(
                    json.dumps(
                        codex_row(
                            {
                                "type": "message",
                                "id": "new-entry",
                                "role": "user",
                                "content": [{"type": "input_text", "text": "A later correction."}],
                            }
                        )
                    )
                    + "\n"
                )
            with (
                mock.patch.object(Path, "home", return_value=home),
                mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=scratch),
            ):
                later, _paths = aar_scan.collect_population(run, transcripts[0])

            self.assertEqual([candidate.identifier for candidate in later], ["new-entry"])

    def test_discovery_bounds_the_scan_and_excludes_drone_transcripts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"
            run = scratch / "runs" / "course-module-discussion"
            run.mkdir(parents=True)
            home = root / "home"
            sessions = home / ".codex" / "sessions"
            archived = home / ".codex" / "archived_sessions"
            claude_subagents = home / ".claude" / "projects" / "session" / "subagents"
            for folder in (sessions, archived, claude_subagents):
                folder.mkdir(parents=True)

            def codex_sitting(path: Path, source: object, command: str) -> None:
                path.write_text(
                    "\n".join(
                        json.dumps(item)
                        for item in (
                            {"type": "session_meta", "payload": {"source": source}},
                            codex_row(
                                {
                                    "type": "custom_tool_call",
                                    "id": path.stem,
                                    "name": "exec",
                                    "input": json.dumps({"cmd": command}),
                                }
                            ),
                        )
                    )
                    + "\n",
                    encoding="utf-8",
                )

            main = sessions / "main.jsonl"
            archived_main = archived / "archived.jsonl"
            old = sessions / "old.jsonl"
            unrelated = sessions / "unrelated.jsonl"
            drone = sessions / "drone.jsonl"
            claude_drone = claude_subagents / "agent-1.jsonl"
            command = f'python tools/aar_scan.py "{run}"'
            codex_sitting(main, "cli", command)
            codex_sitting(archived_main, "cli", command)
            codex_sitting(old, "cli", command)
            codex_sitting(unrelated, "cli", "echo unrelated")
            codex_sitting(drone, {"subagent": {"name": "reader"}}, command)
            write_transcript(claude_drone, run)
            old_time = run.stat().st_ctime - (25 * 60 * 60)
            os.utime(old, (old_time, old_time))

            with (
                mock.patch.object(Path, "home", return_value=home),
                mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=scratch),
                mock.patch.object(aar_scan, "_run_created_at", return_value=run.stat().st_ctime),
            ):
                discovery = aar_scan.discover_transcripts(run)

            self.assertEqual(set(discovery.paths), {main.resolve(), archived_main.resolve()})
            self.assertEqual(discovery.found, 6)
            self.assertEqual(discovery.skipped_by_time, 1)
            self.assertEqual(discovery.skipped_by_byte_search, 1)
            self.assertEqual(discovery.read, 2)

            with (
                mock.patch.object(Path, "home", return_value=home),
                mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=scratch),
            ):
                forced_drone = aar_scan.discover_transcripts(run, claude_drone)

            self.assertNotIn(claude_drone.resolve(), forced_drone.paths)

    def test_grading_counts_sittings_that_began_after_the_extract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"
            run = scratch / "runs" / "course-module-discussion"
            run.mkdir(parents=True)
            home = root / "home"
            sessions = home / ".codex" / "sessions"
            sessions.mkdir(parents=True)
            command = f'python tools/aar_scan.py "{run}"'
            for name, timestamp in (
                ("before", "2026-09-13T11:59:00Z"),
                ("after", "2026-09-13T12:01:00Z"),
            ):
                (sessions / f"{name}.jsonl").write_text(
                    "\n".join(
                        json.dumps(item)
                        for item in (
                            {"type": "session_meta", "timestamp": timestamp, "payload": {"source": "cli"}},
                            codex_row(
                                {
                                    "type": "custom_tool_call",
                                    "id": name,
                                    "name": "exec",
                                    "input": json.dumps({"cmd": command}),
                                },
                                timestamp=timestamp,
                            ),
                        )
                    )
                    + "\n",
                    encoding="utf-8",
                )

            with (
                mock.patch.object(Path, "home", return_value=home),
                mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=scratch),
            ):
                count = aar_scan.count_later_sittings(
                    run, aar_scan._utc_timestamp("2026-09-13T12:00:00Z", "EXTRACTED-AT")
                )

            self.assertEqual(count, 1)


class SubmissionRecord(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run = self.root / "course-module-discussion"
        self.run.mkdir()
        self.transcript = self.root / "session-1.jsonl"
        write_transcript(self.transcript)
        self.memory = self.root / "memory" / "MEMORY.md"
        self.memory.parent.mkdir()
        self.memory.write_text("# Index\n", encoding="utf-8")
        self.submission = "post-2026-09-02"
        (self.run / "reread.md").write_text(
            f"## REREAD: {self.submission}\n"
            "POST-URL: https://example.org/submissions/1\n"
            "POSTED: 2026-09-13T12:00:00Z\n"
            "READ: 2026-09-13\n"
            "VERDICT: matches - the posted artifact was read back\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def extract(self) -> tuple[dict[str, str], set[str]]:
        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        return aar_scan._extract_metadata(aar_scan.extract_path(self.run, self.submission))

    def test_repeated_task_notification_rows_form_one_readable_extract(self) -> None:
        notification = (
            "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
            "<task-notification><task-id>reader-duplicate</task-id>"
            "<result>Finished.</result></task-notification>"
        )
        self.transcript.write_text(
            "\n".join(
                json.dumps(item)
                for item in (
                    {
                        "type": "queue-operation",
                        "uuid": "notification-enqueue",
                        "operation": "enqueue",
                        "content": notification,
                    },
                    row("user", "notification-delivery", {"content": notification}),
                    {
                        "type": "queue-operation",
                        "uuid": "notification-remove",
                        "operation": "remove",
                        "content": notification,
                    },
                )
            )
            + "\n",
            encoding="utf-8",
        )

        destination, count = aar_scan.write_extract(
            self.run, self.transcript, self.submission, self.memory
        )
        _fields, identifiers = aar_scan._extract_metadata(destination)

        self.assertEqual(count, 3)
        self.assertEqual(
            identifiers,
            {"notification-enqueue", "notification-delivery", "notification-remove"},
        )

    def test_an_unreadable_built_extract_leaves_no_round_files(self) -> None:
        population = [
            aar_scan.Candidate("duplicate", self.transcript.stem, "clinician", "First."),
            aar_scan.Candidate("duplicate", self.transcript.stem, "assistant", "Second."),
        ]
        discovery = aar_scan.TranscriptDiscovery(
            paths=(self.transcript,),
            found=1,
            skipped_by_time=0,
            skipped_by_byte_search=0,
            read=1,
        )

        with (
            mock.patch.object(
                aar_scan,
                "_collect_population",
                return_value=(population, (self.transcript,), discovery),
            ),
            self.assertRaisesRegex(ValueError, "identifier is absent or duplicated"),
        ):
            aar_scan.write_extract(
                self.run, self.transcript, self.submission, self.memory
            )

        self.assertFalse(aar_scan.extract_path(self.run, self.submission).exists())
        self.assertFalse(aar_scan.baseline_path(self.run, self.submission).exists())

    def test_rebuild_round_repairs_only_notification_identifiers(self) -> None:
        notification = (
            "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
            "<task-notification><task-id>reader-rebuild</task-id>"
            "<result>Finished.</result></task-notification>"
        )
        identifiers = (
            "notification-enqueue",
            "notification-delivery",
            "notification-remove",
        )
        self.transcript.write_text(
            "\n".join(
                json.dumps(item)
                for item in (
                    {
                        "type": "queue-operation",
                        "uuid": identifiers[0],
                        "operation": "enqueue",
                        "content": notification,
                    },
                    row("user", identifiers[1], {"content": notification}),
                    {
                        "type": "queue-operation",
                        "uuid": identifiers[2],
                        "operation": "remove",
                        "content": notification,
                    },
                )
            )
            + "\n",
            encoding="utf-8",
        )
        destination, _count = aar_scan.write_extract(
            self.run, self.transcript, self.submission, self.memory
        )
        fields, _identifiers = aar_scan._extract_metadata(destination)
        refused = destination.read_text(encoding="utf-8")
        for identifier in identifiers:
            refused = refused.replace(
                f"## ENTRY: {identifier}", "## ENTRY: reader-rebuild"
            )
        refused = refused.replace(
            f"{self.transcript.stem}={identifiers[-1]}",
            f"{self.transcript.stem}=reader-rebuild",
        ).replace(
            f"WATERMARK: {identifiers[-1]}", "WATERMARK: reader-rebuild"
        )
        destination.write_text(refused, encoding="utf-8")
        baseline = aar_scan.baseline_path(self.run, self.submission).read_bytes()
        review = aar_scan.review_path(self.run, self.submission)
        review.write_text(
            "# AFTER-ACTION REVIEW\n"
            f"SUBMISSION: {self.submission}\n"
            f"TRANSCRIPTS: {fields['TRANSCRIPTS']}\n"
            "POPULATION: 3\n"
            "UNREAD: 0\n"
            "WATERMARK: reader-rebuild\n"
            f"MEMORY-INDEX: {self.memory.resolve()}\n"
            "CLASSIFIER: fresh adversarial reader - test\n"
            "CLASSIFIER-ENTRY: reader-next\n"
            "DISAGREEMENTS: none recorded\n"
            "CORRECTIONS: none\n"
            "SUSTAINS: none\n",
            encoding="utf-8",
        )
        review_bytes = review.read_bytes()

        status, stdout, stderr = invoke_main(
            [
                str(self.run),
                "--submission",
                self.submission,
                "--transcript",
                str(self.transcript),
                "--memory-index",
                str(self.memory),
                "--extract",
                "--rebuild-round",
                "1",
            ]
        )

        scan = aar_scan.survey(self.run, self.submission)
        self.assertEqual([finding.kind for finding in scan.findings], [], stdout)
        self.assertEqual((status, stderr), (0, ""), stdout)
        self.assertIn("rebuilt round                 1", stdout)
        self.assertIn("review records                  1", stdout)
        self.assertIn("findings                        0", stdout)
        _fields, rebuilt_identifiers = aar_scan._extract_metadata(destination)
        self.assertEqual(rebuilt_identifiers, set(identifiers))
        self.assertEqual(
            (self.run / "aar" / "refused" / destination.name).read_text(encoding="utf-8"),
            refused,
        )
        self.assertEqual(
            aar_scan.baseline_path(self.run, self.submission).read_bytes(), baseline
        )
        self.assertEqual(review.read_bytes(), review_bytes)

    def test_rebuild_round_rejects_a_changed_non_notification_identifier(self) -> None:
        self.transcript.write_text(
            json.dumps(row("user", "original-row", {"content": "Review this."}))
            + "\n",
            encoding="utf-8",
        )
        destination, _count = aar_scan.write_extract(
            self.run, self.transcript, self.submission, self.memory
        )
        refused = destination.read_bytes()
        baseline = aar_scan.baseline_path(self.run, self.submission).read_bytes()
        self.transcript.write_text(
            json.dumps(row("user", "changed-row", {"content": "Review this."}))
            + "\n",
            encoding="utf-8",
        )

        status, _stdout, stderr = invoke_main(
            [
                str(self.run),
                "--submission",
                self.submission,
                "--memory-index",
                str(self.memory),
                "--extract",
                "--rebuild-round",
                "1",
            ]
        )

        self.assertEqual(status, 2)
        self.assertIn("changed a non-notification entry identifier", stderr)
        self.assertEqual(destination.read_bytes(), refused)
        self.assertEqual(
            aar_scan.baseline_path(self.run, self.submission).read_bytes(), baseline
        )
        self.assertFalse((self.run / "aar" / "refused").exists())

    def test_rebuild_round_compares_the_writers_normalized_line_endings(self) -> None:
        self.transcript.write_text(
            json.dumps(
                row("user", "windows-lines", {"content": "First line.\r\nSecond line."})
            )
            + "\n",
            encoding="utf-8",
        )
        aar_scan.write_extract(
            self.run, self.transcript, self.submission, self.memory
        )

        destination, count, _archived = aar_scan.rebuild_extract(
            self.run, self.submission, 1
        )

        self.assertEqual(count, 1)
        _fields, identifiers = aar_scan._extract_metadata(destination)
        self.assertEqual(identifiers, {"windows-lines"})

    def test_rebuild_round_uses_earlier_cursors_and_its_recorded_entry_count(self) -> None:
        self.transcript.write_text(
            json.dumps(row("user", "round-one", {"content": "First round."})) + "\n",
            encoding="utf-8",
        )
        first, _count = aar_scan.write_extract(
            self.run, self.transcript, self.submission, self.memory
        )
        first_fields, _identifiers = aar_scan._extract_metadata(first)
        aar_scan.review_path(self.run, self.submission).write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\n"
            f"WATERMARK: {first_fields['WATERMARK']}\n",
            encoding="utf-8",
        )
        notification = (
            "<task-notification><task-id>reader-round-two</task-id>"
            "<result>Finished.</result></task-notification>"
        )
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(
                json.dumps(row("user", "round-two-first", {"content": notification}))
                + "\n"
            )
            stream.write(
                json.dumps(row("user", "round-two-second", {"content": notification}))
                + "\n"
            )
        second, _count = aar_scan.write_extract(
            self.run, self.transcript, self.submission, self.memory
        )
        refused = second.read_text(encoding="utf-8")
        for identifier in ("round-two-first", "round-two-second"):
            refused = refused.replace(
                f"## ENTRY: {identifier}", "## ENTRY: reader-round-two"
            )
        second.write_text(refused, encoding="utf-8")
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(
                json.dumps(row("user", "after-round-two", {"content": "Later sitting."}))
                + "\n"
            )

        destination, count, _archived = aar_scan.rebuild_extract(
            self.run, self.submission, 2
        )
        _fields, identifiers = aar_scan._extract_metadata(destination)

        self.assertEqual(count, 2)
        self.assertEqual(identifiers, {"round-two-first", "round-two-second"})

    def test_version_two_extract_frames_a_body_that_quotes_an_entry_heading(self) -> None:
        self.transcript.write_text(
            json.dumps(
                row(
                    "user",
                    "u-collision",
                    {"content": "Classifier discussion:\n## ENTRY: not-an-entry\nStill one body."},
                )
            )
            + "\n",
            encoding="utf-8",
        )

        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        path = aar_scan.extract_path(self.run, self.submission)
        text = path.read_text(encoding="utf-8")
        fields, identifiers = aar_scan._extract_metadata(path)

        self.assertEqual(fields["FORMAT"], "2")
        self.assertEqual(
            fields["ENTRY-KINDS"],
            " | ".join(
                f"{kind} = {description}"
                for kind, description in aar_scan.ENTRY_KIND_DESCRIPTIONS.items()
            ),
        )
        self.assertIn("TEXT-LINES: 3", text)
        self.assertEqual(identifiers, {"u-collision"})

    def test_extract_header_reports_matcher_remainders_and_launch_accounting(self) -> None:
        rows = [
            row(
                "assistant",
                "a1",
                {"content": [{"type": "tool_use", "id": "agent-call", "name": "Agent", "input": {}}]},
                version="2.1.266",
            ),
            row(
                "user",
                "launch",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "agent-call",
                            "content": "Async agent launched successfully.\nagentId: reader-7",
                        }
                    ]
                },
                version="2.1.266",
            ),
            {
                "type": "attachment",
                "uuid": "notification",
                "attachment": {
                    "type": "queued_command",
                    "commandMode": "task-notification",
                    "prompt": (
                        "[SYSTEM NOTIFICATION - NOT USER INPUT]\n"
                        "<task-notification><task-id>reader-7</task-id>"
                        "<result>Finished.</result></task-notification>"
                    ),
                },
                "version": "2.1.266",
            },
            row("user", "new-wrapper", {"content": "<future-wrapper>Injected.</future-wrapper>"}),
            row(
                "assistant",
                "assistant-wrapper",
                {
                    "content": [
                        {"type": "text", "text": "<future-assistant>Injected.</future-assistant>"}
                    ]
                },
            ),
            {"type": "future_row", "payload": {}},
            {"type": "response_item", "payload": {"type": "future_item"}},
        ]
        self.transcript.write_text(
            "\n".join(json.dumps(item) for item in rows) + "\n",
            encoding="utf-8",
        )

        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        fields, _identifiers = aar_scan._extract_metadata(
            aar_scan.extract_path(self.run, self.submission)
        )

        self.assertEqual(fields["HARNESS-VERSIONS"], "2.1.266")
        self.assertEqual(fields["UNDECLARED-ENVELOPES"], "2")
        self.assertEqual(fields["UNDECLARED-CODEX-ROW-TYPES"], "1")
        self.assertEqual(fields["UNDECLARED-CODEX-PAYLOAD-TYPES"], "1")
        self.assertEqual(fields["SUBAGENT-LAUNCHES"], "1")
        self.assertEqual(fields["SUBAGENT-JOINED-RESULTS"], "1")
        self.assertEqual(fields["SUBAGENT-UNJOINED"], "0")
        self.assertEqual(fields["NOTIFICATIONS-WITHOUT-JOIN-KEY"], "0")

    def test_browser_ownership_is_reported_with_all_three_creation_routes(self) -> None:
        rows = [
            row(
                "assistant",
                "create-call",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "create-1",
                            "name": "mcp__claude-in-chrome__tabs_create_mcp",
                            "input": {},
                        }
                    ]
                },
            ),
            row(
                "user",
                "create-result",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "create-1",
                            "content": "Created new tab. Tab ID: 11",
                        }
                    ]
                },
            ),
            row(
                "assistant",
                "context-call",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "context-1",
                            "name": "mcp__claude-in-chrome__tabs_context_mcp",
                            "input": {"createIfEmpty": True},
                        }
                    ]
                },
            ),
            row(
                "user",
                "context-result",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "context-1",
                            "content": "Created new tab because no tabs were available. Tab ID: 12",
                        }
                    ]
                },
            ),
            row(
                "assistant",
                "navigate-create",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "navigate-1",
                            "name": "mcp__claude-in-chrome__navigate",
                            "input": {"url": "https://example.test"},
                        }
                    ]
                },
            ),
            row(
                "user",
                "navigate-result",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "navigate-1",
                            "content": "Created new tab for navigation. Tab ID: 13",
                        }
                    ]
                },
            ),
            row(
                "assistant",
                "page-actions",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "owned-action",
                            "name": "mcp__claude-in-chrome__read_page",
                            "input": {"tabId": 11},
                        },
                        {
                            "type": "tool_use",
                            "id": "unowned-action",
                            "name": "mcp__claude-in-chrome__read_page",
                            "input": {"tabId": 99},
                        },
                    ]
                },
            ),
        ]
        self.transcript.write_text(
            "\n".join(json.dumps(item) for item in rows) + "\n",
            encoding="utf-8",
        )

        fields, _identifiers = self.extract()

        self.assertEqual(fields["UNOWNED-BROWSER-PAGE-ACTIONS"], "1")
        self.assertEqual(fields["TAB-CREATION-PARSES-TABS-CREATE-MCP"], "1")
        self.assertEqual(fields["TAB-CREATION-PARSES-TABS-CONTEXT-MCP"], "1")
        self.assertEqual(fields["TAB-CREATION-PARSES-NAVIGATE-WITHOUT-TAB"], "1")

    def test_create_if_empty_does_not_make_an_existing_returned_tab_owned(self) -> None:
        rows = [
            row(
                "assistant",
                "context-call",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "context-1",
                            "name": "mcp__claude-in-chrome__tabs_context_mcp",
                            "input": {"createIfEmpty": True},
                        }
                    ]
                },
            ),
            row(
                "user",
                "context-result",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "context-1",
                            "content": '{"availableTabs": [{"tabId": 12}]}',
                        }
                    ]
                },
            ),
            row(
                "assistant",
                "page-action",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "unowned-action",
                            "name": "mcp__claude-in-chrome__read_page",
                            "input": {"tabId": 12},
                        }
                    ]
                },
            ),
        ]

        diagnostics = aar_scan._browser_diagnostics(rows)

        self.assertEqual(diagnostics.unowned_page_actions, 1)
        self.assertEqual(diagnostics.creation_parses_tabs_context_mcp, 0)

    def test_creation_parse_counter_requires_a_parsed_tab_id(self) -> None:
        rows = [
            row(
                "assistant",
                "create-call",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "create-1",
                            "name": "mcp__claude-in-chrome__tabs_create_mcp",
                            "input": {},
                        }
                    ]
                },
            ),
            row(
                "user",
                "create-result",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "create-1",
                            "content": "Tab creation failed before an id was returned.",
                        }
                    ]
                },
            ),
        ]

        diagnostics = aar_scan._browser_diagnostics(rows)

        self.assertEqual(diagnostics.creation_parses_tabs_create_mcp, 0)

    def test_batched_tab_creation_owns_its_real_shaped_result(self) -> None:
        rows = [
            row(
                "assistant",
                "batch-create",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "batch-1",
                            "name": "mcp__claude-in-chrome__browser_batch",
                            "input": {
                                "actions": [
                                    {"name": "tabs_create_mcp", "input": {}}
                                ]
                            },
                        }
                    ]
                },
            ),
            row(
                "user",
                "batch-result",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "batch-1",
                            "content": "Result 1: Created new tab. Tab ID: 41",
                        }
                    ]
                },
            ),
            row(
                "assistant",
                "page-actions",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "owned-action",
                            "name": "mcp__claude-in-chrome__read_page",
                            "input": {"tabId": 41},
                        },
                        {
                            "type": "tool_use",
                            "id": "unowned-action",
                            "name": "mcp__claude-in-chrome__read_page",
                            "input": {"tabId": 42},
                        },
                    ]
                },
            ),
        ]

        diagnostics = aar_scan._browser_diagnostics(rows)

        self.assertEqual(diagnostics.creation_parses_tabs_create_mcp, 1)
        self.assertEqual(diagnostics.unowned_page_actions, 1)

    def test_creation_marker_owns_only_the_tab_id_in_its_own_record(self) -> None:
        rows = [
            row(
                "assistant",
                "context-call",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "context-1",
                            "name": "mcp__claude-in-chrome__tabs_context_mcp",
                            "input": {"createIfEmpty": True},
                        }
                    ]
                },
            ),
            row(
                "user",
                "context-result",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "context-1",
                            "content": (
                                '{"availableTabs": ['
                                '{"created": true, "tabId": 12}, '
                                '{"tabId": 99}]}'
                            ),
                        }
                    ]
                },
            ),
            row(
                "assistant",
                "page-actions",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "owned-action",
                            "name": "mcp__claude-in-chrome__read_page",
                            "input": {"tabId": 12},
                        },
                        {
                            "type": "tool_use",
                            "id": "unowned-action",
                            "name": "mcp__claude-in-chrome__read_page",
                            "input": {"tabId": 99},
                        },
                    ]
                },
            ),
        ]

        diagnostics = aar_scan._browser_diagnostics(rows)

        self.assertEqual(diagnostics.unowned_page_actions, 1)

    def test_in_app_tab_creation_owns_only_its_returned_tab(self) -> None:
        rows = [
            row(
                "assistant",
                "create-call",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "create-1",
                            "name": "mcp__Claude_Browser__tabs_create",
                            "input": {},
                        }
                    ]
                },
            ),
            row(
                "user",
                "create-result",
                {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "create-1",
                            "content": '{"tabId": 31}',
                        }
                    ]
                },
            ),
            row(
                "assistant",
                "page-actions",
                {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "owned-action",
                            "name": "mcp__Claude_Browser__read_page",
                            "input": {"tabId": 31},
                        },
                        {
                            "type": "tool_use",
                            "id": "unowned-action",
                            "name": "mcp__Claude_Browser__read_page",
                            "input": {"tabId": 32},
                        },
                    ]
                },
            ),
        ]

        diagnostics = aar_scan._browser_diagnostics(rows)

        self.assertEqual(diagnostics.creation_parses_tabs_create_mcp, 0)
        self.assertEqual(diagnostics.unowned_page_actions, 1)

    def test_browser_ownership_report_is_not_a_graded_finding(self) -> None:
        scan = aar_scan.Scan(
            submission="post-1",
            records=1,
            population=1,
            corrections=0,
            sustains=0,
            unread=0,
            findings=(),
            browser=aar_scan.BrowserDiagnostics(
                unowned_page_actions=2,
                creation_parses_tabs_create_mcp=3,
                creation_parses_tabs_context_mcp=4,
                creation_parses_navigate_without_tab=5,
            ),
        )

        report = aar_scan.format_report(scan, "run")

        self.assertEqual(scan.findings, ())
        self.assertIn("unowned browser page actions    2 (reported, not graded)", report)
        self.assertIn("tab creation parses: tabs_create_mcp  3", report)
        self.assertIn("tab creation parses: tabs_context_mcp 4", report)
        self.assertIn("tab creation parses: navigate no tab  5", report)

    def test_an_unknown_extract_format_is_not_scanned(self) -> None:
        self.write_clean()
        path = aar_scan.extract_path(self.run, self.submission)
        path.write_text(
            path.read_text(encoding="utf-8").replace("FORMAT: 2", "FORMAT: 99", 1),
            encoding="utf-8",
        )

        status, stdout, stderr = invoke_main(
            [str(self.run), "--submission", self.submission]
        )

        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertIn("unknown extract format 99", stderr)

    def test_a_malformed_known_extract_is_an_extract_finding(self) -> None:
        self.write_clean()
        path = aar_scan.extract_path(self.run, self.submission)
        path.write_text(
            path.read_text(encoding="utf-8").replace("TEXT-LINES: 1", "TEXT-LINES: many", 1),
            encoding="utf-8",
        )

        scan = aar_scan.survey(self.run, self.submission)

        self.assertEqual([finding.kind for finding in scan.findings], ["unscannable-extract"])

    def test_a_prior_review_result_is_relabelled_by_recorded_identity(self) -> None:
        self.transcript.write_text(
            "\n".join(
                json.dumps(item)
                for item in [
                    row("user", "watermark", {"content": "First sitting."}),
                    row(
                        "user",
                        "notification-enqueue",
                        {
                            "content": (
                                "<task-notification><task-id>reader-1</task-id>"
                                "<result>Earlier verdicts.</result></task-notification>"
                            )
                        },
                    ),
                    row(
                        "user",
                        "notification-delivery",
                        {
                            "content": (
                                "<task-notification><task-id>reader-1</task-id>"
                                "<result>Earlier verdicts.</result></task-notification>"
                            )
                        },
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "first.md").write_text(
            "\n".join(
                [
                    "# AFTER-ACTION REVIEW",
                    "SUBMISSION: first",
                    f"TRANSCRIPTS: {self.transcript.stem}",
                    "WATERMARK: watermark",
                    "CLASSIFIER-ENTRY: reader-1",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        population, _transcripts = aar_scan.collect_population(self.run, self.transcript)

        self.assertEqual(
            [(item.identifier, item.kind) for item in population],
            [
                ("notification-enqueue", "prior-review"),
                ("notification-delivery", "prior-review"),
            ],
        )

    def test_prior_records_select_the_furthest_watermark_not_the_last_filename(self) -> None:
        self.transcript.write_text(
            "\n".join(
                json.dumps(row("user", identifier, {"content": identifier}))
                for identifier in ("first", "second", "third")
            )
            + "\n",
            encoding="utf-8",
        )
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "review.md").write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\nWATERMARK: second\nCLASSIFIER-ENTRY: current-reader\n",
            encoding="utf-8",
        )
        (aar / "review.pass1.md").write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\nWATERMARK: first\n",
            encoding="utf-8",
        )

        population, _transcripts = aar_scan.collect_population(self.run, self.transcript)

        self.assertEqual([candidate.identifier for candidate in population], ["third"])
        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        fields, _identifiers = aar_scan._extract_metadata(
            aar_scan.extract_path(self.run, self.submission)
        )
        self.assertEqual(fields["UNMARKED-PRIOR-REVIEWS"], "0")

    def test_a_legacy_notification_uuid_remains_a_valid_watermark_alias(self) -> None:
        self.transcript.write_text(
            "\n".join(
                json.dumps(item)
                for item in [
                    row(
                        "user",
                        "legacy-notification-uuid",
                        {
                            "content": (
                                "<task-notification><task-id>reader-legacy</task-id>"
                                "<result>Finished.</result></task-notification>"
                            )
                        },
                    ),
                    row("user", "after", {"content": "Continue."}),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "legacy.md").write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\nWATERMARK: legacy-notification-uuid\n",
            encoding="utf-8",
        )

        population, _transcripts = aar_scan.collect_population(self.run, self.transcript)

        self.assertEqual([candidate.identifier for candidate in population], ["after"])

    def test_a_task_id_watermark_resolves_to_its_first_notification_entry(self) -> None:
        notification = (
            "<task-notification><task-id>reader-shared</task-id>"
            "<result>Finished.</result></task-notification>"
        )
        self.transcript.write_text(
            "\n".join(
                json.dumps(item)
                for item in [
                    row("user", "notification-first", {"content": notification}),
                    row("user", "notification-second", {"content": notification}),
                    row("user", "after", {"content": "Continue."}),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "legacy.md").write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\nWATERMARK: reader-shared\n",
            encoding="utf-8",
        )

        population, _transcripts = aar_scan.collect_population(self.run, self.transcript)

        self.assertEqual(
            [candidate.identifier for candidate in population],
            ["notification-second", "after"],
        )

    def test_a_legacy_classifier_entry_alias_is_relabelled_as_a_prior_review(self) -> None:
        self.transcript.replace(self.transcript.with_name("rollout.jsonl"))
        self.transcript = self.transcript.with_name("rollout.jsonl")
        self.transcript.write_text(
            "\n".join(
                json.dumps(
                    codex_row(
                        {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": text}],
                        }
                    )
                )
                for text in ("Earlier watermark.", "Earlier classifier return.")
            )
            + "\n",
            encoding="utf-8",
        )
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "legacy.md").write_text(
            "TRANSCRIPTS: rollout\n"
            "WATERMARK: line-1\n"
            "CLASSIFIER-ENTRY: line-2\n",
            encoding="utf-8",
        )

        population, _transcripts = aar_scan.collect_population(
            self.run, self.transcript
        )

        self.assertEqual(len(population), 1)
        self.assertEqual(population[0].kind, "prior-review")

    def test_a_prior_watermark_without_classifier_identity_is_reported(self) -> None:
        aar = self.run / "aar"
        aar.mkdir()
        (aar / "legacy.md").write_text(
            f"TRANSCRIPTS: {self.transcript.stem}\nWATERMARK: u1\n",
            encoding="utf-8",
        )

        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        fields, _identifiers = aar_scan._extract_metadata(
            aar_scan.extract_path(self.run, self.submission)
        )

        self.assertEqual(fields["UNMARKED-PRIOR-REVIEWS"], "1")
        self.write_clean()
        scan = aar_scan.survey(self.run, self.submission)
        self.assertIn("unmarked-prior-review", [finding.kind for finding in scan.findings])

    def write_clean(self, round_number: int = 1, *, extract: bool = True) -> None:
        destination = aar_scan.extract_path(self.run, self.submission, round_number)
        if extract and not destination.is_file():
            fields, _identifiers = self.extract()
        else:
            fields, _identifiers = aar_scan._extract_metadata(
                destination
            )
        record = "\n".join(
            [
                "# AFTER-ACTION REVIEW",
                f"SUBMISSION: {self.submission}",
                f"TRANSCRIPTS: {fields['TRANSCRIPTS']}",
                f"POPULATION: {fields['POPULATION']}",
                "UNREAD: 0",
                f"WATERMARK: {fields['WATERMARK']}",
                f"MEMORY-INDEX: {self.memory}",
                "CLASSIFIER: fresh adversarial reader",
                "CLASSIFIER-ENTRY: reader-1",
                "DISAGREEMENTS: none recorded",
                "CORRECTIONS: none",
                "SUSTAINS: none",
                "",
            ]
        )
        aar_scan.review_path(self.run, self.submission, round_number).write_text(
            record, encoding="utf-8"
        )

    def test_extract_refuses_before_the_submission_has_a_posted_reading(self) -> None:
        (self.run / "reread.md").unlink()

        with self.assertRaisesRegex(ValueError, "REREAD"):
            self.extract()

        self.assertFalse(aar_scan.extract_path(self.run, self.submission).exists())

    def test_the_exact_posted_reading_is_fingerprinted_not_the_whole_file(self) -> None:
        self.write_clean()
        extract = aar_scan.extract_path(self.run, self.submission)
        fields, _identifiers = aar_scan._extract_metadata(extract)

        self.assertRegex(fields["POSTED-READING-FINGERPRINT"], r"^[0-9a-f]{64}$")
        reread = self.run / "reread.md"
        reread.write_text(
            reread.read_text(encoding="utf-8")
            + "\n## REREAD: another-submission\n"
            + "POST-URL: https://example.org/submissions/2\n"
            + "POSTED: 2026-09-13T13:00:00Z\n"
            + "READ: 2026-09-13\n"
            + "VERDICT: matches - another artifact was read back\n",
            encoding="utf-8",
        )

        self.assertNotIn(
            "posted-reading-mismatch",
            [finding.kind for finding in aar_scan.survey(self.run, self.submission).findings],
        )

    def test_a_changed_or_missing_posted_reading_fingerprint_fails_the_grade(self) -> None:
        self.write_clean()
        reread = self.run / "reread.md"
        reread.write_text(
            reread.read_text(encoding="utf-8").replace(
                "the posted artifact was read back", "the posted artifact changed"
            ),
            encoding="utf-8",
        )
        self.assertIn(
            "posted-reading-mismatch",
            [finding.kind for finding in aar_scan.survey(self.run, self.submission).findings],
        )

    def test_a_changed_visit_locator_moves_with_the_posted_reading_block(self) -> None:
        reread = self.run / "reread.md"
        reread.write_text(
            reread.read_text(encoding="utf-8")
            + "VISIT: 1 | reference matched | patient-detail=/patients/17 | "
            "note-view=/forms/view?resultid=31 | visit-date=08/17/2026 | matches\n",
            encoding="utf-8",
        )
        self.write_clean()
        reread.write_text(
            reread.read_text(encoding="utf-8").replace("resultid=31", "resultid=32"),
            encoding="utf-8",
        )

        self.assertIn(
            "posted-reading-mismatch",
            [finding.kind for finding in aar_scan.survey(self.run, self.submission).findings],
        )

    def test_a_current_extract_cannot_drop_its_format_and_fingerprint_to_look_legacy(self) -> None:
        self.write_clean()
        extract = aar_scan.extract_path(self.run, self.submission)
        extract.write_text(
            "\n".join(
                line
                for line in extract.read_text(encoding="utf-8").splitlines()
                if line != "FORMAT: 2"
                and not line.startswith("POSTED-READING-FINGERPRINT:")
            )
            + "\n",
            encoding="utf-8",
        )

        self.assertIn(
            "posted-reading-mismatch",
            [finding.kind for finding in aar_scan.survey(self.run, self.submission).findings],
        )

        extract = aar_scan.extract_path(self.run, self.submission)
        extract.write_text(
            "\n".join(
                line
                for line in extract.read_text(encoding="utf-8").splitlines()
                if not line.startswith("POSTED-READING-FINGERPRINT:")
            )
            + "\n",
            encoding="utf-8",
        )
        self.assertIn(
            "posted-reading-mismatch",
            [finding.kind for finding in aar_scan.survey(self.run, self.submission).findings],
        )

    def test_a_second_round_keeps_the_first_round_and_its_landing_baseline(self) -> None:
        fields, identifiers = self.extract()
        event = sorted(identifiers)[0]
        target = self.memory.parent / "landing.md"
        first_record = "\n".join(
            [
                "# AFTER-ACTION REVIEW",
                f"SUBMISSION: {self.submission}",
                f"TRANSCRIPTS: {fields['TRANSCRIPTS']}",
                f"POPULATION: {fields['POPULATION']}",
                "UNREAD: 0",
                f"WATERMARK: {fields['WATERMARK']}",
                f"MEMORY-INDEX: {self.memory}",
                "CLASSIFIER: fresh adversarial reader",
                "CLASSIFIER-ENTRY: reader-1",
                "DISAGREEMENTS: none recorded",
                "SUSTAINS: none",
                f"## CORRECTION: {event}",
                "CORRECTOR: clinician",
                "IN-ERROR: orchestrator",
                "SUMMARY: the durable memory needed one correction",
                "CLASSIFIER: durable memory",
                "ORCHESTRATOR: agree - the memory was corrected",
                "DISPOSITION: memory-write",
                f"TARGET: {target}",
                "LANDING: memory entry added",
                "",
            ]
        )
        aar_scan.review_path(self.run, self.submission).write_text(first_record, encoding="utf-8")
        target.write_text("landed\n", encoding="utf-8")
        first_extract = aar_scan.extract_path(self.run, self.submission).read_bytes()
        first_baseline = aar_scan.baseline_path(self.run, self.submission).read_bytes()

        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row("user", "round-2", {"content": "Review again."})) + "\n")
        destination, _count = aar_scan.write_extract(
            self.run, self.transcript, self.submission, self.memory
        )
        self.assertEqual(destination, aar_scan.extract_path(self.run, self.submission, 2))
        self.write_clean(2, extract=False)

        scan = aar_scan.survey(self.run, self.submission)

        self.assertEqual(scan.records, 2)
        self.assertNotIn("unlanded-memory", [finding.kind for finding in scan.findings])
        self.assertEqual(aar_scan.extract_path(self.run, self.submission).read_bytes(), first_extract)
        self.assertEqual(aar_scan.baseline_path(self.run, self.submission).read_bytes(), first_baseline)
        self.assertTrue(aar_scan.review_path(self.run, self.submission, 2).is_file())

    def test_every_round_is_reported_and_an_earlier_unlanded_round_still_fails(self) -> None:
        fields, identifiers = self.extract()
        event = sorted(identifiers)[0]
        target = self.memory.parent / "never-landed.md"
        record = "\n".join(
            [
                "# AFTER-ACTION REVIEW",
                f"SUBMISSION: {self.submission}",
                f"TRANSCRIPTS: {fields['TRANSCRIPTS']}",
                f"POPULATION: {fields['POPULATION']}",
                "UNREAD: 0",
                f"WATERMARK: {fields['WATERMARK']}",
                f"MEMORY-INDEX: {self.memory}",
                "CLASSIFIER: fresh adversarial reader",
                "CLASSIFIER-ENTRY: reader-1",
                "DISAGREEMENTS: none recorded",
                "SUSTAINS: none",
                f"## CORRECTION: {event}",
                "CORRECTOR: clinician",
                "IN-ERROR: orchestrator",
                "SUMMARY: the durable memory needed one correction",
                "CLASSIFIER: durable memory",
                "ORCHESTRATOR: agree - the memory should be corrected",
                "DISPOSITION: memory-write",
                f"TARGET: {target}",
                "LANDING: memory entry absent",
                "",
            ]
        )
        aar_scan.review_path(self.run, self.submission).write_text(record, encoding="utf-8")
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row("user", "round-2", {"content": "Review again."})) + "\n")
        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        self.write_clean(2, extract=False)

        scan = aar_scan.survey(self.run, self.submission)
        report = aar_scan.format_report(scan, self.run.name)

        self.assertIn("unlanded-memory", [finding.kind for finding in scan.findings])
        self.assertIn("round 1 corrections 1; unlanded 1", report)
        self.assertIn("round 2 corrections 0; unlanded 0", report)

    def test_an_empty_current_extract_in_a_round_walking_grade_still_fails(self) -> None:
        self.write_clean()
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row("user", "round-2", {"content": "Review again."})) + "\n")
        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        self.write_clean(2, extract=False)
        extract = aar_scan.extract_path(self.run, self.submission, 2)
        lines = extract.read_text(encoding="utf-8").splitlines()
        header_end = lines.index("")
        empty_header = [
            "POPULATION: 0" if line.startswith("POPULATION:") else line
            for line in lines[:header_end]
        ]
        extract.write_text("\n".join((*empty_header, "", "")), encoding="utf-8")

        status, _stdout, _stderr = invoke_main(
            [str(self.run), "--submission", self.submission]
        )

        self.assertEqual(status, 1)

    def test_missing_record_is_the_expected_row(self) -> None:
        scan = aar_scan.survey(self.run, self.submission)

        self.assertEqual([row.kind for row in scan.findings], ["missing-review"])
        self.assertIsNotNone(aar_scan.completion_finding(self.run, [self.submission]))

    def test_a_complete_zero_correction_review_passes(self) -> None:
        self.write_clean()

        scan = aar_scan.survey(self.run, self.submission)

        self.assertEqual(scan.findings, ())
        self.assertEqual(scan.unread, 0)
        self.assertIsNone(aar_scan.completion_finding(self.run, [self.submission]))

    def test_a_post_cutoff_review_requires_the_classifier_entry_identity(self) -> None:
        self.write_clean()
        review = aar_scan.review_path(self.run, self.submission)
        review.write_text(
            review.read_text(encoding="utf-8").replace("CLASSIFIER-ENTRY: reader-1\n", ""),
            encoding="utf-8",
        )

        scan = aar_scan.survey(self.run, self.submission)

        self.assertIn("missing-classifier-entry", [finding.kind for finding in scan.findings])

    def test_the_first_run_moves_legacy_orphan_pointers_aside_without_deleting_them(self) -> None:
        pointer = self.run / "aar" / "orphaned-earlier.json"
        pointer.parent.mkdir()
        contents = (
            json.dumps(
                {
                    "transcript_path": str(self.transcript),
                    "run_key": self.run.name,
                }
            )
            + "\n"
        )
        pointer.write_text(
            contents,
            encoding="utf-8",
        )

        self.extract()

        retired = pointer.with_name("retired-orphaned-earlier.json")
        self.assertFalse(pointer.exists())
        self.assertEqual(retired.read_text(encoding="utf-8"), contents)

    def test_a_correction_cannot_be_dispositioned_nowhere(self) -> None:
        fields, identifiers = self.extract()
        event = sorted(identifiers)[0]
        record = "\n".join(
            [
                "# AFTER-ACTION REVIEW",
                f"SUBMISSION: {self.submission}",
                f"TRANSCRIPTS: {fields['TRANSCRIPTS']}",
                f"POPULATION: {fields['POPULATION']}",
                "UNREAD: 0",
                f"WATERMARK: {fields['WATERMARK']}",
                f"MEMORY-INDEX: {self.memory}",
                "CLASSIFIER: fresh adversarial reader",
                "CLASSIFIER-ENTRY: reader-1",
                "DISAGREEMENTS: none recorded",
                "SUSTAINS: none",
                f"## CORRECTION: {event}",
                "CORRECTOR: clinician",
                "IN-ERROR: orchestrator",
                "SUMMARY: cited the wrong regulation section",
                "CLASSIFIER: tracker ticket",
                "ORCHESTRATOR: agree - the citation was wrong",
                "DISPOSITION: nothing durable",
                "TARGET: none",
                "LANDING: none",
                "",
            ]
        )
        aar_scan.review_path(self.run, self.submission).write_text(record, encoding="utf-8")

        kinds = {row.kind for row in aar_scan.survey(self.run, self.submission).findings}

        self.assertIn("unknown-disposition", kinds)

    def write_correction_record(
        self,
        run: Path,
        submission: str,
        fields: dict[str, str],
        memory: Path,
        corrections: tuple[CorrectionRecord, ...],
    ) -> None:
        lines = [
            "# AFTER-ACTION REVIEW",
            f"SUBMISSION: {submission}",
            f"TRANSCRIPTS: {fields['TRANSCRIPTS']}",
            f"POPULATION: {fields['POPULATION']}",
            "UNREAD: 0",
            f"WATERMARK: {fields['WATERMARK']}",
            f"MEMORY-INDEX: {memory}",
            "CLASSIFIER: fresh adversarial reader",
            "CLASSIFIER-ENTRY: reader-1",
            "DISAGREEMENTS: none recorded",
            "SUSTAINS: none",
        ]
        for correction in corrections:
            disposition = correction.disposition.value
            lines.extend(
                [
                    f"## CORRECTION: {correction.event}",
                    "CORRECTOR: clinician",
                    "IN-ERROR: orchestrator",
                    "SUMMARY: the correction needs a durable landing",
                    f"CLASSIFIER: {disposition} - the disposition matches the correction",
                    f"ORCHESTRATOR: agree - the {disposition} target now carries the correction",
                    f"DISPOSITION: {disposition}",
                    f"TARGET: {correction.target}",
                    f"LANDING: {correction.landing}",
                ]
            )
        aar_scan.review_path(run, submission).write_text(
            "\n".join([*lines, ""]), encoding="utf-8"
        )

    def check_landing_findings(
        self, target_git_state: CheckTargetGitState
    ) -> set[str]:
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
            subprocess.run(
                ["git", "config", "user.email", "tests@example.invalid"],
                cwd=checkout,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "AAR Tests"], cwd=checkout, check=True
            )
            target = checkout / "tools" / "check.py"
            target.parent.mkdir()
            target.write_text("original\n", encoding="utf-8")
            if target_git_state is not CheckTargetGitState.UNTRACKED:
                subprocess.run(["git", "add", "."], cwd=checkout, check=True)
                subprocess.run(
                    ["git", "commit", "-qm", "seed check"], cwd=checkout, check=True
                )

            run = checkout / "scratch" / "runs" / "course-module-discussion"
            run.mkdir(parents=True)
            transcript = checkout / "session-1.jsonl"
            write_transcript(transcript)
            memory = checkout / "memory" / "MEMORY.md"
            memory.parent.mkdir()
            memory.write_text("# Index\n", encoding="utf-8")
            submission = "post-2026-09-02"
            (run / "reread.md").write_text(
                f"## REREAD: {submission}\n"
                "POST-URL: https://example.org/submissions/1\n"
                "POSTED: 2026-09-13T12:00:00Z\n"
                "READ: 2026-09-13\n"
                "VERDICT: matches - the posted artifact was read back\n",
                encoding="utf-8",
            )
            with mock.patch.object(
                aar_scan, "__file__", str(checkout / "tools" / "aar_scan.py")
            ):
                aar_scan.write_extract(run, transcript, submission, memory)
                fields, identifiers = aar_scan._extract_metadata(
                    aar_scan.extract_path(run, submission)
                )
                event = sorted(identifiers)[0]
                if target_git_state in {
                    CheckTargetGitState.UNSTAGED,
                    CheckTargetGitState.STAGED,
                    CheckTargetGitState.COMMITTED,
                }:
                    target.write_text("changed\n", encoding="utf-8")
                if target_git_state in {
                    CheckTargetGitState.STAGED,
                    CheckTargetGitState.COMMITTED,
                }:
                    subprocess.run(["git", "add", "."], cwd=checkout, check=True)
                if target_git_state is CheckTargetGitState.COMMITTED:
                    subprocess.run(
                        ["git", "commit", "-qm", "tighten check"],
                        cwd=checkout,
                        check=True,
                    )
                self.write_correction_record(
                    run,
                    submission,
                    fields,
                    memory,
                    (
                        CorrectionRecord(
                            event=event,
                            disposition=CorrectionDisposition.CHECK,
                            target=target,
                            landing="the check now refuses the regressed behavior",
                        ),
                    ),
                )
                return {
                    finding.kind for finding in aar_scan.survey(run, submission).findings
                }

    def test_a_check_lands_only_when_a_tracked_target_changed_since_baseline(self) -> None:
        expected = {
            CheckTargetGitState.UNTRACKED: True,
            CheckTargetGitState.UNCHANGED: True,
            CheckTargetGitState.UNSTAGED: False,
            CheckTargetGitState.STAGED: False,
            CheckTargetGitState.COMMITTED: False,
        }
        for target_git_state, refused in expected.items():
            with self.subTest(target_git_state=target_git_state.value):
                self.assertEqual(
                    "unlanded-check"
                    in self.check_landing_findings(target_git_state),
                    refused,
                )

    def test_two_corrections_can_repeat_one_extract_identifier(self) -> None:
        second_memory = self.memory.parent / "PREFERENCES.md"
        second_memory.write_text("# Preferences\n", encoding="utf-8")
        fields, identifiers = self.extract()
        event = sorted(identifiers)[0]
        self.memory.write_text("# Index\n- corrected fact\n", encoding="utf-8")
        second_memory.write_text("# Preferences\n- sustained preference\n", encoding="utf-8")
        self.write_correction_record(
            self.run,
            self.submission,
            fields,
            self.memory,
            (
                CorrectionRecord(
                    event=event,
                    disposition=CorrectionDisposition.MEMORY_WRITE,
                    target=self.memory,
                    landing="added the corrected fact to the memory index",
                ),
                CorrectionRecord(
                    event=event,
                    disposition=CorrectionDisposition.MEMORY_WRITE,
                    target=second_memory,
                    landing="added the preference to its durable memory file",
                ),
            ),
        )

        scan = aar_scan.survey(self.run, self.submission)

        self.assertEqual(scan.corrections, 2)
        self.assertEqual(scan.findings, ())

    def test_a_correction_cannot_rest_on_text_written_by_the_extractor(self) -> None:
        self.transcript.write_text(
            json.dumps(
                row(
                    "assistant",
                    "a1",
                    {
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "tool-1",
                                "name": "Bash",
                                "input": {"command": "echo ready"},
                            }
                        ]
                    },
                )
            )
            + "\n",
            encoding="utf-8",
        )
        fields, identifiers = self.extract()
        event = next(iter(identifiers))
        self.memory.write_text("# Index\n- correction landed\n", encoding="utf-8")
        self.write_correction_record(
            self.run,
            self.submission,
            fields,
            self.memory,
            (
                CorrectionRecord(
                    event=event,
                    disposition=CorrectionDisposition.MEMORY_WRITE,
                    target=self.memory,
                    landing="the correction was added to memory",
                ),
            ),
        )

        scan = aar_scan.survey(self.run, self.submission)

        self.assertIn(
            "correction-on-extractor-written-entry",
            [finding.kind for finding in scan.findings],
        )

    def test_the_report_counts_correction_correctors_and_sustains_by_entry_kind(self) -> None:
        self.transcript.write_text(
            "\n".join(
                json.dumps(item)
                for item in (
                    row("user", "u1", {"content": "Use the corrected rule."}),
                    row(
                        "assistant",
                        "a1",
                        {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "tool-1",
                                    "name": "Bash",
                                    "input": {"command": "echo ready"},
                                }
                            ]
                        },
                    ),
                )
            )
            + "\n",
            encoding="utf-8",
        )
        fields, identifiers = self.extract()
        clinician = next(identifier for identifier in identifiers if identifier == "u1")
        tool_call = next(identifier for identifier in identifiers if identifier != "u1")
        self.memory.write_text("# Index\n- correction landed\n", encoding="utf-8")
        self.write_correction_record(
            self.run,
            self.submission,
            fields,
            self.memory,
            (
                CorrectionRecord(
                    event=clinician,
                    disposition=CorrectionDisposition.MEMORY_WRITE,
                    target=self.memory,
                    landing="the correction was added to memory",
                ),
            ),
        )
        review = aar_scan.review_path(self.run, self.submission)
        review.write_text(
            review.read_text(encoding="utf-8")
            .replace("SUSTAINS: none\n", "")
            + f"## SUSTAIN: {tool_call}\nSUMMARY: the tool invocation was retained correctly\n",
            encoding="utf-8",
        )

        scan = aar_scan.survey(self.run, self.submission)
        report = aar_scan.format_report(scan, self.run.name)

        self.assertEqual(scan.findings, ())
        self.assertEqual(
            scan.kind_counts,
            (
                aar_scan.EntryKindCount("correction", "clinician", "clinician", 1),
                aar_scan.EntryKindCount("sustain", "n/a", "tool-call", 1),
            ),
        )
        self.assertIn("  corrector by entry kind", report)
        self.assertIn("    correction | clinician | clinician | 1", report)
        self.assertIn("    sustain | n/a | tool-call | 1", report)


class EveryScopedCompletionGraderExpectsTheReview(unittest.TestCase):
    def test_the_aar_skill_briefs_scan_discovery_and_full_identifiers(self) -> None:
        skill = (
            Path(__file__).resolve().parent.parent / "skills" / "aar" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("reads every other main Claude or Codex transcript", skill)
        self.assertIn("using the identifier exactly as it follows `## ENTRY:`", skill)
        self.assertIn("whose text the extractor wrote rather than copied", skill)

    def test_course_assignment_completion_routes_through_its_artifact_dispatcher(self) -> None:
        self.assertEqual(
            "course_assignment_scan",
            aar_scan.COMPLETION_GRADERS["course-assignment"],
        )

    def test_every_scoped_skill_maps_to_a_grader_that_expects_the_fixed_row(self) -> None:
        self.assertEqual(set(aar_scan.COMPLETION_GRADERS), set(aar_scan.SCOPED_SKILLS))
        for skill, module_name in aar_scan.COMPLETION_GRADERS.items():
            with self.subTest(skill=skill, grader=module_name):
                module = importlib.import_module(module_name)
                expected = (aar_scan.EXPECTED_ROW,)
                if skill in voice_model_identity.SCOPED_SKILLS:
                    expected += (voice_model_identity.EXPECTED_ROW,)
                    expected += (
                        voice_read.EXPECTED_ROW,
                        voice_read.PROFANITY_EXPECTED_ROW,
                    )
                if skill in imagery_proposals.SCOPED_SKILLS:
                    expected += (imagery_proposals.EXPECTED_ROW,)
                if skill in project_context.SCOPED_SKILLS:
                    expected += (project_context.EXPECTED_ROW,)
                self.assertEqual(module.EXPECTED_COMPLETION_CHECKS, expected)
                text = (
                    Path(__file__).resolve().parent.parent / "skills" / skill / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn(module_name, text)
                self.assertIn("--submission", text)

    def test_an_unpaired_scoped_skill_is_named(self) -> None:
        with self.assertRaisesRegex(ValueError, "unpaired-skill"):
            aar_scan.validate_completion_graders(
                {"unpaired-skill"}, aar_scan.COMPLETION_GRADERS
            )

    def test_each_scoped_skill_invokes_aar_and_its_completion_row(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for name in aar_scan.SCOPED_SKILLS:
            with self.subTest(skill=name):
                text = (root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("`/AAR`", text)
                self.assertIn("the after-action review: clean", text)

    def test_session_end_has_no_after_action_review_hook(self) -> None:
        root = Path(__file__).resolve().parent.parent
        settings = json.loads((root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        registered = settings["hooks"]["SessionEnd"]
        aar_handlers = [
            handler
            for registration in registered
            for handler in registration["hooks"]
            if "aar_scan.py" in handler["command"]
        ]

        self.assertEqual(aar_handlers, [])


if __name__ == "__main__":
    unittest.main()
