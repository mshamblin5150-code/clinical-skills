"""Behavior tests for the post-checkout mirror repair hook.

The fixture configures ``core.hooksPath`` the way the setup skill documents it,
as the relative ``tools/hooks``, with the hook files committed inside the
fixture repository. Under that setting each checkout runs the hook files on its
own branch (#1880).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent.parent
POST_CHECKOUT = ROOT / "tools" / "hooks" / "post-checkout"
DOCUMENTED_HOOKS_PATH = "tools/hooks"
PRE_COMMIT_LOGGER = (
    "#!/bin/sh\n"
    'echo "{label}" > "$(git rev-parse --show-toplevel)/pre-commit.log"\n'
    "exit 0\n"
)


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
        hooks = self.main / DOCUMENTED_HOOKS_PATH
        hooks.mkdir(parents=True)
        shutil.copyfile(POST_CHECKOUT, hooks / "post-checkout")
        self.write_pre_commit(self.main, "main")
        self.run_git("add", "tools", cwd=self.main)
        self.run_git("commit", "-m", "fixture", cwd=self.main)
        self.run_git(
            "config", "core.hooksPath", DOCUMENTED_HOOKS_PATH, cwd=self.main
        )

    def tearDown(self):
        self._tmp.cleanup()

    def run_git(self, *args: str, cwd: Path):
        return subprocess.run(
            ["git", *args], cwd=cwd, check=True, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        )

    def write_pre_commit(self, checkout: Path, label: str) -> None:
        (checkout / DOCUMENTED_HOOKS_PATH / "pre-commit").write_text(
            PRE_COMMIT_LOGGER.format(label=label), encoding="utf-8", newline="\n"
        )

    def add_worktree(self) -> Path:
        worktree = self.base / "worktree"
        self.run_git(
            "worktree", "add", "-b", "new-worktree", str(worktree), cwd=self.main
        )
        return worktree

    def test_branch_switch_is_quiet_and_new_worktree_repairs(self):
        self.run_git("checkout", "-b", "ordinary", cwd=self.main)
        self.assertFalse((self.main / "repair.log").exists())

        worktree = self.add_worktree()

        self.assertEqual(
            (worktree / "repair.log").read_text(encoding="utf-8"),
            "--repair --quiet",
        )

    def test_a_worktree_commit_runs_that_worktrees_hook_files(self):
        """The logger writes into the committing tree, so only its label discriminates.

        With an absolute hooksPath naming the main checkout, this commit would
        run main's hook file and log ``main``.
        """
        worktree = self.add_worktree()
        self.write_pre_commit(worktree, "worktree")
        (worktree / "note.txt").write_text("x\n", encoding="utf-8")
        self.run_git("add", "note.txt", cwd=worktree)
        self.run_git("commit", "-m", "worktree commit", cwd=worktree)

        self.assertEqual(
            (worktree / "pre-commit.log").read_text(encoding="utf-8").strip(),
            "worktree",
        )


class TheFixtureUsesTheDocumentedSetting(unittest.TestCase):
    """Every setup command the repository documents writes the value tested above."""

    DOCUMENTS = (
        "skills/setup-clinical-skills/SKILL.md",
        "README.md",
        "CLAUDE.md",
    )
    SETTING = re.compile(r"git config core\.hooksPath ([^\s`]+)")

    def test_each_documented_setup_command_writes_the_tested_value(self):
        for name in self.DOCUMENTS:
            with self.subTest(document=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                values = self.SETTING.findall(text)
                self.assertTrue(values, f"{name} documents no hooksPath command")
                self.assertEqual(set(values), {DOCUMENTED_HOOKS_PATH})


if __name__ == "__main__":
    unittest.main()
