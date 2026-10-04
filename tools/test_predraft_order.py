"""Public pre-draft command contracts, with synthetic coursework. #1404.

phi-scan: synthetic
"""
import json
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import project_context
import voice_model_identity
import repo_root
import coursework_run


class FirstObservation(unittest.TestCase):
    def test_project_command_records_a_late_draft_before_refusing(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "atlas-discussion"
            run.mkdir()
            (run / "project-context.md").write_text(
                "PROJECT-CONTEXT: none - no project material applies\nCONFIRMED: 2026-10-03\n",
                encoding="utf-8",
            )
            (run / "post.md").write_text("draft", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                status = project_context.main([str(run), "--write", "--submission", "atlas-discussion-2026-10-03"])
            self.assertEqual(status, 1)
            self.assertIn("ORDER-OBSERVATION:", (run / "project-context.md").read_text(encoding="utf-8"))
            grade = project_context.completion_gate(run, "atlas-discussion-2026-10-03")
            self.assertTrue(grade.finding)
            self.assertIn("draft present", grade.report)




class CourseworkCommands(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.owner = self.root / "owning"
        self.committer = self.root / "committing"
        (self.committer / "tools").mkdir(parents=True)
        self.run = self.owner / "scratch" / "runs" / "atlas-discussion"
        self.run.mkdir(parents=True)
        for module, name, value in (
            (coursework_run, "scratch_root", self.owner / "scratch"),
            (coursework_run, "output_root", self.owner / "output"),
            (repo_root, "canonical_voice_model", repo_root.VoiceModelResolution(self.owner / "scratch" / "voice-model.md", None, False)),
        ):
            patch = mock.patch.object(module, name, return_value=value)
            patch.start()
            self.addCleanup(patch.stop)
        patch = mock.patch.object(coursework_run, "__file__", str(self.committer / "tools" / "coursework_run.py"))
        patch.start()
        self.addCleanup(patch.stop)
        self.reset()

    def reset(self):
        (self.run / "project-context.md").write_text(
            "PROJECT-CONTEXT: none - no project material applies\nCONFIRMED: 2026-10-03\n", encoding="utf-8")
        (self.run / "voice-model-identity.json").unlink(missing_ok=True)

    def supplied(self, key):
        path = self.run / "voice-reads" / key / "supplied-voice.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")

    def command(self, module, key):
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            return module.main([str(self.run), "--write", "--submission", key])

    def plant(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic prose", encoding="utf-8")

    def waive(self, path):
        record = self.run / "project-context.md"
        text = record.read_text(encoding="utf-8")
        record.write_text("ORDER-WAIVE: " + str(path) + " - opening paragraph drafted; proceed, per the clinician\n" + text, encoding="utf-8")

    def test_every_skill_observes_absent_then_late_then_path_matched_waiver(self):
        cases = (
            ("critique.md", self.run / "critique.md"),
            ("response-maren.md", self.run / "response-maren.md"),
            ("atlas-case-study-2026-10-03", self.owner / "output" / "case-studies" / "atlas-case-study-2026-10-03.md"),
            ("atlas-discussion-2026-10-03", self.run / "post.md"),
            ("atlas-course-assignment-2026-10-03", self.run / "writer" / "atlas-course-assignment-2026-10-03" / "assignment.json"),
        )
        for key, draft in cases:
            for module in (project_context, voice_model_identity):
                with self.subTest(key=key, gate=module.__name__):
                    self.reset()
                    self.supplied(key)
                    self.assertEqual(self.command(module, key), 0)
                    self.plant(draft)
                    self.assertEqual(self.command(module, key), 0, "a clean first observation survives drafting")
                    self.assertFalse(module.completion_gate(self.run, key).finding)
                    self.reset()
                    self.assertEqual(self.command(module, key), 1, "a late first observation is a finding")
                    self.assertTrue(module.completion_gate(self.run, key).finding)
                    self.assertIn("draft present", module.completion_gate(self.run, key).report)
                    self.waive(self.root / "different.md")
                    self.assertEqual(self.command(module, key), 1)
                    self.waive(draft)
                    self.assertEqual(self.command(module, key), 0)
                    result = module.completion_gate(self.run, key)
                    self.assertFalse(result.finding)
                    self.assertIn("waived observations: 1", result.report)
                    draft.unlink()
                    # The observation retains the original late path after the file moves away.
                    self.assertIn(str(draft), project_context.order_observations(self.run)[key]["paths"] if module is project_context else json.loads((self.run / module.RECORD_NAME).read_text(encoding="utf-8"))["observations"][key]["paths"])

    def test_late_observation_cannot_be_laundered_by_a_rerun(self):
        key = "response-maren.md"
        draft = self.run / key
        self.supplied(key)
        self.plant(draft)
        for module in (project_context, voice_model_identity):
            self.assertEqual(self.command(module, key), 1)
        draft.unlink()
        for module in (project_context, voice_model_identity):
            self.assertEqual(self.command(module, key), 1)

    def test_reply_two_is_not_late_because_reply_one_exists(self):
        self.plant(self.run / "response-maren.md")
        key = "response-rowan.md"
        self.supplied(key)
        for module in (project_context, voice_model_identity):
            self.assertEqual(self.command(module, key), 0)
            self.assertFalse(module.completion_gate(self.run, key).finding)

    def test_missing_capture_refuses_without_writing_identity(self):
        self.assertEqual(self.command(voice_model_identity, "critique.md"), 1)
        self.assertFalse((self.run / voice_model_identity.RECORD_NAME).exists())

    def test_staging_is_keyed_and_observed_in_both_scratch_roots(self):
        key = "critique.md"
        self.supplied(key)
        for root in (self.owner, self.committer):
            other = root / "scratch" / "sessions" / "any-pass" / "response-other.md" / "draft.md"
            self.plant(other)
            for module in (project_context, voice_model_identity):
                self.reset()
                self.assertEqual(self.command(module, key), 0)
            draft = root / "scratch" / "sessions" / "any-pass" / key / "draft.md"
            self.plant(draft)
            for module in (project_context, voice_model_identity):
                self.reset()
                self.assertEqual(self.command(module, key), 1)
                self.assertIn(str(draft), module.completion_gate(self.run, key).report)
            draft.unlink()

    def test_completion_requires_the_first_observation_for_each_key(self):
        for module in (project_context, voice_model_identity):
            self.assertTrue(module.completion_gate(self.run, "critique.md").finding)

    def test_assignment_output_and_deck_writer_are_watched(self):
        key = "atlas-course-assignment-2026-10-03"
        self.supplied(key)
        for draft in (
            self.run / "writer" / key / "pass-a" / "draft.pptx",
            self.owner / "output" / "course-assignments" / (key + ".pptx"),
            self.owner / "output" / "course-assignments" / (key + ".docx"),
        ):
            self.plant(draft)
            for module in (project_context, voice_model_identity):
                self.reset()
                self.assertEqual(self.command(module, key), 1)
            draft.unlink()

    def test_both_reply_observations_are_graded_at_completion(self):
        for key in ("response-maren.md", "response-rowan.md"):
            self.supplied(key)
            if key == "response-rowan.md":
                self.plant(self.run / key)
            for module in (project_context, voice_model_identity):
                self.assertEqual(self.command(module, key), int(key == "response-rowan.md"))
        for module in (project_context, voice_model_identity):
            self.assertTrue(module.completion_gate(self.run, "response-maren.md,response-rowan.md").finding)
        self.waive(self.run / "response-rowan.md")
        for module in (project_context, voice_model_identity):
            result = module.completion_gate(self.run, "response-maren.md,response-rowan.md")
            self.assertFalse(result.finding)
            self.assertIn("waived observations: 1", result.report)


if __name__ == "__main__":
    unittest.main()
