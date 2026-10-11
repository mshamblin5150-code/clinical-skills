"""ADR 0322's local-document contract through the public ledger command."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_research_ledger import CLEAN, ledger_text, replace_field
import research_ledger as ledger
from datetime import date

COMMAND = Path(__file__).resolve().parent / "research_ledger.py"


class OwnWorkLedger(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.document = self.root / "Local policy.md"
        self.document.write_bytes(b"Policy completed 2009. Synthetic reference range table.")
        self.digest = hashlib.sha256(self.document.read_bytes()).hexdigest()
        self.claims = self.root / "claims.md"
        self.record = replace_field(CLEAN, "SOURCE", "clinician's own work")
        self.record = replace_field(self.record, "RESOLVED", self.locator())
        self.record = replace_field(self.record, "PAGE-YEAR", "2009 - document statement: completion line.")
        self.record = replace_field(self.record, "SECOND-ROUTE", self.route())
        (self.root / "bar.md").write_text(
            "SIGNED: 2026-08-19\nSOURCE-CLASSES: clinician's own work\nRECENCY-WINDOW-YEARS: 5\n",
            encoding="utf-8",
        )

    def locator(self):
        return f"{self.document} | SHA256: {self.digest} - read 2026-08-19"

    def route(self):
        return f"author document read -> refuter opened {self.document} | SHA256: {self.digest}"

    def run_command(self):
        self.claims.write_text(ledger_text(self.record), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(COMMAND), str(self.claims)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_signed_local_document_is_clean(self):
        result = self.run_command()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_moved_document_is_unread(self):
        self.document.rename(self.root / "Moved.md")
        result = self.run_command()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stderr + result.stdout)
        self.assertRegex(result.stdout, r"records at fault\s+0")

    def test_changed_document_is_unread(self):
        self.document.write_bytes(b"A different policy.")
        result = self.run_command()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stderr + result.stdout)

    def test_finding_wins_over_changed_document(self):
        self.document.write_bytes(b"A different policy.")
        self.record = replace_field(self.record, "RECENCY", "current")
        result = self.run_command()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stderr + result.stdout)

    def test_unsigned_class_is_a_finding(self):
        (self.root / "bar.md").write_text(
            "SOURCE-CLASSES: peer-reviewed\nRECENCY-WINDOW-YEARS: 5\n", encoding="utf-8",
        )
        result = self.run_command()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertRegex(result.stdout, r"unknown-source-class\s+1")

    def test_own_work_opt_in_requires_a_signed_bar(self):
        for signature in (
            "", "SIGNED: 2026-02-30\n", "SIGNED: pending\n",
            "SIGNED: 2026-08-19\nSIGNED: pending\n",
        ):
            with self.subTest(signature=signature):
                (self.root / "bar.md").write_text(
                    signature + "SOURCE-CLASSES: clinician's  own work\nRECENCY-WINDOW-YEARS: 5\n",
                    encoding="utf-8",
                )
                result = self.run_command()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertRegex(result.stdout, r"unknown-source-class\s+1")

    def test_no_bar_admits_neither_own_work_nor_market_source(self):
        (self.root / "bar.md").unlink()
        for source in ("clinician's own work", "market source"):
            with self.subTest(source=source):
                self.record = replace_field(CLEAN, "SOURCE", source)
                result = self.run_command()
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("needs bar.md", result.stderr)
                scan = ledger.survey(ledger.read_records(ledger_text(self.record)), date(2026, 8, 19))
                self.assertEqual(dict(scan.counts)[ledger.UNKNOWN_SOURCE_CLASS], 1)

    def test_local_locator_requires_absolute_path_and_lowercase_digest(self):
        for locator in (
            self.locator().replace(str(self.document), self.document.name),
            self.locator().replace(self.digest, self.digest.upper()),
            self.locator().replace(" | SHA256: " + self.digest, ""),
            "https://example.org/search - read 2026-08-19",
        ):
            with self.subTest(locator=locator):
                self.record = replace_field(self.record, "RESOLVED", locator)
                result = self.run_command()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertRegex(result.stdout, r"unresolvable-locator\s+[1-9]")

    def test_local_locator_keeps_the_read_date_checks(self):
        for value, row in (
            (self.locator().replace(" - read 2026-08-19", ""), "undated-read"),
            (self.locator().replace("2026-08-19", "2099-01-01"), "read-after-date"),
        ):
            with self.subTest(row=row):
                self.record = replace_field(self.record, "RESOLVED", value)
                result = self.run_command()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertRegex(result.stdout, row + r"\s+1")

    def test_refuter_must_record_same_path_and_digest(self):
        for route in (
            self.route().replace(self.digest, "0" * 64),
            self.route().replace(str(self.document), str(self.root / "Other.md")),
            "author document read -> refuter document read",
        ):
            with self.subTest(route=route):
                self.record = replace_field(self.record, "SECOND-ROUTE", route)
                result = self.run_command()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_year_names_one_of_the_ruled_sources(self):
        for source in ("document statement", "internal metadata last-modified", "clinician's answer"):
            with self.subTest(source=source):
                self.record = replace_field(self.record, "PAGE-YEAR", f"2009 - {source}: recorded completion year.")
                result = self.run_command()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.record = replace_field(self.record, "PAGE-YEAR", "2009 - file-system modified date.")
        result = self.run_command()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertRegex(result.stdout, r"page-year-form\s+1")

    def test_other_classes_keep_the_web_locator(self):
        self.record = replace_field(CLEAN, "RESOLVED", self.locator())
        (self.root / "bar.md").write_text(
            "SOURCE-CLASSES: peer-reviewed\nRECENCY-WINDOW-YEARS: 5\n", encoding="utf-8",
        )
        result = self.run_command()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertRegex(result.stdout, r"unresolvable-locator\s+1")


if __name__ == "__main__":
    unittest.main()
