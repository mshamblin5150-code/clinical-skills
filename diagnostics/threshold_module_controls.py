"""Fixed threshold module qualification child; imports are runtime-only.

The caller authenticates the complete arm, this child and its expected source hash,
then owns the bounded process tree and coherent stdout/stderr capture. This helper
is not the timed refusal payload and is not a per-executed-ID observer. Discovery
does not run test bodies; dynamic skipTest membership cannot be inferred from it.
Control results use the stock unittest lifecycle, runner and result, unchanged.
"""
import hashlib
import argparse
import contextlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import sys
import unittest

MODULE = "test_threshold_sheet"
RESULT_PREFIX = "LAZY_PROOF_RESULT:"
EXPECTED_COUNT = 345
EXPECTED_IDS_SHA256 = "b2bbc719d12380d3068eb95f4645b8d7e775c8a22dc4a16386f93f0c5483bf40"
CONTROL_IDS = tuple(sorted(MODULE + "." + name for name in (
    "CoverageIsPerSource.test_a_second_sources_omissions_are_checked",
    "CoverageIsPerSource.test_known_is_filtered_to_the_rows_citing_that_source",
    "CoverageIsPerSource.test_the_ungraded_count_is_a_real_count_of_sources",
    "CoverageIsPerSource.test_one_source_graded_and_one_not_reports_both_halves",
    "CoverageIsPerSource.test_a_scope_out_still_discharges_its_recommendation",
    "CoverageIsPerSource.test_the_mode_cross_check_is_per_source",
    "CoverageIsPerSource.test_a_record_built_from_another_document_is_refused",
    "CoverageIsPerSource.test_where_the_corpus_was_mounted_is_not_a_finding",
    "CoverageIsPerSource.test_a_record_that_names_no_document_is_not_guessed_at",
    "CoverageIsPerSource.test_the_class_check_reads_the_rows_own_source_record",
    "BindingARecordToEachSource.test_the_sweep_alias_wins_over_the_exact_name_root_and_is_reported",
    "BindingARecordToEachSource.test_each_sweep_alias_absence_is_named_before_recs_root_fallback",
    "BindingARecordToEachSource.test_an_explicit_recs_argument_beats_both_lookup_roots",
    "BindingARecordToEachSource.test_a_keyed_argument_binds_to_that_source",
    "BindingARecordToEachSource.test_an_untrusted_record_is_not_bound",
    "BindingARecordToEachSource.test_the_existing_provenance_hatch_can_accept_an_untrusted_record",
    "BindingARecordToEachSource.test_a_bare_path_binds_to_the_only_source",
    "BindingARecordToEachSource.test_a_bare_path_on_a_two_source_sheet_is_refused_rather_than_guessed",
    "BindingARecordToEachSource.test_an_unknown_source_key_is_an_error_and_not_a_silent_no_op",
    "BindingARecordToEachSource.test_the_same_key_twice_is_an_error",
    "BindingARecordToEachSource.test_recs_root_resolves_one_record_per_source_key",
    "BindingARecordToEachSource.test_an_explicit_path_that_does_not_exist_says_no_such_file",
    "BindingARecordToEachSource.test_a_record_the_root_does_not_hold_reads_as_never_built",
    "BindingARecordToEachSource.test_a_file_that_parses_and_is_not_a_record_is_ungraded_too",
    "BindingARecordToEachSource.test_every_absent_record_says_why",
    "BindingARecordToEachSource.test_an_unreadable_record_is_ungraded_rather_than_a_traceback",
    "WatermarkGate.test_conformance_foreign_provenance_needs_the_explicit_override",
    "WatermarkGate.test_conformance_command_override_is_explicit",
    "WatermarkGate.test_conformance_does_not_read_an_extraction_in_progress",
)))
REASONS = frozenset(("module_origin_mismatch", "module_discovery_failed",
                     "duplicate_module_ids", "module_id_reload_mismatch",
                     "module_population_changed", "child_arguments_invalid",
                     "module_source_changed", "controls_population_changed",
                     "controls_result_unread", "child_receipt_invalid"))
DISCOVERY_KEYS = frozenset(("test_ids", "test_count", "sorted_ids_sha256",
                            "loader_errors", "executed_test_count", "reload_verified"))
COMMON_KEYS = frozenset(("schema", "action", "status", "module",
                         "module_origin_verified", "module_source_sha256"))


class Refused(RuntimeError):
    """A literal diagnostic category, never application exception text."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refused("child_receipt_invalid")
        result[key] = value
    return result


def _invalid_constant(_):
    raise Refused("child_receipt_invalid")


def _receipt(stdout_bytes, returncode, expected_source_sha256, action):
    """Decode only canonical finite receipt bytes, never captured stderr text."""
    try:
        if (type(stdout_bytes) is not bytes or len(stdout_bytes) > 131072
                or type(returncode) is not int or returncode != 0
                or type(expected_source_sha256) is not str
                or not re.fullmatch(r"[0-9a-f]{64}", expected_source_sha256)
                or not stdout_bytes.startswith(RESULT_PREFIX.encode("ascii"))):
            raise Refused("child_receipt_invalid")
        row = json.loads(stdout_bytes[len(RESULT_PREFIX):].decode("ascii"),
                         object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
        canonical = (RESULT_PREFIX + json.dumps(row, sort_keys=True, ensure_ascii=True,
                     allow_nan=False, separators=(",", ":")) + "\n").encode("ascii")
        if (type(row) is not dict or stdout_bytes != canonical
                or row.get("schema") != "threshold-module-child-v1"
                or row.get("action") != action or row.get("status") != "passed"
                or row.get("module") != MODULE or row.get("module_origin_verified") is not True
                or row.get("module_source_sha256") != expected_source_sha256):
            raise Refused("child_receipt_invalid")
        return row
    except (ValueError, TypeError, OverflowError, RecursionError):
        raise Refused("child_receipt_invalid") from None


def _validate_discovery(discovery):
    if type(discovery) is not dict or set(discovery) != DISCOVERY_KEYS:
        raise Refused("child_receipt_invalid")
    ids = discovery["test_ids"]
    if (type(ids) is not list or len(ids) != EXPECTED_COUNT
            or any(type(value) is not str or not re.fullmatch(
                r"test_threshold_sheet\.[A-Za-z_][A-Za-z_0-9]*\.test[A-Za-z_0-9]*", value)
                for value in ids)
            or ids != sorted(set(ids))
            or type(discovery["test_count"]) is not int or discovery["test_count"] != EXPECTED_COUNT
            or discovery["sorted_ids_sha256"] != EXPECTED_IDS_SHA256
            or hashlib.sha256(json.dumps(ids, ensure_ascii=True,
                separators=(",", ":")).encode("ascii")).hexdigest() != EXPECTED_IDS_SHA256
            or type(discovery["loader_errors"]) is not int or discovery["loader_errors"] != 0
            or type(discovery["executed_test_count"]) is not int or discovery["executed_test_count"] != 0
            or discovery["reload_verified"] is not True):
        raise Refused("child_receipt_invalid")


def validate_discovery_receipt(stdout_bytes, returncode, expected_source_sha256):
    """Qualify caller-owned stdout bytes; ownership and source pins stay upstream."""
    row = _receipt(stdout_bytes, returncode, expected_source_sha256, "discover")
    if set(row) != COMMON_KEYS | DISCOVERY_KEYS:
        raise Refused("child_receipt_invalid")
    _validate_discovery({key: row[key] for key in DISCOVERY_KEYS})
    return row


def validate_controls_receipt(stdout_bytes, returncode, expected_source_sha256):
    """Only a complete, all-pass original-control population qualifies an arm."""
    row = _receipt(stdout_bytes, returncode, expected_source_sha256, "controls")
    labels = ("failure", "error", "skipped", "expected_failure", "unexpected_success")
    expected = COMMON_KEYS | {"discovery", "control_ids", "tests_run", "passed_count",
                              "successful", "stock_result_accounting", "per_test_execution_observed"}
    expected |= {label + suffix for label in labels for suffix in ("_count", "_ids")}
    if set(row) != expected:
        raise Refused("child_receipt_invalid")
    _validate_discovery(row["discovery"])
    if (row["control_ids"] != list(CONTROL_IDS)
            or type(row["tests_run"]) is not int or row["tests_run"] != 29
            or type(row["passed_count"]) is not int or row["passed_count"] != 29
            or row["successful"] is not True or row["stock_result_accounting"] is not True
            or row["per_test_execution_observed"] is not False):
        raise Refused("child_receipt_invalid")
    for label in labels:
        if (type(row[label + "_count"]) is not int or row[label + "_count"] != 0
                or row[label + "_ids"] != []):
            raise Refused("child_receipt_invalid")
    return row


def cases(member):
    if isinstance(member, unittest.TestSuite):
        for nested in member:
            yield from cases(nested)
    else:
        yield member


def _threshold_case_id(test):
    if (not isinstance(test, unittest.TestCase) or type(test).__module__ != MODULE
            or type(test).__name__ == "_FailedTest"):
        raise Refused("module_discovery_failed")
    identity = MODULE + "." + type(test).__qualname__ + "." + test._testMethodName
    if (not re.fullmatch(r"test_threshold_sheet\.[A-Za-z_][A-Za-z_0-9]*\.test[A-Za-z_0-9]*", identity)
            or test.id() != identity):
        raise Refused("module_discovery_failed")
    return identity


def discover_module(module):
    """Read actual module objects and freshly reload each ID, running no bodies."""
    loader = unittest.TestLoader()
    found = list(cases(loader.loadTestsFromModule(module)))
    if loader.errors or not found or any(type(test).__name__ == "_FailedTest" for test in found):
        raise Refused("module_discovery_failed")
    ids = [_threshold_case_id(test) for test in found]
    if len(set(ids)) != len(ids):
        raise Refused("duplicate_module_ids")
    for test in found:
        fresh = unittest.TestLoader()
        reloaded = list(cases(fresh.loadTestsFromName(test.id())))
        if (fresh.errors or len(reloaded) != 1 or type(reloaded[0]) is not type(test)
                or reloaded[0] is test or reloaded[0]._testMethodName != test._testMethodName
                or _threshold_case_id(reloaded[0]) != _threshold_case_id(test)):
            raise Refused("module_id_reload_mismatch")
    ids.sort()
    digest = hashlib.sha256(json.dumps(ids, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
    return {"test_ids": ids, "test_count": len(ids), "sorted_ids_sha256": digest,
            "loader_errors": 0, "executed_test_count": 0, "reload_verified": True}


def run_controls(module):
    """Run only the literal original IDs with stock unittest lifecycle/result.

    Stock result counts are not a start/stop execution ledger. Unknown/subtest or
    class-lifecycle error identities refuse qualification rather than being renamed.
    """
    if sys.modules.get(MODULE) is not module:
        raise Refused("controls_population_changed")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(CONTROL_IDS)
    selected = list(cases(suite))
    if loader.errors or [_threshold_case_id(test) for test in selected] != list(CONTROL_IDS):
        raise Refused("controls_population_changed")
    with contextlib.redirect_stdout(sys.stderr):
        result = unittest.TextTestRunner(stream=sys.stderr, verbosity=0).run(suite)
    groups = {
        "failure": [test.id() for test, _ in result.failures],
        "error": [test.id() for test, _ in result.errors],
        "skipped": [test.id() for test, _ in result.skipped],
        "expected_failure": [test.id() for test, _ in result.expectedFailures],
        "unexpected_success": [test.id() for test in result.unexpectedSuccesses],
    }
    exceptional = [name for values in groups.values() for name in values]
    if (len(set(exceptional)) != len(exceptional)
            or not set(exceptional).issubset(CONTROL_IDS)
            or result.testsRun != len(CONTROL_IDS)):
        raise Refused("controls_result_unread")
    row = {"control_ids": list(CONTROL_IDS), "tests_run": result.testsRun,
           "passed_count": result.testsRun - len(exceptional),
           "successful": result.wasSuccessful(), "stock_result_accounting": True,
           "per_test_execution_observed": False}
    for label, ids in groups.items():
        row[label + "_count"] = len(ids)
        row[label + "_ids"] = sorted(ids)
    return row


def verify_source(repo, expected_source_sha256):
    """Bind the selected test source; the caller authenticates the full tree."""
    target = repo / "tools/test_threshold_sheet.py"
    if (type(expected_source_sha256) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", expected_source_sha256)):
        raise Refused("module_source_changed")
    before = target.lstat()
    if (not stat.S_ISREG(before.st_mode) or target.is_symlink() or before.st_nlink != 1
            or getattr(before, "st_file_attributes", 0) & 0x400 or before.st_size > 1048576):
        raise Refused("module_source_changed")
    raw = target.read_bytes()
    after = target.lstat()
    key = lambda item: (item.st_dev, item.st_ino, item.st_mode, item.st_size,
                        item.st_mtime_ns, item.st_ctime_ns, item.st_nlink,
                        getattr(item, "st_file_attributes", 0))
    if (key(before) != key(after) or len(raw) != before.st_size
            or hashlib.sha256(raw).hexdigest() != expected_source_sha256):
        raise Refused("module_source_changed")
    return raw


def verify_module_origin(module, repo):
    target = repo / "tools/test_threshold_sheet.py"
    if (Path(module.__file__).resolve() != target
            or Path(module.__spec__.origin).resolve() != target
            or sys.modules.get(MODULE) is not module):
        raise Refused("module_origin_mismatch")


def load_module(repo, expected_source_sha256):
    """Import only this module from the caller-authenticated complete checkout."""
    if not repo.is_absolute() or repo.resolve(strict=True) != repo:
        raise Refused("module_origin_mismatch")
    directory = repo / "tools"
    if (directory.resolve(strict=True) != directory or directory.is_symlink()
            or getattr(directory.lstat(), "st_file_attributes", 0) & 0x400):
        raise Refused("module_origin_mismatch")
    target = repo / "tools/test_threshold_sheet.py"
    if target.is_symlink() or not target.is_file() or MODULE in sys.modules:
        raise Refused("module_origin_mismatch")
    raw = verify_source(repo, expected_source_sha256)
    sys.path.insert(0, str(repo / "tools"))
    # -B prevents cache writes, not cache reads. Compile the authenticated source
    # bytes so stale or substituted .pyc content cannot satisfy source admission.
    spec = importlib.util.spec_from_file_location(MODULE, target)
    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULE] = module
    exec(compile(raw, str(target), "exec"), module.__dict__)
    verify_module_origin(module, repo)
    verify_source(repo, expected_source_sha256)
    return module


def main(argv=None):
    """Emit a finite receipt; incidental imports and tests stay in private stderr."""
    action = "unknown"
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--action", choices=("discover", "controls"), required=True)
        parser.add_argument("--repo", required=True)
        parser.add_argument("--expected-source-sha256", required=True)
        with contextlib.redirect_stdout(sys.stderr):
            args = parser.parse_args(argv)
            action = args.action
            module = load_module(Path(args.repo), args.expected_source_sha256)
            discovery = discover_module(module)
            if (discovery["test_count"] != EXPECTED_COUNT
                    or discovery["sorted_ids_sha256"] != EXPECTED_IDS_SHA256):
                raise Refused("module_population_changed")
            detail = discovery if action == "discover" else {
                "discovery": discovery, **run_controls(module)}
            verify_source(Path(args.repo), args.expected_source_sha256)
            verify_module_origin(module, Path(args.repo))
        row = {"schema": "threshold-module-child-v1", "action": action,
               "status": "passed", "module": MODULE,
               "module_origin_verified": True,
               "module_source_sha256": args.expected_source_sha256, **detail}
        code = 0 if action == "discover" or detail["passed_count"] == 29 else 1
        if code:
            row["status"] = "failed"
    except BaseException as error:
        reason = (error.args[0] if type(error) is Refused and len(error.args) == 1
                  and error.args[0] in REASONS else "child_unavailable")
        row = {"schema": "threshold-module-child-v1", "action": action,
               "status": "refused", "reason": reason}
        code = 2
    # Emit bytes so Windows TextIO newline translation cannot change the receipt.
    wire = (RESULT_PREFIX + json.dumps(row, sort_keys=True, ensure_ascii=True,
            allow_nan=False, separators=(",", ":")) + "\n").encode("ascii")
    sys.stdout.buffer.write(wire)
    sys.stdout.buffer.flush()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
