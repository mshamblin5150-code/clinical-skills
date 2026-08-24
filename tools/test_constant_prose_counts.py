"""Refuse one underived-count shape in non-test tool-module uppercase constants.

This reads only ``the|those|these`` followed by a cardinal and a word ending in
``s``. Other grammatical shapes remain outside the check. In particular, a count
in a class name is reachable by no string walk. Docstrings are deliberately not
graded; docs/adr/0020 records the measured reason for that boundary.
"""

import ast
from pathlib import Path
import re
import subprocess
import unittest


REPO_ROOT = Path(__file__).resolve().parent.parent
CARDINAL = (
    r"(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
    r"thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|\d+)"
)
DEFINITE_COUNT = re.compile(
    rf"\b(?:the|those|these)\s+{CARDINAL}\s+[A-Za-z]+s\b",
    re.IGNORECASE,
)

DECLARED_DEFINITE_COUNTS = {
    (
        "tools/docx_write.py",
        "NOT_APPLIED",
        "the six is",
    ): (
        "The six title-page elements are enumerated in the same sentence; "
        "the match is the predicate reading 'is' as a plural noun."
    ),
}


def _tracked_tool_modules(root: Path) -> list[str]:
    """Return tracked non-test Python modules directly under ``tools/``.

    A clean repository walk means no tracked module fails this check. Untracked
    or unstaged modules remain invisible until they enter the index.
    """

    result = subprocess.run(
        ["git", "ls-files", "--cached", "--", "tools/*.py"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return [
        relative
        for relative in result.stdout.splitlines()
        if not Path(relative).name.startswith("test_")
    ]


def definite_counts(source: str) -> set[tuple[str, str]]:
    """Return constant names and matched count phrases from one module source."""

    found: set[tuple[str, str]] = set()
    for statement in ast.parse(source).body:
        if isinstance(statement, ast.Assign):
            targets = statement.targets
            value = statement.value
        elif isinstance(statement, ast.AnnAssign):
            targets = [statement.target]
            value = statement.value
        else:
            continue

        if value is None:
            continue

        pending = [(target, value) for target in targets]
        while pending:
            target, assigned = pending.pop()
            if isinstance(target, ast.Name):
                if not target.id.isupper():
                    continue
                for node in ast.walk(assigned):
                    if not isinstance(node, ast.Constant) or not isinstance(
                        node.value, str
                    ):
                        continue
                    for match in DEFINITE_COUNT.finditer(node.value):
                        found.add((target.id, match.group(0).lower()))
                continue

            if isinstance(target, ast.Starred):
                pending.append((target.value, assigned))
                continue

            if isinstance(target, (ast.List, ast.Tuple)):
                if isinstance(assigned, (ast.List, ast.Tuple)):
                    starred = [
                        index
                        for index, element in enumerate(target.elts)
                        if isinstance(element, ast.Starred)
                    ]
                    if len(starred) == 1 and len(assigned.elts) >= len(target.elts) - 1:
                        index = starred[0]
                        tail = len(target.elts) - index - 1
                        pending.extend(zip(target.elts[:index], assigned.elts[:index]))
                        if tail:
                            pending.extend(
                                zip(target.elts[index + 1 :], assigned.elts[-tail:])
                            )
                        stop = len(assigned.elts) - tail if tail else len(assigned.elts)
                        pending.append(
                            (
                                target.elts[index],
                                ast.Tuple(
                                    elts=assigned.elts[index:stop], ctx=ast.Load()
                                ),
                            )
                        )
                        continue
                    if len(target.elts) == len(assigned.elts):
                        pending.extend(zip(target.elts, assigned.elts))
                        continue
                pending.extend((element, assigned) for element in target.elts)
    return found


def repository_survivors(root: Path) -> set[tuple[str, str, str]]:
    """Walk every module-level uppercase constant in tracked non-test tools."""

    found: set[tuple[str, str, str]] = set()
    for relative in _tracked_tool_modules(root):
        source = (root / relative).read_text(encoding="utf-8")
        found.update(
            (relative, constant, phrase)
            for constant, phrase in definite_counts(source)
        )
    return found


class DefiniteCountPredicateHasAPositiveControl(unittest.TestCase):
    def test_a_module_level_constant_with_the_shape_is_found(self):
        source = 'A_LIMIT = "These three rows are a planted control."\n'
        self.assertEqual({("A_LIMIT", "these three rows")}, definite_counts(source))

    def test_a_destructured_module_level_constant_is_found(self):
        source = 'FIRST, SECOND = ("plain", "The two rows are counted.")\n'
        self.assertEqual({("SECOND", "the two rows")}, definite_counts(source))

    def test_a_starred_module_level_constant_is_found(self):
        source = (
            'FIRST, *REST = ("plain", "These two rows are counted.", "plain")\n'
        )
        self.assertEqual({("REST", "these two rows")}, definite_counts(source))

    def test_docstrings_and_class_names_are_outside_the_string_walk(self):
        source = '''"""The three rows are only a module docstring."""\n\nclass TheThreeRows:\n    """Those four paths are only a class docstring."""\n'''
        self.assertEqual(set(), definite_counts(source))


class DefiniteCountsInConstantsAreDeclared(unittest.TestCase):
    def test_every_survivor_is_exactly_declared_and_reasoned(self):
        found = repository_survivors(REPO_ROOT)
        self.assertEqual(set(DECLARED_DEFINITE_COUNTS), found)
        for reason in DECLARED_DEFINITE_COUNTS.values():
            self.assertTrue(reason.strip())


if __name__ == "__main__":
    unittest.main()
