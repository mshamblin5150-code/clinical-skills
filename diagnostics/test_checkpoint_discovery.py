"""Portable synthetic controls for the fixed checkpoint discovery route."""
import math
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import copy
import contextlib
import io
from unittest import mock
from types import SimpleNamespace
import unittest

import diagnose_checkpoint_discovery as d


class CheckpointBudget(unittest.TestCase):
    def test_setup_is_charged_to_the_single_job_and_cleanup_is_reserved(self):
        self.assertEqual(d.budget_deadlines(1000, 1040, 20), (520, 580))
        self.assertEqual(d.budget_deadlines(1000, 1539, 20), (21, 81))
        for origin, wall, monotonic in ((1000, 1540, 20), (1000, 999, 20),
                                       (True, 1000, 20), (1000, math.inf, 20),
                                       (1000, 1000, math.nan), (None, 1000, 20)):
            with self.subTest(origin=origin, wall=wall, monotonic=monotonic):
                with self.assertRaises(d.q.Refused):
                    d.budget_deadlines(origin, wall, monotonic)

    def test_cleanup_is_bounded_by_the_original_hard_deadline(self):
        session = object.__new__(d.CheckpointSession)
        session.hard_deadline = 600
        complete = SimpleNamespace(snapshot=SimpleNamespace(cleanup_verified=True))
        retained = mock.Mock(result=complete)
        pending = mock.Mock(result=None)
        pending.cancel.return_value = complete
        session.owners = [retained, pending]
        with mock.patch.object(d.time, 'monotonic', return_value=598):
            self.assertTrue(session.cleanup())
        pending.cancel.assert_called_once_with('coordinator_cleanup', timeout=2)
        retained.cancel.assert_not_called()
        pending.cancel.reset_mock()
        with mock.patch.object(d.time, 'monotonic', return_value=600):
            self.assertFalse(session.cleanup())
        pending.cancel.assert_not_called()
        with mock.patch.object(d.time, 'monotonic', return_value=590):
            pending.cancel.side_effect = RuntimeError('private cleanup detail')
            self.assertFalse(session.cleanup())
        self.assertEqual(session.owners, [retained, pending])


class CheckpointRoute(unittest.TestCase):
    def test_only_first_push_on_the_established_branch_can_enter(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push',
               'GITHUB_REF': 'refs/heads/diagnostic/2013-parallel-proof-20261020',
               'GITHUB_RUN_ATTEMPT': '1'}
        self.assertIsNone(d.authorize_route('nt', '3.14.4', env))
        for key, value in (('GITHUB_ACTIONS', 'false'), ('GITHUB_EVENT_NAME', 'workflow_dispatch'),
                           ('GITHUB_EVENT_NAME', 'pull_request'), ('GITHUB_REF', 'refs/heads/diagnostic/2013-checkpoint-discovery-20261022'),
                           ('GITHUB_RUN_ATTEMPT', '2')):
            with self.subTest(key=key, value=value), self.assertRaises(d.q.Refused):
                d.authorize_route('nt', '3.14.4', env | {key: value})
        for system, version in (('posix', '3.14.4'), ('nt', '3.14.9'), ('nt', '3.10.11')):
            with self.assertRaises(d.q.Refused):
                d.authorize_route(system, version, env)

    def test_workflow_has_one_bounded_job_and_no_full_pair_or_upload_route(self):
        root = Path(d.__file__).resolve().parent.parent
        text = (root / '.github/workflows/ci-checkpoint-discovery.yml').read_text()
        self.assertEqual(text.count('runs-on: windows-latest'), 1)
        self.assertEqual(text.count('timeout-minutes: 10'), 1)
        self.assertEqual(text.count('github.run_attempt == 1'), 1)
        self.assertIn("python-version: '3.14.4'", text)
        self.assertIn('ref: 08db6360b453c2bf969a686f62f0477184d06351', text)
        self.assertIn("branches-ignore: ['**']", text)
        self.assertIn("tags-ignore: ['**']", text)
        self.assertIn('python observer/diagnostics/diagnose_checkpoint_discovery.py', text)
        self.assertLess(text.index('PROOF_JOB_START_EPOCH='), text.index('uses: actions/checkout'))
        self.assertEqual(text.count("GIT_CONFIG_VALUE_0: 'false'"), 2)
        self.assertEqual(text.count('fetch-depth: 0'), 2)
        self.assertEqual(text.count('persist-credentials: false'), 2)
        for forbidden in ('workflow_dispatch', 'upload-artifact', 'strategy:', 'measure_maintainer_pair.py',
                          'python observer/diagnostics/measure_lazy_suite_ids.py', 'tools/suite.py'):
            self.assertNotIn(forbidden, text)
        self.assertEqual(d.q.BASE, '104ee03cd4d37519b12b3edbc4da5fbf31b631cf')
        self.assertEqual(d.SOURCE_SHA, '08db6360b453c2bf969a686f62f0477184d06351')

    def test_established_branch_cannot_restart_discovery_or_the_consumed_pair(self):
        root = Path(d.__file__).resolve().parent.parent
        old = (root / '.github/workflows/ci-parallel-proof.yml').read_text()
        new = (root / '.github/workflows/ci-checkpoint-discovery.yml').read_text()
        self.assertEqual(d.BRANCH, d.q.BRANCH)
        self.assertEqual(new.split('on:\n', 1)[1].split('\npermissions:', 1)[0].strip(),
                         "push:\n    branches-ignore: ['**']\n    tags-ignore: ['**']")
        self.assertEqual(old.split('on:\n', 1)[1].split('\npermissions:', 1)[0].strip(),
                         "push:\n    branches-ignore: ['**']\n    tags-ignore: ['**']")
        self.assertNotIn(d.q.BASE, old)
        self.assertEqual(old.count('ref: ' + d.SOURCE_SHA), 2)

    def test_cli_refuses_unsupported_runtime_with_finite_summary(self):
        with mock.patch.object(d.platform, 'python_version', return_value='3.10.11'):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = d.main(['--observer', '/private/observer', '--seed', '/private/seed',
                             '--job-start-epoch', '1000'])
        rows = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(rc, 2)
        final = rows[-1]
        self.assertEqual(final['event'], 'checkpoint_discovery_summary')
        self.assertEqual(final['failure'], 'windows_python_pin_required')
        self.assertFalse(final['process_cleanup_verified'])
        self.assertFalse(final['source_integrity_verified'])
        self.assertEqual(final['status'], 'inconclusive')
        self.assertFalse(final['full_suite_execution'])
        self.assertNotIn('/private/', output.getvalue())

    def test_pre_suite_contract_never_requires_marker_or_weights(self):
        state = d.pre_suite_state(1000, ('test_tiny.Actual',), observed_epoch=1040)
        self.assertEqual((state.marker, state.weights, state.sessions), ('absent', 'absent', 'optional'))
        self.assertEqual(state.max_job_seconds, 600)
        self.assertEqual(state.units, ('test_tiny.Actual',))
        import generated_output_contract as contract
        contract.validate_state(state)

    def test_budget_and_source_allowlist_are_exact_without_repinning_old_routes(self):
        root = Path(d.__file__).resolve().parent.parent
        plan = json.loads((root / 'diagnostics/checkpoint-discovery-budget.json').read_text())
        d.validate_budget(plan)
        for change in ({'job_seconds': 601}, {'cleanup_reserve_seconds': 59}, {'schema_version': True},
                       {'source_sha': d.q.BASE}, {'unexpected': 'private'}):
            with self.assertRaises(d.q.Refused):
                d.validate_budget(plan | change)
        self.assertEqual(d.OBSERVER_PATHS - d.q.OBSERVER_PATHS, {
            '.github/workflows/ci-checkpoint-discovery.yml',
            'diagnostics/diagnose_checkpoint_discovery.py', 'diagnostics/test_checkpoint_discovery.py',
            'diagnostics/checkpoint-discovery-budget.json', 'diagnostics/checkpoint-discovery-spec.md'})
        self.assertNotEqual(d.OBSERVER_PATHS, d.q.OBSERVER_PATHS)


class FixedSource(unittest.TestCase):
    def test_checkpoint_context_keeps_history_and_historical_defaults_refuse_it(self):
        from test_source_context_real_git import LocalSession
        import measure_maintainer_pair as m
        with tempfile.TemporaryDirectory(prefix='checkpoint-git-') as name:
            root = Path(name)
            seed = root / 'seed'
            seed.mkdir()
            session = LocalSession()
            session.git(seed, 'init', '-b', 'main')
            session.git(seed, 'config', 'user.name', 'Synthetic Fixture')
            session.git(seed, 'config', 'user.email', 'fixture@example.invalid')
            (seed / 'tools').mkdir()
            (seed / 'tools/test_suite_ids.py').write_bytes(b'original\n')
            (seed / '.gitignore').write_bytes(b'__pycache__/\n')
            session.git(seed, 'add', '.')
            session.git(seed, 'commit', '-m', 'Synthetic ancestor')
            ancestor = session.git(seed, 'rev-parse', 'HEAD').strip()
            (seed / 'README.md').write_bytes(b'Synthetic checkpoint\n')
            session.git(seed, 'add', '.')
            session.git(seed, 'commit', '-m', 'Synthetic checkpoint')
            checkpoint = session.git(seed, 'rev-parse', 'HEAD').strip()
            expected = d.q.inventory(seed)
            for variant in ('baseline', 'candidate'):
                repo = root / variant
                target = m.source_context(session, seed, repo, variant, expected, b'lazy\n', source_sha=checkpoint)
                m.verify_refs(session, repo, source_sha=checkpoint)
                d.q.verify_sources(session, repo, target, variant == 'candidate', source_sha=checkpoint)
                self.assertEqual(session.git(repo, 'rev-list', 'HEAD').splitlines(), [checkpoint, ancestor])
                self.assertEqual(session.git(repo, 'diff', '--cached', '--name-only'), '')
                self.assertEqual(session.git(repo, 'diff', '--name-only', 'HEAD').splitlines(),
                                 ['tools/test_suite_ids.py'] if variant == 'candidate' else [])
                with self.assertRaisesRegex(d.q.Refused, 'source_refs_changed'):
                    m.verify_refs(session, repo)
                with self.assertRaisesRegex(d.q.Refused, 'measured_head_changed'):
                    d.q.verify_sources(session, repo, target, variant == 'candidate')
            self.assertEqual([row[-1] for row in session.first_status], [b'original\n', b'original\n'])
            with self.assertRaisesRegex(d.q.Refused, 'baseline_not_safe_or_passed'):
                m.baseline_receipt(json.dumps({'variant': 'baseline', 'safe_to_continue': True,
                                              'all_commands_passed': True, 'source_sha': checkpoint}))


class DiscoveryIdentity(unittest.TestCase):
    def test_real_child_groups_actual_objects_and_never_runs_discovered_bodies(self):
        with tempfile.TemporaryDirectory(prefix='checkpoint-discovery-') as name:
            repo = Path(name)
            tools = repo / 'tools'
            tools.mkdir()
            # This deliberately makes a case's reported ID differ from its class.
            (tools / 'suite.py').write_text(
                'import unittest\nfrom types import SimpleNamespace\n'
                'def _test_cases(item):\n'
                '    if isinstance(item, unittest.TestSuite):\n'
                '        for child in item: yield from _test_cases(child)\n'
                '    else: yield item\n'
                'def _units(tests):\n'
                '    groups = {}\n'
                '    for test in tests: groups.setdefault(type(test), []).append(test)\n'
                '    return [SimpleNamespace(name=c.__module__+"."+c.__qualname__, tests=t) for c,t in groups.items()]\n')
            (tools / 'test_tiny.py').write_text(
                'import unittest\nfrom pathlib import Path\n'
                'class ActualClass(unittest.TestCase):\n'
                '    def id(self): return "reported.Other.test_alias"\n'
                '    def test_body(self): Path(__file__).with_suffix(".executed").touch()\n')
            result = subprocess.run([sys.executable, str(Path(d.__file__).resolve()), '--child', 'units',
                                     '--repo', str(repo)], cwd=tools, text=True, capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            row = d.q.parse_child({'returncode': result.returncode, 'stdout': result.stdout})
            self.assertEqual(row['test_ids'], ['reported.Other.test_alias'])
            self.assertEqual(row['unit_names'], ['test_tiny.ActualClass'])
            self.assertEqual(row['new_module_test_ids'], [])
            self.assertFalse((tools / 'test_tiny.executed').exists())
            # Dropping the actual object is not a valid complete unit grouping.
            suite_path = tools / 'suite.py'
            suite_path.write_text(suite_path.read_text().replace('groups.items()]', 'groups.items()][1:]'))
            changed = subprocess.run([sys.executable, '-B', str(Path(d.__file__).resolve()), '--child', 'units',
                                      '--repo', str(repo)], cwd=tools, text=True, capture_output=True, timeout=15)
            self.assertNotEqual(changed.returncode, 0)
            self.assertFalse((tools / 'test_tiny.executed').exists())

    def test_complete_identity_requires_independent_ids_and_exact_new_object_membership(self):
        new_ids = sorted('test_medatrax_fill.FillCommand.' + name for name in (
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
            'test_generated_script_executes_and_preflights_all_targets'))
        ids = sorted(new_ids + ['test_suite_ids.Sample.test_a'] +
                     ['test_synthetic.Sample.test_%04d' % i for i in range(8474)])
        row = {'test_ids': ids, 'unit_names': ['test_medatrax_fill.FillCommand', 'test_suite_ids.Sample',
                                             'test_synthetic.Sample'], 'new_module_test_ids': new_ids,
               'executed_test_count': 0, 'loader_errors': 0}
        independent = {'test_count': 8487, 'sorted_ids_sha256': d.q.digest(json.dumps(ids, separators=(',', ':')).encode()),
                       'module_test_count': 1, 'loader_error_count': 0, 'executed_test_count': 0,
                       'ids_encoding': 'sorted JSON array, ASCII escaped, compact'}
        result = lambda value: {'returncode': 0, 'stdout': 'LAZY_PROOF_RESULT:' + json.dumps(value)}
        accepted = d.validate_identity(result(row), independent)
        self.assertEqual(accepted['ids'], tuple(ids))
        self.assertEqual(accepted['units'], tuple(row['unit_names']))
        self.assertEqual(accepted['public']['new_module_test_count'], 12)
        self.assertEqual(accepted['public']['test_count'], 8487)
        for changes in ({'loader_errors': 1}, {'loader_errors': False}, {'executed_test_count': 1},
                        {'unit_names': row['unit_names'] * 2}, {'new_module_test_ids': new_ids[:-1]},
                        {'test_ids': ids[:-1]}, {'test_ids': ids + [ids[-1]]}, {'extra': 'private'},
                        {'unit_names': ['private/path']}, {'test_ids': list(reversed(ids))}):
            with self.subTest(changes=tuple(changes)), self.assertRaises(d.q.Refused):
                d.validate_identity(result(row | changes), independent)
        for changes in ({'test_count': True}, {'loader_error_count': 1}, {'executed_test_count': False},
                        {'module_test_count': 2}, {'sorted_ids_sha256': 'a' * 64}, {'extra': 'private'}):
            with self.subTest(changes=tuple(changes)), self.assertRaises(d.q.Refused):
                d.validate_identity(result(row), independent | changes)
        for bad in ({'returncode': True, 'stdout': result(row)['stdout']},
                    {'returncode': 0, 'stdout': result(row)['stdout'] * 2},
                    {'returncode': 0, 'stdout': 'LAZY_PROOF_RESULT:{"loader_errors":0,"loader_errors":0}'},
                    {'returncode': 1, 'stdout': result(row)['stdout']}):
            with self.assertRaises(d.q.Refused):
                d.validate_identity(bad, independent)
        self.assertTrue(d.compare_identities(accepted, accepted))
        changed = copy.deepcopy(accepted)
        changed['ids'] = accepted['ids'][:-1] + ('different.Sample.test_last',)
        with self.assertRaises(d.q.Refused):
            d.compare_identities(accepted, changed)
        changed = copy.deepcopy(accepted)
        changed['units'] = ('different.Sample',)
        with self.assertRaises(d.q.Refused):
            d.compare_identities(accepted, changed)


if __name__ == '__main__':
    unittest.main()
