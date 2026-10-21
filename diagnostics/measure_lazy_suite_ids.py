#!/usr/bin/env python3
"""One bounded, serial lazy-message qualification; no full suite or adoption.

Estimated admission is not a completion guarantee. The only execution deadline
is the remaining whole-job budget minus cleanup reserve, never a test timeout.
All subprocesses are owned Windows Job trees. Raw evidence stays on the runner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import stat
import sys
import tempfile
import time

from lazy_suite_support import (Refused, require, original_payload, child,
                                classify_probe, parse_child, digest)
from measure_parallel_readers import inventory, environment_preflight, corpus_preflight
from parallel_reader_capture import analyze_capture
from parallel_reader_diagnostics import safe_exception
from raw_source_inventory import raw_source_inventory, RawIdentityMismatch
from windows_job_probe import WindowsJobProbe
from windows_job_probe_controls import DECLARED_CONTROL_IDS

BASE = '104ee03cd4d37519b12b3edbc4da5fbf31b631cf'
OBSERVER_BASE = '38c431b15b7fafb0f5f89a67ecb501de318c47a1'
BRANCH = 'refs/heads/diagnostic/2013-parallel-proof-20261020'
SUITE_PATH = 'tools/test_suite_ids.py'
ORIGINAL_HASH = 'b3f804165e04ae0534c36882de699b7ae84e7ebb1df899539497ef1f6a97900c'
CANDIDATE_HASH = 'f2f97e56313d7f8957bec0bd20fd91c9efd8c48c44871c5c69056eb830d43275'
LOOKUPS = ('icd10_lookup', 'procedure_codes_lookup')
EXPECTED_RED = {
    '__main__.LazyBindingControls.test_successful_ids_reload_and_assert_without_diagnostics',
    '__main__.LazyBindingControls.test_multiple_failures_continue_through_later_success_and_failure',
}
CONTROL_IDS = EXPECTED_RED | {
    '__main__.LazyBindingControls.test_empty_population_is_successful_without_diagnostics',
    '__main__.LazyBindingControls.test_each_mismatch_keeps_exact_failure_diagnostic',
    '__main__.LazyBindingControls.test_discovery_errors_stop_before_any_reload_or_diagnostic',
    '__main__.LazyBindingControls.test_helper_error_on_failed_check_remains_visible',
}
SYNTHETIC_SELECTORS = (
    'test_tool_record_writers_approval.ApprovalFamilyWriters.test_receipt_retries_and_coding_retries_retain_concurrent_remarks',
    'test_tool_record_writers_aar.WriterTransactions.test_aar_concurrent_rounds_allocate_distinct_records',
    'test_tool_record_writers_aar.WriterTransactions.test_concurrent_portal_members_survive',
    'test_tool_record_writers_aar.WriterTransactions.test_portal_native_lock_and_interrupted_replace_preserve_bytes',
)
JUNCTION = 'test_aar_scan.ScanBasedSittingDiscovery.test_transcript_junctions_are_counted_without_being_entered'
OBSERVER_PATHS = {
    'diagnostics/diagnostic_observations.py', 'diagnostics/test_diagnostic_observations.py',
    'diagnostics/diagnose_staging_layout.py', 'diagnostics/test_staging_diagnostic.py',
    'diagnostics/staging_retained_controls.py', 'diagnostics/test_staging_retained_controls.py',
    'diagnostics/generated_output_contract.py', 'diagnostics/test_generated_output_contract.py',
    'diagnostics/diagnose_generated_outputs.py', 'diagnostics/test_generated_output_diagnostic.py',
    'diagnostics/measure_maintainer_pair.py', 'diagnostics/full_suite_receipts.py',
    'diagnostics/test_maintainer_pair.py', 'diagnostics/test_full_suite_receipts.py',
    'diagnostics/test_source_context_real_git.py',
    'diagnostics/test_maintainer_workspace.py', 'diagnostics/test_temp_hook_boundary.py',
    SUITE_PATH, '.github/workflows/ci-parallel-proof.yml',
    'diagnostics/parallel-proof-budget.json', 'diagnostics/measure_parallel_readers.py',
    'diagnostics/parallel_reader_scheduler.py', 'diagnostics/parallel_reader_capture.py',
    'diagnostics/parallel_reader_diagnostics.py', 'diagnostics/test_parallel_reader_controls.py',
    'diagnostics/test_parallel_observer_controls.py', 'diagnostics/windows_job_probe.py',
    'diagnostics/windows_job_probe_controls.py', 'diagnostics/measure_lazy_suite_ids.py',
    'diagnostics/lazy_suite_support.py', 'diagnostics/suite_id_lazy_controls.py',
    'diagnostics/lazy-qualification-budget.json', 'diagnostics/lazy-qualification-spec.md',
    'diagnostics/test_lazy_qualification_contracts.py',
    'diagnostics/raw_source_inventory.py', 'diagnostics/test_raw_source_inventory.py',
    'diagnostics/diagnose_lazy_setup.py', 'diagnostics/test_lazy_setup.py',
}
BUDGET = {
    'schema_version': 1, 'admission_mode': 'estimate-not-completion-guarantee',
    'source_sha': BASE, 'approved_job_seconds': 5400,
    'setup_controls_estimate_seconds': 900, 'measurement_estimate_seconds': 3900,
    'cleanup_reserve_seconds': 300, 'contingency_seconds': 300,
    'baseline_probe_estimate_seconds': 350, 'candidate_probe_estimate_seconds': 10,
    'receipt_estimate_seconds': 300, 'minimum_free_bytes': 1073741824,
    'max_capture_bytes': 16777216,
}


def build_plan():
    rows = []
    for sample in range(1, 6):
        for variant in ('baseline', 'candidate'):
            for lookup in LOOKUPS:
                rows.append({'ordinal': len(rows) + 1, 'sample': sample,
                             'variant': variant, 'lookup': lookup})
    return rows


def admit_budget(plan, remaining_seconds):
    require(plan == BUDGET and all(type(plan[key]) is type(value) for key, value in BUDGET.items()),
            'budget_contract_changed')
    require(isinstance(remaining_seconds, (int, float)) and not isinstance(remaining_seconds, bool)
            and math.isfinite(remaining_seconds) and remaining_seconds >= 4200,
            'estimated_complete_plan_no_longer_fits')
    return plan


def read_reviewed_bytes(path, expected_hash):
    data = path.read_bytes()
    require(digest(data) == expected_hash, 'reviewed_raw_bytes_changed')
    return data


def validate_controls(row, variant, returncode, prior_ids=None):
    require(variant in ('baseline', 'candidate'), 'unknown_control_variant')
    require(row.get('schema_version') == 1 and row.get('tests_run') == 6
            and row.get('error_count') == 0, 'controls_work_incomplete')
    outcomes = row.get('control_outcomes')
    require(isinstance(outcomes, list) and len(outcomes) == 6, 'controls_rows_incomplete')
    ids = [item.get('test_id') for item in outcomes]
    require(len(set(ids)) == 6 and set(ids) == CONTROL_IDS, 'controls_population_changed')
    require(prior_ids is None or set(ids) == set(prior_ids), 'controls_population_changed')
    failures = EXPECTED_RED if variant == 'baseline' else set()
    for item in outcomes:
        require(item.get('outcome') == ('failure' if item['test_id'] in failures else 'pass')
                and item.get('expected_baseline_failure') is (item['test_id'] in EXPECTED_RED),
                'controls_unexpected_outcome')
    require(row.get('failure_count') == len(failures)
            and row.get('successful') is (variant == 'candidate')
            and returncode == (1 if variant == 'baseline' else 0), 'controls_exit_mismatch')
    return set(ids)


def validate_owner_controls(row):
    controls = row.get('controls')
    require(isinstance(controls, list) and all(isinstance(item, dict) for item in controls)
            and [item.get('control') for item in controls] == list(DECLARED_CONTROL_IDS),
            'owner_control_rows_incomplete')
    require(row.get('schema') == 'windows-job-probe-controls-v1' and row.get('status') == 'passed'
            and row.get('optimization_level') == 0 and row.get('files_retained') is True
            and row.get('process_cleanup_verified') is True and row.get('platform') == 'win32'
            and str(row.get('python', '')).split()[:1] == ['3.14.4']
            and row.get('failed_count') == 0 and row.get('skipped_count') == 0
            and row.get('declared_control_ids') == row.get('passed_control_ids') == list(DECLARED_CONTROL_IDS)
            and row.get('planned_count') == row.get('passed_count') == len(DECLARED_CONTROL_IDS),
            'owner_controls_incomplete')


def emit(event, **fields):
    # No caller supplies raw streams, paths, exception messages, or fixture data.
    print(json.dumps({'event': event, **fields}, sort_keys=True, allow_nan=False), flush=True)


class Session:
    """Owned command seam, retaining every owner and capture through finalization."""
    def __init__(self, root, deadline):
        self.root, self.deadline = root, deadline
        self.owners = []
        self.git_exe = shutil.which('git')
        require(self.git_exe is not None and Path(self.git_exe).is_absolute(), 'git_unavailable')

    def run(self, argv, cwd):
        require(time.monotonic() < self.deadline, 'global_budget_exhausted')
        require(shutil.disk_usage(self.root).free >= BUDGET['minimum_free_bytes'], 'disk_reserve_exhausted')
        if argv[0] == 'git':
            argv = [self.git_exe, *argv[1:]]
        report = self.root / ('command-%04d' % (len(self.owners) + 1))
        try:
            owner = WindowsJobProbe.start(argv, cwd=str(cwd), env=dict(os.environ), report_dir=str(report))
        except BaseException as error:
            partial = getattr(error, 'owner', None)
            if partial is not None:
                self.owners.append(partial)
                partial.cancel('command_start_exception', timeout=5)
            raise
        self.owners.append(owner)
        while time.monotonic() < self.deadline:
            snapshot = owner.poll()
            if snapshot.root_reaped and snapshot.active_processes == 0:
                result = owner.finish(timeout=5)
                require(result.snapshot.cleanup_verified and result.reason == 'completed', 'process_cleanup_unverified')
                paths = (Path(result.stdout_path), Path(result.stderr_path))
                require(all(path.stat().st_size <= BUDGET['max_capture_bytes'] for path in paths), 'capture_limit_exceeded')
                return {'returncode': result.snapshot.root_exit_code,
                        'stdout': paths[0].read_text(encoding='utf-8', errors='replace'),
                        'stderr': paths[1].read_text(encoding='utf-8', errors='replace'),
                        'wall_seconds': result.snapshot.wall_seconds,
                        'tree_cpu_seconds': result.snapshot.tree_cpu_seconds,
                        'stdout_path': result.stdout_path, 'stderr_path': result.stderr_path,
                        'cleanup_verified': result.snapshot.cleanup_verified}
            if (shutil.disk_usage(self.root).free < BUDGET['minimum_free_bytes']
                    or any(path.stat().st_size > BUDGET['max_capture_bytes'] for path in report.iterdir() if path.is_file())):
                owner.cancel('capture_or_disk_reserve_exhausted', timeout=5)
                raise Refused('capture_or_disk_reserve_exhausted')
            time.sleep(0.02)
        owner.cancel('whole_job_budget_exhausted', timeout=5)
        raise Refused('global_budget_exhausted')

    def git(self, repo, *args):
        result = self.run(['git', '-C', str(repo), *args], repo)
        require(result['returncode'] == 0, 'git_verification_failed')
        return result['stdout']

    def git_bytes(self, repo, *args):
        result = self.run(['git', '-C', str(repo), *args], repo)
        require(result['returncode'] == 0, 'git_verification_failed')
        return Path(result['stdout_path']).read_bytes()

    def cleanup(self):
        clean = True
        for owner in self.owners:
            try:
                result = owner.result or owner.cancel('coordinator_cleanup', timeout=5)
                clean = result.snapshot.cleanup_verified and clean
            except BaseException:
                clean = False
        return clean


def status_receipt(raw):
    """Summarize original porcelain-v1 rows without decoding path fields."""
    counts, entries, total = {}, [], 0
    records = raw.split(b'\n')
    malformed = bool(raw and records[-1])
    if not records[-1]:
        records.pop()
    for row in records:
        code = row[:2]
        valid = len(row) > 3 and row[2:3] == b' ' and all(c in b' MADRCUT?!' for c in code)
        category = code.decode('ascii') if valid else 'malformed'
        counts[category] = counts.get(category, 0) + 1
        total += 1
        if len(entries) < 8:
            entries.append({'category': category,
                            'path_field_token': digest(row[3:]) if valid else None})
        malformed = malformed or not valid
    return {'category_counts': counts, 'entry_count': total, 'entries': entries,
            'omitted_entries': total - len(entries), 'parse_complete': not malformed,
            'path_token_semantics': 'original-possibly-quoted-or-rename-composite-field',
            'raw_paths_disclosed': False, 'raw_contents_disclosed': False}


def conversion_config_receipt(session, repo):
    # Effective values only. Never print config origins, arbitrary keys or values.
    allowed = {'core.autocrlf': {'true', 'false', 'input'},
               'core.eol': {'lf', 'crlf', 'native'},
               'core.safecrlf': {'true', 'false', 'warn'}}
    result = {}
    for key, values in allowed.items():
        try:
            row = session.run(['git', '-C', str(repo), 'config', '--get', key], repo)
            value = row['stdout'].strip().lower()
            result[key] = (value if row['returncode'] == 0 and value in values else
                           'unset' if row['returncode'] == 1 and not value else
                           'unrecognized' if row['returncode'] == 0 else 'unavailable')
        except Exception:
            result[key] = 'unavailable'
    return result


def first_clean(session, repo, head, role):
    require(role in ('observer', 'seed', 'baseline', 'candidate', 'original-layout', 'short-layout'), 'unknown_clone_role')
    require((repo / '.git').is_dir() and not (repo / '.git').is_symlink(), 'independent_clone_required')
    require(not (repo / '.git/objects/info/alternates').exists(), 'shared_objects_refused')
    common = session.git(repo, 'rev-parse', '--git-common-dir').strip()
    require((repo / common).resolve() == (repo / '.git').resolve(), 'shared_git_directory')
    require(session.git(repo, 'rev-parse', 'HEAD').strip() == head, 'wrong_source_head')
    # This must precede normalization, reset, checkout-index, or a candidate copy.
    status = session.git_bytes(repo, 'status', '--porcelain=v1', '--untracked-files=all')
    if status:
        # This exact captured result determines refusal. No second status or repair.
        emit('first_status_discrepancy', role=role, **status_receipt(status))
        emit('first_status_config', role=role, effective_values=conversion_config_receipt(session, repo))
    require(not status, 'first_status_not_clean')


def create_measurement_root(owner_root, observer, seed):
    """Short disposable sibling; owner placement and process environment unchanged."""
    clone_root = Path(tempfile.mkdtemp(prefix='lc-', dir=owner_root.parent))
    require(clone_root.parent == owner_root.parent and clone_root.resolve() == clone_root
            and clone_root.is_dir() and not any(clone_root.iterdir())
            and all(clone_root != other and clone_root not in other.parents and other not in clone_root.parents
                    for other in (owner_root, observer, seed)), 'clone_root_boundary_invalid')
    for component in (clone_root, *clone_root.parents):
        metadata = component.lstat()
        require(stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
                and not (getattr(metadata, 'st_file_attributes', 0) & 0x400), 'clone_root_ancestor_unsafe')
    units = lambda path: len(str(path).encode('utf-16-le', errors='surrogatepass')) // 2
    require(units(clone_root) < units(owner_root), 'clone_root_not_shorter')
    return clone_root


def make_clone(session, seed, root, variant, expected, candidate):
    repo = root / variant
    result = session.run(['git', '-c', 'core.autocrlf=false', 'clone', '--no-local', '--no-hardlinks',
                          '--no-checkout', str(seed), str(repo)], root)
    require(result['returncode'] == 0, 'clone_failed')
    session.git(repo, '-c', 'core.autocrlf=false', 'checkout', '--detach', BASE)
    first_clean(session, repo, BASE, variant)
    require(inventory(repo, deadline=session.deadline) == expected, 'initial_clone_inventory_changed')
    inventory(repo / '.git', exclude_git=False, deadline=session.deadline)
    require(not any(os.path.lexists(repo / name) for name in ('scratch', 'output')), 'private_roots_present')
    if variant == 'candidate':
        (repo / SUITE_PATH).write_bytes(candidate)
    target = dict(expected)
    if variant == 'candidate':
        target[SUITE_PATH] = digest(candidate)
    require(inventory(repo, deadline=session.deadline) == target, 'prepared_clone_inventory_changed')
    return repo, target


def verify_sources(session, repo, expected, candidate=False):
    require(session.git(repo, 'rev-parse', 'HEAD').strip() == BASE, 'measured_head_changed')
    require(not session.git(repo, 'diff', '--cached', '--name-only'), 'measured_index_changed')
    require(session.git(repo, 'diff', '--name-only', 'HEAD').splitlines() == ([SUITE_PATH] if candidate else []),
            'measured_scope_changed')
    require(not session.git(repo, 'ls-files', '--others', '--exclude-standard'), 'untracked_source_changed')
    for name, expected_hash in expected.items():
        path = repo / name
        for component in (path, *path.parents):
            if component == repo:
                break
            metadata = component.lstat()
            require(not component.is_symlink() and not (getattr(metadata, 'st_file_attributes', 0) & 0x400),
                    'tracked_reparse_path_changed')
        require(path.is_file() and path.stat().st_nlink == 1 and digest(path.read_bytes()) == expected_hash,
                'tracked_raw_bytes_changed')
    corpus_preflight((repo,), admission=False)


def child_command(observer, action, repo):
    return [sys.executable, str(observer / 'diagnostics/measure_lazy_suite_ids.py'), '--child', action, '--repo', str(repo)]


def verify_probe(result, expected_count, lookup):
    verdict = classify_probe(result, expected_count)
    parsed = analyze_capture(result['stdout_path'], result['stderr_path'], result['returncode'], lookup)
    require(verdict['valid'] and not parsed['unexpected']
            and parsed['test_count'] == expected_count and parsed['failures'] == parsed['errors'] == 0
            and parsed['skipped'] == parsed['expected_failures'] == 0, 'probe_failed_or_unread')
    return {**verdict, 'output_sha256': parsed['output_sha256'], 'output_bytes': parsed['output_bytes'],
            'failures': parsed['failures'], 'errors': parsed['errors'], 'skipped': parsed['skipped']}


def summarize(samples, plan):
    groups = []
    for variant in ('baseline', 'candidate'):
        for lookup in LOOKUPS:
            values = [row['wall_seconds'] for row in samples if row['variant'] == variant and row['lookup'] == lookup]
            groups.append({'variant': variant, 'lookup': lookup, 'count': len(values),
                           'median_seconds': statistics.median(values) if values else None,
                           'minimum_seconds': min(values) if values else None, 'maximum_seconds': max(values) if values else None})
    complete = len(samples) == len(plan) == 20 and all(
        all(row.get(key) == expected[key] for key in expected)
        and row.get('valid') is True
        and isinstance(row.get('wall_seconds'), (int, float))
        and not isinstance(row['wall_seconds'], bool)
        and math.isfinite(row['wall_seconds']) and row['wall_seconds'] > 0
        for row, expected in zip(samples, plan))
    return complete, groups


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observer', type=Path)
    parser.add_argument('--seed', type=Path)
    parser.add_argument('--budget-sha256')
    parser.add_argument('--job-start-epoch', type=float)
    parser.add_argument('--child', choices=('validate-temp', 'discover'))
    parser.add_argument('--repo', type=Path)
    args = parser.parse_args(argv)
    if args.child:
        require(args.repo is not None, 'child_repo_missing')
        child(args.child, args.repo.resolve())
        return 0
    samples, plan, session, root = [], build_plan(), None, None
    passed, integrity_complete, clean, failure = False, False, False, None
    start = time.monotonic()
    original_env = dict(os.environ)
    try:
        require(os.name == 'nt' and platform.python_version() == '3.14.4', 'windows_python_pin_required')
        require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_EVENT_NAME') == 'push'
                and os.environ.get('GITHUB_REF') == BRANCH and os.environ.get('GITHUB_RUN_ATTEMPT') == '1',
                'unauthorized_event_or_rerun')
        require(all(value is not None for value in (args.observer, args.seed, args.job_start_epoch)), 'arguments_missing')
        elapsed = time.time() - args.job_start_epoch
        require(math.isfinite(elapsed) and 0 <= elapsed < 900, 'setup_estimate_exhausted')
        job_deadline = start + 5400 - elapsed
        deadline = job_deadline - 300
        environment_preflight()
        observer, seed = args.observer.resolve(), args.seed.resolve()
        require(observer != seed and observer not in seed.parents and seed not in observer.parents, 'checkout_overlap')
        corpus_preflight((observer, seed))
        temp = Path(tempfile.gettempdir()).resolve()
        require(all(not temp.is_relative_to(repo) for repo in (observer, seed)), 'temp_inside_checkout')
        root = Path(tempfile.mkdtemp(prefix='lazy-qualification-', dir=temp))
        session = Session(root, deadline)
        first_clean(session, observer, os.environ.get('GITHUB_SHA'), 'observer')
        session.git(observer, 'merge-base', '--is-ancestor', OBSERVER_BASE, 'HEAD')
        changed = set(session.git(observer, 'diff', '--name-only', OBSERVER_BASE, 'HEAD').splitlines())
        require(changed == OBSERVER_PATHS, 'observer_branch_scope_changed')
        first_clean(session, seed, BASE, 'seed')
        budget_bytes = read_reviewed_bytes(observer / 'diagnostics/lazy-qualification-budget.json', args.budget_sha256)
        budget = json.loads(budget_bytes)
        require(budget == BUDGET, 'budget_contract_changed')
        observer_snapshot = inventory(observer, deadline=deadline)
        expected = raw_source_inventory(session, seed, BASE)
        require(expected[SUITE_PATH] == ORIGINAL_HASH, 'baseline_module_hash_changed')
        candidate = read_reviewed_bytes(observer / SUITE_PATH, CANDIDATE_HASH)
        payload = original_payload(seed)
        emit('scope', source_sha=BASE, observer_base=OBSERVER_BASE, candidate_sha256=CANDIDATE_HASH,
             planned_probes=plan, admission='estimate-not-completion-guarantee', total_job_seconds=5400,
             cleanup_reserve_seconds=300, full_suite_execution=False, private_corpus_coverage='NOT RUN',
             cache_policy='fresh child processes; bytecode and OS caches retained; no cold or symmetric-cache claim')
        owned = session.run([sys.executable, str(observer / 'diagnostics/windows_job_probe_controls.py'),
                             '--run', '--report-dir', str(root / 'owner-controls')], observer / 'diagnostics')
        require(owned['returncode'] == 0, 'owner_controls_failed')
        validate_owner_controls(json.loads(owned['stdout']))
        emit('owner_controls', passed=True, count=len(DECLARED_CONTROL_IDS))
        clone_root = create_measurement_root(root, observer, seed)
        clones = {variant: make_clone(session, seed, clone_root, variant, expected, candidate)
                  for variant in ('baseline', 'candidate')}
        baseline = clones['baseline'][0]
        row = parse_child(session.run(child_command(observer, 'validate-temp', baseline), baseline / 'tools'))
        require(row.get('outside_checkout_temp') is True and row.get('temp_environment_unchanged') is True,
                'temp_validation_incomplete')
        junction = session.run([sys.executable, '-c', payload, str(baseline / 'tools'), JUNCTION, LOOKUPS[0]], baseline / 'tools')
        verify_probe(junction, 1, LOOKUPS[0])
        ids, discoveries = None, {}
        for variant, (repo, _) in clones.items():
            result = session.run([sys.executable, str(observer / 'diagnostics/suite_id_lazy_controls.py'), '--repo', str(repo)], repo / 'tools')
            ids = validate_controls(json.loads(result['stdout']), variant, result['returncode'], ids)
            emit('behavior_controls', variant=variant, tests_run=6, expected_failures=2 if variant == 'baseline' else 0, errors=0)
            discoveries[variant] = parse_child(session.run(child_command(observer, 'discover', repo), repo / 'tools'))
            emit('discovery', variant=variant, **discoveries[variant])
        require(discoveries['baseline'] == discoveries['candidate'], 'discovery_population_changed')
        module_count = discoveries['baseline']['module_test_count']
        # Existing controls only. No telemetry patch, timing perturbation, loop, or lock-policy change.
        for selector in SYNTHETIC_SELECTORS:
            result = session.run([sys.executable, '-m', 'unittest', selector], baseline / 'tools')
            verify_probe(result, 1, LOOKUPS[0])
            emit('synthetic_control', selector=selector, tests_run=1, successful=True,
                 contention_reproduced=False, overlap_verified=False, root_cause_established=False)
        admit_budget(budget, job_deadline - time.monotonic())
        emit('estimated_admission', admitted=True, remaining_seconds=job_deadline-time.monotonic(),
             measurement_estimate_seconds=3900, completion_guaranteed=False)
        for index, item in enumerate(plan):
            require(dict(os.environ) == original_env, 'environment_changed')
            for variant, (repo, target) in clones.items():
                verify_sources(session, repo, target, variant == 'candidate')
            estimate = sum(350 if row['variant'] == 'baseline' else 10 for row in plan[index:]) + 300
            require(deadline - time.monotonic() >= estimate, 'remaining_estimated_samples_do_not_fit')
            repo = clones[item['variant']][0]
            emit('timed_probe_started', **item)
            result = session.run([sys.executable, '-c', payload, str(repo / 'tools'), 'test_suite_ids', item['lookup']], repo / 'tools')
            verdict = verify_probe(result, module_count, item['lookup'])
            require(verdict['valid'] and result['tree_cpu_seconds'] is not None, 'timed_probe_incomplete_or_failed')
            row = {**item, **verdict, 'wall_seconds': result['wall_seconds'], 'tree_cpu_seconds': result['tree_cpu_seconds']}
            samples.append(row)
            emit('timed_probe_finished', **row)
        for variant, (repo, target) in clones.items():
            verify_sources(session, repo, target, variant == 'candidate')
            retained = inventory(repo, deadline=deadline)
            emit('retained_inventory', variant=variant, file_count=len(retained),
                 inventory_sha256=digest(json.dumps(retained, sort_keys=True).encode()), ephemeral_writes_observed=False)
        require(inventory(seed, deadline=deadline) == expected, 'seed_changed')
        # Imports may create bytecode in the observer. All tracked source bytes remain immutable.
        for name, expected_hash in observer_snapshot.items():
            require(digest((observer / name).read_bytes()) == expected_hash, 'observer_source_changed')
        require(not session.git(observer, 'status', '--porcelain=v1', '--untracked-files=all'), 'observer_dirty_at_finish')
        require(dict(os.environ) == original_env, 'environment_changed')
        integrity_complete = True
        passed, _ = summarize(samples, plan)
    except BaseException as error:
        # Literal observer codes only; external exception text and raw reports stay private.
        failure = str(error) if isinstance(error, Refused) else 'unexpected_exception_details_withheld'
        details = safe_exception(error, root)
        if isinstance(error, RawIdentityMismatch):
            emit('source_discrepancy', **error.diagnostics)
        emit('hold', reason=failure, error_type=type(error).__name__,
             private_detail_retained=details['private_detail_retained'], comparative_claim_allowed=False)
    finally:
        if session is not None:
            clean = session.cleanup()
        complete, groups = summarize(samples, plan)
        success = passed and complete and clean and integrity_complete
        emit('summary', status='qualified-target-module-only' if success else 'inconclusive',
             planned_probes=len(plan), completed_valid_probes=len(samples),
             unread_ordinals=[row['ordinal'] for row in plan[len(samples):]], groups=groups,
             source_integrity_verified=integrity_complete, process_cleanup_verified=clean,
             raw_evidence_retained=root is not None, raw_evidence_uploaded=False,
             teardown_independently_proved=False, full_suite_execution=False, end_to_end_measured=False,
             adoption_authorized=False, root_cause_established=False, automatic_rerun=False,
             observer_seconds=time.monotonic()-start, failure=failure)
    return 0 if success else 2


if __name__ == '__main__':
    raise SystemExit(main())
