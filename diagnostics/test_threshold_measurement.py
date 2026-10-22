"""Portable synthetic admission and evidence, never the threshold application."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch


class ThresholdSourceControls(unittest.TestCase):
    def test_only_exact_threshold_candidate_is_applied_after_clean_first_status(self):
        import measure_maintainer_pair as m
        from test_source_context_real_git import LocalSession
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); seed = root / 'seed'; seed.mkdir()
            session = LocalSession()
            session.git(seed, 'init', '-b', 'main')
            session.git(seed, 'config', 'user.name', 'Synthetic Fixture')
            session.git(seed, 'config', 'user.email', 'fixture@example.invalid')
            (seed / 'tools').mkdir()
            (seed / m.q.SUITE_PATH).write_bytes(b'unchanged suite\n')
            name = 'tools/test_threshold_sheet.py'
            (seed / name).write_bytes(b'baseline threshold\n')
            session.git(seed, 'add', '.'); session.git(seed, 'commit', '-m', 'synthetic source')
            pin = session.git(seed, 'rev-parse', 'HEAD').strip()
            expected = m.q.inventory(seed); candidate = b'candidate threshold\n'
            target = m.source_context(session, seed, root / 'candidate', 'candidate', expected,
                                      candidate, source_sha=pin, candidate_path=name)
            m.q.verify_sources(session, root / 'candidate', target, True,
                               source_sha=pin, candidate_path=name)
            self.assertEqual(candidate, (root / 'candidate' / name).read_bytes())
            self.assertEqual(b'unchanged suite\n', (root / 'candidate' / m.q.SUITE_PATH).read_bytes())
            self.assertEqual([name], session.git(root / 'candidate', 'diff', '--name-only').splitlines())
            self.assertEqual(b'', session.first_status[0][2])
            with self.assertRaises(m.q.Refused):
                m.q.verify_sources(session, root / 'candidate', target, True, source_sha=pin)
            for bad in ('tools/other.py', '../tools/test_threshold_sheet.py', None):
                with self.subTest(path=bad), self.assertRaises(m.q.Refused):
                    m.source_context(session, seed, root / 'forbidden', 'candidate', expected,
                                     candidate, source_sha=pin, candidate_path=bad)
                self.assertFalse((root / 'forbidden').exists())


class ThresholdAdmissionControls(unittest.TestCase):
    def test_measured_setup_and_remaining_reserves_fit_exact_ten_minutes(self):
        import measure_threshold_module as m
        # Initial setup includes checkout: 79 seconds is admitted, not capped at 60.
        self.assertEqual(m.admit(600, 79, probes=4, controls=2), 61)
        self.assertEqual(m.admit(600, 140, probes=4, controls=2), 0)
        for now, probes, controls in ((140.001, 4, 2), (330.001, 2, 1),
                                      (445.001, 1, 0), (520.001, 0, 0)):
            with self.subTest(now=now), self.assertRaises(m.q.Refused):
                m.admit(600, now, probes=probes, controls=controls)
        for bad in (float('nan'), float('inf'), True, -1):
            with self.assertRaises(m.q.Refused): m.admit(600, bad, probes=4, controls=2)

    def test_candidate_is_exact_one_pinned_file_not_a_generic_patch(self):
        import measure_threshold_module as m
        original, candidate = b'original\n', b'candidate\n'
        blob = lambda raw: m.hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        with patch.multiple(m, BASELINE_HASH=m.q.digest(original), CANDIDATE_HASH=m.q.digest(candidate),
                            BASELINE_BLOB=blob(original), CANDIDATE_BLOB=blob(candidate)):
            self.assertEqual(m.CANDIDATE_HASH, m.verify_candidate(original, candidate))
            for before, after in ((candidate, original), (original, candidate + b'\n'),
                                  (original.replace(b'\n', b'\r\n'), candidate)):
                with self.assertRaises(m.q.Refused): m.verify_candidate(before, after)


class OriginalPayloadControls(unittest.TestCase):
    def test_exact_original_payload_keeps_345_tests_12_skips_and_coherent_owner_capture(self):
        import measure_threshold_module as m
        from test_reader_attribution import SyntheticOwner
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); session = SyntheticOwner(root, [
                (0, b'', b'Ran 345 tests in 44.194s\r\n\r\nOK (skipped=12)\r\n')])
            progress = {'samples': []}
            with patch.object(m.q, 'emit'):
                row = m.measure_probe(session, root, 'UNMODIFIED PAYLOAD', 'baseline', m.q.LOOKUPS[0], progress)
            self.assertEqual(session.calls[0][0], [m.sys.executable, '-c', 'UNMODIFIED PAYLOAD',
                                                  str(root / 'tools'), m.MODULE, m.q.LOOKUPS[0]])
            self.assertEqual((row['test_count'], row['skipped'], row['classification']), (345, 12, 'nonreader'))
            self.assertEqual(row['tree_cpu_seconds'], .05)
            self.assertTrue(row['qualified']); self.assertTrue(row['cleanup_verified'])
            self.assertEqual([row], progress['samples'])
            self.assertNotIn('DO NOT TRUST', json.dumps(row))

    def test_unread_counts_failures_and_private_exception_stop_without_false_clean_row(self):
        import measure_threshold_module as m
        from test_reader_attribution import SyntheticOwner
        for code, output in ((0, b'Ran 344 tests in 0.1s\n\nOK (skipped=12)\n'),
                             (0, b'Ran 345 tests in 0.1s\n\nOK\n'),
                             (1, b'Ran 345 tests in 0.1s\n\nFAILED (errors=1, skipped=12)\n'),
                             (0, b'PRIVATE_SENTINEL')):
            with self.subTest(code=code, output=output), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve(); session = SyntheticOwner(root, [(code, b'', output)])
                progress = {'samples': []}
                with patch.object(m.q, 'emit'), self.assertRaises(m.q.Refused):
                    m.measure_probe(session, root, 'original', 'baseline', m.q.LOOKUPS[0], progress)
                self.assertEqual(len(progress['samples']), 1)
                self.assertFalse(progress['samples'][0]['qualified'])
                self.assertNotIn('PRIVATE_SENTINEL', json.dumps(progress))

    def test_ownership_swap_refuses_even_when_output_is_valid(self):
        import measure_threshold_module as m
        from test_reader_attribution import SyntheticOwner
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); session = SyntheticOwner(root, [
                (0, b'', b'Ran 345 tests in 1.0s\n\nOK (skipped=12)\n')])
            original = session.run
            def swapped(*args):
                result = original(*args); result['stdout_path'] = str(root / 'private-other.bin'); return result
            session.run = swapped; progress = {'samples': []}
            with patch.object(m.q, 'emit'), self.assertRaises(m.q.Refused):
                m.measure_probe(session, root, 'original', 'baseline', m.q.LOOKUPS[0], progress)
            self.assertFalse(progress['samples'][0]['capture_read_verified'])


class BaselineSpendingControls(unittest.TestCase):
    def test_failed_baseline_never_prepares_or_runs_candidate(self):
        import measure_threshold_module as m
        from test_reader_attribution import SyntheticOwner
        for failure in ('probe', 'guard'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                good = b'Ran 345 tests in 1.0s\n\nOK (skipped=12)\n'
                bad = b'Ran 344 tests in 1.0s\n\nOK (skipped=12)\n'
                session = SyntheticOwner(root, [(0, b'', good), (0, b'', bad if failure == 'probe' else good)])
                session.hard_deadline = time.monotonic() + 600
                progress = {'samples': [], 'arms': {}}; prepared = []
                def prepare(session, observer, seed, repo, arm, expected, candidate, guard):
                    prepared.append(arm); repo.mkdir(); return {'pinned': 'source'}
                def guard():
                    if failure == 'guard' and len(session.calls) == 2: raise m.q.Refused('tracked_raw_bytes_changed')
                with patch.object(m, 'prepare_arm', prepare), patch.object(m, 'qualify_arm', return_value={'verified': True}), \
                     patch.object(m.q, 'emit'), self.assertRaises(m.q.Refused):
                    m.run_arms(session, root, root, root, {}, b'candidate', 'original', progress, [], guard)
                self.assertEqual(prepared, ['baseline'])
                self.assertNotIn('candidate', progress['arms'])
                self.assertFalse((root / 'candidate').exists())
                self.assertNotIn('baseline_qualified', progress)

    def test_four_serial_original_calls_follow_two_qualified_arms(self):
        import measure_threshold_module as m
        from test_reader_attribution import SyntheticOwner
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            output = b'Ran 345 tests in 1.0s\n\nOK (skipped=12)\n'
            session = SyntheticOwner(root, [(0, b'', output)] * 4)
            session.hard_deadline = time.monotonic() + 600
            progress = {'samples': [], 'arms': {}}; prepared = []
            def prepare(session, observer, seed, repo, arm, expected, candidate, guard):
                if arm == 'candidate': self.assertTrue(progress['baseline_qualified'])
                prepared.append(arm); repo.mkdir(); return {}
            with patch.object(m, 'prepare_arm', prepare), patch.object(m, 'qualify_arm', return_value={'verified': True}), \
                 patch.object(m.q, 'emit'):
                m.run_arms(session, root, root, root, {}, b'candidate', 'original', progress, [], lambda: None)
            self.assertEqual(prepared, ['baseline', 'candidate'])
            self.assertEqual([(row['arm'], row['lookup']) for row in progress['samples']], list(m.PLAN))
            self.assertEqual(len(session.calls), 4)
            self.assertTrue(all(row['qualified'] for row in progress['samples']))
            self.assertTrue(progress['candidate_qualified'])


class TerminalControls(unittest.TestCase):
    def test_real_cli_refusal_and_publication_exception_are_finite(self):
        import measure_threshold_module as m
        for arguments in ([], ['--PRIVATE_SENTINEL']):
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = m.main(arguments)
            self.assertEqual(status, 2)
            self.assertEqual(stderr.getvalue(), '')
            self.assertNotIn('PRIVATE_SENTINEL', stdout.getvalue())
            self.assertEqual(json.loads(stdout.getvalue())['status'], 'inconclusive')
        with patch.object(m.q, 'emit', side_effect=OSError('PRIVATE_SENTINEL')), \
             contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(m.main([]), 2)
            self.assertEqual(stderr.getvalue(), '')

    def test_terminal_deadline_crossing_fails_without_retry_or_later_work(self):
        import measure_threshold_module as m
        from types import SimpleNamespace
        for emission in ('threshold_environment', 'threshold_summary', None):
            with self.subTest(emission=emission), tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
                root = Path(directory).resolve(); clock = [0.0]; events = []; cleanup = []
                observer = root / 'observer'; seed = root / 'seed'; observer.mkdir(); seed.mkdir()
                session = SimpleNamespace(cleanup=lambda: cleanup.append(True) or True)
                def execute(session, observer, seed, origin, progress, environment):
                    progress.update(baseline_qualified=True, candidate_qualified=True,
                                    source_integrity_verified=True, output_contract_verified=True, receipt_verified=True)
                def emit(event, **fields):
                    events.append((event, fields))
                    if event == emission: clock[0] = 601
                for target, name, value in ((m.checkpoint, 'authorize_route', lambda *a: None),
                    (m.checkpoint, 'budget_deadlines', lambda *a: (540, 600)),
                    (m.q, 'environment_preflight', lambda: None), (m.q, 'corpus_preflight', lambda *a, **k: None),
                    (m.maintainer, 'environment_identity', lambda: {}), (m.maintainer, 'validate_environment', lambda value: None),
                    (m.tempfile, 'mkdtemp', lambda **kw: str(root / 'owned')), (m, 'make_session', lambda *a: session),
                    (m, 'execute', execute), (m.q, 'emit', emit), (m.time, 'monotonic', lambda: clock[0])):
                    stack.enter_context(patch.object(target, name, value))
                stack.enter_context(patch.dict(m.os.environ, {'GITHUB_SHA': 'a' * 40, 'GITHUB_RUN_ID': '123'}))
                status = m.main(['--observer', str(observer), '--seed', str(seed), '--job-start-epoch', '0'])
                self.assertEqual(status, 0 if emission is None else 2)
                self.assertEqual(cleanup, [True])
                self.assertEqual(sum(event == 'threshold_summary' for event, _ in events), 1)
                if emission == 'threshold_environment':
                    self.assertEqual(events[-1][1]['status'], 'inconclusive')
                    self.assertFalse(events[-1][1]['hard_budget_verified'])


class RouteControls(unittest.TestCase):
    def test_only_ten_minute_first_attempt_threshold_route_is_enabled(self):
        import measure_threshold_module as m
        root = Path(m.__file__).resolve().parent.parent
        workflow = (root / '.github/workflows/ci-threshold-module.yml').read_text()
        self.assertIn('timeout-minutes: 10', workflow)
        self.assertIn("python-version: '3.14.4'", workflow)
        self.assertIn('github.run_attempt == 1', workflow)
        self.assertIn(m.SOURCE_SHA, workflow)
        self.assertIn('/tools/test_threshold_sheet.py', workflow)
        for name in ('ci-reader-attribution.yml', 'ci-parallel-proof.yml', 'ci-checkpoint-discovery.yml'):
            old = (root / '.github/workflows' / name).read_text()
            self.assertIn("branches-ignore: ['**']", old)
            self.assertIn("tags-ignore: ['**']", old)
        for forbidden in ('upload-artifact', 'workflow_dispatch', 'strategy:', 'tools/suite.py'):
            self.assertNotIn(forbidden, workflow)
        self.assertEqual(json.loads((root / 'diagnostics/threshold-module-budget.json').read_text()), m.BUDGET)
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push',
               'GITHUB_REF': m.q.BRANCH, 'GITHUB_RUN_ATTEMPT': '1'}
        m.checkpoint.authorize_route('nt', '3.14.4', env)
        for changed in ({'GITHUB_RUN_ATTEMPT': '2'}, {'GITHUB_EVENT_NAME': 'workflow_dispatch'}, {'GITHUB_REF': 'refs/heads/main'}):
            with self.assertRaises(m.q.Refused): m.checkpoint.authorize_route('nt', '3.14.4', env | changed)


if __name__ == '__main__': unittest.main()
