"""Portable contract checks for the narrow Windows snapshot packet."""
import unittest


class SnapshotPacketControls(unittest.TestCase):
    def test_exact_relevant_population_is_separate_from_application_tests(self):
        import diagnose_windows_snapshot as d
        groups = d.control_groups()
        self.assertEqual({name: len(ids) for name, ids in groups.items()},
                         {'contract': 41, 'deterministic': 26, 'native': 6})
        self.assertEqual(len(set(sum(groups.values(), ()))), 73)


class SnapshotReportingControls(unittest.TestCase):
    def test_snapshot_observation_uses_actual_population_bound_before_refusal(self):
        import json
        from pathlib import Path
        import tempfile
        from unittest import mock
        import diagnostic_observations as o
        import diagnose_windows_snapshot as d
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            stdout, stderr = root/'out', root/'err'
            stdout.write_text(o.PREFIX + json.dumps({'events': [], 'preflight_failure': {
                'exception_category': 'Refused', 'reason': 'snapshot_population_changed'}}))
            stderr.write_text('PRIVATE RAW TRACEBACK\n')
            result = {'stdout': stdout.read_text(), 'stderr': stderr.read_text(), 'returncode': 2,
                      'stdout_path': str(stdout), 'stderr_path': str(stderr)}
            with mock.patch.object(o.q, 'emit') as emit:
                row = o.observe_result('snapshot', result, sum(d.control_groups().values(), ()))
            self.assertEqual(row['expected_test_count'], 73)
            self.assertEqual(row['exit_state'], 'nonzero')
            self.assertFalse(row['summary_read'])
            self.assertIn(mock.call('diagnostic_control_preflight', phase='snapshot',
                                    exception_category='Refused', reason='snapshot_population_changed'), emit.call_args_list)
            self.assertNotIn('PRIVATE', repr(emit.call_args_list))

    def test_child_preparser_failure_is_bounded_not_raw_traceback(self):
        import contextlib
        import io
        import json
        from unittest import mock
        import diagnose_windows_snapshot as d
        import diagnostic_observations as o
        output = io.StringIO()
        with mock.patch.object(d, 'control_child', side_effect=PermissionError('PRIVATE path and payload')), \
             contextlib.redirect_stdout(output):
            status = d.main(['--controls-child'])
        self.assertEqual(status, 2)
        row = json.loads(output.getvalue().split(o.PREFIX, 1)[1])
        self.assertEqual(row['preflight_failure']['exception_category'], 'PermissionError')
        self.assertNotIn('PRIVATE', output.getvalue())

    def test_snapshot_failure_ids_are_allowlisted_and_counts_are_bounded(self):
        import json
        from pathlib import Path
        import tempfile
        from unittest import mock
        import diagnostic_observations as o
        import diagnose_windows_snapshot as d
        known = d.control_groups()['native'][0]
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); stdout, stderr = root/'out', root/'err'
            stdout.write_text(o.PREFIX + json.dumps({'events': [{'test_id': known,
                'exception_category': 'AssertionError', 'metadata': []}, {'test_id': 'PRIVATE',
                'exception_category': 'PRIVATE', 'metadata': []}]}))
            stderr.write_text('Ran 74 tests in 0.1s\n\nOK\n')
            result = {'stdout': stdout.read_text(), 'stderr': stderr.read_text(), 'returncode': 0,
                      'stdout_path': str(stdout), 'stderr_path': str(stderr)}
            with mock.patch.object(o.q, 'emit') as emit:
                row = o.observe_result('snapshot', result, sum(d.control_groups().values(), ()))
            self.assertEqual(row['counts_state'], 'out_of_range')
            self.assertIsNone(row['tests_run'])
            self.assertNotIn('PRIVATE', repr(emit.call_args_list))
            ids = [call.kwargs['test_id'] for call in emit.call_args_list
                   if call.args == ('diagnostic_contract_failure',)]
            self.assertEqual(ids, [known, 'unknown'])

    def test_snapshot_command_failure_has_phase_and_original_identity(self):
        from unittest import mock
        import diagnostic_observations as o
        primary = RuntimeError('PRIVATE command')
        session = object.__new__(o.ObservedSession)
        session.owners = []
        session.phase = 'snapshot'
        with mock.patch.object(o.q.Session, 'run', side_effect=primary), mock.patch.object(o.q, 'emit') as emit:
            with self.assertRaises(RuntimeError) as caught:
                session.run([], '.')
        self.assertIs(caught.exception, primary)
        self.assertIn(mock.call('diagnostic_command_failed', phase='snapshot',
                                exception_category='RuntimeError', reason='unavailable',
                                exit_state='unavailable'), emit.call_args_list)

    def test_final_cleanup_failure_cannot_hide_prior_snapshot_failure(self):
        import os
        from pathlib import Path
        import tempfile
        from unittest import mock
        import diagnose_windows_snapshot as d
        import diagnostic_observations as o
        import measure_lazy_suite_ids as q
        real_require = q.require
        def require(value, reason):
            if reason != 'windows_python_pin_required':
                real_require(value, reason)
        def fail(session, observer, seed, progress):
            progress['active_phase'] = 'snapshot'
            raise q.Refused('probe_failed_or_unread')
        with tempfile.TemporaryDirectory() as name:
            observer, seed = Path(name)/'observer', Path(name)/'seed'
            observer.mkdir(); seed.mkdir()
            for cleanup in (False, OSError('PRIVATE cleanup')):
                session = mock.Mock()
                if isinstance(cleanup, BaseException):
                    session.cleanup.side_effect = cleanup
                else:
                    session.cleanup.return_value = cleanup
                with mock.patch.object(q, 'require', side_effect=require), \
                     mock.patch.object(q, 'environment_preflight'), mock.patch.object(q, 'corpus_preflight'), \
                     mock.patch.object(q, 'safe_exception'), mock.patch.object(q, 'emit') as emit, \
                     mock.patch.object(o, 'ObservedSession', return_value=session), \
                     mock.patch.object(d, 'collect', side_effect=fail), \
                     mock.patch.dict(os.environ, {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push',
                                                 'GITHUB_REF': q.BRANCH, 'GITHUB_RUN_ATTEMPT': '1'}):
                    import time
                    status = d.main(['--observer', str(observer), '--seed', str(seed),
                                     '--job-start-epoch', str(time.time())])
                self.assertEqual(status, 2)
                summary = next(c.kwargs for c in emit.call_args_list if c.args == ('snapshot_summary',))
                self.assertEqual(summary['failure_phase'], 'snapshot')
                self.assertEqual(summary['failure'], 'probe_failed_or_unread')
                self.assertFalse(summary['process_cleanup_verified'])
                self.assertFalse(summary['qualification'])
                self.assertNotIn('PRIVATE', repr(emit.call_args_list))

    def test_native_population_contains_mutation_and_replacement_without_sleep_loop(self):
        import inspect
        import windows_snapshot_controls as n
        source = inspect.getsource(n.NativeWindowsSnapshotControls)
        self.assertIn('test_native_change_at_closed_boundary_refuses_restored_write_time', source)
        self.assertIn('test_native_replacement_at_closed_boundary_refuses_same_bytes', source)
        self.assertNotIn('time.sleep', source)
        self.assertNotIn('skipTest', source)
        self.assertIn("not row['fields_equal']['st_ctime_ns']", source)
        self.assertIn("not row['fields_equal']['st_ino']", source)


    def test_fixture_cleanup_is_observed_before_failed_child_parser(self):
        import json
        from pathlib import Path
        import tempfile
        from unittest import mock
        import diagnose_windows_snapshot as d
        import measure_lazy_suite_ids as q
        events = []
        def refuse(*args):
            events.append('verify')
            raise q.Refused('probe_failed_or_unread')
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            session = mock.Mock(root=root, deadline=9999999999.0)
            session.git.side_effect = ['', '\n'.join(q.OBSERVER_PATHS)]
            session.run.side_effect = [{'returncode': 0, 'stdout': '{}'}, {'returncode': 1}]
            import measure_maintainer_pair as m
            with mock.patch.object(m, 'environment_identity', return_value={}), \
                 mock.patch.object(q, 'first_clean'), mock.patch.object(q, 'inventory', return_value={}), \
                 mock.patch.object(q, 'raw_source_inventory', return_value={q.SUITE_PATH: q.ORIGINAL_HASH}), \
                 mock.patch.object(q, 'validate_owner_controls'), \
                 mock.patch.object(q, 'verify_probe', side_effect=refuse), \
                 mock.patch.object(q, 'emit', side_effect=lambda event, **kw: events.append((event, kw))), \
                 self.assertRaises(q.Refused):
                d.collect(session, root/'observer', root/'seed', {})
        observed = next(index for index, event in enumerate(events)
                        if type(event) is tuple and event[0] == 'snapshot_fixture_cleanup')
        self.assertLess(observed, events.index('verify'))
        self.assertTrue(events[observed][1]['verified'])


if __name__ == '__main__':
    unittest.main()
