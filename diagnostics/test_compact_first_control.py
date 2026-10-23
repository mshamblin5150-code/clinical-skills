import contextlib
import io
import json
import tempfile
import math
import unittest
from pathlib import Path
from unittest import mock

import validate_compact_first_control as subject
import compact_native_controls as native
import measure_lazy_suite_ids as q


class FirstControlTests(unittest.TestCase):
    def test_fixed_first_control_has_one_owner_and_no_nested_work(self):
        from test_compact_native_controls import NativePacketControls, SharingNative
        runtime, _, _ = NativePacketControls().runtime(SharingNative())
        progress = {}
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            rows = subject.perform_controls(Path(temporary).resolve(), runtime, progress)
        self.assertEqual([native.CONTROL_IDS[0]], [row['id'] for row in rows])
        self.assertEqual(1, len(runtime.owners))
        self.assertEqual(0, runtime.nested_command_slots)
        self.assertEqual(1, progress['control_count'])
        self.assertIsNone(progress['failed_control'])
        self.assertTrue(runtime.cleanup())

    def test_injected_failure_uses_real_projection_and_terminal_transport(self):
        output = io.StringIO()
        public = subject.reader.PublicOutput(output)
        with contextlib.redirect_stdout(public), mock.patch.object(native, 'run_control', side_effect=AssertionError('native forbidden')):
            result = subject.failure_emission_control()
        row = json.loads(output.getvalue())
        self.assertEqual('compact_first_failure_emission_control', row['event'])
        self.assertEqual('inconclusive', row['status'])
        self.assertEqual('injected_exception_only', row['evidence_kind'])
        self.assertFalse(row['native_control_qualified'])
        self.assertEqual('control_proof_failed', row['failure']['reason'])
        self.assertEqual('prepare', row['failure_witness']['phase'])
        self.assertEqual('not_returned', row['failure_witness']['outcome_state'])
        self.assertIsNone(row['failure_witness']['outcome'])
        self.assertEqual('unknown', row['failure_witness']['overall_retention'])
        self.assertNotIn('PRIVATE', output.getvalue())
        self.assertLessEqual(len(output.getvalue().encode()), 4096)
        self.assertEqual({'verified': True, 'native_control_qualified': False}, result)
        self.assertFalse(public.terminal)


class BudgetControls(unittest.TestCase):
    def test_setup_is_charged_and_cleanup_reserve_cannot_be_borrowed(self):
        self.assertEqual((461.0, 521.0), subject.budget_deadlines(1000, 1079, 0))
        with self.assertRaises(q.Refused):
            subject.admit_controls(359.9, 0)
        subject.admit_controls(360, 0)


class RouteControls(unittest.TestCase):
    def test_only_first_push_of_dedicated_workflow_is_admitted(self):
        env = dict(GITHUB_ACTIONS='true', GITHUB_EVENT_NAME='push',
                   GITHUB_REF='refs/heads/diagnostic/2013-parallel-proof-20261020',
                   GITHUB_RUN_ATTEMPT='1', GITHUB_SHA='a' * 40, GITHUB_RUN_ID='123',
                   GITHUB_WORKFLOW='synthetic compact first control')
        subject.authorize_route('nt', '3.14.4', env)
        for key, value in [('GITHUB_RUN_ATTEMPT', '2'), ('GITHUB_EVENT_NAME', 'workflow_dispatch'),
                           ('GITHUB_WORKFLOW', 'fixed historical reader compact parallel comparison')]:
            with self.subTest(key=key), self.assertRaises(q.Refused):
                subject.authorize_route('nt', '3.14.4', {**env, key: value})
        with self.assertRaises(q.Refused):
            subject.authorize_route('posix', '3.14.4', env)

    def test_budget_rejects_nonfinite_future_and_consumed_origins(self):
        for origin, now in [(float('nan'), 1000), (1001, 1000), (0, 540)]:
            with self.subTest(origin=origin), self.assertRaises(q.Refused):
                subject.budget_deadlines(origin, now, 0)

    def test_actual_free_space_refusal_does_not_credit_planned_disposal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            observer = root / 'observer'
            observer.mkdir()
            admission = subject.VolumeAdmission(root, observer)
            with mock.patch.object(subject.shutil, 'disk_usage', return_value=mock.Mock(free=4 * 1024**3)):
                admission.check()
            self.assertEqual([4294967296, 4294967296], admission.minimum_free)
            with mock.patch.object(subject.shutil, 'disk_usage', return_value=mock.Mock(free=4 * 1024**3 - 1)):
                with self.assertRaisesRegex(q.Refused, '^native_storage_reserve_exhausted$'):
                    admission.check()


class PublicBoundaryControls(unittest.TestCase):
    def test_cli_refusals_and_failed_terminal_output_never_print_private_exception(self):
        import contextlib, io, json
        for argv in ([], ['--job-start-epoch', 'PRIVATE_ARGUMENT_SENTINEL']):
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(2, subject.main(argv))
            self.assertNotIn('PRIVATE_ARGUMENT_SENTINEL', stdout.getvalue() + stderr.getvalue())
            self.assertNotIn('Traceback', stdout.getvalue() + stderr.getvalue())
            self.assertEqual('inconclusive', json.loads(stdout.getvalue())['status'])
        with mock.patch.object(q, 'emit', side_effect=OSError('PRIVATE_PUBLICATION_SENTINEL')):
            self.assertEqual(2, subject.main([]))

    def test_pinned_implementation_cannot_be_replaced_by_new_commit_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / 'diagnostics').mkdir()
            pins = (Path(subject.__file__).parent / 'compact-native-source-pins.json').read_bytes()
            (root / 'diagnostics/compact-native-source-pins.json').write_bytes(pins)
            import json
            original = json.loads(pins)['files']
            subject.validate_core_pins(root, original)
            with self.assertRaisesRegex(q.Refused, '^cleared_implementation_changed$'):
                subject.validate_core_pins(root, {**original, 'diagnostics/compact_capture_native.py': '0' * 64})


class FinalizationControls(unittest.TestCase):
    def harness(self, emit=None, execute_error=None, clean=True):
        import contextlib, io, time
        from types import SimpleNamespace
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        temporary = self.stack.enter_context(tempfile.TemporaryDirectory())
        observer = Path(temporary).resolve() / 'observer'
        observer.mkdir()
        self.session = SimpleNamespace(owners=[None] * 15, cleanup=mock.Mock(return_value=clean))
        self.runtime = SimpleNamespace(owners=[None], nested_command_slots=0,
                                      cleanup=mock.Mock(return_value=True))
        self.clock = [0.0]
        identity = {'python':'3.14.4','image':{'RUNNER_OS':'Windows','RUNNER_ARCH':'X64'}}
        for target, name, value in ((subject, 'authorize_route', lambda *args: None),
            (q, 'environment_preflight', lambda: None), (q, 'corpus_preflight', lambda *args: None),
            (subject.maintainer, 'environment_identity', lambda: identity),
            (subject, 'VolumeAdmission', lambda *args: mock.Mock(check=lambda: None, minimum_free=[4*1024**3, 4*1024**3])),
            (subject, 'make_session', lambda *args: self.session),
            (subject, 'make_runtime', lambda *args: self.runtime),
            (subject.time, 'monotonic', lambda: self.clock[0]),
            (subject.time, 'time', lambda: 1000.0)):
            self.stack.enter_context(mock.patch.object(target, name, value))
        def execute(session, runtime, observer, progress):
            if execute_error:
                progress['stage'] = 'controls'
                raise execute_error
            progress.update(source_integrity_verified=True, controls_verified=True,
                receipt_verified=True, receipt_sha256='a' * 64, control_count=1)
        self.stack.enter_context(mock.patch.object(subject, 'execute', execute))
        if emit:
            self.stack.enter_context(mock.patch.object(q, 'emit', emit))
        self.stdout, self.stderr = io.StringIO(), io.StringIO()
        self.stack.enter_context(contextlib.redirect_stdout(self.stdout))
        self.stack.enter_context(contextlib.redirect_stderr(self.stderr))
        return ['--observer', str(observer), '--job-start-epoch', '1000']

    def test_success_requires_both_cleanup_receipts_and_no_private_stderr(self):
        import json
        args = self.harness()
        self.assertEqual(0, subject.main(args))
        self.session.cleanup.assert_called_once()
        self.runtime.cleanup.assert_called_once()
        self.assertEqual('', self.stderr.getvalue())
        self.assertEqual('passed', json.loads(self.stdout.getvalue().splitlines()[-1])['status'])

    def test_primary_failure_survives_cleanup_and_terminal_emission_failure(self):
        events = []
        def emit(event, **fields):
            events.append((event, fields))
            if event == 'compact_first_summary':
                raise OSError('PRIVATE_PUBLICATION_SENTINEL')
        args = self.harness(emit, q.Refused('native_consumer_control_failed'), clean=False)
        self.assertEqual(2, subject.main(args))
        self.session.cleanup.assert_called_once()
        self.runtime.cleanup.assert_called_once()
        self.assertEqual({'stage':'controls','reason':'native_consumer_control_failed'}, events[-1][1]['failure'])
        self.assertEqual('', self.stderr.getvalue())

    def test_terminal_publication_crossing_hard_deadline_cannot_return_success(self):
        events = []
        def emit(event, **fields):
            events.append((event, fields))
            if event == 'compact_first_summary':
                self.clock[0] = 601
        args = self.harness(emit)
        self.assertEqual(2, subject.main(args))
        self.assertEqual(1, sum(name == 'compact_first_summary' for name, _ in events))
        self.session.cleanup.assert_called_once()
        self.runtime.cleanup.assert_called_once()


class FirstStatusOwnershipControls(unittest.TestCase):
    def test_dirty_status_diagnostics_cannot_launch_after_unknown_prior_owner(self):
        import contextlib, io, time
        from test_compact_native_controls import SyntheticOwners
        from test_compact_capture_retention import FakeNative
        for fault in (None, 'launch', 'poll', 'finish', 'cancel'):
            broken = fault is not None
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                repo, captures = root / 'observer', root / 'captures'
                (repo / '.git').mkdir(parents=True)
                captures.mkdir()
                factory, api, events = SyntheticOwners(), FakeNative(), []
                def start(argv, **kwargs):
                    ordinal = len(factory.owners) + 1
                    raw = {1: b'.git\n', 2: b'a' * 40 + b'\n',
                           3: b'?? synthetic-fixture\n'}.get(ordinal, b'')
                    kwargs['report_dir'] = Path(kwargs['report_dir'])
                    owner = factory.start(['fixture', raw.hex(), '', '0' if ordinal <= 3 else '1'], **kwargs)
                    if broken and ordinal == 4:
                        owner.cancel = mock.Mock(side_effect=OSError('PRIVATE_CANCEL_SENTINEL'))
                        if fault == 'launch':
                            error = OSError('PRIVATE_LAUNCH_SENTINEL')
                            error.owner = owner
                            raise error
                        if fault == 'poll':
                            owner.poll = mock.Mock(side_effect=OSError('PRIVATE_POLL_SENTINEL'))
                        if fault == 'finish':
                            owner.finish = mock.Mock(side_effect=OSError('PRIVATE_FINISH_SENTINEL'))
                    return owner
                def read(root, relative, limit, deadline):
                    with (root / relative).open('rb') as stream:
                        return stream.read(), api.record(stream.fileno())
                resource_refused = [False]
                def check():
                    if fault == 'cancel' and len(factory.owners) == 4 and not resource_refused[0]:
                        resource_refused[0] = True
                        raise q.Refused('native_storage_reserve_exhausted')
                session = subject.SourceSession(captures, time.monotonic()+30, time.monotonic()+90,
                                                 mock.Mock(check=check))
                with mock.patch.object(q, 'WindowsJobProbe', mock.Mock(start=start)), \
                     mock.patch.object(subject.contract, 'read_owned_capture_snapshot', read), \
                     mock.patch.object(q, 'emit', lambda event, **fields: events.append((event, fields))):
                    with self.assertRaisesRegex(q.Refused, '^first_status_not_clean$'):
                        q.first_clean(session, repo, 'a' * 40, 'observer')
                self.assertEqual(4 if broken else 6, len(factory.owners))
                self.assertEqual(len(factory.owners), len(session.owners))
                self.assertEqual(not broken, session.cleanup())
                self.assertEqual('first_status_config', events[-1][0])
                self.assertEqual({'core.autocrlf': 'unavailable' if broken else 'unset',
                                  'core.eol': 'unavailable' if broken else 'unset',
                                  'core.safecrlf': 'unavailable' if broken else 'unset'},
                                 events[-1][1]['effective_values'])
                self.assertNotIn('PRIVATE_', repr(events))
                self.assertEqual(b'?? synthetic-fixture\n', (captures/'command-0003/stdout.bin').read_bytes())
                if broken:
                    self.assertEqual(2 if fault in ('launch', 'cancel') else 1,
                                     factory.owners[3].cancel.call_count)

    def test_each_unverified_prior_owner_dimension_refuses_before_launch(self):
        import time
        from dataclasses import replace
        from test_compact_native_controls import SyntheticOwners
        mutations = ({'cleanup_verified': False}, {'root_reaped': False},
                     {'active_processes': 1}, {'state': 'running'})
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                factory = SyntheticOwners()
                owner = factory.start(['fixture', '', '', '0'], cwd=root, env={},
                                      report_dir=root/'command-0001')
                original = owner.finish(1)
                owner.result = replace(original, snapshot=replace(original.snapshot, **mutation))
                session = subject.SourceSession(root, time.monotonic()+30, time.monotonic()+90,
                                                 mock.Mock(check=lambda: None))
                session.owners.append(owner)
                with mock.patch.object(q, 'WindowsJobProbe') as launch:
                    with self.assertRaisesRegex(q.Refused, '^native_previous_owner_unverified$'):
                        session.run(['git', '-C', str(root), 'config', '--get', 'core.eol'], root)
                launch.start.assert_not_called()
                self.assertEqual([owner], session.owners)


class FailureWitnessControls(unittest.TestCase):
    def test_retirement_failure_keeps_inner_outcome_before_cleanup(self):
        import contextlib, io
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        api = SharingNative()
        api.failures.add(('mark', 'stderr.bin'))
        runtime, _, _ = NativePacketControls().runtime(api)
        progress = {'failed_control': None, 'control_count': 0}
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(native.ControlError, '^control_proof_failed$'):
                subject.perform_controls(Path(temporary).resolve(), runtime, progress)
            witness = progress['failure_witness']
            self.assertEqual('snapshot_share_receipt_success', witness['control'])
            self.assertEqual('retirement_proof', witness['phase'])
            self.assertEqual('returned', witness['outcome_state'])
            self.assertEqual('compact_disposition_failed', witness['outcome']['reason'])
            self.assertEqual(['verified', 'uncertain'], [row['mark'] for row in witness['outcome']['streams']])
            self.assertEqual('unknown', witness['outcome']['retention'])
            self.assertEqual('not_attempted', witness['reconstruction'])
            self.assertEqual(1, len(runtime.owners))
            self.assertEqual(0, progress['control_count'])
            self.assertTrue(runtime.cleanup())

    def test_receipt_reconstruction_failure_keeps_successful_inner_result_but_unknown_overall(self):
        import contextlib, io
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        api = SharingNative()
        api.read_fail_at = ('compact-000001-terminal.json', 2)
        runtime, _, _ = NativePacketControls().runtime(api)
        progress = {'failed_control': None, 'control_count': 0}
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(native.ControlError, '^control_proof_failed$'):
                subject.perform_controls(Path(temporary).resolve(), runtime, progress)
            witness = progress['failure_witness']
            self.assertEqual('receipt_reconstruction', witness['phase'])
            self.assertEqual(True, witness['outcome']['complete'])
            self.assertEqual(None, witness['outcome']['reason'])
            self.assertEqual(['verified', 'verified'], [row['mark'] for row in witness['outcome']['streams']])
            self.assertEqual('unknown', witness['reconstruction'])
            self.assertEqual('unknown', witness['overall_retention'])
            self.assertEqual({'kind': 'terminal', 'phase': 'bytes_proof', 'reason': 'control_proof_failed', 'close': 'verified'},
                             witness['receipt_observation'])
            self.assertTrue(runtime.cleanup())

    def test_first_control_failure_matrix_preserves_finite_retirement_and_authority_boundary(self):
        import contextlib, io, json
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        class FaultNative(SharingNative):
            def __init__(self, fault):
                super().__init__()
                self.fault = fault
                if fault == 'first_mark': self.failures.add(('mark', 'stdout.bin'))
                if fault == 'authority_delete': self.kernel.DeleteFileW.call = lambda *args: 1
            def read(self, handle, limit, deadline):
                name = self.handles[handle]['path'].name
                if (self.fault == 'eligibility' and name.endswith('-eligibility.json')
                    or self.fault == 'outcome' and name.endswith('-outcome.json')
                    or self.fault == 'terminal' and name.endswith('-terminal.json')
                    or self.fault == 'authority_recheck' and name.endswith('-eligibility.json')
                       and len(self.disposed) == 2):
                    raise OSError('PRIVATE_CAPTURE_PATH_AND_PAYLOAD_SENTINEL')
                return super().read(handle, limit, deadline)
            def close(self, handle):
                # Target the original post-disposition authority close, not a
                # new temporary observer sharing its pathname before marks.
                if (self.fault == 'authority_close' and len(self.disposed) == 2
                        and self.handles[handle]['path'].name.endswith('-eligibility.json')):
                    self.failures.add(('close', 'compact-000001-eligibility.json'))
                return super().close(handle)
        for fault, reason, marks, authority_phase in (
            ('eligibility', 'compact_eligibility_receipt_failed', ['not_requested', 'not_requested'], 'not_attempted'),
            ('first_mark', 'compact_disposition_failed', ['uncertain', 'not_requested'], 'readback'),
            ('authority_delete', 'compact_disposition_failed', ['uncertain', 'not_requested'], 'delete'),
            ('outcome', 'compact_outcome_receipt_failed', ['verified', 'verified'], 'binding'),
            ('authority_recheck', 'compact_authority_recheck_failed', ['verified', 'verified'], 'binding'),
            ('authority_close', 'compact_authority_close_failed', ['verified', 'verified'], 'binding'),
            ('terminal', 'compact_terminal_receipt_failed', ['verified', 'verified'], 'binding'),
        ):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
                runtime, _, _ = NativePacketControls().runtime(FaultNative(fault))
                progress = {'failed_control': None, 'control_count': 0}
                with self.assertRaisesRegex(native.ControlError, '^control_proof_failed$'):
                    subject.perform_controls(Path(temporary).resolve(), runtime, progress)
                witness = progress['failure_witness']
                self.assertEqual(reason, witness['outcome']['reason'])
                self.assertEqual(marks, [row['mark'] for row in witness['outcome']['streams']])
                self.assertEqual(authority_phase, witness['authority_phase'])
                self.assertEqual('unknown', witness['overall_retention'])
                self.assertNotIn('PRIVATE_', json.dumps(witness))
                self.assertLessEqual(len(json.dumps(witness).encode()), 4096)
                self.assertEqual(1, len(runtime.owners))
                runtime.cleanup()

    def test_no_retirement_result_is_not_fabricated_as_unmarked(self):
        import contextlib, io
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        api = SharingNative()
        api.failures.add(('open', 'stdout.bin'))
        runtime, _, _ = NativePacketControls().runtime(api)
        progress = {'failed_control': None, 'control_count': 0}
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(PermissionError):
                subject.perform_controls(Path(temporary).resolve(), runtime, progress)
            self.assertEqual('read_share', progress['failure_witness']['phase'])
            self.assertEqual('not_returned', progress['failure_witness']['outcome_state'])
            self.assertIsNone(progress['failure_witness']['outcome'])
            self.assertEqual('unknown', progress['failure_witness']['overall_retention'])
            self.assertTrue(runtime.cleanup())

    def test_malformed_outcome_cannot_publish_private_value_or_change_primary_exception(self):
        import contextlib, io, json
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        sentinel = 'PRIVATE_PATH_PAYLOAD_SECRET_SENTINEL'
        for field, value in (('reason', sentinel), ('receipt_files', {'eligibility': sentinel}),
                             ('streams', [sentinel]), ('pair', sentinel), ('extra', sentinel)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
                runtime, _, _ = NativePacketControls().runtime(SharingNative())
                progress = {'failed_control': None, 'control_count': 0}
                original = native.retention.CompactStore.retire
                def malformed(store, *args):
                    result = original(store, *args)
                    result.update(complete=False, **{field: value})
                    return result
                with mock.patch.object(native.retention.CompactStore, 'retire', malformed):
                    with self.assertRaisesRegex(native.ControlError, '^control_proof_failed$'):
                        subject.perform_controls(Path(temporary).resolve(), runtime, progress)
                witness = progress['failure_witness']
                self.assertEqual('invalid', witness['outcome_state'])
                self.assertIsNone(witness['outcome'])
                self.assertNotIn(sentinel, json.dumps(witness))
                self.assertTrue(runtime.cleanup())

    def test_cli_primary_witness_survives_failed_cleanup_and_failed_publication(self):
        import json
        from test_compact_native_controls import NativePacketControls, SharingNative
        for fail_publication in (False, True):
            with self.subTest(fail_publication=fail_publication):
                harness = FinalizationControls()
                args = harness.harness(clean=False)
                try:
                    api = SharingNative()
                    api.failures.add(('mark', 'stderr.bin'))
                    runtime, _, _ = NativePacketControls().runtime(api)
                    runtime.clock = lambda: harness.clock[0]
                    cleanup = runtime.cleanup
                    runtime.cleanup = mock.Mock(side_effect=cleanup)
                    events = []
                    original_emit = q.emit
                    def emit(event, **fields):
                        events.append((event, fields))
                        if event == 'compact_first_summary' and fail_publication:
                            raise OSError('PRIVATE_TERMINAL_PUBLICATION_SENTINEL')
                        original_emit(event, **fields)
                    def execute(session, runtime, observer, progress):
                        progress['stage'] = 'controls'
                        subject.perform_controls(observer.parent, runtime, progress)
                    with mock.patch.object(subject, 'make_runtime', return_value=runtime), \
                         mock.patch.object(subject, 'execute', execute), mock.patch.object(q, 'emit', emit):
                        self.assertEqual(2, subject.main(args))
                    terminal = [row for event, row in events if event == 'compact_first_summary']
                    self.assertEqual(1, len(terminal))
                    self.assertLessEqual(len(json.dumps({'event': 'compact_first_summary', **terminal[0]}).encode()), 4096)
                    self.assertEqual({'stage': 'controls', 'reason': 'control_proof_failed'}, terminal[0]['failure'])
                    self.assertEqual(False, terminal[0]['process_cleanup_verified'])
                    self.assertEqual('compact_disposition_failed', terminal[0]['failure_witness']['outcome']['reason'])
                    self.assertEqual(['verified', 'uncertain'],
                        [row['mark'] for row in terminal[0]['failure_witness']['outcome']['streams']])
                    self.assertEqual(1, len(runtime.owners))
                    runtime.cleanup.assert_called_once()
                    harness.session.cleanup.assert_called_once()
                    self.assertNotIn('PRIVATE_', harness.stdout.getvalue() + harness.stderr.getvalue())
                    self.assertNotIn('Traceback', harness.stdout.getvalue() + harness.stderr.getvalue())
                finally:
                    harness.doCleanups()

    def test_containing_invocation_proof_failure_stays_inconclusive(self):
        import contextlib, io
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        runtime, _, _ = NativePacketControls().runtime(SharingNative())
        progress = {'failed_control': None, 'control_count': 0}
        original = native.reconstruct_retention
        def wrong_uncontained(*args, **kwargs):
            if not kwargs.get('invocation_complete'):
                return 'disposition_verified'
            return original(*args, **kwargs)
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()), \
             mock.patch.object(native, 'reconstruct_retention', wrong_uncontained):
            with self.assertRaisesRegex(native.ControlError, '^control_proof_failed$'):
                subject.perform_controls(Path(temporary).resolve(), runtime, progress)
            witness = progress['failure_witness']
            self.assertEqual('missing_invocation_proof', witness['phase'])
            self.assertEqual(True, witness['outcome']['complete'])
            self.assertEqual('disposition_verified', witness['reconstruction'])
            self.assertEqual('unknown', witness['overall_retention'])
            self.assertEqual(2, witness['authority_callbacks'])
            self.assertEqual(True, witness['same_authority'])
            self.assertTrue(runtime.cleanup())

    def test_reconstruction_primary_read_fault_survives_secondary_close_fault(self):
        import contextlib, io
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        class FaultNative(SharingNative):
            def read(self, handle, limit, deadline):
                name = self.handles[handle]['path'].name
                if name.endswith('-terminal.json') and self.reads.get(name, 0) == 1:
                    self.failures.add(('close', name))
                    raise OSError('PRIVATE_READ_PRIMARY_SENTINEL')
                return super().read(handle, limit, deadline)
        runtime, _, _ = NativePacketControls().runtime(FaultNative())
        progress = {'failed_control': None, 'control_count': 0}
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(native.ControlError, '^control_proof_failed$'):
                subject.perform_controls(Path(temporary).resolve(), runtime, progress)
            self.assertEqual({'kind': 'terminal', 'phase': 'read',
                              'reason': 'receipt_operation_unavailable', 'close': 'uncertain'},
                             progress['failure_witness']['receipt_observation'])
            self.assertTrue(progress['failure_witness']['outcome']['complete'])
            self.assertEqual('unknown', progress['failure_witness']['overall_retention'])
            self.assertFalse(runtime.cleanup())

    def test_complete_retirement_cannot_hide_failed_same_authority_proof(self):
        import contextlib, io
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        runtime, _, _ = NativePacketControls().runtime(SharingNative())
        progress = {'failed_control': None, 'control_count': 0}
        def bypass_callback(api, handle):
            api.native.mark_delete(handle)
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()), \
             mock.patch.object(native.ObservedAPI, 'mark_delete', bypass_callback):
            with self.assertRaisesRegex(native.ControlError, '^control_proof_failed$'):
                subject.perform_controls(Path(temporary).resolve(), runtime, progress)
            witness = progress['failure_witness']
            self.assertEqual(True, witness['outcome']['complete'])
            self.assertEqual('retirement_proof', witness['phase'])
            self.assertEqual(0, witness['authority_callbacks'])
            self.assertIsNone(witness['same_authority'])
            self.assertEqual('unknown', witness['overall_retention'])
            self.assertTrue(runtime.cleanup())

    def test_finite_witness_fits_existing_terminal_reserve_and_is_detached(self):
        import contextlib, io, json
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        runtime, _, _ = NativePacketControls().runtime(SharingNative())
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            result = native.run_control('snapshot_share_receipt_success', Path(temporary).resolve() / 'new', runtime)
            result['outcome']['reason'] = max(native.retention.REASONS, key=len)
            result['outcome']['pair'] = native.retention.MAX_PAIRS
            witness = native.failure_witness(runtime)
            self.assertEqual('returned', witness['outcome_state'])
            self.assertLessEqual(len(json.dumps(witness).encode()), 2048)
            self.assertEqual({'recheck': 'verified', 'close': 'verified'}, witness['outcome']['receipt_authority'])
            result['outcome']['streams'][0]['mark'] = 'PRIVATE_LATE_MUTATION_SENTINEL'
            self.assertEqual('verified', witness['outcome']['streams'][0]['mark'])
            self.assertNotIn('PRIVATE_', json.dumps(witness))
            self.assertTrue(runtime.cleanup())

    def test_entered_reconstruction_exception_is_unknown_not_unattempted(self):
        import contextlib, io, json
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        runtime, _, _ = NativePacketControls().runtime(SharingNative())
        progress = {'failed_control': None, 'control_count': 0}
        primary = OSError('PRIVATE_RECONSTRUCTION_SENTINEL')
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()), \
             mock.patch.object(native, 'reconstruct_retention', side_effect=primary):
            with self.assertRaises(OSError) as caught:
                subject.perform_controls(Path(temporary).resolve(), runtime, progress)
            self.assertIs(primary, caught.exception)
            witness = progress['failure_witness']
            self.assertEqual('receipt_reconstruction', witness['phase'])
            self.assertEqual('unknown', witness['reconstruction'])
            self.assertEqual(True, witness['outcome']['complete'])
            self.assertEqual('unknown', witness['overall_retention'])
            self.assertEqual(['verified', 'verified'], [row['mark'] for row in witness['outcome']['streams']])
            self.assertNotIn('PRIVATE_', json.dumps(witness))
            self.assertEqual(1, len(runtime.owners))
            self.assertTrue(runtime.cleanup())

    def test_projector_exception_cannot_replace_original_control_exception(self):
        import contextlib, io
        from test_compact_native_controls import NativePacketControls, SharingNative
        import compact_native_controls as native
        api = SharingNative()
        api.failures.add(('mark', 'stderr.bin'))
        runtime, _, _ = NativePacketControls().runtime(api)
        progress = {'failed_control': None, 'control_count': 0, 'failure_witness': None}
        original_run, original_errors = native.run_control, []
        def remember_original(*args):
            try:
                return original_run(*args)
            except BaseException as error:
                original_errors.append(error)
                raise
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()), \
             mock.patch.object(native, 'run_control', remember_original), \
             mock.patch.object(native, 'failure_witness', side_effect=OSError('PRIVATE_PROJECTOR_SENTINEL')):
            with self.assertRaises(BaseException) as caught:
                subject.perform_controls(Path(temporary).resolve(), runtime, progress)
            self.assertEqual(1, len(original_errors))
            self.assertIs(original_errors[0], caught.exception)
            self.assertEqual('control_proof_failed', subject.reason(caught.exception))
            self.assertIsNone(progress['failure_witness'])
            self.assertEqual(0, progress['control_count'])
            self.assertEqual(1, len(runtime.owners))
            self.assertTrue(runtime.cleanup())


class DedicatedRouteControls(unittest.TestCase):
    def test_exact_route_and_all_other_workflows_are_held(self):
        directory = Path(subject.__file__).parent.parent / '.github/workflows'
        active = []
        for path in directory.glob('*.yml'):
            text = path.read_text()
            if "branches-ignore: ['**']" not in text:
                active.append(path.name)
            else:
                self.assertIn("tags-ignore: ['**']", text)
        self.assertEqual(['ci-compact-first-control.yml'], active)
        text = (directory / active[0]).read_text()
        self.assertIn('branches: [diagnostic/2013-parallel-proof-20261020]', text)
        self.assertIn('github.run_attempt == 1', text)
        self.assertIn('validate_compact_first_control.py', text)
        self.assertNotIn('validate_compact_native.py', text)
        self.assertNotIn('workflow_dispatch', text)
        self.assertNotIn('upload-artifact', text)
        self.assertIn('timeout-minutes: 10', text)
        self.assertIn("python-version: '3.14.4'", text)
        self.assertLess(text.index('PROOF_JOB_START_EPOCH='), text.index('uses: actions/checkout'))

    def test_authentication_precedes_self_control_and_native_never_follows_failed_emission(self):
        from types import SimpleNamespace
        import time
        events = []
        session = SimpleNamespace(deadline=time.monotonic()+500, root=Path('/unused/source'), owners=[None]*15)
        observer = Path(subject.__file__).parent.parent
        def record(name, result=None):
            def invoke(*args, **kwargs):
                events.append(name)
                return result
            return invoke
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.dict(subject.os.environ, {'GITHUB_SHA':'a'*40}))
            for module, name, result in ((q,'first_clean',None),(q,'raw_source_inventory',{}),
                (subject,'validate_core_pins',None),(q,'verify_sources',None)):
                stack.enter_context(mock.patch.object(module, name, record(name,result)))
            failure = OSError('PRIVATE_TRANSPORT_FAILURE')
            stack.enter_context(mock.patch.object(subject, 'emit_terminal', side_effect=failure))
            run = stack.enter_context(mock.patch.object(native, 'run_control'))
            progress = {}
            with self.assertRaises(OSError) as caught:
                subject.execute(session, object(), observer, progress)
            self.assertIs(failure, caught.exception)
            run.assert_not_called()
        self.assertEqual(['first_clean','raw_source_inventory','validate_core_pins','verify_sources'], events)
        self.assertTrue(progress['source_integrity_verified'])
        self.assertEqual('failure_emission_control', progress['stage'])
        self.assertNotIn('controls_verified', progress)

    def test_failed_authentication_never_enters_self_control(self):
        from types import SimpleNamespace
        with mock.patch.dict(subject.os.environ, {'GITHUB_SHA':'a'*40}), \
             mock.patch.object(q, 'first_clean', side_effect=q.Refused('first_status_not_clean')), \
             mock.patch.object(subject, 'failure_emission_control') as emission:
            with self.assertRaises(q.Refused):
                subject.execute(SimpleNamespace(), object(), Path('.'), {})
            emission.assert_not_called()

    def test_first_runtime_refuses_any_second_or_nested_owner_before_launch(self):
        from types import SimpleNamespace
        admission = SimpleNamespace(check=lambda: None)
        runtime = subject.make_runtime(100, 160, admission)
        with mock.patch.object(native.ControlRuntime, 'start_owned') as start:
            runtime.owners.append(object())
            with self.assertRaises(q.Refused):
                runtime.start_owned([], Path('.'))
            runtime.owners.clear()
            runtime.nested_command_slots = 1
            with self.assertRaises(q.Refused):
                runtime.start_owned([], Path('.'))
            start.assert_not_called()

    def test_terminal_cap_matches_actual_json_transport_and_failure_is_not_success(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaises(q.Refused):
                subject.emit_terminal('compact_first_summary', private='x'*4096)
        self.assertEqual('', output.getvalue())
        class ShortSink:
            def write(self, text): return 0
            def flush(self): pass
        public = subject.reader.PublicOutput(ShortSink())
        with contextlib.redirect_stdout(public), self.assertRaises(q.Refused):
            subject.failure_emission_control()
        self.assertTrue(public.failed)

    def test_projection_fault_refuses_self_control_instead_of_qualifying_native(self):
        with mock.patch.object(native, 'failure_witness', side_effect=OSError('PRIVATE_PROJECTOR')):
            with self.assertRaisesRegex(q.Refused, '^native_control_receipt_invalid$'):
                subject.failure_emission_control()

    def test_accounting_is_bound_to_route_budget_and_control_source(self):
        import ast
        import inspect
        from test_compact_native_controls import NativePacketControls, SharingNative
        directory = Path(subject.__file__).parent
        budget = json.loads((directory/'compact-first-control-budget.json').read_text())
        self.assertEqual(subject.BUDGET, budget)
        accounting = json.loads((directory/'compact-first-control-accounting.json').read_text())
        runtime, _, _ = NativePacketControls().runtime(SharingNative())
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            root = Path(temporary).resolve()
            rows = subject.perform_controls(root, runtime, {})
            control = root / rows[0]['id']
            replacement_bytes = (control/'receipt-replacement.bin').stat().st_size
            captures = list((control/'command-0001').glob('*.bin'))
            payload_bytes = sum(path.stat().st_size for path in captures)
            receipt_count = len(list(control.glob('compact-*.json')))
            self.assertTrue(runtime.cleanup())
        self.assertEqual(1, len(rows))
        self.assertEqual(1, len(runtime.owners))
        self.assertEqual(2, len(captures))
        self.assertEqual(3, receipt_count)
        # Read the driver's enforced success-source ledger predicate, not a
        # second accounting constant. The expected 15 is also the independently
        # reviewed source protocol: first status 3 + two inventory/verify passes 6.
        source_predicates = [node.comparators[0].value
            for node in ast.walk(ast.parse(inspect.getsource(subject.execute)))
            if isinstance(node, ast.Compare) and len(node.comparators) == 1
            and ast.unparse(node.left) == 'len(session.owners)'
            and isinstance(node.ops[0], ast.Eq)
            and isinstance(node.comparators[0], ast.Constant)]
        self.assertEqual([15], source_predicates)
        source_commands = source_predicates[0]
        native_commands = sum(row['owned_commands'] for row in rows)
        self.assertEqual(native_commands, budget['native_commands'])
        self.assertEqual(receipt_count, budget['max_compact_receipts'])
        pairs = budget['max_source_commands'] + native_commands
        raw = pairs * len(captures) * budget['max_capture_bytes']
        private = raw + receipt_count * budget['max_compact_receipt_bytes'] + 1024**2 + 65536 + payload_bytes + replacement_bytes
        self.assertEqual({
            'conservative_capture_pairs': pairs,
            'conservative_streams': pairs * len(captures),
            'including_public_content_bytes': private + subject.reader.BUDGET['max_receipt_bytes'],
            'native_owned_commands': native_commands,
            'nested_reserved_slots': runtime.nested_command_slots,
            'private_content_bytes': private,
            'raw_content_bytes': raw,
            'success_capture_pairs': source_commands + native_commands,
            'success_source_commands': source_commands,
        }, accounting)
        spec = (directory/'compact-first-control-spec.md').read_text()
        self.assertIn(f'{replacement_bytes}-byte `receipt-replacement.bin`', spec)
        self.assertIn(f'{private:,} bytes', spec)
        self.assertIn(f"{private + subject.reader.BUDGET['max_receipt_bytes']:,} bytes", spec)

    def test_every_accounting_field_mutation_is_rejected(self):
        path = Path(subject.__file__).parent/'compact-first-control-accounting.json'
        original = Path.read_text
        accounting = json.loads(original(path))
        for field in accounting:
            def altered(target, *args, **kwargs):
                text = original(target, *args, **kwargs)
                if target == path:
                    row = json.loads(text)
                    row[field] += 1
                    return json.dumps(row)
                return text
            with self.subTest(field=field), mock.patch.object(Path, 'read_text', altered):
                with self.assertRaises(AssertionError):
                    self.test_accounting_is_bound_to_route_budget_and_control_source()

    def test_expired_deadline_never_enters_the_fixed_control(self):
        import time
        runtime = mock.Mock(work_deadline=time.monotonic()-1)
        with mock.patch.object(native, 'run_control') as run, self.assertRaises(q.Refused):
            subject.perform_controls(Path('.'), runtime, {})
        run.assert_not_called()

    def test_original_full_workflow_identity_is_refused_by_new_driver(self):
        env = dict(GITHUB_ACTIONS='true', GITHUB_EVENT_NAME='push', GITHUB_REF=subject.BRANCH,
            GITHUB_WORKFLOW='synthetic compact native validation', GITHUB_RUN_ATTEMPT='1',
            GITHUB_SHA='a'*40, GITHUB_RUN_ID='123')
        with self.assertRaises(q.Refused):
            subject.authorize_route('nt', '3.14.4', env)
