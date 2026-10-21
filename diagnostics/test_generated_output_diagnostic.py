import inspect
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock
import diagnose_generated_outputs as d


class GeneratedDiagnosticControls(unittest.TestCase):
    def receipt(self):
        row={'test_count':2,'test_ids_sha256':'a'*64,'unit_names':['test_example.Real'],
             'executed_test_count':0,'loader_errors':0}
        return {'returncode':0,'stdout':d.RESULT_PREFIX+json.dumps(row)},row

    def test_discovery_requires_actual_objects_and_bounded_unique_population(self):
        result,row=self.receipt()
        units,public=d.validate_discovery(result)
        self.assertEqual(units,('test_example.Real',))
        self.assertNotIn('unit_names',public)
        self.assertTrue(public['units_derived_from_actual_objects'])
        source=inspect.getsource(d.discovery_child)
        self.assertIn('original_suite._units(discovered)',source)
        self.assertNotIn('rsplit',source)
        for changed in ({},row|{'test_count':True},row|{'unit_names':[]},row|{'unit_names':['bad/path']},
                        row|{'unit_names':['test_example.Real']*2},row|{'executed_test_count':1},row|{'extra':1}):
            with self.assertRaises(d.q.Refused):
                d.validate_discovery(result|{'stdout':d.RESULT_PREFIX+json.dumps(changed)})

    def test_discovery_malformed_json_duplicate_keys_and_exit_types_refuse(self):
        result,row=self.receipt()
        for changed in (result|{'returncode':False},result|{'stdout':d.RESULT_PREFIX+'{'},
                        result|{'stdout':d.RESULT_PREFIX+json.dumps(row)[:-1]+',"test_count":2}'},
                        result|{'stdout':result['stdout']+'\n'+result['stdout']}):
            with self.assertRaises(d.q.Refused):d.validate_discovery(changed)

    def test_native_unittest_targets_are_exact_and_no_temp_expected_failures(self):
        self.assertEqual(d.CASES,(
            'test_hook_payload.UnreadableHookPayloads.test_escaped_trigger_is_a_declared_raw_search_limit',
            'test_subagent_staging_hook.SubagentStagingLaunch.test_existing_nonempty_folder_accepts_relative_absolute_and_backslash_routes',
            'test_suite.SuiteRunControls.test_a_complete_run_atomically_replaces_the_unit_weights'))
        source=inspect.getsource(d.setup)
        self.assertNotIn('COMMANDS',source)
        self.assertNotIn('tools/suite.py',source)
        self.assertIn("'baseline', expected, b''",source)
        self.assertIn("weights='absent'",source)
        self.assertNotIn('create_measurement_root',source)

    def test_source_and_refs_checked_before_output_scan(self):
        calls=[]
        with mock.patch.object(d.q,'verify_sources',side_effect=lambda *a:calls.append('raw')), \
             mock.patch.object(d.m,'verify_refs',side_effect=lambda *a:calls.append('refs')), \
             mock.patch.object(d.contract,'scan',side_effect=lambda *a:calls.append('outputs')):
            d.guarded(SimpleNamespace(deadline=123),Path('r'),{},object())
        self.assertEqual(calls,['raw','refs','outputs'])
        with mock.patch.object(d.q,'verify_sources',side_effect=d.q.Refused('raw')), \
             mock.patch.object(d.contract,'scan') as scan:
            with self.assertRaises(d.q.Refused):d.guarded(SimpleNamespace(deadline=123),Path('r'),{},object())
            scan.assert_not_called()

    def test_later_guard_refusal_preserves_identity_and_first_case_exit(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);session=mock.Mock(root=root,deadline=time.monotonic()+60)
            session.run.return_value={'returncode':0,'stdout':'{}'}
            session.git.return_value='\n'.join(sorted(d.q.OBSERVER_PATHS))
            expected={d.q.SUITE_PATH:d.q.ORIGINAL_HASH};progress={}
            with mock.patch.object(d.q,'first_clean'),mock.patch.object(d.q,'inventory',return_value={}), \
                 mock.patch.object(d.q,'raw_source_inventory',return_value=expected), \
                 mock.patch.object(d.m,'environment_identity',return_value={'finite':'identity'}), \
                 mock.patch.object(d.q,'emit'),mock.patch.object(d.q,'validate_owner_controls'), \
                 mock.patch.object(d,'verify_retained_controls'),mock.patch.object(d,'CONTRACT_CONTROL_COUNT',1), \
                 mock.patch.object(d.q,'verify_probe',return_value={'valid':True}), \
                 mock.patch.object(d.m,'workspace_clone_root',return_value=root), \
                 mock.patch.object(d.m,'source_context',return_value=expected), \
                 mock.patch.object(d.q,'parse_child',return_value={'outside_checkout_temp':True,'temp_environment_unchanged':True}), \
                 mock.patch.object(d.m,'verify_hook_location'), \
                 mock.patch.object(d,'validate_discovery',return_value=(('test_example.Real',),{'unit_count':1})), \
                 mock.patch.object(d,'guarded',side_effect=[{}, {}, d.q.Refused('unsafe_output')]):
                with self.assertRaisesRegex(d.q.Refused,'unsafe_output'):
                    d.setup(session,Path('o'),Path('s'),time.time(),progress)
            self.assertEqual(progress['source_sha'],d.q.BASE)
            self.assertEqual(progress['discovery'],{'unit_count':1})
            self.assertEqual(len(progress['cases']),1)
            self.assertEqual(progress['cases'][0]['returncode'],0)
            self.assertEqual(session.run.call_count,5)

    def test_hosted_contract_population_is_fixed_and_complete(self):
        import test_generated_output_contract
        suite=unittest.defaultTestLoader.loadTestsFromModule(test_generated_output_contract)
        self.assertEqual(suite.countTestCases(),d.CONTRACT_CONTROL_COUNT)
        self.assertEqual(d.CONTRACT_CONTROL_COUNT,41)
        self.assertEqual(len(d.q.DECLARED_CONTROL_IDS),9)
        import staging_retained_controls
        self.assertEqual(len(staging_retained_controls.CASES),5)
        self.assertEqual(d.q.BASE,'104ee03cd4d37519b12b3edbc4da5fbf31b631cf')
        source=inspect.getsource(d.setup)
        self.assertLess(source.index("'native'"),source.index("'retained'"))
        self.assertLess(source.index("'retained'"),source.index("'contract'"))
        self.assertNotIn('diagnose_windows_snapshot',source)
        self.assertNotIn('windows_snapshot_controls',source)

    def test_job_origin_reserves_cleanup(self):
        self.assertEqual(d.budget_deadline(1000,1100,500),940)
        with self.assertRaises(d.q.Refused):d.budget_deadline(1000,1540,500)

    def test_workflow_exclusively_launches_one_narrow_job(self):
        text=(Path(d.__file__).resolve().parent.parent/'.github/workflows/ci-parallel-proof.yml').read_text()
        self.assertEqual(text.count('timeout-minutes: 10'),1)
        self.assertEqual(text.count('python observer/diagnostics/diagnose_generated_outputs.py'),1)
        for forbidden in ('python observer/diagnostics/diagnose_windows_snapshot.py', 'needs: baseline','python observer/diagnostics/measure_maintainer_pair.py','upload-artifact'):
            self.assertNotIn(forbidden,text)
        self.assertEqual(text.count("GIT_CONFIG_VALUE_0: 'false'"),2)
        self.assertIn('github.run_attempt == 1',text)


if __name__=='__main__':unittest.main()
