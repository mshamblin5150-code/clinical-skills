"""Exactly eleven synthetic controls; run only on the admitted hosted Windows job."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import sys
import threading
import unittest

from windows_serial_envelope import Plan, run_owned


ORDER = (
    "test_n1_lineage", "test_n2_nested_job", "test_n3_deadline",
    "test_n4_surviving_descendant", "test_n5_breakaway_refusal",
    "test_n6_output_limit", "test_n7_evidence_setup_failure",
    "test_n8_supervisor_loss", "test_p1_reported_fault",
    "test_p2_exit_discrepancy", "test_p3_missing_terminal",
)
CONFIG = None


def ticks() -> int:
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetTickCount64.restype = ctypes.c_uint64
    return int(kernel.GetTickCount64())


def retain_json(path, value, end_ms):
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(raw) > 32_768:
        raise RuntimeError("receipt size cap; inconclusive")
    if ticks() >= end_ms:
        raise RuntimeError("receipt time exhausted; inconclusive")
    completed, errors = threading.Event(), []
    def retain():
        try:
            path.write_bytes(raw)
            if path.read_bytes() != raw:
                raise OSError("receipt readback differs")
        except BaseException as error:
            errors.append(type(error).__name__)
        finally:
            completed.set()
    threading.Thread(target=retain, daemon=True).start()
    if not completed.wait(max(0, min(10_000, end_ms - ticks())) / 1000) or errors:
        raise RuntimeError("receipt retention unproven; inconclusive")
    return raw


class NativeQualification(unittest.TestCase):
    def exercise(self, recipe, *, invalid_parent=False):
        cfg = CONFIG
        started = ticks()
        protocol = self._testMethodName.startswith("test_p")
        allowance = 10_000 if protocol else 35_000
        case_end = min(started + allowance, cfg.controls_end)
        self.assertEqual(allowance, case_end - started, "full case window unavailable; no launch")
        destination = cfg.root / self._testMethodName
        if invalid_parent:
            destination.write_bytes(b"synthetic non-directory")
            destination = destination / "child"
        receipt = run_owned(Plan(
            recipe=recipe, destination=destination, sources=cfg.sources,
            job_start_ms=cfg.start, case_end_ms=case_end,
            nonce=cfg.nonce + "-" + self._testMethodName,
        ))
        cfg.receipts.append({"case": self._testMethodName, "receipt": receipt,
                             "expected_execution_success": not invalid_parent and recipe in {
                                 "ordinary", "nested", "breakaway"}})
        retain_json(cfg.root / (self._testMethodName + ".json"),
                    cfg.receipts[-1], case_end)
        permitted_faults = {
            "ordinary": {"evidence_setup"} if invalid_parent else set(),
            "nested": set(), "breakaway": set(),
            "deadline": {"deadline", "process_exit", "missing_terminal"},
            "survivor": {"surviving_descendant"},
            "output": {"output_limit", "process_exit", "missing_terminal"},
            "supervisor_loss": {"process_exit", "missing_terminal"},
            "protocol_fault": {"reported_evidence_fault", "process_exit", "terminal_status"},
            "protocol_exit": {"process_exit"}, "protocol_missing": {"missing_terminal"},
        }
        self.assertLessEqual(set(receipt["faults"]), permitted_faults[recipe],
                             "unexpected failure cannot count as an expected negative")
        self.assertFalse(receipt["cleanup_unproven"], "owned cleanup was not proven")
        self.assertEqual(0, receipt["active_processes"])
        self.assertLessEqual(receipt["peak_owned_processes"], 4)
        if receipt["launched"]:
            self.assertTrue(receipt["capture_retention_verified"], "pipe prefix custody unproven")
        self.assertLessEqual(receipt["retained_stdout_bytes"], 65_536)
        self.assertLessEqual(receipt["retained_stderr_bytes"], 65_536)
        return receipt

    def test_n1_lineage(self):
        r = self.exercise("ordinary")
        self.assertTrue(r["success"])
        self.assertTrue(r["membership_before_resume"])
        self.assertTrue(r["lineage_verified"])
        self.assertEqual(3, len(r["lineage_pids"]))
        self.assertEqual(0, r["process_exit"])
        self.assertFalse(r["forced_termination"])

    def test_n2_nested_job(self):
        r = self.exercise("nested")
        self.assertTrue(r["success"])
        inner = r["fixture_terminal"]["inner"]
        self.assertTrue(inner["success"])
        self.assertTrue(inner["hosted_parent_job"])
        self.assertTrue(inner["membership_before_resume"])
        self.assertTrue(inner["lineage_verified"])

    def test_n3_deadline(self):
        r = self.exercise("deadline")
        self.assertFalse(r["success"])
        self.assertIn("deadline", r["faults"])
        self.assertTrue(r["lineage_verified"])
        self.assertEqual(3, len(r["lineage_pids"]))
        self.assertGreaterEqual(r["finished_ms"] - r["started_ms"], 5000)
        self.assertTrue(r["forced_termination"])

    def test_n4_surviving_descendant(self):
        r = self.exercise("survivor")
        self.assertFalse(r["success"])
        self.assertEqual(0, r["process_exit"])
        self.assertIn("surviving_descendant", r["faults"])
        observation = r["root_exit_observation"]
        self.assertFalse(observation["state_unproven"])
        self.assertEqual(1, len(set(observation["live_pids"] + observation["outlived_root_pids"])))
        self.assertLessEqual(observation["observed_ms"], r["empty_observed_ms"])
        self.assertFalse(r["forced_termination"], "N4 must expose disappearance during settling")

    def test_n5_breakaway_refusal(self):
        r = self.exercise("breakaway")
        self.assertTrue(r["success"])
        event = r["fixture_terminal"]
        self.assertTrue(event["ordinary_launch_succeeded"])
        self.assertTrue(r["ordinary_probe_membership_verified"])
        self.assertFalse(event["breakaway_created"])
        self.assertTrue(event["breakaway_rejected"])
        self.assertEqual(5, event["native_error"])

    def test_n6_output_limit(self):
        r = self.exercise("output")
        self.assertFalse(r["success"])
        self.assertIn("output_limit", r["faults"])
        self.assertTrue(r["stdout_truncated"] or r["stderr_truncated"])
        self.assertTrue(r["forced_termination"])

    def test_n7_evidence_setup_failure(self):
        r = self.exercise("ordinary", invalid_parent=True)
        self.assertFalse(r["success"])
        self.assertIn("evidence_setup", r["faults"])
        self.assertFalse(r["launched"])

    def test_n8_supervisor_loss(self):
        r = self.exercise("supervisor_loss")
        self.assertFalse(r["success"])
        self.assertEqual(73, r["process_exit"])
        self.assertTrue(r["lineage_verified"])
        self.assertEqual(4, len(r["lineage_pids"]))
        self.assertLess(r["empty_observed_ms"], r["last_close_before_ms"])
        self.assertFalse(r["forced_termination"], "outer rescue is not inner last-close proof")

    def test_p1_reported_fault(self):
        r = self.exercise("protocol_fault")
        self.assertFalse(r["success"])
        self.assertEqual(7, r["process_exit"])
        self.assertIn("reported_evidence_fault", r["faults"])

    def test_p2_exit_discrepancy(self):
        r = self.exercise("protocol_exit")
        self.assertFalse(r["success"])
        self.assertEqual(7, r["process_exit"])
        self.assertEqual(0, r["fixture_terminal"]["status"])
        self.assertIn("process_exit", r["faults"])

    def test_p3_missing_terminal(self):
        r = self.exercise("protocol_missing")
        self.assertFalse(r["success"])
        self.assertEqual(0, r["process_exit"])
        self.assertIn("missing_terminal", r["faults"])


class BoundedText(io.StringIO):
    def write(self, text):
        if self.tell() + len(text) > 32_768:
            raise RuntimeError("qualification text cap")
        return super().write(text)


def main() -> int:
    global CONFIG
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-start-ms", type=int, required=True)
    parser.add_argument("--module-sha", required=True)
    parser.add_argument("--fixture-sha", required=True)
    parser.add_argument("--tests-sha", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    if (os.name != "nt" or sys.version_info[:3] != (3, 14, 4) or args.attempt != "1"
            or ctypes.sizeof(ctypes.c_void_p) != 8 or os.cpu_count() != 4
            or sys.getwindowsversion().build < 26100
            or sys.getwindowsversion().product_type != 3
            or not os.environ.get("ImageVersion") or not os.environ.get("ImageOS")):
        raise SystemExit("qualification host/runtime/attempt refused")
    now = ticks()
    if not 0 <= now - args.job_start_ms < 180_000:
        raise SystemExit("setup window or job clock refused; no controls")
    if not args.run_id.isdecimal() or not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        raise SystemExit("qualification identity refused")
    root = Path(__file__).resolve().parent.parent / "scratch" / "sessions" / (
        "2013-qualification-" + args.run_id + "-" + args.attempt)
    root.mkdir(parents=True, exist_ok=False)
    sources = {
        "windows_serial_envelope.py": args.module_sha,
        "serial_envelope_fixture.py": args.fixture_sha,
        "test_windows_serial_envelope.py": args.tests_sha,
    }
    source_bytes = 0
    for name, expected in sources.items():
        with Path(__file__).with_name(name).open("rb") as source:
            data = source.read(262_145)
        if len(data) > 262_144 or hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit("reviewed qualification source identity refused")
        source_bytes += len(data)
    workflow = Path(__file__).parent.parent / ".github" / "workflows" / "ci-serial-envelope-qualification.yml"
    with workflow.open("rb") as source:
        workflow_bytes = source.read(16_385)
    if len(workflow_bytes) > 16_384:
        raise SystemExit("reviewed workflow size refused")
    workflow_sha = hashlib.sha256(workflow_bytes).hexdigest()
    source_bytes += len(workflow_bytes)
    if source_bytes > 262_144:
        raise SystemExit("fixture and manifest source budget refused")
    class Configuration:
        pass
    CONFIG = Configuration()
    CONFIG.root, CONFIG.sources, CONFIG.start = root, sources, args.job_start_ms
    CONFIG.controls_end = min(ticks() + 360_000, args.job_start_ms + 540_000)
    CONFIG.nonce, CONFIG.receipts = args.run_id + "-" + args.commit[:12], []
    output = BoundedText()
    result = unittest.TextTestRunner(stream=output, verbosity=2, failfast=True).run(
        unittest.TestSuite(NativeQualification(name) for name in ORDER))
    failed = {case.id().rsplit(".", 1)[-1] for case, _ in result.failures + result.errors}
    retained = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    summary = {
        "kind": "qualification_terminal", "commit": args.commit, "run_id": args.run_id,
        "attempt": 1, "sources": sources, "tests_run": result.testsRun,
        "workflow_sha256": workflow_sha,
        "provenance": {"observer_base": "064f5efc7e23bcb967b3f0681530c7b7f8d8477c",
                       "observer_blob": "076ab5032b18abe229c37b5e407f1077dcac4305",
                       "measurement_source_not_executed": "9e714a255c058fbb3b15f7eb5fd1de76b1ca02f2"},
        "failures": len(result.failures), "errors": len(result.errors),
        "not_run": list(ORDER[result.testsRun:]), "cases": CONFIG.receipts,
        "assertions": {name: ("NOT_RUN" if index >= result.testsRun else
                               "FAILED" if name in failed else "PASSED")
                       for index, name in enumerate(ORDER)},
        "retained_bytes_before_terminal": retained, "measurement_admitted": False,
        "source_bytes": source_bytes, "public_receipt_and_clock_reserve_bytes": 98_304,
        "host": {"os": platform.platform(), "python": platform.python_version(),
                 "cpus": os.cpu_count(), "image_os": os.environ.get("ImageOS"),
                 "image_version": os.environ.get("ImageVersion")},
        "job_start_ms": args.job_start_ms, "finished_ms": ticks(),
        "control_assertions": "expected negative receipts are not execution successes",
        "assertion_log": output.getvalue(),
        "unqualified": ["midrun_sink_failure", "blocked_logger_storage", "queue_full_delivery",
                        "forced_win32_errors", "broker_routes", "future_host_image"],
    }
    success = (result.wasSuccessful() and result.testsRun == 11
               and retained + source_bytes <= 4 * 1024 * 1024 - 98_304)
    summary["success"] = success
    if ticks() >= args.job_start_ms + 660_000:
        raise SystemExit("terminal receipt bound exhausted; inconclusive")
    raw = retain_json(root / "qualification-terminal.json", summary,
                      args.job_start_ms + 660_000)
    # Public output is synthetic receipt JSON only; raw pipe prefixes stay private.
    print(raw.decode(), end="", flush=True)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
