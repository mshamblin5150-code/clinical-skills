"""Bounded status evidence for an unchanged observer prefix, never its full main.

The unprimed process runs no Git command before the original owned HEAD/status
pair. A separate process and checkout deliberately measure status priming.
Only fixed codes, counts, hashes, and exact allowlisted paths leave the runner.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import sys
import tempfile
import time
from types import SimpleNamespace


OBSERVER_HEAD = "96a8c794b71184881fbaa9b3df471fecf2f9b331"
OBSERVER_TREE = "01b0a3e6ad4c2aea7bfb23b37679064877e10d24"
SEED_HEAD = "38c431b15b7fafb0f5f89a67ecb501de318c47a1"
BUDGET_HASH = "a50ca5d8e7d73797b03330e23b57b6354bae95cdbd42f4f526bd4fab9ac65a59"
CANDIDATE_HASH = "f2f97e56313d7f8957bec0bd20fd91c9efd8c48c44871c5c69056eb830d43275"
BRANCH = "refs/heads/diagnostic/2013-parallel-proof-20261020"
SOURCE_HASHES = {
    "diagnostics/measure_parallel_readers.py": "5c1abd882b0e599f413dfc279648bfc0cab0738f4ed8dcd85804941679c5c7c1",
    "diagnostics/parallel_reader_capture.py": "15630af9a15e1bf8a8046dc2b6baffffd48a9046624d9830b7328fc659741542",
    "diagnostics/parallel_reader_diagnostics.py": "f27a9cdc106ed9ffdf48f669004f3263421e33a4211ec785b6791f25754aba50",
    "diagnostics/parallel_reader_scheduler.py": "30d662e7d052dd9ae81e9919ddd35f6059a125b2d8da7e1604f689525b18c4b7",
    "diagnostics/windows_job_probe.py": "23618bc9ce17388c26e35e31e4f302ba5d47aa00158fb4519f1c4909b0a1f261",
    "tools/console_codec.py": "6281bdee51690de7c49d8442a8c5c4fe5d30e482bd35798e5c7cc5d23467dc32",
    "tools/python_floor.py": "7ddcbbdd8c32646ef8764d8dfacd2929ad383c0c6a968373f4d2965322a3ec88",
    "tools/git_paths.py": "3ce90bd4c814f29378d445a0ab895833a4fdfb6f4500599dd7bfa38fd9d02435",
}
IMPORTED_PATHS = tuple(path for path in SOURCE_HASHES if not path.endswith("/measure_parallel_readers.py"))
POLICY_PATHS = ("tools/console_codec.py", "tools/python_floor.py", "tools/git_paths.py")
KNOWN_PATHS = frozenset(SOURCE_HASHES) | {
    "tools/test_suite_ids.py", "diagnostics/parallel-proof-budget.json",
    ".github/workflows/ci-parallel-proof.yml",
    "diagnostics/test_parallel_reader_controls.py", "diagnostics/test_parallel_observer_controls.py",
    "diagnostics/windows_job_probe_controls.py",
} | {
    str(Path(path).parent.as_posix()) + "/__pycache__/" + Path(path).stem + ".cpython-314.pyc"
    for path in IMPORTED_PATHS
}
UNMERGED = frozenset({"DD", "AU", "UD", "UA", "DU", "AA", "UU"})
STATUS_CODES = ({x + y for x in " MTADRC" for y in " MTD"} - {"  "}) | UNMERGED | {"??", "!!"}
SAFE_HOLDS = frozenset({
    "requires_windows_python_3_14_4", "unauthorized_event_or_rerun",
    "optimized_python_invalidates_controls", "inherited_lock_override",
    "clinical_environment_override", "source_environment_override", "known_fixed_corpus_present",
    "preflight_budget_expired", "budget_plan_hash_mismatch", "lazy_budget_evidence_unavailable",
    "lazy_budget_source_mismatch", "lazy_budget_controls_incomplete", "lazy_budget_evidence_link_missing",
    "budget_bound_invalid", "disk_budget_bound_invalid", "disk_cleanup_reserve_too_small",
    "four_pass_budget_does_not_fit", "observer_is_seed", "known_or_default_corpus_present",
    "candidate_hash_mismatch", "evidence_inside_checkout", "preinstalled_git_unavailable",
    "preinstalled_git_executable_invalid", "command_cleanup_unverified", "owned_command_failed",
    "command_output_exceeds_contract", "whole_job_budget_exhausted", "observer_head_mismatch",
    "observer_not_clean", "observer_tree_mismatch", "seed_wrong_head", "post_status_not_clean",
    "before_status_not_clean", "status_record_invalid", "diagnostic_budget_expired",
    "source_hash_mismatch", "source_origin_mismatch", "unexpected_preloaded_module",
    "detached_head_mismatch", "helper_head_mismatch", "before_status_location_invalid",
    "diagnostic_contract_mismatch",
})


class DiagnosticHold(RuntimeError):
    """A fixed diagnostic reason, never arbitrary exception text."""


def require(condition, code):
    if not condition:
        raise DiagnosticHold(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def normalized(path):
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def emit(event, **values):
    print(json.dumps({"event": event, **values}, sort_keys=True, allow_nan=False), flush=True)


def bootstrap_command_policy(helper=None):
    """Run the helper-only command policy, restoring canonical import state."""
    helper = Path(helper).resolve() if helper is not None else Path(__file__).resolve().parent.parent
    names = tuple(Path(path).stem for path in POLICY_PATHS)
    require(all(name not in sys.modules for name in names), "unexpected_preloaded_module")
    previous_path = sys.path[:]
    try:
        for relative in POLICY_PATHS:
            path = helper / relative
            require(not path.is_symlink() and digest(normalized(path)) == SOURCE_HASHES[relative],
                    "source_hash_mismatch")
        sys.path.insert(0, str(helper / "tools"))
        from console_codec import require_python_floor, use_utf8
        verify_origins(helper, ("tools/console_codec.py",))
        use_utf8()
        require_python_floor()
        verify_origins(helper, POLICY_PATHS)
    finally:
        # Every canonical name was absent on entry. Keep references so cleanup
        # removes only modules introduced during this bootstrap, not a later
        # replacement. Restore even when the floor refuses with SystemExit.
        introduced = {name: sys.modules[name] for name in names if name in sys.modules}
        for name, module in introduced.items():
            if sys.modules.get(name) is module:
                del sys.modules[name]
        sys.path[:] = previous_path


def emit_hold(error, mode, original, evidence_root):
    """Keep original sanitized diagnostics; never print raw exception text."""
    if isinstance(error, DiagnosticHold) or (original and isinstance(error, original.Hold)):
        reason = str(error)
        diagnostics = error.diagnostics if original and isinstance(error, original.Hold) else None
        emit("hold", mode=mode, reason=reason if reason in SAFE_HOLDS else "unexpected_exception",
             diagnostics=diagnostics, raw_details_withheld=True)
        return
    if original is not None:
        try:
            details = original.exception_diagnostics(error, evidence_root)
            emit("hold", mode=mode, **details, raw_details_withheld=True)
            return
        except Exception:
            pass
    emit("hold", mode=mode, reason="unexpected_exception", safe_detail_available=False,
         private_detail_retained=False, raw_details_withheld=True)


def require_clean_status(status, original_require):
    """The original predicate and reason, including refusal of whitespace."""
    original_require(not status, "observer_not_clean")


def sanitize_status(raw):
    """Read only porcelain-v1 LF/CRLF records; malformed mixtures fail closed.

    Quoted, renamed, or non-allowlisted path fields are opaque hashes, not paths.
    Unknown names never pass through JSON or an exception message.
    """
    summary = {"bytes": len(raw), "sha256": digest(raw), "clean": not raw,
               "valid": False, "records": 0, "categories": {}, "known_paths": [],
               "unknown_paths": 0, "unknown_path_sha256": [], "detail_truncated": False}
    if len(raw) >= 2000000 or b"\x00" in raw:
        return summary
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeError:
        return summary
    text = text.replace("\r\n", "\n")
    if "\r" in text or (text and not text.endswith("\n")):
        return summary
    lines = text[:-1].split("\n") if text else []
    if any(len(line) < 4 or line[2] != " " or line[:2] not in STATUS_CODES for line in lines):
        return summary
    categories = Counter()
    known = []
    unknown = []
    for line in lines:
        code, path = line[:2], line[3:]
        category = ("untracked" if code == "??" else "ignored" if code == "!!"
                    else "unmerged" if code in UNMERGED else "tracked")
        categories[category] += 1
        if path in KNOWN_PATHS:
            known.append({"status": code, "path": path})
        else:
            unknown.append(digest(path.encode("utf-8")))
    summary.update(valid=True, records=len(lines), categories=dict(categories),
                   known_paths=known[:32], unknown_paths=len(unknown),
                   unknown_path_sha256=unknown[:16], detail_truncated=len(known) > 32 or len(unknown) > 16)
    return summary


def emit_retained_status(commands, attempt, run_root, mode, phase):
    """Read only the exact failed status call's retained, bounded stdout."""
    try:
        counter, owner_count = attempt
        require(commands.counter == counter and len(commands.owners) == owner_count + 1,
                "diagnostic_contract_mismatch")
        result = commands.owners[-1].result
        require(result is not None, "diagnostic_contract_mismatch")
        expected = (run_root / "commands" / ("command-%04d" % counter) / "stdout.bin").resolve()
        path = Path(result.stdout_path).resolve()
        require(path == expected and not path.is_symlink(), "evidence_inside_checkout")
        with path.open("rb") as stream:
            raw = stream.read(2000000)
        size = path.stat().st_size
        complete = size == len(raw) and bool(result.snapshot.cleanup_verified)
        summary = sanitize_status(raw)
        summary.update(capture_bytes=size, read_complete=complete,
                       sha256_scope="complete_capture" if complete else "bounded_prefix",
                       original_status_call_returned=False, clean=False)
        if not complete:
            summary.update(valid=False, clean=False)
        emit("status", mode=mode, phase=phase, **summary)
    except Exception:
        emit("status_unread", mode=mode, phase=phase, reason="retained_status_unavailable",
             raw_details_withheld=True)


def verify_origins(observer, paths):
    for relative in paths:
        module = sys.modules.get(Path(relative).stem)
        require(module is not None and Path(module.__file__).resolve() == (observer / relative).resolve(),
                "source_origin_mismatch")


def load_original(observer):
    # Reading checked-out bytes and detached HEAD files does not run Git or prime
    # the partial clone's object store. Hash every transitive local import first.
    for relative, expected in SOURCE_HASHES.items():
        path = observer / relative
        require(not path.is_symlink() and digest(normalized(path)) == expected, "source_hash_mismatch")
    require(all(Path(path).stem not in sys.modules for path in IMPORTED_PATHS), "unexpected_preloaded_module")
    sys.path.insert(0, str(observer / "diagnostics"))
    # Direct script execution does not cache the main module. run_path preserves
    # that property and retains each original function's original globals.
    original = SimpleNamespace(**runpy.run_path(str(observer / "diagnostics/measure_parallel_readers.py"),
                                               run_name="preflight_observer"))
    verify_origins(observer, tuple(path for path in IMPORTED_PATHS if path.startswith("diagnostics/")))
    sys.path.insert(0, str(observer / "tools"))
    from console_codec import require_python_floor, use_utf8
    verify_origins(observer, ("tools/console_codec.py",))
    use_utf8()
    require_python_floor()
    verify_origins(observer, IMPORTED_PATHS)
    require(original.BASE == SEED_HEAD and original.CANDIDATE_HASH == CANDIDATE_HASH
            and original.BRANCH == BRANCH, "diagnostic_contract_mismatch")
    return original


def capture_owned_status(original, observer, run_root, deadline):
    """Return the original retained stdout path only after owned cleanup verifies."""
    commands = original.OwnedCommands(run_root / "commands")
    attempt = None
    try:
        require(time.monotonic() < deadline, "diagnostic_budget_expired")
        attempt = (commands.counter + 1, len(commands.owners))
        commands.git(observer, "status", "--porcelain=v1", "--untracked-files=all", deadline=deadline)
        captured = Path(commands.owners[-1].result.stdout_path).resolve()
        require(captured.is_relative_to(run_root.resolve()), "evidence_inside_checkout")
        return captured
    except Exception:
        if attempt is not None:
            emit_retained_status(commands, attempt, run_root, "capture-before", "failed_before_import_capture")
        raise
    finally:
        try:
            clean = commands.cleanup()
        except Exception:
            clean = False
        emit("before_capture_cleanup", process_trees_verified=clean, private_files_retained=True,
             raw_reports_uploaded=False)
        require(clean, "command_cleanup_unverified")


def complete_before_capture(captured, deadline):
    """Routing output is not success unless its final operation fits the budget."""
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
        stream.write("before_status=" + str(captured) + "\n")
    emit("before_capture_ready", owner_sources_verified=True, observer_imported=False,
         private_files_retained=True, raw_reports_uploaded=False)
    require(time.monotonic() < deadline, "diagnostic_budget_expired")


def verify_final_identities(original, commands, observer, seed, deadline):
    require(time.monotonic() < deadline, "diagnostic_budget_expired")
    tree = commands.git(observer, "rev-parse", "HEAD^{tree}", deadline=deadline).strip()
    original.require(tree == OBSERVER_TREE, "observer_tree_mismatch")
    require(time.monotonic() < deadline, "diagnostic_budget_expired")
    original.require(commands.git(seed, "rev-parse", "HEAD", deadline=deadline).strip() == SEED_HEAD,
                     "seed_wrong_head")
    require(time.monotonic() < deadline, "diagnostic_budget_expired")


def capture_before_main(args):
    """Load owners from the helper checkout; never import observer source here."""
    started = time.monotonic()
    original = run_root = None
    try:
        elapsed = time.time() - args.job_start_epoch
        require(0 <= elapsed < 510, "diagnostic_budget_expired")
        deadline = min(started + 30, started + 540 - elapsed)
        observer, seed = args.observer.resolve(), args.seed.resolve()
        helper = Path(__file__).resolve().parent.parent
        require(args.before_status is None, "diagnostic_contract_mismatch")
        require((helper / ".git/HEAD").read_text(encoding="ascii").strip() == os.environ.get("GITHUB_SHA"),
                "helper_head_mismatch")
        require((observer / ".git/HEAD").read_text(encoding="ascii").strip() == OBSERVER_HEAD,
                "detached_head_mismatch")
        original = load_original(helper)
        original.require(os.name == "nt" and platform.python_version() == "3.14.4", "requires_windows_python_3_14_4")
        original.require(os.environ.get("GITHUB_RUN_ATTEMPT") == "1" and os.environ.get("GITHUB_REF") == BRANCH,
                         "unauthorized_event_or_rerun")
        original.environment_preflight()
        run_root = Path(tempfile.mkdtemp(prefix="preflight-before-", dir=os.environ["RUNNER_TEMP"]))
        original.require(original.outside(run_root, (observer, seed, helper)), "evidence_inside_checkout")
        captured = capture_owned_status(original, observer, run_root, deadline)
        require(time.monotonic() < deadline, "diagnostic_budget_expired")
        # Workflow routing only: never print this private absolute path. The
        # original owner retains stdout/stderr, and there is no copied raw file.
        complete_before_capture(captured, deadline)
        return 0
    except Exception as error:
        emit_hold(error, "capture-before", original, run_root)
        return 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("unprimed", "status-primed", "capture-before"), required=True)
    parser.add_argument("--observer", type=Path, required=True)
    parser.add_argument("--seed", type=Path, required=True)
    parser.add_argument("--before-status", type=Path)
    parser.add_argument("--job-start-epoch", type=float, required=True)
    args = parser.parse_args(argv)
    if args.mode == "capture-before":
        return capture_before_main(args)
    started = time.monotonic()
    original = commands = run_root = None
    deadline = started
    gate_status = before = gate_attempt = None
    success = False
    try:
        elapsed = time.time() - args.job_start_epoch
        require(0 <= elapsed < 540, "diagnostic_budget_expired")
        # Both observations share one 600-second job. Each has at most 120
        # command seconds and the global last 60 seconds are cleanup reserve.
        deadline = min(started + 120, started + 540 - elapsed)
        observer, seed = args.observer.resolve(), args.seed.resolve()
        helper = Path(__file__).resolve().parent.parent
        for root, expected in ((observer, OBSERVER_HEAD), (seed, SEED_HEAD)):
            require((root / ".git/HEAD").read_text(encoding="ascii").strip() == expected,
                    "detached_head_mismatch")
        require((helper / ".git/HEAD").read_text(encoding="ascii").strip() == os.environ.get("GITHUB_SHA"),
                "helper_head_mismatch")
        require((args.mode == "status-primed") == (args.before_status is not None), "diagnostic_contract_mismatch")
        if args.before_status is not None:
            before_path = args.before_status.resolve()
            require(before_path.is_relative_to(Path(os.environ["RUNNER_TEMP"]).resolve()),
                    "before_status_location_invalid")
            with before_path.open("rb") as stream:
                before = stream.read(2000000)
        original = load_original(observer)
        # Original pure preflight order; the historical 150-minute plan is
        # authenticated as evidence, not used to authorize this job's duration.
        original.require(os.name == "nt" and platform.python_version() == "3.14.4", "requires_windows_python_3_14_4")
        original.require(os.environ.get("GITHUB_RUN_ATTEMPT") == "1" and os.environ.get("GITHUB_REF") == BRANCH,
                         "unauthorized_event_or_rerun")
        original.environment_preflight()
        original.require(0 <= time.time() - args.job_start_epoch < 900, "preflight_budget_expired")
        original.reviewed_budget(observer / "diagnostics/parallel-proof-budget.json", BUDGET_HASH)
        original.require(observer != seed, "observer_is_seed")
        original.corpus_preflight((observer, seed))
        original.require(original.sha(original.normalized(observer / original.SUITE_PATH)) == CANDIDATE_HASH,
                         "candidate_hash_mismatch")
        run_root = Path(tempfile.mkdtemp(prefix="preflight-status-", dir=os.environ["RUNNER_TEMP"]))
        original.require(original.outside(run_root, (observer, seed, helper)), "evidence_inside_checkout")
        require(time.monotonic() < deadline, "diagnostic_budget_expired")
        commands = original.OwnedCommands(run_root / "commands")
        original.require(commands.git(observer, "rev-parse", "HEAD", deadline=deadline).strip() == OBSERVER_HEAD,
                         "observer_head_mismatch")
        require(time.monotonic() < deadline, "diagnostic_budget_expired")
        gate_attempt = (commands.counter + 1, len(commands.owners))
        gate_status = commands.git(observer, "status", "--porcelain=v1", "--untracked-files=all", deadline=deadline)
        require_clean_status(gate_status, original.require)
        success = True
    except Exception as error:
        emit_hold(error, args.mode, original, run_root)
    finally:
        # Nothing below enters original main past its first status guard. These
        # are read-only diagnostic observations, not audit/control admission.
        try:
            statuses_valid = True
            if gate_status is None and gate_attempt is not None:
                emit_retained_status(commands, gate_attempt, run_root, args.mode, "failed_original_guard_capture")
            if before is not None:
                summary = sanitize_status(before)
                emit("status", mode=args.mode, phase="before_import", **summary)
                statuses_valid = summary["valid"]
            if gate_status is not None:
                summary = sanitize_status(gate_status.encode("utf-8"))
                emit("status", mode=args.mode, phase="original_guard", **summary)
                statuses_valid = statuses_valid and summary["valid"]
                require(time.monotonic() < deadline, "diagnostic_budget_expired")
                after = commands.git(observer, "status", "--porcelain=v1", "--untracked-files=all", deadline=deadline)
                summary = sanitize_status(after.encode("utf-8"))
                emit("status", mode=args.mode, phase="after_guard", **summary)
                statuses_valid = statuses_valid and summary["valid"]
                verify_final_identities(original, commands, observer, seed, deadline)
                emit("source_identity", mode=args.mode, observer_head=OBSERVER_HEAD, observer_tree=OBSERVER_TREE,
                     seed_head=SEED_HEAD, imported_sources_verified=True, candidate_sha256=CANDIDATE_HASH,
                     budget_sha256=BUDGET_HASH)
                require(statuses_valid, "status_record_invalid")
                require(not after, "post_status_not_clean")
            require(statuses_valid, "status_record_invalid")
            require(not before, "before_status_not_clean")
            require(time.monotonic() < deadline, "diagnostic_budget_expired")
        except Exception as error:
            success = False
            emit_hold(error, args.mode, original, run_root)
        clean = commands.cleanup() if commands is not None else True
        success = success and clean and time.time() - args.job_start_epoch < 600
        emit("diagnostic_stop", mode=args.mode, prefix_clean=success, process_trees_verified=clean,
             raw_reports_uploaded=False, private_files_retained=True,
             full_original_preflight_passed=False, controls_run=False, population_run=False,
             speed_claim_allowed=False, observer_wall_seconds=time.monotonic() - started)
    return 0 if success else 2


if __name__ == "__main__":
    try:
        bootstrap_command_policy()
    except Exception as error:
        emit_hold(error, "command_policy", None, None)
        raise SystemExit(2)
    raise SystemExit(main())
