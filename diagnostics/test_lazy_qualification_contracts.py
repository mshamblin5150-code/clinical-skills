"""Synthetic public-boundary tests. No Windows execution or measured suite runs.

Run only after independent review, with diagnostics on PYTHONPATH:
  python -B -m unittest discover -s <this directory> -p test_lazy_qualification_contracts.py
"""
import copy
import ast
import inspect
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import measure_lazy_suite_ids as subject


class ShortMeasurementRootTests(unittest.TestCase):
    def setUp(self):
        parent = Path(subject.__file__).resolve().parent.parent / 'scratch/sessions'
        self.temp = tempfile.TemporaryDirectory(prefix='short-root-control-', dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.owner = self.parent / 'lazy-qualification-original-owner-root'
        self.observer = self.parent / 'observer'
        self.seed = self.parent / 'seed'
        for path in (self.owner, self.observer, self.seed):
            path.mkdir()
        self.marker = self.seed / 'unchanged.txt'
        self.marker.write_bytes(b'original\r\nbytes\n')

    def create(self):
        return subject.create_measurement_root(self.owner, self.observer, self.seed)

    def test_fresh_short_sibling_preserves_owner_source_and_environment(self):
        import os
        before_env = dict(os.environ)
        before_owner = list(self.owner.iterdir())
        root = self.create()
        self.assertEqual(root.parent, self.owner.parent)
        self.assertNotEqual(root, self.owner)
        self.assertTrue(root.name.startswith('lc-'))
        self.assertEqual(list(root.iterdir()), [])
        self.assertLess(len(str(root).encode('utf-16-le')), len(str(self.owner).encode('utf-16-le')))
        self.assertEqual(list(self.owner.iterdir()), before_owner)
        self.assertEqual(self.marker.read_bytes(), b'original\r\nbytes\n')
        self.assertEqual(dict(os.environ), before_env)

    def test_overlapping_or_outside_returned_root_refuses(self):
        outside = self.parent / 'elsewhere' / 'lc-outside'
        outside.mkdir(parents=True)
        for root in (self.owner, self.observer, self.seed, self.seed / 'lc-nested', outside):
            with self.subTest(root=root.name), mock.patch.object(subject.tempfile, 'mkdtemp', return_value=str(root)):
                with self.assertRaises(subject.Refused):
                    self.create()

    def test_nonempty_and_regular_returned_root_refuse(self):
        nonempty = self.parent / 'lc-full'
        nonempty.mkdir()
        (nonempty / 'private.txt').write_bytes(b'untouched')
        regular = self.parent / 'lc-file'
        regular.write_bytes(b'untouched')
        for root in (nonempty, regular):
            with self.subTest(root=root.name), mock.patch.object(subject.tempfile, 'mkdtemp', return_value=str(root)):
                with self.assertRaises(subject.Refused):
                    self.create()
        self.assertEqual((nonempty / 'private.txt').read_bytes(), b'untouched')
        self.assertEqual(regular.read_bytes(), b'untouched')

    def test_symlink_returned_root_refuses(self):
        target = self.parent / 'target'
        target.mkdir()
        link = self.parent / 'lc-link'
        link.symlink_to(target, target_is_directory=True)
        with mock.patch.object(subject.tempfile, 'mkdtemp', return_value=str(link)):
            with self.assertRaises(subject.Refused):
                self.create()

    def test_root_that_is_not_shorter_refuses(self):
        root = self.parent / ('x' * 70)
        root.mkdir()
        with mock.patch.object(subject.tempfile, 'mkdtemp', return_value=str(root)):
            with self.assertRaises(subject.Refused):
                self.create()

    def test_reparse_ancestor_refuses(self):
        from types import SimpleNamespace
        root = self.parent / 'lc-fresh'
        root.mkdir()
        original = Path.lstat
        def metadata(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            if path == self.parent:
                return SimpleNamespace(st_mode=result.st_mode, st_file_attributes=0x400)
            return result
        with mock.patch.object(subject.tempfile, 'mkdtemp', return_value=str(root)), \
                mock.patch.object(Path, 'lstat', metadata):
            with self.assertRaises(subject.Refused):
                self.create()

    def test_qualification_uses_short_root_but_retains_original_owner(self):
        tree = ast.parse(inspect.getsource(subject.main))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name)]
        clones = [call for call in calls if call.func.id == 'make_clone']
        self.assertEqual(len(clones), 1)
        self.assertEqual(ast.unparse(clones[0].args[2]), 'clone_root')
        owners = [call for call in calls if call.func.id == 'Session']
        self.assertEqual(len(owners), 1)
        self.assertEqual(ast.unparse(owners[0].args[0]), 'root')
        constructors = [call for call in calls if call.func.id == 'create_measurement_root']
        self.assertEqual(len(constructors), 1)
        self.assertEqual([ast.unparse(arg) for arg in constructors[0].args], ['root', 'observer', 'seed'])


class FirstStatusReceiptTests(unittest.TestCase):
    def test_bounded_binary_safe_path_fields_and_rename_composite(self):
        field = b'"old\\tname" -> "new\\377name"'
        raw = b'R  ' + field + b'\n' + b'?? private\n' * 20
        receipt = subject.status_receipt(raw)
        self.assertEqual(receipt['category_counts'], {'R ': 1, '??': 20})
        self.assertEqual(receipt['entry_count'], 21)
        self.assertEqual(len(receipt['entries']), 8)
        self.assertEqual(receipt['omitted_entries'], 13)
        self.assertEqual(receipt['entries'][0]['path_field_token'], subject.digest(field))
        self.assertTrue(receipt['parse_complete'])
        self.assertNotIn('private', str(receipt))

    def test_malformed_status_never_discloses_rows(self):
        for raw in (b'PRIVATE', b'XX PRIVATE\n', b'R  PRIVATE'):
            with self.subTest(raw=raw):
                receipt = subject.status_receipt(raw)
                self.assertFalse(receipt['parse_complete'])
                self.assertNotIn('PRIVATE', str(receipt))

    def test_first_status_is_called_once_and_same_dirty_result_refuses(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / '.git').mkdir()
            session = mock.Mock()
            session.git.side_effect = ['.git\n', 'pinned\n']
            session.git_bytes.return_value = b' M sensitive\n'
            session.run.return_value = {'returncode': 0, 'stdout': 'PRIVATE VALUE'}
            with mock.patch.object(subject, 'emit') as emit:
                with self.assertRaisesRegex(subject.Refused, '^first_status_not_clean$'):
                    subject.first_clean(session, repo, 'pinned', 'baseline')
            session.git_bytes.assert_called_once_with(
                repo, 'status', '--porcelain=v1', '--untracked-files=all')
            self.assertEqual(session.git.call_count, 2)
            self.assertEqual(emit.call_args_list[0].kwargs['role'], 'baseline')
            self.assertNotIn('PRIVATE', str(emit.call_args_list))
            self.assertNotIn('sensitive', str(emit.call_args_list))

    def test_clean_first_status_does_not_observe_config(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / '.git').mkdir()
            session = mock.Mock()
            session.git.side_effect = ['.git\n', 'pinned\n']
            session.git_bytes.return_value = b''
            subject.first_clean(session, repo, 'pinned', 'candidate')
            session.run.assert_not_called()

    def test_config_allowlist_absent_and_failure(self):
        session = mock.Mock()
        session.run.side_effect = [
            {'returncode': 0, 'stdout': 'TRUE\n'},
            {'returncode': 1, 'stdout': ''}, RuntimeError('PRIVATE')]
        self.assertEqual(subject.conversion_config_receipt(session, Path('.')),
                         {'core.autocrlf': 'true', 'core.eol': 'unset',
                          'core.safecrlf': 'unavailable'})

    def test_config_deadline_failure_keeps_dirty_status_verdict(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / '.git').mkdir()
            session = mock.Mock()
            session.git.side_effect = ['.git\n', 'pinned\n']
            session.git_bytes.return_value = b' M changed\n'
            with mock.patch.object(subject, 'emit') as emit:
                def exhausted(*args):
                    self.assertEqual(emit.call_args_list[0].args, ('first_status_discrepancy',))
                    raise subject.Refused('global_budget_exhausted')
                session.run.side_effect = exhausted
                with self.assertRaisesRegex(subject.Refused, '^first_status_not_clean$'):
                    subject.first_clean(session, repo, 'pinned', 'seed')
            self.assertEqual(session.git_bytes.call_count, 1)
            self.assertEqual(set(emit.call_args_list[1].kwargs['effective_values'].values()),
                             {'unavailable'})


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
        "source_sha": "104ee03cd4d37519b12b3edbc4da5fbf31b631cf",
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
    def test_current_pin_and_raw_budget_are_bound_in_active_workflow(self):
        root = Path(subject.__file__).resolve().parent.parent
        workflow = (root / '.github/workflows/ci-parallel-proof.yml').read_text()
        budget = (root / 'diagnostics/lazy-qualification-budget.json').read_bytes()
        expected_pin = '104ee03cd4d37519b12b3edbc4da5fbf31b631cf'
        self.assertEqual(subject.BASE, expected_pin)
        self.assertEqual(subject.BUDGET['source_sha'], expected_pin)
        self.assertIn('ref: ' + expected_pin, workflow)
        self.assertEqual(subject.digest(budget), 'c8a0195e46b954adad9624ad48baa0c70687d8db6a0c7cde3213e0c4c7c550a7')
        self.assertNotIn('measure_lazy_suite_ids.py --observer', workflow)
        self.assertNotIn('cb0507279e4e6b66ad40d10bc746b0e0b699291e', workflow)

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
