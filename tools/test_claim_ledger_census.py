"""Public-command tests for the claim ledger census."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import claim_ledger_census as census
import research_ledger


SOURCED = (
    "## CLAIM: source claim\n"
    "STATUS: sourced\n"
    "RESTATEMENT: the first reading\n"
    "REFUTATION: stands - an independent check of the source\n"
)
BARE = (
    "## CLAIM: bare claim\n"
    "STATUS: sourced\n"
    "RESTATEMENT: the first reading\n"
    "REFUTATION: stands\n"
)


class ClaimLedgerCensusCommand(unittest.TestCase):
    def run_main(self, roots: tuple[Path, ...]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.object(census.scratch_census, "worktree_roots", return_value=roots),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = census.main([])
        return status, stdout.getvalue(), stderr.getvalue()

    def test_ledger_and_neighboring_snapshot_are_counted_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "scratch" / "runs" / "one"
            run.mkdir(parents=True)
            (run / "claims.md").write_text(
                "DATE: 2099-01-01\n" + SOURCED + BARE + "## CLAIM: no source\nSTATUS: unsourced\n",
                encoding="utf-8",
            )
            (run / "claims-private-marker.md").write_text(
                "## CLAIM: snapshot-only\nSTATUS: sourced\n", encoding="utf-8"
            )
            status, stdout, stderr = self.run_main((root,))

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("checkouts enumerated              1", stdout)
        self.assertIn("scratch roots read                 1", stdout)
        self.assertIn("ledgers read                       1", stdout)
        self.assertIn("ledgers with DATE header           1", stdout)
        self.assertRegex(stdout, r"(?m)^  sourced\s+2$")
        self.assertRegex(stdout, r"(?m)^  unsourced\s+1$")
        self.assertIn("sourced without substantive refutation 1", stdout)
        self.assertIn("snapshots beside a ledger          1", stdout)
        self.assertNotIn("snapshot-only", stdout)
        self.assertNotIn("private-marker", stdout)

    def test_snapshot_only_run_is_a_declared_limit_not_a_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "scratch" / "runs" / "old"
            run.mkdir(parents=True)
            (run / "claims-private-marker.md").write_text(SOURCED, encoding="utf-8")
            status, stdout, stderr = self.run_main((root,))

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("ledgers read                       0", stdout)
        self.assertIn("runs with claim files and no ledger 1", stdout)
        self.assertNotIn("private-marker", stdout)

    def test_unreadable_registered_root_exits_two_without_a_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "private-marker"
            scratch = root / "scratch"
            scratch.mkdir(parents=True)
            with patch.object(census, "read_root", side_effect=OSError("private-marker")):
                status, stdout, stderr = self.run_main((root,))

        self.assertEqual(status, 2)
        self.assertIn("scratch roots unreadable           1", stdout)
        self.assertIn("NOT SCANNED", stderr)
        self.assertNotIn("private-marker", stdout + stderr)

    def test_unavailable_checkout_registry_exits_two_without_a_path(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.object(
                census.scratch_census,
                "worktree_roots",
                side_effect=census.scratch_census.CensusNotRun("private-marker"),
            ),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = census.main([])

        self.assertEqual(status, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("NOT SCANNED", stderr.getvalue())
        self.assertNotIn("private-marker", stderr.getvalue())

    def test_empty_registered_population_is_a_completed_zero_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scratch").mkdir()
            status, stdout, stderr = self.run_main((root,))

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("ledgers read                       0", stdout)
        self.assertIn("runs with claim files and no ledger 0", stdout)

    def test_parser_and_refutation_predicate_are_the_graders_objects(self):
        self.assertIs(census.read_records, research_ledger.read_records)
        self.assertIs(
            census.has_substantive_refutation,
            research_ledger.has_substantive_refutation,
        )

    def test_show_is_not_an_option(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            self.assertEqual(census.main(["--show"]), 2)
        self.assertIn("usage:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
