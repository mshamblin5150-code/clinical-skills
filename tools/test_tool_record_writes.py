"""ADR 0422 locked read/change/replace and append public seam controls."""
# phi-scan: synthetic
import artifact_lock_test_support
import artifact_lock
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import run_record_reader as records


class LockedRecordWrites(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / 'posting-approvals.json'
        self.path.write_bytes(b'{"first": 1}\n')

    def change(self, previous):
        return records.RecordUpdate(json.dumps({**previous, 'second': 2}).encode(), 'saved')

    def test_update_reads_inside_lock_and_no_write_is_explicit(self):
        before = self.path.read_bytes()
        result = records.update_tool_record(
            self.path, records.object_record, lambda old: records.RecordUpdate(None, old))
        self.assertEqual(result, {'first': 1})
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(records.update_tool_record(self.path, records.object_record, self.change), 'saved')
        self.assertEqual(json.loads(self.path.read_bytes()), {'first': 1, 'second': 2})
        absent = self.root / 'new.json'
        self.assertIsNone(records.update_tool_record(
            absent, records.object_record, lambda old: records.RecordUpdate(None, old)))
        self.assertFalse(absent.exists())

    def test_held_lock_refuses_before_callback_with_bounded_safe_cause(self):
        before = self.path.read_bytes()
        change = mock.Mock(side_effect=AssertionError('must not mutate'))
        started = time.monotonic()
        with artifact_lock.hold(self.path, 'synthetic holder'):
            with self.assertRaisesRegex(records.UnreadableRecord,
                                        r'^posting-approvals.json: unreadable — held by another task: (process \d+|another task)$'):
                records.update_tool_record(self.path, records.object_record, change)
        self.assertLess(time.monotonic() - started, 3)
        change.assert_not_called()
        self.assertEqual(self.path.read_bytes(), before)

    def test_interruption_before_replace_retains_prior_bytes_and_removes_partial(self):
        before = self.path.read_bytes()
        with mock.patch.object(records.os, 'replace', side_effect=OSError('PRIVATE-PLANTED')):
            with self.assertRaisesRegex(records.UnreadableRecord,
                                        '^posting-approvals.json: unreadable — could not be opened$'):
                records.update_tool_record(self.path, records.object_record, self.change)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.root.iterdir()), [self.path])

    def test_bad_existing_record_never_reaches_mutation(self):
        self.path.write_bytes(b'{')
        change = mock.Mock(side_effect=AssertionError('must not mutate'))
        with self.assertRaises(records.UnreadableRecord):
            records.update_tool_record(self.path, records.object_record, change)
        change.assert_not_called()
        self.assertEqual(self.path.read_bytes(), b'{')

    def test_compound_rollback_finishes_before_history_lock_is_released(self):
        sibling = self.root / 'retained-copy.md'
        before = self.path.read_bytes()
        def rollback():
            with self.assertRaises(artifact_lock.ArtifactBusy):
                with artifact_lock.hold(self.path, 'competing history writer'):
                    self.fail('history lock released before rollback')
            sibling.unlink()
        def change(previous):
            sibling.write_bytes(b'synthetic copy')
            return records.RecordUpdate(b'{"second": 2}', rollback=rollback)
        with mock.patch.object(records.os, 'replace', side_effect=OSError('PRIVATE-PLANTED')):
            with self.assertRaises(records.UnreadableRecord):
                records.update_tool_record(self.path, records.object_record, change)
        self.assertFalse(sibling.exists())
        self.assertEqual(self.path.read_bytes(), before)

    def test_concurrent_distinct_updates_both_survive(self):
        def update(key):
            def change(previous):
                time.sleep(.05)
                return records.RecordUpdate(json.dumps({**previous, key: True}).encode())
            records.update_tool_record(self.path, records.object_record, change)
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(update, ('left', 'right')))
        self.assertEqual(json.loads(self.path.read_bytes()), {'first': 1, 'left': True, 'right': True})

    def test_failed_rollback_keeps_original_safe_persistence_refusal(self):
        before = self.path.read_bytes()
        def rollback():
            raise ValueError('PRIVATE-ROLLBACK')
        with mock.patch.object(records.os, 'replace', side_effect=OSError('PRIVATE-WRITE')):
            with self.assertRaisesRegex(records.UnreadableRecord,
                                        '^posting-approvals.json: unreadable — could not be opened$'):
                records.update_tool_record(self.path, records.object_record,
                                           lambda old: records.RecordUpdate(b'{}', rollback=rollback))
        self.assertEqual(self.path.read_bytes(), before)

    def test_append_validates_prior_bytes_and_keeps_both_entries(self):
        path = self.root / 'outbound-searches.jsonl'
        decode = lambda text: [json.loads(line) for line in text.splitlines()]
        path.write_bytes(b'{"first": 1}\n')
        records.update_tool_record(path, decode,
                                   lambda old: records.RecordUpdate(b'{"second": 2}\n', len(old)), append=True)
        self.assertEqual(path.read_bytes(), b'{"first": 1}\n{"second": 2}\n')
        before = path.read_bytes()
        with artifact_lock.hold(path, 'synthetic append holder'):
            with self.assertRaises(records.UnreadableRecord):
                records.update_tool_record(path, decode, self.change, append=True)
        self.assertEqual(path.read_bytes(), before)
