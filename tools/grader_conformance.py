"""Reusable public-seam conformance tests for ``run_grader`` members."""

from __future__ import annotations

import ast
import contextlib
import dataclasses
import io
import inspect
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import run_grader


MARKER = "conformance-salted-marker"


class _FindingProbe:
    def __init__(self, kind: str):
        self.kind = kind
        self.line = 1

    def __getattr__(self, _name: str) -> str:
        return MARKER


def _empty_value(field: dataclasses.Field[Any]) -> Any:
    if field.default is not dataclasses.MISSING:
        return field.default
    if field.default_factory is not dataclasses.MISSING:
        return field.default_factory()
    annotation = str(field.type)
    if "bool" in annotation:
        return False
    if any(container in annotation for container in ("tuple", "list", "dict", "set")):
        return ()
    if "str" in annotation:
        return ""
    return 0


def _report_scan(module: Any, kind: str) -> Any:
    values = {field.name: _empty_value(field) for field in dataclasses.fields(module.Scan)}
    values["findings"] = (_FindingProbe(kind),)
    if "counts" in values:
        values["counts"] = tuple((row, int(row == kind)) for row in module.ROWS)
    return module.Scan(**values)


def constructed_kinds(module: Any, function: str | None = None) -> set[str]:
    source_path = getattr(module, "__file__", None) or inspect.getsourcefile(module)
    source = Path(source_path or "").read_text(encoding="utf-8")
    tree = ast.parse(source)
    scope: ast.AST = tree
    if function is not None:
        scope = next(
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function
        )
    domains: dict[str, set[str]] = {}
    for loop in (node for node in ast.walk(scope) if isinstance(node, (ast.For, ast.comprehension))):
        target = loop.target
        if isinstance(target, (ast.Tuple, ast.List)) and target.elts:
            target = target.elts[0]
        population_name: str | None = None
        if isinstance(loop.iter, ast.Name):
            population_name = loop.iter.id
        elif (
            isinstance(loop.iter, ast.Call)
            and isinstance(loop.iter.func, ast.Attribute)
            and loop.iter.func.attr in {"items", "keys"}
            and isinstance(loop.iter.func.value, ast.Name)
        ):
            population_name = loop.iter.func.value.id
        if not isinstance(target, ast.Name) or population_name is None:
            continue
        population = getattr(module, population_name, None)
        if isinstance(population, dict):
            domains[target.id] = set(population)
    kinds: set[str] = set()
    for call in (node for node in ast.walk(scope) if isinstance(node, ast.Call)):
        if not isinstance(call.func, ast.Name) or call.func.id != "Finding":
            continue
        expression = next(
            (keyword.value for keyword in call.keywords if keyword.arg == "kind"),
            call.args[0] if call.args else None,
        )
        if isinstance(expression, ast.Constant) and isinstance(expression.value, str):
            kinds.add(expression.value)
        elif isinstance(expression, ast.Name):
            value = getattr(module, expression.id, None)
            if isinstance(value, str):
                kinds.add(value)
            else:
                kinds.update(domains.get(expression.id, set()))
    return kinds


def for_module(module: Any) -> type[unittest.TestCase]:
    """Return one discoverable conformance case bound to ``module``."""

    class GraderConformance(unittest.TestCase):
        def test_the_module_delegates_its_main_to_the_shared_runner(self):
            source = inspect.getsource(module.main)
            self.assertIn("run_grader.run", source)
            self.assertIs(module.GRADER.format_report, module.format_report)

        def test_an_unrecognized_flag_refuses_before_loading(self):
            with self.assertRaises(run_grader.ParseError):
                run_grader.parse(module.GRADER, ["source", "--shwo"])

        def test_the_finding_inherits_the_shared_kind(self):
            self.assertTrue(issubclass(module.Finding, run_grader.Finding))

        def test_rows_are_the_one_vocabulary_and_every_row_is_constructible(self):
            self.assertEqual(tuple(module.ROWS), module.KINDS)
            self.assertEqual(set(module.ROWS), constructed_kinds(module))

        def test_the_modules_own_report_redacts_until_show(self):
            for kind in module.ROWS:
                with self.subTest(kind=kind):
                    scan = _report_scan(module, kind)
                    default = module.format_report(scan, "source", show=False)
                    shown = module.format_report(scan, "source", show=True)
                    self.assertNotIn(MARKER, default)
                    self.assertIn(MARKER, shown)

        def test_findings_outrank_coverage_after_the_modules_report(self):
            scan = _report_scan(module, next(iter(module.ROWS)))
            command = dataclasses.replace(
                module.GRADER,
                options=(),
                load=lambda _parsed: scan,
                grade=lambda loaded, _parsed: run_grader.Grade(
                    scan=loaded,
                    source="source",
                    findings_failed=True,
                    coverage_failed=True,
                    diagnostics=("tier-two-diagnostic",),
                ),
            )
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = run_grader.run(command, ["source"])
            self.assertEqual(1, status)
            self.assertTrue(stdout.getvalue().startswith(module.format_report(scan, "source")))
            self.assertIn("tier-two-diagnostic", stderr.getvalue())

    GraderConformance.__name__ = f"{module.__name__}GraderConformance"
    GraderConformance.__qualname__ = GraderConformance.__name__
    return GraderConformance
