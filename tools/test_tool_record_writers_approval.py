"""Native approval-family locked writer controls; synthetic records only."""
# phi-scan: synthetic
import artifact_lock_test_support
import artifact_lock
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import approval_record
import assignment_submission
import reader_remarks
import run_record_reader as records
import test_approval_record as approval_fixtures
import test_assignment_submission as submission_fixtures


class ApprovalFamilyWriters(unittest.TestCase):
    ROUTES = ("approve", "agent-post", "clinician-post", "stage", "confirm",
              "clinician-upload", "prepare", "agreement", "specificity")

    def test_prepare_directory_failure_is_classified_and_preserves_receipt(self):
        with self.command_case('prepare') as (path, call):
            before = path.read_bytes()
            original_mkdir = Path.mkdir
            def denied(directory, *args, **kwargs):
                if directory == path.parent:
                    raise OSError('PRIVATE-DIRECTORY-FAILURE')
                return original_mkdir(directory, *args, **kwargs)
            with mock.patch.object(Path, 'mkdir', denied):
                with self.assertRaises(records.UnreadableRecord) as caught:
                    call()
            self.assertEqual(path, caught.exception.path)
            self.assertIn('could not be opened', str(caught.exception))
            self.assertNotIn('PRIVATE-DIRECTORY-FAILURE', str(caught.exception))
            self.assertEqual(before, path.read_bytes())

    def approve(self, fixture, key="first"):
        return approval_record.approve(
            fixture.run, skill="discussion-post", submission=key,
            sources=(fixture.artifact,), grader_args=(str(fixture.run),),
            content_approved=True, clinician_reply="Approve this entire post.")

    @contextmanager
    def approval_case(self):
        fixture = approval_fixtures.ApprovalRecordContract("runTest")
        fixture.setUp()
        try:
            with mock.patch.object(approval_record, "_pre_post_grade", return_value=(0, "grade clean")):
                self.approve(fixture)
                yield fixture
        finally:
            fixture.doCleanups()
            fixture.tearDown()

    @contextmanager
    def command_case(self, kind):
        if kind in {"approve", "agent-post", "clinician-post"}:
            with self.approval_case() as fixture:
                if kind == "approve":
                    fixture.transcript.unlink()  # The existing incomplete-reply route remains usable.
                    call = lambda: self.approve(fixture)
                else:
                    writer = (approval_record.record_agent_posting if kind == "agent-post"
                              else approval_record.record_clinician_posting)
                    call = lambda: writer(fixture.run, skill="discussion-post", submission="first")
                yield fixture.run / approval_record.RECORD, call
            return
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory).resolve()
            source = run / "artifact.docx"
            source.write_bytes(b"synthetic artifact")
            if kind in {"stage", "confirm", "clinician-upload"}:
                fixture = submission_fixtures.TwoGateUpload("runTest")
                verified = approval_record.ReplyVerification("verified", "synthetic Gate 2", 4102444801)
                with mock.patch.object(assignment_submission, "_pre_upload_grade", return_value=(True, "grade clean")), \
                     mock.patch.object(approval_record, "verify_clinician_reply", return_value=verified), \
                     mock.patch.object(reader_remarks, "verify", return_value=[]):
                    staged = fixture.stage(run, source, artifact_approved=True)
                    if kind == "stage":
                        call = lambda: fixture.stage(run, source, artifact_approved=True)
                    elif kind == "confirm":
                        call = lambda: assignment_submission.confirm(
                            staged, uploaded_carriers=(source,), clinician_reply="Submit the synthetic artifact.")
                    else:
                        call = lambda: assignment_submission.record_clinician_upload(
                            run, source, uploaded_carriers=(source,))
                    yield run / assignment_submission.RECORD, call
            elif kind == "prepare":
                reader_remarks.prepare(run, "discussion-post", "first", (source,), "grade clean")
                yield reader_remarks._receipt_path(run, "discussion-post", "first"), lambda: reader_remarks.prepare(
                    run, "discussion-post", "first", (source,), "changed grade")
            else:
                path = run / "reader.json"
                if kind == "agreement":
                    value = {"pairs": [{"stem": "note", "codes": [], "remarks": ["Retain the earlier remark."]}]}
                    replacement = {"pairs": [{"stem": "note", "codes": [], "remarks": ["Retain the new remark."]}]}
                else:
                    value = {"read_on": "2026-10-20", "codes": []}
                    replacement = {"read_on": "2026-10-21", "codes": []}
                path.write_text(json.dumps(value), encoding="utf-8")
                yield path, lambda: reader_remarks.replace_coding_record(path, replacement, kind=kind)

    def test_every_native_writer_refuses_a_held_record_before_changing_bytes(self):
        for kind in self.ROUTES:
            with self.subTest(route=kind), self.command_case(kind) as (path, call):
                before = path.read_bytes()
                with artifact_lock.hold(path, "synthetic competing writer"):
                    with self.assertRaisesRegex(records.UnreadableRecord, "held by another task"):
                        call()
                self.assertEqual(before, path.read_bytes())

    def test_pre_replace_failure_keeps_every_native_record_and_removes_partial(self):
        replace = records.os.replace
        for kind in self.ROUTES:
            with self.subTest(route=kind), self.command_case(kind) as (path, call):
                before = path.read_bytes()
                def fail(source, target):
                    if Path(target) == path:
                        raise OSError("PRIVATE synthetic failure")
                    return replace(source, target)
                with mock.patch.object(records.os, "replace", side_effect=fail):
                    with self.assertRaisesRegex(records.UnreadableRecord, "could not be opened"):
                        call()
                self.assertEqual(before, path.read_bytes())
                self.assertFalse(tuple(path.parent.glob("*.partial")))

    def test_distinct_approval_keys_and_unknown_fields_survive_concurrent_updates(self):
        with self.approval_case() as fixture:
            path = fixture.run / approval_record.RECORD
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["future_optional"] = "retain top-level evidence"
            payload["items"][0]["delegated_answers_verification"] = "verified"
            payload["items"][0]["delegated_answers_reason"] = "retained optional evidence"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(lambda key: self.approve(fixture, key), ("left", "right")))
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual({"first", "left", "right"}, {row["submission"] for row in saved["items"]})
            self.assertEqual(3, saved["approval_revision"])
            self.assertEqual("retain top-level evidence", saved["future_optional"])
            first = next(row for row in saved["items"] if row["submission"] == "first")
            self.assertEqual("verified", first["delegated_answers_verification"])
            self.assertEqual("retained optional evidence", first["delegated_answers_reason"])

    def test_sibling_machine_write_fault_keeps_its_classification_and_prior_approval(self):
        for kind in ("approve", "stage"):
            with self.subTest(route=kind), self.command_case(kind) as (path, call):
                before = path.read_bytes()
                failure = records.UnreadableRecord(path.parent / "context.json", "could not be opened")
                with mock.patch.object(approval_record.project_context, "go_ahead", side_effect=failure):
                    with self.assertRaises(records.UnreadableRecord) as caught:
                        call()
                self.assertIs(failure, caught.exception)
                self.assertEqual(before, path.read_bytes())

    def test_new_approval_retains_its_own_history_and_optional_evidence(self):
        with self.command_case("approve") as (path, call):
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["items"][0]["future_optional"] = "retain reader evidence"
            path.write_text(json.dumps(payload), encoding="utf-8")
            call()
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(2, saved["approval_revision"])
            self.assertEqual([1, 2], [row["approval_revision"] for row in saved["items"][0]["approvals"]])
            self.assertEqual("retain reader evidence", saved["items"][0]["future_optional"])

    def test_assignment_reapprovals_serialize_revisions_and_clear_only_old_gate2_authority(self):
        with self.command_case("stage") as (path, _call):
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload.update(future_optional="retain upload evidence", gate2_confirmed=True,
                           gate2_reply_verification="verified")
            path.write_text(json.dumps(payload), encoding="utf-8")
            def stage(_key):
                return assignment_submission.stage(path.parent, path.parent / "artifact.docx",
                    artifact_approved=True, clinician_reply="Approve the synthetic artifact.")
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(stage, ("left", "right")))
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(3, saved["approval_revision"])
            self.assertEqual("retain upload evidence", saved["future_optional"])
            self.assertEqual("awaiting-upload", saved["upload_route"])
            self.assertNotIn("gate2_confirmed", saved)
            self.assertNotIn("gate2_reply_verification", saved)

    def test_same_posting_route_is_an_explicit_no_write_and_refusal_preserves_bytes(self):
        with self.command_case("agent-post") as (path, call):
            call()
            before = path.read_bytes()
            with mock.patch.object(records.os, "replace", side_effect=AssertionError("unchanged record")):
                call()
            self.assertEqual(before, path.read_bytes())
            payload = json.loads(before)
            Path(payload["items"][0]["sources"][0]).write_text("changed source", encoding="utf-8")
            with self.assertRaisesRegex(approval_record.ApprovalRecordError, "changed after approval"):
                call()
            self.assertEqual(before, path.read_bytes())

        with self.command_case("agreement") as (path, call):
            call()
            before = path.read_bytes()
            current = json.loads(before)
            with mock.patch.object(records.os, "replace", side_effect=AssertionError("unchanged coding record")):
                reader_remarks.replace_coding_record(path, current, kind="agreement")
            with self.assertRaisesRegex(reader_remarks.RemarkError, "cannot drop"):
                reader_remarks.replace_coding_record(path, {"pairs": []}, kind="agreement")
            self.assertEqual(before, path.read_bytes())

    def test_receipt_retries_and_coding_retries_retain_concurrent_remarks(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            source = run / "source.md"
            source.write_text("synthetic source", encoding="utf-8")
            def prepare(text):
                report = reader_remarks.report((reader_remarks.Remark("CLAIM", text),))
                return reader_remarks.prepare(run, "discussion-post", "first", (source,), report)
            prepare("Original remark.")
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(prepare, ("Left remark.", "Right remark.")))
            receipt = json.loads(reader_remarks._receipt_path(run, "discussion-post", "first").read_text(encoding="utf-8"))
            self.assertEqual({"Original remark.", "Left remark.", "Right remark."},
                             {row.text for row in reader_remarks.read_report(receipt["report"])})
            path = run / "reader.json"
            def replace(text):
                reader_remarks.replace_coding_record(path, {"pairs": [{"stem": "note", "codes": [], "remarks": [text]}]}, kind="agreement")
            replace("Original remark.")
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(replace, ("Left remark.", "Right remark.")))
            self.assertEqual({"Original remark.", "Left remark.", "Right remark."},
                             set(json.loads(path.read_text(encoding="utf-8"))["pairs"][0]["remarks"]))


if __name__ == "__main__":
    unittest.main()
