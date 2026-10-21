#!/usr/bin/env python3
"""One bounded original-source staging diagnostic; never a performance run."""
import argparse
import io
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
import staging_retained_controls as retained_controls
from diagnose_lazy_setup import budget_deadline
from lazy_suite_support import RESULT_PREFIX

PREFIX = 'test_subagent_staging_hook.SubagentStagingLaunch.'
CASES = (
    (PREFIX + 'test_existing_nonempty_folder_accepts_relative_absolute_and_backslash_routes', [68, 68, 71]),
    (PREFIX + 'test_reused_brief_fails_after_cleanup_removed_its_folder', [75]),
    (PREFIX + 'test_registered_peer_checkout_is_accepted', [122]),
    (PREFIX + 'test_temp_locations_are_refused_even_without_a_run', []),
    (PREFIX + 'test_file_traversal_root_and_missing_folder_do_not_satisfy_route', []),
)


def child(repo, selector):
    """Observe unchanged cases; raw unittest detail goes only to private capture."""
    q.require(selector in dict(CASES), 'staging_selector_not_allowed')
    sys.path.insert(0, str(repo / 'tools'))
    import subagent_staging_hook as hook
    source = (repo / 'tools/test_subagent_staging_hook.py').resolve()
    sessions = repo / 'scratch/sessions'
    sessions.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='staging-policy-', dir=sessions) as private:
        stage = Path(private) / 'pass'
        stage.mkdir()
        def invoke(route):
            return hook.handle({'tool_name': 'Agent', 'tool_input': {'prompt':
                'Read output/synthetic/; stage in `' + route + '`'}, 'cwd': str(repo)})
        absolute = invoke(str(stage))
        relative = invoke(stage.relative_to(repo).as_posix())
        named_temp = hook.names_temp(str(repo))
        expected_absolute = hook.refuse() if named_temp else {}
        policy = {'absolute_response_exact': absolute == expected_absolute,
                  'registered_relative_accepted': relative == {}}
    events = []
    class Result(unittest.TextTestResult):
        def record(self, test, err):
            locations = []
            cursor = err[2]
            while cursor is not None:
                if Path(cursor.tb_frame.f_code.co_filename).resolve() == source:
                    locations.append(cursor.tb_lineno)
                cursor = cursor.tb_next
            events.append({'test_token': q.digest(test.id().encode()),
                           'exception_type': 'AssertionError' if err[0] is AssertionError else 'OtherException',
                           'source_line': locations[-1] if locations else None})
        def addFailure(self, test, err):
            self.record(test, err)
            super().addFailure(test, err)
        def addError(self, test, err):
            self.record(test, err)
            super().addError(test, err)
        def addSubTest(self, test, subtest, err):
            if err is not None:
                self.record(test, err)
            super().addSubTest(test, subtest, err)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(selector)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, resultclass=Result, verbosity=2).run(suite)
    sys.stderr.write(stream.getvalue())
    row = {'test_token': q.digest(selector.encode()), 'tests_run': result.testsRun,
           'failures': len(result.failures), 'errors': len(result.errors),
           'skips': len(result.skipped), 'expected_failures': len(result.expectedFailures),
           'unexpected_successes': len(result.unexpectedSuccesses), 'loader_errors': len(loader.errors),
           'test_successful': result.wasSuccessful(), 'checkout_named_temp': hook.names_temp(str(repo)),
           **policy, 'failure_events': events[:20], 'events_truncated': len(events) > 20}
    print(RESULT_PREFIX + json.dumps(row, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


def exact_value(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(exact_value(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(exact_value(left, right) for left, right in zip(actual, expected))
    return actual == expected


def validate_case_receipt(raw, returncode):
    """Malformed evidence is unsafe, distinct from a valid unexpected outcome."""
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            q.require(key not in result, 'staging_child_receipt_invalid')
            result[key] = value
        return result
    try:
        row = json.loads(raw, object_pairs_hook=object_pairs)
    except (ValueError, TypeError):
        raise q.Refused('staging_child_receipt_invalid') from None
    counts = {'tests_run', 'failures', 'errors', 'skips', 'expected_failures',
              'unexpected_successes', 'loader_errors'}
    flags = {'test_successful', 'checkout_named_temp', 'absolute_response_exact',
             'registered_relative_accepted', 'events_truncated'}
    q.require(type(row) is dict and set(row) == counts | flags | {'test_token', 'failure_events'},
              'staging_child_receipt_invalid')
    q.require(all(type(row[key]) is int and 0 <= row[key] <= 10000 for key in counts)
              and all(type(row[key]) is bool for key in flags)
              and type(returncode) is int and -(2**31) <= returncode < 2**32,
              'staging_child_receipt_invalid')
    token = lambda value: type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None
    q.require(token(row['test_token']) and type(row['failure_events']) is list
              and len(row['failure_events']) <= 20, 'staging_child_receipt_invalid')
    for event in row['failure_events']:
        q.require(type(event) is dict and set(event) == {'test_token', 'exception_type', 'source_line'},
                  'staging_child_receipt_invalid')
        q.require(token(event['test_token']) and event['exception_type'] in ('AssertionError', 'OtherException')
                  and (event['source_line'] is None or
                       (type(event['source_line']) is int and 0 < event['source_line'] < 1000000)),
                  'staging_child_receipt_invalid')
    return row


def classify_case(result, selector, temp_layout):
    rows = [line[len(RESULT_PREFIX):] for line in result['stdout'].splitlines() if line.startswith(RESULT_PREFIX)]
    q.require(len(rows) == 1, 'staging_child_receipt_missing')
    q.require(selector in dict(CASES) and type(temp_layout) is bool, 'staging_selector_not_allowed')
    row = validate_case_receipt(rows[0], result.get('returncode'))
    expected_lines = dict(CASES)[selector] if temp_layout else []
    token = q.digest(selector.encode())
    expected = {'test_token': token, 'tests_run': 1, 'failures': len(expected_lines), 'errors': 0,
                'skips': 0, 'expected_failures': 0, 'unexpected_successes': 0, 'loader_errors': 0,
                'test_successful': not expected_lines, 'checkout_named_temp': temp_layout,
                'absolute_response_exact': True, 'registered_relative_accepted': True,
                'failure_events': [{'test_token': token, 'exception_type': 'AssertionError', 'source_line': line}
                                   for line in expected_lines], 'events_truncated': False}
    matched = exact_value(row, expected) and type(result['returncode']) is int and result['returncode'] == (1 if expected_lines else 0)
    # Do not emit arbitrary child strings, even on a malformed receipt.
    q.require(isinstance(row, dict), 'staging_child_receipt_invalid')
    observed = {key: value if type(value) is int and 0 <= value <= 10000 else None
                for key in ('tests_run', 'failures', 'errors', 'skips', 'expected_failures', 'unexpected_successes')
                for value in (row.get(key),)}
    events = row.get('failure_events')
    observed_events = []
    if isinstance(events, list):
        for event in events[:20]:
            if not isinstance(event, dict):
                continue
            event_token = event.get('test_token')
            line = event.get('source_line')
            observed_events.append({'test_token': event_token if isinstance(event_token, str) and re.fullmatch(r'[0-9a-f]{64}', event_token) else None,
                                    'source_line': line if type(line) is int and 0 < line < 1000000 else None,
                                    'exception_type': event.get('exception_type') if event.get('exception_type') in ('AssertionError', 'OtherException') else 'unread'})
    return {'test_token': token, 'observed_failure_events': observed_events, 'expected_failure_lines': expected_lines,
            'returncode': result['returncode'], 'expectation_matched': matched,
            'test_successful': row.get('test_successful') is True,
            'checkout_named_temp': row.get('checkout_named_temp') if type(row.get('checkout_named_temp')) is bool else None,
            'absolute_response_exact': row.get('absolute_response_exact') is True,
            'registered_relative_accepted': row.get('registered_relative_accepted') is True,
            **observed}


def run_arm(session, observer, seed, repo, role, expected, progress):
    q.require(role in ('temp-layout', 'workspace-layout'), 'unknown_staging_arm')
    target = m.source_context(session, seed, repo, 'baseline', expected, b'')
    q.require(target == expected, 'staging_source_delta_forbidden')
    temp_receipt = q.parse_child(session.run(q.child_command(observer, 'validate-temp', repo), repo / 'tools'))
    q.require(temp_receipt.get('outside_checkout_temp') is True and temp_receipt.get('temp_environment_unchanged') is True,
              'temp_validation_incomplete')
    row = {'role': role, 'source_sha': q.BASE, 'raw_source_verified': True,
           'setup_admitted': True, 'performance_admitted': False, 'cases': []}
    progress.append(row)
    q.emit('staging_arm_identity', role=role, source_sha=q.BASE, raw_source_verified=True,
           original_source=True, performance_admitted=False)
    for selector, _ in CASES:
        result = session.run([sys.executable, str(observer / 'diagnostics/diagnose_staging_layout.py'),
                              '--child', '--repo', str(repo), '--selector', selector], repo / 'tools')
        outcome = classify_case(result, selector, role == 'temp-layout')
        row['cases'].append(outcome)
        q.emit('staging_case', role=role, **outcome)
        m.retained_guard(session, repo, expected, False)
    sessions = repo / 'scratch/sessions'
    q.require(sessions.is_dir() and not any(sessions.iterdir()), 'staging_parent_not_empty_or_absent')
    m.retained_guard(session, repo, expected, False)
    row.update(empty_sessions_verified=True, final_raw_source_verified=True,
               expectations_matched=all(case['expectation_matched'] for case in row['cases']))
    q.emit('staging_arm_complete', **row)


def verify_retained_controls(session, observer):
    report_root = session.root / 'retained-controls'
    report_root.mkdir()
    result = session.run([sys.executable, str(observer / 'diagnostics/staging_retained_controls.py'),
                          '--report-root', str(report_root), '--deadline', str(session.deadline)], observer / 'diagnostics')
    q.require(type(result.get('returncode')) is int and result['returncode'] == 0,
              'retained_controls_failed')
    try:
        row = json.loads(result['stdout'])
    except (ValueError, TypeError):
        raise q.Refused('retained_controls_receipt_invalid') from None
    retained_controls.validate_receipt(row)
    q.require(row['native_link_kind'] == 'junction', 'retained_controls_native_link_missing')
    q.emit('retained_output_controls', **row)


def setup(session, observer, seed, progress):
    q.first_clean(session, observer, os.environ.get('GITHUB_SHA'), 'observer')
    session.git(observer, 'merge-base', '--is-ancestor', q.OBSERVER_BASE, 'HEAD')
    q.require(set(session.git(observer, 'diff', '--name-only', q.OBSERVER_BASE, 'HEAD').splitlines()) == q.OBSERVER_PATHS,
              'observer_branch_scope_changed')
    q.first_clean(session, seed, q.BASE, 'seed')
    snapshot = q.inventory(observer, deadline=session.deadline)
    expected = q.raw_source_inventory(session, seed, q.BASE)
    q.require(expected[q.SUITE_PATH] == q.ORIGINAL_HASH, 'baseline_module_hash_changed')
    identity = m.environment_identity()
    q.emit('staging_scope', source_sha=q.BASE, environment=identity, planned_cases_per_arm=5,
           full_suite=False, performance_probes=0, job_seconds=600, cleanup_reserve_seconds=60)
    result = session.run([sys.executable, str(observer / 'diagnostics/windows_job_probe_controls.py'),
                          '--run', '--report-dir', str(session.root / 'owner-controls')], observer / 'diagnostics')
    q.require(result['returncode'] == 0, 'owner_controls_failed')
    q.validate_owner_controls(json.loads(result['stdout']))
    q.emit('owner_controls', passed=True, count=9)
    verify_retained_controls(session, observer)
    temp_root = q.create_measurement_root(session.root, observer, seed)
    longest_temp = max(len(str(temp_root / 'baseline' / name).encode('utf-16-le', errors='surrogatepass')) // 2 for name in expected)
    q.require(longest_temp < 260, 'temp_source_path_too_long')
    q.emit('temp_clone_boundary', longest_source_utf16_units=longest_temp, previous_short_temp_layout=True)
    workspace_root = m.workspace_clone_root(session.root, observer, seed, expected)
    for root, role in ((temp_root, 'temp-layout'), (workspace_root, 'workspace-layout')):
        run_arm(session, observer, seed, root / 'baseline', role, expected, progress)
    for root in (temp_root, workspace_root):
        m.retained_guard(session, root / 'baseline', expected, False)
    q.require(q.inventory(seed, deadline=session.deadline) == expected, 'seed_changed')
    for name, checksum in snapshot.items():
        q.require(q.digest((observer / name).read_bytes()) == checksum, 'observer_source_changed')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observer', type=Path)
    parser.add_argument('--seed', type=Path)
    parser.add_argument('--job-start-epoch', type=float)
    parser.add_argument('--child', action='store_true')
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--selector')
    args = parser.parse_args(argv)
    if args.child:
        return child(args.repo.resolve(), args.selector)
    session, root, complete, clean, failure = None, None, False, False, None
    arms = []
    start = time.monotonic()
    environment = dict(os.environ)
    try:
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
        root = Path(tempfile.mkdtemp(prefix='staging-diagnostic-owner-', dir=temp))
        session = q.Session(root, deadline)
        setup(session, observer, seed, arms)
        q.require(dict(os.environ) == environment, 'environment_changed')
        complete = True
    except BaseException as error:
        failure = str(error) if isinstance(error, q.Refused) else 'unexpected_exception_details_withheld'
        q.safe_exception(error, root)
        q.emit('hold', reason=failure, error_type=type(error).__name__, performance_claim_allowed=False)
    finally:
        if session is not None:
            clean = session.cleanup()
        matched = complete and len(arms) == 2 and all(row.get('expectations_matched') is True for row in arms)
        passed = matched and clean
        q.emit('staging_diagnostic_summary', diagnostic_collection_complete=complete,
               diagnostic_expectations_matched=matched, process_cleanup_verified=clean,
               raw_source_integrity_verified=complete, status='diagnostic-passed' if passed else 'inconclusive',
               arms=arms, full_suite=False, performance_probes=0, qualification=False,
               original_hosted_failure_ids_established=False, raw_evidence_uploaded=False,
               automatic_rerun=False, observer_seconds=time.monotonic()-start, failure=failure)
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
