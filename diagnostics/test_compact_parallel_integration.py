"""Synthetic final-consumer controls; no application or Windows process runs."""
import hashlib
from pathlib import Path
import unittest

import test_current_parallel_runner as fixtures
from test_current_parallel_runner import CLEAN, REFUSAL
from generated_output_contract import read_owned_capture
from parallel_reader_scheduler import LOOKUPS
from current_parallel_runner import RunnerRefused


class FakeStore:
    def __init__(self, fail=False):
        self.calls = []; self.fail = fail
    def add_capture_root(self, root):
        self.calls.append(('root', root))
    def reserve(self, root, report, bindings):
        if report.exists(): raise AssertionError('reservation was not before creation')
        ticket = {'root': root, 'report': report}
        self.calls.append(('reserve', ticket)); return ticket
    def register(self, ticket, owner, result, reads):
        assert result is owner.result
        ticket.update(owner=owner, result=result, reads=reads)
        self.calls.append(('register', ticket))
    def retire(self, ticket, consumer, evidence):
        self.calls.append(('retire', consumer, evidence))
        if self.fail: raise RuntimeError('PRIVATE_DISPOSAL_SENTINEL')
        # Only fresh files made by the injected synthetic owner are removed.
        for path in (ticket['owner'].stdout_path, ticket['owner'].stderr_path): path.unlink()
        return {'complete': True}


def synthetic_snapshot(root, relative, limit, deadline):
    return read_owned_capture(root, relative, limit, deadline), object()


def reference(module='test_alpha'):
    return {(module, lookup): {'module': module, 'lookup': lookup, 'returncode': 0,
        'classification': 'nonreader', 'test_count': 3, 'failures': 0, 'errors': 0,
        'skipped': 1, 'expected_failures': 0, 'screen_clean': True,
        'capture_read_verified': True, 'cleanup_verified': True} for lookup in LOOKUPS}


class CompactRunnerControls(unittest.TestCase):
    setUp = fixtures.RunnerTests.setUp
    runner = fixtures.RunnerTests.runner
    schedule = fixtures.RunnerTests.schedule

    def test_real_store_retains_compact_original_rows_with_real_owner_result_types(self):
        from types import SimpleNamespace
        from compact_capture_retention import CompactStore
        from test_compact_capture_retention import FakeNative
        invocation = self.root / 'invocation'; invocation.mkdir()
        api = FakeNative(); store = CompactStore(invocation, self.clock() + 100, api=api)
        captures = invocation / 'cap1-captures'; captures.mkdir()
        start = self.factory.start
        def start_with_saved_native_info(*args, **kwargs):
            owner = start(*args, **kwargs)
            owner._info = SimpleNamespace(dwProcessId=owner.pid)
            return owner
        self.factory.start = start_with_saved_native_info
        def snapshot(root, relative, limit, deadline):
            with (root / relative).open('rb') as stream:
                return stream.read(), api.record(stream.fileno())
        runner = self.runner(arm='cap1', capture_root=captures, compact=store,
            compact_reference=reference(), snapshot_reader=snapshot)
        result = self.schedule(runner, 1)
        self.assertTrue(result.complete, runner.first_failure)
        self.assertTrue(runner.cleanup())
        self.assertEqual(4, len(api.disposed))
        self.assertEqual(6, len(list(invocation.glob('compact-*.json'))))
        self.assertFalse(store.blocked)

    def unexpected_runner(self, plans, *, deadline=None):
        from types import SimpleNamespace
        from compact_capture_retention import CompactStore
        from test_compact_capture_retention import FakeNative
        invocation = self.root / 'invocation'; invocation.mkdir()
        api = FakeNative(); store = CompactStore(invocation, self.clock() + 100, api=api)
        captures = invocation / 'cap2-captures'; captures.mkdir()
        start = self.factory.start
        def owned(*args, **kwargs):
            owner = start(*args, **kwargs)
            owner._info = SimpleNamespace(dwProcessId=owner.pid)
            return owner
        self.factory.start = owned; self.factory.plans = plans
        def snapshot(root, relative, limit, deadline):
            with (root / relative).open('rb') as stream:
                return stream.read(), api.record(stream.fileno())
        modules = ('test_alpha', 'test_beta', 'test_gamma')
        expected = {key: value for module in modules for key, value in reference(module).items()}
        slots = []
        runner = self.runner(arm='cap2', modules=modules, capture_root=captures,
            compact=store, compact_reference=expected, snapshot_reader=snapshot,
            deadline=deadline or self.clock() + 100)
        import measure_current_parallel as driver
        from unittest.mock import patch
        session = SimpleNamespace(root=invocation, deadline=runner.deadline, runners=[runner],
            compact=store, pending_helper_pairs=0, pending_helper_capacity_bytes=0)
        resources = driver.ResourcePlan(session, self.clones[0], self.root)
        def actual_resource_check():
            slots.append(runner.pending_capture_slots)
            with patch.object(driver.shutil, 'disk_usage', return_value=SimpleNamespace(free=2**40)):
                return resources.check()
        runner.resource_check = actual_resource_check
        return runner, store, api, slots

    def test_actual_resource_plan_admits_preowner_reservations_once(self):
        runner, store, api, slots = self.unexpected_runner({})
        result = self.schedule(runner, 2)
        self.assertTrue(result.complete, runner.first_failure)
        self.assertEqual(6, len(self.factory.owners))
        self.assertEqual(6, len(runner.attempt_ledger()))
        self.assertEqual(1, slots[0], 'The first pre-owner reservation occupies one slot')
        self.assertLessEqual(max(slots), 2)
        self.assertEqual(0, runner.pending_capture_slots)
        self.assertEqual(12, len(api.disposed))
        self.assertTrue(runner.cleanup())

    def test_unexpected_later_row_retains_raw_and_preserves_sorted_first_error(self):
        runner, store, api, slots = self.unexpected_runner({
            ('test_alpha', LOOKUPS[0]): {'delay': 5},
            ('test_alpha', LOOKUPS[1]): {'delay': 2, 'code': 1},
            ('test_beta', LOOKUPS[0]): {'delay': 1, 'code': 1}})
        result = self.schedule(runner, 2)
        self.assertEqual((False, ('test_alpha', LOOKUPS[1]), True, 'unexpected_probe_result'),
            (result.complete, result.first_error, result.first_error_resolved, result.stop_reason))
        self.assertEqual([('test_alpha', LOOKUPS[0]), ('test_beta', LOOKUPS[0]),
                          ('test_alpha', LOOKUPS[1])],
                         [(row['module'], row['lookup']) for row in runner.attempt_ledger()])
        self.assertEqual((3, 1, 2), tuple(store.public_summary()[key] for key in
            ('reserved_pairs', 'retired_complete_pairs', 'pending_pairs')))
        self.assertEqual(2, runner.pending_capture_slots)
        self.assertEqual(2, len(api.disposed))
        self.assertLessEqual(max(slots), 2)
        self.assertFalse(runner._compact_failed)
        self.assertEqual('capture_screen_failed', runner.first_failure['reason'])
        for owner in self.factory.owners[1:]:
            self.assertTrue(owner.stdout_path.exists() and owner.stderr_path.exists())
        self.assertTrue(runner.cleanup())

    def test_unexpected_observation_does_not_enter_success_only_retirement_validation(self):
        store = FakeStore()
        def unexpected_registration(*args):
            raise AssertionError('Unexpected execution is not a compact-success candidate')
        store.register = unexpected_registration
        self.factory.plans = {('test_alpha', LOOKUPS[0]): {'code': 1}}
        runner = self.runner(arm='cap1', compact=store, compact_reference=reference(),
                             snapshot_reader=synthetic_snapshot)
        result = self.schedule(runner, 1)
        self.assertEqual((('test_alpha', LOOKUPS[0]), True, 'unexpected_probe_result'),
                         (result.first_error, result.first_error_resolved, result.stop_reason))
        self.assertEqual(['root', 'reserve'], [item[0] for item in store.calls])
        self.assertEqual(1, runner.pending_capture_slots)

    def test_retained_later_failure_allows_earlier_second_lookup_but_no_new_module(self):
        runner, store, api, slots = self.unexpected_runner({
            ('test_alpha', LOOKUPS[0]): {'delay': 5},
            ('test_beta', LOOKUPS[0]): {'delay': 1, 'code': 1}})
        result = self.schedule(runner, 2)
        self.assertEqual((('test_beta', LOOKUPS[0]), True, 'unexpected_probe_result'),
            (result.first_error, result.first_error_resolved, result.stop_reason))
        self.assertEqual(3, len(runner.attempt_ledger()))
        self.assertEqual((1, 0), (runner.pending_capture_slots, runner.pending_capture_bytes()))
        self.assertEqual(4, len(api.disposed))
        self.assertLessEqual(max(slots), 2)
        self.assertTrue(self.factory.owners[1].stderr_path.exists())
        self.assertTrue(runner.cleanup())

    def test_earlier_hang_keeps_original_unresolved_error_and_both_raw_pairs(self):
        runner, store, api, slots = self.unexpected_runner({
            ('test_alpha', LOOKUPS[0]): {'delay': 1000},
            ('test_beta', LOOKUPS[0]): {'delay': 1, 'code': 1}}, deadline=self.clock() + 5)
        result = self.schedule(runner, 2)
        self.assertEqual((False, False, 'whole_job_measurement_budget_exhausted'),
            (result.complete, result.first_error_resolved, result.stop_reason))
        self.assertEqual(2, len(runner.attempt_ledger()))
        self.assertEqual([], api.disposed)
        self.assertEqual(2, runner.pending_capture_slots)
        self.assertTrue(runner.cleanup())
        self.assertTrue(all(owner.stdout_path.exists() and owner.stderr_path.exists()
                            for owner in self.factory.owners))

    def test_pair_is_immutable_and_retired_before_next_original_lookup_launch(self):
        store = FakeStore()
        runner = self.runner(arm='cap1', compact=store, compact_reference=reference(),
                             snapshot_reader=synthetic_snapshot)
        result = self.schedule(runner, 1)
        self.assertTrue(result.complete)
        self.assertEqual(['root', 'reserve', 'register', 'retire', 'reserve', 'register', 'retire'],
                         [row[0] for row in store.calls])
        self.assertEqual(2, len(runner.attempt_ledger()))
        self.assertTrue(runner.cleanup())
        self.assertTrue(all(not owner.stdout_path.exists() and not owner.stderr_path.exists()
                            for owner in self.factory.owners))
        self.assertEqual(hashlib.sha256(CLEAN).hexdigest(), runner.attempt_ledger()[0]['stderr_sha256'])

    def test_reference_mismatch_retains_original_raw_and_stops_before_second_lookup(self):
        expected = reference(); expected[('test_alpha', LOOKUPS[0])]['test_count'] = 4
        store = FakeStore()
        runner = self.runner(arm='cap1', compact=store, compact_reference=expected,
                             snapshot_reader=synthetic_snapshot)
        result = self.schedule(runner, 1)
        self.assertFalse(result.complete)
        self.assertEqual(1, len(self.factory.owners))
        self.assertNotIn('retire', [row[0] for row in store.calls])
        self.assertTrue(self.factory.owners[0].stderr_path.exists())

    def test_partial_disposal_failure_never_retries_or_launches_more_work(self):
        store = FakeStore(fail=True)
        runner = self.runner(arm='cap1', compact=store, compact_reference=reference(),
                             snapshot_reader=synthetic_snapshot)
        result = self.schedule(runner, 1)
        self.assertFalse(result.complete)
        self.assertEqual(1, len(self.factory.owners))
        self.assertEqual(1, sum(row[0] == 'retire' for row in store.calls))
        self.assertEqual('compact_retirement_inconclusive', runner.first_failure['reason'])
        self.assertTrue(runner.cleanup())
        with self.assertRaises(RunnerRefused): runner.start(0, 0, 'test_alpha', LOOKUPS[1])

    def test_expected_pinned_nonzero_reader_is_eligible_without_changing_classification(self):
        self.factory.plans = {('test_alpha', LOOKUPS[0]): {'code': 1, 'stderr': REFUSAL}}
        expected = reference(); expected[('test_alpha', LOOKUPS[0])].update(
            returncode=1, classification='reader', test_count=1, failures=1, skipped=0)
        store = FakeStore()
        runner = self.runner(arm='cap1', compact=store, compact_reference=expected,
                             snapshot_reader=synthetic_snapshot)
        result = self.schedule(runner, 1)
        self.assertTrue(result.complete)
        self.assertEqual('reader', result.observations[0].classification)
        self.assertEqual(2, sum(row[0] == 'retire' for row in store.calls))




class CompactDiskControls(unittest.TestCase):
    def test_admission_receipt_names_the_tighter_clone_ref_condition(self):
        import measure_current_parallel as driver
        policy = driver.compact_admission_policy()
        self.assertEqual(32, policy['pending_helper_pairs'])
        self.assertEqual((11, 8, 13), tuple(policy[key] for key in
            ('clone_context_fixed_calls', 'trailing_guard_peak_calls', 'maximum_deleted_refs_per_clone')))
        self.assertEqual(1346, policy['maximum_successful_helper_calls'])
        self.assertFalse(policy['seed_ref_count_assumed'])
        self.assertEqual(2, policy['undisposed_measured_pairs_including_failures'])

    def test_session_selects_explicit_compact_lifecycle_not_retained_log_fallback(self):
        import tempfile, types
        import measure_current_parallel as driver
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); captures = root / 'captures'; captures.mkdir()
            seed = root / 'seed'; seed.mkdir(); (seed / 'source').write_bytes(b'synthetic')
            store = types.SimpleNamespace(root=captures, remaining_receipt_bytes=107347968)
            session = driver.ComparisonSession(captures, driver.time.monotonic() + 60,
                driver.time.monotonic() + 120, compact=store, snapshot_reader=synthetic_snapshot)
            self.assertIs(store, session.compact)
            plan = driver.ResourcePlan(session, seed, root)
            self.assertLess(plan.required()['evidence'], 12 * driver.GIB)
            plan.inner_pairs = 0
            remaining = plan.required()['evidence']
            self.assertLess(remaining, 11 * driver.GIB)

    def test_compact_lifecycle_counts_next_window_and_full_finite_receipt_allowance(self):
        import measure_current_parallel as driver
        mib = 1024 ** 2
        result = driver.compact_disk_requirements(2 * 32 * mib, 18, 32 * 32 * mib, 107347968, 4, 100, False)
        self.assertEqual(1024 * mib + 64 * mib + 576 * mib + 1024 * mib
                         + 64 * mib + 4096 * mib + 128 * mib + 107347968, result['evidence'])
        self.assertEqual(5 * 1024 * mib + 800, result['clones'])
        joined = driver.compact_disk_requirements(2 * 32 * mib, 18, 32 * 32 * mib, 107347968, 4, 100, True)
        self.assertEqual(result['evidence'] + result['clones'] - 1024 * mib, joined['evidence'])
        self.assertEqual(0, joined['clones'])

    def test_completed_pending_helpers_reduce_future_growth_without_releasing_slots(self):
        import tempfile, types
        import measure_current_parallel as driver
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); seed = root / 'seed'; seed.mkdir()
            session = types.SimpleNamespace(root=root, deadline=driver.time.monotonic() + 60,
                runners=[], compact=types.SimpleNamespace(remaining_receipt_bytes=107347968),
                pending_helper_pairs=0, pending_helper_capacity_bytes=0)
            plan = driver.ResourcePlan(session, seed, root)
            initial = plan.required()['evidence']
            session.pending_helper_pairs = 22
            self.assertEqual(initial - 22 * 32 * 1024 ** 2, plan.required()['evidence'])
            session.pending_helper_pairs = 23
            session.pending_helper_capacity_bytes = 16 * 1024 ** 2
            self.assertEqual(initial - 22 * 32 * 1024 ** 2 - 16 * 1024 ** 2,
                             plan.required()['evidence'])


class DriverConsumerControls(unittest.TestCase):
    def test_actual_clone_preparation_acknowledges_only_after_its_trailing_guard(self):
        import contextlib, types
        from unittest.mock import patch
        import measure_current_parallel as driver
        from compact_parallel_consumers import helper_evidence
        for fail in (False, True):
            events = []; scopes = []
            @contextlib.contextmanager
            def scope(name):
                item = types.SimpleNamespace(records=[]); scopes.append(item)
                try: yield item
                finally: scopes.pop()
            session = types.SimpleNamespace(compact=object(), consumer_scope=scope,
                helper_evidence=helper_evidence,
                complete_consumer=lambda *args: events.append('retire'))
            expected = {driver.q.SUITE_PATH: driver.q.ORIGINAL_HASH,
                        driver.threshold.MODULE_PATH: driver.threshold.BASELINE_HASH}
            target = {**expected, driver.q.SUITE_PATH: driver.q.CANDIDATE_HASH}
            def source_context(session, seed, repo, *args, **kwargs):
                events.append('clone')
                self.assertTrue(scopes, 'clone has no explicit final-consumer scope')
                scopes[-1].records.append({'argv': ('git', '-c', 'core.autocrlf=false', 'clone',
                    '--no-local', '--no-hardlinks', '--no-checkout', str(seed), str(repo)),
                    'result': {'returncode': 0}, 'reads': ((b'', object()), (b'', object()))})
                return target
            def guard():
                events.append('guard')
                if fail and 'clone' in events: raise driver.q.Refused('source_refs_changed')
            resources = types.SimpleNamespace(check=lambda: None, cloned=lambda repo: events.append('inventory'))
            with patch.object(driver.maintainer, 'source_context', side_effect=source_context):
                if fail:
                    with self.assertRaisesRegex(driver.q.Refused, 'source_refs_changed'):
                        driver.prepare_arm(session, Path('/seed'), Path('/fresh'), 'cap1', expected,
                            b'', {'arms': {}}, [], guard, resources)
                    self.assertNotIn('retire', events)
                else:
                    driver.prepare_arm(session, Path('/seed'), Path('/fresh'), 'cap1', expected,
                        b'', {'arms': {}}, [], guard, resources)
                    self.assertEqual(['guard','clone','inventory','guard','retire'] * 2, events)

    def test_clone_and_probe_acknowledgments_keep_exact_validated_semantics(self):
        import types
        from unittest.mock import patch
        import measure_current_parallel as driver
        from compact_parallel_consumers import helper_evidence
        record = {'argv': ('git', '-c', 'core.autocrlf=false', 'clone', '--no-local',
                          '--no-hardlinks', '--no-checkout', '/seed', '/clone'),
                  'result': {'returncode': 0}, 'reads': ((b'', object()), (b'', object()))}
        scope = types.SimpleNamespace(records=[record]); calls = []
        session = types.SimpleNamespace(helper_evidence=helper_evidence,
            complete_consumer=lambda *args: calls.append(args))
        driver.acknowledge_controls(session, scope, 'source_clone')
        self.assertEqual('helper_result', calls.pop()[1][0][1])
        record['argv'] = (driver.sys.executable, '/synthetic/diagnose_generated_outputs.py', '--contract-child')
        with patch.object(driver.q, 'verify_probe', return_value={'valid': True, 'count': 17}) as verified:
            driver.acknowledge_controls(session, scope, 'contract')
        self.assertEqual({'valid': True, 'count': 17}, calls.pop()[1][0][2]['result']['semantic_result'])
        self.assertEqual(1, verified.call_count)

    def test_planted_acknowledgment_requires_original_method_success_and_exact_pair_binding(self):
        import types
        from unittest.mock import patch
        import measure_current_parallel as driver
        from compact_parallel_consumers import helper_evidence
        argv = (driver.sys.executable, '-c', 'synthetic', '/fixture', 'test_one', LOOKUPS[0])
        record = {'argv': argv, 'result': {'returncode': 0}, 'reads': ((b'', object()), (CLEAN, object()))}
        row = {'pair_token': driver.reader.token(['planted', *argv[-2:]]), 'classification': 'nonreader'}
        scope = types.SimpleNamespace(records=[record]); calls = []
        session = types.SimpleNamespace(helper_evidence=helper_evidence,
            complete_consumer=lambda *args: calls.append(args))
        with patch.object(driver, 'PAYLOAD_HASH', driver.q.digest(b'synthetic')):
            with self.assertRaisesRegex(driver.q.Refused, 'compact_consumer_shape_changed'):
                driver.acknowledge_controls(session, scope, 'planted', {'complete': False, 'pairs': [row]})
            self.assertEqual([], calls)
            driver.acknowledge_controls(session, scope, 'planted', {'complete': True, 'pairs': [row]})
            self.assertTrue(calls[0][1][0][2]['result']['root_identity_verified'])
            self.assertNotIn('root_identity_verified', row)
            calls.clear(); row['pair_token'] = 'f' * 64
            with self.assertRaises(driver.q.Refused):
                driver.acknowledge_controls(session, scope, 'planted', {'complete': True, 'pairs': [row]})
            self.assertEqual([], calls)

    def test_known_control_preserves_full_parsed_receipt_and_unknown_scope_retains_raw(self):
        import json, types
        import measure_current_parallel as driver
        from compact_parallel_consumers import helper_evidence
        raw = json.dumps({'schema': 'synthetic', 'controls': [{'original': True}]}).encode()
        record = {'argv': (driver.sys.executable, '/synthetic/diagnostics/windows_job_probe_controls.py',
                    '--run', '--report-dir', '/fresh/owner-controls'),
                  'cwd': Path('/synthetic/diagnostics'), 'result': {'returncode': 0},
                  'reads': ((raw, object()), (b'', object()))}
        scope = types.SimpleNamespace(records=[record]); calls = []
        session = types.SimpleNamespace(helper_evidence=helper_evidence,
            complete_consumer=lambda *args: calls.append(args))
        driver.acknowledge_controls(session, scope, 'native')
        self.assertEqual(json.loads(raw), calls[0][1][0][2]['result'])
        self.assertEqual('outer_control', calls[0][1][0][1])
        calls.clear()
        with self.assertRaisesRegex(driver.q.Refused, 'compact_consumer_shape_changed'):
            driver.acknowledge_controls(session, scope, 'unknown')
        self.assertEqual([], calls)

    def test_detached_head_requires_exact_known_consumer_before_acknowledging_nonzero_success(self):
        import types
        import measure_current_parallel as driver
        from compact_parallel_consumers import helper_evidence
        record = {'argv': ('git', '-C', '/synthetic', 'symbolic-ref', '-q', 'HEAD'),
                  'cwd': Path('/synthetic'), 'result': {'returncode': 1, 'stdout': '', 'stderr': ''},
                  'reads': ((b'', object()), (b'', object()))}
        scope = types.SimpleNamespace(records=[record]); calls = []
        session = types.SimpleNamespace(helper_evidence=helper_evidence,
            complete_consumer=lambda *args: calls.append(args))
        driver.acknowledge_controls(session, scope, 'detached')
        self.assertEqual('detached_head', calls[0][1][0][2]['result']['category'])
        self.assertEqual('helper_result', calls[0][1][0][1])
        calls.clear(); record['argv'] = ('git', '-C', '/synthetic', 'unknown-command')
        with self.assertRaisesRegex(driver.q.Refused, 'compact_consumer_shape_changed'):
            driver.acknowledge_controls(session, scope, 'detached')
        self.assertEqual([], calls)

class FirstStatusPrimaryTests(unittest.TestCase):
    def test_dirty_status_remains_primary_when_optional_diagnostics_refuse(self):
        import tempfile
        import measure_lazy_suite_ids as q
        from types import SimpleNamespace
        from unittest.mock import patch
        for boundary in ('emit', 'conversion_config_receipt'):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as directory:
                repo = Path(directory).resolve()
                (repo / '.git').mkdir()
                status_calls = []
                session = SimpleNamespace(
                    git=lambda root, *args: '.git' if args[-1] == '--git-common-dir' else 'a' * 40,
                    git_bytes=lambda root, *args: status_calls.append(args) or b' M source.py\0')
                with patch.object(q, 'emit'), patch.object(q, boundary,
                        side_effect=q.Refused('compact_helper_pending_limit')):
                    with self.assertRaisesRegex(q.Refused, '^first_status_not_clean$'):
                        q.first_clean(session, repo, 'a' * 40, 'observer')
                self.assertEqual(status_calls, [('status', '--porcelain=v1', '--untracked-files=all')])

if __name__ == '__main__':
    unittest.main()
