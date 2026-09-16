"""Public-seam tests for the batch coding-freshness gate.

phi-scan: synthetic
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from code_set_database_test_support import (
    ICD10_DATABASE_SHA256,
    PROCEDURE_CODES_DATABASE_SHA256,
    assert_code_set_database_digest,
)

ROOT = Path(__file__).resolve().parent.parent
assert_code_set_database_digest(
    ROOT / "reference" / "icd10cm-2026.sqlite",
    ICD10_DATABASE_SHA256,
    "ICD-10-CM Code-set database",
)
assert_code_set_database_digest(
    ROOT / "reference" / "procedure-codes-2026.sqlite",
    PROCEDURE_CODES_DATABASE_SHA256,
    "procedure-code Code-set database",
)

import coding_freshness as gate
import cpt_mdm_sheet


ICD_PAGE = """
April 1, 2026, ICD-10-CM release
FY26 ICD-10-CM codes should be used for healthcare services provided from
April 1, 2026, through September 30, 2026.
"""

HCPCS_PAGE = """
October 2026 Alpha-Numeric HCPCS File (ZIP) - Updated 09/10/2026
July 2026 Alpha-Numeric HCPCS File (ZIP) - Updated 06/17/2026
"""


class CodingFreshnessMain(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.content_hash = "a" * 64
        self.manifest = self.directory / "manifest.json"
        self.manifest.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "service_date": "2026-08-17",
                    "encounters": [
                        {
                            "id": "note-1",
                            "order": 1,
                            "setting": "office",
                            "normalized_sha256": self.content_hash,
                            "patient_status": {
                                "value": "established",
                                "evidence": "identity-map",
                                "evidence_sha256": "b" * 64,
                            },
                            "codes": {
                                "icd10": ["M54.50"],
                                "em": "99214",
                                "cpt": [],
                                "hcpcs": ["J1100"],
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.cpt_receipt = self.directory / "cpt-receipt.json"
        self.cpt_receipt.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "source_id": "ama-cpt-2026-licensed",
                    "source_edition": "Professional Edition 2026",
                    "source_sha256": (
                        "95e657dee044bf8f24683063ee09dbab12274dd09a3558eac1c498c37d60f8ce"
                    ),
                    "valid_through": "2026-12-31",
                }
            ),
            encoding="utf-8",
        )
        self.output = self.directory / "freshness.json"
        (self.directory / "reference").mkdir()
        self.mdm_sheet = self.directory / "reference" / "cpt-em-mdm-2026.md"
        first = self.directory / "first.md"
        second = self.directory / "second.md"
        read = (
            "# CPT E/M MDM 2026\n\n" +
            "".join(
                f"## Entry: {name}\nLocator: CPT Professional 2026, p. 10\n"
                f"```text\n{'Moderate decisions.' if name == 'table-moderate' else name}\n```\n\n"
                for name in sorted(cpt_mdm_sheet.REQUIRED_ENTRIES)
            )
        )
        first.write_text(read, encoding="utf-8")
        second.write_text(read, encoding="utf-8")
        cpt_mdm_sheet.compare(first, second, self.mdm_sheet, "2026-09-16")

    def tearDown(self):
        self.temporary.cleanup()

    def load_manifest(self) -> dict:
        return json.loads(self.manifest.read_text(encoding="utf-8"))

    def save_manifest(self, value: dict) -> None:
        self.manifest.write_text(json.dumps(value), encoding="utf-8")

    def run_gate(self, pages: tuple[str, str] = (ICD_PAGE, HCPCS_PAGE),
                 committed_error: bool = False) -> tuple[int, str]:
        stdout = io.StringIO()
        with (
            patch.object(gate, "read_url", side_effect=pages),
            patch.object(gate, "today", return_value=gate.date(2026, 9, 15)),
            patch.object(gate, "ROOT", self.directory),
            patch.object(gate, "committed_sheet_sha256", return_value="c" * 64,
                         side_effect=ValueError("not committed") if committed_error else None),
            contextlib.redirect_stdout(stdout),
        ):
            status = gate.main(
                [
                    str(self.manifest),
                    "--cpt-receipt",
                    str(self.cpt_receipt),
                    "--receipt",
                    str(self.output),
                ]
            )
        return status, stdout.getvalue()

    def test_pass_binds_order_content_status_codes_and_sources(self):
        status, output = self.run_gate()

        self.assertEqual(0, status, output)
        self.assertEqual("coding-freshness: PASS\n", output)
        receipt = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual("PASS", receipt["verdict"])
        self.assertEqual(self.content_hash, receipt["encounters"][0]["normalized_sha256"])
        self.assertEqual("note-1", receipt["encounters"][0]["id"])
        self.assertEqual("99214", receipt["encounters"][0]["codes"]["em"])
        self.assertIn("database_sha256", receipt["sources"]["cpt"])
        self.assertEqual(self.mdm_sheet.name, receipt["sources"]["cpt"]["mdm_sheet_filename"])
        self.assertEqual(64, len(receipt["sources"]["cpt"]["mdm_sheet_sha256"]))

    def test_missing_or_tampered_mdm_sheet_refuses_final_em(self):
        self.mdm_sheet.write_text(
            self.mdm_sheet.read_text(encoding="utf-8").replace("Moderate decisions", "High decisions"),
            encoding="utf-8",
        )
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("MDM sheet", output)
        self.assertFalse(self.output.exists())

    def test_cpt_receipt_is_judged_by_service_date_not_check_date(self):
        value = self.load_manifest()
        value["service_date"] = "2026-12-20"
        self.save_manifest(value)
        stdout = io.StringIO()
        extended_icd_page = ICD_PAGE.replace("September 30, 2026", "December 31, 2026")
        with (
            patch.object(gate, "read_url", side_effect=(extended_icd_page, HCPCS_PAGE)),
            patch.object(gate, "today", return_value=gate.date(2027, 1, 4)),
            patch.object(gate, "ROOT", self.directory),
            patch.object(gate, "committed_sheet_sha256", return_value="c" * 64),
            contextlib.redirect_stdout(stdout),
        ):
            status = gate.main([
                str(self.manifest), "--cpt-receipt", str(self.cpt_receipt),
                "--receipt", str(self.output),
            ])
        self.assertEqual(0, status, stdout.getvalue())
        self.assertEqual("coding-freshness: PASS\n", stdout.getvalue())

    def test_sheet_must_match_committed_blob(self):
        import subprocess

        sheet = self.mdm_sheet
        original = sheet.read_bytes()
        with (
            patch.object(gate, "ROOT", self.directory),
            patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, original)),
        ):
            self.assertEqual(64, len(gate.committed_sheet_sha256(sheet)))
            sheet.write_bytes(original.replace(b"Moderate decisions", b"Altered decisions"))
            with self.assertRaisesRegex(ValueError, "differs from its committed version"):
                gate.committed_sheet_sha256(sheet)

    def test_uncommitted_sheet_refuses_final_em(self):
        status, output = self.run_gate(committed_error=True)
        self.assertEqual(1, status)
        self.assertIn("not committed", output)

    def test_next_edition_service_date_has_no_2026_mdm_coverage(self):
        value = self.load_manifest()
        value["service_date"] = "2027-01-02"
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("CPT freshness receipt expired", output)
        self.assertIn("E/M MDM sheet is missing or invalid", output)

    def test_ed_em_does_not_require_new_or_established_patient_status(self):
        value = self.load_manifest()
        value["encounters"][0]["setting"] = "emergency-department"
        value["encounters"][0]["codes"]["em"] = "99283"
        value["encounters"][0]["patient_status"] = {"value": "not-applicable"}
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(0, status, output)

    def test_unstated_or_mismatched_setting_refuses_em(self):
        value = self.load_manifest()
        del value["encounters"][0]["setting"]
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("stated place of service", output)

        value["encounters"][0]["setting"] = "emergency-department"
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("stated place of service", output)

    def test_stale_icd_release_still_listed_beside_the_applicable_one_blocks(self):
        page = ICD_PAGE.replace(
            "April 1, 2026, ICD-10-CM release",
            "April 1, 2025, ICD-10-CM release",
        )
        status, output = self.run_gate((page, HCPCS_PAGE))
        self.assertEqual(1, status)
        self.assertIn("ICD-10-CM authoritative release is unread or stale", output)

    def test_newer_published_hcpcs_release_blocks_an_older_database(self):
        page = "January 2027 Alpha-Numeric HCPCS File (ZIP) - Updated 09/12/2026\n" + HCPCS_PAGE
        status, output = self.run_gate((ICD_PAGE, page))
        self.assertEqual(1, status)
        self.assertIn("HCPCS authoritative release is unread or stale", output)

    def test_duplicate_encounter_membership_blocks(self):
        value = self.load_manifest()
        duplicate = dict(value["encounters"][0])
        duplicate["order"] = 2
        value["encounters"].append(duplicate)
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("encounter ids are not unique", output)

    def test_noncontiguous_order_blocks(self):
        value = self.load_manifest()
        value["encounters"][0]["order"] = 2
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("encounter order is not exactly 1 through 1", output)

    def test_missing_normalized_content_hash_blocks(self):
        value = self.load_manifest()
        value["encounters"][0]["normalized_sha256"] = ""
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("normalized content hash is unreadable", output)

    def test_empty_required_code_population_blocks(self):
        value = self.load_manifest()
        value["encounters"][0]["codes"]["icd10"] = []
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("has no final ICD-10-CM code", output)

    def test_unknown_patient_status_blocks(self):
        value = self.load_manifest()
        value["encounters"][0]["patient_status"] = {
            "value": "unknown",
            "evidence": "none",
        }
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("patient status is not account-backed", output)

    def test_a_bare_evidence_label_does_not_back_patient_status(self):
        value = self.load_manifest()
        del value["encounters"][0]["patient_status"]["evidence_sha256"]
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("patient status is not account-backed", output)

    def test_cpt_receipt_cannot_extend_its_derived_edition_boundary(self):
        receipt = json.loads(self.cpt_receipt.read_text(encoding="utf-8"))
        receipt["valid_through"] = "2099-12-31"
        self.cpt_receipt.write_text(json.dumps(receipt), encoding="utf-8")
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("CPT edition boundary does not match its source", output)

    def test_wrong_cpt_receipt_schema_blocks(self):
        receipt = json.loads(self.cpt_receipt.read_text(encoding="utf-8"))
        receipt["schema"] = 2
        self.cpt_receipt.write_text(json.dumps(receipt), encoding="utf-8")
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("CPT freshness receipt schema is unreadable", output)

    def test_inactive_code_blocks(self):
        value = self.load_manifest()
        value["encounters"][0]["codes"]["hcpcs"] = ["A2046"]
        self.save_manifest(value)
        status, output = self.run_gate()
        self.assertEqual(1, status)
        self.assertIn("HCPCS A2046 is not active on 2026-08-17", output)

    def test_blocked_rerun_removes_an_old_pass_receipt(self):
        self.output.write_text('{"verdict":"PASS"}\n', encoding="utf-8")
        self.cpt_receipt.write_text("not json", encoding="utf-8")
        status, output = self.run_gate()
        self.assertEqual(2, status)
        self.assertIn("coding-freshness: BLOCKED", output)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
