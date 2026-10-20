"""Behavioral checks for placement, bounded repairs, and retained evidence."""

# phi-scan: synthetic

import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import artifact_repairs as repairs
import artifact_lock
import aar_scan
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
FILLEDÂ·asserted  History filled.
"""
SCOPE = {"fields": [], "sections": ["worksheet"]}


class RepairChain(unittest.TestCase):
    def command(self, *arguments):
        return repairs.main([str(a) for a in arguments])

    def start(self, fields=()):
        scope = self.run / "scope.json"
        scope.write_text(json.dumps({"fields": list(fields), "sections": ["A", "P"]}))
        self.assertEqual(0, self.command("begin", self.run, self.note, "--scope", scope))
        return scope

    def failed_repair(self):
        self.assertEqual(0, self.command("place", self.run, self.note, "--kind", "note"))
        self.start()
        self.note.write_text(NOTE.replace("Most likely", "Less likely"), encoding="utf-8")
        self.assertEqual(1, self.command("compare", self.run, "--after", self.note))
        return repairs.ledger(self.run)["files"][str(self.note)]["repairs"][0]["id"]

    def test_begin_refuses_changed_file_and_compare_requires_open_begin(self):
        self.command("place", self.run, self.note, "--kind", "note")
        self.assertEqual(2, self.command("compare", self.run, "--after", self.note))
        self.note.write_text(NOTE + "Changed.")
        scope = self.run / "scope.json"
        scope.write_text(json.dumps(SCOPE))
        self.assertEqual(2, self.command("begin", self.run, self.note, "--scope", scope))
        self.assertNotIn("pending", repairs.ledger(self.run)["files"][str(self.note)])

    def test_open_begin_is_incomplete_and_cannot_be_overwritten(self):
        self.command("place", self.run, self.note, "--kind", "note")
        scope = self.start()
        original = repairs.ledger_path(self.run).read_bytes()
        self.assertEqual(2, self.command("begin", self.run, self.note, "--scope", scope))
        self.assertEqual(original, repairs.ledger_path(self.run).read_bytes())
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_restoration_is_recorded_then_new_begin_succeeds_and_failure_stays(self):
        self.failed_repair()
        self.start(["differential-text"])
        self.note.write_bytes(self.before.read_bytes())
        self.assertEqual(0, self.command("compare", self.run, "--after", self.note))
        self.start()
        self.note.write_text(NOTE.replace("Care.", "Changed care."))
        self.assertEqual(0, self.command("compare", self.run, "--after", self.note))
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        self.assertEqual(3, len(repairs.ledger(self.run)["files"][str(self.note)]["repairs"]))

    def test_supersession_requires_verified_whole_reply_and_rechecks_retained_evidence(self):
        repair_id = self.failed_repair()
        scope = self.run / "accept-scope.json"
        scope.write_text(json.dumps({"fields": ["differential-text"], "sections": ["A", "P"]}))
        reply = "I accept this differential repair."
        args = ("re-scope", self.run, self.note, "--repair", repair_id,
                "--scope", scope, "--clinician-reply", reply)
        # Test through real transcript discovery and whole-message verification.
        sessions = self.run / "sessions"
        sessions.mkdir()
        reference = {"type": "assistant", "message": {"content": [{
            "type": "tool_use", "id": "read-run", "name": "read",
            "input": {"path": str(self.run)}}]}}
        transcript = sessions / "main.jsonl"
        with (mock.patch.object(aar_scan, "transcript_roots", return_value=(sessions,)),
              mock.patch.object(aar_scan, "is_live_run", return_value=True),
              mock.patch.object(aar_scan.repo_root, "scratch_root", return_value=Path(self.temp.name) / "scratch")):
            transcript.write_text(json.dumps(reference) + "\n")
            original = repairs.ledger_path(self.run).read_bytes()
            self.assertEqual(2, self.command(*args))
            self.assertEqual(original, repairs.ledger_path(self.run).read_bytes())
            human = {"type": "user", "timestamp": "2100-10-09T12:00:00Z",
                     "message": {"content": reply}}
            transcript.write_text(json.dumps(reference) + "\n" + json.dumps(human) + "\n")
            self.assertEqual(0, self.command(*args))
            self.assertFalse(repairs.completion_gate(self.run, "shift", (self.note,))[0])
            self.assertIn("superseded by clinician", repairs.repairs_report(self.run))
            self.assertEqual(2, self.command(*args))
            record = repairs.ledger(self.run)["files"][str(self.note)]
            self.assertEqual("fail", record["repairs"][0]["comparison"]["verdict"])
            retained = self.run / record["repairs"][0]["copies"] / "before.md"
            retained.write_text("tampered")
            self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_legacy_population_is_read_but_cannot_be_declared_for_new_repairs(self):
        self.command("place", self.run, self.note, "--kind", "note")
        self.start(["differential-text"])
        self.note.write_text(NOTE.replace("Most likely", "Less likely"))
        self.assertEqual(0, self.command("compare", self.run, "--after", self.note))
        payload = repairs.ledger(self.run)
        repair = payload["files"][str(self.note)]["repairs"][0]
        repair["scope"]["fields"] = ["differential-verdicts"]
        repair["comparison"]["changed"] = ["differential-verdicts"]
        repairs.write_ledger(self.run, payload)
        self.assertFalse(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        scope = self.run / "scope.json"
        scope.write_text(json.dumps(repair["scope"]))
        self.assertEqual(2, self.command("begin", self.run, self.note, "--scope", scope))

    def test_every_writer_refuses_held_lock_without_changing_ledger(self):
        repair_id = self.failed_repair()
        scope = self.run / "scope.json"
        original = repairs.ledger_path(self.run).read_bytes()
        with artifact_lock.hold(repairs.ledger_path(self.run), "other writer"):
            for args in (("place", self.run, self.before, "--kind", "note"),
                         ("begin", self.run, self.note, "--scope", scope),
                         ("compare", self.run, "--after", self.note),
                         ("re-scope", self.run, self.note, "--repair", repair_id,
                          "--scope", scope, "--clinician-reply", "Accepted")):
                self.assertEqual(2, self.command(*args))
            with self.assertRaises(artifact_lock.ArtifactBusy):
                repairs.write_ledger(self.run, {"files": {}})
        self.assertEqual(original, repairs.ledger_path(self.run).read_bytes())

    def test_relative_artifact_path_is_refused(self):
        self.assertEqual(2, self.command("place", self.run, "note.md", "--kind", "note"))

    def test_reproduction_requires_scope_before_relabel_and_keeps_failure(self):
        # PR #1842's narrow-scope relabel, through the settled command route.
        scope = self.run / "scope.json"
        scope.write_text(json.dumps({"fields": ["differential-items"], "sections": ["A"]}))
        self.assertEqual(0, repairs.main(["place", str(self.run), str(self.note), "--kind", "note"]))
        self.assertEqual(0, repairs.main(["begin", str(self.run), str(self.note), "--scope", str(scope)]))
        self.note.write_text(NOTE.replace("1. Cough", "1. Acute cough"), encoding="utf-8")
        self.assertEqual(1, repairs.main(["compare", str(self.run), "--after", str(self.note)]))
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        self.assertIn("awaiting clinician", repairs.repairs_report(self.run))

    def test_limit_pointer_names_the_object_without_copying_it(self):
        surface = (Path(__file__).resolve().parents[1] / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual((), bind(repairs.DECLARED_LIMITS, surface, mode=NAMING))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name).resolve() / "scratch" / "runs" / "synthetic-repairs"
        self.run.mkdir(parents=True)
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
        repairs.begin(self.run, self.note, {"fields": [], "sections": ["P"]})
        self.note.write_text(NOTE.replace("Care.", "Changed care."), encoding="utf-8")
        result = repairs.record_repair(self.run, self.note)
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
        self.assertIn("differential-text", result["violations"])

    def test_real_note_verdict_mutation_exits_one(self):
        fixture = Path(__file__).resolve().parents[1] / "fixtures/descriptor-agreement-note-path-control/notes/case-01.md"
        text = fixture.read_text(encoding="utf-8")
        self.assertIn("Less likely.", text)
        self.note.write_text(text, encoding="utf-8")
        self.before.write_bytes(self.note.read_bytes())
        repairs.place(self.run, self.note, "note")
        scope = self.run / "scope.json"
        scope.write_text(json.dumps({"fields": [], "sections": ["A"]}), encoding="utf-8")
        self.assertEqual(0, repairs.main(["begin", str(self.run), str(self.note), "--scope", str(scope)]))
        self.note.write_text(text.replace("Less likely.", "Favored.", 1), encoding="utf-8")
        self.assertEqual(1, repairs.main(["compare", str(self.run), "--after", str(self.note)]))

    def test_code_change_anywhere_cannot_escape_named_population(self):
        for changed in (NOTE.replace("R05.9", "R06.02"), NOTE + "NOT CODED: R06.02 Shortness of breath, unestablished.\n"):
            self.note.write_text(changed, encoding="utf-8")
            self.assertIn("note-codes", repairs.compare(self.before, self.note, {"fields": [], "sections": ["A", "tail"]}, "note")["violations"])

    def test_allowed_verdict_change_passes_but_unknown_scope_is_refused(self):
        self.note.write_text(NOTE.replace("Most likely", "Less likely"), encoding="utf-8")
        self.assertEqual("pass", repairs.compare(self.before, self.note, {"fields": ["differential-text"], "sections": ["A"]}, "note")["verdict"])
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
        scope = self.run / "scope.json"
        scope.write_text(json.dumps(SCOPE), encoding="utf-8")
        self.assertEqual(0, repairs.main(["begin", str(self.run), str(self.note), "--scope", str(scope)]))
        self.note.write_text(text[:entry.end()] + " NOT FOR ENTRY" + text[entry.end():], encoding="utf-8")
        self.assertEqual(1, repairs.main(["compare", str(self.run), "--after", str(self.note)]))
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])

    def test_worksheet_verdict_in_legacy_prose_is_protected(self):
        fixture = Path(__file__).resolve().parents[1] / "fixtures/filled-anchor/run-2/case-01.md"
        text = fixture.read_text(encoding="utf-8")
        self.assertIn("Favored, and the only differential", text)
        self.before.write_text(text, encoding="utf-8")
        self.note.write_text(text.replace("Favored, and the only differential", "Ruled out, and the only differential"), encoding="utf-8")
        self.assertIn("differential-text", repairs.compare(self.before, self.note, SCOPE, "worksheet")["violations"])

    def test_anchor_repair_does_not_authorize_a_note_field_verdict_change(self):
        text = "--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---\nICD-10 R05.9 Cough NOT FOR ENTRY\n  ANCHOR: cough\n  SOURCE: given\n  NOTE: less likely\n"
        self.before.write_text(text, encoding="utf-8")
        self.note.write_text(text.replace("ANCHOR: cough", "ANCHOR: documented cough"), encoding="utf-8")
        self.assertEqual("pass", repairs.compare(self.before, self.note, SCOPE, "worksheet")["verdict"])
        self.note.write_text(text.replace("NOTE: less likely", "NOTE: favored"), encoding="utf-8")
        self.assertIn("differential-text", repairs.compare(self.before, self.note, SCOPE, "worksheet")["violations"])

    def test_outside_scope_section_is_disclosed_without_blocking(self):
        repairs.place(self.run, self.note, "note")
        repairs.begin(self.run, self.note, {"fields": [], "sections": ["A"]})
        self.note.write_text(NOTE.replace("Care.", "Changed care."), encoding="utf-8")
        result = repairs.record_repair(self.run, self.note)
        self.assertEqual("pass", result["verdict"])
        self.assertIn("P (outside scope)", repairs.repairs_report(self.run))

    def test_missing_or_never_run_comparison_is_not_a_chain(self):
        self.assertTrue(repairs.completion_gate(self.run, "shift", (self.note,))[0])
        repairs.place(self.run, self.note, "note")
        payload = repairs.ledger(self.run)
        payload["files"][str(self.note.resolve())]["repairs"].append({"before": repairs.digest(self.note), "after": repairs.digest(self.note)})
        repairs.write_ledger(self.run, payload)
        from run_record_reader import UnreadableRecord
        with self.assertRaises(UnreadableRecord):
            repairs.completion_gate(self.run, "shift", (self.note,))


if __name__ == "__main__":
    unittest.main()
