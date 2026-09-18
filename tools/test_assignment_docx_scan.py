"""Shared-grader conformance for the course-assignment DOCX scanner."""

from __future__ import annotations

import unittest
import tempfile
import zipfile
from dataclasses import replace
from pathlib import Path
from xml.etree import ElementTree

import assignment_docx
import assignment_docx_scan as scan
import file_digest
import research_ledger
import run_grader
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


class WordRangeTest(unittest.TestCase):
    def test_word_maximum_is_recorded_but_not_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            inputs = empty_population_input(Path(directory))
            run = Path(inputs.argv[0])
            artifact = Path(inputs.argv[2])
            bar = (run / "bar.md").read_text(encoding="utf-8")
            (run / "bar.md").write_text(
                bar.replace("WORD-MAX: 200", "WORD-MAX: 1"),
                encoding="utf-8",
            )
            parsed = run_grader.Parsed(
                source=str(run), values={"--docx": str(artifact)}
            )

            bounded = scan.survey(scan.load(parsed))
            (run / "bar.md").write_text(
                bar.replace("WORD-MAX: 200", "WORD-MAX: none"),
                encoding="utf-8",
            )
            unbounded = scan.survey(scan.load(parsed))

        self.assertFalse(any(item.kind == scan.WORD_RANGE for item in bounded.findings))
        self.assertFalse(any(item.kind == scan.WORD_RANGE for item in unbounded.findings))

    def test_word_minimum_remains_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            inputs = empty_population_input(Path(directory))
            run = Path(inputs.argv[0])
            artifact = Path(inputs.argv[2])
            bar = (run / "bar.md").read_text(encoding="utf-8")
            (run / "bar.md").write_text(
                bar.replace("WORD-MIN: 1", "WORD-MIN: 1000").replace(
                    "WORD-MAX: 200", "WORD-MAX: none"
                ),
                encoding="utf-8",
            )
            parsed = run_grader.Parsed(
                source=str(run), values={"--docx": str(artifact)}
            )

            result = scan.survey(scan.load(parsed))

        self.assertTrue(any(item.kind == scan.WORD_RANGE for item in result.findings))


class CitationClaimTraceTest(unittest.TestCase):
    def test_first_name_citation_traces_only_the_matching_first_initial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            inputs = empty_population_input(Path(directory))
            run = Path(inputs.argv[0])
            artifact = Path(inputs.argv[2])
            entry = "Williams, S. (2019). A study. Journal of Care."
            spec = assignment_docx.fixture_spec()
            spec = replace(
                spec,
                sections=(assignment_docx.Section(
                    "Purpose and Scope",
                    ("The result was reported (Sarah Williams, 2019).",),
                ),),
                references=(entry,),
            )
            assignment_docx.build(spec, artifact, force=True)
            file_digest.write_recorded_sha256(
                run / "render" / "pass-1" / scan.FINGERPRINT_FILE,
                file_digest.sha256(artifact),
            )
            heading = "The result was reported."
            claim = (
                f"DATE: 2026-09-13\n\n## CLAIM: {heading}\n"
                "STATUS: sourced\n"
                f"REFERENCE: {entry}\n"
                "REFUTATION: stands - the result appears in the article.\n"
                f"TESTED-HEADING: {research_ledger.heading_digest(heading)}\n"
                "SECOND-ROUTE: article page -> independent reader\n"
            )
            (run / "claims.md").write_text(claim, encoding="utf-8")
            parsed = run_grader.Parsed(source=str(run), values={"--docx": str(artifact)})
            matching = scan.survey(scan.load(parsed))
            (run / "claims.md").write_text(
                claim.replace("Williams, S.", "Williams, R."), encoding="utf-8"
            )
            wrong_initial = scan.survey(scan.load(parsed))

        self.assertNotIn(
            scan.UNTRACED_CITATION,
            {item.kind for item in matching.findings},
            matching.findings,
        )
        self.assertIn(scan.UNTRACED_CITATION, {item.kind for item in wrong_initial.findings})


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
