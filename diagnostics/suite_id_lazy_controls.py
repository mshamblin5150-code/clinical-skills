"""Behavior controls for issue #2013, not a timing or full-suite instrument.

Run unchanged before and after the isolated candidate edit:
    python -B <this-file> --repo <checkout>

The baseline should fail the two success-path diagnostic-call expectations.
All other expectations exercise preserved behavior of the real test method.
Only loader inputs and diagnostic fault injection are controlled. No discovered
test body, lock operation, real discovery, junction, or environment override is
needed. Normal target imports are retained, including their ordinary temporary
root setup. Import failure is a blocker, not something this harness bypasses.

This stdlib-only harness targets Python 3.10 syntax/APIs. Execution on Linux 3.12
does not establish Windows 3.14.4 compatibility or end-to-end CI speed savings.
"""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
import time
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import mock


MEASUREMENTS = []


def _never_execute_fixture_body(self):
    raise AssertionError("The ID control must not execute a discovered test body")


class _Fixtures:
    def __init__(self, subject):
        self.module = ModuleType("test_suite_id_lazy_fixture")
        self.module.__file__ = str(subject.TOOLS / "test_suite_id_lazy_fixture.py")
        methods = {
            "__module__": self.module.__name__,
            "test_first": _never_execute_fixture_body,
            "test_second": _never_execute_fixture_body,
        }
        self.alpha = type("Alpha", (unittest.TestCase,), methods)
        self.beta = type("Beta", (unittest.TestCase,), methods)
        # Identical class names, module, method, and printed ID must not disguise
        # a different class object. This is deliberately not bound in the module.
        self.alpha_twin = type("Alpha", (unittest.TestCase,), methods)
        self.module.Alpha = self.alpha
        self.module.AliasAlpha = self.alpha
        self.module.Beta = self.beta

    def binding_message(self, case):
        if type(case) is self.alpha_twin:
            return "no test-module binding was found"
        names = "AliasAlpha, Alpha" if type(case) is self.alpha else "Beta"
        return "{} binds it as {}".format(self.module.__name__, names)


class _ControlledLoaders:
    """One discovery loader, then a fresh loader for each expected test ID."""

    def __init__(self, discovered, reloads, errors):
        self.discovered = discovered
        self.reloads = reloads
        self.errors = errors
        self.instances = []
        self.discovery_calls = []
        self.reload_calls = []

    def __call__(self):
        position = len(self.instances)
        if position == 0:
            owner = self

            class DiscoveryLoader:
                errors = owner.errors

                def discover(self, **kwargs):
                    owner.discovery_calls.append(kwargs)
                    # Nested real suites exercise the production flattening.
                    return unittest.TestSuite(
                        [unittest.TestSuite(owner.discovered)]
                    )

            loader = DiscoveryLoader()
        else:
            index = position - 1
            if index >= len(self.reloads):
                raise AssertionError("Unexpected extra reload loader")
            owner = self

            class ReloadLoader:
                used = False

                def loadTestsFromName(self, test_id):
                    if self.used:
                        raise AssertionError("A reload loader was reused")
                    self.used = True
                    expected_id = owner.discovered[index].id()
                    if test_id != expected_id:
                        raise AssertionError(
                            "Wrong reload order/ID: {!r} != {!r}".format(
                                test_id, expected_id
                            )
                        )
                    owner.reload_calls.append(test_id)
                    return unittest.TestSuite(
                        [unittest.TestSuite(owner.reloads[index])]
                    )

            loader = ReloadLoader()
        self.instances.append(loader)
        return loader


class _ObservedResult(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.subtests = []

    def addSubTest(self, test, subtest, err):
        detail = None if err is None else (err[0], str(err[1]))
        self.subtests.append((subtest.params["test_id"], detail))
        super().addSubTest(test, subtest, err)


class LazyBindingControls(unittest.TestCase):
    subject = None  # Set only after an ordinary import from --repo/tools.

    def setUp(self):
        self.fixtures = _Fixtures(self.subject)

    def exercise(
        self, discovered, reloads, errors=(), helper_error=None, label=None,
        expected_failures=0, expected_errors=0, expected_helper_calls=0,
        expected_asserted_values=None,
    ):
        loaders = _ControlledLoaders(discovered, reloads, list(errors))
        case = self.subject.EveryDiscoveredTestIdReruns(
            "test_every_discovered_test_id_reruns_the_same_test"
        )
        result = _ObservedResult()
        real_helper = self.subject._describe_test_bindings
        helper_seconds = 0.0

        def observed_helper(test):
            nonlocal helper_seconds
            started = time.perf_counter()
            try:
                if helper_error is not None:
                    raise helper_error
                return real_helper(test)
            finally:
                helper_seconds += time.perf_counter() - started

        # These spies delegate rather than replacing the assertion or helper's
        # behavior. The real predicate, subTest, and TestCase.run remain intact.
        with mock.patch.dict(
            sys.modules, {self.fixtures.module.__name__: self.fixtures.module}
        ), mock.patch.object(
            self.subject.unittest, "TestLoader", loaders
        ), mock.patch.object(
            case, "assertTrue", wraps=case.assertTrue
        ) as assertions, mock.patch.object(
            self.subject,
            "_describe_test_bindings",
            wraps=observed_helper,
        ) as helper:
            started = time.perf_counter()
            case.run(result)
            subject_seconds = time.perf_counter() - started
        expected_reload_count = 0 if errors else len(discovered)
        if expected_asserted_values is None:
            expected_asserted_values = (
                [] if errors or helper_error is not None else [True] * len(discovered)
            )
        MEASUREMENTS.append({
            "control_id": self.id(),
            "case_label": label or self._testMethodName,
            "discovered_count": len(discovered),
            "loader_instances": len(loaders.instances),
            "expected_loader_instances": 1 + expected_reload_count,
            "discovery_calls": len(loaders.discovery_calls),
            "expected_discovery_calls": 1,
            "reload_calls": len(loaders.reload_calls),
            "expected_reload_calls": expected_reload_count,
            "reloaded_ids": loaders.reload_calls,
            "assert_true_calls": assertions.call_count,
            "expected_assert_true_calls": len(expected_asserted_values),
            "asserted_values": [call.args[0] for call in assertions.call_args_list],
            "expected_asserted_values": expected_asserted_values,
            "helper_calls": helper.call_count,
            "helper_ids": [call.args[0].id() for call in helper.call_args_list],
            "expected_helper_calls": expected_helper_calls,
            "subject_failures": len(result.failures),
            "expected_subject_failures": expected_failures,
            "subject_errors": len(result.errors),
            "expected_subject_errors": expected_errors,
            "subtest_outcomes": [
                {
                    "test_id": test_id,
                    "exception_type": None if detail is None else detail[0].__name__,
                    "message": None if detail is None else detail[1],
                }
                for test_id, detail in result.subtests
            ],
            "subject_seconds": subject_seconds,
            "helper_seconds": helper_seconds,
        })
        self.assertEqual(1, result.testsRun)
        self.assertEqual([], result.skipped)
        self.assertEqual([], result.expectedFailures)
        self.assertEqual([], result.unexpectedSuccesses)
        self.assertEqual(
            [{"start_dir": self.subject.TOOLS, "top_level_dir": self.subject.TOOLS}],
            loaders.discovery_calls,
        )
        expected_ids = [] if errors else [test.id() for test in discovered]
        self.assertEqual(expected_ids, loaders.reload_calls)
        self.assertEqual(1 + len(expected_ids), len(loaders.instances))
        self.assertEqual(
            len(loaders.instances), len({id(loader) for loader in loaders.instances})
        )
        return SimpleNamespace(result=result, assertions=assertions, helper=helper)

    def assert_outcomes(self, run, discovered, successful):
        expected = []
        for case, success in zip(discovered, successful):
            detail = None
            if not success:
                detail = (
                    AssertionError,
                    "False is not true : {} did not re-run from {} discovered "
                    "tests; {}".format(
                        case.id(), len(discovered), self.fixtures.binding_message(case)
                    ),
                )
            expected.append((case.id(), detail))
        self.assertEqual(len(discovered), len(successful))
        self.assertEqual(expected, run.result.subtests)
        self.assertEqual(successful.count(False), len(run.result.failures))
        self.assertEqual([], run.result.errors)
        self.assertEqual(len(discovered), run.assertions.call_count)
        self.assertEqual(
            successful, [call.args[0] for call in run.assertions.call_args_list]
        )

    def test_successful_ids_reload_and_assert_without_diagnostics(self):
        f = self.fixtures
        discovered = [f.alpha("test_first"), f.alpha("test_second"), f.beta("test_first")]
        # New objects, not the original instances, satisfy class+method identity.
        reloads = [[type(case)(case._testMethodName)] for case in discovered]
        run = self.exercise(discovered, reloads)
        self.assert_outcomes(run, discovered, [True, True, True])
        run.helper.assert_not_called()

    def test_empty_population_is_successful_without_diagnostics(self):
        run = self.exercise([], [])
        self.assert_outcomes(run, [], [])
        run.helper.assert_not_called()

    def test_each_mismatch_keeps_exact_failure_diagnostic(self):
        f = self.fixtures
        discovered = [f.alpha("test_first")]
        cases = [
            ("zero reloads", []),
            ("multiple reloads", [f.alpha("test_first"), f.alpha("test_first")]),
            ("wrong class object with identical ID", [f.alpha_twin("test_first")]),
            ("wrong method", [f.alpha("test_second")]),
        ]
        for label, loaded in cases:
            with self.subTest(control=label):
                run = self.exercise(
                    discovered, [loaded], label=label,
                    expected_failures=1, expected_helper_calls=1,
                    expected_asserted_values=[False],
                )
                self.assert_outcomes(run, discovered, [False])
                run.helper.assert_called_once_with(discovered[0])

        with self.subTest(control="no test-module binding"):
            unbound = f.alpha_twin("test_first")
            run = self.exercise(
                [unbound], [[]], label="no test-module binding",
                expected_failures=1, expected_helper_calls=1,
                expected_asserted_values=[False],
            )
            self.assert_outcomes(run, [unbound], [False])
            run.helper.assert_called_once_with(unbound)

    def test_multiple_failures_continue_through_later_success_and_failure(self):
        f = self.fixtures
        discovered = [
            f.alpha("test_first"), f.alpha("test_second"),
            f.beta("test_first"), f.beta("test_second"),
        ]
        reloads = [
            [], [f.alpha("test_second")], [f.alpha("test_first")],
            [f.beta("test_second"), f.beta("test_second")],
        ]
        run = self.exercise(
            discovered, reloads, expected_failures=3, expected_helper_calls=3,
            expected_asserted_values=[False, True, False, False],
        )
        self.assert_outcomes(run, discovered, [False, True, False, False])
        self.assertEqual(
            [mock.call(discovered[index]) for index in (0, 2, 3)],
            run.helper.call_args_list,
        )

    def test_discovery_errors_stop_before_any_reload_or_diagnostic(self):
        discovered = [self.fixtures.alpha("test_first")]
        run = self.exercise(
            discovered, [[]], errors=["synthetic discovery failure"],
            expected_failures=1,
        )
        self.assertEqual(1, len(run.result.failures))
        self.assertIn("synthetic discovery failure", run.result.failures[0][1])
        self.assertEqual([], run.result.errors)
        self.assertEqual([], run.result.subtests)
        run.assertions.assert_not_called()
        run.helper.assert_not_called()

    def test_helper_error_on_failed_check_remains_visible(self):
        discovered = [self.fixtures.alpha("test_first")]
        run = self.exercise(
            discovered, [[]], helper_error=RuntimeError("synthetic binding failure"),
            expected_errors=1, expected_helper_calls=1,
        )
        self.assertEqual([], run.result.failures)
        self.assertEqual(1, len(run.result.errors))
        self.assertEqual(
            [(discovered[0].id(), (RuntimeError, "synthetic binding failure"))],
            run.result.subtests,
        )
        run.helper.assert_called_once_with(discovered[0])
        run.assertions.assert_not_called()  # Message evaluation raises first.


def main():
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    args = parser.parse_args()
    tools = args.repo.resolve() / "tools"
    # No bytecode artifacts, dependency substitutions, or lock-root overrides.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(tools))
    try:
        subject = importlib.import_module("test_suite_ids")
    finally:
        sys.path.pop(0)
    if Path(subject.__file__).resolve() != tools / "test_suite_ids.py":
        raise RuntimeError("Imported test_suite_ids from a different checkout")
    import_seconds = time.perf_counter() - started
    LazyBindingControls.subject = subject
    MEASUREMENTS.clear()
    cases = list(unittest.defaultTestLoader.loadTestsFromTestCase(LazyBindingControls))
    control_started = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(cases))
    control_seconds = time.perf_counter() - control_started
    baseline_red_methods = {
        "test_successful_ids_reload_and_assert_without_diagnostics",
        "test_multiple_failures_continue_through_later_success_and_failure",
    }
    outcomes = []
    for case in cases:
        def belongs_to_case(event):
            test, _traceback = event
            return test is case or getattr(test, "test_case", None) is case

        failures = [
            {"test_id": test.id(), "traceback": trace}
            for test, trace in result.failures if belongs_to_case((test, trace))
        ]
        errors = [
            {"test_id": test.id(), "traceback": trace}
            for test, trace in result.errors if belongs_to_case((test, trace))
        ]
        outcomes.append({
            "test_id": case.id(),
            "outcome": "error" if errors else "failure" if failures else "pass",
            "expected_baseline_failure": case._testMethodName in baseline_red_methods,
            "failures": failures,
            "errors": errors,
            "measurements": [row for row in MEASUREMENTS if row["control_id"] == case.id()],
        })
    print(json.dumps({
        "schema_version": 1,
        "scope": "Synthetic behavior controls only; not full discovery or CI speed evidence",
        "repo": str(args.repo.resolve()),
        "target_module": str(Path(subject.__file__).resolve()),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "tests_run": result.testsRun,
        "failure_count": len(result.failures),
        "error_count": len(result.errors),
        "successful": result.wasSuccessful(),
        "expected_baseline_failure_ids": [
            case.id() for case in cases if case._testMethodName in baseline_red_methods
        ],
        "timing_note": "Instrumented synthetic control timings, not CI performance estimates",
        "import_seconds": import_seconds,
        "control_seconds": control_seconds,
        "harness_seconds": time.perf_counter() - started,
        "control_outcomes": outcomes,
    }, indent=2, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
