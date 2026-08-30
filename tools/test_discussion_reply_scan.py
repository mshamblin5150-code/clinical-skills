"""Behavior tests for ``discussion_reply_scan`` at its public run-directory seam.

Every board and reply is synthetic. No classmate or patient is represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import discussion_reply_scan as scan
from grader_conformance import for_module, gate_conformance


GraderConformance = for_module(scan)
GateConformance = gate_conformance(scan)
REPO_ROOT = Path(__file__).resolve().parents[1]
DISCUSSION_REPLY_SKILL = REPO_ROOT / "skills" / "discussion-reply" / "SKILL.md"


BODY = """\
Maren, your distinction between access and availability is persuasive because it
keeps the policy question tied to what a patient can actually use. I agree that
adding a clinic does not solve the problem when transportation, work schedules,
and appointment timing still place care out of reach. The evidence also adds an
important limit to that argument: a program reported a 12% improvement only when
evening access and transit support were offered together (Quill, 2024). That
combination matters because it shifts the intervention from a building-centered
answer to a patient-centered one. But here's the thing: access should be judged
at the point where care becomes usable, not where a service merely exists. Your
post opens the right door by treating availability as necessary while refusing
to treat it as sufficient. I would carry that distinction into the evaluation
plan and measure completed visits rather than scheduled appointments.

**References**

Quill, R. (2024). Measuring usable access in community care. Journal of Care, 4(2), 10-18.
"""

CLAIMS = """\
DATE: 2026-08-22

## CLAIM: [REPLY: maren] The combined program reported a 12% improvement.
STATUS: sourced
SOURCE: peer-reviewed
REFERENCE: Quill, R. (2024). Measuring usable access in community care. Journal of Care, 4(2), 10-18.
RESTATEMENT: Completed visits improved by 12% when evening access and transit support were combined.
RECENCY: current
RESOLVED: https://example.org/usable-access - read 2026-08-22
PAGE-YEAR: 2024 - stated on the article masthead.
REFUTATION: stands - the article reports the measure in its results table.
"""

REREAD = """\
## REREAD: response-maren.md
POST-URL: https://example.org/courses/1/discussion_topics/2?entry_id=31
POSTED: 2026-08-28T20:10:00-04:00
READ: 2026-08-28
VERDICT: matches - The paragraphs, references, and bold label are present.
"""


class Run:
    def __init__(self, root: Path):
        self.root = root
        (root / "posts").mkdir()
        (root / "board-2026-08-22.md").write_text(
            "COURSE: NUR 0000\nMODULE: 2\n", encoding="utf-8"
        )
        (root / "posts" / "maren-quill.md").write_text(
            "AUTHOR: Maren Quill\nREPLIES: 0\n"
            "POST-URL: https://example.org/courses/1/discussion_topics/2?entry_id=21\n\n"
            "A synthetic classmate post.\n",
            encoding="utf-8",
        )
        (root / "claims.md").write_text(CLAIMS, encoding="utf-8")
        (root / "response-maren.md").write_text(BODY, encoding="utf-8")
        (root / "reread.md").write_text(REREAD, encoding="utf-8")


class ACompleteRunPasses(unittest.TestCase):
    def test_the_bold_references_label_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY,
                encoding="utf-8",
            )
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(0, status)

    def test_cli_reports_counts_without_exposing_the_addressed_name(self):
        with tempfile.TemporaryDirectory() as temp:
            Run(Path(temp))
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = scan.main([temp])

        self.assertEqual(0, status)
        self.assertEqual("", stderr.getvalue())
        report = stdout.getvalue()
        self.assertIn("responses: 1", report)
        self.assertIn("references: 1", report)
        self.assertIn("numeric claims: 1", report)
        self.assertIn("findings: 0", report)
        self.assertNotIn("Maren", report)


class EveryPostedReplyHasALocatedReading(unittest.TestCase):
    def grade(self, run: Run) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = scan.main([str(run.root)])
        return status, stdout.getvalue(), stderr.getvalue()

    def test_an_absent_reread_file_is_a_finding_and_other_rows_still_run(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "reread.md").unlink()
            (run.root / "response-maren.md").write_text(
                BODY.replace("12%", "17%", 1), encoding="utf-8"
            )

            status, stdout, stderr = self.grade(run)

        self.assertEqual(1, status)
        self.assertEqual("", stderr)
        self.assertIn("missing-posted-reading: 1", stdout)
        self.assertIn("untraced-number: 1", stdout)

    def test_an_unreadable_reread_file_is_did_not_scan(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "reread.md").write_text(
                "VERDICT: matches - trust me\n", encoding="utf-8"
            )

            status, stdout, stderr = self.grade(run)

        self.assertEqual(2, status)
        self.assertEqual("", stdout)
        self.assertIn("reread.md", stderr)

    def test_a_third_verdict_is_a_finding_not_a_source_error(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "reread.md").write_text(
                REREAD.replace("matches -", "uncertain -"), encoding="utf-8"
            )

            status, stdout, stderr = self.grade(run)

        self.assertEqual(1, status)
        self.assertEqual("", stderr)
        self.assertIn("unknown-verdict: 1", stdout)

    def test_each_declared_verdict_needs_substance(self):
        for verdict in ("matches", "diverges"):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as temp:
                run = Run(Path(temp))
                (run.root / "reread.md").write_text(
                    REREAD.replace(
                        "matches - The paragraphs, references, and bold label are present.",
                        verdict,
                    ),
                    encoding="utf-8",
                )

                status, stdout, _ = self.grade(run)

            self.assertEqual(1, status)
            self.assertIn("bare-verdict: 1", stdout)

    def test_a_reply_reading_needs_an_entry_id(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "reread.md").write_text(
                REREAD.replace("?entry_id=31", ""), encoding="utf-8"
            )

            status, stdout, _ = self.grade(run)

        self.assertEqual(1, status)
        self.assertIn("unlocated-reading: 1", stdout)

    def test_a_classmate_locator_cannot_stand_in_for_the_reply(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "reread.md").write_text(
                REREAD.replace("entry_id=31", "entry_id=21"), encoding="utf-8"
            )

            status, stdout, _ = self.grade(run)

        self.assertEqual(1, status)
        self.assertIn("borrowed-locator: 1", stdout)

    def test_the_initial_post_locator_cannot_stand_in_when_its_reading_is_absent(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "post.md").write_text(
                "POST-URL: https://example.org/courses/1/discussion_topics/2?entry_id=41\n"
                "POSTED: 2026-08-28T19:30:00-04:00\n",
                encoding="utf-8",
            )
            (run.root / "reread.md").write_text(
                REREAD.replace("entry_id=31", "entry_id=41"), encoding="utf-8"
            )

            status, stdout, _ = self.grade(run)

        self.assertEqual(1, status)
        self.assertIn("borrowed-locator: 1", stdout)

    def test_an_nd_citation_resolves_to_its_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "response-maren.md").write_text(
                BODY.replace("Quill, 2024", "Quill, n.d.").replace(
                    "Quill, R. (2024).", "Quill, R. (n.d.)."
                ),
                encoding="utf-8",
            )
            (run.root / "claims.md").write_text(
                CLAIMS.replace("Quill, R. (2024).", "Quill, R. (n.d.)."),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(0, status)
        self.assertIn("unresolved-citation: 0", stdout.getvalue())


class ARecognizedButRefusedLabelStopsTheScan(unittest.TestCase):
    def test_a_plain_references_label_names_the_line_and_ungrades_dependent_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("**References**", "References"),
                encoding="utf-8",
            )
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = scan.main([temp])

        self.assertEqual(2, status)
        self.assertIn("References", stderr.getvalue())
        self.assertIn("addressed-name: 0", stdout.getvalue())
        for row in (
            "word-floor",
            "reference-minimum",
            "unresolved-citation",
            "untraced-number",
            "respent-source",
        ):
            with self.subTest(row=row):
                self.assertIn(f"{row}: not graded", stdout.getvalue())

    def test_a_refused_label_keeps_exit_two_when_the_addressed_name_also_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("Maren,", "Karen,").replace("**References**", "References"),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(2, status)
        self.assertIn("addressed-name: 1", stdout.getvalue())


class AddressedNameIsCheckedAgainstTheRoster(unittest.TestCase):
    def test_one_letter_wrong_name_fails_without_leaking_it_by_default(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(BODY.replace("Maren,", "Karen,"), encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertEqual("", stderr.getvalue())
        self.assertIn("addressed-name: 1", stdout.getvalue())
        self.assertNotIn("Karen", stdout.getvalue())


class TheCliniciansWordFloorIsEnforced(unittest.TestCase):
    def test_ninety_nine_words_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            words = ["Maren,"] + ["word"] * 98
            (run.root / "response-maren.md").write_text(
                " ".join(words) + "\n\n**References**\n\nQuill, R. (2024). Title. Journal.\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("word-floor: 1", stdout.getvalue())


class EachReplyCarriesEvidence(unittest.TestCase):
    def test_a_reply_without_its_own_reference_list_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(BODY.split("\n**References**\n", 1)[0], encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("reference-minimum: 1", stdout.getvalue())

    def test_placeholder_text_is_not_a_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.split("\n**References**\n", 1)[0]
                + "\n**References**\n\nplaceholder\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("references: 0", stdout.getvalue())
        self.assertIn("reference-minimum: 1", stdout.getvalue())

    def test_a_year_shaped_placeholder_is_not_a_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.split("\n**References**\n", 1)[0]
                + "\n**References**\n\nPlaceholder, P. (2024). Placeholder source. Journal.\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("references: 0", stdout.getvalue())
        self.assertIn("reference-minimum: 1", stdout.getvalue())

    def test_an_in_text_citation_missing_from_that_replys_list_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(BODY.replace("Quill, R. (2024)", "Vale, R. (2024)"), encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("unresolved-citation: 1", stdout.getvalue())

    def test_each_source_in_a_multi_source_parenthesis_is_resolved(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("(Quill, 2024)", "(Quill, 2024; Vale, 2023)"),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("citations: 2", stdout.getvalue())
        self.assertIn("unresolved-citation: 1", stdout.getvalue())

    def test_two_author_narrative_citation_resolves_to_the_first_author(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                CLAIMS.replace("Quill, R. (2024)", "Quill, R., & Vale, S. (2024)"),
                encoding="utf-8",
            )
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("(Quill, 2024)", "Quill and Vale (2024)").replace(
                    "Quill, R. (2024)", "Quill, R., & Vale, S. (2024)"
                ),
                encoding="utf-8",
            )
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(0, status)

    def test_parenthetical_page_locator_is_part_of_the_citation(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("(Quill, 2024)", "(Vale, 2023, p. 4)"),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("citations: 1", stdout.getvalue())
        self.assertIn("numeric claims: 1", stdout.getvalue())
        self.assertIn("unresolved-citation: 1", stdout.getvalue())

    def test_narrative_page_locator_is_part_of_the_citation(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                CLAIMS.replace("Quill, R. (2024)", "Quill, R., & Vale, S. (2024)"),
                encoding="utf-8",
            )
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("(Quill, 2024)", "Quill and Vale (2024, pp. 4–5)").replace(
                    "Quill, R. (2024)", "Quill, R., & Vale, S. (2024)"
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(0, status)
        self.assertIn("citations: 1", stdout.getvalue())
        self.assertIn("numeric claims: 1", stdout.getvalue())


class NumbersTraceToTheRunLedger(unittest.TestCase):
    def test_a_body_number_absent_from_claims_md_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(BODY.replace("12%", "17%", 1), encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("untraced-number: 1", stdout.getvalue())

    def test_a_number_in_another_replys_record_does_not_trace_this_reply(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").write_text(
                CLAIMS.replace("[REPLY: maren]", "[REPLY: solin]"), encoding="utf-8"
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("untraced-number: 1", stdout.getvalue())

    def test_the_ledgers_date_does_not_masquerade_as_a_claim_record(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("a program reported a 12% improvement", "the 2026 program improved care"),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("untraced-number: 1", stdout.getvalue())


class ASourceIsSpentOnlyOncePerRun(unittest.TestCase):
    def test_the_same_reference_in_two_replies_fails_once(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "posts" / "solin-vale.md").write_text(
                "AUTHOR: Solin Vale\nREPLIES: 0\n\nA second synthetic post.\n",
                encoding="utf-8",
            )
            (run.root / "response-solin.md").write_text(
                BODY.replace("Maren,", "Solin,"), encoding="utf-8"
            )
            with (run.root / "claims.md").open("a", encoding="utf-8") as ledger:
                ledger.write("\n" + CLAIMS.split("\n\n", 1)[1].replace("[REPLY: maren]", "[REPLY: solin]"))
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("responses: 2", stdout.getvalue())
        self.assertIn("respent-source: 1", stdout.getvalue())


class AdvisoryAndCoverageBehavior(unittest.TestCase):
    def test_an_invoked_source_is_counted_without_changing_the_word_count(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace(
                    "Maren,",
                    "<!-- INVOKED: black hole | it pulls everything near it in -->\nMaren,",
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(0, status)
        self.assertIn("words: 147", stdout.getvalue())
        self.assertIn("invoked sources: 1", stdout.getvalue())

    def test_an_invoked_marker_without_a_property_separator_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("Maren,", "<!-- INVOKED: hole -->\nMaren,"),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("invoked-property: 1", stdout.getvalue())

    def test_an_empty_invoked_domain_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace(
                    "Maren,", "<!-- INVOKED: | it pulls everything in -->\nMaren,"
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("invoked-property: 1", stdout.getvalue())

    def test_an_empty_invoked_property_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("Maren,", "<!-- INVOKED: black hole | -->\nMaren,"),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("invoked-property: 1", stdout.getvalue())

    def test_an_invoked_property_that_restates_the_domain_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace(
                    "Maren,", "<!-- INVOKED: black hole | black hole -->\nMaren,"
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("invoked-property: 1", stdout.getvalue())

    def test_repetition_does_not_turn_a_domain_into_a_property(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("Maren,", "<!-- INVOKED: hole | a hole hole -->\nMaren,"),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("invoked-property: 1", stdout.getvalue())

    def test_a_generic_noun_does_not_turn_a_domain_into_a_property(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace(
                    "Maren,", "<!-- INVOKED: black hole | black hole thing -->\nMaren,"
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(1, status)
        self.assertIn("invoked-property: 1", stdout.getvalue())

    def test_pluralized_and_placeholder_domain_phrases_are_not_properties(self):
        for property_value in (
            "black holes",
            "black hole effect",
            "black hole action",
            "it can",
            "can black hole",
        ):
            with self.subTest(property=property_value), tempfile.TemporaryDirectory() as temp:
                run = Run(Path(temp))
                response = run.root / "response-maren.md"
                response.write_text(
                    BODY.replace(
                        "Maren,",
                        f"<!-- INVOKED: black hole | {property_value} -->\nMaren,",
                    ),
                    encoding="utf-8",
                )
                stdout = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                    status = scan.main([temp])

            self.assertEqual(1, status)
            self.assertIn("invoked-property: 1", stdout.getvalue())

    def test_substantive_behavior_clauses_are_not_over_refused(self):
        for property_value in (
            "it is pulling everything in",
            "a black hole pulls everything in",
        ):
            with self.subTest(property=property_value), tempfile.TemporaryDirectory() as temp:
                run = Run(Path(temp))
                response = run.root / "response-maren.md"
                response.write_text(
                    BODY.replace(
                        "Maren,",
                        f"<!-- INVOKED: black hole | {property_value} -->\nMaren,",
                    ),
                    encoding="utf-8",
                )
                stdout = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                    status = scan.main([temp])

            self.assertEqual(0, status)
            self.assertIn("invoked-property: 0", stdout.getvalue())

    def test_a_pre_496_marker_is_reported_without_changing_the_verdict_or_word_count(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            response = run.root / "response-maren.md"
            response.write_text(
                BODY.replace("Maren,", "<!-- AMPLIFICATION: craft metaphor -->\nMaren,"),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = scan.main([temp])

        self.assertEqual(0, status)
        self.assertIn("words: 147", stdout.getvalue())
        self.assertIn("pre-#496 markers: 1 (counted, not graded)", stdout.getvalue())
        self.assertNotIn("amplifications:", stdout.getvalue())

    def test_a_missing_claim_ledger_is_not_reported_as_a_clean_scan(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "claims.md").unlink()
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = scan.main([temp])

        self.assertEqual(2, status)
        self.assertEqual("", stdout.getvalue())
        self.assertIn("claims.md", stderr.getvalue())

    def test_one_malformed_post_cannot_hide_behind_one_readable_roster_entry(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(Path(temp))
            (run.root / "posts" / "unread.md").write_text(
                "This post has no roster field.\n", encoding="utf-8"
            )
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = scan.main([temp])

        self.assertEqual(2, status)
        self.assertEqual("", stdout.getvalue())
        self.assertIn("roster read 1 of 2", stderr.getvalue())
        self.assertIn("unread remainder 1", stderr.getvalue())


class EveryDeclaredLimitHasOneCheckedInventory(unittest.TestCase):
    def test_the_declared_limits_are_complete_and_substantive(self):
        self.assertEqual(
            tuple((subject, reason) for subject, reason, _ in scan.DECLARED_LIMITS),
            scan.NOT_REACHED,
        )
        self.assertTrue(all(len(reason.split()) > 8 for _key, reason in scan.NOT_REACHED))
        for _subject, _reason, disposition in scan.DECLARED_LIMITS:
            self.assertIsInstance(disposition, scan.EvidenceDisposition)
        self.assertIn(scan.UNMARKED_INVOKED_SOURCE_LIMIT, scan.NOT_REACHED)
        self.assertIn(scan.INVOKED_PROPERTY_LIMIT, scan.NOT_REACHED)

    def test_the_skill_and_module_point_to_the_inventory_without_copying_rows(self):
        skill = DISCUSSION_REPLY_SKILL.read_text(encoding="utf-8")

        self.assertIn("discussion_reply_scan.NOT_REACHED", skill)
        self.assertNotIn(
            "discussion_reply_scan.UNMARKED_INVOKED_SOURCE_LIMIT",
            DISCUSSION_REPLY_SKILL.read_text(encoding="utf-8"),
        )
        self.assertIn("``NOT_REACHED``", scan.__doc__ or "")


class EveryBehaviorLimitHasALiveHandler(unittest.TestCase):
    HANDLERS = {
        "whether reference-dependent rows ran after a refused reference label": (
            "ARecognizedButRefusedLabelStopsTheScan.test_a_plain_references_label_names_the_line_and_ungrades_dependent_rows",
            "ACompleteRunPasses.test_cli_reports_counts_without_exposing_the_addressed_name",
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
                        f"test_discussion_reply_scan.{named}"
                    ).run(result)
                    self.assertTrue(
                        result.wasSuccessful(),
                        f"{subject}: {named}: {result.errors + result.failures}",
                    )


if __name__ == "__main__":
    unittest.main()
