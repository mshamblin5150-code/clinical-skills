"""Attachment identity at the public completion command. Issue #1491."""

import artifact_lock_test_support
import hashlib
import importlib
import json
import subprocess
import sys
import tempfile
import unittest
import artifact_lock_test_support
from pathlib import Path

import lms_attachments
import voice_model_identity
from prose_bind import NAMING, bind


COMMAND = Path(__file__).resolve().parent / "lms_attachments.py"


class AttachmentCommand(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name)
        self.local = self.run / "renamed.txt"
        self.local.write_bytes(b"faculty fixture")
        self.record = self.run / "lms-attachments" / "draft.md"
        self.record.parent.mkdir()

    def write_record(self):
        digest = hashlib.sha256(b"faculty fixture").hexdigest()
        self.record.write_text("ATTACHMENTS: files\n" + json.dumps([{
            "file_id": "42", "name": "faculty.txt", "size": 15,
            "sha256": digest, "local_sha256": digest,
            "local_path": str(self.local), "location_source": "found",
            "test": "sha256",
        }]), encoding="utf-8")

    def command(self, submission=True):
        return subprocess.run(
            [sys.executable, str(COMMAND), str(self.run)]
            + (["--submission", "draft"] if submission else []),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_recorded_match_accepts_a_different_local_filename(self):
        self.write_record()
        result = self.command()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("the LMS attachment identity: clean", result.stdout)

    def test_changed_local_copy_is_a_finding_even_at_the_same_size(self):
        self.write_record()
        self.local.write_bytes(b"changed fixture")
        result = self.command()
        self.assertEqual(result.returncode, 1)
        self.assertIn("local copy is missing or changed", result.stdout)

    def test_missing_record_is_a_finding_only_at_submission(self):
        self.assertEqual(self.command().returncode, 1)
        self.assertIn("record is missing", self.command().stdout)
        early = self.command(submission=False)
        self.assertEqual(early.returncode, 0)
        self.assertIn("not graded", early.stdout)

    def test_explicit_none_is_clean(self):
        self.record.write_text("ATTACHMENTS: none\n", encoding="utf-8")
        self.assertEqual(self.command().returncode, 0)

    def test_size_fallback_retains_a_local_fingerprint(self):
        self.write_record()
        header, body = self.record.read_text(encoding="utf-8").split("\n", 1)
        rows = json.loads(body)
        rows[0].update(sha256=None, test="size", location_source="clinician-supplied")
        self.record.write_text(header + "\n" + json.dumps(rows), encoding="utf-8")
        self.assertEqual(self.command().returncode, 0)
        self.local.write_bytes(b"changed fixture")
        self.assertEqual(self.command().returncode, 1)

    def test_missing_local_copy_is_a_finding(self):
        self.write_record()
        self.local.unlink()
        self.assertEqual(self.command().returncode, 1)

    def test_invalid_records_cannot_stand_for_none(self):
        self.write_record()
        valid = self.record.read_text(encoding="utf-8")
        header, body = valid.split("\n", 1)
        for field, value in (
            ("size", True), ("sha256", "b" * 64), ("local_sha256", None),
            ("location_source", "unknown"), ("local_path", "relative.txt"),
            ("test", "filename"),
        ):
            with self.subTest(field=field):
                rows = json.loads(body)
                rows[0][field] = value
                self.record.write_text(header + "\n" + json.dumps(rows), encoding="utf-8")
                self.assertEqual(self.command().returncode, 1)
        for invalid in ("", "ATTACHMENTS: files\n[]", "ATTACHMENTS: none\nextra"):
            self.record.write_text(invalid, encoding="utf-8")
            self.assertEqual(self.command().returncode, 1)

    def test_selected_reply_records_are_all_checked(self):
        self.record.write_text("ATTACHMENTS: none\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(COMMAND), str(self.run), "--submission", "draft,other.md"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("other.md: record is missing", result.stdout)

    def test_bad_submission_key_is_refused(self):
        result = subprocess.run(
            [sys.executable, str(COMMAND), str(self.run), "--submission", "../outside"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(result.returncode, 1)


class SharedContract(unittest.TestCase):
    def test_each_scoped_grader_and_branch_declares_the_shared_row(self):
        names = set(voice_model_identity.COMPLETION_GRADERS.values()) | {"deck_scan", "assignment_docx_scan"}
        for name in names:
            with self.subTest(grader=name):
                module = importlib.import_module(name)
                self.assertIn(lms_attachments.EXPECTED_ROW, module.EXPECTED_COMPLETION_CHECKS)

    def test_every_first_step_reaches_the_shared_sheet(self):
        root = Path(__file__).resolve().parents[1]
        for skill in voice_model_identity.SCOPED_SKILLS:
            with self.subTest(skill=skill):
                text = (root / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                heading = "### 1. " if skill == "practicum-case-study" else "## 1. "
                first = text.split(heading, 1)[1]
                self.assertIn("../_shared/reference/lms-attachments.md", first.split("2. ", 1)[0])

    def test_shared_sheet_names_the_limits_without_copying_them(self):
        sheet = Path(__file__).resolve().parents[1] / "skills" / "_shared" / "reference" / "lms-attachments.md"
        self.assertFalse(bind(lms_attachments.DECLARED_LIMITS, sheet.read_text(encoding="utf-8"), mode=NAMING))


if __name__ == "__main__":
    unittest.main()
