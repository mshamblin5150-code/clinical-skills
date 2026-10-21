"""Portable behavior controls; hosted Windows execution remains separate."""
from pathlib import Path
from contextlib import contextmanager
import os
import tempfile
import unittest

from clone_inventory_diagnostic import discrepancy, validate_results
from measure_parallel_readers import inventory, Hold


@contextmanager
def fixture_root():
    retained = os.environ.get("INVENTORY_DIAGNOSTIC_TEST_ROOT")
    if retained:
        yield tempfile.mkdtemp(prefix="control-", dir=retained)
    else:
        with tempfile.TemporaryDirectory() as root:
            yield root


class DiagnosticControls(unittest.TestCase):
    def test_raw_mismatch_is_not_admitted_as_equal(self):
        with fixture_root() as root:
            left, right = Path(root) / "left", Path(root) / "right"
            left.mkdir(); right.mkdir()
            (left / "text.txt").write_bytes(b"one\r\ntwo\r\n")
            (right / "text.txt").write_bytes(b"one\ntwo\n")
            result = discrepancy(left, right, inventory(left), inventory(right), {"text.txt"})
            self.assertFalse(result["raw_equal"])
            self.assertEqual(result["content_mismatch"], 1)
            self.assertEqual(result["crlf_only"], 1)

    def test_nonreproducing_baseline_cannot_claim_success(self):
        clean = {"guard": "passed", "raw_equal": True, "missing": 0, "extra": 0,
                 "content_mismatch": 0, "crlf_only": 0}
        with self.assertRaisesRegex(Hold, "baseline_not_explained_by_checkout_conversion"):
            validate_results({"baseline": clean, "candidate": clean})

    def test_nonallowlisted_names_and_binary_changes_remain_private(self):
        with fixture_root() as root:
            left, right = Path(root) / "left", Path(root) / "right"
            left.mkdir(); right.mkdir()
            (left / "secret-name.bin").write_bytes(b"\x00old")
            (right / "secret-name.bin").write_bytes(b"\x00new")
            (left / "missing.txt").write_bytes(b"old")
            (right / "extra.txt").write_bytes(b"new")
            result = discrepancy(left, right, inventory(left), inventory(right), set())
            self.assertFalse(result["raw_equal"])
            self.assertEqual((result["missing"], result["extra"], result["content_mismatch"]), (1, 1, 1))
            self.assertEqual(result["crlf_only"], 0)
            self.assertEqual(result["unlisted_count"], 3)
            self.assertEqual(result["paths"], [])
            self.assertNotIn("secret-name", str(result))

    def test_binary_line_ending_difference_is_not_classified_as_text(self):
        with fixture_root() as root:
            left, right = Path(root) / "left", Path(root) / "right"
            left.mkdir(); right.mkdir()
            (left / "opaque.bin").write_bytes(b"\x00one\r\n")
            (right / "opaque.bin").write_bytes(b"\x00one\n")
            result = discrepancy(left, right, inventory(left), inventory(right), {"opaque.bin"})
            self.assertEqual(result["crlf_only"], 0)
            self.assertFalse(result["raw_equal"])

    def test_candidate_must_pass_raw_guard(self):
        baseline = {"guard": "clone_source_inventory_mismatch", "raw_equal": False,
                    "missing": 0, "extra": 0, "content_mismatch": 1, "crlf_only": 1}
        with self.assertRaisesRegex(Hold, "candidate_inventory_not_equal"):
            validate_results({"baseline": baseline, "candidate": baseline})
        validate_results({"baseline": baseline, "candidate": {"guard": "passed", "raw_equal": True}})

    def test_unexplained_baseline_change_remains_a_hold(self):
        baseline = {"guard": "clone_source_inventory_mismatch", "raw_equal": False,
                    "missing": 0, "extra": 0, "content_mismatch": 2, "crlf_only": 1}
        with self.assertRaisesRegex(Hold, "baseline_not_explained_by_checkout_conversion"):
            validate_results({"baseline": baseline, "candidate": {"guard": "passed", "raw_equal": True}})

    def test_workflow_is_single_bounded_diagnostic(self):
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/ci-parallel-proof.yml").read_text()
        self.assertIn("timeout-minutes: 10\n", workflow)
        self.assertIn("if: github.run_attempt == 1\n", workflow)
        self.assertIn("python-version: '3.14.4'", workflow)
        self.assertIn("python observer/diagnostics/clone_inventory_diagnostic.py", workflow)
        self.assertNotIn("python observer/diagnostics/measure_parallel_readers.py", workflow)
        self.assertLess(workflow.index("PROOF_JOB_START_EPOCH="), workflow.index("uses: actions/checkout"))

    def test_public_path_output_is_bounded(self):
        with fixture_root() as root:
            left, right = Path(root) / "left", Path(root) / "right"
            left.mkdir(); right.mkdir()
            names = {"file-%02d.txt" % number for number in range(24)}
            for name in names:
                (left / name).write_bytes(b"one\r\n")
                (right / name).write_bytes(b"one\n")
            result = discrepancy(left, right, inventory(left), inventory(right), names)
            self.assertEqual(len(result["paths"]), 20)
            self.assertEqual(result["path_overflow"], 4)
            self.assertEqual(result["content_mismatch"], 24)


if __name__ == "__main__":
    unittest.main()
