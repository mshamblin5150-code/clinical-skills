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


def _salted_report_input(module: Any, kind: str) -> Any:
    """Build the ``Scan`` input accepted by one member's own report."""

    values = {field.name: _empty_value(field) for field in dataclasses.fields(module.Scan)}
    values["findings"] = (_FindingProbe(kind),)
    if "counts" in values:
        values["counts"] = tuple((row, int(row == kind)) for row in module.ROWS)
    return module.Scan(**values)


def _graded_value(field: dataclasses.Field[Any]) -> Any:
    """Return a visible, report-safe value for one nullable graded field."""

    annotation = str(field.type)
    if "tuple" in annotation:
        return (SimpleNamespace(domain=MARKER, property=MARKER),)
    return 7


def _gate_scan(module: Any, gate: str, enabled: bool) -> Any:
    """Build one report input with every gate but ``gate`` satisfied."""

    declarations = module.GATED_ROW_SETS
    fields = {field.name: field for field in dataclasses.fields(module.Scan)}
    values: dict[str, Any] = {}
    for name, field in fields.items():
        annotation = str(field.type)
        if annotation == "bool":
            values[name] = True
        elif "None" in annotation:
            values[name] = _graded_value(field)
        else:
            values[name] = _empty_value(field)
    for field_name in module.ABSENT_BY_DESIGN_FIELDS:
        values[field_name] = _empty_value(fields[field_name])
    values[gate] = enabled
    for field_name in declarations[gate][1]:
        values[field_name] = _graded_value(fields[field_name]) if enabled else None
    return module.Scan(**values)


def _report_lines(module: Any, scan: Any) -> tuple[str, ...]:
    return tuple(module.format_report(scan, "source", show=False).splitlines())


def _changed_line_indexes(before: tuple[str, ...], after: tuple[str, ...]) -> set[int]:
    if len(before) != len(after):
        raise AssertionError("a gate changed the report's line population")
    return {index for index, pair in enumerate(zip(before, after)) if pair[0] != pair[1]}


def gate_conformance(module: Any) -> type[unittest.TestCase]:
    """Return the opt-in report-width conformance case for boolean gates.

    Membership is deliberately declared by the caller. This walk cannot discover a
    third module that adopts the same shape without opting in, and it proves only
    report behavior; each member's command tests own flag reachability and status.
    """

    class GateConformance(unittest.TestCase):
        def test_every_boolean_field_is_a_declared_gate(self):
            boolean_fields = {
                field.name
                for field in dataclasses.fields(module.Scan)
                if str(field.type) == "bool"
            }
            self.assertEqual(boolean_fields, set(module.GATED_ROW_SETS))

        def test_gated_fields_are_nullable_and_no_nullable_field_is_orphaned(self):
            fields = {field.name: field for field in dataclasses.fields(module.Scan)}
            declared_fields = {
                name
                for _kinds, field_names in module.GATED_ROW_SETS.values()
                for name in field_names
            }
            absent = set(module.ABSENT_BY_DESIGN_FIELDS)
            self.assertFalse(declared_fields & absent)
            for name in declared_fields | absent:
                with self.subTest(field=name):
                    self.assertIn(name, fields)
                    self.assertIn("None", str(fields[name].type))
            nullable_fields = {
                name for name, field in fields.items() if "None" in str(field.type)
            }
            self.assertEqual(nullable_fields, declared_fields | absent)

        def test_each_gate_changes_only_its_declared_report_lines(self):
            fields = {field.name: field for field in dataclasses.fields(module.Scan)}
            for gate, (kinds, field_names) in module.GATED_ROW_SETS.items():
                with self.subTest(gate=gate):
                    off_scan = _gate_scan(module, gate, False)
                    on_scan = _gate_scan(module, gate, True)
                    off = _report_lines(module, off_scan)
                    on = _report_lines(module, on_scan)
                    changed = _changed_line_indexes(off, on)

                    declared_indexes: set[int] = set()
                    for kind in kinds:
                        matches = {
                            index
                            for index, line in enumerate(off)
                            if line.startswith(f"{kind}:")
                        }
                        self.assertEqual(1, len(matches), kind)
                        index = next(iter(matches))
                        self.assertIn(run_grader.NOT_GRADED, off[index])
                        self.assertEqual(f"{kind}: 0", on[index])
                        declared_indexes.add(index)

                    for field_name in field_names:
                        field = fields[field_name]
                        values = {
                            item.name: getattr(on_scan, item.name)
                            for item in dataclasses.fields(module.Scan)
                        }
                        values[field_name] = None
                        without_field = _report_lines(module, module.Scan(**values))
                        field_indexes = _changed_line_indexes(without_field, on)
                        self.assertTrue(field_indexes, field_name)
                        graded_value = _graded_value(field)
                        displayed_value = (
                            len(graded_value)
                            if isinstance(graded_value, tuple)
                            else graded_value
                        )
                        count_lines = {
                            index
                            for index in field_indexes
                            if run_grader.NOT_GRADED in off[index]
                            and str(displayed_value) in on[index]
                        }
                        self.assertTrue(count_lines, field_name)
                        declared_indexes.update(field_indexes)

                    self.assertEqual(changed, declared_indexes)

    GateConformance.__name__ = f"{module.__name__}GateConformance"
    GateConformance.__qualname__ = GateConformance.__name__
    return GateConformance


def constructed_kinds(module: Any, function: str | None = None) -> set[str]:
    """Return kinds proved by literals or lexically enclosing mapping loops.

    This walk deliberately stops short of general data-flow analysis: a name is
    credited only inside the body of the exact ``for`` or comprehension that
    binds it from a module-level dictionary. Assignments, helper returns, and
    same-spelled names in another lexical scope prove nothing.
    """

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
    kinds: set[str] = set()

    def loop_domain(node: ast.For | ast.comprehension) -> tuple[str, set[str]] | None:
        target = node.target
        if isinstance(target, (ast.Tuple, ast.List)) and target.elts:
            target = target.elts[0]
        population_name: str | None = None
        if isinstance(node.iter, ast.Name):
            population_name = node.iter.id
        elif (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Attribute)
            and node.iter.func.attr in {"items", "keys"}
            and isinstance(node.iter.func.value, ast.Name)
        ):
            population_name = node.iter.func.value.id
        population = getattr(module, population_name or "", None)
        if isinstance(target, ast.Name) and isinstance(population, dict):
            return target.id, set(population)
        return None

    class FindingVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.domains: list[dict[str, set[str]]] = [{}]

        def bound(self, name: str) -> set[str]:
            for domain in reversed(self.domains):
                if name in domain:
                    return domain[name]
            return set()

        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id == "Finding":
                expression = next(
                    (keyword.value for keyword in node.keywords if keyword.arg == "kind"),
                    node.args[0] if node.args else None,
                )
                if isinstance(expression, ast.Constant) and isinstance(expression.value, str):
                    kinds.add(expression.value)
                elif isinstance(expression, ast.Name):
                    value = getattr(module, expression.id, None)
                    if isinstance(value, str):
                        kinds.add(value)
                    else:
                        kinds.update(self.bound(expression.id))
            self.generic_visit(node)

        def visit_For(self, node: ast.For) -> None:
            self.visit(node.iter)
            binding = loop_domain(node)
            self.domains.append({binding[0]: binding[1]} if binding else {})
            for child in node.body:
                self.visit(child)
            self.domains.pop()
            for child in node.orelse:
                self.visit(child)

        def visit_ListComp(self, node: ast.ListComp) -> None:
            self._visit_comprehension(node.elt, node.generators)

        def visit_SetComp(self, node: ast.SetComp) -> None:
            self._visit_comprehension(node.elt, node.generators)

        def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
            self._visit_comprehension(node.elt, node.generators)

        def visit_DictComp(self, node: ast.DictComp) -> None:
            self._visit_comprehension((node.key, node.value), node.generators)

        def _visit_comprehension(
            self,
            result: ast.AST | tuple[ast.AST, ast.AST],
            generators: list[ast.comprehension],
        ) -> None:
            pushed = 0
            for generator in generators:
                self.visit(generator.iter)
                binding = loop_domain(generator)
                self.domains.append({binding[0]: binding[1]} if binding else {})
                pushed += 1
                for condition in generator.ifs:
                    self.visit(condition)
            if isinstance(result, tuple):
                for child in result:
                    self.visit(child)
            else:
                self.visit(result)
            for _ in range(pushed):
                self.domains.pop()

    FindingVisitor().visit(scope)
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
                    scan = _salted_report_input(module, kind)
                    default = module.format_report(scan, "source", show=False)
                    shown = module.format_report(scan, "source", show=True)
                    self.assertNotIn(MARKER, default)
                    self.assertIn(MARKER, shown)

        def test_findings_outrank_coverage_after_the_modules_report(self):
            scan = _salted_report_input(module, next(iter(module.ROWS)))
            command = dataclasses.replace(
                module.GRADER,
                options=(),
                load=lambda _parsed: scan,
                grade=lambda loaded, _parsed: run_grader.Grade(
                    scan=loaded,
                    source="source",
                    findings_failed=True,
                    coverage_failed=True,
                    coverage_limbs=module.GRADER.exit_2_limbs[-1:],
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
