"""Public-CLI tests for retained case-study page pixels.

Every document and page is synthetic. No patient is represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import case_study_render as render
import docx_write
import file_digest


REPO_ROOT = Path(__file__).resolve().parent.parent
ROUTE_RECORD = REPO_ROOT / "docs" / "adr" / (
    "0142-the-word-export-route-is-shared-by-stem-and-a-reached-bound-ends-it.md"
)
CASE_STUDY_SKILL = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"


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
                Path(path).write_bytes(f"page {number}".encode("ascii"))

        return Pixmap()


class FakeDocument:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def __len__(self):
        return 2

    def __iter__(self):
        return iter((FakePage(1), FakePage(2)))


class FakePyMuPDF:
    @staticmethod
    def open(path):
        if not Path(path).is_file():
            raise AssertionError(path)
        return FakeDocument()


class TheCaseStudyRenderCommand(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docx = self.root / "case.docx"
        self.markdown = self.docx.with_suffix(".md")
        self.markdown.write_text("# Synthetic case\n\nOriginal text.\n", encoding="utf-8")
        with zipfile.ZipFile(self.docx, "w") as archive:
            for name, payload in docx_write.parts(
                self.markdown.read_text(encoding="utf-8")
            ).items():
                archive.writestr(name, payload)

    def replace_part(self, changed_name: str, changed_payload: bytes) -> None:
        with zipfile.ZipFile(self.docx) as source:
            parts = {name: source.read(name) for name in source.namelist()}
        parts[changed_name] = changed_payload
        with zipfile.ZipFile(self.docx, "w") as archive:
            for name, payload in parts.items():
                archive.writestr(name, payload)

    @staticmethod
    def successful_export(command, **_kwargs):
        mode = command[command.index("-Mode") + 1]
        if command[command.index("-Stem") + 1] != "case-study":
            raise AssertionError(command)
        output_directory = Path(command[command.index("-OutputDirectory") + 1])
        output = output_directory / f"case-study.{mode}"
        output.write_bytes(f"synthetic {mode}".encode("ascii"))
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"source": f"word-{mode}", "path": str(output)}),
            stderr="",
        )

    def test_a_returned_pdf_failure_advances_to_xps(self):
        modes = []

        def export(command, **kwargs):
            if command[0] == "taskkill.exe":
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            mode = command[command.index("-Mode") + 1]
            modes.append(mode)
            if mode == "pdf":
                return SimpleNamespace(returncode=1, stdout="", stderr="PDF refused")
            return self.successful_export(command, **kwargs)

        stdout = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=export),
            contextlib.redirect_stdout(stdout),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        self.assertEqual(0, status)
        self.assertEqual(["pdf", "xps"], modes)
        self.assertIn("SOURCE: word-xps", stdout.getvalue())
        retained = self.root / "render" / "pass-1"
        self.assertEqual(
            ["case-study-draft.sha256", "case-study.xps", "page-1.png", "page-2.png"],
            sorted(path.name for path in retained.iterdir()),
        )

    def test_a_hand_edited_docx_is_refused_before_automated_export(self):
        self.replace_part("word/document.xml", b"hand edited")
        stderr = io.StringIO()
        with (
            mock.patch.object(render.subprocess, "run") as runner,
            contextlib.redirect_stderr(stderr),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        self.assertEqual(2, status)
        runner.assert_not_called()
        self.assertIn("word/document.xml", stderr.getvalue())
        self.assertIn("recover the edit into the Markdown", stderr.getvalue())

    def test_the_clinician_route_also_refuses_a_hand_edited_docx(self):
        clinician = self.root / "clinician.pdf"
        clinician.write_bytes(b"synthetic clinician PDF")
        self.replace_part("word/styles.xml", b"hand edited")
        status = render.main(
            [
                str(self.root),
                "--docx",
                str(self.docx),
                "--clinician-export",
                str(clinician),
            ]
        )

        self.assertEqual(2, status)

    def test_a_docx_without_same_stem_markdown_is_refused(self):
        self.markdown.unlink()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        self.assertEqual(2, status)
        self.assertIn("no Markdown source", stderr.getvalue())

    def test_a_matching_render_retains_the_markdown_fingerprint(self):
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=self.successful_export),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        fingerprint = self.root / "render" / "pass-1" / "case-study-draft.sha256"
        self.assertEqual(0, status)
        self.assertRegex(fingerprint.read_text(encoding="ascii"), r"^[0-9a-f]{64}\n$")

    def test_a_markdown_change_during_export_does_not_relabel_the_old_render(self):
        original_digest = file_digest.sha256(self.markdown)

        def export_then_change(command, **kwargs):
            result = self.successful_export(command, **kwargs)
            self.markdown.write_text("# Changed during export\n", encoding="utf-8")
            return result

        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=export_then_change),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        recorded = self.root / "render" / "pass-1" / "case-study-draft.sha256"
        self.assertEqual(0, status)
        self.assertEqual(original_digest, recorded.read_text(encoding="ascii").strip())

    def test_a_reached_pdf_bound_does_not_attempt_xps(self):
        commands = []

        def stalled(command, **_kwargs):
            commands.append(command)
            if command[0] == "taskkill.exe":
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            ownership = Path(command[command.index("-OwnershipFile") + 1])
            ownership.write_text("4242|opened", encoding="ascii")
            raise subprocess.TimeoutExpired(command, render.EXPORT_TIMEOUT_SECONDS)

        stderr = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run", side_effect=stalled),
            contextlib.redirect_stderr(stderr),
        ):
            status = render.main([str(self.root), "--docx", str(self.docx)])

        self.assertEqual(2, status)
        self.assertIn("timed out", stderr.getvalue())
        self.assertEqual(
            ["pdf"],
            [
                command[command.index("-Mode") + 1]
                for command in commands
                if command[0] == "powershell.exe"
            ],
        )
        self.assertIn(["taskkill.exe", "/PID", "4242", "/T", "/F"], commands)
        self.assertEqual([], list((self.root / "render").iterdir()))

    def test_a_clinician_export_is_the_whole_route_on_a_rerun(self):
        clinician = self.root / "clinician.pdf"
        clinician.write_bytes(b"synthetic clinician PDF")
        stdout = io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            mock.patch.object(render.subprocess, "run") as runner,
            contextlib.redirect_stdout(stdout),
        ):
            status = render.main(
                [
                    str(self.root),
                    "--docx",
                    str(self.docx),
                    "--clinician-export",
                    str(clinician),
                ]
            )

        self.assertEqual(0, status)
        runner.assert_not_called()
        self.assertIn("SOURCE: clinician", stdout.getvalue())
        retained = self.root / "render" / "pass-1"
        self.assertEqual(clinician.read_bytes(), (retained / "case-study.pdf").read_bytes())

    def test_the_word_route_uses_the_shared_script_and_declared_bound(self):
        source = Path(render.__file__).read_text(encoding="utf-8")

        self.assertIn("office_process.run_owned_process", source)
        self.assertIn("timeout_seconds=EXPORT_TIMEOUT_SECONDS", source)
        self.assertIn('with_name("word_export.ps1")', source)
        self.assertIn('"-Stem",\n        "case-study"', source)
        self.assertIn("uncalibrated", source)
        self.assertIn("safety stop", source)
        self.assertIn("terminal for automation at this site", source)

    def test_decision_figures_equal_their_tracked_sources(self):
        record = ROUTE_RECORD.read_text(encoding="utf-8")
        bound = re.search(
            r"`case_study_render\.EXPORT_TIMEOUT_SECONDS = ([1-9][0-9]*)`",
            record,
        )
        self.assertIsNotNone(bound)
        self.assertEqual(int(bound.group(1)), render.EXPORT_TIMEOUT_SECONDS)

        skill = CASE_STUDY_SKILL.read_text(encoding="utf-8")
        raster = re.search(r"one ([1-9][0-9]*)-dpi PNG per page", skill)
        self.assertIsNotNone(raster)
        self.assertEqual(int(raster.group(1)), render.RASTER_DPI)

    def test_the_cli_has_no_expected_pages_override(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            render.main(
                [
                    str(self.root),
                    "--docx",
                    str(self.docx),
                    "--expected-pages",
                    "2",
                ]
            )

        self.assertEqual(2, raised.exception.code)
        self.assertIn("unrecognized arguments: --expected-pages 2", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
