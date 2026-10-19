"""Recognized recursive walks use the shared reader or a named exception.

This AST check is a floor on rglob, recursive glob and os.walk
spellings. A walk assembled through indirection is invisible to it.
"""

import ast
import unittest
from pathlib import Path

from tree_walk import RECURSIVE_WALK_EXCEPTIONS


def recursive_walks(source: str) -> tuple[tuple[str, int], ...]:
    found = []
    tree = ast.parse(source)
    os_names = {alias.asname or alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names if alias.name == "os"}
    walk_names = {alias.asname or alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module == "os" for alias in node.names if alias.name == "walk"}

    class Reader(ast.NodeVisitor):
        function = "<module>"

        def visit_FunctionDef(self, node):
            previous = self.function
            self.function = node.name
            self.generic_visit(node)
            self.function = previous

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            strings = [arg.value for arg in node.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
            recursive_glob = name in {"glob", "iglob"} and (
                any("**" in value for value in strings)
                or any(keyword.arg == "recursive" and not (isinstance(keyword.value, ast.Constant) and keyword.value.value is False) for keyword in node.keywords)
            )
            os_walk = name == "walk" and (
                isinstance(node.func, ast.Name) and name in walk_names
                or (isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in os_names)
            )
            if name == "rglob" or os_walk or recursive_glob:
                found.append((self.function, node.lineno))
            self.generic_visit(node)

    Reader().visit(tree)
    return tuple(found)


class RecursiveWalkPopulation(unittest.TestCase):
    def test_every_recognized_walk_is_shared_or_named(self):
        tools = Path(__file__).resolve().parent
        unlisted = []
        used = set()
        for path in sorted(tools.glob("*.py")):
            if path.name.startswith("test") or path.name == "tree_walk.py":
                continue
            for function, line in recursive_walks(path.read_text(encoding="utf-8")):
                key = path.name, function
                if key in RECURSIVE_WALK_EXCEPTIONS:
                    used.add(key)
                else:
                    unlisted.append(f"{path.name}:{line} ({function})")
        self.assertEqual(unlisted, [])
        self.assertEqual(used, set(RECURSIVE_WALK_EXCEPTIONS), "remove obsolete exceptions")
        self.assertTrue(all(RECURSIVE_WALK_EXCEPTIONS.values()))

    def test_planted_raw_walks_are_detected(self):
        for code in (
            "root.rglob('*')", "root.glob('**/*.md')", "os.walk(root)",
            "glob.glob(pattern, recursive=True)",
        ):
            with self.subTest(code=code):
                self.assertEqual(recursive_walks("import os\ndef planted():\n    " + code), (("planted", 3),))

    def test_nonrecursive_glob_is_not_a_walk(self):
        self.assertEqual(recursive_walks("root.glob('*.py')"), ())
