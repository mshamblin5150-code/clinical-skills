"""One diagnostic observation of an unchanged, immutable serial audit.

No optimization, concurrent probes, changed assertions, or production verdicts.
Only tracked source and its synthetic fixtures are used. Public output contains
timings, module/test identifiers, counts, hashes, and bounded error categories.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import time
import traceback


EXPECTED_SHA = "38c431b15b7fafb0f5f89a67ecb501de318c47a1"
EXPECTED_AUDIT_SHA256 = "386758808f5b6479ca3d2dad0bf35671e5a4db39651d5a0c2c83b064bd819d08"
EXPECTED_PAYLOAD_SHA256 = "83ffec3f4a7700d6d382c3c773a2b08ad88b2b075b39b5b919941b7072abd9d9"


def sha256_bytes(content):
    return hashlib.sha256(content).hexdigest()


def population_digest(value):
    return sha256_bytes(json.dumps(
        sorted(value), ensure_ascii=True, separators=(",", ":")
    ).encode("utf-8"))


def safe_failure(report):
    # Never print raw fixture text, command arguments, paths, or environment.
    test_ids = re.findall(r"^(?:FAIL|ERROR): ([A-Za-z0-9_.]+)", report, re.M)
    error_types = re.findall(r"^([A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception)):", report, re.M)
    categories = [
        name for token, name in (
            ("Access is denied", "access_denied"),
            ("Permission denied", "permission_denied"),
            ("InsideCheckout", "inside_checkout_refusal"),
            ("No module named", "module_missing"),
            ("No such file or directory", "file_missing"),
        ) if token in report
    ]
    return {
        "test_ids": sorted(set(test_ids))[:30],
        "error_types": sorted(set(error_types))[:20],
        "categories": categories,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo.resolve()
    tools = root / "tools"
    output = args.output.resolve()
    try:
        output.mkdir(mode=0o700, parents=True, exist_ok=False)
    except OSError as error:
        print(json.dumps({"kind": "output_setup_error", "error_type": type(error).__name__}))
        return 1
    events = output / "events.jsonl"
    phases = {}
    probes = []
    planned = None
    audit_started = None
    real_run = subprocess.run
    status = 1
    evidence_faults = []

    def emit(kind, **fields):
        row = {"kind": kind, **fields}
        text = json.dumps(row, ensure_ascii=True, sort_keys=True)
        try:
            with events.open("a", encoding="utf-8") as stream:
                stream.write(text + "\n")
        except OSError as error:
            evidence_faults.append("events:" + type(error).__name__)
        try:
            print(text, flush=True)
        except (OSError, UnicodeError) as error:
            evidence_faults.append("stdout:" + type(error).__name__)

    def private_write(path, text):
        try:
            path.write_text(text, encoding="utf-8")
        except (OSError, UnicodeError) as error:
            evidence_faults.append("private_evidence:" + type(error).__name__)

    def git(*arguments):
        return real_run(
            ["git", *arguments], cwd=root, check=True, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        ).stdout.strip()

    def phase(name, call):
        start = time.perf_counter()
        try:
            return call()
        finally:
            phases[name] = time.perf_counter() - start
            emit("phase", phase=name, seconds=phases[name])

    def retain_failure(label, stdout, stderr):
        # Raw details stay only in this disposable runner's private diagnostic
        # folder. They are never uploaded or placed in public logs/summary.
        for name, text in (("stdout", stdout), ("stderr", stderr)):
            private_write(output / f"{label}-{name}.txt", text[:65536])
        emit(
            "failure_detail", label=label,
            detail_truncated=len(stdout) > 65536 or len(stderr) > 65536,
            report_sha256=sha256_bytes((stdout + stderr).encode("utf-8")),
            **safe_failure(stdout + stderr),
        )

    try:
        if os.name != "nt" or sys.version_info[:3] != (3, 14, 4):
            raise RuntimeError("Wrong diagnostic platform or interpreter")
        if git("rev-parse", "HEAD") != EXPECTED_SHA:
            raise RuntimeError("Wrong measured source revision")
        if git("status", "--porcelain", "--untracked-files=no"):
            raise RuntimeError("Measured tracked source is modified")
        # Normalize only Git checkout line endings for source identity.
        source = (tools / "code_set_database_reader_check.py").read_bytes().replace(b"\r\n", b"\n")
        if sha256_bytes(source) != EXPECTED_AUDIT_SHA256:
            raise RuntimeError("Measured audit source differs")
        sys.path.insert(0, str(tools))
        import code_set_database_reader_check as check
        import repo_root
        if sha256_bytes(check._SUBPROCESS.encode("utf-8")) != EXPECTED_PAYLOAD_SHA256:
            raise RuntimeError("Refusal payload differs")
        if os.environ.get("CLINICAL_SKILLS_LOCK_ROOT") or os.environ.get("CLINICAL_SKILLS_TEST_LOCK_ROOT"):
            raise RuntimeError("Unexpected inherited lock-root override")
        repo_root.ensure_outside_checkout(Path(tempfile.gettempdir()))
        emit(
            "environment", revision=EXPECTED_SHA, python=sys.version,
            platform=platform.platform(), cpus=os.cpu_count(),
            lock_override_present=False, generated_lock_override_present=False,
            audit_source_sha256=EXPECTED_AUDIT_SHA256,
            subprocess_payload_sha256=EXPECTED_PAYLOAD_SHA256,
            observer_lf_sha256=sha256_bytes(Path(__file__).read_bytes().replace(b"\r\n", b"\n")),
            observer_checkout_sha256=sha256_bytes(Path(__file__).read_bytes()),
            mode="standalone_serial_repository_audit", planted_audit_included=False,
            full_suite=False,
        )
        # A single existing Windows junction control qualifies the environment.
        # This is separate from and never counted as the full audit population.
        qualified_name = (
            "test_aar_scan.ScanBasedSittingDiscovery."
            "test_transcript_junctions_are_counted_without_being_entered"
        )
        q_start = time.perf_counter()
        qualified = real_run(
            [sys.executable, "-c", check._SUBPROCESS, str(tools), qualified_name, "icd10_lookup"],
            cwd=tools, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False,
        )
        emit("qualification", seconds=time.perf_counter() - q_start,
             returncode=qualified.returncode, test_id=qualified_name)
        if qualified.returncode:
            retain_failure("qualification", qualified.stdout, qualified.stderr)
            raise RuntimeError("Environment qualification failed")

        def observed_run(command, **kwargs):
            started = time.perf_counter()
            try:
                result = real_run(command, **kwargs)
            except BaseException as error:
                emit("launch_error", module=command[-2], lookup=command[-1],
                     error_type=type(error).__name__, seconds=time.perf_counter() - started)
                raise
            elapsed = time.perf_counter() - started
            report = result.stdout + result.stderr
            marked = check.REFUSAL_MARKER in report
            row = {
                "index": len(probes) + 1, "module": command[-2], "lookup": command[-1],
                "seconds": elapsed, "returncode": result.returncode,
                "classification": "reader" if marked else "unexpected_failure" if result.returncode else "nonreader",
                "stdout_bytes": len(result.stdout.encode("utf-8")),
                "stderr_bytes": len(result.stderr.encode("utf-8")),
            }
            probes.append(row)
            if result.returncode and not marked:
                retain_failure(f"probe-{len(probes):03d}", result.stdout, result.stderr)
            emit("probe", **row)
            return result

        audit_started = time.perf_counter()
        # Original audit() phase expressions, original functions and order.
        # No recursion-level timing or memoization is introduced.
        trees = phase("ast_parse", lambda: check._trees(tools))
        local_modules = frozenset(trees)
        graph = phase("import_graph", lambda: {
            module: check._imports(tree, local_modules)
            for module, tree in trees.items()
        })
        test_modules = frozenset(module for module in trees if module.startswith("test"))
        reaching = phase("reachability", lambda: frozenset(
            module for module in test_modules if check._reaches_lookup(module, graph)
        ))
        pinned = phase("pins", lambda: frozenset(
            (module, lookup)
            for module in test_modules
            for lookup in check._pins(trees[module])
        ))
        planned = len(reaching) * len(check.LOOKUPS)
        emit("population", modules=len(trees), test_modules=len(test_modules),
             candidates=len(reaching), planned_pairs=planned,
             reaching_digest=population_digest(reaching), pinned_digest=population_digest(pinned))
        subprocess.run = observed_run
        readers = phase("refusal_probes", lambda: check._readers_under_refusal(tools, reaching))
        result = check.Audit(
            reaching=reaching, readers=readers, pinned=pinned,
            unpinned_readers=readers - pinned, stale_pins=pinned - readers,
        )
        sets = {
            name: {"count": len(getattr(result, name)),
                   "sha256": population_digest(getattr(result, name)),
                   "members": sorted(getattr(result, name))}
            for name in ("reaching", "readers", "pinned", "unpinned_readers", "stale_pins")
        }
        status = 0 if not result.unpinned_readers and not result.stale_pins else 1
        emit("audit_result", status=status, sets=sets, completed_pairs=len(probes),
             unread_pairs=planned - len(probes))
    except BaseException as error:
        emit("diagnostic_error", error_type=type(error).__name__, completed_pairs=len(probes),
             **safe_failure(str(error)))
        private_write(output / "exception.txt", traceback.format_exc()[:131072])
        status = 1
    finally:
        subprocess.run = real_run
        clean = None
        try:
            clean = git("status", "--porcelain", "--untracked-files=no") == ""
        except Exception as error:
            evidence_faults.append("final_git_status:" + type(error).__name__)
        if clean is not True:
            status = 1
        summary = {
            "audit_elapsed_seconds": None if audit_started is None else time.perf_counter() - audit_started,
            "phase_seconds": phases, "completed_pairs": len(probes),
            "planned_pairs": planned, "unread_pairs": None if planned is None else planned - len(probes),
            "probe_seconds_sum": sum(p["seconds"] for p in probes),
            "slowest_probes": sorted(probes, key=lambda p: p["seconds"], reverse=True)[:15],
            "observed_tracked_tree_clean": clean,
        }
        emit("summary", **summary)
        private_write(output / "summary.json", json.dumps(summary, indent=2, sort_keys=True) + "\n")
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            try:
                with Path(summary_path).open("a", encoding="utf-8") as stream:
                    stream.write("### Standalone serial audit diagnostic\n\n")
                    stream.write("Not a full suite or a parallelism benchmark. A nonzero unread population is incomplete.\n\n")
                    stream.write("```json\n" + json.dumps(summary, indent=2, sort_keys=True) + "\n```\n")
            except (OSError, UnicodeError) as error:
                evidence_faults.append("step_summary:" + type(error).__name__)
        if evidence_faults:
            status = 1
        emit("diagnostic_exit", status=status, evidence_faults=sorted(set(evidence_faults)))
    return 1 if evidence_faults else status


if __name__ == "__main__":
    raise SystemExit(main())
