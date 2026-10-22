#!/usr/bin/env python3
"""One fixed-source serial-first cap-1/cap-2 screen, not adoption or a full suite."""
import argparse
import contextlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import sys
import tempfile
import time
import unittest

import measure_lazy_suite_ids as q
import measure_maintainer_pair as maintainer
import measure_reader_attribution as reader
import measure_threshold_module as threshold
import diagnose_checkpoint_discovery as checkpoint
import generated_output_contract as contract
from diagnostic_observations import unique_json
from parallel_reader_scheduler import run_schedule, account_pairs, audit_sets, Observation, LOOKUPS
from compact_parallel_consumers import CompactCommands

SOURCE_SHA = '08db6360b453c2bf969a686f62f0477184d06351'
OBSERVER_BASE = '05434f875f7e1af570335cff3f324d15e65c0fe7'
PAIR_MANIFEST = '56fd330f6aed1517b76a6d359365ebf9a4ffa3deb0bb4db67ce220c4db0aadb2'
PAYLOAD_HASH = '83ffec3f4a7700d6d382c3c773a2b08ad88b2b075b39b5b919941b7072abd9d9'
REFERENCE_HASH = '99f5a09a831d7fe7383df2c28658039ba2033e577a87710679a352841b8aa56e'
GIB = 1024 ** 3
BUDGET = {'job_seconds': 5400, 'cleanup_seconds': 300, 'shared_setup_seconds': 600,
          'cap1_preparation_seconds': 480, 'cap2_preparation_seconds': 120,
          'arm_seconds': 2100, 'final_verification_seconds': 300,
          'max_capture_bytes': 16 * 1024 ** 2, 'max_receipt_bytes': 4 * 1024 ** 2,
          'minimum_free_bytes': GIB, 'owned_control_command_slots': 1600,
          'inner_control_capture_slots': 18, 'clone_size_estimate_multiplier': 2,
          'compact_pair_slots': 2184, 'compact_receipts_per_pair': 3,
          'max_compact_receipt_bytes': 16384, 'compact_pending_helper_pairs': 32,
          'compact_measured_window': 2,
          'retained_redirected_stream_slots': 4,
          'auxiliary_evidence_reserve_bytes': 128 * 1024 ** 2,
          'temporary_growth_reserve_bytes': 4 * GIB, 'generated_growth_reserve_bytes': 4 * GIB}


def budget_deadlines(origin, wall_now, monotonic_now):
    q.require(all(type(value) in (int, float) and math.isfinite(value)
                  for value in (origin, wall_now, monotonic_now)), 'setup_clock_invalid')
    elapsed = wall_now - origin
    q.require(0 <= elapsed < 5100, 'setup_budget_exhausted')
    hard = monotonic_now + 5400 - elapsed
    return hard - 300, hard


def admit_block(hard, now, block):
    reserves = {'cap1': 4920, 'cap2_prepare': 2820, 'cap2': 2700, 'final': 600}
    q.require(block in reserves and all(reader.metric(value) is not None for value in (hard, now)),
              'parallel_budget_invalid')
    remaining = hard - now - reserves[block]
    q.require(remaining >= 0, 'parallel_admission_exhausted')
    return remaining


def disk_requirements(unstarted, live_bytes, commands, future_clones, clone_basis, same_volume, *, inner_pairs=18):
    """Qualifying capture maxima plus explicitly estimated growth, not a write quota."""
    limits = ((unstarted, 584), (live_bytes, 64 * 1024 ** 2),
              (commands, BUDGET['owned_control_command_slots']), (future_clones, 4),
              (clone_basis, 1024 * GIB), (inner_pairs, 18))
    q.require(all(type(value) is int and 0 <= value <= cap for value, cap in limits)
              and type(same_volume) is bool, 'parallel_disk_plan_invalid')
    pair = 2 * BUDGET['max_capture_bytes']
    evidence = (GIB + (unstarted + commands + inner_pairs) * pair
                + live_bytes + BUDGET['temporary_growth_reserve_bytes']
                + BUDGET['auxiliary_evidence_reserve_bytes'])
    clones = GIB + future_clones * clone_basis * 2 + BUDGET['generated_growth_reserve_bytes']
    return {'evidence': evidence + clones - GIB if same_volume else evidence,
            'clones': 0 if same_volume else clones}


def compact_disk_requirements(measured_bytes, inner_pairs, helper_bytes, receipt_bytes,
                              future_clones, clone_basis, same_volume):
    """Rolling logical allowances plus estimates; never credit expected reclamation."""
    mib = 1024 ** 2
    limits = ((measured_bytes, BUDGET['compact_measured_window'] * 32 * mib),
              (inner_pairs, BUDGET['inner_control_capture_slots']),
              (helper_bytes, BUDGET['compact_pending_helper_pairs'] * 32 * mib),
              (receipt_bytes, BUDGET['compact_pair_slots'] * BUDGET['compact_receipts_per_pair']
                             * BUDGET['max_compact_receipt_bytes']),
              (future_clones, 4), (clone_basis, 1024 * GIB))
    q.require(all(type(value) is int and 0 <= value <= cap for value, cap in limits)
              and type(same_volume) is bool, 'parallel_disk_plan_invalid')
    # The single helper window includes planted pairs and every nested guard.
    evidence = (GIB + measured_bytes + inner_pairs * 32 * mib + helper_bytes
                + BUDGET['retained_redirected_stream_slots'] * BUDGET['max_capture_bytes']
                + BUDGET['temporary_growth_reserve_bytes']
                + BUDGET['auxiliary_evidence_reserve_bytes'] + receipt_bytes)
    clones = GIB + future_clones * clone_basis * 2 + BUDGET['generated_growth_reserve_bytes']
    return {'evidence': evidence + clones - GIB if same_volume else evidence,
            'clones': 0 if same_volume else clones}


def compact_admission_policy():
    # Audited successful call graph; this is necessary eligibility, not a
    # seed-ref assumption or a promise that storage/time admission will pass.
    maximum_refs = BUDGET['compact_pending_helper_pairs'] - 11 - 8
    return {'pending_helper_pairs': BUDGET['compact_pending_helper_pairs'],
            'clone_context_fixed_calls': 11, 'trailing_guard_peak_calls': 8,
            'maximum_deleted_refs_per_clone': maximum_refs,
            'maximum_successful_helper_calls': 1294 + 4 * maximum_refs,
            'seed_ref_count_assumed': False,
            'undisposed_measured_pairs_including_failures': 2}


def consumer_scope(session, name):
    return session.consumer_scope(name) if getattr(session, 'compact', None) is not None else contextlib.nullcontext(None)


def acknowledge_controls(session, scope, phase, planted=None):
    """Only called after the original validator, original assertions and trailing guard."""
    if scope is None: return
    records = scope.records
    if phase in ('clone', 'source_guard'):
        q.require(not records, 'compact_consumer_shape_changed')
        session.complete_consumer(scope, [])
        return
    if phase == 'source_clone':
        q.require(len(records) == 1, 'compact_consumer_shape_changed')
        record = records[0]; argv = record['argv']
        q.require(len(argv) == 9 and argv[:7] == ('git', '-c', 'core.autocrlf=false', 'clone',
                  '--no-local', '--no-hardlinks', '--no-checkout')
                  and record['result']['returncode'] == 0, 'compact_consumer_shape_changed')
        session.complete_consumer(scope, [(record, 'helper_result', session.helper_evidence(record))])
        return
    if phase in ('contract', 'pair_explicit'):
        q.require(len(records) == (1 if phase == 'contract' else 1 + len(q.SYNTHETIC_SELECTORS)),
                  'compact_consumer_shape_changed')
        acknowledgments = []
        for index, record in enumerate(records):
            argv = record['argv']
            if phase == 'contract':
                valid = (len(argv) == 3 and argv[0] == sys.executable
                    and Path(argv[1]).name == 'diagnose_generated_outputs.py' and argv[2] == '--contract-child')
                count = reader.generated.CONTRACT_CONTROL_COUNT
            elif index == 0:
                valid = (len(argv) == 6 and argv[:2] == (sys.executable, '-c')
                    and q.digest(argv[2].encode()) == PAYLOAD_HASH and argv[-2:] == (q.JUNCTION, q.LOOKUPS[0]))
                count = 1
            else:
                valid = argv == (sys.executable, '-m', 'unittest', q.SYNTHETIC_SELECTORS[index - 1])
                count = 1
            q.require(valid, 'compact_consumer_shape_changed')
            evidence = session.helper_evidence(record)
            evidence['result']['semantic_result'] = q.verify_probe(record['result'], count, q.LOOKUPS[0])
            acknowledgments.append((record, 'helper_result', evidence))
        session.complete_consumer(scope, acknowledgments)
        return
    if phase == 'planted':
        q.require(type(planted) is dict and planted['complete'] is True
                  and 0 < len(records) == len(planted['pairs']) <= 22, 'compact_consumer_shape_changed')
        acknowledgments = []
        for record, row in zip(records, planted['pairs']):
            argv = record['argv']
            q.require(len(argv) == 6 and argv[:2] == (sys.executable, '-c')
                      and q.digest(argv[2].encode()) == PAYLOAD_HASH and argv[-1] in LOOKUPS
                      and row['pair_token'] == reader.token(['planted', *argv[-2:]]),
                      'compact_consumer_shape_changed')
            # Exact original row stays unchanged. The extra compact-only flag is
            # justified by the session's authenticated original owner binding.
            acknowledgments.append((record, 'planted_method', {'completed': True, 'validated': True,
                'original_success': True, 'result': {**row, 'root_identity_verified': True}}))
        session.complete_consumer(scope, acknowledgments)
        return
    if phase in ('native', 'dual_native', 'retained', 'pair_behavior', 'temp'):
        expected = {'native': ('windows_job_probe_controls.py',),
                    'dual_native': ('current_parallel_native_controls.py',),
                    'retained': ('staging_retained_controls.py',),
                    'pair_behavior': ('suite_id_lazy_controls.py',),
                    'temp': ('measure_lazy_suite_ids.py', '-c')}[phase]
        q.require(len(records) == len(expected), 'compact_consumer_shape_changed')
        acknowledgments = []
        for record, script in zip(records, expected):
            argv = record['argv']
            q.require(len(argv) >= 3 and argv[0] == sys.executable
                      and (argv[1] == '-c' if script == '-c' else Path(argv[1]).name == script)
                      and record['result']['returncode'] == 0, 'compact_consumer_shape_changed')
            acknowledgments.append((record, 'outer_control', {'completed': True, 'validated': True,
                'original_success': True, 'result': unique_json(record['reads'][0][0])}))
        session.complete_consumer(scope, acknowledgments)
        return
    q.require(phase == 'detached' and len(records) == 1, 'compact_consumer_shape_changed')
    record = records[0]
    q.require(record['argv'] == ('git', '-C', str(record['cwd']), 'symbolic-ref', '-q', 'HEAD')
              and record['result']['returncode'] == 1 and not record['result']['stdout'],
              'compact_consumer_shape_changed')
    session.complete_consumer(scope, [(record, 'helper_result', session.helper_evidence(record, 'detached_head'))])


def observe_planted(check, cls, repository, manifests, session, guard, payload):
    """The actual original first TestCase method, with its assertions and lifecycle."""
    q.require(tuple(unittest.TestLoader().getTestCaseNames(cls)) == reader.METHODS, 'audit_methods_changed')
    adapter = reader.ReaderAdapter(check, repository, manifests, session, payload)
    class Result(unittest.TestResult):
        def addError(self, test, error):
            adapter.note_failure(error[1]); super().addError(test, error)
        def addFailure(self, test, error):
            adapter.note_failure(error[1]); super().addFailure(test, error)
        def stopTest(self, test):
            super().stopTest(test)
            adapter.stage = 'class_guard'
            try: guard()
            except BaseException as error:
                adapter.note_failure(error); raise
    result = Result()
    old_loop, old_subprocess = check._readers_under_refusal, check.subprocess
    adapter.original_readers = old_loop
    started = time.monotonic()
    try:
        check._readers_under_refusal, check.subprocess = adapter.readers, adapter
        with (session.root / 'planted-stdout.private').open('xb') as stdout, \
             (session.root / 'planted-stderr.private').open('xb') as stderr:
            with contextlib.redirect_stdout(reader.PrivateWriter(stdout, session.deadline)), \
                 contextlib.redirect_stderr(reader.PrivateWriter(stderr, session.deadline)):
                unittest.TestSuite([cls(reader.METHODS[0])]).run(result)
    except BaseException as error:
        adapter.failure = 'observer_failure'; adapter.note_failure(error)
        reader.retain_private_error(error, session.root)
    finally:
        check._readers_under_refusal, check.subprocess = old_loop, old_subprocess
    reader.encode_pairs(adapter.rows, manifests)
    complete = (result.testsRun == 1 and result.wasSuccessful() and not result.skipped
                and not result.expectedFailures and not result.unexpectedSuccesses
                and adapter.failure is None and adapter.invocations == ['planted']
                and len(adapter.rows) == 2 * len(manifests['planted']['modules'])
                and all(row['completion'] == 'completed' and row['screen_clean'] for row in adapter.rows))
    return {'method_token': reader.token([reader.CLASS_ID, reader.METHODS[0]]),
            'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
            'complete': complete, 'pairs': adapter.rows, 'wall_seconds': time.monotonic() - started,
            'failure_context': adapter.failure_context}


SIGNATURE_KEYS = ('module', 'lookup', 'returncode', 'classification', 'test_count', 'failures',
                  'errors', 'skipped', 'expected_failures', 'screen_clean', 'capture_read_verified', 'cleanup_verified')
OWNER_RESULT_FIELDS = frozenset(('root_identity_verified', 'root_reaped', 'active_processes', 'total_processes',
                                'cleanup_verified', 'returncode', 'owned_wall_seconds', 'tree_cpu_seconds'))
SNAPSHOT_FIELDS = frozenset(('pair_token', 'completion', 'classification')) | OWNER_RESULT_FIELDS


def signatures(rows):
    return [{key: row[key] for key in SIGNATURE_KEYS} for row in rows]


def encode_arm(record, modules):
    """Exact finite receipt; concurrent observations need not be a serial prefix."""
    from current_parallel_runner import LEDGER_KEYS
    refuse = 'parallel_receipt_invalid'
    keys = {'arm', 'cap', 'manifest_sha256', 'expected_pairs', 'attempt_order', 'observations',
            'scheduler_observations', 'missing', 'unstarted', 'unread', 'first_error',
            'first_error_resolved', 'stop_reason', 'schedule_complete', 'complete',
            'cleanup_verified', 'source_integrity_verified', 'output_contract_verified',
            'work_equivalent', 'qualified', 'schedule_wall_seconds', 'owned_wall_seconds', 'tree_cpu_seconds', 'pin_sets'}
    q.require(type(record) is dict and set(record) == keys and modules == tuple(sorted(set(modules)))
              and 0 < len(modules) <= 10000, refuse)
    pairs = [(module, lookup) for module in modules for lookup in LOOKUPS]
    tokens = [reader.token(['repository', *pair]) for pair in pairs]
    q.require(record['arm'] in ('cap1', 'cap2') and type(record['cap']) is int
              and record['cap'] == int(record['arm'][-1])
              and record['manifest_sha256'] == reader.token([['repository', *pair] for pair in pairs])
              and type(record['expected_pairs']) is int and record['expected_pairs'] == len(pairs), refuse)
    flags = ('first_error_resolved', 'schedule_complete', 'complete', 'cleanup_verified',
             'source_integrity_verified', 'output_contract_verified', 'work_equivalent', 'qualified')
    q.require(all(type(record[key]) is bool for key in flags), refuse)
    rows = record['observations']
    q.require(type(rows) is list and len(rows) <= len(pairs), refuse)
    seen, indices, ordinals, roots, manifests, interpreters = set(), [], [], {}, set(), set()
    for row in rows:
        q.require(type(row) is dict and set(row) == LEDGER_KEYS, refuse)
        index = row['pair_index']
        q.require(type(index) is int and 0 <= index < len(pairs)
                  and (row['module'], row['lookup']) == pairs[index]
                  and row['pair_token'] == tokens[index] and index not in seen
                  and type(row['module_index']) is int and row['module_index'] == index // 2
                  and type(row['lane']) is int and row['lane'] == (index // 2) % 2
                  and row['arm'] == record['arm'], refuse)
        seen.add(index); indices.append(index)
        q.require(type(row['command_ordinal']) is int and 1 <= row['command_ordinal'] <= len(pairs), refuse)
        ordinals.append(row['command_ordinal'])
        q.require(row['source_sha'] == SOURCE_SHA and row['candidate_sha256'] == q.CANDIDATE_HASH
                  and row['payload_sha256'] == PAYLOAD_HASH, refuse)
        for key in ('source_manifest_sha256', 'interpreter_sha256', 'clone_root_token'):
            q.require(type(row[key]) is str and re.fullmatch(r'[0-9a-f]{64}', row[key]), refuse)
        manifests.add(row['source_manifest_sha256']); interpreters.add(row['interpreter_sha256'])
        q.require(roots.setdefault(row['lane'], row['clone_root_token']) == row['clone_root_token'], refuse)
        q.require(row['completion'] in ('completed', 'incomplete')
                  and row['classification'] in ('reader', 'nonreader', 'error', 'unread')
                  and row['reason'] in ('completed', 'launch_incomplete', 'cancelled', 'cleanup_unverified', 'capture_unread'), refuse)
        for key in ('root_identity_verified', 'cleanup_verified', 'root_reaped', 'screen_clean', 'capture_read_verified'):
            q.require(type(row[key]) is bool, refuse)
        for key in ('total_processes', 'active_processes', 'test_count', 'failures', 'errors', 'skipped', 'expected_failures'):
            q.require(row[key] is None or type(row[key]) is int and 0 <= row[key] <= 1000000, refuse)
        for key in ('call_wall_seconds', 'owned_wall_seconds', 'tree_cpu_seconds', 'analysis_seconds'):
            q.require(row[key] is None or reader.metric(row[key]) is not None and row[key] <= 5400 * 1024, refuse)
        for key in ('stdout_bytes', 'stderr_bytes'):
            q.require(row[key] is None or type(row[key]) is int and 0 <= row[key] <= BUDGET['max_capture_bytes'], refuse)
        for key in ('stdout_sha256', 'stderr_sha256'):
            q.require(row[key] is None or type(row[key]) is str and re.fullmatch(r'[0-9a-f]{64}', row[key]), refuse)
        q.require(row['returncode'] is None or type(row['returncode']) is int and -(2 ** 31) <= row['returncode'] < 2 ** 32, refuse)
        if row['completion'] == 'completed':
            q.require(row['reason'] == 'completed' and row['capture_read_verified']
                      and all(row[key] is not None for key in ('call_wall_seconds', 'analysis_seconds',
                          'stdout_bytes', 'stderr_bytes', 'stdout_sha256', 'stderr_sha256')), refuse)
            if row['cleanup_verified']:
                q.require(row['root_identity_verified'] and row['root_reaped'] and row['active_processes'] == 0
                          and all(row[key] is not None for key in ('returncode', 'owned_wall_seconds', 'tree_cpu_seconds')), refuse)
    q.require(indices == sorted(indices) and sorted(ordinals) == list(range(1, len(rows) + 1))
              and len(manifests) <= 1 and len(interpreters) <= 1
              and len(set(roots.values())) == len(roots), refuse)
    order = [row['pair_token'] for row in sorted(rows, key=lambda row: row['command_ordinal'])]
    absent = [token for index, token in enumerate(tokens) if index not in seen]
    unread = [token for index, token in enumerate(tokens) if index not in seen or
              any(row['pair_index'] == index and (row['completion'] != 'completed' or not row['cleanup_verified']) for row in rows)]
    q.require(record['attempt_order'] == order and record['missing'] == record['unstarted'] == absent
              and record['unread'] == unread, refuse)
    snapshots = record['scheduler_observations']
    q.require(type(snapshots) is list and len(snapshots) <= len(rows), refuse)
    by_token = {row['pair_token']: row for row in rows}; snapshot_tokens = []
    for item in snapshots:
        q.require(type(item) is dict and set(item) == SNAPSHOT_FIELDS, refuse)
        q.require(item['pair_token'] in by_token and all(type(item[key]) is bool for key in
                  ('cleanup_verified', 'root_identity_verified', 'root_reaped')), refuse)
        for key in ('active_processes', 'total_processes'):
            q.require(item[key] is None or type(item[key]) is int and 0 <= item[key] <= 1000000, refuse)
        q.require(item['returncode'] is None or type(item['returncode']) is int and -(2 ** 31) <= item['returncode'] < 2 ** 32, refuse)
        for key in ('owned_wall_seconds', 'tree_cpu_seconds'):
            q.require(item[key] is None or reader.metric(item[key]) is not None and item[key] <= 5400 * 1024, refuse)
        row = by_token[item['pair_token']]
        q.require(item['completion'] == row['completion'] and item['classification'] == row['classification'], refuse)
        if item['completion'] == 'completed':
            q.require(item['cleanup_verified'] and item['root_identity_verified'] and item['root_reaped']
                      and item['active_processes'] == 0
                      and all(item[key] is not None for key in ('returncode', 'owned_wall_seconds', 'tree_cpu_seconds')), refuse)
            if row['cleanup_verified']:
                q.require(all(item[key] == row[key] for key in OWNER_RESULT_FIELDS), refuse)
        snapshot_tokens.append(item['pair_token'])
    q.require(len(set(snapshot_tokens)) == len(snapshot_tokens)
              and snapshot_tokens == sorted(snapshot_tokens, key=tokens.index), refuse)
    q.require(record['first_error'] is None or record['first_error'] in by_token,
              refuse)
    q.require(not record['first_error_resolved'] or record['first_error'] is not None, refuse)
    q.require(record['stop_reason'] in (None, 'whole_job_measurement_budget_exhausted',
                  'scheduler_or_runner_exception', 'cleanup_unverified', 'unexpected_probe_result'), refuse)
    pins = record['pin_sets']
    q.require(pins is None or type(pins) is dict and set(pins) == {'unpinned_readers', 'stale_pins', 'verified'}, refuse)
    if pins is not None:
        for key in ('unpinned_readers', 'stale_pins'):
            q.require(type(pins[key]) is list and len(pins[key]) <= 20000 and all(type(value) is str
                      and re.fullmatch(r'[0-9a-f]{64}', value) for value in pins[key])
                      and pins[key] == sorted(set(pins[key])), refuse)
        q.require(set(pins['unpinned_readers']) <= set(tokens) and type(pins['verified']) is bool
                  and pins['verified'] == (not pins['unpinned_readers'] and not pins['stale_pins']), refuse)
    complete = (record['schedule_complete'] and record['stop_reason'] is None and not absent and not unread
                and len(snapshots) == len(rows) and record['cleanup_verified']
                and all(row['screen_clean'] and row['classification'] in ('reader', 'nonreader') for row in rows))
    q.require(record['complete'] == complete and record['qualified'] ==
              (complete and pins is not None and pins['verified'] and record['source_integrity_verified']
               and record['output_contract_verified'] and record['work_equivalent']), refuse)
    for key in ('schedule_wall_seconds', 'owned_wall_seconds', 'tree_cpu_seconds'):
        q.require(record[key] is None or reader.metric(record[key]) is not None and record[key] <= 5400 * 1024, refuse)
    for total, key in (('owned_wall_seconds', 'owned_wall_seconds'), ('tree_cpu_seconds', 'tree_cpu_seconds')):
        values = [row[key] for row in rows]
        q.require(record[total] == (sum(values) if all(value is not None for value in values) else None), refuse)
    raw = json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    q.require(len(raw) <= BUDGET['max_receipt_bytes'], 'parallel_receipt_limit')
    return raw


def arm_record(arm, modules, pins, ledger, schedule, elapsed, cleanup):
    rows = sorted((dict(row) for row in ledger), key=lambda row: row['pair_index'])
    by_pair = {(row['module'], row['lookup']): row for row in rows}
    observed = []
    for item in schedule.observations:
        row = by_pair.get((item.module, item.lookup))
        q.require(row is not None and item.classification == row['classification'], 'parallel_receipt_invalid')
        if row['completion'] == 'completed':
            changes = {key for key in row if item.metadata.get(key) != row[key]}
            q.require(not changes or row['cleanup_verified'] is False and changes <= OWNER_RESULT_FIELDS,
                      'parallel_receipt_invalid')
        else:
            q.require(all(item.metadata.get(key) == row[key] for key in
                ('pair_token', 'command_ordinal', 'module', 'lookup', 'completion', 'classification')), 'parallel_receipt_invalid')
        observed.append({key: item.metadata[key] for key in SNAPSHOT_FIELDS})
    pairs = [(module, lookup) for module in modules for lookup in LOOKUPS]
    tokens = [reader.token(['repository', *pair]) for pair in pairs]
    unstarted = [tokens[index] for index, pair in enumerate(pairs) if pair not in by_pair]
    unread = [tokens[index] for index, pair in enumerate(pairs) if pair not in by_pair or
              by_pair[pair]['completion'] != 'completed' or not by_pair[pair]['cleanup_verified']]
    complete = (schedule.complete and cleanup and not unread and all(row['screen_clean'] for row in rows))
    pin_sets = None
    if schedule.complete and len(schedule.observations) == len(pairs) and all(row['screen_clean'] for row in rows):
        sets = audit_sets(modules, pins, schedule.observations)
        pin_sets = {key: sorted(reader.token(['repository', *pair]) for pair in sets[key])
                    for key in ('unpinned_readers', 'stale_pins')}
        pin_sets['verified'] = not pin_sets['unpinned_readers'] and not pin_sets['stale_pins']
    record = {'arm': arm, 'cap': int(arm[-1]), 'manifest_sha256': reader.token([['repository', *pair] for pair in pairs]),
              'expected_pairs': len(pairs), 'attempt_order': [row['pair_token'] for row in ledger],
              'observations': rows, 'scheduler_observations': observed,
              'missing': unstarted, 'unstarted': unstarted, 'unread': unread,
              'first_error': reader.token(['repository', *schedule.first_error]) if schedule.first_error else None,
              'first_error_resolved': schedule.first_error_resolved, 'stop_reason': schedule.stop_reason,
              'schedule_complete': schedule.complete, 'complete': complete, 'cleanup_verified': cleanup,
              'source_integrity_verified': False, 'output_contract_verified': False, 'work_equivalent': False,
              'qualified': False, 'pin_sets': pin_sets, 'schedule_wall_seconds': elapsed,
              'owned_wall_seconds': sum(row['owned_wall_seconds'] for row in rows) if all(row['owned_wall_seconds'] is not None for row in rows) else None,
              'tree_cpu_seconds': sum(row['tree_cpu_seconds'] for row in rows) if all(row['tree_cpu_seconds'] is not None for row in rows) else None}
    encode_arm(record, modules)
    return record


def tree_size(root, deadline):
    """Logical bytes including full Git history; explicitly not physical peak storage."""
    total = count = 0
    def unread(error):
        raise q.Refused('parallel_storage_inventory_unread') from None
    for parent, directories, files in os.walk(root, followlinks=False, onerror=unread):
        for name in [*directories, *files]:
            q.require(time.monotonic() < deadline, 'global_budget_exhausted')
            path = Path(parent) / name
            meta = path.lstat()
            q.require(not stat.S_ISLNK(meta.st_mode) and not getattr(meta, 'st_file_attributes', 0) & 0x400,
                      'parallel_storage_unsafe')
            if name in files:
                q.require(stat.S_ISREG(meta.st_mode) and meta.st_nlink == 1, 'parallel_storage_unsafe')
                total += meta.st_size; count += 1
                q.require(count <= 100000 and total <= 1024 * GIB, 'parallel_storage_inventory_limit')
    return total


class ResourcePlan:
    def __init__(self, session, seed, clone_parent):
        self.session, self.clone_parent = session, clone_parent
        self.roots = (session.root, clone_parent)
        self.identities = tuple(self.identity(path) for path in self.roots)
        self.clone_basis = tree_size(seed, session.deadline)
        self.future_clones, self.runners, self.inner_pairs = 4, session.runners, 18
    @staticmethod
    def identity(path):
        maintainer.safe_directory(path)
        meta = path.lstat()
        return meta.st_dev, meta.st_ino
    def required(self):
        unstarted = 584 - sum(len(runner.attempt_ledger()) for runner in self.runners)
        pending = sum(runner.pending_capture_bytes() for runner in self.runners)
        if getattr(self.session, 'compact', None) is not None:
            occupied = sum(runner.pending_capture_slots for runner in self.runners)
            measured = pending + min(unstarted, max(0, 2 - occupied)) * 2 * BUDGET['max_capture_bytes']
            helpers = (self.session.pending_helper_capacity_bytes
                + (BUDGET['compact_pending_helper_pairs'] - self.session.pending_helper_pairs)
                * 2 * BUDGET['max_capture_bytes'])
            return compact_disk_requirements(measured, self.inner_pairs, helpers,
                self.session.compact.remaining_receipt_bytes, self.future_clones, self.clone_basis,
                self.identities[0][0] == self.identities[1][0])
        commands = BUDGET['owned_control_command_slots'] - self.session.command_attempts
        commands += int(self.session.command_active)
        return disk_requirements(unstarted, pending, commands, self.future_clones, self.clone_basis,
                                 self.identities[0][0] == self.identities[1][0], inner_pairs=self.inner_pairs)
    def check(self):
        q.require(tuple(self.identity(path) for path in self.roots) == self.identities,
                  'parallel_storage_identity_changed')
        required = self.required()
        for name, path in zip(('evidence', 'clones'), self.roots):
            q.require(shutil.disk_usage(path).free >= required[name], 'parallel_disk_admission_exhausted')
        return required
    def cloned(self, repo):
        self.clone_basis = max(self.clone_basis, tree_size(repo, self.session.deadline))
        self.future_clones -= 1
        return self.check()


class ComparisonSession(CompactCommands, checkpoint.CheckpointSession):
    """A finite retained helper-command count around the unchanged serial owner seam."""
    def __init__(self, root, deadline, hard, *, compact=None, snapshot_reader=None):
        super().__init__(root, deadline, hard)
        if compact is True:
            from compact_capture_retention import CompactStore
            compact = CompactStore(root, deadline)
        self.init_compact(compact, snapshot_reader)
        self.compact_bindings = {'source_sha': SOURCE_SHA, 'candidate_sha256': q.CANDIDATE_HASH,
            'payload_sha256': PAYLOAD_HASH, 'interpreter_sha256': q.digest(Path(sys.executable).read_bytes())}
        self.command_attempts, self.command_active = 0, False
        self.runners = []
        self.resource_check = lambda: None
    def _check_resources(self):
        self.resource_check()
    def run(self, argv, cwd):
        q.require(all(runner.is_quiescent for runner in self.runners), 'parallel_guard_while_live')
        q.require(self.command_attempts < BUDGET['owned_control_command_slots'], 'parallel_control_slots_exhausted')
        self.resource_check()
        ticket = self.reserve_command(argv, cwd)
        self.command_attempts += 1; self.command_active = True
        try: result = self.register_command(ticket, super().run(argv, cwd))
        except BaseException as error:
            self._compact_stop(error)
            raise
        finally: self.command_active = False
        self.resource_check()
        return result
    def cleanup(self):
        clean = True
        for runner in self.runners:
            try: clean = runner.cleanup() is True and clean
            except BaseException: clean = False
        return super().cleanup() is True and clean


def prepare_arm(session, seed, root, arm, expected, candidate, progress, clones, guard, resources):
    q.require(arm == 'cap1' or arm == 'cap2' and progress['arms'].get('cap1', {}).get('qualified') is True
              and progress['arm_receipts'].get('cap1') is True, 'parallel_baseline_not_qualified')
    target_expected = {**expected, q.SUITE_PATH: q.CANDIDATE_HASH}
    q.require(expected.get(q.SUITE_PATH) == q.ORIGINAL_HASH
              and expected.get(threshold.MODULE_PATH) == threshold.BASELINE_HASH, 'parallel_source_delta_changed')
    lanes = []
    for lane in range(2):
        guard(); resources.check()
        repo = root / ('%s-lane%d' % (arm, lane))
        with consumer_scope(session, 'source_clone') as scope:
            target = maintainer.source_context(session, seed, repo, 'candidate', expected, candidate, source_sha=SOURCE_SHA)
            q.require(target == target_expected, 'parallel_source_delta_changed')
            clones.append((repo, target)); lanes.append(repo)
            resources.cloned(repo); guard()
            acknowledge_controls(session, scope, 'source_clone')
    return tuple(lanes)


def reference_rows(raw, modules):
    q.require(type(raw) is bytes and q.digest(raw) == REFERENCE_HASH, 'parallel_reference_changed')
    reference = unique_json(raw)
    rows = reference['pairs']
    q.require(reference['source_sha'] == SOURCE_SHA and reference['candidate_sha256'] == q.CANDIDATE_HASH
              and [(row['module'], row['lookup']) for row in rows] ==
              [(module, lookup) for module in modules for lookup in LOOKUPS], 'parallel_population_changed')
    return rows


def qualify_record(record, modules, reference):
    record.update(source_integrity_verified=True, output_contract_verified=True,
                  work_equivalent=signatures(record['observations']) == reference, qualified=False)
    record['qualified'] = (record['complete'] and record['work_equivalent']
                           and record['pin_sets'] is not None and record['pin_sets']['verified'])
    encode_arm(record, modules)
    q.require(record['qualified'], 'parallel_work_changed')


def retained_json(session, name, raw):
    q.require(type(raw) is bytes and len(raw) <= BUDGET['max_receipt_bytes'], 'parallel_receipt_limit')
    path = session.root / name
    with path.open('xb') as stream: stream.write(raw)
    readback = contract.safe_read(session.root, name, BUDGET['max_receipt_bytes'], session.deadline)
    q.require(readback == raw and unique_json(readback) == unique_json(raw), 'parallel_receipt_invalid')
    return {'receipt_sha256': q.digest(raw), 'receipt_bytes': len(raw), 'receipt_verified': True}


def measure_arm(session, lanes, arm, manifest, target, payload, reference, progress, guard, resources, environment):
    from current_parallel_runner import CurrentParallelRunner
    from parallel_reader_scheduler import ScheduleResult
    modules = manifest['modules']
    capture, temporary = session.root / (arm + '-captures'), session.root / (arm + '-temporary')
    capture.mkdir(); temporary.mkdir()
    guard()
    runner = CurrentParallelRunner(arm=arm, modules=modules, clones=lanes,
        capture_root=capture, temporary_root=temporary, payload=payload, source_sha=SOURCE_SHA,
        source_manifest_sha256=reader.token(target), candidate_sha256=q.CANDIDATE_HASH,
        interpreter_sha256=q.digest(Path(sys.executable).read_bytes()),
        deadline=session.deadline, hard_deadline=session.hard_deadline,
        environment=environment, resource_check=resources.check,
        compact=getattr(session, 'compact', None),
        compact_reference={(row['module'], row['lookup']): row for row in reference})
    session.runners.append(runner)
    schedule = ScheduleResult(False, (), (), None, False, 'scheduler_or_runner_exception', ())
    record = None; cleanup = False
    started = time.monotonic()
    try:
        schedule = run_schedule(modules, int(arm[-1]), runner, deadline=session.deadline,
                                clock=time.monotonic, sleep=time.sleep)
        cleanup = runner.cleanup() is True
        if not cleanup: note_failure(progress, q.Refused('parallel_cleanup_unverified'))
        elapsed = time.monotonic() - started
        record = arm_record(arm, modules, manifest['pinned'], runner.attempt_ledger(), schedule, elapsed, cleanup)
        progress['arms'][arm] = record
        if runner.first_failure is not None:
            progress.setdefault('first_observer_failure', runner.first_failure)
        q.require(cleanup, 'parallel_cleanup_unverified')
        q.require(all(owner.result is not None and owner.result.snapshot.cleanup_verified is True
                      for owner in session.owners), 'parallel_controls_unverified')
        q.require(record['complete'], 'parallel_arm_incomplete')
        q.require(record['pin_sets'] is not None and record['pin_sets']['verified'], 'parallel_pin_sets_changed')
        guard()
        qualify_record(record, modules, reference)
    except BaseException as error:
        note_failure(progress, error)
        raise
    finally:
        if record is None:
            cleanup = runner.cleanup() is True
            record = arm_record(arm, modules, manifest['pinned'], runner.attempt_ledger(), schedule,
                                time.monotonic() - started, cleanup)
            progress['arms'][arm] = record
        try:
            receipt = retained_json(session, arm + '-receipt.json', encode_arm(record, modules))
            progress['arm_receipts'][arm] = True
            if record['qualified']: guard()
            q.emit('parallel_arm', **record, **receipt)
        except BaseException as error:
            note_failure(progress, error)
            record['qualified'] = False
            raise
    return record


FAILURE_REASONS = reader.FAILURE_REASONS | frozenset(('parallel_budget_invalid', 'parallel_admission_exhausted',
    'parallel_disk_plan_invalid', 'parallel_disk_admission_exhausted', 'parallel_storage_identity_changed',
    'parallel_storage_unsafe', 'parallel_storage_inventory_limit', 'parallel_control_slots_exhausted',
    'parallel_baseline_not_qualified', 'parallel_source_delta_changed', 'parallel_reference_changed',
    'parallel_population_changed', 'parallel_work_changed', 'parallel_receipt_invalid', 'parallel_receipt_limit',
    'parallel_pin_sets_changed', 'parallel_native_controls_failed', 'parallel_arm_incomplete',
    'parallel_planted_incomplete', 'parallel_job_identity_missing', 'parallel_controls_unverified',
    'budget_contract_changed', 'public_receipt_limit_exceeded', 'public_output_unavailable',
    'setup_clock_invalid', 'setup_budget_exhausted', 'windows_python_pin_required', 'arguments_missing',
    'unauthorized_event_or_rerun', 'environment_or_budget_changed', 'global_budget_exhausted',
    'parallel_guard_while_live', 'source_refs_changed', 'observer_branch_scope_changed',
    'parallel_storage_inventory_unread', 'parallel_cleanup_unverified', 'compact_consumer_shape_changed',
    'compact_retirement_inconclusive', 'compact_consumer_unacknowledged', 'compact_helper_pending_limit',
    'compact_command_incomplete', 'compact_command_identity_changed', 'compact_consumer_invalid',
    'compact_invocation_incomplete', 'compact_helper_capacity_unread'))

OBSERVER_PATHS = {
    '.github/workflows/ci-threshold-module.yml', '.github/workflows/ci-current-parallel.yml',
    'diagnostics/measure_current_parallel.py', 'diagnostics/test_current_parallel.py',
    'diagnostics/current_parallel_runner.py', 'diagnostics/test_current_parallel_runner.py',
    'diagnostics/current_parallel_native_controls.py', 'diagnostics/test_current_parallel_native_controls.py',
    'diagnostics/current-parallel-budget.json', 'diagnostics/current-parallel-spec.md',
    'diagnostics/current-parallel-reference.json', 'diagnostics/measure_lazy_suite_ids.py',
    'diagnostics/generated_output_contract.py', 'diagnostics/diagnostic_observations.py',
    'diagnostics/compact_capture_native.py', 'diagnostics/test_compact_capture_native.py',
    'diagnostics/compact_capture_retention.py', 'diagnostics/test_compact_capture_retention.py',
    'diagnostics/compact_parallel_consumers.py', 'diagnostics/test_compact_parallel_consumers.py',
    'diagnostics/test_compact_parallel_integration.py'}


def execute(session, observer, seed, origin, progress, environment):
    """Quiescent source/control boundaries surrounding only the unchanged scheduler."""
    import current_parallel_native_controls as dual
    preparation = time.monotonic()
    admit_block(session.hard_deadline, time.monotonic(), 'cap1')
    resources = ResourcePlan(session, seed, seed.parent.parent)
    session.resource_check = resources.check
    progress['initial_disk_reserve'] = resources.check()
    progress['compact_admission_policy'] = compact_admission_policy()
    with consumer_scope(session, 'source_preflight') as scope:
        q.first_clean(session, observer, environment['GITHUB_SHA'], 'observer')
        session.git(observer, 'merge-base', '--is-ancestor', OBSERVER_BASE, 'HEAD')
        q.require(set(session.git(observer, 'diff', '--name-only', OBSERVER_BASE, 'HEAD').splitlines()) == OBSERVER_PATHS,
                  'observer_branch_scope_changed')
        q.first_clean(session, seed, SOURCE_SHA, 'seed')
        budget = unique_json(contract.safe_read(observer, 'diagnostics/current-parallel-budget.json', 16384, session.deadline))
        q.require(type(budget) is dict and budget == BUDGET
                  and all(type(budget[key]) is type(value) for key, value in BUDGET.items()), 'budget_contract_changed')
        snapshot = q.inventory(observer, deadline=session.deadline)
        expected = q.raw_source_inventory(session, seed, SOURCE_SHA)
        if getattr(session, 'compact', None) is not None:
            session.compact_bindings['source_manifest_sha256'] = reader.token(expected)
        q.require(expected.get(q.SUITE_PATH) == q.ORIGINAL_HASH
                  and expected.get(threshold.MODULE_PATH) == threshold.BASELINE_HASH, 'parallel_source_delta_changed')
        candidate = q.read_reviewed_bytes(observer / q.SUITE_PATH, q.CANDIDATE_HASH)
        payload = q.original_payload(seed)
        q.require(q.digest(payload.encode()) == PAYLOAD_HASH, 'payload_hash_mismatch')
        reference_raw = contract.safe_read(observer, 'diagnostics/current-parallel-reference.json', 1024 ** 2, session.deadline)
        refs = {repo: session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)') for repo in (observer, seed)}
        acknowledge_controls(session, scope, 'source_guard')
    clones = []
    def guard():
        q.require(all(runner.is_quiescent for runner in session.runners), 'parallel_guard_while_live')
        q.require(dict(os.environ) == environment and time.monotonic() < session.deadline, 'environment_or_budget_changed')
        state = contract.State(marker='absent', weights='absent', sessions='optional',
            job_start_epoch=origin, observed_epoch=time.time(), max_job_seconds=5400)
        for repo, target, pin in ((observer, snapshot, environment['GITHUB_SHA']), (seed, expected, SOURCE_SHA)):
            with consumer_scope(session, 'source_guard') as scope:
                q.verify_sources(session, repo, target, source_sha=pin)
                q.require(session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)') == refs[repo], 'source_refs_changed')
                contract.scan(repo, target, session.deadline, state)
                acknowledge_controls(session, scope, 'source_guard')
        for repo, target in clones:
            with consumer_scope(session, 'detached') as scope:
                maintainer.generated_guard(session, repo, target, True, state)
                acknowledge_controls(session, scope, 'detached')
        resources.check()
    def checked(phase, action):
        progress['phase'] = session.phase = phase
        started = time.monotonic()
        guard()
        with consumer_scope(session, phase) as scope:
            result = action(); guard()
            acknowledge_controls(session, scope, phase)
        q.emit('parallel_phase', phase=phase, wall_seconds=time.monotonic() - started,
               helper_commands_attempted=session.command_attempts)
        return result
    def native():
        result, raw = threshold.private_command(session, [sys.executable,
            str(observer / 'diagnostics/windows_job_probe_controls.py'), '--run', '--report-dir',
            str(session.root / 'owner-controls')], observer / 'diagnostics')
        q.require(result['returncode'] == 0, 'owner_controls_failed')
        q.validate_owner_controls(unique_json(raw))
        progress['owner_control_count'] = 9
        resources.inner_pairs -= 11
    checked('native', native)
    checked('retained', lambda: reader.verify_retained_controls(session, observer))
    progress['retained_control_count'] = 5
    def generated():
        result, _ = threshold.private_command(session, [sys.executable,
            str(observer / 'diagnostics/diagnose_generated_outputs.py'), '--contract-child'], observer / 'diagnostics')
        q.verify_probe(result, reader.generated.CONTRACT_CONTROL_COUNT, LOOKUPS[0])
        progress['generated_control_count'] = reader.generated.CONTRACT_CONTROL_COUNT
    checked('contract', generated)
    def native_dual():
        result, raw = threshold.private_command(session, [sys.executable,
            str(observer / 'diagnostics/current_parallel_native_controls.py'), '--run', '--report-dir',
            str(session.root / 'dual-controls')], observer / 'diagnostics')
        receipt = dual.read_receipt(raw.removesuffix(b'\n'))
        q.require(result['returncode'] == 0 and not result['stderr'] and receipt['status'] == 'passed'
                  and receipt['process_cleanup_verified'], 'parallel_native_controls_failed')
        progress['dual_owner_control_count'] = 3
        resources.inner_pairs -= 7
    checked('dual_native', native_dual)
    root = checked('clone', lambda: maintainer.workspace_clone_root(session.root, observer, seed, expected))
    q.require(ResourcePlan.identity(root)[0] == resources.identities[1][0], 'parallel_storage_identity_changed')
    saved_path = sys.path[:]
    check = cls = manifest = None
    try:
        for arm in ('cap1', 'cap2'):
            admit_block(session.hard_deadline, time.monotonic(), 'cap1' if arm == 'cap1' else 'cap2_prepare')
            progress['phase'] = session.phase = arm + '_preparation'
            lanes = prepare_arm(session, seed, root, arm, expected, candidate, progress, clones, guard, resources)
            for repo in lanes:
                def temp_check(repo=repo):
                    result, _ = threshold.private_command(session, q.child_command(observer, 'validate-temp', repo), repo / 'tools')
                    receipt = q.parse_child(result)
                    q.require(receipt.get('outside_checkout_temp') is True and receipt.get('temp_environment_unchanged') is True,
                              'temp_validation_incomplete')
                    maintainer.verify_hook_location(session, repo)
                checked('temp', temp_check)
            checked('pair_behavior', lambda: maintainer.behavior_controls(session, observer, lanes[0], 'candidate'))
            checked('pair_explicit', lambda: maintainer.explicit_controls(session, seed, lanes[0]))
            target = {**expected, q.SUITE_PATH: q.CANDIDATE_HASH}
            if check is None:
                progress['phase'] = 'source_population'
                test_path = 'tools/test_code_set_database_reader_check.py'
                test_raw = reader.read_pinned_source(lanes[0], test_path, reader.TEST_HASH, session.deadline)
                reader.read_pinned_source(lanes[0], reader.AUDIT_PATH, reader.AUDIT_HASH, session.deadline)
                q.require(all(name not in sys.modules for name in ('code_set_database_reader_check',
                          'test_code_set_database_reader_check')), 'audit_module_already_loaded')
                sys.path.insert(0, str(lanes[0] / 'tools'))
                with (session.root / 'import-stdout.private').open('xb') as stdout, \
                     (session.root / 'import-stderr.private').open('xb') as stderr:
                    with contextlib.redirect_stdout(reader.PrivateWriter(stdout, session.deadline)), \
                         contextlib.redirect_stderr(reader.PrivateWriter(stderr, session.deadline)):
                        check = importlib.import_module('code_set_database_reader_check')
                        test_module = importlib.import_module('test_code_set_database_reader_check')
                cls = getattr(test_module, reader.CLASS_ID.rsplit('.', 1)[-1])
                q.require(Path(check.__file__).resolve() == lanes[0] / reader.AUDIT_PATH
                          and Path(test_module.__file__).resolve() == lanes[0] / test_path
                          and check.LOOKUPS == frozenset(LOOKUPS) and check._SUBPROCESS == payload
                          and cls.__module__ + '.' + cls.__name__ == reader.CLASS_ID, 'audit_import_identity_changed')
                planted = reader.population_from_sources(check, reader.planted_sources(test_raw))
                q.require(len(planted['modules']) == 11, 'planted_population_changed')
            source_hashes = {Path(name).name: value for name, value in target.items()
                if name.startswith('tools/') and '/' not in name[6:] and name.endswith('.py')}
            for repo in lanes:
                current = reader.source_population(check, repo / 'tools', session.deadline, source_hashes)
                q.require(current['source_file_count'] == 469 and len(current['modules']) == 146
                          and reader.token([['repository', module, lookup] for module in current['modules'] for lookup in LOOKUPS])
                          == PAIR_MANIFEST, 'parallel_population_changed')
                if manifest is None: manifest = current
                else: q.require(current == manifest, 'parallel_population_changed')
            reference = reference_rows(reference_raw, manifest['modules'])
            if arm == 'cap1':
                progress['phase'] = session.phase = 'planted_control'
                guard()
                with consumer_scope(session, 'planted') as scope:
                    progress['planted'] = observe_planted(check, cls, lanes[0] / 'tools', {'planted': planted}, session, guard, payload)
                    q.emit('parallel_planted_control', **progress['planted'])
                    q.require(progress['planted']['complete'] and len(progress['planted']['pairs']) == 22, 'parallel_planted_incomplete')
                    acknowledge_controls(session, scope, 'planted', progress['planted'])
                q.emit('parallel_population', source_sha=SOURCE_SHA, source_file_count=469,
                    manifest_sha256=PAIR_MANIFEST, modules=146, pairs=[{'module': module, 'lookup': lookup,
                    'pair_token': reader.token(['repository', module, lookup]), 'source_sha256': source_hashes[module + '.py']}
                    for module in manifest['modules'] for lookup in LOOKUPS])
                progress['preparation_seconds'] = time.monotonic() - preparation
            else:
                q.require(reference == signatures(progress['arms']['cap1']['observations']), 'parallel_work_changed')
            admit_block(session.hard_deadline, time.monotonic(), arm)
            progress['phase'] = session.phase = arm + '_measurement'
            arm_started = time.monotonic()
            try:
                measure_arm(session, lanes, arm, manifest, target, payload, reference, progress, guard, resources, environment)
            finally:
                progress.setdefault('arm_wall_seconds', {})[arm] = time.monotonic() - arm_started
            q.emit('parallel_arm_timing', arm=arm, wall_seconds=progress['arm_wall_seconds'][arm],
                   schedule_wall_seconds=progress['arms'][arm]['schedule_wall_seconds'])
        admit_block(session.hard_deadline, time.monotonic(), 'final')
        progress['phase'] = session.phase = 'final_verification'
        guard()
        for arm in ('cap1', 'cap2'): encode_arm(progress['arms'][arm], manifest['modules'])
        compact_summary = session.compact.public_summary() if getattr(session, 'compact', None) is not None else None
        envelope = {'schema_version': 1, 'source_sha': SOURCE_SHA, 'candidate_sha256': q.CANDIDATE_HASH,
                    'observer_sha': environment['GITHUB_SHA'], 'run_id': environment['GITHUB_RUN_ID'],
                    'job_start_epoch': origin, 'environment_sha256': progress['environment_sha256'],
                    'reference_sha256': REFERENCE_HASH, 'source_hashes': source_hashes,
                    'manifest_sha256': PAIR_MANIFEST, 'pinned_pairs': sorted(manifest['pinned']),
                    'planted': progress['planted'], 'arms': progress['arms'], 'arm_wall_seconds': progress['arm_wall_seconds'],
                    'compact_retention_before_final_guard': compact_summary}
        progress.update(retained_json(session, 'parallel-receipt.json',
            json.dumps(envelope, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()))
        guard()
        if getattr(session, 'compact', None) is not None:
            progress['compact_retention'] = session.compact.public_summary()
            q.require(progress['compact_retention']['all_retired_verified'], 'compact_invocation_incomplete')
        progress.update(source_integrity_verified=True, output_contract_verified=True,
                        helper_commands_attempted=session.command_attempts, clone_logical_byte_basis=resources.clone_basis)
    finally:
        sys.path[:] = saved_path


def reason(error):
    from compact_capture_retention import CompactRefused, REASONS
    if type(error) is CompactRefused:
        value = error.args[0] if len(error.args) == 1 else None
        return value if type(value) is str and value in REASONS else 'unavailable'
    value = error.args[0] if type(error) is q.Refused and len(error.args) == 1 else None
    return value if type(value) is str and value in FAILURE_REASONS else 'unavailable'


def note_failure(progress, error):
    progress.setdefault('failure_context', {'stage': progress['phase'], 'reason': reason(error)})


def _run(argv, public):
    environment, start = dict(os.environ), time.monotonic()
    session = root = hard = None
    complete = clean = False
    progress = {'phase': 'preflight', 'arms': {}, 'arm_receipts': {}, 'source_integrity_verified': False,
                'output_contract_verified': False, 'receipt_verified': False}
    try:
        parser = threshold.FiniteParser(add_help=False)
        parser.add_argument('--observer', type=Path, required=True)
        parser.add_argument('--seed', type=Path, required=True)
        parser.add_argument('--job-start-epoch', type=float, required=True)
        args = parser.parse_args(argv)
        reader.authorize_route(os.name, platform.python_version(), environment)
        deadline, hard = budget_deadlines(args.job_start_epoch, time.time(), start)
        q.environment_preflight()
        observer, seed = args.observer.resolve(), args.seed.resolve()
        q.require(observer != seed and observer not in seed.parents and seed not in observer.parents, 'checkout_overlap')
        q.corpus_preflight((observer, seed))
        temporary = Path(tempfile.gettempdir()).resolve()
        q.require(all(not temporary.is_relative_to(repo) for repo in (observer, seed)), 'temp_inside_checkout')
        identity = maintainer.environment_identity(); maintainer.validate_environment(identity)
        progress['environment_sha256'] = q.digest(json.dumps(identity, sort_keys=True).encode())
        root = Path(tempfile.mkdtemp(prefix='current-parallel-owner-', dir=temporary)).resolve()
        session = ComparisonSession(root, deadline, hard, compact=True)
        q.emit('parallel_environment', **identity)
        execute(session, observer, seed, args.job_start_epoch, progress, environment)
        q.require(dict(os.environ) == environment and time.monotonic() < deadline, 'environment_or_budget_changed')
        complete = (all(progress[key] is True for key in ('source_integrity_verified', 'output_contract_verified', 'receipt_verified'))
                    and all(progress['arms'].get(arm, {}).get('qualified') is True for arm in ('cap1', 'cap2')))
    except BaseException as error:
        note_failure(progress, error); reader.retain_private_error(error, root)
    finally:
        cleanup_start = time.monotonic()
        if session is not None:
            try: clean = session.cleanup() is True
            except BaseException as error: reader.retain_private_error(error, root)
            if getattr(session, 'compact', None) is not None:
                try:
                    progress['compact_retention'] = session.compact.public_summary()
                    complete = complete and progress['compact_retention']['all_retired_verified'] is True
                except BaseException as error:
                    complete = False; reader.retain_private_error(error, root)
        public.terminal = True
        within = hard is not None and time.monotonic() < hard
        passed = complete and clean and within
        summary = {key: value for key, value in progress.items() if key not in ('arms', 'arm_receipts', 'planted')}
        try:
            q.emit('parallel_summary', **summary, status='complete' if passed else 'inconclusive',
                source_sha=SOURCE_SHA, candidate_sha256=q.CANDIDATE_HASH,
                observer_sha=environment.get('GITHUB_SHA') if re.fullmatch(r'[0-9a-f]{40}', environment.get('GITHUB_SHA', '')) else None,
                run_id=environment.get('GITHUB_RUN_ID') if re.fullmatch(r'[0-9]{1,20}', environment.get('GITHUB_RUN_ID', '')) else None,
                arms_qualified=sum(row.get('qualified') is True for row in progress['arms'].values()), arms_expected=2,
                process_cleanup_verified=clean, hard_budget_verified=within,
                observer_seconds=time.monotonic() - start, cleanup_seconds=time.monotonic() - cleanup_start,
                timing_screen_complete=passed, performance_qualified=False, per_executed_id_attestation=False,
                full_original_reader_class_executed=False, full_suite_execution=False, adoption_authorized=False,
                automatic_rerun=False, private_raw_evidence_uploaded=False, runner_teardown_proved=False,
                capture_retention_policy='compact_verified_success', successful_raw_reanalysis_available=False,
                inner_capture_disposal_enabled=False, secure_erasure_proved=False,
                reclaimed_space_inferred=False)
        except BaseException as error:
            passed = False; reader.retain_private_error(error, root)
    return 0 if passed and hard is not None and time.monotonic() < hard else 2


def main(argv=None):
    public = reader.PublicOutput(sys.stdout)
    try:
        with contextlib.redirect_stdout(public): return _run(argv, public)
    except BaseException:
        return 2


if __name__ == '__main__': raise SystemExit(main())
