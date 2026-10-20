"""Synthetic hosted controls. Author has NOT executed or graded this artifact.

Run only after independent review, on the separately authorized Windows host:
  python windows_job_probe_controls.py --run --report-dir ABSENT_ABSOLUTE_LEAF
No clinical files, network requests, installations, or host-setting changes.
Capture evidence remains until disposable-runner teardown. Cleanup assertions
verify process-tree drain and handle closure, not filesystem removal.
"""
from __future__ import annotations

import argparse
import ctypes
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest import mock

import windows_job_probe as owner_module
from windows_job_probe import ProbeError, WindowsJobProbe


SCRIPT = Path(__file__).resolve()
WAIT_SECONDS = 20.0
OUTPUT_BYTES = 4 * 1024 * 1024
DECLARED_CONTROL_IDS = (
    "normal_tree_cpu_and_active_zero",
    "separate_large_output",
    "cancel_tree_and_retained_evidence",
    "failed_root_keeps_descendants_owned",
    "cleanup_unread_retains_files_and_can_recover",
    "real_invalid_assignment_refused",
    "membership_refusal_terminates_suspended_root",
    "coordinator-death-running",
    "coordinator-death-suspended",
)
PUBLIC_DIAGNOSTIC_CODES = frozenset({
    "CONTROL_OPTIMIZATION_UNSUPPORTED", "CONTROL_PLATFORM_UNSUPPORTED",
    "CONTROL_PROCESS_CLEANUP_INCOMPLETE", "SYNTHETIC_MEMBERSHIP_REFUSAL",
    "ATOMIC_JOB_ASSIGNMENT_PLATFORM_UNSUPPORTED", "CREATE_JOB_FAILED",
    "QUERY_JOB_HANDLE_FAILED", "JOB_HANDLE_UNEXPECTEDLY_INHERITABLE",
    "SET_KILL_ON_CLOSE_FAILED", "OPEN_CAPTURE_STREAM_FAILED",
    "ATTRIBUTE_SIZE_QUERY_FAILED", "ATTRIBUTE_INITIALIZATION_FAILED",
    "HANDLE_LIST_ATTRIBUTE_FAILED", "JOB_LIST_ATTRIBUTE_FAILED",
    "CREATE_SUSPENDED_ASSIGNMENT_FAILED", "JOB_MEMBERSHIP_QUERY_FAILED",
    "JOB_ASSIGNMENT_NOT_VERIFIED", "RESUME_THREAD_FAILED", "UNEXPECTED_SUSPEND_COUNT",
    "QUERY_ACCOUNTING_FAILED", "ACCOUNTING_SIZE_MISMATCH", "TERMINATE_JOB_FAILED",
    "TERMINATE_SUSPENDED_ROOT_FAILED", "WAIT_ROOT_FAILED", "ROOT_EXIT_CODE_FAILED",
    "CLOSE_HANDLE_FAILED", "INVALID_TIMEOUT", "INVALID_ARGV",
    "ABSOLUTE_EXECUTABLE_REQUIRED", "ABSOLUTE_WORK_AND_REPORT_PATHS_REQUIRED",
    "FRESH_REPORT_LEAF_REQUIRED", "INVALID_PER_CALL_ENVIRONMENT",
    "SYSTEMROOT_REQUIRED_IN_ENVIRONMENT", "START_INTERRUPTED",
    "CLEANUP_INCOMPLETE", "INVALID_CANCEL_REASON",
})


def require_unoptimized():
    # Never an assert: -O/PYTHONOPTIMIZE must not erase this safety preflight.
    if sys.flags.optimize != 0:
        raise ProbeError("CONTROL_OPTIMIZATION_UNSUPPORTED")


def failure_report(error):
    """Safe structural diagnostics only: no exception text, source text, or locals."""
    known_types = {"AssertionError", "ProbeError", "OSError", "PermissionError",
                   "FileNotFoundError", "FileExistsError", "TimeoutExpired",
                   "RuntimeError", "ValueError", "TypeError", "KeyboardInterrupt",
                   "SystemExit"}
    type_name = type(error).__name__
    codes = []
    if isinstance(error, ProbeError):
        for code in (error.code, *error.diagnostic_codes):
            if code in PUBLIC_DIAGNOSTIC_CODES and code not in codes:
                codes.append(code)
    trusted_files = {str(SCRIPT): SCRIPT.name,
                     str(Path(owner_module.__file__).resolve()): "windows_job_probe.py"}
    frames = []
    node = error.__traceback__
    while node is not None:
        frame = node.tb_frame
        source = trusted_files.get(str(Path(frame.f_code.co_filename).resolve()))
        if source is not None:
            frames.append({"file": source, "function": frame.f_code.co_name,
                           "line": node.tb_lineno})
        node = node.tb_next
    return {"schema": "windows-job-probe-controls-v1", "status": "failed",
            "error_type": type_name if type_name in known_types else "OtherException",
            "diagnostic_codes": codes, "source_frames": frames[-16:],
            "optimization_level": sys.flags.optimize,
            "files_retained": True, "process_cleanup_verified": False}


def wait_for(predicate, seconds=WAIT_SECONDS):
    end = time.monotonic() + seconds
    while True:
        value = predicate()
        if value:
            return value
        if time.monotonic() >= end:
            raise AssertionError("synthetic readiness deadline expired")
        time.sleep(0.02)


def read_pid(path):
    try:
        return int(path.read_text(encoding="ascii"))
    except (FileNotFoundError, ValueError):
        return None


def write_pid(root, role):
    (root / (role + ".creation")).write_text(str(creation_time()), encoding="ascii")
    (root / (role + ".pid")).write_text(str(os.getpid()), encoding="ascii")


def creation_time(handle=None):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.argtypes = []
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    kernel.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_uint64)] * 4
    kernel.GetProcessTimes.restype = ctypes.c_int32
    values = [ctypes.c_uint64() for _ in range(4)]
    handle = kernel.GetCurrentProcess() if handle is None else handle
    if not kernel.GetProcessTimes(handle, *(ctypes.byref(value) for value in values)):
        raise ctypes.WinError(ctypes.get_last_error())
    return values[0].value


def child(role, root, mode):
    """All descendants use ordinary CreateProcess ancestry through subprocess."""
    write_pid(root, role)
    if role != "grandchild":
        next_role = "child" if role == "root" else "grandchild"
        process = subprocess.Popen(
            [sys.executable, str(SCRIPT), "--child", next_role,
             "--report-dir", str(root), "--mode", mode],
            cwd=str(root), env=dict(os.environ),
        )
        wait_for(lambda: read_pid(root / (next_role + ".pid")))
        if role == "root" and mode == "failure":
            wait_for(lambda: read_pid(root / "grandchild.pid"))
            return 7
        if mode == "normal":
            return process.wait(timeout=WAIT_SECONDS)
    elif mode == "normal":
        stop = time.process_time() + 0.2
        while time.process_time() < stop:
            sum(range(200))
        return 0
    while True:
        time.sleep(1)


def output_child(root):
    write_pid(root, "root")
    # Alternating writes exceed ordinary pipe capacity in both streams.
    # Exact homogeneous bytes make cross-stream mixing detectable.
    for _ in range(OUTPUT_BYTES // 65536):
        sys.stdout.buffer.write(b"O" * 65536)
        sys.stdout.buffer.flush()
        sys.stderr.buffer.write(b"E" * 65536)
        sys.stderr.buffer.flush()
    return 0


def coordinator(root, before_resume):
    api_class = owner_module._Kernel32
    if before_resume:
        class StopBeforeResume(api_class):
            def create_suspended(self, **kwargs):
                info = super().create_suspended(**kwargs)
                (root / "suspended.creation").write_text(str(creation_time(info.hProcess)), encoding="ascii")
                (root / "suspended.pid").write_text(str(info.dwProcessId), encoding="ascii")
                return info

            def resume(self, thread):
                (root / "before-resume.ready").write_text("ready", encoding="ascii")
                while True:
                    time.sleep(1)

        owner_module._Kernel32 = StopBeforeResume
    probe = WindowsJobProbe.start(
        [sys.executable, str(SCRIPT), "--child", "root", "--mode", "hang",
         "--report-dir", str(root)],
        cwd=root, env=dict(os.environ), report_dir=root / "inner-capture",
    )
    # Deliberately retain ownership. The outer control kills ONLY this process.
    (root / "coordinator.ready").write_text(str(probe.poll().root_pid), encoding="ascii")
    while True:
        time.sleep(1)


class ProcessWitness:
    """Independent live kernel handles, not PID-existence guesses or log claims."""
    def __init__(self, pid, expected_creation):
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel = kernel
        kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32]
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        kernel.WaitForSingleObject.restype = ctypes.c_uint32
        kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel.CloseHandle.restype = ctypes.c_int32
        access = 0x00100000 | 0x1000  # SYNCHRONIZE | QUERY_LIMITED_INFORMATION, never terminate.
        self.handle = kernel.OpenProcess(access, False, pid)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            assert creation_time(self.handle) == expected_creation, "PID identity changed"
            assert kernel.WaitForSingleObject(self.handle, 0) == 0x102, "witness must first be live"
        except BaseException:
            self.close()
            raise

    def wait_dead(self):
        value = self.kernel.WaitForSingleObject(self.handle, int(WAIT_SECONDS * 1000))
        assert value == 0, "owned process did not become signaled after coordinator death"

    def close(self):
        if self.handle:
            if not self.kernel.CloseHandle(self.handle):
                raise ctypes.WinError(ctypes.get_last_error())
            self.handle = None


def run_controls(root):
    require_unoptimized()
    if os.name != "nt":
        raise ProbeError("CONTROL_PLATFORM_UNSUPPORTED")
    root.mkdir(parents=False, exist_ok=False)
    owners = []
    results = []
    original_env, original_cwd = dict(os.environ), os.getcwd()

    def launch(name, mode):
        case = root / name
        case.mkdir()
        role = "--output-child" if mode == "output" else "--child"
        argv = [sys.executable, str(SCRIPT), role]
        if role == "--child":
            argv += ["root", "--mode", mode]
        argv += ["--report-dir", str(case)]
        probe = WindowsJobProbe.start(argv, cwd=case, env=dict(os.environ),
                                      report_dir=case / "capture")
        owners.append(probe)
        return case, probe

    def check_terminal(probe, result, reason):
        snapshot = result.snapshot
        assert result.reason == reason
        assert snapshot.root_reaped and snapshot.active_processes == 0
        assert snapshot.cleanup_verified and snapshot.state == "closed"
        assert snapshot.tree_cpu_seconds is not None
        assert snapshot.tree_cpu_seconds >= 0
        assert probe.poll() == snapshot, "closed snapshot must be stable"
        assert Path(result.stdout_path).is_file() and Path(result.stderr_path).is_file()

    try:
        case, probe = launch("normal-tree", "normal")
        result = probe.finish(timeout=WAIT_SECONDS)
        check_terminal(probe, result, "completed")
        assert result.snapshot.root_exit_code == 0
        assert result.snapshot.total_processes == 3
        assert result.snapshot.tree_cpu_seconds >= 0.1
        results.append({"control": "normal_tree_cpu_and_active_zero", "result": asdict(result)})
        assert (case / "capture").is_dir(), "capture evidence must remain"

        case, probe = launch("large-output", "output")
        result = probe.finish(timeout=WAIT_SECONDS)
        check_terminal(probe, result, "completed")
        assert result.snapshot.root_exit_code == 0
        assert Path(result.stdout_path).read_bytes() == b"O" * OUTPUT_BYTES
        assert Path(result.stderr_path).read_bytes() == b"E" * OUTPUT_BYTES
        results.append({"control": "separate_large_output", "bytes_each": OUTPUT_BYTES})

        case, probe = launch("cancel-tree", "hang")
        wait_for(lambda: read_pid(case / "grandchild.pid"))
        assert probe.poll().active_processes == 3
        assert not hasattr(probe, "delete_owned_files"), "capture deletion API must be absent"
        assert (case / "capture" / "stdout.bin").is_file()
        assert (case / "capture" / "stderr.bin").is_file()
        result = probe.cancel("synthetic-cancel", timeout=WAIT_SECONDS)
        check_terminal(probe, result, "synthetic-cancel")
        results.append({"control": "cancel_tree_and_retained_evidence", "result": asdict(result)})

        case, probe = launch("failed-worker", "failure")
        wait_for(lambda: probe.poll().root_reaped)
        snapshot = probe.poll()
        assert snapshot.root_exit_code == 7 and snapshot.active_processes == 2
        result = probe.cancel("worker-failure", timeout=WAIT_SECONDS)
        check_terminal(probe, result, "worker-failure")
        results.append({"control": "failed_root_keeps_descendants_owned", "result": asdict(result)})

        case, probe = launch("cleanup-unread", "hang")
        wait_for(lambda: read_pid(case / "grandchild.pid"))
        with mock.patch.object(probe._api, "accounting", side_effect=ProbeError("QUERY_ACCOUNTING_FAILED")):
            try:
                probe.cancel("synthetic-query-failure", timeout=1)
            except ProbeError as error:
                assert error.code == "CLEANUP_INCOMPLETE"
            else:
                raise AssertionError("unread accounting was reported as cleanup verified")
            assert probe.result is None, "unread process cleanup must not produce a verified result"
            assert not hasattr(probe, "delete_owned_files")
        assert (case / "capture" / "stdout.bin").exists()
        result = probe.cancel("retry-after-query-restored", timeout=WAIT_SECONDS)
        check_terminal(probe, result, "retry-after-query-restored")
        results.append({"control": "cleanup_unread_retains_files_and_can_recover", "result": asdict(result)})

        case = root / "assignment-refusal"
        case.mkdir()
        api_class = owner_module._Kernel32

        class InvalidJobAssignment(api_class):
            def create_suspended(self, **kwargs):
                # Real Windows validation receives an invalid JOB_LIST handle.
                # No successful unmanaged creation is substituted.
                kwargs["job"] = ctypes.c_void_p(-1).value
                return super().create_suspended(**kwargs)

            def resume(self, thread):
                raise AssertionError("assignment failure must never reach ResumeThread")

        with mock.patch.object(owner_module, "_Kernel32", InvalidJobAssignment):
            try:
                WindowsJobProbe.start(
                    [sys.executable, str(SCRIPT), "--child", "root", "--mode", "hang",
                     "--report-dir", str(case)],
                    cwd=case, env=dict(os.environ), report_dir=case / "capture",
                )
            except ProbeError as error:
                assert error.code in {"CREATE_SUSPENDED_ASSIGNMENT_FAILED", "JOB_LIST_ATTRIBUTE_FAILED"}
                probe = error.owner
                assert probe is not None
                owners.append(probe)
                assert probe.result.snapshot.cleanup_verified
                assert probe.result.snapshot.active_processes == 0
                assert not (case / "root.pid").exists()
                results.append({"control": "real_invalid_assignment_refused", "code": error.code,
                                "result": asdict(probe.result)})
            else:
                raise AssertionError("invalid job assignment unexpectedly launched")

        case = root / "membership-refusal"
        case.mkdir()

        class RefuseMembership(api_class):
            def check_membership(self, process, job):
                super().check_membership(process, job)
                raise ProbeError("SYNTHETIC_MEMBERSHIP_REFUSAL")

            def resume(self, thread):
                raise AssertionError("unverified membership must never reach ResumeThread")

        with mock.patch.object(owner_module, "_Kernel32", RefuseMembership):
            try:
                WindowsJobProbe.start(
                    [sys.executable, str(SCRIPT), "--child", "root", "--mode", "hang",
                     "--report-dir", str(case)],
                    cwd=case, env=dict(os.environ), report_dir=case / "capture",
                )
            except ProbeError as error:
                assert error.code == "SYNTHETIC_MEMBERSHIP_REFUSAL"
                probe = error.owner
                assert probe is not None
                owners.append(probe)
                assert probe.result.snapshot.cleanup_verified
                assert probe.result.snapshot.root_reaped
                assert probe.result.snapshot.total_processes == 1
                assert probe.result.snapshot.active_processes == 0
                assert not (case / "root.pid").exists()
                results.append({"control": "membership_refusal_terminates_suspended_root",
                                "result": asdict(probe.result)})
            else:
                raise AssertionError("unverified membership unexpectedly resumed")

        for before_resume in (False, True):
            case = root / ("coordinator-death-suspended" if before_resume else "coordinator-death-running")
            case.mkdir()
            argv = [sys.executable, str(SCRIPT), "--coordinator", "--report-dir", str(case)]
            if before_resume:
                argv.append("--before-resume")
            guard = WindowsJobProbe.start(argv, cwd=case, env=dict(os.environ), report_dir=case / "guard")
            owners.append(guard)
            witnesses = []
            try:
                if before_resume:
                    wait_for(lambda: (case / "before-resume.ready").exists())
                    roles = ["suspended"]
                    pids = [wait_for(lambda: read_pid(case / "suspended.pid"))]
                    assert not (case / "root.pid").exists(), "suspended code executed"
                else:
                    wait_for(lambda: (case / "coordinator.ready").exists())
                    wait_for(lambda: read_pid(case / "grandchild.pid"))
                    roles = ["root", "child", "grandchild"]
                    pids = [read_pid(case / (role + ".pid")) for role in roles]
                for pid, role in zip(pids, roles):
                    witnesses.append(ProcessWitness(pid, read_pid(case / (role + ".creation"))))
                # Kill only the original CreateProcess-returned coordinator handle.
                # No PID-opened witness has termination rights.
                guard._api.terminate_process(guard._info.hProcess)
                for witness in witnesses:
                    witness.wait_dead()
                # Release independent handles before the Job counter emptiness check.
                for witness in witnesses:
                    witness.close()
                result = guard.finish(timeout=WAIT_SECONDS)
                check_terminal(guard, result, "completed")
                results.append({"control": case.name, "observed_processes_gone": len(pids),
                                "result": asdict(result)})
                # The deceased inner owner cannot certify its own cleanup. Retain its
                # capture files as evidence; no unsafe recursive cleanup follows.
            finally:
                for witness in witnesses:
                    witness.close()

        passed_ids = tuple(result["control"] for result in results)
        assert passed_ids == DECLARED_CONTROL_IDS, "control population missing, duplicated, or reordered"
        assert dict(os.environ) == original_env and os.getcwd() == original_cwd
        for probe in owners:
            assert probe.result is not None and probe.result.snapshot.cleanup_verified
            assert probe.stdout_path.is_file() and probe.stderr_path.is_file()
        return {"schema": "windows-job-probe-controls-v1", "status": "passed",
                "platform": sys.platform, "python": sys.version,
                "optimization_level": sys.flags.optimize,
                "files_retained": True, "process_cleanup_verified": True,
                "declared_control_ids": DECLARED_CONTROL_IDS,
                "passed_control_ids": passed_ids,
                "planned_count": len(DECLARED_CONTROL_IDS), "passed_count": len(results),
                "failed_count": 0, "skipped_count": 0,
                "controls": results, "retained_evidence_root": str(root)}
    finally:
        cleanup_errors = []
        for probe in reversed(owners):
            if probe.result is None or not probe.result.snapshot.cleanup_verified:
                try:
                    probe.cancel("control-finally", timeout=WAIT_SECONDS)
                except ProbeError as error:
                    cleanup_errors.append(error.code)
        if cleanup_errors:
            raise ProbeError("CONTROL_PROCESS_CLEANUP_INCOMPLETE",
                             diagnostic_codes=tuple(cleanup_errors))


def main():
    try:
        require_unoptimized()
    except ProbeError as error:
        print(json.dumps(failure_report(error), sort_keys=True))
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--run", action="store_true")
    action.add_argument("--child", choices=("root", "child", "grandchild"))
    action.add_argument("--output-child", action="store_true")
    action.add_argument("--coordinator", action="store_true")
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("normal", "hang", "failure"), default="hang")
    parser.add_argument("--before-resume", action="store_true")
    args = parser.parse_args()
    root = args.report_dir.resolve()
    if args.child:
        return child(args.child, root, args.mode)
    if args.output_child:
        return output_child(root)
    if args.coordinator:
        return coordinator(root, args.before_resume)
    try:
        report = run_controls(root)
    except BaseException as error:
        print(json.dumps(failure_report(error), sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    # Integrated location: <observer checkout>/diagnostics/this_file.py.
    # Reuse unchanged repository command policy; imports alone change no streams.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    from console_codec import require_python_floor, use_utf8

    use_utf8()
    require_python_floor()
    raise SystemExit(main())
