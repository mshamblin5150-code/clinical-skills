"""Five bounded consumers of owned, fixed synthetic output, not Git qualification.

The driver separately guards real Git sources. This adapter substitutes only the
logical command's output-producing child; original source predicates, explicit
acknowledgments, classification, scheduler and CompactStore remain unchanged.
All owner results and snapshots come from the shared runtime. No application is
imported or executed, and this module provides no deletion fallback.
"""
from pathlib import Path
import json
import stat
import sys
from types import MappingProxyType

from compact_capture_retention import CompactStore, MAX_RECEIPT_BYTES
from compact_parallel_consumers import CompactCommands
from current_parallel_runner import CurrentParallelRunner
from parallel_reader_scheduler import LOOKUPS, run_schedule
import generated_output_contract as contract
import measure_current_parallel as original
import measure_lazy_suite_ids as q
import measure_maintainer_pair as maintainer


CONTROL_IDS = ('source_guard_success', 'source_guard_refusal', 'detached_expected_nonzero',
               'outer_control_full_receipt', 'measured_original_outcomes')
COMMAND_COUNTS = MappingProxyType({'source_guard_success': 6, 'source_guard_refusal': 10,
    'detached_expected_nonzero': 1, 'outer_control_full_receipt': 1, 'measured_original_outcomes': 3})
SOURCE = 'a' * 40
SCOPE = 'synthetic_output_consumer_validation_not_git_qualification'


def _need(value):
    q.require(value, 'native_consumer_control_failed')


class _Commands(CompactCommands):
    """Logical Git/consumer argv never reaches an OS process launcher."""
    def __init__(self, root, runtime, plans):
        self.root, self.runtime = root, runtime
        self.deadline, self.owners = runtime.work_deadline, []
        self.plans, self.original_bytes = list(plans), []
        self.init_compact(CompactStore(root, self.deadline, api=runtime.api()),
                          runtime.snapshot_reader)

    def run(self, argv, cwd):
        _need(bool(self.plans))
        expected, stdout, stderr, code = self.plans.pop(0)
        _need(tuple(argv) == expected)
        ticket = self.reserve_command(argv, cwd)
        report = self.root / ('command-%04d' % (len(self.owners) + 1))
        owner, native, reads = self.runtime.launch(report, stdout, stderr, exit_code=code)
        _need(owner.result is native and tuple(raw for raw, _ in reads) == (stdout, stderr))
        self.owners.append(owner)
        self.original_bytes.append((stdout, stderr))
        snapshot = native.snapshot
        return self.register_command(ticket, {'returncode': snapshot.root_exit_code,
            'stdout_path': str(native.stdout_path), 'stderr_path': str(native.stderr_path),
            'cleanup_verified': snapshot.cleanup_verified, 'wall_seconds': snapshot.wall_seconds,
            'tree_cpu_seconds': snapshot.tree_cpu_seconds})


def _git(repo, args, stdout=b'', stderr=b'', code=0):
    return (('git', '-C', str(repo), *args), stdout, stderr, code)


def _session(root, runtime, plan_builder):
    root.mkdir()
    captures, repo = root / 'captures', root / 'repo'
    captures.mkdir()
    (repo / '.git').mkdir(parents=True)
    return _Commands(captures, runtime, plan_builder(repo)), repo


def _first(repo, head=SOURCE, status=b''):
    return [_git(repo, ('rev-parse', '--git-common-dir'), b'.git\n'),
            _git(repo, ('rev-parse', 'HEAD'), (head + '\n').encode()),
            _git(repo, ('status', '--porcelain=v1', '--untracked-files=all'), status)]


def _refs(repo):
    refs = ('refs/remotes/origin/main %s\nrefs/remotes/origin/HEAD %s\n' % (SOURCE, SOURCE)).encode()
    return [_git(repo, ('rev-parse', '--is-shallow-repository'), b'false\n'),
            _git(repo, ('for-each-ref', '--format=%(refname) %(objectname)'), refs),
            _git(repo, ('symbolic-ref', 'refs/remotes/origin/HEAD'), b'refs/remotes/origin/main\n')]


def _summary(store, runtime, reserved, retired):
    summary = store.public_summary()
    _need(tuple(summary[key] for key in ('reserved_pairs', 'retired_complete_pairs',
        'pending_pairs', 'receipt_files_written', 'blocked')) ==
        (reserved, retired, reserved - retired, retired * 3, False))
    paths = sorted(store.root.glob('compact-*.json'))
    _need(len(paths) == retired * 3)
    receipts, triplets = [], []
    for ordinal in range(1, reserved + 1):
        digests = []
        for kind in ('eligibility', 'outcome', 'terminal'):
            path = store.root / ('compact-%06d-%s.json' % (ordinal, kind))
            if ordinal > retired:
                _need(not path.exists())
                digests.append(None)
                continue
            # The original snapshot helper deliberately accepts only capture
            # names. Receipts instead use the existing read-only native handle,
            # with coherent native snapshots and no sharing/access changes.
            api = store.api
            handle = api.open(path)
            try:
                before = contract.windows_snapshot(api, handle, MAX_RECEIPT_BYTES,
                                                    path.name, runtime.work_deadline)
                raw = api.read(handle, MAX_RECEIPT_BYTES, runtime.work_deadline)
                after = contract.windows_snapshot(api, handle, MAX_RECEIPT_BYTES,
                                                   path.name, runtime.work_deadline)
                _need(before == after and len(raw) == before.st_size)
            finally:
                api.close(handle)
            receipt = original.unique_json(raw)
            _need(receipt['kind'] == kind and receipt['pair'] == ordinal)
            receipts.append(receipt)
            digests.append(q.digest(raw))
        triplets.append(digests)
    _need(q.digest(json.dumps(triplets, separators=(',', ':'), ensure_ascii=True).encode('ascii')) ==
          summary['receipt_chain_sha256'])
    for receipt in receipts:
        if receipt['kind'] in ('outcome', 'terminal'):
            _need(receipt['first_failure'] is None and receipt['streams'] == [
                {'stream': 'stdout', 'mark': 'verified', 'close': 'verified'},
                {'stream': 'stderr', 'mark': 'verified', 'close': 'verified'}])
        if receipt['kind'] == 'terminal':
            _need(receipt['receipt_authority'] == {'recheck': 'verified', 'close': 'verified'})
    return summary, receipts


def _no_early_retirement(session, count):
    _need(session.pending_helper_pairs == count and
          session.compact.public_summary()['retired_complete_pairs'] == 0 and
          not list(session.root.glob('compact-*.json')))


def _source_success(root, runtime):
    session, repo = _session(root / 'accepted', runtime, lambda repo: _first(repo) + _refs(repo))
    with session.consumer_scope('source_guard') as scope:
        q.first_clean(session, repo, SOURCE, 'seed')
        maintainer.verify_refs(session, repo, source_sha=SOURCE)
        _no_early_retirement(session, 6)
        original.acknowledge_controls(session, scope, 'source_guard')
    _need(not session.plans and session.pending_helper_pairs == 0)
    summary, receipts = _summary(session.compact, runtime, 6, 6)
    _need([row['final_consumer'] for row in receipts if row['kind'] == 'eligibility'] ==
          ['helper_result'] * 6)
    return [summary], ['source_predicates_accepted']


def _retained(session):
    for owner, expected in zip(session.owners, session.original_bytes):
        observed = tuple(session.runtime.snapshot_reader(session.root,
            owner.report_dir.name + '/' + stream + '.bin', q.BUDGET['max_capture_bytes'],
            session.deadline)[0] for stream in ('stdout', 'stderr'))
        _need(observed == expected)


def _source_refusals(root, runtime):
    def changed_refs(repo):
        return [_refs(repo)[0], _git(repo, ('for-each-ref', '--format=%(refname) %(objectname)'),
                                   b'refs/remotes/origin/main wrong-head\n')]
    def dirty(repo):
        return _first(repo, status=b'?? synthetic.txt\n') + [
            _git(repo, ('config', '--get', key), code=1)
            for key in ('core.autocrlf', 'core.eol', 'core.safecrlf')]
    cases = (('wrong_head', lambda repo: _first(repo, head='wrong-head')[:2],
              'wrong_source_head', 2),
             ('changed_refs', changed_refs, 'source_refs_changed', 2),
             ('dirty_status', dirty, 'first_status_not_clean', 6))
    summaries, outcomes = [], []
    for name, plans, reason, count in cases:
        session, repo = _session(root / name, runtime, plans)
        try:
            with session.consumer_scope('source_guard'):
                if name == 'changed_refs':
                    maintainer.verify_refs(session, repo, source_sha=SOURCE)
                else:
                    q.first_clean(session, repo, SOURCE, 'seed')
        except q.Refused as error:
            _need(str(error) == reason)
        else:
            _need(False)
        _need(not session.plans)
        _no_early_retirement(session, count)
        _retained(session)
        before = len(runtime.owners)
        try:
            with session.consumer_scope('refused_retry'):
                session.git(repo, 'rev-parse', 'HEAD')
        except q.Refused as error:
            _need(str(error) == 'compact_retirement_inconclusive')
        else:
            _need(False)
        _need(len(runtime.owners) == before)
        summary, receipts = _summary(session.compact, runtime, count, 0)
        _need(not receipts)
        summaries.append(summary)
        outcomes.append(reason)
    return summaries, outcomes


def _detached(root, runtime):
    session, repo = _session(root / 'detached', runtime,
        lambda repo: [_git(repo, ('symbolic-ref', '-q', 'HEAD'), code=1)])
    with session.consumer_scope('detached') as scope:
        session.run(['git', '-C', str(repo), 'symbolic-ref', '-q', 'HEAD'], repo)
        _no_early_retirement(session, 1)
        original.acknowledge_controls(session, scope, 'detached')
    _need(not session.plans and session.pending_helper_pairs == 0)
    summary, receipts = _summary(session.compact, runtime, 1, 1)
    eligibility = next(row for row in receipts if row['kind'] == 'eligibility')
    _need(eligibility['final_consumer'] == 'helper_result' and
          eligibility['evidence']['result']['category'] == 'detached_head' and
          eligibility['evidence']['result']['returncode'] == 1)
    return [summary], ['detached_head_expected_status_one']


def _outer(root, runtime):
    # This explicitly labeled JSON is child output for the original validator,
    # not observed native metadata and never evidence that these controls ran.
    ids = list(q.DECLARED_CONTROL_IDS)
    fixture = {'schema': 'windows-job-probe-controls-v1', 'status': 'passed',
        'platform': 'win32', 'python': '3.14.4 synthetic fixture', 'optimization_level': 0,
        'files_retained': True, 'process_cleanup_verified': True,
        'declared_control_ids': ids, 'passed_control_ids': ids,
        'planned_count': len(ids), 'passed_count': len(ids), 'failed_count': 0, 'skipped_count': 0,
        'controls': [{'control': control} for control in ids],
        'fixture_label': 'synthetic_consumer_fixture',
        'additional_evidence': {'kept': [True, 'whole receipt', {'ordinal': 7}]}}
    raw = (json.dumps(fixture, sort_keys=True) + '\n').encode()
    def plans(repo):
        return [((sys.executable, str(repo / 'diagnostics/windows_job_probe_controls.py'),
                  '--run', '--report-dir', str(repo / 'synthetic-output-only')), raw, b'', 0)]
    session, repo = _session(root / 'outer', runtime, plans)
    argv = session.plans[0][0]
    with session.consumer_scope('native') as scope:
        result = session.run(argv, repo)
        q.require(result['returncode'] == 0, 'owner_controls_failed')
        q.validate_owner_controls(original.unique_json(scope.records[0]['reads'][0][0]))
        _no_early_retirement(session, 1)
        original.acknowledge_controls(session, scope, 'native')
    _need(not session.plans and session.pending_helper_pairs == 0)
    summary, receipts = _summary(session.compact, runtime, 1, 1)
    eligibility = next(row for row in receipts if row['kind'] == 'eligibility')
    _need(eligibility['final_consumer'] == 'outer_control' and
          eligibility['evidence']['result'] == fixture)
    return [summary], ['full_outer_control_json_retained']


def _measured_case(root, runtime, unexpected):
    root.mkdir()
    evidence = root / 'evidence'
    evidence.mkdir()
    store = CompactStore(evidence, runtime.work_deadline, api=runtime.api())
    captures, temporary = evidence / 'cap1-captures', root / 'temporary'
    captures.mkdir()
    temporary.mkdir()
    clones = (root / 'left', root / 'right')
    for clone in clones:
        (clone / 'tools').mkdir(parents=True)
    module = 'test_alpha'
    clean = b'Ran 3 tests in 0.001s\n\nOK (skipped=1)\n'
    refusal = (b'FAIL: test_synthetic (test_alpha.Example.test_synthetic)\n'
               b'Traceback (most recent call last):\n  synthetic fixture frame\n'
               b'AssertionError: CODE_SET_DATABASE_OPEN_REFUSED:icd10_lookup\n'
               b'Ran 1 test in 0.001s\n\nFAILED (failures=1)\n')
    plans = [(LOOKUPS[0], clean if unexpected else refusal, 1)]
    if not unexpected:
        plans.append((LOOKUPS[1], clean, 0))
    payload = 'synthetic logical payload; never executed'
    before_next = []
    owners = []

    class OwnedFixtureFactory:
        def start(self, argv, *, cwd, env, report_dir):
            _need(bool(plans))
            lookup, stderr, code = plans.pop(0)
            _need(argv == [sys.executable, '-c', payload, str(clones[0] / 'tools'), module, lookup]
                  and cwd == str(clones[0] / 'tools'))
            prior = store.public_summary()
            # start() has reserved the next slot, but its child must not exist
            # until every earlier successful lookup has retired authentically.
            _need(prior['reserved_pairs'] == len(owners) + 1 and
                  prior['retired_complete_pairs'] == len(owners) and
                  prior['receipt_files_written'] == len(owners) * 3)
            before_next.append(prior['retired_complete_pairs'])
            owner, native, reads = runtime.launch(Path(report_dir), b'', stderr, exit_code=code)
            _need(owner.result is native and tuple(raw for raw, _ in reads) == (b'', stderr))
            owners.append(owner)
            return owner

    reference = {(module, lookup): {'module': module, 'lookup': lookup, 'returncode': 0,
        'classification': 'nonreader', 'test_count': 3, 'failures': 0, 'errors': 0,
        'skipped': 1, 'expected_failures': 0, 'screen_clean': True,
        'capture_read_verified': True, 'cleanup_verified': True} for lookup in LOOKUPS}
    if not unexpected:
        reference[(module, LOOKUPS[0])].update(returncode=1, classification='reader',
                                            test_count=1, failures=1, skipped=0)
    runner = CurrentParallelRunner(arm='cap1', modules=(module,), clones=clones,
        capture_root=captures, temporary_root=temporary, payload=payload,
        source_sha=SOURCE, source_manifest_sha256=q.digest(b'synthetic manifest'),
        candidate_sha256=q.digest(b'synthetic candidate'),
        interpreter_sha256=q.digest(Path(sys.executable).read_bytes()),
        deadline=runtime.work_deadline, hard_deadline=runtime.hard_deadline,
        owner_factory=OwnedFixtureFactory(), environment=runtime.environment,
        clock=runtime.clock, compact=store, compact_reference=reference,
        snapshot_reader=runtime.snapshot_reader)
    try:
        result = run_schedule((module,), 1, runner, deadline=runtime.work_deadline,
                              clock=runtime.clock, sleep=runtime.sleep)
    finally:
        clean_owner = runner.cleanup()
    _need(clean_owner is True and not plans)
    rows = runner.attempt_ledger()
    if unexpected:
        _need((result.complete, result.first_error, result.first_error_resolved, result.stop_reason) ==
              (False, (module, 'icd10_lookup'), True, 'unexpected_probe_result'))
        _need(len(rows) == 1 and rows[0]['classification'] == 'error' and
              rows[0]['screen_clean'] is False and runner.pending_capture_slots == 1 and
              runner.first_failure['reason'] == 'capture_screen_failed')
        raw = tuple(runtime.snapshot_reader(captures, 'command-0001/' + name + '.bin',
            q.BUDGET['max_capture_bytes'], runtime.work_deadline)[0] for name in ('stdout', 'stderr'))
        _need(raw == (b'', clean) and before_next == [0])
        summary, receipts = _summary(store, runtime, 1, 0)
        _need(not receipts)
    else:
        _need(result.complete is True and result.first_error is None and
              result.stop_reason is None and not result.unread_pairs and
              [(row.classification, row.unexpected, row.test_count, row.failures) for row in
               result.observations] == [('reader', False, 1, 1), ('nonreader', False, 3, 0)] and
              before_next == [0, 1] and runner.pending_capture_slots == 0)
        summary, receipts = _summary(store, runtime, 2, 2)
        eligibility = [row for row in receipts if row['kind'] == 'eligibility']
        _need([row['final_consumer'] for row in eligibility] == ['measured_pair', 'measured_pair'] and
              [row['evidence']['result'] for row in eligibility] == list(rows))
    return summary


def _measured(root, runtime):
    accepted = _measured_case(root / 'accepted', runtime, False)
    unexpected = _measured_case(root / 'unexpected', runtime, True)
    return [accepted, unexpected], ['reader_expected_status_one', 'nonreader_expected_status_zero',
                                   'retired_before_next_lookup', 'unexpected_probe_result_raw_retained']


def run_consumer_control(control_id, fresh_root, runtime):
    """Run exactly one finite control in an absent fixture directory.

    runtime must supply owned launch, actual native API/snapshot seams and the
    shared owner ledger. Injected portable models are test-only evidence.
    """
    _need(control_id in CONTROL_IDS)
    root = Path(fresh_root)
    _need(root.is_absolute() and '..' not in root.parts and
          not root.exists() and not root.is_symlink() and root.parent.resolve(strict=True) == root.parent)
    for ancestor in (root.parent, *root.parent.parents):
        metadata = ancestor.lstat()
        _need(stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
              and not getattr(metadata, 'st_file_attributes', 0) & 0x400)
    root.mkdir()
    before = len(runtime.owners)
    handlers = {'source_guard_success': _source_success, 'source_guard_refusal': _source_refusals,
                'detached_expected_nonzero': _detached, 'outer_control_full_receipt': _outer,
                'measured_original_outcomes': _measured}
    summaries, outcomes = handlers[control_id](root, runtime)
    commands = len(runtime.owners) - before
    _need(commands == sum(row['reserved_pairs'] for row in summaries) == COMMAND_COUNTS[control_id])
    return {'id': control_id, 'passed': True, 'scope': SCOPE, 'commands': commands,
            'retired_pairs': sum(row['retired_complete_pairs'] for row in summaries),
            'retained_pairs': sum(row['pending_pairs'] for row in summaries),
            'receipt_files': sum(row['receipt_files_written'] for row in summaries),
            'outcomes': outcomes, 'stores': summaries}
