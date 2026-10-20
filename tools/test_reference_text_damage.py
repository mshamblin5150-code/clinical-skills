"""ADR 0423: raw reference text and the threshold command refuse damage."""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import threshold_grammar
import threshold_sheet as gate
from run_record_reader import outbound_text_damage
import test_threshold_sheet as support

ROOT = Path(__file__).resolve().parents[1]


def decoded_damage(value: object) -> list[str]:
    """Inspect JSON keys and strings as well as its on-disk escape spelling."""
    if isinstance(value, str):
        return [f"line {line}: U+{ord(char):04X}" for line, char in outbound_text_damage(value)]
    if isinstance(value, dict):
        return [finding for key, item in value.items()
                for part in (key, item) for finding in decoded_damage(part)]
    if isinstance(value, list):
        return [finding for item in value for finding in decoded_damage(item)]
    return []


def reference_damage(root: Path) -> list[str]:
    """A clean result covers tracked text only; untracked files are not read.

    Binary files (those not decodable as UTF-8) are outside this text check.
    Tabs are allowed only in TSV, where they separate columns.
    """
    paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "reference/", "skills/", "AGENTS.md"], cwd=root
    ).decode("utf-8").split("\0")
    findings = []
    for name in filter(None, paths):
        path = root / name
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            continue
        findings.extend(f"{name}: line {line}: U+{ord(char):04X}"
                        for line, char in outbound_text_damage(text, allow_tab=path.suffix == ".tsv"))
        if path.suffix == ".json":
            findings.extend(f"{name}: decoded {item}" for item in decoded_damage(json.loads(text)))
    return findings


class ReferenceText(unittest.TestCase):
    def test_tracked_references_and_skills_are_clean(self):
        self.assertEqual(reference_damage(ROOT), [])

    def test_tracked_scan_is_live_and_names_its_untracked_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "reference").mkdir()
            paths = {"reference/plain.md": "x\x07y", "reference/data.tsv": "a\tb\r\n",
                     "reference/data.json": '{"\\u007f": ["\\u0085"]}',
                     "reference/untracked.md": "\x00"}
            for name, text in paths.items():
                (root / name).write_bytes(text.encode())
            subprocess.run(["git", "add", "reference/plain.md", "reference/data.tsv",
                            "reference/data.json"], cwd=root, check=True)
            findings = reference_damage(root)
            self.assertEqual(len(findings), 3, findings)
            self.assertTrue(any("U+0007" in item for item in findings))
            self.assertTrue(any("U+007F" in item for item in findings))
            self.assertTrue(any("U+0085" in item for item in findings))


class ThresholdDamage(unittest.TestCase):
    CLEAN = support.TheExitStatusSaysWhichKindOfNotGraded.CLEAN

    def test_every_damaged_line_survives_the_cli_read_and_other_sheets_are_graded(self):
        characters = "\t\x07\0\f\v\r\x7f\x85\x1e\x1f"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            damaged = root / "damaged.md"
            damaged.write_bytes("".join(f"x{char}y\n" for char in characters).encode())
            (root / "clean.md").write_bytes(self.CLEAN.replace("\n", "\r\n").encode())
            out, err = io.StringIO(), io.StringIO()
            facts = gate.CatalogFacts((), {"Society/doc": 60}, {}, (), ())
            with mock.patch.object(gate, "SHEET_ROOT", root), mock.patch.object(gate, "load_catalog_facts", return_value=facts), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = gate.main(["--all", "--pdf-root", str(root / "pdf"),
                                    "--recs-root", str(root / "recs"), "--text-root", str(root / "text")])
            self.assertEqual(status, 1, err.getvalue())
            for line, char in enumerate(characters, 1):
                self.assertIn(f"line {line}: U+{ord(char):04X}", err.getvalue())
            self.assertIn("not graded — damaged text", err.getvalue())
            self.assertIn("== clean.md", out.getvalue())
            clean = gate.survey(root / "clean.md", support.survey_inputs(page_counts={"Society/doc": 60}))
            self.assertEqual(clean.status, 0, gate.format_report(clean))
            self.assertTrue(clean.results)

    def test_every_character_and_every_sheet_location_is_checked(self):
        for code in (*range(32), *range(127, 160)):
            if code == 10:
                continue
            for position in (0, len(self.CLEAN) // 2, len(self.CLEAN)):
                with self.subTest(code=code, position=position):
                    parsed = threshold_grammar.parse(
                        self.CLEAN[:position] + chr(code) + self.CLEAN[position:], Path("sheet.md"))
                    self.assertFalse(parsed.ok)
                    self.assertIn(f"U+{code:04X}", parsed.why_not)

    def test_operator_and_general_remedies_remain_distinct(self):
        for char in ("\x1e", "\x1f", "\x07"):
            parsed = threshold_grammar.parse(f"x{char}y", Path("sheet.md"))
            self.assertIn("render the cited PDF page", parsed.why_not)
            self.assertIn("<= or >=", parsed.why_not)
            self.assertEqual("mis-encoded comparison operator" in parsed.why_not, char != "\x07")

    def test_the_pre_repair_sepsis_sheet_is_a_damage_control(self):
        historical = subprocess.check_output(
            ["git", "show", "981f63f73146f5e072f485a716a8f8c32804c7d1:reference/thresholds/sepsis-and-septic-shock.md"], cwd=ROOT
        ).decode("utf-8")
        self.assertIn("\x07", historical)
        parsed = threshold_grammar.parse(historical, Path("sepsis.md"))
        self.assertFalse(parsed.ok)
        self.assertTrue(parsed.text_damage)
