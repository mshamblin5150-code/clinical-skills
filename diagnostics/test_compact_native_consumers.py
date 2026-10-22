"""Portable consumer controls with injected native I/O, never Windows execution."""
from pathlib import Path
import re
import tempfile
import time
from types import SimpleNamespace
import unittest

import compact_native_consumers as subject
import measure_lazy_suite_ids as q
from test_compact_capture_retention import FakeNative
from windows_job_probe import ProbeResult, ProbeSnapshot


class PortableRuntime:
    """Only tests manufacture owner/native records; no native success claim."""
    def __init__(self):
        self.work_deadline = time.monotonic() + 120
        self.hard_deadline = self.work_deadline + 60
        self.clock, self.sleep, self.environment = time.monotonic, lambda _: None, {}
        self.owners, self.apis = [], []

    def api(self):
        api = FakeNative()
        self.apis.append(api)
        return api

    def snapshot_reader(self, root, relative, limit, deadline):
        # Preserve the production capture-only path grammar at this seam.
        if not re.fullmatch(r'command-[0-9]{4,10}/(?:stdout|stderr)\.bin', relative):
            raise AssertionError('capture snapshot reader cannot read receipt paths')
        with (root / relative).open('rb') as stream:
            return stream.read(limit + 1), self.apis[-1].record(stream.fileno())

    def launch(self, report_dir, stdout, stderr, exit_code=0):
        report_dir.mkdir()
        paths = [report_dir / (name + '.bin') for name in ('stdout', 'stderr')]
        for path, raw in zip(paths, (stdout, stderr)):
            path.write_bytes(raw)
        pid = len(self.owners) + 100
        snapshot = ProbeSnapshot(pid, exit_code, True, 0, 1, .1, .2, .3, True, 'closed')
        native = ProbeResult(snapshot, 'completed', str(paths[0]), str(paths[1]), ())
        owner = SimpleNamespace(report_dir=report_dir, stdout_path=paths[0], stderr_path=paths[1],
            result=native, _info=SimpleNamespace(dwProcessId=pid), poll=lambda: snapshot,
            finish=lambda **_: native)
        self.owners.append(owner)
        reads = tuple(self.snapshot_reader(report_dir.parent, report_dir.name + '/' + path.name, 2 ** 24,
                                          self.work_deadline) for path in paths)
        return owner, native, reads


class NativeConsumerControls(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(prefix='compact-consumer-portable-')
        self.addCleanup(self.fixture.cleanup)
        self.parent = Path(self.fixture.name).resolve()
        self.runtime = PortableRuntime()

    def run_control(self, name):
        return subject.run_consumer_control(name, self.parent / name, self.runtime)

    def test_original_source_predicates_complete_before_six_retirements(self):
        report = self.run_control('source_guard_success')
        self.assertEqual(('source_guard_success', True, 6, 6, 0, 18), tuple(report[key]
            for key in ('id', 'passed', 'commands', 'retired_pairs', 'retained_pairs', 'receipt_files')))
        self.assertEqual('synthetic_output_consumer_validation_not_git_qualification', report['scope'])
        self.assertEqual(6, len(self.runtime.owners))
        self.assertEqual(['stdout.bin', 'stderr.bin'] * 6, self.runtime.apis[0].disposed)
        self.assertEqual(['source_predicates_accepted'], report['outcomes'])

    def test_original_source_refusals_retain_all_ten_exact_pairs(self):
        report = self.run_control('source_guard_refusal')
        self.assertEqual((10, 0, 10, 0), tuple(report[key] for key in
                         ('commands', 'retired_pairs', 'retained_pairs', 'receipt_files')))
        self.assertEqual(['wrong_source_head', 'source_refs_changed', 'first_status_not_clean'],
                         report['outcomes'])
        self.assertEqual([2, 2, 6], [row['pending_pairs'] for row in report['stores']])
        self.assertEqual(b'wrong-head\n', self.runtime.owners[1].stdout_path.read_bytes())
        self.assertEqual(b'?? synthetic.txt\n', self.runtime.owners[6].stdout_path.read_bytes())
        self.assertEqual([[], [], []], [api.disposed for api in self.runtime.apis])

    def test_detached_status_one_is_accepted_only_by_its_original_consumer(self):
        report = self.run_control('detached_expected_nonzero')
        self.assertEqual((1, 1, 0, 3, ['detached_head_expected_status_one']),
            tuple(report[key] for key in
                  ('commands', 'retired_pairs', 'retained_pairs', 'receipt_files', 'outcomes')))
        self.assertEqual(1, self.runtime.owners[0].result.snapshot.root_exit_code)
        self.assertEqual(['stdout.bin', 'stderr.bin'], self.runtime.apis[0].disposed)

    def test_outer_consumer_receipt_preserves_full_original_shaped_json(self):
        report = self.run_control('outer_control_full_receipt')
        self.assertEqual((1, 1, 0, 3, ['full_outer_control_json_retained']),
            tuple(report[key] for key in
                  ('commands', 'retired_pairs', 'retained_pairs', 'receipt_files', 'outcomes')))
        import json
        root = self.parent / 'outer_control_full_receipt' / 'outer' / 'captures'
        eligibility = json.loads((root / 'compact-000001-eligibility.json').read_bytes())
        self.assertEqual('outer_control', eligibility['final_consumer'])
        self.assertEqual('synthetic_consumer_fixture', eligibility['evidence']['result']['fixture_label'])
        self.assertEqual({'kept': [True, 'whole receipt', {'ordinal': 7}]},
                         eligibility['evidence']['result']['additional_evidence'])

    def test_original_runner_retires_expected_rows_before_next_lookup_and_retains_unexpected(self):
        report = self.run_control('measured_original_outcomes')
        self.assertEqual((3, 2, 1, 6), tuple(report[key] for key in
                         ('commands', 'retired_pairs', 'retained_pairs', 'receipt_files')))
        self.assertEqual(['reader_expected_status_one', 'nonreader_expected_status_zero',
                          'retired_before_next_lookup', 'unexpected_probe_result_raw_retained'],
                         report['outcomes'])
        self.assertEqual([1, 0, 1], [owner.result.snapshot.root_exit_code
                                   for owner in self.runtime.owners])
        self.assertEqual([4, 0], [len(api.disposed) for api in self.runtime.apis])
        self.assertEqual(b'Ran 3 tests in 0.001s\n\nOK (skipped=1)\n',
                         self.runtime.owners[-1].stderr_path.read_bytes())

    def test_all_controls_keep_one_shared_owner_ledger_with_exact_population(self):
        names = ('source_guard_success', 'source_guard_refusal', 'detached_expected_nonzero',
                 'outer_control_full_receipt', 'measured_original_outcomes')
        reports = [self.run_control(name) for name in names]
        self.assertEqual((21, 10, 11, 30), tuple(sum(row[key] for row in reports) for key in
                         ('commands', 'retired_pairs', 'retained_pairs', 'receipt_files')))
        self.assertEqual(21, len({id(owner) for owner in self.runtime.owners}))
        self.assertTrue(all(owner.result.snapshot.cleanup_verified for owner in self.runtime.owners))
        self.assertEqual(20, sum(len(api.disposed) for api in self.runtime.apis))
        self.assertEqual(0, sum(len(api.handles) for api in self.runtime.apis))

    def test_original_detached_consumer_rejects_unexpected_zero_and_retains_owner(self):
        launch = self.runtime.launch
        def wrong_exit(report_dir, stdout, stderr, exit_code=0):
            return launch(report_dir, stdout, stderr, exit_code=0)
        self.runtime.launch = wrong_exit
        with self.assertRaisesRegex(q.Refused, '^compact_consumer_shape_changed$'):
            self.run_control('detached_expected_nonzero')
        self.assertEqual(1, len(self.runtime.owners))
        self.assertEqual(0, self.runtime.owners[0].result.snapshot.root_exit_code)
        self.assertEqual(b'', self.runtime.owners[0].stdout_path.read_bytes())
        self.assertEqual([], self.runtime.apis[0].disposed)

    def test_partial_native_disposition_never_retires_a_later_source_pair(self):
        make_api = self.runtime.api
        def failing_api():
            api = make_api()
            api.failures.add(('mark', 'stderr.bin'))
            return api
        self.runtime.api = failing_api
        with self.assertRaisesRegex(q.Refused, '^compact_retirement_inconclusive$'):
            self.run_control('source_guard_success')
        # The original predicate consumes all six outputs before any retirement.
        # Failure on the first pair permits no retirement of later pairs.
        self.assertEqual(6, len(self.runtime.owners))
        self.assertEqual(['stdout.bin'], self.runtime.apis[0].disposed)
        self.assertEqual(0, len(self.runtime.apis[0].handles))

    def test_receipt_readback_cannot_reuse_capture_only_reader_or_ignore_changed_bytes(self):
        make_api = self.runtime.api
        def changed_receipt_api():
            api = make_api()
            api.read_fail_at = ('compact-000001-eligibility.json', 3)
            return api
        self.runtime.api = changed_receipt_api
        with self.assertRaisesRegex(q.Refused, '^native_consumer_control_failed$'):
            self.run_control('detached_expected_nonzero')
        self.assertEqual(1, len(self.runtime.owners))
        self.assertEqual(['stdout.bin', 'stderr.bin'], self.runtime.apis[0].disposed)
        self.assertEqual(0, len(self.runtime.apis[0].handles))

    def test_existing_fixture_is_refused_before_launch_or_native_acquisition(self):
        root = self.parent / 'existing'
        root.mkdir()
        (root / 'do-not-touch').write_bytes(b'existing evidence')
        with self.assertRaisesRegex(q.Refused, '^native_consumer_control_failed$'):
            subject.run_consumer_control('source_guard_success', root, self.runtime)
        self.assertEqual(b'existing evidence', (root / 'do-not-touch').read_bytes())
        self.assertEqual(([], []), (self.runtime.owners, self.runtime.apis))

    def test_symlink_ancestor_is_refused_before_creating_any_fixture(self):
        target = self.parent / 'target'
        target.mkdir()
        link = self.parent / 'alias'
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(q.Refused, '^native_consumer_control_failed$'):
            subject.run_consumer_control('source_guard_success', link / 'new', self.runtime)
        self.assertEqual([], list(target.iterdir()))
        self.assertEqual(([], []), (self.runtime.owners, self.runtime.apis))


if __name__ == '__main__':
    unittest.main()
