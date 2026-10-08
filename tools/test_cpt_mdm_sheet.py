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


def transcription(text="One uncomplicated problem.", *, entries=None, edition=2026, modifier_page=969):
    return (
        f"# CPT E/M MDM {edition}\n\n" +
        "".join(
            f"## Entry: {name}\nLocator: CPT Professional {edition}, p. {modifier_page if name == 'modifier-25' else 9}\n"
            f"```text\n{text if name == 'table-straightforward' else name}\n```\n\n"
            for name in sorted(sheet.REQUIRED_ENTRIES if entries is None else entries)
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

    def prepare_append(self):
        status, message = self.run_command(
            "--compare", self.first, self.second, "--output", self.output,
            "--agreement-date", "2026-09-16",
        )
        self.assertEqual(0, status, message)
        full = self.output.read_text(encoding="utf-8")
        chunks = full.split("## Entry:")
        base_text = chunks[0] + "".join(
            "## Entry:" + chunk for chunk in chunks[1:]
            if not chunk.startswith(" modifier-25\n")
        )
        base_text = base_text.replace(sheet.PERMISSION, sheet.LEGACY_PERMISSION)
        base_text = base_text.replace("Agreement date: 2026-09-16", "Agreement date: 2026-09-17", 1)
        self.base = self.root / "base.md"
        self.base.write_text(base_text, encoding="utf-8")
        self.output.unlink()
        read = transcription(entries={"modifier-25"})
        self.first.write_text(read, encoding="utf-8")
        self.second.write_text(read, encoding="utf-8")
        return base_text, full

    def append_command(self, **overrides):
        return self.run_command(
            "--compare", self.first, self.second,
            "--append-to", overrides.get("base", self.base),
            "--output", overrides.get("output", self.output),
            "--agreement-date", "2026-10-08",
        )

    def test_full_compare_refuses_missing_modifier(self):
        read = transcription(entries=sheet.REQUIRED_ENTRIES - {"modifier-25"})
        self.first.write_text(read, encoding="utf-8")
        self.second.write_text(read, encoding="utf-8")
        status, message = self.run_command(
            "--compare", self.first, self.second, "--output", self.output,
            "--agreement-date", "2026-10-08",
        )
        self.assertEqual(1, status)
        self.assertIn("modifier-25", message)
        self.assertFalse(self.output.exists())

    def test_ordinary_grade_refuses_missing_modifier(self):
        self.prepare_append()
        status, message = self.run_command(self.base)
        self.assertEqual(1, status)
        self.assertIn("modifier-25", message)

    def test_modifier_2026_requires_exact_printed_page_969(self):
        read = transcription(modifier_page=9)
        self.first.write_text(read, encoding="utf-8")
        self.second.write_text(read, encoding="utf-8")
        status, message = self.run_command(
            "--compare", self.first, self.second, "--output", self.output,
            "--agreement-date", "2026-10-08",
        )
        self.assertEqual(1, status)
        self.assertIn("printed page 969", message)
        self.assertFalse(self.output.exists())

    def test_append_preserves_old_dates_text_and_identity_and_updates_permission_once(self):
        original, _ = self.prepare_append()
        status, message = self.append_command()
        self.assertEqual(0, status, message)
        result = self.output.read_text(encoding="utf-8")
        self.assertTrue(result.startswith(original.replace(sheet.LEGACY_PERMISSION, sheet.PERMISSION)))
        self.assertEqual(1, result.count(sheet.PERMISSION))
        self.assertNotIn(sheet.LEGACY_PERMISSION, result)
        entries = sheet.grade(self.output)
        self.assertEqual("2026-10-08", entries["modifier-25"].agreed)
        self.assertEqual("2026-09-17", entries[sorted(sheet.REQUIRED_ENTRIES - {"modifier-25"})[0]].agreed)
        self.assertEqual(sheet.digest("modifier-25"), entries["modifier-25"].digest)
        self.assertEqual(original, self.base.read_text(encoding="utf-8"))

    def test_append_refuses_disagreeing_modifier_reads(self):
        self.prepare_append()
        self.second.write_text(
            transcription(entries={"modifier-25"}).replace("```text\nmodifier-25", "```text\nDifferent synthetic modifier"),
            encoding="utf-8",
        )
        status, message = self.append_command()
        self.assertEqual(1, status)
        self.assertIn("independent transcriptions disagree", message)
        self.assertFalse(self.output.exists())

    def test_append_refuses_changed_base_digest(self):
        self.prepare_append()
        self.base.write_text(
            self.base.read_text(encoding="utf-8").replace("One uncomplicated", "Two uncomplicated"),
            encoding="utf-8",
        )
        status, message = self.append_command()
        self.assertEqual(1, status)
        self.assertIn("digest", message)
        self.assertFalse(self.output.exists())

    def test_ordinary_grade_refuses_changed_modifier_digest(self):
        self.prepare_append()
        status, message = self.append_command()
        self.assertEqual(0, status, message)
        self.output.write_text(
            self.output.read_text(encoding="utf-8").replace("```text\nmodifier-25", "```text\nChanged synthetic modifier"),
            encoding="utf-8",
        )
        status, message = self.run_command(self.output)
        self.assertEqual(1, status)
        self.assertIn("modifier-25: text digest changed", message)

    def test_append_refuses_replacing_existing_modifier(self):
        _, full = self.prepare_append()
        self.base.write_text(full, encoding="utf-8")
        status, message = self.append_command()
        self.assertEqual(1, status)
        self.assertIn("cannot replace", message)
        self.assertFalse(self.output.exists())

    def test_append_refuses_mixed_edition(self):
        self.prepare_append()
        read = transcription(entries={"modifier-25"}, edition=2027, modifier_page=970)
        self.first.write_text(read, encoding="utf-8")
        self.second.write_text(read, encoding="utf-8")
        status, message = self.append_command()
        self.assertEqual(1, status)
        self.assertIn("edition", message)
        self.assertFalse(self.output.exists())

    def test_append_refuses_changed_base_source_identity(self):
        self.prepare_append()
        self.base.write_text(
            self.base.read_text(encoding="utf-8").replace("ISBN (VitalSource ebook):", "Changed ISBN:"),
            encoding="utf-8",
        )
        status, message = self.append_command()
        self.assertEqual(1, status)
        self.assertIn("ISBN", message)
        self.assertFalse(self.output.exists())

    def test_append_refuses_incomplete_old_coverage(self):
        self.prepare_append()
        self.base.write_text(
            self.base.read_text(encoding="utf-8").replace("## Entry: mdm-selection", "## Entry: missing-mdm-selection"),
            encoding="utf-8",
        )
        status, message = self.append_command()
        self.assertEqual(1, status)
        self.assertIn("incomplete", message)
        self.assertFalse(self.output.exists())

    def test_append_refuses_other_entries_and_base_output_alias(self):
        self.prepare_append()
        status, message = self.append_command(output=self.base)
        self.assertEqual(1, status)
        self.assertIn("must differ", message)
        read = transcription(entries={"modifier-25", "mdm-selection"})
        self.first.write_text(read, encoding="utf-8")
        self.second.write_text(read, encoding="utf-8")
        status, message = self.append_command()
        self.assertEqual(1, status)
        self.assertIn("modifier-25 only", message)
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
        next_read = transcription(edition=2027, modifier_page=970)
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
