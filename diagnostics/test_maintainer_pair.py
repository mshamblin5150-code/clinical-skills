import inspect
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock
import measure_maintainer_pair as m

class PairControls(unittest.TestCase):
    def test_source_known_pair_refusals_keep_finite_categories(self):
        import ast
        import generated_output_contract as contract
        tree=ast.parse("\n".join(inspect.getsource(module) for module in (m,m.q,contract)))
        reasons=set()
        for node in ast.walk(tree):
            if not isinstance(node,ast.Call):
                continue
            name=node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id if isinstance(node.func,ast.Name) else ''
            index=1 if name in ('require','need') else 0 if name in ('Refused','refuse') else None
            if index is not None and len(node.args)>index:
                value=node.args[index]
                if isinstance(value,ast.Constant) and isinstance(value.value,str):
                    reasons.add(value.value)
        self.assertGreater(len(reasons),50)
        self.assertTrue({'measured_head_changed','measured_index_changed','git_verification_failed'} <= reasons)
        for reason in reasons:
            self.assertEqual(m.observation.reason_category(m.q.Refused(reason)),reason)
        self.assertEqual(m.observation.reason_category(m.q.Refused('private payload /unknown/path')),'unavailable')

    def test_exact_unfiltered_commands(self):
        self.assertEqual(m.COMMANDS, (
            ('phi_layers', ('tools/phi_scan.py', '--layers', '--all')),
            ('suite', ('tools/suite.py',)),
            ('publication_measurements', ('tools/tracker_measurements.py',)),
            ('threshold_sheet', ('tools/threshold_sheet.py', '--all')),
            ('phi_shape_only', ('tools/phi_scan.py', '--all', '--allow-no-corpus'))))

    def test_unsafe_or_wrong_source_baseline_refuses(self):
        good={'variant':'baseline','safe_to_continue':True,'source_sha':m.q.BASE,'all_commands_passed':True}
        self.assertEqual(m.baseline_receipt(json.dumps(good)),good)
        for delta in ({'variant':'candidate'},{'safe_to_continue':False},{'source_sha':'0'*40},{'all_commands_passed':False},{'all_commands_passed':None},{'all_commands_passed':1}):
            with self.assertRaises(m.q.Refused): m.baseline_receipt(json.dumps(good|delta))
        for raw in (None,'', ' '*16385):
            with self.assertRaises(m.q.Refused): m.baseline_receipt(raw)

    def test_environment_values_are_finite_and_pairable(self):
        env={'ImageOS':'win25','ImageVersion':'20261020.1','RUNNER_OS':'Windows','RUNNER_ARCH':'X64'}
        with mock.patch.dict(m.os.environ,env,clear=True),mock.patch.object(m.os,'cpu_count',return_value=4):
            self.assertEqual(m.environment_identity()['default_workers'],3)
        with mock.patch.dict(m.os.environ,env|{'ImageOS':'secret/path'},clear=True):
            with self.assertRaises(m.q.Refused): m.environment_identity()

    def test_full_ref_allowlist_and_history_required(self):
        session=mock.Mock()
        good=['false','refs/remotes/origin/main '+m.q.BASE+'\nrefs/remotes/origin/HEAD '+m.q.BASE,'refs/remotes/origin/main']
        session.git.side_effect=good
        m.verify_refs(session,Path('repo'))
        for values in (['true'],['false',good[1]+'\nrefs/heads/other '+m.q.BASE],['false',good[1],'refs/heads/main']):
            session.git.side_effect=values
            with self.assertRaises(m.q.Refused):m.verify_refs(session,Path('repo'))

    def test_retained_output_guard_rejects_unknown_ignored_fixture(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name); (root/'tools').mkdir(); (root/'tools/a.py').write_bytes(b'pass')
            target={'tools/a.py':m.q.digest(b'pass')}
            session=mock.Mock(deadline=time.monotonic()+30)
            with mock.patch.object(m.q,'verify_sources'),mock.patch.object(m,'verify_refs'):
                self.assertEqual(m.retained_guard(session,root,target,False)['allowed_retained_file_count'],0)
                (root/'tools/__pycache__').mkdir(); (root/'tools/__pycache__/a.cpython-314.pyc').write_bytes(b'cache')
                self.assertEqual(m.retained_guard(session,root,target,False)['allowed_retained_file_count'],1)
                (root/'scratch').mkdir(); (root/'scratch/leaked-fixture.txt').write_bytes(b'synthetic')
                with self.assertRaises(m.q.Refused):m.retained_guard(session,root,target,False)

    def test_unread_permitted_directory_refuses_instead_of_empty_inventory(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name); denied=root/'tools/__pycache__'; denied.mkdir(parents=True)
            (root/'tools/a.py').write_bytes(b'pass')
            (denied/'unexpected-private-fixture').write_bytes(b'synthetic')
            original=m.os.scandir
            def scan(path):
                if Path(path)==denied: raise PermissionError('private path must not be emitted')
                return original(path)
            session=mock.Mock(deadline=time.monotonic()+30)
            with mock.patch.object(m.q,'verify_sources'),mock.patch.object(m,'verify_refs'), \
                 mock.patch.object(m.os,'scandir',side_effect=scan):
                with self.assertRaisesRegex(m.q.Refused,'retained_directory_unread'):
                    m.retained_guard(session,root,{'tools/a.py':m.q.digest(b'pass')},False)

    def test_real_output_guard_uses_complete_contract_and_exact_state(self):
        import generated_output_contract as contract
        from types import SimpleNamespace
        calls=[]
        state=contract.State(job_start_epoch=time.time(),observed_epoch=time.time(),max_job_seconds=5400)
        with mock.patch.object(m.q,'verify_sources',side_effect=lambda *a:calls.append('raw')), \
             mock.patch.object(m,'verify_refs',side_effect=lambda *a:calls.append('refs')), \
             mock.patch.object(contract,'scan',side_effect=lambda *a:calls.append(a) or {'verified':True}):
            session=SimpleNamespace(deadline=123)
            self.assertEqual(m.generated_guard(session,Path('repo'),{'a':'b'},True,state),{'verified':True})
        self.assertEqual(calls[:2],['raw','refs'])
        self.assertEqual(calls[2],(Path('repo'),{'a':'b'},123,state))

    def test_behavior_controls_use_original_exact_classifier(self):
        session=mock.Mock(); session.run.return_value={'stdout':'{"schema_version":1}','returncode':1}
        with mock.patch.object(m.q,'validate_controls',return_value={'control'}) as classifier, \
             mock.patch.object(m.q,'emit'):
            self.assertEqual(m.behavior_controls(session,Path('observer'),Path('repo'),'baseline'),['control'])
        classifier.assert_called_once_with({'schema_version':1},'baseline',1)
        self.assertEqual(session.run.call_args.args[0][1:],[str(Path('observer/diagnostics/suite_id_lazy_controls.py')),'--repo','repo'])
        with mock.patch.object(m.q,'validate_controls',side_effect=m.q.Refused('controls_unexpected_outcome')):
            with self.assertRaises(m.q.Refused):m.behavior_controls(session,Path('observer'),Path('repo'),'candidate')

    def test_explicit_original_selectors_are_verified_once_and_fail_closed(self):
        session=mock.Mock(); session.run.return_value={'synthetic':'result'}
        with mock.patch.object(m.q,'original_payload',return_value='payload'), \
             mock.patch.object(m.q,'verify_probe') as verify,mock.patch.object(m.q,'emit'):
            m.explicit_controls(session,Path('seed'),Path('repo'))
        self.assertEqual(verify.call_count,5)
        calls=session.run.call_args_list
        self.assertEqual(calls[0].args[0][2:4],['payload','repo/tools'])
        self.assertEqual(calls[0].args[0][-2:], [m.q.JUNCTION,m.q.LOOKUPS[0]])
        self.assertEqual([call.args[0][-1] for call in calls[1:]],list(m.q.SYNTHETIC_SELECTORS))
        session.reset_mock()
        with mock.patch.object(m.q,'original_payload',return_value='payload'), \
             mock.patch.object(m.q,'verify_probe',side_effect=m.q.Refused('probe_failed_or_unread')):
            with self.assertRaises(m.q.Refused):m.explicit_controls(session,Path('seed'),Path('repo'))
        self.assertEqual(session.run.call_count,1)

    def test_exact_sequential_full_pair_workflow(self):
        root=Path(m.__file__).resolve().parent.parent
        flow=(root/'.github/workflows/ci-parallel-proof.yml').read_text()
        self.assertEqual(flow.count('timeout-minutes: 90'),2)
        self.assertEqual(flow.count('needs: baseline'),1)
        self.assertEqual(flow.count('python observer/diagnostics/measure_maintainer_pair.py'),2)
        self.assertNotIn('python observer/diagnostics/diagnose_generated_outputs.py',flow)
        self.assertEqual(flow.count('github.run_attempt == 1'),2)
        self.assertIn("needs.baseline.outputs.safe == 'true' && needs.baseline.outputs.passed == 'true'",flow)
        self.assertEqual(flow.count("GIT_CONFIG_VALUE_0: 'false'"),4)
        self.assertEqual(flow.count("python-version: '3.14.4'"),2)
        self.assertEqual(flow.count('ref: '+m.q.BASE),2)
        self.assertNotIn('upload-artifact',flow)

    def test_hosted_output_controls_precede_real_clone_and_no_temp_benchmark(self):
        import inspect
        source=inspect.getsource(m.execute)
        self.assertIn('verify_retained_controls(session, observer)',source)
        self.assertLess(source.index('verify_retained_controls(session, observer)'),source.index('workspace_clone_root('))
        self.assertNotIn('run_arm(',source)
        self.assertNotIn('classify_case(',source)
        self.assertIn('preserve_identity(progress',source)
        self.assertLess(source.index('preserve_identity(progress'),source.index('for name, argv in COMMANDS'))

    def test_cleanup_failure_cannot_be_overridden_by_successful_evidence(self):
        from types import SimpleNamespace
        for cleanup, commands_passed, expected in ((False, True, 2), (True, False, 1), (True, True, 0), (True, 'unread', 2)):
            with self.subTest(cleanup=cleanup, commands_passed=commands_passed), tempfile.TemporaryDirectory() as name:
                root=Path(name); observer=root/'observer'; seed=root/'seed'
                observer.mkdir(); seed.mkdir()
                env={'GITHUB_OUTPUT':str(root/'github-output'),'GITHUB_ACTIONS':'true','GITHUB_EVENT_NAME':'push','GITHUB_REF':m.q.BRANCH,'GITHUB_RUN_ATTEMPT':'1'}
                session=mock.Mock(); session.cleanup.return_value=cleanup
                emitted=[]
                with mock.patch.object(m,'os',SimpleNamespace(name='nt',environ=env)), \
                     mock.patch.object(m.platform,'python_version',return_value='3.14.4'), \
                     mock.patch.object(m,'environment_identity',return_value={}), \
                     mock.patch.object(m.q,'environment_preflight'),mock.patch.object(m.q,'corpus_preflight'), \
                     mock.patch.object(m.observation,'ObservedSession',return_value=session), \
                     mock.patch.object(m,'execute',return_value={'all_commands_passed':commands_passed}, side_effect=m.q.Refused('retained_directory_unread') if commands_passed == 'unread' else None), \
                     mock.patch.object(m.q,'safe_exception'), \
                     mock.patch.object(m.q,'emit',side_effect=lambda event,**kw:emitted.append((event,kw))), \
                     mock.patch.object(m.tempfile,'mkdtemp',return_value=str(root/'capture')):
                    result=m.main(['--observer',str(observer),'--seed',str(seed),'--variant','baseline','--job-start-epoch',str(time.time())])
                self.assertEqual(result,expected)
                receipt=[row for event,row in emitted if event=='maintainer_arm_summary'][0]
                self.assertEqual(receipt['safe_to_continue'],cleanup and commands_passed != 'unread')
                self.assertEqual(receipt['all_commands_passed'],cleanup and commands_passed is True)
                self.assertFalse(receipt['pair_passed'])
                output=(root/'github-output').read_text()
                self.assertIn('passed='+str(cleanup and commands_passed is True).lower()+'\n',output)

    def test_execute_routes_every_real_guard_through_exact_generated_state(self):
        from contextlib import ExitStack
        from types import SimpleNamespace
        import diagnose_generated_outputs as generated
        import diagnose_staging_layout as staging
        discovery={'test_count':2,'sorted_ids_sha256':'a'*64,'loader_error_count':0,
                   'module_test_count':1,'executed_test_count':0,
                   'ids_encoding':'sorted JSON array, ASCII escaped, compact'}
        units=('test_example.Real',)
        unit_identity={'test_count':2,'test_ids_sha256':'a'*64,'unit_count':1,
                       'unit_names_sha256':'b'*64,'executed_test_count':0,'loader_errors':0,
                       'units_derived_from_actual_objects':True}
        for fail_after_suite in (False,True,'unit_mismatch'):
            with self.subTest(fail_after_suite=fail_after_suite), tempfile.TemporaryDirectory() as raw, ExitStack() as stack:
                root=Path(raw); capture=root/'capture';capture.write_bytes(b'synthetic')
                result={'returncode':0,'stdout':'{}','stderr':'','wall_seconds':1,
                        'tree_cpu_seconds':1,'stdout_path':str(capture),'stderr_path':str(capture)}
                session=mock.Mock(root=root,deadline=time.monotonic()+6000)
                session.run.return_value=result
                session.git.return_value='\n'.join(sorted(m.q.OBSERVER_PATHS))
                expected={m.q.SUITE_PATH:m.q.ORIGINAL_HASH}; progress={};states=[]
                def scan(repo,target,deadline,state):
                    states.append(state)
                    if fail_after_suite is True and len(states)==3:raise m.q.Refused('generated_output_unexpected')
                    return {'guard_verified':True}
                import generated_output_contract as contract
                patches=((m.q,'first_clean',{}),(m.q,'inventory',{'side_effect':[{},expected]}),
                    (m.q,'raw_source_inventory',{'return_value':expected}),
                    (m.q,'read_reviewed_bytes',{'return_value':b'candidate'}),
                    (m.q,'validate_owner_controls',{}),(m.q,'emit',{}),(m.q,'verify_probe',{'return_value':{'valid':True}}),
                    (staging,'verify_retained_controls',{}),(m,'workspace_clone_root',{'return_value':root}),
                    (m,'source_context',{'return_value':expected}),
                    (m.q,'parse_child',{'side_effect':[{'outside_checkout_temp':True,'temp_environment_unchanged':True},discovery]}),
                    (m,'verify_hook_location',{}),(m,'behavior_controls',{'return_value':sorted(m.q.CONTROL_IDS)}),
                    (m,'explicit_controls',{}),(generated,'validate_discovery',{'return_value':(units,unit_identity)}),
                    (m.q,'verify_sources',{}),(m,'verify_refs',{}),(contract,'scan',{'side_effect':scan}),
                    (m,'observe_suite',{'return_value':{'returncode':0,'accounting_valid':True}}),
                    (m,'parse_suite',{'return_value':{'unaccounted':0}}))
                for obj,name,kwargs in patches:stack.enter_context(mock.patch.object(obj,name,**kwargs))
                if fail_after_suite == 'unit_mismatch':
                    prior={'environment':{'default_workers':3,'cpu_count':4},'discovery':discovery,
                           'behavior_control_ids':sorted(m.q.CONTROL_IDS),'unit_discovery':{}}
                    with self.assertRaisesRegex(m.q.Refused,'matched_environment_or_discovery_changed'):
                        m.execute(session,root/'observer',root/'seed','candidate',prior['environment'],prior,progress,time.time())
                    self.assertEqual(states,[])
                    self.assertNotIn('commands',progress)
                    continue
                if fail_after_suite:
                    with self.assertRaisesRegex(m.q.Refused,'generated_output_unexpected'):
                        m.execute(session,root/'observer',root/'seed','baseline',{'default_workers':3,'cpu_count':4},None,progress,time.time())
                    self.assertEqual(progress['suite_observation']['returncode'],0)
                    self.assertEqual(len(progress['commands']),2)
                else:
                    row=m.execute(session,root/'observer',root/'seed','baseline',{'default_workers':3,'cpu_count':4},None,progress,time.time())
                    self.assertTrue(row['all_commands_passed'])
                    self.assertEqual(len(states),7)
                    self.assertEqual([r['command'] for r in row['commands']],[name for name,_ in m.COMMANDS])
                self.assertEqual([(x.marker,x.weights) for x in states[:2]],[('absent','absent')]*2)
                self.assertTrue(all((x.marker,x.weights,x.sessions)==('required','required','required') for x in states[2:]))
                self.assertTrue(all(x.units==units and x.max_job_seconds==5400 for x in states))

    def test_no_suite_patch_or_filters(self):
        source=inspect.getsource(m.execute)
        self.assertNotIn('mock.patch',source)
        self.assertNotIn('--jobs',source)
        self.assertIn('matched_environment_or_discovery_changed',source)
        self.assertIn('initial_suite_weights_or_scratch_present',source)

if __name__=='__main__':unittest.main()
