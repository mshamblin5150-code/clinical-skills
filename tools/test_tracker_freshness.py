"""Command-line behavior for the tracker-sweep base gate in #320."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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

    def run_command(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MODULE)],
            cwd=self.reader,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
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

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("STALE", result.stderr)
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

    def test_feature_branch_ahead_of_main_passes_when_it_contains_main(self) -> None:
        git("config", "user.name", "Test Reader", cwd=self.reader)
        git("config", "user.email", "reader@example.invalid", cwd=self.reader)
        (self.reader / "branch.txt").write_text("branch work\n", encoding="utf-8")
        git("add", "--", "branch.txt", cwd=self.reader)
        git("commit", "-m", "branch work", cwd=self.reader)

        result = self.run_command()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("FRESH", result.stdout)


class DocumentationRequiresBothCheckpoints(unittest.TestCase):
    def test_agent_and_tracker_instructions_require_start_and_publication_checks(self) -> None:
        for relative in ("CLAUDE.md", "docs/agents/issue-tracker.md"):
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(relative=relative):
                self.assertIn("Before reading any ticket", text)
                self.assertIn("Immediately before posting", text)
                self.assertGreaterEqual(text.count("python tools/tracker_freshness.py"), 2)


if __name__ == "__main__":
    unittest.main()
