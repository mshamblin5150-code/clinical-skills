"""Shared-grader conformance for the course-assignment DOCX scanner."""

from __future__ import annotations

import unittest
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import assignment_docx
import assignment_docx_scan as scan
import file_digest
from grader_conformance import EmptyPopulationInput, for_module


GraderConformance = for_module(scan)


class PackageTest(unittest.TestCase):
    def test_every_figure_needs_alt_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "assignment.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), artifact)
            with zipfile.ZipFile(artifact) as archive:
                document = ElementTree.fromstring(archive.read("word/document.xml"))
                paragraphs = scan._paragraphs(document)
                drawing = next(document.iter(scan.WP + "docPr"))
                drawing.append(
                    ElementTree.Element(
                        scan.WP + "docPr", {"id": "2", "name": "Unlabeled figure"}
                    )
                )
                replacement = ElementTree.tostring(document, encoding="utf-8")
                parts = {name: archive.read(name) for name in archive.namelist()}
            parts["word/document.xml"] = replacement
            with zipfile.ZipFile(artifact, "w") as archive:
                for name, payload in parts.items():
                    archive.writestr(name, payload)
            with zipfile.ZipFile(artifact) as archive:
                findings = scan._package(archive, paragraphs)
        self.assertTrue(any("alt text" in finding.detail for finding in findings))

    def test_missing_parts_are_reported_in_the_package_row(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "assignment.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), artifact)
            with zipfile.ZipFile(artifact) as archive:
                parts = {
                    name: archive.read(name)
                    for name in archive.namelist()
                    if name not in {"word/styles.xml", "word/header1.xml"}
                }
            with zipfile.ZipFile(artifact, "w") as archive:
                for name, payload in parts.items():
                    archive.writestr(name, payload)
            with zipfile.ZipFile(artifact) as archive:
                document = ElementTree.fromstring(archive.read("word/document.xml"))
                findings = scan._package(archive, scan._paragraphs(document))
        self.assertTrue(any("missing package parts" in item.detail for item in findings))

    def test_a_missing_relationship_image_is_a_package_finding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "assignment.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), artifact)
            with zipfile.ZipFile(artifact) as archive:
                parts = {
                    name: archive.read(name)
                    for name in archive.namelist()
                    if name != "word/media/relationship.png"
                }
            with zipfile.ZipFile(artifact, "w") as archive:
                for name, payload in parts.items():
                    archive.writestr(name, payload)
            with zipfile.ZipFile(artifact) as archive:
                document = ElementTree.fromstring(archive.read("word/document.xml"))
                findings = scan._package(archive, scan._paragraphs(document))
        self.assertTrue(any("media target" in item.detail for item in findings))

    def test_the_promised_reference_style_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "assignment.docx"
            assignment_docx.build(assignment_docx.fixture_spec(), artifact)
            with zipfile.ZipFile(artifact) as archive:
                parts = {name: archive.read(name) for name in archive.namelist()}
            parts["word/styles.xml"] = parts["word/styles.xml"].replace(
                b'w:styleId="Reference"', b'w:styleId="RemovedReference"'
            )
            with zipfile.ZipFile(artifact, "w") as archive:
                for name, payload in parts.items():
                    archive.writestr(name, payload)
            with zipfile.ZipFile(artifact) as archive:
                document = ElementTree.fromstring(archive.read("word/document.xml"))
                findings = scan._package(archive, scan._paragraphs(document))
        self.assertTrue(any("Reference style" in item.detail for item in findings))


def empty_population_input(root: Path) -> EmptyPopulationInput:
    run = root / "generic-course-assignment"
    retained = run / "render" / "pass-1"
    retained.mkdir(parents=True)
    artifact = root / "generic-course-assignment-2026-09-13.docx"
    assignment_docx.build(assignment_docx.fixture_spec(), artifact)
    (run / "bar.md").write_text(
        "ASSIGNMENT: https://example.invalid/assignment\n"
        "SIGNED: 2026-09-13\nARTIFACT: docx\nSUBMISSION-TYPE: file-upload\n"
        "WORD-MIN: 1\nWORD-MAX: 200\nREFERENCE-MIN: 1\n"
        "SOURCE-CLASSES: peer-reviewed | government\nRECENCY-WINDOW-YEARS: 5\n",
        encoding="utf-8",
    )
    (run / "claims.md").write_text("DATE: 2026-09-13\n", encoding="utf-8")
    (retained / "page-1.png").write_bytes(b"retained page pixels")
    (retained / "assignment-docx.pdf").write_bytes(b"page-faithful export")
    file_digest.write_recorded_sha256(
        retained / scan.FINGERPRINT_FILE, file_digest.sha256(artifact)
    )
    (run / "rendered.md").write_text(
        f"## RENDERED: {artifact.name}\nPASS: 1\nPAGES: 1 of 1 read\n"
        "SOURCE: word-pdf\nUNSEEN: none\nREAD: every page\n"
        "VERDICT: clean - all content is readable\n",
        encoding="utf-8",
    )
    return EmptyPopulationInput(
        argv=(str(run), "--docx", str(artifact)),
        population_size=lambda result: result.claim_records,
    )


if __name__ == "__main__":
    unittest.main()
