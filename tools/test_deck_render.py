"""Public-CLI tests for retained PowerPoint render passes.

Every deck and rendered page is synthetic. No patient is represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import deck_render as render


class FakePage:
    def __init__(self, number: int):
        self.number = number

    def get_pixmap(self, *, dpi: int):
        if dpi != render.RASTER_DPI:
            raise AssertionError(dpi)
        number = self.number

        class Pixmap:
            @staticmethod
            def save(path):
                Path(path).write_bytes(f"slide {number}".encode("ascii"))

        return Pixmap()


class FakeDocument:
    def __init__(self, pages: int = 2, fail_page: int | None = None):
        self.pages = pages
        self.fail_page = fail_page

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def __len__(self):
        return self.pages

    def __iter__(self):
        pages = [FakePage(number) for number in range(1, self.pages + 1)]
        if self.fail_page is not None:
            pages[self.fail_page - 1].get_pixmap = mock.Mock(side_effect=RuntimeError("unreachable slide"))
        return iter(pages)


class FakePyMuPDF:
    @staticmethod
    def open(path):
        if not Path(path).is_file():
            raise AssertionError(path)
        return FakeDocument()


class TheDeckRenderCommand(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.deck = self.root / "deck.pptx"
        with zipfile.ZipFile(self.deck, "w") as archive:
            archive.writestr("ppt/slides/slide1.xml", "synthetic slide 1")
            archive.writestr("ppt/slides/slide2.xml", "synthetic slide 2")

    @staticmethod
    def powerpoint_export(command, **_kwargs):
        output = Path(command[command.index("-OutputPdf") + 1])
        output.write_bytes(b"synthetic PDF")
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"source": "powerpoint-pdf", "path": str(output)}),
            stderr="",
        )

    def run_command(self, *extra: str, pymupdf=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": pymupdf or FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=self.powerpoint_export),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            status = render.main([str(self.root), "--pptx", str(self.deck), *extra])
        return status, stdout.getvalue(), stderr.getvalue()

    def test_each_success_keeps_a_new_pdf_and_one_image_per_slide(self):
        first, first_out, first_err = self.run_command()
        second, second_out, second_err = self.run_command()

        self.assertEqual((0, 0), (first, second))
        self.assertEqual(("", ""), (first_err, second_err))
        self.assertIn("SOURCE: powerpoint-pdf", first_out)
        self.assertIn("SLIDES: 2 of 2 imaged", first_out)
        self.assertIn("render/pass-1", first_out.replace("\\", "/"))
        self.assertIn("render/pass-2", second_out.replace("\\", "/"))
        self.assertEqual(
            ["deck.pdf", "slide-1.png", "slide-2.png"],
            sorted(path.name for path in (self.root / "render" / "pass-1").iterdir()),
        )

    def test_a_gap_and_non_pass_names_allocate_above_the_highest_pass(self):
        render_root = self.root / "render"
        for name in ("pass-1", "pass-3", "pass-01", "pass-0", "pass-²"):
            (render_root / name).mkdir(parents=True)

        status, stdout, stderr = self.run_command()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("render/pass-4", stdout.replace("\\", "/"))
        self.assertTrue((render_root / "pass-4" / "deck.pdf").is_file())

    def test_a_failed_powerpoint_route_retains_no_pass(self):
        failed = SimpleNamespace(returncode=1, stdout="", stderr="PowerPoint refused export")
        stderr = io.StringIO()
        with (
            mock.patch.object(render.subprocess, "run", return_value=failed),
            contextlib.redirect_stderr(stderr),
        ):
            status = render.main([str(self.root), "--pptx", str(self.deck)])

        self.assertEqual(2, status)
        self.assertIn("PowerPoint refused export", stderr.getvalue())
        self.assertEqual([], list((self.root / "render").iterdir()))

    def test_a_failed_raster_retains_no_pass(self):
        class PartialPyMuPDF(FakePyMuPDF):
            @staticmethod
            def open(path):
                return FakeDocument(fail_page=2)

        status, _, stderr = self.run_command(pymupdf=PartialPyMuPDF())

        self.assertEqual(2, status)
        self.assertIn("unreachable slide", stderr)
        self.assertEqual([], list((self.root / "render").iterdir()))

    def test_a_clinician_pdf_is_the_escalation_when_powerpoint_is_unavailable(self):
        clinician = self.root / "clinician.pdf"
        clinician.write_bytes(b"clinician PDF")
        failed = SimpleNamespace(returncode=1, stdout="", stderr="PowerPoint unavailable")
        stdout = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", return_value=failed),
            contextlib.redirect_stdout(stdout),
        ):
            status = render.main(
                [str(self.root), "--pptx", str(self.deck), "--clinician-export", str(clinician)]
            )

        self.assertEqual(0, status)
        self.assertIn("SOURCE: clinician", stdout.getvalue())
        self.assertEqual(clinician.read_bytes(), (self.root / "render" / "pass-1" / "deck.pdf").read_bytes())

    def test_a_truncated_clinician_pdf_retains_no_pass(self):
        class OnePagePyMuPDF(FakePyMuPDF):
            @staticmethod
            def open(path):
                return FakeDocument(pages=1)

        clinician = self.root / "clinician.pdf"
        clinician.write_bytes(b"truncated clinician PDF")
        failed = SimpleNamespace(returncode=1, stdout="", stderr="PowerPoint unavailable")
        stderr = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": OnePagePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", return_value=failed),
            contextlib.redirect_stderr(stderr),
        ):
            status = render.main(
                [str(self.root), "--pptx", str(self.deck), "--clinician-export", str(clinician)]
            )

        self.assertEqual(2, status)
        self.assertIn("2 slides", stderr.getvalue())
        self.assertEqual([], list((self.root / "render").iterdir()))

    def test_the_script_quits_only_a_freshly_owned_powerpoint_process(self):
        script = Path(render.__file__).with_suffix(".ps1").read_text(encoding="utf-8")
        helper = Path(render.__file__).with_name("office_process.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("office_process.ps1", script)
        self.assertIn("$ownershipEstablished = $false", script)
        self.assertIn("$created.Count -ne 1", helper)
        self.assertIn("$ownershipEstablished = $true", script)
        self.assertIn("$null -ne $powerpoint -and $ownershipEstablished", script)

    def test_the_deck_route_uses_the_shared_runner_with_its_own_bound(self):
        source = Path(render.__file__).read_text(encoding="utf-8")

        self.assertIn("office_process.run_owned_process", source)
        self.assertIn("timeout_seconds=EXPORT_TIMEOUT_SECONDS", source)

    def test_the_script_uses_powerpoints_pdf_save_format(self):
        script = Path(render.__file__).with_suffix(".ps1").read_text(encoding="utf-8")
        self.assertIn("$presentation.SaveAs($OutputPdf, 32)", script)
        self.assertNotIn("ExportAsFixedFormat", script)

    def test_the_script_emits_utf8_json(self):
        script = Path(render.__file__).with_suffix(".ps1").read_text(encoding="utf-8")
        self.assertIn("[Console]::OutputEncoding", script)
        self.assertIn("UTF8Encoding", script)


if __name__ == "__main__":
    unittest.main()
