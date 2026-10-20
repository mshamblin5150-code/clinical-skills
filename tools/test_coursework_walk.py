"""Public draft-observation commands refuse incomplete walks without storing them.

All paths and draft content are synthetic.
"""

import artifact_lock_test_support
import io
import json
import os
import subprocess
import tempfile
import unittest
import artifact_lock_test_support
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import coursework_run
import project_context
import repo_root
import tree_walk
import voice_model_identity
from tree_walk_test_support import denied_listing


class DraftWalkCommands(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.run = self.root / "runs" / "atlas-discussion"
        self.run.mkdir(parents=True)
        self.key = "atlas-discussion-2026-10-19.md"
        supplied = coursework_run.voice_records_directory(self.run, self.key)
        supplied.mkdir(parents=True)
        (supplied / "supplied-voice.json").write_text("{}", encoding="utf-8")
        self.context = self.run / project_context.RECORD_NAME
        self.context.write_text("PROJECT-CONTEXT: none - synthetic\n", encoding="utf-8")
        self.resolved = repo_root.VoiceModelResolution(self.root / "model.md", "a" * 64, True)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(coursework_run, "scratch_root", return_value=self.root))
        self.stack.enter_context(patch.object(repo_root, "canonical_voice_model", return_value=self.resolved))
        self.stack.enter_context(patch.object(project_context, "_write_context_record", return_value=project_context.GateResult(0, "context clean")))
        self.stack.enter_context(patch.object(project_context, "retain_heading_context"))

    def command(self, module):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            status = module.main([str(self.run), "--write", "--submission", self.key])
        return status, output.getvalue()

    def assert_unread_refusal(self, denied):
        original = os.scandir

        def read(path):
            if Path(path) == denied:
                raise PermissionError("synthetic denial")
            return original(path)

        for module in (project_context, voice_model_identity):
            with self.subTest(command=module.__name__):
                before = self.context.read_bytes()
                with patch.object(tree_walk.os, "scandir", side_effect=read):
                    status, report = self.command(module)
                self.assertEqual(status, 2, report)
                self.assertIn("1 draft subfolder(s) unreadable", report)
                self.assertIn("restore access and rerun", report)
                self.assertEqual(self.context.read_bytes(), before)
                self.assertFalse((self.run / voice_model_identity.RECORD_NAME).exists())
                self.assertNotIn(str(denied), report)

    def test_unreadable_run_subfolder_records_no_observation(self):
        denied = self.run / "private-folder"
        denied.mkdir()
        self.assert_unread_refusal(denied)

    def test_unreadable_session_subfolder_records_no_observation(self):
        denied = self.root / "sessions" / "sitting" / self.key / "private-folder"
        denied.mkdir(parents=True)
        self.assert_unread_refusal(denied)

    def test_unrelated_nested_session_tree_is_not_walked(self):
        denied = self.root / "sessions" / "sitting" / "other-key" / "private"
        denied.mkdir(parents=True)
        original = os.scandir

        def read(path):
            if Path(path) == denied:
                raise AssertionError("unrelated nested tree was entered")
            return original(path)

        with patch.object(tree_walk.os, "scandir", side_effect=read):
            for module in (project_context, voice_model_identity):
                status, report = self.command(module)
                self.assertEqual(status, 0, report)

    def test_unreadable_session_selection_refuses_before_observation(self):
        sitting = self.root / "sessions" / "sitting"
        sitting.mkdir(parents=True)
        original = Path.iterdir

        def read(path):
            if path == sitting:
                raise PermissionError("synthetic denial")
            return original(path)

        with patch.object(Path, "iterdir", read):
            for module in (project_context, voice_model_identity):
                status, report = self.command(module)
                self.assertEqual(status, 2, report)
                self.assertIn("1 draft subfolder(s) unreadable", report)
        self.assertNotIn("ORDER-OBSERVATION:", self.context.read_text(encoding="utf-8"))
        self.assertFalse((self.run / voice_model_identity.RECORD_NAME).exists())

    def test_linked_session_parent_is_never_entered(self):
        sessions = self.root / "sessions"
        sessions.mkdir()
        target = self.root / "elsewhere"
        (target / self.key).mkdir(parents=True)
        (target / self.key / "draft.txt").touch()
        try:
            (sessions / "linked").symlink_to(target, target_is_directory=True)
        except OSError as error:
            self.skipTest(str(error))
        for module in (project_context, voice_model_identity):
            status, report = self.command(module)
            self.assertEqual(status, 0, report)
            self.assertIn("draft links not entered: 1", report)

    @unittest.skipUnless(os.name == "nt", "Windows ACL denial")
    def test_native_denied_subfolder_refuses_both_commands(self):
        denied = self.run / "private-folder"
        denied.mkdir()
        before = self.context.read_bytes()
        with denied_listing(denied):
            for module in (project_context, voice_model_identity):
                status, report = self.command(module)
                self.assertEqual(status, 2, report)
                self.assertIn("1 draft subfolder(s) unreadable", report)
        self.assertEqual(self.context.read_bytes(), before)
        self.assertFalse((self.run / voice_model_identity.RECORD_NAME).exists())

    def test_writer_patterns_include_direct_and_deep_files(self):
        key = "atlas-course-assignment-2026-10-19.pptx"
        direct = self.run / "writer" / key / "draft.json"
        deep = direct.parent / "deeper" / "draft.pptx"
        deep.parent.mkdir(parents=True)
        direct.touch()
        deep.touch()
        self.assertEqual(coursework_run.draft_files(self.run, key), tuple(sorted((direct, deep))))

    def test_exact_run_filename_does_not_match_a_nested_namesake(self):
        nested = self.run / "private" / "post.md"
        nested.parent.mkdir()
        nested.touch()
        self.assertEqual(coursework_run.draft_files(self.run, self.key), ())

    def assert_link_commands(self):
        for module in (project_context, voice_model_identity):
            with self.subTest(command=module.__name__):
                status, report = self.command(module)
                self.assertEqual(status, 0, report)
                self.assertIn("draft links not entered: 3", report)
        identity = json.loads((self.run / voice_model_identity.RECORD_NAME).read_text(encoding="utf-8"))
        self.assertEqual(identity["observations"], {self.key: {"paths": []}})
        self.assertNotIn("links", self.context.read_text(encoding="utf-8"))

    def test_symbolic_links_are_counted_at_write_time_only(self):
        for name, target in (("live", self.root), ("dangling", self.root / "absent"), ("ancestor", self.run)):
            try:
                (self.run / name).symlink_to(target, target_is_directory=True)
            except OSError as error:
                self.skipTest(str(error))
        self.assert_link_commands()

    @unittest.skipUnless(os.name == "nt", "Windows junctions")
    def test_live_dangling_ancestor_junction_commands(self):
        for name, target in (("live", self.root), ("dangling", self.root / "absent"), ("ancestor", self.run)):
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(self.run / name), str(target)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_link_commands()

    def test_damaged_identity_wins_over_unreadable_tree(self):
        (self.run / voice_model_identity.RECORD_NAME).write_text("broken", encoding="utf-8")
        with patch.object(coursework_run, "draft_files", side_effect=AssertionError("must not walk")):
            status, _ = self.command(voice_model_identity)
        self.assertEqual(status, 1)

    def test_damaged_context_wins_over_unreadable_tree(self):
        self.context.write_text("PROJECT-CONTEXT: none\tbroken\n", encoding="utf-8")
        with patch.object(coursework_run, "draft_files", side_effect=AssertionError("must not walk")):
            status, _ = self.command(project_context)
        self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
