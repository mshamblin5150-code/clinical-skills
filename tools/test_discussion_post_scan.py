"""Behavior tests for ``discussion_post_scan`` at its public artifact seam.

Every board, bar, claim, and draft is synthetic. No classmate or patient is
represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import base64
import io
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import discussion_post_scan as scan
import discussion_post_render as render
import coursework_run
import discussion_reply_scan as reply_scan
import discussion_artifact as artifact
import docx_write
from grader_conformance import for_module, gate_conformance
from test_discussion_reply_scan import (
    BODY as REPLY_BODY,
    CLAIMS as REPLY_CLAIMS,
    Run as ReplyRun,
)


GraderConformance = for_module(scan)
GateConformance = gate_conformance(scan)
REPO_ROOT = Path(__file__).resolve().parents[1]
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class FakePage:
    @staticmethod
    def get_pixmap(*, dpi: int):
        if dpi != artifact.RENDERED_RASTER_DPI:
            raise AssertionError(dpi)
        return object()


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


class FakePyMuPDF:
    @staticmethod
    def open(path):
        source = Path(path)
        if source.suffix.lower() == ".png":
            if not source.read_bytes().startswith(artifact.PNG_SIGNATURE):
                raise ValueError("not PNG data")
            return FakeDocument(1)
        marker = source.read_text(encoding="ascii")
        if not marker.startswith("pages:"):
            raise ValueError("not synthetic export data")
        return FakeDocument(int(marker.removeprefix("pages:")))


BAR = """\
TOPIC: https://example.org/courses/1/discussion_topics/2
SYLLABUS: https://example.org/courses/1/assignments/syllabus
SIGNED: 2026-08-22
WORD-FLOOR: 100
WORD-CEILING: 180
REFERENCE-MINIMUM: 1

## Topic bar

> Explain how access differs from availability.

## Syllabus bar

> Initial posts must contain 100 to 180 words and at least one reference.
"""

CLAIMS = """\
DATE: 2026-08-22

## CLAIM: The combined program reported a 12% improvement.
STATUS: sourced
SOURCE: peer-reviewed
REFERENCE: Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.
RESTATEMENT: Completed visits improved by 12% when both supports were present.
RECENCY: current
RESOLVED: https://example.org/usable-access - read 2026-08-22
PAGE-YEAR: 2024 - stated on the article masthead.
REFUTATION: stands - the results table reports the same measure.

## CLAIM: The regulation supplies legal context.
STATUS: sourced
SOURCE: guideline in force
REFERENCE: Patient rights, 42 C.F.R. § 482.13 (2024).
RESTATEMENT: The cited regulation states the relevant legal context.
RECENCY: guideline in force
RESOLVED: https://example.org/regulation - read 2026-08-22
PAGE-YEAR: 2024 - stated on the regulation page.
REFUTATION: stands - the section number resolves to the cited regulation.
"""

BODY = """\
# Access Is More Than Availability

Access becomes meaningful when a patient can actually use the service. A clinic
may exist nearby while its schedule, transit options, or cost still make care
unreachable. That distinction changes what should be measured. The combined
program reported a 12% improvement when evening hours and transit support were
offered together (Quill, 2024, p. 6). The result does not prove that one design
fits every community, but it does show why a building count is an incomplete
measure. In policy terms, 42 C.F.R. § 482.13 provides a useful legal context
without settling whether a particular delivery model works. The practical test
is completed care, not nominal availability, because the outcome belongs at the
point where a patient can use what the system says it offers.

## References

Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.
"""


class Run:
    def __init__(self, root: Path):
        self.root = root
        self.draft = root / "nur0000-m2.md"
        (root / "bar.md").write_text(BAR, encoding="utf-8")
        (root / "claims.md").write_text(CLAIMS, encoding="utf-8")
        self.draft.write_text(BODY, encoding="utf-8")

    def grade(self, *extra: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            mock.patch.dict(sys.modules, {"pymupdf": FakePyMuPDF()}),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            status = scan.main([str(self.root), "--draft", str(self.draft), *extra])
        return status, stdout.getvalue(), stderr.getvalue()

    def record_render(
        self,
        *,
        seen: int = 2,
        expected: int = 2,
        source: str = "word-pdf",
        unseen: str = "none",
        verdict: str = "clean - both pages compared with the Markdown",
        render_pass: int = 1,
    ) -> None:
        post = self.root / "post.md"
        prior = post.read_text(encoding="utf-8") if post.is_file() else BODY
        post.write_text(
            prior
            + "\n\n## RENDERED: post.md\n"
            + f"PAGES: {seen} of {expected} imaged\n"
            + f"SOURCE: {source}\n"
            + f"UNSEEN: {unseen}\n"
            + "READ: 2026-09-01\n"
            + f"VERDICT: {verdict}\n",
            encoding="utf-8",
        )
        pass_directory = self.root / "render" / f"pass-{render_pass}"
        pass_directory.mkdir(parents=True)
        (pass_directory / "post.pdf").write_text(
            f"pages:{max(1, expected)}", encoding="ascii"
        )
        for page in range(1, seen + 1):
            (pass_directory / f"page-{page}.png").write_bytes(PNG)


class ACompletePostPasses(unittest.TestCase):
    def test_report_is_counts_only_and_excludes_citation_and_statute_numbers(self):
        with tempfile.TemporaryDirectory() as temp:
            status, stdout, stderr = Run(Path(temp)).grade()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("references: 1", stdout)
        self.assertIn("numeric claims: 1", stdout)
        self.assertIn("claim records: 2", stdout)
        self.assertIn("untraced-number: 0", stdout)
        self.assertNotIn("Quill", stdout)
        self.assertNotIn("482.13", stdout)

    def test_the_docx_row_is_not_graded_when_no_archive_is_supplied(self):
        with tempfile.TemporaryDirectory() as temp:
            status, stdout, _ = Run(Path(temp)).grade()

        self.assertEqual(0, status)
        self.assertIn("bold-headings: not graded", stdout)
        self.assertIn("rendered-comments: not graded", stdout)
        self.assertIn("rendered-text: not graded", stdout)
        self.assertIn("rendered-pages: not graded", stdout)


    def test_a_named_heading_style_fails_the_docx_row(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document)
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertIn("bold-headings: 1", stdout)

    def test_a_directly_formatted_heading_passes_the_docx_row(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render()
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(0, status)
        self.assertIn("bold-headings: 0", stdout)
        self.assertIn("rendered-text: 0", stdout)
        self.assertIn("rendered-pages: 0", stdout)
        self.assertIn("missing pass numbers: 0 (counted, not graded)", stdout)

    def test_a_gap_is_counted_without_changing_clean_status(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render(render_pass=1)
            run.record_render(render_pass=3)
            status, stdout, stderr = run.grade("--docx", str(document))

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("missing pass numbers: 1 (counted, not graded)", stdout)
        self.assertIn("rendered-pages: 0", stdout)

    def test_deleting_a_historical_pass_does_not_turn_the_gap_into_a_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render(render_pass=1)
            run.record_render(render_pass=2)
            run.record_render(render_pass=3)
            retained = run.root / "render" / "pass-2"
            for artifact in retained.iterdir():
                artifact.unlink()
            retained.rmdir()
            status, stdout, stderr = run.grade("--docx", str(document))

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("missing pass numbers: 1 (counted, not graded)", stdout)
        self.assertIn("rendered-pages: 0", stdout)

    def test_a_finding_uses_the_retained_pass_number_after_a_gap(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render(render_pass=1)
            run.record_render(
                seen=1,
                expected=2,
                unseen="2",
                render_pass=3,
            )
            status, stdout, _ = run.grade("--docx", str(document), "--show")

        self.assertEqual(1, status)
        self.assertIn("rendered-pages: pass-3:", stdout)
        self.assertNotIn("rendered-pages: pass-2:", stdout)

    def test_an_extra_render_record_keeps_the_empty_pass_evidence_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render(render_pass=1)
            post = run.root / "post.md"
            post.write_text(
                post.read_text(encoding="utf-8")
                + "\n## RENDERED: post.md\n"
                + "PAGES: 2 of 2 imaged\n"
                + "SOURCE: word-pdf\n"
                + "UNSEEN: none\n"
                + "READ: 2026-09-01\n"
                + "VERDICT: clean - both pages compared with the Markdown\n",
                encoding="utf-8",
            )
            status, stdout, _ = run.grade("--docx", str(document), "--show")

        self.assertEqual(1, status)
        self.assertIn("pass-2 keeps 0 page image(s), not 2", stdout)
        self.assertIn("pass-2 keeps 0 page-faithful export(s), not 1", stdout)

    def test_non_pass_directory_names_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render()
            for name in ("pass-01", "pass-0", "pass-²"):
                (run.root / "render" / name).mkdir()
            status, stdout, stderr = run.grade("--docx", str(document))

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("missing pass numbers: 0 (counted, not graded)", stdout)
        self.assertIn("rendered-pages: 0", stdout)

    def test_deck_shaped_pass_names_are_read_through_the_globbed_shape(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render()
            retained = run.root / "render" / "pass-1"
            (retained / "post.pdf").rename(retained / "deck.pdf")
            (retained / "page-1.png").rename(retained / "slide-1.png")
            (retained / "page-2.png").rename(retained / "slide-2.png")
            status, stdout, stderr = run.grade("--docx", str(document))

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("rendered-pages: 0", stdout)

    def test_a_docx_without_a_render_record_fails_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertRegex(stdout, r"rendered-pages: [1-9]\d*")

    def test_a_pass_without_its_page_faithful_export_fails_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render()
            (run.root / "render" / "pass-1" / "post.pdf").unlink()
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertRegex(stdout, r"rendered-pages: [1-9]\d*")

    def test_the_retained_export_supplies_the_page_count_denominator(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render()
            export_path = run.root / "render" / "pass-1" / "post.pdf"
            export_path.write_text("pages:3", encoding="ascii")
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertIn("rendered-pages: 1", stdout)

    def test_the_recorded_automated_source_must_match_the_retained_export(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render(source="word-xps")
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertIn("rendered-pages: 1", stdout)

    def test_an_unimaged_page_fails_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render(seen=1, expected=2, unseen="2")
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertIn("rendered-pages: 1", stdout)

    def test_zero_pages_cannot_be_a_complete_render(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render(seen=0, expected=0)
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertIn("rendered-pages: 1", stdout)

    def test_a_named_path_that_is_not_a_decodable_png_is_not_pixel_evidence(self):
        for replacement in ("directory", "text"):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as temp:
                run = Run(Path(temp))
                document = run.root / "post.docx"
                docx_write.write_docx(BODY, document, bold_headings=True)
                run.record_render(seen=1, expected=1)
                page = run.root / "render" / "pass-1" / "page-1.png"
                page.unlink()
                if replacement == "directory":
                    page.mkdir()
                else:
                    page.write_bytes(b"plain text")
                status, stdout, _ = run.grade("--docx", str(document))

            self.assertEqual(1, status)
            self.assertIn("rendered-pages: 1", stdout)

    def test_an_incomplete_historical_pass_does_not_fail_a_complete_final_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render(
                verdict="defect - the reference heading is clipped",
                seen=1,
                expected=2,
                unseen="2",
                render_pass=1,
            )
            run.record_render(
                render_pass=2,
            )
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(0, status)
        self.assertIn("rendered-pages: 0", stdout)

    def test_the_last_render_pass_must_be_complete_and_clean(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document, bold_headings=True)
            run.record_render(render_pass=1)
            run.record_render(
                verdict="defect - the reference heading is clipped",
                seen=1,
                expected=2,
                unseen="2",
                render_pass=2,
            )
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertRegex(stdout, r"rendered-pages: [1-9]\d*")

    def test_each_malformed_render_record_is_a_finding(self):
        replacements = (
            ("PAGES: 2 of 2 imaged", "PAGES: two pages"),
            ("SOURCE: word-pdf", "SOURCE: pymupdf-docx"),
            ("READ: 2026-09-01", "READ: yesterday"),
            (
                "VERDICT: clean - both pages compared with the Markdown",
                "VERDICT: clean",
            ),
        )
        for old, new in replacements:
            with self.subTest(field=old.split(":", 1)[0]), tempfile.TemporaryDirectory() as temp:
                run = Run(Path(temp))
                document = run.root / "post.docx"
                docx_write.write_docx(BODY, document, bold_headings=True)
                run.record_render()
                post = run.root / "post.md"
                post.write_text(
                    post.read_text(encoding="utf-8").replace(old, new),
                    encoding="utf-8",
                )
                status, stdout, _ = run.grade("--docx", str(document))

            self.assertEqual(1, status)
            self.assertGreaterEqual(
                int(re.search(r"rendered-pages: (\d+)", stdout).group(1)), 1
            )

    def test_unknown_fields_and_free_prose_make_the_render_record_malformed(self):
        for residue in ("EXTRA: silently accepted", "arbitrary free prose"):
            with self.subTest(residue=residue), tempfile.TemporaryDirectory() as temp:
                run = Run(Path(temp))
                document = run.root / "post.docx"
                docx_write.write_docx(BODY, document, bold_headings=True)
                run.record_render()
                post = run.root / "post.md"
                post.write_text(
                    post.read_text(encoding="utf-8") + residue + "\n",
                    encoding="utf-8",
                )
                status, stdout, _ = run.grade("--docx", str(document))

            self.assertEqual(1, status)
            self.assertIn("rendered-pages: 1", stdout)

    def test_a_document_whose_paragraph_text_differs_from_the_draft_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(
                BODY.replace("Access becomes meaningful", "Availability becomes meaningful"),
                document,
                bold_headings=True,
            )
            run.record_render()
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(0, status)
        self.assertIn("rendered-text: 1 (reported, not graded)", stdout)

    def test_a_rendered_mid_line_comment_fails_the_docx_row(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(
                BODY.replace(
                    "The practical test",
                    "<!-- INVOKED: gravity | attracts mass --> The practical test",
                ),
                document,
                bold_headings=True,
            )
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertIn("rendered-comments: 1", stdout)

    def test_both_lines_of_a_rendered_multi_line_comment_are_counted(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            document = run.root / "post.docx"
            docx_write.write_docx(
                BODY.replace(
                    "The practical test",
                    "<!-- INVOKED: gravity\n| attracts mass -->\nThe practical test",
                ),
                document,
                bold_headings=True,
            )
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertIn("rendered-comments: 2", stdout)

    def test_an_nd_citation_and_reference_are_traced(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace("Quill, 2024", "Quill, n.d.").replace(
                    "Quill, R. (2024).", "Quill, R. (n.d.)."
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace("Quill, R. (2024).", "Quill, R. (n.d.)."),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("citations: 2", stdout)
        self.assertIn("untraced-citation: 0", stdout)

    def test_an_nd_disambiguation_suffix_is_traced(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace("Quill, 2024", "Quill, n.d.-a").replace(
                    "Quill, R. (2024).", "Quill, R. (n.d.-a)."
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace("Quill, R. (2024).", "Quill, R. (n.d.-a)."),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("untraced-citation: 0", stdout)

    def test_a_parenthetical_two_author_citation_matches_its_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            multi_author = "Quill, R., & Vale, S. (2024)."
            run.draft.write_text(
                BODY.replace("(Quill, 2024, p. 6)", "(Quill & Vale, 2024)").replace(
                    "Quill, R. (2024).", multi_author
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace("Quill, R. (2024).", multi_author),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("untraced-citation: 0", stdout)

    def test_an_organizational_abbreviation_resolves_after_its_definition(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            organization = (
                "Centers for Disease Control and Prevention. (2024). Measuring usable access."
            )
            draft = BODY.replace("a 12% improvement", "an improvement").replace(
                "(Quill, 2024, p. 6)",
                "(Centers for Disease Control and Prevention [CDC], 2024)",
            ).replace(
                "The result does not prove",
                "A later section reaches the same source (CDC, 2024). The result does not prove",
            ).replace(
                "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                organization,
            )
            run.draft.write_text(draft, encoding="utf-8")
            second_record = """\
## CLAIM: The later section restates the organization source.
STATUS: sourced
SOURCE: government
REFERENCE: Centers for Disease Control and Prevention. (2024). Measuring usable access.
RESTATEMENT: The same source supports the later section.
RECENCY: current
RESOLVED: https://example.org/usable-access - read 2026-08-22
PAGE-YEAR: 2024 - stated on the page.
REFUTATION: stands - the page addresses the cited proposition.
"""
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    organization,
                ).replace(
                    "## CLAIM: The regulation supplies legal context.",
                    second_record
                    + "\n## CLAIM: The regulation supplies legal context.",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("citations: 3", stdout)
        self.assertIn("untraced-citation: 0", stdout)

    def test_a_narrative_organizational_abbreviation_defines_the_full_author(self):
        citations = artifact.read_citations(
            "Centers for Disease Control and Prevention (CDC, 2024) reported the result."
        )
        keys = artifact.citation_occurrence_keys(citations)

        self.assertEqual(1, len(citations))
        self.assertIn(
            ("centersfordiseasecontrolandprevention", "2024"),
            keys[0],
        )

    def test_a_signal_like_organization_keeps_its_full_narrative_definition(self):
        citations = artifact.read_citations(
            "As You Sow (AYS, 2024) reported the result; later (AYS, 2024) agreed."
        )
        keys = artifact.citation_occurrence_keys(citations)
        expected = (artifact.author_key("As You Sow"), "2024")

        self.assertIn(expected, keys[0])
        self.assertIn(expected, keys[1])

    def test_an_organizational_alias_applies_across_reference_years(self):
        citations = artifact.read_citations(
            "(Centers for Disease Control and Prevention [CDC], 2024) "
            "and later (CDC, 2023)."
        )
        keys = artifact.citation_occurrence_keys(citations)

        self.assertIn(
            ("centersfordiseasecontrolandprevention", "2023"),
            keys[1],
        )

    def test_a_unicode_personal_author_is_read_as_a_citation(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace("(Quill, 2024, p. 6)", "García (2024)").replace(
                    "Quill, R. (2024).", "García, M. (2024)."
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace("Quill, R. (2024).", "García, M. (2024)."),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("citations: 2", stdout)
        self.assertIn("untraced-citation: 0", stdout)

    def test_distinct_unicode_surnames_do_not_collapse(self):
        self.assertNotEqual(artifact.author_key("Müller"), artifact.author_key("Møller"))

    def test_accented_multi_author_initials_match_the_parenthetical_citation(self):
        reference = "García, É., & Müller, J. (2024). Title. Journal."

        self.assertIn(
            (artifact.author_key("García & Müller"), "2024"),
            artifact.reference_keys(reference),
        )

    def test_unicode_authors_outside_latin_one_are_read(self):
        for author in ("Černý", "Łukasz", "Māori Health Authority"):
            with self.subTest(author=author):
                citations = artifact.read_citations(f"{author} (2024) reports the result.")
                self.assertEqual(1, len(citations))
                self.assertEqual(author, citations[0].author)

    def test_narrative_signal_words_are_not_part_of_the_author(self):
        citations = artifact.read_citations(
            "As Quill (2024) explains, In García and Müller (2024) is a separate phrase."
        )

        keys = artifact.citation_occurrence_keys(citations)
        self.assertIn((artifact.author_key("Quill"), "2024"), keys[0])
        self.assertIn((artifact.author_key("García and Müller"), "2024"), keys[1])

    def test_signal_like_organizational_names_keep_their_full_key(self):
        for author in (
            "In Defense of Animals",
            "As You Sow",
            "By Design",
            "See Change Institute",
        ):
            with self.subTest(author=author):
                citations = artifact.read_citations(f"{author} (2024) reports the result.")
                keys = artifact.citation_occurrence_keys(citations)
                self.assertIn((artifact.author_key(author), "2024"), keys[0])

    def test_yearless_legal_citation_matches_a_dated_regulation_record(self):
        citations = artifact.read_citations("42 C.F.R. § 482.13 supplies the legal context.")
        reference = artifact.reference_keys("Patient rights, 42 C.F.R. § 482.13 (2024).")

        self.assertEqual(1, len(citations))
        self.assertTrue(set(artifact.citation_occurrence_keys(citations)[0]) & set(reference))

    def test_a_legal_reference_keys_on_its_name_and_section(self):
        self.assertEqual(
            (
                (artifact.author_key("Patient rights"), "2024"),
                (artifact.author_key("42 C.F.R. § 482.13"), "2024"),
                (artifact.author_key("42 C.F.R. § 482.13"), ""),
            ),
            artifact.reference_keys("Patient rights, 42 C.F.R. § 482.13 (2024)."),
        )

    def test_a_parenthesized_legal_citation_owns_its_year_span(self):
        body = "The rule applies (42 C.F.R. § 482.13, 2024) to this setting."

        citations = artifact.read_citations(body)

        self.assertEqual(1, len(citations))
        self.assertEqual("2024", citations[0].year)
        self.assertEqual("(42 C.F.R. § 482.13, 2024)", body[citations[0].start:citations[0].end])
        self.assertEqual((), scan._numeric_values(body))

    def test_the_shared_section_grammar_reads_subsections_without_taking_a_spaced_year(self):
        section = re.compile(artifact.LEGAL_SECTION_NUMBER)

        for written in (
            "414.56",
            "1.501(c)(3)-1",
            "164.512(b)(1)(v)",
            "53.4958-4",
            "1910.1030",
            "1395dd",
            "30-7-15b",
            "15-1-17",
            "19-7",
            "16-54-4",
            "60A-9-5a",
            "21-5F-1",
            "30-5-12b",
            "54.1-2957",
            "6B-2-5",
            "16-29B-19",
            "16-3C",
            "19-8-3.7",
            "414.56-414.60",
        ):
            with self.subTest(written=written):
                self.assertIsNotNone(section.fullmatch(written))
        self.assertEqual("414.56", section.match("414.56 (2025)").group())

    def test_the_wider_section_tail_keeps_the_ruled_bare_section_residue(self):
        for body, expected_numbers in (
            ("Section 3 of the plan sets § 5 as the floor.", ("3",)),
            ("The schedule calls this § 5-year planning.", ()),
        ):
            with self.subTest(body=body):
                self.assertEqual((), artifact.read_citations(body))
                self.assertEqual(expected_numbers, scan._numeric_values(body))

    def test_subsectioned_section_forms_drive_both_readers_independently(self):
        cases = (
            (
                "The rule applies (26 C.F.R. § 1.501(c)(3)-1, 2026).",
                "(26 C.F.R. § 1.501(c)(3)-1, 2026)",
            ),
            (
                "Under 26 C.F.R. § 1.501(c)(3)-1 (2026), the rule applies.",
                "26 C.F.R. § 1.501(c)(3)-1 (2026)",
            ),
            ("Under § 1.501(c)(3)-1, the rule applies.", None),
        )

        for body, legal_span in cases:
            with self.subTest(body=body):
                citations = artifact.read_citations(body)
                self.assertEqual(1 if legal_span else 0, len(citations))
                if legal_span is not None:
                    self.assertEqual(
                        legal_span,
                        body[citations[0].start : citations[0].end],
                    )
                self.assertEqual((), scan._numeric_values(body, citations))

    def test_the_ruled_legal_sources_drive_both_readers_independently(self):
        cases = (
            ("42 CFR", "482.23"),
            ("29 U.S.C.", "794"),
            ("16 CCR", "1481"),
            ("W. Va. Code", "60A-9-5a"),
            ("W. Va. Code R.", "19-8-3.7"),
        )

        for source, section in cases:
            body = f"The rule applies ({source} § {section}, 2024)."
            with self.subTest(source=source):
                citations = artifact.read_citations(body)
                self.assertEqual(1, len(citations))
                self.assertEqual(
                    f"({source} § {section}, 2024)",
                    body[citations[0].start : citations[0].end],
                )
                self.assertEqual((), scan._numeric_values(body, citations))

    def test_an_unlisted_or_bare_source_does_not_become_a_legal_citation(self):
        for body in ("The Code § 5 (2024).", "§ 5 (2024)."):
            with self.subTest(body=body):
                self.assertEqual((), artifact.read_citations(body))

    def test_a_legal_and_ordinary_citation_share_one_parenthetical_without_a_double_read(self):
        for inside in (
            "W. Va. Code § 60A-9-5a, 2021; Smith, 2020",
            "Smith, 2020; W. Va. Code § 60A-9-5a, 2021",
        ):
            body = f"The rule applies ({inside})."
            with self.subTest(inside=inside):
                citations = artifact.read_citations(body)
                self.assertEqual(2, len(citations))
                self.assertEqual(
                    {
                        (artifact.author_key("W. Va. Code § 60A-9-5a"), "2021"),
                        (artifact.author_key("Smith"), "2020"),
                    },
                    {
                        pair
                        for occurrence in artifact.citation_occurrence_keys(citations)
                        for pair in occurrence
                    },
                )

    def test_a_section_only_legal_record_is_a_post_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "Patient rights, 42 C.F.R. § 482.13 (2024).",
                    "42 C.F.R. § 482.13 (2024). Patient rights.",
                ),
                encoding="utf-8",
            )

            status, stdout, _ = run.grade("--show")

        self.assertEqual(1, status)
        self.assertIn("legal-reference-name: 1", stdout)
        self.assertIn("legal-reference-name: claims.md:", stdout)

    def test_a_subsectioned_section_only_legal_record_is_a_post_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "Patient rights, 42 C.F.R. § 482.13 (2024).",
                    "26 C.F.R. § 1.501(c)(3)-1 (2026).",
                ),
                encoding="utf-8",
            )

            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("legal-reference-name: 1", stdout)

    def test_a_section_only_legal_entry_is_a_reply_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            run = ReplyRun(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                REPLY_BODY.replace(
                    "Quill, R. (2024). Measuring usable access in community care. Journal of Care, 4(2), 10-18.",
                    "42 C.F.R. § 482.13 (2024). Patient rights.",
                ),
                encoding="utf-8",
            )
            with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()):
                status = reply_scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("legal-reference-name: 1", stdout.getvalue())

    def test_every_legal_entry_and_in_text_form_has_a_ruled_resolution(self):
        entries = {
            "name-and-section": (
                "Patient rights, 42 C.F.R. § 482.13 (2024).",
                (True, True, True, True, True),
            ),
            "section-only": (
                "42 C.F.R. § 482.13 (2024). Patient rights.",
                (True, True, True, True, True),
            ),
        }
        forms = (
            "42 C.F.R. § 482.13 (2024)",
            "(42 C.F.R. § 482.13, 2024)",
            "42 C.F.R. § 482.13",
            "Patient rights (2024)",
            "(Patient rights, 2024)",
        )
        for entry_name, (entry, expected) in entries.items():
            keys = frozenset(artifact.reference_keys(entry))
            for form, should_resolve in zip(forms, expected):
                with self.subTest(entry=entry_name, form=form):
                    citations = artifact.read_citations(
                        f"Under {form}, the rule applies.", keys
                    )
                    resolved = any(
                        key in keys
                        for occurrence in artifact.citation_occurrence_keys(citations)
                        for key in occurrence
                    )
                    self.assertEqual(should_resolve, resolved)

    def test_a_name_narrative_is_read_from_the_reference_key_set(self):
        keys = frozenset(
            artifact.reference_keys("Patient rights, 42 C.F.R. § 482.13 (2024).")
        )

        citations = artifact.read_citations("Patient rights (2024) governs care.", keys)

        self.assertEqual(1, len(citations))
        self.assertEqual("Patient rights", citations[0].author)

    def test_a_section_first_entry_still_evidences_its_trailing_name(self):
        keys = artifact.reference_keys(
            "42 C.F.R. § 482.13 (2024). Patient rights."
        )

        self.assertIn((artifact.author_key("Patient rights"), "2024"), keys)

    def test_an_unmatched_year_is_not_reclassified_as_a_citation(self):
        keys = frozenset({(artifact.author_key("Patient rights"), "2024")})
        body = "The policy was finalized (2024)."

        citations = artifact.read_citations(body, keys)

        self.assertEqual((), citations)
        self.assertEqual(("2024",), scan._numeric_values(body, citations))

    def test_the_longest_matching_reference_name_wins(self):
        keys = frozenset(
            {
                (artifact.author_key("Rights"), "2024"),
                (artifact.author_key("Patient rights"), "2024"),
            }
        )

        citations = artifact.read_citations("Patient rights (2024) governs care.", keys)

        self.assertEqual("Patient rights", citations[0].author)

    def test_an_organizational_comma_is_not_mistaken_for_a_personal_author(self):
        reference = (
            "Rights, A. Very long regulation name title, "
            "42 C.F.R. § 482.13 (2024)."
        )
        keys = frozenset(artifact.reference_keys(reference))
        expected_key = "rightsaverylongregulationnametitle"

        citations = artifact.read_citations(
            "Rights, A. Very long regulation name title (2024) governs care.",
            keys,
        )

        self.assertIn((expected_key, "2024"), keys)
        self.assertEqual(1, len(citations))
        self.assertEqual("Rights, A. Very long regulation name title", citations[0].author)

    def test_personal_author_initials_still_reduce_to_the_surname(self):
        self.assertEqual("quill", artifact.author_key("Quill, R. J."))

    def test_text_beyond_the_longest_key_bound_does_not_change_the_walk(self):
        class CountedKeys(frozenset):
            checks = 0

            def __contains__(self, key):
                self.checks += 1
                return super().__contains__(key)

        keys = CountedKeys(
            {
                (artifact.author_key("Patient rights"), "2024"),
                (artifact.author_key("Rights"), "2024"),
            }
        )
        with mock.patch.object(
            artifact, "author_key", wraps=artifact.author_key
        ) as normalizer:
            short = artifact.read_citations(
                "Patient rights (2024) governs care.", keys
            )
            short_normalizations = normalizer.call_count
            short_checks = keys.checks
            normalizer.reset_mock()
            keys.checks = 0
            long = artifact.read_citations(
                "Rights, A. "
                + ("unrelated " * 1_000)
                + "Patient rights (2024) governs care.",
                keys,
            )
            long_normalizations = normalizer.call_count

        self.assertEqual(short[0].author, long[0].author)
        self.assertEqual(short[0].year, long[0].year)
        self.assertEqual(short_checks, keys.checks)
        self.assertEqual(short_normalizations + 1, long_normalizations)

    def test_a_yearless_section_only_record_is_a_post_finding(self):
        claims = CLAIMS.replace(
            "Patient rights, 42 C.F.R. § 482.13 (2024).",
            "42 C.F.R. § 482.13",
        )
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(claims, encoding="utf-8")

            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("legal-reference-name: 1", stdout)

    def test_the_post_grader_reads_and_resolves_against_one_key_set_object(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "42 C.F.R. § 482.13 provides",
                    "Patient rights (2024) provides",
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                scan, "read_citations", wraps=artifact.read_citations
            ) as reader, mock.patch.object(
                scan, "_citation_keys", wraps=scan._citation_keys
            ) as key_reader, mock.patch.object(
                scan.ClaimReferenceIndex,
                "matching_record_indices",
                autospec=True,
                side_effect=scan.ClaimReferenceIndex.matching_record_indices,
            ) as resolver:
                status, _, _ = run.grade()

        key_set = key_reader.call_args.args[1]
        self.assertEqual(0, status)
        self.assertIs(reader.call_args.args[1], key_set)
        self.assertIs(resolver.call_args.args[0], key_set)

    def test_the_reply_grader_reads_and_resolves_against_one_key_set_object(self):
        personal = (
            "Quill, R. (2024). Measuring usable access in community care. "
            "Journal of Care, 4(2), 10-18."
        )
        legal = (
            "Patient rights, 42 C.F.R. § 482.13 (2024). "
            "https://example.org/regulation"
        )
        with tempfile.TemporaryDirectory() as temp:
            run = ReplyRun(Path(temp))
            (run.root / "claims.md").write_text(
                REPLY_CLAIMS.replace(personal, legal), encoding="utf-8"
            )
            response = run.root / "response-maren.md"
            response.write_text(
                REPLY_BODY.replace("(Quill, 2024)", "Patient rights (2024)").replace(
                    personal, legal
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                reply_scan, "read_citations", wraps=artifact.read_citations
            ) as reader, mock.patch.object(
                reply_scan, "_citation_findings", wraps=reply_scan._citation_findings
            ) as resolver, redirect_stdout(io.StringIO()), redirect_stderr(
                io.StringIO()
            ):
                status = reply_scan.main([temp])

        self.assertEqual(0, status)
        self.assertIs(reader.call_args.args[1], resolver.call_args.args[2])

    def test_dated_legal_citation_is_one_citation_not_a_body_number(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "42 C.F.R. § 482.13 provides",
                    "42 C.F.R. § 482.13 (2024) provides",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("numeric claims: 1", stdout)
        self.assertIn("untraced-citation: 0", stdout)

    def test_shared_discussion_tokens_are_one_object(self):
        for name in (
            "WORD",
            "NUMBER",
            "AMPLIFICATION",
            "INVOKED",
            "CLAIM_BLOCK",
            "RESTATEMENT",
            "read_citations",
            "reference_key",
            "split_references",
        ):
            with self.subTest(name=name):
                self.assertIs(getattr(artifact, name), getattr(reply_scan, name))
                self.assertIs(getattr(artifact, name), getattr(scan, name))


class APostedInitialEntryHasItsOwnReading(unittest.TestCase):
    POST_URL = "https://example.org/courses/1/discussion_topics/2?entry_id=41"

    def posted_run(self, root: Path) -> Run:
        run = Run(root)
        (root / "post.md").write_text(
            f"POST-URL: {self.POST_URL}\n"
            "POSTED: 2026-08-28T19:30:00-04:00\n\n"
            + BODY,
            encoding="utf-8",
        )
        (root / "reread.md").write_text(
            "## REREAD: post.md\n"
            f"POST-URL: {self.POST_URL}\n"
            "POSTED: 2026-08-28T19:30:00-04:00\n"
            "READ: 2026-08-28\n"
            "VERDICT: matches - The headings, paragraphs, and references are present.\n",
            encoding="utf-8",
        )
        return run

    def test_a_complete_initial_post_reading_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            status, stdout, stderr = self.posted_run(Path(temp)).grade()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("missing-posted-reading: 0", stdout)

    def test_a_reply_record_does_not_cover_the_initial_post(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.posted_run(Path(temp))
            reread = run.root / "reread.md"
            reread.write_text(
                reread.read_text(encoding="utf-8").replace(
                    "## REREAD: post.md", "## REREAD: response-maren.md"
                ),
                encoding="utf-8",
            )

            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("missing-posted-reading: 1", stdout)

    def test_the_reading_locator_must_equal_post_md(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.posted_run(Path(temp))
            reread = run.root / "reread.md"
            reread.write_text(
                reread.read_text(encoding="utf-8").replace("entry_id=41", "entry_id=99"),
                encoding="utf-8",
            )

            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("borrowed-locator: 1", stdout)

    def test_the_initial_post_reading_needs_an_entry_id(self):
        with tempfile.TemporaryDirectory() as temp:
            run = self.posted_run(Path(temp))
            reread = run.root / "reread.md"
            reread.write_text(
                reread.read_text(encoding="utf-8").replace("?entry_id=41", "", 1),
                encoding="utf-8",
            )

            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("unlocated-reading: 1", stdout)

    def test_unknown_and_bare_verdicts_are_post_findings(self):
        for replacement, kind in (
            ("uncertain - The board was opened.", "unknown-verdict"),
            ("diverges", "bare-verdict"),
        ):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                run = self.posted_run(Path(temp))
                reread = run.root / "reread.md"
                reread.write_text(
                    reread.read_text(encoding="utf-8").replace(
                        "matches - The headings, paragraphs, and references are present.",
                        replacement,
                    ),
                    encoding="utf-8",
                )

                status, stdout, _ = run.grade()

            self.assertEqual(1, status)
            self.assertIn(f"{kind}: 1", stdout)


class ARecognizedButRefusedLabelStopsTheScan(unittest.TestCase):
    def test_every_recognizable_label_form_has_both_ruled_grader_verdicts(self):
        forms = {
            "References": (2, 2),
            "**References**": (0, 2),
            "## References": (2, 0),
            "*References*": (2, 2),
            "References:": (2, 2),
            "Reference": (2, 2),
        }
        for label, expected in forms.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as reply_temp:
                reply = ReplyRun(Path(reply_temp))
                response = reply.root / "response-maren.md"
                response.write_text(
                    REPLY_BODY.replace("**References**", label),
                    encoding="utf-8",
                )
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    reply_status = reply_scan.main([reply_temp])
            with tempfile.TemporaryDirectory() as post_temp:
                post = Run(Path(post_temp))
                post.draft.write_text(
                    BODY.replace("## References", label),
                    encoding="utf-8",
                )
                post_status, _, _ = post.grade()

            self.assertEqual(expected, (reply_status, post_status))

    def test_the_shared_recognizer_is_a_superset_of_both_accepted_patterns(self):
        forms = {
            "References": (False, False),
            "**References**": (True, False),
            "## References": (False, True),
            "*References*": (False, False),
            "References:": (False, False),
            "Reference": (False, False),
        }
        for label, accepted in forms.items():
            with self.subTest(label=label):
                recognized = artifact.REFERENCE_LABEL_RECOGNIZER.search(label) is not None
                reply_accepted = reply_scan.REFERENCE_LABEL.search(label) is not None
                post_accepted = scan.REFERENCE_HEADING.search(label) is not None
                self.assertTrue(recognized)
                self.assertEqual(accepted, (reply_accepted, post_accepted))
                self.assertFalse((reply_accepted or post_accepted) and not recognized)

    def test_a_bold_references_label_names_the_line_and_ungrades_dependent_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace("## References", "**References**"),
                encoding="utf-8",
            )
            status, stdout, stderr = run.grade()

        self.assertEqual(2, status)
        self.assertIn("**References**", stderr)
        for row in (
            "word-floor",
            "reference-minimum",
            "untraced-number",
            "untraced-citation",
        ):
            with self.subTest(row=row):
                self.assertIn(f"{row}: not graded", stdout)
        self.assertIn("claim records: not graded", stdout)
        self.assertIn("bold-headings: not graded", stdout)

    def test_a_render_finding_keeps_exit_one_when_the_reference_boundary_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace("## References", "**References**"),
                encoding="utf-8",
            )
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document)
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(1, status)
        self.assertIn("bold-headings: 1", stdout)


class TheSubmissionJoinsItsRunDirectory(unittest.TestCase):
    def roots(self, root: Path):
        return (
            mock.patch.object(coursework_run, "output_root", return_value=root / "output"),
            mock.patch.object(coursework_run, "scratch_root", return_value=root / "scratch"),
        )

    def make(self, root: Path, run_key: str, draft_key: str | None = None):
        run = root / "scratch" / "runs" / run_key
        run.mkdir(parents=True)
        (run / "bar.md").write_text(BAR, encoding="utf-8")
        (run / "claims.md").write_text(CLAIMS, encoding="utf-8")
        draft = root / "output" / "discussions" / f"{draft_key or run_key}-2026-08-22.md"
        draft.parent.mkdir(parents=True)
        draft.write_text(BODY, encoding="utf-8")
        return run, draft

    def test_a_matching_submission_and_run_pass_the_join(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            run, draft = self.make(root, "nur0000-m2-discussion")
            first, second = self.roots(root)
            with first, second:
                status = scan.main([str(run), "--draft", str(draft)])
        self.assertEqual(status, 0)

    def test_a_submission_with_a_different_key_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            run, draft = self.make(root, "nur0000-m2-discussion", "nur0000-m3-discussion")
            first, second = self.roots(root)
            stderr = io.StringIO()
            with first, second, redirect_stderr(stderr):
                status = scan.main([str(run), "--draft", str(draft)])
        self.assertEqual(status, 2)
        self.assertIn("does not belong", stderr.getvalue())

    def test_a_submission_with_no_derived_run_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            loose = root / "loose-run"
            loose.mkdir()
            (loose / "bar.md").write_text(BAR, encoding="utf-8")
            (loose / "claims.md").write_text(CLAIMS, encoding="utf-8")
            draft = root / "output" / "discussions" / "nur0000-m2-discussion-2026-08-22.md"
            draft.parent.mkdir(parents=True)
            draft.write_text(BODY, encoding="utf-8")
            first, second = self.roots(root)
            stderr = io.StringIO()
            with first, second, redirect_stderr(stderr):
                status = scan.main([str(loose), "--draft", str(draft)])
        self.assertEqual(status, 2)
        self.assertIn("no run directory", stderr.getvalue())


class TheSignedBarIsTheScannerInput(unittest.TestCase):
    def test_an_unsigned_bar_is_not_reported_as_a_clean_scan(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "bar.md").write_text(BAR.replace("SIGNED: 2026-08-22\n", ""), encoding="utf-8")
            status, stdout, stderr = run.grade()

        self.assertEqual(2, status)
        self.assertEqual("", stdout)
        self.assertIn("SIGNED", stderr)

    def test_a_duplicate_bar_field_is_refused_instead_of_last_winning(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            duplicate = BAR.replace(
                "WORD-FLOOR: 100\n",
                "WORD-FLOOR: 100\nWORD-FLOOR: 0\n",
            )
            (run.root / "bar.md").write_text(duplicate, encoding="utf-8")
            status, stdout, stderr = run.grade()

        self.assertEqual(2, status)
        self.assertEqual("", stdout)
        self.assertIn("duplicate WORD-FLOOR", stderr)

    def test_a_missing_draft_option_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = scan.main([str(run.root)])

        self.assertEqual(2, status)
        self.assertIn("--draft", stderr.getvalue())


class TheMechanicalBarRowsAreGraded(unittest.TestCase):
    def test_a_post_below_the_word_floor_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text("Short post.\n\n## References\n\nQuill, R. (2024). Title. Journal.\n", encoding="utf-8")
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("word-floor: 1", stdout)

    def test_a_post_below_the_reference_minimum_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "bar.md").write_text(BAR.replace("REFERENCE-MINIMUM: 1", "REFERENCE-MINIMUM: 2"), encoding="utf-8")
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("reference-minimum: 1", stdout)

    def test_an_untraced_body_number_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(BODY.replace("12% improvement", "15% improvement"), encoding="utf-8")
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("untraced-number: 1", stdout)

    def test_repeated_numeric_values_need_one_tracing_record(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "The result does not prove",
                    "A second program also reported a 12% improvement. The result does not prove",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("numeric claims: 1", stdout)
        self.assertIn("untraced-number: 0", stdout)

    def test_one_record_can_trace_two_numbers_and_carry_its_citation(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            claims = CLAIMS.replace(
                "Completed visits improved by 12%",
                "Completed visits improved by 12% across 500 visits",
            )
            (run.root / "claims.md").write_text(claims, encoding="utf-8")
            run.draft.write_text(
                BODY.replace(
                    "The result does not prove",
                    "The sample included 500 visits. The result does not prove",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("untraced-number: 0", stdout)
        self.assertIn("untraced-citation: 0", stdout)

    def test_a_nonnumeric_citation_needs_its_own_claim_record(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text("DATE: 2026-08-22\n", encoding="utf-8")
            run.draft.write_text(BODY.replace("a 12% improvement", "an improvement"), encoding="utf-8")
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("citations: 2", stdout)
        self.assertIn("untraced-citation: 2", stdout)
        self.assertIn("respent-record: 0", stdout)

    def test_two_citations_of_one_source_cannot_spend_one_claim_record(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "The result does not prove",
                    "Quill (2024) reports the same result. The result does not prove",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade("--show")

        self.assertEqual(1, status)
        self.assertIn("untraced-citation: 0", stdout)
        self.assertIn("respent-record: 1", stdout)
        self.assertIn(
            "2 citations of Quill (2024) share 1 claim record — 1 short",
            stdout,
        )

    def test_a_contended_shortfall_reports_the_maximal_deficiency(self):
        second_quill_record = """\
## CLAIM: Quill also supports the combined-program proposition.
STATUS: sourced
SOURCE: peer-reviewed
REFERENCE: Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.
RESTATEMENT: The source reports the same combined-program outcome.
RECENCY: current
RESOLVED: https://example.org/usable-access - read 2026-08-22
PAGE-YEAR: 2024 - stated on the article masthead.
REFUTATION: stands - the article addresses the cited proposition.
"""
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "## CLAIM: The regulation supplies legal context.",
                    second_quill_record
                    + "\n## CLAIM: The regulation supplies legal context.",
                ),
                encoding="utf-8",
            )
            run.draft.write_text(
                BODY.replace(
                    "The result does not prove",
                    "Quill (2024) reports the result twice (Quill, 2024). "
                    "The result does not prove",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade("--show")

        self.assertEqual(1, status)
        self.assertIn("untraced-citation: 0", stdout)
        self.assertIn("respent-record: 1", stdout)
        self.assertIn(
            "3 citations of Quill (2024) share 2 claim records — 1 short",
            stdout,
        )

    def test_a_multiword_organizational_author_matches_its_claim_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            organization = (
                "World Health Organization. (2024). Measuring usable access. "
                "Journal of Care, 4(2), 10-18."
            )
            run.draft.write_text(
                BODY.replace("(Quill, 2024, p. 6)", "World Health Organization (2024)").replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    organization,
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    organization,
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("untraced-citation: 0", stdout)

    def test_organizational_authors_with_the_same_prefix_do_not_collide(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "(Quill, 2024, p. 6)",
                    "Department of Health and Human Services (2024)",
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    "Department of Health and Safety. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("untraced-citation: 1", stdout)

    def test_an_organizational_and_phrase_does_not_gain_a_personal_author_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "(Quill, 2024, p. 6)",
                    "Centers for Disease Control and Prevention (2024)",
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    "Centers for Disease Control. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("untraced-citation: 1", stdout)

    def test_a_two_word_organization_does_not_match_a_personal_author(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "(Quill, 2024, p. 6)",
                    "Research and Development (2024)",
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    "Research, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("untraced-citation: 1", stdout)

    def test_an_organizational_author_keeps_an_internal_comma(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            organization = (
                "Department of Health, Division of Access. (2024). Measuring usable access. "
                "Journal of Care, 4(2), 10-18."
            )
            run.draft.write_text(
                BODY.replace(
                    "(Quill, 2024, p. 6)",
                    "(Department of Health, Division of Access, 2024)",
                ).replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    organization,
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    organization,
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("untraced-citation: 0", stdout)

    def test_standalone_page_locators_are_not_numeric_claims(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "The result does not prove",
                    "See p. 6 and pages 8–10 for context. The result does not prove",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("numeric claims: 1", stdout)


class CountedPreferencesNeverBecomeFindings(unittest.TestCase):
    def test_an_invoked_source_with_a_substantive_property_is_counted(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "# Access Is More Than Availability",
                    "# Access Is More Than Availability\n\n"
                    "<!-- INVOKED: black hole | it pulls everything near it in -->",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("invoked sources: 1", stdout)
        self.assertIn("unfilled invoked properties: 0 (counted, not graded)", stdout)

    def test_a_named_principle_with_a_predicate_is_substantive(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "# Access Is More Than Availability",
                    "# Access Is More Than Availability\n\n"
                    "<!-- INVOKED: Marcus Aurelius | the obstacle becomes the way -->",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("unfilled invoked properties: 0 (counted, not graded)", stdout)

    def test_incomplete_and_self_restating_markers_are_counted_without_failing(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "# Access Is More Than Availability",
                    "# Access Is More Than Availability\n\n"
                    "<!-- INVOKED: black hole | -->\n"
                    "<!-- INVOKED: hole | hole -->\n"
                    "<!-- INVOKED: | it pulls everything in -->\n"
                    "<!-- INVOKED: hole -->",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("invoked sources: 4", stdout)
        self.assertIn("unfilled invoked properties: 4 (counted, not graded)", stdout)

    def test_show_retains_each_invoked_source_domain_and_property(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "# Access Is More Than Availability",
                    "# Access Is More Than Availability\n\n"
                    "<!-- INVOKED: black hole | nothing escapes -->",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade("--show")

        self.assertEqual(0, status)
        self.assertIn("invoked source: black hole | nothing escapes", stdout)

    def test_the_word_ceiling_and_pre_496_marker_are_reported_without_failing(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace(
                    "# Access Is More Than Availability",
                    "# Access Is More Than Availability\n\n<!-- AMPLIFICATION: craft metaphor -->",
                ).replace(
                    "\n## References",
                    "\n" + " ".join(["reasoning"] * 100) + "\n\n## References",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("word ceiling exceeded: yes (counted, never graded)", stdout)
        self.assertIn("pre-#496 markers: 1 (counted, not graded)", stdout)
        self.assertNotIn("amplifications:", stdout)

    def test_the_closed_legal_source_vocabulary_prints_on_every_run(self):
        with tempfile.TemporaryDirectory() as temp:
            status, stdout, _ = Run(Path(temp)).grade()

        self.assertEqual(0, status)
        self.assertIn(scan.legal_source_vocabulary_covered(), stdout)

        widened = (*scan.LEGAL_SOURCE_VOCABULARY, "Example Code")
        with mock.patch.object(scan, "LEGAL_SOURCE_VOCABULARY", widened):
            self.assertIn(str(len(widened)), scan.legal_source_vocabulary_covered())


class ProseBarElementsStayDeclaredReadings(unittest.TestCase):
    def test_the_declared_limits_are_one_named_object(self):
        self.assertEqual(
            tuple((subject, reason) for subject, reason, _ in scan.DECLARED_LIMITS),
            scan.NOT_REACHED,
        )
        self.assertTrue(all(len(reason.split()) > 8 for _key, reason in scan.NOT_REACHED))
        for _subject, _reason, disposition in scan.DECLARED_LIMITS:
            self.assertIsInstance(disposition, scan.EvidenceDisposition)

    def test_an_isbn_bar_element_is_not_pattern_matched_into_a_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            bar = BAR.replace(
                "> Initial posts must contain 100 to 180 words and at least one reference.",
                "> Initial posts must contain 100 to 180 words, at least one reference, and the textbook ISBN.",
            )
            (run.root / "bar.md").write_text(bar, encoding="utf-8")
            status, stdout, _ = run.grade()

        self.assertEqual(0, status)
        self.assertIn("findings: 0", stdout)


class TheRenderedDocumentContractIsPublished(unittest.TestCase):
    def skill_text(self):
        return (REPO_ROOT / "skills" / "discussion-post" / "SKILL.md").read_text(
            encoding="utf-8"
        )

    def test_the_skill_names_every_rendered_document_report_row(self):
        text = self.skill_text()
        for row in (
            scan.BOLD_HEADINGS,
            scan.RENDERED_COMMENTS,
            scan.RENDERED_TEXT,
            scan.RENDERED_PAGES,
        ):
            with self.subTest(row=row):
                self.assertIn(f"`{row}`", text)

    def test_the_skill_names_every_claim_record_report_row(self):
        text = self.skill_text()
        for row in (
            scan.UNTRACED_NUMBER,
            scan.UNTRACED_CITATION,
            scan.RESPENT_RECORD,
        ):
            with self.subTest(row=row):
                self.assertIn(f"`{row}`", text)

    def test_the_skill_publishes_the_counted_render_route(self):
        text = self.skill_text()
        self.assertIn("discussion_post_render.py", text)
        self.assertIn("render/pass-N/", text)
        self.assertIn(f"{render.RASTER_DPI}-dpi", text)
        self.assertIn("## RENDERED: post.md", text)
        for source in artifact.RENDERED_SOURCES:
            with self.subTest(source=source):
                self.assertIn(source, text)
        self.assertIn("Re-renders append", text)

    def test_the_skill_recovers_an_editor_change_before_force(self):
        text = self.skill_text()
        self.assertIn("Markdown is the authoritative artifact", text)
        self.assertIn("recover the edit", text)
        self.assertIn("claim ledger", text)


class EveryBehaviorLimitHasALiveHandler(unittest.TestCase):
    HANDLERS = {
        "whether equal numeric values always describe one fact": (
            "TheMechanicalBarRowsAreGraded.test_repeated_numeric_values_need_one_tracing_record",
            "TheMechanicalBarRowsAreGraded.test_an_untraced_body_number_fails",
        ),
        "whether rendered-document rows were graded when --docx was omitted": (
            "ACompletePostPasses.test_the_docx_row_is_not_graded_when_no_archive_is_supplied",
            "ACompletePostPasses.test_a_directly_formatted_heading_passes_the_docx_row",
        ),
        "whether reference-dependent rows ran after a refused reference label": (
            "ARecognizedButRefusedLabelStopsTheScan.test_a_bold_references_label_names_the_line_and_ungrades_dependent_rows",
            "ACompletePostPasses.test_report_is_counts_only_and_excludes_citation_and_statute_numbers",
        ),
    }

    def test_behavior_subjects_are_exactly_the_handled_subjects(self):
        behavior = {
            subject
            for subject, _reason, disposition in scan.DECLARED_LIMITS
            if disposition is scan.EvidenceDisposition.BEHAVIOR
        }
        self.assertEqual(behavior, set(self.HANDLERS))

    def test_every_handler_runs_a_blind_spot_and_positive_control(self):
        for subject, (blind_spot, positive_control) in self.HANDLERS.items():
            with self.subTest(subject=subject):
                self.assertNotEqual(blind_spot, positive_control)
                for named in (blind_spot, positive_control):
                    result = unittest.TestResult()
                    unittest.defaultTestLoader.loadTestsFromName(
                        f"test_discussion_post_scan.{named}"
                    ).run(result)
                    self.assertTrue(
                        result.wasSuccessful(),
                        f"{subject}: {named}: {result.errors + result.failures}",
                    )


class TheSharedConformanceKitStatesItsBoundary(unittest.TestCase):
    def test_claude_distinguishes_universal_and_opt_in_membership(self):
        guidance = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertIn("`for_module` is universal by convention", guidance)
        self.assertIn("`gate_conformance` is opt-in", guidance)
        self.assertIn("banner flags", guidance)


if __name__ == "__main__":
    unittest.main()
