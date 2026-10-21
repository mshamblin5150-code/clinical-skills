"""Finite generated-output contract; never substitutes for raw source verification."""
from dataclasses import dataclass
from datetime import date
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import time

import measure_lazy_suite_ids as q
from full_suite_receipts import allowed_retained

MARKER_DIR = 'scratch/runs/tracker-publish-hook'
WEIGHTS = 'scratch/runs/suite-weights.json'
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_ENTRIES = 10000
MAX_DISCREPANCIES = 128


@dataclass(frozen=True)
class State:
    marker: str = 'absent'
    weights: str = 'absent'
    units: tuple[str, ...] = ()
    job_start_epoch: float = 0.0
    observed_epoch: float = 0.0
    max_job_seconds: int = 600
    sessions: str = 'optional'


def refuse(reason, relative=None):
    q.emit('generated_output_rejected', reason=reason,
           path_token=q.digest(relative.encode('utf-8', errors='surrogatepass')) if relative is not None else None)
    raise q.Refused(reason)


def need(condition, reason, relative=None):
    if not condition:
        refuse(reason, relative)


def validate_state(state):
    need(type(state) is State and state.marker in ('absent', 'required')
         and state.weights in ('absent', 'required') and state.sessions in ('optional', 'required'),
         'generated_state_invalid')
    need(type(state.max_job_seconds) is int and state.max_job_seconds in (600, 5400), 'generated_state_invalid')
    need(all(type(value) in (int, float) and math.isfinite(value) for value in (state.job_start_epoch, state.observed_epoch)),
         'generated_date_interval_invalid')
    need(0 <= state.job_start_epoch <= state.observed_epoch
         and state.observed_epoch - state.job_start_epoch <= state.max_job_seconds, 'generated_date_interval_invalid')
    try:
        first, last = date.fromtimestamp(state.job_start_epoch), date.fromtimestamp(state.observed_epoch)
    except (ValueError, OverflowError, OSError):
        refuse('generated_date_interval_invalid')
    need(0 <= (last-first).days <= 1, 'generated_date_interval_invalid')
    need(type(state.units) is tuple and len(state.units) <= MAX_ENTRIES
         and all(type(unit) is str and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*){1,16}', unit)
                 and len(unit) <= 512 for unit in state.units), 'generated_units_invalid')
    need(len(set(state.units)) == len(state.units), 'generated_units_invalid')
    need(state.weights != 'required' or bool(state.units), 'generated_units_invalid')
    return first, last


def marker_relative(repo):
    identity = hashlib.sha256(os.path.normcase(str(repo)).encode('utf-8')).hexdigest()
    return MARKER_DIR + '/' + identity + '.json'


def _safe_directory(path, relative=None):
    try:
        metadata = path.lstat()
    except OSError:
        refuse('generated_directory_unread', relative)
    need(stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
         and not (getattr(metadata, 'st_file_attributes', 0) & 0x400), 'generated_directory_unsafe', relative)
    return metadata


def _metadata_key(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_nlink,
            metadata.st_size, metadata.st_mtime_ns, metadata.st_ctime_ns,
            getattr(metadata, 'st_file_attributes', 0))


def _regular(metadata, limit, relative):
    need(stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
         and metadata.st_nlink == 1 and not (getattr(metadata, 'st_file_attributes', 0) & 0x400),
         'generated_file_unsafe', relative)
    need(0 <= metadata.st_size <= limit, 'generated_file_oversize', relative)


def _open_readonly(path):
    if os.name != 'nt':
        need(hasattr(os, 'O_NOFOLLOW'), 'generated_nofollow_unavailable')
        return os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    import ctypes
    from ctypes import wintypes
    import msvcrt
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                   wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL
    class Attributes(ctypes.Structure):
        _fields_ = [('attributes', wintypes.DWORD), ('tag', wintypes.DWORD)]
    kernel.GetFileInformationByHandleEx.argtypes = (wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD)
    kernel.GetFileInformationByHandleEx.restype = wintypes.BOOL
    handle = kernel.CreateFileW(str(path), 0x80000000, 1, None, 3, 0x00200000 | 0x08000000, None)
    need(handle != ctypes.c_void_p(-1).value, 'generated_file_unread')
    try:
        attributes = Attributes()
        need(kernel.GetFileInformationByHandleEx(handle, 9, ctypes.byref(attributes), ctypes.sizeof(attributes)),
             'generated_handle_metadata_unread')
        need(not attributes.attributes & 0x400, 'generated_file_unsafe')
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except BaseException:
        kernel.CloseHandle(handle)
        raise
    return fd  # ownership transferred to the Python file descriptor


def safe_read(repo, relative, limit, deadline):
    need(isinstance(repo, Path) and repo.is_absolute() and repo.resolve() == repo, 'generated_root_invalid')
    for ancestor in (repo, *repo.parents):
        _safe_directory(ancestor)
    need(type(relative) is str and relative and '\\' not in relative and ':' not in relative
         and not Path(relative).is_absolute() and Path(relative).as_posix() == relative
         and not any(part in ('.', '..') for part in Path(relative).parts), 'generated_relative_path_invalid')
    path = repo / relative
    need(time.monotonic() < deadline, 'global_budget_exhausted')
    ancestors = {}
    for ancestor in (path.parent, *path.parent.parents):
        metadata = _safe_directory(ancestor, relative)
        ancestors[ancestor] = (metadata.st_dev, metadata.st_ino)
        if ancestor == repo:
            break
    try:
        before = path.lstat()
        _regular(before, limit, relative)
        fd = _open_readonly(path)
        with os.fdopen(fd, 'rb') as stream:
            opened = os.fstat(stream.fileno())
            _regular(opened, limit, relative)
            need(_metadata_key(before) == _metadata_key(opened), 'generated_file_identity_changed', relative)
            raw = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
        final = path.lstat()
    except OSError:
        refuse('generated_file_unread', relative)
    need(len(raw) <= limit, 'generated_file_oversize', relative)
    need(_metadata_key(before) == _metadata_key(after) == _metadata_key(final)
         and len(raw) == before.st_size, 'generated_file_identity_changed', relative)
    for ancestor, identity in ancestors.items():
        metadata = _safe_directory(ancestor, relative)
        need(identity == (metadata.st_dev, metadata.st_ino), 'generated_directory_identity_changed', relative)
    need(time.monotonic() < deadline, 'global_budget_exhausted')
    return raw


def _json(raw, relative):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'generated_json_duplicate_key', relative)
            result[key] = value
        return result
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
    except (ValueError, UnicodeError, RecursionError):
        refuse('generated_json_invalid', relative)


def validate_marker(raw, state, relative):
    first, last = validate_state(state)
    row = _json(raw, relative)
    need(type(row) is dict and set(row) == {'version', 'ran_on'} and type(row['version']) is int
         and row['version'] == 2 and type(row['ran_on']) is str, 'generated_marker_schema_invalid', relative)
    try:
        ran_on = date.fromisoformat(row['ran_on'])
    except ValueError:
        refuse('generated_marker_date_invalid', relative)
    need(row['ran_on'] == ran_on.isoformat() and first <= ran_on <= last, 'generated_marker_date_invalid', relative)
    expected = (json.dumps(row, sort_keys=True) + '\n').replace('\n', os.linesep).encode('utf-8')
    need(raw == expected, 'generated_marker_bytes_invalid', relative)


def validate_weights(raw, state, relative=WEIGHTS):
    validate_state(state)
    row = _json(raw, relative)
    need(type(row) is dict and set(row) == set(state.units), 'generated_weights_units_invalid', relative)
    need(all(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= state.max_job_seconds
             for value in row.values()), 'generated_weights_values_invalid', relative)
    expected = (json.dumps(dict(sorted(row.items())), indent=2) + '\n').replace('\n', os.linesep).encode('utf-8')
    need(raw == expected, 'generated_weights_bytes_invalid', relative)


def scan(repo, target, deadline, state):
    """Collect bounded safe discrepancies without opening unknown payloads."""
    validate_state(state)
    need(isinstance(repo, Path) and repo.is_absolute() and repo.resolve() == repo, 'generated_root_invalid')
    for ancestor in (repo, *repo.parents):
        _safe_directory(ancestor)
    marker = marker_relative(repo)
    allowed_dirs = {'.', 'scratch', 'scratch/runs', 'scratch/sessions'}
    if state.marker == 'required':
        allowed_dirs.add(MARKER_DIR)
    for name in target:
        allowed_dirs.update(parent.as_posix() for parent in Path(name).parents)
    cache_parents = {Path(name).parent.as_posix() for name in target if name.endswith('.py')}
    extras, counts, seen_dirs, entry_count = {}, {'bytecode': 0, 'marker': 0, 'weights': 0}, set(), 0
    discrepancies, watched, collection_complete = [], {}, False
    def record(category, relative):
        need(len(discrepancies) < MAX_DISCREPANCIES, 'generated_discrepancy_limit')
        discrepancies.append({'category': category, 'path_token': q.digest(relative.encode('utf-8', errors='surrogatepass'))})
    def unread(error):
        refuse('generated_directory_unread')
    try:
        for directory, dirs, files in os.walk(repo, followlinks=False, onerror=unread):
            need(time.monotonic() < deadline, 'global_budget_exhausted')
            relative_dir = Path(directory).relative_to(repo).as_posix()
            seen_dirs.add(relative_dir)
            metadata = _safe_directory(Path(directory), relative_dir)
            key = _metadata_key(metadata)
            need(relative_dir not in watched or watched[relative_dir] == key, 'generated_directory_identity_changed', relative_dir)
            watched[relative_dir] = key
            if relative_dir == '.':
                if '.git' in dirs:
                    _safe_directory(repo / '.git', '.git')
                dirs[:] = [name for name in dirs if name != '.git']
            if relative_dir == 'scratch/sessions' and (dirs or files):
                record('sessions_not_empty', relative_dir)
            for name in dirs:
                relative = (Path(directory) / name).relative_to(repo).as_posix()
                metadata = _safe_directory(repo / relative, relative)
                watched[relative] = _metadata_key(metadata)
                cache = name == '__pycache__' and relative_dir in cache_parents
                if relative not in allowed_dirs and not cache:
                    record('unknown_directory', relative)
            for name in files:
                relative = (Path(directory) / name).relative_to(repo).as_posix()
                entry_count += 1
                need(entry_count <= MAX_ENTRIES, 'generated_entry_limit')
                if relative in target:
                    continue
                if relative == marker and state.marker == 'required':
                    kind, limit = 'marker', 128
                elif relative == WEIGHTS and state.weights == 'required':
                    kind, limit = 'weights', MAX_FILE_BYTES
                elif relative != WEIGHTS and allowed_retained(relative, target):
                    kind, limit = 'bytecode', MAX_FILE_BYTES
                else:
                    # Metadata only. Never read or hash an unrecognized payload.
                    try:
                        metadata = (repo / relative).lstat()
                    except OSError:
                        refuse('generated_file_unread', relative)
                    _regular(metadata, MAX_FILE_BYTES, relative)
                    watched[relative] = _metadata_key(metadata)
                    record('unknown_file', relative)
                    continue
                raw = safe_read(repo, relative, limit, deadline)
                if kind == 'marker':
                    validate_marker(raw, state, relative)
                elif kind == 'weights':
                    validate_weights(raw, state)
                counts[kind] += 1
                extras[relative] = q.digest(raw)
            entry_count += len(dirs)
            need(entry_count <= MAX_ENTRIES, 'generated_entry_limit')
        # A safe unknown entry is not stable evidence until the bounded walk ends.
        for relative, before in watched.items():
            need(time.monotonic() < deadline, 'global_budget_exhausted')
            try:
                metadata = (repo / relative).lstat()
            except OSError:
                refuse('generated_metadata_unread', relative)
            need(_metadata_key(metadata) == before, 'generated_entry_identity_changed', relative)
        if state.marker == 'required' and counts['marker'] != 1:
            record('marker_missing', marker)
        if state.weights == 'required' and counts['weights'] != 1:
            record('weights_missing', WEIGHTS)
        if state.sessions == 'required' and 'scratch/sessions' not in seen_dirs:
            record('sessions_missing', 'scratch/sessions')
        need(time.monotonic() < deadline, 'global_budget_exhausted')
        collection_complete = True
    finally:
        if discrepancies:
            category_counts = {category: sum(row['category'] == category for row in discrepancies)
                               for category in sorted({row['category'] for row in discrepancies})}
            q.emit('generated_output_discrepancies', count=len(discrepancies), category_counts=category_counts,
                   entries=discrepancies, collection_complete=collection_complete,
                   unknown_payloads_read=False, overall_admitted=False)
    need(not discrepancies, 'generated_output_discrepancies_found')
    return {'generated_counts': counts, 'generated_inventory_sha256': q.digest(json.dumps(extras, sort_keys=True).encode()),
            'marker_required': state.marker == 'required', 'weights_required': state.weights == 'required',
            'sessions_required': state.sessions == 'required', 'contract_verified': True,
            'unknown_absolute_writes_proved_absent': False}
