"""Clinical credential choices stop on silence and persist without defaults."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import clinical_credentials as settings


class ClinicalCredentials(unittest.TestCase):
    def test_silence_stops_then_both_answers_are_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.md"
            profile.write_text("# Account\nTITLE-PAGE-CREDENTIALS: none\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ask once"):
                settings.read(profile)
            settings.record(profile, "RN, Example", "NP, Example")
            self.assertEqual(settings.read(profile), ("RN, Example", "NP, Example"))
            self.assertEqual(settings.read(profile), settings.read(profile))
            settings.record(profile, "RN", "NP")
            text = profile.read_text(encoding="utf-8")
            self.assertIn("TITLE-PAGE-CREDENTIALS: none", text)
            for field in settings.FIELDS:
                self.assertEqual(text.count(field), 1)

    def test_missing_blank_duplicate_and_multiline_choices_refuse_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.md"
            for text in ("SIGNATURE-CREDENTIALS: RN\n",
                         "SIGNATURE-CREDENTIALS: \nPRESCRIBING-CREDENTIALS: NP\n",
                         "SIGNATURE-CREDENTIALS: RN\nSIGNATURE-CREDENTIALS: RN\nPRESCRIBING-CREDENTIALS: NP\n"):
                profile.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    settings.read(profile)
            with self.assertRaises(ValueError):
                settings.record(profile, "RN", "NP")
            for signature, prescribing in (("", "NP"), ("RN", " "), ("RN\nOther: value", "NP"), ("RN", "NP\rOther: value")):
                with self.assertRaises(ValueError):
                    settings.record(profile, signature, prescribing)
            self.assertEqual(profile.read_text(encoding="utf-8"), text)

    def test_command_requires_the_answer_pair_and_reports_missing_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.md"
            profile.write_text("# Account\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(settings.main(["--profile", str(profile)]), 2)
                self.assertEqual(settings.main(["--profile", str(profile), "--signature", "RN"]), 2)
                self.assertEqual(settings.main(["--profile", str(profile), "--signature", "RN", "--prescribing", "NP"]), 0)
                self.assertEqual(settings.main(["--profile", str(profile)]), 0)
                self.assertEqual(settings.main(["--profile", str(profile.with_name("absent.md"))]), 2)

    def test_shared_examples_and_setup_use_account_fields(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("skills/setup-clinical-skills/SKILL.md", "skills/practicum-case-study/SKILL.md", "skills/_shared/reference/style.md"):
            text = (root / name).read_text(encoding="utf-8")
            for field in settings.FIELDS:
                self.assertIn(field, text, name)
            self.assertNotIn("CEN, TCRN", text, name)


if __name__ == "__main__":
    unittest.main()
