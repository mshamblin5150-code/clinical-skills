"""Public-command tests for the APA manual coverage registry from issue #976."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import artifact_lock_test_support  # noqa: F401
import apa7_coverage
import run_grader


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "tools" / "apa7_coverage.py"

SECTION_LIMITS = {2: 28, 4: 30, 5: 10, 6: 52, 7: 36, 8: 36, 9: 52, 10: 16, 11: 10}
MEDIA_LIMITS = {
    2: (3, 5),
    4: (1, 0),
    5: (0, 0),
    6: (5, 0),
    7: (24, 21),
    8: (2, 7),
    9: (1, 4),
    10: (0, 0),
    11: (2, 0),
}
FIRST_DIGEST = "9c187ca7d31f3bf928bad7505e198cb90c52c98d6dd7bb41c36eae0d83e170ec"
SECOND_DIGEST = "4b0df398b9eac122316b0f321be00abea8f5a0ee263469f6ea6f31b380a19d4c"


def expected_items() -> list[str]:
    items = [
        f"{chapter}.{number}"
        for chapter, last in SECTION_LIMITS.items()
        for number in range(1, last + 1)
    ]
    for chapter, (tables, figures) in MEDIA_LIMITS.items():
        items.extend(f"Table {chapter}.{number}" for number in range(1, tables + 1))
        items.extend(f"Figure {chapter}.{number}" for number in range(1, figures + 1))
    return items


def sheet() -> str:
    return """# APA 7

## 1. One

First claim.

## 2. Two

Second claim.
"""


def registry(overrides: dict[str, str] | None = None, *, marker: bool = True) -> str:
    overrides = overrides or {}
    rows = []
    for item in expected_items():
        rows.append(
            overrides.get(
                item,
                f"| {item} | Item {item} | never-checked | — | — | — | — | — |",
            )
        )
    marker_line = (
        "<!-- schema: apa7-coverage/1 -->\n"
        + apa7_coverage.rule_identity_marker()
        + "\n\n"
        if marker
        else ""
    )
    return (
        "# APA 7 manual coverage\n\n"
        + marker_line
        + "| manual item | title | state | checked | evidence | refutation | apa7 sections | digests |\n"
        + "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n"
    )


class Apa7CoverageCli(unittest.TestCase):
    def run_cli(self, sheet_text: str, coverage_text: str, *extra: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheet_path = root / "apa7.md"
            coverage_path = root / "apa7-coverage.md"
            sheet_path.write_text(sheet_text, encoding="utf-8")
            coverage_path.write_text(coverage_text, encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "--sheet",
                    str(sheet_path),
                    "--coverage",
                    str(coverage_path),
                    *extra,
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

    def test_only_coverage_qualifiers_survive_quiet(self):
        result = self.run_cli(
            sheet(),
            registry(
                {
                    "2.1": (
                        f"| 2.1 | One source section | read-root | 2026-09-08 | "
                        "The complete numbered section and owned material were read. | "
                        "A second reader tested whether the sheet omitted or misstated it. | "
                        f"1, 2 | 1={FIRST_DIGEST}; 2={SECOND_DIGEST} |"
                    ),
                    "2.2": (
                        "| 2.2 | Another source section | ruled-out | 2026-09-08 | "
                        "The section was opened and concerns a journal-only submission step. | "
                        "A second reader challenged that boundary and found no student-paper rule. | — | — |"
                    ),
                }
            ),
            "--quiet",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "never-checked  343\n"
            "gone-stale     0\n",
        )

    def test_structural_drift_refuses_in_both_directions(self):
        missing_sheet_section = self.run_cli(
            sheet(),
            registry({"2.1": f"| 2.1 | One | read-root | 2026-09-08 | Read completely. | Refuted independently. | 1 | 1={FIRST_DIGEST} |"}),
        )
        nonexistent_sheet_section = self.run_cli(
            sheet(),
            registry({"2.1": f"| 2.1 | One | read-root | 2026-09-08 | Read completely. | Refuted independently. | 1, 3 | 1={FIRST_DIGEST}; 3={'0' * 64} |"}),
        )

        self.assertEqual(missing_sheet_section.returncode, 1)
        self.assertIn("apa7.md section 2 has no registry row", missing_sheet_section.stderr)
        self.assertEqual(nonexistent_sheet_section.returncode, 1)
        self.assertIn("names nonexistent apa7.md section 3", nonexistent_sheet_section.stderr)

    def test_missing_marker_unknown_state_and_manual_population_drift_refuse(self):
        bad = registry(
            {"2.1": "| 2.1 | One | guessed | 2026-09-08 | Read. | Refuted. | — | — |"},
            marker=False,
        ).replace("| 2.2 | Item 2.2 | never-checked | — | — | — | — | — |\n", "")
        result = self.run_cli(sheet(), bad, "--quiet")

        self.assertEqual(result.returncode, 1)
        self.assertIn("has no <!-- schema: apa7-coverage/1 --> marker", result.stderr)
        self.assertIn("manual item '2.1' has unknown state 'guessed'", result.stderr)
        self.assertIn("missing manual item '2.2'", result.stderr)
        self.assertNotIn("manual items", result.stdout)
        self.assertIn("never-checked  343", result.stdout)

    def test_rule_identity_drift_refuses_with_the_recompute_remedy(self):
        coverage = registry().replace(
            apa7_coverage.rule_identity_marker(),
            "<!-- rule-identity: tools/prose_bind.py sha256=" + "0" * 64 + " -->",
        )

        result = self.run_cli(sheet(), coverage, "--quiet")

        self.assertEqual(result.returncode, 1)
        self.assertIn("prose-bind rule identity has structural drift", result.stderr)
        self.assertIn("recompute the digests", result.stderr)

    def test_checked_rows_require_substantive_evidence_and_refutation(self):
        result = self.run_cli(
            sheet(),
            registry(
                {
                    "2.1": (
                        f"| 2.1 | One | read-root | 2026-09-08 | — | — | "
                        f"1, 2 | 1={FIRST_DIGEST}; 2={SECOND_DIGEST} |"
                    )
                }
            ),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("manual item '2.1' has no substantive evidence", result.stderr)
        self.assertIn("manual item '2.1' has no substantive refutation", result.stderr)

        verdict_only = self.run_cli(
            sheet(),
            registry(
                {
                    "2.1": (
                        f"| 2.1 | One | read-root | 2026-09-08 | Read. | Refuted. | "
                        f"1 | 1={FIRST_DIGEST} |"
                    )
                }
            ),
        )

        self.assertEqual(verdict_only.returncode, 1)
        self.assertIn("manual item '2.1' has no substantive evidence", verdict_only.stderr)
        self.assertIn("manual item '2.1' has no substantive refutation", verdict_only.stderr)

        verbose_verdict_only = self.run_cli(
            sheet(),
            registry(
                {
                    "2.1": (
                        f"| 2.1 | One | read-root | 2026-09-08 | "
                        "Reader opened the source carefully and found this correct today. | "
                        "Independent reader opened source carefully and found this correct today. | "
                        f"1 | 1={FIRST_DIGEST} |"
                    )
                }
            ),
        )

        self.assertEqual(verbose_verdict_only.returncode, 1)
        self.assertIn(
            "manual item '2.1' has no substantive evidence",
            verbose_verdict_only.stderr,
        )
        self.assertIn(
            "manual item '2.1' has no substantive refutation",
            verbose_verdict_only.stderr,
        )

    def test_root_read_requires_a_nonempty_section_and_digest_bind(self):
        result = self.run_cli(
            sheet(),
            registry(
                {
                    "2.1": (
                        "| 2.1 | One | read-root | 2026-09-08 | "
                        "The complete section and all owned material were read carefully. | "
                        "An independent reader tested the interpretation against the source. | — | — |"
                    )
                }
            ),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "manual item '2.1' has no apa7 section and digest bind",
            result.stderr,
        )

    def test_digest_mismatch_reports_staleness_without_structural_refusal(self):
        result = self.run_cli(
            sheet(),
            registry(
                {
                    "2.1": (
                        f"| 2.1 | One | read-root | 2026-09-08 | "
                        "The complete section and its supporting examples were read. | "
                        "An independent reader challenged the interpretation against the source. | 1, 2 | "
                        f"1={'0' * 64}; 2={SECOND_DIGEST} |"
                    )
                }
            ),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("gone-stale     1", result.stdout)
        self.assertIn("STALE: manual item '2.1' bind for apa7.md section 1", result.stderr)
        self.assertIn("read-to-root   0", result.stdout)
        self.assertIn("never-checked  344", result.stdout)

    def test_duplicate_rule_identity_is_structural_drift(self):
        coverage = registry()
        coverage += (
            "\n<!-- rule-identity: tools/prose_bind.py sha256="
            f"{'0' * 64} -->\n"
        )

        _entries, problems = apa7_coverage.parse_registry(coverage)

        self.assertEqual(len(problems), 1)
        self.assertIn("structural drift: duplicate markers", problems[0])
        self.assertIn("recompute the digests", problems[0])

    def test_pre_commit_runs_the_bind_when_either_side_is_staged(self):
        hook = (ROOT / "tools" / "hooks" / "pre-commit").read_text(encoding="utf-8")

        self.assertIn(
            "^skills/_shared/reference/apa7(-coverage)?\\.md$",
            hook,
        )
        self.assertIn(
            '"$python" "$repo_root/tools/apa7_coverage.py" --quiet >&2 || status=1',
            hook,
        )


class DeclaredBoundary(unittest.TestCase):
    def test_the_five_permanent_limits_are_owned(self):
        self.assertEqual(
            set(apa7_coverage.DECLARED_LIMITS),
            {
                "reader-accuracy",
                "out-of-scope-chapters",
                "sequential-census",
                "manual-site-agreement",
                "normalization-rule-identity",
            },
        )

    def test_this_registry_checker_is_not_a_run_grader(self):
        self.assertNotIn("apa7_coverage", run_grader.MEMBERS)


class CommittedRegistry(unittest.TestCase):
    def test_all_345_manual_items_are_current_and_read_to_root(self):
        sheet_text = apa7_coverage.DEFAULT_SHEET.read_text(encoding="utf-8")
        coverage_text = apa7_coverage.DEFAULT_COVERAGE.read_text(encoding="utf-8")
        entries, parse_problems = apa7_coverage.parse_registry(coverage_text)
        failures, stale = apa7_coverage.audit(
            entries, apa7_coverage.sheet_sections(sheet_text)
        )

        self.assertEqual(parse_problems, [])
        self.assertEqual(failures, [])
        self.assertEqual(stale, set())
        self.assertEqual(len(entries), 345)
        self.assertEqual({entry.state for entry in entries}, {"read-root"})


if __name__ == "__main__":
    unittest.main()
