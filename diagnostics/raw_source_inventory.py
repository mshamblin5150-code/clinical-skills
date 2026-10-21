"""Verify raw workfile bytes against pinned Git tree/blob identities.

No archive, worktree conversion, clean/smudge filter, or normalization participates
in the oracle. The Git object hash includes its blob header; SHA-256 inventories
remain a separate identity used for subsequent clone/source checks.
"""
from __future__ import annotations

import hashlib
from pathlib import PurePosixPath
import re
import time

from lazy_suite_support import Refused, require
from measure_parallel_readers import inventory


class RawIdentityMismatch(Refused):
    def __init__(self, details):
        super().__init__('seed_raw_bytes_differ_from_commit')
        self.diagnostics = details


def parse_tree(raw, object_format):
    require(object_format in ('sha1', 'sha256'), 'unsupported_git_object_format')
    require(isinstance(raw, bytes) and 0 < len(raw) <= 16777216 and raw.endswith(b'\0'),
            'raw_tree_output_invalid')
    width = 40 if object_format == 'sha1' else 64
    records = raw[:-1].split(b'\0')
    require(0 < len(records) <= 10000, 'raw_tree_population_limit')
    manifest = {}
    for record in records:
        fields = record.split(b'\t', 1)
        require(len(fields) == 2, 'raw_tree_record_invalid')
        header = fields[0].split(b' ')
        require(len(header) == 3 and header[0] in (b'100644', b'100755') and header[1] == b'blob',
                'raw_tree_nonregular_or_unread')
        require(re.fullmatch(rb'[0-9a-f]{' + str(width).encode('ascii') + rb'}', header[2]) is not None,
                'raw_tree_oid_invalid')
        try:
            name = fields[1].decode('utf-8', errors='strict')
        except UnicodeDecodeError:
            raise Refused('raw_tree_path_encoding_unread') from None
        path = PurePosixPath(name)
        require(name and not path.is_absolute() and path.as_posix() == name
                and all(part not in ('', '.', '..', '.git') for part in name.split('/'))
                and '\\' not in name and ':' not in name and name not in manifest,
                'raw_tree_path_invalid_or_duplicate')
        manifest[name] = header[2].decode('ascii')
    require('.gitignore' in manifest, 'pinned_ignore_missing')
    return manifest


def discrepancy(manifest, observed, changed):
    """Bounded structural receipt: no paths, content, or external error text."""
    missing = sorted(set(manifest) - set(observed))
    extra = sorted(set(observed) - set(manifest))
    changed = sorted(changed)
    rows = []
    for category, names in (('missing', missing), ('extra', extra), ('changed', changed)):
        for name in names:
            if len(rows) == 8:
                break
            rows.append({'category': category, 'path_token': hashlib.sha256(name.encode('utf-8')).hexdigest()})
    total = len(missing) + len(extra) + len(changed)
    return {'missing': len(missing), 'extra': len(extra), 'changed': len(changed),
            'entries': rows, 'omitted_entries': total - len(rows),
            'raw_contents_disclosed': False, 'raw_paths_disclosed': False}


def raw_source_inventory(session, seed, pin):
    require(time.monotonic() < session.deadline, 'raw_oracle_deadline_expired')
    require(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', pin) is not None, 'raw_oracle_pin_invalid')
    object_format = session.git(seed, 'rev-parse', '--show-object-format').strip()
    require(object_format in ('sha1', 'sha256'), 'unsupported_git_object_format')
    require(len(pin) == (40 if object_format == 'sha1' else 64), 'raw_oracle_pin_format_mismatch')
    manifest = parse_tree(session.git_bytes(seed, '--no-replace-objects', 'ls-tree', '-r', '-z', '--full-tree', pin), object_format)
    # Proven inventory refuses symlinks, Windows reparse paths, hardlinks and
    # special files, and checks its inherited global deadline during the walk.
    observed = inventory(seed, deadline=session.deadline)
    changed = []
    for name in sorted(set(manifest) & set(observed)):
        require(time.monotonic() < session.deadline, 'raw_oracle_deadline_expired')
        path = seed / name
        for component in (path, *path.parents):
            if component == seed:
                break
            metadata = component.lstat()
            require(not component.is_symlink() and not (getattr(metadata, 'st_file_attributes', 0) & 0x400),
                    'raw_oracle_reparse_path_changed')
        before = path.lstat()
        require(path.is_file() and not path.is_symlink() and before.st_nlink == 1
                and not (getattr(before, 'st_file_attributes', 0) & 0x400), 'raw_oracle_file_kind_changed')
        object_hash = hashlib.new(object_format)
        object_hash.update(b'blob ' + str(before.st_size).encode('ascii') + b'\0')
        content_hash = hashlib.sha256()
        length = 0
        with path.open('rb') as stream:
            while True:
                require(time.monotonic() < session.deadline, 'raw_oracle_deadline_expired')
                chunk = stream.read(65536)
                if not chunk:
                    break
                length += len(chunk)
                object_hash.update(chunk)
                content_hash.update(chunk)
        after = path.lstat()
        require((before.st_ino, before.st_size, before.st_mtime_ns) ==
                (after.st_ino, after.st_size, after.st_mtime_ns) and length == before.st_size,
                'raw_oracle_file_changed_during_read')
        if object_hash.hexdigest() != manifest[name] or content_hash.hexdigest() != observed[name]:
            changed.append(name)
    details = discrepancy(manifest, observed, changed)
    if details['missing'] or details['extra'] or details['changed']:
        raise RawIdentityMismatch(details)
    require(time.monotonic() < session.deadline, 'raw_oracle_deadline_expired')
    return observed
