"""Behavior tests for shared artifact provenance trust."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import artifact_provenance  # noqa: E402


class MergeParentTrustTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self._git("init", "--initial-branch=main")
        self._git("config", "user.email", "fixture@example.com")
        self._git("config", "user.name", "Fixture")
        (self.repo / "tools").mkdir()
        (self.repo / "tools" / "guidelines_extract.py").write_text(
            "EXTRACTOR = 'stable'\n", encoding="utf-8"
        )
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        self._git("add", "tools/guidelines_extract.py", "base.txt")
        self._git("commit", "-m", "base")
        self._git("branch", "feature")

    def _git(self, *arguments: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()

    def test_an_unchanged_extractor_built_on_the_incoming_parent_is_trusted(self):
        (self.repo / "main.txt").write_text("main\n", encoding="utf-8")
        self._git("add", "main.txt")
        self._git("commit", "-m", "main work")
        incoming_parent = self._git("rev-parse", "HEAD")
        self._git("switch", "feature")
        (self.repo / "feature.txt").write_text("feature\n", encoding="utf-8")
        self._git("add", "feature.txt")
        self._git("commit", "-m", "feature work")
        self._git("merge", "--no-commit", "--no-ff", "main")

        result = artifact_provenance.check_producer(
            {"commit": incoming_parent, "dirty": False},
            self.repo / "manifest.json",
            repo_root=self.repo,
            unchanged_paths=("tools/guidelines_extract.py",),
        )

        self.assertTrue(result.trusted)

    def test_a_changed_extractor_from_the_incoming_parent_is_refused(self):
        incoming_parent = self._git("rev-parse", "HEAD")
        self._git("switch", "feature")
        (self.repo / "tools" / "guidelines_extract.py").write_text(
            "EXTRACTOR = 'changed'\n", encoding="utf-8"
        )
        self._git("add", "tools/guidelines_extract.py")
        self._git("commit", "-m", "change extractor")
        self._git("merge", "--no-commit", "--no-ff", "main")

        with self.assertRaisesRegex(
            artifact_provenance.UntrustedProvenance, "different commit"
        ):
            artifact_provenance.check_producer(
                {"commit": incoming_parent, "dirty": False},
                self.repo / "manifest.json",
                repo_root=self.repo,
                unchanged_paths=("tools/guidelines_extract.py",),
            )

    def test_an_artifact_from_head_is_refused_when_the_merge_changes_its_extractor(self):
        (self.repo / "tools" / "guidelines_extract.py").write_text(
            "EXTRACTOR = 'changed on main'\n", encoding="utf-8"
        )
        self._git("add", "tools/guidelines_extract.py")
        self._git("commit", "-m", "change extractor on main")
        self._git("switch", "feature")
        (self.repo / "feature.txt").write_text("feature\n", encoding="utf-8")
        self._git("add", "feature.txt")
        self._git("commit", "-m", "feature work")
        current_parent = self._git("rev-parse", "HEAD")
        self._git("merge", "--no-commit", "--no-ff", "main")

        with self.assertRaisesRegex(
            artifact_provenance.UntrustedProvenance, "producer code has changed"
        ):
            artifact_provenance.check_producer(
                {"commit": current_parent, "dirty": False},
                self.repo / "manifest.json",
                repo_root=self.repo,
                unchanged_paths=("tools/guidelines_extract.py",),
            )


if __name__ == "__main__":
    unittest.main()
