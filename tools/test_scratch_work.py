"""Behavior tests for the accounted scratch-work producer."""

from __future__ import annotations

import io
import re
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import scratch_work
import scratch_census


REPO_ROOT = Path(__file__).resolve().parent.parent
HARVEST_SIGNATURE = (
    'gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100"'
)
PRODUCER_CALL = 'H=$(python tools/scratch_work.py ticket "$TICKET_NUMBER")'
BRANCH_KEY = "H=scratch/sessions/$(git rev-parse --abbrev-ref HEAD)"


class ScratchWorkCommandTests(unittest.TestCase):
    def test_ticket_command_creates_and_prints_the_ticket_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            scratch = Path(raw).resolve() / "scratch"
            output = io.StringIO()
            with (
                mock.patch.object(
                    scratch_work.repo_root,
                    "scratch_root",
                    return_value=scratch,
                ),
                redirect_stdout(output),
            ):
                status = scratch_work.main(["ticket", "700"])

            produced = Path(output.getvalue().strip())
            self.assertEqual(status, 0)
            self.assertEqual(produced, scratch / "sessions" / "ticket-700")
            self.assertTrue(produced.is_dir())
            self.assertNotEqual(produced.parent, scratch)

    def test_a_followup_on_one_ticket_reopens_existing_work(self) -> None:
        self.assertIn(
            scratch_census.SHARED_TICKET_DIRECTORY_LIMIT,
            scratch_census.DECLARED_LIMITS,
        )
        with tempfile.TemporaryDirectory() as raw:
            scratch = Path(raw).resolve() / "scratch"
            with mock.patch.object(
                scratch_work.repo_root,
                "scratch_root",
                return_value=scratch,
            ):
                first = scratch_work.ticket_directory(700)
                marker = first / "predecessor-work"
                marker.touch()
                second = scratch_work.ticket_directory(700)

            self.assertEqual(first, second)
            self.assertTrue(marker.is_file())

    def test_sweep_command_creates_and_prints_the_dated_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            scratch = Path(raw).resolve() / "scratch"
            output = io.StringIO()
            with (
                mock.patch.object(
                    scratch_work.repo_root,
                    "scratch_root",
                    return_value=scratch,
                ),
                redirect_stdout(output),
            ):
                status = scratch_work.main(["sweep", "2026-09-01"])

            produced = Path(output.getvalue().strip())
            self.assertEqual(status, 0)
            self.assertEqual(produced, scratch / "sessions" / "sweep-2026-09-01")
            self.assertTrue(produced.is_dir())
            self.assertNotEqual(produced.parent, scratch)

    def test_the_producer_refuses_a_scratch_top_level_destination(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            scratch = Path(raw).resolve() / "scratch"
            with mock.patch.object(
                scratch_work.repo_root,
                "scratch_root",
                return_value=scratch,
            ):
                with self.assertRaisesRegex(ValueError, "scratch top level"):
                    scratch_work._create("..")


class DocumentedHarvestTests(unittest.TestCase):
    def test_every_tracked_harvest_calls_the_ticket_directory_producer(self) -> None:
        """Clean means no tracked harvest fails; unstaged files are not read."""
        listed = subprocess.run(
            ["git", "ls-files", "*.md", "*.py"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        harvests: list[tuple[Path, str]] = []
        for relative in listed.stdout.splitlines():
            path = REPO_ROOT / relative
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(re.escape(HARVEST_SIGNATURE), text):
                write = text[match.start() : match.end() + 160]
                if '"$H/tracker-issues.json"' not in write:
                    continue
                block = text[max(0, match.start() - 220) : match.end() + 160]
                harvests.append((path, block))

        self.assertTrue(harvests)
        for path, block in harvests:
            with self.subTest(path=path):
                self.assertIn(PRODUCER_CALL, block)
                self.assertNotIn(BRANCH_KEY, block)


if __name__ == "__main__":
    unittest.main()
