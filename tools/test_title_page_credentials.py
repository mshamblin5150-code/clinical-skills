"""Account title-page settings persist a decision without manufacturing a default."""

import tempfile
import unittest
from pathlib import Path

import title_page_credentials as settings


class TitlePageSetting(unittest.TestCase):
    def test_silence_stops_then_the_saved_answer_is_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.md"
            profile.write_text("# Account\n\nOther setting: retained\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ask once"):
                settings.read(profile)
            settings.record(profile, "RN, Example Credential")
            self.assertEqual(settings.read(profile), "RN, Example Credential")
            self.assertEqual(settings.read(profile), "RN, Example Credential")
            self.assertIn("Other setting: retained", profile.read_text(encoding="utf-8"))
            settings.record(profile, "none")
            self.assertEqual(settings.read(profile), "")
            self.assertEqual(profile.read_text(encoding="utf-8").count(settings.FIELD), 1)

    def test_ambiguous_settings_and_multiline_answers_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.md"
            original = "TITLE-PAGE-CREDENTIALS: none\nTITLE-PAGE-CREDENTIALS: RN\n"
            profile.write_text(original, encoding="utf-8")
            with self.assertRaises(ValueError):
                settings.read(profile)
            with self.assertRaises(ValueError):
                settings.record(profile, "RN")
            with self.assertRaises(ValueError):
                settings.record(profile, "RN\nOther: value")
            self.assertEqual(profile.read_text(encoding="utf-8"), original)

    def test_both_artifact_branches_and_setup_reach_the_same_setting(self):
        root = Path(__file__).resolve().parents[1]
        for path in ("skills/setup-clinical-skills/SKILL.md", "skills/course-assignment/SKILL.md",
                     "skills/course-assignment/references/docx.md", "skills/_shared/reference/apa7.md"):
            with self.subTest(path=path):
                text = (root / path).read_text(encoding="utf-8")
                self.assertIn(settings.FIELD, text)


if __name__ == "__main__":
    unittest.main()
