"""ADR0381 reversal candidates and search-before-landing public controls."""
# phi-scan: synthetic
import artifact_lock_test_support
import contextlib
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import aar_scan


class ReversalCandidates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "run"
        self.run.mkdir()
        self.memory = self.root / "memory" / "MEMORY.md"
        self.memory.parent.mkdir()
        self.memory.write_text("# Index\n", encoding="utf-8")
        self.transcript = self.root / "session.jsonl"
        self.transcript.write_text(json.dumps({"type": "user", "uuid": "user-1",
            "timestamp": "2026-10-19T10:00:00Z", "message": {"content": "Correct the workflow."}}) + "\n", encoding="utf-8")
        for name, value in (("_check_snapshot_posted_reading", None),
                            ("_posted_reading_fingerprint", "a" * 64), ("_tracked_files", ()),
                            ("count_later_sittings", 0)):
            patch = mock.patch.object(aar_scan, name, return_value=value)
            patch.start()
            self.addCleanup(patch.stop)
        patch = mock.patch.object(aar_scan, "discover_transcripts", return_value=
            aar_scan.TranscriptDiscovery((self.transcript,), 1, 0, 0, 1))
        patch.start()
        self.addCleanup(patch.stop)
        self.input = aar_scan.reversal_candidates_path(self.run, "synthetic", 1)
        self.input.parent.mkdir()

    def command(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = aar_scan.main([str(self.run), "--submission", "synthetic", *args])
        return status, output.getvalue() + error.getvalue()

    def extract(self, text="none\n"):
        self.input.write_text(text, encoding="utf-8")
        status, report = self.command("--memory-index", str(self.memory), "--extract")
        self.assertEqual(0, status, report)
        path = aar_scan.extract_path(self.run, "synthetic")
        self.fields, self.entries = aar_scan._extract_entries_text(path.read_text(encoding="utf-8"))
        self.record = aar_scan.review_path(self.run, "synthetic")
        self.record.write_text("\n".join((
            "SUBMISSION: synthetic", "TRANSCRIPTS: " + self.fields["TRANSCRIPTS"],
            "POPULATION: " + self.fields["POPULATION"], "UNREAD: 0", "WATERMARK: " + self.fields["WATERMARK"],
            "MEMORY-INDEX: " + str(self.memory), "CLASSIFIER: fresh reader", "CLASSIFIER-ENTRY: reader-1",
            "DISAGREEMENTS: none recorded", "CORRECTIONS: none", "SUSTAINS: none", "")), encoding="utf-8")
        aar_scan.measure_memory(self.run, "synthetic", 1)

    def append(self, text):
        with self.record.open("a", encoding="utf-8") as stream:
            stream.write(text)

    def correction(self, event="user-1", disposition="memory-write", landing=None):
        self.record.write_text(self.record.read_text(encoding="utf-8").replace("CORRECTIONS: none\n", ""), encoding="utf-8")
        target = self.memory.parent / "correction.md"
        target.write_text("# Corrected workflow\n", encoding="utf-8")
        self.append(f"\n## CORRECTION: {event}\nCORRECTOR: clinician\nIN-ERROR: orchestrator\n"
                    "SUMMARY: The workflow was corrected.\nCLASSIFIER: memory-write - retain the rule\n"
                    "ORCHESTRATOR: agree - retain the corrected rule\n"
                    f"DISPOSITION: {disposition}\nTARGET: {target}\nLANDING: {landing or 'recorded correction'}\n")

    def test_absent_file_writes_neither_extract_nor_baseline_and_none_passes(self):
        status, report = self.command("--memory-index", str(self.memory), "--extract")
        self.assertEqual(2, status, report)
        self.assertFalse(aar_scan.extract_path(self.run, "synthetic").exists())
        self.assertFalse(aar_scan.baseline_path(self.run, "synthetic").exists())
        self.extract()
        self.assertEqual(0, self.command()[0])
        self.assertNotIn("reversals", self.fields["TRANSCRIPT-WATERMARKS"])

    def test_every_candidate_needs_an_answer_and_a_reasoned_rejection_passes(self):
        self.extract("Corrected the workflow.\nCorrected the second workflow.\n")
        self.assertEqual(1, self.command()[0])
        self.append("\n## CANDIDATE: 1\nANSWER: not a correction - no contradiction stood\n")
        self.assertEqual(1, self.command()[0])
        self.append("\n## CANDIDATE: 2\nANSWER: not a correction - the earlier claim was supported\n")
        status, report = self.command()
        self.assertEqual(0, status, report)
        self.assertIn("reversal candidates: 2; answered 2; not a correction 2", report)

    def test_candidate_grade_uses_the_strict_extract_read_and_damage_is_not_empty(self):
        self.extract("Corrected the workflow.\n")
        self.append("\n## CANDIDATE: 1\nANSWER: not a correction - the earlier claim was supported\n")
        path = aar_scan.extract_path(self.run, "synthetic")
        read_text = Path.read_text
        def no_unchecked_extract_read(source, *args, **kwargs):
            self.assertNotEqual(path, source, "candidate grading must reuse the classified extract entries")
            return read_text(source, *args, **kwargs)
        with mock.patch.object(Path, "read_text", no_unchecked_extract_read):
            status, report = self.command()
        self.assertEqual(0, status, report)
        for damaged in (b"{", b"SUBMISSION: synthetic\nPOPULATION: wrong\n\n", b"\xff"):
            with self.subTest(damage=damaged):
                path.write_bytes(damaged)
                status, report = self.command()
                self.assertEqual(2, status, report)
                self.assertIn("unread remainder 1", report)
                self.assertIn("extract-dependent checks: not graded", report)
                self.assertNotIn("reversal-candidates:", report)

    def test_answer_must_name_a_recorded_correction_or_have_a_substantive_reason(self):
        self.extract("Corrected the workflow.\n")
        base = self.record.read_text(encoding="utf-8")
        for answer in ("user-1", "not a correction - ", "not a correction - no"):
            with self.subTest(answer=answer):
                self.record.write_text(base, encoding="utf-8")
                self.append("\n## CANDIDATE: 1\nANSWER: " + answer + "\n")
                self.assertEqual(1, self.command()[0])
        self.record.write_text(base, encoding="utf-8")
        self.correction()
        self.append("\n## CANDIDATE: 1\nANSWER: user-1\n")
        self.assertEqual(0, self.command()[0])
        self.append("\n## CANDIDATE: 1\nANSWER: user-1\n")
        self.assertEqual(1, self.command()[0])

    def test_neither_correction_nor_sustain_can_rest_on_candidate_entry(self):
        self.extract()
        candidate = next(entry.identifier for entry in self.entries if entry.kind == "reversal-candidates")
        self.correction(candidate)
        status, report = self.command("--show")
        self.assertEqual(1, status, report)
        self.assertIn("correction-on-extractor-written-entry", report)
        self.record.write_text(self.record.read_text(encoding="utf-8").replace("SUSTAINS: none\n", ""), encoding="utf-8")
        self.append(f"\n## SUSTAIN: {candidate}\nSUMMARY: Retain the workflow.\n")
        self.assertIn("sustain-on-reversal-candidates", self.command("--show")[1])

    def test_rebuild_retains_its_round_file_and_refuses_a_changed_input(self):
        self.extract("Corrected the workflow.\n")
        self.assertEqual(1, self.command("--memory-index", str(self.memory), "--extract", "--rebuild-round", "1")[0])
        self.input.write_text("Changed population.\n", encoding="utf-8")
        status, report = self.command("--memory-index", str(self.memory), "--extract", "--rebuild-round", "1")
        self.assertEqual(2, status, report)
        self.assertIn("do not match", report)

    def test_next_round_requires_its_own_file(self):
        self.extract()
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"type": "user", "uuid": "u2", "message": {"content": "Review again."}}) + "\n")
        status, report = self.command("--memory-index", str(self.memory), "--extract")
        self.assertEqual(2, status, report)
        self.assertFalse(aar_scan.extract_path(self.run, "synthetic", 2).exists())

    def test_reversal_files_are_never_reopened_as_review_cursors(self):
        original = aar_scan.read_review
        def read_review(path, **kwargs):
            self.assertFalse(path.name.endswith(".reversal-candidates.md"))
            return original(path, **kwargs)
        with mock.patch.object(aar_scan, "read_review", side_effect=read_review):
            self.extract()
            self.assertEqual(0, self.command()[0])

    def test_search_before_landing_is_required_in_both_transcript_shapes(self):
        self.extract()
        landing = "https://github.com/example/repo/issues/42#issuecomment-123"
        self.correction(disposition="tracker-ticket", landing=landing)
        base = self.transcript.read_text(encoding="utf-8")
        when = datetime.fromisoformat(self.fields["EXTRACTED-AT"].replace("Z", "+00:00"))
        def codex(command, at, output="", failed=False):
            return {"type": "event_msg", "timestamp": at.isoformat(), "payload": {"type": "item_completed",
                "item": {"type": "CommandExecution", "command": command, "status": "completed", "exit_code": int(failed), "stdout": output}}}
        for shape in ("codex", "claude"):
            for mode in ("absent", "late", "failed", "echo", "before-extract", "correct"):
                with self.subTest(shape=shape, mode=mode):
                    search_at = when + timedelta(seconds=3 if mode == "late" else 1)
                    if mode == "before-extract":
                        search_at = when - timedelta(seconds=1)
                    command = "echo 'gh issue list --state all --search workflow'" if mode == "echo" else "gh issue list --state all --search workflow"
                    rows = []
                    if mode != "absent":
                        if shape == "codex":
                            rows.append(codex(command, search_at, failed=mode == "failed"))
                        else:
                            rows += [{"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "search", "name": "Bash", "input": {"command": command}}]}},
                                     {"type": "user", "timestamp": search_at.isoformat(), "message": {"content": [{"type": "tool_result", "tool_use_id": "search", "is_error": mode == "failed", "content": "[]"}]}}]
                    rows.append(codex("gh issue comment 42", when + timedelta(seconds=2), landing))
                    self.transcript.write_text(base + "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
                    status, report = self.command("--show")
                    self.assertEqual(0 if mode in {"correct", "before-extract"} else 1, status, report)

    def test_pre_build_round_keeps_its_grade_and_the_exact_boundary_enables_new_checks(self):
        self.extract()
        landing = "https://github.com/example/repo/issues/42#issuecomment-123"
        self.correction(disposition="tracker-ticket", landing=landing)
        cutoff = aar_scan.REVERSAL_CANDIDATES_CUTOFF
        (self.memory.parent / "correction.md").unlink()  # Tracker landing adds no memory.
        candidate = next(entry.identifier for entry in self.entries if entry.kind == "reversal-candidates")
        self.record.write_text(self.record.read_text(encoding="utf-8").replace("SUSTAINS: none\n", ""), encoding="utf-8")
        self.append(f"\n## SUSTAIN: {candidate}\nSUMMARY: Retain the settled workflow.\n")
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"type": "event_msg", "timestamp": (cutoff + timedelta(seconds=5)).isoformat(),
                "payload": {"type": "item_completed", "item": {"type": "CommandExecution",
                    "command": "gh issue comment 42", "status": "completed", "exit_code": 0, "stdout": landing}}}) + "\n")
        self.input.unlink()
        path = aar_scan.extract_path(self.run, "synthetic")
        original = path.read_text(encoding="utf-8")
        for when, expected in ((cutoff - timedelta(microseconds=1), 0), (cutoff, 1)):
            with self.subTest(when=when):
                path.write_text(original.replace(self.fields["EXTRACTED-AT"], when.isoformat()), encoding="utf-8")
                aar_scan.measure_memory(self.run, "synthetic", 1)
                status, report = self.command("--show")
                self.assertEqual(expected, status, report)
                if expected:
                    self.assertIn("reversal-candidates:", report)
                    self.assertIn("missing-landing-search:", report)
                    self.assertIn("sustain-on-reversal-candidates:", report)
                else:
                    self.assertIn("not graded - extract predates check", report)


if __name__ == "__main__":
    unittest.main()
