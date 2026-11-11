"""Synthetic public-command checks for the E/M audit check-off renderer."""
# phi-scan: synthetic
from __future__ import annotations

import artifact_lock_test_support

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import em_audit
import review_manifest
from prose_bind import bind, NAMING
from test_review_manifest import passing_receipt, synthetic_run

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "reference" / "em-audit-checkoff.md"
SKILL = ROOT / "skills" / "em-audit" / "SKILL.md"
CONSTANTS = dict(course="Synthetic course", preceptor="Synthetic preceptor", site="Synthetic site")
PRIVATE = """ICD-10-CM R05.9 Cough
  ANCHOR: "Cough."
  SPECIFICITY: complete - the synthetic encounter documents no further axis
  CONFIDENCE: verified against ICD-10-CM FY2026
CPT 99283 Emergency visit

## Coded, anchor was filled: confirm before submitting

None.

## Not coded, nothing established it

Synthetic refusal line
  NOT CODED: J18.9  Pneumonia, unspecified organism
  needs: imaging establishing pneumonia
  proposed instead: R05.9  Cough
"""
VISIBLE = """ICD-10-CM R05.9 Cough
CPT 99283 Emergency visit
E/M: 99283, low complexity, synthetic support [SOURCE: filled - data: chest radiograph]
"""
NOTE_EM = "E/M: Low complexity, synthetic support; 99283, emergency department service.\n\n"
RECORD = """RE-DERIVATION: note-1
SETTING: emergency department
PROBLEM: definition-acute-uncomplicated - "Cough."
DATA: none documented
RISK: table-low - "Education: Rest."
ANSWER: none
RULE: ADR 0308 ruling 1
MDM: problems low; data minimal; risk low; two of three low
RE-DERIVED LEVEL: {level}
"""


def headings(text: str) -> list[str]:
    return re.findall(r"(?m)^## (.+?)[ \t]*$", text)


class CheckOffCommand(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run = synthetic_run(Path(self.temporary.name))
        (self.run / "worksheets/note-1.md").write_text(PRIVATE, encoding="utf-8")
        (self.run / "visible-worksheet-1.md").write_text(VISIBLE, encoding="utf-8")
        note = self.run / "note-1.md"
        note.write_text(note.read_text(encoding="utf-8").replace(
            "## Medatrax entry fields", NOTE_EM + "## Medatrax entry fields"), encoding="utf-8")
        review_manifest.build(self.run, self.run / "inputs.json", batch=True, constants=CONSTANTS)
        passing_receipt(self.run)
        self.sheet = self.run / em_audit.OUTPUT_DIRECTORY / "note-1.md"

    def invoke(self, *args):
        command = [sys.executable, str(Path(__file__).with_name("em_audit.py")), str(self.run), *map(str, args)]
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")

    def record(self, text: str) -> None:
        folder = self.run / em_audit.OUTPUT_DIRECTORY / em_audit.REDERIVATION_DIRECTORY
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "note-1.md").write_text(text, encoding="utf-8")

    def test_default_prints_counts_only_and_writes_nothing(self):
        result = self.invoke()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for line in ("em-audit: notes in run 1; selected 1",
                     "codes rendered: icd10 1, cpt 0, hcpcs 0, em 1",
                     "codes without an anchor 0",
                     "worksheet blocks: filled-anchor 1, refusal 1, undocumented 0",
                     "E/M filled marks 1",
                     "re-derivations: agree 0; disagree 0; damaged 0; absent 1",
                     "sheets not written (pass --write)",
                     "unread remainder 0"):
            self.assertIn(line, result.stdout)
        for private in ("Cough", "radiograph", "J18.9", "Example Person"):
            self.assertNotIn(private, result.stdout)
        self.assertFalse(self.sheet.exists())

    def test_written_sheet_renders_every_recorded_decision_in_template_order(self):
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("sheets written 1", result.stdout)
        text = self.sheet.read_text(encoding="utf-8")
        self.assertEqual(list(em_audit.SECTIONS), headings(text))
        for expected in ("- [ ] ICD-10-CM R05.9 Cough", "  - Anchor: \"Cough.\"",
                         "  - Source: recorded (no SOURCE line)",
                         "  - Specificity: complete - the synthetic encounter documents no further axis",
                         "NOT CODED: J18.9  Pneumonia, unspecified organism",
                         "- [ ] E/M code: 99283", "- Filled marks: [SOURCE: filled - data: chest radiograph]",
                         "- Setting: emergency department", "- Coding freshness: PASS, checked 2026-10-21",
                         "- MDM sheet: synthetic-mdm.md", NOTE_EM.strip(), "Not performed.",
                         "Clinician signature:", em_audit.NO_ECG_CODE):
            self.assertIn(expected, text)
        self.assertNotIn("office-mdm-check.md", text)

    def test_template_carries_the_renderer_sections_and_no_filled_value(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(list(em_audit.SECTIONS), headings(text))
        self.assertIn("Clinician signature:", text)

    def test_agreement_is_computed_and_a_disagreement_changes_nothing(self):
        self.record(RECORD.format(level="99283"))
        result = self.invoke("--write")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("re-derivations: agree 1; disagree 0; damaged 0; absent 0", result.stdout)
        self.assertIn("agrees with the selected level 99283", self.sheet.read_text(encoding="utf-8"))
        before = {path: path.read_bytes() for path in (self.run / "note-1.md", self.run / "visible-worksheet-1.md",
                                                       self.run / "worksheets/note-1.md")}
        self.record(RECORD.format(level="99284"))
        result = self.invoke("--write")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("disagree 1", result.stdout)
        self.assertIn("DISAGREES: the re-derived level is 99284", self.sheet.read_text(encoding="utf-8"))
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_a_record_without_its_shape_is_unread_rather_than_agreeing(self):
        self.record(RECORD.format(level="99283").replace("MDM: problems low; data minimal; risk low; two of three low\n", ""))
        result = self.invoke()
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("unread remainder 1", result.stdout)
        self.assertIn("agree 0", result.stdout)

    def test_stale_records_refuse_and_write_nothing(self):
        note = self.run / "note-1.md"
        note.write_text(note.read_text(encoding="utf-8").replace("Cough.", "Cough and fever."), encoding="utf-8")
        result = self.invoke("--write")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("refused", result.stdout)
        self.assertFalse(self.sheet.exists())

    def test_note_selection_and_unknown_note(self):
        self.assertIn("selected 1", self.invoke("--note", 1).stdout)
        self.assertEqual(2, self.invoke("--note", 2).returncode)

    def test_declared_limits_are_named_by_the_skill_and_not_copied(self):
        self.assertEqual((), bind(em_audit.DECLARED_LIMITS, SKILL.read_text(encoding="utf-8"), mode=NAMING))


if __name__ == "__main__":
    unittest.main()
