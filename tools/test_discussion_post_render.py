"""Public-CLI tests for retained discussion-post page pixels.

Every document and page is synthetic. No classmate or patient is represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import base64
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import discussion_post_render as render
import docx_write


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class FakePage:
    def __init__(self, number: int):
        self.number = number

    def get_pixmap(self, *, dpi: int):
        if dpi != render.RASTER_DPI:
            raise AssertionError(dpi)

        number = self.number

        class Pixmap:
            def save(self, path):
                Path(path).write_bytes(f"page {number}".encode("ascii"))

        return Pixmap()


class FakeDocument:
    def __init__(
        self,
        pages: int = 2,
        failing_pages: tuple[int, ...] = (),
        partial_write_pages: tuple[int, ...] = (),
    ):
        self.pages = pages
        self.failing_pages = failing_pages
        self.partial_write_pages = partial_write_pages

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def __len__(self):
        return self.pages

    def __iter__(self):
        pages = [FakePage(number) for number in range(1, self.pages + 1)]
        for page in pages:
            if page.number in self.failing_pages:
                page.get_pixmap = mock.Mock(side_effect=RuntimeError("unreachable page"))
            elif page.number in self.partial_write_pages:
                number = page.number

                class PartialPixmap:
                    def save(self, path):
                        Path(path).write_bytes(f"partial page {number}".encode("ascii"))
                        raise RuntimeError("partial raster write")

                page.get_pixmap = mock.Mock(return_value=PartialPixmap())
        return iter(pages)


class FakePyMuPDF:
    @staticmethod
    def open(path):
        artifact = Path(path)
        if not artifact.is_file():
            raise AssertionError(path)
        if artifact.suffix.lower() == ".png":
            if not artifact.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("not PNG data")
            return FakeDocument(pages=1)
        return FakeDocument()


class TheRenderCommand(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docx = self.root / "post.docx"
        docx_write.write_docx("# Synthetic\n\nBody.", self.docx)

    @staticmethod
    def word_export(command, **_kwargs):
        mode = command[command.index("-Mode") + 1]
        output_directory = Path(command[command.index("-OutputDirectory") + 1])
        output = output_directory / f"post.{mode}"
        output.write_bytes(f"synthetic {mode}".encode("ascii"))
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"source": f"word-{mode}", "path": str(output)}),
            stderr="",
        )

    def run_command(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=self.word_export),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])
        return status, stdout.getvalue(), stderr.getvalue()

    def test_each_render_keeps_a_new_complete_pass(self):
        first, first_out, first_err = self.run_command()
        second, second_out, second_err = self.run_command()

        self.assertEqual((0, 0), (first, second))
        self.assertEqual(("", ""), (first_err, second_err))
        self.assertIn("SOURCE: word-pdf", first_out)
        self.assertIn("PAGES: 2 of 2 imaged", first_out)
        self.assertIn("render/pass-1", first_out.replace("\\", "/"))
        self.assertIn("render/pass-2", second_out.replace("\\", "/"))
        self.assertEqual(
            ["page-1.png", "page-2.png", "post.pdf"],
            sorted(path.name for path in (self.root / "render" / "pass-1").iterdir()),
        )
        self.assertEqual(
            ["page-1.png", "page-2.png", "post.pdf"],
            sorted(path.name for path in (self.root / "render" / "pass-2").iterdir()),
        )

    def test_a_gap_and_non_pass_names_allocate_above_the_highest_pass(self):
        render_root = self.root / "render"
        for name in ("pass-1", "pass-3", "pass-01", "pass-0", "pass-²"):
            (render_root / name).mkdir(parents=True)

        status, stdout, stderr = self.run_command()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("render/pass-4", stdout.replace("\\", "/"))
        self.assertTrue((render_root / "pass-4" / "post.pdf").is_file())

    def test_a_failed_word_export_retains_no_partial_pass(self):
        failed = SimpleNamespace(returncode=1, stdout="", stderr="Word refused export")
        stderr = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", return_value=failed),
            contextlib.redirect_stderr(stderr),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        self.assertEqual(2, status)
        self.assertIn("Word refused export", stderr.getvalue())
        self.assertEqual([], list((self.root / "render").iterdir()))

    def test_xps_replaces_every_pdf_pixel_when_the_pdf_route_is_incomplete(self):
        stdout = io.StringIO()

        class PdfPage(FakePage):
            def get_pixmap(self, *, dpi: int):
                if self.number == 2:
                    raise RuntimeError("unreachable page")

                class Pixmap:
                    @staticmethod
                    def save(path):
                        Path(path).write_bytes(b"pdf page 1")

                return Pixmap()

        class PdfDocument(FakeDocument):
            def __iter__(self):
                return iter((PdfPage(1), PdfPage(2)))

        class PartialPyMuPDF(FakePyMuPDF):
            @staticmethod
            def open(path):
                artifact = Path(path)
                if artifact.suffix.lower() == ".png":
                    return FakePyMuPDF.open(path)
                if artifact.suffix.lower() == ".pdf":
                    return PdfDocument()
                return FakeDocument()

        with (
            mock.patch.dict(sys.modules, {"pymupdf": PartialPyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=self.word_export),
            contextlib.redirect_stdout(stdout),
        ):
            status = render.main(
                [
                    str(self.root),
                    "--docx",
                    str(self.docx),
                ]
            )

        self.assertEqual(0, status)
        self.assertIn("SOURCE: word-xps", stdout.getvalue())
        retained = self.root / "render" / "pass-1"
        self.assertEqual(b"page 1", (retained / "page-1.png").read_bytes())
        self.assertEqual(b"page 2", (retained / "page-2.png").read_bytes())
        self.assertTrue((retained / "post.xps").is_file())

    def test_a_clinician_export_can_supply_the_whole_pass_after_both_exports_fail(self):
        clinician_export = self.root / "clinician.pdf"
        clinician_export.write_bytes(b"synthetic clinician PDF")
        failed = SimpleNamespace(returncode=1, stdout="", stderr="Word refused export")
        stdout = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", return_value=failed),
            contextlib.redirect_stdout(stdout),
        ):
            status = render.main(
                [
                    str(self.root),
                    "--docx",
                    str(self.docx),
                    "--clinician-export",
                    str(clinician_export),
                ]
            )

        self.assertEqual(0, status)
        self.assertIn("SOURCE: clinician", stdout.getvalue())
        retained = self.root / "render" / "pass-1"
        self.assertEqual(
            ["page-1.png", "page-2.png", "post.pdf"],
            sorted(path.name for path in retained.iterdir()),
        )
        self.assertEqual(clinician_export.read_bytes(), (retained / "post.pdf").read_bytes())

    def test_expected_count_cannot_override_words_larger_denominator(self):
        class ThreePagePyMuPDF(FakePyMuPDF):
            @staticmethod
            def open(path):
                artifact = Path(path)
                if artifact.suffix.lower() == ".png":
                    return FakePyMuPDF.open(path)
                return FakeDocument(pages=3)

        stderr = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": ThreePagePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=self.word_export),
            contextlib.redirect_stderr(stderr),
        ):
            status = render.main(
                [
                    str(self.root),
                    "--docx",
                    str(self.docx),
                    "--expected-pages",
                    "2",
                ]
            )

        self.assertEqual(2, status)
        self.assertIn("reports 3 pages", stderr.getvalue())
        self.assertEqual([], list((self.root / "render").iterdir()))

    def test_a_non_pdf_or_xps_is_refused_as_a_clinician_export(self):
        export = self.root / "not-an-export.png"
        export.write_bytes(PNG)
        stderr = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            contextlib.redirect_stderr(stderr),
        ):
            status = render.main(
                [
                    str(self.root),
                    "--docx",
                    str(self.docx),
                    "--clinician-export",
                    str(export),
                ]
            )

        self.assertEqual(2, status)
        self.assertIn("existing PDF or XPS", stderr.getvalue())
        self.assertFalse((self.root / "render").exists())

    def test_xps_covers_a_page_the_pdf_cannot_rasterize_before_clinician_escalation(self):
        commands = []

        class RoutePyMuPDF(FakePyMuPDF):
            @staticmethod
            def open(path):
                artifact = Path(path)
                if artifact.suffix.lower() == ".pdf":
                    return FakeDocument(failing_pages=(2,))
                return FakeDocument()

        def export(command, **kwargs):
            commands.append(command)
            return self.word_export(command, **kwargs)

        stdout = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": RoutePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=export),
            contextlib.redirect_stdout(stdout),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        self.assertEqual(0, status)
        self.assertIn("SOURCE: word-xps", stdout.getvalue())
        self.assertEqual(
            ["pdf", "xps"],
            [command[command.index("-Mode") + 1] for command in commands],
        )

    def test_xps_replaces_a_failed_pdf_partial_write(self):
        class RoutePyMuPDF(FakePyMuPDF):
            @staticmethod
            def open(path):
                artifact = Path(path)
                if artifact.suffix.lower() == ".pdf":
                    return FakeDocument(partial_write_pages=(2,))
                return FakeDocument()

        with (
            mock.patch.dict(sys.modules, {"pymupdf": RoutePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=self.word_export),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        self.assertEqual(0, status)
        retained = self.root / "render" / "pass-1"
        self.assertEqual(b"page 2", (retained / "page-2.png").read_bytes())
        self.assertEqual([], list(retained.glob("*.building.png")))

    def test_the_word_script_quits_only_after_process_ownership_is_established(self):
        script = Path(render.__file__).with_suffix(".ps1").read_text(encoding="utf-8")
        helper = Path(render.__file__).with_name("office_process.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("office_process.ps1", script)
        self.assertIn("$created.Count -ne 1", helper)
        self.assertIn("$ownershipEstablished = $false", script)
        self.assertIn("$ownershipEstablished = $true", script)
        self.assertIn("$null -ne $word -and $ownershipEstablished", script)
        self.assertIn("$cleanupFailure", script)

    def test_the_word_route_uses_the_shared_runner_with_its_own_bound(self):
        source = Path(render.__file__).read_text(encoding="utf-8")

        self.assertIn("office_process.run_owned_process", source)
        self.assertIn("timeout_seconds=EXPORT_TIMEOUT_SECONDS", source)

    def test_a_stalled_pdf_attempt_stops_only_its_owned_word_and_uses_xps(self):
        commands = []

        def stalled_pdf(command, **_kwargs):
            commands.append(command)
            if command[0] == "taskkill.exe":
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            mode = command[command.index("-Mode") + 1]
            output_directory = Path(command[command.index("-OutputDirectory") + 1])
            ownership = Path(command[command.index("-OwnershipFile") + 1])
            if mode == "pdf":
                ownership.write_text("4242|opened", encoding="ascii")
                raise render.subprocess.TimeoutExpired(command, 20)
            output = output_directory / "post.xps"
            output.write_bytes(b"synthetic XPS")
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps({"source": "word-xps", "path": str(output)}),
                stderr="",
            )

        stdout = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=stalled_pdf),
            contextlib.redirect_stdout(stdout),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        self.assertEqual(0, status)
        self.assertIn("SOURCE: word-xps", stdout.getvalue())
        self.assertIn(["taskkill.exe", "/PID", "4242", "/T", "/F"], commands)
        self.assertEqual(
            ["pdf", "xps"],
            [
                command[command.index("-Mode") + 1]
                for command in commands
                if command[0] == "powershell.exe"
            ],
        )

    def test_a_nonzero_word_attempt_stops_its_recorded_owned_process(self):
        commands = []

        def failed_attempt(command, **_kwargs):
            commands.append(command)
            if command[0] == "taskkill.exe":
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            ownership = Path(command[command.index("-OwnershipFile") + 1])
            ownership.write_text("5150|opened", encoding="ascii")
            return SimpleNamespace(returncode=1, stdout="", stderr="export failed")

        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=failed_attempt),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        self.assertEqual(2, status)
        self.assertGreaterEqual(
            commands.count(["taskkill.exe", "/PID", "5150", "/T", "/F"]),
            1,
        )


if __name__ == "__main__":
    unittest.main()
