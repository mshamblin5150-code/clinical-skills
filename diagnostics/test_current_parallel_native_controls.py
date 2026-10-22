"""Portable P18 control receipt proofs; no native or application execution."""
import json
import unittest
from dataclasses import replace
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
from windows_job_probe import ProbeResult, ProbeSnapshot

from current_parallel_native_controls import encode_receipt, read_receipt


class ReceiptTests(unittest.TestCase):
    def test_exact_three_controls_round_trip_without_private_evidence(self):
        report = {
            'schema': 'current-parallel-native-controls-v1', 'status': 'passed',
            'control_ids': ['dual_owner_reverse_completion', 'failure_hung_sibling_drained',
                            'coordinator_death_two_active_trees'],
            'passed_control_ids': ['dual_owner_reverse_completion', 'failure_hung_sibling_drained',
                                   'coordinator_death_two_active_trees'],
            'planned_count': 3, 'passed_count': 3, 'failed_count': 0, 'skipped_count': 0,
            'diagnostic_codes': [], 'process_cleanup_verified': True, 'files_retained': True,
        }
        raw = encode_receipt(report)
        self.assertEqual(read_receipt(raw), report)
        self.assertEqual(json.loads(raw)['status'], 'passed')



class GateFailureTests(unittest.TestCase):
    def test_unsupported_platform_is_finite_failure_and_does_not_claim_cleanup(self):
        from current_parallel_native_controls import run_controls
        report = run_controls(None, platform='synthetic-non-Windows')
        self.assertEqual((report['status'], report['passed_count'], report['failed_count'],
                          report['skipped_count'], report['diagnostic_codes'],
                          report['process_cleanup_verified']),
                         ('failed', 0, 1, 2, ['control_platform_unsupported'], False))
        self.assertEqual(read_receipt(encode_receipt(report)), report)


class Clock:
    def __init__(self):
        self.now = time.monotonic()
    def __call__(self):
        return self.now
    def sleep(self, seconds):
        self.now += max(seconds, .1)


class FakeOwner:
    def __init__(self, factory, argv, cwd, env, report_dir):
        self.factory, self.report_dir = factory, Path(report_dir)
        self.argv = argv
        self.report_dir.mkdir()
        self.stdout_path = self.report_dir / 'stdout.bin'
        self.stderr_path = self.report_dir / 'stderr.bin'
        self.stdout_path.write_bytes(b'')
        self.stderr_path.write_bytes(b'')
        self.result = None
        self.guard = '--coordinator' in argv
        self.root_dead = False
        self.case = Path(cwd)
        self.temporary = Path(env.get('TEMP', cwd))
        self.pid = factory.next_pid()
        self.identities = [self.pid]
        factory.processes[self.pid] = [self.pid * 10, True]
        if self.guard:
            for index in (1, 2):
                temporary = self.case / 'pair' / 'temporary' / ('command-%04d' % index)
                temporary.mkdir(parents=True)
                for role in ('root', 'child', 'grandchild'):
                    pid = factory.next_pid()
                    factory.processes[pid] = [pid * 10, True]
                    self.identities.append(pid)
                    (temporary / (role + '.pid')).write_text(str(pid))
                    (temporary / (role + '.creation')).write_text(str(pid * 10))
            (self.case / 'coordinator.ready').write_text('ready')
        else:
            self.mode = (self.case.parent.parent / 'mode').read_text()
            self.lane = int(argv[-2][-1])
            self.identities.extend([factory.next_pid(), factory.next_pid()])
            for role, pid in zip(('root', 'child', 'grandchild'), self.identities):
                factory.processes[pid] = [pid * 10, True]
                (self.temporary / (role + '.pid')).write_text(str(pid))
                (self.temporary / (role + '.creation')).write_text(str(pid * 10))
            self.stdout_path.write_bytes(('lane%d:root\nlane%d:child\nlane%d:grandchild\n' %
                                         (self.lane, self.lane, self.lane)).encode())
            self.stderr_path.write_bytes(('lane%d:stderr\nRan 1 test in 0.001s\n\nOK\n' % self.lane).encode())

    def poll(self):
        if self.result:
            return self.result.snapshot
        if not self.guard and (self.temporary / 'release').exists():
            for pid in self.identities:
                self.factory.processes[pid][1] = False
            self.root_dead = True
        if not self.guard and (self.temporary / 'fail').exists():
            self.factory.processes[self.pid][1] = False
            self.root_dead = True
        active = sum(self.factory.processes[pid][1] or
                     (self.factory.references_retain_count and
                      any(witness.pid == pid and not witness.closed for witness in self.factory.witnesses))
                     for pid in self.identities)
        code = 7 if not self.guard and (self.temporary / 'fail').exists() else 0
        return ProbeSnapshot(self.pid, code if self.root_dead else None, self.root_dead,
                             active, len(self.identities), .1, .1, .2, False, 'running')

    def finish(self, timeout):
        if self.guard and self.factory.finish_late:
            self.factory.clock.now += 121
        self.result = ProbeResult(replace(self.poll(), cleanup_verified=True, state='closed'),
                                  'completed', str(self.stdout_path), str(self.stderr_path), ())
        return self.result

    def cancel(self, reason, timeout):
        for pid in self.identities:
            self.factory.processes[pid][1] = False
        self.root_dead = True
        self.result = ProbeResult(replace(self.poll(),
                                  cleanup_verified=not self.factory.bad_cleanup and
                                  self.poll().active_processes == 0, state='closed'),
                                  reason, str(self.stdout_path), str(self.stderr_path), ())
        return self.result


class FakeFactory:
    def __init__(self):
        self.processes, self.owners, self.witnesses = {}, [], []
        self.counter = 100
        self.bad_cleanup = False
        self.survive_death = False
        self.cross_wire_capture = False
        self.finish_late = False
        self.partial_start = False
        self.bad_identity = False
        self.references_retain_count = False
        self.fail_witness_number = None
    def next_pid(self):
        self.counter += 1
        return self.counter
    def start(self, argv, *, cwd, env, report_dir):
        owner = FakeOwner(self, argv, cwd, env, report_dir)
        if self.cross_wire_capture and len(self.owners) == 1:
            owner.stdout_path.write_bytes(self.owners[0].stdout_path.read_bytes())
        self.owners.append(owner)
        if self.partial_start and len(self.owners) == 2:
            error = RuntimeError("private native path /secret/owner, PID 987654")
            error.owner = owner
            raise error
        return owner
    def witness(self, pid, creation):
        factory = self
        if (self.bad_identity or self.fail_witness_number == len(self.witnesses) + 1
                or self.processes[pid] != [creation, True]):
            raise RuntimeError('private identity failure')
        class Witness:
            closed = False
            def signaled(self):
                return not factory.processes[pid][1]
            def close(self):
                self.closed = True
        witness = Witness()
        witness.pid = pid
        self.witnesses.append(witness)
        return witness
    def kill_coordinator(self, owner):
        identities = owner.identities[:1] if self.survive_death else owner.identities
        for pid in identities:
            self.processes[pid][1] = False
        owner.root_dead = True


class PortableControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dual-owner-controls-synthetic-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'evidence'
        self.clock, self.factory = Clock(), FakeFactory()
        self.factory.clock = self.clock

    def run_controls(self):
        from current_parallel_native_controls import ControlRuntime, run_controls
        runtime = ControlRuntime(owner_factory=self.factory, witness_factory=self.factory.witness,
                                 terminate_coordinator=self.factory.kill_coordinator,
                                 clock=self.clock, sleep=self.clock.sleep,
                                 environment={'SYSTEMROOT': 'synthetic-system'},
                                 disk_usage=lambda root: SimpleNamespace(free=2**40))
        return run_controls(self.root, runtime=runtime, platform='nt')

    def test_three_controls_qualify_actual_caller_with_fake_native_boundary(self):
        report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['process_cleanup_verified']),
                         ('passed', 3, True))
        self.assertEqual(report['passed_control_ids'], ['dual_owner_reverse_completion',
                         'failure_hung_sibling_drained', 'coordinator_death_two_active_trees'])
        self.assertEqual(sum(alive for creation, alive in self.factory.processes.values()), 0)
        self.assertEqual(sum(witness.closed for witness in self.factory.witnesses), 18)
        self.assertEqual(read_receipt((self.root / 'receipt.json').read_bytes()), report)

    def test_failure_payload_preserves_root_exit_code_at_native_launch_boundary(self):
        from unittest import mock
        import runpy
        import sys
        report = self.run_controls()
        self.assertEqual(report['status'], 'passed')
        argv = self.factory.owners[2].argv
        with mock.patch.object(runpy, 'run_path', return_value={'tree': lambda *args: 7}), \
             mock.patch.object(sys, 'argv', argv[2:]), \
             mock.patch.dict(os.environ, {'TEMP': str(self.root)}):
            with self.assertRaises(SystemExit) as caught:
                exec(argv[2], {})
        self.assertEqual(caught.exception.code, 7)

    def test_cross_wired_capture_cannot_qualify_reverse_completion(self):
        self.factory.cross_wire_capture = True
        report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['diagnostic_codes'],
                          report['process_cleanup_verified']),
                         ('failed', 0, ['control_proof_failed'], True))
        self.assertEqual(sum(alive for creation, alive in self.factory.processes.values()), 0)

    def test_outer_guard_cleanup_does_not_disguise_failed_coordinator_death(self):
        self.factory.survive_death = True
        report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['diagnostic_codes'],
                          report['process_cleanup_verified']),
                         ('failed', 2, ['control_deadline'], True))
        self.assertEqual(sum(alive for creation, alive in self.factory.processes.values()), 0)
        self.assertEqual((self.root / 'coordinator_death_two_active_trees' / 'guard' / 'stdout.bin').is_file(), True)

    def test_failed_tree_drain_remains_failed_even_when_cancel_returns(self):
        self.factory.bad_cleanup = True
        report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['process_cleanup_verified']),
                         ('failed', 1, False))
        self.assertEqual(report['failed_count'], 1)
        self.assertEqual(read_receipt((self.root / 'receipt.json').read_bytes()), report)

    def test_strict_gate_rejects_false_populations_and_private_fields(self):
        from current_parallel_native_controls import ControlError
        report = self.run_controls()
        self.assertEqual(report['status'], 'passed')
        invalids = [dict(report, passed_count=True),
                    dict(report, control_ids=report['control_ids'][:-1] + [report['control_ids'][0]]),
                    dict(report, passed_control_ids=list(reversed(report['passed_control_ids']))),
                    dict(report, process_cleanup_verified=1),
                    dict(report, private_path='/private/evidence'),
                    dict(report, diagnostic_codes=['/private/failure']),
                    dict(report, passed_count=float('nan'))]
        for invalid in invalids:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ControlError) as caught:
                    encode_receipt(invalid)
                self.assertEqual(caught.exception.code, 'control_receipt_invalid')
        raw = encode_receipt(report)
        invalid_bytes = [raw.replace(b'"status":"passed"', b'"status":"passed","status":"passed"'),
                         raw + b'\n', b' ' * (16 * 1024 + 1), b'{', b'[]']
        for invalid in invalid_bytes:
            with self.assertRaises(ControlError) as caught:
                read_receipt(invalid)
            self.assertEqual(caught.exception.code, 'control_receipt_invalid')

    def test_launched_fixture_loads_helpers_without_inherited_pythonpath(self):
        from unittest import mock
        import importlib.machinery
        import runpy
        import sys
        report = self.run_controls()
        self.assertEqual(report['status'], 'passed')
        argv = self.factory.owners[0].argv
        def read_script(path):
            spec = importlib.machinery.PathFinder.find_spec('windows_job_probe_controls', sys.path)
            self.assertIsNotNone(spec)
            self.assertEqual(Path(spec.origin).name, 'windows_job_probe_controls.py')
            return {'tree': lambda *args: 7}
        without_helpers = [entry for entry in sys.path
                           if not (Path(entry) / 'windows_job_probe_controls.py').is_file()]
        with mock.patch.object(runpy, 'run_path', side_effect=read_script), \
             mock.patch.object(sys, 'argv', argv[2:]), \
             mock.patch.object(sys, 'path', without_helpers), \
             mock.patch.dict(os.environ, {'TEMP': str(self.root)}):
            with self.assertRaises(SystemExit) as caught:
                exec(argv[2], {})
        self.assertEqual(caught.exception.code, 7)

    def test_late_final_drain_cannot_issue_successful_qualification(self):
        self.factory.finish_late = True
        report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['diagnostic_codes']),
                         ('failed', 2, ['control_deadline']))
        self.assertEqual(report['process_cleanup_verified'], True)

    def test_partial_start_is_retained_and_drained_without_private_error_leakage(self):
        self.factory.partial_start = True
        report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['diagnostic_codes'],
                          report['process_cleanup_verified']),
                         ('failed', 0, ['control_unavailable'], True))
        self.assertEqual(sum(alive for creation, alive in self.factory.processes.values()), 0)
        self.assertNotIn(b'/secret/', encode_receipt(report))
        self.assertNotIn(b'987654', encode_receipt(report))
        self.assertEqual((self.root / 'dual_owner_reverse_completion' / 'capture' /
                          'command-0002' / 'stdout.bin').is_file(), True)

    def test_unmatched_creation_identity_never_counts_as_witnessed_success(self):
        self.factory.bad_identity = True
        report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['diagnostic_codes'],
                          report['process_cleanup_verified']),
                         ('failed', 0, ['control_unavailable'], True))
        self.assertEqual(sum(alive for creation, alive in self.factory.processes.values()), 0)

    def test_optimized_native_route_refuses_before_starting_any_tree(self):
        from unittest import mock
        import sys
        with mock.patch.object(sys, 'flags', SimpleNamespace(optimize=1)):
            report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['diagnostic_codes'],
                          report['process_cleanup_verified']),
                         ('failed', 0, ['control_optimization_unsupported'], False))
        self.assertEqual(len(self.factory.owners), 0)

    def test_witness_references_are_released_before_job_drain_checks(self):
        self.factory.references_retain_count = True
        report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['process_cleanup_verified']),
                         ('passed', 3, True))
        self.assertEqual(sum(witness.closed for witness in self.factory.witnesses), 18)

    def test_partial_witness_failure_closes_references_before_failure_cleanup(self):
        self.factory.references_retain_count = True
        self.factory.fail_witness_number = 2
        report = self.run_controls()
        self.assertEqual((report['status'], report['passed_count'], report['diagnostic_codes'],
                          report['process_cleanup_verified']),
                         ('failed', 0, ['control_unavailable'], True))
        self.assertEqual(sum(alive for creation, alive in self.factory.processes.values()), 0)


if __name__ == '__main__':
    unittest.main()
