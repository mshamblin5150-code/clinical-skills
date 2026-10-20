"""Tool-written record boundary and freeze refusal controls; ADR 0422."""
# phi-scan: synthetic
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

import artifact_lock_test_support
import artifact_lock
import frozen_grade
import run_record_reader as records
import run_status_stop_hook as hook


class ToolRecordReader(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_missing_decode_wrong_shape_and_unopenable_are_distinct_and_safe(self):
        path = self.root / "frozen-grades.json"
        self.assertIsNone(records.read_tool_record(path, records.frozen_record))
        for content, expected in ((b'{', 'does not decode at line 1 column 2'),
                                  (b'{"items": []}', 'wrong shape: record items'),
                                  (b'\xff', 'does not decode at line 1 column 1')):
            path.write_bytes(content)
            with self.assertRaises(records.UnreadableRecord) as caught:
                records.read_tool_record(path, records.frozen_record)
            self.assertEqual(f"frozen-grades.json: unreadable — {expected}", str(caught.exception))
        path.unlink()
        path.mkdir()
        with self.assertRaisesRegex(records.UnreadableRecord, 'could not be opened'):
            records.read_tool_record(path, records.frozen_record)

    def test_unknown_filename_and_exception_values_never_leak(self):
        path = self.root / "private-example-name.json"
        path.write_text('{}', encoding='utf-8')
        def decoder(text):
            raise ValueError('private example value')
        with self.assertRaises(records.UnreadableRecord) as caught:
            records.read_tool_record(path, decoder)
        self.assertEqual('file 1 of 1: unreadable — wrong shape: declared record shape', str(caught.exception))

    def test_decoder_recursion_is_a_safe_unreadable_record_on_consumer_python(self):
        path = self.root / 'posting-approvals.json'
        path.write_text('[' * 2000 + '0' + ']' * 2000, encoding='utf-8')
        def recursive_decoder(_text):
            raise RecursionError('PRIVATE-PLANTED')
        for decoder in (records.posting_record, recursive_decoder):
            with self.subTest(decoder=decoder.__name__), self.assertRaises(records.UnreadableRecord) as caught:
                records.read_tool_record(path, decoder)
            self.assertIn('posting-approvals.json: unreadable — wrong shape:', str(caught.exception))
            self.assertNotIn('PRIVATE-PLANTED', str(caught.exception))

    def test_an_existing_entry_with_a_missing_read_target_is_not_absent(self):
        path = self.root / 'frozen-grades.json'
        path.write_text('{"items":{}}', encoding='utf-8')
        with mock.patch.object(Path, 'open', side_effect=FileNotFoundError('PRIVATE-PLANTED')):
            with self.assertRaisesRegex(records.UnreadableRecord, '^frozen-grades.json: unreadable — could not be opened$'):
                records.read_tool_record(path, records.frozen_record)

    def test_assignment_carrier_keys_and_required_item_fields_share_one_schema(self):
        record = {'approval_revision': 1, 'gate1_approved': True,
                  'artifact': 'synthetic.pptx', 'artifact_path': 'synthetic.pptx', 'sha256': 'a' * 64,
                  'attachment_count': 1, 'uploaded_files': [], 'upload_route': 'awaiting-upload',
                  'approved_carriers': [{'filename': 'synthetic.pptx', 'sha256': 'a' * 64}]}
        records.submission_record(json.dumps(record))
        duplicate = {**record, 'approved_carriers': record['approved_carriers'] * 2}
        missing = {**record, 'approved_carriers': [{'filename': 'synthetic.pptx'}]}
        for damaged in (duplicate, missing):
            with self.assertRaises(records.RecordShapeError):
                records.submission_record(json.dumps(damaged))

    def test_raw_cr_is_preserved_and_content_damage_keeps_its_meaning(self):
        path = self.root / 'project-context.md'
        path.write_bytes(b'one\rtwo\r\n')
        self.assertEqual('one\rtwo\r\n', records.read_tool_record(path, lambda text: text))
        def content_check(text):
            raise records.RecordContentError('content finding')
        with self.assertRaises(records.RecordContentError):
            records.read_tool_record(path, content_check)

    def test_one_record_is_counted_once_across_readers_and_capture_is_per_command(self):
        path = self.root / 'posting-approvals.json'
        path.write_text('{', encoding='utf-8')
        with records.capture_errors() as faults:
            for _ in range(2):
                with self.assertRaises(records.UnreadableRecord):
                    records.read_tool_record(path, records.posting_record)
            self.assertEqual(1, len(faults))
        with records.capture_errors() as following:
            self.assertFalse(following)

    def test_freeze_refuses_damage_and_held_lock_without_mutation(self):
        path = self.root / frozen_grade.RECORD
        item = {'approval_revision': 2, 'submission': 'synthetic', 'sources': []}
        for content in (b'{', b'{"items": []}'):
            path.write_bytes(content)
            with self.assertRaises(records.UnreadableRecord):
                frozen_grade.freeze(self.root, 'clinical-note', item)
            self.assertEqual(content, path.read_bytes())
        path.write_text('{"items": {}}', encoding='utf-8')
        original = path.read_bytes()
        with artifact_lock.hold(path, 'synthetic competing writer'):
            with self.assertRaisesRegex(records.UnreadableRecord, 'held by another task: process'):
                frozen_grade.freeze(self.root, 'clinical-note', item)
        self.assertEqual(original, path.read_bytes())

    def test_both_approval_readers_reject_duplicate_keys_and_missing_item_fields(self):
        import approval_record
        item = {'skill': 'clinical-note', 'submission': 'synthetic', 'sha256': 'a' * 64,
                'sources': ['synthetic.md'], 'grader_args': ['synthetic.md'], 'posting_route': 'awaiting-posting',
                'pregrade_status': 'clean', 'approval_revision': 1}
        path = self.root / 'posting-approvals.json'
        for items in ([item, item], [{key: value for key, value in item.items() if key != 'sources'}]):
            path.write_text(json.dumps({'version': 1, 'approval_revision': 1, 'items': items}), encoding='utf-8')
            for reader in (lambda: approval_record._read(self.root), lambda: hook.approvals(self.root)):
                with self.assertRaises(records.UnreadableRecord):
                    reader()

    def test_damaged_approval_demands_stopped_reason_and_never_rewrites_it(self):
        path = self.root / 'posting-approvals.json'
        path.write_bytes(b'{')
        transcript = self.root / 'session.jsonl'
        transcript.write_text('', encoding='utf-8')
        with mock.patch.object(hook, 'touched_runs', return_value=(self.root,)):
            for status in ('complete', 'awaiting AAR', 'stopped'):
                response = hook.handle({'transcript_path': str(transcript),
                    'last_assistant_message': f'Run status: {self.root.name} — {status}'})
                self.assertEqual('block', response.get('decision'))
            response = hook.handle({'transcript_path': str(transcript),
                'last_assistant_message': f'Run status: {self.root.name} — stopped - bookkeeping unreadable'})
            self.assertEqual({}, response)
        self.assertEqual(b'{', path.read_bytes())
        self.assertFalse((self.root / hook.STATE_RECORD).exists())

    def test_damaged_revision_cannot_restart_and_reuse_an_earlier_frozen_grade(self):
        import assignment_submission
        import approval_record
        artifact = self.root / 'synthetic.pptx'
        artifact.write_bytes(b'synthetic artifact')
        gates = self.root / assignment_submission.RECORD
        gates.write_bytes(b'{"approval_revision":4,')
        retained = self.root / frozen_grade.RECORD
        retained.write_text(json.dumps({'items': {'course-assignment:synthetic': {
            'approval_revision': 1, 'frozen_at': '2026-01-01T00:00:00Z',
            'kind': 'graded clean', 'sources': {str(artifact): 'a' * 64}}}}), encoding='utf-8')
        original = retained.read_bytes()
        with (mock.patch.object(assignment_submission, '_require_signed_bar'),
              mock.patch.object(assignment_submission, '_pre_upload_grade', return_value=(True, 'clean')),
              mock.patch.object(assignment_submission.project_context, 'go_ahead', return_value=SimpleNamespace(finding=False, report='clean')),
              mock.patch.object(approval_record, 'verify_clinician_reply', return_value=approval_record.ReplyVerification('verified', 'synthetic', time.time()+1)),
              mock.patch.object(assignment_submission.reader_remarks, 'verify', return_value=[])):
            with self.assertRaises(records.UnreadableRecord):
                assignment_submission.stage(self.root, artifact, artifact_approved=True, clinician_reply='Approved.')
        self.assertEqual(b'{"approval_revision":4,', gates.read_bytes())
        self.assertEqual(original, retained.read_bytes())


if __name__ == '__main__':
    unittest.main()
