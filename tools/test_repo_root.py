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

from repo_root import (
    ForeignCheckout,
    InsideCheckout,
    enclosing_checkout,
    ensure_main_checkout,
    ensure_outside_checkout,
    main_repo_root,
    output_root,
    scratch_root,
)


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


class OutputRoot(Checkouts):
    """Finished submissions share the main checkout across worktrees -- #417."""

    def test_from_a_worktree_it_points_at_the_main_checkout(self):
        gitdir = self.main / ".git" / "worktrees" / "ticket-93"
        tree = self.worktree(gitdir.as_posix())
        self.assertEqual(output_root(tree / "tools"), self.main / "output")

    def test_it_does_not_require_the_directory_to_exist(self):
        self.assertFalse(output_root(self.main / "tools").exists())
        self.assertEqual(output_root(self.main / "tools").name, "output")


class EnclosingCheckout(Checkouts):
    """The write guard's detection rule -- issue #176.

    Three modules used to hold three answers to *is this path inside a git
    checkout*, and one of them compared against a list of known roots rather than
    walking up for a ``.git`` entry. The list-based one misses a sibling worktree,
    which under ``.claude/worktrees/`` is the ordinary case here rather than an
    exotic one. The walk is the rule that survived.
    """

    def test_a_path_under_a_checkout_names_that_checkout(self):
        self.assertEqual(
            enclosing_checkout(self.main / "reference" / "guidelines.sqlite"), self.main
        )

    def test_the_checkout_root_itself_is_inside_it(self):
        """A directory target may *be* the repo -- ``--out C:/codeing/clinical_skills``.
        Walking only the parents would bless it."""
        self.assertEqual(enclosing_checkout(self.main), self.main)

    def test_a_path_under_no_checkout_at_all_names_none(self):
        self.assertIsNone(enclosing_checkout(self.root / "guidelines-index" / "g.sqlite"))

    def test_a_sibling_worktree_is_found_and_not_only_the_one_we_stand_in(self):
        """The whole reason the known-roots rule was the weaker of the two. A
        worktree's ``.git`` is a *file*, so this has to test existence rather than
        directory-ness."""
        tree = self.worktree((self.main / ".git" / "worktrees" / "ticket-93").as_posix())
        self.assertEqual(enclosing_checkout(tree / "guidelines-text"), tree)

    def test_a_path_that_only_shares_a_name_prefix_is_outside(self):
        """``clinical_skills-notes`` is not inside ``clinical_skills``. A string
        prefix would say it is, which is the case the known-roots rule was
        careful about and which the walk gets for free."""
        self.assertIsNone(enclosing_checkout(self.root / "clinical_skills-notes" / "g.sqlite"))

    def test_a_permitted_directory_inside_a_checkout_is_allowed(self):
        """``name_index`` writes a list of patient names into the repo's own
        ``scratch/`` on purpose: it is gitignored and ``phi_scan``'s path layer
        refuses a commit from it even under ``git add -f``. So the shared rule
        takes a parameter rather than being one rule."""
        scratch = self.main / "scratch"
        self.assertIsNone(
            enclosing_checkout(scratch / "name-index.json", permitted=[scratch])
        )

    def test_a_directory_merely_sharing_the_permitted_name_is_not_permitted(self):
        """The permission is a resolved directory, never a path component. Keyed
        on the name it would bless somebody else's ``~/scratch/`` on a
        coincidence -- the narrowing ``name_index`` found on its first version."""
        self.assertIsNotNone(
            enclosing_checkout(
                self.main / "scratch" / "name-index.json",
                permitted=[self.main / "elsewhere"],
            )
        )

    def test_permission_does_not_reach_a_sibling_of_the_permitted_directory(self):
        """``scratch-old`` is not ``scratch``, for the name-prefix reason above."""
        self.assertIsNotNone(
            enclosing_checkout(
                self.main / "scratch-old" / "name-index.json",
                permitted=[self.main / "scratch"],
            )
        )

    def test_the_permitted_directory_need_not_exist(self):
        """``scratch/`` is gitignored, so a worktree has never had one. A guard
        that required it to exist would refuse the write that creates it."""
        scratch = self.main / "scratch"
        self.assertFalse(scratch.exists())
        self.assertIsNone(enclosing_checkout(scratch / "name-index.json", permitted=[scratch]))


class EnsureOutsideCheckout(Checkouts):
    """The raising wrapper. One exception type, so a caller can handle *refused*
    uniformly -- the three sites used to raise ``SystemExit``, ``InsideRepo`` and
    nothing at all."""

    def test_it_returns_the_resolved_target_when_the_path_is_outside(self):
        target = self.root / "guidelines-index" / "g.sqlite"
        self.assertEqual(ensure_outside_checkout(target), target.resolve())

    def test_it_accepts_a_string(self):
        target = self.root / "guidelines-index" / "g.sqlite"
        self.assertEqual(ensure_outside_checkout(str(target)), target.resolve())

    def test_it_raises_inside_a_checkout(self):
        with self.assertRaises(InsideCheckout):
            ensure_outside_checkout(self.main / "reference" / "g.sqlite")

    def test_the_refusal_carries_the_target_and_the_checkout_it_landed_in(self):
        """Each caller's reason for refusing differs -- #87's copyright, a
        worktree's materialization, a list of patient names -- so the exception
        carries the facts and the caller supplies the sentence."""
        with self.assertRaises(InsideCheckout) as refused:
            ensure_outside_checkout(self.main / "reference" / "g.sqlite")
        self.assertEqual(refused.exception.checkout, self.main)
        self.assertEqual(
            refused.exception.target, (self.main / "reference" / "g.sqlite").resolve()
        )

    def test_the_callers_own_detail_reaches_the_message(self):
        with self.assertRaises(InsideCheckout) as refused:
            ensure_outside_checkout(self.main, detail="This file holds the society's text. #87.")
        self.assertIn("This file holds the society's text. #87.", str(refused.exception))

    def test_a_refusal_names_both_paths_without_a_detail(self):
        with self.assertRaises(InsideCheckout) as refused:
            ensure_outside_checkout(self.main / "reference")
        message = str(refused.exception)
        self.assertIn(str(self.main), message)
        self.assertIn(str((self.main / "reference").resolve()), message)

    def test_it_is_a_value_error(self):
        """``guidelines_index`` raised a ``ValueError`` subclass and the other two
        raised ``SystemExit``. A library-level refusal is the former; the command
        lines convert at their own boundary."""
        self.assertTrue(issubclass(InsideCheckout, ValueError))

    def test_permission_passes_through(self):
        scratch = self.main / "scratch"
        self.assertEqual(
            ensure_outside_checkout(scratch / "name-index.json", permitted=[scratch]),
            (scratch / "name-index.json").resolve(),
        )


class EnsureMainCheckout(Checkouts):
    """A finished submission may be external, but never in a disposable worktree."""

    def test_it_allows_the_main_checkout(self):
        target = self.main / "output" / "case-studies" / "draft.docx"
        self.assertEqual(ensure_main_checkout(target, self.main / "tools"), target.resolve())

    def test_it_allows_a_path_outside_every_checkout(self):
        target = self.root / "rendered" / "draft.docx"
        self.assertEqual(ensure_main_checkout(target, self.main / "tools"), target.resolve())

    def test_it_refuses_a_foreign_worktree(self):
        tree = self.worktree((self.main / ".git" / "worktrees" / "ticket-93").as_posix())
        target = tree / "output" / "case-studies" / "draft.docx"
        with self.assertRaises(ForeignCheckout) as refused:
            ensure_main_checkout(target, self.main / "tools")
        self.assertEqual(refused.exception.target, target.resolve())
        self.assertEqual(refused.exception.expected, self.main)
        self.assertIn(str(self.main / "output"), str(refused.exception))

    def test_the_two_opposite_policies_have_sibling_exception_types(self):
        self.assertTrue(issubclass(ForeignCheckout, ValueError))
        self.assertFalse(issubclass(ForeignCheckout, InsideCheckout))


if __name__ == "__main__":
    unittest.main()
