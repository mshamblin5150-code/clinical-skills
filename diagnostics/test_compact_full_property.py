"""Migrated full population through public boundaries, synthetic data only."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
import json
import os
import re
from unittest import mock

import compact_native_controls as native
import compact_native_consumers as consumers
import compact_replacement_property as property_control
import validate_compact_native as subject
import test_compact_native_controls as fixtures
from test_compact_replacement_calibration import CalibrationNative
from test_compact_replacement_property import PropertyNative


def full_runtime(live=None, calibration=None):
    """Separate calibration model preserves each inherited live fault boundary."""
    runtime, owners, api = fixtures.NativePacketControls().runtime(live or fixtures.SharingNative())
    calibration = calibration or CalibrationNative()
    factories = iter((calibration,))
    runtime.api_factory = lambda: next(factories, api)
    runtime.owner_factory = fixtures.SyntheticCoordinatorOwners()
    runtime.environment = {}
    runtime.terminate_coordinator = lambda owner: setattr(owner, 'stopped', True)
    return runtime, owners, api


class FullPropertyTests(unittest.TestCase):
    def test_observation_faults_preserve_exact_primary_and_invalidate_unknown(self):
        for operation in ('get', 'update', 'setitem'):
            for after_write in (False, True):
                with self.subTest(operation=operation, after_write=after_write):
                    primary = OSError('private original control error')
                    secondary = RuntimeError('private observation error')
                    class Broken(dict):
                        def get(self, key, default=None):
                            if operation == 'get':
                                raise secondary
                            return super().get(key, default)
                        def update(self, *args, **kwargs):
                            if operation == 'update':
                                if after_write:
                                    super().update(*args, **kwargs)
                                raise secondary
                            return super().update(*args, **kwargs)
                        def __setitem__(self, key, value):
                            if operation == 'setitem' and key.endswith('_witness'):
                                if after_write:
                                    super().__setitem__(key, value)
                                raise secondary
                            return super().__setitem__(key, value)
                    progress = Broken(control_count=0, failure_witness={'status': 'verified'},
                                      first_property_witness={'status': 'verified'})
                    runtime, _, _ = full_runtime()
                    # Malformed projections exercise actual serialization and bounding,
                    # not a Boolean-only success/failure stand-in.
                    with tempfile.TemporaryDirectory() as tmp, \
                         mock.patch.object(subject, 'run_first_property', side_effect=primary), \
                         mock.patch.object(native, 'failure_witness',
                             return_value={'status': 'verified', 'oversize': 'x' * 4096}
                             if operation == 'update' else object()), \
                         mock.patch.object(property_control, 'property_witness',
                             return_value={'status': 'verified'} if operation == 'update' else object()), \
                         mock.patch.object(native, 'run_control') as later:
                        with self.assertRaises(OSError) as caught:
                            subject.perform_controls(Path(tmp), runtime, progress)
                    self.assertIs(primary, caught.exception)
                    self.assertIsNone(dict.get(progress, 'failure_witness'))
                    self.assertIsNone(dict.get(progress, 'first_property_witness'))
                    self.assertEqual(0, progress['control_count'])
                    later.assert_not_called()
                    self.assertTrue(runtime.cleanup())

    def test_silent_update_cannot_retain_oversized_stale_success(self):
        class IgnoreUpdate(dict):
            def update(self, *args, **kwargs):
                pass
        progress = IgnoreUpdate(failure_witness={'oversize': 'x' * 4096},
                                first_property_witness={'status': 'verified'})
        subject.bound_witnesses(progress)
        self.assertEqual({'failure_witness': None, 'first_property_witness': None}, progress)

    def test_unserializable_projection_is_unknown(self):
        progress = {'failure_witness': object(), 'first_property_witness': {'status': 'verified'}}
        subject.bound_witnesses(progress)
        self.assertEqual({'failure_witness': None, 'first_property_witness': None}, progress)

    def test_projector_fault_invalidates_stale_success_without_replacing_primary(self):
        primary = OSError('private control error')
        runtime, _, _ = full_runtime()
        progress = {'failure_witness': {'status': 'verified'},
                    'first_property_witness': {'status': 'verified'}}
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(subject, 'run_first_property', side_effect=primary), \
             mock.patch.object(native, 'failure_witness', side_effect=RuntimeError()), \
             mock.patch.object(property_control, 'property_witness', side_effect=RuntimeError()):
            with self.assertRaises(OSError) as caught:
                subject.perform_controls(Path(tmp), runtime, progress)
        self.assertIs(primary, caught.exception)
        self.assertIsNone(progress['failure_witness'])
        self.assertIsNone(progress['first_property_witness'])
        self.assertTrue(runtime.cleanup())

    def test_full_driver_runs_fresh_property_first_and_all_other_controls_unchanged(self):
        runtime, _, live = full_runtime(PropertyNative())
        calls = []
        core, consumer = native.run_control, consumers.run_consumer_control
        def run_core(name, root, passed):
            calls.append((name, root.name, passed is runtime))
            return core(name, root, passed)
        def run_consumer(name, root, passed):
            calls.append((name, root.name, passed is runtime))
            return consumer(name, root, passed)
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()), \
             mock.patch.object(native, 'run_control', run_core), \
             mock.patch.object(consumers, 'run_consumer_control', run_consumer):
            progress = {}
            rows = subject.perform_controls(Path(tmp), runtime, progress)
        self.assertEqual('replacement-property-v1', rows[0]['evidence']['schema'])
        self.assertEqual('access_5', rows[0]['evidence']['calibration']['held_error'])
        self.assertEqual('verified', rows[0]['evidence']['control']['replacement_poststate'])
        self.assertEqual('disposition_verified', rows[0]['evidence']['control']['retention'])
        expected = list(native.CONTROL_IDS[1:]) + list(consumers.CONTROL_IDS)
        self.assertEqual([(name, name, True) for name in expected], calls)
        self.assertEqual(list(native.CONTROL_IDS) + list(consumers.CONTROL_IDS), [row['id'] for row in rows])
        self.assertEqual((18,35,34,1), (len(rows),sum(row['owned_commands'] for row in rows),len(runtime.owners),runtime.nested_command_slots))
        self.assertTrue(runtime.cleanup())

    def test_property_faults_stop_before_second_dispatch_and_keep_distinct_observation(self):
        for fault in ('calibration_error', 'calibration_close', 'live_mismatch', 'live_mutation', 'live_close'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as tmp:
                calibration=PropertyNative(held=999 if fault=='calibration_error' else 32 if fault=='live_mismatch' else 5)
                if fault=='calibration_close':calibration.failures.add(('close','source.bin'))
                class Live(PropertyNative):
                    def move(self,source,destination,flags):
                        result=super().move(source,destination,flags)
                        if fault=='live_mutation':Path(source).write_bytes(b'X'*37)
                        return result
                    def close(self,handle):
                        path=self.handles[handle]['path']
                        super().close(handle)
                        if fault=='live_close' and self.calls and path.name=='receipt-replacement.bin':
                            raise OSError('PRIVATE_CLOSE')
                runtime,_,live=full_runtime(Live(),calibration)
                progress={'control_count':0}
                with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(native,'run_control') as next_control:
                    with self.assertRaises(Exception):subject.perform_controls(Path(tmp),runtime,progress)
                    next_control.assert_not_called()
                self.assertEqual(0,progress['control_count'])
                self.assertEqual('snapshot_share_receipt_success',progress['failed_control'])
                self.assertEqual('replacement-property-v1',progress['first_property_witness']['schema'])
                self.assertFalse(live.disposed)
                runtime.cleanup()

    def test_later_failure_keeps_completed_first_property_separate(self):
        runtime,_,_=full_runtime()
        progress={'control_count':0}
        primary=OSError('PRIVATE_LATER_FAILURE')
        def fail_second(name,root,passed):
            self.assertEqual('replacement_identity_refusal',name)
            passed.control_observation={'control':name,'phase':'prepare'}
            raise primary
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()),mock.patch.object(native,'run_control',fail_second):
            with self.assertRaises(OSError) as caught:subject.perform_controls(Path(tmp),runtime,progress)
        self.assertIs(primary,caught.exception)
        self.assertEqual(1,progress['control_count'])
        self.assertEqual('verified',progress['first_property_witness']['calibration']['status'])
        self.assertEqual('replacement_identity_refusal',progress['failure_witness']['control'])
        self.assertTrue(runtime.cleanup())

    def test_population_reorder_rename_count_mutants_refuse_before_any_control(self):
        for ids,counts in ((native.CONTROL_IDS[::-1],native.CONTROL_COMMAND_COUNTS),
                (('wrong',)+native.CONTROL_IDS[1:],native.CONTROL_COMMAND_COUNTS),
                (native.CONTROL_IDS,(2,)+native.CONTROL_COMMAND_COUNTS[1:])):
            runtime,_,_=full_runtime()
            with tempfile.TemporaryDirectory() as tmp,mock.patch.object(native,'CONTROL_IDS',ids),mock.patch.object(native,'CONTROL_COMMAND_COUNTS',counts),mock.patch.object(subject,'run_first_property') as first:
                with self.assertRaises(subject.q.Refused):subject.perform_controls(Path(tmp),runtime,{})
                first.assert_not_called()
            self.assertFalse(runtime.owners)


def selected_push_workflows(directory, branch):
    """Evaluate the current repository's explicit push-filter shapes, not YAML generally."""
    import fnmatch
    selected=[]
    paths=sorted(directory.glob('*.yml'))
    if {path.name for path in paths} != {'checks.yml','tracker.yml','ci-checkpoint-discovery.yml',
            'ci-compact-first-control.yml','ci-compact-native.yml','ci-current-parallel.yml',
            'ci-parallel-proof.yml','ci-reader-attribution.yml','ci-threshold-module.yml'}:
        raise AssertionError('workflow population changed')
    for path in paths:
        text=path.read_text()
        header=text.split('\njobs:',1)[0]
        if '\non:\n' not in header:raise AssertionError('unread event shape')
        events=header.split('\non:\n',1)[1]
        push=re.search(r'^  push:\s*\n((?:    .*\n|\s*#.*\n)*)',events,re.M)
        if not push:
            if re.search(r'\bpush\b', '\n'.join(line for line in events.splitlines() if not line.lstrip().startswith('#'))):
                raise AssertionError('unread push shape')
            continue
        filters={key:[item.strip().strip("'\"") for item in values.split(',')]
            for key,values in re.findall(r'^    (branches|branches-ignore|tags|tags-ignore): \[([^\]]*)\]',push.group(1),re.M)}
        allowed=not filters.get('branches') or any(fnmatch.fnmatchcase(branch,p) for p in filters['branches'])
        denied=any(fnmatch.fnmatchcase(branch,p) for p in filters.get('branches-ignore',()))
        if allowed and not denied:selected.append(path.name)
    return selected


class FullRouteAccountingTests(unittest.TestCase):
    def test_workflow_double_activation_and_wrong_single_selector_mutants_refuse(self):
        workflows=Path(subject.__file__).parent.parent/'.github/workflows'
        original=Path.read_text
        for mutation in ('double','isolated_only','no_route','main_expansion'):
            def altered(path,*args,**kwargs):
                text=original(path,*args,**kwargs)
                if path.parent!=workflows:return text
                if mutation in ('double','isolated_only') and path.name=='ci-compact-first-control.yml':
                    text=text.replace("branches-ignore: ['**']\n    tags-ignore: ['**']",'branches: [diagnostic/2013-parallel-proof-20261020]')
                if mutation in ('isolated_only','no_route') and path.name=='ci-compact-native.yml':
                    text=text.replace('branches: [diagnostic/2013-parallel-proof-20261020]',"branches-ignore: ['**']\n    tags-ignore: ['**']")
                if mutation=='main_expansion' and path.name=='checks.yml':text=text.replace('branches: [main]',"branches: ['**']")
                return text
            with self.subTest(mutation=mutation),mock.patch.object(Path,'read_text',altered),self.assertRaises(AssertionError):
                self.test_workflow_selects_only_full_route_on_this_push()

    def test_workflow_selects_only_full_route_on_this_push(self):
        workflows=Path(subject.__file__).parent.parent/'.github/workflows'
        self.assertEqual(['ci-compact-native.yml'],selected_push_workflows(workflows,'diagnostic/2013-parallel-proof-20261020'))
        self.assertEqual(['checks.yml'],selected_push_workflows(workflows,'main'))

    def test_complete_full_accounting_and_retained_property_use_actual_workflow_cli(self):
        from types import SimpleNamespace
        import test_compact_native_validation as harnesses
        directory=Path(subject.__file__).parent
        budget=json.loads((directory/'compact-native-budget.json').read_text())
        accounting=json.loads((directory/'compact-native-property-accounting.json').read_text())
        harness=harnesses.FinalizationControls();original_execute=subject.execute
        args0=harness.harness()
        text=(directory.parent/'.github/workflows/ci-compact-native.yml').read_text()
        commands=[line.strip().split()[2:] for line in text.splitlines() if line.strip().startswith('python ')]
        self.assertEqual(1,len(commands))
        args=[args0[1] if arg=='observer' else '1000' if arg=='$env:PROOF_JOB_START_EPOCH' else arg for arg in commands[0]]
        try:
            observer=Path(args[args.index('--observer')+1]);(observer/'diagnostics').mkdir()
            (observer/'diagnostics/compact-native-budget.json').write_text(json.dumps(subject.BUDGET))
            session=harness.session;session.owners=[];session.root=observer.parent/'source-captures';session.root.mkdir();session.deadline=540
            old_clean,old_inventory,old_verify=subject.q.first_clean,subject.q.raw_source_inventory,subject.q.verify_sources
            def clean(current,*args,**kwargs):
                if current is not session:return old_clean(current,*args,**kwargs)
                session.owners.extend([None]*3)
            def inventory(current,*args,**kwargs):
                if current is not session:return old_inventory(current,*args,**kwargs)
                session.owners.extend([None]*2);return {'synthetic':'inventory'}
            def verify(current,*args,**kwargs):
                if current is not session:return old_verify(current,*args,**kwargs)
                session.owners.extend([None]*4)
            calibration=PropertyNative();peak=[];move=calibration.move
            def measured(source,destination,flags):
                peak.append(sum(path.stat().st_size for path in Path(source).parent.iterdir()))
                return move(source,destination,flags)
            calibration.kernel.MoveFileExW.call=measured
            runtime,_,live=full_runtime(PropertyNative(),calibration)
            runtime.work_deadline,runtime.hard_deadline=540,600;runtime.clock=lambda:0
            with mock.patch.object(subject,'execute',original_execute),mock.patch.object(subject,'make_runtime',return_value=runtime), \
                 mock.patch.object(subject.q,'first_clean',clean),mock.patch.object(subject.q,'raw_source_inventory',inventory), \
                 mock.patch.object(subject.q,'verify_sources',verify),mock.patch.object(subject,'validate_core_pins'), \
                 mock.patch.dict(os.environ,{'GITHUB_SHA':'a'*40}):
                self.assertEqual(0,subject.main(args),harness.stdout.getvalue())
            terminal=json.loads(harness.stdout.getvalue().splitlines()[-1])
            retained=json.loads((session.root/'native-validation.json').read_bytes())
            self.assertEqual('compact-native-property-v1',retained['schema'])
            self.assertEqual('replacement-property-v1',retained['first_property_route'])
            self.assertFalse(retained['production_qualified'])
            self.assertEqual('disposition_verified',retained['controls'][0]['evidence']['control']['retention'])
            self.assertEqual(18,len(retained['controls']))
            self.assertEqual([74,74],peak)
            # Inventory every regular content object. Existing capture aliases
            # (hardlink/reparse) share a funded capture object, not a new body.
            capture_ids={(p.stat().st_dev,p.stat().st_ino) for owner in runtime.owners
                         for p in (Path(owner.stdout_path),Path(owner.stderr_path))}
            auxiliary={};receipts=[];ready=[];seen=set()
            for path in sorted(observer.parent.rglob('*')):
                if not path.is_file() or observer in path.parents or session.root in path.parents:continue
                item=path.stat();identity=(item.st_dev,item.st_ino)
                if identity in capture_ids or identity in seen:continue
                seen.add(identity)
                relative=str(path.relative_to(observer.parent))
                if re.fullmatch(r'compact-\d{6}-(eligibility|outcome|terminal)\.json',path.name):receipts.append(path)
                elif path.name=='coordinator-ready.json':ready.append(path)
                else:auxiliary[relative]=path.read_bytes()
            self.assertEqual({
                'snapshot_share_receipt_success/calibration/target.bin':b'synthetic replacement must be denied\n',
                'snapshot_share_receipt_success/first-control/receipt-replacement.bin':b'synthetic replacement must be denied\n',
                'replacement_identity_refusal/retained-original.bin':b'synthetic output\n'},auxiliary)
            self.assertEqual(1,len(ready));self.assertLessEqual(ready[0].stat().st_size,16384)
            self.assertLessEqual(len(receipts),budget['max_compact_receipts'])
            self.assertTrue(all(path.stat().st_size<=budget['max_compact_receipt_bytes'] for path in receipts))
            native_pairs=len(runtime.owners)+runtime.nested_command_slots
            conservative_pairs=budget['max_source_commands']+native_pairs
            raw_bytes=conservative_pairs*2*budget['max_capture_bytes']
            compact_bytes=budget['max_compact_receipts']*budget['max_compact_receipt_bytes']
            maximum=1024*1024-max(peak)
            encoded=b'{"p":"'+b'x'*(maximum-8)+b'"}'
            receipt_root=observer.parent/'max-receipt';receipt_root.mkdir()
            receipt_session=SimpleNamespace(root=receipt_root,deadline=540)
            receipt=subject.retain_native_receipt(receipt_session,encoded)
            self.assertEqual(encoded,(receipt_root/'native-validation.json').read_bytes())
            with self.assertRaises(subject.q.Refused):subject.retain_native_receipt(receipt_session,encoded+b' ')
            fixed_existing=sum(len(raw) for name,raw in auxiliary.items() if '/calibration/' not in name)
            private=raw_bytes+compact_bytes+16384+receipt['receipt_bytes']+65536+fixed_existing+max(peak)
            work,hard=subject.budget_deadlines(1000,1000,0)
            self.assertLessEqual(len(harness.stdout.getvalue().splitlines(keepends=True)[-1].encode()),4096)
            self.assertLessEqual(len(json.dumps({key:terminal[key] for key in ('failure_witness','first_property_witness')}).encode()),2048)
            self.assertEqual({
                'control_count':len(retained['controls']), 'native_top_level_owners':len(runtime.owners),
                'native_nested_pairs':runtime.nested_command_slots,'native_pairs':native_pairs,
                'source_success_commands':len(session.owners),'source_max_commands':budget['max_source_commands'],
                'success_capture_pairs':len(session.owners)+native_pairs,'conservative_capture_pairs':conservative_pairs,
                'conservative_streams':conservative_pairs*2,'stream_max_bytes':budget['max_capture_bytes'],
                'raw_content_bytes':raw_bytes,'compact_receipt_count':budget['max_compact_receipts'],
                'compact_receipt_max_bytes':budget['max_compact_receipt_bytes'],'compact_content_bytes':compact_bytes,
                'coordinator_ready_max_bytes':16384,'private_failure_max_bytes':65536,
                'existing_auxiliary_bytes':fixed_existing,'calibration_fixture_bytes':max(peak),
                'aggregate_receipt_max_bytes':receipt['receipt_bytes'],'private_content_bytes':private,
                'including_public_content_bytes':private+subject.reader.BUDGET['max_receipt_bytes'],
                'work_seconds':work,'cleanup_seconds':hard-work,'total_job_seconds':hard,
            },accounting)
        finally:harness.doCleanups()

    def test_every_full_accounting_field_mutation_is_rejected(self):
        path=Path(subject.__file__).with_name('compact-native-property-accounting.json')
        original=Path.read_text;values=json.loads(original(path))
        for field in values:
            def altered(target,*args,**kwargs):
                text=original(target,*args,**kwargs)
                if target==path:
                    row=json.loads(text);row[field]=999;return json.dumps(row)
                return text
            with self.subTest(field=field),mock.patch.object(Path,'read_text',altered),self.assertRaises(AssertionError):
                self.test_complete_full_accounting_and_retained_property_use_actual_workflow_cli()


class FullFailureTransportTests(unittest.TestCase):
    def test_early_calibration_and_late_control_failures_fit_actual_terminal(self):
        import test_compact_native_validation as harnesses
        for stage in ('calibration','last_core','last_consumer'):
            harness=harnesses.FinalizationControls();args=harness.harness()
            try:
                calibration=PropertyNative(held=999 if stage=='calibration' else 5)
                runtime,_,_=full_runtime(calibration=calibration)
                runtime.work_deadline,runtime.hard_deadline=540,600;runtime.clock=lambda:0
                core,consumer=native.run_control,consumers.run_consumer_control
                primary=OSError('PRIVATE_ORIGINAL')
                def run_core(name,root,passed):
                    row=core(name,root,passed)
                    if stage=='last_core' and name=='terminal_readback_unknown':raise primary
                    return row
                def run_consumer(name,root,passed):
                    row=consumer(name,root,passed)
                    if stage=='last_consumer' and name=='measured_original_outcomes':raise primary
                    return row
                def execute(session,runtime,observer,progress):
                    progress['stage']='controls'
                    subject.perform_controls(observer.parent,runtime,progress)
                with mock.patch.object(subject,'make_runtime',return_value=runtime),mock.patch.object(subject,'execute',execute), \
                     mock.patch.object(native,'run_control',run_core),mock.patch.object(consumers,'run_consumer_control',run_consumer):
                    self.assertEqual(2,subject.main(args))
                terminal=json.loads(harness.stdout.getvalue().splitlines()[-1])
                self.assertEqual({'calibration':0,'last_core':11,'last_consumer':17}[stage],terminal['control_count'])
                self.assertEqual('inconclusive',terminal['status'])
                self.assertEqual('replacement-property-v1',terminal['first_property_witness']['schema'])
                if stage!='calibration':self.assertEqual('verified',terminal['first_property_witness']['live_poststate'])
                self.assertLessEqual(len(json.dumps({key:terminal[key] for key in ('failure_witness','first_property_witness')}).encode()),2048)
                self.assertLessEqual(len(harness.stdout.getvalue().splitlines(keepends=True)[-1].encode()),4096)
                self.assertNotIn('PRIVATE',harness.stdout.getvalue())
            finally:harness.doCleanups()

    def test_full_receipt_cap_and_fixture_allocation_mutants_refuse_without_write(self):
        import compact_replacement_calibration as calibration
        from types import SimpleNamespace
        import time
        for key,value in (('FIXTURE_BYTES',73),('AGGREGATE_BYTES',1048503)):
            with self.subTest(key=key),tempfile.TemporaryDirectory() as tmp:
                session=SimpleNamespace(root=Path(tmp),deadline=time.monotonic()+30)
                with mock.patch.object(calibration,key,value),self.assertRaises(subject.q.Refused):subject.retain_native_receipt(session,b'{}')
                self.assertFalse(list(Path(tmp).iterdir()))
