"""Explicit final consumers for new comparison helper captures only.

Generic command completion registers authenticated bytes but never disposes them.
The original helper validator and its trailing guard must complete before its
caller acknowledges every direct result. Git returns materialized bytes/text but
keeps raw evidence until its enclosing source predicate and guard are complete.
Unknown, interrupted, or inconclusive consumption stops admission.
"""
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
import stat

import generated_output_contract as contract
import measure_lazy_suite_ids as q
import measure_reader_attribution as reader


MAX_PENDING_HELPER_PAIRS = 32
CONSUMERS = frozenset(('helper_result', 'planted_method', 'outer_control'))


def _directory_identity(path):
    metadata = path.lstat()
    q.require(stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
              and not getattr(metadata, 'st_file_attributes', 0) & 0x400
              and path.resolve(strict=True) == path, 'compact_helper_capacity_unread')
    return metadata.st_dev, metadata.st_ino


def helper_evidence(record, category='validated_helper'):
    """Hashes describe the registered raw bytes, never the decoded result text."""
    reads = record['reads']
    result = {'category': category, 'returncode': record['result']['returncode']}
    for stream, (raw, _) in zip(('stdout', 'stderr'), reads):
        result[stream + '_bytes'] = len(raw)
        result[stream + '_sha256'] = q.digest(raw)
    return {'completed': True, 'validated': True, 'original_success': True, 'result': result}


@dataclass(eq=False)
class _Scope:
    session: object
    name: str
    records: list = field(default_factory=list)
    git_records: list = field(default_factory=list)
    completed: bool = False


@dataclass(eq=False)
class _Command:
    ticket: object
    ordinal: int
    report: Path
    scope: object
    record: dict
    git: bool
    git_materialized: bool = False
    owner: object = None
    native_result: object = None
    reads: object = None
    report_identity: object = None
    stream_identities: dict = field(default_factory=dict)


class CompactCommands:
    """Mixin preceding the original serial checkpoint session in its MRO."""

    helper_evidence = staticmethod(helper_evidence)

    def init_compact(self, store=None, snapshot_reader=None):
        self.compact = store
        self.compact_bindings = {}
        self._compact_snapshot_reader = snapshot_reader or contract.read_owned_capture_snapshot
        self._compact_pending = []
        self._compact_scopes = []
        self._compact_git = False
        self._compact_failure = None
        if store is not None:
            q.require(store.root == self.root, 'compact_capture_root_invalid')
            self._compact_root_identity = _directory_identity(self.root)

    @property
    def pending_helper_pairs(self):
        """Reserved slots are released only by verified retirement."""
        return len(self._compact_pending)

    @property
    def pending_helper_capacity_bytes(self):
        """Remaining live growth only; existing closed bytes reduce actual free space."""
        if self.compact is None:
            return 0
        try:
            self._compact_ready()
            q.require(_directory_identity(self.root) == self._compact_root_identity,
                      'compact_helper_capacity_unread')
            remaining = 0
            for command in self._compact_pending:
                if command.owner is not None:
                    continue
                try:
                    identity = _directory_identity(command.report)
                except FileNotFoundError:
                    q.require(command.report_identity is None, 'compact_helper_capacity_unread')
                    remaining += 2 * q.BUDGET['max_capture_bytes']
                    continue
                q.require(command.report_identity in (None, identity), 'compact_helper_capacity_unread')
                command.report_identity = identity
                for stream in ('stdout', 'stderr'):
                    try:
                        metadata = (command.report / (stream + '.bin')).lstat()
                    except FileNotFoundError:
                        q.require(stream not in command.stream_identities, 'compact_helper_capacity_unread')
                        remaining += q.BUDGET['max_capture_bytes']
                        continue
                    identity = metadata.st_dev, metadata.st_ino
                    q.require(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1
                              and not getattr(metadata, 'st_file_attributes', 0) & 0x400
                              and 0 <= metadata.st_size <= q.BUDGET['max_capture_bytes']
                              and command.stream_identities.get(stream, identity) == identity,
                              'compact_helper_capacity_unread')
                    command.stream_identities[stream] = identity
                    remaining += q.BUDGET['max_capture_bytes'] - metadata.st_size
            return remaining
        except BaseException as error:
            self._compact_stop(error)
            raise

    def _compact_stop(self, error):
        if self._compact_failure is None:
            self._compact_failure = error

    def _compact_ready(self):
        q.require(self._compact_failure is None, 'compact_retirement_inconclusive')

    def reserve_command(self, argv, cwd):
        if self.compact is None:
            return None
        try:
            self._compact_ready()
            q.require(self._compact_scopes
                      and not self._compact_scopes[-1].completed, 'compact_consumer_unacknowledged')
            q.require(len(self._compact_pending) < MAX_PENDING_HELPER_PAIRS,
                      'compact_helper_pending_limit')
            q.require(all(command.owner is not None for command in self._compact_pending),
                      'compact_command_incomplete')
            ordinal = len(self.owners) + 1
            report = self.root / ('command-%04d' % ordinal)
            bindings = {**self.compact_bindings,
                        'command_token': reader.token([list(argv), str(cwd)])}
            ticket = self.compact.reserve(self.root, report, bindings)
            scope = self._compact_scopes[-1]
            record = {'argv': tuple(argv), 'cwd': Path(cwd), 'ticket': ticket,
                      'result': None, 'reads': None}
            self._compact_pending.append(_Command(ticket, ordinal, report, scope, record, self._compact_git))
            return ticket
        except BaseException as error:
            self._compact_stop(error)
            raise

    def _compact_command(self, selected):
        matches = []
        for command in self._compact_pending:
            record = command.record
            if selected is command.ticket or selected is record:
                matches.append(command)
            elif type(selected) is dict and record['result'] is not None:
                try:
                    if (type(selected.get('returncode')) is int
                            and selected['returncode'] == record['result']['returncode']
                            and selected.get('cleanup_verified') is True
                            and all(type(selected.get(stream)) is str
                                    and selected[stream] == reader.original_text(command.reads[index][0])
                                    for index, stream in enumerate(('stdout', 'stderr')))
                            and all(Path(selected[key]) == Path(record['result'][key])
                                    for key in ('stdout_path', 'stderr_path'))):
                        matches.append(command)
                except (KeyError, TypeError, ValueError):
                    pass
        q.require(len(matches) == 1, 'compact_command_identity_changed')
        return matches[0]

    def _compact_bind(self, command, result):
        q.require(len(self.owners) >= command.ordinal, 'compact_command_identity_changed')
        owner = self.owners[command.ordinal - 1]
        native = owner.result
        q.require(native is not None and (command.owner is None or command.owner is owner)
                  and (command.native_result is None or command.native_result is native)
                  and not any(owner is item for item in self.owners[:command.ordinal - 1]),
                  'compact_command_identity_changed')
        snapshot = native.snapshot
        q.require(native.reason == 'completed' and snapshot.state == 'closed'
                  and type(snapshot.root_pid) is int and snapshot.root_pid > 0
                  and snapshot.root_pid == owner._info.dwProcessId
                  and Path(owner.report_dir) == command.report
                  and snapshot.cleanup_verified is True and snapshot.root_reaped is True
                  and snapshot.active_processes == 0
                  and type(result.get('returncode')) is int
                  and result['returncode'] == snapshot.root_exit_code
                  and result.get('cleanup_verified') is True, 'compact_command_identity_changed')
        for stream in ('stdout', 'stderr'):
            key = stream + '_path'
            q.require(Path(result[key]) == Path(getattr(native, key))
                      == Path(getattr(owner, key)) == command.report / (stream + '.bin'),
                      'compact_command_identity_changed')
        if command.reads is not None:
            q.require(command.record['reads'] is command.reads
                      and all(result[stream] == reader.original_text(command.reads[index][0])
                              for index, stream in enumerate(('stdout', 'stderr'))),
                      'compact_command_identity_changed')
        return owner, native

    def register_command(self, ticket, result):
        if self.compact is None:
            return result
        try:
            self._compact_ready()
            command = self._compact_command(ticket)
            q.require(command.owner is None and len(self.owners) == command.ordinal,
                      'compact_command_identity_changed')
            owner, native = self._compact_bind(command, result)
            reads = tuple(self._compact_snapshot_reader(self.root,
                '%s/%s.bin' % (command.report.name, stream), q.BUDGET['max_capture_bytes'],
                self.deadline) for stream in ('stdout', 'stderr'))
            q.require(all(type(raw) is bytes and len(raw) <= q.BUDGET['max_capture_bytes']
                          for raw, _ in reads), 'compact_command_identity_changed')
            self.compact.register(ticket, owner, native, reads)
            result = {**result, 'stdout': reader.original_text(reads[0][0]),
                      'stderr': reader.original_text(reads[1][0])}
            command.owner, command.native_result = owner, native
            command.reads = reads
            command.record.update(result=result, reads=reads)
            records = command.scope.git_records if command.git else command.scope.records
            records.append(command.record)
            return result
        except BaseException as error:
            self._compact_stop(error)
            raise

    def begin_consumer(self, name):
        self._compact_ready()
        q.require(type(name) is str and 0 < len(name) <= 80, 'compact_consumer_invalid')
        scope = _Scope(self, name)
        self._compact_scopes.append(scope)
        return scope

    @contextmanager
    def consumer_scope(self, name):
        scope = self.begin_consumer(name)
        try:
            yield scope
            q.require(scope.completed or self.compact is None, 'compact_consumer_unacknowledged')
        except BaseException as error:
            self._compact_stop(error)
            raise
        finally:
            if self._compact_scopes and self._compact_scopes[-1] is scope:
                self._compact_scopes.pop()

    def complete_consumer(self, scope, acknowledgments):
        if self.compact is None:
            scope.completed = True
            return
        try:
            self._compact_ready()
            q.require(scope.session is self and self._compact_scopes
                      and self._compact_scopes[-1] is scope and not scope.completed,
                      'compact_consumer_invalid')
            pending = [command for command in self._compact_pending if command.scope is scope]
            expected = [command for command in pending if not command.git]
            q.require(type(acknowledgments) in (list, tuple)
                      and len(acknowledgments) == len(expected), 'compact_consumer_unacknowledged')
            q.require(all(type(item) in (list, tuple) and len(item) == 3
                          and type(item[1]) is str for item in acknowledgments),
                      'compact_consumer_invalid')
            selected = [self._compact_command(item[0]) for item in acknowledgments]
            q.require(selected == expected, 'compact_consumer_unacknowledged')
            direct = {command: (consumer, evidence)
                      for command, (_, consumer, evidence) in zip(selected, acknowledgments)}
            # Scope completion is the caller's explicit acknowledgment that the
            # original source predicates and trailing guard also accepted Git's
            # materialized outputs. Exit zero alone never reaches this boundary.
            batch = []
            for command in pending:
                if command.git:
                    q.require(command.git_materialized, 'compact_consumer_unacknowledged')
                    consumer, evidence = 'helper_result', helper_evidence(command.record)
                else:
                    consumer, evidence = direct[command]
                batch.append((command, consumer, evidence))
            for command, consumer, evidence in batch:
                q.require(consumer in CONSUMERS and type(evidence) is dict
                          and set(evidence) == {'completed', 'validated', 'original_success', 'result'}
                          and all(evidence[key] is True for key in
                                  ('completed', 'validated', 'original_success'))
                          and type(evidence['result']) is dict, 'compact_consumer_invalid')
                self._compact_bind(command, command.record['result'])
            # Pending commands preserve original launch order across both kinds.
            for command, consumer, evidence in batch:
                outcome = self.compact.retire(command.ticket, consumer, evidence)
                q.require(type(outcome) is dict and outcome.get('complete') is True,
                          'compact_retirement_inconclusive')
                self._compact_pending.remove(command)
            scope.completed = True
        except BaseException as error:
            self._compact_stop(error)
            raise

    def _compact_git_return(self, repo, args, raw):
        try:
            self._compact_ready()
            q.require(not self._compact_git, 'compact_consumer_invalid')
            self._compact_git = True
            result = self.run(['git', '-C', str(repo), *args], repo)
            q.require(result['returncode'] == 0, 'git_verification_failed')
            command = self._compact_command(result)
            self._compact_bind(command, result)
            # Materialization is not source validation. Its raw pair stays pending
            # until the caller completes the enclosing guarded consumer scope.
            returned = command.record['reads'][0][0] if raw else result['stdout']
            command.git_materialized = True
            return returned
        except BaseException as error:
            self._compact_stop(error)
            raise
        finally:
            self._compact_git = False

    def git(self, repo, *args):
        if self.compact is None:
            return super().git(repo, *args)
        return self._compact_git_return(repo, args, False)

    def git_bytes(self, repo, *args):
        if self.compact is None:
            return super().git_bytes(repo, *args)
        return self._compact_git_return(repo, args, True)
