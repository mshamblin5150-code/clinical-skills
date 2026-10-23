"""Inactive property route through public seams, synthetic namespace only."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import compact_native_controls as controls
import compact_replacement_property as subject
from test_compact_replacement_calibration import CalibrationNative
import test_compact_native_controls as fixtures

class PropertyNative(CalibrationNative):
    def __init__(self, held=5, live=5):
        super().__init__()
        self.held, self.live, self.deletes = held, live, []
        self.kernel.CreateFileW.call = self.denied_open
        self.kernel.DeleteFileW.call = self.denied_delete
    def _open(self, path, kind):
        self.last_error = 32
        return super()._open(path, kind)
    def denied_open(self, *args):
        self.last_error = 32
        return -1
    def denied_delete(self, *args):
        self.deletes.append(args)
        self.last_error = 32
        return 0
    def move(self, source, destination, flags):
        result = super().move(source, destination, flags)
        if not result:
            self.last_error = self.live if Path(destination).name.endswith('eligibility.json') else self.held
        return result

class PropertyTests(unittest.TestCase):
    def test_live5_requires_fresh_held5_and_exact_poststate_before_disposition(self):
        native = PropertyNative()
        runtime, factory, _ = fixtures.NativePacketControls().runtime(native)
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            row = subject.run_property_control(Path(tmp)/'invocation', runtime)
            self.assertEqual('replacement-property-v1', row['schema'])
            self.assertFalse(row['production_qualified'])
            self.assertEqual('disposition_verified', row['control']['retention'])
            self.assertEqual('verified', row['control']['replacement_poststate'])
            self.assertEqual(3, len(native.calls))
            self.assertEqual(1, len(native.deletes))
            self.assertEqual(1, len(factory.owners))
            self.assertEqual(2, sum(api.mark_count for api in runtime.apis))
            self.assertEqual([3, 2], [len(row) for row in native.mark_barriers])
            self.assertTrue(runtime.cleanup())

    def test_matching_error_matrix_refuses_other_before_live_owner(self):
        for held, live, success in ((5,5,True),(5,32,True),(32,32,True),(32,5,False),(999,32,False)):
            with self.subTest(held=held, live=live), tempfile.TemporaryDirectory() as tmp:
                native = PropertyNative(held, live)
                runtime, factory, _ = fixtures.NativePacketControls().runtime(native)
                with contextlib.redirect_stdout(io.StringIO()):
                    if success:
                        subject.run_property_control(Path(tmp)/'new', runtime)
                    else:
                        with self.assertRaises(Exception): subject.run_property_control(Path(tmp)/'new', runtime)
                self.assertEqual(0 if held == 999 else 1, len(factory.owners))
                self.assertEqual(1 if success else 0, len(native.deletes))
                self.assertEqual(2 if success else 0, len(native.mark_barriers))
                self.assertTrue(runtime.cleanup())

    def test_same_bytes_rebound_names_and_true_or_false_mutations_stop_before_delete(self):
        import os
        for name in ('source', 'destination'):
            for returned in (0, 1):
                with self.subTest(name=name, returned=returned), tempfile.TemporaryDirectory() as tmp:
                    class Changed(PropertyNative):
                        def move(self, source, destination, flags):
                            answer = super().move(source,destination,flags)
                            if Path(destination).name.endswith('eligibility.json'):
                                path = Path(source if name == 'source' else destination)
                                spare = path.parent/'same-bytes-mutant'
                                spare.write_bytes(path.read_bytes())
                                os.replace(spare,path)
                                return returned
                            return answer
                    native = Changed()
                    runtime, _, _ = fixtures.NativePacketControls().runtime(native)
                    with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(Exception):
                        subject.run_property_control(Path(tmp)/'new', runtime)
                    self.assertEqual([], native.deletes)
                    self.assertFalse(native.disposed)
                    self.assertTrue(runtime.cleanup())

    def test_public_projection_cannot_replace_private_calibration(self):
        from unittest import mock
        import compact_replacement_calibration as calibration
        native=PropertyNative()
        runtime, owners, _ = fixtures.NativePacketControls().runtime(native)
        forged={'status':'verified','cleanup':'verified','held_error':'access_5','namespace_transition':'verified'}
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(calibration,'_run_calibration',return_value=forged):
            with self.assertRaises(Exception): subject.run_property_control(Path(tmp)/'new',runtime)
        self.assertEqual([],owners.owners)
        self.assertFalse(native.disposed)
        self.assertTrue(runtime.cleanup())

class RouteTests(unittest.TestCase):
    def test_cli_selects_versioned_property_only_without_fallback(self):
        import json
        from unittest import mock
        import validate_compact_first_control as first
        import test_compact_first_control as fixtures
        workflow=(Path(first.__file__).parent.parent/'.github/workflows/ci-compact-first-control.yml').read_text()
        commands=[line.strip().split()[2:] for line in workflow.splitlines()
                  if line.strip().startswith('python ')]
        self.assertEqual(1,len(commands))
        for fail in (False,True):
            harness=fixtures.FinalizationControls()
            original_args=harness.harness()
            args=[original_args[1] if arg=='observer' else '1000'
                  if arg=='$env:PROOF_JOB_START_EPOCH' else arg for arg in commands[0]]
            try:
                def execute(session,runtime,observer,progress):
                    progress.update(property_verified=not fail, controls_verified=not fail, control_count=1)
                    if fail: raise controls.ControlError('control_proof_failed')
                with mock.patch.object(first,'execute_property',execute,create=True), \
                     mock.patch.object(first,'execute',side_effect=AssertionError('legacy fallback')), \
                     mock.patch.object(first,'execute_calibration',side_effect=AssertionError('calibration fallback')):
                    self.assertEqual(2 if fail else 0,first.main(args))
                row=json.loads(harness.stdout.getvalue().splitlines()[-1])
                self.assertEqual('compact_replacement_property_v1_summary',row['event'])
                self.assertFalse(row['production_qualified'])
                self.assertEqual('replacement-property-v1',row['property_route'])
            finally: harness.doCleanups()

class BindingTests(unittest.TestCase):
    def test_live_faults_cannot_reach_delete_or_native_disposition(self):
        from dataclasses import replace
        for fault in ('lifetime','source_bytes','source_missing','volume','close_unknown','call','getter','true','other'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as tmp:
                native=PropertyNative()
                runtime,_,_=fixtures.NativePacketControls().runtime(native)
                original=native.kernel.MoveFileExW.call
                def attack(source,destination,flags):
                    answer=original(source,destination,flags)
                    if Path(destination).name.endswith('eligibility.json'):
                        api=runtime.apis[-1]
                        if fault=='lifetime':
                            h=api.authority_handoff[0];api.lifetimes[h]+=1
                        if fault=='source_bytes':Path(source).write_bytes(b'X'*37)
                        if fault=='source_missing':Path(source).rename(Path(source).with_suffix('.retained'))
                        if fault=='close_unknown':api.close_uncertain=True
                        if fault=='call':raise OSError('PRIVATE_CALL')
                        if fault=='getter':native.c.get_last_error=lambda: (_ for _ in ()).throw(OSError('PRIVATE_GETTER'))
                        if fault=='true':return 1
                        if fault=='other':native.last_error=999
                    return answer
                native.kernel.MoveFileExW.call=attack
                original_record=native.record
                def record(handle):
                    row=original_record(handle)
                    if fault=='volume' and len(runtime.owners):return replace(row,st_dev=row.st_dev+1)
                    return row
                native.record=record
                with contextlib.redirect_stdout(io.StringIO()),self.assertRaises(Exception):
                    subject.run_property_control(Path(tmp)/'new',runtime)
                self.assertFalse(native.deletes)
                self.assertFalse(native.disposed)
                clean=runtime.cleanup()
                self.assertEqual(fault!='close_unknown',clean)

    def test_mandatory_proof_errors_never_suppressed_and_public_observation_not_authority(self):
        from unittest import mock
        import compact_replacement_poststate as proof
        original=proof.ReplacementPoststate.verify
        for live in (5,32):
            for fault in ('proof_error','missing_observation','malformed_observation'):
                with self.subTest(live=live,fault=fault),tempfile.TemporaryDirectory() as tmp:
                    native=PropertyNative(live=live)
                    runtime,_,_=fixtures.NativePacketControls().runtime(native)
                    def verify(check):
                        if check.destination.name.endswith('eligibility.json') and fault=='proof_error':
                            raise OSError('PRIVATE_PROOF')
                        original(check)
                        if check.destination.name.endswith('eligibility.json'):
                            check.observation.pop('replacement_poststate',None)
                            if fault=='malformed_observation':check.observation['replacement_poststate']={}
                    with mock.patch.object(proof.ReplacementPoststate,'verify',verify),contextlib.redirect_stdout(io.StringIO()):
                        if fault=='proof_error':
                            with self.assertRaises(Exception):subject.run_property_control(Path(tmp)/'new',runtime)
                        else:
                            row=subject.run_property_control(Path(tmp)/'new',runtime)
                            self.assertEqual('disposition_verified',row['control']['retention'])
                    self.assertEqual(0 if fault=='proof_error' else 1,len(native.deletes))
                    self.assertTrue(runtime.cleanup())

    def test_direct_open_and_delete_error32_safeguards_unchanged(self):
        for operation in ('open','delete'):
            with self.subTest(operation=operation),tempfile.TemporaryDirectory() as tmp:
                native=PropertyNative()
                if operation=='open':
                    def bad(*args):native.last_error=5;return -1
                    native.kernel.CreateFileW.call=bad
                else:
                    def bad(*args):native.last_error=5;return 0
                    native.kernel.DeleteFileW.call=bad
                runtime,_,_=fixtures.NativePacketControls().runtime(native)
                with contextlib.redirect_stdout(io.StringIO()),self.assertRaises(Exception):
                    subject.run_property_control(Path(tmp)/'new',runtime)
                self.assertFalse(native.disposed)
                self.assertTrue(runtime.cleanup())

    def test_calibration_history_and_reused_runtime_cannot_authorize_new_pair(self):
        from unittest import mock
        import compact_replacement_calibration as calibration
        with tempfile.TemporaryDirectory() as tmp:
            native=PropertyNative();runtime,owners,_=fixtures.NativePacketControls().runtime(native)
            old_api=controls.ObservedAPI(native)
            result=calibration._run_calibration(Path(tmp)/'historical',old_api,runtime.work_deadline,{})
            with mock.patch.object(calibration,'_run_calibration',return_value=result),self.assertRaises(Exception):
                subject.run_property_control(Path(tmp)/'new',runtime)
            self.assertFalse(owners.owners)
            self.assertTrue(runtime.cleanup())
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
            native=PropertyNative();runtime,owners,_=fixtures.NativePacketControls().runtime(native)
            subject.run_property_control(Path(tmp)/'one',runtime)
            with self.assertRaises(Exception):subject.run_property_control(Path(tmp)/'two',runtime)
            self.assertEqual(1,len(owners.owners));self.assertEqual(3,len(native.calls))
            self.assertTrue(runtime.cleanup())

    def test_writer_primary_exception_survives_uncertain_close(self):
        from unittest import mock
        primary=OSError('PRIVATE_PRIMARY');secondary=OSError('PRIVATE_SECONDARY')
        original_open=Path.open;original_lifecycle=controls._snapshot_share_success
        captured=[]
        class Broken:
            def __init__(self,stream):self.stream=stream
            def write(self,raw):raise primary
            def close(self):self.stream.close();raise secondary
        def open_file(path,*args,**kwargs):
            stream=original_open(path,*args,**kwargs)
            return Broken(stream) if path.name=='receipt-replacement.bin' else stream
        def lifecycle(pair,runtime,*,authority_check=None):
            def boundary(current):
                try:return authority_check(current)
                except BaseException as error:captured.append(error);raise
            return original_lifecycle(pair,runtime,authority_check=boundary)
        native=PropertyNative();runtime,_,_=fixtures.NativePacketControls().runtime(native)
        with tempfile.TemporaryDirectory() as tmp,mock.patch.object(Path,'open',open_file), \
             mock.patch.object(controls,'_snapshot_share_success',lifecycle),contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(Exception):subject.run_property_control(Path(tmp)/'new',runtime)
        self.assertIs(primary,captured[0])
        self.assertFalse(native.disposed)
        self.assertFalse(runtime.cleanup())

class AccountingTests(unittest.TestCase):
    def test_complete_accounting_matches_actual_cli_and_encoded_boundary(self):
        import json
        import os
        from unittest import mock
        from types import SimpleNamespace
        import validate_compact_first_control as first
        import test_compact_first_control as harnesses
        directory=Path(first.__file__).parent
        accounting=json.loads((directory/'compact-replacement-property-v1-accounting.json').read_text())
        baseline=json.loads((directory/'compact-first-control-accounting.json').read_text())
        budget=json.loads((directory/'compact-first-control-budget.json').read_text())
        harness=harnesses.FinalizationControls()
        original_args=harness.harness()
        workflow=(directory.parent/'.github/workflows/ci-compact-first-control.yml').read_text()
        commands=[line.strip().split()[2:] for line in workflow.splitlines()
                  if line.strip().startswith('python ')]
        self.assertEqual(1,len(commands))
        args=[original_args[1] if arg=='observer' else '1000'
              if arg=='$env:PROOF_JOB_START_EPOCH' else arg for arg in commands[0]]
        try:
            observer=Path(args[args.index('--observer')+1]);(observer/'diagnostics').mkdir()
            (observer/'diagnostics/compact-first-control-budget.json').write_text(json.dumps(first.BUDGET))
            session=harness.session
            session.root=observer.parent/'source-captures';session.root.mkdir()
            session.deadline=540;session.owners=[]
            def clean(*args,**kwargs):session.owners.extend([None]*3)
            def inventory(*args,**kwargs):session.owners.append(None);return {'synthetic':'inventory'}
            def verify(*args,**kwargs):session.owners.extend([None]*5)
            native=PropertyNative();sizes=[];original=native.move
            def measured(source,destination,flags):
                sizes.append(sum(p.stat().st_size for p in Path(source).parent.iterdir() if p.is_file())
                    if Path(destination).name=='target.bin' else Path(source).stat().st_size)
                return original(source,destination,flags)
            native.kernel.MoveFileExW.call=measured
            runtime,_,_=fixtures.NativePacketControls().runtime(native)
            runtime.work_deadline,runtime.hard_deadline=540,600;runtime.clock=lambda:0
            with mock.patch.object(first,'make_runtime',return_value=runtime), \
                 mock.patch.object(first.q,'first_clean',clean), \
                 mock.patch.object(first.q,'raw_source_inventory',inventory), \
                 mock.patch.object(first.q,'verify_sources',verify), \
                 mock.patch.object(first,'validate_core_pins'), \
                 mock.patch.object(first,'execute',side_effect=AssertionError('legacy forbidden')), \
                 mock.patch.object(first,'execute_calibration',side_effect=AssertionError('calibration-only forbidden')), \
                 mock.patch.dict(os.environ,{'GITHUB_SHA':'a'*40}):
                self.assertEqual(0,first.main(args),harness.stdout.getvalue())
            terminal=json.loads(harness.stdout.getvalue().splitlines()[-1])
            retained=json.loads((session.root/'replacement-property-v1-validation.json').read_bytes())
            self.assertEqual('replacement-property-v1',retained['schema'])
            self.assertEqual('disposition_verified',retained['property']['control']['retention'])
            self.assertFalse(retained['production_qualified'])
            self.assertEqual([74,74,37],sizes)
            self.assertLessEqual(len(harness.stdout.getvalue().splitlines(keepends=True)[-1].encode()),4096)
            self.assertNotIn('PRIVATE',harness.stdout.getvalue())
            receipt_root=observer.parent/'max-receipt';receipt_root.mkdir()
            maximum=1024*1024-max(sizes[:2])
            raw=b'{"p":"'+b'x'*(maximum-8)+b'"}'
            receipt_session=SimpleNamespace(root=receipt_root,deadline=540)
            receipt=first.retain_property_receipt(receipt_session,raw)
            self.assertEqual(raw,(receipt_root/'replacement-property-v1-validation.json').read_bytes())
            with self.assertRaises(first.q.Refused):first.retain_property_receipt(receipt_session,raw+b' ')
            work,hard=first.budget_deadlines(1000,1000,0)
            pairs=budget['max_source_commands']+len(runtime.owners)
            private=baseline['private_content_bytes']+max(sizes[:2])+receipt['receipt_bytes']-1024*1024
            self.assertEqual({
                'aggregate_receipt_max_bytes':receipt['receipt_bytes'],
                'calibration_fixture_max_bytes':max(sizes[:2]),
                'live_replacement_source_bytes':sizes[-1],
                'native_owned_commands':len(runtime.owners),
                'nested_reserved_slots':runtime.nested_command_slots,
                'capture_disposition_calls':len(native.mark_barriers),
                'replacement_attempts':len(native.calls),
                'success_capture_pairs':terminal['source_commands']+len(runtime.owners),
                'source_success_commands':terminal['source_commands'],
                'conservative_capture_pairs_ceiling':pairs,
                'conservative_streams_ceiling':pairs*2,
                'private_content_bytes_ceiling':private,
                'including_public_content_bytes_ceiling':private+first.reader.BUDGET['max_receipt_bytes'],
                'work_seconds':work,'cleanup_seconds':hard-work,'total_job_seconds':hard,
            },accounting)
        finally:harness.doCleanups()

    def test_every_accounting_field_mutation_is_rejected(self):
        import json
        from unittest import mock
        path=Path(subject.__file__).with_name('compact-replacement-property-v1-accounting.json')
        original=Path.read_text;values=json.loads(original(path))
        for field in values:
            def altered(target,*args,**kwargs):
                text=original(target,*args,**kwargs)
                if target==path:
                    row=json.loads(text);row[field]=999;return json.dumps(row)
                return text
            with self.subTest(field=field),mock.patch.object(Path,'read_text',altered),self.assertRaises(AssertionError):
                self.test_complete_accounting_matches_actual_cli_and_encoded_boundary()

class PublicTests(unittest.TestCase):
    def test_property_projection_is_finite_detached_and_not_authority(self):
        import json
        from types import SimpleNamespace
        for state in ({},{'calibration_witness':{'held_error':'PRIVATE_PATH_ID_BYTES'}},None):
            row=subject.property_witness(SimpleNamespace(property_observation=state,control_observation=None))
            self.assertLessEqual(len(json.dumps(row).encode()),2048)
            self.assertNotIn('PRIVATE',json.dumps(row))
            self.assertFalse(row['production_qualified'])
            self.assertEqual('replacement-property-v1',row['schema'])

class ClosureAndBudgetTests(unittest.TestCase):
    def test_mandatory_proof_primary_survives_observer_close_failure_for_both_codes(self):
        from unittest import mock
        original_lifecycle=controls._snapshot_share_success
        for live in (5,32):
            primary=OSError('PRIVATE_PROOF_PRIMARY');captured=[]
            class Changed(PropertyNative):
                def record(self,handle):
                    row=self.handles.get(handle)
                    if len(self.calls)==3 and row and row['path'].name=='receipt-replacement.bin':
                        raise primary
                    return super().record(handle)
                def close(self,handle):
                    path=self.handles[handle]['path']
                    super().close(handle)
                    if len(self.calls)==3 and path.name=='receipt-replacement.bin':
                        raise OSError('PRIVATE_CLOSE_SECONDARY')
            def lifecycle(pair,runtime,*,authority_check=None):
                def boundary(current):
                    try:return authority_check(current)
                    except BaseException as error:captured.append(error);raise
                return original_lifecycle(pair,runtime,authority_check=boundary)
            native=Changed(live=live);runtime,_,_=fixtures.NativePacketControls().runtime(native)
            with self.subTest(live=live),tempfile.TemporaryDirectory() as tmp,mock.patch.object(controls,'_snapshot_share_success',lifecycle),contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(Exception):subject.run_property_control(Path(tmp)/'new',runtime)
            self.assertIs(primary,captured[0])
            self.assertFalse(native.disposed);self.assertFalse(native.deletes)
            self.assertFalse(runtime.cleanup())

    def test_shared_invocation_parent_rebind_after_calibration_refuses_before_owner(self):
        from unittest import mock
        import compact_replacement_calibration as calibration
        original=calibration._run_calibration
        def rebound(root,*args,**kwargs):
            result=original(root,*args,**kwargs)
            parent=root.parent
            parent.rename(parent.with_name('retained-original-parent'))
            parent.mkdir()
            return result
        native=PropertyNative();runtime,owners,_=fixtures.NativePacketControls().runtime(native)
        with tempfile.TemporaryDirectory() as tmp,mock.patch.object(calibration,'_run_calibration',rebound),contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(Exception):subject.run_property_control(Path(tmp)/'new',runtime)
        self.assertFalse(owners.owners)
        self.assertEqual(2,len(native.calls))
        self.assertTrue(runtime.cleanup())

    def test_observer_close_uncertainty_stops_at_exact_challenge_boundary(self):
        for when in ('calibration','live_preflight','live_poststate'):
            with self.subTest(when=when),tempfile.TemporaryDirectory() as tmp:
                class Changed(PropertyNative):
                    def close(self,handle):
                        path=self.handles[handle]['path']
                        fault=(when=='calibration' and path.name=='source.bin' or
                            when=='live_preflight' and path.name=='receipt-replacement.bin' or
                            when=='live_poststate' and path.name=='receipt-replacement.bin' and len(self.calls)==3)
                        super().close(handle)
                        if fault:raise OSError('PRIVATE_CLOSE_UNCERTAIN')
                native=Changed();runtime,owners,_=fixtures.NativePacketControls().runtime(native)
                with contextlib.redirect_stdout(io.StringIO()),self.assertRaises(Exception):
                    subject.run_property_control(Path(tmp)/'new',runtime)
                self.assertEqual({'calibration':0,'live_preflight':2,'live_poststate':3}[when],len(native.calls))
                self.assertEqual(0 if when=='calibration' else 1,len(owners.owners))
                self.assertFalse(native.deletes);self.assertFalse(native.disposed)
                self.assertFalse(runtime.cleanup())

    def test_route_receipt_cap_mutations_fail_before_writing(self):
        from unittest import mock
        from types import SimpleNamespace
        import time
        import compact_replacement_calibration as calibration
        import validate_compact_first_control as first
        for name,value in (('FIXTURE_BYTES',73),('AGGREGATE_BYTES',1048503)):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
                session=SimpleNamespace(root=Path(tmp),deadline=time.monotonic()+30)
                with mock.patch.object(calibration,name,value),self.assertRaises(first.q.Refused):
                    first.retain_property_receipt(session,b'{}')
                self.assertEqual([],list(Path(tmp).iterdir()))

    def test_calibration_does_not_reset_or_extend_deadline(self):
        import time
        native=PropertyNative();runtime,owners,_=fixtures.NativePacketControls().runtime(native)
        runtime.work_deadline=0
        with tempfile.TemporaryDirectory() as tmp,self.assertRaises(Exception):
            subject.run_property_control(Path(tmp)/'new',runtime)
        self.assertEqual([],native.calls);self.assertFalse(owners.owners)
        self.assertEqual(0,runtime.work_deadline)
        self.assertTrue(runtime.cleanup())
