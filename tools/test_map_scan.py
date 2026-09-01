"""Public-contract tests for the offline implementation-map grader."""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import map_scan


STATE_BEGIN = "<!-- implementation-map:v1:state:begin -->"
STATE_END = "<!-- implementation-map:v1:state:end -->"


def issue(number, *, state="open", labels=(), body="", title="private title"):
    return {
        "number": number,
        "state": state,
        "labels": [{"name": label} for label in labels],
        "assignees": [],
        "body": body,
        "title": title,
    }


def map_body(state, *, pointer=True, state_prefix=""):
    prose = (
        "## Maintenance rule\nMaintenance uses `tools/map_scan.py` and points to "
        "`map_scan.DECLARED_LIMITS`.\n\n## How to update this map"
        if pointer
        else "## Maintenance rule\nMaintenance asks somebody to remember the reconciliation."
    )
    payload = json.dumps(state, indent=2, sort_keys=True)
    return (
        f"{prose}\n{STATE_BEGIN}\n```json\n{state_prefix}{payload}\n```\n"
        f"{STATE_END}\n"
    )


def state(anchor, *, packets=None, exclusions=None):
    return {
        "schema": 1,
        "repo": "owner/repo",
        "ready_labels": ["ready-for-agent"],
        "in_flight_labels": ["in flight"],
        "reconciled_through": anchor,
        "packets": packets or [],
        "edges": [],
        "collision_groups": [],
        "exclusions": exclusions or [],
    }


class ScannerCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "tests@example.invalid"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Map Scanner Tests"],
            cwd=self.root,
            check=True,
        )
        (self.root / "docs" / "adr").mkdir(parents=True)
        (self.root / "seed.txt").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.root, check=True)
        self.anchor = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()

    def tearDown(self):
        self.temp.cleanup()

    def write_harvest(self, rows, name="issues.json"):
        path = self.root / name
        path.write_text(json.dumps(rows), encoding="utf-8")
        return path

    def run_scan(self, rows, *arguments):
        path = self.write_harvest(rows)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = map_scan.main([str(path), *arguments], repo_root=self.root)
        return code, stdout.getvalue(), stderr.getvalue()

    def map_issue(self, value, *, pointer=True, number=596, **kw):
        return issue(number, body=map_body(value, pointer=pointer), **kw)


class ReadinessDisagreement(ScannerCase):
    def test_a_clean_harvest_is_clean(self):
        value = state(
            self.anchor,
            packets=[{"id": "P10", "tickets": [10], "title": "", "outcome": ""}],
        )
        code, stdout, _ = self.run_scan(
            [self.map_issue(value), issue(10, labels=["ready-for-agent"])]
        )
        self.assertEqual(code, map_scan.CLEAN)
        self.assertIn("clean: no findings", stdout)

    def test_an_unmapped_ready_ticket_is_a_finding(self):
        value = state(self.anchor)
        code, stdout, _ = self.run_scan(
            [self.map_issue(value), issue(42, labels=["ready-for-agent"])]
        )
        self.assertEqual(code, map_scan.FOUND)
        self.assertIn("unmapped-ready", stdout)
        self.assertIn("ticket #42", stdout)
        self.assertIn("ready-for-agent", stdout)
        self.assertIn("packet -", stdout)

    def test_a_packeted_open_ticket_that_is_no_longer_ready_is_a_finding(self):
        value = state(
            self.anchor,
            packets=[{"id": "P17", "tickets": [17], "title": "", "outcome": ""}],
        )
        code, stdout, _ = self.run_scan([self.map_issue(value), issue(17)])
        self.assertEqual(code, map_scan.FOUND)
        self.assertIn("mapped-not-ready", stdout)
        self.assertIn("ticket #17", stdout)
        self.assertIn("ready-for-agent", stdout)
        self.assertIn("packet P17", stdout)

    def test_closed_mapped_tickets_are_not_required_to_stay_ready(self):
        value = state(
            self.anchor,
            packets=[{"id": "P17", "tickets": [17], "title": "", "outcome": ""}],
        )
        code, _, _ = self.run_scan(
            [self.map_issue(value), issue(17, state="closed")]
        )
        self.assertEqual(code, map_scan.CLEAN)

    def test_an_explicitly_excluded_ready_ticket_is_not_unmapped(self):
        value = state(
            self.anchor,
            exclusions=[{"ticket": 42, "why": "not implementation work"}],
        )
        code, _, _ = self.run_scan(
            [self.map_issue(value), issue(42, labels=["ready-for-agent"])]
        )
        self.assertEqual(code, map_scan.CLEAN)

    def test_pull_requests_are_not_ready_tickets(self):
        value = state(self.anchor)
        pull = issue(42, labels=["ready-for-agent"])
        pull["pull_request"] = {"url": "https://example.invalid/pulls/42"}
        code, _, _ = self.run_scan([self.map_issue(value), pull])
        self.assertEqual(code, map_scan.CLEAN)


class ReconciliationObligation(ScannerCase):
    def add_adr_commit(self):
        path = self.root / "docs" / "adr" / "0001-decision.md"
        path.write_text("# Decision\n", encoding="utf-8")
        subprocess.run(["git", "add", str(path)], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "add ADR"], cwd=self.root, check=True)

    def test_an_adr_after_the_anchor_is_a_finding(self):
        self.add_adr_commit()
        code, stdout, _ = self.run_scan([self.map_issue(state(self.anchor))])
        self.assertEqual(code, map_scan.FOUND)
        self.assertIn("unreconciled-adr", stdout)
        self.assertIn("ticket #596", stdout)
        self.assertNotIn("Decision", stdout)

    def test_a_missing_anchor_is_not_a_clean_scan(self):
        value = state(self.anchor)
        del value["reconciled_through"]
        code, _, stderr = self.run_scan([self.map_issue(value)])
        self.assertEqual(code, map_scan.NOT_SCANNED)
        self.assertIn("reconciled_through", stderr)

    def test_a_git_failure_is_not_scanned(self):
        value = state("not-a-commit")
        code, _, stderr = self.run_scan([self.map_issue(value)])
        self.assertEqual(code, map_scan.NOT_SCANNED)
        self.assertIn("git log", stderr)


class PointerAndStatus(ScannerCase):
    def test_a_state_block_mention_is_not_the_maintenance_pointer(self):
        value = state(
            self.anchor,
            packets=[{
                "id": "P679",
                "tickets": [679],
                "title": "",
                "outcome": "add tools/map_scan.py and map_scan.DECLARED_LIMITS",
            }],
        )
        code, stdout, _ = self.run_scan(
            [self.map_issue(value, pointer=False), issue(679, labels=["ready-for-agent"])]
        )
        self.assertEqual(code, map_scan.FOUND)
        self.assertIn("missing-limits-pointer", stdout)

    def test_a_pointer_outside_the_maintenance_rule_does_not_count(self):
        value = state(self.anchor)
        body = map_body(value, pointer=False).replace(
            "Maintenance asks somebody to remember the reconciliation.",
            "Maintenance asks somebody to remember the reconciliation.\n\n"
            "## Notes\n`tools/map_scan.py` and `map_scan.DECLARED_LIMITS`",
        )
        code, stdout, _ = self.run_scan([issue(596, body=body)])
        self.assertEqual(code, map_scan.FOUND)
        self.assertIn("missing-limits-pointer", stdout)

    def test_advisory_converts_a_finding_to_success(self):
        code, stdout, _ = self.run_scan(
            [self.map_issue(state(self.anchor)), issue(42, labels=["ready-for-agent"])],
            "--advisory",
        )
        self.assertEqual(code, map_scan.CLEAN)
        self.assertIn("unmapped-ready", stdout)

    def test_advisory_does_not_convert_not_scanned(self):
        value = state(self.anchor)
        del value["reconciled_through"]
        code, _, _ = self.run_scan([self.map_issue(value)], "--advisory")
        self.assertEqual(code, map_scan.NOT_SCANNED)

    def test_advisory_converts_a_mixed_result_because_findings_win(self):
        value = state("not-a-commit")
        code, stdout, stderr = self.run_scan(
            [self.map_issue(value), issue(42, labels=["ready-for-agent"])],
            "--advisory",
        )
        self.assertEqual(code, map_scan.CLEAN)
        self.assertIn("unmapped-ready", stdout)
        self.assertIn("git log", stderr)

    def test_a_finding_wins_when_git_could_not_run(self):
        value = state("not-a-commit")
        code, stdout, stderr = self.run_scan(
            [self.map_issue(value), issue(42, labels=["ready-for-agent"])]
        )
        self.assertEqual(code, map_scan.FOUND)
        self.assertIn("unmapped-ready", stdout)
        self.assertIn("git log", stderr)

    def test_report_never_prints_a_title_or_body(self):
        secret = "SECRET-BODY-AND-TITLE"
        code, stdout, stderr = self.run_scan(
            [
                self.map_issue(state(self.anchor)),
                issue(42, labels=["ready-for-agent"], body=secret, title=secret),
            ]
        )
        self.assertEqual(code, map_scan.FOUND)
        self.assertNotIn(secret, stdout + stderr)


class InvalidHarvests(ScannerCase):
    def test_no_argument_is_not_scanned(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = map_scan.main([], repo_root=self.root)
        self.assertEqual(code, map_scan.NOT_SCANNED)

    def test_absent_unparseable_empty_and_wrong_shape_are_not_scanned(self):
        cases = {
            "absent": self.root / "absent.json",
            "unparseable": self.root / "unparseable.json",
            "empty": self.root / "empty.json",
            "object": self.root / "object.json",
        }
        cases["unparseable"].write_text("{", encoding="utf-8")
        cases["empty"].write_text("[]", encoding="utf-8")
        cases["object"].write_text("{}", encoding="utf-8")
        for name, path in cases.items():
            with self.subTest(name=name):
                with contextlib.redirect_stderr(io.StringIO()):
                    code = map_scan.main([str(path)], repo_root=self.root)
                self.assertEqual(code, map_scan.NOT_SCANNED)

    def test_zero_or_several_map_issues_are_not_scanned(self):
        value = state(self.anchor)
        for rows in ([], [self.map_issue(value), self.map_issue(value, number=597)]):
            with self.subTest(count=len(rows)):
                path = self.write_harvest(rows, f"issues-{len(rows)}.json")
                with contextlib.redirect_stderr(io.StringIO()):
                    code = map_scan.main([str(path)], repo_root=self.root)
                self.assertEqual(code, map_scan.NOT_SCANNED)

    def test_a_state_marker_on_an_issue_other_than_596_is_not_the_map(self):
        path = self.write_harvest([self.map_issue(state(self.anchor), number=597)])
        with contextlib.redirect_stderr(io.StringIO()):
            code = map_scan.main([str(path)], repo_root=self.root)
        self.assertEqual(code, map_scan.NOT_SCANNED)


class DeclaredLimitsAreBound(unittest.TestCase):
    def test_the_docstring_and_claude_point_to_the_object_without_copying_rows(self):
        prose = Path(__file__).resolve().parents[1].joinpath("CLAUDE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("map_scan.DECLARED_LIMITS", map_scan.__doc__)
        self.assertIn("map_scan.DECLARED_LIMITS", prose)
        for row in map_scan.DECLARED_LIMITS:
            with self.subTest(key=row.key):
                self.assertNotIn(row.limit, map_scan.__doc__)
                self.assertNotIn(row.limit, prose)


if __name__ == "__main__":
    unittest.main()
