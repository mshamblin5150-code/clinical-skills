"""Synthetic checks for the pre-approval answers record."""
# phi-scan: synthetic
from __future__ import annotations

import artifact_lock_test_support

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import approval_record
import preapproval_answers
from prose_bind import bind, NAMING
from test_review_manifest import synthetic_run

REFERENCE = Path(__file__).resolve().parent.parent / "skills" / "_shared" / "reference" / "em-elements.md"
QUESTION = "Did you evaluate or treat the synthetic hypertension this visit? 99203 now; 99204 if yes."
REPLY = "Synthetic reply: yes, I adjusted the dose."
VERIFIED = approval_record.ReplyVerification("verified", "synthetic reply", 4102444800.0)
NOT_FOUND = approval_record.ReplyVerification("not found", "no later whole clinician message matches")


class AnswersRecord(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run = synthetic_run(Path(self.temporary.name))
        self.path = self.run / preapproval_answers.RECORD

    def main(self, *args, verification=VERIFIED):
        output = io.StringIO()
        with mock.patch.object(approval_record, "verify_clinician_reply", return_value=verification), \
                contextlib.redirect_stdout(output):
            status = preapproval_answers.main([str(self.run), *map(str, args)])
        return status, output.getvalue()

    def test_a_verified_reply_is_recorded_once_with_its_id_and_levels(self):
        status, output = self.main("--note", 1, "--question", QUESTION, "--level", "99203", "--level", "99204",
                                   "--reply", REPLY)
        self.assertEqual(0, status, output)
        self.assertEqual("pre-approval answers: note-1.q1 recorded; reply check verified\n", output)
        self.main("--note", 1, "--question", QUESTION, "--level", "99203", "--level", "99204", "--reply", REPLY)
        self.main("--note", 1, "--question", "A second synthetic question with no level.", "--reply", REPLY)
        record = preapproval_answers.read(self.run)
        self.assertEqual(["note-1.q1", "note-1.q2"], [entry["id"] for entry in record["answers"]])
        first = record["answers"][0]
        self.assertEqual((QUESTION, REPLY, ["99203", "99204"], "verified", 4102444800.0),
                         (first["question"], first["clinician_reply"], first["levels"], first["verification"],
                          first["reply_matched_at"]))
        self.assertEqual([], record["answers"][1]["levels"])

    def test_h2_a_missing_opener_source_refuses_and_writes_nothing(self):
        # Thirteenth review: only an unreadable transcript may make an unreadable entry.
        import encounter_openers
        openers = encounter_openers.read_openers(self.run)
        source = Path(openers["source"])
        # The source is gone after the opener record was read: its time cannot be read, and that is
        # not an unreadable transcript.
        moved = dict(openers, source=str(source.with_name("moved-away.txt")))
        with mock.patch.object(preapproval_answers, "read_openers", return_value=moved), \
                self.assertRaises(ValueError):
            preapproval_answers.record(self.run, 1, QUESTION, [], "Synthetic reply never sent.")
        self.assertFalse(self.path.exists())
        source.unlink()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = preapproval_answers.main([str(self.run), "--note", "1", "--question", QUESTION,
                                               "--reply", "Synthetic reply never sent."])
        self.assertEqual(2, status, output.getvalue())
        self.assertFalse(self.path.exists())

    def test_an_unreadable_transcript_is_recorded_as_such(self):
        identifier, state = preapproval_answers.record(self.run, 1, QUESTION, [], REPLY)
        self.assertEqual(("note-1.q1", "unreadable"), (identifier, state))
        self.assertIsNone(preapproval_answers.read(self.run)["answers"][0]["reply_matched_at"])

    def test_nothing_is_recorded_without_a_matching_whole_reply_a_known_note_or_valid_levels(self):
        for args, verification in ((("--note", 1), NOT_FOUND), (("--note", 2), VERIFIED),
                                   (("--note", 1, "--level", "9921"), VERIFIED)):
            with self.subTest(args=args):
                status, output = self.main(*args, "--question", QUESTION, "--reply", REPLY, verification=verification)
                self.assertEqual(2, status, output)
                self.assertNotIn(REPLY, output)
                self.assertFalse(self.path.exists())

    def test_a_malformed_record_is_refused_rather_than_partly_read(self):
        self.main("--note", 1, "--question", QUESTION, "--reply", REPLY)
        value = json.loads(self.path.read_text(encoding="utf-8"))
        value["answers"].append(dict(value["answers"][0]))
        for text in (json.dumps(value), "{\"schema\": 1, \"producer\": \"preapproval_answers\"}", "not json"):
            with self.subTest(text=text[:20]):
                self.path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    preapproval_answers.read(self.run)

    def test_f7_an_unreadable_entry_is_upgraded_once_verified_and_never_downgraded(self):
        self.assertEqual("unreadable", preapproval_answers.record(self.run, 1, QUESTION, [], REPLY)[1])
        status, output = self.main("--note", 1, "--question", QUESTION, "--reply", REPLY)
        self.assertEqual("pre-approval answers: note-1.q1 recorded; reply check verified\n", output)
        entries = preapproval_answers.read(self.run)["answers"]
        self.assertEqual([("note-1.q1", "verified", 4102444800.0)],
                         [(entry["id"], entry["verification"], entry["reply_matched_at"]) for entry in entries])
        before = self.path.read_bytes()
        self.assertEqual(("note-1.q1", "verified"), preapproval_answers.record(self.run, 1, QUESTION, [], REPLY))
        self.main("--note", 1, "--question", QUESTION, "--reply", REPLY)
        self.assertEqual(before, self.path.read_bytes())

    def test_r7_levels_in_another_order_are_the_same_answer(self):
        preapproval_answers.record(self.run, 1, QUESTION, ["99203", "99204"], REPLY)
        self.main("--note", 1, "--question", QUESTION, "--level", "99204", "--level", "99203", "--reply", REPLY)
        entries = preapproval_answers.read(self.run)["answers"]
        self.assertEqual([("note-1.q1", "verified")], [(entry["id"], entry["verification"]) for entry in entries])

    def test_t7_a_delegated_run_records_nothing(self):
        import delegated_answers
        (self.run / delegated_answers.RECORD).write_text("## QUESTION: synthetic delegated question\n", encoding="utf-8")
        status, output = self.main("--note", 1, "--question", QUESTION, "--reply", REPLY)
        self.assertEqual(2, status, output)
        self.assertIn("delegated", output)
        self.assertNotIn(REPLY, output)
        self.assertFalse(self.path.exists())

    def test_declared_limits_are_named_by_the_reference_and_not_copied(self):
        self.assertEqual((), bind(preapproval_answers.DECLARED_LIMITS, REFERENCE.read_text(encoding="utf-8"),
                                  mode=NAMING))


if __name__ == "__main__":
    unittest.main()
