"""Portable current-pair admission tests; synthetic data, no application suite."""
import json
import re
import time
import tempfile
from pathlib import Path
import unittest
from unittest import mock

import measure_maintainer_pair as m


PIN = '08db6360b453c2bf969a686f62f0477184d06351'
OBSERVER = 'a' * 40
RUN_ID = '12345'


def passing_receipt():
    return {
        'variant': 'baseline', 'source_sha': PIN,
        'observer_sha': OBSERVER, 'run_id': RUN_ID,
        'safe_to_continue': True, 'all_commands_passed': True,
        'source_integrity_verified': True, 'process_cleanup_verified': True,
        'output_contract_verified': True, 'hard_budget_verified': True,
        'environment': {
            'image': {'ImageOS': 'win25', 'ImageVersion': '20261014.91.1',
                      'RUNNER_OS': 'Windows', 'RUNNER_ARCH': 'X64'},
            'python': '3.14.4', 'interpreter_build_sha256': 'c' * 64,
            'cpu_count': 4, 'default_workers': 3},
        'discovery': {'test_count': 8487,
                      'sorted_ids_sha256': '2ddedf085b83618b1d059976838e80392c08b80d13ab40d954f887f258cb76a9',
                      'module_test_count': 1, 'loader_error_count': 0, 'executed_test_count': 0,
                      'ids_encoding': 'sorted JSON array, ASCII escaped, compact'},
        'unit_discovery': {
            'test_count': 8487, 'unit_count': 1373,
            'sorted_ids_sha256': '2ddedf085b83618b1d059976838e80392c08b80d13ab40d954f887f258cb76a9',
            'unit_names_sha256': '0611deba35e93059a153e542142e297b31acefa18bac6fdca98bfc86ca9219d9',
            'module_test_count': 1, 'new_module_test_count': 12,
            'new_module_ids_sha256': '61758003177b4195d5a753d13b5e2a9ef6f824083595474408f2f514ad89e6a8',
            'loader_error_count': 0, 'executed_test_count': 0,
            'units_derived_from_actual_objects': True, 'observed_baseline_count_corroborated': True},
        'behavior_control_ids': sorted(m.q.CONTROL_IDS),
        'command_returncodes': [
            ['phi_layers', 0], ['suite', 0], ['publication_measurements', 0],
            ['threshold_sheet', 0], ['phi_shape_only', 0]],
        'accounting': {'discovered': 8487, 'unaccounted': 0, 'jobs': 3, 'cpu_count': 4,
                       'weights': 'equal', 'returncode': 0, 'successful': True,
                       'internal_accounting': True, 'independent_executed_id_manifest': False,
                       'skips': 'not separately exposed', 'expected_failures': 'not separately exposed',
                       'critical_unit_token': 'e' * 64, 'critical_unit_seconds': 1.25,
                       'suite_reported_wall_seconds': 2.0, 'next_worker_seconds': 1.0},
    }


class CurrentPairReceipt(unittest.TestCase):
    def test_receipt_keeps_complete_native_accounting_and_finite_timings(self):
        good = passing_receipt()
        accounting = good['accounting']
        mutations = [accounting | {'unexpected': 'value'}]
        for key in accounting:
            mutations.append({name: value for name, value in accounting.items() if name != key})
            mutations.append(accounting | {key: None})
        for key in ('critical_unit_seconds', 'suite_reported_wall_seconds', 'next_worker_seconds'):
            for value in (-1.0, True, '1.0', float('nan'), float('inf'), 1e10):
                mutations.append(accounting | {key: value})
        mutations.extend(accounting | {key: value} for key, value in (
            ('suite_reported_wall_seconds', 0.0), ('critical_unit_token', 'invalid'),
            ('skips', 0), ('expected_failures', 0)))
        with mock.patch.dict(m.os.environ, {'GITHUB_SHA': OBSERVER, 'GITHUB_RUN_ID': RUN_ID}):
            self.assertEqual(m.baseline_receipt(json.dumps(good)), good)
            for bad in mutations:
                with self.subTest(accounting=bad), self.assertRaises(m.q.Refused):
                    m.baseline_receipt(json.dumps(good | {'accounting': bad}))

    def test_candidate_environment_must_match_before_any_owner_or_session(self):
        from types import SimpleNamespace
        from contextlib import ExitStack
        good = passing_receipt()
        identity = good['environment']
        cases = [identity,
                 identity | {'image': identity['image'] | {'ImageVersion': '20261015.1'}},
                 identity | {'image': identity['image'] | {'ImageOS': 'win22'}},
                 identity | {'interpreter_build_sha256': 'd' * 64},
                 identity | {'python': '3.14.3'}, identity | {'image': {}},
                 identity | {'interpreter_build_sha256': 'invalid'},
                 {key: value for key, value in identity.items() if key != 'python'}]
        for current in cases:
            with self.subTest(environment=current), tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
                root = Path(directory)
                observer, seed = root / 'observer', root / 'seed'
                observer.mkdir()
                seed.mkdir()
                env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push', 'GITHUB_REF': m.q.BRANCH,
                       'GITHUB_RUN_ATTEMPT': '1', 'GITHUB_SHA': OBSERVER, 'GITHUB_RUN_ID': RUN_ID,
                       'GITHUB_OUTPUT': str(root / 'github-output'), 'BASELINE_RECEIPT': json.dumps(good)}
                evidence = passing_receipt()
                evidence['commands'] = [{'command': name, 'returncode': code}
                                        for name, code in evidence.pop('command_returncodes')]
                session = mock.Mock()
                session.cleanup.return_value = True
                stack.enter_context(mock.patch.object(m, 'os', SimpleNamespace(name='nt', environ=env)))
                stack.enter_context(mock.patch.object(m.platform, 'python_version', return_value='3.14.4'))
                stack.enter_context(mock.patch.object(m, 'environment_identity', return_value=current))
                stack.enter_context(mock.patch.object(m.q, 'environment_preflight'))
                stack.enter_context(mock.patch.object(m.q, 'corpus_preflight'))
                stack.enter_context(mock.patch.object(m.q, 'emit'))
                stack.enter_context(mock.patch.object(m.q, 'safe_exception'))
                owner = stack.enter_context(mock.patch.object(m.tempfile, 'mkdtemp', return_value=str(root / 'capture')))
                create = stack.enter_context(mock.patch.object(m, 'make_session', return_value=session))
                execute = stack.enter_context(mock.patch.object(m, 'execute', return_value=evidence))
                result = m.main(['--observer', str(observer), '--seed', str(seed), '--variant', 'candidate',
                                 '--job-start-epoch', str(time.time())])
                if current == identity:
                    self.assertEqual(result, 0)
                    owner.assert_called_once()
                    create.assert_called_once()
                    execute.assert_called_once()
                else:
                    self.assertEqual(result, 2)
                    owner.assert_not_called()
                    create.assert_not_called()
                    execute.assert_not_called()
                    self.assertEqual((root / 'github-output').read_text().splitlines()[:2],
                                     ['safe=false', 'passed=false'])

    def test_receipt_requires_complete_bounded_environment_identity(self):
        good = passing_receipt()
        identity = good['environment']
        mutations = [None, [], identity | {'unexpected': 'value'}]
        for key in identity:
            mutations.append({name: value for name, value in identity.items() if name != key})
            mutations.append(identity | {key: None})
        for key, values in (
                ('python', [1, True, ['3.14.4'], '', '3.12.14', '3.14.4\n']),
                ('interpreter_build_sha256', [1, True, [], '', 'z' * 64, 'A' * 64, 'a' * 63, 'a' * 65]),
                ('cpu_count', [True, '4', 3]), ('default_workers', [True, '3', 4])):
            mutations.extend(identity | {key: value} for value in values)
        image = identity['image']
        mutations.append(identity | {'image': image | {'unexpected': 'value'}})
        for key in image:
            mutations.append(identity | {'image': {name: value for name, value in image.items() if name != key}})
            for value in (None, 1, True, [], '', 'x' * 129, 'line\nbreak'):
                mutations.append(identity | {'image': image | {key: value}})
        mutations.extend(identity | {'image': image | {key: value}}
                         for key, value in (('RUNNER_OS', 'Linux'), ('RUNNER_ARCH', 'ARM64')))
        with mock.patch.dict(m.os.environ, {'GITHUB_SHA': OBSERVER, 'GITHUB_RUN_ID': RUN_ID}):
            self.assertEqual(m.baseline_receipt(json.dumps(good)), good)
            for bad in mutations:
                with self.subTest(environment=bad), self.assertRaises(m.q.Refused):
                    m.baseline_receipt(json.dumps(good | {'environment': bad}))

    def test_successful_baseline_publishes_complete_receipt_and_bad_prior_spends_nothing(self):
        from types import SimpleNamespace
        from contextlib import ExitStack
        for bad_prior in (False, True, 'incomplete_evidence'):
            with self.subTest(bad_prior=bad_prior), tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
                root = Path(directory)
                observer, seed = root / 'observer', root / 'seed'
                observer.mkdir()
                seed.mkdir()
                env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push', 'GITHUB_REF': m.q.BRANCH,
                       'GITHUB_RUN_ATTEMPT': '1', 'GITHUB_SHA': OBSERVER, 'GITHUB_RUN_ID': RUN_ID,
                       'GITHUB_OUTPUT': str(root / 'github-output')}
                prior = passing_receipt()
                prior['process_cleanup_verified'] = False
                env['BASELINE_RECEIPT'] = json.dumps(prior)
                evidence = passing_receipt()
                evidence['commands'] = [{'command': name, 'returncode': code}
                                        for name, code in evidence.pop('command_returncodes')]
                if bad_prior == 'incomplete_evidence':
                    del evidence['unit_discovery']
                session = mock.Mock()
                session.cleanup.return_value = True
                stack.enter_context(mock.patch.object(m, 'os', SimpleNamespace(name='nt', environ=env)))
                stack.enter_context(mock.patch.object(m.platform, 'python_version', return_value='3.14.4'))
                stack.enter_context(mock.patch.object(m, 'environment_identity', return_value=evidence['environment']))
                stack.enter_context(mock.patch.object(m.q, 'environment_preflight'))
                stack.enter_context(mock.patch.object(m.q, 'corpus_preflight'))
                stack.enter_context(mock.patch.object(m.q, 'emit'))
                stack.enter_context(mock.patch.object(m.q, 'safe_exception'))
                stack.enter_context(mock.patch.object(m.tempfile, 'mkdtemp', return_value=str(root / 'capture')))
                create = stack.enter_context(mock.patch.object(m, 'make_session', return_value=session))
                execute = stack.enter_context(mock.patch.object(m, 'execute', return_value=evidence))
                variant = 'candidate' if bad_prior is True else 'baseline'
                result = m.main(['--observer', str(observer), '--seed', str(seed), '--variant', variant,
                                 '--job-start-epoch', str(time.time())])
                if bad_prior is True:
                    self.assertEqual(result, 2)
                    create.assert_not_called()
                    execute.assert_not_called()
                elif bad_prior == 'incomplete_evidence':
                    self.assertEqual(result, 2)
                    self.assertEqual((root / 'github-output').read_text().splitlines()[:2],
                                     ['safe=false', 'passed=false'])
                else:
                    self.assertEqual(result, 0)
                    lines = (root / 'github-output').read_text().splitlines()
                    self.assertEqual(lines[:2], ['safe=true', 'passed=true'])
                    receipt = m.baseline_receipt(lines[2].removeprefix('receipt='))
                    self.assertEqual(receipt['source_sha'], PIN)
                    self.assertTrue(receipt['output_contract_verified'])
                    self.assertTrue(receipt['hard_budget_verified'])

    def test_candidate_requires_current_population_integrity_accounting_and_cleanup(self):
        good = passing_receipt()
        with mock.patch.dict(m.os.environ, {'GITHUB_SHA': OBSERVER, 'GITHUB_RUN_ID': RUN_ID}):
            self.assertEqual(m.baseline_receipt(json.dumps(good)), good)
            mutations = [dict(good, source_sha=m.q.BASE), dict(good, observer_sha='b' * 40),
                         dict(good, run_id='12346'), dict(good, variant='candidate')]
            for key in ('safe_to_continue', 'all_commands_passed', 'source_integrity_verified',
                        'process_cleanup_verified', 'output_contract_verified', 'hard_budget_verified'):
                for value in (False, None, 1):
                    mutations.append(dict(good, **{key: value}))
                missing = dict(good)
                del missing[key]
                mutations.append(missing)
            for key, value in (('discovered', 8300), ('unaccounted', 1), ('weights', 'recorded'),
                               ('returncode', 1), ('successful', False), ('jobs', 4)):
                mutations.append(dict(good, accounting=good['accounting'] | {key: value}))
            for key, value in (('test_count', 8300), ('unit_count', 1372), ('new_module_test_count', 11),
                               ('new_module_ids_sha256', 'f' * 64), ('units_derived_from_actual_objects', False)):
                mutations.append(dict(good, unit_discovery=good['unit_discovery'] | {key: value}))
            mutations.append(dict(good, command_returncodes=good['command_returncodes'][:-1]))
            mutations.append(dict(good, command_returncodes=list(reversed(good['command_returncodes']))))
            for bad in mutations:
                with self.subTest(bad=bad), self.assertRaises(m.q.Refused):
                    m.baseline_receipt(json.dumps(bad))
            for raw in (None, '', ' ' * 16385, json.dumps(good)[:-1] + ',"safe_to_continue":true}'):
                with self.assertRaises(m.q.Refused):
                    m.baseline_receipt(raw)


class CurrentPairSafety(unittest.TestCase):
    def test_input_guard_binds_raw_observer_and_seed_and_refuses_ref_drift(self):
        import generated_output_contract as contract
        session = mock.Mock(deadline=time.monotonic() + 30)
        observer, seed = Path('observer'), Path('seed')
        snapshots = {observer: 'observer refs', seed: 'seed refs'}
        session.git.side_effect = ['observer refs', 'seed refs']
        with mock.patch.dict(m.os.environ, {'GITHUB_SHA': OBSERVER}), \
             mock.patch.object(m.q, 'verify_sources') as sources, \
             mock.patch.object(contract, 'scan') as scan:
            m.verify_input_sources(session, observer, seed, {'observer': 'hash'}, {'seed': 'hash'}, snapshots, 1000)
            self.assertEqual(sources.call_args_list, [
                mock.call(session, observer, {'observer': 'hash'}, source_sha=OBSERVER),
                mock.call(session, seed, {'seed': 'hash'}, source_sha=PIN)])
            self.assertEqual(scan.call_count, 2)
            for call in scan.call_args_list:
                state = call.args[-1]
                self.assertEqual((state.marker, state.weights, state.sessions), ('absent', 'absent', 'optional'))
                self.assertEqual(state.max_job_seconds, 5400)
            session.git.side_effect = ['changed refs']
            with self.assertRaises(m.q.Refused):
                m.verify_input_sources(session, observer, seed, {}, {}, snapshots, 1000)

    def test_generated_guard_uses_current_source_and_detached_head(self):
        import generated_output_contract as contract
        session = mock.Mock(deadline=time.monotonic() + 30)
        session.run.return_value = {'returncode': 1, 'stdout': ''}
        repo, target, state = Path('synthetic'), {'source': 'hash'}, object()
        with mock.patch.object(m.q, 'verify_sources') as sources, \
             mock.patch.object(m, 'verify_refs') as refs, \
             mock.patch.object(contract, 'scan', return_value={'verified': True}) as scan:
            self.assertEqual(m.generated_guard(session, repo, target, True, state), {'verified': True})
            sources.assert_called_once_with(session, repo, target, True, source_sha=PIN)
            refs.assert_called_once_with(session, repo, source_sha=PIN)
            scan.assert_called_once_with(repo, target, session.deadline, state)
            session.run.return_value = {'returncode': 0, 'stdout': 'refs/heads/main\n'}
            with self.assertRaises(m.q.Refused):
                m.generated_guard(session, repo, target, True, state)

    def test_cleanup_cannot_approve_an_expired_hard_budget(self):
        from types import SimpleNamespace
        session = m.make_session(Path('synthetic'), 5100, 5400)
        pending = mock.Mock(result=None)
        pending.cancel.return_value = SimpleNamespace(snapshot=SimpleNamespace(cleanup_verified=True))
        session.owners = [pending]
        with mock.patch.object(m.time, 'monotonic', return_value=5398):
            self.assertTrue(session.cleanup())
        pending.cancel.assert_called_once_with('coordinator_cleanup', timeout=2)
        pending.cancel.reset_mock()
        with mock.patch.object(m.time, 'monotonic', return_value=5400):
            self.assertFalse(session.cleanup())
        pending.cancel.assert_not_called()


class CurrentPairRoute(unittest.TestCase):
    def test_current_source_pin_does_not_rewrite_historical_proof_or_lazy_bytes(self):
        root = Path(m.__file__).resolve().parent.parent
        self.assertEqual(m.SOURCE_SHA, PIN)
        self.assertEqual(m.q.BASE, '104ee03cd4d37519b12b3edbc4da5fbf31b631cf')
        self.assertEqual(m.q.digest((root / 'tools/test_suite_ids.py').read_bytes()),
                         'f2f97e56313d7f8957bec0bd20fd91c9efd8c48c44871c5c69056eb830d43275')

    def test_only_current_pair_can_start_and_candidate_requires_success(self):
        root = Path(m.__file__).resolve().parent.parent
        pair = (root / '.github/workflows/ci-parallel-proof.yml').read_text()
        discovery = (root / '.github/workflows/ci-checkpoint-discovery.yml').read_text()
        self.assertEqual(pair.split('on:\n', 1)[1].split('\npermissions:', 1)[0].strip(),
                         'push:\n    branches: [diagnostic/2013-parallel-proof-20261020]')
        self.assertEqual(discovery.split('on:\n', 1)[1].split('\npermissions:', 1)[0].strip(),
                         "push:\n    branches-ignore: ['**']\n    tags-ignore: ['**']")
        self.assertEqual(pair.count('ref: 08db6360b453c2bf969a686f62f0477184d06351'), 2)
        self.assertEqual(pair.count('timeout-minutes: 90'), 2)
        self.assertEqual(pair.count("python-version: '3.14.4'"), 2)
        self.assertIn("needs.baseline.result == 'success'", pair)
        self.assertIn("needs.baseline.outputs.safe == 'true' && needs.baseline.outputs.passed == 'true'", pair)
        self.assertEqual(pair.count('github.run_attempt == 1'), 2)
        self.assertEqual(re.findall(r'^  ([a-z_]+):$', pair.split('jobs:\n', 1)[1], re.MULTILINE),
                         ['baseline', 'candidate'])
        for forbidden in ('workflow_dispatch', 'strategy:', 'upload-artifact', 'continue-on-error', '--jobs'):
            self.assertNotIn(forbidden, pair)


if __name__ == '__main__':
    unittest.main()
