"""Pin issue #205's per-allergen reasoning rule.

The value itself is not graded.  A modal reaction can honestly repeat across
several drugs, so a cap would force variation the encounter does not support.
The enforceable boundary is the audit trail: each distinct allergen gets its
own declaration, and that declaration says what made this reaction plausible
for this allergen.  A shared sentence about the list does not satisfy the rule.

``duration-span`` case 1 is the committed regression shape.  Its allergy clause
contains two spellings of one drug, so it also fixes the unit: transcription
noise is corrected before distinct allergens are counted.
"""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
SOAP = REPO_ROOT / "skills" / "clinical-note" / "SOAP.md"
HP = REPO_ROOT / "skills" / "clinical-note" / "HP.md"
ASSERTIONS = REPO_ROOT / "fixtures" / "duration-span" / "assertions.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    start = text.index(heading)
    end = text.find("\n#", start + len(heading))
    return text[start:] if end == -1 else text[start:end]


class TheSkillGradesReasoningPerDistinctAllergen(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = section(read(SKILL), "##### The reaction beside a given allergen")

    def test_each_distinct_allergen_gets_its_own_declaration(self) -> None:
        self.assertIn("each distinct allergen", self.rule)
        self.assertIn("its own `FILLED·asserted` entry", self.rule)

    def test_each_entry_names_that_allergens_own_reasoning(self) -> None:
        self.assertIn("reasoned from for that allergen", self.rule)
        self.assertIn("one rationale for the list", self.rule.lower())

    def test_spelling_variants_do_not_create_a_second_allergen(self) -> None:
        self.assertIn("after obvious misspellings are corrected", self.rule.lower())


class BothBranchesCarryTheSameBoundary(unittest.TestCase):
    def test_both_templates_require_per_allergen_reasoning(self) -> None:
        for path in (SOAP, HP):
            with self.subTest(path=path.name):
                text = read(path)
                self.assertIn("each distinct allergen", text)
                self.assertIn("reasoned from for that allergen", text)


class DriftRowTwentySevenWalksTheRule(unittest.TestCase):
    def test_the_row_exists_and_names_all_three_limbs(self) -> None:
        rows = [line for line in read(SKILL).splitlines() if line.startswith("| 27 ")]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        for limb in ("distinct allergen", "own `FILLED·asserted` entry", "reasoned from"):
            with self.subTest(limb=limb):
                self.assertIn(limb, row)


class TheCommittedMultiAllergenShapeCarriesTheAssertion(unittest.TestCase):
    def test_duration_span_has_one_binary_row_for_the_new_rule(self) -> None:
        rows = [line for line in read(ASSERTIONS).splitlines() if line.startswith("| S4 ")]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        for limb in ("distinct drug allergen", "one `FILLED·asserted` entry", "reasoned from"):
            with self.subTest(limb=limb):
                self.assertIn(limb, row)


if __name__ == "__main__":
    unittest.main()
