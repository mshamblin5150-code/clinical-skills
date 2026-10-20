"""Coding record remarks, retry retention, and the public clinical approval. #1702."""
# phi-scan: synthetic
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import time
import unittest
from unittest import mock

from code_set_database_test_support import (
    ICD10_DATABASE_SHA256,
    PROCEDURE_CODES_DATABASE_SHA256,
    assert_code_set_database_digest,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
assert_code_set_database_digest(
    REPO_ROOT / "reference" / "icd10cm-2026.sqlite",
    ICD10_DATABASE_SHA256,
    "ICD-10-CM Code-set database",
)
assert_code_set_database_digest(
    REPO_ROOT / "reference" / "procedure-codes-2026.sqlite",
    PROCEDURE_CODES_DATABASE_SHA256,
    "procedure-code Code-set database",
)

import aar_scan
import approval_record as approvals
import completion_checks
import reader_remarks as remarks
import test_anchor_scan as agreement_tests
import test_specificity_scan as specificity_tests
from test_approval_record import NOTE


class CodingRecordRemarks(unittest.TestCase):
    def setUp(self):
        self.agreement = agreement_tests.AgreementModes("runTest")
        self.agreement.setUp()
        self.addCleanup(self.agreement.doCleanups)
        self.addCleanup(self.agreement.tearDown)

    def test_agreement_remark_is_reported_privately_and_column_ground_is_expected(self):
        record = self.agreement.clean_record()
        record["pairs"][0]["remarks"] = ["R12: Clarify the stated route."]
        record["pairs"][0]["codes"][0]["column_ground"] = "none"
        status, report = self.agreement.grade(record, show=True)
        self.assertEqual(status, 0, report)
        self.assertIn("Clarify the stated route.", report)
        self.assertEqual(1, len(remarks.read_report(report)))
        self.assertNotIn("Clarify the stated route.", self.agreement.grade(record)[1])

    def test_each_unexpected_agreement_key_is_unread_at_its_own_level(self):
        for level in ("file", "note", "code"):
            record = self.agreement.clean_record()
            target = {"file": record, "note": record["pairs"][0], "code": record["pairs"][0]["codes"][0]}[level]
            target["unrecognized"] = "Outside problem."
            status, report = self.agreement.grade(record)
            self.assertEqual(status, 2, report)
            self.assertIn("unexpected agreement keys                 1", report)
            self.assertIn("unread agreement record: file 1 of 1", report)
            self.assertEqual(1, report.splitlines().count("unread remainder 1"))

    def test_writer_has_no_remark_field_and_free_text_remains_a_limit(self):
        record = self.agreement.clean_record()
        record["pairs"][0]["remarks"] = ["An outside problem."]
        path = Path(self.agreement.raw.name) / "agreement-self" / "case-01.json"
        path.parent.mkdir()
        path.write_text(json.dumps(record), encoding="utf-8")
        pairs, unread, _ = agreement_tests.scan._pair_agreement_sources(self.agreement.worksheets, self.agreement.notes, {})
        result = agreement_tests.scan._grade_agreement(pairs, unread, [path])
        self.assertEqual(1, result.unexpected_keys)
        self.assertEqual((), result.remarks)
        record["pairs"][0].pop("remarks")
        record["pairs"][0]["codes"][0]["threshold"] = "Outside problem hidden in ordinary evidence."
        self.assertEqual(0, self.agreement.grade(record)[0])

    def test_specificity_remarks_and_each_unexpected_nested_key_use_public_command(self):
        fixture = specificity_tests.TheCommandGradesTheSeparatedRead("runTest")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for level in (None, "file", "code", "family", "note"):
            value = fixture._record()
            value["remarks"] = ["Z90.49: Clarify the secondary source."]
            if level is not None:
                subject = value["codes"][0]
                fact = next(row for row in subject["family"] if row["notes"])
                target = {"file": value, "code": subject, "family": fact, "note": fact["notes"][0]}[level]
                target["unrecognized"] = "Outside problem."
            fixture._write(value)
            status, report, errors = fixture._run("--second-read", str(fixture.read_path), "--show")
            self.assertEqual(status, 0 if level is None else 2, report + errors)
            self.assertIn("Clarify the secondary source.", report)
            self.assertEqual(1, len([line for line in report.splitlines() if line.startswith("unread remainder ")]))
            if level:
                self.assertIn("unread specificity reader record: file 1 of 1", errors)

    def test_replacement_preserves_both_reader_kinds_without_a_prepare_receipt(self):
        agreement = self.agreement.clean_record()
        agreement["pairs"][0]["remarks"] = ["R12: Retain this outside problem."]
        specific = specificity_tests.second_read(specificity_tests.read_code("R12", family=specificity_tests.release_family("R12")))
        specific["remarks"] = ["R12: Retain the family question."]
        for kind, value in (("agreement", agreement), ("specificity", specific)):
            path = Path(self.agreement.raw.name) / f"{kind}.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            replacement = json.loads(json.dumps(value))
            destination = replacement["pairs"][0] if kind == "agreement" else replacement
            destination["remarks"] = ["R12: A new retry remark."]
            remarks.replace_coding_record(path, replacement, kind=kind)
            retained = json.loads(path.read_text(encoding="utf-8"))
            retained = retained["pairs"][0] if kind == "agreement" else retained
            self.assertEqual(2, len(retained["remarks"]))
            self.assertIn("Retain", retained["remarks"][0])

    def test_dated_key_checks_start_at_the_exact_boundary(self):
        record = self.agreement.clean_record()
        record["extra"] = "Outside problem."
        path = Path(self.agreement.raw.name) / "read.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        pairs, unread, _ = agreement_tests.scan._pair_agreement_sources(self.agreement.worksheets, self.agreement.notes, {})
        cutoff = completion_checks.registry()["anchor_scan:unexpected-reader-keys"][0]
        for moment, expected in ((cutoff - timedelta(microseconds=1), 0), (cutoff, 1)):
            token = completion_checks.MOMENTS.set({"approval": moment})
            try:
                self.assertEqual(expected, agreement_tests.scan._grade_agreement(pairs, unread, [path]).unexpected_keys)
            finally:
                completion_checks.MOMENTS.reset(token)

    def test_a_damaged_retry_source_is_never_replaced_as_empty(self):
        path = Path(self.agreement.raw.name) / "read.json"
        path.write_bytes(b'{')
        with self.assertRaises(ValueError):
            remarks.replace_coding_record(path, self.agreement.clean_record(), kind="agreement")
        self.assertEqual(b'{', path.read_bytes())


class ClinicalCodingRemarks(unittest.TestCase):
    def setUp(self):
        self.fixture = agreement_tests.AgreementModes("runTest")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.addCleanup(self.fixture.tearDown)
        self.run = Path(self.fixture.raw.name)
        self.note = self.fixture.notes / "case-01.md"
        record = self.fixture.clean_record()
        record["pairs"][0]["remarks"] = ["R12: Clarify the stated route."]
        self.record = self.run / "agreement-reader" / "read.json"
        self.record.parent.mkdir()
        self.record.write_text(json.dumps(record), encoding="utf-8")
        assessment = self.note.read_text(encoding="utf-8").replace("## A:", "")
        self.note.write_text(NOTE.replace("Assessment.", assessment), encoding="utf-8")
        os.utime(self.note, (1, 1))
        self.transcript = self.run / "session.jsonl"
        self.patch = mock.patch.object(approvals, "_pre_post_grade", return_value=(0, "paired grade clean\nunread remainder 0"))
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.discovery = mock.patch.object(aar_scan, "discover_transcripts", return_value=aar_scan.TranscriptDiscovery((self.transcript,), 1, 0, 0, 1)).start()
        self.addCleanup(mock.patch.stopall)

    def arguments(self, skill="clinical-note"):
        return dict(skill=skill, submission="synthetic-note", sources=(self.note,), grader_args=(str(self.run),))

    def show(self, text, reply="Approved.", *, delegate=False):
        import uptodate_block
        now = time.time() + 10
        def row(role, content, at):
            return {"type": role, "timestamp": datetime.fromtimestamp(at, timezone.utc).isoformat(), "message": {"content": content}}
        rows = [row("assistant", uptodate_block.render(self.run, (self.note,)) + "\n" + text, now)]
        rows.append(row("assistant" if delegate else "user", reply, now + 1))
        self.transcript.write_text("\n".join(json.dumps(value) for value in rows) + "\n", encoding="utf-8")

    def approve(self, reply="Approved.", outcomes=(), skill="clinical-note"):
        return approvals.approve(self.run, **self.arguments(skill), content_approved=True,
                                 clinician_reply=reply, remark_outcomes=outcomes)

    def test_each_reader_kind_reaches_both_clinical_approvals_and_the_durable_record(self):
        specific = specificity_tests.second_read(specificity_tests.read_code("R12", family=specificity_tests.release_family("R12")))
        specific["remarks"] = ["R12: Clarify the secondary source."]
        specific_path = self.run / "specificity-reader" / "read.json"
        specific_path.parent.mkdir()
        specific_path.write_text(json.dumps(specific), encoding="utf-8")
        for skill in sorted(approvals.CLINICAL_SKILLS):
            (self.run / approvals.RECORD).unlink(missing_ok=True)
            prepared = approvals.prepare(self.run, **self.arguments(skill))
            self.assertEqual(2, len(prepared.remarks))
            outcomes = tuple(remarks.Outcome("fixed", "The stated source was clarified.") for _ in prepared.remarks)
            self.show(remarks.surface(prepared, outcomes, clinical=True))
            self.discovery.reset_mock()
            with mock.patch.object(approvals.project_context, "go_ahead", side_effect=AssertionError("coursework only")):
                self.approve(outcomes=outcomes, skill=skill)
            self.discovery.assert_called_once()
            item = json.loads((self.run / approvals.RECORD).read_text(encoding="utf-8"))["items"][0]
            self.assertEqual(2, len(item["reader_remarks"]))
            self.assertFalse(item["project_context_check"])

    def test_missing_block_unanswered_leave_and_delegated_leave_refuse(self):
        prepared = approvals.prepare(self.run, **self.arguments())
        outcomes = (remarks.Outcome("leave", "Keep the stated route for this exercise."),)
        self.show("\n".join(prepared.coverage))
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "not shown"):
            self.approve(outcomes=outcomes)
        self.show(remarks.surface(prepared, outcomes, clinical=True))
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "unanswered leave.*1"):
            self.approve(outcomes=outcomes)
        self.show(remarks.surface(prepared, outcomes, clinical=True), "Approved; leave 1.", delegate=True)
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "reply was not found"):
            self.approve("Approved; leave 1.", outcomes)
        self.show(remarks.surface(prepared, outcomes, clinical=True), "Approved; leave 1.")
        self.approve("Approved; leave 1.", outcomes)
        item = json.loads((self.run / approvals.RECORD).read_text(encoding="utf-8"))["items"][0]
        self.assertEqual("left on clinician's word", item["reader_remarks"][0]["outcome"])

    def test_damaged_records_refuse_preparation_and_late_changes_refuse_approval(self):
        original = self.record.read_bytes()
        for damaged in (b'{', b'[]', b'\xff'):
            self.record.write_bytes(damaged)
            with self.assertRaisesRegex(approvals.ApprovalRecordError, "coding reader record is unreadable"):
                approvals.prepare(self.run, **self.arguments())
        self.record.write_bytes(original)
        prepared = approvals.prepare(self.run, **self.arguments())
        outcomes = (remarks.Outcome("fixed", "The stated source was clarified."),)
        self.show(remarks.surface(prepared, outcomes, clinical=True))
        record = json.loads(original)
        record["pairs"][0]["remarks"].append("R12: A late reader remark.")
        self.record.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaisesRegex(approvals.ApprovalRecordError, "prepared grade or source changed"):
            self.approve(outcomes=outcomes)

    def test_check_generated_column_ground_reaches_the_public_approval(self):
        words = "took too many acetaminophen tablets"
        route = "Acetaminophen > Poisoning Accidental (unintentional) -> code T39.1X1"
        self.assertEqual(0, self.fixture.drug_read(words, "T39.1X1A", route, ground=words)[0])
        assessment = self.note.read_text(encoding="utf-8")
        self.note.write_text(NOTE.replace("Assessment.", assessment), encoding="utf-8")
        os.utime(self.note, (1, 1))
        self.record.write_bytes((self.run / "agreement-read.json").read_bytes())
        prepared = approvals.prepare(self.run, **self.arguments())
        self.assertEqual(1, len(prepared.remarks))
        self.assertIn("T39.1X1A", prepared.remarks[0].text)
        self.assertIn(words, prepared.remarks[0].text)
        outcomes = (remarks.Outcome("fixed", "The quoted ground is retained beside the code."),)
        self.show(remarks.surface(prepared, outcomes, clinical=True))
        self.approve(outcomes=outcomes)
        item = json.loads((self.run / approvals.RECORD).read_text(encoding="utf-8"))["items"][0]
        self.assertIn(words, item["reader_remarks"][0]["text"])

    def test_historical_approval_is_exempt_until_the_exact_new_gate_start(self):
        self.record.write_bytes(b'{')
        cutoff = completion_checks.registry()["reader_remarks:clinical-go-ahead"][0]
        token = completion_checks.MOMENTS.set({"approval": cutoff - timedelta(microseconds=1)})
        try:
            prepared = approvals.prepare(self.run, **self.arguments())
            self.show("\n".join(prepared.coverage))
            self.approve()
        finally:
            completion_checks.MOMENTS.reset(token)
        token = completion_checks.MOMENTS.set({"approval": cutoff})
        try:
            with self.assertRaisesRegex(approvals.ApprovalRecordError, "coding reader record is unreadable"):
                approvals.prepare(self.run, **self.arguments())
        finally:
            completion_checks.MOMENTS.reset(token)


if __name__ == "__main__":
    unittest.main()
