"""Windows-only process-tree ownership for a staged diagnostic, not production.

Not executed or self-graded by its author. See windows_job_probe_sources.md.
An unnamed, non-inherited Job handle is owned solely by this coordinator.
CREATE_SUSPENDED + PROC_THREAD_ATTRIBUTE_JOB_LIST assigns at creation, before
Python can die between CreateProcess and a separate assignment call. Membership
is checked before ResumeThread. Unsupported/rejected assignment is a refusal.

Job membership controls ordinary CreateProcess descendants, not brokered/WMI
launches. This is not filesystem, credential, network, or malicious-code isolation.
The caller retains each owner until finish/cancel and treats any unread cleanup
as incomplete. No destructor, GC event, or root exit certifies tree cleanup.
All capture files are intentionally retained until disposable-runner teardown.
No file-deletion API is provided; cleanup_verified means process/handle cleanup.
"""
from __future__ import annotations

import ctypes as C
from dataclasses import dataclass
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Mapping, Sequence


# Win32 widths, not host C long widths. Layouts use native pointer alignment.
DWORD = C.c_uint32
BOOL = C.c_int32
WORD = C.c_uint16
HANDLE = C.c_void_p
SIZE_T = C.c_size_t
LARGE_INTEGER = C.c_int64
ULONG_PTR = C.c_size_t

CREATE_SUSPENDED = 0x00000004
CREATE_UNICODE_ENVIRONMENT = 0x00000400
EXTENDED_STARTUPINFO_PRESENT = 0x00080000
STARTF_USESTDHANDLES = 0x00000100
PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002
PROC_THREAD_ATTRIBUTE_JOB_LIST = 0x0002000D
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 0x00000102
WAIT_FAILED = 0xFFFFFFFF
CANCEL_EXIT_CODE = 0xE0000001
INVALID_HANDLE_VALUE = C.c_void_p(-1).value


class _SECURITY_ATTRIBUTES(C.Structure):
    _fields_ = [("nLength", DWORD), ("lpSecurityDescriptor", C.c_void_p),
                ("bInheritHandle", BOOL)]


class _STARTUPINFOW(C.Structure):
    _fields_ = [("cb", DWORD), ("lpReserved", C.c_wchar_p),
                ("lpDesktop", C.c_wchar_p), ("lpTitle", C.c_wchar_p),
                ("dwX", DWORD), ("dwY", DWORD), ("dwXSize", DWORD),
                ("dwYSize", DWORD), ("dwXCountChars", DWORD),
                ("dwYCountChars", DWORD), ("dwFillAttribute", DWORD),
                ("dwFlags", DWORD), ("wShowWindow", WORD),
                ("cbReserved2", WORD), ("lpReserved2", C.c_void_p),
                ("hStdInput", HANDLE), ("hStdOutput", HANDLE),
                ("hStdError", HANDLE)]


class _STARTUPINFOEXW(C.Structure):
    _fields_ = [("StartupInfo", _STARTUPINFOW), ("lpAttributeList", C.c_void_p)]


class _PROCESS_INFORMATION(C.Structure):
    _fields_ = [("hProcess", HANDLE), ("hThread", HANDLE),
                ("dwProcessId", DWORD), ("dwThreadId", DWORD)]


class _BASIC_LIMIT(C.Structure):
    _fields_ = [("PerProcessUserTimeLimit", LARGE_INTEGER),
                ("PerJobUserTimeLimit", LARGE_INTEGER), ("LimitFlags", DWORD),
                ("MinimumWorkingSetSize", SIZE_T), ("MaximumWorkingSetSize", SIZE_T),
                ("ActiveProcessLimit", DWORD), ("Affinity", ULONG_PTR),
                ("PriorityClass", DWORD), ("SchedulingClass", DWORD)]


class _IO_COUNTERS(C.Structure):
    _fields_ = [(name, C.c_uint64) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class _EXTENDED_LIMIT(C.Structure):
    _fields_ = [("BasicLimitInformation", _BASIC_LIMIT), ("IoInfo", _IO_COUNTERS),
                ("ProcessMemoryLimit", SIZE_T), ("JobMemoryLimit", SIZE_T),
                ("PeakProcessMemoryUsed", SIZE_T), ("PeakJobMemoryUsed", SIZE_T)]


class _ACCOUNTING(C.Structure):
    _fields_ = [("TotalUserTime", LARGE_INTEGER), ("TotalKernelTime", LARGE_INTEGER),
                ("ThisPeriodTotalUserTime", LARGE_INTEGER),
                ("ThisPeriodTotalKernelTime", LARGE_INTEGER),
                ("TotalPageFaultCount", DWORD), ("TotalProcesses", DWORD),
                ("ActiveProcesses", DWORD), ("TotalTerminatedProcesses", DWORD)]


@dataclass(frozen=True)
class ProbeSnapshot:
    """cleanup_verified covers process-tree drain and handle closure, not files."""
    root_pid: int | None
    root_exit_code: int | None
    root_reaped: bool
    active_processes: int | None
    total_processes: int | None
    user_cpu_seconds: float | None
    kernel_cpu_seconds: float | None
    wall_seconds: float
    cleanup_verified: bool
    state: str

    @property
    def tree_cpu_seconds(self) -> float | None:
        if self.user_cpu_seconds is None or self.kernel_cpu_seconds is None:
            return None
        return self.user_cpu_seconds + self.kernel_cpu_seconds


@dataclass(frozen=True)
class ProbeResult:
    """Capture paths name retained private evidence; this module never deletes it."""
    snapshot: ProbeSnapshot
    reason: str
    stdout_path: str
    stderr_path: str
    diagnostic_codes: tuple[str, ...]


class ProbeError(RuntimeError):
    """Stable code, numeric OS error, retained owner. Never includes argv/env."""
    def __init__(self, code: str, *, winerror: int | None = None,
                 owner: WindowsJobProbe | None = None,
                 diagnostic_codes: tuple[str, ...] = ()):
        self.code = code
        self.winerror = winerror
        self.owner = owner
        self.diagnostic_codes = diagnostic_codes
        super().__init__(code + (f" (winerror={winerror})" if winerror is not None else ""))


def _native_error(code):
    return ProbeError(code, winerror=C.get_last_error())


class _Kernel32:
    """Small typed binding to documented APIs; no third-party dependencies."""
    def __init__(self):
        if os.name != "nt" or sys.getwindowsversion().major < 10:
            raise ProbeError("ATOMIC_JOB_ASSIGNMENT_PLATFORM_UNSUPPORTED")
        self.dll = C.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": (HANDLE, [C.c_void_p, C.c_wchar_p]),
            "GetHandleInformation": (BOOL, [HANDLE, C.POINTER(DWORD)]),
            "SetInformationJobObject": (BOOL, [HANDLE, C.c_int32, C.c_void_p, DWORD]),
            "QueryInformationJobObject": (BOOL, [HANDLE, C.c_int32, C.c_void_p, DWORD, C.POINTER(DWORD)]),
            "CreateFileW": (HANDLE, [C.c_wchar_p, DWORD, DWORD, C.POINTER(_SECURITY_ATTRIBUTES), DWORD, DWORD, HANDLE]),
            "InitializeProcThreadAttributeList": (BOOL, [C.c_void_p, DWORD, DWORD, C.POINTER(SIZE_T)]),
            "UpdateProcThreadAttribute": (BOOL, [C.c_void_p, DWORD, ULONG_PTR, C.c_void_p, SIZE_T, C.c_void_p, C.c_void_p]),
            "DeleteProcThreadAttributeList": (None, [C.c_void_p]),
            "CreateProcessW": (BOOL, [C.c_wchar_p, C.c_wchar_p, C.c_void_p, C.c_void_p, BOOL, DWORD, C.c_void_p, C.c_wchar_p, C.POINTER(_STARTUPINFOEXW), C.POINTER(_PROCESS_INFORMATION)]),
            "IsProcessInJob": (BOOL, [HANDLE, HANDLE, C.POINTER(BOOL)]),
            "ResumeThread": (DWORD, [HANDLE]),
            "TerminateProcess": (BOOL, [HANDLE, DWORD]),
            "TerminateJobObject": (BOOL, [HANDLE, DWORD]),
            "WaitForSingleObject": (DWORD, [HANDLE, DWORD]),
            "GetExitCodeProcess": (BOOL, [HANDLE, C.POINTER(DWORD)]),
            "CloseHandle": (BOOL, [HANDLE]),
        }
        for name, (result, arguments) in signatures.items():
            function = getattr(self.dll, name)
            function.restype = result
            function.argtypes = arguments

    def create_job(self):
        handle = self.dll.CreateJobObjectW(None, None)
        if not handle:
            raise _native_error("CREATE_JOB_FAILED")
        return handle

    def configure_job(self, job):
        flags = DWORD()
        if not self.dll.GetHandleInformation(job, C.byref(flags)):
            raise _native_error("QUERY_JOB_HANDLE_FAILED")
        if flags.value & 1:  # HANDLE_FLAG_INHERIT
            raise ProbeError("JOB_HANDLE_UNEXPECTEDLY_INHERITABLE")
        limits = _EXTENDED_LIMIT()
        # No ACTIVE_PROCESS cap, BREAKAWAY_OK, SILENT_BREAKAWAY_OK, or CPU quota.
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.dll.SetInformationJobObject(job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                                                C.byref(limits), C.sizeof(limits)):
            raise _native_error("SET_KILL_ON_CLOSE_FAILED")

    def open_stream(self, path, *, input_stream=False):
        security = _SECURITY_ATTRIBUTES(C.sizeof(_SECURITY_ATTRIBUTES), None, True)
        handle = self.dll.CreateFileW(
            str(path), 0x80000000 if input_stream else 0x40000000,
            3, C.byref(security), 3 if input_stream else 1, 0x80, None,
        )  # GENERIC_READ/WRITE, SHARE_READ|WRITE, OPEN_EXISTING/CREATE_NEW
        if handle == INVALID_HANDLE_VALUE:
            raise _native_error("OPEN_CAPTURE_STREAM_FAILED")
        return handle

    def create_suspended(self, *, argv, cwd, env, job, streams, info):
        size = SIZE_T()
        self.dll.InitializeProcThreadAttributeList(None, 2, 0, C.byref(size))
        if not size.value:
            raise _native_error("ATTRIBUTE_SIZE_QUERY_FAILED")
        storage = C.create_string_buffer(size.value)
        if not self.dll.InitializeProcThreadAttributeList(storage, 2, 0, C.byref(size)):
            raise _native_error("ATTRIBUTE_INITIALIZATION_FAILED")
        # Both value buffers must remain alive until DeleteProcThreadAttributeList.
        stream_handles = (HANDLE * len(streams))(*streams)
        job_handles = (HANDLE * 1)(job)
        try:
            for key, values, code in (
                (PROC_THREAD_ATTRIBUTE_HANDLE_LIST, stream_handles, "HANDLE_LIST_ATTRIBUTE_FAILED"),
                (PROC_THREAD_ATTRIBUTE_JOB_LIST, job_handles, "JOB_LIST_ATTRIBUTE_FAILED"),
            ):
                if not self.dll.UpdateProcThreadAttribute(storage, 0, key, values,
                                                         C.sizeof(values), None, None):
                    raise _native_error(code)
            startup = _STARTUPINFOEXW()
            startup.StartupInfo.cb = C.sizeof(startup)
            startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES
            startup.StartupInfo.hStdInput, startup.StartupInfo.hStdOutput, startup.StartupInfo.hStdError = streams
            startup.lpAttributeList = C.cast(storage, C.c_void_p)
            command = C.create_unicode_buffer(subprocess.list2cmdline(argv))
            environment = C.create_unicode_buffer("\0".join(
                name + "=" + env[name] for name in sorted(env, key=str.casefold)) + "\0\0")
            flags = CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT | EXTENDED_STARTUPINFO_PRESENT
            if not self.dll.CreateProcessW(argv[0], command, None, None, True, flags,
                                           environment, str(cwd), C.byref(startup), C.byref(info)):
                raise _native_error("CREATE_SUSPENDED_ASSIGNMENT_FAILED")
            return info
        finally:
            self.dll.DeleteProcThreadAttributeList(storage)

    def check_membership(self, process, job):
        member = BOOL()
        if not self.dll.IsProcessInJob(process, job, C.byref(member)):
            raise _native_error("JOB_MEMBERSHIP_QUERY_FAILED")
        if not member.value:
            raise ProbeError("JOB_ASSIGNMENT_NOT_VERIFIED")

    def resume(self, thread):
        previous = self.dll.ResumeThread(thread)
        if previous == WAIT_FAILED:
            raise _native_error("RESUME_THREAD_FAILED")
        if previous != 1:
            raise ProbeError("UNEXPECTED_SUSPEND_COUNT")

    def accounting(self, job):
        value = _ACCOUNTING()
        returned = DWORD()
        if not self.dll.QueryInformationJobObject(job, JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
                                                  C.byref(value), C.sizeof(value), C.byref(returned)):
            raise _native_error("QUERY_ACCOUNTING_FAILED")
        if returned.value != C.sizeof(value):
            raise ProbeError("ACCOUNTING_SIZE_MISMATCH")
        return value

    def terminate_job(self, job):
        if not self.dll.TerminateJobObject(job, CANCEL_EXIT_CODE):
            raise _native_error("TERMINATE_JOB_FAILED")

    def terminate_process(self, process):
        if not self.dll.TerminateProcess(process, CANCEL_EXIT_CODE):
            raise _native_error("TERMINATE_SUSPENDED_ROOT_FAILED")

    def exit_if_signaled(self, process):
        wait = self.dll.WaitForSingleObject(process, 0)
        if wait == WAIT_TIMEOUT:
            return None
        if wait != WAIT_OBJECT_0:
            raise _native_error("WAIT_ROOT_FAILED")
        exit_code = DWORD()
        if not self.dll.GetExitCodeProcess(process, C.byref(exit_code)):
            raise _native_error("ROOT_EXIT_CODE_FAILED")
        # Even 259 is a real exit code once the process handle is signaled.
        return exit_code.value

    def close(self, handle):
        if not self.dll.CloseHandle(handle):
            raise _native_error("CLOSE_HANDLE_FAILED")


def _timeout(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ProbeError("INVALID_TIMEOUT")
    return float(value)


def _arguments(argv, cwd, env, report_dir):
    if isinstance(argv, (str, bytes)) or not argv:
        raise ProbeError("INVALID_ARGV")
    argv = tuple(argv)
    if any(not isinstance(arg, str) or "\0" in arg for arg in argv):
        raise ProbeError("INVALID_ARGV")
    executable = Path(argv[0])
    if not executable.is_absolute() or not executable.is_file() or executable.suffix.casefold() != ".exe":
        raise ProbeError("ABSOLUTE_EXECUTABLE_REQUIRED")
    cwd, report_dir = Path(cwd), Path(report_dir)
    if not cwd.is_absolute() or not cwd.is_dir() or not report_dir.is_absolute():
        raise ProbeError("ABSOLUTE_WORK_AND_REPORT_PATHS_REQUIRED")
    if not report_dir.name or report_dir.name in {".", ".."} or report_dir.exists() or report_dir.is_symlink():
        raise ProbeError("FRESH_REPORT_LEAF_REQUIRED")
    report_dir = report_dir.parent.resolve(strict=True) / report_dir.name
    copied_env = dict(env)
    folded = set()
    for key, value in copied_env.items():
        if (not isinstance(key, str) or not key or "=" in key or "\0" in key
                or not isinstance(value, str) or "\0" in value or key.casefold() in folded):
            raise ProbeError("INVALID_PER_CALL_ENVIRONMENT")
        folded.add(key.casefold())
    if "systemroot" not in folded:
        raise ProbeError("SYSTEMROOT_REQUIRED_IN_ENVIRONMENT")
    return argv, cwd.resolve(strict=True), copied_env, report_dir


class WindowsJobProbe:
    """Single-caller owner. Separate instances may be polled by one scheduler.

    Do not concurrently launch unrelated inherit-all processes while start runs:
    its short-lived inheritable standard-file handles are coordinator-local.
    The Job/process/thread handles are never inheritable. No global env/cwd moves.
    """
    def __init__(self, api, report_dir):
        self._api = api
        self.report_dir = report_dir
        self.stdout_path = report_dir / "stdout.bin"
        self.stderr_path = report_dir / "stderr.bin"
        self._job = None
        self._info = _PROCESS_INFORMATION()
        self._streams = []
        self._exit_code = None
        self._root_reaped = False
        self._resumed = False
        self._started = time.monotonic()
        self._state = "preparing"
        self._diagnostics = []
        self._last_accounting = None
        self.result = None

    @classmethod
    def start(cls, argv: Sequence[str], *, cwd: str | Path,
              env: Mapping[str, str], report_dir: str | Path) -> WindowsJobProbe:
        api = _Kernel32()  # Refuse Linux/old Windows before touching any files.
        argv, cwd, env, report_dir = _arguments(argv, cwd, env, report_dir)
        self = cls(api, report_dir)
        try:
            self._job = api.create_job()
            api.configure_job(self._job)
            report_dir.mkdir(parents=False, exist_ok=False)
            self._streams.append(api.open_stream("NUL", input_stream=True))
            for path in (self.stdout_path, self.stderr_path):
                self._streams.append(api.open_stream(path))
            # info is already owned before native creation writes returned handles.
            api.create_suspended(argv=argv, cwd=cwd, env=env, job=self._job,
                                 streams=self._streams, info=self._info)
            self._state = "suspended_assigned"
            api.check_membership(self._info.hProcess, self._job)
            self._close_streams()
            api.resume(self._info.hThread)
            self._resumed = True
            self._close_info_handle("hThread")
            self._state = "running"
            return self
        except BaseException as cause:
            code = cause.code if isinstance(cause, ProbeError) else "START_INTERRUPTED"
            self._diagnostics.append(code)
            try:
                self.cancel("start-refused", timeout=10)
            except ProbeError as cleanup_error:
                raise ProbeError("CLEANUP_INCOMPLETE", owner=self,
                                 diagnostic_codes=tuple(self._diagnostics)) from cleanup_error
            if isinstance(cause, ProbeError):
                cause.owner = self
                cause.diagnostic_codes = tuple(self._diagnostics)
                raise
            if isinstance(cause, (KeyboardInterrupt, SystemExit)):
                raise
            raise ProbeError(code, owner=self, diagnostic_codes=tuple(self._diagnostics)) from cause

    def _close_info_handle(self, name):
        handle = getattr(self._info, name)
        if handle:
            self._api.close(handle)
            setattr(self._info, name, None)

    def _close_streams(self):
        while self._streams:
            self._api.close(self._streams[-1])
            self._streams.pop()

    def _reap_root(self):
        if not self._info.hProcess:
            if not self._info.dwProcessId:
                self._root_reaped = True  # Launch never returned a process.
            return
        exit_code = self._api.exit_if_signaled(self._info.hProcess)
        if exit_code is not None:
            self._exit_code = exit_code
            self._close_info_handle("hThread")
            self._close_info_handle("hProcess")
            self._root_reaped = True

    def _snapshot(self, *, verified=False, elapsed=None):
        accounting = self._last_accounting
        return ProbeSnapshot(
            int(self._info.dwProcessId) or None, self._exit_code, self._root_reaped,
            int(accounting.ActiveProcesses) if accounting is not None else None,
            int(accounting.TotalProcesses) if accounting is not None else None,
            accounting.TotalUserTime / 10_000_000 if accounting is not None else None,
            accounting.TotalKernelTime / 10_000_000 if accounting is not None else None,
            time.monotonic() - self._started if elapsed is None else elapsed,
            verified, self._state,
        )

    def poll(self) -> ProbeSnapshot:
        if self.result is not None:
            return self.result.snapshot
        try:
            self._reap_root()
            if self._job:
                self._last_accounting = self._api.accounting(self._job)
            return self._snapshot()
        except ProbeError as error:
            self._last_accounting = None  # Never display stale counters as current.
            error.owner = self
            raise

    def _seal(self, reason):
        # Caller just observed ActiveProcesses==0 and reaped/closed the root.
        self._close_streams()
        self._close_info_handle("hThread")
        self._close_info_handle("hProcess")
        if self._job:
            self._api.close(self._job)
            self._job = None
        self._state = "closed"
        self.result = ProbeResult(self._snapshot(verified=True), reason,
                                  str(self.stdout_path), str(self.stderr_path),
                                  tuple(self._diagnostics))
        return self.result

    def finish(self, timeout: float = 30.0) -> ProbeResult:
        """Wait for the entire tree. Deadline cancels it, returning reason=timeout."""
        deadline = time.monotonic() + _timeout(timeout)
        if self.result is not None:
            return self.result
        while True:
            snapshot = self.poll()
            if snapshot.root_reaped and snapshot.active_processes == 0:
                try:
                    return self._seal("completed")
                except ProbeError as error:
                    self._state = "cleanup_incomplete"
                    self._diagnostics.append(error.code)
                    raise ProbeError("CLEANUP_INCOMPLETE", owner=self,
                                     diagnostic_codes=tuple(self._diagnostics)) from error
            if time.monotonic() >= deadline:
                return self.cancel("timeout", timeout=10.0)
            time.sleep(min(0.02, max(0.0, deadline - time.monotonic())))

    def cancel(self, reason: str = "cancelled", timeout: float = 10.0) -> ProbeResult:
        """Terminate, drain accounting, reap root, then close. Never deletes files.

        Incomplete cleanup keeps the Job handle owned and files intact for retry;
        coordinator exit still closes the last Job handle and kills owned members.
        """
        deadline = time.monotonic() + _timeout(timeout)
        if not isinstance(reason, str) or not reason:
            raise ProbeError("INVALID_CANCEL_REASON", owner=self)
        if self.result is not None:
            return self.result
        self._state = "cancelling"
        # Membership verification failure must kill the still-suspended root even
        # if the OS unexpectedly returned a process outside the requested Job.
        if self._info.hProcess and not self._resumed:
            try:
                self._api.terminate_process(self._info.hProcess)
            except ProbeError as error:
                self._diagnostics.append(error.code)
        if self._job:
            try:
                self._api.terminate_job(self._job)
            except ProbeError as error:
                self._diagnostics.append(error.code)
        while True:
            try:
                snapshot = self.poll()
                if snapshot.root_reaped and snapshot.active_processes == 0:
                    return self._seal(reason)
                if self._job is None and not self._info.dwProcessId:
                    # Job creation itself failed; no process/files were created.
                    # No ActiveProcesses observation is invented.
                    self._close_streams()
                    self._state = "closed_without_launch"
                    self.result = ProbeResult(self._snapshot(), reason, str(self.stdout_path),
                                              str(self.stderr_path), tuple(self._diagnostics))
                    return self.result
            except ProbeError as error:
                if error.code not in self._diagnostics:
                    self._diagnostics.append(error.code)
            if time.monotonic() >= deadline:
                self._state = "cleanup_incomplete"
                raise ProbeError("CLEANUP_INCOMPLETE", owner=self,
                                 diagnostic_codes=tuple(self._diagnostics))
            time.sleep(min(0.02, max(0.0, deadline - time.monotonic())))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if self.result is None:
            self.cancel("context-exit", timeout=10)
        return False
