"""Synthetic accounting/capture controls; never run repository test bodies."""
import unittest

from lazy_suite_support import Refused, digest
from full_suite_receipts import allowed_retained, parse_suite


def report(count=9000, jobs=3, cpu=4, weights='equal'):
    return (f'discovered: {count}\nunaccounted: 0\n'
            f'jobs: {jobs} (max(1, (os.cpu_count() or 1) * 3 // 4); os.cpu_count()={cpu})\n'
            f'weights: {weights}\n'
            "critical path (this run's elapsed time): test_example.Case 12.250s; wall 18.500s; next-slowest worker 9.000s\n")


class SuiteReceiptTests(unittest.TestCase):
    def parse(self, stdout=None, stderr='', code=0, count=9000, cpu=4):
        return parse_suite(report() if stdout is None else stdout, stderr, code, count, cpu)

    def test_exact_accounting_does_not_claim_every_body_or_zero_skips(self):
        row = self.parse()
        self.assertEqual(row['discovered'], 9000)
        self.assertEqual(row['unaccounted'], 0)
        self.assertEqual(row['jobs'], 3)
        self.assertEqual(row['weights'], 'equal')
        self.assertEqual(row['returncode'], 0)
        self.assertTrue(row['internal_accounting'])
        self.assertEqual(row['skips'], 'not separately exposed')
        self.assertFalse(row['independent_executed_id_manifest'])
        self.assertEqual(row['critical_unit_token'], digest(b'test_example.Case'))
        self.assertNotIn('test_example', str(row))

    def test_original_test_failure_is_accounted_but_not_success(self):
        row = self.parse('FAIL: synthetic\nre-run (from tools/): python -m unittest test_example.Case.test_x\n' + report(), code=1)
        self.assertEqual(row['returncode'], 1)
        self.assertFalse(row['successful'])
        self.assertTrue(row['internal_accounting'])

    def test_single_cpu_default_jobs_one_is_preserved(self):
        self.assertEqual(self.parse(report(jobs=1, cpu=1), cpu=1)['jobs'], 1)

    def test_duplicate_and_nonterminal_summary_refuse(self):
        for text in (report() + report(), 'discovered: 9000\n' + report(),
                     report() + 'post-summary output\n', report() + '\n',
                     report().replace('weights: equal\n', 'weights: equal\n\n')):
            with self.subTest(text=text), self.assertRaises(Refused):
                self.parse(text)

    def test_truncation_and_malformed_fields_refuse(self):
        for text in (report().rsplit('\n', 2)[0], report().replace('discovered: 9000', 'discovered: nope'),
                     report().replace('unaccounted: 0', 'unaccounted: 1'),
                     report().replace('wall 18.500s', 'wall nans'),
                     report().replace('wall 18.500s', 'wall 0.000s'),
                     report().replace('wall 18.500s', 'wall -1.000s'),
                     report().replace('12.250s', 'infs'),
                     report().replace('next-slowest worker 9.000s', 'next-slowest worker -1.000s')):
            with self.subTest(text=text), self.assertRaises(Refused):
                self.parse(text)

    def test_population_workers_weights_and_exit_must_match(self):
        for kwargs in ({'count': 9001}, {'stdout': report(jobs=2)}, {'cpu': 8},
                       {'stdout': report(weights='recorded')}, {'code': 2}, {'code': -1},
                       {'code': True}, {'count': True}, {'count': 0}, {'cpu': None}):
            with self.subTest(kwargs=kwargs), self.assertRaises(Refused):
                self.parse(**kwargs)

    def test_loader_missing_worker_and_identity_faults_refuse_even_with_good_summary(self):
        diagnostics = ('module did not load: private_module',
                       'worker 2 ended without reporting (exit 1; no report)',
                       'duplicate id: private_id', 'duplicate worker id: private_id',
                       'unexpected id: private_id')
        for diagnostic in diagnostics:
            for stream in ('stdout', 'stderr'):
                with self.subTest(diagnostic=diagnostic, stream=stream), self.assertRaises(Refused):
                    self.parse(**{stream: diagnostic + '\n' + report() if stream == 'stdout' else diagnostic + '\n'})

    def test_stderr_cannot_supply_or_duplicate_summary(self):
        with self.assertRaises(Refused):
            self.parse(stderr=report())
        with self.assertRaises(Refused):
            self.parse(stdout='', stderr=report())


class RetainedOutputTests(unittest.TestCase):
    def setUp(self):
        self.expected = {'tools/example.py': 'digest', 'tools/pkg/__init__.py': 'digest'}

    def test_only_narrow_suite_weights_and_tracked_module_bytecode(self):
        for name in ('scratch/runs/suite-weights.json',
                     'tools/__pycache__/example.cpython-314.pyc',
                     'tools/pkg/__pycache__/__init__.cpython-314.opt-1.pyc'):
            self.assertTrue(allowed_retained(name, self.expected), name)

    def test_unknown_ignored_outputs_do_not_get_blanket_waiver(self):
        for name in ('scratch/private.json', 'scratch/runs/suite-weights-123.tmp',
                     'output/report.pdf', 'tools/unknown.pyc',
                     'tools/__pycache__/unknown.cpython-314.pyc',
                     'tools/__pycache__/example.evil.pyc',
                     'tools/__pycache__/example.cpython-314.opt-9.pyc',
                     '/scratch/runs/suite-weights.json', '../scratch/runs/suite-weights.json',
                     'scratch//runs/suite-weights.json', 'scratch\\runs\\suite-weights.json',
                     'tools/example.py'):
            self.assertFalse(allowed_retained(name, self.expected), name)


if __name__ == '__main__':
    unittest.main()

class DiagnosticReceiptTests(unittest.TestCase):
    def test_native_failure_targets_are_bounded_tokens_not_payloads(self):
        from full_suite_receipts import failure_target_receipt
        output=('private assertion contents\nre-run (from tools/): python -m unittest test_public.Class.test_case\n'
                're-run (from tools/): python -m unittest /private/path\n')
        row=failure_target_receipt(output)
        self.assertEqual(row['failure_target_line_count'],2)
        self.assertEqual(row['unread_target_count'],1)
        self.assertEqual(len(row['failure_target_tokens']),1)
        self.assertNotIn('private',str(row))
        self.assertNotIn('test_public',str(row))
        row=failure_target_receipt('re-run (from tools/): python -m unittest test_a.C.t\n'*101)
        self.assertEqual(len(row['failure_target_tokens']),100)
        self.assertTrue(row['truncated'])
