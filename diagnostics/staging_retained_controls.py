"""Finite synthetic output-guard controls, isolated from every source checkout."""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import time
import sys
from types import SimpleNamespace
from unittest import mock

import measure_maintainer_pair as m

q = m.q
CASES = (('empty_sessions', None),
         ('sessions_content', 'scratch_sessions_not_empty'),
         ('sessions_nested', 'scratch_sessions_not_empty'),
         ('unread_directory', 'retained_directory_unread'),
         ('linked_sessions', 'unexpected_retained_directory'))


def make_link(link, target):
    """No policy changes; junctions need no symlink privilege on Windows."""
    if os.name == 'nt':
        result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(link), str(target)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        q.require(result.returncode == 0, 'retained_control_link_unavailable')
        kind = 'junction'
    else:
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            raise q.Refused('retained_control_link_unavailable') from None
        kind = 'symlink'
    metadata = link.lstat()
    q.require(stat.S_ISLNK(metadata.st_mode) or bool(getattr(metadata, 'st_file_attributes', 0) & 0x400),
              'retained_control_link_not_native')
    return kind


def unlink_native(link, kind):
    if kind == 'junction':
        os.rmdir(link)
    else:
        link.unlink()
    q.require(not os.path.lexists(link), 'retained_control_link_cleanup_failed')


@contextlib.contextmanager
def fixture(report_root, observe):
    holder = tempfile.TemporaryDirectory(prefix='retained-controls-', dir=report_root)
    try:
        yield Path(holder.name)
    except BaseException as error:
        if observe is not None:
            observe(None, 'failed', error)  # Preserve current case setup failure before fixture cleanup.
        raise
    finally:
        if observe is not None:
            observe('fixture', 'cleanup_started')
        try:
            holder.cleanup()
        except BaseException as error:
            if observe is not None:
                observe('fixture', 'cleanup_failed', error)
            raise
        if observe is not None:
            observe('fixture', 'cleanup_passed')


def controls(report_root, deadline, observe=None):
    if observe is not None:
        observe('fixture', 'started')
    m.safe_directory(report_root)
    rows = []
    link_kind = None
    with fixture(report_root, observe) as root:
        for case, wanted in CASES:
            if observe is not None:
                observe(case, 'started')
            q.require(time.monotonic() < deadline, 'global_budget_exhausted')
            repo = root / case
            sessions = repo / 'scratch/sessions'
            sessions.mkdir(parents=True)
            link = None
            if case == 'sessions_content':
                (sessions / 'synthetic.txt').write_bytes(b'synthetic\n')
            elif case == 'sessions_nested':
                (sessions / 'nested').mkdir()
            original_scandir = os.scandir
            def scandir(path):
                if case == 'unread_directory' and Path(path) == sessions:
                    raise PermissionError('synthetic unread control')
                return original_scandir(path)
            observed = None
            try:
                if case == 'linked_sessions':
                    sessions.rmdir()
                    target = root / 'owned-link-target'
                    target.mkdir()
                    (target / 'sentinel').write_bytes(b'synthetic')
                    link = sessions
                    link_kind = 'junction' if os.name == 'nt' else 'symlink'
                    q.require(make_link(sessions, target) == link_kind, 'retained_control_link_kind_changed')
                # Only this child-owned synthetic tree lacks real Git source/refs.
                # The real source-arm process never enters these patch contexts.
                with mock.patch.object(q, 'verify_sources'), mock.patch.object(m, 'verify_refs'), \
                     mock.patch.object(os, 'scandir', side_effect=scandir), \
                     contextlib.redirect_stdout(io.StringIO()):
                    try:
                        result = m.retained_guard(SimpleNamespace(deadline=deadline), repo, {}, False)
                        q.require(result['allowed_retained_file_count'] == 0, 'retained_control_extra_admitted')
                    except q.Refused as error:
                        observed = str(error)
                q.require(observed == wanted, 'retained_control_outcome_mismatch')
                rows.append({'id': case, 'refusal': observed, 'passed': True})
                if observe is not None:
                    observe(case, 'passed')
            except BaseException as error:
                if observe is not None:
                    observe(case, 'failed', error)
                raise
            finally:
                if observe is not None:
                    observe(case, 'cleanup_started')
                try:
                    if link is not None and os.path.lexists(link):
                        unlink_native(link, link_kind)
                        q.require(target.is_dir() and (target / 'sentinel').read_bytes() == b'synthetic',
                                  'retained_control_link_target_changed')
                except BaseException as error:
                    if observe is not None:
                        observe(case, 'cleanup_failed', error)
                    raise
                if observe is not None:
                    observe(case, 'cleanup_passed')
        # TemporaryDirectory cleanup is limited to this newly owned synthetic tree.
    q.require(not root.exists(), 'retained_control_cleanup_failed')
    return {'cases': rows, 'count': 5, 'synthetic_source_ref_isolation': True,
            'unread_mode': 'injected_scandir_permission_error', 'native_link_kind': link_kind,
            'fixture_cleanup_verified': True, 'passed': True}


def validate_receipt(row):
    q.require(type(row) is dict and set(row) == {'cases', 'count', 'synthetic_source_ref_isolation',
              'unread_mode', 'native_link_kind', 'fixture_cleanup_verified', 'passed'},
              'retained_control_receipt_invalid')
    q.require(type(row['count']) is int and row['count'] == 5 and row['passed'] is True
              and row['synthetic_source_ref_isolation'] is True and row['fixture_cleanup_verified'] is True
              and row['unread_mode'] == 'injected_scandir_permission_error'
              and row['native_link_kind'] in ('junction', 'symlink')
              and type(row['cases']) is list and len(row['cases']) == 5,
              'retained_control_receipt_invalid')
    for actual, (case, refusal) in zip(row['cases'], CASES):
        q.require(type(actual) is dict and set(actual) == {'id', 'refusal', 'passed'}
                  and actual['id'] == case and actual['refusal'] == refusal and actual['passed'] is True,
                  'retained_control_receipt_invalid')
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-root', required=True, type=Path)
    parser.add_argument('--deadline', required=True, type=float)
    args = parser.parse_args()
    active = {'case': 'fixture', 'state': 'started'}
    primary = {}
    def observe(case, state, error=None):
        from diagnostic_observations import exception_category, reason_category
        case = active['case'] if case is None else case
        if error is not None and not primary:
            primary.update(case=case, state='failed', failure_stage=active['state'],
                           exception_category=exception_category(error), reason=reason_category(error))
        active.update(case=case, state=state)
        print('RETAINED_CONTROL_OBSERVATION:' + json.dumps({'case': case, 'state': state}), file=sys.stderr)
    try:
        row = validate_receipt(controls(args.report_root, args.deadline, observe=observe))
    except BaseException as error:
        from diagnostic_observations import exception_category, reason_category
        print('RETAINED_CONTROL_OBSERVATION:' + json.dumps(primary or {**active, 'state': 'failed',
              'failure_stage': active['state'], 'exception_category': exception_category(error),
              'reason': reason_category(error)}), file=sys.stderr)
        print(json.dumps({'passed': False, 'reason': 'retained_controls_inconclusive'}))
        return 2
    print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
