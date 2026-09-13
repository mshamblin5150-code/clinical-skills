"""Public-interface tests for course-assignment artifact discrimination."""

from __future__ import annotations

import unittest
from pathlib import Path
import tempfile
from unittest import mock

import assignment_bar
import course_assignment_scan
import deck_scan
import run_grader


DOCX_BAR = """\
ASSIGNMENT: https://example.invalid/assignment
SIGNED: 2026-09-13
ARTIFACT: docx
SUBMISSION-TYPE: file-upload
WORD-MIN: 900
WORD-MAX: 1200
REFERENCE-MIN: 3
SOURCE-CLASSES: peer-reviewed | government
RECENCY-WINDOW-YEARS: 5
"""

DECK_BAR = """\
ASSIGNMENT: https://example.invalid/assignment
SIGNED: 2026-09-13
ARTIFACT: deck
SLIDE-MAX: 10
BULLETS-PER-SLIDE: 6
WORDS-PER-BULLET: 6
FONT-POINTS: 24
FONT-DIRECTION: floor
SOURCE-CLASSES: peer-reviewed | government
RECENCY-WINDOW-YEARS: 5
"""


class ArtifactDiscrimination(unittest.TestCase):
    def test_a_valid_docx_bar_selects_the_docx_adapter(self):
        envelope = assignment_bar.parse(DOCX_BAR)

        self.assertEqual("docx", envelope.artifact)
        self.assertEqual("assignment_docx_scan", assignment_bar.adapter_name(envelope))

    def test_an_ambiguous_artifact_field_fails_loudly(self):
        ambiguous = DOCX_BAR.replace(
            "ARTIFACT: docx", "ARTIFACT: deck\nARTIFACT: docx"
        )

        with self.assertRaisesRegex(
            run_grader.SourceError, "duplicate ARTIFACT"
        ):
            assignment_bar.parse(ambiguous)

    def test_the_dispatcher_passes_the_parsed_envelope_to_the_docx_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
            adapter = mock.Mock()
            adapter.main.return_value = 17

            with mock.patch.object(
                course_assignment_scan, "_import_adapter", return_value=adapter
            ) as imported:
                status = course_assignment_scan.main([str(run), "--artifact", "paper.docx"])

        imported.assert_called_once_with("assignment_docx_scan")
        envelope = adapter.main.call_args.kwargs["envelope"]
        self.assertEqual("docx", envelope.artifact)
        self.assertEqual(17, status)

    def test_bar_only_validation_does_not_require_a_finished_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(0, status)

    def test_bar_only_validation_rejects_an_incomplete_docx_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            incomplete = DOCX_BAR.replace("WORD-MIN: 900\n", "")
            (run / "bar.md").write_text(incomplete, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(2, status)

    def test_bar_only_validation_rejects_a_nonpositive_recency_window(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            invalid = DOCX_BAR.replace("RECENCY-WINDOW-YEARS: 5", "RECENCY-WINDOW-YEARS: 0")
            (run / "bar.md").write_text(invalid, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(2, status)

    def test_bar_only_validation_rejects_an_unknown_source_class(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            invalid = DOCX_BAR.replace(
                "peer-reviewed | government", "peer-reviewed | invented source"
            )
            (run / "bar.md").write_text(invalid, encoding="utf-8")

            status = course_assignment_scan.main([str(run), "--bar-only"])

        self.assertEqual(2, status)

    def test_the_legacy_deck_adapter_accepts_a_preparsed_envelope(self):
        status = deck_scan.main([], envelope=assignment_bar.parse(DECK_BAR))

        self.assertEqual(2, status)


if __name__ == "__main__":
    unittest.main()
