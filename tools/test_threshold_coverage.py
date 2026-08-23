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

<!-- schema: threshold-coverage/1 -->

| topic | state | record |
| --- | --- | --- |
""" + "".join(rows)


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
        self.assertIn("<!-- schema: threshold-coverage/1 -->", result.stdout)

    def test_a_complete_registry_reports_rederived_state_counts(self):
        result = self.run_cli(
            CATALOG,
            registry(
                "| cervical cancer | none | guideline read; no decision point |\n",
                "| hypertension | unread | blocked on #436 |\n",
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
                "| cervical cancer | pending | later |\n",
                "| cervical cancer | none | guideline read; no decision point |\n",
            ),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate topic 'cervical cancer'", result.stderr)
        self.assertIn("missing topic 'hypertension'", result.stderr)
        self.assertIn("unknown state 'pending'", result.stderr)

    def test_a_state_requires_a_record_and_sheet_state_requires_its_file(self):
        result = self.run_cli(
            CATALOG,
            registry(
                "| cervical cancer | sheet | cervical-cancer.md |\n",
                "| hypertension | unread |  |\n",
            ),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("sheet 'cervical-cancer.md' does not exist", result.stderr)
        self.assertIn("state 'unread' has no record", result.stderr)

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
