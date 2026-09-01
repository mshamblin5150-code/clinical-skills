"""Behavior tests for the scratch-session directory producer."""

from __future__ import annotations

import io
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import session_directory
import scratch_census


REPO_ROOT = Path(__file__).resolve().parent.parent
HARVEST_COPIES = {
    REPO_ROOT / "CLAUDE.md": 2,
    REPO_ROOT / "docs" / "agents" / "issue-tracker.md": 1,
    REPO_ROOT / "tools" / "tracker_scan.py": 1,
    REPO_ROOT / "tools" / "tracker_bodies.py": 1,
}
PRODUCER_CALL = 'H=$(python tools/session_directory.py ticket "$TICKET_NUMBER")'
BRANCH_KEY = "H=scratch/sessions/$(git rev-parse --abbrev-ref HEAD)"


class SessionDirectoryCommandTests(unittest.TestCase):
    def test_ticket_command_creates_and_prints_the_ticket_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            scratch = Path(raw).resolve() / "scratch"
            output = io.StringIO()
            with (
                mock.patch.object(
                    session_directory.repo_root,
                    "scratch_root",
                    return_value=scratch,
                ),
                redirect_stdout(output),
            ):
                status = session_directory.main(["ticket", "700"])

            produced = Path(output.getvalue().strip())
            self.assertEqual(status, 0)
            self.assertEqual(produced, scratch / "sessions" / "ticket-700")
            self.assertTrue(produced.is_dir())
            self.assertNotEqual(produced.parent, scratch)

    def test_two_drones_on_one_ticket_share_one_directory(self) -> None:
        self.assertIn(
            scratch_census.SHARED_TICKET_DIRECTORY_LIMIT,
            scratch_census.DECLARED_LIMITS,
        )
        with tempfile.TemporaryDirectory() as raw:
            scratch = Path(raw).resolve() / "scratch"
            with mock.patch.object(
                session_directory.repo_root,
                "scratch_root",
                return_value=scratch,
            ):
                with ThreadPoolExecutor(max_workers=2) as pool:
                    first, second = pool.map(
                        session_directory.ticket_directory,
                        (700, 700),
                    )

            self.assertEqual(first, second)
            self.assertTrue(second.is_dir())

    def test_sweep_command_creates_and_prints_the_dated_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            scratch = Path(raw).resolve() / "scratch"
            output = io.StringIO()
            with (
                mock.patch.object(
                    session_directory.repo_root,
                    "scratch_root",
                    return_value=scratch,
                ),
                redirect_stdout(output),
            ):
                status = session_directory.main(["sweep", "2026-09-01"])

            produced = Path(output.getvalue().strip())
            self.assertEqual(status, 0)
            self.assertEqual(produced, scratch / "sessions" / "sweep-2026-09-01")
            self.assertTrue(produced.is_dir())
            self.assertNotEqual(produced.parent, scratch)


class DocumentedHarvestTests(unittest.TestCase):
    def test_all_five_harvests_call_the_ticket_directory_producer(self) -> None:
        for path, expected in HARVEST_COPIES.items():
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(text.count(PRODUCER_CALL), expected)
                self.assertNotIn(BRANCH_KEY, text)


if __name__ == "__main__":
    unittest.main()
