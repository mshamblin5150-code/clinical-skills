"""The shared run-key and population policy -- issue #417."""

import tempfile
import unittest
from pathlib import Path

import coursework_run


class RunKey(unittest.TestCase):
    def test_a_submission_date_is_provenance_not_identity(self):
        self.assertEqual(
            coursework_run.key_of("nur5144-m1-case-study-2026-08-20"),
            "nur5144-m1-case-study",
        )

    def test_only_a_trailing_iso_date_is_removed(self):
        self.assertEqual(
            coursework_run.key_of("nur5144-2026-08-20-case-study"),
            "nur5144-2026-08-20-case-study",
        )

    def test_a_stem_without_a_date_is_unchanged(self):
        self.assertEqual(
            coursework_run.key_of("nur5144-m1-case-study"),
            "nur5144-m1-case-study",
        )


class Populations(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve() / "clinical_skills"
        (self.root / "tools").mkdir(parents=True)
        (self.root / ".git").mkdir()

    def test_runs_live_under_the_main_scratch_root(self):
        self.assertEqual(
            coursework_run.runs_root(self.root / "tools"),
            self.root / "scratch" / "runs",
        )

    def test_a_direct_child_is_a_canonical_run_directory(self):
        run = self.root / "scratch" / "runs" / "nur5144-m1-case-study"
        self.assertTrue(coursework_run.is_run_directory(run, self.root / "tools"))

    def test_a_nested_or_loose_directory_is_not_a_run_directory(self):
        nested = self.root / "scratch" / "runs" / "key" / "posts"
        loose = self.root / "scratch" / "key"
        self.assertFalse(coursework_run.is_run_directory(nested, self.root / "tools"))
        self.assertFalse(coursework_run.is_run_directory(loose, self.root / "tools"))

    def test_a_draft_under_output_is_a_submission(self):
        draft = self.root / "output" / "case-studies" / "key-2026-08-20.md"
        self.assertTrue(coursework_run.is_submission(draft, self.root / "tools"))

    def test_a_temp_draft_is_not_a_submission(self):
        draft = Path(self.directory.name) / "draft.md"
        self.assertFalse(coursework_run.is_submission(draft, self.root / "tools"))
