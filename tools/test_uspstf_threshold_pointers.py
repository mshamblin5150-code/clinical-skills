"""Bind shipped threshold pointers to the catalog/coverage join, without a corpus.

This checks pointer derivation and target existence, not agreement between a
recommendation and its linked sheet. The pipe reader covers the producer's current
nine-column table; the public curated reader independently checks its row count.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import artifact_lock_test_support  # noqa: F401

import guidelines_recs
import uspstf_table


REFERENCE = Path(__file__).resolve().parent.parent / "reference"
TABLE = REFERENCE / "guidelines-uspstf.md"


def recommendation_cells(markdown: str) -> list[list[str]]:
    markdown = "\n".join(markdown.splitlines())
    section = markdown.split("## Recommendations\n", 1)[1].split("\n## ", 1)[0]
    return [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in section.splitlines()
        if line.startswith("|")
    ][2:]


class TheCommittedThresholdPointersFollowTheRegistry(unittest.TestCase):
    def assert_pointers_match(self, path: Path) -> None:
        markdown = path.read_text(encoding="utf-8")
        grouped = guidelines_recs.parse_curated_table(markdown)
        sheets = uspstf_table.threshold_sheets_by_filename(
            (REFERENCE / "guidelines-catalog.md").read_text(encoding="utf-8"),
            (REFERENCE / "thresholds" / "coverage.md").read_text(encoding="utf-8"),
        )
        results = [
            uspstf_table.DocumentResult(
                filename,
                rows=[
                    uspstf_table.Row(
                        row.topic, row.population, row.grade, row.interval,
                        row.year, row.filename, row.page, statement=row.statement,
                    )
                    for row in rows
                ],
            )
            for filename, rows in grouped.items()
        ]
        rendered = uspstf_table.render_markdown(results, threshold_sheets=sheets)
        expected = {
            cells[7]: cells[6] for cells in recommendation_cells(rendered)
        }
        cells = recommendation_cells(markdown)
        population = sum(len(rows) for rows in grouped.values())
        self.assertEqual(len(cells), population, "unread recommendation rows")
        self.assertTrue(population, "no recommendation rows checked")
        differences = [
            (index, row[7], row[6], expected[row[7]])
            for index, row in enumerate(cells, start=1)
            if row[6] != expected[row[7]]
        ]
        self.assertEqual(
            len(differences), 0,
            f"{len(differences)} differing threshold-pointer cells across "
            f"{population} rows; unread remainder 0; first differences: {differences[:5]}",
        )
        for filename in grouped:
            if sheet := sheets.get(filename):
                self.assertTrue(
                    (REFERENCE / "thresholds" / sheet).is_file(), sheet,
                )

    def test_every_committed_pointer_matches_the_public_render(self) -> None:
        self.assert_pointers_match(TABLE)

    def test_a_planted_blank_cell_reports_one_difference(self) -> None:
        markdown = TABLE.read_text(encoding="utf-8")
        pointer = next(row[6] for row in recommendation_cells(markdown) if row[6])
        planted = markdown.replace(pointer, "", 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / TABLE.name
            path.write_text(planted, encoding="utf-8")
            with self.assertRaisesRegex(
                AssertionError, "1 differing threshold-pointer cells across 143 rows",
            ):
                self.assert_pointers_match(path)


if __name__ == "__main__":
    unittest.main()
