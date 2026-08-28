"""Pin ADR 0043's page-transcription ruling to the reader-facing files.

The ruling is mostly prose, so this is ``test_ruling_cohort.py``'s seam: assert
that the rule remains written in the ADR, the glossary, and both format-sheet
paragraphs a drafter follows.  A tidy that turns ``RENDERED:`` back into an
extraction-failure marker must fail without needing the external PDF corpus.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from prose_bind import ProseBind


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTEXT = REPO_ROOT / "CONTEXT.md"
FORMAT_SHEET = REPO_ROOT / "reference" / "thresholds" / "README.md"
ADR = (
    REPO_ROOT
    / "docs"
    / "adr"
    / "0043-a-rendered-cell-is-a-page-transcription-and-its-marker-records-the-read-rather-than-an-extraction-failure.md"
)


class TheAdrKeepsTheRuledMeaning(unittest.TestCase):
    def setUp(self):
        self.text = ADR.read_text(encoding="utf-8")

    def test_the_marker_records_the_read_not_an_extraction_failure(self):
        self.assertIn(
            "the marker names an audit claim, and an extraction failure is a common cause of one and never its definition",
            self.text,
        )

    def test_a_rendered_cell_is_a_page_transcription(self):
        self.assertIn(
            "a `RENDERED:` cell is a **page transcription**",
            self.text,
        )


class TheGlossaryDefinesPageTranscription(ProseBind, unittest.TestCase):
    def setUp(self):
        self.text = CONTEXT.read_text(encoding="utf-8")

    def test_the_term_is_filed_against_snippet(self):
        self.assertIn("**Page transcription**:", self.text)
        self.assertProseIn(
            "What a reader saw on a rendered guideline page, reassembled into one cell",
            self.text,
        )
        self.assertIn("it is not a **snippet**", self.text)

    def test_the_marker_is_the_audit_claim_that_licenses_the_cell(self):
        start = self.text.index("**Page transcription**:")
        block = self.text[start : start + 1_000]
        self.assertProseIn(
            "The marker is the audit claim that a page was rendered and read, and that claim is what licenses the cell.",
            block,
        )
        self.assertIn(
            "_Avoid_: snippet, quote, paraphrase, reconstruction, transcription",
            block,
        )


class TheFormatSheetTeachesBothRoutes(ProseBind, unittest.TestCase):
    def setUp(self):
        self.text = FORMAT_SHEET.read_text(encoding="utf-8")

    def test_the_marker_declares_a_page_transcription_whatever_prompted_the_read(self):
        self.assertProseIn(
            "A cell in the snippet column may begin `RENDERED:` to declare a page transcription and record that its cited page was rendered and read, whatever prompted the read.",
            self.text,
        )

    def test_a_machine_clean_page_transcription_is_not_a_defect(self):
        self.assertProseIn(
            "A marked row may also extract cleanly, and that is not a defect.",
            self.text,
        )

    def test_prophylactic_and_reactive_routes_are_both_named(self):
        self.assertProseIn(
            "The ordinary route is prophylactic: a drafter reassembling a table or figure renders and reads the page before recording the transcription.",
            self.text,
        )
        self.assertProseIn(
            "The reactive route follows a gate 4 refusal: a working agent renders the page and records the same read after confirming that the label and value belong together.",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
