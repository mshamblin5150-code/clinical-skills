"""Synthetic disposable-workspace and independent failure receipts."""
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock
import measure_maintainer_pair as m
from test_full_suite_receipts import report

class WorkspaceBoundaries(unittest.TestCase):
    def setUp(self):
        parent=Path(m.__file__).resolve().parent.parent/'scratch/sessions'
        self.temporary=tempfile.TemporaryDirectory(prefix='workspace-control-',dir=parent)
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name);self.workspace=self.root/'w';self.workspace.mkdir()
        self.observer=self.workspace/'observer';self.seed=self.workspace/'source-seed'
        self.temp=self.root/'temporary-location';self.temp.mkdir()
        self.owner=self.temp/'maintainer-pair-owner-capture';self.owner.mkdir()
        self.observer.mkdir();self.seed.mkdir()
        (self.seed/'source').write_bytes(b'unchanged')
        self.env=mock.patch.dict(m.os.environ,{'GITHUB_WORKSPACE':str(self.workspace),'TEMP':str(self.temp),'TMP':str(self.temp)})
        self.env.start();self.addCleanup(self.env.stop)
        self.gettemp=mock.patch.object(m.tempfile,'gettempdir',return_value=str(self.temp))
        self.gettemp.start();self.addCleanup(self.gettemp.stop)
    def create(self,expected=None):
        return m.workspace_clone_root(self.owner,self.observer,self.seed,expected or {'tools/a.py':'hash'})
    def test_fresh_short_non_temp_sibling_preserves_environment_and_source(self):
        before=dict(os.environ)
        with mock.patch.object(m.q,'emit'):
            root=self.create()
        self.assertEqual(root.parent,self.workspace.parent)
        self.assertFalse(root.is_relative_to(self.temp))
        self.assertFalse(root.is_relative_to(self.workspace))
        self.assertEqual(list(root.iterdir()),[])
        self.assertEqual(dict(os.environ),before)
        self.assertEqual((self.seed/'source').read_bytes(),b'unchanged')
    def test_missing_mismatched_or_temp_workspace_refuses(self):
        for value in ('',str(self.seed),str(self.temp)):
            with mock.patch.dict(m.os.environ,{'GITHUB_WORKSPACE':value}):
                with self.assertRaises(m.q.Refused):self.create()
        with mock.patch.object(m.tempfile,'gettempdir',return_value=str(self.root)):
            with self.assertRaisesRegex(m.q.Refused,'inside_temp'):self.create()
    def test_nonfresh_overlap_outside_and_overlong_roots_refuse(self):
        nonempty=self.root/'lc-full';nonempty.mkdir();(nonempty/'keep').write_bytes(b'keep')
        outside=self.workspace/'lc-other';outside.mkdir()
        for root in (nonempty,outside,self.observer,self.seed,self.owner):
            with mock.patch.object(m.tempfile,'mkdtemp',return_value=str(root)):
                with self.assertRaises(m.q.Refused):self.create()
        with self.assertRaisesRegex(m.q.Refused,'too_long'):self.create({'x'*300:'hash'})
    def test_symlink_workspace_refuses(self):
        link=self.root/'alias';link.symlink_to(self.workspace,target_is_directory=True)
        with mock.patch.dict(m.os.environ,{'GITHUB_WORKSPACE':str(link)}):
            with self.assertRaises(m.q.Refused):self.create()
    def test_reparse_ancestor_refuses(self):
        from types import SimpleNamespace
        original=Path.lstat
        def metadata(path,*a,**kw):
            row=original(path,*a,**kw)
            return SimpleNamespace(st_mode=row.st_mode,st_file_attributes=0x400) if path==self.root else row
        with mock.patch.object(Path,'lstat',metadata):
            with self.assertRaises(m.q.Refused):self.create()

class EvidenceBoundaries(unittest.TestCase):
    def test_suite_failure_observed_without_raw_content(self):
        result={'returncode':1,'stdout':'private text\nre-run (from tools/): python -m unittest test_a.C.t\n'+report(count=2),'stderr':''}
        with mock.patch.object(m.q,'emit') as emit:
            row=m.observe_suite(result,{'test_count':2},{'cpu_count':4})
        self.assertTrue(row['accounting_valid']);self.assertEqual(row['returncode'],1)
        self.assertFalse(row['accounting']['successful'])
        self.assertNotIn('private',json.dumps(row))
        emit.assert_called_once_with('suite_native_observation',**row)
    def test_invalid_accounting_still_preserves_original_exit(self):
        with mock.patch.object(m.q,'emit'):
            row=m.observe_suite({'returncode':1,'stdout':'private text','stderr':''},{'test_count':2},{'cpu_count':4})
        self.assertFalse(row['accounting_valid']);self.assertEqual(row['returncode'],1)
        self.assertNotIn('private',json.dumps(row))
    def test_rejected_entry_receipt_precedes_original_refusal(self):
        with mock.patch.object(m.q,'emit') as emit:
            with self.assertRaisesRegex(m.q.Refused,'unexpected_retained_directory'):
                m.rejected_entry('unexpected_retained_directory','private-name','directory')
        row=emit.call_args.kwargs
        self.assertEqual(row['entry_kind'],'directory')
        self.assertNotIn('private-name',json.dumps(row))
        self.assertEqual(len(row['path_token']),64)
    def test_precommand_identity_is_bounded_and_survives_later_refusal(self):
        import inspect
        progress={};environment={'python':'3.14.4'}
        discovery={'test_count':2,'sorted_ids_sha256':'a'*64,'loader_error_count':0,
                   'module_test_count':1,'executed_test_count':0,
                   'ids_encoding':'sorted JSON array, ASCII escaped, compact'}
        controls=sorted(m.q.CONTROL_IDS)
        with mock.patch.object(m.q,'emit') as emit:
            m.preserve_identity(progress,environment,discovery,controls)
        self.assertEqual(progress,{'environment':environment,'discovery':discovery,'behavior_control_ids':controls})
        emit.assert_called_once_with('maintainer_precommand_identity',**progress)
        source=inspect.getsource(m.execute)
        self.assertLess(source.index('preserve_identity('),source.index('for name, argv in COMMANDS'))
        for bad in (discovery|{'test_count':False},discovery|{'sorted_ids_sha256':'private'},discovery|{'extra':'private'}):
            with self.assertRaises(m.q.Refused):m.preserve_identity({},environment,bad,controls)

    def test_original_suite_exit_and_later_guard_failure_survive_summary(self):
        from types import SimpleNamespace
        from test_current_pair import passing_receipt
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);observer=root/'observer';seed=root/'seed';observer.mkdir();seed.mkdir()
            env={'GITHUB_ACTIONS':'true','GITHUB_EVENT_NAME':'push','GITHUB_REF':m.q.BRANCH,'GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':'a'*40,'GITHUB_RUN_ID':'12345'}
            session=mock.Mock();session.cleanup.side_effect=RuntimeError('private cleanup detail');emitted=[]
            def failed_execute(session, observer, seed, variant, identity, prior, progress, job_start_epoch):
                m.preserve_identity(progress, {'python':'3.14.4'},
                    {'test_count':2,'sorted_ids_sha256':'a'*64,'loader_error_count':0,
                     'module_test_count':1,'executed_test_count':0,'ids_encoding':'sorted JSON array, ASCII escaped, compact'},
                    sorted(m.q.CONTROL_IDS))
                progress['suite_observation']={'returncode':1,'accounting_valid':True}
                progress['active_phase']='pair_guard_suite'
                raise m.q.Refused('generated_output_unexpected')
            with mock.patch.object(m,'os',SimpleNamespace(name='nt',environ=env)), \
                 mock.patch.object(m.platform,'python_version',return_value='3.14.4'), \
                 mock.patch.object(m,'environment_identity',return_value=passing_receipt()['environment']), \
                 mock.patch.object(m.q,'environment_preflight'),mock.patch.object(m.q,'corpus_preflight'), \
                 mock.patch.object(m,'make_session',return_value=session),mock.patch.object(m.q,'safe_exception',side_effect=PermissionError('private evidence detail')), \
                 mock.patch.object(m,'execute',side_effect=failed_execute), \
                 mock.patch.object(m.q,'emit',side_effect=lambda event,**kw:emitted.append((event,kw))), \
                 mock.patch.object(m.tempfile,'mkdtemp',return_value=str(root/'capture')):
                rc=m.main(['--observer',str(observer),'--seed',str(seed),'--variant','baseline','--job-start-epoch',str(time.time())])
            self.assertEqual(rc,2)
            row=[row for event,row in emitted if event=='maintainer_arm_summary'][0]
            self.assertEqual(row['suite_observation']['returncode'],1)
            self.assertEqual(row['environment'],{'python':'3.14.4'})
            self.assertEqual(row['discovery']['test_count'],2)
            self.assertEqual(row['behavior_control_ids'],sorted(m.q.CONTROL_IDS))
            self.assertEqual(row['failure'],'generated_output_unexpected')
            self.assertEqual(row['failure_phase'],'pair_guard_suite')
            self.assertFalse(row['process_cleanup_verified'])
            self.assertNotIn('private cleanup detail',json.dumps(emitted))
            self.assertNotIn('private evidence detail',json.dumps(emitted))
            self.assertFalse(row['safe_to_continue'])
            self.assertFalse(row['all_commands_passed'])

    def test_unchanged_hook_location_refusal_is_not_overridden(self):
        session=mock.Mock();session.run.return_value={'returncode':0,'stdout':'{"checkout_named_temp":true}'}
        with self.assertRaisesRegex(m.q.Refused,'source_hook_refuses'):m.verify_hook_location(session,Path('repo'))

if __name__=='__main__':unittest.main()
