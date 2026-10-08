"""The summary agrees with tier counts and absent evidence stays incomplete."""

# phi-scan: synthetic

import tempfile
import unittest
from pathlib import Path

import shift_summary


class GenerationSummary(unittest.TestCase):
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
            summary = run / "shift-summary.md"
            summary.write_text(expected, encoding="utf-8")
            self.assertEqual((False, False), shift_summary.check(run, (note,), True)[:2])
            self.assertIn("Antibiotic", shift_summary.check(run, (note,), True, True)[2])
            for text in ("", expected.replace("proposed=1", "proposed=0"), expected * 2):
                summary.write_text(text, encoding="utf-8")
                self.assertEqual((True, False), shift_summary.check(run, (note,), True)[:2])


if __name__ == "__main__":
    unittest.main()
