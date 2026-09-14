"""Tests for the licensed CPT/HCPCS procedure-code build and lookup seams."""

from __future__ import annotations

import csv
import io
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

import procedure_codes_build as build
import procedure_codes_lookup as lookup


def hcpcs_line(
    code: str,
    description: str,
    short: str,
    *,
    kind: str = "code",
    effective: str = "20260101",
    termination: str = "",
    action: str = "N",
) -> str:
    row = [" "] * 293
    if kind == "code":
        row[0:5] = code
        row[10] = "3"
    else:
        row[3:5] = code
        row[10] = "7"
    row[11:91] = f"{description:<80}"[:80]
    row[91:119] = f"{short:<28}"[:28]
    row[268:276] = "20250101"
    row[276:284] = effective
    row[284:292] = f"{termination:<8}"[:8]
    row[292] = action
    return "".join(row)


class HcpcsParser(unittest.TestCase):
    def test_reads_code_descriptors_and_dates(self):
        entry = build.parse_hcpcs_line(
            hcpcs_line("J1100", "Injection, example drug", "Example injection")
        )
        self.assertEqual(entry.code, "J1100")
        self.assertEqual(entry.description, "Injection, example drug")
        self.assertEqual(entry.effective_date, "2026-01-01")

    def test_distinguishes_two_character_modifiers(self):
        entry = build.parse_hcpcs_line(
            hcpcs_line("GA", "Example modifier", "Example modifier", kind="modifier")
        )
        self.assertEqual((entry.code, entry.kind), ("GA", "modifier"))

    def test_single_line_parser_refuses_continuations_instead_of_truncating(self):
        line = list(hcpcs_line("J1100", "Example", "Example"))
        line[10] = "4"
        with self.assertRaisesRegex(ValueError, "stateful"):
            build.parse_hcpcs_line("".join(line))

    def test_file_parser_joins_continuation_text(self):
        directory = Path(tempfile.mkdtemp())
        path = directory / "hcpcs.zip"
        continuation = "J1100002004continued description"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(
                "HCPC2026_OCT_ANWEB.txt",
                hcpcs_line("J1100", "First fragment", "Example") + "\n" + continuation,
            )
        self.assertEqual(
            build.read_hcpcs(path)[0].description,
            "First fragment continued description",
        )

    def test_file_parser_refuses_a_mismatched_continuation(self):
        directory = Path(tempfile.mkdtemp())
        path = directory / "hcpcs.zip"
        continuation = "J1101002004wrong code"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(
                "HCPC2026_OCT_ANWEB.txt",
                hcpcs_line("J1100", "First fragment", "Example") + "\n" + continuation,
            )
        with self.assertRaisesRegex(ValueError, "does not follow"):
            build.read_hcpcs(path)


class CptParser(unittest.TestCase):
    def test_reads_the_normalized_licensed_csv(self):
        directory = Path(tempfile.mkdtemp())
        path = directory / "cpt.csv"
        path.write_text(
            "code,description,short_description,effective_date,category,locator\n"
            "12345,Synthetic procedure,Synthetic,2026-01-01,Category I,page 10\n",
            encoding="utf-8",
        )
        entry = build.read_cpt(path)[0]
        self.assertEqual((entry.system, entry.code), ("CPT", "12345"))
        self.assertEqual(entry.locator, "page 10")

    def test_rejects_a_non_five_digit_code(self):
        directory = Path(tempfile.mkdtemp())
        path = directory / "cpt.csv"
        path.write_text("code,description\n1234,Synthetic\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid CPT"):
            build.read_cpt(path)


def database() -> Path:
    directory = Path(tempfile.mkdtemp())
    source = directory / "hcpcs.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr(
            "HCPC2026_OCT_ANWEB.txt",
            "\n".join(
                [
                    hcpcs_line("J1100", "Injection, example drug", "Example injection"),
                    hcpcs_line(
                        "Q9999",
                        "Future example",
                        "Future example",
                        effective="20261001",
                        action="A",
                    ),
                    hcpcs_line("GA", "Example modifier", "Example modifier", kind="modifier"),
                ]
            ),
        )
    cpt = directory / "cpt.csv"
    with cpt.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["code", "description"])
        writer.writeheader()
        writer.writerow({"code": "12345", "description": "Synthetic CPT procedure"})
        writer.writerow({"code": "0001F", "description": "Synthetic Category II procedure"})
        writer.writerow({"code": "0001T", "description": "Synthetic Category III procedure"})
        writer.writerow({"code": "0001U", "description": "Synthetic PLA procedure"})
    output = directory / "codes.sqlite"
    entries = build.read_hcpcs(source) + build.read_cpt(cpt)
    build.write_database(output, entries, source, "2026-10-01", cpt)
    return output


class Lookup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = database()

    def setUp(self):
        self.connection = lookup.open_database(self.path)

    def tearDown(self):
        self.connection.close()

    def test_infers_cpt_from_five_digits(self):
        self.assertEqual(lookup.describe(self.connection, "12345").system, "CPT")

    def test_infers_all_alphanumeric_cpt_categories(self):
        for code in ("0001F", "0001T", "0001U"):
            with self.subTest(code=code):
                self.assertEqual(lookup.describe(self.connection, code).system, "CPT")

    def test_database_does_not_claim_a_partial_cpt_import_is_complete(self):
        self.assertFalse(lookup.complete(self.connection, "CPT"))
        self.assertTrue(lookup.complete(self.connection, "HCPCS"))

    def test_infers_hcpcs_from_the_alphanumeric_shape(self):
        self.assertEqual(lookup.describe(self.connection, "j1100").system, "HCPCS")

    def test_modifiers_do_not_collide_with_codes(self):
        self.assertIsNone(lookup.describe(self.connection, "GA"))
        self.assertEqual(lookup.describe(self.connection, "GA", "modifier").kind, "modifier")

    def test_validity_is_service_date_aware(self):
        future = lookup.describe(self.connection, "Q9999")
        self.assertFalse(lookup.valid_on(future, "2026-09-14"))
        self.assertTrue(lookup.valid_on(future, "2026-10-01"))

    def test_finds_by_descriptor(self):
        self.assertEqual([m.code for m in lookup.find(self.connection, "injection", None)], ["J1100"])

    def test_records_both_book_authorities(self):
        rows = self.connection.execute("SELECT system, isbn FROM source ORDER BY system").fetchall()
        self.assertEqual(rows, [("CPT", "9781640163232"), ("HCPCS", "9781640163317")])


if __name__ == "__main__":
    unittest.main()
