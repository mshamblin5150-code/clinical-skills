"""Synthetic reporting controls; never a Windows owner or hosted admission proof."""

import copy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import sys
import time
from types import SimpleNamespace
import unittest
from unittest import mock

import diagnostic_observations as d
from lazy_suite_support import MARKER


PHASE = 'contract'
ALLOWED_ID = 'test_public.Controls.test_allowed'
PRIVATE = 'SYNTHETIC_PRIVATE_PAYLOAD_NOT_FOR_PUBLIC_REPORTING'


def failure_frame(kind, method, test_id, terminal):
    return ('=' * 70 + '\n'
            + f'{kind}: {method} ({test_id})\n'
            + '-' * 70 + '\n'
            + 'Traceback (most recent call last):\n'
            + '  File "' + PRIVATE + '/synthetic.py", line 7, in test_case\n'
            + '    raise AssertionError("' + PRIVATE + '")\n'
            + terminal + '\n\n')


class DiagnosticObservationControls(unittest.TestCase):
    def setUp(self):
        self.capture_dir = tempfile.TemporaryDirectory(prefix='synthetic-observation-')
        self.addCleanup(self.capture_dir.cleanup)
        self.root = Path(self.capture_dir.name)

    def capture(self, stderr, *, stdout='', returncode=0):
        stdout_path = self.root / ('stdout-' + PRIVATE + '.txt')
        stderr_path = self.root / ('stderr-' + PRIVATE + '.txt')
        stdout_path.write_text(stdout, encoding='utf-8')
        stderr_path.write_text(stderr, encoding='utf-8')
        return {'returncode': returncode, 'stdout': stdout, 'stderr': stderr,
                'stdout_path': str(stdout_path), 'stderr_path': str(stderr_path),
                'cleanup_verified': True, 'wall_seconds': 0.125,
                'tree_cpu_seconds': 0.0625}

    def observe(self, result, *, allowed_ids=(), phase=PHASE):
        before = copy.deepcopy(result)
        with mock.patch.object(d.q, 'emit') as emit:
            d.observe_result(phase, result, allowed_ids=allowed_ids)
        self.assertEqual(result, before, 'Reporting must not rewrite command evidence.')
        self.emitted = emit.call_args_list
        self.assertNotIn(PRIVATE, repr(self.emitted))
        observed = [call for call in self.emitted
                    if call.args == ('diagnostic_child_observed',)]
        self.assertEqual(len(observed), 1)
        args, row = observed[0]
        self.assertEqual(args, ('diagnostic_child_observed',))
        self.assertEqual(row['phase'], phase)
        self.assertIs(type(row['summary_read']), bool)
        self.assertIn(row['exit_state'], ('zero', 'nonzero', 'unavailable'))
        for key in ('tests_run', 'failures', 'errors', 'skipped'):
            self.assertTrue(row[key] is None or type(row[key]) is int, key)
            if row[key] is not None:
                self.assertGreaterEqual(row[key], 0, key)
        self.assertIs(type(row['unknown_failure_ids']), int)
        self.assertGreaterEqual(row['unknown_failure_ids'], 0)
        self.assertLessEqual(set(row['failed_test_ids']), set(allowed_ids))
        self.assertNotIn(PRIVATE, json.dumps(row, sort_keys=True))
        for field in ('stdout', 'stderr', 'stdout_path', 'stderr_path', 'traceback',
                      'argv', 'cwd', 'message', 'exception_message'):
            self.assertNotIn(field, row)
        return row

    def test_clean_unittest_counts_are_observed_without_changing_the_result(self):
        row = self.observe(self.capture('Ran 3 tests in 0.125s\n\nOK\n',
                                       stdout=PRIVATE + '\n'))
        self.assertEqual(row['exit_state'], 'zero')
        self.assertTrue(row['summary_read'])
        self.assertEqual((row['tests_run'], row['failures'], row['errors'], row['skipped']),
                         (3, 0, 0, 0))
        self.assertEqual(row['failed_test_ids'], [])
        self.assertEqual(row['unknown_failure_ids'], 0)

    def test_skipped_count_is_visible_without_becoming_a_clean_admission(self):
        result = self.capture('Ran 3 tests in 0.125s\n\nOK (skipped=1)\n')
        row = self.observe(result)
        self.assertTrue(row['summary_read'])
        self.assertEqual((row['tests_run'], row['skipped']), (3, 1))
        with self.assertRaises(d.q.Refused) as raised:
            d.q.verify_probe(result, 3, d.q.LOOKUPS[0])
        self.assertEqual(str(raised.exception), 'probe_failed_or_unread')

    def test_failed_child_reports_counts_and_only_allowlisted_failure_ids(self):
        private_id = PRIVATE + '.Private.test_secret'
        stderr = (
            failure_frame('FAIL', 'test_allowed', ALLOWED_ID, 'AssertionError: ' + PRIVATE)
            + failure_frame('ERROR', PRIVATE, private_id, 'RuntimeError: ' + PRIVATE)
            + 'Ran 4 tests in 0.125s\n\nFAILED (failures=1, errors=1, skipped=1)\n')
        row = self.observe(self.capture(stderr, returncode=1), allowed_ids=(ALLOWED_ID,))
        self.assertEqual(row['exit_state'], 'nonzero')
        self.assertTrue(row['summary_read'])
        self.assertEqual((row['tests_run'], row['failures'], row['errors'], row['skipped']),
                         (4, 1, 1, 1))
        self.assertEqual(row['failed_test_ids'], [ALLOWED_ID])
        self.assertEqual(row['unknown_failure_ids'], 1)

    def test_no_allowlist_does_not_publish_even_syntactically_valid_test_ids(self):
        stderr = (failure_frame('FAIL', 'test_allowed', ALLOWED_ID,
                                'AssertionError: ' + PRIVATE)
                  + 'Ran 1 test in 0.125s\n\nFAILED (failures=1)\n')
        row = self.observe(self.capture(stderr, returncode=1))
        self.assertEqual(row['failed_test_ids'], [])
        self.assertEqual(row['unknown_failure_ids'], 1)
        self.assertNotIn(ALLOWED_ID, json.dumps(row))

    def test_malformed_capture_emits_unread_counts_not_a_success_claim(self):
        result = self.capture(PRIVATE + '\nRan no readable summary\n', returncode=1)
        row = self.observe(result)
        self.assertFalse(row['summary_read'])
        self.assertEqual(row['exit_state'], 'nonzero')
        self.assertTrue(all(row[key] is None
                            for key in ('tests_run', 'failures', 'errors', 'skipped')))

    def test_missing_capture_does_not_raise_or_expose_the_private_path(self):
        result = self.capture('Ran 1 test in 0.125s\n\nOK\n')
        Path(result['stderr_path']).unlink()
        row = self.observe(result)
        self.assertFalse(row['summary_read'])
        self.assertTrue(all(row[key] is None
                            for key in ('tests_run', 'failures', 'errors', 'skipped')))

    def test_unreadable_capture_kind_does_not_raise_or_expose_the_private_path(self):
        result = self.capture('Ran 1 test in 0.125s\n\nOK\n')
        Path(result['stderr_path']).unlink()
        Path(result['stderr_path']).mkdir()
        row = self.observe(result)
        self.assertFalse(row['summary_read'])
        self.assertTrue(all(row[key] is None
                            for key in ('tests_run', 'failures', 'errors', 'skipped')))

    def test_parser_integer_conversion_error_is_reported_without_escaping(self):
        # This exceeds Python's default integer-string conversion guard. It is
        # synthetic parser input, not a source or process capture-size waiver.
        stderr = 'Ran ' + ('9' * 5000) + ' tests in 0.125s\n\nOK\n'
        row = self.observe(self.capture(stderr, stdout=PRIVATE))
        self.assertFalse(row['summary_read'])
        self.assertIsNone(row['tests_run'])

    def test_absent_or_noninteger_exit_is_unavailable_not_zero(self):
        for code in (None, False, True, '0', PRIVATE):
            with self.subTest(code=type(code).__name__):
                row = self.observe(self.capture(PRIVATE, returncode=code))
                self.assertEqual(row['exit_state'], 'unavailable')
        result = self.capture(PRIVATE)
        del result['returncode']
        self.assertEqual(self.observe(result)['exit_state'], 'unavailable')

    def test_expected_refusal_remains_refused_after_observation(self):
        stderr = (failure_frame('FAIL', 'test_allowed', ALLOWED_ID,
                                'AssertionError: ' + MARKER + ':' + d.q.LOOKUPS[0])
                  + 'Ran 1 test in 0.125s\n\nFAILED (failures=1)\n')
        result = self.capture(stderr, returncode=1)
        with self.assertRaises(d.q.Refused) as before:
            d.q.verify_probe(result, 1, d.q.LOOKUPS[0])
        row = self.observe(result, allowed_ids=(ALLOWED_ID,))
        self.assertEqual(row['exit_state'], 'nonzero')
        self.assertEqual((row['tests_run'], row['failures']), (1, 1))
        with self.assertRaises(d.q.Refused) as after:
            d.q.verify_probe(result, 1, d.q.LOOKUPS[0])
        self.assertEqual(str(before.exception), 'probe_failed_or_unread')
        self.assertEqual(str(after.exception), str(before.exception))

    def test_malformed_summary_counts_are_unread_not_zero(self):
        row = self.observe(self.capture(
            'Ran 1 test in 0.125s\n\nFAILED (errors=not-number)\n', returncode=1))
        self.assertFalse(row['summary_read'])
        self.assertTrue(all(row[key] is None
                            for key in ('tests_run', 'failures', 'errors', 'skipped')))

    def test_out_of_range_summary_counts_are_categorized_not_emitted_as_integers(self):
        result = self.capture('Ran 987654321 tests in 0.125s\n\n'
                              'FAILED (failures=987654321, errors=987654321, skipped=987654321)\n',
                              returncode=1)
        row = self.observe(result)
        self.assertTrue(row['summary_read'])
        self.assertEqual(row['counts_state'], 'out_of_range')
        self.assertTrue(all(row[key] is None
                            for key in ('tests_run', 'failures', 'errors', 'skipped')))
        self.assertNotIn('987654321', repr(self.emitted))

    def test_unknown_failure_header_count_is_capped_by_the_phase_population(self):
        for phase, bound in (('contract', 41), ('native', 9), ('retained', 5), ('case_0', 1)):
            with self.subTest(phase=phase):
                for count, truncated in ((bound, False), (bound + 3, True)):
                    stderr = (f'FAIL: {PRIVATE} ({PRIVATE})\n' * count
                              + 'Ran 1 test in 0.125s\n\nFAILED (failures=1)\n')
                    row = self.observe(self.capture(stderr, returncode=1), phase=phase)
                    self.assertEqual(row['unknown_failure_ids'], bound)
                    self.assertIs(row['unknown_failure_ids_truncated'], truncated)
                    self.assertEqual(row['failed_test_ids'], [])

    def test_duplicate_or_malformed_contract_json_is_unread_without_private_payloads(self):
        bodies = ('{', '{"events":[],"events":["' + PRIVATE + '"]}',
                  '{"events":[{"test_id":"' + PRIVATE + '","test_id":"other"}]}')
        for body in bodies:
            with self.subTest(body_kind=len(body)):
                self.observe(self.capture('Ran 1 test in 0.125s\n\nOK\n',
                                          stdout=d.PREFIX + body))
                unread = [call.kwargs for call in self.emitted
                          if call.args == ('diagnostic_receipt_observed',)]
                self.assertEqual(unread, [{'phase': 'contract', 'receipt_state': 'unread'}])
                self.assertFalse(any(call.args == ('diagnostic_contract_failure',)
                                     for call in self.emitted))

    def test_contract_failure_receipt_discards_unknown_identity_category_and_metadata(self):
        event = {'test_id': PRIVATE, 'exception_category': PRIVATE,
                 'metadata': [{'stage': PRIVATE}, {'stage': 'read_length',
                               'length_equal': False, 'raw_path': PRIVATE}],
                 'traceback': PRIVATE}
        self.observe(self.capture('Ran 1 test in 0.125s\n\nFAILED (errors=1)\n',
                                  stdout=d.PREFIX + json.dumps({'events': [event]}),
                                  returncode=1), allowed_ids=(ALLOWED_ID,))
        rows = [call.kwargs for call in self.emitted
                if call.args == ('diagnostic_contract_failure',)]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['test_id'], 'unknown')
        self.assertEqual(rows[0]['exception_category'], 'OtherException')
        self.assertEqual(rows[0]['metadata'], [{'stage': 'read_length', 'length_equal': False}])
        self.assertEqual(rows[0]['metadata_scope'], 'observed_during_failed_test_not_causal_proof')

    def test_native_failure_progress_preserves_only_allowed_controls_codes_and_states(self):
        data = {'status': 'failed', 'error_type': 'ProbeError',
                'passed_control_ids': ['normal_tree_cpu_and_active_zero', PRIVATE],
                'diagnostic_codes': ['CLEANUP_INCOMPLETE', PRIVATE],
                'source_frames': [PRIVATE],
                'control_observation': {'active_control_id': 'separate_large_output',
                                        'completed_control_ids': ['normal_tree_cpu_and_active_zero', PRIVATE],
                                        'cleanup_state': 'failed', 'private_detail': PRIVATE}}
        self.observe(self.capture('', stdout=json.dumps(data), returncode=1), phase='native')
        native = [call.kwargs for call in self.emitted
                  if call.args == ('diagnostic_native_observed',)]
        progress = [call.kwargs for call in self.emitted
                    if call.args == ('diagnostic_native_progress',)]
        self.assertEqual(len(native), 1)
        self.assertEqual(native[0]['reported_status'], 'failed')
        self.assertEqual(native[0]['exception_category'], 'ProbeError')
        self.assertEqual(native[0]['passed_control_ids'], ['normal_tree_cpu_and_active_zero'])
        self.assertEqual(native[0]['diagnostic_codes'], ['CLEANUP_INCOMPLETE'])
        self.assertEqual(progress, [{'active_control_id': 'separate_large_output',
                                     'completed_control_ids': ['normal_tree_cpu_and_active_zero'],
                                     'cleanup_state': 'failed',
                                     'primary_error_type': 'unavailable',
                                     'primary_diagnostic_codes': None}])
        data['status'] = data['error_type'] = PRIVATE
        data['control_observation']['active_control_id'] = PRIVATE
        data['control_observation']['cleanup_state'] = PRIVATE
        data['control_observation']['primary_error_type'] = PRIVATE
        data['control_observation']['primary_diagnostic_codes'] = ['CLEANUP_INCOMPLETE', PRIVATE, 7]
        self.observe(self.capture('', stdout=json.dumps(data), returncode=1), phase='native')
        native = next(call.kwargs for call in self.emitted
                      if call.args == ('diagnostic_native_observed',))
        progress = next(call.kwargs for call in self.emitted
                        if call.args == ('diagnostic_native_progress',))
        self.assertEqual(native['reported_status'], 'unavailable')
        self.assertEqual(native['exception_category'], 'unavailable')
        self.assertIsNone(progress['active_control_id'])
        self.assertEqual(progress['cleanup_state'], 'unavailable')
        self.assertEqual(progress['primary_error_type'], 'unavailable')
        self.assertEqual(progress['primary_diagnostic_codes'], ['CLEANUP_INCOMPLETE'])
        data['control_observation']['primary_error_type'] = 'OSError'
        self.observe(self.capture('', stdout=json.dumps(data), returncode=1), phase='native')
        progress = next(call.kwargs for call in self.emitted
                        if call.args == ('diagnostic_native_progress',))
        self.assertEqual(progress['primary_error_type'], 'OSError')
        self.assertEqual(progress['primary_diagnostic_codes'], ['CLEANUP_INCOMPLETE'])

    def test_retained_failure_stage_reason_and_category_are_allowlisted(self):
        data = {'case': 'linked_sessions', 'state': 'failed',
                'failure_stage': 'cleanup_started', 'exception_category': 'Refused',
                'reason': 'retained_control_link_cleanup_failed', 'raw_path': PRIVATE}
        self.observe(self.capture('RETAINED_CONTROL_OBSERVATION:' + json.dumps(data),
                                  returncode=1), phase='retained')
        rows = [call.kwargs for call in self.emitted
                if call.args == ('diagnostic_retained_observed',)]
        self.assertEqual(rows, [{'case': 'linked_sessions', 'state': 'failed',
                                 'failure_stage': 'cleanup_started', 'exception_category': 'Refused',
                                 'reason': 'retained_control_link_cleanup_failed'}])
        for field in ('failure_stage', 'exception_category', 'reason'):
            data[field] = PRIVATE
        self.observe(self.capture('RETAINED_CONTROL_OBSERVATION:' + json.dumps(data),
                                  returncode=1), phase='retained')
        row = next(call.kwargs for call in self.emitted
                   if call.args == ('diagnostic_retained_observed',))
        self.assertIsNone(row['failure_stage'])
        self.assertIsNone(row['exception_category'])
        self.assertIsNone(row['reason'])

    def test_retained_unknown_case_or_state_is_unread_not_disclosed(self):
        for data in ({'case': PRIVATE, 'state': 'failed'},
                     {'case': 'linked_sessions', 'state': PRIVATE}):
            self.observe(self.capture('RETAINED_CONTROL_OBSERVATION:' + json.dumps(data),
                                      returncode=1), phase='retained')
            self.assertFalse(any(call.args == ('diagnostic_retained_observed',)
                                 for call in self.emitted))
            self.assertIn(mock.call('diagnostic_receipt_observed', phase='retained',
                                    receipt_state='unread'), self.emitted)

    def test_contract_expected_count_matches_the_actual_unittest_population(self):
        suite = unittest.defaultTestLoader.loadTestsFromName('test_generated_output_contract')
        actual_count = suite.countTestCases()
        self.assertGreater(actual_count, 0)
        self.assertEqual(len(d.contract_ids()), actual_count)
        row = self.observe(self.capture('Ran 1 test in 0.125s\n\nOK\n',
                                        stdout=d.PREFIX + '{"events":[]}'))
        self.assertEqual(row['expected_test_count'], actual_count)


class MetadataSanitizerControls(unittest.TestCase):
    def valid_row(self):
        from generated_output_contract import METADATA_FIELDS
        return {'stage': 'before_after',
                'fields_equal': {field: True for field in METADATA_FIELDS},
                'left_ctime_equals_birthtime': False,
                'right_ctime_equals_birthtime': 'unavailable'}

    def test_finite_metadata_flags_survive_without_raw_values_or_tokens(self):
        expected = self.valid_row()
        supplied = dict(expected, path=PRIVATE, left_metadata=PRIVATE,
                        right_metadata=PRIVATE, file_token=PRIVATE)
        result = d.metadata_flags(supplied)
        self.assertEqual(result, expected)
        self.assertNotIn(PRIVATE, repr(result))
        self.assertEqual(d.metadata_flags({'stage': 'read_length', 'length_equal': False,
                                          'read_length': PRIVATE}),
                         {'stage': 'read_length', 'length_equal': False})

    def test_unknown_stage_nonboolean_fields_and_birthtime_values_are_rejected(self):
        row = self.valid_row()
        field = next(iter(row['fields_equal']))
        malformed = (None, PRIVATE, dict(row, stage=PRIVATE),
                     dict(row, fields_equal={}),
                     dict(row, fields_equal=dict(row['fields_equal'], unknown=True)),
                     dict(row, fields_equal=dict(row['fields_equal'], **{field: 1})),
                     dict(row, left_ctime_equals_birthtime=PRIVATE),
                     dict(row, right_ctime_equals_birthtime=0),
                     {'stage': 'read_length', 'length_equal': True})
        for value in malformed:
            with self.subTest(value_kind=type(value).__name__):
                self.assertIsNone(d.metadata_flags(value))


class ContractChildIntegrationControls(unittest.TestCase):
    def test_only_unhandled_failure_reports_existing_finite_emit_metadata(self):
        allowed = d.contract_ids()
        self.assertGreaterEqual(len(allowed), 2)

        class SyntheticControl(unittest.TestCase):
            def __init__(self, identity, caught):
                super().__init__('runTest')
                self.identity, self.caught = identity, caught

            def id(self):
                return self.identity

            def runTest(self):
                self.emit = mock.Mock()
                self.emit('generated_file_comparison', stage='read_length',
                          length_equal=False, path=PRIVATE, metadata=PRIVATE)
                self.emit('unrelated_private_event', payload=PRIVATE)
                if self.caught:
                    with self.assertRaises(d.q.Refused):
                        raise d.q.Refused(PRIVATE)
                else:
                    raise AssertionError(PRIVATE)

        suite = unittest.TestSuite([SyntheticControl(allowed[0], False),
                                    SyntheticControl(allowed[1], True)])
        public, private = io.StringIO(), io.StringIO()
        with mock.patch.object(unittest.defaultTestLoader, 'loadTestsFromNames',
                               return_value=suite) as load, \
             contextlib.redirect_stdout(public), contextlib.redirect_stderr(private):
            status = d.contract_child()
        load.assert_called_once_with(['test_generated_output_contract'], None)
        self.assertEqual(status, 1)
        self.assertIn('Ran 2 tests', private.getvalue())
        lines = public.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith(d.PREFIX))
        receipt = json.loads(lines[0][len(d.PREFIX):])
        self.assertEqual(receipt, {'events': [{'test_id': allowed[0],
                                              'exception_category': 'AssertionError',
                                              'metadata': [{'stage': 'read_length',
                                                            'length_equal': False}]}]})
        self.assertNotIn(PRIVATE, public.getvalue())


class RetainedMainIntegrationControls(unittest.TestCase):
    def exercise_real_pre_case_failure(self, *, expired):
        import staging_retained_controls as retained

        original_mkdir = Path.mkdir

        def injected_mkdir(path, *args, **kwargs):
            if path.name == 'sessions' and path.parent.parent.name == 'empty_sessions':
                raise OSError(PRIVATE)
            return original_mkdir(path, *args, **kwargs)

        with tempfile.TemporaryDirectory(prefix='synthetic-retained-main-') as raw:
            root = Path(raw).resolve()
            stdout, stderr = io.StringIO(), io.StringIO()
            deadline = 0 if expired else time.monotonic() + 30
            with contextlib.ExitStack() as stack:
                if not expired:
                    stack.enter_context(mock.patch.object(Path, 'mkdir', new=injected_mkdir))
                stack.enter_context(mock.patch.object(sys, 'argv',
                    ['retained-controls', '--report-root', str(root), '--deadline', str(deadline)]))
                stack.enter_context(contextlib.redirect_stdout(stdout))
                stack.enter_context(contextlib.redirect_stderr(stderr))
                status = retained.main()
            self.assertEqual(list(root.iterdir()), [], 'The owned fixture must be cleaned.')
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(stdout.getvalue()),
                         {'passed': False, 'reason': 'retained_controls_inconclusive'})
        prefix = 'RETAINED_CONTROL_OBSERVATION:'
        lines = stderr.getvalue().splitlines()
        self.assertTrue(all(line.startswith(prefix) for line in lines))
        rows = [json.loads(line[len(prefix):]) for line in lines]
        self.assertIn({'case': 'empty_sessions', 'state': 'started'}, rows)
        self.assertIn({'case': 'fixture', 'state': 'cleanup_passed'}, rows)
        self.assertEqual(rows[-1], {'case': 'empty_sessions', 'state': 'failed',
                                    'failure_stage': 'started',
                                    'exception_category': 'Refused' if expired else 'OSError',
                                    'reason': 'global_budget_exhausted' if expired else 'unavailable'})
        self.assertNotIn(PRIVATE, stdout.getvalue() + stderr.getvalue())

    def test_real_expired_deadline_is_identified_before_fixture_cleanup(self):
        self.exercise_real_pre_case_failure(expired=True)

    def test_real_mkdir_setup_error_is_identified_before_fixture_cleanup(self):
        self.exercise_real_pre_case_failure(expired=False)

    def test_primary_failure_survives_case_and_fixture_cleanup_transitions(self):
        import staging_retained_controls as retained

        for cleanup_fails in (False, True):
            with self.subTest(cleanup_fails=cleanup_fails):
                primary = d.q.Refused('retained_control_link_unavailable')
                cleanup_error = OSError(PRIVATE)

                def synthetic_controls(report_root, deadline, observe):
                    observe('linked_sessions', 'started')
                    observe('linked_sessions', 'failed', primary)
                    observe('linked_sessions', 'cleanup_started')
                    observe('linked_sessions', 'cleanup_passed')
                    observe('fixture', 'cleanup_started')
                    if cleanup_fails:
                        observe('fixture', 'cleanup_failed', cleanup_error)
                        raise cleanup_error
                    observe('fixture', 'cleanup_passed')
                    raise primary

                stdout, stderr = io.StringIO(), io.StringIO()
                with mock.patch.object(retained, 'controls', side_effect=synthetic_controls), \
                     mock.patch.object(sys, 'argv', ['retained-controls', '--report-root',
                                                    'synthetic-unused', '--deadline', '1000']), \
                     contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    status = retained.main()
                self.assertEqual(status, 2)
                self.assertEqual(json.loads(stdout.getvalue()),
                                 {'passed': False, 'reason': 'retained_controls_inconclusive'})
                prefix = 'RETAINED_CONTROL_OBSERVATION:'
                lines = stderr.getvalue().splitlines()
                self.assertTrue(all(line.startswith(prefix) for line in lines))
                rows = [json.loads(line[len(prefix):]) for line in lines]
                self.assertIn({'case': 'fixture', 'state':
                               'cleanup_failed' if cleanup_fails else 'cleanup_passed'}, rows)
                self.assertEqual(rows[-1], {'case': 'linked_sessions', 'state': 'failed',
                                            'failure_stage': 'started',
                                            'exception_category': 'Refused',
                                            'reason': 'retained_control_link_unavailable'})
                self.assertNotIn(PRIVATE, stdout.getvalue() + stderr.getvalue())


class NativePrimaryFailureControls(unittest.TestCase):
    def test_cleanup_failure_keeps_original_outcome_and_observes_primary_failure_separately(self):
        import windows_job_probe_controls as native

        probe = SimpleNamespace(result=None,
            finish=mock.Mock(side_effect=OSError(PRIVATE)),
            cancel=mock.Mock(side_effect=native.ProbeError('TERMINATE_JOB_FAILED')))
        observation = {}
        platform = SimpleNamespace(name='nt', environ=dict(native.os.environ),
                                   getcwd=native.os.getcwd)
        with tempfile.TemporaryDirectory(prefix='synthetic-native-primary-') as raw:
            root = Path(raw) / 'controls'
            with mock.patch.object(native, 'os', platform), \
                 mock.patch.object(native.WindowsJobProbe, 'start', return_value=probe) as start:
                with self.assertRaises(native.ProbeError) as raised:
                    native.run_controls(root, observation)
        self.assertEqual(raised.exception.code, 'CONTROL_PROCESS_CLEANUP_INCOMPLETE')
        self.assertEqual(raised.exception.diagnostic_codes, ('TERMINATE_JOB_FAILED',))
        start.assert_called_once()
        probe.finish.assert_called_once_with(timeout=native.WAIT_SECONDS)
        probe.cancel.assert_called_once_with('control-finally', timeout=native.WAIT_SECONDS)
        self.assertEqual(observation['active_control_id'], 'normal_tree_cpu_and_active_zero')
        self.assertEqual(observation['completed_control_ids'], [])
        self.assertEqual(observation['primary_error_type'], 'OSError')
        self.assertEqual(observation['primary_diagnostic_codes'], [])
        self.assertEqual(observation['cleanup_state'], 'failed')
        self.assertNotIn(PRIVATE, json.dumps(observation))


class ExceptionCategoryControls(unittest.TestCase):
    def test_known_classes_have_finite_labels_without_exception_messages(self):
        for kind in (AssertionError, ValueError, RuntimeError, TypeError, OSError,
                     FileNotFoundError, PermissionError, KeyError, TimeoutError):
            with self.subTest(kind=kind.__name__):
                self.assertEqual(d.exception_category(kind(PRIVATE)), kind.__name__)

    def test_arbitrary_exception_class_name_is_not_disclosed(self):
        kind = type(PRIVATE, (Exception,), {})
        self.assertEqual(d.exception_category(kind(PRIVATE)), 'OtherException')

    def test_custom_exception_cannot_spoof_a_known_class_label(self):
        kind = type('ValueError', (Exception,), {})
        self.assertEqual(d.exception_category(kind(PRIVATE)), 'OtherException')


class ObservedSessionControls(unittest.TestCase):
    def session(self):
        session = d.ObservedSession.__new__(d.ObservedSession)
        session.phase = PHASE
        return session

    def test_success_returns_the_original_result_without_starting_a_real_owner(self):
        result = {'returncode': 0, 'stdout': PRIVATE, 'stderr': PRIVATE}
        argv, cwd = ['synthetic-command', PRIVATE], Path(PRIVATE)
        session = self.session()
        with mock.patch.object(d.q.Session, 'run', return_value=result) as run, \
             mock.patch.object(d.q, 'emit') as emit:
            actual = session.run(argv, cwd)
        self.assertIs(actual, result)
        run.assert_called_once_with(argv, cwd)
        rows = [call for call in emit.call_args_list
                if call.args == ('diagnostic_child_observed',)]
        self.assertEqual(len(rows), 1)
        self.assertNotIn(PRIVATE, repr(emit.call_args_list))

    def test_command_failure_reports_bounded_metadata_and_reraises_original_identity(self):
        private_error = type(PRIVATE, (Exception,), {})(PRIVATE)
        for error in (d.q.Refused('global_budget_exhausted'),
                      OSError(PRIVATE), private_error, KeyboardInterrupt(PRIVATE)):
            with self.subTest(error_type=type(error).__name__):
                session = self.session()
                with mock.patch.object(d.q.Session, 'run', side_effect=error), \
                     mock.patch.object(d.q, 'emit') as emit:
                    with self.assertRaises(BaseException) as raised:
                        session.run(['synthetic-command', PRIVATE], Path(PRIVATE))
                self.assertIs(raised.exception, error)
                emit.assert_called_once()
                self.assertEqual(emit.call_args.args, ('diagnostic_command_failed',))
                self.assertEqual(emit.call_args.kwargs['phase'], PHASE)
                self.assertNotIn(PRIVATE, repr(emit.call_args))

    def test_reporting_failure_cannot_replace_the_original_command_exception(self):
        error = d.q.Refused('global_budget_exhausted')
        with mock.patch.object(d.q.Session, 'run', side_effect=error), \
             mock.patch.object(d.q, 'emit', side_effect=BrokenPipeError(PRIVATE)):
            with self.assertRaises(BaseException) as raised:
                self.session().run(['synthetic-command'], Path('synthetic'))
        self.assertIs(raised.exception, error)

    def test_capture_failure_preserves_the_newly_finished_owner_exit_state(self):
        for code, expected in ((0, 'zero'), (7, 'nonzero')):
            with self.subTest(code=code):
                session = self.session()
                session.owners = []
                error = OSError(PRIVATE)

                def capture_failure(argv, cwd):
                    session.owners.append(SimpleNamespace(result=SimpleNamespace(
                        snapshot=SimpleNamespace(root_exit_code=code))))
                    raise error

                with mock.patch.object(d.q.Session, 'run', side_effect=capture_failure), \
                     mock.patch.object(d.q, 'emit') as emit:
                    with self.assertRaises(OSError) as raised:
                        session.run(['synthetic-command'], Path('synthetic'))
                self.assertIs(raised.exception, error)
                emit.assert_called_once()
                self.assertEqual(emit.call_args.args, ('diagnostic_command_failed',))
                self.assertEqual(emit.call_args.kwargs['exit_state'], expected)
                self.assertEqual(emit.call_args.kwargs['exception_category'], 'OSError')
                self.assertNotIn(PRIVATE, repr(emit.call_args_list))

    def test_unfinished_or_absent_new_owner_cannot_borrow_a_previous_owner_exit(self):
        for add_unfinished in (False, True):
            with self.subTest(add_unfinished=add_unfinished):
                session = self.session()
                session.owners = [SimpleNamespace(result=SimpleNamespace(
                    snapshot=SimpleNamespace(root_exit_code=0)))]
                error = d.q.Refused('global_budget_exhausted')

                def incomplete_run(argv, cwd):
                    if add_unfinished:
                        session.owners.append(SimpleNamespace(result=None))
                    raise error

                with mock.patch.object(d.q.Session, 'run', side_effect=incomplete_run), \
                     mock.patch.object(d.q, 'emit') as emit:
                    with self.assertRaises(d.q.Refused) as raised:
                        session.run(['synthetic-command'], Path('synthetic'))
                self.assertIs(raised.exception, error)
                emit.assert_called_once()
                self.assertEqual(emit.call_args.args, ('diagnostic_command_failed',))
                self.assertEqual(emit.call_args.kwargs['exit_state'], 'unavailable')

    def test_observation_or_allowlist_load_failure_returns_the_original_result(self):
        result = {'returncode': 1, 'stdout': PRIVATE, 'stderr': PRIVATE}
        before = copy.deepcopy(result)
        for operation in ('observe_result', 'contract_ids'):
            for emit_raises in (False, True):
                with self.subTest(operation=operation, emit_raises=emit_raises):
                    with mock.patch.object(d.q.Session, 'run', return_value=result), \
                         mock.patch.object(d, operation, side_effect=RuntimeError(PRIVATE)), \
                         mock.patch.object(d.q, 'emit', side_effect=
                                           BrokenPipeError(PRIVATE) if emit_raises else None) as emit:
                        actual = self.session().run(['synthetic-command'], Path('synthetic'))
                    self.assertIs(actual, result)
                    self.assertEqual(result, before)
                    emit.assert_called_once_with('diagnostic_receipt_observed',
                                                 phase=PHASE, receipt_state='unread')
                    self.assertNotIn(PRIVATE, repr(emit.call_args_list))


class DiagnosticCleanupControls(unittest.TestCase):
    def exercise_main(self, *, primary_failure, cleanup_raises):
        import diagnose_generated_outputs as entrypoint

        session = mock.Mock(phase='preflight')
        if cleanup_raises:
            session.cleanup.side_effect = OSError(PRIVATE)
        else:
            session.cleanup.return_value = False

        def synthetic_setup(session, observer, seed, job_start, progress):
            entrypoint.phase(session, progress, 'contract')
            if primary_failure:
                raise d.q.Refused('probe_failed_or_unread')

        environment = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push',
                       'GITHUB_REF': d.q.BRANCH, 'GITHUB_RUN_ATTEMPT': '1'}
        with tempfile.TemporaryDirectory(prefix='synthetic-cleanup-observation-') as raw:
            root = Path(raw)
            with mock.patch.object(entrypoint, 'os',
                                   SimpleNamespace(name='nt', environ=environment)), \
                 mock.patch.object(entrypoint.platform, 'python_version', return_value='3.14.4'), \
                 mock.patch.object(entrypoint, 'budget_deadline', return_value=12345), \
                 mock.patch.object(entrypoint.q, 'environment_preflight'), \
                 mock.patch.object(entrypoint.q, 'corpus_preflight'), \
                 mock.patch.object(entrypoint.tempfile, 'mkdtemp', return_value=str(root / 'owner')), \
                 mock.patch.object(entrypoint.observation, 'ObservedSession', return_value=session), \
                 mock.patch.object(entrypoint, 'setup', side_effect=synthetic_setup), \
                 mock.patch.object(entrypoint.q, 'emit') as emit:
                status = entrypoint.main(['--observer', str(root / 'observer'),
                                          '--seed', str(root / 'seed'),
                                          '--job-start-epoch', '1000'])
        self.assertEqual(status, 2)
        session.cleanup.assert_called_once_with()
        self.assertNotIn(PRIVATE, repr(emit.call_args_list))
        summaries = [call.kwargs for call in emit.call_args_list
                     if call.args == ('generated_output_summary',)]
        self.assertEqual(len(summaries), 1)
        cleanup = [call.kwargs for call in emit.call_args_list
                   if call.args == ('diagnostic_cleanup',)]
        self.assertEqual(len(cleanup), 1)
        self.assertIs(cleanup[0]['verified'], False)
        self.assertEqual(cleanup[0]['exception_category'], 'OSError' if cleanup_raises else None)
        self.assertIs(summaries[0]['process_cleanup_verified'], False)
        self.assertEqual(summaries[0]['status'], 'inconclusive')
        self.assertIs(summaries[0]['qualification'], False)
        self.assertIs(summaries[0]['full_suite'], False)
        self.assertIs(summaries[0]['automatic_rerun'], False)
        return summaries[0]

    def test_cleanup_false_or_exception_preserves_the_prior_primary_failure(self):
        for cleanup_raises in (False, True):
            with self.subTest(cleanup_raises=cleanup_raises):
                summary = self.exercise_main(primary_failure=True, cleanup_raises=cleanup_raises)
                self.assertEqual(summary['failure'], 'probe_failed_or_unread')
                self.assertEqual(summary['failure_phase'], 'contract')
                self.assertIs(summary['diagnostic_collection_complete'], False)

    def test_cleanup_false_or_exception_prevents_success_after_completed_collection(self):
        for cleanup_raises in (False, True):
            with self.subTest(cleanup_raises=cleanup_raises):
                summary = self.exercise_main(primary_failure=False, cleanup_raises=cleanup_raises)
                self.assertEqual(summary['failure'],
                                 'cleanup_failed' if cleanup_raises else 'cleanup_unverified')
                self.assertEqual(summary['failure_phase'], 'cleanup')
                self.assertIs(summary['diagnostic_collection_complete'], True)


if __name__ == '__main__':
    unittest.main()
