"""Per-launch ownership adapter for the fixed-source reader comparison.

The driver authenticates source inventories before scheduling. This adapter binds
those identities to each fresh process and retains all attempts, including failed
starts. Native ownership is not filesystem isolation; polling is not a hard byte
quota. No application imports, helper launches, or source scans occur here.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import stat
import sys
import time

from generated_output_contract import read_owned_capture
from parallel_reader_capture import analyze_capture
from parallel_reader_diagnostics import SAFE_CHILD_TYPES, safe_exception
from parallel_reader_scheduler import LOOKUPS, Observation
from windows_job_probe import WindowsJobProbe


MAX_CAPTURE_BYTES = 16 * 1024 * 1024
MINIMUM_FREE_BYTES = 1024 * 1024 * 1024
COUNTS = ("test_count", "failures", "errors", "skipped", "expected_failures")
LEDGER_KEYS = frozenset({
    "arm", "module_index", "pair_index", "module", "lookup", "lane", "command_ordinal",
    "pair_token", "clone_root_token", "source_sha", "source_manifest_sha256",
    "candidate_sha256", "payload_sha256", "interpreter_sha256", "completion", "classification",
    "reason", "returncode", "root_identity_verified", "total_processes", "cleanup_verified",
    "root_reaped", "active_processes", "screen_clean", "capture_read_verified", "call_wall_seconds",
    "owned_wall_seconds", "tree_cpu_seconds", "analysis_seconds", "stdout_bytes", "stderr_bytes",
    "stdout_sha256", "stderr_sha256", *COUNTS,
})
FIRST_FAILURE_REASONS = frozenset({
    "launch_failed", "launch_cancelled", "completion_failed", "cleanup_unverified",
    "capture_screen_failed", "work_deadline_exhausted", "directory_identity_invalid",
    "directory_identity_changed", "owner_capture_identity_changed", "owner_result_identity_changed",
    "owner_pid_changed", "capture_stream_unsafe", "capture_stream_identity_changed",
    "capture_limit_exceeded", "disk_reserve_exhausted",
    "live_resource_unread", "unavailable",
    "compact_retirement_inconclusive", "compact_reference_changed", "compact_pending_pair_limit",
})


class RunnerRefused(RuntimeError):
    """Only a finite, caller-selected category, never native exception text."""


def _require(condition, category):
    if not condition:
        raise RunnerRefused(category)


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _token(parts):
    return _digest(json.dumps(parts, separators=(",", ":"), ensure_ascii=True).encode())


def _metric(value):
    return value if type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1e9 else None


def _count(value):
    return value if type(value) is int and 0 <= value <= 1000000 else None


def _directory(path):
    _require(isinstance(path, Path) and path.is_absolute() and ".." not in path.parts,
             "directory_identity_invalid")
    for component in (path, *path.parents):
        item = component.lstat()
        _require(stat.S_ISDIR(item.st_mode) and not stat.S_ISLNK(item.st_mode)
                 and not getattr(item, "st_file_attributes", 0) & 0x400,
                 "directory_identity_invalid")
    _require(path.resolve(strict=True) == path, "directory_identity_invalid")
    item = path.lstat()
    return os.path.normcase(str(path)), item.st_dev, item.st_ino


@dataclass(frozen=True)
class LaunchRecord:
    arm: str
    module_index: int
    pair_index: int
    module: str
    lookup: str
    lane: int
    command_ordinal: int
    pair_token: str
    clone_root_token: str
    source_sha: str
    source_manifest_sha256: str
    candidate_sha256: str
    payload_sha256: str
    interpreter_sha256: str
    clone_root: Path
    report_dir: Path
    stdout_path: Path
    stderr_path: Path
    temporary: Path
    launched_at: float


class CurrentParallelRunner:
    """One coordinator, at most two specific owners, no shared last-owner slot.

    clones are authenticated full clones supplied by the driver. The public
    ledger excludes filesystem paths and native messages. LaunchRecord is a
    private handle, not a public receipt. Synthetic tests may inject the native
    owner boundary, clock, disk observation, and coherent capture-reader seam.
    """
    def __init__(self, *, arm, modules, clones, capture_root, temporary_root,
                 payload, source_sha, source_manifest_sha256, candidate_sha256,
                 interpreter_sha256, deadline, hard_deadline,
                 owner_factory=WindowsJobProbe, executable=sys.executable,
                 environment=None, clock=time.monotonic,
                 disk_usage=shutil.disk_usage, capture_reader=read_owned_capture,
                 resource_check=None, compact=None, compact_reference=None, snapshot_reader=None):
        self.arm, self.modules, self.clones = arm, tuple(modules), tuple(map(Path, clones))
        self.capture_root, self.temporary_root = Path(capture_root), Path(temporary_root)
        self.payload, self.executable = payload, str(executable)
        self.source_sha, self.source_manifest_sha256 = source_sha, source_manifest_sha256
        self.candidate_sha256, self.interpreter_sha256 = candidate_sha256, interpreter_sha256
        self.deadline, self.hard_deadline, self.clock = deadline, hard_deadline, clock
        self.owner_factory, self.disk_usage, self.capture_reader = owner_factory, disk_usage, capture_reader
        self.resource_check = resource_check
        self.compact, self.compact_reference = compact, compact_reference
        self.snapshot_reader = snapshot_reader
        self._compact_tickets, self._compact_retired, self._compact_failed = {}, set(), False
        self.environment = dict(os.environ if environment is None else environment)
        self._records, self._owners, self._rows, self._active = [], {}, {}, {}
        self._observations, self._pids = {}, {}
        self._launch_directories, self._stream_identities = {}, {}
        self._first_failure = None
        _require(arm in ("serial", "cap1", "cap2") and len(self.clones) == 2,
                 "runner_configuration_invalid")
        _require(self.modules and self.modules == tuple(sorted(set(self.modules)))
                 and len(self.modules) <= 10000
                 and all(type(name) is str and name.isidentifier() and len(name) <= 200 for name in self.modules),
                 "runner_population_invalid")
        _require(_metric(deadline) is not None and _metric(hard_deadline) is not None
                 and clock() < deadline < hard_deadline, "runner_deadline_invalid")
        _require(type(payload) is str and payload and len(payload) <= 1024 * 1024,
                 "runner_payload_invalid")
        for value, width in ((source_sha, 40), (source_manifest_sha256, 64),
                             (candidate_sha256, 64), (interpreter_sha256, 64)):
            _require(type(value) is str and len(value) == width
                     and all(char in "0123456789abcdef" for char in value), "runner_identity_invalid")
        _require(Path(self.executable).is_absolute()
                 and _digest(Path(self.executable).read_bytes()) == interpreter_sha256,
                 "interpreter_identity_changed")
        _require(not any(key.upper().startswith("CLINICAL_")
                         or key.upper() in ("PYTHONPATH", "PYTHONHOME", "GIT_DIR", "GIT_WORK_TREE")
                         for key in self.environment), "inherited_environment_override")
        self._roots = {path: _directory(path) for path in
                       (*self.clones, *(root / "tools" for root in self.clones),
                        self.capture_root, self.temporary_root)}
        independent = (*self.clones, self.capture_root, self.temporary_root)
        _require(all(not left.is_relative_to(right) and not right.is_relative_to(left)
                     for index, left in enumerate(independent) for right in independent[index + 1:]),
                 "runner_roots_overlap")
        _require(not any(self.capture_root.iterdir()) and not any(self.temporary_root.iterdir()),
                 "runner_private_root_not_fresh")
        if compact is not None:
            if snapshot_reader is None:
                from generated_output_contract import read_owned_capture_snapshot
                self.snapshot_reader = read_owned_capture_snapshot
            _require(type(compact_reference) is dict and set(compact_reference) ==
                     {(module, lookup) for module in self.modules for lookup in LOOKUPS},
                     "compact_reference_changed")
            compact.add_capture_root(self.capture_root)

    @property
    def first_failure(self):
        return None if self._first_failure is None else json.loads(json.dumps(self._first_failure))

    @property
    def is_quiescent(self) -> bool:
        """No reserved/live or cleanup-unverified owner; never polls or scans."""
        return not self._active

    def attempt_ledger(self):
        return tuple(dict(self._rows[record.command_ordinal]) for record in self._records)

    def diagnose_exception(self, error):
        diagnostic = safe_exception(error)
        if diagnostic["exception_type"] not in SAFE_CHILD_TYPES:
            diagnostic["exception_type"] = "unavailable"
        return diagnostic

    def _failure(self, record, category, error=None):
        if self._first_failure is None:
            self._first_failure = {"reason": category if category in FIRST_FAILURE_REASONS else "unavailable",
                                   "command_ordinal": record.command_ordinal,
                                   "pair_token": record.pair_token,
                                   "diagnostic": self.diagnose_exception(error) if error else None}

    def start(self, index, lane, module, lookup):
        _require(not self._compact_failed, "compact_retirement_inconclusive")
        _require(self.compact is None or self.pending_capture_slots < 2, "compact_pending_pair_limit")
        _require(type(index) is int and 0 <= index < len(self.modules)
                 and type(lane) is int and lane == index % 2
                 and module == self.modules[index] and lookup in LOOKUPS,
                 "launch_pair_identity_changed")
        _require(len(self._active) < 2 and all(row.lane != lane for row in self._active.values()),
                 "launch_lane_already_active")
        _require(not any(row.module == module and row.lookup == lookup for row in self._records),
                 "launch_pair_repeated")
        ordinal = len(self._records) + 1
        report = self.capture_root / ("command-%04d" % ordinal)
        record = LaunchRecord(self.arm, index, index * 2 + LOOKUPS.index(lookup), module, lookup, lane,
                              ordinal, _token(["repository", module, lookup]),
                              _token(self._roots[self.clones[lane]]), self.source_sha,
                              self.source_manifest_sha256, self.candidate_sha256,
                              _digest(self.payload.encode()), self.interpreter_sha256,
                              self.clones[lane], report, report / "stdout.bin", report / "stderr.bin",
                              self.temporary_root / ("command-%04d" % ordinal), self.clock())
        self._records.append(record)  # Reserve before any native creation or fallible preparation.
        row = {name: getattr(record, name) for name in
               ("arm", "module_index", "pair_index", "module", "lookup", "lane", "command_ordinal",
                "pair_token", "clone_root_token", "source_sha", "source_manifest_sha256",
                "candidate_sha256", "payload_sha256", "interpreter_sha256")}
        row.update(completion="incomplete", classification="unread", reason="launch_incomplete",
                   returncode=None, root_identity_verified=False, total_processes=None,
                   cleanup_verified=False, root_reaped=False, active_processes=None,
                   screen_clean=False, capture_read_verified=False, call_wall_seconds=None,
                   owned_wall_seconds=None, tree_cpu_seconds=None, analysis_seconds=None,
                   stdout_bytes=None, stderr_bytes=None, stdout_sha256=None, stderr_sha256=None)
        row.update({name: None for name in COUNTS})
        self._rows[ordinal] = row
        self._active[ordinal] = record
        try:
            _require(self.clock() < self.deadline, "work_deadline_exhausted")
            self._monitor_all()
            self._free_space(self.capture_root)
            self._free_space(self.temporary_root)
            self._check_roots(record)
            if self.compact is not None:
                self._compact_tickets[ordinal] = self.compact.reserve(self.capture_root, record.report_dir,
                    {name: getattr(record, name) for name in ('source_sha', 'source_manifest_sha256',
                        'candidate_sha256', 'payload_sha256', 'interpreter_sha256', 'pair_token')})
            record.temporary.mkdir()
            env = dict(self.environment)
            # Windows environment names are case-insensitive; replace every spelling.
            env = {key: value for key, value in env.items() if key.upper() not in ("TEMP", "TMP")}
            env["TEMP"] = env["TMP"] = str(record.temporary)
            owner = self.owner_factory.start(
                [self.executable, "-c", self.payload, str(record.clone_root / "tools"), module, lookup],
                cwd=str(record.clone_root / "tools"), env=env, report_dir=str(record.report_dir))
            self._owners[ordinal] = owner
            self._active[ordinal] = record
            _require(all(owner is not other for key, other in self._owners.items() if key != ordinal),
                     "owner_identity_changed")
            self._check_owner(record, owner)
            self._launch_directories[ordinal] = {path: _directory(path)
                                                for path in (record.report_dir, record.temporary)}
            for path in (record.stdout_path, record.stderr_path):
                self._stream_size(path)
                metadata = path.lstat()
                self._stream_identities[path] = (metadata.st_dev, metadata.st_ino)
            snap = owner.poll()
            _require(type(snap.root_pid) is int and snap.root_pid > 0, "owner_pid_unread")
            self._pids[ordinal] = snap.root_pid
            row["root_identity_verified"] = True
            return record
        except BaseException as error:
            self._failure(record, "launch_failed", error)
            partial = getattr(error, "owner", None)
            if ordinal not in self._owners and partial is not None:
                self._owners[ordinal] = partial
                self._active[ordinal] = record
            if ordinal in self._owners:
                if ordinal not in self._pids:
                    try:
                        retained = self._owners[ordinal]
                        self._check_owner(record, retained)
                        snap = retained.poll()
                        if type(snap.root_pid) is int and snap.root_pid > 0:
                            self._pids[ordinal] = snap.root_pid
                    except BaseException:
                        pass  # Keep the original start cause and still attempt cancellation.
                self.cancel(record, "launch_failed")
            else:
                self._active.pop(ordinal, None)
            raise

    def _check_roots(self, record):
        for path in (record.clone_root, record.clone_root / "tools", self.capture_root, self.temporary_root):
            _require(_directory(path) == self._roots[path], "directory_identity_changed")
        for path, expected in self._launch_directories.get(record.command_ordinal, {}).items():
            _require(_directory(path) == expected, "directory_identity_changed")

    def _check_owner(self, record, owner):
        _require(Path(owner.report_dir) == record.report_dir
                 and Path(owner.stdout_path) == record.stdout_path
                 and Path(owner.stderr_path) == record.stderr_path, "owner_capture_identity_changed")

    def _timeout(self):
        # A short finalization wait is not a timeout on the test payload. Bound
        # each drain so a failing first owner cannot spend the sibling's reserve.
        return min(5.0, max(0.0, self.hard_deadline - self.clock()))

    def _free_space(self, path):
        free = self.disk_usage(path).free
        _require(type(free) is int and free >= MINIMUM_FREE_BYTES, "disk_reserve_exhausted")

    def _stream_size(self, path):
        item = path.lstat()
        _require(stat.S_ISREG(item.st_mode) and item.st_nlink == 1
                 and not getattr(item, "st_file_attributes", 0) & 0x400, "capture_stream_unsafe")
        _require(item.st_size <= MAX_CAPTURE_BYTES, "capture_limit_exceeded")
        _require(path not in self._stream_identities or self._stream_identities[path] == (item.st_dev, item.st_ino),
                 "capture_stream_identity_changed")
        return item.st_size

    def pending_capture_bytes(self):
        """Remaining qualifying capture allowance, not a hard write quota.

        Reserved pre-start streams each consume their full allowance. Retained
        completed captures already reduce free space and are not reserved twice.
        """
        remaining = 0
        for record in self._active.values():
            for path in (record.stdout_path, record.stderr_path):
                size = self._stream_size(path) if record.command_ordinal in self._owners else 0
                remaining += MAX_CAPTURE_BYTES - size
        return remaining

    @property
    def pending_capture_slots(self):
        # Unexpected results stay raw while the unchanged scheduler resolves
        # already-dispatched earlier work; they still occupy a capture slot.
        if self.compact is None:
            return len(self._active)
        # Admission also sees the pre-owner reservation before reserve() binds
        # its ticket. Union prevents counting that same active row twice later.
        return len((set(self._compact_tickets) - self._compact_retired) | set(self._active))

    def _monitor_all(self):
        # Observe every live owner's two streams before polling the requested
        # owner. A slow low-index tree cannot hide a later tree's exhaustion.
        failures = []
        for record in tuple(self._active.values()):
            try:
                _require(self.clock() < self.deadline, "work_deadline_exhausted")
                self._check_roots(record)
                if record.command_ordinal not in self._owners:
                    continue
                self._check_owner(record, self._owners[record.command_ordinal])
                self._free_space(record.report_dir)
                self._free_space(record.temporary)
                for path in (record.stdout_path, record.stderr_path):
                    self._stream_size(path)
            except Exception as error:
                category = str(error) if type(error) is RunnerRefused else "live_resource_unread"
                self._failure(record, category, error)
                failures.append(error)
        if failures:
            raise failures[0]
        if self.resource_check is not None:
            self.resource_check()
        _require(self.clock() < self.deadline, "work_deadline_exhausted")

    def _retain_result(self, record, result):
        row, snap = self._rows[record.command_ordinal], result.snapshot
        row.update(returncode=snap.root_exit_code if type(snap.root_exit_code) is int else None,
                   root_identity_verified=type(snap.root_pid) is int and snap.root_pid > 0
                   and self._pids.get(record.command_ordinal) == snap.root_pid,
                   root_reaped=snap.root_reaped is True,
                   active_processes=_count(snap.active_processes), total_processes=_count(snap.total_processes),
                   cleanup_verified=snap.cleanup_verified is True and snap.root_reaped is True
                   and type(snap.active_processes) is int and snap.active_processes == 0,
                   call_wall_seconds=row["call_wall_seconds"] if row["call_wall_seconds"] is not None
                   else _metric(self.clock() - record.launched_at),
                   owned_wall_seconds=_metric(snap.wall_seconds), tree_cpu_seconds=_metric(snap.tree_cpu_seconds))

    def _validate_result(self, record, owner, result):
        self._rows[record.command_ordinal]["root_identity_verified"] = False
        self._check_owner(record, owner)
        _require(result is owner.result and Path(result.stdout_path) == record.stdout_path
                 and Path(result.stderr_path) == record.stderr_path, "owner_result_identity_changed")
        expected_pid = self._pids.get(record.command_ordinal)
        _require(expected_pid is None or (type(result.snapshot.root_pid) is int
                 and result.snapshot.root_pid == expected_pid), "owner_pid_changed")
        self._rows[record.command_ordinal]["root_identity_verified"] = expected_pid is not None

    def _observation(self, record):
        row = self._rows[record.command_ordinal]
        return Observation(record.module, record.lookup, row["classification"],
                           not row["screen_clean"], row["cleanup_verified"], row["test_count"],
                           row["failures"], row["errors"], row["owned_wall_seconds"],
                           row["tree_cpu_seconds"], row["reason"], dict(row))

    def poll(self, handle):
        record = self._handle(handle)
        if record.command_ordinal in self._observations:
            return self._observations[record.command_ordinal]
        owner = self._owners[record.command_ordinal]
        try:
            self._monitor_all()
            snap = owner.poll()
            _require(type(snap.root_pid) is int and snap.root_pid == self._pids[record.command_ordinal],
                     "owner_pid_changed")
            if not snap.root_reaped or snap.active_processes != 0:
                return None
            result = owner.finish(timeout=self._timeout())
            self._validate_result(record, owner, result)
            _require(result.reason == "completed"
                     and result.snapshot.root_pid == snap.root_pid
                     and result.snapshot.root_exit_code == snap.root_exit_code
                     and result.snapshot.tree_cpu_seconds == snap.tree_cpu_seconds
                     and result.snapshot.user_cpu_seconds == snap.user_cpu_seconds
                     and result.snapshot.kernel_cpu_seconds == snap.kernel_cpu_seconds
                     and result.snapshot.total_processes == snap.total_processes
                     and result.snapshot.wall_seconds >= snap.wall_seconds
                     and Path(result.stdout_path) == record.stdout_path
                     and Path(result.stderr_path) == record.stderr_path, "owner_result_identity_changed")
            self._retain_result(record, result)
            row = self._rows[record.command_ordinal]
            _require(row["cleanup_verified"], "owner_cleanup_unverified")
            _require(all(row[key] is not None for key in
                         ("returncode", "owned_wall_seconds", "tree_cpu_seconds", "total_processes"))
                     and row["total_processes"] > 0
                     and _metric(result.snapshot.user_cpu_seconds) is not None
                     and _metric(result.snapshot.kernel_cpu_seconds) is not None,
                     "owner_metrics_unread")
            self._check_roots(record)
            captures, snapshots = [], []
            for path in (record.stdout_path, record.stderr_path):
                self._stream_size(path)
                relative = record.report_dir.name + "/" + path.name
                if self.compact is None:
                    captures.append(self.capture_reader(self.capture_root, relative, MAX_CAPTURE_BYTES, self.deadline))
                else:
                    raw, metadata = self.snapshot_reader(self.capture_root, relative, MAX_CAPTURE_BYTES, self.deadline)
                    captures.append(raw); snapshots.append((raw, metadata))
                self._stream_size(path)
            self._check_roots(record)
            raw = tuple(captures)
            started = self.clock()
            parsed = analyze_capture(None, None, row["returncode"], record.lookup,
                                     module=record.module, capture_bytes=raw)
            row.update({key: _count(parsed[key]) for key in COUNTS})
            counts_read = all(row[key] is not None for key in COUNTS)
            row.update(completion="completed" if counts_read else "incomplete",
                       reason="completed" if counts_read else "capture_unread", classification=parsed["classification"],
                       screen_clean=not parsed["unexpected"] and counts_read,
                       capture_read_verified=True, analysis_seconds=_metric(self.clock() - started),
                       stdout_bytes=len(raw[0]), stderr_bytes=len(raw[1]),
                       stdout_sha256=_digest(raw[0]), stderr_sha256=_digest(raw[1]))
            if not row["screen_clean"]:
                self._failure(record, "capture_screen_failed")
            self._active.pop(record.command_ordinal, None)
            observation = self._observation(record)
            self._observations[record.command_ordinal] = observation
            if self.compact is not None:
                if not row['screen_clean']:
                    # Unexpected execution is not a compact-success candidate.
                    # Its reserved slot and original raw evidence remain intact.
                    return observation
                try:
                    ticket = self._compact_tickets[record.command_ordinal]
                    self.compact.register(ticket, owner, result, tuple(snapshots))
                    expected = self.compact_reference[(record.module, record.lookup)]
                    _require(all(row.get(key) == value for key, value in expected.items()),
                             'compact_reference_changed')
                    outcome = self.compact.retire(ticket, 'measured_pair',
                        {'completed': True, 'validated': True, 'original_success': True, 'result': dict(row)})
                    _require(outcome.get('complete') is True,
                             'compact_retirement_inconclusive')
                    self._compact_retired.add(record.command_ordinal)
                except BaseException as error:
                    self._compact_failed = True
                    self._failure(record, 'compact_reference_changed' if type(error) is RunnerRefused
                                  and str(error) == 'compact_reference_changed'
                                  else 'compact_retirement_inconclusive', error)
                    raise
            return observation
        except BaseException as error:
            self._failure(record, "completion_failed", error)
            raise

    def _handle(self, handle):
        _require(type(handle) is LaunchRecord and 0 < handle.command_ordinal <= len(self._records)
                 and self._records[handle.command_ordinal - 1] is handle, "launch_handle_changed")
        return handle

    def cancel(self, handle, reason):
        record = self._handle(handle)
        row = self._rows[record.command_ordinal]
        if record.command_ordinal in self._observations:
            return self._observations[record.command_ordinal]
        self._failure(record, "launch_cancelled")
        row.update(reason="cancelled", completion="incomplete", screen_clean=False)
        try:
            owner = self._owners[record.command_ordinal]
            result = owner.cancel("coordinator_cancel", timeout=self._timeout())
            self._validate_result(record, owner, result)
            self._retain_result(record, result)
        except BaseException as error:
            row["cleanup_verified"] = False
            row["reason"] = "cleanup_unverified"
            self._failure(record, "cleanup_unverified", error)
        if row["cleanup_verified"]:
            self._active.pop(record.command_ordinal, None)
        observation = self._observation(record)
        self._observations[record.command_ordinal] = observation
        return observation

    def cleanup(self):
        clean = True
        for record in self._records:
            owner = self._owners.get(record.command_ordinal)
            if owner is None:
                continue
            try:
                result = owner.result or owner.cancel("coordinator_cleanup", timeout=self._timeout())
                self._validate_result(record, owner, result)
                self._retain_result(record, result)
                clean = self._rows[record.command_ordinal]["cleanup_verified"] and clean
                if self._rows[record.command_ordinal]["cleanup_verified"]:
                    self._active.pop(record.command_ordinal, None)
                else:
                    self._active[record.command_ordinal] = record
            except BaseException as error:
                self._failure(record, "cleanup_unverified", error)
                self._rows[record.command_ordinal]["cleanup_verified"] = False
                self._active[record.command_ordinal] = record
                clean = False
        return clean
