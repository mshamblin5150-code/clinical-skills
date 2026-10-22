import unittest
from unittest import mock
from pathlib import Path
import tempfile
import math
import validate_compact_native as subject
import measure_lazy_suite_ids as q

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
                   GITHUB_WORKFLOW='synthetic compact native validation')
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

if __name__ == '__main__':
    unittest.main()

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

class IntegratedPortableControls(unittest.TestCase):
    def test_driver_executes_exact_native_and_consumer_population_with_one_owner_ledger(self):
        import contextlib, io, json, time
        from test_compact_native_controls import NativePacketControls, SharingNative, SyntheticCoordinatorOwners
        runtime, _, _ = NativePacketControls().runtime(SharingNative())
        runtime.owner_factory = SyntheticCoordinatorOwners()
        runtime.environment = {}
        runtime.terminate_coordinator = lambda owner: setattr(owner, 'stopped', True)
        progress = {'failed_control': None, 'control_count': 0}
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()) as output:
            rows = subject.perform_controls(Path(temporary).resolve(), runtime, progress)
            self.assertEqual(18, len(rows))
            self.assertTrue(all(0 <= row['wall_seconds'] <= 540 for row in rows))
            self.assertEqual(35, sum(row['owned_commands'] for row in rows))
            self.assertEqual(34, len(runtime.owners))
            self.assertEqual(1, runtime.nested_command_slots)
            self.assertTrue(runtime.cleanup())
            self.assertEqual(18, progress['control_count'])
            self.assertIsNone(progress['failed_control'])
            public = [json.loads(line) for line in output.getvalue().splitlines()]
            self.assertEqual(18, sum(row['event'] == 'compact_native_control' for row in public))

    def test_expired_work_never_starts_a_control(self):
        import time
        runtime = mock.Mock(work_deadline=time.monotonic() - 1, owners=[], nested_command_slots=0)
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(q.Refused, '^global_budget_exhausted$'):
            subject.perform_controls(Path(temporary).resolve(), runtime, {})
        runtime.resource_check.assert_not_called()

    def test_workflow_is_single_synthetic_route_with_original_budget(self):
        root = Path(subject.__file__).parent.parent
        text = (root / '.github/workflows/ci-compact-native.yml').read_text()
        self.assertIn('timeout-minutes: 10', text)
        self.assertIn("python-version: '3.14.4'", text)
        self.assertLess(text.index('PROOF_JOB_START_EPOCH='), text.index('uses: actions/checkout'))
        self.assertNotIn('source-seed', text)
        self.assertNotIn('tools/suite.py', text)
        for name in ('ci-current-parallel', 'ci-threshold-module', 'ci-reader-attribution',
                     'ci-parallel-proof', 'ci-checkpoint-discovery'):
            held = (root / '.github/workflows' / (name + '.yml')).read_text()
            self.assertIn("branches-ignore: ['**']", held)
            self.assertIn("tags-ignore: ['**']", held)

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
        self.runtime = SimpleNamespace(owners=[None] * 34, nested_command_slots=1,
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
                receipt_verified=True, receipt_sha256='a' * 64, control_count=18)
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
            if event == 'compact_native_summary':
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
            if event == 'compact_native_summary':
                self.clock[0] = 601
        args = self.harness(emit)
        self.assertEqual(2, subject.main(args))
        self.assertEqual(1, sum(name == 'compact_native_summary' for name, _ in events))
        self.session.cleanup.assert_called_once()
        self.runtime.cleanup.assert_called_once()

class SourceOwnerControls(unittest.TestCase):
    def test_source_command_is_owner_bound_coherently_read_and_retained(self):
        import time
        from test_compact_native_controls import SyntheticOwners
        from test_compact_capture_retention import FakeNative
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            factory, api = SyntheticOwners(), FakeNative()
            def start(argv, **kwargs):
                kwargs['report_dir'] = Path(kwargs['report_dir'])
                return factory.start(['fixture', b'known-source\r\n'.hex(), '', '0'], **kwargs)
            def read(root, relative, limit, deadline):
                with (root / relative).open('rb') as stream:
                    return stream.read(), api.record(stream.fileno())
            session = subject.SourceSession(root, time.monotonic()+30, time.monotonic()+90, mock.Mock(check=lambda: None))
            with mock.patch.object(q, 'WindowsJobProbe', mock.Mock(start=start)), mock.patch.object(subject.contract, 'read_owned_capture_snapshot', read):
                self.assertEqual(b'known-source\r\n', session.git_bytes(root, 'rev-parse', 'HEAD'))
            self.assertEqual(1, len(session.owners))
            self.assertTrue(session.cleanup())
            self.assertEqual(b'known-source\r\n', (root / 'command-0001/stdout.bin').read_bytes())

    def test_unsafe_native_handles_refuse_before_the_next_control(self):
        import compact_native_controls as native, time
        from types import SimpleNamespace
        runtime = SimpleNamespace(work_deadline=time.monotonic()+30, owners=[], nested_command_slots=0,
            resource_check=lambda: None, apis=[SimpleNamespace(handles={123: object()}, close_uncertain=False)])
        def run(*args):
            runtime.owners.append(object())
            return {}
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(native, 'run_control', side_effect=run) as call:
            with self.assertRaisesRegex(q.Refused, '^native_handle_cleanup_unverified$'):
                subject.perform_controls(Path(temporary).resolve(), runtime, {})
            self.assertEqual(1, call.call_count)

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
