"""Wiring tests for the shared UpToDate workflow."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class TheAccountAnswerAndLocalRefuserReachTheirConsumers(unittest.TestCase):
    def test_setup_collects_the_exact_profile_field(self):
        setup = (ROOT / "skills/setup-clinical-skills/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Do you have an UpToDate account?", setup)
        self.assertIn("UPTODATE-ACCOUNT: yes", setup)
        self.assertIn("UPTODATE-ACCOUNT: no", setup)

    def test_a_staged_topic_sheet_runs_the_grader(self):
        hook = (ROOT / "tools/hooks/pre-commit").read_text(encoding="utf-8")
        self.assertIn("reference/uptodate/[^/]*\\.md$", hook)
        self.assertIn('uptodate_sheet.py" --all --quiet', hook)


if __name__ == "__main__":
    unittest.main()
