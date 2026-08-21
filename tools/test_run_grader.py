from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

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


class TheMembershipClaimIsDerivedFromTheTree(unittest.TestCase):
    def test_every_grader_shape_is_declared_with_the_walks_ceiling(self):
        population = run_grader.walk_grader_modules()

        self.assertEqual(
            population,
            run_grader.MEMBERS | set(run_grader.NOT_MEMBERS),
        )
        self.assertIn("__main__", run_grader.WALK_CEILING)
        self.assertIn("survey", run_grader.WALK_CEILING)
        self.assertIn("format_report", run_grader.WALK_CEILING)

    def test_every_exclusion_carries_a_reason(self):
        self.assertTrue(all(run_grader.NOT_MEMBERS.values()))
        self.assertTrue(all(run_grader.OUTSIDE_WALK.values()))


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


if __name__ == "__main__":
    unittest.main()
