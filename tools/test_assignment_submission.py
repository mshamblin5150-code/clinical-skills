"""Authorization tests for course-assignment upload carriers."""

from __future__ import annotations

import artifact_lock_test_support
import tempfile
import json
import os
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import assignment_submission
import approval_record
import file_digest
from project_context_test_support import write_none_context


class TwoGateUpload(unittest.TestCase):
    def test_a_same_name_identical_copy_in_another_folder_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            deck.write_bytes(b"approved synthetic deck")
            staged = self.stage(root, deck, artifact_approved=True)
            copy = root / "elsewhere" / deck.name
            copy.parent.mkdir()
            copy.write_bytes(deck.read_bytes())

            self.assertTrue(assignment_submission.upload_is_allowed(staged, deck))
            self.assertFalse(assignment_submission.upload_is_allowed(staged, copy))
            with self.assertRaises(assignment_submission.GateError):
                assignment_submission.confirm(
                    staged, uploaded_carriers=(copy,), clinician_reply="Submit the synthetic assignment."
                )

    def stage(self, run, artifact, **kwargs):
        if not (run / "bar.md").exists():
            from test_assignment_bar import DOCX_BAR
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
        if not (run / "project-context.md").exists():
            write_none_context(run)
        with mock.patch("approval_record.verify_clinician_reply", return_value=approval_record.ReplyVerification("verified", "synthetic reply", 4102444800)), mock.patch.object(assignment_submission.reader_remarks, "verify", return_value=[]):
            return assignment_submission.stage(run, artifact, clinician_reply="Approve the synthetic artifact.", **kwargs)

    def setUp(self) -> None:
        mock.patch("approval_record.verify_clinician_reply", return_value=approval_record.ReplyVerification("verified", "synthetic Gate 2", 4102444801)).start()
        self.pre_upload_grade = mock.patch.object(
            assignment_submission,
            "_pre_upload_grade",
            return_value=(True, "pre-upload grade: clean"),
            create=True,
        ).start()
        self.addCleanup(mock.patch.stopall)

    def test_gate2_uses_a_later_whole_human_reply(self):
        import aar_scan
        # Restore the actual matcher for the public confirm call.
        mock.patch.stopall()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            deck.write_bytes(b"synthetic")
            with mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "clean")):
                staged = self.stage(root, deck, artifact_approved=True)
            transcript = root / "session.jsonl"
            discovery = aar_scan.TranscriptDiscovery((transcript,), 1, 0, 0, 1)
            for timestamp, content, source_time, passes in (
                ("2100-01-01T00:00:01Z", "Submit the synthetic assignment.", 1, True),
                ("2100-01-01T00:00:01Z", "Different whole reply.", 1, False),
                ("2099-12-31T23:59:59Z", "Submit the synthetic assignment.", 1, False),
                ("2100-01-01T00:00:01Z", "Submit the synthetic assignment.", 4102444802, False),
                ("2100-01-01T00:00:01Z", "Submit the synthetic assignment.\n<hook-context>automated</hook-context>", 1, False),
                ("2100-01-01T00:00:01Z", "Submit the synthetic assignment.\n<scheduled-trigger>automated</scheduled-trigger>", 1, False),
            ):
                with self.subTest(timestamp=timestamp, content=content, source_time=source_time):
                    os.utime(deck, (source_time, source_time))
                    transcript.write_text(json.dumps({"type": "user", "timestamp": timestamp,
                        "message": {"content": content}}) + "\n", encoding="utf-8")
                    with mock.patch.object(aar_scan, "discover_transcripts", return_value=discovery):
                        if passes:
                            assignment_submission.confirm(staged, uploaded_carriers=(deck,), clinician_reply=content)
                            self.assertTrue(assignment_submission.submit_is_authorized(staged))
                        else:
                            with self.assertRaises(assignment_submission.GateError):
                                assignment_submission.confirm(staged, uploaded_carriers=(deck,), clinician_reply="Submit the synthetic assignment.")
            transcript.unlink()
            with mock.patch.object(aar_scan, "discover_transcripts", return_value=discovery):
                with self.assertRaises(assignment_submission.GateError):
                    assignment_submission.confirm(staged, uploaded_carriers=(deck,), clinician_reply="Submit the synthetic assignment.")

    def test_gate2_completion_requires_verified_reply_except_historical_or_clinician_upload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            deck.write_bytes(b"synthetic")
            staged = self.stage(root, deck, artifact_approved=True)
            assignment_submission.confirm(staged, uploaded_carriers=(deck,), clinician_reply="Submit the synthetic assignment.")
            record = json.loads((root / assignment_submission.RECORD).read_text(encoding="utf-8"))
            del record["gate2_clinician_reply"]
            assignment_submission._write(root / assignment_submission.RECORD, record)
            self.assertTrue(assignment_submission.completion_gate(root, deck)[0])
            self.assertFalse(assignment_submission.submit_is_authorized(staged))
            record["reply_matched_at"] = 1
            assignment_submission._write(root / assignment_submission.RECORD, record)
            self.assertTrue(assignment_submission.completion_gate(root, deck)[0])
            record.pop("gate1_recorded_at")  # A genuinely pre-build record has no recording timestamp.
            assignment_submission._write(root / assignment_submission.RECORD, record)
            failed, report = assignment_submission.completion_gate(root, deck)
            self.assertFalse(failed, report)
            self.assertIn("not graded", report)
            assignment_submission.record_clinician_upload(root, deck, uploaded_carriers=(deck,))
            self.assertFalse(assignment_submission.completion_gate(root, deck)[0])

    def test_both_skill_branches_use_the_reply_signature(self):
        import inspect
        parameters = inspect.signature(assignment_submission.confirm).parameters
        self.assertIn("clinician_reply", parameters)
        self.assertNotIn("final_confirmation", parameters)
        skill = Path(__file__).resolve().parent.parent / "skills" / "course-assignment"
        for path in (skill / "SKILL.md", skill / "references" / "docx.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("clinician_reply=", text)
            self.assertNotIn("final_confirmation=True", text)

    def test_gate2_historical_cutoff_uses_the_exact_implementation_instant(self):
        from datetime import timedelta
        start, _ = assignment_submission.completion_checks.registry()["assignment_submission:gate2-reply"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            deck.write_bytes(b"synthetic")
            self.stage(root, deck, artifact_approved=True)
            record = assignment_submission._read(root)
            record.update(upload_route="agent", uploaded_files=[deck.name])
            for observed, expected_failure in ((start - timedelta(microseconds=1), False), (start, True)):
                with self.subTest(observed=observed):
                    record["gate1_recorded_at"] = observed.timestamp()
                    assignment_submission._write(root / assignment_submission.RECORD, record)
                    failed, report = assignment_submission.completion_gate(root, deck)
                    self.assertEqual(expected_failure, failed, report)
                    if not expected_failure:
                        self.assertIn("not graded", report)

    @contextmanager
    def _canonical_copy(
        self, canonical_root: Path, artifact: Path
    ) -> Iterator[Path]:
        canonical = canonical_root / "course-assignments" / artifact.name
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_bytes(artifact.read_bytes())
        with mock.patch.object(
            assignment_submission.repo_root,
            "output_root",
            return_value=canonical_root,
        ):
            yield canonical

    def _completed_submission(self, root: Path, artifact: Path) -> None:
        staged = self.stage(root, artifact, artifact_approved=True)
        with mock.patch("approval_record.verify_clinician_reply", return_value=approval_record.ReplyVerification("verified", "synthetic Gate 2", 4102444801)):
            assignment_submission.confirm(
                staged, uploaded_carriers=(artifact,), clinician_reply="Submit the synthetic assignment."
            )
        (root / "reread.md").write_text(
            "## REREAD: assignment\n"
            "POST-URL: https://example.test/submission\n"
            "POSTED: 2026-09-23\n"
            "READ: 2026-09-23\n"
            "ATTACHMENT-COUNT: 1\n"
            f"SUBMITTED-FILE: {artifact.name}\n"
            f"POSTED-FILE: {artifact.name} | sha256={file_digest.sha256(artifact)} | route=page\n"
            f"SUBMISSION-SHA256: {file_digest.sha256(artifact)}\n"
            "VERDICT: matches - the posted artifact matches the reviewed file\n",
            encoding="utf-8",
        )

    def test_terminal_completion_names_and_matches_the_canonical_output_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "worktree" / "scratch" / "runs" / "assignment"
            reviewed = root / "worktree" / "output" / "course-assignments" / "assignment.pptx"
            run.mkdir(parents=True)
            reviewed.parent.mkdir(parents=True)
            reviewed.write_bytes(b"reviewed deck")
            self._completed_submission(run, reviewed)

            with self._canonical_copy(root / "owning" / "output", reviewed) as canonical:
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
            run.mkdir()
            reviewed.parent.mkdir(parents=True)
            reviewed.write_bytes(b"reviewed deck")
            self._completed_submission(run, reviewed)

            with self._canonical_copy(canonical_root, reviewed) as canonical:
                canonical.write_bytes(b"older deck")
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
            write_none_context(root)
            replace_file = assignment_submission.os.replace

            def fail_approval_write(source, destination):
                if Path(destination).name == assignment_submission.RECORD:
                    raise OSError("busy")
                return replace_file(source, destination)

            with mock.patch.object(
                assignment_submission.os, "replace", side_effect=fail_approval_write
            ):
                with self.assertRaises(OSError):
                    self.stage(root, docx, artifact_approved=True)

            self.assertEqual((), tuple(root.glob("*.building")))

    def test_approval_is_refused_until_the_run_directory_pre_upload_grade_is_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            deck.write_bytes(b"reviewed deck")
            self.pre_upload_grade.return_value = (
                False,
                "pre-upload grade: not clean - review records are missing",
            )

            with self.assertRaisesRegex(
                assignment_submission.GateError, "review records are missing"
            ):
                self.stage(root, deck, artifact_approved=True)

            self.pre_upload_grade.assert_called_once_with(root.resolve(), deck.resolve())
            self.assertFalse((root / assignment_submission.RECORD).exists())

    def test_artifact_approval_only_authorizes_staging_the_exact_docx(self):
        with tempfile.TemporaryDirectory() as directory:
            docx = Path(directory) / "assignment.docx"
            docx.write_bytes(b"canonical Word artifact")

            staged = self.stage(
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
            record = assignment_submission._read(Path(directory))
            self.assertEqual("awaiting-upload", record["upload_route"])
            self.assertNotIn("gate2_confirmed", record)
            self.assertNotIn("clinician_upload_recorded", record)

    def test_default_carrier_set_excludes_a_review_companion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            companion = root / "review-notes.docx"
            deck.write_bytes(b"canonical PowerPoint artifact")
            companion.write_bytes(b"private review companion")

            staged = self.stage(
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
                self.stage(
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

            staged = self.stage(
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
                    clinician_reply="Submit the synthetic assignment.",
                )

    def test_final_confirmation_requires_the_exact_approved_population(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            companion = root / "named-companion.pdf"
            deck.write_bytes(b"canonical PowerPoint artifact")
            companion.write_bytes(b"approved companion")
            staged = self.stage(
                root,
                deck,
                artifact_approved=True,
                approved_carriers=(deck, companion),
            )

            with self.assertRaises(assignment_submission.GateError):
                assignment_submission.confirm(
                    staged,
                    uploaded_carriers=(deck,),
                    clinician_reply="Submit the synthetic assignment.",
                )

            assignment_submission.confirm(
                staged,
                uploaded_carriers=(deck, companion),
                clinician_reply="Submit the synthetic assignment.",
            )
            self.assertTrue(assignment_submission.submit_is_authorized(staged))

    def test_final_confirmation_applies_only_while_the_staged_bytes_still_match(self):
        with tempfile.TemporaryDirectory() as directory:
            docx = Path(directory) / "assignment.docx"
            docx.write_bytes(b"canonical Word artifact")
            staged = self.stage(
                Path(directory), docx, artifact_approved=True
            )

            assignment_submission.confirm(
                staged, uploaded_carriers=(docx,), clinician_reply="Submit the synthetic assignment."
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
            deck.write_bytes(b"canonical PowerPoint artifact")
            staged = self.stage(root, deck, artifact_approved=True)
            assignment_submission.confirm(
                staged, uploaded_carriers=(deck,), clinician_reply="Submit the synthetic assignment."
            )
            (root / "reread.md").write_text(
                "## REREAD: assignment\n"
                "POST-URL: https://example.test/submission\n"
                "POSTED: 2026-09-23\n"
                "READ: 2026-09-23\n"
                "ATTACHMENT-COUNT: 1\n"
                "SUBMITTED-FILE: assignment.pptx\n"
                f"POSTED-FILE: assignment.pptx | sha256={file_digest.sha256(deck)} | route=page\n"
                "SUBMISSION-SHA256: " + assignment_submission.file_digest.sha256(deck) + "\n"
                "VERDICT: matches - the posted file population and artifact match\n",
                encoding="utf-8",
            )

            with self._canonical_copy(canonical_root, deck):
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

    def test_an_approved_clinician_upload_completes_after_the_matching_posted_reading(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            canonical_root = root / "canonical-output"
            deck.write_bytes(b"reviewed deck")
            self.stage(root, deck, artifact_approved=True)
            assignment_submission.record_clinician_upload(
                root, deck, uploaded_carriers=(deck,)
            )
            self.assertEqual(
                "clinician", assignment_submission._read(root)["upload_route"]
            )
            (root / "reread.md").write_text(
                "## REREAD: assignment\n"
                "POST-URL: https://example.test/submission\n"
                "POSTED: 2026-09-25\n"
                "READ: 2026-09-25\n"
                "ATTACHMENT-COUNT: 1\n"
                "SUBMITTED-FILE: assignment.pptx\n"
                f"SUBMISSION-SHA256: {file_digest.sha256(deck)}\n"
                f"POSTED-FILE: assignment.pptx | sha256={file_digest.sha256(deck)} | route=page\n"
                "VERDICT: matches - the clinician-uploaded deck matches the approved artifact\n",
                encoding="utf-8",
            )

            with self._canonical_copy(canonical_root, deck):
                failed, report = assignment_submission.completion_gate(
                    root, deck, submission="assignment"
                )

        self.assertFalse(failed, report)

    def test_posted_fingerprints_bind_every_approved_carrier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            companion = root / "notes.docx"
            deck.write_bytes(b"approved deck")
            companion.write_bytes(b"approved notes")
            staged = self.stage(root, deck, artifact_approved=True, approved_carriers=(deck, companion))
            assignment_submission.confirm(staged, uploaded_carriers=(deck, companion), clinician_reply="Submit the synthetic assignment.")
            baseline = (
                "## REREAD: assignment\nPOST-URL: https://example.test/submission\n"
                "POSTED: 2026-10-12\nREAD: 2026-10-12\nATTACHMENT-COUNT: 2\n"
                "SUBMITTED-FILE: assignment.pptx\nSUBMITTED-FILE: notes.docx\n"
                f"SUBMISSION-SHA256: {file_digest.sha256(deck)}\n"
                f"POSTED-FILE: assignment.pptx | sha256={file_digest.sha256(deck)} | route=page\n"
                f"POSTED-FILE: notes.docx | sha256={file_digest.sha256(companion)} | route=page\n"
                "VERDICT: matches - both approved attachments were read\n"
            )
            note_line = f"POSTED-FILE: notes.docx | sha256={file_digest.sha256(companion)} | route=page\n"
            (root / "posted").mkdir()
            supplied = root / "posted" / companion.name
            supplied.write_bytes(companion.read_bytes())
            supplied_line = note_line.replace("route=page", "route=clinician-supplied | path=posted/notes.docx")
            cases = (
                (baseline, False),
                (baseline.replace(note_line, ""), True),
                (baseline.replace(note_line, note_line * 2), True),
                (baseline.replace(file_digest.sha256(companion), "f" * 64), True),
                (baseline.replace(note_line, supplied_line), False),
            )
            with self._canonical_copy(root / "canonical-output", deck):
                for text, expected in cases:
                    with self.subTest(text=text):
                        (root / "reread.md").write_text(text, encoding="utf-8")
                        failed, report = assignment_submission.completion_gate(root, deck, submission="assignment")
                        self.assertEqual(expected, failed, report)
                supplied.write_bytes(b"changed notes")
                (root / "reread.md").write_text(baseline.replace(note_line, supplied_line), encoding="utf-8")
                self.assertTrue(assignment_submission.completion_gate(root, deck, submission="assignment")[0])

    def test_a_clinician_upload_without_recorded_approval_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deck = root / "assignment.pptx"
            deck.write_bytes(b"unapproved deck")

            with self.assertRaisesRegex(
                assignment_submission.GateError, "recorded approval"
            ):
                assignment_submission.record_clinician_upload(
                    root, deck, uploaded_carriers=(deck,)
                )

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
                docx.write_bytes(b"canonical Word artifact")
                staged = self.stage(
                    root, docx, artifact_approved=True
                )
                assignment_submission.confirm(
                    staged, uploaded_carriers=(docx,), clinician_reply="Submit the synthetic assignment."
                )
                digest = assignment_submission.file_digest.sha256(docx)
                reread = (
                    "## REREAD: assignment\n"
                    "POST-URL: https://example.test/submission\n"
                    "POSTED: 2026-09-23\n"
                    "READ: 2026-09-23\n"
                    "ATTACHMENT-COUNT: 1\n"
                    "SUBMITTED-FILE: assignment.docx\n"
                    "POSTED-FILE: assignment.docx | sha256={digest} | route=page\n"
                    "SUBMISSION-SHA256: {digest}\n"
                    "VERDICT: matches - the posted file population and artifact match\n"
                ).format(digest=digest)
                (root / "reread.md").write_text(
                    reread.replace(old.format(digest=digest), new),
                    encoding="utf-8",
                )

                with self._canonical_copy(canonical_root, docx):
                    failed, _ = assignment_submission.completion_gate(
                        root, docx, submission="assignment"
                    )

            self.assertTrue(failed)


if __name__ == "__main__":
    unittest.main()
