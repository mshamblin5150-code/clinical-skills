"""Public synthetic calibration behavior, never Windows qualification."""
import contextlib
import io
import os
from pathlib import Path
import tempfile
import time
import unittest
from dataclasses import replace

import compact_native_controls as controls
import compact_replacement_calibration as subject
from test_compact_native_controls import SharingNative


class CalibrationNative(SharingNative):
    """Real synthetic namespace changes and actual open descriptors.

    Stable synthetic birthtimes compensate for POSIX ctime not being birthtime.
    The model's denial is explicitly not a claim about native Windows.
    """
    def __init__(self):
        super().__init__()
        self.birthtimes, self.calls, self.last_error = {}, [], 0
        self.c.get_last_error = lambda: self.last_error
        self.kernel.MoveFileExW.call = self.move

    def record(self, handle):
        item = super().record(handle)
        birth = self.birthtimes.setdefault((item.st_dev, item.st_ino), item.st_birthtime_ns)
        return replace(item, st_birthtime_ns=birth)

    def move(self, source, destination, flags):
        self.calls.append((source, destination, flags))
        if any(row['path'] == Path(destination) for row in self.handles.values()):
            self.last_error = 5
            return 0
        os.replace(source, destination)
        return 1


class CalibrationTests(unittest.TestCase):
    def test_held_refusal_then_released_namespace_transition_is_explanatory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)/'fresh'
            native = CalibrationNative()
            api = controls.ObservedAPI(native)
            progress = {}
            row = subject.run_calibration(root, api, time.monotonic()+30, progress)
            self.assertEqual('verified', row['status'])
            self.assertEqual('access_5', row['held_error'])
            self.assertEqual('returned_true', row['released_call'])
            self.assertEqual('verified', row['namespace_transition'])
            self.assertFalse(row['native_control_qualified'])
            self.assertEqual(b'synthetic replacement must be denied\n', (root/'target.bin').read_bytes())
            self.assertFalse((root/'source.bin').exists())
            self.assertEqual(2, len(native.calls))
            self.assertEqual(native.calls[0], native.calls[1])
            self.assertEqual({}, api.handles)


class RouteTests(unittest.TestCase):
    def test_cli_selects_calibration_only_and_never_original_control(self):
        import json
        from unittest import mock
        import validate_compact_first_control as first
        import test_compact_first_control as fixtures
        for fails in (False, True):
            with self.subTest(fails=fails):
                harness = fixtures.FinalizationControls()
                args = harness.harness() + ['--replacement-calibration']
                harness.runtime.owners = []
                try:
                    def calibration(session, runtime, observer, progress):
                        progress.update(calibration_verified=not fails,
                            source_integrity_verified=True, receipt_verified=not fails)
                        if fails:
                            raise subject.CalibrationRefused()
                    with mock.patch.object(first, 'execute_calibration', calibration, create=True), \
                         mock.patch.object(first, 'execute', side_effect=AssertionError('original forbidden')), \
                         mock.patch.object(controls, 'run_control', side_effect=AssertionError('native control forbidden')):
                        self.assertEqual(2 if fails else 0, first.main(args))
                    row = json.loads(harness.stdout.getvalue().splitlines()[-1])
                    self.assertEqual('compact_replacement_calibration_summary', row['event'])
                    self.assertEqual('inconclusive' if fails else 'passed', row['status'])
                    self.assertTrue(row['calibration_only'])
                    self.assertFalse(row['native_control_qualified'])
                    self.assertEqual(0, row['native_owner_count'])
                    self.assertEqual(0, row['control_count'])
                finally:
                    harness.doCleanups()


class CloseBoundaryTests(unittest.TestCase):
    def test_unclosed_writer_stops_before_any_replacement(self):
        from unittest import mock
        original_open = Path.open
        opened = []
        class UnclosedWriter:
            def __init__(self, stream): self.stream = stream
            def __getattr__(self, name): return getattr(self.stream, name)
            def close(self): pass
        def unclosed(path, *args, **kwargs):
            stream = original_open(path, *args, **kwargs)
            opened.append(stream)
            return UnclosedWriter(stream)
        with tempfile.TemporaryDirectory() as tmp:
            native = CalibrationNative()
            api = controls.ObservedAPI(native)
            progress = {}
            try:
                with mock.patch.object(Path, 'open', unclosed), self.assertRaises(subject.CalibrationRefused):
                    subject.run_calibration(Path(tmp)/'new', api, time.monotonic()+30, progress)
                self.assertEqual('unknown', progress['calibration_witness']['cleanup'])
                self.assertEqual('not_attempted', progress['calibration_witness']['held_call'])
                self.assertEqual([], native.calls)
            finally:
                for stream in opened: stream.close()


class AdversarialTests(unittest.TestCase):
    def run_fixture(self, native, *, succeeds=False, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'fresh'
            api = controls.ObservedAPI(native)
            progress = {}
            with contextlib.redirect_stdout(io.StringIO()):
                if succeeds:
                    row = subject.run_calibration(root, api, time.monotonic()+30, progress, **kwargs)
                    self.assertEqual('verified', row['status'])
                else:
                    with self.assertRaises(Exception):
                        subject.run_calibration(root, api, time.monotonic()+30, progress, **kwargs)
                    self.assertEqual('failed', progress['calibration_witness']['status'])
                    self.assertNotEqual('verified', progress['calibration_witness']['namespace_transition'])
            self.assertFalse(native.disposed)
            self.assertLessEqual(len(native.calls), 2)
            return progress['calibration_witness']

    def test_positive_rename_allows_only_changetime_transition(self):
        for change, succeeds in (
            ({'st_ctime_ns': 900}, True), ({'st_mtime_ns': 900}, False),
            ({'st_birthtime_ns': 900}, False), ({'st_dev': 900}, False),
            ({'st_ino': 2**120+900}, False), ({'st_size': 36}, False),
            ({'st_file_attributes': 0x20}, False), ({'st_nlink': 2}, False),
            ({'reparse_tag': 0xA000000C}, False), ({'file_type': 2}, False),
            ({'delete_pending': True}, False), ({'st_mode': 0}, False)):
            with self.subTest(change=change):
                class Changed(CalibrationNative):
                    def record(self, handle):
                        row = super().record(handle)
                        return replace(row, **change) if len(self.calls) == 2 else row
                self.run_fixture(Changed(), succeeds=succeeds)

    def test_true_without_move_false_with_move_and_held_success_stop(self):
        for fault in ('no_transition', 'false_positive_move', 'held_success'):
            with self.subTest(fault=fault):
                class Changed(CalibrationNative):
                    def move(self, source, destination, flags):
                        if fault == 'held_success' or (fault == 'no_transition' and self.calls):
                            self.calls.append((source, destination, flags))
                            if fault == 'held_success': os.replace(source, destination)
                            return 1
                        result = super().move(source, destination, flags)
                        return 0 if fault == 'false_positive_move' and len(self.calls) == 2 else result
                native = Changed()
                row = self.run_fixture(native)
                self.assertEqual(1 if fault == 'held_success' else 2, len(native.calls))
                self.assertEqual('not_attempted' if fault == 'held_success' else
                    ('returned_false' if fault == 'false_positive_move' else 'returned_true'), row['released_call'])

    def test_held_path_identity_bytes_and_source_mutants_stop_before_release(self):
        for fault in ('target_same_bytes', 'source_bytes', 'source_missing', 'target_bytes'):
            with self.subTest(fault=fault):
                class Changed(CalibrationNative):
                    def move(self, source, destination, flags):
                        result = super().move(source, destination, flags)
                        if fault == 'target_same_bytes':
                            spare = Path(source).parent/'mutant'
                            spare.write_bytes(Path(destination).read_bytes())
                            os.replace(spare, destination)
                        elif fault == 'source_missing':
                            Path(source).rename(Path(source).with_name('moved-source'))
                        else:
                            Path(source if fault == 'source_bytes' else destination).write_bytes(b'X'*37)
                        return result
                native = Changed()
                row = self.run_fixture(native)
                self.assertEqual(1, len(native.calls))
                self.assertEqual('unknown', row['held_poststate'])
                self.assertEqual('not_attempted', row['released_call'])

    def test_source_presence_permission_and_missing_parent_refuse(self):
        for fault in ('present', 'permission', 'missing_parent'):
            with self.subTest(fault=fault):
                def missing(path):
                    if fault == 'present': return False
                    if fault == 'permission': raise PermissionError('PRIVATE_PERMISSION')
                    path.parent.rename(path.parent.with_name('moved-parent'))
                    return subject.sampled_missing(path)
                row = self.run_fixture(CalibrationNative(), missing=missing)
                self.assertEqual('returned_true', row['released_call'])
                self.assertEqual('unknown', row['namespace_transition'])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'dangling'
            path.symlink_to(Path(tmp)/'missing')
            self.assertFalse(subject.sampled_missing(path))

    def test_close_uncertainty_stops_before_next_challenge_and_never_retries(self):
        for when in ('preflight', 'authority', 'post_positive'):
            with self.subTest(when=when):
                class Changed(CalibrationNative):
                    def __init__(self):
                        super().__init__()
                        self.authority = None
                        self.faulted = []
                    def _open(self, path, kind):
                        handle = super()._open(path, kind)
                        if self.authority is None and Path(path).name == 'target.bin': self.authority = handle
                        return handle
                    def close(self, handle):
                        fail = (when == 'preflight' and not self.calls
                            or when == 'authority' and len(self.calls) == 1 and handle == self.authority
                            or when == 'post_positive' and len(self.calls) == 2)
                        super().close(handle)
                        if fail and not self.faulted:
                            self.faulted.append(handle)
                            raise OSError('PRIVATE_CLOSE_UNCERTAIN')
                native = Changed()
                row = self.run_fixture(native)
                self.assertEqual({'preflight': 0, 'authority': 1, 'post_positive': 2}[when], len(native.calls))
                self.assertEqual('unknown', row['cleanup'])
                self.assertEqual(1, len(native.faulted))

    def test_call_getter_and_observation_faults_preserve_original_exception(self):
        from unittest import mock
        for boundary in ('call', 'getter'):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as tmp:
                native = CalibrationNative()
                api = controls.ObservedAPI(native)
                primary = OSError('PRIVATE_PRIMARY')
                def fail(*args): raise primary
                class Broken(dict):
                    def __setitem__(self, key, value):
                        dict.__setitem__(self, key, {'status': 'verified'})
                        raise RuntimeError('PRIVATE_SECONDARY')
                obs = Broken()
                kwargs = {'move': fail} if boundary == 'call' else {'get_error': fail}
                with self.assertRaises(OSError) as caught:
                    subject.run_calibration(Path(tmp)/'new', api, time.monotonic()+30, obs, **kwargs)
                self.assertIs(primary, caught.exception)
                self.assertNotIn('calibration_witness', obs)
                self.assertEqual({}, api.handles)

    def test_existing_root_and_exhausted_deadline_never_create_or_challenge(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for deadline in (time.monotonic()+30, 0):
                native = CalibrationNative()
                progress = {}
                with self.assertRaises(Exception):
                    subject.run_calibration(root, controls.ObservedAPI(native), deadline, progress)
                self.assertEqual([], native.calls)
                self.assertEqual([], list(root.iterdir()))
                self.assertEqual('not_attempted', progress['calibration_witness']['held_call'])


class ReceiptAndTransportTests(unittest.TestCase):
    def test_encoded_receipt_boundary_pays_for_all_fixture_bytes(self):
        from types import SimpleNamespace
        from unittest import mock
        import validate_compact_first_control as first
        import json
        accounting = json.loads((Path(first.__file__).parent/'compact-replacement-calibration-accounting.json').read_text())
        for size, accepted in ((1048502, True), (1048503, False)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                session = SimpleNamespace(root=root, deadline=time.monotonic()+30)
                raw = b'{"p":"' + b'x'*(size-8) + b'"}'
                if accepted:
                    row = first.retain_calibration_receipt(session, raw)
                    self.assertEqual(1048502, row['receipt_bytes'])
                    self.assertEqual(row['receipt_bytes'], accounting['aggregate_receipt_max_bytes'])
                    self.assertTrue(row['receipt_verified'])
                    self.assertEqual(raw, (root/'replacement-calibration-validation.json').read_bytes())
                else:
                    with self.assertRaises(first.q.Refused): first.retain_calibration_receipt(session, raw)
                    self.assertEqual([], list(root.iterdir()))
        for name, value in (('AGGREGATE_BYTES', 1048503), ('FIXTURE_BYTES', 73)):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                session = SimpleNamespace(root=Path(tmp), deadline=time.monotonic()+30)
                with mock.patch.object(subject, name, value), self.assertRaises(first.q.Refused):
                    first.retain_calibration_receipt(session, b'{}')
                self.assertEqual([], list(Path(tmp).iterdir()))
        with tempfile.TemporaryDirectory() as tmp:
            native = CalibrationNative()
            original = native.move
            amounts = []
            def measured(source, destination, flags):
                amounts.append(sum(p.stat().st_size for p in Path(source).parent.iterdir()))
                return original(source, destination, flags)
            subject.run_calibration(Path(tmp)/'fixture', controls.ObservedAPI(native),
                                    time.monotonic()+30, {}, move=measured)
            self.assertEqual([74, 74], amounts)
            self.assertEqual(amounts[0], accounting['calibration_fixture_max_bytes'])
            self.assertEqual(1048576, 1048502 + amounts[0])

    def test_actual_cli_executes_only_calibration_and_retains_finite_result(self):
        import json
        from unittest import mock
        import validate_compact_first_control as first
        import test_compact_first_control as fixtures
        import test_compact_native_controls as native_fixtures
        for failed_close in (False, True):
            harness = fixtures.FinalizationControls()
            original_args = harness.harness()
            # The retained calibration-only route remains callable. The combined
            # property test now exercises the actual workflow-selected command.
            args = original_args + ['--replacement-calibration']
            try:
                observer = Path(args[args.index('--observer')+1])
                (observer/'diagnostics').mkdir()
                (observer/'diagnostics/compact-first-control-budget.json').write_text(json.dumps(first.BUDGET))
                harness.session.root = observer.parent/'source-captures'
                harness.session.root.mkdir()
                harness.session.deadline = 540
                native = CalibrationNative()
                if failed_close: native.failures.add(('close', 'source.bin'))
                runtime, _, _ = native_fixtures.NativePacketControls().runtime(native)
                runtime.work_deadline, runtime.hard_deadline = 540, 600
                runtime.clock = lambda: 0
                with mock.patch.object(first, 'execute', side_effect=AssertionError('original forbidden')), \
                     mock.patch.object(controls, 'run_control', side_effect=AssertionError('control forbidden')), \
                     mock.patch.object(first, 'make_runtime', return_value=runtime), \
                     mock.patch.object(first.q, 'first_clean'), \
                     mock.patch.object(first.q, 'raw_source_inventory', return_value={'synthetic': 'inventory'}), \
                     mock.patch.object(first, 'validate_core_pins'), \
                     mock.patch.object(first.q, 'verify_sources'), \
                     mock.patch.dict(os.environ, {'GITHUB_SHA': 'a'*40}):
                    self.assertEqual(2 if failed_close else 0, first.main(args), harness.stdout.getvalue())
                row = json.loads(harness.stdout.getvalue().splitlines()[-1])
                self.assertEqual('compact_replacement_calibration_summary', row['event'])
                self.assertEqual('inconclusive' if failed_close else 'passed', row['status'])
                self.assertEqual(0, row['native_owner_count'])
                self.assertFalse(row['native_control_qualified'])
                self.assertFalse(row['controls_verified'])
                self.assertEqual('unknown' if failed_close else 'verified', row['calibration_witness']['cleanup'])
                self.assertEqual(0 if failed_close else 2, len(native.calls))
                self.assertLessEqual(len(harness.stdout.getvalue().splitlines(keepends=True)[-1].encode()), 4096)
                self.assertNotIn('PRIVATE', harness.stdout.getvalue())
                if not failed_close:
                    retained = json.loads((harness.session.root/'replacement-calibration-validation.json').read_bytes())
                    self.assertEqual('verified', retained['calibration']['namespace_transition'])
                    self.assertEqual(b'synthetic replacement must be denied\n',
                        (observer.parent/'replacement-calibration/target.bin').read_bytes())
            finally:
                harness.doCleanups()

    def test_true_returns_do_not_read_stale_error_and_false_release_never_passes(self):
        native = CalibrationNative()
        calls = []
        def getter():
            calls.append(len(native.calls))
            if len(native.calls) != 1: raise AssertionError('stale getter')
            return 5
        with tempfile.TemporaryDirectory() as tmp:
            row = subject.run_calibration(Path(tmp)/'new', controls.ObservedAPI(native),
                                         time.monotonic()+30, {}, get_error=getter)
            self.assertEqual('verified', row['status'])
            self.assertEqual([1], calls)
        for error in (0, 5, 32, 999):
            with self.subTest(error=error):
                native = CalibrationNative()
                original = native.move
                def refused(source, target, flags):
                    if native.calls:
                        native.calls.append((source, target, flags))
                        return 0
                    return original(source, target, flags)
                with tempfile.TemporaryDirectory() as tmp:
                    progress = {}
                    with self.assertRaises(subject.CalibrationRefused):
                        subject.run_calibration(Path(tmp)/'new', controls.ObservedAPI(native),
                            time.monotonic()+30, progress, move=refused, get_error=lambda: error)
                    self.assertEqual('returned_false', progress['calibration_witness']['released_call'])
                    self.assertEqual('unknown', progress['calibration_witness']['namespace_transition'])


class ProjectionTests(unittest.TestCase):
    def test_incomplete_success_claims_remain_unknown_and_private_values_are_removed(self):
        import json
        for row in ({'status': 'verified'}, {'status': 'verified', 'namespace_transition': 'verified'},
                    {'status': 'PRIVATE', 'held_error': 'PRIVATE', 'held_call': [], 'cleanup': {}}, {}):
            projected = subject.calibration_witness(row)
            self.assertIsNone(projected['status'])
            self.assertNotIn('PRIVATE', json.dumps(projected))
            self.assertIsNone(projected['namespace_transition'])
        projected = subject.calibration_witness({'status': 'not_attempted'})
        self.assertEqual('not_attempted', projected['status'])

    def test_full_success_witness_survives_actual_public_terminal_transport(self):
        import json
        import validate_compact_first_control as first
        with tempfile.TemporaryDirectory() as tmp:
            row = subject.run_calibration(Path(tmp)/'fresh', controls.ObservedAPI(CalibrationNative()),
                                          time.monotonic()+30, {})
        output = io.StringIO()
        public = first.reader.PublicOutput(output)
        public.terminal = True
        with contextlib.redirect_stdout(public):
            first.emit_terminal('compact_replacement_calibration_summary', status='passed',
                calibration_only=True, native_control_qualified=False, calibration_witness=row,
                controls_verified=False, control_count=0, native_owner_count=0,
                process_cleanup_verified=True, hard_budget_verified=True)
        delivered = json.loads(output.getvalue())
        self.assertEqual('verified', delivered['calibration_witness']['status'])
        self.assertEqual('access_5', delivered['calibration_witness']['held_error'])
        self.assertEqual('returned_true', delivered['calibration_witness']['released_call'])
        self.assertLessEqual(len(json.dumps(row).encode()), 2048)
        self.assertLessEqual(len(output.getvalue().encode()), 4096)


class AccountingRelationTests(unittest.TestCase):
    def test_every_accounting_field_mutation_is_rejected(self):
        import json
        from unittest import mock
        path = Path(subject.__file__).with_name('compact-replacement-calibration-accounting.json')
        original = Path.read_text
        values = json.loads(original(path))
        for field in values:
            def altered(target, *args, **kwargs):
                text = original(target, *args, **kwargs)
                if target == path:
                    row = json.loads(text)
                    row[field] = 999
                    return json.dumps(row)
                return text
            with self.subTest(field=field), mock.patch.object(Path, 'read_text', altered):
                with self.assertRaises(AssertionError):
                    self.test_complete_accounting_matches_executed_route_and_existing_ceiling()

    def test_complete_accounting_matches_executed_route_and_existing_ceiling(self):
        import ast
        import inspect
        import json
        from types import SimpleNamespace
        import validate_compact_first_control as first
        import test_compact_native_controls as fixtures
        directory = Path(first.__file__).parent
        accounting = json.loads((directory/'compact-replacement-calibration-accounting.json').read_text())
        existing = json.loads((directory/'compact-first-control-accounting.json').read_text())
        budget = json.loads((directory/'compact-first-control-budget.json').read_text())
        native = CalibrationNative()
        original_move = native.move
        peak_sizes = []
        def measured_move(source, destination, flags):
            peak_sizes.append(sum(path.stat().st_size for path in Path(source).parent.iterdir()))
            return original_move(source, destination, flags)
        native.kernel.MoveFileExW.call = measured_move
        runtime, _, _ = fixtures.NativePacketControls().runtime(native)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            progress = {}
            row = first.perform_calibration(root, runtime, progress)
            self.assertEqual('verified', row['namespace_transition'])
            self.assertEqual('access_5', row['held_error'])
            self.assertEqual([74, 74], peak_sizes)
            receipts = root/'receipts'
            receipts.mkdir()
            session = SimpleNamespace(root=receipts, deadline=time.monotonic()+30)
            # Bound the actual encoded write/readback, not a copied cap constant.
            aggregate_size = 1024 * 1024 - max(peak_sizes)
            raw = b'{"p":"' + b'x'*(aggregate_size-8) + b'"}'
            receipt = first.retain_calibration_receipt(session, raw)
            self.assertTrue(receipt['receipt_verified'])
            self.assertEqual(raw, (receipts/'replacement-calibration-validation.json').read_bytes())
            with self.assertRaises(first.q.Refused):
                first.retain_calibration_receipt(session, raw+b' ')
            self.assertTrue(runtime.cleanup())
        # Read the success-source predicate actually enforced by this route.
        # Its independent protocol is first-clean3 + two inventory/verify passes6.
        source_counts = [node.comparators[0].value
            for node in ast.walk(ast.parse(inspect.getsource(first.execute_calibration)))
            if isinstance(node, ast.Compare) and len(node.comparators) == 1
            and ast.unparse(node.left) == 'len(session.owners)'
            and isinstance(node.ops[0], ast.Eq)
            and isinstance(node.comparators[0], ast.Constant)]
        self.assertEqual([15], source_counts)
        work, hard = first.budget_deadlines(1000, 1000, 0)
        pairs = budget['max_source_commands'] + budget['native_commands']
        streams_per_pair = existing['conservative_streams'] // existing['conservative_capture_pairs']
        private = existing['private_content_bytes'] + max(peak_sizes) + receipt['receipt_bytes'] - 1024*1024
        self.assertEqual({
            'aggregate_receipt_max_bytes': receipt['receipt_bytes'],
            'calibration_fixture_max_bytes': max(peak_sizes),
            'calibration_native_owned_commands': len(runtime.owners),
            'calibration_capture_disposition_calls': sum(api.mark_count for api in runtime.apis),
            'calibration_replacement_attempts': len(native.calls),
            'conservative_capture_pairs_ceiling': pairs,
            'conservative_streams_ceiling': pairs * streams_per_pair,
            'including_public_content_bytes_ceiling': private + first.reader.BUDGET['max_receipt_bytes'],
            'private_content_bytes_ceiling': private,
            'source_success_commands': source_counts[0],
            'work_seconds': work,
            'cleanup_seconds': hard - work,
            'total_job_seconds': hard,
        }, accounting)
