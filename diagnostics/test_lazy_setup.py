"""Portable setup-only boundary controls; no hosted or native execution."""
import ast
from contextlib import ExitStack
import inspect
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import diagnose_lazy_setup as subject


class SetupBudgetTests(unittest.TestCase):
    def test_budget_is_ten_minutes_with_one_minute_reserved(self):
        self.assertEqual(subject.JOB_SECONDS, 600)
        self.assertEqual(subject.CLEANUP_SECONDS, 60)
        self.assertEqual(subject.budget_deadline(1000.0, 1000.0, 50.0), 590.0)
        self.assertEqual(subject.budget_deadline(1000.0, 1100.0, 50.0), 490.0)

    def test_deadline_subtracts_setup_time_instead_of_restarting_clock(self):
        early = subject.budget_deadline(1000.0, 1010.0, 20.0)
        later = subject.budget_deadline(1000.0, 1110.0, 120.0)
        self.assertEqual(early, later)
        self.assertAlmostEqual(subject.budget_deadline(1000.0, 1539.5, 60.0), 60.5)

    def test_exhausted_or_backward_origin_refuses(self):
        for now in (999.0, 1540.0, 1600.0, 10000.0):
            with self.subTest(now=now), self.assertRaises(subject.q.Refused):
                subject.budget_deadline(1000.0, now, 50.0)

    def test_nonfinite_clock_values_refuse(self):
        for bad in (math.nan, math.inf, -math.inf):
            for args in ((bad, 1000.0, 50.0), (1000.0, bad, 50.0),
                         (1000.0, 1000.0, bad)):
                with self.subTest(args=args), self.assertRaises(subject.q.Refused):
                    subject.budget_deadline(*args)


class SetupScopeTests(unittest.TestCase):
    def test_main_always_cleans_and_never_qualifies(self):
        for setup_fails, cleanup_ok in ((True, True), (False, False), (False, True)):
            with self.subTest(setup_fails=setup_fails, cleanup_ok=cleanup_ok), ExitStack() as stack:
                env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push',
                       'GITHUB_REF': subject.q.BRANCH, 'GITHUB_RUN_ATTEMPT': '1'}
                stack.enter_context(mock.patch.object(subject, 'os', SimpleNamespace(name='nt', environ=env)))
                stack.enter_context(mock.patch.object(subject.platform, 'python_version', return_value='3.14.4'))
                stack.enter_context(mock.patch.object(subject.time, 'time', return_value=1000.0))
                stack.enter_context(mock.patch.object(subject.time, 'monotonic', return_value=50.0))
                stack.enter_context(mock.patch.object(subject.q, 'environment_preflight'))
                stack.enter_context(mock.patch.object(subject.q, 'corpus_preflight'))
                stack.enter_context(mock.patch.object(subject.tempfile, 'gettempdir', return_value='/synthetic/temp'))
                stack.enter_context(mock.patch.object(subject.tempfile, 'mkdtemp', return_value='/synthetic/temp/run'))
                stack.enter_context(mock.patch.object(subject.q, 'safe_exception',
                    return_value={'private_detail_retained': True}))
                session = mock.Mock()
                session.cleanup.return_value = cleanup_ok
                factory = stack.enter_context(mock.patch.object(subject.q, 'Session', return_value=session))
                stack.enter_context(mock.patch.object(subject, 'setup',
                    side_effect=subject.q.Refused('first_status_not_clean') if setup_fails else None))
                emit = stack.enter_context(mock.patch.object(subject.q, 'emit'))
                result = subject.main(['--observer', '/synthetic/observer', '--seed', '/synthetic/seed',
                                       '--job-start-epoch', '1000'])
                factory.assert_called_once_with(Path('/synthetic/temp/run'), 590.0)
                session.cleanup.assert_called_once_with()
                summary = emit.call_args_list[-1]
                self.assertEqual(summary.args, ('setup_summary',))
                self.assertFalse(summary.kwargs['qualification'])
                self.assertEqual(summary.kwargs['completed_performance_probes'], 0)
                self.assertEqual(summary.kwargs['planned_performance_probes'], 0)
                self.assertEqual(summary.kwargs['process_cleanup_verified'], cleanup_ok)
                success = not setup_fails and cleanup_ok
                self.assertEqual(result, 0 if success else 2)
                self.assertEqual(summary.kwargs['status'], 'setup-complete' if success else 'inconclusive')

    def run_setup_fixture(self, clone_failure=False, owner_failure=False):
        events = []
        observer, seed = Path('/synthetic/observer'), Path('/synthetic/seed')
        session = mock.Mock(root=Path('/synthetic/run'), deadline=1000.0)
        session.git.side_effect = ['', '\n'.join(subject.q.OBSERVER_PATHS)]
        expected = {subject.q.SUITE_PATH: subject.q.ORIGINAL_HASH}
        def run(argv, cwd):
            events.append('native-owner')
            self.assertIn('windows_job_probe_controls.py', argv[1])
            return {'returncode': 1 if owner_failure else 0, 'stdout': '{}'}
        session.run.side_effect = run
        def clone(session_arg, seed_arg, root_arg, variant, expected_arg, candidate):
            events.append(variant)
            self.assertIs(session_arg, session)
            self.assertEqual(seed_arg, seed)
            self.assertEqual(expected_arg, expected)
            if clone_failure:
                raise subject.q.Refused('first_status_not_clean')
            return Path('/synthetic/' + variant), {}
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(subject.q, 'first_clean',
                side_effect=lambda session, repo, head, role: events.append(role)))
            stack.enter_context(mock.patch.object(subject.q, 'inventory',
                side_effect=lambda repo, **kwargs: expected if repo == seed else {}))
            stack.enter_context(mock.patch.object(subject.q, 'raw_source_inventory', return_value=expected))
            stack.enter_context(mock.patch.object(subject.q, 'read_reviewed_bytes', return_value=b'candidate'))
            stack.enter_context(mock.patch.object(subject.q, 'original_payload'))
            stack.enter_context(mock.patch.object(subject.q, 'emit'))
            stack.enter_context(mock.patch.object(subject.q, 'validate_owner_controls',
                side_effect=lambda row: events.append('owner-validated')))
            stack.enter_context(mock.patch.object(subject.q, 'make_clone', side_effect=clone))
            if clone_failure or owner_failure:
                with self.assertRaisesRegex(subject.q.Refused,
                        'owner_controls_failed' if owner_failure else 'first_status_not_clean'):
                    subject.setup(session, observer, seed)
            else:
                subject.setup(session, observer, seed)
        self.assertEqual(session.run.call_count, 1)
        return events

    def test_setup_runs_native_owner_before_exact_two_clone_roles(self):
        self.assertEqual(len(subject.q.DECLARED_CONTROL_IDS), 9)
        self.assertEqual(self.run_setup_fixture(),
                         ['observer', 'seed', 'native-owner', 'owner-validated', 'baseline', 'candidate'])

    def test_dirty_baseline_stops_before_candidate_without_retry(self):
        self.assertEqual(self.run_setup_fixture(clone_failure=True),
                         ['observer', 'seed', 'native-owner', 'owner-validated', 'baseline'])

    def test_failed_owner_controls_stop_before_cloning(self):
        self.assertEqual(self.run_setup_fixture(owner_failure=True),
                         ['observer', 'seed', 'native-owner'])

    def test_entrypoint_cannot_call_qualification_workload_helpers(self):
        tree = ast.parse(inspect.getsource(subject))
        forbidden = {'build_plan', 'admit_budget', 'validate_controls', 'verify_probe',
                     'child_command', 'child', 'summarize'}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, forbidden)
            if isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, forbidden)
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'q':
                    self.assertNotEqual(node.func.attr, 'main')

    def test_no_subprocess_or_alternate_process_owner_in_entrypoint(self):
        tree = ast.parse(inspect.getsource(subject))
        forbidden_imports = {'subprocess', 'multiprocessing', 'concurrent.futures', 'ctypes'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertFalse({alias.name for alias in node.names} & forbidden_imports)
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(node.module, forbidden_imports)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, {'system', 'popen', 'spawn', 'execv', 'execve'})

    def test_workflow_only_invokes_setup_entrypoint_with_ten_minute_cap(self):
        root = Path(subject.q.__file__).resolve().parent.parent
        workflow = (root / '.github/workflows/ci-parallel-proof.yml').read_text()
        self.assertIn('timeout-minutes: 10', workflow)
        self.assertIn('diagnostics/diagnose_lazy_setup.py', workflow)
        self.assertNotIn('diagnostics/measure_lazy_suite_ids.py', workflow)
        self.assertIn('github.run_attempt == 1', workflow)
        self.assertIn('PROOF_JOB_START_EPOCH', workflow)
        self.assertEqual(workflow.count("GIT_CONFIG_VALUE_0: 'false'"), 2)
        self.assertIn('/.gitignore', workflow)


if __name__ == '__main__':
    unittest.main()
