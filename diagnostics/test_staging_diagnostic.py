import ast
import copy
import inspect
import json
from pathlib import Path
import unittest
from unittest import mock
import diagnose_staging_layout as d


def result(selector,temp_layout):
    lines=dict(d.CASES)[selector] if temp_layout else []
    token=d.q.digest(selector.encode())
    row={'test_token':token,'tests_run':1,'failures':len(lines),'errors':0,'skips':0,
         'expected_failures':0,'unexpected_successes':0,'loader_errors':0,
         'test_successful':not lines,'checkout_named_temp':temp_layout,
         'absolute_response_exact':True,'registered_relative_accepted':True,
         'failure_events':[{'test_token':token,'exception_type':'AssertionError','source_line':line} for line in lines],
         'events_truncated':False}
    return {'returncode':1 if lines else 0,'stdout':d.RESULT_PREFIX+json.dumps(row)},row

class StagingDiagnosticControls(unittest.TestCase):
    def test_exact_predicted_cases_and_zero_skips(self):
        self.assertEqual([lines for _,lines in d.CASES],[[68,68,71],[75],[122],[],[]])
        for selector,_ in d.CASES:
            for temp in (True,False):
                capture,_=result(selector,temp)
                self.assertTrue(d.classify_case(capture,selector,temp)['expectation_matched'])
    def test_arbitrary_failure_wrong_frame_target_policy_and_type_do_not_match(self):
        selector=d.CASES[0][0];capture,row=result(selector,True)
        variants=[]
        for key,value in [('errors',1),('skips',1),('absolute_response_exact',False),
                          ('registered_relative_accepted',False),('test_token','a'*64),('events_truncated',True)]:
            variants.append(row|{key:value})
        for key,value in [('source_line',69),('exception_type','OtherException'),('test_token','b'*64)]:
            changed=copy.deepcopy(row);changed['failure_events'][0][key]=value;variants.append(changed)
        for changed in variants:
            capture['stdout']=d.RESULT_PREFIX+json.dumps(changed)
            self.assertFalse(d.classify_case(capture,selector,True)['expectation_matched'])
    def test_malformed_or_missing_receipt_is_not_expected_failure(self):
        for stdout in ('',d.RESULT_PREFIX+'[]',d.RESULT_PREFIX+'{}\n'+d.RESULT_PREFIX+'{}'):
            with self.assertRaises(d.q.Refused):d.classify_case({'stdout':stdout,'returncode':1},d.CASES[0][0],True)
    def test_mismatch_does_not_emit_raw_payload(self):
        selector=d.CASES[0][0];capture,row=result(selector,True)
        row['failure_events']=[{'test_token':'PRIVATE','source_line':'PRIVATE','exception_type':'PRIVATE'}]
        capture['stdout']=d.RESULT_PREFIX+json.dumps(row)
        with self.assertRaises(d.q.Refused) as caught:
            d.classify_case(capture,selector,True)
        self.assertNotIn('PRIVATE',str(caught.exception))
    def test_malformed_schema_types_ranges_and_unknown_fields_refuse(self):
        selector=d.CASES[0][0];capture,row=result(selector,True)
        variants=[{}, row|{'unknown':1}]
        for key,value in [('tests_run',True),('failures',-1),('errors',10001),
                          ('checkout_named_temp',1),('failure_events',{}),('test_token','x'),
                          ('events_truncated',None)]:
            variants.append(row|{key:value})
        for key,value in [('source_line',True),('exception_type','Unknown'),('test_token','x')]:
            changed=copy.deepcopy(row);changed['failure_events'][0][key]=value;variants.append(changed)
        changed=copy.deepcopy(row);del changed['loader_errors'];variants.append(changed)
        changed=copy.deepcopy(row);changed['failure_events'][0]['extra']=1;variants.append(changed)
        for changed in variants:
            with self.subTest(changed=changed),self.assertRaises(d.q.Refused):
                d.classify_case(capture|{'stdout':d.RESULT_PREFIX+json.dumps(changed)},selector,True)
        for raw in ('{', json.dumps(row)[:-1]+',"tests_run":1}'):
            with self.assertRaises(d.q.Refused):
                d.classify_case(capture|{'stdout':d.RESULT_PREFIX+raw},selector,True)
        with self.assertRaises(d.q.Refused):
            d.classify_case(capture|{'returncode':True},selector,True)

    def test_malformed_receipt_stops_arm_before_guard_or_next_case(self):
        session=mock.Mock();session.run.return_value={'stdout':d.RESULT_PREFIX+'{}','returncode':1}
        with mock.patch.object(d.m,'source_context',return_value={'a':'hash'}), \
             mock.patch.object(d.q,'parse_child',return_value={'outside_checkout_temp':True,'temp_environment_unchanged':True}), \
             mock.patch.object(d.q,'emit'),mock.patch.object(d.m,'retained_guard') as guard:
            progress=[]
            with self.assertRaises(d.q.Refused):d.run_arm(session,Path('o'),Path('s'),Path('r'),'temp-layout',{'a':'hash'},progress)
            self.assertEqual(session.run.call_count,2)
            self.assertEqual(progress[0]['cases'],[])
            guard.assert_not_called()

    def test_budget_includes_cleanup_from_job_origin(self):
        self.assertEqual(d.budget_deadline(1000,1100,500),940)
        with self.assertRaises(d.q.Refused):d.budget_deadline(1000,1540,500)
    def test_setup_has_two_original_arms_no_full_suite_or_candidate(self):
        source=inspect.getsource(d.setup)
        self.assertIn('q.create_measurement_root',source)
        self.assertIn('m.workspace_clone_root',source)
        self.assertNotIn('COMMANDS',source)
        self.assertNotIn('tools/suite.py',source)
        self.assertNotIn('behavior_controls',source)
        self.assertIn("'baseline', expected, b''",inspect.getsource(d.run_arm))
    def test_guard_refusal_stops_before_next_test(self):
        session=mock.Mock();session.run.return_value={'stdout':'','returncode':0}
        with mock.patch.object(d.m,'source_context',return_value={'a':'hash'}), \
             mock.patch.object(d.q,'parse_child',return_value={'outside_checkout_temp':True,'temp_environment_unchanged':True}), \
             mock.patch.object(d,'classify_case',return_value={'expectation_matched':False}), \
             mock.patch.object(d.q,'emit'),mock.patch.object(d.m,'retained_guard',side_effect=d.q.Refused('unexpected_retained_file')):
            progress=[]
            with self.assertRaises(d.q.Refused):d.run_arm(session,Path('o'),Path('s'),Path('r'),'temp-layout',{'a':'hash'},progress)
            self.assertEqual(session.run.call_count,2)
            self.assertEqual(len(progress[0]['cases']),1)
    def test_final_verdict_requires_both_expectations_and_owned_cleanup(self):
        import tempfile,time
        from types import SimpleNamespace
        for matched,clean,wanted in ((True,True,0),(False,True,2),(True,False,2)):
            with tempfile.TemporaryDirectory() as name:
                root=Path(name);observer=root/'observer';seed=root/'seed';observer.mkdir();seed.mkdir()
                env={'GITHUB_ACTIONS':'true','GITHUB_EVENT_NAME':'push','GITHUB_REF':d.q.BRANCH,'GITHUB_RUN_ATTEMPT':'1'}
                session=mock.Mock();session.cleanup.return_value=clean;emitted=[]
                def setup(session,observer,seed,arms):
                    arms.extend([{'expectations_matched':True},{'expectations_matched':matched}])
                with mock.patch.object(d,'os',SimpleNamespace(name='nt',environ=env)), \
                     mock.patch.object(d.platform,'python_version',return_value='3.14.4'), \
                     mock.patch.object(d.q,'environment_preflight'),mock.patch.object(d.q,'corpus_preflight'), \
                     mock.patch.object(d.q,'Session',return_value=session),mock.patch.object(d.q,'safe_exception'), \
                     mock.patch.object(d,'setup',side_effect=setup), \
                     mock.patch.object(d.q,'emit',side_effect=lambda event,**kw:emitted.append((event,kw))), \
                     mock.patch.object(d.tempfile,'mkdtemp',return_value=str(root/'capture')):
                    rc=d.main(['--observer',str(observer),'--seed',str(seed),'--job-start-epoch',str(time.time())])
                self.assertEqual(rc,wanted)
                row=[row for event,row in emitted if event=='staging_diagnostic_summary'][0]
                self.assertEqual(row['status'],'diagnostic-passed' if wanted==0 else 'inconclusive')
                self.assertFalse(row['qualification'])
                self.assertEqual(row['performance_probes'],0)

    def test_hosted_controls_owned_deadline_and_strict_receipt_before_arms(self):
        import tempfile
        from types import SimpleNamespace
        row={'cases':[{'id':case,'refusal':refusal,'passed':True} for case,refusal in d.retained_controls.CASES],
             'count':5,'synthetic_source_ref_isolation':True,'unread_mode':'injected_scandir_permission_error',
             'native_link_kind':'junction','fixture_cleanup_verified':True,'passed':True}
        for changed,code,ok in ((row,0,True),(row,2,False),(row|{'count':True},0,False),
                               (row|{'native_link_kind':'symlink'},0,False),(row|{'fixture_cleanup_verified':False},0,False)):
            with tempfile.TemporaryDirectory() as directory,mock.patch.object(d.q,'emit'):
                session=SimpleNamespace(root=Path(directory),deadline=1234,
                    run=mock.Mock(return_value={'stdout':json.dumps(changed),'returncode':code}))
                if ok:d.verify_retained_controls(session,Path('observer'))
                else:
                    with self.assertRaises(d.q.Refused):d.verify_retained_controls(session,Path('observer'))
                argv,cwd=session.run.call_args.args
                self.assertEqual(argv[-2:],['--deadline','1234'])
                self.assertTrue((session.root/'retained-controls').is_dir())
        source=inspect.getsource(d.setup)
        self.assertLess(source.index('verify_retained_controls('),source.index('q.create_measurement_root('))

    def test_workflow_launches_only_one_narrow_job(self):
        root=Path(d.__file__).resolve().parent.parent
        text=(root/'.github/workflows/ci-parallel-proof.yml').read_text()
        self.assertEqual(text.count('timeout-minutes: 10'),1)
        self.assertIn('python observer/diagnostics/diagnose_staging_layout.py',text)
        self.assertNotIn('python observer/diagnostics/measure_maintainer_pair.py',text)
        self.assertNotIn('needs: baseline',text)
        self.assertEqual(text.count("GIT_CONFIG_VALUE_0: 'false'"),2)
        self.assertIn('PROOF_JOB_START_EPOCH',text)
        self.assertIn('github.run_attempt == 1',text)

if __name__=='__main__':unittest.main()
