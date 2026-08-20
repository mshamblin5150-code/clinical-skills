"""Pin issue #127's ``FILLED·proposed`` unit and its evidence.

The historical notes are a run record, not a conformance fixture.  This test
therefore records the three shapes they actually contain while separately
checking that the current skill and assertion rows state the future-output
rule consistently.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
DAY_B = REPO_ROOT / "fixtures" / "day-b" / "assertions.md"
PEDS_BP = REPO_ROOT / "fixtures" / "peds-bp" / "assertions.md"
NOTES = REPO_ROOT / "fixtures" / "filled-anchor" / "notes"

NEXT_LABEL = re.compile(r"^(?:FLAG|GAPS|UNKNOWN)\b")
NUMBERED = re.compile(r"^(?:FILLED·proposed\s+|\s+)\d+\.\s", re.MULTILINE)
P_TAGGED = re.compile(r"^\s+P\d+\s", re.MULTILINE)


def proposed_section(text: str) -> str:
    """Return the first proposed section through the next tier-block label."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("FILLED·proposed"))
    end = next(
        (i for i in range(start + 1, len(lines)) if NEXT_LABEL.match(lines[i])),
        len(lines),
    )
    return "\n".join(lines[start:end])


def proposal_shape(text: str) -> str:
    section = proposed_section(text)
    numbered = bool(NUMBERED.search(section))
    p_tagged = bool(P_TAGGED.search(section))
    if numbered and p_tagged:
        raise AssertionError("one proposed block uses both enumeration shapes")
    if numbered:
        return "numbered"
    if p_tagged:
        return "p-tagged"
    return "unenumerated"


class TheHistoricalMeasurementIsPinned(unittest.TestCase):
    def test_the_twelve_notes_have_the_corrected_four_two_six_split(self) -> None:
        observed = {
            path.stem: proposal_shape(path.read_text(encoding="utf-8"))
            for path in sorted(NOTES.glob("case-*.md"))
        }
        self.assertEqual(
            observed,
            {
                "case-01": "unenumerated",
                "case-02": "unenumerated",
                "case-03": "unenumerated",
                "case-04": "unenumerated",
                "case-05": "numbered",
                "case-06": "numbered",
                "case-07": "p-tagged",
                "case-08": "p-tagged",
                "case-09": "unenumerated",
                "case-10": "unenumerated",
                "case-11": "numbered",
                "case-12": "numbered",
            },
        )


class TheRuleNamesOneUnitEverywhere(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.day_b = DAY_B.read_text(encoding="utf-8")
        cls.peds_bp = PEDS_BP.read_text(encoding="utf-8")

    def test_the_tier_block_template_requires_one_numbered_action(self) -> None:
        self.assertIn(
            "FILLED·proposed   1. <one proposed action>",
            self.skill,
        )

    def test_row_21_defines_the_item_and_its_wrap(self) -> None:
        self.assertIn("An item is one numbered `FILLED·proposed` entry", self.skill)
        self.assertIn(
            "A wrapped line belongs to the numbered item that opened it and never opens one",
            self.skill,
        )

    def test_row_24_cannot_collapse_several_verdicts_into_one_item(self) -> None:
        self.assertIn(
            "Each separately acceptable action is its own numbered item and carries its own verdict",
            self.skill,
        )

    def test_both_fixture_rows_use_the_same_unit(self) -> None:
        phrase = "An item is one numbered `FILLED·proposed` entry"
        self.assertIn(phrase, self.day_b)
        self.assertIn(phrase, self.peds_bp)

    def test_an_assessment_recommendation_is_a_named_landing(self) -> None:
        phrase = "a self-contained Assessment recommendation for the preceptor to rule on"
        self.assertIn(phrase, self.skill)
        self.assertIn(phrase, self.day_b)
        self.assertIn(phrase, self.peds_bp)


if __name__ == "__main__":
    unittest.main()
