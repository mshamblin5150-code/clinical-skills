"""Behavior tests for ``discussion_post_scan`` at its public artifact seam.

Every board, bar, claim, and draft is synthetic. No classmate or patient is
represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import discussion_post_scan as scan
import coursework_run
import discussion_reply_scan as reply_scan
import discussion_artifact as artifact
import docx_write
from grader_conformance import for_module


GraderConformance = for_module(scan)


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

## CLAIM: Quill supports the combined-program proposition.
STATUS: sourced
SOURCE: peer-reviewed
REFERENCE: Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.
RESTATEMENT: The source reports an outcome for the combined program.
RECENCY: current
RESOLVED: https://example.org/usable-access - read 2026-08-22
PAGE-YEAR: 2024 - stated on the article masthead.
REFUTATION: stands - the article addresses the cited proposition.

## CLAIM: The regulation supplies legal context.
STATUS: sourced
SOURCE: guideline in force
REFERENCE: 42 C.F.R. § 482.13 (2024).
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
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = scan.main([str(self.root), "--draft", str(self.draft), *extra])
        return status, stdout.getvalue(), stderr.getvalue()


class ACompletePostPasses(unittest.TestCase):
    def test_report_is_counts_only_and_excludes_citation_and_statute_numbers(self):
        with tempfile.TemporaryDirectory() as temp:
            status, stdout, stderr = Run(Path(temp)).grade()

        self.assertEqual(0, status)
        self.assertEqual("", stderr)
        self.assertIn("references: 1", stdout)
        self.assertIn("numeric claims: 1", stdout)
        self.assertIn("untraced-number: 0", stdout)
        self.assertNotIn("Quill", stdout)
        self.assertNotIn("482.13", stdout)

    def test_the_docx_row_is_not_graded_when_no_archive_is_supplied(self):
        with tempfile.TemporaryDirectory() as temp:
            status, stdout, _ = Run(Path(temp)).grade()

        self.assertEqual(0, status)
        self.assertIn("bold-headings: not graded", stdout)

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
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(0, status)
        self.assertIn("bold-headings: 0", stdout)

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
            (run.root / "claims.md").write_text(
                CLAIMS.replace(
                    "Quill, R. (2024). Measuring usable access. Journal of Care, 4(2), 10-18.",
                    organization,
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
        reference = artifact.reference_keys("42 C.F.R. § 482.13 (2024).")

        self.assertEqual(1, len(citations))
        self.assertTrue(set(artifact.citation_occurrence_keys(citations)[0]) & set(reference))

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
            "CLAIM_BLOCK",
            "RESTATEMENT",
            "read_citations",
            "reference_key",
            "split_references",
        ):
            with self.subTest(name=name):
                self.assertIs(getattr(artifact, name), getattr(reply_scan, name))
                self.assertIs(getattr(artifact, name), getattr(scan, name))


class ARecognizedButRefusedLabelStopsTheScan(unittest.TestCase):
    def test_every_recognizable_label_form_has_the_ruled_post_verdict(self):
        forms = {
            "References": 2,
            "**References**": 2,
            "## References": 0,
            "*References*": 2,
            "References:": 2,
            "Reference": 2,
        }
        for label, expected in forms.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temp:
                run = Run(Path(temp))
                run.draft.write_text(
                    BODY.replace("## References", label),
                    encoding="utf-8",
                )
                status, _, _ = run.grade()

            self.assertEqual(expected, status)

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
        self.assertIn("bold-headings: not graded", stdout)

    def test_a_refused_label_keeps_exit_two_when_the_docx_row_also_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            run.draft.write_text(
                BODY.replace("## References", "**References**"),
                encoding="utf-8",
            )
            document = run.root / "post.docx"
            docx_write.write_docx(BODY, document)
            status, stdout, _ = run.grade("--docx", str(document))

        self.assertEqual(2, status)
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

    def test_two_claims_using_the_same_number_need_two_records(self):
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

        self.assertEqual(1, status)
        self.assertIn("numeric claims: 2", stdout)
        self.assertIn("untraced-number: 1", stdout)

    def test_one_record_cannot_discharge_two_numbers_and_a_citation(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            one_record = CLAIMS.split("\n## CLAIM: Quill supports", 1)[0]
            one_record = one_record.replace(
                "Completed visits improved by 12%",
                "Completed visits improved by 12% across 500 visits",
            )
            (run.root / "claims.md").write_text(one_record, encoding="utf-8")
            run.draft.write_text(
                BODY.replace(
                    "The result does not prove",
                    "The sample included 500 visits. The result does not prove",
                ),
                encoding="utf-8",
            )
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("untraced-number: 1", stdout)
        self.assertIn("untraced-citation: 2", stdout)

    def test_a_nonnumeric_citation_needs_its_own_claim_record(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text("DATE: 2026-08-22\n", encoding="utf-8")
            run.draft.write_text(BODY.replace("a 12% improvement", "an improvement"), encoding="utf-8")
            status, stdout, _ = run.grade()

        self.assertEqual(1, status)
        self.assertIn("citations: 2", stdout)
        self.assertIn("untraced-citation: 2", stdout)

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
    def test_the_word_ceiling_and_amplification_are_reported_without_failing(self):
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
        self.assertIn("amplifications: 1 (counted, never graded)", stdout)


class ProseBarElementsStayDeclaredReadings(unittest.TestCase):
    def test_the_declared_limits_are_one_named_object(self):
        self.assertEqual(
            {
                "whether the bar transcription is complete",
                "whether the topic overrides the syllabus",
                "whether a prose bar element is satisfied",
                "whether a reference actually supports the required proposition",
                "whether a claim record describes the cited sentence",
            },
            {key for key, _reason in scan.NOT_REACHED},
        )
        self.assertTrue(all(len(reason.split()) > 8 for _key, reason in scan.NOT_REACHED))

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


if __name__ == "__main__":
    unittest.main()
