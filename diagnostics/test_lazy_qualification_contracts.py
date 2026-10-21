"""Synthetic public-boundary tests. No Windows execution or measured suite runs.

Run only after independent review, with diagnostics on PYTHONPATH:
  python -B -m unittest discover -s <this directory> -p test_lazy_qualification_contracts.py
"""
import copy
from pathlib import Path
import tempfile
import unittest

import measure_lazy_suite_ids as subject


CONTROL_IDS = (
    "__main__.LazyBindingControls.test_successful_ids_reload_and_assert_without_diagnostics",
    "__main__.LazyBindingControls.test_empty_population_is_successful_without_diagnostics",
    "__main__.LazyBindingControls.test_each_mismatch_keeps_exact_failure_diagnostic",
    "__main__.LazyBindingControls.test_multiple_failures_continue_through_later_success_and_failure",
    "__main__.LazyBindingControls.test_discovery_errors_stop_before_any_reload_or_diagnostic",
    "__main__.LazyBindingControls.test_helper_error_on_failed_check_remains_visible",
)
RED_IDS = {CONTROL_IDS[0], CONTROL_IDS[3]}
OWNER_IDS = (
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


def control_report(variant):
    baseline = variant == "baseline"
    return {
        "schema_version": 1, "tests_run": 6, "error_count": 0,
        "failure_count": 2 if baseline else 0, "successful": not baseline,
        "expected_baseline_failure_ids": sorted(RED_IDS),
        "control_outcomes": [
            {"test_id": identity,
             "outcome": "failure" if baseline and identity in RED_IDS else "pass",
             "expected_baseline_failure": identity in RED_IDS,
             "errors": [], "failures": [], "measurements": []}
            for identity in CONTROL_IDS
        ],
    }


def owner_report():
    return {
        "schema": "windows-job-probe-controls-v1", "status": "passed",
        "platform": "win32", "python": "3.14.4", "optimization_level": 0,
        "files_retained": True, "process_cleanup_verified": True,
        "declared_control_ids": list(OWNER_IDS), "passed_control_ids": list(OWNER_IDS),
        "planned_count": 9, "passed_count": 9, "failed_count": 0, "skipped_count": 0,
        "controls": [{"control": identity} for identity in OWNER_IDS],
        "retained_evidence_root": "synthetic-retained-evidence",
    }


class TimedPlanContracts(unittest.TestCase):
    def test_twenty_probes_alternate_with_five_samples_in_each_population(self):
        plan = subject.build_plan()
        self.assertEqual([row["ordinal"] for row in plan], list(range(1, 21)))
        for lookup in ("icd10_lookup", "procedure_codes_lookup"):
            variants = [row["variant"] for row in plan if row["lookup"] == lookup]
            self.assertEqual(variants, ["baseline", "candidate"] * 5)
        self.assertEqual({row["lookup"] for row in plan},
                         {"icd10_lookup", "procedure_codes_lookup"})
        self.assertEqual([(row["variant"], row["lookup"]) for row in plan], [
            ("baseline", "icd10_lookup"), ("baseline", "procedure_codes_lookup"),
            ("candidate", "icd10_lookup"), ("candidate", "procedure_codes_lookup"),
        ] * 5)


def budget_plan():
    return {
        "schema_version": 1,
        "admission_mode": "estimate-not-completion-guarantee",
        "source_sha": "cb0507279e4e6b66ad40d10bc746b0e0b699291e",
        "approved_job_seconds": 5400,
        "setup_controls_estimate_seconds": 900,
        "measurement_estimate_seconds": 3900,
        "cleanup_reserve_seconds": 300,
        "contingency_seconds": 300,
        "baseline_probe_estimate_seconds": 350,
        "candidate_probe_estimate_seconds": 10,
        "receipt_estimate_seconds": 300,
        "minimum_free_bytes": 1073741824,
        "max_capture_bytes": 16777216,
    }


class BudgetAdmissionContracts(unittest.TestCase):
    def test_measurement_and_cleanup_reserve_fit_exactly_after_preflight(self):
        subject.admit_budget(budget_plan(), 4200)
        subject.admit_budget(budget_plan(), 4500)

    def test_one_fractional_second_short_cannot_admit(self):
        with self.assertRaises(subject.Refused):
            subject.admit_budget(budget_plan(), 4199.999)

    def test_missing_changed_and_unknown_budget_fields_refuse(self):
        for key in budget_plan():
            with self.subTest(missing=key):
                plan = budget_plan()
                del plan[key]
                with self.assertRaises(subject.Refused):
                    subject.admit_budget(plan, 4500)
            with self.subTest(changed=key):
                plan = budget_plan()
                plan[key] = 0 if isinstance(plan[key], int) else "unapproved"
                with self.assertRaises(subject.Refused):
                    subject.admit_budget(plan, 4500)
        plan = budget_plan()
        plan["per_probe_timeout_seconds"] = 350
        with self.assertRaises(subject.Refused):
            subject.admit_budget(plan, 4500)

    def test_nonfinite_or_nonnumeric_remaining_time_cannot_admit(self):
        for remaining in (float("nan"), float("inf"), -1, True, "4500", None):
            with self.subTest(remaining=remaining):
                with self.assertRaises(subject.Refused):
                    subject.admit_budget(budget_plan(), remaining)


class ActualMethodControlContracts(unittest.TestCase):
    def test_expected_baseline_red_and_candidate_green_have_identical_six_ids(self):
        ids = subject.validate_controls(control_report("baseline"), "baseline", 1)
        self.assertEqual(ids, set(CONTROL_IDS))
        self.assertEqual(subject.validate_controls(control_report("candidate"), "candidate", 0, ids), ids)

    def test_baseline_green_is_not_accepted_as_expected_red(self):
        with self.assertRaises(subject.Refused):
            subject.validate_controls(control_report("candidate"), "baseline", 0)

    def test_candidate_red_is_not_accepted_as_green(self):
        with self.assertRaises(subject.Refused):
            subject.validate_controls(control_report("baseline"), "candidate", 1)

    def test_incomplete_or_inconsistent_counts_and_exit_codes_refuse(self):
        for field, value in (("schema_version", 2), ("tests_run", 5),
                             ("error_count", 1), ("failure_count", 1), ("successful", False)):
            with self.subTest(field=field):
                row = control_report("candidate")
                row[field] = value
                with self.assertRaises(subject.Refused):
                    subject.validate_controls(row, "candidate", 0)
        with self.assertRaises(subject.Refused):
            subject.validate_controls(control_report("candidate"), "candidate", 1)

    def test_missing_duplicate_and_replaced_control_id_refuse(self):
        for mode in ("missing", "duplicate", "replaced"):
            with self.subTest(mode=mode):
                row = control_report("candidate")
                if mode == "missing":
                    row["control_outcomes"].pop()
                elif mode == "duplicate":
                    row["control_outcomes"][-1] = copy.deepcopy(row["control_outcomes"][0])
                else:
                    row["control_outcomes"][-1]["test_id"] = "__main__.LazyBindingControls.test_unapproved"
                with self.assertRaises(subject.Refused):
                    subject.validate_controls(row, "candidate", 0, set(CONTROL_IDS))

    def test_swapped_baseline_failure_identity_refuses_even_with_same_total(self):
        row = control_report("baseline")
        row["control_outcomes"][0]["outcome"] = "pass"
        row["control_outcomes"][1]["outcome"] = "failure"
        with self.assertRaises(subject.Refused):
            subject.validate_controls(row, "baseline", 1)

    def test_error_or_changed_expected_failure_flag_refuses(self):
        for key, value in (("outcome", "error"), ("expected_baseline_failure", False)):
            with self.subTest(key=key):
                row = control_report("candidate")
                row["control_outcomes"][0][key] = value
                with self.assertRaises(subject.Refused):
                    subject.validate_controls(row, "candidate", 0)


class OwnerControlContracts(unittest.TestCase):
    def test_exact_nine_controls_and_verified_cleanup_are_accepted(self):
        subject.validate_owner_controls(owner_report())

    def test_incomplete_or_unsafe_owner_report_refuses(self):
        for field, value in (("schema", "unknown"), ("status", "failed"),
                             ("optimization_level", 1), ("files_retained", False),
                             ("process_cleanup_verified", False), ("planned_count", 8),
                             ("passed_count", 8), ("failed_count", 1), ("skipped_count", 1)):
            with self.subTest(field=field):
                row = owner_report()
                row[field] = value
                with self.assertRaises(subject.Refused):
                    subject.validate_owner_controls(row)

    def test_missing_duplicate_swapped_and_unknown_owner_controls_refuse(self):
        for field in ("declared_control_ids", "passed_control_ids", "controls"):
            for mode in ("missing", "duplicate", "swapped", "unknown"):
                with self.subTest(field=field, mode=mode):
                    row = owner_report()
                    values = row[field]
                    if mode == "missing":
                        values.pop()
                    elif mode == "duplicate":
                        values[-1] = copy.deepcopy(values[0])
                    elif mode == "swapped":
                        values[0], values[1] = values[1], values[0]
                    else:
                        values[-1] = {"control": "unknown"} if field == "controls" else "unknown"
                    with self.assertRaises(subject.Refused):
                        subject.validate_owner_controls(row)


class SummaryContracts(unittest.TestCase):
    def samples(self):
        return [{**row, "wall_seconds": float(row["ordinal"]),
                 "tree_cpu_seconds": 0.5, "valid": True,
                 "module_tests_run": 6, "module_tests_expected": 6}
                for row in subject.build_plan()]

    def test_complete_ordered_twenty_samples_yield_four_honest_groups(self):
        complete, groups = subject.summarize(self.samples(), subject.build_plan())
        self.assertTrue(complete)
        self.assertEqual(groups, [
            {"variant": "baseline", "lookup": "icd10_lookup", "count": 5,
             "median_seconds": 9.0, "minimum_seconds": 1.0, "maximum_seconds": 17.0},
            {"variant": "baseline", "lookup": "procedure_codes_lookup", "count": 5,
             "median_seconds": 10.0, "minimum_seconds": 2.0, "maximum_seconds": 18.0},
            {"variant": "candidate", "lookup": "icd10_lookup", "count": 5,
             "median_seconds": 11.0, "minimum_seconds": 3.0, "maximum_seconds": 19.0},
            {"variant": "candidate", "lookup": "procedure_codes_lookup", "count": 5,
             "median_seconds": 12.0, "minimum_seconds": 4.0, "maximum_seconds": 20.0},
        ])

    def test_partial_samples_cannot_claim_complete(self):
        complete, groups = subject.summarize(self.samples()[:-1], subject.build_plan())
        self.assertFalse(complete)
        self.assertEqual([row["count"] for row in groups], [5, 5, 5, 4])

    def test_empty_samples_make_no_timing_claims(self):
        for plan in (subject.build_plan(), []):
            with self.subTest(plan_length=len(plan)):
                complete, groups = subject.summarize([], plan)
                self.assertFalse(complete)
                self.assertEqual(len(groups), 4)
                for row in groups:
                    self.assertEqual(row["count"], 0)
                    for key in ("median_seconds", "minimum_seconds", "maximum_seconds"):
                        self.assertIsNone(row[key])

    def test_duplicate_swapped_and_mutated_samples_cannot_claim_complete(self):
        for mode in ("duplicate", "swapped", "lookup"):
            with self.subTest(mode=mode):
                samples = self.samples()
                if mode == "duplicate":
                    samples[-1] = copy.deepcopy(samples[0])
                elif mode == "swapped":
                    samples[0], samples[1] = samples[1], samples[0]
                else:
                    samples[0]["lookup"] = "procedure_codes_lookup"
                complete, _groups = subject.summarize(samples, subject.build_plan())
                self.assertFalse(complete)

    def test_invalid_sample_cannot_claim_complete(self):
        for value in (False, None, 1):
            with self.subTest(valid=value):
                samples = self.samples()
                samples[0]["valid"] = value
                complete, _groups = subject.summarize(samples, subject.build_plan())
                self.assertFalse(complete)

    def test_nonpositive_or_nonfinite_duration_cannot_claim_complete(self):
        for value in (0, -1, float("nan"), float("inf"), float("-inf")):
            with self.subTest(wall_seconds=value):
                samples = self.samples()
                samples[0]["wall_seconds"] = value
                complete, _groups = subject.summarize(samples, subject.build_plan())
                self.assertFalse(complete)


class VerifiedCaptureContracts(unittest.TestCase):
    def verify(self, stderr, stdout="", expected_count=3):
        with tempfile.TemporaryDirectory(prefix="synthetic-capture-", dir=Path(__file__).parent) as directory:
            root = Path(directory)
            output, errors = root / "stdout.bin", root / "stderr.bin"
            output.write_text(stdout, encoding="utf-8")
            errors.write_text(stderr, encoding="utf-8")
            result = {"stdout_path": str(output), "stderr_path": str(errors),
                      "stdout": stdout, "stderr": stderr, "returncode": 0}
            return subject.verify_probe(result, expected_count, "icd10_lookup")

    def test_exact_three_test_capture_passes(self):
        self.verify("Ran 3 tests in 0.123s\n\nOK\n")

    def test_orphan_traceback_cannot_hide_behind_clean_footer(self):
        with self.assertRaises(subject.Refused):
            self.verify("Traceback (most recent call last):\n  File \"synthetic.py\", line 1, in test\n"
                        "RuntimeError: synthetic\nRan 3 tests in 0.123s\n\nOK\n")

    def test_refusal_marker_cannot_hide_behind_clean_footer(self):
        with self.assertRaises(subject.Refused):
            self.verify("Ran 3 tests in 0.123s\n\nOK\n", "CODE_SET_DATABASE_OPEN_REFUSED\n")

    def test_mismatched_test_count_refuses(self):
        with self.assertRaises(subject.Refused):
            self.verify("Ran 2 tests in 0.123s\n\nOK\n")

    def test_skipped_result_refuses(self):
        with self.assertRaises(subject.Refused):
            self.verify("Ran 3 tests in 0.123s\n\nOK (skipped=1)\n")

    def test_failed_result_refuses(self):
        with self.assertRaises(subject.Refused):
            self.verify("Ran 3 tests in 0.123s\n\nFAILED (failures=1)\n")


class ExactModuleResultContracts(unittest.TestCase):
    def probe(self, report, returncode=0, expected_count=6):
        return subject.classify_probe({"stdout": "", "stderr": report,
                                       "returncode": returncode}, expected_count)

    def test_exact_successful_result_is_valid(self):
        self.assertEqual(self.probe("Ran 6 tests in 1.2s\n\nOK\n"), {
            "classification": "nonreader", "refusal_marker_present": False,
            "module_tests_run": 6, "module_tests_expected": 6,
            "completed_test_result": True, "valid": True,
        })

    def test_refusal_marker_precedes_process_error(self):
        row = self.probe("CODE_SET_DATABASE_OPEN_REFUSED\nRan 6 tests in 1.2s\nOK\n", 1)
        self.assertEqual(row["classification"], "reader")
        self.assertFalse(row["valid"])

    def test_nonzero_exit_is_error_even_when_footer_claims_success(self):
        row = self.probe("Ran 6 tests in 1.2s\nOK\n", 1)
        self.assertEqual(row["classification"], "error")
        self.assertFalse(row["valid"])

    def test_missing_underfilled_duplicate_or_failed_results_are_invalid(self):
        for report in ("", "Ran 5 tests in 1.2s\nOK\n",
                       "Ran 6 tests in 1.2s\n", "OK\n",
                       "Ran 6 tests in 1.2s\nOK\nOK\n",
                       "Ran 6 tests in 1.2s\nRan 6 tests in 1.2s\nOK\n",
                       "Ran 6 tests in 1.2s\nFAILED (errors=1)\n"):
            with self.subTest(report=report):
                self.assertFalse(self.probe(report)["valid"])


class RawIdentityContracts(unittest.TestCase):
    def test_exact_reviewed_bytes_are_returned_unchanged(self):
        from pathlib import Path
        import hashlib
        import tempfile
        raw = b'{"synthetic": true}\n'
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directory:
            path = Path(directory) / 'reviewed.txt'
            path.write_bytes(raw)
            self.assertEqual(subject.read_reviewed_bytes(path, hashlib.sha256(raw).hexdigest()), raw)

    def test_line_ending_and_other_byte_mutations_refuse(self):
        from pathlib import Path
        import hashlib
        import tempfile
        raw = b'{"synthetic": true}\n'
        expected = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directory:
            path = Path(directory) / 'reviewed.txt'
            for mutated in (raw.replace(b'\n', b'\r\n'), raw.replace(b'\n', b'\r'),
                            raw + b' ', raw.replace(b'true', b'false')):
                with self.subTest(mutated=mutated):
                    path.write_bytes(mutated)
                    with self.assertRaises(subject.Refused):
                        subject.read_reviewed_bytes(path, expected)


if __name__ == "__main__":
    unittest.main()
