"""Contract checks for issue #132's impossible-given rule.

The public seam is the complete ``clinical-note`` output: note body, tier block,
Medatrax field block and drift matrix. The fixture assertion pins the only
committed impossible vital; Medatrax has no heart-rate field, so that generic
structured-field limb stays pinned in the drift row rather than this case.
"""

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
HEDGED = REPO_ROOT / "fixtures" / "hedged-dx" / "assertions.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def drift_row(text: str, number: int) -> str:
    match = re.search(rf"^\| {number} \|.*$", text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"drift row {number} is absent")
    return match.group(0)


class TheImpossibleGivenRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(SKILL)

    def test_preserves_the_number_and_refuses_a_silent_correction(self):
        self.assertIn("An impossible given stays given", self.text)
        self.assertIn("Never replace it with a plausible candidate", self.text)

    def test_uses_unknown_and_flag_for_distinct_jobs(self):
        section = self.text.split("#### An impossible given stays given", 1)[1]
        section = section.split("#### ", 1)[0]
        self.assertIn("`UNKNOWN`", section)
        self.assertIn("`FLAG`", section)
        self.assertIn("marked as a guess", section)

    def test_bars_every_downstream_use(self):
        row = drift_row(self.text, 25)
        for obligation in ("arithmetic", "diagnosis", "code", "dose", "reasoning"):
            self.assertIn(obligation, row)

    def test_an_unusable_medatrax_value_becomes_an_explicit_gap(self):
        row = drift_row(self.text, 25)
        self.assertIn("Medatrax", row)
        self.assertIn("GAPS", row)
        self.assertIn("unusable", row)


class HedgedDxAnchorsTheRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(HEDGED)

    def test_case_one_has_a_binary_drift_assertion(self):
        match = re.search(r"^\| D2 \|.*$", self.text, re.MULTILINE)
        self.assertIsNotNone(match)
        row = match.group(0)
        self.assertIn("1 — 7 yo f", row)
        self.assertIn("`hr 1238`", row)
        self.assertIn("UNKNOWN", row)
        self.assertIn("FLAG", row)
        self.assertIn("no heart-rate field", row)

    def test_the_case_is_no_longer_called_unscored(self):
        self.assertNotIn("Case 1's impossible heart rate is unscored", self.text)


if __name__ == "__main__":
    unittest.main()
