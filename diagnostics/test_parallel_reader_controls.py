"""Synthetic controls for the actual scheduler. Run only by a nonauthoring checker.

These are synthetic scheduler controls, not Windows process-tree qualification.
The separate owner control suite must pass on the hosted Windows runner too.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
import traceback
import unittest

from parallel_reader_capture import analyze_capture
from parallel_reader_scheduler import Observation, LOOKUPS, account_pairs, audit_sets, run_schedule


CONTROL_EVIDENCE_ROOT = None


@contextmanager
def control_case(*, prefix):
    """Hosted evidence stays in its qualified root; local cases clean normally."""
    if CONTROL_EVIDENCE_ROOT is None:
        with tempfile.TemporaryDirectory(prefix=prefix) as name:
            yield name
    else:
        yield tempfile.mkdtemp(prefix=prefix, dir=CONTROL_EVIDENCE_ROOT)


def configure_control_evidence(argv=None):
    """CLI-only explicit evidence path, never an inherited environment override."""
    global CONTROL_EVIDENCE_ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retained-evidence-root", type=Path)
    args = parser.parse_args(argv)
    root = args.retained_evidence_root
    if root is not None:
        if not root.is_absolute() or root.exists() or not root.parent.is_dir():
            parser.error("retained evidence root must be a fresh absolute child of an existing directory")
        root.mkdir()
        CONTROL_EVIDENCE_ROOT = root.resolve()
    return root is not None


class Clock:
    def __init__(self):
        self.tick = 0

    def __call__(self):
        return self.tick

    def sleep(self, ignored):
        self.tick += 1


class SyntheticRunner:
    def __init__(self, clock, plans=None, barrier=False):
        self.clock = clock
        self.plans = plans or {}
        self.barrier = barrier
        self.active = {}
        self.starts = []
        self.canceled = []
        self.maximum = 0

    def start(self, index, lane, module, lookup):
        if lane in (item["lane"] for item in self.active.values()):
            raise AssertionError("two active trees in one clone")
        key = (module, lookup)
        self.starts.append((index, lane, key, self.clock.tick))
        self.active[key] = {"lane": lane, "started": self.clock.tick}
        self.maximum = max(self.maximum, len(self.active))
        return key

    def poll(self, key):
        delay, unexpected, cleanup = self.plans.get(key, (1, False, True))
        if self.barrier and len(self.starts) < 2:
            return None
        if self.clock.tick - self.active[key]["started"] < delay:
            return None
        del self.active[key]
        return Observation(*key, "error" if unexpected else "nonreader",
                           unexpected=unexpected, cleanup_verified=cleanup, test_count=1)

    def cancel(self, key, reason):
        self.active.pop(key)
        self.canceled.append(key)
        return Observation(*key, "unread", unexpected=True, reason=reason)


class SchedulerControls(unittest.TestCase):
    def schedule(self, cap, plans=None, modules=("test_a", "test_b", "test_c"), barrier=False, deadline=50):
        clock = Clock()
        runner = SyntheticRunner(clock, plans, barrier)
        result = run_schedule(modules, cap, runner, deadline=deadline,
                              clock=clock, sleep=clock.sleep)
        return runner, result

    def test_barrier_overlap_cap_and_serial_lookups(self):
        runner, result = self.schedule(2, barrier=True)
        self.assertTrue(result.complete)
        self.assertEqual(runner.maximum, 2)
        self.assertEqual([row.lookup for row in result.observations], list(LOOKUPS) * 3)
        self.assertFalse(runner.active)

    def test_serial_same_lane_assignment_and_complete_population(self):
        serial, a = self.schedule(1)
        parallel, b = self.schedule(2)
        self.assertTrue(a.complete and b.complete)
        self.assertEqual(serial.maximum, 1)
        self.assertEqual(sorted((i, lane, key) for i, lane, key, _ in serial.starts),
                         sorted((i, lane, key) for i, lane, key, _ in parallel.starts))
        self.assertEqual([(row.module, row.lookup) for row in a.observations],
                         [(row.module, row.lookup) for row in b.observations])

    def test_only_two_unretired_modules_no_far_ahead_lane_queue(self):
        runner, result = self.schedule(2, {("test_a", LOOKUPS[0]): (8, False, True)})
        self.assertTrue(result.complete)
        c_start = next(tick for _, _, key, tick in runner.starts if key[0] == "test_c")
        self.assertGreaterEqual(c_start, 9)

    def test_reverse_failure_completion_preserves_serial_first_error(self):
        runner, result = self.schedule(2, {
            ("test_a", LOOKUPS[0]): (4, True, True),
            ("test_b", LOOKUPS[0]): (1, True, True),
        })
        self.assertFalse(result.complete)
        self.assertEqual(result.first_error, ("test_a", LOOKUPS[0]))
        self.assertTrue(result.first_error_resolved)
        self.assertEqual(len(runner.starts), 2)

    def test_earlier_second_lookup_needed_for_serial_first_error(self):
        runner, result = self.schedule(2, {
            ("test_a", LOOKUPS[0]): (3, False, True),
            ("test_a", LOOKUPS[1]): (1, True, True),
            ("test_b", LOOKUPS[0]): (1, True, True),
        })
        self.assertEqual(result.first_error, ("test_a", LOOKUPS[1]))
        self.assertEqual(len(runner.starts), 3)

    def test_earlier_hang_remains_unread_never_promotes_later_error(self):
        runner, result = self.schedule(2, {
            ("test_a", LOOKUPS[0]): (100, False, True),
            ("test_b", LOOKUPS[0]): (1, True, True),
        }, deadline=7)
        self.assertFalse(result.complete or result.first_error_resolved)
        self.assertIn(("test_a", LOOKUPS[0]), result.unread_pairs)
        self.assertIn(("test_a", LOOKUPS[0]), runner.canceled)

    def test_later_owned_tree_canceled_immediately(self):
        runner, result = self.schedule(2, {
            ("test_a", LOOKUPS[0]): (1, True, True),
            ("test_b", LOOKUPS[0]): (100, False, True),
        })
        self.assertIn(("test_b", LOOKUPS[0]), runner.canceled)
        self.assertFalse(result.complete)

    def test_cleanup_failure_never_success(self):
        _, result = self.schedule(2, {("test_a", LOOKUPS[0]): (1, False, False)})
        self.assertFalse(result.complete)
        self.assertEqual(result.stop_reason, "cleanup_unverified")

    def test_duplicate_missing_not_hidden_by_equal_count(self):
        _, result = self.schedule(2)
        changed = list(result.observations)
        changed[-1] = changed[0]
        accounting = account_pairs(("test_a", "test_b", "test_c"), changed)
        self.assertEqual(len(accounting["duplicate"]), 1)
        self.assertEqual(len(accounting["missing"]), 1)
        with self.assertRaisesRegex(ValueError, "pair_accounting"):
            audit_sets(("test_a", "test_b", "test_c"), set(), changed)

    def test_pins_unpinned_and_stale_from_actual_schedule(self):
        _, result = self.schedule(2)
        rows = list(result.observations)
        rows[0] = replace(rows[0], classification="reader")
        sets = audit_sets(("test_a", "test_b", "test_c"),
                          {("test_c", LOOKUPS[1])}, rows)
        self.assertEqual(sets["unpinned_readers"], [("test_a", LOOKUPS[0])])
        self.assertEqual(sets["stale_pins"], [("test_c", LOOKUPS[1])])


class CaptureControls(unittest.TestCase):
    def orphan_traceback(self):
        """Use the real traceback producer, not an idealized exception string."""
        stream = io.StringIO()
        try:
            raise ValueError("synthetic visible unrelated failure")
        except ValueError:
            traceback.print_exc(file=stream)
        return stream.getvalue()

    def test_visible_orphan_traceback_contaminates_valid_stock_refusal(self):
        orphan = self.orphan_traceback()
        refusal = self.stock_outcomes(["test_refusal"])
        for stdout, stderr in ((orphan, refusal), ("", orphan + refusal),
                               ("", refusal + orphan)):
            with self.subTest(stdout_orphan=bool(stdout), before=stderr.startswith(orphan)):
                row = self.capture(stdout, stderr, 1)
                self.assertEqual(row["classification"], "reader")
                self.assertTrue(row["unexpected"] and row["contaminated"])
                self.assertEqual(row.get("orphan_traceback_count"), 1)

    def test_visible_orphan_traceback_refuses_stock_success_but_ordinary_stdout_does_not(self):
        report = self.stock_outcomes(["test_skipped"])
        ordinary = self.capture("ordinary synthetic output without a traceback\n", report, 0)
        self.assertFalse(ordinary["unexpected"])
        orphan = self.capture(self.orphan_traceback(), report, 0)
        self.assertEqual(orphan["classification"], "nonreader")
        self.assertTrue(orphan["unexpected"])
        self.assertEqual(orphan.get("orphan_traceback_count"), 1)

    def stock_outcomes(self, names):
        class Synthetic(unittest.TestCase):
            @unittest.skip("synthetic skipped case")
            def test_skipped(self):
                self.fail("skip decorator should prevent execution")

            @unittest.expectedFailure
            def test_expected_failure(self):
                self.fail("synthetic expected failure")

            def test_refusal(self):
                self.fail("CODE_SET_DATABASE_OPEN_REFUSED:icd10_lookup")

        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=0).run(
            unittest.TestSuite(Synthetic(name) for name in names))
        self.assertEqual(result.wasSuccessful(), "test_refusal" not in names)
        return stream.getvalue()

    def test_stock_skipped_count_is_preserved(self):
        row = self.capture("", self.stock_outcomes(["test_skipped"]), 0)
        self.assertFalse(row["unexpected"])
        self.assertEqual(row.get("skipped"), 1)
        self.assertEqual(row.get("expected_failures"), 0)

    def test_stock_expected_failure_and_combined_counts_are_preserved(self):
        for names, skipped in ((["test_expected_failure"], 0),
                               (["test_skipped", "test_expected_failure"], 1)):
            with self.subTest(names=names):
                row = self.capture("", self.stock_outcomes(names), 0)
                self.assertFalse(row["unexpected"])
                self.assertEqual(row.get("skipped"), skipped)
                self.assertEqual(row.get("expected_failures"), 1)
        self.check_stock_failed_summary_retains_skips_and_expected_failures()

    def check_stock_failed_summary_retains_skips_and_expected_failures(self):
        row = self.capture("", self.stock_outcomes(["test_refusal", "test_skipped", "test_expected_failure"]), 1)
        self.assertEqual(row["classification"], "reader")
        self.assertFalse(row["unexpected"])
        self.assertEqual(row.get("skipped"), 1)
        self.assertEqual(row.get("expected_failures"), 1)

    WRAPPER_SUBJECT = "note-side ICD-10 database membership"

    def wrapper(self, mode="pure"):
        """Run the real stock producer with synthetic source-qualified identities."""
        lookup = "procedure_codes_lookup" if mode == "wrong_lookup" else "icd10_lookup"
        nested_name = "test_vitamin_b12_in_final_diagnosis_is_counted_but_not_bound"
        outer_name = "test_each_behavior_subject_names_a_passing_control"

        def nested_refusal(case):
            if mode == "chained_nested":
                try:
                    raise ValueError("synthetic unrelated nested failure")
                except ValueError:
                    raise AssertionError("CODE_SET_DATABASE_OPEN_REFUSED:" + lookup)
            raise AssertionError("CODE_SET_DATABASE_OPEN_REFUSED:" + lookup)

        def unrelated(case):
            raise ValueError("synthetic unrelated failure")

        nested_class = type("OtherCase" if mode == "wrong_nested" else "AgreementModes",
                            (unittest.TestCase,), {"__module__": "test_anchor_scan", nested_name: nested_refusal,
                                                 "test_unrelated": unrelated})

        def outer_wrapper(case):
            nested = [nested_class(nested_name)]
            if mode == "mixed_nested":
                nested.append(nested_class("test_unrelated"))
            if mode == "duplicate_tuple":
                nested.append(nested_class(nested_name))
            result = unittest.TestResult()
            unittest.TestSuite(nested).run(result)
            if mode in ("truncated_nested", "trailing_nested"):
                test, report = result.failures[0]
                report = report[:-8] if mode == "truncated_nested" else report + "unrecognized trailing detail\n"
                result.failures[0] = (test, report)
            subject = "unqualified subject" if mode == "wrong_subject" else self.WRAPPER_SUBJECT
            case.assertTrue(result.wasSuccessful(), f"{subject}: {result.errors + result.failures}")

        outer_class = type("OtherOuter" if mode == "wrong_outer" else "EveryBehaviorLimitHasALiveControl",
                           (unittest.TestCase,), {"__module__": "test_anchor_scan", outer_name: outer_wrapper,
                                                "test_unrelated": unrelated})
        cases = [outer_class(outer_name)]
        if mode == "mixed_outer":
            cases.append(outer_class("test_unrelated"))
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=0).run(unittest.TestSuite(cases))
        self.assertFalse(result.wasSuccessful())
        return stream.getvalue()

    def test_source_qualified_nested_refusal_wrapper_is_readable(self):
        row = self.capture("", self.wrapper(), 1, module="test_anchor_scan")
        self.assertEqual(row["classification"], "reader")
        self.assertFalse(row["unexpected"])

    def test_wrapped_refusal_from_wrong_invoked_module_is_contaminated(self):
        row = self.capture("", self.wrapper(), 1, module="test_specificity_scan")
        self.assertTrue(row["unexpected"])

    def test_chained_outer_exception_before_refusal_is_contaminated(self):
        report = ("FAIL: test_synthetic\n----------------------------------------------------------------------\n"
                  "Traceback (most recent call last):\nValueError: unrelated first error\n\n"
                  "During handling of the above exception, another exception occurred:\n\n"
                  "Traceback (most recent call last):\n"
                  "AssertionError: CODE_SET_DATABASE_OPEN_REFUSED:icd10_lookup\n\n"
                  "Ran 1 test in 0.001s\n\nFAILED (failures=1)\n")
        self.assertTrue(self.capture("", report, 1)["unexpected"])

    def test_nested_wrapper_mutants_are_contaminated(self):
        for mode in ("wrong_subject", "wrong_nested", "wrong_outer", "mixed_nested", "chained_nested",
                     "trailing_nested", "truncated_nested", "duplicate_tuple", "mixed_outer", "wrong_lookup"):
            with self.subTest(mode=mode):
                row = self.capture("CODE_SET_DATABASE_OPEN_REFUSED", self.wrapper(mode), 1, module="test_anchor_scan")
                self.assertTrue(row["unexpected"])

    def capture(self, stdout, stderr, code, *, module="test_capture"):
        with control_case(prefix="synthetic-capture-") as name:
            root = Path(name)
            class CaptureRunner:
                def start(self, index, lane, module, lookup):
                    return module, lookup

                def poll(self, handle):
                    module, lookup = handle
                    (root / "stdout").write_text(stdout.replace(LOOKUPS[0], lookup), encoding="utf-8")
                    (root / "stderr").write_text(stderr.replace(LOOKUPS[0], lookup), encoding="utf-8")
                    parsed = analyze_capture(root / "stdout", root / "stderr", code, lookup, module=module)
                    return Observation(module, lookup, parsed["classification"], parsed["unexpected"],
                                       test_count=parsed["test_count"], metadata=parsed)

                def cancel(self, handle, reason):
                    return Observation(*handle, "unread", unexpected=True, reason=reason)

            clock = Clock()
            result = run_schedule((module,), 2, CaptureRunner(), deadline=10,
                                  clock=clock, sleep=clock.sleep)
            row = result.observations[0].metadata
            self.assertEqual(result.complete, not row["unexpected"])
            if row["unexpected"]:
                self.assertEqual(result.first_error, (module, LOOKUPS[0]))
                self.assertIn((module, LOOKUPS[1]), result.unread_pairs)
            return row

    def frame(self, kind="AssertionError: CODE_SET_DATABASE_OPEN_REFUSED:icd10_lookup"):
        return "FAIL: test_synthetic\n----------------------------------------------------------------------\nTraceback (most recent call last):\n" + kind + "\n\n"

    def test_large_separate_output_and_marker_precedence(self):
        row = self.capture("safe synthetic line\n" * 100000,
                           self.frame() + "Ran 1 test in 0.001s\n\nFAILED (failures=1)\n", 1)
        self.assertEqual(row["classification"], "reader")
        self.assertFalse(row["unexpected"])
        self.assertGreater(row["output_bytes"], 1000000)

    def test_mixed_marker_plus_unrelated_error_is_contaminated_not_success(self):
        row = self.capture("", self.frame() + self.frame("ValueError: synthetic other failure")
                           + "Ran 2 tests in 0.001s\n\nFAILED (failures=2)\n", 1)
        self.assertEqual(row["classification"], "reader")
        self.assertTrue(row["unexpected"] and row["contaminated"])
        self.assertEqual(row["unrelated_failure_frames"], 1)

    def test_marker_without_readable_frame_is_unread(self):
        row = self.capture("CODE_SET_DATABASE_OPEN_REFUSED", "", 0)
        self.assertEqual(row["classification"], "reader")
        self.assertTrue(row["unexpected"])

    def test_error_without_marker_is_not_reader(self):
        row = self.capture("", self.frame("ValueError: synthetic")
                           + "Ran 1 test in 0.001s\n\nFAILED (errors=1)\n", 1)
        self.assertEqual(row["classification"], "error")
        self.assertTrue(row["unexpected"])


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    from console_codec import require_python_floor, use_utf8
    use_utf8()
    require_python_floor()
    retained_evidence = configure_control_evidence()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__)))
    print(json.dumps({"schema_version": 1, "kind": "scheduler-synthetic-controls",
                      "tests_run": result.testsRun, "failures": len(result.failures),
                      "errors": len(result.errors), "successful": result.wasSuccessful(),
                      "retained_evidence_requested": retained_evidence}, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
