"""Tests for the peer-critique grader.

phi-scan: synthetic

Every fixture below is invented. The classmate names are manufactured teaching
material, never a real roster, and no run under ``scratch/`` is read.
"""

from __future__ import annotations

import io
import hashlib
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import peer_critique_scan as scan
import research_ledger
import file_digest

SKILL = Path(__file__).resolve().parents[1] / "skills" / "peer-critique" / "SKILL.md"
from grader_conformance import (
    EmptyPopulationInput,
    UnreadRemainderInput,
    for_module,
    gate_conformance,
    unread_remainder_conformance,
)
from prose_bind import NAMING, bind


GraderConformance = for_module(scan)
GateConformance = gate_conformance(scan)
UnreadRemainderConformance = unread_remainder_conformance(scan)

HEADINGS = scan.REQUIRED_HEADINGS
FILLER = " ".join(["word"] * 70)
REFERENCES = (
    "\n**References**\n\n"
    "Ross, J. (2025). A topic. UpToDate. https://example.org/x\n\n"
    "Sena, A. C. (2026). Another topic. UpToDate. https://example.org/y\n"
)
REREAD = (
    "## REREAD: critique.md\n"
    "POST-URL: https://example.org/t?entry_id=1\n"
    "POSTED: 2026-09-09\n"
    "READ: 2026-09-09\n"
    "SUBMISSION-SHA256: {submission_sha256}\n"
    "VERDICT: matches - the board text equals the artifact\n"
)


def claim_record(
    number: int,
    *,
    status: str = "sourced",
    refutation: str = "stands - the result was confirmed",
    second_route: str | None = "publisher HTML -> journal PDF",
    dropped: str | None = None,
) -> str:
    fields = [
        f"## CLAIM: a claim carrying {number}",
        f"RESTATEMENT: the result was {number}",
        f"STATUS: {status}",
        f"REFUTATION: {refutation}",
        f"TESTED-HEADING: {research_ledger.heading_digest(f'a claim carrying {number}')}",
    ]
    if second_route is not None:
        fields.append(f"SECOND-ROUTE: {second_route}")
    if dropped is not None:
        fields.append(f"DROPPED: {dropped}")
    return "\n".join(fields) + "\n"


def empty_population_input(root: Path) -> EmptyPopulationInput:
    (root / "posts").mkdir()
    (root / "posts" / "synthetic.md").write_text(
        "AUTHOR: Maren Quill\n", encoding="utf-8"
    )
    critique = root / "critique.md"
    critique.write_text("", encoding="utf-8")
    (root / "claims.md").write_text("DATE: 2026-09-09\n", encoding="utf-8")
    (root / "reread.md").write_text(
        REREAD.format(submission_sha256=file_digest.sha256(critique)),
        encoding="utf-8",
    )
    digest = hashlib.sha256((root / "critique.md").read_bytes()).hexdigest()
    (root / "heading-read.md").write_text(
        f"## HEADING-READ: critique.md\nDRAFT: {digest}\n"
        "ROUTE: separate context\nSENTENCES: 0 factual, 0 clinician's own\nVERDICT: clean\n",
        encoding="utf-8",
    )
    return EmptyPopulationInput(
        (str(root),), population_size=lambda result: result.words or 0
    )


def build_run(
    *,
    headings=HEADINGS,
    opening="Maren,",
    filler=FILLER,
    references=REFERENCES,
    empty=(),
    reread=REREAD,
    extra="",
    claims="DATE: 2026-09-09\n\n## CLAIM: a claim\nRESTATEMENT: says the thing\n",
    root: Path | None = None,
) -> Path:
    """Write one synthetic run directory and return its path."""

    directory = root or Path(tempfile.mkdtemp()) / "run"
    (directory / "posts").mkdir(parents=True)
    (directory / "posts" / "k.md").write_text("AUTHOR: Maren Quill\n", encoding="utf-8")
    sections = "\n\n".join(
        f"**{heading}**\n\n" + ("" if heading in empty else f"{filler} (Ross, 2025).") + "\n"
        for heading in headings
    )
    critique = f"{opening}\n\n{sections}{extra}{references}"
    (directory / "critique.md").write_text(critique, encoding="utf-8")
    (directory / "claims.md").write_text(claims, encoding="utf-8")
    digest = hashlib.sha256((directory / "critique.md").read_bytes()).hexdigest()
    (directory / "heading-read.md").write_text(
        f"## HEADING-READ: critique.md\nDRAFT: {digest}\n"
        "ROUTE: separate context\nSENTENCES: 0 factual, 0 clinician's own\nVERDICT: clean\n",
        encoding="utf-8",
    )
    if reread is not None:
        (directory / "reread.md").write_text(
            reread.format(
                submission_sha256=file_digest.sha256(directory / "critique.md")
            ),
            encoding="utf-8",
        )
    return directory


def unread_remainder_input(root: Path) -> UnreadRemainderInput:
    unread = build_run(root=root / "unread")
    twin = build_run(root=root / "twin")
    (unread / "posts" / "unread.md").write_text(
        "A synthetic post with no author field.\n", encoding="utf-8"
    )
    return UnreadRemainderInput(
        (str(unread),),
        (str(twin),),
        unread_remainder=lambda result: (
            result.posts_total - result.posts_read + result.heading_read_unread
        ),
    )


def graded(directory: Path) -> scan.Scan:
    parsed = scan.run_grader.Parsed(source=str(directory))
    return scan.survey(scan.load(parsed))


def kinds(directory: Path) -> list[str]:
    return [finding.kind for finding in graded(directory).findings]


class TheCleanRunPasses(unittest.TestCase):
    def test_a_compliant_critique_reports_no_finding(self):
        self.assertEqual([], kinds(build_run()))

    def test_a_missing_critique_fingerprint_is_a_finding(self):
        directory = build_run(reread=REREAD.replace("SUBMISSION-SHA256: {submission_sha256}\n", ""))
        self.assertIn(scan.SUBMISSION_FINGERPRINT, kinds(directory))

    def test_an_unrelated_reading_does_not_stand_in_for_the_critique(self):
        directory = build_run(reread=REREAD.replace("critique.md", "unrelated.md"))
        self.assertIn(scan.MISSING_POSTED_READING, kinds(directory))

    def test_a_one_word_critique_edit_makes_its_fingerprint_stale(self):
        directory = build_run()
        critique = directory / "critique.md"
        critique.write_text(
            critique.read_text(encoding="utf-8").replace("word", "term", 1),
            encoding="utf-8",
        )
        self.assertIn(scan.SUBMISSION_FINGERPRINT, kinds(directory))

    def test_every_required_heading_is_counted(self):
        self.assertEqual(len(HEADINGS), graded(build_run()).headings_found)

    def test_a_missing_heading_read_fails(self):
        directory = build_run()
        (directory / "heading-read.md").unlink()
        self.assertIn(scan.heading_read.MISSING_RECORD, kinds(directory))

    def test_a_heading_read_for_prior_critique_bytes_is_stale(self):
        directory = build_run()
        critique = directory / "critique.md"
        critique.write_text(critique.read_text(encoding="utf-8") + "\nLater edit.\n", encoding="utf-8")
        self.assertIn(scan.heading_read.DRAFT_MISMATCH, kinds(directory))


class EveryRowFiresOnItsOwnDefect(unittest.TestCase):
    """Each row is driven by a mutation of a passing run, one at a time."""

    def test_a_dropped_heading_is_a_finding(self):
        self.assertIn(scan.MISSING_HEADING, kinds(build_run(headings=HEADINGS[:-1])))

    def test_a_heading_with_no_prose_is_a_finding(self):
        self.assertIn(scan.EMPTY_HEADING, kinds(build_run(empty=("Preventive Care",))))

    def test_transposed_headings_are_a_finding(self):
        shuffled = (HEADINGS[1], HEADINGS[0]) + HEADINGS[2:]
        self.assertIn(scan.HEADING_ORDER, kinds(build_run(headings=shuffled)))

    def test_addressing_someone_off_the_roster_is_a_finding(self):
        self.assertIn(scan.ADDRESSED_NAME, kinds(build_run(opening="Rhoda,")))

    def test_a_critique_under_the_floor_is_a_finding(self):
        self.assertIn(scan.WORD_FLOOR, kinds(build_run(filler="short")))

    def test_one_reference_is_below_the_floor(self):
        single = "\n**References**\n\nRoss, J. (2025). A topic. UpToDate. https://example.org/x\n"
        self.assertIn(scan.REFERENCE_MINIMUM, kinds(build_run(references=single)))

    def test_a_citation_with_no_reference_is_a_finding(self):
        self.assertIn(
            scan.UNRESOLVED_CITATION,
            kinds(build_run(extra="\n\nA further point (Nguyen, 2024).\n")),
        )

    def test_a_shortened_title_citation_resolves(self):
        references = (
            REFERENCES
            + "\nNursing today (2nd ed.). (2020). Publisher.\n"
        )

        self.assertNotIn(
            scan.UNRESOLVED_CITATION,
            kinds(
                build_run(
                    extra="\n\nA further point follows (Nursing, 2020).\n",
                    references=references,
                )
            ),
        )

    def test_a_republished_original_element_is_not_compared(self):
        references = (
            REFERENCES
            + "\nWatson, J. B., & Rayner, R. (2013). Conditioned emotional reactions. "
            "(Original work published 1920)\n"
        )

        self.assertNotIn(
            scan.UNRESOLVED_CITATION,
            kinds(
                build_run(
                    extra="\n\nA further point follows (Watson & Rayner, 1919/2013).\n",
                    references=references,
                )
            ),
        )

    def test_a_republished_second_year_must_match_the_reference(self):
        references = (
            REFERENCES
            + "\nWatson, J. B., & Rayner, R. (2013). Conditioned emotional reactions. "
            "(Original work published 1920)\n"
        )

        self.assertIn(
            scan.UNRESOLVED_CITATION,
            kinds(
                build_run(
                    extra="\n\nA further point follows (Watson & Rayner, 1920/2014).\n",
                    references=references,
                )
            ),
        )

    def test_a_number_with_no_claim_record_is_a_finding(self):
        self.assertIn(scan.UNTRACED_NUMBER, kinds(build_run(extra="\n\nThe rate was 47 percent.\n")))

    def test_an_unrecorded_posted_reading_is_a_finding(self):
        self.assertIn(scan.MISSING_POSTED_READING, kinds(build_run(reread=None)))

    def test_an_unrecognized_verdict_is_a_finding(self):
        reread = REREAD.replace("matches - the board text equals the artifact", "maybe - unclear")
        self.assertIn(scan.UNKNOWN_VERDICT, kinds(build_run(reread=reread)))

    def test_a_verdict_with_no_substance_is_a_finding(self):
        reread = REREAD.replace("matches - the board text equals the artifact", "matches")
        self.assertIn(scan.BARE_VERDICT, kinds(build_run(reread=reread)))

    def test_no_row_fires_on_another_rows_defect(self):
        """A row that fires on a neighbor's mutation grades nothing of its own."""

        self.assertEqual([scan.WORD_FLOOR], kinds(build_run(filler="short")))
        self.assertEqual([scan.ADDRESSED_NAME], kinds(build_run(opening="Rhoda,")))


class TheCitationYearIsNotABodyNumber(unittest.TestCase):
    def test_a_resolved_citation_year_does_not_trace_as_a_numeral(self):
        # Every heading carries "(Ross, 2025)"; none of those years is a claim.
        self.assertNotIn(scan.UNTRACED_NUMBER, kinds(build_run()))


class CitationResolutionResidues(unittest.TestCase):
    def test_the_three_declared_prefix_edges_resolve(self):
        today = scan.ReferenceKeySet.from_references(
            ("Nursing today. (2020). Publisher.",)
        )
        tomorrow = scan.ReferenceKeySet.from_references(
            ("Nursing tomorrow. (2020). Publisher.",)
        )
        group = scan.ReferenceKeySet.from_references(
            ("World Health Organization. (2020). A title.",)
        )

        self.assertTrue(today.resolves(("nursing", "2020")))
        self.assertTrue(tomorrow.resolves(("nursing", "2020")))
        self.assertTrue(group.resolves(("worldhealth", "2020")))
        self.assertTrue(today.resolves(("nursingtod", "2020")))

    def test_single_given_name_resolves_in_critique(self):
        references = scan.ReferenceKeySet.from_references(
            ("Williams, S. (2019). A title.", "Williams, S. (2020). Another title.")
        )
        body = "The result is reported (Sarah Williams, 2019)."
        cited = scan.read_citations(body, references)
        self.assertTrue(any(
            references.resolves(key)
            for key in scan.citation_occurrence_keys(cited, body, references)[0]
        ))
        self.assertNotIn(
            scan.UNRESOLVED_CITATION,
            kinds(build_run(
                extra="\n\n" + body,
                references=REFERENCES + "\nWilliams, S. (2019). A title.\n",
            )),
        )

    def test_combined_given_name_and_initials_remain_unlisted(self):
        self._assert_first_name_limit("Sarah M. Williams")

    def test_hyphenated_given_name_remains_unlisted(self):
        self._assert_first_name_limit("Mary-Kate Williams")

    def _assert_first_name_limit(self, name):
        references = scan.ReferenceKeySet.from_references(("Williams, S. (2019). A title.",))
        body = f"The result is reported ({name}, 2019)."
        cited = scan.read_citations(body, references)
        self.assertTrue(cited)
        self.assertFalse(any(
            references.resolves(key)
            for keys in scan.citation_occurrence_keys(cited, body, references)
            for key in keys
        ))


class TheWordCeilingIsReportedAndNeverGraded(unittest.TestCase):
    def test_a_critique_past_the_ceiling_is_clean(self):
        long_filler = " ".join(["word"] * 200)
        result = graded(build_run(filler=long_filler))
        self.assertGreater(result.words, scan.WORD_CEILING_COUNT)
        self.assertEqual([], list(result.findings))

    def test_the_ceiling_is_reported_beside_the_count(self):
        report = scan.format_report(graded(build_run()), "source")
        self.assertIn(f"word ceiling: {scan.WORD_CEILING_COUNT}", report)
        self.assertIn(scan.NOT_GRADED, report)


class TheAmpersandIsCountedAndNeverGraded(unittest.TestCase):
    def test_an_ampersand_in_the_body_is_counted(self):
        result = graded(build_run(extra="\n\nRoss & Sena agree on the point.\n"))
        self.assertEqual(1, result.ampersands)

    def test_an_ampersand_is_not_a_finding(self):
        self.assertNotIn(
            "ampersand",
            " ".join(kinds(build_run(extra="\n\nRoss & Sena agree on the point.\n"))),
        )


class TheHeadingRowProvesPresenceAndNotAnswer(unittest.TestCase):
    def test_irrelevant_prose_under_a_required_heading_passes(self):
        """The declared blind spot: presence is provable, an answer is not."""

        run = build_run(filler="This sentence is about nothing the spec asked for at all " * 12)
        self.assertNotIn(scan.EMPTY_HEADING, kinds(run))

    def test_an_empty_required_heading_still_fails(self):
        self.assertIn(scan.EMPTY_HEADING, kinds(build_run(empty=("Patient Education",))))


class TheNumericWalkMatchesTokensAndNotMeaning(unittest.TestCase):
    def test_heading_number_traces_when_restatement_disagrees(self):
        claims = claim_record(42).replace(
            "RESTATEMENT: the result was 42",
            "RESTATEMENT: the result was 47",
        )
        self.assertNotIn(
            scan.UNTRACED_NUMBER,
            kinds(build_run(claims=claims, extra="\n\nThe rate was 42 percent.\n")),
        )
        findings = [
            finding
            for finding in graded(
                build_run(claims=claims, extra="\n\nThe rate was 47 percent.\n")
            ).findings
            if finding.kind == scan.UNTRACED_NUMBER
        ]
        self.assertEqual(
            "47 appears only in a claim record's restatement; state it in the heading",
            findings[0].detail,
        )

    def test_restatement_only_number_requires_the_heading(self):
        claims = claim_record(47).replace(
            "## CLAIM: a claim carrying 47", "## CLAIM: a claim carrying a result"
        ).replace(
            research_ledger.heading_digest("a claim carrying 47"),
            research_ledger.heading_digest("a claim carrying a result"),
        )
        findings = [
            finding
            for finding in graded(
                build_run(claims=claims, extra="\n\nThe rate was 47 percent.\n")
            ).findings
            if finding.kind == scan.UNTRACED_NUMBER
        ]
        self.assertEqual(
            "47 appears only in a claim record's restatement; state it in the heading",
            findings[0].detail,
        )

    def test_passage_locator_number_does_not_trace(self):
        claims = claim_record(47).replace(
            "## CLAIM: a claim carrying 47", "## CLAIM: a claim carrying a result"
        ).replace(
            research_ledger.heading_digest("a claim carrying 47"),
            research_ledger.heading_digest("a claim carrying a result"),
        ).replace(
            "RESTATEMENT: the result was 47",
            "RESTATEMENT: the result was described\nPASSAGE: table 47",
        )
        findings = [
            finding
            for finding in graded(
                build_run(claims=claims, extra="\n\nThe rate was 47 percent.\n")
            ).findings
            if finding.kind == scan.UNTRACED_NUMBER
        ]
        self.assertEqual("47 is absent from claims.md", findings[0].detail)

    def test_a_number_absent_from_every_record_still_fails(self):
        findings = [
            finding
            for finding in graded(build_run(extra="\n\nThe rate was 91 percent.\n")).findings
            if finding.kind == scan.UNTRACED_NUMBER
        ]
        self.assertEqual("91 is absent from claims.md", findings[0].detail)


class OnlyBelievedClaimRecordsCertifyBodyNumbers(unittest.TestCase):
    def test_standing_refuted_unsourced_incomplete_and_dropped_records(self):
        cases = {
            "standing": (claim_record(42), False),
            "refuted": (
                claim_record(42, refutation="refuted - the source contradicts the claim"),
                True,
            ),
            "unsourced": (claim_record(42, status="unsourced"), True),
            "refutation-incomplete": (claim_record(42, second_route=None), True),
            "dropped": (
                claim_record(42, dropped="the draft no longer makes this claim"),
                True,
            ),
        }

        for name, (claims, should_fail) in cases.items():
            with self.subTest(name=name):
                findings = [
                    finding
                    for finding in graded(
                        build_run(claims=claims, extra="\n\nThe rate was 42 percent.\n")
                    ).findings
                    if finding.kind == scan.UNTRACED_NUMBER
                ]
                self.assertEqual(should_fail, bool(findings))
                if should_fail:
                    self.assertEqual(
                        "42 appears only in a disbelieved claim record",
                        findings[0].detail,
                    )

    def test_report_counts_distinct_body_numerals_and_claim_records(self):
        result = graded(
            build_run(
                claims=claim_record(42) + "\n" + claim_record(47),
                extra="\n\nThe rates were 42, 42, and 47 percent.\n",
            )
        )
        report = scan.format_report(result, "source")

        self.assertEqual(2, result.numeric_claims)
        self.assertEqual(2, result.claim_records)
        self.assertIn("numeric claims: 2", report)
        self.assertIn("claim records: 2", report)

    def test_both_counts_are_not_graded_when_the_reference_boundary_is_refused(self):
        result = graded(
            build_run(references=REFERENCES.replace("**References**", "References"))
        )
        report = scan.format_report(result, "source")

        self.assertIsNone(result.numeric_claims)
        self.assertIsNone(result.claim_records)
        self.assertIn(f"numeric claims: {scan.NOT_GRADED}", report)
        self.assertIn(f"claim records: {scan.NOT_GRADED}", report)

    def test_a_refused_label_keeps_a_missing_heading_finding(self):
        directory = build_run(
            headings=HEADINGS[:-1],
            references=REFERENCES.replace("**References**", "References"),
        )
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = scan.main([str(directory)])

        self.assertEqual(1, status)
        self.assertIn("References", stderr.getvalue())
        self.assertIn("missing-heading: 1", stdout.getvalue())
        self.assertIn("reference-minimum: not graded", stdout.getvalue())


class TheCommandRefusesAnUnscannableRun(unittest.TestCase):
    def test_a_missing_directory_is_exit_two(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            status = scan.main([str(Path(tempfile.mkdtemp()) / "absent")])
        self.assertEqual(2, status)

    def test_a_run_with_no_critique_is_exit_two(self):
        directory = build_run()
        (directory / "critique.md").unlink()
        self.assertEqual(2, scan.main([str(directory)]))

    def test_a_run_with_no_author_line_is_exit_two(self):
        directory = build_run()
        (directory / "posts" / "k.md").write_text("no fields here\n", encoding="utf-8")
        self.assertEqual(2, scan.main([str(directory)]))


class TheCommandLineIsLive(unittest.TestCase):
    def test_a_clean_run_exits_zero_through_the_command_path(self):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("peer_critique_scan.py")), str(build_run())],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("peer critique in", result.stdout)

    def test_a_defect_exits_one_through_the_command_path(self):
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("peer_critique_scan.py")),
                str(build_run(filler="short")),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(1, result.returncode)


class TheReportRedactsUntilShow(unittest.TestCase):
    def test_the_default_report_names_no_classmate(self):
        report = scan.format_report(graded(build_run(opening="Rhoda,")), "source")
        self.assertNotIn("roster first name", report)

    def test_show_carries_the_finding_detail(self):
        report = scan.format_report(graded(build_run(opening="Rhoda,")), "source", show=True)
        self.assertIn("roster first name", report)


class TheDeclaredLimitsAreDerivedAndBound(unittest.TestCase):
    def test_field_completeness_limit_is_derived_from_the_ledger_contract(self):
        fields = ", ".join(research_ledger.REFUTATION_EVIDENCE_COMPLEMENT)

        self.assertEqual(fields, scan.UNJOINED_SOURCE_FIELDS)
        self.assertEqual(
            (
                f"whether a sourced record missing one or more of {fields} is still believed",
                f"Field completeness for {fields} belongs to research_ledger; this certifier still reads numbers from a record carrying substantive refutation-evidence fields.",
                scan.EvidenceDisposition.BEHAVIOR,
            ),
            scan.UNJOINED_SOURCE_FIELDS_LIMIT,
        )
        self.assertIn(scan.UNJOINED_SOURCE_FIELDS_LIMIT, scan.DECLARED_LIMITS)

    def test_not_reached_is_derived_from_declared_limits(self):
        self.assertEqual(
            tuple((subject, reason) for subject, reason, _ in scan.DECLARED_LIMITS),
            scan.NOT_REACHED,
        )

    def test_every_reason_is_a_sentence_rather_than_a_label(self):
        self.assertTrue(all(len(reason.split()) > 8 for _subject, reason in scan.NOT_REACHED))

    def test_every_disposition_is_declared(self):
        for _subject, _reason, disposition in scan.DECLARED_LIMITS:
            self.assertIsInstance(disposition, scan.EvidenceDisposition)

    def test_the_skill_and_module_point_to_the_inventory_without_copying_rows(self):
        skill = SKILL.read_text(encoding="utf-8")

        self.assertEqual((), bind(scan.DECLARED_LIMITS, scan.__doc__, mode=NAMING))
        self.assertIn("peer_critique_scan.NOT_REACHED", skill)
        self.assertIn("``NOT_REACHED``", scan.__doc__ or "")
        for where, prose in {
            "the skill": skill,
            "the module docstring": scan.__doc__ or "",
        }.items():
            self.assertEqual((), bind(scan.NOT_REACHED, prose, mode=NAMING), where)


class EveryBehaviorLimitHasALiveHandler(unittest.TestCase):
    HANDLERS = {
        "first-name citations combining a given name with initials": (
            "CitationResolutionResidues.test_combined_given_name_and_initials_remain_unlisted",
            "CitationResolutionResidues.test_single_given_name_resolves_in_critique",
        ),
        "hyphenated given names in first-name citations": (
            "CitationResolutionResidues.test_hyphenated_given_name_remains_unlisted",
            "CitationResolutionResidues.test_single_given_name_resolves_in_critique",
        ),
        "whether a shortened title resolves against more than one reference entry": (
            "CitationResolutionResidues.test_the_three_declared_prefix_edges_resolve",
            "EveryRowFiresOnItsOwnDefect.test_a_shortened_title_citation_resolves",
        ),
        "whether a citation naming part of a group author's name resolves": (
            "CitationResolutionResidues.test_the_three_declared_prefix_edges_resolve",
            "EveryRowFiresOnItsOwnDefect.test_a_shortened_title_citation_resolves",
        ),
        "whether a citation stopping mid-word resolves": (
            "CitationResolutionResidues.test_the_three_declared_prefix_edges_resolve",
            "EveryRowFiresOnItsOwnDefect.test_a_shortened_title_citation_resolves",
        ),
        "whether a republished citation's original element matches its source": (
            "EveryRowFiresOnItsOwnDefect.test_a_republished_original_element_is_not_compared",
            "EveryRowFiresOnItsOwnDefect.test_a_republished_second_year_must_match_the_reference",
        ),
        "whether a heading's prose answers the sub-questions the spec states under it": (
            "TheHeadingRowProvesPresenceAndNotAnswer.test_irrelevant_prose_under_a_required_heading_passes",
            "TheHeadingRowProvesPresenceAndNotAnswer.test_an_empty_required_heading_still_fails",
        ),
        "whether a believed record's heading supports the number traced from it": (
            "TheNumericWalkMatchesTokensAndNotMeaning.test_restatement_only_number_requires_the_heading",
            "TheNumericWalkMatchesTokensAndNotMeaning.test_a_number_absent_from_every_record_still_fails",
        ),
        "whether a sourced record missing one or more of SOURCE, REFERENCE, RESTATEMENT, PASSAGE, RECENCY, RESOLVED, PAGE-YEAR, STATED-EXPIRY is still believed": (
            "OnlyBelievedClaimRecordsCertifyBodyNumbers.test_standing_refuted_unsourced_incomplete_and_dropped_records",
        ),
        "whether the critique's word count should have been cut to the stated ceiling": (
            "TheWordCeilingIsReportedAndNeverGraded.test_a_critique_past_the_ceiling_is_clean",
            "TheWordCeilingIsReportedAndNeverGraded.test_the_ceiling_is_reported_beside_the_count",
        ),
        "the legacy peer-review page's display of a stored ampersand": (
            "TheAmpersandIsCountedAndNeverGraded.test_an_ampersand_in_the_body_is_counted",
            "TheAmpersandIsCountedAndNeverGraded.test_an_ampersand_is_not_a_finding",
        ),
    }

    def test_behavior_subjects_are_exactly_the_handled_subjects(self):
        behavior = {
            subject
            for subject, _reason, disposition in scan.DECLARED_LIMITS
            if disposition is scan.EvidenceDisposition.BEHAVIOR
        }
        self.assertEqual(behavior, set(self.HANDLERS))

    def test_every_handler_names_a_real_test(self):
        for handlers in self.HANDLERS.values():
            for handler in handlers:
                class_name, method = handler.split(".")
                with self.subTest(handler=handler):
                    self.assertTrue(hasattr(globals()[class_name], method))


if __name__ == "__main__":
    unittest.main()
