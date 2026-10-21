#!/usr/bin/env python3
"""One bounded generated-output diagnostic, never the application full suite."""
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
import measure_maintainer_pair as m
import generated_output_contract as contract
import diagnostic_observations as observation
from diagnose_lazy_setup import budget_deadline
from diagnose_staging_layout import verify_retained_controls
from lazy_suite_support import RESULT_PREFIX

CASES = (
    'test_hook_payload.UnreadableHookPayloads.test_escaped_trigger_is_a_declared_raw_search_limit',
    'test_subagent_staging_hook.SubagentStagingLaunch.test_existing_nonempty_folder_accepts_relative_absolute_and_backslash_routes',
    'test_suite.SuiteRunControls.test_a_complete_run_atomically_replaces_the_unit_weights',
)
CONTRACT_CONTROL_COUNT = 41


def phase(session, progress, name):
    q.require(name in observation.PHASES, 'diagnostic_phase_invalid')
    progress['active_phase'] = name
    if session is not None:
        session.phase = name
    q.emit('diagnostic_phase', phase=name)


def discovery_child(repo):
    tools = repo / 'tools'
    sys.path.insert(0, str(tools))
    import suite as original_suite
    loader = unittest.TestLoader()
    discovered = tuple(original_suite._test_cases(loader.discover(start_dir=tools, top_level_dir=tools)))
    q.require(not loader.errors and discovered and all(type(test).__name__ != '_FailedTest' for test in discovered),
              'discovery_failed')
    ids = sorted(test.id() for test in discovered)
    q.require(len(set(ids)) == len(ids), 'duplicate_discovered_ids')
    # The original grouper consumes the actual objects, never ID string guesses.
    units = sorted(unit.name for unit in original_suite._units(discovered))
    q.require(len(set(units)) == len(units), 'duplicate_discovered_unit_names')
    row = {'test_count': len(ids), 'test_ids_sha256': q.digest(json.dumps(ids, separators=(',', ':')).encode()),
           'unit_names': units, 'executed_test_count': 0, 'loader_errors': 0}
    print(RESULT_PREFIX + json.dumps(row, sort_keys=True))
    return 0


def validate_discovery(result):
    rows = [line[len(RESULT_PREFIX):] for line in result['stdout'].splitlines() if line.startswith(RESULT_PREFIX)]
    q.require(type(result.get('returncode')) is int and result['returncode'] == 0 and len(rows) == 1,
              'unit_discovery_receipt_invalid')
    def unique(pairs):
        data = {}
        for key, value in pairs:
            q.require(key not in data, 'unit_discovery_receipt_invalid')
            data[key] = value
        return data
    try:
        row = json.loads(rows[0], object_pairs_hook=unique)
    except (ValueError, TypeError, RecursionError):
        raise q.Refused('unit_discovery_receipt_invalid') from None
    q.require(type(row) is dict and set(row) == {'test_count', 'test_ids_sha256', 'unit_names', 'executed_test_count', 'loader_errors'},
              'unit_discovery_receipt_invalid')
    units = row['unit_names']
    q.require(type(row['test_count']) is int and 0 < row['test_count'] <= 1000000
              and type(row['executed_test_count']) is int and row['executed_test_count'] == 0
              and type(row['loader_errors']) is int and row['loader_errors'] == 0
              and type(row['test_ids_sha256']) is str and re.fullmatch(r'[0-9a-f]{64}', row['test_ids_sha256'])
              and type(units) is list and 0 < len(units) <= min(row['test_count'], 10000)
              and all(type(name) is str and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]{0,511}', name) for name in units)
              and units == sorted(set(units)), 'unit_discovery_receipt_invalid')
    public = {key: row[key] for key in ('test_count', 'test_ids_sha256', 'executed_test_count', 'loader_errors')}
    public.update(unit_count=len(units), unit_names_sha256=q.digest(json.dumps(units, separators=(',', ':')).encode()),
                  units_derived_from_actual_objects=True)
    return tuple(units), public


def guarded(session, repo, expected, state):
    q.verify_sources(session, repo, expected, False)
    m.verify_refs(session, repo)
    return contract.scan(repo, expected, session.deadline, state)


def setup(session, observer, seed, job_start, progress):
    phase(session, progress, 'source')
    q.first_clean(session, observer, os.environ.get('GITHUB_SHA'), 'observer')
    session.git(observer, 'merge-base', '--is-ancestor', q.OBSERVER_BASE, 'HEAD')
    q.require(set(session.git(observer, 'diff', '--name-only', q.OBSERVER_BASE, 'HEAD').splitlines()) == q.OBSERVER_PATHS,
              'observer_branch_scope_changed')
    q.first_clean(session, seed, q.BASE, 'seed')
    snapshot = q.inventory(observer, deadline=session.deadline)
    expected = q.raw_source_inventory(session, seed, q.BASE)
    q.require(expected[q.SUITE_PATH] == q.ORIGINAL_HASH, 'baseline_module_hash_changed')
    progress.update(source_sha=q.BASE, environment=m.environment_identity())
    q.emit('generated_output_scope', **progress, full_suite=False, performance_probes=0,
           job_seconds=600, cleanup_reserve_seconds=60)
    phase(session, progress, 'native')
    owned = session.run([sys.executable, str(observer / 'diagnostics/windows_job_probe_controls.py'),
                         '--run', '--report-dir', str(session.root / 'owner-controls')], observer / 'diagnostics')
    q.require(owned['returncode'] == 0, 'owner_controls_failed')
    q.validate_owner_controls(json.loads(owned['stdout']))
    q.emit('owner_controls', count=9, passed=True)
    phase(session, progress, 'retained')
    verify_retained_controls(session, observer)
    phase(session, progress, 'contract')
    q.require(CONTRACT_CONTROL_COUNT > 0, 'contract_control_population_unset')
    controls = session.run([sys.executable, str(observer / 'diagnostics/diagnose_generated_outputs.py'),
                            '--contract-child'], observer / 'diagnostics')
    progress['contract_controls'] = q.verify_probe(controls, CONTRACT_CONTROL_COUNT, q.LOOKUPS[0])
    q.emit('generated_contract_controls', tests_run=CONTRACT_CONTROL_COUNT, **progress['contract_controls'])
    phase(session, progress, 'clone')
    clone_root = m.workspace_clone_root(session.root, observer, seed, expected)
    repo = clone_root / 'baseline'
    target = m.source_context(session, seed, repo, 'baseline', expected, b'')
    q.require(target == expected, 'generated_diagnostic_source_delta_forbidden')
    phase(session, progress, 'temp')
    temp = q.parse_child(session.run(q.child_command(observer, 'validate-temp', repo), repo / 'tools'))
    q.require(temp.get('outside_checkout_temp') is True and temp.get('temp_environment_unchanged') is True,
              'temp_validation_incomplete')
    m.verify_hook_location(session, repo)
    def state(marker, units=(), sessions='optional'):
        return contract.State(marker=marker, weights='absent', units=units, job_start_epoch=job_start,
                              observed_epoch=time.time(), max_job_seconds=600, sessions=sessions)
    phase(session, progress, 'initial_guard')
    progress['initial_output'] = guarded(session, repo, expected, state('absent'))
    phase(session, progress, 'discovery')
    discovered = session.run([sys.executable, str(observer / 'diagnostics/diagnose_generated_outputs.py'),
                              '--discovery-child', '--repo', str(repo)], repo / 'tools')
    phase(session, progress, 'discovery_validate')
    units, public = validate_discovery(discovered)
    progress['discovery'] = public
    q.emit('generated_unit_discovery', **public)
    phase(session, progress, 'discovery_guard')
    guarded(session, repo, expected, state('absent', units))
    progress['cases'] = []
    for index, selector in enumerate(CASES):
        phase(session, progress, 'case_' + str(index))
        result = session.run([sys.executable, '-m', 'unittest', selector], repo / 'tools')
        # Preserve command outcome before any parser/guard refusal.
        row = {'test_token': q.digest(selector.encode()), 'returncode': result['returncode']}
        progress['cases'].append(row)
        q.emit('generated_case_observed', **row)
        phase(session, progress, 'case_verify_' + str(index))
        row.update(q.verify_probe(result, 1, q.LOOKUPS[0]))
        phase(session, progress, 'case_guard_' + str(index))
        row['retained'] = guarded(session, repo, expected, state('required', units, 'required' if index >= 1 else 'optional'))
        q.emit('generated_case_verified', **row)
    phase(session, progress, 'final_source')
    sessions = repo / 'scratch/sessions'
    q.require(sessions.is_dir() and not any(sessions.iterdir()), 'staging_parent_not_empty_or_absent')
    progress['final_output'] = guarded(session, repo, expected, state('required', units, 'required'))
    q.require(q.inventory(seed, deadline=session.deadline) == expected, 'seed_changed')
    for name, checksum in snapshot.items():
        q.require(q.digest((observer / name).read_bytes()) == checksum, 'observer_source_changed')
    progress['raw_source_integrity_verified'] = True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observer', type=Path)
    parser.add_argument('--seed', type=Path)
    parser.add_argument('--job-start-epoch', type=float)
    parser.add_argument('--discovery-child', action='store_true')
    parser.add_argument('--contract-child', action='store_true')
    parser.add_argument('--repo', type=Path)
    args = parser.parse_args(argv)
    if args.contract_child:
        return observation.contract_child()
    if args.discovery_child:
        return discovery_child(args.repo.resolve())
    start = time.monotonic()
    session, root, complete, clean, failure = None, None, False, False, None
    progress = {'raw_source_integrity_verified': False, 'active_phase': 'preflight'}
    environment = dict(os.environ)
    try:
        phase(None, progress, 'preflight')
        q.require(os.name == 'nt' and platform.python_version() == '3.14.4', 'windows_python_pin_required')
        q.require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_EVENT_NAME') == 'push'
                  and os.environ.get('GITHUB_REF') == q.BRANCH and os.environ.get('GITHUB_RUN_ATTEMPT') == '1',
                  'unauthorized_event_or_rerun')
        deadline = budget_deadline(args.job_start_epoch, time.time(), start)
        q.environment_preflight()
        observer, seed = args.observer.resolve(), args.seed.resolve()
        q.require(observer != seed and observer not in seed.parents and seed not in observer.parents, 'checkout_overlap')
        q.corpus_preflight((observer, seed))
        temp = Path(tempfile.gettempdir()).resolve()
        q.require(all(not temp.is_relative_to(repo) for repo in (observer, seed)), 'temp_inside_checkout')
        root = Path(tempfile.mkdtemp(prefix='generated-output-owner-', dir=temp))
        session = observation.ObservedSession(root, deadline)
        setup(session, observer, seed, args.job_start_epoch, progress)
        phase(session, progress, 'environment')
        q.require(dict(os.environ) == environment, 'environment_changed')
        complete = True
    except BaseException as error:
        failure = observation.reason_category(error)
        try:
            q.safe_exception(error, root)  # Preserve bounded private evidence, never forward its frames.
        except BaseException:
            pass  # Private evidence failure must not replace the original failure.
        progress['failure_phase'] = progress['active_phase']
        q.emit('hold', reason=failure, phase=progress['failure_phase'],
               error_type=observation.exception_category(error), comparative_claim_allowed=False)
    finally:
        if session is not None:
            phase(session, progress, 'cleanup')
            try:
                clean = session.cleanup()
                q.emit('diagnostic_cleanup', verified=clean is True, exception_category=None)
                if clean is not True and failure is None:
                    failure = 'cleanup_unverified'
                    progress['failure_phase'] = 'cleanup'
            except BaseException as error:
                clean = False
                q.emit('diagnostic_cleanup', verified=False, exception_category=observation.exception_category(error))
                if failure is None:
                    failure = 'cleanup_failed'
                    progress['failure_phase'] = 'cleanup'
        passed = complete and clean
        q.emit('generated_output_summary', **progress, diagnostic_collection_complete=complete,
               process_cleanup_verified=clean, status='diagnostic-passed' if passed else 'inconclusive',
               full_suite=False, performance_probes=0, qualification=False, automatic_rerun=False,
               prior_hosted_contents_verified=False, private_raw_evidence_uploaded=False,
               failure=failure, observer_seconds=time.monotonic()-start)
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
