"""Authorization tests for the DOCX branch's two Canvas gates."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import assignment_submission


class TwoGateUpload(unittest.TestCase):
    def test_a_failed_gate_write_leaves_no_partial_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docx = root / "assignment.docx"
            docx.write_bytes(b"canonical Word artifact")

            with mock.patch.object(
                assignment_submission.os, "replace", side_effect=OSError("busy")
            ):
                with self.assertRaises(OSError):
                    assignment_submission.stage(root, docx, artifact_approved=True)

            self.assertEqual((), tuple(root.glob("*.building")))

    def test_artifact_approval_only_authorizes_staging_the_exact_docx(self):
        with tempfile.TemporaryDirectory() as directory:
            docx = Path(directory) / "assignment.docx"
            docx.write_bytes(b"canonical Word artifact")

            staged = assignment_submission.stage(
                Path(directory), docx, artifact_approved=True
            )

            self.assertEqual(docx.resolve(), staged.artifact)
            self.assertFalse(
                assignment_submission.submit_is_authorized(
                    staged
                )
            )
            failed, _ = assignment_submission.completion_gate(Path(directory), docx)
            self.assertTrue(failed)

    def test_final_confirmation_applies_only_while_the_staged_bytes_still_match(self):
        with tempfile.TemporaryDirectory() as directory:
            docx = Path(directory) / "assignment.docx"
            docx.write_bytes(b"canonical Word artifact")
            staged = assignment_submission.stage(
                Path(directory), docx, artifact_approved=True
            )

            assignment_submission.confirm(staged, final_confirmation=True)
            self.assertTrue(assignment_submission.submit_is_authorized(staged))
            failed, report = assignment_submission.completion_gate(
                Path(directory), docx
            )
            self.assertFalse(failed, report)
            docx.write_bytes(b"changed after review")
            self.assertFalse(assignment_submission.submit_is_authorized(staged))
            failed, _ = assignment_submission.completion_gate(Path(directory), docx)
            self.assertTrue(failed)


if __name__ == "__main__":
    unittest.main()
