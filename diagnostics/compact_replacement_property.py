"""Inactive opt-in sampled property v1, not production qualification.

Numerically broader than strict32: false5 additionally needs this invocation's
held5 calibration. No public/historical observation is an authorization input.
"""
import ctypes as c
import os

import compact_native_controls as native
import compact_capture_retention as retention
import compact_replacement_calibration as calibration
import compact_replacement_poststate as poststate


def property_witness(runtime):
    """Finite detached observation only. Never consumed by the property predicate."""
    observed = getattr(runtime, 'property_observation', None)
    source = observed if type(observed) is dict else {}
    live = native.failure_witness(runtime) or {}
    return {'schema': 'replacement-property-v1', 'production_qualified': False,
        'calibration': calibration.calibration_witness(source.get('calibration_witness')),
        'live_call': live.get('replacement_call'), 'live_error': live.get('replacement_error'),
        'live_poststate': live.get('replacement_poststate')}


def run_property_control(root, runtime):
    """Own fresh calibration and one first-control pair in a single invocation.

    Local binding prevents accidental reuse, not malicious in-process Python.
    Calibration matches API policy/volume, not ACL/filter equivalence or cause.
    """
    native.require(not runtime.owners and not runtime.apis and runtime.nested_command_slots == 0)
    runtime.check_time()
    runtime.resource_check()
    root.mkdir()
    parent_chain = retention._directory(root)
    api = runtime.api()
    deadline = runtime.work_deadline
    progress = {}
    runtime.property_observation = progress
    result = calibration._run_calibration(root/'calibration', api, deadline, progress)
    native.require(type(result) is calibration._CalibrationSuccess and result.api is api
        and result.root == root/'calibration' and result.deadline == deadline
        and type(result.held_error) is int and result.held_error in (5, 32)
        and not api.handles and not api.close_uncertain
        and retention._directory(root) == parent_chain)
    runtime.check_time()
    runtime.resource_check()
    native.require(runtime.work_deadline == deadline and not runtime.owners)
    runtime.control_observation = {'control': 'snapshot_share_receipt_success', 'phase': 'prepare',
        'authority_phase': 'not_attempted', 'outcome_state': 'not_returned',
        'replacement_call': 'not_returned', 'replacement_error': None,
        'outcome': None, 'reconstruction': 'not_attempted'}
    pair = native.prepare_pair(root/'first-control', runtime)
    consumed = False

    def authority_check(current):
        nonlocal consumed
        native.require(not consumed and current is pair and current.runtime is runtime
            and runtime.work_deadline == deadline and result.api is api
            and not api.handles and not api.close_uncertain
            and retention._directory(root) == parent_chain)
        consumed = True
        handles = [(h, p) for h, p in pair.api.handles.items() if p.name.endswith('-eligibility.json')]
        native.require(len(handles) == 1)
        handle, path = handles[0]
        bound = pair.api.authority_handoff
        native.require(bound is not None and bound[0] == handle
            and pair.api.lifetimes.get(handle) == bound[1] and bound[2].st_dev == result.volume)
        lifetime = bound[1]
        kernel, ffi = pair.api.native.kernel, pair.api.native.c
        denials = []
        for label, access in (('write', 0x40000000), ('delete_open', 0x00010000)):
            runtime.control_observation['authority_phase'] = label
            opened = kernel.CreateFileW(str(path), access, 1, None, 3, 0x08200000, None)
            if opened not in (None, ffi.c_void_p(-1).value):
                pair.api.handles[opened] = path
                try:
                    pair.api.close(opened)
                finally:
                    raise native.ControlError('control_native_sharing_unexpected')
            native.require(ffi.get_last_error() == 32, 'control_native_sharing_unexpected')
            denials.append(label)
        source = pair.root/'receipt-replacement.bin'
        stream = source.open('xb')
        primary = None
        try:
            native.require(stream.write(poststate.REPLACEMENT_BYTES) == 37)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException as error:
            primary = error
            raise
        finally:
            try:
                stream.close()
                native.require(stream.closed is True)
            except BaseException:
                pair.api.close_uncertain = True
                if primary is None:
                    raise
        proof = poststate.ReplacementPoststate(pair.api, handle, path, source,
            baseline=bound[2:], deadline=deadline, observation=runtime.control_observation)
        proof.prepare()
        move = kernel.MoveFileExW
        move.argtypes, move.restype = (c.c_wchar_p, c.c_wchar_p, c.c_uint32), c.c_int
        runtime.control_observation['authority_phase'] = 'replace'
        native._replacement_observation(runtime, 'entered')
        try:
            returned_false = not move(str(source), str(path), 1)
        except BaseException:
            native._replacement_observation(runtime, 'call_raised')
            raise
        error = None
        if returned_false:
            try:
                error = ffi.get_last_error()
            except BaseException:
                native._replacement_observation(runtime, 'error_read_raised')
                raise
        native._replacement_observation(runtime, 'returned_false' if returned_false else 'returned_true',
            ('access_5' if error == 5 else 'sharing_32' if error == 32 else 'other') if returned_false else None)
        native.require(returned_false and type(error) is int and error in (5, 32)
            and (error != 5 or result.held_error == 5), 'control_native_sharing_unexpected')
        proof.verify()  # Mandatory: no supplemental suppression or projected-status acceptance.
        native.require(pair.api.lifetimes.get(handle) == lifetime and not pair.api.close_uncertain
            and retention._directory(root) == parent_chain)
        denials.append('replace')
        delete = kernel.DeleteFileW
        delete.argtypes, delete.restype = (c.c_wchar_p,), c.c_int
        runtime.control_observation['authority_phase'] = 'delete'
        native.require(not delete(str(path)) and ffi.get_last_error() == 32,
                       'control_native_sharing_unexpected')
        denials.append('delete')
        runtime.control_observation['authority_phase'] = 'readback'
        native.require(pair.api.read(handle, native.MAX_RECEIPT_BYTES, deadline))
        return denials

    control = native._snapshot_share_success(pair, runtime, authority_check=authority_check)
    native.require(consumed and len(runtime.owners) == 1 and runtime.nested_command_slots == 0
        and not any(item.handles or item.close_uncertain for item in runtime.apis))
    runtime.check_time()
    return {'schema': 'replacement-property-v1', 'production_qualified': False,
            'calibration': result.witness, 'control': control}
