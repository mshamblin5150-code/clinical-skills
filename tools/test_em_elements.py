"""The E/M element block: its strict reader, and every worksheet reader tolerating it."""
from __future__ import annotations

import artifact_lock_test_support

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import review_manifest
import worksheet_grammar as grammar

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "skills" / "_shared" / "reference" / "em-elements.md"
PRESERVED = ROOT / "fixtures" / "worksheet-grammar-positive-control" / "case-01.md"
BLOCK = """  EM-PROBLEM: definition-stable-chronic | counted | "Diabetes stable" | evaluated and continued
  EM-DATA: none | not counted | none | no test documented
  EM-RISK: table-moderate | counted | "Continue metformin" | prescription drug management
  EM-RULE: ADR 0308 ruling 1
  EM-ANSWER: none
  EM-ECG: not applicable
  EM-MDM: problems low; data straightforward; risk moderate; mdm low
  EM-LEVEL: 99213
"""
EM_LINE = "E/M: 99213 Office or other outpatient visit, established patient, low MDM\n"
EM_CODES = review_manifest.EM_CODES


def astuple_of(elements):
    return elements.block, elements.outside, elements.blocks


class TheStrictReader(unittest.TestCase):
    def test_the_reference_example_is_a_complete_block(self):
        text = REFERENCE.read_text(encoding="utf-8")
        example = text.split("Synthetic example", 1)[1].split("```text", 1)[1].split("```", 1)[0]
        block, outside, _ = astuple_of(grammar.worksheet_em_block(example, EM_CODES))
        self.assertEqual(0, outside)
        self.assertEqual(0, block.unread)
        self.assertEqual(("low", "low"), (block.mdm["mdm"], block.two_of_three()))
        self.assertEqual("99213", block.level)
        self.assertEqual(["note-1.q1"], list(block.answers))
        self.assertEqual({"PROBLEM", "DATA", "RISK"}, {item.kind for item in block.items})

    def test_every_refused_line_and_a_missing_required_line_are_unread(self):
        self.assertEqual(0, grammar.em_block(BLOCK).unread)
        for broken in (BLOCK.replace("| counted |", "| maybe |", 1),
                       BLOCK + "  EM-OPINION: something\n",
                       BLOCK.replace("mdm low", "mdm middling"),
                       BLOCK.replace("EM-ANSWER: none", "EM-ANSWER: the second question"),
                       BLOCK.replace("  EM-LEVEL: 99213\n", ""),
                       BLOCK.replace("  EM-DATA: none | not counted | none | no test documented\n", "")):
            with self.subTest(broken=broken):
                self.assertGreater(grammar.em_block(broken).unread, 0)

    def test_two_of_three_is_the_middle_level(self):
        block = grammar.em_block(BLOCK.replace("problems low; data straightforward; risk moderate",
                                               "problems high; data straightforward; risk moderate"))
        self.assertEqual("moderate", block.two_of_three())

    def test_a_worksheet_without_the_block_stays_valid(self):
        preserved = PRESERVED.read_text(encoding="utf-8")
        self.assertEqual(grammar.WorksheetElements(None, 0, 0), grammar.worksheet_em_block(preserved, EM_CODES))
        self.assertIsNone(grammar.em_block("E/M: 99213 low MDM\nNo element lines here.\n"))

    def test_element_lines_away_from_the_em_line_are_counted_outside(self):
        text = "ICD-10  E11.9  Type 2 diabetes mellitus without complications\n" + BLOCK + "\n" + EM_LINE
        block, outside, _ = astuple_of(grammar.worksheet_em_block(text, EM_CODES))
        self.assertIsNone(block)
        self.assertEqual(len(BLOCK.splitlines()), outside)

    def test_every_anchor_spelling_the_code_reader_accepts_carries_the_block(self):
        for anchor in ("CPT  99213  Office visit, established patient", "cpt 99213 Office",
                       "**E/M**: 99213 low MDM", "e/m: 99213 low MDM", EM_LINE.strip()):
            with self.subTest(anchor=anchor):
                block, outside, blocks = astuple_of(grammar.worksheet_em_block(anchor + "\n" + BLOCK, EM_CODES))
                self.assertEqual((0, 0, "99213", 1), (outside, block.unread, block.level, blocks))
                self.assertEqual("99213", review_manifest.selected_codes(
                    "ICD-10  E11.9  Type 2 diabetes mellitus without complications\n" + anchor + "\n" + BLOCK,
                    private=True)["em"])

    def test_the_block_under_the_second_anchor_is_read_and_two_blocks_are_counted(self):
        entry = "CPT  99213  Office visit, established patient\n"
        block, outside, blocks = astuple_of(grammar.worksheet_em_block(entry + "\n" + EM_LINE + BLOCK, EM_CODES))
        self.assertEqual((0, 1, "99213"), (outside, blocks, block.level))
        _, _, blocks = astuple_of(grammar.worksheet_em_block(entry + BLOCK + "\n" + EM_LINE + BLOCK, EM_CODES))
        self.assertEqual(2, blocks)

    def test_r6_a_nested_em_line_inside_a_cpt_entry_counts_each_element_line_once(self):
        text = "CPT  99213  Office visit, established patient\n  E/M: 99213 low MDM\n" + BLOCK
        block, outside, blocks = astuple_of(grammar.worksheet_em_block(text, EM_CODES))
        self.assertEqual((0, 1, 0), (outside, blocks, block.unread))

    def test_t6_a_block_without_an_answer_or_an_ecg_line_is_incomplete(self):
        for missing in ("  EM-ANSWER: none\n", "  EM-ECG: not applicable\n"):
            with self.subTest(missing=missing):
                self.assertEqual(1, grammar.em_block(BLOCK.replace(missing, "")).unread)

    def test_t1_a_refused_element_line_keeps_its_element_and_entry_id(self):
        refused = ('  EM-PROBLEM: definition-stable-chronic | not counted | "History" | history | only\n'
                   "  EM-RISK: unreadable entry id! | counted | none | x\n")
        block = grammar.em_block(BLOCK + refused)
        self.assertEqual(2, block.unread)
        self.assertEqual((("PROBLEM", "definition-stable-chronic"), ("RISK", None)), block.unread_items)

    def test_t2_a_step_four_block_ends_at_an_em_line_written_after_it(self):
        for anchor in (EM_LINE, "CPT  99213  Office visit, established patient\n"):
            with self.subTest(anchor=anchor):
                text = "---NOT CODED, NOTHING ESTABLISHED IT---\nrefused\n" + anchor + BLOCK
                self.assertEqual("refused", grammar.block_text(text, grammar.REFUSAL_HEADING, EM_CODES))

    def test_u6_an_element_line_ending_in_not_for_entry_leaves_the_em_entry_for_entry(self):
        text = ("ICD-10  E11.9  Type 2 diabetes mellitus without complications\n"
                "CPT  99213  Office visit, established patient\n"
                + BLOCK.replace("EM-RULE: ADR 0308 ruling 1", "EM-RULE: the refused code is not for entry"))
        self.assertEqual([True, True], [entry.for_entry for entry in grammar.read_entries(text)])
        self.assertEqual("99213", review_manifest.selected_codes(text, private=True)["em"])

    def test_a_block_ends_at_an_unspaced_step_four_heading(self):
        text = "---CODED, ANCHOR WAS FILLED---\nNone.\n---NOT CODED, NOTHING ESTABLISHED IT---\nrefused\n"
        self.assertEqual("None.", grammar.block_text(text, grammar.BLOCK_HEADING))
        self.assertEqual("refused", grammar.block_text(text, grammar.REFUSAL_HEADING))


class EveryWorksheetReaderToleratesTheBlock(unittest.TestCase):
    """Adding the block to a preserved worksheet changes no worksheet grader report."""

    commands = ("specificity_scan.py", "refusal_scan.py", "anchor_scan.py")

    def reports(self, text: str) -> list[tuple[str, int, str]]:
        with tempfile.TemporaryDirectory() as folder:
            worksheets = Path(folder) / "worksheets"
            worksheets.mkdir()
            (worksheets / "case-01.md").write_text(text, encoding="utf-8")
            results = []
            for command in self.commands:
                run = subprocess.run([sys.executable, str(Path(__file__).with_name(command)), str(worksheets)],
                                     capture_output=True, text=True, encoding="utf-8", errors="replace")
                results.append((command, run.returncode, run.stdout))
            return results

    def test_the_block_at_the_end_and_before_the_differential(self):
        preserved = PRESERVED.read_text(encoding="utf-8")
        differential = re.search(r"(?m)^--- DIFFERENTIAL", preserved).start()
        placements = {
            "end": (preserved + "\n" + EM_LINE, preserved + "\n" + EM_LINE + BLOCK),
            "before the differential": (
                preserved[:differential] + EM_LINE + "\n" + preserved[differential:],
                preserved[:differential] + EM_LINE + BLOCK + "\n" + preserved[differential:]),
        }
        for placement, (without, with_block) in placements.items():
            with self.subTest(placement=placement):
                self.assertEqual(self.reports(without), self.reports(with_block))

    def test_selected_codes_ignore_the_block(self):
        private = "ICD-10  E11.9  Type 2 diabetes mellitus without complications\n" + EM_LINE
        self.assertEqual(review_manifest.selected_codes(private, private=True),
                         review_manifest.selected_codes(private + BLOCK, private=True))
        entry = "ICD-10  E11.9  Type 2 diabetes mellitus without complications\nCPT  99213  Office visit\n"
        self.assertEqual(review_manifest.selected_codes(entry, private=True),
                         review_manifest.selected_codes(entry + BLOCK, private=True))


if __name__ == "__main__":
    unittest.main()
