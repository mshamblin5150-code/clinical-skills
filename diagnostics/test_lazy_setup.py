"""Portable setup-only boundary controls; no hosted or native execution."""
import ast
from contextlib import ExitStack
import inspect
import math
import os
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import diagnose_lazy_setup as subject


class RootLengthTests(unittest.TestCase):
    def test_lengths_use_utf16_units_not_codepoints(self):
        self.assertEqual(subject.utf16_units('a\U0001f600b'), 4)
        self.assertEqual(subject.utf16_units('a\ud800b'), 3)

    def test_fixed_path_is_the_reviewed_185_unit_path(self):
        self.assertEqual(subject.utf16_units(subject.EXACT_PATH), 185)
        self.assertEqual(subject.q.digest(subject.EXACT_PATH.encode()),
                         '13e64eea8bdeb9f1739eb07657c35e4a7494fa4f00478117bd63e1f10c98dd44')


class ExactPathSafetyTests(unittest.TestCase):
    def setUp(self):
        root = Path(subject.q.__file__).resolve().parent.parent / 'scratch/sessions'
        self.temp = tempfile.TemporaryDirectory(prefix='two-root-control-', dir=root)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.path = self.repo / subject.EXACT_PATH
        self.path.parent.mkdir(parents=True)
        self.data = b'harmless exact synthetic bytes\n'
        self.path.write_bytes(self.data)
        self.session = mock.Mock(deadline=time.monotonic() + 60)
        self.session.run.return_value = {'returncode': 1, 'stdout': ''}

    def test_nondirectory_ancestor_refuses_globally_after_dirty_status(self):
        self.path.unlink()
        self.path.parent.rmdir()
        (self.repo / 'docs').rmdir()
        (self.repo / 'docs').write_bytes(b'not a directory')
        with self.assertRaisesRegex(subject.q.Refused, 'exact_path_ancestor_not_directory'):
            subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))
        self.session.run.return_value = {'returncode': 0, 'stdout': 'false'}
        with mock.patch.object(subject.q, 'first_clean',
                side_effect=subject.q.Refused('first_status_not_clean')) as first, \
                mock.patch.object(subject.q, 'emit'), \
                mock.patch.object(subject.q, 'inventory') as inventory:
            with self.assertRaisesRegex(subject.q.Refused, 'exact_path_ancestor_not_directory'):
                subject.run_arm(self.session, self.repo.parent, self.repo,
                                'original-layout', {subject.EXACT_PATH: subject.q.digest(self.data)})
        first.assert_called_once()
        inventory.assert_not_called()

    def test_parent_symlink_is_refused_before_reading(self):
        self.path.unlink()
        self.path.parent.rmdir()
        outside = self.repo / 'outside'
        outside.mkdir()
        self.path.parent.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(subject.q.Refused):
            subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))

    def test_multiple_hardlinks_are_refused(self):
        os.link(self.path, self.repo / 'other-link')
        with self.assertRaises(subject.q.Refused):
            subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))

    def test_expired_deadline_refuses_evidence_read(self):
        self.session.deadline = time.monotonic() - 1
        with self.assertRaises(subject.q.Refused):
            subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))

    def test_exact_bytes_and_finite_configuration(self):
        self.session.run.return_value = {'returncode': 0, 'stdout': 'PRIVATE CONFIG VALUE'}
        row = subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))
        self.assertEqual(row['raw_identity'], 'equal')
        self.assertEqual(row['filesystem'], 'regular')
        self.assertEqual(row['core_longpaths'], 'unrecognized')
        self.assertNotIn('PRIVATE', str(row))
        self.assertNotIn(str(self.repo), str(row))

    def test_missing_does_not_claim_confirmed_absence(self):
        self.path.unlink()
        row = subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))
        self.assertEqual(row['filesystem'], 'missing-or-inaccessible')
        self.assertEqual(row['raw_identity'], 'unavailable')

    def test_read_denial_is_finite_inaccessible_not_missing(self):
        with mock.patch.object(Path, 'open', side_effect=PermissionError('PRIVATE')):
            row = subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))
        self.assertEqual(row['filesystem'], 'inaccessible')
        self.assertEqual(row['raw_identity'], 'unavailable')
        self.assertNotIn('PRIVATE', str(row))

    def test_changed_raw_bytes_are_not_normalized(self):
        self.path.write_bytes(self.data.replace(b'\n', b'\r\n'))
        row = subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))
        self.assertEqual(row['raw_identity'], 'different')

    def test_reparse_ancestor_refuses_before_open(self):
        original = Path.lstat
        def lstat(path):
            result = original(path)
            if path == self.repo / 'docs':
                return SimpleNamespace(st_mode=result.st_mode, st_file_attributes=0x400)
            return result
        with mock.patch.object(Path, 'lstat', lstat), \
                mock.patch.object(Path, 'open') as opened:
            with self.assertRaisesRegex(subject.q.Refused, 'exact_path_link_refused'):
                subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))
        opened.assert_not_called()

    def test_changed_open_identity_refuses(self):
        before = self.path.stat()
        changed = SimpleNamespace(st_dev=before.st_dev, st_ino=before.st_ino + 1,
                                  st_size=before.st_size, st_mtime_ns=before.st_mtime_ns,
                                  st_mode=before.st_mode, st_nlink=1)
        with mock.patch.object(subject.os, 'fstat', return_value=changed):
            with self.assertRaisesRegex(subject.q.Refused, 'exact_path_changed_during_read'):
                subject.exact_path_evidence(self.session, self.repo, subject.q.digest(self.data))


class RootArmTests(unittest.TestCase):
    def fixture(self, refusal=None, raw_identity='equal', bad_inventory=False):
        session = mock.Mock(deadline=time.monotonic() + 60)
        session.run.return_value = {'returncode': 0}
        repo, seed = Path('/synthetic/clone'), Path('/synthetic/seed')
        expected = {subject.EXACT_PATH: 'expected'}
        events = []
        def status(*args):
            events.append('status')
            if refusal:
                raise subject.q.Refused(refusal)
        def evidence(*args):
            events.append('evidence')
            return {'raw_identity': raw_identity}
        with ExitStack() as stack:
            first = stack.enter_context(mock.patch.object(subject.q, 'first_clean', side_effect=status))
            stack.enter_context(mock.patch.object(subject, 'exact_path_evidence', side_effect=evidence))
            stack.enter_context(mock.patch.object(subject.q, 'inventory',
                return_value={} if bad_inventory else expected))
            stack.enter_context(mock.patch.object(subject.q, 'corpus_preflight'))
            stack.enter_context(mock.patch.object(subject.q, 'emit'))
            stack.enter_context(mock.patch.object(subject.os.path, 'lexists', return_value=False))
            try:
                result = subject.run_arm(session, seed, repo, 'original-layout', expected)
            finally:
                first.assert_called_once_with(session, repo, subject.q.BASE, 'original-layout')
                session.run.assert_called_once()
                session.git.assert_called_once_with(repo, '-c', 'core.autocrlf=false',
                                                    'checkout', '--detach', subject.q.BASE)
        return result, events

    def test_clean_arm_requires_raw_equality_and_status_before_read(self):
        row, events = self.fixture()
        self.assertEqual(events, ['status', 'evidence'])
        self.assertTrue(row['admitted'])
        self.assertTrue(row['raw_tree_identity_verified'])

    def test_dirty_arm_stays_rejected_despite_equal_poststatus_bytes(self):
        row, events = self.fixture(refusal='first_status_not_clean')
        self.assertEqual(events, ['status', 'evidence'])
        self.assertFalse(row['admitted'])
        self.assertFalse(row['raw_tree_identity_verified'])
        self.assertTrue(row['first_status_refused'])

    def test_other_first_status_refusals_propagate(self):
        for reason in ('wrong_source_head', 'global_budget_exhausted', 'shared_objects_refused'):
            with self.subTest(reason=reason), self.assertRaisesRegex(subject.q.Refused, '^' + reason + '$'):
                self.fixture(refusal=reason)

    def test_present_but_changed_bytes_stop_even_dirty_arm(self):
        with self.assertRaisesRegex(subject.q.Refused, '^exact_path_raw_identity_changed$'):
            self.fixture(refusal='first_status_not_clean', raw_identity='different')

    def test_clean_status_cannot_bypass_full_inventory(self):
        with self.assertRaisesRegex(subject.q.Refused, '^initial_clone_inventory_changed$'):
            self.fixture(bad_inventory=True)


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
        cases = ((True, True, (False, True)), (False, False, (False, True)),
                 (False, True, (False, True)), (False, True, (False, False)),
                 (False, True, (True, True)), (False, True, (True,)))
        for setup_fails, cleanup_ok, admitted in cases:
            with self.subTest(setup_fails=setup_fails, cleanup_ok=cleanup_ok, admitted=admitted), ExitStack() as stack:
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
                    side_effect=subject.q.Refused('unsafe') if setup_fails else None,
                    return_value=[{'admitted': value, 'raw_tree_identity_verified': value} for value in admitted]))
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
                self.assertEqual(summary.kwargs['diagnostic_collection_complete'], not setup_fails)
                self.assertEqual(summary.kwargs['setup_integrity_verified'],
                                 not setup_fails and len(admitted) == 2 and all(admitted))
                success = not setup_fails and cleanup_ok
                self.assertEqual(result, 0 if success else 2)
                self.assertEqual(summary.kwargs['status'], 'diagnostic-complete' if success else 'inconclusive')

    def run_setup_fixture(self, dirty_first=False, unsafe=False, owner_failure=False):
        events = []
        observer, seed = Path('/synthetic/observer'), Path('/synthetic/seed')
        root = Path(subject.q.__file__).resolve().parent.parent / 'scratch/sessions'
        with tempfile.TemporaryDirectory(prefix='two-root-layout-', dir=root) as temp:
            temp = Path(temp)
            owner = temp / 'lazy-setup-diagnostic-long-random'
            owner.mkdir()
            session = mock.Mock(root=owner, deadline=1000.0)
            session.git.side_effect = ['', '\n'.join(subject.q.OBSERVER_PATHS)]
            expected = {subject.q.SUITE_PATH: subject.q.ORIGINAL_HASH}
            def run(argv, cwd):
                events.append('native-owner')
                self.assertIn('windows_job_probe_controls.py', argv[1])
                return {'returncode': 1 if owner_failure else 0, 'stdout': '{}'}
            session.run.side_effect = run
            def arm(session_arg, seed_arg, repo, role, expected_arg):
                events.append(role)
                self.assertIs(session_arg, session)
                self.assertEqual(seed_arg, seed)
                self.assertEqual(expected_arg, expected)
                self.assertEqual(repo.name, 'baseline')
                self.assertEqual(repo.parent.parent, owner.parent)
                if role == 'original-layout':
                    self.assertEqual(repo.parent, owner)
                else:
                    self.assertLess(subject.utf16_units(repo.parent), subject.utf16_units(owner))
                if unsafe:
                    raise subject.q.Refused('unsafe')
                return {'role': role, 'admitted': not (dirty_first and role == 'original-layout')}
            with ExitStack() as stack:
                stack.enter_context(mock.patch.object(subject.q, 'first_clean',
                    side_effect=lambda session, repo, head, role: events.append(role)))
                stack.enter_context(mock.patch.object(subject.q, 'inventory',
                    side_effect=lambda repo, **kwargs: {} if repo == observer else expected))
                stack.enter_context(mock.patch.object(subject.q, 'raw_source_inventory', return_value=expected))
                stack.enter_context(mock.patch.object(subject.q, 'original_payload'))
                stack.enter_context(mock.patch.object(subject.q, 'emit'))
                stack.enter_context(mock.patch.object(subject.q, 'validate_owner_controls',
                    side_effect=lambda row: events.append('owner-validated')))
                stack.enter_context(mock.patch.object(subject, 'run_arm', side_effect=arm))
                if unsafe or owner_failure:
                    with self.assertRaisesRegex(subject.q.Refused,
                            'owner_controls_failed' if owner_failure else 'unsafe'):
                        subject.setup(session, observer, seed)
                else:
                    rows = subject.setup(session, observer, seed)
                    self.assertEqual(len(rows), 2)
                    self.assertEqual(rows[0]['admitted'], not dirty_first)
            self.assertEqual(session.run.call_count, 1)
        return events

    def test_setup_runs_owner_before_two_same_parent_original_source_arms(self):
        self.assertEqual(len(subject.q.DECLARED_CONTROL_IDS), 9)
        self.assertEqual(self.run_setup_fixture(),
                         ['observer', 'seed', 'native-owner', 'owner-validated', 'original-layout', 'short-layout'])

    def test_permanently_dirty_arm_allows_only_independent_second_arm(self):
        self.assertEqual(self.run_setup_fixture(dirty_first=True),
                         ['observer', 'seed', 'native-owner', 'owner-validated', 'original-layout', 'short-layout'])

    def test_unsafe_arm_stops_before_second_arm(self):
        self.assertEqual(self.run_setup_fixture(unsafe=True),
                         ['observer', 'seed', 'native-owner', 'owner-validated', 'original-layout'])

    def test_failed_owner_controls_stop_before_cloning(self):
        self.assertEqual(self.run_setup_fixture(owner_failure=True),
                         ['observer', 'seed', 'native-owner'])

    def test_entrypoint_cannot_call_qualification_workload_helpers(self):
        tree = ast.parse(inspect.getsource(subject))
        forbidden = {'build_plan', 'admit_budget', 'validate_controls', 'verify_probe',
                     'child_command', 'child', 'summarize', 'make_clone', 'write_bytes', 'write_text'}
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

    def test_setup_entrypoint_is_dormant_in_replacement_qualification_workflow(self):
        root = Path(subject.q.__file__).resolve().parent.parent
        workflow = (root / '.github/workflows/ci-parallel-proof.yml').read_text()
        self.assertIn('timeout-minutes: 90', workflow)
        self.assertNotIn('python observer/diagnostics/diagnose_lazy_setup.py', workflow)
        self.assertNotIn('python observer/diagnostics/diagnose_staging_layout.py', workflow)
        self.assertIn('python observer/diagnostics/measure_maintainer_pair.py', workflow)
        self.assertIn('github.run_attempt == 1', workflow)
        self.assertIn('PROOF_JOB_START_EPOCH', workflow)
        self.assertEqual(workflow.count("GIT_CONFIG_VALUE_0: 'false'"), 4)
        self.assertIn('/.gitignore', workflow)


if __name__ == '__main__':
    unittest.main()
