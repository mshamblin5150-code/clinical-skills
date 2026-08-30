"""Public-command tests for the threshold-topic coverage registry from issue #429."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "tools" / "threshold_coverage.py"
sys.path.insert(0, str(ROOT / "tools"))
import threshold_sheet  # noqa: E402


CATALOG = """| society | filename | title | topic | population | year | page_count | class | citation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| USPSTF | first.pdf | First | cervical cancer | adults | 2018 | 10 | recommendation-statement | ? |
| AHA ACC | second.pdf | Second | hypertension | adults | 2025 | 20 | guideline | ? |
| AHA ACC | third.pdf | Third | hypertension | adults | 2024 | 18 | guideline | ? |
"""

NON_SOURCE_CATALOG = CATALOG + (
    "| KDIGO | scope.pdf | Scope | heart failure in chronic kidney disease | "
    "adults | 2026 | 9 | scope-of-work | ? |\n"
)


def registry(*rows: str) -> str:
    return """# Threshold-sheet coverage

<!-- schema: threshold-coverage/2 -->

| topic | state | artifact | record |
| --- | --- | --- | --- |
""" + "".join(rows)


def artifact(read: str) -> str:
    remaining_read = "read 2026-08-23" if read == "yes" else read
    return f"""# Cervical cancer

<!-- schema: threshold-sheet/2 -->

## Sources

| key | society | document | source class | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| first | USPSTF | USPSTF/first | recommendation-statement | 2018 | 2018 | https://example.invalid | exact |

## Scope

extraction identity: producer 0000000000000000000000000000000000000000; tools/guidelines_extract.py sha256 0000000000000000000000000000000000000000000000000000000000000000

**Read:** recommendation statement.

**Not read:** as declared below.

| span | pages | read |
| --- | --- | --- |
| recommendation statement | 1 | yes |
| remaining document | 2-10 | {remaining_read} |

## Populations

| key | verbatim |
| --- | --- |
| adults | adults |

## Quantities

| key | verbatim |
| --- | --- |
| interval | interval |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| interval | adults | 3 years | "every 3 years" | first | p1 | p1/rec/1 | B |
"""


def null_artifact() -> str:
    return artifact("yes").replace(
        "**Not read:** as declared below.",
        "**Not read:** nothing in the source page range.",
    ).replace(
        "| recommendation statement | 1 | yes |",
        "| recommendation statement | 1 | read 2026-08-29 |",
    ).replace(
        "| quantity | population | value | snippet | source | page | rec | class |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| interval | adults | 3 years | \"every 3 years\" | first | p1 | p1/rec/1 | B |",
        threshold_sheet.NONE_DECLARATION,
    )


def non_source_artifact(pages: str = "1-9") -> str:
    return f"""# Heart failure in chronic kidney disease

<!-- schema: threshold-sheet/2 -->

## Sources

| key | society | document | source class | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scope | KDIGO | KDIGO/scope | scope-of-work | 2026 | 2026 | https://example.invalid | bound |

## Scope

extraction identity: producer {'0' * 40}; tools/guidelines_extract.py sha256 {'0' * 64}

**Read:** all source pages.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| scope of work | {pages} | read 2026-08-29 |

## Thresholds

{threshold_sheet.NON_SOURCE_DECLARATION}
"""


class ThresholdCoverageCli(unittest.TestCase):
    def run_cli(
        self, catalog_text: str, coverage_text: str | None, *extra: str
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.md"
            coverage = root / "coverage.md"
            sheets = root / "thresholds"
            catalog.write_text(catalog_text, encoding="utf-8")
            sheets.mkdir()
            if coverage_text is not None:
                coverage.write_text(coverage_text, encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "--catalog",
                    str(catalog),
                    "--coverage",
                    str(coverage),
                    "--sheet-root",
                    str(sheets),
                    *extra,
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

    def test_draft_derives_one_row_per_distinct_catalog_topic(self):
        result = self.run_cli(CATALOG, None, "--draft")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("| cervical cancer |"), 1)
        self.assertEqual(result.stdout.count("| hypertension |"), 1)
        self.assertIn("<!-- schema: threshold-coverage/2 -->", result.stdout)

    def test_a_complete_registry_reports_rederived_state_counts(self):
        result = self.run_cli(
            CATALOG,
            registry(
                "| cervical cancer | unread |  | pending |\n",
                "| hypertension | unread |  | blocked on #436 |\n",
            ),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "topics     2 from 3 catalog rows\n"
            "sheet      0   artifacts   0\n"
            "none       0   artifacts   0   -- every span retired on a marker or a class exemption; no row carries a gated citation\n"
            "non-source 0   artifacts   0   -- every span retired; source form is in the declared non-source class set\n"
            "unread     2   artifacts   0\n",
        )

    def test_scope_of_work_derives_non_source_before_the_zero_row_fork(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "thresholds"
            sheets.mkdir()
            (sheets / "heart-failure.md").write_text(non_source_artifact(), encoding="utf-8")
            result = self.run_cli(
                NON_SOURCE_CATALOG,
                registry(
                    "| cervical cancer | unread |  | pending |\n",
                    "| heart failure in chronic kidney disease | non-source | heart-failure.md | source is a scope of work; all pages read |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )
            wrong_state = self.run_cli(
                NON_SOURCE_CATALOG,
                registry(
                    "| cervical cancer | unread |  | pending |\n",
                    "| heart failure in chronic kidney disease | none | heart-failure.md | all pages read |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"(?m)^non-source\s+1\s+artifacts\s+1")
        self.assertEqual(wrong_state.returncode, 1)
        self.assertIn("derived state 'non-source'", wrong_state.stderr)

    def test_scope_of_work_needs_full_page_coverage_to_derive_non_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "thresholds"
            sheets.mkdir()
            (sheets / "heart-failure.md").write_text(
                non_source_artifact("1-8"), encoding="utf-8"
            )
            result = self.run_cli(
                NON_SOURCE_CATALOG,
                registry(
                    "| cervical cancer | unread |  | pending |\n",
                    "| heart failure in chronic kidney disease | unread | heart-failure.md | incomplete read |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("zero-row artifact", result.stderr)
        self.assertIn("does not cover every catalog page", result.stderr)

    def test_a_full_coverage_null_sheet_derives_none(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "thresholds"
            sheets.mkdir()
            (sheets / "cervical.md").write_text(null_artifact(), encoding="utf-8")
            result = self.run_cli(
                CATALOG,
                registry(
                    "| cervical cancer | none | cervical.md | all pages read; no decision point |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"(?m)^none\s+1\s+artifacts\s+1")

    def test_a_null_sheet_stranded_under_unread_refuses_as_derived_none(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "thresholds"
            sheets.mkdir()
            (sheets / "cervical.md").write_text(null_artifact(), encoding="utf-8")
            result = self.run_cli(
                CATALOG,
                registry(
                    "| cervical cancer | unread | cervical.md | state not promoted |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("state 'unread'", result.stderr)
        self.assertIn("derived state 'none'", result.stderr)

    def test_a_none_row_over_a_populated_sheet_refuses_as_derived_sheet(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "thresholds"
            sheets.mkdir()
            (sheets / "cervical.md").write_text(artifact("yes"), encoding="utf-8")
            result = self.run_cli(
                CATALOG,
                registry(
                    "| cervical cancer | none | cervical.md | wrong null claim |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("state 'none'", result.stderr)
        self.assertIn("derived state 'sheet'", result.stderr)

    def test_source_class_query_rederives_topics_without_a_registry(self):
        result = self.run_cli(
            NON_SOURCE_CATALOG,
            None,
            "--source-class", "scope-of-work",
            "--source-class", "draft",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "source class\ttopic\n"
            "scope-of-work\theart failure in chronic kidney disease\n",
        )

    def test_missing_topic_duplicate_topic_and_unknown_state_refuse(self):
        result = self.run_cli(
            CATALOG,
            registry(
                "| cervical cancer | pending |  | later |\n",
                "| cervical cancer | none |  | guideline read; no decision point |\n",
            ),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate topic 'cervical cancer'", result.stderr)
        self.assertIn("missing topic 'hypertension'", result.stderr)
        self.assertIn("unknown state 'pending'", result.stderr)

    def test_positive_states_require_records_and_artifacts(self):
        result = self.run_cli(
            CATALOG,
            registry(
                "| cervical cancer | none |  | full-document read complete |\n",
                "| hypertension | non-source |  |  |\n",
            ),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("state 'none' has no artifact", result.stderr)
        self.assertIn("state 'non-source' has no artifact", result.stderr)
        self.assertIn("state 'non-source' has no record", result.stderr)

    def test_an_unread_topic_may_register_a_partial_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.md"
            coverage = root / "coverage.md"
            sheets = root / "thresholds"
            catalog.write_text(CATALOG, encoding="utf-8")
            sheets.mkdir()
            (sheets / "cervical.md").write_text(artifact("no"), encoding="utf-8")
            coverage.write_text(
                registry(
                    "| cervical cancer | unread | cervical.md | full-document read pending |\n",
                    "| hypertension | unread |  | blocked on #436 |\n",
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(COMMAND),
                    "--catalog",
                    str(catalog),
                    "--coverage",
                    str(coverage),
                    "--sheet-root",
                    str(sheets),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        state_artifacts = [
            int(re.search(r"artifacts\s+(\d+)", line).group(1))
            for line in result.stdout.splitlines()
            if "artifacts" in line
        ]
        self.assertEqual(state_artifacts, [0, 0, 0, 1])
        self.assertEqual(sum(state_artifacts), 1)

    def test_sheet_state_refuses_an_artifact_with_an_unread_span(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "thresholds"
            sheets.mkdir()
            (sheets / "cervical.md").write_text(artifact("no"), encoding="utf-8")
            result = self.run_cli(
                CATALOG,
                registry(
                    "| cervical cancer | sheet | cervical.md | complete |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("state 'sheet'", result.stderr)
        self.assertIn("derived state 'unread'", result.stderr)

    def test_registry_state_is_not_bound_to_an_artifact_that_fails_schema(self):
        malformed = artifact("yes").replace(
            "| remaining document | 2-10 | read 2026-08-23 |",
            "| remaining document | 2-10 | banana |",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "thresholds"
            sheets.mkdir()
            (sheets / "cervical.md").write_text(malformed, encoding="utf-8")
            result = self.run_cli(
                CATALOG,
                registry(
                    "| cervical cancer | sheet | cervical.md | complete |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("fails threshold-sheet/2 schema", result.stderr)
        self.assertIn("invalid read value", result.stderr)

    def test_a_complete_artifact_stranded_under_unread_refuses(self):
        """The second direction reproduces #455 rather than only asserting symmetry."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "thresholds"
            sheets.mkdir()
            (sheets / "cervical.md").write_text(artifact("yes"), encoding="utf-8")
            result = self.run_cli(
                CATALOG,
                registry(
                    "| cervical cancer | unread | cervical.md | state not promoted |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("state 'unread'", result.stderr)
        self.assertIn("derived state 'sheet'", result.stderr)

    def test_an_overlapping_unread_span_keeps_the_artifact_partial(self):
        overlapping = artifact("yes").replace(
            "| remaining document | 2-10 | read 2026-08-23 |",
            "| remaining document | 2-10 | read 2026-08-23 |\n"
            "| rationale | 1-10 | no |",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "thresholds"
            sheets.mkdir()
            (sheets / "cervical.md").write_text(overlapping, encoding="utf-8")
            result = self.run_cli(
                CATALOG,
                registry(
                    "| cervical cancer | unread | cervical.md | rationale pending |\n",
                    "| hypertension | unread |  | pending |\n",
                ),
                "--sheet-root", str(sheets),
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_the_committed_registry_audits_against_the_committed_catalog_and_sheets(self):
        result = subprocess.run(
            [sys.executable, str(COMMAND)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"(?m)^topics\s+169 from 179 catalog rows$")


if __name__ == "__main__":
    unittest.main()
