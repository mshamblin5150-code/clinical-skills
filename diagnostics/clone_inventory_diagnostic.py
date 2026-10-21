"""Temporary checkout-conversion diagnosis, never a population benchmark."""
from pathlib import Path
import argparse
import os
import platform
import tempfile
import time
import sys
import re
import shutil

import measure_parallel_readers as proof

DIAGNOSTIC_PATHS = {"diagnostics/clone_inventory_diagnostic.py",
                    "diagnostics/test_clone_inventory_diagnostic.py"}
PACKET_BASE = "e68ad4dc6080a77f776e6d23d1ef1ab75aa9ba56"


def text_crlf_equivalent(left, right):
    if b"\x00" in left or b"\x00" in right:
        return False
    try:
        left.decode("utf-8"); right.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return left.replace(b"\r\n", b"\n") == right.replace(b"\r\n", b"\n")


def discrepancy(left, right, expected, measured, allowlist):
    missing = set(expected) - set(measured)
    extra = set(measured) - set(expected)
    changed = {key for key in expected.keys() & measured.keys() if expected[key] != measured[key]}
    crlf_only = sum(text_crlf_equivalent((left / key).read_bytes(), (right / key).read_bytes())
                    for key in changed)
    different = missing | extra | changed
    visible = sorted(different & allowlist)
    return {"raw_equal": measured == expected, "missing": len(missing), "extra": len(extra),
            "content_mismatch": len(changed), "crlf_only": crlf_only,
            "paths": visible[:20], "path_overflow": max(0, len(visible) - 20),
            "unlisted_count": len(different - allowlist)}


def fresh_checkout(commands, donor, target, revision, deadline, *, before=False, synthetic=False):
    commands.run(["git", "clone", "--no-local", "--no-hardlinks", "--no-checkout",
                  str(donor), str(target)], target.parent, deadline)
    if synthetic:
        # Fixture-local setting only, same in both arms; never changes real seeds.
        commands.git(target, "config", "core.autocrlf", "true", deadline=deadline)
    else:
        inherited = commands.git(donor, "config", "get", "--default", "unset", "core.autocrlf",
                                 deadline=deadline).strip()
        fresh = commands.git(target, "config", "get", "--default", "unset", "core.autocrlf",
                             deadline=deadline).strip()
        proof.require(inherited == fresh, "fresh_seed_conversion_environment_differs")
    conversion = ["-c", "core.autocrlf=false"] if before else []
    commands.git(target, *conversion, "checkout", "--detach", revision, deadline=deadline)
    proof.require(commands.git(target, "rev-parse", "HEAD", deadline=deadline).strip() == revision,
                  "fresh_checkout_wrong_head")
    # This is the first status, matching the original clean-seed precondition.
    proof.require(not commands.git(target, "status", "--porcelain=v1", "--untracked-files=all",
                                   deadline=deadline), "fresh_checkout_not_clean")
    commands.git(target, "-c", "core.autocrlf=false", "checkout-index", "--force", "--all",
                 deadline=deadline)


def synthetic_comparison(commands, root, deadline):
    donor = root / "synthetic-donor"
    donor.mkdir()
    commands.git(donor, "init", deadline=deadline)
    files = {".gitattributes": b".gitattributes text eol=lf\n*.txt text\nfixed-lf.txt text eol=lf\nfixed-crlf.txt text eol=crlf\n*.bin -text\n",
             "default.txt": b"one\ntwo\n", "fixed-lf.txt": b"one\ntwo\n",
             "fixed-crlf.txt": b"one\ntwo\n", "opaque.bin": b"\x00one\r\ntwo\xff"}
    for name, data in files.items():
        (donor / name).write_bytes(data)
    commands.git(donor, "-c", "core.autocrlf=false", "add", "--all", deadline=deadline)
    commands.git(donor, "-c", "user.name=Diagnostic Fixture", "-c",
                 "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                 "commit", "-m", "Synthetic checkout fixture", deadline=deadline)
    revision = commands.git(donor, "rev-parse", "HEAD", deadline=deadline).strip()
    baseline, candidate = root / "synthetic-baseline", root / "synthetic-candidate"
    fresh_checkout(commands, donor, baseline, revision, deadline, synthetic=True)
    fresh_checkout(commands, donor, candidate, revision, deadline, before=True, synthetic=True)
    result = discrepancy(baseline, candidate, proof.inventory(baseline, deadline=deadline),
                         proof.inventory(candidate, deadline=deadline), set(files))
    proof.emit("synthetic_inventory", **result)
    proof.require(result["content_mismatch"] == 1 and result["crlf_only"] == 1
                  and result["paths"] == ["default.txt"] and not result["missing"] and not result["extra"],
                  "synthetic_mechanism_not_reproduced")


def clone_comparison(commands, seed, candidate, root, source_inventory, deadline, allowlist):
    clone = root / "clone"
    commands.run(["git", "-c", "core.autocrlf=false", "clone", "--no-local", "--no-hardlinks",
                  "--no-checkout", str(seed), str(clone)], root, deadline)
    commands.git(clone, "-c", "core.autocrlf=false", "checkout", "--detach", proof.BASE, deadline=deadline)
    (clone / proof.SUITE_PATH).write_bytes(candidate)
    expected = dict(source_inventory)
    expected[proof.SUITE_PATH] = proof.sha(candidate)
    measured = proof.inventory(clone, deadline=deadline)
    # Suite replacement is intentional in both branches. Exclude its original
    # seed bytes from classification; raw admission below still includes its hash.
    result = discrepancy(seed, clone, {k: v for k, v in expected.items() if k != proof.SUITE_PATH},
                         {k: v for k, v in measured.items() if k != proof.SUITE_PATH}, allowlist)
    result["raw_equal"] = measured == expected
    try:
        proof.verify_clone(commands, clone, source_inventory, candidate, deadline)
    except proof.Hold as error:
        if str(error) != "clone_source_inventory_mismatch":
            raise
        result["guard"] = "clone_source_inventory_mismatch"
    else:
        result["guard"] = "passed"
    return clone, result


def negative_controls(commands, clone, expected, candidate, root, deadline):
    """Exercise the original verifier, retain every injected file off-checkout."""
    target = clone / ".gitignore"
    original = target.read_bytes()
    retained = root / "negative-evidence"
    retained.mkdir()
    for kind in ("modified", "missing", "extra", "binary"):
        extra = clone / "diagnostic-injected-extra.txt"
        if kind == "missing":
            target.rename(retained / "missing-original")
        elif kind == "extra":
            extra.write_bytes(b"synthetic extra\n")
        else:
            target.write_bytes((b"\x00" if kind == "binary" else b"synthetic modification\n") + original)
        rejected = False
        try:
            proof.verify_clone(commands, clone, expected, candidate, deadline)
        except proof.Hold as error:
            proof.require(str(error) == "clone_source_inventory_mismatch", "negative_wrong_guard")
            rejected = True
        finally:
            if kind == "missing":
                (retained / "missing-original").rename(target)
            elif kind == "extra":
                extra.rename(retained / "extra")
            else:
                target.rename(retained / kind)
                target.write_bytes(original)
        proof.require(rejected, "inventory_negative_control_not_rejected")
        proof.verify_clone(commands, clone, expected, candidate, deadline)
        proof.emit("inventory_negative_control", kind=kind, rejected=True, restored_raw_inventory=True)


def validate_results(results):
    baseline = results["baseline"]
    proof.require(baseline["guard"] == "clone_source_inventory_mismatch"
                  and baseline["content_mismatch"] > 0 and not baseline["missing"]
                  and not baseline["extra"]
                  and baseline["crlf_only"] == baseline["content_mismatch"],
                  "baseline_not_explained_by_checkout_conversion")
    proof.require(results["candidate"]["guard"] == "passed"
                  and results["candidate"]["raw_equal"], "candidate_inventory_not_equal")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observer", type=Path, required=True)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--job-start-epoch", type=float, required=True)
    args = parser.parse_args(argv)
    started = time.monotonic()
    commands = None
    success = False
    try:
        proof.require(os.name == "nt" and platform.python_version() == "3.14.4",
                      "requires_windows_python_3_14_4")
        proof.require(os.environ.get("GITHUB_RUN_ATTEMPT") == "1"
                      and os.environ.get("GITHUB_REF") == proof.BRANCH, "unauthorized_event_or_rerun")
        proof.environment_preflight()
        proof.require("INVENTORY_DIAGNOSTIC_TEST_ROOT" not in os.environ,
                      "inherited_diagnostic_test_override")
        elapsed = time.time() - args.job_start_epoch
        proof.require(0 <= elapsed < 480, "diagnostic_setup_budget_expired")
        deadline = time.monotonic() + 540 - elapsed
        observer, donor = args.observer.resolve(), args.seed.resolve()
        proof.require(observer != donor, "observer_is_seed")
        proof.corpus_preflight((observer, donor))
        root = Path(tempfile.mkdtemp(prefix="clone-inventory-", dir=os.environ["RUNNER_TEMP"]))
        proof.require(proof.outside(root, (observer, donor)), "evidence_inside_checkout")
        commands = proof.OwnedCommands(root / "commands")
        # Retain all clones/captures. Refuse low-disk runners rather than deleting
        # evidence to make room; this bound is diagnostic-only, not a benchmark claim.
        proof.require(shutil.disk_usage(root).free >= 10 * 1024 ** 3, "diagnostic_disk_reserve_unavailable")
        proof.require(commands.git(observer, "rev-parse", "HEAD", deadline=deadline).strip()
                      == os.environ.get("GITHUB_SHA"), "observer_head_mismatch")
        proof.require(not commands.git(observer, "status", "--porcelain=v1", "--untracked-files=all",
                                       deadline=deadline), "observer_not_clean")
        commands.git(observer, "merge-base", "--is-ancestor", proof.BASE, "HEAD", deadline=deadline)
        changed = set(commands.git(observer, "diff", "--name-only", proof.BASE, "HEAD",
                                   deadline=deadline).splitlines())
        proof.require(proof.OBSERVER_REQUIRED | DIAGNOSTIC_PATHS <= changed
                      <= proof.OBSERVER_ALLOWED | DIAGNOSTIC_PATHS, "observer_branch_scope_mismatch")
        commands.git(observer, "merge-base", "--is-ancestor", PACKET_BASE, "HEAD", deadline=deadline)
        packet_changed = set(commands.git(observer, "diff", "--name-only", PACKET_BASE, "HEAD",
                                          deadline=deadline).splitlines())
        proof.require(packet_changed == DIAGNOSTIC_PATHS | {".github/workflows/ci-parallel-proof.yml"},
                      "diagnostic_packet_scope_mismatch")
        proof.require(commands.git(donor, "rev-parse", "HEAD", deadline=deadline).strip() == proof.BASE,
                      "seed_wrong_head")
        proof.require(not commands.git(donor, "status", "--porcelain=v1", "--untracked-files=all",
                                       deadline=deadline), "seed_not_clean")
        candidate = proof.normalized(observer / proof.SUITE_PATH)
        proof.require(proof.sha(candidate) == proof.CANDIDATE_HASH, "candidate_hash_mismatch")
        tracked = set(commands.git(donor, "ls-tree", "-r", "--name-only", proof.BASE,
                                   deadline=deadline).splitlines())
        allowlist = {name for name in tracked if name.startswith("tools/") or name in
                     {".gitignore", ".gitattributes", "README.md", "AGENTS.md"}}
        version = commands.run(["git", "--version"], root, deadline).decode().strip()
        version = version if re.fullmatch(r"git version [0-9]+(?:\.[0-9]+)+\.windows\.[0-9]+", version) else "other"
        conversion = commands.git(donor, "config", "get", "--default", "unset", "core.autocrlf",
                                  deadline=deadline).strip().lower()
        conversion = conversion if conversion in {"true", "false", "input", "unset"} else "other"
        proof.emit("diagnostic_admitted", population_probes=0, speed_claim_allowed=False,
                   git_version=version, inherited_conversion=conversion,
                   setup_elapsed_seconds=elapsed, cleanup_reserve_seconds=60)
        test_root = root / "portable-controls"
        test_root.mkdir()
        test_env = dict(os.environ, INVENTORY_DIAGNOSTIC_TEST_ROOT=str(test_root))
        commands.run([sys.executable, "-m", "unittest", "discover", "-s", "diagnostics",
                      "-p", "test_clone_inventory_diagnostic.py"], observer, deadline, env=test_env)
        proof.emit("portable_diagnostic_controls", passed=True)
        synthetic_comparison(commands, root, deadline)
        results = {}
        for label, before in (("baseline", False), ("candidate", True)):
            case_root = root / label
            case_root.mkdir()
            seed = case_root / "seed"
            fresh_checkout(commands, donor, seed, proof.BASE, deadline, before=before)
            proof.corpus_preflight((seed,))
            expected = proof.inventory(seed, deadline=deadline)
            clone, result = clone_comparison(commands, seed, candidate, case_root, expected, deadline, allowlist)
            results[label] = result
            proof.emit("repository_inventory", case=label, **result)
            if before and result["guard"] == "passed":
                negative_controls(commands, clone, expected, candidate, case_root, deadline)
        validate_results(results)
        proof.require(not commands.git(observer, "status", "--porcelain=v1", "--untracked-files=all",
                                       deadline=deadline), "observer_post_status_not_clean")
        proof.emit("diagnostic_complete", baseline_reproduced=True, candidate_raw_equal=True,
                   population_probes=0, speed_claim_allowed=False,
                   observer_seconds=time.monotonic() - started,
                   whole_job_elapsed_seconds=time.time() - args.job_start_epoch)
        success = True
    except proof.Hold as error:
        proof.emit("diagnostic_hold", reason=str(error), population_probes=0, speed_claim_allowed=False)
    except Exception:
        proof.emit("diagnostic_hold", reason="unexpected_diagnostic_exception",
                   population_probes=0, speed_claim_allowed=False)
    finally:
        clean = commands.cleanup() if commands is not None else True
        proof.emit("diagnostic_cleanup", process_trees_verified=clean, retained_evidence=True,
                   raw_reports_uploaded=False, observer_seconds=time.monotonic() - started)
        success = success and clean
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
