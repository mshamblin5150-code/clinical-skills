"""Public-command tests for the two-reader CPT MDM sheet.

phi-scan: synthetic
"""

import contextlib
import hashlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path

import cpt_mdm_sheet as sheet


def transcription(text="One uncomplicated problem."):
    return (
        "# CPT E/M MDM 2026\n\n" +
        "".join(
            f"## Entry: {name}\nLocator: CPT Professional 2026, p. 9\n"
            f"```text\n{text if name == 'table-straightforward' else name}\n```\n\n"
            for name in sorted(sheet.REQUIRED_ENTRIES)
        )
    )


class SheetCommand(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.first = self.root / "first.md"
        self.second = self.root / "second.md"
        self.output = self.root / "sheet.md"
        self.first.write_text(transcription(), encoding="utf-8")
        self.second.write_text(transcription("One   uncomplicated\nproblem."), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def run_command(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = sheet.main(list(map(str, args)))
        return status, out.getvalue()

    def test_two_independent_transcriptions_agree_after_whitespace_normalization(self):
        status, message = self.run_command(
            "--compare", self.first, self.second, "--output", self.output,
            "--agreement-date", "2026-09-16",
        )
        self.assertEqual(0, status, message)
        result = self.output.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(b"One uncomplicated problem.").hexdigest(), result)
        self.assertIn("Agreement date: 2026-09-16", result)

    def test_disagreement_refuses_to_publish_a_sheet(self):
        self.second.write_text(transcription("Two problems."), encoding="utf-8")
        status, message = self.run_command(
            "--compare", self.first, self.second, "--output", self.output,
            "--agreement-date", "2026-09-16",
        )
        self.assertEqual(1, status)
        self.assertIn("table-straightforward", message)
        self.assertFalse(self.output.exists())

    def test_same_transcript_path_is_not_two_independent_reads(self):
        status, message = self.run_command(
            "--compare", self.first, self.first, "--output", self.output,
            "--agreement-date", "2026-09-16",
        )
        self.assertEqual(1, status)
        self.assertIn("independent", message)

    def test_later_text_edit_without_two_reader_agreement_is_refused(self):
        self.run_command(
            "--compare", self.first, self.second, "--output", self.output,
            "--agreement-date", "2026-09-16",
        )
        self.output.write_text(
            self.output.read_text(encoding="utf-8").replace("One uncomplicated", "Two uncomplicated"),
            encoding="utf-8",
        )
        status, message = self.run_command(self.output)
        self.assertEqual(1, status)
        self.assertIn("digest", message)

    def test_incomplete_coverage_refuses_publication(self):
        self.first.write_text(self.first.read_text(encoding="utf-8").replace(
            "## Entry: mdm-two-of-three", "## Entry: missing-two-of-three"
        ), encoding="utf-8")
        self.second.write_text(self.first.read_text(encoding="utf-8"), encoding="utf-8")
        status, message = self.run_command(
            "--compare", self.first, self.second, "--output", self.output,
            "--agreement-date", "2026-09-16",
        )
        self.assertEqual(1, status)
        self.assertIn("incomplete", message)
        self.assertFalse(self.output.exists())

    def test_changed_edition_identity_blocks_valid_digest_sheet(self):
        self.run_command(
            "--compare", self.first, self.second, "--output", self.output,
            "--agreement-date", "2026-09-16",
        )
        self.output.write_text(self.output.read_text(encoding="utf-8").replace(
            "ISBN (VitalSource ebook): 9781640163232", "ISBN (VitalSource ebook): 0000000000000"
        ), encoding="utf-8")
        status, message = self.run_command(self.output)
        self.assertEqual(1, status)
        self.assertIn("ISBN", message)

    def test_next_edition_uses_supplied_rebuilt_source_database(self):
        database = self.root / "cpt-2027.sqlite"
        connection = sqlite3.connect(database)
        try:
            connection.execute(
                "CREATE TABLE source (id TEXT, title TEXT, edition TEXT, isbn TEXT, "
                "sha256 TEXT, effective_date TEXT, system TEXT)"
            )
            connection.execute(
                "INSERT INTO source VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("licensed-2027", "CPT Professional 2027", "Professional Edition 2027",
                 "ebook-2027", "a" * 64, "2027-01-01", "CPT"),
            )
            connection.commit()
        finally:
            connection.close()
        next_read = transcription().replace("2026", "2027")
        self.first.write_text(next_read, encoding="utf-8")
        self.second.write_text(next_read, encoding="utf-8")
        status, message = self.run_command(
            "--compare", self.first, self.second, "--output", self.output,
            "--agreement-date", "2027-09-16", "--database", database,
        )
        self.assertEqual(0, status, message)
        self.assertEqual(2027, next(iter(sheet.grade(self.output, database).values())).edition)
        with self.assertRaisesRegex(ValueError, "edition differs"):
            sheet.grade(self.output)

    def test_private_receipt_derives_edition_fingerprint_and_boundary_from_source_row(self):
        import json

        (sheet.ROOT / "scratch" / "sessions").mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=sheet.ROOT / "scratch" / "sessions") as private:
            destination = Path(private) / "cpt.json"
            status, message = self.run_command("--write-receipt", destination)
            self.assertEqual(0, status, message)
            receipt = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual("ama-cpt-2026-licensed", receipt["source_id"])
            self.assertEqual("Professional Edition 2026", receipt["source_edition"])
            self.assertEqual("2026-12-31", receipt["valid_through"])

    def test_receipt_refuses_an_output_outside_owning_checkout_scratch(self):
        status, message = self.run_command("--write-receipt", self.root / "cpt.json")
        self.assertEqual(1, status)
        self.assertIn("scratch", message)

    def test_receipt_refuses_loose_checkout_scratch_path(self):
        status, message = self.run_command(
            "--write-receipt", sheet.ROOT / "scratch" / "loose.json"
        )
        self.assertEqual(1, status)
        self.assertIn("sessions", message)


if __name__ == "__main__":
    unittest.main()
