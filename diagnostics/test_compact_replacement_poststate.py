"""Portable sampled poststate seam; no Windows qualification."""
import contextlib
import io
import os
from pathlib import Path
import tempfile
import time
import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest import mock

import generated_output_contract as contract
import compact_native_controls as controls
import test_compact_native_controls as fixtures
SharingNative = fixtures.SharingNative
import compact_replacement_poststate as proof


class PoststateTests(unittest.TestCase):
    def test_unchanged_names_objects_bytes_and_closed_observers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            destination, source = root/'receipt', root/'replacement'
            destination.write_bytes(b'original receipt')
            source.write_bytes(proof.REPLACEMENT_BYTES)
            api = controls.ObservedAPI(SharingNative())
            authority = api.open(destination)
            baseline = (api.record(authority), api.read(authority, 16384, time.monotonic()+30))
            held = dict(api.handles)
            witness = {}
            check = proof.ReplacementPoststate(api, authority, destination, source,
                baseline=baseline, deadline=time.monotonic()+30, observation=witness)
            check.prepare()
            self.assertEqual(held, api.handles)
            check.verify()
            self.assertEqual(held, api.handles)
            self.assertEqual('verified', witness['replacement_poststate'])
            api.close(authority)

    def test_first_control_supplement_verifies_but_error5_still_refuses(self):
        for error, accepted in ((32, True), (5, False)):
            with self.subTest(error=error), tempfile.TemporaryDirectory() as tmp:
                api = SharingNative()
                runtime, _, _ = fixtures.NativePacketControls().runtime(api)
                runtime.replacement_poststate = True
                api.c.get_last_error = lambda: error if runtime.control_observation['authority_phase'] == 'replace' else 32
                with contextlib.redirect_stdout(io.StringIO()):
                    if accepted:
                        controls.run_control('snapshot_share_receipt_success', Path(tmp)/'new', runtime)
                    else:
                        with self.assertRaises(controls.ControlError):
                            controls.run_control('snapshot_share_receipt_success', Path(tmp)/'new', runtime)
                self.assertEqual('verified', controls.failure_witness(runtime)['replacement_poststate'])
                if not accepted:
                    self.assertFalse(api.disposed)
                self.assertTrue(runtime.cleanup())


class NamespaceAPI:
    """Independent path->object and handle->object maps, immutable full IDs.

    Mutating names never changes a held handle's binding. Deliberately independent
    identity and byte lookup supports same-byte/different-ID discrimination.
    """
    def __init__(self, root):
        import stat
        self.names = {root/'receipt': 101, root/'replacement': 202}
        self.objects = {101: [b'original receipt', None], 202: [proof.REPLACEMENT_BYTES, None]}
        for identity, row in self.objects.items():
            row[1] = contract.WindowsSnapshot(77, identity, stat.S_IFREG|0o600,
                1, len(row[0]), 10, 20, 0, 30, 1, 0, False)
        self.handles, self.next = {}, 0
        self.read_from = self.record_from = None
        self.close_fails = False

    def open(self, path):
        identity = self.names[path]
        self.next += 1
        self.handles[self.next] = identity
        return self.next

    def read(self, handle, limit, deadline):
        return self.objects[self.read_from or self.handles[handle]][0]

    def record(self, handle):
        return self.objects[self.record_from or self.handles[handle]][1]

    def close(self, handle):
        del self.handles[handle]
        if self.close_fails:
            raise OSError('PRIVATE_CLOSE')


class NamespaceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path('/synthetic')
        self.native = NamespaceAPI(self.root)
        self.api = controls.ObservedAPI(self.native)
        self.authority = self.api.open(self.root/'receipt')
        self.baseline = (self.api.record(self.authority), self.api.read(self.authority, 16384, 0))
        self.observation = {}
        self.chain = [('parent', 77, 303)]
        self.check = proof.ReplacementPoststate(self.api, self.authority, self.root/'receipt',
            self.root/'replacement', baseline=self.baseline, deadline=time.monotonic()+30,
            observation=self.observation, directory=lambda _: tuple(self.chain))

    def assert_refused(self, operation):
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(Exception):
            operation()
        self.assertEqual('failed', self.observation['replacement_poststate'])

    def test_equal_bytes_rebound_name_is_not_original_held_object(self):
        self.check.prepare()
        self.native.objects[404] = [self.baseline[1], replace(self.baseline[0], st_ino=404)]
        self.native.names[self.root/'receipt'] = 404
        self.assert_refused(self.check.verify)
        self.assertEqual(self.baseline[0], self.api.record(self.authority))

    def test_source_missing_rebound_and_changed_are_independently_refused(self):
        for change in ('missing', 'rebound', 'bytes'):
            with self.subTest(change=change):
                self.setUp()
                self.check.prepare()
                if change == 'missing':
                    del self.native.names[self.root/'replacement']
                elif change == 'rebound':
                    self.native.objects[505] = [proof.REPLACEMENT_BYTES,
                        replace(self.native.objects[202][1], st_ino=505)]
                    self.native.names[self.root/'replacement'] = 505
                else:
                    self.native.objects[202][0] = b'X' * len(proof.REPLACEMENT_BYTES)
                self.assert_refused(self.check.verify)
                self.assertEqual({self.authority: self.root/'receipt'}, self.api.handles)

    def test_full_snapshot_prerequisites_and_same_volume(self):
        changes = ({'st_dev': 78}, {'st_ino': 101}, {'st_nlink': 2},
            {'st_file_attributes': 0x400, 'reparse_tag': 1}, {'delete_pending': True},
            {'st_file_attributes': 1}, {'st_file_attributes': 2},
            {'st_file_attributes': 4}, {'st_file_attributes': 0x100})
        for change in changes:
            with self.subTest(change=change):
                self.setUp()
                self.native.objects[202][1] = replace(self.native.objects[202][1], **change)
                self.assert_refused(self.check.prepare)

    def test_changed_parent_chain_and_deadline_fail_closed(self):
        self.check.prepare()
        self.chain[0] = ('parent', 77, 606)
        self.assert_refused(self.check.verify)
        self.setUp()
        self.check.deadline = 0
        self.assert_refused(self.check.prepare)

    def test_close_failure_and_observer_leaks_before_move_or_delete(self):
        for stage in ('prepare', 'verify'):
            for fault in ('close', 'leak'):
                with self.subTest(stage=stage, fault=fault):
                    self.setUp()
                    if stage == 'verify':
                        self.check.prepare()
                    if fault == 'close':
                        self.native.close_fails = True
                    else:
                        self.api.close = lambda handle: None
                    self.assert_refused(getattr(self.check, stage))

    def test_wrong_handle_identity_and_mixed_handle_bytes_fail_closed(self):
        # Cached original metadata on the replacement is not proof of its ID.
        self.native.record_from = 101
        self.assert_refused(self.check.prepare)
        self.setUp()
        self.check.prepare()
        self.native.read_from = 202
        self.assert_refused(self.check.verify)

    def test_handoff_baseline_and_authority_lifetime_are_not_replaceable(self):
        self.check.baseline = (replace(self.baseline[0], st_ino=808), self.baseline[1])
        self.assert_refused(self.check.prepare)
        self.setUp()
        self.check.prepare()
        self.api.lifetimes[self.authority] += 1
        self.assert_refused(self.check.verify)

    def test_unstable_or_partial_reads_and_receipt_limit(self):
        self.check.prepare()
        original = self.native.record
        count = [0]
        def unstable(handle):
            count[0] += 1
            return replace(original(handle), st_ctime_ns=20+count[0])
        self.native.record = unstable
        self.assert_refused(self.check.verify)
        self.setUp()
        self.native.objects[101][0] = b'short'
        self.assert_refused(self.check.prepare)
        self.setUp()
        self.native.objects[101] = [b'x'*16385, replace(self.baseline[0], st_size=16385)]
        self.assert_refused(self.check.prepare)


class IntegratedPoststateTests(unittest.TestCase):
    def test_actual_same_byte_namespace_replacement_refuses_true_and_false(self):
        for returned in (1, 0):
            with self.subTest(returned=returned), tempfile.TemporaryDirectory() as tmp:
                api = SharingNative()
                runtime, _, _ = fixtures.NativePacketControls().runtime(api)
                runtime.replacement_poststate = True
                deletes = []
                def move(source, destination, flags):
                    # Actual synthetic namespace mutation: old handle still owns
                    # the old object, new name holds another same-byte object.
                    replacement = Path(tmp)/'same-byte-object'
                    replacement.write_bytes(Path(destination).read_bytes())
                    os.replace(replacement, destination)
                    return returned
                api.kernel.MoveFileExW.call = move
                api.kernel.DeleteFileW.call = lambda *args: deletes.append(args) or 0
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(controls.ControlError):
                    controls.run_control('snapshot_share_receipt_success', Path(tmp)/'new', runtime)
                self.assertEqual([], deletes)
                self.assertFalse(api.disposed)
                witness = controls.failure_witness(runtime)
                self.assertEqual('prepared' if returned else 'failed', witness['replacement_poststate'])
                self.assertTrue(runtime.cleanup())

    def test_observers_absent_at_both_native_challenges_and_marks(self):
        with tempfile.TemporaryDirectory() as tmp:
            api = SharingNative()
            runtime, _, _ = fixtures.NativePacketControls().runtime(api)
            runtime.replacement_poststate = True
            calls = []
            def attack(label):
                names = sorted(row['path'].name for row in api.handles.values())
                self.assertEqual(['compact-000001-eligibility.json', 'stderr.bin', 'stdout.bin'], names)
                calls.append(label)
                return 0
            api.kernel.MoveFileExW.call = lambda *args: attack('move')
            api.kernel.DeleteFileW.call = lambda *args: attack('delete')
            with contextlib.redirect_stdout(io.StringIO()):
                controls.run_control('snapshot_share_receipt_success', Path(tmp)/'new', runtime)
            self.assertEqual(['move', 'delete'], calls)
            self.assertEqual([3, 2], [len(row) for row in api.mark_barriers])
            self.assertTrue(runtime.cleanup())

    def test_known_error5_remains_primary_when_poststate_also_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            api = SharingNative()
            runtime, _, _ = fixtures.NativePacketControls().runtime(api)
            runtime.replacement_poststate = True
            def move(source, destination, flags):
                Path(source).write_bytes(b'X' * len(proof.REPLACEMENT_BYTES))
                return 0
            api.kernel.MoveFileExW.call = move
            api.c.get_last_error = lambda: 5 if runtime.control_observation['authority_phase'] == 'replace' else 32
            caught = []
            original = controls._authority_denials
            def boundary(pair):
                try:
                    return original(pair)
                except BaseException as error:
                    caught.append(error)
                    raise
            with mock.patch.object(controls, '_authority_denials', boundary), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(controls.ControlError):
                    controls.run_control('snapshot_share_receipt_success', Path(tmp)/'new', runtime)
            self.assertEqual('control_native_sharing_unexpected', caught[0].code)
            self.assertEqual('failed', controls.failure_witness(runtime)['replacement_poststate'])
            self.assertFalse(api.disposed)
            self.assertTrue(runtime.cleanup())

    def test_call_and_error_exceptions_are_not_replaced_by_supplement(self):
        for where in ('call', 'getter'):
            with self.subTest(where=where), tempfile.TemporaryDirectory() as tmp:
                api = SharingNative()
                runtime, _, _ = fixtures.NativePacketControls().runtime(api)
                runtime.replacement_poststate = True
                original_error = OSError('PRIVATE_ORIGINAL')
                def fail():
                    raise original_error
                api.kernel.MoveFileExW.call = lambda *args: fail() if where == 'call' else 0
                api.c.get_last_error = lambda: fail() if runtime.control_observation['authority_phase'] == 'replace' else 32
                caught = []
                original = controls._authority_denials
                def boundary(pair):
                    try:
                        return original(pair)
                    except BaseException as error:
                        caught.append(error)
                        raise
                with mock.patch.object(controls, '_authority_denials', boundary), contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(controls.ControlError):
                        controls.run_control('snapshot_share_receipt_success', Path(tmp)/'new', runtime)
                self.assertIs(original_error, caught[0])
                self.assertFalse(api.disposed)
                self.assertTrue(runtime.cleanup())

    def test_public_projection_does_not_copy_arbitrary_proof_data(self):
        for value in ('PRIVATE_PATH_BYTES_ID', {}, [], 1, True, None):
            witness = controls.failure_witness(SimpleNamespace(control_observation={
                'control': 'snapshot_share_receipt_success', 'replacement_poststate': value}))
            self.assertIsNone(witness['replacement_poststate'])
            self.assertNotIn('PRIVATE', str(witness))


class ObservationFaultTests(unittest.TestCase):
    def test_missing_malformed_and_explicit_initial_status_are_distinct(self):
        for row in ({}, {'replacement_poststate': {}}, {'replacement_poststate': 'PRIVATE'},
                    {'replacement_poststate': None}, {'replacement_poststate': True}):
            witness = controls.failure_witness(SimpleNamespace(control_observation={
                'control': 'snapshot_share_receipt_success', 'phase': 'retirement_proof', **row}))
            self.assertIsNone(witness['replacement_poststate'])
        witness = controls.failure_witness(SimpleNamespace(control_observation={
            'control': 'snapshot_share_receipt_success', 'replacement_poststate': 'not_checked'}))
        self.assertEqual('not_checked', witness['replacement_poststate'])

    def test_prepare_verify_preserve_primary_when_failure_observation_raises(self):
        class BrokenObservation(dict):
            def __setitem__(self, key, value):
                if value == 'failed':
                    if after_write:
                        dict.__setitem__(self, key, 'verified')
                    raise RuntimeError('PRIVATE_SECONDARY')
                return super().__setitem__(key, value)
            def pop(self, *args):
                raise RuntimeError('PRIVATE_POP')
        for stage, after_write in (('prepare', False), ('verify', False),
                                   ('prepare', True), ('verify', True)):
            with self.subTest(stage=stage, after_write=after_write):
                fixture = NamespaceTests()
                fixture.setUp()
                observation = BrokenObservation()
                check = proof.ReplacementPoststate(fixture.api, fixture.authority,
                    fixture.root/'receipt', fixture.root/'replacement', baseline=fixture.baseline,
                    deadline=time.monotonic()+30, observation=observation, directory=lambda _: ())
                if stage == 'verify':
                    check.prepare()
                    check.verify()
                    self.assertEqual('verified', observation['replacement_poststate'])
                primary = OSError('PRIVATE_PRIMARY')
                def fail(handle):
                    raise primary
                fixture.native.record = fail
                with self.assertRaises(OSError) as caught:
                    getattr(check, stage)()
                self.assertIs(primary, caught.exception)
                self.assertNotIn('replacement_poststate', observation)
                witness = controls.failure_witness(SimpleNamespace(control_observation={
                    'control': 'snapshot_share_receipt_success', **observation}))
                self.assertIsNone(witness['replacement_poststate'])

    def test_maximum_explicit_status_uses_actual_bounded_cli_transport(self):
        import test_compact_replacement_witness as transport
        original = controls.failure_witness
        def explicit_status(runtime):
            runtime.control_observation['replacement_poststate'] = 'not_checked'
            return original(runtime)
        with mock.patch.object(controls, 'failure_witness', explicit_status):
            transport.ReplacementWitness().test_maximal_valid_witness_uses_actual_cli_transport_within_caps()
