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

import measure_lazy_suite_ids as q

JOB_SECONDS = 600
CLEANUP_SECONDS = 60


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
    candidate = q.read_reviewed_bytes(observer / q.SUITE_PATH, q.CANDIDATE_HASH)
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
    clones = {variant: q.make_clone(session, seed, session.root, variant, expected, candidate)
              for variant in ('baseline', 'candidate')}
    for variant, (repo, target) in clones.items():
        q.require(q.inventory(repo, deadline=session.deadline) == target, 'final_clone_inventory_changed')
        q.emit('clone_setup_complete', role=variant, raw_identity_verified=True)
    q.require(q.inventory(seed, deadline=session.deadline) == expected, 'seed_changed')
    for name, expected_hash in observer_snapshot.items():
        q.require(q.digest((observer / name).read_bytes()) == expected_hash, 'observer_source_changed')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observer', type=Path, required=True)
    parser.add_argument('--seed', type=Path, required=True)
    parser.add_argument('--job-start-epoch', type=float, required=True)
    args = parser.parse_args(argv)
    session, root, complete, clean, failure = None, None, False, False, None
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
        setup(session, observer, seed)
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
        q.emit('setup_summary', status='setup-complete' if complete and clean else 'inconclusive',
               planned_performance_probes=0, completed_performance_probes=0,
               setup_integrity_verified=complete, process_cleanup_verified=clean,
               raw_evidence_retained=root is not None, raw_evidence_uploaded=False,
               teardown_independently_proved=False, qualification=False,
               root_cause_established=False, configuration_fix=False, automatic_rerun=False,
               observer_seconds=time.monotonic()-start, failure=failure)
    return 0 if complete and clean else 2


if __name__ == '__main__':
    raise SystemExit(main())
