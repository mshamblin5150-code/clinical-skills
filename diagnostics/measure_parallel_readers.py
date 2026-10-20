#!/usr/bin/env python3
"""Unpublished proof-only ABBA screening: serial versus cap two, same lazy code.

This evaluates TWO independent full clones, not concurrent production use of one
checkout. It does not provide filesystem isolation or an adoption recommendation.
Two samples per side do not meet the P-Stack five-sample benchmark minimum.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import sys
import tempfile
import time

from parallel_reader_capture import analyze_capture, QUALIFIED_ANCHOR_SHA256
from parallel_reader_diagnostics import safe_exception, child_failure_diagnostic
from parallel_reader_scheduler import LOOKUPS, MARKER, Observation, account_pairs, audit_sets, run_schedule
from windows_job_probe import WindowsJobProbe


BASE = "38c431b15b7fafb0f5f89a67ecb501de318c47a1"
CANDIDATE_HASH = "f2f97e56313d7f8957bec0bd20fd91c9efd8c48c44871c5c69056eb830d43275"
AUDIT_HASH = "386758808f5b6479ca3d2dad0bf35671e5a4db39651d5a0c2c83b064bd819d08"
PAYLOAD_HASH = "83ffec3f4a7700d6d382c3c773a2b08ad88b2b075b39b5b919941b7072abd9d9"
SUITE_PATH = "tools/test_suite_ids.py"
AUDIT_PATH = "tools/code_set_database_reader_check.py"
ORDER = (1, 2, 2, 1)
BRANCH = "refs/heads/diagnostic/2013-parallel-proof-20261020"
LOCK_VARIABLES = ("CLINICAL_SKILLS_LOCK_ROOT", "CLINICAL_SKILLS_TEST_LOCK_ROOT")
EXTERNAL_CORPUS_NAMES = ("guidelines-src", "guidelines-text", "guidelines-index", "guidelines-recs",
                         "guidelines-builds", "kdigo-src", "kdigo-text", "society", "society-text")
KNOWN_FIXED_CORPORA = (
    "C:/codeing/clinical_skills/scratch", "C:/codeing/clinical_skills/output",
    "C:/codeing/clinical-skills/scratch", "C:/codeing/clinical-skills/output",
) + tuple("C:/codeing/" + name for name in EXTERNAL_CORPUS_NAMES)
OBSERVER_REQUIRED = {
    SUITE_PATH,
    "diagnostics/parallel_reader_scheduler.py", "diagnostics/parallel_reader_capture.py",
    "diagnostics/parallel_reader_diagnostics.py",
    "diagnostics/test_parallel_reader_controls.py", "diagnostics/test_parallel_observer_controls.py",
    "diagnostics/measure_parallel_readers.py", "diagnostics/windows_job_probe.py",
    "diagnostics/windows_job_probe_controls.py", "diagnostics/parallel-proof-budget.json",
    ".github/workflows/ci-parallel-proof.yml",
}
OBSERVER_ALLOWED = OBSERVER_REQUIRED | {
    "diagnostics/windows_job_probe_sources.md", "diagnostics/measure_lazy_suite_ids.py",
    "diagnostics/suite_id_lazy_controls.py", ".github/workflows/ci-lazy-proof.yml",
}
OWNER_CONTROL_IDS = [
    "normal_tree_cpu_and_active_zero", "separate_large_output",
    "cancel_tree_and_retained_evidence", "failed_root_keeps_descendants_owned",
    "cleanup_unread_retains_files_and_can_recover", "real_invalid_assignment_refused",
    "membership_refusal_terminates_suspended_root", "coordinator-death-running",
    "coordinator-death-suspended",
]


class Hold(RuntimeError):
    """A stable reason code only, never private report text."""

    def __init__(self, code, *, diagnostics=None):
        super().__init__(code)
        self.diagnostics = diagnostics


def require(condition, code):
    if not condition:
        raise Hold(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalized(path):
    return Path(path).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def emit(event, **values):
    # Every caller passes counts, reviewed source names, digests, or fixed codes.
    print(json.dumps({"event": event, **values}, sort_keys=True, allow_nan=False), flush=True)


def outside(path, roots):
    resolved = Path(path).resolve()
    return all(not resolved.is_relative_to(Path(root).resolve()) for root in roots)


def environment_preflight():
    require(sys.flags.optimize == 0, "optimized_python_invalidates_controls")
    require(not any(name in os.environ for name in LOCK_VARIABLES), "inherited_lock_override")
    require(not any(name.startswith("CLINICAL_") for name in os.environ), "clinical_environment_override")
    require(not any(os.environ.get(name) for name in ("PYTHONPATH", "PYTHONHOME", "GIT_DIR", "GIT_WORK_TREE")),
            "source_environment_override")
    require(not any(os.path.lexists(path) for path in KNOWN_FIXED_CORPORA), "known_fixed_corpus_present")


def corpus_preflight(roots, *, admission=True):
    candidates = {Path(path) for path in KNOWN_FIXED_CORPORA}
    for root in roots:
        if admission:
            candidates.update(root / name for name in ("scratch", "output"))
        candidates.update(root.parent / name for name in EXTERNAL_CORPUS_NAMES)
        candidates.update(root / name for name in EXTERNAL_CORPUS_NAMES)
    require(not any(os.path.lexists(path) for path in candidates), "known_or_default_corpus_present")


def exception_diagnostics(error, evidence_root):
    return safe_exception(error, evidence_root)


def load_audit(seed):
    require(sha(normalized(seed / AUDIT_PATH)) == AUDIT_HASH, "audit_hash_mismatch")
    sys.path.insert(0, str(seed / "tools"))
    try:
        spec = importlib.util.spec_from_file_location("original_reader_audit", seed / AUDIT_PATH)
        audit = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = audit
        spec.loader.exec_module(audit)
    finally:
        sys.path.pop(0)
    require(sha(audit._SUBPROCESS.encode("utf-8")) == PAYLOAD_HASH, "payload_hash_mismatch")
    require(tuple(sorted(audit.LOOKUPS)) == LOOKUPS and audit.REFUSAL_MARKER == MARKER,
            "audit_contract_changed")
    return audit


def static_population(audit, repo):
    trees = audit._trees(repo / "tools")
    modules = frozenset(trees)
    graph = {name: audit._imports(tree, modules) for name, tree in trees.items()}
    tests = frozenset(name for name in modules if name.startswith("test"))
    reaching = tuple(sorted(name for name in tests if audit._reaches_lookup(name, graph)))
    pins = frozenset((name, lookup) for name in tests for lookup in audit._pins(trees[name]))
    return {"module_count": len(modules), "test_module_count": len(tests),
            "reaching": list(reaching), "pinned": sorted(pins),
            "import_walk_declared_limit": audit.DECLARED_LIMITS["import walk"]}


def work_signature(observations):
    require(all(isinstance(row.metadata.get(key), int) and row.metadata[key] >= 0
                for row in observations for key in ("skipped", "expected_failures")),
            "probe_outcome_counts_unread")
    return [(row.module, row.lookup, row.classification, row.test_count, row.failures, row.errors,
             row.metadata["skipped"], row.metadata["expected_failures"])
            for row in observations]


def inventory(root, *, exclude_git=True, deadline=math.inf):
    """Hash retained files; cannot observe ephemeral or unknown absolute writes."""
    result = {}

    def check_deadline():
        require(time.monotonic() < deadline, "measurement_budget_expired")

    def visit(directory):
        check_deadline()
        paths = sorted(directory.iterdir())
        check_deadline()
        for path in paths:
            check_deadline()
            relative = path.relative_to(root).as_posix()
            if exclude_git and relative == ".git":
                continue
            stat = path.lstat()
            require(not path.is_symlink() and not (getattr(stat, "st_file_attributes", 0) & 0x400),
                    "unexpected_symlink_or_reparse_path")
            if path.is_dir():
                check_deadline()
                visit(path)
                check_deadline()
            elif path.is_file():
                require(stat.st_nlink == 1, "hardlinked_file")
                check_deadline()
                data = path.read_bytes()
                check_deadline()
                result[relative] = sha(data)
                check_deadline()
            else:
                raise Hold("unexpected_special_file")
    visit(root)
    check_deadline()
    return result


class OwnedCommands:
    """All child launch paths, including git/setup, use the Windows owner."""
    def __init__(self, root):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=False)
        git_path = shutil.which("git")
        require(git_path is not None, "preinstalled_git_unavailable")
        self.git_executable = Path(git_path).resolve()
        require(self.git_executable.is_absolute() and self.git_executable.is_file()
                and (os.name != "nt" or self.git_executable.suffix.lower() == ".exe"),
                "preinstalled_git_executable_invalid")
        self.counter = 0
        self.owners = []
        self.tree_cpu_seconds = 0.0
        self.cpu_unread_commands = 0

    def run(self, argv, cwd, deadline, *, env=None):
        if argv[0] == "git":
            argv = [str(self.git_executable), *argv[1:]]
        self.counter += 1
        path = self.root / ("command-%04d" % self.counter)
        try:
            owner = WindowsJobProbe.start(argv, cwd=str(cwd), env=dict(os.environ) if env is None else env,
                                          report_dir=str(path))
        except Exception as error:
            partial = getattr(error, "owner", None)
            if partial is not None:
                self.owners.append(partial)
                partial.cancel("command_start_exception", timeout=5)
            raise
        self.owners.append(owner)
        while time.monotonic() < deadline:
            snap = owner.poll()
            if snap.root_reaped and snap.active_processes == 0:
                result = owner.finish(timeout=5)
                require(result.snapshot.cleanup_verified, "command_cleanup_unverified")
                cpu = getattr(result.snapshot, "tree_cpu_seconds", None)
                if cpu is None:
                    self.cpu_unread_commands += 1
                else:
                    self.tree_cpu_seconds += cpu
                if result.snapshot.root_exit_code != 0 or result.reason != "completed":
                    raise Hold("owned_command_failed", diagnostics=child_failure_diagnostic(result))
                require(Path(result.stdout_path).stat().st_size < 2000000, "command_output_exceeds_contract")
                output = Path(result.stdout_path).read_bytes()
                return output
            time.sleep(0.01)
        result = owner.cancel("whole_job_budget_exhausted", timeout=5)
        require(result.snapshot.cleanup_verified, "command_cleanup_unverified")
        raise Hold("whole_job_budget_exhausted")

    def git(self, repo, *args, deadline):
        return self.run(["git", "-C", str(repo), *args], repo, deadline).decode("utf-8", errors="strict")

    def cleanup(self):
        clean = True
        for owner in self.owners:
            try:
                result = owner.result or owner.cancel("coordinator_cleanup", timeout=5)
                clean = clean and result.snapshot.cleanup_verified
            except Exception:
                clean = False
        return clean


class LiveRunner:
    def __init__(self, clones, payload, root, *, owner_factory=WindowsJobProbe, minimum_free_bytes=0,
                 deadline=math.inf):
        self.clones = clones
        self.payload = payload
        self.root = root
        self.owner_factory = owner_factory
        self.minimum_free_bytes = minimum_free_bytes
        self.deadline = deadline
        self.active = {}
        self.owners = []
        self.counter = 0
        self.private_roots = []

    def diagnose_exception(self, error):
        return exception_diagnostics(error, self.root)

    def start(self, index, lane, module, lookup):
        require(lane not in (handle["lane"] for handle in self.active.values()), "clone_already_active")
        self.counter += 1
        probe_root = self.root / ("probe-%04d" % self.counter)
        probe_root.mkdir(parents=True, exist_ok=False)
        temporary = probe_root / "temporary"
        temporary.mkdir()
        require(outside(temporary, self.clones), "temporary_inside_checkout")
        env = dict(os.environ)
        require(not any(name in env for name in LOCK_VARIABLES), "inherited_lock_override")
        env["TEMP"] = env["TMP"] = str(temporary.resolve())
        tools = self.clones[lane] / "tools"
        try:
            owner = self.owner_factory.start(
                [sys.executable, "-c", self.payload, str(tools), module, lookup],
                cwd=str(tools), env=env, report_dir=str(probe_root / "capture"))
        except Exception as error:
            partial = getattr(error, "owner", None)
            if partial is not None:
                self.owners.append(partial)
                partial.cancel("start_exception", timeout=5)
            raise
        self.owners.append(owner)
        handle = {"owner": owner, "lane": lane, "module": module, "lookup": lookup,
                  "root": probe_root, "temporary": temporary}
        self.active[id(handle)] = handle
        self.private_roots.append(probe_root)
        return handle

    def observation(self, handle, result, *, canceled=False):
        snap = result.snapshot
        self.active.pop(id(handle), None)
        clean = snap.cleanup_verified and snap.active_processes == 0 and snap.root_reaped
        if canceled or not clean or result.reason != "completed":
            return Observation(handle["module"], handle["lookup"], "unread", unexpected=True,
                               cleanup_verified=clean, reason=result.reason,
                               wall_seconds=snap.wall_seconds, tree_cpu_seconds=snap.tree_cpu_seconds)
        parsed = analyze_capture(result.stdout_path, result.stderr_path, snap.root_exit_code,
                                 handle["lookup"], private_frames=handle["root"] / "private-failure-frames",
                                 module=handle["module"])
        temporary = inventory(handle["temporary"], deadline=self.deadline)
        metadata = {key: value for key, value in parsed.items()
                    if key not in {"classification", "unexpected", "test_count", "failures", "errors"}}
        metadata.update({"temporary_retained_file_count": len(temporary),
                         "temporary_inventory_sha256": sha(json.dumps(temporary, sort_keys=True).encode()),
                         "process_count": snap.total_processes, "tree_cleanup_verified": clean})
        row = Observation(handle["module"], handle["lookup"], parsed["classification"],
                          parsed["unexpected"], clean, parsed["test_count"], parsed["failures"],
                          parsed["errors"], snap.wall_seconds, snap.tree_cpu_seconds, "completed", metadata)
        # Retain capture, TEMP, and bounded failure frames on this disposable
        # runner. Verified tree exit is not permission to unlink by pathname.
        return row

    def poll(self, handle):
        require(shutil.disk_usage(self.root).free >= self.minimum_free_bytes,
                "disk_reserve_exhausted")
        snap = handle["owner"].poll()
        if not snap.root_reaped or snap.active_processes != 0:
            return None
        return self.observation(handle, handle["owner"].finish(timeout=5))

    def cancel(self, handle, reason):
        return self.observation(handle, handle["owner"].cancel(reason, timeout=5), canceled=True)

    def cleanup(self):
        clean = True
        for owner in self.owners:
            try:
                result = owner.result or owner.cancel("coordinator_cleanup", timeout=5)
                clean = clean and result.snapshot.cleanup_verified
            except Exception:
                clean = False
        return clean


def verify_clone(commands, clone, source_inventory, candidate, deadline):
    require((clone / ".git").is_dir() and not (clone / ".git").is_symlink(), "not_full_clone")
    require(not (clone / ".git/objects/info/alternates").exists(), "object_alternates_present")
    common = commands.git(clone, "rev-parse", "--git-common-dir", deadline=deadline).strip()
    require((clone / common).resolve() == (clone / ".git").resolve(), "shared_git_common_dir")
    require(commands.git(clone, "rev-parse", "HEAD", deadline=deadline).strip() == BASE, "clone_wrong_head")
    require(not any(os.path.lexists(clone / name) for name in ("scratch", "output")), "private_roots_present")
    require(sha(normalized(clone / SUITE_PATH)) == CANDIDATE_HASH, "candidate_hash_mismatch")
    measured = inventory(clone, deadline=deadline)
    expected = dict(source_inventory)
    expected[SUITE_PATH] = sha(candidate)
    require(measured == expected, "clone_source_inventory_mismatch")
    # Also inspect Git object files for hardlinks, not only tracked work files.
    inventory(clone / ".git", exclude_git=False, deadline=deadline)
    return measured


def make_clones(commands, seed, candidate, run_root, sample, source_inventory, deadline):
    clones = []
    for lane in range(2):
        clone = run_root / ("sample-%d-lane-%d" % (sample, lane))
        commands.run(["git", "-c", "core.autocrlf=false", "clone", "--no-local", "--no-hardlinks",
                      "--no-checkout", str(seed), str(clone)], run_root, deadline)
        commands.git(clone, "-c", "core.autocrlf=false", "checkout", "--detach", BASE, deadline=deadline)
        (clone / SUITE_PATH).write_bytes(candidate)
        verify_clone(commands, clone, source_inventory, candidate, deadline)
        clones.append(clone)
    require(clones[0].resolve() != clones[1].resolve(), "clone_paths_overlap")
    return clones


def reviewed_budget(path, expected_hash):
    raw = normalized(path)
    require(len(expected_hash) == 64 and sha(raw) == expected_hash, "budget_plan_hash_mismatch")
    plan = json.loads(raw)
    require(plan.get("schema_version") == 1 and plan.get("status") == "reviewed-complete-lazy-proof",
            "lazy_budget_evidence_unavailable")
    require(plan.get("base") == BASE and plan.get("candidate_sha256") == CANDIDATE_HASH,
            "lazy_budget_source_mismatch")
    require(plan.get("lazy_proof_complete") is True and plan.get("all_lazy_controls_passed") is True,
            "lazy_budget_controls_incomplete")
    require(isinstance(plan.get("evidence_run_url"), str)
            and plan["evidence_run_url"].startswith("https://github.com/mshamblin5150-code/clinical-skills/actions/runs/"),
            "lazy_budget_evidence_link_missing")
    for field in ("per_pass_upper_seconds", "clone_setup_upper_seconds", "receipt_cleanup_upper_seconds"):
        value = plan.get(field)
        require(isinstance(value, (int, float)) and math.isfinite(value) and value > 0,
                "budget_bound_invalid")
    for field in ("per_pass_retained_disk_upper_bytes", "minimum_free_disk_reserve_bytes"):
        require(isinstance(plan.get(field), int) and plan[field] > 0, "disk_budget_bound_invalid")
    require(plan["minimum_free_disk_reserve_bytes"] >= 1024 ** 3, "disk_cleanup_reserve_too_small")
    require(plan["per_pass_upper_seconds"] * 4 + plan["clone_setup_upper_seconds"] * 4
            + plan["receipt_cleanup_upper_seconds"] * 4 <= 7800, "four_pass_budget_does_not_fit")
    return plan


def run_live_controls(commands, audit, root, deadline):
    """The *unchanged* refusal payload against independent synthetic fixture roots."""
    fixtures = []
    for lane in range(2):
        fixture = root / ("fixture-%d" % lane)
        tools = fixture / "tools"
        tools.mkdir(parents=True)
        for lookup in LOOKUPS:
            (tools / (lookup + ".py")).write_text(
                "from pathlib import Path\nDEFAULT_DATABASE = Path(__file__).with_name('committed.sqlite')\n"
                "def open_database(path=DEFAULT_DATABASE):\n    return 'synthetic unrelated open'\n", encoding="utf-8")
        for name, expression in (("default", "open_database()"),
                                 ("explicit", "open_database(DEFAULT_DATABASE)"),
                                 ("unrelated", "open_database(DEFAULT_DATABASE.with_name('other.sqlite'))")):
            # Two tests exercise both refusal targets in each unchanged payload.
            source = "import unittest\nimport icd10_lookup as a\nimport procedure_codes_lookup as b\nclass Synthetic(unittest.TestCase):\n"
            for index, target in enumerate(("a", "b")):
                expression_target = expression.replace("DEFAULT_DATABASE", target + ".DEFAULT_DATABASE")
                source += "    def test_%d(self):\n        %s.%s\n" % (index, target, expression_target)
            (tools / ("test_" + name + ".py")).write_text(source, encoding="utf-8")
        fixtures.append(fixture)
    runner = LiveRunner(fixtures, audit._SUBPROCESS, root / "refusal-probes", deadline=deadline)
    result = run_schedule(("test_default", "test_explicit", "test_unrelated"), 2, runner,
                          deadline=deadline, clock=time.monotonic, sleep=time.sleep)
    require(runner.cleanup() and result.complete, "live_refusal_controls_failed")
    require([row.classification for row in result.observations] ==
            ["reader", "reader", "reader", "reader", "nonreader", "nonreader"],
            "default_explicit_unrelated_refusal_contract_failed")
    emit("live_refusal_controls", pairs=6, passed=True)
    # A deterministic exclusive-create collision is forced in a shared path. It
    # detects the conflict, it does not certify arbitrary external paths safe.
    for private in (False, True):
        shared = root / ("private-collision" if private else "forced-collision")
        shared.mkdir()
        for lane, fixture in enumerate(fixtures):
            for module_index in range(2):
                module = "test_collision_%d" % module_index
                target = shared / (("lane-%d" % module_index) if private else "shared")
                source = (
                    "import unittest\nfrom pathlib import Path\nimport time\n"
                    "class Collision(unittest.TestCase):\n"
                    "    def test_exclusive_claim(self):\n"
                    "        root = Path(%r)\n"
                    "        peer = Path(%r)\n"
                    "        target = Path(%r)\n"
                    "        root.touch()\n"
                    "        with target.open('x'):\n"
                    "            limit = time.monotonic() + 10\n"
                    "            while not peer.exists() and time.monotonic() < limit:\n"
                    "                time.sleep(0.005)\n"
                    "            self.assertTrue(peer.exists())\n"
                    % (str(shared / ("ready-%d" % module_index)),
                       str(shared / ("ready-%d" % (1 - module_index))), str(target)))
                (fixture / "tools" / (module + ".py")).write_text(source, encoding="utf-8")
        # The payload runs two lookups, so the synthetic claim is removed only
        # between complete first/second-lookups via separate names below.
        # Derive the lookup from sys.argv in the fixture to keep claims distinct.
        for fixture in fixtures:
            for path in (fixture / "tools").glob("test_collision_*.py"):
                value = path.read_text(encoding="utf-8").replace("import unittest\n", "import unittest\nimport sys\n")
                value = value.replace("        root.touch()", "        target = target.with_name(target.name + '-' + sys.argv[3])\n        root.touch()")
                path.write_text(value, encoding="utf-8")
        runner = LiveRunner(fixtures, audit._SUBPROCESS, root / ("collision-private-probes" if private else "collision-shared-probes"),
                            deadline=deadline)
        result = run_schedule(("test_collision_0", "test_collision_1"), 2, runner,
                              deadline=deadline, clock=time.monotonic, sleep=time.sleep)
        require(runner.cleanup(), "collision_control_cleanup_failed")
        require(result.complete if private else (not result.complete and any(row.unexpected for row in result.observations)),
                "collision_control_did_not_discriminate")
        emit("collision_control", private_paths=private, expected_outcome_observed=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observer", type=Path, required=True)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--budget-plan", type=Path, required=True)
    parser.add_argument("--budget-sha256", required=True)
    parser.add_argument("--job-start-epoch", type=float, required=True)
    args = parser.parse_args(argv)
    started = time.monotonic()
    commands = None
    runners = []
    run_root = None
    success = False
    try:
        require(os.name == "nt" and platform.python_version() == "3.14.4", "requires_windows_python_3_14_4")
        require(os.environ.get("GITHUB_RUN_ATTEMPT") == "1" and os.environ.get("GITHUB_REF") == BRANCH,
                "unauthorized_event_or_rerun")
        environment_preflight()
        # Workflow records this before checkout/setup. Clock drift cannot expand
        # the authority: the monotonic deadlines only shrink after this reading.
        elapsed = time.time() - args.job_start_epoch
        require(0 <= elapsed < 900, "preflight_budget_expired")
        job_deadline = started + max(0, 9000 - elapsed)
        preflight_deadline = started + max(0, 900 - elapsed)
        measurement_deadline = job_deadline - 300
        plan = reviewed_budget(args.budget_plan, args.budget_sha256)
        observer, seed = args.observer.resolve(), args.seed.resolve()
        require(observer != seed, "observer_is_seed")
        corpus_preflight((observer, seed))
        candidate = normalized(observer / SUITE_PATH)
        require(sha(candidate) == CANDIDATE_HASH, "candidate_hash_mismatch")
        run_root = Path(tempfile.mkdtemp(prefix="reader-comparison-", dir=os.environ["RUNNER_TEMP"]))
        require(outside(run_root, (observer, seed)), "evidence_inside_checkout")
        commands = OwnedCommands(run_root / "commands")
        require(commands.git(observer, "rev-parse", "HEAD", deadline=preflight_deadline).strip()
                == os.environ.get("GITHUB_SHA"), "observer_head_mismatch")
        require(not commands.git(observer, "status", "--porcelain=v1", "--untracked-files=all", deadline=preflight_deadline),
                "observer_not_clean")
        commands.git(observer, "merge-base", "--is-ancestor", BASE, "HEAD", deadline=preflight_deadline)
        observer_changed = set(commands.git(observer, "diff", "--name-only", BASE, "HEAD", deadline=preflight_deadline).splitlines())
        require(OBSERVER_REQUIRED <= observer_changed <= OBSERVER_ALLOWED, "observer_branch_scope_mismatch")
        require(commands.git(seed, "rev-parse", "HEAD", deadline=preflight_deadline).strip() == BASE, "seed_wrong_head")
        require(not commands.git(seed, "status", "--porcelain=v1", "--untracked-files=all", deadline=preflight_deadline),
                "seed_not_clean")
        require(not any(os.path.lexists(seed / name) for name in ("scratch", "output")), "seed_has_private_roots")
        # Match clone checkout normalization without altering committed identity.
        commands.git(seed, "-c", "core.autocrlf=false", "checkout-index", "--force", "--all", deadline=preflight_deadline)
        source_inventory = inventory(seed, deadline=preflight_deadline)
        audit = load_audit(seed)
        require(sha(normalized(seed / "tools/test_anchor_scan.py")) == QUALIFIED_ANCHOR_SHA256,
                "qualified_wrapper_source_changed")
        expected_static = static_population(audit, seed)
        require(expected_static["module_count"] == 447 and expected_static["test_module_count"] == 264
                and len(expected_static["reaching"]) == 131 and len(expected_static["pinned"]) == 11,
                "historical_population_changed")
        owner_controls = commands.run(
            [sys.executable, str(observer / "diagnostics/windows_job_probe_controls.py"),
             "--run", "--report-dir", str(run_root / "owner-controls")],
            observer / "diagnostics", preflight_deadline)
        owner_receipt = json.loads(owner_controls)
        require(owner_receipt.get("schema") == "windows-job-probe-controls-v1"
                and owner_receipt.get("status") == "passed"
                and owner_receipt.get("optimization_level") == 0
                and owner_receipt.get("files_retained") is True
                and owner_receipt.get("process_cleanup_verified") is True
                and owner_receipt.get("platform") == "win32"
                and str(owner_receipt.get("python", "")).split()[0] == "3.14.4"
                and owner_receipt.get("failed_count") == 0 and owner_receipt.get("skipped_count") == 0
                and owner_receipt.get("declared_control_ids") == owner_receipt.get("passed_control_ids") == OWNER_CONTROL_IDS
                and isinstance(owner_receipt.get("declared_control_ids"), list)
                and len(owner_receipt["declared_control_ids"]) > 0
                and owner_receipt.get("planned_count") == len(owner_receipt["declared_control_ids"])
                and owner_receipt.get("passed_count") == owner_receipt.get("planned_count"),
                "owner_controls_incomplete")
        emit("owner_controls", control_ids=OWNER_CONTROL_IDS, passed_count=len(OWNER_CONTROL_IDS),
             failed_count=0, skipped_count=0, passed=True)
        portable = commands.run([sys.executable, str(observer / "diagnostics/test_parallel_reader_controls.py"),
                                 "--retained-evidence-root", str(run_root / "scheduler-controls-evidence")],
                                observer / "diagnostics", preflight_deadline)
        portable_receipt = json.loads(portable)
        require(portable_receipt.get("schema_version") == 1 and portable_receipt.get("tests_run") == 22
                and portable_receipt.get("successful") is True
                and portable_receipt.get("retained_evidence_requested") is True
                and portable_receipt.get("failures") == 0 and portable_receipt.get("errors") == 0,
                "scheduler_controls_incomplete")
        registry = commands.run([sys.executable, str(observer / "diagnostics/test_parallel_observer_controls.py"),
                                 "--retained-evidence-root", str(run_root / "observer-controls-evidence")],
                                observer / "diagnostics", preflight_deadline)
        registry_receipt = json.loads(registry)
        require(registry_receipt.get("schema_version") == 1 and registry_receipt.get("tests_run") == 20
                and registry_receipt.get("successful") is True
                and registry_receipt.get("retained_evidence_requested") is True
                and registry_receipt.get("local_cleanup_proof_executed") is False
                and registry_receipt.get("failures") == 0 and registry_receipt.get("errors") == 0,
                "registry_controls_incomplete")
        emit("observer_controls", tests_run=20, failures=0, errors=0, passed=True,
             retained_evidence_requested=True, local_cleanup_proof_executed=False)
        run_live_controls(commands, audit, run_root / "live-controls", preflight_deadline)
        require(time.monotonic() < preflight_deadline, "preflight_budget_expired")
        measurement_deadline = min(measurement_deadline, time.monotonic() + 7800)
        emit("qualified", base=BASE, candidate_sha256=CANDIDATE_HASH, payload_sha256=PAYLOAD_HASH,
             population=expected_static, lock_override=False, clone_layout="two independent full clones",
             complete_filesystem_isolation=False, total_budget_seconds=9000,
             preflight_budget_seconds=900, measurement_budget_seconds=7800, cleanup_reserve_seconds=300)
        samples = []
        expected_dynamic = None
        expected_work = None
        for sample, cap in enumerate(ORDER):
            reserve = (4 - sample) * (plan["per_pass_upper_seconds"] + plan["clone_setup_upper_seconds"]
                                      + plan["receipt_cleanup_upper_seconds"])
            require(measurement_deadline - time.monotonic() >= reserve, "remaining_passes_do_not_fit_budget")
            remaining_disk = ((4 - sample) * plan["per_pass_retained_disk_upper_bytes"]
                              + plan["minimum_free_disk_reserve_bytes"])
            free_disk = shutil.disk_usage(run_root).free
            require(free_disk >= remaining_disk, "remaining_retained_clones_and_reports_do_not_fit_disk")
            emit("sample_budget", sample=sample, free_disk_bytes=free_disk,
                 remaining_disk_bound_bytes=remaining_disk, remaining_time_bound_seconds=reserve)
            sample_start = time.monotonic()
            observer_cpu_start = time.process_time()
            command_cpu_start = commands.tree_cpu_seconds
            command_cpu_unread_start = commands.cpu_unread_commands
            clones = make_clones(commands, seed, candidate, run_root, sample, source_inventory, measurement_deadline)
            corpus_preflight(clones)
            setup_seconds = time.monotonic() - sample_start
            for clone in clones:
                require(static_population(audit, clone) == expected_static, "static_population_changed")
            runner = LiveRunner(clones, audit._SUBPROCESS, run_root / ("sample-%d-evidence" % sample),
                                minimum_free_bytes=plan["minimum_free_disk_reserve_bytes"], deadline=measurement_deadline)
            runners.append(runner)
            audit_start = time.monotonic()
            result = run_schedule(expected_static["reaching"], cap, runner,
                                  deadline=measurement_deadline, clock=time.monotonic, sleep=time.sleep)
            wall_seconds = time.monotonic() - audit_start
            require(runner.cleanup(), "sample_cleanup_unverified")
            corpus_preflight(clones, admission=False)
            # Canonical rows are public allowlisted metrics; raw reports never are.
            for row in result.observations:
                emit("probe", sample=sample, cap=cap, **asdict(row))
            emit("sample_accounting", sample=sample, complete=result.complete,
                 accounting=account_pairs(expected_static["reaching"], result.observations),
                 unread_pairs=result.unread_pairs, first_error=result.first_error,
                 first_error_resolved=result.first_error_resolved, stop_reason=result.stop_reason,
                 diagnostics=result.diagnostics)
            require(result.complete, "sample_incomplete_no_speed_claim")
            sets = audit_sets(expected_static["reaching"], expected_static["pinned"], result.observations)
            require(not sets["unpinned_readers"] and not sets["stale_pins"], "reader_pin_findings")
            require(expected_dynamic is None or sets == expected_dynamic, "dynamic_audit_sets_changed")
            expected_dynamic = sets
            observed_work = work_signature(result.observations)
            require(expected_work is None or observed_work == expected_work, "per_pair_work_or_error_counts_changed")
            expected_work = observed_work
            require(len(result.observations) == 262, "pair_population_changed")
            require(all(row.tree_cpu_seconds is not None for row in result.observations), "tree_cpu_unread")
            for lane, clone in enumerate(clones):
                # Source bytes and database hashes must remain identical. Ignored
                # artifacts are separately counted and hashed, not called absent.
                tracked = commands.git(clone, "ls-files", "-z", deadline=measurement_deadline).split("\0")
                require(commands.git(clone, "rev-parse", "HEAD", deadline=measurement_deadline).strip() == BASE,
                        "sample_git_head_changed")
                require(not commands.git(clone, "diff", "--cached", "--name-only", deadline=measurement_deadline),
                        "sample_git_index_changed")
                require(commands.git(clone, "diff", "--name-only", "HEAD", deadline=measurement_deadline).splitlines() == [SUITE_PATH],
                        "sample_tracked_scope_changed")
                ignored = set(filter(None, commands.git(clone, "ls-files", "--others", "--ignored", "--exclude-standard", "-z",
                                                       deadline=measurement_deadline).split("\0")))
                untracked = set(filter(None, commands.git(clone, "ls-files", "--others", "--exclude-standard", "-z",
                                                         deadline=measurement_deadline).split("\0")))
                measured = inventory(clone, deadline=measurement_deadline)
                expected = dict(source_inventory)
                expected[SUITE_PATH] = sha(candidate)
                require(all(measured.get(path) == value for path, value in expected.items()), "source_or_database_mutated")
                extras = {name: digest for name, digest in measured.items() if name not in expected}
                require(set(extras) == ignored | untracked, "extra_file_accounting_unread")
                require(time.monotonic() < measurement_deadline, "measurement_budget_expired")
                emit("clone_receipt", sample=sample, lane=lane, tracked_paths=len([p for p in tracked if p]),
                     source_inventory_sha256=sha(json.dumps(expected, sort_keys=True).encode()),
                     ignored_or_untracked_files=len(extras), extra_inventory_sha256=sha(json.dumps(extras, sort_keys=True).encode()),
                     ignored_files=len(ignored), untracked_files=len(untracked),
                     database_hashes={name: value for name, value in expected.items() if name.endswith(".sqlite")},
                     ephemeral_absolute_writes_observed=False)
                # Retain the complete clone and all evidence until disposable
                # hosted-runner teardown. Later samples always use fresh clones.
            total_seconds = time.monotonic() - sample_start
            observer_cpu_seconds = time.process_time() - observer_cpu_start
            command_cpu_seconds = commands.tree_cpu_seconds - command_cpu_start
            require(commands.cpu_unread_commands == command_cpu_unread_start, "sample_command_tree_cpu_unread")
            probe_cpu_seconds = sum(row.tree_cpu_seconds for row in result.observations)
            record = {"sample": sample, "cap": cap, "refusal_probe_phase_wall_seconds": wall_seconds,
                      "setup_seconds": setup_seconds, "sample_including_setup_cleanup_seconds": total_seconds,
                      "summed_probe_wall_seconds": sum(row.wall_seconds for row in result.observations),
                      "summed_tree_cpu_seconds": probe_cpu_seconds,
                      "observer_process_cpu_seconds": observer_cpu_seconds,
                      "command_tree_cpu_seconds": command_cpu_seconds,
                      "measured_family_cpu_seconds": probe_cpu_seconds + observer_cpu_seconds + command_cpu_seconds,
                      "cpu_scope": "probe trees + setup/receipt command trees + observer process; excludes Actions/setup services and unrelated host work",
                      "tests_run": sum(row.test_count for row in result.observations),
                      "skipped_count": sum(row.metadata["skipped"] for row in result.observations),
                      "expected_failure_count": sum(row.metadata["expected_failures"] for row in result.observations),
                      "canonical_work_sha256": sha(json.dumps(observed_work, separators=(",", ":")).encode()),
                      "expected_refusal_failures": sum(row.failures for row in result.observations),
                      "expected_refusal_errors": sum(row.errors for row in result.observations),
                      "unexpected_errors": 0, "completed_unique_pairs": 262, "audit_sets": sets,
                      "import_walk_declared_limit": audit.DECLARED_LIMITS["import walk"]}
            require(time.monotonic() < measurement_deadline, "measurement_budget_expired")
            samples.append(record)
            emit("sample_complete", **record)
            require(time.monotonic() < measurement_deadline, "measurement_budget_expired")
        summaries = {}
        for cap in (1, 2):
            selected = [row for row in samples if row["cap"] == cap]
            summaries[str(cap)] = {key: {"median": statistics.median(row[key] for row in selected),
                                        "minimum": min(row[key] for row in selected),
                                        "maximum": max(row[key] for row in selected),
                                        "sample_variance": statistics.variance(row[key] for row in selected)}
                                   for key in ("refusal_probe_phase_wall_seconds", "summed_tree_cpu_seconds",
                                               "observer_process_cpu_seconds", "command_tree_cpu_seconds", "measured_family_cpu_seconds",
                                               "summed_probe_wall_seconds", "sample_including_setup_cleanup_seconds")}
        require(time.monotonic() < measurement_deadline, "measurement_budget_expired")
        emit("screening_complete", samples_per_side=2, summaries=summaries, adoption_proof=False,
             import_walk_declared_limit=audit.DECLARED_LIMITS["import walk"],
             five_sample_minimum_met=False, end_to_end_ci_measured=False,
             production_shared_checkout_safety_proved=False, complete_filesystem_isolation=False)
        require(time.monotonic() < measurement_deadline, "measurement_budget_expired")
        success = True
    except Hold as error:
        emit("hold", reason=str(error), diagnostics=error.diagnostics, speed_claim_allowed=False)
    except Exception as error:
        emit("hold", **exception_diagnostics(error, run_root), speed_claim_allowed=False)
    finally:
        clean = True
        for runner in runners:
            clean = runner.cleanup() and clean
        if commands is not None:
            clean = commands.cleanup() and clean
        # A cleanup failure preserves evidence and prevents a successful screen.
        emit("cleanup", process_trees_verified=clean, raw_reports_uploaded=False,
             retained_private_evidence=run_root is not None, retained_sample_clones=True,
             retained_probe_temporary=True, retained_capture_files=True,
             observer_wall_seconds=time.monotonic() - started)
        success = success and clean
    return 0 if success else 2


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    from console_codec import require_python_floor, use_utf8
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
