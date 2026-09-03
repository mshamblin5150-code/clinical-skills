from __future__ import annotations

import ast
import contextlib
import importlib
import io
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import run_grader
from grader_conformance import constructed_kinds


@dataclass(frozen=True)
class ExampleFinding(run_grader.Finding):
    detail: str


@dataclass(frozen=True)
class ExampleScan:
    findings: tuple[ExampleFinding, ...]


def command_for(result: run_grader.Grade[ExampleScan]) -> run_grader.Grader:
    return run_grader.Grader(
        usage="usage: example.py <source> [--show]",
        options=(run_grader.Option("--show"),),
        load=lambda parsed: parsed.source,
        grade=lambda _source, _parsed: result,
        format_report=lambda scan, source, show=False: (
            f"report {source} "
            + (scan.findings[0].detail if show and scan.findings else "redacted")
        ),
    )


class FindingCarriesOnlyTheSharedKind(unittest.TestCase):
    def test_a_frozen_subclass_keeps_its_own_required_fields(self):
        finding = ExampleFinding("row-a", "marker")

        self.assertEqual("row-a", finding.kind)
        self.assertEqual("marker", finding.detail)
        with self.assertRaises((AttributeError, TypeError)):
            finding.kind = "changed"  # type: ignore[misc]


class TheRunnerOwnsTheCommandTail(unittest.TestCase):
    def run_command(self, command, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = run_grader.run(command, argv)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_an_unrecognized_flag_refuses_before_loading(self):
        called = False

        def load(_parsed):
            nonlocal called
            called = True

        command = run_grader.Grader(
            usage="usage: example.py <source> [--show]",
            options=(run_grader.Option("--show"),),
            load=load,
            grade=lambda _source, _parsed: None,
            format_report=lambda _scan, _source, show=False: "never",
        )

        status, stdout, stderr = self.run_command(command, ["source", "--shwo"])

        self.assertEqual(2, status)
        self.assertEqual("", stdout)
        self.assertIn("unrecognized option --shwo", stderr)
        self.assertFalse(called)

    def test_a_source_failure_exits_before_a_report_is_printed(self):
        def load(_parsed):
            raise run_grader.SourceError("source could not be read")

        command = run_grader.Grader(
            usage="usage: example.py <source>",
            load=load,
            grade=lambda _source, _parsed: None,
            format_report=lambda _scan, _source, show=False: "never",
        )

        status, stdout, stderr = self.run_command(command, ["source"])

        self.assertEqual(2, status)
        self.assertEqual("", stdout)
        self.assertEqual("source could not be read\n", stderr)

    def test_the_report_prints_before_a_tier_two_failure_is_decided(self):
        result = run_grader.Grade(
            scan=ExampleScan(()),
            source="source",
            coverage_failed=True,
            diagnostics=("nothing was scanned",),
        )

        status, stdout, stderr = self.run_command(command_for(result), ["source"])

        self.assertEqual(2, status)
        self.assertEqual("report source redacted\n", stdout)
        self.assertEqual("nothing was scanned\n", stderr)

    def test_a_finding_outranks_a_tier_two_failure(self):
        result = run_grader.Grade(
            scan=ExampleScan((ExampleFinding("row-a", "marker"),)),
            source="source",
            findings_failed=True,
            coverage_failed=True,
            diagnostics=("one row did not scan", "one finding"),
        )

        status, stdout, stderr = self.run_command(command_for(result), ["source"])

        self.assertEqual(1, status)
        self.assertEqual("report source redacted\n", stdout)
        self.assertEqual("one row did not scan\none finding\n", stderr)

    def test_show_is_the_only_declared_flag_and_reaches_the_report(self):
        result = run_grader.Grade(
            scan=ExampleScan((ExampleFinding("row-a", "salted marker"),)),
            source="source",
            findings_failed=True,
        )

        status, stdout, _stderr = self.run_command(command_for(result), ["source", "--show"])

        self.assertEqual(1, status)
        self.assertIn("salted marker", stdout)

    def test_a_declared_exit_two_vocabulary_rejects_an_unmapped_source_failure(self):
        def load(_parsed):
            raise run_grader.SourceError(
                "source could not be read", exit_2_limb="a different source failure"
            )

        command = run_grader.Grader(
            usage="usage: example.py <source>",
            load=load,
            grade=lambda _source, _parsed: None,
            format_report=lambda _scan, _source, show=False: "never",
            exit_2_limbs=("invalid invocation", "source unavailable"),
            invalid_invocation_limb="invalid invocation",
        )

        with self.assertRaisesRegex(ValueError, "undeclared exit-2 limb"):
            self.run_command(command, ["source"])

    def test_a_declared_exit_two_vocabulary_requires_coverage_to_name_its_limbs(self):
        result = run_grader.Grade(
            scan=ExampleScan(()),
            source="source",
            coverage_failed=True,
            diagnostics=("nothing was scanned",),
        )
        command = run_grader.Grader(
            usage="usage: example.py <source>",
            load=lambda parsed: parsed.source,
            grade=lambda _source, _parsed: result,
            format_report=lambda _scan, _source, show=False: "report",
            exit_2_limbs=("invalid invocation", "coverage incomplete"),
            invalid_invocation_limb="invalid invocation",
        )

        with self.assertRaisesRegex(ValueError, "names no exit-2 limb"):
            self.run_command(command, ["source"])


class TheRunDirectoryReaderOwnsTheSetPolicy(unittest.TestCase):
    def test_it_sorts_markdown_replaces_an_undecodable_byte_and_excludes_readme(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "b.md").write_text("second", encoding="utf-8")
            (root / "README.md").write_text("not an artifact", encoding="utf-8")
            (root / "a.md").write_bytes(b"first\xff")

            self.assertEqual(
                ["first\ufffd", "second"],
                run_grader.read_run_directory(root),
            )

    def test_an_artifact_that_cannot_be_opened_is_a_declared_source_failure(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "case-01.md").write_text("held", encoding="utf-8")
            sensitive = str(root / "patient-name.md")
            denied = PermissionError(13, "denied", sensitive)
            with mock.patch.object(Path, "read_text", side_effect=denied):
                with self.assertRaises(run_grader.SourceError) as raised:
                    run_grader.read_run_directory(root)

        self.assertEqual(run_grader.UNREADABLE_RUN_ARTIFACT, raised.exception.exit_2_limb)
        self.assertIn("could not read a run artifact", str(raised.exception))
        self.assertNotIn(sensitive, str(raised.exception))

    def test_the_declared_consumers_call_the_shared_reader_without_local_aliases(self):
        here = Path(__file__).parent
        for name in sorted(run_grader.RUN_DIRECTORY_READERS):
            with self.subTest(module=name):
                tree = ast.parse((here / f"{name}.py").read_text(encoding="utf-8"))
                local_functions = {
                    node.name
                    for node in tree.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                calls_shared_reader = any(
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "run_grader"
                    and node.func.attr == "read_run_directory"
                    for node in ast.walk(tree)
                )

                self.assertNotIn("read_notes", local_functions)
                self.assertNotIn("read_worksheets", local_functions)
                self.assertTrue(calls_shared_reader)

    def test_all_declared_consumers_refuse_an_artifact_open_failure_at_exit_two(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "case-01.md").write_text("held", encoding="utf-8")
            failure = run_grader.SourceError(
                "could not read a run artifact",
                exit_2_limb=run_grader.UNREADABLE_RUN_ARTIFACT,
            )
            for name in sorted(run_grader.RUN_DIRECTORY_READERS):
                module = importlib.import_module(name)
                with self.subTest(module=name):
                    stdout = io.StringIO()
                    stderr = io.StringIO()
                    with (
                        mock.patch.object(
                            run_grader,
                            "read_run_directory",
                            side_effect=failure,
                        ),
                        contextlib.redirect_stdout(stdout),
                        contextlib.redirect_stderr(stderr),
                    ):
                        status = module.main([str(root)])

                    self.assertEqual(2, status)
                    emitted = stdout.getvalue() if name == "refusal_scan" else stderr.getvalue()
                    quiet = stderr.getvalue() if name == "refusal_scan" else stdout.getvalue()
                    self.assertEqual("", quiet)
                    self.assertIn("could not read a run artifact", emitted)


class TheUndecodableBytePostureIsDeclaredForTheFamily(unittest.TestCase):
    def test_every_reader_has_one_reasoned_posture(self):
        declared = run_grader.UNDECODABLE_BYTE_POSTURES
        population = run_grader.MEMBERS | set(run_grader.DEFERRED)
        named = [name for reasons in declared.values() for name in reasons]

        self.assertEqual(population, set(named))
        self.assertEqual(len(named), len(set(named)))
        self.assertTrue(all(reason for reasons in declared.values() for reason in reasons.values()))
        self.assertEqual(
            {"grade", "refuse", "crash", "no text read"},
            set(declared),
        )

    def test_the_unshared_readers_have_ast_evidence_with_a_written_ceiling(self):
        here = Path(__file__).parent
        posture_of = {
            name: posture
            for posture, reasons in run_grader.UNDECODABLE_BYTE_POSTURES.items()
            for name in reasons
        }
        remaining = (
            run_grader.MEMBERS | set(run_grader.DEFERRED)
        ) - run_grader.RUN_DIRECTORY_READERS
        self.assertIn("read_text", run_grader.TEXT_READ_WALK_CEILING)
        self.assertIn("floor", run_grader.TEXT_READ_WALK_CEILING)

        for name in sorted(remaining):
            with self.subTest(module=name):
                source = (here / f"{name}.py").read_text(encoding="utf-8")
                evidence = run_grader.walk_text_reads(source)
                self.assertEqual(evidence.total, evidence.recognized)
                posture = posture_of[name]
                if posture == "grade":
                    self.assertGreater(evidence.replacing, 0)
                elif posture == "refuse":
                    self.assertGreater(evidence.refusing, 0)
                    self.assertEqual(0, evidence.replacing)
                    self.assertEqual(0, evidence.crashing)
                elif posture == "crash":
                    self.assertGreater(evidence.crashing, 0)
                    self.assertGreater(evidence.replacing, 0)
                else:
                    self.assertEqual("no text read", posture)
                    self.assertEqual(0, evidence.total)

    def test_a_zero_match_mutant_is_unread_rather_than_clean(self):
        evidence = run_grader.walk_text_reads(
            "def load(path, mode):\n    return path.read_text(encoding='utf-8', errors=mode)\n"
        )

        self.assertEqual(1, evidence.total)
        self.assertEqual(0, evidence.recognized)
        self.assertEqual(1, evidence.unread)

    def test_a_partial_match_mutant_reports_its_unread_remainder(self):
        evidence = run_grader.walk_text_reads(
            "def load(first, second, mode):\n"
            "    return (first.read_text(encoding='utf-8', errors='replace'),\n"
            "            second.read_text(encoding='utf-8', errors=mode))\n"
        )

        self.assertEqual(2, evidence.total)
        self.assertEqual(1, evidence.recognized)
        self.assertEqual(1, evidence.unread)

    def test_a_strict_read_refuses_only_when_both_open_and_decode_failures_convert(self):
        complete = run_grader.walk_text_reads(
            "def load(path):\n"
            "    try:\n        return path.read_text(encoding='utf-8')\n"
            "    except (OSError, UnicodeError):\n        raise run_grader.SourceError('no source')\n"
        )
        partial = run_grader.walk_text_reads(
            "def load(path):\n"
            "    try:\n        return path.read_text(encoding='utf-8')\n"
            "    except OSError:\n        raise run_grader.SourceError('no source')\n"
        )

        self.assertEqual(1, complete.refusing)
        self.assertEqual(0, complete.crashing)
        self.assertEqual(0, partial.refusing)
        self.assertEqual(1, partial.crashing)


class TheMembershipClaimIsDerivedFromTheTree(unittest.TestCase):
    def test_every_grader_shape_is_declared_with_the_walks_ceiling(self):
        population = run_grader.walk_grader_modules()

        self.assertEqual(
            population,
            run_grader.MEMBERS
            | set(run_grader.REFUSED)
            | set(run_grader.DEFERRED),
        )
        self.assertIn("__main__", run_grader.WALK_CEILING)
        self.assertIn("survey", run_grader.WALK_CEILING)
        self.assertIn("format_report", run_grader.WALK_CEILING)

    def test_every_nonmember_verdict_carries_a_reason(self):
        self.assertTrue(all(run_grader.REFUSED.values()))
        self.assertTrue(all(run_grader.DEFERRED.values()))
        self.assertTrue(all(run_grader.OUTSIDE_WALK.values()))

    def test_threshold_sheet_names_both_runner_mismatches(self):
        reason = run_grader.REFUSED["threshold_sheet"]

        self.assertIn("quiet", reason)
        self.assertIn("multiple sheets", reason)

    def test_aar_scan_is_deferred_with_its_migration_work_named(self):
        reason = run_grader.DEFERRED["aar_scan"]

        self.assertIn("#840", reason)
        self.assertIn("second entry point", reason)
        self.assertIn("post-report side effect", reason)

    def test_filled_vitals_census_deferral_names_its_owner(self):
        reason = run_grader.DEFERRED["filled_vitals_census"]

        self.assertIn("#842", reason)
        self.assertIn("Finding rewrite", reason)

    def test_every_declared_member_delegates_and_adopts_the_kit(self):
        here = Path(__file__).parent
        for member in sorted(run_grader.MEMBERS):
            with self.subTest(member=member):
                source = (here / f"{member}.py").read_text(encoding="utf-8")
                member_tree = ast.parse(source)
                imports_runner = any(
                    isinstance(node, ast.Import)
                    and any(alias.name == "run_grader" for alias in node.names)
                    for node in member_tree.body
                )
                main = next(
                    node
                    for node in member_tree.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == "main"
                )
                delegates_to_runner = any(
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "run_grader"
                    and node.func.attr == "run"
                    for node in ast.walk(main)
                )
                self.assertTrue(imports_runner and delegates_to_runner)
                tests = (here / f"test_{member}.py").read_text(encoding="utf-8")
                tree = ast.parse(tests)
                imports_kit = any(
                    isinstance(node, ast.ImportFrom)
                    and node.module == "grader_conformance"
                    and any(alias.name == "for_module" for alias in node.names)
                    or isinstance(node, ast.Import)
                    and any(alias.name == "grader_conformance" for alias in node.names)
                    for node in tree.body
                )
                calls_kit = any(
                    isinstance(node, ast.Call)
                    and (
                        isinstance(node.func, ast.Name)
                        and node.func.id == "for_module"
                        or isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "grader_conformance"
                        and node.func.attr == "for_module"
                    )
                    for node in ast.walk(tree)
                )
                self.assertTrue(imports_kit and calls_kit)

    def test_members_import_the_shared_not_graded_sentinel(self):
        here = Path(__file__).parent
        for member in sorted(run_grader.MEMBERS):
            with self.subTest(member=member):
                module = importlib.import_module(member)
                tree = ast.parse(
                    (here / f"{member}.py").read_text(encoding="utf-8")
                )
                executable_literals: set[str] = set()
                for function in (
                    node
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                ):
                    docstring = function.body[0] if function.body else None
                    executable_literals.update(
                        node.value
                        for node in ast.walk(function)
                        if isinstance(node, ast.Constant)
                        and isinstance(node.value, str)
                        and not (
                            isinstance(docstring, ast.Expr)
                            and node is docstring.value
                        )
                    )
                self.assertFalse(
                    any("not graded" in literal for literal in executable_literals),
                    "executable code writes the shared sentinel as a local literal",
                )
                if any(
                    isinstance(node, ast.Name) and node.id == "NOT_GRADED"
                    for node in ast.walk(tree)
                ):
                    self.assertIs(module.NOT_GRADED, run_grader.NOT_GRADED)

    def test_aar_scan_uses_the_shared_not_graded_sentinel_while_deferred(self):
        module = importlib.import_module("aar_scan")

        self.assertIs(module.NOT_GRADED, run_grader.NOT_GRADED)


class TheSharedFindingWalkStatesAndTestsItsCeiling(unittest.TestCase):
    def module_for(self, source: str):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "grader.py"
        path.write_text(source, encoding="utf-8")
        module = SimpleNamespace(__file__=str(path), ROWS={"row-a": "rule", "row-b": "rule"})
        return directory, module

    def test_a_computed_kind_with_no_declared_population_proves_nothing(self):
        directory, module = self.module_for(
            "def findings(kind):\n    return Finding(kind, 'detail')\n"
        )
        try:
            self.assertEqual(set(), constructed_kinds(module))
        finally:
            directory.cleanup()

    def test_a_partial_literal_population_stays_partial(self):
        directory, module = self.module_for(
            "ROW_A = 'row-a'\ndef findings():\n    return Finding(ROW_A, 'detail')\n"
        )
        module.ROW_A = "row-a"
        try:
            self.assertEqual({"row-a"}, constructed_kinds(module))
            self.assertNotEqual(set(module.ROWS), constructed_kinds(module))
        finally:
            directory.cleanup()

    def test_a_loop_over_a_declared_mapping_proves_its_keys(self):
        directory, module = self.module_for(
            "ROW_PATTERNS = {'row-a': 1, 'row-b': 2}\n"
            "def findings():\n"
            "    return [Finding(row, 'detail') for row, pattern in ROW_PATTERNS.items()]\n"
        )
        module.ROW_PATTERNS = {"row-a": 1, "row-b": 2}
        try:
            self.assertEqual(set(module.ROWS), constructed_kinds(module))
        finally:
            directory.cleanup()

    def test_a_same_spelled_name_outside_the_loop_proves_nothing(self):
        directory, module = self.module_for(
            "ROW_PATTERNS = {'row-a': 1, 'row-b': 2}\n"
            "def unrelated():\n"
            "    for kind in ROW_PATTERNS:\n"
            "        pass\n"
            "def findings(kind):\n"
            "    return Finding(kind, 'detail')\n"
        )
        module.ROW_PATTERNS = {"row-a": 1, "row-b": 2}
        try:
            self.assertEqual(set(), constructed_kinds(module))
        finally:
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
