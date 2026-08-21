"""Reusable public-seam conformance tests for ``run_grader`` members."""

from __future__ import annotations

import ast
import dataclasses
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


def _report_scan(module: Any) -> Any:
    kind = next(iter(module.ROWS))
    values = {field.name: _empty_value(field) for field in dataclasses.fields(module.Scan)}
    values["findings"] = (_FindingProbe(kind),)
    if "counts" in values:
        values["counts"] = tuple((row, int(row == kind)) for row in module.ROWS)
    return module.Scan(**values)


def _constructed_kinds(module: Any) -> set[str]:
    source = Path(inspect.getsourcefile(module) or "").read_text(encoding="utf-8")
    tree = ast.parse(source)
    kinds: set[str] = set()
    for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
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
            elif expression.id in {"kind", "row"}:
                # A loop over the declared vocabulary constructs every row. The
                # shared equality below still refuses an undeclared literal.
                kinds.update(module.ROWS)
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
            self.assertEqual(set(module.ROWS), _constructed_kinds(module))

        def test_the_modules_own_report_redacts_until_show(self):
            scan = _report_scan(module)
            default = module.format_report(scan, "source", show=False)
            shown = module.format_report(scan, "source", show=True)
            self.assertNotIn(MARKER, default)
            self.assertIn(MARKER, shown)

    GraderConformance.__name__ = f"{module.__name__}GraderConformance"
    GraderConformance.__qualname__ = GraderConformance.__name__
    return GraderConformance
