import dataclasses
from datetime import date, datetime, timedelta
import inspect
import json
import math
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import generated_output_contract as g


class GeneratedOutputControls(unittest.TestCase):
    def setUp(self):
        self.holder = tempfile.TemporaryDirectory(prefix='generated-contract-')
        self.addCleanup(self.holder.cleanup)
        self.repo = Path(self.holder.name).resolve()
        patcher = mock.patch.object(g.q, 'emit')
        self.emit = patcher.start()
        self.addCleanup(patcher.stop)
        self.now = time.time()
        self.state = g.State(job_start_epoch=self.now, observed_epoch=self.now)
        self.target = {'tools/example.py': 'not-used-source-already-verified'}
        (self.repo/'tools').mkdir()
        (self.repo/'tools/example.py').write_bytes(b'pass\n')
        self.deadline = time.monotonic() + 30

    def put(self, relative, raw):
        path=self.repo/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        return path

    def marker(self, raw=None):
        row={'version':2,'ran_on':date.fromtimestamp(self.now).isoformat()}
        if raw is None:raw=(json.dumps(row,sort_keys=True)+'\n').replace('\n',os.linesep).encode()
        return self.put(g.marker_relative(self.repo),raw)

    def weights(self, row=None):
        row={'test_tiny.Tiny':0.25} if row is None else row
        return self.put(g.WEIGHTS,(json.dumps(dict(sorted(row.items())),indent=2)+'\n').replace('\n',os.linesep).encode())

    def scan(self, **changes):
        return g.scan(self.repo,self.target,self.deadline,dataclasses.replace(self.state,**changes))

    def refused(self, **changes):
        with self.assertRaises(g.q.Refused):self.scan(**changes)

    def test_pristine_and_source_bound_bytecode_pass(self):
        self.assertTrue(self.scan()['contract_verified'])
        self.put('tools/__pycache__/example.cpython-314.pyc',b'bounded opaque code')
        self.assertEqual(self.scan()['generated_counts']['bytecode'],1)

    def test_exact_marker_native_bytes_required_and_identity_pass(self):
        self.marker()
        self.assertEqual(self.scan(marker='required')['generated_counts']['marker'],1)
        self.refused()

    def test_marker_missing_required_and_wrong_checkout_identity_refuse(self):
        self.refused(marker='required')
        self.put(g.MARKER_DIR+'/'+'0'*64+'.json',b'{}')
        self.refused(marker='required')

    def test_marker_extra_file_and_nested_directory_refuse(self):
        self.marker();extra=self.put(g.MARKER_DIR+'/extra',b'')
        self.refused(marker='required');extra.unlink()
        (self.repo/g.MARKER_DIR/'nested').mkdir();self.refused(marker='required')

    def test_marker_duplicate_unknown_missing_keys_and_bad_version_refuse(self):
        today=date.fromtimestamp(self.now).isoformat()
        raws=[f'{{"ran_on":"{today}","version":2,"version":2}}'.encode()]
        for row in ({'version':2},{'version':2,'ran_on':today,'extra':0},
                    {'version':True,'ran_on':today},{'version':1,'ran_on':today}):
            raws.append(json.dumps(row).encode())
        for raw in raws:
            self.marker(raw);self.refused(marker='required')

    def test_marker_stale_future_invalid_dates_and_wrong_native_bytes_refuse(self):
        for value in ('not-a-date','20261021',date.fromtimestamp(self.now-86400).isoformat(),date.fromtimestamp(self.now+86400).isoformat()):
            self.marker((json.dumps({'version':2,'ran_on':value},sort_keys=True)+'\n').replace('\n',os.linesep).encode())
            self.refused(marker='required')
        self.marker(b' ' * 129);self.refused(marker='required')
        expected=(json.dumps({'version':2,'ran_on':date.fromtimestamp(self.now).isoformat()},sort_keys=True)+'\n')
        opposite='\n' if os.linesep=='\r\n' else '\r\n'
        self.marker(expected.replace('\n',opposite).encode());self.refused(marker='required')
        self.marker(expected.rstrip().encode());self.refused(marker='required')

    def test_bounded_midnight_span_accepts_both_observed_dates(self):
        start=datetime.combine(date.today(),datetime.min.time()).timestamp()-30
        state=g.State(marker='required',job_start_epoch=start,observed_epoch=start+60)
        for value in (date.fromtimestamp(start),date.fromtimestamp(start+60)):
            raw=(json.dumps({'version':2,'ran_on':value.isoformat()},sort_keys=True)+'\n').replace('\n',os.linesep).encode()
            g.validate_marker(raw,state,'synthetic')

    def test_reversed_nonfinite_and_broad_date_spans_refuse(self):
        for changes in ({'observed_epoch':self.now-1},{'observed_epoch':self.now+601},
                        {'job_start_epoch':float('nan')},{'job_start_epoch':True},
                        {'max_job_seconds':True},{'units':(['bad'],)}):
            self.refused(**changes)

    def test_weights_exact_native_content_and_population_pass(self):
        self.weights()
        self.assertEqual(self.scan(weights='required',units=('test_tiny.Tiny',))['generated_counts']['weights'],1)
        self.refused()

    def test_weights_missing_wrong_unknown_duplicate_units_refuse(self):
        self.refused(weights='required',units=('test_tiny.Tiny',))
        for row in ({},{'test_other.Other':0.1},{'test_tiny.Tiny':0.1,'test_other.Other':0.2}):
            self.weights(row);self.refused(weights='required',units=('test_tiny.Tiny',))
        self.put(g.WEIGHTS,b'{"test_tiny.Tiny":0.1,"test_tiny.Tiny":0.2}')
        self.refused(weights='required',units=('test_tiny.Tiny',))
        self.refused(weights='required',units=('test_tiny.Tiny','test_tiny.Tiny'))

    def test_weights_boolean_negative_nonfinite_and_excessive_values_refuse(self):
        for value in (True,-1,float('nan'),float('inf'),601):
            self.weights({'test_tiny.Tiny':value});self.refused(weights='required',units=('test_tiny.Tiny',))

    def test_weights_wrong_bytes_and_temporary_leftover_refuse(self):
        self.put(g.WEIGHTS,b'{"test_tiny.Tiny":0.25}')
        self.refused(weights='required',units=('test_tiny.Tiny',))
        self.weights();self.put('scratch/runs/suite-weights-abcd.tmp',b'')
        self.refused(weights='required',units=('test_tiny.Tiny',))

    def test_sessions_empty_required_pass_and_missing_content_nested_refuse(self):
        self.refused(sessions='required')
        (self.repo/'scratch/sessions').mkdir(parents=True)
        self.assertTrue(self.scan(sessions='required')['contract_verified'])
        item=self.put('scratch/sessions/content',b'');self.refused();item.unlink()
        (self.repo/'scratch/sessions/nested').mkdir();self.refused()

    def test_unknown_bytecode_source_extension_and_directory_refuse(self):
        for relative in ('tools/__pycache__/unknown.cpython-314.pyc','tools/__pycache__/example.pyo','output/private'):
            path=self.put(relative,b'');self.refused();path.unlink()
            # Unknown directories themselves remain rejected: remove the owned leaf tree.
            if relative.startswith('output'):path.parent.rmdir()

    def test_empty_cache_directory_without_pinned_python_parent_refuses(self):
        (self.repo/'scratch/__pycache__').mkdir(parents=True)
        self.refused()

    def test_oversize_generated_file_refuses(self):
        path=self.put('tools/__pycache__/example.cpython-314.pyc',b'')
        with path.open('wb') as stream:stream.truncate(g.MAX_FILE_BYTES+1)
        self.refused()

    def test_native_hardlink_refuses(self):
        source=self.put('tools/__pycache__/example.cpython-314.pyc',b'x')
        with tempfile.TemporaryDirectory(prefix='hardlink-control-') as outside:
            os.link(source,Path(outside)/'owned-hardlink')
            with self.assertRaisesRegex(g.q.Refused,'generated_file_unsafe'):
                self.scan()

    def test_marker_hardlink_and_weights_oversize_refuse(self):
        source=self.marker()
        with tempfile.TemporaryDirectory(prefix='marker-link-control-') as outside:
            os.link(source,Path(outside)/'owned-hardlink')
            with self.assertRaisesRegex(g.q.Refused,'generated_file_unsafe'):
                self.scan(marker='required')
        source.unlink();source.parent.rmdir()
        path=self.weights()
        with path.open('wb') as stream:stream.truncate(g.MAX_FILE_BYTES+1)
        with self.assertRaisesRegex(g.q.Refused,'generated_file_oversize'):
            self.scan(weights='required',units=('test_tiny.Tiny',))

    def test_safe_read_rejects_outside_relative_paths(self):
        for relative in ('../outside','/outside','tools/../outside','tools\\outside','C:outside'):
            with self.assertRaises(g.q.Refused):g.safe_read(self.repo,relative,128,self.deadline)

    def test_direct_safe_read_rejects_relative_noncanonical_and_unsafe_roots(self):
        self.marker()
        relative=g.marker_relative(self.repo)
        for root in (Path('.'),self.repo/'tools'/'..'):
            with self.assertRaises(g.q.Refused):g.safe_read(root,relative,128,self.deadline)
        with mock.patch.object(g,'_safe_directory',side_effect=g.q.Refused('generated_directory_unsafe')):
            with self.assertRaises(g.q.Refused):g.safe_read(self.repo,relative,128,self.deadline)
        with mock.patch.object(g,'_safe_directory',wraps=g._safe_directory) as checked:
            g.safe_read(self.repo,relative,128,self.deadline)
            paths=[call.args[0] for call in checked.call_args_list]
            for ancestor in (self.repo,*self.repo.parents):self.assertIn(ancestor,paths)

    def test_weights_unit_population_comes_from_actual_class_object(self):
        tiny_class=type('Tiny',(unittest.TestCase,),{'__module__':'synthetic_units'})
        tiny=tiny_class()
        units=(tiny.__class__.__module__+'.'+tiny.__class__.__qualname__,)
        self.weights({units[0]:0.25})
        self.assertTrue(self.scan(weights='required',units=units)['contract_verified'])

    def test_git_file_is_not_a_permitted_generated_output(self):
        self.put('.git',b'gitdir: unrelated')
        self.refused()

    def test_native_owned_directory_link_refuses_and_target_survives(self):
        from staging_retained_controls import make_link, unlink_native
        with tempfile.TemporaryDirectory(prefix='generated-link-target-') as name:
            target=Path(name).resolve();(target/'sentinel').write_bytes(b'synthetic')
            link=self.repo/'scratch/sessions';link.parent.mkdir()
            kind='junction' if os.name=='nt' else 'symlink'
            try:
                self.assertEqual(make_link(link,target),kind)
                self.refused()
            finally:
                if os.path.lexists(link):unlink_native(link,kind)
            self.assertEqual((target/'sentinel').read_bytes(),b'synthetic')

    def test_handle_metadata_change_after_read_refuses(self):
        from types import SimpleNamespace
        self.marker();calls=0
        if os.name == 'nt':
            original = g.WindowsMetadataAPI.record
            def changed(api, handle):
                nonlocal calls
                calls += 1
                sample = original(api, handle)
                return dataclasses.replace(sample, st_mtime_ns=sample.st_mtime_ns+100) if calls == 5 else sample
            with mock.patch.object(g.WindowsMetadataAPI, 'record', changed):
                self.refused(marker='required')
        else:
            original = os.fstat
            def changed(fd):
                nonlocal calls
                calls += 1
                sample = original(fd)
                if calls == 2:
                    fields = {name: getattr(sample, name) for name in dir(sample) if name.startswith('st_')}
                    fields['st_mtime_ns'] += 1
                    return SimpleNamespace(**fields)
                return sample
            with mock.patch.object(os, 'fstat', side_effect=changed):
                self.refused(marker='required')

    def test_injected_reparse_and_link_metadata_refuse(self):
        import stat
        from types import SimpleNamespace
        sample=os.stat(self.repo/'tools/example.py')
        fields={name:getattr(sample,name) for name in dir(sample) if name.startswith('st_')}
        fields.update(st_file_attributes=0x400)
        with self.assertRaises(g.q.Refused):g._regular(SimpleNamespace(**fields),128,'synthetic')
        fields.update(st_file_attributes=0,st_mode=stat.S_IFLNK|0o777)
        with self.assertRaises(g.q.Refused):g._regular(SimpleNamespace(**fields),128,'synthetic')

    def test_non_directory_ancestor_refuses(self):
        self.put('scratch',b'not-directory')
        self.refused()

    def test_unread_directory_and_file_refuse(self):
        self.marker()
        actual=os.scandir
        def denied(path):
            if Path(path)==self.repo/g.MARKER_DIR:raise PermissionError('private')
            return actual(path)
        with mock.patch.object(os,'scandir',side_effect=denied):self.refused(marker='required')
        with mock.patch.object(g,'_open_readonly',side_effect=PermissionError('private')):self.refused(marker='required')

    def test_stat_open_identity_change_refuses(self):
        self.marker();actual=g._open_readonly
        def replaced(path):
            raw=path.read_bytes();path.unlink();path.write_bytes(raw+b' ')
            return actual(path)
        with mock.patch.object(g,'_open_readonly',side_effect=replaced):self.refused(marker='required')

    def test_deadline_exhaustion_and_entry_limit_refuse(self):
        self.deadline=time.monotonic()-1;self.refused()
        self.deadline=time.monotonic()+30
        with mock.patch.object(g,'MAX_ENTRIES',0):self.refused()

    def test_refusal_receipt_contains_no_raw_path_or_contents(self):
        self.put('PRIVATE_PATH',b'PRIVATE_CONTENT');self.refused()
        serialized=json.dumps(self.emit.call_args.kwargs)
        self.assertNotIn('PRIVATE_PATH',serialized);self.assertNotIn('PRIVATE_CONTENT',serialized)

    def test_all_safe_unknown_entries_collected_without_reading_payloads(self):
        first=self.put('unknown_one/a.txt',b'PRIVATE_ONE')
        second=self.put('unknown_two/nested/b.txt',b'PRIVATE_TWO')
        with mock.patch.object(g,'safe_read',side_effect=AssertionError('unknown payload read')):
            self.refused()
        summaries=[call.kwargs for call in self.emit.call_args_list if call.args[0]=='generated_output_discrepancies']
        self.assertEqual(len(summaries),1)
        row=summaries[0]
        self.assertTrue(row['collection_complete'])
        expected={'unknown_one','unknown_one/a.txt','unknown_two','unknown_two/nested','unknown_two/nested/b.txt'}
        self.assertEqual({entry['path_token'] for entry in row['entries']},{g.q.digest(name.encode()) for name in expected})
        self.assertEqual(row['count'],5)
        self.assertNotIn('PRIVATE',json.dumps(row))
        self.assertNotIn('unknown_one',json.dumps(row))

    def test_unknown_metadata_change_stops_collection_as_incomplete(self):
        from types import SimpleNamespace
        unknown=self.put('unknown.txt',b'PRIVATE')
        original=Path.lstat;seen=0
        def unstable(path,*a,**kw):
            nonlocal seen
            result=original(path,*a,**kw)
            if path==unknown:
                seen+=1
                if seen>=2:
                    fields={name:getattr(result,name) for name in dir(result) if name.startswith('st_')}
                    fields['st_ino']+=1
                    return SimpleNamespace(**fields)
            return result
        with mock.patch.object(Path,'lstat',unstable):self.refused()
        row=[call.kwargs for call in self.emit.call_args_list if call.args[0]=='generated_output_discrepancies'][0]
        self.assertFalse(row['collection_complete'])

    def test_unsafe_later_entry_refuses_immediately_with_partial_collection(self):
        self.put('ordinary',b'PRIVATE')
        original=self.put('unsafe',b'PRIVATE');os.link(original,self.repo/'second-link')
        rows=[(str(self.repo),[],['ordinary','unsafe','not-inspected'])]
        with mock.patch.object(os,'walk',return_value=iter(rows)):
            self.refused()
        row=[call.kwargs for call in self.emit.call_args_list if call.args[0]=='generated_output_discrepancies'][0]
        self.assertFalse(row['collection_complete'])
        self.assertEqual(row['count'],1)
        self.assertEqual(row['entries'][0]['path_token'],g.q.digest(b'ordinary'))

    def test_unknown_discrepancy_limit_is_immediate_and_never_passes(self):
        self.put('one',b'PRIVATE');self.put('two',b'PRIVATE')
        with mock.patch.object(g,'MAX_DISCREPANCIES',1):self.refused()
        row=[call.kwargs for call in self.emit.call_args_list if call.args[0]=='generated_output_discrepancies'][0]
        self.assertFalse(row['collection_complete'])
        self.assertEqual(row['count'],1)

    def test_native_windows_open_uses_nonfollowing_handle_without_fallback(self):
        source=inspect.getsource(g._open_readonly)
        self.assertIn('0x00200000',source)
        self.assertIn('GetFileInformationByHandleEx',source)
        self.assertIn('msvcrt.open_osfhandle',source)
        self.assertIn('kernel.CloseHandle(handle)',source)


    def metadata_fixture(self, **changes):
        # CPython 23116f998f6789d8c2fbe5ed5b8146854c8c2a4f (v3.14.4):
        # Modules/posixmodule.c:2289-2299; Python/fileutils.c:1117-1123,1283-1285.
        # Windows path ctime is CreationTime; handle ctime
        # is ChangeTime. Synthetic values model semantics, not hosted evidence.
        from types import SimpleNamespace
        fields=dict(st_dev=1, st_ino=2, st_mode=0o100666, st_nlink=1,
                    st_size=3, st_mtime_ns=4, st_ctime_ns=5,
                    st_file_attributes=32, st_birthtime_ns=5)
        fields.update(changes)
        return SimpleNamespace(**fields)

    def test_windows_creation_change_time_model_remains_refused(self):
        path=self.metadata_fixture(); handle=self.metadata_fixture(st_ctime_ns=6)
        with self.assertRaisesRegex(g.q.Refused, 'generated_file_identity_changed'):
            g.compare_metadata('before_open', path, handle, 'fixed.pyc')
        row=self.emit.call_args_list[-2]
        self.assertEqual(row.args, ('generated_file_comparison',))
        self.assertEqual(row.kwargs['unequal_fields'], ['st_ctime_ns'])
        self.assertTrue(row.kwargs['left_ctime_equals_birthtime'])
        self.assertFalse(row.kwargs['right_ctime_equals_birthtime'])
        self.assertEqual(self.emit.call_args_list[-1].args, ('generated_output_rejected',))

    def test_comparison_preserves_every_original_identity_field(self):
        before=self.metadata_fixture()
        for field in g.METADATA_FIELDS:
            self.emit.reset_mock()
            after=self.metadata_fixture(**{field:getattr(before,field)+1})
            with self.assertRaises(g.q.Refused):
                g.compare_metadata('before_after', before, after, 'fixed.pyc')
            self.assertEqual(self.emit.call_args_list[-2].kwargs['unequal_fields'], [field])

    def test_equal_comparison_emits_nothing_and_absent_birthtime_is_finite(self):
        left=self.metadata_fixture(); del left.st_birthtime_ns
        g.compare_metadata('after_final',left,left,'fixed.pyc')
        self.emit.assert_not_called()
        right=self.metadata_fixture(st_ino=99); del right.st_birthtime_ns
        with self.assertRaises(g.q.Refused):g.compare_metadata('after_final',left,right,'fixed.pyc')
        row=self.emit.call_args_list[-2].kwargs
        self.assertEqual(row['left_ctime_equals_birthtime'], 'unavailable')
        self.assertEqual(row['right_ctime_equals_birthtime'], 'unavailable')
        self.assertNotIn('fixed.pyc', json.dumps(row))

    def test_length_refusal_emits_only_finite_comparison_before_refusal(self):
        with self.assertRaises(g.q.Refused):g.compare_read_length(2,3,'fixed.pyc')
        row=self.emit.call_args_list[-2]
        self.assertEqual(row.kwargs['stage'],'read_length')
        self.assertFalse(row.kwargs['length_equal'])
        self.assertNotIn('actual',row.kwargs)


    def test_observation_never_adds_filesystem_reads_or_rechecks(self):
        import ast
        source = inspect.getsource(g._safe_read)
        calls = [node.func.attr for node in ast.walk(ast.parse(source))
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
        self.assertEqual(calls.count('lstat'), 2)
        self.assertEqual(calls.count('fstat'), 2)
        self.assertEqual(calls.count('read'), 1)
        self.assertEqual(source.count('_open_readonly(path)'), 1)
        for helper in (g.compare_metadata, g.compare_read_length):
            calls = [node.func.attr for node in ast.walk(ast.parse(inspect.getsource(helper)))
                     if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
            self.assertTrue(set(calls).isdisjoint({'lstat', 'fstat', 'read', 'open', 'stat'}))

    def test_all_comparison_stages_emit_only_finite_flags_and_path_token(self):
        for stage in ('before_open', 'before_after', 'after_final'):
            self.emit.reset_mock()
            with self.assertRaisesRegex(g.q.Refused, 'generated_file_identity_changed'):
                g.compare_metadata(stage, self.metadata_fixture(), self.metadata_fixture(st_ino=987654321), 'private-name.pyc')
            row = self.emit.call_args_list[-2].kwargs
            self.assertEqual(set(row), {'stage', 'path_token', 'fields_equal', 'unequal_fields',
                                        'left_ctime_equals_birthtime', 'right_ctime_equals_birthtime'})
            self.assertEqual(set(row['fields_equal']), set(g.METADATA_FIELDS))
            self.assertTrue(all(type(value) is bool for value in row['fields_equal'].values()))
            self.assertNotIn('private-name', json.dumps(row))
            self.assertNotIn('987654321', json.dumps(row))


if __name__=='__main__':unittest.main()
