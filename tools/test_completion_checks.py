"""ADR 0346 dated-check contracts through public grading seams. Synthetic."""
import contextlib
from datetime import date
import io
from pathlib import Path
import tempfile
import unittest

import completion_checks as checks
import discussion_artifact
import research_ledger
import medatrax_posting
import coursework_run
from test_frozen_grade import FrozenFixture
from test_medatrax_posting import reading
from prose_bind import bind, NAMING


class CompletionRegistry(unittest.TestCase):
    def test_derivation_boundary_is_named_without_copying_it(self):
        self.assertEqual((), bind(checks.DECLARED_LIMITS,
            (checks.ROOT.parent / "AGENTS.md").read_text(encoding="utf-8"), mode=NAMING))
    def test_every_derived_completion_check_has_a_start_and_moment(self):
        self.assertEqual(set(), set(checks.derive()) - checks.registry().keys())

    def test_new_literal_completion_check_without_entry_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "discussion_post_scan.py").write_text(
                'def survey():\n    return Finding("new-synthetic-check", "draft", "finding")\n', encoding="utf-8")
            self.assertIn("discussion_post_scan:new-synthetic-check", set(checks.derive(path)) - checks.registry().keys())

    def test_existing_cutoffs_keep_their_reference_moments(self):
        self.assertEqual("extraction", checks.registry()["aar_scan:memory-measurement"][1])
        self.assertEqual("confirmation", checks.registry()["project_context:classmate"][1])
        self.assertEqual("ledger", checks.registry()["research_ledger:stated-expiry"][1])
        self.assertFalse(checks.active("research_ledger:stated-expiry", date(2026, 8, 27)))
        self.assertTrue(checks.active("research_ledger:stated-expiry", date(2026, 8, 28)))


class CheckLandingBetweenPostingAndGrade(FrozenFixture):
    def test_time_log_is_required_only_after_its_start(self):
        self.item["skill"] = "clinical-note"
        self.item["recorded_at"] = 1790812800  # 2026-10-01 UTC
        self.save()
        text = reading(self.item["sha256"]).replace("shift-2026-08-17", "post").replace("TIME-LOG: not requested\n", "")
        (self.run / "reread.md").write_text(text, encoding="utf-8")
        self.assertEqual((), medatrax_posting.posted_reading_check(self.run, "post", batch=False))
        self.item["recorded_at"] = 1791504000  # 2026-10-09 UTC
        self.item["approval_revision"] = 2
        self.save()
        self.assertEqual(["time-log"], [r.code for r in medatrax_posting.posted_reading_check(self.run, "post", batch=False)])
    def test_old_approval_does_not_owe_a_later_draft_observation(self):
        self.item["recorded_at"] = 1790812800  # 2026-10-01 UTC
        self.save()
        result = coursework_run.grade_order(None, "post", lambda *args: False, run=self.run)
        self.assertFalse(result.finding)
        self.assertIn("not graded", result.report)
        self.item["recorded_at"] = 1791158400  # after the observation check starts
        self.save()
        self.assertTrue(coursework_run.grade_order(None, "post", lambda *args: False, run=self.run).finding)


if __name__ == "__main__":
    unittest.main()
