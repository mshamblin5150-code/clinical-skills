"""Public library entrypoints that have no separate CLI (synthetic ADR 0422 controls)."""
# phi-scan: synthetic
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import artifact_lock_test_support
import approval_record
import assignment_submission
import frozen_grade
import reader_remarks
import run_record_reader as records
import run_status_stop_hook as hook


class PublicRecordApis(unittest.TestCase):
    def setUp(self):
        from approval_record_test_support import isolate_manifest_binding
        isolate_manifest_binding(self)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / 'synthetic.pptx'
        self.source.write_bytes(b'synthetic artifact')

    def refuses(self, path, action, *, wrong_cause='wrong shape: record object'):
        path.parent.mkdir(parents=True, exist_ok=True)
        for content, cause in ((b'{', 'does not decode at line 1 column 2'),
                               (b'[]', wrong_cause), (None, 'could not be opened')):
            with self.subTest(kind=path.name, cause=cause):
                if content is None:
                    path.mkdir()
                else:
                    path.write_bytes(content)
                with self.assertRaises(records.UnreadableRecord) as caught:
                    action()
                self.assertEqual(f'{records.checked_label(path)}: unreadable — {cause}', str(caught.exception))
                if content is None:
                    self.assertEqual([], list(path.iterdir()))
                    path.rmdir()
                else:
                    self.assertEqual(content, path.read_bytes())
                    path.unlink()

    def test_content_approval_cannot_restart_damaged_approval_history(self):
        self.refuses(self.root / approval_record.RECORD, lambda: approval_record.approve(
            self.root, skill='discussion-post', submission='synthetic', sources=(self.source,),
            grader_args=(str(self.root),), content_approved=True, clinician_reply='Synthetic approval.',
        ))

    def test_clinical_prepare_preserves_existing_shared_coding_record_faults(self):
        def prepare():
            return approval_record.prepare(self.root, skill='clinical-note', submission='synthetic',
                sources=(self.source,), grader_args=(str(self.root),))
        with mock.patch.object(approval_record, '_pre_post_grade', return_value=(0, 'synthetic grade: clean')):
            self.assertEqual('synthetic grade: clean', prepare().report.strip())
            receipt = reader_remarks._receipt_path(self.root, 'clinical-note', 'synthetic')
            original = receipt.read_bytes()
            for directory in ('agreement-reader', 'specificity-reader'):
                self.refuses(self.root / directory / 'read.json', prepare,
                    wrong_cause='wrong shape: declared record shape')
                self.assertEqual(original, receipt.read_bytes())

    def test_only_shared_absence_can_start_a_new_approval_history(self):
        self.assertEqual([], approval_record._read(self.root, missing_ok=True)['items'])
        self.assertFalse(assignment_submission.project_context_posting(self.root, 'synthetic').posted)
        for name, action in (
            (approval_record.RECORD, lambda: approval_record.approve(
                self.root, skill='discussion-post', submission='synthetic', sources=(self.source,),
                grader_args=(str(self.root),), content_approved=True, clinician_reply='Synthetic approval.')),
            (assignment_submission.RECORD, lambda: assignment_submission.project_context_posting(self.root, 'synthetic')),
        ):
            path = self.root / name
            try:
                path.symlink_to(self.root / 'missing-target.json')
            except OSError:
                self.skipTest('symbolic link creation unavailable')
            try:
                with self.assertRaisesRegex(records.UnreadableRecord, 'could not be opened'):
                    action()
                self.assertTrue(path.is_symlink())
                self.assertFalse(path.exists())
            finally:
                path.unlink()

    def test_prepare_refuses_both_damaged_approval_history_and_receipt(self):
        context = SimpleNamespace(finding=False, coverage=False, report='project context: clean')
        def prepare():
            return approval_record.prepare(self.root, skill='discussion-post', submission='synthetic',
                                           sources=(self.source,), grader_args=(str(self.root),))
        with (mock.patch.object(approval_record, '_pre_post_grade', return_value=(0, 'synthetic grade: clean')),
              mock.patch.object(approval_record.project_context, 'go_ahead', return_value=context)):
            self.refuses(self.root / approval_record.RECORD, prepare)
            self.refuses(reader_remarks._receipt_path(self.root, 'discussion-post', 'synthetic'), prepare)

    def test_assignment_stage_cannot_restart_damaged_revision(self):
        with (mock.patch.object(assignment_submission, '_pre_upload_grade', return_value=(True, 'clean')),
              mock.patch.object(assignment_submission, '_require_signed_bar')):
            self.refuses(self.root / assignment_submission.RECORD, lambda: assignment_submission.stage(
                self.root, self.source, artifact_approved=True, clinician_reply='Synthetic approval.',
            ))

    def test_freeze_api_preserves_truncated_wrong_shape_and_unopenable_records(self):
        self.refuses(self.root / frozen_grade.RECORD, lambda: frozen_grade.freeze(
            self.root, 'discussion-post', {'approval_revision': 1, 'submission': 'synthetic', 'sources': [str(self.source)]},
        ))

    def test_stop_classifies_each_approval_and_state_record_fault(self):
        import json
        from tool_record_test_support import posting_record
        valid = json.dumps(posting_record(self.source, {'skill': 'discussion-post', 'submission': 'synthetic'}))
        posting = self.root / 'posting-approvals.json'
        transcript = self.root / 'session.jsonl'
        transcript.write_text('', encoding='utf-8')
        for name in ('posting-approvals.json', 'submission-gates.json', 'run-status.json'):
            path = self.root / name
            for content, cause in ((b'{', 'does not decode at line 1 column 2'),
                                   (b'[]', 'wrong shape: record object'), (None, 'could not be opened')):
                with self.subTest(name=name, cause=cause):
                    posting.write_text(valid, encoding='utf-8')
                    if content is None:
                        path.unlink(missing_ok=True)
                        path.mkdir()
                    else:
                        path.write_bytes(content)
                    with mock.patch.object(hook, 'touched_runs', return_value=(self.root,)):
                        payload = {'transcript_path': str(transcript),
                                   'last_assistant_message': f'Run status: {self.root.name} — complete'}
                        result = hook.handle(payload)
                        self.assertEqual('block', result.get('decision'))
                        self.assertIn(f'{name}: unreadable — {cause}', result['reason'])
                        payload['last_assistant_message'] = f'Run status: {self.root.name} — stopped - bookkeeping unreadable'
                        self.assertEqual({}, hook.handle(payload))
                    if content is None:
                        self.assertEqual([], list(path.iterdir()))
                        path.rmdir()
                    else:
                        self.assertEqual(content, path.read_bytes())
                        path.unlink()

    def test_damaged_state_does_not_open_a_run_without_an_approval(self):
        transcript = self.root / 'session.jsonl'
        transcript.write_text('', encoding='utf-8')
        state = self.root / hook.STATE_RECORD
        for content in (b'{', b'[]', None):
            if content is None:
                state.mkdir()
            else:
                state.write_bytes(content)
            with mock.patch.object(hook, 'touched_runs', return_value=(self.root,)):
                self.assertEqual({}, hook.handle({'transcript_path': str(transcript),
                    'last_assistant_message': 'Ordinary reply; no approved run.'}))
            if content is None:
                self.assertEqual([], list(state.iterdir()))
                state.rmdir()
            else:
                self.assertEqual(content, state.read_bytes())
                state.unlink()

    def test_receipt_prepare_including_coverage_only_and_verify_refuse_damage(self):
        path = reader_remarks._receipt_path(self.root, 'discussion-post', 'synthetic')
        for coverage_only in (False, True):
            self.refuses(path, lambda: reader_remarks.prepare(
                self.root, 'discussion-post', 'synthetic', (self.source,), 'clean', coverage_only=coverage_only,
            ))
        self.refuses(path, lambda: reader_remarks.verify(
            self.root, 'discussion-post', 'synthetic', (self.source,), 'clean', 'Synthetic approval.', 4102444800, (),
        ))


if __name__ == '__main__':
    unittest.main()
