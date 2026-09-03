"""Public-CLI tests for the course-assignment deck grader.

Every deck, bar, and claim is synthetic. No patient is represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import deck_scan as scan
from grader_conformance import for_module


GraderConformance = for_module(scan)


A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"


def paragraph(text: str, *, points: int = 28) -> str:
    return (
        f'<a:p><a:r><a:rPr sz="{points * 100}"/><a:t>{text}</a:t>'
        f'</a:r><a:endParaRPr sz="{points * 100}"/></a:p>'
    )


def slide_xml(title: str, *bullets: str, points: int = 28) -> str:
    body = "".join(paragraph(item, points=points) for item in bullets)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree>
  <p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:txBody><a:bodyPr/><a:lstStyle/>{paragraph(title, points=points)}</p:txBody></p:sp>
  <p:sp><p:nvSpPr><p:cNvPr id="3" name="Content"/><p:cNvSpPr/><p:nvPr><p:ph type="body"/></p:nvPr></p:nvSpPr><p:txBody><a:bodyPr/><a:lstStyle/>{body}</p:txBody></p:sp>
</p:spTree></p:cSld></p:sld>'''


def notes_xml(*paragraphs: str, points: int = 12) -> str:
    body = "".join(paragraph(text, points=points) for text in paragraphs)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<p:notes xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree>
  <p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes"/><p:cNvSpPr/><p:nvPr><p:ph type="body"/></p:nvPr></p:nvSpPr><p:txBody><a:bodyPr/><a:lstStyle/>{body}</p:txBody></p:sp>
</p:spTree></p:cSld></p:notes>'''


def table_slide_xml(text: str, *, points: int = 28) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree>
  <p:graphicFrame><a:graphic><a:graphicData><a:tbl><a:tr><a:tc><a:txBody>
    <a:bodyPr/><a:lstStyle/>{paragraph(text, points=points)}
  </a:txBody></a:tc></a:tr></a:tbl></a:graphicData></a:graphic></p:graphicFrame>
</p:spTree></p:cSld></p:sld>'''


BAR = """\
ASSIGNMENT: https://example.test/assignment
SIGNED: 2026-09-02
ARTIFACT: deck
SLIDE-MAX: 2
BULLETS-PER-SLIDE: 2
WORDS-PER-BULLET: 6
FONT-POINTS: 30
FONT-DIRECTION: ceiling
SOURCE-CLASSES: society guideline | peer-reviewed | government | tertiary reference | market source
RECENCY-WINDOW-YEARS: 2
"""


class Run:
    def __init__(self, root: Path):
        self.root = root
        self.deck = root / "synthetic.pptx"
        (root / "bar.md").write_text(BAR, encoding="utf-8")
        (root / "claims.md").write_text(
            "DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000.\n",
            encoding="utf-8",
        )

    def write_deck(self, slides: tuple[str, ...], notes: tuple[str, ...] = ()) -> None:
        with zipfile.ZipFile(self.deck, "w") as archive:
            for index, xml in enumerate(slides, 1):
                archive.writestr(f"ppt/slides/slide{index}.xml", xml)
            for index, xml in enumerate(notes, 1):
                archive.writestr(f"ppt/notesSlides/notesSlide{index}.xml", xml)

    def grade(self, *extra: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = scan.main([str(self.root), "--pptx", str(self.deck), *extra])
        return status, stdout.getvalue(), stderr.getvalue()


class TheDeckContainerReadsOnlyTheSlideFace(unittest.TestCase):
    def test_a_clean_deck_is_counted_without_private_text(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (slide_xml("Plan", "Build-out costs $47,000", "Lease term is two years"),),
                (notes_xml("Narrative may exceed six words and use 12-point type."),),
            )
            status, stdout, stderr = run.grade()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("slides read", stdout)
        for row in scan.ROWS:
            self.assertIn(f"{row}: 0", stdout)
        self.assertNotIn("Build-out", stdout)

    def test_container_findings_move_with_slide_face_content_not_notes(self):
        long_line = "one two three four five six seven"
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "short line"),), (notes_xml(long_line),))
            note_status, _, _ = run.grade()
            run.write_deck((slide_xml("Plan", long_line),), (notes_xml("short line"),))
            face_status, stdout, _ = run.grade()

        self.assertEqual(0, note_status)
        self.assertEqual(1, face_status)
        self.assertIn(f"{scan.WORDS_PER_BULLET}: 1", stdout)

    def test_font_direction_is_applied_to_slide_face_only(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Within limit", points=32),), (notes_xml("Small notes", points=12),))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn(f"{scan.FONT_POINTS}: 1", stdout)


class CostedClaimsReadSlidesAndSpeakerNotes(unittest.TestCase):
    def test_an_unrecorded_cost_on_either_population_is_a_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Unrecorded $19,500"),), (notes_xml("Recorded $47,000"),))
            face_status, _, _ = run.grade()
            run.write_deck((slide_xml("Plan", "Recorded $47,000"),), (notes_xml("Unrecorded $19,500"),))
            notes_status, stdout, _ = run.grade()

        self.assertEqual(1, face_status)
        self.assertEqual(1, notes_status)
        self.assertIn(f"{scan.UNTRACED_COST}: 1", stdout)

    def test_recorded_costs_on_both_populations_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000 and equipment costs $19,500.\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),), (notes_xml("Equipment $19,500"),))
            status, _, _ = run.grade()

        self.assertEqual(0, status)

    def test_a_cost_outside_a_claim_heading_does_not_trace_the_deck(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: The site needs renovation.\nRESTATEMENT: Costs $47,000.\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn(f"{scan.UNTRACED_COST}: 1", stdout)

    def test_ungrouped_costs_are_not_truncated_to_three_digits(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: Initial fee is $470.\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47000"),))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn(f"{scan.UNTRACED_COST}: 1", stdout)

    def test_table_text_is_in_the_container_and_claim_populations(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((table_slide_xml("one two three four five six seven costs $19,500"),))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn(f"{scan.WORDS_PER_BULLET}: 1", stdout)
        self.assertIn(f"{scan.UNTRACED_COST}: 1", stdout)


class AnUnreadableOrUnsignedBarDidNotScan(unittest.TestCase):
    def test_every_required_field_is_required_and_artifact_is_deck(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            for field in scan.REQUIRED_BAR_FIELDS:
                original = (run.root / "bar.md").read_text(encoding="utf-8")
                without = "\n".join(line for line in original.splitlines() if not line.startswith(field + ":")) + "\n"
                (run.root / "bar.md").write_text(without, encoding="utf-8")
                status, _, stderr = run.grade()
                self.assertEqual(2, status, field)
                self.assertIn(field, stderr)
                (run.root / "bar.md").write_text(original, encoding="utf-8")

            (run.root / "bar.md").write_text(BAR.replace("ARTIFACT: deck", "ARTIFACT: paper"), encoding="utf-8")
            status, _, stderr = run.grade()

        self.assertEqual(2, status)
        self.assertIn("deck", stderr)


if __name__ == "__main__":
    unittest.main()
