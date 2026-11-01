"""Qualification-only Windows ownership seam; measurement is deliberately disabled.

No project module is imported. Native success, bounded storage and cancellation
remain unqualified until the single admitted hosted run. Broker processes and
forced Win32/storage failures are outside this candidate's qualified claims.
"""

from __future__ import annotations

import ctypes as c
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import threading
import time


RECIPES = frozenset({"ordinary", "nested", "deadline", "survivor", "breakaway",
                     "output", "supervisor_loss", "protocol_fault", "protocol_exit",
                     "protocol_missing"})
PREFIX_CAP = 65_536
DWORD, BOOL, HANDLE, SIZE = c.c_uint32, c.c_int32, c.c_void_p, c.c_size_t
KILL_ON_CLOSE, STILL_ACTIVE, WAIT_TIMEOUT = 0x2000, 259, 258


@dataclass(frozen=True)
class Plan:
    recipe: str
    destination: Path
    sources: dict[str, str]
    job_start_ms: int
    case_end_ms: int
    nonce: str


class _EvidenceRefused(Exception):
    pass


class _BasicLimits(c.Structure):
    _fields_ = [("process_time", c.c_int64), ("job_time", c.c_int64),
                ("flags", DWORD), ("minimum_ws", SIZE), ("maximum_ws", SIZE),
                ("active_limit", DWORD), ("affinity", SIZE),
                ("priority", DWORD), ("scheduling", DWORD)]


class _IO(c.Structure):
    _fields_ = [(name, c.c_uint64) for name in
                ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]


class _Limits(c.Structure):
    _fields_ = [("basic", _BasicLimits), ("io", _IO),
                ("process_memory", SIZE), ("job_memory", SIZE),
                ("peak_process_memory", SIZE), ("peak_job_memory", SIZE)]


class _Accounting(c.Structure):
    _fields_ = [("user", c.c_int64), ("kernel", c.c_int64),
                ("period_user", c.c_int64), ("period_kernel", c.c_int64),
                ("faults", DWORD), ("total", DWORD), ("active", DWORD), ("terminated", DWORD)]


class _Members(c.Structure):
    _fields_ = [("assigned", DWORD), ("listed", DWORD), ("ids", SIZE * 64)]


class _Security(c.Structure):
    _fields_ = [("length", DWORD), ("descriptor", HANDLE), ("inherit", BOOL)]


class _Startup(c.Structure):
    _fields_ = [("cb", DWORD), ("reserved", c.c_wchar_p), ("desktop", c.c_wchar_p),
                ("title", c.c_wchar_p), ("x", DWORD), ("y", DWORD),
                ("width", DWORD), ("height", DWORD), ("xchars", DWORD),
                ("ychars", DWORD), ("fill", DWORD), ("flags", DWORD),
                ("show", c.c_uint16), ("reserved_size", c.c_uint16),
                ("reserved_bytes", HANDLE), ("stdin", HANDLE),
                ("stdout", HANDLE), ("stderr", HANDLE)]


class _StartupEx(c.Structure):
    _fields_ = [("startup", _Startup), ("attributes", HANDLE)]


class _Process(c.Structure):
    _fields_ = [("process", HANDLE), ("thread", HANDLE), ("pid", DWORD), ("tid", DWORD)]


class _Kernel:
    def __init__(self):
        self.dll = c.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": (HANDLE, [HANDLE, c.c_wchar_p]),
            "SetInformationJobObject": (BOOL, [HANDLE, c.c_int, HANDLE, DWORD]),
            "QueryInformationJobObject": (BOOL, [HANDLE, c.c_int, HANDLE, DWORD, HANDLE]),
            "CreatePipe": (BOOL, [c.POINTER(HANDLE), c.POINTER(HANDLE), c.POINTER(_Security), DWORD]),
            "SetHandleInformation": (BOOL, [HANDLE, DWORD, DWORD]),
            "GetHandleInformation": (BOOL, [HANDLE, c.POINTER(DWORD)]),
            "InitializeProcThreadAttributeList": (BOOL, [HANDLE, DWORD, DWORD, c.POINTER(SIZE)]),
            "UpdateProcThreadAttribute": (BOOL, [HANDLE, DWORD, SIZE, HANDLE, SIZE, HANDLE, HANDLE]),
            "DeleteProcThreadAttributeList": (None, [HANDLE]),
            "CreateProcessW": (BOOL, [c.c_wchar_p, c.c_wchar_p, HANDLE, HANDLE, BOOL,
                                     DWORD, HANDLE, c.c_wchar_p, HANDLE, c.POINTER(_Process)]),
            "IsProcessInJob": (BOOL, [HANDLE, HANDLE, c.POINTER(BOOL)]),
            "GetCurrentProcess": (HANDLE, []),
            "ResumeThread": (DWORD, [HANDLE]),
            "WaitForSingleObject": (DWORD, [HANDLE, DWORD]),
            "GetExitCodeProcess": (BOOL, [HANDLE, c.POINTER(DWORD)]),
            "OpenProcess": (HANDLE, [DWORD, BOOL, DWORD]),
            "GetProcessTimes": (BOOL, [HANDLE, c.POINTER(c.c_uint64), c.POINTER(c.c_uint64),
                                       c.POINTER(c.c_uint64), c.POINTER(c.c_uint64)]),
            "TerminateJobObject": (BOOL, [HANDLE, DWORD]),
            "CloseHandle": (BOOL, [HANDLE]),
            "PeekNamedPipe": (BOOL, [HANDLE, HANDLE, DWORD, HANDLE, c.POINTER(DWORD), HANDLE]),
            "ReadFile": (BOOL, [HANDLE, HANDLE, DWORD, c.POINTER(DWORD), HANDLE]),
            "WriteFile": (BOOL, [HANDLE, HANDLE, DWORD, c.POINTER(DWORD), HANDLE]),
            "GetTickCount64": (c.c_uint64, []),
        }
        for name, (result, arguments) in signatures.items():
            method = getattr(self.dll, name)
            method.restype, method.argtypes = result, arguments

    def ok(self, value):
        if not value:
            raise OSError(c.get_last_error(), "native ownership operation failed")
        return value

    def ticks(self):
        return int(self.dll.GetTickCount64())

    def close(self, handle):
        if handle:
            self.ok(self.dll.CloseHandle(handle))

    def members(self, job):
        value = _Members()
        self.ok(self.dll.QueryInformationJobObject(job, 3, c.byref(value), c.sizeof(value), None))
        if value.listed > 64 or value.assigned > 64:
            raise OSError("owned process list exceeds fixed capacity")
        return {int(pid) for pid in value.ids[:value.listed]}

    def accounting(self, job):
        value = _Accounting()
        self.ok(self.dll.QueryInformationJobObject(job, 1, c.byref(value), c.sizeof(value), None))
        return value

    def process_times(self, process):
        # FILETIME is two DWORDs; the required host is explicitly x64 little
        # endian. Exit time is consumed only after a signaled process wait.
        creation, exit_time, system, user = (c.c_uint64() for _ in range(4))
        self.ok(self.dll.GetProcessTimes(process, c.byref(creation), c.byref(exit_time),
                                         c.byref(system), c.byref(user)))
        return creation.value, exit_time.value

    def pipe(self, *, parent_reads):
        read, write = HANDLE(), HANDLE()
        security = _Security(c.sizeof(_Security), None, True)
        self.ok(self.dll.CreatePipe(c.byref(read), c.byref(write), c.byref(security), 4096))
        parent, child = (read.value, write.value) if parent_reads else (write.value, read.value)
        try:
            self.ok(self.dll.SetHandleInformation(parent, 1, 0))
        except BaseException:
            self.close(read.value)
            self.close(write.value)
            raise
        return parent, child

    def read_available(self, pipe):
        available = DWORD()
        if not self.dll.PeekNamedPipe(pipe, None, 0, None, c.byref(available), None):
            if c.get_last_error() == 109:  # ERROR_BROKEN_PIPE
                return b""
            self.ok(False)
        if not available.value:
            return b""
        size = min(4096, available.value)
        buffer, count = c.create_string_buffer(size), DWORD()
        self.ok(self.dll.ReadFile(pipe, buffer, size, c.byref(count), None))
        return buffer.raw[:count.value]


def _bounded_io(call, end_ms, kernel):
    """No unbounded join; a timed-out daemon makes this observation unsuccessful."""
    if kernel.ticks() >= end_ms:
        return False, True
    done = threading.Event()
    errors = []
    def work():
        try:
            call()
        except BaseException as error:
            errors.append(type(error).__name__)
        finally:
            done.set()
    threading.Thread(target=work, daemon=True).start()
    settled = done.wait(max(0, end_ms - kernel.ticks()) / 1000)
    return settled and not errors, settled


def run_owned(plan: Plan) -> dict:
    """Run one allowlisted synthetic recipe; return independent execution/cleanup proof.

    Measurement, arbitrary commands, private fault injection and retries are not
    implemented. A public receipt never contains exception text or raw streams.
    """
    receipt = {
        "success": False, "launched": False, "process_exit": None,
        "membership_before_resume": False, "hosted_parent_job": None,
        "lineage_verified": False, "peak_owned_processes": 0,
        "active_processes": 0, "cleanup_unproven": False,
        "forced_termination": False, "faults": [], "fixture_terminal": None,
        "capture_retention_verified": False,
        "retained_stdout_bytes": 0, "retained_stderr_bytes": 0,
        "observed_stdout_bytes": 0, "observed_stderr_bytes": 0,
    }
    faults = receipt["faults"]
    if os.name != "nt" or sys.version_info[:3] != (3, 14, 4) or c.sizeof(HANDLE) != 8:
        faults.append("host_runtime")
        return receipt
    kernel = _Kernel()
    now = kernel.ticks()
    receipt["started_ms"] = now
    receipt["recipe"] = plan.recipe
    if (plan.recipe not in RECIPES or not re.fullmatch(r"[A-Za-z0-9_-]{1,120}", plan.nonce)
            or not 0 <= now - plan.job_start_ms < 540_000
            or not now < plan.case_end_ms <= min(now + 35_000, plan.job_start_ms + 540_000)):
        faults.append("plan_refused")
        return receipt
    work_end = min(now + (5000 if plan.recipe == "deadline" else 10_000), plan.case_end_ms - 1000)
    job, pi, attributes = None, _Process(), None
    attributes_initialized = False
    handles = set()
    prefixes = {"stdout": bytearray(), "stderr": bytearray()}
    pending = bytearray()
    parent_out = parent_err = parent_in = None
    observed_processes = {}
    ended_processes = {}
    root_exit_recorded = False

    def observe_members(members):
        """Retain query/synchronize handles, never PID-selected kill authority."""
        for pid in members - {pi.pid}:
            if pid in observed_processes:
                continue
            handle = kernel.ok(kernel.dll.OpenProcess(0x101000, False, pid))
            try:
                member = BOOL()
                kernel.ok(kernel.dll.IsProcessInJob(handle, job, c.byref(member)))
                if not member.value:
                    raise OSError("observed process membership unproven")
                creation, _ = kernel.process_times(handle)
                if not creation:
                    raise OSError("observed process identity unproven")
                if (pid, creation) in ended_processes:
                    kernel.close(handle)
                    continue
                if len(observed_processes) + len(ended_processes) >= 3:
                    raise OSError("synthetic lifetime population exceeded")
                observed_processes[pid] = (handle, creation)
            except BaseException:
                kernel.close(handle)
                raise
        # Release completed-process references promptly. Keeping them would
        # itself delay nested job accounting and contaminate the observation.
        for pid, (handle, creation) in tuple(observed_processes.items()):
            wait = kernel.dll.WaitForSingleObject(handle, 0)
            if wait == 0:
                identity, exit_time = kernel.process_times(handle)
                if identity != creation or not exit_time:
                    raise OSError("completed process identity unproven")
                ended_processes[pid, creation] = exit_time
                kernel.close(handle)
                del observed_processes[pid]
            elif wait != WAIT_TIMEOUT:
                raise OSError("observed process wait unproven")

    def observe_root_exit():
        nonlocal root_exit_recorded
        if root_exit_recorded:
            return
        root_exit_recorded = True
        observation = {"observed_ms": kernel.ticks(), "live_pids": [],
                       "outlived_root_pids": [], "completed_before_root_pids": [],
                       "state_unproven": True}
        receipt["root_exit_observation"] = observation
        try:
            value = DWORD()
            kernel.ok(kernel.dll.GetExitCodeProcess(pi.process, c.byref(value)))
            receipt["process_exit"] = value.value
            _, root_exit = kernel.process_times(pi.process)
            if not root_exit:
                raise OSError("root exit time unproven")
            observation["root_exit_filetime"] = root_exit
            observe_members(kernel.members(job))
            known = {pid for pid, _ in ended_processes} | set(observed_processes) | {pi.pid}
            accounting = kernel.accounting(job)
            uncertain = (not kernel.members(job) <= known
                         or accounting.total != 1 + len(ended_processes) + len(observed_processes))
            observation["total_processes"] = accounting.total
            observation["known_processes"] = 1 + len(ended_processes) + len(observed_processes)
            exits = dict(ended_processes)
            for pid, (handle, creation) in observed_processes.items():
                wait = kernel.dll.WaitForSingleObject(handle, 0)
                if wait == WAIT_TIMEOUT:
                    observation["live_pids"].append(pid)
                elif wait == 0:
                    identity, exit_time = kernel.process_times(handle)
                    if identity != creation or not exit_time:
                        uncertain = True
                    else:
                        exits[pid, creation] = exit_time
                else:
                    uncertain = True
            for (pid, _), exit_time in exits.items():
                if exit_time > root_exit:
                    observation["outlived_root_pids"].append(pid)
                elif exit_time < root_exit:
                    observation["completed_before_root_pids"].append(pid)
                else:
                    # Equal native timestamps do not establish exit order.
                    uncertain = True
            observation["state_unproven"] = uncertain
        except BaseException:
            observation["state_unproven"] = True
        # This fact is latched before drain/settling, independently of final
        # emptiness. A process that later exits cannot erase an observed leak.
        if receipt["process_exit"] == 0 and (
                observation["live_pids"] or observation["outlived_root_pids"]):
            faults.append("surviving_descendant")
        if observation["state_unproven"]:
            faults.append("root_exit_state_unproven")

    def release_observations():
        for handle, _ in observed_processes.values():
            try:
                kernel.close(handle)
            except BaseException:
                receipt["cleanup_unproven"] = True
                faults.append("process_observation_cleanup")
        observed_processes.clear()

    try:
        expected = {"windows_serial_envelope.py", "serial_envelope_fixture.py",
                    "test_windows_serial_envelope.py"}
        if set(plan.sources) != expected:
            raise ValueError("source manifest refused")
        for name, digest in plan.sources.items():
            with Path(__file__).with_name(name).open("rb") as source:
                data = source.read(262_145)
            if (len(data) > 262_144 or not re.fullmatch(r"[0-9a-f]{64}", digest)
                    or hashlib.sha256(data).hexdigest() != digest):
                raise ValueError("source identity refused")
        receipt["sources"] = dict(plan.sources)
        destination = Path(plan.destination)
        if not destination.is_absolute():
            raise ValueError("absolute task-owned destination required")
        destination = Path(os.path.abspath(destination))
        # Resolve the parent, not the nonexistent leaf beneath N7's regular
        # file. That native mkdir failure belongs to evidence_setup.
        destination = destination.parent.resolve() / destination.name
        run_id = plan.nonce.split("-", 1)[0]
        task_root = Path(__file__).resolve().parent.parent / "scratch" / "sessions" / (
            "2013-qualification-" + run_id + "-1")
        if (not run_id.isdecimal() or not destination.is_relative_to(task_root.resolve())
                or destination == task_root.resolve()):
            raise ValueError("task-owned destination required")
        def prepare():
            destination.mkdir(parents=True, exist_ok=False)
        prepared, settled = _bounded_io(prepare, min(now + 3000, work_end), kernel)
        if not prepared:
            faults.append("evidence_setup")
            receipt["cleanup_unproven"] = not settled
            raise _EvidenceRefused

        job = kernel.ok(kernel.dll.CreateJobObjectW(None, None))
        limits = _Limits()
        limits.basic.flags = KILL_ON_CLOSE
        kernel.ok(kernel.dll.SetInformationJobObject(job, 9, c.byref(limits), c.sizeof(limits)))
        inherited = DWORD()
        kernel.ok(kernel.dll.GetHandleInformation(job, c.byref(inherited)))
        if inherited.value & 1:
            raise ValueError("job handle must not be inherited")
        inside = BOOL()
        kernel.ok(kernel.dll.IsProcessInJob(kernel.dll.GetCurrentProcess(), None, c.byref(inside)))
        receipt["hosted_parent_job"] = bool(inside.value)

        parent_out, child_out = kernel.pipe(parent_reads=True)
        handles.update((parent_out, child_out))
        parent_err, child_err = kernel.pipe(parent_reads=True)
        handles.update((parent_err, child_err))
        parent_in, child_in = kernel.pipe(parent_reads=False)
        handles.update((parent_in, child_in))
        size = SIZE()
        kernel.dll.InitializeProcThreadAttributeList(None, 2, 0, c.byref(size))
        attributes = c.create_string_buffer(size.value)
        kernel.ok(kernel.dll.InitializeProcThreadAttributeList(attributes, 2, 0, c.byref(size)))
        attributes_initialized = True
        jobs = (HANDLE * 1)(job)
        streams = (HANDLE * 3)(child_in, child_out, child_err)
        kernel.ok(kernel.dll.UpdateProcThreadAttribute(attributes, 0, 0x2000D,
                                                       jobs, c.sizeof(jobs), None, None))
        kernel.ok(kernel.dll.UpdateProcThreadAttribute(attributes, 0, 0x20002,
                                                       streams, c.sizeof(streams), None, None))
        startup = _StartupEx()
        startup.startup.cb = c.sizeof(startup)
        startup.startup.flags = 0x100  # STARTF_USESTDHANDLES
        startup.startup.stdin, startup.startup.stdout, startup.startup.stderr = child_in, child_out, child_err
        startup.attributes = c.cast(attributes, HANDLE)
        command = [sys.executable, "-B", str(Path(__file__).with_name("serial_envelope_fixture.py")),
                   "--recipe", plan.recipe, "--destination", str(destination),
                   "--sources", json.dumps(plan.sources, separators=(",", ":")),
                   "--job-start-ms", str(plan.job_start_ms), "--case-end-ms", str(plan.case_end_ms),
                   "--nonce", plan.nonce]
        command_line = c.create_unicode_buffer(subprocess.list2cmdline(command))
        if kernel.ticks() >= work_end:
            faults.append("deadline")
            raise _EvidenceRefused
        kernel.ok(kernel.dll.CreateProcessW(sys.executable, command_line, None, None, True,
                                            0x80000 | 4, None, str(Path(__file__).parent),
                                            c.byref(startup), c.byref(pi)))
        receipt["launched"] = True
        member = BOOL()
        kernel.ok(kernel.dll.IsProcessInJob(pi.process, job, c.byref(member)))
        if not member.value:
            raise ValueError("membership before resume unproven")
        receipt["membership_before_resume"] = True
        if kernel.ticks() >= work_end:
            faults.append("deadline")
            raise _EvidenceRefused
        previous_suspend_count = kernel.dll.ResumeThread(pi.thread)
        if previous_suspend_count != 1:
            raise OSError("expected initial suspension unproven")
        kernel.close(pi.thread)
        pi.thread = None
        for handle in (child_in, child_out, child_err):
            kernel.close(handle)
            handles.remove(handle)
        sent_go = root_exited = False
        while True:
            members = kernel.members(job)
            receipt["peak_owned_processes"] = max(receipt["peak_owned_processes"], len(members))
            if len(members) > 4:
                faults.append("synthetic_population")
                break
            if not root_exit_recorded:
                observe_members(members)
            read_any = False
            for label, handle in (("stdout", parent_out), ("stderr", parent_err)):
                data = kernel.read_available(handle)
                read_any |= bool(data)
                receipt["observed_" + label + "_bytes"] += len(data)
                space = PREFIX_CAP - len(prefixes[label])
                prefixes[label].extend(data[:space])
                if len(data) > space:
                    faults.append("output_limit")
                if label == "stdout":
                    pending.extend(data[:max(0, PREFIX_CAP - len(pending))])
                    while b"\n" in pending:
                        line, _, tail = pending.partition(b"\n")
                        pending[:] = tail
                        try:
                            row = json.loads(line)
                        except (ValueError, UnicodeError):
                            continue
                        if not isinstance(row, dict) or row.get("nonce") != plan.nonce:
                            faults.append("fixture_protocol")
                            continue
                        if row.get("kind") == "ready":
                            pids = row.get("pids")
                            named_members = kernel.members(job)
                            receipt["peak_owned_processes"] = max(
                                receipt["peak_owned_processes"], len(named_members))
                            if len(named_members) > 4:
                                faults.append("synthetic_population")
                            if (not isinstance(pids, list) or not pids or len(pids) > 4
                                    or any(type(pid) is not int for pid in pids)
                                    or len(set(pids)) != len(pids) or pi.pid not in pids
                                    or not set(pids) <= named_members):
                                faults.append("lineage_unproven")
                            else:
                                observe_members(named_members)
                                receipt["lineage_verified"] = True
                                receipt["lineage_pids"] = pids
                                ordinary_probe = (plan.recipe == "breakaway"
                                                  and row.get("stage") == "ordinary_suspended")
                                if ordinary_probe:
                                    if len(set(pids)) != 2:
                                        faults.append("lineage_unproven")
                                    else:
                                        receipt["ordinary_probe_membership_verified"] = True
                                if plan.recipe == "supervisor_loss":
                                    boundary = row.get("last_close_before_ms")
                                    if type(boundary) is not int:
                                        faults.append("fixture_protocol")
                                    else:
                                        receipt["last_close_before_ms"] = boundary
                                if (not faults and plan.recipe != "deadline"
                                        and (not sent_go or ordinary_probe)):
                                    count = DWORD()
                                    kernel.ok(kernel.dll.WriteFile(parent_in, b"GO\n", 3, c.byref(count), None))
                                    if count.value != 3:
                                        faults.append("fixture_input")
                                    sent_go = True
                        elif row.get("kind") == "terminal":
                            if receipt["fixture_terminal"] is not None:
                                faults.append("duplicate_terminal")
                            receipt["fixture_terminal"] = row
                            if row.get("evidence_faults"):
                                faults.append("reported_evidence_fault")
                            if row.get("cleanup_unproven"):
                                receipt["cleanup_unproven"] = True
                                faults.append("fixture_cleanup_unproven")
            if faults:
                break
            wait = kernel.dll.WaitForSingleObject(pi.process, 0)
            if wait == 0:
                observe_root_exit()
                # Exit may race the preceding empty pipe read. Drain once more
                # after observing exit; no terminal row is inferred from exit 0.
                if root_exited and not read_any:
                    break
                root_exited = True
            elif wait != WAIT_TIMEOUT:
                raise OSError("process wait failed")
            if kernel.ticks() >= work_end:
                faults.append("deadline")
                break
            time.sleep(0.005)
    except _EvidenceRefused:
        pass
    except BaseException as error:
        faults.append("native_or_admission_failure")
        receipt["error_category"] = type(error).__name__
        if isinstance(error, OSError) and type(error.errno) is int:
            receipt["native_error"] = error.errno
    finally:
        if job:
            try:
                try:
                    if pi.process and kernel.dll.WaitForSingleObject(pi.process, 0) == 0:
                        observe_root_exit()
                    if pi.process and receipt["fixture_terminal"] is not None:
                        # Only a still-finalizing root gets terminal exit grace.
                        # An already observed exit cannot gain a clean verdict
                        # from any descendant's subsequent disappearance.
                        grace = max(0, min(500, plan.case_end_ms - kernel.ticks()))
                        if kernel.dll.WaitForSingleObject(pi.process, grace) == 0:
                            observe_root_exit()
                finally:
                    release_observations()
                if pi.process and kernel.dll.WaitForSingleObject(pi.process, 0) == 0:
                    value = DWORD()
                    kernel.ok(kernel.dll.GetExitCodeProcess(pi.process, c.byref(value)))
                    receipt["process_exit"] = value.value
                    kernel.close(pi.process)
                    pi.process = None
                # Allow already terminating inner jobs to settle; this is not a
                # fresh per-probe timeout or permission to continue after a leak.
                settle_end = min(kernel.ticks() + 500, plan.case_end_ms)
                while not pi.process and kernel.accounting(job).active and kernel.ticks() < settle_end:
                    time.sleep(0.005)
                if kernel.accounting(job).active:
                    receipt["forced_termination"] = True
                    kernel.ok(kernel.dll.TerminateJobObject(job, 79))
                if pi.process:
                    remaining = max(0, plan.case_end_ms - kernel.ticks())
                    if kernel.dll.WaitForSingleObject(pi.process, remaining) != 0:
                        raise OSError("root termination unproven")
                    value = DWORD()
                    kernel.ok(kernel.dll.GetExitCodeProcess(pi.process, c.byref(value)))
                    receipt["process_exit"] = value.value
                    kernel.close(pi.process)
                    pi.process = None
                while kernel.accounting(job).active:
                    if kernel.ticks() >= plan.case_end_ms:
                        raise OSError("owned emptiness deadline")
                    time.sleep(0.005)
                receipt["active_processes"] = kernel.accounting(job).active
                receipt["empty_observed_ms"] = kernel.ticks()
            except BaseException:
                faults.append("cleanup_unproven")
                receipt["cleanup_unproven"] = True
                receipt["active_processes"] = None
        release_observations()
        for handle in tuple(handles) + (pi.thread, pi.process):
            if handle:
                try:
                    kernel.close(handle)
                except BaseException:
                    receipt["cleanup_unproven"] = True
                    faults.append("handle_cleanup")
        if attributes_initialized:
            try:
                kernel.dll.DeleteProcThreadAttributeList(attributes)
            except BaseException:
                receipt["cleanup_unproven"] = True
                faults.append("attribute_cleanup")
        if job:
            try:
                kernel.close(job)
            except BaseException:
                receipt["cleanup_unproven"] = True
                faults.append("job_handle_cleanup")

    terminal = receipt["fixture_terminal"]
    if receipt["launched"]:
        if receipt["process_exit"] != 0:
            faults.append("process_exit")
        if terminal is None:
            faults.append("missing_terminal")
        elif terminal.get("status") != 0:
            faults.append("terminal_status")
    if receipt["launched"] and not receipt["cleanup_unproven"]:
        def persist():
            for name, data in prefixes.items():
                path = Path(plan.destination) / (name + ".bin")
                path.write_bytes(data)
                if path.read_bytes() != data:
                    raise OSError("capture readback differs")
        retained, settled = _bounded_io(persist, plan.case_end_ms, kernel)
        receipt["capture_retention_verified"] = retained
        if not retained:
            faults.append("evidence_retention")
            receipt["cleanup_unproven"] |= not settled
    for name, data in prefixes.items():
        receipt["memory_" + name + "_prefix_bytes"] = len(data)
        receipt["retained_" + name + "_bytes"] = (
            len(data) if receipt["capture_retention_verified"] else (None if receipt["launched"] else 0))
        receipt[name + "_prefix_sha256"] = hashlib.sha256(data).hexdigest()
        receipt[name + "_truncated"] = receipt["observed_" + name + "_bytes"] > len(data)
    receipt["faults"] = sorted(set(faults))
    receipt["success"] = not receipt["faults"] and not receipt["cleanup_unproven"]
    receipt["finished_ms"] = kernel.ticks()
    receipt["host"] = {"os": platform.system(), "release": platform.release(),
                       "python": platform.python_version(), "cpus": os.cpu_count()}
    return receipt
