"""Public-contract tests for the approved-run guard installer. #1398."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import install_run_status_guard as installer


class InstallerContract(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.source = self.root / "worktree"
        self.owning = self.root / "owning"
        for root in (self.source, self.owning):
            (root / "tools").mkdir(parents=True)
            (root / "tools" / "run_status_stop_hook.py").write_text(
                "tracked hook\n", encoding="utf-8"
            )
        (self.home / ".codex").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def install(self) -> None:
        installer.install(
            home=self.home,
            source_root=self.source,
            owning_checkout=self.owning,
        )

    def commands(self) -> list[str]:
        document = json.loads(
            (self.home / ".codex" / "hooks.json").read_text(encoding="utf-8")
        )
        return [
            hook["command"]
            for registration in document["hooks"]["Stop"]
            for hook in registration["hooks"]
        ]

    def test_install_preserves_existing_hooks_and_is_idempotent(self) -> None:
        existing = {
            "hooks": {
                "Stop": [
                    {"hooks": [{"type": "command", "command": "python grilling_stop_hook.py"}]}
                ]
            }
        }
        (self.home / ".codex" / "hooks.json").write_text(
            json.dumps(existing), encoding="utf-8"
        )

        self.install()
        self.install()

        commands = self.commands()
        self.assertIn("python grilling_stop_hook.py", commands)
        self.assertEqual(
            1, sum("run_status_stop_hook.py" in command for command in commands)
        )
        self.assertTrue(any(str(self.owning.resolve()) in command for command in commands))

    def test_an_unmerged_owning_copy_refuses_before_writing_user_config(self) -> None:
        (self.owning / "tools" / "run_status_stop_hook.py").write_text(
            "older hook\n", encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "owning checkout"):
            self.install()

        self.assertFalse((self.home / ".codex" / "hooks.json").exists())


if __name__ == "__main__":
    unittest.main()
