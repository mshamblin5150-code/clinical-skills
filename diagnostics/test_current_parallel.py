"""Portable, source-only controls at the reviewed comparison boundaries."""
import copy
import io
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

import measure_current_parallel as subject


class AdmissionControls(unittest.TestCase):
    def test_clone_inventory_refuses_unreadable_git_instead_of_undercounting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); (root / '.git').mkdir()
            (root / 'visible').write_bytes(b'abcd'); (root / '.git/pack').write_bytes(b'0123456789')
            deadline = subject.time.monotonic() + 60
            self.assertEqual(14, subject.tree_size(root, deadline))
            original = subject.os.scandir
            def scandir(path):
                if Path(path) == root / '.git': raise PermissionError('PRIVATE inventory sentinel')
                return original(path)
            with mock.patch.object(subject.os, 'scandir', side_effect=scandir):
                with self.assertRaisesRegex(subject.q.Refused, '^parallel_storage_inventory_unread$'):
                    subject.tree_size(root, deadline)

    def test_single_origin_preserves_cleanup_and_declines_late_second_arm(self):
        work, hard = subject.budget_deadlines(1000, 1120, 200)
        self.assertEqual((5180, 5480), (work, hard))
        self.assertEqual(360, subject.admit_block(hard, 200, 'cap1'))
        self.assertEqual(0, subject.admit_block(hard, 2660, 'cap2_prepare'))
        with self.assertRaisesRegex(subject.q.Refused, 'parallel_admission_exhausted'):
            subject.admit_block(hard, 2660.001, 'cap2_prepare')
        for origin in (True, float('nan'), 1121, -5000):
            with self.assertRaises(subject.q.Refused): subject.budget_deadlines(origin, 1120, 200)

    def test_disk_reserves_actual_remaining_work_without_double_counting_retained_bytes(self):
        start = subject.disk_requirements(584, 0, 2, 4, 100, False)
        later = subject.disk_requirements(292, 123, 1, 2, 200, False)
        self.assertEqual(9831448453, start['evidence'] - later['evidence'])
        self.assertEqual(start['clones'], later['clones'])
        joined = subject.disk_requirements(584, 0, 2, 4, 100, True)
        self.assertEqual(start['evidence'] + start['clones'] - 1073741824, joined['evidence'])
        self.assertEqual(0, joined['clones'])
        with self.assertRaises(subject.q.Refused): subject.disk_requirements(True, 0, 2, 4, 100, False)
        complete = subject.disk_requirements(584, 0, 2, 4, 100, False, inner_pairs=0)
        self.assertEqual(start['evidence'] - complete['evidence'], 18 * 32 * 1024 ** 2)
        with self.assertRaises(subject.q.Refused): subject.disk_requirements(584, 0, 2, 4, 100, False, inner_pairs=True)

    def test_disk_plan_authenticates_roots_and_refuses_insufficient_actual_capacity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); capture = root / 'capture'; capture.mkdir()
            seed = root / 'seed'; seed.mkdir(); (seed / 'data').write_bytes(b'123')
            session = types.SimpleNamespace(root=capture, command_attempts=0, command_active=False,
                                            deadline=subject.time.monotonic() + 60, runners=[])
            plan = subject.ResourcePlan(session, seed, root)
            required = plan.required()
            with mock.patch.object(subject.shutil, 'disk_usage', return_value=types.SimpleNamespace(free=10 ** 15)):
                observed = plan.check()
            self.assertEqual(required, observed)
            self.assertGreater(required['evidence'], 18 * 1024 ** 3)
            with mock.patch.object(subject.shutil, 'disk_usage', return_value=types.SimpleNamespace(free=required['evidence'] - 1)):
                with self.assertRaisesRegex(subject.q.Refused, 'parallel_disk_admission_exhausted'): plan.check()
            capture.rename(root / 'old'); capture.mkdir()
            with self.assertRaisesRegex(subject.q.Refused, 'parallel_storage_identity_changed'): plan.check()


class PlantedBoundaryControls(unittest.TestCase):
    def test_real_method_lifecycle_is_not_replaced_with_an_assertion_free_planted_loop(self):
        from test_reader_attribution import synthetic_check, SyntheticOwner
        for fail in (False, True):
            with self.subTest(fail=fail), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve(); (root / 'captures').mkdir()
                planted = root / 'planted'; planted.mkdir()
                (planted / 'test_one.py').write_bytes(b'import icd10_lookup\n')
                (planted / 'icd10_lookup.py').write_bytes(b'')
                check = synthetic_check()
                manifests = {'planted': subject.reader.population_from_sources(check,
                    {'test_one.py': b'import icd10_lookup\n', 'icd10_lookup.py': b''})}
                class Fixture(unittest.TestCase):
                    def test_planted_unpinned_readers_and_a_stale_pin_fail_in_both_directions(self):
                        self.assertEqual(frozenset(), check._readers_under_refusal(planted, frozenset(('test_one',))))
                        self.assertFalse(fail, 'PRIVATE_ASSERTION_SENTINEL')
                    def test_the_repository_reader_population_and_pins_agree(self):
                        raise AssertionError('the repository method must not run here')
                session = SyntheticOwner(root / 'captures')
                guards = []
                old = check.subprocess
                result = subject.observe_planted(check, Fixture, root / 'repository', manifests,
                    session, lambda: guards.append('method boundary'), 'synthetic payload')
                self.assertEqual((1, 2, not fail), (result['tests_run'], len(result['pairs']), result['complete']))
                self.assertEqual(['method boundary'], guards)
                self.assertEqual(1 if fail else 0, result['failures'])
                self.assertNotIn('PRIVATE_ASSERTION_SENTINEL', json.dumps(result))
                self.assertIs(old, check.subprocess)


def ledger_row(module='test_b', index=1, ordinal=1):
    return dict(arm='cap1', module_index=index, pair_index=index * 2, module=module,
        lookup='icd10_lookup', lane=index % 2, command_ordinal=ordinal,
        pair_token=subject.reader.token(['repository', module, 'icd10_lookup']),
        clone_root_token=str(index % 2 + 1) * 64, source_sha=subject.SOURCE_SHA,
        source_manifest_sha256='2' * 64, candidate_sha256=subject.q.CANDIDATE_HASH,
        payload_sha256=subject.PAYLOAD_HASH, interpreter_sha256='3' * 64,
        completion='completed', classification='nonreader', reason='completed', returncode=0,
        root_identity_verified=True, total_processes=1, cleanup_verified=True,
        root_reaped=True, active_processes=0, screen_clean=True, capture_read_verified=True,
        call_wall_seconds=0.2, owned_wall_seconds=0.1, tree_cpu_seconds=0.05,
        analysis_seconds=0.01, stdout_bytes=0, stderr_bytes=32,
        stdout_sha256='4' * 64, stderr_sha256='5' * 64,
        test_count=1, failures=0, errors=0, skipped=0, expected_failures=0)


class ConcurrentReceiptControls(unittest.TestCase):
    def test_nonprefix_completion_and_two_unread_attempts_remain_inconclusive(self):
        from parallel_reader_scheduler import ScheduleResult, Observation
        rows = [ledger_row()]
        observed = Observation('test_b', 'icd10_lookup', 'nonreader', wall_seconds=0.1,
            tree_cpu_seconds=0.05, test_count=1, metadata=dict(rows[0]))
        schedule = ScheduleResult(False, (observed,), (), None, False,
                                  'whole_job_measurement_budget_exhausted', ())
        result = subject.arm_record('cap1', ('test_a', 'test_b'), (), rows, schedule, 1.0, True)
        self.assertEqual((False, 1, 3), (result['complete'], len(result['observations']), len(result['unstarted'])))
        self.assertEqual(rows[0]['pair_token'], result['observations'][0]['pair_token'])
        self.assertEqual(subject.encode_arm(result, ('test_a', 'test_b')), subject.encode_arm(
            json.loads(subject.encode_arm(result, ('test_a', 'test_b'))), ('test_a', 'test_b')))
        for change in ('duplicate', 'unknown', 'nan', 'bool', 'substitution', 'forged_complete'):
            damaged = copy.deepcopy(result)
            if change == 'duplicate': damaged['observations'].append(dict(rows[0]))
            if change == 'unknown': damaged['observations'][0]['private'] = 'SENTINEL'
            if change == 'nan': damaged['observations'][0]['owned_wall_seconds'] = float('nan')
            if change == 'bool': damaged['observations'][0]['test_count'] = True
            if change == 'substitution': damaged['observations'][0]['module'] = 'test_other'
            if change == 'forged_complete': damaged['complete'] = True
            with self.subTest(change=change), self.assertRaises(subject.q.Refused):
                subject.encode_arm(damaged, ('test_a', 'test_b'))
        for index, module in enumerate(('test_a', 'test_b')):
            row = ledger_row(module, index, index + 1)
            row.update(completion='incomplete', classification='unread', reason='cancelled',
                       screen_clean=False, capture_read_verified=False,
                       call_wall_seconds=None, owned_wall_seconds=None, tree_cpu_seconds=None)
            rows[index:index + 1] = [row]
        result = subject.arm_record('cap1', ('test_a', 'test_b'), (), rows,
            ScheduleResult(False, (), (), None, False, 'cleanup_unverified', ()), 1, False)
        self.assertEqual((2, 4, False), (len(result['observations']), len(result['unread']), result['complete']))


class CloneAdmissionControls(unittest.TestCase):
    def test_second_arm_never_clones_before_qualified_retained_baseline(self):
        for qualified, retained, extra_delta in ((False, True, False), (True, False, False),
                                                (True, True, True), (True, True, False)):
            with self.subTest(qualified=qualified, retained=retained, extra_delta=extra_delta), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                progress = {'arms': {'cap1': {'qualified': qualified}}, 'arm_receipts': {'cap1': retained}}
                expected = {subject.q.SUITE_PATH: subject.q.ORIGINAL_HASH, threshold_path(): subject.threshold.BASELINE_HASH}
                cloned = []
                def create(session, seed, repo, variant, inventory, candidate, **kwargs):
                    self.assertEqual('candidate', variant)
                    self.assertEqual(subject.SOURCE_SHA, kwargs['source_sha'])
                    self.assertNotIn('candidate_path', kwargs)
                    repo.mkdir()
                    target = {**inventory, subject.q.SUITE_PATH: subject.q.CANDIDATE_HASH}
                    if extra_delta: target[threshold_path()] = subject.threshold.CANDIDATE_HASH
                    return target
                with mock.patch.object(subject.maintainer, 'source_context', side_effect=create):
                    args = (object(), root, root, 'cap2', expected, b'lazy', progress, cloned,
                            lambda: None, types.SimpleNamespace(cloned=lambda repo: None, check=lambda: None))
                    if not qualified or not retained or extra_delta:
                        with self.assertRaises(subject.q.Refused): subject.prepare_arm(*args)
                        if not qualified or not retained: self.assertEqual([], list(root.iterdir()))
                    else:
                        result = subject.prepare_arm(*args)
                        self.assertEqual(['cap2-lane0', 'cap2-lane1'], [repo.name for repo in result])
                        self.assertEqual(2, len(cloned))


def threshold_path(): return 'tools/test_threshold_sheet.py'


class SemanticReferenceControls(unittest.TestCase):
    def test_reference_is_source_pinned_and_full_manifest_not_just_same_count(self):
        raw = Path(subject.__file__).with_name('current-parallel-reference.json').read_bytes()
        modules = tuple(sorted({row['module'] for row in json.loads(raw)['pairs']}))
        rows = subject.reference_rows(raw, modules)
        self.assertEqual(292, len(rows))
        self.assertEqual(146, len(modules))
        with self.assertRaises(subject.q.Refused): subject.reference_rows(raw + b' ', modules)
        with self.assertRaises(subject.q.Refused): subject.reference_rows(raw, tuple(sorted((*modules[1:], 'test_wrong'))))

    def test_cross_arm_semantics_ignore_capture_hashes_but_not_work_counts(self):
        from parallel_reader_scheduler import ScheduleResult, Observation
        rows = []
        for ordinal, lookup in enumerate(subject.LOOKUPS, 1):
            row = ledger_row('test_a', 0, ordinal)
            row.update(lookup=lookup, pair_index=ordinal - 1,
                       pair_token=subject.reader.token(['repository', 'test_a', lookup]))
            rows.append(row)
        observations = tuple(Observation('test_a', row['lookup'], 'nonreader', test_count=1,
            wall_seconds=0.1, tree_cpu_seconds=0.05, metadata=dict(row)) for row in rows)
        result = subject.arm_record('cap1', ('test_a',), (), rows,
            ScheduleResult(True, observations, (), None, False, None, ()), 1, True)
        reference = subject.signatures(rows)
        result['observations'][0]['stderr_sha256'] = 'f' * 64
        subject.qualify_record(result, ('test_a',), reference)
        self.assertTrue(result['qualified'])
        result['observations'][0]['test_count'] = 2
        with self.assertRaisesRegex(subject.q.Refused, 'parallel_work_changed'):
            subject.qualify_record(result, ('test_a',), reference)
        self.assertFalse(result['qualified'])


class TerminalControls(unittest.TestCase):
    def test_cli_refuses_private_arguments_and_broken_terminal_without_a_traceback(self):
        for sink in (None, OSError('PRIVATE_TERMINAL_SENTINEL')):
            output = io.StringIO(); errors = io.StringIO()
            with contextlib_redirect(output, errors):
                if sink:
                    with mock.patch.object(subject.q, 'emit', side_effect=sink): status = subject.main(['--PRIVATE_ARGUMENT'])
                else: status = subject.main(['--PRIVATE_ARGUMENT'])
            self.assertEqual(2, status)
            self.assertNotIn('PRIVATE_', output.getvalue() + errors.getvalue())
            self.assertNotIn('Traceback', output.getvalue() + errors.getvalue())

    def test_hard_deadline_covers_arm_and_terminal_publication_without_retry(self):
        for crossing in (None, 'parallel_arm', 'parallel_summary'):
            with self.subTest(crossing=crossing), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve(); observer = root / 'observer'; observer.mkdir()
                seed = root / 'seed'; seed.mkdir(); clock = [0.0]; cleaned = []
                output = io.StringIO(); errors = io.StringIO(); emitted = []
                original_emit = subject.q.emit
                def emit(event, **fields):
                    emitted.append((event, fields)); original_emit(event, **fields)
                    if event == crossing: clock[0] = 5401
                def execute(session, observer, seed, origin, progress, env):
                    progress.update(source_integrity_verified=True, output_contract_verified=True, receipt_verified=True)
                    progress['arms'] = {'cap1': {'qualified': True}, 'cap2': {'qualified': True}}
                    subject.q.emit('parallel_arm', synthetic=True)
                def session(*args, **kwargs):
                    self.assertIs(True, kwargs.get("compact"))
                    return types.SimpleNamespace(cleanup=lambda: cleaned.append('cleanup') or True)
                with contextlib_redirect(output, errors), mock.patch.object(subject.reader, 'authorize_route'), \
                     mock.patch.object(subject.q, 'environment_preflight'), mock.patch.object(subject.q, 'corpus_preflight'), \
                     mock.patch.object(subject.maintainer, 'environment_identity', return_value={}), \
                     mock.patch.object(subject.maintainer, 'validate_environment'), \
                     mock.patch.object(subject, 'ComparisonSession', side_effect=session), \
                     mock.patch.object(subject, 'execute', side_effect=execute, create=True), \
                     mock.patch.object(subject.q, 'emit', side_effect=emit), \
                     mock.patch.object(subject.time, 'time', return_value=1), \
                     mock.patch.object(subject.time, 'monotonic', side_effect=lambda: clock[0]):
                    code = subject.main(['--observer', str(observer), '--seed', str(seed), '--job-start-epoch', '1'])
                self.assertEqual(0 if crossing is None else 2, code)
                self.assertEqual(['cleanup'], cleaned)
                self.assertEqual(1, sum(event == 'parallel_summary' for event, fields in emitted))
                if crossing == 'parallel_arm':
                    self.assertEqual(('inconclusive', False), (emitted[-1][1]['status'], emitted[-1][1]['hard_budget_verified']))
                self.assertEqual('', errors.getvalue())


class AssembledArmControls(unittest.TestCase):
    def test_actual_scheduler_owner_capture_and_retained_receipt_guard_boundary(self):
        from current_parallel_runner import CurrentParallelRunner
        from test_current_parallel_runner import Factory, Clock, PAYLOAD, REFUSAL
        from dataclasses import replace
        for mutation in ('none', 'source', 'stale', 'unpinned', 'cleanup', 'identity', 'cleanup_publication'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve(); capture = root / 'capture'; capture.mkdir()
                lanes = (root / 'lane0', root / 'lane1')
                for lane in lanes: (lane / 'tools').mkdir(parents=True)
                clock = Clock(); factory = Factory(clock)
                session = types.SimpleNamespace(root=capture, deadline=clock() + 100,
                    hard_deadline=clock() + 120, runners=[], owners=[])
                resources = types.SimpleNamespace(runners=session.runners, check=lambda: None)
                manifest = {'modules': ('test_a',), 'pinned': ()}
                if mutation == 'stale': manifest['pinned'] = (('test_a', subject.LOOKUPS[0]),)
                if mutation == 'unpinned':
                    factory.plans = {('test_a', subject.LOOKUPS[0]): {'code': 1, 'stderr': REFUSAL.replace(b'test_alpha', b'test_a')}}
                reference = [dict(module='test_a', lookup=lookup, returncode=0, classification='nonreader',
                    test_count=3, failures=0, errors=0, skipped=1, expected_failures=0,
                    screen_clean=True, capture_read_verified=True, cleanup_verified=True) for lookup in subject.LOOKUPS]
                progress = {'phase': 'cap1_measurement', 'arms': {}, 'arm_receipts': {}}
                calls = []
                def guard():
                    calls.append('guard')
                    if mutation == 'source' and factory.owners: raise subject.q.Refused('source_refs_changed')
                original_schedule = subject.run_schedule
                def schedule(*args, **kwargs):
                    result = original_schedule(*args, **kwargs)
                    if mutation in ('cleanup', 'cleanup_publication'):
                        owner = factory.owners[0]
                        owner.result = replace(owner.result, snapshot=replace(owner.result.snapshot, cleanup_verified=False))
                    elif mutation == 'identity':
                        owner = factory.owners[0]
                        owner.result = replace(owner.result, stdout_path=str(capture / 'substituted.bin'))
                    return result
                def publish(*args, **kwargs):
                    if mutation == 'cleanup_publication': raise subject.q.Refused('audit_receipt_limit')
                def make(**kwargs):
                    return CurrentParallelRunner(**kwargs, owner_factory=factory, clock=clock,
                        disk_usage=lambda path: types.SimpleNamespace(free=2 ** 40))
                with mock.patch('current_parallel_runner.CurrentParallelRunner', side_effect=make), \
                     mock.patch.object(subject, 'run_schedule', side_effect=schedule), \
                     mock.patch.object(subject.q, 'emit', side_effect=publish), \
                     mock.patch.object(subject, 'PAYLOAD_HASH', subject.q.digest(PAYLOAD.encode())), \
                     mock.patch.object(subject.time, 'monotonic', clock), mock.patch.object(subject.time, 'sleep', clock.sleep), \
                     contextlib_redirect(io.StringIO(), io.StringIO()):
                    args = (session, lanes, 'cap1', manifest, {'source': 'a' * 64}, PAYLOAD,
                            reference, progress, guard, resources, {'SYSTEMROOT': 'synthetic-system'})
                    if mutation != 'none':
                        with self.assertRaises(subject.q.Refused): subject.measure_arm(*args)
                    else: subject.measure_arm(*args)
                self.assertEqual(2, len(progress['arms']['cap1']['observations']))
                self.assertEqual(mutation == 'none', progress['arms']['cap1']['qualified'])
                self.assertTrue(progress['arm_receipts']['cap1'])
                self.assertTrue((capture / 'cap1-receipt.json').is_file())
                self.assertEqual(1, factory.maximum)
                self.assertEqual(2, len(factory.owners))
                record = json.loads((capture / 'cap1-receipt.json').read_bytes())
                self.assertEqual([], record['unstarted'])
                if mutation in ('stale', 'unpinned'):
                    self.assertEqual('parallel_pin_sets_changed', progress['failure_context']['reason'])
                    key = 'stale_pins' if mutation == 'stale' else 'unpinned_readers'
                    self.assertEqual([subject.reader.token(['repository', 'test_a', subject.LOOKUPS[0]])], record['pin_sets'][key])
                if mutation in ('cleanup', 'identity', 'cleanup_publication'):
                    self.assertEqual('parallel_cleanup_unverified', progress['failure_context']['reason'])
                    self.assertTrue(record['scheduler_observations'][0]['cleanup_verified'])
                    self.assertFalse(record['observations'][0]['cleanup_verified'])
                    self.assertEqual([record['observations'][0]['pair_token']], record['unread'])
                if mutation != 'none':
                    with self.assertRaisesRegex(subject.q.Refused, '^parallel_baseline_not_qualified$'):
                        subject.prepare_arm(session, root, root, 'cap2', {}, b'', progress, [], lambda: None, resources)


class AssembledRouteControls(unittest.TestCase):
    def test_full_fixed_population_route_uses_four_lazy_only_lanes_and_584_bound_launches(self):
        import contextlib
        import os
        from current_parallel_runner import CurrentParallelRunner
        from test_current_parallel_runner import Factory, Clock, PAYLOAD
        from test_reader_attribution import synthetic_check
        import current_parallel_native_controls as dual
        import current_parallel_runner as runner_module
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            root = Path(directory).resolve(); observer = root / 'observer'; seed = root / 'seed'
            evidence = root / 'evidence'; lanes_root = root / 'lanes'
            for path in (observer / 'diagnostics', seed / 'tools', evidence, lanes_root): path.mkdir(parents=True)
            original = b'import icd10_lookup\n'; candidate = original + b'# lazy synthetic fixture\n'
            names = ['test_suite_ids', 'test_threshold_sheet'] + ['test_item_%03d' % index for index in range(144)]
            sources = {name + '.py': original for name in names}
            sources.update({name + '.py': b'' for name in (*subject.LOOKUPS, 'code_set_database_reader_check',
                                                         'test_code_set_database_reader_check')})
            sources.update({'helper_%03d.py' % index: b'' for index in range(469 - len(sources))})
            for name, raw in sources.items(): (seed / 'tools' / name).write_bytes(raw)
            expected = {'tools/' + name: subject.q.digest(raw) for name, raw in sources.items()}
            (observer / 'diagnostics/current-parallel-budget.json').write_text(json.dumps(subject.BUDGET))
            (observer / 'diagnostics/current-parallel-reference.json').write_bytes(b'{}')
            clock = Clock(); factory = Factory(clock)
            session = types.SimpleNamespace(root=evidence, deadline=clock() + 5100, hard_deadline=clock() + 5400,
                runners=[], owners=[], command_attempts=0, command_active=False,
                git=lambda repo, *args: '\n'.join(subject.OBSERVER_PATHS) if args[0] == 'diff' else '')
            check = synthetic_check(); check._SUBPROCESS = PAYLOAD
            cls = type(subject.reader.CLASS_ID.rsplit('.', 1)[-1], (), {'__module__': 'test_code_set_database_reader_check'})
            test_module = types.SimpleNamespace(**{cls.__name__: cls})
            planted_sources = {lookup + '.py': b'' for lookup in subject.LOOKUPS}
            planted_sources.update({'test_plant_%d.py' % index: original for index in range(11)})
            modules = tuple(sorted(names)); manifest_hash = subject.reader.token(
                [['repository', module, lookup] for module in modules for lookup in subject.LOOKUPS])
            original_population = subject.reader.source_population
            original_read = subject.q.read_reviewed_bytes
            def population(*args):
                result = original_population(*args)
                self.assertEqual(469, result['source_file_count']); self.assertEqual(modules, result['modules'])
                return result
            reference = [{'module': module, 'lookup': lookup, 'returncode': 0, 'classification': 'nonreader',
                'test_count': 3, 'failures': 0, 'errors': 0, 'skipped': 1, 'expected_failures': 0,
                'screen_clean': True, 'capture_read_verified': True, 'cleanup_verified': True}
                for module in modules for lookup in subject.LOOKUPS]
            preparations = []
            def clone(session, seed, repo, variant, source, raw, **options):
                preparations.append(repo.name); (repo / 'tools').mkdir(parents=True)
                for name, content in sources.items():
                    (repo / 'tools' / name).write_bytes(raw if 'tools/' + name == subject.q.SUITE_PATH else content)
                check.__file__ = str(lanes_root / 'cap1-lane0' / subject.reader.AUDIT_PATH)
                test_module.__file__ = str(lanes_root / 'cap1-lane0/tools/test_code_set_database_reader_check.py')
                return {**source, subject.q.SUITE_PATH: subject.q.digest(raw)}
            patches = [(subject.q, 'ORIGINAL_HASH', subject.q.digest(original)),
                (subject.q, 'CANDIDATE_HASH', subject.q.digest(candidate)),
                (subject.threshold, 'BASELINE_HASH', subject.q.digest(original)),
                (subject.reader, 'AUDIT_HASH', subject.q.digest(b'')), (subject.reader, 'TEST_HASH', subject.q.digest(b'')),
                (subject, 'PAYLOAD_HASH', subject.q.digest(PAYLOAD.encode())), (subject, 'PAIR_MANIFEST', manifest_hash),
                (subject.q, 'first_clean', lambda *a, **k: None), (subject.q, 'inventory', lambda *a, **k: {}),
                (subject.q, 'raw_source_inventory', lambda *a: expected), (subject.q, 'original_payload', lambda *a: PAYLOAD),
                (subject.q, 'read_reviewed_bytes', lambda path, digest: candidate if path == observer / subject.q.SUITE_PATH
                    else original_read(path, digest)), (subject.q, 'verify_sources', lambda *a, **k: None),
                (subject.contract, 'scan', lambda *a: None), (subject.maintainer, 'generated_guard', lambda *a: None),
                (subject.q, 'validate_owner_controls', lambda *a: None), (subject.q, 'verify_probe', lambda *a: None),
                (subject.reader, 'verify_retained_controls', lambda *a: None),
                (subject.threshold, 'private_command', lambda *a: ({'returncode': 0, 'stderr': ''}, b'{}\n')),
                (dual, 'read_receipt', lambda *a: {'status': 'passed', 'process_cleanup_verified': True}),
                (subject.maintainer, 'workspace_clone_root', lambda *a: lanes_root),
                (subject.maintainer, 'source_context', clone), (subject.maintainer, 'verify_hook_location', lambda *a: None),
                (subject.maintainer, 'behavior_controls', lambda *a: None), (subject.maintainer, 'explicit_controls', lambda *a: None),
                (subject.q, 'parse_child', lambda *a: {'outside_checkout_temp': True, 'temp_environment_unchanged': True}),
                (subject.reader, 'planted_sources', lambda *a: planted_sources),
                (subject.reader, 'source_population', population),
                (subject, 'observe_planted', lambda *a: {'complete': True, 'pairs': [{}] * 22}),
                (subject, 'reference_rows', lambda *a: reference),
                (subject.importlib, 'import_module', lambda name: check if name == 'code_set_database_reader_check' else test_module),
                (subject.shutil, 'disk_usage', lambda path: types.SimpleNamespace(free=2 ** 50)),
                (subject.time, 'monotonic', clock), (subject.time, 'sleep', clock.sleep)]
            for obj, name, value in patches: stack.enter_context(mock.patch.object(obj, name, value))
            stack.enter_context(mock.patch.object(runner_module, 'CurrentParallelRunner', side_effect=lambda **kwargs:
                CurrentParallelRunner(**kwargs, owner_factory=factory, clock=clock)))
            stack.enter_context(contextlib_redirect(io.StringIO(), io.StringIO()))
            progress = {'arms': {}, 'arm_receipts': {}, 'environment_sha256': 'a' * 64}
            environment = {key: value for key, value in os.environ.items() if not key.upper().startswith(('PYTHON', 'CLINICAL_'))}
            environment.update(GITHUB_SHA='a' * 40, GITHUB_RUN_ID='1')
            stack.enter_context(mock.patch.dict(os.environ, environment, clear=True))
            subject.execute(session, observer, seed, subject.time.time(), progress, environment)
            self.assertEqual(['cap1-lane0', 'cap1-lane1', 'cap2-lane0', 'cap2-lane1'], preparations)
            self.assertEqual(584, len(factory.owners)); self.assertEqual(2, factory.maximum)
            self.assertTrue(all(progress['arms'][arm]['qualified'] for arm in ('cap1', 'cap2')))
            self.assertTrue(progress['source_integrity_verified'] and progress['output_contract_verified'] and progress['receipt_verified'])


def contextlib_redirect(output, errors):
    import contextlib
    stack = contextlib.ExitStack(); stack.enter_context(contextlib.redirect_stdout(output))
    stack.enter_context(contextlib.redirect_stderr(errors)); return stack


"""Portable Session.run/cleanup controls; only injected owners ever execute.

These classes can be appended to the comparison driver's portable tests.
Imports load diagnostic definitions only, never application test modules.
"""
from contextlib import ExitStack
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

import measure_lazy_suite_ids as serial_resource_subject


class SerialResourceFakeOwner:
    def __init__(self, report, *, cancel_errors=(), completed=False):
        report.mkdir()
        self.stdout_path = report / 'stdout.bin'
        self.stderr_path = report / 'stderr.bin'
        self.stdout_path.write_bytes(b'synthetic output\n')
        self.stderr_path.write_bytes(b'synthetic error\n')
        self.cancel_errors = list(cancel_errors)
        self.cancel_calls = []
        self.finish_calls = []
        self.poll_count = 0
        self.completed = completed
        self.result = None

    def poll(self):
        self.poll_count += 1
        done = self.completed or self.poll_count > 1
        return types.SimpleNamespace(root_reaped=done, active_processes=0 if done else 1)

    def _result(self, reason):
        self.result = types.SimpleNamespace(reason=reason,
            stdout_path=str(self.stdout_path), stderr_path=str(self.stderr_path),
            snapshot=types.SimpleNamespace(cleanup_verified=True, root_exit_code=7,
                wall_seconds=0.75, tree_cpu_seconds=0.25))
        return self.result

    def finish(self, *, timeout):
        self.finish_calls.append(timeout)
        return self._result('completed')

    def cancel(self, reason, *, timeout):
        self.cancel_calls.append((reason, timeout))
        if self.cancel_errors:
            raise self.cancel_errors.pop(0)
        return self._result(reason)


class SerialResourceHookControls(unittest.TestCase):
    def environment(self, session_type=None, *, cancel_errors=(), completed=False,
                    free_bytes=None, clock_values=None):
        q = serial_resource_subject
        stack = ExitStack()
        self.addCleanup(stack.close)
        directory = stack.enter_context(tempfile.TemporaryDirectory(
            prefix='synthetic-serial-', dir=Path(__file__).resolve().parent))
        root = Path(directory).resolve()
        captures = root / 'captures'; captures.mkdir()
        launches, owners, sleeps = [], [], []
        def start(argv, **kwargs):
            launches.append((argv, kwargs))
            owner = SerialResourceFakeOwner(Path(kwargs['report_dir']),
                cancel_errors=cancel_errors, completed=completed)
            owners.append(owner)
            return owner
        stack.enter_context(mock.patch.object(q.WindowsJobProbe, 'start', side_effect=start))
        stack.enter_context(mock.patch.object(q.shutil, 'which', return_value=str(root / 'git')))
        free = iter(free_bytes) if free_bytes is not None else None
        stack.enter_context(mock.patch.object(q.shutil, 'disk_usage',
            side_effect=lambda path: types.SimpleNamespace(free=next(free) if free else 10 ** 15)))
        clock = iter(clock_values) if clock_values is not None else None
        stack.enter_context(mock.patch.object(q, 'time', types.SimpleNamespace(
            monotonic=lambda: next(clock) if clock else 100,
            sleep=lambda seconds: sleeps.append(seconds))))
        session = (session_type or q.Session)(captures, 200)
        return session, root, launches, owners, sleeps

    def test_default_serial_route_keeps_result_git_resolution_and_retained_owner(self):
        session, root, launches, owners, sleeps = self.environment()
        result = session.run(['git', 'status'], root)
        self.assertEqual(dict(returncode=7, stdout='synthetic output\n',
            stderr='synthetic error\n', wall_seconds=0.75, tree_cpu_seconds=0.25,
            stdout_path=str(root / 'captures/command-0001/stdout.bin'),
            stderr_path=str(root / 'captures/command-0001/stderr.bin'),
            cleanup_verified=True), result)
        self.assertEqual([str(root / 'git'), 'status'], launches[0][0])
        self.assertEqual(str(root), launches[0][1]['cwd'])
        self.assertEqual([0.02], sleeps)
        self.assertEqual([5], owners[0].finish_calls)
        self.assertEqual([], owners[0].cancel_calls)
        self.assertEqual([owners[0]], session.owners)
        self.assertTrue(session.cleanup())
        self.assertEqual([], owners[0].cancel_calls)

    def test_live_hook_refusal_cancels_exact_registered_owner_and_keeps_primary_error(self):
        q = serial_resource_subject
        primary = q.Refused('synthetic_clone_reserve_exhausted')
        seen = []
        class Guarded(q.Session):
            def _check_resources(inner):
                seen.append(tuple(inner.owners))
                raise primary
        session, root, launches, owners, sleeps = self.environment(Guarded)
        previous = SerialResourceFakeOwner(root / 'previous')
        session.owners.append(previous)
        with self.assertRaises(q.Refused) as caught:
            session.run(['synthetic-command'], root)
        self.assertIs(primary, caught.exception)
        self.assertEqual([(previous, owners[0])], seen)
        self.assertEqual([('resource_check_refused', 5)], owners[0].cancel_calls)
        self.assertEqual([], previous.cancel_calls)
        self.assertEqual([], owners[0].finish_calls)
        self.assertEqual([], sleeps)
        self.assertEqual([previous, owners[0]], session.owners)
        self.assertTrue(session.cleanup())

    def test_default_serial_disk_capture_and_budget_refusals_remain_equivalent(self):
        q = serial_resource_subject
        cases = (
            ('disk', {'free_bytes': (10 ** 15, 0)},
             'capture_or_disk_reserve_exhausted', 'capture_or_disk_reserve_exhausted'),
            ('capture', {},
             'capture_or_disk_reserve_exhausted', 'capture_or_disk_reserve_exhausted'),
            ('budget', {'clock_values': (100, 100, 200)},
             'global_budget_exhausted', 'whole_job_budget_exhausted'),
        )
        for label, settings, refusal, cancellation in cases:
            with self.subTest(route=label):
                session, root, launches, owners, sleeps = self.environment(**settings)
                with mock.patch.dict(q.BUDGET,
                    {'max_capture_bytes': 4} if label == 'capture' else {}):
                    with self.assertRaisesRegex(q.Refused, '^' + refusal + '$'):
                        session.run(['synthetic-command'], root)
                self.assertEqual([(cancellation, 5)], owners[0].cancel_calls)
                self.assertEqual([], owners[0].finish_calls)
                self.assertEqual([owners[0]], session.owners)
                self.assertTrue(session.cleanup())

    def test_hook_runs_for_each_poll_including_terminal_before_finish(self):
        q = serial_resource_subject
        seen = []
        class Guarded(q.Session):
            def _check_resources(inner):
                owner = inner.owners[-1]
                seen.append((owner.poll_count, tuple(owner.finish_calls)))
        session, root, launches, owners, sleeps = self.environment(Guarded)
        result = session.run(['synthetic-command'], root)
        self.assertEqual((7, 'synthetic output\n', True),
            (result['returncode'], result['stdout'], result['cleanup_verified']))
        self.assertEqual([(1, ()), (2, ())], seen)
        self.assertEqual([5], owners[0].finish_calls)

    def test_terminal_poll_still_refuses_instead_of_publishing_completed_command(self):
        q = serial_resource_subject
        class Guarded(q.Session):
            def _check_resources(inner):
                raise q.Refused('synthetic_terminal_reserve_exhausted')
        session, root, launches, owners, sleeps = self.environment(Guarded, completed=True)
        with self.assertRaisesRegex(q.Refused, '^synthetic_terminal_reserve_exhausted$'):
            session.run(['synthetic-command'], root)
        self.assertEqual([('resource_check_refused', 5)], owners[0].cancel_calls)
        self.assertEqual([], owners[0].finish_calls)
        self.assertEqual([owners[0]], session.owners)
        self.assertTrue(session.cleanup())

    def test_cancel_failure_preserves_refusal_and_cleanup_retries_retained_owner(self):
        q = serial_resource_subject
        class Guarded(q.Session):
            def _check_resources(inner):
                raise primary
        for cancellation_error in (OSError('synthetic cancellation failure'),
                                   KeyboardInterrupt('synthetic cancellation interruption')):
            with self.subTest(cancellation_error=type(cancellation_error).__name__):
                primary = q.Refused('synthetic_evidence_reserve_exhausted')
                session, root, launches, owners, sleeps = self.environment(Guarded,
                    cancel_errors=(cancellation_error, OSError('synthetic cleanup failure')))
                with self.assertRaises(q.Refused) as caught:
                    session.run(['synthetic-command'], root)
                self.assertIs(primary, caught.exception)
                self.assertEqual([owners[0]], session.owners)
                self.assertIsNone(owners[0].result)
                self.assertFalse(session.cleanup())
                self.assertEqual([owners[0]], session.owners)
                self.assertTrue(session.cleanup())
                self.assertEqual([('resource_check_refused', 5),
                    ('coordinator_cleanup', 5), ('coordinator_cleanup', 5)],
                    owners[0].cancel_calls)
                self.assertEqual([], owners[0].finish_calls)



class CloneVolumeHookControl(unittest.TestCase):
    environment = SerialResourceHookControls.environment
    def test_actual_comparison_callback_refuses_live_clone_volume_and_keeps_cleanup(self):
        session, root, launches, owners, _ = self.environment(
            session_type=lambda capture, deadline: subject.ComparisonSession(capture, deadline, subject.time.monotonic() + 600))
        session.deadline = subject.time.monotonic() + 600
        seed = root / 'seed'; seed.mkdir(); (seed / 'file').write_bytes(b'x')
        identities = lambda path: (1 if path == session.root else 2, path.stat().st_ino)
        with mock.patch.object(subject.ResourcePlan, 'identity', side_effect=identities), \
             mock.patch.object(subject.shutil, 'disk_usage', side_effect=lambda path:
                types.SimpleNamespace(free=0 if path == root and session.command_active else 2 ** 50)), \
             contextlib_redirect(io.StringIO(), io.StringIO()):
            resources = subject.ResourcePlan(session, seed, root)
            session.resource_check = resources.check
            with self.assertRaisesRegex(subject.q.Refused, '^parallel_disk_admission_exhausted$'):
                session.run(['git', 'clone'], root)
            self.assertEqual(1, len(launches)); self.assertEqual(1, session.command_attempts)
            self.assertFalse(session.command_active)
            self.assertEqual([('resource_check_refused', 5)], owners[0].cancel_calls)
            self.assertIs(owners[0], session.owners[0]); self.assertTrue(session.cleanup())


if __name__ == '__main__': unittest.main()
