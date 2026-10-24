"""Observe rerun identity checks through their unittest results."""

import sys
import types
import unittest
from unittest.mock import patch

import test_suite_ids


class LazyRerunDiagnostics(unittest.TestCase):
    def run_identity_check(self, mismatch=None, *, poison=False):
        module_name = "test_rerun_diagnostic_fixture"
        fixture = types.ModuleType(module_name)
        fixture.__file__ = str(test_suite_ids.TOOLS / f"{module_name}.py")
        fixture.Subject = type("Subject", (unittest.TestCase,), {
            "__module__": module_name,
            "test_one": lambda self: None,
            "test_two": lambda self: None,
        })
        fixture.Other = type("Other", (fixture.Subject,), {"__module__": module_name})
        case = (fixture.Other if mismatch == "class" else fixture.Subject)(
            "test_two" if mismatch == "method" else "test_one"
        )
        case.id = lambda: "test_rerun_diagnostic_fixture.Subject.test_one"

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
        with patch.dict(sys.modules, modules), patch.object(
            unittest.TestLoader, "discover", return_value=unittest.TestSuite([case])
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


if __name__ == "__main__":
    unittest.main()
