"""Behavioral checks for placement, bounded repairs, and retained evidence."""

# phi-scan: synthetic

import json
import tempfile
import unittest
from pathlib import Path

import artifact_repairs as repairs
import artifact_lock_test_support
from code_set_database_test_support import ICD10_DATABASE_SHA256, assert_code_set_database_digest
from prose_bind import NAMING, bind

assert_code_set_database_digest(
    Path(__file__).resolve().parents[1] / "reference/icd10cm-2026.sqlite",
    ICD10_DATABASE_SHA256,
    "ICD-10-CM Code-set database",
)

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
    def test_limit_pointer_names_the_object_without_copying_it(self):
        surface = (Path(__file__).resolve().parents[1] / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual((), bind(repairs.DECLARED_LIMITS, surface, mode=NAMING))

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

    def test_worksheet_verdict_in_legacy_prose_is_protected(self):
        fixture = Path(__file__).resolve().parents[1] / "fixtures/filled-anchor/run-2/case-01.md"
        text = fixture.read_text(encoding="utf-8")
        self.assertIn("Favored, and the only differential", text)
        self.before.write_text(text, encoding="utf-8")
        self.note.write_text(text.replace("Favored, and the only differential", "Ruled out, and the only differential"), encoding="utf-8")
        self.assertIn("differential-verdicts", repairs.compare(self.before, self.note, SCOPE, "worksheet")["violations"])

    def test_anchor_repair_does_not_authorize_a_note_field_verdict_change(self):
        text = "--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---\nICD-10 R05.9 Cough NOT FOR ENTRY\n  ANCHOR: cough\n  SOURCE: given\n  NOTE: less likely\n"
        self.before.write_text(text, encoding="utf-8")
        self.note.write_text(text.replace("ANCHOR: cough", "ANCHOR: documented cough"), encoding="utf-8")
        self.assertEqual("pass", repairs.compare(self.before, self.note, SCOPE, "worksheet")["verdict"])
        self.note.write_text(text.replace("NOTE: less likely", "NOTE: favored"), encoding="utf-8")
        self.assertIn("differential-verdicts", repairs.compare(self.before, self.note, SCOPE, "worksheet")["violations"])

    def test_outside_scope_section_is_disclosed_without_blocking(self):
        repairs.place(self.run, self.note, "note")
        self.note.write_text(NOTE.replace("Care.", "Changed care."), encoding="utf-8")
        result = repairs.record_repair(self.run, self.before, self.note, {"fields": [], "sections": ["A"]})
        self.assertEqual("pass", result["verdict"])
        self.assertIn("P (outside scope)", repairs.repairs_report(self.run))

    def test_narrow_scope_breaks_the_chain_until_an_equal_or_wider_rescope(self):
        repairs.place(self.run, self.note, "note")
        # Relabel the differential entry: the label also sits inside the item's
        # verdict text, so differential-items and differential-verdicts change.
        self.note.write_text(NOTE.replace("Cough", "Coughing"), encoding="utf-8")
        narrow = {"fields": ["differential-items"], "sections": ["A"]}
        result = repairs.record_repair(self.run, self.before, self.note, narrow)
        self.assertEqual("fail", result["verdict"])
        self.assertIn("differential-verdicts", result["violations"])
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        wide = {"fields": ["differential-items", "differential-verdicts"], "sections": ["A"]}
        result = repairs.record_repair(self.run, self.before, self.note, wide, rescope=True)
        self.assertEqual("pass", result["verdict"])
        self.assertFalse(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        report = repairs.repairs_report(self.run)
        self.assertIn("fail (superseded by a re-scope)", report)
        self.assertIn("differential-items,differential-verdicts,A", report)
        chain = repairs.ledger(self.run)["files"][str(self.note.resolve())]["repairs"]
        self.assertEqual(chain[0]["copies"], chain[1]["supersedes"])
        self.assertEqual("fail", chain[0]["comparison"]["verdict"])

    def test_rescope_route_exits_zero_through_the_command(self):
        repairs.place(self.run, self.note, "note")
        self.note.write_text(NOTE.replace("Cough", "Coughing"), encoding="utf-8")
        narrow = self.run / "narrow.json"
        narrow.write_text(json.dumps({"fields": ["differential-items"], "sections": ["A"]}), encoding="utf-8")
        self.assertEqual(1, repairs.main(["compare", str(self.run), "--before", str(self.before),
                                          "--after", str(self.note), "--scope", str(narrow)]))
        wide = self.run / "wide.json"
        wide.write_text(json.dumps({"fields": ["differential-items", "differential-verdicts"],
                                    "sections": ["A"]}), encoding="utf-8")
        self.assertEqual(0, repairs.main(["compare", str(self.run), "--before", str(self.before),
                                          "--after", str(self.note), "--scope", str(wide), "--rescope"]))
        self.assertFalse(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_rescope_requires_a_recorded_failed_pair(self):
        repairs.place(self.run, self.note, "note")
        scope = {"fields": [], "sections": ["P"]}
        with self.assertRaises(ValueError):
            repairs.record_repair(self.run, self.before, self.note, scope, rescope=True)
        self.note.write_text(NOTE.replace("Care.", "Changed care."), encoding="utf-8")
        repairs.record_repair(self.run, self.before, self.note, scope)
        # A passing comparison is not the failure this route exists to repair.
        with self.assertRaises(ValueError):
            repairs.record_repair(self.run, self.before, self.note, scope, rescope=True)

    def test_rescope_requires_the_same_pair_and_a_wider_declaration(self):
        repairs.place(self.run, self.note, "note")
        self.note.write_text(NOTE.replace("Cough", "Coughing"), encoding="utf-8")
        failed = {"fields": ["differential-items", "note-codes"], "sections": ["A", "P"]}
        result = repairs.record_repair(self.run, self.before, self.note, failed)
        self.assertEqual("fail", result["verdict"])
        # A later edit is a different pair, not a re-scope of the failed one.
        self.note.write_text(self.note.read_text(encoding="utf-8").replace("Care.", "Changed care."), encoding="utf-8")
        wide = {"fields": ["differential-items", "differential-verdicts"], "sections": ["A"]}
        with self.assertRaises(ValueError):
            repairs.record_repair(self.run, self.before, self.note, wide, rescope=True)
        # Re-scoping can only widen: dropping a declared population or section
        # would rewrite the recorded authorization backwards.
        self.note.write_text(NOTE.replace("Cough", "Coughing"), encoding="utf-8")
        with self.assertRaises(ValueError):
            repairs.record_repair(self.run, self.before, self.note,
                                  {"fields": ["differential-items"], "sections": ["A"]}, rescope=True)
        with self.assertRaises(ValueError):
            repairs.record_repair(self.run, self.before, self.note,
                                  {"fields": ["differential-items", "differential-verdicts", "note-codes"],
                                   "sections": ["A"]}, rescope=True)

    def test_a_rescope_that_still_fails_keeps_the_chain_broken(self):
        repairs.place(self.run, self.note, "note")
        self.note.write_text(NOTE.replace("Cough", "Coughing"), encoding="utf-8")
        repairs.record_repair(self.run, self.before, self.note,
                              {"fields": ["differential-items"], "sections": ["A"]})
        # Wider, but still not naming differential-verdicts.
        result = repairs.record_repair(self.run, self.before, self.note,
                                       {"fields": ["differential-items", "note-codes"], "sections": ["A"]},
                                       rescope=True)
        self.assertEqual("fail", result["verdict"])
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        result = repairs.record_repair(self.run, self.before, self.note,
                                       {"fields": ["differential-items", "differential-verdicts", "note-codes"],
                                        "sections": ["A"]}, rescope=True)
        self.assertEqual("pass", result["verdict"])
        self.assertFalse(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_tampered_evidence_of_a_superseded_record_is_still_a_finding(self):
        repairs.place(self.run, self.note, "note")
        self.note.write_text(NOTE.replace("Cough", "Coughing"), encoding="utf-8")
        repairs.record_repair(self.run, self.before, self.note,
                              {"fields": ["differential-items"], "sections": ["A"]})
        repairs.record_repair(self.run, self.before, self.note,
                              {"fields": ["differential-items", "differential-verdicts"], "sections": ["A"]},
                              rescope=True)
        self.assertFalse(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        superseded = self.run / repairs.ledger(self.run)["files"][str(self.note.resolve())]["repairs"][0]["copies"]
        (superseded / "before.md").write_text("tampered", encoding="utf-8")
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_superseding_a_passing_comparison_is_refused_by_the_gate(self):
        repairs.place(self.run, self.note, "note")
        self.note.write_text(NOTE.replace("Care.", "Changed care."), encoding="utf-8")
        scope = {"fields": [], "sections": ["P"]}
        repairs.record_repair(self.run, self.before, self.note, scope)
        self.assertFalse(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        # A ledger claiming the passing record was superseded cannot pass the
        # gate: re-scoping exists for a failed pair only.
        payload = repairs.ledger(self.run)
        record = payload["files"][str(self.note.resolve())]
        copies = self.run / record["repairs"][0]["copies"]
        forged = self.run / "private" / "repairs" / "forged"
        forged.mkdir(parents=True)
        (forged / "before.md").write_bytes((copies / "before.md").read_bytes())
        (forged / "after.md").write_bytes((copies / "after.md").read_bytes())
        record["repairs"].append({"before": record["repairs"][0]["before"],
                                  "after": record["repairs"][0]["after"],
                                  "scope": scope, "copies": str(forged.relative_to(self.run)),
                                  "comparison": record["repairs"][0]["comparison"],
                                  "supersedes": record["repairs"][0]["copies"]})
        repairs.write_ledger(self.run, payload)
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_missing_or_never_run_comparison_is_not_a_chain(self):
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        repairs.place(self.run, self.note, "note")
        payload = repairs.ledger(self.run)
        payload["files"][str(self.note.resolve())]["repairs"].append({"before": repairs.digest(self.note), "after": repairs.digest(self.note)})
        repairs.write_ledger(self.run, payload)
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])


if __name__ == "__main__":
    unittest.main()
