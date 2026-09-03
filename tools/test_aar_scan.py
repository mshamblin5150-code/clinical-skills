"""Contract tests for the submission-keyed after-action review. #814."""

from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import aar_scan
import checks_ledger
import differential_scan
import discussion_post_scan
import discussion_reply_scan
import filled_vitals_census
import grader_conformance
import specificity_scan


AarScanConformance = grader_conformance.for_module(aar_scan)


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
            "  orphaned sittings               0\n"
            "  findings                        1\n\n"
            "  declared limits:\n"
            "    semantic classification\n"
            "    tool-result-only correction\n"
            "    uncorrected error\n"
            "    orchestrator veto\n"
            "    subagent silence\n"
            "    transcript flush\n"
            "    run-key discovery\n",
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
            "  private extract written         post-1.extract.md\n",
        )

    def test_the_session_end_mode_keeps_its_silent_exit_two(self) -> None:
        self.assertEqual(invoke_main(["--session-end"], stdin="{}"), (2, "", ""))

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

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def extract(self) -> tuple[dict[str, str], set[str]]:
        aar_scan.write_extract(self.run, self.transcript, self.submission, self.memory)
        return aar_scan._extract_metadata(aar_scan.extract_path(self.run, self.submission))

    def write_clean(self) -> None:
        fields, _identifiers = self.extract()
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
                "DISAGREEMENTS: none recorded",
                "CORRECTIONS: none",
                "SUSTAINS: none",
                "",
            ]
        )
        aar_scan.review_path(self.run, self.submission).write_text(record, encoding="utf-8")

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

    def test_a_clean_graded_command_drains_orphan_pointers_after_reporting(self) -> None:
        self.write_clean()
        pointer = self.run / "aar" / "orphaned-earlier.json"
        pointer.write_text(
            json.dumps(
                {
                    "transcript_path": str(self.transcript),
                    "run_key": self.run.name,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        stdout = io.StringIO()
        stderr = io.StringIO()
        original_unlink = Path.unlink

        def unlink_after_report(path: Path, *args: object, **kwargs: object) -> None:
            self.assertIn(
                "after-action review over course-module-discussion", stdout.getvalue()
            )
            original_unlink(path, *args, **kwargs)

        with (
            mock.patch.object(Path, "unlink", unlink_after_report),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = aar_scan.main([str(self.run), "--submission", self.submission])

        self.assertEqual((status, stderr.getvalue()), (0, ""))
        self.assertFalse(pointer.exists())

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


class EveryScopedCompletionGraderExpectsTheReview(unittest.TestCase):
    def test_the_six_named_graders_share_the_fixed_row(self) -> None:
        graders = (
            filled_vitals_census,
            differential_scan,
            discussion_post_scan,
            discussion_reply_scan,
            specificity_scan,
            checks_ledger,
        )

        self.assertEqual(
            [module.EXPECTED_COMPLETION_CHECKS for module in graders],
            [(aar_scan.EXPECTED_ROW,)] * len(graders),
        )

    def test_each_scoped_skill_invokes_aar_and_its_completion_row(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for name in aar_scan.SCOPED_SKILLS:
            with self.subTest(skill=name):
                text = (root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("`/AAR`", text)
                self.assertIn("the after-action review: clean", text)

    def test_session_end_is_registered_as_the_orphan_pointer_only(self) -> None:
        root = Path(__file__).resolve().parent.parent
        settings = json.loads((root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        registered = settings["hooks"]["SessionEnd"]

        self.assertEqual(len(registered), 1)
        self.assertIn("aar_scan.py", registered[0]["hooks"][0]["command"])
        self.assertIn("--session-end", registered[0]["hooks"][0]["command"])


class OrphanedSitting(unittest.TestCase):
    def test_session_end_writes_exactly_the_two_field_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "scratch" / "runs" / "course-module-discussion"
            run.mkdir(parents=True)
            transcript = root / "session-1.jsonl"
            write_transcript(transcript, run)
            original = aar_scan.repo_root.scratch_root
            aar_scan.repo_root.scratch_root = lambda: root / "scratch"
            try:
                status = aar_scan.session_end(
                    {
                        "hook_event_name": "SessionEnd",
                        "session_id": "session-1",
                        "transcript_path": str(transcript),
                        "reason": "other",
                    }
                )
            finally:
                aar_scan.repo_root.scratch_root = original

            self.assertEqual(status, 0)
            pointers = aar_scan.orphan_paths(run)
            self.assertEqual(len(pointers), 1)
            payload = json.loads(pointers[0].read_text(encoding="utf-8"))
            self.assertEqual(set(payload), {"transcript_path", "run_key"})
            self.assertEqual(payload["run_key"], run.name)

    def test_subagent_session_gets_no_pointer(self) -> None:
        self.assertEqual(
            aar_scan.session_end(
                {
                    "hook_event_name": "SessionEnd",
                    "agent_id": "agent-1",
                    "session_id": "session-1",
                    "transcript_path": "missing.jsonl",
                }
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
