#!/usr/bin/env python3
"""Dedicated synthetic-only Windows compact validation, never an application screen."""
from __future__ import annotations

import math
import measure_lazy_suite_ids as q

BUDGET = {'job_seconds': 600, 'cleanup_seconds': 60,
          'setup_planning_seconds': 180, 'controls_planning_seconds': 300,
          'verification_planning_seconds': 60, 'max_capture_bytes': 16 * 1024 * 1024,
          'max_source_commands': 18, 'native_commands': 35,
          'max_compact_receipts': 69, 'max_compact_receipt_bytes': 16 * 1024,
          'minimum_free_bytes': 4 * 1024 ** 3}


def budget_deadlines(origin, wall_now, monotonic_now):
    q.require(all(type(value) in (int, float) and math.isfinite(value)
                  for value in (origin, wall_now, monotonic_now)), 'setup_clock_invalid')
    elapsed = wall_now - origin
    q.require(0 <= elapsed < 540, 'setup_budget_exhausted')
    hard = monotonic_now + 600 - elapsed
    return hard - 60, hard


def admit_controls(deadline, now):
    q.require(all(type(value) in (int, float) and math.isfinite(value)
                  for value in (deadline, now)) and deadline - now >= 360,
              'estimated_controls_no_longer_fit')

import re
import shutil
import measure_maintainer_pair as maintainer

BRANCH = 'refs/heads/diagnostic/2013-parallel-proof-20261020'
WORKFLOW = 'synthetic compact native validation'


def authorize_route(system, version, environment):
    q.require(system == 'nt' and version == '3.14.4', 'windows_python_pin_required')
    q.require(environment.get('GITHUB_ACTIONS') == 'true'
              and environment.get('GITHUB_EVENT_NAME') == 'push'
              and environment.get('GITHUB_REF') == BRANCH
              and environment.get('GITHUB_WORKFLOW') == WORKFLOW
              and environment.get('GITHUB_RUN_ATTEMPT') == '1'
              and re.fullmatch(r'[0-9a-f]{40}', environment.get('GITHUB_SHA', ''))
              and re.fullmatch(r'[0-9]{1,20}', environment.get('GITHUB_RUN_ID', '')),
              'unauthorized_event_or_rerun')


class VolumeAdmission:
    """Conservative fresh-free checks, never a deletion credit or physical quota."""
    def __init__(self, evidence, observer):
        self.roots = evidence, observer
        self.identities = []
        self.minimum_free = [None, None]
        for root in self.roots:
            maintainer.safe_directory(root)
            metadata = root.lstat()
            self.identities.append((metadata.st_dev, metadata.st_ino))

    def check(self):
        for index, (root, identity) in enumerate(zip(self.roots, self.identities)):
            maintainer.safe_directory(root)
            metadata = root.lstat()
            q.require((metadata.st_dev, metadata.st_ino) == identity, 'native_volume_identity_changed')
            minimum = BUDGET['minimum_free_bytes'] if index == 0 else 1024 ** 3
            free = shutil.disk_usage(root).free
            q.require(type(free) is int and free >= 0, 'native_storage_reserve_exhausted')
            previous = self.minimum_free[index]
            self.minimum_free[index] = free if previous is None else min(previous, free)
            q.require(free >= minimum, 'native_storage_reserve_exhausted')

import argparse
import contextlib
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import time

import diagnostic_observations as observation
import diagnose_checkpoint_discovery as checkpoint
import generated_output_contract as contract
import measure_reader_attribution as reader
import measure_current_parallel as comparison

PINS_HASH = 'd2ef2e61b37ff00dc795fe1c53a6093029a166542a4b2038382f4fee7364fdc0'
CORE_TREE = '658ccdae556c73508b38d8ab8c6ed39645d3af78'
REASONS = observation.REASONS | frozenset({
    'arguments_invalid', 'arguments_missing', 'budget_contract_changed',
    'cleared_implementation_changed', 'native_storage_reserve_exhausted',
    'native_volume_identity_changed', 'native_source_command_limit',
    'native_control_receipt_invalid', 'native_consumer_control_failed',
    'native_population_changed', 'native_receipt_limit', 'native_source_changed',
    'estimated_controls_no_longer_fit', 'setup_clock_invalid', 'setup_budget_exhausted',
    'native_owner_identity_changed', 'native_previous_owner_unverified', 'native_handle_cleanup_unverified', 'native_environment_unread', 'native_source_receipt_invalid',
    'publication_failed', 'unknown_failure'})


def reason(error):
    value = error.args[0] if type(error) is q.Refused and len(error.args) == 1 else None
    if type(value) is str and value in REASONS:
        return value
    native = sys.modules.get('compact_native_controls')
    if native is not None and type(error) is native.ControlError:
        return error.code if error.code in native.DIAGNOSTICS else 'unknown_failure'
    return 'unknown_failure'


def validate_core_pins(observer, inventory):
    raw = q.read_reviewed_bytes(observer / 'diagnostics/compact-native-source-pins.json', PINS_HASH)
    pins = observation.unique_json(raw)
    q.require(pins['base_tree'] == CORE_TREE and len(pins['files']) == 30
              and all(inventory.get(name) == digest for name, digest in pins['files'].items()),
              'cleared_implementation_changed')


class SourceSession(checkpoint.CheckpointSession):
    """Retain every real Git capture, coherently reading its original owner result."""
    def __init__(self, root, deadline, hard, admission):
        super().__init__(root, deadline, hard)
        self.admission = admission

    def _check_resources(self):
        self.admission.check()

    def run(self, argv, cwd):
        q.require(all(owner.result is not None
                      and owner.result.snapshot.cleanup_verified is True
                      and owner.result.snapshot.root_reaped is True
                      and owner.result.snapshot.active_processes == 0
                      and owner.result.snapshot.state == 'closed' for owner in self.owners),
                  'native_previous_owner_unverified')
        q.require(len(self.owners) < BUDGET['max_source_commands'], 'native_source_command_limit')
        self._check_resources()
        result = super().run(argv, cwd)
        owner = self.owners[-1]
        native = owner.result
        report = self.root / ('command-%04d' % len(self.owners))
        q.require(native is not None and native.reason == 'completed'
                  and native.snapshot.cleanup_verified is True
                  and native.snapshot.root_pid == int(owner._info.dwProcessId)
                  and Path(owner.report_dir) == report
                  and native.snapshot.root_exit_code == result['returncode']
                  and all(Path(getattr(native, stream + '_path')) == report / (stream + '.bin')
                          == Path(result[stream + '_path']) for stream in ('stdout', 'stderr')),
                  'native_owner_identity_changed')
        reads = [contract.read_owned_capture_snapshot(self.root,
            report.name + '/' + stream + '.bin', BUDGET['max_capture_bytes'], self.deadline)[0]
            for stream in ('stdout', 'stderr')]
        return {**result, 'stdout': reader.original_text(reads[0]),
                'stderr': reader.original_text(reads[1]), '_stdout_raw': reads[0]}

    def git_bytes(self, repo, *args):
        result = self.run(['git', '-C', str(repo), *args], repo)
        q.require(result['returncode'] == 0, 'git_verification_failed')
        return result['_stdout_raw']


def make_session(root, deadline, hard, admission):
    return SourceSession(root, deadline, hard, admission)


def make_runtime(deadline, hard, admission):
    from compact_native_controls import ControlRuntime
    runtime = ControlRuntime(resource_check=admission.check)
    runtime.work_deadline, runtime.hard_deadline = deadline, hard
    return runtime


def perform_controls(root, runtime, progress):
    import compact_native_controls as native
    import compact_native_consumers as consumers
    population = [(name, count, native.run_control)
                  for name, count in zip(native.CONTROL_IDS, native.CONTROL_COMMAND_COUNTS)]
    population += [(name, consumers.COMMAND_COUNTS[name], consumers.run_consumer_control)
                   for name in consumers.CONTROL_IDS]
    q.require(len(population) == 18 and len({name for name, _, _ in population}) == 18
              and sum(count for _, count, _ in population) == 35, 'native_population_changed')
    rows = []
    for name, count, run in population:
        q.require(time.monotonic() < runtime.work_deadline, 'global_budget_exhausted')
        runtime.resource_check()
        progress['failed_control'] = name
        before = len(runtime.owners) + runtime.nested_command_slots
        control_started = time.monotonic()
        row = run(name, root / name, runtime)
        elapsed = time.monotonic() - control_started
        q.require(math.isfinite(elapsed) and 0 <= elapsed <= 540, 'global_budget_exhausted')
        q.require(not any(api.handles or api.close_uncertain for api in runtime.apis),
                  'native_handle_cleanup_unverified')
        raw = json.dumps(row, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
        q.require(len(raw) <= 16384, 'native_receipt_limit')
        q.require(len(runtime.owners) + runtime.nested_command_slots - before == count,
                  'native_population_changed')
        q.require(time.monotonic() < runtime.work_deadline, 'global_budget_exhausted')
        rows.append({'id': name, 'owned_commands': count, 'wall_seconds': elapsed, 'evidence': row})
        progress['control_count'] = len(rows)
        q.emit('compact_native_control', id=name, status='passed', owned_commands=count, wall_seconds=elapsed,
               evidence_sha256=q.digest(raw))
        progress['failed_control'] = None
    q.require(len(runtime.owners) == 34 and runtime.nested_command_slots == 1,
              'native_population_changed')
    return rows


def execute(session, runtime, observer, progress):
    source = os.environ['GITHUB_SHA']
    progress['stage'] = 'source'
    q.first_clean(session, observer, source, 'observer')
    original = q.raw_source_inventory(session, observer, source)
    validate_core_pins(observer, original)
    q.verify_sources(session, observer, original, source_sha=source)
    plan = observation.unique_json((observer / 'diagnostics/compact-native-budget.json').read_bytes())
    q.require(plan == BUDGET and all(type(plan[key]) is type(value) for key, value in BUDGET.items()),
              'budget_contract_changed')
    progress['source_integrity_verified'] = True
    admit_controls(session.deadline, time.monotonic())
    progress['stage'] = 'controls'
    rows = perform_controls(session.root.parent, runtime, progress)
    progress['controls_verified'] = True
    progress['stage'] = 'final_source'
    q.require(q.raw_source_inventory(session, observer, source) == original, 'native_source_changed')
    q.verify_sources(session, observer, original, source_sha=source)
    q.require(len(session.owners) == 15, 'native_population_changed')
    progress['stage'] = 'receipt'
    raw = json.dumps({'schema': 'compact-native-validation-v1', 'source_sha': source,
        'cleared_tree': CORE_TREE, 'synthetic_only': True, 'controls': rows},
        sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    q.require(len(raw) <= 1024 * 1024, 'native_receipt_limit')
    q.require(time.monotonic() < session.deadline, 'global_budget_exhausted')
    receipt = comparison.retained_json(session, 'native-validation.json', raw)
    q.require(time.monotonic() < session.deadline, 'global_budget_exhausted')
    q.require(receipt['receipt_verified'] is True, 'native_source_receipt_invalid')
    progress.update(receipt_verified=True, receipt_sha256=receipt['receipt_sha256'])


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise q.Refused('arguments_invalid')


def _run(argv, public):
    start = time.monotonic()
    session = runtime = root = hard = admission = None
    failure = None
    clean = complete = False
    progress = {'stage': 'preflight', 'source_integrity_verified': False,
        'controls_verified': False, 'receipt_verified': False, 'receipt_sha256': None,
        'failed_control': None, 'control_count': 0}
    try:
        parser = Parser(description=__doc__, add_help=False)
        parser.add_argument('--observer', type=Path)
        parser.add_argument('--job-start-epoch', type=float)
        args = parser.parse_args(argv)
        authorize_route(os.name, platform.python_version(), dict(os.environ))
        q.require(args.observer is not None, 'arguments_missing')
        deadline, hard = budget_deadlines(args.job_start_epoch, time.time(), start)
        q.environment_preflight()
        observer = args.observer.resolve(strict=True)
        maintainer.safe_directory(observer)
        q.corpus_preflight((observer,))
        identity = maintainer.environment_identity()
        q.require(identity['python'] == '3.14.4'
                  and identity['image']['RUNNER_OS'] == 'Windows'
                  and identity['image']['RUNNER_ARCH'] == 'X64', 'native_environment_unread')
        root = Path(tempfile.mkdtemp(prefix='compact-native-')).resolve(strict=True)
        q.require(root != observer and observer not in root.parents and root not in observer.parents,
                  'native_volume_identity_changed')
        admission = VolumeAdmission(root, observer)
        admission.check()
        captures = root / 'source-captures'
        captures.mkdir()
        session = make_session(captures, deadline, hard, admission)
        runtime = make_runtime(deadline, hard, admission)
        q.emit('compact_native_environment', **identity, cleared_tree=CORE_TREE,
               synthetic_only=True, job_seconds=600, cleanup_seconds=60)
        execute(session, runtime, observer, progress)
        complete = True
    except BaseException as error:
        failure = {'stage': progress['stage'], 'reason': reason(error)}
        if root is not None:
            reader.retain_private_error(error, root)
    finally:
        clean = session is not None and runtime is not None
        for owner_group in (runtime, session):
            if owner_group is not None:
                try:
                    clean = owner_group.cleanup() is True and clean
                except BaseException:
                    clean = False
        if not clean and failure is None:
            failure = {'stage': 'cleanup', 'reason': 'process_cleanup_unverified'}
    elapsed = time.monotonic() - start
    within = hard is not None and time.monotonic() < hard
    passed = complete and clean and within and failure is None
    public.terminal = True
    try:
        q.emit('compact_native_summary', status='passed' if passed else 'inconclusive',
               **progress, failure=failure, process_cleanup_verified=clean,
               hard_budget_verified=within, observer_seconds=elapsed,
               synthetic_only=True, application_executed=False,
               source_commands=len(session.owners) if session is not None else 0,
               native_owner_count=len(runtime.owners) if runtime is not None else 0,
               nested_reserved_slots=runtime.nested_command_slots if runtime is not None else 0,
               minimum_observed_free_bytes=admission.minimum_free if admission is not None else None)
    except BaseException:
        return 2
    return 0 if passed and time.monotonic() < hard else 2


def main(argv=None):
    public = reader.PublicOutput(sys.stdout)
    try:
        with contextlib.redirect_stdout(public):
            return _run(argv, public)
    except BaseException:
        return 2  # Never leak a private traceback from a terminal/public boundary.


if __name__ == '__main__':
    raise SystemExit(main())
