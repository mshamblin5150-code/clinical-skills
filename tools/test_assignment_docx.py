"""Public-interface tests for the rich course-assignment DOCX branch."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
import zipfile
from dataclasses import replace
from xml.etree import ElementTree as ET
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


def _payload(spec: assignment_docx.AssignmentSpec) -> dict:
    return {
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
        "figure_image": spec.figure_image,
        "figure_title": spec.figure_title,
        "references": list(spec.references),
        "figure_alt_text": spec.figure_alt_text,
    }


class RichPackage(unittest.TestCase):
    def test_supplied_image_bytes_and_proportions_survive_with_a_two_line_caption(self):
        spec = assignment_docx.fixture_spec()
        package = assignment_docx.parts(spec)
        self.assertEqual(package["word/media/figure.png"], Path(spec.figure_image).read_bytes())
        root = ET.fromstring(package["word/document.xml"])
        w = assignment_docx_scan.W
        wp = assignment_docx_scan.WP
        extent = root.find(f".//{wp}extent")
        self.assertEqual(extent.attrib, {"cx": "5943600", "cy": "1717040"})
        paragraphs = root.findall(f"{w}body/{w}p")
        index = next(i for i, p in enumerate(paragraphs) if p.find(f".//{w}drawing") is not None)
        number, title = paragraphs[index - 2:index]
        self.assertEqual("".join(number.itertext()), "Figure 1")
        self.assertIsNotNone(number.find(f"{w}r/{w}rPr/{w}b"))
        self.assertEqual("".join(title.itertext()), spec.figure_title)
        self.assertIsNotNone(title.find(f"{w}r/{w}rPr/{w}i"))
        self.assertNotIn("The figure connects", package["word/document.xml"])

    def test_retired_figure_fields_name_the_replacement_interface(self):
        payload = _payload(assignment_docx.fixture_spec())
        payload["relationship_labels"] = ["Intent", "Coordination", "Feedback"]
        with self.assertRaisesRegex(ValueError, "figure_image, figure_title, and figure_alt_text"):
            assignment_docx.from_mapping(payload)

    def test_title_repeats_and_an_explicit_omission_writes_no_credential_paragraph(self):
        spec = assignment_docx.fixture_spec()
        payload = _payload(spec)
        payload["title_page"]["credentials"] = ""
        root = ET.fromstring(assignment_docx.parts(assignment_docx.from_mapping(payload))["word/document.xml"])
        w = assignment_docx_scan.W
        texts = ["".join(p.itertext()) for p in root.findall(f"{w}body/{w}p")]
        self.assertEqual(texts[:6], ["", "", "", spec.title_page.title, "", spec.title_page.author])
        self.assertEqual(texts.count(spec.title_page.title), 2)
        self.assertNotIn(spec.title_page.credentials, texts)

    def test_figure_note_is_below_the_supplied_image_and_not_generated_by_the_producer(self):
        spec = replace(assignment_docx.fixture_spec(), figure_note="Image generated using Example Tool (Example, 2026).")
        document = assignment_docx.parts(spec)["word/document.xml"]
        self.assertGreater(document.index(spec.figure_note), document.index("</w:drawing>"))

    def test_invalid_image_refuses_before_replacing_the_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "bad.png"
            image.write_bytes(b"not an image")
            path = Path(directory) / "assignment.docx"
            path.write_bytes(b"previous document")
            with self.assertRaisesRegex(ValueError, "PNG or JPEG"):
                assignment_docx.build(replace(assignment_docx.fixture_spec(), figure_image=str(image)), path, force=True)
            self.assertEqual(path.read_bytes(), b"previous document")

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

        self.assertIn("word/media/figure.png", names)
        self.assertIn('w:styleId="Title"', styles)
        self.assertIn('w:styleId="Heading1"', styles)
        self.assertIn('w:styleId="Caption"', styles)
        self.assertNotIn('<w:tbl', document)
        self.assertIn('descr="Generic system relationship diagram"', document)
        self.assertIn('w:pStyle w:val="Caption"', document)
        self.assertIn("<w:fitText", document)
        for label in ("Intent", "Coordination", "Feedback"):
            self.assertIn(label, document)
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

    def test_a_spec_without_a_matrix_or_figure_writes_neither(self):
        payload = _payload(assignment_docx.fixture_spec())
        for key in ("command_rows", "figure_image", "figure_title", "figure_alt_text"):
            del payload[key]
        spec = assignment_docx.from_mapping(payload)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plain-assignment.docx"
            assignment_docx.build(spec, path)

            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                document = archive.read("word/document.xml").decode("utf-8")
                rels = archive.read("word/_rels/document.xml.rels").decode("utf-8")
                types = archive.read("[Content_Types].xml").decode("utf-8")

        self.assertNotIn("word/media/figure.png", names)
        self.assertNotIn("media/figure.png", rels)
        self.assertNotIn("<w:drawing>", document)
        self.assertNotIn("Command Matrix", document)
        self.assertNotIn("System Relationships", document)
        self.assertIn("References", document)
        self.assertIn('Extension="xml"', types)

    def test_a_matrix_may_stand_without_a_figure(self):
        payload = _payload(assignment_docx.fixture_spec())
        del payload["figure_image"]
        del payload["figure_title"]
        del payload["figure_alt_text"]
        spec = assignment_docx.from_mapping(payload)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix-only.docx"
            assignment_docx.build(spec, path)
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                document = archive.read("word/document.xml").decode("utf-8")

        self.assertIn("Command Matrix", document)
        self.assertNotIn("System Relationships", document)
        self.assertNotIn("word/media/figure.png", names)

    def test_a_half_specified_figure_is_refused(self):
        for missing in ("figure_image", "figure_title", "figure_alt_text"):
            payload = _payload(assignment_docx.fixture_spec())
            del payload[missing]
            with self.subTest(missing=missing), self.assertRaisesRegex(
                ValueError, "figure_image, figure_title, and figure_alt_text"
            ):
                assignment_docx.from_mapping(payload)

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
            "figure_image": spec.figure_image,
            "figure_title": spec.figure_title,
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

    def test_a_document_without_a_figure_owes_no_figure_alt_text_or_caption(self):
        payload = _payload(assignment_docx.fixture_spec())
        for key in ("command_rows", "figure_image", "figure_title", "figure_alt_text"):
            del payload[key]
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "generic-course-assignment"
            run.mkdir()
            artifact = Path(directory) / "generic-course-assignment-2026-09-13.docx"
            assignment_docx.build(assignment_docx.from_mapping(payload), artifact)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
            (run / "claims.md").write_text(
                "DATE: 2026-09-13\n\n"
                "## CLAIM: Authority, coordination, and feedback are connected.\n",
                encoding="utf-8",
            )
            report = io.StringIO()
            with contextlib.redirect_stdout(report):
                assignment_docx_scan.main([str(run), "--docx", str(artifact)])

        self.assertIn("package-structure: 0", report.getvalue())

    def test_a_drawing_without_alt_text_is_still_a_package_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "generic-course-assignment"
            run.mkdir()
            artifact = Path(directory) / "generic-course-assignment-2026-09-13.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), artifact)
            stripped = Path(directory) / "stripped.docx"
            with zipfile.ZipFile(artifact) as source, zipfile.ZipFile(stripped, "w") as target:
                for item in source.infolist():
                    payload = source.read(item.filename)
                    if item.filename == "word/document.xml":
                        payload = payload.replace(
                            b'descr="Generic system relationship diagram"', b'descr=""'
                        )
                    target.writestr(item, payload)
            (run / "bar.md").write_text(DOCX_BAR, encoding="utf-8")
            (run / "claims.md").write_text(
                "DATE: 2026-09-13\n\n"
                "## CLAIM: Authority, coordination, and feedback are connected.\n",
                encoding="utf-8",
            )
            report = io.StringIO()
            with contextlib.redirect_stdout(report):
                assignment_docx_scan.main([str(run), "--docx", str(stripped)])

        self.assertIn("package-structure: 1", report.getvalue())

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
                "PROJECT-CONTEXT: none - synthetic assignment\nOWN-SUBMISSION: none - no earlier synthetic submission\nCASE-MATERIAL: none - no synthetic case material\nCASE-RESEARCH: none - no synthetic case research\n"
                "CONFIRMED: 2001-01-01\nCONTEXT-DIGEST: e9480117c1477001f65666233ed4ef160c1544873d6184ff730a83380429f1bf\n",
                encoding="utf-8",
            )
            (run / "heading-read.md").write_text(
                f"## HEADING-READ: {artifact.name}\n"
                f"DRAFT: {file_digest.sha256(artifact)}\n"
                "ROUTE: separate context\n"
                "SENTENCES: 0 factual, 0 clinician's own\n"
                "CONTEXT-DIGEST: e9480117c1477001f65666233ed4ef160c1544873d6184ff730a83380429f1bf\n"
                "CONTEXT-VERDICT: agrees\n"
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
