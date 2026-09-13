"""Retained-render tests for course-assignment Word artifacts."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import assignment_docx
import assignment_docx_render as render
import file_digest


class RetainedWordRender(unittest.TestCase):
    def test_the_pass_is_bound_to_the_exact_canonical_docx(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            docx = Path(directory) / "assignment.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), docx)
            expected = file_digest.sha256(docx)

            def exported(_docx: Path, conversion: Path):
                pdf = conversion / "assignment-docx.pdf"
                pdf.write_bytes(b"page-faithful Word PDF")
                return "word-pdf", pdf

            def rasterized(_export: Path, staging: Path):
                (staging / "page-1.png").write_bytes(b"page pixels")
                return 1

            with (
                mock.patch.object(render, "_automated_export", side_effect=exported),
                mock.patch.object(render, "_rasterize", side_effect=rasterized),
            ):
                source, retained, pages = render.render(run, docx)

            recorded = (retained / render.FINGERPRINT_FILE).read_text(
                encoding="ascii"
            ).strip()
            retained_names = sorted(path.name for path in retained.iterdir())

        self.assertEqual(("word-pdf", 1), (source, pages))
        self.assertEqual(expected, recorded)
        self.assertEqual(
            ["assignment-docx.pdf", "assignment-docx.sha256", "page-1.png"],
            retained_names,
        )


if __name__ == "__main__":
    unittest.main()
