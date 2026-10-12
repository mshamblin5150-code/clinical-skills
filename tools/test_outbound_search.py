"""Public command checks for ADR 0347's encounter search boundary."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import outbound_search as command
import differential_scan
import filled_vitals_census
from prose_bind import NAMING, bind


class OutboundSearchCommand(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        self.profile = self.run / "profile.md"
        self.profile.write_text("**Site**:\n\n```\nSynthetic Clinic\n```\n", encoding="utf-8")
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(command.phi_scan, "corpus_identifiers", return_value=({"Fictional Person"}, {"private-date"})).start()
        mock.patch.object(command.phi_scan, "missing_corpus_sources", return_value=[]).start()

    def invoke(self, query):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return command.main(["check", query, "--run", str(self.run), "--search-id", "search-a", "--profile", str(self.profile)])

    def test_clean_search_is_recorded_before_a_pull(self):
        self.assertEqual(0, self.invoke("pneumonia older adult female"))
        record = json.loads((self.run / "outbound-searches.jsonl").read_text())
        self.assertEqual("pneumonia older adult female", record["query"])
        self.assertEqual("search-a", record["search_id"])

    def test_refused_search_writes_nothing(self):
        for query in ("pneumonia age 42", "pneumonia ２０", "pneumonia October twelve", "Fictional Person pneumonia", "pneumonia private-date", "pneumonia Synthetic Clinic", "pneumonia child adult", "pneumonia older adult adult", "pneumonia female male", "pneumonia male male"):
            with self.subTest(query=query):
                self.assertEqual(2, self.invoke(query))
                self.assertFalse((self.run / "outbound-searches.jsonl").exists())

    def test_missing_corpus_or_profile_refuses_without_recording(self):
        with mock.patch.object(command.phi_scan, "missing_corpus_sources", return_value=["name-index.json"]):
            self.assertEqual(2, self.invoke("pneumonia adult"))
        self.profile.unlink()
        self.assertEqual(2, self.invoke("pneumonia adult"))
        self.assertFalse((self.run / command.SEARCHES).exists())

    def test_pull_command_requires_the_pretyping_record(self):
        arguments = ["pull", "--run", str(self.run), "--search-id", "search-a", "--dump-id", "live-a"]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(2, command.main(arguments))
            self.assertEqual(0, self.invoke("pneumonia adult"))
            self.assertEqual(0, command.main(arguments))
        self.assertEqual((False, "Outbound searches: clean - 1 live pull(s), 1 search record(s)"), command.completion_gate(self.run, "note-a"))
        (self.run / command.SEARCHES).unlink()
        failed, report = command.completion_gate(self.run, "note-a")
        self.assertTrue(failed)
        self.assertIn("lack a passed search-record line", report)

    def test_declared_limits_are_named_beside_the_command_instructions(self):
        text = (Path(__file__).resolve().parents[1] / "skills/clinical-note/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual((), bind(command.DECLARED_LIMITS, text, mode=NAMING))

    def test_account_location_site_label_is_checked(self):
        self.profile.write_text("**Location / Site** - exact strings:\n\n```\nSynthetic Clinic.\n```\n", encoding="utf-8")
        self.assertEqual(2, self.invoke("pneumonia Synthetic Clinic"))
        self.assertEqual(0, self.invoke("pneumonia adult"))

    def test_both_submission_commands_report_an_unmatched_live_pull(self):
        (self.run / "note.md").write_text("A:\nDifferential:\n1. Cough - R05.9: Documented symptom. Most likely.\n\nFILLED:\nFILLED·asserted Height 66 in for a 40-year-old female.\n", encoding="utf-8")
        (self.run / command.PULLS).write_text(json.dumps({"search_id": "missing", "dump_id": "live-a"}) + "\n", encoding="utf-8")
        for grader in (differential_scan, filled_vitals_census):
            with self.subTest(grader=grader.__name__), contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(1, grader.main([str(self.run), "--submission", "synthetic"]))
                self.assertIn("live pull(s) lack a passed search-record line", output.getvalue())


if __name__ == "__main__":
    unittest.main()
