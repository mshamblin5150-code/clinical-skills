"""Public-CLI tests for the course-assignment deck grader.

Every deck, bar, and claim is synthetic. No patient is represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import io
import hashlib
import re
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import deck_scan as scan
import file_digest
import render_pass
import research_ledger
from grader_conformance import (
    EmptyPopulationInput,
    UnreadRemainderInput,
    for_module,
    unread_remainder_conformance,
)


GraderConformance = for_module(scan)
POWERPOINT_FIXTURE = Path(__file__).with_name("testdata") / "deck-scan-smartart-chart.pptx"
MISSING_DIAGRAM_FIXTURE = (
    Path(__file__).with_name("testdata")
    / "deck-scan-smartart-chart-missing-diagram.pptx"
)
CURRENCY_FORMAT_FIXTURE = (
    Path(__file__).with_name("testdata")
    / "deck-scan-smartart-chart-currency-format.pptx"
)


A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
DGM = "http://schemas.openxmlformats.org/drawingml/2006/diagram"
DSP = "http://schemas.microsoft.com/office/drawing/2008/diagram"
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
PACKAGE_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


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


def object_slide_xml(
    *bullets: str,
    diagram: str | None = None,
    chart: str | None = None,
    ordinary_title: bool = True,
) -> str:
    objects = []
    if diagram:
        objects.append(
            f'<p:graphicFrame><a:graphic><a:graphicData uri="{DGM}">'
            f'<dgm:relIds xmlns:dgm="{DGM}" xmlns:r="{R}" r:dm="{diagram}"/>'
            '</a:graphicData></a:graphic></p:graphicFrame>'
        )
    if chart:
        objects.append(
            f'<p:graphicFrame><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart">'
            f'<c:chart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:r="{R}" r:id="{chart}"/>'
            '</a:graphicData></a:graphic></p:graphicFrame>'
        )
    ordinary_text = (
        slide_xml("Synthetic title", *bullets).split("<p:spTree>", 1)[1].split("</p:spTree>", 1)[0]
        if ordinary_title
        else ""
    )
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<p:sld xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree>'
        f'{ordinary_text}'
        f'{"".join(objects)}</p:spTree></p:cSld></p:sld>'
    )


def relationships_xml(*relationships: tuple[str, str, str]) -> str:
    rows = "".join(
        f'<Relationship Id="{identifier}" Type="{kind}" Target="{target}"/>'
        for identifier, kind, target in relationships
    )
    return f'<Relationships xmlns="{PACKAGE_REL}">{rows}</Relationships>'


def diagram_data_xml(
    model_id: str,
    text: str,
    *,
    drawing_id: str | None = None,
) -> str:
    extension = (
        f'<dgm:extLst><a:ext uri="{DSP}"><dsp:dataModelExt xmlns:dsp="{DSP}" '
        f'relId="{drawing_id}"/></a:ext></dgm:extLst>'
        if drawing_id
        else ""
    )
    return (
        f'<dgm:dataModel xmlns:dgm="{DGM}" xmlns:a="{A}"><dgm:ptLst>'
        f'<dgm:pt modelId="{model_id}"><dgm:prSet/><dgm:t><a:bodyPr/><a:lstStyle/>'
        f'{paragraph(text)}</dgm:t></dgm:pt></dgm:ptLst>{extension}</dgm:dataModel>'
    )


def diagram_drawing_xml(model_id: str, text: str, *, points: int = 28) -> str:
    return (
        f'<dsp:drawing xmlns:dsp="{DSP}" xmlns:a="{A}"><dsp:spTree>'
        f'<dsp:sp modelId="{model_id}"><dsp:txBody><a:bodyPr/><a:lstStyle/>'
        f'{paragraph(text, points=points)}</dsp:txBody></dsp:sp>'
        f'</dsp:spTree></dsp:drawing>'
    )


def chart_xml() -> str:
    return f'''<c:chartSpace xmlns:c="{C}" xmlns:a="{A}"><c:chart>
<c:title><c:tx><c:rich>{paragraph("Synthetic households")}</c:rich></c:tx></c:title>
<c:plotArea><c:barChart><c:ser>
<c:idx val="0"/><c:tx><c:v>Program total</c:v></c:tx>
<c:dLbls>
  <c:dLbl><c:idx val="0"/><c:numFmt formatCode="General" sourceLinked="0"/><c:showVal val="1"/></c:dLbl>
  <c:dLbl><c:idx val="1"/><c:numFmt formatCode="0%" sourceLinked="0"/><c:showVal val="1"/></c:dLbl>
</c:dLbls>
<c:cat><c:strLit><c:pt idx="0"><c:v>Households</c:v></c:pt><c:pt idx="1"><c:v>Participation</c:v></c:pt><c:pt idx="2"><c:v>Stored only</c:v></c:pt></c:strLit></c:cat>
<c:val><c:numLit><c:pt idx="0"><c:v>325</c:v></c:pt><c:pt idx="1"><c:v>0.42</c:v></c:pt><c:pt idx="2"><c:v>999</c:v></c:pt></c:numLit></c:val>
</c:ser></c:barChart></c:plotArea></c:chart></c:chartSpace>'''


def trusted_claim(*figures: str) -> str:
    claim = "The synthetic control records " + ", ".join(figures) + "."
    return (
        f"DATE: 2026-09-14\n\n## CLAIM: {claim}\n"
        "STATUS: sourced\n"
        "REFUTATION: stands - the source states the synthetic values.\n"
        f"TESTED-HEADING: {research_ledger.heading_digest(claim)}\n"
        "SECOND-ROUTE: publisher HTML -> synthetic source PDF\n"
    )


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


class TheDeckWordCounterTreatsApostropheFormsAlike(unittest.TestCase):
    def test_ascii_and_typographic_apostrophes_have_the_same_word_count(self):
        self.assertEqual(3, len(scan.WORD.findall("the mayor's plan")))
        self.assertEqual(3, len(scan.WORD.findall("the mayor’s plan")))


class Run:
    def __init__(self, root: Path):
        self.root = root
        self.deck = root / "synthetic.pptx"
        (root / "bar.md").write_text(BAR, encoding="utf-8")
        (root / "claims.md").write_text(
            "DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000.\n"
            "STATUS: sourced\n"
            "REFUTATION: stands - the source states this cost.\n"
            "TESTED-HEADING: 1cd871eac5cc0b4ea522c820edf8c7855dcc8367d13aba2b4fa43021041eaf66\n"
            "SECOND-ROUTE: publisher HTML -> market report PDF\n",
            encoding="utf-8",
        )

    def write_deck(
        self,
        slides: tuple[str, ...],
        notes: tuple[str, ...] = (),
        parts: dict[str, str] | None = None,
    ) -> None:
        with zipfile.ZipFile(self.deck, "w") as archive:
            for index, xml in enumerate(slides, 1):
                archive.writestr(f"ppt/slides/slide{index}.xml", xml)
            for index, xml in enumerate(notes, 1):
                archive.writestr(f"ppt/notesSlides/notesSlide{index}.xml", xml)
            for name, xml in (parts or {}).items():
                archive.writestr(name, xml)
        self.write_heading_read()

    def write_heading_read(self) -> None:
        digest = hashlib.sha256(self.deck.read_bytes()).hexdigest()
        (self.root / "heading-read.md").write_text(
            f"## HEADING-READ: {self.deck.name}\nDRAFT: {digest}\n"
            "ROUTE: separate context\nSENTENCES: 0 factual, 0 clinician's own\nVERDICT: clean\n",
            encoding="utf-8",
        )

    def grade(self, *extra: str, bind: bool = True) -> tuple[int, str, str]:
        if bind:
            if not (self.root / "render" / "pass-1").is_dir():
                self.retain(1, 1)
            if not (self.root / "rendered.md").is_file():
                self.write_rendered()
            if not (self.root / "adversarial.md").is_file():
                self.write_adversarial()
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = scan.main([str(self.root), "--pptx", str(self.deck), *extra])
        return status, stdout.getvalue(), stderr.getvalue()

    def retain(self, number: int, images: int, *, fingerprint: bool = True) -> None:
        retained = self.root / "render" / f"pass-{number}"
        retained.mkdir(parents=True)
        for index in range(1, images + 1):
            (retained / f"slide-{index}.png").write_bytes(b"synthetic")
        if fingerprint:
            (retained / "deck.sha256").write_text(
                file_digest.sha256(self.deck) + "\n", encoding="ascii"
            )

    def write_rendered(
        self,
        *,
        deck: str = "synthetic.pptx",
        pass_number: str = "1",
        slides: str = "1 of 1 read",
        source: str = "powerpoint-pdf",
        unseen: str = "none",
        verdict: str = "clean - every slide is readable",
    ) -> None:
        (self.root / "rendered.md").write_text(
            "\n".join(
                (
                    f"## RENDERED: {deck}",
                    f"PASS: {pass_number}",
                    f"SLIDES: {slides}",
                    f"SOURCE: {source}",
                    f"UNSEEN: {unseen}",
                    "READ: every retained slide against the deck and bar.md",
                    f"VERDICT: {verdict}",
                    "",
                )
            ),
            encoding="utf-8",
        )

    def write_adversarial(
        self,
        *,
        deck: str = "synthetic.pptx",
        pass_number: str | None = None,
        slides: str | None = None,
        unseen: str = "none",
        claims: str | None = None,
        verdict: str = "clean - every slide agrees with its record",
    ) -> None:
        digest = file_digest.sha256(self.root / "claims.md") if claims is None else claims
        passes = render_pass.read_passes(self.root / "render")
        if pass_number is None:
            pass_number = str(passes[-1][0]) if passes else "1"
        if slides is None:
            png_count = sum(1 for path in passes[-1][1].glob("*.png")) if passes else 0
            with zipfile.ZipFile(self.deck) as archive:
                slide_count = sum(bool(scan.SLIDE_PART.fullmatch(name)) for name in archive.namelist())
            slides = f"{png_count} of {slide_count} read"
        (self.root / "adversarial.md").write_text(
            f"## ADVERSARIAL: {deck}\n"
            f"PASS: {pass_number}\n"
            f"SLIDES: {slides}\n"
            f"UNSEEN: {unseen}\n"
            f"CLAIMS: {digest}\n"
            f"VERDICT: {verdict}\n",
            encoding="utf-8",
        )

    def write_reread(self, *, fingerprint: str | None = None) -> None:
        digest = file_digest.sha256(self.deck) if fingerprint is None else fingerprint
        (self.root / "reread.md").write_text(
            f"## REREAD: {self.deck.stem}\n"
            "POST-URL: https://example.test/submission\n"
            "POSTED: 2026-09-13\n"
            "READ: 2026-09-13\n"
            f"SUBMISSION-SHA256: {digest}\n"
            "VERDICT: matches - the submitted deck was read back from the LMS\n",
            encoding="utf-8",
        )

    def terminal(self, *, bind: bool = True) -> tuple[int, str, str]:
        if bind and not (self.root / "reread.md").is_file():
            self.write_reread()
        with mock.patch.object(
            scan.aar_scan,
            "completion_gate",
            return_value=(False, "the after-action review: clean"),
        ):
            return self.grade("--submission", self.deck.stem, bind=bind)


def empty_population_input(root: Path) -> EmptyPopulationInput:
    empty_root, twin_root = root / "empty", root / "twin"
    empty_root.mkdir()
    twin_root.mkdir()
    empty, twin = Run(empty_root), Run(twin_root)
    empty.write_deck(
        ("<p:sld xmlns:p='http://schemas.openxmlformats.org/presentationml/2006/main'/>",)
    )
    twin.write_deck((slide_xml("Synthetic title"),))
    for run in (empty, twin):
        run.retain(1, 1)
        run.write_rendered()
        run.write_adversarial()
    return EmptyPopulationInput(
        (str(empty.root), "--pptx", str(empty.deck)),
        population_size=lambda result: result.font_runs_read,
        twin_argv=(str(twin.root), "--pptx", str(twin.deck)),
    )


def unread_remainder_input(root: Path) -> UnreadRemainderInput:
    unread_root, twin_root = root / "unread", root / "twin"
    unread_root.mkdir()
    twin_root.mkdir()

    def configured(path: Path, fixture: Path) -> Run:
        run = Run(path)
        run.deck.write_bytes(fixture.read_bytes())
        run.write_heading_read()
        run.retain(1, 2)
        run.write_rendered(slides="2 of 2 read")
        (run.root / "bar.md").write_text(
            BAR.replace("WORDS-PER-BULLET: 6", "WORDS-PER-BULLET: 20"),
            encoding="utf-8",
        )
        (run.root / "claims.md").write_text(
            trusted_claim("$99,000", "325", "42%"), encoding="utf-8"
        )
        run.write_adversarial()
        return run

    unread = configured(unread_root, MISSING_DIAGRAM_FIXTURE)
    twin = configured(twin_root, POWERPOINT_FIXTURE)
    return UnreadRemainderInput(
        (str(unread.root), "--pptx", str(unread.deck)),
        (str(twin.root), "--pptx", str(twin.deck)),
        unread_remainder=lambda result: result.unread_members
        + result.heading_read_unread,
    )


UnreadRemainderConformance = unread_remainder_conformance(scan)


class TheDeckContainerReadsOnlyTheSlideFace(unittest.TestCase):
    def test_a_slide_with_no_face_text_exits_two_after_printing_its_report(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                ("<p:sld xmlns:p='http://schemas.openxmlformats.org/presentationml/2006/main'/>",)
            )
            status, stdout, stderr = run.grade()

        self.assertEqual(2, status)
        self.assertIn("font runs read    0", stdout)
        self.assertIn("no text run was read from any slide face", stderr)

    def test_a_clean_deck_is_counted_without_private_text(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (slide_xml("Plan", "Build-out costs $47,000", "Lease term is two years"),),
                (notes_xml("Narrative may exceed six words and use small type."),),
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

    def test_layout_alternative_and_master_text_are_not_slide_face_text(self):
        slide = slide_xml("Synthetic title").replace(
            "</p:spTree>",
            '<p:pic><p:nvPicPr><p:cNvPr id="4" name="Picture" '
            'descr="Alternative figure 881"/></p:nvPicPr></p:pic></p:spTree>',
        )
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (slide,),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId1",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
                            "../slideLayouts/slideLayout1.xml",
                        ),
                    ),
                    "ppt/slideLayouts/slideLayout1.xml": slide_xml(
                        "Layout figure 771"
                    ),
                    "ppt/notesMasters/notesMaster1.xml": notes_xml(
                        "Notes master figure 661"
                    ),
                    "ppt/handoutMasters/handoutMaster1.xml": notes_xml(
                        "Handout master figure 551"
                    ),
                },
            )
            status, stdout, _ = run.grade("--show")

        self.assertEqual(0, status)
        self.assertIn("figures           0", stdout)
        for excluded in ("881", "771", "661", "551"):
            self.assertNotIn(excluded, stdout)


class SmartArtIsSlideFaceText(unittest.TestCase):
    def test_a_smartart_paragraph_enters_the_bullet_word_figure_and_font_populations(self):
        text = "one two three four five six seven costs $19,500"
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(diagram="rId2"),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/diagramData",
                            "../diagrams/data1.xml",
                        ),
                        (
                            "rId3",
                            "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing",
                            "../diagrams/drawing1.xml",
                        ),
                    ),
                    "ppt/diagrams/data1.xml": diagram_data_xml("node-1", text),
                    "ppt/diagrams/drawing1.xml": diagram_drawing_xml("node-1", text),
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("diagram text read 1", stdout)
        self.assertIn(f"{scan.WORDS_PER_BULLET}: 1", stdout)
        self.assertIn(f"{scan.FONT_POINTS}: 0", stdout)
        self.assertIn(f"{scan.UNTRACED_FIGURE}: 1", stdout)

    def test_smartart_font_grading_uses_the_matching_drawing_part_size(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(diagram="rId2"),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/diagramData",
                            "../diagrams/data1.xml",
                        ),
                        (
                            "rId3",
                            "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing",
                            "../diagrams/drawing1.xml",
                        ),
                    ),
                    "ppt/diagrams/data1.xml": diagram_data_xml("node-1", "Within limit"),
                    "ppt/diagrams/drawing1.xml": diagram_drawing_xml(
                        "node-1", "Duplicated drawing text", points=32
                    ),
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("font runs read    2", stdout)
        self.assertIn(f"{scan.FONT_POINTS}: 1", stdout)

    def test_smartart_drawing_text_is_not_read_or_counted_twice(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(diagram="rId2"),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/diagramData",
                            "../diagrams/data1.xml",
                        ),
                        (
                            "rId3",
                            "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing",
                            "../diagrams/drawing1.xml",
                        ),
                    ),
                    "ppt/diagrams/data1.xml": diagram_data_xml(
                        "node-1", "Data value $19,500"
                    ),
                    "ppt/diagrams/drawing1.xml": diagram_drawing_xml(
                        "node-1", "Drawing duplicate $88,000"
                    ),
                },
            )
            status, stdout, _ = run.grade("--show")

        self.assertEqual(1, status)
        self.assertIn("figures           1", stdout)
        self.assertIn("19,500 has no claim record", stdout)
        self.assertNotIn("88,000", stdout)

    def test_each_smartart_uses_the_drawing_relationship_named_by_its_data_part(self):
        slide = object_slide_xml(diagram="rId2").replace(
            "</p:spTree>",
            f'<p:graphicFrame><a:graphic><a:graphicData uri="{DGM}">'
            f'<dgm:relIds xmlns:dgm="{DGM}" xmlns:r="{R}" r:dm="rId4"/>'
            '</a:graphicData></a:graphic></p:graphicFrame></p:spTree>',
        )
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (slide,),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/diagramData",
                            "../diagrams/data1.xml",
                        ),
                        (
                            "rId3",
                            "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing",
                            "../diagrams/drawing1.xml",
                        ),
                        (
                            "rId4",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/diagramData",
                            "../diagrams/data2.xml",
                        ),
                        (
                            "rId5",
                            "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing",
                            "../diagrams/drawing2.xml",
                        ),
                    ),
                    "ppt/diagrams/data1.xml": diagram_data_xml(
                        "node-1", "First diagram", drawing_id="rId3"
                    ),
                    "ppt/diagrams/drawing1.xml": diagram_drawing_xml(
                        "node-1", "First diagram", points=28
                    ),
                    "ppt/diagrams/data2.xml": diagram_data_xml(
                        "node-2", "Second diagram", drawing_id="rId5"
                    ),
                    "ppt/diagrams/drawing2.xml": diagram_drawing_xml(
                        "node-2", "Second diagram", points=32
                    ),
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("diagram text read 2", stdout)
        self.assertIn(f"{scan.FONT_POINTS}: 1", stdout)


class ChartTextIsSlideFaceText(unittest.TestCase):
    def test_chart_text_and_displayed_general_and_percent_labels_enter_the_figure_population(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(chart="rId2"),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                            "../charts/chart1.xml",
                        ),
                    ),
                    "ppt/charts/chart1.xml": chart_xml(),
                },
            )
            status, stdout, _ = run.grade("--show")

        self.assertEqual(1, status)
        self.assertIn("chart text read   7", stdout)
        self.assertIn("figures           2", stdout)
        self.assertIn("325 has no claim record", stdout)
        self.assertIn("42% has no claim record", stdout)
        self.assertNotIn("999 has no claim record", stdout)
        self.assertIn(f"{scan.WORDS_PER_BULLET}: 0", stdout)

    def test_a_chart_only_slide_counts_as_read_slide_face_text(self):
        unlabeled = chart_xml().replace('<c:showVal val="1"', '<c:showVal val="0"')
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(chart="rId2", ordinary_title=False),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                            "../charts/chart1.xml",
                        ),
                    ),
                    "ppt/charts/chart1.xml": unlabeled,
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("font runs read    0", stdout)
        self.assertIn("chart text read   5", stdout)

    def test_general_formats_binary_rounding_noise_as_powerpoint_displays_it(self):
        noisy = (
            chart_xml()
            .replace("<c:v>325</c:v>", "<c:v>4.4000000000000004</c:v>", 1)
            .replace(
                'formatCode="0%" sourceLinked="0"/><c:showVal val="1"',
                'formatCode="0%" sourceLinked="0"/><c:showVal val="0"',
                1,
            )
        )
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(chart="rId2"),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                            "../charts/chart1.xml",
                        ),
                    ),
                    "ppt/charts/chart1.xml": noisy,
                },
            )
            status, stdout, _ = run.grade("--show")

        self.assertEqual(1, status)
        self.assertIn("4.4 has no claim record", stdout)
        self.assertNotIn("4.4000000000000004 has no claim record", stdout)

    def test_a_linked_chart_title_is_read_from_its_cached_value(self):
        linked_title = chart_xml().replace(
            f'<c:tx><c:rich>{paragraph("Synthetic households")}</c:rich></c:tx>',
            '<c:tx><c:strRef><c:f>Sheet1!$A$1</c:f><c:strCache>'
            '<c:pt idx="0"><c:v>Linked synthetic title</c:v></c:pt>'
            '</c:strCache></c:strRef></c:tx>',
            1,
        )
        linked_title = linked_title.replace('<c:showVal val="1"', '<c:showVal val="0"')
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(chart="rId2", ordinary_title=False),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                            "../charts/chart1.xml",
                        ),
                    ),
                    "ppt/charts/chart1.xml": linked_title,
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("chart text read   5", stdout)

    def test_a_text_box_overlaid_on_a_chart_remains_a_slide_bullet(self):
        unlabeled = chart_xml().replace('<c:showVal val="1"', '<c:showVal val="0"')
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (
                    object_slide_xml(
                        "one two three four five six seven costs $19,500",
                        chart="rId2",
                    ),
                ),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                            "../charts/chart1.xml",
                        ),
                    ),
                    "ppt/charts/chart1.xml": unlabeled,
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn(f"{scan.WORDS_PER_BULLET}: 1", stdout)
        self.assertIn(f"{scan.UNTRACED_FIGURE}: 1", stdout)
        self.assertIn("chart text read   5", stdout)


class ThePowerPointAuthoredObjectControl(unittest.TestCase):
    def run_from_fixture(self, root: Path, fixture: Path = POWERPOINT_FIXTURE) -> Run:
        run = Run(root)
        run.deck.write_bytes(fixture.read_bytes())
        run.write_heading_read()
        run.retain(1, 2)
        run.write_rendered(slides="2 of 2 read")
        return run

    def make_other_findings_clean(self, run: Run) -> None:
        (run.root / "bar.md").write_text(
            BAR.replace("WORDS-PER-BULLET: 6", "WORDS-PER-BULLET: 20"),
            encoding="utf-8",
        )
        (run.root / "claims.md").write_text(
            trusted_claim("$99,000", "325", "42%"), encoding="utf-8"
        )

    def test_powerpoint_authored_smartart_and_chart_text_are_read(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.run_from_fixture(Path(temp))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("diagram text read 1", stdout)
        self.assertIn("chart text read   6", stdout)
        self.assertIn(f"{scan.WORDS_PER_BULLET}: 1", stdout)
        self.assertIn(f"{scan.UNTRACED_FIGURE}: 3", stdout)

    def test_a_copy_with_its_diagram_part_removed_exits_two(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.run_from_fixture(Path(temp), MISSING_DIAGRAM_FIXTURE)
            self.make_other_findings_clean(run)
            status, stdout, stderr = run.grade()

        self.assertEqual(2, status, stdout + stderr)
        self.assertIn("unread remainder 1", stdout)

    def test_a_copy_with_an_unmeasured_chart_format_exits_two(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.run_from_fixture(Path(temp), CURRENCY_FORMAT_FIXTURE)
            self.make_other_findings_clean(run)
            status, stdout, stderr = run.grade()

        self.assertEqual(2, status, stdout + stderr)
        self.assertIn("unread remainder 1", stdout)


class UnreadObjectMembersAreNotScanned(unittest.TestCase):
    def test_the_declared_limits_name_the_intentionally_unread_slide_surfaces(self):
        keys = {limit.key for limit in scan.DECLARED_LIMITS}
        self.assertTrue(
            {
                "slide-layout-text-unread",
                "alternative-text-unread",
                "value-axis-ticks-unread",
                "chart-font-sizes-unread",
            }.issubset(keys)
        )

    def test_missing_and_unparseable_referenced_parts_exit_two(self):
        cases = (
            (
                "missing diagram",
                object_slide_xml(diagram="rId2"),
                relationships_xml(
                    (
                        "rId2",
                        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/diagramData",
                        "../diagrams/data1.xml",
                    ),
                ),
                {},
            ),
            (
                "unparseable diagram",
                object_slide_xml(diagram="rId2"),
                relationships_xml(
                    (
                        "rId2",
                        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/diagramData",
                        "../diagrams/data1.xml",
                    ),
                    (
                        "rId3",
                        "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing",
                        "../diagrams/drawing1.xml",
                    ),
                ),
                {
                    "ppt/diagrams/data1.xml": "<broken",
                    "ppt/diagrams/drawing1.xml": diagram_drawing_xml("node-1", "Synthetic"),
                },
            ),
            (
                "unmatched diagram drawing",
                object_slide_xml(diagram="rId2"),
                relationships_xml(
                    (
                        "rId2",
                        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/diagramData",
                        "../diagrams/data1.xml",
                    ),
                    (
                        "rId3",
                        "http://schemas.microsoft.com/office/2007/relationships/diagramDrawing",
                        "../diagrams/drawing1.xml",
                    ),
                ),
                {
                    "ppt/diagrams/data1.xml": diagram_data_xml(
                        "node-1", "Synthetic diagram"
                    ),
                    "ppt/diagrams/drawing1.xml": diagram_drawing_xml(
                        "another-node", "Synthetic diagram"
                    ),
                },
            ),
            (
                "missing chart",
                object_slide_xml(chart="rId2"),
                relationships_xml(
                    (
                        "rId2",
                        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                        "../charts/chart1.xml",
                    ),
                ),
                {},
            ),
            (
                "unparseable chart",
                object_slide_xml(chart="rId2"),
                relationships_xml(
                    (
                        "rId2",
                        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                        "../charts/chart1.xml",
                    ),
                ),
                {"ppt/charts/chart1.xml": "<broken"},
            ),
        )
        for name, slide, relationships, object_parts in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                run = Run(Path(temp))
                run.write_deck(
                    (slide,),
                    parts={
                        "ppt/slides/_rels/slide1.xml.rels": relationships,
                        **object_parts,
                    },
                )
                status, stdout, stderr = run.grade()

                self.assertEqual(2, status)
                self.assertIn("unread remainder 1", stdout)
                self.assertNotIn("deck findings require review", stderr)

    def test_an_unparseable_slide_relationship_part_exits_two(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(chart="rId2"),),
                parts={"ppt/slides/_rels/slide1.xml.rels": "<broken"},
            )
            status, _, stderr = run.grade()

        self.assertEqual(2, status)
        self.assertIn("could not read the deck run", stderr)

    def test_an_unmeasured_labeled_value_format_exits_two(self):
        currency_chart = chart_xml().replace(
            'formatCode="General"', 'formatCode="$0"', 1
        ).replace(
            'formatCode="0%" sourceLinked="0"/><c:showVal val="1"',
            'formatCode="0%" sourceLinked="0"/><c:showVal val="0"',
            1,
        )
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(chart="rId2"),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                            "../charts/chart1.xml",
                        ),
                    ),
                    "ppt/charts/chart1.xml": currency_chart,
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(2, status)
        self.assertIn("unread remainder 1", stdout)

    def test_a_source_linked_label_uses_the_value_cache_format(self):
        source_linked = (
            chart_xml()
            .replace(
                '<c:numFmt formatCode="General" sourceLinked="0"',
                '<c:numFmt formatCode="General" sourceLinked="1"',
                1,
            )
            .replace("<c:numLit>", "<c:numLit><c:formatCode>$0</c:formatCode>", 1)
            .replace(
                'formatCode="0%" sourceLinked="0"/><c:showVal val="1"',
                'formatCode="0%" sourceLinked="0"/><c:showVal val="0"',
                1,
            )
        )
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(chart="rId2"),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                            "../charts/chart1.xml",
                        ),
                    ),
                    "ppt/charts/chart1.xml": source_linked,
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(2, status)
        self.assertIn("unread remainder 1", stdout)

    def test_a_pie_percentage_label_exits_two(self):
        pie_chart = (
            chart_xml()
            .replace("<c:barChart>", "<c:pieChart>")
            .replace("</c:barChart>", "</c:pieChart>")
            .replace(
                '<c:numFmt formatCode="General" sourceLinked="0"/><c:showVal val="1"',
                '<c:numFmt formatCode="General" sourceLinked="0"/><c:showVal val="0"/><c:showPercent val="1"',
                1,
            )
            .replace(
                'formatCode="0%" sourceLinked="0"/><c:showVal val="1"',
                'formatCode="0%" sourceLinked="0"/><c:showVal val="0"',
                1,
            )
        )
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml(chart="rId2"),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                            "../charts/chart1.xml",
                        ),
                    ),
                    "ppt/charts/chart1.xml": pie_chart,
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(2, status)
        self.assertIn("unread remainder 1", stdout)

    def test_a_finding_outranks_an_unread_member(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (object_slide_xml("one two three four five six seven", chart="rId2"),),
                parts={
                    "ppt/slides/_rels/slide1.xml.rels": relationships_xml(
                        (
                            "rId2",
                            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart",
                            "../charts/missing.xml",
                        ),
                    ),
                },
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("unread remainder 1", stdout)
        self.assertIn(f"{scan.WORDS_PER_BULLET}: 1", stdout)


class FiguresReadSlidesAndSpeakerNotes(unittest.TestCase):
    def test_the_field_completeness_residue_names_the_refutation_complement(self):
        self.assertIn(
            ", ".join(scan.REFUTATION_EVIDENCE_COMPLEMENT),
            scan.SOURCED_FIELD_COMPLETENESS_LIMIT.limit,
        )

    def test_a_missing_heading_read_fails_the_pre_post_deck_scan(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            (run.root / "heading-read.md").unlink()
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("missing-heading-read: 1", stdout)

    def test_a_heading_read_with_an_old_deck_digest_is_stale(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            record = run.root / "heading-read.md"
            record.write_text(
                record.read_text(encoding="utf-8").replace(
                    hashlib.sha256(run.deck.read_bytes()).hexdigest(), "0" * 64
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("heading-read-draft-mismatch: 1", stdout)

    def test_an_unrecorded_cost_on_either_population_is_a_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Unrecorded $19,500"),), (notes_xml("Recorded $47,000"),))
            face_status, _, _ = run.grade()
            run.write_deck((slide_xml("Plan", "Recorded $47,000"),), (notes_xml("Unrecorded $19,500"),))
            notes_status, stdout, _ = run.grade()

        self.assertEqual(1, face_status)
        self.assertEqual(1, notes_status)
        self.assertIn(f"{scan.UNTRACED_FIGURE}: 1", stdout)

    def test_an_unrecorded_non_dollar_number_is_a_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Serve 325 households"),))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("untraced-figure: 1", stdout)
        self.assertIn("figures           1", stdout)

    def test_a_non_dollar_number_in_a_believed_claim_heading_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: The program serves 325 households.\n"
                "STATUS: sourced\n"
                "REFUTATION: stands - the source states this figure.\n"
                "TESTED-HEADING: 0066c503fd14aec6e9dc4ae73b20f06c9483620f08616e0b4a57b30da0288e2a\n"
                "SECOND-ROUTE: publisher HTML -> market report PDF\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Serve 325 households"),))
            status, _, _ = run.grade()

        self.assertEqual(0, status)

    def test_a_non_dollar_number_only_in_a_restatement_does_not_trace_the_deck(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: The program serves local households.\n"
                "STATUS: sourced\nRESTATEMENT: The program serves 325 households.\n"
                "REFUTATION: stands - the source states the service population.\n"
                "SECOND-ROUTE: publisher HTML -> market report PDF\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Serve 325 households"),))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn(f"{scan.UNTRACED_FIGURE}: 1", stdout)

    def test_citation_year_page_locator_and_statute_number_do_not_fire(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck(
                (slide_xml("Authority (Agency, 2024)", "p. 12", "42 U.S.C. section 300"),)
            )
            status, _, _ = run.grade()

        self.assertEqual(0, status)


    def test_recorded_costs_on_both_populations_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000 and equipment costs $19,500.\n"
                "STATUS: sourced\n"
                "REFUTATION: stands - the source states both costs.\n"
                "TESTED-HEADING: 487f1e9907aefdc789e537b8642c4fff64cf89486269ceb71a39189461f27c6a\n"
                "SECOND-ROUTE: publisher HTML -> market report PDF\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),), (notes_xml("Equipment $19,500"),))
            status, _, _ = run.grade()

        self.assertEqual(0, status)

    def test_only_believed_claim_records_trace_costs(self):
        states = (
            "STATUS: unsourced - searched the named market sources.",
            "STATUS: unreadable - both instruments failed.",
            "STATUS: sourced\nREFUTATION: refuted - the source states a different cost.",
        )
        for state in states:
            with self.subTest(state=state.splitlines()[-1].split(" -", 1)[0]):
                with tempfile.TemporaryDirectory() as temp:
                    run = Run(Path(temp))
                    (run.root / "claims.md").write_text(
                        f"DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000.\n{state}\n",
                        encoding="utf-8",
                    )
                    run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
                    status, stdout, _ = run.grade()

                self.assertEqual(1, status)
                self.assertIn(f"{scan.UNTRACED_FIGURE}: 1", stdout)

    def test_a_sourced_standing_record_still_traces_its_cost(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000.\n"
                "STATUS: sourced\nREFUTATION: stands - the source states this cost.\n"
                "TESTED-HEADING: 1cd871eac5cc0b4ea522c820edf8c7855dcc8367d13aba2b4fa43021041eaf66\n"
                "SECOND-ROUTE: publisher HTML -> market report PDF\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            status, _, _ = run.grade()

        self.assertEqual(0, status)

    def test_a_sourced_record_missing_non_refutation_fields_is_still_believed(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000.\n"
                "STATUS: sourced\n"
                "REFUTATION: stands - the source states this cost.\n"
                "TESTED-HEADING: 1cd871eac5cc0b4ea522c820edf8c7855dcc8367d13aba2b4fa43021041eaf66\n"
                "SECOND-ROUTE: publisher HTML -> market report PDF\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            status, _, _ = run.grade()

        self.assertEqual(0, status)

    def test_a_cost_only_in_a_disbelieved_record_says_so(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000.\n"
                "STATUS: unsourced - no source found.\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            status, stdout, _ = run.grade("--show")

        self.assertEqual(1, status)
        self.assertIn("47,000 appears only in a disbelieved claim record", stdout)

    def test_a_cost_only_in_a_stale_tested_heading_is_disbelieved(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            claims = run.root / "claims.md"
            claims.write_text(
                claims.read_text(encoding="utf-8").replace(
                    "Build-out costs $47,000.", "Build-out costs $47,000!", 1
                ),
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            status, stdout, _ = run.grade("--show")

        self.assertEqual(1, status)
        self.assertIn("47,000 appears only in a disbelieved claim record", stdout)

    def test_a_cost_absent_from_every_record_keeps_the_existing_detail(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Unrecorded $19,500"),))
            status, stdout, _ = run.grade("--show")

        self.assertEqual(1, status)
        self.assertIn("19,500 has no claim record", stdout)

    def test_token_identity_does_not_establish_claim_support(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: An unrelated item costs $47,000.\n"
                "STATUS: sourced\nREFUTATION: stands - the source states the unrelated cost.\n"
                "TESTED-HEADING: 997d9b5858ec2e2537b0900555ca1961b9f59260d25544fd59dbedd832e47e87\n"
                "SECOND-ROUTE: publisher HTML -> market report PDF\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            status, _, _ = run.grade()

        self.assertEqual(0, status)

    def test_a_cost_outside_a_claim_heading_does_not_trace_the_deck(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: The site needs renovation.\n"
                "STATUS: sourced\nRESTATEMENT: Costs $47,000.\n"
                "REFUTATION: stands - the source states the renovation need.\n"
                "SECOND-ROUTE: publisher HTML -> market report PDF\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn(f"{scan.UNTRACED_FIGURE}: 1", stdout)

    def test_ungrouped_costs_are_not_truncated_to_three_digits(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: Initial fee is $470.\n"
                "STATUS: sourced\nREFUTATION: stands - the source states this fee.\n"
                "SECOND-ROUTE: publisher HTML -> market report PDF\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47000"),))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn(f"{scan.UNTRACED_FIGURE}: 1", stdout)

    def test_table_text_is_in_the_container_and_claim_populations(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((table_slide_xml("one two three four five six seven costs $19,500"),))
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn(f"{scan.WORDS_PER_BULLET}: 1", stdout)
        self.assertIn(f"{scan.UNTRACED_FIGURE}: 1", stdout)


class TheRenderedDeckRecordNamesTheTerminalPass(unittest.TestCase):
    def a_run(self, root: Path, *, slides: int = 1) -> Run:
        run = Run(root)
        run.write_deck(
            tuple(
                slide_xml(f"Slide {chr(64 + index)}", "Within limit")
                for index in range(1, slides + 1)
            )
        )
        return run

    def test_a_matching_highest_pass_and_clean_review_complete_the_deck(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.retain(1, 1)
            run.write_rendered()
            status, stdout, stderr = run.terminal()

        self.assertEqual((status, stderr), (0, ""))
        self.assertIn("rendered record: clean", stdout)
        self.assertIn("the after-action review: clean", stdout)

    def test_preflight_grades_format_and_the_render_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.write_rendered(source="browser")
            bad_status, _, _ = run.grade()
            run.write_rendered()
            clean_status, stdout, _ = run.grade()

        self.assertEqual(bad_status, 1)
        self.assertEqual(clean_status, 0)
        self.assertIn("rendered record: clean", stdout)

    def test_every_declared_record_field_is_well_formed_on_preflight(self):
        replacements = (
            ("synthetic.pptx", "synthetic.pdf"),
            ("PASS: 1", "PASS: 0"),
            ("SLIDES: 1 of 1 read", "SLIDES: all read"),
            ("SOURCE: powerpoint-pdf", "SOURCE: browser"),
            ("UNSEEN: none", "UNSEEN:"),
            ("READ: every retained slide against the deck and bar.md", "READ:"),
            ("VERDICT: clean - every slide is readable", "VERDICT: clean"),
        )
        for old, new in replacements:
            with self.subTest(field=old.split(":", 1)[0]):
                with tempfile.TemporaryDirectory() as temp:
                    run = self.a_run(Path(temp))
                    run.write_rendered()
                    path = run.root / "rendered.md"
                    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
                    status, _, _ = run.grade()
                self.assertEqual(status, 1)

    def test_submission_requires_a_retained_pass_and_a_record(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.write_rendered()
            no_pass, _, _ = run.terminal(bind=False)
            run.retain(1, 1)
            (run.root / "rendered.md").unlink()
            no_record, _, _ = run.terminal(bind=False)

        self.assertEqual(no_pass, 1)
        self.assertEqual(no_record, 1)

    def test_submission_accepts_a_matching_deck_fingerprint(self):
        with tempfile.TemporaryDirectory() as temp:
            status, stdout, stderr = self.a_run(Path(temp)).terminal()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("submission-fingerprint: 0", stdout)

    def test_submission_refuses_a_missing_deck_fingerprint(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.write_reread()
            reread = run.root / "reread.md"
            reread.write_text(
                re.sub(r"^SUBMISSION-SHA256:.*\n", "", reread.read_text(encoding="utf-8"), flags=re.MULTILINE),
                encoding="utf-8",
            )
            status, stdout, stderr = run.terminal()

        self.assertEqual(1, status)
        self.assertIn("deck findings require review", stderr)
        self.assertIn("submission-fingerprint: 1", stdout)

    def test_submission_refuses_a_deck_edited_after_the_reading(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.write_reread()
            run.write_deck((slide_xml("Plan", "Expansion $47,000"),))
            status, stdout, stderr = run.terminal()

        self.assertEqual(1, status)
        self.assertIn("deck findings require review", stderr)
        self.assertIn("submission-fingerprint: 1", stdout)

    def test_preflight_refuses_a_pass_without_a_fingerprint(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.retain(1, 1, fingerprint=False)
            run.write_rendered()
            status, _, _ = run.grade(bind=False)

        self.assertEqual(1, status)

    def test_preflight_refuses_a_pass_fingerprinted_for_another_deck(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.retain(1, 1)
            (run.root / "render" / "pass-1" / "deck.sha256").write_text(
                "f" * 64 + "\n", encoding="ascii"
            )
            run.write_rendered()
            status, _, _ = run.grade(bind=False)

        self.assertEqual(1, status)

    def test_submission_joins_the_highest_pass_deck_and_slide_counts(self):
        cases = (
            ({"pass_number": "1"}, (1, 1), (2, 1)),
            ({"deck": "another.pptx", "pass_number": "2"}, (1, 1), (2, 1)),
            ({"slides": "1 of 2 read", "pass_number": "2"}, (1, 1), (2, 1)),
            ({"slides": "2 of 1 read", "pass_number": "2"}, (1, 1), (2, 1)),
        )
        for rendered, first, second in cases:
            with self.subTest(rendered=rendered):
                with tempfile.TemporaryDirectory() as temp:
                    run = self.a_run(Path(temp))
                    run.retain(*first)
                    run.retain(*second)
                    run.write_rendered(**rendered)
                    status, _, _ = run.terminal()
                self.assertEqual(status, 1)

    def test_an_unrecorded_earlier_pass_is_counted_and_not_failed(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.retain(1, 1)
            run.retain(2, 1)
            run.write_rendered(pass_number="2")
            status, stdout, _ = run.terminal()

        self.assertEqual(status, 0)
        self.assertIn("retained passes without a record 1", stdout)

    def test_two_records_cannot_claim_the_same_read_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.retain(1, 1)
            run.write_rendered()
            path = run.root / "rendered.md"
            path.write_text(path.read_text(encoding="utf-8") * 2, encoding="utf-8")
            status, _, _ = run.grade()

        self.assertEqual(status, 1)


class TheAdversarialReadNamesTheDeckPassAndClaims(unittest.TestCase):
    def test_preflight_and_submission_require_a_record_for_the_highest_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Within limit"),))
            run.retain(1, 1)
            run.write_rendered()
            preflight, _, _ = run.grade(bind=False)
            submission, _, _ = run.terminal(bind=False)
            run.write_adversarial()
            clean_preflight, report, _ = run.grade(bind=False)
            clean_submission, _, _ = run.terminal()

        self.assertEqual((preflight, submission), (1, 1))
        self.assertEqual((clean_preflight, clean_submission), (0, 0))
        self.assertIn("adversarial-record: 0", report)

    def test_each_record_refusal_has_a_clean_preflight_control(self):
        cases = (
            ("missing", lambda run: (run.root / "adversarial.md").unlink()),
            ("malformed", lambda run: run.write_adversarial(pass_number="0")),
            ("other deck", lambda run: run.write_adversarial(deck="another.pptx")),
            ("old pass", lambda run: run.retain(2, 1)),
            ("other bytes", lambda run: (run.root / "render" / "pass-1" / "deck.sha256").write_text("f" * 64 + "\n", encoding="ascii")),
            ("short PNG count", lambda run: run.write_adversarial(slides="0 of 1 read")),
            ("wrong deck count", lambda run: run.write_adversarial(slides="1 of 2 read")),
            ("unseen", lambda run: run.write_adversarial(unseen="slide 1")),
            ("defect", lambda run: run.write_adversarial(verdict="defect - missing claim")),
            ("no verdict reason", lambda run: run.write_adversarial(verdict="clean")),
            ("blank verdict reason", lambda run: run.write_adversarial(verdict="clean -   ")),
            ("stale claims", lambda run: (run.root / "claims.md").write_text("revised claims\n", encoding="utf-8")),
        )
        for name, damage in cases:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as temp:
                run = Run(Path(temp))
                run.write_deck((slide_xml("Plan", "Within limit"),))
                run.retain(1, 1)
                run.write_rendered()
                run.write_adversarial()
                control, report, _ = run.grade(bind=False)
                damage(run)
                refused, failed_report, _ = run.grade(bind=False)
                self.assertEqual(control, 0, name)
                self.assertIn("adversarial-record: 0", report)
                self.assertEqual(refused, 1, name)
                self.assertNotIn("adversarial-record: 0", failed_report)

    def test_latest_read_must_name_the_highest_pass_and_be_clean(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.write_deck((slide_xml("Plan", "Within limit"),))
            run.retain(1, 1)
            run.retain(2, 1)
            run.write_rendered(pass_number="2")
            run.write_adversarial(pass_number="2")
            clean, _, _ = run.grade(bind=False)
            current = (run.root / "adversarial.md").read_text(encoding="utf-8")
            run.write_adversarial(pass_number="1")
            old = (run.root / "adversarial.md").read_text(encoding="utf-8")
            (run.root / "adversarial.md").write_text(current + old, encoding="utf-8")
            refused, report, _ = run.grade(bind=False)

        self.assertEqual(clean, 0)
        self.assertEqual(refused, 1)
        self.assertNotIn("adversarial-record: 0", report)


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
