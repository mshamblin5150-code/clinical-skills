#!/usr/bin/env python3
"""Proof-only Windows screening of lazy suite-ID failure descriptions.

This observer never runs the full suite or full reader audit. It discovers the
complete tools population, qualifies the environment, requires behavior controls,
profiles one baseline module probe separately, then runs eight original module
probes serially in A-B-B-A order. Two samples per side per lookup do NOT meet the
P-Stack five-sample minimum. No adoption or end-to-end speedup conclusion follows.

Only synthetic test inputs and committed source belong on this disposable runner.
Raw failures stay bounded and private on that runner; public events are allowlisted.
"""

from __future__ import annotations

import argparse
import ast
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import tempfile
import time
import traceback


BASE = "38c431b15b7fafb0f5f89a67ecb501de318c47a1"
BRANCH = "refs/heads/diagnostic/2013-lazy-proof-20261020"
ORIGINAL_SUITE_HASH = "b3f804165e04ae0534c36882de699b7ae84e7ebb1df899539497ef1f6a97900c"
AUDIT_HASH = "386758808f5b6479ca3d2dad0bf35671e5a4db39651d5a0c2c83b064bd819d08"
PAYLOAD_HASH = "83ffec3f4a7700d6d382c3c773a2b08ad88b2b075b39b5b919941b7072abd9d9"
SUITE_PATH = "tools/test_suite_ids.py"
AUDIT_PATH = "tools/code_set_database_reader_check.py"
MARKER = "CODE_SET_DATABASE_OPEN_REFUSED"
LOOKUPS = ("icd10_lookup", "procedure_codes_lookup")
JUNCTION_QUALIFICATION = "test_aar_scan.ScanBasedSittingDiscovery.test_transcript_junctions_are_counted_without_being_entered"
ORDER = ("baseline", "candidate", "candidate", "baseline")
LOCK_VARIABLES = ("CLINICAL_SKILLS_LOCK_ROOT", "CLINICAL_SKILLS_TEST_LOCK_ROOT")
OBSERVER_PATHS = {
    SUITE_PATH,
    "diagnostics/measure_lazy_suite_ids.py",
    "diagnostics/suite_id_lazy_controls.py",
    ".github/workflows/ci-lazy-proof.yml",
}
EXPECTED_RED = {
    "__main__.LazyBindingControls.test_successful_ids_reload_and_assert_without_diagnostics",
    "__main__.LazyBindingControls.test_multiple_failures_continue_through_later_success_and_failure",
}
SAFE_ID = re.compile(r"__main__\.LazyBindingControls\.test_[a-z0-9_]+\Z")
RESULT_PREFIX = "LAZY_PROOF_RESULT:"
MAX_RAW_BYTES = 65536
MAX_RAW_REPORTS = 16
MAX_DIAGNOSTICS = 16
MAX_SAFE_FRAMES = 12
SAFE_EXCEPTION_TYPES = frozenset({
    "AssertionError", "AttributeError", "BrokenPipeError", "EOFError", "FileExistsError",
    "FileNotFoundError", "ImportError", "IndexError", "IsADirectoryError", "KeyError",
    "KeyboardInterrupt", "LookupError", "MemoryError", "ModuleNotFoundError",
    "NotADirectoryError", "NotImplementedError", "OSError", "OverflowError",
    "PermissionError", "RecursionError", "RuntimeError", "StopIteration", "SyntaxError",
    "SystemError", "SystemExit", "TimeoutError", "TypeError", "UnicodeDecodeError",
    "UnicodeEncodeError", "UnicodeError", "ValueError", "ZeroDivisionError",
    "JSONDecodeError", "CalledProcessError", "TimeoutExpired", "Refused",
    "InsideCheckout", "ForeignCheckout",
})
# Source: threshold_sheet.DEFAULT_PDF_ROOT / DEFAULT_RECS_ROOT and alias;
# guidelines_catalog.DEFAULT_TEXT_SRC; guidelines_index.default_database and
# repo_root.canonical_voice_model additionally depend on each checkout below.
FIXED_PRIVATE_ROOTS = (
    "C:/codeing/guidelines-src", "C:/codeing/guidelines-text",
    "C:/codeing/guidelines-index", "C:/codeing/guidelines-recs",
)


class Refused(RuntimeError):
    """A stable, non-private reason code; never contains a path or report."""


def require(condition, code):
    if not condition:
        raise Refused(code)


def bounded_raw(report):
    data = report.encode("utf-8", errors="replace")
    if len(data) <= MAX_RAW_BYTES:
        return data
    notice = b"\n[private report truncated]\n"
    budget = (MAX_RAW_BYTES - len(notice)) // 2
    return data[:budget] + notice + data[-budget:]


class SafeDiagnostics:
    """Only committed source labels/functions, fixed types, and literal reasons."""

    def __init__(self):
        self.sources = {Path(__file__).resolve(): "diagnostics/measure_lazy_suite_ids.py"}
        self.parsed = {}
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        self.reasons = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            index = 1 if node.func.id == "require" else 0 if node.func.id == "Refused" else None
            if index is not None and len(node.args) > index:
                value = node.args[index]
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    self.reasons.add(value.value)

    def add_checkout(self, repo):
        # The caller has already verified the immutable tree. No product module
        # is imported, and fixture/generated filenames are never registered.
        for path in (repo / "tools").glob("*.py"):
            self.sources[path.resolve()] = "tools/" + path.name
        controls = repo / "diagnostics/suite_id_lazy_controls.py"
        if controls.is_file():
            self.sources[controls.resolve()] = "diagnostics/suite_id_lazy_controls.py"

    def reason(self, value):
        return value if isinstance(value, str) and value in self.reasons else None

    def frame(self, filename, function, line):
        path = Path(filename).resolve()
        if path not in self.sources or not isinstance(line, int) or isinstance(line, bool):
            return None
        if path not in self.parsed:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            functions = {"<module>"} | {
                node.name for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            self.parsed[path] = functions, len(source.splitlines())
        functions, lines = self.parsed[path]
        if function not in functions or not 1 <= line <= lines:
            return None
        return {"source": self.sources[path], "function": function, "line": line}

    def exception(self, error):
        name = type(error).__name__
        result = {"exception_type": name if name in SAFE_EXCEPTION_TYPES else "unlisted_exception",
                  "frames": [], "omitted_frame_count": 0}
        reason = self.reason(error.args[0]) if isinstance(error, Refused) and error.args else None
        if reason is not None:
            result["refusal_reason"] = reason
        current = error.__traceback__
        while current is not None:
            frame = self.frame(current.tb_frame.f_code.co_filename,
                               current.tb_frame.f_code.co_name, current.tb_lineno)
            if frame is None:
                result["omitted_frame_count"] += 1
            else:
                result["frames"].append(frame)
            current = current.tb_next
        if len(result["frames"]) > MAX_SAFE_FRAMES:
            result["omitted_frame_count"] += len(result["frames"]) - MAX_SAFE_FRAMES
            result["frames"] = result["frames"][-MAX_SAFE_FRAMES:]
        return result

    def captured(self, result):
        # Parse only bounded retained text, never echo a traceback/source line,
        # exception message, absolute path, local variable, or unknown type name.
        report = bounded_raw(result.get("stdout", "") + result.get("stderr", "")).decode("utf-8", errors="replace")
        frames, types, reasons = [], [], []
        for line in report.splitlines():
            match = re.fullmatch(r'\s*File "([^"\r\n]+)", line (\d+), in ([^\r\n]+)', line)
            if match:
                frame = self.frame(match[1], match[3], int(match[2]))
                if frame is not None:
                    frames.append(frame)
            match = re.match(r"^(?:[A-Za-z_][A-Za-z_0-9]*\.)?([A-Za-z_][A-Za-z_0-9]*):", line)
            if match and match[1] in SAFE_EXCEPTION_TYPES:
                types.append(match[1])
            prefix = "observer child refused: "
            if line.startswith(prefix):
                reason = self.reason(line[len(prefix):])
                if reason is not None:
                    reasons.append(reason)
        return {"exception_types": list(dict.fromkeys(types))[-MAX_SAFE_FRAMES:],
                "frames": frames[-MAX_SAFE_FRAMES:],
                "refusal_reasons": list(dict.fromkeys(reasons))[-MAX_SAFE_FRAMES:],
                "diagnostic_source": "bounded captured text, not an independent result"}


def safe_error_code(error, diagnostics, fallback):
    if isinstance(error, Refused) and error.args:
        return diagnostics.reason(error.args[0]) or "unrecognized_refusal"
    return fallback


def normalized_bytes(path):
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=False,
    )
    require(result.returncode == 0, "git_verification_failed")
    return result.stdout


def original_payload(repo):
    source = normalized_bytes(repo / AUDIT_PATH)
    require(digest(source) == AUDIT_HASH, "audit_source_hash_mismatch")
    tree = ast.parse(source.decode("utf-8"))
    assignments = {
        node.targets[0].id: node.value for node in tree.body
        if isinstance(node, ast.Assign) and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
    }
    require(ast.literal_eval(assignments["REFUSAL_MARKER"]) == MARKER,
            "refusal_marker_changed")
    expression = assignments["_SUBPROCESS"]
    require(isinstance(expression, ast.JoinedStr), "payload_shape_changed")
    pieces = []
    for value in expression.values:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            pieces.append(value.value)
        else:
            require(
                isinstance(value, ast.FormattedValue)
                and isinstance(value.value, ast.Name)
                and value.value.id == "REFUSAL_MARKER"
                and value.conversion == -1 and value.format_spec is None,
                "payload_interpolation_changed",
            )
            pieces.append(MARKER)
    payload = "".join(pieces)
    require(digest(payload.encode("utf-8")) == PAYLOAD_HASH, "payload_hash_mismatch")
    return payload


class Evidence:
    def __init__(self):
        self.directory = None
        self.raw_count = 0
        self.sink_errors = []
        self.rows = []
        self.raw_reports = []
        self.diagnostics = SafeDiagnostics()
        self.failures = []
        self.temp_qualified = False

    def emit(self, event, **fields):
        row = {"event": event, **fields}
        self.rows.append(row)
        try:
            print(json.dumps(row, sort_keys=True, allow_nan=False), flush=True)
        except Exception:
            self.sink_errors.append("public_event_sink_failed")
            raise Refused("public_event_sink_failed") from None
        if self.directory is not None:
            try:
                with (self.directory / "sanitized-events.jsonl").open(
                    "a", encoding="utf-8", newline="\n"
                ) as stream:
                    stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            except Exception:
                self.sink_errors.append("private_event_sink_failed")
                raise Refused("private_event_sink_failed") from None

    def retain_raw(self, report):
        # A secondary sink failure must not replace the error that caused capture.
        if self.raw_count >= MAX_RAW_REPORTS:
            return
        self.raw_count += 1
        data = bounded_raw(report)
        self.raw_reports.append(data)
        # Before TEMP qualification, raw evidence remains bounded in memory.
        # It is never written into a fallback or unqualified location.
        if self.directory is None:
            return
        self._write_raw(self.raw_count, data)

    def _write_raw(self, number, data):
        try:
            (self.directory / ("raw-%02d.txt" % number)).write_bytes(data)
        except Exception:
            self.sink_errors.append("private_raw_sink_failed")

    def bind_directory(self, directory):
        require(self.temp_qualified, "private_directory_not_qualified")
        require(directory.is_dir(), "private_directory_unavailable")
        self.directory = directory
        for number, data in enumerate(self.raw_reports, start=1):
            self._write_raw(number, data)

    def failure(self, stage, error, result=None):
        """Retain primary evidence first; reporting is best-effort, never raising."""
        try:
            if result is not None:
                self.retain_raw(result.get("stdout", "") + result.get("stderr", ""))
            self.retain_raw("".join(traceback.format_exception(type(error), error, error.__traceback__)))
            details = {"stage": stage, "exception": self.diagnostics.exception(error)}
            if result is not None:
                details["captured_child"] = self.diagnostics.captured(result)
            if len(self.failures) < MAX_DIAGNOSTICS:
                self.failures.append(details)
                try:
                    self.emit("failure_diagnostic", **details)
                except BaseException:
                    # emit already records its sink error. Preserve the primary.
                    pass
        except BaseException:
            self.sink_errors.append("failure_diagnostic_collection_failed")


class WindowsCPU:
    """Read-only counters. Direct child excludes every descendant process."""

    def __init__(self):
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        pointer = ctypes.POINTER(wintypes.FILETIME)
        self.kernel.GetSystemTimes.argtypes = [pointer, pointer, pointer]
        self.kernel.GetSystemTimes.restype = wintypes.BOOL
        self.kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, pointer, pointer, pointer, pointer]
        self.kernel.GetProcessTimes.restype = wintypes.BOOL

    @staticmethod
    def seconds(value):
        return ((value.dwHighDateTime << 32) | value.dwLowDateTime) / 10000000

    def host(self):
        idle, kernel, user = (wintypes.FILETIME() for _ in range(3))
        if not self.kernel.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
            return None
        return tuple(self.seconds(value) for value in (idle, kernel, user))

    def direct_child(self, process):
        # CPython's Popen handle remains owned until Popen is disposed of.
        # No new handle, system permission, or descendant enumeration is requested.
        handle = getattr(process, "_handle", None)
        if handle is None:
            return None
        created, exited, kernel, user = (wintypes.FILETIME() for _ in range(4))
        if not self.kernel.GetProcessTimes(
            wintypes.HANDLE(int(handle)), ctypes.byref(created), ctypes.byref(exited),
            ctypes.byref(kernel), ctypes.byref(user),
        ):
            return None
        return self.seconds(kernel) + self.seconds(user)


def host_delta(before, after):
    if before is None or after is None:
        return {"host_busy_seconds": None, "host_counter_status": "unavailable"}
    idle, kernel, user = (end - start for start, end in zip(before, after))
    busy = kernel + user - idle
    if min(idle, kernel, user, busy) < 0:
        return {"host_busy_seconds": None, "host_counter_status": "invalid_delta"}
    return {
        "host_busy_seconds": busy,
        "host_capacity_seconds": kernel + user,
        "host_counter_status": "read",
    }


def capture(command, cwd, cpu, evidence=None, stage="subprocess"):
    stdout, stderr = "", ""
    try:
        before = cpu.host()
        started = time.perf_counter()
        # The environment, executable, cwd, UTF-8 decoding and separate process
        # match the audit. No timeout, retry, shell, tracing, or loader patch.
        with subprocess.Popen(
            command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace",
        ) as process:
            stdout, stderr = process.communicate()
            elapsed = time.perf_counter() - started
            direct_cpu = cpu.direct_child(process)
            status = process.returncode
        after = cpu.host()
        return {
            "returncode": status, "stdout": stdout, "stderr": stderr,
            "wall_seconds": elapsed, "direct_child_cpu_seconds": direct_cpu,
            "direct_child_cpu_status": "read" if direct_cpu is not None else "unavailable",
            **host_delta(before, after),
        }
    except BaseException as error:
        if evidence is not None:
            # communicate exceptions may expose partial output. Capture privately,
            # never interpolate it into the primary error or a public event.
            for name in ("output", "stderr"):
                value = getattr(error, name, None)
                if isinstance(value, bytes):
                    value = value.decode("utf-8", errors="replace")
                if isinstance(value, str):
                    if name == "output":
                        stdout += value
                    else:
                        stderr += value
            evidence.failure(stage, error, {"stdout": stdout, "stderr": stderr})
        raise


def public_timing(result):
    return {key: value for key, value in result.items() if key not in {"stdout", "stderr"}}


def parse_child(result):
    rows = [line[len(RESULT_PREFIX):] for line in result["stdout"].splitlines()
            if line.startswith(RESULT_PREFIX)]
    require(result["returncode"] == 0 and len(rows) == 1, "observer_child_failed")
    row = json.loads(rows[0])
    require(isinstance(row, dict), "observer_child_report_invalid")
    return row


def unchanged_environment(original):
    require(dict(os.environ) == original, "observer_environment_changed")
    require(not any(name in os.environ for name in LOCK_VARIABLES), "inherited_lock_override")
    require(not any(name.startswith("CLINICAL_") for name in os.environ), "external_clinical_override")
    require(not any(os.environ.get(name) for name in ("PYTHONPATH", "PYTHONHOME", "GIT_DIR", "GIT_WORK_TREE")),
            "external_source_override")


def isolated_checkout(repo):
    require((repo / ".git").is_dir() and not (repo / ".git").is_symlink(), "requires_independent_clone")
    common = Path(git(repo, "rev-parse", "--git-common-dir").strip())
    if not common.is_absolute():
        common = repo / common
    require(common.resolve() == (repo / ".git").resolve(), "shared_git_directory")
    require(not (repo / ".git/objects/info/alternates").exists(), "shared_git_objects")
    require(not any(os.path.lexists(repo / name) for name in ("scratch", "output")), "private_corpus_root_present")


def private_corpus_absent(repos):
    paths = {Path(value) for value in FIXED_PRIVATE_ROOTS}
    for repo in repos:
        paths.add(repo.parent / "guidelines-index")
        # Independent clones own their own canonical model and account stores.
        paths.add(repo / "scratch" / "voice-model.md")
        paths.add(repo / "scratch" / "uptodate")
    require(not any(os.path.lexists(path) for path in paths), "external_private_corpus_present")


def clean_base(repo):
    isolated_checkout(repo)
    require(git(repo, "rev-parse", "HEAD").strip() == BASE, "wrong_measured_base")
    require(not git(repo, "status", "--porcelain=v1", "--untracked-files=all"), "base_not_clean")
    require(digest(normalized_bytes(repo / SUITE_PATH)) == ORIGINAL_SUITE_HASH, "baseline_suite_hash_mismatch")
    original_payload(repo)


def integrity(baseline, candidate, candidate_hash):
    clean_base(baseline)
    isolated_checkout(candidate)
    require(git(candidate, "rev-parse", "HEAD").strip() == BASE, "candidate_head_changed")
    require(not git(candidate, "diff", "--cached", "--name-only"), "candidate_index_changed")
    changed = git(candidate, "diff", "--name-only", "HEAD").splitlines()
    require(changed == [SUITE_PATH], "candidate_scope_changed")
    require(not git(candidate, "ls-files", "--others", "--exclude-standard"), "candidate_untracked_source")
    require(digest(normalized_bytes(candidate / SUITE_PATH)) == candidate_hash, "candidate_hash_mismatch")
    original_payload(candidate)
    private_corpus_absent((baseline, candidate))


def observer_identity(observer):
    require(git(observer, "rev-parse", "HEAD").strip() == os.environ.get("GITHUB_SHA"), "observer_head_mismatch")
    require(not git(observer, "status", "--porcelain=v1", "--untracked-files=all"), "observer_not_clean")
    git(observer, "merge-base", "--is-ancestor", BASE, "HEAD")
    paths = set(git(observer, "diff", "--name-only", BASE, "HEAD").splitlines())
    require(paths == OBSERVER_PATHS, "observer_branch_scope_mismatch")


def run_controls(script, repo, variant, cpu, evidence, prior_ids=None):
    """The single controls integration seam; requires the reviewed six-case schema."""
    result = capture([sys.executable, str(script), "--repo", str(repo)], repo / "tools", cpu,
                     evidence, "controls_capture")
    try:
        row = json.loads(result["stdout"])
        require(isinstance(row, dict) and row.get("schema_version") == 1, "controls_schema_mismatch")
        require(row.get("tests_run") == 6 and row.get("error_count") == 0, "controls_work_incomplete")
        outcomes = row.get("control_outcomes")
        require(isinstance(outcomes, list) and len(outcomes) == 6, "controls_rows_incomplete")
        ids = [item["test_id"] for item in outcomes]
        require(len(set(ids)) == 6 and all(SAFE_ID.fullmatch(item) for item in ids), "controls_id_mismatch")
        require(EXPECTED_RED <= set(ids), "controls_expected_red_missing")
        require(prior_ids is None or set(ids) == prior_ids, "controls_population_changed")
        expected_failures = EXPECTED_RED if variant == "baseline" else set()
        for item in outcomes:
            require(item.get("outcome") == ("failure" if item["test_id"] in expected_failures else "pass"),
                    "controls_unexpected_outcome")
            require(item.get("expected_baseline_failure") is (item["test_id"] in EXPECTED_RED),
                    "controls_expected_failure_flag_changed")
        require(row.get("failure_count") == len(expected_failures), "controls_failure_count_mismatch")
        require(row.get("successful") is (variant == "candidate"), "controls_success_mismatch")
        require(result["returncode"] == (1 if variant == "baseline" else 0), "controls_exit_mismatch")
    except BaseException as error:
        evidence.failure("controls_result", error, result)
        raise
    # Expected baseline RED is evidence, not an unexpected benchmark error.
    if variant == "baseline":
        evidence.retain_raw(result["stdout"] + result["stderr"])
    evidence.emit("behavior_controls", variant=variant, tests_run=6,
                  expected_failure_count=len(expected_failures), error_count=0,
                  matched_expected_outcomes=True, timed_sample=False,
                  control_outcomes=[{"test_id": item["test_id"], "outcome": item["outcome"]}
                                    for item in outcomes])
    return set(ids)


def classify_probe(result, expected_count):
    report = result["stdout"] + result["stderr"]
    # Same precedence as _readers_under_refusal: marker first, then return code.
    classification = "reader" if MARKER in report else "error" if result["returncode"] else "nonreader"
    counts = re.findall(r"(?m)^Ran (\d+) tests? in [0-9.]+s\s*$", report)
    clean_footer = re.findall(r"(?m)^OK\s*$", report)
    count = int(counts[0]) if len(counts) == 1 else None
    completed = count == expected_count and len(clean_footer) == 1
    return {
        "classification": classification, "refusal_marker_present": MARKER in report,
        "module_tests_run": count, "module_tests_expected": expected_count,
        "completed_test_result": completed,
        "valid": classification == "nonreader" and result["returncode"] == 0 and completed,
    }


def finish_timed_probe(evidence, item, result, expected_count):
    try:
        verdict = classify_probe(result, expected_count)
        public = {**item, **public_timing(result), **verdict}
    except BaseException as error:
        evidence.failure("timed_result", error, result)
        raise
    if not verdict["valid"]:
        primary = Refused("unexpected_timed_probe_result")
        evidence.failure("timed_result", primary, result)
        try:
            evidence.emit("timed_probe_finished", **public)
        except BaseException:
            pass  # The evidence sink records its error; the probe remains primary.
        raise primary
    evidence.emit("timed_probe_finished", **public)
    return public


def child(action, repo):
    """Untimed observation children. The timed probes do not call this wrapper."""
    import unittest

    tools = repo / "tools"
    sys.path.insert(0, str(tools))
    if action == "validate-temp":
        import repo_root
        require(not any(name in os.environ for name in LOCK_VARIABLES), "child_inherited_lock_override")
        for name in ("TEMP", "TMP"):
            if os.environ.get(name):
                repo_root.ensure_outside_checkout(os.environ[name])
        repo_root.ensure_outside_checkout(tempfile.gettempdir())
        row = {"outside_checkout_temp": True, "temp_environment_unchanged": True}
    elif action == "discover":
        loader = unittest.TestLoader()
        def cases(member):
            if isinstance(member, unittest.TestSuite):
                for nested in member:
                    yield from cases(nested)
            else:
                yield member
        # Import output is captured by the parent, never forwarded into public logs.
        discovered = tuple(cases(loader.discover(start_dir=tools, top_level_dir=tools)))
        failed = sum(type(test).__name__ == "_FailedTest" and type(test).__module__ == "unittest.loader"
                     for test in discovered)
        require(not loader.errors and failed == 0 and discovered, "discovery_failed")
        ids = sorted(test.id() for test in discovered)
        require(len(set(ids)) == len(ids), "duplicate_discovered_ids")
        module_count = sum(test.id().startswith("test_suite_ids.") for test in discovered)
        require(module_count > 0, "measured_module_missing")
        row = {"test_count": len(ids), "sorted_ids_sha256": digest(json.dumps(
            ids, ensure_ascii=True, separators=(",", ":")).encode("utf-8")),
            "loader_error_count": 0, "module_test_count": module_count,
            "executed_test_count": 0, "ids_encoding": "sorted JSON array, ASCII escaped, compact"}
    elif action == "profile":
        import cProfile
        import pstats
        payload = original_payload(repo)
        sys.argv = ["-c", str(tools), "test_suite_ids", "icd10_lookup"]
        scope = {"__name__": "__main__"}
        profiler = cProfile.Profile()
        original_exit = None
        try:
            profiler.enable()
            exec(compile(payload, "<original-refusal-payload>", "exec"), scope)
        except SystemExit as error:
            original_exit = error.code
        finally:
            profiler.disable()
        stats = pstats.Stats(profiler).stats
        safe_stats = []
        for (filename, line, name), (primitive, calls, own, cumulative, _callers) in stats.items():
            # Exclude built-in repr names, paths, synthetic fixture contents, and callers.
            if not name.isidentifier():
                continue
            basename = Path(filename).name
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", basename):
                basename = "observer-generated"
            safe_stats.append({"basename": basename, "line": line, "function": name,
                               "primitive_calls": primitive, "total_calls": calls,
                               "self_seconds": own, "cumulative_seconds": cumulative})
        selected = sorted(safe_stats, key=lambda item: (-item["cumulative_seconds"], item["function"]))[:20]
        required_names = {"_describe_test_bindings", "discover", "loadTestsFromName"}
        required = [item for item in safe_stats if item["function"] in required_names]
        require({item["function"] for item in required} == required_names, "profile_targets_missing")
        for item in required:
            if item not in selected:
                selected.append(item)
        result = scope.get("result")
        row = {"stats": selected, "profiled_payload_sha256": digest(payload.encode("utf-8")),
               "profile_module_tests_run": getattr(result, "testsRun", None),
               "profile_result_successful": result is not None and result.wasSuccessful(),
               "original_exit": original_exit}
        print(RESULT_PREFIX + json.dumps(row, sort_keys=True))
        # Preserve the original payload's process exit semantics after observation.
        raise SystemExit(original_exit if original_exit is not None else 2)
    else:
        raise Refused("unknown_child_action")
    print(RESULT_PREFIX + json.dumps(row, sort_keys=True))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observer", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--candidate-sha256")
    parser.add_argument("--child", choices=("validate-temp", "discover", "profile"))
    parser.add_argument("--repo", type=Path)
    args = parser.parse_args(argv)
    if args.child:
        try:
            require(args.repo is not None, "missing_child_repo")
            child(args.child, args.repo.resolve())
        except Refused as error:
            reason = safe_error_code(error, SafeDiagnostics(), "unexpected_child_exception")
            print("observer child refused: " + reason, file=sys.stderr)
            return 2
        return 0

    evidence = Evidence()
    errors = []
    samples = []
    attempted = []
    qualification_done = []
    controls_done = []
    discoveries = {}
    profile_done = False
    source_prepared = False
    source_verified_at_finish = False
    original_environment = dict(os.environ)
    snapshots = {}
    plan = [{"ordinal": index * len(LOOKUPS) + lookup_index + 1,
             "variant": variant, "lookup": lookup}
            for index, variant in enumerate(ORDER)
            for lookup_index, lookup in enumerate(LOOKUPS)]
    try:
        require(os.name == "nt" and platform.system() == "Windows", "requires_windows")
        require(sys.version_info[:3] == (3, 14, 4), "requires_python_3_14_4")
        require(os.environ.get("GITHUB_ACTIONS") == "true", "requires_disposable_actions_runner")
        require(os.environ.get("GITHUB_EVENT_NAME") == "push"
                and os.environ.get("GITHUB_REF") == BRANCH
                and os.environ.get("GITHUB_RUN_ATTEMPT") == "1", "unapproved_event_or_rerun")
        require(all(value is not None for value in (args.observer, args.baseline, args.candidate)), "missing_checkout")
        require(isinstance(args.candidate_sha256, str)
                and re.fullmatch(r"[0-9a-f]{64}", args.candidate_sha256)
                and args.candidate_sha256 != ORIGINAL_SUITE_HASH, "reviewed_candidate_hash_required")
        observer, baseline, candidate = (value.resolve() for value in (args.observer, args.baseline, args.candidate))
        require(len({observer, baseline, candidate}) == 3, "checkouts_not_distinct")
        require(not any(left in right.parents for left in (observer, baseline, candidate)
                        for right in (observer, baseline, candidate) if left != right), "nested_checkouts")
        unchanged_environment(original_environment)
        observer_identity(observer)
        clean_base(baseline)
        clean_base(candidate)
        private_corpus_absent((baseline, candidate))
        for repo in (observer, baseline, candidate):
            evidence.diagnostics.add_checkout(repo)
        payload = original_payload(baseline)
        candidate_source = observer / SUITE_PATH
        require(digest(normalized_bytes(candidate_source)) == args.candidate_sha256, "observer_candidate_hash_mismatch")
        observer_files = [candidate_source, observer / "diagnostics/measure_lazy_suite_ids.py",
                          observer / "diagnostics/suite_id_lazy_controls.py"]
        snapshots = {path: path.read_bytes() for path in observer_files}
        # Baseline identity and independent review hash are established BEFORE copy.
        (candidate / SUITE_PATH).write_bytes(candidate_source.read_bytes())
        source_prepared = True
        integrity(baseline, candidate, args.candidate_sha256)
        cpu = WindowsCPU()
        evidence.emit("scope", base_sha=BASE, candidate_source_sha256=args.candidate_sha256,
                      audit_source_sha256=AUDIT_HASH, payload_sha256=PAYLOAD_HASH,
                      assessment="PRELIMINARY SCREENING ONLY", planned_timed_module_probes=len(plan),
                      timed_order=plan, full_suite_execution=False, full_audit_execution=False,
                      samples_per_side_per_lookup=2, pstack_required_samples_per_side=5,
                      profiler_in_timed_samples=False, original_payload_unmodified=True,
                      environment_inherited=True, private_corpus_access=False,
                      pstack_source_commit="e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a",
                      installed_pstack_archive_manifest_verified=False)
        evidence.emit("machine", platform="Windows", python=platform.python_version(),
                      logical_cores=os.cpu_count(), machine=platform.machine(),
                      host_cpu_scope="whole host including background work; NOT attribution",
                      child_cpu_scope="direct child only; NOT summed descendants",
                      cache_policy="fresh processes; bytecode and OS caches retained, not claimed cold or symmetric; baseline profile precedes samples")
        # Before expensive discovery/profile: the unchanged outside-checkout TEMP
        # validator, then exactly the previously accepted native-junction probe.
        result = capture([sys.executable, str(observer / "diagnostics/measure_lazy_suite_ids.py"),
                          "--child", "validate-temp", "--repo", str(baseline)], baseline / "tools", cpu,
                         evidence, "temp_capture")
        try:
            row = parse_child(result)
            require(row.get("outside_checkout_temp") is True, "temp_validation_incomplete")
        except BaseException as error:
            evidence.failure("temp_result", error, result)
            raise
        evidence.emit("temp_validation", **row)
        # Validation above established TEMP remains outside all checkouts. No
        # variable is redirected and no explicit/generated lock root is installed.
        evidence.temp_qualified = True
        evidence.bind_directory(Path(tempfile.mkdtemp(prefix="lazy-proof-private-")))
        result = capture([sys.executable, "-c", payload, str(baseline / "tools"),
                          JUNCTION_QUALIFICATION, "icd10_lookup"], baseline / "tools", cpu,
                         evidence, "junction_capture")
        try:
            qualification = classify_probe(result, 1)
            require(qualification["valid"], "junction_qualification_failed")
        except BaseException as error:
            evidence.failure("junction_result", error, result)
            raise
        qualification_done.append("baseline")
        evidence.emit("junction_qualification", variant="baseline", test_id=JUNCTION_QUALIFICATION,
                      lookup="icd10_lookup", timed_sample=False, **qualification)
        ids = None
        for variant, repo in (("baseline", baseline), ("candidate", candidate)):
            ids = run_controls(observer / "diagnostics/suite_id_lazy_controls.py", repo,
                               variant, cpu, evidence, ids)
            controls_done.append(variant)
        for variant, repo in (("baseline", baseline), ("candidate", candidate)):
            result = capture([sys.executable, str(observer / "diagnostics/measure_lazy_suite_ids.py"),
                              "--child", "discover", "--repo", str(repo)], repo / "tools", cpu,
                             evidence, "discovery_capture")
            try:
                row = parse_child(result)
                require(row.get("loader_error_count") == 0 and row.get("test_count", 0) > 0,
                        "discovery_report_incomplete")
            except BaseException as error:
                evidence.failure("discovery_result", error, result)
                raise
            discoveries[variant] = row
            evidence.emit("complete_population_discovery", variant=variant, **row)
        require(discoveries["baseline"] == discoveries["candidate"], "discovered_population_changed")
        module_count = discoveries["baseline"]["module_test_count"]
        before = cpu.host()
        ambient_started = time.perf_counter()
        time.sleep(1.0)
        evidence.emit("ambient_cpu", observed_wall_seconds=time.perf_counter() - ambient_started,
                      measurement="whole-host idle interval before profile", **host_delta(before, cpu.host()))
        evidence.emit("profile_started", variant="baseline", lookup="icd10_lookup", timed_sample=False)
        result = capture([sys.executable, str(observer / "diagnostics/measure_lazy_suite_ids.py"),
                          "--child", "profile", "--repo", str(baseline)], baseline / "tools", cpu,
                         evidence, "profile_capture")
        try:
            row = parse_child(result)
            verdict = classify_probe(result, module_count)
            require(verdict["valid"] and row.get("profile_module_tests_run") == module_count
                    and row.get("profile_result_successful") is True and row.get("original_exit") == 0,
                    "profile_probe_failed")
        except BaseException as error:
            evidence.failure("profile_result", error, result)
            raise
        profile_done = True
        evidence.emit("profile_complete", variant="baseline", lookup="icd10_lookup", timed_sample=False,
                      overhead="cProfile overhead included here only; not comparable to uninstrumented wall time",
                      cumulative_times_overlap=True, **row, **public_timing(result))
        for item in plan:
            unchanged_environment(original_environment)
            integrity(baseline, candidate, args.candidate_sha256)
            attempted.append(item["ordinal"])
            evidence.emit("timed_probe_started", **item)
            repo = baseline if item["variant"] == "baseline" else candidate
            result = capture([sys.executable, "-c", payload, str(repo / "tools"),
                              "test_suite_ids", item["lookup"]], repo / "tools", cpu,
                             evidence, "timed_capture")
            public = finish_timed_probe(evidence, item, result, module_count)
            samples.append(public)
        require(len(samples) == len(plan), "timed_work_incomplete")
    except BaseException as error:
        code = safe_error_code(error, evidence.diagnostics, "unexpected_observer_exception")
        errors.append(code)
        evidence.failure("observer", error)
    finally:
        # Finalization is guarded so neither a sink failure nor an integrity failure
        # can erase a primary failure. Every failure keeps the exit nonzero.
        if source_prepared:
            try:
                integrity(baseline, candidate, args.candidate_sha256)
                observer_identity(observer)
                require(all(path.read_bytes() == content for path, content in snapshots.items()),
                        "observer_source_changed")
                unchanged_environment(original_environment)
                source_verified_at_finish = True
            except BaseException as error:
                errors.append(safe_error_code(error, evidence.diagnostics, "final_integrity_exception"))
                evidence.failure("final_integrity", error)
        # No observer file is patched anywhere in this harness, so there is no
        # profile instrumentation to restore. Never overwrite unexpected changes.
        grouped = []
        for variant in ("baseline", "candidate"):
            for lookup in LOOKUPS:
                values = [item["wall_seconds"] for item in samples
                          if item["variant"] == variant and item["lookup"] == lookup]
                grouped.append({"variant": variant, "lookup": lookup, "valid_run_count": len(values),
                                "median_wall_seconds": statistics.median(values) if values else None,
                                "min_wall_seconds": min(values) if values else None,
                                "max_wall_seconds": max(values) if values else None})
        summary = {
            "assessment": "PRELIMINARY SCREENING ONLY",
            "conclusion": "inconclusive for adoption or end-to-end speedup",
            "planned_timed_module_probes": len(plan), "attempted_timed_module_probes": len(attempted),
            "completed_valid_timed_module_probes": len(samples),
            "unread_probes": [item for item in plan if item["ordinal"] not in {row["ordinal"] for row in samples}],
            "qualification_completed": qualification_done, "controls_completed": controls_done,
            "discovery_completed": sorted(discoveries), "separate_baseline_profile_completed": profile_done,
            "source_integrity_verified_at_finish": source_verified_at_finish,
            "unexpected_error_count": len(errors) + len(evidence.sink_errors),
            "error_codes": errors + evidence.sink_errors, "wall_time_groups": grouped,
            "failure_diagnostics": evidence.failures,
            "bounded_raw_reports_retained": evidence.raw_count,
            "raw_reports_memory_bytes": sum(map(len, evidence.raw_reports)),
            "qualified_private_directory_bound": evidence.directory is not None,
            "limitations": [
                "two samples per side per lookup, below the P-Stack minimum of five",
                "no full-suite or full-audit timing and no end-to-end share measured",
                "whole-host CPU includes background work; direct-child CPU excludes descendants",
                "fresh child processes retain bytecode and operating-system caches; no cold symmetry claimed",
                "profile timings include profiler overhead and cumulative times overlap",
                "P-Stack pinned upstream read; installed archive and manifest unavailable",
                "no parallel experiment, extrapolated perfect parallelism, or production adoption",
                "runner cancellation can prevent finalization; started probes without valid finish remain unread",
            ],
        }
        try:
            evidence.emit("summary", **summary)
        except BaseException:
            errors.append("summary_event_failed")
        # Only the sanitized final JSON may enter the Actions summary. No raw
        # reports, arbitrary exception strings, fixture text, or local paths.
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            try:
                with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as stream:
                    stream.write("\nPRELIMINARY SCREENING ONLY\n\n")
                    stream.write(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
            except BaseException:
                errors.append("actions_summary_sink_failed")
                try:
                    evidence.emit("finalization_error", code="actions_summary_sink_failed")
                except BaseException:
                    pass
    return 0 if not errors and not evidence.sink_errors and source_verified_at_finish and len(samples) == len(plan) else 1


if __name__ == "__main__":
    raise SystemExit(main())
