"""Require every test in CI's ``test*.py`` population under ``tools/`` to re-run."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import grader_conformance
import run_grader


TOOLS = Path(__file__).resolve().parent


def _iter_test_cases(suite):
    for member in suite:
        if isinstance(member, unittest.TestSuite):
            yield from _iter_test_cases(member)
        else:
            yield member


def _describe_test_bindings(test):
    test_class = test.__class__
    found = []
    for module_name, module in tuple(sys.modules.items()):
        module_path = getattr(module, "__file__", None)
        if not module_path or not module_name.startswith("test"):
            continue
        if Path(module_path).resolve().parent != TOOLS:
            continue
        names = sorted(
            name for name, value in vars(module).items() if value is test_class
        )
        if names:
            found.append(f"{module_name} binds it as {', '.join(names)}")
    return "; ".join(found) or "no test-module binding was found"


class EveryDiscoveredTestIdReruns(unittest.TestCase):
    def test_every_discovered_test_id_reruns_the_same_test(self):
        discovery = unittest.TestLoader()
        discovered = tuple(
            _iter_test_cases(
                discovery.discover(start_dir=TOOLS, top_level_dir=TOOLS)
            )
        )
        self.assertEqual([], discovery.errors)
        denominator = len(discovered)

        for test in discovered:
            test_id = test.id()
            loaded = tuple(
                _iter_test_cases(unittest.TestLoader().loadTestsFromName(test_id))
            )
            same_test = (
                len(loaded) == 1
                and loaded[0].__class__ is test.__class__
                and loaded[0]._testMethodName == test._testMethodName
            )
            with self.subTest(test_id=test_id):
                self.assertTrue(
                    same_test,
                    f"{test_id} did not re-run from {denominator} discovered tests; "
                    f"{_describe_test_bindings(test)}",
                )


class EveryDeclaredLimitHasAnEvidenceDisposition(unittest.TestCase):
    DOUBLE_BINDING = (
        "whether every generated class a test module creates is bound where "
        "discovery can find it"
    )

    def test_every_limit_has_one_disposition_and_behavior_has_the_binding_row(self):
        for subject, _reason, disposition in grader_conformance.DECLARED_LIMITS:
            with self.subTest(subject=subject):
                self.assertIsInstance(disposition, run_grader.EvidenceDisposition)

        behavior = [
            subject
            for subject, _reason, disposition in grader_conformance.DECLARED_LIMITS
            if disposition is run_grader.EvidenceDisposition.BEHAVIOR
        ]
        self.assertEqual([self.DOUBLE_BINDING], behavior)


class ASecondBindingOfOneKindStillReplacesTheFirst(unittest.TestCase):
    def test_discovery_sees_only_the_second_class_and_its_ids_rerun(self):
        module_name = "test_double_grader_binding"
        prior_path = list(sys.path)
        sys.modules.pop(module_name, None)
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / f"{module_name}.py").write_text(
                    "from grader_conformance import EmptyPopulationInput, for_module\n"
                    "from pathlib import Path\n"
                    "import block_scan\n"
                    "import refusal_scan\n"
                    "def empty_population_input(root):\n"
                    "    empty, twin = root / 'empty', root / 'twin'\n"
                    "    empty.mkdir()\n"
                    "    twin.mkdir()\n"
                    "    (empty / 'note.md').write_text('# Synthetic note\\n', encoding='utf-8')\n"
                    "    (twin / 'note.md').write_text('```\\nGAPS              None\\n```\\n', encoding='utf-8')\n"
                    "    return EmptyPopulationInput((str(empty),), lambda scan: scan.notes_with_block, twin_argv=(str(twin),))\n"
                    "_first = []\n"
                    "GraderConformance = for_module(refusal_scan)\n"
                    "_first.append(GraderConformance)\n"
                    "GraderConformance = for_module(block_scan)\n",
                    encoding="utf-8",
                )
                loader = unittest.TestLoader()
                discovered = tuple(
                    _iter_test_cases(
                        loader.discover(start_dir=root, top_level_dir=root)
                    )
                )
                self.assertEqual([], loader.errors)
                synthetic = sys.modules[module_name]
                self.assertEqual(7, len(discovered))
                self.assertNotIn(
                    synthetic._first[0], {test.__class__ for test in discovered}
                )
                self.assertEqual(
                    {synthetic.GraderConformance},
                    {test.__class__ for test in discovered},
                )
                for test in discovered:
                    with self.subTest(test_id=test.id()):
                        loaded = tuple(
                            _iter_test_cases(
                                unittest.TestLoader().loadTestsFromName(test.id())
                            )
                        )
                        self.assertEqual(1, len(loaded))
                        self.assertIs(test.__class__, loaded[0].__class__)
                        self.assertEqual(
                            test._testMethodName, loaded[0]._testMethodName
                        )
        finally:
            sys.modules.pop(module_name, None)
            sys.path[:] = prior_path


if __name__ == "__main__":
    unittest.main()
