"""Tests for the corpus resolver -- issue #93.

Every case here is built in a temp directory, because the thing under test is
*which checkout you are standing in* and the suite has to be able to stand in
both. A test that read the real tree would answer only for the tree it happened
to run in, which is the defect itself.

The shapes that matter are the two the resolver has to tell apart: a plain clone,
whose ``.git`` is a directory, and a worktree, whose ``.git`` is a *file* naming
``<main>/.git/worktrees/<name>``. Getting the second one wrong is what #93 is --
``Path(__file__).resolve().parent.parent`` stops at the worktree, so the corpus
layer looks for ``scratch/`` somewhere it has never been.
"""

import tempfile
import unittest
from pathlib import Path

from repo_root import main_repo_root, scratch_root


class Checkouts(unittest.TestCase):
    """Builds a main checkout with a worktree hanging off it, the way this repo is."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.main = self.root / "clinical_skills"
        (self.main / "tools").mkdir(parents=True)
        (self.main / ".git" / "worktrees" / "ticket-93").mkdir(parents=True)
        (self.main / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    def worktree(self, pointer: str) -> Path:
        """A worktree whose ``.git`` file names its gitdir however ``pointer`` says."""
        tree = self.main / ".claude" / "worktrees" / "ticket-93"
        (tree / "tools").mkdir(parents=True)
        (tree / ".git").write_text(f"gitdir: {pointer}\n", encoding="utf-8")
        return tree


class MainRepoRoot(Checkouts):
    def test_a_worktree_resolves_to_the_checkout_that_owns_it(self):
        """The whole ticket. Stop at the worktree and scratch/ is never found."""
        gitdir = self.main / ".git" / "worktrees" / "ticket-93"
        tree = self.worktree(gitdir.as_posix())
        self.assertEqual(main_repo_root(tree / "tools"), self.main)

    def test_a_relative_pointer_resolves_against_the_worktree(self):
        """Git may write the gitdir relative. Read literally it lands nowhere."""
        tree = self.worktree("../../../.git/worktrees/ticket-93")
        self.assertEqual(main_repo_root(tree / "tools"), self.main)

    def test_a_plain_checkout_is_its_own_main_root(self):
        self.assertEqual(main_repo_root(self.main / "tools"), self.main)

    def test_a_directory_that_is_no_checkout_at_all_is_its_own_root(self):
        """An exported tree with no .git. There is nothing to walk up to, and
        inventing a parent would send the scan somewhere it was never pointed."""
        plain = self.root / "exported"
        (plain / "tools").mkdir(parents=True)
        self.assertEqual(main_repo_root(plain / "tools"), plain)

    def test_a_git_file_that_points_somewhere_unexpected_stays_put(self):
        """A submodule's .git file is also a pointer, and it does not name a
        worktree. Only the <main>/.git/worktrees/<name> shape is followed."""
        tree = self.worktree((self.root / "elsewhere" / "modules" / "thing").as_posix())
        self.assertEqual(main_repo_root(tree / "tools"), tree)


class ScratchRoot(Checkouts):
    """``scratch/`` is the corpus, and it lives in exactly one checkout."""

    def test_from_a_worktree_it_points_at_the_main_checkout(self):
        gitdir = self.main / ".git" / "worktrees" / "ticket-93"
        tree = self.worktree(gitdir.as_posix())
        self.assertEqual(scratch_root(tree / "tools"), self.main / "scratch")

    def test_from_the_main_checkout_it_points_at_itself(self):
        self.assertEqual(scratch_root(self.main / "tools"), self.main / "scratch")

    def test_it_does_not_require_the_directory_to_exist(self):
        """Absence is the caller's finding to make and report -- #93 is a ticket
        about a layer going quiet, so the resolver must not quietly return None."""
        self.assertFalse(scratch_root(self.main / "tools").exists())
        self.assertEqual(scratch_root(self.main / "tools").name, "scratch")


if __name__ == "__main__":
    unittest.main()
