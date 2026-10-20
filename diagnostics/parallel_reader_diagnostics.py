"""Safe exception identity plus optional bounded private, never uploaded detail."""

from __future__ import annotations

from pathlib import Path
import traceback


SAFE_SOURCES = {
    "measure_parallel_readers.py", "parallel_reader_scheduler.py",
    "parallel_reader_capture.py", "parallel_reader_diagnostics.py",
    "test_parallel_observer_controls.py", "test_parallel_reader_controls.py",
    "windows_job_probe.py", "windows_job_probe_controls.py",
}
SAFE_CHILD_TYPES = {"ProbeError", "AssertionError", "RuntimeError", "ValueError", "TypeError",
                    "OSError", "FileNotFoundError", "PermissionError", "TimeoutError"}
SAFE_PROBE_CODES = {
    "ATOMIC_JOB_ASSIGNMENT_PLATFORM_UNSUPPORTED", "CREATE_JOB_FAILED", "QUERY_JOB_HANDLE_FAILED",
    "JOB_HANDLE_UNEXPECTEDLY_INHERITABLE", "SET_KILL_ON_CLOSE_FAILED", "OPEN_CAPTURE_STREAM_FAILED",
    "ATTRIBUTE_SIZE_QUERY_FAILED", "ATTRIBUTE_INITIALIZATION_FAILED", "CREATE_SUSPENDED_ASSIGNMENT_FAILED",
    "JOB_MEMBERSHIP_QUERY_FAILED", "JOB_ASSIGNMENT_NOT_VERIFIED", "RESUME_THREAD_FAILED",
    "UNEXPECTED_SUSPEND_COUNT", "QUERY_ACCOUNTING_FAILED", "ACCOUNTING_SIZE_MISMATCH",
    "TERMINATE_JOB_FAILED", "TERMINATE_SUSPENDED_ROOT_FAILED", "WAIT_ROOT_FAILED", "ROOT_EXIT_CODE_FAILED",
    "CLOSE_HANDLE_FAILED", "INVALID_TIMEOUT", "INVALID_ARGV", "ABSOLUTE_EXECUTABLE_REQUIRED",
    "ABSOLUTE_WORK_AND_REPORT_PATHS_REQUIRED", "FRESH_REPORT_LEAF_REQUIRED", "INVALID_PER_CALL_ENVIRONMENT",
    "SYSTEMROOT_REQUIRED_IN_ENVIRONMENT", "START_INTERRUPTED", "CLEANUP_INCOMPLETE", "INVALID_CANCEL_REASON",
    "CLEANUP_NOT_VERIFIED", "HANDLE_LIST_ATTRIBUTE_FAILED", "JOB_LIST_ATTRIBUTE_FAILED",
    "CONTROL_OPTIMIZATION_UNSUPPORTED", "CONTROL_PLATFORM_UNSUPPORTED",
    "CONTROL_PROCESS_CLEANUP_INCOMPLETE", "SYNTHETIC_MEMBERSHIP_REFUSAL",
}


def child_failure_diagnostic(result):
    """Only verified schema fields survive; raw output and messages stay private."""
    import json

    public = {"child_exit_code": result.snapshot.root_exit_code, "exception_type": "UnreadChildFailure",
              "diagnostic_codes": [], "source_frames": [], "child_receipt_read": False}
    try:
        with Path(result.stdout_path).open("rb") as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            return public
        row = json.loads(raw)
        if not isinstance(row, dict):
            return public
        public["child_receipt_read"] = True
        kind = row.get("error_type")
        public["exception_type"] = kind if kind in SAFE_CHILD_TYPES else "OtherChildFailure"
        codes = row.get("diagnostic_codes", [])
        if isinstance(codes, list):
            public["diagnostic_codes"] = [code for code in codes[:32]
                                          if isinstance(code, str) and code in SAFE_PROBE_CODES]
        frames = row.get("source_frames", [])
        if isinstance(frames, list):
            for frame in frames[-8:]:
                if not isinstance(frame, dict):
                    continue
                source = frame.get("file", frame.get("source"))
                if source not in SAFE_SOURCES:
                    continue
                line, function = frame.get("line"), frame.get("function")
                if isinstance(line, int) and 0 < line < 1000000 and isinstance(function, str) and function.isidentifier() and len(function) <= 100:
                    public["source_frames"].append({"source": source, "line": line, "function": function})
        for key in ("tests_run", "failures", "errors", "failed_count", "passed_count", "skipped_count"):
            if isinstance(row.get(key), int) and 0 <= row[key] < 1000000:
                public[key] = row[key]
    except Exception:
        pass
    return public


def safe_exception(error, evidence_root=None):
    frames = []
    for frame, line in traceback.walk_tb(error.__traceback__):
        basename = Path(frame.f_code.co_filename).name
        if basename in SAFE_SOURCES:
            name = frame.f_code.co_name
            frames.append({"source": basename, "line": line,
                           "function": name if name.isidentifier() and len(name) <= 100 else "anonymous"})
        else:
            frames.append({"source": "external"})
    name = type(error).__name__
    public = {"reason": "observer_exception_private_details_withheld",
              "exception_type": name if name.isidentifier() and len(name) <= 80 else "UnknownException",
              "source_frames": frames[-8:], "private_detail_retained": False,
              "diagnostic_codes": []}
    code = getattr(error, "code", None)
    if isinstance(code, str) and code in SAFE_PROBE_CODES:
        public["diagnostic_codes"] = [code]
    if evidence_root is not None:
        try:
            root = Path(evidence_root)
            root.mkdir(parents=True, exist_ok=True)
            raw = "".join(traceback.format_exception(error, limit=8)).encode("utf-8", errors="replace")
            if len(raw) > 65536:
                notice = b"\n[private exception detail truncated]\n"
                half = (65536 - len(notice)) // 2
                raw = raw[:half] + notice + raw[-half:]
            # Preserve the first observation, do not overwrite an earlier cause.
            with (root / "private-observer-error.txt").open("xb") as stream:
                stream.write(raw)
            public["private_detail_retained"] = True
        except Exception:
            public["private_detail_retained"] = False
    return public
