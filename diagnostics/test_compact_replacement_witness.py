"""Portable replacement observations; fake calls never replace a pathname."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import compact_native_controls as native
import validate_compact_first_control as first
import test_compact_native_controls as fixtures


class ReplacementWitness(unittest.TestCase):
    def test_return_categories_preserve_guard_and_call_order(self):
        for result, error, state, category, passes in (
            (0, 32, 'returned_false', 'sharing_32', True),
            (0, 5, 'returned_false', 'access_5', False),
            (0, 0, 'returned_false', 'other', False),
            (0, 1234, 'returned_false', 'other', False),
            (1, None, 'returned_true', None, False),
            (-1, None, 'returned_true', None, False),
        ):
            with self.subTest(result=result, error=error), tempfile.TemporaryDirectory() as temporary:
                api = fixtures.SharingNative()
                runtime, _, _ = fixtures.NativePacketControls().runtime(api)
                calls = []
                def move(*args):
                    calls.append('move')
                    return result
                def getter():
                    if runtime.control_observation['authority_phase'] == 'replace':
                        calls.append('error')
                        if error is None:
                            raise AssertionError('PRIVATE_STALE_ERROR')
                        return error
                    return 32
                api.kernel.MoveFileExW.call = move
                api.c.get_last_error = getter
                with contextlib.redirect_stdout(io.StringIO()):
                    if passes:
                        native.run_control('snapshot_share_receipt_success', Path(temporary)/'new', runtime)
                    else:
                        with self.assertRaises(native.ControlError):
                            native.run_control('snapshot_share_receipt_success', Path(temporary)/'new', runtime)
                witness = native.failure_witness(runtime)
                self.assertEqual(state, witness['replacement_call'])
                self.assertEqual(category, witness['replacement_error'])
                self.assertEqual(['move', 'error'] if result == 0 else ['move'], calls)
                if not passes:
                    self.assertEqual('replace', witness['authority_phase'])
                    self.assertEqual(['uncertain', 'not_requested'],
                        [row['mark'] for row in witness['outcome']['streams']])
                    self.assertFalse(api.disposed)
                self.assertEqual(1, len(runtime.owners))
                self.assertTrue(runtime.cleanup())

    def test_callback_exceptions_keep_identity_even_when_observation_writes_fail(self):
        class BrokenObservation(dict):
            def update(self, *args, **kwargs):
                if 'replacement_call' in kwargs:
                    raise OSError('PRIVATE_STORAGE')
                return super().update(*args, **kwargs)
        for boundary in ('call', 'error_read'):
            for broken in (False, True):
                with self.subTest(boundary=boundary, broken=broken), tempfile.TemporaryDirectory() as temporary:
                    api = fixtures.SharingNative()
                    runtime, _, _ = fixtures.NativePacketControls().runtime(api)
                    primary = OSError('PRIVATE_PRIMARY')
                    calls, caught = [], []
                    def move(*args):
                        calls.append('move')
                        if boundary == 'call':
                            raise primary
                        return 0
                    def getter():
                        if runtime.control_observation['authority_phase'] == 'replace':
                            calls.append('error')
                            raise primary
                        return 32
                    api.kernel.MoveFileExW.call = move
                    api.c.get_last_error = getter
                    original = native._authority_denials
                    def callback(pair):
                        if broken:
                            runtime.control_observation = BrokenObservation(runtime.control_observation)
                        try:
                            return original(pair)
                        except BaseException as error:
                            caught.append(error)
                            raise
                    with mock.patch.object(native, '_authority_denials', callback), contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaises(native.ControlError):
                            native.run_control('snapshot_share_receipt_success', Path(temporary)/'new', runtime)
                    self.assertEqual([primary], caught)
                    self.assertIs(primary, caught[0])
                    self.assertEqual(['move'] if boundary == 'call' else ['move', 'error'], calls)
                    if not broken:
                        witness = native.failure_witness(runtime)
                        self.assertEqual(boundary + '_raised', witness['replacement_call'])
                        self.assertIsNone(witness['replacement_error'])
                    self.assertFalse(api.disposed)
                    self.assertTrue(runtime.cleanup())

    def test_missing_malformed_and_cross_field_observations_stay_unknown(self):
        valid = [('not_returned', None), ('entered', None), ('returned_true', None),
                 ('call_raised', None), ('error_read_raised', None),
                 ('returned_false', 'sharing_32'), ('returned_false', 'access_5'),
                 ('returned_false', 'other')]
        for call, error in valid:
            witness = native.failure_witness(SimpleNamespace(control_observation={
                'control': 'snapshot_share_receipt_success',
                'replacement_call': call, 'replacement_error': error}))
            self.assertEqual((call, error), (witness['replacement_call'], witness['replacement_error']))
        invalid = [{}, {'replacement_call': 'entered'},
                   {'replacement_call': 'returned_false', 'replacement_error': None}]
        for value in (True, 32, [], {}, 'PRIVATE_RAW', None):
            invalid.append({'replacement_call': value, 'replacement_error': None})
            invalid.append({'replacement_call': 'returned_false', 'replacement_error': value})
        for call in ('not_returned', 'entered', 'returned_true', 'call_raised', 'error_read_raised'):
            invalid.append({'replacement_call': call, 'replacement_error': 'sharing_32'})
        for row in invalid:
            with self.subTest(row=row):
                witness = native.failure_witness(SimpleNamespace(control_observation={
                    'control': 'snapshot_share_receipt_success', **row}))
                self.assertEqual((None, None), (witness['replacement_call'], witness['replacement_error']))
                self.assertNotIn('PRIVATE_RAW', json.dumps(witness))

    def test_maximal_valid_witness_uses_actual_cli_transport_within_caps(self):
        import test_compact_first_control as cli
        api = fixtures.SharingNative()
        runtime, _, _ = fixtures.NativePacketControls().runtime(api)
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            result = native.run_control('snapshot_share_receipt_success', Path(temporary)/'new', runtime)
            result['outcome']['reason'] = max(native.retention.REASONS, key=len)
            result['outcome']['pair'] = native.retention.MAX_PAIRS
            for stream in result['outcome']['streams']:
                stream.update(mark='not_requested', close='not_opened')
            result['outcome']['receipt_authority'].update(recheck='not_attempted', close='not_opened')
            runtime.control_observation.update(phase='missing_invocation_proof', authority_phase='delete_open',
                receipt_observation={'kind': 'eligibility', 'phase': 'snapshot_before',
                    'reason': 'receipt_operation_unavailable', 'close': 'not_opened'})
            self.assertTrue(runtime.cleanup())
        states = [('not_returned', None), ('entered', None), ('returned_true', None),
                  ('call_raised', None), ('error_read_raised', None),
                  ('returned_false', 'sharing_32'), ('returned_false', 'access_5'),
                  ('returned_false', 'other')]
        for call, error in states:
            runtime.control_observation.update(replacement_call=call, replacement_error=error)
            witness = native.failure_witness(runtime)
            self.assertEqual('returned', witness['outcome_state'])
            self.assertLessEqual(len(json.dumps(witness).encode()) + 1, 2048)
            harness = cli.FinalizationControls()
            args = harness.harness()
            try:
                def execute(session, unused_runtime, observer, progress):
                    progress.update(stage='controls', failure_witness=witness,
                        source_integrity_verified=True, receipt_sha256='a'*64,
                        failed_control='snapshot_share_receipt_success',
                        failure_emission_control={'verified': True, 'native_control_qualified': False})
                    raise native.ControlError('control_native_sharing_unexpected')
                with mock.patch.object(first, 'execute', execute):
                    self.assertEqual(2, first.main(args))
                lines = harness.stdout.getvalue().splitlines(keepends=True)
                row = json.loads(lines[-1])
                self.assertEqual('compact_first_summary', row['event'])
                self.assertEqual(witness, row['failure_witness'])
                self.assertLessEqual(len(lines[-1].encode()), 4096)
                self.assertLessEqual(len(harness.stdout.getvalue().encode()), 4*1024*1024)
                self.assertEqual('inconclusive', row['status'])
                harness.runtime.cleanup.assert_called_once()
                harness.session.cleanup.assert_called_once()
            finally:
                harness.doCleanups()

    def test_projector_fault_on_replacement_failure_keeps_terminal_and_cleanup(self):
        import test_compact_first_control as cli
        harness = cli.FinalizationControls()
        args = harness.harness()
        try:
            api = fixtures.SharingNative()
            runtime, _, _ = fixtures.NativePacketControls().runtime(api)
            runtime.clock = lambda: harness.clock[0]
            runtime.cleanup = mock.Mock(wraps=runtime.cleanup)
            calls = []
            def move(*args):
                calls.append('move')
                raise OSError('PRIVATE_REPLACEMENT')
            api.kernel.MoveFileExW.call = move
            def execute(session, runtime, observer, progress):
                progress['stage'] = 'controls'
                first.perform_controls(observer.parent, runtime, progress)
            with mock.patch.object(first, 'make_runtime', return_value=runtime), \
                 mock.patch.object(first, 'execute', execute), \
                 mock.patch.object(native, 'failure_witness', side_effect=OSError('PRIVATE_PROJECTOR')):
                self.assertEqual(2, first.main(args))
            line = harness.stdout.getvalue().splitlines(keepends=True)[-1]
            row = json.loads(line)
            self.assertIsNone(row['failure_witness'])
            self.assertEqual({'stage': 'controls', 'reason': 'control_proof_failed'}, row['failure'])
            self.assertEqual('inconclusive', row['status'])
            self.assertLessEqual(len(line.encode()), 4096)
            self.assertNotIn('PRIVATE_', harness.stdout.getvalue() + harness.stderr.getvalue())
            self.assertEqual(['move'], calls)
            self.assertFalse(api.disposed)
            runtime.cleanup.assert_called_once()
            harness.session.cleanup.assert_called_once()
        finally:
            harness.doCleanups()


if __name__ == '__main__':
    unittest.main()
