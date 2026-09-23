"""Authorization tests for course-assignment upload carriers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import assignment_submission
import file_digest


class TwoGateUpload(unittest.TestCase):
    def _completed_submission(self, root: Path, artifact: Path) -> None:
        staged = assignment_submission.stage(root, artifact, artifact_approved=True)
        assignment_submission.confirm(
            staged, uploaded_carriers=(artifact,), final_confirmation=True
        )
        (root / "reread.md").write_text(
            "## REREAD: assignment\n"
            "POST-URL: https://example.test/submission\n"
            "POSTED: 2026-09-23\n"
            "READ: 2026-09-23\n"
            "ATTACHMENT-COUNT: 1\n"
            f"SUBMITTED-FILE: {artifact.name}\n"
            f"SUBMISSION-SHA256: {file_digest.sha256(artifact)}\n"
            "VERDICT: matches - the posted artifact matches the reviewed file\n",
            encoding="utf-8",
        )

    def test_terminal_completion_names_and_matches_the_canonical_output_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "worktree" / "scratch" / "runs" / "assignment"
            reviewed = root / "worktree" / "output" / "course-assignments" / "assignment.pptx"
            canonical = root / "owning" / "output" / "course-assignments" / reviewed.name
            run.mkdir(parents=True)
            reviewed.parent.mkdir(parents=True)
            canonical.parent.mkdir(parents=True)
            reviewed.write_bytes(b"reviewed deck")
            canonical.write_bytes(reviewed.read_bytes())
            self._completed_submission(run, reviewed)

            with mock.patch.object(
                assignment_submission.repo_root,
                "output_root",
                return_value=root / "owning" / "output",
            ):
                failed, report = assignment_submission.completion_gate(
                    run, reviewed, submission="assignment"
                )

        self.assertFalse(failed, report)
        self.assertIn(str(canonical), report)

    def test_terminal_completion_refuses_a_missing_canonical_output_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            reviewed = root / "worktree" / "output" / "course-assignments" / "assignment.docx"
            run.mkdir()
            reviewed.parent.mkdir(parents=True)
            reviewed.write_bytes(b"reviewed document")
            self._completed_submission(run, reviewed)
            expected = root / "owning" / "output"

            with mock.patch.object(
                assignment_submission.repo_root, "output_root", return_value=expected
            ):
                failed, report = assignment_submission.completion_gate(
                    run, reviewed, submission="assignment"
                )

        self.assertTrue(failed)
        self.assertIn("canonical artifact is missing", report)
        self.assertIn(str(expected / "course-assignments" / reviewed.name), report)

    def test_terminal_completion_refuses_a_different_canonical_output_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "run"
            reviewed = root / "worktree" / "output" / "course-assignments" / "assignment.pptx"
            canonical_root = root / "owning" / "output"
            canonical = canonical_root / "course-assignments" / reviewed.name
            run.mkdir()
            reviewed.parent.mkdir(parents=True)
            canonical.parent.mkdir(parents=True)
            reviewed.write_bytes(b"reviewed deck")
            canonical.write_bytes(b"older deck")
            self._completed_submission(run, reviewed)

            with mock.patch.object(
                assignment_submission.repo_root,
                "output_root",
                return_value=canonical_root,
            ):
                failed, report = assignment_submission.completion_gate(
                    run, reviewed, submission="assignment"
                )

        self.assertTrue(failed)
        self.assertIn("canonical artifact fingerprint differs", report)
        self.assertIn(str(canonical), report)

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

    def test_default_carrier_set_excludes_a_review_companion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            companion = root / "review-notes.docx"
            deck.write_bytes(b"canonical PowerPoint artifact")
            companion.write_bytes(b"private review companion")

            staged = assignment_submission.stage(
                root, deck, artifact_approved=True
            )

            self.assertEqual(
                "ATTACHMENT-COUNT: 1\nFILENAME: assignment.pptx",
                assignment_submission.approval_surface(staged),
            )
            self.assertTrue(assignment_submission.upload_is_allowed(staged, deck))
            self.assertFalse(
                assignment_submission.upload_is_allowed(staged, companion)
            )

    def test_an_explicitly_empty_carrier_set_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            deck.write_bytes(b"canonical PowerPoint artifact")

            with self.assertRaises(assignment_submission.GateError):
                assignment_submission.stage(
                    root,
                    deck,
                    artifact_approved=True,
                    approved_carriers=(),
                )

    def test_an_explicit_carrier_set_lists_every_file_and_refuses_an_extra(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            companion = root / "named-companion.pdf"
            extra = root / "unapproved.docx"
            for path in (deck, companion, extra):
                path.write_bytes(path.name.encode("utf-8"))

            staged = assignment_submission.stage(
                root,
                deck,
                artifact_approved=True,
                approved_carriers=(deck, companion),
            )

            self.assertEqual(
                "ATTACHMENT-COUNT: 2\n"
                "FILENAME: assignment.pptx\n"
                "FILENAME: named-companion.pdf",
                assignment_submission.approval_surface(staged),
            )
            with self.assertRaises(assignment_submission.GateError):
                assignment_submission.confirm(
                    staged,
                    uploaded_carriers=(deck, companion, extra),
                    final_confirmation=True,
                )

    def test_final_confirmation_requires_the_exact_approved_population(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            companion = root / "named-companion.pdf"
            deck.write_bytes(b"canonical PowerPoint artifact")
            companion.write_bytes(b"approved companion")
            staged = assignment_submission.stage(
                root,
                deck,
                artifact_approved=True,
                approved_carriers=(deck, companion),
            )

            with self.assertRaises(assignment_submission.GateError):
                assignment_submission.confirm(
                    staged,
                    uploaded_carriers=(deck,),
                    final_confirmation=True,
                )

            assignment_submission.confirm(
                staged,
                uploaded_carriers=(deck, companion),
                final_confirmation=True,
            )
            self.assertTrue(assignment_submission.submit_is_authorized(staged))

    def test_final_confirmation_applies_only_while_the_staged_bytes_still_match(self):
        with tempfile.TemporaryDirectory() as directory:
            docx = Path(directory) / "assignment.docx"
            docx.write_bytes(b"canonical Word artifact")
            staged = assignment_submission.stage(
                Path(directory), docx, artifact_approved=True
            )

            assignment_submission.confirm(
                staged, uploaded_carriers=(docx,), final_confirmation=True
            )
            self.assertTrue(assignment_submission.submit_is_authorized(staged))
            failed, report = assignment_submission.completion_gate(
                Path(directory), docx
            )
            self.assertFalse(failed, report)
            docx.write_bytes(b"changed after review")
            self.assertFalse(assignment_submission.submit_is_authorized(staged))
            failed, _ = assignment_submission.completion_gate(Path(directory), docx)
            self.assertTrue(failed)

    def test_completion_requires_the_posted_filename_population(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            canonical_root = root / "canonical-output"
            canonical = canonical_root / "course-assignments" / deck.name
            deck.write_bytes(b"canonical PowerPoint artifact")
            canonical.parent.mkdir(parents=True)
            canonical.write_bytes(deck.read_bytes())
            staged = assignment_submission.stage(root, deck, artifact_approved=True)
            assignment_submission.confirm(
                staged, uploaded_carriers=(deck,), final_confirmation=True
            )
            (root / "reread.md").write_text(
                "## REREAD: assignment\n"
                "POST-URL: https://example.test/submission\n"
                "POSTED: 2026-09-23\n"
                "READ: 2026-09-23\n"
                "ATTACHMENT-COUNT: 1\n"
                "SUBMITTED-FILE: assignment.pptx\n"
                "SUBMISSION-SHA256: " + assignment_submission.file_digest.sha256(deck) + "\n"
                "VERDICT: matches - the posted file population and artifact match\n",
                encoding="utf-8",
            )

            with mock.patch.object(
                assignment_submission.repo_root,
                "output_root",
                return_value=canonical_root,
            ):
                failed, report = assignment_submission.completion_gate(
                    root, deck, submission="assignment"
                )
            self.assertFalse(failed, report)

            reread = root / "reread.md"
            reread.write_text(
                reread.read_text(encoding="utf-8").replace(
                    "SUBMITTED-FILE: assignment.pptx",
                    "SUBMITTED-FILE: review-notes.docx",
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                assignment_submission.repo_root,
                "output_root",
                return_value=canonical_root,
            ):
                failed, _ = assignment_submission.completion_gate(
                    root, deck, submission="assignment"
                )
            self.assertTrue(failed)

    def test_completion_requires_the_posted_fingerprint_and_matching_verdict(self):
        replacements = (
            ("SUBMISSION-SHA256: {digest}", "SUBMISSION-SHA256: " + "f" * 64),
            (
                "VERDICT: matches - the posted file population and artifact match",
                "VERDICT: diverges - the posted artifact differs",
            ),
            (
                "VERDICT: matches - the posted file population and artifact match",
                "VERDICT: matches",
            ),
        )
        for old, new in replacements:
            with self.subTest(new=new), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                docx = root / "assignment.docx"
                canonical_root = root / "canonical-output"
                canonical = canonical_root / "course-assignments" / docx.name
                docx.write_bytes(b"canonical Word artifact")
                canonical.parent.mkdir(parents=True)
                canonical.write_bytes(docx.read_bytes())
                staged = assignment_submission.stage(
                    root, docx, artifact_approved=True
                )
                assignment_submission.confirm(
                    staged, uploaded_carriers=(docx,), final_confirmation=True
                )
                digest = assignment_submission.file_digest.sha256(docx)
                reread = (
                    "## REREAD: assignment\n"
                    "POST-URL: https://example.test/submission\n"
                    "POSTED: 2026-09-23\n"
                    "READ: 2026-09-23\n"
                    "ATTACHMENT-COUNT: 1\n"
                    "SUBMITTED-FILE: assignment.docx\n"
                    "SUBMISSION-SHA256: {digest}\n"
                    "VERDICT: matches - the posted file population and artifact match\n"
                ).format(digest=digest)
                (root / "reread.md").write_text(
                    reread.replace(old.format(digest=digest), new),
                    encoding="utf-8",
                )

                with mock.patch.object(
                    assignment_submission.repo_root,
                    "output_root",
                    return_value=canonical_root,
                ):
                    failed, _ = assignment_submission.completion_gate(
                        root, docx, submission="assignment"
                    )

            self.assertTrue(failed)


if __name__ == "__main__":
    unittest.main()
