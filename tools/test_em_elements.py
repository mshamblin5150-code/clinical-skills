"""The E/M element block: its strict reader, and every worksheet reader tolerating it."""
from __future__ import annotations

import artifact_lock_test_support  # noqa: F401

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import review_manifest
import worksheet_grammar as grammar


def quote(text, heading, kind):
    """The check-off's quotation of one icd10-cpt step 4 block of ``text`` (em_audit.block_quote)."""
    import em_audit
    return em_audit.block_quote(em_audit.parse_private(text), heading, kind)

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


def astuple_of(elements):
    return elements.block, elements.outside, elements.blocks


def strict_block(text: str) -> grammar.EmBlock:
    """``grammar.em_block`` of a text this test wrote with element lines in it, so a block is read."""
    block = grammar.em_block(text)
    assert block is not None, "the text carries element lines, so a block is read"
    return block


class TheStrictReader(unittest.TestCase):
    def test_the_reference_example_is_a_complete_block(self):
        text = REFERENCE.read_text(encoding="utf-8")
        example = text.split("Synthetic example", 1)[1].split("```text", 1)[1].split("```", 1)[0]
        block, outside, _ = astuple_of(grammar.worksheet_em_block(example))
        self.assertEqual(0, outside)
        self.assertEqual(0, block.unread)
        self.assertEqual(("low", "low"), (block.mdm["mdm"], block.two_of_three()))
        self.assertEqual("99213", block.level)
        self.assertEqual(["note-1.q1"], list(block.answers))
        self.assertEqual({"PROBLEM", "DATA", "RISK"}, {item.kind for item in block.items})

    def test_every_refused_line_and_a_missing_required_line_are_unread(self):
        self.assertEqual(0, strict_block(BLOCK).unread)
        for broken in (BLOCK.replace("| counted |", "| maybe |", 1),
                       BLOCK + "  EM-OPINION: something\n",
                       BLOCK.replace("mdm low", "mdm middling"),
                       BLOCK.replace("EM-ANSWER: none", "EM-ANSWER: the second question"),
                       BLOCK.replace("  EM-LEVEL: 99213\n", ""),
                       BLOCK.replace("  EM-DATA: none | not counted | none | no test documented\n", "")):
            with self.subTest(broken=broken):
                self.assertGreater(strict_block(broken).unread, 0)

    def test_two_of_three_is_the_middle_level(self):
        block = strict_block(BLOCK.replace("problems low; data straightforward; risk moderate",
                                           "problems high; data straightforward; risk moderate"))
        self.assertEqual("moderate", block.two_of_three())

    def test_a_worksheet_without_the_block_stays_valid(self):
        preserved = PRESERVED.read_text(encoding="utf-8")
        self.assertEqual(grammar.WorksheetElements(None, 0, 0), grammar.worksheet_em_block(preserved))
        self.assertIsNone(grammar.em_block("E/M: 99213 low MDM\nNo element lines here.\n"))

    def test_element_lines_away_from_the_em_line_are_counted_outside(self):
        text = "ICD-10  E11.9  Type 2 diabetes mellitus without complications\n" + BLOCK + "\n" + EM_LINE
        block, outside, _ = astuple_of(grammar.worksheet_em_block(text))
        self.assertIsNone(block)
        self.assertEqual(len(BLOCK.splitlines()), outside)

    def test_every_anchor_spelling_the_code_reader_accepts_carries_the_block(self):
        for anchor in ("CPT  99213  Office visit, established patient", "cpt 99213 Office",
                       "**E/M**: 99213 low MDM", "e/m: 99213 low MDM", EM_LINE.strip()):
            with self.subTest(anchor=anchor):
                block, outside, blocks = astuple_of(grammar.worksheet_em_block(anchor + "\n" + BLOCK))
                self.assertEqual((0, 0, "99213", 1), (outside, block.unread, block.level, blocks))
                self.assertEqual("99213", review_manifest.selected_codes(
                    "ICD-10  E11.9  Type 2 diabetes mellitus without complications\n" + anchor + "\n" + BLOCK,
                    private=True)["em"])

    def test_the_block_under_the_second_anchor_is_read_and_two_blocks_are_counted(self):
        entry = "CPT  99213  Office visit, established patient\n"
        block, outside, blocks = astuple_of(grammar.worksheet_em_block(entry + "\n" + EM_LINE + BLOCK))
        self.assertEqual((0, 1, "99213"), (outside, blocks, block.level))
        _, _, blocks = astuple_of(grammar.worksheet_em_block(entry + BLOCK + "\n" + EM_LINE + BLOCK))
        self.assertEqual(2, blocks)

    def test_r6_a_nested_em_line_inside_a_cpt_entry_counts_each_element_line_once(self):
        text = "CPT  99213  Office visit, established patient\n  E/M: 99213 low MDM\n" + BLOCK
        block, outside, blocks = astuple_of(grammar.worksheet_em_block(text))
        self.assertEqual((0, 1, 0), (outside, blocks, block.unread))

    def test_t6_a_block_without_an_answer_or_an_ecg_line_is_incomplete(self):
        for missing in ("  EM-ANSWER: none\n", "  EM-ECG: not applicable\n"):
            with self.subTest(missing=missing):
                self.assertEqual(1, strict_block(BLOCK.replace(missing, "")).unread)

    def test_t1_a_refused_element_line_keeps_its_element_and_entry_id(self):
        refused = ('  EM-PROBLEM: definition-stable-chronic | not counted | "History" | history | only\n'
                   "  EM-RISK: unreadable entry id! | counted | none | x\n")
        block = strict_block(BLOCK + refused)
        self.assertEqual(2, block.unread)
        self.assertEqual((("PROBLEM", "definition-stable-chronic"), ("RISK", None)), block.unread_items)

    def test_t2_a_step_four_block_ends_at_an_em_line_written_after_it(self):
        text = "---NOT CODED, NOTHING ESTABLISHED IT---\nrefused\n" + EM_LINE + BLOCK
        self.assertEqual("refused", quote(text, grammar.REFUSAL_HEADING, "refusal"))
        # Ninth review: a CPT entry after the icd10-cpt step 4 blocks is not one the manifest selects, so it
        # anchors nothing and stays the block's text, as selected_codes reads it.
        entry = "CPT  99213  Office visit, established patient\n"
        text = "---NOT CODED, NOTHING ESTABLISHED IT---\nrefused\n" + entry + BLOCK
        self.assertEqual("refused\n" + entry + BLOCK.rstrip("\n"),
                         quote(text, grammar.REFUSAL_HEADING, "refusal"))

    def test_u6_an_element_line_ending_in_not_for_entry_leaves_the_em_entry_for_entry(self):
        text = ("ICD-10  E11.9  Type 2 diabetes mellitus without complications\n"
                "CPT  99213  Office visit, established patient\n"
                + BLOCK.replace("EM-RULE: ADR 0308 ruling 1", "EM-RULE: the refused code is not for entry"))
        self.assertEqual([True, True], [entry.for_entry for entry in grammar.read_entries(text)])
        self.assertEqual("99213", review_manifest.selected_codes(text, private=True)["em"])

    def test_v5_only_an_unindented_em_line_ends_a_step_four_block(self):
        inside = "refused\n  E/M: 99214 would be supported if the history were documented\n  more"
        text = "---NOT CODED, NOTHING ESTABLISHED IT---\n" + inside + "\n"
        self.assertEqual(inside, quote(text, grammar.REFUSAL_HEADING, "refusal"))
        indented_entry = "refused\n  CPT  99214  Office visit, established patient"
        self.assertEqual(indented_entry, quote(
            "---NOT CODED, NOTHING ESTABLISHED IT---\n" + indented_entry + "\n", grammar.REFUSAL_HEADING, "refusal"))
        self.assertEqual("refused", quote(
            "---NOT CODED, NOTHING ESTABLISHED IT---\nrefused\n" + EM_LINE + BLOCK, grammar.REFUSAL_HEADING, "refusal"))
        # A margin E/M line or entry with no element block beneath it is the block's own text.
        for margin in (EM_LINE, "CPT 99214 would be supported with documented time\n"):
            with self.subTest(margin=margin):
                text = "---UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE---\n" + margin + "history in part\n"
                self.assertEqual(margin + "history in part",
                                 quote(text, grammar.UNDOCUMENTED_HEADING, "undocumented"))

    def test_x2_a_unicode_line_separator_inside_note_text_stays_on_its_element_line(self):
        moved = BLOCK.replace('"Diabetes stable"', '"Diabetes' + chr(0x2028) + 'stable"')
        block, outside, blocks = astuple_of(grammar.worksheet_em_block(EM_LINE + moved))
        self.assertEqual((1, 0, 0), (blocks, outside, block.unread))
        changed = moved.replace(chr(0x2028) + "stable", chr(0x2028) + "steady")
        self.assertNotEqual(review_manifest.private_worksheet_sha256(EM_LINE + moved),
                            review_manifest.private_worksheet_sha256(EM_LINE + changed))
        # Twenty-sixth review: the check-off splits through validation's read, review_manifest.read_private.
        self.assertIs(grammar.physical_lines, review_manifest.physical_lines)

    def test_x3_a_refused_element_line_without_a_colon_keeps_its_element_and_entry_id(self):
        line = '  EM-PROBLEM definition-stable-chronic | not counted | "History" | history only\n'
        self.assertEqual((("PROBLEM", "definition-stable-chronic"),), strict_block(BLOCK + line).unread_items)

    def test_x4_one_refused_required_line_counts_once(self):
        for old, new in (("| counted |", "| maybe |"), ("EM-LEVEL: 99213", "EM-LEVEL: not a code"),
                         ("EM-ANSWER: none", "EM-ANSWER: the second question")):
            with self.subTest(old=old):
                self.assertEqual(1, strict_block(BLOCK.replace(old, new, 1)).unread)

    def test_z2_a_lower_case_element_name_is_unread_and_fingerprinted(self):
        for spelling in ("EM-Problem", "em-problem", "- em-data"):
            with self.subTest(spelling=spelling):
                near = "  " + spelling + ': definition-acute-uncomplicated | counted | "Cough" | evaluated\n'
                block, outside, _ = astuple_of(grammar.worksheet_em_block(EM_LINE + BLOCK + near))
                self.assertEqual((0, 1), (outside, block.unread))
                self.assertNotEqual(review_manifest.private_worksheet_sha256(EM_LINE + BLOCK + near),
                                    review_manifest.private_worksheet_sha256(EM_LINE + BLOCK + near.replace("Cough", "Fever")))
        self.assertIsNone(grammar.em_block("- em-dashes set this sentence apart\n"))

    def test_z3_the_anchor_takes_its_for_entry_flag_from_the_entry_reader(self):
        text = "CPT 99284 Emergency visit\n\n  reasoning only, NOT FOR ENTRY\n"
        lines = text.splitlines()
        self.assertFalse(grammar.read_entries(text)[0].for_entry)
        self.assertNotIn(0, grammar.selected_em_lines(lines))
        self.assertIn(0, grammar.selected_em_lines(["CPT 99284 Emergency visit", "", "  reasoning"]))

    def test_z4_an_element_block_inside_a_step_four_block_is_skipped_not_an_end(self):
        # Eleventh review: the graders read the E/M section as block text, as main read it; only the
        # check-off quotation leaves it out, and neither treats it as the end of the block.
        import anchor_scan
        import refusal_scan
        filled = "---CODED, ANCHOR WAS FILLED---\n" + EM_LINE + BLOCK + "Z68.36\n"
        self.assertEqual(([*(EM_LINE + BLOCK).splitlines(), "Z68.36"], True), anchor_scan._block_lines(filled))
        self.assertEqual("Z68.36", quote(filled, grammar.BLOCK_HEADING, "filled"))
        refused = "---NOT CODED, NOTHING ESTABLISHED IT---\nrefused\n" + EM_LINE + BLOCK + "more\n"
        self.assertEqual((["refused", *(EM_LINE + BLOCK).splitlines(), "more"], True),
                         refusal_scan._block_lines(refused.splitlines()))
        self.assertEqual("refused\nmore", quote(refused, grammar.REFUSAL_HEADING, "refusal"))

    def test_n2_for_entry_is_read_by_the_manifest_rule_over_the_entry_region(self):
        text = "CPT  99213  Office visit, established patient\n\n## DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY\n"
        self.assertEqual("99213", review_manifest.selected_codes("ICD-10  E11.9  Type 2 diabetes\n" + text,
                                                                  private=True)["em"])
        self.assertIn(0, grammar.selected_em_lines(text.splitlines()))

    def test_q1_a_lower_case_or_suffixed_element_line_counts_once_and_maps_to_its_element(self):
        self.assertEqual(1, strict_block(BLOCK.replace("  EM-DATA:", "  em-data:")).unread)
        moved = strict_block(BLOCK.replace("  EM-PROBLEM: definition-stable-chronic",
                                           "  EM-PROBLEMS: definition-stable-chronic"))
        self.assertEqual((1, (("PROBLEM", "definition-stable-chronic"),)), (moved.unread, moved.unread_items))
        opinion = strict_block(BLOCK + "  EM-OPINION: something\n")
        self.assertEqual({("PROBLEM", None), ("DATA", None), ("RISK", None)}, set(opinion.unread_items))

    def test_q4_only_the_anchor_and_its_element_lines_are_skipped_in_a_step_four_block(self):
        import refusal_scan
        text = ("---NOT CODED, NOTHING ESTABLISHED IT---\nrefused\n" + EM_LINE + "  a note the grader reads\n"
                + BLOCK + "more\n")
        self.assertEqual((text.splitlines()[1:], True), refusal_scan._block_lines(text.splitlines()))
        # Fifteenth review: the wrapped header line is the E/M line's own, shown once in the E/M section.
        self.assertEqual("refused\nmore", quote(text, grammar.REFUSAL_HEADING, "refusal"))

    def test_a_block_ends_at_an_unspaced_step_four_heading(self):
        text = "---CODED, ANCHOR WAS FILLED---\nNone.\n---NOT CODED, NOTHING ESTABLISHED IT---\nrefused\n"
        self.assertEqual("None.", quote(text, grammar.BLOCK_HEADING, "filled"))
        self.assertEqual("refused", quote(text, grammar.REFUSAL_HEADING, "refusal"))


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
        heading = re.search(r"(?m)^--- DIFFERENTIAL", preserved)
        assert heading is not None, "the preserved worksheet carries a differential"
        differential = heading.start()
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
