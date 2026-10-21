"""Public command checks for ADR 0347's encounter search boundary."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import artifact_lock_test_support  # noqa: F401
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

    def test_mismatched_sent_query_is_recorded_but_not_as_a_live_pull(self):
        self.assertEqual(0, self.invoke("pneumonia adult"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            status = command.main(["pull", "--run", str(self.run), "--search-id", "search-a",
                "--dump-id", "live-a", "--query-readback", "pneumonia Fictional Person",
                "--profile", str(self.profile)])
        self.assertEqual(2, status)
        record = command.records(self.run / command.PULLS)[0]
        self.assertEqual("mismatched", record["outcome"])
        self.assertFalse(record["sent_query_passed"])
        self.assertNotIn("dump_id", record)
        self.assertIn("1 mismatched search(es)", command.completion_gate(self.run, "note-a")[1])

    def test_passed_search_needs_an_outcome_and_failed_gap_pull_counts(self):
        self.assertEqual(0, self.invoke("pneumonia adult"))
        failed, report = command.completion_gate(self.run, "note-a")
        self.assertTrue(failed)
        self.assertIn("no recorded outcome", report)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            status = command.main(["failed-pull", "--run", str(self.run),
                "--search-id", "search-a", "--decision", "antibiotic choice",
                "--instrument", "browser reader", "--query-readback", "pneumonia adult",
                "--reason", "no-match", "--results-read", "0"])
        self.assertEqual(0, status)
        self.assertFalse(command.completion_gate(self.run, "note-a")[0])
        self.assertIn("1 failed pull(s)", command.completion_gate(self.run, "note-a")[1])

    def test_refused_search_writes_nothing(self):
        for query in ("pneumonia age 42", "pneumonia ２０", "pneumonia October twelve", "Fictional Person pneumonia", "pneumonia private-date", "pneumonia Synthetic Clinic", "pneumonia child adult", "pneumonia older adult adult", "pneumonia female male", "pneumonia male male"):
            with self.subTest(query=query):
                self.assertEqual(2, self.invoke(query))
                self.assertFalse((self.run / "outbound-searches.jsonl").exists())

    def test_timestamp_query_is_refused_before_a_live_search(self):
        with mock.patch.object(command.phi_scan, "corpus_identifiers", return_value=(set(), {"1988-04-17"})):
            self.assertEqual(2, self.invoke("pneumonia 1988-04-17T12:34:56Z"))
        self.assertFalse((self.run / command.SEARCHES).exists())

    def test_missing_corpus_or_profile_refuses_without_recording(self):
        with mock.patch.object(command.phi_scan, "missing_corpus_sources", return_value=["name-index.json"]):
            self.assertEqual(2, self.invoke("pneumonia adult"))
        self.profile.unlink()
        self.assertEqual(2, self.invoke("pneumonia adult"))
        self.assertFalse((self.run / command.SEARCHES).exists())

    def test_pull_command_requires_the_pretyping_record(self):
        arguments = ["pull", "--run", str(self.run), "--search-id", "search-a", "--dump-id", "live-a",
                     "--query-readback", "  PNEUMONIA   adult  "]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(2, command.main(arguments))
            self.assertEqual(0, self.invoke("pneumonia adult"))
            self.assertEqual(0, command.main(arguments))
        self.assertEqual((False, "Outbound searches: clean - 1 live pull(s), 1 search record(s)"), command.completion_gate(self.run, "note-a"))
        (self.run / command.SEARCHES).unlink()
        failed, report = command.completion_gate(self.run, "note-a")
        self.assertTrue(failed)
        self.assertIn("lack a passed search-record line", report)

    def test_failed_pull_requires_evidence_for_each_reason(self):
        self.assertEqual(0, self.invoke("pneumonia adult"))
        cases = (("signed-out", ["--page-url", "https://www.uptodate.com/login", "--sign-in-tried", "no"]),
                 ("service-unavailable", ["--page-url", "https://www.uptodate.com/error"]),
                 ("no-match", ["--results-read", "0"]),
                 ("page-unreadable", ["--page-url", "https://www.uptodate.com/topic", "--second-method", "page screenshot"]))
        for reason, evidence in cases:
            with self.subTest(reason=reason), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                args = ["failed-pull", "--run", str(self.run), "--search-id", "search-a",
                        "--query-readback", "pneumonia adult", "--reason", reason,
                        "--decision", "antibiotic choice", "--instrument", "browser reader"]
                self.assertEqual(2, command.main(args))
                self.assertFalse((self.run / command.PULLS).exists())
                self.assertEqual(0, command.main(args + evidence))
                self.assertFalse(command.completion_gate(self.run, "note-a")[0])
                (self.run / command.PULLS).unlink()

    def test_completion_refuses_a_live_pull_whose_recorded_readback_differs(self):
        self.assertEqual(0, self.invoke("pneumonia adult"))
        (self.run / command.PULLS).write_text(json.dumps({"search_id": "search-a", "dump_id": "live-a",
            "query_readback": "asthma adult"}) + "\n", encoding="utf-8")
        finding, report = command.completion_gate(self.run, "note-a")
        self.assertTrue(finding)
        self.assertIn("readback", report)

    def test_declared_limits_are_named_beside_the_command_instructions(self):
        text = (Path(__file__).resolve().parents[1] / "skills/clinical-note/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual((), bind(command.DECLARED_LIMITS, text, mode=NAMING))

    def test_account_location_site_label_is_checked(self):
        self.profile.write_text("**Location / Site** - exact strings:\n\n```\nSynthetic Clinic.\n```\n", encoding="utf-8")
        self.assertEqual(2, self.invoke("pneumonia Synthetic Clinic"))
        self.assertEqual(0, self.invoke("pneumonia adult"))

    def test_identifier_spacing_cannot_bypass_the_check(self):
        self.assertEqual(2, self.invoke("pneumonia Fictional   Person"))
        self.assertEqual(2, self.invoke("pneumonia Synthetic\tClinic"))

    def test_both_submission_commands_report_an_unmatched_live_pull(self):
        (self.run / "note.md").write_text("A:\nDifferential:\n1. Cough - R05.9: Documented symptom. Most likely.\n\nFILLED:\nFILLED·asserted Height 66 in for a 40-year-old female.\n", encoding="utf-8")
        (self.run / command.PULLS).write_text(json.dumps({"search_id": "missing", "dump_id": "live-a"}) + "\n", encoding="utf-8")
        for grader in (differential_scan, filled_vitals_census):
            with self.subTest(grader=grader.__name__), contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(1, grader.main([str(self.run), "--submission", "synthetic"]))
                self.assertIn("live pull(s) lack a passed search-record line", output.getvalue())


if __name__ == "__main__":
    unittest.main()
