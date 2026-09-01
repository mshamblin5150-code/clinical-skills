"""Word calibration command and the Word-free tripwires for APA renderer claims."""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path

import docx_word_probe
import docx_write


class EverySectionSixRowHasACalibrationIdentity(unittest.TestCase):
    SHEET = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "practicum-case-study"
        / "reference"
        / "apa7.md"
    )

    def section_rows(self):
        text = self.SHEET.read_text(encoding="utf-8")
        section = text[text.index("## 6.") : text.index("## 7.")]
        applied, not_applied = section.split("still not applied", 1)
        return docx_write.table_first_cells(applied) + docx_write.table_first_cells(
            not_applied
        )

    def test_every_documented_row_has_one_distinct_calibration(self):
        rows = self.section_rows()
        matched = []
        for spec in docx_word_probe.CALIBRATIONS:
            hits = [row for row in rows if spec.row_phrase in row]
            self.assertEqual(hits, [hits[0]] if hits else [], spec.key)
            matched.extend(hits)

        self.assertCountEqual(matched, rows)
        self.assertEqual(
            len({spec.key for spec in docx_word_probe.CALIBRATIONS}), len(rows)
        )

    def test_each_row_prints_its_calibration_key_once(self):
        text = self.SHEET.read_text(encoding="utf-8")
        section = text[text.index("## 6.") : text.index("## 7.")]
        for spec in docx_word_probe.CALIBRATIONS:
            self.assertEqual(section.count("`" + spec.key + "`"), 1, spec.key)


class EveryCalibrationHasAWordFreeRendererShape(unittest.TestCase):
    def test_the_current_renderer_reports_one_nonempty_shape_per_row(self):
        shapes = docx_word_probe.renderer_shapes()
        self.assertEqual(
            set(shapes), {spec.key for spec in docx_word_probe.CALIBRATIONS}
        )
        for key, shape in shapes.items():
            with self.subTest(key=key):
                self.assertIsInstance(shape, dict)
                self.assertTrue(shape)


class TheCommittedWordMeasurement(unittest.TestCase):
    RECORD = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "practicum-case-study"
        / "reference"
        / "word-renderer-calibration.json"
    )

    def test_every_row_records_its_word_measurement_and_covered_xml_shape(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        specs = {spec.key: spec for spec in docx_word_probe.CALIBRATIONS}
        self.assertEqual(set(record["rows"]), set(specs))
        for key, row in record["rows"].items():
            with self.subTest(key=key):
                self.assertEqual(row["measured_on"], "2026-08-22")
                self.assertEqual(row["word_version"], "16.0")
                self.assertTrue(row["word_build"])
                self.assertEqual(row["verdict"], specs[key].verdict)
                self.assertTrue(row["word_observation"])
                self.assertTrue(row["renderer_shape"])

    def test_the_measurement_still_covers_every_shape_this_renderer_emits(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        expected = {
            key: row["renderer_shape"] for key, row in record["rows"].items()
        }
        self.assertEqual(
            docx_word_probe.renderer_shapes(),
            expected,
            "the renderer emits a shape outside the Word 16.0 measurement; "
            "retake the affected row with docx_word_probe.py --word",
        )

    def test_the_word_save_guard_limit_is_recorded_from_the_same_instrument(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        guard = record["word_save_guard"]
        self.assertEqual(guard["measured_on"], "2026-09-01")
        self.assertEqual(guard["word_version"], "16.0")
        self.assertTrue(guard["word_build"])
        self.assertFalse(guard["original_and_saved_part_sets_equal"])
        self.assertTrue(guard["destination_guard_would_refuse"])
        self.assertTrue(guard["observed_added_parts"])
        self.assertTrue(guard["comparison_observation_added_parts"])
        self.assertIn("probe edits the document", guard["observation"])
        self.assertIn("unedited-but-dirty", guard["observation"])

    def test_the_declined_word_part_allowlist_disagrees_with_its_second_observation(self):
        """Executable record of ADR 0086's refused predicate.

        The candidate recognizes a saved document when it is a superset of the
        renderer's parts and every extra part appeared in the calibration probe. Its
        second recorded observation falsifies that known-extra set.
        """
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        guard = record["word_save_guard"]
        known_word_parts = frozenset(guard["observed_added_parts"])

        def declined_allowlist(added_parts):
            saved_parts = docx_write.PART_NAMES | frozenset(added_parts)
            return (
                saved_parts.issuperset(docx_write.PART_NAMES)
                and saved_parts - docx_write.PART_NAMES <= known_word_parts
            )

        first = declined_allowlist(guard["observed_added_parts"])
        second = declined_allowlist(guard["comparison_observation_added_parts"])
        self.assertTrue(first)
        self.assertFalse(second)
        self.assertNotEqual(first, second)

    def test_the_heading_clipboard_measurements_are_dated_and_versioned(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        specs = {spec.key: spec for spec in docx_word_probe.PASTE_CALIBRATIONS}
        self.assertEqual(set(record["paste_rows"]), set(specs))
        for key, row in record["paste_rows"].items():
            with self.subTest(key=key):
                self.assertEqual(row["measured_on"], "2026-08-22")
                self.assertEqual(row["word_version"], "16.0")
                self.assertTrue(row["word_build"])
                self.assertEqual(row["verdict"], specs[key].verdict)
                self.assertTrue(row["word_observation"])
                self.assertTrue(row["renderer_shape"])

    def test_the_heading_measurement_still_covers_both_renderer_shapes(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        expected = {
            key: row["renderer_shape"]
            for key, row in record["paste_rows"].items()
        }
        self.assertEqual(docx_word_probe.paste_renderer_shapes(), expected)


class TheMaintainerCommand(unittest.TestCase):
    def test_word_mode_has_one_probe_for_every_calibration(self):
        self.assertEqual(
            set(docx_word_probe.PROBES),
            {spec.key for spec in docx_word_probe.CALIBRATIONS},
        )
        self.assertEqual(
            set(docx_word_probe.PASTE_PROBES),
            {spec.key for spec in docx_word_probe.PASTE_CALIBRATIONS},
        )

    def test_shape_mode_prints_the_word_free_side_without_opening_word(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = docx_word_probe.main(["--shapes"])

        self.assertEqual(status, 0)
        report = json.loads(output.getvalue())
        self.assertEqual(
            set(report["rows"]), {spec.key for spec in docx_word_probe.CALIBRATIONS}
        )
        self.assertEqual(report["instrument"], "renderer XML shape only; Word not opened")
        self.assertEqual(
            set(report["paste_rows"]),
            {spec.key for spec in docx_word_probe.PASTE_CALIBRATIONS},
        )


if __name__ == "__main__":
    unittest.main()
