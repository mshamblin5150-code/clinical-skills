"""ADR 0408 disclosure through its public command and clinical approval seam."""
from __future__ import annotations

import artifact_lock_test_support
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import aar_scan
import approval_record
import outbound_search
import uptodate_block
from test_approval_record import NOTE
from prose_bind import NAMING, bind


EMPTY = "UPTODATE CONFLICTS: none\nUPTODATE FAILED PULLS: none\nUPTODATE MISMATCHED SEARCHES: none\n"


class Disclosure(unittest.TestCase):
    def test_limits_are_named_without_copying_them(self):
        text = (Path(__file__).resolve().parents[1] / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual((), bind(uptodate_block.DECLARED_LIMITS, text, mode=NAMING))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name)
        self.note = self.run / "note-1.md"
        self.note.write_text(NOTE, encoding="utf-8")
        os.utime(self.note, (1, 1))

    def block(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            status = uptodate_block.main(["--run", str(self.run), "--notes", str(self.note)])
        return status, out.getvalue()

    def test_empty_and_failed_gap_pull_without_note_mark(self):
        self.assertEqual((0, EMPTY), self.block())
        (self.run / outbound_search.SEARCHES).write_text(json.dumps({"search_id": "gap", "query": "cough", "passed": True}) + "\n")
        (self.run / outbound_search.PULLS).write_text(json.dumps({"search_id": "gap", "outcome": "failed", "decision": "antibiotic choice", "instrument": "browser reader"}) + "\n")
        status, text = self.block()
        self.assertEqual(0, status)
        self.assertIn("UPTODATE FAILED PULLS: 1\n- gap | antibiotic choice | browser reader", text)

    def test_conflict_requires_the_same_sheet_row_and_dump(self):
        self.note.write_text(NOTE + "\nFILLED·proposed 1. Treatment [uptodate over thresholds/hypertension aha-2025: Hypertension, updated October 2026, live-a]\n", encoding="utf-8")
        (self.run / outbound_search.SEARCHES).write_text(json.dumps({"search_id": "conflict", "query": "hypertension", "passed": True}) + "\n")
        pull = {"search_id": "conflict", "dump_id": "live-a", "sheet": "hypertension", "row": "aha-2025", "difference": "threshold 130 versus 140"}
        path = self.run / outbound_search.PULLS
        path.write_text(json.dumps(pull) + "\n")
        self.assertIn("threshold 130 versus 140", self.block()[1])
        for key in ("sheet", "row", "dump_id"):
            path.write_text(json.dumps({**pull, key: "wrong"}) + "\n")
            self.assertEqual(2, self.block()[0])

    def test_unreadable_private_log_does_not_emit_a_partial_block(self):
        (self.run / outbound_search.PULLS).write_text('{"search_id":', encoding="utf-8")
        self.assertEqual((2, ""), self.block())

    def test_wrong_shape_search_record_cannot_disappear_from_the_population(self):
        for row in ({}, {"search_id": "lost", "passed": True},
                    {"query": "cough", "passed": True}):
            with self.subTest(row=row):
                (self.run / outbound_search.SEARCHES).write_text(json.dumps(row) + "\n")
                self.assertEqual((2, ""), self.block())

    def test_unterminated_failed_pull_tail_is_unread_not_an_empty_population(self):
        self.note.write_text(NOTE + "\nFILLED [thresholds/hypertension aha-2025; uptodate pull failed\n", encoding="utf-8")
        self.assertEqual((2, ""), self.block())

    def test_mismatched_search_displays_whether_sent_words_passed_identifier_check(self):
        (self.run / outbound_search.SEARCHES).write_text(json.dumps({"search_id": "search-a", "passed": True, "query": "cough"}) + "\n")
        for passed in (True, False):
            (self.run / outbound_search.PULLS).write_text(json.dumps({"search_id": "search-a", "outcome": "mismatched", "query_readback": "cough stray", "sent_query_passed": passed}) + "\n")
            status, text = self.block()
            self.assertEqual(0, status)
            self.assertIn("sent-query identifier check: " + ("passed" if passed else "refused"), text)

    def test_shown_block_cannot_grow_extra_details(self):
        self.assertFalse(uptodate_block.shown_matches(EMPTY + "- invented detail\n", EMPTY))

    def test_approval_refuses_missing_line_wrong_count_and_wrong_detail(self):
        for skill in ("clinical-note", "batch-shift"):
            for block in (EMPTY, EMPTY.replace("UPTODATE FAILED PULLS: none\n", ""),
                          EMPTY.replace("CONFLICTS: none", "CONFLICTS: 1"),
                          EMPTY.replace("FAILED PULLS: none", "FAILED PULLS: wrong")):
                with self.subTest(skill=skill, block=block):
                    (self.run / approval_record.RECORD).unlink(missing_ok=True)
                    transcript = self.run / "session.jsonl"
                    transcript.write_text("\n".join(json.dumps(row) for row in (
                        {"type": "assistant", "timestamp": "2100-01-01T10:00:00Z", "message": {"content": block}},
                        {"type": "user", "timestamp": "2100-01-01T11:00:00Z", "message": {"content": "Approved."}},
                    )) + "\n", encoding="utf-8")
                    with mock.patch.object(aar_scan, "discover_transcripts", return_value=aar_scan.TranscriptDiscovery((transcript,), 1, 0, 0, 1)), mock.patch.object(approval_record, "_pre_post_grade", return_value=(0, "clean")):
                        approval_record.prepare(self.run, skill=skill, submission="shift",
                            sources=(self.note,), grader_args=(str(self.run),))
                        def approve():
                            return approval_record.approve(self.run, skill=skill, submission="shift", sources=(self.note,), grader_args=(str(self.run),), content_approved=True, clinician_reply="Approved.")
                        if block == EMPTY:
                            approve()
                        else:
                            with self.assertRaisesRegex(approval_record.ApprovalRecordError, "UpToDate"):
                                approve()

    def test_unreadable_transcript_records_incomplete_approval(self):
        with mock.patch.object(approval_record, "_main_transcripts", return_value=([], True)), mock.patch.object(approval_record, "_pre_post_grade", return_value=(0, "clean")):
            approval_record.prepare(self.run, skill="clinical-note", submission="note",
                sources=(self.note,), grader_args=(str(self.run),))
            approval_record.approve(self.run, skill="clinical-note", submission="note", sources=(self.note,),
                grader_args=(str(self.run),), content_approved=True, clinician_reply="Approved.")
        item = json.loads((self.run / approval_record.RECORD).read_text())["items"][0]
        self.assertEqual("incomplete", item["pregrade_status"])
        self.assertEqual("unreadable", item["shown_text_verification"])

    def test_disclosure_must_be_after_sources_and_before_reply_in_codex_chat(self):
        transcript = self.run / "session.jsonl"
        for timestamp, expected in (("1970-01-01T00:00:00Z", "not found"),
                                    ("2100-01-01T10:00:00Z", "verified"),
                                    ("2100-01-01T12:00:00Z", "not found")):
            with self.subTest(timestamp=timestamp):
                transcript.write_text(json.dumps({"type": "response_item", "timestamp": timestamp,
                    "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": EMPTY}]}}) + "\n")
                with mock.patch.object(aar_scan, "discover_transcripts", return_value=aar_scan.TranscriptDiscovery((transcript,), 1, 0, 0, 1)):
                    from datetime import datetime
                    result = approval_record.verify_uptodate_block(self.run, (self.note,), datetime.fromisoformat("2100-01-01T11:00:00+00:00").timestamp())
                    self.assertEqual(expected, result.state)

    def test_internal_codex_analysis_is_not_a_shown_disclosure(self):
        transcript = self.run / "session.jsonl"
        transcript.write_text(json.dumps({"type": "response_item", "timestamp": "2100-01-01T10:00:00Z",
            "payload": {"type": "message", "role": "assistant", "channel": "analysis",
                        "content": [{"type": "output_text", "text": EMPTY}]}}) + "\n")
        with mock.patch.object(aar_scan, "discover_transcripts", return_value=aar_scan.TranscriptDiscovery((transcript,), 1, 0, 0, 1)):
            from datetime import datetime
            result = approval_record.verify_uptodate_block(self.run, (self.note,), datetime.fromisoformat("2100-01-01T11:00:00+00:00").timestamp())
            self.assertEqual("not found", result.state)


if __name__ == "__main__":
    unittest.main()
