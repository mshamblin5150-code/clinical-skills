"""Public-command tests for the two-reader CPT descriptor agreement (#1348, ADR 0269).

Every descriptor here is synthetic; no licensed CPT text is committed.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sqlite3
import tempfile
import unittest
import zipfile
from contextlib import closing, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import cpt_descriptor_agreement as agreement
import procedure_codes_build as build
from run_grader import format_unread_remainder


def write_reading(path: Path, rows: dict[str, str], *, locators: bool = False) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(("code", "description", "locator") if locators else ("code", "description"))
    for code, description in rows.items():
        writer.writerow((code, description, f"page {code}") if locators else (code, description))
    path.write_text(buffer.getvalue(), encoding="utf-8")


def write_resolutions(path: Path, rows: list[tuple[str, str, str]]) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(("code", "description", "printed_page"))
    writer.writerows(rows)
    path.write_text(buffer.getvalue(), encoding="utf-8")


READING = {
    "12345": "Stem procedure; first",
    "12346": "Stem procedure; second",
    "0001T": "Emerging technology service",
}


class Run(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()).resolve() / "cpt-2026"
        self.root.mkdir()

    def run_command(self, *extra: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = agreement.main(["--root", str(self.root), *extra])
        return status, stdout.getvalue(), stderr.getvalue()


class AgreeingReaders(Run):
    def test_maaa_category_survives_agreement_without_reader_metadata(self):
        reading = {"0002M": "Synthetic algorithmic assay"}
        write_reading(self.root / "reader-1.csv", reading, locators=True)
        write_reading(self.root / "reader-2.csv", reading)
        status, out, err = self.run_command("--write")
        self.assertEqual(0, status, out + err)
        entry = build.read_cpt(self.root / "agreed.csv")[0]
        self.assertEqual("MAAA", entry.category)

    def test_agreeing_readers_write_a_record_the_build_verifies(self):
        write_reading(self.root / "reader-1.csv", READING, locators=True)
        write_reading(self.root / "reader-2.csv", READING)
        status, out, err = self.run_command("--write")
        self.assertEqual(0, status, out + err)
        self.assertIn(format_unread_remainder(0), out)
        record = json.loads((self.root / "agreement.json").read_text(encoding="utf-8"))
        self.assertEqual(3, record["reader_1"]["codes_read"])
        self.assertEqual("page_structure", record["reader_1"]["method"])
        self.assertEqual("rendered_screenshots", record["reader_2"]["method"])
        self.assertEqual(0, record["disagreement_count"])
        self.assertEqual([], record["unread_remainder"])
        digest = hashlib.sha256((self.root / "agreement.json").read_bytes()).hexdigest()
        self.assertIn(f"agreement sha256 {digest}", out)
        evidence = build.verify_cpt_agreement(self.root, self.root / "agreed.csv", self.root / "agreement.json")
        self.assertEqual(self.root / "agreed.csv", evidence.agreed)
        rows = {entry.code: entry for entry in build.read_cpt(self.root / "agreed.csv")}
        self.assertEqual("page 12345", rows["12345"].locator)
        self.assertEqual("III", rows["0001T"].category)
        self.assertEqual("I", rows["12345"].category)

    def test_the_report_prints_counts_and_never_a_descriptor(self):
        write_reading(self.root / "reader-1.csv", READING)
        write_reading(self.root / "reader-2.csv", READING | {"12346": "Stem procedure; secnd"})
        status, out, err = self.run_command()
        self.assertEqual(2, status)
        for description in (*READING.values(), "secnd"):
            self.assertNotIn(description, out + err)

    def test_categories_follow_the_code_shape(self):
        self.assertEqual(
            ["I", "II", "III", "PLA"],
            [agreement.category("99213"), agreement.category("1036F"), agreement.category("0042T"), agreement.category("0001U")],
        )


class Disagreements(Run):
    def setUp(self):
        super().setUp()
        write_reading(self.root / "reader-1.csv", READING)
        write_reading(self.root / "reader-2.csv", READING | {"12346": "Stem procedure; secnd"})

    def test_an_unsettled_disagreement_is_an_unread_remainder_and_writes_no_record(self):
        status, out, _ = self.run_command("--write")
        self.assertEqual(2, status)
        self.assertIn(format_unread_remainder(1), out)
        self.assertFalse((self.root / "agreement.json").exists())
        self.assertFalse((self.root / "agreed.csv").exists())
        with (self.root / "disagreements.csv").open(encoding="utf-8", newline="") as stream:
            work = list(csv.DictReader(stream))
        self.assertEqual([("12346", "Stem procedure; second", "Stem procedure; secnd")], [
            (row["code"], row["reader_1"], row["reader_2"]) for row in work
        ])

    def test_a_page_resolution_settles_it_and_the_agreed_text_is_the_page(self):
        write_resolutions(self.root / "resolutions.csv", [("12346", "Stem procedure; second", "42")])
        status, out, err = self.run_command("--write")
        self.assertEqual(0, status, out + err)
        record = json.loads((self.root / "agreement.json").read_text(encoding="utf-8"))
        self.assertEqual(1, record["disagreement_count"])
        self.assertEqual([{"code": "12346", "description": "Stem procedure; second", "printed_page": "42"}], record["resolutions"])
        build.verify_cpt_agreement(self.root, self.root / "agreed.csv", self.root / "agreement.json")

    def test_a_resolution_without_a_printed_page_is_a_finding(self):
        write_resolutions(self.root / "resolutions.csv", [("12346", "Stem procedure; second", "")])
        status, out, _ = self.run_command("--write")
        self.assertEqual(1, status)
        self.assertIn("resolution without a printed page", out)
        self.assertFalse((self.root / "agreement.json").exists())

    def test_a_resolution_for_an_agreeing_code_is_a_finding(self):
        write_resolutions(
            self.root / "resolutions.csv",
            [("12346", "Stem procedure; second", "42"), ("12345", "Stem procedure; first", "41")],
        )
        status, out, _ = self.run_command("--write")
        self.assertEqual(1, status)
        self.assertIn("resolution for a code the readers agree on", out)


class Populations(Run):
    def test_a_code_only_one_reader_read_is_unread(self):
        write_reading(self.root / "reader-1.csv", READING)
        write_reading(self.root / "reader-2.csv", {k: v for k, v in READING.items() if k != "0001T"})
        status, out, _ = self.run_command("--write")
        self.assertEqual(2, status)
        self.assertRegex(out, re.compile(r"^  only reader 1 +1$", re.M))
        self.assertIn(format_unread_remainder(1), out)

    def test_a_missing_reading_does_not_scan(self):
        write_reading(self.root / "reader-1.csv", READING)
        status, _, err = self.run_command()
        self.assertEqual(2, status)
        self.assertIn("reader-2.csv", err)

    def test_a_duplicate_code_in_a_reading_does_not_scan(self):
        (self.root / "reader-1.csv").write_text("code,description\n12345,A\n12345,B\n", encoding="utf-8")
        write_reading(self.root / "reader-2.csv", {"12345": "A"})
        status, _, err = self.run_command()
        self.assertEqual(2, status)
        self.assertIn("duplicate", err)


class DefectShapes(Run):
    def test_an_agreed_stacked_descriptor_is_a_finding_and_writes_nothing(self):
        stacked = {"12345": "Stem; first", "12346": "Stem; first; second"}
        write_reading(self.root / "reader-1.csv", stacked)
        write_reading(self.root / "reader-2.csv", stacked)
        status, out, _ = self.run_command("--write")
        self.assertEqual(1, status)
        self.assertRegex(out, re.compile(r"^  agreed descriptors stacked +1$", re.M))
        self.assertFalse((self.root / "agreement.json").exists())

    def test_the_report_counts_each_shape_even_when_clean(self):
        write_reading(self.root / "reader-1.csv", READING)
        write_reading(self.root / "reader-2.csv", READING)
        _, out, _ = self.run_command()
        for shape in build.DESCRIPTOR_DEFECTS:
            self.assertRegex(out, re.compile(rf"^  agreed descriptors {shape} +0$", re.M))

    def test_a_wrong_control_is_a_finding(self):
        rows = {"87804": "Example test; group B; influenza", "12345": "Other"}
        write_reading(self.root / "reader-1.csv", rows)
        write_reading(self.root / "reader-2.csv", rows)
        status, out, _ = self.run_command("--write")
        self.assertEqual(1, status)
        self.assertRegex(out, re.compile(r"^  control disagrees with its digest +1$", re.M))
        self.assertFalse((self.root / "agreement.json").exists())


class ReviewFindings(Run):
    def test_a_line_break_inside_a_resolution_reaches_a_record_the_build_accepts(self):
        write_reading(self.root / "reader-1.csv", {"12345": "A"})
        write_reading(self.root / "reader-2.csv", {"12345": "B"})
        (self.root / "resolutions.csv").write_bytes(
            b'code,description,printed_page\r\n12345,"Lead-in\r\n\xe2\x80\xa2 one",p1\r\n'
        )
        status, out, err = self.run_command("--write")
        self.assertEqual(0, status, out + err)
        build.verify_cpt_agreement(self.root, self.root / "agreed.csv", self.root / "agreement.json")

    def test_two_empty_readings_do_not_scan(self):
        write_reading(self.root / "reader-1.csv", {})
        write_reading(self.root / "reader-2.csv", {})
        status, _, err = self.run_command("--write")
        self.assertEqual(2, status)
        self.assertIn("no code was read by both readers", err)
        self.assertFalse((self.root / "agreement.json").exists())

    def test_a_finding_wins_over_the_unread_remainder(self):
        write_reading(self.root / "reader-1.csv", READING)
        write_reading(self.root / "reader-2.csv", {"12345": READING["12345"], "12346": "Stem procedure; secnd"})
        write_resolutions(self.root / "resolutions.csv", [("12345", READING["12345"], "41")])
        status, out, _ = self.run_command()
        self.assertEqual(1, status)
        self.assertIn(format_unread_remainder(2), out)

    def test_a_refused_write_removes_an_earlier_record(self):
        write_reading(self.root / "reader-1.csv", READING)
        write_reading(self.root / "reader-2.csv", READING)
        self.assertEqual(0, self.run_command("--write")[0])
        write_reading(self.root / "reader-2.csv", READING | {"12346": "Stem procedure; secnd"})
        self.assertEqual(2, self.run_command("--write")[0])
        self.assertFalse((self.root / "agreement.json").exists())
        self.assertFalse((self.root / "agreed.csv").exists())

    def test_a_root_inside_a_checkout_outside_scratch_does_not_scan(self):
        status, _, err = self.run_command_at(Path(agreement.__file__).resolve().parent)
        self.assertEqual(2, status)
        self.assertIn("DID NOT SCAN", err)

    def run_command_at(self, root: Path) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = agreement.main(["--root", str(root)])
        return status, stdout.getvalue(), stderr.getvalue()


class TheBuildConsumesTheRecord(Run):
    def test_a_written_record_builds_verified_end_to_end(self):
        rows = {
            "12345": "Synthetic procedure",
            "87804": "Example test; influenza",
            "86486": "Example skin test; unlisted antigen",
            "97169": "Example evaluation • First • Second",
            "45825": "Example closure; with colostomy",
        }
        write_reading(self.root / "reader-1.csv", rows)
        write_reading(self.root / "reader-2.csv", rows)
        controls = {code: hashlib.sha256(text.encode("utf-8")).hexdigest() for code, text in rows.items() if code != "12345"}
        with mock.patch.object(build, "CPT_CONTROL_SHA256", controls):
            status, out, err = self.run_command("--write")
        self.assertEqual(0, status, out + err)
        digest = hashlib.sha256((self.root / "agreement.json").read_bytes()).hexdigest()
        base = self.root.parent / f"{self.root.name}-build"
        base.mkdir()
        hcpcs = base / "hcpcs.zip"
        with zipfile.ZipFile(hcpcs, "w") as archive:
            archive.writestr("HCPC2026_OCT_ANWEB.txt", "")
        shipped = base / "shipped.sqlite"
        with closing(sqlite3.connect(shipped)) as connection:
            connection.execute("CREATE TABLE code (system TEXT, code TEXT)")
            connection.executemany("INSERT INTO code VALUES ('CPT', ?)", ((code,) for code in rows))
            connection.commit()
        output = base / "out.sqlite"
        args = [
            "--hcpcs", str(hcpcs), "--hcpcs-effective", "2026-10-01",
            "--cpt", str(self.root / "agreed.csv"), "--cpt-complete",
            "--cpt-agreement", str(self.root / "agreement.json"), "--cpt-agreement-sha256", digest,
            "--out", str(output),
        ]
        with (
            mock.patch.object(build, "scratch_root", return_value=self.root.parent),
            mock.patch.object(build, "DEFAULT_OUT", shipped),
            mock.patch.object(build, "CPT_CONTROL_SHA256", controls),
            mock.patch.object(build, "read_hcpcs", return_value=[]),
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(0, build.main(args))
        with closing(sqlite3.connect(output)) as connection:
            self.assertEqual(
                ("verified",), connection.execute("SELECT value FROM meta WHERE key='cpt_descriptors'").fetchone()
            )


class Limits(unittest.TestCase):
    def test_the_module_declares_its_limits(self):
        self.assertTrue(agreement.DECLARED_LIMITS)
        for name, text in agreement.DECLARED_LIMITS:
            self.assertTrue(name and text)


if __name__ == "__main__":
    unittest.main()
