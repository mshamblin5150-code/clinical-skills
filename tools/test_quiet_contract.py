"""The suppressor population and each command's declared survivor set."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest


TOOLS = Path(__file__).resolve().parent
EXPECTED = {
    "apa7_coverage",
    "closing_keyword_scan",
    "guidelines_extract",
    "skills_mirror",
    "spelling_scan",
    "threshold_sheet",
    "uptodate_sheet",
}


def module_tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def declares_quiet(tree: ast.AST) -> bool:
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_argument"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "--quiet"
        for node in ast.walk(tree)
    )


def declared_survivors(tree: ast.Module) -> tuple[str, ...] | None:
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "UNSUPPRESSED_LINES"
            for target in statement.targets
        ):
            continue
        value = ast.literal_eval(statement.value)
        return tuple(value)
    return None


def survivor_uses(tree: ast.AST) -> tuple[str, ...]:
    return tuple(
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_quiet_keeps"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    )


class QuietContract(unittest.TestCase):
    def test_the_suppressor_population_is_the_seven_commands(self):
        population = {
            path.stem
            for path in TOOLS.glob("*.py")
            if not path.name.startswith("test_") and declares_quiet(module_tree(path))
        }

        self.assertEqual(population, EXPECTED)

    def test_each_non_line_command_binds_its_survivors_both_ways(self):
        for name in sorted(EXPECTED - {"threshold_sheet"}):
            with self.subTest(module=name):
                tree = module_tree(TOOLS / f"{name}.py")
                declared = declared_survivors(tree)
                used = survivor_uses(tree)

                self.assertIsNotNone(declared)
                self.assertTrue(declared)
                self.assertEqual(set(declared or ()), set(used))
                self.assertEqual(len(declared or ()), len(set(declared or ())))


if __name__ == "__main__":
    unittest.main()
