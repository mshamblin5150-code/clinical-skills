"""Portable diagnostic boundaries only; never import the application suite."""
import json
import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch

from parallel_reader_capture import analyze_capture


def synthetic_check():
    check = types.SimpleNamespace(subprocess=subprocess, LOOKUPS=frozenset(('icd10_lookup', 'procedure_codes_lookup')))
    def readers(tools, reaching):
        found = set()
        for module in sorted(reaching):
            for lookup in sorted(check.LOOKUPS):
                result = check.subprocess.run([sys.executable, '-c', 'synthetic payload', str(tools), module, lookup],
                    cwd=tools, text=True, encoding='utf-8', errors='replace', capture_output=True, check=False)
                if 'CODE_SET_DATABASE_OPEN_REFUSED' in result.stdout + result.stderr:
                    found.add((module, lookup))
                elif result.returncode:
                    raise RuntimeError('PRIVATE original error')
        return frozenset(found)
    check._readers_under_refusal = readers
    def imports(tree, local):
        return frozenset(node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)) & local
    def reaches(module, graph, seen=frozenset()):
        return module in check.LOOKUPS or (module not in seen and any(reaches(item, graph, seen | {module})
                                                                   for item in graph.get(module, ())))
    def pins(tree):
        return frozenset(node.value.value for node in tree.body if isinstance(node, ast.Expr)
                         and isinstance(node.value, ast.Constant) and node.value.value in check.LOOKUPS)
    check._imports, check._reaches_lookup, check._pins = imports, reaches, pins
    return check


class SyntheticOwner:
    def __init__(self, root, outputs=None):
        self.root, self.deadline = root, time.monotonic() + 60
        self.calls, self.outputs, self.owners = [], outputs or [], []
    def run(self, argv, cwd):
        self.calls.append((argv, cwd))
        output = self.outputs.pop(0) if self.outputs else (0, b'', b'Ran 1 test in 0.1s\r\n\r\nOK\r\n')
        report = self.root / ('command-%04d' % (len(self.owners) + 1)); report.mkdir()
        paths = [report / (stream + '.bin') for stream in ('stdout', 'stderr')]
        for path, raw in zip(paths, output[1:]):
            path.write_bytes(raw)
        self.owners.append(types.SimpleNamespace(result=types.SimpleNamespace(
            stdout_path=str(paths[0]), stderr_path=str(paths[1]),
            snapshot=types.SimpleNamespace(root_exit_code=output[0], cleanup_verified=True,
                                           wall_seconds=0.1, tree_cpu_seconds=0.05))))
        return {'returncode': output[0], 'stdout_path': str(paths[0]), 'stderr_path': str(paths[1]),
                'stdout': 'DO NOT TRUST THIS SECOND READ', 'stderr': 'DO NOT TRUST THIS SECOND READ',
                'wall_seconds': 0.1, 'tree_cpu_seconds': 0.05, 'cleanup_verified': True}


class OriginalLifecycleControls(unittest.TestCase):
    def test_fatal_interruption_does_not_complete_the_active_method(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
            class ActualClass(unittest.TestCase):
                def test_planted_unpinned_readers_and_a_stale_pin_fail_in_both_directions(self):
                    raise KeyboardInterrupt('PRIVATE interruption')
                def test_the_repository_reader_population_and_pins_agree(self): self.fail('must not run')
            record = subject.observe_class(check, ActualClass, root / 'repository',
                {scope: {'modules': ('test_one',), 'pinned': frozenset()} for scope in subject.SCOPES},
                owner, lambda: None, 'synthetic payload')
            self.assertEqual((True, False, 'unread', False), (record['methods'][0]['started'],
                record['methods'][0]['completed'], record['methods'][0]['outcome'], record['methods'][1]['started']))
            self.assertFalse(record['complete'])

    def test_guard_failure_retains_original_outcome_and_restores_bindings(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
            original_loop, original_binding = check._readers_under_refusal, check.subprocess
            class ActualClass(unittest.TestCase):
                def test_planted_unpinned_readers_and_a_stale_pin_fail_in_both_directions(self): pass
                def test_the_repository_reader_population_and_pins_agree(self): self.fail('must not run')
            def guard(): raise OSError('PRIVATE GUARD PATH')
            record = subject.observe_class(check, ActualClass, root / 'repository',
                {scope: {'modules': ('test_one',), 'pinned': frozenset()} for scope in subject.SCOPES},
                owner, guard, 'synthetic payload')
            self.assertEqual(('pass', True, 'unread'), (record['methods'][0]['outcome'],
                             record['methods'][0]['completed'], record['methods'][1]['outcome']))
            self.assertFalse(record['complete'])
            self.assertTrue(record['observer_failure'])
            self.assertNotIn('PRIVATE', json.dumps(record))
            self.assertIs(check._readers_under_refusal, original_loop)
            self.assertIs(check.subprocess, original_binding)

    def test_two_original_methods_and_lifecycle_run_once_with_local_adapter(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            planted, repository = root / 'planted', root / 'repository'
            planted.mkdir(); repository.mkdir()
            check = synthetic_check()
            original_run, original_loop, original_binding = subprocess.run, check._readers_under_refusal, check.subprocess
            owner = SyntheticOwner(root)
            lifecycle = []
            class ActualClass(unittest.TestCase):
                def setUp(self): lifecycle.append('setup')
                def tearDown(self): lifecycle.append('teardown')
                def test_planted_unpinned_readers_and_a_stale_pin_fail_in_both_directions(self):
                    self.addCleanup(lifecycle.append, 'cleanup')
                    self.assertEqual(frozenset(), check._readers_under_refusal(planted, frozenset(('test_plant',))))
                def test_the_repository_reader_population_and_pins_agree(self):
                    self.addCleanup(lifecycle.append, 'cleanup')
                    self.assertEqual(frozenset(), check._readers_under_refusal(repository, frozenset(('test_real',))))
            manifests = {'planted': {'modules': ('test_plant',), 'pinned': frozenset(), 'source_file_count': 3},
                         'repository': {'modules': ('test_real',), 'pinned': frozenset(), 'source_file_count': 3}}
            result = subject.observe_class(check, ActualClass, repository, manifests, owner,
                                           lambda: None, 'synthetic payload')
            self.assertEqual(['setup', 'teardown', 'cleanup'] * 2, lifecycle)
            self.assertEqual((2, 4, True), (result['tests_run'], len(result['pairs']), result['complete']))
            self.assertEqual(['pass', 'pass'], [row['outcome'] for row in result['methods']])
            self.assertEqual([('test_plant', 'icd10_lookup'), ('test_plant', 'procedure_codes_lookup'),
                              ('test_real', 'icd10_lookup'), ('test_real', 'procedure_codes_lookup')],
                             [tuple(argv[-2:]) for argv, _ in owner.calls])
            self.assertIs(check.subprocess, original_binding)
            self.assertIs(check._readers_under_refusal, original_loop)
            self.assertIs(subprocess.run, original_run)
            summary = subject.summarize(result, manifests)
            self.assertEqual((2, 4, 0.2), (len(summary['module_totals']), len(summary['top_children']),
                                         summary['child_tree_cpu_seconds']))
            context = {'observer_sha': 'a' * 40, 'run_id': '123', 'job_start_epoch': 1000,
                       'environment_sha256': 'b' * 64}
            receipt = subject.retained_receipt(owner, result, manifests, context)
            raw = (root / 'reader-receipt.json').read_bytes()
            envelope = json.loads(raw)
            self.assertEqual(('a' * 40, '123', subject.SOURCE_SHA),
                             (envelope['observer_sha'], envelope['run_id'], envelope['source_sha']))
            self.assertTrue(receipt['receipt_verified'])
            self.assertNotIn('DO NOT TRUST', raw.decode())


class CoherentCaptureControls(unittest.TestCase):
    def test_owned_bin_reads_keep_every_native_identity_dimension_and_generated_refusals(self):
        import dataclasses
        import measure_reader_attribution as subject
        from test_windows_metadata import WindowsMetadataControls
        fixture = WindowsMetadataControls(); good = fixture.specimen()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); report = root / 'command-0001'; report.mkdir()
            (report / 'stdout.bin').write_bytes(b'abc')
            api = fixture.fake_api()
            with patch.object(subject.contract, 'windows_metadata_api', return_value=api):
                self.assertEqual(b'abc', subject.contract.read_owned_capture(root, 'command-0001/stdout.bin', 128, time.monotonic() + 10))
            self.assertEqual((8, 2), (api.record.call_count, api.close.call_count))
            for field in (*subject.contract.METADATA_FIELDS, 'st_birthtime_ns'):
                with self.subTest(field=field):
                    changed = dataclasses.replace(good, **{field: getattr(good, field) + 1})
                    api = fixture.fake_api([good] * 4 + [changed] * 2)
                    with patch.object(subject.contract, 'windows_metadata_api', return_value=api), \
                         patch.object(subject.q, 'emit'), self.assertRaises(subject.q.Refused):
                        subject.contract.read_owned_capture(root, 'command-0001/stdout.bin', 128, time.monotonic() + 10)
            for relative in ('command-0001/stdout.bin', 'source.py'):
                api = fixture.fake_api()
                with patch.object(subject.contract, 'windows_metadata_api', return_value=api), \
                     patch.object(subject.q, 'emit'), self.assertRaises(subject.q.Refused):
                    subject.contract.safe_read(root, relative, 128, time.monotonic() + 10)
                api.open.assert_not_called()
            for relative in ('../stdout.bin', 'command-0001/unknown.bin', 'command-0001/stdout.exe', 'stdout.bin'):
                api = fixture.fake_api()
                with patch.object(subject.contract, 'windows_metadata_api', return_value=api), \
                     patch.object(subject.q, 'emit'), self.assertRaises(subject.q.Refused):
                    subject.contract.read_owned_capture(root, relative, 128, time.monotonic() + 10)
                api.open.assert_not_called()

    def test_native_path_semantics_integrate_source_population_owned_children_and_receipt(self):
        import os
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
            sources = {'icd10_lookup.py': b'', 'test_reader.py': b'import icd10_lookup\n'}
            hashes = {name: subject.q.digest(raw) for name, raw in sources.items()}
            for scope in subject.SCOPES:
                (root / scope).mkdir()
                for name, raw in sources.items(): (root / scope / name).write_bytes(raw)
            api = unittest.mock.Mock()
            api.open.side_effect = lambda path: os.open(path, os.O_RDONLY)
            api.close.side_effect = os.close
            api.from_fd.side_effect = lambda fd: fd
            def record(fd):
                st = os.fstat(fd)
                return subject.contract.WindowsSnapshot(st.st_dev, st.st_ino, st.st_mode, st.st_nlink,
                    st.st_size, st.st_mtime_ns, st.st_ctime_ns, 0, st.st_ctime_ns, 1, 0, False)
            api.record.side_effect = record
            class ActualClass(unittest.TestCase):
                def test_planted_unpinned_readers_and_a_stale_pin_fail_in_both_directions(self):
                    self.assertEqual(frozenset(), check._readers_under_refusal(root / 'planted', frozenset(('test_reader',))))
                def test_the_repository_reader_population_and_pins_agree(self):
                    self.assertEqual(frozenset(), check._readers_under_refusal(root / 'repository', frozenset(('test_reader',))))
            with patch.object(subject.contract, 'windows_metadata_api', return_value=api):
                manifests = {scope: subject.source_population(check, root / scope, owner.deadline, hashes)
                             for scope in subject.SCOPES}
                result = subject.observe_class(check, ActualClass, root / 'repository', manifests, owner,
                                               lambda: None, 'synthetic payload')
                receipt = subject.retained_receipt(owner, result, manifests,
                    {'observer_sha': 'a' * 40, 'run_id': '123', 'job_start_epoch': 1000, 'environment_sha256': 'b' * 64})
            self.assertTrue(result['complete']); self.assertTrue(receipt['receipt_verified'])
            self.assertEqual((4, 4), (len(owner.calls), len(owner.owners)))
            self.assertTrue(all(call.args[0].suffix in ('.bin', '.json') for call in api.open.call_args_list))
            self.assertEqual(72, api.record.call_count)

    def test_parser_consumes_verified_bytes_without_reopening_paths(self):
        result = analyze_capture('missing-stdout', 'missing-stderr', 0, 'icd10_lookup',
                                 capture_bytes=(b'', b'Ran 3 tests in 0.1s\r\n\r\nOK\r\n'))
        self.assertEqual(('nonreader', 3, False),
                         (result['classification'], result['test_count'], result['unexpected']))


class PopulationAndFailureControls(unittest.TestCase):
    def test_source_population_does_not_use_the_generated_windows_path_kind_policy(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / 'icd10_lookup.py').write_bytes(b'')
            (root / 'test_reader.py').write_bytes(b'import icd10_lookup\n')
            with patch.object(subject.contract, 'windows_metadata_api', return_value=object()):
                hashes = {path.name: subject.q.digest(path.read_bytes()) for path in root.glob('*.py')}
                population = subject.source_population(synthetic_check(), root, time.monotonic() + 10, hashes)
            self.assertEqual(('test_reader',), population['modules'])

    def test_source_identity_and_path_kind_refuse_before_population_admission(self):
        import measure_reader_attribution as subject
        import os
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); raw = b'import icd10_lookup\n'
            (root / 'test_reader.py').write_bytes(raw)
            expected = {'test_reader.py': subject.q.digest(raw)}
            for relative in ('../test_reader.py', '/test_reader.py', 'test_reader.bin', 'test_reader.json'):
                with self.subTest(relative=relative), self.assertRaises(subject.q.Refused):
                    subject.read_pinned_source(root, relative, expected['test_reader.py'], time.monotonic() + 10)
            with self.assertRaises(subject.q.Refused):
                subject.read_pinned_source(root, 'test_reader.py', 'a' * 64, time.monotonic() + 10)
            with self.assertRaises(subject.q.Refused):
                subject.read_pinned_source(root, 'test_reader.py', expected['test_reader.py'], time.monotonic() - 1)
            (root / 'test_extra.py').write_bytes(raw)
            with self.assertRaises(subject.q.Refused):
                subject.source_population(synthetic_check(), root, time.monotonic() + 10, expected)
            (root / 'test_extra.py').unlink()
            os.link(root / 'test_reader.py', root / 'linked.py')
            with self.assertRaises(subject.q.Refused):
                subject.read_pinned_source(root, 'test_reader.py', expected['test_reader.py'], time.monotonic() + 10)

    def test_owned_capture_path_and_owner_identity_cannot_be_substituted(self):
        import measure_reader_attribution as subject
        for change in ('wrong_path', 'wrong_owner', 'unretired_owner'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
                original = owner.run
                def run(argv, cwd):
                    result = original(argv, cwd)
                    if change == 'wrong_path': result['stdout_path'] = result['stderr_path']
                    elif change == 'wrong_owner': owner.owners[-1].result.stdout_path = result['stderr_path']
                    else: owner.owners[-1].result.snapshot.cleanup_verified = False
                    return result
                owner.run = run
                adapter = subject.ReaderAdapter(check, root / 'repository',
                    {'planted': {'modules': ('test_one',), 'pinned': frozenset()}}, owner, 'synthetic payload')
                adapter.original_readers = check._readers_under_refusal; check.subprocess = adapter
                with self.assertRaises(subject.q.Refused): adapter.readers(root / 'planted', frozenset(('test_one',)))
                self.assertEqual('incomplete', adapter.rows[0]['completion'])

    def test_interrupted_owner_keeps_known_root_status_without_completing_row(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
            def interrupted(argv, cwd):
                snapshot = types.SimpleNamespace(root_exit_code=23, cleanup_verified=False,
                                                  wall_seconds=0.2, tree_cpu_seconds=0.1)
                owner.owners.append(types.SimpleNamespace(result=types.SimpleNamespace(snapshot=snapshot)))
                raise OSError('PRIVATE partial start')
            owner.run = interrupted
            adapter = subject.ReaderAdapter(check, root / 'repository',
                {'planted': {'modules': ('test_one',), 'pinned': frozenset()}}, owner, 'synthetic payload')
            adapter.original_readers = check._readers_under_refusal; check.subprocess = adapter
            with self.assertRaises(OSError): adapter.readers(root / 'planted', frozenset(('test_one',)))
            self.assertEqual((23, 'incomplete', False), (adapter.rows[0]['returncode'],
                adapter.rows[0]['completion'], adapter.rows[0]['cleanup_verified']))

    def test_exact_proxy_contract_rejects_truthy_nonbooleans_before_launch(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
            adapter = subject.ReaderAdapter(check, root / 'repository',
                {'planted': {'modules': ('test_one',), 'pinned': frozenset()}}, owner, 'synthetic payload')
            def bad_loop(tools, reaching):
                return adapter.run([sys.executable, '-c', 'synthetic payload', str(tools), 'test_one', 'icd10_lookup'],
                                   cwd=tools, text=1, encoding='utf-8', errors='replace', capture_output=True, check=False)
            adapter.original_readers = bad_loop
            with self.assertRaisesRegex(subject.q.Refused, 'audit_command_changed'):
                adapter.readers(root / 'planted', frozenset(('test_one',)))
            self.assertEqual([], owner.calls)

    def test_missing_extra_out_of_order_and_same_count_replacements_do_not_launch(self):
        import measure_reader_attribution as subject
        for pairs in ((), (('test_other', 'icd10_lookup'),), (('test_one', 'procedure_codes_lookup'),),
                      (('test_one', 'icd10_lookup'), ('test_one', 'icd10_lookup'))):
            with self.subTest(pairs=pairs), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
                adapter = subject.ReaderAdapter(check, root / 'repository',
                    {'planted': {'modules': ('test_one',), 'pinned': frozenset()}}, owner, 'synthetic payload')
                def wrong_loop(tools, reaching):
                    for module, lookup in pairs:
                        adapter.run([sys.executable, '-c', 'synthetic payload', str(tools), module, lookup],
                                    cwd=tools, text=True, encoding='utf-8', errors='replace', capture_output=True, check=False)
                    return frozenset()
                adapter.original_readers = wrong_loop
                with self.assertRaises(subject.q.Refused):
                    adapter.readers(root / 'planted', frozenset(('test_one',)))
                self.assertLessEqual(len(owner.calls), 1)

    def test_marker_precedence_is_kept_but_contamination_cannot_be_clean(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); check = synthetic_check()
            owner = SyntheticOwner(root, [(1, b'CODE_SET_DATABASE_OPEN_REFUSED', b'PRIVATE OTHER FAILURE')])
            adapter = subject.ReaderAdapter(check, root / 'repository',
                {'planted': {'modules': ('test_one',), 'pinned': frozenset()}}, owner, 'synthetic payload')
            adapter.original_readers = check._readers_under_refusal; check.subprocess = adapter
            with self.assertRaisesRegex(subject.q.Refused, 'audit_capture_contaminated_or_unread'):
                adapter.readers(root / 'planted', frozenset(('test_one',)))
            self.assertEqual(('reader', False, 1),
                             (adapter.rows[0]['classification'], adapter.rows[0]['screen_clean'], len(owner.calls)))
            self.assertNotIn('PRIVATE', json.dumps(adapter.rows))

    def test_capture_launch_cleanup_and_publication_faults_remain_incomplete_or_held(self):
        import measure_reader_attribution as subject
        for fault in ('launch', 'capture', 'cleanup', 'publication'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
                original = owner.run
                def run(argv, cwd):
                    if fault == 'launch': raise OSError('PRIVATE launch')
                    result = original(argv, cwd)
                    if fault == 'capture': Path(result['stdout_path']).unlink()
                    if fault == 'cleanup': result['cleanup_verified'] = False
                    return result
                owner.run = run
                def publish(row):
                    if fault == 'publication': raise OSError('PRIVATE publication')
                adapter = subject.ReaderAdapter(check, root / 'repository',
                    {'planted': {'modules': ('test_one',), 'pinned': frozenset()}}, owner, 'synthetic payload', publish)
                adapter.original_readers = check._readers_under_refusal; check.subprocess = adapter
                with self.assertRaises((OSError, subject.q.Refused)):
                    adapter.readers(root / 'planted', frozenset(('test_one',)))
                self.assertIsNotNone(adapter.failure)
                self.assertEqual(1, len(adapter.rows))
                if fault != 'publication': self.assertEqual('incomplete', adapter.rows[0]['completion'])
                self.assertNotIn('PRIVATE', json.dumps(adapter.rows))

    def test_complete_source_population_includes_test_prefix_and_nonreaching_pins(self):
        import measure_reader_attribution as subject
        sources = {'icd10_lookup.py': b'', 'procedure_codes_lookup.py': b'',
                   'testnew.py': b'import icd10_lookup\n',
                   'helper.py': b'import procedure_codes_lookup\n',
                   'test_second.py': b'import helper\n',
                   'test_stale.py': b'"icd10_lookup"\n'}
        result = subject.population_from_sources(synthetic_check(), sources)
        self.assertEqual(('test_second', 'testnew'), result['modules'])
        self.assertEqual(frozenset((('test_stale', 'icd10_lookup'),)), result['pinned'])
        self.assertEqual(6, result['source_file_count'])
        sources['test_second.py'] = b'pass\n'
        self.assertEqual(('testnew',), subject.population_from_sources(synthetic_check(), sources)['modules'])

    def test_original_first_unmarked_nonzero_stops_without_a_retry(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            check = synthetic_check()
            owner = SyntheticOwner(root, [(7, b'PRIVATE_FAILURE', b'')])
            adapter = subject.ReaderAdapter(check, root / 'repository',
                {'planted': {'modules': ('test_one', 'test_two'), 'pinned': frozenset()}}, owner, 'synthetic payload')
            adapter.original_readers = check._readers_under_refusal
            check.subprocess = adapter
            with self.assertRaisesRegex(RuntimeError, 'PRIVATE original error'):
                adapter.readers(root / 'planted', frozenset(('test_one', 'test_two')))
            self.assertEqual((1, 'error', 7),
                             (len(owner.calls), adapter.rows[0]['classification'], adapter.rows[0]['returncode']))

    def test_runtime_source_change_with_same_count_refuses_before_launch(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            tools = root / 'planted'; tools.mkdir()
            sources = {'icd10_lookup.py': b'', 'test_one.py': b'import icd10_lookup\n'}
            for name, raw in sources.items(): (tools / name).write_bytes(raw)
            check = synthetic_check(); owner = SyntheticOwner(root)
            manifest = subject.population_from_sources(check, sources)
            (tools / 'test_one.py').write_bytes(b'import icd10_lookup\n"icd10_lookup"\n')
            adapter = subject.ReaderAdapter(check, root / 'repository', {'planted': manifest}, owner, 'synthetic payload')
            adapter.original_readers = check._readers_under_refusal; check.subprocess = adapter
            with self.assertRaisesRegex(subject.q.Refused, 'reviewed_raw_bytes_changed'):
                adapter.readers(tools, frozenset(('test_one',)))
            self.assertEqual([], owner.calls)

    def test_unread_metrics_cannot_complete_attribution(self):
        import measure_reader_attribution as subject
        for key, value in (('tree_cpu_seconds', None), ('tree_cpu_seconds', float('nan')),
                           ('wall_seconds', -1), ('tree_cpu_seconds', True)):
            with self.subTest(key=key, value=value), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
                original = owner.run
                owner.run = lambda argv, cwd: original(argv, cwd) | {key: value}
                adapter = subject.ReaderAdapter(check, root / 'repository',
                    {'planted': {'modules': ('test_one',), 'pinned': frozenset()}}, owner, 'synthetic payload')
                adapter.original_readers = check._readers_under_refusal; check.subprocess = adapter
                with self.assertRaisesRegex(subject.q.Refused, 'audit_metrics_unread'):
                    adapter.readers(root / 'planted', frozenset(('test_one',)))
                self.assertEqual(('incomplete', None), (adapter.rows[0]['completion'],
                                 adapter.rows[0]['tree_cpu_seconds' if key == 'tree_cpu_seconds' else 'owned_wall_seconds']))

    def test_public_pair_schema_rejects_raw_text_unknown_tokens_and_duplicate_keys(self):
        import measure_reader_attribution as subject
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); check = synthetic_check(); owner = SyntheticOwner(root)
            manifests = {'planted': {'modules': ('test_one',), 'pinned': frozenset()}}
            adapter = subject.ReaderAdapter(check, root / 'repository', manifests, owner, 'synthetic payload')
            adapter.original_readers = check._readers_under_refusal; check.subprocess = adapter
            adapter.readers(root / 'planted', frozenset(('test_one',)))
            clean = subject.encode_pairs(adapter.rows, manifests)
            self.assertEqual(2, len(subject.read_pairs(clean, manifests)))
            self.assertNotIn(b'PRIVATE', clean)
            for change in ({'raw': 'PRIVATE'}, {'pair_token': 'a' * 64}, {'index': True},
                           {'tree_cpu_seconds': float('inf')}, {'stdout_bytes': 16777217},
                           {'classification': 'PRIVATE'}, {'test_count': True}):
                with self.subTest(change=change), self.assertRaises(subject.q.Refused):
                    subject.encode_pairs([adapter.rows[0] | change, adapter.rows[1]], manifests)
            with self.assertRaises(subject.q.Refused):
                subject.read_pairs(b'[{"scope":"planted","scope":"repository"}]', manifests)
            with self.assertRaises(subject.q.Refused):
                subject.encode_pairs([adapter.rows[0], adapter.rows[0]], manifests)


class BudgetRouteControls(unittest.TestCase):
    def test_terminal_publication_cannot_outlive_the_whole_job_deadline(self):
        import contextlib
        import io
        import measure_reader_attribution as subject
        for crossing_event in ('reader_class_observation', 'reader_attribution_summary'):
            for terminal_time in (3600, 3601):
                with self.subTest(event=crossing_event, terminal_time=terminal_time), tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary); owner = root / 'owner'; owner.mkdir()
                    session = types.SimpleNamespace(cleanup=unittest.mock.Mock(return_value=True))
                    now, emissions, executions = [0], [], []
                    def execute(session, observer, seed, origin, progress, environment):
                        executions.append(True)
                        progress['class_summary'] = {'complete': True, 'top_children': [], 'module_totals': []}
                    def emit(event, **fields):
                        emissions.append((event, fields))
                        if event == crossing_event: now[0] = terminal_time
                    with contextlib.ExitStack() as stack:
                        for obj, name, replacement in ((subject, 'authorize_route', lambda *a: None),
                            (subject.q, 'environment_preflight', lambda: None),
                            (subject.q, 'corpus_preflight', lambda *a: None),
                            (subject.maintainer, 'environment_identity', lambda: {}),
                            (subject.maintainer, 'validate_environment', lambda *a: None),
                            (subject.tempfile, 'mkdtemp', lambda **kw: str(owner)),
                            (subject.time, 'monotonic', lambda: now[0]), (subject.time, 'time', lambda: 1000),
                            (subject, 'make_session', lambda *a: session),
                            (subject, 'execute', execute), (subject.q, 'emit', emit)):
                            stack.enter_context(patch.object(obj, name, replacement))
                        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                        error = stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                        result = subject.main(['--observer', str(root / 'observer'), '--seed', str(root / 'seed'),
                                               '--job-start-epoch', '1000'])
                    self.assertEqual(2, result)
                    session.cleanup.assert_called_once_with()
                    self.assertEqual([True], executions)
                    self.assertEqual('', error.getvalue())
                    self.assertEqual(1, sum(event == 'reader_attribution_summary' for event, fields in emissions))
                    final = emissions[-1][1]
                    if crossing_event == 'reader_class_observation':
                        self.assertEqual(('inconclusive', False, terminal_time),
                            (final['status'], final['hard_budget_verified'], final['observer_seconds']))

    def test_public_budget_is_shared_excludes_private_capture_and_reserves_terminal(self):
        import contextlib
        import io
        import measure_reader_attribution as subject
        output = io.StringIO(); public = subject.PublicOutput(output)
        with contextlib.redirect_stdout(public):
            subject.q.emit('reader_environment', label='fixed')
            for event in ('reader_source_map', 'reader_pair', 'reader_class_observation'):
                subject.q.emit(event, bounded='x' * 1200000)
            charged = public.bytes_written
            with contextlib.redirect_stdout(io.StringIO()): print('private' * 500000)
            self.assertEqual(charged, public.bytes_written)
            with self.assertRaisesRegex(subject.q.Refused, 'public_receipt_limit_exceeded'):
                subject.q.emit('reader_pair', bounded='x' * 1200000)
            public.terminal = True
            subject.q.emit('reader_attribution_summary', status='inconclusive')
        raw = output.getvalue().encode()
        self.assertLessEqual(len(raw), subject.BUDGET['max_receipt_bytes'])
        self.assertEqual(len(raw), public.bytes_written)
        self.assertEqual(5, len([json.loads(line) for line in raw.splitlines()]))
        self.assertEqual('inconclusive', json.loads(raw.splitlines()[-1])['status'])

    def test_failed_public_sink_is_not_retried_and_main_returns_nonzero(self):
        import io
        import measure_reader_attribution as subject
        sink = unittest.mock.Mock()
        sink.write.side_effect = OSError('PRIVATE_SINK_SENTINEL')
        with patch('sys.stdout', sink), patch('sys.stderr', new_callable=io.StringIO) as error:
            self.assertEqual(2, subject.main([]))
        self.assertEqual('', error.getvalue())
        self.assertEqual(1, sink.write.call_count)

    def test_terminal_publication_fault_preserves_cleanup_and_first_private_cause(self):
        import contextlib
        import io
        import measure_reader_attribution as subject
        for event in ('reader_class_observation', 'reader_attribution_summary'):
            for primary_failure in (False, True):
                with self.subTest(event=event, primary_failure=primary_failure), tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary); owner = root / 'owner'; owner.mkdir()
                    session = types.SimpleNamespace(cleanup=unittest.mock.Mock(return_value=True))
                    def execute(session, observer, seed, origin, progress, environment):
                        progress['class_summary'] = {'complete': True, 'top_children': [], 'module_totals': []}
                        if primary_failure: raise RuntimeError('PRIVATE_PRIMARY_SENTINEL')
                    def emit(name, **fields):
                        if name == event: raise OSError('PRIVATE_PUBLICATION_SENTINEL')
                    with contextlib.ExitStack() as stack:
                        for obj, name, replacement in ((subject, 'authorize_route', lambda *a: None),
                            (subject.q, 'environment_preflight', lambda: None),
                            (subject.q, 'corpus_preflight', lambda *a: None),
                            (subject.maintainer, 'environment_identity', lambda: {}),
                            (subject.maintainer, 'validate_environment', lambda *a: None),
                            (subject.tempfile, 'mkdtemp', lambda **kw: str(owner)),
                            (subject, 'make_session', lambda *a: session),
                            (subject, 'execute', execute), (subject.q, 'emit', emit)):
                            stack.enter_context(patch.object(obj, name, replacement))
                        output, error = io.StringIO(), io.StringIO()
                        stack.enter_context(contextlib.redirect_stdout(output))
                        stack.enter_context(contextlib.redirect_stderr(error))
                        result = subject.main(['--observer', str(root / 'observer'), '--seed', str(root / 'seed'),
                                               '--job-start-epoch', str(time.time())])
                    self.assertEqual(2, result)
                    session.cleanup.assert_called_once_with()
                    self.assertEqual('', output.getvalue() + error.getvalue())
                    private = (owner / 'private-observer-error.txt').read_text()
                    self.assertIn('PRIVATE_PRIMARY_SENTINEL' if primary_failure else 'PRIVATE_PUBLICATION_SENTINEL', private)
                    if primary_failure: self.assertNotIn('PRIVATE_PUBLICATION_SENTINEL', private)

    def test_terminal_publication_fault_cannot_escape_the_cli_with_private_traceback(self):
        root = Path(__file__).resolve().parent
        script = ('import runpy, sys; sys.path.insert(0, sys.argv[1]); '
                  'import measure_lazy_suite_ids as q; '
                  'q.emit = lambda *a, **k: (_ for _ in ()).throw(OSError("PRIVATE_CLI_SENTINEL")); '
                  'driver = sys.argv[2]; sys.argv = [driver]; runpy.run_path(driver, run_name="__main__")')
        result = subprocess.run([sys.executable, '-c', script, str(root), str(root / 'measure_reader_attribution.py')],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(2, result.returncode)
        self.assertEqual('', result.stdout + result.stderr)

    def test_private_error_retention_fault_also_remains_inside_failure_boundary(self):
        import io
        import measure_reader_attribution as subject
        with patch.object(subject, 'authorize_route', side_effect=OSError('PRIVATE_PRIMARY_SENTINEL')), \
             patch.object(subject.q, 'safe_exception', side_effect=OSError('PRIVATE_RETAIN_SENTINEL')), \
             patch('sys.stdout', new_callable=io.StringIO) as output, \
             patch('sys.stderr', new_callable=io.StringIO) as error:
            result = subject.main([])
        self.assertEqual(2, result)
        self.assertNotIn('PRIVATE', output.getvalue() + error.getvalue())
        self.assertEqual('inconclusive', json.loads(output.getvalue())['status'])

    def test_pre_suite_output_contract_uses_this_jobs_bound_without_suite_outputs(self):
        import measure_reader_attribution as subject
        state = subject.output_state(1000, 1100)
        self.assertEqual(('absent', 'absent', 'optional', 3600),
                         (state.marker, state.weights, state.sessions, state.max_job_seconds))
        subject.contract.validate_state(state)

    def test_unsupported_cli_cannot_create_an_owner_or_emit_private_error(self):
        import measure_reader_attribution as subject
        import io
        with patch.object(subject, 'make_session') as make, patch('sys.stdout', new_callable=io.StringIO) as output:
            result = subject.main([])
        self.assertEqual(2, result)
        make.assert_not_called()
        rows = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual('inconclusive', rows[-1]['status'])
        self.assertEqual(False, rows[-1]['process_cleanup_verified'])

    def test_setup_is_charged_and_cleanup_cannot_fund_class_admission(self):
        import measure_reader_attribution as subject
        self.assertEqual((3400, 3700), subject.budget_deadlines(1000, 1600, 700))
        self.assertIsNone(subject.admit_class(3400, 1000))
        for remaining in (2399.999, 0, -1, float('nan'), True):
            with self.subTest(remaining=remaining), self.assertRaises(subject.q.Refused):
                subject.admit_class(remaining, 0)
        for origin, now in ((None, 1000), (1001, 1000), (0, 4000), (True, 1000)):
            with self.subTest(origin=origin), self.assertRaises(subject.q.Refused):
                subject.budget_deadlines(origin, now, 500)

    def test_only_new_candidate_workflow_can_receive_the_branch_push(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / '.github/workflows/ci-reader-attribution.yml').read_text()
        self.assertEqual(1, text.count('timeout-minutes: 60'))
        self.assertEqual(['candidate'], __import__('re').findall(r'^  ([a-z]+):$', text.split('jobs:\n', 1)[1], __import__('re').M))
        self.assertLess(text.index('PROOF_JOB_START_EPOCH='), text.index('uses: actions/checkout'))
        for filename in ('ci-parallel-proof.yml', 'ci-checkpoint-discovery.yml'):
            other = (root / '.github/workflows' / filename).read_text()
            self.assertEqual("push:\n    branches-ignore: ['**']\n    tags-ignore: ['**']",
                             other.split('on:\n', 1)[1].split('\n\n', 1)[0].strip())
        for forbidden in ('workflow_dispatch', 'upload-artifact', 'strategy:', '--jobs', 'tools/suite.py', '--variant'):
            self.assertNotIn(forbidden, text)


if __name__ == '__main__':
    unittest.main()
