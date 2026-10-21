#!/usr/bin/env python3
"""Dedicated synthetic Windows metadata validation. Never application tests."""
import unittest


def control_groups():
    from test_generated_output_contract import GeneratedOutputControls
    from test_windows_metadata import WindowsMetadataControls
    from windows_snapshot_controls import NativeWindowsSnapshotControls
    classes = {'contract': GeneratedOutputControls, 'deterministic': WindowsMetadataControls,
               'native': NativeWindowsSnapshotControls}
    return {group: tuple(cls.__module__ + '.' + cls.__name__ + '.' + name
                         for name in unittest.defaultTestLoader.getTestCaseNames(cls))
            for group, cls in classes.items()}


def control_child(report_root, deadline):
    import os
    from pathlib import Path
    import platform
    import time
    import diagnostic_observations as observation
    import windows_snapshot_controls as native
    import measure_lazy_suite_ids as q
    q.require(os.name == 'nt' and platform.python_version() == '3.14.4', 'windows_python_pin_required')
    q.require(report_root.is_absolute() and report_root.is_dir() and report_root.resolve() == report_root
              and type(deadline) is float and time.monotonic() < deadline, 'snapshot_fixture_scope_invalid')
    groups = control_groups()
    q.require({name: len(ids) for name, ids in groups.items()} ==
              {'contract': 41, 'deterministic': 26, 'native': 6}, 'snapshot_population_changed')
    ids = sum(groups.values(), ())
    q.require(len(set(ids)) == 73, 'snapshot_population_changed')
    modules = ('test_generated_output_contract', 'test_windows_metadata', 'windows_snapshot_controls')
    def flatten(suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                yield from flatten(item)
            else:
                yield item.id()
    loader = unittest.TestLoader()
    loaded = tuple(flatten(loader.loadTestsFromNames(modules)))
    q.require(not loader.errors and sorted(loaded) == sorted(ids), 'snapshot_population_changed')
    native.REPORT_ROOT, native.DEADLINE = report_root, deadline
    return observation.control_child(modules, ids, 73)


def collect(session, observer, seed, progress):
    import os
    import sys
    from pathlib import Path
    import measure_lazy_suite_ids as q
    import measure_maintainer_pair as m
    from diagnose_generated_outputs import phase
    phase(session, progress, 'source')
    q.first_clean(session, observer, os.environ.get('GITHUB_SHA'), 'observer')
    session.git(observer, 'merge-base', '--is-ancestor', q.OBSERVER_BASE, 'HEAD')
    q.require(set(session.git(observer, 'diff', '--name-only', q.OBSERVER_BASE, 'HEAD').splitlines()) == q.OBSERVER_PATHS,
              'observer_branch_scope_changed')
    q.first_clean(session, seed, q.BASE, 'seed')
    snapshot = q.inventory(observer, deadline=session.deadline)
    expected = q.raw_source_inventory(session, seed, q.BASE)
    q.require(expected[q.SUITE_PATH] == q.ORIGINAL_HASH, 'baseline_module_hash_changed')
    q.emit('snapshot_scope', source_sha=q.BASE, environment=m.environment_identity(),
           job_seconds=600, cleanup_reserve_seconds=60, full_suite=False, performance_probes=0,
           application_methods=0, expected_unittest_count=73,
           groups={'contract': 41, 'deterministic_fake_native': 26, 'native_fixture': 6},
           native_boundary_interventions=2, natural_concurrent_race_claim=False)
    phase(session, progress, 'native')
    owned = session.run([sys.executable, str(observer/'diagnostics/windows_job_probe_controls.py'),
                         '--run', '--report-dir', str(session.root/'owner-controls')], observer/'diagnostics')
    q.require(owned['returncode'] == 0, 'owner_controls_failed')
    import json
    q.validate_owner_controls(json.loads(owned['stdout']))
    q.emit('owner_controls', count=9, passed=True)
    phase(session, progress, 'snapshot')
    fixture_root = session.root/'snapshot-fixtures'
    fixture_root.mkdir()
    controls = session.run([sys.executable, str(observer/'diagnostics/diagnose_windows_snapshot.py'),
                            '--controls-child', '--report-root', str(fixture_root),
                            '--deadline', str(session.deadline)], observer/'diagnostics')
    # Observe fixture cleanup before any count/parser refusal can hide it.
    fixture_clean = False
    try:
        import generated_output_contract as contract
        contract._safe_directory(fixture_root)
        fixture_clean = not any(fixture_root.iterdir())
        q.emit('snapshot_fixture_cleanup', verified=fixture_clean, state='observed')
    except BaseException as error:
        import diagnostic_observations as observation
        q.emit('snapshot_fixture_cleanup', verified=False, state='unread',
               exception_category=observation.exception_category(error))
    progress['snapshot_controls'] = q.verify_probe(controls, 73, q.LOOKUPS[0])
    q.require(fixture_clean, 'snapshot_fixture_cleanup_failed')
    fixture_root.rmdir()
    q.emit('snapshot_controls', tests_run=73, native_fixture_count=6, deterministic_count=26,
           contract_count=41, fixture_cleanup_verified=True, **progress['snapshot_controls'])
    phase(session, progress, 'final_source')
    q.require(q.inventory(seed, deadline=session.deadline) == expected, 'seed_changed')
    for name, checksum in snapshot.items():
        q.require(q.digest((observer/name).read_bytes()) == checksum, 'observer_source_changed')
    progress['raw_source_integrity_verified'] = True


def main(argv=None):
    import argparse
    import os
    from pathlib import Path
    import platform
    import tempfile
    import time
    import measure_lazy_suite_ids as q
    import diagnostic_observations as observation
    from diagnose_generated_outputs import phase
    from diagnose_lazy_setup import budget_deadline
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observer', type=Path)
    parser.add_argument('--seed', type=Path)
    parser.add_argument('--job-start-epoch', type=float)
    parser.add_argument('--controls-child', action='store_true')
    parser.add_argument('--report-root', type=Path)
    parser.add_argument('--deadline', type=float)
    args = parser.parse_args(argv)
    if args.controls_child:
        try:
            return control_child(args.report_root, args.deadline)
        except BaseException as error:
            import json
            print(observation.PREFIX + json.dumps({'events': [], 'preflight_failure': {
                'exception_category': observation.exception_category(error),
                'reason': observation.reason_category(error)}}), flush=True)
            return 2
    start = time.monotonic()
    environment = dict(os.environ)
    session, root, complete, clean, failure = None, None, False, False, None
    progress = {'raw_source_integrity_verified': False, 'active_phase': 'preflight'}
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
        root = Path(tempfile.mkdtemp(prefix='snapshot-owner-', dir=temp))
        session = observation.ObservedSession(root, deadline)
        collect(session, observer, seed, progress)
        phase(session, progress, 'environment')
        q.require(dict(os.environ) == environment, 'environment_changed')
        complete = True
    except BaseException as error:
        failure = observation.reason_category(error)
        try:
            q.safe_exception(error, root)
        except BaseException:
            pass
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
        q.emit('snapshot_summary', **progress, diagnostic_collection_complete=complete,
               process_cleanup_verified=clean, status='diagnostic-passed' if passed else 'inconclusive',
               full_suite=False, performance_probes=0, application_methods=0, qualification=False,
               automatic_rerun=False, private_raw_evidence_uploaded=False,
               failure=failure, observer_seconds=time.monotonic()-start)
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
