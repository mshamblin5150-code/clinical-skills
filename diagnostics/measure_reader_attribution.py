#!/usr/bin/env python3
"""One unchanged reader-audit class on the lazy candidate; no full-suite route."""
import contextlib
import ast
import argparse
import importlib
import io
import json
import math
import os
import platform
import re
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

import measure_lazy_suite_ids as q
import generated_output_contract as contract
import measure_maintainer_pair as maintainer
import diagnose_generated_outputs as generated
from diagnose_checkpoint_discovery import CheckpointSession
from diagnose_staging_layout import verify_retained_controls
from lazy_suite_support import AUDIT_PATH, AUDIT_HASH
from diagnostic_observations import unique_json
from parallel_reader_capture import analyze_capture
from parallel_reader_scheduler import Observation, account_pairs, audit_sets

SOURCE_SHA = '08db6360b453c2bf969a686f62f0477184d06351'
TEST_HASH = '082cf406faf237ec34839e49a7046b2dc049e721887a4a8671817cd8ef8f2d21'
CLASS_ID = 'test_code_set_database_reader_check.TheReaderPopulationAndThePinsMustAgree'
METHODS = ('test_planted_unpinned_readers_and_a_stale_pin_fail_in_both_directions',
           'test_the_repository_reader_population_and_pins_agree')
SCOPES = ('planted', 'repository')
BRANCH = 'refs/heads/diagnostic/2013-parallel-proof-20261020'
BUDGET = {'schema_version': 1, 'admission_mode': 'estimate-not-completion-guarantee',
          'source_sha': SOURCE_SHA, 'candidate_sha256': q.CANDIDATE_HASH,
          'approved_job_seconds': 3600, 'setup_controls_estimate_seconds': 900,
          'measurement_estimate_seconds': 2100, 'final_verification_estimate_seconds': 300,
          'cleanup_reserve_seconds': 300, 'minimum_free_bytes': 1073741824,
          'max_capture_bytes': 16777216, 'max_receipt_bytes': 4194304}
OBSERVER_PATHS = maintainer.OBSERVER_PATHS | {
    '.github/workflows/ci-reader-attribution.yml', 'diagnostics/measure_reader_attribution.py',
    'diagnostics/test_reader_attribution.py', 'diagnostics/reader-attribution-budget.json',
    'diagnostics/reader-attribution-spec.md'}


def validate_budget(plan):
    q.require(type(plan) is dict and plan == BUDGET
              and all(type(plan[key]) is type(value) for key, value in BUDGET.items()), 'budget_contract_changed')


def budget_deadlines(origin, wall_now, monotonic_now):
    q.require(all(type(value) in (int, float) and math.isfinite(value)
                  for value in (origin, wall_now, monotonic_now)), 'setup_clock_invalid')
    elapsed = wall_now - origin
    q.require(0 <= elapsed < 3300, 'setup_budget_exhausted')
    hard = monotonic_now + 3600 - elapsed
    return hard - 300, hard


def admit_class(deadline, now):
    q.require(type(deadline) in (int, float) and type(now) in (int, float)
              and math.isfinite(deadline) and math.isfinite(now) and deadline - now >= 2400,
              'estimated_reader_class_no_longer_fits')


def authorize_route(system, version, environment):
    q.require(system == 'nt' and version == '3.14.4', 'windows_python_pin_required')
    q.require(environment.get('GITHUB_ACTIONS') == 'true' and environment.get('GITHUB_EVENT_NAME') == 'push'
              and environment.get('GITHUB_REF') == BRANCH and environment.get('GITHUB_RUN_ATTEMPT') == '1'
              and re.fullmatch(r'[0-9a-f]{40}', environment.get('GITHUB_SHA', ''))
              and re.fullmatch(r'[0-9]{1,20}', environment.get('GITHUB_RUN_ID', '')),
              'unauthorized_event_or_rerun')


def population_from_sources(check, sources):
    """Use the pinned audit's import/reach/pin rules on every top-level .py file."""
    q.require(0 < len(sources) <= 10000 and all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*\.py', name)
              and type(raw) is bytes for name, raw in sources.items()), 'audit_sources_invalid')
    trees = {name[:-3]: ast.parse(raw.decode('utf-8')) for name, raw in sources.items()}
    local = frozenset(trees)
    graph = {name: check._imports(tree, local) for name, tree in trees.items()}
    tests = frozenset(name for name in trees if name.startswith('test'))
    modules = tuple(sorted(name for name in tests if check._reaches_lookup(name, graph)))
    pins = frozenset((name, lookup) for name in tests for lookup in check._pins(trees[name]))
    return {'modules': modules, 'pinned': pins, 'source_file_count': len(sources),
            'source_hashes': {name: q.digest(raw) for name, raw in sorted(sources.items())}}


def source_population(check, tools, deadline):
    sources = {path.name: contract.safe_read(tools, path.name, q.BUDGET['max_capture_bytes'], deadline)
               for path in tools.glob('*.py')}
    return population_from_sources(check, sources)


def planted_sources(raw):
    """Recover literal synthetic writes from the pinned original method, without running it."""
    tree = ast.parse(raw.decode('utf-8'))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == CLASS_ID.rsplit('.', 1)[-1])
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == METHODS[0])
    sources = {}
    for node in ast.walk(method):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == 'write_text'):
            continue
        path = node.func.value
        q.require(isinstance(path, ast.BinOp) and isinstance(path.op, ast.Div)
                  and isinstance(path.left, ast.Name) and path.left.id == 'tools'
                  and isinstance(path.right, ast.Constant) and type(path.right.value) is str
                  and path.right.value not in sources and len(node.args) == 1,
                  'planted_source_changed')
        content = ast.literal_eval(node.args[0])
        q.require(type(content) is str, 'planted_source_changed')
        sources[path.right.value] = content.replace('\n', os.linesep).encode('utf-8')
    return sources


def token(parts):
    return q.digest(json.dumps(parts, ensure_ascii=True, separators=(',', ':')).encode())


def metric(value):
    return value if type(value) in (int, float) and math.isfinite(value) and value >= 0 else None


def original_text(raw):
    # Same UTF-8/errors-replace and universal-newline semantics as subprocess.run.
    return raw.decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n')


PAIR_KEYS = frozenset(('scope', 'index', 'pair_token', 'classification', 'returncode', 'completion',
    'call_wall_seconds', 'owned_wall_seconds', 'tree_cpu_seconds', 'analysis_seconds', 'test_count',
    'failures', 'errors', 'skipped', 'expected_failures', 'stdout_bytes', 'stderr_bytes',
    'stdout_sha256', 'stderr_sha256', 'cleanup_verified', 'screen_clean', 'capture_read_verified'))


def encode_pairs(rows, manifests):
    """Public receipt boundary: source-known identities, exact fields and strict finite types."""
    expected = [(scope, index + 1, token([scope, module, lookup])) for scope in SCOPES if scope in manifests
                for index, (module, lookup) in enumerate((module, lookup)
                    for module in manifests[scope]['modules'] for lookup in q.LOOKUPS)]
    q.require(type(rows) is list and len(rows) <= len(expected), 'audit_receipt_invalid')
    for position, row in enumerate(rows):
        q.require(type(row) is dict and set(row) == PAIR_KEYS, 'audit_receipt_invalid')
        q.require((row['scope'], row['index'], row['pair_token']) == expected[position]
                  and type(row['index']) is int, 'audit_receipt_invalid')
        q.require(row['classification'] in ('reader', 'nonreader', 'error', 'unread')
                  and row['completion'] in ('completed', 'incomplete'), 'audit_receipt_invalid')
        q.require(all(type(row[key]) is bool for key in ('cleanup_verified', 'screen_clean', 'capture_read_verified')),
                  'audit_receipt_invalid')
        for key in ('call_wall_seconds', 'owned_wall_seconds', 'tree_cpu_seconds', 'analysis_seconds'):
            q.require(row[key] is None or (metric(row[key]) is not None and row[key] <= 3600 * 1024),
                      'audit_receipt_invalid')
        for key in ('test_count', 'failures', 'errors', 'skipped', 'expected_failures'):
            q.require(row[key] is None or (type(row[key]) is int and 0 <= row[key] <= 1000000), 'audit_receipt_invalid')
        for key in ('stdout_bytes', 'stderr_bytes'):
            q.require(row[key] is None or (type(row[key]) is int and 0 <= row[key] <= BUDGET['max_capture_bytes']),
                      'audit_receipt_invalid')
        for key in ('stdout_sha256', 'stderr_sha256'):
            q.require(row[key] is None or (type(row[key]) is str and re.fullmatch(r'[0-9a-f]{64}', row[key])),
                      'audit_receipt_invalid')
        q.require(row['returncode'] is None or (type(row['returncode']) is int
                  and -(2**31) <= row['returncode'] < 2**32), 'audit_receipt_invalid')
        if row['completion'] == 'completed':
            q.require(row['cleanup_verified'] and row['capture_read_verified']
                      and all(row[key] is not None for key in ('returncode', 'call_wall_seconds',
                          'owned_wall_seconds', 'tree_cpu_seconds', 'analysis_seconds',
                          'stdout_bytes', 'stderr_bytes', 'stdout_sha256', 'stderr_sha256'))
                      and row['classification'] != 'unread', 'audit_receipt_invalid')
        else:
            q.require(position == len(rows) - 1, 'audit_receipt_invalid')
    try:
        raw = json.dumps(rows, sort_keys=True, allow_nan=False, separators=(',', ':')).encode()
    except (ValueError, TypeError, RecursionError):
        raise q.Refused('audit_receipt_invalid') from None
    q.require(len(raw) <= BUDGET['max_receipt_bytes'], 'audit_receipt_limit')
    return raw


def read_pairs(raw, manifests):
    q.require(type(raw) is bytes and len(raw) <= BUDGET['max_receipt_bytes'], 'audit_receipt_limit')
    try:
        rows = unique_json(raw)
    except (ValueError, TypeError, RecursionError, UnicodeError):
        raise q.Refused('audit_receipt_invalid') from None
    encode_pairs(rows, manifests)
    return rows


class PrivateWriter:
    """Bound Python import/test output without forwarding any of its content."""
    encoding = 'utf-8'
    def __init__(self, stream, deadline):
        self.stream, self.deadline, self.count = stream, deadline, 0
    def write(self, text):
        raw = text.encode('utf-8', errors='replace')
        q.require(time.monotonic() < self.deadline, 'global_budget_exhausted')
        q.require(self.count + len(raw) <= q.BUDGET['max_capture_bytes'], 'capture_limit_exceeded')
        q.require(shutil.disk_usage(Path(self.stream.name).parent).free >= BUDGET['minimum_free_bytes'],
                  'disk_reserve_exhausted')
        self.stream.write(raw)
        self.count += len(raw)
        return len(text)
    def flush(self):
        self.stream.flush()


class ReaderAdapter:
    """The original loop delegates only its module-local run binding to ownership."""
    def __init__(self, check, repository, manifests, session, payload, publish=None):
        self.check, self.repository, self.manifests = check, repository, manifests
        self.session, self.payload = session, payload
        self.rows, self.observations, self.invocations = [], {}, []
        self.scope, self.tools, self.expected, self.index = None, None, (), 0
        self.failure = None
        self.publish = publish
        self.population_check_seconds = 0.0
        self.pair_observer_seconds = 0.0
        self.sets = {}

    def readers(self, tools, reaching):
        scope = 'repository' if tools == self.repository else 'planted'
        q.require(self.scope is None and scope not in self.invocations, 'audit_scope_repeated')
        q.require(scope == SCOPES[len(self.invocations)], 'audit_scope_order_changed')
        manifest = self.manifests[scope]
        q.require(frozenset(manifest['modules']) == reaching, 'audit_population_changed')
        if 'source_hashes' in manifest:
            population_start = time.monotonic()
            q.require(source_population(self.check, tools, self.session.deadline) == manifest,
                      'audit_source_population_changed')
            self.population_check_seconds += time.monotonic() - population_start
        self.scope, self.tools = scope, tools
        self.expected = tuple((module, lookup) for module in manifest['modules'] for lookup in q.LOOKUPS)
        self.index = 0
        self.invocations.append(scope)
        self.observations[scope] = []
        try:
            readers = self.original_readers(tools, reaching)
            accounting = account_pairs(manifest['modules'], self.observations[scope])
            q.require(self.index == len(self.expected) and not any(accounting.values()), 'audit_pairs_incomplete')
            observed = frozenset((row.module, row.lookup) for row in self.observations[scope]
                                 if row.classification == 'reader')
            q.require(observed == readers, 'audit_reader_result_changed')
            self.sets[scope] = audit_sets(manifest['modules'], manifest['pinned'], self.observations[scope])
            # Return exactly the original value. The actual test retains both
            # directions of its own assertions, including the planted failures.
            return readers
        finally:
            self.scope = None

    def run(self, argv, **kwargs):
        start = time.monotonic()
        q.require(self.scope is not None and self.index < len(self.expected), 'audit_unexpected_command')
        module, lookup = self.expected[self.index]
        q.require(argv == [sys.executable, '-c', self.payload, str(self.tools), module, lookup]
                  and kwargs == {'cwd': self.tools, 'text': True, 'encoding': 'utf-8', 'errors': 'replace',
                                 'capture_output': True, 'check': False}
                  and all(type(kwargs[key]) is bool for key in ('text', 'capture_output', 'check')),
                  'audit_command_changed')
        row = {'scope': self.scope, 'index': self.index + 1,
               'pair_token': token([self.scope, module, lookup]), 'classification': 'unread',
               'returncode': None, 'completion': 'incomplete', 'call_wall_seconds': None,
               'owned_wall_seconds': None, 'tree_cpu_seconds': None, 'analysis_seconds': None,
               'test_count': None, 'failures': None, 'errors': None, 'skipped': None,
               'expected_failures': None, 'stdout_bytes': None, 'stderr_bytes': None,
               'stdout_sha256': None, 'stderr_sha256': None, 'cleanup_verified': False,
               'screen_clean': False, 'capture_read_verified': False}
        self.rows.append(row)
        self.index += 1
        previous_owners = len(self.session.owners)
        try:
            result = self.session.run(argv, self.tools)
            row.update(returncode=result['returncode'], cleanup_verified=result['cleanup_verified'] is True,
                       owned_wall_seconds=metric(result.get('wall_seconds')),
                       tree_cpu_seconds=metric(result.get('tree_cpu_seconds')))
            q.require(type(row['returncode']) is int and row['cleanup_verified'], 'process_cleanup_unverified')
            raw = tuple(contract.safe_read(self.session.root,
                        Path(result[key]).relative_to(self.session.root).as_posix(),
                        q.BUDGET['max_capture_bytes'], self.session.deadline)
                        for key in ('stdout_path', 'stderr_path'))
            stdout, stderr = map(original_text, raw)
            row['call_wall_seconds'] = time.monotonic() - start
            analysis_start = time.monotonic()
            parsed = analyze_capture(None, None, result['returncode'], lookup,
                                     module=module, capture_bytes=raw)
            row.update(classification=parsed['classification'], screen_clean=not parsed['unexpected'],
                       analysis_seconds=time.monotonic() - analysis_start, capture_read_verified=True,
                       stdout_bytes=len(raw[0]), stderr_bytes=len(raw[1]),
                       stdout_sha256=q.digest(raw[0]), stderr_sha256=q.digest(raw[1]))
            for key in ('test_count', 'failures', 'errors', 'skipped', 'expected_failures'):
                value = parsed[key]
                row[key] = value if type(value) is int and 0 <= value <= 1000000 else None
            counts_read = all(row[key] is not None for key in ('test_count', 'failures', 'errors', 'skipped', 'expected_failures'))
            row['screen_clean'] = row['screen_clean'] and counts_read
            metrics_read = all(row[key] is not None for key in ('call_wall_seconds', 'owned_wall_seconds', 'tree_cpu_seconds'))
            if not metrics_read:
                self.failure = 'observer_failure'
                if parsed['classification'] != 'error':
                    raise q.Refused('audit_metrics_unread')
            else:
                row['completion'] = 'completed'
            self.observations[self.scope].append(Observation(module, lookup, parsed['classification'],
                unexpected=parsed['unexpected'], cleanup_verified=True))
            # The original first unmarked failure must reach its original raise.
            if (parsed['unexpected'] or not counts_read) and parsed['classification'] != 'error':
                raise q.Refused('audit_capture_contaminated_or_unread')
            return subprocess.CompletedProcess(argv, result['returncode'], stdout, stderr)
        except BaseException:
            self.failure = 'observer_failure'
            # Preserve a known terminal root status from an interrupted owned
            # launch/retirement, without crediting that attempt as complete.
            if row['returncode'] is None and len(self.session.owners) > previous_owners:
                finished = self.session.owners[-1].result
                if finished is not None:
                    snapshot = finished.snapshot
                    code = snapshot.root_exit_code
                    row.update(returncode=code if type(code) is int else None,
                               cleanup_verified=snapshot.cleanup_verified is True,
                               owned_wall_seconds=metric(snapshot.wall_seconds),
                               tree_cpu_seconds=metric(snapshot.tree_cpu_seconds))
            raise
        finally:
            overhead_start = time.monotonic()
            try:
                encode_pairs(self.rows, self.manifests)
                if self.publish is not None:
                    self.publish(row)
            except BaseException:
                self.failure = 'observer_failure'
                raise
            finally:
                self.pair_observer_seconds += time.monotonic() - overhead_start


def observe_class(check, cls, repository, manifests, session, guard, payload, publish=None):
    """Run the real class once using stock loader, TestSuite and TestCase lifecycle."""
    loader = unittest.TestLoader()
    q.require(tuple(loader.getTestCaseNames(cls)) == METHODS, 'audit_methods_changed')
    suite = loader.loadTestsFromTestCase(cls)
    adapter = ReaderAdapter(check, repository, manifests, session, payload, publish)
    methods = [{'method_token': token([CLASS_ID, method]), 'outcome': 'unread',
                'started': False, 'completed': False, 'wall_seconds': None} for method in METHODS]
    guard_seconds = 0.0
    class Result(unittest.TestResult):
        def startTest(self, test):
            row = methods[METHODS.index(test._testMethodName)]
            q.require(not row['started'], 'audit_method_repeated')
            row['started'], self.started_at = True, time.monotonic()
            super().startTest(test)
        def outcome(self, test, name):
            methods[METHODS.index(test._testMethodName)]['outcome'] = name
            if name != 'pass': self.stop()
        def addSuccess(self, test):
            super().addSuccess(test); self.outcome(test, 'pass')
        def addFailure(self, test, err):
            super().addFailure(test, err); self.outcome(test, 'failure')
        def addError(self, test, err):
            super().addError(test, err)
            if isinstance(err[1], q.Refused): adapter.failure = 'observer_failure'
            if getattr(test, '_testMethodName', None) in METHODS: self.outcome(test, 'error')
            else: self.stop()
        def addSkip(self, test, reason):
            super().addSkip(test, reason); self.outcome(test, 'skipped')
        def addExpectedFailure(self, test, err):
            super().addExpectedFailure(test, err); self.outcome(test, 'expected_failure')
        def addUnexpectedSuccess(self, test):
            super().addUnexpectedSuccess(test); self.outcome(test, 'unexpected_success')
        def addSubTest(self, test, subtest, err):
            super().addSubTest(test, subtest, err)
            if err is not None: self.outcome(test, 'failure')
        def stopTest(self, test):
            nonlocal guard_seconds
            row = methods[METHODS.index(test._testMethodName)]
            row.update(completed=row['outcome'] != 'unread' and adapter.failure is None,
                       wall_seconds=time.monotonic() - self.started_at)
            super().stopTest(test)
            started = time.monotonic()
            try: guard()
            finally: guard_seconds += time.monotonic() - started
    result = Result()
    old_loop, old_subprocess = check._readers_under_refusal, check.subprocess
    adapter.original_readers = old_loop
    start = time.monotonic()
    try:
        check._readers_under_refusal, check.subprocess = adapter.readers, adapter
        with (session.root / 'class-stdout.private').open('xb') as stdout, \
             (session.root / 'class-stderr.private').open('xb') as stderr:
            with contextlib.redirect_stdout(PrivateWriter(stdout, session.deadline)), \
                 contextlib.redirect_stderr(PrivateWriter(stderr, session.deadline)):
                suite.run(result)
    except BaseException as error:
        adapter.failure = 'observer_failure'
        q.safe_exception(error, session.root)
    finally:
        check._readers_under_refusal, check.subprocess = old_loop, old_subprocess
    class_wall = time.monotonic() - start
    complete = (result.testsRun == 2 and all(row['outcome'] == 'pass' and row['completed'] for row in methods)
                and adapter.invocations == list(SCOPES) and adapter.failure is None
                and all(row['completion'] == 'completed' and row['screen_clean'] for row in adapter.rows)
                and len(adapter.rows) == sum(len(manifests[scope]['modules']) * 2 for scope in SCOPES))
    return {'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
            'skipped': len(result.skipped), 'expected_failures': len(result.expectedFailures),
            'unexpected_successes': len(result.unexpectedSuccesses), 'methods': methods,
            'pairs': adapter.rows, 'complete': complete, 'class_wall_seconds': class_wall,
            'guard_seconds': guard_seconds, 'population_check_seconds': adapter.population_check_seconds,
            'pair_observer_seconds': adapter.pair_observer_seconds,
            'observer_failure': adapter.failure is not None}


def output_state(origin, observed=None):
    return contract.State(marker='absent', weights='absent', sessions='optional',
                          job_start_epoch=origin, observed_epoch=time.time() if observed is None else observed,
                          max_job_seconds=3600)


def make_session(root, deadline, hard_deadline):
    return CheckpointSession(root, deadline, hard_deadline)


def validate_record(record, manifests):
    keys = {'tests_run', 'failures', 'errors', 'skipped', 'expected_failures', 'unexpected_successes',
            'methods', 'pairs', 'complete', 'class_wall_seconds', 'guard_seconds',
            'population_check_seconds', 'pair_observer_seconds', 'observer_failure'}
    q.require(type(record) is dict and set(record) == keys, 'audit_receipt_invalid')
    for key in ('tests_run', 'failures', 'errors', 'skipped', 'expected_failures', 'unexpected_successes'):
        q.require(type(record[key]) is int and 0 <= record[key] <= 1000000, 'audit_receipt_invalid')
    q.require(record['tests_run'] <= 2 and type(record['complete']) is bool
              and type(record['observer_failure']) is bool, 'audit_receipt_invalid')
    for key in ('class_wall_seconds', 'guard_seconds', 'population_check_seconds', 'pair_observer_seconds'):
        q.require(metric(record[key]) is not None and record[key] < 3600, 'audit_receipt_invalid')
    methods = record['methods']
    q.require(type(methods) is list and len(methods) == 2, 'audit_receipt_invalid')
    for name, row in zip(METHODS, methods):
        q.require(type(row) is dict and set(row) == {'method_token', 'outcome', 'started', 'completed', 'wall_seconds'}
                  and row['method_token'] == token([CLASS_ID, name])
                  and row['outcome'] in ('unread', 'pass', 'failure', 'error', 'skipped', 'expected_failure', 'unexpected_success')
                  and type(row['started']) is bool and type(row['completed']) is bool
                  and (row['wall_seconds'] is None or metric(row['wall_seconds']) is not None)
                  and (not row['completed'] or (row['started'] and row['wall_seconds'] is not None)),
                  'audit_receipt_invalid')
    encode_pairs(record['pairs'], manifests)
    if record['complete']:
        q.require(record['tests_run'] == 2 and not record['observer_failure']
                  and all(record[key] == 0 for key in ('failures', 'errors', 'skipped', 'expected_failures', 'unexpected_successes'))
                  and all(row['completed'] and row['outcome'] == 'pass' for row in methods)
                  and len(record['pairs']) == sum(len(manifests[scope]['modules']) * 2 for scope in SCOPES)
                  and all(row['screen_clean'] and row['completion'] == 'completed' for row in record['pairs']),
                  'audit_receipt_invalid')
    return record


def retained_receipt(session, record, manifests, context):
    start = time.monotonic()
    validate_record(record, manifests)
    q.require(type(context) is dict and set(context) == {'observer_sha', 'run_id', 'job_start_epoch', 'environment_sha256'}
              and type(context['observer_sha']) is str and re.fullmatch(r'[0-9a-f]{40}', context['observer_sha'])
              and type(context['run_id']) is str and re.fullmatch(r'[0-9]{1,20}', context['run_id'])
              and metric(context['job_start_epoch']) is not None
              and type(context['environment_sha256']) is str and re.fullmatch(r'[0-9a-f]{64}', context['environment_sha256']),
              'audit_receipt_context_invalid')
    envelope = {'schema_version': 1, 'source_sha': SOURCE_SHA, 'candidate_sha256': q.CANDIDATE_HASH,
                **context, 'class_receipt': record,
                'population_sha256': token([[scope, list(manifests[scope]['modules']),
                    sorted(manifests[scope]['pinned'])] for scope in SCOPES])}
    raw = json.dumps(envelope, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    q.require(len(raw) <= BUDGET['max_receipt_bytes'], 'audit_receipt_limit')
    path = session.root / 'reader-receipt.json'
    with path.open('xb') as stream:
        stream.write(raw)
    readback = contract.safe_read(session.root, path.name, BUDGET['max_receipt_bytes'], session.deadline)
    q.require(readback == raw, 'audit_receipt_changed')
    try:
        parsed = unique_json(readback)
    except (ValueError, TypeError, RecursionError, UnicodeError):
        raise q.Refused('audit_receipt_invalid') from None
    q.require(parsed == envelope, 'audit_receipt_changed')
    validate_record(parsed['class_receipt'], manifests)
    return {'receipt_sha256': q.digest(readback), 'receipt_bytes': len(readback), 'receipt_verified': True,
            'receipt_verification_seconds': time.monotonic() - start}


def summarize(record, manifests):
    """Only complete observed costs can be ranked as a complete population."""
    validate_record(record, manifests)
    rows = record['pairs']
    scopes = []
    for scope in SCOPES:
        manifest = manifests[scope]
        scoped = [row for row in rows if row['scope'] == scope]
        scopes.append({'scope': scope, 'source_file_count': manifest['source_file_count'],
                       'modules_expected': len(manifest['modules']), 'pairs_expected': len(manifest['modules']) * 2,
                       'pairs_attempted': len(scoped), 'pairs_completed': sum(row['completion'] == 'completed' for row in scoped),
                       'pairs_unread': len(manifest['modules']) * 2 - sum(row['completion'] == 'completed' for row in scoped),
                       'pair_manifest_sha256': token([[scope, module, lookup] for module in manifest['modules'] for lookup in q.LOOKUPS])})
    summary = {key: record[key] for key in record if key != 'pairs'}
    summary['scopes'] = scopes
    summary['top_children'] = []
    summary['module_totals'] = []
    summary['child_tree_cpu_seconds'] = None
    summary['residual_static_and_observer_seconds'] = None
    summary['between_method_seconds'] = None
    if record['complete']:
        summary['top_children'] = sorted(rows, key=lambda row: (-row['call_wall_seconds'], row['pair_token']))[:10]
        summary['child_tree_cpu_seconds'] = sum(row['tree_cpu_seconds'] for row in rows)
        analysis = sum(row['analysis_seconds'] for row in rows)
        summary['capture_analysis_seconds'] = analysis
        summary['residual_static_and_observer_seconds'] = max(0.0, record['class_wall_seconds']
            - sum(row['call_wall_seconds'] for row in rows) - analysis - record['guard_seconds']
            - record['population_check_seconds'] - record['pair_observer_seconds'])
        summary['between_method_seconds'] = max(0.0, record['class_wall_seconds']
            - sum(row['wall_seconds'] for row in record['methods']) - record['guard_seconds'])
        by_token = {row['pair_token']: row for row in rows}
        for scope in SCOPES:
            for module in manifests[scope]['modules']:
                members = [by_token[token([scope, module, lookup])] for lookup in q.LOOKUPS]
                summary['module_totals'].append({'scope': scope, 'module_token': token([scope, module]),
                    'call_wall_seconds': sum(row['call_wall_seconds'] for row in members),
                    'tree_cpu_seconds': sum(row['tree_cpu_seconds'] for row in members)})
        summary['module_totals'].sort(key=lambda row: (-row['call_wall_seconds'], row['module_token']))
    return summary


def execute(session, observer, seed, origin, progress, environment):
    """Current raw/source/native guard chain, followed by exactly one actual class."""
    preparation = time.monotonic()
    q.first_clean(session, observer, environment['GITHUB_SHA'], 'observer')
    session.git(observer, 'merge-base', '--is-ancestor', q.OBSERVER_BASE, 'HEAD')
    q.require(set(session.git(observer, 'diff', '--name-only', q.OBSERVER_BASE, 'HEAD').splitlines()) == OBSERVER_PATHS,
              'observer_branch_scope_changed')
    q.first_clean(session, seed, SOURCE_SHA, 'seed')
    validate_budget(unique_json(contract.safe_read(observer, 'diagnostics/reader-attribution-budget.json',
                                                   16384, session.deadline)))
    snapshot = q.inventory(observer, deadline=session.deadline)
    expected = q.raw_source_inventory(session, seed, SOURCE_SHA)
    q.require(expected[q.SUITE_PATH] == q.ORIGINAL_HASH, 'baseline_module_hash_changed')
    candidate = q.read_reviewed_bytes(observer / q.SUITE_PATH, q.CANDIDATE_HASH)
    refs = {repo: session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)') for repo in (observer, seed)}
    clone = None
    def guard():
        q.require(dict(os.environ) == environment and time.monotonic() < session.deadline, 'environment_or_budget_changed')
        for repo, target, pin in ((observer, snapshot, environment['GITHUB_SHA']), (seed, expected, SOURCE_SHA)):
            q.verify_sources(session, repo, target, source_sha=pin)
            q.require(session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)') == refs[repo], 'source_refs_changed')
            contract.scan(repo, target, session.deadline, output_state(origin))
        if clone is not None:
            maintainer.generated_guard(session, *clone, True, output_state(origin))
    def checked(phase, action):
        progress['phase'] = phase
        session.phase = phase
        guard()
        result = action()
        guard()
        return result
    def native():
        result = session.run([sys.executable, str(observer / 'diagnostics/windows_job_probe_controls.py'),
                              '--run', '--report-dir', str(session.root / 'owner-controls')], observer / 'diagnostics')
        q.require(result['returncode'] == 0, 'owner_controls_failed')
        q.validate_owner_controls(unique_json(result['stdout']))
        progress['owner_control_count'] = len(q.DECLARED_CONTROL_IDS)
    checked('native', native)
    checked('retained', lambda: verify_retained_controls(session, observer))
    def output_controls():
        result = session.run([sys.executable, str(observer / 'diagnostics/diagnose_generated_outputs.py'),
                              '--contract-child'], observer / 'diagnostics')
        q.verify_probe(result, generated.CONTRACT_CONTROL_COUNT, q.LOOKUPS[0])
        progress['generated_control_count'] = generated.CONTRACT_CONTROL_COUNT
    checked('contract', output_controls)
    root = checked('clone', lambda: maintainer.workspace_clone_root(session.root, observer, seed, expected))
    repo = root / 'candidate'
    target = checked('clone', lambda: maintainer.source_context(session, seed, repo, 'candidate', expected,
                                                              candidate, source_sha=SOURCE_SHA))
    clone = (repo, target)
    def temp_check():
        row = q.parse_child(session.run(q.child_command(observer, 'validate-temp', repo), repo / 'tools'))
        q.require(row.get('outside_checkout_temp') is True and row.get('temp_environment_unchanged') is True,
                  'temp_validation_incomplete')
        maintainer.verify_hook_location(session, repo)
    checked('temp', temp_check)
    checked('pair_behavior', lambda: maintainer.behavior_controls(session, observer, repo, 'candidate'))
    checked('pair_explicit', lambda: maintainer.explicit_controls(session, seed, repo))
    guard()
    tools = repo / 'tools'
    test_path = 'tools/test_code_set_database_reader_check.py'
    test_raw = contract.safe_read(repo, test_path, BUDGET['max_capture_bytes'], session.deadline)
    audit_raw = contract.safe_read(repo, AUDIT_PATH, BUDGET['max_capture_bytes'], session.deadline)
    q.require(q.digest(test_raw) == TEST_HASH and q.digest(audit_raw) == AUDIT_HASH, 'audit_source_hash_mismatch')
    payload = q.original_payload(repo)
    # No application import/discovery occurs before this gated point.
    for name in ('code_set_database_reader_check', 'test_code_set_database_reader_check'):
        q.require(name not in sys.modules, 'audit_module_already_loaded')
    saved_path = sys.path[:]
    sys.path.insert(0, str(tools))
    public = sys.stdout
    try:
        with (session.root / 'import-stdout.private').open('xb') as stdout, \
             (session.root / 'import-stderr.private').open('xb') as stderr:
            with contextlib.redirect_stdout(PrivateWriter(stdout, session.deadline)), \
                 contextlib.redirect_stderr(PrivateWriter(stderr, session.deadline)):
                check = importlib.import_module('code_set_database_reader_check')
                test_module = importlib.import_module('test_code_set_database_reader_check')
        q.require(Path(check.__file__).resolve() == repo / AUDIT_PATH
                  and Path(test_module.__file__).resolve() == repo / test_path
                  and check.LOOKUPS == frozenset(q.LOOKUPS) and check._SUBPROCESS == payload,
                  'audit_import_identity_changed')
        cls = getattr(test_module, CLASS_ID.rsplit('.', 1)[-1])
        q.require(cls.__module__ + '.' + cls.__name__ == CLASS_ID, 'audit_class_identity_changed')
        manifests = {'repository': source_population(check, tools, session.deadline),
                     'planted': population_from_sources(check, planted_sources(test_raw))}
        q.require(len(manifests['planted']['modules']) == 11, 'planted_population_changed')
        q.require(manifests['repository']['source_hashes'] ==
                  {Path(name).name: value for name, value in target.items()
                   if name.startswith('tools/') and '/' not in name[6:] and name.endswith('.py')},
                  'audit_source_population_changed')
        guard()
        admit_class(session.deadline, time.monotonic())
        progress['setup_seconds'] = time.monotonic() - preparation
        progress['phase'] = 'reader_class'
        source_map = [{'scope': scope, 'module': module, 'lookup': lookup,
                       'module_token': token([scope, module]), 'pair_token': token([scope, module, lookup])}
                      for scope in SCOPES for module in manifests[scope]['modules'] for lookup in q.LOOKUPS]
        q.require(len(json.dumps(source_map)) < BUDGET['max_receipt_bytes'], 'audit_receipt_limit')
        q.emit('reader_source_map', source_sha=SOURCE_SHA, candidate_sha256=q.CANDIDATE_HASH, pairs=source_map)
        def publish(row):
            public.write(json.dumps({'event': 'reader_pair', **row}, sort_keys=True, allow_nan=False) + '\n')
            public.flush()
        record = observe_class(check, cls, tools, manifests, session, guard, payload, publish)
        progress['class_record'] = record
        progress['class_summary'] = summarize(record, manifests)
        progress.update(retained_receipt(session, record, manifests,
            {'observer_sha': environment['GITHUB_SHA'], 'run_id': environment['GITHUB_RUN_ID'],
             'job_start_epoch': origin, 'environment_sha256': progress['environment_sha256']}))
        guard()
        progress.update(source_integrity_verified=True, output_contract_verified=True)
        q.require(record['complete'], 'reader_attribution_incomplete')
    finally:
        sys.path[:] = saved_path


class PublicOutput:
    """One route-wide public byte allowance, including reused helper emissions."""
    def __init__(self, stream):
        self.stream, self.bytes_written, self.terminal, self.failed = stream, 0, False, False

    def write(self, text):
        q.require(not self.failed, 'public_output_unavailable')
        size = len(text.encode('utf-8'))
        limit = BUDGET['max_receipt_bytes'] - (0 if self.terminal else 4096)
        # print writes the JSON object and newline separately. Reserve that
        # newline before forwarding the object so a quota refusal is framed.
        q.require(self.bytes_written + size + (not text.endswith('\n')) <= limit,
                  'public_receipt_limit_exceeded')
        self.bytes_written += size  # Charge a possibly partial failed write, too.
        try:
            written = self.stream.write(text)
            q.require(written == len(text), 'public_output_incomplete')
        except BaseException:
            self.failed = True
            raise
        return written

    def flush(self):
        q.require(not self.failed, 'public_output_unavailable')
        try:
            self.stream.flush()
        except BaseException:
            self.failed = True
            raise


def retain_private_error(error, root):
    try:
        q.safe_exception(error, root)
    except BaseException:
        pass


def _run(argv, public):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observer', type=Path)
    parser.add_argument('--seed', type=Path)
    parser.add_argument('--job-start-epoch', type=float)
    args = parser.parse_args(argv)
    environment, start = dict(os.environ), time.monotonic()
    session = root = hard = None
    complete = clean = False
    progress = {'phase': 'preflight', 'source_integrity_verified': False, 'output_contract_verified': False,
                'receipt_verified': False}
    failure = None
    try:
        authorize_route(os.name, platform.python_version(), environment)
        q.require(args.observer is not None and args.seed is not None, 'arguments_missing')
        deadline, hard = budget_deadlines(args.job_start_epoch, time.time(), start)
        q.environment_preflight()
        observer, seed = args.observer.resolve(), args.seed.resolve()
        q.require(observer != seed and observer not in seed.parents and seed not in observer.parents, 'checkout_overlap')
        q.corpus_preflight((observer, seed))
        temp = Path(tempfile.gettempdir()).resolve()
        q.require(all(not temp.is_relative_to(repo) for repo in (observer, seed)), 'temp_inside_checkout')
        identity = maintainer.environment_identity()
        maintainer.validate_environment(identity)
        progress['environment_sha256'] = q.digest(json.dumps(identity, sort_keys=True).encode())
        root = Path(tempfile.mkdtemp(prefix='reader-attribution-owner-', dir=temp))
        session = make_session(root, deadline, hard)
        q.emit('reader_environment', **identity)
        execute(session, observer, seed, args.job_start_epoch, progress, environment)
        q.require(dict(os.environ) == environment and time.monotonic() < deadline, 'environment_or_budget_changed')
        complete = True
    except BaseException as error:
        failure = 'observer_or_evidence_failure'
        retain_private_error(error, root)
    finally:
        cleanup_start = time.monotonic()
        if session is not None:
            try:
                clean = session.cleanup() is True
            except BaseException:
                clean = False
        within = hard is not None and time.monotonic() < hard
        passed = complete and clean and within
        original = progress.get('class_record', {})
        status = 'complete' if passed else ('failed' if original.get('tests_run') and
                  not original.get('observer_failure') and (original.get('failures') or original.get('errors')) else 'inconclusive')
        summary = {key: value for key, value in progress.items() if key not in ('class_record', 'class_summary')}
        try:
            if 'class_summary' in progress:
                progress['class_summary']['attribution_complete'] = passed
                if not passed:
                    progress['class_summary']['top_children'] = []
                    progress['class_summary']['module_totals'] = []
                q.emit('reader_class_observation', **progress['class_summary'])
        except BaseException as error:
            passed, status = False, 'inconclusive'
            failure = failure or 'terminal_publication_failed'
            retain_private_error(error, root)
        public.terminal = True
        within = hard is not None and time.monotonic() < hard
        passed = passed and within
        if not within:
            status = 'inconclusive'
            failure = failure or 'hard_budget_exhausted'
        try:
            q.emit('reader_attribution_summary', **summary, status=status, failure=failure,
                   source_sha=SOURCE_SHA, candidate_sha256=q.CANDIDATE_HASH,
                   observer_sha=environment.get('GITHUB_SHA') if re.fullmatch(r'[0-9a-f]{40}', environment.get('GITHUB_SHA', '')) else None,
                   run_id=environment.get('GITHUB_RUN_ID') if re.fullmatch(r'[0-9]{1,20}', environment.get('GITHUB_RUN_ID', '')) else None,
                   process_cleanup_verified=clean, hard_budget_verified=within,
                   observer_seconds=time.monotonic() - start, cleanup_seconds=time.monotonic() - cleanup_start,
                   full_suite_execution=False, performance_qualified=False, adoption_authorized=False,
                   automatic_rerun=False, private_raw_evidence_uploaded=False, runner_teardown_proved=False)
        except BaseException as error:
            passed = False
            retain_private_error(error, root)
    # Publishing the last record consumes the same fixed whole-job budget.
    # A late/failed publication is not retried or credited as success.
    return 0 if passed and hard is not None and time.monotonic() < hard else 2


def main(argv=None):
    public = PublicOutput(sys.stdout)
    with contextlib.redirect_stdout(public):
        return _run(argv, public)


if __name__ == '__main__':
    raise SystemExit(main())
