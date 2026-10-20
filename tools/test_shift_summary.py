"""The summary agrees with tier counts and absent evidence stays incomplete."""

# phi-scan: synthetic

import artifact_lock_test_support
import tempfile
import unittest
import artifact_lock_test_support
from pathlib import Path

import shift_summary
from prose_bind import NAMING, bind


class GenerationSummary(unittest.TestCase):
    def test_limits_are_named_without_copying(self):
        surface = (Path(__file__).resolve().parents[1] / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual((), bind(shift_summary.DECLARED_LIMITS, surface, mode=NAMING))

    def test_numbered_items_wrap_and_empty_blocks(self):
        counts = shift_summary.generation("FILLED·asserted  1. History\n  wrapped.\nFILLED·asserted  2. Vitals\nFILLED·proposed  1. Antibiotic\n  continuation.\nFILLED·proposed  2. Recheck\nFLAG  issue\n")
        self.assertEqual((2, 2), (len(counts["asserted"]), len(counts["proposed"])))
        self.assertEqual((), shift_summary.generation("FILLED·proposed  none\n")["proposed"])
        self.assertEqual(1, len(shift_summary.generation("FILLED·proposed  1. Recheck\n---\n1. Other content\n")["proposed"]))

    def test_summary_missing_mismatch_duplicate_and_private_names(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            note = run / "note-3.md"
            note.write_text("FILLED·asserted  Vitals\nFILLED·proposed  Antibiotic\n", encoding="utf-8")
            failed, incomplete, report = shift_summary.check(run, (note,), True)
            self.assertFalse(failed)
            self.assertTrue(incomplete)
            self.assertNotIn("Antibiotic", report)
            expected = "GENERATION: note-3.md | FILLED·asserted=1 | FILLED·proposed=1\n"
            self.assertEqual(expected.rstrip(), report.splitlines()[0])
            summary = run / "shift-summary.md"
            summary.write_text(expected, encoding="utf-8")
            self.assertEqual((False, False), shift_summary.check(run, (note,), True)[:2])
            self.assertIn("Antibiotic", shift_summary.check(run, (note,), True, True)[2])
            for text in ("", expected.replace("proposed=1", "proposed=0"), expected * 2):
                summary.write_text(text, encoding="utf-8")
                self.assertEqual((True, False), shift_summary.check(run, (note,), True)[:2])

    def test_private_names_are_display_labels_but_summary_matches_real_names(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            private = run / "HAND-NAMED-MARKER.md"
            numbered = run / "NOTE-7.MD"
            for note in (private, numbered):
                note.write_text("FILLED·asserted  Vitals\n", encoding="utf-8")
            paths = (private, numbered)
            summary = run / "shift-summary.md"
            real = (
                "GENERATION: HAND-NAMED-MARKER.md | FILLED·asserted=1 | FILLED·proposed=0\n"
                "GENERATION: NOTE-7.MD | FILLED·asserted=1 | FILLED·proposed=0\n"
            )
            summary.write_text(real, encoding="utf-8")
            failed, incomplete, report = shift_summary.check(run, paths, True)
            self.assertEqual((False, False), (failed, incomplete))
            self.assertEqual(
                "GENERATION: file 1 of 2 | FILLED·asserted=1 | FILLED·proposed=0\n"
                "GENERATION: NOTE-7.MD | FILLED·asserted=1 | FILLED·proposed=0\n"
                "the shift summary: clean", report,
            )
            self.assertEqual(real + "the shift summary: clean", shift_summary.check(run, paths, True, True)[2])
            for wrong in (real.replace("HAND-NAMED-MARKER.md", "file 1 of 2"), real.replace("asserted=1", "asserted=0")):
                summary.write_text(wrong, encoding="utf-8")
                self.assertEqual((True, False), shift_summary.check(run, paths, True)[:2])


if __name__ == "__main__":
    unittest.main()
