#!/usr/bin/env python3
"""One unfiltered maintainer arm; the workflow admits only baseline then candidate."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import stat
import sys
import tempfile
import time

import measure_lazy_suite_ids as q
import diagnostic_observations as observation
from full_suite_receipts import parse_suite, allowed_retained, failure_target_receipt

SOURCE_SHA = '08db6360b453c2bf969a686f62f0477184d06351'
# Immutable discovery evidence from run 39752292249, not a full-suite result.
CURRENT_POPULATION = {
    'test_count': 8487,
    'sorted_ids_sha256': '2ddedf085b83618b1d059976838e80392c08b80d13ab40d954f887f258cb76a9',
    'unit_count': 1373,
    'unit_names_sha256': '0611deba35e93059a153e542142e297b31acefa18bac6fdca98bfc86ca9219d9',
    'new_module_test_count': 12,
    'new_module_ids_sha256': '61758003177b4195d5a753d13b5e2a9ef6f824083595474408f2f514ad89e6a8',
    'loader_error_count': 0, 'executed_test_count': 0,
    'units_derived_from_actual_objects': True, 'observed_baseline_count_corroborated': True,
}
OBSERVER_PATHS = q.OBSERVER_PATHS | {
    '.github/workflows/ci-checkpoint-discovery.yml',
    'diagnostics/diagnose_checkpoint_discovery.py', 'diagnostics/test_checkpoint_discovery.py',
    'diagnostics/checkpoint-discovery-budget.json', 'diagnostics/checkpoint-discovery-spec.md',
    'diagnostics/test_current_pair.py', 'diagnostics/current-pair-spec.md',
}

COMMANDS = (
    ('phi_layers', ('tools/phi_scan.py', '--layers', '--all')),
    ('suite', ('tools/suite.py',)),
    ('publication_measurements', ('tools/tracker_measurements.py',)),
    ('threshold_sheet', ('tools/threshold_sheet.py', '--all')),
    ('phi_shape_only', ('tools/phi_scan.py', '--all', '--allow-no-corpus')),
)


def environment_identity():
    image = {key: os.environ.get(key, '') for key in ('ImageOS', 'ImageVersion', 'RUNNER_OS', 'RUNNER_ARCH')}
    q.require(all(re.fullmatch(r'[A-Za-z0-9_. -]{1,128}', value) for value in image.values()), 'runner_identity_unread')
    cpu = os.cpu_count()
    q.require(type(cpu) is int and cpu > 0, 'cpu_identity_unread')
    return {'image': image, 'python': platform.python_version(),
            'interpreter_build_sha256': q.digest(sys.version.encode()), 'cpu_count': cpu,
            'default_workers': max(1, cpu * 3 // 4)}


def safe_directory(path):
    q.require(path.is_absolute() and path.resolve() == path, 'workspace_path_noncanonical')
    for component in (path, *path.parents):
        metadata = component.lstat()
        q.require(stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
                  and not (getattr(metadata, 'st_file_attributes', 0) & 0x400), 'workspace_ancestor_unsafe')


def workspace_clone_root(owner, observer, seed, expected):
    """Fresh short sibling of the actual workflow workspace, never under TEMP."""
    raw = os.environ.get('GITHUB_WORKSPACE')
    q.require(isinstance(raw, str) and bool(raw), 'workflow_workspace_unavailable')
    workspace = Path(raw)
    safe_directory(workspace)
    q.require(observer.parent == workspace and seed.parent == workspace,
              'workflow_workspace_identity_changed')
    temporary = {Path(tempfile.gettempdir()).resolve()}
    temporary.update(Path(os.environ[key]).resolve() for key in ('TEMP', 'TMP') if os.environ.get(key))
    for path in temporary:
        safe_directory(path)
    parent = workspace.parent
    safe_directory(parent)
    q.require(all(parent != temp and not parent.is_relative_to(temp) for temp in temporary),
              'workspace_parent_inside_temp')
    root = Path(tempfile.mkdtemp(prefix='lc-', dir=parent))
    safe_directory(root)
    q.require(root.parent == parent and not any(root.iterdir()), 'workspace_clone_not_fresh')
    others = (owner, observer, seed, workspace, *temporary)
    q.require(all(root != other and root not in other.parents and other not in root.parents for other in others),
              'workspace_clone_overlap')
    units = lambda path: len(str(path).encode('utf-16-le', errors='surrogatepass')) // 2
    q.require(units(root) < units(owner), 'workspace_clone_not_shorter')
    longest = max(units(root / 'candidate' / name) for name in expected)
    q.require(longest < 260, 'workspace_source_path_too_long')
    q.emit('workspace_clone_boundary', outside_actual_temp=True, root_utf16_units=units(root),
           longest_source_utf16_units=longest, settings_changed=False)
    return root


def verify_hook_location(session, repo):
    payload = ("import json,sys;sys.path.insert(0,sys.argv[1]);"
               "import subagent_staging_hook as h;"
               "print(json.dumps({'checkout_named_temp':h.names_temp(sys.argv[2])}))")
    result = session.run([sys.executable, '-c', payload, str(repo / 'tools'), str(repo)], repo / 'tools')
    q.require(result['returncode'] == 0 and json.loads(result['stdout']) == {'checkout_named_temp': False},
              'source_hook_refuses_checkout_location')
    q.emit('source_hook_location', checkout_named_temp=False, source_hook_modified=False)


def rejected_entry(reason, relative=None, kind='unread'):
    q.emit('retained_entry_rejected', reason=reason, entry_kind=kind,
           path_token=q.digest(relative.encode('utf-8', errors='surrogatepass')) if relative is not None else None,
           category='scratch_sessions' if relative == 'scratch/sessions' else 'other_or_unread')
    raise q.Refused(reason)


def preserve_identity(progress, identity, discovery, behavior_ids):
    """Keep already validated finite environment/controls and bounded discovery."""
    keys = {'test_count', 'sorted_ids_sha256', 'loader_error_count', 'module_test_count',
            'executed_test_count', 'ids_encoding'}
    q.require(set(discovery) == keys
              and type(discovery['test_count']) is int and 0 < discovery['test_count'] <= 1000000
              and type(discovery['module_test_count']) is int
              and 0 < discovery['module_test_count'] <= discovery['test_count']
              and type(discovery['loader_error_count']) is int and discovery['loader_error_count'] == 0
              and type(discovery['executed_test_count']) is int and discovery['executed_test_count'] == 0
              and isinstance(discovery['sorted_ids_sha256'], str)
              and re.fullmatch(r'[0-9a-f]{64}', discovery['sorted_ids_sha256'])
              and discovery['ids_encoding'] == 'sorted JSON array, ASCII escaped, compact',
              'discovery_identity_invalid')
    q.require(behavior_ids == sorted(q.CONTROL_IDS), 'controls_population_changed')
    row = {'environment': identity, 'discovery': discovery, 'behavior_control_ids': behavior_ids}
    q.require(len(json.dumps(row, allow_nan=False)) <= 16384, 'precommand_identity_limit')
    progress.update(row)
    q.emit('maintainer_precommand_identity', **row)


def observe_suite(result, discovery, identity):
    row = {'returncode': result['returncode'], **failure_target_receipt(result['stdout'])}
    try:
        row['accounting'] = parse_suite(result['stdout'], result['stderr'], result['returncode'],
                                        discovery['test_count'], identity['cpu_count'])
        row['accounting_valid'] = True
    except q.Refused as error:
        row.update(accounting_valid=False, accounting_refusal=str(error))
    q.emit('suite_native_observation', **row)
    return row


def source_context(session, seed, repo, variant, expected, candidate, *, source_sha=None):
    source_sha = q.BASE if source_sha is None else source_sha
    result = session.run(['git', '-c', 'core.autocrlf=false', 'clone', '--no-local', '--no-hardlinks',
                          '--no-checkout', str(seed), str(repo)], repo.parent)
    q.require(result['returncode'] == 0, 'clone_failed')
    session.git(repo, '-c', 'core.autocrlf=false', 'checkout', '--detach', source_sha)
    # Only disposable refs change. HEAD/index/workfile source and genuine history do not.
    refs = session.git(repo, 'for-each-ref', '--format=%(refname)').splitlines()
    for ref in refs:
        q.require(re.fullmatch(r'refs/(heads|remotes|tags)/[A-Za-z0-9_./-]+', ref), 'source_ref_unread')
        session.git(repo, 'update-ref', '--no-deref', '-d', ref)
    session.git(repo, 'update-ref', 'refs/remotes/origin/main', source_sha)
    session.git(repo, 'symbolic-ref', 'refs/remotes/origin/HEAD', 'refs/remotes/origin/main')
    verify_refs(session, repo, source_sha=source_sha)
    q.first_clean(session, repo, source_sha, variant)
    q.require(q.inventory(repo, deadline=session.deadline) == expected, 'initial_clone_inventory_changed')
    q.inventory(repo / '.git', exclude_git=False, deadline=session.deadline)
    q.corpus_preflight((repo,))
    target = dict(expected)
    if variant == 'candidate':
        (repo / q.SUITE_PATH).write_bytes(candidate)
        target[q.SUITE_PATH] = q.digest(candidate)
    q.require(q.inventory(repo, deadline=session.deadline) == target, 'prepared_clone_inventory_changed')
    return target


def verify_refs(session, repo, *, source_sha=None):
    source_sha = q.BASE if source_sha is None else source_sha
    q.require(session.git(repo, 'rev-parse', '--is-shallow-repository').strip() == 'false', 'source_history_shallow')
    refs = session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)').splitlines()
    q.require(set(refs) == {'refs/remotes/origin/main ' + source_sha, 'refs/remotes/origin/HEAD ' + source_sha},
              'source_refs_changed')
    q.require(session.git(repo, 'symbolic-ref', 'refs/remotes/origin/HEAD').strip() == 'refs/remotes/origin/main',
              'source_remote_head_changed')


def retained_guard(session, repo, target, candidate):
    q.verify_sources(session, repo, target, candidate)
    verify_refs(session, repo)
    permitted_dirs = {'.', 'scratch', 'scratch/runs', 'scratch/sessions'}
    for name in target:
        permitted_dirs.update(p.as_posix() for p in Path(name).parents)
    extras = {}
    def unread_directory(error):
        rejected_entry('retained_directory_unread')
    for directory, dirs, files in os.walk(repo, followlinks=False, onerror=unread_directory):
        q.require(time.monotonic() < session.deadline, 'global_budget_exhausted')
        relative_dir = Path(directory).relative_to(repo).as_posix()
        if relative_dir == '.':
            dirs[:] = [name for name in dirs if name != '.git']
        if relative_dir == 'scratch/sessions' and (dirs or files):
            rejected_entry('scratch_sessions_not_empty', relative_dir, 'directory')
        for name in dirs:
            path = Path(directory) / name
            metadata = path.lstat()
            relative = path.relative_to(repo).as_posix()
            cache_dir = name == '__pycache__' and relative_dir in permitted_dirs
            if not (stat.S_ISDIR(metadata.st_mode) and not path.is_symlink()
                      and not (getattr(metadata, 'st_file_attributes', 0) & 0x400)
                      and (relative in permitted_dirs or cache_dir)):
                rejected_entry('unexpected_retained_directory', relative, 'directory')
        for name in files:
            path = Path(directory) / name
            relative = path.relative_to(repo).as_posix()
            if relative in target:
                continue
            metadata = path.lstat()
            if not (allowed_retained(relative, target) and stat.S_ISREG(metadata.st_mode)
                      and not path.is_symlink() and metadata.st_nlink == 1
                      and not (getattr(metadata, 'st_file_attributes', 0) & 0x400)
                      and metadata.st_size <= q.BUDGET['max_capture_bytes']):
                rejected_entry('unexpected_retained_file', relative, 'file')
            extras[relative] = q.digest(path.read_bytes())
            q.require(len(extras) <= 10000 and time.monotonic() < session.deadline, 'retained_output_limit')
    return {'allowed_retained_file_count': len(extras),
            'allowed_retained_inventory_sha256': q.digest(json.dumps(extras, sort_keys=True).encode()),
            'ephemeral_or_unknown_absolute_writes_proved_absent': False}


def generated_guard(session, repo, target, candidate, state):
    """Real-output admission uses the complete native-validated contract."""
    import generated_output_contract as contract
    q.verify_sources(session, repo, target, candidate, source_sha=SOURCE_SHA)
    verify_refs(session, repo, source_sha=SOURCE_SHA)
    detached = session.run(['git', '-C', str(repo), 'symbolic-ref', '-q', 'HEAD'], repo)
    q.require(detached['returncode'] == 1 and not detached['stdout'], 'source_refs_changed')
    return contract.scan(repo, target, session.deadline, state)


def behavior_controls(session, observer, repo, variant):
    result = session.run([sys.executable, str(observer / 'diagnostics/suite_id_lazy_controls.py'),
                          '--repo', str(repo)], repo / 'tools')
    q.emit('behavior_control_observed', variant=variant, exit_state=observation.exit_state(result.get('returncode')))
    ids = q.validate_controls(json.loads(result['stdout']), variant, result['returncode'])
    q.emit('behavior_controls', variant=variant, tests_run=6,
           expected_failures=2 if variant == 'baseline' else 0, errors=0)
    return sorted(ids)


def explicit_controls(session, seed, repo):
    payload = q.original_payload(seed)
    junction = session.run([sys.executable, '-c', payload, str(repo / 'tools'), q.JUNCTION, q.LOOKUPS[0]], repo / 'tools')
    q.emit('explicit_control_observed', selector=q.JUNCTION, exit_state=observation.exit_state(junction.get('returncode')))
    q.verify_probe(junction, 1, q.LOOKUPS[0])
    q.emit('junction_control', tests_run=1, successful=True)
    for selector in q.SYNTHETIC_SELECTORS:
        result = session.run([sys.executable, '-m', 'unittest', selector], repo / 'tools')
        q.emit('explicit_control_observed', selector=selector, exit_state=observation.exit_state(result.get('returncode')))
        q.verify_probe(result, 1, q.LOOKUPS[0])
        q.emit('synthetic_control', selector=selector, tests_run=1, successful=True,
               contention_reproduced=False, overlap_verified=False, root_cause_established=False)


def validate_environment(identity):
    keys = {'image', 'python', 'interpreter_build_sha256', 'cpu_count', 'default_workers'}
    q.require(type(identity) is dict and set(identity) == keys, 'baseline_not_safe_or_passed')
    image = identity['image']
    q.require(type(image) is dict and set(image) == {'ImageOS', 'ImageVersion', 'RUNNER_OS', 'RUNNER_ARCH'}
              and all(type(value) is str and re.fullmatch(r'[A-Za-z0-9_. -]{1,128}', value)
                      for value in image.values())
              and image['RUNNER_OS'] == 'Windows' and image['RUNNER_ARCH'] == 'X64'
              and type(identity['python']) is str and identity['python'] == '3.14.4'
              and type(identity['interpreter_build_sha256']) is str
              and re.fullmatch(r'[0-9a-f]{64}', identity['interpreter_build_sha256'])
              and type(identity['cpu_count']) is int and identity['cpu_count'] == 4
              and type(identity['default_workers']) is int and identity['default_workers'] == 3,
              'baseline_not_safe_or_passed')


def baseline_receipt(raw):
    q.require(isinstance(raw, str) and 0 < len(raw) <= 16384, 'baseline_receipt_missing_or_large')
    try:
        row = observation.unique_json(raw)
    except (ValueError, TypeError, RecursionError):
        raise q.Refused('baseline_not_safe_or_passed') from None
    q.require(type(row) is dict and row.get('variant') == 'baseline'
              and row.get('source_sha') == SOURCE_SHA
              and type(row.get('observer_sha')) is str
              and re.fullmatch(r'[0-9a-f]{40}', row['observer_sha'])
              and row['observer_sha'] == os.environ.get('GITHUB_SHA')
              and type(row.get('run_id')) is str and re.fullmatch(r'[0-9]+', row['run_id'])
              and row['run_id'] == os.environ.get('GITHUB_RUN_ID')
              and all(row.get(key) is True for key in (
                  'safe_to_continue', 'all_commands_passed', 'source_integrity_verified',
                  'process_cleanup_verified', 'output_contract_verified', 'hard_budget_verified')),
              'baseline_not_safe_or_passed')
    validate_population(row.get('discovery'), row.get('unit_discovery'))
    q.require(row.get('behavior_control_ids') == sorted(q.CONTROL_IDS), 'controls_population_changed')
    commands = row.get('command_returncodes')
    q.require(type(commands) is list and len(commands) == len(COMMANDS)
              and all(type(item) is list and len(item) == 2 and item[0] == name
                      and type(item[1]) is int and item[1] == 0
                      for item, (name, _) in zip(commands, COMMANDS)), 'baseline_not_safe_or_passed')
    identity, accounting = row.get('environment'), row.get('accounting')
    validate_environment(identity)
    q.require(type(accounting) is dict, 'baseline_not_safe_or_passed')
    required = {'discovered': CURRENT_POPULATION['test_count'], 'unaccounted': 0,
                'jobs': 3, 'cpu_count': 4, 'weights': 'equal', 'returncode': 0,
                'successful': True, 'internal_accounting': True, 'independent_executed_id_manifest': False,
                'skips': 'not separately exposed', 'expected_failures': 'not separately exposed'}
    timings = {'critical_unit_seconds', 'suite_reported_wall_seconds', 'next_worker_seconds'}
    q.require(set(accounting) == set(required) | timings | {'critical_unit_token'}
              and all(type(accounting.get(key)) is type(value) and accounting[key] == value
                      for key, value in required.items())
              and type(accounting['critical_unit_token']) is str
              and re.fullmatch(r'[0-9a-f]{64}', accounting['critical_unit_token'])
              and all(type(accounting[key]) is float and q.math.isfinite(accounting[key])
                      and 0 <= accounting[key] < 1e10 for key in timings)
              and accounting['suite_reported_wall_seconds'] > 0,
              'baseline_not_safe_or_passed')
    return row


def validate_population(discovery, units):
    q.require(type(discovery) is dict and type(units) is dict,
              'matched_environment_or_discovery_changed')
    q.require(set(units) == set(CURRENT_POPULATION) | {'module_test_count'}
              and all(type(units.get(key)) is type(value) and units[key] == value
                      for key, value in CURRENT_POPULATION.items())
              and type(units['module_test_count']) is int and 0 < units['module_test_count'] <= units['test_count'],
              'matched_environment_or_discovery_changed')
    expected = {key: units[key] for key in ('test_count', 'sorted_ids_sha256', 'module_test_count',
                                           'loader_error_count', 'executed_test_count')}
    expected['ids_encoding'] = 'sorted JSON array, ASCII escaped, compact'
    q.require(set(discovery) == set(expected)
              and all(type(discovery[key]) is type(value) and discovery[key] == value
                      for key, value in expected.items()), 'matched_environment_or_discovery_changed')


def compact_receipt(receipt):
    keys = ('variant', 'source_sha', 'observer_sha', 'run_id', 'safe_to_continue', 'all_commands_passed',
            'source_integrity_verified', 'process_cleanup_verified', 'output_contract_verified',
            'hard_budget_verified', 'environment', 'discovery', 'unit_discovery', 'behavior_control_ids',
            'accounting')
    row = {key: receipt[key] for key in keys if key in receipt}
    row['command_returncodes'] = [[item['command'], item['returncode']] for item in receipt.get('commands', ())]
    return row


def make_session(root, deadline, hard_deadline):
    # The discovery route already proved bounded owner finalization; share it.
    from diagnose_checkpoint_discovery import CheckpointSession
    return CheckpointSession(root, deadline, hard_deadline)


def verify_input_sources(session, observer, seed, snapshot, expected, refs, job_start_epoch):
    import generated_output_contract as contract
    for repo, target, pin in ((observer, snapshot, os.environ.get('GITHUB_SHA')), (seed, expected, SOURCE_SHA)):
        q.verify_sources(session, repo, target, source_sha=pin)
        q.require(session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)') == refs[repo],
                  'source_refs_changed')
        state = contract.State(marker='absent', weights='absent', sessions='optional',
                               job_start_epoch=job_start_epoch, observed_epoch=time.time(), max_job_seconds=5400)
        contract.scan(repo, target, session.deadline, state)


def execute(session, observer, seed, variant, identity, prior, progress=None, job_start_epoch=None):
    progress = progress if progress is not None else {}
    import diagnose_generated_outputs as generated
    import diagnose_checkpoint_discovery as checkpoint
    import generated_output_contract as contract
    preparation_start = time.monotonic()
    inputs, clone = None, None
    units, after_suite = (), False
    environment = dict(os.environ)
    def output_state():
        return contract.State(marker='required' if after_suite else 'absent',
                              weights='required' if after_suite else 'absent', units=units,
                              job_start_epoch=job_start_epoch, observed_epoch=time.time(),
                              max_job_seconds=5400, sessions='required' if after_suite else 'optional')
    def phase(name):
        generated.phase(session, progress, name)
        q.require(dict(os.environ) == environment, 'environment_changed')
        if inputs is not None:
            verify_input_sources(session, observer, seed, *inputs, job_start_epoch)
        if clone is not None:
            generated_guard(session, *clone, variant == 'candidate', output_state())
    phase('source')
    q.require(type(identity.get('cpu_count')) is int and identity['cpu_count'] == 4
              and type(identity.get('default_workers')) is int and identity['default_workers'] == 3,
              'matched_worker_topology_changed')
    q.first_clean(session, observer, os.environ.get('GITHUB_SHA'), 'observer')
    session.git(observer, 'merge-base', '--is-ancestor', q.OBSERVER_BASE, 'HEAD')
    q.require(set(session.git(observer, 'diff', '--name-only', q.OBSERVER_BASE, 'HEAD').splitlines()) == OBSERVER_PATHS,
              'observer_branch_scope_changed')
    q.first_clean(session, seed, SOURCE_SHA, 'seed')
    observer_snapshot = q.inventory(observer, deadline=session.deadline)
    expected = q.raw_source_inventory(session, seed, SOURCE_SHA)
    q.require(expected[q.SUITE_PATH] == q.ORIGINAL_HASH, 'baseline_module_hash_changed')
    candidate = q.read_reviewed_bytes(observer / q.SUITE_PATH, q.CANDIDATE_HASH)
    ref_snapshots = {repo: session.git(repo, 'for-each-ref', '--format=%(refname) %(objectname)')
                     for repo in (observer, seed)}
    inputs = (observer_snapshot, expected, ref_snapshots)
    phase('native')
    owned = session.run([sys.executable, str(observer / 'diagnostics/windows_job_probe_controls.py'), '--run',
                         '--report-dir', str(session.root / 'owner-controls')], observer / 'diagnostics')
    q.require(owned['returncode'] == 0, 'owner_controls_failed')
    q.validate_owner_controls(json.loads(owned['stdout']))
    q.emit('owner_controls', passed=True, count=9)
    # Reuse only the bounded synthetic guard gate, not TEMP layout test cases.
    from diagnose_staging_layout import verify_retained_controls
    phase('retained')
    verify_retained_controls(session, observer)
    phase('contract')
    controls = session.run([sys.executable, str(observer / 'diagnostics/diagnose_generated_outputs.py'),
                            '--contract-child'], observer / 'diagnostics')
    progress['contract_controls'] = q.verify_probe(controls, generated.CONTRACT_CONTROL_COUNT, q.LOOKUPS[0])
    q.emit('generated_contract_controls', tests_run=generated.CONTRACT_CONTROL_COUNT, **progress['contract_controls'])
    phase('clone')
    clone_root = workspace_clone_root(session.root, observer, seed, expected)
    repo = clone_root / variant
    target = source_context(session, seed, repo, variant, expected, candidate, source_sha=SOURCE_SHA)
    clone = (repo, target)
    phase('temp')
    temp_receipt = q.parse_child(session.run(q.child_command(observer, 'validate-temp', repo), repo / 'tools'))
    q.require(temp_receipt.get('outside_checkout_temp') is True and temp_receipt.get('temp_environment_unchanged') is True,
              'temp_validation_incomplete')
    verify_hook_location(session, repo)
    phase('pair_behavior')
    behavior_ids = behavior_controls(session, observer, repo, variant)
    phase('pair_explicit')
    explicit_controls(session, seed, repo)
    phase('discovery')
    discovery = q.parse_child(session.run(q.child_command(observer, 'discover', repo), repo / 'tools'))
    phase('discovery_validate')
    unit_result = session.run([sys.executable, str(observer / 'diagnostics/diagnose_checkpoint_discovery.py'),
                               '--child', 'units', '--repo', str(repo)], repo / 'tools')
    actual = checkpoint.validate_identity(unit_result, discovery)
    units, unit_identity = actual['units'], actual['public']
    validate_population(discovery, unit_identity)
    progress['unit_discovery'] = unit_identity
    q.emit('generated_unit_discovery', **unit_identity)
    preserve_identity(progress, identity, discovery, behavior_ids)
    q.require(not (repo / 'scratch').exists(), 'initial_suite_weights_or_scratch_present')
    if prior:
        q.require(prior.get('environment') == identity and prior.get('discovery') == discovery
                  and prior.get('behavior_control_ids') == behavior_ids
                  and prior.get('unit_discovery') == unit_identity,
                  'matched_environment_or_discovery_changed')
    phase('initial_guard')
    generated_guard(session, repo, target, variant == 'candidate', output_state())
    setup_seconds = time.monotonic() - preparation_start
    q.require(session.deadline - time.monotonic() >= 4200, 'estimated_maintainer_plan_no_longer_fits')
    q.emit('estimated_admission', suite_and_ancillary_seconds=4200, cleanup_reserve_seconds=300, completion_guaranteed=False)
    rows, suite_result = [], None
    # Preserve maintainer always-after-suite semantics for ordinary nonzero exits.
    # Ownership/deadline/capture/source violations still stop immediately.
    for name, argv in COMMANDS:
        phase('pair_' + name)
        q.emit('maintainer_command_started', command=name)
        result = session.run([sys.executable, *argv], repo)
        row = {'command': name, 'returncode': result['returncode'],
               'wall_seconds': result['wall_seconds'], 'tree_cpu_seconds': result['tree_cpu_seconds'],
               'stdout_sha256': q.digest(Path(result['stdout_path']).read_bytes()),
               'stderr_sha256': q.digest(Path(result['stderr_path']).read_bytes())}
        rows.append(row)
        progress['commands'] = list(rows)
        q.emit('maintainer_command_finished', **row)
        if name == 'suite':
            suite_result = result
            progress['suite_observation'] = observe_suite(result, discovery, identity)
            after_suite = True
        phase('pair_guard_' + name)
        generated_guard(session, repo, target, variant == 'candidate', output_state())
        if name == 'suite':
            q.require(progress['suite_observation']['accounting_valid'], 'suite_accounting_incomplete')
    accounting = parse_suite(suite_result['stdout'], suite_result['stderr'], suite_result['returncode'],
                             discovery['test_count'], identity['cpu_count'])
    phase('final_source')
    retained = generated_guard(session, repo, target, variant == 'candidate', output_state())
    q.require(q.inventory(seed, deadline=session.deadline) == expected, 'seed_changed')
    verify_input_sources(session, observer, seed, *inputs, job_start_epoch)
    return {'unit_discovery': unit_identity, 'behavior_control_ids': behavior_ids, 'setup_seconds': setup_seconds, 'discovery': discovery, 'environment': identity, 'commands': rows, 'accounting': accounting,
            'retained': retained, 'all_commands_passed': all(row['returncode'] == 0 for row in rows)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observer', type=Path, required=True)
    parser.add_argument('--seed', type=Path, required=True)
    parser.add_argument('--variant', choices=('baseline', 'candidate'), required=True)
    parser.add_argument('--job-start-epoch', type=float, required=True)
    args = parser.parse_args(argv)
    start = time.monotonic()
    session, root, complete, clean, failure, evidence, prior = None, None, False, False, None, {}, None
    hard_deadline = None
    original_env = dict(os.environ)
    try:
        q.require(os.name == 'nt' and platform.python_version() == '3.14.4', 'windows_python_pin_required')
        q.require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_EVENT_NAME') == 'push'
                  and os.environ.get('GITHUB_REF') == q.BRANCH and os.environ.get('GITHUB_RUN_ATTEMPT') == '1',
                  'unauthorized_event_or_rerun')
        q.require(re.fullmatch(r'[0-9a-f]{40}', os.environ.get('GITHUB_SHA', ''))
                  and re.fullmatch(r'[0-9]+', os.environ.get('GITHUB_RUN_ID', '')), 'unauthorized_event_or_rerun')
        elapsed = time.time() - args.job_start_epoch
        q.require(q.math.isfinite(elapsed) and 0 <= elapsed < 900, 'setup_estimate_exhausted')
        hard_deadline = start + 5400 - elapsed
        deadline = hard_deadline - 300
        prior = baseline_receipt(os.environ.get('BASELINE_RECEIPT')) if args.variant == 'candidate' else None
        identity = environment_identity()
        validate_environment(identity)
        q.require(prior is None or prior['environment'] == identity, 'matched_environment_or_discovery_changed')
        q.environment_preflight()
        observer, seed = args.observer.resolve(), args.seed.resolve()
        q.require(observer != seed and observer not in seed.parents and seed not in observer.parents, 'checkout_overlap')
        q.corpus_preflight((observer, seed))
        temp = Path(tempfile.gettempdir()).resolve()
        q.require(all(not temp.is_relative_to(repo) for repo in (observer, seed)), 'temp_inside_checkout')
        root = Path(tempfile.mkdtemp(prefix='maintainer-pair-', dir=temp))
        session = make_session(root, deadline, hard_deadline)
        evidence.update(execute(session, observer, seed, args.variant, identity, prior, evidence, args.job_start_epoch))
        evidence['active_phase'] = session.phase = 'environment'
        q.require(dict(os.environ) == original_env, 'environment_changed')
        q.require(time.monotonic() < deadline, 'global_budget_exhausted')
        complete = True
    except BaseException as error:
        failure = observation.reason_category(error)
        evidence['failure_phase'] = observation.phase_name(evidence.get('active_phase', 'preflight'))
        try:
            q.safe_exception(error, root)
        except BaseException:
            pass
        q.emit('hold', reason=failure, phase=evidence['failure_phase'],
               error_type=observation.exception_category(error), comparative_claim_allowed=False)
    finally:
        cleanup_start = time.monotonic()
        if session is not None:
            session.phase = 'cleanup'
            try:
                clean = session.cleanup() is True
                q.emit('diagnostic_cleanup', verified=clean, exception_category=None)
                if not clean and failure is None:
                    failure = 'cleanup_unverified'
                    evidence['failure_phase'] = 'cleanup'
            except BaseException as error:
                clean = False
                q.emit('diagnostic_cleanup', verified=False, exception_category=observation.exception_category(error))
                if failure is None:
                    failure = 'cleanup_failed'
                    evidence['failure_phase'] = 'cleanup'
        within_budget = hard_deadline is not None and time.monotonic() < hard_deadline
        safe = complete and clean and within_budget
        passed = safe and evidence.get('all_commands_passed') is True
        pair_passed = passed and args.variant == 'candidate' and prior.get('all_commands_passed') is True
        receipt = {**evidence, 'variant': args.variant, 'source_sha': SOURCE_SHA, 'safe_to_continue': safe,
                   'observer_sha': os.environ.get('GITHUB_SHA'), 'run_id': os.environ.get('GITHUB_RUN_ID'),
                   'process_cleanup_verified': clean, 'source_integrity_verified': complete,
                   'output_contract_verified': complete, 'hard_budget_verified': within_budget,
                   'all_commands_passed': passed, 'pair_passed': pair_passed,
                   'preliminary_one_pair_only': True, 'stable_speedup_or_adoption': False,
                   'pr_and_production_push_metadata_checks': 'NOT RUN', 'clinical_corpus': 'NOT RUN',
                   'private_raw_evidence_uploaded': False, 'runner_teardown_proved': False,
                   'observer_seconds': time.monotonic()-start, 'failure': failure, 'cleanup_seconds': time.monotonic()-cleanup_start}
        # Do not publish spending permission from flags alone. Validate the same
        # complete receipt here, before the workflow can schedule the next arm.
        if passed:
            try:
                baseline_receipt(json.dumps(compact_receipt(receipt) | {'variant': 'baseline'}, allow_nan=False))
            except (q.Refused, ValueError, TypeError):
                safe = passed = False
                receipt.update(safe_to_continue=False, all_commands_passed=False, pair_passed=False,
                               failure='baseline_not_safe_or_passed')
        q.emit('maintainer_arm_summary', **receipt)
        output = os.environ.get('GITHUB_OUTPUT')
        if output:
            compact = compact_receipt(receipt)
            payload = json.dumps(compact, separators=(',', ':'), allow_nan=False)
            q.require(len(payload) <= 16384, 'pair_receipt_limit')
            with open(output, 'a', encoding='utf-8') as stream:
                stream.write('safe=' + str(safe).lower() + '\npassed=' + str(passed).lower() + '\nreceipt=' + payload + '\n')
    return 0 if passed else 1 if safe else 2


if __name__ == '__main__':
    raise SystemExit(main())
