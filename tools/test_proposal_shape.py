"""Pin issue #127's ``FILLED·proposed`` unit and its evidence.

The historical notes are a run record, not a conformance fixture.  This test
therefore records the three shapes they actually contain while separately
checking that the current skill and assertion rows state the future-output
rule consistently.
"""

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
DAY_B = REPO_ROOT / "fixtures" / "day-b" / "assertions.md"
PEDS_BP = REPO_ROOT / "fixtures" / "peds-bp" / "assertions.md"
NOTES = REPO_ROOT / "fixtures" / "filled-anchor" / "notes"

NEXT_LABEL = re.compile(r"^(?:FLAG|GAPS|UNKNOWN)\b")
NUMBERED = re.compile(r"^(?:FILLED·proposed\s+|\s+)(\d+)\.\s", re.MULTILINE)
P_TAGGED = re.compile(r"^\s+P(\d+)\s", re.MULTILINE)

PROPOSED_SECTION_SHA256 = {
    "case-01": "9a7e98b3ee05a8918b7942d7d884b553f99aa518ef986d969e57f32728f81744",
    "case-02": "b8e893d1e36733b75c3d2424bf6a7c2560e5fd8c04c3820da917d802abc796bd",
    "case-03": "9da0381e4bde75163a0e1102e3ad29a87b28c4e274cea3d67478cacae002d697",
    "case-04": "655d28fd4a09c4ba8dd2bd94511a6e05e22af9a303a859ee2b2a1c939e2a4740",
    "case-05": "ab9d2ff7844abffcd9a79c67acd83c62e6481114a827a11ac58a5f98053a99c0",
    "case-06": "50489474acc7b73f5d04cb7539c92d52f19341a5f2c86bb709d8229a33a7e681",
    "case-07": "57b30b7f02339501dfe6eb0120db432e91386cec210a9016b3da94a8ba0272db",
    "case-08": "d2d027ff603131e1787337692e77330c5def1500a2fb6c5f698ce31cd19158eb",
    "case-09": "9fdbd94127ec28dce7e11375039169d4f8bb69d2820118bf7942a9e69cac7702",
    "case-10": "2fb68db803f59f448e241039e45796157f335e7e56c8d6f009373a4c06d5d2fb",
    "case-11": "3124a071c917af836d6d44ba64dcf253f350f4b11ec0a43e3262df749195e7f0",
    "case-12": "ff8dc458213d564bc218d0c1db6879d512e1072d6e56af80c43fc81439143362",
}


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
    numbered = [int(value) for value in NUMBERED.findall(section)]
    p_tagged = [int(value) for value in P_TAGGED.findall(section)]
    if numbered and p_tagged:
        raise AssertionError("one proposed block uses both enumeration shapes")
    if numbered:
        if numbered != list(range(numbered[0], numbered[0] + len(numbered))):
            raise AssertionError(f"numbered proposal sequence is incomplete: {numbered}")
        return "numbered"
    if p_tagged:
        if p_tagged != list(range(1, len(p_tagged) + 1)):
            raise AssertionError(f"P-tagged proposal sequence is incomplete: {p_tagged}")
        return "p-tagged"
    return "unenumerated"


class TheHistoricalMeasurementIsPinned(unittest.TestCase):
    def test_each_complete_proposed_section_is_pinned(self) -> None:
        """A recognized opener never makes a partly readable block look complete."""
        observed = {
            path.stem: hashlib.sha256(
                proposed_section(path.read_text(encoding="utf-8")).encode("utf-8")
            ).hexdigest()
            for path in sorted(NOTES.glob("case-*.md"))
        }
        self.assertEqual(observed, PROPOSED_SECTION_SHA256)

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
