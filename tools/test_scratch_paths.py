"""Guard the scratch resolver's declared root-shape floor, with mutants."""

import ast
from pathlib import Path
import unittest

import repo_root
import scratch_census


def direct_joins(sources: dict[str, str]) -> tuple[str, ...]:
    """Trace syntactic roots; parameters and runtime assembly stay unrecognized.

    Tests are deliberately outside the population: their synthetic roots and
    arbitrary private names are fixture inputs, not account-state resolvers.
    """
    trees = {name: ast.parse(text) for name, text in sources.items()}
    globals_by_module = {name: set() for name in trees}

    def imports(tree):
        modules = {}
        resolvers = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update((item.asname or item.name, item.name) for item in node.names)
            if isinstance(node, ast.ImportFrom):
                if node.module == "repo_root":
                    resolvers.update(item.asname or item.name for item in node.names
                                     if item.name == "scratch_root")
        return modules, resolvers

    def is_root(node, names, modules, resolvers):
        if isinstance(node, ast.Name):
            return node.id in names
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            return node.attr in globals_by_module.get(modules.get(node.value.id), set())
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in resolvers:
                return True
            if isinstance(node.func, ast.Attribute):
                if (node.func.attr == "scratch_root"
                        and isinstance(node.func.value, ast.Name)
                        and modules.get(node.func.value.id) == "repo_root"):
                    return True
                if node.func.attr in ("resolve", "expanduser"):
                    return is_root(node.func.value, names, modules, resolvers)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            return isinstance(node.right, ast.Constant) and node.right.value == "scratch"
        if isinstance(node, (ast.Set, ast.Tuple, ast.List)):
            return any(is_root(item, names, modules, resolvers) for item in node.elts)
        if isinstance(node, ast.IfExp):
            return any(is_root(item, names, modules, resolvers)
                       for item in (node.body, node.orelse))
        return False

    def scope_nodes(statements):
        # Nested function scopes are separate; walk control-flow blocks here.
        for node in statements:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            yield node
            for field in ("body", "orelse", "finalbody"):
                yield from scope_nodes(getattr(node, field, ()))
            for handler in getattr(node, "handlers", ()):
                yield from scope_nodes(handler.body)

    def trace(nodes, names, modules, resolvers):
        changed = True
        while changed:
            before = names.copy()
            for node in nodes:
                if isinstance(node, ast.Assign):
                    targets, value = node.targets, node.value
                elif isinstance(node, ast.AnnAssign):
                    targets, value = (node.target,), node.value
                elif isinstance(node, (ast.For, ast.AsyncFor)):
                    targets, value = (node.target,), node.iter
                else:
                    continue
                if is_root(value, names, modules, resolvers):
                    names.update(target.id for target in targets if isinstance(target, ast.Name))
            changed = before != names

    # Module constants may depend on another module's constants.
    changed = True
    while changed:
        before = {name: names.copy() for name, names in globals_by_module.items()}
        for name, tree in trees.items():
            trace(list(scope_nodes(tree.body)), globals_by_module[name], *imports(tree))
        changed = before != globals_by_module

    findings = set()
    for name, tree in trees.items():
        if name == "repo_root":
            continue
        modules, resolvers = imports(tree)
        scopes = [tree.body] + [node.body for node in ast.walk(tree)
                               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for statements in scopes:
            nodes = list(scope_nodes(statements))
            names = globals_by_module[name].copy()
            trace(nodes, names, modules, resolvers)
            for statement in nodes:
                # Inspect expressions without leaking nested function definitions.
                for field, value in ast.iter_fields(statement):
                    if field in ("body", "orelse", "finalbody", "handlers"):
                        continue
                    expressions = value if isinstance(value, list) else [value]
                    for expression in expressions:
                        if not isinstance(expression, ast.AST):
                            continue
                        for node in ast.walk(expression):
                            if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
                                    and isinstance(node.right, (ast.Constant, ast.Name, ast.Attribute))
                                    and is_root(node.left, names, modules, resolvers)):
                                findings.add(f"{name}:{node.lineno}")
    return tuple(sorted(findings))


class ScratchPathGuardTests(unittest.TestCase):
    def test_no_account_resolver_bypasses_the_list(self):
        directory = Path(__file__).parent
        sources = {path.stem: path.read_text(encoding="utf-8")
                   for path in directory.glob("*.py") if not path.name.startswith("test")}
        self.assertEqual(direct_joins(sources), ())

    def test_each_declared_root_shape_and_name_source_refuses_a_mutant(self):
        mutants = (
            'import repo_root\np = repo_root.scratch_root() / "runs"',
            'from repo_root import scratch_root as root\np = root() / NAME',
            'p = ROOT / "scratch" / "runs"',
            'import repo_root\nSCRATCH = repo_root.scratch_root()\np = SCRATCH / NAME',
            'import owner\np = owner.SCRATCH / "runs"',
            'from repo_root import scratch_root\ndef f():\n s = scratch_root().resolve()\n p = s / "runs"',
            'import repo_root\np = repo_root.scratch_root() / repo_root.VOICE_MODEL_NAME',
            'from repo_root import scratch_root\ndef f():\n local = ROOT / "scratch"\n for root in {local, scratch_root()}:\n  p = root / "runs"',
        )
        for mutant in mutants:
            with self.subTest(mutant=mutant):
                self.assertTrue(direct_joins({"mutant": mutant, "owner":
                    'from repo_root import scratch_root\nSCRATCH = scratch_root()'}))

    def test_parameter_root_is_outside_the_declared_floor(self):
        self.assertEqual(direct_joins({"mutant": 'def f(root):\n return root / "runs"'}), ())
        self.assertTrue(any("parameter-rooted" in row for row in scratch_census.DECLARED_LIMITS))

    def test_registered_name_preserves_the_callers_root_and_refuses_unknown_names(self):
        root = Path("synthetic")
        self.assertEqual(repo_root.scratch_path(root, "runs"), root / "runs")
        for name in ("unregistered.md", "../runs", "runs/child"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                repo_root.scratch_path(root, name)


if __name__ == "__main__":
    unittest.main()
