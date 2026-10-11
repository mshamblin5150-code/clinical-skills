"""Tests for the licensed CPT/HCPCS procedure-code build and lookup seams."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
import tempfile
import unittest
import zipfile
from contextlib import closing, redirect_stdout
from pathlib import Path
from unittest import mock

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
    def test_reads_maaa_administrative_codes_from_the_normalized_csv(self):
        entry = build.read_cpt_text(
            "code,description,category\n0002M,Synthetic algorithmic assay,MAAA\n",
            "synthetic.csv",
        )[0]
        self.assertEqual((entry.system, entry.code, entry.category), ("CPT", "0002M", "MAAA"))

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

    def test_rejects_all_three_broken_descriptor_shapes_with_codes(self):
        cases = (
            ("12345,Stem; First\n12346,Stem; First; Second\n", "12346"),
            ("12345,Stem;; Child\n", "12345"),
            ("12345,Elements:\n", "12345"),
        )
        for rows, code in cases:
            with self.subTest(code=code, rows=rows):
                with self.assertRaisesRegex(ValueError, code):
                    build.read_cpt_text("code,description\n" + rows, "synthetic.csv")

    def test_a_clean_import_builds_and_says_it_is_unverified(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            hcpcs = base / "hcpcs.zip"
            with zipfile.ZipFile(hcpcs, "w") as archive:
                archive.writestr("HCPC2026_OCT_ANWEB.txt", hcpcs_line("J1100", "Example", "Example"))
            cpt = base / "cpt.csv"
            cpt.write_text("code,description\n12345,Stem; First\n12346,Stem; Second\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                status = build.main(["--hcpcs", str(hcpcs), "--hcpcs-effective", "2026-10-01", "--cpt", str(cpt), "--out", str(base / "out.sqlite")])
            self.assertEqual(0, status)
            self.assertIn("CPT descriptors  unverified (no agreement record supplied)", stdout.getvalue())

    def test_bulleted_descriptor_is_valid(self):
        entries = build.read_cpt_text(
            'code,description\n12345,"Elements: • One • Two"\n', "synthetic.csv"
        )
        self.assertEqual("Elements: • One • Two", entries[0].description)

    def test_named_2026_controls_refuse_known_defects(self):
        correct = {
            "87804": "Example test; influenza",
            "86486": "Example skin test; unlisted antigen",
            "97169": "Example evaluation: • First • Second • Third",
            "45825": "Example closure; with colostomy",
        }
        hashes = {code: hashlib.sha256(text.encode("utf-8")).hexdigest() for code, text in correct.items()}
        wrong = {
            "87804": correct["87804"].replace("; influenza", "; group B strep; influenza"),
            "86486": "Example hematology test; unlisted antigen",
            "97169": correct["97169"].replace("Second", "Different"),
            "45825": "Example closure;; with colostomy",
        }
        with mock.patch.object(build, "CPT_CONTROL_SHA256", hashes):
            build.verify_cpt_controls(correct)
            for code, description in wrong.items():
                with self.subTest(code=code):
                    candidates = correct | {code: description}
                    with self.assertRaisesRegex(ValueError, code):
                        build.verify_cpt_controls(candidates)

    def test_agreement_requires_both_complete_readings_and_page_resolutions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()  # the record resolves; a runner temp path may be 8.3
            first = root / "reader-1.csv"
            second = root / "reader-2.csv"
            agreed = root / "agreed.csv"
            first.write_text("code,description\n12345,First reading\n", encoding="utf-8")
            second.write_text("code,description\n12345,Second reading\n", encoding="utf-8")
            agreed.write_text("code,description\n12345,Resolved reading\n", encoding="utf-8")
            record = {
                "reader_1": {"file": first.name, "sha256": build._sha256(first), "codes_read": 1, "method": "page_structure"},
                "reader_2": {"file": second.name, "sha256": build._sha256(second), "codes_read": 1, "method": "rendered_screenshots"},
                "agreed": {"file": agreed.name, "sha256": build._sha256(agreed)},
                "disagreement_count": 1,
                "resolutions": [{"code": "12345", "description": "Resolved reading", "printed_page": "42"}],
                "unread_remainder": [],
            }
            record_path = root / "agreement.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            self.assertEqual(
                build.CptEvidence(first, second, agreed, record_path),
                build.verify_cpt_agreement(root, agreed, record_path),
            )
            record["disagreement_count"] = 2
            record_path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "counts 2 disagreements; the readers disagree on 1"):
                build.verify_cpt_agreement(root, agreed, record_path)
            record["disagreement_count"] = 1
            del record["unread_remainder"]
            record_path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing field 'unread_remainder'"):
                build.verify_cpt_agreement(root, agreed, record_path)
            record["unread_remainder"] = []
            record["resolutions"] = []
            record_path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "12345"):
                build.verify_cpt_agreement(root, agreed, record_path)

    def test_agreement_refuses_changed_or_missing_recorded_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            agreed = root / "agreed.csv"
            agreed.write_text("code,description\n12345,Procedure\n", encoding="utf-8")
            record = {
                "reader_1": {"file": "missing.csv", "sha256": "0" * 64, "codes_read": 1, "method": "page_structure"},
                "reader_2": {"file": "other.csv", "sha256": "0" * 64, "codes_read": 1, "method": "rendered_screenshots"},
                "agreed": {"file": "agreed.csv", "sha256": build._sha256(agreed)},
                "disagreement_count": 0,
                "resolutions": [],
                "unread_remainder": [],
            }
            record_path = root / "agreement.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing.csv"):
                build.verify_cpt_agreement(root, agreed, record_path)
            (root / "missing.csv").write_text("code,description\n12345,Changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "digest disagrees: missing.csv"):
                build.verify_cpt_agreement(root, agreed, record_path)

    def test_build_marks_only_matching_agreement_verified_and_records_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "scratch" / "cpt-2026"
            root.mkdir(parents=True)
            hcpcs = base / "hcpcs.zip"
            with zipfile.ZipFile(hcpcs, "w") as archive:
                archive.writestr("HCPC2026_OCT_ANWEB.txt", hcpcs_line("J1100", "Example", "Example"))
            cpt_rows = {
                "12345": "Synthetic procedure",
                "87804": "Example test; influenza",
                "86486": "Example skin test; unlisted antigen",
                "97169": "Example evaluation: • First • Second • Third",
                "45825": "Example closure; with colostomy",
            }
            control_hashes = {
                code: hashlib.sha256(description.encode("utf-8")).hexdigest()
                for code, description in cpt_rows.items() if code != "12345"
            }
            buffer = io.StringIO(newline="")
            writer = csv.writer(buffer)
            writer.writerow(("code", "description"))
            writer.writerows(cpt_rows.items())
            for name in ("reader-1.csv", "reader-2.csv", "agreed.csv"):
                (root / name).write_text(buffer.getvalue(), encoding="utf-8")
            record = {
                "reader_1": {"file": "reader-1.csv", "sha256": build._sha256(root / "reader-1.csv"), "codes_read": len(cpt_rows), "method": "page_structure"},
                "reader_2": {"file": "reader-2.csv", "sha256": build._sha256(root / "reader-2.csv"), "codes_read": len(cpt_rows), "method": "rendered_screenshots"},
                "agreed": {"file": "agreed.csv", "sha256": build._sha256(root / "agreed.csv")},
                "disagreement_count": 0, "resolutions": [], "unread_remainder": [],
            }
            agreement = root / "agreement.json"
            agreement.write_text(json.dumps(record), encoding="utf-8")
            output = base / "codes.sqlite"
            args = ["--hcpcs", str(hcpcs), "--hcpcs-effective", "2026-10-01", "--cpt", str(root / "agreed.csv"), "--cpt-agreement", str(agreement), "--cpt-agreement-sha256", build._sha256(agreement), "--out", str(output)]
            def run(extra: list[str]) -> str:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    self.assertEqual(0, build.main(args + extra))
                return stdout.getvalue()

            with mock.patch.object(build, "scratch_root", return_value=base / "scratch"):
                self.assertIn("CPT descriptors  unverified (--cpt-complete not asserted)", run([]))
                with closing(sqlite3.connect(output)) as connection:
                    self.assertEqual("unverified", connection.execute("SELECT value FROM meta WHERE key='cpt_descriptors'").fetchone()[0])
                    self.assertEqual(build._sha256(root / "agreed.csv"), connection.execute("SELECT sha256 FROM source WHERE id='ama-cpt-2026-licensed'").fetchone()[0])
                baseline = base / "baseline.sqlite"
                with closing(sqlite3.connect(baseline)) as connection:
                    connection.execute("CREATE TABLE code (system TEXT, code TEXT)")
                    connection.executemany("INSERT INTO code VALUES ('CPT', ?)", ((code,) for code in cpt_rows))
                    connection.commit()
                with mock.patch.object(build, "DEFAULT_OUT", baseline), mock.patch.object(build, "CPT_CONTROL_SHA256", control_hashes):
                    self.assertIn("CPT descriptors  verified", run(["--cpt-complete"]))
                with closing(sqlite3.connect(output)) as connection:
                    self.assertEqual("verified", connection.execute("SELECT value FROM meta WHERE key='cpt_descriptors'").fetchone()[0])
                    self.assertEqual(5, connection.execute("SELECT COUNT(*) FROM source").fetchone()[0])
                    self.assertEqual(
                        [("ama-cpt-2026-licensed",)],
                        connection.execute("SELECT id FROM source WHERE system = 'CPT'").fetchall(),
                    )
                    self.assertEqual(
                        set(build.CPT_EVIDENCE_SOURCE_IDS.values()),
                        {row[0] for row in connection.execute("SELECT id FROM source WHERE system = ?", (build.CPT_EVIDENCE_SYSTEM,))},
                    )
                with closing(sqlite3.connect(baseline)) as connection:
                    connection.execute("INSERT INTO code VALUES ('CPT', '12346')")
                    connection.commit()
                with mock.patch.object(build, "DEFAULT_OUT", baseline), mock.patch.object(build, "CPT_CONTROL_SHA256", control_hashes):
                    with self.assertRaisesRegex(SystemExit, "12346"):
                        build.main(args + ["--cpt-complete"])
                args[args.index(build._sha256(agreement))] = "0" * 64
                self.assertIn("agreement record digest disagrees", run(["--cpt-complete"]))
                with closing(sqlite3.connect(output)) as connection:
                    self.assertEqual("unverified", connection.execute("SELECT value FROM meta WHERE key='cpt_descriptors'").fetchone()[0])
                (root / "reader-2.csv").unlink()
                for extra in ([], ["--cpt-complete"]):
                    with self.subTest(extra=extra), self.assertRaisesRegex(SystemExit, "reader-2.csv"):
                        build.main(args + extra)


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
        writer.writerow({"code": "0002M", "description": "Synthetic MAAA administrative assay"})
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
        for code in ("0001F", "0002M", "0001T", "0001U"):
            with self.subTest(code=code):
                self.assertEqual(lookup.describe(self.connection, code).system, "CPT")

    def test_database_does_not_claim_a_partial_cpt_import_is_complete(self):
        self.assertFalse(lookup.complete(self.connection, "CPT"))
        self.assertTrue(lookup.complete(self.connection, "HCPCS"))
        self.assertFalse(lookup.cpt_descriptors_verified(self.connection))

    def test_unverified_cpt_hit_warns_without_warning_on_hcpcs(self):
        output = io.StringIO()
        with redirect_stdout(output):
            status = lookup.main([
                "12345", "J1100", "--database", str(self.path), "--on", "2026-10-01"
            ])
        self.assertEqual(0, status)
        self.assertEqual(1, output.getvalue().count("CPT DESCRIPTORS UNVERIFIED"))
        self.assertIn("rendered VitalSource page", output.getvalue())

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

    def test_unagreed_import_is_marked_unverified(self):
        value = self.connection.execute("SELECT value FROM meta WHERE key='cpt_descriptors'").fetchone()
        self.assertEqual(("unverified",), value)


if __name__ == "__main__":
    unittest.main()
