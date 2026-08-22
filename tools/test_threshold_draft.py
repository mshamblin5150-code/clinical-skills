"""Tests for the threshold-sheet draft CLI introduced by issue #403."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import threshold_sheet  # noqa: E402


ROOT = Path(__file__).resolve().parent.parent
COMMAND = ROOT / "tools" / "threshold_draft.py"


def catalog_row(topic: str = "hypertension") -> str:
    return (
        "| society | filename | title | topic | population | year | page_count | class |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        f"| AHA ACC | guideline.pdf | Guideline title | {topic} | adult | 2025 | 12 | guideline |\n"
    )


def recommendation_record() -> dict:
    return {
        "doc_id": "AHA ACC/guideline",
        "source": "C:/corpus/AHA ACC/guideline.pdf",
        "mode": "exact",
        "totals": {"recommendations": 2, "tables": 1},
        "recommendations": [
            {
                "rec_id": "p3/topic/1",
                "page": 3,
                "cor": "1",
                "text": "Adults should have an SBP goal below 130 mm Hg.",
            },
            {
                "rec_id": "p3/topic/2",
                "page": 3,
                "cor": "2a",
                "text": "Use standardized measurement technique.",
            },
        ],
    }


def seeded_sheet() -> str:
    return f"""# Hypertension

{threshold_sheet.SCHEMA_MARKER}

## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| aha-2025 | AHA/ACC | AHA ACC/guideline | 2025 | 2025 | https://example.invalid | exact |

## Scope

**Read:** recommendation tables.

**Not read:** narrative.

## Populations

| key | verbatim |
| --- | --- |
| adults | adults |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bp-goal-sbp | adults | <130 mm Hg | "an SBP goal below 130 mm Hg" | aha-2025 | p3 | p3/topic/1 | 1 |

## Conflicts

## Coverage

- `p3/topic/2` - no decision point
"""


class ThresholdDraftCli(unittest.TestCase):
    def run_cli(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        catalog = root / "catalog.md"
        recs = root / "recs"
        sheets = root / "sheets"
        catalog.write_text(catalog_row(), encoding="utf-8")
        recs.mkdir()
        sheets.mkdir(exist_ok=True)
        (recs / "recs-aha-2025.json").write_text(
            json.dumps(recommendation_record()), encoding="utf-8"
        )
        return subprocess.run(
            [
                sys.executable,
                str(COMMAND),
                "hypertension",
                "--catalog",
                str(catalog),
                "--recs-root",
                str(recs),
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

    def test_a_new_topic_prints_a_skeleton_with_only_machine_cells_filled(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Candidate set", result.stdout)
        self.assertIn("## Rejected candidates", result.stdout)
        self.assertIn("|  |  |  | \"Adults should have an SBP goal below 130 mm Hg.\"", result.stdout)
        self.assertIn("| aha-2025 | p3 | p3/topic/1 | 1 |", result.stdout)
        scope = result.stdout.split("## Scope", 1)[1].split("## ", 1)[0]
        self.assertNotIn("Read:", scope)
        self.assertNotIn("Not read:", scope)
        self.assertIn("| 2 | 2 | 0 |", scope)

    def test_an_existing_curated_sheet_selects_rows_without_copying_judgment_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sheets = root / "sheets"
            sheets.mkdir()
            (sheets / "hypertension.md").write_text(seeded_sheet(), encoding="utf-8")
            result = self.run_cli(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        drafted = threshold_sheet.parse(result.stdout, Path("draft.md"))
        self.assertEqual(len(drafted.rows), 1)
        self.assertEqual(drafted.rows[0].quantity, "")
        self.assertEqual(drafted.rows[0].population, "")
        self.assertEqual(drafted.rows[0].value, "")
        self.assertEqual(drafted.rows[0].snippet, "an SBP goal below 130 mm Hg")
        self.assertEqual(drafted.rows[0].rec, "p3/topic/1")
        self.assertEqual(drafted.scoped_out, {"p3/topic/2": "no decision point"})
        scope = result.stdout.split("## Scope", 1)[1].split("## ", 1)[0]
        self.assertIn("| 2 | 1 | 1 |", scope)
        self.assertNotIn("recommendation tables", result.stdout)

    def test_hypertension_reproduces_the_committed_data_half_when_records_exist(self):
        recs = Path(threshold_sheet.DEFAULT_RECS_ROOT) / "recs-aha-2025.json"
        if not recs.is_file():
            self.skipTest(f"acceptance record not present at {recs}")

        result = subprocess.run(
            [sys.executable, str(COMMAND), "hypertension"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        drafted = threshold_sheet.parse(result.stdout, Path("draft.md"))
        committed_path = ROOT / "reference" / "thresholds" / "hypertension.md"
        committed = threshold_sheet.parse(
            committed_path.read_text(encoding="utf-8"), committed_path
        )
        self.assertEqual(len(drafted.rows), 74)
        self.assertEqual(len({row.rec for row in drafted.rows}), 53)
        self.assertEqual(len(drafted.scoped_out), 50)
        self.assertEqual(
            len({row.rec for row in drafted.rows} | set(drafted.scoped_out)), 103
        )
        self.assertEqual(
            [
                (row.snippet, row.source, row.page, row.rec, row.klass)
                for row in drafted.rows
            ],
            [
                (row.snippet, row.source, row.page, row.rec, row.klass)
                for row in committed.rows
            ],
        )
        self.assertEqual(drafted.sources, committed.sources)
        self.assertEqual(drafted.scoped_out, committed.scoped_out)
        self.assertTrue(all(not row.quantity and not row.population and not row.value for row in drafted.rows))
        scope = result.stdout.split("## Scope", 1)[1].split("## ", 1)[0]
        self.assertNotIn("Read:", scope)
        self.assertNotIn("Not read:", scope)
        self.assertNotIn("quoting posture", result.stdout.casefold())
        self.assertNotIn("Recommendations for", result.stdout)
        self.assertIn("hypertension screening", result.stdout)


if __name__ == "__main__":
    unittest.main()
