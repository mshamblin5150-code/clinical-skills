#!/usr/bin/env python3
"""Setup evidence only: no discovery, behavior tests, or performance probes."""
import argparse
import math
import os
from pathlib import Path
import platform
import tempfile
import time
import json
import sys
import stat
import hashlib

import measure_lazy_suite_ids as q

JOB_SECONDS = 600
CLEANUP_SECONDS = 60
EXACT_PATH = ('docs/adr/0121-the-module-root-literal-is-the-worktree-and-is-bound-by-a-property-'
              'rather-than-a-walk-and-a-failed-tree-read-is-a-coverage-gap-while-an-unvouched-publication-is-refused.md')


def utf16_units(path):
    size = len(str(path).encode('utf-16-le', errors='surrogatepass')) // 2
    q.require(size <= 1000000, 'path_length_unread')
    return size


def exact_path_evidence(session, repo, expected_hash):
    """Only called AFTER first status; no Git refresh or second status."""
    q.require(time.monotonic() < session.deadline, 'global_budget_exhausted')
    path = repo / EXACT_PATH
    result = {'path_token': q.digest(EXACT_PATH.encode()), 'root_utf16_units': utf16_units(repo),
              'relative_utf16_units': utf16_units(EXACT_PATH), 'full_path_utf16_units': utf16_units(path),
              'core_longpaths': 'unavailable', 'filesystem': 'unavailable', 'raw_identity': 'unavailable'}
    config = session.run(['git', '-C', str(repo), 'config', '--get', 'core.longpaths'], repo)
    value = config['stdout'].strip().lower()
    result['core_longpaths'] = (value if config['returncode'] == 0 and value in ('true', 'false') else
                               'unset' if config['returncode'] == 1 and not value else
                               'unrecognized' if config['returncode'] == 0 else 'unavailable')
    read_complete = False
    try:
        for component in (repo, repo / 'docs', repo / 'docs/adr', path):
            metadata = component.lstat()
            q.require(not stat.S_ISLNK(metadata.st_mode)
                      and not (getattr(metadata, 'st_file_attributes', 0) & 0x400), 'exact_path_link_refused')
            if component != path:
                q.require(stat.S_ISDIR(metadata.st_mode), 'exact_path_ancestor_not_directory')
        before = path.lstat()
        q.require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'exact_path_nonregular_refused')
        q.require(before.st_size <= q.BUDGET['max_capture_bytes'], 'exact_path_read_limit')
        result['filesystem'] = 'regular'
        hashed, size = hashlib.sha256(), 0
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            q.require((opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
                      == (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
                      and stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1,
                      'exact_path_changed_during_read')
            while True:
                q.require(time.monotonic() < session.deadline, 'global_budget_exhausted')
                chunk = stream.read(65536)
                if not chunk:
                    break
                size += len(chunk)
                q.require(size <= q.BUDGET['max_capture_bytes'], 'exact_path_read_limit')
                hashed.update(chunk)
        read_complete = True
        after = path.lstat()
        q.require((after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_mode, after.st_nlink)
                  == (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_mode, before.st_nlink)
                  and size == before.st_size, 'exact_path_changed_during_read')
        result['raw_identity'] = 'equal' if hashed.hexdigest() == expected_hash else 'different'
    except FileNotFoundError:
        q.require(not read_complete, 'exact_path_changed_during_read')
        result['filesystem'] = 'missing-or-inaccessible'
    except PermissionError:
        q.require(not read_complete, 'exact_path_changed_during_read')
        result['filesystem'] = 'inaccessible'
    except OSError:
        q.require(not read_complete, 'exact_path_changed_during_read')
        result['filesystem'] = 'unavailable'
    q.require(time.monotonic() < session.deadline, 'global_budget_exhausted')
    return result


def run_arm(session, seed, repo, role, expected):
    q.require(role in ('original-layout', 'short-layout'), 'unknown_root_arm')
    q.require(EXACT_PATH in expected, 'exact_path_not_pinned')
    cloned = session.run(['git', '-c', 'core.autocrlf=false', 'clone', '--no-local', '--no-hardlinks',
                          '--no-checkout', str(seed), str(repo)], repo.parent)
    q.require(cloned['returncode'] == 0, 'clone_failed')
    session.git(repo, '-c', 'core.autocrlf=false', 'checkout', '--detach', q.BASE)
    admitted = True
    try:
        q.first_clean(session, repo, q.BASE, role)
    except q.Refused as error:
        if str(error) != 'first_status_not_clean':
            raise
        admitted = False  # Permanent rejection; later evidence never changes this.
    evidence = exact_path_evidence(session, repo, expected[EXACT_PATH])
    q.emit('exact_path_observation', role=role, **evidence)
    q.require(evidence['raw_identity'] != 'different', 'exact_path_raw_identity_changed')
    if admitted:
        q.require(q.inventory(repo, deadline=session.deadline) == expected, 'initial_clone_inventory_changed')
    q.inventory(repo / '.git', exclude_git=False, deadline=session.deadline)
    q.require(not any(os.path.lexists(repo / name) for name in ('scratch', 'output')), 'private_roots_present')
    q.corpus_preflight((repo,), admission=False)
    row = {'role': role, 'admitted': admitted, 'raw_tree_identity_verified': admitted,
           'first_status_refused': not admitted, 'exact_path': evidence}
    q.emit('root_arm', **row)
    return row


def budget_deadline(job_start_epoch, wall_now, monotonic_now):
    values = (job_start_epoch, wall_now, monotonic_now)
    q.require(all(isinstance(v, (int, float)) and not isinstance(v, bool)
                  and math.isfinite(v) for v in values), 'setup_clock_invalid')
    elapsed = wall_now - job_start_epoch
    q.require(0 <= elapsed < JOB_SECONDS - CLEANUP_SECONDS, 'setup_budget_exhausted')
    return monotonic_now + JOB_SECONDS - elapsed - CLEANUP_SECONDS


def setup(session, observer, seed):
    q.first_clean(session, observer, os.environ.get('GITHUB_SHA'), 'observer')
    session.git(observer, 'merge-base', '--is-ancestor', q.OBSERVER_BASE, 'HEAD')
    changed = set(session.git(observer, 'diff', '--name-only', q.OBSERVER_BASE, 'HEAD').splitlines())
    q.require(changed == q.OBSERVER_PATHS, 'observer_branch_scope_changed')
    q.first_clean(session, seed, q.BASE, 'seed')
    observer_snapshot = q.inventory(observer, deadline=session.deadline)
    expected = q.raw_source_inventory(session, seed, q.BASE)
    q.require(expected[q.SUITE_PATH] == q.ORIGINAL_HASH, 'baseline_module_hash_changed')
    q.original_payload(seed)  # Preserve the existing source-only validation order.
    q.emit('setup_scope', source_sha=q.BASE, observer_base=q.OBSERVER_BASE,
           planned_performance_probes=0, job_seconds=JOB_SECONDS,
           cleanup_reserve_seconds=CLEANUP_SECONDS, configuration_fix=False)
    owned = session.run([sys.executable, str(observer / 'diagnostics/windows_job_probe_controls.py'),
                         '--run', '--report-dir', str(session.root / 'owner-controls')],
                        observer / 'diagnostics')
    q.require(owned['returncode'] == 0, 'owner_controls_failed')
    q.validate_owner_controls(json.loads(owned['stdout']))
    q.emit('owner_controls', passed=True, count=len(q.DECLARED_CONTROL_IDS))
    rows = [run_arm(session, seed, session.root / 'baseline', 'original-layout', expected)]
    short_root = Path(tempfile.mkdtemp(prefix='lc-', dir=session.root.parent))
    q.require(short_root.parent == session.root.parent and short_root != session.root
              and short_root.resolve() == short_root and short_root.is_dir()
              and not any(short_root.iterdir())
              and all(short_root != other and short_root not in other.parents and other not in short_root.parents
                      for other in (session.root, observer, seed))
              and not short_root.is_symlink() and not (getattr(short_root.lstat(), 'st_file_attributes', 0) & 0x400),
              'short_root_boundary_invalid')
    for component in (short_root, *short_root.parents):
        metadata = component.lstat()
        q.require(stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
                  and not (getattr(metadata, 'st_file_attributes', 0) & 0x400), 'short_root_ancestor_unsafe')
    q.require(utf16_units(short_root) < utf16_units(session.root), 'short_root_not_shorter')
    rows.append(run_arm(session, seed, short_root / 'baseline', 'short-layout', expected))
    for row, repo in zip(rows, (session.root / 'baseline', short_root / 'baseline')):
        if row['admitted']:
            q.require(q.inventory(repo, deadline=session.deadline) == expected, 'final_clone_inventory_changed')
    q.require(q.inventory(seed, deadline=session.deadline) == expected, 'seed_changed')
    for name, expected_hash in observer_snapshot.items():
        q.require(q.digest((observer / name).read_bytes()) == expected_hash, 'observer_source_changed')
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observer', type=Path, required=True)
    parser.add_argument('--seed', type=Path, required=True)
    parser.add_argument('--job-start-epoch', type=float, required=True)
    args = parser.parse_args(argv)
    session, root, complete, clean, failure = None, None, False, False, None
    arms = []
    start = time.monotonic()
    original_env = dict(os.environ)
    try:
        q.require(os.name == 'nt' and platform.python_version() == '3.14.4', 'windows_python_pin_required')
        q.require(os.environ.get('GITHUB_ACTIONS') == 'true'
                  and os.environ.get('GITHUB_EVENT_NAME') == 'push'
                  and os.environ.get('GITHUB_REF') == q.BRANCH
                  and os.environ.get('GITHUB_RUN_ATTEMPT') == '1', 'unauthorized_event_or_rerun')
        deadline = budget_deadline(args.job_start_epoch, time.time(), start)
        q.environment_preflight()
        observer, seed = args.observer.resolve(), args.seed.resolve()
        q.require(observer != seed and observer not in seed.parents and seed not in observer.parents,
                  'checkout_overlap')
        q.corpus_preflight((observer, seed))
        temp = Path(tempfile.gettempdir()).resolve()
        q.require(all(not temp.is_relative_to(repo) for repo in (observer, seed)), 'temp_inside_checkout')
        root = Path(tempfile.mkdtemp(prefix='lazy-setup-diagnostic-', dir=temp))
        session = q.Session(root, deadline)
        arms = setup(session, observer, seed)
        q.require(dict(os.environ) == original_env, 'environment_changed')
        complete = True
    except BaseException as error:
        failure = str(error) if isinstance(error, q.Refused) else 'unexpected_exception_details_withheld'
        details = q.safe_exception(error, root)
        if isinstance(error, q.RawIdentityMismatch):
            q.emit('source_discrepancy', **error.diagnostics)
        q.emit('hold', reason=failure, error_type=type(error).__name__,
               private_detail_retained=details['private_detail_retained'], comparative_claim_allowed=False)
    finally:
        if session is not None:
            clean = session.cleanup()
        q.emit('setup_summary', status='diagnostic-complete' if complete and clean else 'inconclusive',
               planned_performance_probes=0, completed_performance_probes=0,
               diagnostic_collection_complete=complete,
               setup_integrity_verified=complete and len(arms) == 2 and all(
                   row.get('admitted') is True and row.get('raw_tree_identity_verified') is True for row in arms),
               process_cleanup_verified=clean,
               root_arms=arms, all_arms_admitted=bool(arms) and all(row['admitted'] for row in arms),
               raw_evidence_retained=root is not None, raw_evidence_uploaded=False,
               teardown_independently_proved=False, qualification=False,
               root_cause_established=False, configuration_fix=False, automatic_rerun=False,
               observer_seconds=time.monotonic()-start, failure=failure)
    return 0 if complete and clean else 2


if __name__ == '__main__':
    raise SystemExit(main())
