"""Behavior tests for the post-checkout mirror repair hook."""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "tools" / "hooks"


@unittest.skipUnless(shutil.which("git"), "git is required")
class PostCheckoutRepairsOnlyNewWorktrees(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.base = Path(self._tmp.name).resolve()
        self.main = self.base / "main"
        self.main.mkdir()
        self.run_git("init", cwd=self.main)
        self.run_git(
            "config", "user.email", "fixture@example.invalid", cwd=self.main
        )
        self.run_git("config", "user.name", "Fixture", cwd=self.main)

        mirror = self.main / "tools" / "skills_mirror.py"
        mirror.parent.mkdir(parents=True)
        mirror.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "Path.cwd().joinpath('repair.log').write_text("
            "' '.join(sys.argv[1:]), encoding='utf-8')\n",
            encoding="utf-8",
        )
        self.run_git("add", "tools/skills_mirror.py", cwd=self.main)
        self.run_git("commit", "-m", "fixture", cwd=self.main)
        self.run_git("config", "core.hooksPath", str(HOOKS), cwd=self.main)

    def tearDown(self):
        self._tmp.cleanup()

    def run_git(self, *args: str, cwd: Path):
        return subprocess.run(
            ["git", *args], cwd=cwd, check=True, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        )

    def test_branch_switch_is_quiet_and_new_worktree_repairs(self):
        self.run_git("checkout", "-b", "ordinary", cwd=self.main)
        self.assertFalse((self.main / "repair.log").exists())

        worktree = self.base / "worktree"
        self.run_git(
            "worktree", "add", "-b", "new-worktree", str(worktree), cwd=self.main
        )

        self.assertEqual(
            (worktree / "repair.log").read_text(encoding="utf-8"),
            "--repair --quiet",
        )


if __name__ == "__main__":
    unittest.main()
