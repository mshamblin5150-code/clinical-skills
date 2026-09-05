"""Public-seam tests for the case-study retained-render grader."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import discussion_post_scan
import render_scan
from grader_conformance import for_module


GraderConformance = for_module(render_scan)


class TheRenderWiringDecisionIsPublished(unittest.TestCase):
    def test_both_graders_point_to_adr_0125(self):
        post_limits = " ".join(
            text
            for subject, reason, _disposition in discussion_post_scan.DECLARED_LIMITS
            for text in (subject, reason)
        )

        self.assertIn("ADR 0125", post_limits)
        self.assertIn("ADR 0125", render_scan.__doc__ or "")


class FakeDocument:
    def __init__(self, pages: int):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def __len__(self):
        return self.pages

    def __iter__(self):
        return iter(FakePage() for _ in range(self.pages))


class FakePage:
    def get_pixmap(self, *, dpi: int):
        if dpi != 120:
            raise ValueError("unexpected raster resolution")
        return object()


class FakePyMuPDF:
    @staticmethod
    def open(path):
        payload = Path(path).read_bytes()
        if payload == b"\x89PNG\r\n\x1a\nretained pixels":
            return FakeDocument(1)
        marker = payload.decode("ascii")
        if not marker.startswith("pages:"):
            raise ValueError("not synthetic export data")
        return FakeDocument(int(marker.removeprefix("pages:")))


class Run:
    def __init__(self, root: Path):
        self.root = root

    def add_pass(
        self,
        number: int,
        *,
        pages: int | None,
        pixels: int,
        suffix: str = ".pdf",
    ) -> Path:
        render_pass = self.root / "render" / f"pass-{number}"
        render_pass.mkdir(parents=True)
        if pages is not None:
            (render_pass / f"case-study{suffix}").write_text(
                f"pages:{pages}", encoding="ascii"
            )
        for page in range(1, pixels + 1):
            (render_pass / f"page-{page}.png").write_bytes(
                b"\x89PNG\r\n\x1a\nretained pixels"
            )
        return render_pass

    def grade(self, *extra: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = render_scan.main([str(self.root), *extra])
        return status, stdout.getvalue(), stderr.getvalue()


class ACompleteFinalPassIsClean(unittest.TestCase):
    def test_pdf_pages_are_the_denominator_and_png_files_are_the_numerator(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=2, pixels=2)
            status, stdout, stderr = run.grade()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("passes read", stdout)
        self.assertIn("exported pages", stdout)
        self.assertIn("page images", stdout)
        self.assertIn("final-page-coverage: 0", stdout)
        self.assertIn("missing pass numbers         0", stdout)
        self.assertNotIn("page-1.png", stdout)
        self.assertNotIn(Path(temp).name, stdout)

    def test_xps_can_supply_the_same_page_count(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=1, pixels=1, suffix=".xps")
            status, _, _ = run.grade()

        self.assertEqual(0, status)

    def test_an_incomplete_earlier_pass_is_reported_but_does_not_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=3, pixels=1)
            run.add_pass(2, pages=2, pixels=2)
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("incomplete earlier passes", stdout)
        self.assertIn("1", stdout)
        self.assertIn("pass-1: 1 of 3 readable page images", stdout)
        self.assertIn("pass-2: 2 of 2 readable page images", stdout)


class AMeasuredShortFinalPassIsAFinding(unittest.TestCase):
    def test_fewer_pixels_than_exported_pages_exits_one(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=3, pixels=2)
            status, stdout, stderr = run.grade()

        self.assertEqual(1, status)
        self.assertIn("final-page-coverage: 1", stdout)
        self.assertIn("final render pass is short", stderr)

    def test_default_reports_pass_counts_and_show_adds_finding_detail(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=2, pixels=1)
            _, default, _ = run.grade()
            _, shown, _ = run.grade("--show")

        self.assertIn("pass-1: 1 of 2 readable page images", default)
        self.assertNotIn("keeps 1 page image", default)
        self.assertIn("pass-1", shown)
        self.assertIn("keeps 1 page image", shown)

    def test_a_nominal_png_that_cannot_be_decoded_is_not_counted(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            render_pass = run.add_pass(1, pages=2, pixels=2)
            (render_pass / "page-2.png").write_bytes(b"not a PNG")
            status, stdout, stderr = run.grade()

        self.assertEqual(1, status)
        self.assertIn("pass-1: 1 of 2 readable page images", stdout)
        self.assertIn("1 unreadable page image", stderr)
        self.assertNotIn("page-2.png", stderr)


class MissingEvidenceDidNotScan(unittest.TestCase):
    def test_a_gap_is_counted_without_changing_clean_status(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=1, pixels=1)
            run.add_pass(3, pages=1, pixels=1)
            status, stdout, stderr = run.grade()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("missing pass numbers         1", stdout)

    def test_non_pass_directory_names_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=1, pixels=1)
            for name in ("pass-01", "pass-0", "pass-²"):
                (Path(temp) / "render" / name).mkdir()
            status, stdout, stderr = run.grade()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("passes read                 1", stdout)
        self.assertIn("missing pass numbers         0", stdout)

    def test_a_gap_does_not_change_a_short_final_pass_status(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=1, pixels=1)
            run.add_pass(3, pages=2, pixels=1)
            status, stdout, stderr = run.grade()

        self.assertEqual(1, status)
        self.assertIn("final-page-coverage: 1", stdout)
        self.assertIn("missing pass numbers         1", stdout)
        self.assertNotIn("canonical uninterrupted", stderr)

    def test_no_render_directory_exits_two(self):
        with tempfile.TemporaryDirectory() as temp:
            status, _, stderr = Run(Path(temp)).grade()

        self.assertEqual(2, status)
        self.assertIn("no render directory", stderr)

    def test_pixels_without_an_export_exit_two(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=None, pixels=2)
            status, _, stderr = run.grade()

        self.assertEqual(2, status)
        self.assertIn("no retained PDF or XPS", stderr)

    def test_an_unreadable_export_exits_two(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            render_pass = run.add_pass(1, pages=2, pixels=2)
            (render_pass / "case-study.pdf").write_text("broken", encoding="ascii")
            status, _, stderr = run.grade()

        self.assertEqual(2, status)
        self.assertIn("could not read", stderr)
        self.assertNotIn("case-study.pdf", stderr)

    def test_a_finding_outranks_missing_evidence_across_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.add_pass(1, pages=None, pixels=1)
            run.add_pass(2, pages=2, pixels=1)
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("final-page-coverage: 1", stdout)


class TheSkillSaysWhatThisGrades(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (
            Path(__file__).resolve().parent.parent
            / "skills"
            / "practicum-case-study"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

    def test_the_command_is_part_of_step_nine(self):
        step = self.skill.split("### 9. Check", 1)[1]
        self.assertIn("python tools/render_scan.py <run-directory>", step)

    def test_the_export_and_pixels_are_both_kept_per_pass(self):
        normalized = " ".join(self.skill.split())
        self.assertIn("render/pass-N/", normalized)
        self.assertIn("one page-faithful PDF or XPS", normalized)
        self.assertIn("one 120-dpi PNG per page", normalized)

    def test_only_the_last_pass_must_be_complete(self):
        self.assertIn("Only the last pass must be complete", self.skill)
        self.assertIn("Earlier passes are counted and reported", self.skill)

    def test_pass_history_and_readable_pixel_contract_are_written_out(self):
        normalized = " ".join(self.skill.split())
        self.assertIn("gap count is reported and never graded", normalized)
        self.assertIn("count only PNGs that decode as one readable image", normalized)
        self.assertIn("report each pass's readable-image and exported-page counts", normalized)

    def test_exit_one_and_exit_two_are_distinguished_in_prose(self):
        self.assertIn("fewer PNGs than exported pages is exit 1", self.skill)
        self.assertIn("no measurable retained export is exit 2", self.skill)

    def test_the_automated_route_is_bounded_and_the_clinician_exports_on_fallback(self):
        self.assertIn("bounded automated route", self.skill)
        self.assertIn("File > Export > Create PDF/XPS", self.skill)
        self.assertIn("The agent still rasterizes and compares every page", self.skill)

    def test_the_bound_is_a_stop_and_not_a_measurement_or_second_attempt_trigger(self):
        normalized = " ".join(self.skill.split())
        self.assertIn("The bound is a safety stop, not a timing measurement", normalized)
        self.assertIn("does not establish that the automated route works", normalized)
        self.assertIn("goes directly to the clinician export", normalized)

    def test_the_substantiated_checks_ledger_verdict_is_not_replaced(self):
        self.assertIn(
            "Coverage does not replace the substantiated `the rendered document` verdict",
            self.skill,
        )


if __name__ == "__main__":
    unittest.main()
