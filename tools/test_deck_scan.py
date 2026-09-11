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
from unittest import mock

import deck_scan as scan
from grader_conformance import EmptyPopulationInput, for_module


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

    def retain(self, number: int, images: int) -> None:
        retained = self.root / "render" / f"pass-{number}"
        retained.mkdir(parents=True)
        for index in range(1, images + 1):
            (retained / f"slide-{index}.png").write_bytes(b"synthetic")

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

    def terminal(self) -> tuple[int, str, str]:
        with mock.patch.object(
            scan.aar_scan,
            "completion_gate",
            return_value=(False, "the after-action review: clean"),
        ):
            return self.grade("--submission", self.deck.stem)


def empty_population_input(root: Path) -> EmptyPopulationInput:
    empty_root, twin_root = root / "empty", root / "twin"
    empty_root.mkdir()
    twin_root.mkdir()
    empty, twin = Run(empty_root), Run(twin_root)
    empty.write_deck(
        ("<p:sld xmlns:p='http://schemas.openxmlformats.org/presentationml/2006/main'/>",)
    )
    twin.write_deck((slide_xml("Synthetic title"),))
    return EmptyPopulationInput(
        (str(empty.root), "--pptx", str(empty.deck)),
        population_size=lambda result: result.font_runs_read,
        twin_argv=(str(twin.root), "--pptx", str(twin.deck)),
    )


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
                self.assertIn(f"{scan.UNTRACED_COST}: 1", stdout)

    def test_a_sourced_standing_record_still_traces_its_cost(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000.\n"
                "STATUS: sourced\nREFUTATION: stands - the source states this cost.\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            status, _, _ = run.grade()

        self.assertEqual(0, status)

    def test_a_sourced_record_missing_ledger_fields_is_still_believed(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: Build-out costs $47,000.\nSTATUS: sourced\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
            status, _, _ = run.grade()

        self.assertEqual(0, status)

    def test_token_identity_does_not_establish_claim_support(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                "DATE: 2026-09-02\n\n## CLAIM: An unrelated item costs $47,000.\n"
                "STATUS: sourced\nREFUTATION: stands - the source states the unrelated cost.\n",
                encoding="utf-8",
            )
            run.write_deck((slide_xml("Plan", "Build-out $47,000"),))
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


class TheRenderedDeckRecordNamesTheTerminalPass(unittest.TestCase):
    def a_run(self, root: Path, *, slides: int = 1) -> Run:
        run = Run(root)
        run.write_deck(tuple(slide_xml(f"Slide {index}", "Within limit") for index in range(1, slides + 1)))
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

    def test_preflight_grades_format_but_not_the_terminal_join(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.a_run(Path(temp))
            run.write_rendered(source="browser")
            bad_status, _, _ = run.grade()
            run.write_rendered()
            clean_status, stdout, _ = run.grade()

        self.assertEqual(bad_status, 1)
        self.assertEqual(clean_status, 0)
        self.assertIn("rendered record: not graded - --submission was not supplied", stdout)

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
            no_pass, _, _ = run.terminal()
            run.retain(1, 1)
            (run.root / "rendered.md").unlink()
            no_record, _, _ = run.terminal()

        self.assertEqual(no_pass, 1)
        self.assertEqual(no_record, 1)

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
