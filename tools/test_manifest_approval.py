"""Real manifest approval binds coding/fields while portal evidence binds note bytes."""

import artifact_lock_test_support
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import aar_scan
import approval_record
import medatrax_posting
import reader_remarks
import review_manifest
import uptodate_block
from run_record_reader import UnreadableRecord
from test_approval_record import NOTE
from test_review_manifest import synthetic_run, passing_receipt


class ManifestApproval(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.grader = patch.object(approval_record, "_pre_post_grade", return_value=(0, "clean"))
        self.grader.start()
        self.addCleanup(self.grader.stop)

    def make_run(self, batch):
        run = synthetic_run(self.root / str(batch), batch=batch)
        note = run / "note-1.md"
        note.write_text(NOTE.removesuffix("Coding worksheet\n") +
                        "\n## Medatrax entry fields\nGender: Female\n", encoding="utf-8")
        review_manifest.build(run, run / "inputs.json", batch=batch,
                              constants=dict(course="Synthetic course", preceptor="Synthetic preceptor",
                                             site="Synthetic site") if batch else None)
        passing_receipt(run, batch=batch)
        for source in (note, run / "visible-worksheet-1.md", run / review_manifest.MANIFEST,
                       run / review_manifest.RECEIPT):
            os.utime(source, (1, 1))
        return run, note

    def approve(self, run, note, batch):
        skill = "batch-shift" if batch else "clinical-note"
        args = dict(skill=skill, submission="synthetic", sources=(note,), grader_args=(str(run),))
        prepared = approval_record.prepare(run, **args)
        stamp = time.time() + 10
        row = lambda role, text, at: {"type": role, "timestamp": datetime.fromtimestamp(at, timezone.utc).isoformat(),
                                      "message": {"content": text}}
        transcript = run / "session.jsonl"
        transcript.write_text("\n".join(json.dumps(value) for value in (
            row("assistant", uptodate_block.render(run, (note,)) + "\n" + "\n".join(prepared.coverage), stamp),
            row("user", "Approved.", stamp + 1))) + "\n", encoding="utf-8")
        with patch.object(aar_scan, "discover_transcripts", return_value=aar_scan.TranscriptDiscovery((transcript,), 1, 0, 0, 1)):
            return approval_record.approve(run, **args, content_approved=True, clinician_reply="Approved.")

    def test_both_skills_bind_json_and_reject_code_and_field_changes(self):
        for batch in (False, True):
            with self.subTest(batch=batch):
                run, note = self.make_run(batch)
                approved = self.approve(run, note, batch)
                self.assertEqual((run / review_manifest.MANIFEST, run / review_manifest.RECEIPT), approved.sources)
                item = json.loads((run / approval_record.RECORD).read_text())["items"][0]
                self.assertEqual([str(note)], item["note_sources"])
                self.assertTrue(item["clinical_manifest_binding"])
                if not batch:
                    (run / "another.md").write_text("Unrelated Markdown.")
                    self.assertEqual((note,), medatrax_posting.note_paths(run, batch=False))
                skill = approved.skill
                for path, before, after in ((run / "visible-worksheet-1.md", "R05.9", "I10"),
                                             (note, "Female", "Male")):
                    old = path.read_bytes()
                    path.write_bytes(old.replace(before.encode(), after.encode()))
                    with self.assertRaises(approval_record.ApprovalRecordError):
                        approval_record.record_agent_posting(run, skill=skill, submission="synthetic")
                    path.write_bytes(old)
                # Re-rendering itself never enters the approved source population.
                with patch("docx_write.write_docx", return_value=self.root / "review.docx"):
                    if batch:
                        review_manifest.render(run, self.root / "review.docx")
                approval_record.record_agent_posting(run, skill=skill, submission="synthetic")

    def test_portal_join_keeps_raw_note_digest_after_layout_whitespace_edit(self):
        run, note = self.make_run(False)
        approved = self.approve(run, note, False)
        note.write_text(note.read_text().replace("Subjective.", "Subjective.  "), encoding="utf-8")
        approval_record.record_agent_posting(run, skill=approved.skill, submission="synthetic")
        actual = medatrax_posting.source_sha256((note,))
        (run / "reread.md").write_text(
            "## REREAD: synthetic\nPOST-URL: https://example.test/visit\nPOSTED: 2026-10-01 10:00\n"
            "READ: 2026-10-01\n" + f"SUBMISSION-SHA256: {actual}\n"
            "VERDICT: matches - saved note matches\n", encoding="utf-8")
        self.assertNotEqual(actual, approved.sha256)
        failed, report = approval_record.completion_gate(run, approved.skill, "synthetic")
        self.assertFalse(failed, report)

    def test_latest_worksheet_change_starts_reply_and_prepare_window(self):
        run, note = self.make_run(False)
        future = time.time() + 100
        os.utime(run / "visible-worksheet-1.md", (future, future))
        with self.assertRaisesRegex(approval_record.ApprovalRecordError, "reply was not found"):
            self.approve(run, note, False)

    def test_missing_manifest_never_accepts_raw_note_approval(self):
        run, note = self.make_run(False)
        (run / review_manifest.MANIFEST).unlink()
        with self.assertRaises(approval_record.ApprovalRecordError):
            approval_record.prepare(run, skill="clinical-note", submission="synthetic",
                                    sources=(note,), grader_args=(str(run),))

    def test_damaged_receipt_refuses_render_and_both_approval_skills(self):
        for batch in (False, True):
            with self.subTest(batch=batch):
                run, note = self.make_run(batch)
                path = run / review_manifest.RECEIPT
                receipt = json.loads(path.read_text())
                receipt["sources"] = {}
                path.write_text(json.dumps(receipt), encoding="utf-8")
                before = path.read_bytes()
                with self.assertRaises(UnreadableRecord):
                    approval_record.prepare(run, skill="batch-shift" if batch else "clinical-note",
                                            submission="synthetic", sources=(note,), grader_args=(str(run),))
                if batch:
                    with self.assertRaises(UnreadableRecord):
                        review_manifest.render(run, self.root / "review.docx")
                self.assertEqual(before, path.read_bytes())
                self.assertFalse((run / approval_record.RECORD).exists())


if __name__ == "__main__":
    unittest.main()
