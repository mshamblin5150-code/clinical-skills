"""Behavior and ownership tests for the guideline split census."""

from __future__ import annotations

import ast
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import guidelines_extract as extract
import split_census as census
from prose_bind import ProseBind


def rawline(text: str, split_at: set[int] = frozenset()) -> dict:
    """One synthetic rawdict line; ``split_at`` names wide incoming gaps."""
    chars = []
    right = 0.0
    for index, glyph in enumerate(text):
        left = right + (2.0 if index in split_at else 0.0)
        right = left + 1.0
        chars.append({"c": glyph, "bbox": (left, 0.0, right, 1.0)})
    return {
        "blocks": [
            {
                "type": 0,
                "lines": [{"spans": [{"size": 10.0, "font": "Text", "chars": chars}]}],
            }
        ]
    }


class ShapeCensusTests(unittest.TestCase):
    def test_a_split_is_recorded_as_run_to_pieces(self):
        result = census.census_rawdict(rawline("1234", {2}))

        self.assertEqual(result.shapes, {"1234 -> 12|34": 1})
        self.assertEqual(result.boundaries["digit|digit"], 1)

    def test_all_five_digit_adjacent_boundary_classes_are_counted(self):
        result = census.Census()
        for text, split_at in (
            ("A1", {1}),
            ("1A", {1}),
            (".1", {1}),
            ("1.", {1}),
            ("12", {1}),
        ):
            result.update(census.census_rawdict(rawline(text, split_at)))

        self.assertEqual(
            result.boundaries,
            {
                "alpha|digit": 1,
                "digit|alpha": 1,
                "punct|digit": 1,
                "digit|punct": 1,
                "digit|digit": 1,
            },
        )

    def test_quantity_shapes_are_digit_digit_or_decimal_and_comma_adjacent(self):
        result = census.Census()
        for text, split_at in (
            ("12", {1}),
            ("0.5", {2}),
            ("1,000", {2}),
            ("S1", {1}),
        ):
            result.update(census.census_rawdict(rawline(text, split_at)))

        self.assertEqual(
            result.quantity_shapes,
            {"12 -> 1|2": 1, "0.5 -> 0.|5": 1, "1,000 -> 1,|000": 1},
        )


class LexiconClassificationTests(unittest.TestCase):
    def test_each_evidence_state_has_its_own_bucket(self):
        lexicon = {"seethe", "see", "the", "contents", "con", "tents"}
        shapes = {
            "seethe -> see|the": 1,
            "contents -> con|tents": 1,
            "primarycare -> primary|care": 1,
            "xylophone -> xylo|phone": 1,
        }

        result = census.classify_shapes(shapes, lexicon)

        self.assertEqual(
            result,
            {"ambiguous": 2, "fix": 0, "wrong": 0, "undecidable": 2},
        )

    def test_known_run_with_unknown_piece_is_wrong_and_known_pieces_fix_unknown_run(self):
        result = census.classify_shapes(
            {"seethe -> se|ethe": 2, "primarycare -> primary|care": 3},
            {"seethe", "primary", "care"},
        )

        self.assertEqual(
            result,
            {"ambiguous": 0, "fix": 3, "wrong": 2, "undecidable": 0},
        )


class CommandTests(unittest.TestCase):
    def test_no_corpus_is_not_a_scan(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stderr(io.StringIO()) as err:
            status = census.main([str(Path(tmp) / "missing")])

        self.assertEqual(status, 2)
        self.assertIn("no corpus", err.getvalue())

    def test_a_missing_pdf_dependency_is_not_a_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "synthetic.pdf").touch()
            with mock.patch.object(
                census.guidelines_extract,
                "require_pymupdf",
                side_effect=SystemExit("pymupdf missing"),
            ), redirect_stderr(io.StringIO()) as err:
                status = census.main([tmp])

        self.assertEqual(status, 2)
        self.assertIn("pymupdf missing", err.getvalue())

    def test_a_quantity_shaped_split_is_a_finding(self):
        measured = census.Census()
        measured.update(census.census_rawdict(rawline("0.5", {2})))
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "synthetic.pdf").touch()
            with mock.patch.object(
                census, "scan_corpus", return_value=measured
            ), redirect_stdout(io.StringIO()) as out:
                status = census.main([tmp])

        self.assertEqual(status, 1)
        self.assertIn("FINDING", out.getvalue())
        self.assertIn("0.5 -> 0.|5", out.getvalue())

    def test_classification_mode_rebuilds_the_lexicon_and_writes_nothing(self):
        measured = census.Census(shapes={"primarycare -> primary|care": 1})
        root = Path(tempfile.mkdtemp())
        (root / "synthetic.pdf").touch()
        with mock.patch.object(census, "scan_corpus", return_value=measured), mock.patch.object(
            census, "harvest_lexicon", return_value={"primary", "care"}
        ) as harvest, redirect_stdout(io.StringIO()):
            status = census.main(["--classify", str(root)])

        self.assertEqual(status, 0)
        harvest.assert_called_once()
        self.assertEqual([path.name for path in root.iterdir()], ["synthetic.pdf"])


class RuleOwnershipTests(unittest.TestCase):
    def test_the_census_calls_the_shared_generator_and_holds_no_gap_rule(self):
        source = Path(census.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "guidelines_extract"
            and node.func.attr == "walk_line_glyphs"
        ]
        forbidden = {
            node.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "guidelines_extract"
            and node.attr in {"SPACE_GAP_FRACTION", "SPACE_GAP_FLOOR", "SPACE_ADVANCE_FRACTION"}
        }

        self.assertTrue(calls)
        self.assertEqual(forbidden, set())

    def test_the_tool_declares_why_it_needs_no_write_guard(self):
        self.assertIn("writes nothing", census.WHY_NO_WRITE_GUARD)


class HistoricalClaimsBind(ProseBind, unittest.TestCase):
    def test_claude_points_at_the_declared_object_and_copies_no_row(self):
        prose = (Path(__file__).resolve().parent.parent / "CLAUDE.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("guidelines_extract.ORPHANED_FIGURES", prose)
        for label, value, _reason in extract.ORPHANED_FIGURES:
            self.assertProseNotIn((label, value), prose)

    def test_historical_shape_figures_bind_the_docstring_and_safety_claim(self):
        prose = (Path(__file__).resolve().parent.parent / "CLAUDE.md").read_text(
            encoding="utf-8"
        )
        module_prose = census.__doc__ or ""
        figures = census.HISTORICAL_SHAPE_FIGURES

        for field in ("occurrences", "distinct_shapes"):
            value = figures[field]
            self.assertIn(f"{value:,}", module_prose)
            self.assertNotIn(f"{value:,}", prose)
        digit_breaks = figures["digit|digit"]
        self.assertIn(f"{digit_breaks:,} ``digit|digit``", module_prose)
        self.assertIn(f"{digit_breaks:,} `digit|digit` breaks", prose)


if __name__ == "__main__":
    unittest.main()
