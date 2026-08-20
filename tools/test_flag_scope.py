"""Contract checks for issue #159's FLAG scope.

The public seam is the finished ``clinical-note`` artifact: its note body and
tier block, plus the drift matrix a generating pass walks.  ``day-a`` holds the
observed regression class without exposing any patient material.
"""

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
DAY_A = REPO_ROOT / "fixtures" / "day-a" / "assertions.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def drift_row(text: str, number: int) -> str:
    match = re.search(rf"^\| {number} \|.*$", text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"drift row {number} is absent")
    return match.group(0)


class AFlagReportsTheFinishedNote(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(SKILL)
        cls.block = cls.text.split("**FLAG is the block that matters.**", 1)[1]
        cls.block = cls.block.split("**What never goes under GAPS:**", 1)[0]

    def test_the_template_scopes_the_claim_to_the_finished_note(self):
        self.assertIn(
            "<a documented finding the finished note still fails to act on>",
            self.text,
        )

    def test_the_definition_rejects_encounter_scope(self):
        self.assertIn(
            "A FLAG is always a claim about the finished note, never about the source encounter",
            self.block,
        )

    def test_an_addressed_finding_is_not_flagged(self):
        self.assertIn(
            "If the finished note supplies the action the FLAG says is absent, there is no FLAG",
            self.block,
        )
        self.assertIn("Merely naming the finding does not clear", self.block)

    def test_an_encounter_omission_the_note_corrects_is_only_proposed(self):
        self.assertIn("belongs under `FILLED·proposed`, not `FLAG`", self.block)

    def test_the_voice_rule_no_longer_calls_every_tier_a_patient_claim(self):
        self.assertNotIn("a tier block is for claims about the patient", self.text)
        self.assertIn("tier block is not one kind of claim", self.text)
        self.assertIn("separate lanes hold arithmetic", self.text)


class TheDriftMatrixWalksFlagScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(SKILL)
        cls.row = drift_row(cls.text, 26)

    def test_row_26_is_named_flag_scope(self):
        self.assertIn("**FLAG scope**", self.row)

    def test_row_26_compares_each_flag_to_the_finished_note(self):
        self.assertIn("finished note", self.row)
        self.assertIn("Assessment or Plan", self.row)
        self.assertIn("source encounter", self.row)
        self.assertIn("the action it says is absent remains absent", self.row)
        self.assertIn("Merely naming the finding does not clear", self.row)

    def test_the_append_convention_is_recorded(self):
        self.assertIn("**Row 26 is appended", self.text)


class DayARecordsTheRegressionClass(unittest.TestCase):
    def test_f8_scores_plan_contradictions_separately_from_f4(self):
        text = read(DAY_A)
        match = re.search(r"^\| F8 \|.*$", text, re.MULTILINE)
        self.assertIsNotNone(match)
        row = match.group(0)
        self.assertIn("finished note", row)
        self.assertIn("Assessment or Plan", row)
        self.assertIn("source encounter", row)
        self.assertIn("F4", row)


if __name__ == "__main__":
    unittest.main()
