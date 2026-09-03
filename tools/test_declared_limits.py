"""Every top-level ``DECLARED_LIMITS`` object is named by its module test.

ADR 0119 assertion 1. Candidacy is deliberately the literal top-level constant,
not a row or container shape. This is only a bind floor: naming the object does
not establish that the test proves every row or that the object is complete.
"""

from __future__ import annotations

import ast
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parent


def declares_limits(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return any(
        isinstance(node, (ast.Assign, ast.AnnAssign))
        and (
            any(
                isinstance(target, ast.Name) and target.id == "DECLARED_LIMITS"
                for target in node.targets
            )
            if isinstance(node, ast.Assign)
            else isinstance(node.target, ast.Name)
            and node.target.id == "DECLARED_LIMITS"
        )
        for node in tree.body
    )


def declarers(root: Path = TOOLS) -> set[str]:
    return {
        path.stem
        for path in root.glob("*.py")
        if declares_limits(path)
    }


def named_by_tests(root: Path = TOOLS) -> set[str]:
    named = set()
    population = declarers(root)
    for path in root.glob("test_*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        aliases = {
            alias.asname or alias.name: alias.name
            for node in tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        dynamic_specs = {}
        for node in tree.body:
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "spec_from_file_location"
                and node.value.args
                and isinstance(node.value.args[0], ast.Constant)
                and isinstance(node.value.args[0].value, str)
            ):
                dynamic_specs[node.targets[0].id] = node.value.args[0].value
        for node in tree.body:
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "module_from_spec"
                and len(node.value.args) == 1
                and isinstance(node.value.args[0], ast.Name)
                and node.value.args[0].id in dynamic_specs
            ):
                aliases[node.targets[0].id] = dynamic_specs[node.value.args[0].id]
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "DECLARED_LIMITS"
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
            ):
                named.add(aliases[node.value.id])
            elif isinstance(node, ast.ImportFrom) and any(
                alias.name == "DECLARED_LIMITS" for alias in node.names
            ):
                named.add(node.module or "")
            elif (
                path.stem == "test_glossary_collisions"
                and isinstance(node, ast.Name)
                and node.id == "DECLARED_LIMITS"
                and isinstance(node.ctx, ast.Load)
            ):
                named.add(path.stem)
    return named


class EveryDeclaredLimitsObjectIsNamedByItsTest(unittest.TestCase):
    def test_every_declarer_test_names_the_object(self):
        missing = sorted(declarers() - named_by_tests())

        self.assertEqual([], missing, "declarers whose test does not name DECLARED_LIMITS")

    def test_the_candidacy_derivation_is_live(self):
        population = declarers()

        self.assertIn("case_study_scan", population)
        self.assertIn("test_glossary_collisions", population)
        self.assertNotIn("differential_scan", population)

    def test_a_comment_does_not_name_the_object(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text(
                'DECLARED_LIMITS = ("outside",)\n',
                encoding="utf-8",
            )
            (root / "test_sample.py").write_text(
                "# sample.DECLARED_LIMITS\n",
                encoding="utf-8",
            )

            self.assertNotIn("sample", named_by_tests(root))

    def test_a_truthy_inert_assertion_does_not_name_the_object(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text(
                'DECLARED_LIMITS = ("outside",)\n',
                encoding="utf-8",
            )
            (root / "test_sample.py").write_text(
                "import unittest\n"
                "class Test(unittest.TestCase):\n"
                "    def test_pointer(self):\n"
                '        self.assertTrue("sample.DECLARED_LIMITS")\n',
                encoding="utf-8",
            )

            self.assertNotIn("sample", named_by_tests(root))


if __name__ == "__main__":
    unittest.main()
