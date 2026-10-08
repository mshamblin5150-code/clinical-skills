"""A snapshot refuses the skill's malformed posted reading before writing files."""

# phi-scan: synthetic

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

import aar_scan
import course_assignment_scan
import medatrax_posting
import peer_critique_scan


class PostedReadingSnapshot(unittest.TestCase):
    def fixtures(self, root: Path, skill: str, submission: str) -> tuple[Path, Path, Path]:
        run = root / "run"
        run.mkdir()
        (run / "posting-approvals.json").write_text(json.dumps({"items": [{
            "skill": skill, "submission": submission, "grader_args": [str(run)],
        }]}), encoding="utf-8")
        transcript = root / "transcript.jsonl"
        transcript.write_text(json.dumps({
            "type": "user", "uuid": "synthetic-user-1",
            "timestamp": "2026-10-08T12:00:00Z",
            "message": {"content": "That is the wrong section; use the nurse practitioner section."},
            "attributionSkill": skill,
        }) + "\n", encoding="utf-8")
        memory = root / "MEMORY.md"
        memory.write_text("# Synthetic index\n", encoding="utf-8")
        return run, transcript, memory

    def assert_refusal(self, run: Path, transcript: Path, memory: Path, submission: str, message: str) -> None:
        with self.assertRaisesRegex(ValueError, message):
            aar_scan.write_extract(run, transcript, submission, memory)
        self.assertFalse(aar_scan.extract_path(run, submission).exists())
        self.assertFalse(aar_scan.baseline_path(run, submission).exists())

    def test_malformed_visit_refuses_then_corrected_twin_extracts(self):
        with tempfile.TemporaryDirectory() as temporary:
            run, transcript, memory = self.fixtures(Path(temporary), "batch-shift", "synthetic-shift")
            note = run / "note-1.md"
            note.write_text("Synthetic note.\n", encoding="utf-8")
            record = (
                "## REREAD: synthetic-shift\n"
                "POST-URL: https://example.org/patient-visits\n"
                "POSTED: 10/08/2026 12:00\nREAD: 1 of 1 read\n"
                "VERDICT: matches - The saved visit and note form matched.\n"
                f"SUBMISSION-SHA256: {medatrax_posting.source_sha256((note,))}\n"
                "TIME-LOG: not requested\n"
                "VISIT: 1 | patient 1 | reference matched P-17 | patient-detail=/patients/17 | "
                "note-view=/forms/view?resultid=31 | visit-date=10/08/2026 | finished=10/08/2026 12:00 | matches\n"
            )
            reread = run / "reread.md"
            reread.write_text(record.replace("reference matched P-17", "reference missing P-17"), encoding="utf-8")
            self.assert_refusal(run, transcript, memory, "synthetic-shift", "VISIT")
            reread.write_text(record, encoding="utf-8")
            destination, _ = aar_scan.write_extract(run, transcript, "synthetic-shift", memory)
            self.assertTrue(destination.is_file())
            self.assertTrue(aar_scan.baseline_path(run, "synthetic-shift").is_file())

    def test_canvas_legacy_display_refuses_then_corrected_twin_extracts(self):
        with tempfile.TemporaryDirectory() as temporary:
            run, transcript, memory = self.fixtures(Path(temporary), "peer-critique", "critique.md")
            critique = run / "critique.md"
            critique.write_text("Synthetic academic critique.\n", encoding="utf-8")
            record = (
                "## REREAD: critique.md\nPOST-URL: https://example.org/t?entry_id=1\n"
                "POSTED: 2026-10-08\nREAD: 2026-10-08\n"
                f"SUBMISSION-SHA256: {sha256(critique.read_bytes()).hexdigest()}\n"
                "VERDICT: matches - The board text equals the artifact.\n"
                "LEGACY-DISPLAY: expected - Visible text recorded.\n"
            )
            reread = run / "reread.md"
            reread.write_text(record.replace("expected - Visible text recorded.", "maybe"), encoding="utf-8")
            self.assert_refusal(run, transcript, memory, "critique.md", "LEGACY-DISPLAY")
            reread.write_text(record, encoding="utf-8")
            destination, _ = aar_scan.write_extract(run, transcript, "critique.md", memory)
            self.assertTrue(destination.is_file())
            critique.write_text("Changed after posting.\n", encoding="utf-8")
            self.assertEqual([item.code for item in peer_critique_scan.posted_reading_check(run, "critique.md")], ["fingerprint"])

    def test_assignment_checks_complete_carrier_population(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            artifact = run / "synthetic.docx"
            artifact.write_bytes(b"synthetic artifact bytes")
            (run / "submission-gates.json").write_text(json.dumps({
                "approved_carriers": [{"filename": "synthetic.docx"}, {"filename": "supplement.pdf"}],
            }), encoding="utf-8")
            record = (
                "## REREAD: synthetic\n"
                f"SUBMISSION-SHA256: {sha256(artifact.read_bytes()).hexdigest()}\n"
                "VERDICT: matches - Both uploaded files were read.\n"
                "ATTACHMENT-COUNT: 2\nSUBMITTED-FILE: synthetic.docx\nSUBMITTED-FILE: supplement.pdf\n"
            )
            reread = run / "reread.md"
            args = (str(run), "--artifact", str(artifact))
            reread.write_text(record, encoding="utf-8")
            self.assertEqual(course_assignment_scan.posted_reading_check(run, "synthetic", args), ())
            reread.write_text(record.replace("ATTACHMENT-COUNT: 2", "ATTACHMENT-COUNT: 1"), encoding="utf-8")
            self.assertEqual([item.code for item in course_assignment_scan.posted_reading_check(run, "synthetic", args)], ["attachment-count"])
            reread.write_text(record.replace("SUBMITTED-FILE: supplement.pdf\n", ""), encoding="utf-8")
            self.assertEqual([item.code for item in course_assignment_scan.posted_reading_check(run, "synthetic", args)], ["submitted-files"])

    def test_initial_post_saved_locator_refuses_then_corrected_twin_extracts(self):
        with tempfile.TemporaryDirectory() as temporary:
            run, transcript, memory = self.fixtures(Path(temporary), "discussion-post", "draft")
            draft = run / "draft.md"
            draft.write_text("Synthetic initial post.\n", encoding="utf-8")
            html = run / "draft.html"
            html.write_text("<p>Synthetic initial post.</p>\n", encoding="utf-8")
            (run / "posting-approvals.json").write_text(json.dumps({"items": [{
                "skill": "discussion-post", "submission": "draft",
                "grader_args": [str(run), "--draft", str(draft), "--html", str(html)],
            }]}), encoding="utf-8")
            record = (
                "## REREAD: draft\nPOST-URL: https://example.org/t?entry_id=1\n"
                "POSTED: 2026-10-08\nREAD: 2026-10-08\n"
                f"SUBMISSION-SHA256: {sha256(draft.read_bytes()).hexdigest()}\n"
                "VERDICT: matches - The saved post equals the artifact.\n"
                "COMPOSER-OUTCOME: inline\n"
                f"HTML-BYTES: {html.stat().st_size}\n"
            )
            (run / "reread.md").write_text(record, encoding="utf-8")
            post = run / "post.md"
            metadata = "POST-URL: https://example.org/t?entry_id=1\nPOSTED: 2026-10-08\n"
            post.write_text(metadata.replace("entry_id=1", "entry_id=2"), encoding="utf-8")
            self.assert_refusal(run, transcript, memory, "draft", "POST-URL differs")
            post.write_text(metadata, encoding="utf-8")
            destination, _ = aar_scan.write_extract(run, transcript, "draft", memory)
            self.assertTrue(destination.is_file())


if __name__ == "__main__":
    unittest.main()
