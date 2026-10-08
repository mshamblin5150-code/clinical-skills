"""Behavioral checks for placement, bounded repairs, and retained evidence."""

# phi-scan: synthetic

import json
import tempfile
import unittest
from pathlib import Path

import artifact_repairs as repairs

NOTE = """S
History.
O
Exam.
A
Differential diagnoses:
1. Cough - R05.9: Most likely.

Final diagnosis: Cough - R05.9

P
Care.
---
FILLED·asserted  History filled.
"""
SCOPE = {"fields": [], "sections": ["worksheet"]}


class RepairChain(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        self.note = self.run / "note-1.md"
        self.note.write_text(NOTE, encoding="utf-8")
        self.before = self.run / "before.md"
        self.before.write_bytes(self.note.read_bytes())

    def test_unrecorded_change_breaks_terminal_chain(self):
        repairs.place(self.run, self.note, "note")
        self.assertFalse(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        self.note.write_text(NOTE.replace("Care.", "Changed care."), encoding="utf-8")
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_scoped_prose_repair_retains_evidence_and_ends_chain(self):
        repairs.place(self.run, self.note, "note")
        self.note.write_text(NOTE.replace("Care.", "Changed care."), encoding="utf-8")
        result = repairs.record_repair(self.run, self.before, self.note, {"fields": [], "sections": ["P"]})
        self.assertEqual("pass", result["verdict"])
        self.assertEqual(["P"], result["sections"])
        self.assertFalse(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        self.assertIn("sections=P", repairs.repairs_report(self.run))
        payload = repairs.ledger(self.run)
        copy = self.run / payload["files"][str(self.note.resolve())]["repairs"][0]["copies"] / "before.md"
        copy.write_text("tampered", encoding="utf-8")
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_verdict_change_inside_allowed_assessment_still_fails(self):
        self.note.write_text(NOTE.replace("Most likely", "Less likely"), encoding="utf-8")
        result = repairs.compare(self.before, self.note, {"fields": [], "sections": ["A"]}, "note")
        self.assertIn("differential-verdicts", result["violations"])

    def test_real_note_verdict_mutation_exits_one(self):
        fixture = Path(__file__).resolve().parents[1] / "fixtures/descriptor-agreement-note-path-control/notes/case-01.md"
        text = fixture.read_text(encoding="utf-8")
        self.assertIn("Less likely.", text)
        self.note.write_text(text, encoding="utf-8")
        self.before.write_bytes(self.note.read_bytes())
        repairs.place(self.run, self.note, "note")
        self.note.write_text(text.replace("Less likely.", "Favored.", 1), encoding="utf-8")
        scope = self.run / "scope.json"
        scope.write_text(json.dumps({"fields": [], "sections": ["A"]}), encoding="utf-8")
        self.assertEqual(1, repairs.main(["compare", str(self.run), "--before", str(self.before), "--after", str(self.note), "--scope", str(scope)]))

    def test_code_change_anywhere_cannot_escape_named_population(self):
        for changed in (NOTE.replace("R05.9", "R06.02"), NOTE + "NOT CODED: R06.02 Shortness of breath, unestablished.\n"):
            self.note.write_text(changed, encoding="utf-8")
            self.assertIn("note-codes", repairs.compare(self.before, self.note, {"fields": [], "sections": ["A", "tail"]}, "note")["violations"])

    def test_allowed_verdict_change_passes_but_unknown_scope_is_refused(self):
        self.note.write_text(NOTE.replace("Most likely", "Less likely"), encoding="utf-8")
        self.assertEqual("pass", repairs.compare(self.before, self.note, {"fields": ["differential-verdicts"], "sections": ["A"]}, "note")["verdict"])
        with self.assertRaises(ValueError):
            repairs.compare(self.before, self.note, {"fields": ["anything"], "sections": ["A"]}, "note")

    def test_real_committed_worksheet_status_mutation_is_refused_by_command(self):
        fixture = Path(__file__).resolve().parents[1] / "fixtures/filled-anchor/run-2/case-01.md"
        self.assertTrue(fixture.exists())
        text = fixture.read_text(encoding="utf-8")
        entry = next(repairs.worksheet.ENTRY.finditer(text))
        # The allowed worksheet section cannot authorize changing entry status.
        self.note.write_text(text, encoding="utf-8")
        self.before.write_bytes(self.note.read_bytes())
        repairs.place(self.run, self.note, "worksheet")
        self.note.write_text(text[:entry.end()] + " NOT FOR ENTRY" + text[entry.end():], encoding="utf-8")
        scope = self.run / "scope.json"
        scope.write_text(json.dumps(SCOPE), encoding="utf-8")
        self.assertEqual(1, repairs.main(["compare", str(self.run), "--before", str(self.before), "--after", str(self.note), "--scope", str(scope)]))
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_outside_scope_section_is_disclosed_without_blocking(self):
        repairs.place(self.run, self.note, "note")
        self.note.write_text(NOTE.replace("Care.", "Changed care."), encoding="utf-8")
        result = repairs.record_repair(self.run, self.before, self.note, {"fields": [], "sections": ["A"]})
        self.assertEqual("pass", result["verdict"])
        self.assertIn("P (outside scope)", repairs.repairs_report(self.run))

    def test_missing_or_never_run_comparison_is_not_a_chain(self):
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        repairs.place(self.run, self.note, "note")
        payload = repairs.ledger(self.run)
        payload["files"][str(self.note.resolve())]["repairs"].append({"before": repairs.digest(self.note), "after": repairs.digest(self.note)})
        repairs.write_ledger(self.run, payload)
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])


if __name__ == "__main__":
    unittest.main()
