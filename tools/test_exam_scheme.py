"""Exercise the examination-scheme gate through its public command."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOL = Path(__file__).with_name("exam_scheme.py")


class ExaminationSchemeCommand(unittest.TestCase):
    def run_check(self, *notes, scheme="nine regions", profile_text=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            profile = root / "profile.md"
            profile.write_text(
                profile_text if profile_text is not None else
                f"## Normal examination\nAbdominal scheme: {scheme}\nGI: Chosen wording\n",
                encoding="utf-8",
            )
            paths = []
            for index, note in enumerate(notes):
                path = root / f"note-{index}.md"
                path.write_text(note, encoding="utf-8")
                paths.append(str(path))
            return subprocess.run(
                [sys.executable, str(TOOL), "--profile", str(profile), *paths],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )

    def test_quadrant_exam_is_refused_without_disclosing_note_text(self):
        result = self.run_check("S:\nHistory\nO:\nGen: Well\nGI: Sounds in all quadrants\nA:\nDiagnosis\nP:\nPlan")
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("notes read 1; examination sections found 1", result.stdout)
        self.assertIn("unread remainder 0", result.stdout)
        self.assertNotIn("Sounds", result.stdout)

    def test_plan_imaging_and_differential_descriptor_are_outside_the_exam(self):
        result = self.run_check(
            "S:\nHPI: Right upper quadrant pain\nO:\nVS: normal\nGen: Well\n"
            "GI: Right iliac tenderness\nLabs/Tests today: right upper quadrant ultrasound\n"
            "A:\nDifferential:\n1. Right lower quadrant pain - R10.31\n"
            "P:\nNon-pharmacologic: right upper quadrant ultrasound\n"
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("examination sections found 1", result.stdout)

    def test_hp_location_and_abbreviations_are_refused(self):
        for wording in ("Right lower quadrant tenderness", "RLQ tender", "RUQ tender", "LLQ tender", "LUQ tender"):
            with self.subTest(wording=wording):
                result = self.run_check(
                    f"Objective:\nVital signs\nBP normal\n\n"
                    f"Physical Exam (pertinent to the differential)\nGI: {wording}\n"
                    "Lab, x-ray, other tests\nNone\nAssessment\nDiagnosis"
                )
                self.assertEqual(1, result.returncode, result.stdout + result.stderr)

    def test_four_quadrants_has_no_mirror_check(self):
        for wording in ("All quadrants normal", "Right lumbar tenderness; epigastric tenderness"):
            result = self.run_check(f"O:\nGI: {wording}\nA:\nDiagnosis", scheme="four quadrants")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_missing_empty_ambiguous_unclosed_and_vitals_only_exams_are_unread(self):
        for note in (
            "S:\nHistory\nA:\nDiagnosis\nP:\nPlan",
            "O:\nA:\nDiagnosis",
            "O:\nGen: Well\nO:\nGI: Normal\nA:\nDiagnosis",
            "Physical Exam\nGI: Normal",
            "O:\nVS: BP 120/80\nLabs/Tests today: None\nA:\nDiagnosis",
            "Physical Exam\nGI: Normal\nAssessment\nPhysical Exam\nGI: Normal\nAssessment",
        ):
            with self.subTest(note=note):
                result = self.run_check(note)
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertIn("examination sections found 0", result.stdout)
                self.assertIn("unread remainder 1", result.stdout)

    def test_a_finding_wins_over_an_unread_remainder(self):
        result = self.run_check("O:\nGI: All quadrants normal\nA:\nDiagnosis", "Unrecognized note")
        self.assertEqual(1, result.returncode)
        self.assertIn("notes read 2; examination sections found 1", result.stdout)
        self.assertIn("unread remainder 1", result.stdout)

    def test_missing_or_invalid_profile_cannot_report_clean(self):
        for profile in ("## Other settings\nNo block", "## Normal examination\nGI: Normal", "## Normal examination\nAbdominal scheme: unknown"):
            result = self.run_check("O:\nGI: Normal\nA:\nDiagnosis", profile_text=profile)
            self.assertEqual(2, result.returncode)
            self.assertIn("notes read 0", result.stdout)
            self.assertIn("unread remainder 1", result.stdout)

    def test_markdown_headings_and_bold_labels(self):
        result = self.run_check("## O:\n**Gen:** Well\n**GI:** All quadrants normal\n## A:\nDiagnosis")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)

    def test_committed_note_examination_is_read_through_the_command(self):
        fixture = TOOL.parent.parent / "fixtures" / "filled-anchor" / "notes" / "case-06.md"
        result = self.run_check(fixture.read_text(encoding="utf-8"))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("notes read 1; examination sections found 1", result.stdout)
        self.assertIn("unread remainder 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
