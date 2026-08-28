"""Behavior tests for the scratch-root census."""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import scratch_census as census


SCRIPT = Path(__file__).with_name("scratch_census.py")
PRE_COMMIT = Path(__file__).with_name("hooks") / "pre-commit"


def git(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        check=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


class ScratchRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve() / "owning"
        self.root.mkdir()
        git(self.root, "init", "--initial-branch=main")
        git(self.root, "config", "user.email", "tests@example.invalid")
        git(self.root, "config", "user.name", "Scratch census tests")
        (self.root / "README.md").write_text(
            "Account artifacts live at `scratch/sessions/`.\n", encoding="utf-8"
        )
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-m", "fixture")
        scratch = self.root / "scratch"
        scratch.mkdir()
        for index in range(census.OWNING_BASELINE):
            (scratch / f"residue-{index}").touch()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def add_worktree(self, name: str = "other", ref: str | None = None) -> Path:
        worktree = self.root.parent / name
        arguments = ["worktree", "add", "--detach", str(worktree)]
        if ref is not None:
            arguments.append(ref)
        git(self.root, *arguments)
        return worktree

    def run_census(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=self.root,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )


class ScratchCensusCommandTests(ScratchRepository):
    def test_an_accounted_worktree_root_and_the_owning_baseline_are_clean(self) -> None:
        other = self.add_worktree()
        (other / "scratch" / "sessions").mkdir(parents=True)
        (other / "scratch" / "sessions" / "working.txt").touch()

        finished = self.run_census()

        self.assertEqual(finished.returncode, 0, finished.stderr)
        self.assertIn("2 worktrees enumerated", finished.stdout)
        self.assertIn("2 checkouts own a scratch root", finished.stdout)
        self.assertIn(
            f"{census.OWNING_BASELINE + 1} files beneath", finished.stdout
        )
        self.assertIn(
            f"{census.OWNING_BASELINE} owning-checkout unaccounted",
            finished.stdout,
        )
        self.assertIn("0 other-checkout unaccounted", finished.stdout)
        self.assertIn("CLEAN", finished.stdout)

    def test_a_loose_worktree_entry_is_a_count_only_finding(self) -> None:
        other = self.add_worktree()
        (other / "scratch").mkdir()
        private_name = "do-not-print-this-name"
        (other / "scratch" / private_name).touch()

        finished = self.run_census()

        self.assertEqual(finished.returncode, 1, finished.stderr)
        self.assertIn("FINDING", finished.stdout)
        self.assertIn("1 other-checkout unaccounted", finished.stdout)
        self.assertNotIn(private_name, finished.stdout + finished.stderr)

    def test_the_owning_checkout_refuses_only_above_its_ceiling(self) -> None:
        private_name = "another-private-name"
        (self.root / "scratch" / private_name).touch()

        finished = self.run_census()

        self.assertEqual(finished.returncode, 1, finished.stderr)
        self.assertIn(
            f"{census.OWNING_BASELINE + 1} owning-checkout unaccounted",
            finished.stdout,
        )
        self.assertNotIn(private_name, finished.stdout + finished.stderr)

    def test_an_absent_owning_scratch_root_is_not_a_clean_scan(self) -> None:
        for entry in (self.root / "scratch").iterdir():
            entry.unlink()
        (self.root / "scratch").rmdir()

        finished = self.run_census()

        self.assertEqual(finished.returncode, 2, finished.stderr)
        self.assertIn("NOT SCANNED", finished.stdout)
        self.assertNotIn("CLEAN", finished.stdout)

    def test_a_finding_wins_when_another_registered_checkout_is_unreadable(self) -> None:
        failing = self.add_worktree("failing")
        (failing / "scratch").mkdir()
        (failing / "scratch" / "private-entry").touch()
        unreadable = self.add_worktree("registered-but-gone")
        shutil.rmtree(unreadable)

        finished = self.run_census()

        self.assertEqual(finished.returncode, 1, finished.stderr)
        self.assertIn("1 unreadable", finished.stdout)
        self.assertIn(str(unreadable), finished.stdout)
        self.assertIn("FINDING", finished.stdout)
        self.assertIn("NOT SCANNED", finished.stdout)

    def test_worktree_state_is_measured_only_when_requested(self) -> None:
        (self.root / "README.md").write_text(
            "Account artifacts live at `scratch/sessions/`.\n\nLater commit.\n",
            encoding="utf-8",
        )
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-m", "move owning checkout forward")
        other = self.add_worktree(ref="HEAD~1")
        (other / "scratch" / "sessions").mkdir(parents=True)

        ordinary = self.run_census()
        measured = self.run_census("--worktrees")

        self.assertEqual(ordinary.returncode, 0, ordinary.stderr)
        self.assertNotIn("worktree state:", ordinary.stdout)
        self.assertEqual(
            measured.returncode, 0, measured.stdout + measured.stderr
        )
        self.assertIn(
            "worktree state: 1 merged; 1 clean; 0 ahead",
            measured.stdout,
        )

    def test_a_cited_name_may_contain_unicode_and_spaces(self) -> None:
        (self.root / "README.md").write_text(
            "Account artifacts live at scratch/café notes/.\n"
            "Another lives at scratch/name,comma/.\n",
            encoding="utf-8",
        )
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-m", "name a spaced artifact")
        (self.root / "scratch" / "café notes").mkdir()
        (self.root / "scratch" / "name,comma").mkdir()

        finished = self.run_census()

        self.assertEqual(finished.returncode, 0, finished.stdout + finished.stderr)

    def test_a_quoted_python_path_may_name_a_spaced_leaf(self) -> None:
        source = self.root / "paths.py"
        source.write_text('TARGET = "scratch/café notes"\n', encoding="utf-8")
        git(self.root, "add", "paths.py")
        git(self.root, "commit", "-m", "name a quoted artifact")
        (self.root / "scratch" / "café notes").mkdir()

        finished = self.run_census()

        self.assertEqual(finished.returncode, 0, finished.stdout + finished.stderr)

    def test_a_complete_spaced_path_does_not_account_for_its_prefix(self) -> None:
        (self.root / "README.md").write_text(
            "Account artifacts live at scratch/café notes/.\n", encoding="utf-8"
        )
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-m", "name only the complete artifact")
        (self.root / "scratch" / "café").mkdir()

        finished = self.run_census()

        self.assertEqual(finished.returncode, 1, finished.stdout + finished.stderr)

    def test_a_near_prefix_does_not_account_for_a_name(self) -> None:
        (self.root / "README.md").write_text(
            "This is not a path: not-scratch/private-name.\n", encoding="utf-8"
        )
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-m", "near miss")
        (self.root / "scratch" / "private-name").touch()

        finished = self.run_census()

        self.assertEqual(finished.returncode, 1, finished.stdout + finished.stderr)


class AccountedSetTests(unittest.TestCase):
    def test_every_standing_artifact_is_in_the_derived_set(self) -> None:
        repo = Path(__file__).resolve().parent.parent

        derived = census.accounted_names(repo)

        self.assertTrue(census.STANDING_ARTIFACTS <= derived)
        self.assertNotEqual(census.STANDING_ARTIFACTS, derived)

    def test_the_census_refuses_from_the_hook_and_is_not_advisory(self) -> None:
        hook = PRE_COMMIT.read_text(encoding="utf-8")

        self.assertIn('scratch_census.py" >&2 || status=1', hook)

    def test_the_ordinary_census_uses_one_registry_and_one_grep_process(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            scratch = root / "scratch"
            scratch.mkdir()
            for index in range(census.OWNING_BASELINE):
                (scratch / f"residue-{index}").touch()
            responses = [
                subprocess.CompletedProcess(
                    ["git", "worktree"],
                    0,
                    stdout=f"worktree {root}\nHEAD abc\nbranch refs/heads/main\n",
                    stderr="",
                ),
                subprocess.CompletedProcess(
                    ["git", "grep"], 0, stdout="scratch/sessions/\n", stderr=""
                ),
            ]
            with (
                mock.patch.object(census.Path, "cwd", return_value=root),
                mock.patch.object(census, "run_git", side_effect=responses) as run,
                redirect_stdout(io.StringIO()),
            ):
                status = census.main([])

        self.assertEqual(status, 0)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[0].args[1:], ("worktree", "list", "--porcelain"))
        self.assertEqual(
            run.call_args_list[1].args[1:],
            ("grep", "-h", "-I", "-e", "scratch/", "--", "."),
        )

    def test_a_process_launch_failure_is_not_scanned_without_a_traceback(self) -> None:
        output = io.StringIO()
        error = io.StringIO()
        with (
            mock.patch.object(
                census.subprocess, "run", side_effect=OSError("git is unavailable")
            ),
            redirect_stdout(output),
            redirect_stderr(error),
        ):
            status = census.main([])

        self.assertEqual(status, 2)
        self.assertIn("NOT SCANNED", error.getvalue())
        self.assertNotIn("Traceback", output.getvalue() + error.getvalue())

    def test_a_grep_failure_preserves_the_enumerated_population(self) -> None:
        root = Path.cwd().resolve()
        responses = [
            subprocess.CompletedProcess(
                ["git", "worktree"],
                0,
                stdout=f"worktree {root}\nHEAD abc\nbranch refs/heads/main\n",
                stderr="",
            ),
            subprocess.CompletedProcess(
                ["git", "grep"], 2, stdout="", stderr="forced grep failure"
            ),
        ]
        output = io.StringIO()
        error = io.StringIO()
        with (
            mock.patch.object(census, "run_git", side_effect=responses),
            redirect_stdout(output),
            redirect_stderr(error),
        ):
            status = census.main([])

        self.assertEqual(status, 2)
        self.assertIn("1 worktrees enumerated", output.getvalue())
        self.assertIn("scratch roots:", output.getvalue())
        self.assertIn("forced grep failure", error.getvalue())


if __name__ == "__main__":
    unittest.main()
