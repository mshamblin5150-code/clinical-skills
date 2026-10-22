"""Synthetic helper/final-consumer seam; no application or native execution."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

import compact_parallel_consumers as subject
import measure_lazy_suite_ids as q
from windows_job_probe import ProbeResult, ProbeSnapshot


class SyntheticStore:
    """Retirement removes only this test's fresh synthetic capture files."""
    def __init__(self, root):
        self.root = root
        self.events = []
        self.retired_reports = []
        self.failure = None
        self.outcome = {'complete': True}

    def reserve(self, root, report, bindings):
        if report.exists():
            raise AssertionError('reservation must precede launch')
        ticket = {'report': report, 'bindings': dict(bindings)}
        self.events.append(('reserve', ticket))
        return ticket

    def register(self, ticket, owner, result, reads):
        if owner.result is not result:
            raise AssertionError('registered another owner result')
        ticket.update(owner=owner, result=result, reads=reads)
        self.events.append(('register', ticket))

    def retire(self, ticket, consumer, evidence):
        self.events.append(('retire', consumer, evidence))
        self.retired_reports.append(ticket['report'].name)
        if self.failure is not None:
            raise self.failure
        if self.outcome.get('complete') is not True:
            return self.outcome
        for stream in ('stdout', 'stderr'):
            Path(getattr(ticket['result'], stream + '_path')).unlink()
        return self.outcome


class SyntheticCommands(subject.CompactCommands):
    def __init__(self, root, store, snapshot_reader=None):
        self.root, self.deadline, self.owners = root, time.monotonic() + 30, []
        self.plans = []
        self.init_compact(store, snapshot_reader or self.read_snapshot)

    @staticmethod
    def read_snapshot(root, relative, limit, deadline):
        return (root / relative).read_bytes(), object()

    def run(self, argv, cwd):
        ticket = self.reserve_command(argv, cwd)
        plan = self.plans.pop(0) if self.plans else {}
        report = self.root / ('command-%04d' % (len(self.owners) + 1))
        report.mkdir()
        paths = [report / (name + '.bin') for name in ('stdout', 'stderr')]
        for path, raw in zip(paths, (plan.get('stdout', b'value\r\n'), plan.get('stderr', b''))):
            path.write_bytes(raw)
        pid = len(self.owners) + 1
        snapshot = ProbeSnapshot(pid, plan.get('code', 0), True, 0, 1, 0.2, 0.3, 1.0, True, 'closed')
        finished = ProbeResult(snapshot, 'completed', str(paths[0]), str(paths[1]), ())
        owner = SimpleNamespace(result=finished, report_dir=report,
            stdout_path=paths[0], stderr_path=paths[1], _info=SimpleNamespace(dwProcessId=pid))
        self.owners.append(owner)
        result = {'returncode': snapshot.root_exit_code, 'stdout': 'UNAUTHENTICATED',
            'stderr': 'UNAUTHENTICATED', 'stdout_path': str(paths[0]), 'stderr_path': str(paths[1]),
            'cleanup_verified': True, 'wall_seconds': 1.0, 'tree_cpu_seconds': 0.5}
        result.update(plan.get('result_updates', {}))
        return self.register_command(ticket, result)


class CompactConsumerControls(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='compact-consumers-')
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.store = SyntheticStore(self.root)
        self.session = SyntheticCommands(self.root, self.store)

    def acknowledge(self, scope, category='validated_helper'):
        return [(record, 'helper_result', subject.helper_evidence(record, category))
                for record in scope.records]

    @contextlib.contextmanager
    def assembled_source(self, name, plans):
        """Real serial chain and store with only owned launch/native I/O replaced."""
        import measure_current_parallel as comparison
        from compact_capture_retention import CompactStore
        from test_compact_capture_retention import FakeNative
        root = self.root / name
        root.mkdir()
        captures, repo = root / 'captures', root / 'repo'
        captures.mkdir()
        (repo / '.git').mkdir(parents=True)
        api = FakeNative()
        deadline = time.monotonic() + 30
        store = CompactStore(captures, deadline, api=api)
        def read_snapshot(root, relative, limit, deadline):
            with (root / relative).open('rb') as stream:
                return stream.read(), api.record(stream.fileno())
        session = comparison.ComparisonSession(captures, deadline, deadline + 10,
            compact=store, snapshot_reader=read_snapshot)
        queue = list(plans)
        def launch(argv, cwd, env, report_dir):
            plan = queue.pop(0)
            if 'args' in plan:
                self.assertEqual(tuple(plan['args']), tuple(argv[3:]))
            else:
                self.assertEqual(tuple(plan['args_prefix']), tuple(argv[3:3 + len(plan['args_prefix'])]))
            report = Path(report_dir)
            self.assertFalse(report.exists())
            report.mkdir()
            stdout, stderr = report / 'stdout.bin', report / 'stderr.bin'
            stdout.write_bytes(plan.get('stdout', b''))
            stderr.write_bytes(plan.get('stderr', b''))
            pid = 71 + len(session.owners)
            snapshot = ProbeSnapshot(pid, plan.get('code', 0), True, 0, 1, 0.2, 0.3, 1.0, True, 'closed')
            owner = SimpleNamespace(report_dir=report, stdout_path=stdout, stderr_path=stderr,
                result=None, _info=SimpleNamespace(dwProcessId=pid), poll=lambda: snapshot)
            def finish(timeout):
                owner.result = ProbeResult(snapshot, 'completed', str(stdout), str(stderr), ())
                return owner.result
            owner.finish = finish
            return owner
        with mock.patch.object(q.WindowsJobProbe, 'start', side_effect=launch), \
                contextlib.redirect_stdout(io.StringIO()):
            yield session, store, api, repo
        self.assertEqual([], queue)

    def test_assembled_first_clean_wrong_head_retains_all_successful_git_output(self):
        plans = [{'args': ('rev-parse', '--git-common-dir'), 'stdout': b'.git\n'},
                 {'args': ('rev-parse', 'HEAD'), 'stdout': b'wrong-head\n'}]
        with self.assembled_source('wrong_head', plans) as (session, store, api, repo):
            with self.assertRaisesRegex(q.Refused, '^wrong_source_head$'):
                with session.consumer_scope('first_clean'):
                    q.first_clean(session, repo, 'expected-head', 'seed')
            self.assertEqual([], api.disposed)
            self.assertEqual(2, session.pending_helper_pairs)
            self.assertTrue(all(owner.stdout_path.exists() for owner in session.owners))
            with self.assertRaisesRegex(q.Refused, '^compact_retirement_inconclusive$'):
                with session.consumer_scope('retry'):
                    session.git(repo, 'rev-parse', 'HEAD')

    def test_assembled_first_clean_dirty_status_preserves_original_refusal_and_all_raw(self):
        plans = [{'args': ('rev-parse', '--git-common-dir'), 'stdout': b'.git\n'},
                 {'args': ('rev-parse', 'HEAD'), 'stdout': b'expected-head\n'},
                 {'args': ('status', '--porcelain=v1', '--untracked-files=all'), 'stdout': b'?? synthetic.txt\n'}]
        plans.extend({'args': ('config', '--get', key), 'code': 1}
                     for key in ('core.autocrlf', 'core.eol', 'core.safecrlf'))
        with self.assembled_source('dirty_status', plans) as (session, store, api, repo):
            with self.assertRaisesRegex(q.Refused, '^first_status_not_clean$'):
                with session.consumer_scope('first_clean'):
                    q.first_clean(session, repo, 'expected-head', 'seed')
            self.assertEqual([], api.disposed)
            self.assertEqual(6, session.pending_helper_pairs)
            self.assertTrue(all(owner.stdout_path.exists() and owner.stderr_path.exists()
                                for owner in session.owners))

    def test_assembled_dirty_status_stays_primary_when_config_admission_is_full(self):
        plans = [{'args': ('synthetic-prelude',)} for _ in range(29)]
        plans.extend([{'args': ('rev-parse', '--git-common-dir'), 'stdout': b'.git\n'},
                      {'args': ('rev-parse', 'HEAD'), 'stdout': b'expected-head\n'},
                      {'args': ('status', '--porcelain=v1', '--untracked-files=all'),
                       'stdout': b'?? synthetic.txt\n'}])
        with self.assembled_source('config_admission', plans) as (session, store, api, repo):
            with self.assertRaisesRegex(q.Refused, '^first_status_not_clean$'):
                with session.consumer_scope('source_context'):
                    for _ in range(29):
                        session.git(repo, 'synthetic-prelude')
                    q.first_clean(session, repo, 'expected-head', 'seed')
            self.assertEqual(32, len(session.owners))
            self.assertEqual(32, session.pending_helper_pairs)
            self.assertEqual([], api.disposed)
            self.assertTrue(all(owner.stdout_path.exists() and owner.stderr_path.exists()
                                for owner in session.owners))

    def test_assembled_verify_refs_changed_ref_retains_all_successful_git_output(self):
        import measure_maintainer_pair as maintainer
        plans = [{'args': ('rev-parse', '--is-shallow-repository'), 'stdout': b'false\n'},
                 {'args': ('for-each-ref', '--format=%(refname) %(objectname)'),
                  'stdout': b'refs/remotes/origin/main wrong-head\n'}]
        with self.assembled_source('changed_refs', plans) as (session, store, api, repo):
            with self.assertRaisesRegex(q.Refused, '^source_refs_changed$'):
                with session.consumer_scope('verify_refs'):
                    maintainer.verify_refs(session, repo, source_sha='a' * 40)
            self.assertEqual([], api.disposed)
            self.assertEqual(2, session.pending_helper_pairs)
            self.assertTrue(all(owner.stdout_path.exists() for owner in session.owners))

    def test_assembled_original_source_predicates_retire_only_after_explicit_completion(self):
        import measure_maintainer_pair as maintainer
        source = 'a' * 40
        refs = ('refs/remotes/origin/main %s\nrefs/remotes/origin/HEAD %s\n' % (source, source)).encode()
        plans = [{'args': ('rev-parse', '--git-common-dir'), 'stdout': b'.git\n'},
                 {'args': ('rev-parse', 'HEAD'), 'stdout': (source + '\n').encode()},
                 {'args': ('status', '--porcelain=v1', '--untracked-files=all')},
                 {'args': ('rev-parse', '--is-shallow-repository'), 'stdout': b'false\n'},
                 {'args': ('for-each-ref', '--format=%(refname) %(objectname)'), 'stdout': refs},
                 {'args': ('symbolic-ref', 'refs/remotes/origin/HEAD'), 'stdout': b'refs/remotes/origin/main\n'}]
        with self.assembled_source('clean_source', plans) as (session, store, api, repo):
            with session.consumer_scope('source_checkpoint') as scope:
                q.first_clean(session, repo, source, 'seed')
                maintainer.verify_refs(session, repo, source_sha=source)
                self.assertEqual([], scope.records)
                self.assertEqual(6, len(scope.git_records))
                self.assertEqual(6, session.pending_helper_pairs)
                self.assertEqual(0, session.pending_helper_capacity_bytes)
                self.assertEqual([], api.disposed)
                session.complete_consumer(scope, [])
            self.assertEqual(['stdout.bin', 'stderr.bin'] * 6, api.disposed)
            self.assertEqual(0, session.pending_helper_pairs)
            self.assertFalse(store.blocked)

    def test_assembled_high_ref_clone_refuses_before_pair_33_without_early_retirement(self):
        import measure_maintainer_pair as maintainer
        source = 'a' * 40
        refs = ['refs/heads/synthetic%02d' % index for index in range(40)]
        plans = [{'args_prefix': ('clone', '--no-local', '--no-hardlinks', '--no-checkout')},
                 {'args': ('-c', 'core.autocrlf=false', 'checkout', '--detach', source)},
                 {'args': ('for-each-ref', '--format=%(refname)'),
                  'stdout': ('\n'.join(refs) + '\n').encode()}]
        plans.extend({'args': ('update-ref', '--no-deref', '-d', ref)} for ref in refs[:29])
        with self.assembled_source('high_ref_clone', plans) as (session, store, api, repo):
            with self.assertRaisesRegex(q.Refused, '^compact_helper_pending_limit$'):
                with session.consumer_scope('source_context'):
                    maintainer.source_context(session, self.root / 'seed', repo, 'baseline', {}, b'',
                                              source_sha=source)
            self.assertEqual(32, len(session.owners))
            self.assertEqual(32, session.pending_helper_pairs)
            self.assertEqual([], api.disposed)
            self.assertTrue(all(owner.stdout_path.exists() and owner.stderr_path.exists()
                                for owner in session.owners))

    def test_git_and_direct_retirement_preserves_original_interleaved_launch_order(self):
        with self.session.consumer_scope('guarded_mixed') as scope:
            self.session.git(self.root, 'synthetic-before')
            self.session.run(['synthetic-direct'], self.root)
            self.session.git_bytes(self.root, 'synthetic-after')
            self.assertEqual(1, len(scope.records))
            self.assertEqual(2, len(scope.git_records))
            self.assertEqual([], self.store.retired_reports)
            self.session.complete_consumer(scope, self.acknowledge(scope))
        self.assertEqual(['command-0001', 'command-0002', 'command-0003'], self.store.retired_reports)

    def test_nested_22_planted_and_8_git_guard_slots_are_counted_until_actual_retirement(self):
        with self.session.consumer_scope('planted') as outer:
            for index in range(22):
                self.session.run(['synthetic-planted', str(index)], self.root)
            with self.session.consumer_scope('nested_guard') as inner:
                for index in range(8):
                    self.session.git(self.root, 'synthetic-guard', str(index))
                self.assertEqual(30, self.session.pending_helper_pairs)
                self.assertEqual(0, self.session.pending_helper_capacity_bytes)
                self.assertEqual(22, len(outer.records))
                self.assertEqual(8, len(inner.git_records))
                self.assertEqual([], self.store.retired_reports)
                self.session.complete_consumer(inner, [])
            self.assertEqual(22, self.session.pending_helper_pairs)
            self.assertTrue(all(owner.stdout_path.exists() for owner in self.session.owners[:22]))
            self.assertEqual(['command-%04d' % index for index in range(23, 31)], self.store.retired_reports)
            self.session.complete_consumer(outer, self.acknowledge(outer))
        self.assertEqual(0, self.session.pending_helper_pairs)

    def test_pending_capacity_rejects_linked_live_capture_and_stops_further_launch(self):
        import os
        with self.assertRaisesRegex(q.Refused, '^compact_helper_capacity_unread$'):
            with self.session.consumer_scope('live_unsafe'):
                self.session.reserve_command(['synthetic-live'], self.root)
                report = self.root / 'command-0001'
                report.mkdir()
                (report / 'stdout.bin').write_bytes(b'fixture')
                os.link(report / 'stdout.bin', report / 'extra-link.bin')
                self.session.pending_helper_capacity_bytes
        self.assertEqual(1, self.session.pending_helper_pairs)
        self.assertEqual([], self.store.retired_reports)
        with self.assertRaisesRegex(q.Refused, '^compact_retirement_inconclusive$'):
            self.session.reserve_command(['synthetic-retry'], self.root)

    def test_pending_capacity_rejects_replaced_previously_seen_report_or_stream(self):
        for kind in ('report', 'stream'):
            with self.subTest(kind=kind):
                root = self.root / kind
                root.mkdir()
                store = SyntheticStore(root)
                session = SyntheticCommands(root, store)
                with self.assertRaisesRegex(q.Refused, '^compact_helper_capacity_unread$'):
                    with session.consumer_scope('live_replaced'):
                        session.reserve_command(['synthetic-live'], root)
                        report = root / 'command-0001'
                        report.mkdir()
                        (report / 'stdout.bin').write_bytes(b'fixture')
                        self.assertEqual(32 * 1024 ** 2 - 7, session.pending_helper_capacity_bytes)
                        if kind == 'report':
                            report.rename(root / 'retained-original-report')
                            report.mkdir()
                        else:
                            (report / 'stdout.bin').rename(report / 'retained-original-stream.bin')
                            (report / 'stdout.bin').write_bytes(b'fixture')
                        session.pending_helper_capacity_bytes
                self.assertEqual(1, session.pending_helper_pairs)
                self.assertEqual([], store.retired_reports)

    def test_direct_helper_reads_exact_bytes_and_waits_for_explicit_final_consumer(self):
        self.session.plans = [{'stdout': b'value\r\nline\r\xff', 'stderr': b'note\r\n'}]
        with self.session.consumer_scope('validated_fixture') as scope:
            result = self.session.run(['synthetic', 'helper'], self.root)
            self.assertEqual('value\nline\n\ufffd', result['stdout'])
            self.assertEqual('note\n', result['stderr'])
            self.assertEqual(['reserve', 'register'], [row[0] for row in self.store.events])
            self.assertTrue(Path(result['stdout_path']).exists())
            self.session.complete_consumer(scope, self.acknowledge(scope))
        self.assertEqual(['reserve', 'register', 'retire'], [row[0] for row in self.store.events])
        self.assertFalse(Path(result['stdout_path']).exists())
        evidence = self.store.events[-1][2]
        self.assertEqual(13, evidence['result']['stdout_bytes'])
        self.assertEqual(6, evidence['result']['stderr_bytes'])
        self.assertTrue(evidence['completed'] and evidence['validated'] and evidence['original_success'])

    def test_git_materializes_text_and_bytes_but_waits_for_guarded_scope_completion(self):
        self.session.plans = [{'stdout': b'text\r\n'}, {'stdout': b'raw\x00\xff\r\n'}]
        with self.session.consumer_scope('outer_helper') as scope:
            self.assertEqual('text\n', self.session.git(self.root, 'synthetic'))
            self.assertEqual(b'raw\x00\xff\r\n', self.session.git_bytes(self.root, 'synthetic'))
            self.assertEqual([], scope.records)
            self.assertEqual(2, len(scope.git_records))
            self.assertEqual(['reserve', 'register'] * 2, [row[0] for row in self.store.events])
            self.assertTrue(all(owner.stdout_path.exists() for owner in self.session.owners))
            self.session.complete_consumer(scope, [])
        self.assertEqual(['reserve', 'register'] * 2 + ['retire'] * 2,
                         [row[0] for row in self.store.events])
        self.assertTrue(all(not owner.stdout_path.exists() for owner in self.session.owners))

    def test_git_success_followed_by_source_predicate_failure_retains_raw(self):
        self.session.plans = [{'stdout': b'wrong-head\n'}]
        with self.assertRaisesRegex(q.Refused, '^wrong_source_head$'):
            with self.session.consumer_scope('source_guard'):
                head = self.session.git(self.root, 'rev-parse', 'HEAD').strip()
                q.require(head == 'expected-head', 'wrong_source_head')
        self.assertEqual(['reserve', 'register'], [row[0] for row in self.store.events])
        self.assertTrue(self.session.owners[0].stdout_path.exists())

    def test_result_copy_with_changed_semantic_text_never_acknowledges_registered_bytes(self):
        with self.assertRaisesRegex(q.Refused, 'compact_command_identity_changed'):
            with self.session.consumer_scope('validated_fixture') as scope:
                result = self.session.run(['synthetic', 'helper'], self.root)
                changed = {**result, 'stdout': 'different validation input'}
                self.session.complete_consumer(scope,
                    [(changed, 'helper_result', self.session.helper_evidence(scope.records[0]))])
        self.assertEqual(['reserve', 'register'], [row[0] for row in self.store.events])
        self.assertTrue(Path(result['stdout_path']).exists())

    def test_real_store_already_owns_helper_root_and_is_not_registered_twice(self):
        from compact_capture_retention import CompactStore
        store = CompactStore(self.root, time.monotonic() + 30, api=object())
        session = SyntheticCommands(self.root, store)
        with session.consumer_scope('empty_fixture') as scope:
            session.complete_consumer(scope, [])
        self.assertFalse(store.blocked)

    def test_malformed_acknowledgment_is_a_finite_refusal_before_any_retirement(self):
        with self.assertRaisesRegex(q.Refused, '^compact_consumer_invalid$'):
            with self.session.consumer_scope('validated_fixture') as scope:
                self.session.run(['synthetic', 'first'], self.root)
                self.session.run(['synthetic', 'second'], self.root)
                acknowledgments = self.acknowledge(scope)
                acknowledgments[1] = (scope.records[1], 'helper_result')
                self.session.complete_consumer(scope, acknowledgments)
        self.assertNotIn('retire', [row[0] for row in self.store.events])
        self.assertTrue(all(owner.stdout_path.exists() for owner in self.session.owners))

    def test_unknown_direct_command_refuses_before_reservation_or_launch(self):
        with self.assertRaisesRegex(q.Refused, '^compact_consumer_unacknowledged$'):
            self.session.run(['synthetic', 'unknown'], self.root)
        self.assertEqual([], self.store.events)
        self.assertEqual([], self.session.owners)

    def test_git_wrappers_require_enclosing_scope_before_any_reservation(self):
        for method in ('git', 'git_bytes'):
            with self.subTest(method=method):
                root = self.root / method
                root.mkdir()
                store = SyntheticStore(root)
                session = SyntheticCommands(root, store)
                with self.assertRaisesRegex(q.Refused, '^compact_consumer_unacknowledged$'):
                    getattr(session, method)(root, 'synthetic')
                self.assertEqual([], store.events)
                self.assertEqual([], session.owners)

    def test_nested_scope_keeps_parent_raw_until_its_own_acknowledgment(self):
        with self.session.consumer_scope('parent_fixture') as parent:
            outer = self.session.run(['synthetic', 'parent'], self.root)
            with self.session.consumer_scope('detached_guard') as guard:
                self.session.plans = [{'stdout': b'', 'code': 1}]
                inner = self.session.run(['git', 'symbolic-ref', '-q', 'HEAD'], self.root)
                self.session.complete_consumer(guard, self.acknowledge(guard, 'detached_head'))
            self.assertTrue(Path(outer['stdout_path']).exists())
            self.assertFalse(Path(inner['stdout_path']).exists())
            self.assertEqual([outer], [record['result'] for record in parent.records])
            copied_result = {**outer}
            self.session.complete_consumer(parent, [(copied_result, 'helper_result',
                self.session.helper_evidence(parent.records[0]))])
        self.assertFalse(Path(outer['stdout_path']).exists())

    def test_missing_duplicate_reordered_and_unknown_selections_preserve_every_raw_pair(self):
        for case in ('missing', 'duplicate', 'reordered', 'unknown'):
            with self.subTest(case=case):
                root = self.root / case
                root.mkdir()
                store = SyntheticStore(root)
                session = SyntheticCommands(root, store)
                with self.assertRaises(q.Refused):
                    with session.consumer_scope('validated_fixture') as scope:
                        session.run(['synthetic', 'one'], root)
                        session.run(['synthetic', 'two'], root)
                        entries = [(record, 'helper_result', session.helper_evidence(record))
                                   for record in scope.records]
                        if case == 'missing': entries.pop()
                        if case == 'duplicate': entries[1] = entries[0]
                        if case == 'reordered': entries.reverse()
                        if case == 'unknown': entries[1] = (object(), 'helper_result', entries[1][2])
                        session.complete_consumer(scope, entries)
                self.assertNotIn('retire', [row[0] for row in store.events])
                self.assertTrue(all(owner.stdout_path.exists() and owner.stderr_path.exists()
                                    for owner in session.owners))

    def test_original_validator_failure_is_primary_and_blocks_later_launches(self):
        primary = AssertionError('synthetic original validator failure')
        with self.assertRaises(AssertionError) as raised:
            with self.session.consumer_scope('validated_fixture'):
                result = self.session.run(['synthetic', 'helper'], self.root)
                raise primary
        self.assertIs(primary, raised.exception)
        self.assertNotIn('retire', [row[0] for row in self.store.events])
        self.assertTrue(Path(result['stdout_path']).exists())
        with self.assertRaisesRegex(q.Refused, '^compact_retirement_inconclusive$'):
            self.session.git(self.root, 'next')
        self.assertEqual(1, len(self.session.owners))

    def test_unacknowledged_scope_never_infers_success_from_zero_exit(self):
        with self.assertRaisesRegex(q.Refused, '^compact_consumer_unacknowledged$'):
            with self.session.consumer_scope('unvalidated_fixture'):
                result = self.session.run(['synthetic', 'successful_process'], self.root)
        self.assertEqual(0, result['returncode'])
        self.assertTrue(Path(result['stdout_path']).exists())
        self.assertNotIn('retire', [row[0] for row in self.store.events])

    def test_git_failure_keeps_original_refusal_and_raw_evidence(self):
        self.session.plans = [{'code': 1, 'stdout': b'', 'stderr': b'synthetic failure'}]
        with self.assertRaisesRegex(q.Refused, '^git_verification_failed$'):
            with self.session.consumer_scope('source_guard'):
                self.session.git_bytes(self.root, 'synthetic')
        self.assertTrue(self.session.owners[0].stderr_path.exists())
        self.assertNotIn('retire', [row[0] for row in self.store.events])

    def test_disposal_exception_stops_without_retry_and_preserves_primary_error(self):
        self.store.failure = RuntimeError('synthetic disposition failure')
        with self.assertRaises(RuntimeError) as raised:
            with self.session.consumer_scope('validated_fixture') as scope:
                self.session.run(['synthetic', 'one'], self.root)
                self.session.run(['synthetic', 'two'], self.root)
                self.session.complete_consumer(scope, self.acknowledge(scope))
        self.assertIs(self.store.failure, raised.exception)
        with self.assertRaisesRegex(q.Refused, '^compact_retirement_inconclusive$'):
            self.session.git(self.root, 'next')
        self.assertEqual(1, sum(row[0] == 'retire' for row in self.store.events))
        self.assertTrue(all(owner.stdout_path.exists() for owner in self.session.owners))
        self.assertEqual(2, self.session.pending_helper_pairs)

    def test_inconclusive_disposition_outcome_stops_before_retiring_next_pair(self):
        self.store.outcome = {'complete': False, 'retention': 'uncertain'}
        with self.assertRaisesRegex(q.Refused, '^compact_retirement_inconclusive$'):
            with self.session.consumer_scope('validated_fixture') as scope:
                self.session.run(['synthetic', 'one'], self.root)
                self.session.run(['synthetic', 'two'], self.root)
                self.session.complete_consumer(scope, self.acknowledge(scope))
        self.assertEqual(1, sum(row[0] == 'retire' for row in self.store.events))
        self.assertTrue(all(owner.stdout_path.exists() for owner in self.session.owners))
        self.assertEqual(2, self.session.pending_helper_pairs)

    def test_changed_owner_result_refuses_before_any_disposal(self):
        with self.assertRaisesRegex(q.Refused, '^compact_command_identity_changed$'):
            with self.session.consumer_scope('validated_fixture') as scope:
                self.session.run(['synthetic', 'helper'], self.root)
                owner = self.session.owners[0]
                owner.result = SimpleNamespace(**vars(owner.result))
                self.session.complete_consumer(scope, self.acknowledge(scope))
        self.assertNotIn('retire', [row[0] for row in self.store.events])
        self.assertTrue(self.session.owners[0].stdout_path.exists())

    def test_wrong_result_path_never_registers_an_owner_capture(self):
        self.session.plans = [{'result_updates': {'stdout_path': str(self.root / 'unowned.bin')}}]
        with self.assertRaisesRegex(q.Refused, '^compact_command_identity_changed$'):
            with self.session.consumer_scope('validated_fixture'):
                self.session.run(['synthetic', 'helper'], self.root)
        self.assertEqual(['reserve'], [row[0] for row in self.store.events])
        self.assertTrue(self.session.owners[0].stdout_path.exists())

    def test_snapshot_read_failure_retains_raw_and_never_registers_partial_pair(self):
        primary = OSError('synthetic snapshot failure')
        def fail_read(*args):
            raise primary
        session = SyntheticCommands(self.root, self.store, snapshot_reader=fail_read)
        with self.assertRaises(OSError) as raised:
            with session.consumer_scope('validated_fixture'):
                session.run(['synthetic', 'helper'], self.root)
        self.assertIs(primary, raised.exception)
        self.assertEqual(['reserve'], [row[0] for row in self.store.events])
        self.assertTrue(session.owners[0].stdout_path.exists())

    def test_pending_cap_refuses_before_a_thirty_third_helper_launch(self):
        with self.assertRaisesRegex(q.Refused, '^compact_helper_pending_limit$'):
            with self.session.consumer_scope('bounded_fixture'):
                for index in range(33):
                    self.session.run(['synthetic', str(index)], self.root)
        self.assertEqual(32, len(self.session.owners))
        self.assertEqual(32, sum(row[0] == 'reserve' for row in self.store.events))
        self.assertNotIn('retire', [row[0] for row in self.store.events])

    def test_pending_capacity_reserves_only_remaining_live_stream_growth(self):
        with self.assertRaisesRegex(q.Refused, '^compact_consumer_unacknowledged$'):
            with self.session.consumer_scope('incomplete_fixture'):
                self.session.reserve_command(['synthetic', 'live'], self.root)
                self.assertEqual(1, self.session.pending_helper_pairs)
                self.assertEqual(32 * 1024 ** 2, self.session.pending_helper_capacity_bytes)
                report = self.root / 'command-0001'
                report.mkdir()
                (report / 'stdout.bin').write_bytes(b'0123456789abcdef')
                self.assertEqual(32 * 1024 ** 2 - 16, self.session.pending_helper_capacity_bytes)

    def test_real_store_registers_and_retires_authentic_owner_contract_with_synthetic_native_api(self):
        from compact_capture_retention import CompactStore
        from test_compact_capture_retention import FakeNative
        api = FakeNative()
        store = CompactStore(self.root, time.monotonic() + 30, api=api)
        def read_snapshot(root, relative, limit, deadline):
            path = root / relative
            with path.open('rb') as stream:
                return stream.read(), api.record(stream.fileno())
        session = SyntheticCommands(self.root, store, snapshot_reader=read_snapshot)
        with session.consumer_scope('validated_fixture') as scope:
            result = session.run(['synthetic', 'helper'], self.root)
            self.assertEqual('value\n', result['stdout'])
            session.complete_consumer(scope,
                [(scope.records[0], 'helper_result', session.helper_evidence(scope.records[0]))])
        self.assertFalse(store.blocked)
        self.assertEqual(['stdout.bin', 'stderr.bin'], api.disposed)
        self.assertEqual(3, len(list(self.root.glob('compact-*.json'))))

    def test_mutated_returned_result_cannot_acknowledge_unchanged_registered_bytes(self):
        with self.assertRaisesRegex(q.Refused, '^compact_command_identity_changed$'):
            with self.session.consumer_scope('validated_fixture') as scope:
                result = self.session.run(['synthetic', 'helper'], self.root)
                result['stdout'] = 'not the bytes validated by the capture reader'
                self.session.complete_consumer(scope, self.acknowledge(scope))
        self.assertNotIn('retire', [row[0] for row in self.store.events])
        self.assertTrue(self.session.owners[0].stdout_path.exists())

    def test_assembled_session_preserves_observer_and_probe_reopens_before_real_store_retirement(self):
        import measure_current_parallel as comparison
        from compact_capture_retention import CompactStore
        from test_compact_capture_retention import FakeNative
        api = FakeNative()
        deadline = time.monotonic() + 30
        store = CompactStore(self.root, deadline, api=api)
        observations = io.StringIO()
        def read_snapshot(root, relative, limit, deadline):
            # The inherited observer must already have reopened the raw pair.
            event = json.loads(observations.getvalue().splitlines()[0])
            self.assertEqual('diagnostic_child_observed', event['event'])
            self.assertTrue(event['summary_read'])
            path = root / relative
            with path.open('rb') as stream:
                return stream.read(), api.record(stream.fileno())
        session = comparison.ComparisonSession(self.root, deadline, deadline + 10,
            compact=store, snapshot_reader=read_snapshot)
        session.phase = 'temp'
        def launch(argv, cwd, env, report_dir):
            report = Path(report_dir)
            self.assertFalse(report.exists())
            report.mkdir()
            stdout, stderr = report / 'stdout.bin', report / 'stderr.bin'
            stdout.write_bytes(b'')
            stderr.write_bytes(b'Ran 1 test in 0.001s\r\n\r\nOK\r\n')
            snapshot = ProbeSnapshot(71, 0, True, 0, 1, 0.2, 0.3, 1.0, True, 'closed')
            owner = SimpleNamespace(report_dir=report, stdout_path=stdout, stderr_path=stderr,
                result=None, _info=SimpleNamespace(dwProcessId=71), poll=lambda: snapshot)
            def finish(timeout):
                owner.result = ProbeResult(snapshot, 'completed', str(stdout), str(stderr), ())
                return owner.result
            owner.finish = finish
            return owner
        with mock.patch.object(q.WindowsJobProbe, 'start', side_effect=launch), \
                contextlib.redirect_stdout(observations):
            with session.consumer_scope('synthetic_probe') as scope:
                result = session.run(['synthetic', 'probe'], self.root)
                self.assertEqual([], api.disposed)
                verdict = q.verify_probe(result, 1, q.LOOKUPS[0])
                self.assertTrue(verdict['valid'])
                session.complete_consumer(scope,
                    [(scope.records[0], 'helper_result', session.helper_evidence(scope.records[0]))])
        self.assertEqual(['stdout.bin', 'stderr.bin'], api.disposed)
        self.assertEqual(1, session.command_attempts)
        self.assertTrue(session.cleanup())

    def test_unknown_consumer_or_false_envelope_later_in_batch_prevents_all_disposal(self):
        for case in ('unknown_consumer', 'false_validation'):
            with self.subTest(case=case):
                root = self.root / case
                root.mkdir()
                store = SyntheticStore(root)
                session = SyntheticCommands(root, store)
                with self.assertRaisesRegex(q.Refused, '^compact_consumer_invalid$'):
                    with session.consumer_scope('validated_fixture') as scope:
                        session.run(['synthetic', 'one'], root)
                        session.run(['synthetic', 'two'], root)
                        entries = [(record, 'helper_result', session.helper_evidence(record))
                                   for record in scope.records]
                        if case == 'unknown_consumer':
                            entries[1] = (entries[1][0], 'unknown', entries[1][2])
                        else:
                            entries[1][2]['validated'] = False
                        session.complete_consumer(scope, entries)
                self.assertNotIn('retire', [row[0] for row in store.events])

    def test_reservation_freezes_only_known_bindings_and_exact_logical_command(self):
        self.session.compact_bindings = {'source_sha': 'a' * 40, 'payload_sha256': 'b' * 64}
        with self.session.consumer_scope('validated_fixture') as scope:
            self.session.run(['synthetic', 'helper'], self.root)
            bindings = self.store.events[0][1]['bindings']
            self.session.compact_bindings['source_sha'] = 'c' * 40
            self.assertEqual('a' * 40, bindings['source_sha'])
            self.assertEqual({'source_sha', 'payload_sha256', 'command_token'}, set(bindings))
            self.assertEqual(64, len(bindings['command_token']))
            self.session.complete_consumer(scope, self.acknowledge(scope))

    def test_real_store_accepts_expected_detached_head_nonzero_only_after_named_validation(self):
        from compact_capture_retention import CompactStore
        from test_compact_capture_retention import FakeNative
        api = FakeNative()
        store = CompactStore(self.root, time.monotonic() + 30, api=api)
        def read_snapshot(root, relative, limit, deadline):
            with (root / relative).open('rb') as stream:
                return stream.read(), api.record(stream.fileno())
        session = SyntheticCommands(self.root, store, snapshot_reader=read_snapshot)
        session.plans = [{'code': 1, 'stdout': b''}]
        with session.consumer_scope('detached_guard') as scope:
            result = session.run(['git', '-C', str(self.root), 'symbolic-ref', '-q', 'HEAD'], self.root)
            self.assertEqual(1, result['returncode'])
            self.assertEqual([], api.disposed)
            session.complete_consumer(scope, [(scope.records[0], 'helper_result',
                session.helper_evidence(scope.records[0], 'detached_head'))])
        self.assertEqual(['stdout.bin', 'stderr.bin'], api.disposed)
        self.assertFalse(store.blocked)


if __name__ == '__main__':
    unittest.main()
