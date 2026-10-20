"""ADR 0356 controls. All draft text is synthetic (phi-scan: synthetic)."""
import artifact_lock_test_support
import io
import tempfile
import unittest
import artifact_lock_test_support
from contextlib import redirect_stdout, redirect_stderr
from datetime import date
from pathlib import Path

import reference_scan as scan
import reference_alphabets as alphabets


class PaperLanguage(unittest.TestCase):
    def test_english_letters_fold_at_every_position(self):
        self.assertEqual(scan.ordering_text("ØŒÆŁÐĐÞıß"), "ooeaelddthiss")
        self.assertEqual(scan.ordering_text("MØller"), scan.ordering_text("Moller"))
        names = ["Zhang", "Øvretveit", "Olsen", "Thomas", "Þórsson", "Thorn"]
        self.assertEqual(sorted(names, key=scan.ordering_text),
                         ["Olsen", "Øvretveit", "Thomas", "Thorn", "Þórsson", "Zhang"])

    def test_every_locale_matches_frozen_icu_controls(self):
        for language, row in alphabets.TABLE["languages"].items():
            with self.subTest(language=language):
                controls = row["controls"]
                self.assertEqual(sorted(controls["input"], key=lambda s: alphabets.ordering(s, language)), controls["ordered"])
                self.assertEqual(row["cldr"], "48.0")
                self.assertTrue(row["source"].endswith(".xml"))

    def test_norwegian_and_czech_contractions(self):
        self.assertLess(alphabets.ordering("Zhang", "nb"), alphabets.ordering("Øvretveit", "nb"))
        self.assertEqual(alphabets.ordering("Aasen", "nb"), alphabets.ordering("Åsen", "nb"))
        self.assertLess(alphabets.ordering("Husa", "cs"), alphabets.ordering("Chata", "cs"))
        self.assertLess(alphabets.ordering("Chata", "cs"), alphabets.ordering("Ivan", "cs"))

    def test_german_files_umlauts_as_plain_vowels_and_leaves_ties_unbroken(self):
        """ADR 0399: Göbel files with Gobel, before Goebel; ß and ss tie either way."""
        self.assertEqual(alphabets.language_name("Deutsch"), "de")
        self.assertEqual(alphabets.language_name("German"), "de")
        self.assertEqual(alphabets.ordering("Göbel", "de"), alphabets.ordering("Gobel", "de"))
        self.assertEqual(alphabets.ordering("Müller", "de"), alphabets.ordering("Muller", "de"))
        self.assertEqual(alphabets.ordering("Straße", "de"), alphabets.ordering("Strasse", "de"))
        self.assertLess(alphabets.ordering("Göbel", "de"), alphabets.ordering("Goebel", "de"))
        self.assertLess(alphabets.ordering("Mueller", "de"), alphabets.ordering("Müller", "de"))
        for pair in (("Straße", "Strasse"), ("Strasse", "Straße"), ("Räben", "Raben"), ("Raben", "Räben")):
            with self.subTest(order=pair):
                entries = "".join(f"{name}, J. (2025). Topic. Publisher.\n" for name in pair)
                text = f"A claim ({pair[0]}, 2025; {pair[1]}, 2025).\n\n## References\n\n{entries}"
                kinds = [f.kind for f in scan.survey(scan.read_document(text), date(2026, 10, 12), "German").findings]
                self.assertNotIn(scan.LIST_NOT_SORTED, kinds)
        text = "A claim (Goebel, 2025; Göbel, 2025).\n\n## References\n\nGoebel, J. (2025). Topic. Publisher.\nGöbel, J. (2025). Topic. Publisher.\n"
        kinds = [f.kind for f in scan.survey(scan.read_document(text), date(2026, 10, 12), "German").findings]
        self.assertIn(scan.LIST_NOT_SORTED, kinds)

    def test_citation_matches_but_reports_spelling(self):
        for cited, listed in [("Ovretveit", "Øvretveit"), ("Kubler", "Kübler"), ("Moller", "Møller"), ("Strasse", "Straße")]:
            text = f"A claim ({cited}, 2025).\n\n## References\n\n{listed}, J. (2025). Topic. Publisher.\n"
            for language in ("en", "nb", "German", "Dutch", None):
                findings = scan.survey(scan.read_document(text), date(2026, 10, 12), language).findings
                self.assertEqual([f.kind for f in findings], [scan.CITATION_AUTHOR_SPELLING])

    def test_command_override_profile_and_ungraded_status(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.md"
            profile.write_text("PAPER-LANGUAGE: Norwegian Bokmål\n", encoding="utf-8")
            draft = Path(directory) / "draft.md"
            draft.write_text("A claim (Øvretveit, 2025; Zhang, 2025).\n\n## References\n\nØvretveit, J. (2025). Topic. Publisher.\nZhang, J. (2025). Topic. Publisher.\n", encoding="utf-8")
            base = [str(draft), "--as-of", "2026-10-12", "--profile", str(profile)]
            for extra, status, label in [([], 1, "nb"), (["--paper-language", "English"], 0, "en"), (["--paper-language", "German"], 0, "de"), (["--paper-language", "Dutch"], 2, "Dutch"), (["--paper-language", "Klingon"], 2, "Klingon")]:
                with redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
                    self.assertEqual(scan.main(base + extra), status)
                self.assertIn(label.casefold(), output.getvalue())
            profile.write_text("Other setting: retained\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
                self.assertEqual(scan.main(base), 2)
            self.assertIn("not graded", output.getvalue())

    def test_ungraded_order_does_not_hide_other_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.md"
            profile.write_text("PAPER-LANGUAGE: English\nPAPER-LANGUAGE: Spanish\n", encoding="utf-8")
            self.assertIsNone(alphabets.paper_language(profile=profile))
            draft = Path(directory) / "draft.md"
            draft.write_text("A claim (Absent, 2025).\n\n## References\n\nSmith, J. (2025). Topic. Publisher.\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
                self.assertEqual(scan.main([str(draft), "--profile", str(profile), "--as-of", "2026-10-12"]), 1)
            self.assertIn("not graded", output.getvalue())
            self.assertIn("unlisted-citation", output.getvalue())

    def test_full_group_spelling_is_checked_but_abbreviations_are_preserved(self):
        for cited, expected in [("Oresund Institute", [scan.CITATION_AUTHOR_SPELLING]),
                                ("Oresund-Institute", [scan.CITATION_AUTHOR_SPELLING]),
                                ("Øresund Institute", [])]:
            text = f"A claim ({cited}, 2025).\n\n## References\n\nØresund Institute. (2025). Topic. Publisher.\n"
            self.assertEqual([f.kind for f in scan.survey(scan.read_document(text), date(2026, 10, 12), "en").findings], expected)
        text = "A claim (Øresund Institute [OI], 2025). A claim (OI, 2025).\n\n## References\n\nØresund Institute. (2025). Topic. Publisher.\n"
        self.assertNotIn(scan.CITATION_AUTHOR_SPELLING, [f.kind for f in scan.survey(scan.read_document(text), date(2026, 10, 12), "en").findings])


if __name__ == "__main__":
    unittest.main()
