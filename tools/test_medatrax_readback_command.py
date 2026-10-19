"""The committed writer and standalone check reject malformed portal records."""
from __future__ import annotations

import contextlib
import io
import json
import copy
import tempfile
import unittest
from pathlib import Path

import medatrax_posting


class ReadbackCommand(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name)
        (self.run / "note-3.md").write_bytes(b"approved note")
        self.payload = {
            "post_url": "https://example.org/patient-visits", "posted": "displayed time",
            "verdict_detail": "Saved visit and form match the approved fields and Entry copy.",
            "time_log": {"date": "displayed-date", "hours": 12, "minutes": 0, "outcome": "entered"},
            "visits": [{"patient": 3, "reference_status": "matched", "reference": "P-3",
                "patient_detail": "/patients/3", "note_view": "/forms/view?resultid=31",
                "visit_date": "displayed-date", "finished": "displayed-finished", "verdict": "matches"}],
        }
        self.input = self.run / "readback.json"

    def invoke(self, action):
        arguments = [action, "--run", str(self.run), "--submission", "shift", "--batch"]
        if action == "write":
            self.input.write_text(json.dumps(self.payload), encoding="utf-8")
            arguments += ["--input", str(self.input)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return medatrax_posting.main(arguments)

    def test_writer_computes_count_digest_and_hours_and_minutes_then_check_passes(self):
        self.assertEqual(0, self.invoke("write"))
        text = (self.run / "reread.md").read_text(encoding="utf-8")
        self.assertIn("READ: 1 of 1 read", text)
        self.assertIn("duration=12 hours 0 minutes", text)
        self.assertIn("SUBMISSION-SHA256: " + medatrax_posting.source_sha256((self.run / "note-3.md",)), text)
        self.assertEqual(0, self.invoke("check"))
        self.assertFalse(medatrax_posting.completion_gate(self.run, "shift", batch=True)[0])

    def test_no_write_for_stray_line_bad_patient_or_malformed_duration(self):
        clean = copy.deepcopy(self.payload)
        for mutate in (
            lambda: self.payload.update(posted="time\nstray copied line"),
            lambda: self.payload["visits"][0].update(patient=1),
            lambda: self.payload.update(time_log="12 hours"),
            lambda: self.payload["time_log"].update(minutes=60),
        ):
            with self.subTest(mutate=mutate):
                self.payload = copy.deepcopy(clean)
                mutate()
                self.assertEqual(2, self.invoke("write"))
                self.assertFalse((self.run / "reread.md").exists())

    def test_standalone_output_note_and_no_requested_time_log(self):
        note = self.run / "note-3.md"
        output = self.run / "output" / "encounter.md"
        output.parent.mkdir()
        note.rename(output)
        self.payload["time_log"] = None
        self.input.write_text(json.dumps(self.payload), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0, medatrax_posting.main(["write", "--run", str(self.run), "--submission", "note", "--notes", str(output), "--input", str(self.input)]))
            self.assertEqual(0, medatrax_posting.main(["check", "--run", str(self.run), "--submission", "note", "--notes", str(output)]))
        self.assertIn("TIME-LOG: not requested", (self.run / "reread.md").read_text())

    def test_hand_edited_stray_line_and_whole_hours_are_refused_before_aar(self):
        self.assertEqual(0, self.invoke("write"))
        path = self.run / "reread.md"
        clean = path.read_text(encoding="utf-8")
        for damaged in (clean + "stray copied line\n", clean.replace("12 hours 0 minutes", "12 hours")):
            path.write_text(damaged, encoding="utf-8")
            self.assertEqual(2, self.invoke("check"))
            before = path.read_bytes()
            self.assertEqual(2, self.invoke("write"))
            self.assertEqual(before, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
