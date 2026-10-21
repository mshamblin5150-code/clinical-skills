"""Six real Windows fixtures; capability failures are errors, never skips."""
import os
from pathlib import Path
import platform
import tempfile
import time
import unittest
from unittest import mock

import generated_output_contract as g
from staging_retained_controls import make_link, unlink_native

REPORT_ROOT = None
DEADLINE = None


class NativeWindowsSnapshotControls(unittest.TestCase):
    def setUp(self):
        g.need(os.name == 'nt' and platform.python_version() == '3.14.4', 'windows_python_pin_required')
        g.need(isinstance(REPORT_ROOT, Path) and REPORT_ROOT.is_absolute()
               and type(DEADLINE) is float and time.monotonic() < DEADLINE,
               'snapshot_fixture_scope_invalid')
        g._safe_directory(REPORT_ROOT)
        holder = tempfile.TemporaryDirectory(prefix='native-snapshot-', dir=REPORT_ROOT)
        self.root = Path(holder.name).resolve()
        def cleanup():
            holder.cleanup()
            g.need(not os.path.lexists(self.root), 'snapshot_fixture_cleanup_failed')
        self.addCleanup(cleanup)
        patcher = mock.patch.object(g.q, 'emit')
        self.emit = patcher.start()
        self.addCleanup(patcher.stop)

    def read(self, name):
        return g.safe_read(self.root, name, 128, DEADLINE)

    def test_native_stable_bytecode_retains_exact_bytes(self):
        (self.root/'synthetic.pyc').write_bytes(b'synthetic bytecode fixture\x00\xff')
        self.assertEqual(self.read('synthetic.pyc'), b'synthetic bytecode fixture\x00\xff')

    def test_native_stable_json_retains_exact_bytes(self):
        (self.root/'synthetic.json').write_bytes(b'{"synthetic":true}\r\n')
        self.assertEqual(self.read('synthetic.json'), b'{"synthetic":true}\r\n')

    def test_native_hardlink_refuses_without_read_admission(self):
        target = self.root/'synthetic.pyc'
        target.write_bytes(b'synthetic')
        os.link(target, self.root/'second.pyc')
        with self.assertRaisesRegex(g.q.Refused, 'generated_file_unsafe'):
            self.read('synthetic.pyc')

    def test_native_junction_ancestor_refuses_and_target_is_unchanged(self):
        target = self.root/'target'
        target.mkdir()
        (target/'synthetic.pyc').write_bytes(b'synthetic')
        link = self.root/'junction'
        self.addCleanup(lambda: unlink_native(link, 'junction') if os.path.lexists(link) else None)
        kind = make_link(link, target)
        self.assertEqual(kind, 'junction')
        try:
            with self.assertRaisesRegex(g.q.Refused, 'generated_directory_unsafe'):
                self.read('junction/synthetic.pyc')
        finally:
            unlink_native(link, kind)
        self.assertEqual((target/'synthetic.pyc').read_bytes(), b'synthetic')

    def test_native_replacement_at_closed_boundary_refuses_same_bytes(self):
        target = self.root/'synthetic.pyc'
        replacement = self.root/'replacement.pyc'
        target.write_bytes(b'abc')
        replacement.write_bytes(b'abc')
        old = target.stat()
        os.utime(replacement, ns=(old.st_atime_ns, old.st_mtime_ns))
        original = g._open_readonly
        def replace_then_open(path):
            os.replace(replacement, target)
            return original(path)
        with mock.patch.object(g, '_open_readonly', side_effect=replace_then_open):
            with self.assertRaisesRegex(g.q.Refused, 'generated_file_identity_changed'):
                self.read('synthetic.pyc')
        comparisons = [call.kwargs for call in self.emit.call_args_list
                       if call.args == ('generated_file_comparison',)]
        self.assertTrue(any(row['stage'] == 'before_open' and not row['fields_equal']['st_ino']
                            for row in comparisons))
        self.assertEqual(target.read_bytes(), b'abc')

    def test_native_change_at_closed_boundary_refuses_restored_write_time(self):
        target = self.root/'synthetic.pyc'
        target.write_bytes(b'abc')
        old = target.stat()
        original = g._open_readonly
        def mutate_then_open(path):
            target.write_bytes(b'def')
            os.utime(target, ns=(old.st_atime_ns, old.st_mtime_ns))
            return original(path)
        with mock.patch.object(g, '_open_readonly', side_effect=mutate_then_open):
            with self.assertRaisesRegex(g.q.Refused, 'generated_file_identity_changed'):
                self.read('synthetic.pyc')
        comparisons = [call.kwargs for call in self.emit.call_args_list
                       if call.args == ('generated_file_comparison',)]
        self.assertTrue(any(row['stage'] == 'before_open'
                            and not row['fields_equal']['st_ctime_ns']
                            and row['fields_equal']['st_size'] and row['fields_equal']['st_mtime_ns']
                            for row in comparisons))
        self.assertEqual(target.read_bytes(), b'def')
