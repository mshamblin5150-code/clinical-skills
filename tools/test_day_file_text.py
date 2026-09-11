"""Command-level contract for assembling one day file into the PHI corpus."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import day_file_text
import pdf_engine
from prose_bind import NAMING, bind


ROOT = Path(__file__).resolve().parent.parent
BATCH_SHIFT = ROOT / "skills" / "batch-shift" / "SKILL.md"


class FakePage:
    def __init__(self, number: int, text: str) -> None:
        self.number = number
        self._text = text

    def plain_text(self) -> str:
        return self._text


class FakeDocument:
    def __init__(self, texts: list[str]) -> None:
        self._pages = tuple(
            FakePage(number, text) for number, text in enumerate(texts, start=1)
        )

    @property
    def page_count(self) -> int:
        return len(self._pages)

    def pages(self):
        return iter(self._pages)


class DayFileTextCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.scratch = self.root / "scratch"
        self.source = self.root / "September 11.pdf"
        self.source.write_bytes(b"first source")
        self.texts = ["Note 1\ntext page\n"]

    @contextmanager
    def opened(self, _path: Path):
        yield FakeDocument(self.texts)

    def rasterize(self, _source, destination, *, name, dpi, page_numbers):
        self.assertEqual(dpi, 140)
        for number in page_numbers:
            destination.mkdir(parents=True, exist_ok=True)
            (destination / f"{name}-{number}.png").write_bytes(b"png")
        return len(tuple(page_numbers))

    def run_main(self, *extra: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(day_file_text.repo_root, "scratch_root", return_value=self.scratch),
            mock.patch.object(day_file_text.page_text, "open_document", side_effect=self.opened),
            mock.patch.object(day_file_text.page_image, "rasterize", side_effect=self.rasterize),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = day_file_text.main(
                [str(self.source), "--date", "2026-09-11", *extra]
            )
        return status, stdout.getvalue(), stderr.getvalue()

    def corpus_file(self) -> Path:
        return self.scratch / "day-file-text" / "September 11.txt"

    def day_directory(self) -> Path:
        return self.scratch / "runs" / "shift-2026-09-11" / "day-file"

    def test_text_pages_write_the_corpus_file_and_report_counts_and_paths_only(self):
        status, output, errors = self.run_main()

        self.assertEqual(status, 0)
        self.assertEqual(errors, "")
        self.assertEqual(self.corpus_file().read_text(encoding="utf-8"), self.texts[0])
        self.assertIn("Pages read as text: 1", output)
        self.assertIn("Pages rendered: 0", output)
        self.assertIn(str(self.corpus_file()), output)
        self.assertNotIn("Note 1", output)

    def test_a_textless_page_is_rendered_at_140_dpi_and_returns_pending(self):
        self.texts = ["typed\n", " \t\n"]

        status, output, errors = self.run_main()

        self.assertEqual(status, 1)
        self.assertEqual(errors, "")
        self.assertFalse(self.corpus_file().exists())
        self.assertTrue((self.day_directory() / "page-2.png").is_file())
        self.assertTrue((self.day_directory() / "source.sha256").is_file())
        self.assertIn("Pages read as text: 1", output)
        self.assertIn("Pages rendered: 1", output)
        self.assertIn("Pages awaiting reading: 1", output)
        self.assertIn(str(self.day_directory() / "page-2.png"), output)

    def test_partial_transcriptions_wait_and_complete_transcriptions_assemble_in_order(self):
        self.texts = ["typed page\n", "", "\n"]
        self.day_directory().mkdir(parents=True)
        (self.day_directory() / "page-2.txt").write_text(
            "transcribed two\n", encoding="utf-8"
        )

        pending, output, _errors = self.run_main()
        self.assertEqual(pending, 1)
        self.assertFalse(self.corpus_file().exists())
        self.assertIn(str(self.day_directory() / "page-3.png"), output)
        self.assertNotIn(str(self.day_directory() / "page-2.png"), output)

        (self.day_directory() / "page-3.txt").write_text(
            "transcribed three\n", encoding="utf-8"
        )
        complete, _output, _errors = self.run_main()
        self.assertEqual(complete, 0)
        self.assertEqual(
            self.corpus_file().read_text(encoding="utf-8"),
            "typed page\ntranscribed two\ntranscribed three\n",
        )

    def test_identical_is_a_no_op_different_is_refused_and_force_replaces(self):
        self.assertEqual(self.run_main()[0], 0)
        original_stat = self.corpus_file().stat()

        self.assertEqual(self.run_main()[0], 0)
        self.assertEqual(self.corpus_file().stat().st_mtime_ns, original_stat.st_mtime_ns)

        self.texts = ["changed\n"]
        refused, _output, errors = self.run_main()
        self.assertEqual(refused, 2)
        self.assertIn(str(self.corpus_file()), errors)
        self.assertEqual(self.corpus_file().read_text(encoding="utf-8"), "Note 1\ntext page\n")

        replaced, _output, errors = self.run_main("--force")
        self.assertEqual(replaced, 0)
        self.assertEqual(errors, "")
        self.assertEqual(self.corpus_file().read_text(encoding="utf-8"), "changed\n")

    def test_a_different_existing_corpus_file_creates_no_run_artifact(self):
        self.corpus_file().parent.mkdir(parents=True)
        self.corpus_file().write_text("hand corrected\n", encoding="utf-8")

        status, _output, errors = self.run_main()

        self.assertEqual(status, 2)
        self.assertIn(str(self.corpus_file()), errors)
        self.assertFalse(self.day_directory().exists())

    def test_a_different_source_for_the_same_date_is_refused_before_opening(self):
        self.texts = [""]
        self.assertEqual(self.run_main()[0], 1)
        self.source.write_bytes(b"different source")

        stderr = io.StringIO()
        with (
            mock.patch.object(day_file_text.repo_root, "scratch_root", return_value=self.scratch),
            mock.patch.object(day_file_text.page_text, "open_document") as open_document,
            redirect_stderr(stderr),
        ):
            status = day_file_text.main(
                [str(self.source), "--date", "2026-09-11"]
            )

        self.assertEqual(status, 2)
        open_document.assert_not_called()
        self.assertIn(str(self.day_directory() / "source.sha256"), stderr.getvalue())

    def test_engine_absence_and_an_unreadable_document_are_status_two(self):
        for failure in (
            pdf_engine.EngineUnavailable(),
            pdf_engine.SourceUnreadable("secret engine detail"),
        ):
            with self.subTest(failure=type(failure).__name__):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with (
                    mock.patch.object(day_file_text.repo_root, "scratch_root", return_value=self.scratch),
                    mock.patch.object(day_file_text.page_text, "open_document", side_effect=failure),
                    redirect_stdout(stdout),
                    redirect_stderr(stderr),
                ):
                    status = day_file_text.main(
                        [str(self.source), "--date", "2026-09-12"]
                    )
                self.assertEqual(status, 2)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn(str(self.source), stderr.getvalue())
                self.assertNotIn("secret engine detail", stderr.getvalue())
                self.assertFalse((self.scratch / "runs" / "shift-2026-09-12").exists())

    def test_a_document_with_no_pages_produces_nothing(self):
        self.texts = []

        status, output, errors = self.run_main()

        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn(str(self.source), errors)
        self.assertFalse(self.corpus_file().exists())
        self.assertFalse(self.day_directory().exists())

    def test_the_command_declares_what_its_statuses_do_not_establish(self):
        self.assertTrue(day_file_text.DECLARED_LIMITS)
        self.assertEqual(
            (), bind(day_file_text.DECLARED_LIMITS, day_file_text.__doc__, mode=NAMING)
        )

    def test_the_command_imports_both_adapters_and_never_the_engine(self):
        source = (ROOT / "tools" / "day_file_text.py").read_text(encoding="utf-8")
        self.assertIn("import page_text", source)
        self.assertIn("import page_image", source)
        self.assertNotIn("import pdf_engine", source)

    def test_batch_shift_writes_note_markdown_where_its_terminal_grader_reads(self):
        skill = BATCH_SHIFT.read_text(encoding="utf-8")
        step_five = skill.split("### 5. Process each encounter", 1)[1].split(
            "### 6. Roll up the shift", 1
        )[0]
        self.assertIn("scratch/runs/shift-<date>/", step_five)
        self.assertIn("note-N.md", step_five)


if __name__ == "__main__":
    unittest.main()
