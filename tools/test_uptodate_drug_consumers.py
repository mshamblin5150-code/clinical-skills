"""Filed drug pages through the clinical and coursework command boundaries."""
from __future__ import annotations

import contextlib
import io
from datetime import date
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import research_ledger as ledger
import test_encounter_uptodate as encounter
from test_research_ledger import CLEAN, ledger_text, replace_field, write_bar


class DrugConsumers(unittest.TestCase):
    setUp = encounter.EncounterUpToDate.setUp
    ingest = encounter.EncounterUpToDate.ingest
    scan = encounter.EncounterUpToDate.scan

    def drug(self, title="Sample: Drug information", read_on=None, dump="drug"):
        read_on = read_on or date.today().isoformat()
        section = "Pediatric" if "Pediatric" in title else "Adult"
        html = (f"<h1>{title}</h1><h2>Dosing: {section}</h2>"
                '<span class="collapsible-indication-title" aria-expanded="true">Sample indication</span>'
                '<p>Oral: 5 mg daily.</p><div>Topic 123 Version 1.0</div>')
        self.assertEqual(0, self.ingest(dump, html, "--drug-page", "--read-on", read_on))
        self.drug_source = self.run / f"{dump}.txt"

    def test_drug_tail_compares_exact_title_version_and_freshness(self):
        self.drug()
        status, report = self.scan("[uptodate drug: Sample: Drug information, version 1.0, drug]")
        self.assertEqual(0, status, report)
        self.assertIn("guideline tails checked against source evidence  1", report)
        for tail in (
            "[uptodate drug: Sample: Drug information, version 2.0, drug]",
            "[uptodate drug: Sample: Pediatric drug information, version 1.0, drug]",
            "[uptodate drug over thresholds/hypertension row: Sample: Drug information, version 1.0, drug]",
        ):
            with self.subTest(tail=tail):
                status, report = self.scan(tail)
                self.assertEqual(1, status, report)
                self.assertIn("guideline tails checked against source evidence  0", report)
        self.drug(read_on=date(2000, 1, 1).isoformat(), dump="old")
        self.assertEqual(1, self.scan("[uptodate drug: Sample: Drug information, version 1.0, old]")[0])

    def coursework(self, title, reference_title=None):
        entry = (f"Drug Author. (n.d.). *{reference_title or title}* [Drug information]. UpToDate. "
                 "Retrieved August 19, 2026, from https://www.uptodate.com/contents/sample")
        record = replace_field(CLEAN, "REFERENCE", entry)
        record = replace_field(record, "PAGE-YEAR", "no year stated on this changing drug page")
        record = replace_field(record, "RECENCY", "current")
        claims = self.run / "claims.md"
        claims.write_text(ledger_text(record), encoding="utf-8")
        write_bar(self.run)
        with contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()), \
             mock.patch.object(ledger, "clinician_has_uptodate_account", return_value=False):
            status = ledger.main([str(claims), "--evidence", str(self.drug_source), "--show"])
        return status, output.getvalue()

    def test_current_undated_drug_reference_joins(self):
        title = "Sample: Drug information"
        self.drug(title, read_on=date(2026, 8, 18).isoformat())
        status, report = self.coursework(title)
        self.assertEqual(0, status, report)

    def test_old_drug_requires_refresh_even_without_an_account(self):
        # Even a clinician without a current account must refresh an old drug
        # page; the topic review-window waiver does not waive the drug's year.
        title = "Sample: Drug information"
        self.drug(title, read_on=date(2000, 1, 1).isoformat(), dump="old")
        status, report = self.coursework(title)
        self.assertEqual(1, status, report)
        self.assertIn(ledger.UPTODATE_REREAD_DUE, report)

    def test_pediatric_reference_requires_its_own_filed_page(self):
        self.drug(read_on=date(2026, 8, 18).isoformat())
        status, report = self.coursework("Sample: Drug information", "Sample: Pediatric drug information")
        self.assertEqual(1, status, report)
        self.assertIn(ledger.CITED_TOPIC_NOT_IN_EVIDENCE, report)
        self.drug("Sample: Pediatric drug information", read_on=date(2026, 8, 18).isoformat(), dump="pediatric")
        status, report = self.coursework("Sample: Pediatric drug information")
        self.assertEqual(0, status, report)

    def test_pediatric_tail_resolves_its_own_filed_page(self):
        self.drug("Sample: Pediatric drug information", dump="pediatric")
        status, report = self.scan("[uptodate drug: Sample: Pediatric drug information, version 1.0, pediatric]")
        self.assertEqual(0, status, report)


if __name__ == "__main__":
    unittest.main()
