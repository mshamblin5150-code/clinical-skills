"""Allowlisted synthetic processes, never repository audit or private inputs.

Run only as descendants of the reviewed qualification controller. A blocked
fixture is deliberate and is terminated by its owning job, not a probe timeout.
"""

from __future__ import annotations

import argparse
import ctypes as c
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

from windows_serial_envelope import Plan, run_owned


def emit(args, kind, **fields):
    print(json.dumps({"nonce": args.nonce, "kind": kind, **fields},
                     separators=(",", ":")), flush=True)


def wait_go():
    while True:
        if sys.stdin.buffer.readline() == b"GO\n":
            return
        # EOF must not make the last-handle-close control pass accidentally.
        time.sleep(0.01)


def spawn(args, role):
    return subprocess.Popen(
        [sys.executable, "-B", str(Path(__file__).resolve()), "--recipe", args.recipe,
         "--role", role, "--destination", args.destination, "--sources", args.sources,
         "--job-start-ms", str(args.job_start_ms), "--case-end-ms", str(args.case_end_ms),
         "--nonce", args.nonce,
         *(["--parent-pid", str(os.getpid())] if args.recipe == "survivor" else [])],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, close_fds=True,
    )


def child_ready(child):
    row = json.loads(child.stdout.readline())
    if row.get("kind") != "ready" or not isinstance(row.get("pids"), list):
        raise RuntimeError("synthetic child protocol refused")
    return row["pids"]


def finish_child(child):
    child.stdin.write(b"GO\n")
    child.stdin.flush()
    child.stdin.close()
    # Descendants produce only the single small readiness row already consumed.
    code = child.wait()
    child.stdout.close()
    if code:
        raise RuntimeError("synthetic descendant failed")


def ordinary(args):
    if args.role == "leaf":
        if args.recipe == "survivor":
            # The parent is still blocked waiting for READY, so its supplied
            # PID cannot have been reused. Open only a noninherited wait handle;
            # it never grants kill authority or transfers a job handle.
            kernel = c.WinDLL("kernel32", use_last_error=True)
            kernel.OpenProcess.argtypes = [c.c_uint32, c.c_int32, c.c_uint32]
            kernel.OpenProcess.restype = c.c_void_p
            kernel.WaitForSingleObject.argtypes = [c.c_void_p, c.c_uint32]
            kernel.WaitForSingleObject.restype = c.c_uint32
            kernel.CloseHandle.argtypes = [c.c_void_p]
            kernel.CloseHandle.restype = c.c_int32
            parent = kernel.OpenProcess(0x100000, False, args.parent_pid)
            if not parent:
                raise RuntimeError("synthetic parent wait identity unproven")
            try:
                emit(args, "ready", pids=[os.getpid()])
                if kernel.WaitForSingleObject(parent, 0xFFFFFFFF) != 0:
                    raise RuntimeError("synthetic parent exit unproven")
            finally:
                if not kernel.CloseHandle(parent):
                    raise RuntimeError("synthetic parent handle cleanup unproven")
            # N4 alone: finish 200 ms after confirmed root exit, inside the
            # former grace. Later emptiness must not erase the cleanup fault.
            time.sleep(0.2)
        else:
            emit(args, "ready", pids=[os.getpid()])
            wait_go()
        return 0
    child = spawn(args, "leaf" if args.role == "branch" else "branch")
    pids = [os.getpid(), *child_ready(child)]
    if args.role == "root":
        # Task-owned fixed-size evidence used only by the N8 supervisor.
        marker = Path(args.destination) / "lineage.json"
        raw = json.dumps(pids, separators=(",", ":")).encode()
        if len(raw) > 256:
            raise RuntimeError("synthetic lineage cap")
        temporary = marker.with_suffix(".tmp")
        temporary.write_bytes(raw)
        if temporary.read_bytes() != raw:
            raise RuntimeError("synthetic lineage readback differs")
        temporary.replace(marker)
    emit(args, "ready", pids=pids)
    wait_go()
    finish_child(child)
    if args.role == "root":
        emit(args, "terminal", status=0)
    return 0


def breakaway(args):
    # Same executable and arguments first prove ordinary launch. Neither probe
    # executes its suspended image. The only termination targets are handles
    # returned by these specific CreateProcessW calls.
    DWORD, HANDLE, BOOL = c.c_uint32, c.c_void_p, c.c_int32
    class Startup(c.Structure):
        _fields_ = [("cb", DWORD), ("reserved", c.c_wchar_p), ("desktop", c.c_wchar_p),
                    ("title", c.c_wchar_p), ("x", DWORD), ("y", DWORD),
                    ("width", DWORD), ("height", DWORD), ("xchars", DWORD),
                    ("ychars", DWORD), ("fill", DWORD), ("flags", DWORD),
                    ("show", c.c_uint16), ("reserved_size", c.c_uint16),
                    ("reserved_bytes", HANDLE), ("stdin", HANDLE),
                    ("stdout", HANDLE), ("stderr", HANDLE)]
    class Process(c.Structure):
        _fields_ = [("process", HANDLE), ("thread", HANDLE), ("pid", DWORD), ("tid", DWORD)]
    dll = c.WinDLL("kernel32", use_last_error=True)
    signatures = {
        "CreateProcessW": (BOOL, [c.c_wchar_p, c.c_wchar_p, HANDLE, HANDLE, BOOL,
                                 DWORD, HANDLE, c.c_wchar_p, HANDLE, c.POINTER(Process)]),
        "IsProcessInJob": (BOOL, [HANDLE, HANDLE, c.POINTER(BOOL)]),
        "TerminateProcess": (BOOL, [HANDLE, DWORD]),
        "WaitForSingleObject": (DWORD, [HANDLE, DWORD]),
        "CloseHandle": (BOOL, [HANDLE]),
    }
    for name, (result, arguments) in signatures.items():
        getattr(dll, name).restype, getattr(dll, name).argtypes = result, arguments
    def attempt(flags):
        startup, process = Startup(), Process()
        startup.cb = c.sizeof(startup)
        text = c.create_unicode_buffer(subprocess.list2cmdline([sys.executable, "-B", "-c", "pass"]))
        ok = bool(dll.CreateProcessW(sys.executable, text, None, None, False,
                                     flags | 4, None, None, c.byref(startup), c.byref(process)))
        error, member, reaped = c.get_last_error() if not ok else 0, BOOL(), False
        membership_ok = False
        try:
            if ok:
                membership_ok = bool(dll.IsProcessInJob(process.process, None, c.byref(member)))
                if flags == 0:
                    emit(args, "ready", stage="ordinary_suspended", pids=[os.getpid(), process.pid])
                    wait_go()
                if not dll.TerminateProcess(process.process, 78):
                    raise RuntimeError("suspended probe termination unproven")
                # One outer controller deadline owns this wait too. There is no
                # detached fallback or retry and an unexpected breakaway never runs.
                reaped = dll.WaitForSingleObject(process.process, 5000) == 0
                if not reaped:
                    raise RuntimeError("suspended probe reap unproven")
                if not membership_ok:
                    raise RuntimeError("probe membership unproven")
            return ok, error, bool(member.value), reaped
        finally:
            closed = True
            for handle in (process.thread, process.process):
                if handle and not dll.CloseHandle(handle):
                    closed = False
            if not closed:
                raise RuntimeError("probe handle cleanup unproven")
    try:
        ordinary_ok, _, member, reaped = attempt(0)
        if not ordinary_ok or not member or not reaped:
            emit(args, "terminal", status=1, ordinary_launch_succeeded=False)
            return 1
        escaped, error, escaped_member, escaped_reaped = attempt(0x01000000)
    except BaseException:
        emit(args, "terminal", status=1, cleanup_unproven=True)
        return 1
    rejected = not escaped and error == 5  # ERROR_ACCESS_DENIED, after positive control
    emit(args, "terminal", status=0 if ordinary_ok and member and reaped and rejected else 1,
         ordinary_launch_succeeded=ordinary_ok and member and reaped,
         ordinary_any_job_member=member, ordinary_reaped=reaped,
         breakaway_created=escaped, breakaway_rejected=rejected, native_error=error,
         breakaway_any_job_member=escaped_member if escaped else None,
         breakaway_reaped=escaped_reaped if escaped else None)
    return 0 if ordinary_ok and member and reaped and rejected else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recipe", required=True)
    parser.add_argument("--role", choices=("root", "branch", "leaf"), default="root")
    parser.add_argument("--parent-pid", type=int, default=0)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--sources", required=True)
    parser.add_argument("--job-start-ms", type=int, required=True)
    parser.add_argument("--case-end-ms", type=int, required=True)
    parser.add_argument("--nonce", required=True)
    args = parser.parse_args()
    if os.name != "nt" or sys.version_info[:3] != (3, 14, 4):
        return 1
    if args.recipe in {"ordinary", "deadline"} or args.role != "root":
        return ordinary(args)
    if args.recipe == "nested":
        emit(args, "ready", pids=[os.getpid()])
        wait_go()
        inner = run_owned(Plan("ordinary", Path(args.destination) / "inner",
                               json.loads(args.sources), args.job_start_ms,
                               args.case_end_ms, args.nonce + "-inner"))
        emit(args, "terminal", status=0 if inner["success"] else 1, inner=inner)
        return 0 if inner["success"] else 1
    if args.recipe == "supervisor_loss":
        # This process alone holds the inner job handle. Outer accounting,
        # never an extra inner handle, observes its last-close effect.
        target = Path(args.destination) / "inner"
        kernel = c.WinDLL("kernel32", use_last_error=True)
        kernel.GetTickCount64.restype = c.c_uint64
        # Actual inner five-second deadline begins later than this conservative
        # boundary. Emptiness before it rules out inner deadline termination.
        last_close_before = int(kernel.GetTickCount64()) + 5000
        threading.Thread(target=lambda: run_owned(Plan(
            "deadline", target, json.loads(args.sources), args.job_start_ms,
            args.case_end_ms, args.nonce + "-inner")), daemon=True).start()
        while not (target / "lineage.json").is_file():
            time.sleep(0.005)
        pids = json.loads((target / "lineage.json").read_bytes())
        emit(args, "ready", pids=[os.getpid(), *pids], last_close_before_ms=last_close_before)
        wait_go()
        os._exit(73)
    if args.recipe == "survivor":
        child = spawn(args, "leaf")
        emit(args, "ready", pids=[os.getpid(), *child_ready(child)])
        wait_go()
        emit(args, "terminal", status=0)
        # Deliberately leave its owned child alive at root exit. It finishes
        # shortly after confirmed root exit; retain the fault even after it ends.
        child.stdin.close()
        child.stdout.close()
        return 0
    emit(args, "ready", pids=[os.getpid()])
    wait_go()
    if args.recipe == "breakaway":
        return breakaway(args)
    if args.recipe == "output":
        chunk = b"X" * 4096
        # Reserve one chunk for stdout protocol rows within the 2 MiB ceiling.
        for _ in range(511):
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            sys.stderr.buffer.write(chunk)
            sys.stderr.buffer.flush()
        emit(args, "terminal", status=0)
        return 0
    if args.recipe == "protocol_fault":
        emit(args, "terminal", status=1, evidence_faults=["synthetic_delayed_write"])
        return 7
    if args.recipe == "protocol_exit":
        emit(args, "terminal", status=0)
        return 7
    if args.recipe == "protocol_missing":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
