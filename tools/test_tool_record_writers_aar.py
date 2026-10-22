"""Synthetic native writer transactions for AAR, outbound logs and portal readings."""
# phi-scan: synthetic
import artifact_lock_test_support
import artifact_lock
from concurrent.futures import ThreadPoolExecutor
import contextlib
import io
import json
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest import mock

import aar_scan
import medatrax_posting
import outbound_search
import run_record_reader as records
import test_aar_scan as aar_fixtures
import test_medatrax_readback_command as portal_fixtures


class WriterTransactions(unittest.TestCase):
    def test_extract_directory_failure_is_safe_and_preserves_prior_round(self):
        fixture = self.aar()
        fixture.write_clean()
        first = aar_scan.extract_path(fixture.run, fixture.submission)
        baseline = aar_scan.baseline_path(fixture.run, fixture.submission)
        before = first.read_bytes(), baseline.read_bytes()
        aar_scan.review_path(fixture.run, fixture.submission).unlink()
        target = aar_scan.extract_path(fixture.run, fixture.submission, 2)
        original_mkdir = Path.mkdir
        def denied(directory, *args, **kwargs):
            if directory == target.parent:
                raise OSError('PRIVATE-DIRECTORY-FAILURE')
            return original_mkdir(directory, *args, **kwargs)
        with mock.patch.object(Path, 'mkdir', denied):
            status, report = self.capture(lambda: aar_scan.main([
                str(fixture.run), '--submission', fixture.submission, '--extract',
                '--memory-index', str(fixture.memory), '--transcript', str(fixture.transcript)]))
        self.assertEqual(2, status, report)
        self.assertIn('unreadable — could not be opened', report)
        self.assertNotIn('PRIVATE-DIRECTORY-FAILURE', report)
        self.assertEqual(before, (first.read_bytes(), baseline.read_bytes()))
        self.assertFalse(target.exists())

    def capture(self, action):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            status = action()
        return status, output.getvalue()

    def aar(self):
        fixture = aar_fixtures.SubmissionRecord('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.addCleanup(fixture.tearDown)
        patcher = mock.patch.object(aar_scan, '_tracked_files', return_value=())
        patcher.start()
        self.addCleanup(patcher.stop)
        return fixture

    def portal(self):
        fixture = portal_fixtures.ReadbackCommand('runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.input.write_text(json.dumps(fixture.payload), encoding='utf-8')
        return fixture

    def portal_write(self, fixture, key='shift', replace=False):
        return medatrax_posting.main(['write', '--run', str(fixture.run), '--submission', key,
            '--batch', '--input', str(fixture.input), *(['--replace'] if replace else [])])

    def test_portal_native_lock_and_interrupted_replace_preserve_bytes(self):
        fixture = self.portal()
        self.assertEqual(0, self.capture(lambda: self.portal_write(fixture))[0])
        target = fixture.run / 'reread.md'
        before = target.read_bytes()
        with artifact_lock.hold(target, 'synthetic holder'):
            status, output = self.capture(lambda: self.portal_write(fixture, replace=True))
        self.assertEqual(2, status, output)
        self.assertIn('reread.md: unreadable — held by another task:', output)
        self.assertEqual(before, target.read_bytes())
        with mock.patch.object(records.os, 'replace', side_effect=OSError('PRIVATE-PLANTED')):
            status, output = self.capture(lambda: self.portal_write(fixture, replace=True))
        self.assertEqual(2, status, output)
        self.assertNotIn('PRIVATE-PLANTED', output)
        self.assertEqual(before, target.read_bytes())
        self.assertEqual([], list(fixture.run.glob('*.partial')))
        status, _output = self.capture(lambda: self.portal_write(fixture))
        self.assertEqual(2, status)  # Replacing an existing member still requires the explicit option.
        self.assertEqual(before, target.read_bytes())

    def test_concurrent_portal_members_survive(self):
        fixture = self.portal()
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(lambda key: self.portal_write(fixture, key), ('left', 'right')))
        self.assertEqual([0, 0], statuses)
        self.assertEqual({'left', 'right'}, {item.artifact for item in
            medatrax_posting.read_posted_readings((fixture.run / 'reread.md').read_text(encoding='utf-8'))})

    def test_outbound_appends_validate_under_lock_and_keep_distinct_updates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / outbound_search.SEARCHES
            target.write_text('{"search_id":"initial","query":"synthetic","passed":true}\n', encoding='utf-8')
            def invoke(key):
                return outbound_search.main(['check', 'synthetic', '--run', str(root), '--search-id', key])
            before = target.read_bytes()
            with mock.patch.object(outbound_search, 'refusal', return_value=None):
                with artifact_lock.hold(target, 'synthetic holder'):
                    status, output = self.capture(lambda: invoke('initial'))
                self.assertEqual(2, status, output)
                self.assertIn('held by another task:', output)
                self.assertEqual(before, target.read_bytes())
                original = outbound_search._decode_records
                def decode(path, text):
                    with self.assertRaises(artifact_lock.ArtifactBusy):
                        with artifact_lock.hold(path, 'competing validation'):
                            self.fail('append validation ran outside the owning lock')
                    return original(path, text)
                with mock.patch.object(outbound_search, '_decode_records', side_effect=decode):
                    self.assertEqual(0, self.capture(lambda: invoke('checked'))[0])
                with ThreadPoolExecutor(max_workers=2) as pool:
                    def checked_invoke(key):
                        with records.capture_errors() as faults:
                            status = invoke(key)
                        if status != 0:
                            self.assertEqual(2, status)
                            self.assertEqual({target.resolve()}, set(faults))
                            self.assertTrue(faults[target.resolve()].cause.startswith('held by another task: process '))
                        else:
                            self.assertEqual({}, faults)
                        return key, status
                    outcomes = list(pool.map(checked_invoke, ('left', 'right')))
                successful = {key for key, status in outcomes if status == 0}
                self.assertTrue(successful, outcomes)
                rows = outbound_search.records(target)
                self.assertEqual({'initial', 'checked'} | successful, {row['search_id'] for row in rows})
                self.assertEqual(2 + len(successful), len(rows))
                # Fresh serial requests require both distinct updates regardless of
                # how the OS scheduled the concurrent wave. No failed call is retried.
                for key in ('serial-left', 'serial-right'):
                    self.assertEqual(0, self.capture(lambda: invoke(key))[0])
                rows = outbound_search.records(target)
                self.assertEqual({'initial', 'checked', 'serial-left', 'serial-right'} | successful,
                                 {row['search_id'] for row in rows})
                self.assertEqual(4 + len(successful), len(rows))
                self.assertTrue(target.read_bytes().startswith(before))
                target.write_bytes(b'{')
                status, output = self.capture(lambda: invoke('bad'))
                self.assertEqual(2, status, output)
                self.assertEqual(b'{', target.read_bytes())
                self.assertEqual(2, self.capture(lambda: outbound_search.main([
                    'pull', '--run', str(root), '--search-id', 'missing', '--dump-id', 'synthetic',
                    '--query-readback', 'synthetic']))[0])
                self.assertFalse((root / outbound_search.PULLS).exists())

    def test_aar_allocation_and_actual_records_refuse_held_locks(self):
        fixture = self.aar()
        fixture.extract()
        extract = aar_scan.extract_path(fixture.run, fixture.submission)
        aar_scan.measure_memory(fixture.run, fixture.submission, 1)
        measurement = aar_scan.memory_measurement_path(fixture.run, fixture.submission)
        actions = (
            (fixture.run / 'aar' / '.record-allocation', lambda: aar_scan.write_extract(
                fixture.run, fixture.transcript, fixture.submission, fixture.memory)),
            (extract, lambda: aar_scan.rebuild_extract(fixture.run, fixture.submission, 1)),
            (measurement, lambda: aar_scan.measure_memory(fixture.run, fixture.submission, 1)),
            (aar_scan.baseline_path(fixture.run, fixture.submission, 2), lambda: aar_scan.write_extract(
                fixture.run, fixture.transcript, fixture.submission, fixture.memory)),
        )
        for target, action in actions:
            with self.subTest(target=target.name):
                before = {path: path.read_bytes() for path in (extract, measurement)}
                with artifact_lock.hold(target, 'synthetic holder'):
                    with self.assertRaisesRegex(records.UnreadableRecord, 'held by another task:'):
                        action()
                self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_outbound_append_preserves_a_valid_unterminated_jsonl_tail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / outbound_search.SEARCHES
            before = b'{"search_id":"initial","query":"synthetic","passed":true}'
            target.write_bytes(before)
            with mock.patch.object(outbound_search, 'refusal', return_value=None):
                status, output = self.capture(lambda: outbound_search.main([
                    'check', 'synthetic', '--run', str(root), '--search-id', 'next']))
            self.assertEqual(0, status, output)
            self.assertTrue(target.read_bytes().startswith(before + b'\n'))
            self.assertEqual({'initial', 'next'}, {row['search_id'] for row in outbound_search.records(target)})

    def test_every_native_append_refuses_held_lock_and_failure_before_open(self):
        routes = (
            ('check', ['check', 'synthetic'], outbound_search.SEARCHES),
            ('pull', ['pull', '--dump-id', 'synthetic', '--query-readback', 'synthetic'], outbound_search.PULLS),
            ('failed-pull', ['failed-pull', '--decision', 'synthetic', '--instrument', 'synthetic',
                             '--query-readback', 'synthetic', '--reason', 'no-match', '--results-read', '0'], outbound_search.PULLS),
        )
        for name, command, filename in routes:
            with self.subTest(route=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / outbound_search.SEARCHES).write_text(
                    '{"search_id":"passed","query":"synthetic","passed":true}\n', encoding='utf-8')
                target = root / filename
                if filename == outbound_search.PULLS:
                    target.write_text('{"search_id":"passed","dump_id":"prior"}\n', encoding='utf-8')
                before = target.read_bytes()
                arguments = [*command, '--run', str(root), '--search-id',
                             'next' if name == 'check' else 'passed']
                original_open = Path.open
                def interrupted(path, mode='r', *args, **kwargs):
                    if path == target and mode == 'ab':
                        raise OSError('PRIVATE-PLANTED')
                    return original_open(path, mode, *args, **kwargs)
                with mock.patch.object(outbound_search, 'refusal', return_value=None), \
                     mock.patch.object(outbound_search, 'private_line', side_effect=lambda value: value):
                    with artifact_lock.hold(target, 'synthetic holder'):
                        status, output = self.capture(lambda: outbound_search.main(arguments))
                    self.assertEqual(2, status, output)
                    self.assertIn('held by another task:', output)
                    self.assertEqual(before, target.read_bytes())
                    with mock.patch.object(Path, 'open', interrupted):
                        status, output = self.capture(lambda: outbound_search.main(arguments))
                    self.assertEqual(2, status, output)
                    self.assertIn('could not be opened', output)
                    self.assertNotIn('PRIVATE-PLANTED', output)
                    self.assertEqual(before, target.read_bytes())

    def test_aar_rebuild_interruption_keeps_source_and_removes_only_new_archive(self):
        fixture = self.aar()
        fixture.extract()
        extract = aar_scan.extract_path(fixture.run, fixture.submission)
        before = extract.read_bytes()
        archive = extract.parent / 'refused' / extract.name
        archive.parent.mkdir()
        archive.write_bytes(b'earlier retained evidence')
        with mock.patch.object(records.os, 'replace', side_effect=OSError('PRIVATE-PLANTED')):
            with self.assertRaisesRegex(records.UnreadableRecord, 'could not be opened'):
                aar_scan.rebuild_extract(fixture.run, fixture.submission, 1)
        self.assertEqual(before, extract.read_bytes())
        self.assertEqual([archive], list(archive.parent.iterdir()))
        self.assertEqual(b'earlier retained evidence', archive.read_bytes())
        aar_scan.rebuild_extract(fixture.run, fixture.submission, 1)
        self.assertEqual(before, archive.with_name(extract.stem + '.2' + extract.suffix).read_bytes())

    def test_memory_measurement_rewrite_refuses_damage_and_failed_replace(self):
        fixture = self.aar()
        fixture.extract()
        target = aar_scan.measure_memory(fixture.run, fixture.submission, 1)
        before = target.read_bytes()
        with mock.patch.object(records.os, 'replace', side_effect=OSError('PRIVATE-PLANTED')):
            with self.assertRaisesRegex(records.UnreadableRecord, 'could not be opened'):
                aar_scan.measure_memory(fixture.run, fixture.submission, 1)
        self.assertEqual(before, target.read_bytes())
        target.write_bytes(b'{')
        with self.assertRaisesRegex(records.UnreadableRecord, 'does not decode'):
            aar_scan.measure_memory(fixture.run, fixture.submission, 1)
        self.assertEqual(b'{', target.read_bytes())

    def test_archive_creation_collision_never_removes_another_creators_bytes(self):
        fixture = self.aar()
        fixture.extract()
        extract = aar_scan.extract_path(fixture.run, fixture.submission)
        before = extract.read_bytes()
        archive = extract.parent / 'refused' / extract.name
        original_open = Path.open
        def collide(path, mode='r', *args, **kwargs):
            if path == archive and mode == 'xb':
                with original_open(path, 'wb') as stream:
                    stream.write(b'other creator evidence')
            return original_open(path, mode, *args, **kwargs)
        with mock.patch.object(Path, 'open', collide):
            with self.assertRaisesRegex(records.UnreadableRecord, 'could not be opened'):
                aar_scan.rebuild_extract(fixture.run, fixture.submission, 1)
        self.assertEqual(before, extract.read_bytes())
        self.assertEqual(b'other creator evidence', archive.read_bytes())

    def test_native_extract_lock_refusal_writes_no_round(self):
        fixture = self.aar()
        arguments = [str(fixture.run), '--submission', fixture.submission,
                     '--transcript', str(fixture.transcript), '--memory-index', str(fixture.memory), '--extract']
        target = aar_scan.extract_path(fixture.run, fixture.submission)
        with artifact_lock.hold(target, 'synthetic holder'):
            status, output = self.capture(lambda: aar_scan.main(arguments))
        self.assertEqual(2, status, output)
        self.assertIn('held by another task:', output)
        self.assertFalse(target.exists())
        self.assertFalse(aar_scan.baseline_path(fixture.run, fixture.submission).exists())

    def test_native_rebuild_sanitizes_archive_publication_failure(self):
        fixture = self.aar()
        fixture.extract()
        extract = aar_scan.extract_path(fixture.run, fixture.submission)
        before = extract.read_bytes()
        archive = extract.parent / 'refused' / extract.name
        original_open = Path.open
        def interrupted(path, mode='r', *args, **kwargs):
            if path == archive and mode == 'xb':
                raise OSError('PRIVATE-PLANTED-ARCHIVE')
            return original_open(path, mode, *args, **kwargs)
        with mock.patch.object(Path, 'open', interrupted):
            status, report = self.capture(lambda: aar_scan.main([
                str(fixture.run), '--submission', fixture.submission, '--extract',
                '--rebuild-round', '1', '--memory-index', str(fixture.memory)]))
        self.assertEqual(status, 2, report)
        self.assertIn('unreadable — could not be opened', report)
        self.assertNotIn('PRIVATE-PLANTED-ARCHIVE', report)
        self.assertEqual(extract.read_bytes(), before)
        self.assertFalse(archive.exists())

    def test_each_native_aar_writer_refuses_held_and_interrupted_record_publication(self):
        for route in ('extract', 'baseline', 'rebuild', 'measurement'):
            for failure in ('held', 'replace'):
                with self.subTest(route=route, failure=failure):
                    fixture = self.aar()
                    fixture.write_clean()
                    first = aar_scan.extract_path(fixture.run, fixture.submission)
                    baseline = aar_scan.baseline_path(fixture.run, fixture.submission)
                    arguments = [str(fixture.run), '--submission', fixture.submission]
                    if route == 'measurement':
                        target = aar_scan.memory_measurement_path(fixture.run, fixture.submission)
                        arguments += ['--measure-memory', '--round', '1']
                    else:
                        arguments += ['--extract', '--memory-index', str(fixture.memory), '--transcript', str(fixture.transcript)]
                        if route == 'rebuild':
                            target = first
                            arguments += ['--rebuild-round', '1']
                        elif route == 'baseline':
                            aar_scan.review_path(fixture.run, fixture.submission).unlink()
                            target = aar_scan.baseline_path(fixture.run, fixture.submission, 2)
                        else:
                            aar_scan.review_path(fixture.run, fixture.submission).unlink()
                            target = aar_scan.extract_path(fixture.run, fixture.submission, 2)
                    before = target.read_bytes() if target.exists() else None
                    prior_round = first.read_bytes(), baseline.read_bytes()
                    original_replace = records.os.replace
                    def interrupted(source, destination):
                        if Path(destination) == target:
                            raise OSError('PRIVATE-PLANTED-PUBLICATION')
                        return original_replace(source, destination)
                    manager = (artifact_lock.hold(target, 'synthetic AAR holder') if failure == 'held'
                               else mock.patch.object(records.os, 'replace', side_effect=interrupted))
                    with manager:
                        status, report = self.capture(lambda: aar_scan.main(arguments))
                    self.assertEqual(status, 2, report)
                    self.assertIn('held by another task:' if failure == 'held' else 'could not be opened', report)
                    self.assertNotIn('PRIVATE-PLANTED-PUBLICATION', report)
                    self.assertEqual(target.read_bytes() if target.exists() else None, before)
                    self.assertEqual((first.read_bytes(), baseline.read_bytes()), prior_round)

    def test_aar_concurrent_rounds_allocate_distinct_records(self):
        fixture = self.aar()
        def invoke(_key):
            try:
                return aar_scan.write_extract(fixture.run, fixture.transcript, fixture.submission, fixture.memory)
            except records.UnreadableRecord as failure:
                self.assertEqual((fixture.run / 'aar' / '.record-allocation').resolve(), failure.path)
                self.assertTrue(failure.cause.startswith('held by another task: process '))
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(invoke, range(2)))
        results = [result for result in outcomes if result is not None]
        self.assertTrue(results, outcomes)
        self.assertEqual({aar_scan.extract_path(fixture.run, fixture.submission, round_number)
                          for round_number in range(1, len(results) + 1)}, {path for path, _count in results})
        self.assertEqual(len(results), len({path for path, _count in results}))
        self.assertEqual({path for path, _count in results}, set((fixture.run / 'aar').glob('*.extract.md')))
        for round_number in range(1, len(results) + 1):
            self.assertTrue(aar_scan.baseline_path(fixture.run, fixture.submission, round_number).is_file())
        self.assertEqual(len(results), len(list((fixture.run / 'aar').glob('*.baseline.json'))))
        # A separate serial control always requires two successful, distinct rounds.
        serial = self.aar()
        paths = [aar_scan.write_extract(serial.run, serial.transcript, serial.submission, serial.memory)[0]
                 for _ in range(2)]
        self.assertEqual([aar_scan.extract_path(serial.run, serial.submission, n) for n in (1, 2)], paths)
        for n in (1, 2):
            self.assertTrue(aar_scan.baseline_path(serial.run, serial.submission, n).is_file())

    def test_suspended_native_owner_refuses_contender_without_losing_evidence(self):
        # A process can be descheduled longer than locked_record's wall-clock
        # budget. Wait for the real refusal before releasing the native owner;
        # neither the clock nor the production timeout is patched.
        for kind in ('aar', 'outbound'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                if kind == 'aar':
                    fixture = self.aar()
                    target = fixture.run / 'aar' / '.record-allocation'
                    def invoke(key):
                        return aar_scan.write_extract(fixture.run, fixture.transcript,
                                                      fixture.submission, fixture.memory)
                else:
                    root = Path(directory)
                    target = root / outbound_search.SEARCHES
                    target.write_bytes(b'{"search_id":"prior","query":"synthetic","passed":true}\n')
                    before = target.read_bytes()
                    def invoke(key):
                        return outbound_search.main(['check', 'synthetic', '--run', str(root), '--search-id', key])
                acquired, release = Event(), Event()
                native = artifact_lock.hold
                @contextlib.contextmanager
                def paused(path, action, **kwargs):
                    with native(path, action, **kwargs) as held:
                        if Path(path) == target and not acquired.is_set():
                            acquired.set()
                            release.wait()
                        yield held
                with mock.patch.object(artifact_lock, 'hold', paused), \
                     mock.patch.object(outbound_search, 'refusal', return_value=None), \
                     ThreadPoolExecutor(max_workers=2) as pool:
                    owner = pool.submit(invoke, 'owner')
                    try:
                        self.assertTrue(acquired.wait(10), 'native owner never acquired')
                        if kind == 'aar':
                            with self.assertRaises(records.UnreadableRecord) as caught:
                                pool.submit(invoke, 'contender').result(timeout=10)
                            self.assertEqual(target.resolve(), caught.exception.path)
                            self.assertTrue(caught.exception.cause.startswith('held by another task: process '))
                            self.assertFalse(list((fixture.run / 'aar').glob('*.extract.md')))
                            self.assertFalse(list((fixture.run / 'aar').glob('*.baseline.json')))
                        else:
                            def contend():
                                with records.capture_errors() as faults:
                                    status = invoke('contender')
                                return status, faults
                            status, faults = pool.submit(contend).result(timeout=10)
                            self.assertEqual(2, status)
                            self.assertEqual({target.resolve()}, set(faults))
                            self.assertTrue(faults[target.resolve()].cause.startswith('held by another task: process '))
                            self.assertEqual(before, target.read_bytes())
                    finally:
                        release.set()
                    result = owner.result(timeout=10)
                if kind == 'aar':
                    self.assertEqual(aar_scan.extract_path(fixture.run, fixture.submission), result[0])
                    self.assertTrue(aar_scan.baseline_path(fixture.run, fixture.submission).is_file())
                    self.assertFalse(aar_scan.extract_path(fixture.run, fixture.submission, 2).exists())
                else:
                    self.assertEqual(0, result)
                    self.assertTrue(target.read_bytes().startswith(before))
                    self.assertEqual(['prior', 'owner'], [row['search_id'] for row in outbound_search.records(target)])

    def test_busy_legacy_retirement_preserves_independent_review_grade(self):
        fixture = self.aar()
        fixture.write_clean()
        command = [str(fixture.run), '--submission', fixture.submission]
        self.assertEqual(0, self.capture(lambda: aar_scan.main(command))[0])
        pointer = fixture.run / 'aar/orphaned-synthetic.json'
        pointer.write_bytes(b'{"retained":true}\n')
        before = pointer.read_bytes()
        review = aar_scan.review_path(fixture.run, fixture.submission)
        original = review.read_text(encoding='utf-8')
        for finding, expected in ((False, 2), (True, 1)):
            with self.subTest(independent_finding=finding):
                review.write_text(original.replace('UNREAD: 0', 'UNREAD: 1') if finding else original, encoding='utf-8')
                with artifact_lock.hold(pointer, 'synthetic retirement holder'):
                    status, report = self.capture(lambda: aar_scan.main(command))
                self.assertEqual(status, expected, report)
                self.assertIn('legacy AAR pointer retirement: not graded', report)
                self.assertIn('held by another task:', report)
                if finding:
                    self.assertIn('unread candidates               1', report)
                self.assertEqual(pointer.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
