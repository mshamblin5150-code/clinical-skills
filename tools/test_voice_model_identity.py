"""Contract tests for the coursework voice-model identity row. #1393."""

from __future__ import annotations

import json
import importlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import repo_root
import run_grader
import voice_model_identity as identity
import voice_read
import imagery_proposals
import project_context


class RecordWriter(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.run = Path(self._temporary.name) / "run"
        self.run.mkdir()

    def test_present_model_record_is_written_from_the_shared_resolution(self) -> None:
        resolved = repo_root.VoiceModelResolution(
            path=Path(self._temporary.name) / "scratch" / "voice-model.md",
            sha256="a" * 64,
            exists=True,
        )
        with mock.patch.object(repo_root, "canonical_voice_model", return_value=resolved):
            report = identity.write_record(self.run)

        payload = json.loads((self.run / identity.RECORD_NAME).read_text(encoding="utf-8"))
        self.assertEqual(
            payload,
            {"path": str(resolved.path), "sha256": "a" * 64, "exists": True},
        )
        self.assertEqual(report, f"voice model identity: recorded {resolved.path}")

    def test_absent_model_record_uses_the_existing_unmodeled_declaration(self) -> None:
        resolved = repo_root.VoiceModelResolution(
            path=Path(self._temporary.name) / "scratch" / "voice-model.md",
            sha256=None,
            exists=False,
        )
        with mock.patch.object(repo_root, "canonical_voice_model", return_value=resolved):
            report = identity.write_record(self.run)

        payload = json.loads((self.run / identity.RECORD_NAME).read_text(encoding="utf-8"))
        self.assertEqual(
            payload,
            {"path": str(resolved.path), "sha256": None, "exists": False},
        )
        self.assertEqual(
            report,
            f"voice model: NOT RUN -- no model at {resolved.path}; voice unmodeled",
        )


class CompletionGate(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)
        self.run = self.root / "run"
        self.run.mkdir()
        self.canonical = self.root / "owning" / "scratch" / "voice-model.md"
        self.resolved = repo_root.VoiceModelResolution(
            path=self.canonical,
            sha256="a" * 64,
            exists=True,
        )

    def write(self, **changes: object) -> None:
        payload: dict[str, object] = {
            "path": str(self.canonical),
            "sha256": "a" * 64,
            "exists": True,
        }
        payload.update(changes)
        (self.run / identity.RECORD_NAME).write_text(
            json.dumps(payload) + "\n", encoding="utf-8"
        )

    def grade(self) -> identity.CompletionGate:
        with mock.patch.object(
            repo_root, "canonical_voice_model", return_value=self.resolved
        ):
            return identity.completion_gate(self.run, "submission")

    def test_matching_path_and_digest_are_clean(self) -> None:
        self.write()
        result = self.grade()
        self.assertEqual(
            result,
            identity.CompletionGate(
                finding=False,
                coverage=False,
                report=f"{identity.EXPECTED_ROW}: clean",
            ),
        )

    def test_wrong_path_is_a_finding(self) -> None:
        self.write(path=str(self.root / "dated-snapshot" / "voice-model.md"))
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertFalse(result.coverage)
        self.assertIn("finding - declared path is not canonical", result.report)

    def test_matching_path_with_a_moved_digest_is_coverage(self) -> None:
        self.write(sha256="b" * 64)
        result = self.grade()
        self.assertFalse(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("not scanned - canonical digest moved", result.report)

    def test_unreadable_canonical_identity_is_coverage_not_an_exception(self) -> None:
        self.write()
        with mock.patch.object(
            repo_root,
            "canonical_voice_model",
            side_effect=IsADirectoryError("private path withheld"),
        ):
            result = identity.completion_gate(self.run, "submission")
        self.assertFalse(result.finding)
        self.assertTrue(result.coverage)
        self.assertIn("identity is unreadable", result.report)
        self.assertNotIn("private path", result.report)

    def test_wrong_path_wins_when_its_digest_also_moved(self) -> None:
        self.write(
            path=str(self.root / "dated-snapshot" / "voice-model.md"),
            sha256="b" * 64,
        )
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertTrue(result.coverage)

    def test_absence_record_is_clean_when_the_canonical_model_remains_absent(self) -> None:
        self.resolved = repo_root.VoiceModelResolution(
            path=self.canonical,
            sha256=None,
            exists=False,
        )
        self.write(sha256=None, exists=False)
        result = self.grade()
        self.assertFalse(result.finding)
        self.assertFalse(result.coverage)

    def test_no_override_state_is_accepted(self) -> None:
        self.write(override=True)
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("record shape is invalid", result.report)

    def test_missing_record_is_a_finding_only_when_completion_is_enabled(self) -> None:
        result = self.grade()
        self.assertTrue(result.finding)
        self.assertIn("record is missing", result.report)
        with mock.patch.object(
            repo_root, "canonical_voice_model", return_value=self.resolved
        ):
            early = identity.completion_gate(self.run, None)
        self.assertEqual(
            early.report,
            f"{identity.EXPECTED_ROW}: not graded - --submission was not supplied",
        )
        self.assertFalse(early.finding)

    def test_shared_adapter_preserves_finding_precedence_and_coverage_limb(self) -> None:
        self.write(
            path=str(self.root / "dated-snapshot" / "voice-model.md"),
            sha256="b" * 64,
        )
        base = run_grader.Grade(scan=object(), source=str(self.run))
        with mock.patch.object(
            repo_root, "canonical_voice_model", return_value=self.resolved
        ):
            result = identity.apply_completion_gate(
                base, self.run, "submission", coverage_limb="voice digest moved"
            )
        self.assertTrue(result.findings_failed)
        self.assertTrue(result.coverage_failed)
        self.assertEqual(result.coverage_limbs, ("voice digest moved",))
        self.assertIn("declared path is not canonical", result.reports[-1])


class ScopedCompletionGraders(unittest.TestCase):
    def test_the_scoped_completion_graders_declare_the_same_row(self) -> None:
        self.assertEqual(
            set(identity.COMPLETION_GRADERS),
            {
                "course-assignment",
                "discussion-post",
                "discussion-reply",
                "peer-critique",
                "practicum-case-study",
            },
        )
        for skill, module_name in identity.COMPLETION_GRADERS.items():
            with self.subTest(skill=skill, grader=module_name):
                module = importlib.import_module(module_name)
                self.assertEqual(
                    module.EXPECTED_COMPLETION_CHECKS,
                    (
                        "the after-action review",
                        identity.EXPECTED_ROW,
                        voice_read.EXPECTED_ROW,
                        voice_read.PROFANITY_EXPECTED_ROW,
                        imagery_proposals.EXPECTED_ROW,
                        project_context.EXPECTED_ROW,
                    ),
                )

    def test_each_scoped_skill_writes_the_record_before_drafting(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for skill in identity.COMPLETION_GRADERS:
            with self.subTest(skill=skill):
                text = (root / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("voice_model_identity.py", text)
                self.assertIn("--write", text)
                self.assertIn("--submission", text)

    def test_no_scoped_use_or_existence_test_names_the_bare_relative_path(self) -> None:
        root = Path(__file__).resolve().parent.parent
        occurrences: list[tuple[str, str]] = []
        for skill in identity.COMPLETION_GRADERS:
            for path in sorted((root / "skills" / skill).rglob("*.md")):
                text = path.read_text(encoding="utf-8")
                for line in text.splitlines():
                    if "scratch/voice-model.md" in line:
                        occurrences.append((skill, line.strip()))
        self.assertEqual(
            occurrences,
            [
                (
                    "practicum-case-study",
                    "to imitate. **What it builds is `scratch/voice-model.md`** — gitignored, one per clinician, built",
                )
            ],
        )
        shared = (
            root / "skills" / "_shared" / "reference" / "voice.md"
        ).read_text(encoding="utf-8")
        absence_rule = shared.split("**Where there is no model.**", 1)[1].split(
            "**A run does not stop", 1
        )[0]
        self.assertIn("repo_root.canonical_voice_model()", absence_rule)
        self.assertNotIn("scratch/voice-model.md", absence_rule)

    def test_graders_and_claude_point_to_one_limits_object_without_copying_rows(self) -> None:
        root = Path(__file__).resolve().parent.parent
        readers = [
            root / "tools" / f"{module_name}.py"
            for module_name in identity.COMPLETION_GRADERS.values()
        ]
        readers.append(root / "CLAUDE.md")
        for path in readers:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("voice_model_identity.DECLARED_LIMITS", text)
                for key, reason in identity.DECLARED_LIMITS:
                    self.assertNotIn(key, text)
                    self.assertNotIn(reason, text)


if __name__ == "__main__":
    unittest.main()
