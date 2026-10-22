#!/usr/bin/env python3
"""One bounded baseline-first, four-call threshold-module timing screen."""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys
import tempfile
import time

import measure_lazy_suite_ids as q
import measure_maintainer_pair as maintainer
import measure_reader_attribution as reader
import diagnose_checkpoint_discovery as checkpoint
import generated_output_contract as contract
from diagnostic_observations import unique_json
from parallel_reader_capture import analyze_capture

SOURCE_SHA = '08db6360b453c2bf969a686f62f0477184d06351'
OBSERVER_BASE = 'b8de38f1c13e3800d3f2733c6b45103431cd4f86'
MODULE = 'test_threshold_sheet'
MODULE_PATH = 'tools/test_threshold_sheet.py'
BASELINE_HASH = '4444a8e477c7f0e6c7204c8691d216de8d3585c3942f24fab3f9a727d97c41f3'
CANDIDATE_HASH = '884d03f3a87239d2730c6729a44fa134338e48a282112eecd5a147d5992148f7'
BASELINE_BLOB = '3568f82d8e6e0a178783d434c09ff0e1997f3094'
CANDIDATE_BLOB = 'd44dcbd4a5a98a3a2cd185acc58aa0f24afc89e7'
MODULE_IDS_HASH = 'b2bbc719d12380d3068eb95f4645b8d7e775c8a22dc4a16386f93f0c5483bf40'
PLAN = tuple((arm, lookup) for arm in ('baseline', 'candidate') for lookup in q.LOOKUPS)
BUDGET = {'max_job_seconds': 600, 'cleanup_reserve_seconds': 60,
          'initial_setup_estimate_seconds': 140, 'arm_control_reserve_seconds': 40,
          'probe_reserve_seconds': 75, 'final_verification_reserve_seconds': 20,
          'max_capture_bytes': 16 * 1024 * 1024, 'max_receipt_bytes': 4 * 1024 * 1024,
          'minimum_free_bytes': q.BUDGET['minimum_free_bytes']}
OBSERVER_PATHS = {
    '.github/workflows/ci-reader-attribution.yml', '.github/workflows/ci-threshold-module.yml',
    'diagnostics/measure_lazy_suite_ids.py', 'diagnostics/measure_maintainer_pair.py',
    'diagnostics/measure_threshold_module.py', 'diagnostics/test_threshold_measurement.py',
    'diagnostics/threshold_module_controls.py', 'diagnostics/test_threshold_module_controls.py',
    'diagnostics/threshold-module-budget.json', 'diagnostics/threshold-module-spec.md', MODULE_PATH}
RELEVANT_SOURCE = {
    MODULE_PATH: BASELINE_HASH,
    'tools/threshold_sheet.py': '04bcf1bde7d1e128b09a1eb7749e7d4e2b4a76dcc83e606d674c1db1be6fd925',
    'tools/threshold_grammar.py': '03772941b28ab0b5116c9050f6eb552c3f8ff4a647eef6a8333e321ff5d59dbc',
    'tools/guidelines_recs.py': '8addca2a126c8bab761edbfa5ddb93316a238a1ea825a186f47653feb61efffd',
    'tools/guidelines_recs_test_support.py': '2a379470194dd325c08e73a6a23081f7fd046fed8322ceba8f70455220b74569',
    'tools/artifact_provenance.py': '4525353713444e602915b8d955e1bf3d7cf6271ed68f3e63c92e03bcc54c2e12',
    'tools/guidelines_manifest_test_support.py': 'b36092df6e7473110ffe1a0024d4178f9c9b59e8a3793217c2c0002181d05a62',
    'tools/code_set_database_reader_check.py': '386758808f5b6479ca3d2dad0bf35671e5a4db39651d5a0c2c83b064bd819d08'}


def admit(hard, now, *, probes, controls):
    """Estimates reserve future work; only the fixed global deadline bounds it."""
    q.require(all(type(value) in (int, float) and reader.metric(value) is not None
                  for value in (hard, now)) and hard > now
              and type(probes) is int and 0 <= probes <= 4
              and type(controls) is int and 0 <= controls <= 2, 'threshold_budget_invalid')
    reserve = 60 + 20 + probes * 75 + controls * 40
    q.require(hard - now >= reserve, 'threshold_admission_exhausted')
    return hard - now - reserve


def verify_candidate(original, candidate):
    def blob(raw): return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    q.require(q.digest(original) == BASELINE_HASH and blob(original) == BASELINE_BLOB,
              'threshold_baseline_source_changed')
    q.require(q.digest(candidate) == CANDIDATE_HASH and blob(candidate) == CANDIDATE_BLOB,
              'threshold_candidate_source_changed')
    return CANDIDATE_HASH


def owned_capture(session, result, previous):
    """Bind one completed native owner before re-reading its two private files."""
    q.require(type(result.get('returncode')) is int and result.get('cleanup_verified') is True,
              'process_cleanup_unverified')
    q.require(len(session.owners) == previous + 1, 'audit_capture_owner_changed')
    finished = session.owners[-1].result
    q.require(finished is not None and finished.snapshot.root_exit_code == result['returncode']
              and finished.snapshot.cleanup_verified is True, 'audit_capture_owner_changed')
    for key in ('wall_seconds', 'tree_cpu_seconds'):
        q.require(reader.metric(result.get(key)) is not None
                  and result[key] == getattr(finished.snapshot, key), 'audit_metrics_unread')
    captures = []
    for key, stream in (('stdout_path', 'stdout'), ('stderr_path', 'stderr')):
        relative = 'command-%04d/%s.bin' % (previous + 1, stream)
        q.require(Path(result[key]) == Path(getattr(finished, key)) == session.root / relative,
                  'audit_capture_owner_changed')
        captures.append(contract.read_owned_capture(session.root, relative,
                        BUDGET['max_capture_bytes'], session.deadline))
    return tuple(captures)


def measure_probe(session, repo, payload, arm, lookup, progress):
    rows = progress['samples']
    q.require(len(rows) < 4 and PLAN[len(rows)] == (arm, lookup), 'threshold_probe_order_changed')
    row = {'arm': arm, 'lookup': lookup, 'module_token': q.digest(MODULE_PATH.encode()),
           'source_sha256': BASELINE_HASH if arm == 'baseline' else CANDIDATE_HASH,
           'classification': 'unread', 'returncode': None, 'test_count': None,
           'failures': None, 'errors': None, 'skipped': None, 'expected_failures': None,
           'owned_wall_seconds': None, 'tree_cpu_seconds': None, 'call_wall_seconds': None,
           'stdout_bytes': None, 'stderr_bytes': None, 'stdout_sha256': None, 'stderr_sha256': None,
           'cleanup_verified': False, 'capture_read_verified': False, 'qualified': False}
    rows.append(row)
    previous, start = len(session.owners), time.monotonic()
    try:
        result = session.run([sys.executable, '-c', payload, str(repo / 'tools'), MODULE, lookup], repo / 'tools')
        row.update(returncode=result.get('returncode') if type(result.get('returncode')) is int else None,
                   cleanup_verified=result.get('cleanup_verified') is True,
                   owned_wall_seconds=reader.metric(result.get('wall_seconds')),
                   tree_cpu_seconds=reader.metric(result.get('tree_cpu_seconds')),
                   call_wall_seconds=time.monotonic() - start)
        raw = owned_capture(session, result, previous)
        parsed = analyze_capture(None, None, result['returncode'], lookup, module=MODULE, capture_bytes=raw)
        row.update(classification=parsed['classification'], capture_read_verified=True,
                   stdout_bytes=len(raw[0]), stderr_bytes=len(raw[1]),
                   stdout_sha256=q.digest(raw[0]), stderr_sha256=q.digest(raw[1]))
        keys = ('test_count', 'failures', 'errors', 'skipped', 'expected_failures')
        for key in keys:
            value = parsed[key]
            row[key] = value if type(value) is int and 0 <= value <= 1000000 else None
        row['qualified'] = (result['returncode'] == 0 and parsed['classification'] == 'nonreader'
                            and not parsed['unexpected'] and [row[key] for key in keys] == [345, 0, 0, 12, 0])
        q.require(row['qualified'], 'threshold_probe_incomplete')
        return row
    except BaseException as error:
        # First captured refusal survives a later publication failure.
        progress.setdefault('failure_context', {'stage': 'probe', 'reason': reason(error)})
        if len(session.owners) == previous + 1:
            finished = session.owners[-1].result
            if finished is not None:
                snapshot = finished.snapshot
                row.update(returncode=snapshot.root_exit_code if type(snapshot.root_exit_code) is int else None,
                           owned_wall_seconds=reader.metric(snapshot.wall_seconds),
                           tree_cpu_seconds=reader.metric(snapshot.tree_cpu_seconds),
                           cleanup_verified=snapshot.cleanup_verified is True)
        raise
    finally:
        row['call_wall_seconds'] = row['call_wall_seconds'] or time.monotonic() - start
        q.emit('threshold_probe', **row)


def reason(error):
    allowed = reader.FAILURE_REASONS | frozenset(('threshold_budget_invalid', 'threshold_admission_exhausted',
        'threshold_baseline_source_changed', 'threshold_candidate_source_changed', 'threshold_probe_order_changed',
        'threshold_probe_incomplete', 'threshold_baseline_not_qualified', 'threshold_receipt_invalid',
        'threshold_controls_incomplete', 'threshold_discovery_invalid', 'threshold_source_identity_changed',
        'budget_contract_changed', 'public_receipt_limit_exceeded', 'public_output_unavailable',
        'child_receipt_invalid', 'module_discovery_failed', 'module_source_changed',
        'module_location_changed', 'module_reload_changed', 'duplicate_module_ids'))
    value = error.args[0] if type(error) is q.Refused and len(error.args) == 1 else None
    return value if type(value) is str and value in allowed else 'unavailable'


def private_command(session, argv, cwd):
    previous = len(session.owners)
    result = session.run(argv, cwd)
    stdout, stderr = owned_capture(session, result, previous)
    return {**result, 'stdout': reader.original_text(stdout), 'stderr': reader.original_text(stderr)}, stdout


def prepare_arm(session, observer, seed, repo, arm, expected, candidate, guard):
    guard()
    target = maintainer.source_context(session, seed, repo, arm, expected, candidate,
                                      source_sha=SOURCE_SHA, candidate_path=MODULE_PATH)
    return target


def qualify_arm(session, observer, repo, arm, guard):
    import threshold_module_controls as controls
    expected_hash = BASELINE_HASH if arm == 'baseline' else CANDIDATE_HASH
    guard()
    result, _ = private_command(session, q.child_command(observer, 'validate-temp', repo), repo / 'tools')
    temp = q.parse_child(result)
    q.require(temp.get('outside_checkout_temp') is True and temp.get('temp_environment_unchanged') is True,
              'temp_validation_incomplete')
    maintainer.verify_hook_location(session, repo)
    guard()
    receipts = {}
    for action, validator in (('discover', controls.validate_discovery_receipt),
                              ('controls', controls.validate_controls_receipt)):
        guard()
        result, stdout = private_command(session, [sys.executable,
            str(observer / 'diagnostics/threshold_module_controls.py'), '--action', action,
            '--repo', str(repo), '--expected-source-sha256', expected_hash], repo / 'tools')
        try:
            receipts[action] = validator(stdout, result['returncode'], expected_hash)
        except controls.Refused:
            raise q.Refused('child_receipt_invalid') from None
        guard()
    q.require(receipts['discover']['test_ids'] == receipts['controls']['discovery']['test_ids'],
              'threshold_discovery_invalid')
    return receipts


def run_arms(session, observer, seed, root, expected, candidate, payload, progress, clones, guard):
    """The candidate cannot be cloned, imported or run before baseline qualification."""
    for arm_index, arm in enumerate(('baseline', 'candidate')):
        q.require(arm == 'baseline' or progress.get('baseline_qualified') is True, 'threshold_baseline_not_qualified')
        admit(session.hard_deadline, time.monotonic(), probes=4 - len(progress['samples']), controls=2 - arm_index)
        progress['phase'] = arm + '_preparation'
        repo = root / arm
        target = prepare_arm(session, observer, seed, repo, arm, expected, candidate, guard)
        clones.append((repo, target, arm == 'candidate'))
        guard()
        progress['phase'] = arm + '_controls'
        qualification = qualify_arm(session, observer, repo, arm, guard)
        for lookup in q.LOOKUPS:
            admit(session.hard_deadline, time.monotonic(), probes=4 - len(progress['samples']), controls=1 - arm_index)
            progress['phase'] = arm + '_probe'
            guard()
            measure_probe(session, repo, payload, arm, lookup, progress)
            guard()
        q.require(len(progress['samples']) == 2 * (arm_index + 1)
                  and all(row['qualified'] and row['capture_read_verified'] and row['cleanup_verified']
                          for row in progress['samples']), 'threshold_probe_incomplete')
        q.require(all(owner.result is not None and owner.result.snapshot.cleanup_verified is True
                      for owner in session.owners), 'process_cleanup_unverified')
        # All source, output, accounting and per-child cleanup checks have passed.
        progress['arms'][arm] = qualification
        progress[arm + '_qualified'] = True
        q.emit('threshold_arm_qualified', arm=arm, module_source_sha256=BASELINE_HASH if arm == 'baseline' else CANDIDATE_HASH,
               test_count=345, skipped=12, discovery_ids_sha256=MODULE_IDS_HASH, original_controls=29,
               source_integrity_verified=True, output_contract_verified=True, process_cleanup_verified=True,
               per_executed_id_attestation=False)
    admit(session.hard_deadline, time.monotonic(), probes=0, controls=0)


def retain_receipt(session, progress, environment, origin):
    q.require(progress.get('baseline_qualified') is True and progress.get('candidate_qualified') is True
              and [(row['arm'], row['lookup']) for row in progress['samples']] == list(PLAN)
              and all(row['qualified'] for row in progress['samples']), 'threshold_receipt_invalid')
    envelope = {'schema_version': 1, 'source_sha': SOURCE_SHA,
                'observer_sha': environment['GITHUB_SHA'], 'run_id': environment['GITHUB_RUN_ID'],
                'job_start_epoch': origin, 'environment_sha256': progress['environment_sha256'],
                'baseline_sha256': BASELINE_HASH, 'candidate_sha256': CANDIDATE_HASH,
                'arms': progress['arms'], 'samples': progress['samples'],
                'discovery_equivalence_and_original_counts_only': True, 'per_executed_id_attestation': False}
    raw = json.dumps(envelope, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    q.require(len(raw) <= BUDGET['max_receipt_bytes'], 'threshold_receipt_invalid')
    path = session.root / 'threshold-receipt.json'
    with path.open('xb') as stream: stream.write(raw)
    readback = contract.safe_read(session.root, path.name, BUDGET['max_receipt_bytes'], session.deadline)
    q.require(readback == raw and unique_json(readback) == envelope, 'threshold_receipt_invalid')
    return {'receipt_sha256': q.digest(readback), 'receipt_bytes': len(readback), 'receipt_verified': True}


def execute(session, observer, seed, origin, progress, environment):
    q.first_clean(session, observer, environment['GITHUB_SHA'], 'observer')
    session.git(observer, 'merge-base', '--is-ancestor', OBSERVER_BASE, 'HEAD')
    q.require(set(session.git(observer, 'diff', '--name-only', OBSERVER_BASE, 'HEAD').splitlines()) == OBSERVER_PATHS,
              'observer_branch_scope_changed')
    q.first_clean(session, seed, SOURCE_SHA, 'seed')
    budget = unique_json(contract.safe_read(observer, 'diagnostics/threshold-module-budget.json', 16384, session.deadline))
    q.require(type(budget) is dict and budget == BUDGET
              and all(type(budget[key]) is type(value) for key, value in BUDGET.items()), 'budget_contract_changed')
    snapshot = q.inventory(observer, deadline=session.deadline)
    expected = q.raw_source_inventory(session, seed, SOURCE_SHA)
    q.require(all(expected.get(path) == value for path, value in RELEVANT_SOURCE.items()), 'threshold_baseline_source_changed')
    original = reader.read_pinned_source(seed, MODULE_PATH, BASELINE_HASH, session.deadline)
    candidate = reader.read_pinned_source(observer, MODULE_PATH, CANDIDATE_HASH, session.deadline)
    verify_candidate(original, candidate)
    refs = {repo: session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)') for repo in (observer, seed)}
    clones = []
    def guard():
        q.require(dict(os.environ) == environment and time.monotonic() < session.deadline, 'environment_or_budget_changed')
        for repo, target, pin in ((observer, snapshot, environment['GITHUB_SHA']), (seed, expected, SOURCE_SHA)):
            q.verify_sources(session, repo, target, source_sha=pin)
            q.require(session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)') == refs[repo], 'source_refs_changed')
            contract.scan(repo, target, session.deadline, checkpoint.pre_suite_state(origin))
        for repo, target, changed in clones:
            maintainer.generated_guard(session, repo, target, changed, checkpoint.pre_suite_state(origin), candidate_path=MODULE_PATH)
    def checked(phase, action):
        progress['phase'] = session.phase = phase
        guard(); result = action(); guard()
        return result
    def native():
        result, raw = private_command(session, [sys.executable, str(observer / 'diagnostics/windows_job_probe_controls.py'),
                                     '--run', '--report-dir', str(session.root / 'owner-controls')], observer / 'diagnostics')
        q.require(result['returncode'] == 0, 'owner_controls_failed')
        q.validate_owner_controls(unique_json(raw))
        progress['owner_control_count'] = len(q.DECLARED_CONTROL_IDS)
    checked('native', native)
    checked('retained', lambda: reader.verify_retained_controls(session, observer))
    progress['retained_control_count'] = 5
    def output_controls():
        result, _ = private_command(session, [sys.executable, str(observer / 'diagnostics/diagnose_generated_outputs.py'),
                                            '--contract-child'], observer / 'diagnostics')
        count = reader.generated.CONTRACT_CONTROL_COUNT
        verdict = q.classify_probe(result, count)
        parsed = analyze_capture(None, None, result['returncode'], q.LOOKUPS[0],
                                 capture_bytes=(result['stdout'].encode(), result['stderr'].encode()))
        q.require(verdict['valid'] and not parsed['unexpected'] and parsed['test_count'] == count
                  and all(parsed[key] == 0 for key in ('failures', 'errors', 'skipped', 'expected_failures')),
                  'probe_failed_or_unread')
        progress['generated_control_count'] = reader.generated.CONTRACT_CONTROL_COUNT
    checked('contract', output_controls)
    root = checked('clone', lambda: maintainer.workspace_clone_root(session.root, observer, seed, expected))
    payload = q.original_payload(seed)
    progress['payload_sha256'] = q.digest(payload.encode())
    run_arms(session, observer, seed, root, expected, candidate, payload, progress, clones, guard)
    progress['phase'] = 'final_verification'
    guard()
    progress.update(retain_receipt(session, progress, environment, origin))
    guard()
    progress.update(source_integrity_verified=True, output_contract_verified=True)


def make_session(root, deadline, hard):
    return checkpoint.CheckpointSession(root, deadline, hard)


class FiniteParser(argparse.ArgumentParser):
    def error(self, message):
        raise q.Refused('arguments_missing')


def _run(argv, public):
    environment, start = dict(os.environ), time.monotonic()
    session = root = hard = None
    complete = clean = False
    progress = {'phase': 'preflight', 'samples': [], 'arms': {}, 'source_integrity_verified': False,
                'output_contract_verified': False, 'receipt_verified': False}
    try:
        parser = FiniteParser(add_help=False)
        parser.add_argument('--observer', type=Path, required=True)
        parser.add_argument('--seed', type=Path, required=True)
        parser.add_argument('--job-start-epoch', type=float, required=True)
        args = parser.parse_args(argv)
        checkpoint.authorize_route(os.name, platform.python_version(), environment)
        q.require(re.fullmatch(r'[0-9a-f]{40}', environment.get('GITHUB_SHA', '')) is not None
                  and re.fullmatch(r'[0-9]{1,20}', environment.get('GITHUB_RUN_ID', '')) is not None,
                  'observer_identity_missing')
        deadline, hard = checkpoint.budget_deadlines(args.job_start_epoch, time.time(), start)
        q.environment_preflight()
        observer, seed = args.observer.resolve(), args.seed.resolve()
        q.require(observer != seed and observer not in seed.parents and seed not in observer.parents, 'checkout_overlap')
        q.corpus_preflight((observer, seed))
        temp = Path(tempfile.gettempdir()).resolve()
        q.require(all(not temp.is_relative_to(repo) for repo in (observer, seed)), 'temp_inside_checkout')
        identity = maintainer.environment_identity(); maintainer.validate_environment(identity)
        progress['environment_sha256'] = q.digest(json.dumps(identity, sort_keys=True).encode())
        root = Path(tempfile.mkdtemp(prefix='threshold-module-owner-', dir=temp)).resolve()
        session = make_session(root, deadline, hard)
        q.emit('threshold_environment', **identity)
        q.require(time.monotonic() < deadline, 'global_budget_exhausted')
        execute(session, observer, seed, args.job_start_epoch, progress, environment)
        q.require(dict(os.environ) == environment and time.monotonic() < deadline, 'environment_or_budget_changed')
        complete = all(progress.get(key) is True for key in ('baseline_qualified', 'candidate_qualified',
                       'source_integrity_verified', 'output_contract_verified', 'receipt_verified'))
    except BaseException as error:
        progress.setdefault('failure_context', {'stage': progress['phase'], 'reason': reason(error)})
        reader.retain_private_error(error, root)
    finally:
        cleanup_start = time.monotonic()
        if session is not None:
            try: clean = session.cleanup() is True
            except BaseException as error: reader.retain_private_error(error, root)
        public.terminal = True
        within = hard is not None and time.monotonic() < hard
        passed = complete and clean and within
        summary = {key: value for key, value in progress.items() if key not in ('samples', 'arms')}
        try:
            q.emit('threshold_summary', **summary, status='complete' if passed else 'inconclusive',
                   source_sha=SOURCE_SHA, baseline_sha256=BASELINE_HASH, candidate_sha256=CANDIDATE_HASH,
                   observer_sha=environment.get('GITHUB_SHA') if re.fullmatch(r'[0-9a-f]{40}', environment.get('GITHUB_SHA', '')) else None,
                   run_id=environment.get('GITHUB_RUN_ID') if re.fullmatch(r'[0-9]{1,20}', environment.get('GITHUB_RUN_ID', '')) else None,
                   samples_attempted=len(progress['samples']), samples_expected=4,
                   process_cleanup_verified=clean, hard_budget_verified=within,
                   observer_seconds=time.monotonic() - start, cleanup_seconds=time.monotonic() - cleanup_start,
                   timing_screen_complete=passed, performance_qualified=False, per_executed_id_attestation=False,
                   full_suite_execution=False, adoption_authorized=False, automatic_rerun=False,
                   private_raw_evidence_uploaded=False, runner_teardown_proved=False)
        except BaseException as error:
            passed = False
            reader.retain_private_error(error, root)
    return 0 if passed and hard is not None and time.monotonic() < hard else 2


def main(argv=None):
    public = reader.PublicOutput(sys.stdout)
    try:
        with contextlib.redirect_stdout(public): return _run(argv, public)
    except BaseException:
        return 2  # A failed terminal sink is never retried or printed as a traceback.


if __name__ == '__main__':
    raise SystemExit(main())
