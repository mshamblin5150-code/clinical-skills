"""The user settings check reports access without changing settings. #1500."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import claude_output_access


class OutputAccess(unittest.TestCase):
    def test_settings_check_statuses_and_read_only_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            settings = home / ".claude" / "settings.json"
            settings.parent.mkdir()
            output = home / "owning checkout" / "output"
            for payload, expected in (
                ({"permissions": {"additionalDirectories": [str(output)]}}, 0),
                ({"permissions": {"additionalDirectories": [str(output / ".." / "output")]}}, 0),
                ({"permissions": {"additionalDirectories": [str(home / "worktree" / "output")]}}, 1),
                ({}, 1),
                ({"permissions": {"additionalDirectories": []}}, 1),
            ):
                with self.subTest(payload=payload):
                    settings.write_text(json.dumps(payload), encoding="utf-8")
                    before = settings.read_bytes()
                    result = io.StringIO()
                    with mock.patch("claude_output_access.Path.home", return_value=home), mock.patch("claude_output_access.repo_root.output_root", return_value=output), contextlib.redirect_stdout(result):
                        self.assertEqual(expected, claude_output_access.main())
                    self.assertEqual(before, settings.read_bytes())
                    if expected == 1:
                        self.assertIn(json.dumps({"permissions": {"additionalDirectories": [str(output.resolve())]}}, ensure_ascii=False), result.getvalue())

    def test_unreadable_or_invalid_settings_exit_2_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            settings = home / ".claude" / "settings.json"
            settings.parent.mkdir()
            for contents in (None, "{", "[]", '{"permissions": []}', '{"permissions": {"additionalDirectories": "folder"}}', '{"permissions": {"additionalDirectories": [42]}}'):
                with self.subTest(contents=contents):
                    if contents is not None:
                        settings.write_text(contents, encoding="utf-8")
                    result = io.StringIO()
                    with mock.patch("claude_output_access.Path.home", return_value=home), mock.patch("claude_output_access.repo_root.output_root", return_value=home / "output"), contextlib.redirect_stdout(result):
                        self.assertEqual(2, claude_output_access.main())
                    if contents is None:
                        self.assertFalse(settings.exists())
                    else:
                        self.assertEqual(contents, settings.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
