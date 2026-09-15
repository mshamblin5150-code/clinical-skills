#!/usr/bin/env python3
"""Keep Code-set database reader tests and their digest pins in agreement."""

from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from console_codec import require_python_floor, use_utf8


TOOLS = Path(__file__).resolve().parent
LOOKUPS = frozenset({"icd10_lookup", "procedure_codes_lookup"})
PIN_CALL = "assert_code_set_database_digest"
PIN_MODULE = "code_set_database_test_support"
PIN_DIGESTS = frozenset({"ICD10_DATABASE_SHA256", "PROCEDURE_CODES_DATABASE_SHA256"})
REFUSAL_MARKER = "CODE_SET_DATABASE_OPEN_REFUSED"

DECLARED_LIMITS = {
    "import walk": (
        "The population includes Python imports visible to ast.Import and "
        "ast.ImportFrom; dynamic imports and commands assembled at run time are unread."
    ),
}

_SUBPROCESS = f"""
import sys
import unittest
from pathlib import Path

tools = Path(sys.argv[1]).resolve()
module_name = sys.argv[2]
sys.path.insert(0, str(tools))

def install_refusal(module_name):
    module = __import__(module_name)
    original = module.open_database
    committed = module.DEFAULT_DATABASE.resolve()
    def refused(path=module.DEFAULT_DATABASE):
        if Path(path).resolve() == committed:
            raise AssertionError('{REFUSAL_MARKER}:' + module_name)
        return original(path)
    module.open_database = refused

for lookup in ('icd10_lookup', 'procedure_codes_lookup'):
    install_refusal(lookup)

suite = unittest.defaultTestLoader.loadTestsFromName(module_name)
result = unittest.TextTestRunner(verbosity=0).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
"""


@dataclass(frozen=True)
class Audit:
    reaching: frozenset[str]
    readers: frozenset[str]
    pinned: frozenset[str]
    unpinned_readers: frozenset[str]
    stale_pins: frozenset[str]


def _trees(tools: Path) -> dict[str, ast.Module]:
    return {
        path.stem: ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for path in tools.glob("*.py")
    }


def _imports(tree: ast.Module, local_modules: frozenset[str]) -> frozenset[str]:
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", 1)[0])
    return frozenset(imported & local_modules)


def _reaches_lookup(
    module: str,
    graph: dict[str, frozenset[str]],
    seen: frozenset[str] = frozenset(),
) -> bool:
    if module in LOOKUPS:
        return True
    if module in seen:
        return False
    return any(
        _reaches_lookup(imported, graph, seen | {module})
        for imported in graph.get(module, ())
    )


class _ModuleBindings(ast.NodeVisitor):
    """Find names a top-level statement can bind without entering a new scope."""

    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.names.add(node.id)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.names.add(node.name)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.names.add(node.name)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return


def _has_pin(tree: ast.Module) -> bool:
    bindings: dict[str, str] = {}
    for statement in tree.body:
        if isinstance(statement, ast.ImportFrom):
            for alias in statement.names:
                name = alias.asname or alias.name
                bindings[name] = (
                    "pin-function"
                    if statement.module == PIN_MODULE and alias.name == PIN_CALL
                    else "pin-digest"
                    if statement.module == PIN_MODULE and alias.name in PIN_DIGESTS
                    else "other"
                )
            continue
        if isinstance(statement, ast.Import):
            for alias in statement.names:
                name = alias.asname or alias.name.split(".", 1)[0]
                bindings[name] = "pin-module" if alias.name == PIN_MODULE else "other"
            continue
        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
            function = statement.value.func
            authentic_function = (
                isinstance(function, ast.Name)
                and bindings.get(function.id) == "pin-function"
                or isinstance(function, ast.Attribute)
                and function.attr == PIN_CALL
                and isinstance(function.value, ast.Name)
                and bindings.get(function.value.id) == "pin-module"
            )
            arguments = statement.value.args
            authentic_digest = len(arguments) >= 2 and (
                isinstance(arguments[1], ast.Name)
                and bindings.get(arguments[1].id) == "pin-digest"
                or isinstance(arguments[1], ast.Attribute)
                and arguments[1].attr in PIN_DIGESTS
                and isinstance(arguments[1].value, ast.Name)
                and bindings.get(arguments[1].value.id) == "pin-module"
            )
            if authentic_function and authentic_digest:
                return True
        assigned = _ModuleBindings()
        assigned.visit(statement)
        for name in assigned.names:
            bindings[name] = "other"
    return False


def _readers_under_refusal(tools: Path, reaching: frozenset[str]) -> frozenset[str]:
    readers: set[str] = set()
    for module in sorted(reaching):
        result = subprocess.run(
            [sys.executable, "-c", _SUBPROCESS, str(tools), module],
            cwd=tools,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        report = result.stdout + result.stderr
        if REFUSAL_MARKER in report:
            readers.add(module)
        elif result.returncode:
            raise RuntimeError(
                f"{module} failed without a Code-set database refusal:\n{report}"
            )
    return frozenset(readers)


def audit(tools: Path = TOOLS) -> Audit:
    """Derive the reaching, reading, and pinned Code-set database test modules."""
    trees = _trees(tools)
    local_modules = frozenset(trees)
    graph = {
        module: _imports(tree, local_modules)
        for module, tree in trees.items()
    }
    test_modules = frozenset(
        module for module in trees if module.startswith("test")
    )
    reaching = frozenset(
        module for module in test_modules if _reaches_lookup(module, graph)
    )
    pinned = frozenset(module for module in test_modules if _has_pin(trees[module]))
    readers = _readers_under_refusal(tools, reaching)
    return Audit(
        reaching=reaching,
        readers=readers,
        pinned=pinned,
        unpinned_readers=readers - pinned,
        stale_pins=pinned - readers,
    )


def main(
    argv: list[str] | None = None,
    *,
    tools: Path = TOOLS,
    stream: TextIO = sys.stdout,
) -> int:
    """Print the derived Code-set database reader population and pin verdict."""
    del argv
    result = audit(tools)
    print("reaching test modules: " + ", ".join(sorted(result.reaching)), file=stream)
    print(DECLARED_LIMITS["import walk"], file=stream)
    for module in sorted(result.unpinned_readers):
        print(f"unpinned Code-set database reader: {module}", file=stream)
    for module in sorted(result.stale_pins):
        print(f"stale Code-set database pin: {module}", file=stream)
    clean = not result.unpinned_readers and not result.stale_pins
    print(
        "Code-set database reader pins: " + ("clean" if clean else "finding"),
        file=stream,
    )
    return 0 if clean else 1


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
