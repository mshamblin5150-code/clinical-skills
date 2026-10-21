"""Portable behavioral controls for the approved Windows metadata boundary."""
import dataclasses
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import generated_output_contract as g


class WindowsMetadataControls(unittest.TestCase):
    def test_consistent_change_time_accepts_without_using_creation_time(self):
        # Native values deliberately differ: creation=100, change=200.
        native = dict(st_dev=7, st_ino=(1 << 100)+11, st_mode=0o100666,
                      st_nlink=1, st_size=3, st_mtime_ns=150,
                      st_ctime_ns=200, st_file_attributes=32,
                      st_birthtime_ns=100, file_type=1, reparse_tag=0,
                      delete_pending=False)
        api = mock.Mock()
        api.record.side_effect = [g.WindowsSnapshot(**native), g.WindowsSnapshot(**native)]
        result = g.windows_snapshot(api, 123, 128, 'synthetic.pyc', time.monotonic()+30)
        self.assertEqual(result.st_ctime_ns, 200)
        self.assertEqual(result.st_birthtime_ns, 100)
        self.assertEqual(api.record.call_count, 2)

    def test_unsafe_complete_native_records_refuse(self):
        good = g.WindowsSnapshot(7, 11, 0o100666, 1, 3, 150, 200, 32, 100, 1, 0, False)
        for changes in ({'st_nlink': 2}, {'file_type': 2}, {'file_type': 3},
                        {'file_type': 0}, {'reparse_tag': 1}, {'st_file_attributes': 0x400},
                        {'delete_pending': True}, {'st_mode': 0o040777},
                        {'st_size': -1}, {'st_size': 129}):
            with self.subTest(changes=changes):
                bad = dataclasses.replace(good, **changes)
                api = mock.Mock(record=mock.Mock(return_value=bad))
                with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
                    g.windows_snapshot(api, 123, 128, 'synthetic.pyc', time.monotonic()+30)

    def test_read_boundary_uses_two_path_checks_and_original_read_fd(self):
        good = g.WindowsSnapshot(7, 11, 0o100666, 1, 3, 150, 200, 32, 100, 1, 0, False)
        api = mock.Mock()
        api.open.side_effect = [101, 102]
        api.from_fd.return_value = 103
        api.record.return_value = good
        with tempfile.TemporaryDirectory() as name:
            path = Path(name)/'synthetic.pyc'
            path.write_bytes(b'abc')
            raw, before = g.read_windows(path, 128, 'synthetic.pyc', time.monotonic()+30, api)
        self.assertEqual(raw, b'abc')
        self.assertEqual(before, good)
        self.assertEqual(api.open.call_count, 2)
        self.assertEqual(api.close.call_args_list, [mock.call(101), mock.call(102)])
        self.assertEqual([call.args[0] for call in api.record.call_args_list],
                         [101, 101, 103, 103, 103, 103, 102, 102])

    def test_primary_query_failure_survives_path_close_failure(self):
        primary = PermissionError('PRIVATE query')
        api = mock.Mock()
        api.open.return_value = 101
        api.record.side_effect = primary
        api.close.side_effect = OSError('PRIVATE close')
        with mock.patch.object(g.q, 'emit') as emit:
            with self.assertRaises(PermissionError) as caught:
                g.read_windows(Path('/synthetic.pyc'), 128, 'synthetic.pyc', time.monotonic()+30, api)
        self.assertIs(caught.exception, primary)
        self.assertEqual(api.close.call_count, 1)
        self.assertNotIn('PRIVATE', repr(emit.call_args_list))
        self.assertTrue(any(call.kwargs.get('verified') is False for call in emit.call_args_list))

    def test_native_adapter_preserves_documented_fields_and_exact_open_policy(self):
        kernel = mock.Mock()
        kernel.CreateFileW.return_value = 101
        kernel.CloseHandle.return_value = 1
        kernel.GetFileType.return_value = 1
        def query(handle, kind, pointer, size):
            item = pointer._obj
            if kind == 0:
                item.CreationTime = 116444736000000001
                item.LastWriteTime = 116444736000000002
                item.ChangeTime = 116444736000000003
                item.FileAttributes = 32
                self.assertEqual(size, 40)
            elif kind == 1:
                item.EndOfFile = 3
                item.NumberOfLinks = 1
                self.assertEqual(size, 24)
            elif kind == 9:
                item.FileAttributes = 32
                self.assertEqual(size, 8)
            elif kind == 18:
                item.VolumeSerialNumber = 7
                item.FileId[0] = 11
                item.FileId[15] = 1
                self.assertEqual(size, 24)
            else:
                self.fail('Unexpected native information class')
            return 1
        kernel.GetFileInformationByHandleEx.side_effect = query
        api = g.WindowsMetadataAPI(kernel)
        handle = api.open(Path('/synthetic.pyc'))
        sample = api.record(handle)
        api.close(handle)
        self.assertEqual((sample.st_birthtime_ns, sample.st_mtime_ns, sample.st_ctime_ns), (100, 200, 300))
        self.assertEqual(sample.st_ino, (1 << 120)+11)
        self.assertEqual(sample.st_mode, 0o100666)
        self.assertEqual(kernel.CreateFileW.call_args.args[1:],
                         (0x80000000, 1, None, 3, 0x00200000 | 0x08000000, None))
        self.assertEqual(kernel.CloseHandle.call_args_list, [mock.call(101)])

    def test_safe_read_selects_consistent_windows_adapter_and_preserves_bytes(self):
        good = g.WindowsSnapshot(7, 11, 0o100666, 1, 3, 150, 200, 32, 100, 1, 0, False)
        api = mock.Mock()
        api.open.side_effect = [101, 102]
        api.from_fd.return_value = 103
        api.record.return_value = good
        with tempfile.TemporaryDirectory() as name:
            repo = Path(name).resolve()
            (repo/'synthetic.pyc').write_bytes(b'abc')
            with mock.patch.object(g, 'windows_metadata_api', return_value=api, create=True):
                self.assertEqual(g.safe_read(repo, 'synthetic.pyc', 128, time.monotonic()+30), b'abc')
        self.assertEqual(api.open.call_count, 2)

    def test_failed_read_handle_transfer_and_close_preserve_primary(self):
        import ctypes
        import sys
        from types import SimpleNamespace
        kernel = mock.Mock()
        kernel.CreateFileW.return_value = 101
        kernel.GetFileInformationByHandleEx.return_value = 1
        kernel.CloseHandle.return_value = 0
        primary = OSError('PRIVATE transfer')
        runtime = SimpleNamespace(open_osfhandle=mock.Mock(side_effect=primary))
        with mock.patch.object(g.os, 'name', 'nt'), \
             mock.patch.object(g.os, 'O_BINARY', 0, create=True), \
             mock.patch.object(ctypes, 'WinDLL', return_value=kernel, create=True), \
             mock.patch.dict(sys.modules, {'msvcrt': runtime}), mock.patch.object(g.q, 'emit') as emit:
            with self.assertRaises(OSError) as caught:
                g._open_readonly('synthetic.pyc')
        self.assertIs(caught.exception, primary)
        self.assertEqual(kernel.CloseHandle.call_args_list, [mock.call(101)])
        self.assertTrue(any(call.kwargs.get('verified') is False for call in emit.call_args_list))
        self.assertNotIn('PRIVATE', repr(emit.call_args_list))

    def test_creation_only_change_has_explicit_bounded_evidence(self):
        good = g.WindowsSnapshot(7, 11, 0o100666, 1, 3, 150, 200, 32, 100, 1, 0, False)
        changed = dataclasses.replace(good, st_birthtime_ns=101)
        api = mock.Mock()
        api.open.return_value = 101
        api.from_fd.return_value = 103
        api.record.side_effect = [good, good, changed, changed]
        with tempfile.TemporaryDirectory() as name:
            path = Path(name)/'synthetic.pyc'; path.write_bytes(b'abc')
            with mock.patch.object(g.q, 'emit') as emit, self.assertRaises(g.q.Refused):
                g.read_windows(path, 128, 'synthetic.pyc', time.monotonic()+30, api)
        self.assertTrue(any(call.args == ('generated_creation_comparison',)
                            and call.kwargs.get('creation_equal') is False for call in emit.call_args_list))

    def specimen(self):
        return g.WindowsSnapshot(7, (1 << 100)+11, 0o100666, 1, 3, 150, 200, 32, 100, 1, 0, False)

    def read_fixture(self, api, *, content=b'abc', limit=128):
        with tempfile.TemporaryDirectory() as name:
            repo = Path(name).resolve()
            (repo/'synthetic.pyc').write_bytes(content)
            with mock.patch.object(g, 'windows_metadata_api', return_value=api):
                return g.safe_read(repo, 'synthetic.pyc', limit, time.monotonic()+30)

    def fake_api(self, records=None):
        api = mock.Mock()
        api.open.side_effect = [101, 102]
        api.from_fd.return_value = 103
        api.record.side_effect = records
        if records is None:
            api.record.return_value = self.specimen()
        return api

    def test_each_dimension_changed_at_each_observation_boundary_refuses(self):
        good = self.specimen()
        for field in (*g.METADATA_FIELDS, 'st_birthtime_ns'):
            for start in (2, 4, 6):
                with self.subTest(field=field, start=start):
                    change = 1 << 120 if field == 'st_ino' else 1
                    bad = dataclasses.replace(good, **{field: getattr(good, field)+change})
                    records = [good]*8
                    records[start:start+2] = [bad, bad]
                    api = self.fake_api(records)
                    with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
                        self.read_fixture(api)
                    self.assertEqual(api.close.call_count, 2 if start == 6 else 1)

    def test_change_time_detects_equal_size_and_restored_write_time(self):
        good = self.specimen()
        changed = dataclasses.replace(good, st_ctime_ns=201)
        api = self.fake_api([good]*4 + [changed]*2)
        with mock.patch.object(g.q, 'emit') as emit, self.assertRaises(g.q.Refused):
            self.read_fixture(api)
        comparisons = [c.kwargs for c in emit.call_args_list if c.args == ('generated_file_comparison',)]
        self.assertEqual(comparisons[-1]['unequal_fields'], ['st_ctime_ns'])
        self.assertEqual(comparisons[-1]['stage'], 'before_after')

    def test_native_repeat_mismatch_refuses_without_retry(self):
        good = self.specimen()
        for field in (*g.METADATA_FIELDS, 'st_birthtime_ns'):
            with self.subTest(field=field):
                bad = dataclasses.replace(good, **{field: getattr(good, field)+1})
                api = self.fake_api([good, bad, good, good])
                with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
                    self.read_fixture(api)
                self.assertEqual(api.record.call_count, 2)
                self.assertEqual(api.close.call_args_list, [mock.call(101)])

    def test_query_failure_at_every_record_closes_owned_path_handles(self):
        good = self.specimen()
        for index in range(8):
            with self.subTest(index=index):
                api = self.fake_api([good]*index + [PermissionError('PRIVATE metadata')])
                with mock.patch.object(g.q, 'emit') as emit, self.assertRaises(g.q.Refused):
                    self.read_fixture(api)
                self.assertEqual(api.close.call_args_list,
                                 [mock.call(101)] + ([mock.call(102)] if index >= 6 else []))
                self.assertNotIn('PRIVATE', repr(emit.call_args_list))

    def test_missing_api_never_falls_back_to_python_mixed_metadata(self):
        with mock.patch.object(g, 'windows_metadata_api', side_effect=AttributeError('missing API')), \
             mock.patch.object(g, '_open_readonly') as opened:
            with tempfile.TemporaryDirectory() as name, self.assertRaises(AttributeError):
                g.safe_read(Path(name).resolve(), 'synthetic.pyc', 128, time.monotonic()+30)
        opened.assert_not_called()

    def test_path_open_failure_does_not_close_an_unowned_handle(self):
        api = self.fake_api()
        api.open.side_effect = PermissionError('PRIVATE sharing')
        with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
            self.read_fixture(api)
        api.close.assert_not_called()

    def test_close_failure_alone_refuses_and_is_not_retried(self):
        for which in (1, 2):
            with self.subTest(which=which):
                api = self.fake_api()
                api.close.side_effect = ([None] if which == 2 else []) + [OSError('PRIVATE close')]
                with mock.patch.object(g.q, 'emit') as emit, self.assertRaisesRegex(g.q.Refused, 'generated_handle_cleanup_failed'):
                    self.read_fixture(api)
                self.assertEqual(api.close.call_count, which)
                self.assertNotIn('PRIVATE', repr(emit.call_args_list))

    def test_fdopen_failure_closes_fd_exactly_once(self):
        api = self.fake_api()
        with mock.patch.object(g, '_open_readonly', return_value=777), \
             mock.patch.object(g.os, 'fdopen', side_effect=OSError('PRIVATE fdopen')), \
             mock.patch.object(g.os, 'close') as close, mock.patch.object(g.q, 'emit'), \
             self.assertRaises(g.q.Refused):
            self.read_fixture(api)
        self.assertEqual(close.call_args_list.count(mock.call(777)), 1)
        self.assertEqual(api.close.call_args_list, [mock.call(101)])

    def test_read_failure_and_stream_close_failure_keep_primary(self):
        api = self.fake_api()
        stream = mock.Mock()
        primary = RuntimeError('PRIVATE read')
        stream.read.side_effect = primary
        stream.close.side_effect = OSError('PRIVATE close')
        with mock.patch.object(g, '_open_readonly', return_value=777), \
             mock.patch.object(g.os, 'fdopen', return_value=stream), \
             mock.patch.object(g.q, 'emit') as emit, self.assertRaises(RuntimeError) as caught:
            self.read_fixture(api)
        self.assertIs(caught.exception, primary)
        stream.close.assert_called_once()
        self.assertEqual(api.close.call_args_list, [mock.call(101)])
        self.assertNotIn('PRIVATE', repr(emit.call_args_list))

    def test_read_length_and_limit_refuse_even_with_stable_metadata(self):
        for content, limit in ((b'ab', 128), (b'abcd', 128), (b'abcde', 3)):
            with self.subTest(content=content, limit=limit), mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
                self.read_fixture(self.fake_api(), content=content, limit=limit)

    def test_expired_deadline_prevents_path_handle_creation(self):
        api = self.fake_api()
        with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
            g.read_windows(Path('/synthetic.pyc'), 128, 'synthetic.pyc', time.monotonic()-1, api)
        api.open.assert_not_called()

    def test_unsupported_extension_cannot_get_simplified_mode_mapping(self):
        api = self.fake_api()
        with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
            g.read_windows(Path('/synthetic.exe'), 128, 'synthetic.exe', time.monotonic()+30, api)
        api.open.assert_not_called()

    def test_malformed_native_record_refuses_without_public_payload(self):
        good = self.specimen()
        for bad in (None, dataclasses.replace(good, st_size=True), dataclasses.replace(good, delete_pending=1)):
            api = self.fake_api([bad, bad])
            with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
                self.read_fixture(api)

    def test_deadline_between_records_stops_without_second_query(self):
        api = self.fake_api()
        with mock.patch.object(g.time, 'monotonic', side_effect=[1, 3]), \
             mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
            g.windows_snapshot(api, 123, 128, 'synthetic.pyc', 2)
        self.assertEqual(api.record.call_count, 1)

    def test_native_query_failure_and_invalid_open_have_no_fallback(self):
        kernel = mock.Mock()
        kernel.GetFileInformationByHandleEx.return_value = 0
        api = g.WindowsMetadataAPI(kernel)
        with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
            api.record(101)
        self.assertEqual(kernel.GetFileInformationByHandleEx.call_count, 1)
        for invalid in (None, api.c.c_void_p(-1).value):
            kernel.CreateFileW.return_value = invalid
            with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
                api.open('synthetic.pyc')
        kernel.CloseHandle.assert_not_called()
        kernel.CloseHandle.return_value = 0
        with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
            api.close(101)
        kernel.CloseHandle.assert_called_once_with(101)

    def test_native_readonly_mode_and_attribute_disagreement(self):
        kernel = mock.Mock()
        kernel.GetFileType.return_value = 1
        disagree = False
        def query(handle, kind, pointer, size):
            item = pointer._obj
            if kind == 0:
                item.FileAttributes = 33
            elif kind == 1:
                item.NumberOfLinks = 1
            elif kind == 9:
                item.FileAttributes = 32 if disagree else 33
            return 1
        kernel.GetFileInformationByHandleEx.side_effect = query
        api = g.WindowsMetadataAPI(kernel)
        sample = api.record(101)
        self.assertEqual(sample.st_mode, 0o100444)
        disagree = True
        with mock.patch.object(g.q, 'emit'), self.assertRaises(g.q.Refused):
            api.record(101)

    def test_stream_close_failure_after_success_refuses(self):
        api = self.fake_api()
        stream = mock.Mock()
        stream.read.return_value = b'abc'
        stream.close.side_effect = OSError('PRIVATE close')
        with mock.patch.object(g, '_open_readonly', return_value=777), \
             mock.patch.object(g.os, 'fdopen', return_value=stream), \
             mock.patch.object(g.q, 'emit'), self.assertRaisesRegex(g.q.Refused, 'generated_handle_cleanup_failed'):
            self.read_fixture(api)
        stream.close.assert_called_once()
        self.assertEqual(api.open.call_count, 1)

    def test_final_path_replacement_with_same_bytes_times_is_refused(self):
        good = self.specimen()
        replaced = dataclasses.replace(good, st_ino=good.st_ino+(1 << 120))
        api = self.fake_api([good]*6+[replaced]*2)
        with mock.patch.object(g.q, 'emit') as emit, self.assertRaises(g.q.Refused):
            self.read_fixture(api)
        rows = [c.kwargs for c in emit.call_args_list if c.args == ('generated_file_comparison',)]
        self.assertEqual(rows[-1]['stage'], 'after_final')
        self.assertEqual(rows[-1]['unequal_fields'], ['st_ino'])
        self.assertEqual(api.close.call_args_list, [mock.call(101), mock.call(102)])


if __name__ == '__main__':
    unittest.main()
