"""Disposable held/released replacement comparison, never live qualification.

Exactly two same-path attempts; only this fixture's authority is released.
Evidence is sampled, not an ACL theorem, continuous-presence or erasure claim.
"""
import errno
import os
import time
from dataclasses import dataclass, fields

import compact_capture_retention as retention
import compact_replacement_poststate as poststate
import generated_output_contract as contract

TARGET_BYTES = b'synthetic original must remain here!\n'
SOURCE_BYTES = poststate.REPLACEMENT_BYTES
FIXTURE_BYTES = len(TARGET_BYTES) + len(SOURCE_BYTES)
AGGREGATE_BYTES = 1024 * 1024 - FIXTURE_BYTES


class CalibrationRefused(RuntimeError):
    def __init__(self):
        super().__init__('replacement_calibration_inconclusive')


def need(value):
    if not value:
        raise CalibrationRefused()


def sampled_missing(path):
    """Fresh non-following namespace sample, not a persistent absence claim."""
    try:
        path.lstat()
    except FileNotFoundError as error:
        need(error.errno == errno.ENOENT)
        return True
    return False


def calibration_witness(state):
    """Finite detached projection only; absent or malformed evidence is unknown."""
    states = {'not_attempted', 'prepared', 'held_refused', 'released', 'verified', 'failed'}
    calls = {'not_attempted', 'entered', 'returned_false', 'returned_true', 'call_raised', 'error_read_raised'}
    errors = {'sharing_32', 'access_5', 'other'}
    source = state if type(state) is dict else {}
    row = {'schema': 'replacement-calibration-v1', 'calibration_only': True,
           'native_control_qualified': False, 'status': None,
           'held_call': None, 'held_error': None, 'released_call': None,
           'released_error': None, 'held_poststate': None,
           'namespace_transition': None, 'cleanup': None}
    for name, allowed in (('status', states), ('held_poststate', {'verified', 'unknown'}),
                          ('namespace_transition', {'verified', 'unknown'}),
                          ('cleanup', {'verified', 'unknown'})):
        value = source.get(name)
        if type(value) is str and value in allowed:
            row[name] = value
    for leg in ('held', 'released'):
        call, error = source.get(leg+'_call'), source.get(leg+'_error')
        if (type(call) is str and call in calls and leg+'_error' in source
                and ((call == 'returned_false' and type(error) is str and error in errors)
                     or (call != 'returned_false' and error is None))):
            row[leg+'_call'], row[leg+'_error'] = call, error
    if row['held_poststate'] == 'verified' and row['held_call'] != 'returned_false':
        row['held_poststate'] = None
    if row['namespace_transition'] == 'verified' and not (
            row['held_poststate'] == 'verified' and row['released_call'] == 'returned_true'):
        row['namespace_transition'] = None
    if row['status'] == 'verified' and not (
            row['namespace_transition'] == 'verified' and row['cleanup'] == 'verified'):
        row['status'] = None
    return row


@dataclass(frozen=True)
class _CalibrationSuccess:
    api: object
    root: object
    deadline: float
    held_error: int
    volume: int
    witness: dict


def run_calibration(root, api, deadline, observation, *, move=None, get_error=None,
                    missing=sampled_missing, directory=retention._directory):
    return _run_calibration(root, api, deadline, observation, move=move,
        get_error=get_error, missing=missing, directory=directory).witness


def _run_calibration(root, api, deadline, observation, *, move=None, get_error=None,
                    missing=sampled_missing, directory=retention._directory):
    """Public injected seam. Native defaults retain READ/shareREAD and flags1.

    root must not exist. Existing/historical files are never reused or removed.
    Unknown close prevents further challenge/read work; cleanup may close other
    still-owned handles once. A failed close is never retried.
    """
    state = {'status': 'not_attempted', 'held_call': 'not_attempted', 'held_error': None,
             'released_call': 'not_attempted', 'released_error': None,
             'held_poststate': 'unknown', 'namespace_transition': 'unknown', 'cleanup': 'unknown'}
    authority = None
    held_error = None
    primary = None
    target, source = root/'target.bin', root/'source.bin'

    def publish():
        try:
            if isinstance(observation, dict):
                dict.pop(observation, 'calibration_witness', None)
                observation['calibration_witness'] = calibration_witness(state)
        except BaseException:
            if isinstance(observation, dict):
                dict.pop(observation, 'calibration_witness', None)

    def check():
        need(time.monotonic() < deadline and not api.close_uncertain)

    def ledger(expected):
        check()
        need(api.handles == expected)

    def close(handle):
        try:
            api.close(handle)
            need(handle not in api.handles)
        except BaseException:
            api.close_uncertain = True
            raise

    def sample(handle):
        check()
        before = contract.windows_snapshot(api, handle, 37, 'replacement-calibration', deadline)
        raw = api.read(handle, 37, deadline)
        after = contract.windows_snapshot(api, handle, 37, 'replacement-calibration', deadline)
        need(before == after and type(raw) is bytes and len(raw) == 37)
        retention._native_snapshot(before, len(raw))
        need(not before.st_file_attributes & (1 | 2 | 4 | 0x100))
        check()
        return before, raw

    def path_sample(path):
        check()
        handle = api.open(path)
        fault = None
        try:
            return sample(handle)
        except BaseException as error:
            fault = error
            raise
        finally:
            try:
                close(handle)
            except BaseException:
                if fault is None:
                    raise

    def write(path, raw):
        check()
        stream = path.open('x+b')
        fault = None
        try:
            need(stream.write(raw) == 37)
            stream.flush()
            os.fsync(stream.fileno())
            snapshot = contract.windows_snapshot(api, api.from_fd(stream.fileno()),
                37, 'replacement-calibration-writer', deadline)
            retention._native_snapshot(snapshot, 37)
            return snapshot
        except BaseException as error:
            fault = error
            raise
        finally:
            try:
                stream.close()
                need(stream.closed is True)
            except BaseException:
                api.close_uncertain = True
                if fault is None:
                    raise

    def same_metadata(before, after, allowed=()):
        return all(getattr(before, item.name) == getattr(after, item.name)
                   for item in fields(contract.WindowsSnapshot) if item.name not in allowed)

    def attempt(leg):
        nonlocal held_error
        check()
        state.update({leg+'_call': 'entered', leg+'_error': None})
        publish()
        try:
            returned_false = not move(str(source), str(target), 1)
        except BaseException:
            state[leg+'_call'] = 'call_raised'
            raise
        error = None
        if returned_false:
            try:
                error = get_error()
            except BaseException:
                state[leg+'_call'] = 'error_read_raised'
                raise
        if leg == 'held':
            held_error = error
        state.update({leg+'_call': 'returned_false' if returned_false else 'returned_true',
                      leg+'_error': ('sharing_32' if error == 32 else 'access_5' if error == 5 else 'other')
                      if returned_false else None})
        publish()
        return returned_false

    publish()
    try:
        ledger({})
        need(root.is_absolute() and '..' not in root.parts)
        root.mkdir()  # Never reuse a prior fixture, even if it appears empty.
        chain = directory(root)
        target_writer = write(target, TARGET_BYTES)
        source_writer = write(source, SOURCE_BYTES)
        check()
        authority = api.open(target)
        lifetime = api.lifetimes[authority]
        original = sample(authority)
        replacement = path_sample(source)
        need(same_metadata(target_writer, original[0], ('st_mtime_ns', 'st_ctime_ns'))
             and same_metadata(source_writer, replacement[0], ('st_mtime_ns', 'st_ctime_ns'))
             and original[1] == TARGET_BYTES and replacement[1] == SOURCE_BYTES)
        need(directory(root) == chain)
        proof = poststate.ReplacementPoststate(api, authority, target, source,
            baseline=original, deadline=deadline, observation={}, directory=directory)
        proof.prepare()
        need(api.lifetimes.get(authority) == lifetime)
        ledger({authority: target})
        if move is None:
            import ctypes as c
            move = api.native.kernel.MoveFileExW
            move.argtypes, move.restype = (c.c_wchar_p, c.c_wchar_p, c.c_uint32), c.c_int
        if get_error is None:
            get_error = api.native.c.get_last_error
        state['status'] = 'prepared'
        need(attempt('held'))
        proof.verify()
        need(directory(root) == chain and api.lifetimes.get(authority) == lifetime)
        ledger({authority: target})
        state.update(status='held_refused', held_poststate='verified')
        publish()
        released, authority = authority, None  # No retry even if close is uncertain.
        close(released)
        ledger({})
        need(path_sample(target) == original and path_sample(source) == replacement)
        need(directory(root) == chain)
        ledger({})
        state['status'] = 'released'
        need(not attempt('released'))
        need(directory(root) == chain)
        destination = path_sample(target)
        # Only positive rename ChangeTime may transition. All other native
        # identity/metadata and exact bytes are compared, not just BOOL/content.
        need(same_metadata(replacement[0], destination[0], ('st_ctime_ns',))
             and destination[1] == SOURCE_BYTES)
        check()
        need(missing(source) is True)
        need(directory(root) == chain)
        ledger({})
        state.update(status='verified', namespace_transition='verified')
    except BaseException as error:
        primary = error
        state['status'] = 'failed'
        raise
    finally:
        if authority is not None:
            closing, authority = authority, None
            try:
                close(closing)
            except BaseException:
                state['status'] = 'failed'
                if primary is None:
                    publish()
                    raise
        state['cleanup'] = 'verified' if not api.handles and not api.close_uncertain else 'unknown'
        publish()
    return _CalibrationSuccess(api, root, deadline, held_error, original[0].st_dev, calibration_witness(state))
