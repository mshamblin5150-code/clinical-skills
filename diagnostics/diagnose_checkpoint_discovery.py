#!/usr/bin/env python3
"""Fixed-checkpoint discovery and behavior only, never a suite execution."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import sys
import tempfile
import time
import unittest

import measure_lazy_suite_ids as q
import diagnostic_observations as observation
import measure_maintainer_pair as maintainer
import diagnose_generated_outputs as generated
import generated_output_contract as contract
from diagnose_lazy_setup import budget_deadline
from diagnose_staging_layout import verify_retained_controls
from lazy_suite_support import RESULT_PREFIX
from measure_parallel_readers import Hold

SOURCE_SHA = '08db6360b453c2bf969a686f62f0477184d06351'
BRANCH = 'refs/heads/diagnostic/2013-parallel-proof-20261020'
BUDGET = {'schema_version': 1, 'source_sha': SOURCE_SHA, 'job_seconds': 600,
          'cleanup_reserve_seconds': 60, 'python': '3.14.4', 'attempts': 1,
          'minimum_free_bytes': 1073741824, 'max_capture_bytes': 16777216}
OBSERVER_PATHS = q.OBSERVER_PATHS | {
    '.github/workflows/ci-checkpoint-discovery.yml',
    'diagnostics/diagnose_checkpoint_discovery.py', 'diagnostics/test_checkpoint_discovery.py',
    'diagnostics/checkpoint-discovery-budget.json', 'diagnostics/checkpoint-discovery-spec.md',
}
REASONS = observation.REASONS | frozenset((
    'checkpoint_identity_invalid', 'checkpoint_membership_changed', 'checkpoint_baseline_count_changed',
    'checkpoint_unit_membership_changed',
    'setup_clock_invalid', 'setup_budget_exhausted', 'checkpoint_budget_exhausted',
    'discovery_failed', 'duplicate_discovered_ids', 'duplicate_discovered_unit_names',
    'measured_module_missing', 'source_detached_head_required', 'source_refs_changed',
    'observer_child_failed', 'observer_child_report_invalid', 'cleanup_unverified', 'cleanup_failed',
    'seed_raw_bytes_differ_from_commit', 'raw_oracle_deadline_expired', 'raw_oracle_pin_invalid',
    'raw_oracle_pin_format_mismatch', 'raw_oracle_reparse_path_changed', 'raw_oracle_file_kind_changed',
    'raw_oracle_file_changed_during_read', 'unsupported_git_object_format', 'raw_tree_output_invalid',
    'raw_tree_population_limit', 'raw_tree_record_invalid', 'raw_tree_nonregular_or_unread',
    'raw_tree_oid_invalid', 'raw_tree_path_encoding_unread', 'raw_tree_path_invalid_or_duplicate',
    'pinned_ignore_missing',
    'optimized_python_invalidates_controls', 'inherited_lock_override', 'clinical_environment_override',
    'source_environment_override', 'known_fixed_corpus_present', 'known_or_default_corpus_present',
    'measurement_budget_expired', 'unexpected_symlink_or_reparse_path', 'hardlinked_file', 'unexpected_special_file',
))
NEW_UNIT = 'test_medatrax_fill.FillCommand'
OBSERVED_BASELINE_COUNT = 8487  # Exact-pin main-push run 39644301218, not arithmetic.
NEW_METHODS = (
    'test_clean_batch_keeps_nondefault_level_and_writes_ordered_list_and_script',
    'test_field_edit_and_rebuilt_unapproved_manifest_both_refuse',
    'test_field_change_between_approval_validation_and_exact_fill_read_refuses',
    'test_exact_source_checks_refuse_without_output',
    'test_clean_single_uses_its_approved_note_population',
    'test_profile_table_header_and_explanatory_prose_are_not_choices',
    'test_given_us_date_is_compared_without_rewriting_and_bare_age_does_not_infer_unit',
    'test_handwritten_content_damage_is_a_finding_not_unread_machine_evidence',
    'test_damaged_records_are_preserved_and_refuse',
    'test_missing_or_duplicate_field_and_unread_shift_refuse',
    'test_two_encounters_use_shared_order_spacing_and_midnight_window',
    'test_generated_script_executes_and_preflights_all_targets',
)


def budget_deadlines(job_start_epoch, wall_now, monotonic_now):
    work_deadline = budget_deadline(job_start_epoch, wall_now, monotonic_now)
    return work_deadline, work_deadline + 60


def authorize_route(system, version, environment):
    q.require(system == 'nt' and version == '3.14.4', 'windows_python_pin_required')
    q.require(environment.get('GITHUB_ACTIONS') == 'true' and environment.get('GITHUB_EVENT_NAME') == 'push'
              and environment.get('GITHUB_REF') == BRANCH and environment.get('GITHUB_RUN_ATTEMPT') == '1',
              'unauthorized_event_or_rerun')


def validate_budget(plan):
    q.require(type(plan) is dict and plan == BUDGET
              and all(type(plan[key]) is type(value) for key, value in BUDGET.items())
              and all(BUDGET[key] == q.BUDGET[key] for key in ('minimum_free_bytes', 'max_capture_bytes')),
              'budget_contract_changed')


def pre_suite_state(job_start_epoch, units=(), *, observed_epoch=None):
    return contract.State(marker='absent', weights='absent', units=units, sessions='optional',
                          job_start_epoch=job_start_epoch,
                          observed_epoch=time.time() if observed_epoch is None else observed_epoch,
                          max_job_seconds=600)


def reason_category(error):
    value = error.args[0] if isinstance(error, (q.Refused, Hold)) and len(error.args) == 1 else None
    return value if type(value) is str and value in REASONS else 'unavailable'


class CheckpointSession(observation.ObservedSession):
    """Keep the reviewed owner seam, bounding finalization inside this job."""
    def __init__(self, root, deadline, hard_deadline):
        super().__init__(root, deadline)
        self.hard_deadline = hard_deadline

    def cleanup(self):
        clean = True
        for owner in self.owners:
            try:
                result = owner.result
                if result is None:
                    remaining = self.hard_deadline - time.monotonic()
                    if remaining <= 0:
                        clean = False
                        continue
                    result = owner.cancel('coordinator_cleanup', timeout=min(5, remaining))
                clean = result.snapshot.cleanup_verified is True and clean
            except BaseException:
                clean = False
        return clean and time.monotonic() < self.hard_deadline


def discovery_child(repo):
    """Discover afresh; group actual TestCase objects with the pinned suite."""
    tools = repo / 'tools'
    sys.path.insert(0, str(tools))
    import suite as original_suite
    loader = unittest.TestLoader()
    tests = tuple(original_suite._test_cases(loader.discover(start_dir=tools, top_level_dir=tools)))
    q.require(tests and not loader.errors and all(type(test).__name__ != '_FailedTest' for test in tests),
              'discovery_failed')
    ids = sorted(test.id() for test in tests)
    q.require(len(set(ids)) == len(ids), 'duplicate_discovered_ids')
    units = tuple(original_suite._units(tests))
    grouped = tuple(test for unit in units for test in unit.tests)
    q.require(sorted(map(id, grouped)) == sorted(map(id, tests)), 'checkpoint_unit_membership_changed')
    names = sorted(unit.name for unit in units)
    q.require(len(set(names)) == len(names), 'duplicate_discovered_unit_names')
    membership = sorted(test.id() for unit in units if unit.name == NEW_UNIT for test in unit.tests)
    row = {'test_ids': ids, 'unit_names': names, 'new_module_test_ids': membership,
           'executed_test_count': 0, 'loader_errors': 0}
    print(RESULT_PREFIX + json.dumps(row, sort_keys=True))
    return 0


def identity_digest(names):
    return q.digest(json.dumps(names, ensure_ascii=True, separators=(',', ':')).encode())


def validate_identity(result, independent):
    """Validate private complete lists before emitting finite identity receipts."""
    q.require(type(result.get('returncode')) is int and result['returncode'] == 0
              and type(result.get('stdout')) is str
              and len(result['stdout'].encode()) <= q.BUDGET['max_capture_bytes'], 'checkpoint_identity_invalid')
    rows = [line[len(RESULT_PREFIX):] for line in result['stdout'].splitlines() if line.startswith(RESULT_PREFIX)]
    q.require(len(rows) == 1, 'checkpoint_identity_invalid')
    try:
        row = observation.unique_json(rows[0])
    except (ValueError, TypeError, RecursionError):
        raise q.Refused('checkpoint_identity_invalid') from None
    q.require(type(row) is dict and set(row) == {'test_ids', 'unit_names', 'new_module_test_ids',
                                               'executed_test_count', 'loader_errors'}, 'checkpoint_identity_invalid')
    for key in ('executed_test_count', 'loader_errors'):
        q.require(type(row[key]) is int and row[key] == 0, 'checkpoint_identity_invalid')
    for key in ('test_ids', 'unit_names', 'new_module_test_ids'):
        names = row[key]
        q.require(type(names) is list and 0 < len(names) <= (1000000 if key == 'test_ids' else 10000)
                  and all(type(name) is str and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]{0,511}', name) for name in names)
                  and names == sorted(set(names)), 'checkpoint_identity_invalid')
    ids, units = row['test_ids'], row['unit_names']
    expected = sorted(NEW_UNIT + '.' + name for name in NEW_METHODS)
    q.require(NEW_UNIT in units and row['new_module_test_ids'] == expected
              and [name for name in ids if name.startswith('test_medatrax_fill.')] == expected,
              'checkpoint_membership_changed')
    q.require(len(ids) == OBSERVED_BASELINE_COUNT and len(units) <= len(ids), 'checkpoint_baseline_count_changed')
    module_count = sum(name.startswith('test_suite_ids.') for name in ids)
    q.require(module_count > 0, 'measured_module_missing')
    q.require(type(independent) is dict and set(independent) == {'test_count', 'sorted_ids_sha256',
              'loader_error_count', 'module_test_count', 'executed_test_count', 'ids_encoding'}, 'checkpoint_identity_invalid')
    expected_counts = {'test_count': len(ids), 'module_test_count': module_count,
                       'loader_error_count': 0, 'executed_test_count': 0}
    q.require(all(type(independent[key]) is int and independent[key] == value for key, value in expected_counts.items())
              and independent['sorted_ids_sha256'] == identity_digest(ids)
              and independent['ids_encoding'] == 'sorted JSON array, ASCII escaped, compact',
              'unit_discovery_identity_changed')
    public = {'test_count': len(ids), 'sorted_ids_sha256': identity_digest(ids),
              'unit_count': len(units), 'unit_names_sha256': identity_digest(units),
              'module_test_count': module_count, 'new_module_test_count': len(expected),
              'new_module_ids_sha256': identity_digest(expected), 'loader_error_count': 0,
              'executed_test_count': 0, 'units_derived_from_actual_objects': True,
              'observed_baseline_count_corroborated': True}
    return {'ids': tuple(ids), 'units': tuple(units), 'public': public}


def compare_identities(baseline, candidate):
    q.require(baseline == candidate, 'discovery_population_changed')
    return True


def execute(session, observer, seed, job_start_epoch, progress, environment):
    """One serial pair of discovery prerequisites, with no suite command path."""
    def phase(name):
        generated.phase(session, progress, name)
    phase('source')
    q.first_clean(session, observer, os.environ.get('GITHUB_SHA'), 'observer')
    session.git(observer, 'merge-base', '--is-ancestor', q.OBSERVER_BASE, 'HEAD')
    q.require(set(session.git(observer, 'diff', '--name-only', q.OBSERVER_BASE, 'HEAD').splitlines()) == OBSERVER_PATHS,
              'observer_branch_scope_changed')
    q.first_clean(session, seed, SOURCE_SHA, 'seed')
    validate_budget(observation.unique_json((observer / 'diagnostics/checkpoint-discovery-budget.json').read_text()))
    snapshot = q.inventory(observer, deadline=session.deadline)
    expected = q.raw_source_inventory(session, seed, SOURCE_SHA)
    q.require(expected[q.SUITE_PATH] == q.ORIGINAL_HASH, 'baseline_module_hash_changed')
    candidate = q.read_reviewed_bytes(observer / q.SUITE_PATH, q.CANDIDATE_HASH)
    ref_snapshots = {repo: session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)')
                     for repo in (observer, seed)}
    clones, identities = {}, {}
    progress['arms'] = {}

    def guard():
        q.require(dict(os.environ) == environment, 'environment_changed')
        q.require(time.monotonic() < session.deadline, 'checkpoint_budget_exhausted')
        for repo, target, pin in ((observer, snapshot, os.environ.get('GITHUB_SHA')), (seed, expected, SOURCE_SHA)):
            q.verify_sources(session, repo, target, source_sha=pin)
            q.require(session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)') == ref_snapshots[repo],
                      'source_refs_changed')
            contract.scan(repo, target, session.deadline, pre_suite_state(job_start_epoch))
        for variant, (repo, target) in clones.items():
            q.verify_sources(session, repo, target, variant == 'candidate', source_sha=SOURCE_SHA)
            maintainer.verify_refs(session, repo, source_sha=SOURCE_SHA)
            detached = session.run(['git', '-C', str(repo), 'symbolic-ref', '-q', 'HEAD'], repo)
            q.require(detached['returncode'] == 1 and not detached['stdout'], 'source_detached_head_required')
            units = identities.get(variant, {}).get('units', ())
            contract.scan(repo, target, session.deadline, pre_suite_state(job_start_epoch, units))

    def checked(name, action):
        phase(name)
        guard()
        result = action()
        guard()
        return result

    def native():
        result = session.run([sys.executable, str(observer / 'diagnostics/windows_job_probe_controls.py'),
                              '--run', '--report-dir', str(session.root / 'owner-controls')], observer / 'diagnostics')
        q.require(result['returncode'] == 0, 'owner_controls_failed')
        q.validate_owner_controls(observation.unique_json(result['stdout']))
        q.emit('owner_controls', passed=True, count=len(q.DECLARED_CONTROL_IDS))
    checked('native', native)
    checked('retained', lambda: verify_retained_controls(session, observer))

    def output_controls():
        result = session.run([sys.executable, str(observer / 'diagnostics/diagnose_generated_outputs.py'),
                              '--contract-child'], observer / 'diagnostics')
        progress['contract_controls'] = q.verify_probe(result, generated.CONTRACT_CONTROL_COUNT, q.LOOKUPS[0])
        q.emit('generated_contract_controls', tests_run=generated.CONTRACT_CONTROL_COUNT, **progress['contract_controls'])
    checked('contract', output_controls)
    clone_root = checked('clone', lambda: maintainer.workspace_clone_root(session.root, observer, seed, expected))
    for variant in ('baseline', 'candidate'):
        progress['active_variant'] = variant
        repo = clone_root / variant

        def prepare():
            target = maintainer.source_context(session, seed, repo, variant, expected, candidate, source_sha=SOURCE_SHA)
            clones[variant] = (repo, target)
        checked('clone', prepare)

        def temp_check():
            row = q.parse_child(session.run(q.child_command(observer, 'validate-temp', repo), repo / 'tools'))
            q.require(row.get('outside_checkout_temp') is True and row.get('temp_environment_unchanged') is True,
                      'temp_validation_incomplete')
            maintainer.verify_hook_location(session, repo)
        checked('temp', temp_check)
        behavior_ids = checked('pair_behavior', lambda: maintainer.behavior_controls(session, observer, repo, variant))
        # Keep the historical junction plus four writer selectors, not a new test-body population.
        checked('pair_explicit', lambda: maintainer.explicit_controls(session, seed, repo))
        independent = checked('discovery', lambda: q.parse_child(
            session.run(q.child_command(observer, 'discover', repo), repo / 'tools')))

        def actual_objects():
            result = session.run([sys.executable, str(observer / 'diagnostics/diagnose_checkpoint_discovery.py'),
                                  '--child', 'units', '--repo', str(repo)], repo / 'tools')
            identity = validate_identity(result, independent)
            identities[variant] = identity
            progress['arms'][variant] = {'discovery': identity['public'], 'behavior_control_ids': behavior_ids,
                                        'expected_behavior_failures': 2 if variant == 'baseline' else 0,
                                        'explicit_selector_invocations': 5}
            q.emit('checkpoint_arm_identity', variant=variant, **progress['arms'][variant])
        checked('discovery_validate', actual_objects)
    checked('final_source', lambda: compare_identities(identities['baseline'], identities['candidate']))
    progress.update(source_integrity_verified=True, exact_id_and_unit_equality=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--child', choices=('units',))
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--observer', type=Path)
    parser.add_argument('--seed', type=Path)
    parser.add_argument('--job-start-epoch', type=float)
    args = parser.parse_args(argv)
    if args.child:
        q.require(args.repo is not None, 'child_repo_missing')
        return discovery_child(args.repo.resolve())
    start = time.monotonic()
    session, root, hard_deadline = None, None, None
    complete, clean, failure = False, False, None
    progress = {'active_phase': 'preflight', 'source_integrity_verified': False}
    environment = dict(os.environ)
    try:
        authorize_route(os.name, platform.python_version(), environment)
        q.require(args.observer is not None and args.seed is not None, 'arguments_missing')
        deadline, hard_deadline = budget_deadlines(args.job_start_epoch, time.time(), start)
        q.environment_preflight()
        observer, seed = args.observer.resolve(), args.seed.resolve()
        q.require(observer != seed and observer not in seed.parents and seed not in observer.parents, 'checkout_overlap')
        q.corpus_preflight((observer, seed))
        temp = Path(tempfile.gettempdir()).resolve()
        q.require(all(not temp.is_relative_to(repo) for repo in (observer, seed)), 'temp_inside_checkout')
        root = Path(tempfile.mkdtemp(prefix='checkpoint-discovery-owner-', dir=temp))
        session = CheckpointSession(root, deadline, hard_deadline)
        progress['environment'] = maintainer.environment_identity()
        q.emit('checkpoint_scope', source_sha=SOURCE_SHA, candidate_sha256=q.CANDIDATE_HASH,
               job_seconds=600, cleanup_reserve_seconds=60, full_suite_execution=False,
               timed_module_probes=0, new_medatrax_test_bodies_executed=0, automatic_rerun=False)
        execute(session, observer, seed, args.job_start_epoch, progress, environment)
        q.require(dict(os.environ) == environment, 'environment_changed')
        q.require(time.monotonic() < deadline, 'checkpoint_budget_exhausted')
        complete = True
    except BaseException as error:
        failure = reason_category(error)
        progress['failure_phase'] = observation.phase_name(progress['active_phase'])
        try:
            q.safe_exception(error, root)
        except BaseException:
            pass
        q.emit('hold', reason=failure, phase=progress['failure_phase'],
               error_type=observation.exception_category(error), comparative_claim_allowed=False)
    finally:
        cleanup_start = time.monotonic()
        if session is not None:
            session.phase = 'cleanup'
            try:
                clean = session.cleanup() is True
                if not clean and failure is None:
                    failure = 'cleanup_unverified'
                    progress['failure_phase'] = 'cleanup'
            except BaseException:
                if failure is None:
                    failure = 'cleanup_failed'
                    progress['failure_phase'] = 'cleanup'
        within_budget = hard_deadline is not None and time.monotonic() < hard_deadline
        passed = complete and clean and within_budget
        q.emit('checkpoint_discovery_summary', **progress,
               status='checkpoint-discovery-passed' if passed else 'inconclusive',
               source_sha=SOURCE_SHA, diagnostic_collection_complete=complete,
               process_cleanup_verified=clean, hard_budget_verified=within_budget,
               full_suite_execution=False, timed_module_probes=0, new_medatrax_test_bodies_executed=0,
               performance_qualified=False, adoption_authorized=False, automatic_rerun=False,
               private_raw_evidence_uploaded=False, runner_teardown_proved=False,
               failure=failure, observer_seconds=time.monotonic() - start,
               cleanup_seconds=time.monotonic() - cleanup_start)
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
