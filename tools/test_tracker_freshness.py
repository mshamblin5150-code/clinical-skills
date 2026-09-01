"""Command-line behavior for the tracker-sweep base gate in #320."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import tracker_freshness


MODULE = Path(__file__).with_name("tracker_freshness.py")
REPO_ROOT = MODULE.parent.parent


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    )


class TrackerFreshnessCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.writer = self.root / "writer"
        self.reader = self.root / "reader"

        git("init", "--bare", "--initial-branch=main", str(self.remote), cwd=self.root)
        git("clone", str(self.remote), str(self.writer), cwd=self.root)
        git("config", "user.name", "Test Writer", cwd=self.writer)
        git("config", "user.email", "writer@example.invalid", cwd=self.writer)
        (self.writer / "tracked.txt").write_text("one\n", encoding="utf-8")
        git("add", "--", "tracked.txt", cwd=self.writer)
        git("commit", "-m", "initial", cwd=self.writer)
        git("push", "origin", "main", cwd=self.writer)
        git("clone", str(self.remote), str(self.reader), cwd=self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_command(self, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MODULE)],
            cwd=self.reader,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            env=env,
        )

    def advance_main(self) -> str:
        (self.writer / "tracked.txt").write_text("two\n", encoding="utf-8")
        git("add", "--", "tracked.txt", cwd=self.writer)
        git("commit", "-m", "advance main", cwd=self.writer)
        git("push", "origin", "main", cwd=self.writer)
        return git("rev-parse", "HEAD", cwd=self.writer).stdout.strip()

    def test_current_branch_passes_after_fetching_main(self) -> None:
        result = self.run_command()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("FRESH", result.stdout)
        self.assertIn(git("rev-parse", "HEAD", cwd=self.reader).stdout.strip(), result.stdout)

    def test_branch_missing_latest_main_stops_after_refreshing_the_ref(self) -> None:
        latest_main = self.advance_main()

        result = self.run_command()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("STALE", result.stderr)
        self.assertNotIn("DID NOT CHECK", result.stderr)
        self.assertIn(latest_main, result.stderr)
        self.assertIn("git rebase origin/main", result.stderr)
        self.assertEqual(
            git("rev-parse", "origin/main", cwd=self.reader).stdout.strip(),
            latest_main,
        )

    def test_fetch_failure_cannot_pass_using_the_old_remote_reference(self) -> None:
        git("remote", "set-url", "origin", str(self.root / "missing.git"), cwd=self.reader)

        result = self.run_command()

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("DID NOT CHECK", result.stderr)
        self.assertIn("fetch", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_an_unrunnable_git_binary_did_not_check_rather_than_found_something(self) -> None:
        """#744: before the split this route exited 1 through an uncaught OSError.

        With STALE now 1, a crash that reaches the same status is worse than the
        collapse the ticket was filed about -- it is indistinguishable from the
        one finding this gate exists to report.
        """

        stripped = dict(os.environ)
        stripped["PATH"] = str(self.root / "no-git-here")

        result = self.run_command(env=stripped)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("DID NOT CHECK", result.stderr)
        self.assertNotIn("STALE", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_a_git_failure_after_a_successful_fetch_did_not_check(self) -> None:
        """The fetch succeeds and a later command fails, which used to traceback."""

        git("remote", "set-url", "origin", str(self.remote), cwd=self.reader)
        # An unborn HEAD fetches fine and cannot be resolved by rev-parse.
        git("checkout", "--orphan", "unborn", cwd=self.reader)
        git("rm", "-rf", "--cached", ".", cwd=self.reader)

        result = self.run_command()

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("DID NOT CHECK", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_only_a_stale_base_reaches_status_one(self) -> None:
        """Every route this suite can drive, gathered so the partition is visible."""

        fresh = self.run_command()
        self.assertEqual(fresh.returncode, 0, fresh.stdout + fresh.stderr)

        unreachable = dict(os.environ)
        unreachable["PATH"] = str(self.root / "no-git-here")
        self.assertEqual(self.run_command(env=unreachable).returncode, 2)

        self.advance_main()
        self.assertEqual(self.run_command().returncode, 1)

    def test_feature_branch_ahead_of_main_passes_when_it_contains_main(self) -> None:
        git("config", "user.name", "Test Reader", cwd=self.reader)
        git("config", "user.email", "reader@example.invalid", cwd=self.reader)
        (self.reader / "branch.txt").write_text("branch work\n", encoding="utf-8")
        git("add", "--", "branch.txt", cwd=self.reader)
        git("commit", "-m", "branch work", cwd=self.reader)

        result = self.run_command()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("FRESH", result.stdout)


class AnAncestryQuestionGitDeclinesToAnswer(unittest.TestCase):
    """#744: `merge-base --is-ancestor` answers 0 or 1 and errors otherwise.

    The subprocess cases above cannot reach this branch -- every route that
    corrupts the ancestry query also fails the `rev-parse` before it -- so it is
    driven directly rather than declared unreached. Reading a git error as
    `IS_NOT_ANCESTOR` would report `STALE` about a base nothing measured, which
    is the ticket's own defect with the sign flipped.
    """

    def setUp(self) -> None:
        self.calls: list[tuple[str, ...]] = []

    def fake_run_git(self, status: int):
        def run_git(*args: str) -> subprocess.CompletedProcess[str]:
            self.calls.append(args)
            if args[0] == "merge-base":
                return subprocess.CompletedProcess(args, status, "", "fatal: bad object")
            return subprocess.CompletedProcess(args, 0, "0" * 40 + "\n", "")

        return run_git

    def statuses_for(self, ancestry_status: int) -> int:
        original = tracker_freshness.run_git
        tracker_freshness.run_git = self.fake_run_git(ancestry_status)
        try:
            return tracker_freshness.main()
        finally:
            tracker_freshness.run_git = original

    def test_a_declined_ancestry_question_did_not_check(self) -> None:
        self.assertEqual(self.statuses_for(128), tracker_freshness.DID_NOT_CHECK)

    def test_the_two_documented_answers_still_mean_what_they_say(self) -> None:
        self.assertEqual(self.statuses_for(0), tracker_freshness.FRESH)
        self.assertEqual(self.statuses_for(1), tracker_freshness.STALE)

    def test_the_stub_is_live(self) -> None:
        """A stub that never ran would let all three assertions above pass."""

        self.statuses_for(0)
        self.assertIn(("merge-base", "--is-ancestor", tracker_freshness.REMOTE_REF, "HEAD"), self.calls)


class DocumentationRequiresBothCheckpoints(unittest.TestCase):
    def test_agent_and_tracker_instructions_require_start_and_publication_checks(self) -> None:
        command = "python tools/tracker_freshness.py"
        for relative in ("CLAUDE.md", "docs/agents/issue-tracker.md"):
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                start = text.index("Before reading any ticket")
                first_command = text.index(command)
                publication = text.index("Immediately before posting")
                second_command = text.index(command, first_command + 1)

                self.assertEqual(text.count(command), 2)
                self.assertLess(start, first_command)
                self.assertLess(first_command, publication)
                self.assertLess(publication, second_command)


if __name__ == "__main__":
    unittest.main()
