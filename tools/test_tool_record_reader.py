"""Tool-written record boundary and freeze refusal controls; ADR 0422."""
# phi-scan: synthetic
import json
from pathlib import Path
import tempfile
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
                                  (b'\xff', 'does not decode at byte offset 0')):
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


if __name__ == '__main__':
    unittest.main()
