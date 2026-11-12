"""Observe rerun identity checks through their unittest results."""

import importlib.machinery
import sys
import types
import unittest
from unittest.mock import patch

import test_suite_ids


class LazyRerunDiagnostics(unittest.TestCase):
    def run_identity_check(self, mismatch=None, *, poison=False, discovery_errors=()):
        module_name = "test_rerun_diagnostic_fixture"
        fixture = types.ModuleType(module_name)
        fixture.__file__ = str(test_suite_ids.TOOLS / f"{module_name}.py")
        # A real module carries a spec; Python 3.15's traceback formatting reads the parent
        # module's resources while reporting a failed dotted import, and refuses a spec of None.
        fixture.__spec__ = importlib.machinery.ModuleSpec(module_name, None, origin=fixture.__file__)
        fixture.Subject = type("Subject", (unittest.TestCase,), {
            "__module__": module_name,
            "test_one": lambda self: None,
            "test_two": lambda self: None,
            "test_three": lambda self: None,
        })
        fixture.Other = type("Other", (fixture.Subject,), {"__module__": module_name})
        mismatches = mismatch if isinstance(mismatch, tuple) else (mismatch,)
        cases = []
        for kind, method in zip(mismatches, ("test_one", "test_two", "test_three")):
            actual_method = (
                "test_two" if method == "test_one" else "test_one"
            ) if kind == "method" else method
            case = (fixture.Other if kind == "class" else fixture.Subject)(actual_method)
            case.id = lambda method=method: f"{module_name}.Subject.{method}"
            cases.append(case)

        class PoisonModule(types.ModuleType):
            def __getattribute__(self, name):
                if name == "__file__":
                    raise RuntimeError("synthetic diagnostic fault")
                return super().__getattribute__(name)

        modules = {module_name: fixture}
        if poison:
            modules["test_rerun_diagnostic_poison"] = PoisonModule(
                "test_rerun_diagnostic_poison"
            )
        def discover(loader, *args, **kwargs):
            loader.errors.extend(discovery_errors)
            return unittest.TestSuite(cases)

        with patch.dict(sys.modules, modules), patch.object(
            unittest.TestLoader, "discover", autospec=True, side_effect=discover
        ):
            result = unittest.TestResult()
            test_suite_ids.EveryDiscoveredTestIdReruns(
                "test_every_discovered_test_id_reruns_the_same_test"
            ).run(result)
        return result

    def test_success_survives_incidental_diagnostic_exception(self):
        result = self.run_identity_check(poison=True)
        self.assertEqual(
            (1, True, [], []),
            (result.testsRun, result.wasSuccessful(), result.failures, result.errors),
        )

    def test_class_mismatch_keeps_literal_failure_text(self):
        result = self.run_identity_check("class")
        self.assertEqual((1, False, []),
                         (result.testsRun, result.wasSuccessful(), result.errors))
        self.assertEqual([
            "AssertionError: False is not true : test_rerun_diagnostic_fixture.Subject.test_one did not re-run from 1 discovered tests; test_rerun_diagnostic_fixture binds it as Other"
        ], [text.splitlines()[-1] for _, text in result.failures])

    def test_method_mismatch_keeps_literal_failure_text(self):
        result = self.run_identity_check("method")
        self.assertEqual((1, False, []),
                         (result.testsRun, result.wasSuccessful(), result.errors))
        self.assertEqual([
            "AssertionError: False is not true : test_rerun_diagnostic_fixture.Subject.test_one did not re-run from 1 discovered tests; test_rerun_diagnostic_fixture binds it as Subject"
        ], [text.splitlines()[-1] for _, text in result.failures])

    def test_diagnostic_exception_on_failure_remains_an_error(self):
        result = self.run_identity_check("class", poison=True)
        self.assertEqual((1, False, []),
                         (result.testsRun, result.wasSuccessful(), result.failures))
        self.assertEqual(["RuntimeError: synthetic diagnostic fault"],
                         [text.splitlines()[-1] for _, text in result.errors])

    def test_every_success_still_asserts_without_describing_bindings(self):
        with patch.object(
            test_suite_ids.EveryDiscoveredTestIdReruns,
            "assertTrue", autospec=True, side_effect=unittest.TestCase.assertTrue,
        ) as assertions, patch.object(
            test_suite_ids, "_describe_test_bindings",
            side_effect=RuntimeError("successful IDs must not need diagnostics"),
        ) as descriptions:
            result = self.run_identity_check((None, None, None))

        self.assertTrue(result.wasSuccessful(), (result.failures, result.errors))
        self.assertEqual([True, True, True],
                         [call.args[1] for call in assertions.call_args_list])
        descriptions.assert_not_called()

    def test_zero_and_multiple_reloads_keep_the_failure_description(self):
        for count in (0, 2):
            with self.subTest(reloaded=count), patch.object(
                unittest.TestLoader, "loadTestsFromName",
                return_value=unittest.TestSuite([
                    unittest.FunctionTestCase(lambda: None) for _ in range(count)
                ]),
            ) as reload:
                result = self.run_identity_check()

            reload.assert_called_once_with(
                "test_rerun_diagnostic_fixture.Subject.test_one"
            )
            self.assertEqual([], result.errors)
            self.assertEqual([
                "AssertionError: False is not true : test_rerun_diagnostic_fixture.Subject.test_one did not re-run from 1 discovered tests; test_rerun_diagnostic_fixture binds it as Subject"
            ], [text.splitlines()[-1] for _, text in result.failures])

    def test_multiple_failures_are_separate_and_later_ids_are_checked(self):
        original_reload = unittest.TestLoader.loadTestsFromName
        with patch.object(
            unittest.TestLoader, "loadTestsFromName",
            autospec=True, side_effect=original_reload,
        ) as reload, patch.object(
            test_suite_ids.EveryDiscoveredTestIdReruns,
            "assertTrue", autospec=True, side_effect=unittest.TestCase.assertTrue,
        ) as assertions:
            result = self.run_identity_check(("class", "method", None))

        self.assertEqual([], result.errors)
        self.assertEqual(2, len(result.failures))
        for method, (_, text) in zip(("test_one", "test_two"), result.failures):
            self.assertIn(f"Subject.{method} did not re-run from 3 discovered tests", text)
        self.assertEqual([
            f"test_rerun_diagnostic_fixture.Subject.{method}"
            for method in ("test_one", "test_two", "test_three")
        ], [call.args[1] for call in reload.call_args_list])
        self.assertEqual([False, False, True],
                         [call.args[1] for call in assertions.call_args_list])

    def test_discovery_errors_stop_before_any_id_is_reloaded(self):
        with patch.object(
            unittest.TestLoader, "loadTestsFromName",
            side_effect=RuntimeError("discovery failed before identity reload"),
        ) as reload:
            result = self.run_identity_check(
                discovery_errors=("synthetic discovery failure",)
            )

        reload.assert_not_called()
        self.assertEqual([], result.errors)
        self.assertEqual(1, len(result.failures))
        self.assertIn("synthetic discovery failure", result.failures[0][1])


if __name__ == "__main__":
    unittest.main()
