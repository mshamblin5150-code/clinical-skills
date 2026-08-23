"""Contract checks for issue #412's prose assertion helper."""

import ast
import subprocess
from pathlib import Path
import unittest

from prose_bind import GLUE, ProseBind


REPO_ROOT = Path(__file__).resolve().parent.parent
RESOLVED_READ_FLOOR = 20
CONVERTED_PROSE_BINDS = {
    ("tools/test_artifact_provenance.py", "unstamped extracted corpus and warn"),
    ("tools/test_artifact_provenance.py", "unstamped index and warn"),
    ("tools/test_discussion_post_skill.py", "discussion board"),
    ("tools/test_guideline_sheets.py", "and for the same reason: no guidelines"),
    ("tools/test_name_index.py", "no generator for the index is committed"),
    ("tools/test_research_ledger.py", "five years the outside limit"),
    ("tools/test_research_ledger.py", "written as historical or dropped"),
    ("tools/test_skill_agreement.py", "under GAPS"),
    (
        "tools/test_skill_agreement.py",
        "until it lands this example is the only place the distinction is written down",
    ),
    ("tools/test_skill_agreement.py", "on the branch the user named"),
    ("tools/test_skill_agreement.py", "The rules live in the reference"),
    (
        "tools/test_skill_agreement.py",
        "**declared rule** in ``reference/medatrax-fields.md``",
    ),
    ("tools/test_skill_agreement.py", "all of it is currently written into"),
    ("tools/test_skill_agreement.py", "Ask for 5 at minimum"),
    ("tools/test_skill_agreement.py", "isvery commonand"),
    ("tools/test_specificity_scan.py", "SPECIFICITY: <complete | needs:"),
}
DECLARED_PROSE_BIND_EXCEPTIONS = {
    (
        "tools/test_discussion_post_skill.py",
        "<course>-<module>-<date>",
    ): "angle brackets are run-key syntax, not prose emphasis",
}


SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)


def _operand_key(node: ast.expr) -> tuple[str, str] | None:
    if isinstance(node, ast.Name):
        return ("name", node.id)
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in {"self", "cls"}
    ):
        return ("class-attribute", node.attr)
    return None


def _thin_read_helpers(tree: ast.Module) -> set[str]:
    """Return local helpers whose only return delegates to ``Path.read_text``."""

    found: set[str] = set()
    for node in tree.body:
        if (
            not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            or not node.args.args
        ):
            continue
        parameter = node.args.args[0].arg
        returns = [child for child in ast.walk(node) if isinstance(child, ast.Return)]
        if returns and all(
            isinstance(item.value, ast.Call)
            and isinstance(item.value.func, ast.Attribute)
            and item.value.func.attr == "read_text"
            and isinstance(item.value.func.value, ast.Name)
            and item.value.func.value.id == parameter
            for item in returns
        ):
            found.add(node.name)
    return found


def _module_repository_paths(
    tree: ast.Module,
    module_path: Path,
) -> dict[str, set[Path]]:
    """Evaluate module path constants rooted in this module's ``__file__``."""

    found: dict[str, set[Path]] = {}

    def path_values(value: ast.AST) -> set[Path]:
        if isinstance(value, ast.Name):
            return found.get(value.id, set())
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "Path"
            and len(value.args) == 1
            and isinstance(value.args[0], ast.Name)
            and value.args[0].id == "__file__"
        ):
            return {module_path}
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and value.func.attr == "resolve"
        ):
            return {path.resolve() for path in path_values(value.func.value)}
        if isinstance(value, ast.Attribute) and value.attr == "parent":
            return {path.parent for path in path_values(value.value)}
        if (
            isinstance(value, ast.BinOp)
            and isinstance(value.op, ast.Div)
            and isinstance(value.right, ast.Constant)
            and isinstance(value.right.value, str)
        ):
            return {path / value.right.value for path in path_values(value.left)}
        return set()

    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        values = path_values(node.value)
        for target in _assignment_targets(node):
            if not isinstance(target, ast.Name):
                continue
            if values:
                found[target.id] = values
            else:
                found.pop(target.id, None)
    return found


def _path_values(
    node: ast.AST,
    repository_paths: dict[str, set[Path]],
) -> set[Path]:
    if isinstance(node, ast.Name):
        return repository_paths.get(node.id, set())
    if (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Div)
        and isinstance(node.right, ast.Constant)
        and isinstance(node.right.value, str)
    ):
        return {
            path / node.right.value
            for path in _path_values(node.left, repository_paths)
        }
    return set()


def _is_tracked_path(
    node: ast.AST,
    repository_paths: dict[str, set[Path]],
    tracked_paths: set[Path],
    parents: dict[ast.AST, ast.AST],
) -> bool:
    values = {path.resolve() for path in _path_values(node, repository_paths)}
    if values:
        return values <= tracked_paths
    if not isinstance(node, ast.Name):
        return False
    child: ast.AST = node
    while child in parents:
        child = parents[child]
        if not isinstance(child, (ast.For, ast.AsyncFor)):
            continue
        if not isinstance(child.target, ast.Name) or child.target.id != node.id:
            continue
        iterable = child.iter
        if (
            isinstance(iterable, ast.Call)
            and isinstance(iterable.func, ast.Name)
            and iterable.func.id == "sorted"
            and iterable.args
        ):
            iterable = iterable.args[0]
        if (
            isinstance(iterable, ast.Call)
            and isinstance(iterable.func, ast.Attribute)
            and iterable.func.attr == "glob"
            and iterable.args
            and isinstance(iterable.args[0], ast.Constant)
            and iterable.args[0].value in {"*.md", "*.py"}
        ):
            roots = _path_values(iterable.func.value, repository_paths)
            matches = {
                match.resolve()
                for root in roots
                for match in root.glob(iterable.args[0].value)
            }
            return bool(matches) and matches <= tracked_paths
        if isinstance(iterable, (ast.Tuple, ast.List)) and all(
            _is_tracked_path(item, repository_paths, tracked_paths, parents)
            for item in iterable.elts
        ):
            return True
    return False


def _is_read_call(
    node: ast.AST,
    helpers: set[str],
    repository_paths: dict[str, set[Path]],
    tracked_paths: set[Path],
    parents: dict[ast.AST, ast.AST],
) -> bool:
    return isinstance(node, ast.Call) and (
        (
            isinstance(node.func, ast.Name)
            and node.func.id in helpers
            and bool(node.args)
            and _is_tracked_path(
                node.args[0], repository_paths, tracked_paths, parents
            )
        )
        or (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "read_text"
            and _is_tracked_path(
                node.func.value, repository_paths, tracked_paths, parents
            )
        )
    )


def _is_read_expression(
    node: ast.AST,
    helpers: set[str],
    repository_paths: dict[str, set[Path]],
    tracked_paths: set[Path],
    parents: dict[ast.AST, ast.AST],
) -> bool:
    """Return whether an assignment derives directly from a tracked-file read.

    String slicing and iteration preserve that relation. An arbitrary wrapper
    does not: notably, ``squashed(read(path))`` is already normalized and must
    not make a differently scoped raw assertion look like a prose bind.
    """

    if _is_read_call(node, helpers, repository_paths, tracked_paths, parents):
        return True
    if isinstance(node, ast.Subscript):
        return _is_read_expression(
            node.value, helpers, repository_paths, tracked_paths, parents
        )
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            return _is_read_expression(
                node.func.value, helpers, repository_paths, tracked_paths, parents
            )
        if isinstance(node.func, ast.Name) and node.func.id == "next":
            return any(
                _is_read_expression(
                    arg, helpers, repository_paths, tracked_paths, parents
                )
                for arg in node.args
            )
        return False
    if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
        return _is_read_expression(
            node.elt, helpers, repository_paths, tracked_paths, parents
        ) or any(
            _is_read_expression(
                generator.iter, helpers, repository_paths, tracked_paths, parents
            )
            for generator in node.generators
        )
    return False


def _assignment_targets(node: ast.Assign | ast.AnnAssign) -> list[ast.expr]:
    return node.targets if isinstance(node, ast.Assign) else [node.target]


def _nearest_scope(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> ast.AST:
    while node in parents:
        node = parents[node]
        if isinstance(node, SCOPES):
            return node
    raise AssertionError("an assignment parsed outside a module")


def _nearest_class(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> ast.ClassDef | None:
    while node in parents:
        node = parents[node]
        if isinstance(node, ast.ClassDef):
            return node
    return None


def _assignments_in_scope(
    scope: ast.AST,
    key: tuple[str, str],
    parents: dict[ast.AST, ast.AST],
) -> list[ast.expr]:
    found: list[ast.expr] = []
    for node in ast.walk(scope):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        if not any(_operand_key(target) == key for target in _assignment_targets(node)):
            continue
        owner = _nearest_scope(node, parents)
        if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)) and owner is scope:
            found.append(node.value)
        elif isinstance(scope, ast.ClassDef):
            if key[0] == "class-attribute" and _nearest_class(node, parents) is scope:
                found.append(node.value)
            elif owner is scope:
                found.append(node.value)
        elif isinstance(scope, ast.Module) and owner is scope:
            found.append(node.value)
    return found


def _scope_chain(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> list[ast.AST]:
    found: list[ast.AST] = []
    while node in parents:
        node = parents[node]
        if isinstance(node, SCOPES):
            found.append(node)
    return found


def _resolves_to_read(
    haystack: ast.expr,
    assertion: ast.Call,
    helpers: set[str],
    repository_paths: dict[str, set[Path]],
    tracked_paths: set[Path],
    parents: dict[ast.AST, ast.AST],
) -> bool:
    if _is_read_call(
        haystack, helpers, repository_paths, tracked_paths, parents
    ):
        return True
    key = _operand_key(haystack)
    if key is None:
        return False
    for scope in _scope_chain(assertion, parents):
        assignments = _assignments_in_scope(scope, key, parents)
        if assignments:
            return any(
                _is_read_expression(
                    value, helpers, repository_paths, tracked_paths, parents
                )
                for value in assignments
            )
    return False


def raw_prose_assert_not_in(
    source: str,
    converted_needles: set[str] | None = None,
    *,
    module_path: Path,
    tracked_paths: set[Path],
) -> tuple[set[str], int]:
    """Return transform-relevant raw needles and the resolved-read population.

    ``assertNotIn`` is the silent direction: a hard wrap can make it pass.
    Formatting drift makes ``assertIn`` fail loudly at its own site, so positive
    assertions are deliberately outside this walk.

    The positive resolver accepts a direct tracked-file read or one assignment
    hop, searching function, class, then module scope; the first scope with an
    assignment wins, and any read assignment in that scope is enough. At ticket
    #474's 2026-08-23 measurement on ``d3e39e6``, that reached 20 of 233 constant
    raw negative assertions. The other 213 passed because resolving calls,
    outer-scope assignments, attributes, subscripts, and comprehensions would
    require wider data-flow analysis; the repository test pins the reached
    population as a floor so the resolver cannot quietly lose ground.
    """

    tree = ast.parse(source)
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    helpers = _thin_read_helpers(tree)
    repository_paths = _module_repository_paths(tree, module_path)
    found: set[str] = set()
    resolved_reads = 0
    converted_needles = converted_needles or set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in {"assertNotIn", "assertProseNotIn"} or len(node.args) < 2:
            continue
        needle, haystack = node.args[:2]
        if not (
            isinstance(needle, ast.Constant)
            and isinstance(needle.value, str)
            and _resolves_to_read(
                haystack,
                node,
                helpers,
                repository_paths,
                tracked_paths,
                parents,
            )
        ):
            continue
        if node.func.attr == "assertNotIn" or needle.value in converted_needles:
            resolved_reads += 1
        if node.func.attr == "assertNotIn" and (
            any(character.isspace() for character in needle.value)
            or GLUE.search(needle.value)
        ):
            found.add(needle.value)
    return found, resolved_reads


def _tracked(root: Path, pathspec: str) -> list[str]:
    """Return tracked paths matching ``pathspec`` from the index.

    A clean walk means no tracked test module fails this check. Untracked or
    unstaged modules remain invisible until they enter the index.
    """

    result = subprocess.run(
        ["git", "ls-files", "--cached", "--", pathspec],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.splitlines()


def repository_survivors(root: Path) -> tuple[set[tuple[str, str]], int]:
    """Walk transform-relevant raw prose binds in tracked test modules."""

    found: set[tuple[str, str]] = set()
    resolved_reads = 0
    tracked_paths = {
        (root / relative).resolve()
        for relative in _tracked(root, ".")
    }
    for relative in _tracked(root, "tools/test_*.py"):
        module_path = (root / relative).resolve()
        source = module_path.read_text(encoding="utf-8")
        converted = {
            needle
            for path, needle in CONVERTED_PROSE_BINDS
            if path == relative
        }
        needles, module_resolved_reads = raw_prose_assert_not_in(
            source,
            converted,
            module_path=module_path,
            tracked_paths=tracked_paths,
        )
        found.update((relative, needle) for needle in needles)
        resolved_reads += module_resolved_reads
    return found, resolved_reads


class ProseAssertionsNormalizeBothSides(ProseBind, unittest.TestCase):
    def test_assert_prose_in_reads_across_hard_wraps_and_literal_glue(self):
        self.assertProseIn(
            'a phrase split across two adjacent string literals',
            'a phrase split across two adjacent "string"\n"literals"',
        )

    def test_assert_prose_not_in_fails_when_only_formatting_differs(self):
        with self.assertRaises(AssertionError):
            self.assertProseNotIn(
                "a retired clinician ruling",
                "a retired clinician\n'ruling'",
            )

    def test_the_needle_is_normalized_too(self):
        self.assertProseIn(
            "the needle is\n**hard wrapped**",
            "the needle is hard wrapped",
        )

    def test_a_prose_line_population_is_one_haystack(self):
        with self.assertRaises(AssertionError):
            self.assertProseNotIn(
                "a retired clinician ruling",
                ["a retired clinician", "ruling"],
            )


class TheSilentDirectionHasARefusingWalk(unittest.TestCase):
    MODULE_PATH = (REPO_ROOT / "tools" / "synthetic_contract.py").resolve()

    def walk(
        self,
        source: str,
        *tracked_names: str,
        converted_needles: set[str] | None = None,
    ) -> tuple[set[str], int]:
        tracked_paths = {
            (self.MODULE_PATH.parent / name).resolve()
            for name in tracked_names
        }
        return raw_prose_assert_not_in(
            source,
            converted_needles,
            module_path=self.MODULE_PATH,
            tracked_paths=tracked_paths,
        )

    def test_a_function_assignment_shadows_class_and_module_reads(self):
        source = """
ROOT = Path(__file__).resolve().parent
MODULE_SKILL = ROOT / "module.md"
CLASS_SKILL = ROOT / "class.md"
OTHER_SKILL = ROOT / "other.md"
SKILL = ROOT / "skill.md"

def read(path):
    return path.read_text()

text = read(MODULE_SKILL)

class Contract:
    text = read(CLASS_SKILL)

    def test_shadowed(self):
        text = squashed(read(OTHER_SKILL))
        self.assertNotIn("retired prose", text)

    def test_read(self):
        text = read(SKILL)
        self.assertNotIn("retired prose", text)
"""
        self.assertEqual(
            ({"retired prose"}, 1),
            self.walk(source, "module.md", "class.md", "other.md", "skill.md"),
        )

    def test_a_read_name_or_method_without_repository_path_provenance_passes(self):
        source = """
ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "skill.md"
SCRATCH = ROOT / "scratch"
GENERATED_OUTPUT = SCRATCH / "report.md"

def read(path):
    return generated_report(path)

self.assertNotIn("retired prose", read(SKILL))
self.assertNotIn("retired prose", tmp_path.read_text())
self.assertNotIn("retired prose", GENERATED_OUTPUT.read_text())
"""
        self.assertEqual((set(), 0), self.walk(source, "skill.md"))

    def test_a_path_expression_for_an_untracked_file_passes(self):
        source = """
ROOT = Path(__file__).resolve().parent
UNTRACKED = ROOT / "never-committed.md"

def read(path):
    return path.read_text()

self.assertNotIn("retired prose", read(UNTRACKED))
"""
        self.assertEqual((set(), 0), self.walk(source, "tracked.md"))

    def test_a_later_path_reassignment_wins_without_oscillation(self):
        source = """
ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "tracked.md"
SKILL = ROOT / "never-committed.md"

def read(path):
    return path.read_text()

self.assertNotIn("retired prose", read(SKILL))
"""
        self.assertEqual((set(), 0), self.walk(source, "tracked.md"))

    def test_only_needles_changed_by_prose_normalization_fire(self):
        source = """
ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "skill.md"

def read(path):
    return path.read_text()

self.assertNotIn("retired prose", read(SKILL))
self.assertNotIn("unfilled", read(SKILL))
"""
        self.assertEqual(
            ({"retired prose"}, 2), self.walk(source, "skill.md")
        )

    def test_any_read_assignment_in_the_winning_scope_counts(self):
        source = """
ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "skill.md"

def read(path):
    return path.read_text()

def test_contract(self):
    text = generated_report()
    text = read(SKILL)
    self.assertNotIn("retired prose", text)
"""
        self.assertEqual(
            ({"retired prose"}, 1), self.walk(source, "skill.md")
        )

    def test_assert_in_is_outside_the_silent_direction(self):
        source = """
ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "skill.md"

def read(path):
    return path.read_text()

self.assertIn("required prose", read(SKILL))
"""
        self.assertEqual((set(), 0), self.walk(source, "skill.md"))

    def test_every_survivor_is_exactly_declared_and_reasoned(self):
        found, resolved_reads = repository_survivors(REPO_ROOT)
        self.assertGreaterEqual(resolved_reads, RESOLVED_READ_FLOOR)
        self.assertEqual(set(DECLARED_PROSE_BIND_EXCEPTIONS), found)
        for reason in DECLARED_PROSE_BIND_EXCEPTIONS.values():
            self.assertTrue(reason.strip())

if __name__ == "__main__":
    unittest.main()
