"""Three private Windows dual-owner caller controls, not a launch authorization.

Portable tests inject only synthetic owners/witnesses/clocks. Native execution
requires a separately authorized Windows run. All capture and identity evidence
is retained; cleanup means process/handle drain, never file deletion.
"""
from __future__ import annotations

import json
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from windows_job_probe import WindowsJobProbe
from windows_job_probe_controls import ProcessWitness, read_pid, write_pid

SCHEMA = 'current-parallel-native-controls-v1'
CONTROL_IDS = ('dual_owner_reverse_completion', 'failure_hung_sibling_drained',
               'coordinator_death_two_active_trees')
MAX_RECEIPT_BYTES = 16 * 1024
DIAGNOSTICS = frozenset({'control_platform_unsupported', 'control_optimization_unsupported',
                       'control_deadline', 'control_proof_failed', 'control_cleanup_unverified',
                       'control_unavailable', 'control_receipt_invalid'})


class ControlError(RuntimeError):
    def __init__(self, code):
        self.code = code if code in DIAGNOSTICS else 'control_unavailable'
        super().__init__(self.code)


def _require(value, code='control_proof_failed'):
    if not value:
        raise ControlError(code)


def encode_receipt(report):
    """Validate exact finite public population before serialization."""
    keys = {'schema', 'status', 'control_ids', 'passed_control_ids', 'planned_count',
            'passed_count', 'failed_count', 'skipped_count', 'diagnostic_codes',
            'process_cleanup_verified', 'files_retained'}
    _require(type(report) is dict and set(report) == keys, 'control_receipt_invalid')
    _require(report['schema'] == SCHEMA and report['status'] in ('passed', 'failed'),
             'control_receipt_invalid')
    _require(type(report['control_ids']) is list and report['control_ids'] == list(CONTROL_IDS),
             'control_receipt_invalid')
    for key in ('planned_count', 'passed_count', 'failed_count', 'skipped_count'):
        _require(type(report[key]) is int and 0 <= report[key] <= 3, 'control_receipt_invalid')
    passed = report['passed_count']
    _require(report['planned_count'] == 3 and type(report['passed_control_ids']) is list
             and report['passed_control_ids'] == list(CONTROL_IDS[:passed]),
             'control_receipt_invalid')
    codes = report['diagnostic_codes']
    _require(type(codes) is list and all(type(x) is str and x in DIAGNOSTICS for x in codes)
             and len(codes) == len(set(codes)), 'control_receipt_invalid')
    _require(type(report['process_cleanup_verified']) is bool and report['files_retained'] is True,
             'control_receipt_invalid')
    if report['status'] == 'passed':
        _require(passed == 3 and report['failed_count'] == report['skipped_count'] == 0
                 and not codes and report['process_cleanup_verified'], 'control_receipt_invalid')
    else:
        _require(report['failed_count'] == 1 and passed <= 2 and report['skipped_count'] == 2-passed
                 and bool(codes), 'control_receipt_invalid')
    raw = json.dumps(report, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('ascii')
    _require(len(raw) <= MAX_RECEIPT_BYTES, 'control_receipt_invalid')
    return raw


def read_receipt(raw):
    """Reject duplicate/unknown fields and noncanonical or overlong receipts."""
    _require(type(raw) is bytes and len(raw) <= MAX_RECEIPT_BYTES, 'control_receipt_invalid')
    def pairs(items):
        value = {}
        for key, item in items:
            _require(key not in value, 'control_receipt_invalid')
            value[key] = item
        return value
    try:
        report = json.loads(raw, object_pairs_hook=pairs)
        _require(encode_receipt(report) == raw, 'control_receipt_invalid')
        return report
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise ControlError('control_receipt_invalid') from None


def _report(passed, diagnostic=None, cleanup=False):
    failed = diagnostic is not None
    report = {'schema': SCHEMA, 'status': 'failed' if failed else 'passed',
              'control_ids': list(CONTROL_IDS), 'passed_control_ids': list(CONTROL_IDS[:passed]),
              'planned_count': 3, 'passed_count': passed, 'failed_count': int(failed),
              'skipped_count': 2-passed if failed else 0,
              'diagnostic_codes': [diagnostic] if failed else [],
              'process_cleanup_verified': cleanup, 'files_retained': True}
    encode_receipt(report)
    return report


SCRIPT = Path(__file__).resolve()
WORK_SECONDS = 90.0
CLEANUP_SECONDS = 30.0
ROLES = ('root', 'child', 'grandchild')
MODULES = ('test_control_lane0', 'test_control_lane1')


class _NativeWitness:
    def __init__(self, pid, creation):
        self.witness = ProcessWitness(pid, creation)
    def signaled(self):
        value = self.witness.kernel.WaitForSingleObject(self.witness.handle, 0)
        _require(value in (0, 0x102))
        return value == 0
    def close(self):
        self.witness.close()


def _kill_original_coordinator(owner):
    # Same original CreateProcess handle and operation as the existing native
    # coordinator-death control. No PID-opened termination rights are added.
    owner._api.terminate_process(owner._info.hProcess)


class _TrackedOwners:
    def __init__(self, factory):
        self.factory, self.owners = factory, []
    def start(self, *args, **kwargs):
        try:
            owner = self.factory.start(*args, **kwargs)
        except BaseException as error:
            owner = getattr(error, 'owner', None)
            if owner is not None and all(owner is not item for item in self.owners):
                self.owners.append(owner)
            raise
        self.owners.append(owner)
        return owner
    def for_handle(self, handle):
        owners = [owner for owner in self.owners if Path(owner.report_dir) == handle.report_dir]
        _require(len(owners) == 1)
        return owners[0]


class ControlRuntime:
    """Portable native-boundary seam, never selected through the CLI."""
    def __init__(self, *, owner_factory=WindowsJobProbe, witness_factory=_NativeWitness,
                 terminate_coordinator=_kill_original_coordinator, clock=time.monotonic,
                 sleep=time.sleep, environment=None, disk_usage=shutil.disk_usage):
        self.owners = _TrackedOwners(owner_factory)
        self.witness_factory, self.terminate_coordinator = witness_factory, terminate_coordinator
        self.clock, self.sleep = clock, sleep
        self.environment = dict(os.environ if environment is None else environment)
        self.disk_usage = disk_usage
        self.runners, self.witnesses = [], []
        self.deadline = self.hard_deadline = None

    def wait(self, predicate):
        while self.clock() < self.deadline:
            value = predicate()
            if value:
                return value
            self.sleep(min(.02, self.deadline - self.clock()))
        raise ControlError('control_deadline')

    def witness(self, temporary):
        result = []
        for role in ROLES:
            pid = self.wait(lambda: read_pid(temporary / (role + '.pid')))
            creation = self.wait(lambda: read_pid(temporary / (role + '.creation')))
            witness = self.witness_factory(pid, creation)
            self.witnesses.append(witness)
            result.append((pid, creation, witness))
        return result

    def cleanup(self):
        okay = True
        # A failed proof must not keep process references open while the native
        # owner waits for its Job accounting to reach zero.
        for witness in self.witnesses:
            try:
                witness.close()
            except BaseException:
                okay = False
        for runner in reversed(self.runners):
            try:
                okay = runner.cleanup() and okay
            except BaseException:
                okay = False
        for owner in reversed(self.owners.owners):
            try:
                result = owner.result
                if result is None or not result.snapshot.cleanup_verified:
                    remaining = self.hard_deadline - self.clock()
                    _require(remaining > 0, 'control_cleanup_unverified')
                    result = owner.cancel('control-finally', timeout=remaining)
                _require(result.snapshot.cleanup_verified and result.snapshot.root_reaped
                         and result.snapshot.active_processes == 0 and result.snapshot.state == 'closed',
                         'control_cleanup_unverified')
            except BaseException:
                okay = False
        return okay


def _payload(mode):
    return ('import os,runpy,sys; from pathlib import Path; '
            'sys.path.insert(0,%r); '
            'raise SystemExit(runpy.run_path(%r)["tree"](Path(os.environ["TEMP"]),"root",int(sys.argv[-2][-1]),%r))' %
            (str(SCRIPT.parent), str(SCRIPT), mode))


def _prepare_pair(root, mode, runtime):
    from current_parallel_runner import CurrentParallelRunner
    root.mkdir()
    (root / 'mode').write_text(mode, encoding='ascii')
    clones = (root / 'lane0', root / 'lane1')
    for clone in clones:
        (clone / 'tools').mkdir(parents=True)
    capture, temporary = root / 'capture', root / 'temporary'
    capture.mkdir()
    temporary.mkdir()
    payload = _payload(mode)
    fixture_hash = hashlib.sha256(b'P18 synthetic control fixture; not application source').hexdigest()
    runner = CurrentParallelRunner(arm='cap2', modules=MODULES, clones=clones,
        capture_root=capture, temporary_root=temporary, payload=payload,
        source_sha=fixture_hash[:40], source_manifest_sha256=fixture_hash,
        candidate_sha256=fixture_hash,
        interpreter_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
        deadline=runtime.deadline, hard_deadline=runtime.hard_deadline,
        owner_factory=runtime.owners, clock=runtime.clock, environment=runtime.environment,
        disk_usage=runtime.disk_usage)
    runtime.runners.append(runner)
    handles = [runner.start(index, index, module, 'icd10_lookup')
               for index, module in enumerate(MODULES)]
    return runner, handles


def _live_pair(runtime, handles):
    identities = [runtime.witness(handle.temporary) for handle in handles]
    _require(len({pid for lane in identities for pid, creation, witness in lane}) == 6)
    for handle, lane in zip(handles, identities):
        snap = runtime.owners.for_handle(handle).poll()
        _require(snap.root_pid == lane[0][0] and not snap.root_reaped
                 and snap.active_processes == snap.total_processes == 3)
    _require(handles[0].report_dir != handles[1].report_dir
             and handles[0].temporary != handles[1].temporary)
    # ActiveProcesses can retain terminated process objects until independent
    # references close. These controls need live identity, not a death witness.
    for lane in identities:
        for pid, creation, witness in lane:
            witness.close()


def _drained(runtime, identities):
    runtime.wait(lambda: all(witness.signaled() for lane in identities for pid, creation, witness in lane))
    for lane in identities:
        for pid, creation, witness in lane:
            witness.close()


def _terminal(observation):
    row = observation.metadata
    _require(observation.cleanup_verified is True and row['cleanup_verified'] is True
             and row['root_reaped'] is True and row['active_processes'] == 0
             and row['total_processes'] == 3)


def _expected_capture(lane):
    return (('lane%d:root\nlane%d:child\nlane%d:grandchild\n' % (lane, lane, lane)).encode('ascii'),
            ('lane%d:stderr\nRan 1 test in 0.001s\n\nOK\n' % lane).encode('ascii'))


def _reverse(root, runtime):
    runner, handles = _prepare_pair(root, 'reverse', runtime)
    _live_pair(runtime, handles)
    (handles[1].temporary / 'release').write_bytes(b'release')
    second = runtime.wait(lambda: runner.poll(handles[1]))
    _require(runner.poll(handles[0]) is None)
    _require(runtime.owners.for_handle(handles[0]).poll().active_processes == 3)
    (handles[0].temporary / 'release').write_bytes(b'release')
    first = runtime.wait(lambda: runner.poll(handles[0]))
    for lane, observation in enumerate((first, second)):
        _terminal(observation)
        _require(not observation.unexpected and observation.metadata['returncode'] == 0
                 and observation.metadata['capture_read_verified'] is True)
        expected = _expected_capture(lane)
        for stream, data in zip(('stdout', 'stderr'), expected):
            _require(observation.metadata[stream + '_sha256'] == hashlib.sha256(data).hexdigest()
                     and observation.metadata[stream + '_bytes'] == len(data))


def _failure_hang(root, runtime):
    runner, handles = _prepare_pair(root, 'failure', runtime)
    _live_pair(runtime, handles)
    (handles[0].temporary / 'fail').write_bytes(b'fail')
    failed = runtime.owners.for_handle(handles[0])
    runtime.wait(lambda: failed.poll().root_reaped)
    snap = failed.poll()
    _require(snap.root_exit_code == 7 and snap.active_processes == 2
             and runtime.owners.for_handle(handles[1]).poll().active_processes == 3)
    _require(runner.poll(handles[0]) is None and runner.poll(handles[1]) is None)
    for handle in handles:
        observation = runner.cancel(handle, 'synthetic-failure')
        _terminal(observation)
        _require(observation.unexpected is True)


def _coordinator_death(root, runtime):
    root.mkdir()
    guard = runtime.owners.start([sys.executable, str(SCRIPT), '--coordinator', '--report-dir', str(root),
                                  '--deadline', str(runtime.deadline), '--hard-deadline', str(runtime.hard_deadline)],
                                 cwd=root, env=runtime.environment, report_dir=root / 'guard')
    runtime.wait(lambda: (root / 'coordinator.ready').is_file())
    identities = [runtime.witness(root / 'pair' / 'temporary' / ('command-%04d' % index))
                  for index in (1, 2)]
    _require(len({pid for lane in identities for pid, creation, witness in lane}) == 6)
    snap = guard.poll()
    _require(not snap.root_reaped and snap.active_processes == snap.total_processes == 7)
    runtime.terminate_coordinator(guard)
    # Crucial order: witness inner descendants dead BEFORE outer owner cleanup.
    # Otherwise killing the enclosing guard job could make this proof vacuous.
    _drained(runtime, identities)
    result = guard.finish(timeout=max(0.0, runtime.hard_deadline - runtime.clock()))
    _require(result.snapshot.cleanup_verified and result.snapshot.root_reaped
             and result.snapshot.active_processes == 0 and result.snapshot.state == 'closed')


def run_controls(root, *, runtime=None, platform=None):
    if (os.name if platform is None else platform) != 'nt':
        return _report(0, 'control_platform_unsupported')
    if sys.flags.optimize:
        return _report(0, 'control_optimization_unsupported')
    runtime = ControlRuntime() if runtime is None else runtime
    runtime.deadline = runtime.clock() + WORK_SECONDS
    runtime.hard_deadline = runtime.deadline + CLEANUP_SECONDS
    passed, diagnostic, created = 0, None, False
    try:
        _require(isinstance(root, Path) and root.is_absolute() and root.resolve() == root)
        root.mkdir(parents=False, exist_ok=False)
        created = True
        for control, name in zip((_reverse, _failure_hang, _coordinator_death), CONTROL_IDS):
            runtime.wait(lambda: True)
            control(root / name, runtime)
            passed += 1
    except BaseException as error:
        diagnostic = error.code if isinstance(error, ControlError) else 'control_unavailable'
    finally:
        cleanup = runtime.cleanup()
    if not cleanup:
        passed = min(passed, 2)
        diagnostic = diagnostic or 'control_cleanup_unverified'
    if runtime.clock() >= runtime.hard_deadline:
        passed = min(passed, 2)
        diagnostic = diagnostic or 'control_deadline'
    report = _report(passed, diagnostic, cleanup)
    if created and runtime.clock() < runtime.hard_deadline:
        try:
            raw = encode_receipt(report)
            (root / 'receipt.json').write_bytes(raw)
            _require(read_receipt((root / 'receipt.json').read_bytes()) == report, 'control_receipt_invalid')
            _require(runtime.clock() < runtime.hard_deadline, 'control_deadline')
        except BaseException as error:
            category = error.code if isinstance(error, ControlError) else 'control_receipt_invalid'
            report = _report(min(passed, 2), diagnostic or category, cleanup)
    return report


def tree(root, role, lane, mode):
    """Only synthetic nested processes; no imports of application code."""
    write_pid(root, role)
    sys.stdout.buffer.write(('lane%d:%s\n' % (lane, role)).encode('ascii'))
    sys.stdout.buffer.flush()
    process = None
    if role != 'grandchild':
        next_role = 'child' if role == 'root' else 'grandchild'
        process = subprocess.Popen([sys.executable, str(SCRIPT), '--tree', next_role,
                                    '--report-dir', str(root), '--lane', str(lane), '--mode', mode],
                                   cwd=root, env=dict(os.environ))
    while True:
        if role == 'root' and mode == 'failure' and lane == 0 and (root / 'fail').exists():
            return 7
        if (root / 'release').exists():
            if process is not None:
                process.wait(timeout=CLEANUP_SECONDS)
            if role == 'root':
                sys.stderr.buffer.write(_expected_capture(lane)[1])
                sys.stderr.buffer.flush()
            return 0
        time.sleep(.02)


def coordinator(root, deadline, hard_deadline):
    runtime = ControlRuntime()
    runtime.deadline, runtime.hard_deadline = deadline, hard_deadline
    try:
        runner, handles = _prepare_pair(root / 'pair', 'hang', runtime)
        for handle in handles:
            runtime.wait(lambda: read_pid(handle.temporary / 'grandchild.pid'))
            snap = runtime.owners.for_handle(handle).poll()
            _require(snap.active_processes == snap.total_processes == 3 and not snap.root_reaped)
        (root / 'coordinator.ready').write_bytes(b'ready')
        while runtime.clock() < deadline:
            for handle in handles:
                _require(runner.poll(handle) is None)
            runtime.sleep(.02)
        raise ControlError('control_deadline')
    finally:
        runtime.cleanup()


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ControlError('control_unavailable')


def main():
    try:
        parser = _Parser(description=__doc__)
        actions = parser.add_mutually_exclusive_group(required=True)
        actions.add_argument('--run', action='store_true')
        actions.add_argument('--coordinator', action='store_true')
        actions.add_argument('--tree', choices=ROLES)
        parser.add_argument('--report-dir', required=True, type=Path)
        parser.add_argument('--lane', type=int, choices=(0, 1))
        parser.add_argument('--mode', choices=('reverse', 'failure', 'hang'))
        parser.add_argument('--deadline', type=float)
        parser.add_argument('--hard-deadline', type=float)
        args = parser.parse_args()
        _require(os.name == 'nt', 'control_platform_unsupported')
        _require(not sys.flags.optimize, 'control_optimization_unsupported')
        if args.tree:
            return tree(args.report_dir, args.tree, args.lane, args.mode)
        if args.coordinator:
            return coordinator(args.report_dir, args.deadline, args.hard_deadline)
        report = run_controls(args.report_dir)
    except BaseException as error:
        report = _report(0, error.code if isinstance(error, ControlError) else 'control_unavailable')
    sys.stdout.buffer.write(encode_receipt(report) + b'\n')
    return 0 if report['status'] == 'passed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
