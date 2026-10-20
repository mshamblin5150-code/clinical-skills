"""Public-command coverage of ADR 0427 build 1; synthetic source only."""
# phi-scan: synthetic
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import artifact_lock_test_support
import encounter_openers


COMMAND = Path(__file__).with_name("encounter_openers.py")


class OpenerCommands(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.run = self.root / "run"
        self.source = self.root / "source.txt"
        self.readings = self.root / "readings.json"
        self.map = self.root / "map.md"

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(COMMAND), *map(str, args)], capture_output=True, text=True, encoding="utf-8")

    def record(self, text="Note 1 Example Person\nadult female\n", readings=None, *extra):
        self.source.write_bytes(text.encode())
        self.readings.write_text(json.dumps(readings if readings is not None else [{"note": 1, "name": "Example Person", "age": "adult", "sex": "female"}]), encoding="utf-8")
        return self.invoke("record", "--run", self.run, "--source", self.source, "--readings", self.readings, "--service-date", "2026-01-01", *extra)

    def identity(self, reference="abcdef123456789", *extra):
        return self.invoke("identity", "--run", self.run, "--note", 1, "--reference", reference, "--map", self.map, *extra)

    def test_note_number_line_name_and_complete_source_with_header(self):
        text = "Header\r\nNote 1 Example Person\r\nadult female\r\nNOte 2 Another Example\r\nchild male\r\n"
        readings = [{"note": 1, "name": "Example Person", "age": "adult", "sex": "female"}, {"note": 2, "name": "Another Example", "age": "child", "sex": "male"}]
        result = self.record(text, readings)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("Example Person", result.stdout + result.stderr)
        record = encounter_openers.read_openers(self.run)
        self.assertEqual("Example Person", record["encounters"][0]["name"])
        reconstructed = (self.run / "encounters/unassigned.txt").read_bytes() + b"".join((self.run / item["file"]).read_bytes() for item in record["encounters"])
        self.assertEqual(text.encode(), reconstructed)

    def test_absent_name_broken_numbering_and_dropped_encounter_refuse_without_record(self):
        for text in ("Note 1 Someone Else\n", "Note 2 Example Person\n", "Note 1 Example Person\nNote 2 Second Example\n", "unmarked Example Person\n"):
            with self.subTest(text=text):
                result = self.record(text)
                self.assertEqual(2, result.returncode)
                self.assertFalse((self.run / "openers.json").exists())

    def test_hand_cut_reason_and_no_gaps_or_dropped_tail(self):
        text = "Example Person\nadult female\n"
        item = {"note": 1, "name": "Example Person", "age": "adult", "sex": "female", "start": 0, "end": len(text)}
        self.assertEqual(2, self.record(text, [item], "--mode", "hand").returncode)
        self.assertEqual(2, self.record(text, [{**item, "end": len(text) - 1}], "--mode", "hand", "--reason", "No numbering").returncode)
        self.assertEqual(0, self.record(text, [item], "--mode", "hand", "--reason", "No numbering").returncode)
        self.assertEqual("No numbering", encounter_openers.read_openers(self.run)["reason"])

    def test_single_encounter_and_clinician_name_answer_exemption(self):
        item = {"note": 1, "name": None, "age": "adult", "sex": None}
        self.assertEqual(0, self.record("adult\n", [item], "--mode", "single").returncode)
        self.assertEqual(2, self.identity().returncode)
        answered = self.invoke("answer", "--run", self.run, "--note", 1, "--name", "Example Person", "--reply", "The name is Example Person")
        self.assertEqual(0, answered.returncode, answered.stderr)
        self.assertEqual(0, self.identity().returncode)
        self.assertIn("Example Person", self.map.read_text())

    def test_unanswered_name_routes_to_cannot_be_matched_with_age_and_sex(self):
        item = {"note": 1, "name": None, "age": "adult", "sex": "female"}
        self.assertEqual(0, self.record("adult female\n", [item], "--mode", "single").returncode)
        self.assertEqual(0, self.invoke("answer", "--run", self.run, "--note", 1, "--reply", "I cannot supply a name").returncode)
        self.assertEqual(0, self.identity().returncode)
        text = self.map.read_text()
        self.assertIn("## Cannot be matched", text)
        self.assertIn("| adult | female |", text)

    def test_collision_requires_every_reference_and_preserves_all_prior_bytes(self):
        self.assertEqual(0, self.record().returncode)
        original = b"# Map\r\n\r\n## Existing\r\n| Example Person | 111111111111111 |\r\n| Example Person | 222222222222222 |\r\n\r\n## Newly entered patients\r\n| Name | Patient Reference |\r\n| --- | --- |\r\n\r\n## Tail\r\nkeep exact\r\n"
        self.map.write_bytes(original)
        self.assertEqual(2, self.identity().returncode)
        self.assertEqual(original, self.map.read_bytes())
        collision_file = self.root / "collisions.json"
        collision_file.write_text(json.dumps({"111111111111111": "Different recorded age"}))
        self.assertEqual(2, self.identity("abcdef123456789", "--collisions", collision_file).returncode)
        collision_file.write_text(json.dumps({"111111111111111": "Different recorded age", "222222222222222": "Different recorded sex"}))
        self.assertEqual(0, self.identity("abcdef123456789", "--collisions", collision_file).returncode)
        changed = self.map.read_bytes()
        self.assertIn(b"## Collisions\r\n", changed)
        for line in original.splitlines(keepends=True):
            self.assertIn(line, changed)
        self.assertEqual(2, self.identity().returncode)

    def test_malformed_reference_damaged_record_or_changed_encounter_refuse(self):
        self.assertEqual(0, self.record().returncode)
        for reference in ("short", "g" * 15):
            self.assertEqual(2, self.identity(reference).returncode)
        encounter = self.run / "encounters/encounter-1.txt"
        original = encounter.read_bytes()
        encounter.write_bytes(original + b"changed")
        self.assertEqual(2, self.identity().returncode)
        encounter.write_bytes(original)
        record = self.run / "openers.json"
        record.write_bytes(b"{")
        self.assertEqual(2, self.identity().returncode)
        self.assertEqual(b"{", record.read_bytes())
        self.assertFalse(self.map.exists())

    def test_live_map_lock_and_tracked_destination_refuse(self):
        self.assertEqual(0, self.record().returncode)
        with encounter_openers.artifact_lock.hold(self.map, "test writer"):
            self.assertEqual(2, self.identity().returncode)
        tracked = COMMAND.parent.parent / "never-write-identity.md"
        self.assertEqual(2, self.invoke("identity", "--run", self.run, "--note", 1, "--reference", "abcdef123456789", "--map", tracked).returncode)
        self.assertFalse(tracked.exists())


if __name__ == "__main__":
    unittest.main()
