"""Public-command tests for the threshold-topic coverage registry from issue #429."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "tools" / "threshold_coverage.py"


CATALOG = """| society | filename | title | topic | population | year | page_count | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| USPSTF | first.pdf | First | cervical cancer | adults | 2018 | 10 | recommendation-statement |
| AHA ACC | second.pdf | Second | hypertension | adults | 2025 | 20 | guideline |
| AHA ACC | third.pdf | Third | hypertension | adults | 2024 | 18 | guideline |
"""


def registry(*rows: str) -> str:
    return """# Threshold-sheet coverage

<!-- schema: threshold-coverage/2 -->

| topic | state | artifact | record |
| --- | --- | --- | --- |
""" + "".join(rows)


def artifact(read: str) -> str:
    return f"""# Cervical cancer

<!-- schema: threshold-sheet/2 -->

## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| first | USPSTF | USPSTF/first | 2018 | 2018 | https://example.invalid | exact |

## Scope

**Read:** recommendation statement.

**Not read:** as declared below.

| span | pages | read |
| --- | --- | --- |
| whole document | 1-10 | {read} |

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
                "| cervical cancer | none |  | guideline read; no decision point |\n",
                "| hypertension | unread |  | blocked on #436 |\n",
            ),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("topics     2", result.stdout)
        self.assertIn("none       1", result.stdout)
        self.assertIn("unread     1", result.stdout)

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

    def test_a_state_requires_a_record_and_sheet_state_requires_an_artifact(self):
        result = self.run_cli(
            CATALOG,
            registry(
                "| cervical cancer | sheet |  | full-document read complete |\n",
                "| hypertension | unread |  |  |\n",
            ),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("state 'sheet' has no artifact", result.stderr)
        self.assertIn("state 'unread' has no record", result.stderr)

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
        self.assertIn("unread span", result.stderr)

    def test_registry_state_is_not_bound_to_an_artifact_that_fails_schema(self):
        malformed = artifact("yes").replace(
            "| whole document | 1-10 | yes |",
            "| whole document | 1-10 | banana |",
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
        self.assertIn("every page", result.stderr)

    def test_an_overlapping_unread_span_keeps_the_artifact_partial(self):
        overlapping = artifact("yes").replace(
            "| whole document | 1-10 | yes |",
            "| recommendation statement | 1-10 | yes |\n"
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
        self.assertRegex(result.stdout, r"(?m)^topics\s+169$")


if __name__ == "__main__":
    unittest.main()
