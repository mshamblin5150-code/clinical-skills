"""Tests for the peer-critique grader.

phi-scan: synthetic

Every fixture below is invented. The classmate names are manufactured teaching
material, never a real roster, and no run under ``scratch/`` is read.
"""

from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import peer_critique_scan as scan

SKILL = Path(__file__).resolve().parents[1] / "skills" / "peer-critique" / "SKILL.md"
from grader_conformance import EmptyPopulationInput, for_module
from prose_bind import NAMING, bind


GraderConformance = for_module(scan)

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
    "VERDICT: matches - the board text equals the artifact\n"
)


def empty_population_input(root: Path) -> EmptyPopulationInput:
    (root / "posts").mkdir()
    (root / "posts" / "synthetic.md").write_text(
        "AUTHOR: Maren Quill\n", encoding="utf-8"
    )
    (root / "critique.md").write_text("", encoding="utf-8")
    (root / "claims.md").write_text("DATE: 2026-09-09\n", encoding="utf-8")
    (root / "reread.md").write_text(REREAD, encoding="utf-8")
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
) -> Path:
    """Write one synthetic run directory and return its path."""

    directory = Path(tempfile.mkdtemp()) / "run"
    (directory / "posts").mkdir(parents=True)
    (directory / "posts" / "k.md").write_text("AUTHOR: Maren Quill\n", encoding="utf-8")
    sections = "\n\n".join(
        f"**{heading}**\n\n" + ("" if heading in empty else f"{filler} (Ross, 2025).") + "\n"
        for heading in headings
    )
    (directory / "critique.md").write_text(
        f"{opening}\n\n{sections}{extra}{references}", encoding="utf-8"
    )
    (directory / "claims.md").write_text(claims, encoding="utf-8")
    if reread is not None:
        (directory / "reread.md").write_text(reread, encoding="utf-8")
    return directory


def graded(directory: Path) -> scan.Scan:
    parsed = scan.run_grader.Parsed(source=str(directory))
    return scan.survey(scan.load(parsed))


def kinds(directory: Path) -> list[str]:
    return [finding.kind for finding in graded(directory).findings]


class TheCleanRunPasses(unittest.TestCase):
    def test_a_compliant_critique_reports_no_finding(self):
        self.assertEqual([], kinds(build_run()))

    def test_every_required_heading_is_counted(self):
        self.assertEqual(len(HEADINGS), graded(build_run()).headings_found)


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
    def test_a_number_traced_to_an_unrelated_restatement_passes(self):
        """The declared blind spot: the token matches, the meaning is unread."""

        claims = "DATE: 2026-09-09\n\n## CLAIM: a claim\nRESTATEMENT: an unrelated 47 appears here\n"
        self.assertNotIn(
            scan.UNTRACED_NUMBER,
            kinds(build_run(claims=claims, extra="\n\nThe rate was 47 percent.\n")),
        )

    def test_a_number_absent_from_every_record_still_fails(self):
        self.assertIn(scan.UNTRACED_NUMBER, kinds(build_run(extra="\n\nThe rate was 91 percent.\n")))


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
        "whether a believed record's restatement supports the number traced from it": (
            "TheNumericWalkMatchesTokensAndNotMeaning.test_a_number_traced_to_an_unrelated_restatement_passes",
            "TheNumericWalkMatchesTokensAndNotMeaning.test_a_number_absent_from_every_record_still_fails",
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
