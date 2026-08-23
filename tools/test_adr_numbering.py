"""ADR numbering is unique on disk and allocation reads every worktree."""

import subprocess
import sys
import shutil
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import adr_next


ADR_NEXT = Path(__file__).with_name("adr_next.py")
PRE_COMMIT = Path(__file__).with_name("hooks") / "pre-commit"


def adr_stems_are_unique_on_disk(adr_dir: Path) -> bool:
    """Independent merge assertion: first four filename characters, Markdown only.

    It deliberately shares no matcher with ``adr_next``. A production extractor
    that matches no files, or only conventional ``NNNN-slug.md`` files, must not
    be able to make the merge assertion pass by construction.
    """

    stems = [
        path.name[:4]
        for path in adr_dir.iterdir()
        if path.is_file()
        and path.suffix == ".md"
        and len(path.name) >= 4
        and path.name[:4].isdecimal()
    ]
    return len(stems) == len(set(stems))


def git(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )


class TempGitRepository(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve() / "checkout"
        self.root.mkdir()
        git(self.root, "init", "--initial-branch=main")
        git(self.root, "config", "user.email", "tests@example.invalid")
        git(self.root, "config", "user.name", "ADR tests")
        (self.root / "docs" / "adr").mkdir(parents=True)
        (self.root / "docs" / "adr" / "0003-existing.md").write_text(
            "# Existing\n", encoding="utf-8"
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "fixture")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def add_worktree(self, name: str = "other") -> Path:
        worktree = self.root.parent / name
        git(self.root, "worktree", "add", "--detach", str(worktree))
        return worktree

    def run_command(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ADR_NEXT), *arguments],
            cwd=self.root,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )


class AdrNumberUniquenessTests(unittest.TestCase):
    def test_a_real_duplicate_makes_the_predicate_fail(self) -> None:
        with TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            (adr_dir / "0007.md").write_text("# First\n", encoding="utf-8")
            (adr_dir / "0007-second-record.md").write_text("# Second\n", encoding="utf-8")

            self.assertFalse(adr_next.adr_numbers_are_unique(adr_dir))
            self.assertFalse(adr_stems_are_unique_on_disk(adr_dir))

    def test_the_real_adr_directory_is_unique(self) -> None:
        self.assertTrue(adr_stems_are_unique_on_disk(adr_next.REPO_ROOT / "docs" / "adr"))


class AdrPreCommitHookTests(unittest.TestCase):
    def test_the_cross_worktree_check_is_staged_only_and_advisory(self) -> None:
        hook = PRE_COMMIT.read_text(encoding="utf-8")

        self.assertIn("--diff-filter=ACMR", hook)
        self.assertIn("grep -q '^docs/adr/'", hook)
        self.assertIn('adr_next.py" --check-staged >&2 || true', hook)


class AdrNextCommandTests(TempGitRepository):
    def test_the_highest_number_across_worktrees_wins(self) -> None:
        other = self.add_worktree()
        (other / "docs" / "adr" / "0009-uncommitted.md").write_text(
            "# Uncommitted\n", encoding="utf-8"
        )

        finished = self.run_command("a record is corrected in place")

        self.assertEqual(finished.returncode, 0, finished.stderr)
        destination = self.root / "docs" / "adr" / "0010-a-record-is-corrected-in-place.md"
        self.assertTrue(destination.is_file())
        self.assertEqual(
            destination.read_text(encoding="utf-8"),
            "---\nstatus: proposed\n---\n\n# A record is corrected in place\n",
        )
        self.assertEqual(finished.stdout.strip(), "docs/adr/0010-a-record-is-corrected-in-place.md")
        self.assertIn("2 worktrees enumerated", finished.stderr)
        self.assertIn("0 unreadable", finished.stderr)

    def test_a_registered_worktree_whose_directory_is_gone_is_counted_and_named(self) -> None:
        other = self.add_worktree("registered-but-unreadable")
        shutil.rmtree(other)

        finished = self.run_command("a new decision")

        self.assertEqual(finished.returncode, 0, finished.stderr)
        self.assertIn("2 worktrees enumerated", finished.stderr)
        self.assertIn("1 unreadable", finished.stderr)
        self.assertIn(str(other), finished.stderr)

    def test_no_title_exits_two_without_writing(self) -> None:
        before = sorted((self.root / "docs" / "adr").iterdir())

        finished = self.run_command()

        self.assertEqual(finished.returncode, 2)
        self.assertEqual(sorted((self.root / "docs" / "adr").iterdir()), before)
        self.assertIn("usage:", finished.stderr)

    def test_an_absent_adr_directory_exits_two(self) -> None:
        shutil.rmtree(self.root / "docs" / "adr")

        finished = self.run_command("a new decision")

        self.assertEqual(finished.returncode, 2)
        self.assertIn("docs/adr is absent or unreadable", finished.stderr)

    def test_git_worktree_list_failure_exits_two(self) -> None:
        def fail_only_worktree_list(
            cwd: Path, *arguments: str
        ) -> subprocess.CompletedProcess[str]:
            if arguments == ("rev-parse", "--show-toplevel"):
                return subprocess.CompletedProcess(
                    ["git", *arguments], 0, stdout=str(self.root) + "\n", stderr=""
                )
            self.assertEqual(arguments, ("worktree", "list", "--porcelain"))
            return subprocess.CompletedProcess(
                ["git", *arguments],
                1,
                stdout="",
                stderr="forced worktree-list failure",
            )

        error = StringIO()
        with (
            patch.object(adr_next, "run_git", side_effect=fail_only_worktree_list),
            redirect_stderr(error),
        ):
            status = adr_next.main(["a new decision"])

        self.assertEqual(status, 2)
        self.assertIn("forced worktree-list failure", error.getvalue())

    def test_running_outside_a_checkout_exits_two(self) -> None:
        with TemporaryDirectory() as tmp:
            finished = subprocess.run(
                [sys.executable, str(ADR_NEXT), "a new decision"],
                cwd=tmp,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )

        self.assertEqual(finished.returncode, 2)
        self.assertIn("could not enumerate worktrees", finished.stderr)

    def test_an_existing_destination_exits_two(self) -> None:
        scan = adr_next.WorktreeScan((self.root,), (), (3,))
        error = StringIO()
        with (
            patch.object(adr_next, "checkout_root", return_value=self.root),
            patch.object(adr_next, "scan_worktrees", return_value=scan),
            patch.object(
                adr_next,
                "write_claim",
                side_effect=FileExistsError("destination already exists"),
            ),
            redirect_stderr(error),
        ):
            status = adr_next.main(["a new decision"])

        self.assertEqual(status, 2)
        self.assertIn("destination already exists", error.getvalue())

    def test_an_os_error_exits_two_without_a_traceback(self) -> None:
        scan = adr_next.WorktreeScan((self.root,), (), (3,))
        error = StringIO()
        with (
            patch.object(adr_next, "checkout_root", return_value=self.root),
            patch.object(adr_next, "scan_worktrees", return_value=scan),
            patch.object(
                adr_next, "write_claim", side_effect=PermissionError("file is locked")
            ),
            redirect_stderr(error),
        ):
            status = adr_next.main(["a new decision"])

        self.assertEqual(status, 2)
        self.assertIn("file is locked", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())

    def test_check_staged_warns_about_another_worktree_claiming_the_number(self) -> None:
        other = self.add_worktree("other-claim")
        claimed = "0004-other-claim.md"
        (other / "docs" / "adr" / claimed).write_text("# Other\n", encoding="utf-8")
        current = self.root / "docs" / "adr" / "0004-current-claim.md"
        current.write_text("# Current\n", encoding="utf-8")
        git(self.root, "add", current.relative_to(self.root).as_posix())

        finished = self.run_command("--check-staged")

        self.assertEqual(finished.returncode, 2, finished.stderr)
        self.assertIn("warning:", finished.stderr)
        self.assertIn("0004", finished.stderr)
        self.assertIn(str(other), finished.stderr)
        self.assertFalse((self.root / "docs" / "adr" / "0005-check-staged.md").exists())

    def test_check_staged_does_not_call_the_same_record_a_collision(self) -> None:
        self.add_worktree("same-record")
        current = self.root / "docs" / "adr" / "0003-existing.md"
        current.write_text("# Corrected existing record\n", encoding="utf-8")
        git(self.root, "add", current.relative_to(self.root).as_posix())

        finished = self.run_command("--check-staged")

        self.assertEqual(finished.returncode, 2, finished.stderr)
        self.assertNotIn("warning:", finished.stderr)

    def test_check_staged_includes_a_renamed_adr(self) -> None:
        other = self.add_worktree("rename-collision")
        (other / "docs" / "adr" / "0004-other-claim.md").write_text(
            "# Other\n", encoding="utf-8"
        )
        git(
            self.root,
            "mv",
            "docs/adr/0003-existing.md",
            "docs/adr/0004-current-claim.md",
        )

        finished = self.run_command("--check-staged")

        self.assertEqual(finished.returncode, 2, finished.stderr)
        self.assertIn("warning:", finished.stderr)
        self.assertIn("0004-other-claim.md", finished.stderr)


if __name__ == "__main__":
    unittest.main()
