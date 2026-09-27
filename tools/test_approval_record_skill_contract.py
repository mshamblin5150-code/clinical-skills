"""The six posting skills expose the shared approval-record and status contract. #1421."""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "discussion-post",
    "discussion-reply",
    "peer-critique",
    "practicum-case-study",
    "clinical-note",
    "batch-shift",
)


class PostingSkillContract(unittest.TestCase):
    def test_each_posting_skill_records_approval_route_and_keyed_status(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                text = (ROOT / "skills" / skill / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("approval_record.approve", text)
                self.assertIn("approval_record.record_agent_posting", text)
                self.assertIn("approval_record.record_clinician_posting", text)
                self.assertIn("skips", text)
                self.assertIn("Run status: <run-key> —", text)
                self.assertIn("--submission", text)

    def test_standalone_clinical_note_names_its_private_run_directory(self) -> None:
        text = (ROOT / "skills" / "clinical-note" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "scratch/runs/<encounter-key>-<date>-clinical-note/", text
        )


if __name__ == "__main__":
    unittest.main()
