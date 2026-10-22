"""Synthetic controls only; no Windows kernel or application is executed."""
import contextlib
import ctypes
import dataclasses
import io
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import generated_output_contract as g

SYNTHETIC_ROOT = Path(Path.cwd().anchor) / 'synthetic'


class KernelFunction:
    def __init__(self, implementation):
        self.implementation = implementation

    def __call__(self, *args):
        return self.implementation(*args)


class SyntheticKernel:
    """A tiny sharing/disposition model, not evidence of real Windows behavior."""

    def __init__(self):
        self.files = {}
        self.handles = {}
        self.next_handle = 100
        self.operations = []
        self.chunk_size = 2
        for public, implementation in (
                ('CreateFileW', self.open), ('CloseHandle', self.close),
                ('GetFileType', lambda handle: 1),
                ('GetFileInformationByHandleEx', self.record),
                ('SetFilePointerEx', self.seek), ('ReadFile', self.read),
                ('SetFileInformationByHandle', self.mark)):
            setattr(self, public, KernelFunction(implementation))

    def add(self, path, data=b'abc'):
        self.files[str(path)] = {'data': data, 'pending': False}

    def open(self, path, access, sharing, security, creation, flags, template):
        self.operations.append(('open', path, access, sharing, security, creation, flags, template))
        if path not in self.files or self.files[path]['pending']:
            return ctypes.c_void_p(-1).value
        if creation != 3 or security is not None or template is not None or flags != 0x08200000:
            return ctypes.c_void_p(-1).value
        for state in self.handles.values():
            if state['path'] != path:
                continue
            for requested, granted in ((access, state['sharing']), (state['access'], sharing)):
                if ((requested & 0x80000000 and not granted & 1)
                        or (requested & 0x40000000 and not granted & 2)
                        or (requested & 0x00010000 and not granted & 4)):
                    return ctypes.c_void_p(-1).value
        self.next_handle += 1
        self.handles[self.next_handle] = {'path': path, 'access': access, 'sharing': sharing,
                                          'object': self.files[path], 'position': 0}
        return self.next_handle

    def close(self, handle):
        self.operations.append(('close', handle))
        if handle not in self.handles:
            return 0
        state = self.handles.pop(handle)
        if state['object']['pending'] and not any(
                other['object'] is state['object'] for other in self.handles.values()):
            self.files = {name: item for name, item in self.files.items() if item is not state['object']}
        return 1

    def record(self, handle, kind, pointer, size):
        state = self.handles[handle]
        item = pointer._obj
        if kind == 0:
            item.CreationTime = 116444736000000001
            item.LastWriteTime = 116444736000000002
            item.ChangeTime = 116444736000000003
            item.FileAttributes = 32
        elif kind == 1:
            item.EndOfFile = len(state['object']['data'])
            item.NumberOfLinks = 1
            item.DeletePending = state['object']['pending']
        elif kind == 18:
            item.VolumeSerialNumber = 7
            item.FileId[0], item.FileId[15] = 11, 1
        elif kind == 9:
            item.FileAttributes = 32
        else:
            return 0
        return 1

    def seek(self, handle, distance, result, method):
        self.operations.append(('seek', handle, distance, method))
        if method != 0 or distance != 0:
            return 0
        self.handles[handle]['position'] = 0
        return 1

    def read(self, handle, buffer, requested, count, overlapped):
        self.operations.append(('read', handle, requested, overlapped))
        state = self.handles[handle]
        if not state['access'] & 0x80000000 or overlapped is not None:
            return 0
        data = state['object']['data'][state['position']:state['position'] + min(requested, self.chunk_size)]
        ctypes.memmove(buffer, data, len(data))
        count._obj.value = len(data)
        state['position'] += len(data)
        return 1

    def mark(self, handle, kind, pointer, size):
        self.operations.append(('mark', handle, kind, ctypes.string_at(pointer, size), size))
        state = self.handles[handle]
        if not state['access'] & 0x00010000 or kind != 4 or size != 1 or pointer._obj.DeleteFile != 1:
            return 0
        state['object']['pending'] = True
        return 1


class CompactNativeControls(unittest.TestCase):
    def setUp(self):
        from compact_capture_native import WindowsCompactAPI
        self.kernel = SyntheticKernel()
        self.path = SYNTHETIC_ROOT / 'command-0001/stdout.bin'
        self.kernel.add(self.path)
        self.api = WindowsCompactAPI(self.kernel)
        self.deadline = time.monotonic() + 30

    def test_missing_capture_refuses_without_creating_or_closing_any_file(self):
        with contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(g.q.Refused, 'compact_capture_unread'):
            self.api.open_capture(SYNTHETIC_ROOT / 'command-0002/stderr.bin')
        self.assertEqual(self.kernel.files[str(self.path)]['data'], b'abc')
        self.assertEqual([operation[0] for operation in self.kernel.operations], ['open'])

    def test_capture_open_refuses_traversal_even_with_an_allowed_tail(self):
        path = SYNTHETIC_ROOT / '../unowned/command-0001/stdout.bin'
        self.kernel.add(path)
        with contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(g.q.Refused, 'compact_capture_path_invalid'):
            self.api.open_capture(path)
        self.assertEqual(self.kernel.operations, [])

    def test_capture_open_accepts_only_an_absolute_fixed_owner_stream_name(self):
        for path in (self.path.as_posix(), Path('command-0001/stdout.bin'),
                     SYNTHETIC_ROOT / 'command-001/stdout.bin',
                     SYNTHETIC_ROOT / 'command-0001/output.bin',
                     SYNTHETIC_ROOT / 'command-0001/receipt.json',
                     SYNTHETIC_ROOT / 'command-0001/stdout.bin:alternate'):
            with self.subTest(path=path), contextlib.redirect_stdout(io.StringIO()), \
                    self.assertRaisesRegex(g.q.Refused, 'compact_capture_path_invalid'):
                self.api.open_capture(path)
        self.assertEqual(self.kernel.operations, [])
        handle = self.api.open_capture(self.path)
        self.assertEqual(self.api.read(handle, 3, self.deadline), b'abc')
        self.api.close(handle)

    def test_sharing_conflicts_refuse_in_both_directions_without_widening(self):
        reader = self.api.open(self.path)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(g.q.Refused):
            self.api.open_capture(self.path)
        self.assertEqual(self.api.read(reader, 3, self.deadline), b'abc')
        self.api.close(reader)
        capture = self.api.open_capture(self.path)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(g.q.Refused):
            self.api.open(self.path)
        self.assertEqual(self.api.read(capture, 3, self.deadline), b'abc')
        self.api.close(capture)
        opens = [operation for operation in self.kernel.operations if operation[0] == 'open']
        self.assertEqual([operation[2:4] for operation in opens],
                         [(0x80000000, 1), (0x80010000, 1), (0x80010000, 1), (0x80000000, 1)])

    def test_receipt_handle_remains_readonly_and_prevents_write_or_delete_opens(self):
        receipt = SYNTHETIC_ROOT / 'compact-success.json'
        self.kernel.add(receipt, b'{}\n')
        handle = self.api.open(receipt)
        self.assertEqual(self.api.read(handle, 16384, self.deadline), b'{}\n')
        for access in (0x40000000, 0x00010000):
            self.assertEqual(self.kernel.CreateFileW(str(receipt), access, 7, None, 3, 0x08200000, None),
                             ctypes.c_void_p(-1).value)
        with contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(g.q.Refused, 'compact_capture_disposition_failed'):
            self.api.mark_delete(handle)
        self.assertFalse(self.api.record(handle).delete_pending)
        self.api.close(handle)
        self.assertEqual(self.kernel.files[str(receipt)]['data'], b'{}\n')

    def test_read_refuses_oversize_without_implicit_mark_or_close(self):
        handle = self.api.open_capture(self.path)
        with contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(g.q.Refused, 'generated_file_oversize'):
            self.api.read(handle, 2, self.deadline)
        self.assertFalse(self.api.record(handle).delete_pending)
        self.assertEqual(self.api.read(handle, 3, self.deadline), b'abc')
        self.api.close(handle)
        self.assertEqual(self.kernel.files[str(self.path)]['data'], b'abc')

    def test_empty_capture_accepts_zero_limit_but_nonempty_capture_does_not(self):
        self.kernel.add(self.path, b'')
        handle = self.api.open_capture(self.path)
        self.assertEqual(self.api.read(handle, 0, self.deadline), b'')
        self.api.close(handle)
        self.kernel.add(self.path, b'x')
        handle = self.api.open_capture(self.path)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(g.q.Refused, 'generated_file_oversize'):
            self.api.read(handle, 0, self.deadline)
        self.api.close(handle)

    def test_large_capture_is_read_with_a_finite_per_call_allocation(self):
        self.kernel.add(self.path, b'x' * 65537)
        self.kernel.chunk_size = 65536
        handle = self.api.open_capture(self.path)
        self.assertEqual(self.api.read(handle, 65537, self.deadline), b'x' * 65537)
        self.assertEqual([operation[2] for operation in self.kernel.operations if operation[0] == 'read'],
                         [65536, 2, 1])
        self.api.close(handle)

    def test_invalid_read_limit_or_deadline_refuses_before_any_io(self):
        handle = self.api.open_capture(self.path)
        for limit in (-1, True, 1.5, 16777217, None):
            with self.subTest(limit=limit), contextlib.redirect_stdout(io.StringIO()), \
                    self.assertRaisesRegex(g.q.Refused, 'compact_read_limit_invalid'):
                self.api.read(handle, limit, self.deadline)
        for deadline in (float('inf'), float('nan'), True, None, 'later'):
            with self.subTest(deadline=deadline), contextlib.redirect_stdout(io.StringIO()), \
                    self.assertRaisesRegex(g.q.Refused, 'compact_read_deadline_invalid'):
                self.api.read(handle, 3, deadline)
        self.assertEqual([operation[0] for operation in self.kernel.operations], ['open'])
        self.assertEqual(self.api.read(handle, 3, self.deadline), b'abc')
        self.api.close(handle)

    def test_deadline_checks_cover_admission_seek_and_each_read_including_eof(self):
        for ticks, expected_reads in (([3], 0), ([1, 3], 0), ([1, 1, 3], 1),
                                      ([1, 1, 1, 1, 1, 1, 3], 3)):
            with self.subTest(ticks=ticks):
                self.setUp()
                handle = self.api.open_capture(self.path)
                with mock.patch.object(time, 'monotonic', side_effect=ticks), \
                        contextlib.redirect_stdout(io.StringIO()), \
                        self.assertRaisesRegex(g.q.Refused, 'global_budget_exhausted'):
                    self.api.read(handle, 3, 2)
                self.assertEqual(len([operation for operation in self.kernel.operations
                                      if operation[0] == 'read']), expected_reads)
                self.assertFalse(self.api.record(handle).delete_pending)
                self.api.close(handle)

    def test_native_seek_or_read_failure_is_not_retried_and_retains_raw_data(self):
        for operation, reason in (('SetFilePointerEx', 'compact_capture_seek_failed'),
                                  ('ReadFile', 'compact_capture_read_failed')):
            with self.subTest(operation=operation):
                self.setUp()
                handle = self.api.open_capture(self.path)
                failure = mock.Mock(return_value=0)
                setattr(self.kernel, operation, failure)
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(g.q.Refused, reason):
                    self.api.read(handle, 3, self.deadline)
                self.assertEqual(failure.call_count, 1)
                self.assertFalse(self.api.record(handle).delete_pending)
                self.api.close(handle)
                self.assertEqual(self.kernel.files[str(self.path)]['data'], b'abc')

    def test_impossible_native_byte_count_refuses_without_returning_partial_bytes(self):
        handle = self.api.open_capture(self.path)
        def invalid_count(handle, buffer, requested, count, overlapped):
            count._obj.value = requested + 1
            return 1
        self.kernel.ReadFile = KernelFunction(invalid_count)
        with contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(g.q.Refused, 'compact_capture_read_invalid'):
            self.api.read(handle, 3, self.deadline)
        self.assertFalse(self.api.record(handle).delete_pending)
        self.api.close(handle)

    def test_failed_disposition_is_reported_once_and_does_not_trigger_a_fallback(self):
        handle = self.api.open_capture(self.path)
        failure = mock.Mock(return_value=0)
        self.kernel.SetFileInformationByHandle = failure
        with contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(g.q.Refused, 'compact_capture_disposition_failed'):
            self.api.mark_delete(handle)
        self.assertEqual(failure.call_count, 1)
        self.assertFalse(self.api.record(handle).delete_pending)
        self.api.close(handle)
        self.assertEqual(self.kernel.files[str(self.path)]['data'], b'abc')

    def test_uncertain_disposition_can_have_executed_and_is_never_retried(self):
        handle = self.api.open_capture(self.path)
        def uncertain(*args):
            self.kernel.mark(*args)
            return 0
        self.kernel.SetFileInformationByHandle = KernelFunction(uncertain)
        with contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(g.q.Refused, 'compact_capture_disposition_failed'):
            self.api.mark_delete(handle)
        self.assertTrue(self.api.record(handle).delete_pending)
        self.assertEqual([operation[0] for operation in self.kernel.operations], ['open', 'mark'])
        self.api.close(handle)
        self.assertNotIn(str(self.path), self.kernel.files)

    def test_close_failure_is_reported_once_without_a_second_close(self):
        handle = self.api.open_capture(self.path)
        failure = mock.Mock(return_value=0)
        self.kernel.CloseHandle = failure
        with contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(g.q.Refused, 'generated_handle_cleanup_failed'):
            self.api.close(handle)
        self.assertEqual(failure.call_args_list, [mock.call(handle)])
        self.assertEqual(self.kernel.files[str(self.path)]['data'], b'abc')

    def test_disposition_targets_the_retained_object_not_a_replaced_path(self):
        handle = self.api.open_capture(self.path)
        self.assertEqual(self.api.read(handle, 3, self.deadline), b'abc')
        original = self.kernel.files[str(self.path)]
        retired = str(SYNTHETIC_ROOT / 'retired-original')
        self.kernel.files[retired] = original
        # Deliberately bypass the model's sharing check to inject a changed namespace.
        self.kernel.add(self.path, b'new')
        self.api.mark_delete(handle)
        self.api.close(handle)
        self.assertNotIn(retired, self.kernel.files)
        self.assertEqual(self.kernel.files[str(self.path)]['data'], b'new')

    def test_missing_native_operation_never_selects_an_alternate_api(self):
        from compact_capture_native import WindowsCompactAPI
        for operation in ('ReadFile', 'SetFilePointerEx', 'SetFileInformationByHandle'):
            with self.subTest(operation=operation):
                kernel = SyntheticKernel()
                delattr(kernel, operation)
                with self.assertRaises(AttributeError):
                    WindowsCompactAPI(kernel)
                self.assertEqual(kernel.operations, [])

    def test_only_explicit_same_handle_disposition_marks_then_close_retires_the_object(self):
        from compact_capture_native import WindowsCompactAPI
        kernel = SyntheticKernel()
        path = SYNTHETIC_ROOT / 'command-0001/stdout.bin'
        kernel.add(path)
        api = WindowsCompactAPI(kernel)
        handle = api.open_capture(path)
        self.assertEqual(api.read(handle, 128, time.monotonic() + 30), b'abc')
        self.assertFalse(api.record(handle).delete_pending)
        api.mark_delete(handle)
        self.assertTrue(api.record(handle).delete_pending)
        self.assertIn(str(path), kernel.files)
        self.assertEqual(kernel.operations[-1], ('mark', handle, 4, b'\x01', 1))
        api.close(handle)
        self.assertNotIn(str(path), kernel.files)
        self.assertEqual([item for item in kernel.operations if item[0] == 'close'], [('close', handle)])

    def test_same_retained_handle_reads_binary_bytes_from_the_beginning(self):
        from compact_capture_native import WindowsCompactAPI
        kernel = SyntheticKernel()
        path = SYNTHETIC_ROOT / 'command-0001/stdout.bin'
        kernel.add(path, b'a\x00bcde')
        api = WindowsCompactAPI(kernel)
        handle = api.open_capture(path)
        self.assertEqual(api.read(handle, 6, time.monotonic() + 30), b'a\x00bcde')
        self.assertEqual(api.read(handle, 6, time.monotonic() + 30), b'a\x00bcde')
        self.assertEqual([item[1] for item in kernel.operations if item[0] == 'read'], [handle] * 8)
        self.assertEqual([item[0] for item in kernel.operations].count('open'), 1)
        api.close(handle)

    def test_capture_open_requests_only_the_approved_capability(self):
        from compact_capture_native import WindowsCompactAPI
        kernel = SyntheticKernel()
        path = SYNTHETIC_ROOT / 'command-0001/stdout.bin'
        kernel.add(path)
        api = WindowsCompactAPI(kernel)
        handle = api.open_capture(path)
        self.assertEqual(dataclasses.astuple(api.record(handle)),
                         (7, (1 << 120) + 11, 0o100666, 1, 3, 200, 300, 32, 100, 1, 0, False))
        self.assertEqual(kernel.operations[0],
                         ('open', str(path), 0x80010000, 1, None, 3, 0x08200000, None))
        api.close(handle)
        self.assertIn(str(path), kernel.files)


class SyntheticReadMetadata:
    """Native-shaped records at the injected operating-system boundary."""

    def __init__(self, records=None):
        self.snapshot = g.WindowsSnapshot(
            7, (1 << 120) + 11, 0o100666, 1, 3, 200, 300, 32, 100, 1, 0, False)
        self.records = iter(records) if records is not None else None
        self.next_handle = 100
        self.closed = []

    def open(self, path):
        self.next_handle += 1
        return self.next_handle

    def close(self, handle):
        self.closed.append(handle)

    def from_fd(self, fd):
        return 103

    def record(self, handle):
        return next(self.records) if self.records is not None else self.snapshot


class OwnedCaptureSnapshotControls(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory()
        self.addCleanup(self.fixture.cleanup)
        self.repo = Path(self.fixture.name).resolve()
        (self.repo / 'command-0001').mkdir()
        (self.repo / 'command-0001/stdout.bin').write_bytes(b'abc')
        self.deadline = time.monotonic() + 30

    def test_returns_exact_bytes_and_the_authenticated_full_native_identity(self):
        api = SyntheticReadMetadata()
        with mock.patch.object(g, 'windows_metadata_api', return_value=api):
            raw, snapshot = g.read_owned_capture_snapshot(
                self.repo, 'command-0001/stdout.bin', 128, self.deadline)
        self.assertEqual(raw, b'abc')
        self.assertEqual(dataclasses.astuple(snapshot),
                         (7, (1 << 120) + 11, 0o100666, 1, 3, 200, 300, 32, 100, 1, 0, False))
        self.assertEqual(api.closed, [101, 102])

    def test_snapshot_reader_refuses_an_unbounded_limit_before_native_open(self):
        api = SyntheticReadMetadata()
        with mock.patch.object(g, 'windows_metadata_api', return_value=api), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(g.q.Refused, 'compact_read_limit_invalid'):
                g.read_owned_capture_snapshot(self.repo, 'command-0001/stdout.bin', 16777217, self.deadline)
        self.assertEqual(api.next_handle, 100)

    def test_snapshot_reader_requires_a_finite_deadline_before_native_open(self):
        api = SyntheticReadMetadata()
        with mock.patch.object(g, 'windows_metadata_api', return_value=api), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(g.q.Refused, 'compact_read_deadline_invalid'):
                g.read_owned_capture_snapshot(self.repo, 'command-0001/stdout.bin', 128, float('inf'))
        self.assertEqual(api.next_handle, 100)

    def test_snapshot_reader_refuses_without_native_identity_but_legacy_bytes_still_work(self):
        with mock.patch.object(g, 'windows_metadata_api', return_value=None), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(g.q.Refused, 'generated_native_snapshot_unavailable'):
                g.read_owned_capture_snapshot(self.repo, 'command-0001/stdout.bin', 128, self.deadline)
            self.assertEqual(g.read_owned_capture(self.repo, 'command-0001/stdout.bin', 128, self.deadline), b'abc')

    def test_native_legacy_capture_and_general_readers_still_return_bytes_only(self):
        (self.repo / 'result.json').write_bytes(b'abc')
        for reader, relative in ((g.read_owned_capture, 'command-0001/stdout.bin'),
                                 (g.safe_read, 'result.json')):
            with self.subTest(relative=relative), \
                    mock.patch.object(g, 'windows_metadata_api', return_value=SyntheticReadMetadata()):
                self.assertEqual(reader(self.repo, relative, 128, self.deadline), b'abc')

    def test_snapshot_reader_preserves_every_coherent_field_at_every_boundary(self):
        good = SyntheticReadMetadata().snapshot
        for field in (*g.METADATA_FIELDS, 'st_birthtime_ns'):
            for start in (2, 4, 6):
                with self.subTest(field=field, start=start):
                    delta = 1 << 121 if field == 'st_ino' else 1
                    bad = dataclasses.replace(good, **{field: getattr(good, field) + delta})
                    records = [good] * 8
                    records[start:start + 2] = [bad, bad]
                    api = SyntheticReadMetadata(records)
                    with mock.patch.object(g, 'windows_metadata_api', return_value=api), \
                            contextlib.redirect_stdout(io.StringIO()), self.assertRaises(g.q.Refused):
                        g.read_owned_capture_snapshot(self.repo, 'command-0001/stdout.bin', 128, self.deadline)
                    self.assertEqual(api.closed, [101, 102] if start == 6 else [101])

    def test_snapshot_reader_rejects_reparse_hardlink_delete_pending_and_nonregular_records(self):
        good = SyntheticReadMetadata().snapshot
        for change in ({'reparse_tag': 1}, {'st_file_attributes': 0x400}, {'st_nlink': 2},
                       {'delete_pending': True}, {'file_type': 2}, {'st_mode': 0o040777}):
            with self.subTest(change=change):
                bad = dataclasses.replace(good, **change)
                api = SyntheticReadMetadata([bad, bad])
                with mock.patch.object(g, 'windows_metadata_api', return_value=api), \
                        contextlib.redirect_stdout(io.StringIO()), \
                        self.assertRaisesRegex(g.q.Refused, 'generated_file_unsafe'):
                    g.read_owned_capture_snapshot(self.repo, 'command-0001/stdout.bin', 128, self.deadline)
                self.assertEqual(api.closed, [101])

    def test_snapshot_reader_rejects_a_native_record_that_changes_between_queries(self):
        good = SyntheticReadMetadata().snapshot
        bad = dataclasses.replace(good, st_ctime_ns=301)
        api = SyntheticReadMetadata([good, bad])
        with mock.patch.object(g, 'windows_metadata_api', return_value=api), \
                contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(g.q.Refused, 'generated_native_snapshot_unstable'):
            g.read_owned_capture_snapshot(self.repo, 'command-0001/stdout.bin', 128, self.deadline)
        self.assertEqual(api.closed, [101])

    def test_snapshot_reader_length_mismatch_and_limit_never_return_a_snapshot(self):
        for raw, limit, reason in ((b'ab', 128, 'generated_file_identity_changed'),
                                   (b'abcd', 128, 'generated_file_identity_changed'),
                                   (b'abcd', 3, 'generated_file_oversize')):
            with self.subTest(raw=raw, limit=limit):
                (self.repo / 'command-0001/stdout.bin').write_bytes(raw)
                with mock.patch.object(g, 'windows_metadata_api', return_value=SyntheticReadMetadata()), \
                        contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(g.q.Refused, reason):
                    g.read_owned_capture_snapshot(self.repo, 'command-0001/stdout.bin', limit, self.deadline)

    def test_snapshot_reader_fixed_stream_scope_and_root_checks_remain_closed(self):
        api = SyntheticReadMetadata()
        with mock.patch.object(g, 'windows_metadata_api', return_value=api):
            for relative in ('result.json', '../command-0001/stdout.bin',
                             'command-0001/../stdout.bin', 'command-0001/stdout.bin:alternate',
                             'command-1/stdout.bin'):
                with self.subTest(relative=relative), contextlib.redirect_stdout(io.StringIO()), \
                        self.assertRaisesRegex(g.q.Refused, 'generated_native_path_kind_unsupported'):
                    g.read_owned_capture_snapshot(self.repo, relative, 128, self.deadline)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(g.q.Refused, 'generated_root_invalid'):
                g.read_owned_capture_snapshot(Path('relative'), 'command-0001/stdout.bin', 128, self.deadline)
        self.assertEqual(api.next_handle, 100)

    def test_snapshot_reader_does_not_hide_primary_failure_when_close_also_fails(self):
        api = SyntheticReadMetadata()
        primary = RuntimeError('synthetic query failure')
        api.record = mock.Mock(side_effect=primary)
        api.close = mock.Mock(side_effect=OSError('synthetic close failure'))
        with mock.patch.object(g, 'windows_metadata_api', return_value=api), \
                contextlib.redirect_stdout(io.StringIO()) as evidence, \
                self.assertRaises(RuntimeError) as caught:
            g.read_owned_capture_snapshot(self.repo, 'command-0001/stdout.bin', 128, self.deadline)
        self.assertIs(caught.exception, primary)
        self.assertEqual(api.close.call_args_list, [mock.call(101)])
        self.assertNotIn('synthetic query failure', evidence.getvalue())
        self.assertNotIn('synthetic close failure', evidence.getvalue())


if __name__ == '__main__':
    unittest.main()
