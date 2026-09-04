"""Tests for the declined interval-reach discriminators from ADR 0028."""

from __future__ import annotations

import unittest
from pathlib import Path

import artifact_lock_test_support  # noqa: F401

import uspstf_interval_reach as reach


TESTDATA = Path(__file__).resolve().parent / "testdata" / "uspstf"


class TheDeclinedRegionRuleFiresOnKnownWrongDocuments(unittest.TestCase):
    """A later proposal must confront the false positives that ruled widening out."""

    def test_the_region_rule_fires_on_both_committed_excerpts(self) -> None:
        fixtures = (
            "screening-anxiety-children.txt",
            "latent-tuberulosis.txt",
        )

        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                text = (TESTDATA / fixture).read_text(encoding="utf-8")
                self.assertTrue(reach.declined_region_phrases(text))


class TheInstrumentCountsEachPopulationOnce(unittest.TestCase):
    def test_counts_are_by_file_even_when_one_file_has_several_hits(self) -> None:
        rows = (
            reach.TableRow("one.pdf", "not stated", "No period here."),
            reach.TableRow("one.pdf", "not stated", "Still no period."),
            reach.TableRow("two.pdf", "annual", "Annual screening."),
        )
        documents = {
            "one.pdf": """Screening Intervals
The USPSTF found no evidence on an interval. Repeated screening may be useful.
Treatment
The USPSTF suggests annual screening in a different population.
""",
            "two.pdf": "Annual screening.",
        }

        measurement = reach.measure(rows, documents)

        self.assertEqual(measurement.rows, 3)
        self.assertEqual(measurement.not_stated_rows, 2)
        self.assertEqual(measurement.files_with_not_stated, 1)
        self.assertEqual(measurement.naive_files, 1)
        self.assertEqual(measurement.region_files, 1)
        self.assertEqual(measurement.attributed_files, 1)
        self.assertEqual(measurement.unhedged_files, 1)
        self.assertEqual(measurement.naive_absence_files, 1)
        self.assertEqual(measurement.committed_absence_files, 0)

    def test_a_phrase_already_carried_by_a_sibling_row_is_not_new(self) -> None:
        rows = (
            reach.TableRow("mixed.pdf", "not stated", "No period here."),
            reach.TableRow("mixed.pdf", "annual", "Annual screening."),
        )
        documents = {"mixed.pdf": "Annual screening."}

        measurement = reach.measure(rows, documents)

        self.assertEqual(measurement.files_with_not_stated, 1)
        self.assertEqual(measurement.naive_files, 0)

    def test_candidate_census_reports_overlap_with_the_committed_reading(self) -> None:
        named = reach.INTERVAL_ABSENCES[0].filename
        rows = (reach.TableRow(named, "not stated", "No period here."),)
        documents = {
            named: "The USPSTF found no evidence on appropriate screening intervals.",
            "new.pdf": "The USPSTF found no evidence to determine screening frequency.",
        }

        measurement = reach.measure(rows, documents)

        self.assertEqual(measurement.naive_absence_files, 2)
        self.assertEqual(measurement.committed_absence_files, 1)


if __name__ == "__main__":
    unittest.main()
