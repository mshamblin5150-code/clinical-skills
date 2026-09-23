"""Public-interface tests for the rich course-assignment DOCX branch."""

from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import assignment_docx
import assignment_docx_scan
import file_digest
from repo_root import main_repo_root
from research_ledger import heading_digest


DOCX_BAR = """\
ASSIGNMENT: https://example.invalid/assignment
SIGNED: 2026-09-13
ARTIFACT: docx
SUBMISSION-TYPE: file-upload
WORD-MIN: 1
WORD-MAX: 200
REFERENCE-MIN: 1
SOURCE-CLASSES: peer-reviewed | government
RECENCY-WINDOW-YEARS: 5
"""


class RichPackage(unittest.TestCase):
    def test_the_generic_fixture_has_the_required_rich_word_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generic-assignment.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), path)

            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                document = archive.read("word/document.xml").decode("utf-8")
                styles = archive.read("word/styles.xml").decode("utf-8")
                header = archive.read("word/header1.xml").decode("utf-8")
                core = archive.read("docProps/core.xml").decode("utf-8")

        self.assertIn("word/media/relationship.png", names)
        self.assertIn('w:styleId="Title"', styles)
        self.assertIn('w:styleId="Heading1"', styles)
        self.assertIn('w:styleId="Caption"', styles)
        self.assertIn('w:tblHeader', document)
        self.assertIn('descr="Generic system relationship diagram"', document)
        self.assertIn('w:pStyle w:val="Caption"', document)
        self.assertIn("<w:fitText", document)
        for label in ("Intent", "Coordination", "Feedback"):
            self.assertIn(f"<w:t>{label}</w:t>", document)
        self.assertIn('w:instr="PAGE"', header)
        self.assertIn("[AUTHOR]", document)
        self.assertIn("[DOCUMENT TITLE]", core)

    def test_the_same_spec_produces_identical_package_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.docx"
            second = Path(directory) / "second.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), first)
            assignment_docx.build(assignment_docx.fixture_spec(), second)

            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_an_existing_document_requires_explicit_force(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assignment.docx"
            path.write_bytes(b"human-edited document")

            with self.assertRaisesRegex(ValueError, "--force"):
                assignment_docx.build(assignment_docx.fixture_spec(), path)
            self.assertEqual(b"human-edited document", path.read_bytes())

            assignment_docx.build(assignment_docx.fixture_spec(), path, force=True)
            self.assertTrue(zipfile.is_zipfile(path))

    def test_a_finished_document_cannot_land_in_a_tracked_checkout_path(self):
        path = main_repo_root() / "tracked-course-assignment.docx"

        with self.assertRaisesRegex(ValueError, "output/course-assignments"):
            assignment_docx.build(assignment_docx.fixture_spec(), path)

    def test_the_command_builds_from_configurable_title_and_content_metadata(self):
        spec = assignment_docx.fixture_spec()
        payload = {
            "title_page": {
                field: getattr(spec.title_page, field)
                for field in spec.title_page.__dataclass_fields__
            },
            "sections": [
                {"heading": section.heading, "paragraphs": list(section.paragraphs)}
                for section in spec.sections
            ],
            "command_rows": [
                {
                    "role": row.role,
                    "responsibility": row.responsibility,
                    "decision_right": row.decision_right,
                }
                for row in spec.command_rows
            ],
            "relationship_labels": list(spec.relationship_labels),
            "references": list(spec.references),
            "figure_alt_text": spec.figure_alt_text,
        }
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "assignment.json"
            output = Path(directory) / "assignment.docx"
            config.write_text(json.dumps(payload), encoding="utf-8")

            status = assignment_docx.main([str(config), str(output)])

            self.assertEqual(0, status)
            self.assertTrue(output.is_file())


class DocxGrader(unittest.TestCase):
    def test_a_valid_docx_bar_and_package_are_scanned_not_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "generic-course-assignment"
            run.mkdir()
            artifact = Path(directory) / "generic-course-assignment-2026-09-13.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), artifact)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
            (run / "claims.md").write_text(
                "DATE: 2026-09-13\n\n"
                "## CLAIM: Authority, coordination, and feedback are connected.\n",
                encoding="utf-8",
            )

            status = assignment_docx_scan.main(
                [str(run), "--docx", str(artifact)]
            )

        self.assertEqual(1, status)

    def test_a_complete_docx_run_grades_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "generic-course-assignment"
            retained = run / "render" / "pass-1"
            retained.mkdir(parents=True)
            artifact = Path(directory) / "generic-course-assignment-2026-09-13.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), artifact)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
            (run / "claims.md").write_text(
                "DATE: 2026-09-13\n\n"
                "## CLAIM: Authority, coordination, and feedback are connected.\n"
                "STATUS: sourced\n"
                "REFERENCE: Example Agency. (2025). *Systems coordination brief*. "
                "https://example.invalid/brief\n"
                "REFUTATION: stands - the source supports the relationship.\n"
                f"TESTED-HEADING: {heading_digest('Authority, coordination, and feedback are connected.')}\n"
                "SECOND-ROUTE: agency page -> source brief\n",
                encoding="utf-8",
            )
            (run / "project-context.md").write_text(
                "PROJECT-CONTEXT: none - synthetic assignment\n"
                "CONFIRMED: 2026-09-23\nCONTEXT-DIGEST: none\n",
                encoding="utf-8",
            )
            (run / "heading-read.md").write_text(
                f"## HEADING-READ: {artifact.name}\n"
                f"DRAFT: {file_digest.sha256(artifact)}\n"
                "ROUTE: separate context\n"
                "SENTENCES: 0 factual, 0 clinician's own\n"
                "CONTEXT-DIGEST: none\n"
                "CONTEXT-VERDICT: none\n"
                "VERDICT: clean\n",
                encoding="utf-8",
            )
            (retained / "page-1.png").write_bytes(b"retained page pixels")
            (retained / "assignment.pdf").write_bytes(b"retained page-faithful export")
            file_digest.write_recorded_sha256(
                retained / assignment_docx_scan.FINGERPRINT_FILE,
                file_digest.sha256(artifact),
            )
            (run / "rendered.md").write_text(
                "## RENDERED: generic-course-assignment-2026-09-13.docx\n"
                "PASS: 1\n"
                "PAGES: 1 of 1 read\n"
                "SOURCE: word-pdf\n"
                "UNSEEN: none\n"
                "READ: the retained page against the DOCX and signed bar\n"
                "VERDICT: clean - all content is readable\n",
                encoding="utf-8",
            )

            status = assignment_docx_scan.main(
                [str(run), "--docx", str(artifact)]
            )

        self.assertEqual(0, status)

    def test_retained_pixels_without_a_page_faithful_export_are_a_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "generic-course-assignment"
            retained = run / "render" / "pass-1"
            retained.mkdir(parents=True)
            artifact = Path(directory) / "generic-course-assignment-2026-09-13.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), artifact)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
            (run / "claims.md").write_text(
                "## CLAIM: Authority, coordination, and feedback are connected.\n"
                "STATUS: sourced\n"
                "REFERENCE: Example Agency. (2025). *Systems coordination brief*. "
                "https://example.invalid/brief\n"
                "REFUTATION: stands - the source supports the relationship.\n"
                f"TESTED-HEADING: {heading_digest('Authority, coordination, and feedback are connected.')}\n"
                "SECOND-ROUTE: agency page -> source brief\n",
                encoding="utf-8",
            )
            (retained / "page-1.png").write_bytes(b"retained page pixels")
            file_digest.write_recorded_sha256(
                retained / assignment_docx_scan.FINGERPRINT_FILE,
                file_digest.sha256(artifact),
            )
            (run / "rendered.md").write_text(
                "## RENDERED: generic-course-assignment-2026-09-13.docx\n"
                "PASS: 1\nPAGES: 1 of 1 read\nSOURCE: word-pdf\nUNSEEN: none\n"
                "READ: every retained page\nVERDICT: clean - readable\n",
                encoding="utf-8",
            )

            status = assignment_docx_scan.main(
                [str(run), "--docx", str(artifact)]
            )

        self.assertEqual(1, status)


if __name__ == "__main__":
    unittest.main()
